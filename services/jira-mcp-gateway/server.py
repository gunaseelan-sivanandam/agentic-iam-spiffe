import base64
import json
import os
import re
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import error, request
from urllib.parse import quote, urlencode

import redis
from biscuit_auth import (
    Algorithm,
    Biscuit,
    BiscuitBlockError,
    BiscuitSerializationError,
    BiscuitValidationError,
    PublicKey,
)
from shared.enforcement_contract import verify_chain_contract


SPIFFE_HEADER = "x-spiffe-id"
REQUIRED_AUD = "jira-mcp-gateway"
SUMMARY_ACT = "read_project_summary"
CREATE_ACT = "create_story"
RESOURCE_PREFIX = "jira-mcp:/project:"
PROJECT_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")
ISSUE_KEY_RE = re.compile(r"^([A-Z][A-Z0-9]{1,9})-[1-9][0-9]*$")
MAX_BODY_BYTES = 65536
MAX_TEXT = 4096
MAX_AC_ITEMS = 20

CAPISS_PUBLIC_KEY_PATH = os.getenv(
    "CAPISS_PUBLIC_KEY_PATH", "/var/lib/capiss/keys/root_public_key.b64"
)
M4_MAX_DEPTH = int(os.getenv("M4_MAX_DEPTH", "3"))
M4_RATE_LIMIT = int(os.getenv("M4_RATE_LIMIT", "20"))
M4_RATE_WINDOW_SECONDS = int(os.getenv("M4_RATE_WINDOW_SECONDS", "10"))
M4_REQUEST_COST = int(os.getenv("M4_REQUEST_COST", "1"))
M4_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
M4_REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "0.5"))
JIRA_MCP_UPSTREAM_MODE = os.getenv("JIRA_MCP_UPSTREAM_MODE", "mock")
JIRA_MCP_MOCK_BASE_URL = os.getenv("JIRA_MCP_MOCK_BASE_URL", "http://jira-mcp-mock:8080")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
UPSTREAM_TIMEOUT_SECONDS = float(os.getenv("JIRA_UPSTREAM_TIMEOUT_SECONDS", "3.0"))

CONSUME_BUDGET_RATE_LUA = """
local budget_key = KEYS[1]
local rate_key = KEYS[2]
local request_cost = tonumber(ARGV[1])
local rate_limit = tonumber(ARGV[2])
local rate_window = tonumber(ARGV[3])
local budget_ttl = tonumber(ARGV[4])

local budget = redis.call('GET', budget_key)
if not budget then
  return {0, 'missing_budget', -1}
end

local budget_num = tonumber(budget)
if budget_num == nil then
  return {0, 'invalid_budget', -1}
end

local new_rate = redis.call('INCR', rate_key)
if new_rate == 1 then
  redis.call('EXPIRE', rate_key, rate_window)
end
if new_rate > rate_limit then
  return {0, 'rate_limited', budget_num}
end

if budget_num < request_cost then
  return {0, 'budget_exhausted', budget_num}
end

local remaining = redis.call('DECRBY', budget_key, request_cost)
if redis.call('TTL', budget_key) < 0 then
  redis.call('EXPIRE', budget_key, budget_ttl)
end
return {1, 'ok', remaining}
"""

_redis_client: redis.Redis | None = None
_capiss_public_key: PublicKey | None = None


class UpstreamConfigError(Exception):
    pass


# DD: DD-501
# Implements: ARCH-030
# Title: iso_utc_now jira-mcp-gateway audit timestamp helper
def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# DD: DD-502
# Implements: ARCH-030
# Title: log_event jira-mcp-gateway structured audit logger
def log_event(event_type: str, **fields: object) -> None:
    payload = {"event_type": event_type, "timestamp": iso_utc_now(), **fields}
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True), flush=True)


# DD: DD-503
# Implements: ARCH-030
# Title: project_from_resource jira-mcp-gateway token resource parser
def project_from_resource(res: str) -> str | None:
    if not res.startswith(RESOURCE_PREFIX):
        return None
    project_key = res.removeprefix(RESOURCE_PREFIX)
    if not PROJECT_KEY_RE.fullmatch(project_key):
        return None
    return project_key


