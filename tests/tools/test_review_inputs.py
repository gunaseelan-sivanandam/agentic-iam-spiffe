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
inputs_module = launcher._INPUTS
REAL_COMPUTE = launcher.compute_evidence
REAL_UPSTREAM = launcher._upstream_and_trace
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
    monkeypatch.setattr(launcher, "_upstream_and_trace", REAL_UPSTREAM)
    monkeypatch.setattr(inputs_module, "github_repo", lambda _repo: ("owner", "repo"))
    monkeypatch.setattr(inputs_module, "fetch_json", lambda _url: {"workflow_runs": []})
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
    commit = base._recheck(fx, f"| X1 | high | rejected: the scenario does not happen, {base.FACT} |")
    fx.scenario(base._reply(accounted=[base._accounted("X1", quotes=[base.QUOTE])]))
    assert base._run(fx, round_no=2, commit=commit) == 0
    assert "open the files each answer names first" in base._section(base._prompt(fx), "Paths under review")


def test_review_that_opened_none_of_the_hint_files_fails_even_when_it_opened_other_listed_files(fx: base.Fixture) -> None:
    fx.scenario({"reads": ["AGENTS.md"]})
    assert base._run(fx) == 1
    assert base._ends(fx)[0]["reason"] == "the review saw none of the paths under review"
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
    assert inputs_module.UPSTREAM_QUESTION in upstream


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
    assert inputs_module.UPSTREAM_QUESTION in base._prompt(fx)
    assert inputs_module.UPSTREAM_QUESTION == ("Does any problem you find originate upstream (a requirement, the "
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
    assert inputs_module.SUBPROCESS_NOTE in evidence
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

    monkeypatch.setattr(inputs_module, "github_repo", lambda _repo: ("owner", "repo"))
    evidence = inputs_module.Evidence()
    inputs_module.ci_evidence(evidence, tmp_path, commit, fake)
    text = evidence.text()
    assert all(e in text for e in expected) and not any(a in text for a in absent)
    assert "CI run CI 2" not in text and calls[0].endswith(f"head_sha={commit}&per_page=50")
    assert evidence.status["ci"] == "ok"


def test_unreadable_ci_api_is_shown_as_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(_url: str) -> dict:
        raise OSError("network down")

    monkeypatch.setattr(inputs_module, "github_repo", lambda _repo: ("owner", "repo"))  # any clone's origin
    evidence = inputs_module.Evidence()
    inputs_module.ci_evidence(evidence, ROOT, "c" * 40, broken)
    assert evidence.entries == [f"EV1: failed: {inputs_module.CI_COMMAND}: OSError"]
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
    assert base._ends(fx)[0]["reason"].startswith("the reply does not match the report schema: accounted 0: a flagged")


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
    assert f"failed: {inputs_module.COVERAGE_COMMAND}: exit " in evidence
    assert "No entries" not in evidence and ev.log()[-2]["evidence_status"]["coverage"] == "failed"


def test_trace_model_that_cannot_run_is_shown_as_failed(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "docs/requirements.md": "# no requirements\n"})
    _run_accounting_everything(ev)
    prompt = base._prompt(ev)
    assert f"failed: {inputs_module.TRACE_COMMAND}: exit 2" in _evidence_section(prompt)
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
    scratch = inputs_module.Scratch(tmp_path, tmp_path / "clone", tmp_path / "home")
    text = (f"{scratch.clone}/scripts/x.py:3 {scratch.home}/.local/lib/x {os.path.expanduser('~')}/y "
            f"{os.path.join(sys.prefix, 'lib', 'python')}3.10/site.py")
    clean = inputs_module.sanitise(text, scratch)
    assert clean == "scripts/x.py:3 <home>/.local/lib/x <home>/y <python>/lib/python3.10/site.py"
    assert inputs_module.leaked_paths(clean, scratch) == []
    assert inputs_module.leaked_paths(f"{tmp_path}/coverage.json", scratch) == ["the scratch root"]


