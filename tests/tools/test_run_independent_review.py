"""Tooling tests for scripts/run_independent_review.py (agentic-sdlc-poc slice 2, test plan "launcher").

Every test builds a throwaway Git repository with a bare origin, and puts fake `claude` and `codex`
executables first on PATH. The fakes record each call (arguments, environment, working directory,
standard input, visible files) and print a scripted stream, so no test spends tokens.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_independent_review.py"
FAKES = Path(__file__).resolve().parent / "fakes"
_spec = importlib.util.spec_from_file_location("run_independent_review", SCRIPT)
assert _spec and _spec.loader
launcher = importlib.util.module_from_spec(_spec)
sys.modules["run_independent_review"] = launcher
_spec.loader.exec_module(launcher)

RECORD = "docs/slices/demo/review_demo.md"
LOG = "docs/slices/demo/review_attempts.jsonl"
REVIEWED = "scripts/review_me.py"
PR_COMMENT = "https://github.com/owner/repo/pull/7#issuecomment-123"


@dataclass
class Fixture:
    work: Path
    origin: Path
    home: Path
    commit: str
    prompt: Path

    def calls(self) -> list[dict]:
        calls = self.home / "calls"
        return [json.loads(p.read_text()) for p in sorted(calls.glob("*.json"))] if calls.exists() else []

    def log(self) -> list[dict]:
        path = self.work / LOG
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

    def scenario(self, *scenarios: dict) -> None:
        (self.home / "scenario.json").write_text(json.dumps(list(scenarios) or [{}]))
        (self.home / "counter").unlink(missing_ok=True)


def _git(repo: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@example.org"}
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,  # noqa: S603, S607 - test git
                          env=env).stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _commit_all(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def fx(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Fixture:
    origin, work, home, bin_dir = (tmp_path / n for n in ("origin.git", "work", "home", "bin"))
    for path in (work, home, bin_dir):
        path.mkdir()
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)  # noqa: S603, S607 - test git
    _git(work, "init", "-q", "-b", "main")
    _write(work, "AGENTS.md", "BASE RULE SENTENCE v1\n")
    _write(work, "tests/unit/AGENTS.md", "UNIT BASE RULE\n")
    _write(work, REVIEWED, "print('base')\n")
    _write(work, RECORD, "# record\nPRIOR REPORT TEXT\n")
    _write(work, LOG, "")
    _commit_all(work, "base")
    _git(work, "remote", "add", "origin", str(origin))
    _git(work, "push", "-q", "origin", "main:poc/base")
    _write(work, "AGENTS.md", "BASE RULE SENTENCE v1\nBRANCH MARKER SENTENCE\n")
    _write(work, "tests/unit/AGENTS.md", "UNIT BASE RULE\nBRANCH UNIT MARKER\n")
    _write(work, REVIEWED, "print('change')\n")
    commit = _commit_all(work, "change")
    _write(work, "untracked_secret.txt", "UNTRACKED CONTENT\n")
    for name, fake in (("claude", "fake_claude.py"), ("codex", "fake_codex.py")):
        shutil.copy(FAKES / fake, bin_dir / name)
        (bin_dir / name).chmod(0o755)
    prompt = tmp_path / "task.md"
    prompt.write_text("Review the change. PROMPT MARKER SENTENCE\n", encoding="utf-8")
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GITHUB_TOKEN", "planted-token-value-not-for-reviewers")
    fixture = Fixture(work, origin, home, commit, prompt)
    fixture.scenario({})
    return fixture


def _args(fx: Fixture, *extra: str, round_no: int = 1, labels: tuple[str, ...] = ("A",), commit: str | None = None) -> list[str]:
    args = ["--commit", commit or fx.commit, "--base", "poc/base", "--record", RECORD, "--unit", "unit1",
            "--round", str(round_no), "--path", REVIEWED]
    for label in labels:
        args += ["--reviewer", f"{label}:{fx.prompt}:claude-opus-5-5:high"]
    return args + list(extra)


def _run(fx: Fixture, *extra: str, **kwargs: object) -> int:
    return launcher.main(_args(fx, *extra, **kwargs), repo=fx.work)  # type: ignore[arg-type]


def _ends(fx: Fixture) -> list[dict]:
    return [e for e in fx.log() if e["event"] == "end"]


def _report(fx: Fixture, start: dict) -> Path:
    return fx.work / start["report_path"]


# --- Frozen copy -------------------------------------------------------------------------------


def test_copy_holds_the_tracked_tree_without_the_review_files(fx: Fixture) -> None:
    assert _run(fx) == 0
    files = fx.calls()[0]["files"]
    assert REVIEWED in files and "AGENTS.md" in files
    assert "untracked_secret.txt" not in files
    assert RECORD not in files and LOG not in files
    start = fx.log()[0]
    assert set(start["withheld_sha256"]) == {RECORD, LOG}
    assert all(isinstance(h, str) and len(h) == 64 for h in start["withheld_sha256"].values())
    assert "_review_inputs/change.diff" in files
    assert not Path(fx.calls()[0]["cwd"]).exists()  # the copy is deleted after the review


def test_change_diff_leaves_out_the_withheld_files(fx: Fixture, tmp_path: Path) -> None:
    _write(fx.work, RECORD, "# record\nROUND ONE ANSWERS\n")
    commit = _commit_all(fx.work, "record update")
    copy = tmp_path / "copy"
    launcher.make_frozen_copy(fx.work, commit, copy, [RECORD, LOG], "refs/remotes/origin/poc/base")
    diff = (copy / "_review_inputs" / "change.diff").read_text()
    assert REVIEWED in diff
    assert "ROUND ONE ANSWERS" not in diff and RECORD not in diff
    assert not (copy / RECORD).exists()


def test_unknown_commit_is_refused_before_any_call(fx: Fixture) -> None:
    assert _run(fx, commit="0" * 40) == 2
    assert fx.calls() == []


def test_symlink_pointing_outside_the_copy_is_refused(fx: Fixture) -> None:
    os.symlink("../../outside.txt", fx.work / "scripts" / "escape")
    commit = _commit_all(fx.work, "symlink")
    assert _run(fx, commit=commit) == 2
    assert fx.calls() == []


@pytest.mark.parametrize("attribute", ["export-ignore", "export-subst"])
def test_export_attributes_are_refused(fx: Fixture, attribute: str) -> None:
    _write(fx.work, ".gitattributes", f"scripts/review_me.py {attribute}\n")
    commit = _commit_all(fx.work, "attributes")
    assert _run(fx, commit=commit) == 2
    assert fx.calls() == []


# --- Approved rules ----------------------------------------------------------------------------


def test_rules_come_from_the_fetched_base_not_the_branch(fx: Fixture, tmp_path: Path) -> None:
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", "-b", "poc/base", str(fx.origin), str(other)], check=True)  # noqa: S603, S607 - test git
    _write(other, "AGENTS.md", "BASE RULE SENTENCE v2\n")
    _commit_all(other, "base moves on")
    _git(other, "push", "-q", "origin", "poc/base")
    assert _run(fx) == 0
    stdin = fx.calls()[0]["stdin"]
    assert "BASE RULE SENTENCE v2" in stdin and "UNIT BASE RULE" in stdin
    assert "BRANCH MARKER SENTENCE" not in stdin and "BRANCH UNIT MARKER" not in stdin
    assert fx.log()[0]["base_commit"] == _git(fx.work, "rev-parse", "refs/remotes/origin/poc/base")


# --- Confinement -------------------------------------------------------------------------------


def test_call_carries_the_confinement_flags_and_a_minimal_environment(fx: Fixture) -> None:
    assert _run(fx) == 0
    call = fx.calls()[0]
    assert call["argv"] == launcher.build_invocation("claude-opus-5-5", "high")[1:]
    for flag in ("--safe-mode", "--strict-mcp-config", "--no-session-persistence"):
        assert flag in call["argv"]
    argv = call["argv"]
    assert argv[argv.index("--setting-sources") + 1] == ""
    assert argv[argv.index("--tools") + 1] == "Read,Grep,Glob"
    assert argv[argv.index("--permission-mode") + 1] == "dontAsk"
    assert argv[argv.index("--mcp-config") + 1] == '{"mcpServers":{}}'
    assert argv[argv.index("--effort") + 1] == "high"
    assert not any(a.startswith("--allowedTools") or a.startswith("--allowed-tools") for a in argv)
    assert set(call["env"]) <= {"PATH", "HOME", "LANG"}
    assert "planted-token-value-not-for-reviewers" not in json.dumps(call["env"])
    assert fx.work.resolve() not in [Path(call["cwd"]).resolve(), *Path(call["cwd"]).resolve().parents]


@pytest.mark.parametrize("drop", ["--commit", "--base", "--record", "--unit", "--round"])
def test_missing_required_argument_is_refused(fx: Fixture, drop: str) -> None:
    args = _args(fx)
    index = args.index(drop)
    del args[index:index + 2]
    assert launcher.main(args, repo=fx.work) == 2
    assert fx.calls() == []


@pytest.mark.parametrize("reviewer", ["A:{p}:claude-opus-5-5", ":{p}:claude-opus-5-5:high", "A::claude-opus-5-5:high",
                                      "A:{p}::high", "A:{p}:claude-opus-5-5:", "A:{p}:claude-opus-5-5:default"])
def test_incomplete_reviewer_is_refused(fx: Fixture, reviewer: str) -> None:
    args = _args(fx, labels=())
    args += ["--reviewer", reviewer.format(p=fx.prompt)]
    assert launcher.main(args, repo=fx.work) == 2
    assert fx.calls() == []


# --- Invocation from the log -------------------------------------------------------------------


def test_invocation_and_hashes_are_rebuilt_from_a_log_entry(fx: Fixture) -> None:
    assert _run(fx) == 0
    start = fx.log()[0]
    argv, mismatches = launcher.invocation_from_entry(start, fx.work, fx.prompt)
    assert argv[1:] == fx.calls()[0]["argv"]
    assert mismatches == []
    fx.prompt.write_text("A changed task.\n", encoding="utf-8")
    _argv, mismatches = launcher.invocation_from_entry(start, fx.work, fx.prompt)
    assert mismatches == ["prompt_sha256", "full_prompt_sha256"]


# --- Attempt log -------------------------------------------------------------------------------


START_FIELDS = {"event", "attempt", "unit", "count", "round", "round_reviewers", "reviewer", "model", "effort",
                "cli_version", "commit", "tree", "base", "base_commit", "rules_sha256", "prompt_file",
                "prompt_sha256", "full_prompt_sha256", "paths_sha256", "withheld_sha256", "diff_sha256",
                "schema_sha256", "extension", "reset", "report_path", "started_at"}
END_FIELDS = {"event", "attempt", "status", "reason", "ended_at", "verdict", "report_sha256", "duration_ms", "turns",
              "tokens", "cost_usd_estimate", "tool_calls", "paths_read", "denied", "outside_calls", "outside",
              "other_tools", "other_tools_not_offered", "utilization"}


def test_log_has_one_start_and_one_end_entry_with_the_planned_fields(fx: Fixture) -> None:
    assert _run(fx, labels=("A", "B")) == 0
    entries = fx.log()
    assert [e["event"] for e in entries].count("start") == 2 and [e["event"] for e in entries].count("end") == 2
    for entry in entries:
        assert set(entry) == (START_FIELDS if entry["event"] == "start" else END_FIELDS)
    start = entries[0]
    assert start["round_reviewers"] == ["A", "B"] and start["cli_version"] == "9.9.9 (Claude Code)"
    assert start["paths_sha256"] == {REVIEWED: launcher.sha256_text("print('change')\n")}
    end = next(e for e in entries if e["event"] == "end" and e["attempt"] == start["attempt"])
    assert end["paths_read"] == [REVIEWED] and end["tool_calls"] == 1 and end["verdict"] == "yes"
    assert end["report_sha256"] == launcher.sha256_bytes(_report(fx, start).read_bytes())


def test_log_is_only_appended(fx: Fixture) -> None:
    assert _run(fx) == 0
    first = (fx.work / LOG).read_text()
    assert _run(fx, round_no=2) == 0
    assert (fx.work / LOG).read_text().startswith(first)


def test_log_holds_no_prompt_or_reply_text(fx: Fixture) -> None:
    finding = {"id": "X-B1", "kind": "blocking", "file": REVIEWED, "line": 1, "problem": "REPLY MARKER SENTENCE",
               "evidence": "e", "failure_scenario": "f"}
    fx.scenario({"result": {"structured_output": {"findings": [finding], "verdict": "no"}}})
    assert _run(fx) == 0  # a "no" verdict still completes the attempt
    text = (fx.work / LOG).read_text()
    assert "PROMPT MARKER SENTENCE" not in text and "REPLY MARKER SENTENCE" not in text
    assert _ends(fx)[0]["status"] == "completed"


# --- Interruption and the lock -----------------------------------------------------------------


def _start_launcher(fx: Fixture, *extra: str, **kwargs: object) -> subprocess.Popen:
    return subprocess.Popen([sys.executable, str(SCRIPT), *_args(fx, *extra, **kwargs)], cwd=fx.work,  # type: ignore[arg-type]  # noqa: S603 - the launcher under test
                            env=dict(os.environ), start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _wait_for_call(fx: Fixture, proc: subprocess.Popen) -> None:
    for _ in range(200):
        if fx.calls() and (fx.work / LOG).read_text().strip():
            return
        assert proc.poll() is None, proc.stderr.read() if proc.stderr else ""
        time.sleep(0.05)
    raise AssertionError("the launcher never reached the reviewer call")


def test_killed_launcher_releases_nothing_and_its_attempt_is_marked_interrupted(fx: Fixture) -> None:
    fx.scenario({"sleep": 30}, {})
    proc = _start_launcher(fx)
    _wait_for_call(fx, proc)
    os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()
    first = fx.log()
    assert [e["event"] for e in first] == ["start"]
    assert not _report(fx, first[0]).exists() and not Path(str(_report(fx, first[0])) + ".partial").exists()
    assert _run(fx) == 0
    entries = fx.log()
    assert entries[1] == {**entries[1], "event": "end", "attempt": first[0]["attempt"], "status": "interrupted"}
    assert entries[-1]["status"] == "completed" and entries[-1]["attempt"].endswith("/A/2")
    assert len(fx.calls()) == 2


def test_second_invocation_is_refused_while_the_first_holds_the_lock(fx: Fixture) -> None:
    fx.scenario({"sleep": 30})
    proc = _start_launcher(fx)
    try:
        _wait_for_call(fx, proc)
        assert _run(fx) == 2
        assert len(fx.calls()) == 1
    finally:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()


def _start(attempt: str, labels: list[str], label: str, report_path: str, round_no: int = 1) -> dict:
    return {"event": "start", "attempt": attempt, "unit": "unit1", "count": 1, "round": round_no,
            "round_reviewers": labels, "reviewer": label, "report_path": report_path}


def test_report_of_a_completed_attempt_is_released_on_the_next_invocation(fx: Fixture) -> None:
    report = "artifacts/reviews/unit1/a.json"
    text = json.dumps({"findings": [], "verdict": "yes"})
    _write(fx.work, report + ".partial", text)
    entries = [_start("unit1/c1/r1/A/1", ["A", "B"], "A", report),
               {"event": "end", "attempt": "unit1/c1/r1/A/1", "status": "completed", "verdict": "yes",
                "report_sha256": launcher.sha256_text(text)}]
    _write(fx.work, LOG, "".join(json.dumps(e) + "\n" for e in entries))
    assert _run(fx, labels=("A", "B")) == 0
    assert (fx.work / report).read_text() == text and not (fx.work / (report + ".partial")).exists()
    assert len(fx.calls()) == 1
    assert [e["reviewer"] for e in fx.log() if e["event"] == "start"] == ["A", "B"]


def test_partial_report_of_a_failed_attempt_is_deleted(fx: Fixture) -> None:
    report = "artifacts/reviews/unit1/a.json"
    _write(fx.work, report + ".partial", "{}")
    entries = [_start("unit1/c1/r1/A/1", ["A"], "A", report),
               {"event": "end", "attempt": "unit1/c1/r1/A/1", "status": "failed", "verdict": None, "report_sha256": None}]
    _write(fx.work, LOG, "".join(json.dumps(e) + "\n" for e in entries))
    assert _run(fx) == 0
    assert not (fx.work / (report + ".partial")).exists() and not (fx.work / report).exists()


def test_partial_report_without_an_end_entry_is_deleted_and_the_attempt_interrupted(fx: Fixture) -> None:
    report = "artifacts/reviews/unit1/a.json"
    _write(fx.work, report + ".partial", json.dumps({"findings": [], "verdict": "yes"}))
    _write(fx.work, LOG, json.dumps(_start("unit1/c1/r1/A/1", ["A"], "A", report)) + "\n")
    assert _run(fx) == 0
    assert not (fx.work / (report + ".partial")).exists() and not (fx.work / report).exists()
    assert fx.log()[1] == {**fx.log()[1], "attempt": "unit1/c1/r1/A/1", "status": "interrupted"}


def test_symlinked_copy_root_still_counts_reads_inside_the_copy(tmp_path: Path) -> None:
    real = tmp_path / "real"
    (real / "scripts").mkdir(parents=True)
    link = tmp_path / "link"
    link.symlink_to(real)
    assert launcher.relative_to_copy(str(real / "scripts" / "x.py"), link) == "scripts/x.py"
    assert launcher.relative_to_copy(str(tmp_path / "outside.txt"), link) is None


def test_corrupt_log_line_is_refused(fx: Fixture) -> None:
    _write(fx.work, LOG, "not json\n")
    assert _run(fx) == 2
    assert fx.calls() == []


# --- Round admission ---------------------------------------------------------------------------


def _done(round_no: int, label: str, verdict: str | None, labels: list[str], status: str = "completed") -> list[dict]:
    """A start and an end entry of one attempt; the attempt ID follows the launcher's scheme."""
    attempt = f"unit1/c1/r{round_no}/{label}/1"
    return [_start(attempt, labels, label, "r", round_no),
            {"event": "end", "attempt": attempt, "status": status, "verdict": verdict}]


