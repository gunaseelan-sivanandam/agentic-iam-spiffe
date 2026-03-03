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


def test_run_policy_or_fail_allows_when_opa_allows(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("mock opa allow", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda _: (True, None)))
    ok, fail = guard.exercise("run policy", lambda: capiss_module.run_policy_or_fail({"aud": "tool-b"}))
    guard.outcome("policy allowed", ok is True)
    guard.outcome("no failure response", fail is None)


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


@pytest.mark.invariant
def test_run_policy_or_fail_fail_closed_when_opa_unavailable(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("mock opa unavailable", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda _: (None, "down")))
    ok, fail = guard.exercise("run policy with opa down", lambda: capiss_module.run_policy_or_fail({"aud": "tool-b"}))
    body = guard.exercise("decode policy failure body", lambda: json.loads(fail.body.decode("utf-8")) if fail is not None else {})
    guard.outcome("policy denied", ok is False)
    guard.outcome("failure response present", fail is not None)
    guard.outcome("status 503", fail is not None and fail.status_code == 503)
    guard.outcome("reason opa_unavailable", body.get("reason") == "opa_unavailable")


@pytest.mark.invariant
def test_run_policy_or_fail_denies_when_policy_denies(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("mock opa deny", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda _: (False, None)))
    ok, fail = guard.exercise("run policy with deny", lambda: capiss_module.run_policy_or_fail({"aud": "tool-b"}))
    body = guard.exercise("decode deny body", lambda: json.loads(fail.body.decode("utf-8")) if fail is not None else {})
    guard.outcome("policy denied", ok is False)
    guard.outcome("failure response present", fail is not None)
    guard.outcome("status 403", fail is not None and fail.status_code == 403)
    guard.outcome("reason policy", body.get("reason") == "policy")


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
            "tool-b:/search",
        ),
    )
    guard.outcome("budget check fails", ok is False)
    guard.outcome("redis error surfaced", err is not None and "redis down" in err)
