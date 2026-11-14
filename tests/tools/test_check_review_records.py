"""Tooling tests for slice 4.3's review records (test plan of poc-4-3-review-records): the launcher writes every
record block exactly, and `scripts/check_review_records.py` fails on every kind of mismatch, on answers changed after
a recheck read them, and on answers a finding's severity does not allow.

Records are written by the real launcher with the fake `claude` (the launcher's fixture, evidence stubbed), then
edited by hand to make each kind of mismatch.
"""

from __future__ import annotations

import importlib.util
import json
import os
import signal
import sys
from pathlib import Path

import pytest

from tests.tools import test_run_independent_review as base

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("check_review_records", ROOT / "scripts" / "check_review_records.py")
assert _spec and _spec.loader
check = importlib.util.module_from_spec(_spec)
sys.modules["check_review_records"] = check
_spec.loader.exec_module(check)
launcher = base.launcher
records = launcher._RECORDS
fx = base.fx
RECORD, LOG = base.RECORD, base.LOG
FACT, QUOTE = base.FACT, base.QUOTE


def _problems(fx: base.Fixture) -> list[str]:
    return check.check_review_records(fx.work)


def _record(fx: base.Fixture) -> Path:
    return fx.work / RECORD


def _edit(fx: base.Fixture, old: str, new: str) -> None:
    text = _record(fx).read_text()
    assert old in text, old
    _record(fx).write_text(text.replace(old, new, 1))


def _completed(fx: base.Fixture, *findings: dict) -> None:
    fx.evidence = ["no CI run for this commit"]
    fx.scenario(base._reply(list(findings), accounted=[base._accounted("EV1", "explained")],
                            verdict="no" if findings else "yes"))
    assert base._run(fx) == 0


# --- The launcher writes the blocks (S43-D1) ------------------------------------------------------------------------


def test_completed_attempt_leaves_prompt_evidence_and_report_blocks_that_the_check_accepts(fx: base.Fixture) -> None:
    _completed(fx)
    sections, form = records.parse_record(_record(fx).read_text())
    section = sections["unit1/c1/r1/A/1"]
    start, end = fx.log()[0], fx.log()[1]
    assert form == [] and start["record_blocks"] == 1
    assert launcher.sha256_text(section.blocks["prompt"]) == start["prompt_sha256"]
    assert launcher.sha256_text(section.blocks["evidence"]) == start["evidence_sha256"]
    assert launcher.sha256_text(section.blocks["report"]) == end["report_sha256"]
    assert "Status: completed; approvable within the threat model: yes." in _record(fx).read_text()
    assert _problems(fx) == []


def test_text_holding_seven_backticks_gets_an_eight_backtick_fence(fx: base.Fixture) -> None:
    fx.prompt.write_text("A task quoting a fence: ```````\n")
    _completed(fx, base._finding("X1", problem="a report quoting ``````` too"))
    text = _record(fx).read_text()
    assert "````````markdown\nA task quoting a fence: ```````\n````````" in text
    assert "````````json\n" in text
    base._answers(fx, "unit1/c1/r1/A/1", "| X1 | high | rejected: style |")
    assert [p for p in _problems(fx) if "Report block" in p or "Prompt block" in p] == []


@pytest.mark.parametrize("scenario", [{"result": {"result": "not json"}}, {"reads": ["AGENTS.md"]}],
                         ids=["malformed", "empty-review"])
def test_failed_attempt_keeps_its_prompt_and_evidence_and_a_status_line(fx: base.Fixture, scenario: dict) -> None:
    fx.scenario(scenario)
    assert base._run(fx) == 1
    section = records.parse_record(_record(fx).read_text())[0]["unit1/c1/r1/A/1"]
    assert set(section.blocks) == {"prompt", "evidence"}
    assert "Status: failed (" in _record(fx).read_text()
    assert _problems(fx) == []


def test_withheld_attempt_keeps_its_prompt_and_evidence_and_says_it_was_withheld(fx: base.Fixture) -> None:
    pem = base._pem_private_key()
    fx.scenario(base._reply([base._finding("X", severity="low", problem=pem)]))
    assert base._run(fx) == 3
    text = _record(fx).read_text()
    assert "Status: withheld (the publication check found a secret in the report" in text
    assert pem.splitlines()[1] not in text and "#### Report" not in text
    assert _problems(fx) == []
    fx.scenario(base._reply())
    assert base._run(fx) == 0  # the next run reruns the reviewer; the withheld status stays as it was
    assert "Status: withheld (the publication check" in _record(fx).read_text() and _problems(fx) == []


