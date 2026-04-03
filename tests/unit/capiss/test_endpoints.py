from __future__ import annotations

import json

import pytest
from fastapi.responses import JSONResponse


SPIFFE_ID = "spiffe://example.org/agent-a"


def decode_body(resp: JSONResponse) -> dict:
    return json.loads(resp.body.decode("utf-8"))


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


# UT: UT-015
# Test Description: Verifies that root mint requires spiffe id.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-115
def test_root_mint_requires_spiffe_id(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)

    def call_root_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.root_mint(payload={}, x_spiffe_id=None)
        return exc.value

    exc_value = guard.exercise("call root_mint without spiffe", call_root_mint)
    guard.outcome("status is 401", exc_value.status_code == 401)


# UT: UT-016
# Test Description: Verifies that root mint rejects invalid spiffe id.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-115
def test_root_mint_rejects_invalid_spiffe_id(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)

    def call_root_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.root_mint(payload={}, x_spiffe_id="not-spiffe")
        return exc.value

    exc_value = guard.exercise("call root_mint with invalid spiffe", call_root_mint)
    guard.outcome("status is 400", exc_value.status_code == 400)


# UT: UT-017
# Test Description: Verifies that root mint rejects invalid resource.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-115
def test_root_mint_rejects_invalid_resource(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    resp = guard.exercise(
        "root mint with invalid resource",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "bad"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 400", resp.status_code == 400)
    guard.outcome("reason is res", body.get("reason") == "res")


# UT: UT-018
# Test Description: Verifies root mint fail closed when budget store unavailable.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-120
@pytest.mark.invariant
def test_root_mint_fail_closed_when_budget_store_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock mint root",
        lambda: monkeypatch.setattr(
            capiss_module,
            "mint_root_biscuit",
            lambda *_: ("token", 2_000_000_000, "root-1", "token-1"),
        ),
    )
    guard.exercise("mock budget unavailable", lambda: monkeypatch.setattr(capiss_module, "ensure_root_budget", lambda *_: (False, "down")))
    resp = guard.exercise(
        "invoke root mint",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason is store_unavailable", body.get("reason") == "store_unavailable")


# UT: UT-019
# Test Description: Verifies root mint fail closed when marker store unavailable.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-121
def test_root_mint_fail_closed_when_marker_store_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock mint root",
        lambda: monkeypatch.setattr(
            capiss_module,
            "mint_root_biscuit",
            lambda *_: ("token", 2_000_000_000, "root-1", "token-1"),
        ),
    )
    guard.exercise("mock budget allow", lambda: monkeypatch.setattr(capiss_module, "ensure_root_budget", lambda *_: (True, "")))
    guard.exercise("mock marker failure", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (False, "down")))
    resp = guard.exercise(
        "invoke root mint",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason is store_unavailable", body.get("reason") == "store_unavailable")


# UT: UT-020
# Test Description: Verifies that root mint success.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-104
def test_root_mint_success(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock mint root",
        lambda: monkeypatch.setattr(
            capiss_module,
            "mint_root_biscuit",
            lambda *_: ("token-value", 2_000_000_000, "root-1", "token-1"),
        ),
    )
    guard.exercise("mock budget allow", lambda: monkeypatch.setattr(capiss_module, "ensure_root_budget", lambda *_: (True, "")))
    guard.exercise("mock marker allow", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    out = guard.exercise(
        "invoke root mint",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    guard.outcome("token present", out.get("token") == "token-value")
    guard.outcome("root token id preserved", out.get("root_token_id") == "root-1")
    guard.outcome("depth is zero", out.get("delegation_depth") == 0)
    guard.outcome("parent token id absent", out.get("parent_token_id") is None)


# UT: UT-087
# Test Description: Verifies that the compatibility mint endpoint dispatches directly to root mint.
# Precondition: Module fixtures are loaded and root mint is stubbed to a deterministic response.
# Expected Output: The SUT forwards payload and caller SPIFFE identity unchanged and returns the exact root mint result.
# Covers DD: DD-106
def test_mint_dispatches_to_root_mint(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = {"aud": "tool-b", "act": "read", "res": "tool-b:/search"}
    forwarded = {}
    expected = {"token": "compat-token", "root_token_id": "root-1"}

    def fake_root_mint(*, payload=None, x_spiffe_id=None):
        forwarded["payload"] = payload
        forwarded["x_spiffe_id"] = x_spiffe_id
        return expected

    guard.exercise("mock root mint", lambda: monkeypatch.setattr(capiss_module, "root_mint", fake_root_mint))
    out = guard.exercise(
        "invoke compatibility mint",
        lambda: capiss_module.mint(payload=payload, x_spiffe_id=SPIFFE_ID),
    )
    guard.outcome("root mint result returned", out == expected)
    guard.outcome("payload forwarded", forwarded.get("payload") == payload)
    guard.outcome("spiffe id forwarded", forwarded.get("x_spiffe_id") == SPIFFE_ID)


def base_parent_claims(**overrides):
    claims = {
        "subject_spiffe_id": SPIFFE_ID,
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "root_token_id": "root-1",
        "token_id": "parent-1",
        "effective_depth": 0,
        "exp": 2_000_000_000,
    }
    claims.update(overrides)
    return claims


# UT: UT-021
# Test Description: Verifies that resource mint requires bearer token.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105
def test_resource_mint_requires_bearer_token(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    resp = guard.exercise(
        "resource mint without auth header",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization=None,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 401", resp.status_code == 401)
    guard.outcome("reason missing_token", body.get("reason") == "missing_token")


# UT: UT-022
# Test Description: Verifies that resource mint rejects invalid parent token.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
def test_resource_mint_rejects_invalid_parent_token(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("mock parse token invalid", lambda: monkeypatch.setattr(capiss_module, "parse_token", lambda *_: (None, None, "invalid_token")))
    resp = guard.exercise(
        "resource mint with invalid parent token",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 401", resp.status_code == 401)
    guard.outcome("reason invalid_token", body.get("reason") == "invalid_token")


# UT: UT-023
# Test Description: Verifies that resource mint rejects subject mismatch.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
@pytest.mark.invariant
def test_resource_mint_rejects_subject_mismatch(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parse token with subject mismatch",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(subject_spiffe_id="spiffe://example.org/rogue"), None),
        ),
    )
    resp = guard.exercise(
        "resource mint with mismatched subject",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason sub_mismatch", body.get("reason") == "sub_mismatch")


# UT: UT-024
# Test Description: Verifies that resource mint enforces depth limit.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
@pytest.mark.boundary
def test_resource_mint_enforces_depth_limit(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parse token at max depth",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(effective_depth=capiss_module.M4_MAX_DEPTH), None),
        ),
    )
    resp = guard.exercise(
        "resource mint over depth limit",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason depth_exceeded", body.get("reason") == "depth_exceeded")


# UT: UT-025
# Test Description: Verifies that resource mint requires registry hit for new resource.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-122
@pytest.mark.invariant
def test_resource_mint_requires_registry_hit_for_new_resource(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(res="tool-b:/search"), None),
        ),
    )
    guard.exercise("mock registry miss", lambda: monkeypatch.setattr(capiss_module, "registry_has_resource", lambda *_: (True, False, "")))
    resp = guard.exercise(
        "resource mint for undiscovered resource",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason registry_miss", body.get("reason") == "registry_miss")


# UT: UT-026
# Test Description: Verifies resource mint fail closed on registry store error.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-122
@pytest.mark.invariant
def test_resource_mint_fail_closed_on_registry_store_error(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(res="tool-b:/search"), None),
        ),
    )
    guard.exercise("mock registry store error", lambda: monkeypatch.setattr(capiss_module, "registry_has_resource", lambda *_: (False, False, "down")))
    resp = guard.exercise(
        "resource mint while registry down",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason store_unavailable", body.get("reason") == "store_unavailable")


# UT: UT-027
# Test Description: Verifies that resource mint success.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-105
def test_resource_mint_success(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(), None),
        ),
    )
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock append token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "append_resource_token",
            lambda *_: ("resource-token", 2_000_000_000, "token-child"),
        ),
    )
    guard.exercise("mock marker allow", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    out = guard.exercise(
        "invoke resource mint",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    guard.outcome("token returned", out.get("token") == "resource-token")
    guard.outcome("root token id kept", out.get("root_token_id") == "root-1")
    guard.outcome("parent token id set", out.get("parent_token_id") == "parent-1")


# UT: UT-028
# Test Description: Verifies that resource mint rejects amplified authority.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
def test_resource_mint_rejects_amplified_authority(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parent claims",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(act="read"), None),
        ),
    )
    resp = guard.exercise(
        "resource mint with amplified act",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "write", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason amplified_authority", body.get("reason") == "amplified_authority")
