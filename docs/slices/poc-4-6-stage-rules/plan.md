# Slice Plan — poc-4-6-stage-rules: stage rules in the slice workflow

Plan of slice 4.6 of the agentic-SDLC PoC (issue #43, part of slice 4, #33): the `AGENTS.md` slice
workflow names the seven stages of the delivery cycle. For each it says what the stage produces, how
it is reviewed and checked, and how discovered issues are handed over so they are not lost.

Status: draft, 2026-11-08. Approved when the owner merges slice 4's single plan PR.

## Goal

The PoC's Goal table (`docs/slices/agentic-sdlc-poc/plan.md`) defines seven stages, from discovery to
handoff. `AGENTS.md`'s slice workflow still has four steps (plan, tests first, implement, verify and
close), so requirements, architecture and the final review have no stage rules. Two problems from
slices 1 to 3 show what is missing:
- reviews never asked where a problem started;
- discovered issues ended up as untracked notes in PR descriptions.

The owner: "Making the notes in the plan PR is only going to get lost like now". This slice writes the
stage rules, using 4.4's lists for each stage's review, and settles the carry-overs from the PoC
plan's review.

## Threat model

- **Delivery** (honest mistakes):
  - a stage skipped without a reason;
  - a downstream review built on an upstream document that was later corrected;
  - a blocker waived by someone other than the owner;
  - a review loop that keeps going without progress;
  - a discovered issue left only in a PR.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S46-D1 | **Seven stages in the slice workflow:** discovery, requirements, architecture and interfaces, tests first, implementation, final review, handoff. For each, the stage table in `AGENTS.md` gives: what it produces, its review (the matching 4.4 list), its deterministic checks, and its exit. A stage that does not apply is marked "none, with a reason" in the plan. | the PoC plan's Goal table; #33's description |
| S46-D2 | **Discovery without a grill-me when the design is clear:** a grill-me is for unclear design. When the design is clear, the plan lists every decision with its source (the owner with date and link, or "default by the author" with a reason), and the owner confirms the defaults when approving the plan. | owner, 2026-11-08 ("grill-me is when the design or approach is not clear to create a contract") |
| S46-D3 | **Larger chunks:** a slice may hold several sub-issues. They share one plan PR, which the owner approves once, and one final PR with a section per sub-issue. Each sub-issue keeps its own review units (plan, implementation) with their own round limits. | owner, 2026-11-08 (this slice's run mode) |
| S46-D4 | **Upstream reviews:** requirements and architecture are reviewed at their own stage before tests and code are built on them. A correction to an upstream document reopens the reviews of the documents built on it, and the reopening is recorded in the attempt log as a new revision. | [reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090); PoC plan (slice 4 row) |
| S46-D5 | **Final review:** a fresh review with the open prompt "What did everyone before you miss?", given all the evidence and no question list. Its second pass gets the finding history through its prompt (4.1's recheck inputs). | [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147); #33's description |
| S46-D6 | **Only the owner waives a blocker** (D12 of PR #26). An author may reject a finding with a checkable reason, and the reviewer accepts or re-raises it. Waiving a blocker that is still disputed is the owner's alone. | #33's description; PoC plan mapping |
| S46-D7 | **Earlier escalation** (D13 of PR #26): the author escalates to the owner before round 4 when a finding conflicts with an approved decision, or when two rounds in a row end with the same blocking finding. | same |
| S46-D8 | **Test-first working rules** (D38 of PR #26), for stage 4: interface skeletons exist before tests, so a red test fails for the intended reason; each new test records its expected failure on the base code; security paths get targeted mutants. | same |
| S46-D9 | **Handoff:** every discovered issue becomes an issue with a "needed before" point, or a comment on the issue it belongs to, before the PR is handed over. The PR lists each with its status and link and is updated when a later fix lands. | owner, 2026-11-08 ("create issues, prioratize when they needs to be in place") |
| S46-D10 | **Discoverability:** `AGENTS.md`'s "Start here" table gains a row: how to run a review, and where attempt logs and review records live. `docs/STATUS.md` shows the open PoC work in its "needed before" order. | [slice 2, round 5](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196); owner, 2026-11-08 |
| S46-D11 | **Templates:** the plan template gains the stage table (which stages apply, or "none, with a reason") and the decision-source column. The test-plan template points each stage's review at its 4.4 list. | default (the templates carry the rules into every new slice) |

## Requirements

None added (POC-D9).

## Success criteria

- `AGENTS.md` states the seven stages and S46-D2 to S46-D10. The review quotes the text that states each
  one, and no rule contradicts them.
- A slice bundle made from the templates passes `make docs-check` and the lint gate's header check.
- `docs/STATUS.md` lists the open PoC work in "needed before" order.

## In scope

`AGENTS.md` (slice workflow, Start here, Independent review), `docs/slices/_template/plan.md` and
`test_plan.md`, `docs/STATUS.md`.

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
| Open PoC issues | GitHub issues (2026-11-08) | #33 (slice 4) with sub-issues #38–#43; #44 (before slice 5); #45 (before slice 7); #46 (at the merge into `main`); #36 (slice 7); #21 (before slice 5) |

## Hidden-state and trust decisions

None.

## Authored source changes

- Requirements and architecture: none.
- Proof: review (the text for each decision); a tooling test that a bundle made from the templates
  passes `docs-check` and the header check.
- Rulebook: `AGENTS.md` and the templates, as above.

## Checks this slice adds (POC-D6)

None that run as a gate. The template test is a tooling test of documents the slice changes.

## Retirement and compatibility

- The four-step workflow text is replaced by the seven-stage table. Steps 2 to 4's existing rules
  (expected outcomes from the plan, negative tests with twins, static proof, the close-out list) are kept
  inside the matching stages, not dropped.
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm: S46-D11 (template changes), and the escalation
triggers in S46-D7 ("two rounds in a row with the same blocking finding").
