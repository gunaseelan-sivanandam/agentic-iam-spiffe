# Review record — agentic-sdlc-poc, unit `owner-decisions-2`

The record of the review unit `owner-decisions-2`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt owner-decisions-2/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `f0eb19ee7e30`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Review of the owner's decisions of 2026-11-16: decision concerns 13 and 11

## Intent

After round 2, the benchmark's recheck case RC-3 (a `fixed:` answer that silences a finding by adding a repeated
step, where leaving the CI result out of the PR body would do) was accepted by both recheck wordings. The author
explained why on the decision page `docs/slices/agentic-sdlc-poc/slice_4_decisions.md` (decision concern 13): the
word "mechanism" was read as gate or job, so a step repeated after every push and a second copy of a fact kept
current did not count; and the same observation fitted two labels with opposite effects, a re-raise at the finding's
severity or a "simpler alternative", which is always low. The author offered three options and recommended B: change
the wording (the mechanism definition names a step added or repeated and a second copy of a fact kept current; a fix
that adds one is re-raised at its severity, not reported as a simpler alternative; a simpler alternative is a
mechanism the owner approved), then run RC-3 once on each recheck wording, 2 calls. The owner answered: "okay go ahead
and also increase the review counts to 85" (the decision page, "Decisions made", 2026-11-16): option B, and decision
concern 11, the stage-B budget raised from 60 to 85, confirmed.

The change is the commits after `bb817a8`: the decisions recorded (`e2399c7`); the launcher's prompt wording, its
own commit (`5941c56`, decision 2); the rulebook text (`42aef6a`); the hard stop of 85 with the key's budget checked
against it again (`ed061ba`), all three before the runs; RC-3's two new results and their blind verdicts
(`6627268`); the benchmark report (`03c02c0`); and the records (the decision page, the implementation log,
`docs/STATUS.md`, `docs/delivery_problem_log.md`). Round 2 itself was reviewed in its unit `round-2`.

## The author's self-review (claims to verify, not facts)

1. **Facts outside the repository.** The installed Claude CLI is 2.1.325, which has no canary; the two runs used a
   pinned install of 2.1.323, whose canary is valid and passed, as round 2's runs did (`cli_version` in each result
   line of `docs/slices/poc-4-5-benchmark/benchmark_results_B.jsonl`). The results file sums to 82 calls of the hard
   stop of 85.
2. **Checks added or changed, and their tests.** No check is added. The prompt text is pinned by
   `test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism` and
   `test_a_simpler_alternative_is_only_a_mechanism_the_owner_approved`; that both recheck wordings get it identically
   by `test_the_mechanism_question_reaches_both_recheck_wordings_and_every_initial_setup`. The budget:
   `test_stage_b_stops_at_its_budget_counting_retries_and_the_canary`,
   `test_a_key_whose_budget_is_above_the_hard_stop_is_refused_though_the_runs_budget_is_within_it`,
   `test_the_committed_keys_budget_is_the_stage_b_hard_stop`. Their failures on the code before each change are in
   the implementation log entry of 2026-11-16.
3. **Claims checked mechanically.** That the prompt text, the cases and the budget were committed before the runs: the
   commit order and the results' timestamps. That both runs re-raised R1-1: their accounted entries in the results
   file. Not mechanical: the blind verdicts on the two re-raises (a fresh session that, by its report, opened only the
   two exported rows and the match rule; decision concern 16 asks the owner whether such verdicts stand).
4. **Fixes and their upstream choice.** RC-3's miss is answered at its two causes in the wording, not by a new check.
   Round 2's workaround for the budget (a run's `--budget` checked instead of the key's) is removed now that the key's
   85 equals the hard stop, and the earlier check is restored.
5. **Tried the way the next user runs it.** The two runs went through the runner as a user runs it, after a dry run
   that built both prompts with the new wording and passed the leak search. The wording has not yet been used in a
   live review; this review is its first live initial review.