def _admit(entries: list[dict], round_no: int, labels: list[str], extension: str | None = None,
           reset: str | None = None) -> launcher.Admission:
    return launcher.admit_round(entries, "unit1", round_no, labels, (extension, reset))


def test_round_one_runs_all_four_listed_reviewers_in_one_invocation(fx: Fixture) -> None:
    assert _run(fx, labels=("A", "B", "C", "D")) == 0
    starts = [e for e in fx.log() if e["event"] == "start"]
    assert sorted(e["reviewer"] for e in starts) == ["A", "B", "C", "D"]
    assert {e["round"] for e in starts} == {1} and len(fx.calls()) == 4
    assert _run(fx, round_no=2, labels=("A", "B", "C", "D")) == 0  # the next round is 2: round 1 counted once


def test_next_round_runs_when_every_reviewer_completed_and_may_drop_yes_verdicts() -> None:
    entries = _done(1, "A", "yes", ["A", "B"]) + _done(1, "B", "no", ["A", "B"])
    assert _admit(entries, 2, ["B"]).to_run == ["B"]
    assert _admit(entries, 2, ["A", "B"]).to_run == ["A", "B"]


def test_later_invocation_of_the_same_round_runs_only_reviewers_without_a_completed_attempt() -> None:
    entries = (_done(1, "A", "yes", ["A", "B", "C"]) + _done(1, "B", None, ["A", "B", "C"], status="failed")
               + _done(1, "C", None, ["A", "B", "C"], status="interrupted"))
    assert _admit(entries, 1, ["C", "B", "A"]).to_run == ["C", "B"]


