from __future__ import annotations

import io
import json
import sys

import pytest


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
