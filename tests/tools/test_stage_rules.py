"""Tooling tests for slice 4.6's stage rules (test plan of poc-4-6-stage-rules): `AGENTS.md`'s table of the seven
stages, the slice templates that carry it into every new slice, the grill-me skill kept in the repository, and no live
document left pointing at the old step numbers. The owner's decisions of 2026-11-13 (slice 4's decision page, decision
concerns 7 and 10) add the plan template's small-slice part and the decision-page template.

Each check reads this repository's own files and has negative cases on planted text.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
STAGES = ["Discovery", "Requirements", "Architecture and interfaces", "Tests first", "Implementation", "Final review",
          "Handoff"]
LISTS = sorted(p.stem for p in (ROOT / "docs" / "review_checklists").glob("*.md"))
HEADER = "| Stage | Produces | Review | Checks | Exit |"
# The plan's probe (environment facts of 4.6), and the README's old name for the workflow (the dry slice found it).
STEP_REFERENCE = re.compile(r"\bstep [1-4]\b|\bfour-phase\b", re.IGNORECASE)
# The implementation-review questions AGENTS.md requires of the test-plan template (Independent review).
REVIEW_QUESTIONS = ("which wrong failure would still pass it", "a key, socket or secret reachable by a service outside",
                    "start with a comment that says what the file is for")
TEMPLATES = ROOT / "docs" / "slices" / "_template"
SKILL = ROOT / ".claude" / "skills" / "grill-me" / "SKILL.md"
# S46-D1: the lists each stage's review takes; the final review takes none, and handoff is the user's approval.
STAGE_LISTS = {"Discovery": ["plan-and-test-plan"], "Requirements": ["requirements"],
               "Architecture and interfaces": ["architecture-and-interfaces"], "Tests first": ["unit-tests", "e2e-tests"],
               "Implementation": ["code"], "Final review": [], "Handoff": []}
DISCOVERY_EXIT = ("| the plan review has ended, and the user merges the plan PR; a small slice's plan stays in its one "
                  "PR |")
# Decision concern 10 of slice 4 (owner, 2026-11-13): the sections of every slice's decision page.
DECISION_PAGE_SECTIONS = ("Goal", "What the slice builds", "Decisions made", "Decisions to make", "Decision concerns",
                          "Discovered issues", "Implementation review: the test-plan questions", "Review outcome",
                          "How the user can check the work")


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


lint = _load("lint_changed_files")
docs = _load("check_docs")


def _table(text: str, header: str) -> list[list[str]]:
    """The rows of the Markdown table that starts with `header`, as stripped cells."""
    lines = text.split("\n")
    rows = []
    for line in lines[lines.index(header) + 2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


# --- The stage table (S46-D1) ---------------------------------------------------------------------


def stage_table_problems(agents: str) -> list[str]:
    """Why `AGENTS.md`'s stage table does not state S46-D1: the seven stages in order, no empty cell, and every
    review naming an existing list, the final mode or the user's approval."""
    if HEADER not in agents.split("\n"):
        return ["no stage table"]
    rows = _table(agents, HEADER)
    problems = [] if [r[0] for r in rows] == STAGES else [f"stages are {[r[0] for r in rows]}"]
    for row in rows:
        problems += [f"{row[0]}: an empty cell" for cell in row if not cell]
        named = re.findall(r"`([a-z0-9-]+)`", row[2])
        problems += [f"{row[0]}: no list {name}" for name in named if name not in LISTS]
        if row[0] in STAGE_LISTS and sorted(named) != sorted(STAGE_LISTS[row[0]]):
            problems.append(f"{row[0]}: its review takes {named}, not S46-D1's {STAGE_LISTS[row[0]]}")
        if not named and "final mode" not in row[2] and "approval" not in row[2]:
            problems.append(f"{row[0]}: its review names no list, final mode or approval")
    return problems


def test_agents_md_states_the_seven_stages_with_every_cell_filled() -> None:
    assert stage_table_problems((ROOT / "AGENTS.md").read_text()) == []


