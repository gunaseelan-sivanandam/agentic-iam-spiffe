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


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event_type: str, **fields: object) -> None:
    payload = {
        "event_type": event_type,
        "timestamp": iso_utc_now(),
        **fields,
    }
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True), flush=True)


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


def write_public_key(private_key: PrivateKey) -> None:
    keypair = KeyPair.from_private_key(private_key)
    encoded = base64.b64encode(keypair.public_key.to_bytes())
    fd = os.open(CAPISS_PUBLIC_KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(encoded)


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


def canonicalize_resource(aud: str, res: str) -> str | None:
    if aud != "tool-b":
        return None

    # Keep /secret compatibility for existing tests.
    if res == "/secret":
        return "/secret"

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


def extract_chain_claims(biscuit: Biscuit) -> list[dict[str, str | int]]:
    count = biscuit.block_count()
    chain: list[dict[str, str | int]] = []
    for idx in range(count):
        block = parse_block_source(biscuit.block_source(idx))
        if "delegation_depth" not in block:
            block["delegation_depth"] = idx
        chain.append(block)
    return chain


def verify_and_extract_chain(biscuit: Biscuit) -> tuple[dict[str, str | int] | None, str | None]:
    chain = extract_chain_claims(biscuit)
    if not chain:
        return None, "invalid_chain"

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

        if aud != prev_aud or act != prev_act or res != prev_res:
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
    return final, None


def parse_token(token_value: str) -> tuple[Biscuit | None, dict[str, str | int] | None, str | None]:
    try:
        biscuit = Biscuit.from_base64(token_value, ROOT_PUBLIC_KEY)
    except (BiscuitSerializationError, BiscuitValidationError, BiscuitBlockError, Exception):
        return None, None, "invalid_token"

    claims, err = verify_and_extract_chain(biscuit)
    if err is not None:
        return None, None, err
    return biscuit, claims, None


def ensure_root_budget(root_token_id: str, root_exp: int, initial_res: str) -> tuple[bool, str]:
    ttl = max(1, root_exp - int(time.time()))
    budget_key = f"m4:budget:{root_token_id}"
    registry_key = f"m4:registry:{root_token_id}"
    try:
        client = get_redis()
        pipe = client.pipeline(transaction=True)
        pipe.set(budget_key, M4_DEFAULT_BUDGET, ex=ttl)
        pipe.sadd(registry_key, initial_res)
        pipe.expire(registry_key, ttl)
        pipe.execute()
        return True, ""
    except redis.RedisError as exc:
        return False, str(exc)


def mark_capiss_minted_token(token_id: str, exp: int) -> tuple[bool, str]:
    ttl = max(1, exp - int(time.time()))
    mint_key = f"m4:capiss_minted:{token_id}"
    try:
        client = get_redis()
        client.set(mint_key, "1", ex=ttl)
        return True, ""
    except redis.RedisError as exc:
        return False, str(exc)


def registry_has_resource(root_token_id: str, res: str) -> tuple[bool, bool, str]:
    registry_key = f"m4:registry:{root_token_id}"
    try:
        client = get_redis()
        script = "return redis.call('SISMEMBER', KEYS[1], ARGV[1])"
        result = client.eval(script, 1, registry_key, res)
        return True, bool(int(result)), ""
    except redis.RedisError as exc:
        return False, False, str(exc)


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
            policy_id="capiss.allow.v2",
            policy_hash="sha256:capiss-policy-v2",
        )
        return False, JSONResponse(
            status_code=403,
            content={"error": "denied", "reason": "policy"},
        )
    return True, None


