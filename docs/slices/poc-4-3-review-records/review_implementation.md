# Review record — poc-4-3-review-records, unit `implementation`

The record of the review unit `implementation`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt implementation/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `392cd29f7a53`, base `3347754ef038`.

Status: failed (the reply does not match the report schema).

#### Prompt

```markdown
# Implementation review of slice 4.3 (review records written by the launcher and checked, issue #40)

## Intent

The approved plan and test plan are `docs/slices/poc-4-3-review-records/plan.md` (decisions S43-D1 to S43-D8) and
`docs/slices/poc-4-3-review-records/test_plan.md`, merged into `poc/agentic-sdlc` by plan PR #48 (the base of this
review). 4.1 (prompt sections, recheck inputs, severity, the answers table) and 4.2 (files from the diff, upstream
items, computed evidence) were implemented and reviewed before this one; their review records are
`docs/slices/poc-4-1-review-prompts/review_implementation.md` and `docs/slices/poc-4-2-review-inputs/review_implementation.md`.
Those records were built by the author's own script; this review is the first whose record the launcher writes.

The change from the base is in `_review_inputs/change.diff`; the commits of 4.3 start at `89b8f2b`. New files:
`scripts/review_records.py` (parsing and editing records, used by the launcher and the check),
`scripts/check_review_records.py` (the check, run by `make docs-check` through `scripts/check_docs.py`) and
`tests/tools/test_check_review_records.py`.

## The author's self-review (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.** None new beyond 4.1 and 4.2: the CLI version is still
   `2.1.321 (Claude Code)` (`claude --version`). The evidence secret check's shapes were not changed; a single base64
   line of a PEM key in an answers row is not found by it (it needs the PEM header or a run of 200 characters), which
   the author saw while writing the scan test and handled by putting the whole key in the answers section.
2. **Each check added or changed, the case it catches, and its test** (all in `tests/tools/test_check_review_records.py`).
   - The launcher's blocks hash as logged, for completed, failed, withheld and killed attempts, with fences longer than
     the text's own backtick runs: `test_completed_attempt_leaves_…`, `test_text_holding_seven_backticks_…`,
     `test_failed_attempt_keeps_…` (two cases), `test_withheld_attempt_…`, `test_killed_attempt_…`.
   - A section written but never logged is removed by the next run: `test_section_written_but_never_logged_…`.
   - Parallel reviewers each keep a whole section: `test_parallel_reviewers_leave_two_whole_separate_sections`.
   - The whole prompt is scanned before anything is written or sent (a key in the task, the evidence or the answers;
     the author's HOME path in the task): `test_secret_or_local_path_in_the_prompt_is_refused_before_anything_is_written`
     (four cases), and a task without a final newline is refused: `test_task_prompt_without_a_final_newline_is_refused`.
   - The check fails on one changed character in each block, a Report block under another attempt's heading, a heading
     without a logged attempt and a logged attempt without a heading, a logged report without a block and a block
     without a logged report, a missing record, and answers changed after a recheck read them; it passes a fenced
     snippet in answers and ignores attempts without `record_blocks`: the tests of the section "The check: blocks".
   - Allowed answers: six allowed forms pass and eight disallowed ones fail, among them a rejected high finding that
     only links to evidence without `owner:`: the two parametrised tests at the end.
   - `make docs-check` runs the check: `test_docs_check_runs_the_record_check`.
   - The recheck reads the earlier report from the record with the released file deleted, and refuses a Report block
     that does not match the log or is missing: in `tests/tools/test_run_independent_review.py`,
     `test_recheck_reads_the_earlier_report_from_the_record_with_the_released_file_deleted` and
     `test_recheck_without_its_inputs_is_refused_before_any_call`.
3. **Claims and what checks them mechanically.** "The record holds the prompt, evidence and report verbatim": the
   check compares each block's SHA-256 with the log, on every `make docs-check`. "Parallel reviewers cannot
   interleave": the Report block is inserted at the end of its own attempt's section, never appended at the end of
   the file, and the parallel test checks both sections. "A killed launcher leaves neither a heading without a logged
   attempt nor a logged attempt without a heading": the section is written before the start entry under one lock,
   `recover` removes a trailing section without a start, and the kill test checks the result. Not mechanical: that
   the answers' text is true.
4. **Fixes and their upstream choice.** No reviewer findings yet. The author's dry run (below) found that the check
   accepted any link in a rejected answer, while S43-D4 asks for an `owner:` link; the rule now matches the plan's
   words, with a test of the looser form.
5. **Tried the way the next user runs it.** In a scratch clone of this repository at the branch, with real evidence
   and the fake CLI: two units of different bundles ran in parallel (108 seconds); each record was created with a
   title and purpose paragraph and held its blocks; the check then failed both records for the missing answers, as
   S43-D4 intends ("`docs-check` is red between a released report and its answers"), and passed once the answers
   were committed. A fresh clone without `artifacts/reviews/` then ran the round-2 recheck from the record's Report
   block, and the check passed again.
6. **Where each rule lives.** `AGENTS.md`: the `docs-check` row of the gates table and the Independent review's
   "Reviewer" paragraph (who writes which part of a record; the hand check is replaced). `docs/delivery_problem_log.md`:
   DPL-010's status names 4.3's action. The modules' docstrings describe the record's form.
7. **What was removed, and its review.** The launcher no longer reads a recheck's earlier report from the git-ignored
   released file (it still writes the file, and recovery uses it to complete a killed attempt's Report block). The
   author's record-building script stays outside the repository and is not used for 4.3 and later units; records of
   4.1, 4.2 and the plan reviews, whose attempts carry no `record_blocks`, are not checked (S43-D5). The evidence text
   now ends with a newline, so its block hashes as logged.

## Questions (a minimum, from the test plan)

1. *Tests:* for each new or changed test, which wrong behaviour would still pass it, for example a check that
   compares hashes as a set, or one that passes an empty record?
2. *Keys:* does a key, socket or secret now reach a service outside its holders? Can a secret or an operational
   detail reach the reviewer or a record through the launcher's writing?
3. *Names and headers:* do new files and names say what they do?

Also: does every decision S43-D1 to S43-D8 have its implementation and proof (or, for rule text, its `AGENTS.md`
sentence), and does the change do anything no decision asked for?
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/review_records.py: changed lines not run: 50, 70, 73, 93, 100, 121, 149, 165; branches not taken: 47->50, 69->70, 72->73, 92->93, 99->100, 148->149, 164->165, 166->168 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 42, 80, 177-178, 183-186, 190; branches not taken: 41->42, 79->80, 115->108, 117->108, 184->185, 184->186, 189->190 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/run_independent_review.py: changed lines not run: 166, 904, 962-963; branches not taken: 903->904, 926->exit, 1428->1430 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/check_docs.py: changed lines not run: 205, 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/run_review_benchmark.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

