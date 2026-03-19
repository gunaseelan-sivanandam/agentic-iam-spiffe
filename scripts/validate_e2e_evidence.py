#!/usr/bin/env python3
"""Validate E2E evidence directories to reduce false-green risk."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(
        "[qa-evidence] PyYAML is required. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests", default="trace/tests.yaml")
    parser.add_argument("--evidence-dir", default="artifacts/rogue-tests")
    parser.add_argument("--test-report", default="test_report.log")
    parser.add_argument("--report-json", default="artifacts/quality/evidence_report.json")
    parser.add_argument(
        "--max-age-hours",
        type=float,
        default=0.0,
        help="Optional freshness check. 0 disables age validation.",
    )
    return parser.parse_args()


def _load_tests(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"missing tests file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("tests"), list):
        raise ValueError(f"{path}: expected top-level 'tests' list")
    out: list[dict[str, Any]] = []
    for idx, item in enumerate(data["tests"], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: tests[{idx}] must be a map")
        out.append(item)
    return out


def _count(pattern: str, base: Path) -> int:
    return len(list(base.glob(pattern)))


def _read_lines(pattern: str, base: Path) -> list[str]:
    out: list[str] = []
    for path in sorted(base.glob(pattern)):
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if text:
            out.append(text)
    return out


def _parse_fail_count(test_report: Path) -> int | None:
    if not test_report.exists():
        return None
    text = test_report.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Failed:\s*(\d+)", text)
    if not m:
        return None
    return int(m.group(1))


def _parse_prefix_statuses(test_report: Path) -> dict[str, str]:
    if not test_report.exists():
        return {}

    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    evdir_re = re.compile(r"EVIDENCE_DIR=/tmp/rogue-tests/([^/\s]+)")
    status_re = re.compile(r"\[T\d+\].*?\.{4}\s*(PASS|FAIL)\b")

    statuses: dict[str, str] = {}
    current_prefix: str | None = None

    for raw in test_report.read_text(encoding="utf-8", errors="replace").splitlines():
        line = ansi_re.sub("", raw)
        m_dir = evdir_re.search(line)
        if m_dir:
            basename = m_dir.group(1)
            current_prefix = basename.split("_", 1)[0]
            continue

        m_status = status_re.search(line)
        if m_status and current_prefix:
            statuses[current_prefix] = m_status.group(1)
            current_prefix = None

    return statuses


def _latest_dir_for_prefix(base: Path, prefix: str) -> Path | None:
    matches = sorted([p for p in base.glob(f"{prefix}_*") if p.is_dir()])
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


def main() -> int:
    args = parse_args()

    try:
        tests = _load_tests(Path(args.tests))
    except ValueError as exc:
        print(f"[qa-evidence] FAILED: {exc}", file=sys.stderr)
        return 2

    evidence_root = Path(args.evidence_dir)
    if not evidence_root.exists() or not evidence_root.is_dir():
        print(f"[qa-evidence] FAILED: missing evidence dir: {evidence_root}", file=sys.stderr)
        return 1

    active_e2e = [
        t
        for t in tests
        if t.get("type") == "e2e_suite" and str(t.get("status", "active")).lower() == "active"
    ]

    failures: list[str] = []
    warnings: list[str] = []
    report_tests: list[dict[str, Any]] = []
    expected_prefix_count = 0
    now = time.time()
    report_statuses = _parse_prefix_statuses(Path(args.test_report))

    for test in active_e2e:
        test_id = str(test.get("id", ""))
        prefixes = test.get("evidence_prefixes", [])
        if not isinstance(prefixes, list) or not prefixes:
            failures.append(f"{test_id}: missing evidence_prefixes")
            continue

        for raw_prefix in prefixes:
            if not isinstance(raw_prefix, str) or not raw_prefix:
                failures.append(f"{test_id}: invalid evidence prefix '{raw_prefix}'")
                continue

            expected_prefix_count += 1
            prefix = raw_prefix
            ev_dir = _latest_dir_for_prefix(evidence_root, prefix)
            if ev_dir is None:
                failures.append(f"{test_id}: missing evidence directory for prefix '{prefix}'")
                continue

            premise_count = _count("premise_*.txt", ev_dir)
            exercise_count = _count("exercise_*.txt", ev_dir)
            outcome_count = _count("outcome_*.txt", ev_dir)
            cmd_count = _count("cmd_*.txt", ev_dir)
            fail_reason_count = _count("fail_reason.txt", ev_dir)
            warning_count = _count("warning_reason_*.txt", ev_dir)
            warning_messages = _read_lines("warning_reason_*.txt", ev_dir)
            fail_reason_messages = _read_lines("fail_reason.txt", ev_dir)

            if premise_count == 0:
                failures.append(f"{test_id}/{prefix}: missing premise guard artifacts")
            if exercise_count == 0:
                failures.append(f"{test_id}/{prefix}: missing exercise guard artifacts")
            if outcome_count == 0:
                failures.append(f"{test_id}/{prefix}: missing outcome guard artifacts")
            if cmd_count == 0:
                failures.append(f"{test_id}/{prefix}: missing command capture artifacts")

            report_status = report_statuses.get(prefix)
            if report_status is None:
                failures.append(f"{test_id}/{prefix}: missing per-test PASS/FAIL status in test_report.log")
            elif report_status != "PASS":
                failures.append(f"{test_id}/{prefix}: test_report.log status is {report_status}")
            elif fail_reason_count > 0:
                failures.append(
                    f"{test_id}/{prefix}: passing test left fail_reason artifact: "
                    + " | ".join(fail_reason_messages or ["present"])
                )

            age_hours = (now - ev_dir.stat().st_mtime) / 3600.0
            if args.max_age_hours > 0 and age_hours > args.max_age_hours:
                failures.append(
                    f"{test_id}/{prefix}: stale evidence ({age_hours:.1f}h > {args.max_age_hours:.1f}h)"
                )

            if warning_messages:
                warnings.extend(f"{test_id}/{prefix}: {message}" for message in warning_messages)

            report_tests.append(
                {
                    "suite_id": test_id,
                    "prefix": prefix,
                    "evidence_dir": str(ev_dir),
                    "premise_count": premise_count,
                    "exercise_count": exercise_count,
                    "outcome_count": outcome_count,
                    "cmd_count": cmd_count,
                    "has_fail_reason": fail_reason_count > 0,
                    "fail_reason_messages": fail_reason_messages,
                    "warning_count": warning_count,
                    "warning_messages": warning_messages,
                    "report_status": report_status,
                    "age_hours": round(age_hours, 2),
                }
            )

    test_report_path = Path(args.test_report)
    failed_count = _parse_fail_count(test_report_path)
    if failed_count is None:
        failures.append(f"test report missing or unparsable: {test_report_path}")
    elif failed_count > 0:
        failures.append(f"test_report.log indicates failed tests: {failed_count}")

    report = {
        "summary": {
            "e2e_suites": len(active_e2e),
            "expected_test_prefixes": expected_prefix_count,
            "validated_prefixes": len(report_tests),
            "failures": len(failures),
            "warnings": len(warnings),
            "failed_count_from_report": failed_count,
            "max_age_hours": args.max_age_hours,
        },
        "tests": report_tests,
        "warnings": warnings,
    }

    report_path = Path(args.report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if failures:
        print("[qa-evidence] FAILED", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        print(f"[qa-evidence] report: {report_path}", file=sys.stderr)
        return 1

    summary = report["summary"]
    print(
        "[qa-evidence] PASSED "
        f"(validated={summary['validated_prefixes']}/{summary['expected_test_prefixes']}, "
        f"warnings={summary['warnings']})"
    )
    print(f"[qa-evidence] report: {report_path}")
    if warnings:
        print("[qa-evidence] warnings:")
        for item in warnings:
            print(f"  - {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
