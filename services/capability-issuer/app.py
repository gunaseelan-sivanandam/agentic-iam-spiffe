import base64
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from urllib import request
from urllib.error import URLError

import redis
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from shared.enforcement_contract import verify_chain_contract

from biscuit_auth import (
    Algorithm,
    Biscuit,
    BiscuitBlockError,
    BiscuitBuilder,
    BiscuitSerializationError,
    BiscuitValidationError,
    BlockBuilder,
    Fact,
    KeyPair,
    PrivateKey,
)

app = FastAPI()


@app.get("/health")
# DD: DD-107
# Implements: ARCH-012
# Title: health capability issuer health endpoint
def health():
    return {"status": "ok"}


OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/capiss/allow")
OPA_TIMEOUT_SECONDS = float(os.getenv("OPA_TIMEOUT_SECONDS", "1.0"))
CAPABILITY_TTL_SECONDS = int(os.getenv("CAPABILITY_TTL_SECONDS", "60"))
M4_MAX_DEPTH = int(os.getenv("M4_MAX_DEPTH", "3"))
M4_DEFAULT_BUDGET = int(os.getenv("M4_DEFAULT_BUDGET", "10"))
M4_ROOT_TTL_SECONDS = int(os.getenv("M4_ROOT_TTL_SECONDS", "60"))
M4_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
M4_REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "0.5"))
CAPISS_KEY_DIR = os.getenv("CAPISS_KEY_DIR", "/var/lib/capiss/keys")
CAPISS_KEY_FILE = os.path.join(CAPISS_KEY_DIR, "root_key.b64")
CAPISS_PUBLIC_KEY_FILE = os.path.join(CAPISS_KEY_DIR, "root_public_key.b64")

FACT_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)$")
JIRA_PROJECT_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")
CAPISS_POLICY_ID = "capiss.allow.v3"
CAPISS_POLICY_HASH = "sha256:capiss-policy-v3"

CONSUME_MINT_RATE_LUA = """
local mint_rate_key = KEYS[1]
local allowed = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])

if allowed == nil or ttl == nil then
  return {0, 'invalid_arguments', -1}
end

local current = tonumber(redis.call('GET', mint_rate_key) or '0')
if current == nil then
  return {0, 'invalid_counter', -1}
end

if current >= allowed then
  redis.call('EXPIRE', mint_rate_key, ttl)
  return {0, 'mint_rate_exceeded', current}
end

local new_count = redis.call('INCR', mint_rate_key)
redis.call('EXPIRE', mint_rate_key, ttl)
return {1, 'ok', new_count}
"""


# DD: DD-108
# Implements: ARCH-012
# Title: iso_utc_now capability issuer audit timestamp helper
def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# DD: DD-109
# Implements: ARCH-012
# Title: log_event capability issuer structured audit logger
def log_event(event_type: str, **fields: object) -> None:
    payload = {
        "event_type": event_type,
        "timestamp": iso_utc_now(),
        **fields,
    }
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True), flush=True)


# DD: DD-110
# Implements: ARCH-012, ARCH-013
# Title: check_opa_allow capability issuer OPA decision client
def check_opa_allow(input_payload: dict) -> tuple[bool | None, str | None]:
    data = json.dumps({"input": input_payload}).encode("utf-8")
    req = request.Request(
        OPA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=OPA_TIMEOUT_SECONDS) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return bool(body.get("result")), None
    except (URLError, json.JSONDecodeError, TimeoutError) as exc:
        return None, str(exc)