def test_evidence_still_holding_a_local_path_is_refused_before_any_call(fx: base.Fixture,
                                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    def leaky(*_args: object) -> tuple[str, object]:
        raise launcher.ReviewRefusedError("the computed evidence still holds the author's HOME path; nothing was sent")

    monkeypatch.setattr(launcher, "compute_evidence", leaky)
    assert base._run(fx) == 2
    assert fx.calls() == [] and fx.log() == []


def test_leak_check_in_compute_evidence_refuses(ev: base.Fixture, monkeypatch: pytest.MonkeyPatch) -> None:
    home = os.path.expanduser("~")
    monkeypatch.setattr(inputs_module, "sanitise", lambda text, _scratch: text + f" {home}/x")
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED})
    ev.scenario(base._reply())
    assert base._run(ev) == 2
    assert ev.calls() == []


def test_start_entry_holds_the_hash_of_the_evidence_text_in_the_prompt(fx: base.Fixture) -> None:
    fx.evidence = ["no CI run for this commit"]
    fx.scenario(base._reply(accounted=[base._accounted("EV1", "explained")]))
    assert base._run(fx) == 0
    section = _evidence_section(base._prompt(fx)).split("\n## Evidence\n\n", 1)[1].rstrip("\n") + "\n"
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
    lines = inputs_module.plan_lines(ev.work, ev.commit, RECORD, ["docs/slices/noplan/notes.md"])
    assert "- docs/slices/noplan/plan.md: not at this commit (the change touches docs/slices/noplan/notes.md)" in lines


def test_template_and_archive_folders_are_not_bundles(ev: base.Fixture) -> None:
    lines = inputs_module.plan_lines(ev.work, ev.commit, RECORD, ["docs/slices/_template/plan.md",
                                                                   "docs/slices/archive/old/plan.md"])
    assert lines == [lines[0]] and "the governing plan" in lines[0]


def test_ranges_join_consecutive_lines() -> None:
    assert inputs_module._ranges([5, 1, 2, 3, 9, 10]) == "1-3, 5, 9-10"


@pytest.mark.parametrize("error", [OSError("no python"), subprocess.TimeoutExpired("pytest", 600)], ids=["oserror", "timeout"])
def test_coverage_and_trace_commands_that_raise_are_shown_as_failed(ev: base.Fixture, monkeypatch: pytest.MonkeyPatch,
                                                                    error: Exception) -> None:
    def raising(*_args: object) -> None:
        raise error

    _change(ev)  # a commit with the trace model
    monkeypatch.setattr(inputs_module, "_run", raising)
    scratch = inputs_module.make_scratch(ev.work, ev.commit)
    try:
        evidence = inputs_module.Evidence()
        inputs_module.coverage_evidence(evidence, ev.work, (ev.commit, ev.commit), ["scripts/tool.py"], scratch)
        report, reason = inputs_module.trace_report(scratch, ev.commit)
    finally:
        shutil.rmtree(scratch.root)
    assert evidence.entries == [f"EV1: failed: {inputs_module.COVERAGE_COMMAND}: {type(error).__name__}"]
    assert evidence.status["coverage"] == "failed" and report is None and reason == type(error).__name__


def test_fully_covered_script_and_services_only_change_give_notes_not_entries(ev: base.Fixture) -> None:
    covered = TOOL.replace('"positive"', '"plus"')
    tool_test = TOOL_TEST.replace('"positive"', '"plus"')
    _change(ev, **{"scripts/tool.py": covered, "tests/tools/test_tool.py": tool_test})
    scratch = inputs_module.make_scratch(ev.work, ev.commit)
    try:
        merge_base = base._git(ev.work, "merge-base", "refs/remotes/origin/poc/base", ev.commit)
        evidence = inputs_module.Evidence()
        inputs_module.coverage_evidence(evidence, ev.work, (merge_base, ev.commit), ["scripts/tool.py"], scratch)
        services_only = inputs_module.Evidence()
        inputs_module.coverage_evidence(services_only, ev.work, (merge_base, ev.commit), ["docs/x.md"], scratch)
        inputs_module.trace_evidence(services_only, {"coverage_gaps": {}, "gap_gate": {}}, "", frozenset())
    finally:
        shutil.rmtree(scratch.root)
    assert evidence.entries == [] and "Every changed line and branch run by the tooling tests: scripts/tool.py." in evidence.notes
    assert services_only.entries == [] and services_only.status == {"coverage": "ok", "trace": "ok"}
    assert any(note.startswith("No trace gap among the upstream items") for note in services_only.notes)


