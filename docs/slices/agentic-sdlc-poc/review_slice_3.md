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

Round 3 closed with no blocking finding open; round 4 followed as an open-mandate review.

## Round 4 (open mandate, high effort)

The last round the rules allow without an extension. It applied DPL-010's lesson to slice 3 before its
PR opened: an open mandate, with the review record and the attempt log (withheld from the copy) and
the list of never-reviewed files as evidence. Reviewed commit `a654e89`, base `poc/agentic-sdlc`
at `5a5aba7` (after slices 1 and 2 merged); attempt `slice_3/c1/r4/impl/1`: 430 seconds, 28 turns,
26 tool calls (all inside the copy, none denied), 42,155 output tokens, CLI cost estimate USD
2.43; afterwards the 5-hour window stood at 22% and the weekly window at 7%. Status
completed, verdict "no".

<details><summary>Task prompt (verbatim, SHA-256 <code>51ada59ce74663ef5cc1734c631f9f05db6ac10b3bf192706baf49ea62c602b0</code>; it contains this record and the attempt log as they stood before this round)</summary>

````````text
## Your mandate

Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, untested, stale, overclaimed, unsafe or unclear, inside or outside the files listed under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and pointing that out is part of the task. For every earlier answer you rely on, open the code and test it concerns rather than trusting the answer.

## The change

Slice 3 of the agentic-SDLC PoC, "Changed-files lint", about to become a pull request into `poc/agentic-sdlc`, where slices 1 (rules) and 2 (review launcher and benchmark) are already merged. The approved plan is docs/slices/agentic-sdlc-poc/plan.md ("Slice 3 — Changed-files lint", POC-D7, POC-D8, "Checks this plan adds", the user actions). The test plan is docs/slices/agentic-sdlc-poc/test_plan.md ("Slice 3 — lint"). By the owner's answer in PR #34, coding rule 8 in AGENTS.md covers every file, and the gate also checks added Markdown files. _review_inputs/change.diff is the whole change against `poc/agentic-sdlc`. The reviewed commit is a654e89.

This is review round 4. Rounds 1 to 3 asked focused questions; their history is in the review record below. While reviewing slice 2, an open-mandate round found misses that four focused rounds had not (recorded as DPL-010 in docs/delivery_problem_log.md). The owner's principle: "each steps should think for themselfs and add anything that is missing, flag that is wrong and orchestrator narrow prompts should not steer the agents narrowly." This round applies it to slice 3 before its PR opens.

## Evidence

- Branch history: slice 3 was built on slice 2 before slice 2's rebase. After slice 2 merged, slice 3 was rebased onto `poc/agentic-sdlc`. `git range-diff` shows every code commit unchanged; two commits changed only where conflicts in status lines and the shared attempt log were resolved.
- Tests: `make tooling-test` locally gives 388 passed and 6 failed. The 6 are the shell cases of tests/tools/test_lint_changed_files.py, which need `shellcheck`; it is not installed on the author's machine. A CI run (workflow_dispatch, before the rebase) passed all 382 tooling tests, the shell cases included.
- `make lint BASE_REF=origin/poc/agentic-sdlc` passes on this branch.
- CI: `gate-consistency` will fail on the PR until the owner adds `lint` to the PoC ruleset's required checks (user action 2). That failure is expected.
- Coverage (`pytest --cov=scripts --cov-branch` over the lint and gate-consistency tests):
  scripts/check_gate_consistency.py          85     27     26      7    66%   32, 40->35, 50, 62, 74, 77-79, 81, 97-116, 120
  scripts/lint_changed_files.py             209    209     62      0     0%   16-310
  The 0% for scripts/lint_changed_files.py is not a measurement: the tests run the gate as a separate process, which the coverage tool does not follow. So nobody knows which lines of the gate run in any test.
- Files of this change that no review round had under review: docs/history/implementation_log.md, docs/slices/README.md, and docs/slices/agentic-sdlc-poc/review_slice_3.md and review_attempts.jsonl. The last two are withheld from every reviewer by the launcher and are given below.

## The review record docs/slices/agentic-sdlc-poc/review_slice_3.md (verbatim)

```````markdown
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
```````

## The attempt log docs/slices/agentic-sdlc-poc/review_attempts.jsonl (verbatim)

