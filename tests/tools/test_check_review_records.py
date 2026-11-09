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
    assert "Status: withheld: the publication check found a secret in the report" in text
    assert pem.splitlines()[1] not in text and "#### Report" not in text
    assert _problems(fx) == []
    base._run(fx, labels=("A",))  # the next run marks the attempt interrupted in the log; the record stays valid
    assert _problems(fx) == []


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
    _record(fx).write_text(_record(fx).read_text() + "\n### Attempt unit1/c1/r1/B/1\n\nStatus: started.\n")
    assert any("has a heading but no entry" in p for p in _problems(fx))
    assert base._run(fx, unit="unit2") == 0  # any run of the same record recovers it first
    assert "unit1/c1/r1/B/1" not in _record(fx).read_text() and _problems(fx) == []


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
        commit, round_no = base._recheck(fx, "| X1 | high | rejected: the key below is a test value |",
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
    base._answers(fx, "unit1/c1/r1/A/1", "| X1 | high | rejected: style; owner: docs/x.md |")
    fx.scenario(base._reply(accounted=[base._accounted("X1"), base._accounted("EV1", "explained")]))
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


@pytest.mark.parametrize(("finding", "answer"), [
    (base._finding("X1", severity="blocking"), "fixed: scripts/review_me.py: guarded"),
    (base._finding("X1", severity="high"), "owner: https://github.com/o/r/pull/1#issuecomment-2"),
    (base._finding("X1", severity="medium"), "deferred: #12"),
    (base._finding("X1", severity="low"), "rejected: style"),
    (base._finding("X1", severity="high"), "rejected: disputed; owner: https://github.com/o/r/pull/1#issuecomment-3"),
    (base._finding("X1", kind="decision_concern", severity="medium"), "owner: docs/slices/demo/decisions.md"),
], ids=["blocking-fixed", "high-owner", "medium-deferred", "low-rejected", "high-rejected-with-owner-link",
        "decision-concern-owner"])
def test_each_allowed_answer_passes(fx: base.Fixture, finding: dict, answer: str) -> None:
    _completed(fx, finding)
    base._answers(fx, "unit1/c1/r1/A/1", f"| X1 | {finding['severity']} | {answer} |")
    assert _problems(fx) == []


def test_rejected_blocking_finding_that_the_next_round_accepts_passes(fx: base.Fixture) -> None:
    _completed(fx, base._finding("X1", severity="blocking"))
    commit = base._answers(fx, "unit1/c1/r1/A/1", "| X1 | blocking | rejected: the scenario does not happen |")
    assert any("X1 is a rejected blocking finding that no later round accepted" in p for p in _problems(fx))
    fx.scenario(base._reply(accounted=[base._accounted("X1"), base._accounted("EV1", "explained")]))
    assert base._run(fx, round_no=2, commit=commit) == 0
    assert _problems(fx) == []


@pytest.mark.parametrize(("finding", "rows", "problem"), [
    (base._finding("X1"), (), "has findings and the record has no answers"),
    (base._finding("X1"), ("| X1 | high | accepted: fine |",), "does not start with fixed:"),
    (base._finding("X1", severity="medium"), ("| X1 | medium | deferred: later |",), "names no issue"),
    (base._finding("X1", severity="blocking"), ("| X1 | blocking | deferred: #3 |",), "cannot be answered deferred"),
    (base._finding("X1", severity="high"), ("| X1 | high | rejected: no |",), "no later round accepted"),
    (base._finding("X1", severity="high"), ("| X1 | high | rejected: see docs/slices/demo/plan.md |",),
     "no later round accepted"),
    (base._finding("X1", kind="decision_concern", severity="low"), ("| X1 | low | rejected: no |",),
     "must be answered owner"),
    (base._finding("X1"), ("| X1 | high | fixed: scripts/review_me.py: g |", "| X9 | low | rejected: r |"),
     "which the report does not hold"),
], ids=["no-row", "other-first-word", "deferred-without-issue", "blocking-deferred", "high-rejected-alone",
     "high-rejected-with-a-link-but-no-owner",
        "decision-concern-rejected", "row-for-unknown-id"])
def test_each_answer_the_rules_do_not_allow_fails(fx: base.Fixture, finding: dict, rows: tuple[str, ...],
                                                  problem: str) -> None:
    _completed(fx, finding)
    if rows:
        base._answers(fx, "unit1/c1/r1/A/1", *rows)
    assert any(problem in p for p in _problems(fx)), _problems(fx)
