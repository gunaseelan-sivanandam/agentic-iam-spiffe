# Plan review — 4.1 (#38), review prompts and severity order

Record of the plan review of slice 4.1 (#38), review prompts and severity order in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

Round 4 was the last allowed round. The fixes of its advisory findings (answers below) were made afterwards and are not rechecked; the owner decides whether they need another round.

## Round 1

### Attempt plan/c1/r1/plan/1

Commit `dfc88e2`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-1-review-prompts/plan.md` `b7b7489c02ef`, `docs/slices/poc-4-1-review-prompts/test_plan.md` `2daa733791c0`.

Status: interrupted (no end entry: the launcher stopped, or the publication check withheld the report).

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 1 (the initial review), of slice 4.1 of the agentic-SDLC PoC: `docs/slices/poc-4-1-review-prompts/plan.md` and `test_plan.md` (GitHub issue #38). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#38)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** every review prompt follows one structure, and every finding has a severity that decides what the author must do with it.

**Decided:**
- **Prompt structure** ([decision](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242), [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147)):
  - first the open mandate: add anything missing, flag anything wrong, inside or outside the listed files;
  - then the stage checklist (sub-issue 4.4) as the minimum, never the limit;
  - then the evidence (sub-issue 4.2).
- **Review modes:** initial and final reviews are fully open. Rechecks are bounded to the fixes: they verify every answer by opening the changed code and its test, and say what they opened ([R5-A6](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)).
- **Recheck inputs:** a recheck gets its own earlier report, the author's answers and the evidence that is not in its copy, never the whole review record. Records that embed earlier prompts grow with every round ([R6-9](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844)).
- **Severity order** ([decision](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242)):
  - blocking: fixed before merge, or the owner decides;
  - high: fixed in the same PR unless the owner defers it;
  - medium: fixed, or deferred with an issue link;
  - low: the author's choice.

  Every finding gets a one-line answer: fixed, deferred (with an issue) or declined (with a reason). The launcher's report schema gains a `severity` field, and the PR shows the count per severity.
- **Secrets are blocking:** a secret written into logs, evidence or any published record is blocking ([decision](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672)).
- **Rules in `AGENTS.md`** for whoever writes prompts: no file list as the scope, no "only check X", the open mandate first.

**Done when:** the launcher builds every prompt in this structure; the recheck mode and the `severity` field exist; `AGENTS.md` states the rules; tooling tests cover them.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: the open mandate as the default review, checklists as the floor, and an order for advisories** (owner decision, 2026-11-08)

**The owner's words:** "Fixing all advisory is authors choice, so we need a mandate for it, maybe a priority or severity order? Yes, let's bench mark it, Maybe learning from open ended mandate to improve the checklist is an option as well. But at the moment, checklist alone is not completely reliable. and go with your recommendation."

**Evidence for the decision.** Two open-mandate rounds each found two blockers that 3–4 focused rounds had missed: slice 2's round 5 (PR #35) and slice 3's round 4 (PR #37). They also checked the review record and the attempt log, which no focused round had looked at. The costs:
- Time and money: the open rounds took 230–443 s and about USD 2–3 (CLI estimate) each, against 17–60 s and about USD 0.25–0.40 for focused rechecks.
- Advisories: each open round gave 8–9, and nothing said which ones had to be fixed.

**Agreed direction for slice 4:**
1. **Prompt structure for every review:**
   - first the open mandate: add anything missing, flag anything wrong, inside or outside the listed files;
   - then the stage checklist from slice 4's research, as the minimum, never the limit;
   - then the evidence: coverage, tool-computed gap lists, CI results.
   A checklist alone is not reliable enough.
2. **Initial and final reviews are fully open.** Rechecks are open but bounded to the fixes: verify every answer by opening the changed code and its test, and report anything wrong or missing in what the fixes touch, so rounds converge.
3. **An order for advisories** (proposal for the grill-me). Today, which advisories to fix is the author's choice with no rule; this replaces that. The reviewer gives every finding a severity:
   - **blocking**: the existing criteria; fixed before merge, or the owner decides;
   - **high**: a real defect or false claim that does not meet the blocking criteria (for example a misleading document, new behaviour without a test, an untested fail-closed path); fixed in the same PR unless the owner defers it;
   - **medium**: clear value (robustness, diagnosability, naming); fixed, or deferred with a tracking issue;
   - **low**: style, preference, simpler alternatives; the author's choice.

   Every finding gets a one-line answer: fixed (where), deferred (issue link) or declined (reason). The author may contest a severity with a reason the reviewer can check, as for blocking findings. The launcher's report schema gains a `severity` field, and the PR shows the count per severity.
4. **Benchmark it.** The open-mandate prompt becomes a third configuration beside the short prompt and the checklist, on the same cases. The question: does it catch the defects of absence (requirements without proof, gates hidden in another CI job), and at what cost in false blockers and quota?
5. **Learn from open reviews.** When an open review finds a class of defect the stage checklist lacks, the author proposes a checklist item, and the owner approves it (POC-D6). Over time the floor rises, and the open mandate keeps covering what no list foresaw.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: every stage thinks for itself; no narrow steering** (owner, 2026-11-08)

**The owner's principle:** "each steps should think for themselfs and add anything that is missing, flag that is wrong and orchestrator narrow prompts should not steer the agents narrowly."

**The miss behind it.** Slice 2's launcher (PR #35) has defensive refusal paths that no test covers. Examples: refusing when `AGENTS.md` is missing on the base, or when the record path is invalid. Three things let this through:
- The tests were derived only from the approved test plan's rows, and the refusal paths were added during implementation.
- Coverage was not measured before the slice was called done, and the reviewer did not get a coverage report.
- The review prompt asked a closed question, "Name any test-plan row that has no test", which led the reviewer to the rows instead of the code.

The owner chose not to fix it now; the aim is to catch this kind of miss in the process.

**Proposals for the SDLC process:**
1. **Every prompt opens with an open mandate**, for authors, testers and reviewers alike: "Beyond the questions below, add anything that is missing and flag anything that is wrong, inside or outside the listed files." Specific questions are a minimum, never the limit.
2. **Agents get evidence, not the author's conclusions:** the coverage report, CI results, lint output and the traceability report. The author does not pass judgments such as "all rows are tested".
3. **Tools compute what is missing, and agents explain or fix every entry.** Candidate lists:
   - code paths without a test (coverage);
   - requirements without a test (`qa-trace`);
   - decisions without matching rule text;
   - changed files outside the review list.

   The lists are cheap and deterministic, and they would have caught this miss before any review.
4. **Each stage questions the stage before it.** The agent writing tests checks whether the plan's test list is complete. The agent writing code flags behaviour the tests do not cover. No upstream document is treated as the ceiling. This complements the question on upstream origins in the previous comment.
5. **A final review with a deliberately open prompt**, "What did everyone before you miss?", given all the evidence and no question list.
6. **Rules for whoever writes the prompts** (the author today, slice 7's loop later):
   - A rule in `AGENTS.md`: never a file list as the scope, never "only check X", and the open mandate first. Prompts are already kept verbatim in the review records, so the final review can check them.
   - This miss becomes a benchmark case: the launcher at its commit with the untested refusal paths, reviewed once with a narrow prompt and once with an open one, to measure whether the principle changes what reviewers find.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: findings of slice 2's review round 5 left for slice 4** (owner, 2026-11-08)

Round 5 of slice 2's review (PR #35) was an extra review the owner asked for before merging. It had an open mandate and the coverage report as evidence, and it was the first to see the review record. Its two blockers and three advisories are fixed in PR #35. The owner put these on slice 4; the full findings are in `docs/slices/agentic-sdlc-poc/review_slice_2.md`, round 5.

1. **Rechecks accepted answers on the author's word (R5-A6).** Round 2 accepted launcher fixes after opening only the benchmark files. Round 4 accepted a fix claiming an "Advisory only" report column that did not exist; round 5 found it missing. Proposal: a recheck opens the changed code and tests for every answer it accepts, and the review record says what each recheck read (the attempt log already lists the paths read).
2. **The benchmark cannot re-measure cleanly yet (R5-A2).**
   - A result is identified only by the answer key's hash. The prompts' hash is recorded but never checked, so a run after changing a prompt finds every case "done" and makes no call.
   - A changed answer key restarts the 26-call budget at zero and makes `--report` refuse all earlier results.
   - Proposal: a run or stage ID, the prompt hash in a result's identity, and a results file per stage. Slice 4 needs this to measure its new checklists.
3. **Planted-defect cases score too loosely (R5-A7).** Their only leak term, `PLANT-`, appears nowhere, so the leak search checks nothing. Several expected terms quote the planted line itself ("401", "|| true", "capiss_keys", "70"), so any blocking finding there that quotes the change counts as a detection. Stage A rests on the hand confirmation, but a re-run relying on the automatic columns would not.
4. **Untested behaviour beyond the refusal paths (R5-A8).** The planted-patch path and `dry_run` of the benchmark runner are never run by a test. Three branches of the launcher's report-shape check are untested ("findings is not a list", "unknown kind", "negative line"), and so is skipping non-JSON stream lines. This is the same lesson as the untested refusal paths above.
5. **A simpler alternative (R5-S1).** Both callers always pass a diff base, so the optional `diff_base` branch in `make_frozen_copy`, `build_prompt` and `invocation_from_entry` can go.
6. **Discoverability (the author's own check).** `AGENTS.md`'s "Start here" table does not say how to run a review or where the attempt logs and review records live.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: from slice 2's review round 6** (the recheck the owner asked for, PR #35)

1. **Verbatim review records grow with every round (R6-9).** Since review records keep every prompt verbatim, and each recheck prompt contained the whole record, each round's prompt repeats all the rounds before it. Slice 2's record already needs nested 5-, 6- and 7-backtick fences. Proposal for the prompt rules: a recheck gets its own earlier report, the author's answers and the evidence that is not in its copy, not the whole record.
2. **The record check is a script run by hand (R6-2).** The check that every verbatim block of a review record matches the attempt log's hashes ran as an ad-hoc script. Nobody can repeat it from the repository. A committed check is a candidate for slice 6 (gates that the run shows are needed).
3. **Repeat CLI probes when the CLI changes (R6-7).** The launcher's fix for failed Reads relies on how the CLI reports them. On 2026-11-08, with CLI 2.1.319, a failed Read came back as an error result carrying the call's ID. This probe joins the canary in the list of checks to repeat when the CLI version in the attempt log changes. Today that repeat is manual; making it automatic is part of the same decision as the canary.
4. **DPL-010** (delivery problem log, open) records slice 2's review misses. Its preventive actions are the slice-4 items in this issue.

### A comment on issue #33 (slice 4's inputs)

**Owner decisions of 2026-11-08 on the slice-2 benchmark** ([report](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/poc/slice-2-review-launcher/docs/slices/agentic-sdlc-poc/benchmark_report.md), PR #35), recorded here as inputs for slice 4's grill-me. The owner's words are quoted.

1. **Reviews that never open the files under review** (5 of 22 benchmark reviews failed this way): "keep the rule". The launcher keeps failing such a review, and its instructions will tell the reviewer to open every file it is asked to review.
2. **Secrets in published files are blocking:** a secret written into logs, evidence or any published record blocks a change. The owner also asked to reconsider the blocking list itself: "it feels like it is just for implementation, what about, architecture or requirements or tests?" Slice 4 defines blocking criteria for each stage.
3. **Questions for what is missing:** add "Does every new or changed requirement have a test or check that proves it?" and "Does every new check run as its own required CI job, named after it?" Those two misses (DPL-004, DPL-005) are "the result of inadequate review checklists".
4. **Research industry practice:** "we have to look or research for industry best practice review checklist", not only our own past problems ("reinventing the wheel"). Slice 4 researches established review checklists for each stage, then turns them into short stage-specific questions and blocking criteria. Examples of sources:
   - requirements: ISO/IEC/IEEE 29148, INCOSE;
   - architecture: ATAM, threat modelling;
   - tests: ISTQB, test smells;
   - code: Google's review guide, OWASP, CERT;
   - reviews in general: IEEE 1028, plus OWASP's LLM top 10, since the reviewers are AI agents.

   The repository's past misses (DPL entries) become test cases for the lists rather than their source. "Different models input might be good for this from different angles": several models critique the draft lists, and the comparison of models as reviewers (stage B) moves into slice 4, after the new lists exist. Using Codex there is a slice-4 decision, because today's rules allow Codex only for implementation work.

### Owner, in the session on 2026-11-08 (not on GitHub), verbatim:
- "grill-me is when the design or approach is not clear to create a contract between you and me. But most of the slice 4 is clear enough, do you think you need a grill-me for each sub issue?"
- "I would suggest to create issues, prioratize when they needs to be in place, before we move forward. Making the notes in the plan PR is only going to get lost like now."
- Answers to three questions: benchmark budget "Up to 40 runs"; models "Sonnet and Codex"; "Plan PR, then one final PR"; and plan approval "One plan PR up front".

## Minimum questions

1. Does every decision follow from the owner's words, or carry a stated reason? Is anything the owner decided missing, changed or weakened? Is anything presented as the owner's decision that the owner did not make?
2. Can each decision be built from this plan without asking the owner again? What is underspecified?
3. Does the test plan prove every decision (an approved decision without a test blocks)? Which wrong implementation would still pass the planned tests?
4. Is anything over-engineered for a proof of concept under the honest-mistake threat model, or is there a simpler way within the owner's decisions?
5. Contradictions: with AGENTS.md, with the PoC plan, with another sub-issue's plan, or inside this plan.
6. Keys and publication: can anything here make a credential, a secret or an operational detail (a local path, an account) reach a reviewer or a public record?
```

#### Report

None: the publication check withheld it, so it was never written (DPL-011).

### Attempt plan/c1/r1/plan/2

Commit `f070669`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-1-review-prompts/plan.md` `b7b7489c02ef`, `docs/slices/poc-4-1-review-prompts/test_plan.md` `2daa733791c0`.

Status: completed; approvable within the threat model: no.

#### Prompt

The same task prompt as attempt plan/c1/r1/plan/1 (SHA-256 `5b8f81ebcf83`).

#### Report

```json
{
  "findings": [
    {
      "evidence": "scripts/run_review_benchmark.py:335-340: `build_case_prompt` returns `launcher.build_prompt(inputs, case_task(...), has_diff=True)`; the canary also uses it (line 408). 4.5 S45-D6 plans 'Opus with stage A's short prompt on the 4 new cases', and S45-D4 plans the DPL-010 case 'once with round 1's narrow question and once with the open mandate'. Owner, #33 item 4: 'The open-mandate prompt becomes a third configuration beside the short prompt and the checklist'. 4.1 puts `run_review_benchmark.py` in scope only for scoring (plan.md:66-67), and no plan gives the benchmark a way to build a prompt without the mandate.",
      "failure_scenario": "4.5 runs its short-prompt and narrow-prompt configurations after 4.1 is implemented (S45-D9). Every prompt silently carries the open mandate, so the comparison 'open mandate vs short or narrow' measures the mandate against itself. The report would still present it as the owner's comparison: a false result that the default-setup decision (S45-D7) is then based on.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "B1",
      "kind": "blocking",
      "line": 37,
      "problem": "Contradiction with 4.5 and with the owner's benchmark decision. S41-D1 puts the open mandate inside `build_prompt` so that 'a task text cannot remove or reorder' it. The benchmark builds every case prompt through that same function. Once 4.1 lands, no configuration without the mandate can be built: not stage A's short prompt, not the checklist prompt, and not the DPL-010 'narrow question' run."
    },
    {
      "evidence": "scripts/run_independent_review.py:58-82 (the schema: findings and verdict only). Test plan row 'Mandate per mode' (test_plan.md:27) only checks that the mandate text is present. The owner's R5-A6 proposal: 'the review record says what each recheck read (the attempt log already lists the paths read)'.",
      "failure_scenario": "A round-2 recheck returns `{\"findings\": [], \"verdict\": \"yes\"}` after reading only the answers in its prompt. This is exactly the round-4 miss of slice 2 (accepting a fix for an 'Advisory only' column that did not exist). Every planned test passes, the launcher releases the report, and the record cannot show what was verified. A simple control is a per-answer field in the recheck schema (`answer_id`, `accepted`, `opened`), or a launcher check that each `fixed (where)` file appears among the attempt's read paths.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "B2",
      "kind": "blocking",
      "line": 39,
      "problem": "The owner decided that rechecks 'verify every answer by opening the changed code and its test, and say what they opened' (R5-A6). Decision S41-D3 only puts that sentence into the prompt. The report schema stays `findings` plus `verdict` with `additionalProperties: false`, so a report has no place to say which answers were accepted or which files were opened for each. An accepted answer produces no finding at all. Nothing in the plan or the test plan checks or records that a recheck actually opened the files an answer points to. This is an approved decision without a test, and the threat listed at plan.md:23 has no control."
    },
    {
      "evidence": "plan.md:38-39 (final = initial mandate). docs/slices/poc-4-6-stage-rules/plan.md:40. docs/slices/poc-4-4-stage-checklists/plan.md:34 and :38 ('final review' list holds the two questions for what is missing).",
      "failure_scenario": "The implementer builds `final` as an alias of `initial`, as 4.1 says. The final review then gets a checklist and a question-led mandate, which is the narrow steering the owner's principle 5 wanted to avoid. Or the implementer follows 4.6 and drops 4.4's final checklist. Either way one approved plan is not met, and the implementation run has to stop and ask the owner, which this slice's run mode rules out.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "B3",
      "kind": "blocking",
      "line": 39,
      "problem": "The `final` mode contradicts 4.6 and 4.4. S41-D2 and S41-D3 give `final` the same mandate as `initial`, and that mandate says 'The checklist and the questions below are a minimum'. S41-D1 adds the stage checklist whenever one is given. 4.6 S46-D5 defines the final review as the open prompt 'What did everyone before you miss?', 'given all the evidence and no question list'. 4.4 S44-D1 and S44-D5 make 'final review' an artifact type with its own checklist. 4.1 is the plan that builds the final mode, and it does not say which of these wins. It also does not say whether the final review is its own unit, and with it its own round count. Finally, S46-D5's 'finding history' does not match S41-D4's inputs, which are only the reviewer's own earlier report and the answers."
    },
    {
      "evidence": "Owner on #38: 'a recheck gets its own earlier report, the author's answers and the evidence that is not in its copy, never the whole review record.' plan.md:40 and test_plan.md:29 do not mention evidence. S41-D1 only says evidence appears 'if given'.",
      "failure_scenario": "The recheck path builds its prompt without 4.2's computed evidence (coverage of the fix, CI results). The recheck then judges fixes without the evidence the owner required, and no planned test notices.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A1",
      "kind": "advisory",
      "line": 40,
      "problem": "[high] S41-D4 drops part of the owner's decision on recheck inputs. The owner said a recheck gets 'its own earlier report, the author's answers and the evidence that is not in its copy'. The plan lists only the first two, and the test plan's 'Recheck inputs' row never checks that a recheck prompt carries the evidence section."
    },
    {
      "evidence": "plan.md:41 and :124. Owner, #33 decision 3: '**low**: style, preference, simpler alternatives; the author's choice'; 'The reviewer gives every finding a severity'.",
      "failure_scenario": "The owner approves the plan PR thinking the `severity` field exists, as #38's Done-when states, and finds a different schema at the final PR. A serious decision concern then has no severity, and its required handling is undefined under the new order.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A2",
      "kind": "advisory",
      "line": 41,
      "problem": "[high] S41-D5 changes an owner decision but presents it only as an author default. The owner decided that 'the launcher's report schema gains a `severity` field' (also in #38's Done-when) and that 'the reviewer gives every finding a severity', with simpler alternatives under low. The plan replaces this with new `kind` values. As a result `simpler_alternative` and `decision_concern` findings carry no severity, and nothing says what the author must do with them. The Review notes list 'S41-D5 (one field)' as a default but do not say that it departs from the owner's words."
    },
    {
      "evidence": "S41-D3 only adds `--mode initial|recheck|final` and records it. The round admission (`admit_round`, run_independent_review.py:629-707) knows nothing about modes.",
      "failure_scenario": "The author runs round 2 with `--mode initial`. That needs no `--answers` and no earlier report, and it skips the bounded mandate. The recheck requirement (R5-A6, R6-9) is bypassed by a flag choice, and every planned test still passes.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A3",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] The plan does not tie the mode to the round. Nothing says which modes round 1 or round 2 and later may use, whether `final` counts against the 4-round limit, or whether `initial` may be repeated later. The test plan has no row for an invalid pairing of mode and round."
    },
    {
      "evidence": "test_plan.md:29 refuses only when there is 'no completed attempt in the previous round', a missing `--answers`, or a hash mismatch. The log path is `record.parent / review_attempts.jsonl` (run_independent_review.py:866). Attempt IDs carry unit and count (line 726).",
      "failure_scenario": "An implementation that takes the latest completed attempt by label, whatever its unit or count, feeds the plan review's report into an implementation recheck. The planned tests still pass, and the recheck verifies answers against the wrong findings.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A4",
      "kind": "advisory",
      "line": 40,
      "problem": "[high] The planned recheck tests would pass a wrong lookup of the earlier report. The attempt log is one file per slice and holds several units (`plan` and implementation units), and reviewer labels repeat across them. The tests never put a completed attempt of the same label into another unit or another count (after a reset). They also never cover a missing released file: reports are git-ignored and exist only on the author's machine."
    },
    {
      "evidence": "AGENTS.md (base), Review findings and Plan review. plan.md:42 and :61-62 ('no other rule in it contradicts them') with no list of the edits. docs/slices/poc-4-3-review-records/plan.md:35.",
      "failure_scenario": "The implementer adds the scale but leaves 'not fixed by default' or the round-2 rule in place. A high finding raised in a recheck is then both mandatory and ignorable. Or AGENTS.md says 'declined' is allowed for high, and 4.3's check fails records that follow AGENTS.md.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A5",
      "kind": "advisory",
      "line": 42,
      "problem": "[high] The plan does not name the AGENTS.md sentences that the severity order contradicts. Today AGENTS.md says 'Everything else is advisory. It is listed once and is not fixed by default', and 'from round 2 a new finding counts only if it blocks'. It uses 'fixed or rejected' where S41-D6 uses fixed/deferred/declined, and it sets no handling for high findings still open after round 4. S41-D6 also lets the author decline any finding, while the owner's rule for high is 'fixed unless the owner defers', and S43-D4 fails a declined high."
    },
    {
      "evidence": "run_independent_review.py:872-890. docs/slices/agentic-sdlc-poc/plan.md:423. tests/tools/test_run_independent_review.py:241-254.",
      "failure_scenario": "Every recheck entry reports a `full_prompt_sha256` mismatch on rebuild, or the implementer quietly removes the comparison. Either way the existing rebuild check loses its meaning without a plan decision.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A6",
      "kind": "advisory",
      "line": 95,
      "problem": "[medium] The full prompt can no longer be rebuilt from a log entry. The PoC plan makes the attempt log authoritative for 'rebuilding an invocation', and `invocation_from_entry` recomputes `full_prompt_sha256`. The new prompt depends on the mode, the answers file, the earlier report (plus 4.2's evidence and 4.4's checklist), but the plan records only `mode`. It also leaves `invocation_from_entry` out of scope."
    },
    {
      "evidence": "plan.md:40; `--reviewer label:prompt:model:effort` (run_independent_review.py:822-834) has no answers part.",
      "failure_scenario": "In a two-reviewer recheck both reports use 'B1'. Reviewer A reads the answer meant for B's B1 and accepts or re-raises against the wrong finding.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A7",
      "kind": "advisory",
      "line": 40,
      "problem": "[medium] `--answers <file>` is a single round-level argument, but a round can hold several reviewers, each needing answers to its own report. The plan does not say whether answers are per reviewer, how finding IDs that collide across reviewers (F1, B1\u2026) are kept apart, or whether one reviewer sees the answers to another's findings."
    },
    {
      "evidence": "docs/slices/poc-4-2-review-inputs/plan.md:16. docs/slices/poc-4-4-stage-checklists/plan.md:43. docs/slices/poc-4-5-benchmark/plan.md:46. docs/slices/poc-4-6-stage-rules/plan.md:46.",
      "failure_scenario": "The Codex mode is built first with the old kinds, as S45-D9 says, and then breaks or is reworked when 4.1 changes the enum. Or 4.4's critique runs before the mandate exists.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A8",
      "kind": "advisory",
      "line": 71,
      "problem": "[medium] The plan states no order of work, although others depend on it. 4.2 fills 4.1's evidence section, and 4.4 fills its checklist section. 4.4's multi-model critique runs 'through the launcher, with the open mandate'. 4.5's Codex mode (S45-D9: 'comes first') needs 4.1's final report schema for `--output-schema`. 4.1 and 4.6 both edit the test-plan template and the Independent review section of AGENTS.md."
    },
    {
      "evidence": "S41-D3 wording; every slice has a plan review unit with rechecks.",
      "failure_scenario": "A plan recheck finds no 'code and test' to open, takes the wording literally, accepts the answers on their text, and is still compliant with its own mandate.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A9",
      "kind": "advisory",
      "line": 39,
      "problem": "[medium] The bounded recheck mandate says 'open the code and test it concerns'. Plan reviews such as this unit have no code or test, so the text is wrong for half of all rechecks. It should say 'the changed files the answer names'."
    },
    {
      "evidence": "run_review_benchmark.py:240-264 and :555; :153.",
      "failure_scenario": "Stale wording in reports and the canary. The twin's validity still rests on finding IDs, so nothing false-greens, but a reader sees retired terms.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A10",
      "kind": "advisory",
      "line": 46,
      "problem": "[low] S41-D10 already describes today's behaviour: `score()` counts only `kind == \"blocking\"` and treats every other kind as 'advisory_only'. So the decision adds nothing. Retiring `advisory` also leaves stale names that the retirement list (plan.md:117-120) leaves out: the report column 'Advisory only', and the canary instruction 'always add an advisory finding', which the twin's schema-constrained reply can no longer follow literally."
    },
    {
      "evidence": "plan.md:80-82; docs/slices/poc-4-3-review-records/plan.md:33 (scans the task prompt only).",
      "failure_scenario": "The author passes the wrong file by mistake (a local notes file with a token or a local path), and its content goes to the model provider. Nothing is published, so the impact is low.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A11",
      "kind": "advisory",
      "line": 80,
      "problem": "[low] The answers file is read from any path and put into the reviewer's prompt without the publication scan. 4.3 scans only the task prompt. 'Assets and holders' says nothing new reaches the reviewer, but this new input is not mentioned."
    },
    {
      "evidence": "call_stats and summarise_paths already record the paths read (run_independent_review.py:436-485). The empty-review rule already fails reviews that open none of the files.",
      "failure_scenario": "Without it, R5-A6 (accepting answers without reading) relies only on the model following one sentence.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "S1",
      "kind": "simpler_alternative",
      "line": 39,
      "problem": "A launcher check against the attempt log's read paths (already recorded per attempt) would replace trust in the recheck's prose with a deterministic floor: every file named in a 'fixed (where)' answer must appear among the attempt's read paths, or the recheck counts as failed, as the empty-review rule does today."
    }
  ],
  "verdict": "no"
}
```

#### Answers to plan/c1/r1/plan/2

| ID | Severity | Answer |
| --- | --- | --- |
| B1 | blocking | fixed: 4.1 S41-D2 (a configuration only the benchmark runner passes builds prompts without the mandate; the command line cannot); 4.5 S45-D3 names the configurations; test rows "No way to drop the mandate" and "Runner configurations" |
| B2 | blocking | fixed: 4.1 S41-D8 (`accounted` lists every answer with `opened` files; the launcher fails a recheck that leaves one out, names an unread file, or did not read a file a `fixed:` answer names); test rows "Answers section" and "Accounted" |
| B3 | blocking | fixed: 4.1 S41-D3 and S41-D4 (the final mode has its own mandate, the owner's question, no checklist; the unit `final` counts its own rounds; its history is the other units' records in its copy); 4.4 S44-D1 drops the final-review list; 4.6 S46-D5 matches |
| A1 | high | fixed: 4.1 S41-D5(c) (a recheck gets the evidence recomputed at its commit); test row "Recheck inputs" |
| A2 | high | fixed: 4.1 S41-D6 follows the owner's words (a `severity` field on every finding; `kind` keeps defect, simpler_alternative, decision_concern) |
| A3 | high | fixed: 4.1 S41-D3 (the mode follows the round; no flag, so no invalid pairing); test row "Mode from the round" |
| A4 | high | fixed: 4.1 S41-D5(a) (same unit and label, previous round, after any reset; the file at the start entry's `report_path` must exist and match); test row "Recheck inputs" lists the other-unit, reset and missing-file cases |
| A5 | high | fixed: 4.1 S41-D12 names each `AGENTS.md` sentence that changes; S41-D7 uses the rulebook's word "rejected" with the rules per severity, consistent with 4.3 S43-D4 |
| A6 | medium | fixed: the answers section's hash goes into the start entry (S41-D5), 4.2 S42-D9 and 4.3 S43-D1 keep the evidence verbatim, `invocation_from_entry` is in scope; test row "Rebuild" |
| A7 | medium | fixed: answers live in the record per attempt (`#### Answers to <attempt id>`, S41-D5(b)), so each reviewer gets the answers to its own report; finding IDs never collide across reports |
| A8 | medium | fixed: the order of work is in the slice index (`docs/slices/README.md`), and each plan opens with an "Order of work" line |
| A9 | medium | fixed: S41-D4's recheck mandate says "open the files the answer names and the tests that cover them" |
| A10 | low | fixed: S41-D13 replaces the empty decision with the scoring on `severity`, the column "Not blocking" and the canary's "low finding" |
| A11 | low | fixed: 4.3 S43-D2 scans the whole built prompt, answers included, before the start entry and the call |
| S1 | low | fixed: adopted in S41-D8 (the check uses the read paths the launcher already logs) |

