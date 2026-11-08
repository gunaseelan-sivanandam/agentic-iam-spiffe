# Slice Test Plan — poc-4-4-stage-checklists

Test plan of slice 4.4 of the agentic-SDLC PoC (issue #41): how we show the stage checklists exist
in the agreed form, reach each review from the base branch, and would have caught the repository's
past misses.

## Goal

Prove S44-D1 to S44-D11 of [`plan.md`](plan.md):
- the form of the lists and the launcher's `--stage` with tooling tests;
- the research and the DPL mapping by review, by three models.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S44-D1 to S44-D11.
- The DPL entries in `docs/delivery_problem_log.md` (DPL-001 to DPL-010) as test cases for the lists.

## Unit test plan

Tooling tests in `tests/tools/`.

| Area | Passes when | Fails when | Proves | Source |
| --- | --- | --- | --- | --- |
| List form | Every file in `docs/review_checklists/` starts with a title and a purpose paragraph, has at most 12 numbered questions and a "Blocks at this stage" section, and every question has a source tag that exists in `research.md` | Each of: 13 questions; a question without a source tag; a tag not in `research.md`; a missing "Blocks at this stage" section | S44-D2, S44-D3, S44-D4 | plan |
| All types present | The eight artifact types each have a list | — | S44-D1 | plan |
| Missing-things questions | The requirements, tests and final-review lists contain the proof question. The code and final-review lists contain the CI-job question. | — | S44-D5 | plan |
| `--stage` | A review with `--stage requirements` gets the base commit's requirements list in its checklist section | A list changed on the branch under review does not reach its own review. An unknown stage is refused before any call. | S44-D7 | plan |

## Review-based proof

- **DPL mapping:** the plan review and the critiques check that every DPL entry has a question at the
  stage where the miss happened, or a reason why not (S44-D9).
- **Critiques:** Opus, Sonnet and Codex each review the drafts with the open mandate (S44-D10).
  Every finding gets an answer under 4.1's severity rules.

## E2E test plan

None.

## Planned verification commands

- `make tooling-test`
- `make docs-check`
- `make lint`

## Independent review at the implementation PR

After the open mandate, the reviewer answers in the PR body:
1. *Lists:* which known class of defect, from the sources or from the DPL entries, would still pass
   every list?
2. *Tests:* which wrong behaviour would still pass each new test?
3. *Names and headers.*

A gap in question 1 for a DPL entry blocks; the rest follow the severity rules.
