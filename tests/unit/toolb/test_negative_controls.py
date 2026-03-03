from __future__ import annotations

import pytest


SPIFFE_ID = "spiffe://example.org/agent-a"


def _premise_modules_loaded(guard, toolb_module, signed_secret_token):
    guard.premise("tool-b module loaded", toolb_module is not None)
    guard.premise("signed token fixture provided", signed_secret_token is not None)


@pytest.fixture()
def signed_secret_token(capiss_module):
    token, exp, *_ = capiss_module.mint_root_biscuit(
        SPIFFE_ID,
        "tool-b",
        "read",
        "/secret",
    )
    return token, exp, capiss_module


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
            "spiffe://example.org/rogue",
            "read",
            "/secret",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason sub_mismatch", reason == "sub_mismatch")


@pytest.mark.negative_control
def test_verify_biscuit_expired_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, exp, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget success", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (True, "ok", 9)))
    guard.exercise("advance clock past expiry", lambda: monkeypatch.setattr(toolb_module.time, "time", lambda: exp + 1))
    allowed, reason, _ = guard.exercise("verify expired token", lambda: toolb_module.verify_biscuit(token, SPIFFE_ID, "read", "/secret"))
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason expired", reason == "expired")


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


@pytest.mark.negative_control
def test_verify_biscuit_budget_exceeded_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, _, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock budget deny missing_budget", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (False, "missing_budget", -1)))
    allowed, reason, _ = guard.exercise("verify token over budget", lambda: toolb_module.verify_biscuit(token, SPIFFE_ID, "read", "/secret"))
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason budget_exceeded", reason == "budget_exceeded")


@pytest.mark.negative_control
def test_verify_biscuit_rate_limited_exact_reason(toolb_module, signed_secret_token, monkeypatch, guard):
    _premise_modules_loaded(guard, toolb_module, signed_secret_token)
    token, _, capiss_module = signed_secret_token
    guard.exercise("mock public key loader", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: capiss_module.ROOT_PUBLIC_KEY))
    guard.exercise("mock rate limit deny", lambda: monkeypatch.setattr(toolb_module, "consume_budget_and_rate", lambda *_: (False, "rate_limited", 2)))
    allowed, reason, _ = guard.exercise("verify rate-limited token", lambda: toolb_module.verify_biscuit(token, SPIFFE_ID, "read", "/secret"))
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason rate_limited", reason == "rate_limited")
