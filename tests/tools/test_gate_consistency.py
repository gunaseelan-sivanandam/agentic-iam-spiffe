"""Negative controls for scripts/check_gate_consistency.py (slice ci-evidence-trace, test plan V10):
the AGENTS.md CI gates, the CI jobs (and the command each runs) and the required checks must agree.
Slice agent-identity (test plan V1): the main ruleset must also require an approving review."""

from __future__ import annotations

import importlib.util
import json
import subprocess  # nosec B404 - fixed argv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_gate_consistency.py"
_spec = importlib.util.spec_from_file_location("check_gate_consistency", SCRIPT)
assert _spec and _spec.loader
gc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gc)

AGENTS = """## Quality gates

| Gate | Command | Enforced by | Threshold |
| --- | --- | --- | --- |
| Trace | `make qa-trace` | CI, every push/PR | x |
| Deploy | `make qa-deploy` | CI (without image inspection) | x |
| Evidence | `make qa-evidence` | in the CI `e2e` job; local | x |
| Local only | `make local-thing` | local, required in step 4 | x |

## Next section
"""
WORKFLOW = """jobs:
  qa-trace:
    steps:
      - uses: actions/checkout@v6
      - run: make qa-trace QA_TRACE_ARGS="--mode push"
  qa-deploy:
    steps:
      - run: make qa-deploy QA_DEPLOY_ARGS=--skip-image-users
"""


def _ruleset(*checks: str, approvals: int | None = 1) -> dict:
    rules: list[dict] = [{"type": "deletion"},
                         {"type": "required_status_checks",
                          "parameters": {"required_status_checks": [{"context": c} for c in checks]}}]
    if approvals is not None:
        rules.append({"type": "pull_request", "parameters": {"required_approving_review_count": approvals}})
    return {"rules": rules}


RULESET = _ruleset("qa-trace", "qa-deploy")


def test_agreeing_lists_pass() -> None:
    assert gc.ci_gates(AGENTS) == ["qa-trace", "qa-deploy"]
    assert gc.check(AGENTS, WORKFLOW, RULESET) == []


def test_ci_gate_without_job_fails() -> None:
    agents = AGENTS.replace("| Local only | `make local-thing` | local", "| Lint | `make test-lint` | CI")
    assert gc.check(agents, WORKFLOW, RULESET) == ["gate test-lint is enforced by CI in AGENTS.md but has no CI job"]


def test_job_without_row_fails() -> None:
    workflow = WORKFLOW + "  docs-check:\n    steps:\n      - run: make docs-check\n"
    problems = gc.check(AGENTS, workflow, _ruleset("qa-trace", "qa-deploy", "docs-check"))
    assert problems == ["CI job docs-check has no row enforced by CI in the AGENTS.md quality gates"]


def test_job_that_is_not_a_required_check_fails() -> None:
    assert gc.check(AGENTS, WORKFLOW, _ruleset("qa-trace")) == ["CI job qa-deploy is not a required check of the main ruleset"]


def test_required_check_without_job_fails() -> None:
    problems = gc.check(AGENTS, WORKFLOW, _ruleset("qa-trace", "qa-deploy", "old-gate"))
    assert problems == ["required check old-gate is not a CI job"]


def test_job_running_another_target_fails() -> None:
    workflow = WORKFLOW.replace("make qa-deploy QA_DEPLOY_ARGS=--skip-image-users", "make docs-check")
    assert gc.check(AGENTS, workflow, RULESET) == ["CI job qa-deploy does not run `make qa-deploy`"]


def test_target_prefix_is_not_its_own_target() -> None:
    workflow = WORKFLOW.replace("make qa-deploy QA_DEPLOY_ARGS=--skip-image-users", "make qa-deploy-extra")
    assert gc.check(AGENTS, workflow, RULESET) == ["CI job qa-deploy does not run `make qa-deploy`"]


@pytest.mark.parametrize("approvals", [None, 0])
def test_ruleset_without_a_required_approval_fails(approvals: int | None) -> None:
    ruleset = _ruleset("qa-trace", "qa-deploy", approvals=approvals)
    assert gc.check(AGENTS, WORKFLOW, ruleset) == ["the main ruleset does not require an approving review"]


def test_pull_request_rule_without_parameters_fails() -> None:
    ruleset = _ruleset("qa-trace", "qa-deploy", approvals=None)
    ruleset["rules"].append({"type": "pull_request"})
    assert gc.check(AGENTS, WORKFLOW, ruleset) == ["the main ruleset does not require an approving review"]


@pytest.mark.parametrize("content", ["{not json", "[]", json.dumps({"rules": "x"})])
def test_unreadable_or_unparsable_ruleset_fails_closed(tmp_path: Path, content: str) -> None:
    (tmp_path / "AGENTS.md").write_text(AGENTS)
    (tmp_path / "ci.yml").write_text(WORKFLOW)
    (tmp_path / "ruleset.json").write_text(content)
    result = subprocess.run([sys.executable, str(SCRIPT), "--agents", str(tmp_path / "AGENTS.md"),
                             "--workflow", str(tmp_path / "ci.yml"), "--ruleset-json", str(tmp_path / "ruleset.json")],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2 and "FAILED" in result.stderr


def test_missing_ruleset_source_fails_closed() -> None:
    with pytest.raises(ValueError):
        gc.load_ruleset(None, None)


def test_repository_table_and_workflow_agree_with_the_planned_required_checks() -> None:
    """Positive control: today's AGENTS.md and ci.yml with the required checks after this slice."""
    planned = _ruleset("docs-check", "e2e", "gate-consistency", "qa-deploy", "qa-trace", "test-lint",
                       "tooling-test", "unit-diff-cov", "unit-guard-check", "unit-mutation", "unit-trust")
    problems = gc.check((ROOT / "AGENTS.md").read_text(encoding="utf-8"),
                        (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"), planned)
    assert problems == []
