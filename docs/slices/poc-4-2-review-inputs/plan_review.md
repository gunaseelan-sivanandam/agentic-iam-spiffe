# Plan review — 4.2 (#39), review inputs and evidence

Record of the plan review of slice 4.2 (#39), review inputs and evidence in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

After the last round, the plan changed only by quoting the owner's words in its Source column (commit `a99d4f8`); it was not rechecked.

## Round 1

### Attempt plan/c1/r1/plan/1

Commit `dfc88e2`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-2-review-inputs/plan.md` `c4ec79cb8fb4`, `docs/slices/poc-4-2-review-inputs/test_plan.md` `c985d717f728`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 1 (the initial review), of slice 4.2 of the agentic-SDLC PoC: `docs/slices/poc-4-2-review-inputs/plan.md` and `test_plan.md` (GitHub issue #39). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#39)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** the reviewer gets the right inputs and evidence without the author choosing them.

**Decided** ([reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090), [evidence](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147), [empty-review rule](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672)):
- **Files under review come from the diff,** so the author cannot leave a changed file out. That is how DPL-005 slipped through.
- **The task names the upstream items** the change traces to: its requirement and architecture IDs (from `make qa-trace`) and the plan's decisions.
- **Every review asks** whether a problem originates upstream (a requirement, the architecture, the plan), and if so, in which document and section.
- **Evidence computed by tools,** never the author's conclusions:
  - coverage of new code;
  - requirements without a test (`qa-trace`);
  - changed files outside the review list;
  - CI results.

  The reviewer explains or flags every entry.
- **Keep the rule** that fails a review which opened none of its files (owner: "keep the rule"). The launcher's instructions tell the reviewer to open every file it is asked to review.
- **Simplification** ([R5-S1](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)): `diff_base` becomes required, because both callers always pass it.

**Done when:** the launcher computes the file list and the evidence, and names the upstream items; tooling tests cover each part.

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

Lost: another unit's report overwrote its file before the fix of the report path (DPL-011). The log keeps its SHA-256 `af8990d62ae7`.

## Round 2

### Attempt plan/c1/r2/plan/1

Commit `f070669`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-2-review-inputs/plan.md` `c4ec79cb8fb4`, `docs/slices/poc-4-2-review-inputs/test_plan.md` `c985d717f728`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
**Note on this round:** round 1 of this review unit completed with verdict "no", but its report was lost: a launcher bug made all six plan reviews write the same report file (fixed in commit f070669, which is in your copy). This round 2 is therefore a full review with the open mandate, not a recheck.

## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 2 (a full review; see the note above), of slice 4.2 of the agentic-SDLC PoC: `docs/slices/poc-4-2-review-inputs/plan.md` and `test_plan.md` (GitHub issue #39). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#39)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** the reviewer gets the right inputs and evidence without the author choosing them.

**Decided** ([reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090), [evidence](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147), [empty-review rule](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672)):
- **Files under review come from the diff,** so the author cannot leave a changed file out. That is how DPL-005 slipped through.
- **The task names the upstream items** the change traces to: its requirement and architecture IDs (from `make qa-trace`) and the plan's decisions.
- **Every review asks** whether a problem originates upstream (a requirement, the architecture, the plan), and if so, in which document and section.
- **Evidence computed by tools,** never the author's conclusions:
  - coverage of new code;
  - requirements without a test (`qa-trace`);
  - changed files outside the review list;
  - CI results.

  The reviewer explains or flags every entry.
- **Keep the rule** that fails a review which opened none of its files (owner: "keep the rule"). The launcher's instructions tell the reviewer to open every file it is asked to review.
- **Simplification** ([R5-S1](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)): `diff_base` becomes required, because both callers always pass it.

**Done when:** the launcher computes the file list and the evidence, and names the upstream items; tooling tests cover each part.

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

```json
{
  "findings": [
    {
      "evidence": "plan.md:32 'without the withheld files and files deleted by the change'; plan.md:22 threat model; plan.md:47; plan.md:36 item (c). test_plan.md:25 even pins 'A file the change deletes is not listed.' The exclusion comes from the existing path_hashes (run_independent_review.py:232-239), which refuses a path that is absent at the commit. That is an implementation constraint, not a decision with a reason.",
      "failure_scenario": "An honest-mistake change deletes a negative-control tooling test or a CI workflow step file, i.e. it weakens a check. The deletion is in change.diff but not on the list, and nothing makes the reviewer examine it. This is the same DPL-005 mechanism the slice exists to close. A fix: list deleted files in their own 'deleted by the change (examine in the diff)' part of the paths section, and test it.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B1",
      "kind": "blocking",
      "line": 32,
      "problem": "S42-D1 leaves files the change deletes off the list under review. This contradicts the plan's own threat model ('a changed file left out of the review'), its success criterion (line 47: 'a change that touches a file not given with --path lists that file') and S42-D5(c) ('empty after S42-D1, unless a file is withheld'). A deleted file is a changed file, and (c) is not empty when a file is deleted."
    },
    {
      "evidence": "Owner, #39: 'The task names the upstream items ... and the plan's decisions.' plan.md:34 'lists the slice bundles the change touches, so the prompt can name their plan.md'. AGENTS.md (approved): 'QA gate code carries no DD tags.' main() withholds the record and the log (run_independent_review.py:898-899). test_plan.md:27 tests only 'A change inside a slice bundle names that bundle's plan.md'.",
      "failure_scenario": "Slice 4.2's implementation review: the diff changes scripts/run_independent_review.py and tests/tools/*, but nothing visible in docs/slices/poc-4-2-review-inputs/. The upstream section says 'no upstream item found', so the reviewer is never pointed at plan.md's decisions S42-D1 to D8. The DPL-004-style plan-versus-code miss the owner wanted to prevent recurs, and the planned tests pass. A simple fix: derive the governing bundle from --record (docs/slices/<id>/\u2026), name its plan.md and its decision IDs, and add a test where the diff does not touch the bundle.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B2",
      "kind": "blocking",
      "line": 34,
      "problem": "The owner decided that 'the task names the upstream items the change traces to: its requirement and architecture IDs ... and the plan's decisions.' S42-D3 narrows the plan part to 'the slice bundles the change touches'. Implementation diffs usually don't touch their own bundle: the review record and attempt log are withheld, and close-out edits STATUS.md and docs/slices/README.md. So the governing plan is not named. The trace-model part is also empty for all QA tooling, because AGENTS.md says 'QA gate code carries no DD tags'. For slice 4's own implementation reviews, the prompt would say 'no upstream item found'. That is false, and it weakens an owner decision."
    },
    {
      "evidence": "Owner, #39 Decided: 'Evidence computed by tools ... The reviewer explains or flags every entry.' The #33 principle comment, item 3: 'Tools compute what is missing, and agents explain or fix every entry.' plan.md S42-D1 to D8 have no such decision. test_plan.md:29 checks only that the evidence is shown.",
      "failure_scenario": "The evidence lists uncovered new lines in a changed script, but the reviewer is never asked about them. The reviewer ignores them, as happened with DPL-010's untested refusal paths, and the review completes with no finding. This approved owner decision has no test.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B3",
      "kind": "blocking",
      "line": 36,
      "problem": "An owner decision is missing. Issue #39 says 'The reviewer explains or flags every entry' of the computed evidence. No decision, prompt text or test in this plan, or in 4.1 (whose evidence section has no instruction), tells the reviewer to account for each entry."
    },
    {
      "evidence": "plan.md:36 '(d) when the author passes --ci-run <run id>, the CI job conclusions of that run'. test_plan.md:29 checks only that conclusions are shown 'from a fake API response'. There is no check of the run's head_sha against the reviewed commit. AGENTS.md: 'A gate's result is its CI job's conclusion on GitHub'. The threat model lists 'stale evidence'.",
      "failure_scenario": "Round 2 runs on a fix commit, and the author reuses round 1's command line with the old --ci-run. The prompt shows every CI job green for the reviewed commit, while the new commit's lint job failed. The reviewer weighs a false green as tool evidence, and the planned tests pass. Fix: look up runs with head_sha=<commit> (no flag), or refuse/flag a run whose head_sha differs. Show 'no CI run for this commit' when there is none.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B4",
      "kind": "blocking",
      "line": 36,
      "problem": "S42-D5(d): the author chooses the CI evidence with --ci-run <run id>, and the launcher does not check that the run belongs to the reviewed commit. Stale evidence is part of the approved delivery threat model. The goal is evidence 'without the author choosing them'."
    },
    {
      "evidence": "plan.md:36 '(a) line and branch coverage of changed Python files under scripts/'; plan.md:62; AGENTS.md Quality gates: unit-diff-cov '\u2265 90% of changed lines in services/capability-issuer/ and services/tool-b/' only.",
      "failure_scenario": "A launcher change adds two untested refusal branches to a file that is 91% covered. The evidence says '91% lines', and the reviewer sees nothing to flag. Or slice 5 changes services/jira-tool code without tests, and no coverage evidence appears. Fix: report the uncovered changed lines and branches (diff against the merge-base) as a list.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A1",
      "kind": "advisory",
      "line": 36,
      "problem": "[high] The coverage evidence is narrower than the owner's 'coverage of new code', and the narrowing is not marked as a default. (1) It reports per-file line and branch coverage of changed scripts/ files. It does not list the uncovered changed lines or branches, so there are no 'entries' to explain, and a high file percentage can hide uncovered new paths (the DPL-010 pattern). (2) Services are excluded because they are 'already gated by make unit-trust', but diff coverage is gated only for capability-issuer and tool-b. Changes to jira-tool, jira-mcp or varambu code get no new-code evidence."
    },
    {
      "evidence": "plan.md:74 'Coverage evidence for such scripts reads \"not measurable\" until #44 is closed'; test_plan.md:41-42 pins the wording but not the condition.",
      "failure_scenario": "The author adds scripts/new_check.py with no tests. The evidence reads 'not measurable', and the reviewer treats it as the known #44 limitation and does not flag it. Fix: name the scripts that are 'not measurable' explicitly (e.g., test files that invoke them as a subprocess), or show 'no test imports or runs this file'. A simpler alternative is coverage's subprocess support (COVERAGE_PROCESS_START), which may close #44's case outright.",
      "file": "docs/slices/poc-4-2-review-inputs/test_plan.md",
      "id": "S42-R2-A2",
      "kind": "advisory",
      "line": 41,
      "problem": "[high] The plan doesn't say how the launcher decides that coverage is 'not measurable' rather than 0%. A script whose tests run it as a subprocess and a new script with no tests both measure 0% in-process. If the rule maps 0% to 'not measurable (#44)', then a wholly untested new script reads as excused. That is the soft wording for the exact miss (DPL-010) this slice targets."
    },
    {
      "evidence": "plan.md:81 'prompt, plus the evidence's SHA-256 in the start entry'; plan.md:82 scratch 'deleted after the round'; docs/slices/poc-4-3-review-records/plan.md:32 (S43-D1 writes the task prompt and the full-prompt hash only); run_independent_review.py:888.",
      "failure_scenario": "The owner asks why a review missed an uncovered path. Whether the evidence showed it can't be established, and invocation_from_entry reports full_prompt_sha256 mismatches for every slice-4 attempt. Fix: store the evidence text verbatim (scanned) as a file or record block, and have invocation_from_entry use it.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A3",
      "kind": "advisory",
      "line": 81,
      "problem": "[high] The evidence goes into the full prompt, but only its SHA-256 is kept. The scratch checkout is deleted, and 4.3's record keeps only the task prompt and the full prompt's hash. Nobody can later check what evidence a reviewer was given: not the owner, not the final review ('given all the evidence'), not a recheck. invocation_from_entry (run_independent_review.py:872-890) rebuilds the full prompt and compares full_prompt_sha256. With evidence that changes over time (CI conclusions after a re-run, coverage after an environment change), every rebuilt entry reports a mismatch. The plan addresses neither."
    },
    {
      "evidence": "docs/slices/poc-4-5-benchmark/plan.md:13 and S45-D6/D7; plan.md:39; run_review_benchmark.py:191, 327, 335-340.",
      "failure_scenario": "4.5's stage B runs 'the new setup' without evidence or upstream items, or with all-failed evidence for planted cases. S45-D7's decision rule then judges 4.2's contribution on runs that never included it. Fix: S42-D8 states which evidence items the runner computes per case kind, and what it shows when an item cannot exist.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A4",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] Cross-plan gap with 4.5. 4.5 measures 'inputs and evidence computed by tools (4.2)', but S42-D8 covers only the benchmark's paths. The plan doesn't say whether benchmark prompts get the upstream items and the computed evidence. CI results can't exist for planted or canary commits, and coverage and trace runs at old commits may fail. S42-D8's reason, 'cases stay comparable with stage A', is also wrong: the file list grows from the answer key's paths to the whole diff, so prompts differ from stage A anyway. Also, build_case_prompt (run_review_benchmark.py:335-340) builds ReviewInputs itself and bypasses resolve_inputs, so nothing in the plan routes it through the new computation."
    },
    {
      "evidence": "plan.md:34 lists only 'Implemented by: lines, DD tags in changed functions'. DPL-004 lived in docs/requirements.md. validate_traceability.py records DD locations as file:line of the tag (line 293), not function extents.",
      "failure_scenario": "A change adds REQ-X to docs/requirements.md and edits a harness case. The upstream section says 'no upstream item found', and the reviewer isn't pointed at REQ-X or its proof. Fix: also list the REQ and ARCH headings changed in the diff, and the test IDs whose entries changed. Define the DD rule as 'tags in changed files' unless function extents are worth the cost.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A5",
      "kind": "advisory",
      "line": 34,
      "problem": "[high] The link sources in S42-D3 miss the most direct upstream items. A change that edits docs/requirements.md or docs/architecture.md sections, trace/tests.yaml entries, E2E harness cases (\u2192 source_requirements) or unit tests (UT Covers DD \u2192 ARCH) is not linked. The prompt then says 'no upstream item found' plainly, which is false. 'DD tags in changed functions' also needs hunk-to-function mapping, which the plan doesn't define (whole file or function extent)."
    },
    {
      "evidence": "test_plan.md:30; plan.md:38; run_independent_review.py:265, 280, 295-298, 761, 887; owner #33 comment item 5: 'the optional diff_base branch in make_frozen_copy, build_prompt and invocation_from_entry can go'; AGENTS.md: 'mypy and bandit are not configured'.",
      "failure_scenario": "The implementer changes only the type hint, and all planned tests pass with the dead branches intact. Fix: extend D7 to all three functions, and test that every prompt carries the change.diff line and that has_diff no longer exists.",
      "file": "docs/slices/poc-4-2-review-inputs/test_plan.md",
      "id": "S42-R2-A6",
      "kind": "advisory",
      "line": 30,
      "problem": "[high] The S42-D7 test row isn't a test. 'make_frozen_copy without a diff base is a type error caught by the tests' call sites' \u2014 this repo has no mypy (AGENTS.md), and diff_base is already a positional parameter, so passing None still runs. An implementation that keeps the `if diff_base is None: return None` branch passes. The decision also covers less than R5-S1, which names make_frozen_copy, build_prompt and invocation_from_entry. The plan names only make_frozen_copy, so build_prompt's has_diff and invocation_from_entry's has_diff branch stay."
    },
    {
      "evidence": "run_independent_review.py:544-545 'if not set(stats[\"paths_read\"]) & set(review_paths)'; plan.md:32-33; poc-4-6 S46-D3 (several sub-issues per slice, one branch).",
      "failure_scenario": "A 4.2 implementation reviewer opens only docs/STATUS.md and reports nothing on the launcher, and the attempt completes. Cheap options: apply the rule to the --path hint files when given, and log the listed files that were not opened (paths_read already exists) as a deterministic entry for the record.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A7",
      "kind": "advisory",
      "line": 33,
      "problem": "[medium] A diff-derived list weakens the kept empty-review rule. classify() passes when the reviewer read any listed path. Once the list holds every changed file (STATUS.md, docs/slices/README.md, the other five slice-4 plans), opening one incidental file satisfies it. In slice 4's run mode, six units share one branch and --path 'never narrows', so every unit's review lists the whole slice-4 diff."
    },
    {
      "evidence": "plan.md:66-67; plan.md:37 (failure text includes the reason); reviewer_env() limits only the reviewer's env; test_plan.md has no test for the evidence's environment or paths. The implementation-review question 2 (test_plan.md:54) anticipates this but the plan doesn't decide it.",
      "failure_scenario": "A tooling test fails in the scratch checkout. The evidence shows a traceback with /home/<user>/\u2026 paths, and a reviewer quotes it in a finding that is written into a committed review record. Fix: run the evidence commands with a minimal env (as reviewer_env) and relative paths, strip the scratch root, and add a test that no absolute path or HOME value appears in the prompt.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A8",
      "kind": "advisory",
      "line": 67,
      "problem": "[medium] 'Nothing from the author's environment enters the prompt' is claimed but neither specified nor tested. The evidence commands (pytest with coverage, validate_traceability, the CI call) run with the author's full environment. Failure reasons ('failed: <command>: <reason>') and coverage output naturally carry absolute paths (the scratch dir, the user's home and site-packages, the account name). The plan also doesn't say how the CI call avoids a token: if it is implemented with `gh api`, as AGENTS.md uses elsewhere, the agent's token is sent. Reviewer reports that quote evidence are published, and the publication check knows secret shapes, not paths."
    },
    {
      "evidence": "Owner, #39: 'requirements without a test (qa-trace)'; plan.md:36 (b); AGENTS.md Quality gates: qa-trace PR mode fails on added gaps.",
      "failure_scenario": "A change edits code for a requirement that has been a known gap for months. The evidence shows 'no new gaps', and the reviewer isn't told that the requirement the change touches is unproved. Fix: list every gap among the change's upstream items, with new and accepted gaps marked.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A9",
      "kind": "advisory",
      "line": 36,
      "problem": "[medium] S42-D5(b) narrows the owner's 'requirements without a test (qa-trace)' to 'gaps that the change adds against the base', without marking this as a default. New gaps already fail the CI qa-trace gate unless accepted_gaps lists them, so the item mostly repeats CI. It also hides the useful case: a requirement the change edits or implements that already had no proof."
    },
    {
      "evidence": "docs/slices/poc-4-1-review-prompts/plan.md:37 (S41-D1) and test_plan.md:26; poc-4-2 plan.md:15-16; test_plan.md:27-28.",
      "failure_scenario": "4.1 and 4.2 are implemented in sequence on one branch, and 4.2 adds an 'Upstream items' section. Either 4.1's order test is edited after the fact, or the implementer guesses a place. Neither was approved.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A10",
      "kind": "advisory",
      "line": 15,
      "problem": "[medium] The plan doesn't say where the upstream items and the upstream question go in 4.1's fixed section order (role, mandate, rules, checklist, evidence, paths, task, output). Line 16 puts only the four evidence items into 4.1's evidence section, and test_plan.md:27 implies a separate section ('instead of an empty section'). A new section breaks 4.1's exact-order test. The plan also doesn't state that 4.2 is built after 4.1, which it depends on."
    },
    {
      "evidence": "plan.md:33; docs/slices/poc-4-1-review-prompts/plan.md:39 (S41-D3 bounded mandate).",
      "failure_scenario": "A recheck reviewer either spends the budget reopening the whole slice diff or ignores one instruction. Either way the record shows a prompt that contradicts itself. Fix: in recheck mode, require opening the files the answers concern.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A11",
      "kind": "advisory",
      "line": 33,
      "problem": "[medium] S42-D2 puts 'open every file under review' into every prompt's paths section, recheck mode included. 4.1's recheck mandate bounds a recheck to 'the code and test it concerns'. Combined with a full-diff list, a recheck prompt gives two conflicting instructions."
    },
    {
      "evidence": "plan.md:37; plan.md:81.",
      "failure_scenario": "A red tooling test turns the whole coverage item into 'failed: pytest \u2026: exit 1'. The reviewer loses both the coverage and the names of the failing tests, and the owner can't see in the log which reviews had no evidence.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A12",
      "kind": "advisory",
      "line": 37,
      "problem": "[medium] S42-D6 doesn't say how a pytest run that executes but has failing tests is shown: as 'failed' (coverage dropped) or as coverage plus the failed tests. It also doesn't say whether evidence failures are logged per item. The start entry holds only the evidence hash, so an attempt where all evidence failed looks the same in the log as a fully evidenced one."
    },
    {
      "evidence": "plan.md:36 '(c) ... (empty after S42-D1, unless a file is withheld)'; run_independent_review.py:473 paths_read.",
      "failure_scenario": "The item adds code, a test and prompt text that never shows anything useful, and the unopened listed files stay unreported.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-S1",
      "kind": "simpler_alternative",
      "line": 36,
      "problem": "S42-D5(c) ('changed files the review list leaves out') is empty by construction after S42-D1, except for the withheld record and log, which would appear in every review as noise. Drop it, or replace it with the deterministic list the owner's principle actually needs: the listed files the reviewer did not open, from the paths_read the launcher already logs."
    },
    {
      "evidence": "docs/delivery_problem_log.md:304-312; #33 comment 'Weak spots' item 2.",
      "failure_scenario": "A reader misattributes the cause, and a later DPL test (4.4's S44-D9 mapping) tests the wrong question against DPL-010.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A13",
      "kind": "advisory",
      "line": 11,
      "problem": "[low] The goal says DPL-010 slipped through partly because 'nothing asked where a problem started'. DPL-010 is about closed questions and rechecks that took the author's word. The missing upstream question is the #33 comment's lesson from DPL-004. The environment-fact probes (lines 73-75) give no date or commit, unlike the other plans."
    }
  ],
  "verdict": "no"
}
```

#### Answers to plan/c1/r2/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| S42-R2-B1 | blocking | fixed: S42-D1 lists deleted files in their own part ("deleted by the change: examine in `change.diff`"); test row "File list" |
| S42-R2-B2 | blocking | fixed: S42-D3(a) always names the governing plan, the bundle of `--record`, and its decision IDs; test row "Governing plan" (a change that touches no file of its bundle) |
| S42-R2-B3 | blocking | fixed: S42-D6 (every evidence entry appears in `accounted` as `explained` or `flagged`; a report that leaves one out fails); test row "Accounted entries" |
| S42-R2-B4 | blocking | fixed: S42-D5(c) reads the runs whose head is the reviewed commit, or says "no CI run for this commit"; `--ci-run` is gone; test row "CI results" |
| S42-R2-A1 | high | fixed: S42-D5(a) lists the uncovered changed lines and branches per file; each changed `services/` file names its coverage gate or "no coverage gate"; test row "Uncovered lines" |
| S42-R2-A2 | high | fixed: the "not measurable" label is gone; a fixed note says a script run as a subprocess shows as uncovered (#44), and its lines are listed like any other, for the reviewer to account for |
| S42-R2-A3 | high | fixed: S42-D9 (the evidence is kept verbatim in the record, 4.3 S43-D1, and its hash in the start entry); test row "Evidence hash" |
| S42-R2-A4 | high | fixed: S42-D11 says what the benchmark gets (paths as hints, upstream items, no computed evidence) and why; 4.5's goal and out-of-scope say so |
| S42-R2-A5 | high | fixed: S42-D3(c) takes `DD` tags anywhere in a changed file; S42-D3(d) adds changed `REQ` and `ARCH` headings and changed `trace/tests.yaml` entries; test row "Upstream items" |
| S42-R2-A6 | high | fixed: S42-D10 covers `make_frozen_copy`, `build_prompt` and `invocation_from_entry`, keyword-only without a default; test row "Required diff base" expects `TypeError` and the `change.diff` line in every prompt |
| S42-R2-A7 | medium | fixed: S42-D2 (the empty-review rule applies to the `--path` files when given; unopened listed files go into `paths_not_read` and the record) |
| S42-R2-A8 | medium | fixed: S42-D8 (minimal environment, relative paths, no token, refusal on the author's HOME path or the scratch root); test row "Clean environment" |
| S42-R2-A9 | medium | fixed: S42-D5(b) lists every gap among the upstream items, marked new, existing or accepted |
| S42-R2-A10 | medium | fixed: 4.1 S41-D1 gives the upstream section its place (after the checklist, before the evidence); the order of work is in the slice index |
| S42-R2-A11 | medium | fixed: S42-D2 says a recheck opens the answered files first, matching 4.1's recheck mandate |
| S42-R2-A12 | medium | fixed: S42-D7 (failing tests shown with coverage and their names; each item's status in the start entry) |
| S42-R2-S1 | low | fixed: adopted; the item is dropped (Retirement), and unopened files are shown by S42-D2 |
| S42-R2-A13 | low | fixed: the goal names DPL-010's rechecks and DPL-004 for the upstream question; the probes carry dates and commits |

## Round 3

### Attempt plan/c1/r3/plan/1

Commit `ebb1029`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-2-review-inputs/plan.md` `de88bc50d526`, `docs/slices/poc-4-2-review-inputs/test_plan.md` `a1b77356fd19`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 3 of the plan review of slice 4.2 (review inputs and evidence, #39), a recheck of your earlier report (round 2, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it. (Slice 4.1 replaces this with an `accounted` field; until then this finding carries it.)
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## Your earlier report (round 2, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "plan.md:32 'without the withheld files and files deleted by the change'; plan.md:22 threat model; plan.md:47; plan.md:36 item (c). test_plan.md:25 even pins 'A file the change deletes is not listed.' The exclusion comes from the existing path_hashes (run_independent_review.py:232-239), which refuses a path that is absent at the commit. That is an implementation constraint, not a decision with a reason.",
      "failure_scenario": "An honest-mistake change deletes a negative-control tooling test or a CI workflow step file, i.e. it weakens a check. The deletion is in change.diff but not on the list, and nothing makes the reviewer examine it. This is the same DPL-005 mechanism the slice exists to close. A fix: list deleted files in their own 'deleted by the change (examine in the diff)' part of the paths section, and test it.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B1",
      "kind": "blocking",
      "line": 32,
      "problem": "S42-D1 leaves files the change deletes off the list under review. This contradicts the plan's own threat model ('a changed file left out of the review'), its success criterion (line 47: 'a change that touches a file not given with --path lists that file') and S42-D5(c) ('empty after S42-D1, unless a file is withheld'). A deleted file is a changed file, and (c) is not empty when a file is deleted."
    },
    {
      "evidence": "Owner, #39: 'The task names the upstream items ... and the plan's decisions.' plan.md:34 'lists the slice bundles the change touches, so the prompt can name their plan.md'. AGENTS.md (approved): 'QA gate code carries no DD tags.' main() withholds the record and the log (run_independent_review.py:898-899). test_plan.md:27 tests only 'A change inside a slice bundle names that bundle's plan.md'.",
      "failure_scenario": "Slice 4.2's implementation review: the diff changes scripts/run_independent_review.py and tests/tools/*, but nothing visible in docs/slices/poc-4-2-review-inputs/. The upstream section says 'no upstream item found', so the reviewer is never pointed at plan.md's decisions S42-D1 to D8. The DPL-004-style plan-versus-code miss the owner wanted to prevent recurs, and the planned tests pass. A simple fix: derive the governing bundle from --record (docs/slices/<id>/\u2026), name its plan.md and its decision IDs, and add a test where the diff does not touch the bundle.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B2",
      "kind": "blocking",
      "line": 34,
      "problem": "The owner decided that 'the task names the upstream items the change traces to: its requirement and architecture IDs ... and the plan's decisions.' S42-D3 narrows the plan part to 'the slice bundles the change touches'. Implementation diffs usually don't touch their own bundle: the review record and attempt log are withheld, and close-out edits STATUS.md and docs/slices/README.md. So the governing plan is not named. The trace-model part is also empty for all QA tooling, because AGENTS.md says 'QA gate code carries no DD tags'. For slice 4's own implementation reviews, the prompt would say 'no upstream item found'. That is false, and it weakens an owner decision."
    },
    {
      "evidence": "Owner, #39 Decided: 'Evidence computed by tools ... The reviewer explains or flags every entry.' The #33 principle comment, item 3: 'Tools compute what is missing, and agents explain or fix every entry.' plan.md S42-D1 to D8 have no such decision. test_plan.md:29 checks only that the evidence is shown.",
      "failure_scenario": "The evidence lists uncovered new lines in a changed script, but the reviewer is never asked about them. The reviewer ignores them, as happened with DPL-010's untested refusal paths, and the review completes with no finding. This approved owner decision has no test.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B3",
      "kind": "blocking",
      "line": 36,
      "problem": "An owner decision is missing. Issue #39 says 'The reviewer explains or flags every entry' of the computed evidence. No decision, prompt text or test in this plan, or in 4.1 (whose evidence section has no instruction), tells the reviewer to account for each entry."
    },
    {
      "evidence": "plan.md:36 '(d) when the author passes --ci-run <run id>, the CI job conclusions of that run'. test_plan.md:29 checks only that conclusions are shown 'from a fake API response'. There is no check of the run's head_sha against the reviewed commit. AGENTS.md: 'A gate's result is its CI job's conclusion on GitHub'. The threat model lists 'stale evidence'.",
      "failure_scenario": "Round 2 runs on a fix commit, and the author reuses round 1's command line with the old --ci-run. The prompt shows every CI job green for the reviewed commit, while the new commit's lint job failed. The reviewer weighs a false green as tool evidence, and the planned tests pass. Fix: look up runs with head_sha=<commit> (no flag), or refuse/flag a run whose head_sha differs. Show 'no CI run for this commit' when there is none.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-B4",
      "kind": "blocking",
      "line": 36,
      "problem": "S42-D5(d): the author chooses the CI evidence with --ci-run <run id>, and the launcher does not check that the run belongs to the reviewed commit. Stale evidence is part of the approved delivery threat model. The goal is evidence 'without the author choosing them'."
    },
    {
      "evidence": "plan.md:36 '(a) line and branch coverage of changed Python files under scripts/'; plan.md:62; AGENTS.md Quality gates: unit-diff-cov '\u2265 90% of changed lines in services/capability-issuer/ and services/tool-b/' only.",
      "failure_scenario": "A launcher change adds two untested refusal branches to a file that is 91% covered. The evidence says '91% lines', and the reviewer sees nothing to flag. Or slice 5 changes services/jira-tool code without tests, and no coverage evidence appears. Fix: report the uncovered changed lines and branches (diff against the merge-base) as a list.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A1",
      "kind": "advisory",
      "line": 36,
      "problem": "[high] The coverage evidence is narrower than the owner's 'coverage of new code', and the narrowing is not marked as a default. (1) It reports per-file line and branch coverage of changed scripts/ files. It does not list the uncovered changed lines or branches, so there are no 'entries' to explain, and a high file percentage can hide uncovered new paths (the DPL-010 pattern). (2) Services are excluded because they are 'already gated by make unit-trust', but diff coverage is gated only for capability-issuer and tool-b. Changes to jira-tool, jira-mcp or varambu code get no new-code evidence."
    },
    {
      "evidence": "plan.md:74 'Coverage evidence for such scripts reads \"not measurable\" until #44 is closed'; test_plan.md:41-42 pins the wording but not the condition.",
      "failure_scenario": "The author adds scripts/new_check.py with no tests. The evidence reads 'not measurable', and the reviewer treats it as the known #44 limitation and does not flag it. Fix: name the scripts that are 'not measurable' explicitly (e.g., test files that invoke them as a subprocess), or show 'no test imports or runs this file'. A simpler alternative is coverage's subprocess support (COVERAGE_PROCESS_START), which may close #44's case outright.",
      "file": "docs/slices/poc-4-2-review-inputs/test_plan.md",
      "id": "S42-R2-A2",
      "kind": "advisory",
      "line": 41,
      "problem": "[high] The plan doesn't say how the launcher decides that coverage is 'not measurable' rather than 0%. A script whose tests run it as a subprocess and a new script with no tests both measure 0% in-process. If the rule maps 0% to 'not measurable (#44)', then a wholly untested new script reads as excused. That is the soft wording for the exact miss (DPL-010) this slice targets."
    },
    {
      "evidence": "plan.md:81 'prompt, plus the evidence's SHA-256 in the start entry'; plan.md:82 scratch 'deleted after the round'; docs/slices/poc-4-3-review-records/plan.md:32 (S43-D1 writes the task prompt and the full-prompt hash only); run_independent_review.py:888.",
      "failure_scenario": "The owner asks why a review missed an uncovered path. Whether the evidence showed it can't be established, and invocation_from_entry reports full_prompt_sha256 mismatches for every slice-4 attempt. Fix: store the evidence text verbatim (scanned) as a file or record block, and have invocation_from_entry use it.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A3",
      "kind": "advisory",
      "line": 81,
      "problem": "[high] The evidence goes into the full prompt, but only its SHA-256 is kept. The scratch checkout is deleted, and 4.3's record keeps only the task prompt and the full prompt's hash. Nobody can later check what evidence a reviewer was given: not the owner, not the final review ('given all the evidence'), not a recheck. invocation_from_entry (run_independent_review.py:872-890) rebuilds the full prompt and compares full_prompt_sha256. With evidence that changes over time (CI conclusions after a re-run, coverage after an environment change), every rebuilt entry reports a mismatch. The plan addresses neither."
    },
    {
      "evidence": "docs/slices/poc-4-5-benchmark/plan.md:13 and S45-D6/D7; plan.md:39; run_review_benchmark.py:191, 327, 335-340.",
      "failure_scenario": "4.5's stage B runs 'the new setup' without evidence or upstream items, or with all-failed evidence for planted cases. S45-D7's decision rule then judges 4.2's contribution on runs that never included it. Fix: S42-D8 states which evidence items the runner computes per case kind, and what it shows when an item cannot exist.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A4",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] Cross-plan gap with 4.5. 4.5 measures 'inputs and evidence computed by tools (4.2)', but S42-D8 covers only the benchmark's paths. The plan doesn't say whether benchmark prompts get the upstream items and the computed evidence. CI results can't exist for planted or canary commits, and coverage and trace runs at old commits may fail. S42-D8's reason, 'cases stay comparable with stage A', is also wrong: the file list grows from the answer key's paths to the whole diff, so prompts differ from stage A anyway. Also, build_case_prompt (run_review_benchmark.py:335-340) builds ReviewInputs itself and bypasses resolve_inputs, so nothing in the plan routes it through the new computation."
    },
    {
      "evidence": "plan.md:34 lists only 'Implemented by: lines, DD tags in changed functions'. DPL-004 lived in docs/requirements.md. validate_traceability.py records DD locations as file:line of the tag (line 293), not function extents.",
      "failure_scenario": "A change adds REQ-X to docs/requirements.md and edits a harness case. The upstream section says 'no upstream item found', and the reviewer isn't pointed at REQ-X or its proof. Fix: also list the REQ and ARCH headings changed in the diff, and the test IDs whose entries changed. Define the DD rule as 'tags in changed files' unless function extents are worth the cost.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A5",
      "kind": "advisory",
      "line": 34,
      "problem": "[high] The link sources in S42-D3 miss the most direct upstream items. A change that edits docs/requirements.md or docs/architecture.md sections, trace/tests.yaml entries, E2E harness cases (\u2192 source_requirements) or unit tests (UT Covers DD \u2192 ARCH) is not linked. The prompt then says 'no upstream item found' plainly, which is false. 'DD tags in changed functions' also needs hunk-to-function mapping, which the plan doesn't define (whole file or function extent)."
    },
    {
      "evidence": "test_plan.md:30; plan.md:38; run_independent_review.py:265, 280, 295-298, 761, 887; owner #33 comment item 5: 'the optional diff_base branch in make_frozen_copy, build_prompt and invocation_from_entry can go'; AGENTS.md: 'mypy and bandit are not configured'.",
      "failure_scenario": "The implementer changes only the type hint, and all planned tests pass with the dead branches intact. Fix: extend D7 to all three functions, and test that every prompt carries the change.diff line and that has_diff no longer exists.",
      "file": "docs/slices/poc-4-2-review-inputs/test_plan.md",
      "id": "S42-R2-A6",
      "kind": "advisory",
      "line": 30,
      "problem": "[high] The S42-D7 test row isn't a test. 'make_frozen_copy without a diff base is a type error caught by the tests' call sites' \u2014 this repo has no mypy (AGENTS.md), and diff_base is already a positional parameter, so passing None still runs. An implementation that keeps the `if diff_base is None: return None` branch passes. The decision also covers less than R5-S1, which names make_frozen_copy, build_prompt and invocation_from_entry. The plan names only make_frozen_copy, so build_prompt's has_diff and invocation_from_entry's has_diff branch stay."
    },
    {
      "evidence": "run_independent_review.py:544-545 'if not set(stats[\"paths_read\"]) & set(review_paths)'; plan.md:32-33; poc-4-6 S46-D3 (several sub-issues per slice, one branch).",
      "failure_scenario": "A 4.2 implementation reviewer opens only docs/STATUS.md and reports nothing on the launcher, and the attempt completes. Cheap options: apply the rule to the --path hint files when given, and log the listed files that were not opened (paths_read already exists) as a deterministic entry for the record.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A7",
      "kind": "advisory",
      "line": 33,
      "problem": "[medium] A diff-derived list weakens the kept empty-review rule. classify() passes when the reviewer read any listed path. Once the list holds every changed file (STATUS.md, docs/slices/README.md, the other five slice-4 plans), opening one incidental file satisfies it. In slice 4's run mode, six units share one branch and --path 'never narrows', so every unit's review lists the whole slice-4 diff."
    },
    {
      "evidence": "plan.md:66-67; plan.md:37 (failure text includes the reason); reviewer_env() limits only the reviewer's env; test_plan.md has no test for the evidence's environment or paths. The implementation-review question 2 (test_plan.md:54) anticipates this but the plan doesn't decide it.",
      "failure_scenario": "A tooling test fails in the scratch checkout. The evidence shows a traceback with /home/<user>/\u2026 paths, and a reviewer quotes it in a finding that is written into a committed review record. Fix: run the evidence commands with a minimal env (as reviewer_env) and relative paths, strip the scratch root, and add a test that no absolute path or HOME value appears in the prompt.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A8",
      "kind": "advisory",
      "line": 67,
      "problem": "[medium] 'Nothing from the author's environment enters the prompt' is claimed but neither specified nor tested. The evidence commands (pytest with coverage, validate_traceability, the CI call) run with the author's full environment. Failure reasons ('failed: <command>: <reason>') and coverage output naturally carry absolute paths (the scratch dir, the user's home and site-packages, the account name). The plan also doesn't say how the CI call avoids a token: if it is implemented with `gh api`, as AGENTS.md uses elsewhere, the agent's token is sent. Reviewer reports that quote evidence are published, and the publication check knows secret shapes, not paths."
    },
    {
      "evidence": "Owner, #39: 'requirements without a test (qa-trace)'; plan.md:36 (b); AGENTS.md Quality gates: qa-trace PR mode fails on added gaps.",
      "failure_scenario": "A change edits code for a requirement that has been a known gap for months. The evidence shows 'no new gaps', and the reviewer isn't told that the requirement the change touches is unproved. Fix: list every gap among the change's upstream items, with new and accepted gaps marked.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A9",
      "kind": "advisory",
      "line": 36,
      "problem": "[medium] S42-D5(b) narrows the owner's 'requirements without a test (qa-trace)' to 'gaps that the change adds against the base', without marking this as a default. New gaps already fail the CI qa-trace gate unless accepted_gaps lists them, so the item mostly repeats CI. It also hides the useful case: a requirement the change edits or implements that already had no proof."
    },
    {
      "evidence": "docs/slices/poc-4-1-review-prompts/plan.md:37 (S41-D1) and test_plan.md:26; poc-4-2 plan.md:15-16; test_plan.md:27-28.",
      "failure_scenario": "4.1 and 4.2 are implemented in sequence on one branch, and 4.2 adds an 'Upstream items' section. Either 4.1's order test is edited after the fact, or the implementer guesses a place. Neither was approved.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A10",
      "kind": "advisory",
      "line": 15,
      "problem": "[medium] The plan doesn't say where the upstream items and the upstream question go in 4.1's fixed section order (role, mandate, rules, checklist, evidence, paths, task, output). Line 16 puts only the four evidence items into 4.1's evidence section, and test_plan.md:27 implies a separate section ('instead of an empty section'). A new section breaks 4.1's exact-order test. The plan also doesn't state that 4.2 is built after 4.1, which it depends on."
    },
    {
      "evidence": "plan.md:33; docs/slices/poc-4-1-review-prompts/plan.md:39 (S41-D3 bounded mandate).",
      "failure_scenario": "A recheck reviewer either spends the budget reopening the whole slice diff or ignores one instruction. Either way the record shows a prompt that contradicts itself. Fix: in recheck mode, require opening the files the answers concern.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A11",
      "kind": "advisory",
      "line": 33,
      "problem": "[medium] S42-D2 puts 'open every file under review' into every prompt's paths section, recheck mode included. 4.1's recheck mandate bounds a recheck to 'the code and test it concerns'. Combined with a full-diff list, a recheck prompt gives two conflicting instructions."
    },
    {
      "evidence": "plan.md:37; plan.md:81.",
      "failure_scenario": "A red tooling test turns the whole coverage item into 'failed: pytest \u2026: exit 1'. The reviewer loses both the coverage and the names of the failing tests, and the owner can't see in the log which reviews had no evidence.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A12",
      "kind": "advisory",
      "line": 37,
      "problem": "[medium] S42-D6 doesn't say how a pytest run that executes but has failing tests is shown: as 'failed' (coverage dropped) or as coverage plus the failed tests. It also doesn't say whether evidence failures are logged per item. The start entry holds only the evidence hash, so an attempt where all evidence failed looks the same in the log as a fully evidenced one."
    },
    {
      "evidence": "plan.md:36 '(c) ... (empty after S42-D1, unless a file is withheld)'; run_independent_review.py:473 paths_read.",
      "failure_scenario": "The item adds code, a test and prompt text that never shows anything useful, and the unopened listed files stay unreported.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-S1",
      "kind": "simpler_alternative",
      "line": 36,
      "problem": "S42-D5(c) ('changed files the review list leaves out') is empty by construction after S42-D1, except for the withheld record and log, which would appear in every review as noise. Drop it, or replace it with the deterministic list the owner's principle actually needs: the listed files the reviewer did not open, from the paths_read the launcher already logs."
    },
    {
      "evidence": "docs/delivery_problem_log.md:304-312; #33 comment 'Weak spots' item 2.",
      "failure_scenario": "A reader misattributes the cause, and a later DPL test (4.4's S44-D9 mapping) tests the wrong question against DPL-010.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R2-A13",
      "kind": "advisory",
      "line": 11,
      "problem": "[low] The goal says DPL-010 slipped through partly because 'nothing asked where a problem started'. DPL-010 is about closed questions and rechecks that took the author's word. The missing upstream question is the #33 comment's lesson from DPL-004. The environment-fact probes (lines 73-75) give no date or commit, unlike the other plans."
    }
  ],
  "verdict": "no"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| S42-R2-B1 | blocking | fixed: S42-D1 lists deleted files in their own part ("deleted by the change: examine in `change.diff`"); test row "File list" |
| S42-R2-B2 | blocking | fixed: S42-D3(a) always names the governing plan, the bundle of `--record`, and its decision IDs; test row "Governing plan" (a change that touches no file of its bundle) |
| S42-R2-B3 | blocking | fixed: S42-D6 (every evidence entry appears in `accounted` as `explained` or `flagged`; a report that leaves one out fails); test row "Accounted entries" |
| S42-R2-B4 | blocking | fixed: S42-D5(c) reads the runs whose head is the reviewed commit, or says "no CI run for this commit"; `--ci-run` is gone; test row "CI results" |
| S42-R2-A1 | high | fixed: S42-D5(a) lists the uncovered changed lines and branches per file; each changed `services/` file names its coverage gate or "no coverage gate"; test row "Uncovered lines" |
| S42-R2-A2 | high | fixed: the "not measurable" label is gone; a fixed note says a script run as a subprocess shows as uncovered (#44), and its lines are listed like any other, for the reviewer to account for |
| S42-R2-A3 | high | fixed: S42-D9 (the evidence is kept verbatim in the record, 4.3 S43-D1, and its hash in the start entry); test row "Evidence hash" |
| S42-R2-A4 | high | fixed: S42-D11 says what the benchmark gets (paths as hints, upstream items, no computed evidence) and why; 4.5's goal and out-of-scope say so |
| S42-R2-A5 | high | fixed: S42-D3(c) takes `DD` tags anywhere in a changed file; S42-D3(d) adds changed `REQ` and `ARCH` headings and changed `trace/tests.yaml` entries; test row "Upstream items" |
| S42-R2-A6 | high | fixed: S42-D10 covers `make_frozen_copy`, `build_prompt` and `invocation_from_entry`, keyword-only without a default; test row "Required diff base" expects `TypeError` and the `change.diff` line in every prompt |
| S42-R2-A7 | medium | fixed: S42-D2 (the empty-review rule applies to the `--path` files when given; unopened listed files go into `paths_not_read` and the record) |
| S42-R2-A8 | medium | fixed: S42-D8 (minimal environment, relative paths, no token, refusal on the author's HOME path or the scratch root); test row "Clean environment" |
| S42-R2-A9 | medium | fixed: S42-D5(b) lists every gap among the upstream items, marked new, existing or accepted |
| S42-R2-A10 | medium | fixed: 4.1 S41-D1 gives the upstream section its place (after the checklist, before the evidence); the order of work is in the slice index |
| S42-R2-A11 | medium | fixed: S42-D2 says a recheck opens the answered files first, matching 4.1's recheck mandate |
| S42-R2-A12 | medium | fixed: S42-D7 (failing tests shown with coverage and their names; each item's status in the start entry) |
| S42-R2-S1 | low | fixed: adopted; the item is dropped (Retirement), and unopened files are shown by S42-D2 |
| S42-R2-A13 | low | fixed: the goal names DPL-010's rechecks and DPL-004 for the upstream question; the probes carry dates and commits |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "S42-R2-B1: accepted (poc-4-2 plan.md:39, test_plan.md:26)\nS42-R2-B2: accepted (plan.md:41, test_plan.md:28)\nS42-R2-B3: accepted (plan.md:44, test_plan.md:35, poc-4-1 plan.md:50 S41-D8 '4.2 adds the evidence entries to the same list')\nS42-R2-B4: accepted (plan.md:43 (c), test_plan.md:33, plan.md:89 probe)\nS42-R2-A1: accepted (plan.md:43 (a), plan.md:73-74, test_plan.md:31)\nS42-R2-A2: accepted (plan.md:43 #44 note, test_plan.md:49)\nS42-R2-A3: accepted (plan.md:47, poc-4-3 plan.md:37 S43-D1 Evidence block, :39 S43-D3 evidence_sha256 check, test_plan.md:38)\nS42-R2-A4: accepted (plan.md:49 S42-D11, poc-4-5 plan.md:18, 29-30, 87, test_plan.md:40)\nS42-R2-A5: accepted (plan.md:41 (c),(d), test_plan.md:29)\nS42-R2-A6: accepted (plan.md:48, test_plan.md:39)\nS42-R2-A7: accepted (plan.md:40, test_plan.md:27)\nS42-R2-A8: accepted (plan.md:46, test_plan.md:37, poc-4-3 plan.md:38)\nS42-R2-A9: accepted (plan.md:43 (b), test_plan.md:32)\nS42-R2-A10: accepted (poc-4-1 plan.md:43 S41-D1 order, plan.md:10-12, docs/slices/README.md:16)\nS42-R2-A11: accepted (plan.md:40, test_plan.md:27)\nS42-R2-A12: accepted (plan.md:45, test_plan.md:36)\nS42-R2-S1: accepted (plan.md:116-117)\nS42-R2-A13: accepted (plan.md:16-18, 87-89)",
      "failure_scenario": "None; bookkeeping entry.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    },
    {
      "evidence": "plan.md:46 'only PATH, LANG and a scratch HOME. Paths in their output are made relative to the checkout... on a match the launcher refuses before any call'; plan.md:45 S42-D7 shows failing tests with their names; test_plan.md:37 tests only the refusal and relative checkout paths.",
      "failure_scenario": "The author's interpreter lives in /home/<user>/.venv; a changed tooling test fails, pytest prints a frame from site-packages, and the launcher refuses. The author then either cannot review the failing state or is pushed to weaken the check. Fix: replace the author's HOME and the interpreter prefix with fixed placeholders before the check (refuse only what remains), and test a traceback through site-packages.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R3-A1",
      "kind": "advisory",
      "line": 46,
      "problem": "[medium] S42-D8 refuses the whole review when the evidence holds the author's HOME path, but the evidence commands' own output will often hold it: the interpreter and site-packages paths in a pytest traceback or a coverage warning (a venv under the author's home, kept on PATH) are not under the scratch checkout, so 'made relative to the checkout' does not remove them. A review of a change with any failing tooling test (exactly where evidence matters, S42-D7) would then be refused, not sanitised."
    },
    {
      "evidence": "plan.md:43 'the job conclusions of the workflow runs whose head is the reviewed commit ... or \"no CI run for this commit\"'; test_plan.md:33 covers only a matching run and no run.",
      "failure_scenario": "The implementation shows an in-progress run's null conclusions as an empty list or omits unfinished jobs; the reviewer reads the visible green jobs as the commit's CI result. Fix: show each job's status as well as conclusion ('in_progress', 'queued'), and add a test row for an unfinished run.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R3-A2",
      "kind": "advisory",
      "line": 43,
      "problem": "[medium] S42-D5(c) does not say what is shown when the reviewed commit's CI run exists but is still running or queued (jobs without a conclusion), nor when the commit is not yet pushed. Reviews commonly run right after the push, before CI finishes."
    },
    {
      "evidence": "poc-4-1 plan.md:50 S41-D8; poc-4-2 plan.md:44; test_plan.md:35.",
      "failure_scenario": "The 4.1 implementer writes a strict enum and recheck-only requirement; 4.2's tests then need 4.1's schema edited after the fact. Fix: one sentence in S41-D8 or S42-D6 naming the extra statuses and that the field applies in every mode.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "S42-R3-A3",
      "kind": "advisory",
      "line": 44,
      "problem": "[low] S42-D6 puts evidence entries into 4.1's `accounted` list with statuses `explained`/`flagged`, but S41-D8 defines `accounted` as `{item, status, note, opened}` with status `accepted` or `re-raised` and describes it for rechecks. Neither plan states that the schema's status enum widens and that `accounted` is required in initial and final reviews too when evidence exists."
    }
  ],
  "verdict": "yes"
}
```

#### Answers to plan/c1/r3/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| S42-R3-A1 | medium | fixed: docs/slices/poc-4-2-review-inputs/plan.md, docs/slices/poc-4-2-review-inputs/test_plan.md: S42-D8 replaces the HOME path and the interpreter prefix with `<home>` and `<python>` before the check, and refuses only what remains; the "Clean environment" row has a traceback through site-packages |
| S42-R3-A2 | medium | fixed: docs/slices/poc-4-2-review-inputs/plan.md, docs/slices/poc-4-2-review-inputs/test_plan.md: S42-D5(c) shows each job's status and conclusion; the "CI results" row has a running job |
| S42-R3-A3 | low | fixed: docs/slices/poc-4-1-review-prompts/plan.md: S41-D8 says `accounted` is required whenever the prompt lists items, with the evidence statuses `explained` and `flagged` in every mode |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
