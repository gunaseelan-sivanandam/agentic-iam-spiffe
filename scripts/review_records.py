"""Review records as the launcher writes them (agentic-sdlc-poc slice 4.3, S43-D1 and S43-D6).

A review record (`docs/slices/<id>/<record>.md`) holds, for each attempt, a section the launcher writes:

    ### Attempt <attempt id>

    Reviewer `<label>`: model, effort, mode, commit.

    Status: <started, then the attempt's end status>.

    #### Prompt       the task prompt, verbatim, in a fenced block
    #### Evidence     the computed evidence, verbatim
    #### Report       the released report, verbatim (only for a completed attempt)

The author writes only `#### Answers to <attempt id>` after it. Each fence is one backtick longer than the longest
backtick run inside its text, so a block's text is the lines between its fences plus a final newline, and hashes to
what the attempt log holds. This module parses records (for the launcher's recheck inputs and for
`scripts/check_review_records.py`) and edits them; the launcher calls the edits under the attempt log's lock.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ATTEMPT_HEADING = re.compile(r"^### Attempt (\S+)\s*$")
ATTEMPT_ID = re.compile(r"^[A-Za-z0-9_-]+/c\d+/r\d+/[A-Za-z0-9_-]+/\d+$")  # the launcher's attempt IDs
BLOCK_LABEL = re.compile(r"^#### (Prompt|Evidence|Report)\s*$")
HEADING = re.compile(r"^#{1,4} ")
# One fence rule for every reader of a record (CommonMark): up to three spaces of indent, three or more backticks
# or tildes, then any info string; a backtick fence's info string holds no backtick.
OPEN_FENCE = re.compile(r"^ {0,3}(`{3,}(?=[^`]*$)|~{3,})")
STATUS = "Status: "
STARTED = f"{STATUS}started."


def fenced(text: str, info: str = "") -> str:
    """A fenced block one backtick longer than the longest backtick run inside the text. Only one final newline is
    dropped, so the block's lines plus one newline give the text back exactly, blank last lines included."""
    fence = "`" * max([3, *(len(run) + 1 for run in re.findall(r"`+", text))])
    body = text[:-1] if text.endswith("\n") else text
    return f"{fence}{info}\n{body}\n{fence}"


def lines_of(text: str) -> list[str]:
    """A record's lines, split on newlines only, so that no other character ends a line (as `str.splitlines` would
    with a form feed or a carriage return) and a block's text survives a round trip unchanged."""
    return text.split("\n")


def closes(line: str, opener: str) -> bool:
    """Whether a line closes a fence opened by `opener`: the same character, at least as long, nothing else."""
    run = line.strip()
    return bool(run) and set(run) == {opener[0]} and len(run) >= len(opener) and len(line) - len(line.lstrip()) <= 3


def _fence_end(lines: list[str], index: int) -> int:
    """For a line that opens a fence, the index of its closing line (or the last line); otherwise the index itself."""
    opener = OPEN_FENCE.match(lines[index])
    if not opener:
        return index
    for close in range(index + 1, len(lines)):
        if closes(lines[close], opener.group(1)):
            return close
    return len(lines) - 1


def next_fence(line: str, fence: str) -> str:
    """The open fence after reading a line, for readers that go line by line (the launcher's answers section)."""
    if fence:
        return "" if closes(line, fence) else fence
    opener = OPEN_FENCE.match(line)
    return opener.group(1) if opener else ""


@dataclass
class AttemptSection:
    """One `### Attempt` section: its blocks by label, how often each label occurs, its status line, and where it
    starts and ends (line indexes; `end` is the first line after it)."""

    start: int
    end: int = 0
    blocks: dict[str, str] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    status: int | None = None


def _block_after(lines: list[str], index: int) -> tuple[str | None, int]:
    """The fenced block at the first non-blank line from `index`, and the index after it."""
    while index < len(lines) and not lines[index].strip():
        index += 1
    opener = OPEN_FENCE.match(lines[index]) if index < len(lines) else None
    if opener is None:
        return None, index
    close = _fence_end(lines, index)
    if close == index or not closes(lines[close], opener.group(1)):
        return None, len(lines)
    return "\n".join(lines[index + 1:close]) + "\n", close + 1


def parse_record(text: str) -> tuple[dict[str, AttemptSection], list[str]]:
    """The attempt sections of a record by attempt ID, and problems of its form (a heading twice, a label without a
    fenced block). A fence outside a labelled block, for example in an answers section, is skipped as a whole."""
    lines = lines_of(text)
    sections: dict[str, AttemptSection] = {}
    problems: list[str] = []
    current: AttemptSection | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        heading, label = ATTEMPT_HEADING.match(line), BLOCK_LABEL.match(line)
        if HEADING.match(line) and not label and current is not None:
            current.end = index
            current = None
        if heading:
            if heading.group(1) in sections:
                problems.append(f"attempt {heading.group(1)} has more than one heading")
            current = sections.setdefault(heading.group(1), AttemptSection(index))
        elif label and current is not None:
            name = label.group(1).lower()
            current.counts[name] = current.counts.get(name, 0) + 1
            block, index = _block_after(lines, index + 1)
            if block is None:
                problems.append(f"line {index + 1}: the {label.group(1)} label has no fenced block after it")
            else:
                current.blocks.setdefault(name, block)
            continue
        elif current is not None and current.status is None and line.startswith(STATUS):
            current.status = index
        index = _fence_end(lines, index) + 1
    if current is not None:
        current.end = len(lines)
    return sections, problems


