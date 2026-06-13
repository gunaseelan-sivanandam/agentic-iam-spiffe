from __future__ import annotations

import json

import pytest


JIRA_IAM_BODY = {"aud": "jira-tool", "act": "read", "res": "jira-tool:/project:IAM"}
JIRA_IAM_WRITE_BODY = {"aud": "jira-tool", "act": "write", "res": "jira-tool:/project:IAM"}


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


def _json_response_body(response) -> dict:
    return json.loads(response.body.decode("utf-8"))


# UT: UT-160
# Test Description: Verifies capiss sends the full Jira authority tuple to policy and mints the allowed IAM token.
# Precondition: capiss module is loaded and policy/store dependencies are stubbed to allow the exact IAM tuple.
# Expected Output: root mint succeeds and the policy input includes caller, aud, act, and canonical Jira project resource.
# Covers DD: DD-104, DD-125, DD-126
@pytest.mark.invariant
def test_root_mint_jira_allowed_full_tuple(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    captured: list[dict[str, object]] = []

    def fake_opa(payload):
        captured.append(payload)
        return True, None

    guard.exercise("stub opa allow", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", fake_opa))
    guard.exercise("stub budget init", lambda: monkeypatch.setattr(capiss_module, "ensure_root_budget", lambda *_: (True, "")))
    guard.exercise("stub mint marker", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    out = guard.exercise(
        "mint Jira IAM root token",
        lambda: capiss_module.root_mint(payload=JIRA_IAM_BODY, x_spiffe_id="spiffe://varambu.org/agent-a"),
    )
    guard.outcome("mint returned dict response", isinstance(out, dict))
    guard.outcome("issued Jira audience", out["aud"] == "jira-tool")
    guard.outcome("issued read action", out["act"] == "read")
    guard.outcome("issued IAM project resource", out["res"] == "jira-tool:/project:IAM")
    guard.outcome(
        "policy saw full tuple",
        captured
        == [
            {
                "decision_type": "root_mint",
                "sub": "spiffe://varambu.org/agent-a",
                "subject_spiffe_id": "spiffe://varambu.org/agent-a",
                "aud": "jira-tool",
                "act": "read",
                "res": "jira-tool:/project:IAM",
            }
        ],
    )


# UT: UT-161
# Test Description: Verifies capiss denies Jira project minting when the action is not policy-approved.
# Precondition: capiss module is loaded and OPA is stubbed to deny the presented full tuple.
# Expected Output: root mint returns a policy denial and the denied tuple retains the unsupported action for audit/policy evaluation.
# Covers DD: DD-103, DD-104, DD-125, DD-126
@pytest.mark.invariant
def test_root_mint_jira_unsupported_action_denied_by_policy(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    captured: list[dict[str, object]] = []

    def fake_opa(payload):
        captured.append(payload)
        return False, None

    body = {"aud": "jira-tool", "act": "delete", "res": "jira-tool:/project:IAM"}
    guard.exercise("stub opa deny", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", fake_opa))
    response = guard.exercise(
        "attempt unsupported-action Jira mint",
        lambda: capiss_module.root_mint(payload=body, x_spiffe_id="spiffe://varambu.org/agent-a"),
    )
    guard.outcome("policy denial status", response.status_code == 403)
    guard.outcome("policy denial reason", _json_response_body(response)["reason"] == "policy")
    guard.outcome("unsupported action reached policy tuple", captured[0]["act"] == "delete")


# UT: UT-178
# Test Description: Verifies capiss sends the M4b Jira write authority tuple to policy and mints the allowed IAM token.
# Precondition: capiss module is loaded and policy/store dependencies are stubbed to allow the exact IAM write tuple.
# Expected Output: root mint succeeds and the policy input includes caller, aud, write act, and canonical Jira project resource.
# Covers DD: DD-104, DD-125, DD-126, DD-128
@pytest.mark.invariant
def test_root_mint_jira_write_allowed_full_tuple(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    captured: list[dict[str, object]] = []

    def fake_opa(payload):
        captured.append(payload)
        return True, None

    guard.exercise("stub opa allow", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", fake_opa))
    guard.exercise("stub budget init", lambda: monkeypatch.setattr(capiss_module, "ensure_root_budget", lambda *_: (True, "")))
    guard.exercise("stub mint marker", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    out = guard.exercise(
        "mint Jira IAM write root token",
        lambda: capiss_module.root_mint(payload=JIRA_IAM_WRITE_BODY, x_spiffe_id="spiffe://varambu.org/agent-a"),
    )
    guard.outcome("mint returned dict response", isinstance(out, dict))
    guard.outcome("issued Jira audience", out["aud"] == "jira-tool")
    guard.outcome("issued write action", out["act"] == "write")
    guard.outcome("issued IAM project resource", out["res"] == "jira-tool:/project:IAM")
    guard.outcome(
        "policy saw full write tuple",
        captured
        == [
            {
                "decision_type": "root_mint",
                "sub": "spiffe://varambu.org/agent-a",
                "subject_spiffe_id": "spiffe://varambu.org/agent-a",
                "aud": "jira-tool",
                "act": "write",
                "res": "jira-tool:/project:IAM",
            }
        ],
    )


# UT: UT-162
# Test Description: Verifies capiss denies syntactically valid Jira project mints for non-allowed projects.
# Precondition: capiss module is loaded and OPA is stubbed to deny the NAS project tuple.
# Expected Output: root mint returns a policy denial after canonicalizing the NAS project resource.
# Covers DD: DD-103, DD-104, DD-125, DD-126
@pytest.mark.invariant
def test_root_mint_jira_non_allowed_project_denied_by_policy(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    captured: list[dict[str, object]] = []

    def fake_opa(payload):
        captured.append(payload)
        return False, None

    body = {"aud": "jira-tool", "act": "read", "res": "jira-tool:/project:NAS"}
    guard.exercise("stub opa deny", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", fake_opa))
    response = guard.exercise(
        "attempt NAS project Jira mint",
        lambda: capiss_module.root_mint(payload=body, x_spiffe_id="spiffe://varambu.org/agent-a"),
    )
    guard.outcome("policy denial status", response.status_code == 403)
    guard.outcome("policy denial reason", _json_response_body(response)["reason"] == "policy")
    guard.outcome("NAS resource reached policy tuple", captured[0]["res"] == "jira-tool:/project:NAS")


# UT: UT-163
# Test Description: Verifies capiss denies Jira mints for rogue caller identity.
# Precondition: capiss module is loaded and OPA is stubbed to deny the rogue caller tuple.
# Expected Output: root mint returns a policy denial and the caller identity is preserved in the policy input.
# Covers DD: DD-103, DD-104, DD-125, DD-126
@pytest.mark.invariant
def test_root_mint_jira_rogue_caller_denied_by_policy(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    captured: list[dict[str, object]] = []

    def fake_opa(payload):
        captured.append(payload)
        return False, None

    guard.exercise("stub opa deny", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", fake_opa))
    response = guard.exercise(
        "attempt rogue Jira mint",
        lambda: capiss_module.root_mint(payload=JIRA_IAM_BODY, x_spiffe_id="spiffe://varambu.org/rogue"),
    )
    guard.outcome("policy denial status", response.status_code == 403)
    guard.outcome("policy denial reason", _json_response_body(response)["reason"] == "policy")
    guard.outcome("rogue caller reached policy tuple", captured[0]["sub"] == "spiffe://varambu.org/rogue")
