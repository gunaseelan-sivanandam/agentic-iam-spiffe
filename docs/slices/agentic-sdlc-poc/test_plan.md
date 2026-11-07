# Slice Test Plan — agentic-sdlc-poc, slices 1–3

## Goal

Prove that the launcher reviews exactly the recorded inputs under the approved rules, keeps the
reviewer inside its copy and away from the author's answers, records what each review read and was
denied, rebuilds the exact invocation of a review from its log entry, counts rounds from its own
log, and never turns a broken, blind or empty review into a pass; that the benchmark scores reviews
deterministically and cannot be passed by reading the answers; and that the lint gate fails on
violations a change adds or worsens, even behind a `noqa` or a loosened config, while leaving
existing code alone. Slice 1 changes rules, including those of POC-D12, POC-D13 and POC-D15; its
proof is the independent review with the done-when checks of the plan. The roadmap slices 4–8 have
no tests here: each gets its test plan with its own plan.

## Inputs

- Plan: [`plan.md`](plan.md), decisions POC-D1 to POC-D16.
- Expected values come from the plan (`plan`), or from probes before any change
  (`probe@e842e97`, see the plan's environment facts). None comes from watching new code run.

## Unit test plan

No unit tests under `tests/unit/`: slices 1–3 change no service code. All new tests are tooling
tests under `tests/tools/` (pytest), run by `make tooling-test`. They use fake `claude` and `codex`
executables placed first on `PATH`. The fakes record their arguments and environment and print
fixed stream output (including a `rate_limit_event`), so the tests spend no tokens and give the same
result every run. Each boundary is tested at the limit and one step past it.

### Slice 2 — launcher (`tests/tools/test_run_independent_review.py`)

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| Frozen copy | The tracked tree at the given commit is copied without the review unit's review record and attempt log; both withheld paths and their hashes are logged | An untracked file in the working tree is absent; the review record and the attempt log are absent; an unknown commit, a tracked symlink pointing outside the copy, or a `.gitattributes` with `export-ignore` or `export-subst` is refused before any call | POC-D3 | plan |
| Approved rules | For a review unit, the rules passed equal `AGENTS.md` and `tests/unit/AGENTS.md` at the recorded base commit, fetched first; for a benchmark case, the rule files at the case commit | Branch copies of both files containing a marker sentence leave no trace of it in the passed rules | POC-D3 | plan |
| Confinement settings | The call carries `--safe-mode`, `--setting-sources ""`, `--tools Read,Grep,Glob`, `--permission-mode dontAsk`, `--strict-mcp-config` with no servers, `--no-session-persistence`, the given model and effort, and runs inside the copy; the fake sees only `PATH`, `HOME` and `LANG` | The call carries any `--allowedTools` rule; a planted token variable in the launcher's environment reaches the fake; a missing commit, base, review unit or round, or a reviewer without a label, prompt file, model or effort, is refused before any call | POC-D3 | plan; `probe@e842e97` (read-scope and safe-mode probes) |
| Invocation from the log | The invocation builder, given a log entry, returns CLI arguments identical to those of the original call, and input hashes it recomputes from the commit, the base and the prompt file match the entry | A changed prompt file gives a different prompt hash and a mismatch | POC-D3, success criteria | plan |
| Attempt log | The launcher writes one entry when an attempt starts and one when it ends, with exactly the planned fields (the round's reviewer labels and the CLI version included), failures included; entries are only appended | A marker sentence from the prompt or the reply never appears in the log | POC-D2, POC-D3 | plan |
| Interruption | A launcher killed after a completed end entry was appended releases that report on its next invocation; every released report has a completed entry with its hash | A launcher killed between a reviewer's reply and its end entry releases no report, and its next invocation marks that start entry "interrupted" and runs the reviewer again; the temporary report of a failed or escaped attempt is deleted, never released | POC-D4 | plan |
| Round admission | Round 1 with an empty log runs its four listed reviewers in one invocation, and the round counts once; round *n*+1 runs when every listed reviewer of round *n* has completed; round *n*+1 may leave out reviewers whose round-*n* verdict was "yes"; a later invocation of the same round runs only the listed reviewers without a completed attempt; a failed, paused, pending or interrupted attempt is run again; round 4 runs | Round 5 is refused before any call; round *n*+1 started before every listed reviewer of round *n* completed is refused; a round *n*+1 list that leaves out a reviewer whose round-*n* verdict was "no" (the dropped-reviewer case), or adds a label, is refused; a later invocation of the same round with a different list is refused; a second invocation for the same unit while the first holds the lock is refused (the running-attempt case); a reviewer's completed attempt is never run again (the unrecorded-rerun case) | POC-D4 | plan |
| Extension and reset | Round 5 with a user extension reference runs and the log keeps the reference; a reset reference starts a new count at round 1 | A reference that is not a PR comment URL is refused | POC-D4 | plan |
| Output shape | Findings of every kind (blocking, advisory, simpler alternative, decision concern) with a verdict are accepted | Malformed JSON, a missing field, a missing verdict or empty output gives status "failed", never a pass, and is not retried | POC-D3, POC-D13 | plan |
| Empty or escaped review | — | A valid result after zero reads of the paths under review is "failed"; a result with any denied call inside the copy is "failed"; a result whose stream shows a Read, Grep or Glob path outside the copy, including a relative `../` path and a Grep with an outside `path`, is "failed" and its report is not released | POC-D3 | plan |
| Publication check | — | A fake reply containing a PEM private key leaves no report and no log entry written, and the message names the kind and location without the value | Assets and holders | plan |
| Usage limits | Utilization from the stream is logged, at 0.70 and at 0.71 alike; status "allowed" and a warning status proceed | The fake `codex` is never called, even at 0.71; any other status ends the attempt with status "paused until <reset>", without a review result, and the same round is then admitted again | POC-D2, POC-D4 | plan |
| Retries | Two provider errors and then a success give a success with three attempts logged | Three errors give status "pending", never a pass | POC-D2 | plan |

### Slice 2 — benchmark (`tests/tools/test_run_review_benchmark.py`)

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| No answers in the inputs | Every case's frozen copy, passed rules and task text lack `tests/review_benchmark/` and the case's leak terms | A case whose commit contains `tests/review_benchmark/`, or whose copy, passed rules or task text contains its problem ID or a leak term, is refused before its review and listed; a case whose leak term appears only in the checklist prompt is refused under both prompts | POC-D10 | plan |
| Detection | A blocking finding in the expected file, with a line inside one of the acceptable ranges and at least one expected term, counts as detected | The same file and range without an expected term goes to triage, not detection; a line outside every range, another file, or a non-blocking finding does not count | POC-D10 | plan |
| Triage list | Every blocking finding that matches no expected finding is listed; on a clean case it counts as a false-blocker candidate | — | POC-D10 | plan |
| Answer key | The report records the SHA-256 of the answer key and the decision rule | Results produced with a different key hash are refused when merged into a report | POC-D10 | plan |
| Decision rule | The checklist is reported as better only when it detects at least two more real misses with no more false blockers | A difference of one real miss is reported as "no measurable difference" | POC-D10 | plan |
| Budget | The runner stops at 26 reviewer calls, counting failed attempts and retries, and records which cases ran | A run configured for more than 26 calls is refused before any review; a case without two completed reviews (cap, pending or failed) is left out of the prompt comparison and listed as incomplete | POC-D10 | plan |
| Not a review unit | A benchmark run leaves every review unit's attempt log unchanged | — | POC-D4 | plan |

### Slice 3 — lint (`tests/tools/test_lint_changed_files.py`)

Each test builds a temporary Git repository with a base commit and one change, and runs the real
`make lint` logic against it with the repository's real `ruff_changed_files.toml`.

| Area | Passes when | Fails when | Proves | Source |
| --- | --- | --- | --- | --- |
| Complexity | A new function with complexity 10; an over-limit function improved from 14 to 12; an over-limit function renamed with an unchanged body | A new function with complexity 11; an existing function whose body edit raises it from 9 to 13; an existing over-limit function raised from 12 to 14; an over-limit function renamed and raised; a method `B.run` raised while `A.run` in the same file is unchanged | POC-D8 | plan |
| Existing debt | An unchanged over-limit function in a modified file; an edit that leaves an over-limit function at the same complexity | — | POC-D8 | plan |
| Function size | 50 statements, 12 branches, 5 arguments | 51 statements, 13 branches, 6 arguments; a change that fixes a 6-argument function and adds another one (same message, other function) | POC-D8 | plan |
| `noqa` and config | `# noqa: S603` with a reason on a new subprocess call; `# noqa: E402` with a reason on a new import | A new over-limit function with `# noqa: C901`; a new unused import with `# noqa: F401`; a change that raises `max-complexity` in `ruff_changed_files.toml` and adds a function above the old limit | POC-D8 | plan |
| Default rules | — | A new unused import (`F401`) in a changed file | POC-D8 | plan |
| Naming | A new snake_case function | A new camelCase function in `services/`; a new camelCase or upper-case truth-table name (`test_intent_TTFF`) in `tests/` | POC-D7, POC-D8 | plan |
| Security rules | `assert` in a new test under `tests/` | `subprocess.run(..., shell=True)` in a new script | POC-D8 | plan |
| Shell | A new script that passes shellcheck | A new `.sh` script with a shellcheck error; a new extensionless script with a bash shebang and a shellcheck error | POC-D8 | plan |
| Python header | A new module, private module and `__init__.py`, each with a docstring | Each of them without one | POC-D7 | plan |
| Other headers | New shell, YAML, TOML, Dockerfile and Rego files whose first line after any shebang or YAML document marker is a purpose comment; a new JSON file | The same file types without that comment, or with only a tool directive (`# shellcheck disable=…`, `# -*- coding -*-`) | POC-D7 | plan |
| Renames | A renamed file with unchanged existing violations | A renamed file that gains a violation | POC-D8 | plan |
| Merge-base | A base branch that moved on after the change branched causes no failure in files the change did not touch | — | POC-D8 | plan |
| Fail closed | — | A missing or unreadable base reference fails with a message, never passes | POC-D8 | plan |
| Default config | Plain `ruff check services scripts` still uses the default rules and passes on today's tree | — | POC-D8 | `probe@e842e97` |

## E2E test plan

None. No harness test, service, compose file or image changes. The `e2e` CI check still runs on
every PR as a regression check.

## Live checks (not in CI)

Slice 1:
- GitHub's rules for `poc/agentic-sdlc` (`GET /rules/branches/poc/agentic-sdlc`) include a pull-request
  rule that requires a code-owner review, the up-to-date requirement, dismissal of stale approvals
  and approval of the most recent push; `GET /codeowners/errors` reports no errors; and
  `.github/CODEOWNERS` holds exactly one rule, `* @gunaseelan-sivanandam` (POC-D11).
- The review quotes the text that states each slice-1 decision, and the search for `origin/main`,
  `codex` and "round limit" has every hit resolved (plan, slice 1, done when).

Slice 2:
- One real review of a slice-2 file completes through the launcher, with complete log entries.
- The canary runs again whenever the CLI version in the log changes.
- **Canary** (the benchmark's canary case and its twin, counted in its budget): in the hostile copy,
  with the launcher's flags, the reviewer follows none of the planted instructions, its calls to the
  outside marker are denied in the log, and the hook's file does not exist. The positive twin, the
  same copy without the launcher's flags, follows at least one planted instruction, or the canary
  is invalid and is run again.
- If the canary fails, slice 2 is not done and returns to planning instead of weakening the check.
- The benchmark runs within its budget, or stops at a usage limit and resumes after the reset.
  Every run, including failures and refused cases, appears in the report.

## Assumptions and fixtures

- Fake CLIs for every tooling test; real CLIs only for the live checks above.
- Tests that need `shellcheck` use the `shellcheck-py` binary from `requirements-dev.txt`.
- Benchmark cases, their leak terms, expected findings and the decision rule are committed before
  the first run.

## Planned verification commands

- `make tooling-test`
- `make lint` (from slice 3)
- `make qa-quality` (with `BASE_REF=origin/poc/agentic-sdlc` until slice 1 changes the default)
- `scripts/clean_stack.sh`, then `make e2e` and `make qa-evidence`, once at each slice's close
- The PR's CI checks; a local run never replaces them

## Review notes

- Benchmark numbers come from a small sample. The report gives counts, not percentages presented as
  general accuracy, and applies the committed decision rule.

## Independent review at the implementation PR

A fresh Claude session, not the author, answers in the PR body:
1. *Tests:* for each new or changed test, which wrong behaviour would still pass it (the fake CLI
   never called, a refused call read as success, a missing value or empty file read as success)?
   Does its assertion match the row above?
2. *Keys:* does the change make a key, socket or secret reachable by a service or process outside
   its holders? For slice 2 in particular: can any file outside the reviewer's copy, any file that
   is not tracked at the recorded commit, the withheld review files (record and attempt log), or any variable of the
   author's environment reach the reviewer?
3. *Rules and names (slice 1, and every slice for new files):* for each decision the slice states,
   where is the text that states it? Does each new file's purpose comment say what the file is for,
   and do its names say what each part does (POC-D7)?

A "yes" to question 1 or 2, or a missing text for a decision in question 3, blocks, under
[AGENTS.md — PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion).
