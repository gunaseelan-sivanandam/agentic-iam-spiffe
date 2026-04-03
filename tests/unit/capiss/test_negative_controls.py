from __future__ import annotations

import json

import pytest
from fastapi.responses import JSONResponse


SPIFFE_ID = "spiffe://example.org/agent-a"


def decode_body(resp: JSONResponse) -> dict:
    return json.loads(resp.body.decode("utf-8"))


def parent_claims(**overrides):
    base = {
        "subject_spiffe_id": SPIFFE_ID,
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "root_token_id": "root-1",
        "token_id": "parent-1",
        "effective_depth": 0,
        "exp": 2_000_000_000,
    }
    base.update(overrides)
    return base


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


# UT: UT-031
# Test Description: Verifies root mint missing aud has exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-104, DD-115
@pytest.mark.negative_control
def test_root_mint_missing_aud_has_exact_reason(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    resp = guard.exercise(
        "root mint missing aud",
        lambda: capiss_module.root_mint(
            payload={"act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 400", resp.status_code == 400)
    guard.outcome("error is bad_request", body.get("error") == "bad_request")
    guard.outcome("reason is aud", body.get("reason") == "aud")


# UT: UT-032
# Test Description: Verifies that resource mint requires registry proof exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-122
@pytest.mark.negative_control
def test_resource_mint_requires_registry_proof_exact_reason(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parent token",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), parent_claims(res="tool-b:/search"), None),
        ),
    )
    guard.exercise("mock registry miss", lambda: monkeypatch.setattr(capiss_module, "registry_has_resource", lambda *_: (True, False, "")))
    resp = guard.exercise(
        "resource mint without registry proof",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason is registry_miss", body.get("reason") == "registry_miss")


# UT: UT-033
# Test Description: Verifies resource mint depth exceeded exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
@pytest.mark.negative_control
def test_resource_mint_depth_exceeded_exact_reason(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parent at max depth",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (
                object(),
                parent_claims(effective_depth=capiss_module.M4_MAX_DEPTH),
                None,
            ),
        ),
    )
    resp = guard.exercise(
        "resource mint over depth",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
            authorization="Bearer parent",
        ),
    )
    body = guard.exercise("decode body", lambda: decode_body(resp))
    guard.outcome("status is 403", resp.status_code == 403)
    guard.outcome("reason is depth_exceeded", body.get("reason") == "depth_exceeded")


# UT: UT-034
# Test Description: Verifies resource mint amplification exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-105, DD-102
@pytest.mark.negative_control
def test_resource_mint_amplification_exact_reason(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock parent token claims",
        lambda: monkeypatch.setattr(
            capiss_module,
            "parse_token",
            lambda *_: (object(), parent_claims(act="read"), None),
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
    guard.outcome("reason is amplified_authority", body.get("reason") == "amplified_authority")
