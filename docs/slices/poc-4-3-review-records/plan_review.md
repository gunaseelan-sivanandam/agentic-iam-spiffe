# Plan review — 4.3 (#40), review records and their check

Record of the plan review of slice 4.3 (#40), review records and their check in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

After round 4, the last allowed, the plan changed only by quoting the owner's words in its Source column and re-sourcing S43-D7 to the owner's words on #21 (commit `a99d4f8`); it was not rechecked.

## Round 1

### Attempt plan/c1/r1/plan/1

Commit `dfc88e2`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-3-review-records/plan.md` `a5dbc58fb7c1`, `docs/slices/poc-4-3-review-records/test_plan.md` `41f4807d658d`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 1 (the initial review), of slice 4.3 of the agentic-SDLC PoC: `docs/slices/poc-4-3-review-records/plan.md` and `test_plan.md` (GitHub issue #40). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#40)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** review records are written and checked by tools, not by hand. See [the decision](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725327080).

**Problem:** a review record must keep every prompt and report verbatim. In slices 2 and 3 the author built these blocks by hand and got it wrong: prompts held placeholders, reports were reformatted, and the attempt log's fingerprints matched nothing (DPL-010). Until this lands, the author checks records by hand before every push.

**Decided:**
1. **The launcher writes the blocks.** When it releases a report, it appends the exact prompt and the exact report to the review record, under a heading per attempt. The author adds only the answers.
2. **The launcher scans before publishing.** It runs the evidence secret check on the prompt too (today it checks only reports and log lines), and writes nothing on a finding.
3. **`docs-check` verifies the records.** For every slice with an attempt log, every completed attempt's prompt and report must have a matching verbatim block, and every block must match a logged fingerprint. No new CI job is needed.
4. **The hand-run script becomes this committed check** ([R6-2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844)).

**Not here:** scanning whole documents for secrets stays with #21.

**Done when:** the launcher writes the blocks; `docs-check` fails on a mismatch; tooling tests cover both; `AGENTS.md`'s `docs-check` row names the check.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 scope: review records written and checked by tools** (owner decision, 2026-11-08: "do it with slice 4")

**Problem.** A review record (`docs/slices/<id>/review_<unit>.md`) must keep every task prompt and every report verbatim (`AGENTS.md`, Independent review), so anyone can check what a reviewer was asked and what it answered. Today the author builds these blocks by hand. Slices 2 and 3 both got it wrong: prompts held placeholders, reports were reformatted, and the attempt log's SHA-256 fingerprints matched nothing in the repository (slice 2 review round 5, R5-B2; DPL-010). Since the fix, the author checks the blocks against the log with a script run by hand before each push. That check depends on the author remembering it.

**Agreed for slice 4:**
1. **The launcher writes the blocks.** When it releases a report, `scripts/run_independent_review.py` appends the exact prompt and the exact report to the review record, under a heading per attempt. The author adds only the answers. This removes copying by hand at its origin.
2. **The launcher scans before publishing.** It already runs the evidence secret check on reports and log lines; it will also check the prompt before writing it into the public record, and write nothing on a finding.
3. **A deterministic check in `docs-check`.** For every slice with an attempt log, every completed attempt's prompt and report must have a matching verbatim block in its record, and every block must match a logged hash. A record that fails either way fails CI. This needs no new CI job or required check. Records without an attempt log (slice 1, the plan reviews) are not checked.

| Check (POC-D6) | |
| --- | --- |
| Failure it catches | A review record that does not hold exactly what the reviewer was asked and answered (it happened in slices 2 and 3) |
| Cost | One launcher function, one `docs-check` check, tooling tests for both, one line in the `docs-check` row of `AGENTS.md` |
| Simpler alternative considered | The author's script run by hand: it depends on memory, and it is what the owner asked to replace |

**Not in this item:** scanning whole documents for secrets. It stays with #21: today's shape scanner flags a row of `AGENTS.md` that every review prompt quotes, so documents need #21's design.

**Until slice 4:** the author runs the record check by hand before every push.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: from slice 2's review round 6** (the recheck the owner asked for, PR #35)

1. **Verbatim review records grow with every round (R6-9).** Since review records keep every prompt verbatim, and each recheck prompt contained the whole record, each round's prompt repeats all the rounds before it. Slice 2's record already needs nested 5-, 6- and 7-backtick fences. Proposal for the prompt rules: a recheck gets its own earlier report, the author's answers and the evidence that is not in its copy, not the whole record.
2. **The record check is a script run by hand (R6-2).** The check that every verbatim block of a review record matches the attempt log's hashes ran as an ad-hoc script. Nobody can repeat it from the repository. A committed check is a candidate for slice 6 (gates that the run shows are needed).
3. **Repeat CLI probes when the CLI changes (R6-7).** The launcher's fix for failed Reads relies on how the CLI reports them. On 2026-11-08, with CLI 2.1.319, a failed Read came back as an error result carrying the call's ID. This probe joins the canary in the list of checks to repeat when the CLI version in the attempt log changes. Today that repeat is manual; making it automatic is part of the same decision as the canary.
4. **DPL-010** (delivery problem log, open) records slice 2's review misses. Its preventive actions are the slice-4 items in this issue.

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

Lost: another unit's report overwrote its file before the fix of the report path (DPL-011). The log keeps its SHA-256 `a37be39317ce`.

## Round 2

### Attempt plan/c1/r2/plan/1

Commit `f070669`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-3-review-records/plan.md` `a5dbc58fb7c1`, `docs/slices/poc-4-3-review-records/test_plan.md` `41f4807d658d`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
**Note on this round:** round 1 of this review unit completed with verdict "no", but its report was lost: a launcher bug made all six plan reviews write the same report file (fixed in commit f070669, which is in your copy). This round 2 is therefore a full review with the open mandate, not a recheck.

## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 2 (a full review; see the note above), of slice 4.3 of the agentic-SDLC PoC: `docs/slices/poc-4-3-review-records/plan.md` and `test_plan.md` (GitHub issue #40). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#40)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** review records are written and checked by tools, not by hand. See [the decision](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725327080).

**Problem:** a review record must keep every prompt and report verbatim. In slices 2 and 3 the author built these blocks by hand and got it wrong: prompts held placeholders, reports were reformatted, and the attempt log's fingerprints matched nothing (DPL-010). Until this lands, the author checks records by hand before every push.

**Decided:**
1. **The launcher writes the blocks.** When it releases a report, it appends the exact prompt and the exact report to the review record, under a heading per attempt. The author adds only the answers.
2. **The launcher scans before publishing.** It runs the evidence secret check on the prompt too (today it checks only reports and log lines), and writes nothing on a finding.
3. **`docs-check` verifies the records.** For every slice with an attempt log, every completed attempt's prompt and report must have a matching verbatim block, and every block must match a logged fingerprint. No new CI job is needed.
4. **The hand-run script becomes this committed check** ([R6-2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844)).

**Not here:** scanning whole documents for secrets stays with #21.

**Done when:** the launcher writes the blocks; `docs-check` fails on a mismatch; tooling tests cover both; `AGENTS.md`'s `docs-check` row names the check.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 scope: review records written and checked by tools** (owner decision, 2026-11-08: "do it with slice 4")

**Problem.** A review record (`docs/slices/<id>/review_<unit>.md`) must keep every task prompt and every report verbatim (`AGENTS.md`, Independent review), so anyone can check what a reviewer was asked and what it answered. Today the author builds these blocks by hand. Slices 2 and 3 both got it wrong: prompts held placeholders, reports were reformatted, and the attempt log's SHA-256 fingerprints matched nothing in the repository (slice 2 review round 5, R5-B2; DPL-010). Since the fix, the author checks the blocks against the log with a script run by hand before each push. That check depends on the author remembering it.

**Agreed for slice 4:**
1. **The launcher writes the blocks.** When it releases a report, `scripts/run_independent_review.py` appends the exact prompt and the exact report to the review record, under a heading per attempt. The author adds only the answers. This removes copying by hand at its origin.
2. **The launcher scans before publishing.** It already runs the evidence secret check on reports and log lines; it will also check the prompt before writing it into the public record, and write nothing on a finding.
3. **A deterministic check in `docs-check`.** For every slice with an attempt log, every completed attempt's prompt and report must have a matching verbatim block in its record, and every block must match a logged hash. A record that fails either way fails CI. This needs no new CI job or required check. Records without an attempt log (slice 1, the plan reviews) are not checked.

| Check (POC-D6) | |
| --- | --- |
| Failure it catches | A review record that does not hold exactly what the reviewer was asked and answered (it happened in slices 2 and 3) |
| Cost | One launcher function, one `docs-check` check, tooling tests for both, one line in the `docs-check` row of `AGENTS.md` |
| Simpler alternative considered | The author's script run by hand: it depends on memory, and it is what the owner asked to replace |

**Not in this item:** scanning whole documents for secrets. It stays with #21: today's shape scanner flags a row of `AGENTS.md` that every review prompt quotes, so documents need #21's design.

**Until slice 4:** the author runs the record check by hand before every push.

### A comment on issue #33 (slice 4's inputs)

**Slice-4 input: from slice 2's review round 6** (the recheck the owner asked for, PR #35)

1. **Verbatim review records grow with every round (R6-9).** Since review records keep every prompt verbatim, and each recheck prompt contained the whole record, each round's prompt repeats all the rounds before it. Slice 2's record already needs nested 5-, 6- and 7-backtick fences. Proposal for the prompt rules: a recheck gets its own earlier report, the author's answers and the evidence that is not in its copy, not the whole record.
2. **The record check is a script run by hand (R6-2).** The check that every verbatim block of a review record matches the attempt log's hashes ran as an ad-hoc script. Nobody can repeat it from the repository. A committed check is a candidate for slice 6 (gates that the run shows are needed).
3. **Repeat CLI probes when the CLI changes (R6-7).** The launcher's fix for failed Reads relies on how the CLI reports them. On 2026-11-08, with CLI 2.1.319, a failed Read came back as an error result carrying the call's ID. This probe joins the canary in the list of checks to repeat when the CLI version in the attempt log changes. Today that repeat is manual; making it automatic is part of the same decision as the canary.
4. **DPL-010** (delivery problem log, open) records slice 2's review misses. Its preventive actions are the slice-4 items in this issue.

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
      "evidence": "plan.md:34 (D3: 'For every docs/slices/<id>/review_attempts.jsonl \u2026 no logged hash lacks a block'); plan.md:36 (D5: 'Slice 1's record and the plan reviews have no attempt log'). This review's own launcher run withheld `docs/slices/poc-4-3-review-records/review_attempts.jsonl` and `plan_review.md`, so the log exists and names `plan_review.md` as its record. The task note says round 1's reports were lost because all six plan reviews wrote the same report file. The owner's #33 comment ('Records without an attempt log (slice 1, the plan reviews) are not checked') was written before slice 4 ran its plan reviews through the launcher.",
      "failure_scenario": "4.3 is implemented as written. `make docs-check` then fails on the slice-4 branch for at least five of the six `poc-4-*` bundles: a logged round-1 `report_sha256` has no block, and the hand-built blocks are not under `### Attempt` headings. The log is append-only, so the implementer must either stop and ask the owner, which this run mode forbids, or quietly exempt the bundles or hand-edit blocks, which brings back the DPL-010 class. The plan must say how logged plan reviews are treated, including attempts whose report was lost.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B1",
      "kind": "blocking",
      "line": 36,
      "problem": "Contradiction between S43-D3 and S43-D5. D5 (and the environment facts) say 'the plan reviews have no attempt log and are not checked'. D3 says the check runs for every `docs/slices/<id>/review_attempts.jsonl`. Slice 4's own plan reviews go through the launcher and log to `docs/slices/poc-4-*/review_attempts.jsonl`, with `plan_review.md` as the record. So D3 covers them, and the plan has no rule for them: no conversion and no exemption. Those records are hand-written in the old layout. Their round-1 reports were lost to the launcher bug, so their logged `report_sha256` values can never get a matching block."
    },
    {
      "evidence": "review_slice_3.md:551-553 answers with '**No change**' and '**Confirmed**'. Slice 3's round 2 (report ends at line 451, round 3 starts at line 455) has no answers section for its 8 findings. review_slice_3.md:194-201 answers in a table cell starting 'Fixed.', with no D4 grammar. Slice 2's records likewise answer with prose tables. AGENTS.md Documentation rules: 'Implemented slice bundles are frozen records'.",
      "failure_scenario": "The implementer follows D4 and D5 as written. The converted `review_slice_3.md` fails the answers check: round 2 has F1\u2013F8 unanswered, and R3-A2 says 'No change' rather than `declined`. To get green, the implementer invents answers or relabels them in a frozen record, which is a false record. The other way out is to weaken D4 silently. Either way the plan cannot be built without asking the owner.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B2",
      "kind": "blocking",
      "line": 105,
      "problem": "S43-D5 contradicts the rulebook, and D4 and D5 contradict each other. (1) AGENTS.md says 'Implemented slice bundles are frozen records; do not rewrite them to match later reality'. Converting the merged slice 2 and 3 records to a new layout so a new checker accepts them is exactly that. (2) Retirement says their 'content stays verbatim; only the layout changes', but D4 applies the answers check to every released report of every logged unit. The old records' answers do not use `fixed`/`deferred #N`/`declined <reason>`, and some rounds have no answers at all. So the conversion would have to rewrite the answers (content), or the check fails on them."
    },
    {
      "evidence": "plan.md:32 (D1: 'the task prompt verbatim, the full prompt's SHA-256'); plan.md:34 (D3 checks only `prompt_sha256`/`report_sha256`). In run_independent_review.py:738, `prompt_sha256` hashes only the task file and `full_prompt_sha256` the built prompt. poc-4-1 plan.md:40 (S41-D4: the launcher puts the earlier report and `--answers <file>` into the prompt). poc-4-2 plan.md:36 (the evidence goes into the prompt; only its hash goes into the start entry). The owner (#40 decision 1): 'appends the exact prompt and the exact report'. Threat model plan.md:22: 'a record that paraphrases or shortens what the reviewer saw'.",
      "failure_scenario": "The author runs a recheck with `--answers answers_r2.md`, then edits or rewrites the `#### Answers to <attempt>` section in the record, for example to tidy wording or fix an answer after the recheck accepted it. The record now shows answers the reviewer never saw. The task-prompt block still matches `prompt_sha256` and the report block matches `report_sha256`, so docs-check is green. That is a false green inside this plan's own threat model. A fix within the decisions: write the launcher-added variable parts (answers file, earlier-report reference, evidence) verbatim, or the full prompt minus the approved rules (reproducible from `rules_sha256`), and check them against hashes in the start entry.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B3",
      "kind": "blocking",
      "line": 32,
      "problem": "The record holds only the *task prompt* verbatim. After 4.1 and 4.2, the launcher adds most of what the reviewer is asked: the mandate, the checklist, computed evidence, and for rechecks the earlier report and the author's `--answers` file. The record does not hold these, and the check does not verify `full_prompt_sha256`. So 'anyone can check what a reviewer was asked' is false exactly for rechecks: the answers the reviewer verified can differ from the answers in the record, and the check still passes. The owner asked for 'the exact prompt'. Narrowing it to the task file is not flagged as a default."
    },
    {
      "evidence": "run_independent_review.py:764-766: `ctx.log.append(start)` comes before `call_reviewer(...)`. Lines 602-611: `recover` writes an 'interrupted' end entry and has no prompt content; the start entry keeps only `prompt_file` as a basename (line 737). Lines 813-816: a withheld report returns 'withheld'. test_plan.md:28 only asserts that the prompt 'is not written into the record'. It does not assert that the reviewer was not called or that no start entry was logged.",
      "failure_scenario": "Case 1: the author pastes a test key into a task prompt. The launcher logs the start entry, sends the key to the reviewer service, and then refuses to write the block. From then on, every docs-check run fails on that slice for a logged hash with no block. The fix would be hand-writing a block containing the secret, or editing the append-only log. Case 2: a Ctrl-C during a 7-minute review leaves the same permanent failure. Fix: scan the prompt, and write its block, before the start entry and the call; refuse with exit 2 on a finding. Add tests for the blocked-prompt, interrupted and withheld paths.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B4",
      "kind": "blocking",
      "line": 33,
      "problem": "The plan contradicts itself on attempts that never release a report. D1 writes blocks 'after it releases a report'. D3 requires that 'every attempt has its blocks' and that 'no logged hash lacks a block'. The start entry, which carries `prompt_sha256`, is appended before the reviewer call. Three paths therefore log a prompt hash that can never get a block: (a) D2's prompt scan finds a secret and 'writes nothing'; (b) the launcher is killed and `recover()` later writes 'interrupted'; (c) the publication check withholds the report. The log is append-only, so the record can never pass again. In addition, D2 does not say the prompt is scanned before the reviewer call, so a secret in a prompt can still be sent to the external reviewer."
    },
    {
      "evidence": "plan.md:35 Source column: 'owner, #33 decision 7; sub-issue 4.1, S41-D6'. poc-4-1 plan.md:42 labels the check placement 'default'. plan.md:111-112 lists S43-D1, D5 and D7 as defaults, not D4. The POC-D6 cost row the owner approved: 'One launcher function, one docs-check check'.",
      "failure_scenario": "The owner approves the plan PR believing D4 is their own earlier decision. CI then fails every push between a released report and the author's answers, a cost the owner never weighed.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A1",
      "kind": "advisory",
      "line": 35,
      "problem": "[high] S43-D4 is presented as the owner's decision, but the docs-check *gate* on answers is the author's default. #40's decisions 1\u20134 and its 'Done when' cover blocks and hashes only. #33 decision 7 says every finding gets an answer, not that CI checks it. S41-D6 itself marks 'the check lives in 4.3' as a default. D4 is missing from 'Review notes' (defaults for the owner to confirm), so the owner may approve a new gate without noticing (AGENTS.md 'Ask before growing'). The '\"owner deferred\"' text marker is also the author's invention."
    },
    {
      "evidence": "plan.md:35. test_plan.md:30 fail cases: only 'without an answer', 'deferred without an issue', 'high deferred without owner deferred'. Owner's comment on #33, decision 3: 'blocking \u2026 fixed before merge, or the owner decides; \u2026 medium \u2026 fixed, or deferred with a tracking issue'.",
      "failure_scenario": "An implementation that accepts any of the three words for any kind, and checks the 'owner deferred' text only on `deferred`, passes every planned test. A blocking finding answered 'declined: out of scope' then passes docs-check with no owner decision.",
      "file": "docs/slices/poc-4-3-review-records/test_plan.md",
      "id": "R2-A2",
      "kind": "advisory",
      "line": 30,
      "problem": "[high] D4's rules are incomplete and its tests leave obvious wrong implementations green. Under the owner's scale, blocking means 'fixed before merge, or the owner decides', and medium means 'fixed, or deferred with a tracking issue'. D4 constrains only `high`. So a blocking finding answered `deferred #12` or `declined \u2026` passes, and so does a medium one `declined`. D4 also does not say whether `high` may be `declined` (contested). The owner's 'fixed (where)' is not required either. No test covers `declined` without a reason, a `high` finding `declined`, a blocking finding deferred, or an answer that lists an ID not in the report."
    },
    {
      "evidence": "plan.md:34. test_plan.md:29 fail cases: a changed character, an extra block, a missing block, a missing record. None places a valid block under another attempt's heading.",
      "failure_scenario": "During the one-time hand conversion (D5), the author swaps two rounds' report blocks. Every hash still appears in the log, so a set-based check passes. D4 then validates round 2's answers against round 1's findings and may pass with findings unanswered.",
      "file": "docs/slices/poc-4-3-review-records/test_plan.md",
      "id": "R2-A3",
      "kind": "advisory",
      "line": 29,
      "problem": "[high] D3 checks block hashes against any hash in the log ('matches a prompt_sha256 or report_sha256 of that log'), not against the attempt whose heading the block sits under. The planned tests cannot tell a set comparison from per-attempt binding. D4 reads each attempt's findings from 'its' report block, so a block under the wrong heading makes D4 check answers against the wrong findings. Retries and several reviewers sharing a task file also produce repeated prompt hashes."
    },
    {
      "evidence": "plan.md:34 ('Blocks are found outermost first: the longest fences first'); plan.md:38 (D7). review_slice_3.md:567-569 already wraps prompts in `<details>`, and earlier records put a 'Command' section in the header.",
      "failure_scenario": "An author answers a finding with a fenced command snippet under `#### Answers to \u2026`. docs-check then fails with 'block with no logged hash' (a false red), and the author learns to avoid code in answers, or the implementer adds ad-hoc exemptions.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A4",
      "kind": "advisory",
      "line": 38,
      "problem": "[medium] The plan does not define which fenced blocks are 'blocks'. D3's 'every block must match a logged hash' would fail on any other fence in the record: a code fence in the author's answers, in a rendered report view (findings often quote code with backticks), or in a header or command section. D7 says the check 'ignores rendered views' without saying how it recognises them, and the launcher only 'may' add them. 'Longest fences first' is not how CommonMark pairs fences. A sequential parse that only considers fences directly under `### Attempt` labels is simpler and exact."
    },
    {
      "evidence": "poc-4-1 plan.md:89, 95-96. poc-4-3 plan.md:56-61 (In scope). poc-4-5 plan.md:46.",
      "failure_scenario": "The implementer builds 4.3 before 4.1, so the `high` rule has no `high` findings to test against real reports. Or 4.1's 'until 4.3' state never ends, and rechecks keep depending on git-ignored local files that a fresh clone lacks.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A5",
      "kind": "advisory",
      "line": 56,
      "problem": "[medium] Missing cross-plan pieces and order. 4.1 says the recheck reads the earlier report from `artifacts/reviews/` 'until 4.3 moves it into the record', and names '4.3's check' as a reader of `mode` and `severity_counts`. 4.3's scope covers neither: it does not switch the recheck source and does not use either field. D4 also depends on 4.1's kinds (`high`) and answer format, yet no plan states that 4.1 is built before 4.3. Only S45-D9 orders anything."
    },
    {
      "evidence": "review_slice_3.md:17-18 uses `\"impl:<scratch>/task_r<n>.md:\u2026\"`, a placeholder the author used to keep local paths out. plan.md:71-72: 'No asset changes'.",
      "failure_scenario": "A task prompt says 'compare with /home/<user>/work/agentic-iam-spiffe/\u2026'. The launcher publishes it verbatim, the check cannot allow redaction, and the path stays in history. A one-line prompt-writing rule in AGENTS.md (no local paths in task text), or the launcher refusing absolute paths outside the copy, would prevent it.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A6",
      "kind": "advisory",
      "line": 69,
      "problem": "[medium] Operational details in public records. The launcher now writes task prompts and reports verbatim into a committed record, and hash matching forbids redaction. The only scan is for secret shapes. Task prompts written by the author can contain local absolute paths (scratch directories, home directories). Earlier hand records replaced these with `<scratch>` placeholders, which hash matching no longer allows. 'Assets and holders' says nothing changes."
    },
    {
      "evidence": "plan.md:32 ('under `#### Answers to <attempt id>`') and plan.md:35 give only the three words. Existing answers are tables: review_slice_3.md:549-553.",
      "failure_scenario": "The implementer picks a strict line format. The author's first real answers in a table fail docs-check, or a loose regex accepts 'Fixed? not yet' as `fixed`.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A7",
      "kind": "advisory",
      "line": 35,
      "problem": "[medium] The answer grammar the check parses is not specified: a table row or a list line, the ID column, case ('Fixed.' as in earlier records), and where a reason or issue reference must appear. It is left to the implementer, though authors must write to it and the converted records must match it."
    },
    {
      "evidence": "plan.md:107; delivery_problem_log.md:306 ('Status: Open (preventive actions are inputs for slice 4)'); test_plan.md has no row for the AGENTS.md row.",
      "failure_scenario": "The hand check's retirement and DPL-010's status are never recorded in the repository, and the AGENTS.md row goes unreviewed.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A8",
      "kind": "advisory",
      "line": 107,
      "problem": "[low] Retirement relies on 'a memory note', which is outside the repository and invisible to reviewers. The scope also omits updating DPL-010, whose preventive actions are this slice. 'AGENTS.md's docs-check row names the check' (the owner's Done-when) has no test or review line in the test plan."
    },
    {
      "evidence": "run_independent_review.py:803-805 (parallel `_guarded_attempts`); only the attempt log has a mutex and flock (lines 562-599).",
      "failure_scenario": "Two reviewers finish together; their appends interleave and corrupt both blocks. The check then fails, and the reports exist only in git-ignored artifacts.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A9",
      "kind": "advisory",
      "line": 32,
      "problem": "[low] Reviewers in a round run in parallel threads (`ThreadPoolExecutor`). D1 has each one append to the same record file, with no stated lock or order, so blocks can interleave and their order can vary between runs."
    },
    {
      "evidence": "plan.md:78 (the hand check already matches all blocks); AGENTS.md frozen-records rule; R2-B2.",
      "failure_scenario": "Without it, the conversion rewrites frozen records and either invents answers or weakens D4 (R2-B2).",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-S1",
      "kind": "simpler_alternative",
      "line": 36,
      "problem": "Drop the one-time conversion (D5). Make the hash check layout-agnostic: every logged prompt and report hash has an exactly matching fenced block in the record, and every attempt-heading block matches its attempt. Apply the per-attempt heading binding and the answers check (D4) only to attempts the new launcher logs, for example those whose start entry has 4.1's `mode`. The existing records already pass the hash part (13/13 and 8/8 by the author's probe), so nothing frozen is rewritten, and D4 never meets the old answer vocabulary."
    },
    {
      "evidence": "The owner's #33 comment, as quoted in the task; this review's withheld `review_attempts.jsonl`; the task note on the round-1 launcher bug.",
      "failure_scenario": "Without an owner decision, the implementer must choose between a permanently red docs-check and an unapproved exemption (R2-B1).",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-DC1",
      "kind": "decision_concern",
      "line": 36,
      "problem": "The owner's premise 'Records without an attempt log (slice 1, the plan reviews) are not checked' no longer holds: slice 4's plan reviews have attempt logs, and five of their round-1 reports are lost. The owner should decide whether logged plan-review records are checked, and how a logged attempt whose report was lost is recorded. One option is a one-line exception with an expiry. Another is a log-level 'lost' marker written by the launcher, not the author."
    }
  ],
  "verdict": "no"
}
```

#### Answers to plan/c1/r2/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| R2-B1 | blocking | fixed: S43-D3 checks only attempts whose start entry has `record_blocks: 1`, written from 4.3 on; S43-D5 says slice 4's plan-review records (with their lost round-1 reports) stay as they are and were checked by hand before the plan PR |
| R2-B2 | blocking | fixed: S43-D5 drops the conversion; the frozen records of slices 2 and 3 are not rewritten, and S43-D4 never meets their old answers |
| R2-B3 | blocking | fixed: the answers live in the record and a recheck logs their hash (4.1 S41-D5); S43-D1 writes the evidence verbatim; S43-D3 fails answers changed after the recheck that read them; the mandate and checklist are reproducible from the base commit; test row "Check: answers after the recheck" |
| R2-B4 | blocking | fixed: S43-D2 scans the full prompt and refuses before the start entry and the call; S43-D1 writes prompt and evidence before the call, so failed, withheld and interrupted attempts have their blocks and no report hash; test rows "Scan before the call" and "Blocks of attempts without a report" |
| R2-A1 | high | fixed: S43-D4's source names the docs-check placement as a default, Review notes list it, and the POC-D6 row states the cost (docs-check red between a report and its answers) |
| R2-A2 | high | fixed: 4.1 S41-D7 gives the allowed answers per severity, and S43-D4 checks them, including a rejected blocking or high answer (needs the next round's `accepted` or an owner link); test row "Check: allowed answers" lists each wrong case |
| R2-A3 | high | fixed: S43-D3 binds each block to the attempt under whose heading it sits; test row "Check: blocks" has a report block under another attempt's heading |
| R2-A4 | medium | fixed: S43-D3 defines a block as the fence right after a `#### Prompt`, `#### Evidence` or `#### Report` label; other fences are ignored; test row "Check: other fences" |
| R2-A5 | medium | fixed: S43-D6 moves the recheck's earlier report to the record's Report block; the order of work (4.1, 4.2, then 4.3) is in the slice index |
| R2-A6 | medium | fixed: S43-D2 refuses a prompt that holds the author's HOME path or the scratch root |
| R2-A7 | medium | fixed: 4.1 S41-D7 specifies the table (`\| <finding id> \| <answer> \|`) and the four first words |
| R2-A8 | low | fixed: S43-D8 (the end of the hand check stated in `AGENTS.md`; DPL-010's status updated); the review-based proof covers them |
| R2-A9 | low | fixed: S43-D1 (writes hold the attempt log's lock); test row "Parallel reviewers" |
| R2-S1 | low | fixed: adopted in S43-D5 (no conversion; the new checks apply to attempts the new launcher logs) |
| R2-DC1 | decision_concern | owner: asked in the plan PR; S43-D5 removes the conflict meanwhile (attempts logged before 4.3, including those with lost reports, are not checked), as a default for the owner to confirm |

## Round 3

### Attempt plan/c1/r3/plan/1

Commit `ebb1029`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-3-review-records/plan.md` `bb1ffa237e39`, `docs/slices/poc-4-3-review-records/test_plan.md` `92d84c697534`.

Status: completed; approvable within the threat model: no.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 3 of the plan review of slice 4.3 (review records and their check, #40), a recheck of your earlier report (round 2, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

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
      "evidence": "plan.md:34 (D3: 'For every docs/slices/<id>/review_attempts.jsonl \u2026 no logged hash lacks a block'); plan.md:36 (D5: 'Slice 1's record and the plan reviews have no attempt log'). This review's own launcher run withheld `docs/slices/poc-4-3-review-records/review_attempts.jsonl` and `plan_review.md`, so the log exists and names `plan_review.md` as its record. The task note says round 1's reports were lost because all six plan reviews wrote the same report file. The owner's #33 comment ('Records without an attempt log (slice 1, the plan reviews) are not checked') was written before slice 4 ran its plan reviews through the launcher.",
      "failure_scenario": "4.3 is implemented as written. `make docs-check` then fails on the slice-4 branch for at least five of the six `poc-4-*` bundles: a logged round-1 `report_sha256` has no block, and the hand-built blocks are not under `### Attempt` headings. The log is append-only, so the implementer must either stop and ask the owner, which this run mode forbids, or quietly exempt the bundles or hand-edit blocks, which brings back the DPL-010 class. The plan must say how logged plan reviews are treated, including attempts whose report was lost.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B1",
      "kind": "blocking",
      "line": 36,
      "problem": "Contradiction between S43-D3 and S43-D5. D5 (and the environment facts) say 'the plan reviews have no attempt log and are not checked'. D3 says the check runs for every `docs/slices/<id>/review_attempts.jsonl`. Slice 4's own plan reviews go through the launcher and log to `docs/slices/poc-4-*/review_attempts.jsonl`, with `plan_review.md` as the record. So D3 covers them, and the plan has no rule for them: no conversion and no exemption. Those records are hand-written in the old layout. Their round-1 reports were lost to the launcher bug, so their logged `report_sha256` values can never get a matching block."
    },
    {
      "evidence": "review_slice_3.md:551-553 answers with '**No change**' and '**Confirmed**'. Slice 3's round 2 (report ends at line 451, round 3 starts at line 455) has no answers section for its 8 findings. review_slice_3.md:194-201 answers in a table cell starting 'Fixed.', with no D4 grammar. Slice 2's records likewise answer with prose tables. AGENTS.md Documentation rules: 'Implemented slice bundles are frozen records'.",
      "failure_scenario": "The implementer follows D4 and D5 as written. The converted `review_slice_3.md` fails the answers check: round 2 has F1\u2013F8 unanswered, and R3-A2 says 'No change' rather than `declined`. To get green, the implementer invents answers or relabels them in a frozen record, which is a false record. The other way out is to weaken D4 silently. Either way the plan cannot be built without asking the owner.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B2",
      "kind": "blocking",
      "line": 105,
      "problem": "S43-D5 contradicts the rulebook, and D4 and D5 contradict each other. (1) AGENTS.md says 'Implemented slice bundles are frozen records; do not rewrite them to match later reality'. Converting the merged slice 2 and 3 records to a new layout so a new checker accepts them is exactly that. (2) Retirement says their 'content stays verbatim; only the layout changes', but D4 applies the answers check to every released report of every logged unit. The old records' answers do not use `fixed`/`deferred #N`/`declined <reason>`, and some rounds have no answers at all. So the conversion would have to rewrite the answers (content), or the check fails on them."
    },
    {
      "evidence": "plan.md:32 (D1: 'the task prompt verbatim, the full prompt's SHA-256'); plan.md:34 (D3 checks only `prompt_sha256`/`report_sha256`). In run_independent_review.py:738, `prompt_sha256` hashes only the task file and `full_prompt_sha256` the built prompt. poc-4-1 plan.md:40 (S41-D4: the launcher puts the earlier report and `--answers <file>` into the prompt). poc-4-2 plan.md:36 (the evidence goes into the prompt; only its hash goes into the start entry). The owner (#40 decision 1): 'appends the exact prompt and the exact report'. Threat model plan.md:22: 'a record that paraphrases or shortens what the reviewer saw'.",
      "failure_scenario": "The author runs a recheck with `--answers answers_r2.md`, then edits or rewrites the `#### Answers to <attempt>` section in the record, for example to tidy wording or fix an answer after the recheck accepted it. The record now shows answers the reviewer never saw. The task-prompt block still matches `prompt_sha256` and the report block matches `report_sha256`, so docs-check is green. That is a false green inside this plan's own threat model. A fix within the decisions: write the launcher-added variable parts (answers file, earlier-report reference, evidence) verbatim, or the full prompt minus the approved rules (reproducible from `rules_sha256`), and check them against hashes in the start entry.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B3",
      "kind": "blocking",
      "line": 32,
      "problem": "The record holds only the *task prompt* verbatim. After 4.1 and 4.2, the launcher adds most of what the reviewer is asked: the mandate, the checklist, computed evidence, and for rechecks the earlier report and the author's `--answers` file. The record does not hold these, and the check does not verify `full_prompt_sha256`. So 'anyone can check what a reviewer was asked' is false exactly for rechecks: the answers the reviewer verified can differ from the answers in the record, and the check still passes. The owner asked for 'the exact prompt'. Narrowing it to the task file is not flagged as a default."
    },
    {
      "evidence": "run_independent_review.py:764-766: `ctx.log.append(start)` comes before `call_reviewer(...)`. Lines 602-611: `recover` writes an 'interrupted' end entry and has no prompt content; the start entry keeps only `prompt_file` as a basename (line 737). Lines 813-816: a withheld report returns 'withheld'. test_plan.md:28 only asserts that the prompt 'is not written into the record'. It does not assert that the reviewer was not called or that no start entry was logged.",
      "failure_scenario": "Case 1: the author pastes a test key into a task prompt. The launcher logs the start entry, sends the key to the reviewer service, and then refuses to write the block. From then on, every docs-check run fails on that slice for a logged hash with no block. The fix would be hand-writing a block containing the secret, or editing the append-only log. Case 2: a Ctrl-C during a 7-minute review leaves the same permanent failure. Fix: scan the prompt, and write its block, before the start entry and the call; refuse with exit 2 on a finding. Add tests for the blocked-prompt, interrupted and withheld paths.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-B4",
      "kind": "blocking",
      "line": 33,
      "problem": "The plan contradicts itself on attempts that never release a report. D1 writes blocks 'after it releases a report'. D3 requires that 'every attempt has its blocks' and that 'no logged hash lacks a block'. The start entry, which carries `prompt_sha256`, is appended before the reviewer call. Three paths therefore log a prompt hash that can never get a block: (a) D2's prompt scan finds a secret and 'writes nothing'; (b) the launcher is killed and `recover()` later writes 'interrupted'; (c) the publication check withholds the report. The log is append-only, so the record can never pass again. In addition, D2 does not say the prompt is scanned before the reviewer call, so a secret in a prompt can still be sent to the external reviewer."
    },
    {
      "evidence": "plan.md:35 Source column: 'owner, #33 decision 7; sub-issue 4.1, S41-D6'. poc-4-1 plan.md:42 labels the check placement 'default'. plan.md:111-112 lists S43-D1, D5 and D7 as defaults, not D4. The POC-D6 cost row the owner approved: 'One launcher function, one docs-check check'.",
      "failure_scenario": "The owner approves the plan PR believing D4 is their own earlier decision. CI then fails every push between a released report and the author's answers, a cost the owner never weighed.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A1",
      "kind": "advisory",
      "line": 35,
      "problem": "[high] S43-D4 is presented as the owner's decision, but the docs-check *gate* on answers is the author's default. #40's decisions 1\u20134 and its 'Done when' cover blocks and hashes only. #33 decision 7 says every finding gets an answer, not that CI checks it. S41-D6 itself marks 'the check lives in 4.3' as a default. D4 is missing from 'Review notes' (defaults for the owner to confirm), so the owner may approve a new gate without noticing (AGENTS.md 'Ask before growing'). The '\"owner deferred\"' text marker is also the author's invention."
    },
    {
      "evidence": "plan.md:35. test_plan.md:30 fail cases: only 'without an answer', 'deferred without an issue', 'high deferred without owner deferred'. Owner's comment on #33, decision 3: 'blocking \u2026 fixed before merge, or the owner decides; \u2026 medium \u2026 fixed, or deferred with a tracking issue'.",
      "failure_scenario": "An implementation that accepts any of the three words for any kind, and checks the 'owner deferred' text only on `deferred`, passes every planned test. A blocking finding answered 'declined: out of scope' then passes docs-check with no owner decision.",
      "file": "docs/slices/poc-4-3-review-records/test_plan.md",
      "id": "R2-A2",
      "kind": "advisory",
      "line": 30,
      "problem": "[high] D4's rules are incomplete and its tests leave obvious wrong implementations green. Under the owner's scale, blocking means 'fixed before merge, or the owner decides', and medium means 'fixed, or deferred with a tracking issue'. D4 constrains only `high`. So a blocking finding answered `deferred #12` or `declined \u2026` passes, and so does a medium one `declined`. D4 also does not say whether `high` may be `declined` (contested). The owner's 'fixed (where)' is not required either. No test covers `declined` without a reason, a `high` finding `declined`, a blocking finding deferred, or an answer that lists an ID not in the report."
    },
    {
      "evidence": "plan.md:34. test_plan.md:29 fail cases: a changed character, an extra block, a missing block, a missing record. None places a valid block under another attempt's heading.",
      "failure_scenario": "During the one-time hand conversion (D5), the author swaps two rounds' report blocks. Every hash still appears in the log, so a set-based check passes. D4 then validates round 2's answers against round 1's findings and may pass with findings unanswered.",
      "file": "docs/slices/poc-4-3-review-records/test_plan.md",
      "id": "R2-A3",
      "kind": "advisory",
      "line": 29,
      "problem": "[high] D3 checks block hashes against any hash in the log ('matches a prompt_sha256 or report_sha256 of that log'), not against the attempt whose heading the block sits under. The planned tests cannot tell a set comparison from per-attempt binding. D4 reads each attempt's findings from 'its' report block, so a block under the wrong heading makes D4 check answers against the wrong findings. Retries and several reviewers sharing a task file also produce repeated prompt hashes."
    },
    {
      "evidence": "plan.md:34 ('Blocks are found outermost first: the longest fences first'); plan.md:38 (D7). review_slice_3.md:567-569 already wraps prompts in `<details>`, and earlier records put a 'Command' section in the header.",
      "failure_scenario": "An author answers a finding with a fenced command snippet under `#### Answers to \u2026`. docs-check then fails with 'block with no logged hash' (a false red), and the author learns to avoid code in answers, or the implementer adds ad-hoc exemptions.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A4",
      "kind": "advisory",
      "line": 38,
      "problem": "[medium] The plan does not define which fenced blocks are 'blocks'. D3's 'every block must match a logged hash' would fail on any other fence in the record: a code fence in the author's answers, in a rendered report view (findings often quote code with backticks), or in a header or command section. D7 says the check 'ignores rendered views' without saying how it recognises them, and the launcher only 'may' add them. 'Longest fences first' is not how CommonMark pairs fences. A sequential parse that only considers fences directly under `### Attempt` labels is simpler and exact."
    },
    {
      "evidence": "poc-4-1 plan.md:89, 95-96. poc-4-3 plan.md:56-61 (In scope). poc-4-5 plan.md:46.",
      "failure_scenario": "The implementer builds 4.3 before 4.1, so the `high` rule has no `high` findings to test against real reports. Or 4.1's 'until 4.3' state never ends, and rechecks keep depending on git-ignored local files that a fresh clone lacks.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A5",
      "kind": "advisory",
      "line": 56,
      "problem": "[medium] Missing cross-plan pieces and order. 4.1 says the recheck reads the earlier report from `artifacts/reviews/` 'until 4.3 moves it into the record', and names '4.3's check' as a reader of `mode` and `severity_counts`. 4.3's scope covers neither: it does not switch the recheck source and does not use either field. D4 also depends on 4.1's kinds (`high`) and answer format, yet no plan states that 4.1 is built before 4.3. Only S45-D9 orders anything."
    },
    {
      "evidence": "review_slice_3.md:17-18 uses `\"impl:<scratch>/task_r<n>.md:\u2026\"`, a placeholder the author used to keep local paths out. plan.md:71-72: 'No asset changes'.",
      "failure_scenario": "A task prompt says 'compare with /home/<user>/work/agentic-iam-spiffe/\u2026'. The launcher publishes it verbatim, the check cannot allow redaction, and the path stays in history. A one-line prompt-writing rule in AGENTS.md (no local paths in task text), or the launcher refusing absolute paths outside the copy, would prevent it.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A6",
      "kind": "advisory",
      "line": 69,
      "problem": "[medium] Operational details in public records. The launcher now writes task prompts and reports verbatim into a committed record, and hash matching forbids redaction. The only scan is for secret shapes. Task prompts written by the author can contain local absolute paths (scratch directories, home directories). Earlier hand records replaced these with `<scratch>` placeholders, which hash matching no longer allows. 'Assets and holders' says nothing changes."
    },
    {
      "evidence": "plan.md:32 ('under `#### Answers to <attempt id>`') and plan.md:35 give only the three words. Existing answers are tables: review_slice_3.md:549-553.",
      "failure_scenario": "The implementer picks a strict line format. The author's first real answers in a table fail docs-check, or a loose regex accepts 'Fixed? not yet' as `fixed`.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A7",
      "kind": "advisory",
      "line": 35,
      "problem": "[medium] The answer grammar the check parses is not specified: a table row or a list line, the ID column, case ('Fixed.' as in earlier records), and where a reason or issue reference must appear. It is left to the implementer, though authors must write to it and the converted records must match it."
    },
    {
      "evidence": "plan.md:107; delivery_problem_log.md:306 ('Status: Open (preventive actions are inputs for slice 4)'); test_plan.md has no row for the AGENTS.md row.",
      "failure_scenario": "The hand check's retirement and DPL-010's status are never recorded in the repository, and the AGENTS.md row goes unreviewed.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A8",
      "kind": "advisory",
      "line": 107,
      "problem": "[low] Retirement relies on 'a memory note', which is outside the repository and invisible to reviewers. The scope also omits updating DPL-010, whose preventive actions are this slice. 'AGENTS.md's docs-check row names the check' (the owner's Done-when) has no test or review line in the test plan."
    },
    {
      "evidence": "run_independent_review.py:803-805 (parallel `_guarded_attempts`); only the attempt log has a mutex and flock (lines 562-599).",
      "failure_scenario": "Two reviewers finish together; their appends interleave and corrupt both blocks. The check then fails, and the reports exist only in git-ignored artifacts.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-A9",
      "kind": "advisory",
      "line": 32,
      "problem": "[low] Reviewers in a round run in parallel threads (`ThreadPoolExecutor`). D1 has each one append to the same record file, with no stated lock or order, so blocks can interleave and their order can vary between runs."
    },
    {
      "evidence": "plan.md:78 (the hand check already matches all blocks); AGENTS.md frozen-records rule; R2-B2.",
      "failure_scenario": "Without it, the conversion rewrites frozen records and either invents answers or weakens D4 (R2-B2).",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-S1",
      "kind": "simpler_alternative",
      "line": 36,
      "problem": "Drop the one-time conversion (D5). Make the hash check layout-agnostic: every logged prompt and report hash has an exactly matching fenced block in the record, and every attempt-heading block matches its attempt. Apply the per-attempt heading binding and the answers check (D4) only to attempts the new launcher logs, for example those whose start entry has 4.1's `mode`. The existing records already pass the hash part (13/13 and 8/8 by the author's probe), so nothing frozen is rewritten, and D4 never meets the old answer vocabulary."
    },
    {
      "evidence": "The owner's #33 comment, as quoted in the task; this review's withheld `review_attempts.jsonl`; the task note on the round-1 launcher bug.",
      "failure_scenario": "Without an owner decision, the implementer must choose between a permanently red docs-check and an unapproved exemption (R2-B1).",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R2-DC1",
      "kind": "decision_concern",
      "line": 36,
      "problem": "The owner's premise 'Records without an attempt log (slice 1, the plan reviews) are not checked' no longer holds: slice 4's plan reviews have attempt logs, and five of their round-1 reports are lost. The owner should decide whether logged plan-review records are checked, and how a logged attempt whose report was lost is recorded. One option is a one-line exception with an expiry. Another is a log-level 'lost' marker written by the launcher, not the author."
    }
  ],
  "verdict": "no"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| R2-B1 | blocking | fixed: S43-D3 checks only attempts whose start entry has `record_blocks: 1`, written from 4.3 on; S43-D5 says slice 4's plan-review records (with their lost round-1 reports) stay as they are and were checked by hand before the plan PR |
