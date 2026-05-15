from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from tests.unit.shared.loaders import REPO_ROOT, load_module_from_path


CAPISS_APP_PATH = Path(REPO_ROOT, "services", "capability-issuer", "app.py")
TOOLB_SERVER_PATH = Path(REPO_ROOT, "services", "tool-b", "server.py")
JIRATOOL_SERVER_PATH = Path(REPO_ROOT, "services", "jira-tool", "server.py")
SHARED_ENFORCEMENT_PATH = Path(REPO_ROOT, "services", "shared", "enforcement_contract.py")


@dataclass
class GuardEvent:
    phase: str
    step: str
    ok: bool
    detail: str = ""


class UnitGuard:
    def __init__(self, test_node):
        self._node = test_node
        self._events: list[GuardEvent] = []
        self._premise_count = 0
        self._exercise_count = 0
        self._outcome_count = 0
        self._last_exercise_result: Any = None

    def _run_check(self, check: Any) -> Any:
        if callable(check):
            return check()
        return check

    def _record(self, phase: str, step: str, ok: bool, detail: str = "") -> None:
        self._events.append(GuardEvent(phase=phase, step=step, ok=ok, detail=detail))

    def premise(self, step: str, check: Any, expect: bool = True) -> Any:
        self._premise_count += 1
        try:
            value = self._run_check(check)
        except Exception as exc:  # pragma: no cover - exercised via tests using guard
            self._record("premise", step, False, f"{type(exc).__name__}: {exc}")
            pytest.fail(f"[premise:{step}] raised {type(exc).__name__}: {exc}")
        ok = bool(value) if expect else not bool(value)
        self._record("premise", step, ok, f"value={value!r}")
        if not ok:
            expected = "truthy" if expect else "falsy"
            pytest.fail(f"[premise:{step}] expected {expected}, got {value!r}")
        return value

    def exercise(self, step: str, action: Any) -> Any:
        self._exercise_count += 1
        try:
            result = self._run_check(action)
        except Exception as exc:  # pragma: no cover - exercised via tests using guard
            self._record("exercise", step, False, f"{type(exc).__name__}: {exc}")
            pytest.fail(f"[exercise:{step}] raised {type(exc).__name__}: {exc}")
        self._last_exercise_result = result
        self._record("exercise", step, True)
        return result

    def outcome(self, step: str, check: Any, expect: bool = True) -> Any:
        self._outcome_count += 1
        try:
            value = self._run_check(check)
        except Exception as exc:  # pragma: no cover - exercised via tests using guard
            self._record("outcome", step, False, f"{type(exc).__name__}: {exc}")
            pytest.fail(f"[outcome:{step}] raised {type(exc).__name__}: {exc}")
        ok = bool(value) if expect else not bool(value)
        self._record("outcome", step, ok, f"value={value!r}")
        if not ok:
            expected = "truthy" if expect else "falsy"
            pytest.fail(f"[outcome:{step}] expected {expected}, got {value!r}")
        return value

    def counts(self) -> tuple[int, int, int]:
        return self._premise_count, self._exercise_count, self._outcome_count

    def is_complete(self) -> bool:
        return self._premise_count >= 1 and self._exercise_count >= 1 and self._outcome_count >= 1

    def missing_phases(self) -> list[str]:
        missing: list[str] = []
        if self._premise_count < 1:
            missing.append("premise")
        if self._exercise_count < 1:
            missing.append("exercise")
        if self._outcome_count < 1:
            missing.append("outcome")
        return missing

    def trace_json(self) -> str:
        payload = [
            {
                "phase": event.phase,
                "step": event.step,
                "ok": event.ok,
                "detail": event.detail,
            }
            for event in self._events
        ]
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)

    @property
    def last_exercise_result(self) -> Any:
        return self._last_exercise_result


def _is_unit_test_item(nodeid: str) -> bool:
    return nodeid.replace("\\", "/").startswith("tests/unit/")


