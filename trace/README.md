# Traceability Model

This folder defines the bidirectional traceability source of truth.

## Files
- `design.yaml`: detailed design slices mapped to authored architecture IDs plus code paths.
- `tests.yaml`: unit/E2E test mappings to design IDs (and evidence prefixes for E2E suites).

Strict model:
- `docs/requirements.md -> docs/architecture.md -> trace/design.yaml -> trace/tests.yaml`
- `docs/requirements.md` is the only authored requirement source.
- `docs/architecture.md` is the only authored architecture source.
- `trace/design.yaml` and `trace/tests.yaml` do not carry direct requirement IDs.
- Requirement-to-test coverage is derived transitively by the validator.

## Validation
Run from repo root:

```bash
make qa-trace
```

Output:
- `artifacts/quality/traceability_report.json`

## Evidence check
After running E2E tests, validate expected guard artifacts:

```bash
make qa-evidence
```

Output:
- `artifacts/quality/evidence_report.json`
- Warnings are reported separately for accepted alternate-success paths (`warning_reason_*.txt`).
- Any passing test that still leaves `fail_reason.txt` causes `qa-evidence` to fail.
