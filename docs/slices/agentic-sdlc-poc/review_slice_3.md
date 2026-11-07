# Review record — agentic-sdlc-poc slice 3 (changed-files lint)

Implementation review of slice 3 of the [plan](plan.md), on the branch
`poc/slice-3-changed-files-lint`, which is built on slice 2 (`poc/slice-2-review-launcher`) until
slice 2 merges. The reviews ran through `scripts/run_independent_review.py`; each attempt is in
[`review_attempts.jsonl`](review_attempts.jsonl) (unit `slice_3`). This record keeps the task
prompts and the reports verbatim and the author's answers.

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

### Task prompt (verbatim)

````text
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
````

### Report (verbatim, rendered from the released JSON)

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

### Task prompt (verbatim)

````text
This is review round 2 of the implementation review of slice 3 of the agentic-SDLC PoC (the changed-files lint gate): a focused recheck by the original reviewer. Your round-1 report and the author's answers are below; check each answer against the change (_review_inputs/change.diff now covers round 1's commit and the fixes). Under the approved rules, from round 2 a new finding counts only if it blocks, except simpler alternatives and decision concerns. Open files by their path from the copy root.

## Your round-1 report (verbatim JSON)

[the round-1 report below, as the JSON the launcher released]

## The author's answers

[the author's answers to round 1 below]

Local: 376 tooling tests pass; the 6 shell cases still need shellcheck, which only CI has. `make lint` passes on the change.

## Questions to answer

1. For each finding, accept the answer or re-raise it with new evidence.
2. Did the fixes introduce a blocking problem?
````

### Report (verbatim, rendered from the released JSON)

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