@pytest.fixture()
def guard(request):
    recorder = UnitGuard(request.node)
    yield recorder

    premise_count, exercise_count, outcome_count = recorder.counts()
    complete = recorder.is_complete()
    trace_json = recorder.trace_json()
    trace_limit = 6000
    if len(trace_json) > trace_limit:
        trace_json = trace_json[: trace_limit - 3] + "..."

    request.node.user_properties.append(("guard_premise_count", premise_count))
    request.node.user_properties.append(("guard_exercise_count", exercise_count))
    request.node.user_properties.append(("guard_outcome_count", outcome_count))
    request.node.user_properties.append(("guard_complete", complete))
    request.node.user_properties.append(("guard_trace_json", trace_json))
    setattr(
        request.node,
        "_guard_meta",
        {
            "complete": complete,
            "missing": recorder.missing_phases(),
            "counts": (premise_count, exercise_count, outcome_count),
        },
    )


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    allow_guard_exempt = os.getenv("ALLOW_GUARD_EXEMPT", "0") == "1"
    offenders: list[tuple[str, str]] = []
    exemptions: list[str] = []

    for item in session.items:
        if not _is_unit_test_item(item.nodeid):
            continue
        exempt_marker = item.get_closest_marker("guard_exempt")
        if exempt_marker:
            exemptions.append(item.nodeid)
            if not allow_guard_exempt:
                offenders.append((item.nodeid, "guard_exempt marker is disallowed"))
            continue
        guard_meta = getattr(item, "_guard_meta", None)
        if guard_meta is None:
            offenders.append((item.nodeid, "missing guard fixture usage"))
            continue
        if not guard_meta["complete"]:
            missing = ",".join(guard_meta["missing"])
            counts = guard_meta["counts"]
            offenders.append(
                (
                    item.nodeid,
                    f"incomplete guard phases missing={missing} counts={counts}",
                )
            )

    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    if terminal:
        terminal.write_sep("-", "Unit Guard Summary")
        terminal.write_line(
            f"checked={len([i for i in session.items if _is_unit_test_item(i.nodeid)])} "
            f"offenders={len(offenders)} exemptions={len(exemptions)}"
        )
        if offenders:
            for nodeid, reason in offenders:
                terminal.write_line(f"  - {nodeid}: {reason}")

    if offenders and session.exitstatus == 0:
        session.exitstatus = 1


@pytest.fixture()
def capiss_module(tmp_path, monkeypatch):
    monkeypatch.setenv("CAPISS_KEY_DIR", str(tmp_path / "capiss_keys"))
    monkeypatch.setenv("M4_MAX_DEPTH", "3")
    monkeypatch.setenv("M4_DEFAULT_BUDGET", "10")
    monkeypatch.setenv("M4_ROOT_TTL_SECONDS", "60")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    return load_module_from_path(CAPISS_APP_PATH, "capiss_app_test")


@pytest.fixture()
def toolb_module(monkeypatch):
    monkeypatch.setenv("M4_MAX_DEPTH", "3")
    monkeypatch.setenv("M4_RATE_LIMIT", "20")
    monkeypatch.setenv("M4_RATE_WINDOW_SECONDS", "10")
    monkeypatch.setenv("M4_REQUEST_COST", "1")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    return load_module_from_path(TOOLB_SERVER_PATH, "toolb_server_test")


@pytest.fixture()
def jiratool_module(monkeypatch):
    monkeypatch.setenv("M4_MAX_DEPTH", "3")
    monkeypatch.setenv("M4_RATE_LIMIT", "20")
    monkeypatch.setenv("M4_RATE_WINDOW_SECONDS", "10")
    monkeypatch.setenv("M4_REQUEST_COST", "1")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("JIRA_UPSTREAM_MODE", "mock")
    monkeypatch.setenv("JIRA_MOCK_BASE_URL", "http://jira-mock:8080")
    return load_module_from_path(JIRATOOL_SERVER_PATH, "jiratool_server_test")


@pytest.fixture()
def shared_enforcement_module():
    return load_module_from_path(SHARED_ENFORCEMENT_PATH, "shared_enforcement_test")
