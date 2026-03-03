from __future__ import annotations

import time
from pathlib import Path

import pytest
import redis


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


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


def test_parse_token_rejects_invalid_value(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    biscuit, claims, err = guard.exercise("parse invalid token", lambda: capiss_module.parse_token("not-a-token"))
    guard.outcome("biscuit missing", biscuit is None)
    guard.outcome("claims missing", claims is None)
    guard.outcome("reason invalid_token", err == "invalid_token")


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
    guard.outcome("root token id present", payload.get("root_token_id") == "root-1")
    guard.outcome("registry hit true", payload.get("registry_hit") is True)


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
