"""Tooling tests for slice 4.4's stage checklists (test plan of poc-4-4-stage-checklists): the lists in
`docs/review_checklists/` have the agreed form and cite researched sources, the research record names every source the
plan lists and drafts the three mandates, and the launcher's `--stage` gives a review its list from the base commit.

The form tests read this repository's own files; each has negative cases on planted text. The `--stage` tests use the
launcher's throwaway repository and fake `claude`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.tools import test_run_independent_review as base

ROOT = Path(__file__).resolve().parents[2]
LISTS = ROOT / "docs" / "review_checklists"
RESEARCH = ROOT / "docs" / "slices" / "poc-4-4-stage-checklists" / "research.md"
TYPES = {"plan-and-test-plan", "requirements", "architecture-and-interfaces", "unit-tests", "e2e-tests", "code"}
QUESTION = re.compile(r"^(\d+)\. (.+)$")
TAG = re.compile(r"\[S:([\w-]+)\]")
SOURCE = re.compile(r"^### Source `([\w-]+)` — (.+)$")
# S44-D1 and S44-D13: every source the plan names, by the key its section carries in research.md. The plan's
# "studies of LLM code review" are `cihan-acr` and `swr-bench`; "studies of LLMs as judges" are `zheng-judge` and
# `sharma-sycophancy` (4.4 review, F1: the set had left the code-review studies out).
PLANNED_SOURCES = {"iso29148", "incose", "atam", "stride", "owasp-threat", "istqb", "test-smells", "google-looking-for",
                   "google-standard", "owasp-code-review", "asvs", "cert", "ieee1028", "owasp-llm", "ieee1044",
                   "conventional-comments", "zheng-judge", "sharma-sycophancy", "anthropic-prompting", "cihan-acr",
                   "swr-bench"}
PAID = {"iso29148", "ieee1028", "ieee1044"}
PROOF_QUESTION = "have a test or check that proves it"
CI_QUESTION = "run as its own required CI job, named after it"
fx = base.fx
launcher = base.launcher


def research_keys(text: str) -> dict[str, str]:
    """Each source section of the research record, by its key: the section's text up to the next heading."""
    sections, current = {}, None
    for line in text.splitlines():
        match = SOURCE.match(line)
        if match:
            current = match.group(1)
            sections[current] = ""
        elif line.startswith("#"):
            current = None
        elif current:
            sections[current] += line + "\n"
    return sections


# A source that gave nothing: unread, unreachable, or a paid standard cited by title only (S44-D1, S44-D2).
GAVE_NOTHING = ("No item is taken from it", "title only")
LIST_FILES = {"P": "plan-and-test-plan", "R": "requirements", "A": "architecture-and-interfaces", "U": "unit-tests",
              "E": "e2e-tests", "C": "code"}
QUESTION_ID = re.compile(r"\b([PRAUEC])(\d{1,2})\b")


def usable_keys(text: str) -> set[str]:
    """The source keys a question may cite: sections of the research record that gave something."""
    return {key for key, body in research_keys(text).items()
            if not any(mark in " ".join(body.split()) for mark in GAVE_NOTHING)}


def list_problems(text: str, keys: set[str]) -> list[str]:
    """Why a list does not have the agreed form (S44-D3, S44-D4, S44-D9)."""
    lines = text.splitlines()
    problems = []
    if not lines or not lines[0].startswith("# ") or len(lines) < 3 or not lines[2].strip():
        problems.append("no title and purpose paragraph")
    section = text.split("## Questions\n", 1)[-1].split("\n## ", 1)[0].splitlines()
    problems += [f"not a numbered question: {line[:40]}" for line in section if line.strip() and not QUESTION.match(line)]
    questions = [m.group(2) for line in lines if (m := QUESTION.match(line))]
    if len(questions) > 12:
        problems.append(f"{len(questions)} questions")
    for question in questions:
        tags = TAG.findall(question)
        if not tags:
            problems.append(f"untagged: {question[:40]}")
        problems += [f"unknown source {t}" for t in tags if t not in keys]
        problems += [f"a DPL entry as a source: {t}" for t in tags if t.upper().startswith("DPL")]
    if "## Blocks at this stage" not in text:
        problems.append("no Blocks at this stage section")
    return problems


def draft(text: str, title: str) -> list[str]:
    """The numbered sentences, with their tags, of one draft mandate in the research record."""
    body = text.split(f"#### Draft {title} mandate\n", 1)[1].split("\n####", 1)[0]
    return [QUESTION.match(line).group(2) for line in body.splitlines() if QUESTION.match(line)]  # type: ignore[union-attr]


# --- The lists' form and sources -----------------------------------------------------------------


def test_every_list_has_the_agreed_form_and_cites_researched_sources() -> None:
    keys = usable_keys(RESEARCH.read_text())
    for path in sorted(LISTS.glob("*.md")):
        assert list_problems(path.read_text(), keys) == [], path.name