def test_killed_attempt_gets_an_interrupted_status_line_and_the_check_passes(fx: base.Fixture) -> None:
    fx.scenario({"sleep": 30}, {})
    proc = base._start_launcher(fx)
    base._wait_for_call(fx, proc)
    os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()
    assert "Status: started." in _record(fx).read_text()
    assert base._run(fx) == 0
    text = _record(fx).read_text()
    assert "Status: interrupted (no end entry" in text and "Status: started." not in text
    assert _problems(fx) == []


def test_section_written_but_never_logged_is_removed_by_the_next_run(fx: base.Fixture) -> None:
    _completed(fx)
    start = {**fx.log()[0], "attempt": "unit1/c1/r2/A/1", "round": 2}
    text = _record(fx).read_text()
    _record(fx).write_text(text + "\n" + records.start_text(start, "a task\n", "evidence\n", text))
    assert any("has a heading but no entry" in p for p in _problems(fx))
    assert base._run(fx, unit="unit2") == 0  # any run of the same record recovers it first
    after = _record(fx).read_text()
    assert "unit1/c1/r2/A/1" not in after and "## Round 2" not in after and _problems(fx) == []


@pytest.mark.parametrize("tail", ["### Attempt notes\n\nThe author's own text.\n",
                                  "### Attempt unit1/c1/r9/A/1\n\nStatus: started.\n\nNot a launcher section.\n",
                                  "  ```python title\n### Attempt unit1/c1/r9/A/1\n  ```\n"],
                         ids=["word-heading", "unlogged-but-not-the-launchers", "inside-an-indented-fence"])
def test_text_that_is_not_a_launcher_section_is_never_removed(fx: base.Fixture, tail: str) -> None:
    _completed(fx, base._finding("X1"))
    base._answers(fx, "unit1/c1/r1/A/1", "| X1 | high | fixed: scripts/review_me.py: g |", extra="\n" + tail)
    before = _record(fx).read_text()
    assert base._run(fx, unit="unit2") == 0
    assert _record(fx).read_text().startswith(before)


def test_parallel_reviewers_leave_two_whole_separate_sections(fx: base.Fixture) -> None:
    fx.scenario({"sleep": 0.5})
    assert base._run(fx, labels=("A", "B")) == 0
    sections = records.parse_record(_record(fx).read_text())[0]
    for attempt in ("unit1/c1/r1/A/1", "unit1/c1/r1/B/1"):
        assert set(sections[attempt].blocks) == {"prompt", "evidence", "report"}
    assert _problems(fx) == []


# --- The prompt is scanned before the call (S43-D2) -----------------------------------------------------------------


@pytest.mark.parametrize("where", ["task", "evidence", "home-path", "answers"])
def test_secret_or_local_path_in_the_prompt_is_refused_before_anything_is_written(
        fx: base.Fixture, where: str, capsys: pytest.CaptureFixture[str]) -> None:
    pem = base._pem_private_key()
    commit, round_no = None, 1
    if where == "task":
        fx.prompt.write_text(f"Review this.\n{pem}")
    elif where == "evidence":
        fx.evidence = [f"a leaked key {pem}"]
    elif where == "home-path":
        fx.prompt.write_text(f"See {os.path.expanduser('~')}/notes.txt\n")
    else:
        commit, round_no = base._recheck(fx, f"| X1 | high | rejected: the key below is a test value, {FACT} |",
                                         extra=f"\n{pem}"), 2
        fx.scenario(base._reply(accounted=[base._accounted("X1")]))
    before_log, before_record = (fx.work / LOG).read_text(), _record(fx).read_text()
    calls = len(fx.calls())
    assert base._run(fx, round_no=round_no, commit=commit) == 2
    err = capsys.readouterr().err
    assert len(fx.calls()) == calls and (fx.work / LOG).read_text() == before_log
    assert _record(fx).read_text() == before_record
    assert "nothing was sent or written" in err
    assert pem.splitlines()[1] not in err and os.path.expanduser("~") + "/notes" not in err


