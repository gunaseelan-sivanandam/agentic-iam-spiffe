# Slice 4 — the owner's decision file

The one page the owner reads for slice 4, and its end-review page: the goal, what slice 4 builds in plain
words, the steps of the run, and every decision made or still to make. The plans, test plans and review records
under `docs/slices/poc-4-*/` are the working documents for the author and the reviewers. The author keeps this
file current during the run and says in it what was decided on the owner's behalf. At the end it holds the
checklists, the benchmark counts, every decision concern, every parked unit, every process-growth proposal and
every discovered issue with its disposition.

Last updated: 2026-11-13: the owner's decisions on decision concerns 2, 3, 4, 7, 8 and 10 recorded; 7 (small slices) and 10 (the decision page) implemented; the second recheck case (4) and the severity analysis (8) in progress. Before: every sub-issue implemented and reviewed, the benchmark run and its report reviewed, the dry slice and the final review run (2026-11-10).

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
| 4.5b | Ran within 57 of 60 calls; report in [`benchmark_report.md`](../poc-4-5-benchmark/benchmark_report.md): `open+list` 7 of 11, `short+list` 6, `open-B+list` 6, both rechecks 1 of 1; 29 of 125 findings confirmed (two re-judged after unblinding, FR-1), the second confirmer agreeing on 9 of 10; the third canary valid and passed | Report review ended after round 2. Round 1: not approvable; 2 blocking, 1 high, 3 medium, 4 low; all fixed. Round 2: attempt 1 failed the read check (issue 14); attempt 2 approvable, all 10 answers accepted, no new finding |
| 4.6 | Implemented: the seven-stage table and the rules moved into it, the templates, `scripts/review_brief.py`, the grill-me skill in the repository, the front-matter rule of the lint gate | Ended after round 1: approvable; 1 high, 5 medium, 4 low and a simpler alternative; 9 fixed, F4 and F5 to the owner (decision 4, decision concern 7) |
| Final review | Unit `final` of this bundle, with the owner's open question ([record](review_final.md)) | Ended after round 2. Round 1: approvable, no blocker; 2 high, 5 medium, 2 low, all fixed. Round 2: approvable; all 9 answers accepted; 1 new low, fixed |
| Growth (2026-11-13) | Rejections read like fixes, a `searched` list, the checklist question on findings ([record](review_growth.md)) | Ended after round 2. Round 1: approvable; 1 high, 5 medium, 1 low; 6 fixed, the low rejected. Round 2: attempt 1 failed the read check (issue 17); attempt 2 approvable, all 7 answers accepted; 1 new low, fixed |

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
| S45-D1 | `BUDGETS` | `test_stage_b_stops_at_sixty_calls_counting_retries_and_the_canary`; 57 of 60 used |
| S45-D2 | the result identity | `test_result_records_its_full_identity_and_the_report_reads_one_stage` |
| S45-D3 | `CONFIGURATIONS` | `test_configurations_differ_only_in_the_mandate_and_carry_the_same_list_and_rules` |
| S45-D4 | `score`, the match rule | the scoring tests of `tests/tools/test_run_review_benchmark.py` |
| S45-D5 | the answer key's 17 cases | `test_the_dpl_010_case_holds_the_launcher_and_its_tests_and_not_its_answer`; the dry run |
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

## Why the benchmark detected fewer than 80%

