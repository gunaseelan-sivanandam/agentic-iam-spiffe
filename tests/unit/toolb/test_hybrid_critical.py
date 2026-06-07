from __future__ import annotations

import pytest


SPIFFE_ID = "spiffe://example.org/agent-a"


def _premise_modules_loaded(guard, toolb_module, capiss_module):
    guard.premise("tool-b module loaded", toolb_module is not None)
    guard.premise("capiss module loaded", capiss_module is not None)


# UT: UT-070
# Test Description: Verifies verify biscuit hybrid root secret token.
# Precondition: Module fixtures are loaded and hybrid-path test inputs are prepared before the SUT is exercised.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-202, DD-203
@pytest.mark.hybrid_critical
def test_verify_biscuit_hybrid_root_secret_token(toolb_module, capiss_module, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, capiss_module)
    token, _, _, _, _ = guard.exercise(
        "mint root secret token",
        lambda: capiss_module.mint_root_biscuit(
            SPIFFE_ID,
            "tool-b",
            "read",
            "tool-b:/secret",
        ),
    )

    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget consume success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 8)))

    allowed, reason, claims = guard.exercise(
        "verify root secret token",
        lambda: toolb_module.verify_biscuit(token, SPIFFE_ID, "read", "tool-b:/secret"),
    )
    guard.outcome("allowed true", allowed is True)
    guard.outcome("empty reason", reason == "")
    guard.outcome("claims returned", claims is not None)
    guard.outcome("subject bound", claims is not None and claims.get("subject_spiffe_id") == SPIFFE_ID)
    guard.outcome("budget remaining attached", claims is not None and claims.get("budget_remaining") == 8)


# UT: UT-071
# Test Description: Verifies verify biscuit hybrid delegated chain depth.
# Precondition: Module fixtures are loaded and hybrid-path test inputs are prepared before the SUT is exercised.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-202, DD-201
@pytest.mark.hybrid_critical
def test_verify_biscuit_hybrid_delegated_chain_depth(toolb_module, capiss_module, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, capiss_module)
    root_token, _, _, _, _ = guard.exercise(
        "mint root search token",
        lambda: capiss_module.mint_root_biscuit(
            SPIFFE_ID,
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    parent_biscuit, parent_claims, err = guard.exercise("parse root token", lambda: capiss_module.parse_token(root_token))
    guard.outcome("parse succeeded", err is None)
    guard.outcome("parent biscuit returned", parent_biscuit is not None)
    guard.outcome("parent claims returned", parent_claims is not None)

    delegated_token, _, _, _ = guard.exercise(
        "append delegated token",
        lambda: capiss_module.append_resource_token(
            parent_biscuit,
            parent_claims,
            SPIFFE_ID,
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )

    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget consume success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 7)))

    allowed, reason, claims = guard.exercise(
        "verify delegated token",
        lambda: toolb_module.verify_biscuit(
            delegated_token,
            SPIFFE_ID,
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed true", allowed is True)
    guard.outcome("empty reason", reason == "")
    guard.outcome("claims returned", claims is not None)
    guard.outcome("effective depth is one", claims is not None and claims.get("effective_depth") == 1)
