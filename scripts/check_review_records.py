"""Review record check (agentic-sdlc-poc slice 4.3, S43-D3 and S43-D4), run by `make docs-check`.

The review launcher writes the verbatim blocks of every review record: under `### Attempt <attempt id>` a
`#### Prompt` block (the task prompt), an `#### Evidence` block (the computed evidence) and, once released, a
`#### Report` block. The author writes only `#### Answers to <attempt id>`. This check proves the record against the
attempt log, for every attempt whose start entry carries `record_blocks: 1` (attempts logged before slice 4.3 carry
no such field and are not checked, S43-D5):

- the attempt's heading is in its record, once, and each of its blocks hashes to the logged SHA-256;
- a block under an attempt heading that the log does not hold, or a Report block for an attempt without a released
  report, fails;
- a recheck's logged answers hash equals the hash of the answers section it names, so answers edited after the
  recheck read them fail;
- the answers to a released report meet the launcher's answer rules (`answer_rule_problems`, their one home, which
  the launcher also applies before a recheck): every finding has an answer its severity and kind allow, so no
  deferred blocking, high or medium finding (round 2 of slice 4, R2-1); a rejection of a blocking, high or medium
  finding cites a checkable fact (R2-2); a finding re-raised after its rejection is not rejected again, and a finding
  the recheck could not determine, which its report does not hold, may be answered `fixed:` or `owner:` (R2-3);
- a rejected blocking, high or medium finding is accepted by the next round's report, or carries an `owner:` link in
  its own row, or a later round answers the same finding `owner:` or `fixed:` (a re-raised finding keeps its ID).

A block is the fenced block right after a Prompt, Evidence or Report label under an attempt heading; any other fence,
for example one inside an answers section, is not a block.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_NAME = "review_attempts.jsonl"
# S43-D4, R2-1: a rejected blocking, high or medium finding stands without a later round's acceptance only with an
# owner link.
OWNER_LINK = re.compile(r"\bowner:\s*(?:https://\S+|(?:docs|AGENTS)[\w./-]*\.md\b)")
LOG_FIELDS = {"prompt": "prompt_sha256", "evidence": "evidence_sha256"}


def _load_launcher() -> Any:
    spec = importlib.util.spec_from_file_location("run_independent_review", ROOT / "scripts" / "run_independent_review.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scripts/run_independent_review.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("run_independent_review", module)
    spec.loader.exec_module(module)
    return module


launcher = _load_launcher()
records = launcher._RECORDS  # the parser the launcher writes records with
AttemptSection = records.AttemptSection
AnswerRow = launcher.AnswerRow


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LoggedAttempt:
    start: dict[str, Any]
    end: dict[str, Any] | None


def logged_attempts(log: Path) -> dict[str, LoggedAttempt]:
    entries = [json.loads(line) for line in log.read_bytes().decode("utf-8").splitlines() if line.strip()]
    ends = {e["attempt"]: e for e in entries if e.get("event") == "end"}
    return {e["attempt"]: LoggedAttempt(e, ends.get(e["attempt"])) for e in entries if e.get("event") == "start"}


def record_of(start: dict[str, Any]) -> str:
    """The review record of a start entry: its withheld path that is not the attempt log."""
    return next(p for p in start["withheld_sha256"] if Path(p).name != LOG_NAME)


def _block_problems(attempt: str, logged: LoggedAttempt, section: AttemptSection) -> list[str]:
    problems = [f"{attempt}: the {name.capitalize()} block appears {count} times" for name, count in section.counts.items()
                if count > 1]
    for name, key in LOG_FIELDS.items():
        block = section.blocks.get(name)
        if block is None:
            problems.append(f"{attempt}: no {name.capitalize()} block")
        elif sha256_text(block) != logged.start.get(key):
            problems.append(f"{attempt}: the {name.capitalize()} block does not match the logged {key}")
    report_sha = (logged.end or {}).get("report_sha256")
    report = section.blocks.get("report")
    if report_sha and report is None:
        problems.append(f"{attempt}: the released report has no Report block")
    elif report is not None and not report_sha:
        problems.append(f"{attempt}: a Report block, but the log holds no released report for this attempt")
    elif report is not None and sha256_text(report) != report_sha:
        problems.append(f"{attempt}: the Report block does not match the logged report_sha256")
    return problems


def _answers_problems(attempt: str, logged: LoggedAttempt, record_text: str) -> list[str]:
    """A recheck read the answers section of its earlier attempt; that section must not have changed since."""
    earlier = logged.start.get("earlier_attempt")
    if not earlier:
        return []
    section = launcher.answers_section(record_text, earlier)
    if section is None or sha256_text(section) != logged.start.get("answers_sha256"):
        return [f"{attempt}: the answers to {earlier} changed after this recheck read them"]
    return []


@dataclass(frozen=True)
class RecordContext:
    """What the answer rules read besides one attempt's report: the log's attempts, the record's attempt sections
    and the record's text."""

    attempts: dict[str, LoggedAttempt]
    sections: dict[str, AttemptSection]
    text: str


