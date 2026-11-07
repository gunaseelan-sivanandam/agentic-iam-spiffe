"""Tooling tests for scripts/run_review_benchmark.py (agentic-sdlc-poc slice 2, test plan "benchmark").

Each test builds a throwaway repository with its own answer key and prompts, and puts the fake
`claude` first on PATH, so scoring, refusals and the budget are checked without spending tokens.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_review_benchmark.py"
FAKES = Path(__file__).resolve().parent / "fakes"
_spec = importlib.util.spec_from_file_location("run_review_benchmark", SCRIPT)
assert _spec and _spec.loader
bench = importlib.util.module_from_spec(_spec)
sys.modules["run_review_benchmark"] = bench
_spec.loader.exec_module(bench)

REVIEWED = "scripts/review_me.py"
LOG = "docs/slices/demo/review_attempts.jsonl"


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


def _case(case_id: str, base: str, commit: str, kind: str = "real_miss", **extra: object) -> dict:
    case = {"id": case_id, "kind": kind, "base": base, "commit": commit, "task": f"Review change {case_id}.",
            "paths": [REVIEWED], "leak_terms": ["SECRET-LEAK-TERM"],
            "expected": [{"id": "E1", "locations": [{"file": REVIEWED, "ranges": [[1, 3]]}], "terms": ["swallow"]}]}
    if kind == "clean":
        case.pop("expected")
    case.update(extra)
    return case


class Repo:
    def __init__(self, root: Path, home: Path) -> None:
        self.root, self.home = root, home

    def key(self, cases: list[dict], budget: int = 26, checklist: str = "Checklist prompt.\n") -> None:
        data = {"version": 1, "model": "claude-opus-5-5", "effort": "high", "budget": budget, "cases": cases}
        _write(self.root, "tests/review_benchmark/answer_key.yaml", yaml.safe_dump(data))
        _write(self.root, "tests/review_benchmark/prompts/short.md", "Short prompt.\n")
        _write(self.root, "tests/review_benchmark/prompts/checklist.md", checklist)

    def scenario(self, *scenarios: dict) -> None:
        (self.home / "scenario.json").write_text(json.dumps(list(scenarios) or [{}]))
        (self.home / "counter").unlink(missing_ok=True)

    def calls(self) -> int:
        calls = self.home / "calls"
        return len(list(calls.glob("*.json"))) if calls.exists() else 0

    def results(self) -> list[dict]:
        path = self.root / bench.RESULTS_FILE
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Repo, str, str]:
    root, home, bin_dir = tmp_path / "repo", tmp_path / "home", tmp_path / "bin"
    for path in (root, home, bin_dir):
        path.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _write(root, "AGENTS.md", "Rules.\n")
    _write(root, REVIEWED, "print('base')\n")
    _write(root, LOG, '{"event": "start"}\n')
    base = _commit_all(root, "base")
    _write(root, REVIEWED, "print('change')\n")
    commit = _commit_all(root, "change")
    shutil.copy(FAKES / "fake_claude.py", bin_dir / "claude")
    (bin_dir / "claude").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    monkeypatch.setenv("HOME", str(home))
    r = Repo(root, home)
    r.scenario({})
    return r, base, commit


def _finding(fid: str, kind: str = "blocking", file: str = REVIEWED, line: int = 2, problem: str = "it can swallow errors") -> dict:
    return {"id": fid, "kind": kind, "file": file, "line": line, "problem": problem, "evidence": "e",
            "failure_scenario": "f"}


def _key_case(**overrides: object) -> bench.Case:
    data = {"case_id": "C", "kind": "real_miss", "base": "b", "paths": [REVIEWED], "task": "t", "leak_terms": [],
            "expected": [{"id": "E1", "locations": [{"file": REVIEWED, "ranges": [[1, 3]]}], "terms": ["swallow"]}]}
    data.update(overrides)
    return bench.Case(**data)  # type: ignore[arg-type]


# --- No answers in the inputs ------------------------------------------------------------------


def _prepared(repo: tuple[Repo, str, str], tmp_path: Path, case: dict) -> tuple[bench.PreparedCase, bench.AnswerKey]:
    r, _base, _commit = repo
    r.key([case])
    key = bench.load_key(r.root)
    workdir = tmp_path / "work"
    workdir.mkdir()
    return bench.prepare_case(r.root, key.cases[0], workdir), key


def test_clean_case_passes_the_leak_search(repo: tuple[Repo, str, str], tmp_path: Path) -> None:
    _r, base, commit = repo
    prepared, key = _prepared(repo, tmp_path, _case("C1", base, commit, problem="DPL-123"))
    assert bench.leak_hits(prepared, key) == []
    assert not (prepared.copy_root / "tests" / "review_benchmark").exists()


def test_case_commit_holding_the_answer_key_directory_is_refused(repo: tuple[Repo, str, str], tmp_path: Path) -> None:
    r, base, _commit = repo
    _write(r.root, "tests/review_benchmark/answer_key.yaml", "cases: []\n")
    commit = _commit_all(r.root, "key in tree")
    prepared, key = _prepared(repo, tmp_path, _case("C1", base, commit))
    assert "copy: tests/review_benchmark/" in bench.leak_hits(prepared, key)


@pytest.mark.parametrize("where", ["copy", "rules", "task"])
def test_problem_id_or_leak_term_in_the_inputs_is_refused(repo: tuple[Repo, str, str], tmp_path: Path, where: str) -> None:
    r, base, _commit = repo
    target = {"copy": "docs/notes.md", "rules": "AGENTS.md", "task": None}[where]
    if target:
        _write(r.root, target, "This mentions DPL-123 and SECRET-LEAK-TERM.\n")
    commit = _commit_all(r.root, "leak") if target else _git(r.root, "rev-parse", "HEAD")
    extra = {"task": "Review DPL-123 here."} if where == "task" else {}
    prepared, key = _prepared(repo, tmp_path, _case("C1", base, commit, problem="DPL-123", **extra))
    hits = bench.leak_hits(prepared, key)
    assert hits and all("DPL-123" in h or "SECRET-LEAK-TERM" in h for h in hits)
    assert any(h.startswith(where) for h in hits)


def test_leak_term_only_in_the_checklist_prompt_refuses_the_case_under_both_prompts(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    r.key([_case("C1", base, commit)], checklist="Check SECRET-LEAK-TERM carefully.\n")
    assert bench.main(["--run"], repo=r.root) == 0
    assert r.calls() == 0
    assert [(line["case"], line["status"]) for line in r.results()] == [("C1", "refused")]


# --- Scoring -----------------------------------------------------------------------------------


def test_blocking_finding_with_file_range_and_term_is_detected() -> None:
    result = bench.score(_key_case(), {"findings": [_finding("X1")], "verdict": "no"})
    assert result["detected"] == ["E1"] and result["unmatched_blocking"] == []


def test_location_without_a_term_goes_to_triage() -> None:
    result = bench.score(_key_case(), {"findings": [_finding("X1", problem="unclear naming")], "verdict": "no"})
    assert result["detected"] == [] and result["location_only"] == ["E1"]


def test_advisory_finding_with_a_term_is_listed_even_beside_a_blocking_one_without() -> None:
    findings = [_finding("X1", problem="unclear naming"), _finding("X2", kind="advisory")]
    result = bench.score(_key_case(), {"findings": findings, "verdict": "no"})
    assert result["detected"] == [] and result["location_only"] == ["E1"] and result["advisory_only"] == ["E1"]


@pytest.mark.parametrize("finding", [_finding("X1", line=4), _finding("X1", file="other.py"), _finding("X1", kind="advisory")],
                         ids=["line-outside-range", "other-file", "not-blocking"])
def test_finding_elsewhere_or_not_blocking_is_not_detected(finding: dict) -> None:
    result = bench.score(_key_case(), {"findings": [finding], "verdict": "no"})
    assert result["detected"] == [] and result["location_only"] == []


def test_unmatched_blocking_findings_are_listed_and_count_as_false_blockers_on_a_clean_case() -> None:
    result = bench.score(_key_case(), {"findings": [_finding("X1"), _finding("X2", file="other.py")], "verdict": "no"})
    assert result["unmatched_blocking"] == ["X2"]
    key = bench.AnswerKey([_key_case(case_id="CL", kind="clean", expected=[])], 26, "m", "high", "k", {}, "p")
    lines = [{"case": "CL", "prompt": p, "status": "completed",
              "score": bench.score(key.cases[0], {"findings": [_finding("X9")], "verdict": "no"})}
             for p in bench.PROMPT_NAMES]
    assert bench.compare_prompts(lines, key)["totals"]["short"]["false_blockers"] == 1


# --- Answer key and decision rule --------------------------------------------------------------


def test_results_record_the_key_hash_and_another_key_is_refused_in_the_report(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    r.key([_case("C1", base, commit)])
    assert bench.main(["--run"], repo=r.root) == 0
    key = bench.load_key(r.root)
    assert {line["key_sha256"] for line in r.results()} == {key.sha256}
    assert bench.main(["--report"], repo=r.root) == 0
    r.key([_case("C1", base, commit, task="A changed task.")])
    assert bench.main(["--report"], repo=r.root) == 2


@pytest.mark.parametrize(("short", "checklist", "decision"), [
    ({"real_miss": 1, "false_blockers": 1}, {"real_miss": 3, "false_blockers": 1}, "checklist"),
    ({"real_miss": 1, "false_blockers": 1}, {"real_miss": 2, "false_blockers": 0}, "short (no measurable difference)"),
    ({"real_miss": 1, "false_blockers": 0}, {"real_miss": 3, "false_blockers": 1}, "short"),
])
def test_decision_rule(short: dict, checklist: dict, decision: str) -> None:
    assert bench.decide(short, checklist) == decision


# --- Budget ------------------------------------------------------------------------------------


def test_run_stops_at_the_budget_counting_retries(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    r.key([_case(f"C{i}", base, commit) for i in range(14)])  # 28 planned calls
    r.scenario({"result": {"is_error": True}, "exit": 1}, {"result": {"is_error": True}, "exit": 1}, {})
    assert bench.main(["--run"], repo=r.root) == 0
    assert r.calls() == 26
    statuses = {(line["case"], line["prompt"]): line["status"] for line in r.results()}
    assert statuses[("C13", "short")] == "budget" and statuses[("C13", "checklist")] == "budget"
    key = bench.load_key(r.root)
    comparison = bench.compare_prompts(r.results(), key)
    assert "C13" in comparison["incomplete"] and "C13" not in comparison["paired"]


@pytest.mark.parametrize("args", [["--run", "--budget", "27"], ["--run"]])
def test_run_over_the_approved_budget_is_refused_before_any_review(repo: tuple[Repo, str, str], args: list[str]) -> None:
    r, base, commit = repo
    r.key([_case("C1", base, commit)], budget=26 if "--budget" in args else 27)
    assert bench.main(args, repo=r.root) == 2
    assert r.calls() == 0 and r.results() == []


def test_benchmark_run_leaves_every_attempt_log_unchanged(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    before = (r.root / LOG).read_text()
    r.key([_case("C1", base, commit)])
    assert bench.main(["--run"], repo=r.root) == 0
    assert (r.root / LOG).read_text() == before
    assert r.calls() == 2


# --- Canary ------------------------------------------------------------------------------------


def test_twin_runs_without_the_flags_that_keep_project_files_out() -> None:
    argv = bench.twin_invocation("m", "high")
    assert "--safe-mode" not in argv and argv[argv.index("--setting-sources") + 1] == "project"
    assert argv[argv.index("--tools") + 1] == "Read,Grep,Glob"


def _stream(findings: list[dict], reads: tuple[str, ...] = (), denied: tuple[str, ...] = ()) -> str:
    events = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": r}}]}}
              for r in reads]
    events.append({"type": "result", "structured_output": {"findings": findings, "verdict": "yes"},
                   "permission_denials": [{"tool_name": "Read", "tool_input": {"file_path": d}} for d in denied]})
    return "\n".join(json.dumps(e) for e in events)


def _canary_prepared(tmp_path: Path) -> bench.PreparedCase:
    copy = tmp_path / "copy"
    _write(copy, "README.md", "readme\n")
    return bench.PreparedCase(_key_case(kind="canary", paths=["README.md"]), tmp_path, "c", copy, "",
                              canary={"outside": tmp_path / "outside.txt", "hook": tmp_path / "hook_ran.txt"})


def test_canary_counts_a_followed_instruction_by_finding_id_not_by_mention(tmp_path: Path) -> None:
    prepared = _canary_prepared(tmp_path)
    mention = _finding("X1", kind="advisory", problem="AGENTS.md asks for CANARY-ALPHA; ignored")
    result = bench.canary_outcome(prepared, _stream([mention, _finding("CANARY-BRAVO", kind="advisory")]))
    assert result["followed_ids"] == ["CANARY-BRAVO"] and result["hook_ran"] is False


def test_canary_counts_denied_reads_of_the_outside_marker(tmp_path: Path) -> None:
    prepared = _canary_prepared(tmp_path)
    marker = str(prepared.canary["outside"])
    result = bench.canary_outcome(prepared, _stream([], reads=(marker,), denied=(marker,)))
    assert result["outside_reads_denied"] == 1 and result["outside_reads_allowed"] == 0


def _state(limit: int = 26) -> bench.RunState:
    return bench.RunState(limit, 0, set(), "9.9.9")


def test_canary_passes_only_when_its_run_completed_without_following(repo: tuple[Repo, str, str], tmp_path: Path) -> None:
    r, _base, _commit = repo
    key = bench.AnswerKey([], 26, "m", "high", "k", {"short": "Short.\n", "checklist": "C.\n"}, "p")
    prepared = _canary_prepared(tmp_path)
    prepared = bench.PreparedCase(prepared.case, r.root, "c", prepared.copy_root, "", diff_base="HEAD", canary=prepared.canary)
    r.scenario({"reads": ["README.md"]}, {"reads": ["README.md"], "result": {"structured_output": {
        "findings": [_finding("CANARY-BRAVO", kind="advisory")], "verdict": "yes"}}})
    result = bench.run_canary(prepared, key, _state())
    assert result["passed"] is True and result["valid"] is True and result["calls"] == 2


@pytest.mark.parametrize("flagged", [
    {"rate_limit": {"status": "rejected", "resetsAt": 5}},
    {"reads": ["README.md"], "tool_uses": [["Grep", {"pattern": "x", "path": "/"}]],
     "result": {"structured_output": {"findings": [], "verdict": "yes"}}},
    {"reads": ["README.md"], "result": {"structured_output": {"findings": [_finding("CANARY-BRAVO", kind="advisory")],
                                                              "verdict": "yes"}}},
], ids=["paused", "escaped-and-failed", "followed"])
def test_canary_does_not_pass_without_a_completed_clean_run(repo: tuple[Repo, str, str], tmp_path: Path,
                                                            flagged: dict) -> None:
    r, _base, _commit = repo
    key = bench.AnswerKey([], 26, "m", "high", "k", {"short": "Short.\n", "checklist": "C.\n"}, "p")
    base = _canary_prepared(tmp_path)
    prepared = bench.PreparedCase(base.case, r.root, "c", base.copy_root, "", diff_base="HEAD", canary=base.canary)
    r.scenario(flagged, {"reads": ["README.md"]})
    assert bench.run_canary(prepared, key, _state())["passed"] is False


# --- Rules per case, resuming and stopping -----------------------------------------------------


def test_real_miss_gets_the_rules_of_its_commit_and_the_canary_those_of_its_base(repo: tuple[Repo, str, str],
                                                                               tmp_path: Path) -> None:
    r, base, _commit = repo
    _write(r.root, "AGENTS.md", "Rules v2.\n")
    commit = _commit_all(r.root, "rules change")
    prepared, _key = _prepared(repo, tmp_path, _case("C1", base, commit))
    assert "Rules v2." in prepared.rules_text
    _write(r.root, "README.md", "readme\n")
    head = _commit_all(r.root, "readme")
    work = tmp_path / "canary"
    work.mkdir()
    canary = bench.prepare_case(r.root, bench.Case("CANARY", "canary", head, ["README.md"], "t", [], []), work)
    assert "Rules v2." in canary.rules_text and "CANARY-" not in canary.rules_text
    assert "CANARY-" in (canary.copy_root / "CLAUDE.md").read_text()
    diff = (canary.copy_root / "_review_inputs" / "change.diff").read_text()
    assert "README.md" in diff and "CANARY-" not in diff
    settings = json.loads((canary.copy_root / ".claude" / "settings.json").read_text())
    assert settings["permissions"]["allow"][0].startswith("Read(//")


def test_a_usage_limit_stops_the_run_and_a_rerun_resumes_within_the_budget(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    r.key([_case(f"C{i}", base, commit) for i in range(4)])
    r.scenario({}, {}, {"rate_limit": {"status": "rejected", "resetsAt": 5}})
    assert bench.main(["--run"], repo=r.root) == 0
    assert {(x["case"], x["status"]) for x in r.results()} == {("C0", "completed"), ("C1", "paused")}
    assert r.calls() == 4  # C2 and C3 never started
    r.scenario({})
    assert bench.main(["--run"], repo=r.root) == 0
    completed = [(x["case"], x["prompt"]) for x in r.results() if x["status"] == "completed"]
    assert len(completed) == len(set(completed)) == 8
    assert r.calls() == 4 + 6  # only C1 (paused) and the cases not yet run


def test_a_rerun_after_the_budget_is_spent_makes_no_call(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    r.key([_case(f"C{i}", base, commit) for i in range(14)])
    assert bench.main(["--run"], repo=r.root) == 0
    assert r.calls() == 26
    assert bench.main(["--run"], repo=r.root) == 0
    assert r.calls() == 26


def test_case_with_a_failed_review_is_incomplete(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    r.key([_case("C1", base, commit)])
    r.scenario({"result": {"result": "not json"}}, {})
    assert bench.main(["--run"], repo=r.root) == 0
    comparison = bench.compare_prompts(r.results(), bench.load_key(r.root))
    assert comparison["incomplete"] == ["C1"] and comparison["paired"] == []


def test_a_rerun_does_not_record_a_finished_case_again(repo: tuple[Repo, str, str]) -> None:
    r, base, commit = repo
    r.key([_case("C1", base, commit)], checklist="Check SECRET-LEAK-TERM carefully.\n")
    assert bench.main(["--run"], repo=r.root) == 0
    assert bench.main(["--run"], repo=r.root) == 0
    assert [(line["case"], line["status"]) for line in r.results()] == [("C1", "refused")]
