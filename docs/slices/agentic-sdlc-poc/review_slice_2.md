# Review record — agentic-sdlc-poc slice 2 (review launcher and benchmark)

Implementation review of slice 2 of the [plan](plan.md), on the branch `poc/slice-2-review-launcher`,
which is built on slice 1 (`poc/slice-1-rules`) until slice 1 merges. The reviews ran through the new
launcher, `scripts/run_independent_review.py`; each attempt is in
[`review_attempts.jsonl`](review_attempts.jsonl) (unit `slice_2`), which holds the reviewed commit,
the base commit, the hashes of the rules, the task prompt, the full prompt, the paths under review,
the withheld files and the report, and the usage figures. This record keeps every task prompt and
every released report verbatim, each with its SHA-256, which matches the attempt log, and the author's
answers. Rounds 1 and 2 reviewed the code, rounds 3 and 4 the
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

### Task prompt (verbatim, SHA-256 `74835d84064fa14b40387fa352d153ab6d140ae5ca3578cf4ab48b105fc6b2d3`)

`````text
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
`````

### Report (rendered from the released JSON, which follows it verbatim)

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

<details><summary>Released report JSON (verbatim, SHA-256 <code>c9c6d6830d424d78ea2709bf3b010fc1274eaf76df5d452a524720cd00a3e14b</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "run_canary: `\"passed\": flagged[\"status\"] != \"budget\" and not _followed_any(flagged)`. canary_outcome: `findings = (outcome.report or {}).get(\"findings\", [])`. classify() returns CallOutcome(\"failed\", ..., report=None) for any outside call (run_independent_review.py:497-498). _outside_reads gives `allowed = reads - denied`, so a denied read gives allowed 0, and `outside_read_denied` is recorded but never used in `passed`. No test covers run_canary's passed/valid logic: only twin_invocation and canary_outcome on a stub are tested.",
      "failure_scenario": "A later CLI version (the test plan reruns the canary whenever the CLI version changes) loads the hostile CLAUDE.md despite --safe-mode. The reviewer adds the CANARY-BRAVO finding and tries to Read the outside marker, as CLAUDE.md tells it to. dontAsk denies the read, so classify marks the run \"failed\" for an outside call and drops the report, and with it the CANARY-BRAVO finding. hook_ran stays false because settings are still excluded, and outside_read_allowed is 0. The result says passed=true, and the report states that branch instructions did not reach the reviewer, which is the opposite of what happened. A usage-limit pause or a provider error on the flagged call likewise yields passed=true without any review. The plan uses the canary instead of the separate confinement live check, so this is the slice's only evidence for confinement.",
      "file": "scripts/run_review_benchmark.py",
      "id": "B1",
      "kind": "blocking",
      "line": 346,
      "problem": "The canary counts as passed whenever the flagged run did not return status \"budget\" and _followed_any() is false. It never requires the flagged run to have completed, and it ignores denied reads of the outside marker. Followed instruction IDs are taken only from outcome.report, which is None for every non-completed run. So a run that failed, was paused or is pending is reported as a passed canary. A run that followed a leaked CLAUDE.md instruction and was then failed for its outside read is also reported as passed."
    },
    {
      "evidence": "`budget = Budget(budget_limit)` is created in each run_benchmark call; nothing counts the calls already in RESULTS_FILE. review_with_retries breaks on any status other than provider_error, and run_benchmark goes on to the next item, so \"paused\" stops nothing. `_completed_reviews` builds a dict keyed by (case, prompt), so a later line overwrites an earlier one. The test plan's live check says the benchmark 'runs within its budget, or stops at a usage limit and resumes after the reset'. test_run_stops_at_the_budget_counting_retries checks only a single invocation.",
      "failure_scenario": "Stage A hits the 5-hour limit at case 6. Cases 6 to 11 each burn one call on a paused attempt until the 26 calls are used, so they become incomplete. To 'resume after the reset', the author runs --run again. All 12 cases run again from the start, up to 26 more calls (52 in total) without the user's decision, and the comparison uses whichever result was written last. The budget gate passes its test, but the approved cap is exceeded and the paired results can come from different runs.",
      "file": "scripts/run_review_benchmark.py",
      "id": "B2",
      "kind": "blocking",
      "line": 393,
      "problem": "The approved budget of 26 reviewer calls (POC-D10) is enforced only inside one invocation, by an in-memory Budget object. The runner does not stop at a usage limit, and it cannot resume. A paused call consumes budget and the run moves on to the next case, so after a limit is hit the rest of the budget goes on paused calls. Running --run again re-runs every case with a fresh budget of 26 and appends duplicate results. compare_prompts then silently keeps the last result per (case, prompt)."
    },
    {
      "evidence": "The `recomputed` dict has no full_prompt_sha256 and no diff_sha256 key. The start entry records both (start_entry, line 685-686).",
      "failure_scenario": "A later edit to build_prompt changes the text the reviewer receives. Rebuilding an old entry reports no mismatches, so 'the exact invocation can be rebuilt' (success criterion) holds for the argv but not for the stdin.",
      "file": "scripts/run_independent_review.py",
      "id": "A1",
      "kind": "advisory",
      "line": 817,
      "problem": "invocation_from_entry rebuilds only the argv and the hashes of the rules, the prompt file, the paths, the withheld files, the schema and the tree. It does not rebuild the full prompt sent on stdin, and it does not check full_prompt_sha256 or diff_sha256, although every input needed to rebuild them is in the entry."
    },
    {
      "evidence": "_current_count returns count+1 on every invocation that carries a reset. admit_round checks only `round_no > ROUND_LIMIT and extension is None`. Neither looks at the references already in the log.",
      "failure_scenario": "After a reset, a provider error fails one reviewer in round 1 of count 2. The author re-runs the same command line, --reset included. Count 3 starts and every reviewer runs again, so one user act has produced two restarts. Likewise, the extension URL required for round 5 also admits rounds 6 and 7. Both are recorded in the log, but the launcher's admission does not catch them.",
      "file": "scripts/run_independent_review.py",
      "id": "A2",
      "kind": "advisory",
      "line": 603,
      "problem": "Nothing stops a user's reset or extension reference from being reused. Passing the same --reset again on a later round-1 invocation starts yet another count. One --extension URL admits round 5 and every round after it."
    },
    {
      "evidence": "_guarded_attempts returns \"withheld\" only to stdout and stderr. The test test_secret_in_the_reply_leaves_no_report_and_no_end_entry confirms there is no end entry. recover() then appends interrupted with a fixed reason.",
      "failure_scenario": "A slice-6 review-record check, or the user, reads the log and concludes the launcher crashed. The real cause, a secret-shaped reply, does not appear in the record.",
      "file": "scripts/run_independent_review.py",
      "id": "A3",
      "kind": "advisory",
      "line": 567,
      "problem": "When the publication check withholds a report, the start entry is left with no end entry. On the next invocation, recover() records that attempt as \"interrupted\" with the reason 'the launcher stopped during the attempt'. That is false, and the authoritative log never shows that the publication check fired."
    },
    {
      "evidence": "RM-3 locations use [[0, 100000]]. RM-2 has ranges [[1240, 2000]] and terms [evidence, ...]. PD-1 terms include `any`. decide() is fed totals from `len(result[\"detected\"])`.",
      "failure_scenario": "An unrelated blocking finding in docs/slices/agentic-delivery-process/test_plan.md that mentions 'trace' counts as detecting DPL-004. If the report prints the automatic decision without re-applying it after hand confirmation, the prompt choice can rest on false detections.",
      "file": "tests/review_benchmark/answer_key.yaml",
      "id": "A4",
      "kind": "advisory",
      "line": 66,
      "problem": "Some expected findings are scored loosely. RM-3 accepts any line (0 to 100000) of trace/tests.yaml or the test plan, with very common terms (proof, trace, e2e). RM-2 accepts 760 lines of the harness with the term \"evidence\". PD-1 accepts \"any\". compare_prompts/decide applies the decision rule to these automatic detections, not to the hand-confirmed ones the plan describes."
    },
    {
      "evidence": "settings = {\"permissions\": {\"allow\": [f\"Read({outside})\"]}}. The case paths are AGENTS.md, CLAUDE.md, scripts/CLAUDE.md, tests/unit/AGENTS.md and .claude/settings.json. The plan's environment facts say the allow rule never opened the outside file.",
      "failure_scenario": "The 'settings reach the reviewer' half of the canary can rest only on the hook, and the twin's validity can come from prompt injection through file content rather than from the CLI loading the files. So the canary does not cleanly show what it claims to show.",
      "file": "scripts/run_review_benchmark.py",
      "id": "A5",
      "kind": "advisory",
      "line": 154,
      "problem": "The canary's allow rule `Read(<absolute path>)` is probably not an absolute-path rule in Claude Code's permission syntax: a single leading slash is read relative to the settings file, and an absolute path needs '//'. That would explain the probe result 'the project allow rule did not open the outside file in any run'. Also, the hostile instruction files are themselves the paths under review, so a twin that 'follows' them may have taken them from data rather than from instruction loading."
    },
    {
      "evidence": "`root = os.path.normpath(str(copy_root))`, with no realpath on copy_root. The environment facts say the CLI passes absolute paths in tool inputs.",
      "failure_scenario": "On macOS with Rancher Desktop, every launcher review ends as 'failed: a call named a path outside the copy'.",
      "file": "scripts/run_independent_review.py",
      "id": "A6",
      "kind": "advisory",
      "line": 387,
      "problem": "relative_to_copy compares lexically normalised paths against the mkdtemp path without resolving symlinks. On macOS, a supported environment, the temp directory /var/folders/... is reached through a symlink to /private/var/...; if the CLI reports the resolved path, every absolute Read inside the copy counts as outside and every review fails. This fails closed, so it is not a false green."
    },
    {
      "evidence": "No benchmark test asserts on PreparedCase.rules_text for the case commit. test_run_stops_at_the_budget_counting_retries covers only the budget status. test_killed_launcher... kills during `sleep: 30`, before any output.",
      "failure_scenario": "A regression where prepare_case takes the rules from the wrong commit, for example from the planted commit with the canary's hostile AGENTS.md, passes every test.",
      "file": "tests/tools/test_run_review_benchmark.py",
      "id": "A7",
      "kind": "advisory",
      "line": 223,
      "problem": "Some test-plan rows are only partly tested. Benchmark 'Approved rules': nothing checks that a case gets the rules at its own commit, or at its base for planted and canary cases. Budget: incomplete cases are tested only for the budget cap, not for pending or failed. Interruption: nothing tests a kill after the partial report is written but before the end entry; the kill test stops the launcher while the fake is still sleeping, before any reply."
    },
    {
      "evidence": "The function returns statuses paused, provider_error and failed, never \"interrupted\".",
      "failure_scenario": "A maintainer assumes this function produces the \"interrupted\" log status and edits the wrong place.",
      "file": "scripts/run_independent_review.py",
      "id": "A8",
      "kind": "advisory",
      "line": 478,
      "problem": "POC-D7 naming: _interrupted_call handles usage-limit pauses, provider errors and missing results. \"interrupted\" is also the log status for a killed launcher, so the name suggests the wrong thing."
    },
    {
      "evidence": "RESULTS_FILE = Path(\"docs/slices/agentic-sdlc-poc/benchmark_results.jsonl\"). result_line and run_canary have no cli_version field.",
      "failure_scenario": "The report cannot show which CLI version the canary was valid for, and an unplanned record joins the slice bundle.",
      "file": "scripts/run_review_benchmark.py",
      "id": "A9",
      "kind": "advisory",
      "line": 39,
      "problem": "The runner writes a new committed record, docs/slices/agentic-sdlc-poc/benchmark_results.jsonl, holding every reviewer's full findings text. The plan names only benchmark_report.md. Result lines also lack the CLI version, so a canary result cannot be tied to the CLI version it held for, which the 'rerun when the CLI version changes' live check needs."
    }
  ],
  "verdict": "no"
}
`````

</details>

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

### Task prompt (verbatim, SHA-256 `0bff6fe08d52b444bbc6740e055b5f27d718d7b27b004655383a6c8596f9038a`)

`````text
This is review round 2 of the implementation review of slice 2 of the agentic-SDLC PoC: a focused recheck by the original reviewer. Your round-1 report and the author's answers are below; check each answer against the change (the diff in _review_inputs/change.diff now covers round 1's commit and the fixes). Under the approved rules, from round 2 a new finding counts only if it blocks, except simpler alternatives and decision concerns.

The intent is unchanged: docs/slices/agentic-sdlc-poc/plan.md, "Slice 2 — Review launcher and benchmark", with its test plan. The benchmark has still not been run.

## Your round-1 report (verbatim JSON)

