# Review record — poc-4-6-stage-rules, unit `implementation`

The record of the review unit `implementation`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt implementation/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `dd60df14716b`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Implementation review of slice 4.6 (stage rules, issue #43)

## Intent

The approved plan and test plan are `docs/slices/poc-4-6-stage-rules/plan.md` (decisions S46-D1 to S46-D14) and
`test_plan.md`, merged into `poc/agentic-sdlc` by plan PR #48 (the base of this review). Slice 4.6 replaces the
four steps of `AGENTS.md`'s slice workflow with seven stages (a table of what each produces, its review and list, its
checks and its exit), moves every rule of the old steps into its stage, and states the decisions on discovery
without a grill-me, larger chunks, upstream corrections, the final review, waivers, earlier escalation, test-first
working rules, the handoff of discovered issues, discoverability, the templates, the decision brief
(`scripts/review_brief.py`) and the grill-me skill kept in the repository. The reviewed commit also holds slices
4.1 to 4.5, each reviewed in its own unit; 4.6's commit is `dd60df1`.

## The author's self-review (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.**
   - The grill-me skill: `cat ~/.claude/skills/grill-me/SKILL.md` shows YAML front matter (`name`, `description`), no
     `#` title, three short paragraphs, and two lines that end mid-sentence in `>` (the description and the second
     paragraph). It never asks which keys, sockets and secrets a slice touches, although `AGENTS.md` said grill-me
     always asks it. The repository copy keeps the front matter, adds a title and a purpose paragraph, completes the
     two sentences and adds the assets question.
   - The public API for the brief's CI line: running `python3 scripts/review_brief.py --base origin/poc/agentic-sdlc`
     on this branch gave six units, four decision concerns and "CI of `<commit>`: no run for this commit; not a pass"
     (the branch has never been pushed).
   - Step references: the plan's probe pattern ("step 1" to "step 4") found `AGENTS.md`, `docs/STATUS.md`,
     `docs/test_spec.md` and the test-plan template; all are rewritten. The delivery problem log's history says
     "workflow steps 1, 2 and 4" and "steps 3–4" of a milestone; those are history and stay.
2. **Each check added or changed, the case it catches, and its test.**
   - Stage table (`tests/tools/test_stage_rules.py`): a stage missing, an empty cell, a review naming a list that does
     not exist, a review naming neither a list nor the final mode nor the user's approval, the table missing; one
     negative case each.
   - Templates: the plan template without a stage, the Source column or "Rule deviations"; the test-plan template
     without a stage's list or one of the required review questions; a bundle made from the templates passes the
     lint gate's header check and resolves its links from `docs/slices/sample/`.
   - The lint gate's Markdown header check skips a leading front-matter block (`tests/tools/test_lint_changed_files.py`:
     front matter then a title and paragraph passes; front matter then no title, front matter only, and front matter
     never closed fail). The grill-me file passes it, and loses it without its title.
   - Step references: no live document holds one; a planted "See step 4" is found.
   - The brief (`tests/tools/test_review_brief.py`): from launcher-written records in a throwaway repository, each
     unit's verdict and counts, `owner:` answers, decision concerns, `cannot determine`, a finding disputed after its
     recheck, and rejected blocking or high findings; a unit with nothing open says so; an unanswered finding or an
     edited Prompt block makes it fail and `main` write no brief; the CI line for all passed, running, failed,
     skipped, no run, a run without jobs, another commit's run, an unreadable API and no GitHub remote.
   - 752 tooling tests pass locally (`make tooling-test`); `make docs-check` and `make lint` pass.
3. **Claims and what checks them mechanically.** The stage table, the templates and the step references: the tests
   above. "The brief cannot omit what the records hold": it runs the record check on every changed log and checks
   every completed attempt's answers itself, and fails otherwise (tested). Not mechanical: that each of S46-D2 to
   S46-D14 is stated where `AGENTS.md` says it, and that no rule of the old four steps was lost; the list in point 7 is
   the author's mapping.
4. **Fixes and their upstream choice.** No reviewer findings yet. The author's own: the step-reference pattern first
   matched "steps 3–4" in the delivery problem log's history; it now uses the plan's probe pattern, singular "step".
5. **Tried the way the next user runs it.** The brief ran on this branch as the next author will before opening the
   PR. No slice has yet gone through the seven stages; slice 4's end includes one dry slice from a clean session.
