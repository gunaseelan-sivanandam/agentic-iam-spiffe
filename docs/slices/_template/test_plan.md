# Slice Test Plan

Test plan of slice `<slice-id>`: one sentence on what its tests prove. Replace this paragraph; it is
the document's purpose line (`AGENTS.md`, coding rule 8).

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

## Independent review at the implementation PR
A reviewer that is not the author ([AGENTS.md — Independent review](../../../AGENTS.md#independent-review))
answers in the PR body:
1. *Tests:* for each new or changed test, which wrong failure would still pass it (service down,
   another status, the right status with another reason, another component answering, a missing
   value or empty file read as success)? Does its assertion match the expected-outcome row?
2. *Keys:* does the change make a key, socket or secret reachable by a service outside the holder
   list, through a compose mount, an env var, a Dockerfile `COPY`, an entrypoint or script that
   copies or writes it, or a shared volume?
3. *Names and headers:* does each new file start with a comment that says what the file is for
   ([AGENTS.md, coding rule 8](../../../AGENTS.md#coding-rules)), and do its names say what each part
   does?

A "yes" to question 1 or 2 blocks, under [AGENTS.md — PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion).
Findings on question 3 are fix-or-defer: the author fixes them or the user defers them.
