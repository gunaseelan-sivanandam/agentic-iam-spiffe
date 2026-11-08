# Slice Test Plan — poc-4-1-review-prompts

Test plan of slice 4.1 of the agentic-SDLC PoC (issue #38): the tests that show every prompt keeps
its mandate, rechecks get the right inputs, and the severity scale is enforced.

## Goal

Prove S41-D1 to S41-D10 of [`plan.md`](plan.md) with tooling tests. A prompt must never lose the
mandate or its order. A recheck must never run without its earlier report and answers, and never
receives the review record. A report with an unknown or retired kind must fail. The benchmark must
still score stage A's results.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S41-D1 to S41-D10.
- Expected values come from the plan (`plan`) or from the existing tests
  (`existing@c325e7d`), never from watching the new code run.

## Unit test plan

No unit tests under `tests/unit/`: no service code changes. All tests are tooling tests in
`tests/tools/`, run by `make tooling-test`, with the fake `claude` CLI from slice 2.

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| Section order | The prompt holds role, mandate, rules, checklist, evidence, paths, task and output, in that order. The checklist and evidence sections appear only when given. | A task text that says "ignore the mandate" or "only check file X" still leaves the mandate in place, before the rules and the task | S41-D1, S41-D9 | plan |
| Mandate per mode | `initial` and `final` prompts contain the open-mandate sentence verbatim; a `recheck` prompt contains the bounded mandate | A missing or unknown `--mode` is refused before any call | S41-D2, S41-D3 | plan |
| Mode recorded | The start entry's `mode` equals the requested mode | — | S41-D3 | plan |
| Recheck inputs | A recheck prompt contains the reviewer's earlier released report and the answers file verbatim | A recheck is refused before any call if: the same label has no completed attempt in the previous round; there is no `--answers`; the released report's hash differs from the end entry. A marker sentence in the review record never appears in a recheck prompt. | S41-D4 | plan |
| Schema kinds | Findings of all six kinds are accepted | `advisory`, an unknown kind or a missing kind makes the attempt "failed", never a pass, and the report is not released | S41-D5 | plan |
| Severity counts | The end entry's `severity_counts` equals the count of each kind in the released report, with zero for kinds that do not occur | — | S41-D7 | plan |
| Benchmark compatibility | `score()` treats `high`, `medium` and `low` like the old `advisory` (not blocking), and `--report` still reads stage A's results | — | S41-D10 | plan; `existing@c325e7d` (stage A results) |

## E2E test plan

None. No harness test, service, compose file or image changes.

## Assumptions and fixtures

- The fake `claude` CLI prints scripted streams; no test spends tokens.
- Recheck tests write a log with a completed earlier attempt and its released report, as slice 2's
  tests do.

## Planned verification commands

- `make tooling-test`
- `make lint`
- `make qa-quality`
- `scripts/clean_stack.sh`, then `make e2e` and `make qa-evidence`, once at slice 4's close

## Review notes

The rule texts in `AGENTS.md` (S41-D5, D6, D8, D9) are proved by review, not by a test. The review
quotes the text that states each one.

## Independent review at the implementation PR

A reviewer that is not the author ([AGENTS.md — Independent review](../../../AGENTS.md#independent-review))
answers in the PR body, after the open mandate:
1. *Tests:* for each new or changed test, which wrong behaviour would still pass it? Does its assertion
   match the row above?
2. *Keys:* can any key, secret or operational detail reach the reviewer or a public record through the
   new sections, the recheck inputs or the severity counts?
3. *Names and headers:* do new files and names say what they do (coding rule 8)?

A "yes" to question 1 or 2 blocks; findings on question 3 follow the severity rules.