def test_trace_script_missing_at_the_commit_is_named(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/validate_traceability.py": None})
    scratch = inputs_module.make_scratch(ev.work, ev.commit)
    try:
        assert inputs_module.trace_report(scratch, ev.commit) == (
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
        assert inputs_module.fetch_json(f"http://127.0.0.1:{server.server_port}/runs") == {"workflow_runs": []}
    finally:
        server.shutdown()
    assert seen["auth"] is None


def test_github_repo_of_a_clone_without_a_github_origin_is_none(tmp_path: Path) -> None:
    base._git(tmp_path, "init", "-q")
    assert inputs_module.github_repo(tmp_path) is None
    base._git(tmp_path, "remote", "add", "origin", "https://github.com/owner/name.git")
    assert inputs_module.github_repo(tmp_path) == ("owner", "name")


@pytest.mark.parametrize("failure", ["scratch", "compute"])
def test_evidence_that_cannot_be_prepared_refuses_before_any_call(ev: base.Fixture, monkeypatch: pytest.MonkeyPatch,
                                                                   failure: str) -> None:
    def raising(*_args: object) -> None:
        raise ValueError("git clone failed")

    monkeypatch.setattr(inputs_module, "make_scratch" if failure == "scratch" else "upstream_items", raising)
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED})
    assert base._run(ev) == 2
    assert ev.calls() == [] and ev.log() == []


def test_ci_of_a_repository_without_a_github_origin_is_shown_as_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inputs_module, "github_repo", lambda _repo: None)
    evidence = inputs_module.Evidence()
    inputs_module.ci_evidence(evidence, ROOT, "c" * 40, lambda _url: pytest.fail("no API call without a repository"))
    assert evidence.entries == [f"EV1: failed: {inputs_module.CI_COMMAND}: the origin remote is not a GitHub repository"]
    assert evidence.status["ci"] == "failed"


def test_ranges_of_no_lines_is_empty() -> None:
    assert inputs_module._ranges([]) == ""


def test_scratch_of_an_unknown_commit_is_removed_again(fx: base.Fixture) -> None:
    import tempfile
    before = set(Path(tempfile.gettempdir()).glob("review-evidence-*"))
    with pytest.raises(ValueError, match="git checkout failed"):
        inputs_module.make_scratch(fx.work, "0" * 40)
    assert set(Path(tempfile.gettempdir()).glob("review-evidence-*")) == before


# --- Answers to review round 1 of the 4.2 implementation ----------------------------------------------------------


def test_accepted_trace_gap_is_marked_accepted(ev: base.Fixture) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED,
                   "trace/tests.yaml": TESTS.replace("accepted_gaps: []", "accepted_gaps:\n  - gap: "
                                                     "requirements_without_proof:REQ-T-R2\n    reason: planned\n"
                                                     "    expires: 2099-01-01\n")})
    _run_accounting_everything(ev)
    evidence = _evidence_section(base._prompt(ev))
    assert "trace gap requirements_without_proof:REQ-T-R2 (accepted, against the merge-base" in evidence


