from __future__ import annotations

import json

import pytest
from fastapi.responses import JSONResponse


SPIFFE_ID = "spiffe://varambu.org/agent-a"


def decode_body(resp: JSONResponse) -> dict:
    return json.loads(resp.body.decode("utf-8"))


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


def capture_log_events(monkeypatch, capiss_module):
    events = []
    legacy_projection_drop = {
        "timestamp_utc",
        "timestamp_local",
        "timezone",
        "issued_at_utc",
        "issued_at_local",
        "expires_at_utc",
        "expires_at_local",
        "ttl_seconds",
        "resource_attrs",
    }

    def fake_log_event(event_type: str, **fields):
        events.append({"event_type": event_type, **{key: value for key, value in fields.items() if key not in legacy_projection_drop}})

    monkeypatch.setattr(capiss_module, "log_event", fake_log_event)
    return events


def final_mint_events(events: list[dict]) -> list[dict]:
    return [event for event in events if event["event_type"] == "capiss_mint_decision"]


# UT: UT-015
# Test Description: Verifies that root mint requires spiffe id.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-115
@pytest.mark.invariant
def test_root_mint_requires_spiffe_id_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))

    def call_root_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.root_mint(payload={}, x_spiffe_id=None)
        return exc.value

    exc_value = guard.exercise("call root_mint without spiffe", call_root_mint)
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 401", exc_value.status_code == 401)
    guard.outcome(
        "final mint decision logged exactly once",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "missing_spiffe_id",
                "decision_type": "root_mint",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-016
# Test Description: Verifies that root mint rejects invalid spiffe id.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-115
@pytest.mark.invariant
def test_root_mint_rejects_invalid_spiffe_id(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))

    def call_root_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.root_mint(payload={}, x_spiffe_id="not-spiffe")
        return exc.value

    exc_value = guard.exercise("call root_mint with invalid spiffe", call_root_mint)
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 400", exc_value.status_code == 400)
    guard.outcome(
        "invalid spiffe logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "invalid_spiffe_id",
                "decision_type": "root_mint",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-017
# Test Description: Verifies that root mint rejects invalid resource.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-115
@pytest.mark.invariant
def test_root_mint_rejects_invalid_resource(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    resp = guard.exercise(
        "root mint with invalid resource",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "bad"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 400", resp.status_code == 400)
    guard.outcome("reason is res", body.get("reason") == "res")
    guard.outcome(
        "invalid resource logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "res",
                "decision_type": "root_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "aud": "tool-b",
                "act": "read",
                "res": "bad",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-018
# Test Description: Verifies root mint fail closed when budget store unavailable.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-120
@pytest.mark.invariant
def test_root_mint_fail_closed_when_budget_store_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock mint root",
        lambda: monkeypatch.setattr(
            capiss_module,
            "mint_root_biscuit",
            lambda *_: ("token", 1_999_999_940, 2_000_000_000, "root-1", "token-1"),
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason is store_unavailable", body.get("reason") == "store_unavailable")
    guard.outcome(
        "budget store failure logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "store_unavailable",
                "decision_type": "root_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-1",
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "error": "down",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-019
# Test Description: Verifies root mint fail closed when marker store unavailable.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-121
def test_root_mint_fail_closed_when_marker_store_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock mint root",
        lambda: monkeypatch.setattr(
            capiss_module,
            "mint_root_biscuit",
            lambda *_: ("token", 1_999_999_940, 2_000_000_000, "root-1", "token-1"),
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason is store_unavailable", body.get("reason") == "store_unavailable")
    guard.outcome(
        "marker store failure logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "store_unavailable",
                "decision_type": "root_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-1",
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "error": "down",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-020
# Test Description: Verifies that root mint success logs the final mint-decision event.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-104
@pytest.mark.invariant
def test_root_mint_success_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock mint root",
        lambda: monkeypatch.setattr(
            capiss_module,
            "mint_root_biscuit",
            lambda *_: ("token-value", 1_999_999_940, 2_000_000_000, "root-1", "token-1"),
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("token present", out.get("token") == "token-value")
    guard.outcome("root token id preserved", out.get("root_token_id") == "root-1")
    guard.outcome("depth is zero", out.get("delegation_depth") == 0)
    guard.outcome("parent token id absent", out.get("parent_token_id") is None)
    guard.outcome(
        "root mint success logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "allow",
                "reason_code": "ok",
                "decision_type": "root_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-138
# Test Description: Verifies that root mint logs a final mint decision when the payload is invalid before canonicalization.
# Precondition: The caller SPIFFE identity is valid and the request body is missing required mint fields.
# Expected Output: The SUT returns the existing bad-request response and emits one exact final `capiss_mint_decision` event carrying the validation reason and known request fields.
# Covers DD: DD-104, DD-115, DD-222
@pytest.mark.invariant
def test_root_mint_bad_payload_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    resp = guard.exercise(
        "invoke root mint with missing res field",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 400", resp.status_code == 400)
    guard.outcome("reason is res", body == {"error": "bad_request", "reason": "res"})
    guard.outcome(
        "bad payload logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "res",
                "decision_type": "root_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "aud": "tool-b",
                "act": "read",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-139
# Test Description: Verifies that root mint logs a final mint decision when policy denies the request.
# Precondition: The caller identity and payload are valid and the policy boundary denies deterministically.
# Expected Output: The SUT returns the existing policy-deny response and emits one exact final `capiss_mint_decision` event for that deny path.
# Covers DD: DD-103, DD-104, DD-222
@pytest.mark.invariant
def test_root_mint_policy_deny_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock policy deny",
        lambda: monkeypatch.setattr(
            capiss_module,
            "run_policy_or_fail",
            lambda *_: (False, JSONResponse(status_code=403, content={"error": "denied", "reason": "policy"})),
        ),
    )
    resp = guard.exercise(
        "invoke root mint with policy deny",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason is policy", body == {"error": "denied", "reason": "policy"})
    guard.outcome(
        "policy deny logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "policy",
                "decision_type": "root_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


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

    def fake_root_mint(*, payload=None, x_spiffe_id=None, x_correlation_id=None):
        forwarded["payload"] = payload
        forwarded["x_spiffe_id"] = x_spiffe_id
        forwarded["x_correlation_id"] = x_correlation_id
        return expected

    guard.exercise("mock root mint", lambda: monkeypatch.setattr(capiss_module, "root_mint", fake_root_mint))
    out = guard.exercise(
        "invoke compatibility mint",
        lambda: capiss_module.mint(payload=payload, x_spiffe_id=SPIFFE_ID),
    )
    guard.outcome("root mint result returned", out == expected)
    guard.outcome("payload forwarded", forwarded.get("payload") == payload)
    guard.outcome("spiffe id forwarded", forwarded.get("x_spiffe_id") == SPIFFE_ID)
    guard.outcome("correlation absent by default", forwarded.get("x_correlation_id") is None)


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


# UT: UT-229
# Test Description: Verifies that resource mint requires spiffe id before any bearer-token processing.
# Precondition: Module fixtures are loaded and final mint-decision logging is captured.
# Expected Output: The SUT raises the existing 401 error and emits one resource-mint deny decision.
# Covers DD: DD-105, DD-222
@pytest.mark.invariant
def test_resource_mint_requires_spiffe_id_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))

    def call_resource_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.resource_mint(payload={}, x_spiffe_id=None, authorization="Bearer parent")
        return exc.value

    exc_value = guard.exercise("call resource_mint without spiffe", call_resource_mint)
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 401", exc_value.status_code == 401)
    guard.outcome(
        "missing spiffe logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "missing_spiffe_id",
                "decision_type": "resource_mint",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-230
# Test Description: Verifies that resource mint rejects invalid spiffe id before any bearer-token processing.
# Precondition: Module fixtures are loaded and final mint-decision logging is captured.
# Expected Output: The SUT raises the existing 400 error and emits one resource-mint deny decision.
# Covers DD: DD-105, DD-222
@pytest.mark.invariant
def test_resource_mint_rejects_invalid_spiffe_id_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))

    def call_resource_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.resource_mint(payload={}, x_spiffe_id="not-spiffe", authorization="Bearer parent")
        return exc.value

    exc_value = guard.exercise("call resource_mint with invalid spiffe", call_resource_mint)
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 400", exc_value.status_code == 400)
    guard.outcome(
        "invalid spiffe logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "invalid_spiffe_id",
                "decision_type": "resource_mint",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-021
# Test Description: Verifies that resource mint requires bearer token and logs the final mint-decision event.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105
@pytest.mark.invariant
def test_resource_mint_requires_bearer_token_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    resp = guard.exercise(
        "resource mint without auth header",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization=None,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 401", resp.status_code == 401)
    guard.outcome("reason missing_token", body.get("reason") == "missing_token")
    guard.outcome(
        "missing token logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "missing_token",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-231
# Test Description: Verifies that resource mint treats an empty bearer value as a missing token.
# Precondition: Module fixtures are loaded and the authorization header has the Bearer scheme but no token value.
# Expected Output: The SUT returns the existing missing-token denial and emits one final resource-mint decision.
# Covers DD: DD-105, DD-222
@pytest.mark.invariant
def test_resource_mint_rejects_empty_bearer_token_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    resp = guard.exercise(
        "resource mint with empty bearer",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer   ",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 401", resp.status_code == 401)
    guard.outcome("reason missing_token", body.get("reason") == "missing_token")
    guard.outcome(
        "empty bearer logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "missing_token",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-022
# Test Description: Verifies that resource mint rejects invalid parent token.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
def test_resource_mint_rejects_invalid_parent_token(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 401", resp.status_code == 401)
    guard.outcome("reason invalid_token", body.get("reason") == "invalid_token")
    guard.outcome(
        "invalid token logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "invalid_token",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-023
# Test Description: Verifies that resource mint rejects subject mismatch.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
@pytest.mark.invariant
def test_resource_mint_rejects_subject_mismatch(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token with subject mismatch",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(subject_spiffe_id="spiffe://varambu.org/rogue"), None),
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason sub_mismatch", body.get("reason") == "sub_mismatch")
    guard.outcome(
        "subject mismatch logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "sub_mismatch",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-024
# Test Description: Verifies that resource mint enforces depth limit.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
@pytest.mark.boundary
def test_resource_mint_enforces_depth_limit(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason depth_exceeded", body.get("reason") == "depth_exceeded")
    guard.outcome(
        "depth exceeded logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "depth_exceeded",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": capiss_module.M4_MAX_DEPTH,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-025
# Test Description: Verifies that resource mint requires registry hit for new resource.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-122
@pytest.mark.invariant
def test_resource_mint_registry_miss_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason registry_miss", body.get("reason") == "registry_miss")
    guard.outcome(
        "registry miss logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "registry_miss",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/read-file:fileA",
                "registry_hit": False,
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-026
# Test Description: Verifies resource mint fail closed on registry store error.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-122
@pytest.mark.invariant
def test_resource_mint_fail_closed_on_registry_store_error(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason store_unavailable", body.get("reason") == "store_unavailable")
    guard.outcome(
        "registry store failure logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "store_unavailable",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/read-file:fileA",
                "error": "down",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-027
# Test Description: Verifies that resource mint success logs the final mint-decision event.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-105
@pytest.mark.invariant
def test_resource_mint_success_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
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
            lambda *_: ("resource-token", 1_999_999_940, 2_000_000_000, "token-child"),
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("token returned", out.get("token") == "resource-token")
    guard.outcome("root token id kept", out.get("root_token_id") == "root-1")
    guard.outcome("parent token id set", out.get("parent_token_id") == "parent-1")
    guard.outcome(
        "resource mint success logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "allow",
                "reason_code": "ok",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-child",
                "parent_token_id": "parent-1",
                "delegation_depth": 1,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "registry_hit": True,
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-144
# Test Description: Verifies that a delegated resource mint success log carries delegator provenance for reduced-scope reconstruction.
# Precondition: The parent token is valid for `tool-b:/search`, registry proof succeeds for `tool-b:/read-file:fileA`, and final audit emission is captured through the module-local log helper.
# Expected Output: The SUT logs one exact successful `capiss_mint_decision` event for the delegated mint, including `delegator_spiffe_id` together with the correlated root and parent identifiers.
# Covers DD: DD-105, DD-222
@pytest.mark.invariant
def test_resource_mint_success_logs_delegator_provenance(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(res="tool-b:/search"), None),
        ),
    )
    guard.exercise("mock registry hit", lambda: monkeypatch.setattr(capiss_module, "registry_has_resource", lambda *_: (True, True, "")))
    guard.exercise("mock mint-rate allow", lambda: monkeypatch.setattr(capiss_module, "consume_mint_rate", lambda *_: (True, "")))
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock append token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "append_resource_token",
            lambda *_: ("resource-token", 1_999_999_940, 2_000_000_000, "token-child"),
        ),
    )
    guard.exercise("mock marker allow", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    out = guard.exercise(
        "invoke delegated resource mint",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("token returned", out.get("token") == "resource-token")
    guard.outcome(
        "delegated mint success logs delegator provenance exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "allow",
                "reason_code": "ok",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-child",
                "parent_token_id": "parent-1",
                "delegation_depth": 1,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/read-file:fileA",
                "registry_hit": True,
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-028
# Test Description: Verifies that resource mint rejects amplified authority.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
def test_resource_mint_rejects_amplified_authority(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
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
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason amplified_authority", body.get("reason") == "amplified_authority")
    guard.outcome(
        "amplified authority logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "amplified_authority",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "write",
                "res": "tool-b:/search",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-134
# Test Description: Verifies that same-resource child remints do not consume mint-rate allowance.
# Precondition: The parent token is valid for `tool-b:/search` and the mint-rate helper is replaced with a counter fake.
# Expected Output: The SUT succeeds without calling the mint-rate helper when the requested canonical resource equals the parent resource.
# Covers DD: DD-105, DD-221
@pytest.mark.invariant
def test_resource_mint_same_resource_bypasses_mint_rate(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    seen = {"calls": 0}
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(res="tool-b:/search"), None),
        ),
    )
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock append token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "append_resource_token",
            lambda *_: ("resource-token", 1_999_999_940, 2_000_000_000, "token-child"),
        ),
    )
    guard.exercise("mock marker allow", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    guard.exercise(
        "mock mint-rate helper",
        lambda: monkeypatch.setattr(
            capiss_module,
            "consume_mint_rate",
            lambda *_: seen.__setitem__("calls", seen["calls"] + 1) or (True, ""),
        ),
    )
    out = guard.exercise(
        "invoke same-resource mint",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    guard.outcome("mint succeeded", out.get("token") == "resource-token")
    guard.outcome("mint-rate helper not called", seen["calls"] == 0)


# UT: UT-135
# Test Description: Verifies that new-resource mints consume mint-rate allowance exactly once.
# Precondition: The parent token is valid for `tool-b:/search`, the registry lookup succeeds, and the mint-rate helper records its calls.
# Expected Output: The SUT invokes the mint-rate helper once with the parent root token id and root expiry before minting the new resource token.
# Covers DD: DD-105, DD-122, DD-221
@pytest.mark.invariant
def test_resource_mint_new_resource_consumes_mint_rate_once(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    seen = []
    parent_claims = base_parent_claims(res="tool-b:/search", exp=2_000_000_000)
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(capiss_module, "parse_token", lambda *_: (object(), parent_claims, None)),
    )
    guard.exercise("mock registry hit", lambda: monkeypatch.setattr(capiss_module, "registry_has_resource", lambda *_: (True, True, "")))
    guard.exercise(
        "mock mint-rate helper",
        lambda: monkeypatch.setattr(
            capiss_module,
            "consume_mint_rate",
            lambda root_token_id, root_exp, root_lifetime_seconds: seen.append((root_token_id, root_exp, root_lifetime_seconds)) or (True, ""),
        ),
    )
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock append token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "append_resource_token",
            lambda *_: ("resource-token", 1_999_999_940, 2_000_000_000, "token-child"),
        ),
    )
    guard.exercise("mock marker allow", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (True, "")))
    out = guard.exercise(
        "invoke new-resource mint",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    guard.outcome("mint succeeded", out.get("token") == "resource-token")
    guard.outcome("mint-rate helper called once", len(seen) == 1)
    guard.outcome("root token id passed", seen[0][0] == "root-1")
    guard.outcome("root expiry passed", seen[0][1] == 2_000_000_000)
    guard.outcome("root lifetime constant passed", seen[0][2] == capiss_module.M4_ROOT_TTL_SECONDS)


# UT: UT-232
# Test Description: Verifies that resource mint fails closed when the delegated token marker store is unavailable after child token creation.
# Precondition: Parent token, policy, registry, and mint-rate checks allow, but the minted-token marker write fails.
# Expected Output: The SUT returns store_unavailable and emits a final decision with child and parent token context.
# Covers DD: DD-105, DD-121, DD-222
@pytest.mark.invariant
def test_resource_mint_fail_closed_when_marker_store_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(capiss_module, "parse_token", lambda *_: (object(), base_parent_claims(), None)),
    )
    guard.exercise("mock policy allow", lambda: monkeypatch.setattr(capiss_module, "run_policy_or_fail", lambda *_: (True, None)))
    guard.exercise(
        "mock append token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "append_resource_token",
            lambda *_: ("resource-token", 1_999_999_940, 2_000_000_000, "token-child"),
        ),
    )
    guard.exercise("mock marker failure", lambda: monkeypatch.setattr(capiss_module, "mark_capiss_minted_token", lambda *_: (False, "down")))
    resp = guard.exercise(
        "invoke resource mint",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason is store_unavailable", body.get("reason") == "store_unavailable")
    guard.outcome(
        "resource marker failure logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "store_unavailable",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-child",
                "parent_token_id": "parent-1",
                "delegation_depth": 1,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "registry_hit": True,
                "error": "down",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-136
# Test Description: Verifies that capiss denies a new-resource mint when the mint-rate allowance is exhausted.
# Precondition: The parent token is valid for a new-resource mint, the registry lookup succeeds, and the mint-rate helper returns `mint_rate_exceeded`.
# Expected Output: The SUT returns the exact `403` deny payload with reason `mint_rate_exceeded`.
# Covers DD: DD-105, DD-122, DD-221
@pytest.mark.invariant
def test_resource_mint_denies_when_mint_rate_exceeded(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(res="tool-b:/search"), None),
        ),
    )
    guard.exercise("mock registry hit", lambda: monkeypatch.setattr(capiss_module, "registry_has_resource", lambda *_: (True, True, "")))
    guard.exercise("mock mint-rate exceeded", lambda: monkeypatch.setattr(capiss_module, "consume_mint_rate", lambda *_: (False, "mint_rate_exceeded")))
    resp = guard.exercise(
        "invoke over-limit new-resource mint",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason mint_rate_exceeded", body == {"error": "denied", "reason": "mint_rate_exceeded"})
    guard.outcome(
        "mint-rate exceeded logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "mint_rate_exceeded",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/read-file:fileA",
                "registry_hit": True,
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-137
# Test Description: Verifies that capiss fails closed when the mint-rate store is unavailable during a new-resource mint.
# Precondition: The parent token is valid for a new-resource mint, the registry lookup succeeds, and the mint-rate helper returns `store_unavailable`.
# Expected Output: The SUT returns the exact `503` deny payload with reason `store_unavailable`.
# Covers DD: DD-105, DD-122, DD-221
@pytest.mark.invariant
def test_resource_mint_fail_closed_when_mint_rate_store_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), base_parent_claims(res="tool-b:/search"), None),
        ),
    )
    guard.exercise("mock registry hit", lambda: monkeypatch.setattr(capiss_module, "registry_has_resource", lambda *_: (True, True, "")))
    guard.exercise("mock mint-rate store unavailable", lambda: monkeypatch.setattr(capiss_module, "consume_mint_rate", lambda *_: (False, "store_unavailable")))
    resp = guard.exercise(
        "invoke new-resource mint while mint-rate store unavailable",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 503", resp.status_code == 503)
    guard.outcome("reason store_unavailable", body == {"error": "denied", "reason": "store_unavailable"})
    guard.outcome(
        "mint-rate store failure logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "store_unavailable",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/read-file:fileA",
                "registry_hit": True,
                "error": "store_unavailable",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )

# UT: UT-140
# Test Description: Verifies that resource mint logs a final mint decision when policy denies a valid delegated mint request.
# Precondition: The parent token, caller identity, and requested canonical resource are valid and the policy boundary denies deterministically.
# Expected Output: The SUT returns the existing policy-deny response and emits one exact final `capiss_mint_decision` event for that deny path.
# Covers DD: DD-103, DD-105, DD-222
@pytest.mark.invariant
def test_resource_mint_policy_deny_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(capiss_module, "parse_token", lambda *_: (object(), base_parent_claims(), None)),
    )
    guard.exercise(
        "mock policy deny",
        lambda: monkeypatch.setattr(
            capiss_module,
            "run_policy_or_fail",
            lambda *_: (False, JSONResponse(status_code=403, content={"error": "denied", "reason": "policy"})),
        ),
    )
    resp = guard.exercise(
        "invoke delegated mint with policy deny",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason is policy", body == {"error": "denied", "reason": "policy"})
    guard.outcome(
        "resource policy deny logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "policy",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/search",
                "registry_hit": True,
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-141
# Test Description: Verifies that resource mint logs a final mint decision when the delegated mint payload is invalid before canonicalization completes.
# Precondition: The parent token is valid and the child mint request is missing the required `res` field.
# Expected Output: The SUT returns the existing bad-request response and emits one exact final `capiss_mint_decision` event with the validation reason and parent context.
# Covers DD: DD-105, DD-115, DD-222
@pytest.mark.invariant
def test_resource_mint_bad_payload_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(capiss_module, "parse_token", lambda *_: (object(), base_parent_claims(), None)),
    )
    resp = guard.exercise(
        "invoke delegated mint with missing res field",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 400", resp.status_code == 400)
    guard.outcome("reason is res", body == {"error": "bad_request", "reason": "res"})
    guard.outcome(
        "resource bad payload logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "res",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )


# UT: UT-233
# Test Description: Verifies resource mint rejects a syntactically invalid child resource after parent context is known.
# Precondition: The parent token parses successfully and the child request has all required fields but a non-canonical resource.
# Expected Output: The SUT returns the existing bad-request response and emits a final decision with parent/root context.
# Covers DD: DD-105, DD-115, DD-222
@pytest.mark.invariant
def test_resource_mint_invalid_child_resource_logs_final_decision(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, capiss_module))
    guard.exercise(
        "mock parse token",
        lambda: monkeypatch.setattr(capiss_module, "parse_token", lambda *_: (object(), base_parent_claims(), None)),
    )
    resp = guard.exercise(
        "invoke delegated mint with invalid child resource",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "bad"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    mint_events = guard.exercise("collect final mint events", lambda: final_mint_events(events))
    guard.outcome("status is 400", resp.status_code == 400)
    guard.outcome("reason is res", body == {"error": "bad_request", "reason": "res"})
    guard.outcome(
        "invalid child resource logged exactly",
        mint_events
        == [
            {
                "event_type": "capiss_mint_decision",
                "result": "deny",
                "reason_code": "res",
                "decision_type": "resource_mint",
                "subject_spiffe_id": SPIFFE_ID,
                "delegator_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "parent_token_id": "parent-1",
                "delegation_depth": 0,
                "aud": "tool-b",
                "act": "read",
                "res": "bad",
                "policy_id": "capiss.allow.v3",
                "policy_hash": "sha256:capiss-policy-v3",
            }
        ],
    )