@pytest.mark.parametrize("status", ["failed", "paused", "pending", "interrupted"])
def test_unfinished_attempt_is_run_again(status: str) -> None:
    entries = _done(1, "A", None, ["A"], status=status)
    assert _admit(entries, 1, ["A"]).to_run == ["A"]


def test_round_four_runs_and_round_five_needs_an_extension() -> None:
    entries: list[dict] = []
    for round_no in (1, 2, 3):
        entries += _done(round_no, "A", "no", ["A"])
    assert _admit(entries, 4, ["A"]).to_run == ["A"]
    entries += _done(4, "A", "no", ["A"])
    with pytest.raises(launcher.ReviewRefusedError, match="past the limit"):
        _admit(entries, 5, ["A"])
    assert _admit(entries, 5, ["A"], extension=PR_COMMENT).to_run == ["A"]


def test_round_five_with_an_extension_runs_and_the_log_keeps_the_reference(fx: Fixture) -> None:
    entries: list[dict] = []
    for round_no in (1, 2, 3, 4):
        entries += _done(round_no, "A", "no", ["A"])
    _write(fx.work, LOG, "".join(json.dumps(e) + "\n" for e in entries))
    assert _run(fx, round_no=5) == 2
    assert _run(fx, "--extension", PR_COMMENT, round_no=5) == 0
    assert fx.log()[-2]["extension"] == PR_COMMENT and fx.log()[-2]["round"] == 5


