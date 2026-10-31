"""Negative controls for the trace model in scripts/validate_traceability.py (slice ci-evidence-trace,
test plan V4, V7, V8, V9, V11, V12).

Each test builds a small repository in a temporary directory, commits it to git where the gap gate
needs a merge-base, and runs the real script there.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess  # nosec B404 - fixed git/python argv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_traceability.py"

BASE_FILES = {
    "docs/requirements.md": (
        "## REQ-T-A1 — Alpha behaviour\nThe system shall alpha.\n\n"
        "## REQ-SEC-K1 — Key confinement\nThe key reaches only its holders.\n"
    ),
    "docs/architecture.md": (
        "## ARCH-001 Alpha component\n\nType: Component\nSatisfies: REQ-T-A1, REQ-SEC-K1\n"
    ),
    "services/alpha.py": "# DD: DD-001\n# Implements: ARCH-001\n# Title: alpha function\ndef alpha():\n    return 1\n",
    "scripts/.keep": "",
    "tests/unit/test_alpha.py": (
        "# UT: UT-001\n# Test Description: alpha returns one\n# Precondition: none\n"
        "# Expected Output: 1\n# Covers DD: DD-001\ndef test_alpha():\n    assert True\n"
    ),
    "tests/tools/test_gate.py": "def test_gate_fails_on_violation():\n    assert True\n",
    "harness.sh": 'begin_test_evidence "A-T1" "alpha"\n',
    "Makefile": "check:\n\ttrue\n",
    "security/invariants.yaml": (
        "assets:\n  K1:\n    requirement: REQ-SEC-K1\n    locations:\n      - path: keys\n        holders: [issuer]\n"
        "services:\n  issuer:\n    root: forbidden\nknown_violations: []\n"
    ),
    "trace/tests.yaml": (
        "version: 1\ntests:\n"
        "- id: E2E-A\n  type: e2e_suite\n  source_requirements: [REQ-T-A1]\n"
        "  location: {file: harness.sh, selector: A-T1}\n  evidence_prefixes: [A-T1]\n"
        "- id: STATIC-K1\n  type: static_test\n  title: Key confinement\n  source_requirements: [REQ-SEC-K1]\n"
        "  gate: make check\n  negative_controls: [tests/tools/test_gate.py::test_gate_fails_on_violation]\n"
        "  result: artifacts/quality/report.json\n"
        "accepted_gaps: []\n"
    ),
}


def _write(repo: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = repo / name
        if text is None:
            path.unlink(missing_ok=True)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _git(repo: Path, *args: str) -> str:
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
    return subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True).stdout


def _repo(tmp_path: Path, files: dict[str, str] | None = None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, {**BASE_FILES, **(files or {})})
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    return repo


def _commit(repo: Path, files: dict[str, str], branch: str | None = "feature") -> None:
    if branch:
        _git(repo, "checkout", "-q", "-b", branch)
    _write(repo, files)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "change")


def _run(repo: Path, *args: str) -> tuple[subprocess.CompletedProcess, dict]:
    report = repo.parent / "report.json"
    report.unlink(missing_ok=True)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--report-json", str(report),
         "--design-report-json", str(repo.parent / "design.json"), *args],
        cwd=repo, capture_output=True, text=True, check=False)
    data = json.loads(report.read_text()) if report.exists() else {}
    return result, data


def _trace_with(extra: str) -> dict[str, str]:
    return {"trace/tests.yaml": BASE_FILES["trace/tests.yaml"].replace("accepted_gaps: []\n", extra)}


def _static(**overrides: str) -> dict[str, str]:
    text = BASE_FILES["trace/tests.yaml"]
    for old, new in overrides.items():
        text = text.replace(old, new)
    return {"trace/tests.yaml": text}


# --- V4 static test entries ----------------------------------------------------

def test_static_entry_with_gate_and_negative_controls_proves_its_requirement(tmp_path: Path) -> None:
    result, report = _run(_repo(tmp_path), "--mode", "push")
    assert result.returncode == 0, result.stderr
    assert report["requirements"]["REQ-SEC-K1"]["status"] == "proved: static"
    assert report["requirements"]["REQ-T-A1"]["status"] == "proved: e2e"
    assert report["coverage_gaps"]["requirements_without_proof"] == []


@pytest.mark.parametrize(("old", "new", "message"), [
    ("tests/tools/test_gate.py::", "tests/tools/missing.py::", "negative control file not found"),
    ("::test_gate_fails_on_violation", "::test_missing", "negative control test 'test_missing' not found"),
    ("  negative_controls: [tests/tools/test_gate.py::test_gate_fails_on_violation]\n", "", "negative_controls must list"),
    ("gate: make check", "gate: make missing", "gate target 'missing' not found in Makefile"),
    ("gate: make check", "gate: pytest", "gate must be 'make <target>'"),
    ("  result: artifacts/quality/report.json\n", "", "result must name"),
])
def test_broken_static_entry_is_a_structural_failure(tmp_path: Path, old: str, new: str, message: str) -> None:
    result, _ = _run(_repo(tmp_path, _static(**{old: new})), "--mode", "push")
    assert result.returncode == 1
    assert message in result.stderr


# --- V7 status from the register ------------------------------------------------

def test_known_violation_row_makes_the_requirement_not_proved(tmp_path: Path) -> None:
    register = BASE_FILES["security/invariants.yaml"].replace(
        "known_violations: []\n", "known_violations:\n  - {opl: OPL-005, asset: K1, services: [x], expires: 2026-12-31}\n")
    result, report = _run(_repo(tmp_path, {"security/invariants.yaml": register}), "--mode", "push")
    assert result.returncode == 0, result.stderr
    assert report["requirements"]["REQ-SEC-K1"]["status"] == "not proved: known violation OPL-005"
    assert report["coverage_gaps"]["requirements_without_proof"] == ["REQ-SEC-K1"]


@pytest.mark.parametrize(("now", "status"), [
    ("2027-01-31T23:59:59+00:00", "not proved: grace until 2027-01-31"),
    ("2027-02-01T00:00:00+00:00", "proved: static"),
])
def test_nonroot_requirement_is_not_proved_within_its_grace(tmp_path: Path, now: str, status: str) -> None:
    files = {
        "docs/requirements.md": BASE_FILES["docs/requirements.md"] + "\n## REQ-SEC-D2 — Non-root workloads\nNo root.\n",
        "docs/architecture.md": BASE_FILES["docs/architecture.md"].replace("REQ-SEC-K1\n", "REQ-SEC-K1, REQ-SEC-D2\n"),
        "security/invariants.yaml": BASE_FILES["security/invariants.yaml"].replace("root: forbidden", "root: grandfathered"),
        "trace/tests.yaml": BASE_FILES["trace/tests.yaml"].replace(
            "accepted_gaps: []\n",
            "- id: STATIC-D2\n  type: static_test\n  source_requirements: [REQ-SEC-D2]\n  gate: make check\n"
            "  negative_controls: [tests/tools/test_gate.py::test_gate_fails_on_violation]\n  result: r.json\n"
            "accepted_gaps: []\n"),
    }
    result, report = _run(_repo(tmp_path, files), "--mode", "push", "--now", now)
    assert result.returncode == 0, result.stderr
    assert report["requirements"]["REQ-SEC-D2"]["status"] == status


def test_repository_statuses_in_a_clean_copy_without_artifacts(tmp_path: Path) -> None:
    # Only files git tracks or would track: no artifacts, no runtime state (SPIRE data, sockets).
    copy = tmp_path / "copy"
    listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, check=True, capture_output=True, text=True).stdout.split("\0")
    for name in filter(None, listed):
        if (ROOT / name).is_file():
            (copy / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, copy / name)
    assert not (copy / "artifacts").exists()
    result, report = _run(copy, "--mode", "push", "--now", "2026-11-01T00:00:00+00:00")
    assert result.returncode == 0, result.stderr
    status = {r: v["status"] for r, v in report["requirements"].items() if r.startswith("REQ-SEC") or r == "REQ-T-R9"}
    assert status == {
        "REQ-SEC-K1": "not proved: known violation OPL-005",
        "REQ-SEC-K2": "not proved: known violation OPL-006",
        "REQ-SEC-K4": "not proved: known violation OPL-008",
        "REQ-SEC-D2": "not proved: grace until 2027-01-31",
        **{r: "proved: static" for r in ("REQ-SEC-K3", "REQ-SEC-K5", "REQ-SEC-K6", "REQ-SEC-K7",
                                         "REQ-SEC-K8", "REQ-SEC-D1", "REQ-T-R9")},
    }


# --- V8 config-implemented ARCH -----------------------------------------------

def _arch(extra_section: str) -> dict[str, str]:
    return {"docs/architecture.md": BASE_FILES["docs/architecture.md"] + "\n" + extra_section}


def test_implemented_by_existing_files_counts_as_implemented(tmp_path: Path) -> None:
    files = _arch("## ARCH-002 Config\n\nType: Component\nSatisfies: REQ-T-A1\nImplemented by: `Makefile`, `harness.sh`\n")
    result, report = _run(_repo(tmp_path, files), "--mode", "push")
    assert result.returncode == 0, result.stderr
    assert report["architecture"]["ARCH-002"]["implemented_by"] == ["Makefile", "harness.sh"]
    assert report["coverage_gaps"]["architecture_without_implementation"] == []


def test_implemented_by_missing_file_is_a_structural_failure(tmp_path: Path) -> None:
    files = _arch("## ARCH-002 Config\n\nType: Component\nSatisfies: REQ-T-A1\nImplemented by: `missing.conf`\n")
    result, _ = _run(_repo(tmp_path, files), "--mode", "push")
    assert result.returncode == 1
    assert "ARCH-002: Implemented by file not found 'missing.conf'" in result.stderr


def test_arch_without_dd_or_implemented_by_stays_a_gap(tmp_path: Path) -> None:
    files = _arch("## ARCH-002 Config\n\nType: Component\nSatisfies: REQ-T-A1\n")
    result, report = _run(_repo(tmp_path, files), "--mode", "push")
    assert result.returncode == 0, result.stderr
    assert report["coverage_gaps"]["architecture_without_implementation"] == ["ARCH-002"]


# --- V9 gap gate -----------------------------------------------------------------

NEW_GAPS = {
    "requirement without proof": (
        {"docs/requirements.md": BASE_FILES["docs/requirements.md"] + "\n## REQ-T-A2 — Beta\nBeta.\n",
         "docs/architecture.md": BASE_FILES["docs/architecture.md"].replace("REQ-SEC-K1\n", "REQ-SEC-K1, REQ-T-A2\n")},
        "requirements_without_proof:REQ-T-A2"),
    "ARCH without implementation": (_arch("## ARCH-002 Beta\n\nType: Component\nSatisfies: REQ-T-A1\n"),
                                    "architecture_without_implementation:ARCH-002"),
    "DD without UT": ({"services/beta.py": "# DD: DD-002\n# Implements: ARCH-001\n# Title: beta\ndef beta():\n    return 2\n"},
                      "dd_without_ut:DD-002"),
    "test without requirement": (
        {"trace/tests.yaml": BASE_FILES["trace/tests.yaml"].replace(
            "accepted_gaps: []\n",
            "- id: E2E-B\n  type: e2e_suite\n  location: {file: harness.sh, selector: A-T1}\n  evidence_prefixes: [A-T1]\n"
            "accepted_gaps: []\n")},
        "tests_without_requirements:E2E-B"),
}


@pytest.mark.parametrize("kind", sorted(NEW_GAPS))
def test_pr_adding_a_gap_fails_naming_it(tmp_path: Path, kind: str) -> None:
    repo = _repo(tmp_path)
    files, gap = NEW_GAPS[kind]
    _commit(repo, files)
    result, report = _run(repo, "--mode", "pr", "--base", "main")
    assert result.returncode == 1
    assert f"new coverage gap {gap}" in result.stderr
    assert report["gap_gate"]["new_gaps"] == [gap]


def test_closing_one_gap_and_adding_another_fails(tmp_path: Path) -> None:
    repo = _repo(tmp_path, _arch("## ARCH-002 Old\n\nType: Component\nSatisfies: REQ-T-A1\n"))
    _commit(repo, {"docs/architecture.md": BASE_FILES["docs/architecture.md"]
                   + "\n## ARCH-002 Old\n\nType: Component\nSatisfies: REQ-T-A1\nImplemented by: `Makefile`\n"
                   + "\n## ARCH-003 New\n\nType: Component\nSatisfies: REQ-T-A1\n"})
    result, report = _run(repo, "--mode", "pr", "--base", "main")
    assert result.returncode == 1
    assert report["gap_gate"]["closed_gaps"] == ["architecture_without_implementation:ARCH-002"]
    assert report["gap_gate"]["new_gaps"] == ["architecture_without_implementation:ARCH-003"]


def _accepted(gap: str, expires: str = "2026-12-31", reason: str = "planned in slice X") -> str:
    return f'accepted_gaps:\n- {{gap: "{gap}", reason: "{reason}", expires: {expires}}}\n'


def test_accepted_gap_entry_lets_the_gap_pass(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    files, gap = NEW_GAPS["DD without UT"]
    _commit(repo, {**files, **_trace_with(_accepted(gap))})
    result, report = _run(repo, "--mode", "pr", "--base", "main", "--now", "2026-11-01T00:00:00+00:00")
    assert result.returncode == 0, result.stderr
    assert report["gap_gate"]["accepted"] == [gap]


@pytest.mark.parametrize(("now", "passes"), [("2026-12-31T23:59:59+00:00", True), ("2027-01-01T00:00:00+00:00", False)])
def test_accepted_gap_is_valid_through_its_expiry_date(tmp_path: Path, now: str, passes: bool) -> None:
    repo = _repo(tmp_path)
    files, gap = NEW_GAPS["DD without UT"]
    _commit(repo, {**files, **_trace_with(_accepted(gap))})
    result, _ = _run(repo, "--mode", "pr", "--base", "main", "--now", now)
    assert (result.returncode == 0) is passes, result.stderr
    if not passes:
        assert f"accepted gap {gap} expired on 2026-12-31" in result.stderr


def test_stale_accepted_gap_fails(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, _trace_with(_accepted("dd_without_ut:DD-099")))
    result, _ = _run(repo, "--mode", "pr", "--base", "main", "--now", "2026-11-01T00:00:00+00:00")
    assert result.returncode == 1
    assert "accepted gap dd_without_ut:DD-099 does not exist" in result.stderr


@pytest.mark.parametrize("entry", ['- {gap: "dd_without_ut:DD-002", expires: 2026-12-31}',
                                   '- {gap: "dd_without_ut:DD-002", reason: "r"}',
                                   '- {gap: "dd_without_ut:DD-002", reason: "r", expires: "soon"}'])
def test_accepted_gap_without_reason_or_valid_expiry_fails(tmp_path: Path, entry: str) -> None:
    repo = _repo(tmp_path)
    files, _ = NEW_GAPS["DD without UT"]
    _commit(repo, {**files, **_trace_with(f"accepted_gaps:\n{entry}\n")})
    result, _ = _run(repo, "--mode", "pr", "--base", "main", "--now", "2026-11-01T00:00:00+00:00")
    assert result.returncode == 1
    assert "accepted_gaps: needs gap, reason and expires" in result.stderr


def test_closing_a_gap_passes_and_an_old_gap_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path, _arch("## ARCH-002 Old\n\nType: Component\nSatisfies: REQ-T-A1\n## ARCH-003 Kept\n\nType: Component\nSatisfies: REQ-T-A1\n"))
    _commit(repo, {"docs/architecture.md": BASE_FILES["docs/architecture.md"]
                   + "\n## ARCH-002 Old\n\nType: Component\nSatisfies: REQ-T-A1\nImplemented by: `Makefile`\n"
                   + "## ARCH-003 Kept\n\nType: Component\nSatisfies: REQ-T-A1\n"})
    result, report = _run(repo, "--mode", "pr", "--base", "main")
    assert result.returncode == 0, result.stderr
    assert report["gap_gate"]["new_gaps"] == []
    assert report["coverage_gaps"]["architecture_without_implementation"] == ["ARCH-003"]


def test_push_mode_reports_a_new_gap_and_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    files, _ = NEW_GAPS["DD without UT"]
    _commit(repo, files)
    result, report = _run(repo, "--mode", "push")
    assert result.returncode == 0, result.stderr
    assert report["coverage_gaps"]["dd_without_ut"] == ["DD-002"]


def test_pr_mode_needs_an_explicit_mode_and_a_base(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    no_mode, _ = _run(repo)
    no_base, _ = _run(repo, "--mode", "pr")
    assert no_mode.returncode == 2 and "--mode" in no_mode.stderr
    assert no_base.returncode == 1 and "--mode pr needs --base" in no_base.stderr


def test_unresolvable_base_fails_and_never_falls_back(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result, _ = _run(repo, "--mode", "pr", "--base", "origin/nope")
    assert result.returncode == 2
    assert "cannot resolve the merge-base" in result.stderr


def test_unreadable_base_trace_inputs_fail(tmp_path: Path) -> None:
    repo = _repo(tmp_path, {"docs/requirements.md": "no requirements here\n"})
    _commit(repo, {"docs/requirements.md": BASE_FILES["docs/requirements.md"]})
    result, _ = _run(repo, "--mode", "pr", "--base", "main")
    assert result.returncode == 2
    assert "cannot read the trace inputs of the merge-base" in result.stderr


def test_base_is_the_merge_base_not_the_tip_of_main(tmp_path: Path) -> None:
    """main closes an old gap after the branch started; the branch still has it, which is not new."""
    repo = _repo(tmp_path, _arch("## ARCH-002 Old\n\nType: Component\nSatisfies: REQ-T-A1\n"))
    _commit(repo, {"harness.sh": BASE_FILES["harness.sh"] + "# branch work\n"})
    _git(repo, "checkout", "-q", "main")
    _commit(repo, {"docs/architecture.md": BASE_FILES["docs/architecture.md"]
                   + "\n## ARCH-002 Old\n\nType: Component\nSatisfies: REQ-T-A1\nImplemented by: `Makefile`\n"},
            branch=None)
    _git(repo, "checkout", "-q", "feature")
    result, report = _run(repo, "--mode", "pr", "--base", "main")
    assert result.returncode == 0, result.stderr
    assert report["gap_gate"]["new_gaps"] == []


# --- V11 retirement ----------------------------------------------------------------

def test_reusing_a_retired_id_fails(tmp_path: Path) -> None:
    files = _trace_with('retired_ids:\n- {id: DD-001, reason: "retired in slice X"}\naccepted_gaps: []\n')
    result, _ = _run(_repo(tmp_path, files), "--mode", "push")
    assert result.returncode == 1
    assert "DD-001: retired id reused (retired in slice X)" in result.stderr


def test_repository_retired_the_deploy_dds_and_integration_cases() -> None:
    text = (ROOT / "scripts" / "qa_deploy.py").read_text(encoding="utf-8")
    trace = (ROOT / "trace" / "tests.yaml").read_text(encoding="utf-8")
    for n in range(925, 931):
        assert f"# DD: DD-{n}" not in text
        assert f"{{id: DD-{n}, reason:" in trace
    assert "- id: IT-DEPLOY-" not in trace
    assert trace.count("{id: IT-DEPLOY-") == 6


# --- V12 replay of the slice 1B miss -------------------------------------------------

def _tree(commit: str, dest: Path) -> None:
    dest.mkdir()
    archive = subprocess.run(["git", "archive", "--format=tar", commit], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)


def test_gap_gate_replay_of_1b_fails_on_the_ten_new_req_sec_gaps(tmp_path: Path) -> None:
    for commit in ("8faeea9", "0dbd27b"):
        if subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT).returncode != 0:
            pytest.fail(f"commit {commit} not in history (CI needs fetch-depth: 0)")
    repo = tmp_path / "repo"
    _tree("8faeea9", repo)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "1B base")
    _git(repo, "checkout", "-q", "-b", "feature")
    shutil.rmtree(tmp_path / "head", ignore_errors=True)
    _tree("0dbd27b", tmp_path / "head")
    for item in repo.iterdir():
        if item.name != ".git":
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    for item in (tmp_path / "head").iterdir():
        shutil.move(str(item), repo / item.name)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "1B head")
    result, report = _run(repo, "--mode", "pr", "--base", "main")
    assert result.returncode == 1
    new = set(report["gap_gate"]["new_gaps"])
    expected = {f"requirements_without_proof:REQ-SEC-{r}" for r in
                ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "D1", "D2")}
    assert expected <= new, sorted(new)


# --- review round 1 (B1-B1, B1-B2, B1-A2) ----------------------------------------

def test_register_without_assets_mapping_fails_closed(tmp_path: Path) -> None:
    register = BASE_FILES["security/invariants.yaml"].split("services:")[0].replace("assets:", "inventory:")
    register += "services:\n  issuer:\n    root: forbidden\nknown_violations:\n  - {opl: OPL-005, asset: K1, services: [x], expires: 2026-12-31}\n"
    result, _ = _run(_repo(tmp_path, {"security/invariants.yaml": register}), "--mode", "push")
    assert result.returncode == 2
    assert "'assets' must be a dict" in result.stderr


def test_known_violation_row_naming_no_register_asset_fails(tmp_path: Path) -> None:
    register = BASE_FILES["security/invariants.yaml"].replace(
        "known_violations: []\n", "known_violations:\n  - {opl: OPL-005, asset: K9, services: [x], expires: 2026-12-31}\n")
    result, _ = _run(_repo(tmp_path, {"security/invariants.yaml": register}), "--mode", "push")
    assert result.returncode == 1
    assert "names no register asset with a requirement" in result.stderr


def test_missing_register_with_static_tests_fails(tmp_path: Path) -> None:
    result, _ = _run(_repo(tmp_path, {"security/invariants.yaml": None}), "--mode", "push")
    assert result.returncode == 1
    assert "security/invariants.yaml is missing, but static tests take their status from it" in result.stderr


@pytest.mark.parametrize(("entry", "message"), [
    (_accepted("dd_without_ut:DD-001", expires="2026-10-30"), "expired on 2026-10-30"),
    (_accepted("dd_without_ut:DD-099"), "does not exist"),
])
def test_push_mode_fails_on_an_expired_or_stale_acceptance(tmp_path: Path, entry: str, message: str) -> None:
    files = {"tests/unit/test_alpha.py": "", **_trace_with(entry)}
    result, _ = _run(_repo(tmp_path, files), "--mode", "push", "--now", "2026-11-01T00:00:00+00:00")
    assert result.returncode == 1
    assert message in result.stderr


def test_a_run_report_cannot_change_a_status(tmp_path: Path) -> None:
    """qa-trace never reads run reports: a report claiming success leaves a known violation unproved."""
    register = BASE_FILES["security/invariants.yaml"].replace(
        "known_violations: []\n", "known_violations:\n  - {opl: OPL-005, asset: K1, services: [x], expires: 2026-12-31}\n")
    claim = json.dumps({"verdict": "passed", "status": {"REQ-SEC-K1": "proved"}, "known_violations": []})
    files = {"security/invariants.yaml": register, "artifacts/quality/qa_deploy_report.json": claim}
    result, report = _run(_repo(tmp_path, files), "--mode", "push")
    assert result.returncode == 0, result.stderr
    assert report["requirements"]["REQ-SEC-K1"]["status"] == "not proved: known violation OPL-005"


def test_register_asset_naming_an_unknown_requirement_fails(tmp_path: Path) -> None:
    """Round 2 (B1-B1): a typo in an asset's requirement must not let its known violation vanish."""
    register = BASE_FILES["security/invariants.yaml"].replace("requirement: REQ-SEC-K1", "requirement: REQ-SEC-K9").replace(
        "known_violations: []\n", "known_violations:\n  - {opl: OPL-005, asset: K1, services: [x], expires: 2026-12-31}\n")
    result, _ = _run(_repo(tmp_path, {"security/invariants.yaml": register}), "--mode", "push")
    assert result.returncode == 1
    assert "register asset K1 names unknown requirement 'REQ-SEC-K9'" in result.stderr
