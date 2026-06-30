from __future__ import annotations

import io
import json

import pytest


class _MockHarness:
    def __init__(self, mod, path: str, payload: object | bytes | None = None, headers: dict[str, str] | None = None):
        self.handler = mod.JiraMcpMockHandler.__new__(mod.JiraMcpMockHandler)
        if isinstance(payload, bytes):
            body = payload
        else:
            body = b"" if payload is None else json.dumps(payload).encode("utf-8")
        self.handler.path = path
        self.handler.headers = {"Content-Length": str(len(body)), **(headers or {})}
        self.handler.rfile = io.BytesIO(body)
        self.handler.wfile = io.BytesIO()
        self.status = None
        self.headers: list[tuple[str, str]] = []
        self.handler.send_response = lambda status: setattr(self, "status", status)
        self.handler.send_header = lambda key, value: self.headers.append((key, value))
        self.handler.end_headers = lambda: None

    def json_body(self) -> dict:
        raw = self.handler.wfile.getvalue().decode("utf-8")
        return json.loads(raw) if raw else {}


# UT: UT-202
# Test Description: Verifies jira-mcp-mock has broad IAM and NAS fixtures for protected-path narrowing proof.
# Precondition: jira-mcp-mock module is loaded with seeded fixtures.
# Expected Output: Fixture state contains both IAM and NAS projects, many IAM issues, and same/cross-project epics.
# Covers DD: DD-601
@pytest.mark.invariant
def test_mock_contains_broad_iam_and_nas_fixtures(jiramcp_mock_module, guard):
    mod = jiramcp_mock_module
    guard.premise("mock module loaded", mod is not None)
    data = guard.exercise(
        "inspect seeded fixtures",
        lambda: {
            "projects": sorted(mod.PROJECTS),
            "iam_count": len([key for key in mod.ISSUES if key.startswith("IAM-")]),
            "nas_count": len([key for key in mod.ISSUES if key.startswith("NAS-")]),
            "iam_epic": mod.ISSUES["IAM-101"]["issue_type"],
            "nas_epic": mod.ISSUES["NAS-101"]["issue_type"],
        },
    )
    guard.outcome("IAM and NAS projects present", data["projects"] == ["IAM", "NAS"])
    guard.outcome("IAM has summary-bound excess data", data["iam_count"] > 75)
    guard.outcome("NAS fixtures present", data["nas_count"] >= 4)
    guard.outcome("same and cross project epics present", data["iam_epic"] == "Epic" and data["nas_epic"] == "Epic")


# UT: UT-203
# Test Description: Verifies jira-mcp-mock request logs record path, project, status, correlation, and gateway marker.
# Precondition: jira-mcp-mock module is loaded and request log is empty.
# Expected Output: Recorded request includes evidence fields used by E2E proof.
# Covers DD: DD-602
@pytest.mark.invariant
def test_mock_request_log_records_gateway_evidence(jiramcp_mock_module, guard):
    mod = jiramcp_mock_module
    guard.premise("mock module loaded", mod is not None)
    guard.exercise("clear request log", mod.REQUEST_LOG.clear)
    guard.exercise(
        "record request",
        lambda: mod.record_request(
            "GET",
            "/rest/api/3/project/IAM/summary",
            200,
            headers={"X-Correlation-ID": "corr-1", "X-M5-Gateway": "jira-mcp-gateway"},
        ),
    )
    entry = mod.REQUEST_LOG[0]
    guard.outcome("project recorded", entry["project_key"] == "IAM")
    guard.outcome("status recorded", entry["status"] == 200)
    guard.outcome("correlation recorded", entry["correlation_id"] == "corr-1")
    guard.outcome("gateway marker recorded", entry["gateway_marker"] == "jira-mcp-gateway")


