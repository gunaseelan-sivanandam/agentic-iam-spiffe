#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


EVENT_TYPE = "capiss_mint_decision"
DEFAULT_CONTAINER = "spiffe-capability-issuer"
FIELD_ORDER = [
    "event_type",
    "sequence",
    "result",
    "reason_code",
    "correlation_id",
    "subject_spiffe_id",
    "delegator_spiffe_id",
    "decision_type",
    "aud",
    "act",
    "res",
    "resource_attrs",
    "token_id",
    "root_token_id",
    "parent_token_id",
    "delegation_depth",
    "issued_at_local",
    "expires_at_local",
    "timestamp_local",
    "ttl_seconds",
    "issued_at_utc",
    "expires_at_utc",
    "timestamp_utc",
    "timezone",
    "registry_hit",
    "error",
    "policy_id",
    "policy_hash",
]
FORBIDDEN_FIELD_NAMES = {
    "token",
    "authorization",
    "Authorization",
    "cookie",
    "cookies",
    "jira_api_token",
    "JIRA_API_TOKEN",
}
FORBIDDEN_TEXT = ("Bearer ", "Basic ", "biscuit")


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr, flush=True)


def _contains_forbidden_value(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in FORBIDDEN_TEXT)
    if isinstance(value, dict):
        return any(_contains_forbidden_value(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_value(item) for item in value)
    return False


# DD: DD-901
# Implements: ARCH-032
# Title: normalize_event Varambu capiss audit allowlist normalizer
def normalize_event(raw: dict[str, Any], sequence: int) -> dict[str, Any] | None:
    if raw.get("event_type") != EVENT_TYPE:
        return None
    normalized: dict[str, Any] = {}
    for key in FIELD_ORDER:
        if key == "sequence":
            normalized[key] = sequence
            continue
        if key not in raw:
            continue
        if key in FORBIDDEN_FIELD_NAMES or _contains_forbidden_value(raw[key]):
            warn(f"dropped forbidden audit field: {key}")
            continue
        normalized[key] = raw[key]
    for key in raw:
        if key not in FIELD_ORDER:
            warn(f"dropped unknown audit field: {key}")
    return normalized


def _display(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dict):
        return " ".join(f"{k}={value[k]}" for k in sorted(value))
    return str(value)


def _humanize_reason(reason_code: str) -> str:
    """Render a snake_case reason_code as Title Case words (policy -> Policy)."""
    return " ".join(word.capitalize() for word in reason_code.split("_"))


_GREEN = "\033[32m"
_RED = "\033[1;31m"
_RESET = "\033[0m"
_HEADER_RE = re.compile(r"^#\d+ (MINTED|DENIED)\b")


def _colorize_line(line: str) -> str:
    """Color a MINTED/DENIED header line for display only (TTY). The persisted
    file is written by render_record without color; color is applied here at
    print time so the evidence file and any pipe stay plain."""
    if not sys.stdout.isatty():
        return line
    match = _HEADER_RE.match(line)
    if not match:
        return line
    color = _GREEN if match.group(1) == "MINTED" else _RED
    body = line.rstrip("\n")
    newline = "\n" if line.endswith("\n") else ""
    return f"{color}{body}{_RESET}{newline}"


# DD: DD-902
# Implements: ARCH-032
# Title: render_record Varambu human-readable capiss audit renderer
def render_record(record: dict[str, Any], *, verbose: bool = False) -> str:
    result = str(record.get("result", "")).upper()
    reason_code = str(record.get("reason_code", "-"))
    timestamp = _display(record.get("timestamp_local"))
    sequence = record.get("sequence", "-")
    if result == "ALLOW":
        header = f"#{sequence} MINTED {reason_code.upper()}  {timestamp}"
    elif result == "DENY":
        header = f"#{sequence} DENIED: Reason {_humanize_reason(reason_code)}  {timestamp}"
    else:
        header = f"#{sequence} {result or '-'} {reason_code}  {timestamp}"
    lines = [
        header,
        f"Subject:      {_display(record.get('subject_spiffe_id'))}",
        f"Action:       {_display(record.get('act'))}",
        f"Resource:     {_display(record.get('res'))}",
        f"Audience:     {_display(record.get('aud'))}",
        f"Decision:     {_display(record.get('decision_type'))}",
    ]
    if verbose:
        lines.append(f"Scope:        {_display(record.get('resource_attrs'))}")
    lines.extend([
        f"Token ID:     {_display(record.get('token_id'))}",
        f"Root Token:   {_display(record.get('root_token_id'))}",
        f"Parent Token: {_display(record.get('parent_token_id'))}",
        f"Depth:        {_display(record.get('delegation_depth'))}",
        f"Issued At:    {_display(record.get('issued_at_local'))}",
        f"Expires At:   {_display(record.get('expires_at_local'))}",
        f"Logged At:    {_display(record.get('timestamp_local'))}",
        f"TTL:          {_display(str(record['ttl_seconds']) + 's' if 'ttl_seconds' in record else None)}",
        "UTC:          "
        f"issued={_display(record.get('issued_at_utc'))} "
        f"expires={_display(record.get('expires_at_utc'))} "
        f"logged={_display(record.get('timestamp_utc'))}",
        f"Correlation:  {_display(record.get('correlation_id'))}",
        f"Policy:       {_display(record.get('policy_id'))} {_display(record.get('policy_hash'))}",
    ])
    return "\n".join(lines) + "\n"


# DD: DD-903
# Implements: ARCH-032
# Title: tail Varambu capiss audit session tailer
def tail(args: argparse.Namespace) -> int:
    jsonl_path = Path(args.jsonl)
    human_path = Path(args.human)
    err_path = Path(args.err)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.touch(exist_ok=True)
    human_path.touch(exist_ok=True)
    sequence = sum(1 for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()) + 1
    cmd = ["docker", "logs", "--since", args.since, "--follow", args.container]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    assert proc.stderr is not None
    with err_path.open("a", encoding="utf-8") as err_handle:
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            record = normalize_event(raw, sequence)
            if record is None:
                continue
            with jsonl_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n")
            with human_path.open("a", encoding="utf-8") as handle:
                handle.write(render_record(record, verbose=args.verbose) + "\n")
            sequence += 1
        err_handle.write(proc.stderr.read())
    return proc.wait()


def _read_file(path: Path, *, follow: bool) -> int:
    if path.exists() and path.stat().st_size > 0:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                print(_colorize_line(line), end="")
    else:
        print(f"No capiss audit events recorded for the current Varambu session yet.\nAudit file: {path}")
    if follow:
        try:
            with path.open("r", encoding="utf-8") as handle:
                handle.seek(0, 2)
                while True:
                    line = handle.readline()
                    if line:
                        print(_colorize_line(line), end="", flush=True)
                    else:
                        time.sleep(0.5)
        except KeyboardInterrupt:
            print()  # finish the current line so the shell prompt starts clean
            return 0
    return 0


# DD: DD-904
# Implements: ARCH-032
# Title: show Varambu persisted audit display command
def show(args: argparse.Namespace) -> int:
    return _read_file(Path(args.file), follow=args.follow)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Varambu audit log helper")
    sub = parser.add_subparsers(dest="command", required=True)

    tail_parser = sub.add_parser("tail")
    tail_parser.add_argument("--since", required=True)
    tail_parser.add_argument("--jsonl", required=True)
    tail_parser.add_argument("--human", required=True)
    tail_parser.add_argument("--err", type=Path, required=True)
    tail_parser.add_argument("--container", default=DEFAULT_CONTAINER)
    tail_parser.add_argument("--verbose", action="store_true")
    tail_parser.set_defaults(func=tail)

    show_parser = sub.add_parser("show")
    show_parser.add_argument("--file", required=True)
    show_parser.add_argument("--follow", action="store_true")
    show_parser.set_defaults(func=show)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
