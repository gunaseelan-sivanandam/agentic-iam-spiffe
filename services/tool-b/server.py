import base64
import json
import os
import re
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

import redis
from cryptography import x509
from cryptography.x509.oid import ExtensionOID
from biscuit_auth import (
    Algorithm,
    Biscuit,
    BiscuitBlockError,
    BiscuitSerializationError,
    BiscuitValidationError,
    PublicKey,
)

SVID_CERT = os.getenv("SPIFFE_SVID_CERT", "/run/spire/svid/svid.pem")
SPIFFE_HEADER = "x-spiffe-id"
CAPISS_PUBLIC_KEY_PATH = os.getenv(
    "CAPISS_PUBLIC_KEY_PATH", "/var/lib/capiss/keys/root_public_key.b64"
)
REQUIRED_AUD = "tool-b"
M4_MAX_DEPTH = int(os.getenv("M4_MAX_DEPTH", "3"))
M4_RATE_LIMIT = int(os.getenv("M4_RATE_LIMIT", "20"))
M4_RATE_WINDOW_SECONDS = int(os.getenv("M4_RATE_WINDOW_SECONDS", "10"))
M4_REQUEST_COST = int(os.getenv("M4_REQUEST_COST", "1"))
M4_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
M4_REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "0.5"))

SECRET_VALUE = "super sensitive demo secret"
DISCOVERED_FILES = {
    "fileA": "alpha document",
    "fileB": "beta document",
    "fileC": "gamma document",
}

FACT_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)$")

_redis_client: redis.Redis | None = None


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

REGISTRY_ADD_LUA = """
local registry_key = KEYS[1]
local ttl = tonumber(ARGV[1])
for i = 2, #ARGV do
  redis.call('SADD', registry_key, ARGV[i])
end
if redis.call('TTL', registry_key) < 0 then
  redis.call('EXPIRE', registry_key, ttl)
else
  local current_ttl = redis.call('TTL', registry_key)
  if current_ttl > ttl then
    redis.call('EXPIRE', registry_key, ttl)
  end
end
return 1
"""


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event_type: str, **fields: object) -> None:
    payload = {
        "event_type": event_type,
        "timestamp": iso_utc_now(),
        **fields,
    }
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True), flush=True)


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


def spiffe_id_from_cert_path(path: str) -> str | None:
    with open(path, "rb") as handle:
        cert = x509.load_pem_x509_certificate(handle.read())
    san = cert.extensions.get_extension_for_oid(
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    ).value
    for uri in san.get_values_for_type(x509.UniformResourceIdentifier):
        if uri.startswith("spiffe://"):
            return uri
    return None


_CAPISS_PUBLIC_KEY: PublicKey | None = None


def load_capiss_public_key() -> PublicKey | None:
    global _CAPISS_PUBLIC_KEY
    if _CAPISS_PUBLIC_KEY is not None:
        return _CAPISS_PUBLIC_KEY
    if not os.path.exists(CAPISS_PUBLIC_KEY_PATH):
        return None
    with open(CAPISS_PUBLIC_KEY_PATH, "rb") as handle:
        raw = handle.read().strip()
    if not raw:
        return None
    decoded = base64.b64decode(raw)
    _CAPISS_PUBLIC_KEY = PublicKey.from_bytes(decoded, Algorithm.Ed25519)
    return _CAPISS_PUBLIC_KEY


def parse_fact_arg(raw: str) -> str | int:
    value = raw.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        unquoted = value[1:-1]
        return unquoted.replace(r'\"', '"').replace(r"\\", "\\")
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return value


def parse_block_source(src: str) -> dict[str, str | int]:
    claims: dict[str, str | int] = {}
    for line in src.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(";"):
            line = line[:-1].strip()
        match = FACT_RE.match(line)
        if not match:
            continue
        name, arg = match.groups()
        claims[name] = parse_fact_arg(arg)
    if "subject_spiffe_id" not in claims and "sub" in claims:
        claims["subject_spiffe_id"] = claims["sub"]
    return claims


def canonical_res_for_path(path: str) -> tuple[str, str] | None:
    if path == "/secret":
        return "read", "/secret"
    if path == "/search":
        return "read", "tool-b:/search"
    if path.startswith("/read-file/"):
        object_id = path.split("/", 2)[2]
        if not object_id or "/" in object_id or " " in object_id:
            return None
        return "read", f"tool-b:/read-file:{object_id}"
    return None


