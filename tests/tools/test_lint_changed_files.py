"""Tooling tests for scripts/lint_changed_files.py (agentic-sdlc-poc slice 3, test plan "lint").

Each test builds a throwaway Git repository with a base commit (holding the repository's real
`ruff_changed_files.toml`) and one change on a branch, and runs the real gate against it. Shell cases
need `shellcheck` (shellcheck-py in requirements-dev.txt).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "lint_changed_files.py"
CONFIG = ROOT / "ruff_changed_files.toml"
DOC = '"""Module under test."""\n\n'


def _git(repo: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@example.org"}
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,  # noqa: S603, S607 - test git
                          env=env).stdout.strip()


def _write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)


class Repo:
    """A repository with `main` as the base and `change` as the branch under lint."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def base(self, files: dict[str, str]) -> None:
        for rel, text in files.items():
            _write(self.root, rel, text)
        _commit(self.root, "base")
        _git(self.root, "checkout", "-q", "-b", "change")

    def change(self, files: dict[str, str | None], renames: dict[str, str] | None = None) -> None:
        for old, new in (renames or {}).items():
            _git(self.root, "mv", old, new)
        for rel, text in files.items():
            if text is None:
                (self.root / rel).unlink()
            else:
                _write(self.root, rel, text)
        _commit(self.root, "change")

    def lint(self, base: str = "main") -> tuple[int, str]:
        result = subprocess.run([sys.executable, str(SCRIPT), "--base", base], cwd=self.root, capture_output=True,  # noqa: S603 - the gate under test
                                text=True, check=False)
        return result.returncode, result.stdout + result.stderr


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    shutil.copy(CONFIG, root / "ruff_changed_files.toml")
    return Repo(root)


def function_source(name: str, ifs: int = 0, statements: int = 0, if_else: int = 0, args: int = 1) -> str:
    """A function with complexity 1 + ifs, `statements` assignments, `if_else` pairs and `args` arguments."""
    params = ", ".join(f"a{i}" for i in range(args))
    body = [f"a0 = a0 + {i}" for i in range(statements)]
    body += [f"if a0 == {i}:\n    return {i}" for i in range(ifs)]
    body += [f"if a0 == {100 + i}:\n    a0 = 1\nelse:\n    a0 = 2" for i in range(if_else)]
    body.append("return a0")
    inner = "\n".join("    " + line for block in body for line in block.split("\n"))
    return f"def {name}({params}):\n{inner}\n"


def method_source(name: str, ifs: int) -> str:
    """The same function indented as a method of a class."""
    return "".join("    " + line if line.strip() else line for line in function_source(name, ifs=ifs).splitlines(keepends=True))


def module_source(*functions: str) -> str:
    return DOC + "\n\n".join(functions)


# --- Complexity --------------------------------------------------------------------------------


def test_new_function_at_the_complexity_limit_passes(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": module_source(function_source("keep"), function_source("new_fn", ifs=9))})
    assert repo.lint()[0] == 0


def test_new_function_over_the_complexity_limit_fails(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": module_source(function_source("keep"), function_source("new_fn", ifs=10))})
    code, out = repo.lint()
    assert code == 1 and "C901" in out and "(11 > 10)" in out


@pytest.mark.parametrize(("before", "after"), [(8, 12), (11, 13)], ids=["9-to-13", "12-to-14"])
def test_existing_function_made_more_complex_fails(repo: Repo, before: int, after: int) -> None:
    repo.base({"services/a.py": module_source(function_source("work", ifs=before))})
    repo.change({"services/a.py": module_source(function_source("work", ifs=after))})
    code, out = repo.lint()
    assert code == 1 and "C901" in out


def test_over_limit_function_improved_passes(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("work", ifs=13))})
    repo.change({"services/a.py": module_source(function_source("work", ifs=11))})
    assert repo.lint()[0] == 0


def test_over_limit_function_renamed_with_an_unchanged_body_passes(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("old_name", ifs=11))})
    repo.change({"services/a.py": module_source(function_source("new_name", ifs=11))})
    assert repo.lint()[0] == 0


def test_over_limit_function_renamed_and_raised_fails(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("old_name", ifs=11))})
    repo.change({"services/a.py": module_source(function_source("new_name", ifs=12))})
    assert repo.lint()[0] == 1


