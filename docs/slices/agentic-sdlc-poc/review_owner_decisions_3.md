# Review record — agentic-sdlc-poc, unit `owner-decisions-3`

The record of the review unit `owner-decisions-3`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt owner-decisions-3/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `5f5b404c17f7`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Review of round 4 of slice 4: the review mandates and the runner fixes (2026-11-17)

## Intent

After round 3, the owner accepted decisions 1, 3, 4 and 5, asked to revisit decision 2 and to fix discovered issues
56, 57 and 60 ("Decision 1, 3, 4  and 5 - accept, I want to revisit the decision 2 again, fix the issue 56, 57 and
60."). Revisiting decision 2, the owner proposed new initial, recheck and final mandates and found that the
recommendation had not drawn on industry research. After two research passes the owner approved the texts, a
benchmark budget of 120 and the criterion of R4-4: "approve the texts, budget 120, criterion fine." The approved
intent is the decision page `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`, section "Round 4: the review
mandates and the runner fixes (2026-11-17)": R4-1 (the three mandates, verbatim, with the author's stated changes to
the owner's texts), R4-2 (the research record), R4-3 (the fixes, tests first, issue 56 before the runs), R4-4 (the
measurement, its 19 calls and its criterion fixed before any run; the results are reported, not tuned, and if the
criterion fails the owner decides), R4-5 (the final mandate drops "What did everyone before you miss?", and
`AGENTS.md`, Final review, changes with it) and R4-6 (this unit); with the rows of "Decisions to make" decided on
2026-11-17. The owner was away while the work after the decision page was done and has not seen it.

The change is the commits after `96e3b22` (the end of round 3's review) up to the reviewed commit:
- discovered issue 60, git file lists that keep non-ASCII names (`8ab80e5`);
- discovered issue 57, the quote rule that removes quoted parts of a planted line, applied by stage A's rescore
  (`4fb578d`);
- the owner's decisions recorded on the decision page (`f5321cc`);
- discovered issue 56, a case run again under another prompt replacing its earlier line in stage B's counts, with
  the stage-B rescore refreshed (discovered issue 61) (`02281b0`);
- the benchmark report and the decision page after that fix, with new discovered issues 62 and 63 (`ebdb0e8`);
- the research record in `docs/slices/poc-4-4-stage-checklists/research.md`, section "Review prompt" (`90a15ed`);
- the benchmark configurations `open-R4+list` and `recheck-R4`, the answer key's version 8, the budget of 120 and
  decision concern 19, recorded before the runs (`831b47a`);
- the 19 runs' results (`660f57b`), the export of their detections (`78116f7`), the blind verdicts, the counts, the
  criterion's outcome and the new decision 8 (`6add324`), all in `docs/slices/poc-4-5-benchmark/` and on the
  decision page;
- the launcher's `MANDATES` (recheck and final) and `AGENTS.md`, Final review and the stage table (`1f905a9`);
- the records: the decision page, `docs/history/implementation_log.md`, `docs/STATUS.md`, `docs/slices/README.md`
  and the benchmark report (`5f5b404`).

The work up to `96e3b22` was reviewed in its own units. This is the initial review of the unit `owner-decisions-3`.

## The author's self-review (claims to verify, not facts)

1. **What was built.**
   - R4-1 and R4-4: the recheck and final mandates in `MANDATES` are R4-1's texts word for word; the initial mandate
     stays 4.1's, because R4-1's initial wording did not meet R4-4's criterion (below), and decision 8 asks the
     owner what to do with it.
   - The launcher's recheck prompt is byte for byte the prompt `recheck-R4` measured (same prompt identity on RC-1 to
     RC-4).
   - R4-5: `AGENTS.md`, Final review, describes round 4's final mandate and no longer names the question; S46-D5
     stays recorded in its frozen plan.
   - R4-3, discovered issue 60: the git file lists the review tooling reads keep non-ASCII names and spaces.
   - R4-3, discovered issue 57: a quoted span of at least the quote minimum found verbatim in an expected line is
     removed before terms are matched, the reviewer's own words never; one helper serves stage A's and stage B's
     rescore.
   - R4-3, discovered issue 56: stage B's counts take each case's last line per configuration and run
     (`current_lines`), so R2-9's recheck counts read 3 of 3 for both earlier wordings; `load_results`, the
     per-review rows, the origin table and the question line are unchanged.
   - R4-4: two configurations whose mandate files hold R4-1's initial and recheck texts, the key version 8 naming
     version 7's hash, and the stage-B hard stop `BUDGETS["B"]` and the key's `budget:` both 120.
