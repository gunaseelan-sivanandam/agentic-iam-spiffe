from __future__ import annotations

import time

import pytest
import redis


class FakeRedisClient:
    def __init__(self, result=None, raises=None):
        self.result = result
        self.raises = raises

    def eval(self, *args, **kwargs):
        if self.raises:
            raise self.raises
        return self.result


class FakeBiscuitToken:
    pass


def _premise_module_loaded(guard, toolb_module):
    guard.premise("tool-b module loaded", toolb_module is not None)


def test_consume_budget_and_rate_ok(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create redis client returning ok", lambda: FakeRedisClient(result=[1, "ok", 9]))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    allowed, reason, remaining = guard.exercise(
        "consume budget and rate",
        lambda: toolb_module.consume_budget_and_rate("root-1", int(time.time()) + 30),
    )
    guard.outcome("allowed true", allowed is True)
    guard.outcome("reason ok", reason == "ok")
    guard.outcome("remaining budget 9", remaining == 9)


@pytest.mark.invariant
def test_consume_budget_and_rate_fail_closed_on_redis_error(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create redis client raising error", lambda: FakeRedisClient(raises=redis.RedisError("down")))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    allowed, reason, remaining = guard.exercise(
        "consume budget and rate",
        lambda: toolb_module.consume_budget_and_rate("root-1", int(time.time()) + 30),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason store_unavailable", reason == "store_unavailable")
    guard.outcome("remaining -1", remaining == -1)


@pytest.mark.invariant
def test_record_discovery_fails_closed_on_store_error(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class BrokenClient:
        def eval(self, *args, **kwargs):
            raise redis.RedisError("down")

    guard.exercise("mock broken redis client", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: BrokenClient()))
    ok = guard.exercise(
        "record discovery",
        lambda: toolb_module.record_discovery(
            "root-1",
            "spiffe://example.org/agent-a",
            ["tool-b:/read-file:fileA"],
            int(time.time()) + 30,
        ),
    )
    guard.outcome("record discovery fails closed", ok is False)


def base_claims(**overrides):
    claims = {
        "subject_spiffe_id": "spiffe://example.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "exp": 2_000_000_000,
        "root_token_id": "root-1",
        "token_id": "token-1",
        "effective_depth": 0,
    }
    claims.update(overrides)
    return claims


def install_verify_primitives(toolb_module, monkeypatch, claims):
    monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: object())
    monkeypatch.setattr(toolb_module.Biscuit, "from_base64", lambda *_: FakeBiscuitToken())
    monkeypatch.setattr(toolb_module, "verify_chain_and_claims", lambda *_: (claims, ""))


@pytest.mark.invariant
def test_verify_biscuit_rejects_subject_mismatch(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    claims = guard.exercise("build base claims", base_claims)
    guard.exercise("install verify primitives", lambda: install_verify_primitives(toolb_module, monkeypatch, claims))
    allowed, reason, out = guard.exercise(
        "verify biscuit with wrong subject",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://example.org/rogue",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason sub_mismatch", reason == "sub_mismatch")
    guard.outcome("claims passthrough", out is claims)


@pytest.mark.boundary
def test_verify_biscuit_rejects_expired_token(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    now = 1_700_000_000
    claims = guard.exercise("build expired claims", lambda: base_claims(exp=now))
    guard.exercise("install verify primitives", lambda: install_verify_primitives(toolb_module, monkeypatch, claims))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(toolb_module.time, "time", lambda: now))
    allowed, reason, out = guard.exercise(
        "verify expired token",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://example.org/agent-a",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason expired", reason == "expired")
    guard.outcome("claims passthrough", out is claims)


@pytest.mark.invariant
@pytest.mark.parametrize(
    ("budget_reason", "expected"),
    [
        ("rate_limited", "rate_limited"),
        ("budget_exceeded", "budget_exceeded"),
        ("missing_budget", "budget_exceeded"),
        ("invalid_budget", "budget_exceeded"),
        ("store_unavailable", "store_unavailable"),
    ],
)
def test_verify_biscuit_budget_reason_mapping(toolb_module, monkeypatch, budget_reason, expected, guard):
    _premise_module_loaded(guard, toolb_module)
    claims = guard.exercise("build base claims", base_claims)
    guard.exercise("install verify primitives", lambda: install_verify_primitives(toolb_module, monkeypatch, claims))
    guard.exercise(
        "mock budget consume result",
        lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (False, budget_reason, -1)),
    )
    allowed, reason, out = guard.exercise(
        "verify biscuit with budget mapping",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://example.org/agent-a",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason mapped", reason == expected)
    guard.outcome("claims passthrough", out is claims)


def test_verify_biscuit_allows_valid_token(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    claims = guard.exercise("build base claims", base_claims)
    guard.exercise("install verify primitives", lambda: install_verify_primitives(toolb_module, monkeypatch, claims))
    guard.exercise("mock consume success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 8)))
    allowed, reason, out = guard.exercise(
        "verify valid biscuit",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://example.org/agent-a",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed true", allowed is True)
    guard.outcome("reason empty", reason == "")
    guard.outcome("budget remaining attached", out.get("budget_remaining") == 8)
