#!/usr/bin/env python3
"""Extract metadata-only Claude review usage; never publish prompts, replies or thinking.

Input: JSON list of invocation records with log, role, cycle, attempt, requested_effort
and optional exit_code. Output: JSON and a Markdown table. USD is the CLI-reported
estimate, not an invoice or a measure of subscription quota. Missing metrics stay null.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path


TOKEN_FIELDS = {
    "input_tokens": "inputTokens",
    "cache_read_tokens": "cacheReadInputTokens",
    "cache_write_tokens": "cacheCreationInputTokens",
    "output_tokens": "outputTokens",
}


def _tool_metadata(event: dict, state: dict) -> None:
    message = event.get("message", {})
    if not isinstance(message, dict):
        state["malformed"] += 1
        return
    content = message.get("content", [])
    if not isinstance(content, list):
        state["malformed"] += 1
        return
    for item in content:
        if isinstance(item, dict) and item.get("type") == "tool_use":
            if isinstance(item.get("id"), str):
                state["tools"].add(item["id"])


def _summary_metadata(event: dict, state: dict) -> None:
    if isinstance(event.get("session_id"), str):
        state["session"] = event["session_id"]
    if event.get("type") == "system" and event.get("subtype") == "init":
        if isinstance(event.get("model"), str):
            state["models"].add(event["model"])
    if event.get("type") == "result" or ("modelUsage" in event and "duration_ms" in event):
        state["result"] = event


def _read_metadata(path: Path) -> dict:
    state = {"result": {}, "session": None, "models": set(), "tools": set(),
             "malformed": 0, "digest": hashlib.sha256(), "unreadable": False}
    try:
        with path.open("rb") as handle:
            for line in handle:
                state["digest"].update(line)
                try:
                    event = json.loads(line)
                except (ValueError, UnicodeError):
                    state["malformed"] += 1
                    continue
                if not isinstance(event, dict):
                    state["malformed"] += 1
                    continue
                _summary_metadata(event, state)
                _tool_metadata(event, state)
    except OSError:
        state["unreadable"] = True
    return state


def _model_usage(result: dict, state: dict) -> dict:
    usage = result.get("modelUsage", {})
    if not isinstance(usage, dict):
        state["malformed"] += 1
        return {}
    if any(not isinstance(value, dict) for value in usage.values()):
        state["malformed"] += 1
        return {}
    return usage


def _metric(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def _total(usage: dict, field: str):
    values = [_metric(value.get(field)) for value in usage.values()]
    return sum(values) if values and all(value is not None for value in values) else None


def _status(result: dict, spec: dict, unreadable: bool) -> str:
    code = spec.get("exit_code")
    if code == 124:
        return "timed_out"
    if code == 130:
        return "interrupted"
    if unreadable:
        return "unreadable"
    if not result:
        return "failed" if code else "incomplete"
    return _terminal_status(result, code)


def _terminal_status(result: dict, code) -> str:
    failed = result.get("is_error") or result.get("subtype") != "success" or code not in (None, 0)
    if not failed:
        return "completed"
    # Provider error text classifies availability only; it never grants review credit.
    text = str(result.get("result", "")).lower()
    return "quota_limited" if "limit" in text and ("hour" in text or "usage" in text) else "failed"


def _log_mtime(path: Path):
    try:
        return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat()
    except OSError:
        return None


def read_invocation(spec: dict) -> dict:
    path = Path(spec["log"])
    effort = spec.get("requested_effort")
    if effort not in (None, "medium", "high"):
        raise ValueError("requested effort must be medium, high or unknown for historical runs")
    state = _read_metadata(path)
    result = state["result"]
    usage = _model_usage(result, state)
    estimate = _metric(result.get("total_cost_usd"))
    if estimate is None:
        estimate = _total(usage, "costUSD")
    identity = state["session"] or str(path.resolve())
    row = {key: spec.get(key) for key in (
        "role", "cycle", "attempt", "requested_model", "effort_reason", "wall_duration_ms",
        "started_utc", "ended_utc", "exit_code", "termination_cause")}
    row.update(
        kind=spec.get("kind", "review"), stage=spec.get("stage", "plan_bundle"),
        requested_effort=effort,
        observed_effort=result.get("effort") if result.get("effort") in ("medium", "high", "xhigh", "max", "low") else None,
        observed_log_mtime_utc=_log_mtime(path),
        historical_timestamp_limit="File mtime is an observation, not guaranteed invocation time.",
        invocation_id=hashlib.sha256(identity.encode()).hexdigest()[:16],
        log_sha256=state["digest"].hexdigest(), models=sorted(state["models"] | set(usage)),
        status=_status(result, spec, state["unreadable"]),
        duration_ms=_metric(result.get("duration_ms")), turns=_metric(result.get("num_turns")),
        tool_calls=len(state["tools"]), malformed_lines=state["malformed"],
        provider_usd_estimate=estimate, actual_billed_usd=None, subscription_quota_used=None,
        usage_source="terminal modelUsage" if usage else "unavailable", output_includes_thinking=True,
    )
    # Use cumulative terminal modelUsage once; thinking is a subset of output.
    row.update({public: _total(usage, provider) for public, provider in TOKEN_FIELDS.items()})
    return row


def collect(specs: list[dict]) -> dict:
    rows = []
    seen = {}
    duplicates = 0
    for spec in specs:
        row = read_invocation(spec)
        key = row["invocation_id"]
        if key is not None and key in seen:
            prior = seen[key]
            if any(row.get(k) != prior.get(k) for k in ("role", "cycle", "attempt", "requested_effort", "log_sha256")):
                raise ValueError("conflicting metadata for the same invocation")
            duplicates += 1
            continue
        seen[key] = row
        rows.append(row)
    return {"schema_version": 2, "invocations": rows, "duplicates_ignored": duplicates,
            "totals": _totals(rows),
            "coverage": "Only supplied available logs; earlier feasibility probes without logs are excluded from row counts and missing_invocations.",
            "limits": ["USD is a reported estimate, not actual billing or subscription-quota consumption.",
                       "Missing terminal metrics remain unknown; known sums may be incomplete.",
                       "Cached input categories are separate; output already includes thinking.",
                       "Requested effort does not prove effective backend effort; historical defaults are unknown."]}


def _totals(rows: list[dict]) -> dict:
    totals = {}
    for field in (*TOKEN_FIELDS, "provider_usd_estimate"):
        known = [row[field] for row in rows if row.get(field) is not None]
        totals[field] = {"known_sum": sum(known) if known else None,
                         "missing_invocations": sum(row.get(field) is None for row in rows)}
    return totals


def markdown(report: dict) -> str:
    lines = ["| Cycle | Role | Attempt | Effort requested | Status | Seconds | USD estimate |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in report["invocations"]:
        def number(field: str, decimals: int | None = None) -> str:
            value = row.get(field)
            return "unknown" if value is None else (f"{value:.{decimals}f}" if decimals is not None else str(value))
        seconds = "unknown" if row.get("duration_ms") is None else f"{row['duration_ms'] / 1000:.1f}"
        lines.append("| " + " | ".join([
            str(row.get("cycle")), str(row.get("role")), str(row.get("attempt")),
            row.get("requested_effort") or "unknown", row["status"], seconds,
            number("provider_usd_estimate", 4),
        ]) + " |")
    lines.extend(["", "USD values are CLI-reported estimates, not subscription charges or quota percentages.",
                  "Unknown is not zero. Output includes thinking; token categories are not added twice."])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path)
    args = parser.parse_args()
    report = collect(json.loads(args.manifest.read_text()))
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.markdown_out:
        args.markdown_out.write_text(markdown(report))
    print(f"Reported {len(report['invocations'])} invocations; duplicate log copies ignored: {report['duplicates_ignored']}")


if __name__ == "__main__":
    main()
