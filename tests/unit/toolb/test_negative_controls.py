from __future__ import annotations

import pytest


SPIFFE_ID = "spiffe://varambu.org/agent-a"


def _premise_modules_loaded(guard, toolb_module, signed_secret_token):
    guard.premise("tool-b module loaded", toolb_module is not None)
    guard.premise("signed token fixture provided", signed_secret_token is not None)


@pytest.fixture()
def signed_secret_token(capiss_module):
    token, _, exp, *_ = capiss_module.mint_root_biscuit(
        SPIFFE_ID,
        "tool-b",
        "read",
        "tool-b:/secret",
    )
    return token, exp, capiss_module


# UT: UT-072
# Test Description: Verifies verify biscuit subject mismatch exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-202
@pytest.mark.negative_control
def test_verify_biscuit_subject_mismatch_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, _, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 9)))
    allowed, reason, _ = guard.exercise(
        "verify token with subject mismatch",
        lambda: toolb_module.verify_biscuit(
            token,
            "spiffe://varambu.org/rogue",
            "read",
            "tool-b:/secret",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason sub_mismatch", reason == "sub_mismatch")


# UT: UT-073
# Test Description: Verifies verify biscuit expired exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-202
@pytest.mark.negative_control
def test_verify_biscuit_expired_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, exp, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 9)))
    guard.exercise("advance clock past expiry", lambda: monkeypatch.setattr(toolb_module.time, "time", lambda: exp + 1))
    allowed, reason, _ = guard.exercise("verify expired token", lambda: toolb_module.verify_biscuit(token, SPIFFE_ID, "read", "tool-b:/secret"))
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason expired", reason == "expired")


# UT: UT-074
# Test Description: Verifies verify biscuit resource mismatch exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-202
@pytest.mark.negative_control
def test_verify_biscuit_resource_mismatch_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, _, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 9)))
    allowed, reason, _ = guard.exercise(
        "verify token for wrong resource",
        lambda: toolb_module.verify_biscuit(
            token,
            SPIFFE_ID,
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason insufficient_authority", reason == "insufficient_authority")


# UT: UT-075
# Test Description: Verifies verify biscuit budget exceeded exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-202, DD-203
@pytest.mark.negative_control
def test_verify_biscuit_budget_exceeded_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, _, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget deny missing_budget", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (False, "missing_budget", -1)))
    allowed, reason, _ = guard.exercise("verify token over budget", lambda: toolb_module.verify_biscuit(token, SPIFFE_ID, "read", "tool-b:/secret"))
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason budget_exceeded", reason == "budget_exceeded")


# UT: UT-076
# Test Description: Verifies verify biscuit rate limited exact reason.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-202, DD-203
@pytest.mark.negative_control
def test_verify_biscuit_rate_limited_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, _, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock rate limit deny", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (False, "rate_limited", 2)))
    allowed, reason, _ = guard.exercise("verify rate-limited token", lambda: toolb_module.verify_biscuit(token, SPIFFE_ID, "read", "tool-b:/secret"))
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason rate_limited", reason == "rate_limited")
