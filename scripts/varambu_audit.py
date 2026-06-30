#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # zoneinfo is stdlib on 3.9+; render falls back to UTC if a zone is unavailable
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover - environment without tz data
    ZoneInfo = None  # type: ignore[assignment]

    class ZoneInfoNotFoundError(Exception):  # type: ignore[no-redef]
        pass


EVENT_TYPE = "capiss_mint_decision"
DEFAULT_CONTAINER = "spiffe-capability-issuer"
FIELD_ORDER = [
    "event_type",
    "sequence",
    "result",
    "reason_code",
    "correlation_id",
    "subject_spiffe_id",
    "delegator_spiffe_id",
    "decision_type",
    "aud",
    "act",
    "res",
    "resource_attrs",
    "token_id",
    "root_token_id",
    "parent_token_id",
    "delegation_depth",
    "issued_at_local",
    "expires_at_local",
    "timestamp_local",
    "ttl_seconds",
    "issued_at_utc",
    "expires_at_utc",
    "timestamp_utc",
    "timezone",
    "registry_hit",
    "error",
    "policy_id",
    "policy_hash",
]
FORBIDDEN_FIELD_NAMES = {
    "token",
    "authorization",
    "Authorization",
    "cookie",
    "cookies",
    "jira_api_token",
    "JIRA_API_TOKEN",
}
FORBIDDEN_TEXT = ("Bearer ", "Basic ", "biscuit")


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr, flush=True)


