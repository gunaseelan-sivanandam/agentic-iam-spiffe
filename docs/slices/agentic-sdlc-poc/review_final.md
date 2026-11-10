# Review record — agentic-sdlc-poc, unit `final`

The record of the review unit `final`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt final/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode final, commit `e318d95cafe8`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Final review of slice 4 of the agentic-SDLC PoC (issue #33, sub-issues #38 to #43)

## Intent

Slice 4's six plans and test plans are in `docs/slices/poc-4-1-review-prompts/` to `docs/slices/poc-4-6-stage-rules/`
(decisions S41-D* to S46-D*), merged into `poc/agentic-sdlc` by plan PR #48, the base of this review. The owner's goal
for the implementation run, and every choice the author made on the owner's behalf, every decision concern, growth
proposal, discovered issue and the dry slice's trip points, are in `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`.
The change is the whole slice: one final PR into `poc/agentic-sdlc`. Each sub-issue's implementation review, 4.4's
critique and 4.5b's report review are recorded in their bundles.

The owner's question for this review: **what does a plan promise that the change does not do, and what does the
change do that no plan asked for?** Count a decision the author recorded as implemented differently, or a growth the
author made without the owner's approval, as an answer to the second half.

## The author's self-review of the whole slice (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.** The reviewer CLI is 2.1.321 (the canary lines of
   `docs/slices/poc-4-5-benchmark/benchmark_results_B.jsonl`). A failed Read is marked as an error and never counts
   as read (the failed-Read probe, recorded in the decision page). The research sources were read on 2026-11-09 and
   2026-11-10 with a web-fetch tool; unreadable and paid ones are marked so in `research.md`. The owner's user-level
   grill-me skill was read for its text. The branch is not on GitHub, so no CI run exists for it; the brief says so.
2. **Each check added or changed, and its test.** The launcher's sections, modes, accounting and refusals
   (`tests/tools/test_run_independent_review.py`); the computed inputs (`tests/tools/test_review_inputs.py`); the
   records and their check (`tests/tools/test_check_review_records.py`); the lists' form, sources and `--stage`
   (`tests/tools/test_stage_checklists.py`); the benchmark runner (`tests/tools/test_run_review_benchmark.py`); the
   stage table, templates, grill-me and step references (`tests/tools/test_stage_rules.py`); the brief
   (`tests/tools/test_review_brief.py`); the lint gate's front-matter rule (`tests/tools/test_lint_changed_files.py`).
   764 tooling tests pass locally.
3. **Claims and what checks them mechanically.** Record blocks against attempt logs, and answers against findings:
   `make docs-check`. The benchmark's counts: the runner's report, kept verbatim in `benchmark_report.md`. Not
   mechanical: the author's blinded verdicts (27 of 125 match), the map from detections to checklist questions, and
   the text of each `AGENTS.md` rule against its decision.
4. **Fixes and their upstream choice.** The review records of each bundle hold every finding and its answer; the
   decision page's discovered issues 1 to 13 hold the author's own misses, among them a false claim in a self-review
   (issue 9) and a canary built on the review prompt (issue 12).
5. **Tried the way the next user runs it.** A dry slice from a clean session took a one-sentence change through the
   seven stages in a scratch clone; its 18 trip points and their dispositions are in the decision page. The full E2E
   suite passed on a clean stack, 120 of 120.
6. **Where each rule lives.** `AGENTS.md` (Review findings, Review loop, the slice workflow's stages, Independent
   review, Quality gates, coding rule 8), `docs/review_checklists/`, the slice templates, `.claude/skills/grill-me/`.
7. **What was removed, and its review.** The four-step workflow text (its rules moved into the stages, 4.6's
   review); stage A's run path of the benchmark (4.5a's review); the rebuild of prompts logged before 4.1, 4.2 and
   4.4 (refused with a message); the plan template's "Grill-Me Review Summary" section (replaced by the decisions
   table).

## Also

