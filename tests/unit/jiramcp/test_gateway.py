from __future__ import annotations

import io
import json

import pytest


def _claims(**overrides):
    data = {
        "root_token_id": "root-1",
        "token_id": "token-root",
        "subject_spiffe_id": "spiffe://varambu.org/codex-jira-mcp-adapter",
        "aud": "jira-mcp-gateway",
        "act": "read_project_summary",
        "res": "jira-mcp:/project:IAM",
        "exp": 2_000_000_000,
        "effective_depth": 0,
    }
    data.update(overrides)
    return data


def _stub_token_parse(mod, monkeypatch, claims):
    monkeypatch.setattr(mod, "load_capiss_public_key", lambda: object())
    monkeypatch.setattr(mod.Biscuit, "from_base64", lambda *_: object())
    monkeypatch.setattr(mod, "verify_chain_and_claims", lambda _: (dict(claims), ""))


class _HandlerHarness:
    def __init__(self, mod, path: str, payload: object | None = None, headers: dict[str, str] | None = None):
        self.handler = mod.JiraMcpGatewayHandler.__new__(mod.JiraMcpGatewayHandler)
        body = b"" if payload is None else json.dumps(payload).encode("utf-8")
        self.handler.path = path
        self.handler.headers = {"Content-Length": str(len(body)), **(headers or {})}
        self.handler.rfile = io.BytesIO(body)
        self.handler.wfile = io.BytesIO()
        self.status = None
        self.headers: list[tuple[str, str]] = []
        self.handler.send_response = lambda status: setattr(self, "status", status)
        self.handler.send_header = lambda key, value: self.headers.append((key, value))
        self.handler.end_headers = lambda: None

    def json_body(self) -> dict:
        raw = self.handler.wfile.getvalue().decode("utf-8")
        return json.loads(raw) if raw else {}


