# agentic-iam-spiffe

Learning project:
Agentic IAM using SPIFFE / SPIRE

## Quick Start

Bring the stack up (build if needed):
```bash
docker compose -f compose/spiffe.compose.yml up -d --build
```

Run the full test suite:
```bash
docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
```

Test profiling is enabled by default (`TEST_PROFILE=1`) and writes:
- `artifacts/rogue-tests/guard_timings.tsv`
- `artifacts/rogue-tests/guard_timings_top25.txt`

Run tests with profiling disabled:
```bash
docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_PROFILE=0 rogue-tests
```

Detailed test specs:
- `docs/test_spec_detailed.md`
- `docs/test_spec.md`

## What exists today
Most production systems already separate authentication and authorization.
- OAuth/OIDC is widely used to obtain access tokens. Services validate tokens (often JWT) and apply permissions using scopes, claims, or roles.
- Many teams use policy decision and enforcement patterns, for example OPA as a policy decision point (PDP) and an API gateway/service/proxy (like Envoy) as the policy enforcement point (PEP). This can give consistent enforcement across services.
- For service-to-service calls, workload identity (including SPIFFE/SPIRE) is increasingly used to authenticate workloads using mTLS and to provide consistent service identity across environments.

## Where the shortcoming shows up
This lab is not claiming today’s systems are “wrong.” The friction appears when workflows become dynamic and multi-step, as in tool-based automation and agentic systems.
- Work gets split across many small components. A single user request can trigger multiple tool calls across multiple services. Keeping permissions minimal across that chain is harder than in a single service call.
- Authority needs to be delegated and reduced safely. Even if you have strong identity and a PDP/PEP, it is still easy to end up with either broad tokens and ad hoc delegation rules.

## What this lab addresses
This lab is a small, reproducible playground for separating “who is calling” from “what they are allowed to do,” and proving it with tests.

### Implemented in this repo (today):
- Strong workload identity using SPIFFE/SPIRE-issued X.509 SVIDs and mTLS.
- A clear ingress boundary using Envoy to terminate mTLS and forward verified identity to internal services under network isolation.
- Explicit authority using capability tokens (Biscuit), minted behind the boundary and enforced at the tool. Authentication alone is not sufficient to perform protected actions.
- M4 governance truth slice for tool-b: chain metadata, derived depth checks (`N=3`), spend/rate enforcement in Redis per `root_token_id`, discovery-registry-gated resource minting, and fail-closed enforcement on trusted-store errors.
- Evidence-based security tests built around a Premise / Exercise / Outcome structure, with artifacts captured so failures can be inspected and false-green tests are less likely.

#### Planned (not implemented yet, goals may evolve):
- Delegation hardening beyond the M4 slice (for example broader multi-tool flows and stronger trust assumptions).
- Attenuation model expansion beyond single-value authority slices.
- Governance expansion (cross-tool analytics, policy lifecycle controls, richer operational safeguards).
- Intent to limits: compile high-level “intent” into enforceable, mechanical limits.
- Intent-constrained issuance: ensure minted authority never exceeds the limits derived from intent.

### Out of scope (explicit non-goals for this lab):
- Host/node compromise
- Multi-node production hardening (HA, real KMS/HSM key management, production-grade observability).
- Cross-trust-domain federation and multi-tenant boundary guarantees.
- Long-lived token revocation mechanics (this lab favors short TTL and issuance controls).
- Agent “intent understanding” correctness: We don’t try to judge whether an agent’s intent is “honest” or “reasonable.” Intent is treated as untrusted input, like any other user-provided text. The lab focuses on turning intent into clear, enforceable limits (what actions, which resources, how long), not on deciding whether the intent itself is true.

## Architecture

### Component-level architecture:

![Component architecture diagram](docs/only_arch.png)

### Network segmentation and trust boundaries:
![Network segmentation diagram](docs/architecture_diagram.png)

# Milestones
## Milestones implemented
### Milestone 1 — Trust domain & node identity
- Establish a single SPIFFE trust domain with SPIRE server and agent, and bootstrap node identity securely.
- Covers node attestation, join-token handling, and deterministic verification of server-side state.

### Milestone 1.5 — Rogue node resistance
- Validate that unauthorized or malformed node admissions cannot expand the trust domain.
- Covers forged tokens, token replay, join-token isolation.

### Milestone 2 — Workload identity & mTLS
 - Issue SPIFFE IDs to workloads and enforce mutual authentication using short-lived X.509 SVIDs.
 - Covers workload attestation, mTLS between workloads, and rejection of unauthenticated or misidentified clients.

### Milestone 2.5 — Ingress boundary with Envoy
 - Introduce Envoy as the sole ingress point that terminates mTLS and propagates verified identity internally.
 - Covers trusted identity headers, network isolation, and prevention of direct access to application services.

### Milestone 3 — Capability issuance & enforcement
 - Separate identity from authority by introducing explicit, scoped capability tokens (based on Biscuit tokens).
 - Covers capability minting behind Envoy, OPA-gated issuance, short TTLs, and enforcement that identity alone is insufficient.

### Milestone 4 — Checkpointed delegation and governance truth (tool-b slice)
 - Adds mandatory chain metadata (`root_token_id`, `token_id`, `parent_token_id`, `delegator_spiffe_id`, `subject_spiffe_id`, `delegation_depth`) on M4 tokens.
 - Enforces chain integrity and derived depth (`effective_depth = chain_length - 1`) at tool enforcement with `N=3`.
 - Enforces per-request budget and rate keyed by `root_token_id` via Redis (trusted shared state).
 - Adds discovery registry flow (`GET /search`) and registry-gated resource minting (`POST /capabilities/resource-mint`).
 - Keeps capiss out of protected request hot path (capiss mints; tool enforces request-time checks).