def test_completed_ci_job_shows_its_own_conclusion(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    commit = "c" * 40
    run = {"id": 7, "name": "CI", "event": "pull_request", "status": "completed", "conclusion": "success",
           "head_sha": commit}
    jobs = [{"name": "lint", "status": "completed", "conclusion": "success"},
            {"name": "e2e", "status": "completed", "conclusion": "failure"},
            {"name": "docs-check", "status": "queued", "conclusion": None}]

    def fake(url: str) -> dict:
        return {"jobs": jobs} if url.endswith("/jobs?per_page=100") else {"workflow_runs": [run]}

    monkeypatch.setattr(inputs_module, "github_repo", lambda _repo: ("owner", "repo"))
    evidence = inputs_module.Evidence()
    inputs_module.ci_evidence(evidence, tmp_path, commit, fake)
    assert evidence.entries == ["EV1: CI run CI 7 (pull_request): completed/success; jobs: lint: completed/success; "
                                "e2e: completed/failure; docs-check: queued"]


def test_items_unrelated_to_the_change_stay_out_of_upstream_and_evidence(ev: base.Fixture) -> None:
    unrelated_arch = ARCHITECTURE + ("\n## ARCH-002 Another tool\n\nType: Component\nSatisfies: REQ-T-R4\n"
                                     "Implemented by: scripts/other.py\n")
    other = TOOL.replace("def classify", "# DD: DD-002\n# Implements: ARCH-002\n# Title: Other\ndef classify")
    base._write(ev.work, "docs/requirements.md", REQUIREMENTS + "\n## REQ-T-R4 — An unrelated unproved thing\n\nText.\n")
    base._write(ev.work, "docs/architecture.md", unrelated_arch)
    base._write(ev.work, "scripts/other.py", other)
    base._commit_all(ev.work, "an unrelated item with a gap")
    base._git(ev.work, "push", "-q", "-f", "origin", "HEAD:poc/base")
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED})
    _run_accounting_everything(ev)
    prompt = base._prompt(ev)
    upstream, evidence = base._section(prompt, "Upstream items"), _evidence_section(prompt)
    assert "ARCH-001" in upstream and "ARCH-002" not in upstream and "DD-002" not in upstream
    assert "REQ-T-R2" in evidence and "REQ-T-R4" not in evidence and "DD-002" not in evidence


def test_rebuild_of_an_entry_logged_by_4_1s_launcher_says_its_layout_is_retired(fx: base.Fixture) -> None:
    assert base._run(fx) == 0
    entry = {k: v for k, v in fx.log()[0].items() if k not in ("path_hints", "upstream_sha256", "evidence_sha256")}
    with pytest.raises(ValueError, match="before slice 4.2: its prompt layout is retired"):
        launcher.invocation_from_entry(entry, fx.work, fx.prompt, diff_base=entry["base_commit"], given=base._given(fx))


@pytest.mark.parametrize("broken", ["tests: [unclosed\n", "- a list, not a mapping\n"], ids=["invalid-yaml", "not-a-mapping"])
def test_unreadable_trace_tests_yaml_is_shown_not_a_crash(ev: base.Fixture, broken: str) -> None:
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "trace/tests.yaml": broken})
    _run_accounting_everything(ev)
    prompt = base._prompt(ev)
    assert "- not available: trace/tests.yaml is not " in base._section(prompt, "Upstream items")
    assert f"failed: {inputs_module.TRACE_COMMAND}" in _evidence_section(prompt)


def test_scratch_home_links_only_the_user_site_packages(ev: base.Fixture) -> None:
    import site
    scratch = inputs_module.make_scratch(ev.work, ev.commit)
    try:
        links = [p for p in scratch.home.rglob("*") if p.is_symlink()]
        if Path(site.getusersitepackages()).is_dir():
            assert [p.resolve() for p in links] == [Path(site.getusersitepackages()).resolve()]
            assert links[0].relative_to(scratch.home) == Path(".local") / Path(site.getusersitepackages()).relative_to(
                Path(site.getuserbase()))
        assert not (scratch.home / ".local" / "bin").exists() and not (scratch.home / ".local" / "share").exists()
    finally:
        shutil.rmtree(scratch.root)


