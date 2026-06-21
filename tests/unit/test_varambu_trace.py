from __future__ import annotations

import argparse
import json
from pathlib import Path

from tests.unit.shared.loaders import REPO_ROOT, load_module_from_path


VARAMBU_AUDIT_PATH = Path(REPO_ROOT, "scripts", "varambu_audit.py")
UUID_A = "11111111-1111-4111-8111-111111111111"
UUID_B = "22222222-2222-4222-8222-222222222222"
UUID_C = "33333333-3333-4333-8333-333333333333"


def _load():
    return load_module_from_path(VARAMBU_AUDIT_PATH, "varambu_audit_test")


# ---------------------------------------------------------------------------
# Rollout record builders (codex-cli 0.139.0 shape, per validated Join Algorithm)
# ---------------------------------------------------------------------------
def _user_message(text: str, ts: str = "2026-06-19T10:00:00.000Z") -> dict:
    return {"type": "event_msg", "timestamp": ts, "payload": {"type": "user_message", "message": text}}


def _function_call(name: str, call_id: str, arguments: dict, ts: str = "2026-06-19T10:00:01.000Z") -> dict:
    return {
        "type": "response_item",
        "timestamp": ts,
        "payload": {
            "type": "function_call",
            "name": name,
            "call_id": call_id,
            "arguments": json.dumps(arguments, separators=(",", ":")),
            "namespace": "jira-mcp",
        },
    }


def _function_call_output(call_id: str, cid: str | None, ok: bool = True, ts: str = "2026-06-19T10:00:02.000Z") -> dict:
    body: dict = {"ok": ok}
    if cid is not None:
        body["correlation_id"] = cid
    return {
        "type": "response_item",
        "timestamp": ts,
        "payload": {"type": "function_call_output", "call_id": call_id, "output": json.dumps(body)},
    }


def _mcp_tool_call_end(call_id: str, cid: str, ts: str = "2026-06-19T10:00:02.000Z") -> dict:
    text = json.dumps({"ok": True, "correlation_id": cid})
    return {
        "type": "event_msg",
        "timestamp": ts,
        "payload": {
            "type": "mcp_tool_call_end",
            "call_id": call_id,
            "invocation": {"server": "jira-mcp", "tool": "create_story", "arguments": {}},
            "result": {"Ok": {"content": [{"type": "text", "text": text}]}},
        },
    }


# ===========================================================================
# DD-910  normalize_gateway_event
# ===========================================================================
def _gateway_raw(**over) -> dict:
    raw = {
        "event_type": "jiramcp_gateway_decision",
        "timestamp": "2026-06-19T10:00:03Z",
        "decision": "allow",
        "reason_code": "ok",
        "correlation_id": UUID_A,
        "subject_spiffe_id": "spiffe://varambu.org/codex-jira-mcp-adapter",
        "endpoint": "/mcp/jira/stories",
        "project_key": "IAM",
        "aud": "jira-mcp-gateway",
        "act": "create_story",
        "res": "jira-mcp:/project:IAM",
        "token_id": "tok-1",
        "root_token_id": "root-1",
        "upstream_called": True,
        "upstream_operation": "story_create",
        "upstream_status": 201,
        "issue_key": "IAM-5",
    }
    raw.update(over)
    return raw


# UT: UT-248
# Test Description: Verifies the gateway normalizer accepts jiramcp_gateway_decision, sequences it, and keeps approved fields.
# Precondition: The audit module is loaded and a complete allow gateway decision event is presented.
# Expected Output: A sequenced normalized record retaining decision, correlation, act, res, and upstream fields.
# Covers DD: DD-910
def test_gateway_normalize_accepts_and_keeps_approved_fields(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("normalize gateway allow", lambda: mod.normalize_gateway_event(_gateway_raw(), 4))
    guard.outcome("sequence injected", rec["sequence"] == 4)
    guard.outcome("decision kept", rec["decision"] == "allow")
    guard.outcome("act and res kept", rec["act"] == "create_story" and rec["res"] == "jira-mcp:/project:IAM")
    guard.outcome("upstream fields kept", rec["upstream_called"] is True and rec["upstream_status"] == 201)
    guard.outcome("correlation kept", rec["correlation_id"] == UUID_A)


# UT: UT-249
# Test Description: Verifies the gateway normalizer rejects events that are not jiramcp_gateway_decision.
# Precondition: The audit module is loaded and events with a different and a missing event_type are presented.
# Expected Output: The normalizer returns None for both.
# Covers DD: DD-910
def test_gateway_normalize_rejects_other_event_types(guard):
    mod = guard.premise("module loaded", _load)
    other = guard.exercise("normalize unrelated", lambda: mod.normalize_gateway_event({"event_type": "capiss_mint_decision"}, 1))
    missing = guard.exercise("normalize missing type", lambda: mod.normalize_gateway_event({"decision": "allow"}, 2))
    guard.outcome("unrelated returns none", other is None)
    guard.outcome("missing type returns none", missing is None)


# UT: UT-250
# Test Description: Verifies the gateway normalizer drops unknown fields with a warning while keeping approved ones.
# Precondition: The audit module is loaded and a gateway event carries one unknown field.
# Expected Output: The unknown field is absent; approved fields remain.
# Covers DD: DD-910
def test_gateway_normalize_drops_unknown_field(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("normalize with unknown", lambda: mod.normalize_gateway_event(_gateway_raw(surprise="x"), 1))
    guard.outcome("unknown field dropped", "surprise" not in rec)
    guard.outcome("approved field retained", rec["decision"] == "allow")


# UT: UT-251
# Test Description: Verifies the gateway normalizer drops forbidden field names and values carrying secret markers.
# Precondition: The audit module is loaded and a gateway event carries token, Authorization, and a Bearer-bearing approved field.
# Expected Output: Forbidden names are dropped and no secret marker survives in the serialized record.
# Covers DD: DD-910
def test_gateway_normalize_drops_forbidden_names_and_values(guard):
    mod = guard.premise("module loaded", _load)
    raw = _gateway_raw(token="secret", Authorization="Bearer leaked", subject_spiffe_id="Basic abc")
    rec = guard.exercise("normalize forbidden", lambda: mod.normalize_gateway_event(raw, 1))
    serialized = guard.exercise("serialize", lambda: json.dumps(rec, sort_keys=True))
    guard.outcome("forbidden names dropped", "token" not in rec and "Authorization" not in rec)
    guard.outcome("bearer-bearing field dropped", "subject_spiffe_id" not in rec)
    guard.outcome("no secret markers", "Bearer" not in serialized and "Basic" not in serialized and "leaked" not in serialized)


# UT: UT-252
# Test Description: Verifies a deny gateway decision normalizes without upstream fields when they are absent.
# Precondition: The audit module is loaded and a deny event omits upstream_called/operation/status.
# Expected Output: The normalized deny record carries the deny reason and no upstream fields.
# Covers DD: DD-910
def test_gateway_normalize_deny_omits_absent_upstream(guard):
    mod = guard.premise("module loaded", _load)
    raw = {"event_type": "jiramcp_gateway_decision", "timestamp": "2026-06-19T10:00:03Z", "decision": "deny", "reason_code": "budget_exhausted", "correlation_id": UUID_A}
    rec = guard.exercise("normalize deny", lambda: mod.normalize_gateway_event(raw, 1))
    guard.outcome("deny decision kept", rec["decision"] == "deny" and rec["reason_code"] == "budget_exhausted")
    guard.outcome("no upstream_called", "upstream_called" not in rec)
    guard.outcome("no upstream_status", "upstream_status" not in rec)


# ===========================================================================
# DD-911  normalize_adapter_event
# ===========================================================================
def _adapter_request(**over) -> dict:
    raw = {
        "event_type": "adapter_request",
        "timestamp": "2026-06-19T10:00:01Z",
        "correlation_id": UUID_A,
        "tool_name": "create_story",
        "act": "create_story",
        "res": "jira-mcp:/project:IAM",
        "project_key": "IAM",
    }
    raw.update(over)
    return raw


def _adapter_decision(**over) -> dict:
    raw = {
        "event_type": "adapter_decision",
        "timestamp": "2026-06-19T10:00:04Z",
        "correlation_id": UUID_A,
        "ok": True,
        "token_id": "tok-1",
        "root_token_id": "root-1",
        "key": "IAM-5",
    }
    raw.update(over)
    return raw


# UT: UT-253
# Test Description: Verifies the adapter normalizer accepts both adapter_request and adapter_decision events.
# Precondition: The audit module is loaded and one of each adapter event type is presented.
# Expected Output: Both normalize to sequenced records carrying the correlation id.
# Covers DD: DD-911
def test_adapter_normalize_accepts_both_adapter_types(guard):
    mod = guard.premise("module loaded", _load)
    req = guard.exercise("normalize request", lambda: mod.normalize_adapter_event(_adapter_request(), 1))
    dec = guard.exercise("normalize decision", lambda: mod.normalize_adapter_event(_adapter_decision(), 2))
    guard.outcome("request kept", req["event_type"] == "adapter_request" and req["correlation_id"] == UUID_A)
    guard.outcome("decision kept", dec["event_type"] == "adapter_decision" and dec["ok"] is True)


# UT: UT-254
# Test Description: Verifies the adapter normalizer rejects unrelated event types.
# Precondition: The audit module is loaded and an unrelated event is presented.
# Expected Output: The normalizer returns None.
# Covers DD: DD-911
def test_adapter_normalize_rejects_unrelated(guard):
    mod = guard.premise("module loaded", _load)
    other = guard.exercise("normalize unrelated", lambda: mod.normalize_adapter_event({"event_type": "capiss_mint_decision"}, 1))
    guard.outcome("unrelated returns none", other is None)


# UT: UT-255
# Test Description: Verifies the adapter normalizer drops unknown fields while keeping approved ones.
# Precondition: The audit module is loaded and an adapter event carries an unknown field.
# Expected Output: The unknown field is dropped; approved fields remain.
# Covers DD: DD-911
def test_adapter_normalize_drops_unknown(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("normalize unknown", lambda: mod.normalize_adapter_event(_adapter_request(surprise="x"), 1))
    guard.outcome("unknown dropped", "surprise" not in rec)
    guard.outcome("tool_name kept", rec["tool_name"] == "create_story")


# UT: UT-256
# Test Description: Verifies the adapter normalizer retains token identifier metadata but drops forbidden names and bearer values.
# Precondition: The audit module is loaded and an adapter event carries token_id metadata plus a forbidden token and a biscuit value.
# Expected Output: token_id remains; the raw token and biscuit value never appear in the serialized record.
# Covers DD: DD-911
def test_adapter_normalize_keeps_token_metadata_drops_secrets(guard):
    mod = guard.premise("module loaded", _load)
    raw = _adapter_decision(token="raw-biscuit", res="biscuit-leak")
    rec = guard.exercise("normalize secrets", lambda: mod.normalize_adapter_event(raw, 1))
    serialized = guard.exercise("serialize", lambda: json.dumps(rec, sort_keys=True))
    guard.outcome("token_id metadata kept", rec["token_id"] == "tok-1" and rec["root_token_id"] == "root-1")
    guard.outcome("forbidden token name dropped", "token" not in rec)
    guard.outcome("biscuit value field dropped", "res" not in rec)
    guard.outcome("no secret markers", "biscuit" not in serialized and "raw-biscuit" not in serialized)


# UT: UT-257
# Test Description: Verifies a dangling adapter_request (no paired decision) still normalizes cleanly.
# Precondition: The audit module is loaded and only an adapter_request is presented.
# Expected Output: The request normalizes; assembly later marks the decision leg missing.
# Covers DD: DD-911
def test_adapter_normalize_dangling_request(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("normalize dangling", lambda: mod.normalize_adapter_event(_adapter_request(), 1))
    guard.outcome("request normalizes", rec is not None and rec["event_type"] == "adapter_request")


# UT: UT-332
# Test Description: Verifies the adapter normalizer retains the capiss_reason metadata on a mint-denied decision.
# Precondition: The audit module is loaded and an adapter_decision carries a mint-deny reason plus capiss_reason.
# Expected Output: capiss_reason is kept (it is approved adapter metadata, not a secret).
# Covers DD: DD-911
def test_adapter_normalize_keeps_capiss_reason(guard):
    mod = guard.premise("module loaded", _load)
    raw = {"event_type": "adapter_decision", "timestamp": "2026-06-19T10:00:04Z", "correlation_id": UUID_A, "ok": False, "reason": "mint_denied", "status": 403, "capiss_reason": "policy"}
    rec = guard.exercise("normalize mint-deny decision", lambda: mod.normalize_adapter_event(raw, 1))
    guard.outcome("capiss_reason retained", rec["capiss_reason"] == "policy")
    guard.outcome("deny reason retained", rec["reason"] == "mint_denied" and rec["status"] == 403)


# ===========================================================================
# DD-912  extract_correlation_id
# ===========================================================================
# UT: UT-258
# Test Description: Verifies correlation extraction from a function_call_output JSON string.
# Precondition: The audit module is loaded and a function_call_output embeds correlation_id.
# Expected Output: The embedded correlation id is returned.
# Covers DD: DD-912
def test_extract_cid_from_function_call_output(guard):
    mod = guard.premise("module loaded", _load)
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(_function_call_output("call-1", UUID_A)))
    guard.outcome("cid returned", cid == UUID_A)


# UT: UT-259
# Test Description: Verifies correlation extraction from an mcp_tool_call_end result text.
# Precondition: The audit module is loaded and an mcp_tool_call_end result embeds correlation_id.
# Expected Output: The embedded correlation id is returned.
# Covers DD: DD-912
def test_extract_cid_from_mcp_tool_call_end(guard):
    mod = guard.premise("module loaded", _load)
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(_mcp_tool_call_end("call-1", UUID_B)))
    guard.outcome("cid returned", cid == UUID_B)


# UT: UT-260
# Test Description: Verifies correlation extraction returns None when the output carries no correlation id.
# Precondition: The audit module is loaded and a function_call_output omits correlation_id.
# Expected Output: None is returned.
# Covers DD: DD-912
def test_extract_cid_absent_returns_none(guard):
    mod = guard.premise("module loaded", _load)
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(_function_call_output("call-1", None)))
    guard.outcome("none returned", cid is None)


# UT: UT-261
# Test Description: Verifies correlation extraction falls back to a regex path when the output is non-JSON noise.
# Precondition: The audit module is loaded and a function_call_output is non-JSON but contains the id literal.
# Expected Output: The correlation id is recovered by the regex path.
# Covers DD: DD-912
def test_extract_cid_regex_fallback_on_noise(guard):
    mod = guard.premise("module loaded", _load)
    rec = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": f'noise "correlation_id":"{UUID_A}" trailing'}}
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(rec))
    guard.outcome("cid recovered", cid == UUID_A)