def test_task_prompt_without_a_final_newline_is_refused(fx: base.Fixture) -> None:
    fx.prompt.write_text("No newline at the end")
    assert base._run(fx) == 2 and fx.calls() == []


# --- The check: blocks (S43-D3) -------------------------------------------------------------------------------------


@pytest.mark.parametrize("block", ["Prompt", "Evidence", "Report"])
def test_one_changed_character_in_a_block_fails(fx: base.Fixture, block: str) -> None:
    _completed(fx)
    text = _record(fx).read_text()
    label = text.index(f"#### {block}\n")
    fence_line_end = text.index("\n", text.index("```", label)) + 1
    _record(fx).write_text(text[:fence_line_end] + "X" + text[fence_line_end:])
    assert any(f"the {block} block does not match" in p for p in _problems(fx))


def test_report_block_under_another_attempts_heading_fails(fx: base.Fixture) -> None:
    _completed(fx, base._finding("X1"))
    base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | high | rejected: style, {FACT}; owner: https://example.org/decision |")
    fx.scenario(base._reply(accounted=[base._accounted("X1", quotes=[QUOTE]), base._accounted("EV1", "explained")]))
    assert base._run(fx, round_no=2, commit=base._git(fx.work, "rev-parse", "HEAD")) == 0
    text = _record(fx).read_text()
    first = records.parse_record(text)[0]["unit1/c1/r1/A/1"].blocks["report"]
    second = records.parse_record(text)[0]["unit1/c1/r2/A/1"].blocks["report"]
    _record(fx).write_text(text.replace(second, first))
    assert any("unit1/c1/r2/A/1: the Report block does not match" in p for p in _problems(fx))


def test_heading_without_a_logged_attempt_and_logged_attempt_without_a_heading_fail(fx: base.Fixture) -> None:
    _completed(fx)
    _edit(fx, "### Attempt unit1/c1/r1/A/1", "### Attempt unit1/c1/r1/Z/1")
    problems = _problems(fx)
    assert any("unit1/c1/r1/Z/1 has a heading but no entry" in p for p in problems)
    assert any("logged attempt unit1/c1/r1/A/1 has no heading" in p for p in problems)


def test_logged_report_without_a_block_and_a_block_without_a_logged_report_fail(fx: base.Fixture) -> None:
    _completed(fx)
    _edit(fx, "#### Report", "#### Not the report")
    assert any("the released report has no Report block" in p for p in _problems(fx))
    fx.scenario({"result": {"result": "not json"}})
    assert base._run(fx, unit="unit2") == 1
    _edit(fx, "#### Not the report", "#### Report")
    text = _record(fx).read_text()
    report = records.parse_record(text)[0]["unit1/c1/r1/A/1"].blocks["report"]
    _record(fx).write_text(text.replace("Status: failed", f"Status: failed\n\n#### Report\n\n```json\n{report}```\n", 1))
    assert any("unit2/c1/r1/A/1: a Report block, but the log holds no released report" in p for p in _problems(fx))


def test_missing_record_fails(fx: base.Fixture) -> None:
    _completed(fx)
    _record(fx).unlink()
    assert _problems(fx) == [f"records: {RECORD}: missing; the attempt log names it"]


def test_fenced_snippet_inside_an_answers_section_is_not_a_block(fx: base.Fixture) -> None:
    _completed(fx, base._finding("X1"))
    base._answers(fx, "unit1/c1/r1/A/1", "| X1 | high | fixed: scripts/review_me.py: guarded |",
                  extra="\n```text\n#### Report\nnot a block\n```\n")
    assert _problems(fx) == []


def test_answers_changed_after_the_recheck_read_them_fail(fx: base.Fixture) -> None:
    _completed(fx, base._finding("X1"))
    commit = base._answers(fx, "unit1/c1/r1/A/1", "| X1 | high | fixed: scripts/review_me.py: guarded |")
    fx.scenario(base._reply(accounted=[base._accounted("X1"), base._accounted("EV1", "explained")]))
    assert base._run(fx, round_no=2, commit=commit) == 0
    assert _problems(fx) == []
    _edit(fx, "fixed: scripts/review_me.py: guarded", "fixed: scripts/review_me.py: guarded twice")
    assert any("the answers to unit1/c1/r1/A/1 changed after this recheck read them" in p for p in _problems(fx))