@app.post("/capabilities/root-mint")
def root_mint(
    payload: dict | None = None,
    x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id"),
):
    if not x_spiffe_id:
        raise HTTPException(status_code=401, detail="missing x-spiffe-id")
    if not x_spiffe_id.startswith("spiffe://"):
        raise HTTPException(status_code=400, detail="invalid x-spiffe-id")

    cleaned, error_response = validate_mint_payload(payload)
    if error_response is not None:
        return error_response

    canonical_res = canonicalize_resource(cleaned["aud"], cleaned["res"])
    if canonical_res is None:
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
        return fail_response

    token_value, expires_at, root_token_id, token_id = mint_root_biscuit(
        x_spiffe_id,
        cleaned["aud"],
        cleaned["act"],
        canonical_res,
    )

    ready, redis_err = ensure_root_budget(root_token_id, expires_at, canonical_res)
    if not ready:
        log_event(
            "capiss_mint_decision",
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
            policy_id="capiss.allow.v2",
            policy_hash="sha256:capiss-policy-v2",
        )
        return JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "store_unavailable"},
        )

    marked, mark_err = mark_capiss_minted_token(token_id, expires_at)
    if not marked:
        log_event(
            "capiss_mint_decision",
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
            policy_id="capiss.allow.v2",
            policy_hash="sha256:capiss-policy-v2",
        )
        return JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "store_unavailable"},
        )

    log_event(
        "capiss_mint_decision",
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
        registry_hit=True,
        policy_id="capiss.allow.v2",
        policy_hash="sha256:capiss-policy-v2",
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
def resource_mint(
    payload: dict | None = None,
    x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id"),
    authorization: str | None = Header(default=None, alias="authorization"),
):
    if not x_spiffe_id:
        raise HTTPException(status_code=401, detail="missing x-spiffe-id")
    if not x_spiffe_id.startswith("spiffe://"):
        raise HTTPException(status_code=400, detail="invalid x-spiffe-id")
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "denied", "reason": "missing_token"})

    parent_token = authorization.split(" ", 1)[1].strip()
    if not parent_token:
        return JSONResponse(status_code=401, content={"error": "denied", "reason": "missing_token"})

    parent_biscuit, parent_claims, token_err = parse_token(parent_token)
    if token_err is not None or parent_claims is None or parent_biscuit is None:
        return JSONResponse(status_code=401, content={"error": "denied", "reason": "invalid_token"})

    if str(parent_claims["subject_spiffe_id"]) != x_spiffe_id:
        return JSONResponse(status_code=403, content={"error": "denied", "reason": "sub_mismatch"})

    if int(parent_claims["effective_depth"]) >= M4_MAX_DEPTH:
        return JSONResponse(status_code=403, content={"error": "denied", "reason": "depth_exceeded"})

    cleaned, error_response = validate_mint_payload(payload)
    if error_response is not None:
        return error_response

    canonical_res = canonicalize_resource(cleaned["aud"], cleaned["res"])
    if canonical_res is None:
        return JSONResponse(
            status_code=400,
            content={"error": "bad_request", "reason": "res"},
        )

    if str(parent_claims["aud"]) != cleaned["aud"] or str(parent_claims["act"]) != cleaned["act"]:
        return JSONResponse(status_code=403, content={"error": "denied", "reason": "amplified_authority"})

    # Single-value attenuation contract in M4 slice: resource cannot be broadened.
    parent_res = str(parent_claims["res"])
    if canonical_res != parent_res:
        store_ok, registry_hit, store_err = registry_has_resource(str(parent_claims["root_token_id"]), canonical_res)
        if not store_ok:
            return JSONResponse(
                status_code=503,
                content={"error": "denied", "reason": "store_unavailable"},
            )
        if not registry_hit:
            log_event(
                "capiss_mint_decision",
                result="deny",
                reason_code="registry_miss",
                decision_type="resource_mint",
                subject_spiffe_id=x_spiffe_id,
                root_token_id=str(parent_claims["root_token_id"]),
                parent_token_id=str(parent_claims["token_id"]),
                aud=cleaned["aud"],
                act=cleaned["act"],
                res=canonical_res,
                registry_hit=False,
                error=store_err,
                policy_id="capiss.allow.v2",
                policy_hash="sha256:capiss-policy-v2",
            )
            return JSONResponse(
                status_code=403,
                content={"error": "denied", "reason": "registry_miss"},
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
        log_event(
            "capiss_mint_decision",
            result="deny",
            reason_code="store_unavailable",
            decision_type="resource_mint",
            subject_spiffe_id=x_spiffe_id,
            root_token_id=str(parent_claims["root_token_id"]),
            token_id=token_id,
            parent_token_id=str(parent_claims["token_id"]),
            aud=cleaned["aud"],
            act=cleaned["act"],
            res=canonical_res,
            registry_hit=registry_hit,
            error=mark_err,
            policy_id="capiss.allow.v2",
            policy_hash="sha256:capiss-policy-v2",
        )
        return JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "store_unavailable"},
        )

    log_event(
        "capiss_mint_decision",
        result="allow",
        reason_code="ok",
        decision_type="resource_mint",
        subject_spiffe_id=x_spiffe_id,
        root_token_id=str(parent_claims["root_token_id"]),
        token_id=token_id,
        parent_token_id=str(parent_claims["token_id"]),
        delegation_depth=int(parent_claims["effective_depth"]) + 1,
        aud=cleaned["aud"],
        act=cleaned["act"],
        res=canonical_res,
        registry_hit=registry_hit,
        policy_id="capiss.allow.v2",
        policy_hash="sha256:capiss-policy-v2",
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
def mint(
    payload: dict | None = None,
    x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id"),
):
    return root_mint(payload=payload, x_spiffe_id=x_spiffe_id)
