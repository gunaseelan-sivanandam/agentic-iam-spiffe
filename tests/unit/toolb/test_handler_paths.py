from __future__ import annotations

import io
import json

import pytest


SPIFFE_ID = "spiffe://example.org/agent-a"


def make_handler(toolb_module, path: str = "/", headers: dict | None = None):
    class HarnessHandler(toolb_module.ToolBHandler):
        def __init__(self, init_path: str, init_headers: dict | None = None):
            self.path = init_path
            self.headers = init_headers or {}
            self.sent: list[tuple[int, dict]] = []
            self.denies: list[tuple[int, str, str | None, dict | None]] = []

        def _send_json(self, status_code: int, payload: dict):
            self.sent.append((status_code, payload))

        def _deny(self, status: int, reason: str, spiffe_id: str | None, claims: dict | None = None):
            self.denies.append((status, reason, spiffe_id, claims))
            self._send_json(status, {"error": "denied", "reason": reason})

    return HarnessHandler(path, headers)


def make_real_handler(toolb_module, path: str = "/", headers: dict | None = None):
    class RealHarnessHandler(toolb_module.ToolBHandler):
        def __init__(self, init_path: str, init_headers: dict | None = None):
            self.path = init_path
            self.headers = init_headers or {}
            self.status_codes: list[int] = []
            self.sent_headers: list[tuple[str, str]] = []
            self.ended = False
            self.wfile = io.BytesIO()

        def send_response(self, status_code: int, message: str | None = None):
            self.status_codes.append(status_code)

        def send_header(self, keyword: str, value: str):
            self.sent_headers.append((keyword, value))

        def end_headers(self):
            self.ended = True

    return RealHarnessHandler(path, headers)


def capture_log_events(monkeypatch, toolb_module):
    events = []

    def fake_log_event(event_type: str, **fields):
        events.append({"event_type": event_type, **fields})

    monkeypatch.setattr(toolb_module, "log_event", fake_log_event)
    return events


def _premise_module_loaded(guard, toolb_module):
    guard.premise("tool-b module loaded", toolb_module is not None)


# UT: UT-058
# Test Description: Verifies that authorize rejects missing spiffe header.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_rejects_missing_spiffe_header(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create handler with no headers", lambda: make_handler(toolb_module, path="/secret", headers={}))
    claims = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims are none", claims is None)
    guard.outcome("deny status 401", handler.denies[0][0] == 401)
    guard.outcome("deny spiffe id none", handler.denies[0][2] is None)
    guard.outcome("deny reason missing_spiffe_id", handler.denies[0][1] == "missing_spiffe_id")


# UT: UT-059
# Test Description: Verifies that authorize rejects missing token.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_rejects_missing_token(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise(
        "create handler with spiffe header only",
        lambda: make_handler(
            toolb_module,
            path="/secret",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID},
        ),
    )
    claims = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims are none", claims is None)
    guard.outcome("deny status 401", handler.denies[0][0] == 401)
    guard.outcome("deny spiffe id preserved", handler.denies[0][2] == SPIFFE_ID)
    guard.outcome("deny reason missing_token", handler.denies[0][1] == "missing_token")


# UT: UT-101
# Test Description: Verifies that authorize rejects a blank bearer token as missing_token.
# Precondition: Module fixtures are loaded and the Authorization header contains Bearer followed only by whitespace.
# Expected Output: The SUT rejects the request with a 401 missing_token deny and returns no claims.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_rejects_blank_bearer_token(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise(
        "create handler with blank bearer token",
        lambda: make_handler(
            toolb_module,
            path="/secret",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID, "Authorization": "Bearer   "},
        ),
    )
    out = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims none", out is None)
    guard.outcome("deny status 401", handler.denies[0][0] == 401)
    guard.outcome("deny reason missing_token", handler.denies[0][1] == "missing_token")
    guard.outcome("deny spiffe id preserved", handler.denies[0][2] == SPIFFE_ID)


