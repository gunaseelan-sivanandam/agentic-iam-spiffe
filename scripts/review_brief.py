"""The decision brief of the review units a PR adds (agentic-sdlc-poc slice 4.6, S46-D13).

It reads the attempt logs and review records of the review units a PR adds (the attempts logged since the merge-base
with the base branch) and writes Markdown for the review outcome section of the slice's decision page
(`docs/slices/<slice-id>/decisions.md`, from `docs/slices/_template/decisions.md`):

- each unit's last verdict and its findings by severity;
- every finding answered `owner:`, every decision concern, every recheck answer marked `cannot determine`, and every
  finding still disputed after its recheck;
- the blocking, high and medium findings answered `rejected`, with their reasons (round 2 of slice 4, R2-8: with
  R2-1 all three are to be fixed, so the owner sees each rejection of one);
- the origin stage of each finding against the review that found it (S41-D16).

It holds no CI result: the user sees the PR's required checks on the PR page (owner, 2026-11-13, decision concern 10
of slice 4). It writes no brief, and fails, when a record does not hold what its attempt log says
(`scripts/check_review_records.py`) or when a released report has a finding without an answer, so the brief cannot
omit what the records hold. It reads the working tree and the local Git history only, so it runs on a clean checkout of
the PR's head.

Usage: python3 scripts/review_brief.py --base origin/poc/agentic-sdlc [--head HEAD]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_NAME = "review_attempts.jsonl"
SEVERITIES = ("blocking", "high", "medium", "low")


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)  # dataclasses resolve their module by name
    spec.loader.exec_module(module)
    return module


checker = _load("check_review_records")
launcher = checker.launcher
records = checker.records


class BriefError(Exception):
    """The records cannot give a complete brief; nothing is written."""


@dataclass
class Attempt:
    """One logged attempt of a unit, with its released report and the author's answers to it, as the record holds."""

    start: dict[str, Any]
    end: dict[str, Any] | None
    report: dict[str, Any] | None = None
    answers: list[Any] = field(default_factory=list)

    @property
    def completed(self) -> bool:
        return (self.end or {}).get("status") == "completed"


@dataclass
class Unit:
    """A review unit of the PR: its bundle, name and count, and its attempts in the order they were logged."""

    bundle: str
    name: str
    count: int
    attempts: list[Attempt] = field(default_factory=list)

    @property
    def label(self) -> str:
        suffix = f" (count {self.count})" if self.count > 1 else ""
        return f"`{Path(self.bundle).name}` `{self.name}`{suffix}"

    def reported(self) -> list[Attempt]:
        return [a for a in self.attempts if a.completed and a.report is not None]


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)  # noqa: S603, S607 - fixed argv, no shell
    if result.returncode != 0:
        raise BriefError(f"git {args[0]} failed: {result.stderr.strip()[:200]}")
    return result.stdout