def verify_chain_and_claims(biscuit: Biscuit) -> tuple[dict[str, str | int] | None, str]:
    count = biscuit.block_count()
    if count <= 0:
        return None, "invalid_chain"

    chain: list[dict[str, str | int]] = []
    for idx in range(count):
        block = parse_block_source(biscuit.block_source(idx))
        if "delegation_depth" not in block:
            block["delegation_depth"] = idx
        chain.append(block)

    required = ("root_token_id", "token_id", "subject_spiffe_id", "aud", "act", "res", "exp")
    first = chain[0]
    for key in required:
        if key not in first:
            return None, "missing_chain_metadata"

    root_token_id = str(first["root_token_id"])
    prev_token_id = str(first["token_id"])
    prev_aud = str(first["aud"])
    prev_act = str(first["act"])
    prev_res = str(first["res"])
    prev_exp = int(first["exp"])

    for idx in range(1, len(chain)):
        block = chain[idx]
        for key in required:
            if key not in block:
                return None, "missing_chain_metadata"
        if str(block["root_token_id"]) != root_token_id:
            return None, "invalid_chain"
        if str(block.get("parent_token_id", "")) != prev_token_id:
            return None, "invalid_chain"
        if not block.get("delegator_spiffe_id"):
            return None, "invalid_chain"

        aud = str(block["aud"])
        act = str(block["act"])
        res = str(block["res"])
        exp = int(block["exp"])

        # M4 minimal attenuation in this slice:
        # - aud/act must remain equal
        # - res changes are only valid for capiss-minted checkpoint tokens
        if aud != prev_aud or act != prev_act:
            return None, "amplified_authority"
        if res != prev_res:
            store_ok, marker_hit = is_capiss_minted_token(str(block["token_id"]), exp)
            if not store_ok:
                return None, "store_unavailable"
            if not marker_hit:
                return None, "amplified_authority"
        if exp > prev_exp:
            return None, "amplified_authority"

        prev_token_id = str(block["token_id"])
        prev_aud = aud
        prev_act = act
        prev_res = res
        prev_exp = exp

    final = dict(chain[-1])
    effective_depth = len(chain) - 1
    final["effective_depth"] = effective_depth
    if int(final.get("delegation_depth", effective_depth)) != effective_depth:
        return None, "invalid_depth_metadata"
    if effective_depth > M4_MAX_DEPTH:
        return None, "depth_exceeded"

    return final, ""