@pytest.mark.parametrize(("edit", "problem"), [
    (lambda t: re.sub(r"\n\| Requirements \|[^\n]*", "", t, count=1), "stages are"),
    (lambda t: t.replace(DISCOVERY_EXIT, "|  |", 1), "an empty cell"),
    (lambda t: t.replace("list `code`", "list `kode`", 1), "no list kode"),
    (lambda t: t.replace("final review, 4.1's final mode, no list", "the final review", 1), "names no list"),
    (lambda t: t.replace(HEADER, "| Stage | Output | Review | Checks | Exit |", 1), "no stage table"),
    (lambda t: t.replace("list `requirements`", "list `code`", 1), "not S46-D1's"),
], ids=["stage-missing", "empty-cell", "unknown-list", "review-without-list-or-mode", "no-table", "lists-swapped"])
def test_the_stage_table_check_fails_on_each_kind_of_violation(edit: Any, problem: str) -> None:
    text = edit((ROOT / "AGENTS.md").read_text())
    assert any(problem in p for p in stage_table_problems(text)), stage_table_problems(text)


# --- The templates (S46-D11) ----------------------------------------------------------------------


def plan_template_problems(text: str) -> list[str]:
    """Why the plan template does not carry the stage table, the decision-source column, the deviations section and
    the small-slice part that names `AGENTS.md`'s conditions (decision concern 7 of slice 4)."""
    problems = [f"no stage {stage}" for stage in STAGES if f"\n| {stage} |" not in text]
    if "| ID | Decision | Source |" not in text:
        problems.append("no Source column in the decisions table")
    if "\n## Rule deviations\n" not in text:
        problems.append("no Rule deviations section")
    if "\n## Small slice\n" not in text or "AGENTS.md#small-slices" not in text:
        problems.append("no Small slice section naming AGENTS.md's conditions")
    return problems


def decision_page_problems(text: str) -> list[str]:
    """Why the decision-page template lacks a section the owner's resolution of decision concern 10 lists."""
    return [f"no section {name}" for name in DECISION_PAGE_SECTIONS if f"\n## {name}\n" not in text]


def review_plan_problems(text: str) -> list[str]:
    """Why the test-plan template does not name each stage's list and the implementation-review questions."""
    problems = [f"no list {name}" for name in LISTS if f"`{name}`" not in text]
    return problems + [f"no review question '{q}'" for q in REVIEW_QUESTIONS if q not in text]


def test_the_plan_template_carries_the_stages_the_source_column_and_rule_deviations() -> None:
    assert plan_template_problems((TEMPLATES / "plan.md").read_text()) == []


@pytest.mark.parametrize(("old", "new", "problem"), [
    ("\n| Tests first |", "\n| Tests |", "no stage Tests first"),
    ("| ID | Decision | Source |", "| ID | Decision |", "no Source column"),
    ("\n## Rule deviations\n", "\n## Deviations\n", "no Rule deviations"),
    ("\n## Small slice\n", "\n## Size\n", "no Small slice section"),
    ("AGENTS.md#small-slices", "AGENTS.md#slice-workflow", "no Small slice section"),
], ids=["stage-missing", "no-source-column", "no-deviations-section", "no-small-slice-section",
        "small-slice-without-conditions"])
def test_the_plan_template_check_fails_on_each_missing_part(old: str, new: str, problem: str) -> None:
    text = (TEMPLATES / "plan.md").read_text().replace(old, new)
    assert any(problem in p for p in plan_template_problems(text))


def test_the_test_plan_template_names_each_stage_list_and_the_required_review_questions() -> None:
    assert review_plan_problems((TEMPLATES / "test_plan.md").read_text()) == []


@pytest.mark.parametrize(("old", "new", "problem"), [
    ("`architecture-and-interfaces`", "`architecture`", "no list architecture-and-interfaces"),
    (REVIEW_QUESTIONS[0], "which failure", "no review question"),
    (REVIEW_QUESTIONS[1], "a secret reachable", "no review question"),
    (REVIEW_QUESTIONS[2], "say what it is", "no review question"),
], ids=["list-missing", "tests-question-missing", "keys-question-missing", "names-question-missing"])
def test_the_test_plan_template_check_fails_on_each_missing_part(old: str, new: str, problem: str) -> None:
    text = (TEMPLATES / "test_plan.md").read_text().replace(old, new)
    assert any(problem in p for p in review_plan_problems(text))


