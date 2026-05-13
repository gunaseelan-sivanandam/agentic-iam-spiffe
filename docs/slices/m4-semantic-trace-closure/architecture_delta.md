# Architecture Delta

## State Inventory

No new authoritative state is introduced.

Existing M4 state remains:

- `m4:budget:<root_token_id>` and request-rate keys
- `m4:registry:<root_token_id>`
- `m4:mint_rate:<root_token_id>`
- `m4:capiss_minted:<token_id>`

## Architecture Alignment

- The shared enforcement module remains the architecture/design mechanism for consistent chain validation.
- The active requirement is adjusted to externally observable enforcement consistency rather than direct proof of implementation reuse.
- The registry model remains Option A; signed receipts remain future scope.
