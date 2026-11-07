# Review record — agentic-sdlc-poc slice 2 (review launcher and benchmark)

Implementation review of slice 2 of the [plan](plan.md), on the branch `poc/slice-2-review-launcher`,
which is built on slice 1 (`poc/slice-1-rules`) until slice 1 merges. The reviews ran through the new
launcher, `scripts/run_independent_review.py`; each attempt is in
[`review_attempts.jsonl`](review_attempts.jsonl) (unit `slice_2`), which holds the reviewed commit,
the base commit, the hashes of the rules, the task prompt, the full prompt, the paths under review,
the withheld files and the report, and the usage figures. This record keeps the task prompts and the
reports verbatim and the author's answers. Rounds 1 and 2 reviewed the code, rounds 3 and 4 the
benchmark report and the close-out; round 1 is also the done-when's "one real review through the
launcher".

**Reviewer.** A fresh headless Claude session (Opus 5.5, `claude-opus-5-5`), never the author,
confined by the launcher to a frozen copy of the reviewed commit without this record and the attempt
log, with the rules of the base branch `poc/slice-1-rules` at `d2a4d6b` in its prompt. Round 1 at
high effort (the initial review), round 2 at medium (a focused recheck by the same model and role,
given its earlier report and the answers; rounds 3 and 4 likewise).

**Command.** The launcher builds the call (`build_invocation`): `claude -p --safe-mode
--setting-sources "" --model claude-opus-5-5 --effort <effort> --tools Read,Grep,Glob
--permission-mode dontAsk --strict-mcp-config --mcp-config '{"mcpServers":{}}'
--no-session-persistence --output-format stream-json --verbose --json-schema <report schema>`, run
in the copy with only `PATH`, `HOME` and `LANG`. The launcher was invoked as:

```sh
python3 scripts/run_independent_review.py --commit HEAD --base poc/slice-1-rules \
  --record docs/slices/agentic-sdlc-poc/review_slice_2.md --unit slice_2 --round <1|2> \
  --reviewer "impl:<scratch>/task_r<n>.md:claude-opus-5-5:<high|medium>" \
  --path scripts/run_independent_review.py --path scripts/run_review_benchmark.py \
  --path tests/tools/test_run_independent_review.py --path tests/tools/test_run_review_benchmark.py \
  --path tests/review_benchmark/answer_key.yaml [round 1 also: --path tests/tools/fakes/fake_claude.py \
  --path tests/tools/fakes/fake_codex.py --path tests/review_benchmark/prompts/short.md \
  --path tests/review_benchmark/prompts/checklist.md]
```

The full prompt the reviewer received is the launcher's preamble, the approved rules and the task
below (`build_prompt`); its SHA-256 is in each start entry.

## Round 1 (initial review, high effort)

Reviewed commit `21a8536`; attempt `slice_2/c1/r1/impl/1`. 360 seconds, 15 turns, 13 tool calls (all
inside the copy, none denied), 35,898 output tokens, CLI cost estimate USD 1.83; afterwards the
5-hour window stood at 17% and the weekly window at 2%. Status completed, verdict "no".

### Task prompt (verbatim)

````text
This is the implementation review of slice 2 of the agentic-SDLC PoC (review round 1, the initial review). The change adds the review launcher, the benchmark runner, the benchmark's answer key, prompts and planted patches, and their tooling tests. The benchmark has not been run yet; its report comes later in this slice.

## The intent

