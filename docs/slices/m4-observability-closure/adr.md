# ADR

## Architecture decision
- Use stdout JSON audit events plus harness-captured evidence as the reduced-scope M4 observability model instead of adding a new audit store or analytics service.

## Alternatives considered
- Option A: stdout JSON events plus harness capture
  - pros
    - matches current runtime architecture
    - keeps black-box proof tied to actual running services
    - avoids adding another trusted subsystem
  - cons
    - no live query interface
    - correlation happens offline in evidence review
- Option B: Redis-backed audit/event store
  - pros
    - centralized query surface
  - cons
    - mixes governance state with observability
    - adds retention/schema complexity and another hidden dependency
- Option C: separate log collector / analytics service
  - pros
    - clearer observability architecture
  - cons
    - too large for the reduced M4 scope
    - introduces a new service and operational trust boundary

## Chosen option
- Option A.
- Reason:
  - it preserves the current minimal runtime architecture
  - it gives black-box proof through the same containerized runtime the tests already exercise
  - it avoids introducing a new hidden dependency just to prove observability behavior

## Rejected options
- Redis-backed audit storage and a standalone observability service are rejected for the reduced M4 slice because they would expand the architecture beyond the current milestone goal.
