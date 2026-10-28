"""Negative controls for scripts/check_docs.py: every check must fail on a broken input."""

from __future__ import annotations

import importlib.util
import subprocess  # nosec B404 - fixed git argv in fixtures
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_docs.py"
_spec = importlib.util.spec_from_file_location("check_docs", SCRIPT)
assert _spec and _spec.loader
check_docs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_docs)

HARNESS = 'begin_test_evidence "M1-T1" "a"\n  begin_test_evidence "M5-T2" "b"\n'


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)  # nosec B603 B607


def _git_add(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)  # nosec B603 B607


# --- spec -------------------------------------------------------------------


def test_spec_complete_has_no_problems() -> None:
    spec = "### M1-T1 — “a”\n### M5-T2 — “b”\n"
    assert check_docs.check_spec(HARNESS, spec) == []


def test_spec_missing_harness_test_is_reported() -> None:
    problems = check_docs.check_spec(HARNESS, "### M1-T1 — “a”\n")
    assert problems == ["spec: harness test M5-T2 has no heading in the test spec"]


def test_spec_heading_for_unknown_test_is_reported() -> None:
    spec = "### M1-T1 — “a”\n### M5-T2 — “b”\n### M5-T99 — “gone”\n"
    assert check_docs.check_spec(HARNESS, spec) == ["spec: heading M5-T99 names a test the harness does not run"]


def test_spec_duplicate_heading_is_reported() -> None:
    spec = "### M1-T1 — “a”\n### M5-T2 — “b”\n### M5-T2 — “b again”\n"
    assert check_docs.check_spec(HARNESS, spec) == ["spec: duplicate heading for M5-T2"]


def test_spec_bare_heading_does_not_count_as_documented() -> None:
    # The pre-2026-10 style "### T1 — ..." is ambiguous across milestones and must not satisfy the check.
    problems = check_docs.check_spec(HARNESS, "### T1 — “a”\n### T2 — “b”\n")
    assert len(problems) == 2


# --- links ------------------------------------------------------------------


def test_links_valid_file_and_anchor_pass(tmp_path: Path) -> None:
    _write(tmp_path / "AGENTS.md", "# Rules\n\n## Slice workflow\n\n## `make` Quality gates\n")
    doc = _write(tmp_path / "README.md", "[a](AGENTS.md) [b](AGENTS.md#slice-workflow) [c](AGENTS.md#make-quality-gates) [d](https://x.y)\n")
    assert check_docs.check_links(tmp_path, doc) == []


def test_links_missing_file_is_reported(tmp_path: Path) -> None:
    doc = _write(tmp_path / "README.md", "[gone](docs/nope.md)\n")
    assert check_docs.check_links(tmp_path, doc) == ["links: README.md: missing target docs/nope.md"]


def test_links_missing_anchor_is_reported(tmp_path: Path) -> None:
    _write(tmp_path / "AGENTS.md", "## Slice workflow\n")
    doc = _write(tmp_path / "README.md", "[x](AGENTS.md#quality-gates)\n")
    assert check_docs.check_links(tmp_path, doc) == ["links: README.md: missing anchor AGENTS.md#quality-gates"]


def test_links_same_document_anchor_is_checked(tmp_path: Path) -> None:
    doc = _write(tmp_path / "README.md", "## Start here\n[ok](#start-here) [bad](#nowhere)\n")
    assert check_docs.check_links(tmp_path, doc) == ["links: README.md: missing anchor #nowhere"]


def test_repeated_headings_get_numbered_anchors() -> None:
    anchors = check_docs.heading_anchors("## Notes\n## Notes\n")
    assert anchors == {"notes", "notes-1"}


# --- images -----------------------------------------------------------------


def test_images_unreferenced_tracked_render_is_reported(tmp_path: Path) -> None:
    _git_repo(tmp_path)
    _write(tmp_path / "docs" / "used.svg", "<svg/>")
    _write(tmp_path / "docs" / "orphan.png", "png")
    doc = _write(tmp_path / "README.md", "![d](docs/used.svg)\n")
    _git_add(tmp_path)
    assert check_docs.check_images(tmp_path, [doc]) == ["images: docs/orphan.png is not referenced by any live document"]


def test_images_untracked_render_is_ignored(tmp_path: Path) -> None:
    _git_repo(tmp_path)
    doc = _write(tmp_path / "README.md", "no images\n")
    _git_add(tmp_path)
    _write(tmp_path / "docs" / "local_preview.png", "png")
    assert check_docs.check_images(tmp_path, [doc]) == []


def test_images_puml_without_svg_is_reported(tmp_path: Path) -> None:
    _git_repo(tmp_path)
    _write(tmp_path / "docs" / "flow.puml", "@startuml\n@enduml\n")
    doc = _write(tmp_path / "README.md", "x\n")
    _git_add(tmp_path)
    assert check_docs.check_images(tmp_path, [doc]) == ["images: docs/flow.puml has no rendered flow.svg"]


# --- slices -----------------------------------------------------------------


@pytest.mark.parametrize("missing", ["new-slice", "old-slice"])
def test_slice_without_index_row_is_reported(tmp_path: Path, missing: str) -> None:
    slices = tmp_path / "docs" / "slices"
    (slices / "_template").mkdir(parents=True)
    (slices / "new-slice").mkdir()
    (slices / "archive" / "old-slice").mkdir(parents=True)
    rows = {"new-slice": "[new-slice](new-slice/)", "old-slice": "[old-slice](archive/old-slice/)"}
    rows.pop(missing)
    _write(slices / "README.md", "\n".join(rows.values()) + "\n")
    assert check_docs.check_slice_index(tmp_path) == [f"slices: {missing} has no row in docs/slices/README.md"]


# --- TEST_ONLY ids ----------------------------------------------------------


def test_unknown_test_only_id_is_reported(tmp_path: Path) -> None:
    doc = _write(tmp_path / "README.md", "-e TEST_ONLY=M1-T1,M5.S1-T1 rogue-tests\n")
    problems = check_docs.check_test_only_ids(tmp_path, [doc], {"M1-T1", "M5-T2"})
    assert problems == ["ids: README.md: TEST_ONLY example names unknown test M5.S1-T1"]