def test_user_base_keeps_its_place_under_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    assert inputs_module.user_base_under_home(tmp_path / "Library" / "Python" / "3.12") == Path("Library/Python/3.12")
    assert inputs_module.user_base_under_home(tmp_path / ".local") == Path(".local")
    assert inputs_module.user_base_under_home(Path("/elsewhere/.local")) == Path(".local")


# --- Round 2 of slice 4, R2-6: the process files a recheck's evidence lists -------------------------------------


@pytest.mark.parametrize(("path", "process"), [
    ("AGENTS.md", True), ("tests/unit/AGENTS.md", True),  # the rulebook
    ("Makefile", True), ("ruff_changed_files.toml", True), ("scripts/check_docs.py", True),  # gates, QA tooling
    ("scripts/check_review_records.py", True), ("scripts/validate_traceability.py", True),
    ("scripts/mutation_gate.py", True), ("scripts/diff_coverage_gate.sh", True), ("scripts/qa_deploy.py", True),
    ("scripts/test_lint.py", True), ("scripts/lint_changed_files.py", True), ("scripts/evidence_secrets.py", True),
    ("scripts/run_e2e.sh", True),
    (".github/workflows/ci.yml", True), (".github/CODEOWNERS", True),  # CI
    ("docs/slices/_template/plan.md", True), ("docs/review_checklists/code.md", True),  # templates, checklists
    ("scripts/run_independent_review.py", True), ("scripts/review_inputs.py", True),  # the launcher and the brief
    ("scripts/review_records.py", True), ("scripts/review_brief.py", True),
    ("scripts/run_review_benchmark.py", True), ("tests/review_benchmark/answer_key.yaml", True),  # decision concern 15
    (".claude/skills/grill-me/SKILL.md", True),
    ("tests/review_benchmark/prompts/mandate_recheck_b.md", False),
    ("scripts/rogue_node_tests.sh", False), ("tests/tools/test_review_inputs.py", False),  # tests, the E2E harness
    ("tests/unit/test_issuer.py", False), ("services/tool-b/server.py", False), ("docs/slices/demo/plan.md", False),
    ("docs/requirements.md", False), ("docs/AGENTS.md", False), ("README.md", False),
    ("scripts/varambu_audit.py", False),
])
def test_process_files_are_the_rulebook_gates_ci_templates_checklists_and_the_launcher(path: str, process: bool) -> None:
    assert inputs_module.is_process_file(path) is process


def test_process_file_evidence_lists_a_changed_skill_and_the_benchmark_runner_with_its_answer_key(
        fx: base.Fixture) -> None:
    """Decision concern 15 (the owner, 2026-11-17, folded into R3-1): a recheck shows a change to a skill, the benchmark
    runner or its answer key, as it shows a change to the rulebook or a gate."""
    earlier = fx.commit
    base._write(fx.work, ".claude/skills/grill-me/SKILL.md", "---\nname: grill-me\n---\n# Grill me\n")
    base._write(fx.work, "scripts/run_review_benchmark.py", "print('runner')\n")
    base._write(fx.work, "tests/review_benchmark/answer_key.yaml", "# The answer key.\ncases: []\n")
    commit = base._commit_all(fx.work, "a skill, the benchmark runner and its answer key")
    evidence = inputs_module.Evidence()
    inputs_module.process_file_evidence(evidence, fx.work, (earlier,), commit)
    span = f"({earlier[:12]} to {commit[:12]}; {inputs_module.PROCESS_COMMAND})"
    assert evidence.entries == [
        f"EV1: process file changed since the reviewed round: .claude/skills/grill-me/SKILL.md, +4 -0 lines {span}",
        f"EV2: process file changed since the reviewed round: scripts/run_review_benchmark.py, +1 -0 lines {span}",
        f"EV3: process file changed since the reviewed round: tests/review_benchmark/answer_key.yaml, +2 -0 lines {span}"]


