# Slice Test Plan — poc-4-6-stage-rules

Test plan of slice 4.6 of the agentic-SDLC PoC (issue #43): how we show the seven stages and the
handoff rules are stated in the rulebook and carried by the templates.

## Goal

Prove S46-D1 to S46-D11 of [`plan.md`](plan.md). The rule texts are proved by review, which quotes
each one. The templates are proved by a tooling test that a bundle made from them passes the checks.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S46-D1 to S46-D11.

## Unit test plan

| Area | Passes when | Fails when | Proves | Source |
| --- | --- | --- | --- | --- |
| Templates | A slice bundle copied from `docs/slices/_template/` (with its placeholders filled by a fixed sample) passes `scripts/check_docs.py`. Each file passes the lint gate's header check (`header_problem`). | A template whose first lines break the Markdown header rule fails the test | S46-D11 | plan |
| Stage table present | `AGENTS.md`'s slice workflow names the seven stages in order | A stage missing from the table fails the test | S46-D1 | plan |

## Review-based proof

The plan review, the implementation review and the final review quote, for each of S46-D2 to S46-D10,
the `AGENTS.md` or template text that states it. They also check that the old steps' rules (expected
outcomes from the plan, twins for negative tests, static proof, the close-out list) survive in the
stages.

## E2E test plan

None.

## Planned verification commands

- `make tooling-test`
- `make docs-check`
- `make lint`

## Independent review at the implementation PR

After the open mandate, the reviewer answers in the PR body:
1. *Rules:* for each decision, where is the text that states it? Does any rule now contradict another?
   Was any rule of the old four steps lost?
2. *Practicality:* can an author follow the stages for a one-line fix without inventing work ("none, with
   a reason")?
3. *Names and headers.*

A missing text for a decision, or a contradiction, blocks.