# DD: DD-504
# Implements: ARCH-030
# Title: load_capiss_public_key jira-mcp-gateway issuer key loader
def load_capiss_public_key() -> PublicKey | None:
    global _capiss_public_key
    if _capiss_public_key is not None:
        return _capiss_public_key
    if not os.path.exists(CAPISS_PUBLIC_KEY_PATH):
        return None
    with open(CAPISS_PUBLIC_KEY_PATH, "rb") as handle:
        raw = handle.read().strip()
    if not raw:
        return None
    _capiss_public_key = PublicKey.from_bytes(base64.b64decode(raw), Algorithm.Ed25519)
    return _capiss_public_key


# DD: DD-505
# Implements: ARCH-030
# Title: verify_chain_and_claims jira-mcp-gateway shared chain contract adapter
def verify_chain_and_claims(biscuit: Biscuit) -> tuple[dict[str, str | int] | None, str]:
    claims, err = verify_chain_contract(biscuit, max_depth=M4_MAX_DEPTH)
    if claims is None:
        return None, err or "token_invalid"
    if int(claims.get("effective_depth", 0)) != 0:
        return None, "token_invalid"
    return claims, ""


# DD: DD-506
# Implements: ARCH-030
# Title: verify_token jira-mcp-gateway endpoint-bound token verifier
def verify_token(
    token_value: str,
    spiffe_id: str,
    expected_act: str,
    requested_project: str,
) -> tuple[bool, str, dict[str, str | int] | None]:
    public_key = load_capiss_public_key()
    if public_key is None:
        return False, "token_invalid", None
    try:
        biscuit = Biscuit.from_base64(token_value, public_key)
    except (BiscuitSerializationError, BiscuitValidationError, BiscuitBlockError, Exception):
        return False, "token_invalid", None
    claims, chain_err = verify_chain_and_claims(biscuit)
    if claims is None:
        return False, "token_invalid", None

    subject = str(claims.get("subject_spiffe_id", ""))
    aud = str(claims.get("aud", ""))
    act = str(claims.get("act", ""))
    res = str(claims.get("res", ""))
    exp = int(claims.get("exp", 0))
    token_project = project_from_resource(res)
    if token_project:
        claims["token_project"] = token_project

    if subject != spiffe_id:
        return False, "subject_mismatch", claims
    if aud != REQUIRED_AUD:
        return False, "aud_mismatch", claims
    if act != expected_act:
        return False, "act_mismatch", claims
    if token_project is None:
        return False, "project_mismatch", claims
    if token_project != requested_project:
        return False, "project_mismatch", claims
    if exp <= int(time.time()):
        return False, "token_invalid", claims
    return True, "", claims


# DD: DD-507
# Implements: ARCH-030
# Title: consume_budget_and_rate jira-mcp-gateway shared-state governance
def consume_budget_and_rate(root_token_id: str, exp: int) -> tuple[bool, str, int]:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            M4_REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=M4_REDIS_SOCKET_TIMEOUT,
        )
    ttl = max(1, exp - int(time.time()))
    try:
        result = _redis_client.eval(
            CONSUME_BUDGET_RATE_LUA,
            2,
            f"m4:budget:{root_token_id}",
            f"m4:rate:{root_token_id}",
            str(M4_REQUEST_COST),
            str(M4_RATE_LIMIT),
            str(M4_RATE_WINDOW_SECONDS),
            str(ttl),
        )
    except redis.RedisError:
        return False, "gateway_unavailable", -1
    if not isinstance(result, (list, tuple)) or len(result) < 3:
        return False, "gateway_unavailable", -1
    allowed = int(result[0]) == 1
    reason = str(result[1])
    remaining = int(result[2])
    if allowed:
        return True, "ok", remaining
    if reason == "rate_limited":
        return False, "rate_limited", remaining
    if reason in {"missing_budget", "invalid_budget", "budget_exhausted"}:
        return False, "budget_exhausted", remaining
    return False, "gateway_unavailable", remaining


# DD: DD-508
# Implements: ARCH-030
# Title: validate_summary_payload jira-mcp-gateway summary input guard
def validate_summary_payload(payload: object) -> tuple[str | None, str | None]:
    if not isinstance(payload, dict) or set(payload) != {"project_key"}:
        return None, "payload_invalid"
    project_key = payload.get("project_key")
    if not isinstance(project_key, str) or not PROJECT_KEY_RE.fullmatch(project_key):
        return None, "payload_invalid"
    return project_key, None


