# Slice Plan — poc-4-6-stage-rules: stage rules in the slice workflow

Plan of slice 4.6 of the agentic-SDLC PoC (issue #43, part of slice 4, #33): the `AGENTS.md` slice
workflow names the seven stages of the delivery cycle. For each it says what the stage produces, how
it is reviewed and checked, and when it ends, and how discovered issues are handed over so they are
not lost.

Status: draft, 2026-11-08, revised after plan review round 2. Approved when the owner merges slice
4's single plan PR.

**Order of work:** last of slice 4, because its rules name 4.1's modes, 4.3's records and 4.4's list
files. 4.1 and this slice both edit the test-plan template; this slice builds on 4.1's text. The
whole order is in the [slice index](../README.md).

## Goal

The PoC's Goal table (`docs/slices/agentic-sdlc-poc/plan.md`) defines seven stages, from discovery to
handoff. `AGENTS.md`'s slice workflow still has four steps (plan, tests first, implement, verify and
close), so requirements, architecture and the final review have no stage rules. Two problems from
slices 1 to 3 show what is missing:
- reviews never asked where a problem started;
- discovered issues ended up as untracked notes in PR descriptions.

The owner: "Making the notes in the plan PR is only going to get lost like now". This slice writes the
stage rules, using 4.4's lists for each stage's review, and settles the PoC plan's slice-4 items:
how rule deviations are recorded, where the owner's words live for the final review, and the
final-review question on documents a change made false.

## Threat model

- **Delivery** (honest mistakes):
  - a stage skipped without a reason;
  - a downstream review built on an upstream document that was later corrected;
  - a blocker waived by someone other than the owner;
  - a review loop that keeps going without progress;
  - a discovered issue left only in a PR;
  - a rule of the old four steps lost in the rewrite.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S46-D1 | **Seven stages in the slice workflow:** discovery, requirements, architecture and interfaces, tests first, implementation, final review, handoff. A table in `AGENTS.md` gives, for each stage, what it produces, its review, its deterministic checks and its exit (what must hold to leave it). The reviews: discovery uses 4.4's plan-and-test-plan list; requirements, and architecture and interfaces, use their lists; tests first uses the unit-test and E2E-test lists; implementation uses the code list; the final review uses 4.1's final mode, with no list; handoff is the owner's approval. A stage that does not apply is marked "none, with a reason" in the plan. | the PoC plan's Goal table; #33's description; default (the exit column) |
