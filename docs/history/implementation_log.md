# Implementation Log

Historical per-slice implementation and verification record. Until 2026-10-27 this lived in the
gitignored `docs/local_status_capture/implementation_status.md`; older entries still cite that path.
Current state is summarized in `docs/STATUS.md`. Entries are not in strict date order (the newest
is first); every heading carries its date.

## 2026-11-18 Slice agentic-sdlc-poc 4: round 4, decision 8 (the owner): the launcher ships R4-1's initial mandate

- The owner decided decision 8 as option (a): "yes, ship the R4-1 initial mandate and review it", after the author's
  answer to why the wording runs could not settle it (one run per wording; the criterion had no margin; the false
  alarms counted, never judged; decision concern 19's confound). The criterion's outcome stays as recorded. On the
  [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md): decision row 8, section "Round 4", paragraph
  "Decision 8", the Progress row and discovered issue 64.
- The change: the launcher's initial mandate (`MANDATES` in `scripts/run_independent_review.py`) is R4-1's text
  verbatim, so all three are round 4's; the benchmark notes that `open+list` now means that text while its recorded
  lines (and `open+list+sev`'s) ran 4.1's. Byte identity, built with no reviewer call: on the 15 initial cases the
  launcher's own initial prompt (`open+list`) equals `open-R4+list`'s whole prompt, and `open-R4+list`'s prompt
  identity equals its recorded runs' (15 of 15). An unfiltered `--run` still selects the same 66 reviews (issue 64).
- Tests first, red on the base code (`b354446`):
  `test_run_review_benchmark.py::test_the_launcher_ships_r4_1s_mandates_in_all_three_modes[initial-Initial]` (renamed
  from `..._recheck_and_final_mandates`): `AssertionError: assert 'Find anythin...f the review.' == 'Find anythin...s
  is valid.\n'`.
- Validation, local: `make tooling-test` (1001 passed; shell 9 passed), `make docs-check`, `make lint` (0 new or
  worsened) and `make qa-trace` (requirements 170, architecture 34, design 131, tests 386, coverage gaps 113; 0 new
  against the merge-base) passed. Not run: the full E2E suite and the unit gates (no `services/`, harness, compose or CI
  change), and CI (not pushed).
- Next: the review unit `owner-decisions-4` (default by the author, as R4-6); then the owner's decision concerns 16
  and 19, growth proposal 12, the actions of decisions 3 and 4, the push and the final PR.

## 2026-11-18 Slice agentic-sdlc-poc 4: round 4, the review mandates and the runner fixes

- Branch `poc/slice-4-implementation`, 11 commits after round 3's handoff (`96e3b22`): `8ab80e5` (discovered issue
  60), `4fb578d` (issue 57), `f5321cc` (the owner's decisions on the decision page), `02281b0` (issues 56 and 61),
  `ebdb0e8` (the report and the page after issue 56; new issues 62 and 63), `90a15ed` (R4-2), `831b47a`, `660f57b`,
  `78116f7` and `6add324` (R4-4), `1f905a9` (R4-1 and R4-5), then these records. The owner's decisions of 2026-11-17
  ("Decision 1, 3, 4  and 5 - accept, I want to revisit the decision 2 again, fix the issue 56, 57 and 60.") and the
  approval of round 4 ("approve the texts, budget 120, criterion fine.") are on the
  [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md), section "Round 4", with R4-1 to R4-6 and the
  measurement's result.
- R4-1 (`1f905a9`): the launcher's recheck and final mandates (`MANDATES` in `scripts/run_independent_review.py`) are
  R4-1's texts verbatim, one line per paragraph as the benchmark's prompt files hold them. The recheck mandate is byte
  for byte the one `recheck-R4` measured: on RC-1 to RC-4 the launcher's recheck prompt (`recheck-A`) equals
  `recheck-R4`'s, and `recheck-R4`'s prompt identity equals the measured runs'. The final mandate, which no case can
  measure, was approved as written. The initial mandate stays 4.1's: round 4's did not meet R4-4's criterion, and the
  owner decides (decision 8). The benchmark notes that `recheck-A` now means the new recheck text while its recorded
  lines ran 4.1's.
- R4-2 (`90a15ed`): the "Review prompt" section of slice 4.4's research record
  ([`research.md`](../slices/poc-4-4-stage-checklists/research.md)) holds the words of R4-1's mandates that rest on
  research, their 29 sources with verbatim quotes checked against the downloaded copies, the gaps the research leaves,
  and the options considered and left out.
- R4-3, the fixes, tests first:
  - Discovered issue 60 (`8ab80e5`): every place that reads a git file list without `-z` passes the diff's `-c`
    settings (`DEFAULT_DIFF_CONFIG` of `scripts/review_inputs.py`, `core.quotePath=false` among them), so git no longer
    quotes a non-ASCII name: `changed_files` and `process_file_evidence` in `scripts/review_inputs.py`, `final_records`
    and `stage_lists` in the launcher, `changed_logs` in `scripts/review_brief.py`, and `tracked_files` in
    `scripts/check_docs.py`; `stage_lists` and `changed_logs` read one name per line, so a name with a space holds.
  - Discovered issue 57 (`4fb578d`): after the whole-line removal, the scorer also removes each quoted span (backticks,
    straight or curly double quotes) of `QUOTE_MIN` characters or more that occurs verbatim in an expected line, never
    the finding's own words; stage A's rescore prepares each case's expected lines as stage B's does
    (`rescore_quoted`). On the committed data `--rescore B` and `--report --stage B` gave the same bytes before and
    after, and the 10 stage-A reviews kept their detections; the key's rule text and hash are unchanged.
  - Discovered issue 56 (`02281b0`): `rule_views` keeps only the last line in file order of each case, configuration
    and run (`current_lines`), in both views; results stay append-only. Under R2-9 `recheck-A` reads 3 of 3 (was 6 of
    7) and `recheck-B` 3 of 3 (was 3 of 4). Discovered issue 61, in the same commit: `benchmark_rescore_B.jsonl`
    refreshed by `--rescore B` (no reviewer call), key hash `ba6975d46b11` to `0ee2ad1414c0` on all 62 rows, every
    other field unchanged. `ebdb0e8` keeps the rebuilt stage-B report verbatim in the benchmark report and records
    discovered issues 62 and 63.
- R4-4, the measurement: `831b47a` adds the configurations `open-R4+list` and `recheck-R4` (R4-1's initial and
  recheck mandates verbatim, pinned by a test to the decision page), answer key version 8, the stage-B hard stop of
  120 and, before the runs, decision concern 19 (the `open+list` baseline ran under CLI 2.1.321). `660f57b`: the 19
  calls (`open-R4+list` on the 15 initial cases, `recheck-R4` on RC-1 to RC-4), one call each without retries, CLI
  2.1.323, USD 13.58, 105 of 120 calls used; FS-1's line is withheld by the publication check. `78116f7`: the 85 new
  judged findings exported as M153 to M237 (seed 45). `6add324`: two fresh sessions judged them blind, each given half
  of the export and the match rule only: 20 matches. They were the second pair: a first pair, started with a prompt
  that added a test beyond the match rule (whether each finding actually describes the expected defect), was stopped
  after about a minute; by their session transcripts (not kept in the repository) each had made three read-only calls,
  listing its folder and the match rule and printing export rows, and written no verdict, so the author's removal of
  any verdict file in their folders before the relaunch removed nothing. The second pair was asked only to apply the
  rule. The committed rows differ from the sessions' output in one field: `expected_id` is null on the 65 no-match
  rows, as in the earlier rows, where the sessions had named `E1` or `R1` (`read_verdicts` reads only `token` and
  `verdict`). Under R2-9 `open-R4+list` detects 10 of the 11 defect cases
  against `open+list`'s 8, with 8 false alarms in 4 no-defect reviews against 7; under blocking or high, 9 against 7
  detections and 2 against 2 false alarms. `recheck-R4` re-raised RC-1's, RC-3's and RC-4's false answers, each
  re-raise confirmed, and accepted RC-2's. The criterion's outcome: the recheck wording meets it and ships; the
  initial wording raised one more false alarm (a medium finding on CL-2), so it does not ship and the owner decides
  (decision 8).
- R4-5 (`1f905a9`): `AGENTS.md`'s Final review and stage table no longer state 4.1's question "What did everyone
  before you miss?"; S46-D5 stays as recorded.
- Tests first, each new or changed test run by ID on its fix commit's parent with only that commit's test files
  copied in (`python3 -m pytest -q -p no:cacheprovider --tb=line <file>::<test>`), with its first failure line. The
  lines of `8ab80e5`, `4fb578d` and `831b47a` were not recorded and are re-derived for these records in a scratch
  worktree, since removed; those of `02281b0` and `1f905a9` are as their commit messages record them.
  - Issue 60 (base `96e3b22`), one test per place, each setting `core.quotePath=true` in its scratch repository:
    `test_check_docs.py::test_images_unreferenced_render_with_a_non_ascii_name_is_reported`
    `tests/tools/test_check_docs.py:155: AssertionError: assert [] == ['images: doc...ive document']`;
    `test_review_brief.py::test_changed_logs_keep_non_ascii_names_and_spaces_whatever_the_repository_configures`
    `tests/tools/test_review_brief.py:210: AssertionError: assert [] == ['docs/slices...tempts.jsonl']`;
    `test_review_inputs.py::test_changed_files_keep_a_non_ascii_name_whatever_the_repository_configures`
    `tests/tools/test_review_inputs.py:799: assert ChangedFiles(...), deleted=()) == ChangedFiles(...), deleted=())`
    (`to_open: ('"docs/\\303\\251.md"',) != ('docs/é.md',)`);
    `test_review_inputs.py::test_process_file_evidence_keeps_a_non_ascii_name_whatever_the_repository_configures`
    `tests/tools/test_review_inputs.py:812: assert [] == ['EV1: proces...t> <commit>)']`;
    `test_run_independent_review.py::test_final_records_keep_non_ascii_names_whatever_the_repository_configures`
    `tests/tools/test_run_independent_review.py:950: AssertionError: assert () == ('docs/slices...view_impl.md')`;
    `test_stage_checklists.py::test_a_list_whose_name_is_not_ascii_or_holds_a_space_is_found_whatever_the_repository_configures`
    `scripts/run_independent_review.py:2133: run_independent_review.ReviewRefusedError: --stage é names no list at the
    base; the lists are: words`.
  - Issue 57 (base `8ab80e5`, `tests/tools/test_run_review_benchmark.py`):
    `test_a_finding_that_quotes_part_of_the_planted_line_detects_it_only_by_its_own_words`, `[backticks]`,
    `[straight]` and `[curly]`, each `tests/tools/test_run_review_benchmark.py:1208: AssertionError: assert (['E1'] ==
    []`; `test_a_quoted_span_is_removed_from_quote_min_on_and_only_when_an_expected_line_holds_it[at-quote-min]`
    `tests/tools/test_run_review_benchmark.py:1220: AssertionError: assert ['E1'] == []`;
    `test_rescore_a_applies_the_quote_rule_to_the_planted_line` `tests/tools/test_run_review_benchmark.py:778:
    AssertionError: assert [(['E1'], []), (['E1'], [])] == [([], ['E1']), ([], ['E1'])]`. The twins
    `[below-quote-min]` and `[not-in-an-expected-line]` passed on the base, by design.
  - Issue 56 (base `f5321cc`): `test_a_review_run_again_under_another_prompt_replaces_the_earlier_line_in_the_counts`
    `E AssertionError: assert ('1 of 2' == '0 of 1'`; `test_a_recheck_run_again_under_another_prompt_is_listed_once`
    `E AssertionError: assert '1 of 2' == '1 of 1'`.
  - R4-4 (base `90a15ed`): `test_the_committed_keys_budget_is_the_stage_b_hard_stop_of_120` (renamed from `_of_95`)
    `tests/tools/test_run_review_benchmark.py:1594: assert 95 == 120`;
    `test_the_round_4_configurations_send_r4_1s_mandates_verbatim[open-R4+list-initial-Initial]`
    `scripts/run_review_benchmark.py:424: run_review_benchmark.BenchmarkRefusedError: unknown configuration
    'open-R4+list'; the runner knows short+list, open+list, open-B+list, recheck-A, recheck-B, open+list+sev, canary`,
    and `[recheck-R4-recheck-Recheck]` the same for `'recheck-R4'`.
  - R4-1 and R4-5 (base `6add324`):
    `test_run_review_benchmark.py::test_the_launcher_ships_r4_1s_recheck_and_final_mandates[recheck-Recheck]`
    `AssertionError: assert 'For every an... fixes touch.' == 'Verify every...s is valid.\n'` and `[final-Final]`
    `AssertionError: assert 'What did eve..., on purpose.' == 'Independentl...nal review.\n'`; the changed
    `test_stage_rules.py::test_the_stage_table_check_fails_on_each_kind_of_violation[review-without-list-or-mode]`,
    unchanged, on the new `AGENTS.md`: `AssertionError: []` (its edit no longer matched the stage table's row).
- Validation, local: at `1f905a9`, `make tooling-test` (1000 passed; shell 9 passed), `make docs-check`, `make lint`
  and `make gate-consistency` passed, as the commit records. On these records (docs only): `make docs-check`, `make
  qa-trace` (requirements 170, architecture 34, design 131, tests 386, coverage gaps 113; gap gate against the
  merge-base of `origin/poc/agentic-sdlc`: 0 new), `make lint` (0 new or worsened) and `make tooling-test` (1000
  passed, with a scratch shellcheck; shell 9 passed) passed.
- Not run: the full E2E suite (no service, policy, compose, harness or CI file changed, so no runtime change; CI runs
  it on the PR), `make unit-trust`, `make unit-mutation` and `make unit-diff-cov` (no `services/` change), and CI (the
  branch is not pushed).
- Discovered issue 64 is on the decision page: a `--run` that names no case or configuration selects 66 reviews, every
  configuration of every case but round 4's two, since their prompts changed after their recorded runs (probed with no
  reviewer call); low, recorded only.
- Review: the unit `owner-decisions-3` (R4-6), round 1 (`owner-decisions-3/c1/r1/A/1`, Opus at high, CLI 2.1.327,
  USD 3.22, reviewed commit `5f5b404`): approvable, 2 medium and 3 low (`14435c4`). Fixed in `ec4b2a4`: F1, DPL-015
  records discovered issue 56 as a review miss and where the author looked for the same cause; F2, the records of
  R4-4's blind confirmation say that a first confirmer pair was stopped before any verdict and that the committed rows
  set `expected_id` to null on the 65 no-match rows; F4, decision 8's recommendation reads as the author's; F5, row 60
  says issue 60's fix covers non-ASCII names and spaces only. F3 (low, the call range "86 to 105") rejected. The
  answers and discovered issue 65 (the origin table, the question line and `_completed_reviews` still read replaced
  lines) are `34d76f5`.
- Review: round 2, the recheck (`owner-decisions-3/c1/r2/A/1`, Opus at medium, USD 0.53; its range `5f5b404` to
  `34d76f5`), the first under round 4's recheck mandate: approvable, all five answers accepted, no new finding
  (`e6f78d3`). With no blocking, high or medium finding open, the review ended after round 2. The brief is rebuilt on
  the decision page with `python3 scripts/review_brief.py --base origin/poc/agentic-sdlc` (head `e6f78d3`; unit
  `owner-decisions-3`: yes, 2 rounds, 0 blocking, 0 high, 2 medium, 3 low, nothing open), with F5 under the test-plan
  question 1 by its content.
- Next, the owner's: decision 8 (round 4's initial wording); decision concerns 16 and 19; growth proposal 12;
  discovered issues 62 to 65 are recorded; the actions of decisions 3 (recreate the hidden issues, about 2026-11-23)
  and 4 (remove the personal copy of the grill-me skill); and the push and the final PR, which the agent account
  cannot write.

## 2026-11-17 Slice agentic-sdlc-poc 4: round 3, decision concern 18 (diff lines count as seen) and the second mechanics replay

- Branch `poc/slice-4-implementation`, after the records of round 3 (`a6dfcce`): the owner's decision on decision
  concern 18 recorded (`fd1b07e`, `4f5ea83`: option (b), "I choose your recommendation"), the benchmark report with
  RC-1 to RC-4's runs (`2f2f1e2`), then (b) in `04a0ae3` (tests first), `753fc3e` and `5627de7`, then these records.
  The [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md), section "Round 3", holds the as-built
  paragraph and the replay's result.
- What changed (`git diff --name-only 2f2f1e2 5627de7`: `AGENTS.md`, `scripts/run_independent_review.py`,
  `tests/tools/test_run_independent_review.py`): `lines_shown` maps each line of `_review_inputs/change.diff` the
  attempt was shown to the file line it shows (`diff_places`): a context or added line at its new path and line, a
  removed line at its old path and line only for a file the diff deletes, a header line nowhere; the must-see check,
  the quote's file rule and the place check use these lines too. `AGENTS.md` (Modes and prompts) says so, and the
  output section's `SEEN_RULE` in its own commit (`5627de7`, wording only, decision 2). By the author's choice the
  definition holds for every mode, so an initial review's empty-review rule counts diff lines too; the owner approved
  (b) for rechecks and may restrict it.
- Tests first (base `2f2f1e2`, the tests added in the working tree, each by ID with `python3 -m pytest -q
  --tb=line`), with the first failure line:
  `test_a_shown_context_or_added_line_of_the_change_diff_is_a_seen_line_of_its_file_and_a_header_line_of_none`
  `E KeyError: 'scripts/kept.py'`;
  `test_a_shown_removed_line_is_a_seen_line_only_of_a_file_the_change_deletes_at_its_old_line`
  `E KeyError: 'scripts/kept.py'`;
  `test_a_fix_seen_only_as_hunks_of_the_change_diff_is_seen_and_quoted_only_at_the_lines_they_showed`, the two cases
  beyond two lines (`[three-before-the-hunk]`, `[three-past-the-hunk]`) `AssertionError: assert (1 == 1 and 'X1 quotes
  scripts/cover.py:4-4, lines the attempt was not shown' in 'the report does not account for what it was given:
  scripts/cover.py is named in a fixed: or rejected: answer and was not seen; ...')` (`:16-16` for the second), and
  the four within (`[two-before-the-hunk]`, `[the-added-line]`, `[the-last-context-line]`, `[two-past-the-hunk]`)
  `AssertionError: the report does not account for what it was given: scripts/cover.py is named in a fixed: or
  rejected: answer and was not seen; X1 quotes scripts/cover.py, which the attempt did not see`. Not red, by design:
  G2-1's test, `test_a_rejection_citing_a_file_the_change_deletes_must_see_the_change_diff_and_quote_from_it` (three
  cases), passed on the unchanged code; the branch was right and the test pins it (discovered issue 51). The
  commands and lines: `artifacts/work/round3_dc18_red.txt` (not tracked).
- Measurement: the `mechanics` round-2 replay once more, on the launcher at `5627de7`, set up as the first replay
  (one call, no retry, the pinned CLI 2.1.323, USD 1.37): completed and approvable, 15 answers accepted, 1 re-raised
  (H1, high), 0 cannot determine, and two new findings (N1 medium, N2 high). Measurement 2's criterion, fixed before
  the runs, was not met by the first replays; after the owner's decision 18 the failing replay ran once more and
  passed. The counterfactual: the check of `3df47b7` on this attempt still gives the four "not seen" failures, the
  check of `5627de7` none, and the check of `5627de7` on the first attempt still fails L1's misquote; so (b) passed
  M4, and L1 passed because this reviewer quoted correctly. One run, and the evidence differed (4 entries instead of
  5), so run-to-run variance cannot be separated. The analysis:
  `artifacts/work/round3_replays/mechanics-dc18/analysis.md` (not tracked).
