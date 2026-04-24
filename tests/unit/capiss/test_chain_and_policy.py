from __future__ import annotations

import json
import time

import pytest
import redis


class FakeBiscuit:
    def __init__(self, blocks: list[str]):
        self._blocks = blocks

    def block_count(self) -> int:
        return len(self._blocks)

    def block_source(self, idx: int) -> str:
        return self._blocks[idx]


def fact_block(**kwargs) -> str:
    lines: list[str] = []
    for key, value in kwargs.items():
        if isinstance(value, str):
            lines.append(f'{key}("{value}");')
        else:
            lines.append(f"{key}({value});")
    return "\n".join(lines)


def base_root_block(**overrides) -> str:
    data = {
        "root_token_id": "root-1",
        "token_id": "token-root",
        "subject_spiffe_id": "spiffe://example.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "exp": 2_000_000_000,
        "delegation_depth": 0,
    }
    data.update(overrides)
    return fact_block(**data)


def delegated_block(**overrides) -> str:
    data = {
        "root_token_id": "root-1",
        "token_id": "token-child",
        "parent_token_id": "token-root",
        "delegator_spiffe_id": "spiffe://example.org/agent-a",
        "subject_spiffe_id": "spiffe://example.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "exp": 2_000_000_000,
        "delegation_depth": 1,
    }
    data.update(overrides)
    return fact_block(**data)


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


# UT: UT-003
# Test Description: Verifies that verify and extract chain valid root.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-102
@pytest.mark.invariant
def test_verify_and_extract_chain_valid_root(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    out = guard.exercise(
        "verify and extract root chain",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit([base_root_block()])),
    )
    claims, err = out
    guard.outcome("no chain error", err is None)
    guard.outcome("claims returned", claims is not None)
    guard.outcome("root token id matches", claims is not None and claims["root_token_id"] == "root-1")
    guard.outcome("effective depth is zero", claims is not None and claims["effective_depth"] == 0)


# UT: UT-004
# Test Description: Verifies verify and extract chain missing metadata.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-102
@pytest.mark.invariant
def test_verify_and_extract_chain_missing_metadata(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    block = guard.exercise("build block missing exp", lambda: base_root_block().replace('exp(2000000000);', ""))
    claims, err = guard.exercise(
        "verify malformed chain",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit([block])),
    )
    guard.outcome("claims missing", claims is None)
    guard.outcome("missing metadata reason", err == "missing_chain_metadata")


