# Implementation review — 4.1 (#38), review prompts and severity order

Record of the implementation review of slice 4.1 in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- The task prompt of round 1 holds the author's self-review: seven questions the owner asked, answered with evidence, given to the reviewer as claims to verify.
- The launcher of the reviewed branch ran these reviews (slice 4.1's prompt sections, modes and `accounted`); a recheck lists each answer under `accounted`.

## Round 1

### Attempt implementation/c1/r1/A/1

Commit `6476697`, effort high. Files reviewed (SHA-256): `AGENTS.md` `ec46a6f6a720`, `scripts/run_independent_review.py` `12b2aee9eefe`, `scripts/run_review_benchmark.py` `cedaa43609d4`, `tests/tools/test_run_independent_review.py` `6fa194e51eab`, `tests/tools/test_run_review_benchmark.py` `d4f08554af98`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Implementation review of slice 4.1 (review prompt structure and severity order, issue #38)

## Intent

The approved plan and test plan are `docs/slices/poc-4-1-review-prompts/plan.md` (decisions S41-D1 to S41-D16)
and `docs/slices/poc-4-1-review-prompts/test_plan.md`. They were approved by the owner when plan PR #48 merged into
`poc/agentic-sdlc` (the base of this review). The plans quote the owner's words for each decision. Slice 4 is one
branch with six sub-issues (4.1 to 4.6); this review is of 4.1, the first. Later sub-issues fill sections that 4.1
only creates: 4.2 the upstream items, the evidence and the file list from the diff; 4.3 the record blocks and the
record check; 4.4 the stage checklists; 4.5 the benchmark's stage-B configurations and identity.

The change is in `_review_inputs/change.diff`. Besides 4.1, it holds two earlier commits of the branch that add
`docs/slices/agentic-sdlc-poc/slice_4_decisions.md` (the owner's decision file).

## The author's self-review (claims to verify, not facts)

The owner asked the author to answer seven questions with evidence before this review. The answers follow.

1. **Facts outside the repository, and how each was probed.**
   - Claude CLI: `claude --version` prints `2.1.321 (Claude Code)`; the plan's probe was 2.1.319. Whether the CLI's
     `--json-schema` accepts the new schema (enums holding spaces, such as `architecture and interfaces` and
     `cannot determine`, and the new `accounted` array) was not probed before this review; this review is its first
     live run. The launcher validates every reply against its own rules too, so a CLI that ignored the schema would
     give a failed attempt, not a released report.
   - Base branch: `git fetch origin poc/agentic-sdlc` then `git rev-parse origin/poc/agentic-sdlc` prints
     `3347754ef038…`.
   - Local tooling: `which shellcheck` finds nothing, and 9 tests of `tests/tools/test_lint_changed_files.py` fail
     without it, on the base too. The author extracted shellcheck 0.10.0 from the `shellcheck-py` 0.10.0.1 wheel
     into a scratch directory; with it on `PATH`, `make tooling-test` passes 498 tests.
2. **Each check added or changed, the case it catches, and the test that shows it fails on that case.** All in
   `tests/tools/test_run_independent_review.py` unless named otherwise.
   - Report schema (severity, origin stage, retired kinds, simpler alternative always low, `accounted` required,
     `cannot determine` with a note, `flagged` naming a finding): `test_report_outside_the_schema_fails_and_is_not_released`
     (eleven cases), with `test_findings_of_each_severity_kind_and_origin_stage_are_accepted` as the positive twin.
   - A re-raised finding keeps its ID: `test_re_raised_finding_keeps_its_id`.
   - Accounting (an answer left out, an opened file not read, a file a `fixed:` answer names not read, an evidence
     status for an answer): `test_recheck_that_does_not_account_for_every_answer_fails`, whose `control-complete` case
     is the twin; `test_fixed_file_that_was_not_read_fails_even_when_a_path_under_review_was`;
     `test_fixed_answer_naming_a_file_the_change_deletes_is_accepted_and_needs_the_diff_read`.
   - Answers the recheck cannot verify, refused before any call:
     `test_answer_the_recheck_cannot_verify_is_refused_before_any_call` (eight cases);
     `test_answers_table_with_every_answer_word_is_accepted` is the twin.
   - Recheck inputs missing or not matching: `test_recheck_without_its_inputs_is_refused_before_any_call` (its last
     step runs the same round with its inputs), `test_earlier_attempt_is_only_the_same_unit_count_and_label`,
     `test_empty_answers_section_is_refused`.
   - No option that changes the sections: `test_command_line_has_no_option_that_changes_the_sections` pins the
     parser's options.
   - Headings in quoted text passing for sections: `test_headings_in_the_task_text_or_the_rules_cannot_pass_for_prompt_sections`;
     the author ran it against the launcher of `59d0291` (before the fix): it failed there and passes now.
   - The mandate hash taken from the prompt's own configuration: `test_start_entry_records_the_mode_and_the_mandate_hash`
     failed on the author's first implementation (see 4).
   - Benchmark scoring: `test_new_report_counts_blocking_and_high_as_detections_and_blocking_only_apart` and
     `test_stage_a_results_are_read_as_before` in `tests/tools/test_run_review_benchmark.py`.
   - Hand mutation by the author: with the accounting check removed, 5 tests fail; with the `fixed:` path existence
     check, the simpler-alternative rule, the earlier report's hash check, the count filter of the earlier attempt,
     the opened-path check, or the check that a re-raised finding keeps its ID removed, 1 test fails each.
3. **Claims and what checks them mechanically.**
   - "The mandates verbatim": the constants in `MANDATES` were compared with the quoted texts of S41-D4 by a script
     (they are equal); `test_every_mode_holds_its_mandate_verbatim` checks that each prompt holds its constant.
   - "No launcher option removes or reorders a section": the parser test above.
   - "The task text appears only under Claims to verify": `test_task_text_appears_only_under_claims_to_verify`.
   - "A recheck never gets the review record": `test_recheck_prompt_holds_its_earlier_report_and_only_its_answers_section`
     (a marker elsewhere in the record never reaches the prompt; the record is not in the copy).
   - "Stage A's results are read as before": the test above, and `--report` on the repository's stage-A results
     gives output that differs from the base's only in the column header ("Advisory only" to "Not blocking").
   - Not checked mechanically: that `AGENTS.md`'s new sentences say what S41-D6, D7, D10, D11 and D12 decide; the
     test plan proves these by review.
4. **Fixes and their upstream choice.** No reviewer findings yet. The author found two defects while testing:
   - The start entry's mandate hash was computed apart from the prompt, and `build_prompt`'s default configuration
     was bound when the module loaded, so the two could differ. Changed the choice instead of adding a check: the
     launcher builds the prompt and takes the hash from the same configuration object.
   - Text from files or the author (the rules, the task text, the answers) was concatenated raw, so its own `## `
     headings read like the prompt's sections. Changed the choice: such text is now a fenced block, and the prompt
     says that its sections are the headings outside fenced blocks. No heading filter was added.
5. **Tried the way the next user runs it.** In a scratch clone of this repository at the reviewed branch, with the
   real base fetched from GitHub and the fake CLI from the tooling tests: two units of different bundles ran in
   parallel (round 1), then the author committed answers for both and ran both rechecks in parallel (round 2). Each
   recheck got its own answers only; the start entries hold the mode, the answers hash and the earlier attempt;
   prompts held no `/home` or `/tmp` path, and the evidence secret check found nothing in them. The heading problem
   of 4 was found this way. This review is the first run with the real CLI.
6. **Where each rule lives.** `AGENTS.md` (severity rules and blocking list with the secret rule, the answers table,
   the modes and the prompt-writing rules); the launcher's constants (`MANDATES`, `CREDENTIAL_NOTE`, `ABSENCE_RULE`,
   `GATE_RULE`) with the tests above; the slice-test-plan template (questions name the severity scale). The choice to
   review 4.1 with the branch's own launcher is in the decision file.
7. **What was removed, and its review.** Removed: the finding kinds `blocking` and `advisory` from new reports; the
   single-layout prompt; the rule "Everything else is advisory. It is listed once and is not fixed by default"; the
   report column "Advisory only" (renamed). `AGENTS.md` was searched for "advisory" and "blocking": every hit was
   rewritten to the severity scale except "authoritative or advisory" in the hidden-state rule, which is about the
   authority of state, not findings. Still present until 4.2 removes them: the optional `diff_base` of
   `make_frozen_copy` and `has_diff`, now a field of `PromptParts`.

## Questions (a minimum, from the test plan)

1. *Tests:* for each new or changed test, which wrong behaviour would still pass it? Does its assertion match its
   row in the test plan?
2. *Keys:* does a key, socket or secret now reach a service outside its holders? Can a secret or an operational
   detail reach the reviewer or a public record through the new sections, the recheck inputs, the answers section
   or the severity counts?
3. *Names and headers:* do new files and names say what they do (coding rule 8)?

Also: does every decision S41-D1 to S41-D16 have its implementation and proof (or, for rule text, its
`AGENTS.md` sentence), and does the change do anything no decision asked for?
```

#### Report

```json
{
  "accounted": [],
  "findings": [
    {
      "evidence": "`matched.update(... if is_detection(f))` (blocking or high) at line 266, but `result[\"unmatched_blocking\"] = [... if is_blocking(f) ...]` (blocking only) at line 267. `_add_score` counts `false_blockers` from `unmatched_blocking` only (line 570), and `decide` compares on it. `test_new_report_counts_blocking_and_high_as_detections_and_blocking_only_apart` checks only `detected`, `detected_blocking` and `not_blocking`; no test looks at a high finding on a clean case.",
      "failure_scenario": "In 4.5, configuration X gives every finding `high`. On defect cases each high at the right place with a term counts as detected. On CL-1, CL-2 and the decoy, its unmatched high findings count 0 false blockers, while a configuration that uses `blocking` is penalised. The comparison favours over-rating, which is the slanted comparison the plan's delivery threat model names.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R1-1",
      "kind": "defect",
      "line": 267,
      "origin_stage": "implementation",
      "problem": "New-schema scoring counts a `high` finding as a detection but not as a false blocker. A configuration that rates many findings high gets detection credit on defect cases and no penalty on clean cases.",
      "severity": "high"
    },
    {
      "evidence": "run_review_benchmark.py:589-603 (columns Detected, Location only, Not blocking, Unmatched blocking); compare_prompts at 543-554 has totals real_miss, planted, false_blockers. The test only asserts `score()` output.",
      "failure_scenario": "The owner reads `--report` to choose a setup and sees detections that mix blocking and high, with no blocking-only count. The decision S41-D13 promises is not visible in the report until someone counts it by hand from the JSONL.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R1-2",
      "kind": "defect",
      "line": 548,
      "origin_stage": "implementation",
      "problem": "S41-D13 says \"blocking-only counts are reported too\", and the test-plan row says \"the blocking-only count is reported too\". `score()` computes `detected_blocking`, but `--report` never shows it: `report_rows` has no column for it and `compare_prompts`/`_add_score` total only `detected`.",
      "severity": "medium"
    },
    {
      "evidence": "tests/review_benchmark/prompts/short.md:10-11 and checklist.md:22-24 still say kind blocking/advisory. The canary text was changed to \"low\", but these were not. build_case_prompt (line 361-368) now feeds them into launcher.build_prompt with the new schema.",
      "failure_scenario": "In 4.5 the `short+list` baseline gets contradictory instructions. Either the reviewer emits kind `blocking` and `validate_report` fails the attempt (counted as a failure or a miss), or it hesitates between the scales. The baseline is handicapped by its own wording, not by its design, which biases short+list against open+list.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R1-3",
      "kind": "defect",
      "line": 208,
      "origin_stage": "implementation",
      "problem": "`stage_a_configuration` puts stage A's prompt files in place of the initial mandate. Those files still tell the reviewer to \"Use the kind \\\"blocking\\\" ... everything else is advisory\", which contradicts the new schema (those kinds are retired and rejected) and the new severity rules in the same prompt's Output section. S41-D13 says no retired word is left in use, and S45-D3 requires every configuration to get the same severity rules.",
      "severity": "medium"
    },
    {
      "evidence": "plan_reviews builds `Accounting({row.finding: ...})` from the rows only (line 1208). The answer severity is parsed (answer_rows) but never used. AGENTS.md:83 says \"answers every finding ... one table row per finding\" and :88-89 limits blocking/high to fixed/rejected/owner. The plan defers enforcing the table to 4.3's record check, which does not exist yet while 4.2 and 4.3 are reviewed with this launcher.",
      "failure_scenario": "The author answers X1 and X2 but forgets X3, a blocking finding. The recheck prompt says \"List each of these findings under `accounted`: X1, X2\". The reviewer accounts for both and returns yes, the launcher completes the attempt, and X3 silently drops out of the review loop until 4.3's check exists. Comparing the row IDs and severities with `recheck.earlier_report` is a few lines on data already loaded.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-4",
      "kind": "defect",
      "line": 1071,
      "origin_stage": "implementation",
      "problem": "`check_answers` checks each answer row's form but never compares the rows with the earlier report it has already loaded. A finding of the earlier report with no row is never listed for accounting. A row for an ID the report does not hold is accepted. A row whose severity cell differs from the report's (for example blocking relabelled low, then `deferred:`) is accepted. Nothing refuses `deferred:` on a blocking or high finding either, which AGENTS.md now forbids.",
      "severity": "medium"
    },
    {
      "evidence": "check_answers adds must_read only for word == fixed. The test case `control-complete` accepts `opened=()`. AGENTS.md:92 names \"already covered by a named test or gate\" as a valid rejection reason, which is exactly the answer that names a file.",
      "failure_scenario": "The author rejects a high finding with \"covered by tests/tools/test_run_independent_review.py::test_z\", but the test does not exist or does not assert the case. The recheck accepts it without opening the file, and the launcher completes the attempt. This repeats the slice-2 round-4 failure for rejections. For the owner: extend must_read to any copy path named in any answer.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-5",
      "kind": "decision_concern",
      "line": 1084,
      "origin_stage": "architecture and interfaces",
      "problem": "S41-D8 enforces reads only for files a `fixed:` answer names. A `rejected:` answer that rests on files (\"already covered by tests/tools/test_x.py::test_y\") can be accepted with `opened: []`, and nothing checks it. Yet the plan's threat model lists \"a recheck that accepts an answer without opening the files it names\", and the recheck mandate says to open \"the tests that cover them\".",
      "severity": "medium"
    },
    {
      "evidence": "A grep of slice_4_decisions.md for launcher/4.1 finds only line 21 (\"when to use the new launcher on later sub-slices\", which delegates the choice for *later* sub-slices), line 23, and the 4.1 rows of the tables. Lines 271-277 say \"None yet\" under parked units and decision concerns, and under discovered issues. The goal (line 213) requires this page to hold every discovered issue and what was decided on the owner's behalf.",
      "failure_scenario": "At the end review the owner reads this one page and does not learn that 4.1 was reviewed by the launcher under review, a circular check. The page also lists no discovered issues, so the shellcheck problem and the author-found defects never reach the PR body, contrary to the Discovered-issues rule.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "R1-6",
      "kind": "defect",
      "line": 10,
      "origin_stage": "implementation",
      "problem": "The self-review (answer 6) claims \"The choice to review 4.1 with the branch's own launcher is in the decision file\". The file does not record it. It also still says \"Last updated: 2026-11-09, before the implementation starts\" and \"Discovered issues: None yet\", although 4.1 is implemented and the self-review reports discovered issues: shellcheck is missing locally and 9 lint tests fail without it, on the base too; and the author found two launcher defects.",
      "severity": "high"
    },
    {
      "evidence": "Slice 2's fix A1 (review_slice_2.md:601) made the rebuild use `has_diff` from the entry; this change drops that. `test_invocation_from_an_entry_logged_before_slice_4_1_reports_a_mismatch_not_a_crash` only asserts that `full_prompt_sha256` is among the mismatches. plan.md:132-138 retires only the kinds, the single layout and the rule sentence.",
      "failure_scenario": "Someone checks a slice-2 or slice-3 attempt with invocation_from_entry, gets full_prompt_sha256 and mandate_sha256 mismatches, and reads them as evidence that the logged prompt was tampered with or is stale. In fact the tool can no longer rebuild that layout. The retirement should be stated, or the mode-less path should report \"pre-4.1 entry: prompt not rebuildable\".",
      "file": "scripts/run_independent_review.py",
      "id": "R1-7",
      "kind": "defect",
      "line": 1399,
      "origin_stage": "implementation",
      "problem": "`invocation_from_entry` can no longer rebuild any start entry logged before 4.1, because the prompt layout changed, mandate_sha256 is absent and has_diff is no longer taken from the entry's diff_sha256. The plan's retirement section does not say this capability ends (\"Nothing else is retired\"). The `entry.get(\"mode\", \"initial\")` fallback suggests compatibility it does not give.",
      "severity": "medium"
    },
    {
      "evidence": "`if len(cells) != 3 or set(cells[0]) <= set(\"-: \") or cells[0].lower() == \"id\": continue`. AGENTS.md:83-85 gives only `| <finding id> | <severity> | <answer> |`. The test helper always writes `| ID | Severity | Answer |`.",
      "failure_scenario": "An author writes the table with a `Finding` or `Finding ID` header column. The recheck is refused before any call, with an error naming a finding \"Finding\" that does not exist, and the author has to guess that the header is the problem. This fails closed but is hard to diagnose. Either name the header in AGENTS.md or skip the row above the separator.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-8",
      "kind": "defect",
      "line": 1021,
      "origin_stage": "implementation",
      "problem": "`answer_rows` skips a header row only when its first cell is exactly `ID`. AGENTS.md defines the row format but no header. A natural header such as `| Finding | Severity | Answer |` is parsed as an answer, and the round is refused with a misleading message (\"answer to Finding does not start with fixed:, ...\").",
      "severity": "medium"
    },
    {
      "evidence": "The answer is `fixed: scripts/review_me.py`, reads are AGENTS.md and tests/unit/AGENTS.md, and the expected reason is the confinement message. The must_read check is covered separately by `test_fixed_file_that_was_not_read_fails_even_when_a_path_under_review_was`.",
      "failure_scenario": "A reader of the parametrised test thinks it proves the fixed-file check. If the separate test were later removed, removing the must_read check would still pass this case.",
      "file": "tests/tools/test_run_independent_review.py",
      "id": "R1-9",
      "kind": "defect",
      "line": 1005,
      "origin_stage": "tests first",
      "problem": "The case `fixed-file-not-read` of `test_recheck_that_does_not_account_for_every_answer_fails` does not exercise the fixed-file read check. Its fixed file is the path under review, so the attempt fails earlier on the confinement check, and the expected reason is \"the review read none of the paths under review\".",
      "severity": "low"
    },
    {
      "evidence": "A grep for a caller of answer_format_problem outside run_independent_review.py finds none.",
      "failure_scenario": "A reader assumes docs-check already enforces the answer format on records and skips checking records by hand.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-10",
      "kind": "defect",
      "line": 1044,
      "origin_stage": "implementation",
      "problem": "The docstring says \"the launcher and the record check share this rule\", but no record check exists yet (it comes in 4.3). The docstring states as fact something not yet true.",
      "severity": "low"
    },
    {
      "evidence": "`_seen_below_detection` uses `not is_detection(f)`, so high is excluded. S41-D13 picked the name, so this is a naming note.",
      "failure_scenario": "The owner reads \"Not blocking: (empty)\" and concludes that every match was rated blocking, when they were high.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R1-11",
      "kind": "defect",
      "line": 591,
      "origin_stage": "implementation",
      "problem": "The column renamed \"Not blocking\" holds only medium and low matches. A `high` match is also not blocking, but it appears under \"Detected\". The column name says something different from what the column contains.",
      "severity": "low"
    },
    {
      "evidence": "AGENTS.md:97 \"disputed after that goes to the user, who decides. A fix goes to the origin of the problem, and the author searches for the\".",
      "failure_scenario": "Style only.",
      "file": "AGENTS.md",
      "id": "R1-12",
      "kind": "defect",
      "line": 97,
      "origin_stage": "implementation",
      "problem": "The reflow left one line far longer than the rest (about 130 characters) in the Review loop paragraph.",
      "severity": "low"
    },
    {
      "evidence": "docs/slices/README.md:17.",
      "failure_scenario": "A reader of the index thinks 4.1 is not approved. This is expected to be fixed at slice 4's close-out, so it is listed for the final PR.",
      "file": "docs/slices/README.md",
      "id": "R1-13",
      "kind": "defect",
      "line": 17,
      "origin_stage": "implementation",
      "problem": "The slice index row for poc-4-1-review-prompts still says \"Plan under review (slice 4 plan PR)\", although the plan merged (PR #48) and the implementation is done.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to implementation/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| R1-1 | high | fixed: scripts/run_review_benchmark.py, tests/tools/test_run_review_benchmark.py: `score()` adds `unmatched_detections` (blocking or high findings at no expected place), and the totals count them on clean cases as `false_alarms`; `false_blockers` stays blocking-only. Cause: detection was widened to high while the penalty kept stage A's blocking-only rule. Searched for the same asymmetry in `_add_score`, `compare_prompts`, `report_rows` and `decide`: `decide` still compares blocking-only false blockers, which is stage A's committed rule, and 4.5a replaces it with S45-D8's report. Test: `test_unmatched_high_finding_on_a_clean_case_is_a_false_alarm_not_a_false_blocker` |
| R1-2 | medium | fixed: scripts/run_review_benchmark.py, tests/tools/test_run_review_benchmark.py: the report table gains the columns "Detected (blocking)" and "Unmatched (blocking or high)" and a note on what each column holds, and the totals gain `real_miss_blocking`, `planted_blocking` and `false_alarms`. Stage A's rows read their stored scores as before (every stage-A detection was by a blocking finding); the regenerated stage-A report keeps every earlier value and decision. Test: `test_report_shows_blocking_only_detections_beside_all_detections` |
| R1-3 | medium | deferred: #42: 4.5a (issue #42) builds stage B's `short+list` configuration from stage A's short prompt, and is where its output sentence must name the severity scale instead of the retired kinds; stage A's prompt files stay as they were measured, since their hash is part of stage A's results. Recorded as discovered issue 2 in the decision file |
| R1-4 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py: `answer_table_problems` compares the answers table with the earlier report before any call: a finding without exactly one row, a row for an unknown ID, a severity cell that differs from the finding's, and an answer the severity or kind does not allow are refused (exit 2). One function holds the rule, for 4.3's record check to use. Cause: the plan put table enforcement only in 4.3, after rechecks start using answers; searched for other rules deferred to 4.3 that rechecks depend on before it: only the hash binding of the answers section, which needs 4.3's record blocks. Test: `test_answers_that_do_not_answer_the_earlier_report_are_refused_before_any_call` (six cases) |
| R1-5 | medium | owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision concern 1): S41-D8 limits the read check to files a `fixed:` answer names; extending it to every path any answer names changes an approved decision, so it is implemented as written and put to the owner with the recommendation to extend it |
| R1-6 | high | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: the page now records its last update, the progress of 4.1, every decision the author made on the owner's behalf (among them that 4.1's review runs with the branch's launcher, and why the circularity is limited), the decision concern of R1-5, and the discovered issues (shellcheck missing locally, stage A's prompt words, and the two defects the author found) with their dispositions |
| R1-7 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py, docs/slices/agentic-sdlc-poc/slice_4_decisions.md: `invocation_from_entry` raises a `ValueError` saying that an entry logged before 4.1 has a retired prompt layout and cannot be rebuilt, instead of reporting mismatches; the retirement is recorded in the decision file. Test: `test_invocation_from_an_entry_logged_before_slice_4_1_says_its_layout_is_retired` |
| R1-8 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py: `answer_rows` treats the row above a separator row as the header, whatever it says. Test: `test_any_header_row_above_the_separator_is_skipped` |
| R1-9 | low | fixed: tests/tools/test_run_independent_review.py: the case is renamed `nothing-under-review-read`, with a comment that the fixed-file check has its own test |
| R1-10 | low | fixed: scripts/run_independent_review.py: the docstring says that 4.3's record check is to share the rule |
| R1-11 | low | fixed: scripts/run_review_benchmark.py: the name stays as S41-D13 decided; the report's column note says that "Not blocking" holds matches rated medium or low, and that a high match counts as detected |
| R1-12 | low | fixed: AGENTS.md: the line is reflowed |
| R1-13 | low | fixed: docs/slices/README.md: the 4.1 row says the plan merged and the implementation is in review on the slice 4 branch |

## Round 2

### Attempt implementation/c1/r2/A/1

Commit `1be4a84`, effort medium. Files reviewed (SHA-256): `AGENTS.md` `9e7e2bd62bbe`, `docs/slices/agentic-sdlc-poc/slice_4_decisions.md` `a2d323559af7`, `scripts/run_independent_review.py` `3f446a4c3e6d`, `scripts/run_review_benchmark.py` `60aabc083dee`, `tests/tools/test_run_independent_review.py` `671a2e602f0c`, `tests/tools/test_run_review_benchmark.py` `e0812f2de8ab`.

Status: failed (the report does not account for what it was given: R1-3 names an opened file the attempt did not read; R1-5 names an opened file the attempt did not read; R1-6 names an opened file the attempt did not read; R1-7 names an opened file the attempt did not read; R1-12 names an opened file the attempt did not read).

#### Prompt

```markdown
# Recheck of slice 4.1's implementation (issue #38), round 2

The intent is unchanged from round 1: the approved plan and test plan of `docs/slices/poc-4-1-review-prompts/`
(decisions S41-D1 to S41-D16), merged into `poc/agentic-sdlc` by plan PR #48. Round 1 reviewed commit `6476697`; the
author's answers to its report, below, were committed in `1be4a84`, the reviewed commit. The change from the base is in
`_review_inputs/change.diff`; the round-1 fixes are the part of it that `1be4a84` adds.

The answers name the files each fix touched and the tests that cover it. One finding (R1-5) is a decision concern that
the author put to the owner in the decision file, and one (R1-3) is deferred to slice 4.5a under issue #42.
```

### Attempt implementation/c1/r2/A/2

Commit `9413020`, effort medium. Files reviewed (SHA-256): `AGENTS.md` `9e7e2bd62bbe`, `docs/slices/agentic-sdlc-poc/slice_4_decisions.md` `d3e9576818eb`, `scripts/run_independent_review.py` `6e6d2050c834`, `scripts/run_review_benchmark.py` `60aabc083dee`, `tests/tools/test_run_independent_review.py` `ecf5aea2b9f9`, `tests/tools/test_run_review_benchmark.py` `e0812f2de8ab`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Recheck of slice 4.1's implementation (issue #38), round 2

The intent is unchanged from round 1: the approved plan and test plan of `docs/slices/poc-4-1-review-prompts/`
(decisions S41-D1 to S41-D16), merged into `poc/agentic-sdlc` by plan PR #48. Round 1 reviewed commit `6476697`; the
author's answers to its report, below, were committed in `1be4a84`. The reviewed commit, `9413020`, also states in the output section that only a Read opens a file, after the first attempt of this round listed grepped files under `opened`. The change from the base is in
`_review_inputs/change.diff`; the round-1 fixes are the part of it that `1be4a84` and `9413020` add.

The answers name the files each fix touched and the tests that cover it. One finding (R1-5) is a decision concern that
the author put to the owner in the decision file, and one (R1-3) is deferred to slice 4.5a under issue #42.
```

#### Report

```json
{
  "accounted": [
    {
      "item": "R1-1",
      "note": "score() now records unmatched_detections (blocking or high, line 269); _add_score totals them as false_alarms on clean cases (line 582) and keeps false_blockers blocking-only. The new test puts a high finding on a clean case and asserts false_alarms 1 and false_blockers 0 (for blocking, 1 and 1). decide() still compares blocking-only false blockers. That is stage A's committed rule, and the answer says 4.5a replaces it, so I accept it.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/tools/test_run_review_benchmark.py"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-2",
      "note": "report_rows has new columns 'Detected (blocking)' and 'Unmatched (blocking or high)', and COLUMN_NOTE says what each column holds. TOTALS gain real_miss_blocking, planted_blocking and false_alarms. The test checks that a high match shows under Detected but not under Detected (blocking), that the note is in the report, and that real_miss_blocking is 0.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/tools/test_run_review_benchmark.py"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-3",
      "note": "The finding is medium, so deferred is allowed. It is tracked under #42 (4.5a builds short+list) and recorded as discovered issue 2 in the decision file. Keeping the stage-A prompt files as they were measured is a sound reason, since their hash is part of stage A's results.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-4",
      "note": "answer_table_problems (lines 1079-1104) refuses five cases: a finding with no row, a finding with more than one row, a row for an unknown ID, a severity cell that differs from the finding's, and an answer the severity or kind does not allow (deferred on blocking or high; anything but owner on a decision concern). The launcher calls it before any reviewer call and exits 2 (line 1255). The six parametrised cases cover each rule and assert one call (the version probe) only.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-5",
      "note": "This is a decision concern. It was answered owner: with a link to the decision file, where it is recorded as decision concern 1 with the recommendation to extend the read check. Implementing S41-D8 as written until the owner decides is correct under the rules.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-6",
      "note": "The decision file now has a current 'Last updated' line and a Progress table. It records the author's decisions, including the choice to review 4.1 with the branch's launcher and why that circularity is limited. It also lists decision concern 1 and the discovered issues with their dispositions: shellcheck, the stage-A prompt words, and the author-found defects (now 5 entries).",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-7",
      "note": "invocation_from_entry now raises a ValueError for an entry with no mode field; the message says the pre-4.1 layout is retired (lines 1450-1452). The test strips mode and mandate_sha256 from a real entry and expects that message. The retirement is recorded in the decision file (row at line 102).",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-8",
      "note": "answer_rows now skips the row above any separator row, whatever it says, and also skips the separator. The test uses a '| Finding | Severity | Answer |' header with an aligned separator.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-9",
      "note": "The case is renamed nothing-under-review-read. A comment points to the separate test that covers the fixed-file read check.",
      "opened": [
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-10",
      "note": "The answer_format_problem docstring now says that slice 4.3's record check is to share this rule, rather than claiming it already does.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-11",
      "note": "The column name stays as S41-D13 decided. COLUMN_NOTE says that Not blocking holds matches rated medium or low, and that Detected includes high matches.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-12",
      "note": "The Review loop paragraph in AGENTS.md (lines 78-101) is now reflowed to consistent line widths.",
      "opened": [
        "AGENTS.md"
      ],
      "status": "accepted"
    },
    {
      "item": "R1-13",
      "note": "The 4.1 index row now reads 'Plan merged (PR #48); implemented on the slice 4 branch, in review; final PR pending'.",
      "opened": [
        "docs/slices/README.md"
      ],
      "status": "accepted"
    }
  ],
  "findings": [],
  "verdict": "yes"
}
```
