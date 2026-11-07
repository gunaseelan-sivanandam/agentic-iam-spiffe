# Slice Test Plan — agentic-sdlc-poc, slices 1–3

## Goal

Prove that the launcher reviews exactly the recorded inputs under the approved rules, keeps the
reviewer inside its copy, can rebuild the exact invocation of a review from its record, and never turns a broken review into
a pass; that the benchmark scores reviews deterministically and cannot be passed by reading the
answers; and that the lint gate fails on violations a change adds or worsens while leaving existing
code alone. Slice 1 changes only text, so its proof is the independent review.

## Inputs

- Plan: [`plan.md`](plan.md), decisions POC-D1 to POC-D11.
- Expected values come from the plan (`plan`), or from probes before any change
  (`probe@e842e97`, see the plan's environment facts). None comes from watching new code run.

## Unit test plan

No unit tests under `tests/unit/`: slices 1–3 change no service code. All new tests are tooling
tests under `tests/tools/` (pytest), run by `make tooling-test`. They use fake `claude` and `codex`
executables placed first on `PATH`. The fakes record their arguments and print fixed stream output
(including a `rate_limit_event`), so the tests spend no tokens and give the same result every run.
Each boundary is tested at the limit and one step past it.

### Slice 2 — launcher (`tests/tools/test_run_independent_review.py`)

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| Frozen copy | The whole tracked tree at the given commit is copied, each file's SHA-256 recorded | An untracked file in the working tree is absent from the copy; an unknown commit is refused before any call | POC-D3 | plan |
| Approved rules | The rules passed to the CLI equal `AGENTS.md` and `tests/unit/AGENTS.md` at the recorded base commit, which was fetched first | Branch copies of both files containing a marker sentence leave no trace of it in the passed rules | POC-D3 | plan |
| Confinement settings | The call carries `--safe-mode`, `--tools Read,Grep,Glob`, `--permission-mode dontAsk`, `--strict-mcp-config` with no servers, `--no-session-persistence`, the given model and effort, and runs inside the copy | The call carries any `--allowedTools` rule; a missing model, effort or prompt file is refused before any call | POC-D3 | plan; `probe@e842e97` (read-scope probe) |
| Invocation from record | The invocation builder, given an attempt record, returns CLI arguments identical to those of the original call, and input hashes it recomputes from the commit, the base and the prompt file match the record | A changed prompt file gives a different prompt hash and a mismatch | POC-D3, success criteria | plan |
| Round admission | Round 1 with no record runs; round *n* runs when the record's last completed round is *n−1*; round 4 (the third fix round) runs | Round 5 is refused before any call; a round that skips or repeats a number is refused, including one that would reproduce a completed review; a missing or unreadable record is refused for any round after the first; round 5 with a named user extension runs and the record keeps the reference | POC-D4 | plan |
| Output shape | Findings matching the schema are accepted | Malformed JSON, a missing field or empty output gives status "failed", never a pass with zero findings, and is not retried | POC-D3 | plan |
| Attempt record | The record has exactly the planned fields, failures included: the round number and any extension reference for a review unit, the case and configuration for a benchmark run | A marker sentence from the prompt or the reply never appears in the record | POC-D2, POC-D3 | plan |
| Usage limits | Utilization from the stream is recorded, at 0.70 and at 0.71 alike | The fake `codex` is never called, even at 0.71; a window whose status is not "allowed" ends the run with status "paused until <reset>", without a review result; the same round is then admitted again, because the paused attempt completed no round | POC-D2, POC-D4 | plan |
| Retries | Two provider errors and then a success give a success with three attempts recorded | Three errors give status "pending", never a pass | POC-D2 | plan |

### Slice 2 — benchmark (`tests/tools/test_run_review_benchmark.py`)

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| No answers in the copy | Every case's frozen copy lacks `tests/review_benchmark/` and its leak terms | A case whose commit contains `tests/review_benchmark/`, or whose frozen copy contains its problem ID or a leak term anywhere in the tree (the runner's own search), is refused before its review | POC-D10 | plan |
| Not a review unit | A benchmark run leaves every review record unchanged | — | POC-D4 | plan |
| Detection | A blocking finding in the expected file, with a line inside the expected range and at least one expected term, counts as detected | The same file and range without an expected term goes to triage, not detection; a line outside the range, another file, or an *advisory* finding does not count | POC-D10 | plan |
| Triage list | Every blocking finding that matches no expected finding is listed; on a clean case it counts as a false-blocker candidate | — | POC-D10 | plan |
| Answer key | The report records the answer key's SHA-256 | Results produced with a different key hash are refused when merged into a report | POC-D10 | plan |
| Budget | The runner stops at 26 reviewer calls, counting failed attempts and retries, and records which cases ran | A run configured for more than 26 calls is refused before any review; when retries exhaust the cap in the middle of a pair (fake CLI errors), that case is left out of the prompt comparison and listed as incomplete | POC-D10 | plan |