# UT: UT-060
# Test Description: Verifies that authorize allows valid token.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_allows_valid_token(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise(
        "create handler with auth header",
        lambda: make_handler(
            toolb_module,
            path="/secret",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID, "Authorization": "Bearer token"},
        ),
    )
    claims = {
        "root_token_id": "root-1",
        "token_id": "token-1",
        "subject_spiffe_id": SPIFFE_ID,
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/secret",
        "effective_depth": 0,
        "budget_remaining": 8,
    }
    guard.exercise("mock verify_biscuit allow", lambda: monkeypatch.setattr(toolb_module, "verify_biscuit", lambda *_: (True, "", claims)))
    out = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims returned", out is claims)


# UT: UT-061
# Test Description: Verifies that authorize denies when token invalid.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_denies_when_token_invalid(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise(
        "create handler with token",
        lambda: make_handler(
            toolb_module,
            path="/secret",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID, "Authorization": "Bearer token"},
        ),
    )
    guard.exercise("mock verify_biscuit deny", lambda: monkeypatch.setattr(toolb_module, "verify_biscuit", lambda *_: (False, "invalid_token", None)))
    claims = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims are none", claims is None)
    guard.outcome("deny status 401", handler.denies[0][0] == 401)
    guard.outcome("deny reason invalid_token", handler.denies[0][1] == "invalid_token")


# UT: UT-090
# Test Description: Verifies that authorize maps non-token verification failures to HTTP 403 denies.
# Precondition: Module fixtures are loaded, the request carries both SPIFFE identity and bearer token, and biscuit verification is stubbed to deny with an authority reason.
# Expected Output: The SUT rejects the request, records no claims, and emits a 403 deny with the exact authority failure reason.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_denies_with_403_for_authority_failure(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise(
        "create handler with token",
        lambda: make_handler(
            toolb_module,
            path="/secret",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID, "Authorization": "Bearer token"},
        ),
    )
    claims = {"subject_spiffe_id": SPIFFE_ID, "act": "read", "res": "tool-b:/secret"}
    guard.exercise(
        "mock verify_biscuit authority deny",
        lambda: monkeypatch.setattr(toolb_module, "verify_biscuit", lambda *_: (False, "sub_mismatch", claims)),
    )
    out = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims are none", out is None)
    guard.outcome("deny status 403", handler.denies[0][0] == 403)
    guard.outcome("deny reason sub_mismatch", handler.denies[0][1] == "sub_mismatch")


# UT: UT-102
# Test Description: Verifies that authorize maps issuer key unavailability to HTTP 401.
# Precondition: Module fixtures are loaded, the request carries both SPIFFE identity and bearer token, and biscuit verification is stubbed to deny with issuer_key_unavailable.
# Expected Output: The SUT rejects the request with a 401 deny, preserves the exact deny reason, and returns no claims.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_denies_with_401_for_issuer_key_unavailable(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise(
        "create handler with token",
        lambda: make_handler(
            toolb_module,
            path="/secret",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID, "Authorization": "Bearer token"},
        ),
    )
    guard.exercise(
        "mock verify_biscuit issuer key unavailable",
        lambda: monkeypatch.setattr(toolb_module, "verify_biscuit", lambda *_: (False, "issuer_key_unavailable", None)),
    )
    out = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims are none", out is None)
    guard.outcome("deny status 401", handler.denies[0][0] == 401)
    guard.outcome("deny reason issuer_key_unavailable", handler.denies[0][1] == "issuer_key_unavailable")


# UT: UT-103
# Test Description: Verifies that authorize maps budget_exceeded to HTTP 403 rather than 401.
# Precondition: Module fixtures are loaded, the request carries both SPIFFE identity and bearer token, and biscuit verification is stubbed to deny with budget_exceeded.
# Expected Output: The SUT rejects the request with a 403 deny, preserves the exact authority failure reason, and returns no claims.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_denies_with_403_for_budget_exceeded(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise(
        "create handler with token",
        lambda: make_handler(
            toolb_module,
            path="/secret",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID, "Authorization": "Bearer token"},
        ),
    )
    claims = {"subject_spiffe_id": SPIFFE_ID, "act": "read", "res": "tool-b:/secret"}
    guard.exercise(
        "mock verify_biscuit budget exceeded",
        lambda: monkeypatch.setattr(toolb_module, "verify_biscuit", lambda *_: (False, "budget_exceeded", claims)),
    )
    out = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/secret"))
    guard.outcome("claims are none", out is None)
    guard.outcome("deny status 403", handler.denies[0][0] == 403)
    guard.outcome("deny reason budget_exceeded", handler.denies[0][1] == "budget_exceeded")


