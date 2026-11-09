# Plan review — 4.6 (#43), stage rules

Record of the plan review of slice 4.6 (#43), stage rules in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

Round 4 was the last allowed round. The fixes of its advisory findings (answers below) were made afterwards and are not rechecked; the owner decides whether they need another round.

## Round 1

### Attempt plan/c1/r1/plan/1

Commit `dfc88e2`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-6-stage-rules/plan.md` `36f5b2ea484f`, `docs/slices/poc-4-6-stage-rules/test_plan.md` `4b2d94bb80b3`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 1 (the initial review), of slice 4.6 of the agentic-SDLC PoC: `docs/slices/poc-4-6-stage-rules/plan.md` and `test_plan.md` (GitHub issue #43). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#43)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** the plan's original slice 4. The `AGENTS.md` slice workflow gains stages 2 to 7, with what each stage produces, how it is reviewed and which checks run, or "none, with a reason".

**Decided / carried over:**
- **Stages 2 to 7:** requirements, architecture and interfaces, tests first, implementation, final review, handoff (the plan's Goal table). Each uses sub-issue 4.4's list for its stage.
- **Upstream reviews** ([reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090)): upstream documents get their own review stages, and a correction to an upstream document reopens the reviews built on it.
- **A final review with a deliberately open prompt,** "What did everyone before you miss?" ([principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147)). Its second pass gets the finding history through its prompt.
- **From the plan review** (#33's description):
  - only the owner waives a blocker (D12);
  - earlier escalation on a baseline conflict, or when rounds stop making progress (D13);
  - D38's working rules: interface skeletons, the expected failure recorded, targeted mutants on security paths.
- **Handoff format:** every discovered issue carries a status and a tracking link, and is updated when a later fix lands (owner, 2026-11-08: the PRs' discovered-issue lists were partly stale and untracked).
- **Discoverability** ([discoverability](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)): `AGENTS.md`'s "Start here" table says how to run a review and where attempt logs and review records live.

**Done when:** `AGENTS.md` and the slice templates state the stages; a slice made from the templates passes the checks.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: what the reviewer sees, and finding the origin of a problem** (agreed with the owner, 2026-11-08)

**Today.** The review launcher (`scripts/run_independent_review.py`, slice 2) gives the reviewer:
- the files under review, which the author chooses with `--path`;
- the whole change as a diff;
- a frozen copy of the entire repository;
- the task text, which states the intent and the questions;
- the base branch's rules.

The reviewer can open any upstream document (requirements, architecture, plan), but only the task text leads it there. In slice 2's own review the task text named the plan, and the reviewer read `plan.md` and `test_plan.md` and found plan-versus-code problems. In the benchmark, nothing pointed upstream, and the defect that lived partly in `docs/requirements.md` (DPL-004) was missed.

**Weak spots:**
1. **The author chooses the file list.** A file left off it is still in the diff, but nothing makes the reviewer examine it. That is how DPL-005 slipped through: the workflow file was not on the reviewer's list. With the owner's decision that a reviewer must open every listed file, the list matters even more.
2. **No question asks where a problem originates.** POC-D5 asks for fixes at the origin, but no review question asks whether the cause lies upstream.

**Proposals for slice 4:**
- The launcher takes the files under review from the diff, so the author cannot leave one out.
- The task text names the upstream items the change traces to: its requirement and architecture IDs (known to `make qa-trace`) and the plan's decisions.
- Every review asks: "Does the problem originate upstream (a requirement, the architecture, the plan)? If so, name the document and section."
- Upstream documents get their own review stages (requirements review, architecture review), and a correction to an upstream document reopens the reviews built on it (already in the plan's roadmap for slice 4).

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

### Issue #33's description (the original slice-4 inputs)

## Status

Outline in the agentic-sdlc-poc plan (PR #31, roadmap slice 4). Planned after the slice-2 benchmark report, with its own grill-me, plan and review. The plan's slice-4 row points here; the decisions made in the grill-me move into slice 4's `plan.md`.

## Inputs for its grill-me

- **Review lists** for each artifact type (plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code, final review, handoff), given to the reviewer as the launcher's prompt file.
- **Form** (short questions or a full checklist): from the slice-2 benchmark's decision rule.
- **Coding guideline:** a short one, holding only what tools cannot check (error handling, logging, structure, maintainability, whether a name says what it does). What `make lint` and the existing coding rules already enforce stays out.
- **Home:** binding rules in `AGENTS.md` with the review lists as small files in one folder, or everything in `AGENTS.md`.
- **Reviewers per stage:** from the benchmark and slice 5's measured quota.
- **How the lists grow:** a blocker that slips past a list leads to a proposed addition that the owner approves.
- **Carried from the plan review** (`docs/slices/agentic-sdlc-poc/plan_review.md`):
  - the final review's second pass receives the finding history through its prompt;
  - only the owner waives a blocker (D12);
  - earlier escalation on a baseline conflict or when rounds stop making progress (D13);
  - D38's working rules: interface skeletons, the expected failure recorded, targeted mutants on security paths;
  - benchmark cases for stage artifacts (a flawed requirement, a weak test, a design gap).

Refs #16, #31.

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

Lost: another unit's report overwrote its file before the fix of the report path (DPL-011). The log keeps its SHA-256 `b8bcf94171ee`.

## Round 2

### Attempt plan/c1/r2/plan/1

Commit `f070669`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-6-stage-rules/plan.md` `36f5b2ea484f`, `docs/slices/poc-4-6-stage-rules/test_plan.md` `4b2d94bb80b3`.

Status: interrupted (no end entry: the launcher stopped, or the publication check withheld the report).

#### Prompt

```markdown
**Note on this round:** round 1 of this review unit completed with verdict "no", but its report was lost: a launcher bug made all six plan reviews write the same report file (fixed in commit f070669, which is in your copy). This round 2 is therefore a full review with the open mandate, not a recheck.

## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 2 (a full review; see the note above), of slice 4.6 of the agentic-SDLC PoC: `docs/slices/poc-4-6-stage-rules/plan.md` and `test_plan.md` (GitHub issue #43). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#43)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** the plan's original slice 4. The `AGENTS.md` slice workflow gains stages 2 to 7, with what each stage produces, how it is reviewed and which checks run, or "none, with a reason".

**Decided / carried over:**
- **Stages 2 to 7:** requirements, architecture and interfaces, tests first, implementation, final review, handoff (the plan's Goal table). Each uses sub-issue 4.4's list for its stage.
- **Upstream reviews** ([reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090)): upstream documents get their own review stages, and a correction to an upstream document reopens the reviews built on it.
- **A final review with a deliberately open prompt,** "What did everyone before you miss?" ([principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147)). Its second pass gets the finding history through its prompt.
- **From the plan review** (#33's description):
  - only the owner waives a blocker (D12);
  - earlier escalation on a baseline conflict, or when rounds stop making progress (D13);
  - D38's working rules: interface skeletons, the expected failure recorded, targeted mutants on security paths.
- **Handoff format:** every discovered issue carries a status and a tracking link, and is updated when a later fix lands (owner, 2026-11-08: the PRs' discovered-issue lists were partly stale and untracked).
- **Discoverability** ([discoverability](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)): `AGENTS.md`'s "Start here" table says how to run a review and where attempt logs and review records live.

**Done when:** `AGENTS.md` and the slice templates state the stages; a slice made from the templates passes the checks.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: what the reviewer sees, and finding the origin of a problem** (agreed with the owner, 2026-11-08)

**Today.** The review launcher (`scripts/run_independent_review.py`, slice 2) gives the reviewer:
- the files under review, which the author chooses with `--path`;
- the whole change as a diff;
- a frozen copy of the entire repository;
- the task text, which states the intent and the questions;
- the base branch's rules.

The reviewer can open any upstream document (requirements, architecture, plan), but only the task text leads it there. In slice 2's own review the task text named the plan, and the reviewer read `plan.md` and `test_plan.md` and found plan-versus-code problems. In the benchmark, nothing pointed upstream, and the defect that lived partly in `docs/requirements.md` (DPL-004) was missed.

**Weak spots:**
1. **The author chooses the file list.** A file left off it is still in the diff, but nothing makes the reviewer examine it. That is how DPL-005 slipped through: the workflow file was not on the reviewer's list. With the owner's decision that a reviewer must open every listed file, the list matters even more.
2. **No question asks where a problem originates.** POC-D5 asks for fixes at the origin, but no review question asks whether the cause lies upstream.

**Proposals for slice 4:**
- The launcher takes the files under review from the diff, so the author cannot leave one out.
- The task text names the upstream items the change traces to: its requirement and architecture IDs (known to `make qa-trace`) and the plan's decisions.
- Every review asks: "Does the problem originate upstream (a requirement, the architecture, the plan)? If so, name the document and section."
- Upstream documents get their own review stages (requirements review, architecture review), and a correction to an upstream document reopens the reviews built on it (already in the plan's roadmap for slice 4).

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

### Issue #33's description (the original slice-4 inputs)

## Status

Outline in the agentic-sdlc-poc plan (PR #31, roadmap slice 4). Planned after the slice-2 benchmark report, with its own grill-me, plan and review. The plan's slice-4 row points here; the decisions made in the grill-me move into slice 4's `plan.md`.

## Inputs for its grill-me

- **Review lists** for each artifact type (plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code, final review, handoff), given to the reviewer as the launcher's prompt file.
- **Form** (short questions or a full checklist): from the slice-2 benchmark's decision rule.
- **Coding guideline:** a short one, holding only what tools cannot check (error handling, logging, structure, maintainability, whether a name says what it does). What `make lint` and the existing coding rules already enforce stays out.
- **Home:** binding rules in `AGENTS.md` with the review lists as small files in one folder, or everything in `AGENTS.md`.
- **Reviewers per stage:** from the benchmark and slice 5's measured quota.
- **How the lists grow:** a blocker that slips past a list leads to a proposed addition that the owner approves.
- **Carried from the plan review** (`docs/slices/agentic-sdlc-poc/plan_review.md`):
  - the final review's second pass receives the finding history through its prompt;
  - only the owner waives a blocker (D12);
  - earlier escalation on a baseline conflict or when rounds stop making progress (D13);
  - D38's working rules: interface skeletons, the expected failure recorded, targeted mutants on security paths;
  - benchmark cases for stage artifacts (a flawed requirement, a weak test, a design gap).

Refs #16, #31.

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

### Attempt plan/c1/r2/plan/2

Commit `d56c69a`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-6-stage-rules/plan.md` `36f5b2ea484f`, `docs/slices/poc-4-6-stage-rules/test_plan.md` `4b2d94bb80b3`.

Status: completed; approvable within the threat model: no.

#### Prompt

The same task prompt as attempt plan/c1/r2/plan/1 (SHA-256 `7c835cb4a7b5`).

#### Report

```json
{
  "findings": [
    {
      "evidence": "S46-D5: \"a fresh review with the open prompt 'What did everyone before you miss?', given all the evidence and no question list\". S44-D1 lists \"final review\" as an artifact type with its own list. S44-D5: the proof question and the CI-job question go into the \"(code, final review)\" lists. 4.4 test plan line 26: \"The requirements, tests and final-review lists contain the proof question\". S41-D1/D3: the launcher always writes the stage checklist section (if given), and `final` mode gets the S41-D2 mandate verbatim. S42-D4 puts the upstream question \"in every prompt\". The owner's decision comment says the checklist is the minimum for \"every review\", while the principle comment says \"no question list\". These plans resolve that tension in opposite directions.",
      "failure_scenario": "The implementer builds the final review from 4.6 (no `--stage`, a custom task text) or from 4.4/4.1 (`--mode final --stage final-review`). Either way one approved plan is broken. A rule in AGENTS.md (S46-D5) then contradicts the launcher's behaviour and 4.4's list. Because S46-D3 says implementation runs without stopping, nobody asks the owner which one they meant.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-B1",
      "kind": "blocking",
      "line": 40,
      "problem": "Contradiction between plans: S46-D5 says the final review gets \"no question list\", but 4.4 writes a final-review checklist and makes every stage list the minimum of every review. 4.1 also fixes the final-mode prompt to its own open-mandate text, which is not \"What did everyone before you miss?\"."
    },
    {
      "evidence": "S41-D4: a recheck prompt holds \"the reviewer's own earlier report ... and the author's answers\" and \"never puts in the review record\". It is refused \"without a completed earlier attempt by the same reviewer label\". The finding history is the findings and answers of all earlier review units (plan review, implementation review), which live in review records (4.3). The 4.6 test plan proves D5 only by review quoting rule text (test_plan.md:24). No row in the 4.1, 4.3 or 4.6 test plans covers a final-review second pass or the history input.",
      "failure_scenario": "The rule text says the second pass gets the history, so the review-based proof passes. At slice 5 the final reviewer's second pass runs as a 4.1 recheck: it sees only its own first-pass report and is refused the review records. Earlier blockers that were \"accepted as rejected\" or deferred are never shown to it. This is an approved carry-over (#33, PoC plan mapping D11\u2013D14) without a working mechanism or a test.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-B2",
      "kind": "blocking",
      "line": 40,
      "problem": "No plan builds or tests S46-D5's \"second pass gets the finding history through its prompt\", and the mechanism it names (4.1's recheck inputs) does not deliver a finding history."
    },
    {
      "evidence": "test_plan.md:24: \"quote, for each of S46-D2 to S46-D10, the AGENTS.md or template text\", so D1 and D11 are left out. Row 1 checks only that a bundle made from the templates passes `check_docs.py` and `header_problem`. The templates already pass both today (check_docs.py:38 lists `docs/slices/_template/*.md` as live docs), so a template without the stage table or the decision-source column still passes. Row 2 checks only that seven stage names appear in order, not D1's four columns (produces, review = the matching 4.4 list, checks, exit) or the \"none, with a reason\" rule.",
      "failure_scenario": "The implementer adds seven stage names to AGENTS.md with empty or wrong review/check columns, and leaves the plan template without the stage table and the source column. Both tooling tests pass, and no review question asks about D1 or D11. Two approved decisions merge unproved.",
      "file": "docs/slices/poc-4-6-stage-rules/test_plan.md",
      "id": "S46-B3",
      "kind": "blocking",
      "line": 19,
      "problem": "S46-D1's content and S46-D11 have no effective proof. The review-based proof covers only S46-D2 to S46-D10, and the two tooling tests would pass a wrong implementation of D1 and D11."
    },
    {
      "evidence": "AGENTS.md, Independent review: \"Implementation review (step 4). The reviewer answers the questions in the test-plan template (... which wrong failure would still pass each new or changed test, whether a key, socket or secret now reaches a service outside its holders, and ... purpose comment and names)\". The 4.6 test plan replaces these with *Rules*, *Practicality* and *Names and headers*. Yet the slice adds two tooling tests (test_plan.md:19-20).",
      "failure_scenario": "The weak template test (S46-B3) reaches the implementation review. No question asks which wrong template would still pass it, so the reviewer answers the rules questions and the gap merges.",
      "file": "docs/slices/poc-4-6-stage-rules/test_plan.md",
      "id": "S46-B4",
      "kind": "blocking",
      "line": 41,
      "problem": "Contradiction with AGENTS.md: the implementation-review questions leave out the questions AGENTS.md requires. Those are which wrong failure would still pass each new or changed test, and whether a key, socket or secret reaches a non-holder."
    },
    {
      "evidence": "agentic-sdlc-poc/plan.md:325 (slice 4 row): \"how rule deviations are recorded; where the user's words live for the final review\". plan.md:36-37: \"one question in every final review: 'Which tracked document now says something this change made false?'\". The mapping table at :345 says \"handoff format and deviation records in slice 4\". The Goal table at :30 says the final review is \"against the user's recorded words first\". A grep for deviation, user's words and \"made false\" across docs/slices/poc-4-* finds nothing. The owner's words are in GitHub issues, which reviewers cannot read (AGENTS.md Start here: \"reviewers read the repository, not issues\").",
      "failure_scenario": "After slice 4 the final reviewer is told to judge against the owner's words, but they exist only as links to GitHub comments that the confined reviewer cannot open. A deviation from a rule has no place to be recorded. Intents D25/D35 of PR #26, which the approved mapping assigns to slice 4, land nowhere.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A1",
      "kind": "advisory",
      "line": 18,
      "problem": "[high] The plan claims to be \"the plan's original slice 4\" and to settle the carry-overs, but drops three items of the PoC plan's slice-4 row, and no other 4.x plan picks them up: (1) how rule deviations are recorded; (2) where the user's words live for the final review; (3) the final-review question \"Which tracked document now says something this change made false?\"."
    },
    {
      "evidence": "S46-D4: \"A correction to an upstream document reopens the reviews of the documents built on it, and the reopening is recorded in the attempt log as a new revision.\" AGENTS.md Review loop: \"A new revision keeps the count; only the user resets it\". None of 4.1\u20134.3 adds a reopen entry or a dependency between review units. The test plan proves D4 by quoting text only.",
      "failure_scenario": "During slice 5 a requirement is corrected after the test review finished at round 4. One author reopens and gets refused by round admission. Another treats a new commit as \"a new revision\" without any record. The rule is unenforceable, and nothing shows whether a reopening happened.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A2",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] S46-D4 cannot be built without asking the owner. It does not define which reviews are \"built on\" a document, who triggers the reopening, how a reopened unit counts against POC-D4's four rounds (including a unit already closed or merged), or what \"recorded in the attempt log as a new revision\" means. The launcher writes the log, and no 4.x plan changes it for this."
    },
    {
      "evidence": "plan.md:68-69: \"PR text is outside the repository. The handoff rule is proved by review.\" Reviewers read only the frozen copy (AGENTS.md: \"reviewers read the repository, not issues\"). The owner's complaint was that the PRs' lists were \"partly stale and untracked\", and an outdated merged PR body is exactly that failure.",
      "failure_scenario": "Slice 5 fixes an issue listed in slice 4's PR body. Nobody edits the merged PR #N, and no reviewer can see that it is stale. The owner meets the same stale lists again, while review-based proof reports the rule as \"stated\".",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A3",
      "kind": "advisory",
      "line": 44,
      "problem": "[high] S46-D9's \"PR lists each with its status and link and is updated when a later fix lands\" lives entirely outside the repository. No review can check it, and the plan admits it has no check. A simpler way within the owner's decision: keep the discovered-issue list (status and link) in a tracked file in the slice bundle and copy it into the PR body. A later fix then updates a tracked line that reviewers and `docs-check` can see."
    },
    {
      "evidence": "S46-D9: \"every discovered issue becomes an issue with a 'needed before' point, or a comment on the issue it belongs to\". AGENTS.md Few exceptions: \"one line in the review report is enough\" for out-of-model findings. Step 4: \"open a GitHub issue for work found but not done ... and lock its conversation right away\". 4.1's S41-D6 answers each finding fixed/deferred/declined, and only `deferred` needs an issue link.",
      "failure_scenario": "The author opens a public issue for every advisory, including fixed and declined ones. This floods the backlog and conflicts with 4.3's answer check. Or the author reads D9 narrowly and some items go untracked again. New issues may be left unlocked.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A4",
      "kind": "advisory",
      "line": 44,
      "problem": "[medium] S46-D9 is ambiguous and may contradict AGENTS.md's \"Few exceptions\" rule. It does not say whether every discovered issue becomes a GitHub issue, including findings fixed or declined in the same PR and out-of-model notes. It does not say where the \"needed before\" point lives (label, body, milestone). It also drops the existing close-out rule to lock the issue's conversation (POC-D16)."
    },
    {
      "evidence": "AGENTS.md Ask before growing: \"Every new check or process step states the failure it catches, what it costs and the simpler alternative that was considered\". 4.1\u20134.4 each fill this table. The open rounds cost USD 2\u20133 and 230\u2013443 s each (#33 comment), and 4.6 adds up to three more high-effort review units per slice.",
      "failure_scenario": "The owner approves the plan PR without seeing that every slice now carries up to five review units of up to four rounds each. The quota cost first shows up in slice 5.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A5",
      "kind": "advisory",
      "line": 93,
      "problem": "[high] \"Checks this slice adds: None that run as a gate\" understates the growth. The slice adds process steps: a requirements review stage, an architecture review stage, a final review with a second pass, reopened reviews, escalation, an issue per discovered issue and STATUS ordering. It also adds two tooling tests that run in CI under `make tooling-test`. AGENTS.md and POC-D6 require each new check or process step to state the failure it catches, its cost (quota per stage) and the simpler alternative."
    },
    {
      "evidence": "S44-D1 types: plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code, final review, handoff (8), against 7 stages. S44-D7: \"--stage <artifact type>\". PoC plan.md:31: handoff review = \"The user's approval (code owner)\". S46-D3 mentions only plan and implementation units per sub-issue.",
      "failure_scenario": "The implementer picks one test list for stage 4, so E2E-specific questions such as twins and exact outcomes never reach the tests review. Or they invent a handoff review the owner did not ask for.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A6",
      "kind": "advisory",
      "line": 36,
      "problem": "[medium] Mapping stages to 4.4's lists is underspecified. Stage 4 (tests first) has two lists (unit tests, E2E tests), but 4.4's `--stage` takes one. The handoff list exists, while the PoC Goal table says the handoff review is the owner's approval, so it is unclear who runs the handoff review. With several sub-issues (S46-D3) it is also unclear whether the final review is one per slice or one per sub-issue. The \"exit\" column and who approves stage 2/3 outputs are not defined."
    },
    {
      "evidence": "plan.md:99-101 names only steps 2 to 4. References that go stale after the rewrite: AGENTS.md:157 (\"return to step 1\"), :210 (\"Plan review (step 1)\"), :219 (\"Implementation review (step 4)\"), :261 (\"required in step 4\"); docs/STATUS.md:3; docs/test_spec.md:14; docs/slices/_template/test_plan.md:36 (\"slice workflow step 2\"). `docs-check` checks anchors, not \"step N\" prose.",
      "failure_scenario": "When grill-me is skipped under S46-D2, nothing asks which keys and secrets the slice touches. Live docs point to \"step 4\" in a workflow that no longer has numbered steps.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A7",
      "kind": "advisory",
      "line": 99,
      "problem": "[medium] The retirement section keeps only steps 2 to 4's rules. Step 1's rules are not listed: grill-me's assets question (which S46-D2 now lets a slice skip), environment-fact probes, POC-D15 authors working by base rules, approval by merge and implementing only from the merged plan. Step 3's retirement removal is not listed either. Renumbering also leaves stale references to steps 1, 2 and 4."
    },
    {
      "evidence": "Owner, 2026-11-08: \"Plan PR, then one final PR\" was about slice 4; S46-D3 credits \"owner, 2026-11-08 (this slice's run mode)\" for a general rule. The task requires \"every default must be easy for the owner to spot and confirm\".",
      "failure_scenario": "The owner approves the single plan PR thinking only two defaults need checking. A standing rule that any slice may bundle sub-issues and run without stopping enters AGENTS.md without the owner choosing it.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A8",
      "kind": "advisory",
      "line": 106,
      "problem": "[medium] Not all of the author's defaults are flagged for the owner. Several decisions credit the owner with author additions: D3 turns slice 4's run mode into a standing rule for every slice; D4's \"recorded in the attempt log as a new revision\"; D1's \"exit\" column; D9's \"or a comment on the issue it belongs to\"; D10's STATUS ordering; D5's \"(4.1's recheck inputs)\". Only D11 and D7's trigger are listed as defaults."
    },
    {
      "evidence": "S46-D8: \"each new test records its expected failure on the base code; security paths get targeted mutants\". AGENTS.md Mutation gate: \"score \u2265 70% (capiss and tool-b)\".",
      "failure_scenario": "Each author records expected failures in a different place, or not at all. Mutants are never run on the launcher's fail-closed paths (the DPL-010 class), and review-based proof still passes because the text exists.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A9",
      "kind": "advisory",
      "line": 43,
      "problem": "[medium] S46-D8 is not buildable as written. It does not say where the expected failure is recorded (test plan row, test docstring, PR), what counts as a \"security path\" in tooling scripts, or which tool makes \"targeted mutants\". `make unit-mutation` covers only capiss and tool-b, and most PoC changes are in `scripts/`."
    },
    {
      "evidence": "AGENTS.md Review loop: \"a finding still disputed after that goes to the user\". 4.1/4.3 key findings by attempt, with no ID that holds across rounds.",
      "failure_scenario": "The reviewer re-words a recurring blocker under a new ID each round, so the early-escalation trigger never fires and the unit runs to round 4.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A10",
      "kind": "advisory",
      "line": 42,
      "problem": "[medium] S46-D7's trigger, \"the same blocking finding\" in two rounds in a row, has no identity rule. Finding IDs are per report and change between rounds. The trigger also overlaps the existing rule that a rejection the reviewer re-raises goes to the user."
    },
    {
      "evidence": "S46-D1/D11 refer to \"the matching 4.4 list\". S41 in-scope: \"the slice-test-plan template's review questions\". S46-D11: \"The test-plan template points each stage's review at its 4.4 list\".",
      "failure_scenario": "4.6 is implemented first, with stage names that differ from 4.4's file names. Or 4.1 and 4.6 overwrite each other's template edits.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A11",
      "kind": "advisory",
      "line": 0,
      "problem": "[medium] Ordering between sub-issues is not stated. 4.6's AGENTS.md text and templates name 4.4's list files and `--stage` names, 4.1's `final` mode and 4.3's records. 4.1 and 4.6 both edit the same template section (the implementation-review questions). Only the 4.5/4.4 order is fixed (S45-D9)."
    },
    {
      "evidence": "diff:1190-1218 (PLACEHOLDER gains \"`.*\", MIN_CREDENTIAL_LENGTH = 20); diff:1232-1258 (other_tools_failed, report_path). docs/history/implementation_log.md is not in the diff, and none of the six plans lists these changes. AGENTS.md: \"a small fix still gets a plan (it may be a few lines)\".",
      "failure_scenario": "A short alphabetic credential, or a Markdown-quoted `Authorization: `Bearer \u2026`` line in evidence, is no longer flagged by `qa-evidence`. Nothing in the plan PR records that the gate was loosened or why, so the owner approves it without knowing. (Low practical risk: long tokens are still caught by the token-shape check.)",
      "file": "_review_inputs/change.diff",
      "id": "S46-A12",
      "kind": "advisory",
      "line": 1190,
      "problem": "[high] The plan branch narrows a gate and changes the launcher without any plan or implementation-log entry. `evidence_secrets.py` no longer flags credential lines whose value is under 20 characters without a digit, or starts with a backtick. The launcher changes `report_path` and stops failing on tool calls that returned errors. Under AGENTS.md every change, however small, needs a plan, a review and the close-out."
    },
    {
      "evidence": "AGENTS.md Documentation rules: \"One home per fact\". diff:35-40 already adds the ordered list.",
      "failure_scenario": "An issue's \"needed before\" point changes on GitHub and STATUS keeps the old order. Agents then follow the stale order.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A13",
      "kind": "advisory",
      "line": 45,
      "problem": "[low] S46-D10's STATUS \"needed before\" list duplicates priority facts that GitHub issues own (one home per fact). It goes stale whenever an issue opens or closes, and nothing checks it. It is also already written in this plan PR (STATUS.md diff), so success criterion 3 is met before implementation."
    }
  ],
  "verdict": "no"
}
```

#### Answers to plan/c1/r2/plan/2

| ID | Severity | Answer |
| --- | --- | --- |
| S46-B1 | blocking | fixed: S46-D5 uses 4.1's final mode (the owner's question, no list); 4.4 has no final-review list; 4.1 S41-D4's final mandate is the owner's question |
| S46-B2 | blocking | fixed: S46-D5 and 4.1 S41-D4 (the finding history is the other units' review records, which are in the final review's copy; its prompt names them; later rounds are rechecks); 4.1 test row "Mandates verbatim" |
| S46-B3 | blocking | fixed: test rows "Stage table" (seven stages, every cell filled, review cells naming real lists) and "Plan template" / "Test-plan template"; the review-based proof covers S46-D1 to S46-D12 |
| S46-B4 | blocking | fixed: the implementation-review questions now hold `AGENTS.md`'s required ones (wrong behaviour that would still pass a test; keys reaching a non-holder; names) |
| S46-A1 | high | fixed: S46-D11 (a "Rule deviations" section in the plan template), S46-D2 (the owner's words quoted in the plan), S46-D5 and 4.1 S41-D4 (the question on documents made false) |
| S46-A2 | high | fixed: S46-D4 (the next round of the downstream unit, counting against its limit; a closed unit reopens with its next round; beyond round 4 the owner decides; recorded in the plan's review notes; no launcher change) |
| S46-A3 | high | fixed: S46-D9 drops "updated when a later fix lands"; the issue is the home of its status, and the PR body is a snapshot |
| S46-A4 | medium | fixed: S46-D9 (only work found but not done; "Needed before" as the body's first line; locked; fixed or rejected findings and out-of-model notes are not issues) |
| S46-A5 | high | fixed: the POC-D6 table lists each new step with its failure, cost and simpler alternative |
| S46-A6 | medium | fixed: S46-D1 maps every stage (tests first takes two lists, 4.4 S44-D7 allows that; handoff is the owner's approval; one final unit per slice, S46-D3 and S46-D5) |
| S46-A7 | medium | fixed: S46-D12 lists the rules of all four steps and rewrites every step reference; S46-D2 keeps the assets question without a grill-me; test row "Step references" |
| S46-A8 | medium | fixed: Review notes list every default (D1's exit column, D3 as an option for later slices, D4, D7, D8, D9, D10, D11) |
| S46-A9 | medium | fixed: S46-D8 (failures recorded in the implementation log; a test for every fail-closed path; mutants where `make unit-mutation` exists) |
| S46-A10 | medium | fixed: S46-D7's trigger uses 4.1's `accounted` status `re-raised` for the same finding in two rounds in a row |
| S46-A11 | medium | fixed: the order of work is in the slice index; 4.6 is last and builds on 4.1's template text |
| S46-A12 | high | fixed: `docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md`, the implementation-log entry and DPL-011; the gate change is a decision concern for the owner in the plan PR |
| S46-A13 | low | rejected: the owner asked to prioritize open work before moving on and reads `docs/STATUS.md`; S46-D10 keeps the list there, refreshed at each close-out, with each issue as the home of its point |

## Round 3

### Attempt plan/c1/r3/plan/1

Commit `ebb1029`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-6-stage-rules/plan.md` `d68e4de97769`, `docs/slices/poc-4-6-stage-rules/test_plan.md` `3aa31a7e867f`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 3 of the plan review of slice 4.6 (stage rules, #43), a recheck of your earlier report (round 2, attempt 2). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it. (Slice 4.1 replaces this with an `accounted` field; until then this finding carries it.)
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## Your earlier report (round 2, attempt 2)

```json
{
  "findings": [
    {
      "evidence": "S46-D5: \"a fresh review with the open prompt 'What did everyone before you miss?', given all the evidence and no question list\". S44-D1 lists \"final review\" as an artifact type with its own list. S44-D5: the proof question and the CI-job question go into the \"(code, final review)\" lists. 4.4 test plan line 26: \"The requirements, tests and final-review lists contain the proof question\". S41-D1/D3: the launcher always writes the stage checklist section (if given), and `final` mode gets the S41-D2 mandate verbatim. S42-D4 puts the upstream question \"in every prompt\". The owner's decision comment says the checklist is the minimum for \"every review\", while the principle comment says \"no question list\". These plans resolve that tension in opposite directions.",
      "failure_scenario": "The implementer builds the final review from 4.6 (no `--stage`, a custom task text) or from 4.4/4.1 (`--mode final --stage final-review`). Either way one approved plan is broken. A rule in AGENTS.md (S46-D5) then contradicts the launcher's behaviour and 4.4's list. Because S46-D3 says implementation runs without stopping, nobody asks the owner which one they meant.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-B1",
      "kind": "blocking",
      "line": 40,
      "problem": "Contradiction between plans: S46-D5 says the final review gets \"no question list\", but 4.4 writes a final-review checklist and makes every stage list the minimum of every review. 4.1 also fixes the final-mode prompt to its own open-mandate text, which is not \"What did everyone before you miss?\"."
    },
    {
      "evidence": "S41-D4: a recheck prompt holds \"the reviewer's own earlier report ... and the author's answers\" and \"never puts in the review record\". It is refused \"without a completed earlier attempt by the same reviewer label\". The finding history is the findings and answers of all earlier review units (plan review, implementation review), which live in review records (4.3). The 4.6 test plan proves D5 only by review quoting rule text (test_plan.md:24). No row in the 4.1, 4.3 or 4.6 test plans covers a final-review second pass or the history input.",
      "failure_scenario": "The rule text says the second pass gets the history, so the review-based proof passes. At slice 5 the final reviewer's second pass runs as a 4.1 recheck: it sees only its own first-pass report and is refused the review records. Earlier blockers that were \"accepted as rejected\" or deferred are never shown to it. This is an approved carry-over (#33, PoC plan mapping D11\u2013D14) without a working mechanism or a test.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-B2",
      "kind": "blocking",
      "line": 40,
      "problem": "No plan builds or tests S46-D5's \"second pass gets the finding history through its prompt\", and the mechanism it names (4.1's recheck inputs) does not deliver a finding history."
    },
    {
      "evidence": "test_plan.md:24: \"quote, for each of S46-D2 to S46-D10, the AGENTS.md or template text\", so D1 and D11 are left out. Row 1 checks only that a bundle made from the templates passes `check_docs.py` and `header_problem`. The templates already pass both today (check_docs.py:38 lists `docs/slices/_template/*.md` as live docs), so a template without the stage table or the decision-source column still passes. Row 2 checks only that seven stage names appear in order, not D1's four columns (produces, review = the matching 4.4 list, checks, exit) or the \"none, with a reason\" rule.",
      "failure_scenario": "The implementer adds seven stage names to AGENTS.md with empty or wrong review/check columns, and leaves the plan template without the stage table and the source column. Both tooling tests pass, and no review question asks about D1 or D11. Two approved decisions merge unproved.",
      "file": "docs/slices/poc-4-6-stage-rules/test_plan.md",
      "id": "S46-B3",
      "kind": "blocking",
      "line": 19,
      "problem": "S46-D1's content and S46-D11 have no effective proof. The review-based proof covers only S46-D2 to S46-D10, and the two tooling tests would pass a wrong implementation of D1 and D11."
    },
    {
      "evidence": "AGENTS.md, Independent review: \"Implementation review (step 4). The reviewer answers the questions in the test-plan template (... which wrong failure would still pass each new or changed test, whether a key, socket or secret now reaches a service outside its holders, and ... purpose comment and names)\". The 4.6 test plan replaces these with *Rules*, *Practicality* and *Names and headers*. Yet the slice adds two tooling tests (test_plan.md:19-20).",
      "failure_scenario": "The weak template test (S46-B3) reaches the implementation review. No question asks which wrong template would still pass it, so the reviewer answers the rules questions and the gap merges.",
      "file": "docs/slices/poc-4-6-stage-rules/test_plan.md",
      "id": "S46-B4",
      "kind": "blocking",
      "line": 41,
      "problem": "Contradiction with AGENTS.md: the implementation-review questions leave out the questions AGENTS.md requires. Those are which wrong failure would still pass each new or changed test, and whether a key, socket or secret reaches a non-holder."
    },
    {
      "evidence": "agentic-sdlc-poc/plan.md:325 (slice 4 row): \"how rule deviations are recorded; where the user's words live for the final review\". plan.md:36-37: \"one question in every final review: 'Which tracked document now says something this change made false?'\". The mapping table at :345 says \"handoff format and deviation records in slice 4\". The Goal table at :30 says the final review is \"against the user's recorded words first\". A grep for deviation, user's words and \"made false\" across docs/slices/poc-4-* finds nothing. The owner's words are in GitHub issues, which reviewers cannot read (AGENTS.md Start here: \"reviewers read the repository, not issues\").",
      "failure_scenario": "After slice 4 the final reviewer is told to judge against the owner's words, but they exist only as links to GitHub comments that the confined reviewer cannot open. A deviation from a rule has no place to be recorded. Intents D25/D35 of PR #26, which the approved mapping assigns to slice 4, land nowhere.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A1",
      "kind": "advisory",
      "line": 18,
      "problem": "[high] The plan claims to be \"the plan's original slice 4\" and to settle the carry-overs, but drops three items of the PoC plan's slice-4 row, and no other 4.x plan picks them up: (1) how rule deviations are recorded; (2) where the user's words live for the final review; (3) the final-review question \"Which tracked document now says something this change made false?\"."
    },
    {
      "evidence": "S46-D4: \"A correction to an upstream document reopens the reviews of the documents built on it, and the reopening is recorded in the attempt log as a new revision.\" AGENTS.md Review loop: \"A new revision keeps the count; only the user resets it\". None of 4.1\u20134.3 adds a reopen entry or a dependency between review units. The test plan proves D4 by quoting text only.",
      "failure_scenario": "During slice 5 a requirement is corrected after the test review finished at round 4. One author reopens and gets refused by round admission. Another treats a new commit as \"a new revision\" without any record. The rule is unenforceable, and nothing shows whether a reopening happened.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A2",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] S46-D4 cannot be built without asking the owner. It does not define which reviews are \"built on\" a document, who triggers the reopening, how a reopened unit counts against POC-D4's four rounds (including a unit already closed or merged), or what \"recorded in the attempt log as a new revision\" means. The launcher writes the log, and no 4.x plan changes it for this."
    },
    {
      "evidence": "plan.md:68-69: \"PR text is outside the repository. The handoff rule is proved by review.\" Reviewers read only the frozen copy (AGENTS.md: \"reviewers read the repository, not issues\"). The owner's complaint was that the PRs' lists were \"partly stale and untracked\", and an outdated merged PR body is exactly that failure.",
      "failure_scenario": "Slice 5 fixes an issue listed in slice 4's PR body. Nobody edits the merged PR #N, and no reviewer can see that it is stale. The owner meets the same stale lists again, while review-based proof reports the rule as \"stated\".",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A3",
      "kind": "advisory",
      "line": 44,
      "problem": "[high] S46-D9's \"PR lists each with its status and link and is updated when a later fix lands\" lives entirely outside the repository. No review can check it, and the plan admits it has no check. A simpler way within the owner's decision: keep the discovered-issue list (status and link) in a tracked file in the slice bundle and copy it into the PR body. A later fix then updates a tracked line that reviewers and `docs-check` can see."
    },
    {
      "evidence": "S46-D9: \"every discovered issue becomes an issue with a 'needed before' point, or a comment on the issue it belongs to\". AGENTS.md Few exceptions: \"one line in the review report is enough\" for out-of-model findings. Step 4: \"open a GitHub issue for work found but not done ... and lock its conversation right away\". 4.1's S41-D6 answers each finding fixed/deferred/declined, and only `deferred` needs an issue link.",
      "failure_scenario": "The author opens a public issue for every advisory, including fixed and declined ones. This floods the backlog and conflicts with 4.3's answer check. Or the author reads D9 narrowly and some items go untracked again. New issues may be left unlocked.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A4",
      "kind": "advisory",
      "line": 44,
      "problem": "[medium] S46-D9 is ambiguous and may contradict AGENTS.md's \"Few exceptions\" rule. It does not say whether every discovered issue becomes a GitHub issue, including findings fixed or declined in the same PR and out-of-model notes. It does not say where the \"needed before\" point lives (label, body, milestone). It also drops the existing close-out rule to lock the issue's conversation (POC-D16)."
    },
    {
      "evidence": "AGENTS.md Ask before growing: \"Every new check or process step states the failure it catches, what it costs and the simpler alternative that was considered\". 4.1\u20134.4 each fill this table. The open rounds cost USD 2\u20133 and 230\u2013443 s each (#33 comment), and 4.6 adds up to three more high-effort review units per slice.",
      "failure_scenario": "The owner approves the plan PR without seeing that every slice now carries up to five review units of up to four rounds each. The quota cost first shows up in slice 5.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A5",
      "kind": "advisory",
      "line": 93,
      "problem": "[high] \"Checks this slice adds: None that run as a gate\" understates the growth. The slice adds process steps: a requirements review stage, an architecture review stage, a final review with a second pass, reopened reviews, escalation, an issue per discovered issue and STATUS ordering. It also adds two tooling tests that run in CI under `make tooling-test`. AGENTS.md and POC-D6 require each new check or process step to state the failure it catches, its cost (quota per stage) and the simpler alternative."
    },
    {
      "evidence": "S44-D1 types: plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code, final review, handoff (8), against 7 stages. S44-D7: \"--stage <artifact type>\". PoC plan.md:31: handoff review = \"The user's approval (code owner)\". S46-D3 mentions only plan and implementation units per sub-issue.",
      "failure_scenario": "The implementer picks one test list for stage 4, so E2E-specific questions such as twins and exact outcomes never reach the tests review. Or they invent a handoff review the owner did not ask for.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A6",
      "kind": "advisory",
      "line": 36,
      "problem": "[medium] Mapping stages to 4.4's lists is underspecified. Stage 4 (tests first) has two lists (unit tests, E2E tests), but 4.4's `--stage` takes one. The handoff list exists, while the PoC Goal table says the handoff review is the owner's approval, so it is unclear who runs the handoff review. With several sub-issues (S46-D3) it is also unclear whether the final review is one per slice or one per sub-issue. The \"exit\" column and who approves stage 2/3 outputs are not defined."
    },
    {
      "evidence": "plan.md:99-101 names only steps 2 to 4. References that go stale after the rewrite: AGENTS.md:157 (\"return to step 1\"), :210 (\"Plan review (step 1)\"), :219 (\"Implementation review (step 4)\"), :261 (\"required in step 4\"); docs/STATUS.md:3; docs/test_spec.md:14; docs/slices/_template/test_plan.md:36 (\"slice workflow step 2\"). `docs-check` checks anchors, not \"step N\" prose.",
      "failure_scenario": "When grill-me is skipped under S46-D2, nothing asks which keys and secrets the slice touches. Live docs point to \"step 4\" in a workflow that no longer has numbered steps.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A7",
      "kind": "advisory",
      "line": 99,
      "problem": "[medium] The retirement section keeps only steps 2 to 4's rules. Step 1's rules are not listed: grill-me's assets question (which S46-D2 now lets a slice skip), environment-fact probes, POC-D15 authors working by base rules, approval by merge and implementing only from the merged plan. Step 3's retirement removal is not listed either. Renumbering also leaves stale references to steps 1, 2 and 4."
    },
    {
      "evidence": "Owner, 2026-11-08: \"Plan PR, then one final PR\" was about slice 4; S46-D3 credits \"owner, 2026-11-08 (this slice's run mode)\" for a general rule. The task requires \"every default must be easy for the owner to spot and confirm\".",
      "failure_scenario": "The owner approves the single plan PR thinking only two defaults need checking. A standing rule that any slice may bundle sub-issues and run without stopping enters AGENTS.md without the owner choosing it.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A8",
      "kind": "advisory",
      "line": 106,
      "problem": "[medium] Not all of the author's defaults are flagged for the owner. Several decisions credit the owner with author additions: D3 turns slice 4's run mode into a standing rule for every slice; D4's \"recorded in the attempt log as a new revision\"; D1's \"exit\" column; D9's \"or a comment on the issue it belongs to\"; D10's STATUS ordering; D5's \"(4.1's recheck inputs)\". Only D11 and D7's trigger are listed as defaults."
    },
    {
      "evidence": "S46-D8: \"each new test records its expected failure on the base code; security paths get targeted mutants\". AGENTS.md Mutation gate: \"score \u2265 70% (capiss and tool-b)\".",
      "failure_scenario": "Each author records expected failures in a different place, or not at all. Mutants are never run on the launcher's fail-closed paths (the DPL-010 class), and review-based proof still passes because the text exists.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A9",
      "kind": "advisory",
      "line": 43,
      "problem": "[medium] S46-D8 is not buildable as written. It does not say where the expected failure is recorded (test plan row, test docstring, PR), what counts as a \"security path\" in tooling scripts, or which tool makes \"targeted mutants\". `make unit-mutation` covers only capiss and tool-b, and most PoC changes are in `scripts/`."
    },
    {
      "evidence": "AGENTS.md Review loop: \"a finding still disputed after that goes to the user\". 4.1/4.3 key findings by attempt, with no ID that holds across rounds.",
      "failure_scenario": "The reviewer re-words a recurring blocker under a new ID each round, so the early-escalation trigger never fires and the unit runs to round 4.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A10",
      "kind": "advisory",
      "line": 42,
      "problem": "[medium] S46-D7's trigger, \"the same blocking finding\" in two rounds in a row, has no identity rule. Finding IDs are per report and change between rounds. The trigger also overlaps the existing rule that a rejection the reviewer re-raises goes to the user."
    },
    {
      "evidence": "S46-D1/D11 refer to \"the matching 4.4 list\". S41 in-scope: \"the slice-test-plan template's review questions\". S46-D11: \"The test-plan template points each stage's review at its 4.4 list\".",
      "failure_scenario": "4.6 is implemented first, with stage names that differ from 4.4's file names. Or 4.1 and 4.6 overwrite each other's template edits.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A11",
      "kind": "advisory",
      "line": 0,
      "problem": "[medium] Ordering between sub-issues is not stated. 4.6's AGENTS.md text and templates name 4.4's list files and `--stage` names, 4.1's `final` mode and 4.3's records. 4.1 and 4.6 both edit the same template section (the implementation-review questions). Only the 4.5/4.4 order is fixed (S45-D9)."
    },
    {
      "evidence": "diff:1190-1218 (PLACEHOLDER gains \"`.*\", MIN_CREDENTIAL_LENGTH = 20); diff:1232-1258 (other_tools_failed, report_path). docs/history/implementation_log.md is not in the diff, and none of the six plans lists these changes. AGENTS.md: \"a small fix still gets a plan (it may be a few lines)\".",
      "failure_scenario": "A short alphabetic credential, or a Markdown-quoted `Authorization: `Bearer \u2026`` line in evidence, is no longer flagged by `qa-evidence`. Nothing in the plan PR records that the gate was loosened or why, so the owner approves it without knowing. (Low practical risk: long tokens are still caught by the token-shape check.)",
      "file": "_review_inputs/change.diff",
      "id": "S46-A12",
      "kind": "advisory",
      "line": 1190,
      "problem": "[high] The plan branch narrows a gate and changes the launcher without any plan or implementation-log entry. `evidence_secrets.py` no longer flags credential lines whose value is under 20 characters without a digit, or starts with a backtick. The launcher changes `report_path` and stops failing on tool calls that returned errors. Under AGENTS.md every change, however small, needs a plan, a review and the close-out."
    },
    {
      "evidence": "AGENTS.md Documentation rules: \"One home per fact\". diff:35-40 already adds the ordered list.",
      "failure_scenario": "An issue's \"needed before\" point changes on GitHub and STATUS keeps the old order. Agents then follow the stale order.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-A13",
      "kind": "advisory",
      "line": 45,
      "problem": "[low] S46-D10's STATUS \"needed before\" list duplicates priority facts that GitHub issues own (one home per fact). It goes stale whenever an issue opens or closes, and nothing checks it. It is also already written in this plan PR (STATUS.md diff), so success criterion 3 is met before implementation."
    }
  ],
  "verdict": "no"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| S46-B1 | blocking | fixed: S46-D5 uses 4.1's final mode (the owner's question, no list); 4.4 has no final-review list; 4.1 S41-D4's final mandate is the owner's question |
| S46-B2 | blocking | fixed: S46-D5 and 4.1 S41-D4 (the finding history is the other units' review records, which are in the final review's copy; its prompt names them; later rounds are rechecks); 4.1 test row "Mandates verbatim" |
| S46-B3 | blocking | fixed: test rows "Stage table" (seven stages, every cell filled, review cells naming real lists) and "Plan template" / "Test-plan template"; the review-based proof covers S46-D1 to S46-D12 |
| S46-B4 | blocking | fixed: the implementation-review questions now hold `AGENTS.md`'s required ones (wrong behaviour that would still pass a test; keys reaching a non-holder; names) |
| S46-A1 | high | fixed: S46-D11 (a "Rule deviations" section in the plan template), S46-D2 (the owner's words quoted in the plan), S46-D5 and 4.1 S41-D4 (the question on documents made false) |
| S46-A2 | high | fixed: S46-D4 (the next round of the downstream unit, counting against its limit; a closed unit reopens with its next round; beyond round 4 the owner decides; recorded in the plan's review notes; no launcher change) |
| S46-A3 | high | fixed: S46-D9 drops "updated when a later fix lands"; the issue is the home of its status, and the PR body is a snapshot |
| S46-A4 | medium | fixed: S46-D9 (only work found but not done; "Needed before" as the body's first line; locked; fixed or rejected findings and out-of-model notes are not issues) |
| S46-A5 | high | fixed: the POC-D6 table lists each new step with its failure, cost and simpler alternative |
| S46-A6 | medium | fixed: S46-D1 maps every stage (tests first takes two lists, 4.4 S44-D7 allows that; handoff is the owner's approval; one final unit per slice, S46-D3 and S46-D5) |
| S46-A7 | medium | fixed: S46-D12 lists the rules of all four steps and rewrites every step reference; S46-D2 keeps the assets question without a grill-me; test row "Step references" |
| S46-A8 | medium | fixed: Review notes list every default (D1's exit column, D3 as an option for later slices, D4, D7, D8, D9, D10, D11) |
| S46-A9 | medium | fixed: S46-D8 (failures recorded in the implementation log; a test for every fail-closed path; mutants where `make unit-mutation` exists) |
| S46-A10 | medium | fixed: S46-D7's trigger uses 4.1's `accounted` status `re-raised` for the same finding in two rounds in a row |
| S46-A11 | medium | fixed: the order of work is in the slice index; 4.6 is last and builds on 4.1's template text |
| S46-A12 | high | fixed: `docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md`, the implementation-log entry and DPL-011; the gate change is a decision concern for the owner in the plan PR |
| S46-A13 | low | rejected: the owner asked to prioritize open work before moving on and reads `docs/STATUS.md`; S46-D10 keeps the list there, refreshed at each close-out, with each issue as the home of its point |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "S46-B1: accepted \u2014 poc-4-6 plan.md (D1, D5), poc-4-4 plan.md (S44-D1, S44-D7, retirement), poc-4-1 plan.md (S41-D1, S41-D4)\nS46-B2: accepted \u2014 poc-4-6 plan.md (D5), poc-4-1 plan.md (S41-D3, S41-D4), poc-4-1 test_plan.md (row 'Mandates verbatim', 'Mode from the round')\nS46-B3: accepted \u2014 poc-4-6 test_plan.md (rows Stage table, Plan template, Test-plan template, Bundle, Step references; review-based proof D1\u2013D12)\nS46-B4: accepted \u2014 poc-4-6 test_plan.md (implementation-review questions 1, 2, 5)\nS46-A1: accepted \u2014 poc-4-6 plan.md (D2, D5, D11, Goal)\nS46-A2: accepted \u2014 poc-4-6 plan.md (D4)\nS46-A3: accepted \u2014 poc-4-6 plan.md (D9)\nS46-A4: accepted \u2014 poc-4-6 plan.md (D9)\nS46-A5: accepted \u2014 poc-4-6 plan.md (Checks this slice adds)\nS46-A6: accepted \u2014 poc-4-6 plan.md (D1, D3, D5), poc-4-4 plan.md (S44-D7)\nS46-A7: accepted \u2014 poc-4-6 plan.md (D2, D12, environment facts), poc-4-6 test_plan.md (Step references)\nS46-A8: accepted \u2014 poc-4-6 plan.md (Review notes)\nS46-A9: accepted \u2014 poc-4-6 plan.md (D8)\nS46-A10: accepted \u2014 poc-4-6 plan.md (D7), poc-4-1 plan.md (S41-D8)\nS46-A11: accepted \u2014 poc-4-6 plan.md (Order of work), docs/slices/README.md (agentic-sdlc-poc row)\nS46-A12: accepted \u2014 docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md, docs/history/implementation_log.md:12, docs/delivery_problem_log.md:368\nS46-A13: accepted (rejection) \u2014 poc-4-6 plan.md (D10)",
      "failure_scenario": "None; this finding only records which answers were checked.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    },
    {
      "evidence": "plan.md:47: \"The plan's review notes record each reopening.\" docs/slices/README.md:8: \"Once a slice is implemented its bundle is a frozen record\". AGENTS.md: implement only from the plan as merged.",
      "failure_scenario": "An author edits the merged plan.md to note a reopening, and a later reviewer cannot tell an approved decision from an implementation-time note. Or the author skips the note because the plan is frozen. Either way the low-cost record is unreliable.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-N1",
      "kind": "advisory",
      "line": 47,
      "problem": "[low] S46-D4 records each reopening in \"the plan's review notes\". During implementation that plan is already merged and approved, and once the slice is implemented it is a frozen record (docs/slices/README.md). So the record goes into the approved plan text that reviewers judge against. The review record of the reopened unit (4.3) would be the natural home."
    },
    {
      "evidence": "S41-D8: accounted = {item, status, note, opened} per answer. S41-D4's recheck mandate: \"accept or re-raise the finding\". It has no rule on ID reuse.",
      "failure_scenario": "Round 2 re-raises X under a new ID Y, and round 3 re-raises Y. Whether that counts as \"the same finding\" for escalation is a matter of interpretation. The worst case is a late escalation at round 4, which the existing rule still catches.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-N2",
      "kind": "advisory",
      "line": 50,
      "problem": "[low] S46-D7's trigger needs the same finding to be \"re-raised\" in two rounds in a row. Nothing in 4.1 says a re-raised finding keeps its earlier ID. So a chain across three reports still depends on the reviewer choosing to reuse the ID. This review prompt asks for that, but S41-D4/D8 do not state it."
    }
  ],
  "verdict": "yes"
}
```

#### Answers to plan/c1/r3/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| S46-N1 | low | fixed: docs/slices/poc-4-6-stage-rules/plan.md: S46-D4 records the reopening in the reopened unit's review record, not the merged plan |
| S46-N2 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-6-stage-rules/plan.md: S41-D8 says a re-raised finding keeps its ID, and S46-D7 cites it |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |

## Round 4

### Attempt plan/c1/r4/plan/1

Commit `a99d4f8`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-6-stage-rules/plan.md` `917a852cdf54`, `docs/slices/poc-4-6-stage-rules/test_plan.md` `8e6cd81b5e95`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 4 of the plan review of slice 4.6 (stage rules, #43), a recheck of your earlier report (round 3, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

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
      "evidence": "S46-B1: accepted \u2014 poc-4-6 plan.md (D1, D5), poc-4-4 plan.md (S44-D1, S44-D7, retirement), poc-4-1 plan.md (S41-D1, S41-D4)\nS46-B2: accepted \u2014 poc-4-6 plan.md (D5), poc-4-1 plan.md (S41-D3, S41-D4), poc-4-1 test_plan.md (row 'Mandates verbatim', 'Mode from the round')\nS46-B3: accepted \u2014 poc-4-6 test_plan.md (rows Stage table, Plan template, Test-plan template, Bundle, Step references; review-based proof D1\u2013D12)\nS46-B4: accepted \u2014 poc-4-6 test_plan.md (implementation-review questions 1, 2, 5)\nS46-A1: accepted \u2014 poc-4-6 plan.md (D2, D5, D11, Goal)\nS46-A2: accepted \u2014 poc-4-6 plan.md (D4)\nS46-A3: accepted \u2014 poc-4-6 plan.md (D9)\nS46-A4: accepted \u2014 poc-4-6 plan.md (D9)\nS46-A5: accepted \u2014 poc-4-6 plan.md (Checks this slice adds)\nS46-A6: accepted \u2014 poc-4-6 plan.md (D1, D3, D5), poc-4-4 plan.md (S44-D7)\nS46-A7: accepted \u2014 poc-4-6 plan.md (D2, D12, environment facts), poc-4-6 test_plan.md (Step references)\nS46-A8: accepted \u2014 poc-4-6 plan.md (Review notes)\nS46-A9: accepted \u2014 poc-4-6 plan.md (D8)\nS46-A10: accepted \u2014 poc-4-6 plan.md (D7), poc-4-1 plan.md (S41-D8)\nS46-A11: accepted \u2014 poc-4-6 plan.md (Order of work), docs/slices/README.md (agentic-sdlc-poc row)\nS46-A12: accepted \u2014 docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md, docs/history/implementation_log.md:12, docs/delivery_problem_log.md:368\nS46-A13: accepted (rejection) \u2014 poc-4-6 plan.md (D10)",
      "failure_scenario": "None; this finding only records which answers were checked.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    },
    {
      "evidence": "plan.md:47: \"The plan's review notes record each reopening.\" docs/slices/README.md:8: \"Once a slice is implemented its bundle is a frozen record\". AGENTS.md: implement only from the plan as merged.",
      "failure_scenario": "An author edits the merged plan.md to note a reopening, and a later reviewer cannot tell an approved decision from an implementation-time note. Or the author skips the note because the plan is frozen. Either way the low-cost record is unreliable.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-N1",
      "kind": "advisory",
      "line": 47,
      "problem": "[low] S46-D4 records each reopening in \"the plan's review notes\". During implementation that plan is already merged and approved, and once the slice is implemented it is a frozen record (docs/slices/README.md). So the record goes into the approved plan text that reviewers judge against. The review record of the reopened unit (4.3) would be the natural home."
    },
    {
      "evidence": "S41-D8: accounted = {item, status, note, opened} per answer. S41-D4's recheck mandate: \"accept or re-raise the finding\". It has no rule on ID reuse.",
      "failure_scenario": "Round 2 re-raises X under a new ID Y, and round 3 re-raises Y. Whether that counts as \"the same finding\" for escalation is a matter of interpretation. The worst case is a late escalation at round 4, which the existing rule still catches.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "S46-N2",
      "kind": "advisory",
      "line": 50,
      "problem": "[low] S46-D7's trigger needs the same finding to be \"re-raised\" in two rounds in a row. Nothing in 4.1 says a re-raised finding keeps its earlier ID. So a chain across three reports still depends on the reviewer choosing to reuse the ID. This review prompt asks for that, but S41-D4/D8 do not state it."
    }
  ],
  "verdict": "yes"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| S46-N1 | low | fixed: docs/slices/poc-4-6-stage-rules/plan.md: S46-D4 records the reopening in the reopened unit's review record, not the merged plan |
| S46-N2 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-6-stage-rules/plan.md: S41-D8 says a re-raised finding keeps its ID, and S46-D7 cites it |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "S46-N1: accepted \u2014 docs/slices/poc-4-6-stage-rules/plan.md (S46-D4, line 47: \"The reopened unit's review record notes the reopening and the corrected document.\")\nS46-N2: accepted \u2014 docs/slices/poc-4-1-review-prompts/plan.md (S41-D8, line 50: \"A re-raised finding keeps its ID\"), docs/slices/poc-4-6-stage-rules/plan.md (S46-D7, line 50, cites S41-D8)\nACCOUNTED: accepted (rejection) \u2014 no file; this is the stand-in until S41-D8's field exists",
      "failure_scenario": "None. This entry only records which answers were checked.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    },
    {
      "evidence": "plan.md:56: \"...the origin stage against the stage that found each finding (S41-D16); and the latest CI result of the PR's head commit.\" test_plan.md:23 lists verdicts, severity counts, owner answers, decision concerns, cannot-determine answers, disputed findings, rejected blocking/high findings and the origin table. It says nothing about CI. The Environment facts table has no probe of the CI API.",
      "failure_scenario": "The script prints a stale result, or 'unknown', when the API call fails, and no test catches it. The owner reads a brief that shows CI as green, or shows no CI line, while the head commit's checks failed or never ran. That is a false green in the document the owner reads to decide.",
      "file": "docs/slices/poc-4-6-stage-rules/test_plan.md",
      "id": "S46-N3",
      "kind": "advisory",
      "line": 23,
      "problem": "[medium] S46-D13 says the brief includes \"the latest CI result of the PR's head commit\". The \"Decision brief\" test row checks every other part of the brief but not this one. It also has no failure case for a CI result that cannot be read. Reading the result needs the GitHub API, which is outside the repository, and the plan names no probe or fallback for it."
    },
    {
      "evidence": "plan.md:57 (S46-D14); plan.md:76 (\"`.claude/skills/grill-me/` (moved in)\"); test_plan.md:24 (\"exists, starts with a purpose header\"); AGENTS.md Quality gates, `make lint` row (\"every added Markdown file with a `#` title and a paragraph\"); the Environment facts table (plan.md:92-96) has no row for the skill. The copy has no `.claude/` directory.",
      "failure_scenario": "The implementer puts a `#` title first so `make lint` passes, and the skill then stops loading, so discovery silently runs without grill-me. Or the implementer keeps the front matter, `make lint` fails, and the implementer invents an exception during implementation, outside the approved plan.",
      "file": "docs/slices/poc-4-6-stage-rules/test_plan.md",
      "id": "S46-N4",
      "kind": "advisory",
      "line": 24,
      "problem": "[medium] S46-D14 moves the grill-me skill to `.claude/skills/grill-me/SKILL.md`. The test row requires the file to start with a purpose header, and the lint gate requires every added Markdown file to start with a `#` title and a paragraph (coding rule 8). But a Claude Code SKILL.md has to start with YAML front matter (`---`, name, description), or the skill does not load. The plan does not say which rule gives way. It also has no environment-fact probe of where the skill lives today and in what format, although it is a fact outside the repository (the plan says \"moved in\")."
    },
    {
      "evidence": "poc-4-1 plan.md:58; poc-4-6 plan.md:44 (S46-D1), plan.md:56 (S46-D13).",
      "failure_scenario": "The brief's origin-against-found table either leaves out findings of the final unit or puts them under an invented label, so the measure of 'caught where they arise' is skewed. The impact is low.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "S46-N5",
      "kind": "advisory",
      "line": 58,
      "problem": "[low] S41-D16's `origin_stage` values (discovery, requirements, architecture, tests, implementation, unknown) do not match S46-D1's stage names ('architecture and interfaces', 'tests first'). S46-D13's brief sets `origin_stage` against 'the stage that found each finding', but no plan defines how the reviewing unit maps to one of those values. This matters most for the final review, which has no `origin_stage` value."
    }
  ],
  "verdict": "yes"
}
```

#### Answers to plan/c1/r4/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| S46-N3 | medium | fixed: docs/slices/poc-4-6-stage-rules/plan.md, docs/slices/poc-4-6-stage-rules/test_plan.md: S46-D13 reads the CI result from the public API and says so when it cannot be read or a job is running, never showing a pass; the "CI line of the brief" row tests both |
| S46-N4 | medium | fixed: docs/slices/poc-4-6-stage-rules/plan.md, docs/slices/poc-4-6-stage-rules/test_plan.md: S46-D14 keeps the skill's front matter, the lint gate's Markdown check skips a leading front-matter block and then requires the title and paragraph, and an environment fact records the skill's current form |
| S46-N5 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md: S41-D16 uses 4.6's stage names and counts the final unit as "final review" |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
