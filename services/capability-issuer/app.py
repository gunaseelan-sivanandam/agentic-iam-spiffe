import base64
import json
import os
import time
from urllib import request
from urllib.error import URLError

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from biscuit_auth import Algorithm, BiscuitBuilder, Fact, KeyPair, PrivateKey

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/capiss/allow")
OPA_TIMEOUT_SECONDS = float(os.getenv("OPA_TIMEOUT_SECONDS", "1.0"))
CAPABILITY_TTL_SECONDS = int(os.getenv("CAPABILITY_TTL_SECONDS", "60"))
CAPISS_KEY_DIR = os.getenv("CAPISS_KEY_DIR", "/var/lib/capiss/keys")
CAPISS_KEY_FILE = os.path.join(CAPISS_KEY_DIR, "root_key.b64")
CAPISS_PUBLIC_KEY_FILE = os.path.join(CAPISS_KEY_DIR, "root_public_key.b64")


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


def load_or_create_root_private_key() -> PrivateKey:
    os.makedirs(CAPISS_KEY_DIR, exist_ok=True)
    if os.path.exists(CAPISS_KEY_FILE):
        with open(CAPISS_KEY_FILE, "rb") as handle:
            raw = handle.read()
        return PrivateKey.from_bytes(base64.b64decode(raw), Algorithm.Ed25519)

    keypair = KeyPair()
    private_key = keypair.private_key
    encoded = base64.b64encode(private_key.to_bytes())
    fd = os.open(CAPISS_KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(encoded)
    return private_key


def write_public_key(private_key: PrivateKey) -> None:
    keypair = KeyPair.from_private_key(private_key)
    encoded = base64.b64encode(keypair.public_key.to_bytes())
    fd = os.open(CAPISS_PUBLIC_KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(encoded)


ROOT_PRIVATE_KEY = load_or_create_root_private_key()
write_public_key(ROOT_PRIVATE_KEY)


@app.post("/capabilities/mint")
def mint(
    payload: dict | None = None,
    x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id"),
):
    # Trust boundary: this header is only accepted because the app is isolated on
    # capiss_app_net and only the Envoy ingress can reach it.
    if not x_spiffe_id:
        raise HTTPException(status_code=401, detail="missing x-spiffe-id")
    if not x_spiffe_id.startswith("spiffe://"):
        raise HTTPException(status_code=400, detail="invalid x-spiffe-id")

    if payload is None:
        return JSONResponse(
            status_code=400,
            content={"error": "bad_request", "reason": "body"},
        )

    required_fields = ("aud", "act", "res")
    cleaned = {}
    for field in required_fields:
        if field not in payload:
            return JSONResponse(
                status_code=400,
                content={"error": "bad_request", "reason": field},
            )
        value = payload[field]
        if not isinstance(value, str):
            return JSONResponse(
                status_code=400,
                content={"error": "bad_request", "reason": field},
            )
        value = value.strip()
        if not value:
            return JSONResponse(
                status_code=400,
                content={"error": "bad_request", "reason": field},
            )
        cleaned[field] = value

    input_payload = {
        "sub": x_spiffe_id,
        "aud": cleaned["aud"],
        "act": cleaned["act"],
        "res": cleaned["res"],
    }

    allowed, err = check_opa_allow(input_payload)
    result = "allow" if allowed else "deny"
    print(
        "capability-issuer decision:",
        f"sub={input_payload['sub']}",
        f"aud={input_payload['aud']}",
        f"act={input_payload['act']}",
        f"res={input_payload['res']}",
        f"result={result}",
    )

    if allowed is None:
        return JSONResponse(
            status_code=503,
            content={"error": "denied", "reason": "opa_unavailable"},
        )
    if not allowed:
        return JSONResponse(
            status_code=403,
            content={"error": "denied", "reason": "policy"},
        )

    expires_at = int(time.time()) + CAPABILITY_TTL_SECONDS
    builder = BiscuitBuilder()
    builder.add_fact(Fact(f'sub("{x_spiffe_id}")'))
    builder.add_fact(Fact(f'aud("{cleaned["aud"]}")'))
    builder.add_fact(Fact(f'act("{cleaned["act"]}")'))
    builder.add_fact(Fact(f'res("{cleaned["res"]}")'))
    builder.add_fact(Fact(f"exp({expires_at})"))
    token = builder.build(ROOT_PRIVATE_KEY)
    token_value = token.to_base64() if hasattr(token, "to_base64") else base64.b64encode(token.to_bytes()).decode("utf-8")
    print(
        "capability-issuer mint:",
        f"sub={x_spiffe_id}",
        f"aud={cleaned['aud']}",
        f"act={cleaned['act']}",
        f"res={cleaned['res']}",
        f"expires_at={expires_at}",
    )

    return {
        "token_type": "biscuit",
        "token": token_value,
        "expires_at": expires_at,
        "issued_to": x_spiffe_id,
        "aud": cleaned["aud"],
        "act": cleaned["act"],
        "res": cleaned["res"],
    }
