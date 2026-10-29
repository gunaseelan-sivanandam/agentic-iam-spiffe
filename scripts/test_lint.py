#!/usr/bin/env python3
"""Flag loose outcome checks in the E2E harness (slice agentic-delivery-process, Increment 1A).

Only outcome guards are linted: premise and exercise guards may use plumbing such as `|| true`.
A guard preceded by `# test-lint: alternate: <reason>` may accept more than one outcome
(rules any-of and broad-regex); no other rule can be exempted.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HARNESS = Path("scripts/rogue_node_tests.sh")
ALTERNATE_RE = re.compile(r"^\s*#\s*test-lint:\s*alternate:(.*)$")
TEST_ID_RE = re.compile(r'begin_test_evidence "([^"]+)"')
GENERIC_FAILURE_RE = re.compile(
    r"(?i)(error|fail|refused|timed out|timeout|no route|denied|unauthori[sz]ed|forbidden|invalid"
    r"|could not resolve|connect|unable|not found|no such file|not known)"
)
SUBSTITUTION_RE = re.compile(r"\\?\$\([^()]*\)")
REGEX_GROUP_RE =re.compile(r"'\(([^']*\|[^']*)\)'")
EXIT_NONZERO_RE = re.compile(r'-ne 0\b|!= \\?"?0\\?"?(?=\s|\])')
NOT_200_RE = re.compile(r'!= \\?"?200|-ne 200\b')
POSITIVE_CHECK_RE = re.compile(r"(?<!! )\b(grep|text_matches|assert_\w+|jq -e)\b")
MULTI_OUTCOME_RULES = {"any-of", "broad-regex"}


@dataclass(frozen=True)
class Finding:
    test_id: str
    line: int
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"{self.test_id} line {self.line}: {self.rule}: {self.detail}"


@dataclass(frozen=True)
class Guard:
    test_id: str
    line: int
    command: str | None
    alternate: str | None


def _logical_lines(text: str) -> list[tuple[int, str]]:
    """Join backslash-continued lines; return (first line number, joined text)."""
    out: list[tuple[int, str]] = []
    buf = ""
    start = 0
    for number, raw in enumerate(text.split("\n"), 1):
        if not buf:
            start = number
        if raw.endswith("\\"):
            buf += raw[:-1] + " "
            continue
        out.append((start, buf + raw))
        buf = ""
    return out


def _double_quoted_words(text: str) -> list[str]:
    """Return the double-quoted shell words of a line, escapes kept verbatim."""
    words: list[str] = []
    i = 0
    while i < len(text):
        if text[i] != '"':
            i += 1
            continue
        j = i + 1
        while j < len(text) and text[j] != '"':
            j += 2 if text[j] == "\\" else 1
        words.append(text[i + 1 : j])
        i = j + 1
    return words


def _strip_substitutions(command: str) -> str:
    """Drop $(...) command substitutions, innermost first, where `|| true` only defaults a value."""
    previous = None
    while previous != command:
        previous = command
        command = SUBSTITUTION_RE.sub("", command)
    return command


def parse_guards(text: str) -> list[Guard]:
    guards: list[Guard] = []
    test_id = "?"
    alternate: str | None = None
    for number, line in _logical_lines(text):
        match = TEST_ID_RE.search(line)
        if match:
            test_id = match.group(1)
        alt = ALTERNATE_RE.match(line)
        if alt:
            alternate = alt.group(1).strip()
            continue
        stripped = line.strip()
        if stripped.startswith("outcome_guard ") or stripped == "outcome_guard":
            words = _double_quoted_words(stripped)
            command = words[1] if len(words) >= 2 else None
            guards.append(Guard(test_id, number, command, alternate))
        if stripped and not stripped.startswith("#"):
            alternate = None
    return guards


def _is_negative_only(command: str) -> bool:
    parts = [part.strip() for part in command.split("&&") if part.strip()]
    return bool(parts) and all(part.startswith("!") for part in parts)


def _broad_regexes(command: str) -> list[str]:
    broad: list[str] = []
    for match in REGEX_GROUP_RE.finditer(command):
        before = command[max(0, match.start() - 40) : match.start()]
        if "! grep" in before or "! text_matches" in before:
            continue
        generic = [alt for alt in match.group(1).split("|") if GENERIC_FAILURE_RE.search(alt)]
        if len(generic) >= 2:
            broad.append(match.group(1))
    return broad


def check_command(command: str) -> list[tuple[str, str]]:
    """Return (rule, detail) for each loose pattern in one outcome guard command."""
    problems: list[tuple[str, str]] = []
    if "|| true" in _strip_substitutions(command):
        problems.append(("or-true", "`|| true` makes the guard pass on failure"))
    if EXIT_NONZERO_RE.search(command) and not POSITIVE_CHECK_RE.search(command):
        problems.append(("exit-code-only", "a non-zero exit alone does not say why it failed"))
    if "assert_file_any" in command:
        problems.append(("any-of", "accepts more than one outcome"))
    for regex in _broad_regexes(command):
        problems.append(("broad-regex", f"accepts several failures: ({regex[:80]})"))
    if NOT_200_RE.search(command):
        problems.append(("not-200", "`!= 200` accepts every other status"))
    return problems


def _guard_findings(guard: Guard) -> list[Finding]:
    if guard.command is None:
        return [Finding(guard.test_id, guard.line, "unparsed", "outcome guard command not found")]
    findings: list[Finding] = []
    if guard.alternate == "":
        findings.append(Finding(guard.test_id, guard.line, "alternate-without-reason", "give a reason"))
    for rule, detail in check_command(guard.command):
        if guard.alternate and rule in MULTI_OUTCOME_RULES:
            continue
        findings.append(Finding(guard.test_id, guard.line, rule, detail))
    return findings


def lint(text: str) -> list[Finding]:
    guards = parse_guards(text)
    findings: list[Finding] = []
    by_test: dict[str, list[Guard]] = {}
    for guard in guards:
        findings.extend(_guard_findings(guard))
        by_test.setdefault(guard.test_id, []).append(guard)
    for test_id, test_guards in by_test.items():
        commands = [guard.command for guard in test_guards]
        if all(command is not None and _is_negative_only(command) for command in commands):
            detail = "only negative checks: a missing or empty file passes"
            findings.append(Finding(test_id, test_guards[0].line, "negative-only", detail))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", type=Path, default=DEFAULT_HARNESS)
    args = parser.parse_args(argv)
    findings = lint(args.harness.read_text(encoding="utf-8"))
    for finding in findings:
        print(f"[test-lint] {finding}")
    if findings:
        print(f"[test-lint] FAILED ({len(findings)} loose outcome checks)", file=sys.stderr)
        return 1
    print("[test-lint] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