6. **Where each rule lives.** `AGENTS.md`: the slice workflow (the stage table and a subsection per stage), the
   review loop (only the user waives a disputed blocker; earlier escalation), the Start here row (how to run a review,
   where records live), the Independent review section ("Plan review (discovery)", "Implementation review
   (implementation)"). The templates. `.claude/skills/grill-me/SKILL.md`.
7. **What was removed, and its review.** The four-step text. Its rules moved: step 1's grill-me, assets question,
   plan contents, environment-fact probes, review before the user sees the plan, approval by merge, implementing only
   from the merged plan, and working by the base branch's rulebook go to Discovery; step 2's "only from the reviewed
   test plan", "return to step 1", expected outcomes, positive twins and static proof go to Tests first, and "update
   requirements, architecture and `trace/tests.yaml` before runtime code" to Requirements and architecture; step 3 goes
   to Implementation; step 4's gate runs go to Implementation, its `docs/test_spec.md` rule to Tests first, and its
   log, STATUS, slice index, problem logs, issues and PR body to Handoff. The plan template's "Grill-Me Review Summary"
   section became the Decisions table, whose rows record what a grill-me resolved.

## Questions (a minimum, from the test plan)

1. *Tests:* for each new or changed test, which wrong behaviour would still pass it?
2. *Keys:* does a key, socket or secret now reach a service outside its holders?
3. *Rules:* for each of S46-D1 to S46-D14, where is the text that states it? Does any rule now contradict another?
   Was any rule of the old four steps lost?
4. *Practicality:* can an author follow the stages for a one-line fix without inventing work ("none, with a reason")?
5. *Names and headers:* do new files and names say what they do?
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/review_brief.py: changed lines not run: 44, 96, 141, 269, 294, 298; branches not taken: 43->44, 95->96, 140->141, 207->202, 211->209, 264->269, 297->298 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 1418->1420 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/run_review_benchmark.py: changed lines not run: 306, 352, 627, 862, 1102, 1397-1398; branches not taken: 305->306, 309->308, 351->352, 626->627, 794->791, 800->794, 860->862, 897->900, 1083->1081, 1242->1245, 1396->1397 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
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
      "note": "Untested lines 141 and 211->209 are flagged as F1. Line 44 (loader failure), 96 (git failure), 269 (no findings), 294 and 298 (main's success path and the entry point) are minor or defensive and need no finding.",
      "opened": [
        "scripts/review_brief.py",
        "tests/tools/test_review_brief.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV2",
      "note": "check_docs.py:215 is the defensive branch where `spec_from_file_location` returns None for a fixed existing path. It is not a realistic path and comes from slice 4.3.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Lines 43 (a loader failure on a fixed path) and 203-210 (the standalone `main`) are not run. The `make docs-check` path runs through check_docs.check_records into `check_review_records()`, which the tests exercise, and the Makefile does not call `main`.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "review_inputs.py:286 returns early when the interpreter has no user site-packages directory. It only skips linking, which is harmless (slice 4.2 scope).",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Branches 189->191 (a section without a status line) and 228->230 (a tail without a preceding round heading) are minor structural variants of slice 4.3's record writer and decide no outcome.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "166 is a loader failure on a fixed path. 906 is defensive (a log without a record). 964-965 swallow ValueError when recovery finds no section, which the docstring leaves to the record check (and that check reports it). 1418->1420 is HOME equal to '/'. All are slice 4.1 to 4.3 code reviewed in their own units.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "These are run_review_benchmark.py (slice 4.5) lines, reviewed in that slice's own unit. They are not part of 4.6's change, and I did not inspect them in this review.",
      "opened": [],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "No CI run exists because the branch has not been pushed or had a PR opened. CI runs only on pull_request and on pushes to main. The Implementation exit (\"every gate's CI job passes on the PR\") must still be met before merge. The local claim of 752 passing tests is a diagnosis, not a gate result. Related to F3.",
      "opened": [
        ".github/workflows/ci.yml"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "EV1 lists line 141 and branches 140->141 and 211->209 as not run. `grep record_blocks docs/slices` matches only the 4.3, 4.4 and 4.5 logs. `check_review_records.check_log` (line 166) checks only attempts with `record_blocks == 1`. `tests/tools/test_review_brief.py` has no case with a completed attempt and no Report block. The self-review claims \"The brief cannot omit what the records hold\". AGENTS.md classes an untested fail-closed path outside the system under test's security decisions as high.",
      "failure_scenario": "A later edit inverts or drops the `attempt.report is None` branch. For example, `_attempt` starts returning a parsed report of `{}` when the heading is missing. The brief then prints a 4.1 or 4.2 unit with \"no completed attempt\" or zero findings and \"nothing open\" instead of failing, and every tooling test still passes.",
      "file": "scripts/review_brief.py",
      "id": "F1",
      "kind": "defect",
      "line": 141,
      "origin_stage": "tests first",
      "problem": "The brief's own fail-closed guards for attempts that the record check skips are untested. These are line 141 (a completed attempt whose record holds no Report block) and branch 211->209 (a re-raised finding answered again with something other than `rejected:`). These guards are the only completeness check for attempts logged before slice 4.3. This very PR holds such attempts: the 4.1 and 4.2 attempt logs have no `record_blocks` field, so `check_log` skips them.",
      "severity": "high"
    },
    {
      "evidence": "`last = (reported[-1].end or {}).get(\"verdict\", ...)` ignores `start['reviewer']`. No test in `tests/tools/test_review_brief.py` has two reviewers in a round. Slice 4.4 was critiqued by two models, so rounds with several reviewers do happen.",
      "failure_scenario": "Round 2 has reviewer A (verdict \"no\") logged before reviewer B (verdict \"yes\"). The brief shows the unit's last verdict as \"yes\". The owner, who per S46-D13 reads only where the brief points, sees an approvable unit that one reviewer did not approve.",
      "file": "scripts/review_brief.py",
      "id": "F2",
      "kind": "defect",
      "line": 173,
      "origin_stage": "implementation",
      "problem": "`Last verdict` is the verdict of the last completed attempt of the unit, whoever ran it. The rulebook lets several reviewers share a round (\"Several reviewers in one round count as one round\"), and the launcher keys verdicts by (round, reviewer) (run_independent_review.py:1024). The brief therefore shows one reviewer's verdict for the whole round.",
      "severity": "medium"
    },
    {
      "evidence": "AGENTS.md:275-284 (Handoff: open the PR body with the brief; the PR body is a snapshot). The self-review, point 1: \"CI of `<commit>`: no run for this commit; not a pass\" and point 5. ci.yml has `on: pull_request` and `push: branches: [main]`. Also, the final review's record commit moves the head, so the brief must be built after that commit's CI finishes.",
      "failure_scenario": "Every author follows the self-review and pastes the brief when opening the PR. Every brief says \"no run\", the CI line S46-D13 asks for never carries information, and an author who re-runs it after CI must break the \"not updated later\" sentence.",
      "file": "AGENTS.md",
      "id": "F3",
      "kind": "defect",
      "line": 282,
      "origin_stage": "discovery",
      "problem": "No rule says when to build the decision brief relative to CI. CI runs only on `pull_request` and on pushes to `main` (.github/workflows/ci.yml:5-10), so a brief built before the PR is opened always shows \"no run for this commit; not a pass\". The self-review says the brief ran \"as the next author will before opening the PR\". Handoff also says \"the PR body is a snapshot and is not updated later\", which discourages the edit needed to show the real CI result. The stage table's Handoff check (\"the CI result of the PR's head commit\") is therefore always empty in practice.",
      "severity": "medium"
    },
    {
      "evidence": "slice_4_decisions.md:142: \"the user-level copy is left in place for the owner to remove\". plan.md environment facts, row \"The grill-me skill\": content only. AGENTS.md:188: \"Grill-me always asks which keys, sockets and secrets the slice touches\". No probe of skill precedence appears anywhere in the bundle.",
      "failure_scenario": "The next slice runs `grill-me` in this repository. The user-level skill loads, so the interview never asks the assets question and runs the unreviewed prompt. AGENTS.md's claim and S46-D14's purpose (the versioned prompt runs discovery) are then false until the owner deletes the personal copy, and nothing tells the owner to.",
      "file": ".claude/skills/grill-me/SKILL.md",
      "id": "F4",
      "kind": "defect",
      "line": 1,
      "origin_stage": "discovery",
      "problem": "The repository copy of grill-me has the same name as the user-level copy, and that copy is deliberately left in place (slice_4_decisions.md:142). In Claude Code, when skills share a name, the personal location takes precedence over the project location. The truncated user-level skill, without the assets question, would then keep running discovery. The plan's environment facts probed only the content of the user-level file, not which copy loads.",
      "severity": "medium"
    },
    {
      "evidence": "AGENTS.md:163-165: \"a small fix still gets a plan ..., tests first, an independent review and the close-out\". The template rows `| Discovery | yes |`, `| Final review | yes |`, `| Tests first | yes, or none: <reason> |`. The Discovery exit: \"the user merges the plan PR\". The plan's cost table: final review costs \"One or two open rounds per slice\".",
      "failure_scenario": "For each one-line fix, an author either spends three review units and two PRs (USD 6-9 at the plan's estimates) or writes a \"Rule deviations\" line with the user's words. This goes against \"Prefer the smallest check\". The owner should decide whether Final review (and a separate plan PR) may be \"none, with a reason\" for small fixes.",
      "file": "docs/slices/_template/plan.md",
      "id": "F5",
      "kind": "decision_concern",
      "line": 665,
      "origin_stage": "discovery",
      "problem": "Practicality question 4: a one-line fix cannot follow the stages without extra work. The template fixes Discovery, Final review and Handoff to \"yes\", and S46-D5 requires a `final` unit per slice. A one-line fix therefore needs a plan PR merged by the user, a plan review, an implementation review, a final review and a second PR: at least three review units and two merges. The workflow's opening sentence also disagrees with the stages. It says a small fix gets \"tests first, an independent review\", while the template lets Tests first be \"none\" and the stages require several reviews.",
      "severity": "medium"
    },
    {
      "evidence": "docs/STATUS.md:15-17; docs/slices/README.md (the 4.6 row); slice_4_decisions.md:94.",
      "failure_scenario": "A reader of STATUS, which is the \"Where does the project stand\" document that S46-D10 makes the home of open PoC work, believes 4.6 has not started and plans or reviews accordingly.",
      "file": "docs/STATUS.md",
      "id": "F6",
      "kind": "defect",
      "line": 17,
      "origin_stage": "implementation",
      "problem": "STATUS was edited on 2026-11-10 and says \"4.5b (the benchmark runs) and 4.6 next\". In the same commit, the slice index says 4.6 is \"implemented on the slice 4 branch, in review\" and slice_4_decisions.md:94 says 4.6 is \"Implemented on the branch\". STATUS says 4.6 is next while the other two documents say it is done.",
      "severity": "medium"
    },
    {
      "evidence": "`named = re.findall(...)` is compared only with `LISTS`. The parametrized negatives in lines 128-132 cover REVIEW_QUESTIONS[0] and [1] only. check_docs.py:34-42 has no `docs/review_checklists/*.md` or `.claude/**`.",
      "failure_scenario": "Swapping `requirements` and `code` between two stage rows, deleting the names question from the test-plan template, or writing \"see step 4\" in a checklist or in SKILL.md all pass `make tooling-test`.",
      "file": "tests/tools/test_stage_rules.py",
      "id": "F7",
      "kind": "defect",
      "line": 68,
      "origin_stage": "tests first",
      "problem": "Question 1, which wrong behaviour still passes. The stage-table check accepts any existing list name in any stage's Review cell, and any Review cell that contains the word \"approval\". It does not check S46-D1's mapping (discovery to plan-and-test-plan, implementation to code, and so on). The third required review question has no negative case. The step-reference scan covers only `LIVE_DOC_GLOBS`, which excludes `docs/review_checklists/` and `.claude/skills/`.",
      "severity": "low"
    },
    {
      "evidence": "test_review_brief.py:59 asserts 3 medium for 2 distinct findings (\"X1, X2 and the re-raised X1\"). `_found_by` returns `sorted(stages)` or `unit.name`.",
      "failure_scenario": "The owner reads a unit with one finding that was re-raised in three rounds as three findings.",
      "file": "scripts/review_brief.py",
      "id": "F8",
      "kind": "defect",
      "line": 174,
      "origin_stage": "implementation",
      "problem": "Severity counts are summed over every round of the unit, so a re-raised finding, which keeps its ID, is counted once per round. The plan asks for \"each unit's last verdict and its severity counts\". The \"Where findings started\" table also mixes vocabularies: checklist names or unit names (`code`, `plan`, `implementation`) are presented as \"the stage that found\" the finding.",
      "severity": "low"
    },
    {
      "evidence": "lint_changed_files.py `_markdown_header` calls `_without_front_matter` for every Markdown path. AGENTS.md:387 and :412-414 do not mention front matter.",
      "failure_scenario": "An author or reviewer reads the gate description and does not know that front matter is accepted before the title, so the stated gate is narrower than the real one (the rulebook says rules must be true of the repo).",
      "file": "AGENTS.md",
      "id": "F9",
      "kind": "defect",
      "line": 387,
      "origin_stage": "implementation",
      "problem": "The lint gate now skips a leading `---` front-matter block in every added Markdown file, not only skill files. The gate's description in the Quality gates table and coding rule 8 still say only \"a `#` title and a paragraph\".",
      "severity": "low"
    },
    {
      "evidence": "review_inputs.py:444-451 and review_brief.py:230-235 are near-identical.",
      "failure_scenario": "A fix to one fetch, for example pagination or a new exception type, is missed in the other.",
      "file": "scripts/review_brief.py",
      "id": "F10",
      "kind": "simpler_alternative",
      "line": 225,
      "origin_stage": "implementation",
      "problem": "`ci_line` re-implements the run and job fetch of `review_inputs.ci_evidence`: the same URLs, filter and exception tuple. The brief could reuse one shared helper that returns runs and jobs, and only format them differently.",
      "severity": "low"
    },
    {
      "evidence": "Stage table, Tests first row.",
      "failure_scenario": "An author reads \"Checks: make tooling-test\" as \"must pass\" and weakens or skips the red tests to leave the stage.",
      "file": "AGENTS.md",
      "id": "F11",
      "kind": "defect",
      "line": 179,
      "origin_stage": "discovery",
      "problem": "The Tests first row lists `make tooling-test` as its check, while its exit requires each new test to fail on the base code. It does not say whether the checks must pass at that stage's exit, or only run, given that the new tests are red by design.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to implementation/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| F1 | high | fixed: tests/tools/test_review_brief.py: `test_a_completed_attempt_whose_record_lost_its_report_fails_when_the_record_check_skips_it` (an attempt without `record_blocks`, as 4.1 and 4.2 logged, whose record lost its Report block, makes the brief fail; it passes when the guard is removed, checked by editing the brief) and `test_a_re_raised_finding_answered_with_a_fix_is_not_disputed` (the branch where a re-raised finding is answered `fixed:`). The origin was testing the brief only on records the record check also covers |
| F2 | medium | fixed: scripts/review_brief.py, tests/tools/test_review_brief.py: the last verdict is each reviewer's verdict in the unit's last round with a released report, named by label when the round had several reviewers; `test_each_reviewer_of_the_last_round_has_its_verdict_shown` |
| F3 | medium | fixed: AGENTS.md: the brief is built once CI has finished on the PR's head (CI runs on pull requests, so it is pasted after the PR is opened, and built again after a later push), and the PR body is a snapshot at handoff, not updated after the user's merge |
| F4 | medium | owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: decision 4 under "Decisions to make" asks the owner to remove the personal copy, which takes precedence over the repository's while it exists; removing a file from the owner's own folder is the owner's to do |
| F5 | medium | owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: decision concern 7, with a recommendation for small fixes. The opening sentence of the slice workflow now agrees with the stages (a plan and its review, tests first when the fix changes behaviour, the final review and the close-out; AGENTS.md) |
| F6 | medium | fixed: docs/STATUS.md: slice 4's item says 4.4 is reviewed, 4.6 implemented and in review, 4.5b's benchmark running, and the final review and a dry slice next |
| F7 | low | fixed: tests/tools/test_stage_rules.py: the stage table check compares each stage's lists with S46-D1's mapping (a negative case swaps two), the third review question has its negative case, and the step-reference scan covers the stage lists and the skills too. The mapping check found that the list pattern skipped names with a digit, so `e2e-tests` had never been checked; the pattern now takes digits |
| F8 | low | fixed: scripts/review_brief.py, tests/tools/test_review_brief.py: findings are counted once each, by their latest severity (a re-raised finding keeps its ID), and the origin table's heading says the column is the review's `--stage` lists, or its unit when it had none |
| F9 | low | fixed: AGENTS.md: the lint gate's row and coding rule 8 say that a leading YAML front-matter block, as a skill file needs, may come before the title |
| F10 | low | fixed: scripts/review_inputs.py, scripts/review_brief.py: one function, `ci_runs_and_jobs`, reads CI runs and jobs for both the launcher's evidence and the brief, with one tuple of read errors |
| F11 | low | fixed: AGENTS.md: the tests-first row says its checks run with the new tests failing as planned and every other test and check passing |
