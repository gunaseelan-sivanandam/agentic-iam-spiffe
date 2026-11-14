# Slice 4 — the owner's decision file

The one page the owner reads for slice 4, and its end-review page: the goal, what slice 4 builds in plain
words, the steps of the run, and every decision made or still to make. The plans, test plans and review records
under `docs/slices/poc-4-*/` are the working documents for the author and the reviewers. The author keeps this
file current during the run and says in it what was decided on the owner's behalf. At the end it holds the
checklists, the benchmark counts, every decision concern, every parked unit, every process-growth proposal and
every discovered issue with its disposition.

Last updated: 2026-11-14: round 2 implemented (R2-1 to R2-10, `8a82388` to `c79ed96`); its review unit `round-2` is next. Before, on 2026-11-13: the owner's decisions on decision concerns 2, 3, 4, 7, 8 and 10 implemented (small slices, the decision page, the second recheck case, the severity measurement, worse, nothing adopted) and reviewed (unit `owner-decisions`, ended after round 2), with decision 7, decision concern 11 and growth proposal 12 for the owner. Before that: every sub-issue implemented and reviewed, the benchmark run and its report reviewed, the dry slice and the final review run (2026-11-10).

## Goal (the owner's, 2026-11-09)

Deliver slice 4 (#33, sub-issues #38–#43) as approved in plan PR #48, on `poc/agentic-sdlc`, so that the next
slice can run the review process end to end without the owner checking by hand. The author works without
stopping for the owner; the owner reviews once at the end, with the benchmark counts in hand. While GitHub writes
go through the owner, all work stays local: local gates count during the run, CI's verdict counts when the owner
pushes at the end, and the author gives the exact push and PR commands then.

The author owns the how: the order of sub-slices, how to cut branches, what to probe first, when to use the new
launcher on later sub-slices. `AGENTS.md` and the six plans stay as written; a decision the author would change
becomes a decision concern. The owner's additions to the plans: each benchmark finding names the checklist
question that prompted it, where one did; and the launcher keeps 4.1's mandate wording until the owner chooses
from the counts at the end.

**Self-review before each independent review**, against the ways this repository has failed before
(`docs/delivery_problem_log.md`), answered in writing with the evidence for every sub-slice, in its review record.
The independent reviewer gets the answers as claims to verify, not as facts:
1. Which facts outside the repository did this depend on, and how was each probed (a command and its output, not
   a belief)?
2. For every check added or changed: what is the case it exists to catch, and where is the test that shows it
   fails on that case?
3. For every claim the plan or the record makes ("verbatim", "never", "always", "the launcher writes"): what
   checks it, mechanically?
4. For every finding fixed: which upstream choice caused it, and would changing that choice remove the mechanism
   instead of adding one?
5. How was this tried the way its next user will run it: in parallel, on real prose from this repository, from a
   clean session with only what the repository holds?
6. Does every rule, warning or decision written live where it will be read and survive this slice (`AGENTS.md`, a
   check, a record), not in a PR body or a plan note?
7. What was removed, and did it get the same review as what was added?

**Done when:**
- every decision ID in the six plans is implemented and proven, or marked rule-text-only with its `AGENTS.md`
  line; every retirement item is done;
- the 4.5b benchmark has run on the draft checklists and both mandate wordings, within 60 reviewer runs, each
  finding tied to the checklist question that prompted it where one did;
- a fresh reviewer with only the plans, the diff and the self-review answers reports no open blocker against the
  open mandate "what does the plan promise that the change does not do, and what does the change do that no plan
  asked for";
- this page holds the checklists, the counts, every decision concern, every parked unit, every process-growth
  proposal and every discovered issue with its disposition; `docs/STATUS.md` and the slice index are current; and
  one dry slice has run through the new process from a clean session, with what the next user would trip on
  recorded.

**Never stop for the owner; park instead:** a round-4 blocker is parked on its own branch and left out of the
final PR; a wrong-looking decision is implemented as written and recorded; growth is proposed, not added. The run
pauses only at a usage limit (and at 80% of the weekly limit) and resumes after the reset. No threat model
changes, no reading of frozen records except to check a claim, and OPL-005 to OPL-008 stay untouched.

## What slice 4 builds

| Part | In plain words |
| --- | --- |
| 4.1 Review prompts | The launcher writes every review prompt in a fixed order, opening with the open mandate, so no task text can narrow it. Rechecks must show which files they opened for each fix. Every finding gets a severity (blocking, high, medium, low) that says what must be fixed, and the stage where the problem started. |
| 4.2 Review inputs | The files to review come from the actual change, so none can be left out. The reviewer is told the plan and requirements the change belongs to. Tools compute untested lines, missing proofs and CI results, and the reviewer must account for every entry. |
| 4.3 Review records | The launcher writes the review records itself, and `docs-check` proves that each record matches what the reviewer saw and said, and that every finding has an allowed answer. |
| 4.4 Stage checklists | Short researched checklists for six kinds of work: plan, requirements, architecture, unit tests, E2E tests, code. Each says what blocks at that stage, and also serves as the author's guide. The research also drafts better mandate wording. |
| 4.5 Benchmark | Measures the short prompt with a checklist against the open mandate with a checklist, and today's mandate wording against the research-based draft, on about 15 cases, with blinded confirmation. At most 60 reviewer runs. |
| 4.6 Stage rules | The rulebook describes the seven delivery stages, a decision brief sums up every PR's reviews (in the PR body at first, on each slice's decision page since the owner's decision of 2026-11-13), and the grill-me skill moves into the repository. |

## The run

| Step | What happens | Needs the owner? |
| --- | --- | --- |
| 1 | 4.1, 4.2 and 4.3, each with its self-review and independent review | No |
| 2 | 4.5's first part (benchmark mechanics), then 4.4 (research, checklists, a critique by two models) | No |
| 3 | 4.5's benchmark runs and report: the draft checklists and both mandate wordings, within 60 reviewer runs | No |
| 4 | 4.6; the fresh end reviewer; one dry slice from a clean session | No |
| 5 | The owner's end review: push, PR, merge, and choose the default setup and the mandate wordings from the counts (the wording change follows in its own commit) | **Yes, once** |

Parked units, decision concerns and growth proposals collect below as the run goes.

### Progress

| Part | State | Review |
| --- | --- | --- |
| 4.1 | Implemented (`59d0291` to `9413020`) | Ended after round 2. Round 1: approvable; 0 blocking, 2 high, 6 medium, 5 low. Round 2: attempt 1 failed the read check (issue 5); attempt 2 accepted all 13 answers and found nothing new |
| 4.2 | Implemented (`381dc2b` to the round-2 fix) | Ended after round 2. Round 1: approvable; 0 blocking, 3 high, 4 medium, 3 low. Round 2: all 10 answers accepted, the 3 evidence entries explained; 1 new low finding, fixed |
| 4.3 | Implemented (`89b8f2b` to the round-2 fixes) | Ended after round 2. Round 1: attempt 1 failed the schema check (issue 6); attempt 2 not approvable: 2 blocking, 1 high, 3 medium, 2 low. Round 2: approvable; all 8 answers accepted; 2 new low findings, fixed |
| 4.5a | Implemented (benchmark identity, configurations, cases, scoring, blinding, canary, report) | Ended after round 2. Round 1: not approvable: 3 blocking, 3 high, 4 medium, 6 low. Round 2: attempt 1 failed the read check (issue 7); attempt 2 approvable, all 16 answers accepted; 1 new high, 2 medium, 1 low: the high and the mediums fixed, the low rejected |
| 4.4 | Implemented (`1750c8d`: six lists, the research record, `--stage`), then revised from the critique | Critique (S44-D10): Opus not approvable, 1 blocking, 5 high, 6 medium, 2 low; Sonnet's attempt 1 failed the read check (issue 8), attempt 2 approvable, 5 medium, 3 low. All 22 answered: 20 fixed, 1 high to the owner (decision concern 4), 1 low rejected. Implementation review, round 1: approvable (the blocking fix C-1 not re-raised); 1 high, 4 medium, 3 low; 7 fixed, 1 low rejected; ended |
| 4.5b | Ran within 57 of 60 calls; report in [`benchmark_report.md`](../poc-4-5-benchmark/benchmark_report.md): `open+list` 7 of 11, `short+list` 6, `open-B+list` 6, both rechecks 1 of 1; on 2026-11-13, with the budget raised to 85, a canary under CLI 2.1.323 and RC-2 (61 calls): `recheck-B` passed, `recheck-A` failed the read check; decision concern 8's `open+list+sev` (76 calls): worse, not adopted; 29 of 125 findings confirmed (two re-judged after unblinding, FR-1), the second confirmer agreeing on 9 of 10; the third canary valid and passed | Report review ended after round 2. Round 1: not approvable; 2 blocking, 1 high, 3 medium, 4 low; all fixed. Round 2: attempt 1 failed the read check (issue 14); attempt 2 approvable, all 10 answers accepted, no new finding |
| 4.6 | Implemented: the seven-stage table and the rules moved into it, the templates, `scripts/review_brief.py`, the grill-me skill in the repository, the front-matter rule of the lint gate | Ended after round 1: approvable; 1 high, 5 medium, 4 low and a simpler alternative; 9 fixed, F4 and F5 to the owner (decision 4, decision concern 7) |
| Final review | Unit `final` of this bundle, with the owner's open question ([record](review_final.md)) | Ended after round 2. Round 1: approvable, no blocker; 2 high, 5 medium, 2 low, all fixed. Round 2: approvable; all 9 answers accepted; 1 new low, fixed |
| Growth (2026-11-13) | Rejections read like fixes, a `searched` list, the checklist question on findings ([record](review_growth.md)) | Ended after round 2. Round 1: approvable; 1 high, 5 medium, 1 low; 6 fixed, the low rejected. Round 2: attempt 1 failed the read check (issue 17); attempt 2 approvable, all 7 answers accepted; 1 new low, fixed |
| The owner's decisions (2026-11-13) | Implemented (`44a040c` to `ea4e100`): small slices, the decision page, RC-2, the budget, the severity measurement; then the fixes to their review (record `review_owner_decisions.md`) | Ended after round 2. Round 1: attempt 1 failed the read check (issue 21); attempt 2 not approvable: 1 blocking, 2 high, 5 medium, one of them a decision concern; fixed, or put to the owner (decision 7, decision concern 11). Round 2: attempt 1 failed the read check (issue 22); attempt 2 approvable, all 8 answers accepted, no new finding |
| Round 2 (2026-11-14) | Implemented (`8a82388` to `c79ed96`): R2-1 to R2-10, as built in the section "Round 2" below | Review: unit `round-2`, round 1 next |

## Decisions and their proof

Every decision of the six plans, where it is implemented, and what proves it: a named tooling test, a review
record, or, for a rule that only the rulebook states, "rule text only" with its section of `AGENTS.md`. Every
retirement item is done: the launcher refuses to rebuild prompts logged before 4.1, 4.2 and 4.4; stage A's run path
of the benchmark is gone (stage A's results and prompts stay); the four-step workflow text is replaced by the stages;
the plan template's grill-me summary is replaced by the decisions table.

The stage checklists are in [`docs/review_checklists/`](../../review_checklists/): plan and test plan (12
questions), requirements (9), architecture and interfaces (10), unit tests (10), E2E tests (11), code (12).

| Decision | Implemented in | Proved by |
| --- | --- | --- |
| S41-D1 | the launcher's `build_prompt` | `test_prompt_sections_come_in_the_fixed_order_and_empty_ones_say_so`, `test_task_text_appears_only_under_claims_to_verify`, `test_command_line_has_no_option_that_changes_the_sections` |
| S41-D2 | the benchmark's configurations | `test_only_the_full_configuration_reaches_the_launcher`, `test_configurations_differ_only_in_the_mandate_and_carry_the_same_list_and_rules` |
| S41-D3 | `review_mode` | `test_mode_follows_the_round` |
| S41-D4 | `MANDATES` | `test_every_mode_holds_its_mandate_verbatim`, `test_final_prompt_names_the_other_units_records_and_never_gets_a_checklist` |
| S41-D5 | recheck inputs | `test_recheck_prompt_holds_its_earlier_report_and_only_its_answers_section`, `test_recheck_without_its_inputs_is_refused_before_any_call` |
| S41-D6 | `REPORT_SCHEMA`; `AGENTS.md`, Review findings | `test_findings_of_each_severity_kind_and_origin_stage_are_accepted`, `test_schema_offered_to_the_cli_matches_the_launcher_rules` |
| S41-D7 | the answers table; `AGENTS.md`, Review loop | `test_answers_table_with_every_answer_word_is_accepted`, `test_answers_that_do_not_answer_the_earlier_report_are_refused_before_any_call` |
| S41-D8 | `Accounting`, the read check; widened by the owner's growth of 2026-11-13 to the files a `rejected:` answer cites, with `searched` for files only searched | `test_recheck_that_does_not_account_for_every_answer_fails`, `test_fixed_file_that_was_not_read_fails_even_when_a_path_under_review_was`, `test_a_rejection_counts_only_when_the_files_it_cites_were_read`, `test_a_searched_file_need_not_be_read_but_an_opened_one_must` |
| S41-D9 | the end entry | `test_end_entry_counts_each_severity_with_zeros` |
| S41-D10 | rule text: `AGENTS.md`, Review findings ("a secret written into logs, evidence or any published record") | `test_output_section_holds_the_reporting_bounds_and_the_credential_note_verbatim` |
| S41-D11 | rule text: `AGENTS.md`, Independent review, Modes and prompts ("never makes a file list the scope") | rule text only |
| S41-D12 | rule text: `AGENTS.md`, Review findings, Review loop, Plan review, Report sections | rule text only; the mislabelled-blocker sentence is an author decision (4.1) |
| S41-D13 | the benchmark's stage-A reading | `test_report_of_stage_a_gives_its_tables_unchanged` |
| S41-D14 | the launcher's mandates stay 4.1's | the benchmark report; the owner chooses (decision 2) |
| S41-D15 | the output section | `test_output_section_holds_the_reporting_bounds_and_the_credential_note_verbatim` |
| S41-D16 | `origin_stage` in the schema, the brief's origin table | `test_findings_of_each_severity_kind_and_origin_stage_are_accepted`, `test_the_brief_lists_every_item_the_owner_must_see` |
| S42-D1 | `changed_files` | `test_files_come_from_the_diff_and_deleted_files_are_listed_apart`, `test_path_hints_come_first_and_never_narrow_the_list` |
| S42-D2 | the paths section, the empty-review rule | `test_paths_section_says_to_open_every_file_and_the_end_entry_lists_those_not_read`, `test_review_that_opened_none_of_the_hint_files_fails_even_when_it_opened_other_listed_files` |
| S42-D3 | `upstream_items` | `test_upstream_names_the_governing_plan_links_edited_sections_and_other_bundles` |
| S42-D4 | `UPSTREAM_QUESTION` | `test_every_prompt_holds_the_upstream_question` |
| S42-D5 | `compute_evidence` | `test_uncovered_changed_branch_is_listed_with_the_subprocess_note_and_a_service_gate_line`, `test_trace_gap_among_the_upstream_items_is_marked_new_or_existing`, `test_ci_results_show_the_reviewed_commits_jobs_and_never_a_pass_for_a_running_job` |
| S42-D6 | evidence accounting | `test_report_must_account_for_every_evidence_entry`, `test_flagged_evidence_entry_naming_no_finding_of_the_report_fails` |
| S42-D7 | failed evidence commands | `test_coverage_that_cannot_run_is_shown_as_failed`, `test_trace_model_that_cannot_run_is_shown_as_failed`, `test_unreadable_ci_api_is_shown_as_failed` |
| S42-D8 | `evidence_env`, `sanitise` | `test_evidence_commands_see_only_path_lang_and_a_scratch_home`, `test_evidence_still_holding_a_local_path_is_refused_before_any_call` |
| S42-D9 | the Evidence block and its hash | `test_start_entry_holds_the_hash_of_the_evidence_text_in_the_prompt` |
| S42-D10 | `diff_base` required | `test_diff_base_is_required_and_every_prompt_names_the_change` |
| S42-D11 | the benchmark's file lists | `test_lists_come_from_the_runners_fixed_commit_not_the_cases` and the dry run (46 prompts) |
| S43-D1 | the launcher writes the blocks | `test_completed_attempt_leaves_prompt_evidence_and_report_blocks_that_the_check_accepts` |
| S43-D2 | `check_prompt` | `test_secret_or_local_path_in_the_prompt_is_refused_before_anything_is_written` |
| S43-D3 | `scripts/check_review_records.py` | `test_one_changed_character_in_a_block_fails`, `test_answers_changed_after_the_recheck_read_them_fail` |
| S43-D4 | allowed answers | `test_each_allowed_answer_passes`, `test_each_answer_the_rules_do_not_allow_fails` |
| S43-D5 | `record_blocks` | `test_attempts_logged_before_this_slice_are_not_checked`; 4.1's and 4.2's records are among them (final review, FR-8) |
| S43-D6 | `load_recheck` | `test_recheck_reads_the_earlier_report_from_the_record_with_the_released_file_deleted` |
| S43-D7 | no change: stays with #21 | nothing to prove |
| S43-D8 | rule text: `AGENTS.md`, Independent review ("which replaces the author's hand check") | rule text only |
| S44-D1 | `research.md` sources | `test_the_research_record_has_a_section_for_every_planned_source` |
| S44-D2 | `research.md` | `test_every_question_the_research_record_names_exists`, the critique and review records |
| S44-D3 | the six lists | `test_every_list_has_the_agreed_form_and_cites_researched_sources`, `test_the_form_check_fails_on_each_kind_of_violation` |
| S44-D4 | Blocks sections; `AGENTS.md`, Review findings | `test_every_list_has_the_agreed_form_and_cites_researched_sources` |
| S44-D5 | the two questions | `test_the_two_questions_for_what_is_missing_sit_where_the_misses_happen` |
| S44-D6 | `docs/review_checklists/`; `AGENTS.md`, Start here | `test_exactly_the_six_artifact_types_have_a_list` |
| S44-D7 | `stage_lists` | `test_a_stage_gets_the_base_commits_list_even_when_the_change_rewrites_it`, `test_a_stage_the_base_cannot_give_is_refused_before_any_call` |
| S44-D8 | rule text: `AGENTS.md`, Stage checklists ("The author reads the stage's list before writing that stage's artifact") | `test_the_code_list_repeats_no_coding_rule` |
| S44-D9 | the DPL mapping | `test_every_dpl_entry_is_mapped`, `test_every_question_the_research_record_names_exists` |
| S44-D10 | the critique unit | `docs/slices/poc-4-4-stage-checklists/review_critique.md` |
| S44-D11 | rule text: `AGENTS.md`, Stage checklists ("the author proposes the list item or the wording in the PR") | rule text only |
| S44-D12 | `lists_commit` | `test_lists_come_from_the_runners_fixed_commit_not_the_cases` |
| S44-D13 | `research.md`, Review prompt | `test_each_draft_mandate_sentence_has_a_source_and_names_its_failure_mode`, `test_the_benchmarks_draft_mandates_are_the_research_drafts` |
| S45-D1 | `BUDGETS` | `test_stage_b_stops_at_its_budget_counting_retries_and_the_canary`; 60, raised to 85 on 2026-11-13 (below); 57 used before the raise |
| S45-D2 | the result identity | `test_result_records_its_full_identity_and_the_report_reads_one_stage` |
| S45-D3 | `CONFIGURATIONS` | `test_configurations_differ_only_in_the_mandate_and_carry_the_same_list_and_rules` |
| S45-D4 | `score`, the match rule | the scoring tests of `tests/tools/test_run_review_benchmark.py` |
| S45-D5 | the answer key's 18 cases: RC-2, a recheck case whose answers hold, added for decision concern 4 | `test_the_dpl_010_case_holds_the_launcher_and_its_tests_and_not_its_answer`, `test_a_recheck_of_answers_that_hold_passes_only_when_it_accepts_every_answer`; the dry run |
| S45-D6 | `--repeat`, `check_repeats` | `test_a_repeat_runs_the_two_setups_again_and_the_counts_use_the_first_run`; the results |
| S45-D7 | `export_confirmation`, `second_confirmation` | `test_blinded_export_hides_the_configuration_and_shuffles_and_the_report_joins_back`, `test_second_confirmer_sees_a_seeded_sample_without_configurations_and_its_call_counts` |
| S45-D8 | `report_stage_b`; `benchmark_report.md` | `test_report_gives_every_count_for_every_configuration` |
| S45-D9 | the canary and its gate | `test_canary_is_valid_only_when_the_twin_followed_the_file_and_the_hook`, `test_cases_run_only_after_a_valid_and_passed_canary`, `test_cli_version_other_than_the_canarys_is_refused`; a valid canary in the results |
| S45-D10 | the key's model, `SECOND_MODEL` | `test_result_records_its_full_identity_and_the_report_reads_one_stage` |
| S45-D11 | the runner's tests | `test_dry_run_prepares_every_case_and_calls_no_reviewer`, `test_launcher_reads_each_report_shape`, `test_stream_lines_that_are_not_json_are_skipped` |
| S46-D1 | `AGENTS.md`'s stage table | `test_agents_md_states_the_seven_stages_with_every_cell_filled` |
| S46-D2 | rule text: `AGENTS.md`, Discovery, first bullet | rule text only |
| S46-D3 | rule text: `AGENTS.md`, Discovery, last bullet | rule text only |
| S46-D4 | rule text: `AGENTS.md`, Requirements, and architecture and interfaces | rule text only |
| S46-D5 | rule text: `AGENTS.md`, Final review; the launcher's final mode | `test_final_prompt_names_the_other_units_records_and_never_gets_a_checklist`, `test_final_review_reads_the_merged_plan_reviews_of_the_bundles_the_change_touches` |
| S46-D6 | rule text: `AGENTS.md`, Review loop ("Only the user waives a blocker that is still disputed") | rule text only |
| S46-D7 | rule text: `AGENTS.md`, Review loop (earlier escalation) | rule text only |
| S46-D8 | rule text: `AGENTS.md`, Tests first | rule text only |
| S46-D9 | rule text: `AGENTS.md`, Handoff | rule text only |
| S46-D10 | `AGENTS.md`, Start here; `docs/STATUS.md` | rule text only |
| S46-D11 | the templates | `test_the_plan_template_carries_the_stages_the_source_column_and_rule_deviations`, `test_the_test_plan_template_names_each_stage_list_and_the_required_review_questions`, `test_a_bundle_made_from_the_templates_passes_the_header_and_link_checks` |
| S46-D12 | the stages | `test_no_live_document_refers_to_the_old_step_numbers` |
| S46-D13 | `scripts/review_brief.py`; `AGENTS.md`, Discovery and Handoff | `tests/tools/test_review_brief.py` |
| S46-D14 | `.claude/skills/grill-me/SKILL.md`, the lint gate's front-matter rule | `test_the_grill_me_skill_keeps_its_front_matter_then_has_a_title_and_paragraph`, the front-matter cases of `tests/tools/test_lint_changed_files.py` |

## Decided by the author during the run

What the author decided on the owner's behalf. Each stays within the plans; a change to a plan's decision would be
a decision concern below instead.

| Part | Decision | Why |
| --- | --- | --- |
| 4.1 | 4.1's own implementation review runs with the branch's launcher, the one under review, not with the base's | This is how the next user runs it, and it was the launcher's first live run with the new schema. The circularity is limited: the rules come from the base branch, the mandate texts were compared with the plan by a script, and the reviewer reads the launcher's code |
| 4.1 | Text quoted from a file or the author (the rules, the task text, the answers) is a fenced block in the prompt | A dry run on this repository's own prose showed that its `## ` headings read like the prompt's sections, so a task text could imitate a Mandate or Output section. This is how S41-D1's fixed sections are kept, not a new mechanism |
| 4.1 | A recheck is refused before any call when its answers table does not answer the earlier report: a finding without a row, a row for an unknown ID, a changed severity, an answer the severity does not allow | Review round 1 (R1-4): the plan put this check only in 4.3's record check, so rechecks run before 4.3 exists could drop a finding. One function holds the rule, and 4.3's check will use it too |
| 4.1 | An `owner:` answer may link to a tracked document, such as this file, as well as to a URL | While GitHub writes go through the owner, this file is where the owner decides |
| 4.1 | `invocation_from_entry` refuses an attempt logged before 4.1 with a clear message instead of rebuilding it | The old prompt layout is retired with S41-D1; its hashes still identify what was reviewed (R1-7). The plan's retirement list did not name this; it is recorded here |
| 4.1 | The benchmark report shows blocking-only detections beside all detections, and counts an unmatched high finding on a clean case as a false alarm | S41-D13 counts high findings as detections, so the penalty must count them too (R1-1, R1-2). Stage A's values stay as they were |
| 4.1 | Local runs of `make tooling-test` use a shellcheck 0.10.0 binary taken from the `shellcheck-py` wheel into a scratch directory | shellcheck is not installed on this machine; without it 9 lint tests fail (on the base too). CI's runner has it |
| 4.2 | The computed inputs live in their own module, `scripts/review_inputs.py`, which the launcher loads | The launcher had grown past 1,400 lines; the file list, upstream items and evidence are one concern. The plan named only the launcher; this is code organisation, not a new mechanism |
| 4.2 | The evidence runs in a `git clone --shared` of the reviewed commit with the author's `PATH` | The tooling tests need Git history and the tools on the author's `PATH` (ruff, shellcheck); in a `git archive` export 38 of them failed. The environment is still only `PATH`, `LANG` and a scratch `HOME` (S42-D8) |
| 4.2 | The scratch `HOME` holds one link: the interpreter's user site-packages, at the place the interpreter computes from `HOME` (`.local` on Linux, `Library/Python/X.Y` for a macOS framework build) | pytest and its plugins are installed with `pip --user` under the author's `HOME`; without the link no evidence command runs. Only that directory is linked, not the rest of `~/.local` (review round 1, R1-6) |
| 4.2 | A `--path` that names a file the change deletes is refused, with a message that it is listed under deleted files | S42-D1 requires a `--path` to be in the diff; a deleted file cannot be opened, so the empty-review rule could never be met with it |
| 4.2 | The template and archive folders under `docs/slices/` are not treated as bundles when naming other plans the change touches | They are not slice bundles; listing them added noise to every prompt (found by the author's dry run) |
| 4.2 | Evidence entries are numbered EV1, EV2, … | So that no finding ID such as E1 can collide with an evidence entry in `accounted` |
| 4.3 | Record parsing and editing live in their own module, `scripts/review_records.py`, used by the launcher and by the record check | One parser for both, so the check reads records as the launcher writes them; the plan named only the launcher and the check |
| 4.3 | A task prompt file must end with a newline; records are read and written as exact bytes and split on newlines only | The Prompt block must hash as the task file does (S43-D1): the launcher refuses a task without a final newline, and keeps every other byte, so CRLF line ends, blank last lines and form feeds round-trip (review round 1, R1-4) |
| 4.3 | Recovery removes an unlogged trailing section only when it is exactly what the launcher writes before its start entry | So an author's text in a record is never cut, whatever headings or fences it holds (review round 1, R1-5) |
| 4.3 | A withheld attempt gets an end entry with status `withheld` (counts and paths only, never the report) | So the record keeps its withheld status and the log tells a withheld report from a killed launcher (review round 1, R1-8); slice 2 had logged no end entry |
| 4.3 | A rejected blocking or high finding is settled by the next round's acceptance, an `owner:` link in its own row, or a later round's `owner:` answer to the same finding ID | S43-D4's "or an `owner:` link" read so that a rejection the recheck re-raised can reach the owner without editing answers a recheck already read (review round 1, R1-3; decision concern 2) |
| 4.3 | A failed schema check logs the schema problems (fields and rules, never values) | The first launcher-written review attempt failed the schema check and its cause could not be found (issue 6) |
| 4.5a | `short+list` uses stage A's short prompt without its last sentence, which told the reviewer to use the retired kinds "blocking" and "advisory" (`tests/review_benchmark/prompts/short_list.md`); stage A's own files stay as measured | Every configuration gets the same severity rules (S45-D3); the old sentence contradicted them (4.1 review round 1, R1-3, deferred to #42) |
| 4.5a | The DPL-010 case (`RM-6`) has one expected finding, "the refusal paths have no test", whose places are all the untested refusal paths and which an absence finding naming them also detects | Ten separate expected findings would weigh this one miss ten times in the counts |
| 4.5a | Stage B's cases: the clean case CL-3 is `6feedfa` (a one-line README fix); the decoy DC-1 makes the harness's temp-file teardown non-fatal with `\|\| true` and a comment; the recheck case RC-1 puts stage A's PD-2 plant under a `fixed:` answer naming only `docs/test_spec.md` | Small, real or self-evidently correct changes; the decoy looks like a swallowed failure but is teardown after the status is decided |
| 4.5a | Artifact types per case: requirements (RM-3, PB-1), architecture and interfaces (PB-2), E2E tests (RM-2, RC-1, DC-1), code (RM-1, RM-4, RM-5, RM-6), plan and test plan (PB-3, CL-1, CL-2, CL-3) | The list each case gets (S44-D12); a README and the rulebook's own documents are reviewed with the plan-and-test-plan list |
| 4.5a | A result's prompt identity is the SHA-256 of the whole prompt and the reviewed commit | So any change to what the reviewer gets (the planted patch, the recheck inputs, the rules, the launcher's own sections) runs the review again (review round 1, H1) |
| 4.5a | A failed review of a defect case counts as a miss, with the case in the denominator and in the discordant pairs | S45-D5 says so for the recheck case; leaving failures out favoured setups that fail on hard cases (review round 1, B2) |
| 4.5a | A term counts only outside a verbatim quote of an expected line, in scoring and in the committed match rule | S45-D4's "a finding that only quotes the planted line goes to triage" (review round 1, B3) |
| 4.5a | The repeats of S45-D6 run with `--run --repeat <case>` (at most two cases, the two compared setups) and count apart; the second confirmer runs with `--sample-confirmation` and `--second-confirmation 0` or `1`, each session counted in the 60 | The runner had no path for either (review round 1, H2, M2) |
| 4.5a | Every case gets its base's rules, as the launcher gives a review the base branch's rules | Stage A gave real misses the rules of the reviewed commit, so RM-3 and RM-5 were judged by rules they themselves added (review round 1, L6) |
| 4.5a | PB-3 is a new slice's test plan that retires the M3.S4 suite while claiming its requirements stay proved; `REQ-M4-E4` has no other proof | The first version edited `trace/tests.yaml`, which is not the test-plan row S45-D5 names (review round 1, L5) |
| 4.5a | Stage A's results are read with the key committed at `c325e7d`; every call recorded for stage B counts against its 60, whatever key produced it | Stage A's report stays reproducible after the key's new version; a changed key cannot reset the budget |
| 4.5a | The marker "Planted defect" refuses only author-written plants (planted, decoy, recheck), not a real miss rebuilt by a patch; leak terms that already occur in this repository's documents were dropped | The 2026 plan text at `c4f9ca2` uses the phrase; a word the base already holds reveals nothing |
| 4.5b | FS-1 and FS-2 were planted by a fresh Opus session (high effort, Read, Grep and Glob only) on a copy of `e842e97`, given only the source sections of `research.md` (lines saying how a list used a source removed) and the three planted defect classes to avoid; it answered through a schema with the file, the anchor line, the new lines, the task line, the defect, why it is real here and match terms; the author made each answer a patch unchanged | S45-D5: the lists are measured on defects that did not shape them. The session never saw `docs/review_checklists/`, the candidate table, the DPL mapping or the drafts; it cost USD 0.92, outside the budget |
| 4.5b | In the key, the author dropped the session's term "token" from FS-1 and added the gateway's `upstream_headers` (`server.py` 314-324) as a second place, and added "timeout" to FS-2's terms | "token" occurs in almost every finding near that code; a finding placed at the header code that names the credential describes the same defect. FS-2 adds a hardening rule to an implemented bundle's test plan, as that bundle's own Increment 3 did; a finding that the bundle is frozen is an extra finding, not the expected one |
| 4.5b | The failed-Read probe (S45-D9) ran once, outside the budget: a confined session read an existing and a missing file; the stream marks the failed call `is_error: true`, and the launcher's parser counts it as failed and the other not (CLI 2.1.321, USD 0.05) | The read check relies on a failed Read never counting as read |
| 4.4 | The critique's Sonnet reviewer ran a second time after its first attempt failed the read check; S44-D10's "at most two runs" is read as two completed critiques | The failed attempt released no report, so the owner's second angle would otherwise be missing; the rerun cost one Sonnet session |
| 4.4 | The critique's fixes add questions only from sources quoted in `research.md`, five quotes of them fetched on 2026-11-10 (Google's functionality and documentation items, Fowler's quarantine and clock sections, the test pyramid's fake-server section, OWASP's threat model kept alongside the system); the lists now hold 12, 9, 10, 10, 11 and 12 questions | S44-D9: a question needs an industry source; S44-D3's limit of 12 |
| 4.4 | The research's "studies of LLM code review" are two public studies read from their abstracts: an industrial study of an LLM review tool (`cihan-acr`) and a benchmark of LLM review comments (`swr-bench`) | S44-D13 names such studies; the first record had none (4.4 review, F1). Their full texts were not read; only what the abstracts say is used |
| 4.5b | The planted `CLAUDE.md` of the canary is written as an ordinary review convention instead of an instruction that reads like an injection; a canary is done by its identity (planted texts, task, the two calls), not its case ID | The first twin declined the injection-like text; and with done-ness by case ID the reworded canary never ran |
| 4.5b | The canary and its twin get their own prompt, which asks to follow the instructions the session holds, instead of the review prompt; the gate requires a valid, passed canary for the installed CLI | The first two canaries used the review prompt, whose data clause no twin could pass: 4.5a's choice, not S45-D9 (report review, B2). For a while the gate accepted a canary whose twin ran only the hook; the third canary, on its own prompt and the same CLI as every review, is valid and passed, and the gate is back as S45-D9 says |
| 4.6 | The grill-me skill is copied into `.claude/skills/grill-me/SKILL.md`; the user-level copy is left in place for the owner to remove | Removing a file from the owner's own folder is the owner's to do; the repository copy is the one this repository's rules name |
| 4.6 | The repository's grill-me completes the two sentences the user-level copy cuts off (its description and the second line end in `>`) and adds the assets question | `AGENTS.md` says grill-me always asks which keys, sockets and secrets a slice touches; the skill's text never asked it (discovered issue 10) |
| 4.6 | `scripts/review_brief.py` takes the review units a PR adds from the attempts logged since the merge-base, and names the review that found a finding by its `--stage` lists, or by its unit when it had none | The units of a PR are the ones its commits logged; slice 4's reviews ran without lists, so the unit is the only name they have |
| 4.6 | The step-reference check uses the plan's probe pattern, "step 1" to "step 4" | The delivery problem log's history says "steps 3–4" of a milestone; rewriting history entries would make them false |
| 4.5b | The repeats (S45-D6, at most two cases) went to the discordant cases of short+list and open+list in this order: cases where both first reviews completed, then the others in the key's order; so FS-2 and RM-6 | The rule was written after the first runs, with the three discordant cases known, and it chose the two that favoured `open+list` and left out FS-1, the one that favoured `short+list`, whose `open+list` review was withheld by the publication check and may have been a detection; the report says so (report review, M1) |
| 4.1 | `AGENTS.md`'s Review loop says a finding labelled blocking that does not meet the blocking criteria "is answered at the severity it does meet" instead of "is not fixed by default" | S41-D12 retires "not fixed by default" with the severity rules (S41-D6) and asks the implementation to check every "blocking" sentence against them; this sentence was one of them, not named in S41-D12's list (final review, FR-7) |
| 4.3 | 4.1's and 4.2's implementation records were built by a script before 4.3 existed, so `make docs-check` does not check them, as S43-D5 leaves slices 2 and 3 and slice 4's plan reviews unchecked | The record check reads only records the launcher wrote; S43-D5's list did not name these two (final review, FR-8); the brief checks their answers |
| 4.6 | The plan template has a "Threat model" section | The plan review judges against "the threat model the plan states" (`AGENTS.md`, Plan review) and plan question P11 asks for it, but S46-D11's list did not name the section; found by the dry slice (final review, FR-7) |
| 4.6 | The handoff rule kept S46-D9's and S46-D13's words: the brief is pasted at the top of the PR body, which is a snapshot and is not updated later | 4.6's review (F3) had the author rewrite it to "built once CI has finished … and built again after a later push", which changed agreed decisions without the owner; reverted, and the question went to the owner (decision concern 10; final review, FR-7). Superseded by the owner's decision of 2026-11-13: the brief, without CI, goes on the slice's decision page |
| 4.2 | `invocation_from_entry` refuses entries logged by 4.1's launcher with a clear message, as it refuses earlier ones | 4.2 retires 4.1's prompt layout (the file list from `--path`, empty upstream and evidence sections); its plan did not say so (review round 1, R1-4) |
| 4.5 | Stage B's budget raised from 60 to 85 calls (`BUDGETS`, the key's `budget`): a canary pair for CLI 2.1.323, RC-2's two runs, decision concern 8's measurement (15 runs and one retry), a Sonnet second confirmer (2) and a conditional repeat (4), 83 in all; new spend capped at USD 20. Spent: 76 (57 before, then 2 for the canary pair, 2 for RC-2 and 15 for the measurement, with no retry; the second confirmer and the repeat did not run). The hard stop was then lowered to 76 (`BUDGETS`; the key keeps `budget: 85`, so the runner refused every stage-B run before any call); round 2 raised it to 80 for RC-3 and RC-4 (R2-10), and 80 of 80 are spent (decision concern 11) | The owner approved the measurement beyond the 60 calls ("complete it and do not wait for my approval", 2026-11-13); it needs a canary for CLI 2.1.323, which RC-2's runs share. Lowered to 76 so that the 9 calls left are not spent without approval (decision concern 11) |
| 4.5 | Decision concern 8's measurement was confirmed blind by a fresh session the author started, which never saw the configurations, instead of by the author as S45-D7 says and the owner kept (decision concern 3) | The blinding then does not rest on the author not looking, which was decision concern 3's concern: the author wrote the analysis and the candidate, and the token map sits beside the export. The verdict file keeps the role name `author` in its name (`severity_confirmation_author.jsonl`) |
| 4.5 | The measurement's Sonnet second confirmer (`severity_analysis.md`, section 9; 2 calls) was skipped | Not adopting rests on counts that no verdict changes. Criterion (1), RM-3 and RM-4 detected, fails because `open+list+sev` has no blocking or high finding at either case's expected places (RM-3's three are in `scripts/qa_deploy.py`, RM-4's one in a test plan, and neither case has an absence clause). Criterion (4) counts the blocking or high findings on the no-defect cases CL-1 and CL-2 (3 and 1, against 1 and 1), which needs no match verdict. Only "worse" rather than "not better" rests on one verdict: RM-6's one blocking finding (`S006`, line 424, outside every range), judged not a match |
| Round 2 | R2-1 read for the review loop: a medium finding is handled exactly as a high one. A rejected medium finding stands only when the next round accepts it (or the owner decides); rounds continue until the review ends, which the loop defines once (every blocking, high and medium finding fixed, accepted as rejected, or decided by the owner); after round 4 the blocking, high and medium findings still open go to the owner. The first reading (`0007f65`) kept "rounds continue until no blocking or high finding is open" and added a clause for a medium rejection that waits for its recheck, so the loop stated the end twice and the two disagreed on a medium finding open for another reason; replaced in review round 1 (F2) | R2-1 has medium findings fixed; a medium rejection that stood on the author's word alone would bring back problem 2 for medium findings, and a medium fix a recheck re-raised could end the rounds without a recheck confirming it |
| Round 2 | R2-2's checkable facts are shapes: a harness, static, unit or tooling test ID, a gate as `make <target>` in a code span, or a file and line (`CHECKABLE_FACT`). The check looks at the shape only, not whether the test or line still exists | Review records are frozen while the repository moves on, so an existence check would turn old records red; whether the cited fact holds is the recheck's question, and R2-7 makes it quote the lines |
| Round 2 | R2-3: a later `fixed:` answer settles a re-raised rejection, as a later `owner:` answer already did (decision concern 2); a re-raised low finding may be rejected again | R2-3 ends the argument, not the fix; a low finding stays the author's choice (R2-1) |
| Round 2 | The answer rules live once, in the launcher (`FIXED_SEVERITIES`, `ALLOWED_ANSWERS`, `CHECKABLE_FACT`, `answer_rule_problems` in `scripts/run_independent_review.py`); the launcher refuses before a recheck what `make docs-check` refuses after, and the benchmark uses the same function | R2-1 to R2-3 named only `scripts/check_review_records.py`; two copies could drift, and a recheck whose answers the record check later refuses wastes a reviewer call (discovered issue 26). Moving code, not a new mechanism |
| Round 2 | A finding a recheck accounted `cannot determine` may be answered `fixed:` or `owner:` in the answers to that recheck, under its earlier severity (`UNDETERMINED_ANSWERS`), which settles the rejection | R2-3 sends such a finding to a fix or the owner, but the row for it was refused, so the record could never turn green (discovered issue 24) |
| Round 2 | R2-5's question is in the output section (`MECHANISM_RULES`), not in the mandates; the final review gets none | The output section is shared by every mandate wording, so both recheck wordings and every initial setup get the same question and the benchmark still compares wordings; the final review keeps its open question with no question list (S41-D4) |
| Round 2 | R2-7 applies to every `rejected:` answer a recheck accepts or re-raises, low ones too, as R2-7 is written. A quote counts when its file is one the attempt read with the Read tool, and its text, whitespace aside and the Read tool's line numbers dropped, is within the named lines give or take two (`QUOTE_SLACK`) and holds at least one whole non-blank line of them; when the rejection cites files, at least one of its quotes is from one of them (the last three since review round 1, F3); a failure names the item, the path and the lines, never the quoted text | R2-7 says "every rejection" and "the lines its decision rests on": text known from the prompt, a file the rejection does not cite, or one word near the lines would show neither; the two lines absorb an off-by-one line number without letting a quote from elsewhere pass; leaving the text out keeps anything quoted out of the attempt log |
| Round 2 | R2-9: stage A is not re-scored; a medium finding on a no-defect case counts as a false alarm (upper bounds, by the author's reading, as before); the earlier results are re-scored apart only if the earlier rule reproduces every recorded score (62 of 62) | Stage A's kind `advisory` held medium and low alike, so its medium findings cannot be told apart; S41-D13: whatever rating counts as a detection counts as a false alarm elsewhere |
| Round 2 | R2-9's third export (the 146 findings no earlier export held) was judged by a fresh session the author started, given only a copy of the export and the match rule, not by the author | This does not follow decision concern 3 to the letter: the owner kept the author as the confirmer. As for decision concern 8's measurement (row above), the author wrote the rule being measured and the token map sits beside the export, so a fresh session keeps the blinding from resting on the author not looking. The earlier exports keep the author's verdicts; the owner can say whether this departure stands |
| Round 2 | R2-10: RC-3 and RC-4 are planted on `e842e97`, like RC-1 and RC-2, so their reviewers got that commit's `AGENTS.md`, without R2-4's text | A base with R2-4's text would put the benchmark's own directory and the slice's records, which describe these cases, into the copy; the runner refuses such a copy. R2-5's question reached them through the prompt |
| Round 2 | R2-10's four runs used a pinned install of CLI 2.1.323 in a scratch folder, the version of the fourth canary pair, not the installed 2.1.325 | The installed CLI had updated itself to 2.1.325, which has no canary (S45-D9); a new canary pair would have cost 2 calls beyond the 4 the owner approved (discovered issue 23) |
| Round 2 | The runner's budget check reads the run's `--budget` against the hard stop (80), not the key's `budget` (85) | The author's own instruction kept the key at 85 (decision concern 11 is the owner's) and set the hard stop at 80, which made every run refused before any call (discovered issue 30). A plain `--run`, which takes the key's 85, is still refused, and with 80 of 80 spent every further call is refused |

## Why the benchmark detected fewer than 80%

**Under the rule of the runs** (blocking or high): Detected: `short+list` 6, `open+list` 7, `open-B+list` 6 of 11 defect cases. Seen at any severity: 9, 9 and 8; 9 of
10, 9 of 10 and 8 of 10 when failed or withheld reviews are left out. The misses: 5 seen but rated below high (RM-3
and RM-4 by every setup, each citing its list question; decision concern 8), 3 lost to review mechanics (two empty
reviews, one withheld report), and 4 not found (RM-5 everywhere, RM-6 once). The planted cases were found; the
historical misses DPL-004 and DPL-005 are now seen but not flagged, and DPL-010 is caught by one setup of three. The
full analysis is in the [benchmark report](../poc-4-5-benchmark/benchmark_report.md), section "Why fewer than 80% of
the defects were detected".

**Under R2-9** (round 2, 2026-11-14: a medium finding is fixed, so a match rated medium is detected; the same runs,
re-scored, and the new matches confirmed blind): the misses from rating shrink from 5 to 1 (RM-4 under `open+list`,
rated low); review mechanics (3) and not found (4) do not change, since R2-9 changes ratings, not what a review read or
found. `short+list` detects 9 of 11 (82%, interval 48% to 98%), everything it saw; `open+list` and `open-B+list` 8 of 11
(73%, 39% to 94%). The intervals still neither confirm nor rule out 80%. What remains below 80% is mostly review
mechanics and defects not found, not ratings.

## Decisions made

| When | Decision | The owner's words |
| --- | --- | --- |
| 2026-11-08 | Slice 4 runs as sub-issues: one plan PR, one final PR | "Plan PR, then one final PR" |
| 2026-11-08 | The open mandate is the default; checklists are the minimum | "checklist alone is not completely reliable" |
| 2026-11-08 | Findings get a severity order | "maybe a priority or severity order?" |
| 2026-11-08 | Checklists come from industry research, not only from our own misses | "we have to look or research for industry best practice review checklist" |
| 2026-11-08 | Every review prompt, including the mandate, is researched and measured | "if mandate prompts are going to be used, then it must be analyzed" |
| 2026-11-09 | Research how the industry runs agent-first delivery before planning further | "Maybe we should check first how indusctry approaches agent first Sw delivery" |
| 2026-11-09 | No short-prompt-only setup; compare short prompt + checklist with open mandate + checklist | "I do not want short prompts, it was evident that it produced narrow results" |
| 2026-11-09 | Keep four severity levels; blinded screening benchmark, decided from counts; no model comparison; decision brief on every PR; two candidate gates for slice 6 | "I accept your recommendations for my decisions" |
| 2026-11-09 | Slice 4 is about reviews only; author prompts get their own slice next | "let's continue this slice for just review, after this let's run a new slice of author prompts and benchmark them" |
| 2026-11-09 | Plans merged (PR #48) | merged by the owner |
| 2026-11-09 | This file as the owner's one page; planted defects as the owner's own check | "Yes" |
| 2026-11-09 | The goal above: work without stopping, review once at the end; checklist question per benchmark finding; 4.1's mandate wording kept until the owner chooses; a dry slice at the end instead of a real cycle after 4.3 | "save the revised goal" |
| 2026-11-13 | Add the unit-test decision (5) and the analysis of the benchmark's detections below 80% to this page | "yes, add both to the page and implement your gorwth proposal as well" |
| 2026-11-13 | Growth: proposal 5 replaced by two stricter changes, a rejection is checked against the files it cites and a `searched` list for files only searched; both implemented with proposal 9, the checklist question on each finding | "yes, replace it and implement both with proposal 9" |
| 2026-11-13 | Decision concern 2: keep the implemented reading; a later round's `owner:` answer to the same finding ID settles a rejected blocking or high finding | "DC2 Keep" |
| 2026-11-13 | Decision concern 3: keep the author as the blinded confirmer | "DC3 keep" |
| 2026-11-13 | Decision concern 4: run a second recheck case, with a correct rejection, on both recheck wordings; the author adds, at no extra cost, a correct fix next to the correct rejection in the same case: 2 runs, within the 3 calls left of the 60-call budget. As run: calls 60 and 61, after a canary pair for CLI 2.1.323 (calls 58 and 59), under the budget raised to 85 | "DC4 yes run a second recheck" |
| 2026-11-13 | Decision concern 7: a small slice (four conditions, `AGENTS.md`, Small slices) runs as one PR with the plan review and the implementation review as its units and the final review "none, small slice"; the user merges once; the plan states the conditions and the plan review checks the claim; no tool checks them until a review accepts a wrong "small" claim (the author's choice) | "DC7 yes, smaller slices can have single PR, but needs to define what a smaller slice is"; on the definition: "sound right" |
| 2026-11-13 | Decision concern 8: the three-step analysis of why reviewers rate found defects below the detection threshold: classify the mis-rated findings; one general severity-wording change; measure it on all cases (about 15 reviews and USD 12 beyond the 60-call budget); not the two R5 and C10 blocking conditions alone | "I see it as gap that the reviewers cannot assign the severrity scoring propoerly, just adding these two questions would find this issue, but miss others. Needs further analsis"; on the three steps: "complete it and do not wait for my approval" |
| 2026-11-13 | Decision concern 10: the brief holds no CI result; every slice gets a decision page (this page for slice 4) that holds the brief, the implementation review's answers and every discovered issue; the PR body states the goal and what changed and links the page (the author's resolution: one home per fact) | "DC 10 - I can see the CI job failue or success in PR page, Keep the PR page that explain the goal, changes, and anything everything that needs my attention."; on the proposed PR-body layout: "Wont all these info be available in my decisions page" |
| 2026-11-14 | Round 2 (the section below): blocking, high and medium findings are fixed; a rejection cites a checkable fact; one dispute round; a fix never adds a mechanism; the reviews ask it, see the files fixes changed and quote what a rejection rests on; two recheck cases measure it (4 calls). Replaces decision 6 | "Great, now list all the changes in order, capture it as part of second round of implementation" |

## Round 2: the owner's findings and the fixes (2026-11-14)

After the review of the owner's decisions on the decision concerns, the owner questioned how review severity is
handled now. In the owner's words: "still 6 feels short sighted, it is not clear review severity word change has
any impact and we can direct author to fix blocking and high and meduim and author can reject the low findings, I
do not want to get stuck in a loop where reviewer rate something and autour rejects it or did not challenge the
author rejcetion. I feel like something is missing, what is the general industry practice here?"; then "how do we
avoid the situation where the author starts to fix everything and grows the process or gates unncessarlily, like the
base64 case or PR CI info double commits thing we just avoided?"; "should we make sure every agent review and any
stage get this info? Agent.md is good place, but is this enough?"; "how can we ensure that the reviewer actually
opened the author rejection comment cheked for its fact, evauated and accepted or rejected the fact and not just
accept it?"; and, on the list below: "Great, now list all the changes in order, capture it as part of second round
of implementation". This replaces decision 6 under "Decisions to make".

**The three problems.** (1) The reviewer's severity decides what gets fixed, and severity is the least reliable part
of a review (16 of 39 defects found more than once were rated differently; RM-3 was found by every review and rated
medium, so it could merge unfixed). (2) A dispute can loop, or end with the author's word accepted: the same
reviewer rechecks while reading the author's argument, and LLM judges give in to rebuttals
([`industry_research.md`](industry_research.md), finding 5). (3) A fix can grow the process: a valid finding is
silenced with a new mechanism instead of a change to its cause (DPL-007's base64 scan, 4.6's brief pasted again
after CI, the budget raised to 85); the rule against it is in `AGENTS.md`, but nothing asks it when a fix is written
or judged.

**Industry practice it follows.** Fix by default, and let only explicitly optional comments be skipped (Google's
"Nit", "Optional", "FYI"; Conventional Comments' blocking and non-blocking); settle a disagreement with facts, then
by a third party, and do not let a change sit ("Technical facts and data overrule opinions and personal
preferences"; escalate to a lead or maintainer); someone other than the author verifies the rework (the Fagan and
IEEE 1028 moderator); correcting a defect and preventing its recurrence are separate decisions (8D's D5–D6 against
D7); put the question where the action happens (a checklist at the pause point), not only in the manual.

**The changes, in the order they are built:**

| # | Change | Solves | Where |
| --- | --- | --- | --- |
| R2-1 | Blocking, high and medium findings are fixed; only a low finding is the author's choice. A medium finding is no longer deferred to an issue unless the owner decides it (`owner:`). Severity stays as the measure of how serious a finding is, and a blocking finding still holds the merge | 1 | `AGENTS.md` (Review findings, Review loop); `scripts/check_review_records.py` (the answers each severity allows) |
| R2-2 | A rejection of a blocking, high or medium finding cites at least one checkable fact: a test ID, a gate, or a file and line. A rejection that cites none is refused by `make docs-check` | 2 | `AGENTS.md` (Review loop); `scripts/check_review_records.py` |
| R2-3 | One dispute round: a rejection the recheck does not accept goes to the owner (`owner:`) or is fixed; there is no second round of argument | 2 | `AGENTS.md` (Review loop); `scripts/check_review_records.py` |
| R2-4 | A fix corrects the defect or changes the choice that caused it, and never adds a mechanism (a gate, check, CI job, process step, document, register or field). A finding that only a new or wider mechanism would answer goes to the owner as `owner:` with a one-line proposal: the failure it catches, its cost, the simpler alternative weighed | 3 | `AGENTS.md` (Fixes stay within the agreed decisions; Review loop) |
| R2-5 | The review instructions ask it at the pause point: the recheck, for each `fixed:` answer, whether the fix adds a mechanism without the owner's approval where changing a choice would do (re-raise it if so); the initial review the same of the change itself. An instruction-wording change, in its own commit (decision 2) | 3 | `scripts/run_independent_review.py` (mandates, output section) |
| R2-6 | A recheck's evidence lists each rulebook, gate, CI, template, checklist or launcher file that the commits since the reviewed round changed, with its line counts; the recheck accounts for each as explained or flagged | 3 | `scripts/run_independent_review.py`, `scripts/review_inputs.py` |
| R2-7 | For every rejection it accepts or re-raises, the recheck quotes the lines its decision rests on, with file and line; the launcher fails a recheck whose quote is not at that place in the copy. (The launcher already fails a recheck that did not read a cited file) | 2 | `scripts/run_independent_review.py` (report schema, answer checks) |
| R2-8 | The decision brief lists medium findings answered `rejected` too, beside blocking and high ones, so the owner sees every accepted rejection | 2 | `scripts/review_brief.py` |
| R2-9 | The benchmark counts a match rated blocking, high or medium as detected (the existing results re-scored, no reviewer call): with R2-1 a medium finding is fixed, so it is caught | 1 | `scripts/run_review_benchmark.py`, `tests/review_benchmark/answer_key.yaml`, the benchmark report |
| R2-10 | Two recheck cases, run on both recheck wordings after R2-5 and R2-7 (4 reviewer calls; the stage-B hard stop raised from 76 to 80): RC-3, a `fixed:` answer that adds a mechanism where changing a choice would do (a good recheck re-raises it), and RC-4, a false rejection that cites a real test which does not cover the scenario (a good recheck re-raises it). With RC-2, a rejection that holds, they show whether a recheck tells a true fact from a false one | 2, 3 | `tests/review_benchmark/`, the runner, the benchmark report |
| R2-11 | Records: this section; decision 6 replaced; the implementation log, `docs/STATUS.md`; one review unit, `round-2`, at high effort, with its recheck | all | this page, `docs/history/implementation_log.md`, `docs/STATUS.md` |

**Not in round 2.** Running the fact itself (the launcher runs the test a rejection cites on the author's scenario
patch) waits for RC-4's result; the authors' own pause-point check goes to the author-prompts slice; decision 7 (a
Blocks bullet for a false "small" claim), decision concern 11 (the budget) and growth proposal 12 (resuming a review
that failed the read check) stay open. The four severity levels, the stage lists and the gates and CI jobs do not
change, and no gate is added.

**As built: the answer rules** (R2-1 to R2-4 and R2-8; `8a82388`, `5e62097`, `83eabdf`, `0007f65`). `AGENTS.md`
(Review findings, Review loop, Fixes stay within the agreed decisions) now says: blocking, high and medium findings are
fixed and take `fixed:`, `rejected:` or `owner:`; only a low finding may be `deferred:`; a rejection of a blocking,
high or medium finding cites a checkable fact (a test ID, a gate as `make <target>` in a code span, or a file and line)
and stands only when the next round accepts it; the review loop handles a medium finding as a high one, so rounds
continue until the review ends, which it defines once (review round 1, F2); the recheck is the one dispute round, so a
rejection it re-raises or cannot determine is fixed or goes `owner:`, never `rejected:` again; a fix corrects the
defect or changes its cause and adds no mechanism (rule text only). `make docs-check` refuses the answers these rules
refuse, and the brief lists medium rejections beside blocking and high ones. A probe of every record the check reads (23 attempts, 107 answer
rows) found none that the new rules refuse, so no transition rule was added. Proved by
`test_each_answer_the_rules_do_not_allow_fails`,
`test_a_rejection_of_a_blocking_high_or_medium_finding_that_cites_no_checkable_fact_fails`,
`test_a_re_raised_rejection_answered_rejected_again_fails` (`tests/tools/test_check_review_records.py`) and
`test_the_brief_lists_every_item_the_owner_must_see` (`tests/tools/test_review_brief.py`).

**As built: the review prompt and the recheck** (R2-5 to R2-7; `67b0402`, `f884421`, `a549e19`, `7b524b2`, `6e88d19`,
`f8f19c5`). The answer rules live once, in `scripts/run_independent_review.py`, and the launcher refuses before a
recheck what `make docs-check` refuses after. The output section, which every mandate wording shares, asks an initial
review whether the change adds a mechanism without the owner's approval where changing a choice would do, and a
recheck the same of each `fixed:` answer, to re-raise it if so; the final review keeps its open question. That wording
is its own commit, `7b524b2` (decision 2). A recheck's evidence lists each process file (`PROCESS_FILES` in
`scripts/review_inputs.py`: the rulebook, the gates and their QA tooling, CI, the templates, the checklists, the
launcher and the brief) that the commits since the reviewed round changed, with its line counts. A recheck quotes the
lines each rejection it accepts or re-raises rests on (`quotes`: file, lines, text), and the launcher fails it when a
quote is missing, not from a file it read, not at its place in the copy or without a whole line of it, or when none of
a rejection's quotes is from a file the rejection cites (the last three since review round 1, F3). A finding a recheck
could not determine can now be answered (discovered issue 24). Proved by
`test_answers_the_record_check_would_refuse_are_refused_before_the_recheck`,
`test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism`,
`test_a_recheck_accounts_for_each_process_file_changed_since_the_reviewed_round`,
`test_every_rejection_the_recheck_accepts_or_re_raises_is_quoted`, `test_a_quote_counts_only_at_its_place_in_the_copy`,
`test_a_quote_comes_from_a_file_the_recheck_read_and_one_the_rejection_cites`,
`test_a_quote_holds_at_least_one_whole_line_of_its_place` (`tests/tools/test_run_independent_review.py`) and
`test_a_finding_the_recheck_could_not_determine_is_answered_fixed_or_owner_in_the_next_answers`
(`tests/tools/test_check_review_records.py`).

**As built: the benchmark** (R2-9 and R2-10; `294d85b`, `ff276bc`, `e4943aa`, `7fd4723`, `c79ed96`). The answer key's
version 5 counts a match rated medium as detected, and a medium finding on a no-defect case as a false alarm.
`--rescore B` re-scores the earlier results apart and writes nothing unless the earlier rule reproduces every recorded
score (62 of 62 do). A third export of the 146 findings no earlier export held was judged blind by a fresh session: 15
match. Version 6 adds RC-3 and RC-4, committed before their runs, which ran on both recheck wordings as calls 77 to 80
of the hard stop of 80, all four at the first try. Proved by
`test_rescore_b_writes_nothing_when_a_recorded_score_is_not_the_earlier_rules`,
`test_the_third_export_holds_only_findings_no_earlier_export_holds_and_confirms_a_medium_match` and
`test_each_recheck_of_a_false_answer_is_reported_detected_or_missed` (`tests/tools/test_run_review_benchmark.py`); the
counts are in decision 2 below and in the [report](../poc-4-5-benchmark/benchmark_report.md#counts).

**RC-1 to RC-4, read together** (one run per case and wording). Both wordings caught the false answers that the files
refute: RC-1's false fix and RC-4's false rejection (it cites a real test whose fixture holds no code span), each
re-raised under its ID, RC-4's at blocking with the lines quoted. Neither caught a fix that works but grows the process:
on RC-3 (a step added, the summary written after CI and again after every push, where leaving the CI result out would
do) both accepted the fix, each noting that it changes when a step happens and adds no gate or job; `recheck-A` named
the simpler choice, a link to the head's checks, but as a low simpler alternative, and both filed the stale window
between a push and the end of CI as a new finding (decision concern 13). On answers that hold (RC-2) `recheck-B`
accepted both and `recheck-A` failed the read check. These runs give no rate, and RC-3 and RC-4 cannot show what R2-5
or R2-7 changed: they have no run without them, and RC-1 and RC-2 ran before them, with other prompts (RC-1 also
under another CLI version).

**Still not in round 2, after its runs.** Running the fact itself is not proposed: RC-4's false rejection was re-raised
by both wordings (one run each). The authors' own pause-point check still goes to the author-prompts slice. Open for
the owner: decision 7, decision concern 11 and growth proposal 12, and from round 2 decision concern 13 (the RC-3
wording), growth proposal 14 (the plan list's question 8) and decision concern 15 (the process files). The four
severity levels, the stage lists, the gates and the CI jobs did not change, and no gate was added.

## Decisions to make

| # | Decision | When | Options | Recommendation |
| --- | --- | --- | --- | --- |
| 1 | The evidence secret check: a credential value must look like a token (20 characters or more, or a digit), and values in code spans and quotes are found | At the end; already in effect since #48 | Keep; change | Keep: every credential here looks like a token, and CI's full E2E run passed |
| 2 | Default review setup and mandate wordings (initial, recheck, final) | At the end | From the [benchmark's counts](../poc-4-5-benchmark/benchmark_report.md#counts). Under the rule of the runs (blocking or high): detections `short+list` 6, `open+list` 7, `open-B+list` 6 of 11; false alarms 2 (in 4 no-defect reviews), 2 (4) and 4 (2). Under R2-9 (blocking, high or medium): detections 9, 8 and 8 of 11; false alarms 4 (4), 7 (4) and 6 (2), upper bounds. Rechecks of false answers, under R2-9: both wordings 2 of 3 (RC-1's false fix and RC-4's false rejection re-raised, RC-3's fix that adds a step accepted); on answers that hold (RC-2) `recheck-B` passed, `recheck-A` failed the read check | Keep `open+list` and 4.1's initial wording: no setup is shown better under either rule. Under R2-9 `short+list` detects one case more and raises the fewest false alarms, but one case apart is within chance and the intervals overlap almost entirely, so the counts give no reason to leave the open mandate the owner made the default (2026-11-08); the draft still raises the most false alarms per no-defect review (6 in 2). For the recheck, still lean to the draft (`recheck-B`): the wordings did the same on RC-1, RC-3 and RC-4, and only the draft passed RC-2, where 4.1's failed the read check, as four real rechecks did; one run each, so this is a default, not a finding |
| 3 | Recreate the hidden issues under the owner's account if GitHub has not answered | At the end, or about 2026-11-23 if the owner is around | Recreate the open ones; keep waiting | Recreate the open ones |
| 4 | Remove your personal copy of the grill-me skill. A personal skill takes precedence over a project skill of the same name, so while it exists, discovery runs the old text, which cuts off two sentences and never asks the assets question, instead of the repository's (4.6 review, F4) | Before the next slice's discovery | Remove it; rename one of them | Remove it: the repository copy is the reviewed one |
| 5 | Measure the `unit-tests` list, which no benchmark case used, nor the tests-first pair with `e2e-tests` (discovered issue 15) | Before relying on the list, or in slice 8 | Add one or two unit-test cases now (about 6 calls; S45-D5's cases and the 60-call budget change, 3 calls are left); or measure it in slice 8 | Slice 8, which measures the lists' own effect against reviews without them |
| 6 | Replaced on 2026-11-14 by round 2 (the section above): what to do about review severity now | — | — | Decided: R2-1 to R2-11 |
| 7 | How the plan review checks a "small slice" claim. Since decision concern 7, a slice that meets four conditions (`AGENTS.md`, Small slices: no requirement or trace change, nothing that checks everyone else, no security decision path, about 50 lines in 5 files) is one PR without a final review. Only the plan review checks that the claim is true, and its list, `docs/review_checklists/plan-and-test-plan.md` (12 questions, the limit of S44-D3), asks nothing about it. A list item needs the owner's approval (`AGENTS.md`, Stage checklists), so the author has not changed the list (review of the owner's decisions, F2) | Before the first small slice | (a) Add a bullet to the list's "Blocks at this stage": "a plan that claims a small slice while one of the four conditions of `AGENTS.md` (Small slices) does not hold for the planned change"; (b) add it as a 13th question, past the limit of 12; (c) leave it to the open mandate and `AGENTS.md` | (a): the question limit stays, and a false "small" claim skips the final review, so it should block, not only be asked. Until the owner decides, the open mandate and `AGENTS.md` are the only check |

## Parked units, decision concerns and growth proposals

| # | Kind | Part | Item | The author's recommendation |
| --- | --- | --- | --- | --- |
| 1 | Decision concern, resolved | 4.1 | S41-D8 made a recheck read only the files a `fixed:` answer names, so a `rejected:` answer resting on a file could be accepted without opening it (4.1 review round 1, R1-5) | Resolved by the owner on 2026-11-13: the launcher now also requires every file a `rejected:` answer cites to be read |
| 2 | Decision concern, resolved | 4.3 | S43-D3 fails a record whose answers changed after a recheck read them, and S43-D4 settles a rejected blocking or high finding only by the next round's acceptance or an `owner:` link. Read narrowly, a rejection the recheck re-raised could never be decided by the owner without editing answers the recheck read, and `make docs-check` would stay red (4.3 review round 1, R1-3). The check is also red between the answers commit and the recheck, by design | Resolved by the owner on 2026-11-13: the implemented reading is kept, a later round's `owner:` answer to the same finding ID settles it |
| 3 | Decision concern, resolved | 4.5 | S45-D7 makes the author the blinded confirmer, so the blinding rests on the author not looking: the token map and the results with their configurations sit in the same folder as the export (4.5a review round 1, L4) | Resolved by the owner on 2026-11-13: kept; the author stays the blinded confirmer |
| 4 | Decision concern, decided, in progress | 4.5 | S45-D5 has one recheck case, RC-1, whose answer is a false `fixed:`. It measures whether a recheck wording accepts a false fix, not whether it re-raises answers that hold (a correct rejection, a correct fix), so a wording that re-raises everything would score best (4.4 critique, C-2) | Decided by the owner on 2026-11-13: run a second recheck case with a correct rejection, and a correct fix beside it, on both wordings. Done: RC-2 (a test-lint change; the earlier report's R1-1 is wrong, R1-2 fixed) ran on both wordings under CLI 2.1.323, after a canary for that version (the budget raised to 85, see the author's decisions). `recheck-B` accepted both answers and raised nothing; `recheck-A` failed the launcher's read check (`opened` named the harness, which the rejection cites and the review never read), a miss, the failure that also stopped four of this slice's real rechecks. With RC-1, the draft passed both recheck cases and 4.1's one; one run each, so no rate ([report](../poc-4-5-benchmark/benchmark_report.md#counts)). Round 2 (R2-10, 2026-11-14) added two recheck cases of false answers, run on both wordings: RC-4, a false rejection citing a real test that does not cover the scenario, re-raised by both (detected); RC-3, a fix that adds a step where leaving the CI result out would do, accepted by both (missed; decision concern 13) |
| 6 | Decision concern, withdrawn | 4.5 | S45-D9's valid canary seemed impossible: two twins declined the planted `CLAUDE.md`. The cause was the canary prompt, built by the author from the review prompt (report review, B2); with its own prompt the third canary was valid and passed | Nothing to decide |
| 7 | Decision concern, resolved | 4.6 | S46-D1 and S46-D5 give every slice a plan PR the user merges, a plan review, an implementation review and a final review, so a one-line fix costs three review units and two merges (about USD 6 to 9 at the plan's estimates) unless the plan records a rule deviation with the user's words (4.6 review, F5) | Resolved by the owner on 2026-11-13: a small slice, by four conditions, is one PR holding the plan and the change, with the plan review and the implementation review as its units and the final review "none, small slice". Done: `AGENTS.md` (slice workflow, Small slices, Discovery, Final review), the plan template's Small slice part; `test_the_plan_template_check_fails_on_each_missing_part` |
| 8 | Decision concern, decided, done | 4.4 | The benchmark's misses RM-3 (requirements without proof) and RM-4 (a gate inside another CI job) were found by every review, each citing the list question that asks it (R5, C10), and rated medium or low, which the rule does not count as a detection. The lists' "Blocks at this stage" sections do not name these cases, so the reviewers' severities follow the rules | Decided by the owner on 2026-11-13: not the two blocking conditions alone, but the three-step analysis: classify the mis-rated findings, one general severity-wording change, measured on all cases (about 15 reviews, USD 12 beyond the 60-call budget), without waiting for the owner's approval. Done: the [analysis](../poc-4-5-benchmark/severity_analysis.md) found that reviewers rate a scenario's first symptom, under base rules that often supported the low rating; its candidate 1, "finish the scenario", ran on the 15 cases (USD 13.03) and was judged blind against criteria fixed before the runs: worse. RM-3 and RM-4 stayed medium, RM-6 was lost, CL-1 drew two extra blocking or high findings; 7 of 11 detected in both setups. Nothing is adopted: the launcher and `AGENTS.md` stay as they are ([report](../poc-4-5-benchmark/benchmark_report.md#severity-decision-concern-8)). What to do instead was decision 6, which round 2 replaced (2026-11-14): medium findings are fixed (R2-1), and the benchmark counts a medium match (R2-9). Under R2-9 the measurement's outcome stays worse, now by RM-6 lost alone: `open+list` 8 of 11, `open+list+sev` 9 of 11 (RM-3 and RM-4 at medium), and CL-1 and CL-2 together draw 7 findings against 6; read after the fact, since the criteria were fixed for the earlier rule |
| 10 | Decision concern, resolved | 4.6 | S46-D9 and S46-D13: the brief opens the PR body, which is a snapshot not updated later; CI runs on pull requests, so a brief pasted when the PR is opened always says "no run for this commit; not a pass" (4.6 review, F3) | Resolved by the owner on 2026-11-13: the brief holds no CI result, which the owner sees on the PR page; the brief, the review answers and the discovered issues go on the slice's decision page, which the PR body links. Done: `scripts/review_brief.py` (the CI line removed), `AGENTS.md` (Start here, Discovered issues, the stage table, Discovery, Handoff, Stage checklists, Implementation review), `docs/slices/_template/decisions.md`; `test_the_brief_holds_no_ci_result_and_reads_no_network`, `test_the_decision_page_template_has_every_section_the_owner_asked_for` |
| 9 | Growth, approved and implemented | 4.5 | A finding may name the checklist question that prompted it (`question`, for example `code:10`); the benchmark report counts the findings that do. Approved by the owner on 2026-11-13 | Done: the launcher's schema and output section, `AGENTS.md` (Stage checklists), the benchmark report; the benchmark's runs predate the field |
| 5 | Growth, replaced and implemented | 4.1 | The first proposal, to drop unread files from `opened` instead of failing, was withdrawn: of the four failed reviews it would have passed one whose five acceptances rested on files the reviewer never read. In its place, approved by the owner on 2026-11-13: a recheck must read every file a `rejected:` answer cites, as it must for a `fixed:` answer; and a reviewer lists files it only searched under `searched`, so `opened` stays a claim the launcher checks | Done: the launcher's schema, output section and answer checks, `AGENTS.md` (Modes and prompts) |
| 11 | Decision concern, open | 4.5 | The author raised S45-D1's stage-B budget from 60 to 85 calls under the owner's approval of decision concern 8's measurement ("complete it and do not wait for my approval"), which named about 15 reviews, not a call count; 76 were spent (57 before, then 2 for the canary pair under CLI 2.1.323, 2 for RC-2 and 15 for the measurement). At 85 the runner would have spent the 9 calls left without approval, so the hard stop was lowered to 76: `BUDGETS` in `scripts/run_review_benchmark.py`, while the key keeps `budget: 85` (review of the owner's decisions, F6). Round 2 (R2-10, approved by the owner on 2026-11-14) raised the hard stop to 80 for RC-3's and RC-4's 4 runs: 80 of 80 are spent. The key still says 85. The runner had checked the key's budget against the hard stop, so the author's instruction (key at 85, hard stop 80) refused every run; it now checks the run's `--budget` instead. A plain `--run`, which takes the key's 85, is still refused, and with 80 of 80 spent every further stage-B call is refused | Confirm the raise to 85 and the 80 spent; a further stage-B call needs a new decision |
| 12 | Growth, proposed, not implemented | 4.1 | On a read-check failure (a file under `opened` that the review did not read), the launcher resumes the same reviewer session once, names the files it listed as opened but did not read, and asks it to read them or move them to `searched`. The check stays as strict, and a failure stops costing a whole session: eight so far (discovered issues 21 and 22) | The owner decides |
| 13 | Decision concern, open | Round 2 | RC-3 was accepted by both recheck wordings, although R2-5's question asks of each `fixed:` answer whether it adds a mechanism. Both judged that the fix changes when a step happens and adds no gate or job (`recheck-B`: "The fix changes when the step happens instead of adding a gate, job or other mechanism"), so a step written again after every push did not read as an added process step; `recheck-A` named the simpler choice, a link to the head's checks, but filed it as a simpler alternative, which the output section says is "always low". A wording that says a fix which adds or repeats a step, or keeps a second copy of a fact current, adds a mechanism, and that such a fix is re-raised at the finding's severity, not reported as a simpler alternative, would close both outlets. It is a wording change (decision 2), and measuring it needs RC-3 runs beyond the 80 calls (2 calls, one per wording) | The author drafts the wording; the owner decides whether to adopt it and whether to spend 2 calls measuring it |
| 14 | Growth, proposed, not implemented | Round 2 | Question 8 of `docs/review_checklists/plan-and-test-plan.md` still asks the rule before R2-4: "Where a fix answers a review finding, does it change the upstream choice that caused it before adding a mechanism?" Since R2-4, a fix adds no mechanism at all. No other list states the old rule (the code list's question 9 asks that duplicate mechanisms be removed, which still holds). A list change needs the owner (`AGENTS.md`, Stage checklists) | Change question 8 to: "Where a fix answers a review finding, does it correct the defect or change the choice that caused it, without adding a mechanism?" The question count stays 12 |
| 15 | Decision concern, open | Round 2 | R2-6's process files follow R2-6's words (the rulebook, gates, CI, templates, checklists, the launcher), so `PROCESS_FILES` leaves out the benchmark runner and its answer key, `.claude/skills/` and `security/invariants.yaml`. R2-6 would therefore not have shown problem 3's own example, the budget raised to 85 in the runner and the key | Add the benchmark runner, its key and the skills folder to `PROCESS_FILES` (one line). `security/invariants.yaml` is the register of the system under test, not of the delivery process, so this recommendation leaves it out |

DC 8 status, 2026-11-13, updated the same day after the analysis: the owner said, "DC8 needs further analysis." The analysis and one measurement are done ([`severity_analysis.md`](../poc-4-5-benchmark/severity_analysis.md); [benchmark report](../poc-4-5-benchmark/benchmark_report.md), "Severity: decision concern 8"). The answer to the question is both. The rules and the inputs explain the systematic part: in 6 of the 7 findings that saw a defect but rated it medium or low, the rules that case's reviewer received (its base commit's `AGENTS.md`) supported that rating, and each stage list's "Blocks at this stage" is narrower than the question that found the defect. Reviewer judgement explains the noise: 16 of the 39 defects that several reviews found got different severities, and in 2 of 3 repeated identical runs the severity changed. One general wording change ("finish the scenario": rate the end of the failure scenario, not its first symptom) was measured on all 15 initial-review cases and made things worse (RM-3 and RM-4 still missed, RM-6 lost, more false alarms on a no-defect case), so it is not adopted. The launcher still validates severity labels and structure only, not whether a severity is justified. The R5/C10 blocking conditions are still not approved and not implemented. What to do next was decision 6; on 2026-11-14 round 2 replaced it (section "Round 2" above): a medium finding is now fixed (R2-1), so a defect seen at medium, as RM-3 was by every review, is fixed without a blocking condition, and under R2-9 the measurement is still worse, by RM-6 lost alone.

No unit is parked.

## Discovered issues

| # | Issue | Found | Disposition |
| --- | --- | --- | --- |
| 1 | shellcheck is not installed locally, so 9 tests of `tests/tools/test_lint_changed_files.py` fail in a local `make tooling-test`, also on the base | 4.1, by the author | Outside the threat model (local environment); worked around with a scratch binary; CI has shellcheck |
| 2 | Stage A's benchmark prompts (`tests/review_benchmark/prompts/short.md`, `checklist.md`) still tell the reviewer to use the kinds "blocking" and "advisory", which the new schema rejects | 4.1 review round 1, R1-3 | Fixed in 4.5a: stage B's `short+list` uses `tests/review_benchmark/prompts/short_list.md`, the short prompt without that sentence; stage A's files stay as measured |
| 3 | The launcher computed the start entry's mandate hash apart from the prompt; the two could differ | 4.1, by the author's tests | Fixed in 4.1 before its first commit (`59d0291`): both come from one configuration object |
| 4 | Headings in quoted text could pass for the prompt's own sections | 4.1, by a dry run on this repository's prose | Fixed in 4.1 (`6476697`) |
| 5 | The first live recheck (4.1, round 2, attempt 1) listed files it had only grepped under `opened`, and accepted the decision-file fix without opening the file; the launcher failed the attempt, as S41-D8 intends. The prompt had said only "the files you read" | 4.1 review round 2 | Fixed in 4.1: the output section now says that only a Read opens a file, and that the launcher fails the report otherwise; round 2 runs again |
| 6 | The first launcher-written review attempt (4.3, round 1, attempt 1) failed the schema check after 8 minutes and about USD 2.75, and the log said only "does not match the report schema" | 4.3 review round 1 | Fixed in 4.3: the reason names the schema problems; one likely cause, a `flagged` note ending a finding ID with a full stop, is accepted now; round 1 ran again |
| 7 | The 4.5a recheck (round 2, attempt 1) again listed files under `opened` that it had not read with the Read tool (for B1, L1 and EV6), and did not read `docs/slices/README.md`, which a `fixed:` answer names; the launcher failed it, as S41-D8 intends, after a full medium-effort session. Attempt 2 ran on the next commit, which also holds 4.4, so its paths under review held 4.4's files too | 4.5a review round 2 | Kept as found: the read check did its job and the prompt's rule (only a Read opens a file) already says this. If it recurs, the growth proposal is to show the reviewer, before it answers, which named files it has not read |
| 8 | The 4.4 critique's Sonnet reviewer (attempt 1) named a file under `opened` for EV7 that it had not read; the launcher failed it. The third such failure | 4.4 critique | Rerun as attempt 2, which completed; growth proposal 5 in the table above |
| 9 | The author's self-review for 4.4 said the benchmark's dry run built every prompt with the lists; that dry run ran while the key's `lists_commit` was empty, so the +list prompts held no list, and the dry run, unlike a run, did not refuse it | 4.4 implementation review, F3 | Fixed: the dry run refuses as a run does; the dry run with `04f8df4` was checked to put each list in its prompts. A false claim caught by the review before merge |
| 10 | The grill-me skill in the owner's user folder has two lines cut off mid-sentence (they end in `>`) and does not ask which keys, sockets and secrets a slice touches, although `AGENTS.md` said it always does | 4.6, by the author when moving it in | Fixed in the repository copy; the user-level copy is the owner's |
| 11 | The owner's addition, that each benchmark finding names the checklist question that prompted it, was not built into 4.5a: the report schema has no such field. The benchmark report gives the question from the finding's own text where it cites one (4 of 29 confirmed detections) and the author's mapping otherwise, marked as such | 4.5b, by the author when writing the report | Recorded; growth proposal 9 |
| 12 | The canary was built on the review prompt, whose data clause made a valid twin impossible; the author blamed S45-D9 and loosened the gate before fixing the prompt | 4.5b report review, B2 | Fixed: the canary's own prompt, a valid canary, the gate restored |
| 13 | The runner's repeat line read automatic scores, so the report said RM-6 was detected twice | 4.5b report review, B1 | Fixed: the repeats and the rating agreement read the confirmed verdicts |
| 14 | The 4.5b report recheck (round 2, attempt 1) named a file under `opened` for EV4 that it had not read; the launcher failed it. The fourth such failure | 4.5b report review round 2 | Rerun as attempt 2; growth proposal 5 |
| 15 | The benchmark never gave a reviewer the `unit-tests` list, nor the tests-first pair of `unit-tests` and `e2e-tests`: the author's artifact types (4.5a) gave no case a unit-test change, and each case one list | The owner's question, 2026-11-11 | Recorded in the [benchmark report](../poc-4-5-benchmark/benchmark_report.md) ("By stage list"). Measuring it needs one or two unit-test cases, which changes S45-D5's cases and the 60-call budget (3 calls left): the owner's decision; logged in DPL-012 |
| 16 | The author's growth proposal 5 would have stopped failing a review whose `opened` names a file it did not read, argued from the four sessions the rule cost; one of the four had accepted five answers on files it never read, which the proposal would have passed | The owner's question, 2026-11-13 | Withdrawn and replaced by stricter changes the owner approved; logged in DPL-012 |
| 17 | The growth recheck (round 2, attempt 1), the first live review with `searched`, accepted the fix of G1-3 without reading the file the fix names (`benchmark_report.md`); the launcher failed it | Growth review round 2 | The strict check worked as the owner decided on 2026-11-13; rerun as attempt 2 |
| 18 | The benchmark's historical cases get the rules of their base commit, so a rule change in `AGENTS.md` cannot reach them; RM-1, RM-2 and CL-3 got no rules at all | Decision concern 8, step 1 | By design (each case is reviewed as it was); the measurement says so, and slice 8 should give today's rules where it measures today's process |
| 19 | The benchmark's "false blockers" metric counts blocking findings outside the planted defects, and they are mostly real defects: all 20 of the first runs' were real, 8 of them over-rated | Decision concern 8, step 1 | The report says so beside the metric; the metric's name is kept |
| 20 | The CLI updated itself mid-benchmark, from 2.1.321 to 2.1.323, so the runner refused every review until a new canary ran, and the old canary counted as done for the new CLI | RC-2's run | Fixed: a canary is now done per CLI version; a new pair under 2.1.323 is valid and passed, within the budget raised to 85 |
| 21 | The review of the owner's decisions (unit `owner-decisions`, round 1, attempt 1) failed the launcher's read check: its report named a file under `opened` for EV2 that it did not read. The seventh such failure, counting RC-2's `recheck-A` | Review of the owner's decisions, round 1 | Rerun as attempt 2, which completed; growth proposal 12 |
| 22 | The recheck of the owner's decisions (unit `owner-decisions`, round 2, attempt 1) failed the read check too: its report named files under `opened` for F4, F6 and F8 that it did not read, and it did not read `docs/STATUS.md` and `tests/tools/test_run_review_benchmark.py`, which `fixed:` or `rejected:` answers name. The eighth such failure | Review of the owner's decisions, round 2 | Rerun as attempt 2, which accepted all 8 answers; growth proposal 12 |
| 23 | The CLI updated itself again, from 2.1.323 to 2.1.325, before RC-3's and RC-4's runs; no canary has run for 2.1.325, so the runner would refuse every review | R2-10's runs, by the author | Worked around: the four runs used a pinned install of 2.1.323 in a scratch folder, the version of the fourth canary pair, instead of a new pair (2 calls the owner did not approve). A later benchmark run needs that pin or a new canary |
| 24 | A finding a recheck accounted `cannot determine` is not among its findings, so the answer row that fixes it or sends it to the owner was refused as a row for an unknown ID, and the earlier rejection could never be settled: the record could never turn green. In the rules since S43-D4 | R2-3's implementation, by the author | Fixed in `f884421` (`UNDETERMINED_ANSWERS`); `test_a_finding_the_recheck_could_not_determine_is_answered_fixed_or_owner_in_the_next_answers` |
| 25 | The answers to a recheck whose report held no finding were not checked, so an `owner:` row without a link could settle a rejection | R2-3's implementation, by the author | Fixed in `f884421`; `test_the_answers_to_a_recheck_without_findings_are_checked_too` |
| 26 | The launcher refused before a recheck less than `make docs-check` refuses after: answers the record check would fail (for example a rejection without a checkable fact) reached the reviewer, and the record turned red only after the call | R2-1 to R2-3's implementation, by the author | Fixed in `f884421`: one home for the answer rules, `answer_rule_problems` in the launcher; `test_answers_the_record_check_would_refuse_are_refused_before_the_recheck` |
| 27 | `AGENTS.md`'s plan-review rule "from round 2 a new finding counts only if it is blocking or high" sits beside R2-1, which has medium findings fixed | The author, reading the rulebook against R2-1 | Kept: it limits which new findings a plan recheck raises; a medium finding a recheck does report is fixed under R2-1 |
| 28 | The benchmark's leak search scans the rules, the upstream items, the task, the prompts and the copy, but not a recheck case's earlier report and answers | R2-10's cases, by the author | Recorded. Checked by hand for RC-3 and RC-4: the earlier report and the answers section the reviewer gets hold none of their leak terms (RC-3's answers file names one in its header, which the reviewer does not get). Widening the search is a mechanism (R2-4), so it is not added; it is the owner's if more recheck cases are written |
| 29 | Running an earlier export again would now include its medium findings and shuffle new tokens, which would break the joins with the verdicts already recorded | R2-9's implementation, by the author | Recorded: earlier exports are not run again; the third export (`--export-rescore`) holds only the findings no earlier export held |
| 30 | The author's instruction for R2-10, the key's budget kept at 85 and the hard stop set at 80, contradicted the runner's check that the key's budget is within the hard stop, so every run was refused before any call | R2-10's implementation, by the author | Recorded with the changed check (`ff276bc`): the runner checks the run's `--budget`; `test_a_run_within_the_hard_stop_runs_though_the_keys_budget_is_above_it`; decision concern 11 |
| 31 | Between the third export and its verdicts, a detection whose matching findings had tokens but no verdict counted as neither confirmed nor not yet confirmed, so the report showed it as a miss with nothing waiting | R2-9's report, by the author | Fixed in `7fd4723`: a token without a verdict counts as not yet confirmed |
| 32 | RC-3: both recheck wordings accepted a fix that adds a step where changing a choice would do, although R2-5's question asks it | R2-10's runs | Decision concern 13 |
| 33 | `AGENTS.md`'s stage table still makes "no blocking or high finding open" each review's exit, while the review loop now also continues while a rejected medium finding waits for its recheck (`0007f65`) | The author, writing round 2's records | Fixed before the review (`eb46b58`): each exit cell, and the small slice's plan review, now says the review has ended, and the sentence above the table points to the review loop. The loop itself still stated the end twice (review round 1, F2); since that fix it defines the end once |

## The dry slice

One dry slice ran from a clean session (a fresh subagent, in a scratch clone of this branch, with pushes disabled
and at most two Sonnet review calls): a one-sentence `README.md` change through the seven stages. It made 2 review
calls (the plan review completed with one low finding; the implementation review failed the empty-review rule) and
ran every check it could without Docker. What the next user would trip on, with the disposition of each:

| # | Trip point | Disposition |
| --- | --- | --- |
| 1 | The seven stages and the lists exist only on this unmerged branch, and the launcher fetches its base from GitHub, so no review can run with a stage list until slice 4 merges; the dry slice's reviews got the old rules, no list, and all of slice 4's files | Ends when slice 4 merges; nothing to change |
| 2 | Branch names: `poc/slice-<n>-<topic>` has no `<n>` for a slice named by topic | Open: the owner's naming choice |
| 3 | `--base` takes `poc/agentic-sdlc` in the launcher and `origin/poc/agentic-sdlc` in the brief and the Makefile; the launcher's options have no help text | Open, low |
| 4 | No home for a review's task prompt file | Open, low: the launcher copies it into the record, so its file is a draft |
| 5 | The plan template had no threat-model section, although the plan review needs one; a decision's source needs a link that a session request lacks; the test-plan template is long for a docs change | Fixed: a "Threat model" section in the plan template; the rest open, low |
| 6 | `make docs-check` does not check links inside slice bundles | Open, pre-existing |
| 7 | `make lint` checks only committed work; the discovery exit (a merged plan PR) cannot be met locally | As designed |
| 8 | Docker is needed indirectly: `make tooling-test` (`tests/tools/test_qa_deploy.py`), `make qa-deploy`, `make qa-quality` and the launcher's evidence step run `docker compose config` | Open, low: not stated in `AGENTS.md` |
| 9 | A reviewer filed a low wording defect as a decision concern, which the rules then route to the owner | Open: a rules question for the owner |
| 10 | The plan review read 4 of about 70 listed files and was accepted | Trip point 1's consequence (all of slice 4's files were listed); the empty-review rule asks for one |
| 11 | The stage table asks every gate and the full E2E suite even for a one-line change | Decision concern 7 |
| 12 | `--path` hints made the implementation review fail the empty-review rule when it read only the plan | Open, medium: growth proposal 5 is related |
| 13 | The launcher's retries can use more calls than a budget a user set | As designed (S41); the attempt log counts every try |
| 14 | The brief showed a never-completed unit as "nothing open" and did not flag a missing final unit | Fixed: "not reviewed" and a line when no `final` unit is among the PR's units |
| 15 | The brief over the integration branch mixes in every unit of the unmerged slice 4 | Ends when slice 4 merges |
| 16 | The order of handoff edits around the implementation review is unclear | Open, low |
| 17 | `README.md` still said "a four-phase slice workflow", which 4.6's step-reference test missed; its `make qa-quality` comment listed 4 of 6 targets | Fixed, and the step-reference test now looks for "four-phase" |
| 18 | Whether a document made stale by an unmerged slice is a delivery miss yet | Answered by the final review (FR-6): yes, logged as DPL-012 |

## Review outcome

### Decision brief

Built by `scripts/review_brief.py` from the review units this PR adds (head `e266c154e1ef`, merge-base `3347754ef038`). The plans and records are worth reading where this brief points.

| Unit | Last verdict | Rounds | Blocking | High | Medium | Low | Open |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `agentic-sdlc-poc` `final` | yes | 2 | 0 | 2 | 5 | 3 | nothing open |
| `agentic-sdlc-poc` `growth` | yes | 2 | 0 | 1 | 5 | 2 | nothing open |
| `agentic-sdlc-poc` `owner-decisions` | yes | 2 | 1 | 2 | 5 | 0 | 2 for the owner |
| `poc-4-1-review-prompts` `implementation` | yes | 2 | 0 | 2 | 6 | 5 | 1 for the owner |
| `poc-4-2-review-inputs` `implementation` | yes | 2 | 0 | 3 | 4 | 4 | nothing open |
| `poc-4-3-review-records` `implementation` | yes | 2 | 2 | 1 | 3 | 4 | 1 for the owner |
| `poc-4-4-stage-checklists` `critique` | A: no, B: yes | 1 | 1 | 5 | 10 | 6 | 1 for the owner |
| `poc-4-4-stage-checklists` `implementation` | yes | 1 | 0 | 1 | 4 | 3 | nothing open |
| `poc-4-5-benchmark` `mechanics` | yes | 2 | 3 | 4 | 6 | 7 | 1 for the owner |
| `poc-4-5-benchmark` `report` | yes | 2 | 2 | 1 | 3 | 4 | nothing open |
| `poc-4-6-stage-rules` `implementation` | yes | 1 | 0 | 1 | 5 | 5 | 2 for the owner |

**Answered `owner:`**

- `agentic-sdlc-poc` `owner-decisions` F2 (high): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision 7 under "Decisions to make"): adding a list item needs the owner's approval (`AGENTS.md`, Stage checklists), and the list holds its 12 questions; the proposal is a Blocks bullet in `docs/review_checklists/plan-and-test-plan.md` for a plan that claims a small slice while a condition does not hold. Until the owner decides, the open mandate and `AGENTS.md` (Small slices, which the reviewer receives) are the only check
- `poc-4-6-stage-rules` `implementation` F4 (medium): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: decision 4 under "Decisions to make" asks the owner to remove the personal copy, which takes precedence over the repository's while it exists; removing a file from the owner's own folder is the owner's to do

**Decision concerns**

- `agentic-sdlc-poc` `owner-decisions` F6 (medium): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision concern 11): the raise from 60 to 85 under the DC8 approval is put to the owner, recommendation confirm. Meanwhile the hard stop is lowered to the 76 calls used (`scripts/run_review_benchmark.py` `BUDGETS`, its test in `tests/tools/test_run_review_benchmark.py`), so no further stage-B call runs without a new decision; the Decisions-made DC4 row now says RC-2 ran as calls 60 and 61 after a canary for CLI 2.1.323; the report's Calls line and the author-decision budget row agree
- `poc-4-1-review-prompts` `implementation` R1-5 (medium): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision concern 1): S41-D8 limits the read check to files a `fixed:` answer names; extending it to every path any answer names changes an approved decision, so it is implemented as written and put to the owner with the recommendation to extend it
- `poc-4-3-review-records` `implementation` R1-3 (high): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision concern 2): implemented within S43-D4's words, so a later round's `owner:` answer to the same finding ID (a re-raised finding keeps its ID) settles a rejected blocking or high finding without editing answers a recheck read; tests `test_rejected_finding_that_the_next_round_re_raises_still_fails` and `test_a_later_owner_answer_to_the_re_raised_finding_settles_the_rejection`. The owner confirms this reading or chooses another; the red check between the answers commit and the recheck stays, as the plan accepts
- `poc-4-4-stage-checklists` `critique` C-2 (high): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: decision concern 4. S45-D5 fixes one recheck case, a false `fixed:`; the benchmark report will say that the recheck comparison measures only the acceptance of a false fix, not the re-raising of answers that hold. Recommendation: before choosing the recheck wording, run a second recheck case with a correct rejection (2 more runs, within the 60)
- `poc-4-5-benchmark` `mechanics` L4 (low): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision concern 3): S45-D7 makes the author the confirmer; recommended to keep it, with the Sonnet sample measuring agreement
- `poc-4-6-stage-rules` `implementation` F5 (medium): owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: decision concern 7, with a recommendation for small fixes. The opening sentence of the slice workflow now agrees with the stages (a plan and its review, tests first when the fix changes behaviour, the final review and the close-out; AGENTS.md)

