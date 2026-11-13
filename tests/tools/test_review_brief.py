"""Tooling tests for `scripts/review_brief.py`, the decision brief of a PR (slice 4.6, S46-D13).

The brief is built from attempt logs and records that the launcher writes in its throwaway repository (with the fake
`claude`), so it reads records exactly as the launcher writes them. The CI line is tested with fake API answers.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

from tests.tools import test_run_independent_review as base

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("review_brief", ROOT / "scripts" / "review_brief.py")
assert _spec and _spec.loader
brief_module = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("review_brief", brief_module)
_spec.loader.exec_module(brief_module)
fx = base.fx
NO_RUNS: dict[str, Any] = {"workflow_runs": []}


def _no_ci(_url: str) -> Any:
    return NO_RUNS


def _brief(fx: base.Fixture) -> str:
    base._git(fx.work, "fetch", "-q", "origin")
    base._git(fx.work, "remote", "set-url", "origin", "https://github.com/example/demo.git")
    return brief_module.build(fx.work, "origin/poc/base", "HEAD", _no_ci)


def _two_rounds(fx: base.Fixture, last_answer: str = "rejected: it still does not happen") -> None:
    """Round 1 with five findings and their answers; a recheck that re-raises one and cannot settle another; the
    answers to the recheck."""
    findings = [base._finding("X1", severity="medium"), base._finding("X2", severity="medium"),
                base._finding("X3", kind="decision_concern", severity="low", origin="discovery"),
                base._finding("X4", severity="high"), base._finding("X5", severity="high", origin="tests first")]
    commit = base._recheck(fx, "| X1 | medium | rejected: the scenario does not happen |",
                           "| X2 | medium | owner: docs/slices/demo/decisions.md |",
                           "| X3 | low | owner: docs/slices/demo/decisions.md |",
                           "| X4 | high | fixed: scripts/review_me.py: guarded |",
                           "| X5 | high | rejected: already covered by scripts/review_me.py |", findings=tuple(findings))
    fx.scenario(base._reply([base._finding("X1", severity="medium")], verdict="no", accounted=[
        base._accounted("X1", "re-raised"), base._accounted("X2"), base._accounted("X3"),
        base._accounted("X4", "cannot determine", note="NOTE ON X4"), base._accounted("X5")]))
    assert base._run(fx, round_no=2, commit=commit) == 0
    base._answers(fx, "unit1/c1/r2/A/1", f"| X1 | medium | {last_answer} |")


def test_the_brief_lists_every_item_the_owner_must_see(fx: base.Fixture) -> None:
    _two_rounds(fx)
    text = _brief(fx)
    assert "| `demo` `unit1` | no | 2 | 0 | 2 | 2 | 1 | 4 for the owner |" in text  # the re-raised X1 counts once
    owner = text.split("**Answered `owner:`**", 1)[1].split("**Decision concerns**", 1)[0]
    assert "X2 (medium): owner: docs/slices/demo/decisions.md" in owner and "X3" not in owner
    assert "X3 (low): owner:" in text.split("**Decision concerns**", 1)[1].split("**`cannot", 1)[0]
    assert "X4: NOTE ON X4" in text.split("**`cannot determine` in a recheck**", 1)[1].split("**Still", 1)[0]
    disputed = text.split("**Still disputed after a recheck**", 1)[1].split("**Blocking", 1)[0]
    assert "X1: re-raised by the recheck, answered again: rejected: it still does not happen" in disputed
    rejected = text.split("answered `rejected`**", 1)[1].split("**Where", 1)[0]
    assert "X5 (high): rejected: already covered by scripts/review_me.py" in rejected and "X1" not in rejected
    assert "| discovery | 1 |" in text and "| tests first | 1 |" in text and "| implementation | 4 |" in text


def test_a_re_raised_finding_answered_with_a_fix_is_not_disputed(fx: base.Fixture) -> None:
    _two_rounds(fx, last_answer="fixed: scripts/review_me.py: guarded now")
    disputed = _brief(fx).split("**Still disputed after a recheck**", 1)[1].split("**Blocking", 1)[0]
    assert disputed.strip() == "None."


def test_each_reviewer_of_the_last_round_has_its_verdict_shown(fx: base.Fixture) -> None:
    """4.6 review, F2: several reviewers in one round count as one round; the brief shows each one's verdict."""
    fx.scenario(base._reply(verdict="no"), base._reply(verdict="yes"))
    assert base._run(fx, labels=("A", "B")) == 0
    base._commit_all(fx.work, "two reviewers, no findings")
    row = next(line for line in _brief(fx).split("\n") if line.startswith("| `demo` `unit1`"))
    assert "A: " in row and "B: " in row and "no" in row and "yes" in row


def test_a_completed_attempt_whose_record_lost_its_report_fails_when_the_record_check_skips_it(fx: base.Fixture) -> None:
    """4.6 review, F1: attempts logged before slice 4.3 carry no `record_blocks`, so the record check skips them; the
    brief itself fails when such an attempt's record holds no Report block."""
    base._recheck(fx, "| X1 | high | fixed: scripts/review_me.py: guarded |")
    log = fx.work / base.LOG
    entries = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    log.write_text("".join(json.dumps({k: v for k, v in e.items() if k != "record_blocks"}) + "\n" for e in entries))
    record = fx.work / base.RECORD
    record.write_text(record.read_text().replace("#### Report\n", "#### Not the report\n", 1))
    base._commit_all(fx.work, "an attempt from before 4.3 whose record lost its report")
    with pytest.raises(brief_module.BriefError, match="completed, but its record holds no Report block"):
        _brief(fx)