2. **Facts outside the repository.**
   - The leak check of R4-4, run before any call, compared the three wordings with every case's task, patch and
     answers and found no case's words in them; it found the scorer's substring match of `proved` inside `approved`
     (discovered issue 62).
   - The 19 runs: calls 87 to 105 of 120, one try each, on the pinned CLI 2.1.323, about USD 13.6 by the runs' own
     estimates, with a run budget of 105 so no call beyond the approved 19 could start. FS-1's report was withheld by
     the publication check, as its earlier `open+list` run was, and counts as failed.
   - The 85 new detections (M153 to M237) were judged blind by two fresh sessions, each given a directory holding
     only half the exported rows and the committed match rule, with a prompt that asked them to apply the rule; 20
     match. A first pair of sessions was stopped before writing anything because its prompt added a test beyond the
     match rule. The verdict rows' `expected_id` was set to null on no-match rows, as the earlier rows hold it.
   - This review runs on the installed CLI 2.1.326.
3. **The criterion, as fixed before the runs.**
   - The initial wording, under R2-9: 10 of 11 defect cases against `open+list`'s 8, and 8 false alarms against 7
     in 4 no-defect reviews (one more medium finding on CL-2), so it does not ship; under blocking or high (computed
     from the confirmed matches, no report row) 9 against 7 and 2 false alarms each.
   - The recheck wording: RC-1, RC-3 and RC-4 re-raised and confirmed, RC-2's answers accepted, so it ships.
   - Decision concern 19: every `open+list` line ran under CLI 2.1.321, key version 2 and the launcher's prompt
     sections of that time, so the initial comparison differs in more than the mandate.
4. **Checks added or changed, and their tests.**
   - The tests each fix names in `tests/tools/test_review_inputs.py`, `tests/tools/test_check_docs.py`,
     `tests/tools/test_review_brief.py`, `tests/tools/test_run_independent_review.py`,
     `tests/tools/test_stage_rules.py` and `tests/tools/test_run_review_benchmark.py`.
   - The tests that pin the mandates: `test_the_round_4_configurations_send_r4_1s_mandates_verbatim` and
     `test_the_launcher_ships_r4_1s_recheck_and_final_mandates`, both reading R4-1's text from the decision page.
   - Each new test's first failure on the code before its change is in the commit bodies or the implementation log
     entry of 2026-11-18; the twins that pass on the base by design are named there.
5. **Claims checked mechanically.**
   - Locally at the last code commit and after the records: `make tooling-test` (1000 passed; shell 9),
     `make docs-check`, `make lint`, `make qa-trace` and `make gate-consistency` passed.
   - After `02281b0`, the stage-B report changed only in the rows the fix predicts, and the refreshed rescore differs
     only in the key hash.
   - The dry runs passed for 19 of 19 cases (85 prompts).
   - Not run: the E2E suite (no runtime change), `make unit-trust`, `make unit-mutation`, `make unit-diff-cov`, and
     CI (the branch is not pushed).
   - Not mechanical: the mandates' agreement with the decision page beyond the pin tests, the research record's
     quotes against their sources, and the blind verdicts.
6. **Fixes and their upstream choice.**
   - Discovered issues 56, 57 and 60 are fixed at their cause, without a new check.
   - Discovered issues 62, 63 and 64 are reported, not fixed.
7. **Where each rule lives.**
   - `MANDATES` in `scripts/run_independent_review.py`; `AGENTS.md`, Final review.
   - The runner's `BUDGETS` and the key's `budget:`; the configurations' prompt files under
     `tests/review_benchmark/prompts/`.
   - The research record; the decision page.