# UT: UT-210
# Test Description: Verifies jira-mcp-mock GET routes expose health, evidence, breadth, summary, issue, and 404 behavior.
# Precondition: mock module is loaded and handler is exercised with in-memory response streams.
# Expected Output: GET routes return deterministic fixtures and record upstream evidence for Jira paths.
# Covers DD: DD-603, DD-604
@pytest.mark.boundary
def test_mock_get_routes(jiramcp_mock_module, guard):
    mod = jiramcp_mock_module
    guard.premise("mock module loaded", mod is not None)
    guard.exercise("reset state", lambda: (mod.REQUEST_LOG.clear(), mod.CREATED.clear(), mod._seed()))

    health = _MockHarness(mod, "/health")
    breadth = _MockHarness(mod, "/__test__/breadth")
    summary = _MockHarness(mod, "/rest/api/3/project/IAM/summary", headers={"X-Correlation-ID": "corr", "X-M5-Gateway": "jira-mcp-gateway"})
    missing_project = _MockHarness(mod, "/rest/api/3/project/ZZZ/summary")
    issue = _MockHarness(mod, "/rest/api/3/issue/IAM-101")
    missing_issue = _MockHarness(mod, "/rest/api/3/issue/IAM-999999")
    not_found = _MockHarness(mod, "/bad")

    guard.exercise("call GET routes", lambda: [h.handler.do_GET() for h in (health, breadth, summary, missing_project, issue, missing_issue, not_found)])
    guard.outcome("health route passes", health.status == 200 and health.json_body()["status"] == "ok")
    guard.outcome("breadth route shows both projects", breadth.json_body()["projects"] == ["IAM", "NAS"])
    guard.outcome("summary returns many IAM issues", summary.status == 200 and summary.json_body()["project"]["key"] == "IAM" and len(summary.json_body()["issues"]) > 50)
    guard.outcome("missing project and issue return 404", missing_project.status == 404 and missing_issue.status == 404 and not_found.status == 404)
    guard.outcome("issue response has Jira fields", issue.status == 200 and issue.json_body()["fields"]["issuetype"]["name"] == "Epic")
    guard.outcome("Jira GETs recorded", len(mod.REQUEST_LOG) >= 3)


# UT: UT-211
# Test Description: Verifies jira-mcp-mock POST routes reset, inject failures, create stories, and reject bad requests.
# Precondition: mock module is loaded and handler is exercised with in-memory request/response streams.
# Expected Output: Story creation mutates deterministic fixture state and failure toggles are one-shot.
# Covers DD: DD-605
@pytest.mark.boundary
def test_mock_post_routes(jiramcp_mock_module, guard):
    mod = jiramcp_mock_module
    guard.premise("mock module loaded", mod is not None)
    reset = _MockHarness(mod, "/__test__/reset")
    guard.exercise("reset through POST", reset.handler.do_POST)

    fail_arm = _MockHarness(mod, "/__test__/fail_next_create")
    guard.exercise("arm create failure", fail_arm.handler.do_POST)
    create_payload = {"fields": {"project": {"key": "IAM"}, "summary": "s", "description": {"type": "doc"}, "issuetype": {"name": "Story"}, "parent": {"key": "IAM-101"}}}
    failed_create = _MockHarness(mod, "/rest/api/3/issue", create_payload, {"X-Correlation-ID": "corr"})
    guard.exercise("create fails once", failed_create.handler.do_POST)
    created = _MockHarness(mod, "/rest/api/3/issue", create_payload, {"X-Correlation-ID": "corr"})
    guard.exercise("create succeeds after one-shot failure", created.handler.do_POST)
    bad_json = _MockHarness(mod, "/rest/api/3/issue", b"{")
    guard.exercise("bad JSON rejected", bad_json.handler.do_POST)
    bad_project = _MockHarness(mod, "/rest/api/3/issue", {"fields": {"project": {"key": "BAD"}}})
    guard.exercise("bad project rejected", bad_project.handler.do_POST)
    summary_fail_arm = _MockHarness(mod, "/__test__/fail_next_summary")
    guard.exercise("arm summary failure", summary_fail_arm.handler.do_POST)
    failed_summary = _MockHarness(mod, "/rest/api/3/project/IAM/summary")
    guard.exercise("summary fails once", failed_summary.handler.do_GET)
    not_found = _MockHarness(mod, "/bad")
    guard.exercise("unknown POST rejected", not_found.handler.do_POST)

    created_body = created.json_body()
    guard.outcome("reset route succeeded", reset.status == 200)
    guard.outcome("one-shot failure returned 503", failed_create.status == 503)
    guard.outcome("story create returned key", created.status == 201 and created_body["key"].startswith("IAM-"))
    guard.outcome("created fixture recorded parent epic", mod.ISSUES[created_body["key"]]["epic_key"] == "IAM-101")
    guard.outcome("summary failure toggle is one-shot", summary_fail_arm.status == 200 and failed_summary.status == 503 and mod.FAIL_NEXT_SUMMARY is False)
    guard.outcome("invalid create requests rejected", bad_json.status == 400 and bad_project.status == 400 and not_found.status == 404)
