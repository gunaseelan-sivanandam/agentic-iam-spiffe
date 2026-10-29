"""Negative controls for scripts/mutation_gate.py (test plan T-41): untested mutants cannot hide."""

from __future__ import annotations

import json
import subprocess  # nosec B404 - fixed argv to the gate script
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "mutation_gate.py"


def _gate(tmp_path: Path, stats: dict[str, int], min_score: str = "70") -> subprocess.CompletedProcess[str]:
    path = tmp_path / "stats.json"
    path.write_text(json.dumps(stats), encoding="utf-8")
    return subprocess.run(  # nosec B603 - fixed argv
        [sys.executable, str(SCRIPT), "--stats", str(path), "--min-score", min_score],
        capture_output=True,
        text=True,
        check=False,
    )


def test_untested_mutants_count_as_not_killed(tmp_path: Path) -> None:
    # The old rule dropped no_tests from the denominator and scored this 100%.
    result = _gate(tmp_path, {"total": 100, "killed": 1, "no_tests": 99})
    assert result.returncode == 1
    assert "score=1.00%" in result.stderr


def test_skipped_mutants_count_as_not_killed(tmp_path: Path) -> None:
    result = _gate(tmp_path, {"total": 100, "killed": 60, "skipped": 40})
    assert result.returncode == 1
    assert "score=60.00%" in result.stderr


def test_empty_run_fails(tmp_path: Path) -> None:
    result = _gate(tmp_path, {"total": 0, "killed": 0})
    assert result.returncode == 2
    assert "no mutants" in result.stderr


def test_missing_stats_file_is_an_error(tmp_path: Path) -> None:
    result = subprocess.run(  # nosec B603 - fixed argv
        [sys.executable, str(SCRIPT), "--stats", str(tmp_path / "absent.json")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "missing stats file" in result.stderr


def test_score_at_threshold_passes(tmp_path: Path) -> None:
    result = _gate(tmp_path, {"total": 10000, "killed": 7000, "no_tests": 500})
    assert result.returncode == 0
    assert "score=70.00%" in result.stdout


def test_score_just_below_threshold_fails(tmp_path: Path) -> None:
    result = _gate(tmp_path, {"total": 10000, "killed": 6999})
    assert result.returncode == 1
    assert "score=69.99%" in result.stderr
