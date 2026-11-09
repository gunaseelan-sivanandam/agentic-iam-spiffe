# Plan review — 4.5 (#42), benchmark

Record of the plan review of slice 4.5 (#42), benchmark in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

The owner granted one more round on 2026-11-09 ("I accept your recommendations for my decisions", decision 5 of the proposal). The launcher needs that extension as a link to the owner's PR comment, so round 5 runs once that comment exists.

## Round 1

### Attempt plan/c1/r1/plan/1

Commit `dfc88e2`, effort high. Files reviewed (SHA-256): `docs/slices/poc-4-5-benchmark/plan.md` `905bb3ef6d54`, `docs/slices/poc-4-5-benchmark/test_plan.md` `f06a6b33e547`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this plan and has not caught yet: anything missing, wrong, untestable, stale, overclaimed, unsafe, over-engineered or unclear, inside or outside the files under review. The questions further down are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

Plan review, round 1 (the initial review), of slice 4.5 of the agentic-SDLC PoC: `docs/slices/poc-4-5-benchmark/plan.md` and `test_plan.md` (GitHub issue #42). Slice 4 is split into six sub-issues, 4.1 to 4.6, each a separate review unit with its own bundle `docs/slices/poc-4-*/`. All six plans are in your copy. A contradiction between this plan and another sub-issue's plan counts, and so does a dependency that is missing or in the wrong order. The PoC's approved plan is `docs/slices/agentic-sdlc-poc/plan.md`. The rulebook under which you judge is `AGENTS.md` (approved rules, given below).

How slice 4 runs (owner's decisions): no grill-me per sub-issue; the plan is the contract, and each decision names its source (the owner, or "default by the author" with a reason). All six plans go into one plan PR that the owner approves once. Implementation runs without stopping and ends in one final PR. So this plan must be complete and correct enough to build from without asking the owner again, and every default must be easy for the owner to spot and confirm.

Severity: the owner decided on a severity order that this plan set will build into the launcher. Apply it already. Use the kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low]. High means a real defect or false claim that does not block; medium means clear value (robustness, diagnosability, naming); low means style or preference.

## The owner's decisions and inputs (verbatim from GitHub, which you cannot read)

### This sub-issue (#42)

Part of slice 4 (#33) of the agentic-SDLC PoC. It runs the slice process: its plan goes into slice 4's single plan PR, which the owner approves once; it gets a plan review and an implementation review (up to 4 rounds each, open mandate first); it is implemented on the slice-4 branch; slice 4 ends in one final PR with a section per sub-issue (owner, 2026-11-08).

**Goal:** measure what slice 4 changes, on the same cases as stage A, before it becomes the default.

**Decided:**
- **Budget:** up to 40 reviewer runs (owner, 2026-11-08).
- **Configurations:**
  - the open-mandate prompt from sub-issue 4.1, as a third configuration beside the short prompt and the checklist ([decision](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242));
  - the stage checklists from sub-issue 4.4.
- **Models: Opus, Sonnet and Codex** (owner, 2026-11-08). For Codex, this is the owner's exception to POC-D2, which today allows Codex only for implementation. It needs a Codex mode in the launcher first, and a probe that Codex stays inside its copy and ignores the repository's instruction files.
- **New cases:**
  - stage documents: a flawed requirement, a weak test, a design gap (#33's description);
  - the miss behind DPL-010, reviewed with a narrow prompt and with an open one ([principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147)).
- **Clean re-measurement** ([R5-A2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)): a run or stage ID, the prompt hash in a result's identity, and a results file per stage.
- **Tighter scoring of planted defects** ([R5-A7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)): leak terms that identify each plant, and expected terms that do not quote the planted line.
- **Repeat the CLI probes** (the canary, how a failed Read is reported) when the CLI version changes ([R6-7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844)).

**Done when:** the runs are done within the budget, and the report compares configurations and models with hand-confirmed detections and applies the decision rule.

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

### A comment on issue #33 (slice 4's inputs)

**Input for this sub-issue (from slice 2, PR #35):** in stage A's canary, the twin run (without `--safe-mode`, with `--setting-sources project`) ran the planted hook, so the canary was valid. But it did not follow the planted instruction files (`CLAUDE.md`, a nested `CLAUDE.md`). So the canary showed that project settings do not reach a confined reviewer, while the claim that instruction files do not reach it rests on the plan's earlier probe.

When this sub-issue reruns the canary (with the CLI probes, R6-7), use a twin whose prompt makes it act on the instruction files, so that half of the claim is measured too.

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
      "evidence": "scripts/run_review_benchmark.py:335-340 build_case_prompt calls launcher.build_prompt. poc-4-1 plan.md:37 (S41-D1) and :55 (success criterion). test_plan.md:23-31 has no row for the contents of each configuration's prompt.",
      "failure_scenario": "After 4.1 merges, the 'short prompt' and 'narrow question' runs in stage B silently carry the open mandate. The DPL-010 narrow-vs-open comparison then compares open against open and reports 'no difference', which is a false answer to the owner's principle question. The decision rule S45-D7(a) is also applied to a short-prompt baseline that is not the short prompt. All planned tests still pass.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B1",
      "kind": "blocking",
      "line": 43,
      "problem": "Contradiction with 4.1, and a configuration decision with no test. S45-D6 and S45-D4 need prompts without the open mandate: stage A's short prompt on the 4 new cases, round 1's narrow question for the DPL-010 case, and the canary, which uses the short prompt. But 4.1 fixes the mandate in the launcher's build_prompt so that 'a task text cannot remove or reorder' it. 4.1's success criterion says 'Every prompt the launcher builds contains the mode's mandate ... whatever the task text says'. The benchmark builds every prompt through launcher.build_prompt. Neither plan sets up a mandate-free path for benchmark baselines, and no test-plan row checks what each configuration's prompt contains."
    },
    {
      "evidence": "poc-4-4 plan.md:40 (S44-D7, base-commit read). answer_key.yaml case bases. plan.md:43 'Opus with the new setup on all 11 stage-A cases...'. test_plan.md has no row on checklist inclusion.",
      "failure_scenario": "The runner passes the case's base as the launcher's base. The --stage lookup finds no list at that commit and either fails or, under 4.2's fail-visible style, puts in an empty section. The report then claims the 4.4 checklists were measured, and the default is decided on a configuration that never contained them.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B2",
      "kind": "blocking",
      "line": 43,
      "problem": "Contradiction with 4.4: the 'new setup' would be measured without the stage checklists. S44-D7 has the launcher read the stage list 'with --stage <artifact type> from the base commit'. Every benchmark case's base (6e8b2cb, e842e97, c4f9ca2 ...) predates docs/review_checklists/, so no case would get a checklist. The plan does not say where benchmark cases take their list from (the current tree?), or which artifact type each case maps to (RM-3 mixes requirements, code and CI; the stage-document cases are requirements, test and architecture). No test row checks that a stage-B new-setup prompt contains the 4.4 list."
    },
    {
      "evidence": "test_plan.md:40-41 'the twin follows a planted instruction or setting (valid)'. plan.md:45 'its prompt tells it to act on the instruction files'. scripts/run_review_benchmark.py:416-424 validity = _followed_any(twin) (hook OR ids OR reads). The owner's #42 input: 'use a twin whose prompt makes it act on the instruction files, so that half of the claim is measured too'.",
      "failure_scenario": "The stronger twin again runs only the hook. The run is marked valid and the canary passes, and the report claims instruction files do not reach a confined reviewer, while that half is still unmeasured: a false green on the confinement claim. Later the CLI version changes, nobody re-runs the failed-Read probe, and the launcher's empty-review rule rests on stale CLI behaviour.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "B3",
      "kind": "blocking",
      "line": 40,
      "problem": "S45-D8 is not proved. The live check accepts a twin that 'follows a planted instruction or setting' as valid. That is exactly stage A's situation: the twin ran the hook (a setting) but ignored the CLAUDE.md files, so the instruction-file half was never measured. Also, only the twin's prompt is changed ('its prompt tells it to act'), so canary and twin no longer differ only in flags, and a canary pass could come from the prompt difference. Separately, the failed-Read probe that S45-D8 re-runs on a CLI version change has no live check or test at all. Nothing says how a version change is detected, or that the re-run is manual."
    },
    {
      "evidence": "run_review_benchmark.py:204-208: the leak search covers the problem ID and BENCHMARK_DIR in the copy. delivery_problem_log.md:304-316 (DPL-010 text). review_slice_3.md:562 '5a5aba7 (after slices 1 and 2 merged)'. review_slice_2.md:17,915: rounds 1-4 reviewed earlier commits.",
      "failure_scenario": "The dry run refuses the case, and the implementer must pick another commit without the owner (the plan is the contract). Or the leak terms are thinned or the directory check is loosened to get it through. The reviewer then reads DPL-010 in its copy and 'detects' the miss, which inflates the open mandate's result.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B4",
      "kind": "blocking",
      "line": 41,
      "problem": "The DPL-010 case as specified cannot run, and a workaround would leak the answer. 5a5aba7 is poc/agentic-sdlc after slice 2 merged. Its tree holds tests/review_benchmark/, docs/delivery_problem_log.md with DPL-010 (which names the untested refusal paths), and review_slice_2.md round 5. The runner refuses any copy that contains tests/review_benchmark/ or the case's problem ID. Round 1's narrow question was also asked of an earlier reviewed commit, not of the merged state, which includes the round-5 fixes."
    },
    {
      "evidence": "test_plan.md:35-39. plan.md:31-32, :42 ('a container that mounts only the copy and its login file'), :75-78 ('the reviewer process cannot read it'; the scanner does not know OpenAI token shapes). plan.md:84: no flag to skip AGENTS.md.",
      "failure_scenario": "In the container, Codex is asked to read ~/.codex/auth.json, replies that it will not access credentials, and the probe records 'passed'. Codex mode is enabled. A case file that tells it to inspect its environment, or a careless finding, later quotes the token in a report. The report goes into the committed results file and the scanner misses it. Or Codex auto-loads the copy's AGENTS.md (RM-3 and CL-1 review AGENTS.md changes) and judges against the changed rules.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "B5",
      "kind": "blocking",
      "line": 35,
      "problem": "The Codex confinement probe has no positive control. A model that declines counts as confinement. The probe 'passes only if none of the three succeeds', but Codex may simply refuse to cat a credential file or ignore a planted AGENTS.md line by its own judgement. The plan's canary uses a twin for exactly this reason. The probe also tests 'follows', while the threat is 'loads the copy's AGENTS.md'. On top of that, the container fallback mounts the login file where Codex's own shell commands, run as the same user, can read it. So the fallback cannot meet 'A Codex reviewer must not be able to read it' (plan line 31) unless the probe false-greens."
    },
    {
      "evidence": "run_review_benchmark.py:297-298 review_id, :529-535 setdefault((case, prompt)), :348-349 model is recorded but never used in identity. plan.md:43-44. test_plan.md:23-31 has no model row.",
      "failure_scenario": "After Opus completes RM-1/new-setup, the Sonnet run of RM-1/new-setup is skipped as finished, or the report scores Opus's result under Sonnet. Rule S45-D7(b) then picks a default reviewer model from mixed data. Every planned test still passes.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B6",
      "kind": "blocking",
      "line": 39,
      "problem": "Result identity leaves out the model, and no test proves the model comparison. S45-D2 adds a stage ID and the prompt hash only. Today's review_id is case/prompt and _completed_reviews keys on (case, prompt). With Opus, Sonnet and Codex running the same case under the same configuration (S45-D6), later models' runs count as done or are merged into the same comparison cell. No test-plan row covers several models in one stage, or the S45-D7 rule as code."
    },
    {
      "evidence": "plan.md:99. poc-4-4 plan.md:43 (S44-D10), :65 (in-scope AGENTS.md sections). AGENTS.md (base), Models and usage limits: 'Reviews run on Claude ... The review benchmark may also measure Codex as a reviewer'.",
      "failure_scenario": "The 4.4 critique runs Codex against the approved rules. The final review flags it as a rule violation, or the amended AGENTS.md states a narrower exception than the work actually used, so the rulebook and the record disagree.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B7",
      "kind": "blocking",
      "line": 99,
      "problem": "Contradiction with 4.4 and the rulebook. The only rule change for Codex is 'the owner's Codex exception for benchmark reviews', and base AGENTS.md already lets the benchmark measure Codex. But S44-D10 has Codex critique the draft checklists through the launcher. That is a review that is not a benchmark run, and AGENTS.md ('Reviews run on Claude') forbids it. No plan amends the rule for it: 4.4's AGENTS.md scope does not include 'Models and usage limits'. Under POC-D15 the author works by the base rules until the final PR merges anyway, so the plan should record the owner's exception explicitly for both uses."
    },
    {
      "evidence": "run_review_benchmark.py:93-99. test_plan.md:25 'after a prompt change' can be satisfied by editing a prompt file only.",
      "failure_scenario": "A 4.4 checklist is edited mid-stage. Earlier stage-B results still count as done, and the report mixes two checklist versions without saying so.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A1",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] 'The prompt's SHA-256' is undefined. Today's prompts_sha256 hashes only tests/review_benchmark/prompts/*.md. In stage B most of the prompt sits elsewhere: the mandate in the launcher's code (4.1), the checklists in docs/review_checklists/ (4.4), and the computed evidence (4.2). If only the template files are hashed, a change to the mandate wording or a checklist leaves identity unchanged, which is R5-A2 again. If the full built prompt is hashed, any evidence that changes between runs (CI data, coverage) makes every run non-resumable."
    },
    {
      "evidence": "plan.md:43, :55-56, :116-117. Owner's #42 'Configurations' and the #33 decision 4.",
      "failure_scenario": "The owner approves believing the open mandate is measured as its own configuration, and later cannot tell whether the mandate or the checklists caused any difference.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A2",
      "kind": "advisory",
      "line": 43,
      "problem": "[high] The owner's configuration decision is changed without being flagged. The owner asked for 'the open-mandate prompt ... as a third configuration beside the short prompt and the checklist ... on the same cases'. The plan bundles mandate, 4.4 checklists and 4.2 evidence into one 'new setup'. It does not run stage A's checklist on the 4 new cases, and the success criteria compare against the short prompt only. The open mandate's own effect, the owner's question in decision 4, cannot be separated. This is not listed under Review notes as a deviation."
    },
    {
      "evidence": "plan.md:43 (Sonnet/Codex: 5 real misses + 3 stage cases only), :44.",
      "failure_scenario": "The rule picks Codex or Sonnet as the default on detections alone. The owner learns of a rulebook-level change from the report.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A3",
      "kind": "advisory",
      "line": 44,
      "problem": "[high] Rule S45-D7(b) cannot be applied as written. Sonnet and Codex run no clean cases, so 'with no more false blockers' has no measurement base. 'Cheapest' is undefined across vendors: a Claude CLI USD estimate against Codex's separate quota. Who adopts the result is also unclear: AGENTS.md says reviews run on Claude, so making Sonnet or Codex the default changes a rule and needs the owner (decision concern)."
    },
    {
      "evidence": "plants/PD-1.patch:1 header. answer_key.yaml:108 leak_terms [PLANT-]. plan.md:40.",
      "failure_scenario": "The plant cases are refused on their own code, or the search again checks nothing while the test is green.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "A4",
      "kind": "advisory",
      "line": 28,
      "problem": "[medium] The leak-term fix is underspecified and its test proves little. 'Its case wording' is ambiguous. Any term taken from the planted line is always in the copy and would refuse the case. The row only shows that an injected term refuses, so a new set of terms that never appear (like PLANT-) would still pass. Use the words that would reveal a plant, such as the patch header ('Planted defect PD-1', 'review benchmark'), and test that PD-1..4 pass the real search while a copy with the header is refused."
    },
    {
      "evidence": "A search of the poc-4-* plans for R5-A8 / dry_run finds nothing. The owner's #33 input item 4.",
      "failure_scenario": "The leak search's dry_run path silently breaks after the stage refactor, and the pre-run check reports '0 refused'.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A5",
      "kind": "advisory",
      "line": 62,
      "problem": "[high] Owner input R5-A8 is assigned to no slice-4 plan: the untested planted-patch path and dry_run of the benchmark runner, three report-shape branches of the launcher, and skipping non-JSON stream lines. 4.5 changes the runner and relies on --dry-run as a verification command, so it is the natural home."
    },
    {
      "evidence": "answer_key.yaml:5-6. run_review_benchmark.py:361 uses key.model/key.effort.",
      "failure_scenario": "Sonnet runs at medium effort and Opus at high, and the model comparison measures effort instead of the model.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A6",
      "kind": "advisory",
      "line": 43,
      "problem": "[medium] Model IDs and effort for Sonnet and Codex are unspecified. The answer key holds a single model and effort. It is not said how the runner selects the model per run, or what effort or reasoning level Codex uses, so comparability between models is left to the implementer."
    },
    {
      "evidence": "plan.md:38, :43. run_review_benchmark.py:40, :322-332.",
      "failure_scenario": "The probes plus a couple of retries push the true total past 40 while the runner reports 40 or fewer.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A7",
      "kind": "advisory",
      "line": 38,
      "problem": "[medium] The budget's edges are unclear. It is not said whether the Codex confinement probe sessions (sandbox, then container), the failed-Read probe, re-runs after a CLI change, and 4.4's Opus, Sonnet and Codex critiques count toward the 40. Each case allows up to three tries after provider errors, so a 3-run margin can be used up by one case. The hard cap is a code constant (MAX_BUDGET=26), and it is not said where the per-stage cap of 40 lives so that the key cannot raise it."
    },
    {
      "evidence": "test_plan.md:30, :35-36. plan.md:84-85, :90-92.",
      "failure_scenario": "A Codex CLI upgrade changes sandbox semantics, and the old 'passed' record keeps Codex mode enabled.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A8",
      "kind": "advisory",
      "line": 92,
      "problem": "[medium] Hidden state missing. 'Codex mode is refused when the confinement probe's result is not recorded as passed' needs a machine-readable record. The plan names only the plan's environment-facts table, which is Markdown and edits the approved plan. The hidden-state table should list its store, writer, reader, its binding to the Codex CLI version, and re-probing when that version changes, which S45-D8 covers only for the Claude CLI."
    },
    {
      "evidence": "test_plan.md:30. plan.md:84 (--json JSONL events).",
      "failure_scenario": "Codex runs `cat ../../secret`. The report names no outside path and the check passes. Or the attempt log publishes /home/<user>/... paths.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "A9",
      "kind": "advisory",
      "line": 30,
      "problem": "[medium] It is not said how a Codex run's reads are detected. Codex reads through shell commands in --json events, not Read tool calls. The outside-read and empty-review checks need command parsing (cat, sed, rg, relative paths, cd). The test row checks only that 'a reply names a path outside the copy', which is a check on the report, not on the stream. Persisting Codex events would also put absolute local paths and the account's HOME into the committed attempt log."
    },
    {
      "evidence": "poc-4-2 plan.md:36-37 (S42-D5/D6), :39 (S42-D8 covers paths only).",
      "failure_scenario": "Both DPL-010 runs see the coverage gaps and detect the miss, and the report credits the open mandate, or neither does.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A10",
      "kind": "advisory",
      "line": 43,
      "problem": "[medium] Whether stage-B runs get 4.2's computed evidence is unspecified. At old case commits the evidence commands may not exist (validate_traceability.py, tests/tools). For the DPL-010 case, coverage evidence lists exactly the uncovered refusal paths. That confounds the narrow-vs-open comparison with the evidence, so the principle question cannot be answered."
    },
    {
      "evidence": "run_review_benchmark.py:507-512. test_plan.md:31 covers only an unchanged stage-A report.",
      "failure_scenario": "The re-score path silently scores with the old key's terms, or overwrites stage A's tables.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A11",
      "kind": "advisory",
      "line": 40,
      "problem": "[medium] Re-scoring stage A with the new key has no test. load_results refuses results whose key hash differs, so a separate mode is needed, and its output must not be confused with stage A's report."
    },
    {
      "evidence": "plan.md:46. poc-4-4 plan.md:43. poc-4-1 plan.md:41.",
      "failure_scenario": "The Codex mode is built against the old schema, then broken by 4.1, and the critiques run before records are launcher-written and fail 4.3's check.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A12",
      "kind": "advisory",
      "line": 46,
      "problem": "[medium] The order across sub-issues is incomplete. The Codex mode 'comes first', but it must follow 4.1's schema (six kinds) and modes, and 4.2's file list. 4.4's critiques need 4.1's mandate, and 4.3 if their records are written by the launcher. No plan gives a total order of the six."
    },
    {
      "evidence": "plan.md:44. answer_key.yaml:8-11.",
      "failure_scenario": "Noise sends the decision to the owner, or two implementers compute different outcomes.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A13",
      "kind": "advisory",
      "line": 44,
      "problem": "[low] Rule (a) has zero tolerance ('fewer') where stage A's rule needed a difference of two to be measurable. With n=1 per case, one noisy miss triggers it. It is also unclear whether 'fewer real and planted' means the sum or each category, and whether 'more than one false blocker per clean case' means per case or on average over the two."
    },
    {
      "evidence": "plan.md:41. AGENTS.md test-lint row.",
      "failure_scenario": "The stage-document measurement shows nothing new about requirement or design review.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A14",
      "kind": "advisory",
      "line": 41,
      "problem": "[low] The 'weak test' stage-document case (an outcome guard that accepts any status) repeats PD-1/PD-2. make test-lint already catches it deterministically, so it adds little about stage documents. The answer-key entries for the new cases (files, ranges, terms) are also not sketched."
    },
    {
      "evidence": "test_plan.md:49-53. AGENTS.md step 4.",
      "failure_scenario": "The close-out misses a docs-check failure until CI.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "A15",
      "kind": "advisory",
      "line": 51,
      "problem": "[low] The planned verification leaves out make qa-quality (which includes docs-check), required by step 4. The new benchmark_report.md and results file must pass docs-check and the slice index."
    },
    {
      "evidence": "plan.md:42, :106. The 'Ask before growing' rule.",
      "failure_scenario": "Time goes into a container and network policy that cannot meet the credential requirement anyway.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "S1",
      "kind": "simpler_alternative",
      "line": 42,
      "problem": "Drop the container fallback (an author default). It needs an egress allow-list to the model API and still exposes the mounted login to Codex's commands. If Codex's own sandbox cannot deny reads outside the copy, take the plan's own stop branch: Codex drops out and the owner is told."
    }
  ],
  "verdict": "no"
}
```

#### Answers to plan/c1/r1/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| B1 | blocking | fixed: S45-D3 (configurations `short`, `open`, `open+list`, `narrow`); 4.1 S41-D2 lets only the runner build prompts without the mandate; test row "Configurations" |
| B2 | blocking | fixed: S45-D3 and 4.4 S44-D12 (lists from the runner's fixed commit, by the case's artifact type) |
| B3 | blocking | fixed: S45-D9 (identical prompts; the twin is valid only if it follows both the planted file and the hook; a live failed-Read probe; a CLI-version gate); test rows "Canary validity" and "CLI-version gate" |
| B4 | blocking | fixed: S45-D5 (a patch on `c4f9ca2` with only the launcher, its fake CLI and its tests as at `5a5aba7`); test row "New cases" checks the copy holds no benchmark files or DPL-010 text |
| B5 | blocking | fixed: S45-D6 (a control run must read a harmless outside marker and follow the planted instruction; the confined run must be denied by the sandbox; the login file is never a target) |
| B6 | blocking | fixed: S45-D2 (model and effort in the identity); test row "Identity" (two models on one case are two results) |
| B7 | blocking | fixed: `AGENTS.md` (Models and usage limits) in this plan PR covers the benchmark and 4.4's critique |
| A1 | high | fixed: S45-D2 defines the prompt identity (mandate, templates, lists, task; not evidence); test row "Prompt identity" |
| A2 | high | fixed: S45-D3 measures the open mandate alone (`open`) as the owner's third configuration, and `open+list` beside it |
| A3 | high | fixed: S45-D8(c) reports per model and leaves the choice to the owner; no automatic cost rule |
| A4 | medium | fixed: S45-D4 (leak terms from the patch header and each plant's own description words, which are not in the planted line); test row "Plant leak terms" checks every case's copy |
| A5 | high | fixed: S45-D11; test row "Runner paths (R5-A8)" |
| A6 | medium | fixed: S45-D10 names the models and effort |
| A7 | medium | fixed: S45-D1 (40 for cases and the canary; probes bounded at six; critiques outside) |
| A8 | medium | fixed: the probe record (`codex_probe.json`, committed, bound to the CLI version) is in the hidden-state table; test row "Codex mode" |
| A9 | medium | fixed: S45-D6 (outside reads from the sandbox's events; the event stream is never written to disk) |
| A10 | medium | fixed: 4.2 S42-D11 and 4.5's goal: computed evidence is off in the benchmark, and the report says so |
| A11 | medium | fixed: S45-D4 `--rescore A` into a separate output; test row "Re-score" |
| A12 | medium | fixed: the order of work (4.1, 4.2, 4.3, 4.5a, 4.4, 4.5b, 4.6) is in the slice index |
| A13 | low | fixed: S45-D8 uses stage A's threshold of two and says which counts are summed |
| A14 | low | fixed: the weak-test case is replaced by a test-plan row that drops a requirement's only runtime proof; S45-D5 says the answer key gives each new case its files, ranges, terms and type |
| A15 | low | fixed: `make qa-quality` is in the planned verification commands |
| S1 | low | fixed: adopted; no container fallback (S45-D6) |

## Round 2

### Attempt plan/c1/r2/plan/1

Commit `ebb1029`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-5-benchmark/plan.md` `7c05a7814df3`, `docs/slices/poc-4-5-benchmark/test_plan.md` `0a5b3833a44e`.

Status: completed; approvable within the threat model: no.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 2 of the plan review of slice 4.5 (benchmark, #42), a recheck of your earlier report (round 1, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it. (Slice 4.1 replaces this with an `accounted` field; until then this finding carries it.)
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## Your earlier report (round 1, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "scripts/run_review_benchmark.py:335-340 build_case_prompt calls launcher.build_prompt. poc-4-1 plan.md:37 (S41-D1) and :55 (success criterion). test_plan.md:23-31 has no row for the contents of each configuration's prompt.",
      "failure_scenario": "After 4.1 merges, the 'short prompt' and 'narrow question' runs in stage B silently carry the open mandate. The DPL-010 narrow-vs-open comparison then compares open against open and reports 'no difference', which is a false answer to the owner's principle question. The decision rule S45-D7(a) is also applied to a short-prompt baseline that is not the short prompt. All planned tests still pass.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B1",
      "kind": "blocking",
      "line": 43,
      "problem": "Contradiction with 4.1, and a configuration decision with no test. S45-D6 and S45-D4 need prompts without the open mandate: stage A's short prompt on the 4 new cases, round 1's narrow question for the DPL-010 case, and the canary, which uses the short prompt. But 4.1 fixes the mandate in the launcher's build_prompt so that 'a task text cannot remove or reorder' it. 4.1's success criterion says 'Every prompt the launcher builds contains the mode's mandate ... whatever the task text says'. The benchmark builds every prompt through launcher.build_prompt. Neither plan sets up a mandate-free path for benchmark baselines, and no test-plan row checks what each configuration's prompt contains."
    },
    {
      "evidence": "poc-4-4 plan.md:40 (S44-D7, base-commit read). answer_key.yaml case bases. plan.md:43 'Opus with the new setup on all 11 stage-A cases...'. test_plan.md has no row on checklist inclusion.",
      "failure_scenario": "The runner passes the case's base as the launcher's base. The --stage lookup finds no list at that commit and either fails or, under 4.2's fail-visible style, puts in an empty section. The report then claims the 4.4 checklists were measured, and the default is decided on a configuration that never contained them.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B2",
      "kind": "blocking",
      "line": 43,
      "problem": "Contradiction with 4.4: the 'new setup' would be measured without the stage checklists. S44-D7 has the launcher read the stage list 'with --stage <artifact type> from the base commit'. Every benchmark case's base (6e8b2cb, e842e97, c4f9ca2 ...) predates docs/review_checklists/, so no case would get a checklist. The plan does not say where benchmark cases take their list from (the current tree?), or which artifact type each case maps to (RM-3 mixes requirements, code and CI; the stage-document cases are requirements, test and architecture). No test row checks that a stage-B new-setup prompt contains the 4.4 list."
    },
    {
      "evidence": "test_plan.md:40-41 'the twin follows a planted instruction or setting (valid)'. plan.md:45 'its prompt tells it to act on the instruction files'. scripts/run_review_benchmark.py:416-424 validity = _followed_any(twin) (hook OR ids OR reads). The owner's #42 input: 'use a twin whose prompt makes it act on the instruction files, so that half of the claim is measured too'.",
      "failure_scenario": "The stronger twin again runs only the hook. The run is marked valid and the canary passes, and the report claims instruction files do not reach a confined reviewer, while that half is still unmeasured: a false green on the confinement claim. Later the CLI version changes, nobody re-runs the failed-Read probe, and the launcher's empty-review rule rests on stale CLI behaviour.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "B3",
      "kind": "blocking",
      "line": 40,
      "problem": "S45-D8 is not proved. The live check accepts a twin that 'follows a planted instruction or setting' as valid. That is exactly stage A's situation: the twin ran the hook (a setting) but ignored the CLAUDE.md files, so the instruction-file half was never measured. Also, only the twin's prompt is changed ('its prompt tells it to act'), so canary and twin no longer differ only in flags, and a canary pass could come from the prompt difference. Separately, the failed-Read probe that S45-D8 re-runs on a CLI version change has no live check or test at all. Nothing says how a version change is detected, or that the re-run is manual."
    },
    {
      "evidence": "run_review_benchmark.py:204-208: the leak search covers the problem ID and BENCHMARK_DIR in the copy. delivery_problem_log.md:304-316 (DPL-010 text). review_slice_3.md:562 '5a5aba7 (after slices 1 and 2 merged)'. review_slice_2.md:17,915: rounds 1-4 reviewed earlier commits.",
      "failure_scenario": "The dry run refuses the case, and the implementer must pick another commit without the owner (the plan is the contract). Or the leak terms are thinned or the directory check is loosened to get it through. The reviewer then reads DPL-010 in its copy and 'detects' the miss, which inflates the open mandate's result.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B4",
      "kind": "blocking",
      "line": 41,
      "problem": "The DPL-010 case as specified cannot run, and a workaround would leak the answer. 5a5aba7 is poc/agentic-sdlc after slice 2 merged. Its tree holds tests/review_benchmark/, docs/delivery_problem_log.md with DPL-010 (which names the untested refusal paths), and review_slice_2.md round 5. The runner refuses any copy that contains tests/review_benchmark/ or the case's problem ID. Round 1's narrow question was also asked of an earlier reviewed commit, not of the merged state, which includes the round-5 fixes."
    },
    {
      "evidence": "test_plan.md:35-39. plan.md:31-32, :42 ('a container that mounts only the copy and its login file'), :75-78 ('the reviewer process cannot read it'; the scanner does not know OpenAI token shapes). plan.md:84: no flag to skip AGENTS.md.",
      "failure_scenario": "In the container, Codex is asked to read ~/.codex/auth.json, replies that it will not access credentials, and the probe records 'passed'. Codex mode is enabled. A case file that tells it to inspect its environment, or a careless finding, later quotes the token in a report. The report goes into the committed results file and the scanner misses it. Or Codex auto-loads the copy's AGENTS.md (RM-3 and CL-1 review AGENTS.md changes) and judges against the changed rules.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "B5",
      "kind": "blocking",
      "line": 35,
      "problem": "The Codex confinement probe has no positive control. A model that declines counts as confinement. The probe 'passes only if none of the three succeeds', but Codex may simply refuse to cat a credential file or ignore a planted AGENTS.md line by its own judgement. The plan's canary uses a twin for exactly this reason. The probe also tests 'follows', while the threat is 'loads the copy's AGENTS.md'. On top of that, the container fallback mounts the login file where Codex's own shell commands, run as the same user, can read it. So the fallback cannot meet 'A Codex reviewer must not be able to read it' (plan line 31) unless the probe false-greens."
    },
    {
      "evidence": "run_review_benchmark.py:297-298 review_id, :529-535 setdefault((case, prompt)), :348-349 model is recorded but never used in identity. plan.md:43-44. test_plan.md:23-31 has no model row.",
      "failure_scenario": "After Opus completes RM-1/new-setup, the Sonnet run of RM-1/new-setup is skipped as finished, or the report scores Opus's result under Sonnet. Rule S45-D7(b) then picks a default reviewer model from mixed data. Every planned test still passes.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B6",
      "kind": "blocking",
      "line": 39,
      "problem": "Result identity leaves out the model, and no test proves the model comparison. S45-D2 adds a stage ID and the prompt hash only. Today's review_id is case/prompt and _completed_reviews keys on (case, prompt). With Opus, Sonnet and Codex running the same case under the same configuration (S45-D6), later models' runs count as done or are merged into the same comparison cell. No test-plan row covers several models in one stage, or the S45-D7 rule as code."
    },
    {
      "evidence": "plan.md:99. poc-4-4 plan.md:43 (S44-D10), :65 (in-scope AGENTS.md sections). AGENTS.md (base), Models and usage limits: 'Reviews run on Claude ... The review benchmark may also measure Codex as a reviewer'.",
      "failure_scenario": "The 4.4 critique runs Codex against the approved rules. The final review flags it as a rule violation, or the amended AGENTS.md states a narrower exception than the work actually used, so the rulebook and the record disagree.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B7",
      "kind": "blocking",
      "line": 99,
      "problem": "Contradiction with 4.4 and the rulebook. The only rule change for Codex is 'the owner's Codex exception for benchmark reviews', and base AGENTS.md already lets the benchmark measure Codex. But S44-D10 has Codex critique the draft checklists through the launcher. That is a review that is not a benchmark run, and AGENTS.md ('Reviews run on Claude') forbids it. No plan amends the rule for it: 4.4's AGENTS.md scope does not include 'Models and usage limits'. Under POC-D15 the author works by the base rules until the final PR merges anyway, so the plan should record the owner's exception explicitly for both uses."
    },
    {
      "evidence": "run_review_benchmark.py:93-99. test_plan.md:25 'after a prompt change' can be satisfied by editing a prompt file only.",
      "failure_scenario": "A 4.4 checklist is edited mid-stage. Earlier stage-B results still count as done, and the report mixes two checklist versions without saying so.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A1",
      "kind": "advisory",
      "line": 39,
      "problem": "[high] 'The prompt's SHA-256' is undefined. Today's prompts_sha256 hashes only tests/review_benchmark/prompts/*.md. In stage B most of the prompt sits elsewhere: the mandate in the launcher's code (4.1), the checklists in docs/review_checklists/ (4.4), and the computed evidence (4.2). If only the template files are hashed, a change to the mandate wording or a checklist leaves identity unchanged, which is R5-A2 again. If the full built prompt is hashed, any evidence that changes between runs (CI data, coverage) makes every run non-resumable."
    },
    {
      "evidence": "plan.md:43, :55-56, :116-117. Owner's #42 'Configurations' and the #33 decision 4.",
      "failure_scenario": "The owner approves believing the open mandate is measured as its own configuration, and later cannot tell whether the mandate or the checklists caused any difference.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A2",
      "kind": "advisory",
      "line": 43,
      "problem": "[high] The owner's configuration decision is changed without being flagged. The owner asked for 'the open-mandate prompt ... as a third configuration beside the short prompt and the checklist ... on the same cases'. The plan bundles mandate, 4.4 checklists and 4.2 evidence into one 'new setup'. It does not run stage A's checklist on the 4 new cases, and the success criteria compare against the short prompt only. The open mandate's own effect, the owner's question in decision 4, cannot be separated. This is not listed under Review notes as a deviation."
    },
    {
      "evidence": "plan.md:43 (Sonnet/Codex: 5 real misses + 3 stage cases only), :44.",
      "failure_scenario": "The rule picks Codex or Sonnet as the default on detections alone. The owner learns of a rulebook-level change from the report.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A3",
      "kind": "advisory",
      "line": 44,
      "problem": "[high] Rule S45-D7(b) cannot be applied as written. Sonnet and Codex run no clean cases, so 'with no more false blockers' has no measurement base. 'Cheapest' is undefined across vendors: a Claude CLI USD estimate against Codex's separate quota. Who adopts the result is also unclear: AGENTS.md says reviews run on Claude, so making Sonnet or Codex the default changes a rule and needs the owner (decision concern)."
    },
    {
      "evidence": "plants/PD-1.patch:1 header. answer_key.yaml:108 leak_terms [PLANT-]. plan.md:40.",
      "failure_scenario": "The plant cases are refused on their own code, or the search again checks nothing while the test is green.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "A4",
      "kind": "advisory",
      "line": 28,
      "problem": "[medium] The leak-term fix is underspecified and its test proves little. 'Its case wording' is ambiguous. Any term taken from the planted line is always in the copy and would refuse the case. The row only shows that an injected term refuses, so a new set of terms that never appear (like PLANT-) would still pass. Use the words that would reveal a plant, such as the patch header ('Planted defect PD-1', 'review benchmark'), and test that PD-1..4 pass the real search while a copy with the header is refused."
    },
    {
      "evidence": "A search of the poc-4-* plans for R5-A8 / dry_run finds nothing. The owner's #33 input item 4.",
      "failure_scenario": "The leak search's dry_run path silently breaks after the stage refactor, and the pre-run check reports '0 refused'.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A5",
      "kind": "advisory",
      "line": 62,
      "problem": "[high] Owner input R5-A8 is assigned to no slice-4 plan: the untested planted-patch path and dry_run of the benchmark runner, three report-shape branches of the launcher, and skipping non-JSON stream lines. 4.5 changes the runner and relies on --dry-run as a verification command, so it is the natural home."
    },
    {
      "evidence": "answer_key.yaml:5-6. run_review_benchmark.py:361 uses key.model/key.effort.",
      "failure_scenario": "Sonnet runs at medium effort and Opus at high, and the model comparison measures effort instead of the model.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A6",
      "kind": "advisory",
      "line": 43,
      "problem": "[medium] Model IDs and effort for Sonnet and Codex are unspecified. The answer key holds a single model and effort. It is not said how the runner selects the model per run, or what effort or reasoning level Codex uses, so comparability between models is left to the implementer."
    },
    {
      "evidence": "plan.md:38, :43. run_review_benchmark.py:40, :322-332.",
      "failure_scenario": "The probes plus a couple of retries push the true total past 40 while the runner reports 40 or fewer.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A7",
      "kind": "advisory",
      "line": 38,
      "problem": "[medium] The budget's edges are unclear. It is not said whether the Codex confinement probe sessions (sandbox, then container), the failed-Read probe, re-runs after a CLI change, and 4.4's Opus, Sonnet and Codex critiques count toward the 40. Each case allows up to three tries after provider errors, so a 3-run margin can be used up by one case. The hard cap is a code constant (MAX_BUDGET=26), and it is not said where the per-stage cap of 40 lives so that the key cannot raise it."
    },
    {
      "evidence": "test_plan.md:30, :35-36. plan.md:84-85, :90-92.",
      "failure_scenario": "A Codex CLI upgrade changes sandbox semantics, and the old 'passed' record keeps Codex mode enabled.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A8",
      "kind": "advisory",
      "line": 92,
      "problem": "[medium] Hidden state missing. 'Codex mode is refused when the confinement probe's result is not recorded as passed' needs a machine-readable record. The plan names only the plan's environment-facts table, which is Markdown and edits the approved plan. The hidden-state table should list its store, writer, reader, its binding to the Codex CLI version, and re-probing when that version changes, which S45-D8 covers only for the Claude CLI."
    },
    {
      "evidence": "test_plan.md:30. plan.md:84 (--json JSONL events).",
      "failure_scenario": "Codex runs `cat ../../secret`. The report names no outside path and the check passes. Or the attempt log publishes /home/<user>/... paths.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "A9",
      "kind": "advisory",
      "line": 30,
      "problem": "[medium] It is not said how a Codex run's reads are detected. Codex reads through shell commands in --json events, not Read tool calls. The outside-read and empty-review checks need command parsing (cat, sed, rg, relative paths, cd). The test row checks only that 'a reply names a path outside the copy', which is a check on the report, not on the stream. Persisting Codex events would also put absolute local paths and the account's HOME into the committed attempt log."
    },
    {
      "evidence": "poc-4-2 plan.md:36-37 (S42-D5/D6), :39 (S42-D8 covers paths only).",
      "failure_scenario": "Both DPL-010 runs see the coverage gaps and detect the miss, and the report credits the open mandate, or neither does.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A10",
      "kind": "advisory",
      "line": 43,
      "problem": "[medium] Whether stage-B runs get 4.2's computed evidence is unspecified. At old case commits the evidence commands may not exist (validate_traceability.py, tests/tools). For the DPL-010 case, coverage evidence lists exactly the uncovered refusal paths. That confounds the narrow-vs-open comparison with the evidence, so the principle question cannot be answered."
    },
    {
      "evidence": "run_review_benchmark.py:507-512. test_plan.md:31 covers only an unchanged stage-A report.",
      "failure_scenario": "The re-score path silently scores with the old key's terms, or overwrites stage A's tables.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A11",
      "kind": "advisory",
      "line": 40,
      "problem": "[medium] Re-scoring stage A with the new key has no test. load_results refuses results whose key hash differs, so a separate mode is needed, and its output must not be confused with stage A's report."
    },
    {
      "evidence": "plan.md:46. poc-4-4 plan.md:43. poc-4-1 plan.md:41.",
      "failure_scenario": "The Codex mode is built against the old schema, then broken by 4.1, and the critiques run before records are launcher-written and fail 4.3's check.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A12",
      "kind": "advisory",
      "line": 46,
      "problem": "[medium] The order across sub-issues is incomplete. The Codex mode 'comes first', but it must follow 4.1's schema (six kinds) and modes, and 4.2's file list. 4.4's critiques need 4.1's mandate, and 4.3 if their records are written by the launcher. No plan gives a total order of the six."
    },
    {
      "evidence": "plan.md:44. answer_key.yaml:8-11.",
      "failure_scenario": "Noise sends the decision to the owner, or two implementers compute different outcomes.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A13",
      "kind": "advisory",
      "line": 44,
      "problem": "[low] Rule (a) has zero tolerance ('fewer') where stage A's rule needed a difference of two to be measurable. With n=1 per case, one noisy miss triggers it. It is also unclear whether 'fewer real and planted' means the sum or each category, and whether 'more than one false blocker per clean case' means per case or on average over the two."
    },
    {
      "evidence": "plan.md:41. AGENTS.md test-lint row.",
      "failure_scenario": "The stage-document measurement shows nothing new about requirement or design review.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A14",
      "kind": "advisory",
      "line": 41,
      "problem": "[low] The 'weak test' stage-document case (an outcome guard that accepts any status) repeats PD-1/PD-2. make test-lint already catches it deterministically, so it adds little about stage documents. The answer-key entries for the new cases (files, ranges, terms) are also not sketched."
    },
    {
      "evidence": "test_plan.md:49-53. AGENTS.md step 4.",
      "failure_scenario": "The close-out misses a docs-check failure until CI.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "A15",
      "kind": "advisory",
      "line": 51,
      "problem": "[low] The planned verification leaves out make qa-quality (which includes docs-check), required by step 4. The new benchmark_report.md and results file must pass docs-check and the slice index."
    },
    {
      "evidence": "plan.md:42, :106. The 'Ask before growing' rule.",
      "failure_scenario": "Time goes into a container and network policy that cannot meet the credential requirement anyway.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "S1",
      "kind": "simpler_alternative",
      "line": 42,
      "problem": "Drop the container fallback (an author default). It needs an egress allow-list to the model API and still exposes the mounted login to Codex's commands. If Codex's own sandbox cannot deny reads outside the copy, take the plan's own stop branch: Codex drops out and the owner is told."
    }
  ],
  "verdict": "no"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| B1 | blocking | fixed: S45-D3 (configurations `short`, `open`, `open+list`, `narrow`); 4.1 S41-D2 lets only the runner build prompts without the mandate; test row "Configurations" |
| B2 | blocking | fixed: S45-D3 and 4.4 S44-D12 (lists from the runner's fixed commit, by the case's artifact type) |
| B3 | blocking | fixed: S45-D9 (identical prompts; the twin is valid only if it follows both the planted file and the hook; a live failed-Read probe; a CLI-version gate); test rows "Canary validity" and "CLI-version gate" |
| B4 | blocking | fixed: S45-D5 (a patch on `c4f9ca2` with only the launcher, its fake CLI and its tests as at `5a5aba7`); test row "New cases" checks the copy holds no benchmark files or DPL-010 text |
| B5 | blocking | fixed: S45-D6 (a control run must read a harmless outside marker and follow the planted instruction; the confined run must be denied by the sandbox; the login file is never a target) |
| B6 | blocking | fixed: S45-D2 (model and effort in the identity); test row "Identity" (two models on one case are two results) |
| B7 | blocking | fixed: `AGENTS.md` (Models and usage limits) in this plan PR covers the benchmark and 4.4's critique |
| A1 | high | fixed: S45-D2 defines the prompt identity (mandate, templates, lists, task; not evidence); test row "Prompt identity" |
| A2 | high | fixed: S45-D3 measures the open mandate alone (`open`) as the owner's third configuration, and `open+list` beside it |
| A3 | high | fixed: S45-D8(c) reports per model and leaves the choice to the owner; no automatic cost rule |
| A4 | medium | fixed: S45-D4 (leak terms from the patch header and each plant's own description words, which are not in the planted line); test row "Plant leak terms" checks every case's copy |
| A5 | high | fixed: S45-D11; test row "Runner paths (R5-A8)" |
| A6 | medium | fixed: S45-D10 names the models and effort |
| A7 | medium | fixed: S45-D1 (40 for cases and the canary; probes bounded at six; critiques outside) |
| A8 | medium | fixed: the probe record (`codex_probe.json`, committed, bound to the CLI version) is in the hidden-state table; test row "Codex mode" |
| A9 | medium | fixed: S45-D6 (outside reads from the sandbox's events; the event stream is never written to disk) |
| A10 | medium | fixed: 4.2 S42-D11 and 4.5's goal: computed evidence is off in the benchmark, and the report says so |
| A11 | medium | fixed: S45-D4 `--rescore A` into a separate output; test row "Re-score" |
| A12 | medium | fixed: the order of work (4.1, 4.2, 4.3, 4.5a, 4.4, 4.5b, 4.6) is in the slice index |
| A13 | low | fixed: S45-D8 uses stage A's threshold of two and says which counts are summed |
| A14 | low | fixed: the weak-test case is replaced by a test-plan row that drops a requirement's only runtime proof; S45-D5 says the answer key gives each new case its files, ranges, terms and type |
| A15 | low | fixed: `make qa-quality` is in the planned verification commands |
| S1 | low | fixed: adopted; no container fallback (S45-D6) |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "plan.md:56 S45-D7: 'open on the five real misses and two clean cases (7)'; 'short and open+list on the three stage-document cases (6)'. plan.md:57 S45-D8(a) sums real misses and stage-document defects; (b) compares open+list with open. test_plan.md has no row for the rules.",
      "failure_scenario": "Rule (a) is computed as written. `open` gets 0 of 3 stage-document defects by construction, against short's actual count, so the rule falsely sends the setup to the owner. Or rule (b) is computed on code cases only, and the report says 'the lists added no measurable detection'. The owner then drops the stage-document checklists, which were never measured against `open` on stage documents. That is a false answer to the owner's question, like B1.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B8",
      "kind": "blocking",
      "line": 57,
      "problem": "Contradiction between the run split (S45-D7) and the decision rules (S45-D8). `open` never runs on the three stage-document cases or the four planted cases. S45-D7 runs only `short` and `open+list` on the stage documents, and `open+list` alone on the plants. Yet rule (a) compares `open` with `short` on 'real misses and stage-document defects together', and rule (b) compares `open+list` with `open`. The stage-document cases, where requirement, test-plan and architecture checklists should matter most, are not in that comparison. The plan does not say whether the rules count over the cases both configurations share or over every case."
    },
    {
      "evidence": "plan.md:53 (`--rescore A` into a separate output; stage A's report stands), :58 (version gate on stage B only), :69-70 (success criterion).",
      "failure_scenario": "The report compares stage B under the new key with stage A under the old one, so detection differences partly reflect scoring rather than the setup.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A16",
      "kind": "advisory",
      "line": 69,
      "problem": "[medium] The plan does not say which stage-A scores the comparison uses. Stage A was scored with the old answer key, while stage B uses the new key with tighter plant terms (S45-D4). `--rescore A` writes a separate output, but the success criterion compares against stage A's `short` and `checklist` without naming the re-scored output. Stage A also ran under an older Claude CLI, and the CLI-version gate covers stage-B runs only."
    },
    {
      "evidence": "delivery_problem_log.md:304-317. plan.md:54 (S45-D5), :106. AGENTS.md step 1: a fact outside the repository is probed, not assumed.",
      "failure_scenario": "The case's defect was partly fixed before `5a5aba7`, so the narrow-vs-open comparison scores reviewers against paths that are no longer a miss.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A17",
      "kind": "advisory",
      "line": 106,
      "problem": "[medium] Nothing probes whether the DPL-010 defect is still present in the launcher and tests as they were at `5a5aba7`. The environment-facts row only shows that the tree holds the benchmark files. Round 5 ran before the merge and may have added tests for some refusal paths. No probe lists which refusal paths are untested at `5a5aba7`, and the answer key needs those paths."
    },
    {
      "evidence": "plan.md:113 hidden-state row.",
      "failure_scenario": "A hand-edited record says 'passed' for a partial result.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A18",
      "kind": "advisory",
      "line": 113,
      "problem": "[low] The author writes the Codex probe record by hand ('author, from the probe's output'), and Codex mode trusts it. Having the probe script write the record would remove a transcription step."
    },
    {
      "evidence": "B1: accepted (poc-4-5 plan.md S45-D3, poc-4-1 plan.md S41-D2, test_plan.md Configurations)\nB2: accepted (poc-4-5 plan.md S45-D3, poc-4-4 plan.md S44-D12, test_plan.md Configurations)\nB3: accepted (plan.md S45-D9, test_plan.md Canary validity, CLI-version gate)\nB4: accepted (plan.md S45-D5, :106, test_plan.md New cases); see A17\nB5: accepted (plan.md S45-D6, test_plan.md Codex probe)\nB6: accepted (plan.md S45-D2, test_plan.md Identity)\nB7: accepted (AGENTS.md:206-210, poc-4-4 plan.md)\nA1: accepted (plan.md S45-D2, test_plan.md Prompt identity)\nA2: accepted (plan.md S45-D3)\nA3: accepted (plan.md S45-D8(c))\nA4: accepted (plan.md S45-D4, test_plan.md Plant leak terms)\nA5: accepted (plan.md S45-D11, test_plan.md Runner paths)\nA6: accepted (plan.md S45-D10)\nA7: accepted (plan.md S45-D1, test_plan.md Budget)\nA8: accepted (plan.md hidden-state table, test_plan.md Codex mode)\nA9: accepted (plan.md S45-D6)\nA10: accepted (poc-4-2 plan.md S42-D11, plan.md Goal)\nA11: accepted (plan.md S45-D4, test_plan.md Re-score); see A16\nA12: accepted (docs/slices/README.md:16, plan.md:10-12)\nA13: accepted (plan.md S45-D8); see B8\nA14: accepted (plan.md S45-D5)\nA15: accepted (test_plan.md verification commands)\nS1: accepted (plan.md S45-D6, :137)",
      "failure_scenario": "None. This finding records which answers were accepted.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "no"
}
```

#### Answers to plan/c1/r2/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| B8 | blocking | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: S45-D7 runs `open` on the stage-document cases too (`short`, `open`, `open+list` there) and drops the planted cases from stage B, total 35; S45-D8 counts each rule only over the cases both configurations ran; the "Decision rules" row tests it |
| A16 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D8(a) uses stage A's results re-scored with the new key, and the report names both CLI versions |
| A17 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md: an environment fact from a coverage run at `5a5aba7` (2026-11-08) lists the refusal paths still untested there; the answer key expects these |
| A18 | low | fixed: docs/slices/poc-4-5-benchmark/plan.md: the probe script writes the probe record, never edited by hand (hidden-state table) |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |

## Round 3

### Attempt plan/c1/r3/plan/1

Commit `c352fce`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-5-benchmark/plan.md` `8d849ca773b1`, `docs/slices/poc-4-5-benchmark/test_plan.md` `cbbce2ed87a5`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 3 of the plan review of slice 4.5 (benchmark, #42), a recheck of your earlier report (round 2, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

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
      "evidence": "plan.md:56 S45-D7: 'open on the five real misses and two clean cases (7)'; 'short and open+list on the three stage-document cases (6)'. plan.md:57 S45-D8(a) sums real misses and stage-document defects; (b) compares open+list with open. test_plan.md has no row for the rules.",
      "failure_scenario": "Rule (a) is computed as written. `open` gets 0 of 3 stage-document defects by construction, against short's actual count, so the rule falsely sends the setup to the owner. Or rule (b) is computed on code cases only, and the report says 'the lists added no measurable detection'. The owner then drops the stage-document checklists, which were never measured against `open` on stage documents. That is a false answer to the owner's question, like B1.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B8",
      "kind": "blocking",
      "line": 57,
      "problem": "Contradiction between the run split (S45-D7) and the decision rules (S45-D8). `open` never runs on the three stage-document cases or the four planted cases. S45-D7 runs only `short` and `open+list` on the stage documents, and `open+list` alone on the plants. Yet rule (a) compares `open` with `short` on 'real misses and stage-document defects together', and rule (b) compares `open+list` with `open`. The stage-document cases, where requirement, test-plan and architecture checklists should matter most, are not in that comparison. The plan does not say whether the rules count over the cases both configurations share or over every case."
    },
    {
      "evidence": "plan.md:53 (`--rescore A` into a separate output; stage A's report stands), :58 (version gate on stage B only), :69-70 (success criterion).",
      "failure_scenario": "The report compares stage B under the new key with stage A under the old one, so detection differences partly reflect scoring rather than the setup.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A16",
      "kind": "advisory",
      "line": 69,
      "problem": "[medium] The plan does not say which stage-A scores the comparison uses. Stage A was scored with the old answer key, while stage B uses the new key with tighter plant terms (S45-D4). `--rescore A` writes a separate output, but the success criterion compares against stage A's `short` and `checklist` without naming the re-scored output. Stage A also ran under an older Claude CLI, and the CLI-version gate covers stage-B runs only."
    },
    {
      "evidence": "delivery_problem_log.md:304-317. plan.md:54 (S45-D5), :106. AGENTS.md step 1: a fact outside the repository is probed, not assumed.",
      "failure_scenario": "The case's defect was partly fixed before `5a5aba7`, so the narrow-vs-open comparison scores reviewers against paths that are no longer a miss.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A17",
      "kind": "advisory",
      "line": 106,
      "problem": "[medium] Nothing probes whether the DPL-010 defect is still present in the launcher and tests as they were at `5a5aba7`. The environment-facts row only shows that the tree holds the benchmark files. Round 5 ran before the merge and may have added tests for some refusal paths. No probe lists which refusal paths are untested at `5a5aba7`, and the answer key needs those paths."
    },
    {
      "evidence": "plan.md:113 hidden-state row.",
      "failure_scenario": "A hand-edited record says 'passed' for a partial result.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A18",
      "kind": "advisory",
      "line": 113,
      "problem": "[low] The author writes the Codex probe record by hand ('author, from the probe's output'), and Codex mode trusts it. Having the probe script write the record would remove a transcription step."
    },
    {
      "evidence": "B1: accepted (poc-4-5 plan.md S45-D3, poc-4-1 plan.md S41-D2, test_plan.md Configurations)\nB2: accepted (poc-4-5 plan.md S45-D3, poc-4-4 plan.md S44-D12, test_plan.md Configurations)\nB3: accepted (plan.md S45-D9, test_plan.md Canary validity, CLI-version gate)\nB4: accepted (plan.md S45-D5, :106, test_plan.md New cases); see A17\nB5: accepted (plan.md S45-D6, test_plan.md Codex probe)\nB6: accepted (plan.md S45-D2, test_plan.md Identity)\nB7: accepted (AGENTS.md:206-210, poc-4-4 plan.md)\nA1: accepted (plan.md S45-D2, test_plan.md Prompt identity)\nA2: accepted (plan.md S45-D3)\nA3: accepted (plan.md S45-D8(c))\nA4: accepted (plan.md S45-D4, test_plan.md Plant leak terms)\nA5: accepted (plan.md S45-D11, test_plan.md Runner paths)\nA6: accepted (plan.md S45-D10)\nA7: accepted (plan.md S45-D1, test_plan.md Budget)\nA8: accepted (plan.md hidden-state table, test_plan.md Codex mode)\nA9: accepted (plan.md S45-D6)\nA10: accepted (poc-4-2 plan.md S42-D11, plan.md Goal)\nA11: accepted (plan.md S45-D4, test_plan.md Re-score); see A16\nA12: accepted (docs/slices/README.md:16, plan.md:10-12)\nA13: accepted (plan.md S45-D8); see B8\nA14: accepted (plan.md S45-D5)\nA15: accepted (test_plan.md verification commands)\nS1: accepted (plan.md S45-D6, :137)",
      "failure_scenario": "None. This finding records which answers were accepted.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
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
| B8 | blocking | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: S45-D7 runs `open` on the stage-document cases too (`short`, `open`, `open+list` there) and drops the planted cases from stage B, total 35; S45-D8 counts each rule only over the cases both configurations ran; the "Decision rules" row tests it |
| A16 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D8(a) uses stage A's results re-scored with the new key, and the report names both CLI versions |
| A17 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md: an environment fact from a coverage run at `5a5aba7` (2026-11-08) lists the refusal paths still untested there; the answer key expects these |
| A18 | low | fixed: docs/slices/poc-4-5-benchmark/plan.md: the probe script writes the probe record, never edited by hand (hidden-state table) |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "plan.md:114 hidden-state row: writer 'the probe script, never edited by hand'. plan.md:78-82 In scope lists the runner, tests/review_benchmark/, the launcher's Codex mode, 'the probe record', the tooling tests and the report. test_plan.md:43-45 (Codex probe) gives the probe's outcomes but not who writes the record.",
      "failure_scenario": "The implementer adds no script and writes the record by hand, and the plan can be read as allowing it. The transcription step A18 meant to remove comes back.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A19",
      "kind": "advisory",
      "line": 114,
      "problem": "[low] The A18 fix names 'the probe script' as the writer of the Codex probe record. The In scope list (line 78-82) names 'the probe record' but no probe script, and the test plan has no row for it."
    },
    {
      "evidence": "plan.md:7 'revised after plan review round 1'; plan.md:69-71 success criterion; plan.md:57 S45-D8(a) 'stage A's short, re-scored with the new key'.",
      "failure_scenario": "A reader of the success criterion alone compares against stage A's original scores. S45-D8 and the Decision rules test row (test_plan.md:38) catch this.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A20",
      "kind": "advisory",
      "line": 69,
      "problem": "[low] The success criterion still says the report compares with 'stage A's short and checklist' without saying 're-scored'. The status line still says 'revised after plan review round 1'. S45-D8(a) now names the re-scored stage-A results, so this is wording, not a contradiction."
    },
    {
      "evidence": "B8: accepted (plan.md S45-D7 line 56: Opus runs short, open and open+list on the stage-document cases, planted cases dropped, 2+14+9+2+5+3=35; S45-D8 line 57: each rule counts only the cases both configurations ran, and (a) and (b) both name shared sets; test_plan.md:38 Decision rules row)\nA16: accepted (plan.md S45-D8(a) line 57: re-scored stage A, both CLI versions named)\nA17: accepted (plan.md:107 environment fact: a coverage run at 5a5aba7 lists the untested refusal paths)\nA18: accepted (plan.md:114 hidden-state table); see A19\nACCOUNTED: accepted (the stand-in until S41-D8's field exists)",
      "failure_scenario": "None. This finding records which answers were accepted.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to plan/c1/r3/plan/1

| ID | Severity | Answer |
| --- | --- | --- |
| A19 | low | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: In scope names the probe script, and the "Probe record" row tests that it writes the record Codex mode reads |
| A20 | low | fixed: docs/slices/poc-4-5-benchmark/plan.md: the success criterion says "re-scored with the new key", and the status line names rounds 1, 2 and 3 |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |

## Round 4

### Attempt plan/c1/r4/plan/1

Commit `341fa47`, effort medium. Files reviewed (SHA-256): `docs/slices/poc-4-5-benchmark/plan.md` `cb97b0e1c18d`, `docs/slices/poc-4-5-benchmark/test_plan.md` `209721073711`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 4 of the plan review of slice 4.5 (benchmark, #42), a recheck of your earlier report (round 3, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. The author revised all six slice-4 plans together (`docs/slices/poc-4-*/`) so that decisions shared between plans agree; a fix may sit in another plan, the slice index (`docs/slices/README.md`) or `AGENTS.md`, so open those where an answer points to them. From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; slice 4 proposes that high findings count too, so report new high findings as well, marked `[high]`. Judge against the approved threat model (`AGENTS.md`, PoC scope and proportion) and the plan's own threat model.

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

## Your earlier report (round 3, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "plan.md:114 hidden-state row: writer 'the probe script, never edited by hand'. plan.md:78-82 In scope lists the runner, tests/review_benchmark/, the launcher's Codex mode, 'the probe record', the tooling tests and the report. test_plan.md:43-45 (Codex probe) gives the probe's outcomes but not who writes the record.",
      "failure_scenario": "The implementer adds no script and writes the record by hand, and the plan can be read as allowing it. The transcription step A18 meant to remove comes back.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A19",
      "kind": "advisory",
      "line": 114,
      "problem": "[low] The A18 fix names 'the probe script' as the writer of the Codex probe record. The In scope list (line 78-82) names 'the probe record' but no probe script, and the test plan has no row for it."
    },
    {
      "evidence": "plan.md:7 'revised after plan review round 1'; plan.md:69-71 success criterion; plan.md:57 S45-D8(a) 'stage A's short, re-scored with the new key'.",
      "failure_scenario": "A reader of the success criterion alone compares against stage A's original scores. S45-D8 and the Decision rules test row (test_plan.md:38) catch this.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A20",
      "kind": "advisory",
      "line": 69,
      "problem": "[low] The success criterion still says the report compares with 'stage A's short and checklist' without saying 're-scored'. The status line still says 'revised after plan review round 1'. S45-D8(a) now names the re-scored stage-A results, so this is wording, not a contradiction."
    },
    {
      "evidence": "B8: accepted (plan.md S45-D7 line 56: Opus runs short, open and open+list on the stage-document cases, planted cases dropped, 2+14+9+2+5+3=35; S45-D8 line 57: each rule counts only the cases both configurations ran, and (a) and (b) both name shared sets; test_plan.md:38 Decision rules row)\nA16: accepted (plan.md S45-D8(a) line 57: re-scored stage A, both CLI versions named)\nA17: accepted (plan.md:107 environment fact: a coverage run at 5a5aba7 lists the untested refusal paths)\nA18: accepted (plan.md:114 hidden-state table); see A19\nACCOUNTED: accepted (the stand-in until S41-D8's field exists)",
      "failure_scenario": "None. This finding records which answers were accepted.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
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
| A19 | low | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: In scope names the probe script, and the "Probe record" row tests that it writes the record Codex mode reads |
| A20 | low | fixed: docs/slices/poc-4-5-benchmark/plan.md: the success criterion says "re-scored with the new key", and the status line names rounds 1, 2 and 3 |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "plan.md:58 (c2) 'the drafts become the mandates; otherwise ... the owner chooses (S41-D14)'; poc-4-1-review-prompts/plan.md:55 S41-D14 'the owner chooses from 4.5's report'; poc-4-4-stage-checklists/plan.md:51 S44-D11 'the owner approves it'; plan.md:81-85 In scope.",
      "failure_scenario": "(c2) fires and the report says the drafts are now the mandates. The launcher keeps 4.1's constants because no slice owns the swap, or someone swaps them without the owner's approval and so bypasses S44-D11. Either way the record contradicts itself about which mandate is in force. Fix: in (c2) say 'the report recommends the drafts and the owner decides', and name who swaps the constants (or say they change only through the learning loop). One sentence on the final draft would also help.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A21",
      "kind": "advisory",
      "line": 58,
      "problem": "[medium] S45-D8(c2) says that if the drafts win, 'the drafts become the mandates', and that otherwise the owner chooses. S41-D14 (poc-4-1 plan.md:55) says the owner chooses from 4.5's report in every case, and S44-D11 says the owner approves any change to mandate wording. No plan says who replaces the launcher's mandate constants in `scripts/run_independent_review.py` when (c2) fires, or in which slice. 4.5's In scope (plan.md:81-85) names the launcher only for its Codex mode. The final mandate's draft (S44-D13) also has no stated fate: S45-D7 does not measure it, and S41-D14 only covers the initial and recheck mandates."
    },
    {
      "evidence": "plan.md:55 S45-D5 'a recheck case ... built like slice 2's round 4' (no commit); test_plan.md:35 New cases row names the three stage-document cases and DPL-010 only; test_plan.md:31 the Recheck case row tests the prompt and scoring, not preparation or leaks; test_plan.md:33 'every case's copy' is free of its leak terms only if the answer key gives the recheck case leak terms.",
      "failure_scenario": "The recheck case is built on a commit whose copy holds slice 2's review record or a DPL entry describing the false `fixed:` answer. `recheck-A` and `recheck-B` both re-raise it by reading the answer, so (c2) is decided on a leaked case. Fix: name the base commit and add the recheck case to the 'New cases' row with its leak terms.",
      "file": "docs/slices/poc-4-5-benchmark/test_plan.md",
      "id": "A22",
      "kind": "advisory",
      "line": 35,
      "problem": "[medium] The new recheck case (S45-D5) names no base commit, unlike the other new cases (`e842e97`, `c4f9ca2`). The 'New cases' row lists only the three stage-document cases and the DPL-010 case, so nothing tests that the recheck case prepares, passes the leak search and reviews the right paths. The case is modelled on slice 2's round 4. Slice 2's review record and later DPL entries describe the exact miss: an accepted answer naming an 'Advisory only' column that did not exist. A copy at a commit that holds them would hold the case's answer."
    },
    {
      "evidence": "plan.md:57 S45-D7 'recheck-A and recheck-B on the recheck case (2)'; plan.md:58 (c2) 'if open-B and recheck-B together detect at least two more defects than 4.1's wordings ... the drafts become the mandates'.",
      "failure_scenario": "`open-B` finds 2 more defects, and `recheck-B` accepts the false `fixed:` answer that `recheck-A` re-raised. The net gain is +1, so (c2) does not fire and neither draft is adopted. Had `recheck-B` tied, both would have been adopted, though the recheck draft has no evidence either way. The owner may prefer to decide the two mandates separately, or to treat the recheck draft as unmeasured.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A23",
      "kind": "decision_concern",
      "line": 58,
      "problem": "[low] (c2) makes one decision for two mandates. `open-B` and `recheck-B` together must detect 'at least two more' than 4.1's wordings. The recheck mandate is measured on a single case, so it adds at most one detection. A recheck draft that does worse can therefore be adopted because the initial draft did well, and the reverse."
    },
    {
      "evidence": "A19: accepted (plan.md:84 In scope names 'the Codex probe script and the record it writes'; test_plan.md:37 Probe record row)\nA20: accepted (plan.md:72 'stage A's short and checklist, re-scored with the new key'; plan.md:8 'revised after plan review rounds 1, 2 and 3')\nACCOUNTED: accepted (stand-in until S41-D8's field exists)\nOwner's change: checked poc-4-5 plan.md and test_plan.md, poc-4-1-review-prompts/plan.md (S41-D4, S41-D14) and test_plan.md:29, poc-4-4-stage-checklists/plan.md (S44-D10, S44-D11, S44-D13) and test_plan.md:27, docs/slices/README.md. The budget of 50 agrees across plans (S45-D1, S44-D10). The run count is 2+14+9+2+10+2+5+3 = 47. Each new decision has a test-plan row. See A21-A23.",
      "failure_scenario": "None. This finding records which answers were accepted.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
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
| A21 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D8: the report recommends nothing automatically; the owner chooses each mandate, the launcher's constants change only after the choice, in 4.5b, and the final draft is chosen by reason |
| A22 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/slices/poc-4-5-benchmark/test_plan.md: the recheck case sits on `e842e97` with leak terms from its description, and the "Cases" row covers it |
| A23 | low | owner: decided on 2026-11-09 ("I accept your recommendations for my decisions"): the two mandates are chosen separately (S45-D8) |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