# UT: UT-262
# Test Description: Verifies correlation extraction returns None for non-JSON output with no id literal.
# Precondition: The audit module is loaded and a function_call_output is noise with no id.
# Expected Output: None is returned.
# Covers DD: DD-912
def test_extract_cid_malformed_and_absent(guard):
    mod = guard.premise("module loaded", _load)
    rec = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": "just noise"}}
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(rec))
    guard.outcome("none returned", cid is None)


# UT: UT-333
# Test Description: Verifies correlation extraction recovers the id from an escaped MCP-wrapped tool result (JSON-in-JSON).
# Precondition: The audit module is loaded and a function_call_output stores the MCP content wrapper whose inner text holds the escaped correlation_id.
# Expected Output: The embedded correlation id is recovered despite the nested escaping.
# Covers DD: DD-912
def test_extract_cid_from_escaped_mcp_wrapped_output(guard):
    mod = guard.premise("module loaded", _load)
    inner = json.dumps({"ok": False, "correlation_id": UUID_A})
    wrapper = json.dumps({"content": [{"type": "text", "text": inner}]})
    rec = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": wrapper}}
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(rec))
    guard.outcome("cid recovered from nested escaping", cid == UUID_A)


# UT: UT-334
# Test Description: Verifies correlation extraction recovers the id when the output is a structured object rather than a string.
# Precondition: The audit module is loaded and a function_call_output stores the result as a dict (not a serialized string).
# Expected Output: The embedded correlation id is recovered by serializing the structured value.
# Covers DD: DD-912
def test_extract_cid_from_structured_object_output(guard):
    mod = guard.premise("module loaded", _load)
    rec = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": {"content": [{"type": "text", "text": json.dumps({"correlation_id": UUID_A})}]}}}
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(rec))
    guard.outcome("cid recovered from structured object", cid == UUID_A)


# UT: UT-263
# Test Description: Verifies correlation extraction returns the first id and warns when two DISTINCT correlation ids appear in one output.
# Precondition: The audit module is loaded and an output embeds two distinct correlation_id literals.
# Expected Output: The first correlation id is returned (pinned first-match contract) and an anomaly warning is emitted to stderr.
# Covers DD: DD-912
def test_extract_cid_multiple_returns_first(capsys, guard):
    mod = guard.premise("module loaded", _load)
    rec = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": f'"correlation_id":"{UUID_A}" "correlation_id":"{UUID_B}"'}}
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(rec))
    err = capsys.readouterr().err
    guard.outcome("first id returned", cid == UUID_A)
    guard.outcome("anomaly warning emitted", "multiple distinct correlation_ids" in err)


# UT: UT-331
# Test Description: Verifies correlation extraction does not warn when the same correlation id appears twice (benign repeat).
# Precondition: The audit module is loaded and an output embeds the same correlation_id literal twice.
# Expected Output: The correlation id is returned and no anomaly warning is emitted.
# Covers DD: DD-912
def test_extract_cid_identical_repeat_no_warning(capsys, guard):
    mod = guard.premise("module loaded", _load)
    rec = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": f'"correlation_id":"{UUID_A}" ... "correlation_id":"{UUID_A}"'}}
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(rec))
    err = capsys.readouterr().err
    guard.outcome("id returned", cid == UUID_A)
    guard.outcome("no anomaly warning for identical repeat", "multiple distinct correlation_ids" not in err)


# UT: UT-264
# Test Description: Verifies correlation extraction returns None for an empty or missing output value.
# Precondition: The audit module is loaded and a function_call_output has an empty output string.
# Expected Output: None is returned.
# Covers DD: DD-912
def test_extract_cid_empty_output(guard):
    mod = guard.premise("module loaded", _load)
    rec = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c", "output": ""}}
    cid = guard.exercise("extract", lambda: mod.extract_correlation_id(rec))
    guard.outcome("none returned", cid is None)


# ===========================================================================
# DD-913  find_intent_triple  (exhaustive condition coverage, 2^4)
# C1 = correlation_id located in a function_call_output
# C2 = call_id resolves to a function_call
# C3 = function_call.name in {read_project_summary, create_story}
# C4 = a user_message precedes that function_call
# ===========================================================================
def _build_rollout(c1: bool, c2: bool, c3: bool, c4: bool) -> list[dict]:
    """Assemble a rollout exercising the four conditions independently."""
    records: list[dict] = []
    name = "create_story" if c3 else "exec_command"
    if c4:
        records.append(_user_message("create a story for IAM"))
    if c2:  # a resolvable function_call exists
        records.append(_function_call(name, "call-X", {"project_key": "IAM"}))
    if c1:  # an output carrying the target cid (referencing call-X)
        records.append(_function_call_output("call-X", UUID_A))
    return records