@pytest.mark.parametrize(("edit", "problem"), [
    (lambda t: t + "".join(f"\n{n}. Another question? [S:google-standard]" for n in range(20, 33)), "questions"),
    (lambda t: t.replace(" [S:google-looking-for]", "", 1), "untagged"),
    (lambda t: t.replace("[S:google-looking-for]", "[S:nowhere]", 1), "unknown source"),
    (lambda t: t.replace("[S:google-looking-for]", "[S:DPL-010]", 1), "a DPL entry"),
    (lambda t: t.replace("## Blocks at this stage", "## Something else"), "no Blocks"),
    (lambda t: t.replace("[S:google-looking-for]", "[S:cert]", 1), "unknown source cert"),
    (lambda t: t.replace("[S:google-looking-for]", "[S:iso29148]", 1), "unknown source iso29148"),
    (lambda t: t.replace("\n1. ", "\n- ", 1), "not a numbered question"),
], ids=["thirteen-questions", "untagged-question", "unknown-key", "dpl-as-source", "no-blocks-section",
        "source-that-gave-nothing", "title-only-standard", "bulleted-question"])
def test_the_form_check_fails_on_each_kind_of_violation(edit: object, problem: str) -> None:
    keys = usable_keys(RESEARCH.read_text()) | {"DPL-010"}
    text = edit((LISTS / "code.md").read_text())  # type: ignore[operator]
    assert any(problem in p for p in list_problems(text, keys))


def test_exactly_the_six_artifact_types_have_a_list() -> None:
    assert {p.stem for p in LISTS.glob("*.md")} == TYPES
    assert not (LISTS / "final-review.md").exists() and not (LISTS / "handoff.md").exists()


def test_the_two_questions_for_what_is_missing_sit_where_the_misses_happen() -> None:
    texts = {p.stem: p.read_text() for p in LISTS.glob("*.md")}
    assert {t for t, text in texts.items() if PROOF_QUESTION in text} == {"plan-and-test-plan", "requirements",
                                                                         "unit-tests", "e2e-tests"}
    assert {t for t, text in texts.items() if CI_QUESTION in text} == {"plan-and-test-plan", "code"}


def test_the_plan_lists_question_8_asks_the_fix_rule_since_r2_4() -> None:
    """R3-4 (the owner, 2026-11-17): growth proposal 14 rewords question 8 to the rule since R2-4 (a fix adds no
    mechanism at all); the list keeps its 12 questions."""
    text = (LISTS / "plan-and-test-plan.md").read_text()
    questions = dict(m.groups() for line in text.splitlines() if (m := QUESTION.match(line)))
    assert len(questions) == 12
    assert questions["8"] == ("Where a fix answers a review finding, does it correct the defect or change the choice "
                              "that caused it, without adding a mechanism? [S:google-looking-for]")


def test_a_false_small_slice_claim_blocks_at_the_plan_review() -> None:
    """R3-4, decision 7, option (a): a Blocks bullet rather than a 13th question, so the question limit holds."""
    text = (LISTS / "plan-and-test-plan.md").read_text()
    blocks = text.split("## Blocks at this stage", 1)[1]
    assert ("\n- a plan that claims a small slice while one of the four conditions of `AGENTS.md` (Small slices) does "
            "not hold for the planned change") in blocks


def test_the_code_list_repeats_no_coding_rule() -> None:
    code = (LISTS / "code.md").read_text().lower()
    for rule in ("eval(", "except exception", "pkcs#8", "hardcoded secret", "validate and reject"):
        assert rule not in code


# --- The research record -------------------------------------------------------------------------


def test_the_research_record_has_a_section_for_every_planned_source() -> None:
    sections = research_keys(RESEARCH.read_text())
    assert PLANNED_SOURCES <= set(sections)
    for key in PAID:
        assert "title only" in sections[key]


def test_a_planned_source_without_a_section_fails() -> None:
    text = RESEARCH.read_text().replace("### Source `atam`", "### Not a source `atam`")
    assert "atam" not in research_keys(text)


def test_every_dpl_entry_is_mapped() -> None:
    text = RESEARCH.read_text()
    mapping = text.split("## The delivery problem log as a test of the lists", 1)[1].split("\n## ", 1)[0]
    for n in range(1, 12):
        assert f"| DPL-{n:03d} " in mapping


def named_question_problems(research: str, lists: dict[str, str]) -> list[str]:
    """Question IDs that the candidate table or the DPL mapping names and no list has (4.4 critique, CR-B4)."""
    counts = {letter: sum(1 for line in lists[name].splitlines() if QUESTION.match(line))
              for letter, name in LIST_FILES.items()}
    problems = []
    for heading, column in (("## Candidate items and where they went", 3), ("## The delivery problem log as a test", 3)):
        table = research.split(heading, 1)[1].split("\n## ", 1)[0]
        for row in (line.split(" | ") for line in table.splitlines() if line.startswith("| ") and "---" not in line):
            cell = row[column - 1] if len(row) >= column else ""
            problems += [f"{m.group(0)} in {row[0][2:30]}" for m in QUESTION_ID.finditer(cell)
                         if int(m.group(2)) > counts[m.group(1)]]
    return problems


def test_every_question_the_research_record_names_exists() -> None:
    lists = {name: (LISTS / f"{name}.md").read_text() for name in LIST_FILES.values()}
    assert named_question_problems(RESEARCH.read_text(), lists) == []