# DD: DD-111
# Implements: ARCH-012
# Title: load_or_create_root_private_key capability issuer signing key bootstrap
def load_or_create_root_private_key() -> tuple[PrivateKey, bool]:
    os.makedirs(CAPISS_KEY_DIR, exist_ok=True)
    if os.path.exists(CAPISS_KEY_FILE):
        with open(CAPISS_KEY_FILE, "rb") as handle:
            raw = handle.read()
        return PrivateKey.from_bytes(base64.b64decode(raw), Algorithm.Ed25519), False

    keypair = KeyPair()
    private_key = keypair.private_key
    encoded = base64.b64encode(private_key.to_bytes())
    created = False
    try:
        fd = os.open(CAPISS_KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
        created = True
    except FileExistsError:
        with open(CAPISS_KEY_FILE, "rb") as handle:
            raw = handle.read()
        private_key = PrivateKey.from_bytes(base64.b64decode(raw), Algorithm.Ed25519)
    return private_key, created


# DD: DD-112
# Implements: ARCH-012
# Title: write_public_key capability issuer public key export
def write_public_key(private_key: PrivateKey) -> None:
    keypair = KeyPair.from_private_key(private_key)
    encoded = base64.b64encode(keypair.public_key.to_bytes())
    fd = os.open(CAPISS_PUBLIC_KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(encoded)


# DD: DD-113
# Implements: ARCH-012
# Title: public_key_needs_update capability issuer public key drift check
def public_key_needs_update(private_key: PrivateKey) -> bool:
    if not os.path.exists(CAPISS_PUBLIC_KEY_FILE):
        return True
    try:
        with open(CAPISS_PUBLIC_KEY_FILE, "rb") as handle:
            raw = handle.read().strip()
        if not raw:
            return True
        keypair = KeyPair.from_private_key(private_key)
        expected = base64.b64encode(keypair.public_key.to_bytes())
        return raw != expected
    except OSError:
        return True


ROOT_PRIVATE_KEY, _ROOT_KEY_CREATED = load_or_create_root_private_key()
ROOT_PUBLIC_KEY = KeyPair.from_private_key(ROOT_PRIVATE_KEY).public_key
if _ROOT_KEY_CREATED or public_key_needs_update(ROOT_PRIVATE_KEY):
    write_public_key(ROOT_PRIVATE_KEY)

_redis_client: redis.Redis | None = None


# DD: DD-114
# Implements: ARCH-006, ARCH-012, ARCH-016
# Title: get_redis capability issuer shared state client
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


# DD: DD-115
# Implements: ARCH-004, ARCH-012
# Title: validate_mint_payload capability issuer mint request validator
def validate_mint_payload(payload: dict | None) -> tuple[dict | None, JSONResponse | None]:
    if payload is None:
        return None, JSONResponse(
            status_code=400,
            content={"error": "bad_request", "reason": "body"},
        )

    required_fields = ("aud", "act", "res")
    cleaned = {}
    for field in required_fields:
        if field not in payload:
            return None, JSONResponse(
                status_code=400,
                content={"error": "bad_request", "reason": field},
            )
        value = payload[field]
        if not isinstance(value, str):
            return None, JSONResponse(
                status_code=400,
                content={"error": "bad_request", "reason": field},
            )
        value = value.strip()
        if not value:
            return None, JSONResponse(
                status_code=400,
                content={"error": "bad_request", "reason": field},
            )
        cleaned[field] = value

    return cleaned, None


# DD: DD-126
# Implements: ARCH-004, ARCH-012, ARCH-021
# Title: canonicalize_jira_project_resource capability issuer Jira project resource guard
def canonicalize_jira_project_resource(res: str) -> str | None:
    if not res.startswith("jira-tool:/project:"):
        return None

    project_key = res.removeprefix("jira-tool:/project:")
    if not JIRA_PROJECT_KEY_RE.fullmatch(project_key):
        return None
    if any(marker in project_key for marker in ("*", "?", "[", "]", ",", ":")):
        return None
    return f"jira-tool:/project:{project_key}"


# DD: DD-129
# Implements: ARCH-028
# Title: canonicalize_jira_mcp_project_resource capability issuer Jira MCP project resource guard
def canonicalize_jira_mcp_project_resource(res: str) -> str | None:
    if not res.startswith("jira-mcp:/project:"):
        return None

    project_key = res.removeprefix("jira-mcp:/project:")
    if not JIRA_PROJECT_KEY_RE.fullmatch(project_key):
        return None
    if any(marker in project_key for marker in ("*", "?", "[", "]", ",", ":", "/", " ")):
        return None
    return f"jira-mcp:/project:{project_key}"


# DD: DD-101
# Implements: ARCH-004, ARCH-012, ARCH-021
# Title: canonicalize_resource capability issuer resource canonicalization guard
def canonicalize_resource(aud: str, res: str) -> str | None:
    if aud == "jira-mcp-gateway":
        return canonicalize_jira_mcp_project_resource(res)

    if aud == "jira-tool":
        return canonicalize_jira_project_resource(res)

    if aud != "tool-b":
        return None

    if res.startswith("tool-b:/"):
        canonical = res
    elif res.startswith("/"):
        canonical = f"tool-b:{res}"
    else:
        return None

    low = canonical.lower()
    if "*" in canonical or "?" in canonical or "[" in canonical or "]" in canonical:
        return None
    if "regex" in low or "glob" in low or "all" == low.strip():
        return None

    if canonical.startswith("tool-b:/read-file:"):
        object_id = canonical.split(":", 2)[-1]
        if not object_id or "/" in object_id or " " in object_id:
            return None

    if canonical in {"tool-b:/search", "tool-b:/secret"} or canonical.startswith(
        "tool-b:/read-file:"
    ):
        return canonical

    return None


# DD: DD-116
# Implements: ARCH-012
# Title: parse_fact_arg capability issuer biscuit fact parser
def parse_fact_arg(raw: str) -> str | int:
    value = raw.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        unquoted = value[1:-1]
        return unquoted.replace(r'\"', '"').replace(r"\\", "\\")
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return value


# DD: DD-117
# Implements: ARCH-012
# Title: parse_block_source capability issuer biscuit block parser
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


# DD: DD-118
# Implements: ARCH-012
# Title: extract_chain_claims capability issuer chain claim extractor
def extract_chain_claims(biscuit: Biscuit) -> list[dict[str, str | int]]:
    count = biscuit.block_count()
    chain: list[dict[str, str | int]] = []
    for idx in range(count):
        block = parse_block_source(biscuit.block_source(idx))
        if "delegation_depth" not in block:
            block["delegation_depth"] = idx
        chain.append(block)
    return chain


# DD: DD-102
# Implements: ARCH-004, ARCH-012, ARCH-020
# Title: verify_and_extract_chain capability issuance shared chain contract adapter
def verify_and_extract_chain(biscuit: Biscuit) -> tuple[dict[str, str | int] | None, str | None]:
    def _allow_capiss_resource_transition(
        _previous: dict[str, str | int],
        current: dict[str, str | int],
    ) -> tuple[bool, str | None]:
        marker_key = f'm4:capiss_minted:{current["token_id"]}'
        try:
            marker = get_redis().get(marker_key)
        except redis.RedisError:
            return False, "store_unavailable"
        if marker not in (b"1", "1"):
            return False, "amplified_authority"
        return True, None

    return verify_chain_contract(
        biscuit,
        max_depth=M4_MAX_DEPTH,
        allow_resource_transition=_allow_capiss_resource_transition,
    )


# DD: DD-119
# Implements: ARCH-012
# Title: parse_token capability issuer biscuit decode helper
def parse_token(token_value: str) -> tuple[Biscuit | None, dict[str, str | int] | None, str | None]:
    try:
        biscuit = Biscuit.from_base64(token_value, ROOT_PUBLIC_KEY)
    except (BiscuitSerializationError, BiscuitValidationError, BiscuitBlockError, Exception):
        return None, None, "invalid_token"

    claims, err = verify_and_extract_chain(biscuit)
    if err is not None:
        return None, None, err
    return biscuit, claims, None


# DD: DD-120
# Implements: ARCH-006, ARCH-012, ARCH-016
# Title: ensure_root_budget capability issuer root budget initializer
def ensure_root_budget(root_token_id: str, root_exp: int) -> tuple[bool, str]:
    ttl = max(1, root_exp - int(time.time()))
    budget_key = f"m4:budget:{root_token_id}"
    try:
        client = get_redis()
        pipe = client.pipeline(transaction=True)
        pipe.set(budget_key, M4_DEFAULT_BUDGET, ex=ttl)
        pipe.execute()
        return True, ""
    except redis.RedisError as exc:
        return False, str(exc)


# DD: DD-121
# Implements: ARCH-006, ARCH-012, ARCH-016
# Title: mark_capiss_minted_token capability issuer delegated token marker
def mark_capiss_minted_token(token_id: str, exp: int) -> tuple[bool, str]:
    ttl = max(1, exp - int(time.time()))
    mint_key = f"m4:capiss_minted:{token_id}"
    try:
        client = get_redis()
        client.set(mint_key, "1", ex=ttl)
        return True, ""
    except redis.RedisError as exc:
        return False, str(exc)


# DD: DD-122
# Implements: ARCH-006, ARCH-012, ARCH-016
# Title: registry_has_resource capability issuer discovery registry lookup
def registry_has_resource(root_token_id: str, res: str) -> tuple[bool, bool, str]:
    registry_key = f"m4:registry:{root_token_id}"
    try:
        client = get_redis()
        script = "return redis.call('SISMEMBER', KEYS[1], ARGV[1])"
        result = client.eval(script, 1, registry_key, res)
        return True, bool(int(result)), ""
    except redis.RedisError as exc:
        return False, False, str(exc)


# DD: DD-221
# Implements: ARCH-004, ARCH-006, ARCH-012, ARCH-016
# Title: consume_mint_rate capability issuer new-resource mint-rate enforcer
def consume_mint_rate(root_token_id: str, root_exp: int, root_token_lifetime_seconds: int) -> tuple[bool, str]:
    allowed = max(1, root_token_lifetime_seconds // 20)
    ttl = max(1, root_exp - int(time.time()))
    mint_rate_key = f"m4:mint_rate:{root_token_id}"
    try:
        client = get_redis()
        result = client.eval(CONSUME_MINT_RATE_LUA, 1, mint_rate_key, str(allowed), str(ttl))
    except redis.RedisError:
        return False, "store_unavailable"

    if not isinstance(result, (list, tuple)) or len(result) < 2:
        return False, "store_unavailable"

    try:
        allowed_flag = int(result[0])
    except (TypeError, ValueError):
        return False, "store_unavailable"

    reason_value = result[1]
    if isinstance(reason_value, bytes):
        reason = reason_value.decode("utf-8", errors="replace")
    else:
        reason = str(reason_value)

    if allowed_flag == 1 and reason == "ok":
        return True, ""
    if allowed_flag == 0 and reason == "mint_rate_exceeded":
        return False, "mint_rate_exceeded"
    return False, "store_unavailable"


# DD: DD-123
# Implements: ARCH-004, ARCH-012
# Title: mint_root_biscuit capability issuer root biscuit mint helper
def mint_root_biscuit(sub: str, aud: str, act: str, res: str) -> tuple[str, int, str, str]:
    expires_at = int(time.time()) + M4_ROOT_TTL_SECONDS
    root_token_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    builder = BiscuitBuilder()
    builder.add_fact(Fact(f'sub("{sub}")'))
    builder.add_fact(Fact(f'subject_spiffe_id("{sub}")'))
    builder.add_fact(Fact(f'aud("{aud}")'))
    builder.add_fact(Fact(f'act("{act}")'))
    builder.add_fact(Fact(f'res("{res}")'))
    builder.add_fact(Fact(f"exp({expires_at})"))
    builder.add_fact(Fact(f'root_token_id("{root_token_id}")'))
    builder.add_fact(Fact(f'token_id("{token_id}")'))
    builder.add_fact(Fact("delegation_depth(0)"))

    token = builder.build(ROOT_PRIVATE_KEY)
    token_value = token.to_base64()
    return token_value, expires_at, root_token_id, token_id


# DD: DD-124
# Implements: ARCH-004, ARCH-012
# Title: append_resource_token capability issuer delegated biscuit append helper
def append_resource_token(
    parent: Biscuit,
    parent_claims: dict[str, str | int],
    subject_spiffe_id: str,
    aud: str,
    act: str,
    res: str,
) -> tuple[str, int, str]:
    parent_exp = int(parent_claims["exp"])
    expires_at = min(parent_exp, int(time.time()) + CAPABILITY_TTL_SECONDS)
    token_id = str(uuid.uuid4())

    block = BlockBuilder()
    block.add_fact(Fact(f'sub("{subject_spiffe_id}")'))
    block.add_fact(Fact(f'subject_spiffe_id("{subject_spiffe_id}")'))
    block.add_fact(Fact(f'delegator_spiffe_id("{subject_spiffe_id}")'))
    block.add_fact(Fact(f'root_token_id("{parent_claims["root_token_id"]}")'))
    block.add_fact(Fact(f'token_id("{token_id}")'))
    block.add_fact(Fact(f'parent_token_id("{parent_claims["token_id"]}")'))
    block.add_fact(Fact(f'aud("{aud}")'))
    block.add_fact(Fact(f'act("{act}")'))
    block.add_fact(Fact(f'res("{res}")'))
    block.add_fact(Fact(f"exp({expires_at})"))
    next_depth = int(parent_claims["effective_depth"]) + 1
    block.add_fact(Fact(f"delegation_depth({next_depth})"))

    delegated = parent.append(block)
    return delegated.to_base64(), expires_at, token_id


# DD: DD-125
# Implements: ARCH-004, ARCH-012, ARCH-013
# Title: decision_input capability issuer policy input assembler
def decision_input(
    decision_type: str,
    subject: str,
    aud: str,
    act: str,
    res: str,
    root_token_id: str | None = None,
    registry_hit: bool | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "decision_type": decision_type,
        "sub": subject,
        "subject_spiffe_id": subject,
        "aud": aud,
        "act": act,
        "res": res,
    }
    if root_token_id is not None:
        payload["root_token_id"] = root_token_id
    if registry_hit is not None:
        payload["registry_hit"] = registry_hit
    return payload


# DD: DD-222
# Implements: ARCH-004, ARCH-012
# Title: log_mint_decision capability issuer final mint-decision audit helper
def log_mint_decision(
    *,
    result: str,
    reason_code: str,
    decision_type: str,
    subject_spiffe_id: str | None = None,
    delegator_spiffe_id: str | None = None,
    payload: dict | None = None,
    aud: str | None = None,
    act: str | None = None,
    res: str | None = None,
    root_token_id: str | None = None,
    token_id: str | None = None,
    parent_token_id: str | None = None,
    delegation_depth: int | None = None,
    registry_hit: bool | None = None,
    error: str | None = None,
) -> None:
    payload_aud = payload.get("aud") if isinstance(payload, dict) else None
    payload_act = payload.get("act") if isinstance(payload, dict) else None
    payload_res = payload.get("res") if isinstance(payload, dict) else None
    fields = {
        "result": result,
        "reason_code": reason_code,
        "decision_type": decision_type,
        "subject_spiffe_id": subject_spiffe_id,
        "delegator_spiffe_id": delegator_spiffe_id,
        "aud": aud if aud is not None else payload_aud if isinstance(payload_aud, str) and payload_aud.strip() else None,
        "act": act if act is not None else payload_act if isinstance(payload_act, str) and payload_act.strip() else None,
        "res": res if res is not None else payload_res if isinstance(payload_res, str) and payload_res.strip() else None,
        "root_token_id": root_token_id,
        "token_id": token_id,
        "parent_token_id": parent_token_id,
        "delegation_depth": delegation_depth,
        "registry_hit": registry_hit,
        "error": error if error else None,
        "policy_id": CAPISS_POLICY_ID,
        "policy_hash": CAPISS_POLICY_HASH,
    }
    log_event("capiss_mint_decision", **{key: value for key, value in fields.items() if value is not None})


# DD: DD-103
# Implements: ARCH-004, ARCH-012, ARCH-013
# Title: run_policy_or_fail capability issuer policy decision boundary
def run_policy_or_fail(policy_input: dict[str, object]) -> tuple[bool, JSONResponse | None]:
    allowed, err = check_opa_allow(policy_input)
    if allowed is None:
        log_event(
            "capiss_policy_error",
            result="deny",
            reason_code="opa_unavailable",
            policy_input=policy_input,
            error=err,
        )
        return False, JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "opa_unavailable"},
        )
    if not allowed:
        log_event(
            "capiss_policy_decision",
            result="deny",
            reason_code="policy",
            policy_input=policy_input,
            policy_id=CAPISS_POLICY_ID,
            policy_hash=CAPISS_POLICY_HASH,
        )
        return False, JSONResponse(
            status_code=403,
            content={"error": "denied", "reason": "policy"},
        )
    return True, None


@app.post("/capabilities/root-mint")
# DD: DD-104
# Implements: ARCH-004, ARCH-012
# Title: root_mint capability issuer root token endpoint
def root_mint(
    payload: dict | None = None,
    x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id"),
):
    if not x_spiffe_id:
        log_mint_decision(
            result="deny",
            reason_code="missing_spiffe_id",
            decision_type="root_mint",
            payload=payload,
        )
        raise HTTPException(status_code=401, detail="missing x-spiffe-id")
    if not x_spiffe_id.startswith("spiffe://"):
        log_mint_decision(
            result="deny",
            reason_code="invalid_spiffe_id",
            decision_type="root_mint",
            payload=payload,
        )
        raise HTTPException(status_code=400, detail="invalid x-spiffe-id")

    cleaned, error_response = validate_mint_payload(payload)
    if error_response is not None:
        reason_code = json.loads(error_response.body.decode("utf-8"))["reason"]
        log_mint_decision(
            result="deny",
            reason_code=reason_code,
            decision_type="root_mint",
            subject_spiffe_id=x_spiffe_id,
            payload=payload,
        )
        return error_response

    canonical_res = canonicalize_resource(cleaned["aud"], cleaned["res"])
    if canonical_res is None:
        log_mint_decision(
            result="deny",
            reason_code="res",
            decision_type="root_mint",
            subject_spiffe_id=x_spiffe_id,
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=cleaned["res"],
        )
        return JSONResponse(
            status_code=400,
            content={"error": "bad_request", "reason": "res"},
        )

    policy_input = decision_input(
        "root_mint",
        x_spiffe_id,
        cleaned["aud"],
        cleaned["act"],
        canonical_res,
    )
    ok, fail_response = run_policy_or_fail(policy_input)
    if not ok:
        reason_code = json.loads(fail_response.body.decode("utf-8"))["reason"]
        log_mint_decision(
            result="deny",
            reason_code=reason_code,
            decision_type="root_mint",
            subject_spiffe_id=x_spiffe_id,
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=canonical_res,
        )
        return fail_response

    token_value, expires_at, root_token_id, token_id = mint_root_biscuit(
        x_spiffe_id,
        cleaned["aud"],
        cleaned["act"],
        canonical_res,
    )

    ready, redis_err = ensure_root_budget(root_token_id, expires_at)
    if not ready:
        log_mint_decision(
            result="deny",
            reason_code="store_unavailable",
            decision_type="root_mint",
            subject_spiffe_id=x_spiffe_id,
            root_token_id=root_token_id,
            token_id=token_id,
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=canonical_res,
            error=redis_err,
        )
        return JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "store_unavailable"},
        )

    marked, mark_err = mark_capiss_minted_token(token_id, expires_at)
    if not marked:
        log_mint_decision(
            result="deny",
            reason_code="store_unavailable",
            decision_type="root_mint",
            subject_spiffe_id=x_spiffe_id,
            root_token_id=root_token_id,
            token_id=token_id,
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=canonical_res,
            error=mark_err,
        )
        return JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "store_unavailable"},
        )

    log_mint_decision(
        result="allow",
        reason_code="ok",
        decision_type="root_mint",
        subject_spiffe_id=x_spiffe_id,
        root_token_id=root_token_id,
        token_id=token_id,
        parent_token_id=None,
        delegation_depth=0,
        aud=cleaned["aud"],
        act=cleaned["act"],
        res=canonical_res,
    )

    return {
        "token_type": "biscuit",
        "token": token_value,
        "expires_at": expires_at,
        "issued_to": x_spiffe_id,
        "aud": cleaned["aud"],
        "act": cleaned["act"],
        "res": canonical_res,
        "root_token_id": root_token_id,
        "token_id": token_id,
        "parent_token_id": None,
        "delegation_depth": 0,
    }