def test_reference_that_is_not_a_pr_comment_is_refused() -> None:
    with pytest.raises(launcher.ReviewRefusedError, match="PR comment"):
        _admit([], 1, ["A"], extension="https://example.org/approve")
    with pytest.raises(launcher.ReviewRefusedError, match="PR comment"):
        _admit([], 1, ["A"], reset="https://github.com/owner/repo/pull/7")


def test_a_reference_admits_once() -> None:
    entries: list[dict] = []
    for round_no in (1, 2, 3, 4):
        entries += _done(round_no, "A", "no", ["A"])
    round_five = _done(5, "A", "no", ["A"])
    round_five[0]["extension"] = PR_COMMENT
    with pytest.raises(launcher.ReviewRefusedError, match="already admitted another round"):
        _admit(entries + round_five, 6, ["A"], extension=PR_COMMENT)
    assert _admit(entries + round_five[:1], 5, ["A"], extension=PR_COMMENT).to_run == ["A"]  # same round again
    reset_start = _done(1, "A", None, ["A"], status="failed")
    reset_start[0].update(count=2, reset=PR_COMMENT)
    with pytest.raises(launcher.ReviewRefusedError, match="already used"):
        _admit(entries + reset_start, 1, ["A"], reset=PR_COMMENT)
    assert _admit(entries + reset_start, 1, ["A"]).count == 2


