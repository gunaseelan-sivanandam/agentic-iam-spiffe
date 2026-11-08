"""Changed-files lint gate (agentic-sdlc-poc slice 3; POC-D7, POC-D8): fails on violations a change adds or worsens.

For every file the change adds, modifies or renames (against the merge-base of the base reference and
HEAD), ruff and shellcheck run on the merge-base version and on the new version. A finding key is the
file, the rule, and the enclosing function's qualified name (`Class.method`), or the line text for
findings outside a function and for shellcheck. A function whose body, without its name, matches a
function at the merge-base keeps that function's key, so a pure rename is not new. The change fails
when a key occurs more often than at the merge-base, or when its value (the number in the message,
such as the complexity) is higher. Every added Python, shell, YAML, TOML, Dockerfile or Rego file
must start with a purpose comment, and every added Markdown file with a title and a paragraph. The ruff configuration is read from the merge-base when it exists
there, so a change cannot loosen the limits it is checked against. A missing base fails the run.

Usage (from the repository root): python3 scripts/lint_changed_files.py --base <ref>   (make lint)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

CONFIG = "ruff_changed_files.toml"
# Rules whose `noqa` is ignored: the limits, naming, and unused imports and variables (POC-D8).
NO_NOQA_RULES = "C901,PLR0912,PLR0913,PLR0915,N,F401,F841"
SHELL_SHEBANG = re.compile(r"^#!\s*(?:/usr/bin/env\s+)?(?:/bin/|/usr/bin/)?(?:ba|da|k|z)?sh\b")
TOOL_DIRECTIVE = re.compile(r"^#\s*(?:shellcheck\b|-\*-|yaml-language-server\b|noqa\b|type:)")
LIMIT_VALUE = re.compile(r"\((\d+) > \d+\)")
HEADER_SUFFIXES = {".py", ".sh", ".yml", ".yaml", ".toml", ".rego"}


class LintError(Exception):
    """The gate cannot run (missing base, unreadable file, missing tool); the run fails."""


@dataclass(frozen=True)
class Change:
    """One changed file: its Git status (A, M, T, R or C), its path, and its path at the merge-base."""

    status: str
    path: str
    old_path: str | None


@dataclass(frozen=True)
class Finding:
    """One ruff or shellcheck finding: its key, the number in its message (if any), its line and message."""

    key: tuple[str, str, str]
    value: int | None
    line: int
    message: str


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)  # noqa: S603, S607 - fixed argv, no shell
    if result.returncode != 0:
        raise LintError(f"git {args[0]} failed: {result.stderr.strip()[:200]}")
    return result.stdout


def read_at_revision(rev: str, path: str) -> str | None:
    """A file's text at a revision (undecodable bytes replaced, so binary files are skipped, not fatal)."""
    result = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=False)  # noqa: S603, S607 - fixed argv
    return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else None


def changed_files(merge_base: str) -> list[Change]:
    """Added, modified and renamed files between the merge-base and HEAD; deletions need no lint."""
    fields = git("diff", "--name-status", "-M", "-z", merge_base, "HEAD").split("\0")
    changes, index = [], 0
    while index < len(fields) - 1:
        status = fields[index][0]
        if status in "RC":
            changes.append(Change(status, fields[index + 2], fields[index + 1] if status == "R" else None))
            index += 3
            continue
        if status in "AMT":
            changes.append(Change(status, fields[index + 1], fields[index + 1] if status != "A" else None))
        index += 2
    return changes


def is_shell(path: str, text: str) -> bool:
    return path.endswith(".sh") or bool(SHELL_SHEBANG.match(text.split("\n", 1)[0]))


# --- ruff --------------------------------------------------------------------------------------


def function_spans(tree: ast.AST) -> list[tuple[int, int, str, str]]:
    """(first line, last line, qualified name, body signature) of every function, outermost first."""
    spans: list[tuple[int, int, str, str]] = []

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}{child.name}"
                if not isinstance(child, ast.ClassDef):
                    spans.append((child.lineno, child.end_lineno or child.lineno, name, _signature(child)))
                visit(child, f"{name}.")

    visit(tree, "")
    return spans