def test_attempts_logged_before_this_slice_are_not_checked(fx: base.Fixture) -> None:
    entries = [{"event": "start", "attempt": "old/c1/r1/A/1", "unit": "old", "withheld_sha256": {RECORD: None, LOG: None},
                "prompt_sha256": "0" * 64},
               {"event": "end", "attempt": "old/c1/r1/A/1", "status": "completed", "report_sha256": "1" * 64}]
    base._write(fx.work, LOG, "".join(json.dumps(e) + "\n" for e in entries))
    base._write(fx.work, RECORD, "# record\n\n### Attempt someone/else\n\nanything at all\n")
    assert _problems(fx) == []


def test_docs_check_runs_the_record_check(fx: base.Fixture) -> None:
    spec = importlib.util.spec_from_file_location("check_docs", ROOT / "scripts" / "check_docs.py")
    assert spec and spec.loader
    docs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(docs)
    _completed(fx)
    assert docs.check_records(fx.work) == []
    _record(fx).unlink()
    assert docs.check_records(fx.work) == [f"records: {RECORD}: missing; the attempt log names it"]


# --- The check: allowed answers (S43-D4) ----------------------------------------------------------------------------


OWNER_ROW_LINK = "owner: https://github.com/o/r/pull/1#issuecomment-3"


@pytest.mark.parametrize(("finding", "answer"), [
    (base._finding("X1", severity="blocking"), "fixed: scripts/review_me.py: guarded"),
    (base._finding("X1", severity="high"), "owner: https://github.com/o/r/pull/1#issuecomment-2"),
    (base._finding("X1", severity="medium"), "owner: docs/slices/demo/decisions.md"),
    (base._finding("X1", severity="low"), "deferred: #12"),
    (base._finding("X1", severity="low"), "rejected: style"),
    (base._finding("X1", severity="high"), f"rejected: disputed, M5-T49 covers it; {OWNER_ROW_LINK}"),
    (base._finding("X1", kind="decision_concern", severity="medium"), "owner: docs/slices/demo/decisions.md"),
], ids=["blocking-fixed", "high-owner", "medium-owner", "low-deferred", "low-rejected", "high-rejected-with-owner-link",
        "decision-concern-owner"])
def test_each_allowed_answer_passes(fx: base.Fixture, finding: dict, answer: str) -> None:
    _completed(fx, finding)
    base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | {finding['severity']} | {answer} |")
    assert _problems(fx) == []


@pytest.mark.parametrize("severity", ["blocking", "medium"])
def test_rejected_blocking_or_medium_finding_that_the_next_round_accepts_passes(fx: base.Fixture, severity: str) -> None:
    """R2-1: a rejected medium finding, like a blocking or high one, stands only when the next round accepts it."""
    _completed(fx, base._finding("X1", severity=severity))
    commit = base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | {severity} | rejected: it does not happen, scripts/review_me.py:1 |")
    assert any(f"X1 is a rejected {severity} finding that no later round accepted" in p for p in _problems(fx))
    fx.scenario(base._reply(accounted=[base._accounted("X1", quotes=[QUOTE]), base._accounted("EV1", "explained")]))
    assert base._run(fx, round_no=2, commit=commit) == 0
    assert _problems(fx) == []


# --- The check: a rejection cites a checkable fact (R2-2) -----------------------------------------------------------


@pytest.mark.parametrize("fact", ["M5-T49", "M3.S4-T2", "M4a-T3", "DEPLOY-K1", "UT-123", "tests/tools/test_x.py::test_y",
                                  "`make qa-trace`", "scripts/review_me.py:1", "AGENTS.md:40-52", "Makefile:12"],
                         ids=["harness", "harness-sub-slice", "harness-milestone-letter", "static", "unit", "tooling",
                              "gate", "file-and-line", "file-and-lines", "makefile-line"])
def test_a_rejection_citing_a_checkable_fact_of_each_shape_passes(fx: base.Fixture, fact: str) -> None:
    _completed(fx, base._finding("X1", severity="high"))
    base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | high | rejected: already covered by {fact}; {OWNER_ROW_LINK} |")
    assert _problems(fx) == []