## Round 2

### Attempt plan/c1/r2/plan/1

Commit `ebb1029`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-1-review-prompts/plan.md` `f1f72a2781dd`, `docs/slices/poc-4-1-review-prompts/test_plan.md` `4c975742e628`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 2 of the plan review of slice 4.1 (review prompts and severity, #38), a recheck of your earlier report (round 1, attempt 2). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it. (Slice 4.1 replaces this with an `accounted` field; until then this finding carries it.)
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## Your earlier report (round 1, attempt 2)

```json
{
  "findings": [
    {
      "evidence": "scripts/run_review_benchmark.py:335-340: `build_case_prompt` returns `launcher.build_prompt(inputs, case_task(...), has_diff=True)`; the canary also uses it (line 408). 4.5 S45-D6 plans 'Opus with stage A's short prompt on the 4 new cases', and S45-D4 plans the DPL-010 case 'once with round 1's narrow question and once with the open mandate'. Owner, #33 item 4: 'The open-mandate prompt becomes a third configuration beside the short prompt and the checklist'. 4.1 puts `run_review_benchmark.py` in scope only for scoring (plan.md:66-67), and no plan gives the benchmark a way to build a prompt without the mandate.",
      "failure_scenario": "4.5 runs its short-prompt and narrow-prompt configurations after 4.1 is implemented (S45-D9). Every prompt silently carries the open mandate, so the comparison 'open mandate vs short or narrow' measures the mandate against itself. The report would still present it as the owner's comparison: a false result that the default-setup decision (S45-D7) is then based on.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "B1",
      "kind": "blocking",
      "line": 37,
      "problem": "Contradiction with 4.5 and with the owner's benchmark decision. S41-D1 puts the open mandate inside `build_prompt` so that 'a task text cannot remove or reorder' it. The benchmark builds every case prompt through that same function. Once 4.1 lands, no configuration without the mandate can be built: not stage A's short prompt, not the checklist prompt, and not the DPL-010 'narrow question' run."
    },
    {
      "evidence": "scripts/run_independent_review.py:58-82 (the schema: findings and verdict only). Test plan row 'Mandate per mode' (test_plan.md:27) only checks that the mandate text is present. The owner's R5-A6 proposal: 'the review record says what each recheck read (the attempt log already lists the paths read)'.",
      "failure_scenario": "A round-2 recheck returns `{\"findings\": [], \"verdict\": \"yes\"}` after reading only the answers in its prompt. This is exactly the round-4 miss of slice 2 (accepting a fix for an 'Advisory only' column that did not exist). Every planned test passes, the launcher releases the report, and the record cannot show what was verified. A simple control is a per-answer field in the recheck schema (`answer_id`, `accepted`, `opened`), or a launcher check that each `fixed (where)` file appears among the attempt's read paths.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "B2",
      "kind": "blocking",
      "line": 39,
      "problem": "The owner decided that rechecks 'verify every answer by opening the changed code and its test, and say what they opened' (R5-A6). Decision S41-D3 only puts that sentence into the prompt. The report schema stays `findings` plus `verdict` with `additionalProperties: false`, so a report has no place to say which answers were accepted or which files were opened for each. An accepted answer produces no finding at all. Nothing in the plan or the test plan checks or records that a recheck actually opened the files an answer points to. This is an approved decision without a test, and the threat listed at plan.md:23 has no control."
    },
    {
      "evidence": "plan.md:38-39 (final = initial mandate). docs/slices/poc-4-6-stage-rules/plan.md:40. docs/slices/poc-4-4-stage-checklists/plan.md:34 and :38 ('final review' list holds the two questions for what is missing).",
      "failure_scenario": "The implementer builds `final` as an alias of `initial`, as 4.1 says. The final review then gets a checklist and a question-led mandate, which is the narrow steering the owner's principle 5 wanted to avoid. Or the implementer follows 4.6 and drops 4.4's final checklist. Either way one approved plan is not met, and the implementation run has to stop and ask the owner, which this slice's run mode rules out.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "B3",
      "kind": "blocking",
      "line": 39,
      "problem": "The `final` mode contradicts 4.6 and 4.4. S41-D2 and S41-D3 give `final` the same mandate as `initial`, and that mandate says 'The checklist and the questions below are a minimum'. S41-D1 adds the stage checklist whenever one is given. 4.6 S46-D5 defines the final review as the open prompt 'What did everyone before you miss?', 'given all the evidence and no question list'. 4.4 S44-D1 and S44-D5 make 'final review' an artifact type with its own checklist. 4.1 is the plan that builds the final mode, and it does not say which of these wins. It also does not say whether the final review is its own unit, and with it its own round count. Finally, S46-D5's 'finding history' does not match S41-D4's inputs, which are only the reviewer's own earlier report and the answers."
    },
    {
      "evidence": "Owner on #38: 'a recheck gets its own earlier report, the author's answers and the evidence that is not in its copy, never the whole review record.' plan.md:40 and test_plan.md:29 do not mention evidence. S41-D1 only says evidence appears 'if given'.",
      "failure_scenario": "The recheck path builds its prompt without 4.2's computed evidence (coverage of the fix, CI results). The recheck then judges fixes without the evidence the owner required, and no planned test notices.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A1",
      "kind": "advisory",
      "line": 40,
      "problem": "[high] S41-D4 drops part of the owner's decision on recheck inputs. The owner said a recheck gets 'its own earlier report, the author's answers and the evidence that is not in its copy'. The plan lists only the first two, and the test plan's 'Recheck inputs' row never checks that a recheck prompt carries the evidence section."
    },
    {
      "evidence": "plan.md:41 and :124. Owner, #33 decision 3: '**low**: style, preference, simpler alternatives; the author's choice'; 'The reviewer gives every finding a severity'.",
      "failure_scenario": "The owner approves the plan PR thinking the `severity` field exists, as #38's Done-when states, and finds a different schema at the final PR. A serious decision concern then has no severity, and its required handling is undefined under the new order.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A2",
      "kind": "advisory",
      "line": 41,
      "problem": "[high] S41-D5 changes an owner decision but presents it only as an author default. The owner decided that 'the launcher's report schema gains a `severity` field' (also in #38's Done-when) and that 'the reviewer gives every finding a severity', with simpler alternatives under low. The plan replaces this with new `kind` values. As a result `simpler_alternative` and `decision_concern` findings carry no severity, and nothing says what the author must do with them. The Review notes list 'S41-D5 (one field)' as a default but do not say that it departs from the owner's words."
    },
    {
      "evidence": "S41-D3 only adds `--mode initial|recheck|final` and records it. The round admission (`admit_round`, run_independent_review.py:629-707) knows nothing about modes.",
      "failure_scenario": "The author runs round 2 with `--mode initial`. That needs no `--answers` and no earlier report, and it skips the bounded mandate. The recheck requirement (R5-A6, R6-9) is bypassed by a flag choice, and every planned test still passes.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A3",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] The plan does not tie the mode to the round. Nothing says which modes round 1 or round 2 and later may use, whether `final` counts against the 4-round limit, or whether `initial` may be repeated later. The test plan has no row for an invalid pairing of mode and round."
    },
    {
      "evidence": "test_plan.md:29 refuses only when there is 'no completed attempt in the previous round', a missing `--answers`, or a hash mismatch. The log path is `record.parent / review_attempts.jsonl` (run_independent_review.py:866). Attempt IDs carry unit and count (line 726).",
      "failure_scenario": "An implementation that takes the latest completed attempt by label, whatever its unit or count, feeds the plan review's report into an implementation recheck. The planned tests still pass, and the recheck verifies answers against the wrong findings.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A4",
      "kind": "advisory",
      "line": 40,
      "problem": "[high] The planned recheck tests would pass a wrong lookup of the earlier report. The attempt log is one file per slice and holds several units (`plan` and implementation units), and reviewer labels repeat across them. The tests never put a completed attempt of the same label into another unit or another count (after a reset). They also never cover a missing released file: reports are git-ignored and exist only on the author's machine."
    },
    {
      "evidence": "AGENTS.md (base), Review findings and Plan review. plan.md:42 and :61-62 ('no other rule in it contradicts them') with no list of the edits. docs/slices/poc-4-3-review-records/plan.md:35.",
      "failure_scenario": "The implementer adds the scale but leaves 'not fixed by default' or the round-2 rule in place. A high finding raised in a recheck is then both mandatory and ignorable. Or AGENTS.md says 'declined' is allowed for high, and 4.3's check fails records that follow AGENTS.md.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A5",
      "kind": "advisory",
      "line": 42,
      "problem": "[high] The plan does not name the AGENTS.md sentences that the severity order contradicts. Today AGENTS.md says 'Everything else is advisory. It is listed once and is not fixed by default', and 'from round 2 a new finding counts only if it blocks'. It uses 'fixed or rejected' where S41-D6 uses fixed/deferred/declined, and it sets no handling for high findings still open after round 4. S41-D6 also lets the author decline any finding, while the owner's rule for high is 'fixed unless the owner defers', and S43-D4 fails a declined high."
    },
    {
      "evidence": "run_independent_review.py:872-890. docs/slices/agentic-sdlc-poc/plan.md:423. tests/tools/test_run_independent_review.py:241-254.",
      "failure_scenario": "Every recheck entry reports a `full_prompt_sha256` mismatch on rebuild, or the implementer quietly removes the comparison. Either way the existing rebuild check loses its meaning without a plan decision.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A6",
      "kind": "advisory",
      "line": 95,
      "problem": "[medium] The full prompt can no longer be rebuilt from a log entry. The PoC plan makes the attempt log authoritative for 'rebuilding an invocation', and `invocation_from_entry` recomputes `full_prompt_sha256`. The new prompt depends on the mode, the answers file, the earlier report (plus 4.2's evidence and 4.4's checklist), but the plan records only `mode`. It also leaves `invocation_from_entry` out of scope."
    },
    {
      "evidence": "plan.md:40; `--reviewer label:prompt:model:effort` (run_independent_review.py:822-834) has no answers part.",
      "failure_scenario": "In a two-reviewer recheck both reports use 'B1'. Reviewer A reads the answer meant for B's B1 and accepts or re-raises against the wrong finding.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A7",
      "kind": "advisory",
      "line": 40,
      "problem": "[medium] `--answers <file>` is a single round-level argument, but a round can hold several reviewers, each needing answers to its own report. The plan does not say whether answers are per reviewer, how finding IDs that collide across reviewers (F1, B1\u2026) are kept apart, or whether one reviewer sees the answers to another's findings."
    },
    {
      "evidence": "docs/slices/poc-4-2-review-inputs/plan.md:16. docs/slices/poc-4-4-stage-checklists/plan.md:43. docs/slices/poc-4-5-benchmark/plan.md:46. docs/slices/poc-4-6-stage-rules/plan.md:46.",
      "failure_scenario": "The Codex mode is built first with the old kinds, as S45-D9 says, and then breaks or is reworked when 4.1 changes the enum. Or 4.4's critique runs before the mandate exists.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A8",
      "kind": "advisory",
      "line": 71,
      "problem": "[medium] The plan states no order of work, although others depend on it. 4.2 fills 4.1's evidence section, and 4.4 fills its checklist section. 4.4's multi-model critique runs 'through the launcher, with the open mandate'. 4.5's Codex mode (S45-D9: 'comes first') needs 4.1's final report schema for `--output-schema`. 4.1 and 4.6 both edit the test-plan template and the Independent review section of AGENTS.md."
    },
    {
      "evidence": "S41-D3 wording; every slice has a plan review unit with rechecks.",
      "failure_scenario": "A plan recheck finds no 'code and test' to open, takes the wording literally, accepts the answers on their text, and is still compliant with its own mandate.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A9",
      "kind": "advisory",
      "line": 39,
      "problem": "[medium] The bounded recheck mandate says 'open the code and test it concerns'. Plan reviews such as this unit have no code or test, so the text is wrong for half of all rechecks. It should say 'the changed files the answer names'."
    },
    {
      "evidence": "run_review_benchmark.py:240-264 and :555; :153.",
      "failure_scenario": "Stale wording in reports and the canary. The twin's validity still rests on finding IDs, so nothing false-greens, but a reader sees retired terms.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A10",
      "kind": "advisory",
      "line": 46,
      "problem": "[low] S41-D10 already describes today's behaviour: `score()` counts only `kind == \"blocking\"` and treats every other kind as 'advisory_only'. So the decision adds nothing. Retiring `advisory` also leaves stale names that the retirement list (plan.md:117-120) leaves out: the report column 'Advisory only', and the canary instruction 'always add an advisory finding', which the twin's schema-constrained reply can no longer follow literally."
    },
    {
      "evidence": "plan.md:80-82; docs/slices/poc-4-3-review-records/plan.md:33 (scans the task prompt only).",
      "failure_scenario": "The author passes the wrong file by mistake (a local notes file with a token or a local path), and its content goes to the model provider. Nothing is published, so the impact is low.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A11",
      "kind": "advisory",
      "line": 80,
      "problem": "[low] The answers file is read from any path and put into the reviewer's prompt without the publication scan. 4.3 scans only the task prompt. 'Assets and holders' says nothing new reaches the reviewer, but this new input is not mentioned."
    },
    {
      "evidence": "call_stats and summarise_paths already record the paths read (run_independent_review.py:436-485). The empty-review rule already fails reviews that open none of the files.",
      "failure_scenario": "Without it, R5-A6 (accepting answers without reading) relies only on the model following one sentence.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "S1",
      "kind": "simpler_alternative",
      "line": 39,
      "problem": "A launcher check against the attempt log's read paths (already recorded per attempt) would replace trust in the recheck's prose with a deterministic floor: every file named in a 'fixed (where)' answer must appear among the attempt's read paths, or the recheck counts as failed, as the empty-review rule does today."
    }
  ],
  "verdict": "no"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| B1 | blocking | fixed: 4.1 S41-D2 (a configuration only the benchmark runner passes builds prompts without the mandate; the command line cannot); 4.5 S45-D3 names the configurations; test rows "No way to drop the mandate" and "Runner configurations" |
