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


class RecordingRedisClient(FakeRedisClient):
    def __init__(self, result=None, raises=None):
        super().__init__(result=result, raises=raises)
        self.calls = []

    def eval(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return super().eval(*args, **kwargs)


class FakeBiscuitToken:
    pass


def _premise_module_loaded(guard, toolb_module):
    guard.premise("tool-b module loaded", toolb_module is not None)


# UT: UT-044
# Test Description: Verifies consume budget and rate ok.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-203
@pytest.mark.invariant
def test_consume_budget_and_rate_ok(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create redis client returning ok", lambda: FakeRedisClient(result=[1, "ok", 9]))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    result = guard.exercise(
        "consume budget and rate",
        lambda: toolb_module.consume_budget_and_rate("root-1", int(time.time()) + 30),
    )
    guard.outcome("ok tuple exact", result == (True, "ok", 9))


# UT: UT-096
# Test Description: Verifies that consume budget and rate fails closed when the store reply list is too short.
# Precondition: Module fixtures are loaded and the Redis eval result is a list with fewer than three fields.
# Expected Output: The SUT treats the short reply as store_unavailable and returns the standard fail-closed tuple.
# Covers DD: DD-203
@pytest.mark.invariant
def test_consume_budget_and_rate_fail_closed_on_short_store_reply(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create redis client with short reply", lambda: FakeRedisClient(result=[1, "ok"]))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    result = guard.exercise(
        "consume budget and rate with short reply",
        lambda: toolb_module.consume_budget_and_rate("root-1", int(time.time()) + 30),
    )
    guard.outcome("fail closed tuple exact", result == (False, "store_unavailable", -1))


# UT: UT-097
# Test Description: Verifies that consume budget and rate decodes a denied tuple without remapping its reason or remaining budget.
# Precondition: Module fixtures are loaded and the Redis eval result is a valid three-item deny tuple.
# Expected Output: The SUT returns False and preserves the exact reason and remaining values from the store reply.
# Covers DD: DD-203
@pytest.mark.invariant
def test_consume_budget_and_rate_decodes_denied_tuple(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create redis client returning deny", lambda: FakeRedisClient(result=[0, "rate_limited", 0]))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    result = guard.exercise(
        "consume budget and rate denied tuple",
        lambda: toolb_module.consume_budget_and_rate("root-1", int(time.time()) + 30),
    )
    guard.outcome("deny tuple exact", result == (False, "rate_limited", 0))


# UT: UT-045
# Test Description: Verifies consume budget and rate fail closed on redis error.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-203
@pytest.mark.invariant
def test_consume_budget_and_rate_fail_closed_on_redis_error(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create redis client raising error", lambda: FakeRedisClient(raises=redis.RedisError("down")))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    result = guard.exercise(
        "consume budget and rate",
        lambda: toolb_module.consume_budget_and_rate("root-1", int(time.time()) + 30),
    )
    guard.outcome("redis error tuple exact", result == (False, "store_unavailable", -1))


# UT: UT-105
# Test Description: Verifies that consume budget and rate sends the exact Lua script, key count, keys, and argv values to Redis.
# Precondition: Module fixtures are loaded, Redis access is stubbed with a recording client, and time is frozen to a known value.
# Expected Output: The SUT issues exactly one Redis eval call with the canonical script, two keys, expected key names, and expected stringified argv values.
# Covers DD: DD-203
@pytest.mark.invariant
def test_consume_budget_and_rate_issues_exact_eval_call(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create recording redis client", lambda: RecordingRedisClient(result=[1, "ok", 9]))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(toolb_module.time, "time", lambda: 1_000))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    result = guard.exercise("consume budget and rate", lambda: toolb_module.consume_budget_and_rate("root-1", 1_045))
    guard.outcome("ok tuple exact", result == (True, "ok", 9))
    guard.outcome("one eval call recorded", len(client.calls) == 1)
    call_args, call_kwargs = client.calls[0]
    guard.outcome(
        "eval call args exact",
        call_args
        == (
            toolb_module.CONSUME_BUDGET_RATE_LUA,
            2,
            "m4:budget:root-1",
            "m4:rate:root-1",
            str(toolb_module.M4_REQUEST_COST),
            str(toolb_module.M4_RATE_LIMIT),
            str(toolb_module.M4_RATE_WINDOW_SECONDS),
            "45",
        ),
    )
    guard.outcome("eval call kwargs empty", call_kwargs == {})


# UT: UT-106
# Test Description: Verifies that consume budget and rate derives TTL from token expiry and current time before calling Redis.
# Precondition: Module fixtures are loaded, Redis access is stubbed with a recording client, and time is frozen to a known value.
# Expected Output: The SUT passes the exact computed TTL string max(1, exp - now) as the final Redis eval argument.
# Covers DD: DD-203
@pytest.mark.invariant
def test_consume_budget_and_rate_uses_exact_computed_ttl(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create recording redis client", lambda: RecordingRedisClient(result=[1, "ok", 7]))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(toolb_module.time, "time", lambda: 2_000))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    result = guard.exercise("consume budget and rate", lambda: toolb_module.consume_budget_and_rate("root-2", 2_123))
    guard.outcome("ok tuple exact", result == (True, "ok", 7))
    call_args, _ = client.calls[0]
    guard.outcome("ttl arg exact", call_args[-1] == "123")


# UT: UT-107
# Test Description: Verifies that consume budget and rate floors TTL to one second when expiry is not in the future.
# Precondition: Module fixtures are loaded, Redis access is stubbed with a recording client, and time is frozen to a known value after the expiry time.
# Expected Output: The SUT still calls Redis and passes a TTL argument of exactly \"1\".
# Covers DD: DD-203
@pytest.mark.invariant
def test_consume_budget_and_rate_floors_ttl_to_one(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    client = guard.exercise("create recording redis client", lambda: RecordingRedisClient(result=[0, "budget_exceeded", 0]))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(toolb_module.time, "time", lambda: 3_000))
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    result = guard.exercise("consume budget and rate", lambda: toolb_module.consume_budget_and_rate("root-3", 2_999))
    guard.outcome("deny tuple exact", result == (False, "budget_exceeded", 0))
    call_args, _ = client.calls[0]
    guard.outcome("ttl floored to one", call_args[-1] == "1")


# UT: UT-046
# Test Description: Verifies record discovery fails closed on store error.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-204
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
            "spiffe://varambu.org/agent-a",
            ["tool-b:/read-file:fileA"],
            int(time.time()) + 30,
        ),
    )
    guard.outcome("record discovery fails closed", ok is False)


def base_claims(**overrides):
    claims = {
        "subject_spiffe_id": "spiffe://varambu.org/agent-a",
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


# UT: UT-047
# Test Description: Verifies that verify biscuit rejects subject mismatch.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-202
@pytest.mark.invariant
def test_verify_biscuit_rejects_subject_mismatch(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    claims = guard.exercise("build base claims", base_claims)
    guard.exercise("install verify primitives", lambda: install_verify_primitives(toolb_module, monkeypatch, claims))
    allowed, reason, out = guard.exercise(
        "verify biscuit with wrong subject",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://varambu.org/rogue",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason sub_mismatch", reason == "sub_mismatch")
    guard.outcome("claims passthrough", out is claims)


# UT: UT-048
# Test Description: Verifies that verify biscuit rejects expired token.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-202
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
            "spiffe://varambu.org/agent-a",
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
# UT: UT-049
# Test Description: Verifies verify biscuit budget reason mapping.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-202, DD-203
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
            "spiffe://varambu.org/agent-a",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason mapped", reason == expected)
    guard.outcome("claims passthrough", out is claims)


# UT: UT-050
# Test Description: Verifies that verify biscuit allows valid token.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-202, DD-203
def test_verify_biscuit_allows_valid_token(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    claims = guard.exercise("build base claims", base_claims)
    guard.exercise("install verify primitives", lambda: install_verify_primitives(toolb_module, monkeypatch, claims))
    guard.exercise("mock consume success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 8)))
    allowed, reason, out = guard.exercise(
        "verify valid biscuit",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://varambu.org/agent-a",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed true", allowed is True)
    guard.outcome("reason empty", reason == "")
    guard.outcome("budget remaining attached", out.get("budget_remaining") == 8)
