import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit


PROJECTS = {
    "IAM": {"key": "IAM", "name": "Identity Access Management"},
    "NAS": {"key": "NAS", "name": "Network Access Services"},
}
ISSUES: dict[str, dict[str, object]] = {}
CREATED: list[dict[str, object]] = []
REQUEST_LOG: list[dict[str, object]] = []
FAIL_NEXT_CREATE = False
FAIL_NEXT_SUMMARY = False


def _seed() -> None:
    ISSUES.clear()
    for i in range(1, 63):
        ISSUES[f"IAM-{i}"] = {
            "key": f"IAM-{i}",
            "summary": f"IAM story {i}",
            "status": "To Do" if i % 2 else "In Progress",
            "issue_type": "Story",
            "epic_key": "IAM-101" if i <= 5 else None,
            "description": f"Hidden IAM description {i}",
            "comments": [{"body": "hidden"}],
            "assignee": {"displayName": "Hidden User"},
            "sprint": "Hidden Sprint",
            "board": "Hidden Board",
            "raw_jql": "project = IAM",
            "self": f"https://example.atlassian.net/rest/api/3/issue/IAM-{i}",
        }
    for i in range(101, 131):
        ISSUES[f"IAM-{i}"] = {
            "key": f"IAM-{i}",
            "summary": f"IAM epic {i}",
            "status": "To Do",
            "issue_type": "Epic",
            "description": "Hidden epic description",
            "comments": [{"body": "hidden"}],
        }
    ISSUES["IAM-900"] = {
        "key": "IAM-900",
        "summary": "Same-project non-epic fixture",
        "status": "To Do",
        "issue_type": "Task",
    }
    for i in range(1, 4):
        ISSUES[f"NAS-{i}"] = {
            "key": f"NAS-{i}",
            "summary": f"NAS issue {i}",
            "status": "To Do",
            "issue_type": "Story",
            "description": f"Hidden NAS description {i}",
        }
    ISSUES["NAS-101"] = {
        "key": "NAS-101",
        "summary": "NAS epic",
        "status": "To Do",
        "issue_type": "Epic",
    }


_seed()


# DD: DD-601
# Implements: ARCH-031
# Title: iso_utc_now jira-mcp-mock request timestamp helper
def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# DD: DD-602
# Implements: ARCH-031
# Title: record_request jira-mcp-mock upstream request log writer
def record_request(method: str, path: str, status: int, body: object | None = None, headers: dict[str, str] | None = None) -> None:
    key = ""
    project_key = ""
    parts = path.strip("/").split("/")
    if parts[-1].startswith(("IAM-", "NAS-")):
        key = parts[-1]
        project_key = key.split("-", 1)[0]
    elif "project" in parts:
        idx = parts.index("project")
        if idx + 1 < len(parts):
            project_key = parts[idx + 1]
    REQUEST_LOG.append(
        {
            "timestamp": iso_utc_now(),
            "method": method,
            "path": path,
            "project_key": project_key,
            "issue_key": key,
            "status": status,
            "correlation_id": (headers or {}).get("X-Correlation-ID", ""),
            "gateway_marker": (headers or {}).get("X-M5-Gateway", ""),
            "authorization_present": "Authorization" in (headers or {}),
            "body": body if isinstance(body, dict) else None,
        }
    )


def _issue_response(issue: dict[str, object]) -> dict[str, object]:
    key = str(issue["key"])
    return {
        "key": key,
        "self": f"http://jira-mcp-mock:8080/rest/api/3/issue/{key}",
        "fields": {
            "project": {"key": key.split("-", 1)[0]},
            "summary": issue.get("summary"),
            "issuetype": {"name": issue.get("issue_type")},
            "status": {"name": issue.get("status")},
            "description": issue.get("description"),
            "comment": {"comments": issue.get("comments", [])},
            "assignee": issue.get("assignee"),
        },
    }


