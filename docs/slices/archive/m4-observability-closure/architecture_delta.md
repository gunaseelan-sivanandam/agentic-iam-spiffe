# Architecture Delta

## Responsibility changes
- `ARCH-012 capability-issuer`
  - remains the owner of final mint-decision events
  - extends event schema with any missing chain-reconstruction fields required by reduced-scope M4
- `ARCH-015 tool-b`
  - becomes the explicit owner of final enforcement-decision events for all protected request outcomes
  - aligns the event schema to the requirements and removes field-name ambiguity
- `ARCH-019 rogue-tests Harness`
  - becomes the runtime evidence capture point for observability proof by collecting relevant container logs into per-test evidence

## Authoritative state inventory

| State / Key | Store / System | Writer | Reader | TTL / Lifecycle | Decision impact | Type |
|---|---|---|---|---|---|---|
| `capiss` stdout JSON events | container logs / evidence artifacts | capability-issuer | reviewers, harness, operators | retained per container runtime and copied per test evidence | proves mint decisions, policy reason, chain checkpoint creation | Authoritative evidence |
| `tool-b` stdout JSON events | container logs / evidence artifacts | tool-b | reviewers, harness, operators | retained per container runtime and copied per test evidence | proves enforcement allow/deny, request-time chain/budget context | Authoritative evidence |
| `discovery_registry_write` events | container logs / evidence artifacts | tool-b | reviewers, harness, operators | retained per container runtime and copied per test evidence | proves discovery expansion under a `root_token_id` | Authoritative evidence |
| `m4:registry:<root_token_id>` | Redis | tool-b | capability-issuer | TTL bounded to root-token lifetime | governs new-resource mint eligibility | Authoritative state |
| `m4:budget:<root_token_id>` and request-rate keys | Redis | tool-b, with root initialization from capability-issuer | tool-b | TTL bounded to root-token lifetime | governs request-time spend/rate | Authoritative state |
| `m4:mint_rate:<root_token_id>` | Redis | capability-issuer | capability-issuer | TTL bounded to root-token lifetime | governs new-resource mint fan-out | Authoritative state |
| `m4:capiss_minted:<token_id>` | Redis | capability-issuer | capability-issuer, tool-b | TTL bounded to token lifetime | proves trusted issuer provenance for resource-changing child tokens | Authoritative state |

## Hidden behavior disclosure
- `tool-b` currently emits final enforcement events, but the event schema is not yet fully aligned to the authored requirements because it uses `caller_subject_spiffe_id` rather than the requirement term `subject_spiffe_id`.
- Chain reconstruction currently depends on correlating multiple event types plus Redis-backed state decisions, but the harness does not yet capture those logs as authored evidence.
- Reduced-scope M4 observability will continue to rely on stdout JSON events plus test-evidence capture rather than a new observability backend.