# UT: UT-062
# Test Description: Verifies that deny writes standard payload.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-207
def test_deny_writes_standard_payload(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create handler", lambda: make_handler(toolb_module, path="/secret"))
    claims = {
        "root_token_id": "root-1",
        "token_id": "token-1",
        "parent_token_id": "parent-1",
        "effective_depth": 1,
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "budget_remaining": 5,
    }
    guard.exercise("call deny", lambda: toolb_module.ToolBHandler._deny(handler, 403, "budget_exceeded", SPIFFE_ID, claims))
    guard.outcome("status 403 written", handler.sent[0][0] == 403)
    guard.outcome("reason budget_exceeded", handler.sent[0][1].get("reason") == "budget_exceeded")


# UT: UT-142
# Test Description: Verifies that the final tool-b deny audit event uses the requirement-aligned subject field and includes delegator provenance when present.
# Precondition: A real handler is prepared, claims include full delegated-token provenance, and audit emission is captured through the module-local log helper.
# Expected Output: The SUT emits one exact `toolb_enforcement_decision` deny event with `subject_spiffe_id`, includes `delegator_spiffe_id`, omits the obsolete caller field by exact equality, and writes the standard deny body.
# Covers DD: DD-207
@pytest.mark.invariant
def test_deny_logs_exact_final_enforcement_event_schema(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, toolb_module))
    handler = guard.exercise("create real handler", lambda: make_real_handler(toolb_module, path="/read-file/fileA"))
    claims = {
        "root_token_id": "root-1",
        "token_id": "token-child",
        "parent_token_id": "token-root",
        "effective_depth": 1,
        "delegator_spiffe_id": "spiffe://example.org/delegator",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/read-file:fileA",
        "budget_remaining": 5,
    }
    guard.exercise("call real deny path", lambda: toolb_module.ToolBHandler._deny(handler, 403, "budget_exceeded", SPIFFE_ID, claims))
    body = guard.exercise("decode written body", lambda: json.loads(handler.wfile.getvalue().decode("utf-8")))
    guard.outcome("response status recorded", handler.status_codes == [403])
    guard.outcome("deny body exact", body == {"error": "denied", "reason": "budget_exceeded"})
    guard.outcome(
        "final deny event schema exact",
        events
        == [
            {
                "event_type": "toolb_enforcement_decision",
                "result": "deny",
                "reason_code": "budget_exceeded",
                "subject_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-child",
                "parent_token_id": "token-root",
                "delegation_depth": 1,
                "delegator_spiffe_id": "spiffe://example.org/delegator",
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/read-file:fileA",
                "budget_remaining": 5,
                "path": "/read-file/fileA",
            }
        ],
    )


