# Slice Test Plan — poc-4-4-stage-checklists

Test plan of slice 4.4 of the agentic-SDLC PoC (issue #41): how we show the stage checklists exist
in the agreed form, reach each review from the base branch, and would have caught the repository's
past misses.

## Goal

Prove S44-D1 to S44-D13 of [`plan.md`](plan.md):
- the form of the lists, the research sources and the launcher's `--stage` with tooling tests;
- the rule texts, the code list's content, the critiques and the DPL mapping by review.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S44-D1 to S44-D13.
- The DPL entries in `docs/delivery_problem_log.md` (DPL-001 to DPL-011) as test cases for the lists.

## Unit test plan

Tooling tests in `tests/tools/`.

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| List form | Every file in `docs/review_checklists/` starts with a title and a purpose paragraph, has at most 12 numbered questions and a "Blocks at this stage" section, and every question has a `[S:<key>]` tag whose key is a source section of `research.md` | Each fails: 13 questions; a question without a tag; a key not in `research.md`; a tag naming a DPL entry; a missing "Blocks at this stage" section | S44-D3, S44-D4, S44-D9 | plan |
| Types present | Exactly the six artifact types have a list | A list for "final review" or "handoff" fails | S44-D1 | plan |
| Sources researched | `research.md` has a section for each source named in S44-D1; a paid standard's section is marked "title only" | A named source without a section fails | S44-D1, S44-D2 | plan |
| Review-prompt research | `research.md` has a "Review prompt" section with drafts of the initial, recheck and final mandates; every draft sentence has a `[S:<key>]` tag naming a source section and names a failure mode | A draft sentence without a tag, or a missing draft, fails | S44-D13 | plan |
| Missing-things questions | The proof question is in the plan-and-test-plan, requirements, unit-test and E2E-test lists; the CI-job question in the plan-and-test-plan and code lists | — | S44-D5 | plan |
| `--stage` | A review with `--stage requirements` gets the base commit's requirements list, also when the branch under review changes that list (the review gets the base's text); two `--stage` values give both lists; the start entry records each stage and its SHA-256 | Refused before any call: an unknown name; an initial review without `--stage` when the base has lists; a final review with `--stage` | S44-D7 | plan |
| No lists at the base | A review whose base has no `docs/review_checklists/` runs, and its prompt and start entry say "no checklist at base <commit>" | — | S44-D7 | plan |
| Benchmark lists | A benchmark case on a commit without lists gets the list of its artifact type from the runner's fixed commit, and the result's identity records that commit | — | S44-D12 | plan |

## Review-based proof

- **Rule texts:** the implementation review quotes the `AGENTS.md` text for S44-D4, S44-D6 and
  S44-D11, and checks that the code list (S44-D8) repeats none of `make lint`'s rules or the coding
  rules.
- **Citations:** the critiques check a sample of the quotes in `research.md` against what a public
  source could say, and flag any clause that is not marked "title only" for a paid standard.
- **DPL mapping:** the critiques and the implementation review check that every DPL entry has a
  question at the stage where the miss happened, or a reason why not (S44-D9). The plan review cannot,
  because the lists do not exist yet.
- **Critiques:** Opus and Sonnet each review the drafts with the open mandate (S44-D10). Every
  finding gets an answer under 4.1's severity rules.

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
2. *Tests:* for each new or changed test, which wrong behaviour would still pass it?
3. *Keys:* does a key, socket or secret now reach a service outside its holders?
4. *Names and headers:* do new files and names say what they do?

A gap in question 1 for a DPL entry, or a "yes" to question 2 or 3, blocks; the rest follow the
severity rules.
