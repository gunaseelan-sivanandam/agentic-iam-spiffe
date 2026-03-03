from __future__ import annotations

from collections import defaultdict

import pytest


SPIFFE_ID = "spiffe://example.org/agent-a"


class FakePipeline:
    def __init__(self, store: dict[str, object]):
        self.store = store
        self.ops: list[tuple] = []

    def set(self, key, value, ex=None):
        self.ops.append(("set", key, str(value), ex))
        return self

    def sadd(self, key, value):
        self.ops.append(("sadd", key, value))
        return self

    def expire(self, key, ttl):
        self.ops.append(("expire", key, ttl))
        return self

    def execute(self):
        for op in self.ops:
            name = op[0]
            if name == "set":
                _, key, value, _ = op
                self.store[key] = value
            elif name == "sadd":
                _, key, value = op
                bucket = self.store.setdefault(key, set())
                assert isinstance(bucket, set)
                bucket.add(value)
            elif name == "expire":
                continue
        self.ops.clear()
        return True


class FakeRedis:
    def __init__(self):
        self.store: dict[str, object] = defaultdict(set)

    def pipeline(self, transaction=True):
        return FakePipeline(self.store)

    def set(self, key, value, ex=None):
        self.store[key] = str(value)
        return True

    def eval(self, script, numkeys, *args):
        # registry_has_resource calls: eval(script, 1, registry_key, res)
        if "SISMEMBER" in script:
            key = args[0]
            value = args[1]
            bucket = self.store.get(key, set())
            return 1 if value in bucket else 0
        return 0

    def add_registry_item(self, root_token_id: str, resource: str):
        key = f"m4:registry:{root_token_id}"
        bucket = self.store.setdefault(key, set())
        assert isinstance(bucket, set)
        bucket.add(resource)


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


@pytest.mark.hybrid_critical
def test_root_mint_hybrid_with_real_token_logic(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    fake_redis = guard.exercise("create fake redis", FakeRedis)
    guard.exercise("mock redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: fake_redis))
    guard.exercise("mock opa allow", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda *_: (True, None)))

    out = guard.exercise(
        "mint root token",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    guard.outcome("token returned", bool(out.get("token")))
    guard.outcome("root token id returned", bool(out.get("root_token_id")))
    guard.outcome("token id returned", bool(out.get("token_id")))
    guard.outcome("depth is zero", out.get("delegation_depth") == 0)


@pytest.mark.hybrid_critical
def test_resource_mint_hybrid_new_resource_with_registry(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    fake_redis = guard.exercise("create fake redis", FakeRedis)
    guard.exercise("mock redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: fake_redis))
    guard.exercise("mock opa allow", lambda: monkeypatch.setattr(capiss_module, "check_opa_allow", lambda *_: (True, None)))

    root = guard.exercise(
        "mint root token",
        lambda: capiss_module.root_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/search"},
            x_spiffe_id=SPIFFE_ID,
        ),
    )
    root_token = root["token"]
    root_token_id = root["root_token_id"]
    guard.exercise("seed registry with discovered resource", lambda: fake_redis.add_registry_item(root_token_id, "tool-b:/read-file:fileA"))

    child = guard.exercise(
        "mint resource token",
        lambda: capiss_module.resource_mint(
            payload={"aud": "tool-b", "act": "read", "res": "tool-b:/read-file:fileA"},
            x_spiffe_id=SPIFFE_ID,
            authorization=f"Bearer {root_token}",
        ),
    )
    guard.outcome("child token returned", bool(child.get("token")))
    guard.outcome("root token id preserved", child.get("root_token_id") == root_token_id)
    guard.outcome("parent id matches root token id", child.get("parent_token_id") == root["token_id"])
    guard.outcome("delegation depth is one", child.get("delegation_depth") == 1)