````text
{"attempt": "slice_2/c1/r1/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "21a85362cf516c12eb82dc5e2efcb6b35a659047", "count": 1, "diff_sha256": "d3becf476c023aac62bb2b95234aa56055f6152fca7185866344a15fccfa9a1c", "effort": "high", "event": "start", "extension": null, "full_prompt_sha256": "2bab8ce21c776b45276b739ff582f5702b07d3e01fe2ad9259100444ef34e317", "model": "claude-opus-5-5", "paths_sha256": {"scripts/run_independent_review.py": "56ab6682be5659c8cd4896adba1f76b2654712d692fdc37f2ef25f743dcdb68c", "scripts/run_review_benchmark.py": "42a801cc20cd7f17c2092b5434cd27823ee374d7fbf5cabe1b1762368b5c9818", "tests/review_benchmark/answer_key.yaml": "4ef6e22fc28bff4afb8e96dfc2eb0199ed107bc78336cd437abd391d35449425", "tests/review_benchmark/prompts/checklist.md": "fb1e1c97199ae06e45b3b2986d11901d0386ed65d2f12c6f0df2c411b2b9bf28", "tests/review_benchmark/prompts/short.md": "c2f2bbb75cebc72032a93f02e1a396661e58c59063f97c049e46efcba232bd25", "tests/tools/fakes/fake_claude.py": "3968416d52860a8e450ec2304785d5c2965ca5d10e1f44474b733e9f1c467356", "tests/tools/fakes/fake_codex.py": "ba801bf53a85cdb70c146288b2b1c4884f215baf04fc5e7792959fa38a532020", "tests/tools/test_run_independent_review.py": "15413db44fb7b529fc4bf35db3e5ddebb3e5542ccba39fcfd118033aca822ea7", "tests/tools/test_run_review_benchmark.py": "d586513a0d579a1cd87812f8b50365bf7d4246bb8e6af66d9427f2c83f8af756"}, "prompt_file": "task_r1.md", "prompt_sha256": "74835d84064fa14b40387fa352d153ab6d140ae5ca3578cf4ab48b105fc6b2d3", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r1_impl_1.json", "reset": null, "reviewer": "impl", "round": 1, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T21:58:53Z", "tree": "d44c4e36ee95c76469918730e3d2135f82f98973", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r1/impl/1", "cost_usd_estimate": 1.8260885999999998, "denied": [], "duration_ms": 359947, "ended_at": "2026-11-07T22:05:03Z", "event": "end", "outside_calls": 0, "paths_read": ["_review_inputs/change.diff", "docs/slices/agentic-sdlc-poc/plan.md", "docs/slices/agentic-sdlc-poc/test_plan.md", "scripts/run_independent_review.py", "scripts/run_review_benchmark.py", "tests/review_benchmark/answer_key.yaml", "tests/tools/test_run_independent_review.py", "tests/tools/test_run_review_benchmark.py"], "reason": "", "report_sha256": "c9c6d6830d424d78ea2709bf3b010fc1274eaf76df5d452a524720cd00a3e14b", "status": "completed", "tokens": {"cache_creation_input_tokens": 122580, "cache_read_input_tokens": 637003, "input_tokens": 22, "output_tokens": 35898}, "tool_calls": 13, "turns": 15, "utilization": {"five_hour": 0.17, "seven_day": 0.02, "status": "allowed"}, "verdict": "no"}
{"attempt": "slice_2/c1/r2/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "d4916ef3731b9f8d6cb2449b90805559dba46e48", "count": 1, "diff_sha256": "afcc26b6a4e87ba8f72dd96a5630be837d897105424bf6d7fcf70811354bb598", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "6aac6e107499a2863677de14b823cf3115c26ee60dd4979b2d2241672968bc5b", "model": "claude-opus-5-5", "paths_sha256": {"scripts/run_independent_review.py": "c9e95aba252bcb521a6f6bb4e574c0377153990bcdc0d98c53d05ec0824f1e73", "scripts/run_review_benchmark.py": "b85bc4133038b97e14b05bd5607828965e8125f5d5eaa5dbaf4c55e6f51a4b98", "tests/review_benchmark/answer_key.yaml": "51b57cfec277ba8835c82dd28b4ab4985466e87c1e7205f1bff57dfecf2da25d", "tests/tools/test_run_independent_review.py": "bffbb7e0b0ddba73344e04ab34314a180dacc5f79db85c713fad8ef9732b7a8b", "tests/tools/test_run_review_benchmark.py": "db4586a9d8819b6f2c5fe3b23763ab160f1987765bd9a1a91c59d9ceec61aa3c"}, "prompt_file": "task_r2.md", "prompt_sha256": "0bff6fe08d52b444bbc6740e055b5f27d718d7b27b004655383a6c8596f9038a", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r2_impl_1.json", "reset": null, "reviewer": "impl", "round": 2, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:10:34Z", "tree": "22ce75967497b19ce5bd294f1399f804bc144997", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r2/impl/1", "cost_usd_estimate": 0.3983336, "denied": [], "duration_ms": 48334, "ended_at": "2026-11-07T22:11:24Z", "event": "end", "outside_calls": 0, "paths_read": ["scripts/run_review_benchmark.py", "tests/tools/test_run_review_benchmark.py"], "reason": "", "report_sha256": "dbbebbaba4c9c9e1b8c12a91d20576547a445bf7a54d27173f89fc77b2a18623", "status": "completed", "tokens": {"cache_creation_input_tokens": 34523, "cache_read_input_tokens": 192268, "input_tokens": 14, "output_tokens": 4182}, "tool_calls": 6, "turns": 8, "utilization": {"five_hour": 0.2, "seven_day": 0.02, "status": "allowed"}, "verdict": "yes"}
{"attempt": "slice_2/c1/r3/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "642b840268554e3624d1abd23f82ea609c3b6f10", "count": 1, "diff_sha256": "c0819e5fabd5829aeca3911c5fc15a42930d923c97b4633fcb8f97bef55e4865", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "1e155fe0f638a8cfe8d9f45a48f0afa714880e3ac0a42fd21177c3e0b76c8216", "model": "claude-opus-5-5", "paths_sha256": {"AGENTS.md": "fa3b56de5131684eeb876990992dffc388930afd2f857aa20eb8edc49c2c1081", "docs/STATUS.md": "25d7b08fbac9a80bce62c2b27f5390ced6402b64e6376d1947f7275a1eb9d9d3", "docs/history/implementation_log.md": "933abcc98880884de37c4d2ad46fcaa606bd43b91a8f568ea3b74e0ac6586382", "docs/slices/agentic-sdlc-poc/benchmark_report.md": "1afbe9650be377c426fc2139aa40368018c211c9ada7985a4f1c18d5f7fb6315", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl": "13b1e9de449a5c35510b0679c1199d8c8dbc6a3ed84b42aff6c2304b443265ea"}, "prompt_file": "task_r3.md", "prompt_sha256": "de09babcf4119ba368724976b5dddb6f62dbd37473ccc6601ff3fe1c63f4a44a", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r3_impl_1.json", "reset": null, "reviewer": "impl", "round": 3, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:33:13Z", "tree": "6c57b36993155205c958e8825c24333c2f5410c1", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r3/impl/1", "cost_usd_estimate": 0.7176774000000001, "denied": [], "duration_ms": 62140, "ended_at": "2026-11-07T22:34:18Z", "event": "end", "outside_calls": 1, "paths_read": ["docs/slices/agentic-sdlc-poc/benchmark_report.md", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl", "tests/review_benchmark/answer_key.yaml"], "reason": "a call named a path outside the copy", "report_sha256": null, "status": "failed", "tokens": {"cache_creation_input_tokens": 61810, "cache_read_input_tokens": 472387, "input_tokens": 20, "output_tokens": 6432}, "tool_calls": 11, "turns": 13, "utilization": {"five_hour": 0.36, "seven_day": 0.04, "status": "allowed"}, "verdict": null}
{"attempt": "slice_2/c1/r3/impl/2", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "642b840268554e3624d1abd23f82ea609c3b6f10", "count": 1, "diff_sha256": "c0819e5fabd5829aeca3911c5fc15a42930d923c97b4633fcb8f97bef55e4865", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "171ca275b72e31658a2d120186f8443392b9100b0ba5ddb9f54f9de4c6516182", "model": "claude-opus-5-5", "paths_sha256": {"AGENTS.md": "fa3b56de5131684eeb876990992dffc388930afd2f857aa20eb8edc49c2c1081", "docs/STATUS.md": "25d7b08fbac9a80bce62c2b27f5390ced6402b64e6376d1947f7275a1eb9d9d3", "docs/history/implementation_log.md": "933abcc98880884de37c4d2ad46fcaa606bd43b91a8f568ea3b74e0ac6586382", "docs/slices/agentic-sdlc-poc/benchmark_report.md": "1afbe9650be377c426fc2139aa40368018c211c9ada7985a4f1c18d5f7fb6315", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl": "13b1e9de449a5c35510b0679c1199d8c8dbc6a3ed84b42aff6c2304b443265ea"}, "prompt_file": "task_r3b.md", "prompt_sha256": "07c8bad50c40bf3ed8e5610f409895d1330ee6b98894844ce105cba6f077bad5", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r3_impl_2.json", "reset": null, "reviewer": "impl", "round": 3, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:34:53Z", "tree": "6c57b36993155205c958e8825c24333c2f5410c1", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r3/impl/2", "cost_usd_estimate": 0.8448612000000001, "denied": [], "duration_ms": 95406, "ended_at": "2026-11-07T22:36:31Z", "event": "end", "outside_calls": 0, "paths_read": ["_review_inputs/change.diff", "docs/slices/agentic-sdlc-poc/benchmark_report.md", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl", "docs/slices/agentic-sdlc-poc/plan.md", "tests/review_benchmark/answer_key.yaml"], "reason": "", "report_sha256": "b46983b24b67780772c7742749bcc80eb4f23d3060a1c9e2062c1c00d342136f", "status": "completed", "tokens": {"cache_creation_input_tokens": 63623, "cache_read_input_tokens": 855066, "input_tokens": 36, "output_tokens": 8236}, "tool_calls": 18, "turns": 20, "utilization": {"five_hour": 0.38, "seven_day": 0.04, "status": "allowed"}, "verdict": "no"}
{"attempt": "slice_2/c1/r4/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "14810987aa11b24edbd36ded8b1a0ab747774cd3", "count": 1, "diff_sha256": "a265ddaf26a711f868e499db7d2fcbb52dbd01bc4ba134d4f6e833aa696e49d2", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "705d02142874a1bf9cd574ab4e227a457ae872b4531cbca719028c20f420b65e", "model": "claude-opus-5-5", "paths_sha256": {"docs/history/implementation_log.md": "c4c598d0002ddfe6c59507f13812ce8dd382821cc68491e15fba8a2664f79b7b", "docs/slices/agentic-sdlc-poc/benchmark_report.md": "f562799028c8a9b1681b9dbc55ea7131f790dd0c3795c88b48df7840ac703585", "scripts/run_review_benchmark.py": "065897fd9e8c1dc698c5e186e4d998924a66f2419c5332f13d30e8d81cfc69c3", "tests/tools/test_run_review_benchmark.py": "69204d9c50b863ef49e8c85ad110ff56509b0a2ff64215a42a3399f06e275ab8"}, "prompt_file": "task_r4.md", "prompt_sha256": "13288f0d20309acc673bbb82c3f8b678030438285a789193b70d09260bf2337f", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r4_impl_1.json", "reset": null, "reviewer": "impl", "round": 4, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:38:02Z", "tree": "85f2340ecf30eeb95bd1d96cdbe23efeddcc6fc1", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r4/impl/1", "cost_usd_estimate": 0.24109719999999998, "denied": [], "duration_ms": 16961, "ended_at": "2026-11-07T22:38:20Z", "event": "end", "outside_calls": 0, "paths_read": ["docs/slices/agentic-sdlc-poc/benchmark_report.md", "scripts/run_review_benchmark.py"], "reason": "", "report_sha256": "39da685c93491f9333649f24007b707c7a40664fd869897099542352b3da8ed2", "status": "completed", "tokens": {"cache_creation_input_tokens": 23599, "cache_read_input_tokens": 74266, "input_tokens": 8, "output_tokens": 1871}, "tool_calls": 6, "turns": 8, "utilization": {"five_hour": 0.38, "seven_day": 0.04, "status": "allowed"}, "verdict": "yes"}
{"attempt": "slice_2/c1/r5/impl/1", "base": "poc/agentic-sdlc", "base_commit": "c4f9ca21d7fbf724cbba6afddfd6666698edb3e2", "cli_version": "2.1.319 (Claude Code)", "commit": "568d7f1b59631be16f114b9127fa9251d343b463", "count": 1, "diff_sha256": "8ecd327a1980dcaba5e5140334bf5953a66eb9dbd95ba6dec9c098dc884eb13c", "effort": "high", "event": "start", "extension": "https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/pull/35#issuecomment-6723140659", "full_prompt_sha256": "be2407a50a32b8ffc626f4fbe0b9ebca2f064ccc0d0a87afe7f9b1fa9309a172", "model": "claude-opus-5-5", "paths_sha256": {"docs/slices/README.md": "e3bda12d1fee8a925a73b975a3bb8eae34341daf00d9746b028e93dac51eb58f", "docs/slices/agentic-sdlc-poc/benchmark_report.md": "f562799028c8a9b1681b9dbc55ea7131f790dd0c3795c88b48df7840ac703585", "scripts/run_independent_review.py": "be8e72d31c6232d3c0443cf8aacd1d441a9cc3d525f132b81a93a3b2005e211e", "scripts/run_review_benchmark.py": "065897fd9e8c1dc698c5e186e4d998924a66f2419c5332f13d30e8d81cfc69c3", "tests/review_benchmark/answer_key.yaml": "51b57cfec277ba8835c82dd28b4ab4985466e87c1e7205f1bff57dfecf2da25d", "tests/review_benchmark/plants/PD-3.patch": "de9b7b4a94aded66a88609b1635e9f23a23186307a3a5f74645eaa8fd55b24f0", "tests/tools/test_run_independent_review.py": "6b70d751479e29c3b1f7e0a7c1550dc3fb5a8ad7c5c94f8f5869db4319244de4", "tests/tools/test_run_review_benchmark.py": "69204d9c50b863ef49e8c85ad110ff56509b0a2ff64215a42a3399f06e275ab8"}, "prompt_file": "task_r5.md", "prompt_sha256": "b44e6e395d890fce1ee0b23532cd214c7ce7b45e35739db6e5ef3d16f5b6753a", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r5_impl_1.json", "reset": null, "reviewer": "impl", "round": 5, "round_reviewers": ["impl"], "rules_sha256": "543c77e450739e9458ede9c6904d72b90426e0ce482201bfa963fce221b94617", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-08T15:09:00Z", "tree": "b3bab57b6b79374f074900a595dc63569eb63658", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": "d37839a6b21a175fa79b74d0163064e3aa56b4a6a70b2ebfe66f70ead9a5f65d", "docs/slices/agentic-sdlc-poc/review_slice_2.md": "81e6b4eba265ad1f9b2c0e98a7fea387ea409b564723ae79df7cbe4289bafd1e"}}
{"attempt": "slice_2/c1/r5/impl/1", "cost_usd_estimate": 2.944719, "denied": [], "duration_ms": 443203, "ended_at": "2026-11-08T15:16:36Z", "event": "end", "outside_calls": 0, "paths_read": ["_review_inputs/change.diff", "docs/slices/agentic-sdlc-poc/plan.md", "scripts/run_independent_review.py", "scripts/run_review_benchmark.py", "tests/tools/test_run_independent_review.py", "tests/tools/test_run_review_benchmark.py"], "reason": "", "report_sha256": "079233112c49cb0b2cd72188773baf2bca2be88e18d4068e7fa4c3e5d97e2998", "status": "completed", "tokens": {"cache_creation_input_tokens": 202608, "cache_read_input_tokens": 2252835, "input_tokens": 32, "output_tokens": 43658}, "tool_calls": 21, "turns": 23, "utilization": {"five_hour": 0.11, "seven_day": 0.06, "status": "allowed"}, "verdict": "no"}
{"attempt": "slice_2/c1/r6/impl/1", "base": "poc/agentic-sdlc", "base_commit": "c4f9ca21d7fbf724cbba6afddfd6666698edb3e2", "cli_version": "2.1.319 (Claude Code)", "commit": "a58e93a6b19bd84784aea5129387371b4733dfe9", "count": 1, "diff_sha256": "2052e71123fbbd057936c991b07e900d611a7b5946ea0567a2a72f57379dacac", "effort": "high", "event": "start", "extension": "https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/pull/35#issuecomment-6723366537", "full_prompt_sha256": "a2921c1e0f7d4818966e44c9ab81557db503c1e8279424a4ab7bc8b648187091", "model": "claude-opus-5-5", "paths_sha256": {"docs/history/implementation_log.md": "d564d89fbe3cebaaaa55067014249837887c97db357de864a2bcaf1443114116", "scripts/run_independent_review.py": "5a1d039a86f7a67d4a38824a9f755de337bef73e51bba60524de112edfc4bc78", "scripts/run_review_benchmark.py": "d3bf08bbd289cab792824ac4a1b9981596a6136ec1915273f62d4feb2303ff31", "tests/tools/fakes/fake_claude.py": "f9872d8ef44ae661bcee93dde66eb4f4f82f8342569b53f59142b2c4b88aae06", "tests/tools/test_run_independent_review.py": "4808101b08c96bff18e5ccddcb2d5cc5d0e5d62ca6b31cb1698a91fc60f77c34"}, "prompt_file": "task_r6.md", "prompt_sha256": "7e777d7e7a91af32a46b12d8feffb393a35850be8df687854bdf66c922244de0", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r6_impl_1.json", "reset": null, "reviewer": "impl", "round": 6, "round_reviewers": ["impl"], "rules_sha256": "543c77e450739e9458ede9c6904d72b90426e0ce482201bfa963fce221b94617", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-08T15:29:49Z", "tree": "92748c1af13e6be557cfd6b2eb28d7e83071f446", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": "041cdc12a9d8646dfac98bbe6e7e0a714faa52eb0e97e2cad47e88de2a989350", "docs/slices/agentic-sdlc-poc/review_slice_2.md": "3c42e6ae198b500387972d819f0e53dfa4a81236903e6d5cd4a6db3df0d68d5e"}}
{"attempt": "slice_2/c1/r6/impl/1", "cost_usd_estimate": 2.0372932, "denied": [], "duration_ms": 229615, "ended_at": "2026-11-08T15:33:45Z", "event": "end", "other_tools": [], "outside": [], "outside_calls": 0, "paths_read": ["AGENTS.md", "_review_inputs/change.diff", "docs/history/implementation_log.md", "scripts/run_independent_review.py", "scripts/run_review_benchmark.py", "tests/tools/fakes/fake_claude.py", "tests/tools/test_run_independent_review.py"], "reason": "", "report_sha256": "150d867ee939753b8b581749ab1600c0d8933db6471d3d12b7d79ea7cd563195", "status": "completed", "tokens": {"cache_creation_input_tokens": 152338, "cache_read_input_tokens": 2214266, "input_tokens": 34, "output_tokens": 18780}, "tool_calls": 18, "turns": 20, "utilization": {"five_hour": 0.16, "seven_day": 0.06, "status": "allowed"}, "verdict": "yes"}
{"attempt": "slice_3/c1/r1/impl/1", "base": "poc/slice-2-review-launcher", "base_commit": "6512f96812794dc677ef6609a6f0474ebe6e6d19", "cli_version": "2.1.319 (Claude Code)", "commit": "c136da059085d1d2806e6bf81574a61761b80bbe", "count": 1, "diff_sha256": "a0c601087806635a56da0652a220f76ed029aec88fdf6139413f4b0fa3cccea8", "effort": "high", "event": "start", "extension": null, "full_prompt_sha256": "8ab340cd99d7d196868f8505b49f5710a6c0b48c16d3fb1881b7e530fc6b1325", "model": "claude-opus-5-5", "paths_sha256": {".github/workflows/ci.yml": "15393261425542e04a17f7450f5b1f1a5830fb56176baaa00908f4bd90a08429", "AGENTS.md": "20bf41554f5030a927120924ef5be6b834574a56a9a6b828422697f01cd983d6", "Makefile": "b8c15f3b06936e4917c0e40f55168abb53fe16d0bcf28074423bac0e67d5905d", "docs/STATUS.md": "405316e78331eaeb1302d57033680d205025fa1fc4372306e5e738109b756f8e", "requirements-dev.txt": "12431d8a0edcfbf1dddb95d39cadd0a6b8badccafbfae667e83eb61adb856442", "ruff_changed_files.toml": "dd958783a7a72f77fddd2f09610efef99fa75be81f9d05170d495f4119561c91", "scripts/lint_changed_files.py": "77be51c83a3a0ad6ae998c73a607f0e66225760a0501d2dc91792552fc878daa", "tests/tools/test_gate_consistency.py": "463e4bb1e38e0ff5eeec487611242cda4cdd5062f3f3958752910aa5f90f9086", "tests/tools/test_lint_changed_files.py": "511d35f04bffdd84b1f38f5d3196dce053564ab5cd1beca1af39efdf73b72e8b"}, "prompt_file": "task_r1.md", "prompt_sha256": "e8b454df05588f759b5e5c6140c38c442a63b8ac2f66db0bfe54042b1b383de2", "report_path": "artifacts/reviews/slice_3/slice_3_c1_r1_impl_1.json", "reset": null, "reviewer": "impl", "round": 1, "round_reviewers": ["impl"], "rules_sha256": "1c63cf3578aab24234ade05bf07701bf7773c5efba6b80ce4c6e8e7599aae5d4", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:42:01Z", "tree": "d17e089a680ac3f002ddd4e40d48c49b28c9afeb", "unit": "slice_3", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": "d37839a6b21a175fa79b74d0163064e3aa56b4a6a70b2ebfe66f70ead9a5f65d", "docs/slices/agentic-sdlc-poc/review_slice_3.md": null}}
{"attempt": "slice_3/c1/r1/impl/1", "cost_usd_estimate": 1.240812, "denied": [], "duration_ms": 246788, "ended_at": "2026-11-07T22:46:14Z", "event": "end", "outside_calls": 0, "paths_read": [".github/workflows/ci.yml", "_review_inputs/change.diff", "docs/slices/agentic-sdlc-poc/plan.md", "docs/slices/agentic-sdlc-poc/test_plan.md", "scripts/check_gate_consistency.py", "varambu"], "reason": "", "report_sha256": "7a62ad69717ad31b880648b3eacc2cb7727949414a9ca95e981c950227ed85a8", "status": "completed", "tokens": {"cache_creation_input_tokens": 78071, "cache_read_input_tokens": 641040, "input_tokens": 24, "output_tokens": 24397}, "tool_calls": 14, "turns": 16, "utilization": {"five_hour": 0.41, "seven_day": 0.04, "status": "allowed"}, "verdict": "no"}
{"attempt": "slice_3/c1/r2/impl/1", "base": "poc/slice-2-review-launcher", "base_commit": "6512f96812794dc677ef6609a6f0474ebe6e6d19", "cli_version": "2.1.319 (Claude Code)", "commit": "89c9cbe9c39d6e9d1ae5c06fb311159e32a79a45", "count": 1, "diff_sha256": "4d5d43f6a72079065b323cc2fb469cf085187ad78a94b51761ed9d5e2a91edbb", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "79a3d7decc1936e2b67b544ef199b1e296de54f72dafb5a44d5fede7b8794754", "model": "claude-opus-5-5", "paths_sha256": {"scripts/check_gate_consistency.py": "6ad158d4053dcfb5d3ad72d115fbe5d012c2c68115cd4354ee928b90538f3b3a", "scripts/lint_changed_files.py": "617c8fd09321d8932180b152b2da0c25b9395af85448df4e1b3d42456b049f72", "tests/tools/test_gate_consistency.py": "745c835909be29442cfa94a70db0d1cdd18be5a83e16e719e4502a876d939948", "tests/tools/test_lint_changed_files.py": "28e7cbb3a5a0b831997be5e751206374dbc3c2e042296d785b86da716853ed9c"}, "prompt_file": "task_r2.md", "prompt_sha256": "fbedd901c5ce0931796bfd94b4e3de6b8e4d19aee900b3072f2227094127ab34", "report_path": "artifacts/reviews/slice_3/slice_3_c1_r2_impl_1.json", "reset": null, "reviewer": "impl", "round": 2, "round_reviewers": ["impl"], "rules_sha256": "1c63cf3578aab24234ade05bf07701bf7773c5efba6b80ce4c6e8e7599aae5d4", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:48:22Z", "tree": "891db3215c6d2dc50ba5830b440b2acb98a8ffba", "unit": "slice_3", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": "d37839a6b21a175fa79b74d0163064e3aa56b4a6a70b2ebfe66f70ead9a5f65d", "docs/slices/agentic-sdlc-poc/review_slice_3.md": null}}
{"attempt": "slice_3/c1/r2/impl/1", "cost_usd_estimate": 0.3302862, "denied": [], "duration_ms": 29266, "ended_at": "2026-11-07T22:48:53Z", "event": "end", "outside_calls": 0, "paths_read": ["scripts/lint_changed_files.py", "tests/tools/test_lint_changed_files.py"], "reason": "", "report_sha256": "062c31ecd01e7249ce4af77e22080f0cfc02c9bf30df0e27ff30eb2e13b978d1", "status": "completed", "tokens": {"cache_creation_input_tokens": 31223, "cache_read_input_tokens": 92551, "input_tokens": 8, "output_tokens": 3098}, "tool_calls": 5, "turns": 7, "utilization": {"five_hour": 0.42, "seven_day": 0.04, "status": "allowed"}, "verdict": "yes"}
{"attempt": "slice_3/c1/r3/impl/1", "base": "poc/slice-2-review-launcher", "base_commit": "6512f96812794dc677ef6609a6f0474ebe6e6d19", "cli_version": "2.1.319 (Claude Code)", "commit": "92cbd6cb7fda09e93a520966a237462dd7406c56", "count": 1, "diff_sha256": "bc3e66736e6b068024b4af4a27f4305faf6305aa4a58f21574be6eeba5a3560b", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "e5d8b270aaca876682a9b813f001285a9d436aa6b67afa2cc1830b467695cdd7", "model": "claude-opus-5-5", "paths_sha256": {"AGENTS.md": "9469ab0942723101eb8c4ac4d2c07f870a68d53f594475cad5ac7c1074cb5913", "scripts/lint_changed_files.py": "9b060f12057a67bb16a969938632b46da7bdd152dd3f1b030d24ab86676fc23c", "tests/tools/test_lint_changed_files.py": "26aa7b4b023c88683eec26777366f6585bae488dd391bfee7bf08383a657a321"}, "prompt_file": "task_r3.md", "prompt_sha256": "e2d54cfaad6932c0d9b81a3a26fbbdcaf7503d8828003b7c319cf5223dc751b2", "report_path": "artifacts/reviews/slice_3/slice_3_c1_r3_impl_1.json", "reset": null, "reviewer": "impl", "round": 3, "round_reviewers": ["impl"], "rules_sha256": "1c63cf3578aab24234ade05bf07701bf7773c5efba6b80ce4c6e8e7599aae5d4", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-08T11:52:13Z", "tree": "c40b978e2f3de67187deec7220e39b29944a82a6", "unit": "slice_3", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": "3cb75517b0c21036cdcc82fea6489c2c3d5bc5e25e071dc7c4b82354a73d758d", "docs/slices/agentic-sdlc-poc/review_slice_3.md": "323c4ffdf11d2ff668c0c4c2dfa750f9a7d81b8d37c507dc91c068a00b795b12"}}
{"attempt": "slice_3/c1/r3/impl/1", "cost_usd_estimate": 0.35386199999999995, "denied": [], "duration_ms": 58517, "ended_at": "2026-11-08T11:53:15Z", "event": "end", "outside_calls": 0, "paths_read": ["_review_inputs/change.diff", "scripts/lint_changed_files.py", "tests/tools/test_lint_changed_files.py"], "reason": "", "report_sha256": "abb1109b55eb2cbf10dc64c95eeb2e3e8a91721b3f7ab78ab80994c64c675ba2", "status": "completed", "tokens": {"cache_creation_input_tokens": 28536, "cache_read_input_tokens": 242330, "input_tokens": 22, "output_tokens": 3851}, "tool_calls": 12, "turns": 14, "utilization": {"five_hour": 0.04, "seven_day": 0.05, "status": "allowed"}, "verdict": "yes"}
````

## Minimum questions

1. Can the gate pass where it should fail, for a change an honest agent might make? Think of file types, renames, deletions, merges, generated or vendored files, configuration edits, `noqa` forms and tool failures.
2. Which behaviour of the gate has no test, whatever the test plan says? Since coverage cannot be measured, judge it from the code and the tests.
3. Which claim in the change (AGENTS.md row, STATUS, implementation log, review record, the CI job) is false, unsupported or overstated?
4. Does the change break or weaken anything that already worked: CI, gate-consistency, `ruff check` on the tree, local runs, the `main` branch's later merge?
5. What did rounds 1 to 3 miss, and why?

For each finding, say whether it should be fixed before the owner merges, and why.
````````

</details>

### Report (rendered from the released JSON, which follows it verbatim)

Verdict: **no** (approvable within the threat model).

#### R4-B1 (blocking) — `tests/tools/test_lint_changed_files.py:264`

- **Problem:** No test runs the gate on a modified or renamed shell file. POC-D8 says the limits apply to new and changed files, and that a change fails only on violations it adds or worsens. The plan's slice-3 text says shellcheck runs "on the merge-base version and on the new version" of every file the change adds, modifies or renames. Every shell test adds a new file: a good script, a bad `.sh`, a bad extensionless script, and the header cases. So the shell half of the comparison (line 217: `old = shell_findings(change.path, old_text)`) never runs with a real old version, and nothing shows that existing shell findings stay or that a worsened file fails. Coverage cannot show this either, because the gate runs in a child process.
- **Evidence:** scripts/lint_changed_files.py:216-218 compute old and new shellcheck findings for any changed shell file. Every shell test in tests/tools/test_lint_changed_files.py (test_new_script_that_passes_shellcheck_passes, test_new_script_with_a_shellcheck_finding_fails, and the scripts/new.sh and scripts/directive.sh header cases) starts from a base holding only `README.md` and adds the script. The test-plan row "Shell" also lists only new scripts. The repo's most-edited shell file is `scripts/rogue_node_tests.sh`, and every E2E-adding PR modifies it.
- **Failure scenario:** An honest refactor of `file_findings` passes the new text as the old version, or shellchecks only added scripts to avoid existing debt in `rogue_node_tests.sh`. Every test stays green. From then on, a PR that adds an unquoted `$var` (SC2086) to the E2E harness passes `make lint`, although slice 3's success criterion is that "a PR into the PoC branch fails CI when it adds or worsens a violation in a file it touches". The opposite bug, where the old findings are empty, would make the first harness PR fail. Fix before merge with two cheap tests: a base with a shell script that already has an SC2086 line, a change that edits another line (passes), and a change that adds a second unquoted expansion (fails).

#### R4-B2 (blocking) — `docs/history/implementation_log.md:28`

- **Problem:** The slice-3 close-out records contradict the review record and the current tree. The implementation log says "Review: two rounds through the launcher ... round 2 accepted every answer". review_slice_3.md has a third round, which reviewed the Markdown header check, and an R3-A1 fix applied after that round and "not rechecked". This review is round 4. The log and STATUS also give tooling-test counts from round 2: "376 pytest pass" locally and "all 382 ... in CI ... on `a09ab0d`". At the reviewed commit the local run is 388 passed and 6 failed (394 tests). The only CI run that included the shell cases was on `a09ab0d`, before the Markdown check and the R3-A1 tests existed. So the tooling suite at this commit has never passed in full anywhere, while the records suggest it has.
- **Evidence:** implementation_log.md:28-32 ("two rounds") and :34-38 (376 / 382). STATUS.md:47: "376 pytest pass locally, and all 382 (the 6 shell cases need `shellcheck`) in CI's tooling-test job on `a09ab0d`". The review record has Round 3 (commit 92cbd6c) and the R3-A1 answer "Fixed after the round ... Not rechecked". The prompt's evidence: 388 passed, 6 failed locally. 376+6=382 is the round-2 count. The implementation log was edited after round 3 (it describes the Markdown check), but its review and validation lines were not.
- **Failure scenario:** The owner merges on the strength of the log and STATUS: two clean review rounds and a fully passing CI tooling run. In fact a third round changed the gate, an unrechecked fix followed, and the suite at the merged commit has not run in full. This is the stale-evidence class the delivery threat model names. Fix before merge: give the rounds and their outcome (including this round 4), and replace the counts with the PR's own CI tooling-test result for the reviewed commit, or say it is pending.

#### R4-A1 (advisory) — `docs/history/implementation_log.md:33`

- **Problem:** Step 4 of the slice workflow requires `make qa-quality` (qa-trace, docs-check, test-lint, qa-deploy). The slice-3 entry does not report it as run, and does not list it under "what was not run and why". STATUS has no qa-quality row for slice 3 either. The change adds a Markdown review record, edits AGENTS.md's gates table and adds a slice-index status, all of which docs-check and gate-consistency read.
- **Evidence:** implementation_log.md:33-42 lists make lint, tooling-test, E2E, qa-deploy and qa-evidence only. AGENTS.md step 4: "run `make qa-quality` (includes `qa-trace`, `docs-check`, `test-lint` and `qa-deploy`) ... add a dated entry ... (what changed, validation results, what was not run and why)".
- **Failure scenario:** A broken link or anchor in the new review record or the changed docs, or a qa-trace gap, shows up only in PR CI, after the close-out already claims validation. If it was run, record it. If not, say so. Fix before merge: it is one line.

#### R4-A2 (advisory) — `scripts/lint_changed_files.py:244`

- **Problem:** The AGENTS.md row and the log say "every added Python ... file starts with a purpose comment" and is linted. Python is recognised only by the `.py` suffix. An extensionless Python script (`#!/usr/bin/env python3`) or a `.pyi` file gets neither ruff nor the docstring check. Only shell has shebang detection. Dockerfile parser directives (`# syntax=...`, `# escape=...`, `# check=...`) count as purpose comments, because TOOL_DIRECTIVE does not list them. `Containerfile`, `*.Dockerfile` and `.bash` files without a shebang are not recognised at all.
- **Evidence:** header_problem: `if path.endswith(".py")`, then the suffix set and Dockerfile names, then `is_shell`. file_findings:219 returns [] for anything not `.py` that is not shell. TOOL_DIRECTIVE (line 34) has no Docker directives. A grep finds no extensionless Python script and no Docker parser directive in the repo today.
- **Failure scenario:** An agent adds an extensionless Python CLI like the bash `varambu`, with a 15-branch `main` and no docstring, and `make lint` passes. Or it adds a Dockerfile whose first line is `# syntax=docker/dockerfile:1`, and the header check passes. Either narrow the row's wording or extend detection (a python shebang, Docker directives). Not needed for this merge, since no such file exists.

#### R4-A3 (advisory) — `scripts/lint_changed_files.py:152`

- **Problem:** `sorted(unique)` sorts (code, row, message) tuples. As I understand ruff ≥ 0.5, it reports syntax errors with `code: null` while still reporting other rules on the same file. If so, a changed `.py` file with a syntax error plus any coded finding makes `sorted` raise `TypeError` (None vs str). The gate then dies with a traceback and exit code 1, the same code as "findings". This is a red, not a green, but the output is unclear and indistinguishable from a lint failure. No test covers a file that does not parse.
- **Evidence:** Line 151: `unique = {(r["code"], r["location"]["row"], r["message"]) for r in raw}`, then `sorted(unique)`. LintError (exit 2) is the only handled failure; any other exception exits 1 through Python's default handler.
- **Failure scenario:** An agent pushes a half-edited module. The `lint` job fails with a Python traceback instead of a finding line, and the agent may read it as a gate bug. Sorting with `key=lambda t: (t[0] or '', t[1], t[2])` and a syntax-error test would settle this. Not required for this merge.

#### R4-A4 (advisory) — `scripts/lint_changed_files.py:100`

- **Problem:** Some functions share a key, and their findings are compared only by count and max value, so one can mask another. `function_spans` descends only through def and class nodes. Functions defined inside `if`, `try`, `with` or `for` blocks inside a function therefore get the outer function's key. Two functions with the same qualified name (a property getter and setter, `@overload`, conditional redefinitions) also share a key. When one of them is the over-limit function with the higher value, the other can be made worse unnoticed.
- **Evidence:** visit() recurses only into FunctionDef/AsyncFunctionDef/ClassDef children. In added_or_worse, `worse = len(values) > len(before[key]) or max(values) > max(before[key], default=0)`. Before: outer C901=13 and nested C901=11, i.e. [13, 11]. After the nested one goes to 12: [13, 12]. Same count, same max, so the change passes. A grep finds no such nested defs in services/ or scripts/ today.
- **Failure scenario:** Rare today: a later change raises a nested helper or a property setter above its earlier complexity, and the gate stays green. Comparing sorted value lists element-wise, or adding the def line text to the key for unindexed functions, would close it. Advisory only.

#### R4-A5 (advisory) — `scripts/lint_changed_files.py:279`

- **Problem:** `make lint` diffs the merge-base against the committed `HEAD` and reads files with `git show HEAD:`. Uncommitted and staged edits are invisible, and the run still prints PASSED. The step-4 workflow has agents run gates locally before the PR.
- **Evidence:** changed_files: `git diff --name-status -M -z <merge_base> HEAD`. file_findings: `read_at_revision("HEAD", ...)`. The output does not say that only commits are checked.
- **Failure scenario:** An agent runs `make lint` on its working tree before committing, sees PASSED and records it in the implementation log. The over-limit function it just wrote was never linted. CI catches it on the PR, so this is only a false local green. Print a note, or fail, when `git status --porcelain` is not empty.

#### R4-A6 (advisory) — `AGENTS.md:265`

- **Problem:** AGENTS.md still lists "`ruff check services scripts` ... stays clean on the whole tree" under "Standards that are **not** gated yet". This change makes it gated: test_plain_ruff_check_keeps_the_default_rules_and_passes_on_the_tree runs exactly that command in `make tooling-test`, a required CI job. The test is also named for "keeps the default rules", but what it asserts is that the tree is clean.
- **Evidence:** tests/tools/test_lint_changed_files.py, the last test: `subprocess.run(["ruff", "check", "--no-cache", "services", "scripts"], cwd=ROOT ...)`; `assert result.returncode == 0`. The AGENTS.md QA tooling tests row: "`tests/tools/` (pytest) and `tests/shell/` pass".
- **Failure scenario:** A PR that adds a ruff default-rule violation in a file the lint job does not see (a deleted-then-restored path, or a file outside the diff after a ruff upgrade) fails tooling-test. The rulebook tells the author that check is not gated. That is a confusing red and a small rule/repo disagreement. Move the sentence to the tooling-test row, or say there that the test enforces it.

#### R4-A7 (advisory) — `tests/tools/test_lint_changed_files.py:0`

- **Problem:** Other gate behaviours that no test exercises, whatever the test plan says: shellcheck missing or exiting with an error (the residual from F3); an existing module-level, line-text-keyed Python violation staying when its row moves; `noqa` on N, F841 and the PLR rules, and the file-level `# ruff: noqa` form (only `# noqa: C901` and `# noqa: F401` are tested); `.yml` (only `.yaml`) and `Dockerfile.*` headers; an extensionless shell script without a purpose comment; status T (type change). In test_renamed_file_..._gaining_one_fails the second half would also pass if Git no longer detected the rename (status A makes every finding new), so only its first half proves rename matching.
- **Evidence:** Read the test file against `lint_changed_files.py`. The prompt's coverage table shows 0% for the gate, because it runs as a child process. Running the gate in-process for a few tests (`lint_changed_files.main([...])` with `cwd` set via monkeypatch) would give a real coverage measurement.
- **Failure scenario:** A regression in any of these paths, such as dropping `--ignore-noqa` for N or file-level noqa honoured on C901, stays green. Most are low risk. The shellcheck fail-closed path and an in-process coverage run are the cheapest to add.

#### R4-S1 (simpler_alternative) — `scripts/lint_changed_files.py:83`

- **Problem:** The copy branch (status C, `old_path=None`) and the `status in "AC"` header condition are dead code. `git diff -M` detects renames but not copies (copies need `-C`), so a copied file arrives as status A anyway.
- **Evidence:** changed_files calls `git("diff", "--name-status", "-M", "-z", merge_base, "HEAD")`. Without `-C`/`--find-copies`, Git never emits C.
- **Failure scenario:** There is no functional failure. A reader may think copies are detected and handled specially. Dropping the C handling, or documenting why it stays, removes a path no test can reach.

#### R4-A8 (advisory) — `Makefile:18`

- **Problem:** Restoring `RULESET_URL` to the `main` ruleset when the PoC merges into `main` is recorded only in a Makefile comment. No issue or plan item tracks it. The same merge must also decide whether `lint` becomes a required check on `main`, which the plan says would block every `main` PR today.
- **Evidence:** Makefile comment: "Set it back to the main ruleset (26054924) when the PoC merges into main." STATUS and the slice index say nothing about it. AGENTS step 4: "open a GitHub issue for work found but not done".
- **Failure scenario:** When the PoC is merged into `main` (slice 8 or later), gate-consistency on `main` keeps reading the PoC ruleset and either passes against the wrong branch's checks or fails confusingly. Add one line to the handoff, or open an issue, before merge.

<details><summary>Released report JSON (verbatim, SHA-256 <code>eb9d7627f3f49b4e2480511957410b47364fd23d0eec8a43587a35a268e94581</code>)</summary>

````````json
{
  "findings": [
    {
      "evidence": "scripts/lint_changed_files.py:216-218 compute old and new shellcheck findings for any changed shell file. Every shell test in tests/tools/test_lint_changed_files.py (test_new_script_that_passes_shellcheck_passes, test_new_script_with_a_shellcheck_finding_fails, and the scripts/new.sh and scripts/directive.sh header cases) starts from a base holding only `README.md` and adds the script. The test-plan row \"Shell\" also lists only new scripts. The repo's most-edited shell file is `scripts/rogue_node_tests.sh`, and every E2E-adding PR modifies it.",
      "failure_scenario": "An honest refactor of `file_findings` passes the new text as the old version, or shellchecks only added scripts to avoid existing debt in `rogue_node_tests.sh`. Every test stays green. From then on, a PR that adds an unquoted `$var` (SC2086) to the E2E harness passes `make lint`, although slice 3's success criterion is that \"a PR into the PoC branch fails CI when it adds or worsens a violation in a file it touches\". The opposite bug, where the old findings are empty, would make the first harness PR fail. Fix before merge with two cheap tests: a base with a shell script that already has an SC2086 line, a change that edits another line (passes), and a change that adds a second unquoted expansion (fails).",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "R4-B1",
      "kind": "blocking",
      "line": 264,
      "problem": "No test runs the gate on a modified or renamed shell file. POC-D8 says the limits apply to new and changed files, and that a change fails only on violations it adds or worsens. The plan's slice-3 text says shellcheck runs \"on the merge-base version and on the new version\" of every file the change adds, modifies or renames. Every shell test adds a new file: a good script, a bad `.sh`, a bad extensionless script, and the header cases. So the shell half of the comparison (line 217: `old = shell_findings(change.path, old_text)`) never runs with a real old version, and nothing shows that existing shell findings stay or that a worsened file fails. Coverage cannot show this either, because the gate runs in a child process."
    },
    {
      "evidence": "implementation_log.md:28-32 (\"two rounds\") and :34-38 (376 / 382). STATUS.md:47: \"376 pytest pass locally, and all 382 (the 6 shell cases need `shellcheck`) in CI's tooling-test job on `a09ab0d`\". The review record has Round 3 (commit 92cbd6c) and the R3-A1 answer \"Fixed after the round ... Not rechecked\". The prompt's evidence: 388 passed, 6 failed locally. 376+6=382 is the round-2 count. The implementation log was edited after round 3 (it describes the Markdown check), but its review and validation lines were not.",
      "failure_scenario": "The owner merges on the strength of the log and STATUS: two clean review rounds and a fully passing CI tooling run. In fact a third round changed the gate, an unrechecked fix followed, and the suite at the merged commit has not run in full. This is the stale-evidence class the delivery threat model names. Fix before merge: give the rounds and their outcome (including this round 4), and replace the counts with the PR's own CI tooling-test result for the reviewed commit, or say it is pending.",
      "file": "docs/history/implementation_log.md",
      "id": "R4-B2",
      "kind": "blocking",
      "line": 28,
      "problem": "The slice-3 close-out records contradict the review record and the current tree. The implementation log says \"Review: two rounds through the launcher ... round 2 accepted every answer\". review_slice_3.md has a third round, which reviewed the Markdown header check, and an R3-A1 fix applied after that round and \"not rechecked\". This review is round 4. The log and STATUS also give tooling-test counts from round 2: \"376 pytest pass\" locally and \"all 382 ... in CI ... on `a09ab0d`\". At the reviewed commit the local run is 388 passed and 6 failed (394 tests). The only CI run that included the shell cases was on `a09ab0d`, before the Markdown check and the R3-A1 tests existed. So the tooling suite at this commit has never passed in full anywhere, while the records suggest it has."
    },
    {
      "evidence": "implementation_log.md:33-42 lists make lint, tooling-test, E2E, qa-deploy and qa-evidence only. AGENTS.md step 4: \"run `make qa-quality` (includes `qa-trace`, `docs-check`, `test-lint` and `qa-deploy`) ... add a dated entry ... (what changed, validation results, what was not run and why)\".",
      "failure_scenario": "A broken link or anchor in the new review record or the changed docs, or a qa-trace gap, shows up only in PR CI, after the close-out already claims validation. If it was run, record it. If not, say so. Fix before merge: it is one line.",
      "file": "docs/history/implementation_log.md",
      "id": "R4-A1",
      "kind": "advisory",
      "line": 33,
      "problem": "Step 4 of the slice workflow requires `make qa-quality` (qa-trace, docs-check, test-lint, qa-deploy). The slice-3 entry does not report it as run, and does not list it under \"what was not run and why\". STATUS has no qa-quality row for slice 3 either. The change adds a Markdown review record, edits AGENTS.md's gates table and adds a slice-index status, all of which docs-check and gate-consistency read."
    },
    {
      "evidence": "header_problem: `if path.endswith(\".py\")`, then the suffix set and Dockerfile names, then `is_shell`. file_findings:219 returns [] for anything not `.py` that is not shell. TOOL_DIRECTIVE (line 34) has no Docker directives. A grep finds no extensionless Python script and no Docker parser directive in the repo today.",
      "failure_scenario": "An agent adds an extensionless Python CLI like the bash `varambu`, with a 15-branch `main` and no docstring, and `make lint` passes. Or it adds a Dockerfile whose first line is `# syntax=docker/dockerfile:1`, and the header check passes. Either narrow the row's wording or extend detection (a python shebang, Docker directives). Not needed for this merge, since no such file exists.",
      "file": "scripts/lint_changed_files.py",
      "id": "R4-A2",
      "kind": "advisory",
      "line": 244,
      "problem": "The AGENTS.md row and the log say \"every added Python ... file starts with a purpose comment\" and is linted. Python is recognised only by the `.py` suffix. An extensionless Python script (`#!/usr/bin/env python3`) or a `.pyi` file gets neither ruff nor the docstring check. Only shell has shebang detection. Dockerfile parser directives (`# syntax=...`, `# escape=...`, `# check=...`) count as purpose comments, because TOOL_DIRECTIVE does not list them. `Containerfile`, `*.Dockerfile` and `.bash` files without a shebang are not recognised at all."
    },
    {
      "evidence": "Line 151: `unique = {(r[\"code\"], r[\"location\"][\"row\"], r[\"message\"]) for r in raw}`, then `sorted(unique)`. LintError (exit 2) is the only handled failure; any other exception exits 1 through Python's default handler.",
      "failure_scenario": "An agent pushes a half-edited module. The `lint` job fails with a Python traceback instead of a finding line, and the agent may read it as a gate bug. Sorting with `key=lambda t: (t[0] or '', t[1], t[2])` and a syntax-error test would settle this. Not required for this merge.",
      "file": "scripts/lint_changed_files.py",
      "id": "R4-A3",
      "kind": "advisory",
      "line": 152,
      "problem": "`sorted(unique)` sorts (code, row, message) tuples. As I understand ruff \u2265 0.5, it reports syntax errors with `code: null` while still reporting other rules on the same file. If so, a changed `.py` file with a syntax error plus any coded finding makes `sorted` raise `TypeError` (None vs str). The gate then dies with a traceback and exit code 1, the same code as \"findings\". This is a red, not a green, but the output is unclear and indistinguishable from a lint failure. No test covers a file that does not parse."
    },
    {
      "evidence": "visit() recurses only into FunctionDef/AsyncFunctionDef/ClassDef children. In added_or_worse, `worse = len(values) > len(before[key]) or max(values) > max(before[key], default=0)`. Before: outer C901=13 and nested C901=11, i.e. [13, 11]. After the nested one goes to 12: [13, 12]. Same count, same max, so the change passes. A grep finds no such nested defs in services/ or scripts/ today.",
      "failure_scenario": "Rare today: a later change raises a nested helper or a property setter above its earlier complexity, and the gate stays green. Comparing sorted value lists element-wise, or adding the def line text to the key for unindexed functions, would close it. Advisory only.",
      "file": "scripts/lint_changed_files.py",
      "id": "R4-A4",
      "kind": "advisory",
      "line": 100,
      "problem": "Some functions share a key, and their findings are compared only by count and max value, so one can mask another. `function_spans` descends only through def and class nodes. Functions defined inside `if`, `try`, `with` or `for` blocks inside a function therefore get the outer function's key. Two functions with the same qualified name (a property getter and setter, `@overload`, conditional redefinitions) also share a key. When one of them is the over-limit function with the higher value, the other can be made worse unnoticed."
    },
    {
      "evidence": "changed_files: `git diff --name-status -M -z <merge_base> HEAD`. file_findings: `read_at_revision(\"HEAD\", ...)`. The output does not say that only commits are checked.",
      "failure_scenario": "An agent runs `make lint` on its working tree before committing, sees PASSED and records it in the implementation log. The over-limit function it just wrote was never linted. CI catches it on the PR, so this is only a false local green. Print a note, or fail, when `git status --porcelain` is not empty.",
      "file": "scripts/lint_changed_files.py",
      "id": "R4-A5",
      "kind": "advisory",
      "line": 279,
      "problem": "`make lint` diffs the merge-base against the committed `HEAD` and reads files with `git show HEAD:`. Uncommitted and staged edits are invisible, and the run still prints PASSED. The step-4 workflow has agents run gates locally before the PR."
    },
    {
      "evidence": "tests/tools/test_lint_changed_files.py, the last test: `subprocess.run([\"ruff\", \"check\", \"--no-cache\", \"services\", \"scripts\"], cwd=ROOT ...)`; `assert result.returncode == 0`. The AGENTS.md QA tooling tests row: \"`tests/tools/` (pytest) and `tests/shell/` pass\".",
      "failure_scenario": "A PR that adds a ruff default-rule violation in a file the lint job does not see (a deleted-then-restored path, or a file outside the diff after a ruff upgrade) fails tooling-test. The rulebook tells the author that check is not gated. That is a confusing red and a small rule/repo disagreement. Move the sentence to the tooling-test row, or say there that the test enforces it.",
      "file": "AGENTS.md",
      "id": "R4-A6",
      "kind": "advisory",
      "line": 265,
      "problem": "AGENTS.md still lists \"`ruff check services scripts` ... stays clean on the whole tree\" under \"Standards that are **not** gated yet\". This change makes it gated: test_plain_ruff_check_keeps_the_default_rules_and_passes_on_the_tree runs exactly that command in `make tooling-test`, a required CI job. The test is also named for \"keeps the default rules\", but what it asserts is that the tree is clean."
    },
    {
      "evidence": "Read the test file against `lint_changed_files.py`. The prompt's coverage table shows 0% for the gate, because it runs as a child process. Running the gate in-process for a few tests (`lint_changed_files.main([...])` with `cwd` set via monkeypatch) would give a real coverage measurement.",
      "failure_scenario": "A regression in any of these paths, such as dropping `--ignore-noqa` for N or file-level noqa honoured on C901, stays green. Most are low risk. The shellcheck fail-closed path and an in-process coverage run are the cheapest to add.",
      "file": "tests/tools/test_lint_changed_files.py",
      "id": "R4-A7",
      "kind": "advisory",
      "line": 0,
      "problem": "Other gate behaviours that no test exercises, whatever the test plan says: shellcheck missing or exiting with an error (the residual from F3); an existing module-level, line-text-keyed Python violation staying when its row moves; `noqa` on N, F841 and the PLR rules, and the file-level `# ruff: noqa` form (only `# noqa: C901` and `# noqa: F401` are tested); `.yml` (only `.yaml`) and `Dockerfile.*` headers; an extensionless shell script without a purpose comment; status T (type change). In test_renamed_file_..._gaining_one_fails the second half would also pass if Git no longer detected the rename (status A makes every finding new), so only its first half proves rename matching."
    },
    {
      "evidence": "changed_files calls `git(\"diff\", \"--name-status\", \"-M\", \"-z\", merge_base, \"HEAD\")`. Without `-C`/`--find-copies`, Git never emits C.",
      "failure_scenario": "There is no functional failure. A reader may think copies are detected and handled specially. Dropping the C handling, or documenting why it stays, removes a path no test can reach.",
      "file": "scripts/lint_changed_files.py",
      "id": "R4-S1",
      "kind": "simpler_alternative",
      "line": 83,
      "problem": "The copy branch (status C, `old_path=None`) and the `status in \"AC\"` header condition are dead code. `git diff -M` detects renames but not copies (copies need `-C`), so a copied file arrives as status A anyway."
    },
    {
      "evidence": "Makefile comment: \"Set it back to the main ruleset (26054924) when the PoC merges into main.\" STATUS and the slice index say nothing about it. AGENTS step 4: \"open a GitHub issue for work found but not done\".",
      "failure_scenario": "When the PoC is merged into `main` (slice 8 or later), gate-consistency on `main` keeps reading the PoC ruleset and either passes against the wrong branch's checks or fails confusingly. Add one line to the handoff, or open an issue, before merge.",
      "file": "Makefile",
      "id": "R4-A8",
      "kind": "advisory",
      "line": 18,
      "problem": "Restoring `RULESET_URL` to the `main` ruleset when the PoC merges into `main` is recorded only in a Makefile comment. No issue or plan item tracks it. The same merge must also decide whether `lint` becomes a required check on `main`, which the plan says would block every `main` PR today."
    }
  ],
  "verdict": "no"
}
````````

</details>

### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| R4-B1 | **Fixed.** Three tests cover a modified or renamed shell script: an existing finding stays, a new one fails, and a rename with unchanged findings passes. They need `shellcheck`, so their first run is in the PR's CI. A fourth test, which needs no `shellcheck`, shows that a changed shell script fails the run when `shellcheck` is missing. | `test_modified_shell_script_fails_only_on_a_new_finding`, `test_renamed_shell_script_with_unchanged_findings_passes`, `test_missing_shellcheck_fails_the_run_for_a_changed_shell_script` |
| R4-B2 | **Fixed.** The implementation log names four rounds and what each found. The test counts now describe the real state: locally, all pass except the 9 shell cases that need `shellcheck`; the earlier CI run on `a09ab0d` covered only the 6 shell cases that existed then. The STATUS row says the same. | `implementation_log.md`, `STATUS.md` |
| R4-A1 | **Fixed.** `make qa-quality` was run and passes; it is recorded in the log and STATUS. | same |
| R4-A2 | **Partly fixed.** Dockerfile parser directives (`# syntax=`, `# escape=`, `# check=`) no longer count as a purpose comment, with a test. The `AGENTS.md` row now says what is detected: `.py` files, and shell scripts by extension or shebang. Detecting Python by shebang, `.pyi` files and `Containerfile`s is a slice-4 input. | `TOOL_DIRECTIVE`; `test_new_file_without_a_purpose_comment_fails[dockerfile-directive]`; `AGENTS.md` |
| R4-A3 | **Probed; covered.** Ruff 0.15.18, the pinned version, reports a syntax error with the code `invalid-syntax` and nothing else for the file, so the sort cannot fail. A fallback code covers a missing one, and a test shows that a changed module that does not parse fails with a finding. | `python_findings`; `test_changed_module_that_does_not_parse_fails_with_a_finding` |
| R4-A4 | **Slice-4 input.** Nested functions and functions with the same name share a key. | — |
| R4-A5 | **Fixed.** The gate prints a note when the working tree has uncommitted changes, which it does not lint. | `main`; `test_uncommitted_changes_are_reported_as_not_linted` |
| R4-A6 | **Fixed.** The whole-tree `ruff check` moved from "not gated yet" to the tooling-test row, which enforces it. The test is renamed to `test_plain_ruff_check_passes_on_the_tree`. | `AGENTS.md` |
| R4-A7 | **Partly fixed.** Missing `shellcheck` is now tested. The other untested paths are slice-4 input, together with the owner's decision on untested paths. | — |
| R4-A8 | **Fixed in the handoff.** The implementation log and the PR list what to reset when the PoC merges into `main`. | `implementation_log.md`; PR |
| R4-S1 | **Applied.** The copy branch is removed, because `git diff -M` reports no copies. | `changed_files`, `lint` |

Both blocking findings are fixed. A recheck would be round 5, which needs the owner's extension.