def _intent(mod, c1, c2, c3, c4):
    return mod.find_intent_triple(_build_rollout(c1, c2, c3, c4), UUID_A)


# UT: UT-265
# Test Description: find_intent_triple with C1=F,C2=F,C3=F,C4=F yields no triple without crashing.
# Precondition: Module loaded; rollout has no output, no call, non-M5 name, no prompt.
# Expected Output: tool_name, arguments, and user_message are all None.
# Covers DD: DD-913
def test_intent_FFFF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, False, False, False))
    guard.outcome("no action", t["tool_name"] is None and t["arguments"] is None)
    guard.outcome("no intent", t["user_message"] is None)


# UT: UT-266
# Test Description: find_intent_triple with C1=F,C2=F,C3=F,C4=T yields no triple (correlation not found dominates).
# Precondition: Module loaded; only a preceding prompt exists.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_FFFT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, False, False, True))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-267
# Test Description: find_intent_triple with C1=F,C2=F,C3=T,C4=F yields no triple.
# Precondition: Module loaded; no output/cid and no call.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_FFTF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, False, True, False))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-268
# Test Description: find_intent_triple with C1=F,C2=F,C3=T,C4=T yields no triple.
# Precondition: Module loaded; prompt present but no output/cid located.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_FFTT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, False, True, True))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-269
# Test Description: find_intent_triple with C1=F,C2=T,C3=F,C4=F yields no triple.
# Precondition: Module loaded; a call exists but no output ties the cid.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_FTFF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, True, False, False))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-270
# Test Description: find_intent_triple with C1=F,C2=T,C3=F,C4=T yields no triple.
# Precondition: Module loaded; call and prompt exist but no cid output.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_FTFT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, True, False, True))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-271
# Test Description: find_intent_triple with C1=F,C2=T,C3=T,C4=F yields no triple.
# Precondition: Module loaded; M5 call exists but no cid output located.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_FTTF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, True, True, False))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-272
# Test Description: find_intent_triple with C1=F,C2=T,C3=T,C4=T yields no triple (no cid output anchor).
# Precondition: Module loaded; M5 call and prompt present but no cid output.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_FTTT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, False, True, True, True))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-273
# Test Description: find_intent_triple with C1=T,C2=F,C3=F,C4=F yields no triple (output present but call_id unresolved).
# Precondition: Module loaded; output with cid exists but no matching function_call.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_TFFF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, False, False, False))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-274
# Test Description: find_intent_triple with C1=T,C2=F,C3=F,C4=T yields no triple.
# Precondition: Module loaded; cid output and prompt exist but call_id unresolved.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_TFFT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, False, False, True))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-275
# Test Description: find_intent_triple with C1=T,C2=F,C3=T,C4=F yields no triple.
# Precondition: Module loaded; cid output present, no resolvable call.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_TFTF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, False, True, False))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-276
# Test Description: find_intent_triple with C1=T,C2=F,C3=T,C4=T yields no triple.
# Precondition: Module loaded; cid output and prompt present, no resolvable call.
# Expected Output: All triple fields None.
# Covers DD: DD-913
def test_intent_TFTT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, False, True, True))
    guard.outcome("no triple", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-277
# Test Description: find_intent_triple with C1=T,C2=T,C3=F,C4=F filters out a non-M5 call (e.g. exec_command).
# Precondition: Module loaded; cid output resolves to a non-M5 call, no prompt.
# Expected Output: All triple fields None (filtered by name).
# Covers DD: DD-913
def test_intent_TTFF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, True, False, False))
    guard.outcome("filtered out", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-278
# Test Description: find_intent_triple with C1=T,C2=T,C3=F,C4=T filters out a non-M5 call despite a prompt.
# Precondition: Module loaded; cid output resolves to a non-M5 call with a preceding prompt.
# Expected Output: All triple fields None (name not ours).
# Covers DD: DD-913
def test_intent_TTFT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, True, False, True))
    guard.outcome("filtered out", t["tool_name"] is None and t["user_message"] is None)


# UT: UT-279
# Test Description: find_intent_triple with C1=T,C2=T,C3=T,C4=F gives the action but no intent (no preceding prompt).
# Precondition: Module loaded; cid output resolves to an M5 call with no preceding prompt.
# Expected Output: tool_name and arguments present; user_message None.
# Covers DD: DD-913
def test_intent_TTTF(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, True, True, False))
    guard.outcome("action present", t["tool_name"] == "create_story" and t["arguments"] == {"project_key": "IAM"})
    guard.outcome("intent absent", t["user_message"] is None)


# UT: UT-280
# Test Description: find_intent_triple with C1=T,C2=T,C3=T,C4=T yields the complete triple.
# Precondition: Module loaded; cid output resolves to an M5 call with a preceding prompt.
# Expected Output: user_message, tool_name, arguments, and correlation_id all populated.
# Covers DD: DD-913
def test_intent_TTTT(guard):
    mod = guard.premise("module loaded", _load)
    t = guard.exercise("intent", lambda: _intent(mod, True, True, True, True))
    guard.outcome("intent present", t["user_message"] == "create a story for IAM")
    guard.outcome("action present", t["tool_name"] == "create_story" and t["arguments"] == {"project_key": "IAM"})
    guard.outcome("correlation present", t["correlation_id"] == UUID_A)


# --- DD-913 attribution sub-matrix (all conditions true) ---
# UT: UT-281
# Test Description: find_intent_triple attributes the nearest preceding prompt when two precede the call.
# Precondition: Module loaded; two user_messages precede a single M5 call.
# Expected Output: The nearest (later) prompt is selected.
# Covers DD: DD-913
def test_intent_nearest_preceding(guard):
    mod = guard.premise("module loaded", _load)
    rollout = [
        _user_message("far prompt", "2026-06-19T10:00:00.000Z"),
        _user_message("near prompt", "2026-06-19T10:00:00.500Z"),
        _function_call("create_story", "call-X", {"project_key": "IAM"}),
        _function_call_output("call-X", UUID_A),
    ]
    t = guard.exercise("intent", lambda: mod.find_intent_triple(rollout, UUID_A))
    guard.outcome("nearest chosen", t["user_message"] == "near prompt")


# UT: UT-282
# Test Description: One prompt driving two M5 tool calls yields two triples each attributing the same prompt.
# Precondition: Module loaded; single prompt then two M5 calls with two correlation ids.
# Expected Output: Both correlation ids resolve to the same verbatim prompt.
# Covers DD: DD-913
def test_intent_one_turn_two_tools(guard):
    mod = guard.premise("module loaded", _load)
    rollout = [
        _user_message("use jira tools"),
        _function_call("read_project_summary", "call-A", {"project_key": "IAM"}),
        _function_call_output("call-A", UUID_A),
        _function_call("create_story", "call-B", {"project_key": "IAM"}),
        _function_call_output("call-B", UUID_B),
    ]
    ta = guard.exercise("intent A", lambda: mod.find_intent_triple(rollout, UUID_A))
    tb = guard.exercise("intent B", lambda: mod.find_intent_triple(rollout, UUID_B))
    guard.outcome("A maps prompt + read", ta["user_message"] == "use jira tools" and ta["tool_name"] == "read_project_summary")
    guard.outcome("B maps same prompt + create", tb["user_message"] == "use jira tools" and tb["tool_name"] == "create_story")


# UT: UT-283
# Test Description: Interleaved turns attribute each call to its own preceding prompt without cross-attribution.
# Precondition: Module loaded; prompt A->callA, then prompt B->callB.
# Expected Output: A maps to callA, B maps to callB.
# Covers DD: DD-913
def test_intent_interleaved_turns(guard):
    mod = guard.premise("module loaded", _load)
    rollout = [
        _user_message("prompt A", "2026-06-19T10:00:00.000Z"),
        _function_call("read_project_summary", "call-A", {"project_key": "IAM"}, "2026-06-19T10:00:01.000Z"),
        _function_call_output("call-A", UUID_A, ts="2026-06-19T10:00:02.000Z"),
        _user_message("prompt B", "2026-06-19T10:00:03.000Z"),
        _function_call("create_story", "call-B", {"project_key": "IAM"}, "2026-06-19T10:00:04.000Z"),
        _function_call_output("call-B", UUID_B, ts="2026-06-19T10:00:05.000Z"),
    ]
    ta = guard.exercise("intent A", lambda: mod.find_intent_triple(rollout, UUID_A))
    tb = guard.exercise("intent B", lambda: mod.find_intent_triple(rollout, UUID_B))
    guard.outcome("A to prompt A", ta["user_message"] == "prompt A")
    guard.outcome("B to prompt B", tb["user_message"] == "prompt B")


# UT: UT-284
# Test Description: exec_command noise between our call and its output is excluded from attribution.
# Precondition: Module loaded; an M5 call plus an interleaved exec_command call under the same turn.
# Expected Output: The exec call is excluded; our M5 call retains the correct intent.
# Covers DD: DD-913
def test_intent_exec_noise_excluded(guard):
    mod = guard.premise("module loaded", _load)
    rollout = [
        _user_message("create a story"),
        _function_call("create_story", "call-X", {"project_key": "IAM"}),
        _function_call("exec_command", "call-E", {"command": "ls"}),
        _function_call_output("call-E", UUID_C),
        _function_call_output("call-X", UUID_A),
    ]
    t = guard.exercise("intent", lambda: mod.find_intent_triple(rollout, UUID_A))
    exec_t = guard.exercise("exec intent", lambda: mod.find_intent_triple(rollout, UUID_C))
    guard.outcome("our call retained", t["tool_name"] == "create_story" and t["user_message"] == "create a story")
    guard.outcome("exec excluded", exec_t["tool_name"] is None)