### Slice 3 — lint (`tests/tools/test_lint_changed_files.py`)

Each test builds a temporary Git repository with a base commit and one change, and runs the real
`make lint` logic against it.

| Area | Passes when | Fails when | Proves | Source |
| --- | --- | --- | --- | --- |
| Complexity | A new function with complexity 10 | A new function with complexity 11; an existing function whose body edit raises it from 9 to 13; an existing over-limit function raised from 12 to 14 | POC-D8 | plan |
| Existing debt | An unchanged over-limit function in a modified file; an edit that leaves an over-limit function at the same complexity | — | POC-D8 | plan |
| Function size | 50 statements, 12 branches, 5 arguments | 51 statements, 13 branches, 6 arguments | POC-D8 | plan |
| Default rules | — | A new unused import (`F401`) in a changed file | POC-D8 | plan |
| Naming | A new snake_case function | A new camelCase function in `services/`; a new camelCase or upper-case truth-table name (`test_intent_TTFF`) in `tests/` | POC-D7, POC-D8 | plan |
| Security rules | `assert` in a new test under `tests/` | `subprocess.run(..., shell=True)` in a new script | POC-D8 | plan |
| Shell | A new script that passes shellcheck | A new `.sh` script with a shellcheck error; a new extensionless script with a bash shebang and a shellcheck error | POC-D8 | plan |
| Python header | A new module, private module and `__init__.py`, each with a docstring | Each of them without one | POC-D7 | plan |
| Other headers | New shell, YAML, TOML, Dockerfile and Rego files whose first line (after any shebang) is a purpose comment; a new JSON file | The same file types without that comment | POC-D7 | plan |
| Renames | A renamed file with unchanged existing violations | A renamed file that gains a violation | POC-D8 | plan |
| Fail closed | — | A missing or unreadable base reference fails with a message, never passes | POC-D8 | plan |
| Default config | Plain `ruff check services scripts` still uses the default rules and passes on today's tree | — | POC-D8 | `probe@e842e97` |

## E2E test plan

None. No harness test, service, compose file or image changes. The `e2e` CI check still runs on
every PR as a regression check.

## Live checks (not in CI)

Slice 1:
- GitHub's rules for `poc/agentic-sdlc` (`GET /rules/branches/poc/agentic-sdlc`) include a pull-request
  rule that requires a code-owner review, and `.github/CODEOWNERS` names only the user (POC-D11).

Slice 2:

- One real review of a slice-2 file completes through the launcher, with a valid attempt record.
- **Confinement:** the reviewer is asked to Read, Grep and Glob a marker file outside its copy; all
  three are denied, and the record shows the denials.
- **Canary** (the benchmark's canary case, counted once in its budget): with harmless marker instructions in the copy's `AGENTS.md`, `CLAUDE.md`, a nested
  `CLAUDE.md`, `.claude/settings.json` and `tests/unit/AGENTS.md`, the reviewer's output shows no
  sign of following any of them.
- If either check fails, slice 2 is not done and returns to planning instead of weakening the check.
- The benchmark runs within its budget, or stops at a usage limit and resumes after the reset.
  Every run, including failures, appears in the report.

## Assumptions and fixtures

- Fake CLIs for every tooling test; real CLIs only for the live checks above.
- Tests that need `shellcheck` use the `shellcheck-py` binary from `requirements-dev.txt`.
- Benchmark cases, their leak terms and expected findings are committed before the first run.

## Planned verification commands

- `make tooling-test`
- `make lint` (from slice 3)
- `make qa-quality` with `BASE_REF=origin/poc/agentic-sdlc`
- `scripts/clean_stack.sh`, then `make e2e` and `make qa-evidence`, once at each slice's close
- The PR's CI checks; a local run never replaces them

## Review notes

- Benchmark numbers come from a small sample. The report gives counts, not percentages presented as
  general accuracy.

## Independent review at the implementation PR

A fresh Claude session, not the author, answers in the PR body:
1. *Tests:* for each new or changed test, which wrong behaviour would still pass it (the fake CLI
   never called, a refused call read as success, a missing value or empty file read as success)?
   Does its assertion match the row above?
2. *Keys:* does the change make a key, socket or secret reachable by a service or process outside
   its holders? For slice 2 in particular: can any file outside the reviewer's copy, or any file
   that is not tracked at the recorded commit, reach the reviewer?

A "yes" to either blocks, under [AGENTS.md — PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion).