8. **What was removed.**
   - 4.1's recheck and final mandates; the final question in `AGENTS.md`.
   - Stage B's double counting of a case run again under another prompt.

Known and put to the owner on the decision page: decision 8 (the initial wording), decision concern 19, discovered
issues 62 to 64, decision concern 16 (fresh-session blind verdicts), growth proposal 12; no case measures the final
wording.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 256, 1276, 1334-1335; branches not taken: 1275->1276, 1952->1954 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/run_review_benchmark.py: changed lines not run: 361, 408, 741, 985, 1305, 1855-1856; branches not taken: 360->361, 364->363, 407->408, 499->503, 740->741, 910->907, 916->910, 983->985, 1034->1037, 1286->1284, 1854->1855 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_inputs.py: changed lines not run: 316; branches not taken: 315->316 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/check_review_records.py: changed lines not run: 48, 227-230, 234; branches not taken: 47->48, 228->229, 228->230, 233->234 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/review_brief.py: changed lines not run: 43, 304, 308; branches not taken: 42->43, 236->229, 307->308 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/lint_changed_files.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "Not from round 4. Lines 256 (module loader's `spec is None` guard), 1276 (record_text without a record), 1334-1335 (`except ValueError: return` in `_complete_record`; its docstring leaves a missing section to the record check) and the HOME branch 1952->1954 are defensive or environment branches from earlier units (4.1 to 4.3). Round 4's launcher change (MANDATES) is pinned by test_the_launcher_ships_r4_1s_recheck_and_final_mandates.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "Line 361 (an expected file missing in the copy), 408 (a case without a list), 741 (record without a sink), 985 (a refused case already recorded), 1305 (the no-defect total in stage A's scorer) and 1855-1856 (the `--sample-confirmation` dispatch, already open in part as discovered issue 53) are edge or dispatch paths. None of them is the issue 56 or 57 code: `current_lines` and `_without_quoted_parts` are run by the tests at test_run_review_benchmark.py:1198-1221 and :1753-1789.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/tools/test_run_review_benchmark.py",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Line 316 is `_link_user_site` returning early when the interpreter has no user site-packages, an environment branch of the evidence scratch. Not changed by round 4.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "Line 215 is check_docs' loader failure for check_review_records.py, a defensive branch. Round 4's change in this file (tracked_files with core.quotePath=false) is run by test_images_unreferenced_render_with_a_non_ascii_name_is_reported.",
      "opened": [
        "scripts/check_docs.py",
        "tests/tools/test_check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Lines 48 (loader guard), 227-230 and 234 (`main` and the `__main__` entry) run only as a subprocess, which in-process coverage does not see (issue #44). Not round 4 code.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "Lines 43 (loader guard), 304 and 308 (`main`'s success return and the `__main__` entry, run as a subprocess) and the branch 236->229 (an accounted status that is none of the three) are defensive branches. Round 4's change in this file (changed_logs) is run by test_changed_logs_keep_non_ascii_names_and_spaces_whatever_the_repository_configures.",
      "opened": [
        "scripts/review_brief.py",
        "tests/tools/test_review_brief.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "The untaken branches 189->191 (a section without a status line) and 228->230 (no round heading before a truncated tail) are record-writing edge cases from slice 4.3, not round 4.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "There is no CI run because the branch is not pushed. The author says so (\"Not run: ... CI (the branch is not pushed)\", implementation_log.md:107-109). No gate result is claimed from CI, and the CI jobs must still pass on the PR before the user merges.",
      "opened": [
        "docs/history/implementation_log.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "slice_4_decisions.md:855 (issue 56: \"the original A/2 and the first replay accepted the answer\"; the stage-B counts change from 6 of 7 to 3 of 3); delivery_problem_log.md:577-616 (DPL-014, same rerun-under-new-identity cause, lesson about keys only); the handoff rule (approved AGENTS.md step 4) requires DPL entries for a review miss or false claim found or fixed. Same-cause site the fix does not mention: `_completed_reviews` (scripts/run_review_benchmark.py:1281-1288) still keys by case and configuration and keeps the first completed line, the opposite of `current_lines` (:1688-1695).",
      "failure_scenario": "The owner reads the delivery problem log to learn which misses happened and how they were prevented. It does not show that two rechecks accepted a fix that left the benchmark's recheck counts inflated, or that those inflated counts went into decision 2's options. The next change that keys benchmark results by case and configuration (for example a new export through `_completed_reviews`) repeats the cause, and nothing records it as a known lesson.",
      "file": "docs/delivery_problem_log.md",
      "id": "F1",
      "kind": "defect",
      "line": 577,
      "origin_stage": "implementation",
      "problem": "docs/delivery_problem_log.md has no entry for discovered issue 56, and the issue 56 fix does not say where the author looked for the same cause. Searched DPL-001 to DPL-014 for \"issue 56\", \"H1\", \"double\", \"current_lines\", \"first run\" and \"recheck-A\". Issue 56 is a review miss: two rechecks (A/2 and the first mechanics replay) accepted a fix that left stage B double-counting reruns. It is also a false number given to the owner: decision 2's options quoted the runner's `recheck-A` 6 of 7 and `recheck-B` 3 of 4, and the true figures are 3 of 3 and 3 of 3. It shares its root with DPL-014: results keyed by case and configuration, with no allowance for a rerun under a new prompt identity. DPL-014's corrective action fixed only the token key. Round 4 fixed issue 56 without widening DPL-014's lesson or opening a new entry.",
      "severity": "medium"
    },
    {
      "evidence": "benchmark_report.md:576-579 (\"two fresh sessions, each given a folder holding only half of the export and the committed match rule and asked only to apply the rule to each line, opened nothing else and found 20 matches\"); implementation_log.md:51-52 and slice_4_decisions.md:742-744 say the same. A Grep of docs/**/*.md for \"expected_id\", \"first pair\" and \"stopped before\" finds nothing about either fact. rescore_confirmation.jsonl:153-159 shows `\"expected_id\": null` on the new no-match rows.",
      "failure_scenario": "The owner decides decision 8 and decision concern 16 (whether fresh-session blind verdicts count) from the report and the decision page. They believe the committed verdicts are the sessions' untouched output from a single prompt. A later audit that compares the sessions' transcripts with the committed file finds rows the author changed and an earlier confirmation attempt, with no record of either. The blindness claim, which is the measurement's evidence, cannot be checked from the repository.",
      "file": "docs/slices/poc-4-5-benchmark/benchmark_report.md",
      "id": "F2",
      "kind": "defect",
      "line": 576,
      "origin_stage": "implementation",
      "problem": "The records of R4-4's blind confirmation leave out two facts that the task text states. (1) A first pair of confirmer sessions was started with a prompt that added a test beyond the match rule, then stopped. (2) After the sessions wrote their verdicts, the author edited the verdict rows, setting `expected_id` to null on the no-match rows. The benchmark report, the decision page and the implementation log all describe the 20 matches as the output of two fresh sessions that were asked only to apply the rule. The committed `rescore_confirmation.jsonl` is therefore not the sessions' raw output, and the repository does not say so.",
      "severity": "medium"
    },
    {
      "evidence": "slice_4_decisions.md:730 \"19 calls (86 to 105 of the 120 now allowed)\"; scripts/run_review_benchmark.py:69 \"86 were spent before it\"; docs/STATUS.md:18 \"86 of 95 in round 3, and 105 of 120 in round 4\".",
      "failure_scenario": "Someone reconciling the call budget from the decision page counts 20 approved calls and believes one call is unaccounted for, or that call 86 belonged to round 4.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "F3",
      "kind": "defect",
      "line": 730,
      "origin_stage": "implementation",
      "problem": "R4-4 says the 19 calls are \"86 to 105 of the 120\". That range holds 20 numbers, and 86 calls had already been spent before round 4. The 19 calls are numbers 87 to 105, as the task text says.",
      "severity": "low"
    },
    {
      "evidence": "slice_4_decisions.md:766 \"| (a), the owner's decision: the excess is one medium finding ...\"; compare :759-765 \"Decided by the owner on 2026-11-17 ...\".",
      "failure_scenario": "The owner, who was away, or a later agent skims the decisions table and reads decision 8 as decided for (a). The launcher's initial mandate is then switched without the owner's choice.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "F4",
      "kind": "defect",
      "line": 766,
      "origin_stage": "implementation",
      "problem": "Decision 8's Recommendation cell opens with \"(a), the owner's decision: the excess is ...\". In this table the other rows record an owner's decision as \"Decided by the owner on ...\", so this phrase reads as if the owner had already chosen (a), shipping the initial wording that failed the criterion. The intended meaning is the author's recommendation (a), with the owner to decide. The cell clarifies only at its end (\"Until the owner decides\").",
      "severity": "low"
    },
    {
      "evidence": "review_inputs.py:57 DEFAULT_DIFF_CONFIG; :109 and :518 parse `--name-status` and `--numstat` text by tabs and lines; run_independent_review.py:1743-1748 and :2142; check_docs.py:127. By contrast lint_changed_files.py:80 and run_independent_review.py:330 use `-z`.",
      "failure_scenario": "A change adds a file whose name holds a double quote. `changed_files` returns the quoted name, the launcher refuses the review because the file is missing from the copy, and the author loses a review attempt. This is a false refusal, not a false green.",
      "file": "scripts/review_inputs.py",
      "id": "F5",
      "kind": "defect",
      "line": 57,
      "origin_stage": "implementation",
      "problem": "The issue 60 fix passes `core.quotePath=false` to the git calls that list files without `-z`. Git still C-quotes a path that holds a double quote, a backslash, a tab or a newline, whatever core.quotePath says. So `changed_files`, `process_file_evidence`, `final_records`, `stage_lists`, `changed_logs` and `tracked_files` still refuse or miss such a name. Decision page row 60 says the cause is fixed at every site; only the non-ASCII and space cases are.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to owner-decisions-3/c1/r1/A/1

| Finding | Severity | Answer |
| --- | --- | --- |
| F1 | medium | fixed: docs/delivery_problem_log.md, docs/slices/agentic-sdlc-poc/slice_4_decisions.md: DPL-015 records discovered issue 56 (the miss by A/2 and the first mechanics replay, the wrong runner counts quoted in decision 2's options until R4-3, the root shared with DPL-014, the fix `02281b0` and its tests) and where the author looked for the same cause: every function of `scripts/run_review_benchmark.py` that groups, counts or keys result lines (the view under the key's rule, the view under the earlier rule, `report_rows`, `--export-rescore`, `--rescore B`, `_completed_reviews`, `previous_state`), `scripts/review_brief.py` and the launcher's round state; it is open until slice 4's final PR merges, as DPL-014; the two places that still read replaced lines (the origin table and question line, 7 of 538 findings; `_completed_reviews`, latent) are discovered issue 65 on the decision page, left for the owner, since no count of R4-4's criterion reads them |
| F2 | medium | fixed: docs/slices/poc-4-5-benchmark/benchmark_report.md, docs/slices/agentic-sdlc-poc/slice_4_decisions.md, docs/history/implementation_log.md: each record now says that a first pair of confirmer sessions, whose prompt added a test beyond the match rule, was stopped after about a minute and by its session transcripts (not kept in the repository) wrote no verdict, that the second pair, asked only to apply the rule, wrote the committed verdicts, and that the committed rows set `expected_id` to null on the 65 no-match rows as the earlier rows hold it (the 20 match rows are the sessions' output unchanged) |
| F3 | low | rejected: R4-4 is the owner-approved decision record, and "19 calls (86 to 105 of the 120 now allowed)" gives the stage's count of used calls before and after the 19 (86 used before round 4, 105 after), as the measurement paragraph of the same section and the commit `660f57b` state; the approved text is left as the owner approved it |
| F4 | low | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: decision 8's Recommendation cell now opens "The author recommends (a), and the owner decides:" |
| F5 | low | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: row 60 says the fix covers non-ASCII names and spaces only (git still quotes a double quote, a backslash, a tab and a newline), that no tracked file name holds one, and that the code is not changed |
