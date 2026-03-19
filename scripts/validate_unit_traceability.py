#!/usr/bin/env python3
"""Validate requirement-to-unit-test traceability matrix."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQ_RE = re.compile(r"^###\s+(REQ-)?(M4-[A-Z0-9]+)\s+—")
ROW_RE = re.compile(r"^\|\s*(REQ-)?(M4-[A-Z0-9]+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*")
VALID_STATUS = {"Covered", "Partial", "Gap"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", default="docs/requirements.md")
    parser.add_argument("--spec", default="docs/unit_test_spec.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    req_path = Path(args.requirements)
    spec_path = Path(args.spec)
    if not req_path.exists() or not spec_path.exists():
        print("[traceability] requirements/spec file missing", file=sys.stderr)
        return 2

    req_ids: list[str] = []
    for line in req_path.read_text(encoding="utf-8").splitlines():
        m = REQ_RE.match(line.strip())
        if m:
            req_ids.append(m.group(2))
    req_set = set(req_ids)

    seen: dict[str, tuple[str, str]] = {}
    unknown: list[str] = []
    duplicates: list[str] = []
    bad_status: list[str] = []
    missing_tests_for_covered: list[str] = []

    for raw in spec_path.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(raw.strip())
        if not m:
            continue
        req_id = m.group(2).strip()
        tests = m.group(4).strip()
        status = m.group(5).strip()

        if req_id in seen:
            duplicates.append(req_id)
        seen[req_id] = (tests, status)

        if req_id not in req_set:
            unknown.append(req_id)
        if status not in VALID_STATUS:
            bad_status.append(f"{req_id}:{status}")
        if status in {"Covered", "Partial"} and tests in {"-", "", "TBD"}:
            missing_tests_for_covered.append(req_id)

    missing = sorted(req_set - set(seen))

    failures: list[str] = []
    if unknown:
        failures.append(f"unknown requirement IDs in spec: {sorted(set(unknown))}")
    if duplicates:
        failures.append(f"duplicate requirement IDs in spec: {sorted(set(duplicates))}")
    if bad_status:
        failures.append(f"invalid status values: {sorted(set(bad_status))}")
    if missing_tests_for_covered:
        failures.append(
            "covered/partial rows missing test refs: "
            f"{sorted(set(missing_tests_for_covered))}"
        )
    if missing:
        failures.append(f"requirements missing from spec: {missing}")

    if failures:
        print("[traceability] FAILED", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1

    print(f"[traceability] PASSED ({len(seen)} mapped requirements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