def _signature(node: ast.AST) -> str:
    renamed = ast.parse(ast.unparse(node)).body[0]
    renamed.name = ""  # type: ignore[attr-defined]
    return ast.dump(renamed)


def enclosing(spans: list[tuple[int, int, str, str]], line: int) -> str | None:
    inside = [span for span in spans if span[0] <= line <= span[1]]
    return max(inside, key=lambda span: span[0])[2] if inside else None


def ruff_findings(root: Path, path: str, config: Path, extra: list[str]) -> list[dict]:
    if shutil.which("ruff") is None:
        raise LintError("ruff is not installed (requirements-dev.txt)")
    result = subprocess.run(["ruff", "check", "--no-cache", "--config", str(config), "--output-format", "json",  # noqa: S603, S607 - fixed argv
                             *extra, path], cwd=root, capture_output=True, text=True, check=False)
    if result.returncode not in (0, 1):
        raise LintError(f"ruff failed on {path}: {result.stderr.strip()[:200]}")
    return json.loads(result.stdout or "[]")


def python_findings(path: str, text: str, config_text: str, renames: dict[str, str]) -> list[Finding]:
    """ruff findings of one version of a Python file, keyed by the enclosing function or the line text."""
    with tempfile.TemporaryDirectory(prefix="lint-") as tmp:
        root = Path(tmp)
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
        config = root / CONFIG
        config.write_text(config_text, encoding="utf-8")
        raw = ruff_findings(root, path, config, []) + ruff_findings(root, path, config, ["--ignore-noqa", "--select", NO_NOQA_RULES])
    try:
        spans = function_spans(ast.parse(text))
    except SyntaxError:
        spans = []
    context = FileContext(path, spans, text.splitlines(), renames)
    unique = {(r["code"], r["location"]["row"], r["message"]) for r in raw}
    return [_python_finding(context, code, row, message) for code, row, message in sorted(unique)]


@dataclass(frozen=True)
class FileContext:
    """One version of a Python file: its path, function spans, lines and renamed functions."""

    path: str
    spans: list[tuple[int, int, str, str]]
    lines: list[str]
    renames: dict[str, str]


def _python_finding(context: FileContext, code: str, row: int, message: str) -> Finding:
    function = enclosing(context.spans, row)
    if function:
        scope = context.renames.get(function, function)
    else:
        scope = context.lines[row - 1].strip() if 0 < row <= len(context.lines) else ""
    value = LIMIT_VALUE.search(message)
    return Finding((context.path, code, scope), int(value.group(1)) if value else None, row, message)


def rename_map(old_text: str | None, new_text: str) -> dict[str, str]:
    """New function name -> old name, for functions whose body is unchanged but whose name is new."""
    if old_text is None:
        return {}
    try:
        old, new = function_spans(ast.parse(old_text)), function_spans(ast.parse(new_text))
    except SyntaxError:
        return {}
    old_names, new_names = {name for _a, _b, name, _s in old}, {name for _a, _b, name, _s in new}
    # Only a function whose old name is gone can have been renamed.
    by_signature = {signature: name for _a, _b, name, signature in old if name not in new_names}
    return {name: by_signature[sig] for _a, _b, name, sig in new if name not in old_names and sig in by_signature}


# --- shellcheck --------------------------------------------------------------------------------


def shell_findings(path: str, text: str) -> list[Finding]:
    if shutil.which("shellcheck") is None:
        raise LintError("shellcheck is not installed (shellcheck-py in requirements-dev.txt)")
    with tempfile.TemporaryDirectory(prefix="lint-") as tmp:
        target = Path(tmp) / "script"
        target.write_text(text, encoding="utf-8")
        result = subprocess.run(["shellcheck", "--format", "json1", str(target)], capture_output=True, text=True,  # noqa: S603, S607 - fixed argv
                                check=False)
    if result.returncode not in (0, 1):
        raise LintError(f"shellcheck failed on {path}: {result.stderr.strip()[:200]}")
    lines = text.splitlines()
    return [Finding((path, f"SC{c['code']}", lines[c["line"] - 1].strip() if c["line"] <= len(lines) else ""), None,
                    c["line"], c["message"]) for c in json.loads(result.stdout or "{}").get("comments", [])]


# --- Comparison and headers --------------------------------------------------------------------


