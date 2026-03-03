#!/usr/bin/env python3
"""Enforce coverage thresholds for critical modules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-json", default="coverage.json")
    parser.add_argument("--min-total-line", type=float, default=85.0)
    parser.add_argument("--min-critical-branch", type=float, default=75.0)
    parser.add_argument(
        "--critical-file",
        action="append",
        default=[
            "services/capability-issuer/app.py",
            "services/tool-b/server.py",
        ],
    )
    return parser.parse_args()


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def find_file_entry(files: dict, suffix: str) -> tuple[str, dict] | tuple[None, None]:
    needle = normalize(suffix)
    for name, payload in files.items():
        if normalize(name).endswith(needle):
            return name, payload
    return None, None


def main() -> int:
    args = parse_args()
    coverage_path = Path(args.coverage_json)
    if not coverage_path.exists():
        print(f"[coverage-gate] missing coverage file: {coverage_path}", file=sys.stderr)
        return 2

    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    totals = data.get("totals", {})
    total_line = float(totals.get("percent_covered", 0.0))

    failures: list[str] = []
    if total_line < args.min_total_line:
        failures.append(
            f"total line coverage {total_line:.2f}% < required {args.min_total_line:.2f}%"
        )

    files = data.get("files", {})
    for target in args.critical_file:
        name, payload = find_file_entry(files, target)
        if payload is None:
            failures.append(f"critical file missing from report: {target}")
            continue

        summary = payload.get("summary", {})
        num_branches = int(summary.get("num_branches", 0))
        covered_branches = int(summary.get("covered_branches", 0))
        if num_branches <= 0:
            failures.append(f"{name}: no branch data available")
            continue

        branch_pct = (covered_branches / num_branches) * 100.0
        if branch_pct < args.min_critical_branch:
            failures.append(
                f"{name}: branch coverage {branch_pct:.2f}% < required "
                f"{args.min_critical_branch:.2f}%"
            )

    if failures:
        print("[coverage-gate] FAILED", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1

    print(
        "[coverage-gate] PASSED "
        f"(total-line={total_line:.2f}%, critical-branch>={args.min_critical_branch:.2f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
