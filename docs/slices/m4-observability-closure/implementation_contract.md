# Implementation Contract

## Runtime behavior changes
- `tool-b` final enforcement events will use the requirement-aligned field name `subject_spiffe_id`.
- `tool-b` final enforcement events will include `delegator_spiffe_id` when present in token claims.
- `capiss_mint_decision` will include `delegator_spiffe_id` on delegated/resource-mint paths when truthfully available.
- The E2E harness will capture relevant `capability-issuer` and `tool-b` logs into evidence for selected M4 scenarios and assert the expected correlation fields.

## Affected implementation areas
- Functions/modules expected to change:
  - `services/tool-b/server.py`
  - `services/capability-issuer/app.py`
  - `scripts/rogue_node_tests.sh`
  - `trace/tests.yaml`
- Functions/modules expected to be removed or retired:
  - inline duplicated enforcement-event payload assembly in `ToolBHandler._deny` and `ToolBHandler._authorize`
  - obsolete field name `caller_subject_spiffe_id`

## Exact contracts
- APIs/endpoints:
  - no HTTP API changes
- Events/logs:
  - `toolb_enforcement_decision`
    - required: `result`, `reason_code`, `subject_spiffe_id`, `root_token_id`, `token_id`, `parent_token_id`, `delegation_depth`, `aud`, `act`, `res`, `budget_remaining`, `path`
    - optional: `delegator_spiffe_id`
  - `capiss_mint_decision`
    - keep current `REQ-M4-O2` fields
    - add optional `delegator_spiffe_id` on resource-mint paths
  - `discovery_registry_write`
    - retained and used as part of reconstruction evidence
- State keys:
  - no new Redis keys
- Reason codes:
  - no new reason codes in this slice
- Failure modes:
  - log capture failures in E2E must fail the relevant evidence checks

## Test intent
- UT to add:
  - `tool-b` allow and deny event schema exactness
  - `delegator_spiffe_id` propagation when present
  - `subject_spiffe_id` naming consistency
  - `capiss` delegated mint event includes `delegator_spiffe_id`
- E2E/integration to add:
  - allow-flow reconstruction evidence:
    - root mint
    - search
    - resource mint
    - read-file
    - assert correlated `root_token_id` / `token_id` / `parent_token_id` across captured logs
  - deny/drift evidence:
    - repeated delegation depth denial or mint-rate denial
    - assert deny event presence and reason code in evidence

## Explicit non-changes
- no new observability storage backend
- no changes to authorization semantics
- no changes to the reduced-scope offline delegation model
