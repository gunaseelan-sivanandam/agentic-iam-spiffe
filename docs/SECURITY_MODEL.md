## Security Model

This lab demonstrates the separation of identity (SPIFFE) and authority
(capabilities) using explicit network boundaries and policy checks.

### Trust Boundaries

- Envoy is the SPIFFE mTLS termination point and the only component allowed to
  inject `x-spiffe-id`. Services trust that header only because they are isolated
  on app networks that only Envoy can reach.
- The Capability Issuer and tool-b do not accept direct client connections.
  Clients must pass through Envoy, which enforces mTLS and identity validation.

### OPA Policy Boundary

- OPA is private on `capiss_app_net` and has no published ports.
- The Capability Issuer fails closed if OPA is unavailable or errors.
- Policy decisions are made only by OPA; the issuer does not embed allow/deny
  logic beyond structural request validation.

### Capability Issuer Key Bootstrap

- Biscuit signing keys are created or loaded from a configured volume.
- The issuer publishes a public key to the same volume for verification by
  tool-b. The private key never leaves the issuer container.

### Identity vs Authority

- Identity alone is insufficient to access `/secret`. tool-b requires both
  `x-spiffe-id` and a valid Biscuit token with matching `sub` and scoped
  `aud/act/res` claims.
- Tokens are short-lived; tool-b enforces expiry (`exp`) and rejects expired
  tokens.

### Failure Modes

- Missing `x-spiffe-id` or missing/invalid tokens are rejected.
- OPA unavailability results in denial for minting (fail-closed).
- Capability verification failures return explicit reasons in this lab to make
  behavior observable; production systems usually generalize these errors.
