# Slice Plan

## Goal
- Close the remaining reduced-scope M4 observability work by making enforcement and mint audit events sufficient for runtime-visible proof, chain reconstruction, and offline drift analysis without introducing a new storage subsystem.

## Success criteria
- `tool-b` emits one final `toolb_enforcement_decision` event for every protected-request allow or deny path with a stable schema aligned to `REQ-M4-O1`.
- `capiss_mint_decision` and `toolb_enforcement_decision` together carry enough correlated fields to reconstruct the current reduced-scope delegation chain from runtime evidence.
- The E2E harness captures log evidence for at least one allow reconstruction flow and one deny/drift-relevant flow.
- `REQ-M4-O1`, `REQ-M4-O3`, and `REQ-M4-O4` gain authored runtime mappings in `trace/tests.yaml`.

## In scope
- requirement tightening for reduced-scope observability
- architecture updates for audit-event ownership and evidence capture
- `capiss` and `tool-b` final audit-event schema alignment
- E2E log-evidence capture and assertions
- retirement of obsolete audit-field names and duplicated inline logging

## Out of scope
- new log storage backends
- dashboards or live analytics systems
- changes to enforcement or mint authorization decisions themselves
- non-M4 observability work

## Affected authored sources
- Requirements:
  - `REQ-M4-O1`
  - `REQ-M4-O3`
  - `REQ-M4-O4`
- Architecture:
  - `ARCH-012`
  - `ARCH-015`
  - `ARCH-016`
  - `ARCH-019`
- Runtime proof:
  - new M4 observability E2E cases and evidence artifacts

## Review notes
- Logging remains append-only JSON on stdout.
- Runtime proof comes from harness-captured container logs, not from code inspection or a new persisted observability service.
- Current reduced M4 model is still offline self-delegation; reconstruction must reflect that actual model rather than inventing multi-subject online delegation.
