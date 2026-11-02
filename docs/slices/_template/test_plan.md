# Slice Test Plan

## Goal
- Describe what this test plan proves about the approved slice behavior.

## Inputs
- Link this test plan back to the approved `plan.md`.
- List the requirements and agreed design choices this test plan covers.

## Unit test plan
- List the UT areas to add or change.
- For each UT area, describe:
  - behavior under test
  - deny or failure paths to pin
  - expected trace or DD/UT linkage

## E2E test plan
- List the black-box scenarios to add or change.
- For each E2E scenario, describe:
  - premise
  - exercise
  - outcome
  - required evidence artifacts
- For every E2E test added or changed, fill the expected-outcome table. The harness asserts each row
  exactly; `make test-lint` rejects loose checks (`assert_file_any`, `401|403`, broad error regexes,
  `!= 200`, a non-zero exit alone, a test with only negative greps).

| Test | By | Signature | Twin | Source | Replaces |
| --- | --- | --- | --- | --- | --- |
| harness ID | component that must produce the outcome | exact outcome: status + `reason`, curl exit code, exact log line | positive control on the same route: a test ID, or `internal` (a premise in the same test) | `plan`, `probe@<commit>` (observed before the change), `existing@<commit>` | the loose check it replaces, or — |

Every negative test has a twin. A `probe@` value is observed before any change; if it contradicts a
`plan` value, stop for the user instead of changing the row (`AGENTS.md`, slice workflow step 2).

## Assumptions and fixtures
- List mock, live, or environment assumptions needed by the tests.
- State the default mode and any explicit opt-in mode.

## Planned verification commands
- `make unit-guard-check`
- `make unit-trust`
- Targeted E2E run:
- `make qa-trace`
- `make qa-quality`
- `make qa-evidence`

## Review notes
- Record any test-design assumptions that must be approved before implementation begins.
- Record per-invocation model, explicit medium/high effort and reason, duration, turns/tools,
  uncached/cached input, output and reported USD estimate. Include unsuccessful attempts and
  unknowns; do not label estimates as subscription billing or retain private review content.
- For each finding/fix, identify the underlying failure class and concrete affected stages or
  artifact types, or justify why it is local. General rules belong in general process/design
  authority, with fixture scenarios testing them; broader baseline changes still need approval.
- For evidence reuse, identify the approved delivery policy, relevant input/output revisions and
  record-only exceptions. CI conclusions must match actual head, target, tested base/merge and mode.
- If acceptance logic, policy, schema or verification configuration changes, plan independent known-good/bad/missing/stale
  proof checks. Do not rely solely on the changed checker's own pass result.
- Keep reviewer detection, controller containment and evidenced root-cause resolution distinct.
  Record human execution assistance separately from expected approvals and autonomous-run claims.

## Independent review at the implementation PR
An independent Claude reviewer with a different model from the Codex author/fixer answers in
an attributed report, summarized and linked from the PR body:
1. *Tests:* for each new or changed test, which wrong failure would still pass it (service down,
   another status, the right status with another reason, another component answering, a missing
   value or empty file read as success)? Does its assertion match the expected-outcome row?
2. *Keys:* does the change make a key, socket or secret reachable by a service outside the holder
   list, through a compose mount, an env var, a Dockerfile `COPY`, an entrypoint or script that
   copies or writes it, or a shared volume?

A "yes" to either blocks, under [AGENTS.md — PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion).