def test_reset_starts_a_new_count_at_round_one() -> None:
    entries: list[dict] = []
    for round_no in (1, 2, 3, 4):
        entries += _done(round_no, "A", "no", ["A"])
    admission = _admit(entries, 1, ["A"], reset=PR_COMMENT)
    assert admission.count == 2 and admission.to_run == ["A"]
    with pytest.raises(launcher.ReviewRefusedError, match="round 1"):
        _admit(entries, 2, ["A"], reset=PR_COMMENT)


@pytest.mark.parametrize(("round_no", "labels", "match"), [
    (2, ["A", "B"], "not complete"),          # round 2 before every reviewer of round 1 completed
    (3, ["A", "B"], "next round is 2"),       # skipping a round
])
def test_round_started_too_early_is_refused(round_no: int, labels: list[str], match: str) -> None:
    entries = _done(1, "A", "yes", ["A", "B"]) + [_start("u/2", ["A", "B"], "B", "r")]
    with pytest.raises(launcher.ReviewRefusedError, match=match):
        _admit(entries, round_no, labels)


def test_dropped_no_reviewer_added_label_and_changed_list_are_refused() -> None:
    entries = _done(1, "A", "yes", ["A", "B"]) + _done(1, "B", "no", ["A", "B"])
    with pytest.raises(launcher.ReviewRefusedError, match="verdict was no"):
        _admit(entries, 2, ["A"])
    with pytest.raises(launcher.ReviewRefusedError, match="adds reviewers"):
        _admit(entries, 2, ["B", "C"])
    entries += [_start("u/3", ["B"], "B", "r", round_no=2)]
    with pytest.raises(launcher.ReviewRefusedError, match="was started with"):
        _admit(entries, 2, ["A", "B"])


