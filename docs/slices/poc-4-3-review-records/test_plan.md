# Slice Test Plan — poc-4-3-review-records

Test plan of slice 4.3 of the agentic-SDLC PoC (issue #40): the tests that show the launcher writes
review records exactly, and that the record check fails on every kind of mismatch.

## Goal

Prove S43-D1 to S43-D8 of [`plan.md`](plan.md):
- the launcher writes records the check accepts, for completed, failed, withheld and interrupted
  attempts;
- the check fails on every kind of mismatch, on answers changed after a recheck and on answers a
  severity does not allow;
- a secret or a local path in a prompt is never sent or written.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S43-D1 to S43-D8.
- Expected values come from the plan and from the hand check of slices 2 and 3 (`probe@d56c69a`).

## Unit test plan

Tooling tests in `tests/tools/`, with the fake `claude` CLI and throwaway records and logs.

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| Launcher writes blocks | A completed attempt leaves Prompt, Evidence and Report blocks under its heading, and the check passes; a prompt or report holding a run of seven backticks gets an eight-backtick fence | — | S43-D1 | plan |
| Blocks of attempts without a report | A failed attempt, a withheld one and one interrupted by a kill keep their Prompt and Evidence blocks and a status line; the check passes for each | — | S43-D1, S43-D3 | plan |
| Parallel reviewers | Two reviewers of one round finishing together leave two whole, separate attempt sections | — | S43-D1 | plan |
| Scan before the call | — | A task prompt, answers section or evidence with a PEM private key, or with the author's `HOME` path, is refused with exit 2 before the start entry: no log line, no record write, no reviewer call; the message names the kind, never the value | S43-D2 | plan |
| Check: blocks | A record written by the launcher passes | Each fails: one changed character in a Prompt, Evidence or Report block; a Report block under another attempt's heading; a block under a heading with no logged attempt; a logged report hash with no block; a missing record | S43-D3 | plan |
| Check: other fences | A fenced snippet inside an answers section is not treated as a block | — | S43-D3 | plan |
| Check: answers after the recheck | — | An answers section changed after a recheck logged its hash fails | S43-D3 | plan |
| Check: allowed answers | Each allowed answer passes: blocking `fixed`; high `owner: <link>`; medium `deferred: #12`; low `rejected: style`; a blocking `rejected` that the next round lists as `accepted`; a medium `decision_concern` answered `owner: <link>` | Each fails: a finding without a row; a row with another first word; `deferred` without an issue number; a blocking finding `deferred`; a high finding `rejected` with no next round and no owner link; a `decision_concern` answered `rejected`; a row for an ID not in the report | S43-D4 | plan |
| Earlier attempts | A log whose attempts have no `record_blocks` field passes whatever its record holds | — | S43-D5 | plan |
| Recheck from the record | A recheck reads the earlier report from the Report block, with the released file deleted | A Report block whose hash differs from the end entry refuses the recheck | S43-D6 | plan |
| `docs-check` | `make docs-check` runs the record check and fails when it fails | — | S43-D3 | plan |

## Review-based proof

The `AGENTS.md` texts of S43-D8 and the `docs-check` row, and DPL-010's status, are proved by review:
the implementation review quotes them.

## E2E test plan

None.

## Assumptions and fixtures

- Private keys in fixtures are generated at test time, as in the existing secret-check tests.

## Planned verification commands

- `make tooling-test`
- `make docs-check`
- `make lint`

## Independent review at the implementation PR

After the open mandate, the reviewer answers in the PR body:
1. *Tests:* for each new or changed test, which wrong behaviour would still pass it, for example a
   check that compares hashes as a set, or one that passes an empty record?
2. *Keys:* does a key, socket or secret now reach a service outside its holders? Can a secret or an
   operational detail reach the reviewer or a record through the launcher's writing?
3. *Names and headers:* do new files and names say what they do?

A "yes" to question 1 or 2 blocks; findings on question 3 follow the severity rules.
