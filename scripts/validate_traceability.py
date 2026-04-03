#!/usr/bin/env python3
"""Validate layered traceability with explicit gap reporting."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - explicit operator guidance
    print(
        "[qa-trace] PyYAML is required. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


TEST_TYPES = {"e2e_suite", "e2e_case", "integration_case"}
REQ_RE = re.compile(r"^#{2,3}\s+(REQ-[A-Z0-9.-]+)\s+—\s+(.+?)\s*$")
ARCH_RE = re.compile(r"^##\s+(ARCH-\d{3})\s+(.+?)\s*$")
DD_RE = re.compile(r"^\s*#\s*DD:\s*(DD-\d{3})\s*$")
DD_FIELD_RE = re.compile(r"^\s*#\s*(Implements|Title):\s*(.+?)\s*$")
UT_RE = re.compile(r"^\s*#\s*UT:\s*(UT-\d{3})\s*$")
UT_FIELD_RE = re.compile(
    r"^\s*#\s*(Test Description|Precondition|Expected Output|Covers DD):\s*(.+?)\s*$"
)
UNIT_TEST_DEF_RE = re.compile(r"^\s*def\s+(test_[A-Za-z0-9_]+)\s*\(")
DECORATOR_RE = re.compile(r"^\s*@")
SOURCE_EXTENSIONS = {".py", ".sh", ".rego"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements-doc", default="docs/requirements.md")
    parser.add_argument("--architecture-doc", default="docs/architecture.md")
    parser.add_argument("--source-root", action="append", default=["services"])
    parser.add_argument("--unit-root", action="append", default=["tests/unit"])
    parser.add_argument("--tests", default="trace/tests.yaml")
    parser.add_argument("--report-json", default="artifacts/quality/traceability_report.json")
    parser.add_argument("--design-report-json", default="artifacts/quality/design_index.json")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"missing file: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: top-level document must be a map")
    return raw


def _load_items(path: Path, key: str) -> list[dict[str, Any]]:
    data = _load_yaml(path)
    items = data.get(key)
    if not isinstance(items, list):
        raise ValueError(f"{path}: '{key}' must be a list")
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: '{key}[{idx}]' must be a map")
    return items


def _as_non_empty_str_list(value: Any, *, field: str, item_id: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f"{item_id}: '{field}' must be a string list of non-empty values")
    return value


def _check_file_contains(path: Path, needle: str, *, context: str) -> None:
    if not needle:
        return
    content = path.read_text(encoding="utf-8")
    if needle not in content:
        raise ValueError(f"{context}: selector not found in {path}: {needle}")


def _parse_requirements(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise ValueError(f"missing file: {path}")

    requirements: dict[str, dict[str, str]] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = REQ_RE.match(raw.strip())
        if not match:
            continue
        req_id, title = match.groups()
        if req_id in requirements:
            raise ValueError(f"{path}:{lineno}: duplicate requirement id '{req_id}'")
        requirements[req_id] = {
            "id": req_id,
            "title": title,
            "source": f"{path}:{lineno}",
        }

    if not requirements:
        raise ValueError(f"{path}: no requirement ids found")
    return requirements


def _parse_architecture(path: Path, valid_requirements: set[str]) -> dict[str, dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"missing file: {path}")

    sections: dict[str, dict[str, Any]] = {}
    current_id: str | None = None

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.rstrip()
        arch_match = ARCH_RE.match(line.strip())
        if arch_match:
            arch_id, title = arch_match.groups()
            if arch_id in sections:
                raise ValueError(f"{path}:{lineno}: duplicate architecture id '{arch_id}'")
            current_id = arch_id
            sections[arch_id] = {
                "id": arch_id,
                "title": title,
                "source": f"{path}:{lineno}",
                "type": None,
                "satisfies": [],
            }
            continue

        if current_id is None:
            continue

        if line.startswith("Type:"):
            section_type = line.split(":", 1)[1].strip()
            if section_type not in {"Logical", "Component"}:
                raise ValueError(
                    f"{path}:{lineno}: invalid Type for {current_id}: '{section_type}'"
                )
            sections[current_id]["type"] = section_type
            continue

        if line.startswith("Satisfies:"):
            refs = [part.strip() for part in line.split(":", 1)[1].split(",") if part.strip()]
            if not refs:
                raise ValueError(f"{path}:{lineno}: empty Satisfies list for {current_id}")
            unknown = [ref for ref in refs if ref not in valid_requirements]
            if unknown:
                raise ValueError(
                    f"{path}:{lineno}: {current_id} references unknown requirement ids {unknown}"
                )
            sections[current_id]["satisfies"] = refs

    if not sections:
        raise ValueError(f"{path}: no architecture ids found")

    for arch_id, section in sections.items():
        if section["type"] is None:
            raise ValueError(f"{section['source']}: missing Type field for {arch_id}")
        if not section["satisfies"]:
            raise ValueError(f"{section['source']}: missing Satisfies field for {arch_id}")

    return sections


def _iter_source_files(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for root_name in roots:
        root = Path(root_name)
        if not root.exists():
            raise ValueError(f"missing source root: {root}")
        if root.is_file():
            candidates = [root]
        else:
            candidates = [p for p in root.rglob("*") if p.is_file() and p.suffix in SOURCE_EXTENSIONS]
        for path in sorted(candidates):
            if path not in seen:
                seen.add(path)
                files.append(path)
    return files


def _iter_unit_test_files(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for root_name in roots:
        root = Path(root_name)
        if not root.exists():
            raise ValueError(f"missing unit root: {root}")
        if root.is_file():
            candidates = [root]
        else:
            candidates = [p for p in root.rglob("test_*.py") if p.is_file()]
        for path in sorted(candidates):
            if path.name == "__init__.py":
                continue
            if path not in seen:
                seen.add(path)
                files.append(path)
    return files


def _parse_dd_sources(
    roots: list[str], architecture: dict[str, dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    design_by_id: dict[str, dict[str, Any]] = {}
    failures: list[str] = []

    for path in _iter_source_files(roots):
        lines = path.read_text(encoding="utf-8").splitlines()
        idx = 0
        while idx < len(lines):
            match = DD_RE.match(lines[idx])
            if not match:
                idx += 1
                continue

            dd_id = match.group(1)
            start_lineno = idx + 1
            title: str | None = None
            arch_refs: list[str] = []
            cursor = idx + 1

            while cursor < len(lines):
                line = lines[cursor]
                if not line.strip() or DD_RE.match(line):
                    break
                field_match = DD_FIELD_RE.match(line)
                if not field_match:
                    if line.lstrip().startswith("#"):
                        cursor += 1
                        continue
                    break
                field_name, field_value = field_match.groups()
                if field_name == "Implements":
                    arch_refs = [part.strip() for part in field_value.split(",") if part.strip()]
                elif field_name == "Title":
                    title = field_value.strip()
                cursor += 1

            if not arch_refs:
                failures.append(f"{path}:{start_lineno}: {dd_id} missing Implements field")
                idx = cursor
                continue
            if title is None:
                failures.append(f"{path}:{start_lineno}: {dd_id} missing Title field")
                idx = cursor
                continue

            unknown_arch = [arch_id for arch_id in arch_refs if arch_id not in architecture]
            if unknown_arch:
                failures.append(
                    f"{path}:{start_lineno}: {dd_id} references unknown architecture ids {unknown_arch}"
                )
                idx = cursor
                continue

            location = f"{path}:{start_lineno}"
            existing = design_by_id.get(dd_id)
            if existing is None:
                design_by_id[dd_id] = {
                    "id": dd_id,
                    "title": title,
                    "implements_architecture": sorted(arch_refs),
                    "locations": [location],
                    "implementation": [str(path)],
                }
            else:
                failures.append(
                    f"{path}:{start_lineno}: duplicate DD id '{dd_id}' is not allowed; each function must have a unique DD id"
                )

            idx = cursor

    return design_by_id, failures


def _parse_unit_tests(
    roots: list[str], design_by_id: dict[str, dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    unit_by_id: dict[str, dict[str, Any]] = {}
    failures: list[str] = []

    for path in _iter_unit_test_files(roots):
        lines = path.read_text(encoding="utf-8").splitlines()
        idx = 0
        pending: dict[str, Any] | None = None

        while idx < len(lines):
            line = lines[idx]

            if pending is not None:
                stripped = line.strip()
                if not stripped:
                    idx += 1
                    continue
                if DECORATOR_RE.match(stripped):
                    idx += 1
                    continue
                match_def = UNIT_TEST_DEF_RE.match(line)
                if match_def:
                    test_name = match_def.group(1)
                    ut_id = pending["id"]
                    if ut_id in unit_by_id:
                        failures.append(f"{path}:{pending['line']}: duplicate UT id '{ut_id}'")
                    else:
                        unit_by_id[ut_id] = {
                            "id": ut_id,
                            "type": "unit_case",
                            "title": pending["description"],
                            "description": pending["description"],
                            "precondition": pending["precondition"],
                            "expected_output": pending["expected_output"],
                            "source_design": pending["covers_dd"],
                            "location": {
                                "file": str(path),
                                "selector": test_name,
                            },
                            "status": "active",
                        }
                    pending = None
                    idx += 1
                    continue

                failures.append(
                    f"{path}:{pending['line']}: {pending['id']} must be followed by a unit test function"
                )
                pending = None
                continue

            ut_match = UT_RE.match(line)
            if ut_match:
                ut_id = ut_match.group(1)
                start_lineno = idx + 1
                fields: dict[str, str] = {}
                cursor = idx + 1
                while cursor < len(lines):
                    field_line = lines[cursor]
                    if not field_line.strip() or UT_RE.match(field_line):
                        break
                    field_match = UT_FIELD_RE.match(field_line)
                    if not field_match:
                        if field_line.lstrip().startswith("#"):
                            cursor += 1
                            continue
                        break
                    field_name, field_value = field_match.groups()
                    fields[field_name] = field_value.strip()
                    cursor += 1

                required_fields = [
                    "Test Description",
                    "Precondition",
                    "Expected Output",
                    "Covers DD",
                ]
                missing = [name for name in required_fields if not fields.get(name)]
                if missing:
                    failures.append(
                        f"{path}:{start_lineno}: {ut_id} missing {', '.join(missing)}"
                    )
                    idx = cursor
                    continue

                covers_dd = [part.strip() for part in fields["Covers DD"].split(",") if part.strip()]
                if not covers_dd:
                    failures.append(f"{path}:{start_lineno}: {ut_id} missing Covers DD entries")
                    idx = cursor
                    continue
                unknown_dd = [dd_id for dd_id in covers_dd if dd_id not in design_by_id]
                if unknown_dd:
                    failures.append(
                        f"{path}:{start_lineno}: {ut_id} references unknown design ids {unknown_dd}"
                    )
                    idx = cursor
                    continue

                pending = {
                    "id": ut_id,
                    "line": start_lineno,
                    "description": fields["Test Description"],
                    "precondition": fields["Precondition"],
                    "expected_output": fields["Expected Output"],
                    "covers_dd": sorted(covers_dd),
                }
                idx = cursor
                continue

            test_match = UNIT_TEST_DEF_RE.match(line)
            if test_match:
                failures.append(
                    f"{path}:{idx + 1}: unit test '{test_match.group(1)}' missing UT block"
                )
            idx += 1

        if pending is not None:
            failures.append(
                f"{path}:{pending['line']}: {pending['id']} must be followed by a unit test function"
            )

    return unit_by_id, failures


def main() -> int:
    args = parse_args()

    try:
        requirements = _parse_requirements(Path(args.requirements_doc))
        architecture = _parse_architecture(Path(args.architecture_doc), set(requirements))
        test_items = _load_items(Path(args.tests), "tests")
        design_by_id, dd_failures = _parse_dd_sources(args.source_root, architecture)
        unit_tests, ut_failures = _parse_unit_tests(args.unit_root, design_by_id)
        structural_failures = [*dd_failures, *ut_failures]
    except ValueError as exc:
        print(f"[qa-trace] FAILED: {exc}", file=sys.stderr)
        return 2

    test_by_id: dict[str, dict[str, Any]] = {}

    req_to_arch: dict[str, set[str]] = defaultdict(set)
    arch_to_design: dict[str, set[str]] = defaultdict(set)
    dd_to_ut: dict[str, set[str]] = defaultdict(set)
    req_to_e2e: dict[str, set[str]] = defaultdict(set)
    arch_to_it: dict[str, set[str]] = defaultdict(set)
    req_to_ut: dict[str, set[str]] = defaultdict(set)

    coverage_gaps: dict[str, list[str]] = {
        "requirements_without_e2e": [],
        "architecture_without_dd": [],
        "dd_without_ut": [],
        "unit_tests_without_design": [],
        "e2e_tests_without_requirements": [],
        "integration_tests_without_architecture": [],
    }

    for arch_id, section in architecture.items():
        for req_id in section["satisfies"]:
            req_to_arch[req_id].add(arch_id)

    for design_id, item in design_by_id.items():
        for arch_id in item["implements_architecture"]:
            arch_to_design[arch_id].add(design_id)

    for test_id, item in sorted(unit_tests.items()):
        if test_id in test_by_id:
            structural_failures.append(f"tests: duplicate id '{test_id}'")
            continue
        test_by_id[test_id] = item
        for design_id in item["source_design"]:
            dd_to_ut[design_id].add(test_id)
            for arch_id in design_by_id[design_id]["implements_architecture"]:
                for req_id in architecture[arch_id]["satisfies"]:
                    req_to_ut[req_id].add(test_id)

    for item in test_items:
        test_id = item.get("id")
        if not isinstance(test_id, str) or not test_id:
            structural_failures.append("tests: item is missing non-empty 'id'")
            continue
        if test_id in test_by_id:
            structural_failures.append(f"tests: duplicate id '{test_id}'")
            continue
        test_by_id[test_id] = item

        test_type = item.get("type")
        if test_type not in TEST_TYPES:
            structural_failures.append(f"{test_id}: invalid type '{test_type}'")
            continue

        if "source_requirements" in item:
            try:
                req_refs = _as_non_empty_str_list(
                    item.get("source_requirements"),
                    field="source_requirements",
                    item_id=test_id,
                )
            except ValueError as exc:
                structural_failures.append(str(exc))
                req_refs = []
        else:
            req_refs = []

        if "source_architecture" in item:
            try:
                arch_refs = _as_non_empty_str_list(
                    item.get("source_architecture"),
                    field="source_architecture",
                    item_id=test_id,
                )
            except ValueError as exc:
                structural_failures.append(str(exc))
                arch_refs = []
        else:
            arch_refs = []

        if "source_design" in item:
            structural_failures.append(
                f"{test_id}: source_design is no longer allowed in trace/tests.yaml; move unit trace into tests/unit/**"
            )

        if test_type in {"e2e_suite", "e2e_case"}:
            if arch_refs:
                structural_failures.append(f"{test_id}: {test_type} must not use source_architecture")
            if not req_refs:
                coverage_gaps["e2e_tests_without_requirements"].append(test_id)
            for req_id in req_refs:
                if req_id not in requirements:
                    structural_failures.append(f"{test_id}: unknown requirement id '{req_id}'")
                    continue
                req_to_e2e[req_id].add(test_id)

        elif test_type == "integration_case":
            if req_refs:
                structural_failures.append(f"{test_id}: integration_case must not use source_requirements")
            if not arch_refs:
                coverage_gaps["integration_tests_without_architecture"].append(test_id)
            for arch_id in arch_refs:
                if arch_id not in architecture:
                    structural_failures.append(f"{test_id}: unknown architecture id '{arch_id}'")
                    continue
                arch_to_it[arch_id].add(test_id)

        location = item.get("location")
        if not isinstance(location, dict):
            structural_failures.append(f"{test_id}: location must be a map")
            continue

        location_file = location.get("file")
        selector = location.get("selector", "")
        if not isinstance(location_file, str) or not location_file:
            structural_failures.append(f"{test_id}: location.file must be a non-empty string")
        else:
            file_path = Path(location_file)
            if not file_path.exists():
                structural_failures.append(f"{test_id}: location.file not found '{location_file}'")
            elif isinstance(selector, str) and selector:
                try:
                    _check_file_contains(file_path, selector, context=test_id)
                except ValueError as exc:
                    structural_failures.append(str(exc))

        if test_type == "e2e_suite":
            evidence_prefixes = item.get("evidence_prefixes", [])
            if not isinstance(evidence_prefixes, list) or not all(
                isinstance(x, str) and x for x in evidence_prefixes
            ):
                structural_failures.append(f"{test_id}: evidence_prefixes must be a string list")
            elif not evidence_prefixes:
                structural_failures.append(f"{test_id}: evidence_prefixes is empty")

    coverage_gaps["requirements_without_e2e"] = sorted(
        req_id for req_id in requirements if req_id not in req_to_e2e
    )
    coverage_gaps["architecture_without_dd"] = sorted(
        arch_id for arch_id in architecture if arch_id not in arch_to_design
    )
    coverage_gaps["dd_without_ut"] = sorted(
        design_id for design_id in design_by_id if design_id not in dd_to_ut
    )
    for key in coverage_gaps:
        coverage_gaps[key].sort()

    report = {
        "summary": {
            "requirements_total": len(requirements),
            "architecture_total": len(architecture),
            "design_total": len(design_by_id),
            "tests_total": len(test_by_id),
            "unit_tests_total": len(unit_tests),
            "structural_failures": len(structural_failures),
            "coverage_gap_totals": {key: len(vals) for key, vals in coverage_gaps.items()},
        },
        "requirements": {
            req_id: {
                "title": requirements[req_id]["title"],
                "architecture": sorted(req_to_arch.get(req_id, set())),
                "e2e_tests": sorted(req_to_e2e.get(req_id, set())),
                "unit_tests_via_dd": sorted(req_to_ut.get(req_id, set())),
            }
            for req_id in sorted(requirements)
        },
        "architecture": {
            arch_id: {
                "title": section["title"],
                "type": section["type"],
                "satisfies": sorted(section["satisfies"]),
                "design": sorted(arch_to_design.get(arch_id, set())),
                "integration_tests": sorted(arch_to_it.get(arch_id, set())),
            }
            for arch_id, section in sorted(architecture.items())
        },
        "design": {
            design_id: {
                "title": item["title"],
                "implements_architecture": sorted(item["implements_architecture"]),
                "implementation": sorted(item["implementation"]),
                "locations": sorted(item["locations"]),
                "unit_tests": sorted(dd_to_ut.get(design_id, set())),
            }
            for design_id, item in sorted(design_by_id.items())
        },
        "tests": {
            test_id: {
                "type": test_by_id[test_id]["type"],
                "title": test_by_id[test_id].get("title", ""),
                "location": test_by_id[test_id].get("location", {}),
                "source_requirements": sorted(test_by_id[test_id].get("source_requirements", [])),
                "source_architecture": sorted(test_by_id[test_id].get("source_architecture", [])),
                "source_design": sorted(test_by_id[test_id].get("source_design", [])),
            }
            for test_id in sorted(test_by_id)
        },
        "structural_failures": structural_failures,
        "coverage_gaps": coverage_gaps,
    }

    design_index = {
        "design": [
            {
                "id": design_id,
                "title": item["title"],
                "implements_architecture": sorted(item["implements_architecture"]),
                "implementation": sorted(item["implementation"]),
                "locations": sorted(item["locations"]),
            }
            for design_id, item in sorted(design_by_id.items())
        ]
    }

    report_path = Path(args.report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    design_report_path = Path(args.design_report_json)
    design_report_path.parent.mkdir(parents=True, exist_ok=True)
    design_report_path.write_text(json.dumps(design_index, indent=2, sort_keys=True), encoding="utf-8")

    if structural_failures:
        print("[qa-trace] FAILED", file=sys.stderr)
        for item in structural_failures:
            print(f"  - {item}", file=sys.stderr)
        print(f"[qa-trace] report: {report_path}", file=sys.stderr)
        return 1

    gap_total = sum(len(vals) for vals in coverage_gaps.values())
    print(
        "[qa-trace] PASSED "
        f"(requirements={len(requirements)}, architecture={len(architecture)}, design={len(design_by_id)}, "
        f"tests={len(test_by_id)}, coverage_gaps={gap_total})"
    )
    print(f"[qa-trace] report: {report_path}")
    print(f"[qa-trace] design index: {design_report_path}")
    if gap_total:
        print("[qa-trace] coverage gaps:")
        for key, vals in coverage_gaps.items():
            if vals:
                print(f"  - {key}: {len(vals)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