def test_completed_reviewer_is_never_run_again(fx: Fixture) -> None:
    assert _run(fx) == 0
    assert _run(fx) == 2
    assert len(fx.calls()) == 1


# --- Output shape ------------------------------------------------------------------------------


def test_findings_of_every_kind_with_a_verdict_are_accepted(fx: Fixture) -> None:
    findings = [{"id": f"X{i}", "kind": kind, "file": REVIEWED, "line": i, "problem": "p", "evidence": "e",
                 "failure_scenario": "f"} for i, kind in enumerate(launcher.FINDING_KINDS)]
    fx.scenario({"result": {"structured_output": {"findings": findings, "verdict": "no"}}})
    assert _run(fx) == 0
    start = fx.log()[0]
    assert json.loads(_report(fx, start).read_text())["findings"] == findings
    assert _ends(fx)[0]["verdict"] == "no"


@pytest.mark.parametrize("scenario", [
    {"result": {"result": "not json at all"}},
    {"result": {"structured_output": {"findings": [{"id": "X", "kind": "blocking", "file": "f", "line": 1,
                                                    "problem": "p", "failure_scenario": "f"}], "verdict": "yes"}}},
    {"result": {"structured_output": {"findings": []}}},
    {"raw_stdout": ""},
], ids=["malformed-json", "missing-field", "missing-verdict", "empty-output"])
def test_malformed_or_empty_output_fails_and_is_not_retried(fx: Fixture, scenario: dict) -> None:
    fx.scenario(scenario)
    assert _run(fx) == 1
    assert [e["status"] for e in _ends(fx)] == ["failed"]
    assert len(fx.calls()) == 1
    assert not _report(fx, fx.log()[0]).exists()