class JiraMcpMockHandler(BaseHTTPRequestHandler):
    server_version = "jira-mcp-mock"

    # DD: DD-603
    # Implements: ARCH-031
    # Title: JiraMcpMockHandler.log_message access log adapter
    def log_message(self, fmt, *args):
        return

    def _send_json(self, status: int, payload: dict[str, object]):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # DD: DD-604
    # Implements: ARCH-031
    # Title: JiraMcpMockHandler.do_GET summary issue and test routes
    def do_GET(self):
        global FAIL_NEXT_SUMMARY
        path = urlsplit(self.path).path
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/__test__/requests":
            self._send_json(200, {"requests": REQUEST_LOG})
            return
        if path == "/__test__/created":
            self._send_json(200, {"created": CREATED})
            return
        if path == "/__test__/breadth":
            self._send_json(200, {"projects": sorted(PROJECTS), "iam_count": len([k for k in ISSUES if k.startswith("IAM-")]), "nas_count": len([k for k in ISSUES if k.startswith("NAS-")])})
            return
        if path.startswith("/rest/api/3/project/") and path.endswith("/summary"):
            project_key = path.split("/")[-2]
            if FAIL_NEXT_SUMMARY:
                FAIL_NEXT_SUMMARY = False
                record_request("GET", path, 503, headers=dict(self.headers))
                self._send_json(503, {"error": "injected_summary_failure"})
                return
            project = PROJECTS.get(project_key)
            status = 200 if project else 404
            record_request("GET", path, status, headers=dict(self.headers))
            if not project:
                self._send_json(404, {"error": "not_found"})
                return
            issues = [issue for key, issue in sorted(ISSUES.items()) if key.startswith(f"{project_key}-")]
            self._send_json(200, {"project": {**project, "issue_count": len(issues)}, "issues": issues})
            return
        if path.startswith("/rest/api/3/issue/"):
            issue_key = path.removeprefix("/rest/api/3/issue/")
            issue = ISSUES.get(issue_key)
            status = 200 if issue else 404
            record_request("GET", path, status, headers=dict(self.headers))
            if not issue:
                self._send_json(404, {"error": "not_found"})
                return
            self._send_json(200, _issue_response(issue))
            return
        self._send_json(404, {"detail": "not found"})

    # DD: DD-605
    # Implements: ARCH-031
    # Title: JiraMcpMockHandler.do_POST story create and test routes
    def do_POST(self):
        global FAIL_NEXT_CREATE, FAIL_NEXT_SUMMARY
        path = urlsplit(self.path).path
        if path == "/__test__/reset":
            REQUEST_LOG.clear()
            CREATED.clear()
            _seed()
            FAIL_NEXT_CREATE = False
            FAIL_NEXT_SUMMARY = False
            self._send_json(200, {"status": "reset"})
            return
        if path == "/__test__/fail_next_create":
            FAIL_NEXT_CREATE = True
            self._send_json(200, {"status": "armed"})
            return
        if path == "/__test__/fail_next_summary":
            FAIL_NEXT_SUMMARY = True
            self._send_json(200, {"status": "armed"})
            return
        if path == "/rest/api/3/issue":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                record_request("POST", path, 400, headers=dict(self.headers))
                self._send_json(400, {"error": "bad_request"})
                return
            if FAIL_NEXT_CREATE:
                FAIL_NEXT_CREATE = False
                record_request("POST", path, 503, payload, dict(self.headers))
                self._send_json(503, {"error": "injected_create_failure"})
                return
            fields = payload.get("fields", {}) if isinstance(payload, dict) else {}
            project = fields.get("project", {}) if isinstance(fields, dict) else {}
            project_key = project.get("key") if isinstance(project, dict) else None
            if project_key not in PROJECTS:
                record_request("POST", path, 400, payload, dict(self.headers))
                self._send_json(400, {"error": "bad_project"})
                return
            next_id = 1000 + len(CREATED) + 1
            key = f"{project_key}-{next_id}"
            created = {"key": key, "self": f"http://jira-mcp-mock:8080/rest/api/3/issue/{key}", "fields": fields}
            CREATED.append(created)
            ISSUES[key] = {
                "key": key,
                "summary": fields.get("summary"),
                "status": "To Do",
                "issue_type": "Story",
                "epic_key": (fields.get("parent") or {}).get("key") if isinstance(fields.get("parent"), dict) else None,
                "description": fields.get("description"),
            }
            record_request("POST", path, 201, payload, dict(self.headers))
            self._send_json(201, {"id": str(next_id), "key": key, "self": created["self"]})
            return
        self._send_json(404, {"detail": "not found"})


# DD: DD-606
# Implements: ARCH-031
# Title: main jira-mcp-mock HTTP server bootstrap
def main():
    httpd = HTTPServer(("0.0.0.0", 8080), JiraMcpMockHandler)
    print("jira-mcp-mock listening on http://0.0.0.0:8080")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