@pytest.mark.parametrize(("severity", "reason"), [
    ("blocking", "the scenario does not happen"),
    ("high", "see docs/slices/demo/plan.md, which says so"),
    ("medium", "we make sure of it in the gate"),
    ("high", "CR-B8 settled it"),
    ("medium", "REQ-M1-R1 and REQ-SEC-D2 say so"),
], ids=["blocking-prose", "high-file-without-line", "medium-make-in-prose", "high-finding-id", "medium-requirement-ids"])
def test_a_rejection_of_a_blocking_high_or_medium_finding_that_cites_no_checkable_fact_fails(
        fx: base.Fixture, severity: str, reason: str) -> None:
    """R2-2: the owner link settles the dispute, but the rejection itself still has to cite a fact."""
    _completed(fx, base._finding("X1", severity=severity))
    base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | {severity} | rejected: {reason}; {OWNER_ROW_LINK} |")
    problems = _problems(fx)
    assert len(problems) == 1 and f"X1 is a rejected {severity} finding whose answer cites no checkable fact" in problems[0], problems


@pytest.mark.parametrize(("finding", "rows", "problem"), [
    (base._finding("X1"), (), "has findings and the record has no answers"),
    (base._finding("X1"), ("| X1 | high | accepted: fine |",), "does not start with fixed:"),
    (base._finding("X1", severity="low"), ("| X1 | low | deferred: later |",), "names no issue"),
    (base._finding("X1", severity="blocking"), ("| X1 | blocking | deferred: #3 |",), "cannot be answered deferred"),
    (base._finding("X1", severity="medium"), ("| X1 | medium | deferred: #3 |",), "cannot be answered deferred"),
    (base._finding("X1", severity="high"), ("| X1 | high | rejected: covered by M5-T49 |",), "no later round accepted"),
    (base._finding("X1", severity="medium"), ("| X1 | medium | rejected: covered by M5-T49 |",),
     "X1 is a rejected medium finding that no later round accepted"),
    (base._finding("X1", severity="high"), ("| X1 | high | rejected: see docs/slices/demo/plan.md:3 |",),
     "no later round accepted"),
    (base._finding("X1", kind="decision_concern", severity="low"), ("| X1 | low | rejected: no |",),
     "must be answered owner"),
    (base._finding("X1"), ("| X1 | high | fixed: scripts/review_me.py: g |", "| X9 | low | rejected: r |"),
     "which the report does not hold"),
], ids=["no-row", "other-first-word", "deferred-without-issue", "blocking-deferred", "medium-deferred",
        "high-rejected-alone", "medium-rejected-alone", "high-rejected-with-a-link-but-no-owner",
        "decision-concern-rejected", "row-for-unknown-id"])
def test_each_answer_the_rules_do_not_allow_fails(fx: base.Fixture, finding: dict, rows: tuple[str, ...],
                                                  problem: str) -> None:
    _completed(fx, finding)
    if rows:
        base._answers(fx, "unit1/c1/r1/A/1", *rows)
    assert any(problem in p for p in _problems(fx)), _problems(fx)


# --- Answers to review round 1 of the 4.3 implementation ----------------------------------------------------------


def test_docs_check_reports_the_record_problems_through_run_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = importlib.util.spec_from_file_location("check_docs_wiring", ROOT / "scripts" / "check_docs.py")
    assert spec and spec.loader
    docs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(docs)
    monkeypatch.setattr(docs, "check_records", lambda _root: ["records: PLANTED RECORD PROBLEM"])
    problems = docs.run_checks(ROOT, ROOT / "scripts" / "rogue_node_tests.sh", ROOT / "docs" / "test_spec.md")
    assert "records: PLANTED RECORD PROBLEM" in problems


@pytest.mark.parametrize("block", ["Prompt", "Evidence"])
def test_a_logged_attempt_without_its_prompt_or_evidence_block_fails(fx: base.Fixture, block: str) -> None:
    _completed(fx)
    _edit(fx, f"#### {block}\n", f"#### Not the {block.lower()}\n")
    assert any(f"no {block} block" in p for p in _problems(fx))