# --- Empty or escaped review -------------------------------------------------------------------


@pytest.mark.parametrize("scenario", [
    {"reads": ["AGENTS.md"]},
    {"denials": [["Read", {"file_path": "{cwd}/scripts/review_me.py"}]]},
    {"reads": [REVIEWED, "/etc/hostname"]},
    {"reads": [REVIEWED, "../outside.txt"]},
    {"tool_uses": [["Grep", {"pattern": "x", "path": "{cwd}/.."}]]},
    {"tool_uses": [["Glob", {"pattern": "../../*"}]]},
], ids=["no-read-of-paths-under-review", "denied-inside", "absolute-outside", "relative-outside", "grep-outside",
        "glob-outside"])
def test_empty_or_escaped_review_fails_and_releases_no_report(fx: Fixture, scenario: dict) -> None:
    fx.scenario(scenario)
    assert _run(fx) == 1
    assert [e["status"] for e in _ends(fx)] == ["failed"]
    assert not _report(fx, fx.log()[0]).exists()


def test_failed_read_of_the_only_path_under_review_does_not_count(fx: Fixture) -> None:
    fx.scenario({"reads": [REVIEWED, "AGENTS.md"], "read_errors": [REVIEWED]})
    assert _run(fx) == 1
    end = _ends(fx)[0]
    assert end["status"] == "failed" and end["reason"] == "the review read none of the paths under review"
    assert end["paths_read"] == ["AGENTS.md"]


def test_call_to_a_tool_other_than_read_grep_and_glob_fails(fx: Fixture) -> None:
    fx.scenario({"tool_uses": [["Bash", {"command": "ls"}]]})
    assert _run(fx) == 1
    end = _ends(fx)[0]
    assert end["status"] == "failed" and end["other_tools"] == ["Bash"]
    assert not _report(fx, fx.log()[0]).exists()


def test_call_to_a_tool_the_cli_does_not_offer_does_not_fail_the_review(fx: Fixture) -> None:
    fx.scenario({"tool_uses": [["Bash", {"command": "ls"}]], "tool_errors": ["Bash"]})
    assert _run(fx) == 0
    end = _ends(fx)[0]
    assert end["status"] == "completed" and end["other_tools"] == [] and end["other_tools_not_offered"] == ["Bash"]


def test_offered_tool_that_ran_with_an_error_still_fails(fx: Fixture) -> None:
    """An error result does not show that a call never ran: a Bash command can run and exit non-zero."""
    fx.scenario({"offered": ["Bash", "Glob", "Grep", "Read"], "tool_uses": [["Bash", {"command": "false"}]],
                 "tool_errors": ["Bash"]})
    assert _run(fx) == 1
    end = _ends(fx)[0]
    assert end["status"] == "failed" and end["other_tools"] == ["Bash"] and end["other_tools_not_offered"] == []


def test_without_an_offered_tool_list_an_erroring_call_still_fails(fx: Fixture) -> None:
    fx.scenario({"offered": None, "tool_uses": [["Bash", {"command": "ls"}]], "tool_errors": ["Bash"]})
    assert _run(fx) == 1
    assert _ends(fx)[0]["other_tools"] == ["Bash"]


def test_reports_of_the_same_unit_in_two_slices_do_not_overwrite_each_other(fx: Fixture) -> None:
    other = "docs/slices/other/review_other.md"
    _write(fx.work, other, "# record\n")
    _commit_all(fx.work, "second slice")
    commit = _git(fx.work, "rev-parse", "HEAD")
    assert _run(fx, commit=commit) == 0
    assert launcher.main([*_args(fx, commit=commit)[:4], "--record", other, *_args(fx, commit=commit)[6:]], repo=fx.work) == 0
    first = fx.log()[0]["report_path"]
    second = [json.loads(line) for line in (fx.work / "docs/slices/other/review_attempts.jsonl").read_text().splitlines()][0]["report_path"]
    assert first != second and (fx.work / first).exists() and (fx.work / second).exists()
    assert "/demo/" in first and "/other/" in second


