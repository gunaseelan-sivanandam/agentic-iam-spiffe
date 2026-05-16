import json
import os
import ssl
import sys
import time
import uuid
from urllib import error, request


CAPISS_URL = os.getenv("CAPABILITY_ISSUER_URL", "https://capability-issuer-envoy:9443")
GATEWAY_URL = os.getenv("JIRA_MCP_GATEWAY_URL", "https://jira-mcp-envoy:11443")
SVID_DIR = os.getenv("SPIRE_SVID_DIR", "/run/spire/svid")
CERT_FILE = os.path.join(SVID_DIR, "svid.pem")
KEY_FILE = os.path.join(SVID_DIR, "svid.key")
BUNDLE_FILE = os.path.join(SVID_DIR, "bundle.pem")
TOOL_ACTIONS = {
    "read_project_summary": "read_project_summary",
    "create_story": "create_story",
}


# DD: DD-701
# Implements: ARCH-027
# Title: tool_specs codex-jira-mcp-adapter MCP tool surface
def tool_specs() -> list[dict[str, object]]:
    return [
        {
            "name": "read_project_summary",
            "description": "Read bounded Jira project summary metadata.",
            "inputSchema": {
                "type": "object",
                "properties": {"project_key": {"type": "string"}},
                "required": ["project_key"],
                "additionalProperties": False,
            },
        },
        {
            "name": "create_story",
            "description": "Create a Jira story in the authorized project.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_key": {"type": "string"},
                    "summary": {"type": "string"},
                    "description": {"type": "string"},
                    "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                    "epic_key": {"type": "string"},
                },
                "required": ["project_key", "summary", "description"],
                "additionalProperties": False,
            },
        },
    ]


# DD: DD-702
# Implements: ARCH-027
# Title: action_for_tool codex-jira-mcp-adapter fixed action mapper
def action_for_tool(tool_name: str) -> str | None:
    return TOOL_ACTIONS.get(tool_name)


# DD: DD-703
# Implements: ARCH-027
# Title: resource_for_project codex-jira-mcp-adapter resource constructor
def resource_for_project(project_key: str) -> str:
    return f"jira-mcp:/project:{project_key}"


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=BUNDLE_FILE)
    ctx.check_hostname = False
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    return ctx


def _json_request(url: str, payload: dict[str, object], correlation_id: str, token: str | None = None) -> tuple[int, dict]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Correlation-ID": correlation_id,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(
        url,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=5, context=_ssl_context()) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read().decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return exc.code, {"error": "gateway_unavailable"}
    except (error.URLError, TimeoutError, ssl.SSLError):
        return 503, {"error": "gateway_unavailable", "reason": "gateway_unavailable"}


# DD: DD-704
# Implements: ARCH-027, ARCH-028
# Title: mint_token codex-jira-mcp-adapter fresh capiss mint client
def mint_token(action: str, project_key: str, correlation_id: str) -> tuple[str | None, dict[str, object]]:
    status, body = _json_request(
        f"{CAPISS_URL.rstrip('/')}/capabilities/root-mint",
        {"aud": "jira-mcp-gateway", "act": action, "res": resource_for_project(project_key)},
        correlation_id,
    )
    if status != 200:
        return None, {
            "ok": False,
            "reason": "mint_denied",
            "correlation_id": correlation_id,
            "status": status,
            "capiss_reason": body.get("reason"),
        }
    token = body.get("token")
    if not isinstance(token, str) or not token:
        return None, {"ok": False, "reason": "mint_denied", "correlation_id": correlation_id}
    metadata = {key: body.get(key) for key in ("aud", "act", "res", "root_token_id", "token_id", "expires_at")}
    metadata["correlation_id"] = correlation_id
    return token, metadata


# DD: DD-705
# Implements: ARCH-027, ARCH-030
# Title: call_gateway codex-jira-mcp-adapter protected gateway client
def call_gateway(tool_name: str, token: str, payload: dict[str, object], correlation_id: str) -> tuple[int, dict]:
    path = {
        "read_project_summary": "/mcp/jira/project-summary",
        "create_story": "/mcp/jira/stories",
    }[tool_name]
    return _json_request(f"{GATEWAY_URL.rstrip()}{path}", payload, correlation_id, token)