# UT: UT-063
# Test Description: Verifies do get health.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-208
@pytest.mark.invariant
def test_do_get_health(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create health handler", lambda: make_handler(toolb_module, path="/health"))
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 200", handler.sent[0][0] == 200)
    guard.outcome("status payload ok", handler.sent[0][1].get("status") == "ok")


# UT: UT-064
# Test Description: Verifies do get unknown path.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-208
@pytest.mark.invariant
def test_do_get_unknown_path(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create unknown handler", lambda: make_handler(toolb_module, path="/unknown"))
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 404", handler.sent[0][0] == 404)
    guard.outcome("exact not found payload", handler.sent[0][1] == {"detail": "not found"})


# UT: UT-065
# Test Description: Verifies that do get secret success.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-208
@pytest.mark.invariant
def test_do_get_secret_success(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create secret handler", lambda: make_handler(toolb_module, path="/secret"))
    guard.exercise(
        "stub authorize",
        lambda: setattr(handler, "_authorize", lambda *_: {"root_token_id": "root-1", "subject_spiffe_id": SPIFFE_ID, "exp": 2_000_000_000}),
    )
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 200", handler.sent[0][0] == 200)
    guard.outcome("exact secret payload", handler.sent[0][1] == {"secret": toolb_module.SECRET_VALUE})


# UT: UT-066
# Test Description: Verifies that do get search success.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-208, DD-204
@pytest.mark.invariant
def test_do_get_search_success(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create search handler", lambda: make_handler(toolb_module, path="/search"))
    guard.exercise(
        "stub authorize",
        lambda: setattr(handler, "_authorize", lambda *_: {"root_token_id": "root-1", "subject_spiffe_id": SPIFFE_ID, "exp": 2_000_000_000}),
    )
    guard.exercise("mock record discovery success", lambda: monkeypatch.setattr(toolb_module, "record_discovery", lambda *_: True))
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 200", handler.sent[0][0] == 200)
    guard.outcome("resources list returned", "resources" in handler.sent[0][1])
    guard.outcome("fileA discovered", "tool-b:/read-file:fileA" in handler.sent[0][1]["resources"])


# UT: UT-067
# Test Description: Verifies do get search fail closed when registry write fails.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-208, DD-204
@pytest.mark.invariant
def test_do_get_search_fail_closed_when_registry_write_fails(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create search handler", lambda: make_handler(toolb_module, path="/search"))
    guard.exercise(
        "stub authorize",
        lambda: setattr(handler, "_authorize", lambda *_: {"root_token_id": "root-1", "subject_spiffe_id": SPIFFE_ID, "exp": 2_000_000_000}),
    )
    guard.exercise("mock record discovery failure", lambda: monkeypatch.setattr(toolb_module, "record_discovery", lambda *_: False))
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 503", handler.sent[0][0] == 503)
    guard.outcome("reason store_unavailable", handler.sent[0][1].get("reason") == "store_unavailable")


# UT: UT-068
# Test Description: Verifies do get read file not found.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-208
@pytest.mark.invariant
def test_do_get_read_file_not_found(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create read-file handler missing file", lambda: make_handler(toolb_module, path="/read-file/does-not-exist"))
    guard.exercise(
        "stub authorize",
        lambda: setattr(handler, "_authorize", lambda *_: {"root_token_id": "root-1", "subject_spiffe_id": SPIFFE_ID, "exp": 2_000_000_000}),
    )
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 404", handler.sent[0][0] == 404)
    guard.outcome("exact not_found payload", handler.sent[0][1] == {"error": "not_found"})


# UT: UT-104
# Test Description: Verifies that do GET stops immediately when authorization returns no claims.
# Precondition: Module fixtures are loaded, authorization is stubbed to return None, and downstream discovery write behavior is instrumented.
# Expected Output: The SUT does not call downstream record_discovery or emit any new response after the authorization short-circuit.
# Covers DD: DD-208
@pytest.mark.invariant
def test_do_get_short_circuits_after_authorize_failure(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create search handler", lambda: make_handler(toolb_module, path="/search"))
    seen = {"record_discovery_called": False}
    guard.exercise("stub authorize to none", lambda: setattr(handler, "_authorize", lambda *_: None))

    def fake_record_discovery(*args, **kwargs):
        seen["record_discovery_called"] = True
        return True

    guard.exercise("instrument record discovery", lambda: monkeypatch.setattr(toolb_module, "record_discovery", fake_record_discovery))
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("record discovery not called", seen["record_discovery_called"] is False)
    guard.outcome("no response emitted", handler.sent == [])


# UT: UT-069
# Test Description: Verifies that do get read file success.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-208
@pytest.mark.invariant
def test_do_get_read_file_success(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create read-file handler", lambda: make_handler(toolb_module, path="/read-file/fileA"))
    guard.exercise(
        "stub authorize",
        lambda: setattr(handler, "_authorize", lambda *_: {"root_token_id": "root-1", "subject_spiffe_id": SPIFFE_ID, "exp": 2_000_000_000}),
    )
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 200", handler.sent[0][0] == 200)
    guard.outcome("file id fileA", handler.sent[0][1].get("id") == "fileA")


# UT: UT-143
# Test Description: Verifies that the final tool-b allow audit event uses the requirement-aligned subject field and includes delegator provenance when present.
# Precondition: A real handler is prepared, biscuit verification is stubbed to allow with delegated-token provenance claims, and audit emission is captured through the module-local log helper.
# Expected Output: The SUT returns the claims unchanged and emits one exact `toolb_enforcement_decision` allow event with `subject_spiffe_id` and `delegator_spiffe_id`.
# Covers DD: DD-206
@pytest.mark.invariant
def test_authorize_logs_exact_final_allow_event_schema(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    events = guard.exercise("capture log events", lambda: capture_log_events(monkeypatch, toolb_module))
    handler = guard.exercise(
        "create real handler with auth header",
        lambda: make_real_handler(
            toolb_module,
            path="/read-file/fileA",
            headers={toolb_module.SPIFFE_HEADER: SPIFFE_ID, "Authorization": "Bearer token"},
        ),
    )
    claims = {
        "root_token_id": "root-1",
        "token_id": "token-child",
        "parent_token_id": "token-root",
        "subject_spiffe_id": SPIFFE_ID,
        "effective_depth": 1,
        "delegator_spiffe_id": "spiffe://example.org/delegator",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/read-file:fileA",
        "budget_remaining": 4,
    }
    guard.exercise("mock verify biscuit allow", lambda: monkeypatch.setattr(toolb_module, "verify_biscuit", lambda *_: (True, "", claims)))
    out = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "tool-b:/read-file:fileA"))
    guard.outcome("claims returned unchanged", out is claims)
    guard.outcome(
        "final allow event schema exact",
        events
        == [
            {
                "event_type": "toolb_enforcement_decision",
                "result": "allow",
                "reason_code": "ok",
                "subject_spiffe_id": SPIFFE_ID,
                "root_token_id": "root-1",
                "token_id": "token-child",
                "parent_token_id": "token-root",
                "delegation_depth": 1,
                "delegator_spiffe_id": "spiffe://example.org/delegator",
                "aud": "tool-b",
                "act": "read",
                "res": "tool-b:/read-file:fileA",
                "budget_remaining": 4,
                "path": "/read-file/fileA",
            }
        ],
    )


# UT: UT-115
# Test Description: Verifies that ToolBHandler.log_message is a no-op adapter.
# Precondition: Module fixtures are loaded and a lightweight handler instance is available without starting a real HTTP server.
# Expected Output: The SUT returns None and emits no output side effects.
# Covers DD: DD-217
@pytest.mark.invariant
def test_log_message_is_noop(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create lightweight handler", lambda: toolb_module.ToolBHandler.__new__(toolb_module.ToolBHandler))
    printed: list[tuple[tuple[object, ...], dict[str, object]]] = []
    guard.exercise(
        "capture print",
        lambda: monkeypatch.setattr(toolb_module, "print", lambda *args, **kwargs: printed.append((args, kwargs)), raising=False),
    )
    out = guard.exercise("call log_message", lambda: toolb_module.ToolBHandler.log_message(handler, "%s", "ignored"))
    guard.outcome("returns none", out is None)
    guard.outcome("no output emitted", printed == [])


# UT: UT-116
# Test Description: Verifies that ToolBHandler._send_json writes exact response status, headers, and compact JSON body bytes.
# Precondition: Module fixtures are loaded and a lightweight handler instance is instrumented with header and body sinks.
# Expected Output: The SUT writes the exact status code, content headers, and JSON-encoded payload bytes to the response stream.
# Covers DD: DD-218
@pytest.mark.invariant
def test_send_json_writes_exact_headers_and_body(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create lightweight handler", lambda: toolb_module.ToolBHandler.__new__(toolb_module.ToolBHandler))
    sent = {"status": None, "headers": [], "ended": 0}
    guard.exercise("attach body sink", lambda: setattr(handler, "wfile", io.BytesIO()))
    guard.exercise("attach send_response", lambda: setattr(handler, "send_response", lambda status: sent.__setitem__("status", status)))
    guard.exercise("attach send_header", lambda: setattr(handler, "send_header", lambda name, value: sent["headers"].append((name, value))))
    guard.exercise("attach end_headers", lambda: setattr(handler, "end_headers", lambda: sent.__setitem__("ended", sent["ended"] + 1)))
    payload = {"detail": "ok", "count": 2}
    guard.exercise("send json response", lambda: toolb_module.ToolBHandler._send_json(handler, 201, payload))
    body = guard.exercise("read body bytes", lambda: handler.wfile.getvalue())
    guard.outcome("status exact", sent["status"] == 201)
    guard.outcome(
        "headers exact",
        sent["headers"]
        == [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
        ],
    )
    guard.outcome("end headers once", sent["ended"] == 1)
    guard.outcome("body decodes to exact payload", json.loads(body.decode("utf-8")) == payload)