@pytest.mark.parametrize(("edit", "problem"), [
    (("#### Report\n\n```", "#### Report\n\nnot a fence\n\n```"), "the Report label has no fenced block after it"),
    (("### Attempt unit1/c1/r1/A/1\n", "### Attempt unit1/c1/r1/A/1\n\n### Attempt unit1/c1/r1/A/1\n"),
     "has more than one heading"),
], ids=["label-without-block", "heading-twice"])
def test_malformed_record_forms_fail(fx: base.Fixture, edit: tuple[str, str], problem: str) -> None:
    _completed(fx)
    _edit(fx, *edit)
    assert any(problem in p for p in _problems(fx)), _problems(fx)


def test_a_label_twice_and_an_unclosed_fence_fail(fx: base.Fixture) -> None:
    _completed(fx)
    text = _record(fx).read_text()
    evidence = records.parse_record(text)[0]["unit1/c1/r1/A/1"].blocks["evidence"]
    _record(fx).write_text(text + f"\n#### Evidence\n\n```text\n{evidence}```\n")
    assert any("Evidence block appears 2 times" in p for p in _problems(fx))
    _record(fx).write_text(text.replace("#### Report\n\n````json", "#### Report\n\n`````json", 1)
                           if "````json" in text else text.replace("#### Report\n\n```json", "#### Report\n\n````json", 1))
    assert any("the Report label has no fenced block after it" in p for p in _problems(fx))


def test_rejected_finding_that_the_next_round_re_raises_still_fails(fx: base.Fixture) -> None:
    _completed(fx, base._finding("X1", severity="blocking"))
    commit = base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | blocking | rejected: the scenario does not happen, {FACT} |")
    fx.scenario(base._reply([base._finding("X1", severity="blocking")],
                            accounted=[base._accounted("X1", "re-raised", quotes=[QUOTE]),
                                       base._accounted("EV1", "explained")],
                            verdict="no"))
    assert base._run(fx, round_no=2, commit=commit) == 0
    assert any("unit1/c1/r1/A/1: X1 is a rejected blocking finding that no later round accepted" in p for p in _problems(fx))


def test_an_acceptance_in_a_next_round_attempt_that_did_not_complete_settles_nothing(fx: base.Fixture) -> None:
    """4.4 critique, C-14: only a completed attempt's released report can accept a rejection; a Report block put
    into a failed attempt's section by hand does not."""
    _completed(fx, base._finding("X1", severity="blocking"))
    commit = base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | blocking | rejected: the scenario does not happen, {FACT} |")
    fx.scenario(base._reply(accounted=[base._accounted("X1", quotes=[QUOTE])]))  # leaves EV1 out, so the launcher fails it
    assert base._run(fx, round_no=2, commit=commit) == 1
    assert fx.log()[-1]["status"] == "failed"
    accepting = json.dumps({"findings": [], "accounted": [base._accounted("X1", quotes=[QUOTE])], "verdict": "yes"},
                           indent=2)
    _record(fx).write_text(_record(fx).read_text().rstrip("\n") + f"\n\n#### Report\n\n```json\n{accepting}\n```\n")
    problems = _problems(fx)
    assert any("X1 is a rejected blocking finding that no later round accepted" in p for p in problems), problems


def _re_raised_after(fx: base.Fixture, severity: str, first_answer: str) -> None:
    """Round 1 with X1 at `severity` answered `first_answer`; the recheck re-raises X1 at the same severity."""
    _completed(fx, base._finding("X1", severity=severity))
    commit = base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | {severity} | {first_answer} |")
    quotes = [QUOTE] if first_answer.startswith("rejected:") else None  # R2-7: a re-raised rejection is quoted
    fx.scenario(base._reply([base._finding("X1", severity=severity)], verdict="no", accounted=[
        base._accounted("X1", "re-raised", quotes=quotes), base._accounted("EV1", "explained")]))
    assert base._run(fx, round_no=2, commit=commit) == 0


def test_a_later_owner_answer_to_the_re_raised_finding_settles_the_rejection(fx: base.Fixture) -> None:
    _re_raised_after(fx, "high", "rejected: the scenario does not happen, scripts/review_me.py:1")
    base._answers(fx, "unit1/c1/r2/A/1", "| X1 | high | owner: docs/slices/demo/decisions.md |")
    assert _problems(fx) == []


# --- The check: one dispute round (R2-3) ----------------------------------------------------------------------------