{
  "findings": [
    {
      "evidence": "run_canary: `\"passed\": flagged[\"status\"] != \"budget\" and not _followed_any(flagged)`. canary_outcome: `findings = (outcome.report or {}).get(\"findings\", [])`. classify() returns CallOutcome(\"failed\", ..., report=None) for any outside call (run_independent_review.py:497-498). _outside_reads gives `allowed = reads - denied`, so a denied read gives allowed 0, and `outside_read_denied` is recorded but never used in `passed`. No test covers run_canary's passed/valid logic: only twin_invocation and canary_outcome on a stub are tested.",
      "failure_scenario": "A later CLI version (the test plan reruns the canary whenever the CLI version changes) loads the hostile CLAUDE.md despite --safe-mode. The reviewer adds the CANARY-BRAVO finding and tries to Read the outside marker, as CLAUDE.md tells it to. dontAsk denies the read, so classify marks the run \"failed\" for an outside call and drops the report, and with it the CANARY-BRAVO finding. hook_ran stays false because settings are still excluded, and outside_read_allowed is 0. The result says passed=true, and the report states that branch instructions did not reach the reviewer, which is the opposite of what happened. A usage-limit pause or a provider error on the flagged call likewise yields passed=true without any review. The plan uses the canary instead of the separate confinement live check, so this is the slice's only evidence for confinement.",
      "file": "scripts/run_review_benchmark.py",
      "id": "B1",
      "kind": "blocking",
      "line": 346,
      "problem": "The canary counts as passed whenever the flagged run did not return status \"budget\" and _followed_any() is false. It never requires the flagged run to have completed, and it ignores denied reads of the outside marker. Followed instruction IDs are taken only from outcome.report, which is None for every non-completed run. So a run that failed, was paused or is pending is reported as a passed canary. A run that followed a leaked CLAUDE.md instruction and was then failed for its outside read is also reported as passed."
    },
    {
      "evidence": "`budget = Budget(budget_limit)` is created in each run_benchmark call; nothing counts the calls already in RESULTS_FILE. review_with_retries breaks on any status other than provider_error, and run_benchmark goes on to the next item, so \"paused\" stops nothing. `_completed_reviews` builds a dict keyed by (case, prompt), so a later line overwrites an earlier one. The test plan's live check says the benchmark 'runs within its budget, or stops at a usage limit and resumes after the reset'. test_run_stops_at_the_budget_counting_retries checks only a single invocation.",
      "failure_scenario": "Stage A hits the 5-hour limit at case 6. Cases 6 to 11 each burn one call on a paused attempt until the 26 calls are used, so they become incomplete. To 'resume after the reset', the author runs --run again. All 12 cases run again from the start, up to 26 more calls (52 in total) without the user's decision, and the comparison uses whichever result was written last. The budget gate passes its test, but the approved cap is exceeded and the paired results can come from different runs.",
      "file": "scripts/run_review_benchmark.py",
      "id": "B2",
      "kind": "blocking",
      "line": 393,
      "problem": "The approved budget of 26 reviewer calls (POC-D10) is enforced only inside one invocation, by an in-memory Budget object. The runner does not stop at a usage limit, and it cannot resume. A paused call consumes budget and the run moves on to the next case, so after a limit is hit the rest of the budget goes on paused calls. Running --run again re-runs every case with a fresh budget of 26 and appends duplicate results. compare_prompts then silently keeps the last result per (case, prompt)."
    },
    {
      "evidence": "The `recomputed` dict has no full_prompt_sha256 and no diff_sha256 key. The start entry records both (start_entry, line 685-686).",
      "failure_scenario": "A later edit to build_prompt changes the text the reviewer receives. Rebuilding an old entry reports no mismatches, so 'the exact invocation can be rebuilt' (success criterion) holds for the argv but not for the stdin.",
      "file": "scripts/run_independent_review.py",
      "id": "A1",
      "kind": "advisory",
      "line": 817,
      "problem": "invocation_from_entry rebuilds only the argv and the hashes of the rules, the prompt file, the paths, the withheld files, the schema and the tree. It does not rebuild the full prompt sent on stdin, and it does not check full_prompt_sha256 or diff_sha256, although every input needed to rebuild them is in the entry."
    },
    {
      "evidence": "_current_count returns count+1 on every invocation that carries a reset. admit_round checks only `round_no > ROUND_LIMIT and extension is None`. Neither looks at the references already in the log.",
      "failure_scenario": "After a reset, a provider error fails one reviewer in round 1 of count 2. The author re-runs the same command line, --reset included. Count 3 starts and every reviewer runs again, so one user act has produced two restarts. Likewise, the extension URL required for round 5 also admits rounds 6 and 7. Both are recorded in the log, but the launcher's admission does not catch them.",
      "file": "scripts/run_independent_review.py",
      "id": "A2",
      "kind": "advisory",
      "line": 603,
      "problem": "Nothing stops a user's reset or extension reference from being reused. Passing the same --reset again on a later round-1 invocation starts yet another count. One --extension URL admits round 5 and every round after it."
    },
    {
      "evidence": "_guarded_attempts returns \"withheld\" only to stdout and stderr. The test test_secret_in_the_reply_leaves_no_report_and_no_end_entry confirms there is no end entry. recover() then appends interrupted with a fixed reason.",
      "failure_scenario": "A slice-6 review-record check, or the user, reads the log and concludes the launcher crashed. The real cause, a secret-shaped reply, does not appear in the record.",
      "file": "scripts/run_independent_review.py",
      "id": "A3",
      "kind": "advisory",
      "line": 567,
      "problem": "When the publication check withholds a report, the start entry is left with no end entry. On the next invocation, recover() records that attempt as \"interrupted\" with the reason 'the launcher stopped during the attempt'. That is false, and the authoritative log never shows that the publication check fired."
    },
    {
      "evidence": "RM-3 locations use [[0, 100000]]. RM-2 has ranges [[1240, 2000]] and terms [evidence, ...]. PD-1 terms include `any`. decide() is fed totals from `len(result[\"detected\"])`.",
      "failure_scenario": "An unrelated blocking finding in docs/slices/agentic-delivery-process/test_plan.md that mentions 'trace' counts as detecting DPL-004. If the report prints the automatic decision without re-applying it after hand confirmation, the prompt choice can rest on false detections.",
      "file": "tests/review_benchmark/answer_key.yaml",
      "id": "A4",
      "kind": "advisory",
      "line": 66,
      "problem": "Some expected findings are scored loosely. RM-3 accepts any line (0 to 100000) of trace/tests.yaml or the test plan, with very common terms (proof, trace, e2e). RM-2 accepts 760 lines of the harness with the term \"evidence\". PD-1 accepts \"any\". compare_prompts/decide applies the decision rule to these automatic detections, not to the hand-confirmed ones the plan describes."
    },
    {
      "evidence": "settings = {\"permissions\": {\"allow\": [f\"Read({outside})\"]}}. The case paths are AGENTS.md, CLAUDE.md, scripts/CLAUDE.md, tests/unit/AGENTS.md and .claude/settings.json. The plan's environment facts say the allow rule never opened the outside file.",
      "failure_scenario": "The 'settings reach the reviewer' half of the canary can rest only on the hook, and the twin's validity can come from prompt injection through file content rather than from the CLI loading the files. So the canary does not cleanly show what it claims to show.",
      "file": "scripts/run_review_benchmark.py",
      "id": "A5",
      "kind": "advisory",
      "line": 154,
      "problem": "The canary's allow rule `Read(<absolute path>)` is probably not an absolute-path rule in Claude Code's permission syntax: a single leading slash is read relative to the settings file, and an absolute path needs '//'. That would explain the probe result 'the project allow rule did not open the outside file in any run'. Also, the hostile instruction files are themselves the paths under review, so a twin that 'follows' them may have taken them from data rather than from instruction loading."
    },
    {
      "evidence": "`root = os.path.normpath(str(copy_root))`, with no realpath on copy_root. The environment facts say the CLI passes absolute paths in tool inputs.",
      "failure_scenario": "On macOS with Rancher Desktop, every launcher review ends as 'failed: a call named a path outside the copy'.",
      "file": "scripts/run_independent_review.py",
      "id": "A6",
      "kind": "advisory",
      "line": 387,
      "problem": "relative_to_copy compares lexically normalised paths against the mkdtemp path without resolving symlinks. On macOS, a supported environment, the temp directory /var/folders/... is reached through a symlink to /private/var/...; if the CLI reports the resolved path, every absolute Read inside the copy counts as outside and every review fails. This fails closed, so it is not a false green."
    },
    {
      "evidence": "No benchmark test asserts on PreparedCase.rules_text for the case commit. test_run_stops_at_the_budget_counting_retries covers only the budget status. test_killed_launcher... kills during `sleep: 30`, before any output.",
      "failure_scenario": "A regression where prepare_case takes the rules from the wrong commit, for example from the planted commit with the canary's hostile AGENTS.md, passes every test.",
      "file": "tests/tools/test_run_review_benchmark.py",
      "id": "A7",
      "kind": "advisory",
      "line": 223,
      "problem": "Some test-plan rows are only partly tested. Benchmark 'Approved rules': nothing checks that a case gets the rules at its own commit, or at its base for planted and canary cases. Budget: incomplete cases are tested only for the budget cap, not for pending or failed. Interruption: nothing tests a kill after the partial report is written but before the end entry; the kill test stops the launcher while the fake is still sleeping, before any reply."
    },
    {
      "evidence": "The function returns statuses paused, provider_error and failed, never \"interrupted\".",
      "failure_scenario": "A maintainer assumes this function produces the \"interrupted\" log status and edits the wrong place.",
      "file": "scripts/run_independent_review.py",
      "id": "A8",
      "kind": "advisory",
      "line": 478,
      "problem": "POC-D7 naming: _interrupted_call handles usage-limit pauses, provider errors and missing results. \"interrupted\" is also the log status for a killed launcher, so the name suggests the wrong thing."
    },
    {
      "evidence": "RESULTS_FILE = Path(\"docs/slices/agentic-sdlc-poc/benchmark_results.jsonl\"). result_line and run_canary have no cli_version field.",
      "failure_scenario": "The report cannot show which CLI version the canary was valid for, and an unplanned record joins the slice bundle.",
      "file": "scripts/run_review_benchmark.py",
      "id": "A9",
      "kind": "advisory",
      "line": 39,
      "problem": "The runner writes a new committed record, docs/slices/agentic-sdlc-poc/benchmark_results.jsonl, holding every reviewer's full findings text. The plan names only benchmark_report.md. Result lines also lack the CLI version, so a canary result cannot be tied to the CLI version it held for, which the 'rerun when the CLI version changes' live check needs."
    }
  ],
  "verdict": "no"
}

## The author's answers

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

Local: `make tooling-test` passes (327 pytest, 9 shell). Deliberately breaking the canary pass rule, the budget carried across runs, the stop at a pause, and the skip of finished cases makes a test fail each time.

## Questions to answer

