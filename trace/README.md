# Traceability Model

This folder defines the test-side authored trace inputs.

## Files
- `tests.yaml`: E2E and future integration test metadata plus evidence prefixes for E2E suites.

Strict model:
- `docs/requirements.md -> docs/architecture.md -> source-embedded DD tags -> trace/tests.yaml`
- `docs/requirements.md` is the only authored requirement source.
- `docs/architecture.md` is the only authored architecture source.
- Detailed design is authored directly in service implementation-source comments under `services/**` as unique `DD-*` blocks.
- Unit-test traceability is authored directly in `tests/unit/**` as unique `UT-*` blocks.
- `trace/tests.yaml` is typed by non-unit test layer:
  - `e2e_suite/e2e_case -> source_requirements`
  - `integration_case -> source_architecture`
- Structural correctness is enforced.
- Coverage gaps are reported explicitly and are not auto-filled.

## Validation
Run from repo root:

```bash
make qa-trace
```

Output:
- `artifacts/quality/traceability_report.json`
- `artifacts/quality/design_index.json`

## Evidence check
After running E2E tests, validate expected guard artifacts:

```bash
make qa-evidence
```

Output:
- `artifacts/quality/evidence_report.json`
- Warnings are reported separately for accepted alternate-success paths (`warning_reason_*.txt`).
- Any passing test that still leaves `fail_reason.txt` causes `qa-evidence` to fail.