Detected: `short+list` 6, `open+list` 7, `open-B+list` 6 of 11 defect cases. Seen at any severity: 9, 9 and 8; 9 of
10, 9 of 10 and 8 of 10 when failed or withheld reviews are left out. The misses: 5 seen but rated below high (RM-3
and RM-4 by every setup, each citing its list question; decision concern 8), 3 lost to review mechanics (two empty
reviews, one withheld report), and 4 not found (RM-5 everywhere, RM-6 once). The planted cases were found; the
historical misses DPL-004 and DPL-005 are now seen but not flagged, and DPL-010 is caught by one setup of three. The
full analysis is in the [benchmark report](../poc-4-5-benchmark/benchmark_report.md), section "Why fewer than 80% of
the defects were detected".

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
| 2026-11-13 | Decision concern 4: run a second recheck case, with a correct rejection, on both recheck wordings; the author adds, at no extra cost, a correct fix next to the correct rejection in the same case: 2 runs, within the 3 calls left of the 60-call budget | "DC4 yes run a second recheck" |
| 2026-11-13 | Decision concern 7: a small slice (four conditions, `AGENTS.md`, Small slices) runs as one PR with the plan review and the implementation review as its units and the final review "none, small slice"; the user merges once; the plan states the conditions and the plan review checks the claim; no tool checks them until a review accepts a wrong "small" claim (the author's choice) | "DC7 yes, smaller slices can have single PR, but needs to define what a smaller slice is"; on the definition: "sound right" |
| 2026-11-13 | Decision concern 8: the three-step analysis of why reviewers rate found defects below the detection threshold: classify the mis-rated findings; one general severity-wording change; measure it on all cases (about 15 reviews and USD 12 beyond the 60-call budget); not the two R5 and C10 blocking conditions alone | "I see it as gap that the reviewers cannot assign the severrity scoring propoerly, just adding these two questions would find this issue, but miss others. Needs further analsis"; on the three steps: "complete it and do not wait for my approval" |
| 2026-11-13 | Decision concern 10: the brief holds no CI result; every slice gets a decision page (this page for slice 4) that holds the brief, the implementation review's answers and every discovered issue; the PR body states the goal and what changed and links the page (the author's resolution: one home per fact) | "DC 10 - I can see the CI job failue or success in PR page, Keep the PR page that explain the goal, changes, and anything everything that needs my attention."; on the proposed PR-body layout: "Wont all these info be available in my decisions page" |

## Decisions to make

