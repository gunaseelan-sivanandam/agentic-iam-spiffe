from __future__ import annotations

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


def _premise_module_loaded(guard, toolb_module):
    guard.premise("tool-b module loaded", toolb_module is not None)


def test_authorize_rejects_missing_spiffe_header(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create handler with no headers", lambda: make_handler(toolb_module, path="/secret", headers={}))
    claims = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "/secret"))
    guard.outcome("claims are none", claims is None)
    guard.outcome("deny reason missing_spiffe_id", handler.denies[0][1] == "missing_spiffe_id")


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
    claims = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "/secret"))
    guard.outcome("claims are none", claims is None)
    guard.outcome("deny reason missing_token", handler.denies[0][1] == "missing_token")


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
    out = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "/secret"))
    guard.outcome("claims returned", out is claims)


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
    claims = guard.exercise("authorize request", lambda: toolb_module.ToolBHandler._authorize(handler, "read", "/secret"))
    guard.outcome("claims are none", claims is None)
    guard.outcome("deny status 401", handler.denies[0][0] == 401)
    guard.outcome("deny reason invalid_token", handler.denies[0][1] == "invalid_token")


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


def test_do_get_health(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create health handler", lambda: make_handler(toolb_module, path="/health"))
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 200", handler.sent[0][0] == 200)
    guard.outcome("status payload ok", handler.sent[0][1].get("status") == "ok")


def test_do_get_unknown_path(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create unknown handler", lambda: make_handler(toolb_module, path="/unknown"))
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 404", handler.sent[0][0] == 404)


def test_do_get_secret_success(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create secret handler", lambda: make_handler(toolb_module, path="/secret"))
    guard.exercise(
        "stub authorize",
        lambda: setattr(handler, "_authorize", lambda *_: {"root_token_id": "root-1", "subject_spiffe_id": SPIFFE_ID, "exp": 2_000_000_000}),
    )
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 200", handler.sent[0][0] == 200)
    guard.outcome("secret returned", "secret" in handler.sent[0][1])


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


def test_do_get_read_file_not_found(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    handler = guard.exercise("create read-file handler missing file", lambda: make_handler(toolb_module, path="/read-file/does-not-exist"))
    guard.exercise(
        "stub authorize",
        lambda: setattr(handler, "_authorize", lambda *_: {"root_token_id": "root-1", "subject_spiffe_id": SPIFFE_ID, "exp": 2_000_000_000}),
    )
    guard.exercise("invoke do_GET", lambda: toolb_module.ToolBHandler.do_GET(handler))
    guard.outcome("status 404", handler.sent[0][0] == 404)
    guard.outcome("error not_found", handler.sent[0][1].get("error") == "not_found")


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