1. For each finding, accept the answer or re-raise it with new evidence.
2. Did the fixes introduce a blocking problem (a false green, a contradiction, a broken test)?
`````

### Report (rendered from the released JSON, which follows it verbatim)

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

<details><summary>Released report JSON (verbatim, SHA-256 <code>dbbebbaba4c9c9e1b8c12a91d20576547a445bf7a54d27173f89fc77b2a18623</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "run_canary: `passed = flagged['status'] == 'completed' and not _followed_any(flagged)`. canary_outcome reads `launcher.structured_reply(summary.result)` directly. _followed_any includes outside_reads_denied. Tests: test_canary_does_not_pass_without_a_completed_clean_run (cases paused, escaped-and-failed, followed), test_canary_counts_denied_reads_of_the_outside_marker, test_canary_passes_only_when_its_run_completed_without_following.",
      "failure_scenario": "None left. The round-1 scenario (a CLAUDE.md leak followed by a denied outside read, with the run marked failed) now gives passed=false, and so do a paused run and a provider error.",
      "file": "scripts/run_review_benchmark.py",
      "id": "B1",
      "kind": "advisory",
      "line": 407,
      "problem": "Re-check of B1: accepted, fixed. The canary now passes only when the flagged run is 'completed' and none of the follow signals fired. The signals are planted finding IDs, the hook file, and reads of the outside marker, whether the read was allowed or denied. Finding IDs are now read from the stream's structured reply, so they are counted even when classify() drops the report."
    },
    {
      "evidence": "RunState.take checks used >= limit. review_with_retries loops while `not state.paused.is_set() and state.take()`. run_benchmark breaks when paused. Tests: test_a_usage_limit_stops_the_run_and_a_rerun_resumes_within_the_budget (4 calls, then 6), test_a_rerun_after_the_budget_is_spent_makes_no_call (26 calls, then still 26).",
      "failure_scenario": "None left. Resuming after a reset can no longer go over 26 calls, and it cannot pair results from duplicate runs.",
      "file": "scripts/run_review_benchmark.py",
      "id": "B2",
      "kind": "advisory",
      "line": 297,
      "problem": "Re-check of B2: accepted, fixed. previous_state adds up the 'calls' of every recorded line for the same answer key and seeds RunState with that total, so the 26-call cap now holds across invocations. Finished reviews are skipped per case and prompt. A pause sets state.paused: retries stop, and the case loop stops before the next case. _completed_reviews keeps the first completed result."
    },
    {
      "evidence": "invocation_from_entry: `build_prompt(inputs, ..., True)`. main uses `ctx.extra['diff_sha'] is not None`.",
      "failure_scenario": "Rebuilding an entry recorded without a diff reports a false full_prompt_sha256 mismatch. Nothing passes falsely.",
      "file": "scripts/run_independent_review.py",
      "id": "A1",
      "kind": "advisory",
      "line": 847,
      "problem": "Accepted. diff_sha256 and full_prompt_sha256 are now rebuilt and compared. One small leftover: the rebuild always passes has_diff=True, so an entry recorded without a diff would show a false full_prompt mismatch. That fails loudly, not green, so it is not blocking."
    },
    {
      "evidence": "_check_references_unused; test_a_reference_admits_once.",
      "failure_scenario": "None.",
      "file": "scripts/run_independent_review.py",
      "id": "A2",
      "kind": "advisory",
      "line": 609,
      "problem": "Accepted. A reset reference that is already in the log is refused. An extension reference that already admitted a different round is refused, while re-running the same round with it is still allowed."
    },
    {
      "evidence": "recover reason: 'no end entry: the launcher stopped, or the publication check withheld the report'.",
      "failure_scenario": "None.",
      "file": "scripts/run_independent_review.py",
      "id": "A3",
      "kind": "advisory",
      "line": 573,
      "problem": "Accepted. The approved test plan requires that a withheld report leaves no log entry. The interrupted reason now names the publication check as a possible cause, so the log no longer states something false."
    },
    {
      "evidence": "Author's answer and the updated answer key. The benchmark has not run yet.",
      "failure_scenario": "None.",
      "file": "tests/review_benchmark/answer_key.yaml",
      "id": "A4",
      "kind": "advisory",
      "line": 0,
      "problem": "Accepted. The overly common terms are gone. The author says the report labels the automatic comparison as coming before hand confirmation and applies the decision rule again to the confirmed detections. The answer key changed before any run."
    },
    {
      "evidence": "test_real_miss_gets_the_rules_of_its_commit_and_the_canary_those_of_its_base asserts `startswith('Read(//')`, CANARY- absent from rules_text and from the diff, and present in CLAUDE.md.",
      "failure_scenario": "None.",
      "file": "scripts/run_review_benchmark.py",
      "id": "A5",
      "kind": "advisory",
      "line": 0,
      "problem": "Accepted. The allow rule now uses `Read(//...)`. The hostile files are committed in the base, and the change under review is a README edit, so the twin has to load or look for them. The test confirms that the diff and the rules contain no CANARY- text."
    },
    {
      "evidence": "relative_to_copy; test_symlinked_copy_root_still_counts_reads_inside_the_copy.",
      "failure_scenario": "None.",
      "file": "scripts/run_independent_review.py",
      "id": "A6",
      "kind": "advisory",
      "line": 394,
      "problem": "Accepted. The root and each path are resolved with realpath before they are compared."
    },
    {
      "evidence": "The tests named in the author's answer exist at the lines shown.",
      "failure_scenario": "None.",
      "file": "tests/tools/test_run_review_benchmark.py",
      "id": "A7",
      "kind": "advisory",
      "line": 326,
      "problem": "Accepted. There are now tests for the rules each case kind receives, for a case left incomplete by a failed review, and for a partial report left without an end entry."
    },
    {
      "evidence": "Author's answer.",
      "failure_scenario": "None.",
      "file": "scripts/run_independent_review.py",
      "id": "A8",
      "kind": "advisory",
      "line": 0,
      "problem": "Accepted. The function is renamed to _paused_or_unfinished_call."
    },
    {
      "evidence": "result_line and run_canary include cli_version. append_result calls check_publishable.",
      "failure_scenario": "None.",
      "file": "scripts/run_review_benchmark.py",
      "id": "A9",
      "kind": "advisory",
      "line": 338,
      "problem": "Accepted. The results file is needed to resume within the budget and to refuse results from another answer key. Each line goes through the publication check before it is written. Result lines and canary lines now record cli_version."
    }
  ],
  "verdict": "yes"
}
`````

</details>

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

### Task prompt (verbatim, SHA-256 `07c8bad50c40bf3ed8e5610f409895d1330ee6b98894844ce105cba6f077bad5`)

Attempt 2; attempt 1 is in the collapsed block after it.

`````text
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
`````

<details><summary>Attempt 1 task prompt (verbatim, SHA-256 <code>de09babcf4119ba368724976b5dddb6f62dbd37473ccc6601ff3fe1c63f4a44a</code>)</summary>

`````text
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
`````

</details>

### Report (rendered from the released JSON, which follows it verbatim)

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

<details><summary>Released report JSON (verbatim, SHA-256 <code>b46983b24b67780772c7742749bcc80eb4f23d3060a1c9e2062c1c00d342136f</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "In benchmark_results.jsonl line 3 (RM-2, short), finding F8 is kind \"advisory\" at scripts/rogue_node_tests.sh:1604, inside the key's range 1240\u20132000. Its problem says \"M3 tests also write live biscuit bearer tokens to token.txt and into cmd_exercise_*.txt\". Its failure scenario says \"Capability tokens also end up in the same uploaded artifacts\". It contains the key term \"plaintext\". That is DPL-002 as the answer key describes it: token values written into E2E evidence. The score shows advisory_only: [] only because of how scripts/run_review_benchmark.py:_expected_outcome (lines 246\u2013253) works. It returns \"location_only\" whenever any blocking finding sits at the location (F3 here). An advisory finding with a key term is then never reported. The hand triage looked only at F3 and missed F8.",
      "failure_scenario": "The user decides slice 4 and stage B from this report. Recommendation 3 sends the work to new review questions for DPL-002. The real gap is severity calibration: the reviewer found the leak and labelled it advisory. That calls for a different fix, such as a rule that a secret in evidence is blocking. The slice-4 measurement on RM-2 would then target the wrong cause.",
      "file": "docs/slices/agentic-sdlc-poc/benchmark_report.md",
      "id": "R3-1",
      "kind": "blocking",
      "line": 72,
      "problem": "The RM-2 row says \"Neither prompt saw token values written to evidence\". The results file shows otherwise. The short-prompt review reported the DPL-002 defect, but as an advisory finding. Recommendation 3 (line 137\u2013142) repeats the false claim: it says the reviewer found \"none of\" DPL-002 and that \"neither prompt asked about them\". So does the implementation-log entry (\"defects of absence, which neither prompt found\"). The counts and the decision rule are unaffected, because only blocking findings count as detections. The diagnosis behind recommendation 3 is wrong for DPL-002: the reviewer saw the leak but rated it advisory. A missing review question was not the cause."
    },
    {
      "evidence": "_expected_outcome returns \"location_only\" if `blocking` is non-empty. It checks advisory findings with terms only when there is no blocking finding at the location.",
      "failure_scenario": "In future runs, hand triage that follows the automatic columns can again miss a defect the reviewer reported only as advisory.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R3-2",
      "kind": "advisory",
      "line": 251,
      "problem": "The automatic score hides an advisory-only match whenever any blocking finding without a key term sits at the same location. The report's \"Location only\" column therefore cannot show that an advisory finding named the defect. This caused R3-1."
    },
    {
      "evidence": "The diff adds \"Review: two rounds through the launcher \u2026 round 2 accepted every answer.\" The task states this is round 3.",
      "failure_scenario": "The history records fewer review rounds than actually ran, and does not mention this round's findings.",
      "file": "docs/history/implementation_log.md",
      "id": "R3-3",
      "kind": "advisory",
      "line": 72,
      "problem": "The 2026-11-08 entry says the review had two rounds and that \"round 2 accepted every answer\". Round 3 (this focused review of the report and close-out) is now running, so the entry will be out of date once round 3 ends."
    },
    {
      "evidence": "In benchmark_results.jsonl, line 1 has utilization five_hour 0.22, and lines 22\u201323 have 0.35 and seven_day 0.04.",
      "failure_scenario": "A reader cannot check the \"before\" quota figure against the committed record. It is minor.",
      "file": "docs/slices/agentic-sdlc-poc/benchmark_report.md",
      "id": "R3-4",
      "kind": "advisory",
      "line": 123,
      "problem": "The results file cannot confirm \"20% before the run\". Its first recorded five-hour utilization is 0.22, and the weekly figure is 0.02 from the first call. The \"after\" values (35%, 4%) match the last line. Everything else I checked against the results file matches: 24 calls, durations 13\u2013251 s, 189,149 output tokens, 1,003\u201322,320 tokens per review, USD 13.27 total, the canary valid and passed, hook_ran false and true, 5 failed reviews under the empty-review rule, and the confirmations for RM-1, PD-1 to PD-4 and CL-2."
    }
  ],
  "verdict": "no"
}
`````

</details>

### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| R3-1 | Fixed. The RM-2 row now says the short-prompt reviewer saw DPL-002 (F8, advisory, `scripts/rogue_node_tests.sh:1604`) and rated it advisory, so it is not a detection, and that the automatic score hid F8. Recommendation 3 separates the two defects of absence neither prompt found (DPL-004, DPL-005) from DPL-002, which is a severity question: under coding rule 1, a secret in published evidence is blocking. It proposes review questions for the first and a severity rule for the second. The implementation-log entry says the same. Counts and the decision rule are unchanged (1 of 4 real misses for each prompt). | `benchmark_report.md` hand-confirmation table and recommendation 3; `implementation_log.md` |
| R3-2 | Fixed at the origin. `score()` lists an expected finding under `advisory_only` whenever a non-blocking finding with a term sits at its location and it was not detected, including beside a blocking finding without a term. The stored results of this run keep the score of the code that produced them, and the report's hand triage records F8. | `_expected_labels`, `_seen_as_advisory`; test `test_advisory_finding_with_a_term_is_listed_even_beside_a_blocking_one_without` |
| R3-3 | Fixed. The entry names four rounds, round 3's failed first attempt and its finding, and the E2E result at the slice's close. | `implementation_log.md` |
| R3-4 | Fixed. The quota row says where each figure comes from: 20% after review round 2 (attempt log), 22% at the first benchmark call, 35% after the last; weekly 2% to 4%. | `benchmark_report.md`, Quota |

## Round 4 (focused recheck, medium effort; the last round the rules allow)

Reviewed commit `1481098`; attempt `slice_2/c1/r4/impl/1`, completed, verdict "yes" (17 seconds, 8 turns, 6 tool calls, 1,871 output tokens, CLI cost estimate USD 0.24; afterwards the 5-hour window stood at 38% and the weekly window at 4%).

### Task prompt (verbatim, SHA-256 `13288f0d20309acc673bbb82c3f8b678030438285a789193b70d09260bf2337f`)

`````text
This is review round 4 of the implementation review of slice 2 of the agentic-SDLC PoC: a focused recheck, by the original reviewer, of the author's answers to your round-3 findings on the benchmark report and the close-out documents. It is the last round the rules allow; after it, open blockers go to the user.

The intent is unchanged (docs/slices/agentic-sdlc-poc/plan.md, "Slice 2 — Review launcher and benchmark"). Open files by their path from the copy root; Markdown links are relative to the file that contains them.

## Your round-3 report (verbatim JSON)

{
  "findings": [
    {
      "evidence": "In benchmark_results.jsonl line 3 (RM-2, short), finding F8 is kind \"advisory\" at scripts/rogue_node_tests.sh:1604, inside the key's range 1240\u20132000. Its problem says \"M3 tests also write live biscuit bearer tokens to token.txt and into cmd_exercise_*.txt\". Its failure scenario says \"Capability tokens also end up in the same uploaded artifacts\". It contains the key term \"plaintext\". That is DPL-002 as the answer key describes it: token values written into E2E evidence. The score shows advisory_only: [] only because of how scripts/run_review_benchmark.py:_expected_outcome (lines 246\u2013253) works. It returns \"location_only\" whenever any blocking finding sits at the location (F3 here). An advisory finding with a key term is then never reported. The hand triage looked only at F3 and missed F8.",
      "failure_scenario": "The user decides slice 4 and stage B from this report. Recommendation 3 sends the work to new review questions for DPL-002. The real gap is severity calibration: the reviewer found the leak and labelled it advisory. That calls for a different fix, such as a rule that a secret in evidence is blocking. The slice-4 measurement on RM-2 would then target the wrong cause.",
      "file": "docs/slices/agentic-sdlc-poc/benchmark_report.md",
      "id": "R3-1",
      "kind": "blocking",
      "line": 72,
      "problem": "The RM-2 row says \"Neither prompt saw token values written to evidence\". The results file shows otherwise. The short-prompt review reported the DPL-002 defect, but as an advisory finding. Recommendation 3 (line 137\u2013142) repeats the false claim: it says the reviewer found \"none of\" DPL-002 and that \"neither prompt asked about them\". So does the implementation-log entry (\"defects of absence, which neither prompt found\"). The counts and the decision rule are unaffected, because only blocking findings count as detections. The diagnosis behind recommendation 3 is wrong for DPL-002: the reviewer saw the leak but rated it advisory. A missing review question was not the cause."
    },
    {
      "evidence": "_expected_outcome returns \"location_only\" if `blocking` is non-empty. It checks advisory findings with terms only when there is no blocking finding at the location.",
      "failure_scenario": "In future runs, hand triage that follows the automatic columns can again miss a defect the reviewer reported only as advisory.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R3-2",
      "kind": "advisory",
      "line": 251,
      "problem": "The automatic score hides an advisory-only match whenever any blocking finding without a key term sits at the same location. The report's \"Location only\" column therefore cannot show that an advisory finding named the defect. This caused R3-1."
    },
    {
      "evidence": "The diff adds \"Review: two rounds through the launcher \u2026 round 2 accepted every answer.\" The task states this is round 3.",
      "failure_scenario": "The history records fewer review rounds than actually ran, and does not mention this round's findings.",
      "file": "docs/history/implementation_log.md",
      "id": "R3-3",
      "kind": "advisory",
      "line": 72,
      "problem": "The 2026-11-08 entry says the review had two rounds and that \"round 2 accepted every answer\". Round 3 (this focused review of the report and close-out) is now running, so the entry will be out of date once round 3 ends."
    },
    {
      "evidence": "In benchmark_results.jsonl, line 1 has utilization five_hour 0.22, and lines 22\u201323 have 0.35 and seven_day 0.04.",
      "failure_scenario": "A reader cannot check the \"before\" quota figure against the committed record. It is minor.",
      "file": "docs/slices/agentic-sdlc-poc/benchmark_report.md",
      "id": "R3-4",
      "kind": "advisory",
      "line": 123,
      "problem": "The results file cannot confirm \"20% before the run\". Its first recorded five-hour utilization is 0.22, and the weekly figure is 0.02 from the first call. The \"after\" values (35%, 4%) match the last line. Everything else I checked against the results file matches: 24 calls, durations 13\u2013251 s, 189,149 output tokens, 1,003\u201322,320 tokens per review, USD 13.27 total, the canary valid and passed, hook_ran false and true, 5 failed reviews under the empty-review rule, and the confirmations for RM-1, PD-1 to PD-4 and CL-2."
    }
  ],
  "verdict": "no"
}

## The author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| R3-1 | Fixed. The RM-2 row now says the short-prompt reviewer saw DPL-002 (F8, advisory, `scripts/rogue_node_tests.sh:1604`) and rated it advisory, so it is not a detection, and that the automatic score hid F8. Recommendation 3 separates the two defects of absence neither prompt found (DPL-004, DPL-005) from DPL-002, which is a severity question: under coding rule 1, a secret in published evidence is blocking. It proposes review questions for the first and a severity rule for the second. The implementation-log entry says the same. Counts and the decision rule are unchanged (1 of 4 real misses for each prompt). | `benchmark_report.md` hand-confirmation table and recommendation 3; `implementation_log.md` |
| R3-2 | Fixed at the origin. `score()` lists an expected finding under `advisory_only` whenever a non-blocking finding with a term sits at its location and it was not detected, including beside a blocking finding without a term. The stored results of this run keep the score of the code that produced them, and the report's hand triage records F8. | `_expected_labels`, `_seen_as_advisory`; test `test_advisory_finding_with_a_term_is_listed_even_beside_a_blocking_one_without` |
| R3-3 | Fixed. The entry names four rounds, round 3's failed first attempt and its finding, and the E2E result at the slice's close. | `implementation_log.md` |
| R3-4 | Fixed. The quota row says where each figure comes from: 20% after review round 2 (attempt log), 22% at the first benchmark call, 35% after the last; weekly 2% to 4%. | `benchmark_report.md`, Quota |

Since round 3, the full E2E suite ran on a clean stack at `642b840`: 120/120 passed. `make qa-deploy` (image users inspected) and `make qa-evidence` passed after it. `make tooling-test` passes.

## Questions to answer

1. For each finding, accept the answer or re-raise it with new evidence.
2. Did the fixes introduce a blocking problem?
`````