def test_a_mapping_that_names_a_question_no_list_has_fails() -> None:
    lists = {name: (LISTS / f"{name}.md").read_text() for name in LIST_FILES.values()}
    text = RESEARCH.read_text().replace("| A2; C11 (the claim", "| A2; C19 (the claim", 1)
    assert any(p.startswith("C19") for p in named_question_problems(text, lists))


@pytest.mark.parametrize("title", ["initial", "recheck", "final"])
def test_each_draft_mandate_sentence_has_a_source_and_names_its_failure_mode(title: str) -> None:
    keys = usable_keys(RESEARCH.read_text())
    sentences = draft(RESEARCH.read_text(), title)
    assert len(sentences) >= 3
    for sentence in sentences:
        assert TAG.findall(sentence) and set(TAG.findall(sentence)) <= keys and "— counters: " in sentence


def test_a_draft_sentence_without_a_tag_fails_the_check() -> None:
    text = RESEARCH.read_text().replace(" [S:owasp-llm] — counters: indirect", " — counters: indirect", 1)
    assert not all(TAG.findall(s) for s in draft(text, "initial"))


@pytest.mark.parametrize("title", ["initial", "recheck"])
def test_the_benchmarks_draft_mandates_are_the_research_drafts(title: str) -> None:
    from tests.tools import test_run_review_benchmark as benchmark_tests
    bench = benchmark_tests.bench
    text = bench.mandate_text((ROOT / f"tests/review_benchmark/prompts/mandate_{title}_b.md").read_text())
    expected = " ".join(s.split(" [S:")[0] for s in draft(RESEARCH.read_text(), title)) + "\n"
    assert text == expected


# --- --stage (S44-D7) ---------------------------------------------------------------------------


def _lists_at_base(fx: base.Fixture, **lists: str) -> None:
    """Commit stage lists and push them as the base, then make a change on top that edits one of them."""
    for name, text in lists.items():
        base._write(fx.work, f"docs/review_checklists/{name}.md", text)
    base._commit_all(fx.work, "lists at the base")
    base._git(fx.work, "push", "-q", "-f", "origin", "HEAD:poc/base")
    base._write(fx.work, base.REVIEWED, "print('after the lists')\n")
    base._write(fx.work, "docs/review_checklists/requirements.md", "# Requirements\n\nREWRITTEN BY THE CHANGE\n")
    fx.commit = base._commit_all(fx.work, "a change that rewrites a list")


def test_a_stage_gets_the_base_commits_list_even_when_the_change_rewrites_it(fx: base.Fixture) -> None:
    _lists_at_base(fx, requirements="# Requirements\n\nBASE REQUIREMENTS QUESTION\n", code="# Code\n\nBASE CODE QUESTION\n")
    assert base._run(fx, "--stage", "requirements", "--stage", "code") == 0
    checklist = base._section(base._prompt(fx), "Stage checklist")
    assert "BASE REQUIREMENTS QUESTION" in checklist and "BASE CODE QUESTION" in checklist
    assert "REWRITTEN BY THE CHANGE" not in checklist
    start = fx.log()[0]
    assert set(start["stages"]) == {"requirements", "code"}
    assert start["stages"]["code"] == launcher.sha256_text("# Code\n\nBASE CODE QUESTION\n")


@pytest.mark.parametrize(("args", "unit"), [(("--stage", "nonsense"), "unit1"), ((), "unit1"),
                                            (("--stage", "code"), "final")],
                         ids=["unknown-name", "no-stage-when-the-base-has-lists", "final-with-a-stage"])
def test_a_stage_the_base_cannot_give_is_refused_before_any_call(fx: base.Fixture, args: tuple[str, ...], unit: str) -> None:
    _lists_at_base(fx, code="# Code\n\nBASE CODE QUESTION\n")
    record = "docs/slices/demo/review_final.md" if unit == "final" else base.RECORD
    assert base._run(fx, *args, unit=unit, record=record) == 2
    assert fx.calls() == []


def test_a_stage_on_a_base_without_lists_is_refused_before_any_call(fx: base.Fixture) -> None:
    assert base._run(fx, "--stage", "code") == 2
    assert fx.calls() == []


def test_a_final_review_without_a_stage_runs_with_no_list(fx: base.Fixture) -> None:
    _lists_at_base(fx, code="# Code\n\nBASE CODE QUESTION\n")
    assert base._run(fx, unit="final", record="docs/slices/demo/review_final.md") == 0
    assert "## Stage checklist" not in base._prompt(fx) and "BASE CODE QUESTION" not in base._prompt(fx)


def test_a_base_without_lists_says_so_in_the_prompt_and_the_start_entry(fx: base.Fixture) -> None:
    assert base._run(fx) == 0
    assert "No checklist at base " in base._section(base._prompt(fx), "Stage checklist")
    start = fx.log()[0]
    assert start["stages"] == {} and start["checklist_sha256"] == launcher.sha256_text(
        f"No checklist at base {start['base_commit'][:12]}: the base branch has no `docs/review_checklists/`.")