def test_a_recheck_takes_upstream_items_and_evidence_from_the_commits_since_the_reviewed_round(ev: base.Fixture) -> None:
    """R3-1: in a recheck the sections and test entries the change edits, the trace links of its files, the changed
    lines and the trace gaps come from the commits since the reviewed round, a gap marked against that round's commit;
    the governing plan stays."""
    _change(ev, **{"scripts/tool.py": TOOL_CHANGED, "docs/requirements.md": REQUIREMENTS.replace("Text.", "New.", 1)})
    ev.scenario(base._reply())
    base._run(ev)
    items = _items(base._prompt(ev))
    ev.scenario(base._reply([base._finding("X1")], [base._accounted(i, "explained", note="fine") for i in items], "no"))
    assert base._run(ev) == 0
    reviewed = ev.commit
    requirements = (ev.work / "docs/requirements.md").read_text()
    base._write(ev.work, "docs/requirements.md", requirements + "\n## REQ-T-R3 — A new unproved thing\n\nText.\n")
    base._write(ev.work, "docs/architecture.md", ARCHITECTURE.replace("REQ-T-R2", "REQ-T-R2, REQ-T-R3"))
    commit = base._answers(ev, "unit1/c1/r1/A/2", "| X1 | high | fixed: docs/requirements.md: REQ-T-R3 added |")
    ev.scenario(base._reply())
    base._run(ev, round_no=2, commit=commit)
    upstream, evidence = base._section(base._prompt(ev), "Upstream items"), _evidence_section(base._prompt(ev))
    assert "docs/slices/demo/plan.md (the governing plan: the bundle of the review record)" in upstream
    assert "REQ-T-R3 (found: the change edits its section in docs/requirements.md)" in upstream
    assert "REQ-T-R1 (found" not in upstream and "scripts/tool.py" not in upstream  # edited before round 1
    assert f"trace gap requirements_without_proof:REQ-T-R3 (new, against the reviewed round's commit {reviewed[:12]}" in evidence
    assert "scripts/tool.py" not in evidence and "against the merge-base" not in evidence


def test_process_file_evidence_lists_line_counts_and_shows_a_comparison_that_cannot_run_as_failed(fx: base.Fixture) -> None:
    earlier = fx.commit
    base._write(fx.work, "Makefile", "lint:\n\truff check .\n")
    (fx.work / ".github").mkdir()
    (fx.work / ".github" / "logo.png").write_bytes(b"\x00\x01\x02binary")
    base._write(fx.work, "README.md", "# Readme\n")
    commit = base._commit_all(fx.work, "process and other files")
    evidence = inputs_module.Evidence()
    inputs_module.process_file_evidence(evidence, fx.work, (earlier,), commit)
    span = f"({earlier[:12]} to {commit[:12]}; {inputs_module.PROCESS_COMMAND})"
    assert evidence.entries == [
        f"EV1: process file changed since the reviewed round: .github/logo.png, binary {span}",
        f"EV2: process file changed since the reviewed round: Makefile, +2 -0 lines {span}"]
    assert evidence.status == {"process": "ok"} and evidence.notes == []
    unchanged = inputs_module.Evidence()
    inputs_module.process_file_evidence(unchanged, fx.work, (commit,), commit)
    assert unchanged.entries == [] and unchanged.status == {"process": "ok"}
    assert unchanged.notes == [f"No process file changed since the reviewed round ({commit[:12]} to {commit[:12]}; "
                               f"{inputs_module.PROCESS_COMMAND})."]
    failed = inputs_module.Evidence()
    inputs_module.process_file_evidence(failed, fx.work, ("0" * 40,), commit)
    assert failed.entries == [f"EV1: failed: {inputs_module.PROCESS_COMMAND}: git cannot compare {'0' * 12} with "
                              f"{commit[:12]}"]
    assert failed.status == {"process": "failed"}
    nothing = inputs_module.Evidence()
    inputs_module.process_file_evidence(nothing, fx.work, (), commit)  # not a recheck: nothing to compare
    assert (nothing.entries, nothing.notes, nothing.status) == ([], [], {})