# UT: UT-285
# Test Description: mcp_tool_call_end corroboration is optional; the triple is identical with or without it.
# Precondition: Module loaded; a rollout with response_item records, with and without the event_msg corroboration.
# Expected Output: Both produce an identical triple.
# Covers DD: DD-913
def test_intent_mcp_corroboration_optional(guard):
    mod = guard.premise("module loaded", _load)
    base = [
        _user_message("create a story"),
        _function_call("create_story", "call-X", {"project_key": "IAM"}),
        _function_call_output("call-X", UUID_A),
    ]
    with_end = base + [_mcp_tool_call_end("call-X", UUID_A)]
    t1 = guard.exercise("without end", lambda: mod.find_intent_triple(base, UUID_A))
    t2 = guard.exercise("with end", lambda: mod.find_intent_triple(with_end, UUID_A))
    guard.outcome("identical triple", t1 == t2)


# ===========================================================================
# DD-914  scrub_and_bound_triple  (BVA, limits exclusive: len < limit retained)
# ===========================================================================
def _triple(**over) -> dict:
    t = {"correlation_id": UUID_A, "user_message": "hi", "tool_name": "create_story", "arguments": {"project_key": "IAM", "summary": "s", "description": "d"}, "result": {"ok": True, "key": "IAM-5", "status": 201}}
    t.update(over)
    return t


# UT: UT-286
# Test Description: A 2047-byte user_message (B-1) is kept whole.
# Precondition: Module loaded; user_message is one byte below the 2048 limit.
# Expected Output: The message is retained unchanged with no truncation marker.
# Covers DD: DD-914
def test_scrub_user_message_below_limit_kept(guard):
    mod = guard.premise("module loaded", _load)
    msg = "a" * 2047
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(user_message=msg)))
    guard.outcome("kept whole", rec["user_message"] == msg)
    guard.outcome("no marker", "[truncated]" not in rec["user_message"])


# UT: UT-287
# Test Description: A 2048-byte user_message (B, at limit) is truncated with a marker.
# Precondition: Module loaded; user_message equals the exclusive 2048 limit.
# Expected Output: The message is truncated to within the limit and ends with the truncation marker.
# Covers DD: DD-914
def test_scrub_user_message_at_limit_truncated(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(user_message="a" * 2048)))
    guard.outcome("marker appended", rec["user_message"].endswith("[truncated]"))
    guard.outcome("within limit", len(rec["user_message"].encode("utf-8")) <= 2048)


# UT: UT-288
# Test Description: A 2049-byte user_message (B+1) is truncated with a marker.
# Precondition: Module loaded; user_message exceeds the 2048 limit by one byte.
# Expected Output: The message is truncated within the limit and marked.
# Covers DD: DD-914
def test_scrub_user_message_above_limit_truncated(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(user_message="a" * 2049)))
    guard.outcome("marker appended", rec["user_message"].endswith("[truncated]"))
    guard.outcome("within limit", len(rec["user_message"].encode("utf-8")) <= 2048)


# UT: UT-289
# Test Description: A 1023-byte summary (B-1) is kept whole.
# Precondition: Module loaded; arguments.summary is one byte below the 1024 limit.
# Expected Output: summary retained unchanged.
# Covers DD: DD-914
def test_scrub_summary_below_limit_kept(guard):
    mod = guard.premise("module loaded", _load)
    s = "b" * 1023
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(arguments={"project_key": "IAM", "summary": s, "description": "d"})))
    guard.outcome("kept whole", rec["arguments"]["summary"] == s)


# UT: UT-290
# Test Description: A 1024-byte summary (B, at limit) is truncated with a marker.
# Precondition: Module loaded; arguments.summary equals the exclusive 1024 limit.
# Expected Output: summary truncated within the limit and marked.
# Covers DD: DD-914
def test_scrub_summary_at_limit_truncated(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(arguments={"project_key": "IAM", "summary": "b" * 1024, "description": "d"})))
    guard.outcome("marker appended", rec["arguments"]["summary"].endswith("[truncated]"))
    guard.outcome("within limit", len(rec["arguments"]["summary"].encode("utf-8")) <= 1024)


# UT: UT-291
# Test Description: A 1025-byte summary (B+1) is truncated with a marker.
# Precondition: Module loaded; arguments.summary exceeds the 1024 limit by one byte.
# Expected Output: summary truncated within the limit and marked.
# Covers DD: DD-914
def test_scrub_summary_above_limit_truncated(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(arguments={"project_key": "IAM", "summary": "b" * 1025, "description": "d"})))
    guard.outcome("marker appended", rec["arguments"]["summary"].endswith("[truncated]"))
    guard.outcome("within limit", len(rec["arguments"]["summary"].encode("utf-8")) <= 1024)


# UT: UT-292
# Test Description: A 1023-byte description (B-1) is kept whole.
# Precondition: Module loaded; arguments.description is one byte below the 1024 limit.
# Expected Output: description retained unchanged.
# Covers DD: DD-914
def test_scrub_description_below_limit_kept(guard):
    mod = guard.premise("module loaded", _load)
    d = "c" * 1023
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(arguments={"project_key": "IAM", "summary": "s", "description": d})))
    guard.outcome("kept whole", rec["arguments"]["description"] == d)


# UT: UT-293
# Test Description: A 1024-byte description (B, at limit) is truncated with a marker.
# Precondition: Module loaded; arguments.description equals the exclusive 1024 limit.
# Expected Output: description truncated within the limit and marked.
# Covers DD: DD-914
def test_scrub_description_at_limit_truncated(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(arguments={"project_key": "IAM", "summary": "s", "description": "c" * 1024})))
    guard.outcome("marker appended", rec["arguments"]["description"].endswith("[truncated]"))
    guard.outcome("within limit", len(rec["arguments"]["description"].encode("utf-8")) <= 1024)


# UT: UT-294
# Test Description: A 1025-byte description (B+1) is truncated with a marker.
# Precondition: Module loaded; arguments.description exceeds the 1024 limit by one byte.
# Expected Output: description truncated within the limit and marked.
# Covers DD: DD-914
def test_scrub_description_above_limit_truncated(guard):
    mod = guard.premise("module loaded", _load)
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple(arguments={"project_key": "IAM", "summary": "s", "description": "c" * 1025})))
    guard.outcome("marker appended", rec["arguments"]["description"].endswith("[truncated]"))
    guard.outcome("within limit", len(rec["arguments"]["description"].encode("utf-8")) <= 1024)


# UT: UT-295
# Test Description: scrub_and_bound persists only the minimal triple and removes forbidden names/values.
# Precondition: Module loaded; a triple carries forbidden token/Authorization fields and a Bearer value plus extraneous reasoning.
# Expected Output: Only correlation_id, user_message, tool_name, arguments, and bounded result remain; no secrets, no reasoning.
# Covers DD: DD-914
def test_scrub_keeps_minimal_triple_drops_secrets(guard):
    mod = guard.premise("module loaded", _load)
    triple = _triple(token="secret", Authorization="Bearer x", reasoning="model thought", result={"ok": False, "reason": "mint_denied", "status": 403, "token": "leak"})
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(triple))
    serialized = guard.exercise("serialize", lambda: json.dumps(rec, sort_keys=True))
    guard.outcome("only allowed top keys", set(rec) <= {"correlation_id", "user_message", "tool_name", "arguments", "result"})
    guard.outcome("reasoning dropped", "reasoning" not in rec and "model thought" not in serialized)
    guard.outcome("forbidden names dropped", "token" not in rec and "Authorization" not in rec)
    guard.outcome("no secret markers", "Bearer" not in serialized and "leak" not in serialized)
    guard.outcome("result reason kept", rec["result"]["reason"] == "mint_denied" and rec["result"]["status"] == 403)


# UT: UT-296
# Test Description: write_trace_file is idempotent — re-writing the same inputs produces identical bytes.
# Precondition: Module loaded; a scrubbed record is written twice to a temp file.
# Expected Output: Both writes produce byte-identical file content.
# Covers DD: DD-923
def test_scrub_write_trace_file_idempotent(tmp_path, guard):
    mod = guard.premise("module loaded", _load)
    path = tmp_path / "trace.jsonl"
    rec = guard.exercise("scrub", lambda: mod.scrub_and_bound_triple(_triple()))
    guard.exercise("write first", lambda: mod.write_trace_file(path, [rec]))
    first = guard.exercise("read first", lambda: path.read_bytes())
    guard.exercise("write second", lambda: mod.write_trace_file(path, [rec]))
    second = guard.exercise("read second", lambda: path.read_bytes())
    guard.outcome("identical bytes", first == second)


# ===========================================================================
# DD-915  assemble_chains
# ===========================================================================
def _sources_for_complete(cid=UUID_A):
    intents = [{"correlation_id": cid, "user_message": "create a story", "tool_name": "create_story", "arguments": {"project_key": "IAM"}}]
    adapters = [
        mod_request(cid),
        {"event_type": "adapter_decision", "sequence": 2, "correlation_id": cid, "ok": True, "timestamp": "2026-06-19T10:00:04Z"},
    ]
    mints = [{"event_type": "capiss_mint_decision", "sequence": 1, "correlation_id": cid, "result": "allow", "reason_code": "ok", "timestamp_utc": "2026-06-19T10:00:02Z"}]
    gateways = [{"event_type": "jiramcp_gateway_decision", "sequence": 1, "correlation_id": cid, "decision": "allow", "reason_code": "ok", "upstream_called": True, "upstream_operation": "story_create", "upstream_status": 201, "timestamp": "2026-06-19T10:00:03Z"}]
    return intents, adapters, mints, gateways