Is anything in `docs/STATUS.md`, `docs/slices/README.md`, `docs/history/implementation_log.md` or the decision page
now false for this commit?
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_brief.py: changed lines not run: 43, 95, 317, 321; branches not taken: 42->43, 94->95, 227->222, 277->280, 320->321 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 1418->1420 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/run_review_benchmark.py: changed lines not run: 313, 359, 634, 868, 1108, 1425-1426; branches not taken: 312->313, 316->315, 358->359, 438->442, 633->634, 801->798, 807->801, 866->868, 903->906, 1089->1087, 1250->1253, 1424->1425 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/lint_changed_files.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "check_docs.py:215 is the defensive return when spec_from_file_location gives None for a fixed, existing path next to the script. That cannot happen in practice and decides nothing.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "Line 43 is a loader failure on a fixed path. Lines 203-210 are the standalone main, which `make docs-check` does not call: it goes through check_docs.check_records into check_review_records(), which the tests exercise. The real coverage gap of the record check (4.1 and 4.2 records not checked) is a different matter, raised as FR-8.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Lines 43, 317 and 321 are the loader and the entry point. Line 95 (refusal on a git failure) and branch 277->280 (a final unit present, which is this PR's case) have no test: FR-9. Branch 227->222 is an accounted entry with an evidence status, which is benign.",
      "opened": [
        "scripts/review_brief.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV4",
      "note": "review_inputs.py:286 returns early when the interpreter has no user site-packages directory. It only skips the link, and the evidence commands then fail visibly (S42-D7).",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "189->191 is finish() on a section without a status line. 228->230 is truncation of a tail without a preceding round heading. Both are structural variants of the record writer and change no check outcome.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "166 is a loader failure on a fixed path. 906 is a log without a record (a defensive RuntimeError). 964-965: recovery that finds no section leaves the problem to the record check, which reports it. 1418->1420 is a HOME edge case. None is a decision path of the system under test; the untested launcher paths are tracked in #45 (STATUS item 4).",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "313 skips a missing expected file. 359 is a case without lists. 634 is record() without a sink. 868 skips an already-recorded refusal. 1108 is the stage-A fallback for false alarms. 1425-1426 is the --sample-confirmation CLI print. The branches are repeat and refusal variants. All are benchmark bookkeeping, and the 4.5b runs exercised them live. The benchmark's real problem lies in the confirmation verdicts, not in these lines (FR-1).",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The branch has not been pushed, and CI runs on pull requests and on pushes to main, so no run exists. The Implementation exit (every gate's CI job passes on the PR) and the brief's CI line must still be met after the PR is opened. Local runs are diagnoses (Quality gates).",
      "opened": [
        "AGENTS.md",
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "confirmation_key.jsonl lines 8, 43, 47 (T008, T043 and T047 are RM-6 open+list run 2, 1 and 2). confirmation_author.jsonl: T043 \"match\" (\"an untested refusal path \u2026 the log line's secret check\"); T008 and T047 \"no match\". confirmation_export.jsonl:43 gives T043's line as 586; :47 is T047 (blocking, \"No test uses a `~` path\"). benchmark_report.md:150, runner rows: the second RM-6 open+list row shows \"Detected E1, Detected (blocking) E1\", while the repeat line says \"RM-6 open+list: True, False\". Decision page issue 13 calls \"RM-6 detected twice\" false, which is what the committed rule gives. The 4.5b report review (review_report.md:395, :418) accepted the verdicts without checking them against the rule.",
      "failure_scenario": "The owner uses the repeats to tell chance from a real difference (S45-D6, S45-D8). The committed rule makes RM-6 open+list detected twice and short+list missed twice, so this discordance is reinforced. The report instead shows it as one hit and one miss, \"toward agreement\". If the strict reading (planted refusal paths only) were applied to T043 as well, open+list would fall to 6 of 11 and tie the other setups. Decision 2's \"open+list detected one case more\" would then disappear. Either way, the owner chooses the default setup from counts that rest on verdicts that are inconsistent and depart from the committed rule.",
      "file": "docs/slices/poc-4-5-benchmark/benchmark_report.md",
      "id": "FR-1",
      "kind": "defect",
      "line": 36,
      "origin_stage": "implementation",
      "problem": "On RM-6, the author's blinded verdicts do not follow the committed match rule. As a result, the report's repeat line and its statement that \"the repeats moved both cases toward agreement\" are not what the committed rule gives. The rule (answer_key.yaml:10-20) says that a defect of absence is also detected by a blocking or high finding that names one of its absence terms and one of its absence places anywhere in the finding. Blinded confirmation \"applies this rule\". In `open+list` run 2, T047 (RM6-B1, blocking: \"No test uses a `~` path\", file run_independent_review.py) and T008 (RM6-H1, high: \"This path has no test\", file run_independent_review.py) both meet that rule. The automatic score marked run 2 detected by a blocking finding. The author judged both \"a different defect, or not at the planted place\". Yet the author accepted T043 (run 1, RM6-2, line 586), which is equally outside every planted range ([130-140] \u2026 [843-855]), and RM-6 is counted as an `open+list` detection only because of T043. The same rule was applied loosely in one run and strictly in the other.",
      "severity": "high"
    },
    {
      "evidence": "poc-4-6-stage-rules/plan.md:56 (S46-D13: \"opens every plan PR and final PR \u2026 also for plan PRs, which carry the most text\"). AGENTS.md:176 (Discovery row: checks `make docs-check`, `make lint`; no brief). AGENTS.md:184-209 (Discovery subsection: no brief). AGENTS.md:275 (\"open the PR body with the decision brief\" sits only under Handoff). The 4.6 self-review point 3 says \"Not mechanical: that each of S46-D2 to S46-D14 is stated where AGENTS.md says it\", and no review quoted the text for D13.",
      "failure_scenario": "The next slice opens its plan PR by following the Discovery stage as written. No brief is pasted, so the owner again reads tens of thousands of words of plans and plan-review records without knowing where the owner: answers, decision concerns and rejected high findings are. That is the failure (O4) S46-D13 exists to prevent.",
      "file": "AGENTS.md",
      "id": "FR-2",
      "kind": "defect",
      "line": 275,
      "origin_stage": "implementation",
      "problem": "S46-D13 decides that \"A decision brief opens every plan PR and final PR\". `AGENTS.md` states the brief only in the Handoff stage, which is the final PR. The Discovery stage, which ends when the user merges the plan PR, has no rule for a plan PR's brief, and neither its stage-table row nor its subsection mentions one. The script supports plan PRs (it prints \"a plan PR has none\"), but no rule tells an author to use it there. The plan PR is the PR the plan says \"carry the most text\". AGENTS.md has no plan-PR brief rule; I searched for \"plan PR\", \"decision brief\" and \"review_brief\" in AGENTS.md (lines 21, 176, 181, 182, 203, 206, 275) and in the plan template.",
      "severity": "high"
    },
    {
      "evidence": "run_independent_review.py:1242-1248 (bundle ls-tree plus `diff --diff-filter=AMR merge_base..commit`). This prompt's finding-history list has no `docs/slices/poc-4-*/plan_review.md`. Glob shows all six exist. Upstream: S41-D4 (\"Its finding history is the review records of the slice's other units\") and S46-D3 (sub-issues share one plan PR, which is merged before the final PR). The two decisions together create the gap; the plan never said how the final review finds plan reviews that are already on the base.",
      "failure_scenario": "In a multi-sub-issue slice, a plan reviewer raises a high finding that the author rejects or defers to the implementation, and the implementation never addresses it. The final review is told to read the finding history and gets a list that omits the plan reviews. It anchors on the listed records and misses the dropped promise, which is the class of miss the final review exists to catch.",
      "file": "scripts/run_independent_review.py",
      "id": "FR-3",
      "kind": "defect",
      "line": 1242,
      "origin_stage": "implementation",
      "problem": "When a slice holds several sub-issues (S46-D3), the final review's finding history leaves out the plan-review records of its sub-issues. `final_records` takes every record in the final unit's own bundle and only the records the change adds or modifies elsewhere. Slice 4's six `poc-4-*/plan_review.md` files were merged with the plan PR (the merge-base), so none is listed. The governing bundle's slices 1\u20133 records (review_slice_1/2/3, review_industry_research, review_process_audit) are listed, although they are not this slice's units. S41-D4 and S46-D5 say that the final review's \"finding history is the other units' review records\", and a plan review is a unit of the slice.",
      "severity": "medium"
    },
    {
      "evidence": "slice_4_decisions.md:10, :44-45, :51, :94. poc-4-6-stage-rules/review_implementation.md:7-11 (\"Status: completed; approvable \u2026 yes\") and :308-322 (answers). STATUS.md:16 says \"4.1 to 4.6 implemented and reviewed\", which contradicts line 94 of the page.",
      "failure_scenario": "The owner reviews once at the end from this page, as the goal says. The page tells the owner that 4.6 has not been reviewed. Without the decision-to-text mapping, nothing shows that S46-D13's plan-PR brief (FR-2) is missing. A per-decision mapping is exactly the check that would have caught it.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "FR-4",
      "kind": "defect",
      "line": 10,
      "origin_stage": "implementation",
      "problem": "The owner's one page is out of date at this commit, and two of its own \"Done when\" items are unmet. (a) Line 10 says \"Last updated: 2026-11-09, 4.1 to 4.3 reviewed; 4.5a in review (round 1 answered)\". (b) The Progress row for 4.6 (line 94) says \"Implementation review next\", but poc-4-6-stage-rules/review_implementation.md holds a completed round 1 with all 11 answers. (c) \"Done when\" requires every decision ID of the six plans to be \"implemented and proven, or marked rule-text-only with its AGENTS.md line\". No such mapping exists: I searched the repository for \"rule-text\", and its only hits are the goal text itself and one plan review. (d) \"Done when\" also says this page \"holds the checklists\". The page neither holds nor links docs/review_checklists/ (searched the page for \"review_checklists\").",
      "severity": "medium"
    },
    {
      "evidence": "docs/STATUS.md:81-84, :99-102, :66-79. docs/history/implementation_log.md (diff lines 522-527) records the 2026-11-10 validation. delivery_problem_log.md:306 and :373.",
      "failure_scenario": "A reader of the \"where does the project stand\" document believes slice 4's plans are still under review. The reader finds no record of the last full verification, so the author's claim of 120 passing E2E tests (claim 5) has no entry in the place AGENTS.md names for it.",
      "file": "docs/STATUS.md",
      "id": "FR-5",
      "kind": "defect",
      "line": 84,
      "origin_stage": "implementation",
      "problem": "STATUS was edited in this change (dated 2026-11-10) but still says things that are false for this commit. \"Work in flight\" lists only `poc/slice-4-plans` with the state \"Plan reviews running; then one plan PR for the owner\". That plan PR (#48) is merged and is the base, and the branch in flight is `poc/slice-4-implementation`. \"Open delivery problems\" says DPL-010's preventive actions are \"pending in slice 4\", and it omits DPL-011, which the log still marks Open. \"Last verification\" has no row for the run this change claims: 120 of 120 E2E tests passed on a clean stack, `make qa-quality` passed, and 764 tooling tests passed, according to the implementation log.",
      "severity": "medium"
    },
    {
      "evidence": "delivery_problem_log.md:304-373. slice_4_decisions.md discovered issues 9, 12 and 13 and trip point 17. run_independent_review.py:97-98 (CREDENTIAL_NOTE). The decision page's trip point 18 leaves open \"whether a document made stale by an unmerged slice is a delivery miss yet\", for the final review to answer: these are misses found and fixed in the change, so they are entries now.",
      "failure_scenario": "The lessons of slice 4's own false claims (a dry run that did not refuse as a run does, a canary built on the review prompt) are left only on a decision page and in a PR body. The next slice's checklist research (S44-D9 tests the lists against the DPL entries) never sees them, and DPL-011 stays open with nothing to close it.",
      "file": "docs/delivery_problem_log.md",
      "id": "FR-6",
      "kind": "defect",
      "line": 373,
      "origin_stage": "implementation",
      "problem": "The delivery problem log has three gaps. (1) DPL-011 still says \"Open (fixes and their tests are in slice 4's plan PR; closed when it merges)\". The plan PR merged (it is the base), and the action it lists as pending in 4.1 (S41-D1's `<token>` note) is now in the launcher (CREDENTIAL_NOTE). (2) Slice 4's own delivery misses have no DPL entry: a false claim in a self-review (issue 9), a gate loosened before its cause was fixed (issue 12), a report that claimed RM-6 was detected twice (issue 13), and README's \"four-phase\" missed by 4.6's step-reference test and its review (dry-slice trip 17). The Handoff rule (base and new) requires DPL entries for \"delivery misses (a step skipped, a false claim, a review miss) found or fixed\". I searched the delivery_problem_log.md headings: DPL-001 to DPL-011 only. (3) DPL-010's \"Preventive (pending, slice 4)\" list still names \"a check of review records against the attempt log (slice 6 candidate)\", which 4.3 implemented.",
      "severity": "medium"
    },
    {
      "evidence": "AGENTS.md:275-286 against poc-4-6-stage-rules/plan.md:52 and :56. docs/slices/_template/plan.md (diff 773-776) against plan.md:54. AGENTS.md diff lines 106-107 against poc-4-1-review-prompts/plan.md:54. slice_4_decisions.md:96-147 (no row for any of the three). The owner's question for this review counts these as \"what the change does that no plan asked for\".",
      "failure_scenario": "The owner approves from the decision page, which says every author decision is listed and stays within the plans. The owner never sees that the rule for when the decision brief is pasted and edited, and the rule for what happens to a mislabelled blocker, now differ from the plan PR the owner merged.",
      "file": "AGENTS.md",
      "id": "FR-7",
      "kind": "defect",
      "line": 276,
      "origin_stage": "implementation",
      "problem": "The change does things no plan asked for, and the decision page's \"Decided by the author\" table does not record them. (a) The 4.6 F3 fix rewrote the handoff rule to \"built once CI has finished \u2026 and built again after a later push\" and \"a snapshot at handoff, and is not updated after the user's merge\". S46-D9 says that the PR body \"is a snapshot and is not updated later\", and S46-D13 says that \"the author pastes the brief at the top of the PR body\". Editing the PR body after later pushes changes an agreed decision, and AGENTS.md says such a fix goes to the user as a question first. (b) The plan template gained a \"Threat model\" section, which is not in S46-D11's list (stage table, source column, rule deviations); it is recorded only as dry-slice trip 5. (c) The Review loop's \"A finding labelled blocking that does not meet them is not fixed by default\" became \"is answered at the severity it does meet\". S41-D12 names every sentence that changes, and this sentence is not among them.",
      "severity": "medium"
    },
    {
      "evidence": "Grep for \"record_blocks\" under docs/slices finds it only in the 4.3, 4.4, 4.5 and 4.6 logs. poc-4-2-review-inputs/review_attempts.jsonl:9 and :11 have no record_blocks. check_review_records.py:166. poc-4-3-review-records/plan.md:41 (S43-D5's list).",
      "failure_scenario": "Someone edits an answer or a report block in 4.1's or 4.2's record after the fact. `make docs-check` stays green, and a reader trusts the rulebook's sentence that docs-check proves every record.",
      "file": "scripts/check_review_records.py",
      "id": "FR-8",
      "kind": "defect",
      "line": 166,
      "origin_stage": "implementation",
      "problem": "Self-review claim 3 says the record blocks are checked against the attempt logs, and the answers against the findings, by `make docs-check`. That is not true for 4.1's and 4.2's implementation reviews. Their start entries carry no `record_blocks`, so `check_log` skips them, and S43-D5's list of exempt records (slices 2 and 3, slice 4's plan reviews) does not name them. Only `review_brief.py`'s own guard covers their answers, and only when the brief is built.",
      "severity": "low"
    },
    {
      "evidence": "EV3: review_brief.py lines 43, 95, 317 and 321 not run; branches 94->95 and 277->280 not taken. review_brief.py:92-96 and :277-279.",
      "failure_scenario": "A later edit inverts the `if not brief.final` test. Every final PR's brief then says that a final PR needs a final unit, and every plan PR's brief says nothing, and no tooling test fails.",
      "file": "scripts/review_brief.py",
      "id": "FR-9",
      "kind": "defect",
      "line": 277,
      "origin_stage": "tests first",
      "problem": "Two paths of the brief have no test. Branch 277->280 is the case where a `final` unit is among the PR's units, which is the case for every final PR, this one included. Line 95 is the brief's refusal when a git command fails. The tests cover only a PR without a final unit.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to final/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| FR-1 | high | fixed: docs/slices/poc-4-5-benchmark/confirmation_author.jsonl, docs/slices/poc-4-5-benchmark/benchmark_report.md, docs/slices/agentic-sdlc-poc/slice_4_decisions.md: T008 and T047 are now matches by the absence clause, as T043 was, and the report says openly that they were re-judged after unblinding at this review's challenge; RM-6 `open+list` is detected in both runs, the repeat sentence says RM-6 kept the difference, and the first-run counts do not change. The origin was the author applying the clause by a "main claim" reading the rule does not have; every other verdict that differs from the automatic matches was checked (`confirmation_key.jsonl` against the results' `matches`): the eight others are term coincidences at the planted place (for example "the 5-second value has no probe" on FS-2), and the only other case with an absence clause, PB-3, has no rejected finding the clause matches |
| FR-2 | high | fixed: AGENTS.md: the Discovery stage says the plan PR's body opens with the decision brief, built by `scripts/review_brief.py` as at handoff, as S46-D13 decides |
| FR-3 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py: the final review's finding history holds every record of its own bundle and of every bundle the change touches, also records merged before the change, such as a sub-issue's plan review (`test_final_review_reads_the_merged_plan_reviews_of_the_bundles_the_change_touches`, which fails on the old code) |
| FR-4 | medium | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: the date line and the 4.6 progress row are current; a new section maps each of the 73 decisions of the six plans to where it is implemented and what proves it (a named test, a review record, or rule text with its `AGENTS.md` section), says the retirements are done, and links the six checklists with their sizes |
| FR-5 | medium | fixed: docs/STATUS.md: work in flight is `poc/slice-4-implementation`; the open delivery problems are DPL-010, DPL-011 and the new DPL-012, each closing when slice 4 merges; last verification has the 2026-11-10 runs (E2E 120 of 120, qa-evidence, qa-quality with the PR-mode trace gate, lint, tooling tests) |
| FR-6 | medium | fixed: docs/delivery_problem_log.md: DPL-010's preventive actions are marked implemented, with the record check under 4.3; DPL-011's status says what closes it; DPL-012 records slice 4's own misses (a self-review's false claim, a canary built on the review prompt and a gate loosened first, a report read from automatic scores, inconsistent verdicts, README's stale wording, unrecorded rule edits), with root causes, actions and a lesson; the dry slice's trip point 18 now points to it |
| FR-7 | medium | fixed: AGENTS.md, docs/slices/agentic-sdlc-poc/slice_4_decisions.md: (a) the handoff rule is back to S46-D9's and S46-D13's words, and the CI-line question goes to the owner as decision concern 10; (b) and (c) the plan template's "Threat model" section and the mislabelled-blocker sentence are recorded as author decisions, each with the rule it follows |
| FR-8 | low | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: an author-decision row and the decision map's S43-D5 row say that 4.1's and 4.2's records, built before 4.3, are not checked by `make docs-check` |
| FR-9 | low | fixed: tests/tools/test_review_brief.py: `test_a_pr_with_a_final_unit_gets_no_missing_final_line` and `test_a_base_git_cannot_resolve_is_refused` |
