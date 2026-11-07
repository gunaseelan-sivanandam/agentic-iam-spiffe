#!/usr/bin/env python3
"""Fake `claude` CLI for the review launcher's tooling tests: records each call and prints a scripted stream.

The test writes `$HOME/scenario.json`, a list of call scenarios used in order (the last one repeats).
Each call is recorded in `$HOME/calls/` with its arguments, environment, working directory, standard
input and the files it could see. A scenario may set:
    sleep         seconds to wait after recording, before any output (for kill and lock tests)
    exit          the exit code (default 0)
    raw_stdout    print exactly this instead of a built stream
    reads         paths for Read calls ("{cwd}" is replaced by the working directory)
    tool_uses     [name, input] pairs for other tool calls
    denials       [name, input] pairs for the result's permission_denials
    rate_limit    {"status", "five_hour", "seven_day", "resetsAt"}, or null for no event
    result        null for no result event, or {"is_error", "structured_output", "result"}
"""

from __future__ import annotations

import fcntl
import json
import os
import sys
import time
from pathlib import Path

DEFAULT_REPLY = {"findings": [], "verdict": "yes"}


def next_scenario(home: Path) -> dict:
    scenarios = json.loads((home / "scenario.json").read_text(encoding="utf-8"))
    with open(home / "counter.lock", "a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        counter = home / "counter"
        used = int(counter.read_text()) if counter.exists() else 0
        counter.write_text(str(used + 1))
    return scenarios[min(used, len(scenarios) - 1)]


def record_call(home: Path, stdin: str) -> None:
    calls = home / "calls"
    calls.mkdir(exist_ok=True)
    cwd = Path.cwd()
    files = sorted(str(p.relative_to(cwd)) for p in cwd.rglob("*") if p.is_file() or p.is_symlink())
    record = {"argv": sys.argv[1:], "env": dict(os.environ), "cwd": str(cwd), "stdin": stdin, "files": files}
    (calls / f"{time.time_ns()}-{os.getpid()}.json").write_text(json.dumps(record), encoding="utf-8")


def tool_use(name: str, args: dict, cwd: str) -> dict:
    args = {k: v.replace("{cwd}", cwd) if isinstance(v, str) else v for k, v in args.items()}
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": args}]}}


def build_stream(scenario: dict, cwd: str) -> list[dict]:
    events = [{"type": "system", "subtype": "init"}]
    events += [tool_use("Read", {"file_path": path}, cwd) for path in scenario.get("reads", ["scripts/review_me.py"])]
    events += [tool_use(name, args, cwd) for name, args in scenario.get("tool_uses", [])]
    limit = scenario.get("rate_limit", {"status": "allowed", "five_hour": 0.1, "seven_day": 0.05, "resetsAt": 1})
    if limit is not None:
        windows = {"five_hour": {"utilization": limit.get("five_hour"), "resetsAt": limit.get("resetsAt")},
                   "seven_day": {"utilization": limit.get("seven_day"), "resetsAt": limit.get("resetsAt")}}
        events.append({"type": "rate_limit_event", "rate_limit_info": {
            "status": limit["status"], "resetsAt": limit.get("resetsAt"), "unifiedWindows": windows}})
    result = scenario.get("result", {"structured_output": DEFAULT_REPLY})
    if result is not None:
        denials = [{"tool_name": n, "tool_input": a} for n, a in scenario.get("denials", [])]
        events.append({"type": "result", "subtype": "success", "is_error": result.get("is_error", False),
                       "num_turns": 3, "duration_ms": 1000, "total_cost_usd": 0.01,
                       "usage": {"input_tokens": 1, "output_tokens": 2}, "permission_denials": denials,
                       **{k: v for k, v in result.items() if k in ("structured_output", "result")}})
    return events


def main() -> int:
    if sys.argv[1:] == ["--version"]:
        print("9.9.9 (Claude Code)")
        return 0
    home = Path(os.environ["HOME"])
    stdin = sys.stdin.read()
    scenario = next_scenario(home)
    record_call(home, stdin)
    time.sleep(scenario.get("sleep", 0))
    if "raw_stdout" in scenario:
        sys.stdout.write(scenario["raw_stdout"])
    else:
        for event in build_stream(scenario, os.getcwd()):
            print(json.dumps(event))
    return int(scenario.get("exit", 0))


if __name__ == "__main__":
    sys.exit(main())
