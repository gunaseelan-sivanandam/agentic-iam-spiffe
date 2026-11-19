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

## Round 2

### Attempt final/c1/r2/A/1

Reviewer `A`: `claude-opus-5-5`, effort medium, mode recheck, commit `01da96dd4a9e`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Recheck of slice 4's final review, round 2

The intent is unchanged from round 1: slice 4's six plans (merged with plan PR #48, the base), the owner's question
"what does a plan promise that the change does not do, and what does the change do that no plan asked for?", and the
decision page `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`. Round 1's report and the author's answers are
below; the fixes are what the reviewed commit adds after `e318d95`. Among them: two RM-6 verdicts changed by the
match rule's absence clause after unblinding, which the benchmark report says; a rule for the plan PR's brief; the
final review's finding history widened to the merged records of every bundle the change touches; a map from each
of the 73 decisions to its proof on the decision page; the handoff rule returned to the plan's words, with the
question put to the owner; and DPL-012.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_brief.py: changed lines not run: 43, 317, 321; branches not taken: 42->43, 227->222, 320->321 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 1421->1423 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
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
      "item": "FR-1",
      "note": "confirmation_author.jsonl:8 and :47 now say match, with the absence-clause reason and an open note that they were re-judged after unblinding. benchmark_report.md:23-27 says so; :40-44 gives RM-6 open+list as detected twice and says RM-6 kept the difference; the runner's repeat line (:154) says True, True. The first-run counts (7/6/6) are unchanged because both findings are second runs. The decision page's 4.5b row notes the re-judging.",
      "opened": [
        "docs/slices/poc-4-5-benchmark/confirmation_author.jsonl",
        "docs/slices/poc-4-5-benchmark/benchmark_report.md",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-2",
      "note": "AGENTS.md:202-203 (Discovery) now says the plan PR's body opens with the decision brief, built by scripts/review_brief.py as at handoff, which matches S46-D13.",
      "opened": [
        "AGENTS.md"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-3",
      "note": "final_records (run_independent_review.py:1242-1251) now lists every record in every bundle the change touches, using ls-tree at the commit, so plan reviews merged earlier are included. The new test (test_run_independent_review.py:896-908) merges a plan review into the base, touches only that bundle's attempt log, and checks that the plan review is listed and the untouched bundle is not. On the old code, which took only AMR-changed records, the test would fail.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-4",
      "note": "The date line (:10) and the 4.6 progress row (:94) are current. A new section (:96-181) maps all 73 decisions (16+11+8+13+11+14) to where they are implemented and their proof, records that the retirements are done, and links the six checklists with their question counts.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-5",
      "note": "STATUS.md: work in flight is poc/slice-4-implementation (:86); DPL-010, -011 and -012 are listed as closing when slice 4 merges (:103-108); the 2026-11-10 E2E, qa-evidence, qa-quality, lint and tooling runs are recorded (:69-70). A misplaced DPL-008 sentence is noted under FR-10.",
      "opened": [
        "docs/STATUS.md"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-6",
      "note": "DPL-010's status and preventive actions are marked implemented, including the 4.3 record check (:306-309, :358-364). DPL-011's status says what closes it. DPL-012 (:419-465) records slice 4's misses with root causes, actions and a lesson. Dry-slice trip 18 points to it. One stale Preventive line in DPL-011 remains (FR-10, low).",
      "opened": [
        "docs/delivery_problem_log.md",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-7",
      "note": "(a) AGENTS.md:276-285 has the brief at the top of the PR body and the body as a snapshot not updated later, which are the words of S46-D9 and S46-D13; the CI-line question is decision concern 10 (decisions page :277). (b) The Threat model section is recorded as an author decision at :236 and (c) the mislabelled-blocker sentence at :234, each with the rule it follows.",
      "opened": [
        "AGENTS.md",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-8",
      "note": "The answer discloses the gap and does not fix it: decision page :235 and the S43-D5 row at :140 say that 4.1's and 4.2's records are not checked by docs-check. That is enough for a low finding.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "FR-9",
      "note": "test_review_brief.py:118-128 adds a test for a PR with a final unit (no missing-final line, which covers branch 277->280) and a test for a git merge-base failure being refused. EV3 no longer lists line 95.",
      "opened": [
        "tests/tools/test_review_brief.py",
        "scripts/review_brief.py"
      ],
      "status": "accepted"
    },
    {
      "item": "EV1",
      "note": "check_docs.py:215 is the defensive return when the loader of a fixed sibling file is None, which cannot happen for an existing path.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "Line 43 is the loader failure on a fixed path. Lines 203-210 are the standalone main; docs-check calls check_review_records() directly, and the tests exercise that. The coverage gap of 4.1 and 4.2 is disclosed (FR-8).",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Lines 43, 317 and 321 are the loader and the entry point. Branch 227->222 is an accounted entry with another status, which is benign. The earlier gaps (95, 277->280) are now tested (FR-9).",
      "opened": [
        "scripts/review_brief.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "review_inputs.py:286 returns early when there is no user site directory. It only skips the link, and the evidence commands then fail visibly (S42-D7).",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "189->191 is a section without a status line; 228->230 is a tail without a preceding round heading. Both are structural variants and change no check outcome.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "166 is a loader failure; 906 is a defensive log without a record; 964-965 is recovery that leaves the problem to the record check; 1421->1423 is a HOME that is the root. The untested launcher paths are tracked in #45.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "These are benchmark bookkeeping and CLI print branches (1425-1426 is the --sample-confirmation print). They decide nothing about the system under test, and the 4.5b runs exercised them live.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The branch is unpushed and CI runs on PRs, so no run exists yet. The CI result is still needed on the PR at handoff (the Implementation exit), and the CI-line timing question is decision concern 10.",
      "opened": [
        "AGENTS.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "delivery_problem_log.md:373-374 (the Status line names CREDENTIAL_NOTE as present) against :411-414 (the Preventive line says \"Pending in 4.1\"). STATUS.md:107-108.",
      "failure_scenario": "Someone deciding whether DPL-011 can close reads the Preventive line and thinks the `<token>` note still has to be built. The STATUS bullet makes it look as if DPL-008 is related to DPL-012.",
      "file": "docs/delivery_problem_log.md",
      "id": "FR-10",
      "kind": "defect",
      "line": 412,
      "origin_stage": "implementation",
      "problem": "The FR-6 fix updated DPL-011's Status line to say the `<token>` note is in the launcher (`CREDENTIAL_NOTE`). The entry's Preventive bullet still says \"Pending in 4.1 (S41-D1): the launcher's output section tells reviewers to write `<token>`\u2026\", so the same entry says the action is both done and pending. Separately, `docs/STATUS.md:108` adds \"DPL-008 closed on 2026-11-04.\" to the end of the DPL-012 bullet, where it does not belong.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to final/c1/r2/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| FR-10 | low | fixed: docs/delivery_problem_log.md, docs/STATUS.md: DPL-011's preventive bullet says the `<token>` note is implemented in 4.1 (`CREDENTIAL_NOTE`), and STATUS gives DPL-008's closing its own line |

## Round 1 (count 2)

### Attempt final/c2/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode final, commit `d818d8c57cc4`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Final review of slice 4 of the agentic-SDLC PoC, run again over the whole slice (2026-11-18)

## Intent

Slice 4's six plans and test plans are in `docs/slices/poc-4-1-review-prompts/` to `docs/slices/poc-4-6-stage-rules/`
(decisions S41-D* to S46-D*), merged into `poc/agentic-sdlc` by plan PR #48, the base of this review. Everything the
owner decided after them is on the decision page `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`: the owner's
decisions of 2026-11-13, round 2 (2026-11-14), the owner's decisions of 2026-11-16, round 3 (2026-11-17), round 4
(2026-11-17, R4-1 to R4-6), decision 8 (2026-11-18), the section "Direction for the next slices (the owner,
2026-11-18)" and the rows of "Decisions to make" and "Parked units, decision concerns and growth proposals" decided on
2026-11-18. The change is the whole slice: PR #49 into `poc/agentic-sdlc`.

The unit `final` first ran on 2026-11-10, before rounds 2 to 4. The owner reset its count to run it again over the
whole slice under the final mandate the launcher now ships (R4-1), in the owner's words on PR #49: "Reset the review
count of the unit `final` of slice 4: rerun the final review over the whole slice under the new final mandate". Every
other unit's review record, including those of the rounds after 2026-11-10, is in the copy.

## The author's self-review of the whole slice (claims to verify, not facts)

1. **Facts outside the repository.** CI on PR #49 at the reviewed commit: all 12 jobs passed, `e2e`,
   `unit-mutation`, `unit-trust` and `unit-diff-cov` among them. The agent's GitHub account has been suspended since
   2026-11-08, so the owner pushes, opens the PR and posts comments; the issues the PR body closes (#33, #38 to #43)
   were opened by that account and are hidden. The benchmark's reviewer calls ran on the pinned CLI 2.1.323; live
   reviews ran on the installed CLI of their day, as each attempt log records.
2. **Each check added or changed, and its test.** `tests/tools/` (1001 pass locally, and the shell tests 9): the
   launcher (`test_run_independent_review.py`), the computed inputs (`test_review_inputs.py`), the records and their
   check (`test_check_review_records.py`), the lists (`test_stage_checklists.py`), the benchmark runner
   (`test_run_review_benchmark.py`, including the tests that pin the three mandates to R4-1), the stage table and
   templates (`test_stage_rules.py`), the brief (`test_review_brief.py`), the docs check (`test_check_docs.py`) and the
   lint gate (`test_lint_changed_files.py`). Each new test's first failure on its base is in the commit bodies or
   `docs/history/implementation_log.md`.
3. **Claims and what checks them mechanically.** Record blocks against attempt logs, answers against findings:
   `make docs-check`. The benchmark's counts: the runner's report, kept verbatim in
   `docs/slices/poc-4-5-benchmark/benchmark_report.md`. Not mechanical: the blind verdicts, the research record's
   quotes against their sources, and the text of each `AGENTS.md` rule against its decision.
4. **Fixes and their upstream choice.** Every review record holds each finding and its answer; the decision page's
   discovered issues 1 to 65 hold what the work found, each with its disposition; `docs/delivery_problem_log.md`
   DPL-010 to DPL-017 hold the delivery misses, among them DPL-016: the slice was declared done on 2026-11-10 before
   its goal was tested, and the owner adopted six corrective actions that the next slice's plan writes into the
   rulebook, since one of them freezes process rules within a slice.
5. **Tried the way the next user runs it.** The dry slice of the decision page, under the rules of its day; a trial of
   the goal with the owner hands-off has not been run for this slice (DPL-016).
6. **Where each rule lives.** `AGENTS.md`, `tests/unit/AGENTS.md`, `docs/review_checklists/`, the slice templates,
   `.claude/skills/grill-me/`, the launcher (`MANDATES` and its prompt sections) and the benchmark's answer key.
7. **What was removed.** The four-step workflow text; stage A's run path of the benchmark; 4.1's three mandates; the
   `searched` field (round 3); the final question "What did everyone before you miss?" (R4-5).

Known and on the decision page: discovered issues 62 to 65 left as recorded by the owner; DPL-016's corrective actions
open until the next slice's plan merges.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 48, 227-230, 234; branches not taken: 47->48, 228->229, 228->230, 233->234 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_brief.py: changed lines not run: 43, 304, 308; branches not taken: 42->43, 236->229, 307->308 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_inputs.py: changed lines not run: 316; branches not taken: 315->316 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_independent_review.py: changed lines not run: 265, 1285, 1343-1344; branches not taken: 1284->1285, 1961->1963 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/run_review_benchmark.py: changed lines not run: 362, 409, 742, 986, 1306, 1856-1857; branches not taken: 361->362, 365->364, 408->409, 500->504, 741->742, 911->908, 917->911, 984->986, 1035->1038, 1287->1285, 1855->1856 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: CI run CI 44323928711 (pull_request): completed/success; jobs: qa-deploy: completed/success; unit-trust: completed/success; qa-trace: completed/success; unit-diff-cov: completed/success; tooling-test: completed/success; test-lint: completed/success; lint: completed/success; docs-check: completed/success; e2e: completed/success; unit-mutation: completed/success; gate-consistency: completed/success; unit-guard-check: completed/success

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
      "note": "scripts/check_docs.py:215 is the error return for when check_review_records.py cannot be loaded. It is a loader guard for a file that is always in the repository, and docs-check fails closed on it (it returns a problem). It is not a security decision path.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "Line 48 is the loader guard in _load_launcher, and lines 227-234 are main(). The tooling tests call check_review_records() in-process and `make docs-check` runs it through check_docs.check_records, so only the CLI entry point and the cannot-load guard go unrun. Both fail closed.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Line 43 is the loader guard, and lines 304 and 308 are main()'s success return and the __main__ hook. Branch 236->229 is an accounted entry whose status is an evidence status (explained or flagged); _collect_rechecks correctly ignores it. None of these can hide a brief item.",
      "opened": [
        "scripts/review_brief.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "Line 316 returns early when the interpreter has no user site-packages directory, so there is nothing to link into the scratch HOME. It is environment-dependent and harmless: the evidence commands then run without --user packages and would show as failed.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "No changed line of review_records.py is unrun; two branch arcs are untaken. Record writing and parsing are proved end to end by test_check_review_records.py, for example test_completed_attempt_leaves_prompt_evidence_and_report_blocks_that_the_check_accepts.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "Line 265 is the module-loader guard. Line 1285 guards against an attempt log without a record. Lines 1343-1344 are _complete_record's ValueError return when the section is missing, which, as the docstring says, is left to the record check to report. Branch 1961->1963 is a HOME equal to '/'. None of these is a decision that could pass a bad review.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "Benchmark runner lines: 362 skips an expected file absent from the copy, 409 handles a key without lists_commit, and the others are dispatch and retry arcs. Benchmark tooling only. The owner closed discovered issue 53 on 2026-11-18, accepting that the runner's similar retry and dispatch paths stay untested.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The CI run on the PR succeeded with all 12 jobs, including e2e, unit-mutation, unit-trust and unit-diff-cov. This matches the author's claim 1.",
      "opened": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "S41-D8 (line 123) cites `test_fixed_file_that_was_not_read_fails_even_when_a_path_under_review_was` and `test_a_rejection_counts_only_when_the_files_it_cites_were_read`; the tests are now `..._not_seen_...` (tests/tools/test_run_independent_review.py:1123) and `..._were_seen` (:1140). The same row cites `test_a_searched_file_need_not_be_read_but_an_opened_one_must`, which exists nowhere under tests/tools, and still describes `searched`, which R3-2 removed (scripts/run_independent_review.py:81-83). S41-D14 (line 129) says \"the launcher's mandates stay 4.1's\", but all three are R4-1's (scripts/run_independent_review.py:105-108). S45-D1 (line 164) cites `..._hard_stop_of_95` and says \"86 of 95 now\"; the test is `..._of_120` (tests/tools/test_run_review_benchmark.py:1590), BUDGETS is 120 (scripts/run_review_benchmark.py:70), and the page itself says 105 of 120 (line 742). S46-D6 (line 180) quotes \"Only the user waives a blocker that is still disputed\" as its AGENTS.md text; round 2 removed that sentence (review_round_2.md:80-81), and a grep of AGENTS.md finds no match. S44-D11 (line 161) quotes \"proposes the list item or the wording in the PR\"; AGENTS.md:409 now says \"on the slice's decision page\". Parked row 5 (line 828) still describes `searched` as done, and decision concern 11's row (line 829) cites `test_the_committed_keys_budget_is_the_stage_b_hard_stop`, which does not exist under that name.",
      "failure_scenario": "The owner checks a decision's proof on the one page the slice gives them. For S41-D8 they look for three named tests and a `searched` field: one test exists nowhere, two only under other names, and the field is gone. For S46-D6 and S44-D11 they look for quoted rule text that AGENTS.md no longer holds, and S41-D14 tells them the launcher still ships 4.1's mandates. The \"Done when\" claim rests on a table nobody re-checked against the current tree. This is the same cause DPL-017 records (records written from memory, not from the current state), recurring after DPL-017 was written. A frozen record with these errors misleads every later slice that reads it.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "FR2-1",
      "kind": "defect",
      "line": 123,
      "origin_stage": "implementation",
      "problem": "The decision page's table \"Decisions and their proof\", where the owner checks the first \"Done when\" criterion (every decision implemented and proven), still shows the slice as it stood around 2026-11-10 to 2026-11-13. Several rows name tests that no longer exist, quote rule text that has since been removed from AGENTS.md, or describe a launcher state that has changed.",
      "severity": "high"
    },
    {
      "evidence": "Dry-slice trip points 2 (\"Open: the owner's naming choice\"), 9 (\"Open: a rules question for the owner\"), 12 (\"Open, medium\"), and 3, 4, 8 and 16 (\"Open, low\") carry no issue reference (lines 923-937). Discovered issue 23 (line 869: \"A later benchmark run needs that pin or a new canary\") and issue 41 (line 887: \"once this branch merges, the launcher's copy can point to the rules instead\") are deferred work with no tracking. The discovered-issues table has no Tracking column, although the new template has one (docs/slices/_template/decisions.md:44). \"Decisions to make\" (lines 804-813) and the \"What remains for the owner\" text (line 10) list only decisions 3 and 4, the push and the reset, not trip points 2 or 9. Searched the decision page for \"Needed before\", \"issue to open\" and \"new issue\": no match.",
      "failure_scenario": "The page is frozen when slice 4 merges. The owner's two open choices (branch naming, and whether a low wording defect filed as a decision concern should go to the owner) and the medium trip point 12 (`--path` hints that fail the empty-review rule) exist only in a frozen table. No issue holds them and no \"needed before\" point is set, so the next slice never sees them: \"work lost in PR notes\", the failure S46-D9 exists to catch. The agent account's suspension explains why no issue could be opened, but not why these items are missing from the owner's list of actions.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "FR2-2",
      "kind": "defect",
      "line": 920,
      "origin_stage": "implementation",
      "problem": "Work found but not done, including items the page itself calls the owner's to decide, has no issue, no tracking reference and no entry among the owner's open items. The Handoff rule (S46-D9; base AGENTS.md step 4 and the new Handoff section) asks that such work become a GitHub issue, or a comment on the issue it belongs to, with each issue's link on the page.",
      "severity": "medium"
    },
    {
      "evidence": "`_unit_row` computes `opened` from len(brief.owner)+len(brief.concerns)+... and renders \"N for the owner\" (scripts/review_brief.py:201-203). On the decision page the brief shows `owner-decisions` \"2 for the owner\" and `poc-4-1-review-prompts` \"1 for the owner\" (lines 951, 957), but the items behind them (decision 7, decision concerns 1 and 11) are marked decided in lines 812, 819 and 829.",
      "failure_scenario": "An owner who reads the brief first, as AGENTS.md's Handoff tells them to, counts nine units with open items, then has to cross-check each against the rest of the page to find that none is still open. A label such as \"answered owner:\" instead of \"Open\" would avoid that.",
      "file": "scripts/review_brief.py",
      "id": "FR2-3",
      "kind": "defect",
      "line": 201,
      "origin_stage": "implementation",
      "problem": "The brief's \"Open\" column counts every `owner:` answer and every decision concern as \"for the owner\", including those the owner has already decided, so the owner's page shows decided items as open.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to final/c2/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| FR2-1 | high | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md, docs/STATUS.md, docs/slices/README.md: every row the finding names now states the current tree, keeping the decision's text and adding "since <decision>: …" with today's proof (S41-D8 names `..._not_seen_...`, `..._were_seen` and `test_a_report_with_a_searched_field_is_refused_by_the_schema` and says R3-2 removed `searched`; S41-D14 and S46-D5 say all three mandates are R4-1's, `test_the_launcher_ships_r4_1s_mandates_in_all_three_modes`; S44-D11 quotes today's "on the slice's decision page"; S45-D1 and decision concern 11 name `..._of_120`, 105 of 120 used; S46-D6 says round 2 removed the sentence and quotes today's Review loop and Review findings text; parked row 5 says R3-2 removed `searched`). Same cause searched for on the whole page, in `docs/STATUS.md` and the slice index: every `test_…` name checked against `def <name>` under `tests/`, every quoted `AGENTS.md` sentence of the proof table against `AGENTS.md`, every file path and `file:line` of the proof, decisions-to-make and parked tables; found and fixed S45-D5 (20 cases since R2-10), S46-D13 (the brief is on the decision page), decision 2's row, the final review's progress row, STATUS's branch row and owner list, the slice index row, and decision concern 16 still called open on the page, in `docs/slices/poc-4-5-benchmark/benchmark_report.md` and in `docs/delivery_problem_log.md`. Left as they are: three names in the round 2 and round 3 sections, which record what held then |
| FR2-2 | medium | fixed: docs/slices/agentic-sdlc-poc/slice_4_decisions.md, docs/STATUS.md, docs/slices/README.md, docs/delivery_problem_log.md: the work found but not done is in three locked issues labelled `slice`, each opening with "Needed before:", and a comment on #13: #50 (the author-prompts slice: DPL-016's actions, agent definitions, the authors' own check, discovered issue 41, trip points 3, 4, 5, 6, 12 and 16, FR2-3), #51 (the next benchmark run: discovered issues 15, 18, 23 and 37, decision concerns 16 and 19 as rules, 62 to 65 as set aside), #52 (a reviewer that runs tests), and #13 for trip point 8; the discovered issues have the template's Tracking column (an issue, `none:` with the reason, or `—` when closed); each open trip point names its tracking; trip points 2 and 9 are decision 9 under "Decisions to make", for the author-prompts slice's plan (#50); "What remains for the owner" is current on the page, in STATUS and in the slice index. The issues were opened as `guna-agent[bot]` by the owner's decision of 2026-11-18, recorded as a one-line rule deviation under "Decisions made" |
| FR2-3 | low | deferred: #50: the brief's "Open" column is listed there among the low items for the author-prompts slice, which changes the launcher and brief anyway; slice 4 freezes its process tooling (DPL-016, action 4) |

## Round 2 (count 2)

### Attempt final/c2/r2/A/1

Reviewer `A`: `claude-opus-5-5`, effort medium, mode recheck, commit `f7fd4117db19`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Recheck of slice 4's final review (count 2), round 2

The intent is unchanged from round 1 of this count: slice 4's six plans (merged with plan PR #48, the base), the
owner's later decisions on the decision page `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`, and the question
what a plan or decision promises that the change does not do, and what the change does that none asked for. Round 1's
report and the author's answers are below; the fixes are what the reviewed commit adds after `068edb2`. The author
claims, as claims to verify: the proof table "Decisions and their proof" and the page's status cells state the current
tree, and the same cause was searched for across the page, `docs/STATUS.md` and the slice index; the work found but not
done is tracked in issues #50, #51 and #52 and a comment on #13 (the reviewer cannot open GitHub; the issue texts are
not in the repository, so the page's Tracking column and lists are what can be checked), with the owner's open choices
in "Decisions to make"; the issues were opened as `guna-agent[bot]` under a rule deviation the owner decided on
2026-11-18, recorded under "Decisions made"; the brief's "Open" column (FR2-3) is deferred to #50.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
No process file changed since the reviewed round (d818d8c57cc4 to f7fd4117db19; git diff --numstat --no-renames <earlier attempt's commit> <commit>).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "There is no CI run for this commit. The change since d818d8c touches only five Markdown files under docs/ (see the diff headers). Under the base rules a gate's result is its CI conclusion on the PR, which the owner sees on PR #49. Nothing in this recheck rests on a gate result.",
      "opened": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    },
    {
      "item": "FR2-1",
      "note": "Every row the finding named now states the current tree. S41-D8 names the renamed tests (tests/tools/test_run_independent_review.py:1123 and :1140) and the schema test at :1197, and says R3-2 removed `searched`. S41-D14 and S46-D5 name test_the_launcher_ships_r4_1s_mandates_in_all_three_modes (tests/tools/test_run_review_benchmark.py:1623). S45-D1 and decision concern 11 name ..._of_120 (:1590) and 105 of 120. S44-D11 quotes AGENTS.md:409. S46-D6 quotes the Review loop (AGENTS.md:113) and the Review findings text (AGENTS.md:79-80). It also names the test at :1472. Parked row 5 now says `searched` is removed. Every test name the fix cites was found as a `def` under tests/. The same-cause edits (S45-D5, S46-D13, decision 2, the final review's progress row, the status of decision concern 16 in benchmark_report.md and delivery_problem_log.md, and the STATUS and slice-index rows) are in the diff. The fix adds no mechanism: it corrects existing records.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
        "_review_inputs/change.diff",
        "tests/tools/test_run_independent_review.py",
        "tests/tools/test_run_review_benchmark.py",
        "AGENTS.md",
        "docs/STATUS.md",
        "docs/slices/README.md"
      ],
      "quotes": [
        {
          "end_line": 123,
          "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
          "line": 123,
          "text": "| S41-D8 | `Accounting`, the read check; widened by the owner's growth of 2026-11-13 to the files a `rejected:` answer cites, with `searched` for files only searched; since R3-2 (round 3): a file counts as seen where a Read or a content Grep showed its lines (in a recheck also its lines in `change.diff`, decision concern 18), `opened` is unchecked and `searched` is removed | `test_recheck_that_does_not_account_for_every_answer_fails`, `test_fixed_file_that_was_not_seen_fails_even_when_a_path_under_review_was`, `test_a_rejection_counts_only_when_the_files_it_cites_were_seen`, `test_a_report_with_a_searched_field_is_refused_by_the_schema` |"
        },
        {
          "end_line": 129,
          "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
          "line": 129,
          "text": "| S41-D14 | the launcher's mandates stay 4.1's; since R4-1 (round 4): all three are R4-1's, the recheck and final by R4-4's outcome, the initial by decision 8 | the benchmark report; decision 2, revisited as round 4, and decision 8; `test_the_launcher_ships_r4_1s_mandates_in_all_three_modes` |"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "FR2-2",
      "note": "The discovered-issues table now has the template's Tracking column (line 848). Each row gives an issue, a reason after `none:`, or a dash when the issue is closed. Every open trip point of the dry slice names its tracking: #50, or #13 for trip point 8 (lines 926-940). Trip points 2 and 9 are decision 9 under \"Decisions to make\". That decision is timed for the author-prompts slice's plan and tracked in #50. The \"What remains for the owner\" text on the page, in STATUS and in the slice index is current. The issues were opened as guna-agent[bot] instead of gunaseelan-agent. That departs from the Git rules, but it is the owner's recorded decision, written as a one-line rule deviation with an expiry under \"Decisions made\", which meets the one-line-exception rule. I cannot check the contents of issues #50 to #52 here. Adding the Tracking column applies the existing template; it adds no new mechanism.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
        "_review_inputs/change.diff",
        "docs/STATUS.md",
        "docs/slices/README.md",
        "docs/delivery_problem_log.md"
      ],
      "quotes": [
        {
          "end_line": 926,
          "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
          "line": 926,
          "text": "| 2 | Branch names: `poc/slice-<n>-<topic>` has no `<n>` for a slice named by topic | Open: the owner's naming choice; decision 9; tracking: #50 |"
        },
        {
          "end_line": 936,
          "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
          "line": 936,
          "text": "| 12 | `--path` hints made the implementation review fail the empty-review rule when it read only the plan | Open, medium: growth proposal 5 is related; tracking: #50 |"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "FR2-3",
      "note": "The answer is deferred to #50, not fixed or rejected. The finding is low, so it is the author's choice, and the launcher and brief are frozen for this slice (DPL-016). The brief on the page (lines 950-961) still shows \"N for the owner\" for units whose items have been decided, as the finding said. I can't confirm here that #50 actually lists this item.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    }
  ],
  "findings": [],
  "verdict": "yes"
}
```