### Report (rendered from the released JSON, which follows it verbatim)

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

<details><summary>Released report JSON (verbatim, SHA-256 <code>39da685c93491f9333649f24007b707c7a40664fd869897099542352b3da8ed2</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "benchmark_report.md:72 and :140-144; implementation_log.md:27 says 'DPL-002: seen, but rated advisory'. The decision-rule counts are unchanged (1 of 4 for each prompt), which is consistent with counting only blocking findings as detections.",
      "failure_scenario": "None remains. The diagnosis now matches the results file.",
      "file": "docs/slices/agentic-sdlc-poc/benchmark_report.md",
      "id": "R3-1",
      "kind": "advisory",
      "line": 72,
      "problem": "Answer accepted; the finding is closed. The RM-2 row now records F8 as seen but rated advisory, so it is not a detection. Recommendation 3 (lines 137\u2013145) separates DPL-004 and DPL-005, the defects of absence, from DPL-002, which it treats as a severity question. The implementation log (line 27) says the same."
    },
    {
      "evidence": "run_review_benchmark.py:245-256; tests/tools/test_run_review_benchmark.py:180-183 asserts location_only == ['E1'] and advisory_only == ['E1'] when a blocking finding without a term and an advisory finding with a term share the location.",
      "failure_scenario": "None remains. Future hand triage will see the advisory match in its own column.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R3-2",
      "kind": "advisory",
      "line": 249,
      "problem": "Answer accepted; the finding is closed. `_expected_labels` now adds 'advisory_only' whenever the outcome is not 'detected' and a non-blocking finding with a term sits at the location, including beside a blocking finding without a term. The new test covers exactly that case."
    },
    {
      "evidence": "implementation_log.md:29-37.",
      "failure_scenario": "None remains.",
      "file": "docs/history/implementation_log.md",
      "id": "R3-3",
      "kind": "advisory",
      "line": 29,
      "problem": "Answer accepted; the finding is closed. The entry now names four rounds, round 3's finding on DPL-002 and the round-4 recheck, and the close-out E2E run at 642b840 (120/120)."
    },
    {
      "evidence": "benchmark_report.md:123-124. These figures match what I verified against benchmark_results.jsonl in round 3.",
      "failure_scenario": "None remains.",
      "file": "docs/slices/agentic-sdlc-poc/benchmark_report.md",
      "id": "R3-4",
      "kind": "advisory",
      "line": 123,
      "problem": "Answer accepted; the finding is closed. The quota row now gives a source for each figure: 20% from the attempt log after review round 2, 22% at the first benchmark call, 35% after the last; weekly 2% to 4%."
    }
  ],
  "verdict": "yes"
}
`````

</details>

## Round 5 (extension, open mandate, high effort)

The owner asked for one more independent review before merging, from the angle of what a working
delivery process must catch ([extension on PR #35](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/pull/35#issuecomment-6723140659),
recorded in the attempt log). Unlike rounds 1 to 4, the task opened with an open mandate, gave the
coverage report and the list of never-reviewed files as evidence, and included this record and the
attempt log as of `568d7f1` (withheld from the copy, so no reviewer had checked them).

Reviewed commit `568d7f1`, base `poc/agentic-sdlc` at `c4f9ca2`; attempt
`slice_2/c1/r5/impl/1`: 443 seconds, 23 turns, 21 tool calls (all inside the copy, none
denied), 43,658 output tokens, CLI cost estimate USD 2.94; afterwards the 5-hour window stood at
11% and the weekly window at 6%. Status completed, verdict "no".

<details><summary>Task prompt (verbatim, SHA-256 <code>b44e6e395d890fce1ee0b23532cd214c7ce7b45e35739db6e5ef3d16f5b6753a</code>; it contains this record and the attempt log as of <code>568d7f1</code>)</summary>

`````text
## Your mandate

Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, untested, stale, overclaimed, unsafe or unclear, inside or outside the files listed under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and pointing that out is part of the task.

## The change

This is pull request #35: slice 2 of the agentic-SDLC PoC, "Review launcher and benchmark", into `poc/agentic-sdlc`. Slice 1 (the rules) is already merged there. The approved plan is docs/slices/agentic-sdlc-poc/plan.md ("Slice 2 — Review launcher and benchmark", the decisions POC-D1 to POC-D16, "Assets and holders", "Hidden-state and trust decisions", "Checks this plan adds"). The approved test plan is docs/slices/agentic-sdlc-poc/test_plan.md. _review_inputs/change.diff is the whole change. The owner is about to merge it.

This is round 5, an extension the owner asked for. Rounds 1 to 4 reviewed the code (rounds 1 and 2) and the benchmark report and close-out (rounds 3 and 4). Their full history is below. Since then the owner found a miss nobody caught: the launcher's defensive refusal paths (for example refusing when AGENTS.md is missing on the base, an invalid base-branch name, a path under review missing at the commit, an invalid record path) have no tests. Three causes: the tests were derived only from the test plan's rows, coverage was not measured, and round 1's prompt asked a closed question ("name any test-plan row that has no test"). The owner's principle for the delivery process: "each steps should think for themselfs and add anything that is missing, flag that is wrong and orchestrator narrow prompts should not steer the agents narrowly."

## Known and recorded (do not report these again unless you find something new about them)

