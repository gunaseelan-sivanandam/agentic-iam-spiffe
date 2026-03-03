# AGENTS.md (Unit Tests)

## Purpose
This file is the unit-test operating guide for coding agents.
Use it when creating or updating tests under `tests/unit/**`.

## Scope
- Applies only to unit tests in:
  - `tests/unit/capiss/`
  - `tests/unit/toolb/`
  - shared unit helpers in `tests/unit/`
- Integration/E2E harness guidance stays in the repo-root `AGENTS.md`.

## Required test style (hard rule)
- Every unit test must use the `guard` fixture from `tests/unit/conftest.py`.
- Every unit test must execute explicit guard phases:
  - at least one `guard.premise(...)`
  - at least one `guard.exercise(...)`
  - at least one `guard.outcome(...)`
- Use clear step names describing intent and expected behavior.
- For security-deny paths, assert exact deny reasons (for example `sub_mismatch`, `depth_exceeded`, `store_unavailable`).

## Guard evidence emitted by tests
The guard framework attaches the following report properties per test:
- `guard_premise_count`
- `guard_exercise_count`
- `guard_outcome_count`
- `guard_complete`
- `guard_trace_json`

## Exemptions
- Marker `guard_exempt` exists only for exceptional local debugging.
- Exemptions are disallowed by default and should not be used in CI paths.

## Unit-test commands
Run from repo root.

- Full unit suite:
  ```bash
  make unit
  ```
- Guard integrity gate (required):
  ```bash
  make unit-guard-check
  ```
- Trust gate bundle:
  ```bash
  make unit-trust
  ```
- Invariants only:
  ```bash
  make unit-invariants
  ```
- Boundary tests only:
  ```bash
  make unit-boundary
  ```
- Negative controls only:
  ```bash
  make unit-negative-controls
  ```
- Hybrid critical tests only:
  ```bash
  make unit-hybrid-critical
  ```
- Coverage gate:
  ```bash
  make unit-cov
  ```
- Diff coverage gate:
  ```bash
  make unit-diff-cov BASE_REF=origin/main
  ```
- Mutation gate:
  ```bash
  make unit-mutation
  ```
- Requirements traceability check:
  ```bash
  make traceability-check
  ```

## Quality thresholds (CI expectations)
- Total line coverage: `>= 85%`
- Branch coverage for critical modules: `>= 75%`
  - `services/capability-issuer/app.py`
  - `services/tool-b/server.py`
- Diff coverage on changed lines (critical modules): `>= 90%`
- Mutation score: `>= 70%`
- Guard integrity: zero unit tests missing Premise/Exercise/Outcome phases

## Primary references
- Unit trust spec: `docs/unit_test_spec.md`
- Requirements source: `docs/requirements.md`
- Guard fixture and enforcement: `tests/unit/conftest.py`
