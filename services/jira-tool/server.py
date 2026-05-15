import base64
import json
import os
import re
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import error, request
from urllib.parse import quote, urlsplit

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
CAPISS_PUBLIC_KEY_PATH = os.getenv(
    "CAPISS_PUBLIC_KEY_PATH", "/var/lib/capiss/keys/root_public_key.b64"
)
REQUIRED_AUD = "jira-tool"
READ_ACT = "read"
WRITE_ACT = "write"
JIRA_RESOURCE_PREFIX = "jira-tool:/project:"
JIRA_FACADE_PREFIX = "/jira/rest/api/3/issue/"
MAX_WRITE_BODY_BYTES = 65536
M4_MAX_DEPTH = int(os.getenv("M4_MAX_DEPTH", "3"))
M4_RATE_LIMIT = int(os.getenv("M4_RATE_LIMIT", "20"))
M4_RATE_WINDOW_SECONDS = int(os.getenv("M4_RATE_WINDOW_SECONDS", "10"))
M4_REQUEST_COST = int(os.getenv("M4_REQUEST_COST", "1"))
M4_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
M4_REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "0.5"))
JIRA_UPSTREAM_MODE = os.getenv("JIRA_UPSTREAM_MODE", "mock")
JIRA_MOCK_BASE_URL = os.getenv("JIRA_MOCK_BASE_URL", "http://jira-mock:8080")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
UPSTREAM_TIMEOUT_SECONDS = float(os.getenv("JIRA_UPSTREAM_TIMEOUT_SECONDS", "3.0"))

PROJECT_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")
ISSUE_KEY_RE = re.compile(r"^([A-Z][A-Z0-9]{1,9})-[1-9][0-9]*$")

_redis_client: redis.Redis | None = None
_capiss_public_key: PublicKey | None = None


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
  return {0, 'budget_exceeded', budget_num}
end

local remaining = redis.call('DECRBY', budget_key, request_cost)
if redis.call('TTL', budget_key) < 0 then
  redis.call('EXPIRE', budget_key, budget_ttl)
