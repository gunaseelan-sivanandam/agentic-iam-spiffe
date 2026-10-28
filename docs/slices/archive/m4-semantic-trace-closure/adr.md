# ADR: M4 Semantic Trace Closure

## Decision

Close trace gaps by combining three actions:

- add focused E2E checks where behavior is externally observable
- map existing passing E2E evidence where it already proves the requirement
- move internal design or roadmap claims out of active black-box requirement language

## Alternatives Considered

- Map every M4 requirement to the broad M4 suite without changing tests.
- Add one E2E per requirement even for internal design claims.

## Rationale

Broad mappings alone would make the trace graph look cleaner without improving trust. One test per internal design claim would also be misleading because E2E cannot prove implementation reuse. This slice keeps black-box proof honest while still closing requirements that are externally observable.
