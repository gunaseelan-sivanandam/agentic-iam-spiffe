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


### Attempt implementation/c1/r1/A/2

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `e9fc5e74de7d`, base `3347754ef038`.

Status: completed; approvable within the threat model: no.

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
EV3: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 928->exit, 1430->1432 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/check_docs.py: changed lines not run: 205, 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/run_review_benchmark.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

`````json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "Lines 50, 70, 73, 93 and 100 are the record parser's malformed-form paths, which no test exercises (R1-2). Line 121 (new_record) is run only in the launcher subprocess (issue #44); the parallel and dry-run tests create records, so it is not a gap. Line 149 is a dead branch (R1-8). Line 165 is the missing-section error, which only recover hits (see EV3).",
      "opened": [
        "scripts/review_records.py",
        "tests/tools/test_check_review_records.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV2",
      "note": "The check is tested in-process, so these lines are genuinely not run. Line 80 (missing Prompt or Evidence block), branches 115->108 and 117->108 (a next round that does not accept) and lines 177-178 (an unreadable log) are untested fail paths (R1-2). Lines 183-186 and 190 are the CLI main, which docs-check does not use, since it imports the module.",
      "opened": [
        "scripts/check_review_records.py",
        "tests/tools/test_check_review_records.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV3",
      "note": "Line 166 and branch 905->906 are defensive load and no-record errors. Lines 964-965 and branch 928->exit are recover on a record without the section, or with no record file; the docstring says the record check reports such a section, and that path is covered by the 'logged attempt has no heading' test. Branch 1430->1432 is HOME == '/'. All are low risk.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "Line 205 is `problems += check_records(root)` inside run_checks. No test runs it, so the wiring into docs-check is unproven (R1-1). Line 215 is a defensive load failure.",
      "opened": [
        "_review_inputs/change.diff",
        "tests/tools/test_check_review_records.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV5",
      "note": "review_inputs.py:286 is the return taken when the interpreter has no user site-packages directory. It depends on the environment and is 4.2 code that has already been reviewed; it is not a 4.3 concern.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "No CI run exists for this commit. Under AGENTS.md a gate's result is its CI job's conclusion, so the author's local gate results are diagnoses, not proof. The slice 4 goal defers CI to the owner's final push. Nothing in this review depends on a CI result.",
      "opened": [],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "EV4: scripts/check_docs.py line 205 is not run by the tooling tests. In test_check_review_records.py, lines 245-253 call only `docs.check_records`. grep of tests/ for `run_checks` finds nothing.",
      "failure_scenario": "A later refactor of run_checks drops or reorders the `check_records` call, for example while merging the problem lists. Every tooling test still passes, and `make docs-check` turns green on records whose blocks no longer match the log or whose findings have no answers. That is the false green S43-D3 exists to prevent, and a 'yes' to test-plan question 1.",
      "file": "tests/tools/test_check_review_records.py",
      "id": "R1-1",
      "kind": "defect",
      "line": 245,
      "origin_stage": "tests first",
      "problem": "No test shows that `make docs-check` runs the record check. The approved test plan has the row \"`make docs-check` runs the record check and fails when it fails\" (test_plan.md, the `docs-check` row), and claim 2 cites `test_docs_check_runs_the_record_check` for it. That test calls `check_docs.check_records(fx.work)` directly. It never calls `run_checks` or `main`, so it does not exercise the line that wires the check into docs-check (`scripts/check_docs.py:205`, `problems += check_records(root)`). Searched tests/tools/test_check_docs.py, tests/tools/test_check_review_records.py and all of tests/ for run_checks, check_records and check_docs: no test calls run_checks.",
      "severity": "blocking"
    },
    {
      "evidence": "EV1: review_records.py lines 50, 70, 73, 93 and 100 are not run. EV2: check_review_records.py line 80 and branches 79->80, 115->108 and 117->108 are not run. The only next-round test, `test_rejected_blocking_finding_that_the_next_round_accepts_passes`, is the positive case. The `high-rejected-alone` case has no round 2 at all.",
      "failure_scenario": "A wrong check would still pass every test, for example one that reads `if block is not None and sha != logged`, or one where `_next_round_accepts` returns True whenever a completed round-2 attempt exists. In the first case, a record whose Prompt block was deleted by a hand edit passes docs-check. In the second, a rejected blocking finding that the round-2 reviewer re-raised passes as answered. Both are false greens on the trust the record is meant to give (test-plan question 1).",
      "file": "scripts/check_review_records.py",
      "id": "R1-2",
      "kind": "defect",
      "line": 80,
      "origin_stage": "tests first",
      "problem": "Several of the check's fail-closed paths have no test, even though the plan's threat model names \"a check that passes an empty, misplaced or malformed block\":\n- a logged attempt whose Prompt or Evidence block is missing (line 80);\n- a block label with no fenced block after it, or an unclosed fence (review_records.py lines 50, 70, 73, 100);\n- an attempt heading that appears twice (line 93);\n- a block label that appears twice;\n- a later-round attempt that is completed but does not accept the finding, for example one that re-raises it (branches 115->108 and 117->108);\n- a log that cannot be read (lines 177-178).\nThe current code handles these cases, but wrong code would also pass. Searched tests/tools/test_check_review_records.py and test_run_independent_review.py for 'no Prompt block', 'appears', 'more than one heading', 'no fenced block', 're-raised' combined with the record check, and 'cannot be read as an attempt log': none found.",
      "severity": "blocking"
    },
    {
      "evidence": "check_review_records.py:136-140 searches OWNER_LINK only in the row of the attempt's own answers section. `_answers_problems` (lines 94-102) fails any change to that section after the recheck. `_next_round_accepts` accepts only `status == \"accepted\"` in round+1.",
      "failure_scenario": "Round 1 reports high finding X1, and the author answers `rejected: \u2026` with a checkable reason. Round 2 re-raises X1, or answers 'cannot determine', and the owner then decides for the author. The round-1 row still has no owner link, and editing it fails the round-2 attempt. `make docs-check` stays red on that record for good, so the slice cannot merge with a green gate unless the log or record is hand-edited. Possible fix for the owner to decide: accept an `owner:` answer to the same finding ID in a later round's answers.",
      "file": "scripts/check_review_records.py",
      "id": "R1-3",
      "kind": "decision_concern",
      "line": 137,
      "origin_stage": "architecture and interfaces",
      "problem": "Together, S43-D3 and S43-D4 leave docs-check permanently red on a path the rulebook allows. S43-D4 lets a rejected blocking or high finding stand only if the next round lists it as `accepted`, or if its own answer row carries an `owner:` link. S43-D3 fails the record once that answers section changes after the recheck read it. AGENTS.md (Review loop) says a re-raised or 'cannot determine' rejection goes to the user, who decides. That decision can never be recorded in a way the check accepts: the round-1 row cannot gain an `owner:` link without breaking the round-2 attempt's `answers_sha256`, and the check looks for neither an `owner:` answer in round 2's answers nor any later round. The check is also red between the answers commit and the recheck, which is the very commit the recheck must review.",
      "severity": "high"
    },
    {
      "evidence": "review_records.py:39 `text.rstrip(chr(10))`; review_records.py:74 `\"\\n\".join(lines[...]) + \"\\n\"` after `text.splitlines()`; run_independent_review.py:1386 `read_text` against line 1444 `sha256_bytes(reviewer.prompt_file.read_bytes())`; check_prompt:1409 tests only `endswith(\"\\n\")`.",
      "failure_scenario": "The author saves a task prompt with a trailing blank line, which editors commonly do. The review runs and is billed, the record is written, and `make docs-check` then reports \"the Prompt block does not match the logged prompt_sha256\". The only remedy is to hand-edit the launcher-written block, which the plan's success criterion rules out (\"no hand editing other than the answers\"). The fix: refuse any task whose bytes differ from `fenced`'s round trip, or hash what is written.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-4",
      "kind": "defect",
      "line": 1409,
      "origin_stage": "implementation",
      "problem": "The Prompt block does not hash as logged for some task files that `check_prompt` accepts. `prompt_sha256` is the SHA-256 of the task file's bytes (line 1444). The block is written from `read_text()`, which turns CRLF into LF, and then through `fenced()`, which strips every trailing newline and adds back exactly one. A task file that ends in a blank line (`\u2026\\n\\n`) or uses CRLF line ends therefore passes `check_prompt`, which only refuses a missing final newline. The reviewer is called, and the record's Prompt block can never match the log. The same goes for text holding other `str.splitlines()` boundaries (\\f, \\x85, \u2028), because `parse_record` re-joins them with `\\n`.",
      "severity": "medium"
    },
    {
      "evidence": "review_records.py:29-32 (ATTEMPT_HEADING, OPEN_FENCE) against run_independent_review.py:1065 (FENCE `^\\s*(`{3,}|~{3,})`). review_records.py:181-185 truncates from the tail section's start. run_independent_review.py:939 calls this on every run.",
      "failure_scenario": "The author answers the last attempt and quotes a heading inside an indented fence, or a fence such as ```` ```python title ````, or writes a line `### Attempt notes`. The next launcher run on that record silently deletes the whole answers section, from that line to the end of the file. The check then reports missing answers, and the author's text is gone unless it was committed.",
      "file": "scripts/review_records.py",
      "id": "R1-5",
      "kind": "defect",
      "line": 176,
      "origin_stage": "implementation",
      "problem": "`truncate_unlogged_tail` deletes everything from the last unlogged `### Attempt <word>` line to the end of the file. `parse_record` treats any such line as an attempt heading unless it sits inside a fence that matches OPEN_FENCE exactly: no indent, and an info string of `[\\w-]*` only. The launcher's `answers_section` uses a different fence rule (`FENCE` allows indentation and any info string). The two parsers disagree on which lines are inside a fence, and recover acts on the stricter one destructively.",
      "severity": "medium"
    },
    {
      "evidence": "docs/slices/README.md:19; change.diff lines 200-204 update only the 4.1 and 4.2 rows. slice_4_decisions.md says the plans were merged (PR #48).",
      "failure_scenario": "The owner or the next agent reads the slice index (the authoritative status) and believes 4.3's plan is still unapproved, or that 4.3 has not started.",
      "file": "docs/slices/README.md",
      "id": "R1-6",
      "kind": "defect",
      "line": 19,
      "origin_stage": "implementation",
      "problem": "The slice index row for poc-4-3 still reads \"Plan under review (slice 4 plan PR)\". The plan was merged in PR #48, and 4.3 is implemented on this branch and under review. The 4.1 and 4.2 rows were updated in this change; 4.3's was not. The rows for 4.4 to 4.6 carry the same stale status, which predates this change.",
      "severity": "medium"
    },
    {
      "evidence": "slice_4_decisions.md, the 'Decided by the author during the run' table: 4.1 and 4.2 rows only. plan.md 'In scope' lists run_independent_review.py, check_review_records.py and check_docs.py.",
      "failure_scenario": "At the end review the owner cannot see which 4.3 behaviour came from the plan and which was the author's choice, which the goal's 'says in it what was decided on the owner's behalf' requires.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "R1-7",
      "kind": "defect",
      "line": 318,
      "origin_stage": "implementation",
      "problem": "The decision file records the author's 4.1 and 4.2 decisions taken on the owner's behalf, but none for 4.3, even though the change does things the plan did not name:\n- a new module, `scripts/review_records.py`, which the plan's in-scope list does not include (the matching 4.2 split into review_inputs.py was recorded);\n- the refusal of a task prompt without a final newline;\n- recover overwriting a withheld attempt's status line;\n- the reading of S43-D4's `owner:` link as a match anywhere in a rejected answer's text.",
      "severity": "low"
    },
    {
      "evidence": "test_check_review_records.py:100 reruns and checks only `_problems(fx) == []`, not the status text. EV1 line 149 is not run.",
      "failure_scenario": "A reader of the record cannot tell a withheld report from a killed launcher. The log still does not distinguish them either.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-8",
      "kind": "defect",
      "line": 963,
      "origin_stage": "implementation",
      "problem": "For a withheld attempt, the record first gets 'Status: withheld: the publication check found a secret\u2026'. On the next run, `recover` appends an `interrupted` end entry and `_complete_record` overwrites that status line with 'interrupted (no end entry: the launcher stopped, or the publication check withheld the report)', so the record loses the specific withheld status that S43-D1 asks for. `status_text`'s `end is None` branch (review_records.py:148-149) is also dead, since the only caller with None passes `withheld=True`.",
      "severity": "low"
    }
  ],
  "verdict": "no"
}
`````


#### Answers to implementation/c1/r1/A/2

| ID | Severity | Answer |
| --- | --- | --- |
| R1-1 | blocking | fixed: tests/tools/test_check_review_records.py: `test_docs_check_reports_the_record_problems_through_run_checks` replaces `check_records` with a planted problem and calls `run_checks` on the repository; the problem must appear in its output. With the `check_records` call removed from `run_checks`, this test fails (the author's hand mutation). Cause: the earlier test called `check_records` directly; searched the other `check_docs` checks for the same gap: each is called from `run_checks` and covered by `tests/tools/test_check_docs.py` |
| R1-2 | blocking | fixed: tests/tools/test_check_review_records.py, scripts/check_review_records.py: tests for a missing Prompt and a missing Evidence block, a label without a fenced block, an attempt heading twice, a label twice, an unclosed fence, a rejected finding that the next round re-raises, and an unreadable attempt log; the duplicate-label message now names the block as the others do. Hand mutations that skip a missing block, accept any completed next round, or ignore a duplicate heading each make a test fail. Cause: the tests were written from the plan's rows, not from the check's branches; the launcher's own evidence listed these lines, and the author had not acted on it |
| R1-3 | high | owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision concern 2): implemented within S43-D4's words, so a later round's `owner:` answer to the same finding ID (a re-raised finding keeps its ID) settles a rejected blocking or high finding without editing answers a recheck read; tests `test_rejected_finding_that_the_next_round_re_raises_still_fails` and `test_a_later_owner_answer_to_the_re_raised_finding_settles_the_rejection`. The owner confirms this reading or chooses another; the red check between the answers commit and the recheck stays, as the plan accepts |
| R1-4 | medium | fixed: scripts/review_records.py, scripts/run_independent_review.py, scripts/check_review_records.py, tests/tools/test_check_review_records.py: records are read and written as exact bytes and split on newlines only, `fenced` drops only one final newline, and the launcher reads the task as bytes; a task with CRLF line ends, a blank last line, two blank lines or a form feed now hashes as logged (`test_prompt_block_hashes_as_logged_whatever_the_task_files_line_ends`, four cases). Searched for other newline-translating reads of a record: the launcher's two record reads and the check's record and log reads; all changed |
| R1-5 | medium | fixed: scripts/review_records.py, scripts/run_independent_review.py, tests/tools/test_check_review_records.py: one fence rule (CommonMark: indent up to three spaces, any info string) serves the launcher's answers reader and the record parser, and recovery removes an unlogged trailing section only when it is exactly what the launcher writes before its start entry (the launcher's attempt-ID form, the started status, its Prompt and Evidence blocks, nothing after). Test: `test_text_that_is_not_a_launcher_section_is_never_removed` (three cases) and the updated truncation test |
| R1-6 | medium | fixed: docs/slices/README.md: the 4.3 row says it is implemented and in review; the 4.4 to 4.6 rows say their plans merged and they have not started |
| R1-7 | low | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: the 4.3 decisions made on the owner's behalf are recorded (the records module, the final newline and exact bytes, safe recovery, the withheld end entry, the reading of S43-D4, the schema problems in the reason) |
| R1-8 | low | fixed: scripts/run_independent_review.py, scripts/review_records.py, tests/tools/test_check_review_records.py, tests/tools/test_run_independent_review.py: a withheld attempt gets an end entry with status `withheld` (counts and paths only), so recovery no longer overwrites its status line; the dead branch of `status_text` is removed. Tests: `test_withheld_attempt_keeps_its_prompt_and_evidence_and_says_it_was_withheld`, `test_secret_in_the_reply_leaves_no_report_and_a_withheld_end_entry` |