def test_the_decision_page_template_has_every_section_the_owner_asked_for() -> None:
    assert decision_page_problems((TEMPLATES / "decisions.md").read_text()) == []


@pytest.mark.parametrize("section", ["Discovered issues", "Review outcome"])
def test_the_decision_page_check_fails_on_a_missing_section(section: str) -> None:
    text = (TEMPLATES / "decisions.md").read_text().replace(f"\n## {section}\n", "\n## Notes\n")
    assert decision_page_problems(text) == [f"no section {section}"]


def test_a_bundle_made_from_the_templates_passes_the_header_and_link_checks() -> None:
    """The templates, copied into a bundle `docs/slices/sample/` with their placeholder filled, pass the lint gate's
    header check and resolve every relative link from there."""
    bundle = ROOT / "docs" / "slices" / "sample"
    for name in ("plan.md", "test_plan.md", "decisions.md"):
        text = (TEMPLATES / name).read_text().replace("<slice-id>", "sample")
        assert lint.header_problem(f"docs/slices/sample/{name}", text) is None
        links = [t for t in docs.LINK_RE.findall(text) if not re.match(r"^[a-z][a-z0-9+.-]*:", t)]
        assert [docs._link_problem(bundle / name, text, t) for t in links] == [None] * len(links)


# --- The grill-me skill in the repository (S46-D14) -------------------------------------------------


def test_the_grill_me_skill_keeps_its_front_matter_then_has_a_title_and_paragraph() -> None:
    text = SKILL.read_text()
    front, _sep, _rest = text.partition("\n---\n")
    assert front.startswith("---\nname: grill-me\ndescription: ")
    assert lint.header_problem(".claude/skills/grill-me/SKILL.md", text) is None
    assert "keys, sockets and secrets" in text
    assert ".claude/skills/grill-me/SKILL.md" in (ROOT / "AGENTS.md").read_text()


def test_a_skill_whose_front_matter_is_followed_by_no_title_fails_the_header_check() -> None:
    text = SKILL.read_text()
    without_title = re.sub(r"\n# [^\n]*\n", "\n", text, count=1)
    assert lint.header_problem(".claude/skills/grill-me/SKILL.md", without_title) is not None


# --- The old step numbers (S46-D12) ---------------------------------------------------------------


def step_references(paths: list[Path]) -> list[str]:
    """Each live document line that still points at a step of the old four-step workflow."""
    return [f"{p.relative_to(ROOT) if p.is_relative_to(ROOT) else p.name}:{n}: {line.strip()[:60]}" for p in paths
            for n, line in enumerate(p.read_text().split("\n"), 1) if STEP_REFERENCE.search(line)]


# The problem logs record what happened, quoting old wording where a miss was about it (DPL-012); they state no rule.
LOGS = {ROOT / "docs" / "delivery_problem_log.md", ROOT / "docs" / "open_problem_log.md"}


def rule_documents() -> list[Path]:
    """The live documents, the stage lists and the skills: every text that states or carries a rule."""
    return sorted({*docs.live_docs(ROOT), *(ROOT / "docs" / "review_checklists").glob("*.md"),
                   *(ROOT / ".claude" / "skills").rglob("*.md")} - LOGS)


def test_no_live_document_refers_to_the_old_step_numbers() -> None:
    assert SKILL in rule_documents() and ROOT / "docs" / "review_checklists" / "code.md" in rule_documents()
    assert step_references(rule_documents()) == []


def test_a_planted_step_reference_fails(tmp_path: Path) -> None:
    planted = tmp_path / "planted-step-reference.md"
    planted.write_text("# Planted\n\nSee step 4 of the slice workflow.\n")
    assert step_references([planted]) == ["planted-step-reference.md:3: See step 4 of the slice workflow."]
    planted.write_text("# Planted\n\nChanges follow a four-phase slice workflow.\n")
    assert len(step_references([planted])) == 1
