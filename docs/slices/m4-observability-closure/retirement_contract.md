# Retirement Contract

## Logic to remove
- Duplicated inline `toolb_enforcement_decision` payload assembly once a helper owns the final schema
- Obsolete field name `caller_subject_spiffe_id`

## Artifact cleanup
- Update docs/spec text that refers to the old field name or treats observability as a future-only concern for reduced M4
- Remove stale test expectations that still assert `caller_subject_spiffe_id`

## Deferred retention
- No cleanup of the broader `docs/unit_test_spec.md` process in this slice
- No new dashboarding or analytics artifacts are introduced or retired here