# UT: UT-197
# Test Description: Verifies gateway parses only canonical Jira MCP project resources.
# Precondition: gateway module is loaded and resources include valid and invalid forms.
# Expected Output: Valid resources return project keys and malformed resources return no project.
# Covers DD: DD-503
@pytest.mark.boundary
def test_project_from_resource_requires_jira_mcp_prefix(jiramcp_gateway_module, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    results = guard.exercise(
        "parse resources",
        lambda: {
            "iam": mod.project_from_resource("jira-mcp:/project:IAM"),
            "nas": mod.project_from_resource("jira-mcp:/project:NAS"),
            "old": mod.project_from_resource("jira-tool:/project:IAM"),
            "lower": mod.project_from_resource("jira-mcp:/project:iam"),
        },
    )
    guard.outcome("IAM parsed", results["iam"] == "IAM")
    guard.outcome("NAS parsed syntactically", results["nas"] == "NAS")
    guard.outcome("old resource rejected", results["old"] is None)
    guard.outcome("lowercase rejected", results["lower"] is None)


@pytest.mark.negative_control
@pytest.mark.parametrize(
    ("overrides", "spiffe_id", "expected_act", "requested_project", "expected_reason"),
    [
        ({}, "spiffe://varambu.org/rogue", "read_project_summary", "IAM", "subject_mismatch"),
        ({"aud": "jira-tool"}, "spiffe://varambu.org/codex-jira-mcp-adapter", "read_project_summary", "IAM", "aud_mismatch"),
        ({"act": "create_story"}, "spiffe://varambu.org/codex-jira-mcp-adapter", "read_project_summary", "IAM", "act_mismatch"),
        ({"res": "jira-mcp:/project:NAS"}, "spiffe://varambu.org/codex-jira-mcp-adapter", "read_project_summary", "IAM", "project_mismatch"),
    ],
)
# UT: UT-198
# Test Description: Verifies gateway enforces subject, audience, action, and project before budget spend.
# Precondition: token verification dependencies are stubbed and budget spending is captured.
# Expected Output: Authority mismatches return exact M5 deny reasons and do not consume budget.
# Covers DD: DD-506, DD-507
def test_verify_token_denies_authority_mismatches_before_budget(
    jiramcp_gateway_module,
    monkeypatch,
    guard,
    overrides,
    spiffe_id,
    expected_act,
    requested_project,
    expected_reason,
):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    _stub_token_parse(mod, monkeypatch, _claims(**overrides))
    consumed: list[str] = []
    guard.exercise("stub budget capture", lambda: monkeypatch.setattr(mod, "consume_budget_and_rate", lambda root, exp: consumed.append(root) or (True, "ok", 9)))
    allowed, reason, _claims_out = guard.exercise(
        "verify token",
        lambda: mod.verify_token("token", spiffe_id, expected_act, requested_project),
    )
    guard.outcome("token denied", allowed is False)
    guard.outcome("exact reason returned", reason == expected_reason)
    guard.outcome("budget not consumed by verifier", consumed == [])


# UT: UT-199
# Test Description: Verifies gateway create payload validation accepts only the Slice 1 story contract.
# Precondition: gateway module is loaded and valid, raw ADF, and arbitrary field payloads are supplied.
# Expected Output: Required fields pass, raw ADF and arbitrary Jira fields fail closed.
# Covers DD: DD-509
@pytest.mark.boundary
def test_validate_create_payload_allowlist(jiramcp_gateway_module, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    valid, valid_err = guard.exercise(
        "validate story payload",
        lambda: mod.validate_create_payload({"project_key": "IAM", "summary": "s", "description": "d", "acceptance_criteria": ["a"], "epic_key": "IAM-101"}),
    )
    raw_adf, raw_adf_err = guard.exercise(
        "validate raw ADF payload",
        lambda: mod.validate_create_payload({"project_key": "IAM", "summary": "s", "description": {"type": "doc"}}),
    )
    extra, extra_err = guard.exercise(
        "validate arbitrary field payload",
        lambda: mod.validate_create_payload({"project_key": "IAM", "summary": "s", "description": "d", "assignee": "user"}),
    )
    guard.outcome("valid story payload accepted", valid is not None and valid_err is None)
    guard.outcome("raw ADF rejected", raw_adf is None and raw_adf_err == "payload_invalid")
    guard.outcome("arbitrary field rejected", extra is None and extra_err == "payload_invalid")


# UT: UT-200
# Test Description: Verifies gateway shapes project summaries to bounded non-sensitive fields.
# Precondition: gateway module is loaded and upstream payload contains hidden fields and excess counts.
# Expected Output: Summary includes at most 50 issues, 25 epics, and omits hidden Jira data.
# Covers DD: DD-512
@pytest.mark.invariant
def test_shape_project_summary_bounds_and_omits_hidden_fields(jiramcp_gateway_module, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    payload = {
        "project": {"key": "IAM", "name": "IAM", "issue_count": 100},
        "issues": [
            {"key": f"IAM-{i}", "summary": "s", "status": "To Do", "issue_type": "Story", "description": "secret", "comments": ["secret"], "assignee": "secret"}
            for i in range(60)
        ]
        + [
            {"key": f"IAM-{100+i}", "summary": "e", "status": "To Do", "issue_type": "Epic", "description": "secret"}
            for i in range(30)
        ],
    }
    shaped = guard.exercise("shape summary", lambda: mod.shape_project_summary(payload))
    text = str(shaped)
    guard.outcome("issue bound enforced", len(shaped["issues"]) == 50)
    guard.outcome("epic bound enforced", len(shaped["epics"]) == 25)
    guard.outcome("hidden fields omitted", "description" not in text and "comments" not in text and "assignee" not in text)


# UT: UT-201
# Test Description: Verifies gateway validates same-project Epic before story creation.
# Precondition: upstream issue responses are stubbed for Epic, non-Epic, and cross-project cases.
# Expected Output: Valid same-project Epic passes while non-Epic and cross-project values fail.
# Covers DD: DD-513
@pytest.mark.invariant
def test_verify_epic_requires_same_project_epic(jiramcp_gateway_module, monkeypatch, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)

    def fake_upstream(path, _corr):
        if path.endswith("IAM-101"):
            return 200, {"fields": {"project": {"key": "IAM"}, "issuetype": {"name": "Epic"}}}
        if path.endswith("IAM-900"):
            return 200, {"fields": {"project": {"key": "IAM"}, "issuetype": {"name": "Task"}}}
        return 200, {"fields": {"project": {"key": "NAS"}, "issuetype": {"name": "Epic"}}}

    guard.exercise("stub upstream issue lookup", lambda: monkeypatch.setattr(mod, "call_upstream", fake_upstream))
    results = guard.exercise(
        "verify epic candidates",
        lambda: {
            "valid": mod.verify_epic("IAM-101", "IAM", "corr"),
            "non_epic": mod.verify_epic("IAM-900", "IAM", "corr"),
            "cross_project": mod.verify_epic("NAS-101", "IAM", "corr"),
        },
    )
    guard.outcome("same-project Epic accepted", results["valid"] is True)
    guard.outcome("same-project non-Epic rejected", results["non_epic"] is False)
    guard.outcome("cross-project Epic rejected before lookup", results["cross_project"] is False)


# UT: UT-204
# Test Description: Verifies gateway helper branches normalize payload, upstream, and budget errors.
# Precondition: gateway module is loaded and dependencies are stubbed for non-network outcomes.
# Expected Output: Validation, ADF conversion, upstream config, and Redis errors return bounded results.
# Covers DD: DD-507, DD-508, DD-510, DD-511
@pytest.mark.invariant
def test_gateway_helpers_cover_error_and_encoding_paths(jiramcp_gateway_module, monkeypatch, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)

    class FailingRedis:
        def eval(self, *_):
            raise mod.redis.RedisError("down")

    guard.exercise("stub redis failure", lambda: monkeypatch.setattr(mod, "_redis_client", FailingRedis()))
    budget = guard.exercise("consume budget with redis failure", lambda: mod.consume_budget_and_rate("root", 2_000_000_000))
    invalid_summary = guard.exercise("validate invalid summary", lambda: mod.validate_summary_payload({"project_key": "iam"}))
    adf = guard.exercise("convert plain text and acceptance criteria", lambda: mod.adf_from_plain_text("desc", ["one", "two"]))
    guard.exercise("force live mode without config", lambda: monkeypatch.setattr(mod, "JIRA_MCP_UPSTREAM_MODE", "live"))
    guard.exercise("clear live base url", lambda: monkeypatch.setattr(mod, "JIRA_BASE_URL", ""))

    def resolve_live_error():
        try:
            mod.upstream_base_url()
            return None
        except mod.UpstreamConfigError as exc:
            return str(exc)

    live_error = guard.exercise("resolve incomplete live upstream", resolve_live_error)

    guard.outcome("redis failure maps to gateway_unavailable", budget == (False, "gateway_unavailable", -1))
    guard.outcome("invalid summary rejected", invalid_summary == (None, "payload_invalid"))
    guard.outcome("ADF includes criteria heading", any("Acceptance Criteria:" in str(item) for item in adf["content"]))
    guard.outcome("incomplete live config rejected", live_error == "live Jira configuration is incomplete")


# UT: UT-205
# Test Description: Verifies gateway summary endpoint authorizes, consumes budget, shapes output, and logs allow.
# Precondition: HTTP handler is exercised with in-memory streams and token/upstream dependencies are stubbed.
# Expected Output: Summary response is 200, bounded, and includes no upstream hidden fields.
# Covers DD: DD-512, DD-514, DD-515
@pytest.mark.boundary
def test_gateway_summary_handler_happy_path(jiramcp_gateway_module, monkeypatch, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    events: list[tuple[str, dict]] = []
    claims = _claims()
    guard.exercise("stub authorization", lambda: monkeypatch.setattr(mod.JiraMcpGatewayHandler, "_authorize", lambda self, *_: ("spiffe://varambu.org/codex-jira-mcp-adapter", dict(claims))))
    guard.exercise("stub budget", lambda: monkeypatch.setattr(mod.JiraMcpGatewayHandler, "_consume_or_deny", lambda self, *_: True))
    guard.exercise(
        "stub upstream summary",
        lambda: monkeypatch.setattr(
            mod,
            "call_upstream",
            lambda *_args, **_kwargs: (
                200,
                {
                    "project": {"key": "IAM", "name": "Identity Access Management", "issue_count": 2},
                    "issues": [
                        {"key": "IAM-1", "summary": "Story", "status": "To Do", "issue_type": "Story", "description": "hidden"},
                        {"key": "IAM-101", "summary": "Epic", "status": "To Do", "issue_type": "Epic", "comments": ["hidden"]},
                    ],
                },
            ),
        ),
    )
    guard.exercise("capture audit", lambda: monkeypatch.setattr(mod, "log_event", lambda event_type, **fields: events.append((event_type, fields))))
    harness = _HandlerHarness(mod, "/mcp/jira/project-summary", {"project_key": "IAM"}, {"X-Correlation-ID": "corr-204"})
    guard.exercise("call summary handler", harness.handler.do_POST)
    body = harness.json_body()
    guard.outcome("summary returned success", harness.status == 200 and body["ok"] is True)
    guard.outcome("non-epic and epic split", len(body["issues"]) == 1 and len(body["epics"]) == 1)
    guard.outcome("hidden fields omitted", "hidden" not in json.dumps(body))
    guard.outcome("allow event recorded", events and events[0][1]["decision"] == "allow")


# UT: UT-206
# Test Description: Verifies gateway create endpoint validates epic, converts ADF, calls upstream, and returns bounded metadata.
# Precondition: HTTP handler is exercised with in-memory streams and token/upstream dependencies are stubbed.
# Expected Output: Story creation returns 201 with Story metadata and upstream body uses Jira ADF.
# Covers DD: DD-510, DD-513, DD-515
@pytest.mark.boundary
def test_gateway_create_handler_happy_path_with_epic(jiramcp_gateway_module, monkeypatch, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    upstream_bodies: list[dict] = []
    guard.exercise("stub authorization", lambda: monkeypatch.setattr(mod.JiraMcpGatewayHandler, "_authorize", lambda self, *_: ("spiffe://varambu.org/codex-jira-mcp-adapter", _claims(act="create_story"))))
    guard.exercise("stub budget", lambda: monkeypatch.setattr(mod.JiraMcpGatewayHandler, "_consume_or_deny", lambda self, *_: True))
    guard.exercise("stub epic verification", lambda: monkeypatch.setattr(mod, "verify_epic", lambda epic, project, corr: epic == "IAM-101" and project == "IAM"))

    def fake_upstream(path, correlation_id, method="GET", body=None):
        upstream_bodies.append(body or {})
        return 201, {"key": "IAM-1001", "self": "http://jira-mcp-mock/issue/IAM-1001"}

    guard.exercise("stub create upstream", lambda: monkeypatch.setattr(mod, "call_upstream", fake_upstream))
    guard.exercise("silence audit", lambda: monkeypatch.setattr(mod, "log_event", lambda *_args, **_kwargs: None))
    harness = _HandlerHarness(
        mod,
        "/mcp/jira/stories",
        {"project_key": "IAM", "summary": "Story", "description": "Desc", "acceptance_criteria": ["AC"], "epic_key": "IAM-101"},
        {"X-Correlation-ID": "corr-205"},
    )
    guard.exercise("call create handler", harness.handler.do_POST)
    body = harness.json_body()
    description = upstream_bodies[0]["fields"]["description"]
    guard.outcome("story creation returned bounded metadata", harness.status == 201 and body["key"] == "IAM-1001" and body["issue_type"] == "Story")
    guard.outcome("epic parent included", upstream_bodies[0]["fields"]["parent"] == {"key": "IAM-101"})
    guard.outcome("description converted to ADF", description["type"] == "doc" and description["version"] == 1)


# UT: UT-207
# Test Description: Verifies gateway handler denial branches return standardized local errors.
# Precondition: HTTP handler is exercised for unknown path, invalid JSON, authorization, and upstream failure cases.
# Expected Output: Each denial returns a bounded status and reason without raw upstream payload leakage.
# Covers DD: DD-515
@pytest.mark.negative_control
def test_gateway_handler_standard_denials(jiramcp_gateway_module, monkeypatch, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    guard.exercise("silence audit", lambda: monkeypatch.setattr(mod, "log_event", lambda *_args, **_kwargs: None))

    not_found = _HandlerHarness(mod, "/bad", {"project_key": "IAM"})
    guard.exercise("call unknown path", not_found.handler.do_POST)

    bad_json = _HandlerHarness(mod, "/mcp/jira/project-summary", None, {"Content-Length": "1", "X-Correlation-ID": "corr"})
    bad_json.handler.rfile = io.BytesIO(b"{")
    guard.exercise("call invalid json", bad_json.handler.do_POST)

    missing_subject = _HandlerHarness(mod, "/mcp/jira/project-summary", {"project_key": "IAM"})
    guard.exercise("call missing subject", missing_subject.handler.do_POST)

    guard.exercise("stub authorization", lambda: monkeypatch.setattr(mod.JiraMcpGatewayHandler, "_authorize", lambda self, *_: ("spiffe://varambu.org/codex-jira-mcp-adapter", _claims())))
    guard.exercise("stub budget", lambda: monkeypatch.setattr(mod.JiraMcpGatewayHandler, "_consume_or_deny", lambda self, *_: True))
    guard.exercise("stub upstream failure", lambda: monkeypatch.setattr(mod, "call_upstream", lambda *_args, **_kwargs: (503, {"secret": "raw"})))
    upstream_fail = _HandlerHarness(mod, "/mcp/jira/project-summary", {"project_key": "IAM"})
    guard.exercise("call upstream failure", upstream_fail.handler.do_POST)

    guard.outcome("unknown path is 404", not_found.status == 404)
    guard.outcome("invalid json is payload_invalid", bad_json.status == 400 and bad_json.json_body()["reason"] == "payload_invalid")
    guard.outcome("missing subject is subject_mismatch", missing_subject.status == 401 and missing_subject.json_body()["reason"] == "subject_mismatch")
    guard.outcome("upstream failure normalized", upstream_fail.status == 502 and upstream_fail.json_body()["reason"] == "upstream_error" and "secret" not in json.dumps(upstream_fail.json_body()))


# UT: UT-212
# Test Description: Verifies gateway verifier, budget, upstream transport, and GET helper branches.
# Precondition: gateway module is loaded and external key, Redis, and HTTP dependencies are stubbed.
# Expected Output: Success and failure branches normalize reasons and statuses without network access.
# Covers DD: DD-504, DD-505, DD-506, DD-507, DD-511, DD-515
@pytest.mark.invariant
def test_gateway_verifier_budget_transport_and_get_helpers(jiramcp_gateway_module, monkeypatch, guard):
    mod = jiramcp_gateway_module
    guard.premise("gateway module loaded", mod is not None)
    _stub_token_parse(mod, monkeypatch, _claims(exp=2_000_000_000))
    verified = guard.exercise("verify valid token", lambda: mod.verify_token("token", "spiffe://varambu.org/codex-jira-mcp-adapter", "read_project_summary", "IAM"))
    _stub_token_parse(mod, monkeypatch, _claims(exp=1))
    expired = guard.exercise("verify expired token", lambda: mod.verify_token("token", "spiffe://varambu.org/codex-jira-mcp-adapter", "read_project_summary", "IAM"))
    guard.exercise("stub biscuit parse failure", lambda: monkeypatch.setattr(mod.Biscuit, "from_base64", lambda *_: (_ for _ in ()).throw(mod.BiscuitValidationError("bad"))))
    invalid = guard.exercise("verify invalid token", lambda: mod.verify_token("token", "spiffe://varambu.org/codex-jira-mcp-adapter", "read_project_summary", "IAM"))

    class RedisResults:
        def __init__(self):
            self.results = [[1, "ok", 8], [0, "rate_limited", 8], [0, "missing_budget", -1], [9]]

        def eval(self, *_):
            return self.results.pop(0)

    guard.exercise("stub redis result sequence", lambda: monkeypatch.setattr(mod, "_redis_client", RedisResults()))
    budget_results = guard.exercise("consume budget variants", lambda: [mod.consume_budget_and_rate("root", 2_000_000_000) for _ in range(4)])

    class SuccessResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"ok":true}'

    class ErrorBody:
        def read(self):
            return b'{"error":"bad"}'

        def close(self):
            return None

    calls = []
    guard.exercise("stub upstream base", lambda: monkeypatch.setattr(mod, "upstream_base_url", lambda: "http://upstream"))
    guard.exercise("stub upstream headers", lambda: monkeypatch.setattr(mod, "upstream_headers", lambda corr: {"X-Correlation-ID": corr}))
    guard.exercise("stub upstream success", lambda: monkeypatch.setattr(mod.request, "urlopen", lambda req, **_kwargs: calls.append(req) or SuccessResponse()))
    upstream_ok = guard.exercise("call upstream success", lambda: mod.call_upstream("/ok", "corr", method="POST", body={"x": 1}))
    guard.exercise("stub upstream http error", lambda: monkeypatch.setattr(mod.request, "urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(mod.error.HTTPError("http://upstream/bad", 400, "bad", {}, ErrorBody()))))
    upstream_http = guard.exercise("call upstream http error", lambda: mod.call_upstream("/bad", "corr"))
    guard.exercise("stub upstream url error", lambda: monkeypatch.setattr(mod.request, "urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(mod.error.URLError("down"))))
    upstream_down = guard.exercise("call upstream url error", lambda: mod.call_upstream("/down", "corr"))

    health = _HandlerHarness(mod, "/health")
    missing = _HandlerHarness(mod, "/bad")
    guard.exercise("call health and missing GET", lambda: (health.handler.do_GET(), missing.handler.do_GET()))

    guard.outcome("valid token accepted", verified[0] is True and verified[2]["token_project"] == "IAM")
    guard.outcome("expired and invalid tokens denied", expired[1] == "token_invalid" and invalid[1] == "token_invalid")
    guard.outcome("budget variants normalized", budget_results == [(True, "ok", 8), (False, "rate_limited", 8), (False, "budget_exhausted", -1), (False, "gateway_unavailable", -1)])
    guard.outcome("upstream transport variants normalized", upstream_ok == (200, {"ok": True}) and upstream_http == (400, {"error": "bad"}) and upstream_down == (502, {"error": "upstream_unavailable"}))
    guard.outcome("GET health and 404 routes work", health.status == 200 and missing.status == 404)