@pytest.mark.parametrize("severity", ["blocking", "high", "medium"])
def test_a_re_raised_rejection_answered_rejected_again_fails(fx: base.Fixture, severity: str) -> None:
    _re_raised_after(fx, severity, "rejected: the scenario does not happen, scripts/review_me.py:1")
    base._answers(fx, "unit1/c1/r2/A/1", f"| X1 | {severity} | rejected: it still does not happen, scripts/review_me.py:1 |")
    problems = _problems(fx)
    assert any("unit1/c1/r2/A/1: X1 was re-raised after its rejection" in p for p in problems), problems


def test_a_re_raised_rejection_answered_with_a_fix_settles_the_rejection(fx: base.Fixture) -> None:
    """R2-3: a rejection the recheck does not accept goes to the owner or is fixed; the fix settles it too."""
    _re_raised_after(fx, "high", "rejected: the scenario does not happen, scripts/review_me.py:1")
    base._answers(fx, "unit1/c1/r2/A/1", "| X1 | high | fixed: scripts/review_me.py: guarded after all |")
    assert _problems(fx) == []


def test_a_re_raised_low_finding_may_be_rejected_again(fx: base.Fixture) -> None:
    """A low finding is the author's choice (R2-1), so the one-dispute rule does not bind it."""
    _re_raised_after(fx, "low", "rejected: style")
    base._answers(fx, "unit1/c1/r2/A/1", "| X1 | low | rejected: still style |")
    assert _problems(fx) == []


def test_a_re_raised_fix_may_be_rejected_once(fx: base.Fixture) -> None:
    """The one dispute round starts with a rejection: a fix the recheck re-raised may still be defended once."""
    _re_raised_after(fx, "high", "fixed: scripts/review_me.py: guarded")
    base._answers(fx, "unit1/c1/r2/A/1", f"| X1 | high | rejected: the fix holds, scripts/review_me.py:1; {OWNER_ROW_LINK} |")
    assert _problems(fx) == []


def test_an_unreadable_attempt_log_is_reported(fx: base.Fixture) -> None:
    base._write(fx.work, LOG, '{"event": "start", "attempt": "x"}\n')  # a start entry without its fields
    base._write(fx.work, "docs/slices/broken/review_attempts.jsonl", "not json\n")
    problems = _problems(fx)
    assert any("docs/slices/broken/review_attempts.jsonl: cannot be read as an attempt log" in p for p in problems)


@pytest.mark.parametrize("task", ["Review this.\n\n", "Line one.\r\nLine two.\r\n", "Page one.\fPage two.\n",
                                  "Ends in two blank lines.\n\n\n"],
                         ids=["blank-last-line", "crlf", "form-feed", "two-blank-lines"])
def test_prompt_block_hashes_as_logged_whatever_the_task_files_line_ends(fx: base.Fixture, task: str) -> None:
    fx.prompt.write_bytes(task.encode("utf-8"))
    _completed(fx)
    section = records.parse_record(_record(fx).read_bytes().decode("utf-8"))[0]["unit1/c1/r1/A/1"]
    assert section.blocks["prompt"] == task
    assert _problems(fx) == []


# --- Recovery paths the 4.4 critique found untested (CR-B8) -------------------------------------------------------


def _launcher_section(attempt: str) -> str:
    start = {"round": 2, "attempt": attempt, "reviewer": "A", "model": "m", "effort": "medium", "mode": "recheck",
             "commit": "c" * 40, "base_commit": "b" * 40}
    return records.start_text(start, "task\n", "evidence\n", "")


def test_recovery_removes_the_round_heading_written_with_its_first_unlogged_section() -> None:
    kept = "# Review record\n\nAn author's paragraph.\n"
    text = kept + "\n" + _launcher_section("unit1/c1/r2/A/1")
    assert "## Round 2" in text
    assert records.truncate_unlogged_tail(text, logged=set()) == kept


def test_finishing_an_attempt_the_record_has_no_section_for_is_refused() -> None:
    with pytest.raises(ValueError, match="no section for attempt unit1/c1/r2/A/1"):
        records.finish("# Review record\n", "unit1/c1/r2/A/1", "Status: completed.", "{}\n")


# --- Round 2 of slice 4: one home for the answer rules; a finding the recheck could not determine ------------------