def consume_budget_and_rate(root_token_id: str, exp: int) -> tuple[bool, str, int]:
    budget_key = f"m4:budget:{root_token_id}"
    rate_key = f"m4:rate:{root_token_id}"
    ttl = max(1, exp - int(time.time()))
    try:
        client = get_redis()
        result = client.eval(
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

    if not isinstance(result, list) or len(result) < 3:
        return False, "store_unavailable", -1

    allowed = int(result[0]) == 1
    reason = str(result[1])
    remaining = int(result[2])
    return allowed, reason, remaining


def is_capiss_minted_token(token_id: str, exp: int) -> tuple[bool, bool]:
    marker_key = f"m4:capiss_minted:{token_id}"
    ttl = max(1, exp - int(time.time()))
    try:
        client = get_redis()
        hit = client.get(marker_key)
        if hit is None:
            return True, False
        key_ttl = client.ttl(marker_key)
        if key_ttl > ttl:
            client.expire(marker_key, ttl)
        return True, True
    except redis.RedisError:
        return False, False


def record_discovery(
    root_token_id: str,
    subject_spiffe_id: str,
    resources: list[str],
    root_exp: int,
) -> bool:
    registry_key = f"m4:registry:{root_token_id}"
    ttl = max(1, root_exp - int(time.time()))
    try:
        client = get_redis()
        client.eval(REGISTRY_ADD_LUA, 1, registry_key, str(ttl), *resources)
        log_event(
            "discovery_registry_write",
            root_token_id=root_token_id,
            subject_spiffe_id=subject_spiffe_id,
            discovery_endpoint="tool-b:/search",
            res_count=len(resources),
        )
        return True
    except redis.RedisError:
        return False


def verify_biscuit(token_value: str, spiffe_id: str, required_act: str, required_res: str):
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

    if subject != spiffe_id:
        return False, "sub_mismatch", claims
    if aud != REQUIRED_AUD:
        return False, "insufficient_authority", claims
    if act != required_act:
        return False, "insufficient_authority", claims
    if res not in {required_res, "tool-b:/secret" if required_res == "/secret" else required_res}:
        return False, "insufficient_authority", claims
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


class ToolBHandler(BaseHTTPRequestHandler):
    server_version = "tool-b"

    def log_message(self, fmt, *args):
        return

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _deny(self, status: int, reason: str, spiffe_id: str | None, claims: dict | None = None):
        root_token_id = None
        token_id = None
        parent_token_id = None
        depth = None
        aud = None
        act = None
        res = None
        remaining = None
        if claims:
            root_token_id = claims.get("root_token_id")
            token_id = claims.get("token_id")
            parent_token_id = claims.get("parent_token_id")
            depth = claims.get("effective_depth")
            aud = claims.get("aud")
            act = claims.get("act")
            res = claims.get("res")
            remaining = claims.get("budget_remaining")

        log_event(
            "toolb_enforcement_decision",
            result="deny",
            reason_code=reason,
            caller_subject_spiffe_id=spiffe_id,
            root_token_id=root_token_id,
            token_id=token_id,
            parent_token_id=parent_token_id,
            delegation_depth=depth,
            aud=aud,
            act=act,
            res=res,
            budget_remaining=remaining,
            path=self.path,
        )
        self._send_json(status, {"error": "denied", "reason": reason})

    def _authorize(self, required_act: str, required_res: str):
        spiffe_id = self.headers.get(SPIFFE_HEADER)
        if not spiffe_id:
            self._deny(401, "missing_spiffe_id", None)
            return None

        authz = self.headers.get("Authorization")
        if not authz or not authz.startswith("Bearer "):
            self._deny(401, "missing_token", spiffe_id)
            return None

        token_value = authz.split(" ", 1)[1].strip()
        if not token_value:
            self._deny(401, "missing_token", spiffe_id)
            return None

        allowed, reason, claims = verify_biscuit(token_value, spiffe_id, required_act, required_res)
        if not allowed:
            status = 401 if reason in {"invalid_token", "issuer_key_unavailable"} else 403
            self._deny(status, reason, spiffe_id, claims)
            return None

        log_event(
            "toolb_enforcement_decision",
            result="allow",
            reason_code="ok",
            caller_subject_spiffe_id=spiffe_id,
            root_token_id=claims.get("root_token_id"),
            token_id=claims.get("token_id"),
            parent_token_id=claims.get("parent_token_id"),
            delegation_depth=claims.get("effective_depth"),
            aud=claims.get("aud"),
            act=claims.get("act"),
            res=claims.get("res"),
            budget_remaining=claims.get("budget_remaining"),
            path=self.path,
        )
        return claims

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        required = canonical_res_for_path(self.path)
        if required is None:
            self._send_json(404, {"detail": "not found"})
            return

        required_act, required_res = required
        claims = self._authorize(required_act, required_res)
        if claims is None:
            return

        if self.path == "/secret":
            self._send_json(200, {"secret": SECRET_VALUE})
            return

        if self.path == "/search":
            resources = [f"tool-b:/read-file:{key}" for key in sorted(DISCOVERED_FILES.keys())]
            root_exp = int(claims.get("exp", int(time.time()) + 1))
            root_token_id = str(claims["root_token_id"])
            subject = str(claims["subject_spiffe_id"])
            if not record_discovery(root_token_id, subject, resources, root_exp):
                self._deny(503, "store_unavailable", subject, claims)
                return
            self._send_json(200, {"resources": resources})
            return

        if self.path.startswith("/read-file/"):
            file_id = self.path.split("/", 2)[2]
            if file_id not in DISCOVERED_FILES:
                self._send_json(404, {"error": "not_found"})
                return
            self._send_json(200, {"id": file_id, "content": DISCOVERED_FILES[file_id]})
            return

        self._send_json(404, {"detail": "not found"})


def main():
    spiffe_id = spiffe_id_from_cert_path(SVID_CERT)
    print(f"tool-b SPIFFE ID: {spiffe_id}")

    httpd = HTTPServer(("0.0.0.0", 8080), ToolBHandler)
    print("tool-b listening on http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