def file_findings(change: Change, merge_base: str, config_text: str) -> tuple[list[Finding], list[Finding]]:
    """Findings of the merge-base version (under the new path) and of the new version of one file."""
    new_text = read_at_revision("HEAD", change.path)
    if new_text is None:
        raise LintError(f"cannot read {change.path} at HEAD")
    old_text = read_at_revision(merge_base, change.old_path) if change.old_path else None
    if is_shell(change.path, new_text):
        old = shell_findings(change.path, old_text) if old_text is not None else []
        return old, shell_findings(change.path, new_text)
    if not change.path.endswith(".py"):
        return [], []
    old = python_findings(change.path, old_text, config_text, {}) if old_text is not None else []
    return old, python_findings(change.path, new_text, config_text, rename_map(old_text, new_text))


def added_or_worse(old: list[Finding], new: list[Finding]) -> list[str]:
    """Keys that occur more often, or with a higher value, than at the merge-base."""
    before, after = defaultdict(list), defaultdict(list)
    for finding in old:
        before[finding.key].append(finding.value or 0)
    for finding in new:
        after[finding.key].append(finding.value or 0)
    problems = []
    for key, values in after.items():
        worse = len(values) > len(before[key]) or max(values) > max(before[key], default=0)
        if worse:
            sample = next(f for f in new if f.key == key)
            problems.append(f"{key[0]}:{sample.line}: {key[1]} {sample.message} (new or worse than at the merge-base)")
    return problems


def header_problem(path: str, text: str) -> str | None:
    """An added file of a commented type must start with a purpose comment (POC-D7)."""
    name = Path(path).name
    if path.endswith(".py"):
        return _python_header(path, text)
    if path.endswith(".md"):
        return _markdown_header(path, text)
    if Path(path).suffix in HEADER_SUFFIXES or name == "Dockerfile" or name.startswith("Dockerfile.") or is_shell(path, text):
        return _comment_header(path, text)
    return None


def _python_header(path: str, text: str) -> str | None:
    try:
        docstring = ast.get_docstring(ast.parse(text))
    except SyntaxError:
        return f"{path}: cannot parse the file to find its module docstring"
    return None if docstring and docstring.strip() else f"{path}: an added Python file needs a module docstring that says what the file is for"


def _markdown_header(path: str, text: str) -> str | None:
    """A Markdown file starts with a `#` title followed by a paragraph (AGENTS.md coding rule 8)."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 2 and lines[0].startswith("# ") and not lines[1].startswith("#"):
        return None
    return f"{path}: an added Markdown file needs a `#` title followed by a paragraph that says what it is for"


def _comment_header(path: str, text: str) -> str | None:
    lines = text.splitlines()
    while lines and (lines[0].startswith("#!") or lines[0].strip() == "---"):
        lines = lines[1:]
    first = lines[0].strip() if lines else ""
    if first.startswith("#") and len(first.strip("# ")) > 0 and not TOOL_DIRECTIVE.match(first):
        return None
    return f"{path}: an added file needs a first-line comment that says what the file is for"


def lint(base: str) -> list[str]:
    merge_base = git("merge-base", base, "HEAD").strip()
    config_text = read_at_revision(merge_base, CONFIG) or read_at_revision("HEAD", CONFIG)
    if config_text is None:
        raise LintError(f"{CONFIG} exists neither at the merge-base nor at HEAD")
    problems = []
    for change in changed_files(merge_base):
        old, new = file_findings(change, merge_base, config_text)
        problems += added_or_worse(old, new)
        if change.status in "AC":
            header = header_problem(change.path, read_at_revision("HEAD", change.path) or "")
            problems += [header] if header else []
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Fail on lint violations a change adds or worsens.")
    parser.add_argument("--base", required=True, help="the base reference, e.g. origin/poc/agentic-sdlc")
    args = parser.parse_args(argv)
    try:
        problems = lint(args.base)
    except LintError as error:
        print(f"[lint] FAILED: {error}", file=sys.stderr)
        return 2
    for problem in problems:
        print(f"[lint] {problem}")
    print(f"[lint] {'FAILED' if problems else 'PASSED'} ({len(problems)} new or worsened findings)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
