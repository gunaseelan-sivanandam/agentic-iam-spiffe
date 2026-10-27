# Requirements Delta

## Requirement changes
- Tighten `REQ-M4-O1` to make the final enforcement-event contract explicit for reduced M4:
  - one final audit event per protected request allow/deny path
  - `subject_spiffe_id`
  - `root_token_id`, `token_id`, `parent_token_id`, `delegation_depth`
  - `delegator_spiffe_id` when present in the token chain
  - evaluated `aud`, `act`, `res`
  - `budget_remaining`
  - `reason_code`
- Tighten `REQ-M4-O3` so “chain reconstruction” is explicitly defined for the current reduced scope:
  - reconstructable from `capiss_mint_decision` + `toolb_enforcement_decision` + discovery-registry write events
  - uses `root_token_id`, `token_id`, `parent_token_id`, `delegation_depth`, `subject_spiffe_id`, `delegator_spiffe_id`, `policy_hash`, and `reason_code`
- Tighten `REQ-M4-O4` so drift visibility is defined as:
  - emitted audit data is sufficient for offline analysis
  - no live analytics or dashboard subsystem required in the reduced scope

## Ambiguities removed
- “audit event” becomes “one final event per allow/deny decision path” rather than helper-event best effort.
- “who delegated to whom” is constrained to the current reduced-scope token model and must be reconstructable from emitted chain identifiers and subject/delegator fields.
- “drift visibility” is satisfied by emitted data fields and evidence capture, not by a new analytics service.

## Black-box contract
- A reviewer must be able to prove reduced-scope M4 mint and enforcement history from container-log evidence alone for representative allow and deny flows.