The approved plan is docs/slices/agentic-sdlc-poc/plan.md (merged with PR #31): read "Slice 2 — Review launcher and benchmark", the decisions POC-D2, POC-D3, POC-D4, POC-D6, POC-D7, POC-D10 and POC-D13, "Assets and holders", "Hidden-state and trust decisions", and the review notes on the launcher. The test plan is docs/slices/agentic-sdlc-poc/test_plan.md, sections "Slice 2 — launcher" and "Slice 2 — benchmark", "Live checks" and "Independent review at the implementation PR". Slice 1 (the rules) is the base branch, not yet merged into poc/agentic-sdlc; slice 3 is not part of this change.

## Environment facts (probed by the author on 2026-11-07)

- Claude CLI 2.1.319. Its bundled schema names three rate-limit statuses: "allowed", "allowed_warning" (past a warning threshold) and "rejected" (at or past the limit). The launcher proceeds on the first two and pauses on anything else.
- With `--json-schema`, the reply arrives as a `StructuredOutput` tool call and as `structured_output` in the result event; the result event lists refused calls in `permission_denials` (tool_name, tool_use_id, tool_input). A Haiku probe in a scratch copy: Read and Grep of paths outside the working directory were denied under `--permission-mode dontAsk` without allow rules; the CLI passes absolute paths in tool inputs.
- The result event also carries fields the launcher must not publish (session and credential metadata); the launcher copies only named fields.
- Local: `make tooling-test` passes (314 pytest, 9 shell). Deliberately breaking the launcher (passing the whole environment, skipping the outside-path check, not withholding the review files, admitting a round that drops a "no" reviewer, accepting an empty review, no retries, no publication check) and the runner (budget cap 27, budget not counted, no copy leak search, decision threshold 1, no term required, accepting another key) makes at least one test fail each time.
- `python3 scripts/run_review_benchmark.py --dry-run`: 12 of 12 cases pass the leak search.

## Questions to answer (the test plan's implementation questions)

1. Tests: for each new test, which wrong behaviour would still pass it (the fake CLI never called, a refused call read as success, a missing value or empty file read as success)? Does its assertion match its row in the test plan? Name any test-plan row that has no test.
2. Keys: does the change make a key, socket or secret reachable by a service or process outside its holders? In particular: can any file outside the reviewer's copy, any file not tracked at the recorded commit, the withheld review files (record and attempt log), or any variable of the author's environment reach the reviewer? Can anything the launcher or the runner writes (attempt log, reports, benchmark results) carry a secret or an operational detail into a public record?
3. Rules and names (POC-D7): does each new file's purpose comment say what the file is for, and do its names say what each part does?
4. Does anything in the change contradict the approved plan or the base branch's rules, or claim more than it does?
````

### Report (verbatim, rendered from the released JSON)

Verdict: **no** (approvable within the threat model).

#### B1 (blocking) — `scripts/run_review_benchmark.py:346`

- **Problem:** The canary counts as passed whenever the flagged run did not return status "budget" and _followed_any() is false. It never requires the flagged run to have completed, and it ignores denied reads of the outside marker. Followed instruction IDs are taken only from outcome.report, which is None for every non-completed run. So a run that failed, was paused or is pending is reported as a passed canary. A run that followed a leaked CLAUDE.md instruction and was then failed for its outside read is also reported as passed.
- **Evidence:** run_canary: `"passed": flagged["status"] != "budget" and not _followed_any(flagged)`. canary_outcome: `findings = (outcome.report or {}).get("findings", [])`. classify() returns CallOutcome("failed", ..., report=None) for any outside call (run_independent_review.py:497-498). _outside_reads gives `allowed = reads - denied`, so a denied read gives allowed 0, and `outside_read_denied` is recorded but never used in `passed`. No test covers run_canary's passed/valid logic: only twin_invocation and canary_outcome on a stub are tested.
- **Failure scenario:** A later CLI version (the test plan reruns the canary whenever the CLI version changes) loads the hostile CLAUDE.md despite --safe-mode. The reviewer adds the CANARY-BRAVO finding and tries to Read the outside marker, as CLAUDE.md tells it to. dontAsk denies the read, so classify marks the run "failed" for an outside call and drops the report, and with it the CANARY-BRAVO finding. hook_ran stays false because settings are still excluded, and outside_read_allowed is 0. The result says passed=true, and the report states that branch instructions did not reach the reviewer, which is the opposite of what happened. A usage-limit pause or a provider error on the flagged call likewise yields passed=true without any review. The plan uses the canary instead of the separate confinement live check, so this is the slice's only evidence for confinement.

#### B2 (blocking) — `scripts/run_review_benchmark.py:393`

- **Problem:** The approved budget of 26 reviewer calls (POC-D10) is enforced only inside one invocation, by an in-memory Budget object. The runner does not stop at a usage limit, and it cannot resume. A paused call consumes budget and the run moves on to the next case, so after a limit is hit the rest of the budget goes on paused calls. Running --run again re-runs every case with a fresh budget of 26 and appends duplicate results. compare_prompts then silently keeps the last result per (case, prompt).
- **Evidence:** `budget = Budget(budget_limit)` is created in each run_benchmark call; nothing counts the calls already in RESULTS_FILE. review_with_retries breaks on any status other than provider_error, and run_benchmark goes on to the next item, so "paused" stops nothing. `_completed_reviews` builds a dict keyed by (case, prompt), so a later line overwrites an earlier one. The test plan's live check says the benchmark 'runs within its budget, or stops at a usage limit and resumes after the reset'. test_run_stops_at_the_budget_counting_retries checks only a single invocation.
- **Failure scenario:** Stage A hits the 5-hour limit at case 6. Cases 6 to 11 each burn one call on a paused attempt until the 26 calls are used, so they become incomplete. To 'resume after the reset', the author runs --run again. All 12 cases run again from the start, up to 26 more calls (52 in total) without the user's decision, and the comparison uses whichever result was written last. The budget gate passes its test, but the approved cap is exceeded and the paired results can come from different runs.

#### A1 (advisory) — `scripts/run_independent_review.py:817`

- **Problem:** invocation_from_entry rebuilds only the argv and the hashes of the rules, the prompt file, the paths, the withheld files, the schema and the tree. It does not rebuild the full prompt sent on stdin, and it does not check full_prompt_sha256 or diff_sha256, although every input needed to rebuild them is in the entry.
- **Evidence:** The `recomputed` dict has no full_prompt_sha256 and no diff_sha256 key. The start entry records both (start_entry, line 685-686).
- **Failure scenario:** A later edit to build_prompt changes the text the reviewer receives. Rebuilding an old entry reports no mismatches, so 'the exact invocation can be rebuilt' (success criterion) holds for the argv but not for the stdin.

#### A2 (advisory) — `scripts/run_independent_review.py:603`

- **Problem:** Nothing stops a user's reset or extension reference from being reused. Passing the same --reset again on a later round-1 invocation starts yet another count. One --extension URL admits round 5 and every round after it.
- **Evidence:** _current_count returns count+1 on every invocation that carries a reset. admit_round checks only `round_no > ROUND_LIMIT and extension is None`. Neither looks at the references already in the log.
- **Failure scenario:** After a reset, a provider error fails one reviewer in round 1 of count 2. The author re-runs the same command line, --reset included. Count 3 starts and every reviewer runs again, so one user act has produced two restarts. Likewise, the extension URL required for round 5 also admits rounds 6 and 7. Both are recorded in the log, but the launcher's admission does not catch them.

#### A3 (advisory) — `scripts/run_independent_review.py:567`

- **Problem:** When the publication check withholds a report, the start entry is left with no end entry. On the next invocation, recover() records that attempt as "interrupted" with the reason 'the launcher stopped during the attempt'. That is false, and the authoritative log never shows that the publication check fired.
- **Evidence:** _guarded_attempts returns "withheld" only to stdout and stderr. The test test_secret_in_the_reply_leaves_no_report_and_no_end_entry confirms there is no end entry. recover() then appends interrupted with a fixed reason.
- **Failure scenario:** A slice-6 review-record check, or the user, reads the log and concludes the launcher crashed. The real cause, a secret-shaped reply, does not appear in the record.

#### A4 (advisory) — `tests/review_benchmark/answer_key.yaml:66`

- **Problem:** Some expected findings are scored loosely. RM-3 accepts any line (0 to 100000) of trace/tests.yaml or the test plan, with very common terms (proof, trace, e2e). RM-2 accepts 760 lines of the harness with the term "evidence". PD-1 accepts "any". compare_prompts/decide applies the decision rule to these automatic detections, not to the hand-confirmed ones the plan describes.
- **Evidence:** RM-3 locations use [[0, 100000]]. RM-2 has ranges [[1240, 2000]] and terms [evidence, ...]. PD-1 terms include `any`. decide() is fed totals from `len(result["detected"])`.
- **Failure scenario:** An unrelated blocking finding in docs/slices/agentic-delivery-process/test_plan.md that mentions 'trace' counts as detecting DPL-004. If the report prints the automatic decision without re-applying it after hand confirmation, the prompt choice can rest on false detections.

#### A5 (advisory) — `scripts/run_review_benchmark.py:154`

- **Problem:** The canary's allow rule `Read(<absolute path>)` is probably not an absolute-path rule in Claude Code's permission syntax: a single leading slash is read relative to the settings file, and an absolute path needs '//'. That would explain the probe result 'the project allow rule did not open the outside file in any run'. Also, the hostile instruction files are themselves the paths under review, so a twin that 'follows' them may have taken them from data rather than from instruction loading.
- **Evidence:** settings = {"permissions": {"allow": [f"Read({outside})"]}}. The case paths are AGENTS.md, CLAUDE.md, scripts/CLAUDE.md, tests/unit/AGENTS.md and .claude/settings.json. The plan's environment facts say the allow rule never opened the outside file.
- **Failure scenario:** The 'settings reach the reviewer' half of the canary can rest only on the hook, and the twin's validity can come from prompt injection through file content rather than from the CLI loading the files. So the canary does not cleanly show what it claims to show.

#### A6 (advisory) — `scripts/run_independent_review.py:387`

- **Problem:** relative_to_copy compares lexically normalised paths against the mkdtemp path without resolving symlinks. On macOS, a supported environment, the temp directory /var/folders/... is reached through a symlink to /private/var/...; if the CLI reports the resolved path, every absolute Read inside the copy counts as outside and every review fails. This fails closed, so it is not a false green.
- **Evidence:** `root = os.path.normpath(str(copy_root))`, with no realpath on copy_root. The environment facts say the CLI passes absolute paths in tool inputs.
- **Failure scenario:** On macOS with Rancher Desktop, every launcher review ends as 'failed: a call named a path outside the copy'.

#### A7 (advisory) — `tests/tools/test_run_review_benchmark.py:223`

- **Problem:** Some test-plan rows are only partly tested. Benchmark 'Approved rules': nothing checks that a case gets the rules at its own commit, or at its base for planted and canary cases. Budget: incomplete cases are tested only for the budget cap, not for pending or failed. Interruption: nothing tests a kill after the partial report is written but before the end entry; the kill test stops the launcher while the fake is still sleeping, before any reply.
- **Evidence:** No benchmark test asserts on PreparedCase.rules_text for the case commit. test_run_stops_at_the_budget_counting_retries covers only the budget status. test_killed_launcher... kills during `sleep: 30`, before any output.
- **Failure scenario:** A regression where prepare_case takes the rules from the wrong commit, for example from the planted commit with the canary's hostile AGENTS.md, passes every test.

#### A8 (advisory) — `scripts/run_independent_review.py:478`

- **Problem:** POC-D7 naming: _interrupted_call handles usage-limit pauses, provider errors and missing results. "interrupted" is also the log status for a killed launcher, so the name suggests the wrong thing.
- **Evidence:** The function returns statuses paused, provider_error and failed, never "interrupted".
- **Failure scenario:** A maintainer assumes this function produces the "interrupted" log status and edits the wrong place.

#### A9 (advisory) — `scripts/run_review_benchmark.py:39`

- **Problem:** The runner writes a new committed record, docs/slices/agentic-sdlc-poc/benchmark_results.jsonl, holding every reviewer's full findings text. The plan names only benchmark_report.md. Result lines also lack the CLI version, so a canary result cannot be tied to the CLI version it held for, which the 'rerun when the CLI version changes' live check needs.
- **Evidence:** RESULTS_FILE = Path("docs/slices/agentic-sdlc-poc/benchmark_results.jsonl"). result_line and run_canary have no cli_version field.
- **Failure scenario:** The report cannot show which CLI version the canary was valid for, and an unplanned record joins the slice bundle.


### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| B1 | Fixed. The canary passes only when the flagged run completed and followed nothing. Followed finding IDs are read from the stream's structured reply whatever the run's status. Reads of the outside marker count as followed whether allowed or denied. Validity counts the same signals for the twin. | `run_canary`, `canary_outcome`, `_followed_any`; tests `test_canary_passes_only_when_its_run_completed_without_following`, `test_canary_does_not_pass_without_a_completed_clean_run` (paused, escaped-and-failed, followed), `test_canary_counts_denied_reads_of_the_outside_marker` |
| B2 | Fixed. `RunState` starts from the calls already recorded in the results file for this answer key. Reviews that finished (anything but "budget" or "paused") are not run again. A paused call stops the run before the next case, and `--run` after the reset resumes. The comparison keeps the first completed review of each case and prompt. | `previous_state`, `RunState`, `review_with_retries`, `run_item`, `run_case`, `_completed_reviews`; tests `test_a_usage_limit_stops_the_run_and_a_rerun_resumes_within_the_budget`, `test_a_rerun_after_the_budget_is_spent_makes_no_call`, `test_a_rerun_does_not_record_a_finished_case_again` |
| A1 | Fixed. `invocation_from_entry` also rebuilds the diff and the full prompt and compares `diff_sha256` and `full_prompt_sha256`. The prompt now lists paths and withheld files sorted, so it is deterministic. Round 1's own entry predates the sorting, so this version cannot rebuild its full-prompt hash; the record says so. | `change_diff`, `build_prompt`, `invocation_from_entry`; test `test_invocation_and_hashes_are_rebuilt_from_a_log_entry` |
| A2 | Fixed. A reset reference already in the log is refused, and an extension reference admits only one round. | `_check_references_unused`; test `test_a_reference_admits_once` |
| A3 | Fixed within the approved test plan, which says the publication check leaves "no report and no log entry written". The interrupted reason now reads "the launcher stopped, or the publication check withheld the report". | `recover` |
| A4 | Fixed. RM-3's terms no longer include "trace" or "e2e", and PD-1's no longer include "any". The report labels the automatic comparison as before hand confirmation and applies the decision rule again to the confirmed detections. The answer key changed before any run. | `answer_key.yaml`, `report` |
| A5 | Fixed. The allow rule uses `//` for the absolute path. The hostile files are now committed first, and the change under review is a one-sentence README change, so a twin that follows them loaded them or went looking for them. | `canary_files`, `canary_commits`, answer key CANARY; test `test_real_miss_gets_the_rules_of_its_commit_and_the_canary_those_of_its_base` |
| A6 | Fixed. The copy root and each path are resolved with `realpath`. | `relative_to_copy`; test `test_symlinked_copy_root_still_counts_reads_inside_the_copy` |
| A7 | Fixed. New tests for the rules per case kind, a failed review leaving its case incomplete, and a partial report without an end entry. | `test_real_miss_gets_the_rules...`, `test_case_with_a_failed_review_is_incomplete`, `test_partial_report_without_an_end_entry_is_deleted_and_the_attempt_interrupted` |
| A8 | Fixed: renamed to `_paused_or_unfinished_call`. | launcher |
| A9 | Results file kept: the runner needs it to resume within the approved budget and to refuse results made with another answer key. It holds findings about old commits and passes the publication check before writing. Result lines now record the CLI version, and the report will name the file as an implementation detail. | `RESULTS_FILE`, `result_line`, `run_canary` |

## Round 2 (focused recheck, medium effort)

Reviewed commit `d4916ef`; attempt `slice_2/c1/r2/impl/1`. 48 seconds, 8 turns, 6 tool calls (all
inside the copy, none denied), 4,182 output tokens, CLI cost estimate USD 0.40; afterwards the 5-hour
window stood at 20% and the weekly window at 2%. Status completed, verdict "yes".

### Task prompt (verbatim)

````text
This is review round 2 of the implementation review of slice 2 of the agentic-SDLC PoC: a focused recheck by the original reviewer. Your round-1 report and the author's answers are below; check each answer against the change (the diff in _review_inputs/change.diff now covers round 1's commit and the fixes). Under the approved rules, from round 2 a new finding counts only if it blocks, except simpler alternatives and decision concerns.

