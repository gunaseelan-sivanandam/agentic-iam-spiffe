"""Controls against inflated costs, false success and leaked review contents."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SPEC = importlib.util.spec_from_file_location("review_usage", Path(__file__).resolve().parents[2] / "scripts/review_usage.py")
usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(usage)


def write_log(tmp_path, terminal=None):
    path = tmp_path / "review.jsonl"
    events = [{"type": "system", "subtype": "init", "model": "claude-test", "session_id": "synthetic-session"},
              {"type": "assistant", "message": {"content": [{"type": "thinking", "thinking": "PRIVATE_CONTENT"}]}}]
    if terminal is not None:
        events.append({"type": "result", "subtype": "success", **terminal})
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    return {"log": str(path), "role": "security", "cycle": 1, "attempt": 1, "requested_effort": None}


def test_terminal_metrics_not_double_counted_or_billed(tmp_path):
    spec = write_log(tmp_path, {"result": "PRIVATE_CONTENT", "total_cost_usd": 0.2,
        "usage": {"output_tokens": 999}, "modelUsage": {"claude-test": {
            "inputTokens": 10, "cacheReadInputTokens": 100, "cacheCreationInputTokens": 20,
            "outputTokens": 50, "thinkingTokens": 30, "costUSD": 0.2}}})
    report = usage.collect([spec])
    row = report["invocations"][0]
    assert row["output_tokens"] == 50
    assert row["provider_usd_estimate"] == 0.2
    assert row["actual_billed_usd"] is None
    assert row["requested_effort"] is None and row["observed_effort"] is None
    assert "PRIVATE_CONTENT" not in json.dumps(report)


def test_quota_error_is_not_success_and_keeps_consumed_usage(tmp_path):
    spec = write_log(tmp_path, {"is_error": True, "result": "You've hit your 5-hour limit",
                              "modelUsage": {"claude-test": {"outputTokens": 12, "costUSD": 0.01}}})
    row = usage.read_invocation(spec)
    assert row["status"] == "quota_limited"
    assert row["output_tokens"] == 12 and row["provider_usd_estimate"] == 0.01
    assert row["input_tokens"] is None


def test_incomplete_is_unknown_not_free(tmp_path):
    report = usage.collect([write_log(tmp_path)])
    row = report["invocations"][0]
    assert row["status"] == "incomplete" and row["provider_usd_estimate"] is None
    assert report["totals"]["provider_usd_estimate"] == {"known_sum": None, "missing_invocations": 1}


def test_duplicate_session_does_not_inflate_totals(tmp_path):
    spec = write_log(tmp_path, {"total_cost_usd": 0.2})
    report = usage.collect([spec, spec])
    assert len(report["invocations"]) == 1
    assert report["totals"]["provider_usd_estimate"]["known_sum"] == 0.2
    assert report["duplicates_ignored"] == 1


def test_conflicting_effort_for_same_invocation_is_rejected(tmp_path):
    spec = write_log(tmp_path, {})
    with pytest.raises(ValueError, match="conflicting metadata"):
        usage.collect([spec, {**spec, "requested_effort": "high"}])


def test_unapproved_effort_not_accepted(tmp_path):
    spec = write_log(tmp_path, {})
    with pytest.raises(ValueError, match="effort"):
        usage.read_invocation({**spec, "requested_effort": "xhigh"})


def test_manual_launcher_pins_effort_without_spending_tokens(tmp_path):
    authority = tmp_path / "authority"
    authority.mkdir()
    (authority / "governing_review_authority.txt").write_text("Synthetic approved authority")
    script = Path(__file__).resolve().parents[2] / "scripts/run_manual_review.py"
    command = [sys.executable, str(script), str(tmp_path), "--role", "primary", "--cycle", "5",
               "--attempt", "2", "--effort", "medium", "--effort-reason", "Focused recheck", "--dry-run"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    request = json.loads(result.stdout)
    assert request["requested_effort"] == "medium" and request["dry_run"]
    assert request["cycle"] == 5 and request["attempt"] == 2
    argv = request["command"]
    assert "--safe-mode" in argv and "--restricted" in argv
    assert argv[argv.index("--tools") + 1] == "Read,Grep,Glob"
    assert argv[argv.index("--allowedTools") + 1] == "Read,Grep,Glob"
    assert argv[argv.index("--permission-mode") + 1] == "dontAsk"
    assert "--no-session-persistence" in argv and "--strict-mcp-config" in argv
    assert json.loads(argv[argv.index("--mcp-config") + 1]) == {"mcpServers": {}}
    assert argv[argv.index("--append-system-prompt") + 1] == "<approved authority text omitted>"
    assert "Synthetic approved authority" not in result.stdout
    assert request["cwd"] == str(authority)
    assert not list(tmp_path.glob("*_request.json"))
    command[command.index("medium")] = "xhigh"
    rejected = subprocess.run(command, capture_output=True, text=True)
    assert rejected.returncode == 2


@pytest.mark.parametrize("bad", [{"message": None}, {"message": "unexpected"},
                                  {"message": {"content": None}}, {"modelUsage": {"bad": None}, "type": "result"}])
def test_unexpected_provider_shapes_do_not_lose_usage_record(tmp_path, bad):
    spec = write_log(tmp_path)
    with Path(spec["log"]).open("a") as handle:
        handle.write(json.dumps(bad) + "\n")
    row = usage.read_invocation({**spec, "exit_code": 124, "requested_model": "claude-test"})
    assert row["malformed_lines"] >= 1
    assert row["status"] == "timed_out" and row["exit_code"] == 124
    assert row["requested_model"] == "claude-test"


def test_unreadable_log_preserves_request_and_failure_metadata(tmp_path):
    row = usage.read_invocation({"log": str(tmp_path / "missing"), "role": "primary", "cycle": 6,
        "attempt": 1, "kind": "review", "stage": "plan_bundle", "requested_effort": "medium",
        "effort_reason": "Focused recheck", "requested_model": "claude-test", "exit_code": 1,
        "termination_cause": "launch_error", "wall_duration_ms": 10})
    assert row["status"] == "unreadable" and row["termination_cause"] == "launch_error"
    assert row["effort_reason"] == "Focused recheck" and row["wall_duration_ms"] == 10
    assert row["requested_model"] == "claude-test" and row["provider_usd_estimate"] is None


def _launcher(monkeypatch):
    monkeypatch.setitem(sys.modules, "review_usage", usage)
    path = Path(__file__).resolve().parents[2] / "scripts/run_manual_review.py"
    spec = importlib.util.spec_from_file_location("manual_review_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _launch_args(tmp_path):
    authority = tmp_path / "authority"
    authority.mkdir()
    (authority / "governing_review_authority.txt").write_text("Synthetic approved authority")
    (tmp_path / "primary_prompt.txt").write_text("Synthetic prompt")
    return ["run_manual_review", str(tmp_path), "--role", "primary", "--cycle", "6", "--attempt", "1",
            "--effort", "medium", "--effort-reason", "Focused recheck", "--timeout", "1"]


@pytest.mark.parametrize("cause,code,status", [("timeout", 124, "timed_out"),
    ("interrupt", 130, "interrupted"), ("oserror", 1, "failed")])
def test_launcher_failure_still_records_exit_and_usage(tmp_path, monkeypatch, cause, code, status):
    launcher = _launcher(monkeypatch)
    monkeypatch.setattr(sys, "argv", _launch_args(tmp_path))
    def fail(*args, **kwargs):
        if cause == "timeout":
            raise subprocess.TimeoutExpired(args[0], 1)
        if cause == "interrupt":
            raise KeyboardInterrupt
        raise OSError("Synthetic launch failure")
    monkeypatch.setattr(launcher.subprocess, "run", fail)
    assert launcher.main() == code
    row = json.loads((tmp_path / "primary_attempt1_usage.json").read_text())["invocations"][0]
    assert row["exit_code"] == code and row["status"] == status
    assert row["requested_model"] == "claude-opus-5-5"


@pytest.mark.parametrize("invalid", ["omitted", "max"])
def test_launcher_rejects_missing_or_unapproved_effort(tmp_path, monkeypatch, invalid):
    launcher = _launcher(monkeypatch)
    argv = _launch_args(tmp_path)
    if invalid == "omitted":
        index = argv.index("--effort")
        del argv[index:index + 2]
    else:
        argv[argv.index("medium")] = "max"
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as rejected:
        launcher.main()
    assert rejected.value.code == 2


def test_launcher_preserves_existing_attempt(tmp_path, monkeypatch):
    launcher = _launcher(monkeypatch)
    monkeypatch.setattr(sys, "argv", _launch_args(tmp_path))
    request = tmp_path / "primary_attempt1_request.json"
    request.write_text("original record")
    with pytest.raises(SystemExit) as rejected:
        launcher.main()
    assert rejected.value.code == 2 and request.read_text() == "original record"