| # | Decision | When | Options | Recommendation |
| --- | --- | --- | --- | --- |
| 1 | The evidence secret check: a credential value must look like a token (20 characters or more, or a digit), and values in code spans and quotes are found | At the end; already in effect since #48 | Keep; change | Keep: every credential here looks like a token, and CI's full E2E run passed |
| 2 | Default review setup and mandate wordings (initial, recheck, final) | At the end | From the [benchmark's counts](../poc-4-5-benchmark/benchmark_report.md): detections `short+list` 6, `open+list` 7, `open-B+list` 6 of 11; false alarms 2, 2 and 4; rechecks both 1 of 1 | Keep `open+list` and 4.1's wordings: no setup is shown better, and the draft raised the most false alarms; the counts are within chance, so this is a default, not a finding |
| 3 | Recreate the hidden issues under the owner's account if GitHub has not answered | At the end, or about 2026-11-23 if the owner is around | Recreate the open ones; keep waiting | Recreate the open ones |
| 4 | Remove your personal copy of the grill-me skill. A personal skill takes precedence over a project skill of the same name, so while it exists, discovery runs the old text, which cuts off two sentences and never asks the assets question, instead of the repository's (4.6 review, F4) | Before the next slice's discovery | Remove it; rename one of them | Remove it: the repository copy is the reviewed one |
| 5 | Measure the `unit-tests` list, which no benchmark case used, nor the tests-first pair with `e2e-tests` (discovered issue 15) | Before relying on the list, or in slice 8 | Add one or two unit-test cases now (about 6 calls; S45-D5's cases and the 60-call budget change, 3 calls are left); or measure it in slice 8 | Slice 8, which measures the lists' own effect against reviews without them |

## Parked units, decision concerns and growth proposals

| # | Kind | Part | Item | The author's recommendation |
| --- | --- | --- | --- | --- |
| 1 | Decision concern, resolved | 4.1 | S41-D8 made a recheck read only the files a `fixed:` answer names, so a `rejected:` answer resting on a file could be accepted without opening it (4.1 review round 1, R1-5) | Resolved by the owner on 2026-11-13: the launcher now also requires every file a `rejected:` answer cites to be read |
| 2 | Decision concern, resolved | 4.3 | S43-D3 fails a record whose answers changed after a recheck read them, and S43-D4 settles a rejected blocking or high finding only by the next round's acceptance or an `owner:` link. Read narrowly, a rejection the recheck re-raised could never be decided by the owner without editing answers the recheck read, and `make docs-check` would stay red (4.3 review round 1, R1-3). The check is also red between the answers commit and the recheck, by design | Resolved by the owner on 2026-11-13: the implemented reading is kept, a later round's `owner:` answer to the same finding ID settles it |
| 3 | Decision concern, resolved | 4.5 | S45-D7 makes the author the blinded confirmer, so the blinding rests on the author not looking: the token map and the results with their configurations sit in the same folder as the export (4.5a review round 1, L4) | Resolved by the owner on 2026-11-13: kept; the author stays the blinded confirmer |
| 4 | Decision concern, decided, in progress | 4.5 | S45-D5 has one recheck case, RC-1, whose answer is a false `fixed:`. It measures whether a recheck wording accepts a false fix, not whether it re-raises answers that hold (a correct rejection, a correct fix), so a wording that re-raises everything would score best (4.4 critique, C-2) | Decided by the owner on 2026-11-13: run a second recheck case with a correct rejection, and a correct fix beside it, on both wordings: 2 runs within the 3 calls left of the 60. Results to follow; until then the report says what the recheck comparison cannot show |
| 6 | Decision concern, withdrawn | 4.5 | S45-D9's valid canary seemed impossible: two twins declined the planted `CLAUDE.md`. The cause was the canary prompt, built by the author from the review prompt (report review, B2); with its own prompt the third canary was valid and passed | Nothing to decide |
| 7 | Decision concern, resolved | 4.6 | S46-D1 and S46-D5 give every slice a plan PR the user merges, a plan review, an implementation review and a final review, so a one-line fix costs three review units and two merges (about USD 6 to 9 at the plan's estimates) unless the plan records a rule deviation with the user's words (4.6 review, F5) | Resolved by the owner on 2026-11-13: a small slice, by four conditions, is one PR holding the plan and the change, with the plan review and the implementation review as its units and the final review "none, small slice". Done: `AGENTS.md` (slice workflow, Small slices, Discovery, Final review), the plan template's Small slice part; `test_the_plan_template_check_fails_on_each_missing_part` |
| 8 | Decision concern, decided, in progress | 4.4 | The benchmark's misses RM-3 (requirements without proof) and RM-4 (a gate inside another CI job) were found by every review, each citing the list question that asks it (R5, C10), and rated medium or low, which the rule does not count as a detection. The lists' "Blocks at this stage" sections do not name these cases, so the reviewers' severities follow the rules | Decided by the owner on 2026-11-13: not the two blocking conditions alone, but the three-step analysis: classify the mis-rated findings, one general severity-wording change, measured on all cases (about 15 reviews, USD 12 beyond the 60-call budget), without waiting for the owner's approval. Results to follow |
| 10 | Decision concern, resolved | 4.6 | S46-D9 and S46-D13: the brief opens the PR body, which is a snapshot not updated later; CI runs on pull requests, so a brief pasted when the PR is opened always says "no run for this commit; not a pass" (4.6 review, F3) | Resolved by the owner on 2026-11-13: the brief holds no CI result, which the owner sees on the PR page; the brief, the review answers and the discovered issues go on the slice's decision page, which the PR body links. Done: `scripts/review_brief.py` (the CI line removed), `AGENTS.md` (Start here, Discovered issues, the stage table, Discovery, Handoff, Stage checklists, Implementation review), `docs/slices/_template/decisions.md`; `test_the_brief_holds_no_ci_result_and_reads_no_network`, `test_the_decision_page_template_has_every_section_the_owner_asked_for` |
| 9 | Growth, approved and implemented | 4.5 | A finding may name the checklist question that prompted it (`question`, for example `code:10`); the benchmark report counts the findings that do. Approved by the owner on 2026-11-13 | Done: the launcher's schema and output section, `AGENTS.md` (Stage checklists), the benchmark report; the benchmark's runs predate the field |
| 5 | Growth, replaced and implemented | 4.1 | The first proposal, to drop unread files from `opened` instead of failing, was withdrawn: of the four failed reviews it would have passed one whose five acceptances rested on files the reviewer never read. In its place, approved by the owner on 2026-11-13: a recheck must read every file a `rejected:` answer cites, as it must for a `fixed:` answer; and a reviewer lists files it only searched under `searched`, so `opened` stays a claim the launcher checks | Done: the launcher's schema, output section and answer checks, `AGENTS.md` (Modes and prompts) |

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

At handoff, the output of `python3 scripts/review_brief.py --base origin/poc/agentic-sdlc` and the implementation
reviews' answers to the test-plan questions go here.

## How the owner can check the work

- **Plant a defect** in a plan or in the code on the branch, and tell no one. Then see whether the reviews
  find it.
- **Read the decision brief** on each slice's decision page (for slice 4, the review outcome section above): it lists what the author decided for you.
- **Question this file.** If an item here is unclear, the work behind it is probably unclear too.