def _entries(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def changed_logs(repo: Path, merge_base: str, head: str) -> list[str]:
    names = git(repo, "diff", "--name-only", merge_base, head, "--", "docs/slices").split()
    return sorted(n for n in names if Path(n).name == LOG_NAME and (repo / n).is_file())


def units_of_log(repo: Path, log: str, merge_base: str) -> list[Unit]:
    """The units whose attempts this PR logged: the start entries the log at the merge-base does not hold."""
    before = subprocess.run(["git", "-C", str(repo), "show", f"{merge_base}:{log}"],  # noqa: S603, S607 - fixed argv
                            capture_output=True, text=True, check=False).stdout
    known = {e["attempt"] for e in _entries(before) if e.get("event") == "start"}
    entries = _entries((repo / log).read_bytes().decode("utf-8"))
    ends = {e["attempt"]: e for e in entries if e.get("event") == "end"}
    units: dict[tuple[str, int], Unit] = {}
    for start in (e for e in entries if e.get("event") == "start" and e["attempt"] not in known):
        unit = units.setdefault((start["unit"], start.get("count", 1)),
                                Unit(str(Path(log).parent), start["unit"], start.get("count", 1)))
        unit.attempts.append(_attempt(repo, start, ends.get(start["attempt"])))
    return list(units.values())


def _attempt(repo: Path, start: dict[str, Any], end: dict[str, Any] | None) -> Attempt:
    record = repo / checker.record_of(start)
    text = record.read_bytes().decode("utf-8") if record.is_file() else ""
    section = records.parse_record(text)[0].get(start["attempt"])
    block = section.blocks.get("report") if section else None
    answers = launcher.answers_section(text, start["attempt"])
    return Attempt(start, end, json.loads(block) if block else None, launcher.answer_rows(answers) if answers else [])


def integrity_problems(repo: Path, logs: list[str], units: list[Unit]) -> list[str]:
    """What would make the brief omit something: the record check's problems for these logs, and, for attempts the
    record check does not cover (logged before slice 4.3), a missing Report block or a finding without its answer.
    The answer rules are the record check's: an attempt it does not cover is frozen under the rules of its time (round
    2 of slice 4: 4.1's medium finding answered `deferred:`), so the brief checks only that each finding has its row."""
    problems = [p for log in logs for p in checker.check_log(repo, repo / log)]
    for unit in units:
        for attempt in (a for a in unit.attempts if a.completed):
            name = f"{unit.bundle}: {attempt.start['attempt']}"
            if attempt.report is None:
                problems.append(f"{name}: completed, but its record holds no Report block")
            elif attempt.report.get("findings") and not attempt.answers:
                problems.append(f"{name}: its report has findings and the record has no answers to it")
            else:
                rows = Counter(row.finding for row in attempt.answers)
                problems += [f"{name}: finding {f['id']} has {rows[f['id']]} answer rows"
                             for f in attempt.report.get("findings", []) if rows[f["id"]] != 1]
    return sorted(set(problems))


@dataclass
class Brief:
    """What the brief shows, collected from the units; `final` says whether one of them is a final review unit."""

    rows: list[str] = field(default_factory=list)
    owner: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    undetermined: list[str] = field(default_factory=list)
    disputed: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    origins: Counter[tuple[str, str]] = field(default_factory=Counter)
    final: bool = False


def _answer_to(attempt: Attempt, finding: str) -> Any:
    return next((row for row in attempt.answers if row.finding == finding), None)


def _found_by(unit: Unit, attempt: Attempt) -> str:
    stages = attempt.start.get("stages") or {}
    return ", ".join(sorted(stages)) if stages else unit.name


def last_verdicts(unit: Unit) -> str:
    """The verdict of each reviewer of the unit's last round with a released report, by its label when the round had
    several reviewers (several reviewers in one round count as one round)."""
    reported = unit.reported()
    if not reported:
        return "no completed attempt"
    last_round = max(a.start["round"] for a in reported)
    verdicts = {a.start["reviewer"]: (a.end or {}).get("verdict", "—") for a in reported if a.start["round"] == last_round}
    return next(iter(verdicts.values())) if len(verdicts) == 1 else ", ".join(f"{r}: {v}" for r, v in sorted(verdicts.items()))


def finding_counts(unit: Unit) -> Counter[str]:
    """Distinct findings by their latest severity: a re-raised finding keeps its ID and counts once."""
    latest: dict[tuple[str, str], str] = {}
    for attempt in unit.reported():
        for finding in attempt.report.get("findings", []):  # type: ignore[union-attr]
            latest[(attempt.start["reviewer"], finding["id"])] = finding["severity"]
    return Counter(latest.values())


def _unit_row(unit: Unit, brief: Brief, open_before: int) -> str:
    last = last_verdicts(unit)
    counts = finding_counts(unit)
    rounds = max((a.start["round"] for a in unit.attempts), default=0)
    opened = len(brief.owner) + len(brief.concerns) + len(brief.undetermined) + len(brief.disputed) - open_before
    state = "not reviewed: no completed attempt" if not unit.reported() else (
        "nothing open" if opened == 0 else f"{opened} for the owner")
    cells = [unit.label, str(last), str(rounds), *(str(counts.get(s, 0)) for s in SEVERITIES), state]
    return "| " + " | ".join(cells) + " |"


def _collect_findings(unit: Unit, brief: Brief) -> None:
    for attempt in unit.reported():
        for finding in attempt.report.get("findings", []):  # type: ignore[union-attr]
            row = _answer_to(attempt, finding["id"])
            answer = row.answer if row else "(no answer)"
            word = launcher.answer_word(answer) if row else None
            where = f"{unit.label} {finding['id']} ({finding['severity']})"
            brief.origins[(finding.get("origin_stage", "unknown"), _found_by(unit, attempt))] += 1
            if finding.get("kind") == "decision_concern":
                brief.concerns.append(f"{where}: {answer}")
            elif word == "owner":
                brief.owner.append(f"{where}: {answer}")
            if word == "rejected" and finding["severity"] in launcher.FIXED_SEVERITIES:
                brief.rejected.append(f"{where}: {answer}")


def _collect_rechecks(unit: Unit, brief: Brief) -> None:
    """`cannot determine` answers, and findings a recheck re-raised whose latest answer is again `rejected:` (for a
    blocking, high or medium finding the record check refuses that since R2-3)."""
    reraised: dict[str, Attempt] = {}
    for attempt in unit.reported():
        for entry in attempt.report.get("accounted", []):  # type: ignore[union-attr]
            if entry.get("status") == "cannot determine":  # with the answer to it, if any (R2-3)
                row = _answer_to(attempt, entry["item"])
                answered = f"; answered: {row.answer}" if row else ""
                brief.undetermined.append(f"{unit.label} {entry['item']}: {entry.get('note', '')}{answered}")
            elif entry.get("status") == "re-raised":
                reraised[entry["item"]] = attempt
            elif entry.get("status") == "accepted":
                reraised.pop(entry["item"], None)
    for finding, attempt in sorted(reraised.items()):
        row = _answer_to(attempt, finding)
        if row is not None and launcher.answer_word(row.answer) == "rejected":
            brief.disputed.append(f"{unit.label} {finding}: re-raised by the recheck, answered again: {row.answer}")


def summarise(units: list[Unit]) -> Brief:
    brief = Brief(final=any(unit.name == "final" for unit in units))
    for unit in units:
        before = len(brief.owner) + len(brief.concerns) + len(brief.undetermined) + len(brief.disputed)
        _collect_findings(unit, brief)
        _collect_rechecks(unit, brief)
        brief.rows.append(_unit_row(unit, brief, before))
    return brief


def _items(title: str, items: list[str]) -> list[str]:
    return [f"**{title}**", "", *([f"- {item}" for item in items] or ["None."]), ""]


def render(brief: Brief, head: str, merge_base: str) -> str:
    lines = ["### Decision brief", "",  # under the decision page's own "Review outcome" heading
             f"Built by `scripts/review_brief.py` from the review units this PR adds (head `{head[:12]}`, merge-base "
             f"`{merge_base[:12]}`). The plans and records are worth reading where this brief points.", "",
             "| Unit | Last verdict | Rounds | Blocking | High | Medium | Low | Open |",  # findings counted once each
             "| --- | --- | --- | --- | --- | --- | --- | --- |", *brief.rows, ""]
    if not brief.final:
        lines += ["No unit `final` among the review units this PR adds: a plan PR and a small slice's PR have none, a "
                  "final PR needs one (`AGENTS.md`, slice workflow).", ""]
    lines += _items("Answered `owner:`", brief.owner) + _items("Decision concerns", brief.concerns)
    lines += _items("`cannot determine` in a recheck", brief.undetermined)
    lines += _items("Still disputed after a recheck", brief.disputed)
    lines += _items("Blocking, high and medium findings answered `rejected`", brief.rejected)
    found_by = sorted({f for _o, f in brief.origins})
    lines += ["**Where findings started** (origin stage of each finding, against the review that found it: its "
              "`--stage` lists, or its unit when it had none)", ""]
    if brief.origins:
        lines += ["| Origin | " + " | ".join(found_by) + " |", "| --- |" + " --- |" * len(found_by)]
        for origin in sorted({o for o, _f in brief.origins}):
            lines.append(f"| {origin} | " + " | ".join(str(brief.origins.get((origin, f), 0)) for f in found_by) + " |")
    else:
        lines.append("No findings.")
    return "\n".join([*lines, ""])


def build(repo: Path, base: str, head: str) -> str:
    merge_base = git(repo, "merge-base", base, head).strip()
    head_sha = git(repo, "rev-parse", head).strip()
    logs = changed_logs(repo, merge_base, head_sha)
    units = [unit for log in logs for unit in units_of_log(repo, log, merge_base)]
    problems = integrity_problems(repo, logs, units)
    if problems:
        raise BriefError("the records cannot give a complete brief:\n" + "\n".join(f"  - {p}" for p in problems))
    return render(summarise(units), head_sha, merge_base)


def main(argv: list[str] | None = None, repo: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="the base branch ref, for example origin/poc/agentic-sdlc")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)
    try:
        print(build(repo, args.base, args.head))
    except BriefError as error:
        print(f"[review-brief] FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
