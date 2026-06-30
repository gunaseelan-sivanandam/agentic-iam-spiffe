from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
import redis


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


# UT: UT-035
# Test Description: Verifies key material lifecycle.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-111, DD-112, DD-113
def test_key_material_lifecycle(capiss_module, tmp_path, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("set key file paths", lambda: _set_key_paths(capiss_module, tmp_path))

    private_key, created = guard.exercise("create root key", capiss_module.load_or_create_root_private_key)
    guard.outcome("key created", created is True)
    guard.outcome("key file exists", Path(capiss_module.CAPISS_KEY_FILE).exists())

    private_key_2, created_2 = guard.exercise("reload root key", capiss_module.load_or_create_root_private_key)
    guard.outcome("reload does not create new key", created_2 is False)
    guard.outcome("same private key bytes", private_key_2.to_bytes() == private_key.to_bytes())

    needs_update_before = guard.exercise("check public key update before write", lambda: capiss_module.public_key_needs_update(private_key_2))
    guard.exercise("write public key", lambda: capiss_module.write_public_key(private_key_2))
    needs_update_after = guard.exercise("check public key update after write", lambda: capiss_module.public_key_needs_update(private_key_2))
    guard.outcome("update needed before write", needs_update_before is True)
    guard.outcome("no update needed after write", needs_update_after is False)


def _set_key_paths(capiss_module, tmp_path):
    capiss_module.CAPISS_KEY_DIR = str(tmp_path / "keys")
    capiss_module.CAPISS_KEY_FILE = str(Path(capiss_module.CAPISS_KEY_DIR) / "root_key.b64")
    capiss_module.CAPISS_PUBLIC_KEY_FILE = str(Path(capiss_module.CAPISS_KEY_DIR) / "root_public_key.b64")


# UT: UT-036
# Test Description: Verifies parse fact helpers.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-116, DD-117
def test_parse_fact_helpers(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    parsed_string = guard.exercise("parse quoted arg", lambda: capiss_module.parse_fact_arg('"abc"'))
    parsed_number = guard.exercise("parse numeric arg", lambda: capiss_module.parse_fact_arg("123"))
    claims = guard.exercise(
        "parse block source",
        lambda: capiss_module.parse_block_source('sub("spiffe://varambu.org/agent-a");\nexp(10);\n'),
    )
    guard.outcome("quoted arg parsed", parsed_string == "abc")
    guard.outcome("numeric arg parsed", parsed_number == 123)
    guard.outcome("sub extracted", claims.get("sub") == "spiffe://varambu.org/agent-a")
    guard.outcome("subject_spiffe_id extracted", claims.get("subject_spiffe_id") == "spiffe://varambu.org/agent-a")
    guard.outcome("exp extracted", claims.get("exp") == 10)


# UT: UT-037
# Test Description: Verifies mint and parse token round trip.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-119, DD-123
def test_mint_and_parse_token_round_trip(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    token, _, _, root_token_id, token_id = guard.exercise(
        "mint root biscuit",
        lambda: capiss_module.mint_root_biscuit(
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    biscuit, claims, err = guard.exercise("parse minted token", lambda: capiss_module.parse_token(token))
    guard.outcome("no parse error", err is None)
    guard.outcome("biscuit returned", biscuit is not None)
    guard.outcome("claims returned", claims is not None)
    guard.outcome("root token id preserved", claims is not None and claims.get("root_token_id") == root_token_id)
    guard.outcome("token id preserved", claims is not None and claims.get("token_id") == token_id)
    guard.outcome("effective depth zero", claims is not None and claims.get("effective_depth") == 0)


# UT: UT-038
# Test Description: Verifies append resource token round trip.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-119, DD-124
def test_append_resource_token_round_trip(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    token, _, _, _, _ = guard.exercise(
        "mint root biscuit",
        lambda: capiss_module.mint_root_biscuit(
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    parent_biscuit, parent_claims, err = guard.exercise("parse root token", lambda: capiss_module.parse_token(token))
    guard.outcome("root parse has no error", err is None)
    guard.outcome("parent biscuit returned", parent_biscuit is not None)
    guard.outcome("parent claims returned", parent_claims is not None)

    delegated, _, _, child_token_id = guard.exercise(
        "append delegated token",
        lambda: capiss_module.append_resource_token(
            parent_biscuit,
            parent_claims,
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    _, delegated_claims, delegated_err = guard.exercise("parse delegated token", lambda: capiss_module.parse_token(delegated))
    guard.outcome("delegated parse has no error", delegated_err is None)
    guard.outcome("delegated claims returned", delegated_claims is not None)
    guard.outcome("delegated child token id matches", delegated_claims is not None and delegated_claims.get("token_id") == child_token_id)
    guard.outcome(
        "delegated parent token id matches",
        delegated_claims is not None and parent_claims is not None and delegated_claims.get("parent_token_id") == parent_claims.get("token_id"),
    )
    guard.outcome("delegated effective depth one", delegated_claims is not None and delegated_claims.get("effective_depth") == 1)


# UT: UT-039
# Test Description: Verifies that parse token rejects invalid value.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-119
def test_parse_token_rejects_invalid_value(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    biscuit, claims, err = guard.exercise("parse invalid token", lambda: capiss_module.parse_token("not-a-token"))
    guard.outcome("biscuit missing", biscuit is None)
    guard.outcome("claims missing", claims is None)
    guard.outcome("reason invalid_token", err == "invalid_token")


# UT: UT-040
# Test Description: Verifies mark capiss minted token store paths.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-121
def test_mark_capiss_minted_token_store_paths(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class GoodClient:
        def set(self, key, value, ex):
            self.last = (key, value, ex)

    guard.exercise("mock good redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: GoodClient()))
    ok, err = guard.exercise(
        "mark capiss minted token success path",
        lambda: capiss_module.mark_capiss_minted_token("token-1", int(time.time()) + 10),
    )
    guard.outcome("mark success", ok is True)
    guard.outcome("empty error on success", err == "")

    def broken():
        raise redis.RedisError("down")

    guard.exercise("mock broken redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", broken))
    ok, err = guard.exercise(
        "mark capiss minted token failure path",
        lambda: capiss_module.mark_capiss_minted_token("token-1", int(time.time()) + 10),
    )
    guard.outcome("mark fails", ok is False)
    guard.outcome("down error surfaced", err is not None and "down" in err)


# UT: UT-041
# Test Description: Verifies registry has resource store paths.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-122
def test_registry_has_resource_store_paths(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class GoodClient:
        def eval(self, *args):
            return 1

    guard.exercise("mock good registry client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: GoodClient()))
    store_ok, hit, err = guard.exercise(
        "registry hit path",
        lambda: capiss_module.registry_has_resource("root-1", "tool-b:/read-file:fileA"),
    )
    guard.outcome("store ok on hit", store_ok is True)
    guard.outcome("hit true", hit is True)
    guard.outcome("empty error", err == "")

    class BrokenClient:
        def eval(self, *args):
            raise redis.RedisError("down")

    guard.exercise("mock broken registry client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: BrokenClient()))
    store_ok, hit, err = guard.exercise(
        "registry store failure path",
        lambda: capiss_module.registry_has_resource("root-1", "tool-b:/read-file:fileA"),
    )
    guard.outcome("store not ok", store_ok is False)
    guard.outcome("hit false", hit is False)
    guard.outcome("down error surfaced", err is not None and "down" in err)


# UT: UT-128
# Test Description: Verifies that ensure_root_budget initializes only the root budget key and does not seed the discovery registry.
# Precondition: Module fixtures are loaded and the Redis pipeline dependency is replaced with a recording fake.
# Expected Output: The SUT writes exactly the budget key with a TTL and executes the pipeline without any registry writes.
# Covers DD: DD-120
@pytest.mark.invariant
def test_ensure_root_budget_writes_only_budget_key(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    seen: list[tuple] = []

    class RecordingPipeline:
        def set(self, key, value, ex):
            seen.append(("set", key, value, ex))
            return self

        def execute(self):
            seen.append(("execute",))
            return [True]

    class RecordingClient:
        def pipeline(self, transaction=True):
            seen.append(("pipeline", transaction))
            return RecordingPipeline()

    now = int(time.time())
    guard.exercise("mock recording redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: RecordingClient()))
    ok, err = guard.exercise("initialize root budget", lambda: capiss_module.ensure_root_budget("root-1", now + 15))
    guard.outcome("budget init succeeds", ok is True)
    guard.outcome("empty error on success", err == "")
    guard.outcome(
        "only budget write issued",
        len(seen) == 3
        and seen[0] == ("pipeline", True)
        and seen[1][0] == "set"
        and seen[1][1] == "m4:budget:root-1"
        and seen[1][2] == capiss_module.M4_DEFAULT_BUDGET
        and isinstance(seen[1][3], int)
        and seen[1][3] >= 1
        and seen[2] == ("execute",),
    )


# UT: UT-108
# Test Description: Verifies that the capability issuer health endpoint returns the exact ok payload.
# Precondition: Module fixtures are loaded and no additional setup is required.
# Expected Output: The SUT returns exactly `{\"status\": \"ok\"}`.
# Covers DD: DD-107
def test_health_returns_exact_ok_payload(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise("call health endpoint", capiss_module.health)
    guard.outcome("exact ok payload", payload == {"status": "ok"})


# UT: UT-109
# Test Description: Verifies that iso_utc_now returns the exact ISO timestamp from the module-local datetime source.
# Precondition: Module fixtures are loaded and the module-local datetime dependency is stubbed to a fixed UTC instant.
# Expected Output: The SUT returns the exact ISO-8601 string produced by the stubbed datetime object.
# Covers DD: DD-108
@pytest.mark.invariant
def test_iso_utc_now_returns_exact_stubbed_timestamp(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class FixedInstant:
        def isoformat(self):
            return "2026-04-03T10:11:12+00:00"

    class FixedDateTime:
        @staticmethod
        def now(tz):
            return FixedInstant()

    guard.exercise("stub datetime.now", lambda: monkeypatch.setattr(capiss_module, "datetime", FixedDateTime))
    out = guard.exercise("call iso_utc_now", capiss_module.iso_utc_now)
    guard.outcome("exact timestamp returned", out == "2026-04-03T10:11:12+00:00")


# UT: UT-110
# Test Description: Verifies that log_event emits an exact structured JSON audit record using the module-local timestamp helper.
# Precondition: Module fixtures are loaded, the timestamp helper is stubbed to a fixed value, and print output is captured.
# Expected Output: The SUT prints exactly one compact JSON object containing the event type, timestamp, and supplied fields.
# Covers DD: DD-109
@pytest.mark.invariant
def test_log_event_emits_exact_structured_json(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    printed: list[tuple[tuple[object, ...], dict[str, object]]] = []
    guard.exercise("stub audit timestamp", lambda: monkeypatch.setattr(capiss_module, "iso_utc_now", lambda: "2026-04-03T10:11:12+00:00"))
    guard.exercise(
        "capture print",
        lambda: monkeypatch.setattr(capiss_module, "print", lambda *args, **kwargs: printed.append((args, kwargs)), raising=False),
    )
    guard.exercise(
        "emit audit log",
        lambda: capiss_module.log_event("capiss_test", result="ok", reason_code="demo"),
    )
    guard.outcome("single print call", len(printed) == 1)
    guard.outcome(
        "exact print kwargs",
        printed[0][1] == {"flush": True},
    )
    guard.outcome(
        "exact structured payload",
        json.loads(printed[0][0][0])
        == {
            "event_type": "capiss_test",
            "timestamp": "2026-04-03T10:11:12+00:00",
            "result": "ok",
            "reason_code": "demo",
        },
    )


# UT: UT-223
# Test Description: Verifies enriched capiss mint-decision audit schema for successful issued tokens.
# Precondition: Module fixtures are loaded, audit time is deterministic, and a full allow decision is emitted through the mint audit helper.
# Expected Output: The SUT emits local and UTC validity fields, correlation, resource attributes, policy metadata, and no bearer token value.
# Covers DD: DD-222
@pytest.mark.invariant
def test_log_mint_decision_success_includes_validity_and_no_token_secret(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events: list[tuple[str, dict[str, object]]] = []
    guard.exercise("set demo timezone", lambda: setattr(capiss_module, "VARAMBU_TZ", "Europe/Berlin"))
    guard.exercise("freeze audit log time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_800_000_030))
    guard.exercise("capture audit event", lambda: monkeypatch.setattr(capiss_module, "log_event", lambda event_type, **fields: events.append((event_type, fields))))
    guard.exercise(
        "emit allow mint decision",
        lambda: capiss_module.log_mint_decision(
            result="allow",
            reason_code="ok",
            decision_type="root_mint",
            subject_spiffe_id="spiffe://varambu.org/codex-jira-mcp-adapter",
            aud="jira-mcp-gateway",
            act="create_story",
            res="jira-mcp:/project:IAM",
            root_token_id="root-1",
            token_id="token-1",
            delegation_depth=0,
            correlation_id="corr-1",
            issued_at=1_800_000_000,
            expires_at=1_800_000_060,
        ),
    )
    event_type, fields = guard.exercise("read captured event", lambda: events[0])
    serialized = guard.exercise("serialize event", lambda: json.dumps(fields, sort_keys=True))
    guard.outcome("event type preserved", event_type == "capiss_mint_decision")
    guard.outcome("correlation logged", fields["correlation_id"] == "corr-1")
    guard.outcome("issued utc logged", fields["issued_at_utc"] == "2027-01-15T08:00:00Z")
    guard.outcome("expires utc logged", fields["expires_at_utc"] == "2027-01-15T08:01:00Z")
    guard.outcome("logged utc differs from issued when later", fields["timestamp_utc"] == "2027-01-15T08:00:30Z")
    guard.outcome("local timezone label present", fields["timezone"] == "Europe/Berlin")
    guard.outcome("local issued time present", fields["issued_at_local"] == "2027-01-15 09:00:00 Europe/Berlin")
    guard.outcome("actual ttl computed", fields["ttl_seconds"] == 60)
    guard.outcome("resource attrs derived by capiss", fields["resource_attrs"] == {"kind": "jira_project", "project_key": "IAM"})
    guard.outcome("bearer token value not logged", "token" not in fields and "Bearer" not in serialized and "token-secret" not in serialized)


# UT: UT-224
# Test Description: Verifies enriched capiss mint-decision audit schema for denied mint requests.
# Precondition: Module fixtures are loaded and a denied Jira MCP decision is emitted without token issuance fields.
# Expected Output: The SUT emits denial context, local and UTC logged time, resource attributes, and omits token validity fields.
# Covers DD: DD-222
@pytest.mark.invariant
def test_log_mint_decision_deny_omits_validity_but_keeps_context(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events: list[tuple[str, dict[str, object]]] = []
    guard.exercise("set demo timezone", lambda: setattr(capiss_module, "VARAMBU_TZ", "Europe/Berlin"))
    guard.exercise("freeze audit log time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_800_000_030))
    guard.exercise("capture audit event", lambda: monkeypatch.setattr(capiss_module, "log_event", lambda event_type, **fields: events.append((event_type, fields))))
    guard.exercise(
        "emit deny mint decision",
        lambda: capiss_module.log_mint_decision(
            result="deny",
            reason_code="policy",
            decision_type="root_mint",
            subject_spiffe_id="spiffe://varambu.org/codex-jira-mcp-adapter",
            aud="jira-mcp-gateway",
            act="read_project_summary",
            res="jira-mcp:/project:NAS",
            correlation_id="corr-deny",
        ),
    )
    _, fields = guard.exercise("read captured event", lambda: events[0])
    guard.outcome("deny result logged", fields["result"] == "deny" and fields["reason_code"] == "policy")
    guard.outcome("context retained", fields["subject_spiffe_id"] == "spiffe://varambu.org/codex-jira-mcp-adapter")
    guard.outcome("resource attrs derived for denied canonical resource", fields["resource_attrs"] == {"kind": "jira_project", "project_key": "NAS"})
    guard.outcome("logged local time present", fields["timestamp_local"] == "2027-01-15 09:00:30 Europe/Berlin")
    guard.outcome("validity fields omitted", "issued_at_utc" not in fields and "expires_at_utc" not in fields and "ttl_seconds" not in fields)


# UT: UT-225
# Test Description: Verifies capiss audit timestamp formatting falls back to UTC when the configured Varambu timezone is invalid.
# Precondition: Module fixtures are loaded and the Varambu timezone setting is an invalid zone name.
# Expected Output: The SUT emits UTC-labeled local display fields instead of failing audit emission.
# Covers DD: DD-222
@pytest.mark.invariant
def test_log_mint_decision_invalid_timezone_falls_back_to_utc(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events: list[tuple[str, dict[str, object]]] = []
    guard.exercise("set invalid demo timezone", lambda: setattr(capiss_module, "VARAMBU_TZ", "Bad/Zone"))
    guard.exercise("freeze audit log time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_800_000_000))
    guard.exercise("capture audit event", lambda: monkeypatch.setattr(capiss_module, "log_event", lambda event_type, **fields: events.append((event_type, fields))))
    guard.exercise(
        "emit audit decision",
        lambda: capiss_module.log_mint_decision(
            result="deny",
            reason_code="policy",
            decision_type="root_mint",
            subject_spiffe_id="spiffe://varambu.org/agent-a",
            aud="tool-b",
            act="read",
            res="tool-b:/search",
        ),
    )
    _, fields = guard.exercise("read captured event", lambda: events[0])
    guard.outcome("timezone fell back to utc", fields["timezone"] == "UTC")
    guard.outcome("local display uses utc", fields["timestamp_local"] == "2027-01-15 08:00:00 UTC")


# UT: UT-234
# Test Description: Verifies capiss derives resource attributes only for known canonical Jira resources.
# Precondition: Module fixtures are loaded and resource strings cover Jira Tool, Jira MCP, unknown, malformed, and non-string inputs.
# Expected Output: The SUT returns Jira project attributes only when they are safely derivable.
# Covers DD: DD-222
@pytest.mark.boundary
def test_resource_attrs_for_known_and_unknown_resources(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    results = guard.exercise(
        "derive resource attrs",
        lambda: {
            "jira_tool": capiss_module.resource_attrs_for("jira-tool:/project:IAM"),
            "jira_mcp": capiss_module.resource_attrs_for("jira-mcp:/project:NAS"),
            "unknown": capiss_module.resource_attrs_for("tool-b:/search"),
            "malformed": capiss_module.resource_attrs_for("jira-mcp:/project:bad"),
            "none": capiss_module.resource_attrs_for(None),
        },
    )
    guard.outcome("jira tool attrs derived", results["jira_tool"] == {"kind": "jira_project", "project_key": "IAM"})
    guard.outcome("jira mcp attrs derived", results["jira_mcp"] == {"kind": "jira_project", "project_key": "NAS"})
    guard.outcome("unknown omitted", results["unknown"] is None)
    guard.outcome("malformed omitted", results["malformed"] is None)
    guard.outcome("non-string omitted", results["none"] is None)


# UT: UT-235
# Test Description: Verifies optional audit header normalization keeps only non-empty strings.
# Precondition: Module fixtures are loaded and header candidates include a value, empty string, and non-string object.
# Expected Output: The SUT preserves the real header value and normalizes absent or framework-default values to None.
# Covers DD: DD-222
@pytest.mark.boundary
def test_optional_header_value_normalizes_non_strings(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    results = guard.exercise(
        "normalize header values",
        lambda: {
            "value": capiss_module.optional_header_value("corr-1"),
            "empty": capiss_module.optional_header_value("   "),
            "object": capiss_module.optional_header_value(object()),
        },
    )
    guard.outcome("string kept", results["value"] == "corr-1")
    guard.outcome("empty omitted", results["empty"] is None)
    guard.outcome("object omitted", results["object"] is None)


# UT: UT-236
# Test Description: Verifies root key creation handles a concurrent creator by loading the existing file.
# Precondition: The key file already contains a valid private key and os.open is stubbed to raise FileExistsError.
# Expected Output: The SUT loads the existing key and reports that it did not create a new key.
# Covers DD: DD-111
@pytest.mark.invariant
def test_load_or_create_root_private_key_handles_file_exists_race(capiss_module, monkeypatch, tmp_path, guard):
    _premise_module_loaded(guard, capiss_module)
    guard.exercise("set key file paths", lambda: _set_key_paths(capiss_module, tmp_path))
    first_key, _ = guard.exercise("create initial key", capiss_module.load_or_create_root_private_key)
    guard.exercise("remove cached key to force create path", lambda: monkeypatch.setattr(capiss_module, "ROOT_PRIVATE_KEY", first_key))
    guard.exercise("stub os.path.exists false", lambda: monkeypatch.setattr(capiss_module.os.path, "exists", lambda path: False if path == capiss_module.CAPISS_KEY_FILE else Path(path).exists()))
    guard.exercise("stub os.open race", lambda: monkeypatch.setattr(capiss_module.os, "open", lambda *_args, **_kwargs: (_ for _ in ()).throw(FileExistsError())))
    loaded_key, created = guard.exercise("load key after race", capiss_module.load_or_create_root_private_key)
    guard.outcome("not created", created is False)
    guard.outcome("existing key loaded", loaded_key.to_bytes() == first_key.to_bytes())


# UT: UT-237
# Test Description: Verifies mint-rate parsing handles malformed allowed flags and byte reasons.
# Precondition: Redis eval replies are controlled and current time is deterministic.
# Expected Output: The SUT fails closed for a non-integer flag and recognizes a byte-encoded mint-rate denial.
# Covers DD: DD-221
@pytest.mark.boundary
def test_consume_mint_rate_parses_edge_replies(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class SequenceClient:
        def __init__(self):
            self.replies = [["bad", "ok"], [0, b"mint_rate_exceeded"]]

        def eval(self, *_args):
            return self.replies.pop(0)

    client = SequenceClient()
    guard.exercise("mock redis sequence", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: client))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_000))
    malformed = guard.exercise("consume with malformed flag", lambda: capiss_module.consume_mint_rate("root-1", 1_060, 60))
    exceeded = guard.exercise("consume with byte reason", lambda: capiss_module.consume_mint_rate("root-1", 1_060, 60))
    guard.outcome("malformed fails closed", malformed == (False, "store_unavailable"))
    guard.outcome("byte reason decoded", exceeded == (False, "mint_rate_exceeded"))


# UT: UT-240
# Test Description: Verifies capiss parser and payload validators fail closed on boundary inputs.
# Precondition: Module fixtures are loaded and input values cover unknown facts, empty lines, bad payload types, and wildcard resources.
# Expected Output: The SUT ignores non-facts and rejects malformed mint payload or non-canonical resources.
# Covers DD: DD-101, DD-115, DD-116, DD-117
@pytest.mark.boundary
def test_parser_payload_and_resource_rejection_branches(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    raw_arg = guard.exercise("parse raw nonnumeric arg", lambda: capiss_module.parse_fact_arg("plain"))
    claims = guard.exercise(
        "parse block source with ignored lines",
        lambda: capiss_module.parse_block_source('\nignored line\nact("read");\n'),
    )
    missing_body = guard.exercise("validate missing body", lambda: capiss_module.validate_mint_payload(None))
    non_string = guard.exercise("validate non-string field", lambda: capiss_module.validate_mint_payload({"aud": 7, "act": "read", "res": "tool-b:/search"}))
    empty_value = guard.exercise("validate empty field", lambda: capiss_module.validate_mint_payload({"aud": "tool-b", "act": " ", "res": "tool-b:/search"}))
    rejected_resources = guard.exercise(
        "canonicalize rejected resources",
        lambda: [
            capiss_module.canonicalize_jira_project_resource("tool-b:/search"),
            capiss_module.canonicalize_jira_project_resource("jira-tool:/project:BAD:*"),
            capiss_module.canonicalize_jira_mcp_project_resource("tool-b:/search"),
            capiss_module.canonicalize_jira_mcp_project_resource("jira-mcp:/project:BAD/KEY"),
            capiss_module.canonicalize_resource("tool-b", "tool-b:/regex"),
        ],
    )

    guard.outcome("raw arg preserved", raw_arg == "plain")
    guard.outcome("invalid source line ignored", claims == {"act": "read"})
    guard.outcome("missing body rejected", missing_body[0] is None and missing_body[1].status_code == 400)
    guard.outcome("non-string field rejected", non_string[0] is None and non_string[1].status_code == 400)
    guard.outcome("empty field rejected", empty_value[0] is None and empty_value[1].status_code == 400)
    guard.outcome("unsafe resources rejected", rejected_resources == [None, None, None, None, None])


# UT: UT-111
# Test Description: Verifies that get_redis constructs the Redis client once with exact module configuration and then reuses the cached instance.
# Precondition: Module fixtures are loaded, the module cache is empty, and the Redis factory is replaced with a recording stub.
# Expected Output: The SUT calls Redis.from_url exactly once with the configured URL and socket settings, then returns the cached client on subsequent calls.
# Covers DD: DD-114
@pytest.mark.invariant
def test_get_redis_caches_exact_constructed_client(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    client = object()
    guard.exercise("reset redis cache", lambda: monkeypatch.setattr(capiss_module, "_redis_client", None))

    def fake_from_url(*args, **kwargs):
        calls.append((args, kwargs))
        return client

    guard.exercise(
        "capture redis factory",
        lambda: monkeypatch.setattr(capiss_module.redis.Redis, "from_url", fake_from_url),
    )
    first = guard.exercise("get redis first time", capiss_module.get_redis)
    second = guard.exercise("get redis second time", capiss_module.get_redis)
    guard.outcome("cached client returned first time", first is client)
    guard.outcome("cached client returned second time", second is client)
    guard.outcome("factory called once", len(calls) == 1)
    guard.outcome(
        "factory args exact",
        calls[0]
        == (
            (capiss_module.M4_REDIS_URL,),
            {
                "encoding": "utf-8",
                "decode_responses": True,
                "socket_timeout": capiss_module.M4_REDIS_SOCKET_TIMEOUT,
            },
        ),
    )


# UT: UT-042
# Test Description: Verifies that decision input contains optional fields.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_contains_optional_fields(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            root_token_id="root-1",
            registry_hit=True,
        ),
    )
    guard.outcome(
        "exact payload with optionals",
        payload
        == {
            "decision_type": "resource_mint",
            "sub": "spiffe://varambu.org/agent-a",
            "subject_spiffe_id": "spiffe://varambu.org/agent-a",
            "aud": "tool-b",
            "act": "read",
            "res": "tool-b:/search",
            "root_token_id": "root-1",
            "registry_hit": True,
        },
    )


# UT: UT-091
# Test Description: Verifies that decision input returns the exact mandatory payload shape without optional fields.
# Precondition: Module fixtures are loaded and the caller provides only the mandatory decision input fields.
# Expected Output: The SUT returns exactly the six mandatory fields, with sub and subject_spiffe_id matching the provided subject.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_returns_exact_base_payload(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build base decision input",
        lambda: capiss_module.decision_input(
            "root_mint",
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome(
        "exact mandatory payload",
        payload
        == {
            "decision_type": "root_mint",
            "sub": "spiffe://varambu.org/agent-a",
            "subject_spiffe_id": "spiffe://varambu.org/agent-a",
            "aud": "tool-b",
            "act": "read",
            "res": "tool-b:/search",
        },
    )


# UT: UT-092
# Test Description: Verifies that decision input omits root_token_id when it is not provided.
# Precondition: Module fixtures are loaded and only registry_hit is supplied as an optional field.
# Expected Output: The SUT includes registry_hit and omits root_token_id entirely from the payload.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_omits_root_token_id_when_none(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input without root token",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            registry_hit=False,
        ),
    )
    guard.outcome("root_token_id omitted", "root_token_id" not in payload)
    guard.outcome("registry_hit included", payload == {
        "decision_type": "resource_mint",
        "sub": "spiffe://varambu.org/agent-a",
        "subject_spiffe_id": "spiffe://varambu.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "registry_hit": False,
    })


# UT: UT-093
# Test Description: Verifies that decision input omits registry_hit when it is not provided.
# Precondition: Module fixtures are loaded and only root_token_id is supplied as an optional field.
# Expected Output: The SUT includes root_token_id and omits registry_hit entirely from the payload.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_omits_registry_hit_when_none(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input without registry flag",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            root_token_id="root-1",
        ),
    )
    guard.outcome("registry_hit omitted", "registry_hit" not in payload)
    guard.outcome("root_token_id included", payload == {
        "decision_type": "resource_mint",
        "sub": "spiffe://varambu.org/agent-a",
        "subject_spiffe_id": "spiffe://varambu.org/agent-a",
        "aud": "tool-b",
        "act": "read",
        "res": "tool-b:/search",
        "root_token_id": "root-1",
    })


# UT: UT-094
# Test Description: Verifies that decision input preserves an explicit false registry_hit value.
# Precondition: Module fixtures are loaded and registry_hit is provided as False.
# Expected Output: The SUT keeps registry_hit in the payload with the exact False value instead of omitting or coercing it.
# Covers DD: DD-125
@pytest.mark.invariant
def test_decision_input_preserves_false_registry_hit(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    payload = guard.exercise(
        "build decision input with false registry flag",
        lambda: capiss_module.decision_input(
            "resource_mint",
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
            registry_hit=False,
        ),
    )
    guard.outcome("registry_hit explicitly false", payload.get("registry_hit") is False)
    guard.outcome("subject fields match", payload.get("sub") == payload.get("subject_spiffe_id") == "spiffe://varambu.org/agent-a")


# UT: UT-043
# Test Description: Verifies that extract chain claims defaults depth when missing.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-118
@pytest.mark.boundary
def test_extract_chain_claims_defaults_depth_when_missing(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    token, _, _, _, _ = guard.exercise(
        "mint root biscuit",
        lambda: capiss_module.mint_root_biscuit(
            "spiffe://varambu.org/agent-a",
            "tool-b",
            "read",
            "tool-b:/search",
        ),
    )
    biscuit = guard.exercise("load biscuit from token", lambda: capiss_module.Biscuit.from_base64(token, capiss_module.ROOT_PUBLIC_KEY))
    chain = guard.exercise("extract chain claims", lambda: capiss_module.extract_chain_claims(biscuit))
    guard.outcome("default delegation depth is zero", chain[0].get("delegation_depth") == 0)


# UT: UT-129
# Test Description: Verifies that capiss consumes mint-rate allowance until the formula-derived limit is reached and then denies.
# Precondition: The Redis dependency is replaced with a deterministic fake that returns three allows followed by one deny for the same root context.
# Expected Output: The SUT returns allow for the first three consumes under a 60-second lifetime and then returns the exact deny reason `mint_rate_exceeded`.
# Covers DD: DD-221
@pytest.mark.boundary
def test_consume_mint_rate_allows_until_formula_limit_then_denies(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class SequenceClient:
        def __init__(self):
            self.calls = 0

        def eval(self, *args):
            self.calls += 1
            if self.calls <= 3:
                return [1, "ok", self.calls]
            return [0, "mint_rate_exceeded", 3]

    client = SequenceClient()
    guard.exercise("mock sequence redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: client))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_000))

    outcomes = [
        guard.exercise(
            f"consume mint rate call {idx}",
            lambda: capiss_module.consume_mint_rate("root-1", 1_060, 60),
        )
        for idx in range(1, 5)
    ]

    guard.outcome("first consume allowed", outcomes[0] == (True, ""))
    guard.outcome("second consume allowed", outcomes[1] == (True, ""))
    guard.outcome("third consume allowed", outcomes[2] == (True, ""))
    guard.outcome("fourth consume denied exactly", outcomes[3] == (False, "mint_rate_exceeded"))


# UT: UT-130
# Test Description: Verifies that capiss passes the exact Redis key, formula-derived allowance, and remaining root TTL to the mint-rate helper.
# Precondition: The Redis dependency is replaced with a recording fake and current time is frozen.
# Expected Output: The SUT calls Redis with key `m4:mint_rate:<root_token_id>`, an allowance of `3` for a 60-second root lifetime, and a TTL equal to the remaining root lifetime.
# Covers DD: DD-221
@pytest.mark.invariant
def test_consume_mint_rate_uses_exact_key_allowance_and_ttl(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    call_args = []

    class RecordingClient:
        def eval(self, *args):
            call_args.append(args)
            return [1, "ok", 1]

    guard.exercise("mock recording redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: RecordingClient()))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_000))
    ok, err = guard.exercise("consume mint rate", lambda: capiss_module.consume_mint_rate("root-7", 1_017, 60))
    guard.outcome("consume succeeds", ok is True)
    guard.outcome("empty error on success", err == "")
    guard.outcome("redis called once", len(call_args) == 1)
    guard.outcome("script uses one key", call_args[0][1] == 1)
    guard.outcome("mint-rate key exact", call_args[0][2] == "m4:mint_rate:root-7")
    guard.outcome("allowance exact", call_args[0][3] == "3")
    guard.outcome("ttl exact", call_args[0][4] == "17")


# UT: UT-131
# Test Description: Verifies that the mint-rate allowance formula scales with root-token lifetime and floors to one.
# Precondition: The Redis dependency is replaced with a recording fake and current time is frozen.
# Expected Output: The SUT passes allowance `2` for 40 seconds, `1` for 20 seconds, and still `1` for lifetimes below 20 seconds.
# Covers DD: DD-221
@pytest.mark.boundary
def test_consume_mint_rate_formula_scales_and_floors_to_one(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    allowances = []

    class RecordingClient:
        def eval(self, *args):
            allowances.append(args[3])
            return [1, "ok", 1]

    guard.exercise("mock recording redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: RecordingClient()))
    guard.exercise("freeze current time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_000))
    guard.exercise("consume mint rate for 40 second root lifetime", lambda: capiss_module.consume_mint_rate("root-40", 1_030, 40))
    guard.exercise("consume mint rate for 20 second root lifetime", lambda: capiss_module.consume_mint_rate("root-20", 1_020, 20))
    guard.exercise("consume mint rate for 19 second root lifetime", lambda: capiss_module.consume_mint_rate("root-19", 1_019, 19))
    guard.outcome("40 second lifetime yields allowance two", allowances[0] == "2")
    guard.outcome("20 second lifetime yields allowance one", allowances[1] == "1")
    guard.outcome("sub-20 lifetime still yields allowance one", allowances[2] == "1")


# UT: UT-132
# Test Description: Verifies that capiss fails closed when the mint-rate store returns a malformed reply.
# Precondition: The Redis dependency is replaced with a fake that returns a malformed Lua reply shape.
# Expected Output: The SUT returns the exact fail-closed reason `store_unavailable`.
# Covers DD: DD-221
@pytest.mark.invariant
def test_consume_mint_rate_fails_closed_on_malformed_store_reply(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class MalformedClient:
        def eval(self, *args):
            return ["ok"]

    guard.exercise("mock malformed redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: MalformedClient()))
    ok, err = guard.exercise("consume mint rate with malformed reply", lambda: capiss_module.consume_mint_rate("root-1", int(time.time()) + 10, 60))
    guard.outcome("consume denied", ok is False)
    guard.outcome("reason store_unavailable", err == "store_unavailable")


# UT: UT-133
# Test Description: Verifies that capiss fails closed when the mint-rate store raises a Redis error.
# Precondition: The Redis dependency is replaced with a fake that raises `redis.RedisError`.
# Expected Output: The SUT returns the exact fail-closed reason `store_unavailable`.
# Covers DD: DD-221
@pytest.mark.invariant
def test_consume_mint_rate_fails_closed_on_store_error(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)

    class BrokenClient:
        def eval(self, *args):
            raise redis.RedisError("down")

    guard.exercise("mock broken redis client", lambda: monkeypatch.setattr(capiss_module, "get_redis", lambda: BrokenClient()))
    ok, err = guard.exercise("consume mint rate with store error", lambda: capiss_module.consume_mint_rate("root-1", int(time.time()) + 10, 60))
    guard.outcome("consume denied", ok is False)
    guard.outcome("reason store_unavailable", err == "store_unavailable")


# UT: UT-246
# Test Description: Verifies enriched capiss mint-decision audit schema for a delegated resource mint with parent context and token validity fields.
# Precondition: Module fixtures are loaded and a resource mint allow decision is emitted with parent_token_id, delegation_depth, and issued/expires timestamps.
# Expected Output: The SUT emits parent_token_id, delegation_depth, root_token_id, token_id, issued/expires UTC fields, and computed ttl_seconds.
# Covers DD: DD-222
@pytest.mark.invariant
def test_log_mint_decision_resource_mint_includes_parent_context_and_validity(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events: list[tuple[str, dict]] = []
    guard.exercise("freeze audit log time", lambda: monkeypatch.setattr(capiss_module.time, "time", lambda: 1_800_000_030))
    guard.exercise("capture audit event", lambda: monkeypatch.setattr(capiss_module, "log_event", lambda event_type, **fields: events.append((event_type, fields))))
    guard.exercise(
        "emit resource mint allow decision",
        lambda: capiss_module.log_mint_decision(
            result="allow",
            reason_code="ok",
            decision_type="resource_mint",
            subject_spiffe_id="spiffe://varambu.org/codex-jira-mcp-adapter",
            aud="jira-mcp-gateway",
            act="create_story",
            res="jira-mcp:/project:IAM",
            root_token_id="root-1",
            parent_token_id="parent-1",
            token_id="resource-1",
            delegation_depth=1,
            issued_at=1_800_000_000,
            expires_at=1_800_000_060,
        ),
    )
    _, fields = guard.exercise("read captured event", lambda: events[0])
    guard.outcome("decision type is resource_mint", fields["decision_type"] == "resource_mint")
    guard.outcome("parent_token_id included", fields["parent_token_id"] == "parent-1")
    guard.outcome("delegation_depth included", fields["delegation_depth"] == 1)
    guard.outcome("token_id included", fields["token_id"] == "resource-1")
    guard.outcome("root_token_id included", fields["root_token_id"] == "root-1")
    guard.outcome("issued_at_utc present", "issued_at_utc" in fields)
    guard.outcome("expires_at_utc present", "expires_at_utc" in fields)
    guard.outcome("actual ttl computed", fields["ttl_seconds"] == 60)


# UT: UT-247
# Test Description: Verifies capiss audit omits the correlation_id field entirely when the caller does not supply one.
# Precondition: Module fixtures are loaded and a mint decision is emitted without a correlation_id argument.
# Expected Output: The SUT emits a capiss_mint_decision event that does not contain a correlation_id key.
# Covers DD: DD-222
@pytest.mark.invariant
def test_log_mint_decision_omits_correlation_id_when_absent(capiss_module, monkeypatch, guard):
    _premise_module_loaded(guard, capiss_module)
    events: list[tuple[str, dict]] = []
    guard.exercise("capture audit event", lambda: monkeypatch.setattr(capiss_module, "log_event", lambda event_type, **fields: events.append((event_type, fields))))
    guard.exercise(
        "emit decision without correlation",
        lambda: capiss_module.log_mint_decision(
            result="deny",
            reason_code="policy",
            decision_type="root_mint",
            subject_spiffe_id="spiffe://varambu.org/agent-a",
            aud="tool-b",
            act="read",
            res="tool-b:/search",
        ),
    )
    _, fields = guard.exercise("read captured event", lambda: events[0])
    guard.outcome("correlation_id absent when not provided", "correlation_id" not in fields)