@app.post("/capabilities/resource-mint")
# DD: DD-105
# Implements: ARCH-004, ARCH-006, ARCH-012
# Title: resource_mint capability issuer delegated resource endpoint
def resource_mint(
    payload: dict | None = None,
    x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id"),
    authorization: str | None = Header(default=None, alias="authorization"),
):
    if not x_spiffe_id:
        log_mint_decision(
            result="deny",
            reason_code="missing_spiffe_id",
            decision_type="resource_mint",
            payload=payload,
        )
        raise HTTPException(status_code=401, detail="missing x-spiffe-id")
    if not x_spiffe_id.startswith("spiffe://"):
        log_mint_decision(
            result="deny",
            reason_code="invalid_spiffe_id",
            decision_type="resource_mint",
            payload=payload,
        )
        raise HTTPException(status_code=400, detail="invalid x-spiffe-id")

    def _log_resource_mint_decision(**fields):
        log_mint_decision(
            decision_type="resource_mint",
            delegator_spiffe_id=x_spiffe_id,
            **fields,
        )

    if not authorization or not authorization.startswith("Bearer "):
        _log_resource_mint_decision(
            result="deny",
            reason_code="missing_token",
            subject_spiffe_id=x_spiffe_id,
            payload=payload,
        )
        return JSONResponse(status_code=401, content={"error": "denied", "reason": "missing_token"})

    parent_token = authorization.split(" ", 1)[1].strip()
    if not parent_token:
        _log_resource_mint_decision(
            result="deny",
            reason_code="missing_token",
            subject_spiffe_id=x_spiffe_id,
            payload=payload,
        )
        return JSONResponse(status_code=401, content={"error": "denied", "reason": "missing_token"})

    parent_biscuit, parent_claims, token_err = parse_token(parent_token)
    if token_err is not None or parent_claims is None or parent_biscuit is None:
        _log_resource_mint_decision(
            result="deny",
            reason_code="invalid_token",
            subject_spiffe_id=x_spiffe_id,
            payload=payload,
        )
        return JSONResponse(status_code=401, content={"error": "denied", "reason": "invalid_token"})

    if str(parent_claims["subject_spiffe_id"]) != x_spiffe_id:
        _log_resource_mint_decision(
            result="deny",
            reason_code="sub_mismatch",
            subject_spiffe_id=x_spiffe_id,
            payload=payload,
            root_token_id=str(parent_claims["root_token_id"]),
            parent_token_id=str(parent_claims["token_id"]),
            delegation_depth=int(parent_claims["effective_depth"]),
        )
        return JSONResponse(status_code=403, content={"error": "denied", "reason": "sub_mismatch"})

    if int(parent_claims["effective_depth"]) >= M4_MAX_DEPTH:
        _log_resource_mint_decision(
            result="deny",
            reason_code="depth_exceeded",
            subject_spiffe_id=x_spiffe_id,
            payload=payload,
            root_token_id=str(parent_claims["root_token_id"]),
            parent_token_id=str(parent_claims["token_id"]),
            delegation_depth=int(parent_claims["effective_depth"]),
        )
        return JSONResponse(status_code=403, content={"error": "denied", "reason": "depth_exceeded"})

    cleaned, error_response = validate_mint_payload(payload)
    if error_response is not None:
        reason_code = json.loads(error_response.body.decode("utf-8"))["reason"]
        _log_resource_mint_decision(
            result="deny",
            reason_code=reason_code,
            subject_spiffe_id=x_spiffe_id,
            payload=payload,
            root_token_id=str(parent_claims["root_token_id"]),
            parent_token_id=str(parent_claims["token_id"]),
            delegation_depth=int(parent_claims["effective_depth"]),
        )
        return error_response

    canonical_res = canonicalize_resource(cleaned["aud"], cleaned["res"])
    if canonical_res is None:
        _log_resource_mint_decision(
            result="deny",
            reason_code="res",
            subject_spiffe_id=x_spiffe_id,
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=cleaned["res"],
            root_token_id=str(parent_claims["root_token_id"]),
            parent_token_id=str(parent_claims["token_id"]),
            delegation_depth=int(parent_claims["effective_depth"]),
        )
        return JSONResponse(
            status_code=400,
            content={"error": "bad_request", "reason": "res"},
        )

    if str(parent_claims["aud"]) != cleaned["aud"] or str(parent_claims["act"]) != cleaned["act"]:
        _log_resource_mint_decision(
            result="deny",
            reason_code="amplified_authority",
            subject_spiffe_id=x_spiffe_id,
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=canonical_res,
            root_token_id=str(parent_claims["root_token_id"]),
            parent_token_id=str(parent_claims["token_id"]),
            delegation_depth=int(parent_claims["effective_depth"]),
        )
        return JSONResponse(status_code=403, content={"error": "denied", "reason": "amplified_authority"})

    # Single-value attenuation contract in M4 slice: resource cannot be broadened.
    parent_res = str(parent_claims["res"])
    if canonical_res != parent_res:
        store_ok, registry_hit, store_err = registry_has_resource(str(parent_claims["root_token_id"]), canonical_res)
        if not store_ok:
            _log_resource_mint_decision(
                result="deny",
                reason_code="store_unavailable",
                subject_spiffe_id=x_spiffe_id,
                aud=cleaned["aud"],
                act=cleaned["act"],
                res=canonical_res,
                root_token_id=str(parent_claims["root_token_id"]),
                parent_token_id=str(parent_claims["token_id"]),
                delegation_depth=int(parent_claims["effective_depth"]),
                error=store_err,
            )
            return JSONResponse(
                status_code=503,
                content={"error": "denied", "reason": "store_unavailable"},
            )
        if not registry_hit:
            _log_resource_mint_decision(
                result="deny",
                reason_code="registry_miss",
                subject_spiffe_id=x_spiffe_id,
                root_token_id=str(parent_claims["root_token_id"]),
                parent_token_id=str(parent_claims["token_id"]),
                delegation_depth=int(parent_claims["effective_depth"]),
                aud=cleaned["aud"],
                act=cleaned["act"],
                res=canonical_res,
                registry_hit=False,
                error=store_err,
            )
            return JSONResponse(
                status_code=403,
                content={"error": "denied", "reason": "registry_miss"},
            )

        mint_rate_ok, mint_rate_err = consume_mint_rate(
            str(parent_claims["root_token_id"]),
            int(parent_claims["exp"]),
            M4_ROOT_TTL_SECONDS,
        )
        if not mint_rate_ok:
            if mint_rate_err == "mint_rate_exceeded":
                _log_resource_mint_decision(
                    result="deny",
                    reason_code="mint_rate_exceeded",
                    subject_spiffe_id=x_spiffe_id,
                    aud=cleaned["aud"],
                    act=cleaned["act"],
                    res=canonical_res,
                    root_token_id=str(parent_claims["root_token_id"]),
                    parent_token_id=str(parent_claims["token_id"]),
                    delegation_depth=int(parent_claims["effective_depth"]),
                    registry_hit=registry_hit,
                )
                return JSONResponse(
                    status_code=403,
                    content={"error": "denied", "reason": "mint_rate_exceeded"},
                )
            _log_resource_mint_decision(
                result="deny",
                reason_code="store_unavailable",
                subject_spiffe_id=x_spiffe_id,
                aud=cleaned["aud"],
                act=cleaned["act"],
                res=canonical_res,
                root_token_id=str(parent_claims["root_token_id"]),
                parent_token_id=str(parent_claims["token_id"]),
                delegation_depth=int(parent_claims["effective_depth"]),
                registry_hit=registry_hit,
                error=mint_rate_err,
            )
            return JSONResponse(
                status_code=503,
                content={"error": "denied", "reason": "store_unavailable"},
            )
    else:
        registry_hit = True

    policy_input = decision_input(
        "resource_mint",
        x_spiffe_id,
        cleaned["aud"],
        cleaned["act"],
        canonical_res,
        root_token_id=str(parent_claims["root_token_id"]),
        registry_hit=registry_hit,
    )
    ok, fail_response = run_policy_or_fail(policy_input)
    if not ok:
        reason_code = json.loads(fail_response.body.decode("utf-8"))["reason"]
        _log_resource_mint_decision(
            result="deny",
            reason_code=reason_code,
            subject_spiffe_id=x_spiffe_id,
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=canonical_res,
            root_token_id=str(parent_claims["root_token_id"]),
            parent_token_id=str(parent_claims["token_id"]),
            delegation_depth=int(parent_claims["effective_depth"]),
            registry_hit=registry_hit,
        )
        return fail_response

    token_value, expires_at, token_id = append_resource_token(
        parent_biscuit,
        parent_claims,
        x_spiffe_id,
        cleaned["aud"],
        cleaned["act"],
        canonical_res,
    )

    marked, mark_err = mark_capiss_minted_token(token_id, expires_at)
    if not marked:
        _log_resource_mint_decision(
            result="deny",
            reason_code="store_unavailable",
            subject_spiffe_id=x_spiffe_id,
            root_token_id=str(parent_claims["root_token_id"]),
            token_id=token_id,
            parent_token_id=str(parent_claims["token_id"]),
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=canonical_res,
            registry_hit=registry_hit,
            error=mark_err,
        )
        return JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "store_unavailable"},
        )

    _log_resource_mint_decision(
        result="allow",
        reason_code="ok",
        subject_spiffe_id=x_spiffe_id,
        root_token_id=str(parent_claims["root_token_id"]),
        token_id=token_id,
        parent_token_id=str(parent_claims["token_id"]),
        delegation_depth=int(parent_claims["effective_depth"]) + 1,
        aud=cleaned["aud"],
        act=cleaned["act"],
        res=canonical_res,
        registry_hit=registry_hit,
    )

    return {
        "token_type": "biscuit",
        "token": token_value,
        "expires_at": expires_at,
        "issued_to": x_spiffe_id,
        "aud": cleaned["aud"],
        "act": cleaned["act"],
        "res": canonical_res,
        "root_token_id": str(parent_claims["root_token_id"]),
        "token_id": token_id,
        "parent_token_id": str(parent_claims["token_id"]),
        "delegation_depth": int(parent_claims["effective_depth"]) + 1,
    }


# Backward-compatible path used by existing tests. In M4 this maps to root mint.
@app.post("/capabilities/mint")
# DD: DD-106
# Implements: ARCH-004, ARCH-011, ARCH-012
# Title: mint capability issuer compatibility dispatch endpoint
def mint(
    payload: dict | None = None,
    x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id"),
):
    return root_mint(payload=payload, x_spiffe_id=x_spiffe_id)
