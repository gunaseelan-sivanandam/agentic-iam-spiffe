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
