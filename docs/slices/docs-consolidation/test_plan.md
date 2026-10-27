# Documentation Consolidation — Test Plan

This slice changes documentation only. There are no UT or E2E changes; verification proves that
nothing that reads documentation broke and that the new structure is complete.

## Increment 1 checks
| Check | Command / method | Pass condition |
| --- | --- | --- |
| C1 Trace model unaffected | `make qa-trace` | PASSED with the same counts as before the move (requirements=159, architecture=33, design=131, tests=371) |
| C2 Unit matrix still found | `make traceability-check` | exit 0 (reads `docs/unit_test_spec.md`, which does not move) |
| C3 Unit suite unaffected | `make unit-guard-check` | 348 passed, 0 guard offenders |
| C4 Links resolve | relative-link scan over README, AGENTS, CLAUDE, `docs/*.md`, `docs/slices/README.md` | zero missing targets |
| C5 No live doc points at moved paths | `git grep` for `local_status_capture`, `test_spec_detailed`, `test_spec_readable`, legacy slice paths outside `docs/history/`, `docs/archive/`, and frozen slice bundles | zero hits |
| C6 Slice index complete | every directory under `docs/slices/` (except `_template`, `archive`) has a row in `docs/slices/README.md` | true |
| C7 README test ID example is real | every ID in README `TEST_ONLY=` examples exists in `scripts/rogue_node_tests.sh` | true |
| C8 No secrets newly tracked | pattern scan of `docs/history/implementation_log.md` (JWT, Jira API token, PEM, Bearer/Basic values) | zero hits |
| C9 Rulebook claims are true | every gate/threshold in `AGENTS.md` matches `Makefile` and `.github/workflows/unit-trust.yml` | manual diff, recorded below |

## Increment 2 checks
- Every E2E test ID executed by `scripts/rogue_node_tests.sh` appears in `docs/test_spec.md`.

## Increment 3 checks
- `make docs-check` runs C4–C7 plus the Increment 2 check and is wired into CI.

## Results
### Increment 1 (2026-10-27)
- C1 `make qa-trace`: PASSED, counts unchanged (requirements=159, architecture=33, design=131, tests=371).
- C2 `make traceability-check`: exit 0.
- C3 unit suite: 348 passed, 0 guard offenders.
- C4 links: zero missing targets.
- C5 stale references in live docs: zero.
- C6 slice index: every active and archived bundle has a row.
- C7 README/AGENTS `TEST_ONLY` IDs: all four exist in the harness (`M3.S3-T3`, `M3.S4-T2`, `M5-T1`, `M5-T2`).
- C8 secret scan of `docs/history/implementation_log.md`: zero hits.
- C9 rulebook vs Makefile/CI: gate list, thresholds, critical modules, and diff-coverage scope checked
  against `Makefile`, `scripts/coverage_gate.py`, `scripts/diff_coverage_gate.sh`, `setup.cfg`, and
  `.github/workflows/unit-trust.yml`. Corrected during review: diff coverage applies only to capiss and
  tool-b; env-gated skips are not on `main` yet.
