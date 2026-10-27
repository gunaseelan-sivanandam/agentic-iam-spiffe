# DDR: E2E Shape

## Decision

Add focused M4 E2E cases for:

- authority amplification denial
- wildcard/non-canonical resource denial
- budget and registry TTL bounds
- protected resource use not requiring a capiss hot-path mint call

Map existing M4 and earlier milestone tests for:

- depth lineage semantics
- identity binding
- header boundary
- trusted enforcement placement
- capiss mint-decision audit events

## Rationale

The new cases cover the meaningful externally observable gaps. Existing tests already prove several requirements, but the trace map did not reflect that.
