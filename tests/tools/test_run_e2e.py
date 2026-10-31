"""Tests for `make e2e` (scripts/run_e2e.sh; slice ci-evidence-trace, test plan V1).

A stub `docker` on PATH stands in for the stack: the suite's exit code and the ownership step's
result are injected, so these tests start no container.
"""

from __future__ import annotations

import os
import subprocess  # nosec B404 - fixed argv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

STUB = """#!/usr/bin/env bash
echo "$*" >> "$STUB_LOG"
case "$*" in
  *" build"*) exit "${STUB_BUILD_RC:-0}" ;;
  *" up "*) exit "${STUB_SUITE_RC:-0}" ;;
  run*rm\ -rf*) exit "${STUB_RESET_RC:-0}" ;;
  run*chown\ -R*) exit "${STUB_CHOWN_RC:-0}" ;;
esac
exit 0
"""


def _run(tmp_path: Path, **rcs: int) -> tuple[subprocess.CompletedProcess, list[str]]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "docker").write_text(STUB)
    (bin_dir / "docker").chmod(0o755)
    log = tmp_path / "docker.log"
    env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}", STUB_LOG=str(log),
               **{f"STUB_{k.upper()}_RC": str(v) for k, v in rcs.items()})
    result = subprocess.run(["make", "-s", "e2e"], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    calls = log.read_text().splitlines() if log.exists() else []
    return result, calls


def test_e2e_builds_runs_the_suite_and_takes_ownership(tmp_path: Path) -> None:
    result, calls = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    reset = calls[0]
    assert reset.startswith("run --rm -v") and "rm -rf /repo/test_report.log /repo/artifacts/rogue-tests" in reset
    assert "build" in calls[1] and "--profile tests" in calls[1]
    assert "--exit-code-from rogue-tests rogue-tests" in calls[2]
    chown = calls[3]
    assert chown.startswith("run --rm -v") and f"chown -R {os.getuid()}:{os.getgid()}" in chown
    assert "/repo/artifacts" in chown and "/repo/test_report.log" in chown


def test_failed_suite_fails_the_target(tmp_path: Path) -> None:
    result, calls = _run(tmp_path, suite=1)
    assert result.returncode != 0
    assert any("chown -R" in call for call in calls), "ownership is taken even when the suite fails"
    assert "suite exit code: 1" in result.stdout


@pytest.mark.parametrize(("rcs", "message"), [
    ({"reset": 1}, "could not remove the previous run's report"),
    ({"build": 1}, "image build"),
    ({"chown": 1}, "could not take ownership"),
])
def test_failed_build_or_ownership_fails_the_target(tmp_path: Path, rcs: dict[str, int], message: str) -> None:
    result, _ = _run(tmp_path, **rcs)
    assert result.returncode != 0
    assert message in result.stderr