| S46-D2 | **Discovery without a grill-me when the design is clear.** A grill-me is for unclear design. When the design is clear, the plan lists every decision with its source: the owner, with date, link and the owner's words quoted, because reviewers cannot open GitHub; or "default by the author", with a reason. The owner confirms the defaults when approving the plan. Without a grill-me, the plan's "Assets and holders" section still answers which keys, sockets and secrets the slice touches and who may hold them. | owner, 2026-11-08 ("grill-me is when the design or approach is not clear to create a contract between you and me"); the PoC plan's slice-4 row (the owner's words for the final review); plan review round 2, A7 |
| S46-D3 | **Larger chunks, when the owner chooses them for a slice.** A slice may hold several sub-issues. They share one plan PR, which the owner approves once, and one final PR with a section per sub-issue. Each sub-issue keeps its own review units (plan, implementation) with their own round limits, and the slice has one final review unit. | owner, 2026-11-08 (slice 4's run mode); default (an option for later slices, chosen by the owner each time) |
| S46-D4 | **Upstream reviews.** Requirements and architecture are reviewed at their own stage, before tests and code are built on them. When an upstream document is corrected after a downstream unit reviewed it, that unit's next round reviews the correction. The round counts against its limit, since a new revision keeps the count. A unit that had ended reopens with its next round number, and beyond round 4 the owner decides, as for any extension. The reopened unit's review record notes the reopening and the corrected document. The launcher needs no change. | [reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090); PoC plan (slice 4 row); default (the mechanism) |
| S46-D5 | **Final review:** one unit `final` per slice, run in 4.1's final mode. It gets the open question "What did everyone before you miss?", including any tracked document the change made false, and all the evidence, with no question list. Its finding history is the other units' review records, which are in its copy. Its later rounds are 4.1 rechecks. | owner, [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147), item 5; the PoC plan's final-review question; 4.1, S41-D4 |
| S46-D6 | **Only the owner waives a blocker** (D12 of PR #26). An author may reject a finding with a checkable reason, and the reviewer accepts or re-raises it. Waiving a blocker that is still disputed is the owner's alone. | #33's description; PoC plan mapping |
| S46-D7 | **Earlier escalation** (D13 of PR #26): the author asks the owner before round 4 when a finding conflicts with an approved decision, or when rechecks re-raise the answer to the same finding in two rounds in a row (status `re-raised` in 4.1's `accounted`; a re-raised finding keeps its ID, S41-D8). | #33's description; default (the trigger) |
| S46-D8 | **Test-first working rules** (D38 of PR #26), for the tests-first stage: interface skeletons exist before tests, so a red test fails for the intended reason. The implementation log lists, for each new test, the failure it showed on the base code (the command and the first failure line). Every fail-closed path of a security decision gets a test that triggers it, and in capability-issuer and tool-b a mutant (`make unit-mutation`). | #33's description; default (where the failure is recorded; mutants where the gate exists) |
| S46-D9 | **Handoff.** Work found but not done becomes a GitHub issue (label `slice` or `user-action`), whose body starts with "Needed before: <point>" and whose conversation is locked right away. It can instead be a comment on the issue it belongs to. Findings fixed or rejected in the PR, and notes outside the threat model, are not issues ("Few exceptions"). The PR body lists each issue with its link at handoff. The issue is the home of its status; the PR body is a snapshot and is not updated later. | owner, 2026-11-08 ("create issues, prioratize when they needs to be in place"); default (the first line, the snapshot) |
| S46-D10 | **Discoverability.** `AGENTS.md`'s "Start here" table gains a row: how to run a review, and where attempt logs and review records live. `docs/STATUS.md` shows the open PoC work in its "needed before" order and is refreshed at each close-out; each issue stays the home of its own point. | [slice 2, round 5](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196); owner, 2026-11-08 |
| S46-D11 | **Templates.** The plan template gains the stage table (each stage applies, or "none, with a reason"), the decision-source column, and a "Rule deviations" section: one line per deviation, giving the rule, the deviation, the owner's words with the link, and the expiry. The test-plan template points each stage's review at its list and keeps the implementation-review questions `AGENTS.md` requires. | the PoC plan's slice-4 row (how rule deviations are recorded); default (the templates carry the rules into every new slice) |
| S46-D12 | **No rule of the old steps is lost.** Step 1's rules (the assets question, environment-fact probes, working by the base branch's rulebook, approval by merge, implementing only from the merged plan), step 2's (expected outcomes from the plan or a probe, a twin for every negative test, static proof), step 3's (remove what the plan retires) and step 4's close-out list move into their stages. Every reference to "step 1" to "step 4" in live documents is rewritten to the stage's name. | plan review round 2, A7 |

## Requirements

None added (POC-D9).

## Success criteria

- `AGENTS.md` states the seven stages, with every column filled, and S46-D2 to S46-D12. The review
  quotes the text that states each one, and no rule contradicts them.
- The templates carry the stage table, the source column, the rule-deviations section and the
  required review questions, and a bundle made from them passes `make docs-check` and the lint gate's
  header check.
- No live document refers to the old step numbers.

## In scope

`AGENTS.md` (slice workflow, Start here, Independent review, the step references),
`docs/slices/_template/plan.md` and `test_plan.md`, `docs/STATUS.md`, `docs/test_spec.md` (step
references), a tooling test.

## Out of scope

- The stage lists themselves (4.4, #41).
- The delivery loop that runs the stages (slice 7, #36).
- A deterministic check of PR descriptions: PR text is outside the repository. The handoff rule is
  proved by review.

## Assets and holders

None touched.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Current slice workflow | `AGENTS.md` (`c325e7d`) | Four steps: plan and review, tests first, implement, verify and close |
| Step references | `grep -rn "step [1-4]"` in live documents (`d56c69a`, 2026-11-08) | `AGENTS.md` (four places), `docs/STATUS.md`, `docs/test_spec.md`, `docs/slices/_template/test_plan.md` |
| Open PoC issues | GitHub issues (2026-11-08) | #33 (slice 4) with sub-issues #38–#43; #44 (before slice 5); #45 (before slice 7); #46 (at the merge into `main`); #36 (slice 7); #21 (before slice 5) |

## Hidden-state and trust decisions

None.

## Authored source changes

- Requirements and architecture: none.
- Proof: review (the text for each decision); a tooling test of the stage table, the templates and
  the step references.
- Rulebook: `AGENTS.md` and the templates, as above.

## Checks this slice adds (POC-D6)

Process steps, with their cost per slice (the CLI's estimates from slices 2 and 3: an open round at
high effort takes 4 to 7 minutes and USD 2 to 3):

| Step or check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Requirements review stage | A requirement defect found only after tests and code are built on it (DPL-004) | One review unit when a slice changes requirements | Reviewing requirements inside the plan review: the plan review was anchored to the plan (DPL-004) |
| Architecture review stage | The same for architecture and interfaces | One review unit when a slice changes them | The same |
| Final review unit | What every focused round missed (slice 2's round 5, slice 3's round 4) | One or two open rounds per slice | An extra round of the implementation unit: it inherits that unit's framing |
| Reopening after an upstream correction | A review built on a corrected document | A round of the downstream unit | Accepting the risk |
| Earlier escalation | Rounds spent on a dispute only the owner can settle | An earlier owner question | Waiting for round 4 |
| An issue for open discovered work | Work lost in PR notes | One issue each | PR notes: they got lost |
| Tooling test of the stage table, templates and step references | A stage, a column, a required question or a stale step reference missing | One test | Review by eye |

## Retirement and compatibility

- The four-step workflow text is replaced by the seven-stage table. Every rule of the four steps moves
  into its stage (S46-D12).
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm: S46-D1 (the exit column), S46-D3 as an option for
later slices, S46-D4 (the reopening mechanism), S46-D7 (the trigger), S46-D8 (where failures are
recorded; mutants only where the gate exists), S46-D9 (the first line; the PR list as a snapshot),
S46-D10 (STATUS ordering), S46-D11.
