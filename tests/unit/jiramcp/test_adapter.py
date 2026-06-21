from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# DD-919 helpers: read the bind-mounted adapter audit file the adapter writes.
# ---------------------------------------------------------------------------
def _adapter_audit_lines(session_dir: Path) -> list[dict]:
    path = session_dir / "adapter_audit.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _wire_session_env(mod, monkeypatch, tmp_path, rel: str = "20260619-1") -> Path:
    monkeypatch.setenv("VARAMBU_AUDIT_ROOT", str(tmp_path))
    monkeypatch.setenv("VARAMBU_SESSION_REL", rel)
    return tmp_path / rel


# UT: UT-193
# Test Description: Verifies the Codex Jira MCP adapter exposes exactly the approved Slice 1 tools.
# Precondition: adapter module is loaded.
# Expected Output: Tool discovery returns only read_project_summary and create_story.
# Covers DD: DD-701
@pytest.mark.boundary
def test_tool_specs_exposes_exact_slice_tools(codex_jira_mcp_adapter_module, guard):
    guard.premise("adapter module loaded", codex_jira_mcp_adapter_module is not None)
    tools = guard.exercise("list tool specs", codex_jira_mcp_adapter_module.tool_specs)
    names = [tool["name"] for tool in tools]
    guard.outcome("approved tool names only", names == ["read_project_summary", "create_story"])
    guard.outcome("schemas reject additional properties", all(tool["inputSchema"]["additionalProperties"] is False for tool in tools))


# UT: UT-194
# Test Description: Verifies adapter maps tools to fixed actions and does not accept Codex-supplied act.
# Precondition: adapter module is loaded and tool payload includes a forged act field.
# Expected Output: Fixed mappings are returned and forged act is rejected as payload_invalid.
# Covers DD: DD-702, DD-706
@pytest.mark.invariant
def test_adapter_fixed_action_mapping_no_freeform_act(codex_jira_mcp_adapter_module, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    actions = guard.exercise(
        "resolve fixed actions",
        lambda: [mod.action_for_tool("read_project_summary"), mod.action_for_tool("create_story"), mod.action_for_tool("update_story")],
    )
    payload, err = guard.exercise(
        "validate forged act payload",
        lambda: mod.validate_tool_arguments("read_project_summary", {"project_key": "IAM", "act": "create_story"}),
    )
    guard.outcome("known tools map to fixed actions", actions[:2] == ["read_project_summary", "create_story"])
    guard.outcome("unknown tool has no action", actions[2] is None)
    guard.outcome("forged act rejected by schema", payload is None and err == "payload_invalid")


# UT: UT-195
# Test Description: Verifies adapter forwards NAS to capiss instead of authorizing projects locally.
# Precondition: adapter mint and gateway clients are stubbed and the request project is NAS.
# Expected Output: The mint request uses jira-mcp:/project:NAS and the gateway is not called after mint denial.
# Covers DD: DD-703, DD-704, DD-707
@pytest.mark.negative_control
def test_adapter_forwards_nas_to_capiss_without_local_authorization(codex_jira_mcp_adapter_module, monkeypatch, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    minted: list[tuple[str, str]] = []
    gateway_called: list[bool] = []

    def fake_mint(action: str, project_key: str, correlation_id: str):
        minted.append((action, mod.resource_for_project(project_key)))
        return None, {"ok": False, "reason": "mint_denied", "correlation_id": correlation_id}

    guard.exercise("stub mint deny", lambda: monkeypatch.setattr(mod, "mint_token", fake_mint))
    guard.exercise("stub gateway capture", lambda: monkeypatch.setattr(mod, "call_gateway", lambda *_: gateway_called.append(True) or (200, {})))
    result = guard.exercise(
        "invoke NAS summary",
        lambda: mod.invoke_tool("read_project_summary", {"project_key": "NAS"}, "corr-1"),
    )
    guard.outcome("NAS was sent to capiss resource mint", minted == [("read_project_summary", "jira-mcp:/project:NAS")])
    guard.outcome("gateway not called after mint denial", gateway_called == [])
    guard.outcome("standard mint denial returned", result["reason"] == "mint_denied")


# UT: UT-196
# Test Description: Verifies MCP responses contain JSON text and no bearer token material.
# Precondition: adapter invoke path is stubbed with a successful bounded response.
# Expected Output: tools/call returns a protocol result whose text omits token fields.
# Covers DD: DD-707, DD-708
@pytest.mark.invariant
def test_mcp_call_response_omits_tokens(codex_jira_mcp_adapter_module, monkeypatch, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    guard.exercise("stub invoke response", lambda: monkeypatch.setattr(mod, "invoke_tool", lambda *_: {"ok": True, "project": {"key": "IAM"}}))
    response = guard.exercise(
        "handle MCP tools/call",
        lambda: mod.handle_mcp_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "read_project_summary", "arguments": {"project_key": "IAM"}}}),
    )
    text = response["result"]["content"][0]["text"]
    parsed = json.loads(text)
    guard.outcome("MCP text is bounded JSON", parsed == {"ok": True, "project": {"key": "IAM"}})
    guard.outcome("no bearer token text", "Bearer " not in text and "token" not in parsed)