| B2 | blocking | fixed: 4.1 S41-D8 (`accounted` lists every answer with `opened` files; the launcher fails a recheck that leaves one out, names an unread file, or did not read a file a `fixed:` answer names); test rows "Answers section" and "Accounted" |
| B3 | blocking | fixed: 4.1 S41-D3 and S41-D4 (the final mode has its own mandate, the owner's question, no checklist; the unit `final` counts its own rounds; its history is the other units' records in its copy); 4.4 S44-D1 drops the final-review list; 4.6 S46-D5 matches |
| A1 | high | fixed: 4.1 S41-D5(c) (a recheck gets the evidence recomputed at its commit); test row "Recheck inputs" |
| A2 | high | fixed: 4.1 S41-D6 follows the owner's words (a `severity` field on every finding; `kind` keeps defect, simpler_alternative, decision_concern) |
| A3 | high | fixed: 4.1 S41-D3 (the mode follows the round; no flag, so no invalid pairing); test row "Mode from the round" |
| A4 | high | fixed: 4.1 S41-D5(a) (same unit and label, previous round, after any reset; the file at the start entry's `report_path` must exist and match); test row "Recheck inputs" lists the other-unit, reset and missing-file cases |
| A5 | high | fixed: 4.1 S41-D12 names each `AGENTS.md` sentence that changes; S41-D7 uses the rulebook's word "rejected" with the rules per severity, consistent with 4.3 S43-D4 |
| A6 | medium | fixed: the answers section's hash goes into the start entry (S41-D5), 4.2 S42-D9 and 4.3 S43-D1 keep the evidence verbatim, `invocation_from_entry` is in scope; test row "Rebuild" |
| A7 | medium | fixed: answers live in the record per attempt (`#### Answers to <attempt id>`, S41-D5(b)), so each reviewer gets the answers to its own report; finding IDs never collide across reports |
| A8 | medium | fixed: the order of work is in the slice index (`docs/slices/README.md`), and each plan opens with an "Order of work" line |
| A9 | medium | fixed: S41-D4's recheck mandate says "open the files the answer names and the tests that cover them" |
| A10 | low | fixed: S41-D13 replaces the empty decision with the scoring on `severity`, the column "Not blocking" and the canary's "low finding" |
| A11 | low | fixed: 4.3 S43-D2 scans the whole built prompt, answers included, before the start entry and the call |
| S1 | low | fixed: adopted in S41-D8 (the check uses the read paths the launcher already logs) |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "Base AGENTS.md, sections PoC scope and proportion (Review findings, Review loop, Few exceptions) and Independent review (Implementation review, Report sections). plan.md:54. test_plan.md:58-59: the review checks only 'each sentence S41-D12 names'.",
      "failure_scenario": "The implementer edits exactly the sentences S41-D12 lists, and the review checks only those. AGENTS.md then still says the review ends once every blocking finding is handled, and that hardening ideas are 'advisory at most'. Meanwhile 4.3's check (S43-D4) fails a rejected high finding that the next round did not accept. The rulebook and the record check now disagree, and AGENTS.md's own rule says they must not.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A5",
      "kind": "advisory",
      "line": 54,
      "problem": "[high] Re-raised, partly fixed. S41-D12 now names four sentences. But its closing claim, 'No other sentence of the rulebook mentions the old `advisory` handling', is false for the base AGENTS.md. Several sentences are still left unchanged: 'Reviewers should expect production-hardening ideas \u2026 and report them as advisory at most' (Review findings). 'Besides blocking and advisory findings, every round may report\u2026' (Report sections). 'findings on purpose comments and names are fix-or-defer' (Implementation review). 'The review ends when every blocking finding is fixed, accepted as rejected, or decided by the user' (Review loop): this one ignores high findings, which S41-D7 and S43-D4 require to be accepted or decided by the owner. 'one line in the review report is enough' (Few exceptions) does not say which severity that gets."
    },
    {
      "evidence": "plan.md:49-50. test_plan.md:33-34: the refusals cover only a wrong first word and a `fixed:` path missing from the copy; nothing covers a `fixed:` answer with no path. The author's answer table in this round's prompt.",
      "failure_scenario": "An implementation pulls out whatever path-shaped tokens it finds. The author writes 'fixed: S41-D5 now covers it'. No path is extracted, so the read check passes with nothing to check. The recheck accepts the answer without opening anything, and the B2/R5-A6 control is a false green for exactly the answers written in prose.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "N1",
      "kind": "advisory",
      "line": 50,
      "problem": "[high] The S41-D8 check, 'a file named in a `fixed:` answer was not read', depends on extracting file paths from answers. S41-D7 gives `fixed:` only as '(the files changed)' and defines no syntax for those paths. Neither the plan nor the test plan refuses a `fixed:` answer that names no file. The author's own round-1 answers show this case ('fixed: 4.1 S41-D2 (...)', 'fixed: the answers section's hash goes into\u2026'): they name decisions, not paths."
    },
    {
      "evidence": "plan.md:50; test_plan.md:33. AGENTS.md: 'Retire documents with `git mv`'; step 3 removes dead code.",
      "failure_scenario": "The author answers a finding with 'fixed: removed scripts/old_helper.py'. The recheck is refused before any call, and the author has to reword the answer to get around the check.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "N2",
      "kind": "advisory",
      "line": 50,
      "problem": "[medium] 'The launcher refuses an answers section whose `fixed:` paths do not exist in the copy' refuses a valid fix that deletes or retires a file with `git mv` into an archive: the named path no longer exists. The plan does not say whether the old path or the new one is named."
    },
    {
      "evidence": "test_plan.md:36; plan.md:47; docs/slices/poc-4-2-review-inputs/plan.md:47.",
      "failure_scenario": "The rebuild works only once evidence is empty or fixed in the test. A later change to the evidence breaks the `full_prompt_sha256` match, and no test catches it.",
      "file": "docs/slices/poc-4-1-review-prompts/test_plan.md",
      "id": "N3",
      "kind": "advisory",
      "line": 36,
      "problem": "[low] The 'Rebuild' row rebuilds the recheck prompt from the entry, the earlier report and the answers section, but not from the evidence section, which is now part of every recheck prompt (S41-D5(c), 4.2 S42-D9)."
    },
    {
      "evidence": "B1: accepted (poc-4-1 plan.md S41-D2, test_plan.md rows 'No way to drop the mandate' and 'Runner configurations', poc-4-5 plan.md S45-D3)\nB2: accepted (poc-4-1 plan.md S41-D8, test_plan.md rows 'Answers section' and 'Accounted'; see the new N1 on extracting paths)\nB3: accepted (poc-4-1 plan.md S41-D3 and S41-D4, poc-4-4 plan.md S44-D1 and S44-D7, poc-4-6 plan.md S46-D3 and S46-D5)\nA1: accepted (poc-4-1 plan.md S41-D5(c), test_plan.md 'Recheck inputs')\nA2: accepted (poc-4-1 plan.md S41-D6)\nA3: accepted (poc-4-1 plan.md S41-D3, test_plan.md 'Mode from the round')\nA4: accepted (poc-4-1 plan.md S41-D5(a), test_plan.md 'Recheck inputs')\nA5: re-raised (poc-4-1 plan.md S41-D12, S41-D7; poc-4-3 plan.md S43-D4; base AGENTS.md)\nA6: accepted (poc-4-1 plan.md S41-D5 and In scope, test_plan.md 'Rebuild', poc-4-2 plan.md S42-D9, poc-4-3 plan.md S43-D1; see N3)\nA7: accepted (poc-4-1 plan.md S41-D5(b), test_plan.md 'Recheck inputs', poc-4-3 plan.md S43-D1)\nA8: accepted (docs/slices/README.md; Order of work lines in poc-4-1 to poc-4-6 plan.md)\nA9: accepted (poc-4-1 plan.md S41-D4)\nA10: accepted (poc-4-1 plan.md S41-D13, test_plan.md 'Benchmark scoring')\nA11: accepted (poc-4-1 plan.md Assets and holders, poc-4-3 plan.md S43-D2)\nS1: accepted (poc-4-1 plan.md S41-D8, Environment facts)",
      "failure_scenario": "None. This finding is the accounting record for the round.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to plan/c1/r2/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| A5 | high | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: S41-D12 names the five further sentences and replaces the false claim with a search of every "advisory" and "blocking" hit; the review notes check it |
| N1 | high | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: S41-D7 gives the `fixed: <path>[, <path>…]: <what changed>` form with at least one path; S41-D8 and the "Answers section" row refuse a `fixed:` answer that names no path |
| N2 | medium | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: a path the change deletes or renames is accepted (S41-D8 and the "Answers section" row) |
| N3 | low | fixed: docs/slices/poc-4-1-review-prompts/test_plan.md: the "Rebuild" row includes the evidence text and a changed-evidence mismatch |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |

## Round 3

### Attempt plan/c1/r3/plan/1

Commit `341fa47`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-1-review-prompts/plan.md` `d71421a77362`, `docs/slices/poc-4-1-review-prompts/test_plan.md` `6b3d36485fcc`.

Status: completed; approvable within the threat model: no.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 3 of the plan review of slice 4.1 (review prompts and severity, #38), a recheck of your earlier report (round 2, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it. (Slice 4.1 replaces this with an `accounted` field; until then this finding carries it.)
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## The owner's change since your last round

On 2026-11-08 the owner decided: "Everything that we will use in SDLC delivery process has to be analyzed in this slice or upcoming slices, if mandate prompts are going to be used, then it must be analyzed, as we have the seen prompts affects the results of the review", and raised the benchmark budget from 40 to 50 runs. The author changed three plans (commit `341fa47`):
- 4.1 S41-D14: the three mandates are provisional constants, with the SHA-256 of the one used in the start entry; the owner chooses after 4.5's measurement; later changes follow the learning loop.
- 4.4 S44-D13: the review prompt is a seventh research item; `research.md` drafts the initial, recheck and final mandates, each sentence with a source tag and the failure mode it counters; S44-D11's learning loop covers mandate wording.
- 4.5: the budget is 50 (S45-D1); configurations `open-B`, `recheck-A` and `recheck-B` (S45-D3); a recheck case with a false `fixed:` answer (S45-D5); 47 runs planned (S45-D7); rule (c2) for choosing the wording (S45-D8). The final review's mandate is not measured on cases; its findings are tracked slice by slice.

Check this change like a fix: is it consistent across the three plans and their test plans, is every new decision tested, and does it contradict anything approved?

## Your earlier report (round 2, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "Base AGENTS.md, sections PoC scope and proportion (Review findings, Review loop, Few exceptions) and Independent review (Implementation review, Report sections). plan.md:54. test_plan.md:58-59: the review checks only 'each sentence S41-D12 names'.",
      "failure_scenario": "The implementer edits exactly the sentences S41-D12 lists, and the review checks only those. AGENTS.md then still says the review ends once every blocking finding is handled, and that hardening ideas are 'advisory at most'. Meanwhile 4.3's check (S43-D4) fails a rejected high finding that the next round did not accept. The rulebook and the record check now disagree, and AGENTS.md's own rule says they must not.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A5",
      "kind": "advisory",
      "line": 54,
      "problem": "[high] Re-raised, partly fixed. S41-D12 now names four sentences. But its closing claim, 'No other sentence of the rulebook mentions the old `advisory` handling', is false for the base AGENTS.md. Several sentences are still left unchanged: 'Reviewers should expect production-hardening ideas \u2026 and report them as advisory at most' (Review findings). 'Besides blocking and advisory findings, every round may report\u2026' (Report sections). 'findings on purpose comments and names are fix-or-defer' (Implementation review). 'The review ends when every blocking finding is fixed, accepted as rejected, or decided by the user' (Review loop): this one ignores high findings, which S41-D7 and S43-D4 require to be accepted or decided by the owner. 'one line in the review report is enough' (Few exceptions) does not say which severity that gets."
    },
    {
      "evidence": "plan.md:49-50. test_plan.md:33-34: the refusals cover only a wrong first word and a `fixed:` path missing from the copy; nothing covers a `fixed:` answer with no path. The author's answer table in this round's prompt.",
      "failure_scenario": "An implementation pulls out whatever path-shaped tokens it finds. The author writes 'fixed: S41-D5 now covers it'. No path is extracted, so the read check passes with nothing to check. The recheck accepts the answer without opening anything, and the B2/R5-A6 control is a false green for exactly the answers written in prose.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "N1",
      "kind": "advisory",
      "line": 50,
      "problem": "[high] The S41-D8 check, 'a file named in a `fixed:` answer was not read', depends on extracting file paths from answers. S41-D7 gives `fixed:` only as '(the files changed)' and defines no syntax for those paths. Neither the plan nor the test plan refuses a `fixed:` answer that names no file. The author's own round-1 answers show this case ('fixed: 4.1 S41-D2 (...)', 'fixed: the answers section's hash goes into\u2026'): they name decisions, not paths."
    },
    {
      "evidence": "plan.md:50; test_plan.md:33. AGENTS.md: 'Retire documents with `git mv`'; step 3 removes dead code.",
      "failure_scenario": "The author answers a finding with 'fixed: removed scripts/old_helper.py'. The recheck is refused before any call, and the author has to reword the answer to get around the check.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "N2",
      "kind": "advisory",
      "line": 50,
      "problem": "[medium] 'The launcher refuses an answers section whose `fixed:` paths do not exist in the copy' refuses a valid fix that deletes or retires a file with `git mv` into an archive: the named path no longer exists. The plan does not say whether the old path or the new one is named."
    },
    {
      "evidence": "test_plan.md:36; plan.md:47; docs/slices/poc-4-2-review-inputs/plan.md:47.",
      "failure_scenario": "The rebuild works only once evidence is empty or fixed in the test. A later change to the evidence breaks the `full_prompt_sha256` match, and no test catches it.",
      "file": "docs/slices/poc-4-1-review-prompts/test_plan.md",
      "id": "N3",
      "kind": "advisory",
      "line": 36,
      "problem": "[low] The 'Rebuild' row rebuilds the recheck prompt from the entry, the earlier report and the answers section, but not from the evidence section, which is now part of every recheck prompt (S41-D5(c), 4.2 S42-D9)."
    },
    {
      "evidence": "B1: accepted (poc-4-1 plan.md S41-D2, test_plan.md rows 'No way to drop the mandate' and 'Runner configurations', poc-4-5 plan.md S45-D3)\nB2: accepted (poc-4-1 plan.md S41-D8, test_plan.md rows 'Answers section' and 'Accounted'; see the new N1 on extracting paths)\nB3: accepted (poc-4-1 plan.md S41-D3 and S41-D4, poc-4-4 plan.md S44-D1 and S44-D7, poc-4-6 plan.md S46-D3 and S46-D5)\nA1: accepted (poc-4-1 plan.md S41-D5(c), test_plan.md 'Recheck inputs')\nA2: accepted (poc-4-1 plan.md S41-D6)\nA3: accepted (poc-4-1 plan.md S41-D3, test_plan.md 'Mode from the round')\nA4: accepted (poc-4-1 plan.md S41-D5(a), test_plan.md 'Recheck inputs')\nA5: re-raised (poc-4-1 plan.md S41-D12, S41-D7; poc-4-3 plan.md S43-D4; base AGENTS.md)\nA6: accepted (poc-4-1 plan.md S41-D5 and In scope, test_plan.md 'Rebuild', poc-4-2 plan.md S42-D9, poc-4-3 plan.md S43-D1; see N3)\nA7: accepted (poc-4-1 plan.md S41-D5(b), test_plan.md 'Recheck inputs', poc-4-3 plan.md S43-D1)\nA8: accepted (docs/slices/README.md; Order of work lines in poc-4-1 to poc-4-6 plan.md)\nA9: accepted (poc-4-1 plan.md S41-D4)\nA10: accepted (poc-4-1 plan.md S41-D13, test_plan.md 'Benchmark scoring')\nA11: accepted (poc-4-1 plan.md Assets and holders, poc-4-3 plan.md S43-D2)\nS1: accepted (poc-4-1 plan.md S41-D8, Environment facts)",
      "failure_scenario": "None. This finding is the accounting record for the round.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "yes"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| A5 | high | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: S41-D12 names the five further sentences and replaces the false claim with a search of every "advisory" and "blocking" hit; the review notes check it |
| N1 | high | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: S41-D7 gives the `fixed: <path>[, <path>…]: <what changed>` form with at least one path; S41-D8 and the "Answers section" row refuse a `fixed:` answer that names no path |
| N2 | medium | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: a path the change deletes or renames is accepted (S41-D8 and the "Answers section" row) |
| N3 | low | fixed: docs/slices/poc-4-1-review-prompts/test_plan.md: the "Rebuild" row includes the evidence text and a changed-evidence mismatch |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "poc-4-1 plan.md:55 (S41-D14: \"the owner chooses from 4.5's report. A later change to a mandate follows the learning loop ... approved by the owner\"). poc-4-5 plan.md:58 (S45-D8(c2): \"the drafts become the mandates; otherwise ... the owner chooses (S41-D14)\"). poc-4-4 plan.md:51 (S44-D11) and :52 (S44-D13 drafts all three mandates). poc-4-5 plan.md:57: the final mandate is not measured.",
      "failure_scenario": "4.5's run meets the (c2) threshold. The implementer reads (c2) as the decision and replaces the launcher's initial and recheck constants, and perhaps the final one as well, which was never measured. The owner is not asked. That contradicts S41-D14 and the learning loop. Or the implementer follows S41-D14 and waits for the owner, and (c2) is a dead rule. The plans support both readings, and no test settles it.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "C1",
      "kind": "blocking",
      "line": 58,
      "problem": "Contradiction on who adopts the mandate wording. 4.1 S41-D14 says the owner chooses from 4.5's report, and that any later mandate change is approved by the owner (S44-D11). 4.5 S45-D8(c2) says that if `open-B` and `recheck-B` together detect at least two more defects with no extra false blockers, \"the drafts become the mandates\". The owner chooses only in the other branch. Neither plan says which slice changes the launcher constants when (c2) adopts the drafts, or whether 4.4's final-mandate draft, which (c2) never measures, is adopted along with them."
    },
    {
      "evidence": "test_plan.md:8 and :14; test_plan.md:29 (Mandate identity, S41-D14); plan.md:55-56 (D14 before D13); plan.md:63-72 and :105-109.",
      "failure_scenario": "A reviewer or implementer who checks coverage against \"D1 to D13\" misses D14, or the start entry's mandate hash goes undocumented as recorded state.",
      "file": "docs/slices/poc-4-1-review-prompts/test_plan.md",
      "id": "N4",
      "kind": "advisory",
      "line": 8,
      "problem": "[low] The test plan's Goal and Inputs still say decisions \"S41-D1 to S41-D13\", but the new S41-D14 is tested by the \"Mandate identity\" row. In plan.md, S41-D14 sits before S41-D13. The success criteria and the hidden-state table do not mention the mandate SHA-256 in the start entry."
    },
    {
      "evidence": "poc-4-1 plan.md:50 (S41-D8 fails the attempt); poc-4-5 test_plan.md:31 (only re-raise means detected, accept means missed); poc-4-5 plan.md:51 (retries count against 50).",
      "failure_scenario": "`recheck-B` produces a failed attempt because it skipped the file. The runner retries until one attempt completes, spending runs from the 3 spare, or it counts the failure as missed. The two wordings are then compared under different handling.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "N5",
      "kind": "advisory",
      "line": 31,
      "problem": "[medium] The recheck case runs through 4.1's recheck machinery, where S41-D8 fails an attempt that did not read a file a `fixed:` answer names. The 4.5 plan and test plan do not say how such a failed attempt is scored for `recheck-A` and `recheck-B`: as missed, or as a retry against the budget."
    },
    {
      "evidence": "A5: accepted (poc-4-1 plan.md S41-D12; test_plan.md Review notes)\nN1: accepted (poc-4-1 plan.md S41-D7, S41-D8; test_plan.md 'Answers section')\nN2: accepted (poc-4-1 plan.md S41-D8; test_plan.md 'Answers section')\nN3: accepted (poc-4-1 test_plan.md 'Rebuild')\nACCOUNTED: accepted (stand-in, as stated)\nOwner change 341fa47: checked poc-4-1 plan.md S41-D14 and test_plan.md 'Mandate identity'; poc-4-4 plan.md S44-D11, S44-D13 and test_plan.md 'Review-prompt research'; poc-4-5 plan.md S45-D1, D3, D5, D7, D8 and test_plan.md rows 'Budget', 'Mandate variants', 'Recheck case', 'Decision rules' (see C1, N4, N5)",
      "failure_scenario": "None. This finding is the accounting record for the round.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "no"
}
```

#### Answers to plan/c1/r3/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| C1 | blocking | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D8 now reports counts and the owner chooses each mandate wording, initial and recheck separately, as S41-D14 says; the launcher's constants change only after that choice, in 4.5b; the final draft is chosen by reason |
| N4 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: the ranges say S41-D1 to S41-D16, S41-D14 follows S41-D13, and the success criteria and the hidden-state table name the mandate's SHA-256 |
| N5 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: S45-D5 and the "Recheck case" row: an attempt that fails the read check counts as a miss, not a retry |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |

## Round 4

### Attempt plan/c1/r4/plan/1

Commit `a99d4f8`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-1-review-prompts/plan.md` `1d319b1cb8d7`, `docs/slices/poc-4-1-review-prompts/test_plan.md` `320c04c0c122`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 4 of the plan review of slice 4.1 (review prompts and severity, #38), a recheck of your earlier report (round 3, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it. (Slice 4.1 replaces this with an `accounted` field; until then this finding carries it.)
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## The owner's change since your last round

After a study of how the industry runs agent-first delivery and an independent critique of it (summary: `docs/slices/agentic-sdlc-poc/industry_research.md`), the owner decided on 2026-11-09: "I accept your recommendations for my decisions". The author changed the plans in commit `a99d4f8`:
- 4.1: S41-D15 (a missing-thing finding states "X has no Y; searched A, B, C"; do not report what a passing gate already checks, but report defects in gates; the task text is given as claims to verify; a recheck may answer `cannot determine`), S41-D16 (an origin stage on every finding).
- 4.4: S44-D8 (each list is also the author's guideline), S44-D9 (each DPL entry names the check that now catches it), S44-D10 (Opus and Sonnet critique; no Codex), S44-D13 (the research also covers severity schemes and the prompt around the mandate).
- 4.5: rewritten as a blinded screening study (`short+list`, `open+list`, `open-B+list`, recheck A and B; the same severity rules for every setup; cases that did not shape the lists; a decoy; repeats only where setups disagree; counts with exact intervals; the owner decides; no model comparison and no Codex; budget 60 with retries).
- 4.6: S46-D13 (a decision brief generated from the records opens every plan PR and final PR), S46-D14 (the grill-me skill moves into the repository).
- `AGENTS.md`: Opus is the default reviewer by the owner's reasoned choice; the Codex exception is removed.
- Every decision source quotes the owner's words next to its link.

Check this change like a fix: is it consistent across the plans and their test plans, is every new decision tested, and does it contradict anything approved?

## Your earlier report (round 3, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "poc-4-1 plan.md:55 (S41-D14: \"the owner chooses from 4.5's report. A later change to a mandate follows the learning loop ... approved by the owner\"). poc-4-5 plan.md:58 (S45-D8(c2): \"the drafts become the mandates; otherwise ... the owner chooses (S41-D14)\"). poc-4-4 plan.md:51 (S44-D11) and :52 (S44-D13 drafts all three mandates). poc-4-5 plan.md:57: the final mandate is not measured.",
      "failure_scenario": "4.5's run meets the (c2) threshold. The implementer reads (c2) as the decision and replaces the launcher's initial and recheck constants, and perhaps the final one as well, which was never measured. The owner is not asked. That contradicts S41-D14 and the learning loop. Or the implementer follows S41-D14 and waits for the owner, and (c2) is a dead rule. The plans support both readings, and no test settles it.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "C1",
      "kind": "blocking",
      "line": 58,
      "problem": "Contradiction on who adopts the mandate wording. 4.1 S41-D14 says the owner chooses from 4.5's report, and that any later mandate change is approved by the owner (S44-D11). 4.5 S45-D8(c2) says that if `open-B` and `recheck-B` together detect at least two more defects with no extra false blockers, \"the drafts become the mandates\". The owner chooses only in the other branch. Neither plan says which slice changes the launcher constants when (c2) adopts the drafts, or whether 4.4's final-mandate draft, which (c2) never measures, is adopted along with them."
    },
    {
      "evidence": "test_plan.md:8 and :14; test_plan.md:29 (Mandate identity, S41-D14); plan.md:55-56 (D14 before D13); plan.md:63-72 and :105-109.",
      "failure_scenario": "A reviewer or implementer who checks coverage against \"D1 to D13\" misses D14, or the start entry's mandate hash goes undocumented as recorded state.",
      "file": "docs/slices/poc-4-1-review-prompts/test_plan.md",
      "id": "N4",
      "kind": "advisory",
      "line": 8,
      "problem": "[low] The test plan's Goal and Inputs still say decisions \"S41-D1 to S41-D13\", but the new S41-D14 is tested by the \"Mandate identity\" row. In plan.md, S41-D14 sits before S41-D13. The success criteria and the hidden-state table do not mention the mandate SHA-256 in the start entry."
    },
    {
      "evidence": "poc-4-1 plan.md:50 (S41-D8 fails the attempt); poc-4-5 test_plan.md:31 (only re-raise means detected, accept means missed); poc-4-5 plan.md:51 (retries count against 50).",
      "failure_scenario": "`recheck-B` produces a failed attempt because it skipped the file. The runner retries until one attempt completes, spending runs from the 3 spare, or it counts the failure as missed. The two wordings are then compared under different handling.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "N5",
      "kind": "advisory",
      "line": 31,
      "problem": "[medium] The recheck case runs through 4.1's recheck machinery, where S41-D8 fails an attempt that did not read a file a `fixed:` answer names. The 4.5 plan and test plan do not say how such a failed attempt is scored for `recheck-A` and `recheck-B`: as missed, or as a retry against the budget."
    },
    {
      "evidence": "A5: accepted (poc-4-1 plan.md S41-D12; test_plan.md Review notes)\nN1: accepted (poc-4-1 plan.md S41-D7, S41-D8; test_plan.md 'Answers section')\nN2: accepted (poc-4-1 plan.md S41-D8; test_plan.md 'Answers section')\nN3: accepted (poc-4-1 test_plan.md 'Rebuild')\nACCOUNTED: accepted (stand-in, as stated)\nOwner change 341fa47: checked poc-4-1 plan.md S41-D14 and test_plan.md 'Mandate identity'; poc-4-4 plan.md S44-D11, S44-D13 and test_plan.md 'Review-prompt research'; poc-4-5 plan.md S45-D1, D3, D5, D7, D8 and test_plan.md rows 'Budget', 'Mandate variants', 'Recheck case', 'Decision rules' (see C1, N4, N5)",
      "failure_scenario": "None. This finding is the accounting record for the round.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "no"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| C1 | blocking | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D8 now reports counts and the owner chooses each mandate wording, initial and recheck separately, as S41-D14 says; the launcher's constants change only after that choice, in 4.5b; the final draft is chosen by reason |
| N4 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: the ranges say S41-D1 to S41-D16, S41-D14 follows S41-D13, and the success criteria and the hidden-state table name the mandate's SHA-256 |
| N5 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: S45-D5 and the "Recheck case" row: an attempt that fails the read check counts as a miss, not a retry |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "poc-4-5 plan.md:57 (\"The launcher's mandate constants change only after the owner's choice, in 4.5b\"); :77-80 (In scope lists only the runner, tests/review_benchmark/, tooling tests, the report); :84 (Out of scope: \"Changing the review setup itself (4.1 to 4.4)\"); poc-4-5 test_plan.md has no row for the constant change. 4.1's \"Mandate identity\" row (test_plan.md:32) does show that a changed constant changes the start entry's hash.",
      "failure_scenario": "The owner picks the B recheck wording. The 4.5b implementer sees that the launcher is out of scope and leaves the constants unchanged, or changes them in a PR whose plan never listed the edit. Either way the owner's choice and the shipped mandate can drift apart until someone notices.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "R4-1",
      "kind": "advisory",
      "line": 57,
      "problem": "[medium] S45-D8 (the C1 fix) says the launcher's mandate constants change \"in 4.5b\" after the owner chooses. But 4.5's In scope list (line 77) does not include `scripts/run_independent_review.py`, and its Out of scope list (line 84) says \"Changing the review setup itself (4.1 to 4.4)\". So no slice's scope owns the edit to the constants, and no test row covers it."
    },
    {
      "evidence": "plan.md:50 (S41-D8: \"`status` is `accepted` or `re-raised`\"); plan.md:57 (S41-D15: \"`accounted` also takes the status `cannot determine`\"); plan.md:54 (S41-D12 names the sentences that change; the accept-or-re-raise sentence is not one of them); approved AGENTS.md, Review loop: \"either accepts it or re-raises it with new evidence; a finding still disputed after that goes to the user\".",
      "failure_scenario": "An implementer builds the schema from S41-D8 and rejects `cannot determine`, so the test plan's \"Cannot determine\" row fails. Or the schema accepts it, but `AGENTS.md` still allows only accept or re-raise. An author then reads a `cannot determine` as neither status and the finding is not escalated, while 4.6's brief expects it to be.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "R4-2",
      "kind": "advisory",
      "line": 57,
      "problem": "[medium] S41-D15 adds a third recheck status, `cannot determine`, which goes to the owner. S41-D8 (line 50) still says `status` is `accepted` or `re-raised`. S41-D12's list of `AGENTS.md` sentences that change also leaves out the Review loop sentence \"either accepts it or re-raises it with new evidence\". So the plan and the rulebook it edits will disagree on what a recheck may answer."
    },
    {
      "evidence": "plan.md:43 (\"... the paths under review; the task; ...\"); plan.md:57 (\"given as claims to verify, in a section of that name\"); test_plan.md:25 vs :27.",
      "failure_scenario": "The implementer writes the order test against \"task\" and the name test against \"claims to verify\". One of the two tests fails, or the section ends up with both headings.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "R4-3",
      "kind": "advisory",
      "line": 43,
      "problem": "[low] S41-D1's fixed section order and the test plan's \"Section order\" row still call the section \"the task\". S41-D15 says the task text goes into a section named \"claims to verify\". The two decisions should use the same section name."
    },
    {
      "evidence": "poc-4-1 plan.md:58; poc-4-6 plan.md:44 (S46-D1 stage names); poc-4-6 plan.md:56 and test_plan.md:23 (origin-against-found table); poc-4-5 plan.md:57.",
      "failure_scenario": "The brief or the benchmark report puts the found stage under 4.6's names and the origin under 4.1's names. The table shows false mismatches such as \"tests\" against \"tests first\".",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "R4-4",
      "kind": "advisory",
      "line": 58,
      "problem": "[low] S41-D16's `origin_stage` values (discovery, requirements, architecture, tests, implementation, unknown) do not match 4.6's seven stage names (\"architecture and interfaces\", \"tests first\", final review, handoff). The \"origin against found\" table in 4.5 and 4.6 then needs a mapping that no plan states."
    },
    {
      "evidence": "C1: accepted (poc-4-5 plan.md S45-D8, In/Out of scope; poc-4-5 test_plan.md; poc-4-1 plan.md S41-D14; slice index grep for 4.5b). Residual scope gap reported as R4-1\nN4: accepted (poc-4-1 plan.md Goal, S41-D13/D14 order, success criteria, hidden-state table; poc-4-1 test_plan.md Goal and Inputs)\nN5: accepted (poc-4-5 plan.md S45-D5; poc-4-5 test_plan.md 'Recheck case')\nACCOUNTED: accepted (stand-in, as stated)\nOwner change a99d4f8: checked poc-4-1 plan.md S41-D15, D16 and test_plan.md rows 'Reporting bounds', 'Cannot determine', 'Origin stage'; poc-4-6 plan.md S46-D1, D13, D14 and test_plan.md rows 'Decision brief', 'Grill-me in the repository'; poc-4-5 plan.md S45-D1 to D10 and test_plan.md. Every new decision in the plans I opened has a test row. See R4-2 to R4-4",
      "failure_scenario": "None. This finding is the accounting record for the round.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to plan/c1/r4/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| R4-1 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: 4.5's scope now includes setting the launcher's mandate constants after the owner's choice, and a "Mandate constants" row tests it |
| R4-2 | medium | fixed: docs/slices/poc-4-1-review-prompts/plan.md: S41-D8 lists `cannot determine` among the statuses, and S41-D12 changes the Review loop sentence to allow it, going to the user |
| R4-3 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-1-review-prompts/test_plan.md: S41-D1 and the "Section order" row name the section "claims to verify" |
| R4-4 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md: S41-D16 uses 4.6's stage names, and the stage that found a finding is the reviewing unit's stage ("final review" for the final unit) |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
