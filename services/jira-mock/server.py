import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit


ISSUES = {
    "IAM-1": {
        "id": "10001",
        "key": "IAM-1",
        "fields": {
            "project": {"key": "IAM"},
            "summary": "Allowed IAM issue one",
            "description": "Initial IAM issue one description",
        },
    },
    "IAM-2": {
        "id": "10002",
        "key": "IAM-2",
        "fields": {
            "project": {"key": "IAM"},
            "summary": "Allowed IAM issue two",
            "description": "Initial IAM issue two description",
        },
    },
    "NAS-1": {
        "id": "20001",
        "key": "NAS-1",
        "fields": {
            "project": {"key": "NAS"},
            "summary": "Non-allowed NAS issue one",
            "description": "Initial NAS issue one description",
        },
    },
    "NAS-2": {
        "id": "20002",
        "key": "NAS-2",
        "fields": {
            "project": {"key": "NAS"},
            "summary": "Non-allowed NAS issue two",
            "description": "Initial NAS issue two description",
        },
    },
    "IAM-999": {
        "id": "90999",
        "key": "IAM-999",
        "fields": {
            "project": {"key": "NAS"},
            "summary": "Mismatched upstream project fixture",
            "description": "Initial mismatched fixture description",
        },
    },
}

REQUEST_LOG: list[dict[str, object]] = []


# DD: DD-401
# Implements: ARCH-024
# Title: iso_utc_now jira-mock request timestamp helper
def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# DD: DD-402
# Implements: ARCH-024
# Title: record_issue_request jira-mock upstream request log writer
def record_issue_request(issue_key: str, status: int, method: str = "GET") -> None:
    REQUEST_LOG.append(
        {
            "timestamp": iso_utc_now(),
            "method": method,
            "path": f"/rest/api/3/issue/{issue_key}",
            "issue_key": issue_key,
            "status": status,
        }
    )


class JiraMockHandler(BaseHTTPRequestHandler):
    server_version = "jira-mock"

    # DD: DD-403
    # Implements: ARCH-024
    # Title: JiraMockHandler.log_message jira-mock access log adapter
    def log_message(self, fmt, *args):
        return

    # DD: DD-404
    # Implements: ARCH-024
    # Title: JiraMockHandler._send_json jira-mock JSON response helper
    def _send_json(self, status_code: int, payload: dict[str, object]):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # DD: DD-405
    # Implements: ARCH-024
    # Title: JiraMockHandler.do_GET jira-mock issue and test-log routes
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/__test__/requests":
            self._send_json(200, {"requests": REQUEST_LOG})
            return
        if path.startswith("/rest/api/3/issue/"):
            issue_key = path.removeprefix("/rest/api/3/issue/")
            issue = ISSUES.get(issue_key)
            status = 200 if issue is not None else 404
            record_issue_request(issue_key, status, "GET")
            if issue is None:
                self._send_json(404, {"error": "not_found"})
                return
            self._send_json(200, issue)
            return
        self._send_json(404, {"detail": "not found"})

    # DD: DD-408
    # Implements: ARCH-024, ARCH-026
    # Title: JiraMockHandler.do_PUT jira-mock description update route
    def do_PUT(self):
        path = urlsplit(self.path).path
        if path.startswith("/rest/api/3/issue/"):
            issue_key = path.removeprefix("/rest/api/3/issue/")
            issue = ISSUES.get(issue_key)
            if issue is None:
                record_issue_request(issue_key, 404, "PUT")
                self._send_json(404, {"error": "not_found"})
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                record_issue_request(issue_key, 400, "PUT")
                self._send_json(400, {"error": "bad_request"})
                return

            description = payload.get("fields", {}).get("description") if isinstance(payload, dict) else None
            if not isinstance(description, dict):
                record_issue_request(issue_key, 400, "PUT")
                self._send_json(400, {"error": "bad_request"})
                return

            issue["fields"]["description"] = description
            record_issue_request(issue_key, 204, "PUT")
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self._send_json(404, {"detail": "not found"})

    # DD: DD-406
    # Implements: ARCH-024
    # Title: JiraMockHandler.do_POST jira-mock request-log reset route
    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/__test__/reset":
            REQUEST_LOG.clear()
            self._send_json(200, {"status": "reset"})
            return
        self._send_json(404, {"detail": "not found"})


# DD: DD-407
# Implements: ARCH-024
# Title: main jira-mock HTTP server bootstrap
def main():
    httpd = HTTPServer(("0.0.0.0", 8080), JiraMockHandler)
    print("jira-mock listening on http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