def test_a_unit_with_nothing_open_says_so(fx: base.Fixture) -> None:
    base._recheck(fx, "| X1 | high | fixed: scripts/review_me.py: guarded |")
    text = _brief(fx)
    assert "| `demo` `unit1` | no | 1 | 0 | 1 | 0 | 0 | nothing open |" in text
    for title in ("**Answered `owner:`**", "**Decision concerns**", "**Still disputed after a recheck**"):
        assert text.split(title, 1)[1].lstrip().startswith("None.")


def test_a_unit_never_reviewed_and_a_missing_final_unit_are_shown(fx: base.Fixture) -> None:
    """The dry slice found a never-completed unit shown as "nothing open", and no word of a missing final unit."""
    fx.scenario({"reads": []})  # the review reads nothing, so the launcher fails it
    assert base._run(fx) == 1
    base._commit_all(fx.work, "a failed review")
    text = _brief(fx)
    assert "| not reviewed: no completed attempt |" in text and "No unit `final`" in text


def test_a_pr_with_a_final_unit_gets_no_missing_final_line(fx: base.Fixture) -> None:
    """Final review, FR-9: the branch a final PR takes."""
    assert base._run(fx, unit="final", record="docs/slices/demo/review_final.md") == 0
    base._commit_all(fx.work, "the final review")
    text = _brief(fx)
    assert "| `demo` `final` |" in text and "No unit `final`" not in text


def test_a_base_git_cannot_resolve_is_refused(fx: base.Fixture) -> None:
    with pytest.raises(brief_module.BriefError, match="git merge-base failed"):
        brief_module.build(fx.work, "origin/no-such-branch", "HEAD", _no_ci)


def test_a_finding_without_an_answer_fails_instead_of_a_brief_that_omits_it(fx: base.Fixture) -> None:
    base._first_round(fx, base._finding("X1", severity="medium"))
    base._commit_all(fx.work, "the review, not answered")
    with pytest.raises(brief_module.BriefError, match="has findings and the record has no answers"):
        _brief(fx)


def test_a_record_whose_block_differs_from_its_log_fails(fx: base.Fixture) -> None:
    base._recheck(fx, "| X1 | high | fixed: scripts/review_me.py: guarded |")
    record = fx.work / base.RECORD
    record.write_text(record.read_text().replace("Review the change. PROMPT MARKER", "Review the change. EDITED MARKER"))
    base._commit_all(fx.work, "an edited prompt block")
    with pytest.raises(brief_module.BriefError, match="Prompt block"):
        _brief(fx)


def test_main_writes_no_brief_and_fails_when_the_records_are_incomplete(fx: base.Fixture,
                                                                       capsys: pytest.CaptureFixture[str]) -> None:
    base._first_round(fx, base._finding("X1", severity="medium"))
    base._commit_all(fx.work, "the review, not answered")
    base._git(fx.work, "fetch", "-q", "origin")
    assert brief_module.main(["--base", "origin/poc/base"], repo=fx.work, fetch=_no_ci) == 1
    out = capsys.readouterr()
    assert "## Decision brief" not in out.out and "FAILED" in out.err


def _api(runs: list[dict[str, Any]], jobs: list[dict[str, Any]]) -> Any:
    def fetch(url: str) -> Any:
        return {"jobs": jobs} if "/jobs" in url else {"workflow_runs": runs}
    return fetch


def _broken(_url: str) -> Any:
    raise OSError("network down")


HEAD = "a" * 40
RUN = {"id": 7, "head_sha": HEAD}


@pytest.mark.parametrize(("fetch", "expected"), [
    (_api([RUN], [{"name": "qa-trace", "status": "completed", "conclusion": "success"}] * 2), "passed, all 2 jobs."),
    (_api([RUN], [{"name": "e2e", "status": "in_progress"}, {"name": "lint", "status": "completed",
                                                              "conclusion": "success"}]), "still running: e2e; not a pass yet."),
    (_api([RUN], [{"name": "e2e", "status": "completed", "conclusion": "failure"}]), "not passed: e2e (failure)."),
    (_api([RUN], [{"name": "e2e", "status": "completed", "conclusion": "skipped"}]), "not passed: e2e (skipped)."),
    (_api([], []), "no run for this commit; not a pass."),
    (_api([RUN], []), "no run with jobs for this commit; not a pass."),
    (_api([{"id": 8, "head_sha": "b" * 40}], []), "no run for this commit; not a pass."),
    (_broken, "cannot be read (OSError); not a pass."),
], ids=["all-passed", "running", "failed", "skipped", "no-run", "run-without-jobs", "other-commit", "unreadable"])
def test_the_ci_line_shows_a_pass_only_when_every_job_succeeded(tmp_path: Path, fetch: Any, expected: str) -> None:
    base._git(tmp_path, "init", "-q")
    base._git(tmp_path, "remote", "add", "origin", "https://github.com/example/demo.git")
    line = brief_module.ci_line(tmp_path, HEAD, fetch)
    assert line.endswith(expected), line
    assert ("passed, all" in line) is (expected.startswith("passed"))


def test_the_ci_line_of_a_repository_without_a_github_remote_is_not_a_pass(tmp_path: Path) -> None:
    base._git(tmp_path, "init", "-q")
    assert "cannot be read" in brief_module.ci_line(tmp_path, HEAD, _api([RUN], []))