def test_method_raised_in_one_class_fails_while_the_same_name_elsewhere_is_unchanged(repo: Repo) -> None:
    base = DOC + "class A:\n" + method_source("run", 11) + "\n\nclass B:\n" + method_source("run", 11)
    repo.base({"services/a.py": base})
    repo.change({"services/a.py": DOC + "class A:\n" + method_source("run", 11) + "\n\nclass B:\n"
                 + method_source("run", 12)})
    code, out = repo.lint()
    assert code == 1 and "(13 > 10)" in out and "(12 > 10)" not in out


# --- Existing debt -----------------------------------------------------------------------------


def test_unchanged_over_limit_function_in_a_modified_file_passes(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("debt", ifs=12), function_source("other"))})
    repo.change({"services/a.py": module_source(function_source("debt", ifs=12), function_source("other", statements=2))})
    assert repo.lint()[0] == 0


def test_edit_that_keeps_an_over_limit_function_at_the_same_complexity_passes(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("debt", ifs=12))})
    repo.change({"services/a.py": module_source(function_source("debt", ifs=12, statements=1))})
    assert repo.lint()[0] == 0


# --- Function size -----------------------------------------------------------------------------


def test_functions_at_the_size_limits_pass(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": module_source(function_source("keep"), function_source("stmts", statements=50), function_source("branches", if_else=6),
                                         function_source("arguments", args=5))})
    assert repo.lint()[0] == 0


@pytest.mark.parametrize(("function", "rule"), [(function_source("big", statements=51), "PLR0915"), (function_source("big", if_else=6, ifs=1), "PLR0912"),
                                                (function_source("big", args=6), "PLR0913")], ids=["51-statements", "13-branches", "6-arguments"])
def test_functions_over_the_size_limits_fail(repo: Repo, function: str, rule: str) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": module_source(function_source("keep"), function)})
    code, out = repo.lint()
    assert code == 1 and rule in out


def test_fixing_one_six_argument_function_while_adding_another_fails(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("first", args=6))})
    repo.change({"services/a.py": module_source(function_source("first", args=5), function_source("second", args=6))})
    code, out = repo.lint()
    assert code == 1 and "PLR0913" in out


# --- noqa and the configuration ----------------------------------------------------------------


def test_justified_noqa_on_a_security_rule_and_on_e402_passes(repo: Repo) -> None:
    repo.base({"scripts/a.py": module_source(function_source("keep"))})
    repo.change({"scripts/a.py": module_source(function_source("keep")) + "\nimport subprocess  # noqa: E402 - after the helpers on purpose\n\n\n"
                 "def run_ls():\n    return subprocess.run(['ls'], check=False)  # noqa: S603, S607 - fixed argv, no shell\n"})
    assert repo.lint()[0] == 0


@pytest.mark.parametrize(("addition", "rule"), [
    (function_source("big", ifs=10).replace("):\n", "):  # noqa: C901\n", 1), "C901"),
    ("\nimport json  # noqa: F401\n", "F401"),
], ids=["noqa-c901", "noqa-f401"])
def test_noqa_does_not_silence_a_limit_or_an_unused_import(repo: Repo, addition: str, rule: str) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": module_source(function_source("keep")) + "\n\n" + addition})
    code, out = repo.lint()
    assert code == 1 and rule in out