- Validation, local: at `5627de7`, `make lint`, `make docs-check`, `make qa-trace` and `make tooling-test` passed, as
  the build reported. On these records, rerun: `make qa-trace` passed (requirements 170, architecture 34, design 131,
  tests 386, coverage gaps 113; gap gate against the merge-base of `origin/poc/agentic-sdlc`: 0 new) and `make
  docs-check` passed. Not run: `make gate-consistency` (no CI job, Makefile target or Quality gates row changed), the
  full E2E suite (no service, policy, compose, harness or CI file changed), `make unit-trust`, `make unit-mutation`
  and `make unit-diff-cov` (no `services/` change), and CI (the branch is not pushed).
- Discovered issues 56 to 59 are on the decision page: H1 (high) and N1 (medium) still hold at HEAD in slice 4.5's
  runner and are open for the owner; N2 (high) no longer holds (both refusals are tested since `ea5697f`); the
  evidence difference is not investigated. Discovered issue 51 (G2-1) has its test.
- The author's choice (one definition of "seen", so an initial review's empty-review rule also counts diff lines)
  got its test after these records (`f75bc7a`): `test_an_initial_review_that_saw_its_only_path_under_review_only_as_a_hunk_of_the_change_diff_completes`
  fails on the launcher of `3df47b7` with `tests/tools/test_run_independent_review.py:2113: AssertionError: the
  review saw none of the paths under review`; its twin,
  `test_an_initial_review_that_saw_neither_its_path_under_review_nor_a_hunk_line_of_it_in_the_change_diff_fails`,
  passes on both, by design. Then, at `f75bc7a`: `make lint`, `make docs-check`, `make qa-trace`, `make test-lint`,
  `make unit-guard-check` (357), `make qa-deploy` and `make tooling-test` (976 passed; shell 9 passed) passed.
