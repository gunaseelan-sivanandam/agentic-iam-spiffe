# DDR

## Design decision
- Introduce one `tool-b` enforcement-event helper and align all final audit events on a shared reduced-scope schema designed for reconstruction and drift analysis.

## Alternatives considered
- Option A: keep inline `log_event(...)` calls in `_deny` and `_authorize`
  - pros
    - smallest code diff
  - cons
    - higher drift risk between allow and deny payloads
    - harder to retire obsolete field names cleanly
- Option B: add one `log_enforcement_decision(...)` helper in `tool-b`
  - pros
    - one schema owner
    - simpler exact UT assertions
    - easier cleanup of legacy field names
  - cons
    - requires a small refactor
- Option C: generic shared logging helper across services
  - pros
    - one logging utility
  - cons
    - services still need different fields and semantics
    - adds abstraction without enough payoff in this slice

## Chosen option
- Option B.
- Reason:
  - it is enough to eliminate schema drift in `tool-b` without over-generalizing cross-service logging concerns
  - it makes removal of obsolete fields and duplicated inline logic explicit

## Rejected options
- Inline logging is rejected because this slice is primarily about schema completeness and audit consistency.
- A shared cross-service logging helper is rejected because `capiss` and `tool-b` still own different final event semantics.
