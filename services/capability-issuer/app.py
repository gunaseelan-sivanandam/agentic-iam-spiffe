from fastapi import FastAPI, Header, HTTPException

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/capabilities/mint")
def mint(x_spiffe_id: str | None = Header(default=None, alias="x-spiffe-id")):
    # Trust boundary: this header is only accepted because the app is isolated on
    # capiss_app_net and only the Envoy ingress can reach it.
    if not x_spiffe_id:
        raise HTTPException(status_code=401, detail="missing x-spiffe-id")

    return {
        "token_type": "biscuit",
        "token": "",
        "expires_at": None,
        "issued_to": x_spiffe_id,
        "aud": "tool-b",
        "act": "read",
        "res": "/secret",
    }
