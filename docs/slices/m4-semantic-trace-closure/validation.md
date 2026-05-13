# Validation

## Required Commands

- `make qa-trace`
- `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_MILESTONES=m4 rogue-tests`
- `docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests`
- `make qa-evidence`
- `make qa-quality`

## Evidence Expectations

- M4 suite includes `M4-T1` through `M4-T14`.
- No active M4 requirement remains in `requirements_without_e2e` unless it is intentionally tracked as a non-black-box/internal invariant.

## 2026-05-08 Results

- `sh -n scripts/rogue_node_tests.sh`: passed.
- `make qa-trace`: passed.
- Targeted M4 E2E: passed, `14/14`.
- Clean full E2E: passed, `46/46`, with two accepted alternate-isolation warnings:
  - `M3.S2-T3`: DNS resolution timeout while reaching OPA from edge.
  - `M3.S2-T5`: DNS resolution timeout while reaching capability-issuer from edge.
- `make qa-evidence`: passed, `validated=46/46`, `warnings=2`.
- `make qa-quality`: passed, unit baseline `164 passed`.
