# M4 Semantic Trace Closure Plan

## Goal

Close the remaining M4 semantic trace gaps without adding proof that the runtime cannot actually provide.

## Scope

- Audit active M4 requirements against current reduced-scope behavior.
- Add black-box E2E checks for externally observable gaps.
- Map existing E2E evidence to requirements where the evidence already proves the requirement semantics.
- Reword requirements that were expressing internal design or future roadmap as active black-box requirements.
- Update stale implementation status notes.

## Out of Scope

- New M4 feature behavior.
- Pure offline resource delegation.
- Cross-subject delegation.
- Signed discovery receipts.
- New observability storage or visualization.

## Acceptance

- `make qa-trace` passes.
- M4 targeted E2E passes.
- Full E2E remains green.
- M4 requirement text no longer overstates the reduced-scope implementation.