def report_block(text: str | None, attempt: str) -> str | None:
    """S43-D6: the Report block of an attempt, the committed home of its report."""
    sections, _problems = parse_record(text or "")
    section = sections.get(attempt)
    return section.blocks.get("report") if section else None


def new_record(record: str, unit: str) -> str:
    """The head of a record the launcher creates: a title and a paragraph that says what the document is for."""
    return (f"# Review record — {Path(record).parent.name}, unit `{unit}`\n\n"
            f"The record of the review unit `{unit}`: the launcher writes each attempt's task prompt, evidence and "
            "report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. "
            "`make docs-check` checks it against the attempt log, `review_attempts.jsonl`.\n")


def round_heading(start: dict[str, Any]) -> str:
    count = f" (count {start['count']})" if start.get("count", 1) > 1 else ""
    return f"## Round {start['round']}{count}"


def start_text(start: dict[str, Any], task: str, evidence: str, record_text: str) -> str:
    """The section an attempt begins with: its heading, what ran, a started status, and its Prompt and Evidence."""
    heading = round_heading(start)
    lines = [] if heading in lines_of(record_text) else [heading, ""]
    lines += [f"### Attempt {start['attempt']}", "",
              f"Reviewer `{start['reviewer']}`: `{start['model']}`, effort {start['effort']}, mode {start['mode']}, "
              f"commit `{start['commit'][:12]}`, base `{start['base_commit'][:12]}`.", "",
              STARTED, "", "#### Prompt", "", fenced(task, "markdown"), "",
              "#### Evidence", "", fenced(evidence, "text"), ""]
    return "\n".join(lines) + "\n"


def status_text(end: dict[str, Any]) -> str:
    """An attempt's status line, from its end entry."""
    line = f"{STATUS}{end['status']}"
    if end.get("verdict"):
        line += f"; approvable within the threat model: {end['verdict']}"
    if end.get("reason"):
        line += f" ({end['reason']})"
    return line + "."


def finish(text: str, attempt: str, status: str, report: str | None) -> str:
    """The record with the attempt's status line replaced and, for a released report, a Report block added at the
    end of the attempt's own section, so parallel attempts never interleave. A section already holding a Report block
    keeps it."""
    lines = lines_of(text)
    section = parse_record(text)[0].get(attempt)
    if section is None:
        raise ValueError(f"the record has no section for attempt {attempt}")
    if section.status is not None:
        lines[section.status] = status
    if report is not None and "report" not in section.blocks:
        end = section.end
        while end > section.start and not lines[end - 1].strip():
            end -= 1
        lines[end:end] = ["", "#### Report", "", *fenced(report, "json").splitlines()]
    return "\n".join(lines)


def _launcher_wrote(attempt: str, section: AttemptSection, lines: list[str]) -> bool:
    """Whether a section is exactly what the launcher writes before its start entry: an attempt ID of its form, the
    started status, its Prompt and Evidence blocks, and nothing after them but blank lines up to the end of the file."""
    if not ATTEMPT_ID.match(attempt) or section.status is None or lines[section.status] != STARTED:
        return False
    if set(section.blocks) != {"prompt", "evidence"} or section.end != len(lines):
        return False
    evidence_label = max(i for i in range(section.start, section.end) if lines[i] == "#### Evidence")
    return not any(line.strip() for line in lines[_fence_end(lines, _first_fence(lines, evidence_label)) + 1:])


def _first_fence(lines: list[str], index: int) -> int:
    while index < len(lines) and not OPEN_FENCE.match(lines[index]):
        index += 1
    return index


def truncate_unlogged_tail(text: str, logged: set[str]) -> str:
    """Remove a trailing attempt section the attempt log does not hold: what a launcher killed between writing the
    section and logging its start leaves. Only a section exactly as the launcher writes it is removed, so an author's
    text is never cut; any other unlogged heading is left for the record check to report."""
    sections = parse_record(text)[0]
    tail = max(sections.items(), key=lambda item: item[1].start, default=None)
    lines = lines_of(text)
    if tail is None or tail[0] in logged or not _launcher_wrote(tail[0], tail[1], lines):
        return text
    kept_lines = lines[:tail[1].start]
    while kept_lines and not kept_lines[-1].strip():
        kept_lines.pop()
    if kept_lines and kept_lines[-1].startswith("## Round "):
        kept_lines.pop()  # the round heading the launcher wrote with this, its round's first section
    kept = "\n".join(kept_lines).rstrip("\n") + "\n"
    return kept


def write_atomically(path: Path, text: str) -> None:
    """Replace the file with the text in one rename, so a reader never sees half of it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(text.encode("utf-8"))  # exact bytes: no newline translation on any platform
    with open(temporary, "rb") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)
