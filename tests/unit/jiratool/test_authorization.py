from __future__ import annotations

import base64
import io
from urllib import error

import pytest


def _premise_module_loaded(guard, jiratool_module):
    guard.premise("jira-tool module loaded", jiratool_module is not None)


def _claims(**overrides):
    data = {
        "root_token_id": "root-1",
        "token_id": "token-root",
        "subject_spiffe_id": "spiffe://example.org/agent-a",
        "aud": "jira-tool",
        "act": "read",
        "res": "jira-tool:/project:IAM",
        "exp": 2_000_000_000,
        "effective_depth": 0,
    }
    data.update(overrides)
    return data


def _stub_token_parse(jiratool_module, monkeypatch, claims):
    guard_public_key = object()
    biscuit = object()
    monkeypatch.setattr(jiratool_module, "load_capiss_public_key", lambda: guard_public_key)
    monkeypatch.setattr(jiratool_module.Biscuit, "from_base64", lambda *_: biscuit)
    monkeypatch.setattr(jiratool_module, "verify_chain_and_claims", lambda _: (dict(claims), ""))


def _handler(jiratool_module, *, path="/jira/rest/api/3/issue/IAM-1", headers=None):
    handler = object.__new__(jiratool_module.JiraToolHandler)
    handler.path = path
    handler.headers = headers or {}
    return handler


# UT: UT-164
# Test Description: Verifies jira-tool derives project scope from only the supported issue-read facade path.
# Precondition: jira-tool module is loaded and request paths cover allowed and malformed forms.
# Expected Output: Supported issue paths return issue/project tuples while unsupported paths are rejected.
# Covers DD: DD-306
@pytest.mark.boundary
def test_issue_key_from_facade_path_derives_project(jiratool_module, guard):
    _premise_module_loaded(guard, jiratool_module)
    results = guard.exercise(
        "parse jira facade paths",
        lambda: {
            "allowed": jiratool_module.issue_key_from_facade_path("/jira/rest/api/3/issue/IAM-1"),
            "query": jiratool_module.issue_key_from_facade_path("/jira/rest/api/3/issue/IAM-1?expand=all"),
            "search": jiratool_module.issue_key_from_facade_path("/jira/rest/api/3/search"),
            "lower": jiratool_module.issue_key_from_facade_path("/jira/rest/api/3/issue/iam-1"),
            "slash": jiratool_module.issue_key_from_facade_path("/jira/rest/api/3/issue/IAM-1/comment"),
        },
    )
    guard.outcome("allowed issue parsed", results["allowed"] == ("IAM-1", "IAM"))
    guard.outcome("query rejected", results["query"] is None)
    guard.outcome("search rejected", results["search"] is None)
    guard.outcome("lowercase issue rejected", results["lower"] is None)
    guard.outcome("nested route rejected", results["slash"] is None)


# UT: UT-165
# Test Description: Verifies jira-tool parses only canonical Jira project resources from token claims.
# Precondition: jira-tool module is loaded and resource candidates cover valid and invalid forms.
# Expected Output: Valid project resources return the project key and malformed resources return no project.
# Covers DD: DD-305
@pytest.mark.boundary
def test_project_from_resource_requires_canonical_project(jiratool_module, guard):
    _premise_module_loaded(guard, jiratool_module)
    results = guard.exercise(
        "parse token resources",
        lambda: {
            "iam": jiratool_module.project_from_resource("jira-tool:/project:IAM"),
            "nas": jiratool_module.project_from_resource("jira-tool:/project:NAS"),
            "lower": jiratool_module.project_from_resource("jira-tool:/project:iam"),
            "wild": jiratool_module.project_from_resource("jira-tool:/project:IAM*"),
            "wrong": jiratool_module.project_from_resource("jira-tool:/issue:IAM-1"),
        },
    )
    guard.outcome("IAM project parsed", results["iam"] == "IAM")
    guard.outcome("NAS project parsed", results["nas"] == "NAS")
    guard.outcome("lowercase rejected", results["lower"] is None)
    guard.outcome("wildcard rejected", results["wild"] is None)
    guard.outcome("wrong resource kind rejected", results["wrong"] is None)


