#!/usr/bin/env python3
"""Launch one already-authorized Claude review with explicit effort and usage metadata.

This is an invocation wrapper, not the delivery controller: it grants no approval,
selects no stages, does not retry, and never merges or publishes anything.
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
import subprocess
import time

from review_usage import collect


MAX_FIX_CYCLES = 3


def cycle_budget_error(root: Path, cycle: int) -> str | None:
    """Check the declared frozen budget; persistent reconciliation belongs to the controller."""
    if cycle > MAX_FIX_CYCLES:
        return "Three fix-and-recheck cycles exhausted; escalate instead of launching another review"
    try:
        manifest = json.loads((root / "shared/input_manifest.json").read_text())
    except (OSError, ValueError):
        return "A frozen manifest with cumulative cycle accounting is required"
    if not isinstance(manifest, dict):
        return "Invalid cycle accounting"
    completed = manifest.get("completed_cycles_before")
    if type(completed) is not int or completed < 0:
        return "Missing or invalid cumulative completed-cycle count"
    if completed >= MAX_FIX_CYCLES:
        return "Cumulative cycle budget exhausted; the count cannot be reset"
    if manifest.get("cycle") != cycle or completed != max(0, cycle - 1):
        return "Requested cycle does not match the frozen cumulative cycle accounting"
    return None


def enforce_cycle_budget(root: Path, cycle: int, parser: argparse.ArgumentParser) -> None:
    error = cycle_budget_error(root, cycle)
    if error:
        parser.error(error)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Frozen review view with authority/source/shared and role prompt")
    parser.add_argument("--role", choices=["primary", "security", "design"], required=True)
    parser.add_argument("--cycle", type=int, required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--stage", default="plan_bundle")
    parser.add_argument("--effort", choices=["medium", "high"], required=True)
    parser.add_argument("--effort-reason", required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.cycle < 0 or args.attempt < 1 or args.timeout < 1:
        parser.error("cycle must be nonnegative; attempt and timeout must be positive")
    root = args.root.resolve()
    enforce_cycle_budget(root, args.cycle, parser)
    authority = root / "authority/governing_review_authority.txt"
    command = ["claude", "--safe-mode", "--restricted", "--tools", "Read,Grep,Glob",
               "--allowedTools", "Read,Grep,Glob", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--permission-mode", "dontAsk", "--no-session-persistence",
               "--model", "claude-opus-5-5", "--effort", args.effort,
               "--add-dir", str(root / "source"), "--add-dir", str(root / "shared"),
               "--add-dir", str(root / args.role), "--append-system-prompt", authority.read_text(),
               "--output-format", "stream-json", "--verbose", "-p"]
    prefix = root / f"{args.role}_attempt{args.attempt}"
    log = prefix.with_name(prefix.name + "_review.jsonl")
    request_path = prefix.with_name(prefix.name + "_request.json")
    usage_path = prefix.with_name(prefix.name + "_usage.json")
    stderr_path = prefix.with_name(prefix.name + "_review.stderr")
    request = {"role": args.role, "stage": args.stage, "kind": "review", "cycle": args.cycle,
               "attempt": args.attempt, "requested_model": command[command.index("--model") + 1],
               "requested_effort": command[command.index("--effort") + 1],
               "effort_reason": args.effort_reason, "log": str(log),
               "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if args.dry_run:
        redacted_command = command.copy()
        redacted_command[command.index("--append-system-prompt") + 1] = "<approved authority text omitted>"
        print(json.dumps({**request, "dry_run": True, "command": redacted_command,
                          "cwd": str(root / "authority")}))
        return 0
    if any(p.exists() for p in (log, request_path, usage_path, stderr_path)):
        parser.error("attempt files already exist; preserve them and choose a new attempt number")
    # Persist intent before starting; neither request nor usage metadata contains prompt text.
    with request_path.open("x") as handle:
        json.dump(request, handle, indent=2)
    started = time.monotonic()
    exit_code = 1
    termination_cause = "process_exit"
    try:
        with (root / f"{args.role}_prompt.txt").open() as inp, log.open("x") as out, stderr_path.open("x") as err:
            exit_code = subprocess.run(command, stdin=inp, stdout=out, stderr=err,
                                       cwd=root / "authority", timeout=args.timeout).returncode
    except subprocess.TimeoutExpired:
        exit_code = 124
        termination_cause = "timeout"
    except KeyboardInterrupt:
        exit_code = 130
        termination_cause = "interrupted"
    except OSError:
        exit_code = 1
        termination_cause = "launch_error"
    finally:
        request.update(exit_code=exit_code, wall_duration_ms=round((time.monotonic() - started) * 1000),
                       ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       termination_cause=termination_cause)
        report = collect([request])
        with usage_path.open("x") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        row = report["invocations"][0]
        print(json.dumps({"role": args.role, "requested_effort": args.effort,
                          "status": row["status"], "exit_code": exit_code, "usage_record": str(usage_path)}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
