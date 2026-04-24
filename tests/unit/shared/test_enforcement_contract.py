from __future__ import annotations

import pytest


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


def _premise_module_loaded(guard, shared_enforcement_module):
    guard.premise("shared enforcement module loaded", shared_enforcement_module is not None)


# UT: UT-118
# Test Description: Verifies that the shared chain contract accepts a valid root token and derives effective depth.
# Precondition: The shared enforcement module is loaded and a valid single-block root token fixture is available.
# Expected Output: The SUT returns normalized claims with effective depth zero and no deny reason.
# Covers DD: DD-220
@pytest.mark.invariant
def test_verify_chain_contract_valid_root(shared_enforcement_module, guard):
    _premise_module_loaded(guard, shared_enforcement_module)
    claims, err = guard.exercise(
        "verify root chain contract",
        lambda: shared_enforcement_module.verify_chain_contract(
            FakeBiscuit([base_root_block()]),
            max_depth=3,
        ),
    )
    guard.outcome("no chain error", err is None)
    guard.outcome("claims returned", claims is not None)
    guard.outcome("effective depth zero", claims is not None and claims["effective_depth"] == 0)


# UT: UT-119
# Test Description: Verifies that the shared chain contract rejects parent linkage mismatch.
# Precondition: The shared enforcement module is loaded and a delegated block with the wrong parent token id is prepared.
# Expected Output: The SUT rejects the chain with the exact invalid_chain reason.
# Covers DD: DD-220
@pytest.mark.invariant
def test_verify_chain_contract_rejects_parent_mismatch(shared_enforcement_module, guard):
    _premise_module_loaded(guard, shared_enforcement_module)
    child = guard.exercise(
        "build child with wrong parent",
        lambda: delegated_block(parent_token_id="wrong-parent"),
    )
    claims, err = guard.exercise(
        "verify parent mismatch contract",
        lambda: shared_enforcement_module.verify_chain_contract(
            FakeBiscuit([base_root_block(), child]),
            max_depth=3,
        ),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("invalid chain reason", err == "invalid_chain")


# UT: UT-120
# Test Description: Verifies that the shared chain contract rejects resource changes unless a transition validator explicitly allows them.
# Precondition: The shared enforcement module is loaded and a delegated block changes the resource relative to its parent.
# Expected Output: The SUT rejects the chain with the exact amplified_authority reason.
# Covers DD: DD-220
@pytest.mark.invariant
def test_verify_chain_contract_rejects_resource_change_without_validator(shared_enforcement_module, guard):
    _premise_module_loaded(guard, shared_enforcement_module)
    child = guard.exercise(
        "build resource-changing child",
        lambda: delegated_block(res="tool-b:/read-file:fileA"),
    )
    claims, err = guard.exercise(
        "verify resource-changing chain without validator",
        lambda: shared_enforcement_module.verify_chain_contract(
            FakeBiscuit([base_root_block(), child]),
            max_depth=3,
        ),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("amplified authority reason", err == "amplified_authority")


# UT: UT-121
# Test Description: Verifies that the shared chain contract delegates resource-transition decisions to the supplied validator.
# Precondition: The shared enforcement module is loaded and a delegated block changes the resource relative to its parent.
# Expected Output: The SUT accepts the chain, returns normalized claims, and invokes the transition validator exactly once.
# Covers DD: DD-220
@pytest.mark.invariant
def test_verify_chain_contract_allows_resource_change_via_validator(shared_enforcement_module, guard):
    _premise_module_loaded(guard, shared_enforcement_module)
    child = guard.exercise(
        "build resource-changing child",
        lambda: delegated_block(res="tool-b:/read-file:fileA"),
    )
    calls: list[tuple[dict[str, str | int], dict[str, str | int]]] = []

    def allow_resource_change(previous, current):
        calls.append((previous, current))
        return True, None

    claims, err = guard.exercise(
        "verify resource-changing chain with validator",
        lambda: shared_enforcement_module.verify_chain_contract(
            FakeBiscuit([base_root_block(), child]),
            max_depth=3,
            allow_resource_transition=allow_resource_change,
        ),
    )
    guard.outcome("no chain error", err is None)
    guard.outcome("claims returned", claims is not None)
    guard.outcome("validator called once", len(calls) == 1)
    guard.outcome("validator sees previous resource", calls and calls[0][0]["res"] == "tool-b:/search")
    guard.outcome("validator sees current resource", calls and calls[0][1]["res"] == "tool-b:/read-file:fileA")


# UT: UT-122
# Test Description: Verifies that the shared chain contract rejects invalid depth metadata.
# Precondition: The shared enforcement module is loaded and a delegated block advertises a depth inconsistent with the chain length.
# Expected Output: The SUT rejects the chain with the exact invalid_depth_metadata reason.
# Covers DD: DD-220
@pytest.mark.boundary
def test_verify_chain_contract_rejects_invalid_depth_metadata(shared_enforcement_module, guard):
    _premise_module_loaded(guard, shared_enforcement_module)
    child = guard.exercise(
        "build child with invalid depth metadata",
        lambda: delegated_block(delegation_depth=9),
    )
    claims, err = guard.exercise(
        "verify invalid depth metadata contract",
        lambda: shared_enforcement_module.verify_chain_contract(
            FakeBiscuit([base_root_block(), child]),
            max_depth=3,
        ),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("invalid depth metadata reason", err == "invalid_depth_metadata")


# UT: UT-123
# Test Description: Verifies that the shared chain contract enforces the configured maximum depth.
# Precondition: The shared enforcement module is loaded and a three-hop delegated chain is prepared while max depth is set below the effective depth.
# Expected Output: The SUT rejects the chain with the exact depth_exceeded reason.
# Covers DD: DD-220
@pytest.mark.boundary
def test_verify_chain_contract_enforces_depth_limit(shared_enforcement_module, guard):
    _premise_module_loaded(guard, shared_enforcement_module)
    chain = guard.exercise(
        "build over-depth chain",
        lambda: [
            base_root_block(),
            delegated_block(token_id="token-1", parent_token_id="token-root", delegation_depth=1),
            delegated_block(token_id="token-2", parent_token_id="token-1", delegation_depth=2),
        ],
    )
    claims, err = guard.exercise(
        "verify over-depth contract",
        lambda: shared_enforcement_module.verify_chain_contract(
            FakeBiscuit(chain),
            max_depth=1,
        ),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("depth exceeded reason", err == "depth_exceeded")


# UT: UT-124
# Test Description: Verifies that the shared chain contract rejects expiry extension relative to the parent token.
# Precondition: The shared enforcement module is loaded and a delegated block advertises a later expiry than its parent.
# Expected Output: The SUT rejects the chain with the exact amplified_authority reason.
# Covers DD: DD-220
@pytest.mark.invariant
def test_verify_chain_contract_rejects_expiry_extension(shared_enforcement_module, guard):
    _premise_module_loaded(guard, shared_enforcement_module)
    child = guard.exercise(
        "build child with later expiry",
        lambda: delegated_block(exp=2_000_000_100),
    )
    claims, err = guard.exercise(
        "verify expiry-extending chain",
        lambda: shared_enforcement_module.verify_chain_contract(
            FakeBiscuit([base_root_block(), child]),
            max_depth=3,
        ),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("amplified authority reason", err == "amplified_authority")
