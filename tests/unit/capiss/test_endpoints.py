from __future__ import annotations

import json

import pytest
from fastapi.responses import JSONResponse


SPIFFE_ID = "spiffe://example.org/agent-a"


def decode_body(resp: JSONResponse) -> dict:
    return json.loads(resp.body.decode("utf-8"))


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


def test_root_mint_requires_spiffe_id(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)

    def call_root_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.root_mint(payload={}, x_spiffe_id=None)
        return exc.value

    exc_value = guard.exercise("call root_mint without spiffe", call_root_mint)
    guard.outcome("status is 401", exc_value.status_code == 401)


def test_root_mint_rejects_invalid_spiffe_id(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)

    def call_root_mint():
        with pytest.raises(capiss_module.HTTPException) as exc:
            capiss_module.root_mint(payload={}, x_spiffe_id="not-spiffe")
        return exc.value

    exc_value = guard.exercise("call root_mint with invalid spiffe", call_root_mint)
    guard.outcome("status is 400", exc_value.status_code == 400)


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