# UT: UT-208
# Test Description: Verifies adapter MCP protocol control messages and stdio loop stay JSON-clean.
# Precondition: adapter module is loaded and stdin/stdout are in-memory streams.
# Expected Output: Initialize, tool listing, unknown methods, invalid input, and notifications produce valid protocol behavior.
# Covers DD: DD-701, DD-708
@pytest.mark.boundary
def test_adapter_protocol_messages_and_stdio_loop(codex_jira_mcp_adapter_module, monkeypatch, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    init = guard.exercise("handle initialize", lambda: mod.handle_mcp_message({"jsonrpc": "2.0", "id": 1, "method": "initialize"}))
    notification = guard.exercise("handle initialized notification", lambda: mod.handle_mcp_message({"jsonrpc": "2.0", "method": "notifications/initialized"}))
    unknown = guard.exercise("handle unknown method", lambda: mod.handle_mcp_message({"jsonrpc": "2.0", "id": 2, "method": "bad"}))
    bad_call = guard.exercise("handle malformed tool call", lambda: mod.handle_mcp_message({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": []}))
    stdin = io.StringIO("not-json\n[]\n{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"tools/list\"}\n")
    stdout = io.StringIO()
    guard.exercise("patch stdio", lambda: (monkeypatch.setattr(sys, "stdin", stdin), monkeypatch.setattr(sys, "stdout", stdout)))
    guard.exercise("run stdio loop", mod.main)
    lines = [json.loads(line) for line in stdout.getvalue().splitlines()]
    guard.outcome("initialize returns server metadata", init["result"]["serverInfo"]["name"] == "codex-jira-mcp-adapter")
    guard.outcome("notification is silent", notification is None)
    guard.outcome("unknown method returns JSON-RPC error", unknown["error"]["code"] == -32601)
    guard.outcome("malformed tool call is protocol error result", bad_call["result"]["isError"] is True)
    guard.outcome("stdio emitted only valid JSON response", len(lines) == 1 and lines[0]["result"]["tools"])


# UT: UT-209
# Test Description: Verifies adapter HTTP wrapper, mint handling, gateway routing, and tool invocation outcomes.
# Precondition: adapter network dependencies are stubbed at the URL opener boundary and helper boundary.
# Expected Output: HTTP success/error paths are normalized and invoke_tool never returns raw token material.
# Covers DD: DD-704, DD-705, DD-707
@pytest.mark.invariant
def test_adapter_http_mint_gateway_and_invoke_paths(codex_jira_mcp_adapter_module, monkeypatch, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"ok":true,"token":"secret-token","aud":"jira-mcp-gateway","act":"create_story","res":"jira-mcp:/project:IAM","root_token_id":"root","token_id":"tok"}'

    requests_seen = []
    guard.exercise("stub ssl context", lambda: monkeypatch.setattr(mod, "_ssl_context", lambda: None))
    guard.exercise("stub urlopen success", lambda: monkeypatch.setattr(mod.request, "urlopen", lambda req, **_kwargs: requests_seen.append(req) or FakeResponse()))
    status, body = guard.exercise("perform json request", lambda: mod._json_request("https://example/path", {"x": 1}, "corr", "cap"))
    minted = guard.exercise("mint token", lambda: mod.mint_token("create_story", "IAM", "corr"))
    gateway_status, gateway_body = guard.exercise("call gateway", lambda: mod.call_gateway("create_story", "cap", {"project_key": "IAM"}, "corr"))

    guard.exercise("stub mint success", lambda: monkeypatch.setattr(mod, "mint_token", lambda *_: ("secret-token", {"aud": "jira-mcp-gateway", "correlation_id": "corr"})))
    guard.exercise("stub gateway success", lambda: monkeypatch.setattr(mod, "call_gateway", lambda *_: (201, {"ok": True, "key": "IAM-1", "token": "must-strip"})))
    invoked = guard.exercise("invoke tool success", lambda: mod.invoke_tool("create_story", {"project_key": "IAM", "summary": "s", "description": "d"}, "corr"))
    guard.exercise("stub gateway denial", lambda: monkeypatch.setattr(mod, "call_gateway", lambda *_: (403, {"reason": "project_mismatch"})))
    denied = guard.exercise("invoke tool denial", lambda: mod.invoke_tool("create_story", {"project_key": "IAM", "summary": "s", "description": "d"}, "corr"))

    guard.outcome("json request success parsed", status == 200 and body["token"] == "secret-token")
    guard.outcome("authorization header was sent only internally", requests_seen[0].headers.get("Authorization") == "Bearer cap")
    guard.outcome("mint returned token and metadata", minted[0] == "secret-token" and minted[1]["aud"] == "jira-mcp-gateway")
    guard.outcome("gateway call returned success", gateway_status == 200 and gateway_body["ok"] is True)
    guard.outcome("invoke strips raw token", invoked == {"ok": True, "key": "IAM-1"})
    guard.outcome("invoke denial normalized", denied["reason"] == "project_mismatch")


# UT: UT-238
# Test Description: Verifies adapter HTTP and mint helpers fail closed for upstream error branches.
# Precondition: adapter HTTP dependencies are stubbed to return HTTP errors, transport errors, and missing token bodies.
# Expected Output: The SUT normalizes each branch without exposing token material or raising.
# Covers DD: DD-704
@pytest.mark.boundary
def test_adapter_http_and_mint_fail_closed_branches(codex_jira_mcp_adapter_module, monkeypatch, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)

    def http_error_with_json(*_args, **_kwargs):
        raise mod.error.HTTPError("https://example/path", 403, "forbidden", {}, io.BytesIO(b'{"reason":"policy"}'))

    def http_error_with_bad_json(*_args, **_kwargs):
        raise mod.error.HTTPError("https://example/path", 502, "bad gateway", {}, io.BytesIO(b"not-json"))

    guard.exercise("stub ssl context", lambda: monkeypatch.setattr(mod, "_ssl_context", lambda: None))
    guard.exercise("stub http error json", lambda: monkeypatch.setattr(mod.request, "urlopen", http_error_with_json))
    denied_status, denied_body = guard.exercise("request with json http error", lambda: mod._json_request("https://example/path", {}, "corr"))
    guard.exercise("stub http error bad json", lambda: monkeypatch.setattr(mod.request, "urlopen", http_error_with_bad_json))
    bad_status, bad_body = guard.exercise("request with bad json http error", lambda: mod._json_request("https://example/path", {}, "corr"))
    guard.exercise("stub transport error", lambda: monkeypatch.setattr(mod.request, "urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(mod.error.URLError("down"))))
    unavailable_status, unavailable_body = guard.exercise("request with transport error", lambda: mod._json_request("https://example/path", {}, "corr"))
    guard.exercise("stub missing token response", lambda: monkeypatch.setattr(mod, "_json_request", lambda *_args, **_kwargs: (200, {"ok": True})))
    token, metadata = guard.exercise("mint with missing token", lambda: mod.mint_token("read_project_summary", "IAM", "corr"))

    guard.outcome("json http error preserved", denied_status == 403 and denied_body == {"reason": "policy"})
    guard.outcome("bad json http error normalized", bad_status == 502 and bad_body == {"error": "gateway_unavailable"})
    guard.outcome("transport error normalized", unavailable_status == 503 and unavailable_body["reason"] == "gateway_unavailable")
    guard.outcome("missing token denied", token is None and metadata == {"ok": False, "reason": "mint_denied", "correlation_id": "corr"})


# UT: UT-239
# Test Description: Verifies adapter argument validation rejects malformed create-story and MCP tool-name inputs.
# Precondition: adapter module is loaded and caller-supplied arguments cover each invalid branch.
# Expected Output: The SUT returns protocol-safe errors before any mint or gateway call.
# Covers DD: DD-706, DD-707
@pytest.mark.negative_control
def test_adapter_validation_rejects_malformed_create_story_inputs(codex_jira_mcp_adapter_module, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    non_dict = guard.exercise("validate non-dict", lambda: mod.validate_tool_arguments("create_story", []))
    missing_project = guard.exercise("validate missing project", lambda: mod.validate_tool_arguments("create_story", {"summary": "s", "description": "d"}))
    extra_field = guard.exercise(
        "validate extra field",
        lambda: mod.validate_tool_arguments("create_story", {"project_key": "IAM", "summary": "s", "description": "d", "act": "forged"}),
    )
    missing_summary = guard.exercise("validate missing summary", lambda: mod.validate_tool_arguments("create_story", {"project_key": "IAM", "description": "d"}))
    unknown = guard.exercise("invoke unknown tool", lambda: mod.invoke_tool("delete_story", {"project_key": "IAM"}, "corr"))
    bad_mcp_name = guard.exercise(
        "handle non-string tool name",
        lambda: mod.handle_mcp_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": 7, "arguments": {}}}),
    )

    guard.outcome("non-dict rejected", non_dict == (None, "payload_invalid"))
    guard.outcome("missing project rejected", missing_project == (None, "payload_invalid"))
    guard.outcome("extra field rejected", extra_field == (None, "payload_invalid"))
    guard.outcome("missing summary rejected", missing_summary == (None, "payload_invalid"))
    guard.outcome("unknown tool rejected", unknown == {"ok": False, "reason": "unknown_tool", "correlation_id": "corr"})
    guard.outcome("non-string MCP tool name is error result", bad_mcp_name["result"]["isError"] is True)


# UT: UT-325
# Test Description: Verifies the adapter writes adapter_request before the mint and adapter_decision after the gateway call.
# Precondition: adapter module is loaded; session env wired to a temp dir; mint and gateway are stubbed to observe the audit file at call time.
# Expected Output: adapter_request is persisted before mint runs; adapter_decision is persisted only after the gateway call returns.
# Covers DD: DD-919
@pytest.mark.invariant
def test_adapter_emit_ordering_request_before_mint_decision_after_gateway(codex_jira_mcp_adapter_module, monkeypatch, tmp_path, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    session = _wire_session_env(mod, monkeypatch, tmp_path)
    observed: list = []

    def fake_mint(action, project_key, correlation_id):
        types = [r["event_type"] for r in _adapter_audit_lines(session)]
        observed.append(("mint", "adapter_request" in types, "adapter_decision" in types))
        return "tok-secret", {"correlation_id": correlation_id, "token_id": "tok-1", "root_token_id": "root-1"}

    def fake_gateway(tool_name, token, payload, correlation_id):
        types = [r["event_type"] for r in _adapter_audit_lines(session)]
        observed.append(("gateway", "adapter_decision" in types))
        return 201, {"ok": True, "key": "IAM-5"}

    guard.exercise("stub mint", lambda: monkeypatch.setattr(mod, "mint_token", fake_mint))
    guard.exercise("stub gateway", lambda: monkeypatch.setattr(mod, "call_gateway", fake_gateway))
    guard.exercise("invoke allowed", lambda: mod.invoke_tool("create_story", {"project_key": "IAM", "summary": "s", "description": "d"}, "corr-1"))
    lines = guard.exercise("read audit file", lambda: _adapter_audit_lines(session))
    types = [r["event_type"] for r in lines]
    guard.outcome("request before mint", observed[0] == ("mint", True, False))
    guard.outcome("decision not written before gateway returns", observed[1] == ("gateway", False))
    guard.outcome("both legs persisted in order", types == ["adapter_request", "adapter_decision"])


# UT: UT-326
# Test Description: Verifies an exception between mint and gateway leaves adapter_request persisted with no paired adapter_decision.
# Precondition: adapter module is loaded; session env wired; mint succeeds and the gateway call raises.
# Expected Output: adapter_request is present; no adapter_decision is written (crash visibility).
# Covers DD: DD-919
@pytest.mark.negative_control
def test_adapter_emit_crash_visibility_request_without_decision(codex_jira_mcp_adapter_module, monkeypatch, tmp_path, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    session = _wire_session_env(mod, monkeypatch, tmp_path)
    guard.exercise("stub mint", lambda: monkeypatch.setattr(mod, "mint_token", lambda *_: ("tok-secret", {"correlation_id": "corr-1", "token_id": "tok-1"})))

    def boom(*_args, **_kwargs):
        raise RuntimeError("gateway exploded")

    guard.exercise("stub gateway crash", lambda: monkeypatch.setattr(mod, "call_gateway", boom))
    with pytest.raises(RuntimeError):
        mod.invoke_tool("create_story", {"project_key": "IAM", "summary": "s", "description": "d"}, "corr-1")
    types = guard.exercise("read audit types", lambda: [r["event_type"] for r in _adapter_audit_lines(session)])
    guard.outcome("request persisted", "adapter_request" in types)
    guard.outcome("no paired decision", "adapter_decision" not in types)


# UT: UT-327
# Test Description: Verifies adapter emit writes under the session dir when VARAMBU_SESSION_REL is set and is a safe no-op when unset.
# Precondition: adapter module is loaded; emit is invoked once with the session env set and once with it cleared.
# Expected Output: With the env set a file line is written; with it unset no file is created and no exception is raised.
# Covers DD: DD-919
@pytest.mark.boundary
def test_adapter_emit_path_wiring_set_and_unset(codex_jira_mcp_adapter_module, monkeypatch, tmp_path, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    session = _wire_session_env(mod, monkeypatch, tmp_path)
    guard.exercise("emit with env set", lambda: mod.emit_adapter_event("adapter_request", {"correlation_id": "corr-1", "tool_name": "create_story"}))
    set_lines = guard.exercise("read set", lambda: _adapter_audit_lines(session))
    guard.exercise("clear session env", lambda: monkeypatch.delenv("VARAMBU_SESSION_REL", raising=False))
    noop = guard.exercise("emit with env unset", lambda: mod.emit_adapter_event("adapter_request", {"correlation_id": "corr-2"}))
    other = tmp_path / "should-not-exist"
    guard.outcome("written when set", len(set_lines) == 1 and set_lines[0]["correlation_id"] == "corr-1")
    guard.outcome("no-op returns cleanly when unset", noop is None)
    guard.outcome("no stray file when unset", not other.exists())


# UT: UT-328
# Test Description: Verifies the adapter audit file carries token identifier metadata only and never the raw biscuit.
# Precondition: adapter module is loaded; session env wired; mint returns a secret biscuit plus token_id metadata.
# Expected Output: The persisted decision carries token_id but the raw biscuit value never appears in the file.
# Covers DD: DD-919
@pytest.mark.invariant
def test_adapter_emit_secret_discipline_metadata_only(codex_jira_mcp_adapter_module, monkeypatch, tmp_path, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    session = _wire_session_env(mod, monkeypatch, tmp_path)
    guard.exercise("stub mint secret", lambda: monkeypatch.setattr(mod, "mint_token", lambda *_: ("super-secret-biscuit-value", {"correlation_id": "corr-1", "token_id": "tok-1", "root_token_id": "root-1"})))
    guard.exercise("stub gateway", lambda: monkeypatch.setattr(mod, "call_gateway", lambda *_: (201, {"ok": True, "key": "IAM-5"})))
    guard.exercise("invoke allowed", lambda: mod.invoke_tool("create_story", {"project_key": "IAM", "summary": "s", "description": "d"}, "corr-1"))
    content = guard.exercise("read raw file", lambda: (session / "adapter_audit.jsonl").read_text(encoding="utf-8"))
    decision = guard.exercise("find decision", lambda: [r for r in _adapter_audit_lines(session) if r["event_type"] == "adapter_decision"][0])
    guard.outcome("token_id metadata present", decision.get("token_id") == "tok-1")
    guard.outcome("raw biscuit never persisted", "super-secret-biscuit-value" not in content)


# UT: UT-329
# Test Description: Verifies every adapter event stamps the same correlation id as the originating request.
# Precondition: adapter module is loaded; session env wired; an allowed call runs with a known correlation id.
# Expected Output: Both adapter_request and adapter_decision carry that correlation id.
# Covers DD: DD-919
@pytest.mark.invariant
def test_adapter_emit_correlation_stamping(codex_jira_mcp_adapter_module, monkeypatch, tmp_path, guard):
    mod = codex_jira_mcp_adapter_module
    guard.premise("adapter module loaded", mod is not None)
    session = _wire_session_env(mod, monkeypatch, tmp_path)
    guard.exercise("stub mint", lambda: monkeypatch.setattr(mod, "mint_token", lambda *_: ("tok-secret", {"correlation_id": "corr-77", "token_id": "tok-1"})))
    guard.exercise("stub gateway", lambda: monkeypatch.setattr(mod, "call_gateway", lambda *_: (201, {"ok": True, "key": "IAM-5"})))
    guard.exercise("invoke allowed", lambda: mod.invoke_tool("create_story", {"project_key": "IAM", "summary": "s", "description": "d"}, "corr-77"))
    lines = guard.exercise("read audit", lambda: _adapter_audit_lines(session))
    guard.outcome("all events carry correlation id", all(r["correlation_id"] == "corr-77" for r in lines) and len(lines) == 2)