def test_the_record_check_applies_the_launchers_answer_rules(fx: base.Fixture, monkeypatch: pytest.MonkeyPatch) -> None:
    """The rules live once, in the launcher (`answer_rule_problems`), which refuses a recheck before the call on what
    the record check fails after it; the record check holds no copy of them."""
    _completed(fx, base._finding("X1"))
    base._answers(fx, "unit1/c1/r1/A/1", "| X1 | high | fixed: scripts/review_me.py: guarded |")
    assert _problems(fx) == []
    monkeypatch.setattr(check.launcher, "answer_rule_problems", lambda *_args: ["PLANTED RULE PROBLEM"])
    assert _problems(fx) == [f"records: {RECORD}: unit1/c1/r1/A/1: PLANTED RULE PROBLEM"]
    assert not hasattr(check, "CHECKABLE_FACT") and not hasattr(check, "FIXED_SEVERITIES")


def _undetermined_after(fx: base.Fixture, *other: dict) -> None:
    """Round 1 finds X1 (high), answered by a rejection with a fact; the recheck accounts X1 as `cannot determine`,
    so its report does not hold X1, and reports the findings `other`."""
    _completed(fx, base._finding("X1"))
    commit = base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | high | rejected: it does not happen, {FACT} |")
    fx.scenario(base._reply(list(other), verdict="no", accounted=[
        base._accounted("X1", "cannot determine", note="the copy does not settle it"), base._accounted("EV1", "explained")]))
    assert base._run(fx, round_no=2, commit=commit) == 0


@pytest.mark.parametrize(("rows", "problem"), [
    (("| X1 | high | owner: docs/slices/demo/decisions.md |",), None),
    (("| X1 | high | fixed: scripts/review_me.py: guarded after all |",), None),
    ((), "unit1/c1/r1/A/1: X1 is a rejected high finding that no later round accepted"),
    ((f"| X1 | high | rejected: it still does not happen, {FACT} |",),
     "unit1/c1/r2/A/1: X1 was accounted cannot determine, so it is answered fixed: or owner:"),
    (("| X1 | low | owner: docs/slices/demo/decisions.md |",),
     "unit1/c1/r2/A/1: answer row for X1 says 'low'; the finding is 'high'"),
    (("| X1 | high | owner: asked in chat |",), "unit1/c1/r2/A/1: owner answer to X1 gives no link"),
], ids=["owner", "fixed", "no-answer", "rejected-again", "relabelled", "owner-without-link"])
def test_a_finding_the_recheck_could_not_determine_is_answered_fixed_or_owner_in_the_next_answers(
        fx: base.Fixture, rows: tuple[str, ...], problem: str | None) -> None:
    """R2-3 and S43-D4's gap: the recheck's report does not hold the undetermined finding, yet the answers to it may
    hold its row, which settles the earlier rejection; a recheck with another finding (Y1) is checked as before."""
    _undetermined_after(fx, base._finding("Y1", severity="low"))
    base._answers(fx, "unit1/c1/r2/A/1", "| Y1 | low | rejected: style |", *rows)
    problems = _problems(fx)
    assert (problems == []) if problem is None else any(problem in p for p in problems), problems


def test_the_answers_to_a_recheck_without_findings_are_checked_too(fx: base.Fixture) -> None:
    """Before round 2, a recheck without findings had its answers skipped, so any `owner:` word settled a rejection."""
    _undetermined_after(fx)
    base._answers(fx, "unit1/c1/r2/A/1", "| X1 | high | owner: asked in chat |")
    assert any("unit1/c1/r2/A/1: owner answer to X1 gives no link" in p for p in _problems(fx)), _problems(fx)
    _edit(fx, "owner: asked in chat", "owner: docs/slices/demo/decisions.md")
    assert _problems(fx) == []


def test_a_re_raised_rejection_keeps_its_id_so_its_fix_or_owner_row_is_accepted(fx: base.Fixture) -> None:
    """The re-raised path of the same gap: the re-raised finding is in the recheck's findings under its ID."""
    _re_raised_after(fx, "high", f"rejected: the scenario does not happen, {FACT}")
    report = json.loads(records.parse_record(_record(fx).read_text())[0]["unit1/c1/r2/A/1"].blocks["report"])
    assert [f["id"] for f in report["findings"]] == ["X1"]
    base._answers(fx, "unit1/c1/r2/A/1", "| X1 | high | fixed: scripts/review_me.py: guarded after all |")
    assert _problems(fx) == []