def test_outside_calls_are_logged_with_tool_and_denial_but_no_path(fx: Fixture) -> None:
    fx.scenario({"reads": [REVIEWED, "/etc/hostname"], "denials": [["Read", {"file_path": "/etc/hostname"}]],
                 "tool_uses": [["Grep", {"pattern": "x", "path": "{cwd}/.."}]]})
    assert _run(fx) == 1
    end = _ends(fx)[0]
    assert end["outside"] == [{"tool": "Read", "denied": True}, {"tool": "Grep", "denied": False}]
    assert "hostname" not in json.dumps(end) and end["outside_calls"] == 2


def test_review_reads_with_relative_and_absolute_paths_inside_the_copy_count(fx: Fixture) -> None:
    fx.scenario({"reads": ["{cwd}/scripts/review_me.py", "./scripts/../AGENTS.md"]})
    assert _run(fx) == 0
    assert _ends(fx)[0]["paths_read"] == ["AGENTS.md", REVIEWED]


# --- Publication check -------------------------------------------------------------------------


def _pem_private_key() -> str:
    """A throwaway key made at test time, so no key-shaped text is committed."""
    key = ec.generate_private_key(ec.SECP256R1())
    return key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                             serialization.NoEncryption()).decode("ascii")


def test_secret_in_the_reply_leaves_no_report_and_no_end_entry(fx: Fixture, capsys: pytest.CaptureFixture[str]) -> None:
    pem = _pem_private_key()
    finding = {"id": "X", "kind": "advisory", "file": REVIEWED, "line": 1, "problem": pem, "evidence": "e",
               "failure_scenario": "f"}
    fx.scenario({"result": {"structured_output": {"findings": [finding], "verdict": "yes"}}})
    assert _run(fx) == 3
    start = fx.log()[0]
    assert [e["event"] for e in fx.log()] == ["start"]
    assert not _report(fx, start).exists() and not Path(str(_report(fx, start)) + ".partial").exists()
    err = capsys.readouterr().err
    assert "PEM private key" in err and start["report_path"] in err
    assert pem.splitlines()[1] not in err


# --- Usage limits and retries ------------------------------------------------------------------


@pytest.mark.parametrize(("status", "five_hour"), [("allowed", 0.70), ("allowed", 0.71), ("allowed_warning", 0.95)])
def test_allowed_and_warning_statuses_proceed_and_utilization_is_logged(fx: Fixture, status: str,
                                                                        five_hour: float) -> None:
    fx.scenario({"rate_limit": {"status": status, "five_hour": five_hour, "seven_day": 0.2, "resetsAt": 9}})
    assert _run(fx) == 0
    end = _ends(fx)[0]
    assert end["status"] == "completed"
    assert end["utilization"] == {"status": status, "five_hour": five_hour, "seven_day": 0.2}
    assert not (fx.home / "codex_called").exists()


def test_rejected_status_pauses_until_the_reset_and_the_round_is_admitted_again(fx: Fixture) -> None:
    fx.scenario({"rate_limit": {"status": "rejected", "five_hour": 1.0, "seven_day": 0.3, "resetsAt": 1794099600}})
    assert _run(fx) == 1
    end = _ends(fx)[0]
    assert end["status"] == "paused" and end["paused_until"] == 1794099600 and end["verdict"] is None
    assert not _report(fx, fx.log()[0]).exists()
    assert not (fx.home / "codex_called").exists()
    fx.scenario({})
    assert _run(fx) == 0
    assert _ends(fx)[-1]["status"] == "completed"


ERROR = {"result": {"is_error": True}, "exit": 1}


def test_two_provider_errors_then_success_completes_with_three_attempts(fx: Fixture) -> None:
    fx.scenario(ERROR, {"result": None, "exit": 1}, {})
    assert _run(fx) == 0
    assert [e["status"] for e in _ends(fx)] == ["failed", "failed", "completed"]
    assert len([e for e in fx.log() if e["event"] == "start"]) == 3


def test_three_provider_errors_leave_the_attempt_pending(fx: Fixture) -> None:
    fx.scenario(ERROR)
    assert _run(fx) == 1
    assert [e["status"] for e in _ends(fx)] == ["failed", "failed", "pending"]
    assert all(e["verdict"] is None for e in _ends(fx))