# UT: UT-005
# Test Description: Verifies that verify and extract chain rejects parent mismatch.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-102
@pytest.mark.invariant
def test_verify_and_extract_chain_rejects_parent_mismatch(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    child = guard.exercise("create child with wrong parent", lambda: delegated_block(parent_token_id="wrong-parent"))
    claims, err = guard.exercise(
        "verify parent mismatch chain",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("invalid chain reason", err == "invalid_chain")


# UT: UT-006
# Test Description: Verifies that verify and extract chain rejects amplified authority.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-102
@pytest.mark.invariant
def test_verify_and_extract_chain_rejects_amplified_authority(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    child = guard.exercise("create amplified child", lambda: delegated_block(aud="tool-c"))
    claims, err = guard.exercise(
        "verify amplified chain",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("amplified authority reason", err == "amplified_authority")


# UT: UT-007
# Test Description: Verifies that verify and extract chain rejects invalid depth metadata.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-102
@pytest.mark.boundary
def test_verify_and_extract_chain_rejects_invalid_depth_metadata(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    child = guard.exercise("create child with invalid depth", lambda: delegated_block(delegation_depth=9))
    claims, err = guard.exercise(
        "verify invalid depth chain",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("invalid depth metadata reason", err == "invalid_depth_metadata")


# UT: UT-008
# Test Description: Verifies that verify and extract chain enforces depth limit.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-102
@pytest.mark.boundary
def test_verify_and_extract_chain_enforces_depth_limit(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("set max depth to 1", lambda: setattr(capiss_module, "M4_MAX_DEPTH", 1))
    chain = guard.exercise(
        "build depth-exceeding chain",
        lambda: [
            base_root_block(),
            delegated_block(token_id="token-1", parent_token_id="token-root", delegation_depth=1),
            delegated_block(token_id="token-2", parent_token_id="token-1", delegation_depth=2),
        ],
    )
    claims, err = guard.exercise(
        "verify depth exceeding chain",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit(chain)),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("depth exceeded reason", err == "depth_exceeded")


# UT: UT-125
# Test Description: Verifies that the capiss chain verifier delegates to the shared enforcement contract and preserves its deny reason.
# Precondition: Module fixtures are loaded and the shared contract symbol is stubbed to deny the presented chain.
# Expected Output: The SUT returns no claims and preserves the exact deny reason from the shared contract.
# Covers DD: DD-102
@pytest.mark.invariant
def test_verify_and_extract_chain_uses_shared_contract(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise(
        "mock shared contract deny",
        lambda: monkeypatch.setattr(
            capiss_module,
            "verify_chain_contract",
            lambda *_args, **_kwargs: (None, "invalid_chain"),
        ),
    )
    claims, err = guard.exercise(
        "verify chain through capiss adapter",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit([base_root_block()])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("shared deny reason preserved", err == "invalid_chain")


# UT: UT-127
# Test Description: Verifies that the capiss chain verifier accepts a capiss-minted delegated resource transition when the delegation marker exists.
# Precondition: Module fixtures are loaded and Redis lookup for the delegated child token returns the capiss-minted marker.
# Expected Output: The SUT returns normalized claims for the delegated child instead of rejecting the resource transition as amplified authority.
# Covers DD: DD-102
@pytest.mark.invariant
def test_verify_and_extract_chain_allows_capiss_marked_resource_transition(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    marker_keys: list[str] = []

    class FakeRedis:
        def get(self, key: str):
            marker_keys.append(key)
            return b"1"

    child = guard.exercise(
        "create delegated child with discovered file resource",
        lambda: delegated_block(
            token_id="token-child",
            parent_token_id="token-root",
            res="tool-b:/read-file:fileA",
        ),
    )
    guard.exercise("mock redis marker lookup", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: FakeRedis()))
    claims, err = guard.exercise(
        "verify capiss-marked resource transition chain",
        lambda: capiss_module.verify_and_extract_chain(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("no chain error", err is None)
    guard.outcome("claims returned", claims is not None)
    guard.outcome("delegated resource preserved", claims is not None and claims["res"] == "tool-b:/read-file:fileA")
    guard.outcome("delegated depth one", claims is not None and claims["effective_depth"] == 1)
    guard.outcome("marker checked for child token", marker_keys == ["m4:capiss_minted:token-child"])


# UT: UT-009
# Test Description: Verifies that run policy or fail allows when opa allows.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-103
@pytest.mark.invariant
def test_run_policy_or_fail_allows_when_opa_allows(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    log_calls: list[tuple[object, dict[str, object]]] = []
    guard.exercise("mock opa allow", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda _: (True, None)))
    guard.exercise(
        "capture policy logs",
        lambda: monkeypatch.setattr(
            capiss_module,
            "log_event",
            lambda event, **kwargs: log_calls.append((event, kwargs)),
        ),
    )
    ok, fail = guard.exercise("run policy", lambda: capiss_module.run_policy_or_fail({"aud": "tool-b"}))
    guard.outcome("policy allowed", ok is True)
    guard.outcome("no failure response", fail is None)
    guard.outcome("allow path does not log", log_calls == [])


# UT: UT-010
# Test Description: Verifies that check opa allow success.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-110
@pytest.mark.invariant
def test_check_opa_allow_success(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"result": true}'

    guard.exercise(
        "mock opa response",
        lambda: monkeypatch.setattr(capiss_module.request, "urlopen", lambda *args, **kwargs: FakeResp()),
    )
    allowed, err = guard.exercise(
        "check opa allow",
        lambda: capiss_module.check_opa_allow({"sub": "spiffe://example.org/agent-a"}),
    )
    guard.outcome("opa allow true", allowed is True)
    guard.outcome("no opa error", err is None)


# UT: UT-086
# Test Description: Verifies that check opa allow fails closed when OPA returns invalid JSON.
# Precondition: Module fixtures are loaded and the OPA client call is stubbed to return malformed JSON bytes.
# Expected Output: The SUT returns an indeterminate allow decision and captures the JSON parsing error text.
# Covers DD: DD-110
@pytest.mark.invariant
def test_check_opa_allow_fail_closed_on_invalid_json(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"{invalid-json"

    guard.exercise(
        "mock invalid opa json",
        lambda: monkeypatch.setattr(capiss_module.request, "urlopen", lambda *args, **kwargs: FakeResp()),
    )
    allowed, err = guard.exercise(
        "check opa allow with invalid json",
        lambda: capiss_module.check_opa_allow({"sub": "spiffe://example.org/agent-a"}),
    )
    guard.outcome("allow is indeterminate", allowed is None)
    guard.outcome("json error captured", err is not None and "Expecting property name enclosed in double quotes" in err)


# UT: UT-011
# Test Description: Verifies check opa allow fail closed on transport error.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-110
@pytest.mark.invariant
def test_check_opa_allow_fail_closed_on_transport_error(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    def raise_error(*args, **kwargs):
        raise capiss_module.URLError("down")

    guard.exercise("mock opa transport error", lambda: monkeypatch.setattr(capiss_module.request, "urlopen", raise_error))
    allowed, err = guard.exercise(
        "check opa allow with transport error",
        lambda: capiss_module.check_opa_allow({"sub": "spiffe://example.org/agent-a"}),
    )
    guard.outcome("allow is indeterminate", allowed is None)
    guard.outcome("transport error captured", err is not None and "down" in err)


# UT: UT-012
# Test Description: Verifies run policy or fail fail closed when opa unavailable.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-103
@pytest.mark.invariant
def test_run_policy_or_fail_fail_closed_when_opa_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    policy_input = {"aud": "tool-b"}
    log_calls: list[tuple[object, dict[str, object]]] = []
    guard.exercise("mock opa unavailable", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda _: (None, "down")))
    guard.exercise(
        "capture policy logs",
        lambda: monkeypatch.setattr(
            capiss_module,
            "log_event",
            lambda event, **kwargs: log_calls.append((event, kwargs)),
        ),
    )
    ok, fail = guard.exercise("run policy with opa down", lambda: capiss_module.run_policy_or_fail(policy_input))
    body = guard.exercise("decode policy failure body", lambda: json.loads(fail.body.decode("utf-8")) if fail is not None else {})
    guard.outcome("policy denied", ok is False)
    guard.outcome("failure response present", fail is not None)
    guard.outcome("status 503", fail is not None and fail.status_code == 503)
    guard.outcome("exact opa unavailable body", body == {"error": "denied", "reason": "opa_unavailable"})
    guard.outcome(
        "exact opa unavailable log event",
        log_calls
        == [
            (
                "capiss_policy_error",
                {
                    "result": "deny",
                    "reason_code": "opa_unavailable",
                    "policy_input": policy_input,
                    "error": "down",
                },
            )
        ],
    )


# UT: UT-013
# Test Description: Verifies that run policy or fail denies when policy denies.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-103
@pytest.mark.invariant
def test_run_policy_or_fail_denies_when_policy_denies(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    policy_input = {"aud": "tool-b"}
    log_calls: list[tuple[object, dict[str, object]]] = []
    guard.exercise("mock opa deny", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda _: (False, None)))
    guard.exercise(
        "capture policy logs",
        lambda: monkeypatch.setattr(
            capiss_module,
            "log_event",
            lambda event, **kwargs: log_calls.append((event, kwargs)),
        ),
    )
    ok, fail = guard.exercise("run policy with deny", lambda: capiss_module.run_policy_or_fail(policy_input))
    body = guard.exercise("decode deny body", lambda: json.loads(fail.body.decode("utf-8")) if fail is not None else {})
    guard.outcome("policy denied", ok is False)
    guard.outcome("failure response present", fail is not None)
    guard.outcome("status 403", fail is not None and fail.status_code == 403)
    guard.outcome("exact policy deny body", body == {"error": "denied", "reason": "policy"})
    guard.outcome(
        "exact policy deny log event",
        log_calls
        == [
            (
                "capiss_policy_decision",
                {
                    "result": "deny",
                    "reason_code": "policy",
                    "policy_input": policy_input,
                    "policy_id": "capiss.allow.v2",
                    "policy_hash": "sha256:capiss-policy-v2",
                },
            )
        ],
    )


# UT: UT-095
# Test Description: Verifies that run policy or fail forwards the policy input to the OPA client unchanged.
# Precondition: Module fixtures are loaded and check_opa_allow is replaced with a capturing stub.
# Expected Output: The SUT passes the exact policy input through to check_opa_allow and returns the allow path result without modification.
# Covers DD: DD-103
@pytest.mark.invariant
def test_run_policy_or_fail_forwards_policy_input_unchanged(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    policy_input = {
        "decision_type": "resource_mint",
        "sub": "spiffe://example.org/agent-a",
        "subject_spiffe_id": "spiffe://example.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "root_token_id": "root-1",
        "registry_hit": True,
    }
    seen = {}

    def fake_check_opa_allow(payload):
        seen["payload"] = payload
        return True, None

    guard.exercise("install capturing opa stub", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", fake_check_opa_allow))
    ok, fail = guard.exercise("run policy", lambda: capiss_module.run_policy_or_fail(policy_input))
    guard.outcome("policy allowed", ok is True)
    guard.outcome("no failure response", fail is None)
    guard.outcome("policy input forwarded unchanged", seen.get("payload") == policy_input)


# UT: UT-098
# Test Description: Verifies that check opa allow builds a POST JSON request that wraps the payload under input.
# Precondition: Module fixtures are loaded and urlopen is replaced with a capturing stub response.
# Expected Output: The SUT sends a POST request with application/json content type, wraps the payload under input, and returns a successful allow decision.
# Covers DD: DD-110
@pytest.mark.invariant
def test_check_opa_allow_builds_post_json_request(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    captured = {}
    payload = {"sub": "spiffe://example.org/agent-a", "aud": "tool-b"}

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"result": true}'

    def fake_urlopen(req, timeout=None):
        captured["method"] = req.get_method()
        captured["headers"] = dict(req.header_items())
        captured["body"] = req.data.decode("utf-8")
        captured["timeout"] = timeout
        return FakeResp()

    guard.exercise("capture outgoing opa request", lambda: monkeypatch.setattr(capiss_module.request, "urlopen", fake_urlopen))
    allowed, err = guard.exercise("check opa allow", lambda: capiss_module.check_opa_allow(payload))
    guard.outcome("allow returned true", allowed is True)
    guard.outcome("no opa error", err is None)
    guard.outcome("request method is post", captured.get("method") == "POST")
    guard.outcome(
        "content type json",
        any(key.lower() == "content-type" and value == "application/json" for key, value in captured.get("headers", {}).items()),
    )
    guard.outcome("payload wrapped under input", json.loads(captured.get("body", "{}")) == {"input": payload})
    guard.outcome("timeout forwarded", captured.get("timeout") == capiss_module.OPA_TIMEOUT_SECONDS)


# UT: UT-099
# Test Description: Verifies that check opa allow returns a concrete false decision when OPA denies.
# Precondition: Module fixtures are loaded and the OPA client call is stubbed to return a valid JSON deny decision.
# Expected Output: The SUT returns False with no error for an explicit false policy result.
# Covers DD: DD-110
@pytest.mark.invariant
def test_check_opa_allow_returns_false_on_explicit_deny(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"result": false}'

    guard.exercise(
        "mock opa deny response",
        lambda: monkeypatch.setattr(capiss_module.request, "urlopen", lambda *args, **kwargs: FakeResp()),
    )
    allowed, err = guard.exercise("check opa deny", lambda: capiss_module.check_opa_allow({"sub": "spiffe://example.org/agent-a"}))
    guard.outcome("allow false", allowed is False)
    guard.outcome("no error on deny", err is None)


# UT: UT-100
# Test Description: Verifies that check opa allow defaults a missing result field to false rather than failing closed.
# Precondition: Module fixtures are loaded and the OPA client call is stubbed to return a valid JSON body without result.
# Expected Output: The SUT returns False with no error when result is absent from the OPA response body.
# Covers DD: DD-110
@pytest.mark.invariant
def test_check_opa_allow_missing_result_defaults_false(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{}'

    guard.exercise(
        "mock opa response missing result",
        lambda: monkeypatch.setattr(capiss_module.request, "urlopen", lambda *args, **kwargs: FakeResp()),
    )
    allowed, err = guard.exercise("check opa missing result", lambda: capiss_module.check_opa_allow({"sub": "spiffe://example.org/agent-a"}))
    guard.outcome("allow defaults false", allowed is False)
    guard.outcome("no error for missing result", err is None)


# UT: UT-014
# Test Description: Verifies ensure root budget fails closed on store error.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-120
@pytest.mark.invariant
def test_ensure_root_budget_fails_closed_on_store_error(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    def broken_client():
        raise redis.RedisError("redis down")

    guard.exercise("mock redis down", lambda: monkeypatch.setattr(capiss_module, "get_redis", broken_client))
    ok, err = guard.exercise(
        "ensure root budget",
        lambda: capiss_module.ensure_root_budget(
            "root-1",
            int(time.time()) + 30,
        ),
    )
    guard.outcome("budget check fails", ok is False)
    guard.outcome("redis error surfaced", err is not None and "redis down" in err)
