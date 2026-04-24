# Validation

## Planned checks
- `make qa-trace`
- `make qa-quality`
- targeted M4 E2E for the new observability cases
- full E2E run
- `make qa-evidence`

## Runtime proof
- Allow-flow reconstruction:
  - evidence contains correlated `capiss_mint_decision`, `discovery_registry_write`, and `toolb_enforcement_decision` events for one end-to-end `/search -> /read-file` flow
- Deny/drift proof:
  - evidence contains a deny event for a selected M4 drift-relevant path with exact `reason_code`
- Schema proof:
  - unit tests pin exact event field names and payload completeness on final mint and enforcement events

## Completion notes
- Fill in after implementation:
  - what passed
  - any warning paths
  - what observability work still remains beyond reduced-scope M4
