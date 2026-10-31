#!/usr/bin/env python3
"""Validate layered traceability with explicit gap reporting.

Trace model (AGENTS.md "Traceability model and IDs"): every requirement is traced the same way,
requirement -> test ID in trace/tests.yaml -> test specification -> implementation -> stored, checked
result. A requirement is proved by an E2E test or a static test (a gate whose tooling tests show it
fails on each kind of violation); its status also follows the deployment register, so a requirement
whose asset has a known violation, or the non-root rule within its grace period, is not proved.

Coverage gaps are reported. With --mode pr --base <ref>, a gap the change adds compared with its
merge-base fails, unless trace/tests.yaml lists it under accepted_gaps (one line: gap, reason,
expiry). Both sides are computed by this script: the merge-base tree is exported and this same code
runs on it, so both use the same rules and gap names.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # nosec B404 - fixed git/tar/python argv, no shell
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
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


TEST_TYPES = {"e2e_suite", "e2e_case", "integration_case", "static_test"}
REQUIREMENT_PROOF_TYPES = {"e2e_suite", "e2e_case", "static_test"}
GAP_CATEGORIES = (
    "requirements_without_proof",
    "architecture_without_implementation",
    "dd_without_ut",
    "unit_tests_without_design",
    "tests_without_requirements",
    "integration_tests_without_architecture",
)
ARCH_LIST_FIELDS = {"Satisfies": "satisfies", "Implemented by": "implemented_by"}
NEGATIVE_CONTROL_RE = re.compile(r"^([^:\s]+)::([A-Za-z_][A-Za-z0-9_]*)$")
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
    parser.add_argument("--source-root", action="append", default=["services", "scripts"])
    parser.add_argument("--unit-root", action="append", default=["tests/unit"])
    parser.add_argument("--tests", default="trace/tests.yaml")
    parser.add_argument("--report-json", default="artifacts/quality/traceability_report.json")
    parser.add_argument("--design-report-json", default="artifacts/quality/design_index.json")
    parser.add_argument("--register", default="security/invariants.yaml")
    parser.add_argument("--mode", choices=["pr", "push"], required=True,
                        help="pr: fail on a gap the change adds compared with --base; push: report only")
    parser.add_argument("--base", help="ref whose merge-base with HEAD is the comparison base (pr mode)")
    parser.add_argument("--now", help="ISO time for expiry and grace checks (tests); default: now")
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


def _parse_arch_field(line: str, section: dict[str, Any], where: str, valid_requirements: set[str]) -> None:
    """One `Type:`, `Satisfies:` or `Implemented by:` line of an architecture section."""
    field_name, _, value = line.partition(":")
    if field_name == "Type":
        if value.strip() not in {"Logical", "Component"}:
            raise ValueError(f"{where}: invalid Type for {section['id']}: '{value.strip()}'")
        section["type"] = value.strip()
    elif field_name in ARCH_LIST_FIELDS:
        section[ARCH_LIST_FIELDS[field_name]] = _arch_list(field_name, value, section["id"], where, valid_requirements)


def _arch_list(field_name: str, value: str, arch_id: str, where: str, valid_requirements: set[str]) -> list[str]:
    parts = [part.strip().strip("`") for part in value.split(",") if part.strip()]
    if not parts:
        raise ValueError(f"{where}: empty {field_name} list for {arch_id}")
    unknown = [ref for ref in parts if ref not in valid_requirements]
    if field_name == "Satisfies" and unknown:
        raise ValueError(f"{where}: {arch_id} references unknown requirement ids {unknown}")
    return parts


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
                "implemented_by": [],
            }
            continue

        if current_id is not None:
            _parse_arch_field(line, sections[current_id], f"{path}:{lineno}", valid_requirements)

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


def _str_list(item: dict[str, Any], field: str, test_id: str, failures: list[str]) -> list[str]:
    if field not in item:
        return []
    try:
        return _as_non_empty_str_list(item.get(field), field=field, item_id=test_id)
    except ValueError as exc:
        failures.append(str(exc))
        return []


def _check_location(item: dict[str, Any], test_id: str, failures: list[str]) -> None:
    location = item.get("location")
    if not isinstance(location, dict):
        failures.append(f"{test_id}: location must be a map")
        return
    location_file = location.get("file")
    selector = location.get("selector", "")
    if not isinstance(location_file, str) or not location_file:
        failures.append(f"{test_id}: location.file must be a non-empty string")
        return
    file_path = Path(location_file)
    if not file_path.exists():
        failures.append(f"{test_id}: location.file not found '{location_file}'")
    elif isinstance(selector, str) and selector:
        try:
            _check_file_contains(file_path, selector, context=test_id)
        except ValueError as exc:
            failures.append(str(exc))


def _gate_problem(gate: Any) -> str | None:
    target = gate[len("make "):].strip() if isinstance(gate, str) and gate.startswith("make ") else ""
    if not target:
        return "gate must be 'make <target>'"
    makefile = Path("Makefile")
    if not makefile.exists() or not re.search(rf"^{re.escape(target)}:", makefile.read_text(encoding="utf-8"), re.M):
        return f"gate target '{target}' not found in Makefile"
    return None


def _control_problem(control: str) -> str | None:
    match = NEGATIVE_CONTROL_RE.match(control)
    if not match:
        return f"negative control '{control}' must be <file>::<test>"
    control_file, name = match.groups()
    if not Path(control_file).exists():
        return f"negative control file not found '{control_file}'"
    if not re.search(rf"^\s*def {name}\(", Path(control_file).read_text(encoding="utf-8"), re.M):
        return f"negative control test '{name}' not found in {control_file}"
    return None


def _check_static_test(item: dict[str, Any], test_id: str, failures: list[str]) -> None:
    """A static test names its gate (a make target), its negative-control tests and its result."""
    controls = _str_list(item, "negative_controls", test_id, failures)
    problems = [_gate_problem(item.get("gate")), *(_control_problem(c) for c in controls)]
    if not controls:
        problems.append("negative_controls must list at least one <file>::<test> entry")
    if not isinstance(item.get("result"), str) or not item.get("result"):
        problems.append("result must name the stored, checked result")
    failures += [f"{test_id}: {problem}" for problem in problems if problem]


def _link_proof(test_id: str, test_type: str, req_refs: list[str], arch_refs: list[str], ctx: dict[str, Any]) -> None:
    """An E2E or static test proves the requirements it names."""
    if arch_refs:
        ctx["failures"].append(f"{test_id}: {test_type} must not use source_architecture")
    if not req_refs:
        ctx["gaps"]["tests_without_requirements"].append(test_id)
    for req_id in req_refs:
        if req_id not in ctx["requirements"]:
            ctx["failures"].append(f"{test_id}: unknown requirement id '{req_id}'")
            continue
        ctx["req_proofs"][req_id].add(test_id)
        ctx["req_proof_kinds"][req_id].add("static" if test_type == "static_test" else "e2e")


def _link_integration(test_id: str, req_refs: list[str], arch_refs: list[str], ctx: dict[str, Any]) -> None:
    if req_refs:
        ctx["failures"].append(f"{test_id}: integration_case must not use source_requirements")
    if not arch_refs:
        ctx["gaps"]["integration_tests_without_architecture"].append(test_id)
    for arch_id in arch_refs:
        if arch_id not in ctx["architecture"]:
            ctx["failures"].append(f"{test_id}: unknown architecture id '{arch_id}'")
            continue
        ctx["arch_to_it"][arch_id].add(test_id)


def _check_test_item(item: dict[str, Any], test_id: str, ctx: dict[str, Any]) -> None:
    failures: list[str] = ctx["failures"]
    test_type = item.get("type")
    req_refs = _str_list(item, "source_requirements", test_id, failures)
    arch_refs = _str_list(item, "source_architecture", test_id, failures)
    if "source_design" in item:
        failures.append(
            f"{test_id}: source_design is no longer allowed in trace/tests.yaml; move unit trace into tests/unit/**"
        )
    if test_type in REQUIREMENT_PROOF_TYPES:
        _link_proof(test_id, test_type, req_refs, arch_refs, ctx)
    else:
        _link_integration(test_id, req_refs, arch_refs, ctx)
    if test_type == "static_test":
        _check_static_test(item, test_id, failures)
        return
    _check_location(item, test_id, failures)
    if test_type == "e2e_suite":
        evidence_prefixes = item.get("evidence_prefixes", [])
        if not isinstance(evidence_prefixes, list) or not all(isinstance(x, str) and x for x in evidence_prefixes):
            failures.append(f"{test_id}: evidence_prefixes must be a string list")
        elif not evidence_prefixes:
            failures.append(f"{test_id}: evidence_prefixes is empty")


def _retired_ids(data: dict[str, Any], failures: list[str]) -> dict[str, str]:
    retired: dict[str, str] = {}
    for entry in data.get("retired_ids") or []:
        if not isinstance(entry, dict) or not entry.get("id") or not entry.get("reason"):
            failures.append(f"retired_ids: each entry needs id and reason: {entry!r}")
            continue
        retired[str(entry["id"])] = str(entry["reason"])
    return retired


def _load_register(path: Path) -> dict[str, Any]:
    """The deployment register, or an empty one where it does not exist (older trees)."""
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: top-level document must be a map")
    return raw


def _register_holds_back(register: dict[str, Any], now: datetime) -> dict[str, str]:
    """Requirement id -> why the register says it is not proved (known violation, non-root grace)."""
    from qa_deploy import NONROOT_GRACE_END, NONROOT_REQUIREMENT  # same scripts/ directory

    reasons = _known_violation_reasons(register)
    services = register.get("services") or {}
    if now < NONROOT_GRACE_END and any((s or {}).get("root") == "grandfathered" for s in services.values()):
        last_day = (NONROOT_GRACE_END - timedelta(days=1)).date().isoformat()
        reasons.setdefault(NONROOT_REQUIREMENT, f"grace until {last_day}")
    return reasons


def _known_violation_reasons(register: dict[str, Any]) -> dict[str, str]:
    assets = register.get("assets") or {}
    opls: dict[str, set[str]] = defaultdict(set)
    for row in register.get("known_violations") or []:
        requirement = (assets.get(row.get("asset")) or {}).get("requirement")
        if requirement:
            opls[requirement].add(str(row.get("opl")))
    return {req: f"known violation {', '.join(sorted(ids))}" for req, ids in opls.items()}


def _requirement_status(req_id: str, ctx: dict[str, Any], held_back: dict[str, str]) -> str:
    kinds = ctx["req_proof_kinds"].get(req_id, set())
    if not kinds:
        return "not proved: no test"
    if req_id in held_back:
        return f"not proved: {held_back[req_id]}"
    return "proved: " + ", ".join(sorted(kinds))


def _link_architecture(architecture: dict[str, dict[str, Any]], design_by_id: dict[str, dict[str, Any]],
                       failures: list[str]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    req_to_arch: dict[str, set[str]] = defaultdict(set)
    for arch_id, section in architecture.items():
        for req_id in section["satisfies"]:
            req_to_arch[req_id].add(arch_id)
        failures += [f"{arch_id}: Implemented by file not found '{name}'"
                     for name in section["implemented_by"] if not Path(name).exists()]
    arch_to_design: dict[str, set[str]] = defaultdict(set)
    for design_id, item in design_by_id.items():
        for arch_id in item["implements_architecture"]:
            arch_to_design[arch_id].add(design_id)
    return req_to_arch, arch_to_design


def _collect_tests(test_items: list[dict[str, Any]], unit_tests: dict[str, dict[str, Any]],
                   retired: dict[str, str], ctx: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
    failures: list[str] = ctx["failures"]
    test_by_id: dict[str, dict[str, Any]] = dict(sorted(unit_tests.items()))
    dd_to_ut: dict[str, set[str]] = defaultdict(set)
    for test_id, item in test_by_id.items():
        for design_id in item["source_design"]:
            dd_to_ut[design_id].add(test_id)
    for item in test_items:
        test_id = item.get("id")
        if not isinstance(test_id, str) or not test_id:
            failures.append("tests: item is missing non-empty 'id'")
            continue
        if test_id in test_by_id:
            failures.append(f"tests: duplicate id '{test_id}'")
            continue
        if test_id in retired:
            failures.append(f"{test_id}: retired id reused ({retired[test_id]})")
        test_by_id[test_id] = item
        if item.get("type") not in TEST_TYPES:
            failures.append(f"{test_id}: invalid type '{item.get('type')}'")
            continue
        _check_test_item(item, test_id, ctx)
    return test_by_id, dd_to_ut


def _report(inputs: dict[str, Any], ctx: dict[str, Any], links: dict[str, Any], status: dict[str, str]) -> dict[str, Any]:
    requirements, architecture, design_by_id = inputs["requirements"], inputs["architecture"], inputs["design"]
    test_by_id, gaps = links["tests"], ctx["gaps"]
    return {
        "summary": {
            "requirements_total": len(requirements),
            "architecture_total": len(architecture),
            "design_total": len(design_by_id),
            "tests_total": len(test_by_id),
            "unit_tests_total": len(inputs["unit_tests"]),
            "structural_failures": len(ctx["failures"]),
            "coverage_gap_totals": {key: len(vals) for key, vals in gaps.items()},
        },
        "requirements": {
            req_id: {"title": requirements[req_id]["title"], "status": status[req_id],
                     "architecture": sorted(links["req_to_arch"].get(req_id, set())),
                     "proofs": sorted(ctx["req_proofs"].get(req_id, set()))}
            for req_id in sorted(requirements)
        },
        "architecture": {
            arch_id: {"title": section["title"], "type": section["type"], "satisfies": sorted(section["satisfies"]),
                      "design": sorted(links["arch_to_design"].get(arch_id, set())),
                      "implemented_by": section["implemented_by"],
                      "integration_tests": sorted(ctx["arch_to_it"].get(arch_id, set()))}
            for arch_id, section in sorted(architecture.items())
        },
        "design": {
            design_id: {"title": item["title"], "implements_architecture": sorted(item["implements_architecture"]),
                        "implementation": sorted(item["implementation"]), "locations": sorted(item["locations"]),
                        "unit_tests": sorted(links["dd_to_ut"].get(design_id, set()))}
            for design_id, item in sorted(design_by_id.items())
        },
        "tests": {
            test_id: {"type": item["type"], "title": item.get("title", ""),
                      "source_requirements": sorted(item.get("source_requirements") or []),
                      "source_architecture": sorted(item.get("source_architecture") or [])}
            for test_id, item in sorted(test_by_id.items())
        },
        "accepted_gaps": inputs["trace"].get("accepted_gaps") or [],
        "structural_failures": ctx["failures"],
        "coverage_gaps": gaps,
    }


def _load_inputs(args: argparse.Namespace) -> dict[str, Any]:
    requirements = _parse_requirements(Path(args.requirements_doc))
    architecture = _parse_architecture(Path(args.architecture_doc), set(requirements))
    design_by_id, dd_failures = _parse_dd_sources(args.source_root, architecture)
    unit_tests, ut_failures = _parse_unit_tests(args.unit_root, design_by_id)
    return {
        "requirements": requirements, "architecture": architecture, "design": design_by_id,
        "unit_tests": unit_tests, "trace": _load_yaml(Path(args.tests)),
        "test_items": _load_items(Path(args.tests), "tests"), "register": _load_register(Path(args.register)),
        "failures": [*dd_failures, *ut_failures],
    }


def compute(args: argparse.Namespace, now: datetime) -> dict[str, Any]:
    """The full trace of the tree in the current directory; raises ValueError on unreadable inputs."""
    inputs = _load_inputs(args)
    failures = inputs["failures"]
    gaps: dict[str, list[str]] = {name: [] for name in GAP_CATEGORIES}
    ctx: dict[str, Any] = {
        "failures": failures, "gaps": gaps, "requirements": inputs["requirements"],
        "architecture": inputs["architecture"], "req_proofs": defaultdict(set),
        "req_proof_kinds": defaultdict(set), "arch_to_it": defaultdict(set),
    }
    retired = _retired_ids(inputs["trace"], failures)
    failures += [f"{d}: retired id reused ({retired[d]})" for d in inputs["design"] if d in retired]
    req_to_arch, arch_to_design = _link_architecture(inputs["architecture"], inputs["design"], failures)
    test_by_id, dd_to_ut = _collect_tests(inputs["test_items"], inputs["unit_tests"], retired, ctx)

    held_back = _register_holds_back(inputs["register"], now)
    status = {req_id: _requirement_status(req_id, ctx, held_back) for req_id in inputs["requirements"]}
    links = {"tests": test_by_id, "dd_to_ut": dd_to_ut, "req_to_arch": req_to_arch, "arch_to_design": arch_to_design}
    _complete_gaps(gaps, status, inputs, links)
    return _report(inputs, ctx, links, status)


def _complete_gaps(gaps: dict[str, list[str]], status: dict[str, str], inputs: dict[str, Any],
                   links: dict[str, Any]) -> None:
    gaps["requirements_without_proof"] = [r for r, s in status.items() if s.startswith("not proved")]
    gaps["architecture_without_implementation"] = [
        a for a, s in inputs["architecture"].items() if a not in links["arch_to_design"] and not s["implemented_by"]]
    gaps["dd_without_ut"] = [d for d in inputs["design"] if d not in links["dd_to_ut"]]
    for key in gaps:
        gaps[key].sort()


def gap_ids(gaps: dict[str, list[str]]) -> set[str]:
    return {f"{category}:{item}" for category, items in gaps.items() for item in items}


def check_accepted_gaps(entries: Any, head_gaps: set[str], now: datetime) -> tuple[set[str], list[str]]:
    """Valid accepted gaps, and a failure for each malformed, expired or stale entry."""
    if not isinstance(entries, list):
        return set(), ["accepted_gaps must be a list"]
    accepted: set[str] = set()
    failures: list[str] = []
    for entry in entries:
        gap = entry.get("gap") if isinstance(entry, dict) else None
        expires = entry.get("expires") if isinstance(entry, dict) else None
        if not gap or not entry.get("reason") or not isinstance(expires, date):
            failures.append(f"accepted_gaps: needs gap, reason and expires (YYYY-MM-DD): {entry!r}")
            continue
        if now >= datetime.combine(expires + timedelta(days=1), time(), tzinfo=timezone.utc):
            failures.append(f"accepted gap {gap} expired on {expires.isoformat()}")
        elif gap not in head_gaps:
            failures.append(f"accepted gap {gap} does not exist; remove the entry")
        else:
            accepted.add(gap)
    return accepted, failures


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def base_gaps(base_ref: str, args: argparse.Namespace) -> set[str]:
    """Gaps of the merge-base of HEAD and base_ref, computed by this script on an export of that tree."""
    try:
        merge_base = _git("merge-base", "HEAD", base_ref)
    except (subprocess.CalledProcessError, OSError) as exc:
        raise ValueError(f"cannot resolve the merge-base of HEAD and '{base_ref}' (full history needed)") from exc
    with tempfile.TemporaryDirectory(prefix="qa-trace-base-") as tmp:
        archive = subprocess.run(["git", "archive", "--format=tar", merge_base], check=True, capture_output=True)
        subprocess.run(["tar", "-x", "-C", tmp], input=archive.stdout, check=True, capture_output=True)
        report = Path(tmp) / "base_trace.json"
        cmd = [sys.executable, str(Path(__file__).resolve()), "--mode", "push", "--report-json", str(report),
               "--design-report-json", str(Path(tmp) / "base_design.json")]
        if args.now:
            cmd += ["--now", args.now]
        run = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, check=False)
        if run.returncode not in (0, 1) or not report.exists():
            raise ValueError(f"cannot read the trace inputs of the merge-base {merge_base[:12]}: {run.stderr.strip()}")
        return gap_ids(json.loads(report.read_text(encoding="utf-8"))["coverage_gaps"])


def gap_gate(report: dict[str, Any], args: argparse.Namespace, now: datetime) -> list[str]:
    """PR mode: a failure for each gap the change adds that no valid accepted_gaps entry covers."""
    head = gap_ids(report["coverage_gaps"])
    accepted, failures = check_accepted_gaps(report["accepted_gaps"], head, now)
    if args.mode != "pr":
        report["gap_gate"] = {"mode": "push", "accepted_gap_problems": failures}
        return []
    if not args.base:
        return ["--mode pr needs --base <ref>"]
    base = base_gaps(args.base, args)
    new = sorted(head - base)
    failures += [f"new coverage gap {gap} (not on the merge-base); prove it or add an accepted_gaps entry"
                 for gap in new if gap not in accepted]
    report["gap_gate"] = {"mode": "pr", "base": args.base, "new_gaps": new, "closed_gaps": sorted(base - head),
                          "accepted": sorted(accepted), "failures": failures}
    return failures


def _now(args: argparse.Namespace) -> datetime:
    if not args.now:
        return datetime.now(timezone.utc)
    value = datetime.fromisoformat(args.now)
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _write(path_name: str, payload: dict[str, Any]) -> Path:
    path = Path(path_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return path


def _print_result(report: dict[str, Any], gate_failures: list[str], report_path: Path) -> int:
    failures = report["structural_failures"]
    if failures or gate_failures:
        print("[qa-trace] FAILED", file=sys.stderr)
        for item in [*failures, *gate_failures]:
            print(f"  - {item}", file=sys.stderr)
        print(f"[qa-trace] report: {report_path}", file=sys.stderr)
        return 1
    gaps = report["coverage_gaps"]
    summary = report["summary"]
    gap_total = sum(len(vals) for vals in gaps.values())
    print(
        "[qa-trace] PASSED "
        f"(requirements={summary['requirements_total']}, architecture={summary['architecture_total']}, "
        f"design={summary['design_total']}, tests={summary['tests_total']}, coverage_gaps={gap_total})"
    )
    print(f"[qa-trace] report: {report_path}")
    gate = report.get("gap_gate", {})
    if gate.get("mode") == "pr":
        print(f"[qa-trace] gap gate vs merge-base of {gate['base']}: new {len(gate['new_gaps'])} "
              f"(accepted {len(gate['accepted'])}), closed {len(gate['closed_gaps'])}")
    for problem in gate.get("accepted_gap_problems", []):
        print(f"[qa-trace] warning: {problem}")
    if gap_total:
        print("[qa-trace] coverage gaps:")
        for key, vals in gaps.items():
            if vals:
                print(f"  - {key}: {len(vals)}")
    return 0


def main() -> int:
    args = parse_args()
    now = _now(args)
    try:
        report = compute(args, now)
        gate_failures = gap_gate(report, args, now)
    except (ValueError, OSError, yaml.YAMLError, subprocess.CalledProcessError) as exc:
        print(f"[qa-trace] FAILED: {exc}", file=sys.stderr)
        return 2
    report_path = _write(args.report_json, report)
    _write(args.design_report_json, {"design": [{"id": d, **v} for d, v in report["design"].items()]})
    return _print_result(report, gate_failures, report_path)


if __name__ == "__main__":
    raise SystemExit(main())
