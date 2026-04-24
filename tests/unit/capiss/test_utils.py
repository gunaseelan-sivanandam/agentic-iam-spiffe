from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
import redis


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


# UT: UT-035
# Test Description: Verifies key material lifecycle.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-111, DD-112, DD-113
def test_key_material_lifecycle(capiss_module, tmp_path, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("set key file paths", lambda: _set_key_paths(capiss_module, tmp_path))

    private_key, created = guard.exercise("create root key", capiss_module.load_or_create_root_private_key)
    guard.outcome("key created", created is True)
    guard.outcome("key file exists", Path(capiss_module.CAPISS_KEY_FILE).exists())

    private_key_2, created_2 = guard.exercise("reload root key", capiss_module.load_or_create_root_private_key)
    guard.outcome("reload does not create new key", created_2 is False)
    guard.outcome("same private key bytes", private_key_2.to_bytes() == private_key.to_bytes())

    needs_update_before = guard.exercise("check public key update before write", lambda: capiss_module.public_key_needs_update(private_key_2))
    guard.exercise("write public key", lambda: capiss_module.write_public_key(private_key_2))
    needs_update_after = guard.exercise("check public key update after write", lambda: capiss_module.public_key_needs_update(private_key_2))
    guard.outcome("update needed before write", needs_update_before is True)
    guard.outcome("no update needed after write", needs_update_after is False)


def _set_key_paths(capiss_module, tmp_path):
    capiss_module.CAPISS_KEY_DIR = str(tmp_path / "keys")
    capiss_module.CAPISS_KEY_FILE = str(Path(capiss_module.CAPISS_KEY_DIR) / "root_key.b64")
    capiss_module.CAPISS_PUBLIC_KEY_FILE = str(Path(capiss_module.CAPISS_KEY_DIR) / "root_public_key.b64")


# UT: UT-036
# Test Description: Verifies parse fact helpers.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-116, DD-117
def test_parse_fact_helpers(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    parsed_string = guard.exercise("parse quoted arg", lambda: capiss_module.parse_fact_arg('"abc"'))
    parsed_number = guard.exercise("parse numeric arg", lambda: capiss_module.parse_fact_arg("123"))
    claims = guard.exercise(
        "parse block source",
        lambda: capiss_module.parse_block_source('sub("spiffe://example.org/agent-a");\nexp(10);\n'),
    )
    guard.outcome("quoted arg parsed", parsed_string == "abc")
    guard.outcome("numeric arg parsed", parsed_number == 123)
    guard.outcome("sub extracted", claims.get("sub") == "spiffe://example.org/agent-a")
    guard.outcome("subject_spiffe_id extracted", claims.get("subject_spiffe_id") == "spiffe://example.org/agent-a")
    guard.outcome("exp extracted", claims.get("exp") == 10)


# UT: UT-037
# Test Description: Verifies mint and parse token round trip.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-119, DD-123
def test_mint_and_parse_token_round_trip(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    token, _, root_token_id, token_id = guard.exercise(
        "mint root biscuit",
        lambda: capiss_module.mint_root_biscuit(
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    biscuit, claims, err = guard.exercise("parse minted token", lambda: capiss_module.parse_token(token))
    guard.outcome("no parse error", err is None)
    guard.outcome("biscuit returned", biscuit is not None)
    guard.outcome("claims returned", claims is not None)
    guard.outcome("root token id preserved", claims is not None and claims.get("root_token_id") == root_token_id)
    guard.outcome("token id preserved", claims is not None and claims.get("token_id") == token_id)
    guard.outcome("effective depth zero", claims is not None and claims.get("effective_depth") == 0)


# UT: UT-038
# Test Description: Verifies append resource token round trip.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-119, DD-124
def test_append_resource_token_round_trip(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    token, _, _, _ = guard.exercise(
        "mint root biscuit",
        lambda: capiss_module.mint_root_biscuit(
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    parent_biscuit, parent_claims, err = guard.exercise("parse root token", lambda: capiss_module.parse_token(token))
    guard.outcome("root parse has no error", err is None)
    guard.outcome("parent biscuit returned", parent_biscuit is not None)
    guard.outcome("parent claims returned", parent_claims is not None)

    delegated, _, child_token_id = guard.exercise(
        "append delegated token",
        lambda: capiss_module.append_resource_token(
            parent_biscuit,
            parent_claims,
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    _, delegated_claims, delegated_err = guard.exercise("parse delegated token", lambda: capiss_module.parse_token(delegated))
    guard.outcome("delegated parse has no error", delegated_err is None)
    guard.outcome("delegated claims returned", delegated_claims is not None)
    guard.outcome("delegated child token id matches", delegated_claims is not None and delegated_claims.get("token_id") == child_token_id)
    guard.outcome(
        "delegated parent token id matches",
        delegated_claims is not None and parent_claims is not None and delegated_claims.get("parent_token_id") == parent_claims.get("token_id"),
    )
    guard.outcome("delegated effective depth one", delegated_claims is not None and delegated_claims.get("effective_depth") == 1)


# UT: UT-039
# Test Description: Verifies that parse token rejects invalid value.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-119
def test_parse_token_rejects_invalid_value(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    biscuit, claims, err = guard.exercise("parse invalid token", lambda: capiss_module.parse_token("not-a-token"))
    guard.outcome("biscuit missing", biscuit is None)
    guard.outcome("claims missing", claims is None)
    guard.outcome("reason invalid_token", err == "invalid_token")


# UT: UT-040
# Test Description: Verifies mark capiss minted token store paths.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-121
def test_mark_capiss_minted_token_store_paths(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class GoodClient:
        def set(self, key, value, ex):
            self.last = (key, value, ex)

    guard.exercise("mock good redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: GoodClient()))
    ok, err = guard.exercise(
        "mark capiss minted token success path",
        lambda: capiss_module.mark_capiss_minted_token("token-1", int(time.time()) + 10),
    )
    guard.outcome("mark success", ok is True)
    guard.outcome("empty error on success", err == "")

    def broken():
        raise redis.RedisError("down")

    guard.exercise("mock broken redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", broken))
    ok, err = guard.exercise(
        "mark capiss minted token failure path",
        lambda: capiss_module.mark_capiss_minted_token("token-1", int(time.time()) + 10),
    )
    guard.outcome("mark fails", ok is False)
    guard.outcome("down error surfaced", err is not None and "down" in err)


# UT: UT-041
# Test Description: Verifies registry has resource store paths.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-122
def test_registry_has_resource_store_paths(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class GoodClient:
        def eval(self, *args):
            return 1

    guard.exercise("mock good registry client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: GoodClient()))
    store_ok, hit, err = guard.exercise(
        "registry hit path",
        lambda: capiss_module.registry_has_resource("root-1", "tool-b:/read-file:fileA"),
    )
    guard.outcome("store ok on hit", store_ok is True)
    guard.outcome("hit true", hit is True)
    guard.outcome("empty error", err == "")

    class BrokenClient:
        def eval(self, *args):
            raise redis.RedisError("down")

    guard.exercise("mock broken registry client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: BrokenClient()))
    store_ok, hit, err = guard.exercise(
        "registry store failure path",
        lambda: capiss_module.registry_has_resource("root-1", "tool-b:/read-file:fileA"),
    )
    guard.outcome("store not ok", store_ok is False)
    guard.outcome("hit false", hit is False)
    guard.outcome("down error surfaced", err is not None and "down" in err)


# UT: UT-128
# Test Description: Verifies that ensure_root_budget initializes only the root budget key and does not seed the discovery registry.
# Precondition: Module fixtures are loaded and the Redis pipeline dependency is replaced with a recording fake.
# Expected Output: The SUT writes exactly the budget key with a TTL and executes the pipeline without any registry writes.
# Covers DD: DD-120
@pytest.mark.invariant
def test_ensure_root_budget_writes_only_budget_key(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    seen: list[tuple] = []

    class RecordingPipeline:
        def set(self, key, value, ex):
            seen.append(("set", key, value, ex))
            return self

        def execute(self):
            seen.append(("execute",))
            return [True]

    class RecordingClient:
        def pipeline(self, transaction=True):
            seen.append(("pipeline", transaction))
            return RecordingPipeline()

    now = int(time.time())
    guard.exercise("mock recording redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: RecordingClient()))
    ok, err = guard.exercise("initialize root budget", lambda: capiss_module.ensure_root_budget("root-1", now + 15))
    guard.outcome("budget init succeeds", ok is True)
    guard.outcome("empty error on success", err == "")
    guard.outcome(
        "only budget write issued",
        len(seen) == 3
        and seen[0] == ("pipeline", True)
        and seen[1][0] == "set"
        and seen[1][1] == "m4:budget:root-1"
        and seen[1][2] == capiss_module.M4_DEFAULT_BUDGET
        and isinstance(seen[1][3], int)
        and seen[1][3] >= 1
        and seen[2] == ("execute",),
    )


# UT: UT-108
# Test Description: Verifies that the capability issuer health endpoint returns the exact ok payload.
# Precondition: Module fixtures are loaded and no additional setup is required.
# Expected Output: The SUT returns exactly `{\"status\": \"ok\"}`.
# Covers DD: DD-107
def test_health_returns_exact_ok_payload(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise("call health endpoint", capiss_module.health)
    guard.outcome("exact ok payload", payload == {"status": "ok"})


# UT: UT-109
# Test Description: Verifies that iso_utc_now returns the exact ISO timestamp from the module-local datetime source.
# Precondition: Module fixtures are loaded and the module-local datetime dependency is stubbed to a fixed UTC instant.
# Expected Output: The SUT returns the exact ISO-8601 string produced by the stubbed datetime object.
# Covers DD: DD-108
@pytest.mark.invariant
def test_iso_utc_now_returns_exact_stubbed_timestamp(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class FixedInstant:
        def isoformat(self):
            return "2026-04-03T10:11:12+00:00"

    class FixedDateTime:
        @staticmethod
        def now(tz):
            return FixedInstant()

    guard.exercise("stub datetime.now", lambda: monkeypatch.setattr(capiss_module, "datetime", FixedDateTime))
    out = guard.exercise("call iso_utc_now", capiss_module.iso_utc_now)
    guard.outcome("exact timestamp returned", out == "2026-04-03T10:11:12+00:00")


# UT: UT-110
# Test Description: Verifies that log_event emits an exact structured JSON audit record using the module-local timestamp helper.
# Precondition: Module fixtures are loaded, the timestamp helper is stubbed to a fixed value, and print output is captured.
# Expected Output: The SUT prints exactly one compact JSON object containing the event type, timestamp, and supplied fields.
# Covers DD: DD-109
@pytest.mark.invariant
def test_log_event_emits_exact_structured_json(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    printed: list[tuple[tuple[object, ...], dict[str, object]]] = []
    guard.exercise("stub audit timestamp", lambda: monkeypatch.setattr(capiss_module, "iso_utc_now", lambda: "2026-04-03T10:11:12+00:00"))
    guard.exercise(
        "capture print",
        lambda: monkeypatch.setattr(capiss_module, "print", lambda *args, **kwargs: printed.append((args, kwargs)), raising=False),
    )
    guard.exercise(
        "emit audit log",
        lambda: capiss_module.log_event("capiss_test", result="ok", reason_code="demo"),
    )
    guard.outcome("single print call", len(printed) == 1)
    guard.outcome(
        "exact print kwargs",
        printed[0][1] == {"flush": True},
    )
    guard.outcome(
        "exact structured payload",
        json.loads(printed[0][0][0])
        == {
            "event_type": "capiss_test",
            "timestamp": "2026-04-03T10:11:12+00:00",
            "result": "ok",
            "reason_code": "demo",
        },
    )


# UT: UT-111
# Test Description: Verifies that get_redis constructs the Redis client once with exact module configuration and then reuses the cached instance.
# Precondition: Module fixtures are loaded, the module cache is empty, and the Redis factory is replaced with a recording stub.
# Expected Output: The SUT calls Redis.from_url exactly once with the configured URL and socket settings, then returns the cached client on subsequent calls.
# Covers DD: DD-114
@pytest.mark.invariant
def test_get_redis_caches_exact_constructed_client(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    client = object()
    guard.exercise("reset redis cache", lambda: monkeypatch.setattr(capiss_module, "_redis_client", None))

    def fake_from_url(*args, **kwargs):
        calls.append((args, kwargs))
        return client

    guard.exercise(
        "capture redis factory",
        lambda: monkeypatch.setattr(capiss_module.redis.Redis, "from_url", fake_from_url),
    )
    first = guard.exercise("get redis first time", capiss_module.get_redis)
    second = guard.exercise("get redis second time", capiss_module.get_redis)
    guard.outcome("cached client returned first time", first is client)
    guard.outcome("cached client returned second time", second is client)
    guard.outcome("factory called once", len(calls) == 1)
    guard.outcome(
        "factory args exact",
        calls[0]
        == (
            (capiss_module.M4_REDIS_URL,),
            {
                "encoding": "utf-8",
                "decode_responses": True,
                "socket_timeout": capiss_module.M4_REDIS_SOCKET_TIMEOUT,
            },
        ),
    )


# UT: UT-042
# Test Description: Verifies that decision input contains optional fields.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_contains_optional_fields(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            root_token_id="root-1",
            registry_hit=True,
        ),
    )
    guard.outcome(
        "exact payload with optionals",
        payload
        == {
            "decision_type": "resource_mint",
            "sub": "spiffe://example.org/agent-a",
            "subject_spiffe_id": "spiffe://example.org/agent-a",
            "aud": "tool-b",
            "act": "read",
            "res": "tool-b:/search",
            "root_token_id": "root-1",
            "registry_hit": True,
        },
    )


# UT: UT-091
# Test Description: Verifies that decision input returns the exact mandatory payload shape without optional fields.
# Precondition: Module fixtures are loaded and the caller provides only the mandatory decision input fields.
# Expected Output: The SUT returns exactly the six mandatory fields, with sub and subject_spiffe_id matching the provided subject.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_returns_exact_base_payload(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build base decision input",
        lambda: capiss_module.decision_input(
            "root_mint",
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome(
        "exact mandatory payload",
        payload
        == {
            "decision_type": "root_mint",
            "sub": "spiffe://example.org/agent-a",
            "subject_spiffe_id": "spiffe://example.org/agent-a",
            "aud": "tool-b",
            "act": "read",
            "res": "tool-b:/search",
        },
    )


# UT: UT-092
# Test Description: Verifies that decision input omits root_token_id when it is not provided.
# Precondition: Module fixtures are loaded and only registry_hit is supplied as an optional field.
# Expected Output: The SUT includes registry_hit and omits root_token_id entirely from the payload.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_omits_root_token_id_when_none(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input without root token",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            registry_hit=False,
        ),
    )
    guard.outcome("root_token_id omitted", "root_token_id" not in payload)
    guard.outcome("registry_hit included", payload == {
        "decision_type": "resource_mint",
        "sub": "spiffe://example.org/agent-a",
        "subject_spiffe_id": "spiffe://example.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "registry_hit": False,
    })


# UT: UT-093
# Test Description: Verifies that decision input omits registry_hit when it is not provided.
# Precondition: Module fixtures are loaded and only root_token_id is supplied as an optional field.
# Expected Output: The SUT includes root_token_id and omits registry_hit entirely from the payload.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_omits_registry_hit_when_none(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input without registry flag",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            root_token_id="root-1",
        ),
    )
    guard.outcome("registry_hit omitted", "registry_hit" not in payload)
    guard.outcome("root_token_id included", payload == {
        "decision_type": "resource_mint",
        "sub": "spiffe://example.org/agent-a",
        "subject_spiffe_id": "spiffe://example.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "root_token_id": "root-1",
    })


# UT: UT-094
# Test Description: Verifies that decision input preserves an explicit false registry_hit value.
# Precondition: Module fixtures are loaded and registry_hit is provided as False.
# Expected Output: The SUT keeps registry_hit in the payload with the exact False value instead of omitting or coercing it.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_preserves_false_registry_hit(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input with false registry flag",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            registry_hit=False,
        ),
    )
    guard.outcome("registry_hit explicitly false", payload.get("registry_hit") is False)
    guard.outcome("subject fields match", payload.get("sub") == payload.get("subject_spiffe_id") == "spiffe://example.org/agent-a")


# UT: UT-043
# Test Description: Verifies that extract chain claims defaults depth when missing.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-118
@pytest.mark.boundary
def test_extract_chain_claims_defaults_depth_when_missing(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    token, _, _, _ = guard.exercise(
        "mint root biscuit",
        lambda: capiss_module.mint_root_biscuit(
            "spiffe://example.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    biscuit = guard.exercise("load biscuit from token", lambda: capiss_module.Biscuit.from_base64(token, capiss_module.ROOT_PUBLIC_KEY))
    chain = guard.exercise("extract chain claims", lambda: capiss_module.extract_chain_claims(biscuit))
    guard.outcome("default delegation depth is zero", chain[0].get("delegation_depth") == 0)


# UT: UT-129
# Test Description: Verifies that capiss consumes mint-rate allowance until the formula-derived limit is reached and then denies.
# Precondition: The Redis dependency is replaced with a deterministic fake that returns three allows followed by one deny for the same root context.
# Expected Output: The SUT returns allow for the first three consumes under a 60-second lifetime and then returns the exact deny reason `mint_rate_exceeded`.
# Covers DD: DD-221
@pytest.mark.boundary
def test_consume_mint_rate_allows_until_formula_limit_then_denies(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class SequenceClient:
        def __init__(self):
            self.calls = 0

        def eval(self, *args):
            self.calls += 1
            if self.calls <= 3:
                return [1, "ok", self.calls]
            return [0, "mint_rate_exceeded", 3]

    client = SequenceClient()
    guard.exercise("mock sequence redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: client))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_000))

    outcomes = [
        guard.exercise(
            f"consume mint rate call {idx}",
            lambda: capiss_module.consume_mint_rate("root-1", 1_060, 60),
        )
        for idx in range(1, 5)
    ]

    guard.outcome("first consume allowed", outcomes[0] == (True, ""))
    guard.outcome("second consume allowed", outcomes[1] == (True, ""))
    guard.outcome("third consume allowed", outcomes[2] == (True, ""))
    guard.outcome("fourth consume denied exactly", outcomes[3] == (False, "mint_rate_exceeded"))


# UT: UT-130
# Test Description: Verifies that capiss passes the exact Redis key, formula-derived allowance, and remaining root TTL to the mint-rate helper.
# Precondition: The Redis dependency is replaced with a recording fake and current time is frozen.
# Expected Output: The SUT calls Redis with key `m4:mint_rate:<root_token_id>`, an allowance of `3` for a 60-second root lifetime, and a TTL equal to the remaining root lifetime.
# Covers DD: DD-221
@pytest.mark.invariant
def test_consume_mint_rate_uses_exact_key_allowance_and_ttl(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    call_args = []

    class RecordingClient:
        def eval(self, *args):
            call_args.append(args)
            return [1, "ok", 1]

    guard.exercise("mock recording redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: RecordingClient()))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_000))
    ok, err = guard.exercise("consume mint rate", lambda: capiss_module.consume_mint_rate("root-7", 1_017, 60))
    guard.outcome("consume succeeds", ok is True)
    guard.outcome("empty error on success", err == "")
    guard.outcome("redis called once", len(call_args) == 1)
    guard.outcome("script uses one key", call_args[0][1] == 1)
    guard.outcome("mint-rate key exact", call_args[0][2] == "m4:mint_rate:root-7")
    guard.outcome("allowance exact", call_args[0][3] == "3")
    guard.outcome("ttl exact", call_args[0][4] == "17")


# UT: UT-131
# Test Description: Verifies that the mint-rate allowance formula scales with root-token lifetime and floors to one.
# Precondition: The Redis dependency is replaced with a recording fake and current time is frozen.
# Expected Output: The SUT passes allowance `2` for 40 seconds, `1` for 20 seconds, and still `1` for lifetimes below 20 seconds.
# Covers DD: DD-221
@pytest.mark.boundary
def test_consume_mint_rate_formula_scales_and_floors_to_one(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    allowances = []

    class RecordingClient:
        def eval(self, *args):
            allowances.append(args[3])
            return [1, "ok", 1]

    guard.exercise("mock recording redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: RecordingClient()))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_000))
    guard.exercise("consume mint rate for 40 second root lifetime", lambda: capiss_module.consume_mint_rate("root-40", 1_030, 40))
    guard.exercise("consume mint rate for 20 second root lifetime", lambda: capiss_module.consume_mint_rate("root-20", 1_020, 20))
    guard.exercise("consume mint rate for 19 second root lifetime", lambda: capiss_module.consume_mint_rate("root-19", 1_019, 19))
    guard.outcome("40 second lifetime yields allowance two", allowances[0] == "2")
    guard.outcome("20 second lifetime yields allowance one", allowances[1] == "1")
    guard.outcome("sub-20 lifetime still yields allowance one", allowances[2] == "1")


# UT: UT-132
# Test Description: Verifies that capiss fails closed when the mint-rate store returns a malformed reply.
# Precondition: The Redis dependency is replaced with a fake that returns a malformed Lua reply shape.
# Expected Output: The SUT returns the exact fail-closed reason `store_unavailable`.
# Covers DD: DD-221
@pytest.mark.invariant
def test_consume_mint_rate_fails_closed_on_malformed_store_reply(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class MalformedClient:
        def eval(self, *args):
            return ["ok"]

    guard.exercise("mock malformed redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: MalformedClient()))
    ok, err = guard.exercise("consume mint rate with malformed reply", lambda: capiss_module.consume_mint_rate("root-1", int(time.time()) + 10, 60))
    guard.outcome("consume denied", ok is False)
    guard.outcome("reason store_unavailable", err == "store_unavailable")


# UT: UT-133
# Test Description: Verifies that capiss fails closed when the mint-rate store raises a Redis error.
# Precondition: The Redis dependency is replaced with a fake that raises `redis.RedisError`.
# Expected Output: The SUT returns the exact fail-closed reason `store_unavailable`.
# Covers DD: DD-221
@pytest.mark.invariant
def test_consume_mint_rate_fails_closed_on_store_error(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class BrokenClient:
        def eval(self, *args):
            raise redis.RedisError("down")

    guard.exercise("mock broken redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: BrokenClient()))
    ok, err = guard.exercise("consume mint rate with store error", lambda: capiss_module.consume_mint_rate("root-1", int(time.time()) + 10, 60))
    guard.outcome("consume denied", ok is False)
    guard.outcome("reason store_unavailable", err == "store_unavailable")