The intent is unchanged: docs/slices/agentic-sdlc-poc/plan.md, "Slice 2 — Review launcher and benchmark", with its test plan. The benchmark has still not been run.

## Your round-1 report (verbatim JSON)

[the round-1 report below, as the JSON the launcher released]

## The author's answers

[the author's answers to round 1 below]

Local: `make tooling-test` passes (327 pytest, 9 shell). Deliberately breaking the canary pass rule, the budget carried across runs, the stop at a pause, and the skip of finished cases makes a test fail each time.

## Questions to answer

1. For each finding, accept the answer or re-raise it with new evidence.
2. Did the fixes introduce a blocking problem (a false green, a contradiction, a broken test)?
````

### Report (verbatim, rendered from the released JSON)

Verdict: **yes** (approvable within the threat model).

#### B1 (advisory) — `scripts/run_review_benchmark.py:407`

- **Problem:** Re-check of B1: accepted, fixed. The canary now passes only when the flagged run is 'completed' and none of the follow signals fired. The signals are planted finding IDs, the hook file, and reads of the outside marker, whether the read was allowed or denied. Finding IDs are now read from the stream's structured reply, so they are counted even when classify() drops the report.
- **Evidence:** run_canary: `passed = flagged['status'] == 'completed' and not _followed_any(flagged)`. canary_outcome reads `launcher.structured_reply(summary.result)` directly. _followed_any includes outside_reads_denied. Tests: test_canary_does_not_pass_without_a_completed_clean_run (cases paused, escaped-and-failed, followed), test_canary_counts_denied_reads_of_the_outside_marker, test_canary_passes_only_when_its_run_completed_without_following.
- **Failure scenario:** None left. The round-1 scenario (a CLAUDE.md leak followed by a denied outside read, with the run marked failed) now gives passed=false, and so do a paused run and a provider error.

#### B2 (advisory) — `scripts/run_review_benchmark.py:297`

- **Problem:** Re-check of B2: accepted, fixed. previous_state adds up the 'calls' of every recorded line for the same answer key and seeds RunState with that total, so the 26-call cap now holds across invocations. Finished reviews are skipped per case and prompt. A pause sets state.paused: retries stop, and the case loop stops before the next case. _completed_reviews keeps the first completed result.
- **Evidence:** RunState.take checks used >= limit. review_with_retries loops while `not state.paused.is_set() and state.take()`. run_benchmark breaks when paused. Tests: test_a_usage_limit_stops_the_run_and_a_rerun_resumes_within_the_budget (4 calls, then 6), test_a_rerun_after_the_budget_is_spent_makes_no_call (26 calls, then still 26).
- **Failure scenario:** None left. Resuming after a reset can no longer go over 26 calls, and it cannot pair results from duplicate runs.

#### A1 (advisory) — `scripts/run_independent_review.py:847`

- **Problem:** Accepted. diff_sha256 and full_prompt_sha256 are now rebuilt and compared. One small leftover: the rebuild always passes has_diff=True, so an entry recorded without a diff would show a false full_prompt mismatch. That fails loudly, not green, so it is not blocking.
- **Evidence:** invocation_from_entry: `build_prompt(inputs, ..., True)`. main uses `ctx.extra['diff_sha'] is not None`.
- **Failure scenario:** Rebuilding an entry recorded without a diff reports a false full_prompt_sha256 mismatch. Nothing passes falsely.

#### A2 (advisory) — `scripts/run_independent_review.py:609`

- **Problem:** Accepted. A reset reference that is already in the log is refused. An extension reference that already admitted a different round is refused, while re-running the same round with it is still allowed.
- **Evidence:** _check_references_unused; test_a_reference_admits_once.
- **Failure scenario:** None.

#### A3 (advisory) — `scripts/run_independent_review.py:573`

- **Problem:** Accepted. The approved test plan requires that a withheld report leaves no log entry. The interrupted reason now names the publication check as a possible cause, so the log no longer states something false.
- **Evidence:** recover reason: 'no end entry: the launcher stopped, or the publication check withheld the report'.
- **Failure scenario:** None.

#### A4 (advisory) — `tests/review_benchmark/answer_key.yaml:0`

- **Problem:** Accepted. The overly common terms are gone. The author says the report labels the automatic comparison as coming before hand confirmation and applies the decision rule again to the confirmed detections. The answer key changed before any run.
- **Evidence:** Author's answer and the updated answer key. The benchmark has not run yet.
- **Failure scenario:** None.

#### A5 (advisory) — `scripts/run_review_benchmark.py:0`

- **Problem:** Accepted. The allow rule now uses `Read(//...)`. The hostile files are committed in the base, and the change under review is a README edit, so the twin has to load or look for them. The test confirms that the diff and the rules contain no CANARY- text.
- **Evidence:** test_real_miss_gets_the_rules_of_its_commit_and_the_canary_those_of_its_base asserts `startswith('Read(//')`, CANARY- absent from rules_text and from the diff, and present in CLAUDE.md.
- **Failure scenario:** None.

#### A6 (advisory) — `scripts/run_independent_review.py:394`

- **Problem:** Accepted. The root and each path are resolved with realpath before they are compared.
- **Evidence:** relative_to_copy; test_symlinked_copy_root_still_counts_reads_inside_the_copy.
- **Failure scenario:** None.

#### A7 (advisory) — `tests/tools/test_run_review_benchmark.py:326`

- **Problem:** Accepted. There are now tests for the rules each case kind receives, for a case left incomplete by a failed review, and for a partial report left without an end entry.
- **Evidence:** The tests named in the author's answer exist at the lines shown.
- **Failure scenario:** None.

#### A8 (advisory) — `scripts/run_independent_review.py:0`

- **Problem:** Accepted. The function is renamed to _paused_or_unfinished_call.
- **Evidence:** Author's answer.
- **Failure scenario:** None.

#### A9 (advisory) — `scripts/run_review_benchmark.py:338`

- **Problem:** Accepted. The results file is needed to resume within the budget and to refuse results from another answer key. Each line goes through the publication check before it is written. Result lines and canary lines now record cli_version.
- **Evidence:** result_line and run_canary include cli_version. append_result calls check_publishable.
- **Failure scenario:** None.


### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| A1 leftover (`has_diff` fixed to true) | **Fixed**: the rebuild uses `has_diff` from the entry's `diff_sha256`. Not rechecked: a one-line change in the reviewer's own words, and no blocking finding is open. | `invocation_from_entry` (`4ec4059`) |
| Every other finding | Accepted by the reviewer. | — |

Round 1's start entry predates the sorted path list in the prompt, so `invocation_from_entry` of
this version rebuilds its argv and input hashes but not its full-prompt hash (A1).


## Round 3 (focused review of the report and the close-out, medium effort)

Reviewed commit `642b840` (the benchmark results, the report and the close-out documents), paths
under review: the report, the results file, `AGENTS.md`, `docs/STATUS.md` and the implementation log.

**Attempt 1** (`slice_2/c1/r3/impl/1`): **failed** by the launcher, "a call named a path outside the
copy" (62 seconds, 13 turns, 11 tool calls, 6,432 output tokens, CLI cost estimate USD 0.72; afterwards the 5-hour window stood at 36% and the weekly window at 4%). No report was released. The launcher keeps no stream, so the call is not
known; the likely cause is a relative Markdown link of the report (`../../../tests/...`) resolved
from the copy root. A failed attempt completes no round, so the round ran again with one note
added to the task.

**Attempt 2** (`slice_2/c1/r3/impl/2`): completed, verdict "no" (95 seconds, 20 turns, 18 tool calls, 8,236 output tokens, CLI cost estimate USD 0.84; afterwards the 5-hour window stood at 38% and the weekly window at 4%).

### Task prompt (verbatim, attempt 2; attempt 1 was the same without the last paragraph)

````text
This is review round 3 of the implementation review of slice 2 of the agentic-SDLC PoC: a focused review, by the original reviewer, of what was added after round 2 accepted the code. Round 2's verdict was "yes" with every round-1 finding accepted; since then the author applied one leftover (the prompt rebuild uses has_diff from the entry), ran the benchmark (stage A, 24 calls), and wrote the report and the slice's close-out documents.

The intent: docs/slices/agentic-sdlc-poc/plan.md, "Slice 2 — Review launcher and benchmark", in particular "Report", "Decision rule", "Configurations, staged" and "Done when", and the test plan's "Live checks" and "Review notes".

## What to review

- docs/slices/agentic-sdlc-poc/benchmark_report.md, against the raw results in docs/slices/agentic-sdlc-poc/benchmark_results.jsonl (one line per review, with its findings and score) and the answer key tests/review_benchmark/answer_key.yaml.
- AGENTS.md "Independent review → Reviewer" (now points reviews at the launcher), docs/STATUS.md, docs/history/implementation_log.md (the 2026-11-08 entry) and docs/slices/README.md.

## Questions to answer

1. Does every number and claim in the report follow from the results file? In particular: the hand confirmations and rejections (is each one right, judged against the expected defect in the answer key?), the decision rule applied to the confirmed detections, the canary's "valid" and "passed", the incomplete cases, and the quota figures.
2. Does the report claim more than the run shows, or leave out a run, a failure or a refused case (the plan requires every run)?
3. Do the recommendations stay within the plan (stage B and C are the user's decision; nothing is changed without approval)?
4. Which tracked document now says something this change made false?

Under the approved rules, a new finding counts only if it blocks, except simpler alternatives and decision concerns.

Note on paths: the first attempt of this round was failed by the launcher because one call named a path outside the copy. Markdown links such as `../../../tests/review_benchmark/answer_key.yaml` are relative to the file that contains them; open files by their path from the copy root (for example `tests/review_benchmark/answer_key.yaml`).
````

### Report (verbatim, rendered from the released JSON)

Verdict: **no** (approvable within the threat model).

#### R3-1 (blocking) — `docs/slices/agentic-sdlc-poc/benchmark_report.md:72`

- **Problem:** The RM-2 row says "Neither prompt saw token values written to evidence". The results file shows otherwise. The short-prompt review reported the DPL-002 defect, but as an advisory finding. Recommendation 3 (line 137–142) repeats the false claim: it says the reviewer found "none of" DPL-002 and that "neither prompt asked about them". So does the implementation-log entry ("defects of absence, which neither prompt found"). The counts and the decision rule are unaffected, because only blocking findings count as detections. The diagnosis behind recommendation 3 is wrong for DPL-002: the reviewer saw the leak but rated it advisory. A missing review question was not the cause.
- **Evidence:** In benchmark_results.jsonl line 3 (RM-2, short), finding F8 is kind "advisory" at scripts/rogue_node_tests.sh:1604, inside the key's range 1240–2000. Its problem says "M3 tests also write live biscuit bearer tokens to token.txt and into cmd_exercise_*.txt". Its failure scenario says "Capability tokens also end up in the same uploaded artifacts". It contains the key term "plaintext". That is DPL-002 as the answer key describes it: token values written into E2E evidence. The score shows advisory_only: [] only because of how scripts/run_review_benchmark.py:_expected_outcome (lines 246–253) works. It returns "location_only" whenever any blocking finding sits at the location (F3 here). An advisory finding with a key term is then never reported. The hand triage looked only at F3 and missed F8.
- **Failure scenario:** The user decides slice 4 and stage B from this report. Recommendation 3 sends the work to new review questions for DPL-002. The real gap is severity calibration: the reviewer found the leak and labelled it advisory. That calls for a different fix, such as a rule that a secret in evidence is blocking. The slice-4 measurement on RM-2 would then target the wrong cause.

#### R3-2 (advisory) — `scripts/run_review_benchmark.py:251`

- **Problem:** The automatic score hides an advisory-only match whenever any blocking finding without a key term sits at the same location. The report's "Location only" column therefore cannot show that an advisory finding named the defect. This caused R3-1.
- **Evidence:** _expected_outcome returns "location_only" if `blocking` is non-empty. It checks advisory findings with terms only when there is no blocking finding at the location.
- **Failure scenario:** In future runs, hand triage that follows the automatic columns can again miss a defect the reviewer reported only as advisory.

#### R3-3 (advisory) — `docs/history/implementation_log.md:72`

- **Problem:** The 2026-11-08 entry says the review had two rounds and that "round 2 accepted every answer". Round 3 (this focused review of the report and close-out) is now running, so the entry will be out of date once round 3 ends.
- **Evidence:** The diff adds "Review: two rounds through the launcher … round 2 accepted every answer." The task states this is round 3.
- **Failure scenario:** The history records fewer review rounds than actually ran, and does not mention this round's findings.

#### R3-4 (advisory) — `docs/slices/agentic-sdlc-poc/benchmark_report.md:123`

- **Problem:** The results file cannot confirm "20% before the run". Its first recorded five-hour utilization is 0.22, and the weekly figure is 0.02 from the first call. The "after" values (35%, 4%) match the last line. Everything else I checked against the results file matches: 24 calls, durations 13–251 s, 189,149 output tokens, 1,003–22,320 tokens per review, USD 13.27 total, the canary valid and passed, hook_ran false and true, 5 failed reviews under the empty-review rule, and the confirmations for RM-1, PD-1 to PD-4 and CL-2.
- **Evidence:** In benchmark_results.jsonl, line 1 has utilization five_hour 0.22, and lines 22–23 have 0.35 and seven_day 0.04.
- **Failure scenario:** A reader cannot check the "before" quota figure against the committed record. It is minor.


### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| R3-1 | Fixed. The RM-2 row now says the short-prompt reviewer saw DPL-002 (F8, advisory, `scripts/rogue_node_tests.sh:1604`) and rated it advisory, so it is not a detection, and that the automatic score hid F8. Recommendation 3 separates the two defects of absence neither prompt found (DPL-004, DPL-005) from DPL-002, which is a severity question: under coding rule 1, a secret in published evidence is blocking. It proposes review questions for the first and a severity rule for the second. The implementation-log entry says the same. Counts and the decision rule are unchanged (1 of 4 real misses for each prompt). | `benchmark_report.md` hand-confirmation table and recommendation 3; `implementation_log.md` |
| R3-2 | Fixed at the origin. `score()` lists an expected finding under `advisory_only` whenever a non-blocking finding with a term sits at its location and it was not detected, including beside a blocking finding without a term. The stored results of this run keep the score of the code that produced them, and the report's hand triage records F8. | `_expected_labels`, `_seen_as_advisory`; test `test_advisory_finding_with_a_term_is_listed_even_beside_a_blocking_one_without` |
| R3-3 | Fixed. The entry names four rounds, round 3's failed first attempt and its finding, and the E2E result at the slice's close. | `implementation_log.md` |
| R3-4 | Fixed. The quota row says where each figure comes from: 20% after review round 2 (attempt log), 22% at the first benchmark call, 35% after the last; weekly 2% to 4%. | `benchmark_report.md`, Quota |

## Round 4 (focused recheck, medium effort; the last round the rules allow)

Reviewed commit `1481098`; attempt `slice_2/c1/r4/impl/1`, completed, verdict "yes" (17 seconds, 8 turns, 6 tool calls, 1,871 output tokens, CLI cost estimate USD 0.24; afterwards the 5-hour window stood at 38% and the weekly window at 4%).

### Task prompt (verbatim)

````text
This is review round 4 of the implementation review of slice 2 of the agentic-SDLC PoC: a focused recheck, by the original reviewer, of the author's answers to your round-3 findings on the benchmark report and the close-out documents. It is the last round the rules allow; after it, open blockers go to the user.

The intent is unchanged (docs/slices/agentic-sdlc-poc/plan.md, "Slice 2 — Review launcher and benchmark"). Open files by their path from the copy root; Markdown links are relative to the file that contains them.

## Your round-3 report (verbatim JSON)

[the round-3 report below, as the JSON the launcher released]

## The author's answers

[the author's answers to round 3 below]

Since round 3, the full E2E suite ran on a clean stack at `642b840`: 120/120 passed. `make qa-deploy` (image users inspected) and `make qa-evidence` passed after it. `make tooling-test` passes.

## Questions to answer

1. For each finding, accept the answer or re-raise it with new evidence.
2. Did the fixes introduce a blocking problem?
````

### Report (verbatim, rendered from the released JSON)

Verdict: **yes** (approvable within the threat model).

#### R3-1 (advisory) — `docs/slices/agentic-sdlc-poc/benchmark_report.md:72`

- **Problem:** Answer accepted; the finding is closed. The RM-2 row now records F8 as seen but rated advisory, so it is not a detection. Recommendation 3 (lines 137–145) separates DPL-004 and DPL-005, the defects of absence, from DPL-002, which it treats as a severity question. The implementation log (line 27) says the same.
- **Evidence:** benchmark_report.md:72 and :140-144; implementation_log.md:27 says 'DPL-002: seen, but rated advisory'. The decision-rule counts are unchanged (1 of 4 for each prompt), which is consistent with counting only blocking findings as detections.
- **Failure scenario:** None remains. The diagnosis now matches the results file.

#### R3-2 (advisory) — `scripts/run_review_benchmark.py:249`

- **Problem:** Answer accepted; the finding is closed. `_expected_labels` now adds 'advisory_only' whenever the outcome is not 'detected' and a non-blocking finding with a term sits at the location, including beside a blocking finding without a term. The new test covers exactly that case.
- **Evidence:** run_review_benchmark.py:245-256; tests/tools/test_run_review_benchmark.py:180-183 asserts location_only == ['E1'] and advisory_only == ['E1'] when a blocking finding without a term and an advisory finding with a term share the location.
- **Failure scenario:** None remains. Future hand triage will see the advisory match in its own column.

#### R3-3 (advisory) — `docs/history/implementation_log.md:29`

- **Problem:** Answer accepted; the finding is closed. The entry now names four rounds, round 3's finding on DPL-002 and the round-4 recheck, and the close-out E2E run at 642b840 (120/120).
- **Evidence:** implementation_log.md:29-37.
- **Failure scenario:** None remains.

#### R3-4 (advisory) — `docs/slices/agentic-sdlc-poc/benchmark_report.md:123`

- **Problem:** Answer accepted; the finding is closed. The quota row now gives a source for each figure: 20% from the attempt log after review round 2, 22% at the first benchmark call, 35% after the last; weekly 2% to 4%.
- **Evidence:** benchmark_report.md:123-124. These figures match what I verified against benchmark_results.jsonl in round 3.
- **Failure scenario:** None remains.


The review ended after round 4: every finding is fixed or accepted, and no blocking finding is open.