def mod_request(cid, seq=1, ts="2026-06-19T10:00:01Z"):
    return {"event_type": "adapter_request", "sequence": seq, "correlation_id": cid, "tool_name": "create_story", "act": "create_story", "res": "jira-mcp:/project:IAM", "project_key": "IAM", "timestamp": ts}


def _assemble(mod, intents, adapters, mints, gateways):
    return mod.assemble_chains(intents=intents, adapters=adapters, mints=mints, gateways=gateways)


# UT: UT-297
# Test Description: A complete chain assembles all seven legs in canonical order for one correlation id.
# Precondition: Module loaded; intent, action, adapter_request, mint, gateway, upstream, adapter_decision all present.
# Expected Output: One chain whose legs dict carries every leg populated in the 7-leg canonical order.
# Covers DD: DD-915
def test_assemble_complete_chain(guard):
    mod = guard.premise("module loaded", _load)
    guard.outcome("canonical order is seven legs", mod.CHAIN_LEG_ORDER == ["intent", "action", "adapter_request", "mint", "gateway", "upstream", "adapter_decision"])
    chains = guard.exercise("assemble", lambda: _assemble(mod, *_sources_for_complete()))
    guard.outcome("one chain", len(chains) == 1)
    legs = chains[0]["legs"]
    guard.outcome("all seven legs present", all(legs[name] is not None for name in mod.CHAIN_LEG_ORDER))
    guard.outcome("canonical order", list(legs.keys()) == mod.CHAIN_LEG_ORDER)
    guard.outcome("gateway leg is enforcement allow", legs["gateway"]["leg_status"] == "allow")
    guard.outcome("upstream leg is ok with status", legs["upstream"]["leg_status"] == "ok" and legs["upstream"]["upstream_status"] == 201)


# UT: UT-298
# Test Description: Removing the intent leg leaves it marked absent while others stay intact.
# Precondition: Module loaded; the intent triple is removed.
# Expected Output: legs.intent is None; other legs present.
# Covers DD: DD-915
def test_assemble_missing_intent(guard):
    mod = guard.premise("module loaded", _load)
    _, adapters, mints, gateways = _sources_for_complete()
    chains = guard.exercise("assemble", lambda: _assemble(mod, [], adapters, mints, gateways))
    guard.outcome("intent absent", chains[0]["legs"]["intent"] is None)
    guard.outcome("mint present", chains[0]["legs"]["mint"] is not None)


# UT: UT-299
# Test Description: Removing the mint leg leaves it marked absent while others stay intact.
# Precondition: Module loaded; the capiss mint record is removed.
# Expected Output: legs.mint is None; other legs present.
# Covers DD: DD-915
def test_assemble_missing_mint(guard):
    mod = guard.premise("module loaded", _load)
    intents, adapters, _, gateways = _sources_for_complete()
    chains = guard.exercise("assemble", lambda: _assemble(mod, intents, adapters, [], gateways))
    guard.outcome("mint absent", chains[0]["legs"]["mint"] is None)
    guard.outcome("gateway present", chains[0]["legs"]["gateway"] is not None)


# UT: UT-300
# Test Description: Removing the gateway leg leaves it marked absent while others stay intact.
# Precondition: Module loaded; the gateway record is removed.
# Expected Output: legs.gateway is None; other legs present.
# Covers DD: DD-915
def test_assemble_missing_gateway(guard):
    mod = guard.premise("module loaded", _load)
    intents, adapters, mints, _ = _sources_for_complete()
    chains = guard.exercise("assemble", lambda: _assemble(mod, intents, adapters, mints, []))
    guard.outcome("gateway absent", chains[0]["legs"]["gateway"] is None)
    guard.outcome("upstream absent", chains[0]["legs"]["upstream"] is None)
    guard.outcome("adapter_request present", chains[0]["legs"]["adapter_request"] is not None)


# UT: UT-301
# Test Description: Removing the adapter_request leg leaves it absent while the decision leg remains an anchor.
# Precondition: Module loaded; only adapter_decision remains for the adapter source.
# Expected Output: legs.adapter_request is None; legs.adapter_decision present; chain still surfaced.
# Covers DD: DD-915
def test_assemble_missing_adapter_request(guard):
    mod = guard.premise("module loaded", _load)
    intents, adapters, mints, gateways = _sources_for_complete()
    only_decision = [a for a in adapters if a["event_type"] == "adapter_decision"]
    chains = guard.exercise("assemble", lambda: _assemble(mod, intents, only_decision, mints, gateways))
    guard.outcome("adapter_request absent", chains[0]["legs"]["adapter_request"] is None)
    guard.outcome("adapter_decision present", chains[0]["legs"]["adapter_decision"] is not None)


# UT: UT-302
# Test Description: Removing the adapter_decision leg leaves it absent while the request leg remains an anchor.
# Precondition: Module loaded; only adapter_request remains for the adapter source.
# Expected Output: legs.adapter_decision is None; legs.adapter_request present.
# Covers DD: DD-915
def test_assemble_missing_adapter_decision(guard):
    mod = guard.premise("module loaded", _load)
    intents, adapters, mints, gateways = _sources_for_complete()
    only_request = [a for a in adapters if a["event_type"] == "adapter_request"]
    chains = guard.exercise("assemble", lambda: _assemble(mod, intents, only_request, mints, gateways))
    guard.outcome("adapter_decision absent", chains[0]["legs"]["adapter_decision"] is None)
    guard.outcome("adapter_request present", chains[0]["legs"]["adapter_request"] is not None)


# UT: UT-303
# Test Description: Removing the action leg (rollout tool call) leaves it absent while the intent prompt remains.
# Precondition: Module loaded; the intent triple has user_message but no tool_name/arguments.
# Expected Output: legs.action is None; legs.intent present.
# Covers DD: DD-915
def test_assemble_missing_action(guard):
    mod = guard.premise("module loaded", _load)
    _, adapters, mints, gateways = _sources_for_complete()
    intents = [{"correlation_id": UUID_A, "user_message": "create a story", "tool_name": None, "arguments": None}]
    chains = guard.exercise("assemble", lambda: _assemble(mod, intents, adapters, mints, gateways))
    guard.outcome("action absent", chains[0]["legs"]["action"] is None)
    guard.outcome("intent present", chains[0]["legs"]["intent"] is not None)


# UT: UT-304
# Test Description: A denied mint produces a partial chain that ends at the mint deny with later legs absent.
# Precondition: Module loaded; intent, adapter_request, and a deny mint exist; no gateway or adapter_decision.
# Expected Output: legs.mint deny present; legs.gateway and legs.adapter_decision None (not errors).
# Covers DD: DD-915
def test_assemble_denied_mint_partial(guard):
    mod = guard.premise("module loaded", _load)
    intents = [{"correlation_id": UUID_A, "user_message": "read NAS", "tool_name": "read_project_summary", "arguments": {"project_key": "NAS"}}]
    adapters = [mod_request(UUID_A)]
    mints = [{"event_type": "capiss_mint_decision", "sequence": 1, "correlation_id": UUID_A, "result": "deny", "reason_code": "policy", "timestamp_utc": "2026-06-19T10:00:02Z"}]
    chains = guard.exercise("assemble", lambda: _assemble(mod, intents, adapters, mints, []))
    guard.outcome("mint deny present", chains[0]["legs"]["mint"]["result"] == "deny")
    guard.outcome("gateway absent", chains[0]["legs"]["gateway"] is None)
    guard.outcome("upstream absent", chains[0]["legs"]["upstream"] is None)
    guard.outcome("adapter_decision absent", chains[0]["legs"]["adapter_decision"] is None)


# UT: UT-305
# Test Description: Events for two correlation ids assemble into two chains with no cross-leg leakage.
# Precondition: Module loaded; interleaved sources for two correlation ids.
# Expected Output: Two distinct chains, each carrying only its own legs.
# Covers DD: DD-915
def test_assemble_grouping_two_chains(guard):
    mod = guard.premise("module loaded", _load)
    ia, aa, ma, ga = _sources_for_complete(UUID_A)
    ib, ab, mb, gb = _sources_for_complete(UUID_B)
    chains = guard.exercise("assemble", lambda: _assemble(mod, ia + ib, aa + ab, ma + mb, ga + gb))
    by_cid = {c["correlation_id"]: c for c in chains}
    guard.outcome("two chains", len(chains) == 2)
    guard.outcome("A mint is A", by_cid[UUID_A]["legs"]["mint"]["correlation_id"] == UUID_A)
    guard.outcome("B gateway is B", by_cid[UUID_B]["legs"]["gateway"]["correlation_id"] == UUID_B)


# UT: UT-306
# Test Description: Out-of-order capture still yields legs in canonical (not wall-clock) order.
# Precondition: Module loaded; sources fed in scrambled order.
# Expected Output: The legs dict preserves the canonical leg order.
# Covers DD: DD-915
def test_assemble_out_of_order_canonical(guard):
    mod = guard.premise("module loaded", _load)
    intents, adapters, mints, gateways = _sources_for_complete()
    chains = guard.exercise("assemble scrambled", lambda: mod.assemble_chains(intents=intents, adapters=list(reversed(adapters)), mints=mints, gateways=gateways))
    guard.outcome("canonical leg order", list(chains[0]["legs"].keys()) == mod.CHAIN_LEG_ORDER)


# UT: UT-307
# Test Description: Two records for the same (correlation_id, leg) resolve to a single first-wins leg.
# Precondition: Module loaded; two adapter_request records for the same correlation id with different sequences.
# Expected Output: The first-captured (lowest sequence) record is the surfaced leg.
# Covers DD: DD-915
def test_assemble_duplicate_leg_first_wins(guard):
    mod = guard.premise("module loaded", _load)
    intents, adapters, mints, gateways = _sources_for_complete()
    dup = mod_request(UUID_A, seq=5, ts="2026-06-19T10:09:00Z")
    adapters2 = [dup] + adapters  # later sequence listed first to prove sequence wins, not list order
    chains = guard.exercise("assemble dup", lambda: _assemble(mod, intents, adapters2, mints, gateways))
    guard.outcome("first-wins by sequence", chains[0]["legs"]["adapter_request"]["sequence"] == 1)