# UT: UT-166
# Test Description: Verifies jira-tool allows a valid root Jira read token and consumes shared budget.
# Precondition: token parsing, chain verification, and budget state are stubbed for a valid IAM root token.
# Expected Output: The verifier allows the request and records remaining budget in the returned claims.
# Covers DD: DD-309, DD-308
@pytest.mark.invariant
def test_verify_biscuit_allows_full_authority_and_consumes_budget(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    _stub_token_parse(jiratool_module, monkeypatch, _claims())
    consumed: list[tuple[str, int]] = []
    guard.exercise(
        "stub budget allow",
        lambda: monkeypatch.setattr(
            jiratool_module,
            "consume_budget_and_rate",
            lambda root, exp: consumed.append((root, exp)) or (True, "ok", 9),
        ),
    )
    allowed, reason, claims = guard.exercise(
        "verify valid Jira token",
        lambda: jiratool_module.verify_biscuit("token", "spiffe://example.org/agent-a", "IAM"),
    )
    guard.outcome("request allowed", allowed is True)
    guard.outcome("no deny reason", reason == "")
    guard.outcome("budget consumed for root", consumed == [("root-1", 2_000_000_000)])
    guard.outcome("remaining budget recorded", claims["budget_remaining"] == 9)


# UT: UT-179
# Test Description: Verifies jira-tool permits write tokens for read/write checks and denies read tokens for write-only checks.
# Precondition: token parsing, chain verification, and budget state are stubbed for IAM root tokens with controlled actions.
# Expected Output: A write token can satisfy read-compatible and write-only checks, while a read token cannot satisfy write-only checks.
# Covers DD: DD-309
@pytest.mark.invariant
def test_verify_biscuit_enforces_read_write_action_sets(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    consumed: list[str] = []
    guard.exercise(
        "stub budget allow",
        lambda: monkeypatch.setattr(
            jiratool_module,
            "consume_budget_and_rate",
            lambda root, _exp: consumed.append(root) or (True, "ok", 9),
        ),
    )

    guard.exercise("stub write token", lambda: _stub_token_parse(jiratool_module, monkeypatch, _claims(act="write")))
    write_for_get = guard.exercise(
        "verify write token for read-compatible request",
        lambda: jiratool_module.verify_biscuit(
            "token",
            "spiffe://example.org/agent-a",
            "IAM",
            {"read", "write"},
        ),
    )
    write_for_put = guard.exercise(
        "verify write token for write-only request",
        lambda: jiratool_module.verify_biscuit(
            "token",
            "spiffe://example.org/agent-a",
            "IAM",
            {"write"},
        ),
    )
    guard.exercise("stub read token", lambda: _stub_token_parse(jiratool_module, monkeypatch, _claims(act="read")))
    read_for_put = guard.exercise(
        "verify read token for write-only request",
        lambda: jiratool_module.verify_biscuit(
            "token",
            "spiffe://example.org/agent-a",
            "IAM",
            {"write"},
        ),
    )

    guard.outcome("write token satisfies read-compatible request", write_for_get[0] is True)
    guard.outcome("write token satisfies write-only request", write_for_put[0] is True)
    guard.outcome("read token denied for write-only request", read_for_put[0:2] == (False, "insufficient_authority"))
    guard.outcome("budget consumed only for allowed uses", consumed == ["root-1", "root-1"])


# UT: UT-167
# Test Description: Verifies jira-tool denies stolen-token use by subject mismatch before budget consumption.
# Precondition: token parsing is stubbed for an agent-a token used by the rogue SPIFFE identity.
# Expected Output: The verifier denies with sub_mismatch and does not consume budget.
# Covers DD: DD-309
@pytest.mark.invariant
def test_verify_biscuit_denies_subject_mismatch_before_budget(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    _stub_token_parse(jiratool_module, monkeypatch, _claims())
    consumed: list[str] = []
    guard.exercise(
        "stub budget call capture",
        lambda: monkeypatch.setattr(
            jiratool_module,
            "consume_budget_and_rate",
            lambda root, exp: consumed.append(root) or (True, "ok", 9),
        ),
    )
    allowed, reason, _claims_out = guard.exercise(
        "verify stolen token",
        lambda: jiratool_module.verify_biscuit("token", "spiffe://example.org/rogue", "IAM"),
    )
    guard.outcome("request denied", allowed is False)
    guard.outcome("subject mismatch reason", reason == "sub_mismatch")
    guard.outcome("budget not consumed", consumed == [])


@pytest.mark.invariant
@pytest.mark.parametrize(
    ("claim_overrides", "requested_project", "expected_reason"),
    [
        ({"aud": "tool-b"}, "IAM", "insufficient_authority"),
        ({"act": "write"}, "IAM", "insufficient_authority"),
        ({"res": "jira-tool:/project:NAS"}, "IAM", "project_mismatch"),
        ({"res": "jira-tool:/project:iam"}, "IAM", "insufficient_authority"),
    ],
)
# UT: UT-168
# Test Description: Verifies jira-tool denies audience, action, and resource authority mismatches.
# Precondition: token parsing is stubbed with a single mismatched claim for each parameterized case.
# Expected Output: The verifier denies with the exact expected reason before spending budget.
# Covers DD: DD-309, DD-305
def test_verify_biscuit_denies_authority_mismatches(
    jiratool_module,
    monkeypatch,
    guard,
    claim_overrides: dict[str, str],
    requested_project: str,
    expected_reason: str,
):
    _premise_module_loaded(guard, jiratool_module)
    _stub_token_parse(jiratool_module, monkeypatch, _claims(**claim_overrides))
    consumed: list[str] = []
    guard.exercise(
        "stub budget call capture",
        lambda: monkeypatch.setattr(
            jiratool_module,
            "consume_budget_and_rate",
            lambda root, exp: consumed.append(root) or (True, "ok", 9),
        ),
    )
    allowed, reason, _claims_out = guard.exercise(
        "verify mismatched authority",
        lambda: jiratool_module.verify_biscuit("token", "spiffe://example.org/agent-a", requested_project),
    )
    guard.outcome("request denied", allowed is False)
    guard.outcome("exact reason returned", reason == expected_reason)
    guard.outcome("budget not consumed", consumed == [])


# UT: UT-169
# Test Description: Verifies jira-tool rejects delegated Jira tokens because M4a supports root project tokens only.
# Precondition: shared chain verification is stubbed to return an otherwise valid delegated chain.
# Expected Output: The chain adapter denies with delegation_not_supported.
# Covers DD: DD-307
@pytest.mark.invariant
def test_verify_chain_and_claims_rejects_delegated_jira_token(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    guard.exercise(
        "stub shared chain result with delegated depth",
        lambda: monkeypatch.setattr(
            jiratool_module,
            "verify_chain_contract",
            lambda *_args, **_kwargs: (_claims(effective_depth=1, parent_token_id="token-root"), None),
        ),
    )
    claims, err = guard.exercise(
        "verify delegated chain",
        lambda: jiratool_module.verify_chain_and_claims(object()),
    )
    guard.outcome("claims rejected", claims is None)
    guard.outcome("delegation not supported reason", err == "delegation_not_supported")


# UT: UT-170
# Test Description: Verifies jira-tool extracts upstream project keys only from valid successful Jira-shaped bodies.
# Precondition: jira-tool module is loaded and upstream response bodies cover valid, missing, malformed, and lowercase project keys.
# Expected Output: Only the valid uppercase project key is returned.
# Covers DD: DD-313
@pytest.mark.boundary
def test_upstream_project_key_requires_valid_project_field(jiratool_module, guard):
    _premise_module_loaded(guard, jiratool_module)
    results = guard.exercise(
        "extract upstream project keys",
        lambda: [
            jiratool_module.upstream_project_key(b'{"fields":{"project":{"key":"IAM"}}}'),
            jiratool_module.upstream_project_key(b'{"fields":{"project":{}}}'),
            jiratool_module.upstream_project_key(b'{"fields":{}}'),
            jiratool_module.upstream_project_key(b'{"fields":{"project":{"key":"iam"}}}'),
            jiratool_module.upstream_project_key(b"not-json"),
        ],
    )
    guard.outcome("only valid key extracted", results == ["IAM", None, None, None, None])


# UT: UT-171
# Test Description: Verifies jira-tool constructs upstream authorization only inside live mode.
# Precondition: jira-tool module is loaded in mock mode and then explicitly switched to live mode with server-side credentials.
# Expected Output: Mock mode sends no Authorization header and live mode constructs a Basic header from server-side configuration.
# Covers DD: DD-311
@pytest.mark.invariant
def test_upstream_headers_construct_auth_only_in_live_mode(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    mock_headers = guard.exercise("build mock headers", jiratool_module.upstream_headers)
    guard.exercise("switch to live mode", lambda: monkeypatch.setattr(jiratool_module, "JIRA_UPSTREAM_MODE", "live"))
    guard.exercise("set live email", lambda: monkeypatch.setattr(jiratool_module, "JIRA_EMAIL", "bot@example.org"))
    guard.exercise("set live api token", lambda: monkeypatch.setattr(jiratool_module, "JIRA_API_TOKEN", "secret-value"))
    live_headers = guard.exercise("build live headers", jiratool_module.upstream_headers)
    guard.outcome("mock mode has no authorization", "Authorization" not in mock_headers)
    guard.outcome("live mode has basic authorization", live_headers.get("Authorization", "").startswith("Basic "))
    guard.outcome("live header does not expose raw token", "secret-value" not in live_headers.get("Authorization", ""))


# UT: UT-172
# Test Description: Verifies jira-tool issuer-key loading handles missing, empty, valid, and cached key states.
# Precondition: capability issuer public-key path and key parser are controlled by the test.
# Expected Output: Missing/empty files return no key, a valid base64 file is parsed once, and later calls use the cache.
# Covers DD: DD-304
@pytest.mark.boundary
def test_load_capiss_public_key_handles_file_states(jiratool_module, monkeypatch, tmp_path, guard):
    _premise_module_loaded(guard, jiratool_module)
    monkeypatch.setattr(jiratool_module, "_capiss_public_key", None)

    missing_path = tmp_path / "missing.b64"
    guard.exercise("point key loader at missing file", lambda: monkeypatch.setattr(jiratool_module, "CAPISS_PUBLIC_KEY_PATH", str(missing_path)))
    missing = guard.exercise("load missing key", jiratool_module.load_capiss_public_key)

    empty_path = tmp_path / "empty.b64"
    guard.exercise("create empty key file", lambda: empty_path.write_text(""))
    guard.exercise("point key loader at empty file", lambda: monkeypatch.setattr(jiratool_module, "CAPISS_PUBLIC_KEY_PATH", str(empty_path)))
    empty = guard.exercise("load empty key", jiratool_module.load_capiss_public_key)

    valid_path = tmp_path / "valid.b64"
    guard.exercise("create valid key file", lambda: valid_path.write_text(base64.b64encode(b"public-key").decode("ascii")))
    parsed_key = object()
    parser_calls: list[tuple[bytes, object]] = []
    guard.exercise(
        "stub public key parser",
        lambda: monkeypatch.setattr(
            jiratool_module.PublicKey,
            "from_bytes",
            lambda raw, algorithm: parser_calls.append((raw, algorithm)) or parsed_key,
        ),
    )
    guard.exercise("point key loader at valid file", lambda: monkeypatch.setattr(jiratool_module, "CAPISS_PUBLIC_KEY_PATH", str(valid_path)))
    valid = guard.exercise("load valid key", jiratool_module.load_capiss_public_key)
    cached = guard.exercise("load cached key", jiratool_module.load_capiss_public_key)

    guard.outcome("missing key returns none", missing is None)
    guard.outcome("empty key returns none", empty is None)
    guard.outcome("valid key parsed", valid is parsed_key)
    guard.outcome("cached key reused", cached is parsed_key)
    guard.outcome("parser called once with decoded key", parser_calls == [(b"public-key", jiratool_module.Algorithm.Ed25519)])


# UT: UT-173
# Test Description: Verifies jira-tool Redis budget/rate enforcement maps store outcomes to stable decisions.
# Precondition: Redis eval and time are controlled by the test.
# Expected Output: Allow, rate limit, budget exhaustion, malformed replies, and Redis errors produce exact reason codes.
# Covers DD: DD-308
@pytest.mark.invariant
def test_consume_budget_and_rate_maps_redis_outcomes(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    guard.exercise("freeze time", lambda: monkeypatch.setattr(jiratool_module.time, "time", lambda: 1000))

    calls = []

    class FakeRedis:
        def __init__(self, result=None, fail=False):
            self.result = result
            self.fail = fail

        def eval(self, *args):
            calls.append(args)
            if self.fail:
                raise jiratool_module.redis.RedisError("down")
            return self.result

    def run_with(result=None, fail=False):
        monkeypatch.setattr(jiratool_module, "get_redis", lambda: FakeRedis(result, fail))
        return jiratool_module.consume_budget_and_rate("root-1", 1015)

    allowed = guard.exercise("consume allowed budget", lambda: run_with([1, "ok", 9]))
    rate_limited = guard.exercise("consume rate-limited budget", lambda: run_with([0, "rate_limited", 7]))
    exhausted = guard.exercise("consume exhausted budget", lambda: run_with([0, "budget_exceeded", 0]))
    malformed = guard.exercise("consume malformed store reply", lambda: run_with(["bad"]))
    unavailable = guard.exercise("consume with Redis error", lambda: run_with(fail=True))

    guard.outcome("allow maps to ok", allowed == (True, "ok", 9))
    guard.outcome("rate limit maps exactly", rate_limited == (False, "rate_limited", 7))
    guard.outcome("budget exhausted maps exactly", exhausted == (False, "budget_exceeded", 0))
    guard.outcome("malformed store reply fails closed", malformed == (False, "store_unavailable", -1))
    guard.outcome("Redis error fails closed", unavailable == (False, "store_unavailable", -1))
    guard.outcome("Redis keys and ttl are derived from root and exp", calls[0][0:6] == (jiratool_module.CONSUME_BUDGET_RATE_LUA, 2, "m4:budget:root-1", "m4:rate:root-1", "1", "20"))
    guard.outcome("budget ttl is bounded by expiry", calls[0][-1] == "15")


# UT: UT-174
# Test Description: Verifies jira-tool upstream URL and call helpers isolate live configuration and normalize upstream errors.
# Precondition: upstream mode, credentials, and urlopen behavior are controlled by the test.
# Expected Output: Mock/live URLs are built correctly, missing live config fails closed, and HTTP/transport errors are normalized.
# Covers DD: DD-310, DD-312
@pytest.mark.boundary
def test_upstream_url_and_call_helpers(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    guard.exercise("set mock upstream", lambda: monkeypatch.setattr(jiratool_module, "JIRA_UPSTREAM_MODE", "mock"))
    guard.exercise("set mock base url", lambda: monkeypatch.setattr(jiratool_module, "JIRA_MOCK_BASE_URL", "http://jira-mock:8080/"))
    mock_url = guard.exercise("build mock upstream issue url", lambda: jiratool_module.upstream_issue_url("IAM-1"))

    guard.exercise("switch to incomplete live mode", lambda: monkeypatch.setattr(jiratool_module, "JIRA_UPSTREAM_MODE", "live"))
    guard.exercise("clear live base url", lambda: monkeypatch.setattr(jiratool_module, "JIRA_BASE_URL", ""))
    live_error = guard.exercise(
        "build incomplete live upstream issue url",
        lambda: pytest.raises(jiratool_module.UpstreamConfigError, jiratool_module.upstream_issue_url, "IAM-1"),
    )

    guard.exercise("set live base url", lambda: monkeypatch.setattr(jiratool_module, "JIRA_BASE_URL", "https://example.atlassian.net/"))
    guard.exercise("set live email", lambda: monkeypatch.setattr(jiratool_module, "JIRA_EMAIL", "bot@example.org"))
    guard.exercise("set live token", lambda: monkeypatch.setattr(jiratool_module, "JIRA_API_TOKEN", "secret"))
    live_url = guard.exercise("build live upstream issue url", lambda: jiratool_module.upstream_issue_url("IAM-1"))

    class Response:
        status = 200
        headers = {"Content-Type": "application/json"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b'{"ok":true}'

    guard.exercise("stub upstream URL builder", lambda: monkeypatch.setattr(jiratool_module, "upstream_issue_url", lambda issue: f"http://upstream/{issue}"))
    guard.exercise("stub upstream headers", lambda: monkeypatch.setattr(jiratool_module, "upstream_headers", lambda: {"Accept": "application/json"}))
    ok_call = guard.exercise("call successful upstream", lambda: monkeypatch.setattr(jiratool_module.request, "urlopen", lambda *_args, **_kwargs: Response()) or jiratool_module.call_upstream_issue("IAM-1"))

    http_error = error.HTTPError("http://upstream/IAM-1", 404, "not found", {"Content-Type": "application/json"}, io.BytesIO(b'{"error":"missing"}'))
    http_call = guard.exercise("call HTTP-error upstream", lambda: monkeypatch.setattr(jiratool_module.request, "urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(http_error)) or jiratool_module.call_upstream_issue("IAM-1"))
    transport_call = guard.exercise("call unavailable upstream", lambda: monkeypatch.setattr(jiratool_module.request, "urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(error.URLError("down"))) or jiratool_module.call_upstream_issue("IAM-1"))

    guard.outcome("mock URL uses mock base", mock_url == "http://jira-mock:8080/rest/api/3/issue/IAM-1")
    guard.outcome("incomplete live config raises", live_error.type is jiratool_module.UpstreamConfigError)
    guard.outcome("live URL uses live base", live_url == "https://example.atlassian.net/rest/api/3/issue/IAM-1")
    guard.outcome("successful upstream body returned", ok_call == (200, b'{"ok":true}', "application/json"))
    guard.outcome("HTTPError passes through status and body", http_call == (404, b'{"error":"missing"}', "application/json"))
    guard.outcome("transport error becomes 502", transport_call[0] == 502 and b"upstream_unavailable" in transport_call[1])


# UT: UT-180
# Test Description: Verifies jira-tool validates description update bodies and encodes plain text as Jira ADF.
# Precondition: jira-tool module is loaded and candidate PUT bodies include valid, malformed, and overbroad shapes.
# Expected Output: Only the single description string body is accepted and converted to a fields.description ADF document.
# Covers DD: DD-321, DD-322
@pytest.mark.boundary
def test_parse_description_update_body_accepts_only_plain_description(jiratool_module, guard):
    _premise_module_loaded(guard, jiratool_module)
    valid, valid_reason = guard.exercise(
        "parse valid description update",
        lambda: jiratool_module.parse_description_update_body(b'{"description":"line one\\nline two"}'),
    )
    malformed = guard.exercise("parse invalid json", lambda: jiratool_module.parse_description_update_body(b"{"))
    non_string = guard.exercise("parse non-string description", lambda: jiratool_module.parse_description_update_body(b'{"description":{}}'))
    extra = guard.exercise("parse body with extra field", lambda: jiratool_module.parse_description_update_body(b'{"description":"ok","summary":"bad"}'))

    guard.outcome("valid body has no deny reason", valid_reason == "")
    guard.outcome("valid body encodes fields description", valid["fields"]["description"]["type"] == "doc")
    guard.outcome("valid body preserves text lines", valid["fields"]["description"]["content"][1]["content"][0]["text"] == "line two")
    guard.outcome("malformed json rejected", malformed == (None, "malformed_body"))
    guard.outcome("non-string description rejected", non_string == (None, "malformed_body"))
    guard.outcome("extra fields rejected", extra == (None, "unsupported_fields"))


# UT: UT-175
# Test Description: Verifies jira-tool request authorization emits exact local deny statuses and returns valid claims on allow.
# Precondition: handler headers and token verification results are controlled by the test.
# Expected Output: Missing identity/token, invalid token, store failure, and allow paths return exact local outcomes.
# Covers DD: DD-317
@pytest.mark.invariant
def test_handler_authorize_status_mapping(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)

    def run(headers, verify_result=None):
        handler = _handler(jiratool_module, headers=headers)
        denials = []
        handler._deny = lambda *args, **kwargs: denials.append((args, kwargs))
        if verify_result is not None:
            monkeypatch.setattr(jiratool_module, "verify_biscuit", lambda *_args: verify_result)
        result = handler._authorize("IAM-1", "IAM")
        return result, denials

    missing_spiffe = guard.exercise("authorize without SPIFFE ID", lambda: run({}))
    missing_token = guard.exercise("authorize without bearer token", lambda: run({"x-spiffe-id": "spiffe://example.org/agent-a"}))
    empty_token = guard.exercise("authorize with empty bearer token", lambda: run({"x-spiffe-id": "spiffe://example.org/agent-a", "Authorization": "Bearer "}))
    invalid = guard.exercise("authorize invalid token", lambda: run({"x-spiffe-id": "spiffe://example.org/agent-a", "Authorization": "Bearer bad"}, (False, "invalid_token", None)))
    store_down = guard.exercise("authorize store failure", lambda: run({"x-spiffe-id": "spiffe://example.org/agent-a", "Authorization": "Bearer good"}, (False, "store_unavailable", _claims())))
    allowed = guard.exercise("authorize valid token", lambda: run({"x-spiffe-id": "spiffe://example.org/agent-a", "Authorization": "Bearer good"}, (True, "", _claims())))

    guard.outcome("missing SPIFFE ID is 401", missing_spiffe[1][0][0][0:2] == (401, "missing_spiffe_id"))
    guard.outcome("missing token is 401", missing_token[1][0][0][0:2] == (401, "missing_token"))
    guard.outcome("empty bearer token is 401", empty_token[1][0][0][0:2] == (401, "missing_token"))
    guard.outcome("invalid token is 401", invalid[1][0][0][0:2] == (401, "invalid_token"))
    guard.outcome("store unavailable is 503", store_down[1][0][0][0:2] == (503, "store_unavailable"))
    guard.outcome("valid token returns auth tuple", allowed[0][0] == "spiffe://example.org/agent-a" and allowed[0][1]["token_id"] == "token-root")


# UT: UT-176
# Test Description: Verifies jira-tool GET dispatch handles health, unsupported paths, local deny, upstream mismatch, upstream allow, and upstream errors.
# Precondition: handler authorization, upstream call, project verification, and send methods are controlled by the test.
# Expected Output: The dispatcher returns exact response paths and never returns mismatched successful upstream bodies.
# Covers DD: DD-318, DD-313
@pytest.mark.hybrid_critical
def test_handler_get_dispatch_paths(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    guard.exercise("silence audit logger", lambda: monkeypatch.setattr(jiratool_module, "log_event", lambda *_args, **_kwargs: None))

    def run(path, *, auth=("spiffe://example.org/agent-a", _claims(token_project="IAM")), upstream=(200, b'{"fields":{"project":{"key":"IAM"}}}', "application/json")):
        handler = _handler(jiratool_module, path=path)
        sent = []
        denials = []
        handler._send_json = lambda status, payload: sent.append(("json", status, payload))
        handler._send_bytes = lambda status, body, content_type="application/json": sent.append(("bytes", status, body, content_type))
        handler._deny = lambda *args, **kwargs: denials.append((args, kwargs))
        handler._authorize = lambda *_args: auth
        if isinstance(upstream, BaseException):
            monkeypatch.setattr(jiratool_module, "call_upstream_issue", lambda _issue: (_ for _ in ()).throw(upstream))
        else:
            monkeypatch.setattr(jiratool_module, "call_upstream_issue", lambda _issue: upstream)
        jiratool_module.JiraToolHandler.do_GET(handler)
        return sent, denials

    health = guard.exercise("dispatch health", lambda: run("/health"))
    unsupported = guard.exercise("dispatch unsupported path", lambda: run("/jira/rest/api/3/search"))
    auth_denied = guard.exercise("dispatch local auth denial", lambda: run("/jira/rest/api/3/issue/IAM-1", auth=None))
    config_error = guard.exercise(
        "dispatch upstream config error",
        lambda: run("/jira/rest/api/3/issue/IAM-1", upstream=jiratool_module.UpstreamConfigError("bad")),
    )
    mismatch = guard.exercise("dispatch upstream project mismatch", lambda: run("/jira/rest/api/3/issue/IAM-999", upstream=(200, b'{"fields":{"project":{"key":"NAS"}}}', "application/json")))
    allow = guard.exercise("dispatch upstream allow", lambda: run("/jira/rest/api/3/issue/IAM-1"))
    upstream_error = guard.exercise("dispatch upstream error passthrough", lambda: run("/jira/rest/api/3/issue/IAM-404", upstream=(404, b'{"error":"missing"}', "application/json")))

    guard.outcome("health returns ok json", health[0] == [("json", 200, {"status": "ok"})])
    guard.outcome("unsupported path returns 404", unsupported[0][0][0:2] == ("json", 404))
    guard.outcome("auth denial stops before response send", auth_denied == ([], []))
    guard.outcome("config error denies before upstream", config_error[1][0][0][0:2] == (503, "upstream_config"))
    guard.outcome("mismatched upstream success denied", mismatch[1][0][0][0:2] == (403, "upstream_project_mismatch"))
    guard.outcome("allowed upstream body returned", allow[0][0][0:3] == ("bytes", 200, b'{"fields":{"project":{"key":"IAM"}}}'))
    guard.outcome("authorized upstream error passes through", upstream_error[0][0][0:3] == ("bytes", 404, b'{"error":"missing"}'))


# UT: UT-181
# Test Description: Verifies jira-tool PUT dispatch requires write authority, validates body, forwards description update, and returns 204.
# Precondition: handler authorization, body parsing, upstream call, and send methods are controlled by the test.
# Expected Output: The dispatcher passes the write-only action set to authorization, rejects malformed bodies before upstream, and returns no-content on upstream 204.
# Covers DD: DD-317, DD-322, DD-323
@pytest.mark.hybrid_critical
def test_handler_put_dispatch_paths(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    guard.exercise("silence audit logger", lambda: monkeypatch.setattr(jiratool_module, "log_event", lambda *_args, **_kwargs: None))

    def run(body, *, auth=("spiffe://example.org/agent-a", _claims(token_project="IAM", act="write")), upstream=(204, b"", "application/json")):
        handler = _handler(
            jiratool_module,
            path="/jira/rest/api/3/issue/IAM-1",
            headers={"Content-Length": str(len(body))},
        )
        handler.rfile = io.BytesIO(body)
        sent = []
        denials = []
        authorize_calls = []
        upstream_calls = []
        handler._send_json = lambda status, payload: sent.append(("json", status, payload))
        handler._send_bytes = lambda status, response_body, content_type="application/json": sent.append(("bytes", status, response_body, content_type))
        handler._deny = lambda *args, **kwargs: denials.append((args, kwargs))

        def fake_authorize(issue_key, project, allowed_actions=None, jira_operation="issue_read"):
            authorize_calls.append((issue_key, project, allowed_actions, jira_operation))
            return auth

        handler._authorize = fake_authorize

        def fake_upstream(issue_key, **kwargs):
            upstream_calls.append((issue_key, kwargs))
            return upstream

        monkeypatch.setattr(jiratool_module, "call_upstream_issue", fake_upstream)
        jiratool_module.JiraToolHandler.do_PUT(handler)
        return sent, denials, authorize_calls, upstream_calls

    allow = guard.exercise("dispatch allowed description update", lambda: run(b'{"description":"marker"}'))
    malformed = guard.exercise("dispatch malformed description update", lambda: run(b"{"))
    extra = guard.exercise("dispatch overbroad description update", lambda: run(b'{"description":"marker","summary":"bad"}'))
    auth_denied = guard.exercise("dispatch authorization denial", lambda: run(b'{"description":"marker"}', auth=None))
    upstream_error = guard.exercise("dispatch upstream error passthrough", lambda: run(b'{"description":"marker"}', upstream=(404, b'{"error":"missing"}', "application/json")))

    guard.outcome("PUT authorization asks for write only", allow[2] == [("IAM-1", "IAM", {"write"}, "issue_description_write")])
    guard.outcome("allowed PUT returns 204 with empty body", allow[0] == [("bytes", 204, b"", "application/json")])
    guard.outcome("upstream receives PUT and encoded body", allow[3][0][1]["method"] == "PUT" and b'"fields"' in allow[3][0][1]["body"])
    guard.outcome("malformed body denied before upstream", malformed[1][0][0][0:2] == (400, "malformed_body") and malformed[3] == [])
    guard.outcome("extra fields denied before upstream", extra[1][0][0][0:2] == (400, "unsupported_fields") and extra[3] == [])
    guard.outcome("auth denial stops before response send", auth_denied == ([], [], [("IAM-1", "IAM", {"write"}, "issue_description_write")], []))
    guard.outcome("authorized upstream error passes through", upstream_error[0][0][0:3] == ("bytes", 404, b'{"error":"missing"}'))


# UT: UT-177
# Test Description: Verifies jira-tool standardized deny and unsupported-method handlers emit audit-safe local responses.
# Precondition: send and audit methods are controlled by the test.
# Expected Output: Deny emits a structured decision without bearer material and non-GET methods map to 405.
# Covers DD: DD-316, DD-319
@pytest.mark.negative_control
def test_handler_deny_and_unsupported_methods(jiratool_module, monkeypatch, guard):
    _premise_module_loaded(guard, jiratool_module)
    events = []
    guard.exercise("capture audit events", lambda: monkeypatch.setattr(jiratool_module, "log_event", lambda event_type, **fields: events.append((event_type, fields))))

    handler = _handler(jiratool_module, headers={"x-spiffe-id": "spiffe://example.org/agent-a"})
    sent = []
    handler._send_json = lambda status, payload: sent.append((status, payload))
    guard.exercise(
        "deny protected request",
        lambda: jiratool_module.JiraToolHandler._deny(
            handler,
            403,
            "project_mismatch",
            "spiffe://example.org/agent-a",
            _claims(token_project="IAM"),
            issue_key="NAS-1",
            requested_project="NAS",
        ),
    )

    method_denials = []
    method_handler = _handler(jiratool_module, headers={"x-spiffe-id": "spiffe://example.org/agent-a"})
    method_handler._deny = lambda *args, **kwargs: method_denials.append((args, kwargs))
    for method_name in ("do_POST", "do_PATCH", "do_DELETE"):
        guard.exercise(f"deny unsupported {method_name}", lambda method_name=method_name: getattr(jiratool_module.JiraToolHandler, method_name)(method_handler))

    guard.outcome("deny response is standardized", sent == [(403, {"error": "denied", "reason": "project_mismatch"})])
    guard.outcome("deny audit event contains decision fields", events[0][0] == "jiratool_enforcement_decision" and events[0][1]["reason_code"] == "project_mismatch")
    guard.outcome("deny audit event omits bearer material", "token" not in events[0][1])
    guard.outcome("all unsupported methods deny with 405", [call[0][0:2] for call in method_denials] == [(405, "method_not_allowed")] * 3)
