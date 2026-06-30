from __future__ import annotations

import json

import pytest


M5_SUMMARY_BODY = {
    "aud": "jira-mcp-gateway",
    "act": "read_project_summary",
    "res": "jira-mcp:/project:IAM",
}
M5_CREATE_BODY = {
    "aud": "jira-mcp-gateway",
    "act": "create_story",
    "res": "jira-mcp:/project:IAM",
}


def _json_body(response) -> dict:
    return json.loads(response.body.decode("utf-8"))


# UT: UT-190
# Test Description: Verifies capiss canonicalizes only strict Jira MCP project resources.
# Precondition: capiss module is loaded and M5 resource candidates include valid and malformed forms.
# Expected Output: Strict IAM/NAS resources canonicalize and malformed or mixed authority resources are rejected.
# Covers DD: DD-129, DD-101
@pytest.mark.boundary
def test_canonicalize_jira_mcp_project_resource_matrix(capiss_module, guard):
    guard.premise("capiss module loaded", capiss_module is not None)
    results = guard.exercise(
        "canonicalize M5 resources",
        lambda: {
            "iam": capiss_module.canonicalize_resource("jira-mcp-gateway", "jira-mcp:/project:IAM"),
            "nas": capiss_module.canonicalize_resource("jira-mcp-gateway", "jira-mcp:/project:NAS"),
            "lower": capiss_module.canonicalize_resource("jira-mcp-gateway", "jira-mcp:/project:iam"),
            "slash": capiss_module.canonicalize_resource("jira-mcp-gateway", "jira-mcp:/project:IAM/1"),
            "mixed": capiss_module.canonicalize_resource("jira-tool", "jira-mcp:/project:IAM"),
        },
    )
    guard.outcome("IAM canonicalized", results["iam"] == "jira-mcp:/project:IAM")
    guard.outcome("NAS syntactically canonicalized", results["nas"] == "jira-mcp:/project:NAS")
    guard.outcome("lowercase rejected", results["lower"] is None)
    guard.outcome("slash rejected", results["slash"] is None)
    guard.outcome("mixed authority rejected", results["mixed"] is None)


# UT: UT-191
# Test Description: Verifies capiss sends allowed M5 summary and create tuples to policy and mints them.
# Precondition: capiss module is loaded and policy/store dependencies are stubbed to allow M5 IAM tuples.
# Expected Output: M5 summary and create root mints succeed with the distinct M5 audience and resource family.
# Covers DD: DD-104, DD-125, DD-129, DD-130, DD-131
@pytest.mark.invariant
def test_root_mint_jira_mcp_allowed_tuples(capiss_module, monkeypatch, guard):
    guard.premise("capiss module loaded", capiss_module is not None)
    captured: list[dict[str, object]] = []
    guard.exercise("stub opa allow", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda payload: captured.append(payload) or (True, None)))
    guard.exercise("stub budget init", lambda: monkeypatch.setattr(capiss_module, "ensure_root_budget", lambda *_: (True, "")))
    guard.exercise("stub mint marker", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    summary = guard.exercise(
        "mint M5 summary token",
        lambda: capiss_module.root_mint(payload=M5_SUMMARY_BODY, x_spiffe_id="spiffe://varambu.org/codex-jira-mcp-adapter"),
    )
    create = guard.exercise(
        "mint M5 create token",
        lambda: capiss_module.root_mint(payload=M5_CREATE_BODY, x_spiffe_id="spiffe://varambu.org/codex-jira-mcp-adapter"),
    )
    guard.outcome("summary mint uses M5 audience", summary["aud"] == "jira-mcp-gateway")
    guard.outcome("summary mint uses M5 action", summary["act"] == "read_project_summary")
    guard.outcome("create mint uses M5 action", create["act"] == "create_story")
    guard.outcome("policy saw both M5 tuples", [item["act"] for item in captured] == ["read_project_summary", "create_story"])


# UT: UT-192
# Test Description: Verifies capiss denies non-allowed M5 projects and old Jira subjects by policy.
# Precondition: capiss module is loaded and OPA is stubbed to deny evaluated M5 tuples.
# Expected Output: NAS and agent-a M5 mints return policy denials after canonical resource validation.
# Covers DD: DD-103, DD-104, DD-125, DD-129
@pytest.mark.negative_control
def test_root_mint_jira_mcp_denies_nas_and_old_subject(capiss_module, monkeypatch, guard):
    guard.premise("capiss module loaded", capiss_module is not None)
    captured: list[dict[str, object]] = []
    guard.exercise("stub opa deny", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda payload: captured.append(payload) or (False, None)))
    nas_body = {**M5_SUMMARY_BODY, "res": "jira-mcp:/project:NAS"}
    nas = guard.exercise(
        "attempt NAS M5 mint",
        lambda: capiss_module.root_mint(payload=nas_body, x_spiffe_id="spiffe://varambu.org/codex-jira-mcp-adapter"),
    )
    old_subject = guard.exercise(
        "attempt agent-a M5 mint",
        lambda: capiss_module.root_mint(payload=M5_SUMMARY_BODY, x_spiffe_id="spiffe://varambu.org/agent-a"),
    )
    guard.outcome("NAS denied by policy", nas.status_code == 403 and _json_body(nas)["reason"] == "policy")
    guard.outcome("old subject denied by policy", old_subject.status_code == 403 and _json_body(old_subject)["reason"] == "policy")
    guard.outcome("NAS reached policy as canonical M5 resource", captured[0]["res"] == "jira-mcp:/project:NAS")