- Review: the unit `round-3`, round 1 (`round-3/c1/r1/A/1`, Opus at high, CLI 2.1.326, USD 2.54, reviewed commit
  `af9ba98`): approvable, 3 medium and 3 low (`15c6667`). Fixed: F1, by the owner's decision ("Rechecks only"): diff
  lines count as seen only in a recheck (`c105c9d`); F2, a recheck's rebuild and a retry in the same round take the range
  from every reviewer of the round, as the launcher does (`1d728fd`); F3, a test of tool results given as a list of
  blocks and of a content Grep outside the copy (`06857a7`); F6, `change_diff` runs `git diff` in git's default format
  whatever the repository configures (`8ec83b6`; every distinct range of the attempt logs, 78 by the recount of N1's
  fix, gives the same bytes; F6's answer said 89, counted another way). F4 and F5 (low) rejected.
  Each new test's first failure on the code before it: F1's
  `test_an_initial_or_final_review_that_saw_its_only_path_under_review_only_as_a_hunk_of_the_change_diff_fails`
  `[initial]` and `[final]` `AssertionError: assert 0 == 1`, and the benchmark's
  `test_recheck_prompt_holds_the_earlier_report_and_the_false_fix` `AttributeError: 'Accounting' object has no attribute
  'mode'` (on `8ec83b6`); F2's
  `test_a_recheck_of_reviewers_who_reviewed_different_commits_is_rebuilt_from_its_entry_with_no_mismatch` `At index 1
  diff: ['paths_sha256', 'diff_sha256', 'full_prompt_sha256'] != []`; F6's
  `test_change_diff_has_git_default_format_whatever_the_repository_configures` `AssertionError: assert '' ==
  'diff --git a...\n+première\n'` (both on `15c6667`); F3's
  `test_a_tool_result_given_as_a_list_of_blocks_shows_the_lines_of_its_text_blocks` passed on `15c6667`, by design
  (the branches were untested, not wrong). Gates at `c105c9d`: `make lint` and `make qa-trace` passed; `make
  docs-check` and `make tooling-test` (979 passed, 1 failed; shell 9 passed) failed only on the round's missing answers,
  which these records and the answers end. Discovered issue 60 (git file lists without `core.quotePath=false`) came from
  F6's search for the same cause.
- Review: the unit `round-3`, round 2, the recheck (`round-3/c1/r2/A/1`, Opus at medium, CLI 2.1.326, USD 0.66; its
  range `af9ba98` to `35dbead`, 5 files under review): approvable, all six answers accepted with quotes, one new low
  finding, N1: `changed_lines` read `git diff -U0` under the repository's own git configuration. Fixed (`9e6b3e1`): git's
  default diff format is defined once in `scripts/review_inputs.py` and used by `changed_lines` and `change_diff`;
  `test_changed_lines_reads_git_default_format_whatever_the_repository_configures` failed on `b2cceb3` with `assert
  set() == {2, 5, 6, 7}`. Gates at `9e6b3e1`: `make lint` and `make qa-trace` passed, `make tooling-test` 980 passed and
  the one test that runs the record check failed only on the round's missing answers, as `make docs-check` did, until
  these answers. With no blocking, high or medium finding open, the review ended after round 2.
- Handoff of round 3 (docs only): the decision page's measurement 4 states the result (criterion met), its Progress row
  and "Last updated" line say the review ended, and the brief is rebuilt under "Review outcome" with
  `python3 scripts/review_brief.py --base origin/poc/agentic-sdlc` (head `faa6df4`; unit `round-3`: yes, 2 rounds, 0
  blocking, 0 high, 3 medium, 4 low, nothing open); `docs/STATUS.md` and the slice index list what remains for the
  owner. Gates on the handoff tree: `make docs-check`, `make qa-trace` (0 new gaps, 113 coverage gaps remain), `make
  lint` (0 new or worsened), `make test-lint`, `make unit-guard-check` (357), `make qa-deploy` (18 known violations, 22
  warnings) and `make tooling-test` (981 passed, with a scratch shellcheck; shell 9 passed) passed. Not run: the E2E
  suite and gate-consistency (no service, policy, compose, harness or CI file changed), and CI (the branch is not
  pushed).

## 2026-11-17 Slice agentic-sdlc-poc 4: round 3, rechecks that look before they accept

- Branch `poc/slice-4-implementation`, 17 commits `292f270` to `fa7953f`, then these records: round 3, approved by the
  owner on 2026-11-17 ("Round 3 of slice 4: I approve R3-1 to R3-4, the budget 85 → 95, and the probe and replays"),
  in the owner's words on the [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md) (section "Round 3",
  which holds the as-built paragraphs and the measurements' results).
- The probe (`185f93f`, USD 0.49, CLI 2.1.326): one recheck on the launcher at `292f270` accepted a real fix and
  re-raised a false rejection, quoting the cited test's request and assertion from a 70-line read of the harness at
  the answer's `file:line`; it set R3-2's details (a) to (d).
- R3-1 (`d586664`, `1ed4a2f`): a recheck's change, files under review, upstream items (the governing plan kept),
  changed script lines and trace gaps come from the commits since the reviewed round's commit, while the copy holds
  the whole branch; a reviewed round's commit that is not an ancestor is refused before any call; `PROCESS_FILES`
  adds the benchmark runner, its answer key and `.claude/skills/` (decision concern 15); `AGENTS.md`, What the reviewer
  receives.
- R3-2 (`bba4840`, `f7928ae`, and `29061a7`, wording only): a file is seen at the lines a Read showed or a content
  Grep printed; every file a `fixed:` answer names or a `rejected:` answer cites must be seen; every fix and rejection
  a recheck accepts or re-raises is quoted from a named or cited file as it is in the copy (`change.diff` only for a
  named file the range deletes), within two lines of a shown line; `opened` is no longer checked and `searched` left
  the schema; `AGENTS.md`, Modes and prompts. The fake CLI (`tests/tools/fakes/fake_claude.py`) shows each Read's
  window and takes a Grep's result.
- R3-3 (`e4ebda4`, `9a57a88` wording only, `de44fdd`): what an existing rule already requires of a fix, such as a test
  for new behaviour or a handoff record, is not an added mechanism, in the recheck's mechanism question, the shared
  kind bullet and `AGENTS.md` (Fixes stay within the agreed decisions).
- R3-4 (`06fa912`, `3df47b7`): the plan list's question 8 asks the fix rule since R2-4 (growth proposal 14), and a
  false small-slice claim blocks at the plan review (decision 7, option (a)); 12 questions.
- Measurement 3's runner (`a3f1835`, `07f024a`, `a9ec037`): the stage-B hard stop and the key's budget are 95 (key
  version 7, naming version 6's hash); a confirmation token is keyed with its line's prompt identity, and
  `--export-rescore` keeps its earlier rows and tokens (discovered issue 44,
  [DPL-014](../delivery_problem_log.md#dpl-014-a-blind-confirmation-token-was-not-tied-to-its-result-line)). After
  `a9ec037` the stage-B report was byte-identical, `--rescore B` gave all 62 recorded scores, and `--export-rescore`
  on the committed results exported nothing.
- Tests first, each new or changed test run on the unchanged code with the test changes (`python3 -m pytest -q
  -p no:cacheprovider` or `-p no:randomly --tb=line`, by test ID), with its first failure line:
  - R3-1 (base `292f270`, each test alone): `test_an_initial_review_gets_the_branch_and_a_recheck_only_the_commits_since_the_reviewed_round`
    `assert 'the report d... was not read' == 'the review r... under review'`;
    `test_a_recheck_whose_reviewed_round_commit_is_not_an_ancestor_is_refused_before_any_call` `assert 1 == 2`;
    `test_a_recheck_whose_commits_since_the_reviewed_round_change_no_file_still_runs`
    `assert '7ca6ecc9fc08...7d17da018b538' == 'e3b0c44298fc...5991b7852b855'` (the branch's diff, not the empty
    range's); `test_recheck_that_does_not_account_for_every_answer_fails[nothing-under-review-read]` (changed)
    `assert (1 == 1 and 'failed' == 'failed'` (another reason); `test_review_inputs.py`:
    `test_process_file_evidence_lists_a_changed_skill_and_the_benchmark_runner_with_its_answer_key`
    `assert [] == ['EV1: proces...t> <commit>)']`,
    `test_a_recheck_takes_upstream_items_and_evidence_from_the_commits_since_the_reviewed_round`
    `assert ('REQ-T-R1 (found' not in ...` (an item edited before round 1 still listed), and 3 of the 35 cases of
    `test_process_files_are_the_rulebook_gates_ci_templates_checklists_and_the_launcher` (the runner, the key, a skill)
    `assert False is True`; added at implementation,
    `test_a_recheck_whose_reviewers_reviewed_different_commits_starts_at_their_common_ancestor`
    `AttributeError: module 'run_independent_review' has no attribute 'recheck_inputs'`. Not red, by design:
    `test_fixed_answer_naming_a_file_the_change_deletes_is_accepted_and_needs_the_diff_read` (changed: the deletion
    moved into the fix commit, and it is in the merge-base diff too).
  - R3-2 (base `1ed4a2f`; the launcher, record-check, inputs and benchmark tests: 25 failed, 536 passed):
    `test_failed_read_of_the_only_path_under_review_does_not_count` `:639 assert ('failed' == 'failed'` (another
    reason); `test_output_section_holds_the_reporting_bounds_and_the_credential_note_verbatim` `:837 AttributeError:
    ... no attribute 'SEEN_RULE'`; `test_fixed_file_that_was_not_seen_fails_even_when_a_path_under_review_was` `:1097`
    and `test_a_rejection_citing_a_root_level_file_must_see_it` `:1135` (the reason says "was not read", not "was not
    seen"); `test_a_rejection_counts_only_when_the_files_it_cites_were_seen[cited-file-not-read]` `:1118 assert (1,
    False) == (1, True)`; `test_an_opened_file_the_attempt_did_not_read_no_longer_fails` `:1151 ... X1 names an opened
    file the attempt did not read`; `test_a_report_with_a_searched_field_is_refused_by_the_schema` (2 cases) `:1168
    assert [] == ['accounted 0...m the schema']`; `test_the_schema_offers_the_question_field_as_optional_and_no_searched_field`
    `:1175` (`searched` still in the schema); `test_every_fix_and_rejection_the_recheck_accepts_or_re_raises_is_quoted`
    (3 cases) `:1519` (the old rejection-only message, or no failure for an unquoted fix);
    `test_a_quote_comes_from_a_file_the_recheck_read_and_one_the_rejection_cites` (2 cases) `:1549` (the old
    messages); `test_an_initial_review_gets_the_branch_and_a_recheck_only_the_commits_since_the_reviewed_round` `:1653`
    and `test_review_inputs.py::test_review_that_opened_none_of_the_hint_files_fails_even_when_it_opened_other_listed_files`
    `:192` ("read" where "saw" is expected); `test_the_lines_shown_come_from_read_windows_and_the_lines_a_content_grep_printed`
    `:1819 AttributeError: ... no attribute 'lines_shown'`; `test_a_quote_counts_only_within_the_lines_the_attempt_was_shown[start-minus-3,
    end-plus-3]` `:1841 assert (0 == 1)`; `test_a_file_seen_only_by_a_content_grep_counts_as_seen_and_one_only_listed_or_counted_does_not`
    (4 cases) `:1870` and `:1872` (a content Grep not counted; "not read" for a listing or a count);
    `test_a_review_that_saw_its_only_path_under_review_through_a_content_grep_completes` `:1879 the review read none of
    the paths under review`; `test_a_fix_quoted_only_from_the_change_diff_fails_unless_the_range_deletes_the_named_file[in-the-copy]`
    `:1910 assert (0 == 1)`; and, run apart with the launcher of `1ed4a2f`,
    `test_run_review_benchmark.py::test_a_benchmark_recheck_that_accepts_a_rejection_or_a_fix_without_a_quote_fails`
    `:1421` (the old rejection-only message). Not red, by design: the four cases within two lines of a shown line,
    `[deleted-by-the-range]`, `[undetermined-fix-needs-no-quote]`, `[accepted-fix-quoted]`, and
    `test_the_repository_records_released_with_searched_and_unquoted_fixes_still_pass_the_record_check`.
  - R3-3 and R3-4 (base `29061a7`; the launcher and checklist tests: 5 failed, 276 passed):
    `test_a_simpler_alternative_is_only_a_mechanism_the_owner_approved` (the kind bullet lacks the carve-out);
    `test_what_an_existing_rule_requires_of_a_fix_is_not_an_added_mechanism` (the recheck's mechanism rule lacks it);
    `test_the_fix_rule_in_agents_md_says_what_an_existing_rule_requires_is_not_an_added_mechanism` `:1786`;
    `test_stage_checklists.py`: `test_the_plan_lists_question_8_asks_the_fix_rule_since_r2_4` (question 8's old text)
    and `test_a_false_small_slice_claim_blocks_at_the_plan_review` `:147` (no such bullet). Not red, by design:
    `test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism` (changed only to allow the carve-out's "such
    as").
  - Measurement 3's runner (base `3df47b7`, `tests/tools/test_run_review_benchmark.py`):
    `test_stage_b_stops_at_its_budget_counting_retries_and_the_canary` `:332 assert 85 == 95`;
    `test_the_committed_keys_budget_is_the_stage_b_hard_stop_of_95` `:1550 assert 85 == 95`;
    `test_repeats_table_reads_the_confirmed_verdicts_and_shows_a_failed_run` `:1016 AssertionError: assert ('RM
    short+list: True, False' in ...)`; `test_a_new_line_under_another_prompt_takes_no_earlier_lines_token_and_its_findings_are_exported`
    `:1639 assert ({'E1'} == set()` (the second line inherits T001's verdict);
    `test_the_third_export_keeps_its_rows_and_tokens_and_adds_a_new_lines_findings_after_the_last`
    `:1671 assert (set() == {'E1'}` (the re-export reshuffles, and the later row takes the first line's key). Not red,
    by design: `test_the_third_export_holds_only_findings_no_earlier_export_holds_and_confirms_a_medium_match` (its
    fixture only adds the prompt identity every committed key row carries).
- Measurements: the replays (USD 3.07, CLI 2.1.323): `owner-decisions` and `growth` round 2 completed and accepted
  every answer, `mechanics` round 2 failed the new recheck on two causes, so the criterion is not met (decision concern
  18, open); RC-1 to RC-4 on `recheck-A` (`c818c15`, calls 83 to 86 of 95, USD 0.94, CLI 2.1.323): RC-1, RC-3 and RC-4
  re-raised, RC-2 accepted, and a fresh session's blind verdicts (`fa7953f`) confirm M149, M150 and M152 and not M151,
  so the criterion is met on confirmed verdicts.
- Validation, local: `make tooling-test` on `fa7953f`, in a clean worktree, 963 passed, with the 2 deprecation
  warnings of untouched tests (discovered issue 42), and 9 shell tests (with a scratch shellcheck). On these records:
  `make qa-trace` passed (requirements 170, architecture 34, design 131, tests 386, coverage gaps 113; gap gate
  against the merge-base of `origin/poc/agentic-sdlc`: 0 new), `make docs-check` (15 live documents), `make lint` (0
  new or worsened findings), `make test-lint`, `make unit-guard-check` (357 passed) and `make qa-deploy` (18 known
  violations, 22 warnings) passed. Not run: `make gate-consistency` (round 3 changed no CI job, Makefile target or
  Quality gates row); the full E2E suite (`git diff --name-only 4cb7e9b fa7953f` lists `AGENTS.md`, the plan list, the launcher, the
  inputs, the benchmark runner and its key, their tooling tests and fake, the decision page and the benchmark's
  result files: no service, policy, compose, harness or CI file; CI's `e2e` job runs it on the PR), `make unit-trust`,
  `make unit-mutation` and `make unit-diff-cov` (no `services/` change), and CI (the branch is not pushed).
- Review: the unit `round-3` has not run; it waits for the owner's decision on decision concern 18. Discovered issues
  44 to 55 are on the decision page; of the replays' new findings, the growth replay's G2-1 (medium) and part of the
  mechanics replay's R2-1 (high) still hold at HEAD and are open.

## 2026-11-16 Slice agentic-sdlc-poc 4: the owner's decisions on decision concerns 11 and 13

- Branch `poc/slice-4-implementation`, 5 commits `5941c56` to `03c02c0`, then their records; then the fixes to their
  review's round 1, 3 commits `10f2977` to `f22bb89`, and these records: the owner's decisions of 2026-11-16, in the owner's words on the [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md) ("okay go
  ahead and also increase the review counts to 85", in reply to the author's explanation of decision concern 13, which
  recommended option B). Logged under
  [DPL-013](../delivery_problem_log.md#dpl-013-review-severity-decided-what-got-fixed-a-rejection-could-stand-on-the-authors-word-and-fixes-grew-the-process).
- Decision concern 13, option B (`5941c56`, the launcher's wording only, in its own commit as decision 2 asks;
  `42aef6a`, the rulebook): the mechanism wording in `MECHANISM_RULES` and the output section's kind bullet of
  `scripts/run_independent_review.py` now counts "a step that is added or repeated (such as "again after every push")
  and a second copy of a fact that must be kept current" as mechanisms; an initial review reports an unapproved
  mechanism as a `defect`, not a `simpler_alternative`; a recheck re-raises a fix that adds one at the finding's
  severity; a simpler alternative is a mechanism the owner approved. Both recheck wordings share the output section.
  `AGENTS.md` says the same (Fixes stay within the agreed decisions, Report sections; Modes and prompts links to the
  definition instead of repeating it). The stage checklists are not changed.
- Decision concern 11 (`ed061ba`): the owner confirmed the stage-B budget of 85, so the hard stop (`BUDGETS["B"]`)
  goes from 80 to 85, equal to the key's `budget: 85`. The runner checks the key's budget against the hard stop again,
  besides the run's, so a plain `--run` works and round 2's `--budget` workaround is gone.
- RC-3 again (`6627268`, `03c02c0`): calls 81 and 82 of 85, by a plain `--run` with `--case RC-3` and both recheck
  configurations, under the pinned install of CLI 2.1.323 in a scratch folder whose canary is done; both completed at
  the first try and re-raised R1-1 at high, verdict no, with no new finding (`recheck-A` USD 0.23, 0.3 minutes;
  `recheck-B` USD 0.22, 0.2 minutes). The two re-raises were appended to the third export as `M147` and `M148`
  without reshuffling its 146 rows; a fresh session, given only those two rows and the match rule, judged both a
  match (decision concern 16 applies). Under R2-9 the recheck rows read 2 of 3 with RC-3 under R2-5's wording and 3
  of 3 under decision concern 13's; the runner's own report counts both RC-3 runs and reads 3 of 4. The report
  ([`benchmark_report.md`](../slices/poc-4-5-benchmark/benchmark_report.md)) says what this cannot show: the
  wording's example is RC-3's own answer phrase, RC-3's reviewers got the base `e842e97`'s rulebook, which only
  prefers removing a mechanism, and with one run per wording there is no rate; RC-2 and the initial cases did not run
  under the new wording.
- Tests first, rerun for this entry in a scratch clone of each parent commit with the commit's test file:
  - Launcher (base `e2399c7`, `python3 -m pytest -q -p no:cacheprovider --tb=line
    tests/tools/test_run_independent_review.py -k "<names>"`; 2 failed):
    `test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism` `:1635 assert 'a step that is added or
    repeated (such as "again after every push")' in "Mechanisms: ask whether the change adds a mechanism …"`;
    `test_a_simpler_alternative_is_only_a_mechanism_the_owner_approved` `:1662 AssertionError` (the narrowed
    `simpler_alternative` bullet is not in the output section). The rulebook commit `42aef6a` is rule text only.
  - Runner (base `42aef6a`, `python3 -m pytest -q -p no:cacheprovider --tb=line tests/tools/test_run_review_benchmark.py
    -k "<names>"`; 3 failed): `test_stage_b_stops_at_its_budget_counting_retries_and_the_canary`
    `:307 assert 80 == 85`; `test_a_key_whose_budget_is_above_the_hard_stop_is_refused_though_the_runs_budget_is_within_it`
    `:1511 assert (0 == 2)` (the run naming `--budget 80` ran instead of being refused);
    `test_the_committed_keys_budget_is_the_stage_b_hard_stop` `:1518 assert 85 == 80`.
- Validation, local, on `03c02c0` (the commits after it change only `docs/`): `make qa-quality` passed (qa-trace in PR
  mode against `origin/poc/agentic-sdlc`: requirements 170, architecture 34, design 131, tests 386, coverage gaps
  113, 0 new; unit traceability with 28 mapped requirements, the unit guard over 357 tests, docs-check, test-lint, and
  qa-deploy with 18 known violations and 22 warnings); `make tooling-test` 929 passed and 9 shell tests (with a
  scratch shellcheck); `make lint` passed (0 new or worsened findings); `make unit-guard-check` and
  `make gate-consistency` passed. Not run: the full E2E suite (`git diff --name-only e2399c7 03c02c0` lists
  `AGENTS.md`, the launcher, the benchmark runner, their two tooling tests and the benchmark's report and result
  files: no service, policy, compose, harness or CI file, and none since the last E2E run on `11667c5`; CI's `e2e` job
  runs it on the PR), `make unit-trust`, `make unit-mutation` and `make unit-diff-cov` (no `services/` change), and CI
  (the branch is not pushed).
- Review, unit `owner-decisions-2`, round 1 (attempt `owner-decisions-2/c1/r1/A/1`, Opus, high effort, on `f0eb19e`):
  approvable; 0 blocking, 0 high, 4 medium, 2 low, each answered in the
  [review record](../slices/agentic-sdlc-poc/review_owner_decisions_2.md):
  - F1 (medium), fixed: a mechanism added without the owner's approval is a `defect` of at least `medium` severity, so
    it is fixed (R2-1), in the launcher's `MECHANISM_RULES["initial"]` and the output section's kind bullet
    (`10f2977`, wording only, in its own commit as decision 2 asks) and in `AGENTS.md` (Report sections, Modes and
    prompts; `db39dd5`). Before, only the recheck half named a severity.
  - F2 (medium), fixed: the mechanism definition's example, "again after every push", RC-3's own answer phrase, which
    the owner's option B does not hold, is removed from `_MECHANISM` (`10f2977`) and from `AGENTS.md` (Fixes stay
    within the agreed decisions; `db39dd5`). RC-3's two re-raises of 2026-11-16 (calls 81 and 82) ran with the
    example, so the shipped wording is unmeasured; the benchmark report, decision concern 13 and DPL-013 say so, and
    the stored results are unchanged.
  - F3 (medium), fixed (`f22bb89`): the benchmark's `leak_hits` reads the whole prompt each configuration builds
    (`case_prompt(...).prompt`, what the reviewer is sent) in place of the rules, the upstream items and the task with
    its configuration's prompt files, which that prompt holds; the copy is scanned as before, and `_prompt_text` is
    gone. This also covers a recheck case's earlier report and answers (discovered issue 28). `--dry-run` over every
    case afterwards: 20 of 20 cases pass the leak search, 67 prompts built, as before the change; no case hits a leak
    term.
  - F4 (medium, decision concern): to the owner as decision concern 17 (good fixes that add what a rule requires may
    be re-raised; RC-3 and RC-2 under the shipped wording, 4 calls, the budget to 89).
  - F5 (low), rejected: the prompt carries its own copy of the definition while this branch is unmerged, since the
    reviewer receives the base branch's `AGENTS.md`; discovered issue 41, after the merge.
  - F6 (low, simpler alternative), rejected: the key's `budget` is part of the hashed answer key, and the two copies
    are pinned equal by a test and checked before any call.
- Tests first for the fixes, rerun in a scratch clone of each parent commit with the commit's test file:
  - Launcher (base `f0eb19e`, `python3 -m pytest -q -p no:cacheprovider --tb=line
    tests/tools/test_run_independent_review.py -k "<names>"`; 2 failed):
    `test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism` `:1636 assert 'a step that is added or
    repeated and a second copy of a fact that must be kept current are mechanisms too' in "Mechanisms: a mecha…"`;
    `test_a_simpler_alternative_is_only_a_mechanism_the_owner_approved` `:1665 AssertionError` (the kind bullet with
    "of at least `medium` severity" is not in the output section). The rulebook commit `db39dd5` is rule text only.
  - Runner (base `db39dd5`, `python3 -m pytest -q -p no:cacheprovider --tb=line tests/tools/test_run_review_benchmark.py
    -k "<names>"`; 5 failed): the three cases of
    `test_a_leak_term_only_in_a_part_of_the_prompt_the_launcher_builds_is_found` (a term only in the initial or the
    recheck mechanism rule, or only in a recheck case's answers) `:239 AssertionError: assert [] == ['prompt (…):
    SECRET-LEAK-TERM', …]`, after the twin's assertion that the case without the term passes (`:232`) held; and
    `test_problem_id_or_leak_term_in_the_inputs_is_refused[rules-prompt]` and `[task-prompt]` `:208 assert False` (the
    earlier search labelled such a hit `rules` or `task`, not `prompt`).
- Validation of the fixes, local, on `f22bb89` in a clean worktree of that commit (the commits after it change only
  `docs/`): `make qa-quality` passed (qa-trace in PR mode against `origin/poc/agentic-sdlc`: requirements 170,
  architecture 34, design 131, tests 386, coverage gaps 113, 0 new; unit traceability with 28 mapped requirements, the
  unit guard over 357 tests, docs-check over 15 live documents, test-lint, and qa-deploy with 18 known violations and
  22 warnings); `make tooling-test` 932 passed, with 2 deprecation warnings of untouched tests (discovered issue 42),
  and 9 shell tests (with a scratch shellcheck); `make lint` passed (0 new or worsened findings); `make
  unit-guard-check` (357 passed) and `make gate-consistency` passed. Not run, as above: the full E2E suite (no
  service, policy, compose, harness or CI file changed), `make unit-trust`, `make unit-mutation`, `make unit-diff-cov`
  (no `services/` change), and CI (the branch is not pushed).
- Review: round 2 of the unit `owner-decisions-2`, the recheck (`owner-decisions-2/c1/r2/A/1`, medium): approvable; all
  6 answers accepted, F5's and F6's rejections with quotes the launcher checked in the copy; no new finding; the review
  ended. The brief, rebuilt on the decision page, builds over every unit. Discovered issue 43: one uncaptured test
  failure in the first of five reruns of the launcher and benchmark tests, not reproduced in the next four.

## 2026-11-14 Slice agentic-sdlc-poc 4: round 2, the owner's findings on review severity

- Branch `poc/slice-4-implementation`, 15 commits `8a82388` to `c79ed96`: round 2 (R2-1 to R2-10), from the owner's
  findings of 2026-11-14, in the owner's words on the [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md)
  (section "Round 2"); it replaces decision 6. Logged as
  [DPL-013](../delivery_problem_log.md#dpl-013-review-severity-decided-what-got-fixed-a-rejection-could-stand-on-the-authors-word-and-fixes-grew-the-process).
- The answer rules (R2-1 to R2-4, R2-8; `8a82388`, `5e62097`, `83eabdf`, `0007f65`): blocking, high and medium
  findings are fixed and take `fixed`, `rejected` or `owner` (a medium finding is no longer deferred); a rejected
  medium finding, like a blocking or high one, stands only when the next round accepts it, and the review loop handles
  a medium finding as a high one, defining the end of a review once (review round 1, F2, replaced `0007f65`'s extra
  clause); a rejection of those severities cites a checkable fact, checked by shape
  only; one dispute round (a re-raised rejection is fixed or goes `owner:`, never `rejected:` again; a later `fixed:`
  settles it; a low finding may be rejected again); a fix adds no mechanism (rule text, `AGENTS.md`, Fixes stay within
  the agreed decisions); the brief lists medium rejections. A probe of every record the check reads (23 attempts, 107
  answer rows) found none that the new rules refuse, so no transition rule was added.
- The review prompt and the recheck (R2-5 to R2-7; `67b0402`, `f884421`, `a549e19`, `7b524b2`, `6e88d19`,
  `f8f19c5`): the answer rules live once in `scripts/run_independent_review.py` (`FIXED_SEVERITIES`,
  `ALLOWED_ANSWERS`, `CHECKABLE_FACT`, `answer_rule_problems`), and the launcher refuses before a recheck what
  `make docs-check` refuses after; a finding a recheck accounted `cannot determine` can be answered `fixed:` or
  `owner:` (before, its record could never turn green). The output section, shared by every mandate wording, asks an
  initial review whether the change adds a mechanism without the owner's approval where changing a choice would do,
  and a recheck the same of each `fixed:` answer; the final review gets no such question. This wording is its own
  commit, `7b524b2`. A recheck's evidence lists every process file (`PROCESS_FILES` in `scripts/review_inputs.py`)
  changed since the reviewed round, with line counts; a recheck quotes the lines each rejection it accepts or re-raises
  rests on, and the launcher checks each quote in the copy (whitespace aside, Read line prefixes dropped, within the
  named lines give or take two; since review round 1, F3, also from a file the attempt read, holding a whole line, and
  for a rejection that cites files, at least one quote from one of them).
- The benchmark (R2-9, R2-10; `294d85b`, `ff276bc`, committed before any run, `e4943aa`, `7fd4723`, `c79ed96`): a
  match rated medium counts as detected, and a medium finding on a no-defect case as a false alarm; the earlier results
  are re-scored apart (`--rescore B`, which writes nothing unless the earlier rule reproduces every recorded score: 62
  of 62); the 146 findings no earlier export held were judged blind by a fresh session (15 match); stage A is not
  re-scored. First runs, blocking or high against R2-9: `short+list` 6 and 9 of 11, `open+list` 7 and 8, `open-B+list`
  6 and 8. RC-3 (a `fixed:` answer that adds a step) and RC-4 (a rejection citing a test that does not cover the
  scenario) ran on `recheck-A` and `recheck-B`, base `e842e97`: RC-4 re-raised by both, RC-3 accepted by both. Calls 77
  to 80 of the hard stop of 80, under a pinned install of CLI 2.1.323 in a scratch folder (the installed CLI had
  updated itself to 2.1.325, which has no canary). The key kept `budget: 85`; the runner checked the run's `--budget`
  against the hard stop (until 2026-11-16, entry above). Report: [`benchmark_report.md`](../slices/poc-4-5-benchmark/benchmark_report.md).
- Tests first, the failures on the base of each change:
  - Record check and brief (base `4316724`, `python3 -m pytest -q --tb=line tests/tools/test_check_review_records.py
    tests/tools/test_review_brief.py`; 13 failed): `…next_round_accepts_passes[medium]` `:299 assert False`;
    `…cites_no_checkable_fact_fails` (5 cases) `:331 AssertionError: []`; `…rules_do_not_allow_fails[medium-deferred,
    medium-rejected-alone]` `:357 AssertionError: []`; `…answered_rejected_again_fails[blocking, high]` `:449`, only the
    old "no later round accepted" message, `[medium]` `:449 AssertionError: []`;
    `…answered_with_a_fix_settles_the_rejection` `:456`; `test_the_brief_lists_every_item_the_owner_must_see`
    `test_review_brief.py:66`, heading missing. Passing on the base by design: the 10 fact shapes, low-deferred,
    medium-owner, the re-raised low finding, a re-raised fix rejected once.
  - Launcher (base `83eabdf`, `python3 -m pytest -q -p no:cacheprovider --tb=line <ids>`):
    `…refused_before_the_recheck[3]` `:1410 assert 1 == 2`; `…did_not_accept…`, the undetermined cases `:1447` (refused
    "answer row for X1, which the report does not hold"), the re-raised cases `:1424 assert 1 == 0`;
    `…quote_counts…[10]` `:1485/1487`, fields differ from the schema; `…is_quoted` 5 of 7 `:1513` (the two twins pass);
    `…wrong_shape[7]` `:1527`; `…schema_offers_quotes…` `:1532 KeyError: 'quotes'`; `…process_file_changed…`
    `:1548 assert 0 == 1`; `…no_process_file_change…` `:1569`; `…adds_a_mechanism` `:1576 AttributeError
    MECHANISM_RULES`; `…severity_rule_and_the_quote_rule` `:1598`; `test_review_inputs.py:699/710 AttributeError
    is_process_file / process_file_evidence`; record check `:525` no attribute `answer_rule_problems`, `:557` (4
    cases), `:564`, `:436`; benchmark `:1365 AttributeError MECHANISM_RULES`, `:1384 'completed' == 'failed'`,
    `:1396 DID NOT RAISE`; brief `test_review_brief.py:54 assert 1 == 0`. Tests that need a quote could fail on the
    old schema only ("fields differ").
  - Benchmark (the runner of the previous commit, `python3 -m pytest -q --tb=line
    tests/tools/test_run_review_benchmark.py -k <names>`): R2-9's medium detection `assert ([] == ['E1']`, medium false
    alarm `assert ([] == ['X1']`, the case that holds `assert [] == ['R1-2']`, the measurement's export
    `assert (8 == 12)`, the re-score report `assert 0 == 2`, the re-score refusal `invalid choice: 'B'`, the third
    export's not yet confirmed `'0'`, the rating agreement a dict mismatch, the unjudged fix `assert '0' == '1'`;
    R2-10's budget `assert 76 == 80`, a run within the hard stop `assert (2 == 0)`, the recheck line
    `no attribute 'false_answer_line'`. Not red: `test_a_false_rejection_is_scored_as_a_false_fix_is` (the scorer was
    already generic; kept as a regression test).
  - Review round 1, F3, the quote check (base `2270e4a`, `python3 -m pytest -q -p no:cacheprovider --tb=line
    tests/tools/test_run_independent_review.py -k "a_quote_comes_from_a_file or holds_at_least_one_whole_line"`; 4
    failed, 5 passed): `[quote-from-an-unread-file]` and `[quotes-only-from-uncited-files]` `:1544 assert (0 == 1)`,
    `[one-word]` and `[parts-of-two-lines]` `:1566 assert (0 == 1)` (each recheck completed); the five twins pass.
    After the change, `test_a_rejection_counts_only_when_the_files_it_cites_were_read[cited-file-read]` quotes the file
    its answer cites instead of the reviewed file.
  - The brief over a frozen record (base `e621f36`, `python3 -m pytest -q -p no:cacheprovider --tb=line
    tests/tools/test_review_brief.py -k before_4_3`; 1 failed, 1 passed): `[True]` `review_brief.BriefError: the
    records cannot give a complete brief`; the twin `[False]` (the record check reads the attempt) passes. Fixed in
    `5245997`: from `f884421` the brief applied today's answer rules to attempts logged before slice 4.3, so
    `python3 scripts/review_brief.py --base origin/poc/agentic-sdlc` refused to build over 4.1's medium finding
    answered `deferred: #42` (discovered issue 35); it builds again.
- Review round 1 of unit `round-2` (record `docs/slices/agentic-sdlc-poc/review_round_2.md`): attempt 1 failed the
  read check (discovered issue 36); attempt 2 not approvable: 2 high, 2 medium, 3 low. Fixed (`6d8de53` to
  `cdfce97`): F1, the stage-table test's `DISCOVERY_EXIT` held the exit cell `eb46b58` had rewritten, so
  `make tooling-test` failed (discovered issue 34); F2, the review loop handles a medium finding as a high one and
  states the end of a review once; F3, a quote counts only from a file the attempt read, with a whole line, and a
  rejection that cites files is quoted from one of them (`QUOTE_RULE` in its own commit, `99eee9e`); F5, the call
  numbers below; F7, discovered issue 35 (frozen records the check does not read). F4 went to the owner as decision
  concern 16; F6 was rejected with the lines it rests on. Answers committed in `03ffc55`. Round 2, the recheck
  (`round-2/c1/r2/A/1`, medium): approvable; all 7 answers accepted, F6's rejection with three quotes the launcher
  checked in the copy; 1 new low, F8 (the validation named `1f224d1`, not the reviewed commit), fixed in `05c0894`;
  the review ended. The brief, rebuilt on the decision page (`40aecde`), builds over every unit.
- Validation, local, on `1f224d1` (after the brief's fix; first on `03ffc55`, with 925 tooling tests): `make qa-quality` passed (qa-trace in PR mode against `origin/poc/agentic-sdlc`:
  requirements 170, architecture 34, design 131, tests 386, coverage gaps 113, 0 new; docs-check, test-lint, and
  qa-deploy with 18 known violations and 22 warnings); `make tooling-test` 927 passed and 9 shell tests (with a scratch
  shellcheck); `make lint` passed (0 new or worsened findings); `make unit-guard-check` and `make gate-consistency`
  passed. Not run: the full E2E suite (`git diff --name-only 4316724 1f224d1` lists no service, policy, compose,
  harness or CI file; CI's `e2e` job runs it on the PR), `make unit-trust`, `make unit-mutation` and
  `make unit-diff-cov` (no `services/` change), and CI (the branch is not pushed). The validation on `c79ed96` before
  the review had passed `make tooling-test` with 916 tests, but `eb46b58` came after it and was not rerun (F1).
- Review: unit `round-2` of `docs/slices/agentic-sdlc-poc/`, round 1, then round 2 (the recheck), approvable; the review ended (the round-1 and round-2 bullets above).

## 2026-11-13 Slice agentic-sdlc-poc 4: the owner's decisions on the decision concerns

- Branch `poc/slice-4-implementation`, commits `44a040c` to `ea4e100` and the commit with the fixes to their review:
  the owner's decisions of 2026-11-13 on decision concerns 2, 3, 4, 7, 8 and 10, in the owner's words on the
  [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md). Decision concerns 2 and 3 keep what was built.
- Small slices (decision concern 7): `AGENTS.md` (Slice workflow, Small slices, Discovery, Final review) defines a
  small slice by four conditions and runs it as one PR whose review units are the plan review and the implementation
  review, with no final review; the plan template's Small slice part asks why each condition holds.
- The decision page (decision concern 10): every slice starts `decisions.md` from `docs/slices/_template/`; it holds
  the decision brief, the implementation review's findings on the test-plan questions and every discovered issue,
  and the PR body states the goal and what changed and links it. `scripts/review_brief.py` no longer reads or prints
  a CI result.
- RC-2 (decision concern 4): a recheck case whose answers hold (a correct rejection beside a correct fix), answer key
  version 3. On both recheck wordings: `recheck-B` accepted both answers, `recheck-A` failed the launcher's read check.
- The budget: stage B's 60 calls raised to 85 for the canary, RC-2 and the measurement (key version 4); 76 spent. The
  runner's hard stop is now 76, so no further stage-B call runs without a new decision (decision concern 11).
- A canary per CLI version: the CLI updated itself from 2.1.321 to 2.1.323 mid-benchmark; a canary now counts as done
  only for its own CLI version, and a new pair under 2.1.323 is valid and passed.
- Severity (decision concern 8): the [analysis](../slices/poc-4-5-benchmark/severity_analysis.md) found that reviewers
  rate a failure scenario's first symptom, often under base rules that support the low rating. Its candidate "finish
  the scenario" ran as `open+list+sev` on the 15 initial-review cases and was judged blind against criteria fixed
  before the runs: worse (RM-3 and RM-4 still medium, RM-6 lost, two extra blocking or high findings on CL-1), so
  nothing is adopted. The launcher's output section and `AGENTS.md` stay as they were; decision 6 asks the owner what
  to do instead.
- Review: unit `owner-decisions` of `docs/slices/agentic-sdlc-poc/`, round 1: attempt 1 failed the read check
  (discovered issue 21); attempt 2 not approvable, 1 blocking, 2 high, 5 medium. The fixes: the implementation review
  answers the test-plan questions as findings; condition 4 counts the change, not the bundle or the handoff files;
  the confirmation's two departures from the plan are recorded; the report holds the clusters' severities; a test of
  the severity file's refusal. Decision 7, decision concern 11 and growth proposal 12 go to the owner.
  Round 2: attempt 1 failed the read check again; attempt 2 approvable, all 8 answers accepted, no new finding; the
  review ended after round 2.
- Validation, local: `make tooling-test` 800 passed and 9 shell tests (with a scratch shellcheck); `ruff check
  services scripts` clean; `make lint` against `origin/poc/agentic-sdlc` passed (0 new or worsened findings);
  `make docs-check` passed on the commit, in a clone without this review's record, which fails it in the working
  tree until its answers are written. Not run: the E2E suite (`git diff --stat 2da4333 HEAD` lists only rulebook,
  document, template, review-tooling and test files, no service, harness or compose file) and CI (the branch is not
  pushed).

## 2026-11-13 Slice agentic-sdlc-poc 4: the owner's growth to the review launcher

- Branch `poc/slice-4-implementation`, after the final review; approved by the owner on 2026-11-13 ("yes, replace it
  and implement both with proposal 9"; [decision page](../slices/agentic-sdlc-poc/slice_4_decisions.md)).
- `scripts/run_independent_review.py`: a recheck must read every file a `rejected:` answer cites, as for a `fixed:`
  answer, with or without a directory part (`AGENTS.md`, `Makefile`), and a cited path the copy does not hold is
  refused before any call; a reviewer lists files it only searched under `searched`, so `opened` stays a checked
  claim; a finding may name the checklist question that prompted it (`question`, for example `code:10`). An entry
  logged with the earlier report schema is refused for a rebuild. `scripts/run_review_benchmark.py`: the report counts
  the findings that name their question (0 for the stage-B runs, which predate the field).
- Decision concern 1 is resolved; the decision page records why the first proposal was withdrawn (DPL-012).
- Review: unit `growth` of `docs/slices/agentic-sdlc-poc/` ([record](../slices/agentic-sdlc-poc/review_growth.md)).
- Validation, local: `make tooling-test` 786 passed (with a scratch shellcheck); `make qa-quality` and the trace gate
  in PR mode passed (0 new gaps); `make lint` passed. Not run: the E2E suite (no service, harness or compose file
  changed since the 2026-11-10 run) and CI (the branch is not pushed).

## 2026-11-10 Slice agentic-sdlc-poc 4: review prompts, inputs, records, stage checklists, benchmark, stage rules

- Branch `poc/slice-4-implementation`, from `poc/agentic-sdlc` at `3347754` (plan PR #48), local until the owner
  pushes; one final PR with a section per sub-issue (#38 to #43). The owner's decision page, with every author
  decision, decision concern, growth proposal and discovered issue:
  [`slice_4_decisions.md`](../slices/agentic-sdlc-poc/slice_4_decisions.md).
- 4.1 (#38): the launcher writes every prompt in fixed sections, opening with the mandate of the review's mode
  (initial, recheck, final), with quoted text fenced; findings carry a severity, a kind and an origin stage; rechecks
  account for every answer and must read the files a `fixed:` answer names.
- 4.2 (#39): the files under review come from the diff; upstream items and evidence (uncovered changed lines, trace
  gaps, CI results) are computed in a scratch clone (`scripts/review_inputs.py`).
- 4.3 (#40): the launcher writes the review record, and `make docs-check` checks every record against its attempt
  log and every answer against its finding (`scripts/review_records.py`, `scripts/check_review_records.py`).
- 4.4 (#41): six stage checklists in `docs/review_checklists/` from researched sources
  (`docs/slices/poc-4-4-stage-checklists/research.md`), critiqued by Opus and Sonnet; `--stage` reads a list from
  the base commit.
- 4.5 (#42): the stage-B benchmark (`scripts/run_review_benchmark.py`, `tests/review_benchmark/`) ran within 57 of
  60 reviewer calls; the report is [`benchmark_report.md`](../slices/poc-4-5-benchmark/benchmark_report.md):
  `open+list` 7 of 11 defect cases, `short+list` 6, `open-B+list` 6, both recheck wordings 1 of 1, all within
  chance. The launcher's mandates stay 4.1's until the owner chooses.
- 4.6 (#43): `AGENTS.md`'s slice workflow has seven stages, each with its review, list, checks and exit; the
  templates carry the stage table, decision sources and rule deviations; `scripts/review_brief.py` builds a PR's
  decision brief; the grill-me skill lives in `.claude/skills/grill-me/`.
- Reviews: every sub-issue's implementation review ended with no blocking or high finding open (records in each
  bundle); 4.4 had a two-model critique; a dry slice from a clean session recorded 18 trip points, in the decision
  page. The final review of the slice is the unit `final` of `docs/slices/agentic-sdlc-poc/`.
- Validation, local (CI's verdict comes when the owner pushes): `make tooling-test` 764 passed (with a scratch
  shellcheck; this machine has none installed); `make qa-quality` passed (qa-trace, traceability, unit guard,
  docs-check, test-lint, qa-deploy); `make lint` passed; the full E2E suite on a clean stack passed 120 of 120 with
  one warning (M5-T55, live Jira not configured, skipped by its env gate); `make qa-evidence` passed (119 validated,
  1 skipped). Not run: CI (the branch is not pushed) and `make unit-diff-cov` and `make unit-mutation` as CI runs
  them on a PR (slice 4 changes no service code).

## 2026-11-08 Fixes to the review launcher and the secret check (slice 4 plan branch)

- Branch `poc/slice-4-plans`, commits `f070669`, `d56c69a`, `f8b6200`, `8d80ce8` and the commit that ends a
  credential value at a backslash
  ([plan](../slices/agentic-sdlc-poc/plan_launcher_fixes.md), [DPL-011](../delivery_problem_log.md#dpl-011-slice-2s-launcher-and-the-secret-check-broke-on-slice-4s-parallel-plan-reviews)).
- `scripts/run_independent_review.py`: report paths hold the slice directory; a call to a tool the
  session's init event did not offer, answered with an error, is logged (`other_tools_not_offered`)
  instead of failing the review.
- `scripts/evidence_secrets.py`: a credential line needs a token-like value (20 characters or more, or
  a digit), found also in code spans and quotes, and ending at a backslash; `AGENTS.md`'s E2E evidence row, `docs/test_spec.md`
  (EVID-T1) and `trace/tests.yaml` (a new negative control) say so.
- Validation: `pytest tests/tools/test_evidence_secrets.py tests/tools/test_run_independent_review.py`
  140 passed; `make qa-trace`, `make docs-check` and `make lint` passed. The full tooling suite has
  9 failures here, all in the shellcheck tests, which need shellcheck (not installed locally; CI runs
  them). The E2E suite was not run. The new secret check finds nothing in the local
  evidence of the 2026-11-07 full run (`test_report.log`, `artifacts/rogue-tests/`,
  `artifacts/quality/`); the PR's `e2e` job runs the suite and `make qa-evidence`.
- Review: unit `launcher_fixes`, round 1, verdict yes, with four medium, two low findings and one
  decision concern ([record](../slices/agentic-sdlc-poc/review_launcher_fixes.md)).

## 2026-11-08 Slice agentic-sdlc-poc 3: changed-files lint

- Branch `poc/slice-3-changed-files-lint`, built on `poc/slice-2-review-launcher` and rebased onto
  `poc/agentic-sdlc` after PR #35 merged. `git range-diff` showed every code commit unchanged; two
  commits changed only where conflicts in the status lines and the shared attempt log were resolved.
- `make lint` (`scripts/lint_changed_files.py`): for every file the change adds, modifies or renames,
  ruff and shellcheck run on the merge-base and the new version; a finding key (file, rule, enclosing
  function or line text) that occurs more often or with a higher value fails, so existing violations
  stay and a pure rename keeps its key. By the owner's answer in PR #34 (coding rule 8 covers every
  file), added Markdown files need a `#` title and a paragraph too. `ruff_changed_files.toml`, read
  from the merge-base: ruff's
  default rules, C901 ≤ 10, PLR0912/0913/0915 (12 branches, 5 arguments, 50 statements), N, S (except
  `assert` in `tests/`); the limit, naming, F401 and F841 rules run with `--ignore-noqa`. Added
  Python, shell, YAML, TOML, Dockerfile and Rego files need a purpose comment. A missing base or tool
  fails the run.
- CI job `lint` (PRs only); `requirements-dev.txt` pins `ruff==0.15.18` and `shellcheck-py==0.11.0.1`;
  `RULESET_URL` names the `poc/agentic-sdlc` ruleset, so `gate-consistency` checks the integration
  branch's required checks. `AGENTS.md`: a gates row for `lint`; the not-gated standards keep only the
  whole-tree `ruff check` and the debt list. `docs/STATUS.md`: the complexity debt re-measured with
  ruff C901 (12 functions, radon counted 16).
- Review: four rounds through the launcher ([`review_slice_3.md`](../slices/agentic-sdlc-poc/review_slice_3.md)).
  Round 1 found two test gaps that let a regression pass (no `__init__.py` without a docstring; tool
  directives never run on the comment-header file types), both fixed with tests, and six advisories
  (tool errors, stale "main ruleset" wording, binary files, a merge-base test that could not fail,
  names, loose header assertions), all fixed; round 2 accepted every answer. Round 3 reviewed the
  Markdown check added for the owner's answer in PR #34 (verdict yes; its advisory fixed after the
  round). Round 4, an open-mandate review with the review record and attempt log as evidence (the
  lesson of DPL-010), found two blockers: no test ran the gate on a modified or renamed shell script,
  and these records were stale. Both are fixed, as are five advisories (a syntax-error test, a
  missing-shellcheck test, a note that uncommitted changes are not linted, Dockerfile parser
  directives, wording). The rest are slice-4 inputs.
- Validation: `make lint` passes against `origin/poc/agentic-sdlc`, and `make qa-quality` (qa-trace,
  unit traceability, unit guard, docs-check, test-lint, qa-deploy) passes. `make tooling-test`: all
  tests pass locally except the 9 shell cases of `tests/tools/test_lint_changed_files.py`, which
  need `shellcheck` (not installable on this machine). They run for the first time on the reviewed
  commit in the PR's CI; an earlier CI run (`workflow_dispatch` on `a09ab0d`) passed the 6 shell
  cases that existed then. In that run gate-consistency failed only on "CI job lint is not a required
  check", which the owner's user action 2 resolves. Deliberately breaking the gate (honouring `noqa`
  on limits, reading the configuration from the change, ignoring the value, no rename matching, no
  header check) made at least one test fail each time. Full E2E suite on a clean stack at `89c9cbe`:
  120/120 passed, 1 warning (M5-T55, env-gated skip); then `make qa-deploy` with image users inspected
  and `make qa-evidence` (validated 119, skipped 1) passed; the later changes touch only the lint
  gate, its tests and documents, no runtime code.
- When the PoC merges into `main`, reset `RULESET_URL` to the `main` ruleset and the `Makefile`
  default `BASE_REF`, reword the `CODEOWNERS` comment, and decide whether `lint` becomes a required
  check on `main`.

## 2026-11-08 Slice agentic-sdlc-poc 2: review launcher and benchmark

- Branch `poc/slice-2-review-launcher`, built on `poc/slice-1-rules` (slice 1) and rebased onto
  `poc/agentic-sdlc` after PR #34 merged; `git range-diff` showed every slice-2 commit unchanged.
- `scripts/run_independent_review.py`: one review round per invocation. Each reviewer is a fresh
  headless Claude session in a frozen `git archive` copy without the unit's review record and attempt
  log, with only Read, Grep and Glob, `--safe-mode`, `--setting-sources ""`, `dontAsk`, no MCP servers,
  no saved session and only `PATH`, `HOME` and `LANG`; the approved rules come from the fetched base
  branch, the change as a diff without the withheld files. The append-only attempt log
  (`docs/slices/<id>/review_attempts.jsonl`, under an OS lock) admits rounds (POC-D4: round 1 plus
  three fix rounds, an extension or reset reference used once), marks interrupted attempts and
  releases a report only after its end entry. Paused, failed, pending, empty and escaped reviews and
  the publication check fail closed; `invocation_from_entry` rebuilds an entry's call and hashes.
- `scripts/run_review_benchmark.py` and `tests/review_benchmark/` (answer key, two prompts, four
  planted patches): leak search before every case, deterministic scoring, a 26-call budget that holds
  across invocations, a stop at a usage limit with resume, the canary and its twin. Stage A ran 24
  calls; the [report](../slices/agentic-sdlc-poc/benchmark_report.md) recommends the short prompt
  and one reviewer, a fix for the empty-review rule that failed 5 of 22 reviews, review questions
  for defects of absence (DPL-004, DPL-005: neither prompt found them) and a severity rule for
  secrets in evidence (DPL-002: seen, but rated advisory); 1 of 4 paired real misses detected.
- `AGENTS.md`: reviews run through the launcher; the review record keeps task prompts and reports.
- Review: six rounds through the launcher ([`review_slice_2.md`](../slices/agentic-sdlc-poc/review_slice_2.md)).
  Round 1 found two blockers in the code (a canary that passed without a completed run; a budget
  that held only within one invocation), both fixed with tests; round 2 accepted every answer.
  Round 3 reviewed the report and close-out: its first attempt failed closed (a call named a path
  outside the copy, probably a Markdown link resolved from the copy root; the cause cannot be
  confirmed, because the CLI did not deny that call and the log then kept no detail); the rerun found that the report
  missed an advisory finding on DPL-002, fixed in the report and in the scoring; round 4 rechecked.
  Round 5, an extension the owner asked for before merging, had an open mandate, the coverage report
  and the record and attempt log as evidence. It found two blockers that rounds 1 to 4 missed: a
  failed Read counted as reading a file, and the record kept prompts with placeholders and reports
  only rendered, so the log's hashes matched nothing in the repository. Both are fixed; the record
  now keeps every prompt and report verbatim (checked against the log). Of its advisories, four are
  fixed (an advisory-only column, outside calls logged with their tool and denial, any tool other
  than Read, Grep or Glob fails the review, overstated counts and claims), the simpler alternative
  is not applied, and the rest are slice-4 inputs (issue #33) and slice-7 inputs (issue #36).
  Round 6, a recheck the owner asked for, opened the changed code for every answer and accepted
  them all. Its advisories led to a test for the advisory-only column, a probe of how the CLI
  reports a failed Read (CLI 2.1.319: an error result with the matching call ID, as the fix
  assumes), and DPL-010 in the delivery problem log.
- Validation: `make tooling-test` (332 pytest, 9 shell) and `make qa-quality` passed. Deliberately
  breaking the main confinement, admission, budget and canary rules made at least one test fail; not
  every defensive refusal path has a test (round 5). No
  service, compose file or E2E harness changed. Full E2E suite on a clean stack at `642b840`: 120/120
  passed, 1 warning (M5-T55, env-gated skip); then `make qa-deploy` with image users inspected and
  `make qa-evidence` (validated 119, skipped 1) passed.

## 2026-11-07 Slice agentic-sdlc-poc 1: the PoC's rules

- Branch `poc/slice-1-rules`, from `poc/agentic-sdlc` after PR #31 (the plan for slices 1–3).
- `AGENTS.md`: "Ask before growing" asks for the failure a new check catches, its cost and the
  simpler alternative (POC-D6); new rules "Threat model changes" (POC-D13) and "Discovered issues"
  (POC-D12), which step 4 carries into the PR body. The review loop has a limit: round 1 plus at most
  three fix rounds, then the user decides (POC-D4); the original reviewer rechecks rejections, and a
  fix goes to the origin with a search for the same cause (POC-D5). The reviewer is a fresh headless
  Claude session in a frozen copy under the base branch's rules, with explicit effort (POC-D3);
  "Models and usage limits" replaces the Codex-first rule (POC-D2). Step 1 implements from the plan
  as merged on the integration branch, by the base branch's rules on a rule-changing branch
  (POC-D15). The Git rules name the integration branch and the PoC branch scheme (POC-D1) and the
  code-owner review (POC-D11). The not-yet-gated standards state the lint limits of POC-D8; coding
  rule 8 asks for a purpose comment in every new file and names that say what things do (POC-D7).
- `.github/CODEOWNERS` names the owner; the `poc/agentic-sdlc` ruleset requires a code-owner review.
- `Makefile`: `BASE_REF` defaults to `origin/poc/agentic-sdlc`; `tests/unit/AGENTS.md` no longer
  hard-codes `origin/main` in its diff-coverage example. The slice templates: `plan.md` asks the
  POC-D6 questions for every check a slice adds; `test_plan.md` no longer names Codex as reviewer.
- The owner's answers in PR #34 (2026-11-08): coding rule 8 covers every file, Markdown included
  (only JSON, JSONL and binary files are exempt), the slice templates start with a purpose
  paragraph, and the template's implementation review gains a names-and-headers question.
- Validation: `make qa-quality` (qa-trace against the merge-base with `origin/poc/agentic-sdlc`: 0
  new gaps; unit traceability, unit guard, docs-check, test-lint, qa-deploy) and `make
  tooling-test` (230 pytest, 9 shell) passed. Full E2E suite on a clean stack at `7ab71c5`: 120/120
  passed, 1 warning (M5-T55, env-gated skip); then `make qa-deploy` with image users inspected and
  `make qa-evidence` (validated 119, skipped 1) passed. No tests added or changed: the slice changes
  rules, and its proof is the independent review ([`review_slice_1.md`](../slices/agentic-sdlc-poc/review_slice_1.md)).

## 2026-10-31 Slice backlog-issues: open work tracked as GitHub issues

- Branch `backlog-issues`, from `main` after PR #12 (slice `ci-evidence-trace` complete).
- The open items of `docs/slices/agentic-delivery-process/later_slices.md` became GitHub issues
  #13 to #18 (labels `slice`, `user-action`): `gate-register`, `asset-classification`, 100%
  coverage, slice 3 (review design and orchestration, which links the frozen drafts at `aa1f0d4`),
  the OPL-005 to OPL-008 pilot, and the "Automatically delete head branches" setting (DPL-008).
  `later_slices.md` is frozen with a note. The user created the issues; the agent session's
  permission check refused issue creation.
- `AGENTS.md`: a "Start here" row for issues; step 4 opens an issue for work found but not done and
  closes finished ones with `Closes #N`. `docs/STATUS.md` and the slice index show slice 2 as
  implemented and link the issues.
- Validation: `make docs-check` and `make qa-quality` (qa-trace, unit traceability, the unit guard
  check over `tests/unit`, docs-check, test-lint, qa-deploy) passed. No tests added or changed; no
  E2E run, `make unit-trust`, `make tooling-test` or mutation run: documents only.

## 2026-10-31 Slice ci-evidence-trace Increment B: trace model

- Branch `slice/ci-evidence-trace-b`, from `main` after PR #11.
- **D4, D5:** `trace/tests.yaml` gains the `static_test` type (requirement, `gate: make <target>`,
  `negative_controls` as `<file>::<test>`, `result`); `DEPLOY-K1` to `DEPLOY-K8`, `DEPLOY-D1`,
  `DEPLOY-D2` and `EVID-T1` for the new REQ-T-R9. `make qa-trace` takes each requirement's status
  from its proofs and the register: K1, K2, K4 not proved (known violations), D2 not proved (grace
  until 2027-01-31), the other six and REQ-T-R9 proved statically. A requirement that is not proved
  is a `requirements_without_proof` gap, so a status change is never a "new" gap. `make qa-deploy`
  writes `artifacts/quality/qa_deploy_report.json` (verdict, findings, inspection flag, compose and
  register SHA-256); `make qa-evidence` accepts only a passing, inspected, matching report. The
  non-root requirement ID sits beside its grace date in `scripts/qa_deploy.py`.
- **D6:** `Implemented by:` on the 13 config-implemented ARCH sections and ARCH-034 (now "Deployment
  Register": the register and compose); DD-925 to DD-930 and `IT-DEPLOY-*` retired (`retired_ids`).
- **D7:** `make qa-trace --mode pr --base <ref>` exports the merge-base tree with `git archive` and
  runs the same script on it, then fails on a gap the branch adds unless `accepted_gaps` lists it;
  `--mode push` reports. CI runs PR mode on PRs (full history) and push mode on `main`.
- **D8:** `make gate-consistency` (new job) checks the `AGENTS.md` CI gates, the `ci.yml` jobs (each
  runs `make <name>`) and the `main` ruleset's required checks; `unit-diff-cov` has its own job.
- **D9:** `AGENTS.md`: every change follows the slice workflow, scaled to its size; trace model,
  static tests, `Implemented by:`, retired IDs, the gap gate. OPL-009 mitigations updated.
- `docs/test_spec.md` is now "Test Specification" with a "Static tests" part; `make docs-check`
  checks static-test heading parity. The trace validator's `main` (complexity 63) is split into
  functions under 10.
- Found on the way: a tooling test ran `qa-deploy` without `--report-json` and overwrote the run's
  report; `qa-evidence` then rejected it (not inspected). Tests now write reports to a temporary path.
- Independent review (Codex, [`review_b.md`](../slices/ci-evidence-trace/review_b.md)): round 1 found
  two blocking issues, both fixed: an incomplete register could turn known violations into static
  proofs (now fails closed), and push mode passed expired or stale accepted gaps (now fails).
  Round 2 re-raised the first with a register asset naming a non-existent requirement (now fails);
  round 3: approvable within the threat model.
- Records: DPL-004 and DPL-005 closed.
- Validation: see `docs/STATUS.md` "Last verification" (full E2E 120/120 on a clean stack,
  `qa-deploy`, `qa-evidence`, `qa-quality`, `tooling-test` PASSED). Not run locally: `unit-trust`,
  `unit-mutation` (no service or unit-test change; CI runs them). `make gate-consistency` fails until
  `gate-consistency` and `unit-diff-cov` are required checks.

## 2026-10-31 Slice ci-evidence-trace Increment A: CI evidence

- Branch `slice/ci-evidence-trace-a`, from the plan as merged on `main` (PR #9 via PR #10).
- **D12:** capiss stores its root key as `capiss_keys/root_key.pem` (Ed25519 PKCS#8 PEM, `0600`);
  an existing file that is not a valid Ed25519 PKCS#8 PEM key stops capiss (fail closed); it never
  reads `root_key.b64`. `scripts/clean_stack.sh` empties `capiss_keys/` through a container. The
  register's K1 location follows. `AGENTS.md` coding rule 7: secrets this repository creates use
  recognisable formats. UT-347 to UT-350; tooling test V13.
- **D2:** `openpolicyagent/opa:1.13.2` and `redis:7.4.8-alpine` (the versions local runs used,
  probed in the images) in compose and the register; tooling test V3.
- **D3:** guards work in a per-test scratch directory (`/tmp/rogue-scratch`, not mounted); at the end
  of each test the harness publishes it to `artifacts/rogue-tests/` with every token-shaped value
  replaced by `sha256:<fingerprint>` (`scripts/evidence_secrets.py publish`). This one central step
  replaces editing the 146 places that write token files, so no premise, exercise or outcome
  changed. `make qa-evidence` runs a shape-only secret check over the publication set
  (`PUBLICATION_SET` in the `Makefile`); on the 2026-10-29 evidence it found 68 token values, on this
  run none. `docs/test_spec.md` notes the fingerprints. Tooling tests V2.
- **D1:** `make e2e` (`scripts/run_e2e.sh`): removes the previous run's report and evidence, builds
  every image, runs the suite, takes back ownership of the root-owned output through a container,
  exits with the suite's code. The CI job `e2e` runs it, then `make qa-deploy` with image users
  inspected and `make qa-evidence`, and uploads the publication set for 14 days only if the secret
  check found nothing. Tooling tests V1 and an upload-step test.
- Found and fixed: `make e2e` first left the previous run's report in place when the suite never
  started, so `qa-evidence` would have passed on it; it now removes them first (V1). The
  diff-coverage gate never measured capiss (DPL-009); fixed with a tooling test.
- Found and recorded: the SPIRE agent can crash on its first start after a reset (OPL-010); the first
  local run never started the suite.
- Independent review (Codex, [`review_a.md`](../slices/ci-evidence-trace/review_a.md)): round 1
  found two blocking issues, both fixed: a publish that failed part way could leave a partial
  evidence directory that passed `qa-evidence` (publishing is now all or nothing and a failure fails
  the run), and an unlistable directory was skipped by the secret scan (now an error). The report
  rescan was removed so the saved `secret_findings` that gates the CI upload is complete. The full
  suite was rerun on a clean stack after the fixes.
- Records: DPL-002 closed; DPL-008 (stacked PR merged into a stale base) and DPL-009 added; `AGENTS.md`
  gate rows for `e2e` and the `qa-evidence` secret contract, step 4, test commands, git rule on
  stacking; ARCH-007, ARCH-012, ARCH-019; OPL-005's key file name.
- CI on the PR: `unit-mutation` failed on UT-347. With `mutate_only_covered_lines`, mutmut runs the
  tests in its own process, then unloads every module they loaded; `cryptography`'s compiled core
  keeps the first import's classes, so `private_bytes(..., NoEncryption())` fails after the reload.
  The mutation-selected tests no longer call `private_bytes`: UT-347 compares public keys, UT-348
  writes the existing key with capiss's encoder, UT-349 drops its EC-key case (the wrong-prefix case
  covers another key type). Reviewed in round 3 of `review_a.md`.
- Validation: see `docs/STATUS.md` "Last verification" (full E2E 120/120 on a clean stack,
  `qa-evidence` and `qa-quality` PASSED, `unit-trust`, `unit-diff-cov` and `unit-mutation` (85.34%)
  PASSED).

## 2026-10-31 Delivery problem log and the rules from the slice 2 plan review

- Docs-only change on `slice/ci-evidence-trace-plan` (PR #9), after PR #8 (review loop) merged.
- New `docs/delivery_problem_log.md`: misses in how we deliver, with root causes, corrective and
  preventive actions and a lesson each; an entry closes only when its preventive action is merged.
  Seven entries: DPL-001 key directory mounted whole (closed by `qa-deploy`, runtime part is
  OPL-005), DPL-002 tokens in evidence (open, slice 2 D3), DPL-003 review rules only in a slice plan
  (closed, PR #7), DPL-004 1B requirements without proof (open, slice 2 D5/D7), DPL-005 gates hidden
  in another CI job (open, slice 2 D8), DPL-006 a failed CI run reported as passing, DPL-007 the 8D
  of plan review rounds 1–4 of slice 2.
- `AGENTS.md`: Start-here row for the log; step 1 records environment facts with their probe;
  step 4 adds or closes delivery problem entries; independent review: fixes stay within the agreed
  decisions, every round may report simpler alternatives and decision concerns, the reviewer may
  check secret-file metadata; quality gates: a gate's result is its CI job's conclusion (DPL-006,
  DPL-007).
- Plan template: an "Environment facts" section. `plan_review.md` of slice 2 points to DPL-007
  instead of "recorded in the session".
- Validation: `make docs-check` PASSED; `make qa-trace` unchanged (138 non-blocking gaps). No
  independent review was run on this docs change.

## 2026-10-30 Slice 1 standing rules moved into the rulebook

- Docs-only change on `docs/durable-slice1-rules`, before slice 2 starts. A sweep of slice 1's
  `plan.md` and `test_plan.md` found twelve rules or decisions that lived only in frozen slice
  records (or in an agent's private notes), where future agents do not read them.
- `AGENTS.md`: grill-me asks the key, socket and secret question (D16); plan approval by merging the
  plan PR (D8); expected-outcome sources and the stop when a probe contradicts the plan (D4, plan
  review note 4); positive twins (D5); static proofs (1B user decision); a new "Independent review"
  section (D11, D17: reviewer, inputs, plan-review record, implementation questions); only the user
  merges (D15), with the note that the `main` ruleset requires no approving review, so GitHub does
  not enforce it.
- Templates: an "Assets and holders" section and a "Rulebook" line in `plan.md`; the twin and probe
  rules next to the expected-outcome table in `test_plan.md`.
- `docs/STATUS.md`: slice 1 complete, slice 2 next; the open mutation decision
  (`mutate_only_covered_lines`) recorded.
- Review loop (user decision, 2026-10-30): the 3-round limit is removed. Rounds continue until no
  blocking finding is open; the author may reject a finding with a checkable reason; a finding still
  disputed after the next round goes to the user. Each plan states the threat model its reviewer
  judges against.
- Validation: `make docs-check` and `make qa-trace`. No code or test changed, so no E2E run.

## 2026-10-29 Increment 1B: deployment register and qa-deploy

- Slice `agentic-delivery-process` 1B on branch `slice/agentic-delivery-process-1b`, after 1A merged
  as PR #5.
- New `REQ-SEC-K1` to `-K8`, `-D1`, `-D2` in `docs/requirements.md`; `security/invariants.yaml`
  (asset locations and holders, the per-service allowlist over every profile, three known-violation
  rows for OPL-005, OPL-006 and OPL-008 expiring 2026-12-31); `scripts/qa_deploy.py` and
  `make qa-deploy` (in `qa-quality`; in CI without image inspection); ARCH-034; tooling tests T-8 to
  T-13 in `tests/tools/test_qa_deploy.py`, including the `07520d7` replay (reports the capiss key in
  `tool-b`).
- User decisions: `rogue-tests` is a declared test-only holder (whole-repo mount plus the Docker
  socket), extended to K7 for the SVIDs it exports into `tmp_svid/`; Python instead of the planned
  Rego.
- Baseline look at Dockerfiles, entrypoints and scripts: no key copies other than the compose
  mounts and the harness exports above (which the first pass missed; review finding C3).
- `AGENTS.md`: quality-gate rows for `make test-lint` (missed in 1A) and `make qa-deploy`, the new
  mutation rule, and the register in "Start here".
- Independent review (Codex, two rounds, `review_1b.md`): C1–C4 fixed; round 2 "approvable". The
  eight generic review questions were tried as part B.
- Validation: full E2E on a clean stack at `ce465a8` 120/120 (1 warning, M5-T55 env-gated skip),
  `make qa-evidence` PASSED; after the review fixes (no runtime or harness change) `make qa-quality`
  PASSED (`qa-deploy`: 18 known violations, 22 root warnings), `make tooling-test` PASSED,
  `ruff check services scripts` clean. Not rerun: the full E2E suite after the review fixes, since
  they change only `qa-deploy`, the register and docs.

## 2026-10-29 Increment 1A: exact E2E outcomes, test-lint, mutation scoring

- Slice `agentic-delivery-process` 1A on branch `slice/agentic-delivery-process-1a`, from the plan
  merged as PR #4 (`f6a9524`).
- Probed the unchanged harness on a clean stack at `f6a9524` (all rows passed) and pinned the
  observed outcomes; the probe record is in the slice `test_plan.md`.
- Tightened 24 E2E outcome checks to exact statuses, reasons, exit codes and messages: the 15
  planned rows plus 9 that the new lint found (M2-T3, M2-T5, M2-T6, M2-T7, M5-T4, M5-T24, M5-T26,
  M5-T28, M5-T46). `assert_file_any` and the "no network error" greps are gone; the M3.S2-T3/T5
  warning alternates became "does not resolve" plus "pinned IP times out in the connect phase".
  The network isolation tests got in-test positive controls (the app answers 200 from inside its
  network). M1-T2/T3 read the server log from the attempt's start time.
- Found and corrected: M2-T3 never tested expiry (its certificate is from an untrusted CA, so Envoy
  answers `unknown ca`); renamed to what it tests, expiry stays with M2-T9. M5-T4, M5-T26 and M5-T28
  could pass on a missing or empty evidence file; each now checks a positive anchor first.
- New `scripts/test_lint.py` and `make test-lint` (in `qa-quality` and the CI docs-check job, which
  now fetches full history for the baseline test); tooling tests T-7, T-22, T-41 in `tests/tools/`.
- `scripts/mutation_gate.py` counts `no_tests` and `skipped` as not killed and fails an empty run.
  Score under the new rule: 85.58% (1240 of 1449; 0 untested, 0 skipped), unchanged, because
  `mutate_only_covered_lines = true` never creates mutants for uncovered lines.
- Independent review (Codex, three rounds, `review_1a.md`): B1–B6 fixed; B6 after the round limit,
  checked offline, not re-reviewed. Key question answered "no" in round 1.
- Validation: full E2E on a clean stack 120/120 (1 warning, the M5-T55 env-gated skip; the two
  M3.S2 warnings are gone), `make qa-evidence` PASSED, `make qa-quality` PASSED, `make tooling-test`
  PASSED, `make unit-mutation` PASSED, `ruff check services scripts` clean.

## 2026-10-29 Delivery-process plan reviewed, escalated and split into three slices

- Plan PR #4 review comments addressed (terms, D16 security coverage of grill-me, lane home, CI
  trust), then D17 (test adequacy, independent plan review before the user's review).
- Independent review by Codex CLI (`gpt-6.1-sol`; the configured `gpt-5.5` is refused for a ChatGPT
  login, and an expired login first failed every request with HTTP 401). Round 1: 20 findings, all
  resolved. Round 2: 9 partial and 13 new; the repeated findings triggered the D10 stop and an
  escalation.
- User decisions: D18 threat model (fallible agent, not an attacker of the CI infrastructure;
  residual accepted as OPL-009), D19 split into three slices, and an acceptance bar for reviews
  (only in-model blockers and majors in scope are fixed; at most three rounds).
- `plan.md` and `test_plan.md` now cover slice 1 only; slice 2 and 3 drafts and carried findings
  are in `later_slices.md`. Real errors fixed: M5-T21's expected outcome, the mutation-gate
  denominator, the Redis writer model and an unenforceable ACL rule, matrix detectors per asset
  class. New OPL-008 (`spire-token-init` mounts the SPIRE server data directory); OPL-007's fix
  option corrected.
- PoC rules added to `AGENTS.md` ("PoC scope and proportion"): honest-mistake threat model,
  accepted simplifications, ask before growing, few exceptions, which review findings block.
- D20 lean cut of slice 1 (user decision): kept exact outcomes, twins, `test-lint`, the holder list
  with `qa-deploy`, mutation scoring and the independent review. The runtime asset scan became a
  one-time baseline look plus a review question; the replay tool became a test review question;
  kinds, tiers, fault injection, provenance enforcement and the derivation checklist were deferred
  to `later_slices.md`; REQ-SEC-S1 moved to the pilot.
- Not run: documentation only; `make docs-check` and `make qa-trace` were run.

## 2026-10-28 CI mutation gate broken by pytest 9.2.0; pytest pinned

- PR #3 (`docs/consolidation`) failed `unit-trust / mutation-trust` with
  `AttributeError: 'Function' object has no attribute '_nodeid'` before any mutant ran.
- Cause: `requirements-dev.txt` left `pytest` unpinned. pytest 9.2.0 (published 2026-10-27 21:30 UTC,
  after `main`'s last green run at 20:09 UTC) removed the private `Node._nodeid`, which mutmut 3.5.0
  reads directly. `main` is affected the same way.
- Fix: `pytest==9.1.1`. Upgrading to mutmut 3.8.1 (2026-10-28, uses the public `item.nodeid`) is left
  for a separate dependency change.
- Validation in a fresh Python 3.11 virtualenv built from `requirements-dev.txt` (pytest 9.1.1, mutmut
  3.5.0): `qa-trace`, `docs-check`, `tooling-test`, `unit-guard-check`, `unit-trust` and
  `unit-mutation` (score 85.58%) all PASSED.

## 2026-10-28 OPL-005 verified by forgery; OPL-006, OPL-007 found; delivery-process slice planned

- OPL-005 re-checked on the running stack at the user's request. The private key was read (hashes
  only) in `capability-issuer`, `tool-b`, `jira-tool`, `jira-mcp-gateway` and a one-off `rogue`;
  all match. A token forged inside `tool-b` with that key passed tool-b's own `verify_biscuit` once a
  Redis budget existed for its root id. History traced to `07520d7` (2026-01-05) and the copied
  volume blocks.
- New: OPL-006 (SPIRE agent `data/keys.json` readable by every workload that mounts the agent
  directory; `M2-T7` checks a container without that mount) and OPL-007 (Redis without
  authentication, writable from every verifier network).
- Root-cause review of why six layers missed OPL-005, followed by a grill-me that produced the
  [agentic-delivery-process](../slices/agentic-delivery-process/plan.md) plan (D1–D15) and test plan.
  The plan includes an audit of about 20 loose E2E assertions.
- Not run: no code, harness or compose change was made, so no E2E or unit run was needed;
  `make docs-check` and `make qa-trace` were run on the documentation changes.

## 2026-10-27 Docs consolidation, Increments 2 and 3; harness PR merged

- `fix/m5-evidence-harness-hardening` merged to `main` as PR #2 (`fe86c35`). Full E2E on `main`, clean
  stack: 120/120, 3 warnings (M3.S2-T3, M3.S2-T5 accepted isolation; M5-T55 env-gated skip).
  `make qa-evidence` PASSED (validated 119, skipped 1).
- Increment 2: `docs/test_spec.md` now describes all 120 E2E tests. All 58 M5 tests were written by
  hand from the guard code; five entries note where a title claims more than the guards check. All
  headings use full harness IDs.
- Increment 3:
  - `scripts/check_docs.py` (`make docs-check`): spec covers every harness test and vice versa;
    links and anchors in live docs resolve; tracked images are referenced and `.puml` sources have
    their `.svg`; every slice bundle is indexed; `TEST_ONLY=` examples name real tests.
  - `make docs-check` is in `make qa-quality` and a new CI job, with `make tooling-test`
    (`tests/tools/`, 16 negative controls; `tests/shell/test_varambu_output.sh`, previously unwired).
  - `SECURITY_MODEL.md` folded into a "Security model summary" in `docs/architecture.md` and archived.
- Security finding while verifying the old security model: the capiss root signing key is readable as
  root inside `tool-b`, `jira-tool`, `jira-mcp-gateway`, and the `rogue` test container. Recorded as
  OPL-005 with evidence; not fixed (runtime change, needs its own slice).
- Validation: `make qa-quality` PASSED (qa-trace unchanged at requirements=159, architecture=33,
  design=131, tests=371; 348 unit tests; docs-check); `make tooling-test` PASSED; ruff clean;
  no new function above complexity 10.

## 2026-10-27 Docs consolidation, Increment 1

Slice bundle: `docs/slices/docs-consolidation/`.
- `AGENTS.md` rewritten as the single rulebook, checked against `Makefile` and CI; repo `CLAUDE.md` imports it.
- Status log tracked as this file (secret-scanned); new `docs/STATUS.md`.
- One hand-written E2E spec: `docs/test_spec.md` (was `test_spec_detailed.md`); guard listing and readable
  table archived. Phase 4 now requires updating it.
- Legacy slice bundles, `REDTEAM_M3.md`, and the unreferenced `container_architecture` diagram archived
  with `git mv`; slice index rebuilt.
- README corrected: invalid `TEST_ONLY` example, wrong `qa-quality`/unit target descriptions, stale
  Varambu "not implemented" note, doc map.
- Checks C1–C9 in the slice `test_plan.md`: all passed. No runtime, requirement, or test changes.

## 2026-10-27 Full-suite re-baseline and evidence-harness hardening

- First full E2E run since 2026-05-16 (clean stack): `119/120`, `M5-T49` FAIL, `make qa-evidence` FAILED.
  - `M5-T49`: intent assertion used `first(.[])`; the preceding `M5-T48` request landed in the same
    `since` second, so T49's session held a second chain. Product output was correct for T49's cid.
  - `M5-T43..T48`: never printed `EVIDENCE_DIR=`, so `qa-evidence` could not bind their PASS lines.
  - `M5-T55`: mock-mode skip left no premise/exercise/outcome evidence.
- Fix on branch `fix/m5-evidence-harness-hardening` (PR pending at time of writing; slice bundle `m5-full-chain-audit-trace/test_plan.md`, Increment 3, H1-H3):
  - chain-specific outcomes in `M5-T49/T50/T51/T54/T58` select by the test's own cid; human renders use `--cid`;
  - `M5-T43..T48` emit `EVIDENCE_DIR=`;
  - `M5-T55` records the gateway upstream mode as premise evidence and writes `skip_reason.txt`;
    `qa-evidence` accepts a skip only for a prefix declared in the suite's `env_gates` map, with gate
    premise evidence and no exercise/outcome artifacts; skipped prefixes are reported separately.
- Negative controls (scratch, not committed): 31/31 against the failing-run evidence plus mutations, and
  12/12 validator skip-rule cases including undeclared, other-prefix, malformed, wrong-gate, and silent skips.
- Validation after fix (clean stack):
  - full E2E: `120/120` passed, warnings `3` (`M3.S2-T3`, `M3.S2-T5` accepted isolation; `M5-T55` env-gated skip).
  - `make qa-evidence`: PASSED, `validated=119/120, skipped=1, warnings=3`.
  - `make qa-trace`: PASSED. `make qa-quality`: PASSED (`348` unit tests). `ruff` clean on the validator.
- Open: `M5-T55` still prints `PASS` in `test_report.log` when skipped (harness has no SKIP status);
  `validate_e2e_evidence.py:main` cyclomatic complexity 32 (pre-existing, unchanged).

## 2026-06-21 Increment 3: relay scrubbed upstream (Jira) error detail

Motivation: a failed upstream call showed only the bare HTTP status, and worse, Jira Cloud returns an
**ambiguous** status (e.g. an expired API token → **404**, because Jira returns 404 for unauthorized
resource access to avoid enumeration). So the status-only render said "project missing / verify it
exists" when the real cause was an expired credential — not actionable. Root limitation: the gateway
discarded the upstream response body, keeping only the status.

Re-entered the V-model (changes gateway behavior + the `jiramcp_gateway_decision` schema):
- **REQ-M5-FT7** extended: on upstream failure the gateway SHALL relay the upstream error as
  faithfully as possible (redacting only credential-bearing material, bounded), the trace SHALL
  surface it on the upstream leg and re-screen for secrets at read time, and the presentation SHALL
  NOT assert a single cause from an ambiguous status code (e.g. 404).
- **ARCH-033** updated (gateway `summarize_upstream_error` → `upstream_error_detail`; trace `Jira`
  row + read-time re-screen; ambiguous-status messaging).
- **DD-517** (`summarize_upstream_error`, gateway): extracts the message from common Jira shapes
  (`errorMessages`/`errors`/`message`/`error`/non-dict/fallback JSON), redacts `Basic `/`Bearer `
  credential blobs → `[redacted-credential]`, bounds to 512 B (limit exclusive, `…[truncated]`).
  Wired into both upstream-failure `_deny` sites via `_event_fields`/`_deny` new
  `upstream_error_detail` param. CC: all new gateway fns A/B (`_extract_upstream_message` refactored
  to B(9) via `_first_str_field`).
- Trace side (`scripts/varambu_audit.py`): `upstream_error_detail` added to `GATEWAY_FIELD_ORDER`
  (allowlisted + read-time scrubbed by the existing `Bearer `/`Basic `/`biscuit` screen),
  `derive_gateway_upstream` copies it onto the upstream leg, and `_detail_upstream` **passes the
  relayed Jira message through verbatim** as a single `Jira` row. Human-view only; `--json` keeps the
  raw field. Decision (2026-06-21, per operator): **dropped the constructed status interpretation** —
  no `_UPSTREAM_STATUS_HELP` table, no `Error`/`Action` rows. Rationale: relaying Jira's own words is
  simpler and avoids asserting a single cause from an ambiguous status code (Jira's message itself
  resolves e.g. a 404 that is really an expired/unauthorized credential). On a failure with no relayed
  detail the leg is just the `Call` row (status still shown in the row + STATUS column).
- Tests: gateway **UT-343** (shapes + Basic/Bearer redaction + BVA on the 512 B limit); trace
  **UT-344** (normalizer keeps the field, upstream leg renders `Jira`, a `Bearer `-bearing detail is
  dropped at read time); **UT-342** rewritten to pin the verbatim pass-through (Call→Jira only, no
  Error/Action; detail-less failure and success are Call-only). **346 unit tests pass**, guard
  offenders=0; radon all A/B; ruff clean; `make qa-trace` PASSED (design 131, DD-517).
- E2E: **M5-T59** fixture carries `upstream_error_detail`; outcome asserts the human view relays the
  Jira detail verbatim, that no constructed `Action` row is present, and that `--json` carries the
  field on the upstream leg. Full trace suite **M5-T49..T59 = 10/10 PASS**.
- Deployment note: the deterministic suite proves the relay via UT + the synthetic T59 fixture (mock
  mode never triggers a real upstream failure — NAS is denied at the gateway before upstream). The
  **live** gateway emission of `upstream_error_detail` runs only under `M5-T55` (real Jira, env-gated)
  and requires rebuilding the gateway image (`docker compose ... up --build jira-mcp-gateway`); the
  running stack still has the pre-change gateway until then.

## 2026-06-20 Increment 2: M5 trace display redesign (7-leg table)

Re-entered the V-model for a presentation + leg-model change (no enforcement/capiss/gateway/adapter
authorization change). Locked design after live testing.

Phase 1 — docs:
- `plan.md`/`test_plan.md` "Increment 2"; `REQ-M5-FT7` (upstream is a leg distinct from gateway
  enforcement), `REQ-M5-FT9` (single aligned detailed table; mint = same fields, not byte-identical;
  full untruncated identifiers); `ARCH-033` (7 legs, gateway/upstream derivation, renderer).

Phase 2/3 — code + tests (green):
- `scripts/varambu_audit.py`: `derive_gateway_upstream` (DD-924) splits one
  `jiramcp_gateway_decision` into a gateway-enforcement leg and an upstream-call leg
  (gateway ALLOW iff it reached the upstream call or recorded allow; a deny-with-upstream_called is an
  **upstream** failure, not a gateway denial); 7-leg `CHAIN_LEG_ORDER`
  (`…, gateway, upstream, adapter_decision`); a new aligned table `render_chain` (fixed
  `# · LEG · TIME · STATUS` spine + grouped detail, colour TTY-only, full ids wrap-not-truncate,
  local-zone times, `FROM CODEX`/`GATEWAY`/`UPSTREAM`/`RETURN TO CODEX` labels); `render_chain_json`
  with the upstream leg + per-leg advisory offset; `capiss_reason` added to the adapter allowlist.
- UTs: `tests/unit/test_varambu_trace.py` updated to the 7-leg contract; mint "byte-identical" UT →
  "fields present"; **exhaustive-condition + BVA UTs for `derive_gateway_upstream`** (UT-335..340);
  layout/label/full-id UTs. **342 unit tests pass**, guard offenders=0.
- Static gates: `radon` CC ≤ 10 (no grade C), `ruff` clean, `make qa-trace` PASSED (design 130).

Phase 4 — E2E:
- E2E updated to the 7-leg model (T49/T50/T55/T57/T58) + **new M5-T59** (the motivating case:
  gateway ALLOW + upstream 401 FAIL rendered as upstream failure, not gateway denial), mapped in
  `trace/tests.yaml` to REQ-M5-FT7.
- **M5-T56 and M5-T59 PASS** end-to-end through the real `varambu trace` CLI (synthetic fixtures, no
  mock/MCP network dependency) — these directly prove the redesign incl. the gateway/upstream split.
- **E2E now run green (2026-06-21).** With a healthy Docker network the full trace suite passes:
  `TEST_ONLY=M5-T49,M5-T50,M5-T51,M5-T52,M5-T53,M5-T54,M5-T56,M5-T57,M5-T58,M5-T59` → **10/10 PASS**
  (T55 live-Jira-gated, auto-skips in mock). Existing audit E2E `M5-T42..T48` re-run **7/7 PASS**
  (no regression). The prior WSL2 Docker multi-network attach flake did not recur.
- One harness fix surfaced on the first real run of `M5-T49`: its human-render outcome grepped the
  verbatim prompt as a single line, but the redesigned renderer **wraps** the intent detail cell
  (Increment 2 locked decision #5, wrap-not-truncate), so the prompt spans two lines. The exact
  verbatim intent is already proven byte-for-byte by the JSON outcome (`intent leg equals the
  verbatim prompt`); the human-render check now collapses whitespace (`tr '\n' ' ' | tr -s ' '`)
  before grepping, so it is wrap-robust. Implementation unchanged (renderer is correct by design).
- Re-run command (rebuild the rogue-tests image first; T55 is live-Jira-gated):
  `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M5-T49,M5-T50,M5-T51,M5-T52,M5-T53,M5-T54,M5-T56,M5-T57,M5-T58,M5-T59 rogue-tests`
- Mint-leg fidelity fix (REQ-M5-FT9 "same fields as `varambu audit`"): the trace MINT block was
  missing the subject identity (`varambu audit` shows it as `Subject:`, its first field). Added a
  leading `From  <subject_spiffe_id>` row to `_detail_mint` so the mint leg no longer reads as
  incomplete; subject was already carried in the normalized mint leg + `--json`, only the human view
  dropped it. UT-311 updated to assert the subject identity; CC/ruff/qa-trace green, E2E re-run green.
- Gateway-leg fidelity fix (render-what's-there): the gateway ALLOW leg printed a hardcoded literal
  `Checks  token · aud · act · project · budget ok` that asserted a per-check breakdown the
  `jiramcp_gateway_decision` event never contains (it only attests the aggregate `decision=allow,
  reason_code=ok`) and silently omitted `subject` (which the gateway does enforce). Replaced with
  event-grounded rows: `Verified aud … · act …`, `Project request <project_key> = token
  <token_project>` (the actual project check — `project_mismatch` is enforced at
  `services/jira-mcp-gateway/server.py` by comparing the token's resource project to the request),
  and `Budget remaining …`. New UT-341 pins the grounded render and forbids the old literal; the
  `_full_chain` gateway fixture now carries the real `aud/project_key/token_project/budget_remaining`.
  343 unit tests pass; CC/ruff/qa-trace green; E2E re-run green.
- Remaining-leg scrutiny (render-what's-attested audit of every leg): `intent` (verbatim
  agent-attested prompt), `action` (rollout `tool_name`/`arguments`), `adapter_request`
  (`tool_name → res`, both in the adapter event), `upstream` (`upstream_operation`/`upstream_status`
  from the gateway event; `gateway-attested` label is accurate, run-mode is CLI context by REQ-M5-FT7
  design), and `adapter_decision` (`ok`/`reason`/`capiss_reason`/`key`, all conditional on the
  adapter event) were each verified to derive only from their source event — no further manufactured
  literals beyond the mint/gateway ones already fixed.
- Label change (demo clarity): leg 3 `adapter_request` display label reverted `FROM CODEX` → `ADAPTER`
  (JSON leg/event_type keys unchanged — still `adapter_request`, schema stable). `RETURN TO CODEX`
  (leg 7) kept. Updated `LEG_LABELS`, UT-312 assertion + docstring, the M5-T49 E2E grep (now matches
  the `N  ADAPTER ` leg row, not the lowercase spiffe-id substring), `ARCH-033`/architecture.md, and
  the slice plan/test_plan label references. `_full_chain` gateway fixture and `mod_request` adapter
  fixture were made realistic (carry `aud/project_key/token_project/budget_remaining` and `act/res/
  project_key`) so UTs render the same fields the live events carry. 343 UTs + 10/10 trace E2E green.
- Upstream-failure actionability: a failed `upstream` leg now self-explains. `_detail_upstream` adds
  an `Error  HTTP <status> <meaning>` row and an `Action  <remediation>` row, derived from the
  gateway-attested `upstream_status` via `_upstream_status_help` (401 → credential invalid/expired →
  refresh the Jira auth token; 403 → permission; 404 → missing project/issue; 409 → conflict;
  429 → rate limited; 5xx → Jira server error → retry; generic 4xx/unknown fallbacks). The status is
  attested; the meaning/action are standard-HTTP advisory help (same role as `_humanize_reason`),
  human-view only — `--json` keeps the raw `upstream_status`. Successful (2xx) legs stay the single
  `Call` row. New UT-342 (401/5xx/unmapped/2xx) + an M5-T59 outcome asserting the human view explains
  the 401 and names the credential-refresh action. 344 UTs + 10/10 trace E2E green; CC/ruff/qa-trace
  green. Limitation: the gateway's `call_upstream` discards the upstream response body (returns only
  the HTTP status), so Jira's own error text is not available to surface — capturing a bounded,
  scrubbed upstream error body at the gateway would be a separate gateway-schema slice (REQ/ARCH/DD
  + secret hygiene), out of scope for this renderer-only change.

## 2026-06-19 Slice: M5 Full-Chain Audit Trace (`varambu trace`)

Slice bundle: `docs/slices/m5-full-chain-audit-trace/` (plan.md + test_plan.md, grill-me approved).
Authoritative docs already authored before this work: `REQ-M5-FT1..FT9`, `ARCH-033`, `ARCH-032`
state extension.

Phase 2 — tests-first (complete, green):
- New `tests/unit/test_varambu_trace.py`: 77 UTs (`UT-248..UT-324`) covering DD-910..917, DD-922,
  DD-923. Rigor: exhaustive 2^4 condition coverage for `find_intent_triple` (DD-913, UT-265..280),
  BVA (B-1/B/B+1, limits exclusive) for `scrub_and_bound_triple` (DD-914, UT-286..294), exhaustive
  missing-leg/anchor/ordering for `assemble_chains` (DD-915).
- `tests/unit/jiramcp/test_adapter.py`: 5 new UTs (`UT-325..329`) for the adapter independent voice
  (DD-919): request-before-mint / decision-after-gateway ordering, crash visibility, path wiring,
  secret discipline, correlation stamping.
- `tests/unit/test_varambu_audit.py`: `UT-330` for the gateway-source tailer branch (DD-903).
- Failing baseline recorded: before implementation, 77 trace UTs + 5 adapter UTs failed (no impl);
  the 8 prior adapter UTs passed.

Phase 3 — implementation (complete for the unit-testable + deterministic surface):
- `scripts/varambu_audit.py`: `normalize_gateway_event` (DD-910), `normalize_adapter_event`
  (DD-911), `extract_correlation_id` (DD-912), `find_intent_triple` (DD-913),
  `scrub_and_bound_triple` (DD-914), `write_trace_file` (DD-923), `assemble_chains` (DD-915),
  `render_chain` (DD-916), `render_chain_json` (DD-922), `trace` CLI (DD-917); plus a `--source`
  option on `tail` so the same tailer serves the gateway leg with no capiss-path regression.
- `services/codex-jira-mcp-adapter/server.py`: `emit_adapter_event` (DD-919) wired into
  `invoke_tool` — `adapter_request` before mint, `adapter_decision` at each terminal; existing
  stderr line retained; no-op when `VARAMBU_SESSION_REL` is unset (keeps MCP stdout clean).
- `varambu` launcher: `start_gateway_tailer` (DD-918), `provision_codex_home` (DD-920) +
  `CODEX_HOME=` launch line, `run_trace` dispatch (DD-921), per-session `mode` file; exports
  `VARAMBU_SESSION_REL` for the adapter container.
- `compose/spiffe.compose.yml`: adapter `../artifacts/varambu-demo:/var/audit` bind mount +
  `VARAMBU_AUDIT_ROOT` / `VARAMBU_SESSION_REL` env.

Phase 4 — verification completed in this environment:
- `python3 -m pytest -q tests/unit`: **332 passed**, unit guard `offenders=0`.
- `radon cc scripts/varambu_audit.py services/codex-jira-mcp-adapter/server.py -n C`: empty
  (all functions CC ≤ 10; the at-limit normalizer was refactored down to CC 7).
- `make qa-trace`: PASSED. `make unit-guard-check`: PASSED (332). `ruff`: clean on touched files.
  `bandit`: High=0 (the Low/Medium findings are pre-existing in untouched subprocess/urlopen code).
- Functional end-to-end of the read path on a synthetic session (no Docker): `varambu_audit.py
  trace` rendered the full six-leg chain in canonical order, reused the capiss `render_record`
  verbatim for the mint leg, showed local time + advisory deltas, and persisted a minimal scrubbed
  `trace.jsonl`.

E2E layer — authored, mapped, and run green against the live stack (2026-06-20):
- `scripts/rogue_node_tests.sh`: added `M5-T49..T58` (full chain, denied-mint partial, intent
  pending→converge, multi-tool attribution, secret hygiene+bounds, agent-tamper detection, honest
  live upstream, CLI surface + audit non-regression, canonical ordering + join integrity, anchor
  rule + mint reuse + timezone) plus helpers (`mcp_tool_call_traced` injecting
  `VARAMBU_SESSION_REL` per exec, capiss/gateway tailer starters, synthetic codex-rollout builders,
  `write_synth_trace_session`).
- `trace/tests.yaml`: added `E2E-M5-FT-TRACE-SUITE` + `E2E-M5-T49..T58` mapping to `REQ-M5-FT*`
  (all nine FT requirements now have E2E coverage; coverage_gaps 131→122).
- Run result (mock mode, real SPIRE/Envoy/capiss/gateway/adapter stack):
  `TEST_ONLY=M5-T49..T58` → **10/10 PASS** (T55 is live-gated and auto-skips in mock with a
  recorded `warning_reason`). Existing `M5-T42..T48` audit E2E re-run **7/7 PASS** (no regression
  from the `tail --source`/helper changes).
- One code fix surfaced by the E2E: the adapter mint-deny path emits a legitimate `capiss_reason`
  field; added it to `ADAPTER_FIELD_ORDER` so the trace normalizer keeps it instead of warning.
  Regression-covered by new UT-332.
- Stack lifecycle note: a stale prior-run SPIRE CA had expired (issued 2026-06-18, expired
  2026-06-19); `scripts/clean_stack.sh` wiped `/run/spire/server/data` and a fresh
  `up --build` issued SVIDs in ~5s. The `rogue-tests` image bakes the harness script, so it must be
  rebuilt (`docker compose --profile tests build rogue-tests`) after harness edits;
  `scripts/varambu_audit.py` is read live from the `/repo` mount.

Operator ergonomics (added 2026-06-20 after live Codex testing):
- `varambu codex [args...]` subcommand: launches Codex against the **current** session's
  `codex-home` (resolved via the `current` symlink), seeding the env so the operator no longer sets
  `CODEX_HOME` by hand. Flow is now `varambu start` → `varambu codex`.
- Credential seeding: `provision_codex_home` and `varambu codex` **symlink** `~/.codex/auth.json`
  into the per-session home so a freshly provisioned home does not force a Codex re-login. A symlink
  (not a copy) keeps the credential in `~/.codex` — it never enters the `artifacts/` session bundle,
  and `varambu trace` reads only `rollout-*.jsonl`, never `auth.json`. `artifacts/varambu-demo` is
  gitignored (verified). Authored in REQ-M5-FT5 + ARCH-033.
- Extractor hardening (from the same live test): `extract_correlation_id` now recovers the id from
  escaped JSON-in-JSON and structured-object tool results (real Codex MCP result shapes), not just
  the flat string my synthetic fixture used; `adapter_audit` `capiss_reason` added to the allowlist.
  Covered by UT-332/333/334. Root cause of the operator's "intent not yet available" was launching a
  plain `codex` (rollout landed in `~/.codex`, not the session tree) — addressed by `varambu codex`.

Remaining / deferred:
- `M5-T55` (live upstream) only exercises its assertions with real Jira env
  (`JIRA_MCP_UPSTREAM_MODE=live` + `.env`); in mock it auto-skips with a warning. Run with
  `make jira-live-smoke`-style live env when available.
- The launcher (`varambu start`) gateway-tailer / CODEX_HOME provisioning is `bash -n` verified and
  its building blocks (gateway `tail --source gateway`, per-session adapter audit, `trace` dispatch)
  are all exercised by the E2E, but a full interactive `varambu start` + real `codex` agent run was
  not performed here.
- `DD-918/920/921` remain reported `dd_without_ut` gaps (shell-level launcher wiring; proven via
  E2E rather than unit tests, per the black-box model in AGENTS.md).

Decisions / deviations (reviewed 2026-06-20 — resolved):
- **Anchor rule vs REQ-M5-FT8 wording — RESOLVED (REQ tightened).** REQ-M5-FT8 and ARCH-033
  Interactions and the plan.md anchor rule were edited to drop "or an M5 model tool call" as an
  anchor: only the adapter/gateway in-boundary evidence anchors a chain; the untrusted rollout
  intent is *attached* to an already-anchored chain, never used to surface one. Implementation
  already matched this (`_anchor_cids`); the docs now agree.
- **Multiple correlation-ids in one rollout output — RESOLVED (now noticeable).** Confirmed no valid
  flow produces two distinct ids in one output (the adapter/gateway result carries exactly one; user
  content is not echoed). The only causes are a future schema change or a forged/tampered rollout.
  `extract_correlation_id` keeps the deterministic first-match contract (never raises, never blocks)
  but now emits a `warn(...)` when it sees 2+ *distinct* ids, pointing at a possible forged rollout,
  so an auditor can dive to root cause. Identical repeats stay silent. New/updated UT-263, UT-331.
- **Dual Codex MCP registration — RESOLVED (global removed).** The global `configure_codex_mcp`
  function and its "Configure Codex" phase were deleted. Registration is now per-session only
  (`provision_codex_home` into the session `CODEX_HOME`), so intent capture is confined to the
  deterministic session tree (REQ-M5-FT5). `--no-codex-config` and codex-CLI-absent still degrade
  gracefully with the launcher-script pointer. Behavior change: a bare `codex` (without the printed
  `CODEX_HOME=…` launch line) no longer has the MCP registered.
- **Pinned Phase-2 contracts** (in `test_plan.md` "Pinned decisions"), unchanged: duplicate-leg =
  first-wins by sequence; multiple correlation-ids = first match (now + warning); `--strict` for
  trace = deferred; gateway already carries `act`/`res` (no gateway change).
- **Unique-DD-id rule** forced splitting two plan items into their own ids: `write_trace_file` =
  DD-923 (under DD-914's intent), `render_chain_json` = DD-922 (under DD-916's intent). Accepted.

## 2026-05-16 Slice Implemented: M5 Codex Jira MCP Slice 1

- Added a local Codex-to-container MCP launcher path with `scripts/codex_jira_mcp.sh` and `codex-jira-mcp-adapter`.
- The adapter exposes exactly `read_project_summary` and `create_story`, mints fresh `aud=jira-mcp-gateway` capiss tokens, and calls the protected gateway through `jira-mcp-envoy`.
- Added the distinct M5 authority family: `aud=jira-mcp-gateway`, `act=read_project_summary|create_story`, and `res=jira-mcp:/project:IAM`.
- Added `jira-mcp-gateway` as the request-time PEP for token, Envoy identity, action, resource, project, payload, optional epic, budget/rate, upstream, and audit enforcement.
- Added `jira-mcp-mock` as the deterministic upstream Jira Cloud substitute with broad IAM and NAS fixture data. Protected MCP behavior narrows access to IAM.
- Updated requirements, architecture, architecture diagram source, trace mappings, README, slice docs, unit tests, E2E harness, and evidence validation.
- Validation completed:
  - `make unit-guard-check`: 224 passed
  - `make unit-trust`: passed, coverage gate 85.06%
  - `make qa-trace`: passed
  - `make qa-quality`: passed
  - `TEST_MILESTONES=m5`: 40 passed, 0 failed
  - full rogue-tests suite: 102 passed, 0 failed, 2 accepted alternate isolation warnings
  - `make qa-evidence`: passed, validated 102/102 with the same two accepted warnings
- Note: `docs/architecture_diagram.puml` is the updated diagram source. No local PlantUML renderer is installed in this environment, so generated SVG/PNG regeneration was not performed in this turn.

## 2026-05-15 Slice Implemented: M4b Jira Description Write

- Added M4b as a project-scoped Jira description write slice.
- `act=write` for `jira-tool:/project:IAM` now means read plus description replacement only.
- `act=read` remains read-only.
- `jira-tool` rejects NAS writes before upstream use, rejects malformed or overbroad write bodies before upstream use, converts accepted plain text to Jira ADF, and returns `204` on successful update.
- M4b E2E evidence is authored as `M4b-T1` through `M4b-T6`.
- Optional live smoke intentionally leaves the allowed Jira issue description changed and checks demo output for credential-like material.

## 2026-04-12 Black-Box Trust Model

- Primary confidence goal:
  - a reviewer should be able to understand security-relevant behavior from authored docs and runtime evidence without discovering it accidentally from code
- Repo policy going forward:
  - requirements describe what must hold
  - architecture describes component responsibility and authoritative state
  - each slice starts with `grill-me`, then records the agreed design choices, requirements, hidden-state decisions, scope, and retirement expectations in `plan.md`
  - each slice then records the approved UT and E2E strategy in `test_plan.md`
- Internal design and unit artifacts remain useful, but they are not sufficient by themselves to explain hidden governance behavior.
- This process change is intended to prevent future surprises such as undocumented Redis-backed governance or provenance rules surfacing first from implementation details.

## 2026-03-03

### Implemented M4 Vertical Slice

- Tool-b focused vertical slice for checkpointed delegation and governance truth.
- Root and delegated token chain metadata implemented: `root_token_id`, `token_id`, `parent_token_id`, `delegator_spiffe_id`, `subject_spiffe_id`, `delegation_depth`.
- Chain integrity verification and derived depth enforcement implemented with `effective_depth = chain_length - 1` and max depth `N=3`.
- Discovery flow implemented at `tool-b:/search`, writing canonical discovered resources to Redis registry keyed by `root_token_id`.
- Registry-gated resource minting implemented at `capiss` via `POST /capabilities/resource-mint` for new resources (for example `tool-b:/read-file:fileA`).
- Per-request budget and request-rate enforcement implemented in tool-b using Redis, keyed by `root_token_id`.
- Fail-closed behavior implemented on trusted-store/policy errors in enforcement and minting paths.
- Test harness coverage implemented for this slice as M4 T1-T5 in `scripts/rogue_node_tests.sh`, with corresponding test spec entries in docs.

### M4 Review Findings (Requirements Coverage)

1. Missing "new resource mint rate" enforcement at `capiss` (High)
- Requirement explicitly calls for this: `docs/requirements.md:10`.
- `resource_mint` does registry check + policy + mint, but no mint-rate limiter/counter path exists: `services/capability-issuer/app.py:578`, `services/capability-issuer/app.py:621`, `services/capability-issuer/app.py:665`.
- No corresponding config/env in compose for capiss mint-rate control: `compose/spiffe.compose.yml:127`.

2. `capiss` does not log every mint decision path (High)
- Requirement says every mint request should be logged with provenance: `docs/requirements.md:172`.
- Several deny/error exits return without `capiss_mint_decision` logging, e.g. payload/canonical validation and early auth/chain checks:
  - `services/capability-issuer/app.py:472`
  - `services/capability-issuer/app.py:478`
  - `services/capability-issuer/app.py:588`
  - `services/capability-issuer/app.py:596`
  - `services/capability-issuer/app.py:599`
  - `services/capability-issuer/app.py:602`
  - `services/capability-issuer/app.py:616`
  - `services/capability-issuer/app.py:623`

3. Canonical resource contract is inconsistent for `/secret` (Medium)
- Requirements define canonical `res` as `tool-b:/...`: `docs/requirements.md:215`.
- Implementation keeps backward compatibility with raw `/secret`: `services/capability-issuer/app.py:182`.
- OPA root-mint policy allows `/secret` (non-canonical) but not `tool-b:/secret`: `services/opa/policy.rego:5`.
- This deviates from strict "canonical only" requirement intent (`docs/requirements.md:48`).

4. "Single enforcement contract" is not implemented as shared component (Medium)
- Requirement: shared enforcement contract/library/service across PEPs/tools: `docs/requirements.md:139`.
- Chain/depth enforcement logic is duplicated in two different services:
  - `services/capability-issuer/app.py:251`
  - `services/tool-b/server.py:197`
- Functionally similar, but not a single shared contract artifact.

5. M4 test coverage misses multiple requirement areas (Medium)
- Current M4 suite has only T1-T5: `scripts/rogue_node_tests.sh:2593`.
- Missing explicit tests for:
  - chain tamper/integrity denial (`M4-CH1`, `docs/requirements.md:68`)
  - depth limit > N denial (`M4-DL2`, `docs/requirements.md:82`)
  - fail-closed on store errors in M4 paths (`docs/requirements.md:12`)
  - audit/observability requirements (`M4-O1..O4`, `docs/requirements.md:161`)
  - capiss new-resource mint-rate requirement (`docs/requirements.md:10`)

### Areas That Look Covered

- Registry-gated resource minting and budget/rate enforcement per `root_token_id` are implemented and tested (M4 T2-T5).

## 2026-04-03

### Slice Started: Shared Enforcement Contract

- Goal: remove semantic drift between mint-time and request-time M4 chain validation by introducing one shared in-process enforcement contract.
- Scope of this slice:
  - shared chain integrity, derived depth, and attenuation semantics
  - thin caller adapters in `capiss` and `tool-b`
  - traceability updates for requirements, architecture, DD, UT, and E2E
- Explicitly out of scope for this slice:
  - mint-rate enforcement
  - full mint-decision logging closure
  - canonical resource contract cleanup
  - broader observability closure beyond this slice's new tests and trace

### Slice Implemented: Shared Enforcement Contract

- Added a shared in-process Python module for M4 chain validation semantics under `services/shared/enforcement_contract.py`.
- `capiss` and `tool-b` now call the same shared contract for:
  - required chain metadata checks
  - parent-link continuity
  - effective depth derivation
  - depth limit enforcement
  - common attenuation rules for `aud`, `act`, and `exp`
- `tool-b` keeps the resource-transition marker/store decision as a thin local hook layered on top of the shared contract.
- Added a dedicated architecture component for the shared contract in `docs/architecture.md`.
- Tightened `REQ-M4-E2` to make the shared implementation expectation explicit in `docs/requirements.md`.

### Slice Traceability Updates

- Added new source-owned DD for the shared contract:
  - `DD-220`
- Added source-owned UT coverage for the shared contract and thin adapters:
  - `UT-118` to `UT-127`
- Added new M4 E2E coverage and trace updates for:
  - tampered token denial
  - depth-limit denial on repeated delegation chain extension

### Slice Validation Notes

- Initial runtime validation exposed one issuer-side integration bug:
  - `capiss` accepted the shared contract, but its adapter did not allow previously `capiss`-minted resource transitions during later delegated mint hops.
  - Symptom: repeated delegation failed as `invalid_token` before reaching `depth_exceeded`.
- Fixed by adding the same capiss-minted marker check to the `capiss` adapter hook that `tool-b` already used for allowed resource transitions.
- Added `UT-127` to pin this behavior at the adapter level.
- Final validation after the fix:
  - `pytest tests/unit/shared/test_enforcement_contract.py tests/unit/capiss/test_chain_and_policy.py tests/unit/toolb/test_canonical_and_chain.py`
  - `make qa-trace`
  - `make qa-quality`
  - full E2E suite: `39/39` passed
  - `make qa-evidence`: passed with the expected two accepted-warning cases only

### Authoritative State Inventory Notes

- The Redis-backed `m4:capiss_minted:<token_id>` marker was not introduced by this slice. It already existed in the original M4 delegation implementation from commit `4b808cb`.
- What this slice exposed is that the rule was previously implicit and asymmetric:
  - capability-issuer wrote the marker
  - tool-b enforced it for resource-changing delegated tokens
  - the docs did not explicitly describe this as an authoritative state dependency
- The current M4 Redis-backed authoritative state now needs to be read as:
  - `m4:registry:<root_token_id>`:
    - writer: tool-b
    - reader: capability-issuer
    - purpose: discovery-backed permission to mint a new resource-scoped token
  - `m4:budget:<root_token_id>` and related request-rate keys:
    - writer/reader: tool-b, with root-budget initialization from capability-issuer
    - purpose: request-time governance truth
  - `m4:capiss_minted:<token_id>`:
    - writer: capability-issuer
    - readers: capability-issuer, tool-b
    - purpose: issuer-provenance marker for the current M4 resource-transition delegation rule

### 2026-04-03 Follow-up: Registry Seeding Cleanup

- Removed the old capability-issuer behavior that seeded `m4:registry:<root_token_id>` during root mint.
- `ensure_root_budget(...)` now initializes only `m4:budget:<root_token_id>`.
- Resulting state model is cleaner:
  - discovery registry entries come only from tool-b discovery
  - root-token starting authority remains in the token itself
  - capability-issuer still reads the registry only when a delegated mint asks for a different resource than the parent token

### 2026-04-04 Known Shortcuts and Overloads Still Present

1. Canonical resource compatibility remains inconsistent
- `capiss` still preserves raw `/secret` as a compatibility case rather than forcing canonical `tool-b:/...` resources.
- `tool-b` still accepts either raw `/secret` or canonical `tool-b:/secret` for the same protected request.
- OPA policy still reasons over the raw `/secret` form.
- This is the clearest remaining compatibility shortcut and should be removed in the canonical-resource cleanup slice.

2. Redis-backed mint provenance remains part of the M4 security model
- `m4:capiss_minted:<token_id>` is still required to prove that a resource-changing child token came from the trusted issuer path.
- This behavior is now documented, but it is still an implementation-specific governance shortcut rather than a purely token-self-contained proof model.

3. Shared enforcement still depends on service-local hooks
- The shared enforcement contract now owns the common chain/depth semantics, but legal resource transitions are still decided via service-local callbacks in `capiss` and `tool-b`.
- This is acceptable for the reduced M4 slice, but it means the shared contract is not fully self-sufficient.

4. `registry_hit` is still slightly overloaded in mint policy/logging
- When a delegated mint keeps the same resource as the parent token, `capiss` sets `registry_hit=True` without performing a registry lookup.
- Operationally this means “registry proof not needed” rather than “registry checked and hit”.
- The field name should be clarified or split later to avoid misleading logs and policy input semantics.

5. Old chain-parsing helpers remain duplicated in service files
- The active enforcement path now lives in `services/shared/enforcement_contract.py`.
- Older copies of chain/fact parsing helpers still remain in `capiss` and `tool-b`.
- They are now drift risk unless explicitly retired or justified.

6. Provenance check path still mutates TTL on read
- `tool-b` shortens the TTL of `m4:capiss_minted:<token_id>` when the stored TTL exceeds the token TTL.
- That means what looks like a read/check helper still has a state-mutating side effect.
- This should remain visible as an intentional behavior rather than hidden helper logic.

7. Governance ownership is still split across services
- `capiss` initializes root budget context.
- `tool-b` consumes and enforces the request-time spend/rate limits.
- This is workable, but it is a cross-service governance design that must stay explicit in docs and tests.

### 2026-04-04 Slice Started: Canonical Resource Cleanup

- Goal: remove the remaining raw `/secret` compatibility shortcuts and make M4 mint-time and request-time behavior use canonical `tool-b:/...` resource strings only.
- Scope of this slice:
  - capability-issuer canonicalization
  - OPA root-mint policy input alignment
  - tool-b request-path to canonical-resource mapping
  - unit and E2E updates for canonical `tool-b:/secret`
- Explicitly out of scope for this slice:
  - changing the external HTTP path `/secret`
  - redesigning the Redis-backed provenance rule
  - mint-rate enforcement
  - broader observability closure

### Remaining M4 Work After This Slice

- new-resource mint-rate enforcement at `capiss`
- full mint-decision provenance logging on every `capiss` exit path
- strict canonical-resource contract cleanup
- broader M4 observability/reconstruction closure

## 2026-04-08 Slice Started: capiss New-Resource Mint-Rate Enforcement

- Goal: add the missing M4 governance control that bounds how many new canonical resources can be minted under one `root_token_id`.
- Scope of this slice:
  - refine the requirement into a formula-based mint-rate rule
  - add Redis-backed authoritative state for mint-rate consumption
  - enforce the rule only on `resource_mint` when `canonical_res != parent_res`
  - add unit and E2E proof for allow, deny, and fail-closed behavior
- Locked contract for this slice:
  - keying: `root_token_id`
  - rule: `max(1, floor(root_token_lifetime_seconds / 20))`
  - current default: `60s` root lifetime -> `3` allowed new-resource mints
  - same-resource remints do not consume allowance
  - store errors fail closed
- Explicitly out of scope for this slice:
  - redesigning request-time budget/rate enforcement
  - redesigning Redis-backed mint provenance
  - broader mint-decision logging closure outside the new mint-rate path

## 2026-04-08 Slice Implemented: capiss New-Resource Mint-Rate Enforcement

- Requirements and architecture were refined first:
  - added `REQ-M4-B7` as an explicit requirement for formula-based new-resource mint-rate enforcement at `capiss`
  - documented the new Redis key family `m4:mint_rate:<root_token_id>` in architecture as authoritative state written and read only by `capability-issuer`
- Implementation updates applied:
  - added `consume_mint_rate(...)` in `services/capability-issuer/app.py`
  - rule implemented as `max(1, floor(root_token_lifetime_seconds / 20))`
  - current default remains `M4_ROOT_TTL_SECONDS=60`, so the effective allowance is `3`
  - enforcement runs only on `resource_mint` when `canonical_res != parent_res`
  - same-resource remints do not consume mint-rate allowance
  - store failures fail closed as `store_unavailable`
  - over-limit mints deny as `mint_rate_exceeded`
- Redis state introduced by this slice:
  - `m4:mint_rate:<root_token_id>`
    - writer/reader: `capability-issuer`
    - value: consumed new-resource mint count
    - TTL: bounded to the remaining root-token lifetime
- Trace/test updates applied:
  - added `DD-221` for the mint-rate helper
  - added `UT-129` through `UT-137`
  - added `M4-T8` for the fourth new-resource mint denial case
  - updated `trace/tests.yaml` and unit/E2E spec docs
  - updated `docs/unit_test_spec.md` so `M4-B7` is explicitly mapped to unit coverage
- Validation completed and passing:
  - focused capiss mint-rate unit slice: `9 passed`
  - capiss unit files touched by the slice: `42 passed`
  - `make qa-trace`: passed (`requirements=118`, `architecture=20`, `design=46`, `tests=144`)
  - `make qa-quality`: passed (`157 passed`)
  - targeted `M4-T8` run: passed
  - full E2E suite: `40 passed`, `0 failed`
  - `make qa-evidence`: passed (`validated=40/40`, expected 2 warnings only)

### Remaining M4 Work After This Slice

- full mint-decision provenance logging on every `capiss` exit path
- broader M4 observability/reconstruction closure

## 2026-04-09 Slice Started: capiss Mint-Decision Logging Closure

- Goal: close `REQ-M4-O2` by making every `capiss` mint request exit emit one final `capiss_mint_decision` event with stable provenance fields.
- Scope of this slice:
  - tighten the final mint-decision event contract in requirements and architecture
  - add one shared mint-decision logging helper in `capability-issuer`
  - close remaining unlogged `root_mint` and `resource_mint` branches
  - add unit coverage for exact final-event payloads on representative allow, deny, and fail-closed exits
- Locked behavior for this slice:
  - logging remains append-only JSON on stdout
  - container logs remain the immediate runtime sink
  - `subject_spiffe_id` is the only identity field in final mint logs for the current offline-delegation model
  - no new storage or visualization subsystem is introduced here
- Follow-up note:
  - observability presentation/visualization should be revisited in a later slice without changing the current enforcement or logging path

## 2026-04-12 Slice Started: Reduced-Scope M4 Observability and Reconstruction Closure

- Goal: close the remaining reduced-scope M4 observability work (`REQ-M4-O1`, `REQ-M4-O3`, `REQ-M4-O4`) without adding a new storage subsystem.
- Review bundle created under:
  - `docs/slices/m4-observability-closure/`
- Locked direction for this slice:
  - keep stdout JSON as the runtime audit stream
  - capture observability proof through harness-collected container logs and evidence artifacts
  - align final `tool-b` enforcement events to the authored requirement schema
  - add the missing reconstruction fields needed for current reduced-scope offline delegation
  - retire obsolete audit-field names and duplicated inline payload assembly
- No tests or implementation started yet for this slice because the new process requires Phase 1 review first.

## 2026-04-09 Slice Implemented: capiss Mint-Decision Logging Closure

- Requirements and architecture were refined first:
  - `REQ-M4-O2` now explicitly requires one final mint-decision event per mint request outcome
  - `ARCH-012` now states that `capability-issuer` owns complete mint-decision logging for every mint exit and that current storage is structured JSON on stdout captured by container logs
- Implementation updates applied:
  - added `log_mint_decision(...)` in `services/capability-issuer/app.py`
  - added `DD-222` for the final mint-decision logging seam
  - refactored `root_mint(...)` and `resource_mint(...)` so all current exits emit exactly one final `capiss_mint_decision`
  - helper policy events (`capiss_policy_error`, `capiss_policy_decision`) remain secondary events, but `REQ-M4-O2` proof now comes from the final mint-decision event
- Unit/trace updates applied:
  - added `UT-138` through `UT-141`
  - extended existing endpoint tests to assert exact final mint-decision payloads on:
    - early auth/identity failures
    - payload and canonical-resource rejects
    - policy deny
    - registry/store/mint-rate fail-closed paths
    - success paths
  - updated `docs/unit_test_spec.md` so `M4-O2` is now marked covered
- Validation completed and passing:
  - `pytest tests/unit/capiss/test_endpoints.py -q`: `23 passed`
  - `pytest tests/unit/capiss/test_chain_and_policy.py -q`: `19 passed`
  - `make qa-trace`: passed (`requirements=118`, `architecture=20`, `design=47`, `tests=148`)
  - `make qa-quality`: passed (`161 passed`)
- Storage model remains unchanged:
  - append-only structured JSON on stdout
  - container logs remain the immediate runtime sink
  - better observability presentation/visualization remains deferred to a later slice

### Remaining M4 Work After This Slice

- broader M4 observability/reconstruction closure (`REQ-M4-O1`, `REQ-M4-O3`, `REQ-M4-O4`)

### 2026-04-04 Slice Progress: Canonical Resource Cleanup

- Requirements and architecture were aligned first for canonical `tool-b:/...` resource strings.
- Implementation updates applied:
  - `capability-issuer` now canonicalizes `/secret` to `tool-b:/secret` and returns canonical `res` values from mint endpoints.
  - `tool-b` now maps request path `/secret` to canonical required resource `tool-b:/secret` and removed the raw `/secret` token-acceptance compatibility branch.
  - OPA mint policy now reasons over canonical `tool-b:/secret` instead of raw `/secret`.
- Trace/test updates applied:
  - unit tests were updated to use canonical resource values while keeping the external HTTP path `/secret` unchanged.
  - E2E harness request bodies and spec docs were updated so mint requests use canonical `tool-b:/secret`.
  - detailed/readable spec text now distinguishes token resource `tool-b:/secret` from HTTP path `/secret`.
- Validation completed and passing:
  - focused canonical-resource unit tests: `52 passed`
  - `make qa-trace`: passed
  - `make qa-quality`: passed (`148 passed`)
- Runtime validation status:
  - targeted `docker compose run` M3/M4 checks were inconclusive because the run path showed a separate harness/material issue (`curl --key` blank argument).
  - clean full-suite validation is currently blocked by a broader stack startup regression affecting M1/M2 before canonical-slice checks become trustworthy.
  - observed unrelated failures include missing legit SPIRE attestation readiness and unexpected TLS/entry-list outcomes in M1/M2 after clean startup.
- Slice status:
  - implementation and local/unit traceability are complete
  - full E2E validation is blocked by unrelated stack/harness startup issues and is not yet a trustworthy acceptance signal for this slice
- Next action requires explicit direction:
  - either debug the broader stack startup regression first
  - or accept the canonical slice as code-complete pending later E2E revalidation

### 2026-04-12 Slice Progress: Reduced-Scope M4 Observability and Reconstruction Closure

- Phase 1 bundle was created under `docs/slices/m4-observability-closure/`.
- Phase 2 test authoring is now in progress:
  - unit tests were added to pin the target final-event schema for `tool-b` allow/deny audit events and delegated `capiss_mint_decision` provenance.
  - new M4 E2E cases `M4-T9` and `M4-T10` were authored to capture container logs into evidence and assert correlated audit events for one allow flow and one deny flow.
  - trace/spec artifacts were updated so the observability slice is represented at the black-box proof layer before implementation begins.
- Intended failing baseline for Phase 2:
  - `tool-b` still emits `caller_subject_spiffe_id` instead of the requirement-aligned `subject_spiffe_id`.
  - `tool-b` final enforcement events do not yet carry `delegator_spiffe_id`.
  - `capiss_mint_decision` does not yet carry `delegator_spiffe_id` on delegated/resource-mint paths.
- No service implementation changes were made as part of Phase 2.

### 2026-04-12 Slice Progress Update: Reduced-Scope M4 Observability and Reconstruction Closure

- Phase 3 implementation is now applied:
  - `tool-b` final enforcement events are assembled through one shared schema helper.
  - obsolete `caller_subject_spiffe_id` was retired from final `toolb_enforcement_decision` events.
  - final `toolb_enforcement_decision` events now emit `subject_spiffe_id`.
  - final `toolb_enforcement_decision` events now emit `delegator_spiffe_id` when present in verified claims.
  - `capiss_mint_decision` now accepts and emits optional `delegator_spiffe_id`.
  - `resource_mint(...)` now routes its final audit events through a local helper that consistently includes delegator provenance for delegated/resource-mint paths.
- Phase 3 retirement applied:
  - duplicated inline tool-b enforcement-event payload assembly was removed.

### 2026-04-26 Open Problem Tracking

- Added `docs/open_problem_log.md` for runtime and trust-path problems that need follow-up independent of slice-progress notes.
- Current tracked problem:
  - `OPL-001`: test-profile `capability-issuer-no-opa-envoy` can intermittently serve an expired SPIFFE SVID during verified-TLS runs, causing `M3.S2-T4` to fail for the right trust reason while insecure curl-based capture still appears healthy.
  - the obsolete final-event field name `caller_subject_spiffe_id` is no longer used in service code for enforcement decisions.
- Focused sanity checks completed:
  - delegated capiss mint-provenance UT: passed
  - tool-b final allow/deny schema UTs: passed
  - `make qa-trace`: passed
- This phase-4 note is superseded by later completed full-suite runs and by the 2026-05-08 M4 semantic trace closure slice below.


## 2026-04-24 Slice Started: Verified Client Requests

- Goal: remove `--insecure` from normal HTTPS request execution paths that are used as black-box proof in M2/M3, and replace them with a single verified TLS request model.
- Scope of this slice:
  - harness HTTPS request helpers in `scripts/rogue_node_tests.sh`
  - demo client HTTPS request helpers in `agents/agent-a/client.sh`
  - authored requirement and architecture deltas for verified client requests
  - E2E/spec proof paths that currently depend on those helpers
- Locked design decisions for this slice:
  - the final HTTPS request must use one verified TLS connection
  - the helper must verify both trust chain and expected SPIFFE URI SAN
  - the final request path must not depend on IP pinning or `Host:` header spoofing
  - DNS/TCP readiness checks may remain, but they are not treated as proof of verified service identity
- Explicitly out of scope:
  - service runtime topology changes
  - Envoy trust policy changes
  - Redis/OPA/runtime service-to-service trust model changes
  - adding a second parallel request mechanism

- Phase 2 test design applied:
  - representative black-box proof paths tightened on existing cases:
    - `M3.S2-T1` now requires issuer verified-identity evidence
    - `M3.S4-T2` now requires tool-b verified-identity evidence
  - `trace/tests.yaml` now maps these proof cases to:
    - `REQ-M2-R10`
    - `REQ-M2-R11`
- Expected failing baseline before implementation:
  - current helpers do not yet emit `verified_capiss_spiffe_id.txt` / `verified_capiss_result.txt`
  - current helpers do not yet emit `verified_toolb_spiffe_id.txt` / `verified_toolb_result.txt`
  - therefore the tightened proof cases should fail until the verified request helper is implemented

## 2026-04-26 Harness Fix: M1 Rogue Attestation False Negatives

- Problem found:
  - `M1-T1`, `M1-T2`, and `M1-T3` were failing even though rogue attestation was correctly denied by SPIRE.
  - The failure was in harness classification, not in M1 security behavior.
- Root cause:
  - `run_rogue_attest_should_fail(...)` in `scripts/rogue_node_tests.sh` was using fragile live log polling.
  - The helper previously mixed timeout budgets, then still depended on seeing denial text before the rogue agent process had fully exited and flushed its final log lines.
- Fix applied:
  - give the helper one local 60-second wait budget
  - wait for the rogue agent process to exit
  - classify the final copied log after process exit instead of polling for denial strings live
- Validation:
  - rebuilt `rogue-tests`
  - reran targeted tests with the documented command:
    - `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M1-T1,M1-T2,M1-T3 rogue-tests`
  - result:
    - `Total: 3`
    - `Passed: 3`
    - `Failed: 0`

## 2026-04-26 No-OPA Test Runtime Fix

- Problem found:
  - `M3.S2-T4` was still failing after the verified-request helper fixes.
  - The remaining failure was a real runtime mismatch: the no-OPA path returned Envoy `504 upstream request timeout` instead of the authored fail-closed JSON body.
- Root cause:
  - the test-only `capability-issuer-no-opa` service used `OPA_URL=http://opa-missing:8181/...`
  - that unresolvable hostname caused slow DNS failure inside `urllib`
  - `capiss` eventually produced `{"error":"denied","reason":"opa_unavailable"}`, but only after Envoy's `15s` upstream timeout had already returned `504`
- Fix applied:
  - changed the test-only `OPA_URL` to a resolvable closed-port target on the same app network:
    - `http://redis:8181/v1/data/capiss/allow`
  - this preserves the same unavailable-OPA semantics while making failure fast and deterministic

## 2026-05-08 M4 Semantic Trace Closure Slice

- Problem found:
  - Several active M4 requirements were semantically implemented but were not represented by focused black-box E2E proof.
  - `REQ-M4-P5` described future signed discovery receipts as if it were an active M4 requirement.
  - `REQ-M4-E2` mixed black-box requirement wording with the architecture choice of a shared in-process implementation.
- Phase 1 authored:
  - Created `docs/slices/m4-semantic-trace-closure/` with plan, requirements delta, architecture delta, ADR, DDR, implementation contract, retirement contract, and validation notes.
- Requirements and architecture updates:
  - Moved signed discovery receipts out of active M4 scope and into future scope.
  - Reworded `REQ-M4-E2` to require consistent observable PEP enforcement semantics.
  - Kept the shared in-process implementation as an architecture/design choice, not as the black-box requirement itself.
  - Removed the inactive signed-receipt requirement from `ARCH-006`.
- Black-box proof updates:
  - Added focused M4 E2E cases:
    - `M4-T11`: delegated mint authority amplification is denied.
    - `M4-T12`: wildcard/non-concrete delegated resource mint is denied.
    - `M4-T13`: Redis budget and registry TTLs are bounded by root token expiry.
    - `M4-T14`: protected resource use with an already-minted token does not require capiss on the hot path.
  - Updated `trace/tests.yaml` so M4 requirement coverage is represented through suite/case evidence instead of relying on unit-level proof.
  - Updated readable, detailed, and command-level test specifications for the new M4 cases.
- Artifact cleanup:
  - Removed the stale `M4-P5` row from `docs/unit_test_spec.md` after signed receipts were moved out of active requirements.
- Validation completed:
  - `sh -n scripts/rogue_node_tests.sh`: passed.
  - `make qa-trace`: passed.
  - Targeted M4 E2E: passed, `14/14`.
  - Clean full E2E: passed, `46/46`, with two accepted alternate-isolation warnings:
    - `M3.S2-T3`: DNS resolution timeout while reaching OPA from edge.
    - `M3.S2-T5`: DNS resolution timeout while reaching capability-issuer from edge.
  - `make qa-evidence`: passed, `validated=46/46`, `warnings=2`.
  - `make qa-quality`: passed, unit baseline `164 passed`.

## 2026-05-14 M4a Jira Project Access Slice

- Implemented the M4a mock-default Jira project access slice:
  - `capiss` canonicalizes `aud=jira-tool`, `act=read`, `res=jira-tool:/project:<PROJECT_KEY>`.
  - OPA allows only `spiffe://example.org/agent-a` to mint `jira-tool:/project:IAM`.
  - `jira-tool-envoy` is the mTLS edge boundary for Jira-shaped issue reads.
  - `jira-tool` verifies root Jira tokens, binds token subject to the Envoy caller identity, enforces project scope before upstream use, consumes Redis budget/rate state, verifies successful upstream project fields, and emits `jiratool_enforcement_decision`.
  - `jira-mock` provides deterministic broad-upstream fixtures for `IAM-*` and `NAS-*`.
  - `agents/agent-a/jira_demo.sh` and `scripts/jira_live_smoke.sh` are explicit operator actions and do not run automatically.
- Review findings fixed during closure:
  - corrected the `M4a-T9` mock-log jq assertion that caused a false failure;
  - added capiss mTLS `/health` readiness after the existing `M4-T14` capiss restart path;
  - added M4a mint short-circuits so downstream protected reads do not hide mint setup failures;
  - added Jira-tool unit coverage to satisfy the existing `make unit-trust` coverage gate.
- Validation completed:
  - `pytest tests/unit/jiratool/test_authorization.py`: passed, `17 passed`.
  - `make unit-trust`: passed, `194 passed`, total line coverage `89.62%`.
  - targeted M4a E2E: passed, `10/10`.
  - clean full E2E: passed, `56/56`, with the two accepted existing M3 isolation warnings:
    - `M3.S2-T3`: DNS resolution timeout while reaching OPA from edge.
    - `M3.S2-T5`: DNS resolution timeout while reaching capability-issuer from edge.
  - `make qa-trace`: passed, report at `artifacts/quality/traceability_report.json`.
  - `make qa-evidence`: passed, `validated=56/56`, `warnings=2`, report at `artifacts/quality/evidence_report.json`.
  - `make qa-quality`: passed, unit baseline `194 passed`.
- Evidence paths:
  - deterministic E2E evidence: `artifacts/rogue-tests/M4a-*`
  - timing artifacts: `artifacts/rogue-tests/guard_timings.tsv`, `artifacts/rogue-tests/guard_timings_top25.txt`
  - trace/evidence reports: `artifacts/quality/traceability_report.json`, `artifacts/quality/evidence_report.json`
- Remaining note:
  - live Jira smoke was not run in this environment because live Jira configuration was not provided; it remains explicit opt-in via `make jira-live-smoke` and writes to `artifacts/jira-live-smoke/`.

## 2026-06-06 M5 Varambu Audit Demo Slice

- Implemented the Varambu audit demo flow:
  - added top-level `varambu` CLI with `start`, `audit`, `show-audit-logs`, and `audit-file`;
  - retained `start_Varambu` as a compatibility wrapper around `varambu start`;
  - added active capiss audit tailing into per-session `artifacts/varambu-demo/<session>/capiss_audit.jsonl` and `capiss_audit.log`;
  - added current-session selection through `artifacts/varambu-demo/current`;
  - added local-time audit formatting through `VARAMBU_TZ`, with UTC fallback;
  - enriched authoritative `capiss_mint_decision` events with subject, resource context, correlation, issued/expires/logged UTC and local times, TTL, token IDs, and policy metadata;
  - kept bearer token values and upstream secret material out of capiss audit events and Varambu audit artifacts.
- Authored requirements, architecture, slice plan, test plan, and trace updates:
  - `REQ-M4-O2` extended for enriched mint-decision audit fields and secret exclusion;
  - `REQ-M5-VA1` added for Varambu session audit artifacts and command-line display;
  - `ARCH-032` added for Varambu demo audit session state and active tailing;
  - `M5-T42` added for runtime Varambu audit-file proof.
- Validation completed in this environment:
  - `make unit-trust`: passed, `244 passed`, total line coverage `86.40%`.
  - `make qa-trace`: passed, report at `artifacts/quality/traceability_report.json`.
  - `make qa-quality`: passed, unit baseline `244 passed`.
  - `bash -n varambu start_Varambu scripts/rogue_node_tests.sh`: passed.
  - `python3 -m py_compile scripts/varambu_audit.py services/capability-issuer/app.py services/codex-jira-mcp-adapter/server.py scripts/validate_traceability.py`: passed.
  - `./varambu audit-file`: passed and resolved current session audit artifact paths.
- Validation not completed in this environment:
  - Docker-backed targeted E2E `M5-T42` was not run because this process cannot connect to `/var/run/docker.sock` (`permission denied while trying to connect to the docker API`).
  - Run when Docker daemon access is available:
    - `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M5-T42 rogue-tests`
    - `make qa-evidence`
