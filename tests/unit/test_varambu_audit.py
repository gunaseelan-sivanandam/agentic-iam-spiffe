from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from tests.unit.shared.loaders import REPO_ROOT, load_module_from_path


VARAMBU_AUDIT_PATH = Path(REPO_ROOT, "scripts", "varambu_audit.py")


def _load_varambu_audit():
    return load_module_from_path(VARAMBU_AUDIT_PATH, "varambu_audit_test")


# UT: UT-226
# Test Description: Verifies Varambu audit normalizer keeps only approved schema fields and drops forbidden field names and secret values.
# Precondition: The audit helper module is loaded and a raw capiss mint-decision event contains approved, unknown, forbidden-name, and secret fields.
# Expected Output: The SUT returns a sequenced normalized event with approved fields only and no secret-bearing content anywhere in the output.
# Covers DD: DD-901
def test_varambu_audit_normalize_allowlist_drops_forbidden_fields(guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    raw = {
        "event_type": "capiss_mint_decision",
        "result": "allow",
        "reason_code": "ok",
        "subject_spiffe_id": "spiffe://example.org/codex-jira-mcp-adapter",
        "act": "create_story",
        "res": "jira-mcp:/project:IAM",
        "resource_attrs": {"kind": "jira_project", "project_key": "IAM"},
        "token_id": "token-1",
        "token": "secret-token-value",
        "Authorization": "Bearer secret-token-value",
        "surprise": "ignored",
    }
    normalized = guard.exercise("normalize raw event", lambda: mod.normalize_event(raw, 7))
    serialized = guard.exercise("serialize normalized event", lambda: json.dumps(normalized, sort_keys=True))
    guard.outcome("sequence added", normalized["sequence"] == 7)
    guard.outcome("approved token id retained", normalized["token_id"] == "token-1")
    guard.outcome("resource attrs retained", normalized["resource_attrs"] == {"kind": "jira_project", "project_key": "IAM"})
    guard.outcome("unknown field dropped", "surprise" not in normalized)
    guard.outcome("forbidden name fields dropped", "token" not in normalized and "Authorization" not in normalized)
    guard.outcome("secret value absent from serialized output", "secret-token-value" not in serialized)


# UT: UT-243
# Test Description: Verifies Varambu audit normalizer returns None for events that are not capiss_mint_decision.
# Precondition: The audit helper module is loaded and raw events with a different event_type and with no event_type are presented.
# Expected Output: The SUT returns None for both non-matching inputs without emitting any record.
# Covers DD: DD-901
def test_varambu_audit_normalize_ignores_non_mint_decision_events(guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    other = guard.exercise(
        "normalize unrelated event",
        lambda: mod.normalize_event({"event_type": "jiratool_enforcement_decision", "result": "allow"}, 1),
    )
    no_type = guard.exercise(
        "normalize event with no type",
        lambda: mod.normalize_event({"result": "allow"}, 2),
    )
    guard.outcome("unrelated event returns none", other is None)
    guard.outcome("missing event_type returns none", no_type is None)


# UT: UT-244
# Test Description: Verifies Varambu audit normalizer drops an approved-name field whose value contains a forbidden bearer text marker.
# Precondition: The audit helper module is loaded and a raw mint-decision event contains an approved-name field with a bearer secret value.
# Expected Output: The SUT returns a normalized event without the bearer-value field and without the bearer text in serialized output.
# Covers DD: DD-901
def test_varambu_audit_normalize_drops_approved_field_with_forbidden_value(guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    raw = {
        "event_type": "capiss_mint_decision",
        "result": "allow",
        "reason_code": "ok",
        "subject_spiffe_id": "Bearer leaked-secret",
        "act": "read",
        "res": "tool-b:/search",
    }
    normalized = guard.exercise("normalize event with bearer value in approved field", lambda: mod.normalize_event(raw, 1))
    serialized = guard.exercise("serialize normalized event", lambda: json.dumps(normalized, sort_keys=True))
    guard.outcome("bearer-value field dropped", "subject_spiffe_id" not in normalized)
    guard.outcome("bearer text absent from serialized output", "Bearer" not in serialized and "leaked-secret" not in serialized)


# UT: UT-227
# Test Description: Verifies Varambu human rendering uses stable demo field order with local time first for minted records.
# Precondition: The audit helper module is loaded and a normalized minted record contains token validity metadata.
# Expected Output: The SUT renders a readable block with local time in the header, subject before action, logged-at, UTC summary, and policy; resource_attrs scope is hidden by default.
# Covers DD: DD-902
def test_varambu_audit_render_minted_record_order(guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    record = {
        "sequence": 1,
        "result": "allow",
        "reason_code": "ok",
        "subject_spiffe_id": "spiffe://example.org/codex-jira-mcp-adapter",
        "act": "read_project_summary",
        "res": "jira-mcp:/project:IAM",
        "aud": "jira-mcp-gateway",
        "decision_type": "root_mint",
        "token_id": "token-1",
        "root_token_id": "root-1",
        "delegation_depth": 0,
        "issued_at_local": "2026-06-05 11:43:39 Europe/Berlin",
        "expires_at_local": "2026-06-05 11:44:39 Europe/Berlin",
        "timestamp_local": "2026-06-05 11:43:40 Europe/Berlin",
        "ttl_seconds": 60,
        "issued_at_utc": "2026-06-05T09:43:39Z",
        "expires_at_utc": "2026-06-05T09:44:39Z",
        "timestamp_utc": "2026-06-05T09:43:40Z",
        "correlation_id": "corr-1",
        "policy_id": "capiss.allow.v3",
        "policy_hash": "sha256:capiss-policy-v3",
        "resource_attrs": {"kind": "jira_project", "project_key": "IAM"},
    }
    rendered = guard.exercise("render minted record", lambda: mod.render_record(record))
    lines = guard.exercise("split rendered lines", lambda: rendered.splitlines())
    guard.outcome("header is first with local time", lines[0] == "#1 MINTED ok  2026-06-05 11:43:40 Europe/Berlin")
    guard.outcome("subject precedes action", lines.index("Subject:      spiffe://example.org/codex-jira-mcp-adapter") < lines.index("Action:       read_project_summary"))
    guard.outcome("logged at line present", "Logged At:    2026-06-05 11:43:40 Europe/Berlin" in lines)
    guard.outcome("utc summary line present", "UTC:          issued=2026-06-05T09:43:39Z expires=2026-06-05T09:44:39Z logged=2026-06-05T09:43:40Z" in lines)
    guard.outcome("policy line present", "Policy:       capiss.allow.v3 sha256:capiss-policy-v3" in lines)
    guard.outcome("resource_attrs scope hidden by default", not any("Scope:" in line for line in lines))


# UT: UT-228
# Test Description: Verifies Varambu human rendering shows denied requests with dash placeholders for token and validity fields.
# Precondition: The audit helper module is loaded and a normalized deny record has no issued token fields.
# Expected Output: The SUT renders denied status, reason, and dash placeholders for token ID, issued-at, and TTL fields.
# Covers DD: DD-902
def test_varambu_audit_render_denied_record_uses_dash_placeholders(guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    record = {
        "sequence": 2,
        "result": "deny",
        "reason_code": "policy",
        "subject_spiffe_id": "spiffe://example.org/codex-jira-mcp-adapter",
        "act": "create_story",
        "res": "jira-mcp:/project:NAS",
        "aud": "jira-mcp-gateway",
        "decision_type": "root_mint",
        "timestamp_local": "2026-06-05 11:46:38 Europe/Berlin",
        "timestamp_utc": "2026-06-05T09:46:38Z",
        "policy_id": "capiss.allow.v3",
        "policy_hash": "sha256:capiss-policy-v3",
    }
    rendered = guard.exercise("render denied record", lambda: mod.render_record(record))
    guard.outcome("denied header rendered", rendered.startswith("#2 DENIED policy  2026-06-05 11:46:38 Europe/Berlin"))
    guard.outcome("token id placeholder rendered", "Token ID:     -\n" in rendered)
    guard.outcome("issued placeholder rendered", "Issued At:    -\n" in rendered)
    guard.outcome("ttl placeholder rendered", "TTL:          -\n" in rendered)


# UT: UT-245
# Test Description: Verifies Varambu human renderer hides resource_attrs by default and exposes it only in verbose mode.
# Precondition: The audit helper module is loaded and a record contains resource_attrs.
# Expected Output: Default render omits the Scope line; verbose=True render includes a Scope line with sorted attribute key=value pairs.
# Covers DD: DD-902
def test_varambu_audit_render_resource_attrs_hidden_by_default_shown_in_verbose(guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    record = {
        "sequence": 3,
        "result": "allow",
        "reason_code": "ok",
        "res": "jira-mcp:/project:IAM",
        "timestamp_local": "2026-06-05 11:43:40 Europe/Berlin",
        "resource_attrs": {"kind": "jira_project", "project_key": "IAM"},
        "policy_id": "capiss.allow.v3",
        "policy_hash": "sha256:capiss-policy-v3",
    }
    default_render = guard.exercise("render without verbose", lambda: mod.render_record(record))
    verbose_render = guard.exercise("render with verbose=True", lambda: mod.render_record(record, verbose=True))
    guard.outcome("scope absent from default render", "Scope:" not in default_render)
    guard.outcome("scope present in verbose render", "Scope:        kind=jira_project project_key=IAM" in verbose_render)


# UT: UT-241
# Test Description: Verifies Varambu audit tailing appends normalized capiss mint-decision events only, copies tailer stderr, and uses the correct docker logs command.
# Precondition: The audit helper module is loaded and docker-log subprocess output contains invalid JSON, an unrelated event, and one valid mint-decision event.
# Expected Output: The SUT ignores non-events and invalid JSON, persists one sequenced JSONL and human record, copies stderr, and returns the subprocess exit code.
# Covers DD: DD-903
def test_varambu_audit_tail_writes_jsonl_and_human_files(monkeypatch, tmp_path, guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    jsonl_path = tmp_path / "capiss_audit.jsonl"
    human_path = tmp_path / "capiss_audit.log"
    err_path = tmp_path / "capiss_audit.err"

    class FakeProcess:
        stdout = [
            "not-json\n",
            json.dumps({"event_type": "other_event", "result": "allow"}) + "\n",
            json.dumps({
                "event_type": "capiss_mint_decision",
                "result": "allow",
                "reason_code": "ok",
                "subject_spiffe_id": "spiffe://example.org/codex-jira-mcp-adapter",
                "act": "read_project_summary",
                "res": "jira-mcp:/project:IAM",
                "timestamp_local": "2026-06-05 11:43:40 Europe/Berlin",
            }) + "\n",
        ]
        stderr = io.StringIO("docker stderr\n")

        def wait(self):
            return 0

    seen_cmds: list = []
    guard.exercise(
        "stub docker logs process",
        lambda: monkeypatch.setattr(
            mod.subprocess, "Popen", lambda cmd, **_kwargs: seen_cmds.append(cmd) or FakeProcess()
        ),
    )
    args = argparse.Namespace(
        jsonl=jsonl_path,
        human=human_path,
        err=err_path,
        since="2026-06-05T09:43:39Z",
        container="spiffe-capability-issuer",
        verbose=False,
    )
    rc = guard.exercise("tail audit log", lambda: mod.tail(args))
    records = guard.exercise(
        "read jsonl records",
        lambda: [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()],
    )
    human = guard.exercise("read human log", lambda: human_path.read_text(encoding="utf-8"))
    err = guard.exercise("read tailer stderr", lambda: err_path.read_text(encoding="utf-8"))
    guard.outcome(
        "docker command is correct",
        seen_cmds == [["docker", "logs", "--since", "2026-06-05T09:43:39Z", "--follow", "spiffe-capability-issuer"]],
    )
    guard.outcome("tail returned subprocess exit code", rc == 0)
    guard.outcome("invalid json and unrelated events ignored", len(records) == 1)
    guard.outcome("persisted record has sequence 1", records[0]["sequence"] == 1)
    guard.outcome("human record contains minted header", "#1 MINTED ok  2026-06-05 11:43:40 Europe/Berlin" in human)
    guard.outcome("tailer stderr copied to err file", err == "docker stderr\n")


# UT: UT-242
# Test Description: Verifies Varambu audit show reads persisted files and prints an operator message containing the file path when no events exist.
# Precondition: The audit helper module is loaded and show is called with an existing populated file and an existing empty file.
# Expected Output: The SUT prints file content for populated logs and a readable empty-session message containing the file path for empty files.
# Covers DD: DD-904
def test_varambu_audit_show_reads_persisted_files_and_empty_message(tmp_path, capsys, guard):
    mod = guard.premise("varambu audit module loaded", _load_varambu_audit)
    populated = tmp_path / "capiss_audit.log"
    empty = tmp_path / "empty.log"
    populated.write_text("line one\nline two\n", encoding="utf-8")
    empty.touch()
    first_rc = guard.exercise("show populated file", lambda: mod.show(argparse.Namespace(file=populated, follow=False)))
    first = capsys.readouterr().out
    second_rc = guard.exercise("show empty file", lambda: mod.show(argparse.Namespace(file=empty, follow=False)))
    second = capsys.readouterr().out
    guard.outcome("populated show returns 0", first_rc == 0)
    guard.outcome("populated content printed exactly", first == "line one\nline two\n")
    guard.outcome("empty show returns 0", second_rc == 0)
    guard.outcome("empty message contains session notice", "No capiss audit events recorded" in second)
    guard.outcome("empty message contains file path", str(empty) in second)