**`cannot determine` in a recheck**

None.

**Still disputed after a recheck**

None.

**Blocking and high findings answered `rejected`**

None.

**Where findings started** (origin stage of each finding, against the review that found it: its `--stage` lists, or its unit when it had none)

| Origin | critique | final | growth | implementation | mechanics | owner-decisions | report |
| --- | --- | --- | --- | --- | --- | --- | --- |
| architecture and interfaces | 0 | 0 | 0 | 3 | 2 | 1 | 0 |
| discovery | 5 | 0 | 0 | 8 | 0 | 0 | 0 |
| implementation | 14 | 9 | 7 | 32 | 14 | 6 | 9 |
| tests first | 3 | 1 | 1 | 10 | 4 | 1 | 1 |

**The test-plan questions.** Slice 4's implementation reviews ran before the rule that they answer the three
test-plan questions as findings (2026-11-13), so no finding is mapped to a question here; every finding is in its
unit's record.

Round 2's review unit `round-2` is reviewed next; the brief above is rebuilt after it.

## How the owner can check the work

- **Plant a defect** in a plan or in the code on the branch, and tell no one. Then see whether the reviews
  find it.
- **Read the decision brief** on each slice's decision page (for slice 4, the review outcome section above): it lists what the author decided for you.
- **Question this file.** If an item here is unclear, the work behind it is probably unclear too.