# DD: DD-509
# Implements: ARCH-030
# Title: validate_create_payload jira-mcp-gateway story input guard
def validate_create_payload(payload: object) -> tuple[dict[str, object] | None, str | None]:
    allowed = {"project_key", "summary", "description", "acceptance_criteria", "epic_key"}
    if not isinstance(payload, dict) or not {"project_key", "summary", "description"}.issubset(payload):
        return None, "payload_invalid"
    if set(payload) - allowed:
        return None, "payload_invalid"
    project_key = payload.get("project_key")
    summary = payload.get("summary")
    description = payload.get("description")
    if not isinstance(project_key, str) or not PROJECT_KEY_RE.fullmatch(project_key):
        return None, "payload_invalid"
    if not isinstance(summary, str) or not summary.strip() or len(summary) > 255:
        return None, "payload_invalid"
    if not isinstance(description, str) or not description.strip() or len(description) > MAX_TEXT:
        return None, "payload_invalid"
    cleaned: dict[str, object] = {
        "project_key": project_key,
        "summary": summary,
        "description": description,
    }
    ac = payload.get("acceptance_criteria")
    if ac is not None:
        if (
            not isinstance(ac, list)
            or len(ac) > MAX_AC_ITEMS
            or any(not isinstance(item, str) or not item.strip() or len(item) > 512 for item in ac)
        ):
            return None, "payload_invalid"
        cleaned["acceptance_criteria"] = ac
    epic_key = payload.get("epic_key")
    if epic_key is not None:
        if not isinstance(epic_key, str) or not ISSUE_KEY_RE.fullmatch(epic_key):
            return None, "epic_invalid"
        cleaned["epic_key"] = epic_key
    return cleaned, None


# DD: DD-510
# Implements: ARCH-030
# Title: adf_from_plain_text jira-mcp-gateway Jira Cloud description encoder
def adf_from_plain_text(description: str, acceptance_criteria: list[str] | None = None) -> dict[str, object]:
    text = description
    if acceptance_criteria:
        text += "\n\nAcceptance Criteria:\n" + "\n".join(f"- {item}" for item in acceptance_criteria)
    content: list[dict[str, object]] = []
    for line in text.splitlines() or [""]:
        paragraph: dict[str, object] = {"type": "paragraph"}
        if line:
            paragraph["content"] = [{"type": "text", "text": line}]
        content.append(paragraph)
    return {"type": "doc", "version": 1, "content": content}


def upstream_base_url() -> str:
    if JIRA_MCP_UPSTREAM_MODE == "live":
        if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
            raise UpstreamConfigError("live Jira configuration is incomplete")
        return JIRA_BASE_URL.rstrip("/")
    return JIRA_MCP_MOCK_BASE_URL.rstrip("/")


def upstream_headers(correlation_id: str) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Correlation-ID": correlation_id,
        "X-M5-Gateway": "jira-mcp-gateway",
    }
    if JIRA_MCP_UPSTREAM_MODE == "live":
        raw = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode("utf-8")
        headers["Authorization"] = "Basic " + base64.b64encode(raw).decode("ascii")
    return headers