end
return {1, 'ok', remaining}
"""


class UpstreamConfigError(Exception):
    pass


# DD: DD-301
# Implements: ARCH-023
# Title: iso_utc_now jira-tool audit timestamp helper
def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# DD: DD-302
# Implements: ARCH-023
# Title: log_event jira-tool structured audit logger
def log_event(event_type: str, **fields: object) -> None:
    payload = {
        "event_type": event_type,
        "timestamp": iso_utc_now(),
        **fields,
    }
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True), flush=True)


# DD: DD-303
# Implements: ARCH-023
# Title: get_redis jira-tool shared state client
def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            M4_REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=M4_REDIS_SOCKET_TIMEOUT,
        )
    return _redis_client


# DD: DD-304
# Implements: ARCH-023
# Title: load_capiss_public_key jira-tool issuer key loader
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


# DD: DD-305
# Implements: ARCH-023
# Title: project_from_resource jira-tool token project parser
def project_from_resource(res: str) -> str | None:
    if not res.startswith(JIRA_RESOURCE_PREFIX):
        return None
    project_key = res.removeprefix(JIRA_RESOURCE_PREFIX)
    if not PROJECT_KEY_RE.fullmatch(project_key):
        return None
    return project_key


# DD: DD-306
# Implements: ARCH-023
# Title: issue_key_from_facade_path jira-tool request parser
def issue_key_from_facade_path(raw_path: str) -> tuple[str, str] | None:
    parsed = urlsplit(raw_path)
    if parsed.query or parsed.fragment:
        return None
    if not parsed.path.startswith(JIRA_FACADE_PREFIX):
        return None
    issue_key = parsed.path.removeprefix(JIRA_FACADE_PREFIX)
    if "/" in issue_key:
        return None
    match = ISSUE_KEY_RE.fullmatch(issue_key)
    if not match:
        return None
    return issue_key, match.group(1)


# DD: DD-307
# Implements: ARCH-023
# Title: verify_chain_and_claims jira-tool shared chain contract adapter
def verify_chain_and_claims(biscuit: Biscuit) -> tuple[dict[str, str | int] | None, str]:
    claims, err = verify_chain_contract(biscuit, max_depth=M4_MAX_DEPTH)
    if claims is None:
        return None, err or "invalid_chain"
    if int(claims.get("effective_depth", 0)) != 0:
        return None, "delegation_not_supported"
    return claims, ""


# DD: DD-308
# Implements: ARCH-023
# Title: consume_budget_and_rate jira-tool shared-state budget enforcement
def consume_budget_and_rate(root_token_id: str, exp: int) -> tuple[bool, str, int]:
    budget_key = f"m4:budget:{root_token_id}"
    rate_key = f"m4:rate:{root_token_id}"
    ttl = max(1, exp - int(time.time()))
    try:
        result = get_redis().eval(
            CONSUME_BUDGET_RATE_LUA,
            2,
            budget_key,
            rate_key,
            str(M4_REQUEST_COST),
            str(M4_RATE_LIMIT),
            str(M4_RATE_WINDOW_SECONDS),
            str(ttl),
        )
    except redis.RedisError:
        return False, "store_unavailable", -1

    if not isinstance(result, (list, tuple)) or len(result) < 3:
        return False, "store_unavailable", -1

    allowed = int(result[0]) == 1
    reason = str(result[1])
    remaining = int(result[2])
    return allowed, reason, remaining


# DD: DD-309
# Implements: ARCH-023
# Title: verify_biscuit jira-tool request authorization verifier
def verify_biscuit(
    token_value: str,
    spiffe_id: str,
    requested_project: str,
    allowed_actions: set[str] | frozenset[str] | None = None,
) -> tuple[bool, str, dict[str, str | int] | None]:
    if allowed_actions is None:
        allowed_actions = {READ_ACT}
    public_key = load_capiss_public_key()
    if public_key is None:
        return False, "issuer_key_unavailable", None

    try:
        biscuit = Biscuit.from_base64(token_value, public_key)
    except (BiscuitSerializationError, BiscuitValidationError, BiscuitBlockError, Exception):
        return False, "invalid_token", None

    claims, chain_err = verify_chain_and_claims(biscuit)
    if claims is None:
        return False, chain_err, None

    now = int(time.time())
    subject = str(claims["subject_spiffe_id"])
    aud = str(claims["aud"])
    act = str(claims["act"])
    res = str(claims["res"])
    exp = int(claims["exp"])
    root_token_id = str(claims["root_token_id"])
    token_project = project_from_resource(res)
    if token_project is not None:
        claims["token_project"] = token_project

    if subject != spiffe_id:
        return False, "sub_mismatch", claims
    if aud != REQUIRED_AUD:
        return False, "insufficient_authority", claims
    if act not in allowed_actions:
        return False, "insufficient_authority", claims
    if token_project is None:
        return False, "insufficient_authority", claims
    if token_project != requested_project:
        return False, "project_mismatch", claims
    if exp <= now:
        return False, "expired", claims

    allowed, budget_reason, remaining = consume_budget_and_rate(root_token_id, exp)
    claims["budget_remaining"] = remaining
    if not allowed:
        if budget_reason == "rate_limited":
            return False, "rate_limited", claims
        if budget_reason in {"budget_exceeded", "missing_budget", "invalid_budget"}:
            return False, "budget_exceeded", claims
        return False, "store_unavailable", claims

    return True, "", claims


# DD: DD-310
# Implements: ARCH-023
# Title: upstream_issue_url jira-tool upstream route builder
def upstream_issue_url(issue_key: str) -> str:
    if JIRA_UPSTREAM_MODE == "live":
        if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
            raise UpstreamConfigError("live Jira configuration is incomplete")
        base_url = JIRA_BASE_URL.rstrip("/")
    else:
        base_url = JIRA_MOCK_BASE_URL.rstrip("/")
    return f"{base_url}/rest/api/3/issue/{quote(issue_key)}"


# DD: DD-311
# Implements: ARCH-023
# Title: upstream_headers jira-tool upstream credential isolation
def upstream_headers() -> dict[str, str]:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if JIRA_UPSTREAM_MODE == "live":
        raw = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode("utf-8")
        headers["Authorization"] = "Basic " + base64.b64encode(raw).decode("ascii")
    return headers


# DD: DD-312
# Implements: ARCH-023
# Title: call_upstream_issue jira-tool authorized upstream caller
def call_upstream_issue(
    issue_key: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
) -> tuple[int, bytes, str]:
    req = request.Request(
        upstream_issue_url(issue_key),
        headers=upstream_headers(),
        data=body,
        method=method,
    )
    try:
        with request.urlopen(req, timeout=UPSTREAM_TIMEOUT_SECONDS) as resp:
            content_type = resp.headers.get("Content-Type", "application/json")
            return resp.status, resp.read(), content_type
    except error.HTTPError as exc:
        content_type = exc.headers.get("Content-Type", "application/json")
        return exc.code, exc.read(), content_type
    except (error.URLError, TimeoutError):
        return 502, json.dumps({"error": "upstream_unavailable"}).encode("utf-8"), "application/json"


# DD: DD-321
# Implements: ARCH-023, ARCH-026
# Title: adf_from_plain_text jira-tool Jira Cloud description encoder
def adf_from_plain_text(description: str) -> dict[str, object]:
    lines = description.splitlines() or [""]
    content = []
    for line in lines:
        paragraph: dict[str, object] = {"type": "paragraph"}
        if line:
            paragraph["content"] = [{"type": "text", "text": line}]
        content.append(paragraph)
    return {"type": "doc", "version": 1, "content": content}


# DD: DD-322
# Implements: ARCH-023, ARCH-026
# Title: parse_description_update_body jira-tool write body validator
def parse_description_update_body(body: bytes) -> tuple[dict[str, object] | None, str]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "malformed_body"
    if not isinstance(payload, dict):
        return None, "malformed_body"
    if set(payload.keys()) != {"description"}:
        return None, "unsupported_fields"
    description = payload.get("description")
    if not isinstance(description, str):
        return None, "malformed_body"
    return {"fields": {"description": adf_from_plain_text(description)}}, ""


# DD: DD-313
# Implements: ARCH-023
# Title: upstream_project_key jira-tool upstream response project verifier
def upstream_project_key(body: bytes) -> str | None:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    project = payload.get("fields", {}).get("project", {})
    if not isinstance(project, dict):
        return None
    key = project.get("key")
    if not isinstance(key, str) or not PROJECT_KEY_RE.fullmatch(key):
        return None
    return key


def _event_fields(
    *,
    subject_spiffe_id: str | None,
    claims: dict | None,
    issue_key: str | None,
    requested_project: str | None,
    upstream_called: bool,
    jira_operation: str = "issue_read",
    upstream_status: int | None = None,
) -> dict[str, object]:
    fields: dict[str, object] = {
        "subject_spiffe_id": subject_spiffe_id,
        "jira_operation": jira_operation,
        "issue_key": issue_key,
        "requested_project": requested_project,
        "upstream_called": upstream_called,
        "upstream_status": upstream_status,
    }
    if claims:
        fields.update(
            {
                "root_token_id": claims.get("root_token_id"),
                "token_id": claims.get("token_id"),
                "parent_token_id": claims.get("parent_token_id"),
                "delegation_depth": claims.get("effective_depth"),
                "delegator_spiffe_id": claims.get("delegator_spiffe_id"),
                "aud": claims.get("aud"),
                "act": claims.get("act"),
                "res": claims.get("res"),
                "token_project": claims.get("token_project"),
                "budget_remaining": claims.get("budget_remaining"),
            }
        )
    return {key: value for key, value in fields.items() if value is not None}


class JiraToolHandler(BaseHTTPRequestHandler):
    server_version = "jira-tool"

    # DD: DD-314
    # Implements: ARCH-023
    # Title: JiraToolHandler.log_message jira-tool access log adapter
    def log_message(self, fmt, *args):
        return

    # DD: DD-315
    # Implements: ARCH-023
    # Title: JiraToolHandler._send_bytes jira-tool HTTP response helper
    def _send_bytes(self, status_code: int, body: bytes, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status_code: int, payload: dict[str, object]):
        self._send_bytes(status_code, json.dumps(payload).encode("utf-8"), "application/json")

    # DD: DD-316
    # Implements: ARCH-023
    # Title: JiraToolHandler._deny jira-tool standardized deny path
    def _deny(
        self,
        status: int,
        reason: str,
        spiffe_id: str | None,
        claims: dict | None = None,
        issue_key: str | None = None,
        requested_project: str | None = None,
        upstream_called: bool = False,
        jira_operation: str = "issue_read",
        upstream_status: int | None = None,
    ):
        log_event(
            "jiratool_enforcement_decision",
            result="deny",
            reason_code=reason,
            **_event_fields(
                subject_spiffe_id=spiffe_id,
                claims=claims,
                issue_key=issue_key,
                requested_project=requested_project,
                upstream_called=upstream_called,
                jira_operation=jira_operation,
                upstream_status=upstream_status,
            ),
        )
        self._send_json(status, {"error": "denied", "reason": reason})

    # DD: DD-317
    # Implements: ARCH-023
    # Title: JiraToolHandler._authorize jira-tool request authorization handler
    def _authorize(self, issue_key: str, requested_project: str, allowed_actions: set[str] | frozenset[str] | None = None, jira_operation: str = "issue_read"):
        spiffe_id = self.headers.get(SPIFFE_HEADER)
        if not spiffe_id:
            self._deny(401, "missing_spiffe_id", None, issue_key=issue_key, requested_project=requested_project, jira_operation=jira_operation)
            return None

        authz = self.headers.get("Authorization")
        if not authz or not authz.startswith("Bearer "):
            self._deny(401, "missing_token", spiffe_id, issue_key=issue_key, requested_project=requested_project, jira_operation=jira_operation)
            return None

        token_value = authz.split(" ", 1)[1].strip()
        if not token_value:
            self._deny(401, "missing_token", spiffe_id, issue_key=issue_key, requested_project=requested_project, jira_operation=jira_operation)
            return None

        allowed, reason, claims = verify_biscuit(token_value, spiffe_id, requested_project, allowed_actions)
        if not allowed:
            status = 401 if reason in {"invalid_token", "issuer_key_unavailable"} else 403
            if reason == "store_unavailable":
                status = 503
            self._deny(status, reason, spiffe_id, claims, issue_key=issue_key, requested_project=requested_project, jira_operation=jira_operation)
            return None

        return spiffe_id, claims

    # DD: DD-318
    # Implements: ARCH-023
    # Title: JiraToolHandler.do_GET jira-tool issue read dispatch
    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        parsed = issue_key_from_facade_path(self.path)
        if parsed is None:
            self._send_json(404, {"detail": "not found"})
            return

        issue_key, requested_project = parsed
        auth = self._authorize(issue_key, requested_project, {READ_ACT, WRITE_ACT}, "issue_read")
        if auth is None:
            return

        spiffe_id, claims = auth
        try:
            upstream_status, upstream_body, content_type = call_upstream_issue(issue_key)
        except UpstreamConfigError:
            self._deny(
                503,
                "upstream_config",
                spiffe_id,
                claims,
                issue_key=issue_key,
                requested_project=requested_project,
                upstream_called=False,
                jira_operation="issue_read",
            )
            return

        if upstream_status == 200:
            token_project = str(claims.get("token_project", ""))
            if upstream_project_key(upstream_body) != token_project:
                self._deny(
                    403,
                    "upstream_project_mismatch",
                    spiffe_id,
                    claims,
                    issue_key=issue_key,
                    requested_project=requested_project,
                    upstream_called=True,
                    jira_operation="issue_read",
                    upstream_status=upstream_status,
                )
                return

            log_event(
                "jiratool_enforcement_decision",
                result="allow",
                reason_code="ok",
                **_event_fields(
                    subject_spiffe_id=spiffe_id,
                    claims=claims,
                    issue_key=issue_key,
                    requested_project=requested_project,
                    upstream_called=True,
                    jira_operation="issue_read",
                    upstream_status=upstream_status,
                ),
            )
            self._send_bytes(200, upstream_body, content_type)
            return

        log_event(
            "jiratool_enforcement_decision",
            result="allow",
            reason_code="upstream_error",
            **_event_fields(
                subject_spiffe_id=spiffe_id,
                claims=claims,
                issue_key=issue_key,
                requested_project=requested_project,
                upstream_called=True,
                jira_operation="issue_read",
                upstream_status=upstream_status,
            ),
        )
        self._send_bytes(upstream_status, upstream_body, content_type)

    # DD: DD-323
    # Implements: ARCH-023, ARCH-026
    # Title: JiraToolHandler.do_PUT jira-tool issue description write dispatch
    def do_PUT(self):
        parsed = issue_key_from_facade_path(self.path)
        if parsed is None:
            self._send_json(404, {"detail": "not found"})
            return

        issue_key, requested_project = parsed
        auth = self._authorize(issue_key, requested_project, {WRITE_ACT}, "issue_description_write")
        if auth is None:
            return

        spiffe_id, claims = auth
        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._deny(
                400,
                "malformed_body",
                spiffe_id,
                claims,
                issue_key=issue_key,
                requested_project=requested_project,
                jira_operation="issue_description_write",
            )
            return
        if content_length < 0 or content_length > MAX_WRITE_BODY_BYTES:
            self._deny(
                400,
                "malformed_body",
                spiffe_id,
                claims,
                issue_key=issue_key,
                requested_project=requested_project,
                jira_operation="issue_description_write",
            )
            return

        update_payload, body_reason = parse_description_update_body(self.rfile.read(content_length))
        if update_payload is None:
            self._deny(
                400,
                body_reason,
                spiffe_id,
                claims,
                issue_key=issue_key,
                requested_project=requested_project,
                jira_operation="issue_description_write",
            )
            return

        try:
            upstream_status, upstream_body, content_type = call_upstream_issue(
                issue_key,
                method="PUT",
                body=json.dumps(update_payload, separators=(",", ":")).encode("utf-8"),
            )
        except UpstreamConfigError:
            self._deny(
                503,
                "upstream_config",
                spiffe_id,
                claims,
                issue_key=issue_key,
                requested_project=requested_project,
                upstream_called=False,
                jira_operation="issue_description_write",
            )
            return

        if upstream_status == 204:
            log_event(
                "jiratool_enforcement_decision",
                result="allow",
                reason_code="ok",
                **_event_fields(
                    subject_spiffe_id=spiffe_id,
                    claims=claims,
                    issue_key=issue_key,
                    requested_project=requested_project,
                    upstream_called=True,
                    jira_operation="issue_description_write",
                    upstream_status=upstream_status,
                ),
            )
            self._send_bytes(204, b"", content_type)
            return

        log_event(
            "jiratool_enforcement_decision",
            result="allow",
            reason_code="upstream_error",
            **_event_fields(
                subject_spiffe_id=spiffe_id,
                claims=claims,
                issue_key=issue_key,
                requested_project=requested_project,
                upstream_called=True,
                jira_operation="issue_description_write",
                upstream_status=upstream_status,
            ),
        )
        self._send_bytes(upstream_status, upstream_body, content_type)

    # DD: DD-319
    # Implements: ARCH-023
    # Title: JiraToolHandler.do_unsupported_method jira-tool method denial
    def do_POST(self):
        self._deny(405, "method_not_allowed", self.headers.get(SPIFFE_HEADER))

    def do_PATCH(self):
        self._deny(405, "method_not_allowed", self.headers.get(SPIFFE_HEADER))

    def do_DELETE(self):
        self._deny(405, "method_not_allowed", self.headers.get(SPIFFE_HEADER))


# DD: DD-320
# Implements: ARCH-023
# Title: main jira-tool HTTP server bootstrap
def main():
    httpd = HTTPServer(("0.0.0.0", 8080), JiraToolHandler)
    print("jira-tool listening on http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