def _next_round_accepts(ctx: RecordContext, start: dict[str, Any], finding: str) -> bool:
    """Whether the same reviewer's completed attempt in the next round accounts the finding as accepted."""
    for attempt, logged in ctx.attempts.items():
        later = logged.start
        if (later.get("unit"), later.get("count"), later.get("round"), later.get("reviewer")) != (
                start.get("unit"), start.get("count"), start.get("round", 0) + 1, start.get("reviewer")):
            continue
        section = ctx.sections.get(attempt)
        block = section.blocks.get("report") if section else None
        if (logged.end or {}).get("status") == "completed" and block:
            accounted = json.loads(block).get("accounted", [])
            if any(e.get("item") == finding and e.get("status") == "accepted" for e in accounted):
                return True
    return False


def _later_answer_settles(ctx: RecordContext, start: dict[str, Any], finding: str) -> bool:
    """Whether a later round of the same reviewer answers the same finding (a re-raised finding keeps its ID) with
    `owner:` or `fixed:`: how a rejection that the recheck re-raised goes to the owner or is fixed (R2-3) without
    editing answers a recheck read."""
    for attempt, logged in ctx.attempts.items():
        later = logged.start
        if (later.get("unit"), later.get("count"), later.get("reviewer")) != (
                start.get("unit"), start.get("count"), start.get("reviewer")) or later.get("round", 0) <= start.get("round", 0):
            continue
        section = launcher.answers_section(ctx.text, attempt)
        rows = launcher.answer_rows(section) if section else []
        if any(r.finding == finding and launcher.answer_word(r.answer) in ("owner", "fixed") for r in rows):
            return True
    return False


def _unsettled_rejections(attempt: str, rows: list[AnswerRow], report: dict[str, Any], ctx: RecordContext) -> list[str]:
    """S43-D4, R2-1, R2-3: a rejection of a blocking, high or medium finding stands when the next round accepts it, an
    owner link in its row covers it, or a later round answers the same finding `owner:` or `fixed:`. A finding re-raised
    after its rejection already fails the answer rules, so it is not reported twice."""
    start = ctx.attempts[attempt].start
    severities = {f["id"]: f.get("severity") for f in report.get("findings", [])}
    disputed = launcher.rejected_again(report, launcher.earlier_answer_rows(ctx.text, start))
    problems = []
    for row in rows:
        severity = severities.get(row.finding)
        if launcher.answer_word(row.answer) != "rejected" or severity not in launcher.FIXED_SEVERITIES:
            continue
        settled = (OWNER_LINK.search(row.answer) or _next_round_accepts(ctx, start, row.finding)
                   or _later_answer_settles(ctx, start, row.finding))
        if row.finding not in disputed and not settled:
            problems.append(f"{row.finding} is a rejected {severity} finding that no later round accepted and no owner "
                            "link or later fix covers")
    return problems


def _finding_answer_problems(attempt: str, report: dict[str, Any], ctx: RecordContext) -> list[str]:
    """The answers to a released report: required when it has findings, and checked whenever the record holds them,
    by the launcher's answer rules and then for rejections no later round settled."""
    section = launcher.answers_section(ctx.text, attempt)
    if section is None:
        return [f"{attempt}: its report has findings and the record has no answers to it"] if report.get("findings") else []
    rows = launcher.answer_rows(section)
    earlier = launcher.earlier_answer_rows(ctx.text, ctx.attempts[attempt].start)
    problems = [*launcher.answer_rule_problems(report, rows, earlier), *_unsettled_rejections(attempt, rows, report, ctx)]
    return [f"{attempt}: {p}" for p in problems]


def check_log(root: Path, log: Path) -> list[str]:
    attempts = logged_attempts(log)
    checked = {a: logged for a, logged in attempts.items() if logged.start.get("record_blocks") == 1}
    problems: list[str] = []
    for record in sorted({record_of(logged.start) for logged in checked.values()}):
        path = root / record
        if not path.is_file():
            problems.append(f"{record}: missing; the attempt log names it")
            continue
        text = path.read_bytes().decode("utf-8")  # exact bytes: no newline translation, blocks hash as written
        sections, form = records.parse_record(text)
        problems += [f"{record}: {p}" for p in form]
        mine = {a: logged for a, logged in checked.items() if record_of(logged.start) == record}
        context = RecordContext(attempts, sections, text)
        for attempt in sorted(set(sections) - set(attempts)):
            problems.append(f"{record}: attempt {attempt} has a heading but no entry in {log.name}")
        for attempt, logged in sorted(mine.items()):
            if attempt not in sections:
                problems.append(f"{record}: logged attempt {attempt} has no heading")
                continue
            found = [*_block_problems(attempt, logged, sections[attempt]), *_answers_problems(attempt, logged, text)]
            report = sections[attempt].blocks.get("report")
            if report and not found:
                found += _finding_answer_problems(attempt, json.loads(report), context)
            problems += [f"{record}: {p}" for p in found]
    return problems


def check_review_records(root: Path) -> list[str]:
    """Every problem of every review record under `docs/slices/`, prefixed `records:`."""
    problems = []
    for log in sorted((root / "docs" / "slices").rglob(LOG_NAME)):
        try:
            problems += check_log(root, log)
        except (ValueError, KeyError, StopIteration) as broken:
            problems.append(f"{log.relative_to(root)}: cannot be read as an attempt log ({type(broken).__name__})")
    return [f"records: {p}" for p in problems]


def main() -> int:
    problems = check_review_records(ROOT)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
