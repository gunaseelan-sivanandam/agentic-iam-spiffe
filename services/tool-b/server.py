import base64
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from cryptography import x509
from cryptography.x509.oid import ExtensionOID
from biscuit_auth import (
    Algorithm,
    AuthorizerBuilder,
    Biscuit,
    BiscuitBlockError,
    BiscuitSerializationError,
    BiscuitValidationError,
    AuthorizationError,
    Policy,
    PublicKey,
)

SVID_CERT = os.getenv("SPIFFE_SVID_CERT", "/run/spire/svid/svid.pem")
SPIFFE_HEADER = "x-spiffe-id"
CAPISS_PUBLIC_KEY_PATH = os.getenv(
    "CAPISS_PUBLIC_KEY_PATH", "/var/lib/capiss/keys/root_public_key.b64"
)
REQUIRED_AUD = "tool-b"
REQUIRED_ACT = "read"
REQUIRED_RES = "/secret"


def spiffe_id_from_cert_path(path):
    with open(path, "rb") as handle:
        cert = x509.load_pem_x509_certificate(handle.read())
    san = cert.extensions.get_extension_for_oid(
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    ).value
    for uri in san.get_values_for_type(x509.UniformResourceIdentifier):
        if uri.startswith("spiffe://"):
            return uri
    return None


_CAPISS_PUBLIC_KEY = None


def load_capiss_public_key():
    # Trust bootstrap: issuer public key is provided via configured volume.
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


def policy_allows(biscuit, source, parameters=None):
    builder = AuthorizerBuilder()
    builder.add_policy(Policy(source, parameters=parameters or {}))
    try:
        builder.build(biscuit).authorize()
        return True
    except AuthorizationError:
        return False


def verify_biscuit(token_value, spiffe_id):
    public_key = load_capiss_public_key()
    if public_key is None:
        return False, "issuer_key_unavailable"
    try:
        biscuit = Biscuit.from_base64(token_value, public_key)
    except (BiscuitSerializationError, BiscuitValidationError, BiscuitBlockError, Exception):
        return False, "invalid_token"

    now = int(time.time())
    allow_policy = (
        f'allow if sub({{sub}}), aud("{REQUIRED_AUD}"), '
        f'act("{REQUIRED_ACT}"), res("{REQUIRED_RES}"), exp($t), '
        "$t > {now}"
    )
    if policy_allows(biscuit, allow_policy, {"sub": spiffe_id, "now": now}):
        return True, ""

    if not policy_allows(biscuit, "allow if sub({sub})", {"sub": spiffe_id}):
        return False, "sub_mismatch"
    if not policy_allows(biscuit, f'allow if aud("{REQUIRED_AUD}")'):
        return False, "insufficient_authority"
    if not policy_allows(biscuit, f'allow if act("{REQUIRED_ACT}")'):
        return False, "insufficient_authority"
    if not policy_allows(biscuit, f'allow if res("{REQUIRED_RES}")'):
        return False, "insufficient_authority"
    if not policy_allows(biscuit, "allow if exp($t), $t > {now}", {"now": now}):
        return False, "expired"

    return False, "invalid_token"


class ToolBHandler(BaseHTTPRequestHandler):
    server_version = "tool-b"

    def log_message(self, format, *args):
        return

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorize(self):
        # Identity-only access is denied; capability token is required for /secret.
        spiffe_id = self.headers.get(SPIFFE_HEADER)
        if not spiffe_id:
            self._send_json(401, {"error": "denied", "reason": "missing_spiffe_id"})
            return False

        authz = self.headers.get("Authorization")
        if not authz or not authz.startswith("Bearer "):
            self._send_json(401, {"error": "denied", "reason": "missing_token"})
            print(f"tool-b decision: sub={spiffe_id} result=deny reason=missing_token")
            return False
        token_value = authz.split(" ", 1)[1].strip()
        if not token_value:
            self._send_json(401, {"error": "denied", "reason": "missing_token"})
            print(f"tool-b decision: sub={spiffe_id} result=deny reason=missing_token")
            return False

        # Capability enforcement: sub must match x-spiffe-id and be scoped to aud/act/res.
        allowed, reason = verify_biscuit(token_value, spiffe_id)
        if not allowed:
            status = 401 if reason in ("invalid_token", "issuer_key_unavailable") else 403
            self._send_json(status, {"error": "denied", "reason": reason})
            print(f"tool-b decision: sub={spiffe_id} result=deny reason={reason}")
            return False
        print(f"tool-b decision: sub={spiffe_id} result=allow")
        return True

    def do_GET(self):
        if self.path not in ("/health", "/secret"):
            self._send_json(404, {"detail": "not found"})
            return
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if not self._authorize():
            return
        self._send_json(200, {"secret": "super sensitive demo secret"})


def main():
    spiffe_id = spiffe_id_from_cert_path(SVID_CERT)
    print(f"tool-b SPIFFE ID: {spiffe_id}")

    httpd = HTTPServer(("0.0.0.0", 8080), ToolBHandler)
    print("tool-b listening on http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
