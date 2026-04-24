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


def _premise_module_loaded(guard, toolb_module):
    guard.premise("tool-b module loaded", toolb_module is not None)


@pytest.mark.boundary
@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/secret", ("read", "tool-b:/secret")),
        ("/search", ("read", "tool-b:/search")),
        ("/read-file/fileA", ("read", "tool-b:/read-file:fileA")),
        ("/read-file/file A", None),
        ("/read-file/file/A", None),
        ("/unknown", None),
    ],
)
# UT: UT-051
# Test Description: Verifies canonical res for path across the parameterized matrix covered by this test.
# Precondition: Module fixtures are loaded and the parameterized case input is available for the current test iteration.
# Expected Output: Each parameterized case produces the expected result asserted by the outcome guards.
# Covers DD: DD-216
def test_canonical_res_for_path_matrix(toolb_module, path: str, expected, guard):
    _premise_module_loaded(guard, toolb_module)
    out = guard.exercise("canonicalize request path", lambda: toolb_module.canonical_res_for_path(path))
    guard.outcome("canonical mapping matches expected", out == expected)


# UT: UT-052
# Test Description: Verifies that verify chain and claims valid root.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-201
@pytest.mark.invariant
def test_verify_chain_and_claims_valid_root(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    claims, err = guard.exercise(
        "verify root chain",
        lambda: toolb_module.verify_chain_and_claims(FakeBiscuit([base_root_block()])),
    )
    guard.outcome("no chain error", err == "")
    guard.outcome("claims returned", claims is not None)
    guard.outcome("effective depth zero", claims is not None and claims.get("effective_depth") == 0)


# UT: UT-053
# Test Description: Verifies that verify chain and claims rejects amplification.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-201
@pytest.mark.invariant
def test_verify_chain_and_claims_rejects_amplification(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    child = guard.exercise("build amplified child", lambda: delegated_block(aud="other-tool"))
    claims, err = guard.exercise(
        "verify amplified chain",
        lambda: toolb_module.verify_chain_and_claims(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("reason amplified_authority", err == "amplified_authority")


# UT: UT-054
# Test Description: Verifies that verify chain and claims rejects res change without marker.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-201, DD-205
@pytest.mark.invariant
def test_verify_chain_and_claims_rejects_res_change_without_marker(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    child = guard.exercise("build child with changed resource", lambda: delegated_block(res="tool-b:/read-file:fileA"))
    guard.exercise("mock capiss marker miss", lambda: monkeypatch.setattr(toolb_module, "is_capiss_minted_token", lambda *_: (True, False)))
    claims, err = guard.exercise(
        "verify resource-changing chain",
        lambda: toolb_module.verify_chain_and_claims(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("reason amplified_authority", err == "amplified_authority")


# UT: UT-055
# Test Description: Verifies verify chain and claims fail closed if marker store unavailable.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-201, DD-205
@pytest.mark.invariant
def test_verify_chain_and_claims_fail_closed_if_marker_store_unavailable(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    child = guard.exercise("build child with changed resource", lambda: delegated_block(res="tool-b:/read-file:fileA"))
    guard.exercise("mock marker store unavailable", lambda: monkeypatch.setattr(toolb_module, "is_capiss_minted_token", lambda *_: (False, False)))
    claims, err = guard.exercise(
        "verify chain with marker store failure",
        lambda: toolb_module.verify_chain_and_claims(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("reason store_unavailable", err == "store_unavailable")


# UT: UT-056
# Test Description: Verifies that verify chain and claims rejects invalid depth metadata.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-201
@pytest.mark.boundary
def test_verify_chain_and_claims_rejects_invalid_depth_metadata(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    child = guard.exercise("build child with invalid depth", lambda: delegated_block(delegation_depth=7))
    claims, err = guard.exercise(
        "verify chain with invalid depth metadata",
        lambda: toolb_module.verify_chain_and_claims(FakeBiscuit([base_root_block(), child])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("reason invalid_depth_metadata", err == "invalid_depth_metadata")


# UT: UT-057
# Test Description: Verifies that verify chain and claims enforces depth limit.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-201
@pytest.mark.boundary
def test_verify_chain_and_claims_enforces_depth_limit(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    guard.exercise("set max depth to 1", lambda: setattr(toolb_module, "M4_MAX_DEPTH", 1))
    chain = guard.exercise(
        "build over-depth chain",
        lambda: [
            base_root_block(),
            delegated_block(token_id="token-1", parent_token_id="token-root", delegation_depth=1),
            delegated_block(token_id="token-2", parent_token_id="token-1", delegation_depth=2),
        ],
    )
    claims, err = guard.exercise(
        "verify over-depth chain",
        lambda: toolb_module.verify_chain_and_claims(FakeBiscuit(chain)),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("reason depth_exceeded", err == "depth_exceeded")


# UT: UT-126
# Test Description: Verifies that the tool-b chain verifier delegates to the shared enforcement contract and preserves its deny reason.
# Precondition: Module fixtures are loaded and the shared contract symbol is stubbed to deny the presented chain.
# Expected Output: The SUT returns no claims and preserves the exact deny reason from the shared contract.
# Covers DD: DD-201
@pytest.mark.invariant
def test_verify_chain_and_claims_uses_shared_contract(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    guard.exercise(
        "mock shared contract deny",
        lambda: monkeypatch.setattr(
            toolb_module,
            "verify_chain_contract",
            lambda *_args, **_kwargs: (None, "invalid_chain"),
        ),
    )
    claims, err = guard.exercise(
        "verify chain through tool-b adapter",
        lambda: toolb_module.verify_chain_and_claims(FakeBiscuit([base_root_block()])),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("shared deny reason preserved", err == "invalid_chain")
