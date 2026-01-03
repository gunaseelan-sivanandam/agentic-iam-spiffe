import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from cryptography import x509
from cryptography.x509.oid import ExtensionOID

SVID_CERT = os.getenv("SPIFFE_SVID_CERT", "/run/spire/svid/svid.pem")
ALLOWED_CLIENT = os.getenv("ALLOWED_CLIENT_SPIFFE_ID", "spiffe://example.org/agent-a")
SPIFFE_HEADER = "x-spiffe-id"


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
        spiffe_id = self.headers.get(SPIFFE_HEADER)
        print(f"tool-b client SPIFFE ID: {spiffe_id}")
        if not spiffe_id:
            self._send_json(401, {"detail": "missing x-spiffe-id"})
            return False
        if spiffe_id != ALLOWED_CLIENT:
            self._send_json(403, {"detail": "forbidden"})
            return False
        return True

    def do_GET(self):
        if self.path not in ("/health", "/secret"):
            self._send_json(404, {"detail": "not found"})
            return
        if not self._authorize():
            return
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(200, {"secret": "not-yet-protected"})


def main():
    spiffe_id = spiffe_id_from_cert_path(SVID_CERT)
    print(f"tool-b SPIFFE ID: {spiffe_id}")

    httpd = HTTPServer(("0.0.0.0", 8080), ToolBHandler)
    print("tool-b listening on http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
