"""Tooling tests for slice 4.2's review inputs (test plan of poc-4-2-review-inputs): the files under review come from
the diff, the upstream items and the evidence are computed by tools, and every evidence entry must be accounted for.

The launcher tests (`test_run_independent_review.py`) stub the evidence computation; these tests run it for real on a
throwaway repository with its own trace model, tooling tests and a fake CI API, and the fake `claude` on PATH.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.tools import test_run_independent_review as base

launcher = base.launcher
evidence_module = launcher._INPUTS
REAL_COMPUTE = launcher.compute_evidence
REAL_UPSTREAM = launcher._sanitised_upstream
ROOT = Path(__file__).resolve().parents[2]
RECORD = base.RECORD

TOOL = '''"""A tool with two branches; the test runs only one of them."""


def classify(value: int) -> str:
    if value > 0:
        return "positive"
    return "other"
'''
TOOL_CHANGED = TOOL.replace('''    return "other"
''', '''    if value < 0:
        return "negative"
    return "zero"
''')
TOOL_TEST = '''"""Runs one branch of the tool."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("tool", Path(__file__).resolve().parents[2] / "scripts" / "tool.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def test_tool() -> None:
    assert tool.classify(1) == "positive"
'''
REQUIREMENTS = "# Requirements\n\n## REQ-T-R1 — A proved thing\n\nText.\n\n## REQ-T-R2 — An unproved thing\n\nText.\n"
ARCHITECTURE = ("# Architecture\n\n## ARCH-001 The tool\n\nType: Component\nSatisfies: REQ-T-R1, REQ-T-R2\n"
                "Implemented by: scripts/tool.py\n")
TESTS = """tests:
  - id: TOOL-K1
    type: static_test
    title: The tool check
    source_requirements: [REQ-T-R1]
    gate: make tooling-test
    negative_controls: [tests/tools/test_tool.py::test_tool]
    result: artifacts/quality/tool.json
accepted_gaps: []
"""
PLAN = "# Plan\n\n| ID | Decision | Source |\n| --- | --- | --- |\n| S99-D1 | One | owner |\n| S99-D2 | Two | owner |\n"


@pytest.fixture
def ev(base_fx: base.Fixture) -> base.Fixture:
    """The launcher's fixture, with a trace model, a tool, its test and a plan at the base, and the real evidence."""
    work = base_fx.work
    files = {"scripts/validate_traceability.py": (ROOT / "scripts" / "validate_traceability.py").read_text(),
             "scripts/qa_deploy.py": (ROOT / "scripts" / "qa_deploy.py").read_text(),  # the trace tool imports it
             "scripts/tool.py": TOOL, "tests/tools/test_tool.py": TOOL_TEST, "tests/__init__.py": "",
             "tests/tools/__init__.py": "", "docs/requirements.md": REQUIREMENTS, "docs/architecture.md": ARCHITECTURE,
             "trace/tests.yaml": TESTS, "Makefile": "tooling-test:\n\tpytest tests/tools\n",
             "docs/slices/demo/plan.md": PLAN, "docs/slices/other/plan.md": PLAN.replace("S99", "S98"),
             "docs/slices/other/notes.md": "# Notes\n\nOld notes.\n", "scripts/gone.py": "print('gone')\n",
             "services/README.md": "# Services\n", "tests/unit/README.md": "# Unit tests\n"}
    for rel, text in files.items():
        base._write(work, rel, text)
    base._commit_all(work, "trace model and tool")
    base._git(work, "push", "-q", "-f", "origin", "HEAD:poc/base")
    return base_fx


@pytest.fixture
def base_fx(fx: base.Fixture, monkeypatch: pytest.MonkeyPatch) -> base.Fixture:
    monkeypatch.setattr(launcher, "compute_evidence", REAL_COMPUTE)
    monkeypatch.setattr(launcher, "_sanitised_upstream", REAL_UPSTREAM)
    monkeypatch.setattr(evidence_module, "github_repo", lambda _repo: ("owner", "repo"))
    monkeypatch.setattr(evidence_module, "fetch_json", lambda _url: {"workflow_runs": []})
    return fx


fx = base.fx  # the launcher's fixture, under its own name for base_fx


def _change(ev: base.Fixture, **files: str | None) -> str:
    """Commit the given files (None deletes one) and an edit of the hint file, so `--path` stays in the diff."""
    base._write(ev.work, base.REVIEWED, (ev.work / base.REVIEWED).read_text() + "print('edited')\n")
    for rel, text in files.items():
        if text is None:
            (ev.work / rel).unlink()
        else:
            base._write(ev.work, rel, text)
    ev.commit = base._commit_all(ev.work, "the change")
    return ev.commit


def _accounting_reply(items: list[str], **scenario: object) -> dict:
    return base._reply(accounted=[base._accounted(i, "explained", note="fine") for i in items], **scenario)


def _evidence_section(prompt: str) -> str:
    return base._section(prompt, "Evidence")


def _items(prompt: str) -> list[str]:
    return [line.split(":", 1)[0] for line in _evidence_section(prompt).splitlines() if line.startswith("EV")]


def _run_accounting_everything(ev: base.Fixture, *extra: str, **kwargs: object) -> int:
    """Run once to learn the evidence entries, then answer with every entry accounted (the fake CLI replies blindly)."""
    ev.scenario(base._reply())
    first = base._run(ev, *extra, **kwargs)
    prompt = base._prompt(ev)
    items = _items(prompt)
    if first == 0 or not items:
        return first
    ev.scenario(_accounting_reply(items))
    return base._run(ev, *extra, **kwargs)


# --- Files under review (S42-D1, S42-D2) ---------------------------------------------------------------------------


def test_files_come_from_the_diff_and_deleted_files_are_listed_apart(fx: base.Fixture) -> None:
    base._write(fx.work, "scripts/new.py", "print('new')\n")
    base._write(fx.work, "docs/x.md", "# X\n\nText.\n")
    base._commit_all(fx.work, "two more files")
    base._git(fx.work, "push", "-q", "-f", "origin", "HEAD:poc/base")
    (fx.work / "docs/x.md").unlink()
    base._git(fx.work, "mv", "scripts/new.py", "scripts/renamed.py")
    base._write(fx.work, base.REVIEWED, "print('changed')\n")
    fx.commit = base._commit_all(fx.work, "delete, rename, modify")
    args = [a for a in base._args(fx) if a not in ("--path", base.REVIEWED)]
    assert launcher.main(args, repo=fx.work) == 0
    paths = base._section(base._prompt(fx), "Paths under review")
    assert f"- {base.REVIEWED}" in paths and "- scripts/renamed.py" in paths
    deleted = paths.split("Deleted by the change", 1)[1]
    assert "- docs/x.md" in deleted and "- scripts/new.py" in deleted and "scripts/renamed.py" not in deleted
    assert RECORD not in paths and base.LOG not in paths
    assert set(fx.log()[0]["paths_sha256"]) == {base.REVIEWED, "scripts/renamed.py"}


def test_path_hints_come_first_and_never_narrow_the_list(fx: base.Fixture) -> None:
    base._write(fx.work, "scripts/a_first.py", "print('a')\n")
    fx.commit = base._commit_all(fx.work, "another changed file")
    assert base._run(fx) == 0  # --path scripts/review_me.py
    listed = [line[2:] for line in base._section(base._prompt(fx), "Paths under review").splitlines()
              if line.startswith("- ")]
    assert listed[0] == base.REVIEWED and "scripts/a_first.py" in listed and "AGENTS.md" in listed
    assert fx.log()[0]["path_hints"] == [base.REVIEWED]


@pytest.mark.parametrize("hint", ["README.md", base.RECORD], ids=["not-in-the-diff", "withheld"])
def test_a_path_hint_outside_the_files_to_open_is_refused_before_any_call(fx: base.Fixture, hint: str) -> None:
    args = base._args(fx)
    args[args.index("--path") + 1] = hint
    assert launcher.main(args, repo=fx.work) == 2
    assert fx.calls() == []


def test_paths_section_says_to_open_every_file_and_the_end_entry_lists_those_not_read(fx: base.Fixture) -> None:
    assert base._run(fx) == 0
    paths = base._section(base._prompt(fx), "Paths under review")
    assert "Open every one of them." in paths
    assert base._ends(fx)[0]["paths_not_read"] == ["AGENTS.md", "tests/unit/AGENTS.md"]


def test_recheck_paths_section_says_to_open_the_answered_files_first(fx: base.Fixture) -> None:
    commit = base._recheck(fx, "| X1 | high | rejected: the scenario does not happen |")
    fx.scenario(base._reply(accounted=[base._accounted("X1")]))
    assert base._run(fx, round_no=2, commit=commit) == 0
    assert "open the files each answer names first" in base._section(base._prompt(fx), "Paths under review")


def test_review_that_opened_none_of_the_hint_files_fails_even_when_it_opened_other_listed_files(fx: base.Fixture) -> None:
    fx.scenario({"reads": ["AGENTS.md"]})
    assert base._run(fx) == 1
    assert base._ends(fx)[0]["reason"] == "the review read none of the paths under review"
    args = [a for a in base._args(fx, unit="unit2") if a not in ("--path", base.REVIEWED)]
    assert launcher.main(args, repo=fx.work) == 0  # without --path, any listed file counts


# --- Upstream items (S42-D3, S42-D4) -------------------------------------------------------------------------------


def test_upstream_names_the_governing_plan_links_edited_sections_and_other_bundles(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "docs/requirements.md": REQUIREMENTS.replace("Text.", "New.", 1),
                   "trace/tests.yaml": TESTS.replace("The tool check", "The tool check, renamed"),
                   "docs/slices/other/notes.md": "# Notes\n\nNew notes.\n"})
    _run_accounting_everything(ev)
    upstream = base._section(base._prompt(ev), "Upstream items")
    assert "docs/slices/demo/plan.md (the governing plan: the bundle of the review record); decisions: S99-D1, S99-D2" in upstream
    assert "docs/slices/other/plan.md (the change touches docs/slices/other/notes.md); decisions: S98-D1, S98-D2" in upstream
    assert "ARCH-001 (found: its `Implemented by:` line names scripts/tool.py); satisfies REQ-T-R1, REQ-T-R2" in upstream
    assert "REQ-T-R1 (found: the change edits its section in docs/requirements.md)" in upstream
    assert "TOOL-K1; proves REQ-T-R1" in upstream
    assert evidence_module.UPSTREAM_QUESTION in upstream


def test_upstream_names_a_dd_tag_with_its_architecture_and_requirements(ev: base.Fixture) -> None:
    tagged = TOOL_CHANGED.replace("def classify", "# DD: DD-001\n# Implements: ARCH-001\n# Title: Classify\ndef classify")
    base._write(ev.work, "services/svc/tool.py", TOOL)
    base._commit_all(ev.work, "a service at the base")
    base._git(ev.work, "push", "-q", "-f", "origin", "HEAD:poc/base")
    _change(ev, **{"services/svc/tool.py": tagged})
    _run_accounting_everything(ev)
    upstream = base._section(base._prompt(ev), "Upstream items")
    assert "DD-001 (found: its DD tag at services/svc/tool.py:" in upstream and "implements ARCH-001" in upstream
    assert "satisfies REQ-T-R1, REQ-T-R2" in upstream


def test_every_prompt_holds_the_upstream_question(fx: base.Fixture) -> None:
    assert base._run(fx) == 0
    assert evidence_module.UPSTREAM_QUESTION in base._prompt(fx)
    assert evidence_module.UPSTREAM_QUESTION == ("Does any problem you find originate upstream (a requirement, the "
                                                 "architecture, the plan)? If so, name the document and section.")


# --- Evidence (S42-D5 to S42-D9) -----------------------------------------------------------------------------------


def test_uncovered_changed_branch_is_listed_with_the_subprocess_note_and_a_service_gate_line(ev: base.Fixture) -> None:
    base._write(ev.work, "services/tool-b/server.py", "print('b')\n")
    base._write(ev.work, "services/other/app.py", "print('o')\n")
    base._commit_all(ev.work, "services at the base")
    base._git(ev.work, "push", "-q", "-f", "origin", "HEAD:poc/base")
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "services/tool-b/server.py": "print('b2')\n",
                   "services/other/app.py": "print('o2')\n"})
    _run_accounting_everything(ev)
    evidence = _evidence_section(base._prompt(ev))
    tool_line = next(line for line in evidence.splitlines() if "scripts/tool.py:" in line)
    assert "changed lines not run: 7-9" in tool_line and "branches not taken: 7->8, 7->9" in tool_line
    assert evidence_module.SUBPROCESS_NOTE in evidence
    assert "services/tool-b/server.py: covered by the gate make unit-trust and make unit-diff-cov" in evidence
    assert "services/other/app.py: no coverage gate" in evidence
    assert ev.log()[-2]["evidence_status"] == {"coverage": "ok", "trace": "ok", "ci": "ok"}


def test_trace_gap_among_the_upstream_items_is_marked_new_or_existing(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED})
    _run_accounting_everything(ev)
    evidence = _evidence_section(base._prompt(ev))
    assert "trace gap requirements_without_proof:REQ-T-R2 (existing, against the merge-base" in evidence
    base._write(ev.work, "docs/requirements.md", REQUIREMENTS + "\n## REQ-T-R3 — A new unproved thing\n\nText.\n")
    base._write(ev.work, "docs/architecture.md", ARCHITECTURE.replace("REQ-T-R2", "REQ-T-R2, REQ-T-R3"))
    ev.commit = base._commit_all(ev.work, "a new requirement")
    _run_accounting_everything(ev, unit="unit2")
    assert "trace gap requirements_without_proof:REQ-T-R3 (new, against the merge-base" in _evidence_section(base._prompt(ev))


@pytest.mark.parametrize(("runs", "expected", "absent"), [
    ([{"id": 1, "name": "CI", "event": "pull_request", "status": "in_progress", "conclusion": None}],
     ["CI run CI 1 (pull_request): in_progress", "lint: in_progress"], ["success"]),
    ([], ["no CI run for this commit"], ["CI run CI"]),
], ids=["running", "none"])
def test_ci_results_show_the_reviewed_commits_jobs_and_never_a_pass_for_a_running_job(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path, runs: list[dict], expected: list[str], absent: list[str]) -> None:
    commit = "c" * 40
    other = {"id": 2, "name": "CI", "event": "push", "status": "completed", "conclusion": "success", "head_sha": "d" * 40}
    calls: list[str] = []

    def fake(url: str) -> dict:
        calls.append(url)
        if url.endswith("/jobs?per_page=100"):
            return {"jobs": [{"name": "lint", "status": "in_progress", "conclusion": None}]}
        return {"workflow_runs": [{**r, "head_sha": commit} for r in runs] + [other]}

    monkeypatch.setattr(evidence_module, "github_repo", lambda _repo: ("owner", "repo"))
    evidence = evidence_module.Evidence()
    evidence_module.ci_evidence(evidence, tmp_path, commit, fake)
    text = evidence.text()
    assert all(e in text for e in expected) and not any(a in text for a in absent)
    assert "CI run CI 2" not in text and calls[0].endswith(f"head_sha={commit}&per_page=50")
    assert evidence.status["ci"] == "ok"


def test_unreadable_ci_api_is_shown_as_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(_url: str) -> dict:
        raise OSError("network down")

    monkeypatch.setattr(evidence_module, "github_repo", lambda _repo: ("owner", "repo"))  # any clone's origin
    evidence = evidence_module.Evidence()
    evidence_module.ci_evidence(evidence, ROOT, "c" * 40, broken)
    assert evidence.entries == [f"EV1: failed: {evidence_module.CI_COMMAND}: OSError"]
    assert evidence.status["ci"] == "failed"


def test_uncommitted_edit_does_not_change_the_evidence(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED})
    _run_accounting_everything(ev)
    first = _evidence_section(base._prompt(ev))
    base._write(ev.work, "scripts/tool.py", TOOL_CHANGED.replace('return "zero"', 'return "nothing"\n    return 1'))
    _run_accounting_everything(ev, unit="unit2")
    assert _evidence_section(base._prompt(ev)) == first


def test_report_must_account_for_every_evidence_entry(fx: base.Fixture) -> None:
    fx.evidence = ["scripts/x.py: changed lines not run: 3", "no CI run for this commit"]
    fx.scenario(base._reply(accounted=[base._accounted("EV1", "explained")]))
    assert base._run(fx) == 1
    assert "EV2 is not accounted" in base._ends(fx)[0]["reason"]
    fx.scenario(base._reply([base._finding("X1")], accounted=[base._accounted("EV1", "flagged", note="raised X1"),
                                                             base._accounted("EV2", "explained")], verdict="no"))
    assert base._run(fx) == 0
    assert base._ends(fx)[-1]["accounted_counts"]["flagged"] == 1


def test_flagged_evidence_entry_naming_no_finding_of_the_report_fails(fx: base.Fixture) -> None:
    fx.evidence = ["no CI run for this commit"]
    fx.scenario(base._reply(accounted=[base._accounted("EV1", "flagged", note="raised X1")]))
    assert base._run(fx) == 1
    assert base._ends(fx)[0]["reason"] == "the reply does not match the report schema"


def test_failing_tests_are_named_and_a_failed_coverage_run_never_shows_no_entries(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED,
                   "tests/tools/test_tool.py": TOOL_TEST + "\n\ndef test_broken() -> None:\n    assert False\n"})
    _run_accounting_everything(ev)
    evidence = _evidence_section(base._prompt(ev))
    assert "tests failing at this commit" in evidence and "tests/tools/test_tool.py::test_broken" in evidence
    assert "scripts/tool.py: changed lines not run" in evidence
    assert ev.log()[-2]["evidence_status"]["coverage"] == "failed"


def test_coverage_that_cannot_run_is_shown_as_failed(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "tests/tools/test_tool.py": None})
    shutil.rmtree(ev.work / "tests" / "tools")
    ev.commit = base._commit_all(ev.work, "no tooling tests")
    _run_accounting_everything(ev)
    evidence = _evidence_section(base._prompt(ev))
    assert f"failed: {evidence_module.COVERAGE_COMMAND}: exit " in evidence
    assert "No entries" not in evidence and ev.log()[-2]["evidence_status"]["coverage"] == "failed"


def test_trace_model_that_cannot_run_is_shown_as_failed(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "docs/requirements.md": "# no requirements\n"})
    _run_accounting_everything(ev)
    prompt = base._prompt(ev)
    assert f"failed: {evidence_module.TRACE_COMMAND}: exit 2" in _evidence_section(prompt)
    assert "Trace links: not available" in base._section(prompt, "Upstream items")
    assert ev.log()[-2]["evidence_status"]["trace"] == "failed"


def test_evidence_commands_see_only_path_lang_and_a_scratch_home(ev: base.Fixture) -> None:
    probe = TOOL_TEST + ('\n\ndef test_env() -> None:\n    import os\n'
                         '    assert set(os.environ) <= {"PATH", "LANG", "HOME", "PYTEST_CURRENT_TEST", "COV_CORE_SOURCE",'
                         ' "COV_CORE_CONFIG", "COV_CORE_DATAFILE", "COV_CORE_CONTEXT", "COVERAGE_PROCESS_START", "PYTEST_VERSION"}, os.environ\n'
                         f'    assert os.environ["HOME"] != {os.environ["HOME"]!r}\n'
                         '    assert "GITHUB_TOKEN" not in os.environ\n')
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "tests/tools/test_tool.py": probe})
    _run_accounting_everything(ev)
    assert "test_env" not in _evidence_section(base._prompt(ev))  # the probe test passed


def test_sanitise_makes_paths_relative_and_hides_the_homes_and_the_interpreter(tmp_path: Path) -> None:
    import sys
    scratch = evidence_module.Scratch(tmp_path, tmp_path / "clone", tmp_path / "home")
    text = (f"{scratch.clone}/scripts/x.py:3 {scratch.home}/.local/lib/x {os.path.expanduser('~')}/y "
            f"{os.path.join(sys.prefix, 'lib', 'python')}3.10/site.py")
    clean = evidence_module.sanitise(text, scratch)
    assert clean == "scripts/x.py:3 <home>/.local/lib/x <home>/y <python>/lib/python3.10/site.py"
    assert evidence_module.leaked_paths(clean, scratch) == []
    assert evidence_module.leaked_paths(f"{tmp_path}/coverage.json", scratch) == ["the scratch root"]


def test_evidence_still_holding_a_local_path_is_refused_before_any_call(fx: base.Fixture,
                                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    def leaky(*_args: object) -> tuple[str, object]:
        raise launcher.ReviewRefusedError("the computed evidence still holds the author's HOME path; nothing was sent")

    monkeypatch.setattr(launcher, "compute_evidence", leaky)
    assert base._run(fx) == 2
    assert fx.calls() == [] and fx.log() == []


def test_leak_check_in_compute_evidence_refuses(ev: base.Fixture, monkeypatch: pytest.MonkeyPatch) -> None:
    home = os.path.expanduser("~")
    monkeypatch.setattr(evidence_module, "sanitise", lambda text, _scratch: text + f" {home}/x")
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED})
    ev.scenario(base._reply())
    assert base._run(ev) == 2
    assert ev.calls() == []


def test_start_entry_holds_the_hash_of_the_evidence_text_in_the_prompt(fx: base.Fixture) -> None:
    fx.evidence = ["no CI run for this commit"]
    fx.scenario(base._reply(accounted=[base._accounted("EV1", "explained")]))
    assert base._run(fx) == 0
    section = _evidence_section(base._prompt(fx)).split("\n## Evidence\n\n", 1)[1].rstrip("\n")
    assert fx.log()[0]["evidence_sha256"] == launcher.sha256_text(section)


# --- Required diff base (S42-D10) ----------------------------------------------------------------------------------


def test_diff_base_is_required_and_every_prompt_names_the_change(fx: base.Fixture, tmp_path: Path) -> None:
    inputs = launcher.ReviewInputs("c" * 40, "t", "b", "d" * 40, "rules", {base.REVIEWED: ""}, {})
    parts = launcher.PromptParts(mode="initial", task="t")
    with pytest.raises(TypeError):
        launcher.build_prompt(inputs, parts)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        launcher.make_frozen_copy(fx.work, fx.commit, tmp_path / "copy", [])  # type: ignore[call-arg]
    assert base._run(fx) == 0
    with pytest.raises(TypeError):
        launcher.invocation_from_entry(fx.log()[0], fx.work, fx.prompt)  # type: ignore[call-arg]
    assert "_review_inputs/change.diff is the change" in base._prompt(fx)
    assert "_review_inputs/change.diff is the change" in launcher.build_prompt(inputs, parts, diff_base="d" * 40)


def test_rebuild_with_changed_evidence_mismatches(fx: base.Fixture) -> None:
    fx.evidence = ["no CI run for this commit"]
    fx.scenario(base._reply(accounted=[base._accounted("EV1", "explained")]))
    assert base._run(fx) == 0
    start = fx.log()[0]
    given = launcher.GivenInputs(base._evidence_text(fx))
    assert launcher.invocation_from_entry(start, fx.work, fx.prompt, diff_base=start["base_commit"], given=given)[1] == []
    changed = launcher.GivenInputs(base._evidence_text(fx) + "\nEV2: a later CI state")
    mismatches = launcher.invocation_from_entry(start, fx.work, fx.prompt, diff_base=start["base_commit"], given=changed)[1]
    assert mismatches == ["evidence_sha256", "full_prompt_sha256"]


def test_git_is_found_for_the_evidence_clone() -> None:
    assert shutil.which("git") and subprocess.run(["git", "--version"], capture_output=True, check=False).returncode == 0  # noqa: S603, S607 - test probe



# --- Failure paths of the computed inputs (found untested by the launcher's own evidence on this repository) ------


def test_path_hint_naming_a_deleted_file_is_refused(fx: base.Fixture) -> None:
    base._write(fx.work, "scripts/old.py", "print('old')\n")
    base._commit_all(fx.work, "a file to delete")
    base._git(fx.work, "push", "-q", "-f", "origin", "HEAD:poc/base")
    (fx.work / "scripts/old.py").unlink()
    base._write(fx.work, base.REVIEWED, "print('again')\n")
    fx.commit = base._commit_all(fx.work, "delete it")
    args = base._args(fx, "--path", "scripts/old.py")
    assert launcher.main(args, repo=fx.work) == 2 and fx.calls() == []


def test_change_without_a_file_to_open_is_refused(fx: base.Fixture) -> None:
    base._git(fx.work, "push", "-q", "-f", "origin", "HEAD:poc/base")  # the base is the reviewed commit itself
    args = [a for a in base._args(fx) if a not in ("--path", base.REVIEWED)]
    assert launcher.main(args, repo=fx.work) == 2 and fx.calls() == []


def test_a_touched_bundle_without_a_plan_says_so(ev: base.Fixture) -> None:
    base._write(ev.work, "docs/slices/noplan/notes.md", "# Notes\n\nText.\n")
    _change(ev)
    lines = evidence_module.plan_lines(ev.work, ev.commit, RECORD, ["docs/slices/noplan/notes.md"])
    assert "- docs/slices/noplan/plan.md: not at this commit (the change touches docs/slices/noplan/notes.md)" in lines


def test_template_and_archive_folders_are_not_bundles(ev: base.Fixture) -> None:
    lines = evidence_module.plan_lines(ev.work, ev.commit, RECORD, ["docs/slices/_template/plan.md",
                                                                   "docs/slices/archive/old/plan.md"])
    assert lines == [lines[0]] and "the governing plan" in lines[0]


def test_ranges_join_consecutive_lines() -> None:
    assert evidence_module._ranges([5, 1, 2, 3, 9, 10]) == "1-3, 5, 9-10"


@pytest.mark.parametrize("error", [OSError("no python"), subprocess.TimeoutExpired("pytest", 600)], ids=["oserror", "timeout"])
def test_coverage_and_trace_commands_that_raise_are_shown_as_failed(ev: base.Fixture, monkeypatch: pytest.MonkeyPatch,
                                                                    error: Exception) -> None:
    def raising(*_args: object) -> None:
        raise error

    _change(ev)  # a commit with the trace model
    monkeypatch.setattr(evidence_module, "_run", raising)
    scratch = evidence_module.make_scratch(ev.work, ev.commit)
    try:
        evidence = evidence_module.Evidence()
        evidence_module.coverage_evidence(evidence, ev.work, (ev.commit, ev.commit), ["scripts/tool.py"], scratch)
        report, reason = evidence_module.trace_report(scratch, ev.commit)
    finally:
        shutil.rmtree(scratch.root)
    assert evidence.entries == [f"EV1: failed: {evidence_module.COVERAGE_COMMAND}: {type(error).__name__}"]
    assert evidence.status["coverage"] == "failed" and report is None and reason == type(error).__name__


def test_fully_covered_script_and_services_only_change_give_notes_not_entries(ev: base.Fixture) -> None:
    covered = TOOL.replace('"positive"', '"plus"')
    tool_test = TOOL_TEST.replace('"positive"', '"plus"')
    _change(ev, **{"scripts/tool.py": covered, "tests/tools/test_tool.py": tool_test})
    scratch = evidence_module.make_scratch(ev.work, ev.commit)
    try:
        merge_base = base._git(ev.work, "merge-base", "refs/remotes/origin/poc/base", ev.commit)
        evidence = evidence_module.Evidence()
        evidence_module.coverage_evidence(evidence, ev.work, (merge_base, ev.commit), ["scripts/tool.py"], scratch)
        services_only = evidence_module.Evidence()
        evidence_module.coverage_evidence(services_only, ev.work, (merge_base, ev.commit), ["docs/x.md"], scratch)
        evidence_module.trace_evidence(services_only, {"coverage_gaps": {}, "gap_gate": {}}, "", frozenset())
    finally:
        shutil.rmtree(scratch.root)
    assert evidence.entries == [] and "Every changed line and branch run by the tooling tests: scripts/tool.py." in evidence.notes
    assert services_only.entries == [] and services_only.status == {"coverage": "ok", "trace": "ok"}
    assert any(note.startswith("No trace gap among the upstream items") for note in services_only.notes)


def test_trace_script_missing_at_the_commit_is_named(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/validate_traceability.py": None})
    scratch = evidence_module.make_scratch(ev.work, ev.commit)
    try:
        assert evidence_module.trace_report(scratch, ev.commit) == (
            None, "scripts/validate_traceability.py does not exist at this commit")
    finally:
        shutil.rmtree(scratch.root)


def test_fetch_json_reads_json_without_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    import http.server
    import threading

    seen: dict[str, str | None] = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - the http.server hook name
            seen["auth"] = self.headers.get("Authorization")
            body = json.dumps({"workflow_runs": []}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args: object) -> None:
            return

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("GITHUB_TOKEN", "planted-token-value-not-for-the-api")
    try:
        assert evidence_module.fetch_json(f"http://127.0.0.1:{server.server_port}/runs") == {"workflow_runs": []}
    finally:
        server.shutdown()
    assert seen["auth"] is None


def test_github_repo_of_a_clone_without_a_github_origin_is_none(tmp_path: Path) -> None:
    base._git(tmp_path, "init", "-q")
    assert evidence_module.github_repo(tmp_path) is None
    base._git(tmp_path, "remote", "add", "origin", "https://github.com/owner/name.git")
    assert evidence_module.github_repo(tmp_path) == ("owner", "name")


@pytest.mark.parametrize("failure", ["scratch", "compute"])
def test_evidence_that_cannot_be_prepared_refuses_before_any_call(ev: base.Fixture, monkeypatch: pytest.MonkeyPatch,
                                                                   failure: str) -> None:
    def raising(*_args: object) -> None:
        raise ValueError("git clone failed")

    monkeypatch.setattr(evidence_module, "make_scratch" if failure == "scratch" else "upstream_items", raising)
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED})
    assert base._run(ev) == 2
    assert ev.calls() == [] and ev.log() == []
