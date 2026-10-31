"""qa-evidence accepts the qa-deploy report only if it passed, inspected image users and matches the
compose file and register on disk (slice ci-evidence-trace, test plan V6)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess  # nosec B404 - fixed argv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("validate_e2e_evidence", ROOT / "scripts" / "validate_e2e_evidence.py")
assert _spec and _spec.loader
ve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ve)


def _files(tmp_path: Path, **overrides: object) -> tuple[Path, Path, Path]:
    compose, register = tmp_path / "compose.yml", tmp_path / "register.yaml"
    compose.write_text("services: {}\n")
    register.write_text("assets: {}\n")
    report = {"verdict": "passed", "problems": [], "known_violations": [], "warnings": [],
              "image_users_inspected": True,
              "compose_sha256": hashlib.sha256(compose.read_bytes()).hexdigest(),
              "register_sha256": hashlib.sha256(register.read_bytes()).hexdigest()}
    report.update(overrides)
    path = tmp_path / "qa_deploy_report.json"
    path.write_text(json.dumps(report))
    return path, compose, register


def test_passing_inspected_matching_report_is_accepted(tmp_path: Path) -> None:
    assert ve.deploy_report_failures(*_files(tmp_path)) == []


@pytest.mark.parametrize(("overrides", "message"), [
    ({"verdict": "failed"}, "verdict is 'failed'"),
    ({"verdict": "error"}, "verdict is 'error'"),
    ({"image_users_inspected": False}, "did not inspect image users"),
    ({"compose_sha256": "0" * 64}, "another compose file"),
    ({"register_sha256": "0" * 64}, "another register file"),
])
def test_report_that_failed_skipped_inspection_or_is_stale_fails(tmp_path: Path, overrides: dict, message: str) -> None:
    failures = ve.deploy_report_failures(*_files(tmp_path, **overrides))
    assert any(message in f for f in failures), failures


def test_missing_unreadable_or_malformed_report_fails(tmp_path: Path) -> None:
    path, compose, register = _files(tmp_path)
    path.unlink()
    assert "missing or unreadable" in ve.deploy_report_failures(path, compose, register)[0]
    path.write_text("{not json")
    assert "missing or unreadable" in ve.deploy_report_failures(path, compose, register)[0]
    path.write_text("[]")
    assert "not a JSON object" in ve.deploy_report_failures(path, compose, register)[0]


def test_changed_register_after_the_run_makes_the_report_stale(tmp_path: Path) -> None:
    path, compose, register = _files(tmp_path)
    register.write_text("assets: {K1: {}}\n")
    assert any("another register file" in f for f in ve.deploy_report_failures(path, compose, register))


def test_makefile_qa_evidence_checks_the_deploy_report() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "--deploy-report artifacts/quality/qa_deploy_report.json" in makefile
    out = subprocess.run(["make", "-n", "qa-evidence"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert "--deploy-report artifacts/quality/qa_deploy_report.json" in out


@pytest.mark.skipif(sys.platform == "win32" or __import__("os").geteuid() == 0, reason="root reads files regardless of mode")
def test_unreadable_report_fails(tmp_path: Path) -> None:
    path, compose, register = _files(tmp_path)
    path.chmod(0)
    try:
        failures = ve.deploy_report_failures(path, compose, register)
    finally:
        path.chmod(0o600)
    assert "missing or unreadable" in failures[0]


def test_failed_report_fails_qa_evidence_through_its_exit_code(tmp_path: Path) -> None:
    """End to end through the validator's exit: a minimal passing run, with a failed deploy report."""
    (tmp_path / "trace").mkdir()
    (tmp_path / "trace" / "tests.yaml").write_text(
        "tests:\n  - id: E2E-SUITE-X\n    type: e2e_suite\n    evidence_prefixes: [M1-T1]\n")
    evdir = tmp_path / "artifacts" / "rogue-tests" / "M1-T1_case"
    evdir.mkdir(parents=True)
    for name in ("premise_1.txt", "exercise_1.txt", "outcome_1.txt", "cmd_premise_1.txt"):
        (evdir / name).write_text("ok\n")
    (tmp_path / "test_report.log").write_text(
        "EVIDENCE_DIR=/tmp/rogue-tests/M1-T1_case\n[T1] case .... PASS\nTotal: 1  Passed: 1  Failed: 0\n")
    report, compose, register = _files(tmp_path, verdict="failed")
    cmd = [sys.executable, str(ROOT / "scripts" / "validate_e2e_evidence.py"), "--tests", "trace/tests.yaml",
           "--evidence-dir", "artifacts/rogue-tests", "--test-report", "test_report.log",
           "--report-json", "artifacts/quality/evidence_report.json", "--deploy-report", str(report),
           "--compose", str(compose), "--register", str(register)]
    result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True, check=False)
    assert result.returncode == 1 and "verdict is 'failed'" in result.stderr
    report.write_text(report.read_text().replace('"failed"', '"passed"'))
    assert subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True, check=False).returncode == 0
