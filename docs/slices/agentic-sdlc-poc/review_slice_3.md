# Review record — agentic-sdlc-poc slice 3 (changed-files lint)

Implementation review of slice 3 of the [plan](plan.md), on the branch
`poc/slice-3-changed-files-lint`, which was built on slice 2 (`poc/slice-2-review-launcher`) and
rebased onto `poc/agentic-sdlc` after slice 2 merged (PR #35). The reviews ran through `scripts/run_independent_review.py`; each attempt is in
[`review_attempts.jsonl`](review_attempts.jsonl) (unit `slice_3`). This record keeps the task
prompts and released reports verbatim, each with its SHA-256, which matches the attempt log, and the
author's answers.

**Reviewer.** A fresh headless Claude session (Opus 5.5, `claude-opus-5-5`), never the author,
confined by the launcher to a frozen copy of the reviewed commit without this record and the attempt
log, with the rules of the base branch `poc/slice-2-review-launcher` at `6512f96` in its
prompt. Round 1 at high effort (the initial review), round 2 at medium (a focused recheck by the same
model and role, given its round-1 report and the answers).

**Command.** As in [`review_slice_2.md`](review_slice_2.md): the launcher invoked with `--base
poc/slice-2-review-launcher`, `--unit slice_3`, `--reviewer
"impl:<scratch>/task_r<n>.md:claude-opus-5-5:<high|medium>"` and the paths under review: round 1
`scripts/lint_changed_files.py`, `ruff_changed_files.toml`, `tests/tools/test_lint_changed_files.py`,
`Makefile`, `.github/workflows/ci.yml`, `AGENTS.md`, `requirements-dev.txt`,
`tests/tools/test_gate_consistency.py`, `docs/STATUS.md`; round 2 the lint script and its tests and
the gate-consistency script and its tests.

## Round 1 (initial review, high effort)

Reviewed commit `c136da0`; attempt `slice_3/c1/r1/impl/1`: 247 seconds, 16 turns, 14 tool calls (all inside the copy, none denied), 24,397 output tokens, CLI cost estimate USD 1.24; afterwards the 5-hour window stood at 41% and the weekly window at 4%. Status completed,
verdict "no".

### Task prompt (verbatim, SHA-256 `e8b454df05588f759b5e5c6140c38c442a63b8ac2f66db0bfe54042b1b383de2`)

`````text
This is the implementation review of slice 3 of the agentic-SDLC PoC (review round 1, the initial review): the changed-files lint gate. The change adds scripts/lint_changed_files.py, ruff_changed_files.toml, the tooling tests in tests/tools/test_lint_changed_files.py, a `lint` Makefile target and CI job, the ruff and shellcheck-py pins, the AGENTS.md gates row, the gate-consistency ruleset change, and the close-out documents.

## The intent

The approved plan is docs/slices/agentic-sdlc-poc/plan.md (merged with PR #31): read "Slice 3 — Changed-files lint", the decisions POC-D7 and POC-D8, the "Checks this plan adds" table, "Retirement and compatibility" and the user actions. The test plan is docs/slices/agentic-sdlc-poc/test_plan.md, section "Slice 3 — lint", and "Independent review at the implementation PR". The base branch is slice 2 (not yet merged into poc/agentic-sdlc); slices 1 and 2 are not part of this change.

## Environment facts (probed by the author on 2026-11-08)

- ruff 0.15.18 (the pinned version). Probes with ruff_changed_files.toml: complexity 10 passes and 11 is reported "(11 > 10)"; 6 if/else pairs (12 branches) pass and 13 branches are reported; 5 arguments pass and 6 are reported; 50 assignments plus a return pass and 51 assignments are reported as "Too many statements (51 > 50)".
- `shellcheck` is not installed on the author's machine (installing shellcheck-py was not permitted there), so the 6 shell cases of the new test file have not run locally; CI installs shellcheck-py from requirements-dev.txt. Locally 369 tooling tests pass and only those 6 fail, with "shellcheck is not installed".
- `make lint` passes against the slice-2 branch and against origin/poc/agentic-sdlc (slices 1 to 3 together).
- The ruleset of poc/agentic-sdlc (id 26764115) is readable without a token (HTTP 200) and requires 11 checks today, not `lint`; the plan's user action 2 adds `lint` during this slice's PR, after its first run. Until then, gate-consistency on this PR is expected to fail on "CI job lint is not a required check".
- Deliberately breaking the gate (honouring noqa on the limit rules, reading the configuration from the change instead of the merge-base, ignoring the value, no rename matching, no header check) made at least one test fail each time.

## Questions to answer (the test plan's implementation questions)

1. Tests: for each new test, which wrong behaviour would still pass it (the gate never run, a tool error read as success, a missing base or empty output read as success)? Does its assertion match its row in the test plan "Slice 3 — lint"? Name any row without a test.
2. Keys: does the change make a key, socket or secret reachable by a service or process outside its holders, or put an operational detail into a public record?
3. Rules and names (POC-D7): does each new file's purpose comment say what the file is for, and do its names say what each part does?
4. Does anything in the change contradict the approved plan or the base branch's rules, or claim more than it does? Which tracked document does the change make false?
`````

### Report (rendered from the released JSON, which follows it verbatim)

Verdict: **no** (approvable within the threat model).

#### F1 (blocking) — `tests/tools/test_lint_changed_files.py:286`

- **Problem:** The 'Python header' row in the test plan says a new module, a private module and an `__init__.py` each fail without a docstring. The test builds the no-docstring file with `path.replace(".py", "_two.py")`, which turns `services/pkg/__init__.py` into `services/pkg/__init___two.py`. That is an ordinary module, not a package `__init__.py`. So the test never checks an `__init__.py` without a docstring, and that part of the row has no test (POC-D7, plan: 'including private modules and `__init__.py`').
- **Evidence:** Lines 281-288: `@pytest.mark.parametrize("path", ["services/new.py", "services/_private.py", "services/pkg/__init__.py"])` ... `repo.change({path.replace(".py", "_two.py"): "VALUE = 1\n"})`. The fail case for `__init__.py` therefore writes `__init___two.py`.
- **Failure scenario:** A plausible honest regression is to exempt `__init__.py` from `_python_header`, as ruff's D104 conventions and empty package files encourage. That change would leave every test green. A later PR could then add a package `__init__.py` with no docstring and `make lint` would pass, contrary to POC-D7 and the AGENTS.md lint row. Fix: write the no-docstring case as an `__init__.py` in another package, for example `services/pkg2/__init__.py`.

#### F2 (blocking) — `tests/tools/test_lint_changed_files.py:311`

- **Problem:** The 'Other headers' row covers shell, YAML, TOML, Dockerfile and Rego files. It must fail a file whose only first comment is a tool directive, and it names `# -*- coding -*-` as an example. The test checks the coding directive only on a `.py` file (`scripts/coding.py`). Python files go through `_python_header`, the docstring check, so the `-\*-` alternative of `TOOL_DIRECTIVE` in `_comment_header` never runs. Of the planned directives, only `# shellcheck` is exercised on the comment-header path.
- **Evidence:** Line 311: `("scripts/coding.py", "# -*- coding: utf-8 -*-\nVALUE = 1\n")`. `header_problem` sends every `.py` path to `_python_header` (script line 237), and that file fails for the missing docstring whatever `TOOL_DIRECTIVE` contains.
- **Failure scenario:** Dropping `-\*-` (or `yaml-language-server`, `noqa`, `type:`) from `TOOL_DIRECTIVE` would leave all tests green. A new TOML, YAML or shell file whose only header is `# -*- mode: ... -*-` would then pass the purpose-comment check. Fix: run the coding-directive case on one of the comment-header types, for example `config/new.toml` containing `# -*- coding: utf-8 -*-\nkey = 1\n`.

#### F3 (advisory) — `scripts/lint_changed_files.py:125`

- **Problem:** No test shows that a tool error or a missing tool fails the run, although the AGENTS.md row claims 'a missing base or tool fails'. Question 1 asks about exactly this ('a tool error read as success'). If the `returncode not in (0, 1)` checks in `ruff_findings` and `shell_findings`, or the `shutil.which` checks, were removed, every test would still pass. The test plan's 'Fail closed' row only names a missing base, so this is advisory.
- **Evidence:** `ruff_findings`: `if result.returncode not in (0, 1): raise LintError` followed by `json.loads(result.stdout or "[]")`. No test makes ruff or shellcheck exit with 2 or be absent from PATH. The author's local run, where shellcheck was missing, is the only evidence that the missing-tool path works.
- **Failure scenario:** Suppose a later edit relaxes the return-code check. A ruff configuration error (exit 2, empty stdout) would then become `[]`, meaning zero findings, and the gate would pass. A cheap guard would be one test that runs the gate with PATH limited to `git` (or with a fake `ruff` that exits 2) and asserts exit code 2.

#### F4 (advisory) — `scripts/check_gate_consistency.py:90`

- **Problem:** The change points `RULESET_URL` at the PoC ruleset and rewrites the AGENTS.md gate-consistency row to 'the integration branch's ruleset'. Three places still say 'main': the script's docstring (line 7), its error message (line 90, 'is not a required check of the main ruleset') and the CI step name (ci.yml line 188, 'main's required checks'). They are now false.
- **Evidence:** check_gate_consistency.py:7 says 'the required status checks of the `main` ruleset'. Line 90 is `f"CI job {j} is not a required check of the main ruleset"`. ci.yml:188 is the step name 'Check that AGENTS.md CI gates, CI jobs and main's required checks agree'. The Makefile now reads ruleset 26764115 (poc/agentic-sdlc).
- **Failure scenario:** Gate-consistency is expected to fail on this PR until the user carries out user action 2. When it does, it will print 'CI job lint is not a required check of the main ruleset'. That could lead the user to add `lint` to the `main`/`basic` ruleset, which the plan says would block every `main` PR.

#### F5 (advisory) — `scripts/lint_changed_files.py:205`

- **Problem:** `file_findings` reads every changed file with `git show` and `text=True` before it checks the file type. A binary file that is added, modified or renamed (the repo tracks PNGs in docs/archive/diagrams/, and retiring a document with `git mv` creates a rename) raises an uncaught UnicodeDecodeError. The gate then crashes with a traceback instead of skipping the file.
- **Evidence:** `show()` calls `subprocess.run([...], capture_output=True, text=True)`, and `file_findings` calls `show("HEAD", change.path)` unconditionally on its first line. The repo has docs/archive/diagrams/*.png.
- **Failure scenario:** A PR that adds a diagram PNG, or archives a document that contains one, fails `lint` with a traceback (a false red, not a false green). Skipping paths that are neither .py nor shell before reading them, or decoding with errors='replace', would avoid this.

#### F6 (advisory) — `tests/tools/test_lint_changed_files.py:332`

- **Problem:** The merge-base test would also pass if the gate diffed against the base tip instead of the merge-base. The file the base adds (`services/other.py`) would show up as a deletion, and deletions are skipped. So the test matches its row literally but does not show that the merge-base is used. In CI the PR merge ref makes the merge-base equal to the base tip anyway, so the difference only matters locally.
- **Evidence:** Lines 332-339: the base adds a new file containing `import json` after the branch point. With `git diff main HEAD`, that file is status D and `changed_files` drops it.
- **Failure scenario:** Suppose `git merge-base` were dropped. When the base fixes a violation in a file the change did not touch, a local `make lint` would report the change branch's unchanged copy as new, and no test would catch this. A version of the test in which the base modifies an existing file to remove a violation would tell the two behaviours apart.

#### F7 (advisory) — `scripts/lint_changed_files.py:65`

- **Problem:** Naming (POC-D7): some names do not say what they do. `show` reads a file at a revision, so something like `read_at_revision` would say so. `VALUE` is the regex for the measured value in a limit message, so `LIMIT_VALUE` would be clearer. The test helpers `fn`, `method` and `module` build Python source text. The dataclasses `Change` and `Finding` have no docstrings. Every new file does have a purpose comment that says what it is for (both .py docstrings and the ruff_changed_files.toml header).
- **Evidence:** Line 35: `VALUE = re.compile(r"\((\d+) > \d+\)")`. Line 65: `def show(rev, path)`. Test file: `def fn(name, ifs=0, ...)`.
- **Failure scenario:** There is no functional failure. This is readability against POC-D7, for the reviewer's judgment.

#### F8 (advisory) — `tests/tools/test_lint_changed_files.py:317`

- **Problem:** The negative header tests assert `code == 1 and path in out`. Every finding line includes the file path, so any other finding on the same file would satisfy the assertion, header or not. Today none of those fixtures triggers a ruff or shellcheck finding, so the assertion holds, but it is looser than checking the header message ('needs a first-line comment' or 'module docstring').
- **Evidence:** Lines 313-317. `added_or_worse` formats findings as `f"{key[0]}:{sample.line}: ..."`, which also contains the path.
- **Failure scenario:** If a fixture were later edited so that it also triggered a shellcheck finding, a broken header check would no longer be noticed. Asserting on 'purpose' / 'first-line comment' text would prevent this.

<details><summary>Released report JSON (verbatim, SHA-256 <code>7a62ad69717ad31b880648b3eacc2cb7727949414a9ca95e981c950227ed85a8</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "Lines 281-288: `@pytest.mark.parametrize(\"path\", [\"services/new.py\", \"services/_private.py\", \"services/pkg/__init__.py\"])` ... `repo.change({path.replace(\".py\", \"_two.py\"): \"VALUE = 1\\n\"})`. The fail case for `__init__.py` therefore writes `__init___two.py`.",
      "failure_scenario": "A plausible honest regression is to exempt `__init__.py` from `_python_header`, as ruff's D104 conventions and empty package files encourage. That change would leave every test green. A later PR could then add a package `__init__.py` with no docstring and `make lint` would pass, contrary to POC-D7 and the AGENTS.md lint row. Fix: write the no-docstring case as an `__init__.py` in another package, for example `services/pkg2/__init__.py`.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F1",
      "kind": "blocking",
      "line": 286,
      "problem": "The 'Python header' row in the test plan says a new module, a private module and an `__init__.py` each fail without a docstring. The test builds the no-docstring file with `path.replace(\".py\", \"_two.py\")`, which turns `services/pkg/__init__.py` into `services/pkg/__init___two.py`. That is an ordinary module, not a package `__init__.py`. So the test never checks an `__init__.py` without a docstring, and that part of the row has no test (POC-D7, plan: 'including private modules and `__init__.py`')."
    },
    {
      "evidence": "Line 311: `(\"scripts/coding.py\", \"# -*- coding: utf-8 -*-\\nVALUE = 1\\n\")`. `header_problem` sends every `.py` path to `_python_header` (script line 237), and that file fails for the missing docstring whatever `TOOL_DIRECTIVE` contains.",
      "failure_scenario": "Dropping `-\\*-` (or `yaml-language-server`, `noqa`, `type:`) from `TOOL_DIRECTIVE` would leave all tests green. A new TOML, YAML or shell file whose only header is `# -*- mode: ... -*-` would then pass the purpose-comment check. Fix: run the coding-directive case on one of the comment-header types, for example `config/new.toml` containing `# -*- coding: utf-8 -*-\\nkey = 1\\n`.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F2",
      "kind": "blocking",
      "line": 311,
      "problem": "The 'Other headers' row covers shell, YAML, TOML, Dockerfile and Rego files. It must fail a file whose only first comment is a tool directive, and it names `# -*- coding -*-` as an example. The test checks the coding directive only on a `.py` file (`scripts/coding.py`). Python files go through `_python_header`, the docstring check, so the `-\\*-` alternative of `TOOL_DIRECTIVE` in `_comment_header` never runs. Of the planned directives, only `# shellcheck` is exercised on the comment-header path."
    },
    {
      "evidence": "`ruff_findings`: `if result.returncode not in (0, 1): raise LintError` followed by `json.loads(result.stdout or \"[]\")`. No test makes ruff or shellcheck exit with 2 or be absent from PATH. The author's local run, where shellcheck was missing, is the only evidence that the missing-tool path works.",
      "failure_scenario": "Suppose a later edit relaxes the return-code check. A ruff configuration error (exit 2, empty stdout) would then become `[]`, meaning zero findings, and the gate would pass. A cheap guard would be one test that runs the gate with PATH limited to `git` (or with a fake `ruff` that exits 2) and asserts exit code 2.",
      "file": "scripts/lint_changed_files.py",
      "id": "F3",
      "kind": "advisory",
      "line": 125,
      "problem": "No test shows that a tool error or a missing tool fails the run, although the AGENTS.md row claims 'a missing base or tool fails'. Question 1 asks about exactly this ('a tool error read as success'). If the `returncode not in (0, 1)` checks in `ruff_findings` and `shell_findings`, or the `shutil.which` checks, were removed, every test would still pass. The test plan's 'Fail closed' row only names a missing base, so this is advisory."
    },
    {
      "evidence": "check_gate_consistency.py:7 says 'the required status checks of the `main` ruleset'. Line 90 is `f\"CI job {j} is not a required check of the main ruleset\"`. ci.yml:188 is the step name 'Check that AGENTS.md CI gates, CI jobs and main's required checks agree'. The Makefile now reads ruleset 26764115 (poc/agentic-sdlc).",
      "failure_scenario": "Gate-consistency is expected to fail on this PR until the user carries out user action 2. When it does, it will print 'CI job lint is not a required check of the main ruleset'. That could lead the user to add `lint` to the `main`/`basic` ruleset, which the plan says would block every `main` PR.",
      "file": "scripts/check_gate_consistency.py",
      "id": "F4",
      "kind": "advisory",
      "line": 90,
      "problem": "The change points `RULESET_URL` at the PoC ruleset and rewrites the AGENTS.md gate-consistency row to 'the integration branch's ruleset'. Three places still say 'main': the script's docstring (line 7), its error message (line 90, 'is not a required check of the main ruleset') and the CI step name (ci.yml line 188, 'main's required checks'). They are now false."
    },
    {
      "evidence": "`show()` calls `subprocess.run([...], capture_output=True, text=True)`, and `file_findings` calls `show(\"HEAD\", change.path)` unconditionally on its first line. The repo has docs/archive/diagrams/*.png.",
      "failure_scenario": "A PR that adds a diagram PNG, or archives a document that contains one, fails `lint` with a traceback (a false red, not a false green). Skipping paths that are neither .py nor shell before reading them, or decoding with errors='replace', would avoid this.",
      "file": "scripts/lint_changed_files.py",
      "id": "F5",
      "kind": "advisory",
      "line": 205,
      "problem": "`file_findings` reads every changed file with `git show` and `text=True` before it checks the file type. A binary file that is added, modified or renamed (the repo tracks PNGs in docs/archive/diagrams/, and retiring a document with `git mv` creates a rename) raises an uncaught UnicodeDecodeError. The gate then crashes with a traceback instead of skipping the file."
    },
    {
      "evidence": "Lines 332-339: the base adds a new file containing `import json` after the branch point. With `git diff main HEAD`, that file is status D and `changed_files` drops it.",
      "failure_scenario": "Suppose `git merge-base` were dropped. When the base fixes a violation in a file the change did not touch, a local `make lint` would report the change branch's unchanged copy as new, and no test would catch this. A version of the test in which the base modifies an existing file to remove a violation would tell the two behaviours apart.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F6",
      "kind": "advisory",
      "line": 332,
      "problem": "The merge-base test would also pass if the gate diffed against the base tip instead of the merge-base. The file the base adds (`services/other.py`) would show up as a deletion, and deletions are skipped. So the test matches its row literally but does not show that the merge-base is used. In CI the PR merge ref makes the merge-base equal to the base tip anyway, so the difference only matters locally."
    },
    {
      "evidence": "Line 35: `VALUE = re.compile(r\"\\((\\d+) > \\d+\\)\")`. Line 65: `def show(rev, path)`. Test file: `def fn(name, ifs=0, ...)`.",
      "failure_scenario": "There is no functional failure. This is readability against POC-D7, for the reviewer's judgment.",
      "file": "scripts/lint_changed_files.py",
      "id": "F7",
      "kind": "advisory",
      "line": 65,
      "problem": "Naming (POC-D7): some names do not say what they do. `show` reads a file at a revision, so something like `read_at_revision` would say so. `VALUE` is the regex for the measured value in a limit message, so `LIMIT_VALUE` would be clearer. The test helpers `fn`, `method` and `module` build Python source text. The dataclasses `Change` and `Finding` have no docstrings. Every new file does have a purpose comment that says what it is for (both .py docstrings and the ruff_changed_files.toml header)."
    },
    {
      "evidence": "Lines 313-317. `added_or_worse` formats findings as `f\"{key[0]}:{sample.line}: ...\"`, which also contains the path.",
      "failure_scenario": "If a fixture were later edited so that it also triggered a shellcheck finding, a broken header check would no longer be noticed. Asserting on 'purpose' / 'first-line comment' text would prevent this.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F8",
      "kind": "advisory",
      "line": 317,
      "problem": "The negative header tests assert `code == 1 and path in out`. Every finding line includes the file path, so any other finding on the same file would satisfy the assertion, header or not. Today none of those fixtures triggers a ruff or shellcheck finding, so the assertion holds, but it is looser than checking the header message ('needs a first-line comment' or 'module docstring')."
    }
  ],
  "verdict": "no"
}
`````

</details>

### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| F1 | Fixed. Each Python header case now has its own file without a docstring: `services/other.py`, `services/_other.py` and `services/pkg2/__init__.py`. The test asserts the exact header message for that path. Exempting `__init__.py` makes it fail (checked). | `test_new_python_file_with_a_docstring_passes_and_without_fails` |
| F2 | Fixed. Each tool directive (`# -*- coding -*-`, `# yaml-language-server`, `# noqa`, `# type:`) now runs on a comment-header file type (TOML, YAML), and `# shellcheck` on a shell file. The Python coding-line case is its own test. Dropping `-\*-` from `TOOL_DIRECTIVE` makes a test fail (checked). | `test_new_file_without_a_purpose_comment_fails`, `test_new_python_file_with_only_a_coding_line_fails` |
| F3 | Fixed. A test runs the gate with ruff missing from PATH, and with a fake ruff that exits 2; both expect exit 2. Ignoring ruff's return code makes it fail (checked). | `test_missing_or_failing_tool_fails_the_run` |
| F4 | Fixed. The script docstring, its error message (and the test that asserts it) and the CI step name now say "the integration branch's ruleset". | `scripts/check_gate_consistency.py`, `tests/tools/test_gate_consistency.py`, `ci.yml` |
| F5 | Fixed. Files are read as bytes and decoded with replacement, so a binary file is skipped, not fatal. Tested with an added PNG-like file. | `read_at_revision`; `test_added_binary_file_is_skipped_without_an_error` |
| F6 | Fixed. In the merge-base test, the base now fixes a violation after the branch point in a file the change does not touch. Using the base tip instead of the merge-base makes the test fail (checked). | `test_base_that_moved_on_does_not_fail_files_the_change_did_not_touch` |
| F7 | Fixed. The renames are `show` → `read_at_revision`, `VALUE` → `LIMIT_VALUE`, and `fn`/`method`/`module` → `function_source`/`method_source`/`module_source`. `Change` and `Finding` now have docstrings. | lint script, test file |
| F8 | Fixed. The negative header tests assert the header message, not just the path. | header tests |

## Round 2 (focused recheck, medium effort)

Reviewed commit `89c9cbe`; attempt `slice_3/c1/r2/impl/1`: 29 seconds, 7 turns, 5 tool calls (all inside the copy, none denied), 3,098 output tokens, CLI cost estimate USD 0.33; afterwards the 5-hour window stood at 42% and the weekly window at 4%. Status completed,
verdict "yes".

### Task prompt (verbatim, SHA-256 `fbedd901c5ce0931796bfd94b4e3de6b8e4d19aee900b3072f2227094127ab34`)

`````text
This is review round 2 of the implementation review of slice 3 of the agentic-SDLC PoC (the changed-files lint gate): a focused recheck by the original reviewer. Your round-1 report and the author's answers are below; check each answer against the change (_review_inputs/change.diff now covers round 1's commit and the fixes). Under the approved rules, from round 2 a new finding counts only if it blocks, except simpler alternatives and decision concerns. Open files by their path from the copy root.

## Your round-1 report (verbatim JSON)

{
  "findings": [
    {
      "evidence": "Lines 281-288: `@pytest.mark.parametrize(\"path\", [\"services/new.py\", \"services/_private.py\", \"services/pkg/__init__.py\"])` ... `repo.change({path.replace(\".py\", \"_two.py\"): \"VALUE = 1\\n\"})`. The fail case for `__init__.py` therefore writes `__init___two.py`.",
      "failure_scenario": "A plausible honest regression is to exempt `__init__.py` from `_python_header`, as ruff's D104 conventions and empty package files encourage. That change would leave every test green. A later PR could then add a package `__init__.py` with no docstring and `make lint` would pass, contrary to POC-D7 and the AGENTS.md lint row. Fix: write the no-docstring case as an `__init__.py` in another package, for example `services/pkg2/__init__.py`.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F1",
      "kind": "blocking",
      "line": 286,
      "problem": "The 'Python header' row in the test plan says a new module, a private module and an `__init__.py` each fail without a docstring. The test builds the no-docstring file with `path.replace(\".py\", \"_two.py\")`, which turns `services/pkg/__init__.py` into `services/pkg/__init___two.py`. That is an ordinary module, not a package `__init__.py`. So the test never checks an `__init__.py` without a docstring, and that part of the row has no test (POC-D7, plan: 'including private modules and `__init__.py`')."
    },
    {
      "evidence": "Line 311: `(\"scripts/coding.py\", \"# -*- coding: utf-8 -*-\\nVALUE = 1\\n\")`. `header_problem` sends every `.py` path to `_python_header` (script line 237), and that file fails for the missing docstring whatever `TOOL_DIRECTIVE` contains.",
      "failure_scenario": "Dropping `-\\*-` (or `yaml-language-server`, `noqa`, `type:`) from `TOOL_DIRECTIVE` would leave all tests green. A new TOML, YAML or shell file whose only header is `# -*- mode: ... -*-` would then pass the purpose-comment check. Fix: run the coding-directive case on one of the comment-header types, for example `config/new.toml` containing `# -*- coding: utf-8 -*-\\nkey = 1\\n`.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F2",
      "kind": "blocking",
      "line": 311,
      "problem": "The 'Other headers' row covers shell, YAML, TOML, Dockerfile and Rego files. It must fail a file whose only first comment is a tool directive, and it names `# -*- coding -*-` as an example. The test checks the coding directive only on a `.py` file (`scripts/coding.py`). Python files go through `_python_header`, the docstring check, so the `-\\*-` alternative of `TOOL_DIRECTIVE` in `_comment_header` never runs. Of the planned directives, only `# shellcheck` is exercised on the comment-header path."
    },
    {
      "evidence": "`ruff_findings`: `if result.returncode not in (0, 1): raise LintError` followed by `json.loads(result.stdout or \"[]\")`. No test makes ruff or shellcheck exit with 2 or be absent from PATH. The author's local run, where shellcheck was missing, is the only evidence that the missing-tool path works.",
      "failure_scenario": "Suppose a later edit relaxes the return-code check. A ruff configuration error (exit 2, empty stdout) would then become `[]`, meaning zero findings, and the gate would pass. A cheap guard would be one test that runs the gate with PATH limited to `git` (or with a fake `ruff` that exits 2) and asserts exit code 2.",
      "file": "scripts/lint_changed_files.py",
      "id": "F3",
      "kind": "advisory",
      "line": 125,
      "problem": "No test shows that a tool error or a missing tool fails the run, although the AGENTS.md row claims 'a missing base or tool fails'. Question 1 asks about exactly this ('a tool error read as success'). If the `returncode not in (0, 1)` checks in `ruff_findings` and `shell_findings`, or the `shutil.which` checks, were removed, every test would still pass. The test plan's 'Fail closed' row only names a missing base, so this is advisory."
    },
    {
      "evidence": "check_gate_consistency.py:7 says 'the required status checks of the `main` ruleset'. Line 90 is `f\"CI job {j} is not a required check of the main ruleset\"`. ci.yml:188 is the step name 'Check that AGENTS.md CI gates, CI jobs and main's required checks agree'. The Makefile now reads ruleset 26764115 (poc/agentic-sdlc).",
      "failure_scenario": "Gate-consistency is expected to fail on this PR until the user carries out user action 2. When it does, it will print 'CI job lint is not a required check of the main ruleset'. That could lead the user to add `lint` to the `main`/`basic` ruleset, which the plan says would block every `main` PR.",
      "file": "scripts/check_gate_consistency.py",
      "id": "F4",
      "kind": "advisory",
      "line": 90,
      "problem": "The change points `RULESET_URL` at the PoC ruleset and rewrites the AGENTS.md gate-consistency row to 'the integration branch's ruleset'. Three places still say 'main': the script's docstring (line 7), its error message (line 90, 'is not a required check of the main ruleset') and the CI step name (ci.yml line 188, 'main's required checks'). They are now false."
    },
    {
      "evidence": "`show()` calls `subprocess.run([...], capture_output=True, text=True)`, and `file_findings` calls `show(\"HEAD\", change.path)` unconditionally on its first line. The repo has docs/archive/diagrams/*.png.",
      "failure_scenario": "A PR that adds a diagram PNG, or archives a document that contains one, fails `lint` with a traceback (a false red, not a false green). Skipping paths that are neither .py nor shell before reading them, or decoding with errors='replace', would avoid this.",
      "file": "scripts/lint_changed_files.py",
      "id": "F5",
      "kind": "advisory",
      "line": 205,
      "problem": "`file_findings` reads every changed file with `git show` and `text=True` before it checks the file type. A binary file that is added, modified or renamed (the repo tracks PNGs in docs/archive/diagrams/, and retiring a document with `git mv` creates a rename) raises an uncaught UnicodeDecodeError. The gate then crashes with a traceback instead of skipping the file."
    },
    {
      "evidence": "Lines 332-339: the base adds a new file containing `import json` after the branch point. With `git diff main HEAD`, that file is status D and `changed_files` drops it.",
      "failure_scenario": "Suppose `git merge-base` were dropped. When the base fixes a violation in a file the change did not touch, a local `make lint` would report the change branch's unchanged copy as new, and no test would catch this. A version of the test in which the base modifies an existing file to remove a violation would tell the two behaviours apart.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F6",
      "kind": "advisory",
      "line": 332,
      "problem": "The merge-base test would also pass if the gate diffed against the base tip instead of the merge-base. The file the base adds (`services/other.py`) would show up as a deletion, and deletions are skipped. So the test matches its row literally but does not show that the merge-base is used. In CI the PR merge ref makes the merge-base equal to the base tip anyway, so the difference only matters locally."
    },
    {
      "evidence": "Line 35: `VALUE = re.compile(r\"\\((\\d+) > \\d+\\)\")`. Line 65: `def show(rev, path)`. Test file: `def fn(name, ifs=0, ...)`.",
      "failure_scenario": "There is no functional failure. This is readability against POC-D7, for the reviewer's judgment.",
      "file": "scripts/lint_changed_files.py",
      "id": "F7",
      "kind": "advisory",
      "line": 65,
      "problem": "Naming (POC-D7): some names do not say what they do. `show` reads a file at a revision, so something like `read_at_revision` would say so. `VALUE` is the regex for the measured value in a limit message, so `LIMIT_VALUE` would be clearer. The test helpers `fn`, `method` and `module` build Python source text. The dataclasses `Change` and `Finding` have no docstrings. Every new file does have a purpose comment that says what it is for (both .py docstrings and the ruff_changed_files.toml header)."
    },
    {
      "evidence": "Lines 313-317. `added_or_worse` formats findings as `f\"{key[0]}:{sample.line}: ...\"`, which also contains the path.",
      "failure_scenario": "If a fixture were later edited so that it also triggered a shellcheck finding, a broken header check would no longer be noticed. Asserting on 'purpose' / 'first-line comment' text would prevent this.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F8",
      "kind": "advisory",
      "line": 317,
      "problem": "The negative header tests assert `code == 1 and path in out`. Every finding line includes the file path, so any other finding on the same file would satisfy the assertion, header or not. Today none of those fixtures triggers a ruff or shellcheck finding, so the assertion holds, but it is looser than checking the header message ('needs a first-line comment' or 'module docstring')."
    }
  ],
  "verdict": "no"
}

## The author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| F1 | Fixed. Each Python header case now has its own file without a docstring: `services/other.py`, `services/_other.py` and `services/pkg2/__init__.py`. The test asserts the exact header message for that path. Exempting `__init__.py` makes it fail (checked). | `test_new_python_file_with_a_docstring_passes_and_without_fails` |
| F2 | Fixed. Each tool directive (`# -*- coding -*-`, `# yaml-language-server`, `# noqa`, `# type:`) now runs on a comment-header file type (TOML, YAML), and `# shellcheck` on a shell file. The Python coding-line case is its own test. Dropping `-\*-` from `TOOL_DIRECTIVE` makes a test fail (checked). | `test_new_file_without_a_purpose_comment_fails`, `test_new_python_file_with_only_a_coding_line_fails` |
| F3 | Fixed. A test runs the gate with ruff missing from PATH, and with a fake ruff that exits 2; both expect exit 2. Ignoring ruff's return code makes it fail (checked). | `test_missing_or_failing_tool_fails_the_run` |
| F4 | Fixed. The script docstring, its error message (and the test that asserts it) and the CI step name now say "the integration branch's ruleset". | `scripts/check_gate_consistency.py`, `tests/tools/test_gate_consistency.py`, `ci.yml` |
| F5 | Fixed. Files are read as bytes and decoded with replacement, so a binary file is skipped, not fatal. Tested with an added PNG-like file. | `read_at_revision`; `test_added_binary_file_is_skipped_without_an_error` |
| F6 | Fixed. In the merge-base test, the base now fixes a violation after the branch point in a file the change does not touch. Using the base tip instead of the merge-base makes the test fail (checked). | `test_base_that_moved_on_does_not_fail_files_the_change_did_not_touch` |
| F7 | Fixed. The renames are `show` → `read_at_revision`, `VALUE` → `LIMIT_VALUE`, and `fn`/`method`/`module` → `function_source`/`method_source`/`module_source`. `Change` and `Finding` now have docstrings. | lint script, test file |
| F8 | Fixed. The negative header tests assert the header message, not just the path. | header tests |

Local: 376 tooling tests pass; the 6 shell cases still need shellcheck, which only CI has. `make lint` passes on the change.

## Questions to answer

1. For each finding, accept the answer or re-raise it with new evidence.
2. Did the fixes introduce a blocking problem?
`````

### Report (rendered from the released JSON, which follows it verbatim)

Verdict: **yes** (approvable within the threat model).

#### F1 (advisory) — `tests/tools/test_lint_changed_files.py:283`

- **Problem:** Accepted: fixed. The no-docstring case now writes a real package `__init__.py` (`services/pkg2/__init__.py`), next to `services/other.py` and `services/_other.py`.
- **Evidence:** Lines 281-290: the parametrize pairs are (good, bad) and include ("services/pkg/__init__.py", "services/pkg2/__init__.py"). The assertion is `f"{bad}: an added Python file needs a module docstring" in out`. `_python_header` (script line 249) has no exemption for `__init__.py`.
- **Failure scenario:** None remaining. If `__init__.py` were exempted, the pkg2 case would fail.

#### F2 (advisory) — `tests/tools/test_lint_changed_files.py:313`

- **Problem:** Accepted: fixed. Each alternative in TOOL_DIRECTIVE now runs on the comment-header path: `-*-`, `yaml-language-server`, `noqa` and `type:` on TOML/YAML files, and `shellcheck` on a shell file. The test checks the exact header message.
- **Evidence:** Lines 306-323 cover config/coding.toml, config/schema.yaml, config/noqa.toml, config/typed.toml and scripts/directive.sh, each asserting `"{path}: an added file needs a first-line comment"`. Each TOOL_DIRECTIVE alternative (script line 34) has a case.
- **Failure scenario:** None remaining. Dropping any of the alternatives would make its case fail.

#### F3 (advisory) — `tests/tools/test_lint_changed_files.py:381`

- **Problem:** Accepted: fixed for ruff. The gate now runs once with ruff absent from PATH and once with a fake ruff that exits 2, and both runs must exit 2. Shellcheck's missing-tool and error paths still have no test. That is a residual nit, not a blocker: the plan's fail-closed row names only a missing base.
- **Evidence:** Lines 367-386: `_tool_dir` builds a PATH with git and python3 only, plus an optional fake ruff. The test asserts `result.returncode == 2 and "ruff" in result.stderr`. If the `shutil.which` check were removed, a missing ruff would raise FileNotFoundError and exit 1. If the return-code check were removed, the fake ruff's empty stdout would be read as no findings and the run would exit 0. Either way the test fails.
- **Failure scenario:** A relaxed shellcheck return-code check would still go unnoticed. That needs a later edit and a shellcheck error at the same time, so it stays advisory.

#### F4 (advisory) — `scripts/check_gate_consistency.py:91`

- **Problem:** Accepted: fixed. The docstring, the error message and its test now say "the integration branch's ruleset". The CI step name no longer says "main's required checks".
- **Evidence:** check_gate_consistency.py:7 and :91, and test_gate_consistency.py:69, say "integration branch's ruleset". A grep of ci.yml for "main's required" finds nothing.
- **Failure scenario:** None remaining.

#### F5 (advisory) — `scripts/lint_changed_files.py:69`

- **Problem:** Accepted: fixed. `read_at_revision` reads the file as bytes and decodes it with errors='replace'. A binary file with a non-linted suffix then returns no findings, and the header check skips it.
- **Evidence:** Script lines 69-72 decode with `errors="replace"`. Lines 217-218 return [] for files that are neither .py nor shell. Test lines 333-339 add a 1 KiB binary docs/diagram.png and expect exit 0 with PASSED.
- **Failure scenario:** None remaining.

#### F6 (advisory) — `tests/tools/test_lint_changed_files.py:354`

- **Problem:** Accepted: fixed. After the branch point, the base fixes an F401 in `services/debt.py`, a file the change does not touch. If the gate diffed against the base tip, it would see debt.py as modified and report the F401 as new. Against the merge-base the file is unchanged.
- **Evidence:** Lines 354-364: the base adds debt.py with `import json`, the change branches off, and main then rewrites debt.py to `VALUE = 1`. The test expects exit 0. `lint()` diffs from `git merge-base` (script line 268).
- **Failure scenario:** None remaining.

#### F7 (advisory) — `scripts/lint_changed_files.py:69`

- **Problem:** Accepted: fixed. The names are now `read_at_revision`, `LIMIT_VALUE`, `function_source`, `method_source` and `module_source`, and `Change`, `Finding` and `FileContext` have docstrings.
- **Evidence:** Script lines 35, 43-59, 69 and 153-160. Test line 79 defines `function_source`.
- **Failure scenario:** None.

#### F8 (advisory) — `tests/tools/test_lint_changed_files.py:323`

- **Problem:** Accepted: fixed. The header tests now assert the exact header message for the path.
- **Evidence:** Lines 290, 323 and 330 assert the header message text, not just the path.
- **Failure scenario:** None remaining.


The review ended after round 2: every finding is fixed or accepted, and no blocking finding is open.
The residual nit in F3 (shellcheck's missing-tool and error paths have no test of their own) is
listed in the PR.

<details><summary>Released report JSON (verbatim, SHA-256 <code>062c31ecd01e7249ce4af77e22080f0cfc02c9bf30df0e27ff30eb2e13b978d1</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "Lines 281-290: the parametrize pairs are (good, bad) and include (\"services/pkg/__init__.py\", \"services/pkg2/__init__.py\"). The assertion is `f\"{bad}: an added Python file needs a module docstring\" in out`. `_python_header` (script line 249) has no exemption for `__init__.py`.",
      "failure_scenario": "None remaining. If `__init__.py` were exempted, the pkg2 case would fail.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F1",
      "kind": "advisory",
      "line": 283,
      "problem": "Accepted: fixed. The no-docstring case now writes a real package `__init__.py` (`services/pkg2/__init__.py`), next to `services/other.py` and `services/_other.py`."
    },
    {
      "evidence": "Lines 306-323 cover config/coding.toml, config/schema.yaml, config/noqa.toml, config/typed.toml and scripts/directive.sh, each asserting `\"{path}: an added file needs a first-line comment\"`. Each TOOL_DIRECTIVE alternative (script line 34) has a case.",
      "failure_scenario": "None remaining. Dropping any of the alternatives would make its case fail.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F2",
      "kind": "advisory",
      "line": 313,
      "problem": "Accepted: fixed. Each alternative in TOOL_DIRECTIVE now runs on the comment-header path: `-*-`, `yaml-language-server`, `noqa` and `type:` on TOML/YAML files, and `shellcheck` on a shell file. The test checks the exact header message."
    },
    {
      "evidence": "Lines 367-386: `_tool_dir` builds a PATH with git and python3 only, plus an optional fake ruff. The test asserts `result.returncode == 2 and \"ruff\" in result.stderr`. If the `shutil.which` check were removed, a missing ruff would raise FileNotFoundError and exit 1. If the return-code check were removed, the fake ruff's empty stdout would be read as no findings and the run would exit 0. Either way the test fails.",
      "failure_scenario": "A relaxed shellcheck return-code check would still go unnoticed. That needs a later edit and a shellcheck error at the same time, so it stays advisory.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F3",
      "kind": "advisory",
      "line": 381,
      "problem": "Accepted: fixed for ruff. The gate now runs once with ruff absent from PATH and once with a fake ruff that exits 2, and both runs must exit 2. Shellcheck's missing-tool and error paths still have no test. That is a residual nit, not a blocker: the plan's fail-closed row names only a missing base."
    },
    {
      "evidence": "check_gate_consistency.py:7 and :91, and test_gate_consistency.py:69, say \"integration branch's ruleset\". A grep of ci.yml for \"main's required\" finds nothing.",
      "failure_scenario": "None remaining.",
      "file": "scripts/check_gate_consistency.py",
      "id": "F4",
      "kind": "advisory",
      "line": 91,
      "problem": "Accepted: fixed. The docstring, the error message and its test now say \"the integration branch's ruleset\". The CI step name no longer says \"main's required checks\"."
    },
    {
      "evidence": "Script lines 69-72 decode with `errors=\"replace\"`. Lines 217-218 return [] for files that are neither .py nor shell. Test lines 333-339 add a 1 KiB binary docs/diagram.png and expect exit 0 with PASSED.",
      "failure_scenario": "None remaining.",
      "file": "scripts/lint_changed_files.py",
      "id": "F5",
      "kind": "advisory",
      "line": 69,
      "problem": "Accepted: fixed. `read_at_revision` reads the file as bytes and decodes it with errors='replace'. A binary file with a non-linted suffix then returns no findings, and the header check skips it."
    },
    {
      "evidence": "Lines 354-364: the base adds debt.py with `import json`, the change branches off, and main then rewrites debt.py to `VALUE = 1`. The test expects exit 0. `lint()` diffs from `git merge-base` (script line 268).",
      "failure_scenario": "None remaining.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F6",
      "kind": "advisory",
      "line": 354,
      "problem": "Accepted: fixed. After the branch point, the base fixes an F401 in `services/debt.py`, a file the change does not touch. If the gate diffed against the base tip, it would see debt.py as modified and report the F401 as new. Against the merge-base the file is unchanged."
    },
    {
      "evidence": "Script lines 35, 43-59, 69 and 153-160. Test line 79 defines `function_source`.",
      "failure_scenario": "None.",
      "file": "scripts/lint_changed_files.py",
      "id": "F7",
      "kind": "advisory",
      "line": 69,
      "problem": "Accepted: fixed. The names are now `read_at_revision`, `LIMIT_VALUE`, `function_source`, `method_source` and `module_source`, and `Change`, `Finding` and `FileContext` have docstrings."
    },
    {
      "evidence": "Lines 290, 323 and 330 assert the header message text, not just the path.",
      "failure_scenario": "None remaining.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "F8",
      "kind": "advisory",
      "line": 323,
      "problem": "Accepted: fixed. The header tests now assert the exact header message for the path."
    }
  ],
  "verdict": "yes"
}
`````

</details>

## Round 3 (focused review of the Markdown header check, medium effort)

After round 2 closed, the owner answered slice 1's question S1-C2 in PR #34 ("All the files"), so
the lint gate's header check was extended to Markdown. Reviewed commit `92cbd6c`; attempt
`slice_3/c1/r3/impl/1`: 59 seconds, 14 turns, 12 tool calls (all inside the copy,
none denied), 3,851 output tokens, CLI cost estimate USD 0.35; afterwards the 5-hour window
stood at 4% and the weekly window at 5%. Status completed, verdict "yes". Paths under review:
`scripts/lint_changed_files.py`, `tests/tools/test_lint_changed_files.py`, `AGENTS.md`.

### Task prompt (verbatim, SHA-256 `e2d54cfaad6932c0d9b81a3a26fbbdcaf7503d8828003b7c319cf5223dc751b2`)

`````text
This is review round 3 of the implementation review of slice 3 of the agentic-SDLC PoC (the changed-files lint gate), by the original reviewer: a focused review of one change made after round 2 closed with verdict "yes". Open files by their path from the copy root; Markdown links are relative to the file that contains them.

## The intent of this change

The owner answered a question of slice 1's PR (#34) on 2026-11-08: asked whether POC-D7 ("Every new file starts with a comment that says what the file is for") covers Markdown and other documents or only code and configuration, the owner wrote "All the files". Slice 1 now words coding rule 8 accordingly: Markdown starts with a `#` title followed by a paragraph that says what the document is for; only JSON, JSONL and binary files are exempt; formats the lint does not parse are left to a new review question. This slice's lint gate therefore also checks added Markdown files: a `#` title followed by a paragraph (a first non-empty line after the title that is not a heading). The plan's slice-3 list of checked types is widened by that decision. Slice 1's change is on its own branch and not part of this diff.

## What changed since round 2

scripts/lint_changed_files.py (`header_problem`, `_markdown_header`, the module docstring), tests/tools/test_lint_changed_files.py (`test_new_markdown_file_needs_a_title_and_a_purpose_paragraph`), the AGENTS.md "Changed-files lint" row and the implementation-log entry. Removing the Markdown branch from `header_problem` makes three of the new cases fail (checked).

## Questions to answer

1. Does the check do what the intent says, and do the tests show it can fail? Which wrong behaviour would still pass them?
2. Does the change contradict anything, or claim more than it does? Would any Markdown file added by slices 2 or 3 now fail the check (the gate runs on every PR's added files)?
3. Any other blocking problem?

Under the approved rules, a new finding counts only if it blocks, except simpler alternatives and decision concerns.
`````

### Report (rendered from the released JSON, which follows it verbatim)

Verdict: **yes** (approvable within the threat model).

#### R3-A1 (advisory) — `scripts/lint_changed_files.py:262`

- **Problem:** The Markdown check only requires that the second non-empty line does not start with `#`. Any non-heading line after the title counts as the purpose paragraph: a list item, a table row, a code fence, an HTML comment or a link-only line. So `# Notes` followed by ```` ``` ```` or `- item` passes. The tests cover a missing title, a heading straight after the title and a title on its own; they do not cover any of these non-paragraph cases.
- **Evidence:** `_markdown_header`: `lines[0].startswith("# ") and not lines[1].startswith("#")`. The parametrized cases at tests/tools/test_lint_changed_files.py:342-347 are title-and-paragraph, no-title, title-then-heading and title-only.
- **Failure scenario:** An agent adds `docs/x.md` that starts with `# X` and then a table or a code block, with no sentence saying what the document is for. The gate passes. This is an honest-mistake miss of coding rule 8, but the intent defines a paragraph only as "a first non-empty line after the title that is not a heading", so the code matches the approved wording and this is not a false green against the intent. Any judgment beyond that is left to review.

#### R3-A2 (advisory) — `AGENTS.md:253`

- **Problem:** The Changed-files lint row cites "coding rule 8" for the Markdown title-and-paragraph requirement. Coding rule 8 at this commit (and at the base) still says only "Every new file starts with a comment … file types without comments, such as JSON, are exempt". The Markdown wording comes from slice 1's separate branch. Until that branch merges, the gate enforces a reading of rule 8 that the rule text in this tree does not state.
- **Evidence:** The intent says slice 1's change is on its own branch and not part of this diff. The AGENTS.md coding rules section at base reads rule 8 without Markdown wording.
- **Failure scenario:** This branch merges before slice 1's rule-8 change. For a while the rulebook's rule 8 and the gate row describe Markdown differently. No false green results (the gate is stricter, not looser), so this is advisory: merge order, or one clause in the row.

#### R3-A3 (advisory) — `docs/slices/agentic-sdlc-poc/review_slice_3.md:0`

- **Problem:** This branch adds review_slice_3.md, so the new check will run on it in this PR's own lint job. The file is withheld from the review copy, so I could not confirm it passes. Every existing Markdown file in the copy outside docs/archive starts with `# ` (no front matter, no leading HTML comment). The sibling record review_slice_1.md starts with `# Review record …`, a blank line and then a paragraph, which passes. Slice 2's Markdown files are in the merge-base and are not added files for this PR.
- **Evidence:** A multiline grep for files whose first character is not `#` found only docs/archive/SECURITY_MODEL.md, which this PR does not add. A grep for files starting with `---` found none. The diff adds no other .md file.
- **Failure scenario:** If review_slice_3.md started with something other than a `# ` title and a paragraph, the PR's lint job would fail. That would be a visible red, not a false green, and it is easy to fix.

<details><summary>Released report JSON (verbatim, SHA-256 <code>abb1109b55eb2cbf10dc64c95eeb2e3e8a91721b3f7ab78ab80994c64c675ba2</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "`_markdown_header`: `lines[0].startswith(\"# \") and not lines[1].startswith(\"#\")`. The parametrized cases at tests/tools/test_lint_changed_files.py:342-347 are title-and-paragraph, no-title, title-then-heading and title-only.",
      "failure_scenario": "An agent adds `docs/x.md` that starts with `# X` and then a table or a code block, with no sentence saying what the document is for. The gate passes. This is an honest-mistake miss of coding rule 8, but the intent defines a paragraph only as \"a first non-empty line after the title that is not a heading\", so the code matches the approved wording and this is not a false green against the intent. Any judgment beyond that is left to review.",
      "file": "scripts/lint_changed_files.py",
      "id": "R3-A1",
      "kind": "advisory",
      "line": 262,
      "problem": "The Markdown check only requires that the second non-empty line does not start with `#`. Any non-heading line after the title counts as the purpose paragraph: a list item, a table row, a code fence, an HTML comment or a link-only line. So `# Notes` followed by ```` ``` ```` or `- item` passes. The tests cover a missing title, a heading straight after the title and a title on its own; they do not cover any of these non-paragraph cases."
    },
    {
      "evidence": "The intent says slice 1's change is on its own branch and not part of this diff. The AGENTS.md coding rules section at base reads rule 8 without Markdown wording.",
      "failure_scenario": "This branch merges before slice 1's rule-8 change. For a while the rulebook's rule 8 and the gate row describe Markdown differently. No false green results (the gate is stricter, not looser), so this is advisory: merge order, or one clause in the row.",
      "file": "AGENTS.md",
      "id": "R3-A2",
      "kind": "advisory",
      "line": 253,
      "problem": "The Changed-files lint row cites \"coding rule 8\" for the Markdown title-and-paragraph requirement. Coding rule 8 at this commit (and at the base) still says only \"Every new file starts with a comment \u2026 file types without comments, such as JSON, are exempt\". The Markdown wording comes from slice 1's separate branch. Until that branch merges, the gate enforces a reading of rule 8 that the rule text in this tree does not state."
    },
    {
      "evidence": "A multiline grep for files whose first character is not `#` found only docs/archive/SECURITY_MODEL.md, which this PR does not add. A grep for files starting with `---` found none. The diff adds no other .md file.",
      "failure_scenario": "If review_slice_3.md started with something other than a `# ` title and a paragraph, the PR's lint job would fail. That would be a visible red, not a false green, and it is easy to fix.",
      "file": "docs/slices/agentic-sdlc-poc/review_slice_3.md",
      "id": "R3-A3",
      "kind": "advisory",
      "line": 0,
      "problem": "This branch adds review_slice_3.md, so the new check will run on it in this PR's own lint job. The file is withheld from the review copy, so I could not confirm it passes. Every existing Markdown file in the copy outside docs/archive starts with `# ` (no front matter, no leading HTML comment). The sibling record review_slice_1.md starts with `# Review record \u2026`, a blank line and then a paragraph, which passes. Slice 2's Markdown files are in the merge-base and are not added files for this PR."
    }
  ],
  "verdict": "yes"
}
`````

</details>

### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| R3-A1 | **Fixed** after the round: a line that starts a heading, list, table, code block or HTML comment is not a purpose paragraph; four new test cases. Not rechecked: it follows the reviewer's description, and no blocking finding is open. | `NOT_A_PARAGRAPH`, `_markdown_header`; `test_new_markdown_file_needs_a_title_and_a_purpose_paragraph` |
| R3-A2 | **No change**: slices merge in order, so slice 1's rule-8 wording is on `poc/agentic-sdlc` before this slice's PR opens. | — |
| R3-A3 | **Confirmed**: `make lint` passes on this branch, `review_slice_3.md` included, and every file slices 1 to 3 add passes the header check. | — |

The review ended after round 3: no blocking finding is open.