def test_raising_the_limit_in_the_changed_config_does_not_loosen_the_gate(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    loosened = CONFIG.read_text().replace("max-complexity = 10", "max-complexity = 30")
    repo.change({"ruff_changed_files.toml": loosened, "services/a.py": module_source(function_source("keep"), function_source("big", ifs=12))})
    code, out = repo.lint()
    assert code == 1 and "C901" in out


# --- Default rules, naming and security --------------------------------------------------------


def test_new_unused_import_fails(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": DOC + "import json\n\n\n" + function_source("keep")})
    code, out = repo.lint()
    assert code == 1 and "F401" in out


def test_new_snake_case_function_passes(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": module_source(function_source("keep"), function_source("snake_case_name"))})
    assert repo.lint()[0] == 0


@pytest.mark.parametrize(("path", "name"), [("services/a.py", "camelCase"), ("tests/test_a.py", "test_intent_TTFF")])
def test_new_name_outside_the_conventions_fails(repo: Repo, path: str, name: str) -> None:
    repo.base({path: module_source(function_source("keep"))})
    repo.change({path: module_source(function_source("keep"), function_source(name))})
    code, out = repo.lint()
    assert code == 1 and "N802" in out


def test_assert_in_a_new_test_passes(repo: Repo) -> None:
    repo.base({"tests/test_a.py": module_source(function_source("keep"))})
    repo.change({"tests/test_a.py": module_source(function_source("keep"), "def test_x():\n    assert 1 + 1 == 2\n")})
    assert repo.lint()[0] == 0


def test_shell_true_in_a_new_script_fails(repo: Repo) -> None:
    repo.base({"scripts/a.py": module_source(function_source("keep"))})
    repo.change({"scripts/b.py": DOC + "import subprocess\n\n\ndef run(cmd):\n    return subprocess.run(cmd, shell=True, check=False)\n"})
    code, out = repo.lint()
    assert code == 1 and "S602" in out


# --- Shell -------------------------------------------------------------------------------------


GOOD_SHELL = "#!/usr/bin/env bash\n# Prints a greeting for the lint tests.\nset -euo pipefail\necho \"hello\"\n"
BAD_SHELL = "#!/usr/bin/env bash\n# Prints its argument for the lint tests.\necho $1\n"


def test_new_script_that_passes_shellcheck_passes(repo: Repo) -> None:
    repo.base({"README.md": "base\n"})
    repo.change({"scripts/good.sh": GOOD_SHELL})
    assert repo.lint()[0] == 0


@pytest.mark.parametrize("path", ["scripts/bad.sh", "scripts/bad-no-extension"])
def test_new_script_with_a_shellcheck_finding_fails(repo: Repo, path: str) -> None:
    repo.base({"README.md": "base\n"})
    repo.change({path: BAD_SHELL})
    code, out = repo.lint()
    assert code == 1 and "SC2086" in out


# --- Headers -----------------------------------------------------------------------------------


@pytest.mark.parametrize(("good", "bad"), [("services/new.py", "services/other.py"),
                                           ("services/_private.py", "services/_other.py"),
                                           ("services/pkg/__init__.py", "services/pkg2/__init__.py")])
def test_new_python_file_with_a_docstring_passes_and_without_fails(repo: Repo, good: str, bad: str) -> None:
    repo.base({"README.md": "base\n"})
    repo.change({good: DOC + "VALUE = 1\n"})
    assert repo.lint()[0] == 0
    repo.change({bad: "VALUE = 1\n"})
    code, out = repo.lint()
    assert code == 1 and f"{bad}: an added Python file needs a module docstring" in out


@pytest.mark.parametrize(("path", "good"), [
    ("scripts/new.sh", GOOD_SHELL),
    ("config/new.yaml", "---\n# Settings for the lint tests.\nkey: value\n"),
    ("config/new.toml", "# Settings for the lint tests.\nkey = 1\n"),
    ("services/x/Dockerfile", "# Image for the lint tests.\nFROM scratch\n"),
    ("services/opa/new.rego", "# Policy for the lint tests.\npackage x\n"),
])
def test_new_file_with_a_purpose_comment_passes(repo: Repo, path: str, good: str) -> None:
    repo.base({"README.md": "base\n"})
    repo.change({path: good, "config/data.json": "{}\n"})
    assert repo.lint()[0] == 0


@pytest.mark.parametrize(("path", "bad"), [
    ("scripts/new.sh", "#!/usr/bin/env bash\nset -euo pipefail\necho \"hello\"\n"),
    ("scripts/directive.sh", "#!/usr/bin/env bash\n# shellcheck disable=SC2034\nset -euo pipefail\n"),
    ("config/new.yaml", "key: value\n"),
    ("config/new.toml", "key = 1\n"),
    ("services/x/Dockerfile", "FROM scratch\n"),
    ("services/opa/new.rego", "package x\n"),
    ("config/coding.toml", "# -*- coding: utf-8 -*-\nkey = 1\n"),
    ("config/schema.yaml", "# yaml-language-server: $schema=schema.json\nkey: value\n"),
    ("config/noqa.toml", "# noqa: E501\nkey = 1\n"),
    ("config/typed.toml", "# type: ignore\nkey = 1\n"),
], ids=["shell", "shell-directive-only", "yaml", "toml", "dockerfile", "rego", "coding-directive",
        "yaml-language-server", "noqa", "type-comment"])
def test_new_file_without_a_purpose_comment_fails(repo: Repo, path: str, bad: str) -> None:
    repo.base({"README.md": "base\n"})
    repo.change({path: bad})
    code, out = repo.lint()
    assert code == 1 and f"{path}: an added file needs a first-line comment" in out


def test_new_python_file_with_only_a_coding_line_fails(repo: Repo) -> None:
    repo.base({"README.md": "base\n"})
    repo.change({"scripts/coding.py": "# -*- coding: utf-8 -*-\nVALUE = 1\n"})
    code, out = repo.lint()
    assert code == 1 and "scripts/coding.py: an added Python file needs a module docstring" in out


def test_added_binary_file_is_skipped_without_an_error(repo: Repo) -> None:
    repo.base({"README.md": "base\n"})
    (repo.root / "docs").mkdir()
    (repo.root / "docs" / "diagram.png").write_bytes(bytes(range(256)) * 4)
    repo.change({})
    code, out = repo.lint()
    assert code == 0 and "PASSED" in out


# --- Renames, merge-base and failing closed ----------------------------------------------------


def test_renamed_file_with_unchanged_violations_passes_and_gaining_one_fails(repo: Repo) -> None:
    repo.base({"services/old.py": module_source(function_source("debt", ifs=12))})
    repo.change({}, renames={"services/old.py": "services/new.py"})
    assert repo.lint()[0] == 0
    repo.change({"services/new.py": module_source(function_source("debt", ifs=12), function_source("more", ifs=11))})
    code, out = repo.lint()
    assert code == 1 and "C901" in out and "more" in out


def test_base_that_moved_on_does_not_fail_files_the_change_did_not_touch(repo: Repo) -> None:
    """The base fixes a violation after the branch point; compared with the base tip instead of the
    merge-base, the change's untouched copy of that file would look like a new violation."""
    repo.base({"services/a.py": module_source(function_source("keep")),
               "services/debt.py": DOC + "import json\n"})
    repo.change({"services/a.py": module_source(function_source("keep"), function_source("small"))})
    _git(repo.root, "checkout", "-q", "main")
    _write(repo.root, "services/debt.py", DOC + "VALUE = 1\n")
    _commit(repo.root, "base fixes its violation")
    _git(repo.root, "checkout", "-q", "change")
    assert repo.lint()[0] == 0


def _tool_dir(tmp_path: Path, ruff_script: str | None) -> str:
    """A PATH with git and python, and a fake ruff (or none)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("git", "python3"):
        (bin_dir / tool).symlink_to(shutil.which(tool) or tool)
    if ruff_script is not None:
        (bin_dir / "ruff").write_text(ruff_script, encoding="utf-8")
        (bin_dir / "ruff").chmod(0o755)
    return str(bin_dir)


@pytest.mark.parametrize("ruff_script", [None, "#!/bin/sh\necho 'config error' >&2\nexit 2\n"],
                         ids=["ruff-missing", "ruff-error"])
def test_missing_or_failing_tool_fails_the_run(repo: Repo, tmp_path: Path, ruff_script: str | None) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    repo.change({"services/a.py": module_source(function_source("keep"), function_source("more"))})
    result = subprocess.run([sys.executable, str(SCRIPT), "--base", "main"], cwd=repo.root, capture_output=True,  # noqa: S603 - the gate under test
                            text=True, check=False, env={**os.environ, "PATH": _tool_dir(tmp_path, ruff_script)})
    assert result.returncode == 2 and "ruff" in result.stderr


def test_missing_base_reference_fails_with_a_message(repo: Repo) -> None:
    repo.base({"services/a.py": module_source(function_source("keep"))})
    code, out = repo.lint(base="origin/does-not-exist")
    assert code == 2 and "merge-base" in out


def test_plain_ruff_check_keeps_the_default_rules_and_passes_on_the_tree() -> None:
    result = subprocess.run(["ruff", "check", "--no-cache", "services", "scripts"], cwd=ROOT, capture_output=True,  # noqa: S603, S607 - fixed argv
                            text=True, check=False)
    assert result.returncode == 0, result.stdout