def _contains_forbidden_value(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in FORBIDDEN_TEXT)
    if isinstance(value, dict):
        return any(_contains_forbidden_value(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_value(item) for item in value)
    return False


# DD: DD-901
# Implements: ARCH-032
# Title: normalize_event Varambu capiss audit allowlist normalizer
def normalize_event(raw: dict[str, Any], sequence: int) -> dict[str, Any] | None:
    if raw.get("event_type") != EVENT_TYPE:
        return None
    normalized: dict[str, Any] = {}
    for key in FIELD_ORDER:
        if key == "sequence":
            normalized[key] = sequence
            continue
        if key not in raw:
            continue
        if key in FORBIDDEN_FIELD_NAMES or _contains_forbidden_value(raw[key]):
            warn(f"dropped forbidden audit field: {key}")
            continue
        normalized[key] = raw[key]
    for key in raw:
        if key not in FIELD_ORDER:
            warn(f"dropped unknown audit field: {key}")
    return normalized


def _display(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dict):
        return " ".join(f"{k}={value[k]}" for k in sorted(value))
    return str(value)


def _humanize_reason(reason_code: str) -> str:
    """Render a snake_case reason_code as Title Case words (policy -> Policy)."""
    return " ".join(word.capitalize() for word in reason_code.split("_"))


_GREEN = "\033[32m"
_RED = "\033[1;31m"
_BLUE = "\033[94m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_RESET = "\033[0m"
_HEADER_RE = re.compile(r"^#\d+ (MINTED|DENIED)\b")


def _colorize_line(line: str) -> str:
    """Color a MINTED/DENIED header line for display only (TTY). The persisted
    file is written by render_record without color; color is applied here at
    print time so the evidence file and any pipe stay plain."""
    if not sys.stdout.isatty():
        return line
    match = _HEADER_RE.match(line)
    if not match:
        return line
    color = _GREEN if match.group(1) == "MINTED" else _RED
    body = line.rstrip("\n")
    newline = "\n" if line.endswith("\n") else ""
    return f"{color}{body}{_RESET}{newline}"


def _tty_color(text: str, color: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{_RESET}"


# DD: DD-902
# Implements: ARCH-032
# Title: render_record Varambu human-readable capiss audit renderer
def render_record(record: dict[str, Any], *, verbose: bool = False) -> str:
    result = str(record.get("result", "")).upper()
    reason_code = str(record.get("reason_code", "-"))
    timestamp = _display(record.get("timestamp_local"))
    sequence = record.get("sequence", "-")
    if result == "ALLOW":
        header = f"#{sequence} MINTED {reason_code.upper()}  {timestamp}"
    elif result == "DENY":
        header = f"#{sequence} DENIED: Reason {_humanize_reason(reason_code)}  {timestamp}"
    else:
        header = f"#{sequence} {result or '-'} {reason_code}  {timestamp}"
    lines = [
        header,
        f"Subject:      {_display(record.get('subject_spiffe_id'))}",
        f"Action:       {_display(record.get('act'))}",
        f"Resource:     {_display(record.get('res'))}",
        f"Audience:     {_display(record.get('aud'))}",
        f"Decision:     {_display(record.get('decision_type'))}",
    ]
    if verbose:
        lines.append(f"Scope:        {_display(record.get('resource_attrs'))}")
    lines.extend([
        f"Token ID:     {_display(record.get('token_id'))}",
        f"Root Token:   {_display(record.get('root_token_id'))}",
        f"Parent Token: {_display(record.get('parent_token_id'))}",
        f"Depth:        {_display(record.get('delegation_depth'))}",
        f"Issued At:    {_display(record.get('issued_at_local'))}",
        f"Expires At:   {_display(record.get('expires_at_local'))}",
        f"Logged At:    {_display(record.get('timestamp_local'))}",
        f"TTL:          {_display(str(record['ttl_seconds']) + 's' if 'ttl_seconds' in record else None)}",
        "UTC:          "
        f"issued={_display(record.get('issued_at_utc'))} "
        f"expires={_display(record.get('expires_at_utc'))} "
        f"logged={_display(record.get('timestamp_utc'))}",
        f"Correlation:  {_display(record.get('correlation_id'))}",
        f"Policy:       {_display(record.get('policy_id'))} {_display(record.get('policy_hash'))}",
    ])
    return "\n".join(lines) + "\n"


# DD: DD-903
# Implements: ARCH-032
# Title: tail Varambu capiss audit session tailer
def tail(args: argparse.Namespace) -> int:
    jsonl_path = Path(args.jsonl)
    human_path = Path(args.human)
    err_path = Path(args.err)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.touch(exist_ok=True)
    human_path.touch(exist_ok=True)
    sequence = sum(1 for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()) + 1
    source = getattr(args, "source", "capiss")
    normalizer = normalize_gateway_event if source == "gateway" else normalize_event
    cmd = ["docker", "logs", "--since", args.since, "--follow", args.container]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    assert proc.stderr is not None
    with err_path.open("a", encoding="utf-8") as err_handle:
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            record = normalizer(raw, sequence)
            if record is None:
                continue
            with jsonl_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n")
            with human_path.open("a", encoding="utf-8") as handle:
                handle.write(_tail_human_line(record, source, args.verbose))
            sequence += 1
        err_handle.write(proc.stderr.read())
    return proc.wait()


def _tail_human_line(record: dict[str, Any], source: str, verbose: bool) -> str:
    if source == "gateway":
        return json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n"
    return render_record(record, verbose=verbose) + "\n"


def _read_file(path: Path, *, follow: bool) -> int:
    if path.exists() and path.stat().st_size > 0:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                print(_colorize_line(line), end="")
    else:
        print(f"No capiss audit events recorded for the current Varambu session yet.\nAudit file: {path}")
    if follow:
        try:
            with path.open("r", encoding="utf-8") as handle:
                handle.seek(0, 2)
                while True:
                    line = handle.readline()
                    if line:
                        print(_colorize_line(line), end="", flush=True)
                    else:
                        time.sleep(0.5)
        except KeyboardInterrupt:
            print()  # finish the current line so the shell prompt starts clean
            return 0
    return 0


# DD: DD-904
# Implements: ARCH-032
# Title: show Varambu persisted audit display command
def show(args: argparse.Namespace) -> int:
    return _read_file(Path(args.file), follow=args.follow)


# ===========================================================================
# Full-chain audit trace (ARCH-033)
# ===========================================================================
GATEWAY_EVENT_TYPE = "jiramcp_gateway_decision"
ADAPTER_EVENT_TYPES = {"adapter_request", "adapter_decision"}
M5_TOOLS = {"read_project_summary", "create_story"}
CHAIN_LEG_ORDER = ["intent", "action", "adapter_request", "mint", "gateway", "upstream", "adapter_decision"]
IN_BOUNDARY_LEGS = ("adapter_request", "mint", "gateway", "upstream", "adapter_decision")
LEG_LABELS = {
    "intent": "INTENT",
    "action": "ACTION",
    "adapter_request": "ADAPTER",
    "mint": "MINT",
    "gateway": "GATEWAY",
    "upstream": "UPSTREAM",
    "adapter_decision": "RETURN TO CODEX",
}
TRACE_MAX_USER_MESSAGE = 2048
TRACE_MAX_TEXT = 1024
TRUNCATION_MARKER = "…[truncated]"
ALLOWED_RESULT_KEYS = ("ok", "reason", "key", "status")
GATEWAY_FIELD_ORDER = [
    "event_type", "sequence", "decision", "reason_code", "correlation_id",
    "subject_spiffe_id", "endpoint", "project_key", "aud", "act", "res",
    "token_project", "token_id", "root_token_id", "budget_remaining",
    "upstream_called", "upstream_operation", "upstream_status", "upstream_error_detail",
    "issue_key", "epic_key", "timestamp",
]
ADAPTER_FIELD_ORDER = [
    "event_type", "sequence", "correlation_id", "tool_name", "act", "res",
    "project_key", "ok", "reason", "capiss_reason", "status", "key", "aud",
    "token_id", "root_token_id", "issued_at", "expires_at", "timestamp",
]
# Tolerant of nesting/escaping: the agent may store the tool result as escaped
# JSON-in-JSON (\"correlation_id\":\"…\") or as a structured object, so accept any
# run of quote/backslash/colon/whitespace between the key and the UUID value.
_CID_RE = re.compile(
    r'correlation_id[\\":\s]*'
    r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'
)


def _allowed_trace_field(key: str, raw: dict[str, Any]) -> bool:
    if key in FORBIDDEN_FIELD_NAMES or _contains_forbidden_value(raw[key]):
        warn(f"dropped forbidden trace field: {key}")
        return False
    return True


def _warn_unknown_trace_fields(raw: dict[str, Any], field_order: list[str]) -> None:
    for key in raw:
        if key not in field_order:
            warn(f"dropped unknown trace field: {key}")


def _normalize_with_allowlist(raw: dict[str, Any], sequence: int, field_order: list[str], accepted: set[str]) -> dict[str, Any] | None:
    if not isinstance(raw, dict) or raw.get("event_type") not in accepted:
        return None
    normalized: dict[str, Any] = {}
    for key in field_order:
        if key == "sequence":
            normalized[key] = sequence
        elif key in raw and _allowed_trace_field(key, raw):
            normalized[key] = raw[key]
    _warn_unknown_trace_fields(raw, field_order)
    return normalized


# DD: DD-910
# Implements: ARCH-033
# Title: normalize_gateway_event Varambu gateway-leg allowlist normalizer
def normalize_gateway_event(raw: dict[str, Any], sequence: int) -> dict[str, Any] | None:
    return _normalize_with_allowlist(raw, sequence, GATEWAY_FIELD_ORDER, {GATEWAY_EVENT_TYPE})


# DD: DD-911
# Implements: ARCH-033
# Title: normalize_adapter_event Varambu adapter-leg allowlist normalizer
def normalize_adapter_event(raw: dict[str, Any], sequence: int) -> dict[str, Any] | None:
    return _normalize_with_allowlist(raw, sequence, ADAPTER_FIELD_ORDER, ADAPTER_EVENT_TYPES)


def _payload(record: Any) -> dict[str, Any] | None:
    payload = record.get("payload") if isinstance(record, dict) else None
    return payload if isinstance(payload, dict) else None


def _payload_of_type(record: Any, expected: str) -> dict[str, Any] | None:
    payload = _payload(record)
    return payload if payload is not None and payload.get("type") == expected else None


def _mcp_end_text(payload: dict[str, Any]) -> str | None:
    result = payload.get("result")
    ok = result.get("Ok") if isinstance(result, dict) else None
    content = ok.get("content") if isinstance(ok, dict) else None
    if not isinstance(content, list):
        return None
    parts = [c.get("text") for c in content if isinstance(c, dict) and isinstance(c.get("text"), str)]
    return "".join(parts) if parts else None


def _stringify(value: Any) -> str | None:
    """Render a rollout value as searchable text. Codex may store a tool result
    as a plain string, escaped JSON-in-JSON, or a structured object; serializing
    non-strings lets the correlation_id regex find the id wherever it is nested."""
    if isinstance(value, str):
        return value
    if value is None:
        return None
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return None


def _rollout_output_text(record: Any) -> str | None:
    payload = _payload(record)
    if payload is None:
        return None
    if payload.get("type") == "function_call_output":
        return _stringify(payload.get("output"))
    if payload.get("type") == "mcp_tool_call_end":
        return _mcp_end_text(payload) or _stringify(payload.get("result"))
    return None


# DD: DD-912
# Implements: ARCH-033
# Title: extract_correlation_id Varambu rollout correlation extractor
def extract_correlation_id(record: dict[str, Any]) -> str | None:
    text = _rollout_output_text(record)
    if not text:
        return None
    matches = _CID_RE.findall(text)
    if not matches:
        return None
    # The rollout is untrusted (agent-written). A valid adapter/gateway result
    # carries exactly one correlation_id; two distinct ids in one output means a
    # schema change or a forged record. Stay deterministic (first match, never
    # raise) but surface the anomaly so an auditor can investigate the root cause.
    if len(set(matches)) > 1:
        warn(f"multiple distinct correlation_ids in one rollout output; using first ({matches[0]}); investigate possible forged/tampered rollout")
    return matches[0]


def _find_call_id_for_cid(rollout: list[dict[str, Any]], correlation_id: str) -> str | None:
    for record in rollout:
        if extract_correlation_id(record) == correlation_id:
            payload = _payload(record)
            call_id = payload.get("call_id") if payload else None
            if isinstance(call_id, str):
                return call_id
    return None


def _find_function_call(rollout: list[dict[str, Any]], call_id: str) -> tuple[int, dict[str, Any]] | tuple[None, None]:
    for index, record in enumerate(rollout):
        payload = _payload_of_type(record, "function_call")
        if payload is not None and payload.get("call_id") == call_id:
            return index, payload
    return None, None


def _nearest_user_message(rollout: list[dict[str, Any]], before_index: int) -> tuple[int, str] | tuple[None, None]:
    for index in range(before_index - 1, -1, -1):
        payload = _payload_of_type(rollout[index], "user_message")
        if payload is not None and isinstance(payload.get("message"), str):
            return index, payload["message"]
    return None, None


def _parse_arguments(payload: dict[str, Any]) -> dict[str, Any] | None:
    raw = payload.get("arguments")
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


# DD: DD-913
# Implements: ARCH-033
# Title: find_intent_triple Varambu docker-anchored rollout intent join
def find_intent_triple(rollout: list[dict[str, Any]], correlation_id: str) -> dict[str, Any]:
    triple: dict[str, Any] = {"correlation_id": correlation_id, "tool_name": None, "arguments": None, "user_message": None}
    call_id = _find_call_id_for_cid(rollout, correlation_id)
    if call_id is None:
        return triple
    index, payload = _find_function_call(rollout, call_id)
    if payload is None:
        return triple
    if payload.get("name") not in M5_TOOLS:
        return triple
    triple["tool_name"] = payload.get("name")
    triple["arguments"] = _parse_arguments(payload)
    triple["action_timestamp"] = rollout[index].get("timestamp")
    triple["action_sequence"] = index + 1
    msg_index, message = _nearest_user_message(rollout, index)
    if message is not None:
        triple["user_message"] = message
        triple["intent_timestamp"] = rollout[msg_index].get("timestamp")
        triple["intent_sequence"] = msg_index + 1
    return triple


def _bound_text(value: Any, limit: int) -> Any:
    if not isinstance(value, str):
        return value
    if len(value.encode("utf-8")) < limit:
        return value
    budget = max(0, limit - len(TRUNCATION_MARKER.encode("utf-8")))
    truncated = value.encode("utf-8")[:budget].decode("utf-8", errors="ignore")
    return truncated + TRUNCATION_MARKER


def _scrub_arguments(arguments: Any) -> Any:
    if not isinstance(arguments, dict):
        return arguments
    cleaned: dict[str, Any] = {}
    for key, value in arguments.items():
        if key in FORBIDDEN_FIELD_NAMES or _contains_forbidden_value(value):
            warn(f"dropped forbidden trace argument: {key}")
            continue
        if key in ("summary", "description"):
            value = _bound_text(value, TRACE_MAX_TEXT)
        cleaned[key] = value
    return cleaned


def _scrub_result(result: Any) -> dict[str, Any] | None:
    if not isinstance(result, dict):
        return None
    cleaned = {key: result[key] for key in ALLOWED_RESULT_KEYS if key in result and not _contains_forbidden_value(result[key])}
    return cleaned or None


# DD: DD-914
# Implements: ARCH-033
# Title: scrub_and_bound_triple Varambu minimal scrubbed intent record builder
def scrub_and_bound_triple(triple: dict[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {"correlation_id": triple.get("correlation_id")}
    user_message = triple.get("user_message")
    if isinstance(user_message, str):
        record["user_message"] = _bound_text(user_message, TRACE_MAX_USER_MESSAGE)
    if triple.get("tool_name") is not None:
        record["tool_name"] = triple["tool_name"]
    if triple.get("arguments") is not None:
        record["arguments"] = _scrub_arguments(triple["arguments"])
    result = _scrub_result(triple.get("result"))
    if result is not None:
        record["result"] = result
    return record


# DD: DD-923
# Implements: ARCH-033
# Title: write_trace_file Varambu idempotent scrubbed intent persistor
def write_trace_file(path: Any, records: list[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(rec, separators=(",", ":"), ensure_ascii=True, sort_keys=True) for rec in records]
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")


def _seq(leg: Any) -> int:
    return leg.get("sequence", 0) if isinstance(leg, dict) else 0


def _first_wins(existing: dict[str, Any] | None, candidate: dict[str, Any]) -> dict[str, Any]:
    if existing is None or _seq(candidate) < _seq(existing):
        return candidate
    return existing


def _leg_timestamp_utc(leg: Any) -> str | None:
    if not isinstance(leg, dict):
        return None
    return leg.get("timestamp_utc") or leg.get("timestamp")


def _anchor_cids(adapters: list[dict[str, Any]], gateways: list[dict[str, Any]]) -> set[str]:
    cids: set[str] = set()
    for rec in list(adapters) + list(gateways):
        cid = rec.get("correlation_id")
        if cid:
            cids.add(cid)
    return cids


def _attach_ts(leg: dict[str, Any], ts: Any, seq: Any) -> None:
    if ts is not None:
        leg["timestamp"] = ts
    if seq is not None:
        leg["sequence"] = seq


def _intent_legs(triple: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    intent: dict[str, Any] | None = None
    if triple.get("user_message") is not None:
        intent = {"user_message": triple["user_message"]}
        _attach_ts(intent, triple.get("intent_timestamp"), triple.get("intent_sequence"))
    action: dict[str, Any] | None = None
    if triple.get("tool_name") is not None:
        action = {"tool_name": triple["tool_name"], "arguments": triple.get("arguments")}
        _attach_ts(action, triple.get("action_timestamp"), triple.get("action_sequence"))
    return intent, action


def _place_intents(legs_by_cid: dict[str, dict[str, Any]], intents: list[dict[str, Any]]) -> None:
    for triple in intents:
        legs = legs_by_cid.get(triple.get("correlation_id"))
        if legs is None:
            continue
        intent_leg, action_leg = _intent_legs(triple)
        if intent_leg is not None and legs["intent"] is None:
            legs["intent"] = intent_leg
        if action_leg is not None and legs["action"] is None:
            legs["action"] = action_leg


def _place_records(legs_by_cid: dict[str, dict[str, Any]], records: list[dict[str, Any]], slot_for) -> None:
    for rec in records:
        legs = legs_by_cid.get(rec.get("correlation_id"))
        if legs is None:
            continue
        slot = slot_for(rec)
        legs[slot] = _first_wins(legs[slot], rec)


def _chain_sort_key(chain: dict[str, Any]) -> str:
    stamps = [_leg_timestamp_utc(chain["legs"][slot]) for slot in IN_BOUNDARY_LEGS]
    present = [ts for ts in stamps if ts]
    return min(present) if present else ""


_GATEWAY_LEG_FIELDS = ("correlation_id", "aud", "act", "res", "project_key", "token_project", "token_id", "root_token_id", "budget_remaining")


# DD: DD-924
# Implements: ARCH-033
# Title: derive_gateway_upstream Varambu gateway-enforcement / upstream-call leg splitter
def derive_gateway_upstream(gateway: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Split one jiramcp_gateway_decision into the gateway-enforcement leg and the
    upstream-call leg. Enforcement passed iff the request reached the upstream call
    (upstream_called) or the gateway recorded an allow; a deny with upstream_called
    is an upstream failure, not a gateway denial."""
    upstream_called = bool(gateway.get("upstream_called"))
    allowed = gateway.get("decision") == "allow" or upstream_called
    gw_leg: dict[str, Any] = {
        "leg_status": "allow" if allowed else "deny",
        "sequence": gateway.get("sequence"),
        "timestamp": gateway.get("timestamp"),
    }
    for key in _GATEWAY_LEG_FIELDS:
        if key in gateway:
            gw_leg[key] = gateway[key]
    if not allowed:
        gw_leg["reason_code"] = gateway.get("reason_code")
    up_leg: dict[str, Any] | None = None
    if upstream_called:
        status = gateway.get("upstream_status")
        ok = isinstance(status, int) and 200 <= status < 300
        up_leg = {
            "leg_status": "ok" if ok else "fail",
            "correlation_id": gateway.get("correlation_id"),
            "upstream_operation": gateway.get("upstream_operation"),
            "upstream_status": status,
            "sequence": gateway.get("sequence"),
            "timestamp": gateway.get("timestamp"),
        }
        if gateway.get("upstream_error_detail") is not None:
            up_leg["upstream_error_detail"] = gateway["upstream_error_detail"]
    return gw_leg, up_leg


def _split_gateway_leg(legs: dict[str, Any]) -> None:
    raw = legs.get("gateway")
    if isinstance(raw, dict) and ("decision" in raw or "upstream_called" in raw):
        gw_leg, up_leg = derive_gateway_upstream(raw)
        legs["gateway"] = gw_leg
        if up_leg is not None:
            legs["upstream"] = up_leg


# DD: DD-915
# Implements: ARCH-033
# Title: assemble_chains Varambu correlation-grouped chain assembler
def assemble_chains(*, intents: list[dict[str, Any]], adapters: list[dict[str, Any]], mints: list[dict[str, Any]], gateways: list[dict[str, Any]]) -> list[dict[str, Any]]:
    anchors = _anchor_cids(adapters, gateways)
    legs_by_cid = {cid: {name: None for name in CHAIN_LEG_ORDER} for cid in anchors}
    _place_intents(legs_by_cid, intents)
    _place_records(legs_by_cid, adapters, lambda rec: "adapter_request" if rec.get("event_type") == "adapter_request" else "adapter_decision")
    _place_records(legs_by_cid, mints, lambda _rec: "mint")
    _place_records(legs_by_cid, gateways, lambda _rec: "gateway")
    for legs in legs_by_cid.values():
        _split_gateway_leg(legs)
    chains = [{"correlation_id": cid, "legs": legs_by_cid[cid]} for cid in legs_by_cid]
    chains.sort(key=_chain_sort_key)
    return chains


def _safe_zone(tz: str | None):
    if not tz or ZoneInfo is None:
        return None
    try:
        return ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError):
        return None


def _parse_iso(ts: Any) -> datetime | None:
    if not isinstance(ts, str) or not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _to_local(ts_utc: Any, tz: str | None) -> str:
    if not ts_utc:
        return "-"
    parsed = _parse_iso(ts_utc)
    if parsed is None:
        return str(ts_utc)
    zone = _safe_zone(tz)
    if zone is not None:
        parsed = parsed.astimezone(zone)
    return parsed.strftime("%Y-%m-%d %H:%M:%S %Z").strip()


def _delta_advisory(start: Any, ts: Any) -> str:
    begin, here = _parse_iso(start), _parse_iso(ts)
    if begin is None or here is None:
        return "+0s advisory"
    return f"+{(here - begin).total_seconds():.0f}s advisory"


def _scrub_leg(leg: Any) -> dict[str, Any]:
    if not isinstance(leg, dict):
        return {}
    return {k: v for k, v in leg.items() if k not in FORBIDDEN_FIELD_NAMES and not _contains_forbidden_value(v)}


def _chain_start_utc(legs: dict[str, Any]) -> str | None:
    stamps = [_leg_timestamp_utc(legs[slot]) for slot in CHAIN_LEG_ORDER]
    present = [ts for ts in stamps if ts]
    return min(present) if present else None


_LABEL_W = 16
_TIME_W = 11
_STATUS_W = 11
_DETAIL_INDENT = 2 + 2 + 2 + _LABEL_W + _TIME_W + _STATUS_W  # leading + num + gap + columns
_INNER_LABEL_W = 9
_RULE = "━" * 78


def _local_hms(ts: Any, tz: str | None) -> str:
    if not ts:
        return "—"
    parsed = _parse_iso(ts)
    if parsed is None:
        return str(ts)
    zone = _safe_zone(tz)
    if zone is not None:
        parsed = parsed.astimezone(zone)
    return parsed.strftime("%H:%M:%S")


def _fmt_args(arguments: Any) -> str:
    if not isinstance(arguments, dict):
        return _display(arguments)
    return " ".join(f"{k}={arguments[k]}" for k in sorted(arguments))


def _mint_validity(leg: dict[str, Any]) -> str | None:
    parts = []
    if leg.get("issued_at_local"):
        parts.append(f"issued {leg['issued_at_local']}")
    if leg.get("expires_at_local"):
        parts.append(f"expires {leg['expires_at_local']}")
    if "ttl_seconds" in leg:
        parts.append(f"ttl {leg['ttl_seconds']}s")
    return " · ".join(parts) if parts else None


def _detail_intent(leg, _mode):
    return [("Prompt", leg.get("user_message"))]


def _detail_action(leg, _mode):
    return [("Tool", leg.get("tool_name")), ("Args", _fmt_args(leg.get("arguments")))]


def _detail_from_codex(leg, _mode):
    return [("Mapped", f"{_display(leg.get('tool_name'))} → {_display(leg.get('res'))}")]


def _detail_mint(leg, _mode):
    return [
        ("From", _display(leg.get("subject_spiffe_id"))),
        ("Token", leg.get("token_id")),
        ("Root", leg.get("root_token_id")),
        ("Grant", f"{_display(leg.get('act'))} → {_display(leg.get('res'))}"),
        ("For", f"aud {_display(leg.get('aud'))} · depth {_display(leg.get('delegation_depth'))}"),
        ("Validity", _mint_validity(leg)),
        ("Policy", f"{_display(leg.get('policy_id'))} ({_display(leg.get('policy_hash'))})"),
    ]


def _detail_gateway(leg, _mode):
    if leg.get("leg_status") == "deny":
        return [("Denied", _humanize_reason(str(leg.get("reason_code", "-"))))]
    rows = [
        ("Verified", f"aud {_display(leg.get('aud'))} · act {_display(leg.get('act'))}"),
        ("Project", f"request {_display(leg.get('project_key'))} = token {_display(leg.get('token_project'))}"),
    ]
    if leg.get("budget_remaining") is not None:
        rows.append(("Budget", f"remaining {leg.get('budget_remaining')}"))
    return rows


def _detail_upstream(leg, mode):
    op = _display(leg.get("upstream_operation"))
    status = leg.get("upstream_status")
    rows = [("Call", f"{op} → {_display(status)} (gateway-attested, {mode})")]
    detail = leg.get("upstream_error_detail")
    if leg.get("leg_status") != "ok" and detail:
        rows.append(("Jira", detail))
    return rows


def _detail_return(leg, _mode):
    if leg.get("ok"):
        rows = [("Result", "ok")]
        if leg.get("key"):
            rows.append(("Issue", leg.get("key")))
        return rows
    rows = [("Result", f"reason={_display(leg.get('reason'))}")]
    if leg.get("capiss_reason"):
        rows.append(("Capiss", leg.get("capiss_reason")))
    return rows


_DETAIL_BUILDERS = {
    "intent": _detail_intent,
    "action": _detail_action,
    "adapter_request": _detail_from_codex,
    "mint": _detail_mint,
    "gateway": _detail_gateway,
    "upstream": _detail_upstream,
    "adapter_decision": _detail_return,
}


def _status_token(slot: str, leg: dict[str, Any]) -> str:
    if slot == "mint":
        result = str(leg.get("result", "")).upper()
        return "OK" if result == "ALLOW" else ("DENIED" if result == "DENY" else "")
    if slot == "gateway":
        return "ALLOW" if leg.get("leg_status") == "allow" else "DENY"
    if slot == "upstream":
        return f"{_display(leg.get('upstream_status'))} {'OK' if leg.get('leg_status') == 'ok' else 'FAIL'}"
    if slot == "adapter_decision":
        return "OK" if leg.get("ok") else "FAIL"
    return ""


def _color_status(token: str) -> str:
    if not token:
        return token
    upper = token.upper()
    if "FAIL" in upper or upper in ("DENY", "DENIED"):
        return _tty_color(token, _RED)
    if upper in ("OK", "ALLOW") or upper.endswith(" OK"):
        return _tty_color(token, _GREEN)
    return token


def _color_outcome(outcome: str) -> str:
    lowered = outcome.lower()
    if lowered == "ok":
        return _tty_color(outcome, _GREEN)
    if lowered == "in progress":
        return _tty_color(outcome, _YELLOW)
    return _tty_color(outcome, _RED)


def _detail_text(label: str, value: Any, indent: int) -> list[str]:
    plain_label = f"{label:<{_INNER_LABEL_W}} "
    label_part = _tty_color(plain_label, _CYAN)
    avail = max(20, 100 - indent - len(plain_label))
    wrapped = textwrap.wrap(_display(value), width=avail) or [""]
    pad = " " * (indent + len(plain_label))
    return [label_part + wrapped[0]] + [pad + line for line in wrapped[1:]]


def _present_pairs(slot: str, leg: dict[str, Any], mode: str) -> list[tuple[str, Any]]:
    pairs = _DETAIL_BUILDERS[slot](leg, mode)
    return [(label, value) for label, value in pairs if value is not None and str(value) != ""]


def _render_leg_lines(num: int, slot: str, leg: Any, tz: str | None, mode: str) -> list[str]:
    label = LEG_LABELS[slot]
    if leg is None:
        return [f"  {num:>2}  {label:<{_LABEL_W}}{'—':<{_TIME_W}}{'':<{_STATUS_W}}not yet available"]
    leg = _scrub_leg(leg)
    time_s = _local_hms(_leg_timestamp_utc(leg), tz)
    token = _status_token(slot, leg)
    status_cell = _color_status(token) + " " * max(1, _STATUS_W - len(token))
    spine = f"  {num:>2}  {label:<{_LABEL_W}}{time_s:<{_TIME_W}}{status_cell}"
    pairs = _present_pairs(slot, leg, mode)
    if not pairs:
        return [spine.rstrip()]
    first = _detail_text(pairs[0][0], pairs[0][1], _DETAIL_INDENT)
    lines = [spine + first[0]] + first[1:]
    for next_label, next_value in pairs[1:]:
        rendered = _detail_text(next_label, next_value, _DETAIL_INDENT)
        lines.append(" " * _DETAIL_INDENT + rendered[0])
        lines.extend(rendered[1:])
    return lines


def _chain_title(legs: dict[str, Any]) -> str:
    for slot in ("action", "adapter_request"):
        leg = legs.get(slot)
        if isinstance(leg, dict) and leg.get("tool_name"):
            project = leg.get("project_key")
            if not project and isinstance(leg.get("arguments"), dict):
                project = leg["arguments"].get("project_key")
            return f"{leg['tool_name']}  {_display(project)}".rstrip()
    return "M5 request"


def _chain_outcome(legs: dict[str, Any]) -> str:
    ret = legs.get("adapter_decision")
    if isinstance(ret, dict):
        return "ok" if ret.get("ok") else f"failed ({_display(ret.get('reason'))})"
    mint = legs.get("mint")
    if isinstance(mint, dict) and str(mint.get("result", "")).upper() == "DENY":
        return "mint denied"
    upstream = legs.get("upstream")
    if isinstance(upstream, dict) and upstream.get("leg_status") == "fail":
        return f"upstream {_display(upstream.get('upstream_status'))} failed"
    gateway = legs.get("gateway")
    if isinstance(gateway, dict) and gateway.get("leg_status") == "deny":
        return "gateway denied"
    return "in progress"


# DD: DD-916
# Implements: ARCH-033
# Title: render_chain Varambu human full-audit-trace renderer
def render_chain(chain: dict[str, Any], *, tz: str | None = None, mode: str = "mock") -> str:
    legs = chain["legs"]
    start = _chain_start_utc(legs)
    title = _tty_color(_chain_title(legs), _BLUE)
    outcome = _color_outcome(_chain_outcome(legs))
    column_header = _tty_color(
        f"  {'#':>2}  {'LEG':<{_LABEL_W}}{'TIME':<{_TIME_W}}{'STATUS':<{_STATUS_W}}DETAIL",
        _YELLOW,
    )
    header = (
        f"{_RULE}\n"
        f"  {title}  ·  {outcome}\n"
        f"  cid {chain['correlation_id']}   {_to_local(start, tz)}\n"
        f"{column_header}"
    )
    out = [header]
    for index, slot in enumerate(CHAIN_LEG_ORDER, start=1):
        out.extend(_render_leg_lines(index, slot, legs[slot], tz, mode))
    out.append(_RULE)
    return "\n".join(out) + "\n"


def _leg_json(slot: str, leg: Any, start: Any, tz: str | None) -> dict[str, Any]:
    if leg is None:
        return {"leg": slot, "present": False}
    leg = _scrub_leg(leg)
    entry: dict[str, Any] = {"leg": slot, "present": True, "fields": leg}
    ts = _leg_timestamp_utc(leg)
    if ts:
        entry["timestamp_utc"] = ts
        entry["timestamp_local"] = _to_local(ts, tz)
        entry["elapsed_advisory"] = _delta_advisory(start, ts)
    if "sequence" in leg:
        entry["sequence"] = leg["sequence"]
    return entry


# DD: DD-922
# Implements: ARCH-033
# Title: render_chain_json Varambu machine-readable full-audit-trace renderer
def render_chain_json(chain: dict[str, Any], *, tz: str | None = None) -> dict[str, Any]:
    legs = chain["legs"]
    start = _chain_start_utc(legs)
    return {
        "correlation_id": chain["correlation_id"],
        "start_utc": start,
        "legs": [_leg_json(slot, legs[slot], start, tz) for slot in CHAIN_LEG_ORDER],
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _read_source(path: Path, normalizer) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sequence, raw in enumerate(_load_jsonl(path), start=1):
        record = normalizer(raw, sequence)
        if record is not None:
            out.append(record)
    return out


def _load_rollout(session: Path) -> list[dict[str, Any]]:
    home = session / "codex-home"
    if not home.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(home.rglob("rollout-*.jsonl")):
        records.extend(_load_jsonl(path))
    return records


def _persist_trace(session: Path, triples: list[dict[str, Any]]) -> None:
    records = [scrub_and_bound_triple(t) for t in triples if t.get("user_message") is not None or t.get("tool_name") is not None]
    write_trace_file(session / "trace.jsonl", records)


def _trace_session(session: Path) -> list[dict[str, Any]]:
    mints = _read_source(session / "capiss_audit.jsonl", normalize_event)
    gateways = _read_source(session / "gateway_audit.jsonl", normalize_gateway_event)
    adapters = _read_source(session / "adapter_audit.jsonl", normalize_adapter_event)
    rollout = _load_rollout(session)
    triples = [find_intent_triple(rollout, cid) for cid in _anchor_cids(adapters, gateways)]
    _persist_trace(session, triples)
    return assemble_chains(intents=triples, adapters=adapters, mints=mints, gateways=gateways)


def _resolve_sessions(args: argparse.Namespace) -> list[Path]:
    if getattr(args, "all", False):
        root = Path(getattr(args, "sessions_root", "") or "")
        if root.exists():
            return [p for p in sorted(root.iterdir()) if p.is_dir()]
    session = Path(args.session)
    return [session] if session.exists() else []


def _emit_trace(chains: list[dict[str, Any]], args: argparse.Namespace) -> None:
    if getattr(args, "cid", None):
        chains = [c for c in chains if c["correlation_id"] == args.cid]
    tz = getattr(args, "tz", None)
    if getattr(args, "json", False):
        print(json.dumps([render_chain_json(c, tz=tz) for c in chains]))
        return
    if not chains:
        print("No matching trace chains found for the current Varambu session.")
        return
    mode = getattr(args, "mode", "mock")
    for chain in chains:
        print(render_chain(chain, tz=tz, mode=mode))


# DD: DD-917
# Implements: ARCH-033
# Title: trace Varambu full-chain assemble-on-read command
def trace(args: argparse.Namespace) -> int:
    sessions = _resolve_sessions(args)
    if not sessions:
        print("No Varambu session found yet. Run varambu start first.")
        return 0
    chains: list[dict[str, Any]] = []
    for session in sessions:
        chains.extend(_trace_session(session))
    _emit_trace(chains, args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Varambu audit log helper")
    sub = parser.add_subparsers(dest="command", required=True)

    tail_parser = sub.add_parser("tail")
    tail_parser.add_argument("--since", required=True)
    tail_parser.add_argument("--jsonl", required=True)
    tail_parser.add_argument("--human", required=True)
    tail_parser.add_argument("--err", type=Path, required=True)
    tail_parser.add_argument("--container", default=DEFAULT_CONTAINER)
    tail_parser.add_argument("--source", choices=["capiss", "gateway"], default="capiss")
    tail_parser.add_argument("--verbose", action="store_true")
    tail_parser.set_defaults(func=tail)

    show_parser = sub.add_parser("show")
    show_parser.add_argument("--file", required=True)
    show_parser.add_argument("--follow", action="store_true")
    show_parser.set_defaults(func=show)

    trace_parser = sub.add_parser("trace")
    trace_parser.add_argument("--session", required=True)
    trace_parser.add_argument("--sessions-root", dest="sessions_root", default="")
    trace_parser.add_argument("--cid", default=None)
    trace_parser.add_argument("--all", action="store_true")
    trace_parser.add_argument("--json", action="store_true")
    trace_parser.add_argument("--tz", default=None)
    trace_parser.add_argument("--mode", default="mock")
    trace_parser.set_defaults(func=trace)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
