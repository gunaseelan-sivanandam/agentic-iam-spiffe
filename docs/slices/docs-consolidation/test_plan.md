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
- C10 Every E2E test ID executed by `scripts/rogue_node_tests.sh` has exactly one heading in
  `docs/test_spec.md`, and no heading names a test the harness does not run.
- C11 Each M5 entry is written from the test body in the harness (guards read one by one), not
  from the test title.

## Increment 3 checks
- C12 `make docs-check` runs C4–C7 and C10, passes on the repo, and is part of `make qa-quality`
  and a CI job.
- C13 Every `docs-check` rule fails on a broken input (`tests/tools/test_check_docs.py`).
- C14 `SECURITY_MODEL.md` claims are verified against the running stack before being carried into
  `docs/architecture.md`; false claims are recorded in `docs/open_problem_log.md`.

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

### Increments 2 and 3 (2026-10-27)
- C10: 120 harness test IDs, 120 spec headings, none missing, none stale, no duplicates.
- C11: all 58 M5 entries written from the guard code; five entries carry a note where the title
  over-claims (M5-T19, T21, T34, T35, T36).
- C12: `make docs-check` PASSED (13 live documents); `make qa-quality` PASSED; CI job `docs-check`
  added to `.github/workflows/unit-trust.yml`.
- C13: `tests/tools/test_check_docs.py` 16 passed, each asserting the exact problem message.
  `tests/shell/test_varambu_output.sh` 9/9 passed, and exits 1 when its library is broken
  (checked with a mutated copy).
- C14: OPA isolation, fail-closed minting, and Envoy-only identity injection confirmed in compose
  and code. "The private key never leaves the issuer container" is false — the key file is
  readable as root in `tool-b`, `jira-tool`, `jira-mcp-gateway`, and `rogue` → OPL-005.
- Regression: full E2E on `main` (`fe86c35`, code identical to this branch) 120/120, `make qa-evidence`
  PASSED (119 validated, 1 skipped); `make qa-trace` counts unchanged; 348 unit tests passed.