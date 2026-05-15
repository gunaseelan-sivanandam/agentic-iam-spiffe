from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit.shared.loaders import REPO_ROOT


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


@pytest.mark.boundary
@pytest.mark.parametrize(
    ("aud", "res", "expected"),
    [
        ("tool-b", "tool-b:/search", "tool-b:/search"),
        ("tool-b", "/search", "tool-b:/search"),
        ("tool-b", "tool-b:/secret", "tool-b:/secret"),
        ("tool-b", "/secret", "tool-b:/secret"),
        ("tool-b", "tool-b:/read-file:fileA", "tool-b:/read-file:fileA"),
        ("tool-b", "tool-b:/read-file:file A", None),
        ("tool-b", "tool-b:/read-file:file/A", None),
        ("tool-b", "tool-b:/read-file:*", None),
        ("tool-b", "tool-b:/read-file:file?", None),
        ("tool-b", "tool-b:/all", None),
        ("tool-x", "tool-b:/search", None),
        ("tool-b", "search", None),
    ],
)
# UT: UT-001
# Test Description: Verifies canonicalize resource across the parameterized matrix covered by this test.
# Precondition: Module fixtures are loaded and the parameterized case input is available for the current test iteration.
# Expected Output: Each parameterized case produces the expected result asserted by the outcome guards.
# Covers DD: DD-101
def test_canonicalize_resource_matrix(capiss_module, guard, aud: str, res: str, expected: str | None):
    _premise_module_loaded(guard, capiss_module)
    out = guard.exercise(
        "canonicalize resource",
        lambda: capiss_module.canonicalize_resource(aud, res),
    )
    guard.outcome("canonical result matches expected", out == expected)


# UT: UT-002
# Test Description: Verifies that canonicalize resource rejects wildcards.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-101
@pytest.mark.invariant
def test_canonicalize_resource_rejects_wildcards(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    results = guard.exercise(
        "canonicalize wildcard-like resources",
        lambda: [
            capiss_module.canonicalize_resource("tool-b", wildcard_like)
            for wildcard_like in (
                "tool-b:/read-file:*",
                "tool-b:/read-file:[a-z]",
                "tool-b:/read-file:file?",
            )
        ],
    )
    guard.outcome("all wildcard-like resources rejected", all(item is None for item in results))


@pytest.mark.boundary
@pytest.mark.parametrize(
    ("res", "expected"),
    [
        ("jira-tool:/project:IAM", "jira-tool:/project:IAM"),
        ("jira-tool:/project:NAS", "jira-tool:/project:NAS"),
        ("jira-tool:/project:iam", None),
        ("jira-tool:/project:IAM*", None),
        ("jira-tool:/project:IAM,NAS", None),
        ("jira-tool:/project:", None),
        ("jira-tool:/issue:IAM-1", None),
        ("/project:IAM", None),
    ],
)
# UT: UT-158
# Test Description: Verifies Jira project resource canonicalization accepts only strict canonical project resources.
# Precondition: capiss module is loaded and a Jira resource candidate is provided by the parameterized case.
# Expected Output: The canonicalization result equals the expected canonical string or denial.
# Covers DD: DD-126, DD-101
def test_canonicalize_jira_project_resource_matrix(capiss_module, guard, res: str, expected: str | None):
    _premise_module_loaded(guard, capiss_module)
    out = guard.exercise(
        "canonicalize jira project resource",
        lambda: capiss_module.canonicalize_resource("jira-tool", res),
    )
    guard.outcome("canonical result matches expected", out == expected)


# UT: UT-159
# Test Description: Verifies OPA Jira policy source checks the full root-mint tuple.
# Precondition: The OPA policy source is available in the repository.
# Expected Output: The Jira allow rules contain caller, audience, read/write actions, and resource constraints for IAM only.
# Covers DD: DD-127, DD-128
@pytest.mark.invariant
def test_opa_jira_allow_rule_contains_full_tuple(guard):
    policy_path = Path(REPO_ROOT, "services", "opa", "policy.rego")
    guard.premise("opa policy exists", policy_path.exists())
    policy = guard.exercise("read opa policy", lambda: policy_path.read_text(encoding="utf-8"))
    guard.outcome("policy constrains caller", 'input.sub == "spiffe://example.org/agent-a"' in policy)
    guard.outcome("policy constrains jira audience", 'input.aud == "jira-tool"' in policy)
    guard.outcome("policy constrains read action", 'input.act == "read"' in policy)
    guard.outcome("policy constrains write action", 'input.act == "write"' in policy)
    guard.outcome("policy constrains IAM project resource", 'input.res == "jira-tool:/project:IAM"' in policy)
