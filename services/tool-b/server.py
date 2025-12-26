import json
import os
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer

from cryptography import x509
from cryptography.x509.oid import ExtensionOID

SVID_CERT = os.getenv("SPIFFE_SVID_CERT", "/run/spire/svid/svid.pem")
SVID_KEY = os.getenv("SPIFFE_SVID_KEY", "/run/spire/svid/svid.key")
TRUST_BUNDLE = os.getenv("SPIFFE_TRUST_BUNDLE", "/run/spire/svid/bundle.pem")
ALLOWED_CLIENT = os.getenv("ALLOWED_CLIENT_SPIFFE_ID", "spiffe://example.org/agent-a")


def spiffe_id_from_cert_bytes(cert_bytes):
    cert = x509.load_der_x509_certificate(cert_bytes)
    san = cert.extensions.get_extension_for_oid(
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    ).value
    for uri in san.get_values_for_type(x509.UniformResourceIdentifier):
        if uri.startswith("spiffe://"):
            return uri
    return None


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


def client_spiffe_id_from_socket(sock):
    cert_bytes = sock.getpeercert(binary_form=True)
    if cert_bytes:
        return spiffe_id_from_cert_bytes(cert_bytes)
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
        spiffe_id = client_spiffe_id_from_socket(self.connection)
        print(f"tool-b client SPIFFE ID: {spiffe_id}")
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

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=SVID_CERT, keyfile=SVID_KEY)
    context.load_verify_locations(cafile=TRUST_BUNDLE)
    context.verify_mode = ssl.CERT_REQUIRED

    httpd = HTTPServer(("0.0.0.0", 8443), ToolBHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print("tool-b listening on https://0.0.0.0:8443")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