6. **Where each rule lives.** `AGENTS.md` ("Fixes stay within the agreed decisions", "Report sections", "Modes and
   prompts"); the launcher's `_MECHANISM`, `MECHANISM_RULES` and the output section's `kind` bullet; `BUDGETS` and the
   key; the decision page.
7. **What was removed.** The old mechanism wording and the old definition of a simpler alternative (a mechanism that
   could be removed or simplified); round 2's `--budget` workaround and its test.

Known and stated on the decision page: the wording's example, "again after every push", is RC-3's own answer phrase,
because the author wrote the wording from that case, so RC-3's pass cannot show that the wording catches other kinds
of growth; RC-3's reviewers get the rulebook of its base `e842e97`, which only prefers removing a mechanism; one run
per wording, RC-2 and the initial reviews not rerun.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 222, 1039, 1097-1098; branches not taken: 1038->1039, 1699->1701 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/run_review_benchmark.py: changed lines not run: 353, 400, 725, 969, 1276, 1808-1809; branches not taken: 352->353, 356->355, 399->400, 491->495, 724->725, 894->891, 900->894, 967->969, 1018->1021, 1257->1255, 1807->1808 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/check_review_records.py: changed lines not run: 48, 227-230, 234; branches not taken: 47->48, 228->229, 228->230, 233->234 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_brief.py: changed lines not run: 43, 301, 305; branches not taken: 42->43, 233->226, 304->305 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/review_inputs.py: changed lines not run: 303; branches not taken: 302->303 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
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
      "note": "These lines are not in the commits under review. The uncovered lines I saw (1039: the attempt log without a record; 1097-1098: ValueError when finishing a record) are fail-safe guards of 4.3's record machinery, reviewed in that unit. This unit's launcher changes are MECHANISM_RULES (136-148) and the kind bullet (527-530); test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism and test_a_simpler_alternative_is_only_a_mechanism_the_owner_approved run them. Lines 222 and 1699 are outside both changed regions.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "These are guard branches of the benchmark runner from 4.5a and round 2: a missing expected file (353), a case without lists (400), and similar. This change touches only BUDGETS (64-66) and check_budget's use (999-1000), and those lines are run by test_stage_b_stops_at_its_budget_counting_retries_and_the_canary and test_a_key_whose_budget_is_above_the_hard_stop_is_refused_though_the_runs_budget_is_within_it. None of the listed lines is one this change edited.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/tools/test_run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "scripts/check_docs.py is not among the files the 2026-11-16 commits changed: the implementation log's `git diff --name-only e2399c7 03c02c0` lists AGENTS.md, the launcher, the benchmark runner, their tests and the benchmark records. The uncovered line belongs to earlier sub-slices' reviewed changes.",
      "opened": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "scripts/check_review_records.py is not touched by this unit's commits, per the implementation log's file list. The uncovered lines are from 4.3 and round 2, which were reviewed in their own units.",
      "opened": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "scripts/review_brief.py is not touched by this unit's commits, per the implementation log's file list. The uncovered lines are from 4.6 and round 2, which were reviewed earlier.",
      "opened": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "scripts/review_inputs.py is not touched by this unit's commits; the uncovered line 303 is from 4.2 or R2-6, which were reviewed earlier. PROCESS_FILES' scope is open as decision concern 15.",
      "opened": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "Only two branches of scripts/review_records.py are not taken, and this unit's commits do not touch the file; it comes from 4.3, reviewed earlier.",
      "opened": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The implementation log says the branch is not pushed (\"CI (the branch is not pushed)\"), so no CI run exists. The local gates are claimed to pass on 03c02c0. This is no pass and no false claim; CI's verdict comes when the owner pushes.",
      "opened": [
        "_review_inputs/change.diff",
        "docs/STATUS.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "MECHANISM_RULES[\"initial\"] (lines 140-142): \"if it does, report it as a `defect`, not as a `simpler_alternative`\". There is no severity, unlike the recheck rule at 143-147. Output section line 535: \"`low` (style, preference) is the author's choice\". AGENTS.md:429-431 gives a severity only for the recheck. Under \"Ask before growing\" the user approves each addition, so an unapproved addition breaks a rule; it is not a preference. In RC-3's first run, recheck-A put exactly this kind of finding at low, through the simpler_alternative label (benchmark_report.md:150-153). No initial case ran under the new wording (benchmark_report.md:189-191).",
      "failure_scenario": "An initial review of a change that adds \"rewrite the summary after every push\" reports it as a low defect. Low findings are the author's choice, so the author leaves it. The step merges without the owner's approval: the same result RC-3's first runs had, now under the `defect` label.",
      "file": "scripts/run_independent_review.py",
      "id": "F1",
      "kind": "defect",
      "line": 140,
      "origin_stage": "implementation",
      "problem": "The initial-review mechanism rule says to report an unapproved mechanism as a `defect` but gives it no severity. The output section lets a reviewer file it as `low` (\"style, preference ... the author's choice\"), so an unapproved mechanism can still merge unfixed. Decision concern 13 closed that outlet only for rechecks (\"re-raise the finding at its severity\"). AGENTS.md has the same gap: \"A mechanism added without that approval is a defect\" names no severity, while the recheck half does.",
      "severity": "medium"
    },
    {
      "evidence": "Decision page line 304 (the owner's decision) and the task text describe option B as \"the mechanism definition names a step added or repeated and a second copy of a fact kept current\", with no example. The launcher's _MECHANISM (136-138) adds \"(such as \\\"again after every push\\\")\". benchmark_report.md:192-194: \"its example 'again after every push' is the answer's own phrase ... so a re-raise may show the reviewer matching the example\". The summary at benchmark_report.md:182-184 still says the runs show re-raising \"once the mechanism definition names a repeated step\".",
      "failure_scenario": "The owner reads \"both re-raised R1-1\" as evidence for option B and adopts it as measured. The re-raise may come from string-matching RC-3's phrase, so a fix that grows the process another way (DPL-007's base64 scan, a kept register) is accepted, as RC-3 was before. A neutral example, or none, would have made the 2 calls informative.",
      "file": "scripts/run_independent_review.py",
      "id": "F2",
      "kind": "defect",
      "line": 137,
      "origin_stage": "implementation",
      "problem": "The owner approved option B and two RC-3 calls to measure it. The author then put RC-3's own answer phrase into the wording as its example (\"again after every push\"). The owner's recorded option B does not contain this example. Because the author knew this was a confound before the runs, the only measurement the owner paid for cannot tell \"the wording works\" from \"the reviewer matched the example\". The example also now ships in every live review prompt.",
      "severity": "medium"
    },
    {
      "evidence": "leak_hits (523-539): texts = {\"rules\", \"upstream items\", \"task (name)\": _prompt_text(...) + case.task} plus the copy files. The built prompt from case_prompt (line 518, the identity over \"prompt\") is never searched. benchmark_report.md:194-195 admits it: \"the leak search passed because it checks the copy, the rules, the upstream items and the task, not the output section\".",
      "failure_scenario": "A later wording change copies a case's leak term (for RC-3, \"leaving the CI result out\" or \"adds a step\") into MECHANISM_RULES or the kind bullet. The leak search passes, the case runs with its answer in the prompt, and the benchmark records a detection that is a leak. Scanning the built prompt (case_prompt(...).prompt) would catch it, and needs no new mechanism.",
      "file": "scripts/run_review_benchmark.py",
      "id": "F3",
      "kind": "defect",
      "line": 523,
      "origin_stage": "implementation",
      "problem": "The benchmark's leak search claims to search \"what the reviewer gets\", but it scans only the rules, the upstream items, the task with its configuration's prompt files, and the copy. It does not scan the sections the launcher builds itself (output section, mechanism rules, kind bullet), although S45-D2 treats the whole prompt as what the reviewer gets. Now that the output section carries text written from a case, the gate cannot see a leak there.",
      "severity": "medium"
    },
    {
      "evidence": "AGENTS.md:420-423: \"it never adds a mechanism (a gate, check, CI job, process step, document, register or field; a step added or repeated ...)\". The output section's severity bullet calls \"new behaviour without a test\" high. Decision page line 453: \"whether rechecks now re-raise good fixes, or initial reviews over-report mechanisms, is unknown\". benchmark_results_B.jsonl shows 82 calls used against the hard stop of 85 (78 lines, four of them with 2 calls).",
      "failure_scenario": "A high finding about an untested fail-closed path is fixed by adding a tooling test. The recheck treats the test as \"a check added without the owner's approval\" and re-raises it at high. Under the one dispute round it can only go to the owner. This adds owner load and rounds, the opposite of what decision concern 13 wanted. For the owner: say that adding what an existing rule requires is not a mechanism, and/or run RC-2 on both wordings (2 calls).",
      "file": "AGENTS.md",
      "id": "F4",
      "kind": "decision_concern",
      "line": 420,
      "origin_stage": "requirements",
      "problem": "The widened definition counts any added check, document, field or step as a mechanism, together with \"a fix ... never adds a mechanism\" and \"a recheck re-raises a fix that adds one at the finding's severity\". It has no carve-out for what the rules already require a fix to add, such as a missing test for \"new behaviour without a test\" (a high finding by the output section) or a required log entry. Read literally, a recheck re-raises good fixes and sends them to the owner. Whether this happens is unmeasured: RC-2, whose `fixed:` answer adds tests, did not run under the new wording, although 3 of the 85 calls remain.",
      "severity": "medium"
    },
    {
      "evidence": "AGENTS.md:420-423 against run_independent_review.py:136-138. test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism pins only the launcher text (test_run_independent_review.py:1634-1636). AGENTS.md \"Modes and prompts\" (366-369) points to the AGENTS.md definition, while the prompt carries its own.",
      "failure_scenario": "A later edit to one copy (for example an exclusion added for required tests, as F4 asks) does not reach the other. Reviewers then see two definitions and follow whichever the prompt states, as RC-3's reviewers did.",
      "file": "AGENTS.md",
      "id": "F5",
      "kind": "defect",
      "line": 420,
      "origin_stage": "implementation",
      "problem": "The mechanism definition exists in two separately worded copies: AGENTS.md (\"a step added or repeated, such as one done again after every push\") and the launcher's _MECHANISM (\"a step that is added or repeated (such as \\\"again after every push\\\")\"). Nothing ties the two together. By the change's own definition, that is a second copy of a fact that must be kept current. Until this merges, reviewers also get the base AGENTS.md's older simpler-alternative definition (\"a mechanism that could be removed or simplified ... non-blocking\") next to the output section's narrower one. That is two conflicting definitions in one prompt; this review's own prompt has them. The benchmark report discloses it for RC-3 (benchmark_report.md:196-199) but not for live reviews in the meantime.",
      "severity": "low"
    },
    {
      "evidence": "run_review_benchmark.py:66 `BUDGETS = {\"A\": 26, \"B\": 85}`; answer_key.yaml:30 `budget: 85`; line 1793 `args.budget if args.budget is not None else key.budget`; test_run_review_benchmark.py:1516-1518. S45-D1 (poc-4-5-benchmark/plan.md:50) asks for \"A code constant per stage\".",
      "failure_scenario": "The next budget change edits one copy and not the other. Every run is then refused before any call, as in discovered issue 30, or a test fails. This costs a debugging round and not a false green.",
      "file": "scripts/run_review_benchmark.py",
      "id": "F6",
      "kind": "simpler_alternative",
      "line": 66,
      "origin_stage": "implementation",
      "problem": "The stage-B budget is stored twice: BUDGETS[\"B\"] (S45-D1's code constant) and the answer key's `budget: 85`. They are checked against each other (check_budget on both, lines 999-1000) and now pinned equal by test_the_committed_keys_budget_is_the_stage_b_hard_stop. Keeping these two copies in step caused discovered issue 30, round 2's `--budget` workaround and this change's undo of it. If a plain `--run` defaulted to BUDGETS[stage] and the key's budget field were dropped, one copy and its test would go.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to owner-decisions-2/c1/r1/A/1

| Finding | Severity | Answer |
| --- | --- | --- |
| F1 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py, AGENTS.md: an unapproved mechanism now has a floor severity wherever the rules call it a defect. `MECHANISM_RULES["initial"]` says "if it does, report it as a `defect` of at least `medium` severity, not as a `simpler_alternative`", and the output section's kind bullet, which every mode gets (the final review gets no mechanism rule, only this bullet), says "a mechanism added without that approval is a `defect` of at least `medium` severity", so such a finding is fixed (R2-1) and cannot be filed low as the author's choice; `AGENTS.md` says the same in Report sections ("a defect of at least medium severity, not a simpler alternative") and Modes and prompts ("which it reports as a defect of at least medium severity"). The recheck rule already re-raises at the finding's severity and is unchanged. The prompt text is its own commit (`10f2977`, wording only, decision 2), the rulebook `db39dd5`. Tests first: `test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism` and `test_a_simpler_alternative_is_only_a_mechanism_the_owner_approved` pin both texts; on `f0eb19e` with the new test file they failed at `:1636` and `:1665`. Searched for the same cause (a statement that an unapproved mechanism is a defect, without a severity): `MECHANISM_RULES`, the kind bullet, `AGENTS.md` (Fixes stay within the agreed decisions, Report sections, Modes and prompts, the review loop), `docs/review_checklists/`, `docs/slices/_template/`, `.claude/skills/`, `tests/review_benchmark/prompts/` and every script: the kind bullet was the one other place, fixed above |
| F2 | medium | fixed: scripts/run_independent_review.py, AGENTS.md, docs/slices/poc-4-5-benchmark/benchmark_report.md, docs/slices/agentic-sdlc-poc/slice_4_decisions.md: the example is removed at its origin, so the definition is the owner's option B as the decision page records it: `_MECHANISM` reads "a step that is added or repeated and a second copy of a fact that must be kept current are mechanisms too" (`10f2977`, wording only) and `AGENTS.md`, Fixes stay within the agreed decisions, "a step added or repeated and a second copy of a fact that must be kept current are mechanisms too" (`db39dd5`); `test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism` asserts that definition and that no mechanism rule holds "after every push" or "such as" (on `f0eb19e` it failed at `:1636`). The measurement is not rerun and no stored result changes: the benchmark report (the paragraph after the R2-9 counts table, RC-3's second runs and the read-together paragraph) and decision concern 13's row say plainly that RC-3's two re-raises ran under the wording with the example, which is no longer the shipped wording, so the shipped wording is unmeasured, and whether to measure it is the owner's (decision concern 17); discovered issue 37, DPL-013 and the implementation log say the same. Searched for the example in `scripts/`, `AGENTS.md`, `docs/review_checklists/`, `docs/slices/_template/`, `.claude/skills/` and `tests/review_benchmark/prompts/`: no other copy in a rule or prompt |
| F3 | medium | fixed: scripts/run_review_benchmark.py, tests/tools/test_run_review_benchmark.py, docs/history/implementation_log.md: `leak_hits` now scans the whole prompt each configuration of the case builds, `case_prompt(prepared, key, name).prompt`, which is the text the reviewer is sent (mandate, rules, list, upstream items, a recheck's earlier report and answers, task, and the launcher's own sections), in place of the rules, the upstream items and the task with its prompt files, which that prompt already holds; the copy scan is unchanged and `_prompt_text`, which assembled the prompt files' text, is removed, so there is one scan of the prompt, not a second (`f22bb89`). Tests first: `test_a_leak_term_only_in_a_part_of_the_prompt_the_launcher_builds_is_found` (a term only in the initial or the recheck mechanism rule, or only in a recheck case's answers) failed on `db39dd5` at `:239` (`assert [] == ['prompt (…): SECRET-LEAK-TERM', …]`) after its twin, the same case without the term, passed at `:232`; `test_problem_id_or_leak_term_in_the_inputs_is_refused` now finds a leak in the rules or the task under `prompt` (its rules and task cases failed on `db39dd5` at `:208`, where the hit was labelled `rules` or `task`). `--dry-run` over every case of the key afterwards: 20 of 20 cases pass the leak search, 67 prompts built, as before; no existing case hits a leak term (the implementation log's entry of 2026-11-16 records the commands and the first failure lines). Same cause elsewhere: discovered issue 28, a recheck case's earlier report and answers not scanned, is covered by the same change (its disposition on the decision page says so) |
| F4 | medium | owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md (decision concern 17): read literally, "a fix never adds a mechanism" with the widened definition makes a recheck re-raise good fixes that add what an existing rule already requires (a test for new behaviour, which the rules call high when missing; a handoff record such as a log entry), so they go to the owner under the one dispute round. Options: (a) a carve-out sentence in the rule and the prompt, "what an existing rule already requires of the fix, such as a test for new behaviour or a handoff record, is not an added mechanism"; (b) measure first: RC-2, whose `fixed:` answer adds tests, on both recheck wordings under the new wording, 2 calls; (c) both, and also RC-3 again under the shipped wording without its example (F2), 2 more calls: 4 calls, while 3 are left of 85, so the budget would go to 89; (d) neither now, leave both to slice 8. Recommendation: (c): add the carve-out first, then run RC-3 and RC-2 on both wordings (4 calls, about USD 1), because RC-3's result no longer covers the shipped wording and RC-2 is the only case that shows whether good fixes are now re-raised. It blocks nothing now |
| F5 | low | rejected: the prompt must carry its own copy of the definition while this branch is unmerged, because the reviewer receives the rules from the PR's base branch (AGENTS.md:334-335, the reviewer "receives the approved `AGENTS.md` … from the PR's base branch"; the launcher reads them at the base commit, scripts/run_independent_review.py:355-363 and scripts/run_independent_review.py:409), and the base's `AGENTS.md` (`3347754`, the rules section of this review's own prompt) has no definition of a step added or repeated and still calls a simpler alternative "a mechanism that could be removed or simplified". Dropping the launcher's copy now would leave every review before the merge without the definition; one home is possible only once this branch merges, when the launcher's copy can point to the rules instead: discovered issue 41 on docs/slices/agentic-sdlc-poc/slice_4_decisions.md, disposition "after the merge". The two definitions of a simpler alternative in one prompt have the same cause and end at the same merge. Meanwhile the two copies say the same: both lost the example (F2) |
| F6 | low | rejected: the key's `budget` is part of the answer key, which is committed before any run and whose hash every result records: the hash is of the whole key file (scripts/run_review_benchmark.py:201) and a result belongs to a key only by that hash or an `earlier_key_sha256` entry (scripts/run_review_benchmark.py:184-188), so dropping the field (tests/review_benchmark/answer_key.yaml:30) means a new key version for every later result. The two copies cannot drift unseen: `test_the_committed_keys_budget_is_the_stage_b_hard_stop` (tests/tools/test_run_review_benchmark.py:1540-1542) pins them equal, and a run checks both against the hard stop before any call (scripts/run_review_benchmark.py:991-992 with `check_budget` at scripts/run_review_benchmark.py:235-237). Low: the author's choice |

## Round 2

### Attempt owner-decisions-2/c1/r2/A/1

Reviewer `A`: `claude-opus-5-5`, effort medium, mode recheck, commit `7e1593708e13`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Recheck of the owner's decisions of 2026-11-16, review round 2

The intent is unchanged from round 1: the owner's decisions of 2026-11-16 on decision concerns 13 (option B: the
mechanism wording, then RC-3 on both recheck wordings) and 11 (the stage-B budget of 85 confirmed). Round 1's report
and the author's answers are below; the fixes are what the reviewed commit adds after `f0eb19e`, round 1's commit:
an unapproved mechanism is a `defect` of at least `medium` in the prompt (`10f2977`, wording only) and the rulebook
(`db39dd5`); the example that was RC-3's own phrase is removed from both, and the records say that RC-3's two
re-raises ran under the wording with the example, so the shipped wording is unmeasured; the benchmark's leak search
reads the whole prompt the reviewer gets (`f22bb89`); decision concern 17 puts the open measurement and a possible
carve-out to the owner.

The author's claims to verify: every local gate passed on `f22bb89`, and the later commits change only `docs/`; a
dry run over every benchmark case passes the new leak search. Known: in the author's own reruns of
`tests/tools/test_run_independent_review.py` and `tests/tools/test_run_review_benchmark.py`, the first of five runs
had one failure, not captured, while another session may still have been running tests; the next four passed.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 48, 227-230, 234; branches not taken: 47->48, 228->229, 228->230, 233->234 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_brief.py: changed lines not run: 43, 301, 305; branches not taken: 42->43, 233->226, 304->305 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_inputs.py: changed lines not run: 303; branches not taken: 302->303 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_independent_review.py: changed lines not run: 222, 1039, 1097-1098; branches not taken: 1038->1039, 1699->1701 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/run_review_benchmark.py: changed lines not run: 353, 400, 717, 961, 1268, 1800-1801; branches not taken: 352->353, 356->355, 399->400, 491->495, 716->717, 886->883, 892->886, 959->961, 1010->1013, 1249->1247, 1799->1800 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))
EV9: process file changed since the reviewed round: AGENTS.md, +11 -11 lines (f0eb19ee7e30 to 7e1593708e13; git diff --numstat --no-renames <earlier attempt's commit> <commit>)
EV10: process file changed since the reviewed round: scripts/run_independent_review.py, +7 -7 lines (f0eb19ee7e30 to 7e1593708e13; git diff --numstat --no-renames <earlier attempt's commit> <commit>)

Every changed line and branch run by the tooling tests: scripts/lint_changed_files.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "F1",
      "note": "Fixed. MECHANISM_RULES[\"initial\"] (140-142) now reads \"report it as a `defect` of at least `medium` severity, not as a `simpler_alternative`\". The kind bullet that every mode gets (527-530) says the same. AGENTS.md says it in Report sections (429-431) and in Modes and prompts (366-369). test_each_review_asks_whether_the_change_or_a_fix_adds_a_mechanism (1640) and test_a_simpler_alternative_is_only_a_mechanism_the_owner_approved (1665-1667) pin both texts. The fix changes wording only and adds no mechanism.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py",
        "AGENTS.md",
        "docs/history/implementation_log.md"
      ],
      "status": "accepted"
    },
    {
      "item": "F2",
      "note": "Fixed. _MECHANISM (137-138) and AGENTS.md (420-422) now give option B's definition with no example. The test asserts that no mechanism rule holds \"after every push\" or \"such as\" (1638). The records say plainly that RC-3's two re-raises ran under the wording with the example, so the shipped wording is unmeasured: benchmark_report.md:106-112, decision row 13, and decision concern 17 (slice_4_decisions.md:457). The fix adds no mechanism.",
      "opened": [
        "scripts/run_independent_review.py",
        "AGENTS.md",
        "docs/slices/poc-4-5-benchmark/benchmark_report.md",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "F3",
      "note": "Fixed. leak_hits (523-540) now scans case_prompt(prepared, key, name).prompt for each configuration, which is the same prompt the identity hashes. It replaces the per-part texts, so the change removes code rather than adding a scan. The new parametrized test (221-239) has a passing twin, and it finds a term placed only in the initial or recheck mechanism rule or only in a recheck case's answers. The rules and task cases now report the hit under `prompt` (191-208). I cannot rerun the dry-run claim (20 of 20 cases) in this read-only copy. It is consistent with the code and with the implementation log at 74-76.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/tools/test_run_review_benchmark.py",
        "docs/history/implementation_log.md"
      ],
      "status": "accepted"
    },
    {
      "item": "F4",
      "note": "This was a decision concern, and it is now with the owner as decision concern 17 (slice_4_decisions.md:457). The row states the carve-out and the measurement options, recommends one, and says it blocks nothing now. That is the right disposition: it is the owner's to decide.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "accepted"
    },
    {
      "item": "F5",
      "note": "The rejection holds. The reviewer gets AGENTS.md from the base commit (approved_rules(repo, base_commit)), and the base's rulebook does not have the new definition. Until the merge, then, the prompt must carry its own copy. The two copies now say the same thing, and discovered issue 41 tracks moving the definition to one home after the merge. The finding was low, so this is the author's choice.",
      "opened": [
        "AGENTS.md",
        "scripts/run_independent_review.py"
      ],
      "quotes": [
        {
          "end_line": 335,
          "file": "AGENTS.md",
          "line": 334,
          "text": "  and attempt log). It loads no instruction or settings files from the copy and receives the\n  approved `AGENTS.md` and `tests/unit/AGENTS.md` from the PR's base branch. A recheck receives its"
        },
        {
          "end_line": 409,
          "file": "scripts/run_independent_review.py",
          "line": 409,
          "text": "        rules_text=approved_rules(repo, base_commit),"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "F6",
      "note": "The rejection holds. The key's budget is in the hashed answer key file, and of_key ties every result to that hash. Dropping the field would make a new key version. The two copies are pinned equal by test_the_committed_keys_budget_is_the_stage_b_hard_stop (1540-1542), and run_benchmark checks both against the hard stop before any call (991-992). The finding was a low simpler alternative, so this is the author's choice.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/review_benchmark/answer_key.yaml",
        "tests/tools/test_run_review_benchmark.py"
      ],
      "quotes": [
        {
          "end_line": 201,
          "file": "scripts/run_review_benchmark.py",
          "line": 200,
          "text": "    return AnswerKey([_case(c) for c in data[\"cases\"]], int(data[\"budget\"]), data[\"model\"], data.get(\"effort\", \"high\"),\n                     launcher.sha256_bytes(raw), prompts, sha256_text(\"\".join(prompts[n] for n in sorted(prompts))),"
        },
        {
          "end_line": 188,
          "file": "scripts/run_review_benchmark.py",
          "line": 184,
          "text": "def of_key(key: AnswerKey, line: dict[str, Any]) -> bool:\n    \"\"\"Whether a result belongs to this key: produced with it, or with an earlier version that the key names in\n    `earlier_key_sha256`. Such a result keeps the score of its run; where that version's match rule differs from the\n    key's (R2-9), `--rescore B` scores it again under the key's rule, apart from the results.\"\"\"\n    return line.get(\"key_sha256\") in (key.sha256, *key.earlier)"
        },
        {
          "end_line": 1542,
          "file": "tests/tools/test_run_review_benchmark.py",
          "line": 1540,
          "text": "def test_the_committed_keys_budget_is_the_stage_b_hard_stop() -> None:\n    \"\"\"A plain `--run` takes the key's budget, so the committed key must be within the hard stop (decision concern 11).\"\"\"\n    assert bench.load_key(ROOT).budget == bench.BUDGETS[\"B\"]"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "EV1",
      "note": "The fix commits do not touch scripts/check_docs.py. The uncovered line 215 belongs to earlier sub-slices' reviewed changes.",
      "opened": [],
      "searched": [
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "The fix commits do not touch scripts/check_review_records.py. These guard lines come from 4.3 and round 2, which were reviewed in their own units.",
      "opened": [],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "The fix commits do not touch scripts/review_brief.py. These lines come from 4.6 and round 2.",
      "opened": [],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "The fix commits do not touch scripts/review_inputs.py. Line 303 comes from earlier units.",
      "opened": [],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "scripts/review_records.py has only two untaken branches, and the fixes do not touch the file.",
      "opened": [],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "The fixes changed lines 131-148 and 527-529, and the two mechanism tests run them. Lines 222, 1039 and 1097-1098 and branch 1699 are outside the changed regions. They are guards of 4.3's record machinery.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "The rewritten leak_hits (523-540) is not in the list, so the tests run it. The listed lines (353, 400, 717, 961, 1268, 1800-1801) are guard branches from earlier benchmark work that F3's fix does not touch.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The implementation log (103-105) says the branch is not pushed, so there is no CI run. The local gates are claimed to pass on f22bb89. I could not verify that claim here, and CI's verdict comes when the branch is pushed. The author's reported first-run failure in the tooling tests, not captured, cannot be verified either. The four reruns passed, and the author reports it openly.",
      "opened": [
        "docs/history/implementation_log.md"
      ],
      "status": "explained"
    },
    {
      "item": "EV9",
      "note": "These AGENTS.md changes are F1's severity wording and F2's removal of the example, at 366-369, 420-422 and 429-431. I read them, and they add no mechanism.",
      "opened": [
        "AGENTS.md"
      ],
      "status": "explained"
    },
    {
      "item": "EV10",
      "note": "These launcher changes are the _MECHANISM, MECHANISM_RULES and kind-bullet wording plus its comment (131-148, 527-529). I read them, and the two tests pin them.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    }
  ],
  "findings": [],
  "verdict": "yes"
}
```