# DD: DD-706
# Implements: ARCH-027
# Title: validate_tool_arguments codex-jira-mcp-adapter minimal schema guard
def validate_tool_arguments(tool_name: str, arguments: object) -> tuple[dict[str, object] | None, str | None]:
    if not isinstance(arguments, dict):
        return None, "payload_invalid"
    project_key = arguments.get("project_key")
    if not isinstance(project_key, str) or not project_key:
        return None, "payload_invalid"
    if tool_name == "read_project_summary":
        if set(arguments) != {"project_key"}:
            return None, "payload_invalid"
        return {"project_key": project_key}, None
    if tool_name == "create_story":
        allowed = {"project_key", "summary", "description", "acceptance_criteria", "epic_key"}
        if set(arguments) - allowed:
            return None, "payload_invalid"
        summary = arguments.get("summary")
        description = arguments.get("description")
        if not isinstance(summary, str) or not isinstance(description, str):
            return None, "payload_invalid"
        cleaned = dict(arguments)
        return cleaned, None
    return None, "unknown_tool"


# DD: DD-707
# Implements: ARCH-027
# Title: invoke_tool codex-jira-mcp-adapter tool execution coordinator
def invoke_tool(tool_name: str, arguments: object, correlation_id: str | None = None) -> dict[str, object]:
    correlation_id = correlation_id or str(uuid.uuid4())
    action = action_for_tool(tool_name)
    if action is None:
        return {"ok": False, "reason": "unknown_tool", "correlation_id": correlation_id}
    payload, err = validate_tool_arguments(tool_name, arguments)
    if err or payload is None:
        return {"ok": False, "reason": err or "payload_invalid", "correlation_id": correlation_id}
    project_key = str(payload["project_key"])
    token, token_meta = mint_token(action, project_key, correlation_id)
    if token is None:
        print(json.dumps({"event_type": "adapter_decision", **token_meta}), file=sys.stderr, flush=True)
        return token_meta
    status, body = call_gateway(tool_name, token, payload, correlation_id)
    if status not in {200, 201}:
        reason = body.get("reason") if isinstance(body.get("reason"), str) else "gateway_unavailable"
        result = {"ok": False, "reason": reason, "correlation_id": correlation_id}
        print(json.dumps({"event_type": "adapter_decision", **result, "status": status, **token_meta}, sort_keys=True), file=sys.stderr, flush=True)
        return result
    body.pop("token", None)
    print(json.dumps({"event_type": "adapter_decision", "ok": True, "correlation_id": correlation_id, **token_meta}, sort_keys=True), file=sys.stderr, flush=True)
    return body


def _mcp_text_result(payload: dict[str, object], is_error: bool = False) -> dict[str, object]:
    return {"content": [{"type": "text", "text": json.dumps(payload, separators=(",", ":"))}], "isError": is_error}


def handle_mcp_message(message: dict[str, object]) -> dict[str, object] | None:
    method = message.get("method")
    msg_id = message.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": "codex-jira-mcp-adapter", "version": "0.1.0"}, "capabilities": {"tools": {}}}}
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tool_specs()}}
    if method == "tools/call":
        params = message.get("params")
        if not isinstance(params, dict):
            return {"jsonrpc": "2.0", "id": msg_id, "result": _mcp_text_result({"ok": False, "reason": "payload_invalid"}, True)}
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str):
            return {"jsonrpc": "2.0", "id": msg_id, "result": _mcp_text_result({"ok": False, "reason": "unknown_tool"}, True)}
        result = invoke_tool(name, arguments)
        return {"jsonrpc": "2.0", "id": msg_id, "result": _mcp_text_result(result, not bool(result.get("ok")))}
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "method not found"}}


# DD: DD-708
# Implements: ARCH-027
# Title: main codex-jira-mcp-adapter stdio MCP server loop
def main() -> None:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict):
            continue
        response = handle_mcp_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