# DD: DD-511
# Implements: ARCH-030, ARCH-031
# Title: call_upstream jira-mcp-gateway authorized upstream caller
def call_upstream(path: str, correlation_id: str, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
    req = request.Request(
        f"{upstream_base_url()}{path}",
        headers=upstream_headers(correlation_id),
        data=data,
        method=method,
    )
    try:
        with request.urlopen(req, timeout=UPSTREAM_TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return resp.status, json.loads(raw)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8") or "{}"
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"error": "upstream_error"}
    except (error.URLError, TimeoutError):
        return 502, {"error": "upstream_unavailable"}


def live_project_summary(project_key: str, correlation_id: str) -> tuple[int, dict]:
    project_status, project_payload = call_upstream(
        f"/rest/api/3/project/{quote(project_key)}",
        correlation_id,
    )
    if project_status != 200:
        return project_status, project_payload
    query = urlencode(
        {
            "jql": f"project = {project_key} ORDER BY updated DESC",
            "maxResults": "75",
            "fields": "summary,status,issuetype,parent",
        }
    )
    search_status, search_payload = call_upstream(
        f"/rest/api/3/search/jql?{query}",
        correlation_id,
    )
    if search_status != 200:
        return search_status, search_payload
    issues: list[dict[str, object]] = []
    raw_issues = search_payload.get("issues") if isinstance(search_payload, dict) else []
    if not isinstance(raw_issues, list):
        raw_issues = []
    for item in raw_issues:
        if not isinstance(item, dict):
            continue
        fields = item.get("fields")
        if not isinstance(fields, dict):
            fields = {}
        issue_type = fields.get("issuetype")
        status = fields.get("status")
        parent = fields.get("parent")
        issue: dict[str, object] = {
            "key": item.get("key"),
            "summary": fields.get("summary"),
            "status": status.get("name") if isinstance(status, dict) else None,
            "issue_type": issue_type.get("name") if isinstance(issue_type, dict) else None,
        }
        if isinstance(parent, dict) and isinstance(parent.get("key"), str):
            issue["epic_key"] = parent.get("key")
        issues.append(issue)
    return 200, {
        "project": {
            "key": project_payload.get("key"),
            "name": project_payload.get("name"),
            "issue_count": int(search_payload.get("total", len(issues)))
            if isinstance(search_payload, dict)
            else len(issues),
        },
        "issues": issues,
    }


# DD: DD-512
# Implements: ARCH-030, ARCH-031
# Title: shape_project_summary jira-mcp-gateway bounded summary shaper
def shape_project_summary(payload: dict) -> dict[str, object]:
    project = payload.get("project") if isinstance(payload, dict) else {}
    issues = payload.get("issues") if isinstance(payload, dict) else []
    if not isinstance(project, dict):
        project = {}
    if not isinstance(issues, list):
        issues = []
    non_epics: list[dict[str, object]] = []
    epics: list[dict[str, object]] = []
    for item in issues:
        if not isinstance(item, dict):
            continue
        issue_type = str(item.get("issue_type", ""))
        shaped = {
            "key": item.get("key"),
            "summary": item.get("summary"),
            "status": item.get("status"),
            "issue_type": issue_type,
        }
        if item.get("epic_key"):
            shaped["epic_key"] = item.get("epic_key")
        if issue_type == "Epic":
            epics.append({k: shaped[k] for k in ("key", "summary", "status")})
        else:
            non_epics.append(shaped)
    return {
        "project": {
            "key": project.get("key"),
            "name": project.get("name"),
            "issue_count": int(project.get("issue_count", len(issues))),
        },
        "issues": non_epics[:50],
        "epics": epics[:25],
    }


# DD: DD-513
# Implements: ARCH-030, ARCH-031
# Title: verify_epic jira-mcp-gateway same-project epic verifier
def verify_epic(epic_key: str, project_key: str, correlation_id: str) -> bool:
    match = ISSUE_KEY_RE.fullmatch(epic_key)
    if not match or match.group(1) != project_key:
        return False
    status, payload = call_upstream(f"/rest/api/3/issue/{quote(epic_key)}", correlation_id)
    if status != 200:
        return False
    fields = payload.get("fields") if isinstance(payload, dict) else None
    if not isinstance(fields, dict):
        return False
    project = fields.get("project")
    issue_type = fields.get("issuetype")
    return (
        isinstance(project, dict)
        and project.get("key") == project_key
        and isinstance(issue_type, dict)
        and issue_type.get("name") == "Epic"
    )


def _event_fields(
    *,
    subject_spiffe_id: str | None,
    claims: dict | None,
    project_key: str | None,
    endpoint: str,
    decision: str,
    reason: str,
    upstream_called: bool,
    correlation_id: str,
    upstream_operation: str | None = None,
    upstream_status: int | None = None,
    issue_key: str | None = None,
    epic_key: str | None = None,
) -> dict[str, object]:
    fields: dict[str, object] = {
        "subject_spiffe_id": subject_spiffe_id,
        "project_key": project_key,
        "endpoint": endpoint,
        "decision": decision,
        "reason_code": reason,
        "upstream_called": upstream_called,
        "upstream_operation": upstream_operation,
        "upstream_status": upstream_status,
        "issue_key": issue_key,
        "epic_key": epic_key,
        "correlation_id": correlation_id,
    }
    if claims:
        fields.update(
            {
                "aud": claims.get("aud"),
                "act": claims.get("act"),
                "res": claims.get("res"),
                "root_token_id": claims.get("root_token_id"),
                "token_id": claims.get("token_id"),
                "token_project": claims.get("token_project"),
                "budget_remaining": claims.get("budget_remaining"),
            }
        )
    return {key: value for key, value in fields.items() if value is not None}


class JiraMcpGatewayHandler(BaseHTTPRequestHandler):
    server_version = "jira-mcp-gateway"

    # DD: DD-514
    # Implements: ARCH-030
    # Title: JiraMcpGatewayHandler.log_message access log adapter
    def log_message(self, fmt, *args):
        return

    def _send_json(self, status: int, payload: dict[str, object]):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _correlation_id(self) -> str:
        value = self.headers.get("X-Correlation-ID", "").strip()
        return value if value else f"gateway-{int(time.time() * 1000)}"

    def _read_json(self) -> tuple[object | None, str | None]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None, "payload_invalid"
        if length < 0 or length > MAX_BODY_BYTES:
            return None, "payload_invalid"
        try:
            return json.loads(self.rfile.read(length).decode("utf-8")), None
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None, "payload_invalid"

    def _deny(
        self,
        status: int,
        reason: str,
        *,
        spiffe_id: str | None,
        claims: dict | None,
        project_key: str | None,
        endpoint: str,
        correlation_id: str,
        upstream_called: bool = False,
        upstream_operation: str | None = None,
        upstream_status: int | None = None,
        epic_key: str | None = None,
    ):
        log_event(
            "jiramcp_gateway_decision",
            **_event_fields(
                subject_spiffe_id=spiffe_id,
                claims=claims,
                project_key=project_key,
                endpoint=endpoint,
                decision="deny",
                reason=reason,
                upstream_called=upstream_called,
                upstream_operation=upstream_operation,
                upstream_status=upstream_status,
                correlation_id=correlation_id,
                epic_key=epic_key,
            ),
        )
        self._send_json(status, {"ok": False, "reason": reason, "correlation_id": correlation_id})

    def _authorize(self, expected_act: str, project_key: str, endpoint: str, correlation_id: str):
        spiffe_id = self.headers.get(SPIFFE_HEADER)
        if not spiffe_id:
            self._deny(401, "subject_mismatch", spiffe_id=None, claims=None, project_key=project_key, endpoint=endpoint, correlation_id=correlation_id)
            return None
        authz = self.headers.get("Authorization")
        if not authz or not authz.startswith("Bearer "):
            self._deny(401, "token_invalid", spiffe_id=spiffe_id, claims=None, project_key=project_key, endpoint=endpoint, correlation_id=correlation_id)
            return None
        token_value = authz.split(" ", 1)[1].strip()
        allowed, reason, claims = verify_token(token_value, spiffe_id, expected_act, project_key)
        if not allowed:
            status = 401 if reason == "token_invalid" else 403
            self._deny(status, reason, spiffe_id=spiffe_id, claims=claims, project_key=project_key, endpoint=endpoint, correlation_id=correlation_id)
            return None
        return spiffe_id, claims

    def _consume_or_deny(self, claims: dict, spiffe_id: str, project_key: str, endpoint: str, correlation_id: str) -> bool:
        ok, reason, remaining = consume_budget_and_rate(str(claims["root_token_id"]), int(claims["exp"]))
        claims["budget_remaining"] = remaining
        if ok:
            return True
        status = 429 if reason == "rate_limited" else 403
        if reason == "gateway_unavailable":
            status = 503
        self._deny(status, reason, spiffe_id=spiffe_id, claims=claims, project_key=project_key, endpoint=endpoint, correlation_id=correlation_id)
        return False

    # DD: DD-515
    # Implements: ARCH-030, ARCH-031
    # Title: JiraMcpGatewayHandler.do_POST protected endpoint dispatcher
    def do_POST(self):
        if self.path not in {"/mcp/jira/project-summary", "/mcp/jira/stories"}:
            self._send_json(404, {"detail": "not found"})
            return
        correlation_id = self._correlation_id()
        payload, payload_err = self._read_json()
        if payload_err:
            self._deny(400, payload_err, spiffe_id=self.headers.get(SPIFFE_HEADER), claims=None, project_key=None, endpoint=self.path, correlation_id=correlation_id)
            return

        if self.path == "/mcp/jira/project-summary":
            project_key, err = validate_summary_payload(payload)
            if err or project_key is None:
                self._deny(400, "payload_invalid", spiffe_id=self.headers.get(SPIFFE_HEADER), claims=None, project_key=None, endpoint=self.path, correlation_id=correlation_id)
                return
            auth = self._authorize(SUMMARY_ACT, project_key, self.path, correlation_id)
            if auth is None:
                return
            spiffe_id, claims = auth
            if not self._consume_or_deny(claims, spiffe_id, project_key, self.path, correlation_id):
                return
            if JIRA_MCP_UPSTREAM_MODE == "live":
                status, upstream_payload = live_project_summary(project_key, correlation_id)
            else:
                status, upstream_payload = call_upstream(f"/rest/api/3/project/{quote(project_key)}/summary", correlation_id)
            if status != 200:
                self._deny(502, "upstream_error", spiffe_id=spiffe_id, claims=claims, project_key=project_key, endpoint=self.path, correlation_id=correlation_id, upstream_called=True, upstream_operation="project_summary", upstream_status=status)
                return
            shaped = shape_project_summary(upstream_payload)
            log_event(
                "jiramcp_gateway_decision",
                **_event_fields(
                    subject_spiffe_id=spiffe_id,
                    claims=claims,
                    project_key=project_key,
                    endpoint=self.path,
                    decision="allow",
                    reason="ok",
                    upstream_called=True,
                    upstream_operation="project_summary",
                    upstream_status=status,
                    correlation_id=correlation_id,
                ),
            )
            self._send_json(200, {"ok": True, "correlation_id": correlation_id, **shaped})
            return

        cleaned, err = validate_create_payload(payload)
        if err or cleaned is None:
            self._deny(400, err or "payload_invalid", spiffe_id=self.headers.get(SPIFFE_HEADER), claims=None, project_key=None, endpoint=self.path, correlation_id=correlation_id)
            return
        project_key = str(cleaned["project_key"])
        auth = self._authorize(CREATE_ACT, project_key, self.path, correlation_id)
        if auth is None:
            return
        spiffe_id, claims = auth
        epic_key = cleaned.get("epic_key")
        if isinstance(epic_key, str) and not verify_epic(epic_key, project_key, correlation_id):
            self._deny(400, "epic_invalid", spiffe_id=spiffe_id, claims=claims, project_key=project_key, endpoint=self.path, correlation_id=correlation_id, epic_key=epic_key)
            return
        if not self._consume_or_deny(claims, spiffe_id, project_key, self.path, correlation_id):
            return
        body = {
            "fields": {
                "project": {"key": project_key},
                "summary": cleaned["summary"],
                "description": adf_from_plain_text(
                    str(cleaned["description"]),
                    cleaned.get("acceptance_criteria") if isinstance(cleaned.get("acceptance_criteria"), list) else None,
                ),
                "issuetype": {"name": "Story"},
            }
        }
        if isinstance(epic_key, str):
            body["fields"]["parent"] = {"key": epic_key}
        status, upstream_payload = call_upstream("/rest/api/3/issue", correlation_id, method="POST", body=body)
        if status not in {200, 201}:
            self._deny(502, "upstream_error", spiffe_id=spiffe_id, claims=claims, project_key=project_key, endpoint=self.path, correlation_id=correlation_id, upstream_called=True, upstream_operation="story_create", upstream_status=status, epic_key=epic_key if isinstance(epic_key, str) else None)
            return
        issue_key = str(upstream_payload.get("key", ""))
        response = {
            "ok": True,
            "correlation_id": correlation_id,
            "key": issue_key,
            "self": upstream_payload.get("self", ""),
            "project_key": project_key,
            "issue_type": "Story",
        }
        if isinstance(epic_key, str):
            response["epic_key"] = epic_key
        log_event(
            "jiramcp_gateway_decision",
            **_event_fields(
                subject_spiffe_id=spiffe_id,
                claims=claims,
                project_key=project_key,
                endpoint=self.path,
                decision="allow",
                reason="ok",
                upstream_called=True,
                upstream_operation="story_create",
                upstream_status=status,
                issue_key=issue_key,
                epic_key=epic_key if isinstance(epic_key, str) else None,
                correlation_id=correlation_id,
            ),
        )
        self._send_json(201, response)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"detail": "not found"})


# DD: DD-516
# Implements: ARCH-030
# Title: main jira-mcp-gateway HTTP server bootstrap
def main():
    httpd = HTTPServer(("0.0.0.0", 8080), JiraMcpGatewayHandler)
    print("jira-mcp-gateway listening on http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
