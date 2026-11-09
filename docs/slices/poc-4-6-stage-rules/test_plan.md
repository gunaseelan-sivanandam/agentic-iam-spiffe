# Slice Test Plan — poc-4-6-stage-rules

Test plan of slice 4.6 of the agentic-SDLC PoC (issue #43): how we show the seven stages and the
handoff rules are stated in the rulebook and carried by the templates.

## Goal

Prove S46-D1 to S46-D14 of [`plan.md`](plan.md). The stage table, the templates and the step
references are proved by a tooling test; the rule texts by review, which quotes each one.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S46-D1 to S46-D14.

## Unit test plan

| Area | Passes when | Fails when | Proves | Source |
| --- | --- | --- | --- | --- |
| Stage table | `AGENTS.md`'s slice workflow has a table of the seven stages, in order, each with a non-empty "produces", "review", "checks" and "exit" cell; every review cell names a list file in `docs/review_checklists/`, 4.1's final mode, or the owner's approval | Each fails: a stage missing; an empty cell; a review cell naming a list file that does not exist | S46-D1 | plan |
| Plan template | `docs/slices/_template/plan.md` has the stage table with the seven stage names, a "Source" column in its decisions table, and a "Rule deviations" section | A template without any of the three fails | S46-D11 | plan |
| Test-plan template | `docs/slices/_template/test_plan.md` names each stage's list and holds the implementation-review questions `AGENTS.md` requires: which wrong behaviour would still pass each test; whether a key, socket or secret reaches a service outside its holders; whether names and purpose comments say what they do | A template without one of them fails | S46-D11 | plan |
| Bundle from the templates | A bundle copied from the templates, with placeholders filled by a fixed sample, passes `scripts/check_docs.py` and the lint gate's header check | — | S46-D11 | plan |
| Decision brief | From throwaway attempt logs and records, the brief lists each unit's last verdict and severity counts, every `owner:` answer, decision concern, `cannot determine` answer and disputed finding, every rejected blocking or high finding with its reason, and the origin-against-found table; a unit with nothing open says so | A record with an unanswered finding, or a log whose hashes do not match its record, makes the script fail instead of writing a brief that omits it | S46-D13 | plan |
| CI line of the brief | A fake API response with every job passed shows the pass; one with a running job shows it running | An unreadable API response, or no run for the head commit, is shown as such, never as a pass | S46-D13 | plan |
| Grill-me in the repository | `.claude/skills/grill-me/SKILL.md` exists, keeps its front matter, then has a `#` title and purpose paragraph, and `AGENTS.md` names it; the lint gate passes a Markdown file with front matter followed by a title and paragraph | The lint gate fails a Markdown file whose front matter is followed by no title | S46-D14 | plan |
| Step references | No live document (outside `docs/archive/`, `docs/slices/archive/` and frozen slice bundles) says "step 1" to "step 4" | A planted "see step 4" in a live document fails | S46-D12 | plan |

## Review-based proof

The plan review, the implementation review and the final review quote, for each of S46-D1 to S46-D14,
the `AGENTS.md` or template text that states it. They check that every rule of the old steps listed
in S46-D12 survives in a stage.

## E2E test plan

None.

## Planned verification commands

- `make tooling-test`
- `make docs-check`
- `make lint`

## Independent review at the implementation PR

After the open mandate, the reviewer answers in the PR body:
1. *Tests:* for each new or changed test, which wrong behaviour would still pass it?
2. *Keys:* does a key, socket or secret now reach a service outside its holders?
3. *Rules:* for each decision, where is the text that states it? Does any rule now contradict another?
   Was any rule of the old four steps lost?
4. *Practicality:* can an author follow the stages for a one-line fix without inventing work ("none,
   with a reason")?
5. *Names and headers:* do new files and names say what they do?

A "yes" to question 1 or 2, a decision without its text, or a contradiction blocks; the rest follow
the severity rules.