## Planned Milestones
 - Note: Milestones 5–8 are exploratory and may evolve as architectural choices are validated.
 
### Milestone 5 — Attenuation (TBD)
 - Ensure that delegated or derived capabilities can only reduce, never increase, authority.
 - Covers mechanical constraint narrowing (scope, resources, TTL) and proof that authority strictly monotonically decreases along the chain.

### Milestone 6 — Governance (TBD)
 - Introduce control and visibility over the authority system itself, not individual tokens.
 - Covers auditability of issuance, policy lifecycle control, issuer identity restrictions, and emergency issuance cutoffs (not token revocation).

### Milestone 7 — Turn intent into enforceable limits (TBD)
When an agent says what it wants to do (“intent”), we don’t trust that text as authority. Instead, we convert it into a small set of hard limits the system can actually enforce.
Covers compiling intent into an authority envelope like: allowed actions, allowed resources, max TTL, max delegation depth—so enforcement is deterministic, not “interpretive”.
- Note: the idea is to start small and not directly tackle complex multi page prompts

### Milestone 8 — Ensure issued power never exceeds the intent limits (TBD)

Once those intent-based limits exist, the next risk is an agent requesting more power than its intent should allow. This milestone prevents that by enforcing: requested capability is less than or equal to the intent envelope.
Covers issuer-side checks so every minted capability is a subset of the intent envelope (e.g., can’t ask for broader actions, more resources, or longer TTL than the envelope allows), even if the requester is authenticated.


# Test Specification
- [Test Specification](docs/test_spec_detailed.md)
- [Test Specification with implementation commands](docs/test_spec.md)

## Common commands

Bring the stack up (build if needed):
```bash
docker compose -f compose/spiffe.compose.yml up -d --build
```

Observe the SPIRE agent log (confirm SVID issuance / workload API activity):
```bash
docker compose -f compose/spiffe.compose.yml logs -f --tail=200 spire-agent
```

Run the full test suite:
```bash
docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
```

M4 root mint example (`agent-a` mTLS identity):
```bash
curl -sS --insecure \
  --cert tmp_svid/agent-a_out/svid.0.pem --key tmp_svid/agent-a_out/svid.0.key \
  -H 'Content-Type: application/json' \
  -d '{"aud":"tool-b","act":"read","res":"tool-b:/search"}' \
  https://localhost:9443/capabilities/root-mint
```

M4 discovery + resource flow (high level):
1. Mint root token for `tool-b:/search`.
2. Call `GET /search` on tool-b with that token.
3. Mint a resource token with `POST /capabilities/resource-mint` for discovered `tool-b:/read-file:<id>`.
4. Call `GET /read-file/<id>` on tool-b with that resource token.

By default, test profiling is enabled (`TEST_PROFILE=1`). This writes guard timing artifacts to:
- `artifacts/rogue-tests/guard_timings.tsv`
- `artifacts/rogue-tests/guard_timings_top25.txt`

Run tests with profiling disabled:
```bash
docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_PROFILE=0 rogue-tests
```

## Unit Trust Gates (M4)

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

Run unit tests:
```bash
make unit
```

Run explicit Premise/Exercise/Outcome guard enforcement for unit tests:
```bash
make unit-guard-check
```

Run security invariants only:
```bash
make unit-invariants
```

Run boundary tests only:
```bash
make unit-boundary
```

Run trust gate suite (coverage + invariants + flake check):
```bash
make unit-trust
```

Run strict negative controls (must-fail reason-code checks):
```bash
make unit-negative-controls
```

Run low-mock hybrid critical tests:
```bash
make unit-hybrid-critical
```

Run PR diff coverage gate against a base branch:
```bash
make unit-diff-cov BASE_REF=origin/main
```

Run mutation gate (longer-running):
```bash
make unit-mutation
```

Validate requirement-to-test mapping:
```bash
make traceability-check
```

Coverage gates:
- Total line coverage must be `>= 85%`
- Critical module branch coverage must be `>= 75%` for:
  - `services/capability-issuer/app.py`
  - `services/tool-b/server.py`
- PR changed-line coverage for critical modules must be `>= 90%`.
- Mutation score must be `>= 70%`.

Unit-test traceability specification:
- `docs/unit_test_spec.md`

Unit-test guard contract:
- Every test under `tests/unit/**` must use the `guard` fixture and execute at least one `premise`, one `exercise`, and one `outcome` phase.
- Guard evidence is emitted into pytest/JUnit user properties:
  - `guard_premise_count`
  - `guard_exercise_count`
  - `guard_outcome_count`
  - `guard_complete`
  - `guard_trace_json`

## Clean stack helper
To reset the lab without sudo, use:
```bash
scripts/clean_stack.sh
```

### Note on test-only services

The service `capability-issuer-no-opa-envoy` exists **only for tests**.

Its purpose is to deterministically validate **fail-closed behavior**
of the Capability Issuer when the policy decision point (OPA) is
unavailable.

Key points:
- It is used exclusively in test profiles.
- It has a SPIRE workload entry solely so Envoy can enforce SPIFFE mTLS
  during tests.
- It is not intended as a production deployment pattern.

This service ensures that capability minting never succeeds without
an explicit policy decision.

### Note
- Most code and tests were generated with coding agents and then iteratively hardened. The test suite is designed to avoid false-green security tests (Premise/Exercise/Outcome + evidence artifacts)