# UT: UT-308
# Test Description: A correlation id present only in the rollout (no in-boundary source) is not surfaced.
# Precondition: Module loaded; an intent triple references a cid absent from adapter/gateway/mint sources.
# Expected Output: No chain is surfaced for that correlation id.
# Covers DD: DD-915
def test_assemble_rollout_only_not_surfaced(guard):
    mod = guard.premise("module loaded", _load)
    intents = [{"correlation_id": UUID_C, "user_message": "x", "tool_name": "create_story", "arguments": {"project_key": "IAM"}}]
    chains = guard.exercise("assemble", lambda: _assemble(mod, intents, [], [], []))
    guard.outcome("not surfaced", chains == [])


# UT: UT-309
# Test Description: Anchor rule surfaces adapter/gateway ids but not a capiss-only (non-M5) mint id.
# Precondition: Module loaded; cid A has adapter+gateway+mint; cid B has only a capiss mint.
# Expected Output: A is surfaced; B (capiss-only) is not.
# Covers DD: DD-915
def test_assemble_anchor_capiss_only_not_surfaced(guard):
    mod = guard.premise("module loaded", _load)
    ia, aa, ma, ga = _sources_for_complete(UUID_A)
    capiss_only = {"event_type": "capiss_mint_decision", "sequence": 9, "correlation_id": UUID_B, "result": "allow", "reason_code": "ok", "timestamp_utc": "2026-06-19T09:00:00Z"}
    chains = guard.exercise("assemble", lambda: _assemble(mod, ia, aa, ma + [capiss_only], ga))
    cids = {c["correlation_id"] for c in chains}
    guard.outcome("A surfaced", UUID_A in cids)
    guard.outcome("capiss-only B not surfaced", UUID_B not in cids)


# UT: UT-310
# Test Description: Multiple chains are listed in request-start ascending order by earliest in-boundary leg.
# Precondition: Module loaded; three chains captured out of order with distinct earliest in-boundary timestamps.
# Expected Output: Chains are listed earliest-first regardless of capture order.
# Covers DD: DD-915
def test_assemble_chain_listing_request_start_order(guard):
    mod = guard.premise("module loaded", _load)

    def adapter(cid, ts):
        return {"event_type": "adapter_request", "sequence": 1, "correlation_id": cid, "tool_name": "create_story", "timestamp": ts}

    adapters = [adapter(UUID_C, "2026-06-19T10:00:30Z"), adapter(UUID_A, "2026-06-19T10:00:10Z"), adapter(UUID_B, "2026-06-19T10:00:20Z")]
    chains = guard.exercise("assemble", lambda: _assemble(mod, [], adapters, [], []))
    order = [c["correlation_id"] for c in chains]
    guard.outcome("ascending request-start", order == [UUID_A, UUID_B, UUID_C])


# ===========================================================================
# DD-924  derive_gateway_upstream  (exhaustive condition coverage + BVA)
# ===========================================================================
def _gw_event(decision, upstream_called, status=None, reason="ok"):
    ev = {"event_type": "jiramcp_gateway_decision", "sequence": 1, "correlation_id": UUID_A, "decision": decision, "reason_code": reason, "timestamp": "2026-06-19T10:00:03Z"}
    if upstream_called:
        ev["upstream_called"] = True
        ev["upstream_operation"] = "story_create"
        if status is not None:
            ev["upstream_status"] = status
    return ev


# UT: UT-335
# Test Description: derive_gateway_upstream with decision=allow, upstream called, 2xx status → gateway ALLOW + upstream OK.
# Precondition: Module loaded; a successful gateway decision event is presented.
# Expected Output: gateway leg status allow; upstream leg present with ok status.
# Covers DD: DD-924
def test_derive_allow_called_2xx(guard):
    mod = guard.premise("module loaded", _load)
    gw, up = guard.exercise("derive", lambda: mod.derive_gateway_upstream(_gw_event("allow", True, 201)))
    guard.outcome("gateway allow", gw["leg_status"] == "allow")
    guard.outcome("upstream ok with status", up is not None and up["leg_status"] == "ok" and up["upstream_status"] == 201)


# UT: UT-336
# Test Description: derive_gateway_upstream with decision=deny but upstream called and 4xx → gateway ALLOW (enforcement passed) + upstream FAIL.
# Precondition: Module loaded; a gateway event where enforcement passed but the upstream rejected (the "who denied" case).
# Expected Output: gateway leg status allow; upstream leg fail with the upstream status — the denial is attributed to the upstream, not the gateway.
# Covers DD: DD-924
def test_derive_deny_called_4xx_is_upstream_failure(guard):
    mod = guard.premise("module loaded", _load)
    gw, up = guard.exercise("derive", lambda: mod.derive_gateway_upstream(_gw_event("deny", True, 401, reason="upstream_error")))
    guard.outcome("gateway shows allow not deny", gw["leg_status"] == "allow")
    guard.outcome("upstream shows the failure", up is not None and up["leg_status"] == "fail" and up["upstream_status"] == 401)


# UT: UT-337
# Test Description: derive_gateway_upstream with decision=deny and upstream not called → gateway DENY with reason + no upstream leg.
# Precondition: Module loaded; a gateway enforcement denial (upstream never reached).
# Expected Output: gateway leg status deny carrying the enforcement reason; upstream leg None (not reached).
# Covers DD: DD-924
def test_derive_deny_not_called_is_gateway_denial(guard):
    mod = guard.premise("module loaded", _load)
    gw, up = guard.exercise("derive", lambda: mod.derive_gateway_upstream(_gw_event("deny", False, reason="budget_exhausted")))
    guard.outcome("gateway deny with reason", gw["leg_status"] == "deny" and gw["reason_code"] == "budget_exhausted")
    guard.outcome("upstream not reached", up is None)


# UT: UT-338
# Test Description: derive_gateway_upstream with decision=allow and upstream not called → gateway ALLOW + no upstream leg (defensive).
# Precondition: Module loaded; a gateway allow event that records no upstream call.
# Expected Output: gateway leg allow; upstream leg None.
# Covers DD: DD-924
def test_derive_allow_not_called(guard):
    mod = guard.premise("module loaded", _load)
    gw, up = guard.exercise("derive", lambda: mod.derive_gateway_upstream(_gw_event("allow", False)))
    guard.outcome("gateway allow", gw["leg_status"] == "allow")
    guard.outcome("upstream absent", up is None)


# UT: UT-339
# Test Description: BVA on the 2xx upstream-status band — 299 is ok, 300 is fail, 200 is ok.
# Precondition: Module loaded; upstream-called gateway events at the 2xx band boundaries.
# Expected Output: 200 and 299 → ok; 300 → fail.
# Covers DD: DD-924
def test_derive_upstream_status_2xx_boundary(guard):
    mod = guard.premise("module loaded", _load)
    ok_low = guard.exercise("status 200", lambda: mod.derive_gateway_upstream(_gw_event("allow", True, 200))[1])
    ok_high = guard.exercise("status 299", lambda: mod.derive_gateway_upstream(_gw_event("allow", True, 299))[1])
    fail = guard.exercise("status 300", lambda: mod.derive_gateway_upstream(_gw_event("deny", True, 300, reason="upstream_error"))[1])
    guard.outcome("200 ok", ok_low["leg_status"] == "ok")
    guard.outcome("299 ok (top of band)", ok_high["leg_status"] == "ok")
    guard.outcome("300 fail (above band)", fail["leg_status"] == "fail")


# UT: UT-340
# Test Description: derive_gateway_upstream preserves the correlation id on both derived legs for cross-source join.
# Precondition: Module loaded; an upstream-called gateway event with a correlation id.
# Expected Output: Both gateway and upstream legs carry the same correlation id.
# Covers DD: DD-924
def test_derive_preserves_correlation_id(guard):
    mod = guard.premise("module loaded", _load)
    gw, up = guard.exercise("derive", lambda: mod.derive_gateway_upstream(_gw_event("allow", True, 201)))
    guard.outcome("gateway leg keeps cid", gw["correlation_id"] == UUID_A)
    guard.outcome("upstream leg keeps cid", up["correlation_id"] == UUID_A)


# ===========================================================================
# DD-916  render_chain / render_chain_json
# ===========================================================================
def _capiss_mint_record(cid=UUID_A):
    return {
        "event_type": "capiss_mint_decision", "sequence": 1, "result": "allow", "reason_code": "ok",
        "subject_spiffe_id": "spiffe://varambu.org/codex-jira-mcp-adapter", "act": "create_story",
        "res": "jira-mcp:/project:IAM", "aud": "jira-mcp-gateway", "decision_type": "root_mint",
        "token_id": "tok-1", "root_token_id": "root-1", "delegation_depth": 0,
        "issued_at_local": "2026-06-19 12:00:02 Europe/Berlin", "expires_at_local": "2026-06-19 12:01:02 Europe/Berlin",
        "timestamp_local": "2026-06-19 12:00:02 Europe/Berlin", "ttl_seconds": 60,
        "issued_at_utc": "2026-06-19T10:00:02Z", "expires_at_utc": "2026-06-19T10:01:02Z",
        "timestamp_utc": "2026-06-19T10:00:02Z", "correlation_id": cid,
        "policy_id": "capiss.allow.v3", "policy_hash": "sha256:capiss-policy-v3",
    }


