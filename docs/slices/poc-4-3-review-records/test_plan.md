# Slice Test Plan — poc-4-3-review-records

Test plan of slice 4.3 of the agentic-SDLC PoC (issue #40): the tests that show the launcher writes
review records exactly, and that the record check fails on every kind of mismatch.

## Goal

Prove S43-D1 to S43-D7 of [`plan.md`](plan.md):
- the launcher writes records the check accepts;
- the check fails on every kind of mismatch and on unanswered findings;
- a secret in a prompt is never written.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S43-D1 to S43-D7.
- Expected values come from the plan, and from the hand check of 2026-11-08 (`probe@` slices 2 and 3:
  13 and 8 matching blocks).

## Unit test plan

Tooling tests in `tests/tools/`: the launcher with the fake `claude` CLI, and the record check on
small fixture records and logs.

| Area | Passes when | Fails when | Proves | Source |
| --- | --- | --- | --- | --- |
| Launcher writes blocks | After a completed attempt, the record holds the task prompt and the released report verbatim, under the attempt's heading, and the check passes. A failed attempt adds its prompt and status. | — | S43-D1 | plan |
| Fence length | A prompt that contains a fence of six backticks is written inside a fence of seven or more, and read back byte for byte | — | S43-D1 | plan |
| Prompt scan | — | A task prompt containing a PEM private key (generated at test time) is not written into the record; the message names the kind and location, not the value | S43-D2 | plan |
| Check: match | A record whose blocks match its log passes | Each fails: a block changed by one character; an extra block with no logged hash; a logged hash with no block; a record file missing for a logged attempt | S43-D3 | plan |
| Check: answers | Every finding answered `fixed`, `deferred #N` or `declined <reason>` passes | Each fails: a finding without an answer; `deferred` without an issue; a `high` finding deferred without "owner deferred" | S43-D4 | plan |
| Converted records | `review_slice_2.md` and `review_slice_3.md` pass after conversion, with the same blocks (by hash) as before | — | S43-D5 | `probe@` the hand check |
| Unlogged records | A record with no attempt log (slice 1, plan reviews) is not checked and does not fail | — | S43-D5 | plan |
| `docs-check` | `make docs-check` runs the record check and fails when it fails | — | S43-D3 | plan |

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
1. *Tests:* which wrong behaviour would still pass each new test, for example a check that compares
   rendered views, or one that passes an empty record?
2. *Keys:* can a secret or an operational detail reach a record through the launcher's writing?
3. *Names and headers.*

A "yes" to question 1 or 2 blocks.
