"""Negative controls for scripts/test_lint.py (test plan T-7, T-22): loose outcome checks are caught."""

from __future__ import annotations

import importlib.util
import subprocess  # nosec B404 - fixed git and script argv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "test_lint.py"
_spec = importlib.util.spec_from_file_location("harness_test_lint", SCRIPT)
assert _spec and _spec.loader
test_lint = importlib.util.module_from_spec(_spec)
sys.modules["harness_test_lint"] = test_lint
_spec.loader.exec_module(test_lint)

# Loose checks the 1A table lists, plus those the lint found on the same harness (test_plan.md 1A).
BASELINE_COMMIT = "20c074e"
BASELINE_FLAGGED = {
    "M1-T1", "M1-T2", "M1-T3", "M2.5-T1", "M3.S2-T3", "M3.S2-T4", "M3.S2-T5",
    "M3.S4-T1", "M3.S4-T3", "M3.S4-T4", "M3.S4-T5", "M4-T5", "M4-T6", "M5-T21",
    "M2-T3", "M2-T5", "M2-T6", "M2-T7", "M5-T4", "M5-T24", "M5-T26", "M5-T28", "M5-T46",
}


def _harness(guard: str, extra: str = "") -> str:
    """One test with a positive guard plus the guard under test."""
    return (
        'T_test() {\n'
        '  begin_test_evidence "M9-T1" "fixture"\n'
        '  outcome_guard "status exact" "assert_file_eq \\"$EVDIR/status.txt\\" \\"403\\""\n'
        f"{extra}"
        f"  outcome_guard \"under test\" {guard}\n"
        "}\n"
    )


def _rules(text: str) -> list[str]:
    return [finding.rule for finding in test_lint.lint(text)]


@pytest.mark.parametrize(
    ("guard", "rule"),
    [
        ('"grep -q ok \\"$f\\" || true"', "or-true"),
        ('"[ \\"\\$(cat \\"$EVDIR/rc.txt\\")\\" != \\"0\\" ]"', "exit-code-only"),
        ('"rc=\\$(cat \\"$EVDIR/rc.txt\\"); [ \\"\\$rc\\" -ne 0 ]"', "exit-code-only"),
        ('"assert_file_any \\"$EVDIR/status.txt\\" \\"401\\" \\"403\\""', "any-of"),
        ("\"grep -Eq '(error|fail)' \\\"$f\\\"\"", "broad-regex"),
        ("\"grep -Eq 'error|fail' \\\"$f\\\"\"", "broad-regex"),
        ("\"grep -Eq '(Connection refused|timed out|No route to host)' \\\"$f\\\"\"", "broad-regex"),
        ('"[ \\"\\$status\\" != \\"200\\" ]"', "not-200"),
    ],
)
def test_each_loose_pattern_is_flagged(guard: str, rule: str) -> None:
    assert rule in _rules(_harness(guard))


def test_negative_grep_as_only_check_is_flagged() -> None:
    text = (
        'T_test() {\n'
        '  begin_test_evidence "M9-T2" "fixture"\n'
        "  outcome_guard \"no secret\" \"! grep -Eq 'Bearer' \\\"$EVDIR/out.json\\\"\"\n"
        "}\n"
    )
    assert _rules(text) == ["negative-only"]


def test_negative_grep_next_to_a_positive_check_passes() -> None:
    guard = "\"! grep -Eq 'Bearer' \\\"$EVDIR/out.json\\\"\""
    assert _rules(_harness(guard)) == []


def test_or_true_inside_command_substitution_passes() -> None:
    guard = '"s=\\"\\$(cat \\"$EVDIR/status.txt\\" 2>/dev/null || true)\\"; [ \\"\\$s\\" = \\"403\\" ]"'
    assert _rules(_harness(guard)) == []


def test_or_true_in_exercise_plumbing_passes() -> None:
    extra = '  exercise_guard "call" "curl -sS http://x >\\"$EVDIR/out\\" || true"\n'
    assert _rules(_harness('"grep -Fq ok \\"$EVDIR/out\\""', extra)) == []


def test_exit_code_with_exact_message_passes() -> None:
    guard = "\"[ \\\"\\$(cat \\\"$EVDIR/rc.txt\\\")\\\" = \\\"28\\\" ] && grep -Fq 'Connection timed out' \\\"$f\\\"\""
    assert _rules(_harness(guard)) == []


def test_declared_alternate_exempts_multi_outcome_only() -> None:
    extra = "  # test-lint: alternate: path is absent or unreadable, both mean confined\n"
    alt = "\"grep -Eq '(No such file|Permission denied|not found)' \\\"$f\\\"\""
    assert _rules(_harness(alt, extra)) == []
    assert _rules(_harness('"cmd || true"', extra)) == ["or-true"]


def test_declared_alternate_without_reason_is_flagged() -> None:
    extra = "  # test-lint: alternate:\n"
    alt = '"assert_file_any \\"$EVDIR/status.txt\\" \\"401\\" \\"403\\""'
    assert set(_rules(_harness(alt, extra))) == {"any-of", "alternate-without-reason"}


def test_multiline_guard_is_joined() -> None:
    guard = '\\\n    "assert_file_any \\"$EVDIR/status.txt\\" \\"401\\" \\"403\\""'
    assert "any-of" in _rules(_harness(guard))


def test_unparseable_guard_is_flagged() -> None:
    assert "unparsed" in _rules(_harness("$dynamic_guard"))


def test_cli_exit_codes(tmp_path: Path) -> None:
    loose = tmp_path / "loose.sh"
    loose.write_text(_harness('"assert_file_any \\"$f\\" \\"401\\" \\"403\\""'), encoding="utf-8")
    clean = tmp_path / "clean.sh"
    clean.write_text(_harness('"grep -Fq ok \\"$f\\""'), encoding="utf-8")
    run = [sys.executable, str(SCRIPT), "--harness"]
    bad = subprocess.run([*run, str(loose)], capture_output=True, text=True, check=False)  # nosec B603
    good = subprocess.run([*run, str(clean)], capture_output=True, text=True, check=False)  # nosec B603
    assert bad.returncode == 1 and "M9-T1" in bad.stdout and "any-of" in bad.stdout
    assert good.returncode == 0


def test_baseline_harness_flags_every_known_loose_check() -> None:
    text = subprocess.run(  # nosec B603 B607 - fixed git argv
        ["git", "-C", str(ROOT), "show", f"{BASELINE_COMMIT}:scripts/rogue_node_tests.sh"],
        capture_output=True, text=True, check=True,
    ).stdout
    flagged = {finding.test_id for finding in test_lint.lint(text)}
    assert flagged == BASELINE_FLAGGED


def test_current_harness_is_clean() -> None:
    text = (ROOT / "scripts" / "rogue_node_tests.sh").read_text(encoding="utf-8")
    assert [str(finding) for finding in test_lint.lint(text)] == []