def _full_chain(mod):
    intents = [{
        "correlation_id": UUID_A, "user_message": "create a story for IAM",
        "tool_name": "create_story", "arguments": {"project_key": "IAM"},
        "intent_timestamp": "2026-06-19T10:00:00Z", "intent_sequence": 1,
        "action_timestamp": "2026-06-19T10:00:01Z", "action_sequence": 2,
    }]
    adapters = [mod_request(UUID_A), {"event_type": "adapter_decision", "sequence": 2, "correlation_id": UUID_A, "ok": True, "key": "IAM-5", "timestamp": "2026-06-19T10:00:04Z"}]
    mints = [_capiss_mint_record()]
    gateways = [{"event_type": "jiramcp_gateway_decision", "sequence": 1, "correlation_id": UUID_A, "decision": "allow", "reason_code": "ok", "upstream_called": True, "upstream_operation": "story_create", "upstream_status": 201, "aud": "jira-mcp-gateway", "act": "create_story", "res": "jira-mcp:/project:IAM", "project_key": "IAM", "token_project": "IAM", "budget_remaining": 9, "timestamp": "2026-06-19T10:00:03Z"}]
    return mod.assemble_chains(intents=intents, adapters=adapters, mints=mints, gateways=gateways)[0]


# UT: UT-311
# Test Description: The mint leg presents the same capiss fields (not necessarily byte-identical to render_record).
# Precondition: Module loaded; a complete chain with an allow mint is rendered.
# Expected Output: The mint leg shows the subject identity, full token id, grant action/resource, ttl, and policy id.
# Covers DD: DD-916
def test_render_chain_mint_leg_presents_capiss_fields(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    rendered = guard.exercise("render_chain", lambda: mod.render_chain(chain))
    guard.outcome("mint label present", "MINT" in rendered)
    guard.outcome("subject identity present", "spiffe://varambu.org/codex-jira-mcp-adapter" in rendered)
    guard.outcome("token id present in full", "tok-1" in rendered)
    guard.outcome("grant action and resource present", "create_story" in rendered and "jira-mcp:/project:IAM" in rendered)
    guard.outcome("ttl present", "60s" in rendered)
    guard.outcome("policy id present", "capiss.allow.v3" in rendered)


# UT: UT-341
# Test Description: The gateway allow leg renders verified facts from the event (aud/act and the request-vs-token project match), not a hardcoded checklist.
# Precondition: Module loaded; a complete chain with an allow gateway leg is rendered.
# Expected Output: The gateway leg shows aud, act, and the request=token project comparison drawn from the event; no static "token · aud · act · project · budget ok" literal.
# Covers DD: DD-916
def test_render_chain_gateway_leg_shows_verified_project(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    rendered = guard.exercise("render_chain", lambda: mod.render_chain(chain))
    guard.outcome("verified aud/act from event", "jira-mcp-gateway" in rendered and "create_story" in rendered)
    guard.outcome("project request=token match shown", "request IAM = token IAM" in rendered)
    guard.outcome("no hardcoded checklist literal", "token · aud · act · project · budget ok" not in rendered)


# UT: UT-342
# Test Description: A failed upstream leg passes the relayed Jira message straight through with no constructed status interpretation; a success and a detail-less failure stay the single Call row.
# Precondition: Module loaded; the upstream detail builder is invoked for a failure with a relayed detail, a failure without one, and a 2xx success.
# Expected Output: The failure-with-detail adds only a Jira row carrying the message verbatim and no Error/Action rows; the detail-less failure and the 2xx success are the Call row only.
# Covers DD: DD-916
def test_render_upstream_passes_relayed_message_without_interpretation(guard):
    mod = guard.premise("module loaded", _load)
    fail = guard.exercise("failure with detail", lambda: mod._detail_upstream({"leg_status": "fail", "upstream_operation": "read_project_summary", "upstream_status": 404, "upstream_error_detail": "Issue does not exist or you do not have permission to see it."}, "live"))
    labels = [label for label, _ in fail]
    guard.outcome("no constructed Error/Action rows", "Error" not in labels and "Action" not in labels)
    guard.outcome("relayed message passed through verbatim", dict(fail).get("Jira") == "Issue does not exist or you do not have permission to see it.")
    guard.outcome("rows are exactly Call then Jira", labels == ["Call", "Jira"])
    no_detail = guard.exercise("failure without detail", lambda: [label for label, _ in mod._detail_upstream({"leg_status": "fail", "upstream_operation": "story_create", "upstream_status": 502}, "live")])
    guard.outcome("detail-less failure is Call only", no_detail == ["Call"])
    ok_201 = guard.exercise("success", lambda: [label for label, _ in mod._detail_upstream({"leg_status": "ok", "upstream_operation": "story_create", "upstream_status": 201}, "mock")])
    guard.outcome("success stays concise", ok_201 == ["Call"])


# UT: UT-344
# Test Description: A failed upstream leg relays the gateway-attested Jira error detail; the normalizer allowlists it; a forbidden value is dropped at read time.
# Precondition: Module loaded; a gateway deny event with upstream_called and an upstream_error_detail is normalized, derived, and rendered; a second carries a Bearer value.
# Expected Output: The normalizer keeps upstream_error_detail; the upstream leg renders a Jira row with the message; a Bearer-bearing detail is scrubbed (absent).
# Covers DD: DD-910, DD-924, DD-916
def test_upstream_error_detail_relayed_and_scrubbed(guard):
    mod = guard.premise("module loaded", _load)
    detail = "Issue does not exist or you do not have permission to see it."
    raw = {"event_type": "jiramcp_gateway_decision", "decision": "deny", "reason_code": "upstream_error", "correlation_id": UUID_A, "act": "create_story", "res": "jira-mcp:/project:IAM", "upstream_called": True, "upstream_operation": "story_create", "upstream_status": 404, "upstream_error_detail": detail, "timestamp": "2026-06-19T10:00:03Z"}
    norm = guard.exercise("normalize gateway", lambda: mod.normalize_gateway_event(raw, 1))
    guard.outcome("normalizer keeps upstream_error_detail", norm.get("upstream_error_detail") == detail)
    up = guard.exercise("derive upstream leg", lambda: mod.derive_gateway_upstream(norm)[1])
    rows = guard.exercise("render upstream detail", lambda: dict(mod._detail_upstream(up, "live")))
    guard.outcome("Jira row relays the message", rows.get("Jira") == detail)
    forbidden = dict(raw, upstream_error_detail="token Bearer abc.def leaked", sequence=2)
    norm2 = guard.exercise("normalize forbidden detail", lambda: mod.normalize_gateway_event(forbidden, 2))
    guard.outcome("forbidden detail scrubbed at read time", "upstream_error_detail" not in norm2)


# UT: UT-312
# Test Description: The human chain render shows full fields and the redesigned leg labels.
# Precondition: Module loaded; a complete chain is rendered.
# Expected Output: The render carries the full correlation id, verbatim prompt, upstream status, and the ADAPTER / UPSTREAM / RETURN TO CODEX labels.
# Covers DD: DD-916
def test_render_chain_full_fields(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    rendered = guard.exercise("render", lambda: mod.render_chain(chain))
    guard.outcome("full correlation present", UUID_A in rendered)
    guard.outcome("verbatim prompt present", "create a story for IAM" in rendered)
    guard.outcome("upstream status present", "201" in rendered)
    guard.outcome("adapter label present", "ADAPTER" in rendered)
    guard.outcome("separate gateway and upstream labels", "GATEWAY" in rendered and "UPSTREAM" in rendered)
    guard.outcome("return-to-codex label present", "RETURN TO CODEX" in rendered)


# UT: UT-313
# Test Description: The human view omits the advisory elapsed offset (kept only in --json) and shows aligned status tokens.
# Precondition: Module loaded; a complete chain is rendered.
# Expected Output: No "advisory" text in the human render; gateway shows ALLOW and upstream shows its status with OK.
# Covers DD: DD-916
def test_render_chain_human_omits_advisory(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    rendered = guard.exercise("render", lambda: mod.render_chain(chain))
    guard.outcome("no advisory text in human view", "advisory" not in rendered.lower())
    guard.outcome("gateway allow status shown", "ALLOW" in rendered)
    guard.outcome("upstream ok status shown", "201 OK" in rendered)


# UT: UT-314
# Test Description: Local time renders in the configured TZ and falls back to UTC on an invalid TZ without crashing.
# Precondition: Module loaded; a chain is rendered with a valid and then an invalid VARAMBU_TZ.
# Expected Output: Valid TZ renders local time; invalid TZ does not crash and still renders.
# Covers DD: DD-916
def test_render_chain_local_tz_and_invalid_fallback(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    good = guard.exercise("render valid tz", lambda: mod.render_chain(chain, tz="Europe/Berlin"))
    bad = guard.exercise("render invalid tz", lambda: mod.render_chain(chain, tz="Not/AZone"))
    guard.outcome("valid tz renders", UUID_A in good)
    guard.outcome("invalid tz does not crash", isinstance(bad, str) and UUID_A in bad)


# UT: UT-315
# Test Description: A partial chain renders explicit not-yet-available lines for missing legs while present legs render fully.
# Precondition: Module loaded; a chain missing the intent leg is rendered.
# Expected Output: The intent leg shows not yet available; the mint leg still renders.
# Covers DD: DD-916
def test_render_chain_partial_missing_legs(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    chain["legs"]["intent"] = None
    rendered = guard.exercise("render", lambda: mod.render_chain(chain))
    guard.outcome("not yet available shown", "not yet available" in rendered.lower())
    guard.outcome("mint leg still rendered", "MINT" in rendered and "tok-1" in rendered)


# UT: UT-316
# Test Description: In live mode the upstream leg is labeled gateway-attested with no fabricated independent voice.
# Precondition: Module loaded; a chain is rendered with mode=live.
# Expected Output: The upstream leg carries a gateway-attested (live) label and no independent upstream voice.
# Covers DD: DD-916
def test_render_chain_live_mode_gateway_attested(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    rendered = guard.exercise("render live", lambda: mod.render_chain(chain, mode="live"))
    guard.outcome("gateway-attested live label on upstream leg", "gateway-attested, live" in rendered.lower())


# UT: UT-317
# Test Description: render_chain_json emits the seven legs in canonical order including upstream, each present leg carrying UTC, local time, sequence, and advisory offset.
# Precondition: Module loaded; a complete chain is rendered to JSON.
# Expected Output: Valid JSON with a legs array in 7-leg canonical order; the upstream leg is present with its status; present legs carry timestamp_utc/timestamp_local/sequence/elapsed_advisory.
# Covers DD: DD-922
def test_render_chain_json_structure(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    payload = guard.exercise("render json", lambda: mod.render_chain_json(chain, tz="Europe/Berlin"))
    serialized = guard.exercise("serialize", lambda: json.dumps(payload))
    leg_names = [leg["leg"] for leg in payload["legs"]]
    guard.outcome("canonical leg order with upstream", leg_names == mod.CHAIN_LEG_ORDER and "upstream" in leg_names)
    guard.outcome("valid json", isinstance(json.loads(serialized), dict))
    upstream = next(leg for leg in payload["legs"] if leg["leg"] == "upstream")
    guard.outcome("upstream leg present with status", upstream["present"] and upstream["fields"]["upstream_status"] == 201)
    present = [leg for leg in payload["legs"] if leg.get("present")]
    guard.outcome("present legs carry utc, sequence, advisory", all("timestamp_utc" in leg and "sequence" in leg and "elapsed_advisory" in leg for leg in present))
    present = [leg for leg in payload["legs"] if leg.get("present")]
    guard.outcome("present legs carry utc and sequence", all("timestamp_utc" in leg and "sequence" in leg for leg in present))


# UT: UT-318
# Test Description: A forbidden value injected into a leg is not emitted by either renderer.
# Precondition: Module loaded; a chain leg carries a Bearer-bearing field.
# Expected Output: The secret marker appears in neither the human nor JSON render.
# Covers DD: DD-916
def test_render_chain_scrubs_forbidden_value(guard):
    mod = guard.premise("module loaded", _load)
    chain = guard.exercise("build chain", lambda: _full_chain(mod))
    chain["legs"]["gateway"]["subject_spiffe_id"] = "Bearer sneaky-secret"
    human = guard.exercise("render human", lambda: mod.render_chain(chain))
    payload = guard.exercise("render json", lambda: json.dumps(mod.render_chain_json(chain)))
    guard.outcome("human scrubbed", "sneaky-secret" not in human)
    guard.outcome("json scrubbed", "sneaky-secret" not in payload)


# ===========================================================================
# DD-917  trace CLI
# ===========================================================================
def _write_session(session_dir: Path, cid=UUID_A):
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "capiss_audit.jsonl").write_text(json.dumps(_capiss_mint_record(cid)) + "\n", encoding="utf-8")
    (session_dir / "gateway_audit.jsonl").write_text(json.dumps({"event_type": "jiramcp_gateway_decision", "sequence": 1, "correlation_id": cid, "decision": "allow", "reason_code": "ok", "timestamp": "2026-06-19T10:00:03Z"}) + "\n", encoding="utf-8")
    (session_dir / "adapter_audit.jsonl").write_text(
        json.dumps({"event_type": "adapter_request", "sequence": 1, "correlation_id": cid, "tool_name": "create_story", "timestamp": "2026-06-19T10:00:01Z"}) + "\n"
        + json.dumps({"event_type": "adapter_decision", "sequence": 2, "correlation_id": cid, "ok": True, "timestamp": "2026-06-19T10:00:04Z"}) + "\n",
        encoding="utf-8",
    )
    codex_sessions = session_dir / "codex-home" / "sessions" / "2026" / "06" / "19"
    codex_sessions.mkdir(parents=True, exist_ok=True)
    rollout = [
        _user_message("create a story for IAM"),
        _function_call("create_story", "call-X", {"project_key": "IAM"}),
        _function_call_output("call-X", cid),
    ]
    (codex_sessions / "rollout-1.jsonl").write_text("\n".join(json.dumps(r) for r in rollout) + "\n", encoding="utf-8")


def _trace_args(session, **over):
    base = dict(session=str(session), all=False, json=False, cid=None, tz="Europe/Berlin", mode="mock")
    base.update(over)
    return argparse.Namespace(**base)


# UT: UT-319
# Test Description: trace renders the current session's chains by default.
# Precondition: Module loaded; a session directory carries all per-source files and a rollout.
# Expected Output: A non-error return and the correlation id printed.
# Covers DD: DD-917
def test_trace_cli_default_current_session(tmp_path, capsys, guard):
    mod = guard.premise("module loaded", _load)
    session = tmp_path / "20260619-1"
    guard.exercise("write session", lambda: _write_session(session))
    rc = guard.exercise("trace", lambda: mod.trace(_trace_args(session)))
    out = capsys.readouterr().out
    guard.outcome("returns zero", rc == 0)
    guard.outcome("correlation rendered", UUID_A in out)


# UT: UT-320
# Test Description: trace --cid selects a single matching chain and reports a friendly message for a non-matching id.
# Precondition: Module loaded; a session with one chain is queried by matching and non-matching cid.
# Expected Output: Matching cid prints the chain; non-matching prints a friendly empty message.
# Covers DD: DD-917
def test_trace_cli_cid_select(tmp_path, capsys, guard):
    mod = guard.premise("module loaded", _load)
    session = tmp_path / "20260619-1"
    guard.exercise("write session", lambda: _write_session(session))
    guard.exercise("trace match", lambda: mod.trace(_trace_args(session, cid=UUID_A)))
    match_out = capsys.readouterr().out
    guard.exercise("trace nomatch", lambda: mod.trace(_trace_args(session, cid=UUID_B)))
    nomatch_out = capsys.readouterr().out
    guard.outcome("match prints chain", UUID_A in match_out)
    guard.outcome("nomatch friendly", UUID_A not in nomatch_out and ("no" in nomatch_out.lower() or "not found" in nomatch_out.lower()))


# UT: UT-321
# Test Description: trace --all renders chains across two sessions in session order without dedupe.
# Precondition: Module loaded; two session directories each carry a distinct chain.
# Expected Output: Both correlation ids appear in the output.
# Covers DD: DD-917
def test_trace_cli_all_sessions(tmp_path, capsys, guard):
    mod = guard.premise("module loaded", _load)
    root = tmp_path / "varambu-demo"
    s1, s2 = root / "20260619-1", root / "20260619-2"
    guard.exercise("write s1", lambda: _write_session(s1, UUID_A))
    guard.exercise("write s2", lambda: _write_session(s2, UUID_B))
    rc = guard.exercise("trace all", lambda: mod.trace(_trace_args(s2, all=True, sessions_root=str(root))))
    out = capsys.readouterr().out
    guard.outcome("returns zero", rc == 0)
    guard.outcome("both sessions present", UUID_A in out and UUID_B in out)


# UT: UT-322
# Test Description: trace --json emits machine-readable assembled chains.
# Precondition: Module loaded; a session with one chain is queried with --json.
# Expected Output: The printed output parses as JSON carrying the correlation id.
# Covers DD: DD-917
def test_trace_cli_json(tmp_path, capsys, guard):
    mod = guard.premise("module loaded", _load)
    session = tmp_path / "20260619-1"
    guard.exercise("write session", lambda: _write_session(session))
    rc = guard.exercise("trace json", lambda: mod.trace(_trace_args(session, json=True)))
    out = capsys.readouterr().out
    parsed = guard.exercise("parse json", lambda: json.loads(out))
    guard.outcome("returns zero", rc == 0)
    guard.outcome("json carries cid", json.dumps(parsed).count(UUID_A) >= 1)


# UT: UT-323
# Test Description: trace prints a friendly non-crashing message when no current session exists.
# Precondition: Module loaded; the session path does not exist.
# Expected Output: A non-crash return and a guidance message mentioning varambu start.
# Covers DD: DD-917
def test_trace_cli_no_session(tmp_path, capsys, guard):
    mod = guard.premise("module loaded", _load)
    rc = guard.exercise("trace missing", lambda: mod.trace(_trace_args(tmp_path / "missing")))
    out = capsys.readouterr().out
    guard.outcome("non-crash return", rc == 0)
    guard.outcome("guidance message", "varambu start" in out.lower() or "no" in out.lower())


# UT: UT-324
# Test Description: trace persists the scrubbed intent triple to the session trace.jsonl as durable evidence.
# Precondition: Module loaded; trace runs on a session whose rollout carries the verbatim prompt.
# Expected Output: trace.jsonl is written with the scrubbed minimal triple and no whole-rollout content.
# Covers DD: DD-917
def test_trace_cli_persists_scrubbed_trace_jsonl(tmp_path, guard):
    mod = guard.premise("module loaded", _load)
    session = tmp_path / "20260619-1"
    guard.exercise("write session", lambda: _write_session(session))
    guard.exercise("trace", lambda: mod.trace(_trace_args(session)))
    trace_path = session / "trace.jsonl"
    content = guard.exercise("read trace.jsonl", lambda: trace_path.read_text(encoding="utf-8"))
    records = guard.exercise("parse", lambda: [json.loads(line) for line in content.splitlines() if line.strip()])
    guard.outcome("trace.jsonl written", trace_path.exists() and len(records) == 1)
    guard.outcome("verbatim prompt persisted", records[0]["user_message"] == "create a story for IAM")
    guard.outcome("minimal keys only", set(records[0]) <= {"correlation_id", "user_message", "tool_name", "arguments", "result"})