| R2-B2 | blocking | fixed: S43-D5 drops the conversion; the frozen records of slices 2 and 3 are not rewritten, and S43-D4 never meets their old answers |
| R2-B3 | blocking | fixed: the answers live in the record and a recheck logs their hash (4.1 S41-D5); S43-D1 writes the evidence verbatim; S43-D3 fails answers changed after the recheck that read them; the mandate and checklist are reproducible from the base commit; test row "Check: answers after the recheck" |
| R2-B4 | blocking | fixed: S43-D2 scans the full prompt and refuses before the start entry and the call; S43-D1 writes prompt and evidence before the call, so failed, withheld and interrupted attempts have their blocks and no report hash; test rows "Scan before the call" and "Blocks of attempts without a report" |
| R2-A1 | high | fixed: S43-D4's source names the docs-check placement as a default, Review notes list it, and the POC-D6 row states the cost (docs-check red between a report and its answers) |
| R2-A2 | high | fixed: 4.1 S41-D7 gives the allowed answers per severity, and S43-D4 checks them, including a rejected blocking or high answer (needs the next round's `accepted` or an owner link); test row "Check: allowed answers" lists each wrong case |
| R2-A3 | high | fixed: S43-D3 binds each block to the attempt under whose heading it sits; test row "Check: blocks" has a report block under another attempt's heading |
| R2-A4 | medium | fixed: S43-D3 defines a block as the fence right after a `#### Prompt`, `#### Evidence` or `#### Report` label; other fences are ignored; test row "Check: other fences" |
| R2-A5 | medium | fixed: S43-D6 moves the recheck's earlier report to the record's Report block; the order of work (4.1, 4.2, then 4.3) is in the slice index |
| R2-A6 | medium | fixed: S43-D2 refuses a prompt that holds the author's HOME path or the scratch root |
| R2-A7 | medium | fixed: 4.1 S41-D7 specifies the table (`\| <finding id> \| <answer> \|`) and the four first words |
| R2-A8 | low | fixed: S43-D8 (the end of the hand check stated in `AGENTS.md`; DPL-010's status updated); the review-based proof covers them |
| R2-A9 | low | fixed: S43-D1 (writes hold the attempt log's lock); test row "Parallel reviewers" |
| R2-S1 | low | fixed: adopted in S43-D5 (no conversion; the new checks apply to attempts the new launcher logs) |
| R2-DC1 | decision_concern | owner: asked in the plan PR; S43-D5 removes the conflict meanwhile (attempts logged before 4.3, including those with lost reports, are not checked), as a default for the owner to confirm |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "poc-4-1-review-prompts/plan.md:48 (S41-D6, decision_concern goes to the owner whatever its severity); plan.md:49 (S41-D7, 'Medium takes fixed, deferred or rejected'); poc-4-3 plan.md:40 (S43-D4 checks that 'the answer is allowed for its severity (4.1's S41-D7)'); test_plan.md:33 has no decision_concern row.",
      "failure_scenario": "A reviewer reports a decision_concern with severity medium. The author answers it `owner: <link>`, as S41-D6 requires, and docs-check fails because medium does not allow `owner`. To get green, the author relabels it `deferred: #N` or `rejected: \u2026`. The record then shows a decision for the owner as settled by the author, which the rulebook forbids. Fix: allow `owner:` for every decision_concern (or for every severity) in S41-D7, and add a test row.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R3-B1",
      "kind": "blocking",
      "line": 40,
      "problem": "Contradiction between the answer rules S43-D4 enforces and the decision-concern rule. 4.1's S41-D6 says 'A decision_concern goes to the owner, whatever its severity.' S41-D7, which S43-D4 checks, allows `owner:` only for blocking, high and low. Medium gets only `fixed`, `deferred` or `rejected`. So a medium decision concern has no allowed answer that says what the rules require (send it to the owner). The test row 'Check: allowed answers' has no decision-concern case."
    },
    {
      "evidence": "plan.md:37-39; the launcher appends the start entry before call_reviewer (environment fact, plan.md:86).",
      "failure_scenario": "The launcher writes the record section, then crashes or is killed before appending the start entry. docs-check fails on an orphan heading that the author must delete by hand. Fix: state the order (start entry, then blocks, under the same lock). It can be a note for the implementation.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R3-A1",
      "kind": "advisory",
      "line": 37,
      "problem": "[low] S43-D1 writes Prompt and Evidence 'before the call', and S43-D2 refuses 'before the start entry'. The plan does not say whether the blocks are written before or after the start entry. If they are written first and the launcher dies before the start entry, the heading has no logged attempt. S43-D3 then fails it ('a block under an attempt heading with no logged attempt fails'), and the record stays permanently red unless the author edits it by hand."
    },
    {
      "evidence": "R2-B1: accepted (poc-4-3 plan.md D3, D5 and environment facts)\nR2-B2: accepted (poc-4-3 plan.md D5, Retirement)\nR2-B3: accepted (poc-4-3 plan.md D1, D3; poc-4-1 plan.md S41-D5 and the hidden-state row for the answers section; test_plan.md row 'Check: answers after the recheck')\nR2-B4: accepted (poc-4-3 plan.md D1, D2; test_plan.md rows 'Scan before the call' and 'Blocks of attempts without a report'; scripts/run_independent_review.py)\nR2-A1: accepted (poc-4-3 plan.md D4 Source, Review notes, POC-D6 table)\nR2-A2: accepted, with the new contradiction R3-B1 (poc-4-1 plan.md S41-D6 and S41-D7; poc-4-3 plan.md D4; test_plan.md 'Check: allowed answers')\nR2-A3: accepted (poc-4-3 plan.md D3; test_plan.md 'Check: blocks')\nR2-A4: accepted (poc-4-3 plan.md D3; test_plan.md 'Check: other fences')\nR2-A5: accepted (poc-4-3 plan.md D6 and Order of work; docs/slices/README.md:16; poc-4-1 plan.md S41-D5)\nR2-A6: accepted (poc-4-3 plan.md D2; scripts/run_independent_review.py:303, 803)\nR2-A7: accepted (poc-4-1 plan.md S41-D7)\nR2-A8: accepted (poc-4-3 plan.md D8; test_plan.md Review-based proof)\nR2-A9: accepted (poc-4-3 plan.md D1; test_plan.md 'Parallel reviewers')\nR2-S1: accepted (poc-4-3 plan.md D5)\nR2-DC1: accepted as an open question for the owner (poc-4-3 plan.md D5, Review notes)",
      "failure_scenario": "None. This finding only records how each earlier answer was accounted for.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
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
| R3-B1 | blocking | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-3-review-records/plan.md, docs/slices/poc-4-3-review-records/test_plan.md: S41-D7 allows `owner:` at every severity and requires it for a `decision_concern`; S43-D4 checks it; the "Check: allowed answers" row has a medium decision concern answered `owner:` (passes) and one answered `rejected` (fails) |
| R3-A1 | low | fixed: docs/slices/poc-4-3-review-records/plan.md: S43-D1 appends the start entry first and the blocks after it, both under the log's lock |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |

## Round 4

### Attempt plan/c1/r4/plan/1

Commit `c352fce`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-3-review-records/plan.md` `4790d7d149d7`, `docs/slices/poc-4-3-review-records/test_plan.md` `1a6b41bf8240`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 4 of the plan review of slice 4.3 (review records and their check, #40), a recheck of your earlier report (round 3, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it. (Slice 4.1 replaces this with an `accounted` field; until then this finding carries it.)
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## Your earlier report (round 3, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "poc-4-1-review-prompts/plan.md:48 (S41-D6, decision_concern goes to the owner whatever its severity); plan.md:49 (S41-D7, 'Medium takes fixed, deferred or rejected'); poc-4-3 plan.md:40 (S43-D4 checks that 'the answer is allowed for its severity (4.1's S41-D7)'); test_plan.md:33 has no decision_concern row.",
      "failure_scenario": "A reviewer reports a decision_concern with severity medium. The author answers it `owner: <link>`, as S41-D6 requires, and docs-check fails because medium does not allow `owner`. To get green, the author relabels it `deferred: #N` or `rejected: \u2026`. The record then shows a decision for the owner as settled by the author, which the rulebook forbids. Fix: allow `owner:` for every decision_concern (or for every severity) in S41-D7, and add a test row.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R3-B1",
      "kind": "blocking",
      "line": 40,
      "problem": "Contradiction between the answer rules S43-D4 enforces and the decision-concern rule. 4.1's S41-D6 says 'A decision_concern goes to the owner, whatever its severity.' S41-D7, which S43-D4 checks, allows `owner:` only for blocking, high and low. Medium gets only `fixed`, `deferred` or `rejected`. So a medium decision concern has no allowed answer that says what the rules require (send it to the owner). The test row 'Check: allowed answers' has no decision-concern case."
    },
    {
      "evidence": "plan.md:37-39; the launcher appends the start entry before call_reviewer (environment fact, plan.md:86).",
      "failure_scenario": "The launcher writes the record section, then crashes or is killed before appending the start entry. docs-check fails on an orphan heading that the author must delete by hand. Fix: state the order (start entry, then blocks, under the same lock). It can be a note for the implementation.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R3-A1",
      "kind": "advisory",
      "line": 37,
      "problem": "[low] S43-D1 writes Prompt and Evidence 'before the call', and S43-D2 refuses 'before the start entry'. The plan does not say whether the blocks are written before or after the start entry. If they are written first and the launcher dies before the start entry, the heading has no logged attempt. S43-D3 then fails it ('a block under an attempt heading with no logged attempt fails'), and the record stays permanently red unless the author edits it by hand."
    },
    {
      "evidence": "R2-B1: accepted (poc-4-3 plan.md D3, D5 and environment facts)\nR2-B2: accepted (poc-4-3 plan.md D5, Retirement)\nR2-B3: accepted (poc-4-3 plan.md D1, D3; poc-4-1 plan.md S41-D5 and the hidden-state row for the answers section; test_plan.md row 'Check: answers after the recheck')\nR2-B4: accepted (poc-4-3 plan.md D1, D2; test_plan.md rows 'Scan before the call' and 'Blocks of attempts without a report'; scripts/run_independent_review.py)\nR2-A1: accepted (poc-4-3 plan.md D4 Source, Review notes, POC-D6 table)\nR2-A2: accepted, with the new contradiction R3-B1 (poc-4-1 plan.md S41-D6 and S41-D7; poc-4-3 plan.md D4; test_plan.md 'Check: allowed answers')\nR2-A3: accepted (poc-4-3 plan.md D3; test_plan.md 'Check: blocks')\nR2-A4: accepted (poc-4-3 plan.md D3; test_plan.md 'Check: other fences')\nR2-A5: accepted (poc-4-3 plan.md D6 and Order of work; docs/slices/README.md:16; poc-4-1 plan.md S41-D5)\nR2-A6: accepted (poc-4-3 plan.md D2; scripts/run_independent_review.py:303, 803)\nR2-A7: accepted (poc-4-1 plan.md S41-D7)\nR2-A8: accepted (poc-4-3 plan.md D8; test_plan.md Review-based proof)\nR2-A9: accepted (poc-4-3 plan.md D1; test_plan.md 'Parallel reviewers')\nR2-S1: accepted (poc-4-3 plan.md D5)\nR2-DC1: accepted as an open question for the owner (poc-4-3 plan.md D5, Review notes)",
      "failure_scenario": "None. This finding only records how each earlier answer was accounted for.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
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
| R3-B1 | blocking | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-3-review-records/plan.md, docs/slices/poc-4-3-review-records/test_plan.md: S41-D7 allows `owner:` at every severity and requires it for a `decision_concern`; S43-D4 checks it; the "Check: allowed answers" row has a medium decision concern answered `owner:` (passes) and one answered `rejected` (fails) |
| R3-A1 | low | fixed: docs/slices/poc-4-3-review-records/plan.md: S43-D1 appends the start entry first and the blocks after it, both under the log's lock |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "plan.md:37 (S43-D1: 'The start entry is appended first and the blocks after it, both under the attempt log's lock'); plan.md:39 (S43-D3: 'its `### Attempt` heading is in the record'); test_plan.md:27.",
      "failure_scenario": "SIGKILL lands between the log append and the record write. The lock is released when the process dies. docs-check then fails on a logged attempt that has no heading. The window is tiny and the failure is loud, so this is not a false green. Note for the implementation: write the heading and the status line in the same locked step as the start entry, or let the check accept a logged attempt with no end entry and no heading as interrupted.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R4-A1",
      "kind": "advisory",
      "line": 37,
      "problem": "[low] Fixing R3-A1 reversed the order but left a small window open. With the start entry appended first, a launcher killed after the start entry and before the blocks leaves a logged attempt (`record_blocks: 1`) with no `### Attempt` heading. S43-D3 fails that, because the heading must be in the record. The record then stays red until the author edits it by hand. The test row 'Blocks of attempts without a report' covers a kill after the blocks exist, not this window."
    },
    {
      "evidence": "plan.md:7.",
      "failure_scenario": "A reader may take the plan for the round-2 revision. This is only a documentation mismatch.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
      "id": "R4-A2",
      "kind": "advisory",
      "line": 7,
      "problem": "[low] The status line still says 'revised after plan review round 2', although the plan was revised again for round 3's findings R3-B1 and R3-A1."
    },
    {
      "evidence": "R3-B1: accepted (poc-4-1 plan.md S41-D6 and S41-D7 at lines 48-49: `owner` is now allowed at every severity and required for decision_concern; poc-4-3 plan.md S43-D4 at line 40; test_plan.md:33 has a medium decision_concern answered `owner:` that passes and a decision_concern answered `rejected` that fails)\nR3-A1: accepted (poc-4-3 plan.md S43-D1 at line 37: start entry first, then the blocks, under the log's lock; the remaining window is reported as R4-A1)\nACCOUNTED: accepted (stand-in only, until S41-D8's field exists; poc-4-1 plan.md:50)",
      "failure_scenario": "None. This finding only records how each answer was accounted for.",
      "file": "docs/slices/poc-4-3-review-records/plan.md",
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
| R4-A1 | low | fixed: docs/slices/poc-4-3-review-records/plan.md: S43-D1 writes the start entry, the heading and the status line in one locked step, and the blocks after them |
| R4-A2 | low | fixed: docs/slices/poc-4-3-review-records/plan.md: the status line names rounds 2, 3 and 4 |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
