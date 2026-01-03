import json
import os
from urllib import request
from urllib.error import URLError

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/capiss/allow")
OPA_TIMEOUT_SECONDS = float(os.getenv("OPA_TIMEOUT_SECONDS", "1.0"))


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


@app.post("/capabilities/mint")
def mint(x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id")):
    # Trust boundary: this header is only accepted because the app is isolated on
    # capiss_app_net and only the Envoy ingress can reach it.
    if not x_spiffe_id:
        raise HTTPException(status_code=401, detail="missing x-spiffe-id")
    if not x_spiffe_id.startswith("spiffe://"):
        raise HTTPException(status_code=400, detail="invalid x-spiffe-id")

    input_payload = {
        "sub": x_spiffe_id,
        "aud": "tool-b",
        "act": "read",
        "res": "/secret",
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

    return {
        "token_type": "biscuit",
        "token": "",
        "expires_at": None,
        "issued_to": x_spiffe_id,
        "aud": "tool-b",
        "act": "read",
        "res": "/secret",
    }