- The untested refusal paths above. The owner chose not to fix them in this PR; the lesson goes to slice 4 (issue #33).
- The tests use fake CLIs. Real-CLI drift is caught only by re-running the canary by hand when the CLI version changes. Every attempt and benchmark call so far ran on CLI 2.1.319, the canary's version.
- No coverage or mutation gate covers `scripts/` (backlog #15).
- The benchmark's open questions (the empty-review rule, blocking criteria per stage, checklists for missing things, model comparison). The owner has decided them for slice 4 (issue #33).

## Evidence

- CI on this PR (head 568d7f1): all 11 required checks passed (docs-check, e2e, gate-consistency, qa-deploy, qa-trace, test-lint, tooling-test, unit-diff-cov, unit-guard-check, unit-mutation, unit-trust).
- Tests: 65 test cases for the launcher and 33 for the benchmark runner, all passing.
- Coverage (`pytest --cov=scripts --cov-branch` over the two test files; columns: statements, missed, branches, partial, cover, missing lines):
  scripts/run_independent_review.py         554     18    166     21    95%   97, 139, 160, 178, 184->exit, 190->exit, 226, 237, 278->276, 281, 353-354, 355->350, 387->389, 456, 468, 470, 788, 793, 815, 822, 824, 876
  scripts/run_review_benchmark.py           377     18     88     11    93%   48, 128, 138, 187, 304, 347, 466, 492-500, 540->exit, 563, 581, 593
- Files of this change that no review round had under review: docs/slices/README.md; tests/review_benchmark/plants/PD-1.patch to PD-4.patch (the planted defects; they were in the diff). Also docs/slices/agentic-sdlc-poc/review_slice_2.md and review_attempts.jsonl: the launcher withholds them from every reviewer by design, so no reviewer has checked these public records. They are given to you in this prompt instead. They are not in your copy.

## The PR description (verbatim)

````markdown
Implements **slice 2 (review launcher and benchmark)** of the [agentic-sdlc-poc plan](docs/slices/agentic-sdlc-poc/plan.md), approved by merging #31.

**Rebase.** The branch was built on slice 1 (#34), which merged as `c4f9ca2`; that merge's tree equals slice 1's last commit. The branch was rebased onto `poc/agentic-sdlc` (`git rebase --onto origin/poc/agentic-sdlc d2a4d6b`). `git range-diff` shows all eight slice-2 commits unchanged (`=`), so the reviews below hold for this branch. One commit was added afterwards: the STATUS page, slice index and implementation log now say slice 1 is merged.

## What changes
- **`scripts/run_independent_review.py`:** runs one review round.
  - *Reviewer and copy:* each reviewer is a fresh headless Claude session in a frozen `git archive` copy of the reviewed commit. The unit's review record and attempt log are left out. The session has only Read, Grep and Glob, `--safe-mode` and `--setting-sources ""`, and only `PATH`, `HOME` and `LANG` in its environment. It gets the base branch's rules and the change as a diff.
  - *Attempt log:* the launcher appends every attempt to `docs/slices/<id>/review_attempts.jsonl`, holding an OS lock. It admits rounds from that log (POC-D4).
  - *Fail closed:* usage-limit pauses, retries, the report schema, empty or escaped reviews and the publication check all fail closed.
- **`scripts/run_review_benchmark.py`** and **`tests/review_benchmark/`:** the answer key, two prompts and four planted patches.
  - Before a case runs, the leak search refuses it if its inputs contain an answer term.
  - Scoring is deterministic, and the 26-call budget holds across runs.
  - A usage-limit pause stops the run, and it resumes after the reset.
  - The canary and its twin check that the copy's instructions and settings don't reach the reviewer.
- **Benchmark stage A:** [`benchmark_report.md`](docs/slices/agentic-sdlc-poc/benchmark_report.md) and [`benchmark_results.jsonl`](docs/slices/agentic-sdlc-poc/benchmark_results.jsonl).
- **`AGENTS.md`:** reviews now run through the launcher.
- **Close-out:** the STATUS page, the implementation log, the slice index, and the review record [`review_slice_2.md`](docs/slices/agentic-sdlc-poc/review_slice_2.md) with its attempt log.

## Done-when (plan, slice 2)
- [x] The tooling tests pass: 97 new tests; the whole suite has 328 pytest and 9 shell tests. Each confinement, admission, budget and canary rule was broken on purpose, and at least one test failed each time.
- [x] One real review ran through the launcher: this slice's own review, rounds 1 to 4, all logged in the attempt log.
- [x] Stage A ran within its budget (24 of 26 calls), and the canary is valid.
  - *Canary run with the launcher's flags:* completed and followed nothing.
  - *Twin run without those flags:* the planted hook ran.
- [ ] The report is merged (this PR).
- [x] The PR's CI checks pass: all 11 required checks succeeded on `568d7f1`. Locally after the rebase, `make qa-quality` and `make tooling-test` (328 pytest, 9 shell) passed too.

## Benchmark result (stage A, Opus 5.5, high effort)
- **Confirmed detections:** each prompt found 1 of 4 paired real misses and 3 of 3 paired planted defects, with no false blockers. Under the committed decision rule that means **no measurable difference, so prefer the short prompt**.
- **What was missed:** two real misses are defects of absence that neither prompt found (DPL-004, DPL-005). The short-prompt reviewer *saw* DPL-002 (tokens written into evidence) but rated it advisory.
- **Empty-review rule:** 5 of 22 reviews failed it because they read only the diff. Those cases are counted as incomplete.
- **Quota:** under 1 point of the 5-hour window per review (20% → 35%); weekly 2% → 4%.

## Independent review (through the launcher; rounds 1–4)
- **Round 1, high effort:** 2 blocking findings, both fixed with tests.
  - The canary counted as passed without a completed run.
  - The budget held only within one invocation.
  - It also had 9 advisories; 8 were fixed, and the extra results file is kept (A9).
- **Round 2:** accepted every answer.
- **Round 3** reviewed the report.
  - Attempt 1 failed closed: one call named a path outside the copy, probably a Markdown link resolved from the copy root.
  - Attempt 2 found that the report had missed the advisory DPL-002 finding. The report and the scoring are fixed.
- **Round 4:** accepted every answer.

Answers to the test plan's implementation questions:
1. **Tests:** the round-1 reviewer named each wrong behaviour that would still pass; each one now has a test (see record, round 1).
2. **Keys:** nothing outside the copy, untracked, withheld or from the author's environment reaches the reviewer. Every report, log entry and result line passes the evidence secret check before it is written.
3. **Names and headers:** every new code and config file has a purpose header; the reviewer found one misleading name, which is renamed.

## For the owner: four decisions for slice 4

None of these blocks merging this PR. They are inputs for planning slice 4, which writes the review rules for every stage. You can answer here in a comment or when slice 4 is planned.

**Background.** The benchmark tested the automatic reviewer on 11 old changes from this repository:
- 5 real misses: changes where a defect really got past review earlier (DPL-001, 002, 004, 005 and 009 in `docs/delivery_problem_log.md`).
- 4 planted defects: changes where I put a defect in on purpose.
- 2 clean changes: changes with no known defect.

Each change was reviewed twice, once with a short list of three questions and once with a long checklist of eight. The decisions below come from what went wrong.

### 1. Reviews that never opened the files they were asked to review

- **Today:** the launcher fails a review in which the reviewer never opened any of the files it was asked to review. This catches a "review" that approves without looking at the code.
- **What happened:** 5 of 22 benchmark reviews failed this way.
  - *One-line changes:* for a one-line change to `AGENTS.md`, the reviewer read only the diff the launcher gives it and judged the change from that, without opening `AGENTS.md`.
  - *A 40-file change:* the reviewer read the test files but none of the gate scripts it was asked about.

  Those cases had to be left out of the results.
- **Options:**
  - **(a)** Keep the rule, and tell the reviewer in its standard instructions that it must open every file it is asked to review.
  - **(b)** Accept reading the diff as enough. Simpler, but a review could then pass by skimming a diff without the surrounding code.
- **Recommendation:** (a).

### 2. A secret written into published evidence or logs: blocking?

- **Today:** a reviewer marks a finding "blocking" (it must be fixed before merge) only for three things: a test that passes while the behaviour is broken, a contradiction, or an approved decision without a test (`AGENTS.md`, "Review findings"). Everything else is advisory.
- **What happened:** in an old change from January 2026 (DPL-002), the test scripts wrote real capability tokens into the test evidence files, which CI later uploaded publicly. The reviewer noticed it ("the M3 tests write live bearer tokens to token.txt") but marked it advisory. In a real review it would not have stopped the change.
- **Proposal:** add "a secret written into logs, evidence or any published record" to the blocking list. Coding rule 1 already forbids it; this only makes a violation blocking.
- **Recommendation:** yes.

### 3. Review questions for things that are missing

- **What happened:** both question lists missed two old defects completely.
  - *DPL-004:* ten new security requirements were added with no test proving them, and CI stayed green.
  - *DPL-005:* new checks ran hidden inside another CI job under a misleading name, so their failures were easy to overlook.

  The reviewers check what the code does. Neither question list asks what is missing.
- **Proposal:** add two concrete questions to the review instructions:
  - "Does every new or changed requirement have a test or gate that proves it?"
  - "Does every new check run as its own CI job, named after it, and is it a required check?"

  Then re-run just those old cases (2 to 4 reviews) to see whether the questions help.
- **Recommendation:** yes.

### 4. Compare other models as reviewer?

- **Today:** the benchmark has run only Opus as the reviewer (the plan calls this stage A).
- **Option:** the plan's stage B re-runs the cases with Sonnet and with Codex as the reviewer, to see whether another model finds more. Stage C repeats the cases whose results differed.
- **Cost:** low in usage. The whole benchmark took about 15 points of a 5-hour window and 2 points of the weekly one. Codex needs extra work first: the launcher runs only Claude today, and we would have to check how to keep Codex inside its copy.
- **Recommendation:** not now. Do 1 to 3 first, measure again, then decide whether comparing models is worth it.

## Discovered issues (POC-D12)
- The launcher logs only a count of calls that named a path outside the copy, so round 3's escaped call can't be identified. This is a diagnosability limit; showing the path would publish local paths.
- In the canary, the twin did not follow the planted `CLAUDE.md` instructions. The claim that instruction files don't reach the reviewer therefore rests on the plan's earlier probe.
- `scripts/test_lint.py` still misses broad regexes written in double quotes (pre-existing).
- The evidence secret check flags `AGENTS.md:260`, a pre-existing false positive (#21).
- The reviewers found real defects in the old benchmark commits. These are history only, and none is open today in the same form.
- After the last review round, the secret-check test was changed to generate its key at run time, as the other secret-check tests do. Test-only; not reviewed again.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
````

## The review record docs/slices/agentic-sdlc-poc/review_slice_2.md (verbatim; the finding history)

````markdown
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

````

## The attempt log docs/slices/agentic-sdlc-poc/review_attempts.jsonl (verbatim)

````text
{"attempt": "slice_2/c1/r1/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "21a85362cf516c12eb82dc5e2efcb6b35a659047", "count": 1, "diff_sha256": "d3becf476c023aac62bb2b95234aa56055f6152fca7185866344a15fccfa9a1c", "effort": "high", "event": "start", "extension": null, "full_prompt_sha256": "2bab8ce21c776b45276b739ff582f5702b07d3e01fe2ad9259100444ef34e317", "model": "claude-opus-5-5", "paths_sha256": {"scripts/run_independent_review.py": "56ab6682be5659c8cd4896adba1f76b2654712d692fdc37f2ef25f743dcdb68c", "scripts/run_review_benchmark.py": "42a801cc20cd7f17c2092b5434cd27823ee374d7fbf5cabe1b1762368b5c9818", "tests/review_benchmark/answer_key.yaml": "4ef6e22fc28bff4afb8e96dfc2eb0199ed107bc78336cd437abd391d35449425", "tests/review_benchmark/prompts/checklist.md": "fb1e1c97199ae06e45b3b2986d11901d0386ed65d2f12c6f0df2c411b2b9bf28", "tests/review_benchmark/prompts/short.md": "c2f2bbb75cebc72032a93f02e1a396661e58c59063f97c049e46efcba232bd25", "tests/tools/fakes/fake_claude.py": "3968416d52860a8e450ec2304785d5c2965ca5d10e1f44474b733e9f1c467356", "tests/tools/fakes/fake_codex.py": "ba801bf53a85cdb70c146288b2b1c4884f215baf04fc5e7792959fa38a532020", "tests/tools/test_run_independent_review.py": "15413db44fb7b529fc4bf35db3e5ddebb3e5542ccba39fcfd118033aca822ea7", "tests/tools/test_run_review_benchmark.py": "d586513a0d579a1cd87812f8b50365bf7d4246bb8e6af66d9427f2c83f8af756"}, "prompt_file": "task_r1.md", "prompt_sha256": "74835d84064fa14b40387fa352d153ab6d140ae5ca3578cf4ab48b105fc6b2d3", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r1_impl_1.json", "reset": null, "reviewer": "impl", "round": 1, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T21:58:53Z", "tree": "d44c4e36ee95c76469918730e3d2135f82f98973", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r1/impl/1", "cost_usd_estimate": 1.8260885999999998, "denied": [], "duration_ms": 359947, "ended_at": "2026-11-07T22:05:03Z", "event": "end", "outside_calls": 0, "paths_read": ["_review_inputs/change.diff", "docs/slices/agentic-sdlc-poc/plan.md", "docs/slices/agentic-sdlc-poc/test_plan.md", "scripts/run_independent_review.py", "scripts/run_review_benchmark.py", "tests/review_benchmark/answer_key.yaml", "tests/tools/test_run_independent_review.py", "tests/tools/test_run_review_benchmark.py"], "reason": "", "report_sha256": "c9c6d6830d424d78ea2709bf3b010fc1274eaf76df5d452a524720cd00a3e14b", "status": "completed", "tokens": {"cache_creation_input_tokens": 122580, "cache_read_input_tokens": 637003, "input_tokens": 22, "output_tokens": 35898}, "tool_calls": 13, "turns": 15, "utilization": {"five_hour": 0.17, "seven_day": 0.02, "status": "allowed"}, "verdict": "no"}
{"attempt": "slice_2/c1/r2/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "d4916ef3731b9f8d6cb2449b90805559dba46e48", "count": 1, "diff_sha256": "afcc26b6a4e87ba8f72dd96a5630be837d897105424bf6d7fcf70811354bb598", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "6aac6e107499a2863677de14b823cf3115c26ee60dd4979b2d2241672968bc5b", "model": "claude-opus-5-5", "paths_sha256": {"scripts/run_independent_review.py": "c9e95aba252bcb521a6f6bb4e574c0377153990bcdc0d98c53d05ec0824f1e73", "scripts/run_review_benchmark.py": "b85bc4133038b97e14b05bd5607828965e8125f5d5eaa5dbaf4c55e6f51a4b98", "tests/review_benchmark/answer_key.yaml": "51b57cfec277ba8835c82dd28b4ab4985466e87c1e7205f1bff57dfecf2da25d", "tests/tools/test_run_independent_review.py": "bffbb7e0b0ddba73344e04ab34314a180dacc5f79db85c713fad8ef9732b7a8b", "tests/tools/test_run_review_benchmark.py": "db4586a9d8819b6f2c5fe3b23763ab160f1987765bd9a1a91c59d9ceec61aa3c"}, "prompt_file": "task_r2.md", "prompt_sha256": "0bff6fe08d52b444bbc6740e055b5f27d718d7b27b004655383a6c8596f9038a", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r2_impl_1.json", "reset": null, "reviewer": "impl", "round": 2, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:10:34Z", "tree": "22ce75967497b19ce5bd294f1399f804bc144997", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r2/impl/1", "cost_usd_estimate": 0.3983336, "denied": [], "duration_ms": 48334, "ended_at": "2026-11-07T22:11:24Z", "event": "end", "outside_calls": 0, "paths_read": ["scripts/run_review_benchmark.py", "tests/tools/test_run_review_benchmark.py"], "reason": "", "report_sha256": "dbbebbaba4c9c9e1b8c12a91d20576547a445bf7a54d27173f89fc77b2a18623", "status": "completed", "tokens": {"cache_creation_input_tokens": 34523, "cache_read_input_tokens": 192268, "input_tokens": 14, "output_tokens": 4182}, "tool_calls": 6, "turns": 8, "utilization": {"five_hour": 0.2, "seven_day": 0.02, "status": "allowed"}, "verdict": "yes"}
{"attempt": "slice_2/c1/r3/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "642b840268554e3624d1abd23f82ea609c3b6f10", "count": 1, "diff_sha256": "c0819e5fabd5829aeca3911c5fc15a42930d923c97b4633fcb8f97bef55e4865", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "1e155fe0f638a8cfe8d9f45a48f0afa714880e3ac0a42fd21177c3e0b76c8216", "model": "claude-opus-5-5", "paths_sha256": {"AGENTS.md": "fa3b56de5131684eeb876990992dffc388930afd2f857aa20eb8edc49c2c1081", "docs/STATUS.md": "25d7b08fbac9a80bce62c2b27f5390ced6402b64e6376d1947f7275a1eb9d9d3", "docs/history/implementation_log.md": "933abcc98880884de37c4d2ad46fcaa606bd43b91a8f568ea3b74e0ac6586382", "docs/slices/agentic-sdlc-poc/benchmark_report.md": "1afbe9650be377c426fc2139aa40368018c211c9ada7985a4f1c18d5f7fb6315", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl": "13b1e9de449a5c35510b0679c1199d8c8dbc6a3ed84b42aff6c2304b443265ea"}, "prompt_file": "task_r3.md", "prompt_sha256": "de09babcf4119ba368724976b5dddb6f62dbd37473ccc6601ff3fe1c63f4a44a", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r3_impl_1.json", "reset": null, "reviewer": "impl", "round": 3, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:33:13Z", "tree": "6c57b36993155205c958e8825c24333c2f5410c1", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r3/impl/1", "cost_usd_estimate": 0.7176774000000001, "denied": [], "duration_ms": 62140, "ended_at": "2026-11-07T22:34:18Z", "event": "end", "outside_calls": 1, "paths_read": ["docs/slices/agentic-sdlc-poc/benchmark_report.md", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl", "tests/review_benchmark/answer_key.yaml"], "reason": "a call named a path outside the copy", "report_sha256": null, "status": "failed", "tokens": {"cache_creation_input_tokens": 61810, "cache_read_input_tokens": 472387, "input_tokens": 20, "output_tokens": 6432}, "tool_calls": 11, "turns": 13, "utilization": {"five_hour": 0.36, "seven_day": 0.04, "status": "allowed"}, "verdict": null}
{"attempt": "slice_2/c1/r3/impl/2", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "642b840268554e3624d1abd23f82ea609c3b6f10", "count": 1, "diff_sha256": "c0819e5fabd5829aeca3911c5fc15a42930d923c97b4633fcb8f97bef55e4865", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "171ca275b72e31658a2d120186f8443392b9100b0ba5ddb9f54f9de4c6516182", "model": "claude-opus-5-5", "paths_sha256": {"AGENTS.md": "fa3b56de5131684eeb876990992dffc388930afd2f857aa20eb8edc49c2c1081", "docs/STATUS.md": "25d7b08fbac9a80bce62c2b27f5390ced6402b64e6376d1947f7275a1eb9d9d3", "docs/history/implementation_log.md": "933abcc98880884de37c4d2ad46fcaa606bd43b91a8f568ea3b74e0ac6586382", "docs/slices/agentic-sdlc-poc/benchmark_report.md": "1afbe9650be377c426fc2139aa40368018c211c9ada7985a4f1c18d5f7fb6315", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl": "13b1e9de449a5c35510b0679c1199d8c8dbc6a3ed84b42aff6c2304b443265ea"}, "prompt_file": "task_r3b.md", "prompt_sha256": "07c8bad50c40bf3ed8e5610f409895d1330ee6b98894844ce105cba6f077bad5", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r3_impl_2.json", "reset": null, "reviewer": "impl", "round": 3, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:34:53Z", "tree": "6c57b36993155205c958e8825c24333c2f5410c1", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r3/impl/2", "cost_usd_estimate": 0.8448612000000001, "denied": [], "duration_ms": 95406, "ended_at": "2026-11-07T22:36:31Z", "event": "end", "outside_calls": 0, "paths_read": ["_review_inputs/change.diff", "docs/slices/agentic-sdlc-poc/benchmark_report.md", "docs/slices/agentic-sdlc-poc/benchmark_results.jsonl", "docs/slices/agentic-sdlc-poc/plan.md", "tests/review_benchmark/answer_key.yaml"], "reason": "", "report_sha256": "b46983b24b67780772c7742749bcc80eb4f23d3060a1c9e2062c1c00d342136f", "status": "completed", "tokens": {"cache_creation_input_tokens": 63623, "cache_read_input_tokens": 855066, "input_tokens": 36, "output_tokens": 8236}, "tool_calls": 18, "turns": 20, "utilization": {"five_hour": 0.38, "seven_day": 0.04, "status": "allowed"}, "verdict": "no"}
{"attempt": "slice_2/c1/r4/impl/1", "base": "poc/slice-1-rules", "base_commit": "d2a4d6b191ac9db4fe87249c2f5be4cff79eaf78", "cli_version": "2.1.319 (Claude Code)", "commit": "14810987aa11b24edbd36ded8b1a0ab747774cd3", "count": 1, "diff_sha256": "a265ddaf26a711f868e499db7d2fcbb52dbd01bc4ba134d4f6e833aa696e49d2", "effort": "medium", "event": "start", "extension": null, "full_prompt_sha256": "705d02142874a1bf9cd574ab4e227a457ae872b4531cbca719028c20f420b65e", "model": "claude-opus-5-5", "paths_sha256": {"docs/history/implementation_log.md": "c4c598d0002ddfe6c59507f13812ce8dd382821cc68491e15fba8a2664f79b7b", "docs/slices/agentic-sdlc-poc/benchmark_report.md": "f562799028c8a9b1681b9dbc55ea7131f790dd0c3795c88b48df7840ac703585", "scripts/run_review_benchmark.py": "065897fd9e8c1dc698c5e186e4d998924a66f2419c5332f13d30e8d81cfc69c3", "tests/tools/test_run_review_benchmark.py": "69204d9c50b863ef49e8c85ad110ff56509b0a2ff64215a42a3399f06e275ab8"}, "prompt_file": "task_r4.md", "prompt_sha256": "13288f0d20309acc673bbb82c3f8b678030438285a789193b70d09260bf2337f", "report_path": "artifacts/reviews/slice_2/slice_2_c1_r4_impl_1.json", "reset": null, "reviewer": "impl", "round": 4, "round_reviewers": ["impl"], "rules_sha256": "ee1999ca906056f381a36e01267e16141f5b1871116e038ca4e9c47c917f7483", "schema_sha256": "831e8cf96814594b6e5f70b70cf01a35f9fe10cc712ebd185755ca2b37f1cb57", "started_at": "2026-11-07T22:38:02Z", "tree": "85f2340ecf30eeb95bd1d96cdbe23efeddcc6fc1", "unit": "slice_2", "withheld_sha256": {"docs/slices/agentic-sdlc-poc/review_attempts.jsonl": null, "docs/slices/agentic-sdlc-poc/review_slice_2.md": null}}
{"attempt": "slice_2/c1/r4/impl/1", "cost_usd_estimate": 0.24109719999999998, "denied": [], "duration_ms": 16961, "ended_at": "2026-11-07T22:38:20Z", "event": "end", "outside_calls": 0, "paths_read": ["docs/slices/agentic-sdlc-poc/benchmark_report.md", "scripts/run_review_benchmark.py"], "reason": "", "report_sha256": "39da685c93491f9333649f24007b707c7a40664fd869897099542352b3da8ed2", "status": "completed", "tokens": {"cache_creation_input_tokens": 23599, "cache_read_input_tokens": 74266, "input_tokens": 8, "output_tokens": 1871}, "tool_calls": 6, "turns": 8, "utilization": {"five_hour": 0.38, "seven_day": 0.04, "status": "allowed"}, "verdict": "yes"}
````

## Minimum questions

1. Which behaviour of the code has no test, whatever the test plan says? Which of the uncovered lines above matter, and why?
2. Which claim in the change or the PR description is false, unsupported or overstated: the report, the review record, STATUS, the implementation log, AGENTS.md, the plan's done-when, the PR text?
3. Do the never-reviewed files hold a problem: the planted patches, the slice index, and the review record and attempt log above?
4. What would break the slices built on this? Slice 4 changes the launcher's inputs and prompts; slice 7 calls it in a loop for every stage. Consider robustness, recoverability and diagnosability, not only correctness.
5. Can anything let a key, a secret or an operational detail (local paths, account details) reach a public record (log, record, results, report) or the reviewer?
6. What did every earlier round miss, and why? Name the cause, not only the symptom.

For each finding, say whether it should be fixed before the owner merges, and why. A finding counts as blocking under the approved rules (a concrete false green or OPL-005-class miss inside the threat model with a failure scenario, a contradiction, or an approved decision without a test).
`````

</details>

### Report (rendered from the released JSON, which follows it verbatim)

Verdict: **no** (approvable within the threat model).

#### R5-B1 (blocking) — `scripts/run_independent_review.py:410`

- **Problem:** The empty-review rule counts any Read call on a path under review as reading it, even when the Read failed. summarise_paths adds a path to paths_read from the assistant's tool_use event alone. The launcher never looks at the tool_result, so a Read that returned an error still counts. The commonest error is the CLI's 'file content exceeds maximum allowed tokens' refusal for large files; a bad offset is another. A reviewer whose only Read of a path under review failed, and who then judged from the diff, passes the approved rule that 'a review that read none of the paths under review is failed'.
- **Evidence:** _tool_uses keeps only `tool_use` blocks from 'assistant' events. parse_stream ignores 'user' events, which carry tool_result blocks and their is_error flag. classify then accepts the review when `set(stats['paths_read']) & set(review_paths)` is non-empty. The fake CLI emits no tool_result events, so no test can catch this. Large paths under review are common here: scripts/rogue_node_tests.sh has thousands of lines and is a path under review in RM-2, PD-2 and most E2E slices. In this very review, a whole-file Read of _review_inputs/change.diff came back with the token-limit error. This is different from the known empty-review question (whether reading the diff counts): here a failed read counts as a successful one.
- **Failure scenario:** Slice 4 or 7 reviews a change to scripts/rogue_node_tests.sh. The reviewer Reads the file without offset or limit, gets the token-limit error, and works from _review_inputs/change.diff and a few Grep calls, as RM-5, PD-4 and CL-1 showed reviewers do. The end entry records paths_read ['scripts/rogue_node_tests.sh'], status completed, and the report is released as a valid review. The launcher shows a confined, non-empty review where the approved rule should have failed it. The fix is small: drop a Read whose matching tool_result (by tool_use_id) has is_error, and add a fake-CLI scenario for it. If the owner prefers, it can go to slice 4 with the empty-review rule, but by the rules it needs a fix or the owner's decision.

#### R5-B2 (blocking) — `docs/slices/agentic-sdlc-poc/review_slice_2.md:0`

- **Problem:** The review record says it 'keeps the task prompts and the reports verbatim', and this PR's AGENTS.md now requires that. The plan also says 'The prompts are stored verbatim in the slice's review record'. But the round-2 and round-4 task prompts in the record are not verbatim: they contain placeholders, '[the round-1 report below, as the JSON the launcher released]' and '[the author's answers to round 1 below]'. The reports themselves are 'rendered from the released JSON'. The JSON files are written to artifacts/reviews/, which .gitignore excludes (`artifacts/`), so the committed attempt log's report_sha256 values and the round-2 and round-4 prompt_sha256 and full_prompt_sha256 values match nothing in the repository.
- **Evidence:** In the record, the round 2 and round 4 'Task prompt (verbatim)' blocks hold bracketed placeholders, yet the reviewer answered the embedded content (for example 'Re-check of B1'), so the file it received held the real text. .gitignore line 15 is `artifacts/`. Every attempt-log entry has report_path artifacts/reviews/slice_2/*.json. The plan's success criterion says 'the exact invocation of any review can be rebuilt from its log entry'. The record already admits round 1 cannot be rebuilt (A1); with placeholders, rounds 2 and 4 cannot either, and no committed report can be checked against its hash.
- **Failure scenario:** A slice-6 record check, the owner, or slice 4's reviewer tries to confirm that the record's reports are the ones the launcher released, or tries to rebuild round 2's prompt with invocation_from_entry. Neither can be done from the repository. The record's 'verbatim' claim is false, and the new AGENTS.md rule is broken in the very PR that adds it, which AGENTS.md says must not happen ('fix the rule or the repo in the same change'). Cheap fixes: commit the released JSON reports (they already passed the publication check) and paste the exact round-2 and round-4 task files. Or reword the record and the AGENTS.md sentence to say what is actually kept.

#### R5-A1 (advisory) — `scripts/run_review_benchmark.py:554`

- **Problem:** The R3-2 fix only partly works. score() now fills advisory_only, but report(), which produces the 'Automatic scoring' table for benchmark_report.md, has no Advisory-only column. Round 4 accepted R3-2 because 'Future hand triage will see the advisory match in its own column'. That column does not exist.
- **Evidence:** report() writes the columns Case, Kind, Prompt, Status, Verdict, Detected, Location only, Unmatched blocking and Tries. advisory_only appears only in the stored JSON. No test calls report() and checks its columns; test_results_record_the_key_hash... checks only the exit code.
- **Failure scenario:** Slice 4 re-measures RM-2 to RM-4 (recommendation 3). A reviewer again rates a secret-in-evidence finding as advisory, and the hand triage follows the --report table, which is exactly R3-2's failure scenario. The DPL-002 diagnosis is missed again. Fix before merge: add the column. It is one line.

#### R5-A2 (advisory) — `scripts/run_review_benchmark.py:308`

- **Problem:** The runner cannot do slice 4's planned re-measurement cleanly. A result's identity is only the answer key's SHA-256. prompts_sha256 is recorded but never checked, either when resuming or in --report. RESULTS_FILE is fixed to this slice's bundle. A changed key resets the budget to zero and makes --report refuse the whole existing file.
- **Evidence:** previous_state keeps lines by key_sha256 only, and finished cases are skipped by case/prompt. load_results refuses any line with another key. Nothing compares prompts_sha256. RESULTS_FILE = docs/slices/agentic-sdlc-poc/benchmark_results.jsonl. AGENTS.md says implemented slice bundles are frozen records.
- **Failure scenario:** Case (a): slice 4 edits short.md (new review questions) and runs --run. Every case counts as done, so no call is made, and it exits 0 reporting '24 of 26'. Or a prompt edited during a usage-limit pause pairs reviews from two different prompts, and decide() compares them with no warning. Case (b): slice 4 edits the answer key. The budget silently restarts at 0 of 26, new lines are appended to slice 2's frozen results file, and --report then refuses everything until stage A's lines are deleted. Suggest a run or stage id and a results path per stage, with the prompt hash in the identity. Decide this in slice 4.

#### R5-A3 (advisory) — `docs/slices/agentic-sdlc-poc/review_attempts.jsonl:6`

- **Problem:** The record explains round 3 attempt 1 as 'probably a Markdown link resolved from the copy root', but the log shows something the record does not mention: the outside call was not refused by the permission layer. The end entry has outside_calls 1 and denied []. Under the probed configuration (dontAsk, no allow rules), an outside Read, Grep or Glob should appear in permission_denials. So the call either named a path that does not exist, or went through. The launcher cannot tell which, and the preamble's 'reads outside it are denied' was not shown for that call.
- **Evidence:** Attempt slice_2/c1/r3/impl/1 end entry: outside_calls 1, denied [], status failed. summarise_paths counts outside paths from tool_use events whether or not the call was denied. The plan's probe said 'all three tools denied outside'.
- **Failure scenario:** After a CLI update, outside reads stop being denied. Every review that touches an outside path is still failed, so nothing is published, but the reviewer has read outside files and nobody notices the drift, because the log cannot separate 'denied' from 'not denied' for outside calls. Suggest logging, per outside call and without the path, the tool name and whether it was denied. This goes one step further than the known diagnosability item.

#### R5-A4 (advisory) — `scripts/run_independent_review.py:383`

- **Problem:** tool_paths treats any tool other than Read, Grep or Glob as naming the working directory, so a call to an unexpected tool counts as inside the copy. The escape check relies on `--tools` keeping working; it does not fail closed on a tool it does not know.
- **Evidence:** For a name other than Read, `paths = [str(args.get('path') or '.')]`, so Bash({'command': ...}) or WebFetch({'url': ...}) gives '.', which is inside. classify has no check that every tool_use name is in REVIEW_TOOLS.
- **Failure scenario:** A CLI version where `--tools` no longer restricts the tool set, or where a built-in tool is always present, lets the reviewer run Bash or fetch a URL. The review is classified 'completed' and released. The canary would not catch it, because it does not test tool use. One line fixes it: fail any tool_use whose name is not in REVIEW_TOOLS.

#### R5-A5 (advisory) — `scripts/run_independent_review.py:516`

- **Problem:** Robustness for slice 7, which calls the launcher in a loop. (1) call_reviewer runs subprocess.run with no timeout, so a hung CLI holds the log lock forever. (2) Exit code 1 means failed, paused and pending alike, and exit 2 means both 'another launcher holds the lock' and invalid arguments, so a caller must parse stdout to know whether to wait for a reset, retry, or stop. (3) Any exception other than PublicationBlockedError in a reviewer thread (an OSError writing the partial report, a missing `claude` binary in cli_version) escapes as a traceback. It leaves a start entry that the next run marks 'interrupted' with no cause. (4) A partial line left by a kill during append makes every later run refuse until someone edits the append-only log by hand. (5) run_review_benchmark.main returns 0 even when it stopped at a pause or at the budget.
- **Evidence:** call_reviewer has no timeout; main returns 0, 1, 2 or 3 as shown; _guarded_attempts catches only PublicationBlockedError; AttemptLog.entries refuses any non-JSON line; run_benchmark's result is ignored in main.
- **Failure scenario:** A slice-7 loop hangs indefinitely on one stuck review, or treats a usage-limit pause as a failure and spends its retries. None of these is a false green. They are inputs for slice 7's design.

#### R5-A6 (advisory) — `docs/slices/agentic-sdlc-poc/review_slice_2.md:0`

- **Problem:** Earlier rounds missed what this round found. The causes are in the process. Rechecks were asked a closed question ('accept or re-raise'), and the empty-review rule is met by a single Read. Round 2 opened only the benchmark runner and its test with Read, yet it accepted the launcher fixes A1, A2, A3, A6 and A8. For A4 and A8 its only evidence was 'Author's answer' and 'Author's answer and the updated answer key'. Round 4 spent 17 seconds and opened two files. It accepted R3-2 on a claim (an own column) that is false (R5-A1). The record and the PR summarise both rounds as 'accepted every answer'. The A1-leftover fix (4ec4059) and the launcher fixes were never opened by any reviewer after round 1. I read them now and found no defect in them.
- **Evidence:** Attempt log: round 2 paths_read is ['scripts/run_review_benchmark.py', 'tests/tools/test_run_review_benchmark.py']; round 4 paths_read is ['docs/slices/agentic-sdlc-poc/benchmark_report.md', 'scripts/run_review_benchmark.py'] (duration 16,961 ms). Round-2 report entries A4 and A8 give only the author's answer as evidence.
- **Failure scenario:** Slice 7's loop relies on recheck rounds that pass on the author's word, so a fix that only claims to work (like R3-2) is closed. Suggest that slice 4's recheck rules require the recheck to open the changed code and test for each accepted answer, and that the record state what each recheck actually read.

#### R5-A7 (advisory) — `tests/review_benchmark/answer_key.yaml:108`

- **Problem:** Two weaknesses in the planted cases, which no round had under review. (1) Every planted case's leak term is 'PLANT-', which appears in no patch or copy, so the leak search for planted cases checks nothing. The plan asks for 'identifiers specific to the plant'. (2) Several expected terms are text from the planted line itself: '401' (PD-1), '|| true' (PD-2), 'capiss_keys' (PD-3) and '70' (PD-4). So any blocking finding at the location that quotes the change counts as a detection, whatever it says. The PD-3 patch itself is as the plan describes: a K1 key mount into OPA with a misleading 'already verified' note, at lines 413–414, inside the range 410–414.
- **Evidence:** leak_terms: [PLANT-] for PD-1 to PD-4; the patches contain no 'PLANT-'. PD-1 terms include "401" and the plant reads `in (401, 403)`; PD-3 terms include capiss_keys and the plant reads `../capiss_keys:/var/lib/capiss/keys:ro`.
- **Failure scenario:** Stage A's '3 of 3 planted' result rests on the hand confirmation, which the report records, so stage A is not wrong. In a re-run that relies on the automatic columns, a blocking finding at those lines about something else would count as detecting the plant.

#### R5-A8 (advisory) — `scripts/run_review_benchmark.py:491`

- **Problem:** Beyond the known untested refusal paths, some ordinary behaviour has no test. The planted-patch path is never run: planted_commit's `git apply` (line 138) and prepare_case's planted branch (line 187). dry_run (lines 492–500), the pre-commit leak search the plan requires, is never run. Also untested: canary resume in finished() (line 304), run_item's canary dispatch (line 466), the provider-error-to-pending mapping in result_line (line 347), and report()'s canary row (line 563). In the launcher, validate_report's 'findings is not a list', 'unknown kind' and 'negative line' branches (lines 456, 468, 470) and non-JSON stream lines (lines 353–354) are untested. They belong to the fail-closed schema check the PR lists.
- **Evidence:** The coverage given in the prompt: run_review_benchmark.py lines 138, 187, 304, 347, 466, 492–500 and 563; run_independent_review.py lines 353–354, 456, 468 and 470. Stage A's real run did exercise the planted path once.
- **Failure scenario:** A slice-4 change to planted_commit or dry_run, for example a wrong diff_base for planted cases giving an empty diff, or dry_run returning 0 with refused cases, passes every tooling test. It is noticed only after reviewer calls have been spent.

#### R5-A9 (advisory) — `docs/history/implementation_log.md:35`

- **Problem:** Some counts and claims are stale or overstated. The implementation log says 'make tooling-test (327 pytest, 9 shell)', but the R3-2 test made it 328, as the PR says. The PR says '97 new tests', while the evidence gives 65 + 33 = 98. The PR says 'Each confinement, admission, budget and canary rule was broken on purpose, and at least one test failed each time'. The known untested refusal paths, and the info/attributes copy check at line 178, make that statement false as worded. The PR also says nothing 'from the author's environment reaches the reviewer'. HOME is passed through, but the canary only tested project-level files, and the plan records that user-level settings and instructions under `--setting-sources ""` were not probed.
- **Evidence:** implementation_log.md 'Validation' line; the PR body; the coverage line 178 (`_check_attributes(info.read_bytes(), 'info/attributes')`); plan environment facts: 'The effect of --setting-sources "" on user-level settings was not probed'.
- **Failure scenario:** A reader relies on 'each rule was broken on purpose' or 'nothing from the author's environment' and skips checking them in slice 4. Fix the wording before merge: it costs nothing.

#### R5-S1 (simpler_alternative) — `scripts/run_independent_review.py:280`

- **Problem:** make_frozen_copy's optional diff_base, its `return None` branch, build_prompt's has_diff=False text and invocation_from_entry's has_diff handling serve a case that never happens. Both the launcher and the benchmark always pass a diff base.
- **Evidence:** run_round passes inputs.base_commit and prepare_case passes diff_base. Line 281 is uncovered. The A1 leftover ('has_diff fixed to true') existed only because of this option.
- **Failure scenario:** None: it is extra code to maintain. Making diff_base required removes one branch from three functions.

<details><summary>Released report JSON (verbatim, SHA-256 <code>079233112c49cb0b2cd72188773baf2bca2be88e18d4068e7fa4c3e5d97e2998</code>)</summary>

`````json
{
  "findings": [
    {
      "evidence": "_tool_uses keeps only `tool_use` blocks from 'assistant' events. parse_stream ignores 'user' events, which carry tool_result blocks and their is_error flag. classify then accepts the review when `set(stats['paths_read']) & set(review_paths)` is non-empty. The fake CLI emits no tool_result events, so no test can catch this. Large paths under review are common here: scripts/rogue_node_tests.sh has thousands of lines and is a path under review in RM-2, PD-2 and most E2E slices. In this very review, a whole-file Read of _review_inputs/change.diff came back with the token-limit error. This is different from the known empty-review question (whether reading the diff counts): here a failed read counts as a successful one.",
      "failure_scenario": "Slice 4 or 7 reviews a change to scripts/rogue_node_tests.sh. The reviewer Reads the file without offset or limit, gets the token-limit error, and works from _review_inputs/change.diff and a few Grep calls, as RM-5, PD-4 and CL-1 showed reviewers do. The end entry records paths_read ['scripts/rogue_node_tests.sh'], status completed, and the report is released as a valid review. The launcher shows a confined, non-empty review where the approved rule should have failed it. The fix is small: drop a Read whose matching tool_result (by tool_use_id) has is_error, and add a fake-CLI scenario for it. If the owner prefers, it can go to slice 4 with the empty-review rule, but by the rules it needs a fix or the owner's decision.",
      "file": "scripts/run_independent_review.py",
      "id": "R5-B1",
      "kind": "blocking",
      "line": 410,
      "problem": "The empty-review rule counts any Read call on a path under review as reading it, even when the Read failed. summarise_paths adds a path to paths_read from the assistant's tool_use event alone. The launcher never looks at the tool_result, so a Read that returned an error still counts. The commonest error is the CLI's 'file content exceeds maximum allowed tokens' refusal for large files; a bad offset is another. A reviewer whose only Read of a path under review failed, and who then judged from the diff, passes the approved rule that 'a review that read none of the paths under review is failed'."
    },
    {
      "evidence": "In the record, the round 2 and round 4 'Task prompt (verbatim)' blocks hold bracketed placeholders, yet the reviewer answered the embedded content (for example 'Re-check of B1'), so the file it received held the real text. .gitignore line 15 is `artifacts/`. Every attempt-log entry has report_path artifacts/reviews/slice_2/*.json. The plan's success criterion says 'the exact invocation of any review can be rebuilt from its log entry'. The record already admits round 1 cannot be rebuilt (A1); with placeholders, rounds 2 and 4 cannot either, and no committed report can be checked against its hash.",
      "failure_scenario": "A slice-6 record check, the owner, or slice 4's reviewer tries to confirm that the record's reports are the ones the launcher released, or tries to rebuild round 2's prompt with invocation_from_entry. Neither can be done from the repository. The record's 'verbatim' claim is false, and the new AGENTS.md rule is broken in the very PR that adds it, which AGENTS.md says must not happen ('fix the rule or the repo in the same change'). Cheap fixes: commit the released JSON reports (they already passed the publication check) and paste the exact round-2 and round-4 task files. Or reword the record and the AGENTS.md sentence to say what is actually kept.",
      "file": "docs/slices/agentic-sdlc-poc/review_slice_2.md",
      "id": "R5-B2",
      "kind": "blocking",
      "line": 0,
      "problem": "The review record says it 'keeps the task prompts and the reports verbatim', and this PR's AGENTS.md now requires that. The plan also says 'The prompts are stored verbatim in the slice's review record'. But the round-2 and round-4 task prompts in the record are not verbatim: they contain placeholders, '[the round-1 report below, as the JSON the launcher released]' and '[the author's answers to round 1 below]'. The reports themselves are 'rendered from the released JSON'. The JSON files are written to artifacts/reviews/, which .gitignore excludes (`artifacts/`), so the committed attempt log's report_sha256 values and the round-2 and round-4 prompt_sha256 and full_prompt_sha256 values match nothing in the repository."
    },
    {
      "evidence": "report() writes the columns Case, Kind, Prompt, Status, Verdict, Detected, Location only, Unmatched blocking and Tries. advisory_only appears only in the stored JSON. No test calls report() and checks its columns; test_results_record_the_key_hash... checks only the exit code.",
      "failure_scenario": "Slice 4 re-measures RM-2 to RM-4 (recommendation 3). A reviewer again rates a secret-in-evidence finding as advisory, and the hand triage follows the --report table, which is exactly R3-2's failure scenario. The DPL-002 diagnosis is missed again. Fix before merge: add the column. It is one line.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R5-A1",
      "kind": "advisory",
      "line": 554,
      "problem": "The R3-2 fix only partly works. score() now fills advisory_only, but report(), which produces the 'Automatic scoring' table for benchmark_report.md, has no Advisory-only column. Round 4 accepted R3-2 because 'Future hand triage will see the advisory match in its own column'. That column does not exist."
    },
    {
      "evidence": "previous_state keeps lines by key_sha256 only, and finished cases are skipped by case/prompt. load_results refuses any line with another key. Nothing compares prompts_sha256. RESULTS_FILE = docs/slices/agentic-sdlc-poc/benchmark_results.jsonl. AGENTS.md says implemented slice bundles are frozen records.",
      "failure_scenario": "Case (a): slice 4 edits short.md (new review questions) and runs --run. Every case counts as done, so no call is made, and it exits 0 reporting '24 of 26'. Or a prompt edited during a usage-limit pause pairs reviews from two different prompts, and decide() compares them with no warning. Case (b): slice 4 edits the answer key. The budget silently restarts at 0 of 26, new lines are appended to slice 2's frozen results file, and --report then refuses everything until stage A's lines are deleted. Suggest a run or stage id and a results path per stage, with the prompt hash in the identity. Decide this in slice 4.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R5-A2",
      "kind": "advisory",
      "line": 308,
      "problem": "The runner cannot do slice 4's planned re-measurement cleanly. A result's identity is only the answer key's SHA-256. prompts_sha256 is recorded but never checked, either when resuming or in --report. RESULTS_FILE is fixed to this slice's bundle. A changed key resets the budget to zero and makes --report refuse the whole existing file."
    },
    {
      "evidence": "Attempt slice_2/c1/r3/impl/1 end entry: outside_calls 1, denied [], status failed. summarise_paths counts outside paths from tool_use events whether or not the call was denied. The plan's probe said 'all three tools denied outside'.",
      "failure_scenario": "After a CLI update, outside reads stop being denied. Every review that touches an outside path is still failed, so nothing is published, but the reviewer has read outside files and nobody notices the drift, because the log cannot separate 'denied' from 'not denied' for outside calls. Suggest logging, per outside call and without the path, the tool name and whether it was denied. This goes one step further than the known diagnosability item.",
      "file": "docs/slices/agentic-sdlc-poc/review_attempts.jsonl",
      "id": "R5-A3",
      "kind": "advisory",
      "line": 6,
      "problem": "The record explains round 3 attempt 1 as 'probably a Markdown link resolved from the copy root', but the log shows something the record does not mention: the outside call was not refused by the permission layer. The end entry has outside_calls 1 and denied []. Under the probed configuration (dontAsk, no allow rules), an outside Read, Grep or Glob should appear in permission_denials. So the call either named a path that does not exist, or went through. The launcher cannot tell which, and the preamble's 'reads outside it are denied' was not shown for that call."
    },
    {
      "evidence": "For a name other than Read, `paths = [str(args.get('path') or '.')]`, so Bash({'command': ...}) or WebFetch({'url': ...}) gives '.', which is inside. classify has no check that every tool_use name is in REVIEW_TOOLS.",
      "failure_scenario": "A CLI version where `--tools` no longer restricts the tool set, or where a built-in tool is always present, lets the reviewer run Bash or fetch a URL. The review is classified 'completed' and released. The canary would not catch it, because it does not test tool use. One line fixes it: fail any tool_use whose name is not in REVIEW_TOOLS.",
      "file": "scripts/run_independent_review.py",
      "id": "R5-A4",
      "kind": "advisory",
      "line": 383,
      "problem": "tool_paths treats any tool other than Read, Grep or Glob as naming the working directory, so a call to an unexpected tool counts as inside the copy. The escape check relies on `--tools` keeping working; it does not fail closed on a tool it does not know."
    },
    {
      "evidence": "call_reviewer has no timeout; main returns 0, 1, 2 or 3 as shown; _guarded_attempts catches only PublicationBlockedError; AttemptLog.entries refuses any non-JSON line; run_benchmark's result is ignored in main.",
      "failure_scenario": "A slice-7 loop hangs indefinitely on one stuck review, or treats a usage-limit pause as a failure and spends its retries. None of these is a false green. They are inputs for slice 7's design.",
      "file": "scripts/run_independent_review.py",
      "id": "R5-A5",
      "kind": "advisory",
      "line": 516,
      "problem": "Robustness for slice 7, which calls the launcher in a loop. (1) call_reviewer runs subprocess.run with no timeout, so a hung CLI holds the log lock forever. (2) Exit code 1 means failed, paused and pending alike, and exit 2 means both 'another launcher holds the lock' and invalid arguments, so a caller must parse stdout to know whether to wait for a reset, retry, or stop. (3) Any exception other than PublicationBlockedError in a reviewer thread (an OSError writing the partial report, a missing `claude` binary in cli_version) escapes as a traceback. It leaves a start entry that the next run marks 'interrupted' with no cause. (4) A partial line left by a kill during append makes every later run refuse until someone edits the append-only log by hand. (5) run_review_benchmark.main returns 0 even when it stopped at a pause or at the budget."
    },
    {
      "evidence": "Attempt log: round 2 paths_read is ['scripts/run_review_benchmark.py', 'tests/tools/test_run_review_benchmark.py']; round 4 paths_read is ['docs/slices/agentic-sdlc-poc/benchmark_report.md', 'scripts/run_review_benchmark.py'] (duration 16,961 ms). Round-2 report entries A4 and A8 give only the author's answer as evidence.",
      "failure_scenario": "Slice 7's loop relies on recheck rounds that pass on the author's word, so a fix that only claims to work (like R3-2) is closed. Suggest that slice 4's recheck rules require the recheck to open the changed code and test for each accepted answer, and that the record state what each recheck actually read.",
      "file": "docs/slices/agentic-sdlc-poc/review_slice_2.md",
      "id": "R5-A6",
      "kind": "advisory",
      "line": 0,
      "problem": "Earlier rounds missed what this round found. The causes are in the process. Rechecks were asked a closed question ('accept or re-raise'), and the empty-review rule is met by a single Read. Round 2 opened only the benchmark runner and its test with Read, yet it accepted the launcher fixes A1, A2, A3, A6 and A8. For A4 and A8 its only evidence was 'Author's answer' and 'Author's answer and the updated answer key'. Round 4 spent 17 seconds and opened two files. It accepted R3-2 on a claim (an own column) that is false (R5-A1). The record and the PR summarise both rounds as 'accepted every answer'. The A1-leftover fix (4ec4059) and the launcher fixes were never opened by any reviewer after round 1. I read them now and found no defect in them."
    },
    {
      "evidence": "leak_terms: [PLANT-] for PD-1 to PD-4; the patches contain no 'PLANT-'. PD-1 terms include \"401\" and the plant reads `in (401, 403)`; PD-3 terms include capiss_keys and the plant reads `../capiss_keys:/var/lib/capiss/keys:ro`.",
      "failure_scenario": "Stage A's '3 of 3 planted' result rests on the hand confirmation, which the report records, so stage A is not wrong. In a re-run that relies on the automatic columns, a blocking finding at those lines about something else would count as detecting the plant.",
      "file": "tests/review_benchmark/answer_key.yaml",
      "id": "R5-A7",
      "kind": "advisory",
      "line": 108,
      "problem": "Two weaknesses in the planted cases, which no round had under review. (1) Every planted case's leak term is 'PLANT-', which appears in no patch or copy, so the leak search for planted cases checks nothing. The plan asks for 'identifiers specific to the plant'. (2) Several expected terms are text from the planted line itself: '401' (PD-1), '|| true' (PD-2), 'capiss_keys' (PD-3) and '70' (PD-4). So any blocking finding at the location that quotes the change counts as a detection, whatever it says. The PD-3 patch itself is as the plan describes: a K1 key mount into OPA with a misleading 'already verified' note, at lines 413\u2013414, inside the range 410\u2013414."
    },
    {
      "evidence": "The coverage given in the prompt: run_review_benchmark.py lines 138, 187, 304, 347, 466, 492\u2013500 and 563; run_independent_review.py lines 353\u2013354, 456, 468 and 470. Stage A's real run did exercise the planted path once.",
      "failure_scenario": "A slice-4 change to planted_commit or dry_run, for example a wrong diff_base for planted cases giving an empty diff, or dry_run returning 0 with refused cases, passes every tooling test. It is noticed only after reviewer calls have been spent.",
      "file": "scripts/run_review_benchmark.py",
      "id": "R5-A8",
      "kind": "advisory",
      "line": 491,
      "problem": "Beyond the known untested refusal paths, some ordinary behaviour has no test. The planted-patch path is never run: planted_commit's `git apply` (line 138) and prepare_case's planted branch (line 187). dry_run (lines 492\u2013500), the pre-commit leak search the plan requires, is never run. Also untested: canary resume in finished() (line 304), run_item's canary dispatch (line 466), the provider-error-to-pending mapping in result_line (line 347), and report()'s canary row (line 563). In the launcher, validate_report's 'findings is not a list', 'unknown kind' and 'negative line' branches (lines 456, 468, 470) and non-JSON stream lines (lines 353\u2013354) are untested. They belong to the fail-closed schema check the PR lists."
    },
    {
      "evidence": "implementation_log.md 'Validation' line; the PR body; the coverage line 178 (`_check_attributes(info.read_bytes(), 'info/attributes')`); plan environment facts: 'The effect of --setting-sources \"\" on user-level settings was not probed'.",
      "failure_scenario": "A reader relies on 'each rule was broken on purpose' or 'nothing from the author's environment' and skips checking them in slice 4. Fix the wording before merge: it costs nothing.",
      "file": "docs/history/implementation_log.md",
      "id": "R5-A9",
      "kind": "advisory",
      "line": 35,
      "problem": "Some counts and claims are stale or overstated. The implementation log says 'make tooling-test (327 pytest, 9 shell)', but the R3-2 test made it 328, as the PR says. The PR says '97 new tests', while the evidence gives 65 + 33 = 98. The PR says 'Each confinement, admission, budget and canary rule was broken on purpose, and at least one test failed each time'. The known untested refusal paths, and the info/attributes copy check at line 178, make that statement false as worded. The PR also says nothing 'from the author's environment reaches the reviewer'. HOME is passed through, but the canary only tested project-level files, and the plan records that user-level settings and instructions under `--setting-sources \"\"` were not probed."
    },
    {
      "evidence": "run_round passes inputs.base_commit and prepare_case passes diff_base. Line 281 is uncovered. The A1 leftover ('has_diff fixed to true') existed only because of this option.",
      "failure_scenario": "None: it is extra code to maintain. Making diff_base required removes one branch from three functions.",
      "file": "scripts/run_independent_review.py",
      "id": "R5-S1",
      "kind": "simpler_alternative",
      "line": 280,
      "problem": "make_frozen_copy's optional diff_base, its `return None` branch, build_prompt's has_diff=False text and invocation_from_entry's has_diff handling serve a case that never happens. Both the launcher and the benchmark always pass a diff base."
    }
  ],
  "verdict": "no"
}
`````

</details>

### Author's answers

| Finding | Answer | Where |
| --- | --- | --- |
| R5-B1 | **Fixed.** A Read whose result is an error no longer counts as reading the path: the launcher matches each call to its result by ID. | `_failed_results`, `summarise_paths`; test `test_failed_read_of_the_only_path_under_review_does_not_count` |
| R5-B2 | **Fixed.** This record now keeps every task prompt and every released report verbatim, each with its SHA-256; a script checked every block against the attempt log, and all match. The rendered views stay for reading. | this record |
| R5-A1 | **Fixed.** `--report` has an "Advisory only" column. | `report` |
| R5-A2 | **Deferred to slice 4**, which plans the re-measurement: a run or stage ID, the prompt hash in a result's identity, and results per stage. | slice-4 input |
| R5-A3 | **Fixed.** Each call that names a path outside the copy is logged with its tool and whether the CLI denied it, never with the path. Round 3's first attempt predates this, so its cause stays unknown. | `summarise_paths` (`outside`); test `test_outside_calls_are_logged_with_tool_and_denial_but_no_path` |
| R5-A4 | **Fixed.** A call to any tool other than Read, Grep or Glob fails the review. | `call_stats` (`other_tools`), `classify`; test `test_call_to_a_tool_other_than_read_grep_and_glob_fails` |
| R5-A5 | **Deferred to slice 7**, the delivery loop: a timeout for the CLI call, distinct exit codes per outcome, exceptions in reviewer threads, a torn last line in the attempt log, and the benchmark's exit code. | slice-7 input |
| R5-A6 | **Deferred to slice 4** (stage rules): a recheck opens the changed code and tests for every answer it accepts, and the record says what each recheck read. | slice-4 input |
| R5-A7 | **Deferred to slice 4**: leak terms that identify each plant, and expected terms that do not quote the planted line. Stage A's planted results rest on the hand confirmation. | slice-4 input |
| R5-A8 | **Deferred**, with the untested refusal paths the owner chose not to fix in this PR; the lesson is slice-4 input (issue #33). | — |
| R5-A9 | **Fixed.** The counts and the two overstated claims are corrected in the implementation log and the PR description. | `implementation_log.md`; PR #35 |
| R5-S1 | **Not applied**: a refactor after the last review round; slice 4 changes these functions anyway. | — |

The two blocking findings are fixed. A recheck of the fixes would be round 6, which needs another
extension from the owner.
