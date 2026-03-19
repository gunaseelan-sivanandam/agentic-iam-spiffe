#!/usr/bin/env python3
"""Validate strict layered traceability from authored docs and trace maps."""

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


TEST_TYPES = {"e2e_suite", "e2e_case", "integration_case", "unit_case"}
REQ_RE = re.compile(r"^#{2,3}\s+(REQ-[A-Z0-9.-]+)\s+—\s+(.+?)\s*$")
ARCH_RE = re.compile(r"^##\s+(ARCH-\d{3})\s+(.+?)\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements-doc", default="docs/requirements.md")
    parser.add_argument("--architecture-doc", default="docs/architecture.md")
    parser.add_argument("--design", default="trace/design.yaml")
    parser.add_argument("--tests", default="trace/tests.yaml")
    parser.add_argument("--report-json", default="artifacts/quality/traceability_report.json")
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


def _as_str_list(value: Any, *, field: str, item_id: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f"{item_id}: '{field}' must be a non-empty string list")
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
            raw_refs = line.split(":", 1)[1].strip()
            refs = [part.strip() for part in raw_refs.split(",") if part.strip()]
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


def main() -> int:
    args = parse_args()

    try:
        requirements = _parse_requirements(Path(args.requirements_doc))
        architecture = _parse_architecture(Path(args.architecture_doc), set(requirements))
        design_items = _load_items(Path(args.design), "design")
        test_items = _load_items(Path(args.tests), "tests")
    except ValueError as exc:
        print(f"[qa-trace] FAILED: {exc}", file=sys.stderr)
        return 2

    failures: list[str] = []

    design_by_id: dict[str, dict[str, Any]] = {}
    test_by_id: dict[str, dict[str, Any]] = {}

    req_to_arch: dict[str, set[str]] = defaultdict(set)
    arch_to_design: dict[str, set[str]] = defaultdict(set)
    req_to_design: dict[str, set[str]] = defaultdict(set)
    design_to_tests: dict[str, set[str]] = defaultdict(set)
    req_to_tests: dict[str, set[str]] = defaultdict(set)
    test_to_req: dict[str, set[str]] = defaultdict(set)

    for arch_id, section in architecture.items():
        for req_id in section["satisfies"]:
            req_to_arch[req_id].add(arch_id)

    for item in design_items:
        design_id = item.get("id")
        if not isinstance(design_id, str) or not design_id:
            failures.append("design: item is missing non-empty 'id'")
            continue
        if design_id in design_by_id:
            failures.append(f"design: duplicate id '{design_id}'")
            continue
        design_by_id[design_id] = item

        if "source_requirements" in item:
            failures.append(
                f"{design_id}: direct source_requirements is not allowed in strict layered model"
            )

        try:
            arch_refs = _as_str_list(
                item.get("source_architecture", []),
                field="source_architecture",
                item_id=design_id,
            )
            impl_paths = _as_str_list(
                item.get("implementation", []),
                field="implementation",
                item_id=design_id,
            )
        except ValueError as exc:
            failures.append(str(exc))
            continue

        if not arch_refs:
            failures.append(f"{design_id}: source_architecture is empty")
        if not impl_paths:
            failures.append(f"{design_id}: implementation is empty")

        for arch_id in arch_refs:
            if arch_id not in architecture:
                failures.append(f"{design_id}: unknown architecture id '{arch_id}'")
                continue
            arch_to_design[arch_id].add(design_id)
            for req_id in architecture[arch_id]["satisfies"]:
                req_to_design[req_id].add(design_id)

        for impl in impl_paths:
            if not Path(impl).exists():
                failures.append(f"{design_id}: implementation path not found '{impl}'")

    for item in test_items:
        test_id = item.get("id")
        if not isinstance(test_id, str) or not test_id:
            failures.append("tests: item is missing non-empty 'id'")
            continue
        if test_id in test_by_id:
            failures.append(f"tests: duplicate id '{test_id}'")
            continue
        test_by_id[test_id] = item

        if "source_requirements" in item:
            failures.append(
                f"{test_id}: direct source_requirements is not allowed in strict layered model"
            )

        test_type = item.get("type")
        if test_type not in TEST_TYPES:
            failures.append(f"{test_id}: invalid type '{test_type}'")

        try:
            design_refs = _as_str_list(
                item.get("source_design", []),
                field="source_design",
                item_id=test_id,
            )
        except ValueError as exc:
            failures.append(str(exc))
            continue

        if not design_refs:
            failures.append(f"{test_id}: source_design is empty")

        location = item.get("location")
        if not isinstance(location, dict):
            failures.append(f"{test_id}: location must be a map")
            continue

        location_file = location.get("file")
        selector = location.get("selector", "")
        if not isinstance(location_file, str) or not location_file:
            failures.append(f"{test_id}: location.file must be a non-empty string")
        else:
            file_path = Path(location_file)
            if not file_path.exists():
                failures.append(f"{test_id}: location.file not found '{location_file}'")
            elif isinstance(selector, str) and selector:
                try:
                    _check_file_contains(file_path, selector, context=test_id)
                except ValueError as exc:
                    failures.append(str(exc))

        if test_type == "e2e_suite":
            try:
                evidence_prefixes = _as_str_list(
                    item.get("evidence_prefixes", []),
                    field="evidence_prefixes",
                    item_id=test_id,
                )
            except ValueError as exc:
                failures.append(str(exc))
                evidence_prefixes = []
            if not evidence_prefixes:
                failures.append(f"{test_id}: evidence_prefixes is empty")

        for design_id in design_refs:
            if design_id not in design_by_id:
                failures.append(f"{test_id}: unknown design id '{design_id}'")
                continue
            design_to_tests[design_id].add(test_id)

            for arch_id in design_by_id[design_id].get("source_architecture", []):
                if arch_id not in architecture:
                    continue
                for req_id in architecture[arch_id]["satisfies"]:
                    req_to_tests[req_id].add(test_id)
                    test_to_req[test_id].add(req_id)

    missing_arch = sorted(req_id for req_id in requirements if req_id not in req_to_arch)
    missing_design = sorted(req_id for req_id in requirements if req_id not in req_to_design)
    orphan_logical_arch = sorted(
        arch_id
        for arch_id, section in architecture.items()
        if section["type"] == "Logical" and arch_id not in arch_to_design
    )
    orphan_design = sorted(design_id for design_id in design_by_id if design_id not in design_to_tests)

    if missing_arch:
        failures.append(f"requirements missing architecture mapping: {missing_arch}")
    if missing_design:
        failures.append(f"requirements missing downstream design mapping: {missing_design}")
    if orphan_logical_arch:
        failures.append(
            f"logical architecture ids without downstream design mapping: {orphan_logical_arch}"
        )
    if orphan_design:
        failures.append(f"design ids without downstream tests mapping: {orphan_design}")

    report = {
        "summary": {
            "requirements_total": len(requirements),
            "architecture_total": len(architecture),
            "design_total": len(design_by_id),
            "tests_total": len(test_by_id),
            "missing_arch_mappings": len(missing_arch),
            "missing_design_mappings": len(missing_design),
            "orphan_logical_arch": len(orphan_logical_arch),
            "orphan_design": len(orphan_design),
        },
        "requirements": {
            req_id: {
                "title": requirements[req_id]["title"],
                "architecture": sorted(req_to_arch.get(req_id, set())),
                "design": sorted(req_to_design.get(req_id, set())),
                "tests": sorted(req_to_tests.get(req_id, set())),
            }
            for req_id in sorted(requirements)
        },
        "architecture": {
            arch_id: {
                "title": section["title"],
                "type": section["type"],
                "satisfies": sorted(section["satisfies"]),
                "design": sorted(arch_to_design.get(arch_id, set())),
            }
            for arch_id, section in sorted(architecture.items())
        },
        "tests": {
            test_id: {
                "type": test_by_id[test_id]["type"],
                "source_design": sorted(test_by_id[test_id].get("source_design", [])),
                "derived_requirements": sorted(test_to_req.get(test_id, set())),
            }
            for test_id in sorted(test_by_id)
        },
    }

    report_path = Path(args.report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if failures:
        print("[qa-trace] FAILED", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        print(f"[qa-trace] report: {report_path}", file=sys.stderr)
        return 1

    print(
        "[qa-trace] PASSED "
        f"(requirements={len(requirements)}, architecture={len(architecture)}, "
        f"design={len(design_by_id)}, tests={len(test_by_id)})"
    )
    print(f"[qa-trace] report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
