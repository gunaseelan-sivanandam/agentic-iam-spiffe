# Agentic IAM with SPIFFE — Current Architecture

This document describes the current implemented architecture in this repository.
It is the authoritative architecture source for traceability.

Scope notes:
- This document describes the current implementation only.
- It does not describe target-state or future architecture.
- `Satisfies` lists identify which requirements each section is responsible for satisfying.

## Diagrams

### Component Architecture

This diagram shows the main runtime components and their trust-oriented relationships in the current implementation.

![Component architecture diagram](only_arch.png)

### Network Architecture

This diagram shows the current network segmentation and boundary layout used by the stack.

![Network architecture diagram](architecture_diagram.png)

## ARCH-001 Trust Bootstrap and Node Admission

Type: Logical
Satisfies: REQ-G-R2, REQ-G-R3, REQ-M1-R1, REQ-M1-R2, REQ-M1-R3, REQ-M1-R4, REQ-M1-R5, REQ-M1-R6, REQ-M1-R7, REQ-M1-R8, REQ-M1-R9, REQ-M1-R10, REQ-M1-R11, REQ-M1-R12, REQ-M1-R13, REQ-M1-R14, REQ-M1-R16, REQ-X-R1, REQ-X-R7

Overview:
This subsystem establishes the SPIFFE trust domain, controls how nodes join it, and keeps bootstrap authorization explicit rather than implicit. Its job is to make node admission a governed act instead of a side effect of reachability or startup order.

Trust/Responsibility:
It owns node attestation, join-token based bootstrap, and the server-side state that proves which nodes are actually admitted. It is the primary security locus for preventing rogue node admission, replayed bootstrap material, and duplicate or drifting admission paths.

Interactions:
It connects SPIRE server, SPIRE agent, and bootstrap token initialization. It also underpins the negative attestation tests that validate forged, missing, or replayed bootstrap material.

## ARCH-002 Workload Identity Issuance and Secret Isolation

Type: Logical
Satisfies: REQ-G-R1, REQ-G-R2, REQ-G-R3, REQ-M2-R1, REQ-M2-R2, REQ-M2-R3, REQ-M2-R4, REQ-M2-R5, REQ-M2-R6

Overview:
This subsystem governs workload identity issuance after the trust domain is established. It separates authorization to receive an SVID from simple access to files, sockets, or container runtime surfaces.

Trust/Responsibility:
Its responsibility is to ensure that only explicitly registered workloads receive identities and that identity material for one workload is not exposed to another. It also preserves the distinction between Workload API access, file access, and actual identity issuance.

Interactions:
It is implemented through SPIRE workload registration, the shared agent runtime, and the mounted Workload API paths used by workloads such as tool-b, capability-issuer-envoy, and agent-a.

## ARCH-003 Boundary-Authenticated Transport and Identity Propagation

Type: Logical
Satisfies: REQ-M2-R7, REQ-M2-R8, REQ-M2-R9, REQ-M2-R10, REQ-M2-R11, REQ-M2-R12, REQ-M2-R13, REQ-M2-R14, REQ-M2-R15, REQ-M2-R16, REQ-M2-R17, REQ-M2-R18, REQ-M2-R19, REQ-M2-R20, REQ-M2-R21, REQ-M25-R1, REQ-M25-R2, REQ-M25-R3, REQ-M25-R4, REQ-M25-R5, REQ-M3-R8, REQ-M3-R9, REQ-M4-E4, REQ-M4-E5, REQ-X-R2

Overview:
This subsystem establishes the trusted edge/app boundary pattern. It terminates mTLS at Envoy, derives verified caller identity from the authenticated connection, and forwards requests inward only under the isolated boundary model.

Trust/Responsibility:
Its responsibility is to prevent direct application reachability from untrusted networks and to make trusted identity headers meaningful only inside the protected boundary. This is where transport authentication becomes a trustworthy authorization input.

Interactions:
It connects edge clients to `tool-b-envoy` and `capability-issuer-envoy`, then forwards verified requests into the internal application networks. It also includes the special no-OPA envoy path used to validate fail-closed mint behavior.

## ARCH-004 Capability Issuance and Policy Decision

Type: Logical
Satisfies: REQ-G-R1, REQ-G-R2, REQ-G-R3, REQ-M3-R3, REQ-M3-R4, REQ-M3-R5, REQ-M3-R6, REQ-M3-R7, REQ-M3-R10, REQ-M3-R11, REQ-M3-R12, REQ-M3-R13, REQ-M3-R14, REQ-M3-R15, REQ-M3-R25, REQ-M4-D1, REQ-M4-D2, REQ-M4-D3, REQ-M4-D4, REQ-M4-B7, REQ-M4-P1, REQ-M4-E3, REQ-M4-O2, REQ-X-R6

Overview:
This subsystem mints explicit authority artifacts after policy evaluation. It keeps identity and authority separate, treats requested authority as untrusted input, and turns allowed authority into signed capability tokens with enforceable fields.

Trust/Responsibility:
Its responsibility is to gate minting on policy, enforce required authority fields at issuance time, and ensure root or delegated tokens are minted centrally rather than inferred by clients. It is also where new-resource minting is checked against discovery-derived proof in the current M4 slice. For M4 canonical-resource enforcement, mint-time authority is expected to use canonical `tool-b:/...` resources only.

Interactions:
It connects the capability issuer, the policy decision point, and the ingress boundary that supplies verified caller identity. It also interacts with shared state when root budget initialization, formula-based new-resource mint-rate enforcement, and registry-gated resource minting are needed.

## ARCH-005 Request-Time Capability Enforcement

Type: Logical
Satisfies: REQ-G-R1, REQ-G-R2, REQ-G-R3, REQ-M3-R1, REQ-M3-R2, REQ-M3-R16, REQ-M3-R17, REQ-M3-R18, REQ-M3-R19, REQ-M3-R20, REQ-M3-R21, REQ-M3-R22, REQ-M3-R23, REQ-M3-R24, REQ-M3-R26, REQ-M3-R27, REQ-M4-CH1, REQ-M4-DL1, REQ-M4-DL2, REQ-M4-DL3, REQ-M4-E1, REQ-M4-E2, REQ-M4-E4, REQ-M4-O1, REQ-M4-O3, REQ-M4-O4, REQ-X-R6

Overview:
This subsystem is the request-time enforcement path. It verifies tokens at the moment of use and denies access unless the caller identity, token authenticity, token claims, and current enforcement context all line up.

Trust/Responsibility:
Its responsibility is to make capability use a real authorization check rather than a token-presence check. It enforces authenticity, expiry, subject binding, audience, action, resource, and the current M4 chain and depth rules. For M4 canonical-resource enforcement, request-time checks are expected to evaluate against the same canonical `tool-b:/...` resource form used at mint-time.

Interactions:
It connects the Envoy boundary for verified caller identity, the tool implementation that performs request-time checks, and the shared state consulted during M4 governance enforcement.

## ARCH-006 Shared Governance State and Discovery Registry

Type: Logical
Satisfies: REQ-G-R2, REQ-G-R3, REQ-M4-B1, REQ-M4-B2, REQ-M4-B3, REQ-M4-B4, REQ-M4-B5, REQ-M4-B6, REQ-M4-B7, REQ-M4-P1, REQ-M4-P2, REQ-M4-P3, REQ-M4-P4, REQ-M4-P5, REQ-M4-E1, REQ-M4-E3, REQ-M4-O1, REQ-M4-O3, REQ-M4-O4

Overview:
This subsystem provides the trusted shared state used by the current M4 implementation. It holds the budget and rate state keyed by `root_token_id`, the mint-rate state used to bound new-resource mint fan-out, and the discovery registry used to gate minting of new resource-scoped capabilities.

Trust/Responsibility:
Its responsibility is to keep governance truth out of untrusted agents and inside trusted services plus shared state. It is central to fail-closed request spending, discovery-time expansion, and later audit or drift analysis.

Interactions:
It is used by capability issuance for root-budget initialization, mint-rate consumption, and registry membership checks, and by tool-b for per-request spend/rate consumption and discovery writes.

Authoritative State:
The current M4 slice depends on four Redis-backed authoritative state families. `m4:registry:<root_token_id>` is written by tool-b during discovery and read by capability-issuer to decide whether a new resource-scoped mint is allowed; capability-issuer no longer seeds this set during root mint. `m4:budget:<root_token_id>` and the related request-rate keys are initialized or consumed by trusted services and are used only for request-time governance enforcement. `m4:mint_rate:<root_token_id>` is written and consumed by capability-issuer to enforce the formula-based new-resource mint allowance per root-token context. `m4:capiss_minted:<token_id>` is written by capability-issuer when it mints a delegated or resource-scoped token and is later read by capability-issuer and tool-b as issuer-provenance state for the current resource-transition delegation rule.

## ARCH-007 Evidence and Security Verification Harness

Type: Logical
Satisfies: REQ-G-R4, REQ-G-R5, REQ-M1-R15, REQ-X-R3, REQ-X-R4, REQ-X-R5, REQ-T-R1, REQ-T-R2, REQ-T-R3, REQ-T-R4, REQ-T-R5, REQ-T-R6, REQ-T-R7, REQ-T-R8

Overview:
This subsystem defines how the project proves security behavior. It is responsible for collecting authoritative evidence, distinguishing control failures from harness failures, and structuring tests around premise, exercise, and outcome.

Trust/Responsibility:
Its responsibility is not to enforce system security directly, but to ensure that security claims are backed by meaningful proof. It prevents false-green outcomes by requiring guard evidence and by preferring authoritative sources such as server state, logs, and direct enforcement results.

Interactions:
It connects the rogue test harness, evidence artifact capture, profiling output, and the generated test specifications that document what the harness actually executes.

## ARCH-008 SPIRE Server

Type: Component
Satisfies: REQ-M1-R1, REQ-M1-R2, REQ-M1-R3, REQ-M1-R4, REQ-M1-R5, REQ-M1-R6, REQ-M1-R7, REQ-M1-R8, REQ-M1-R9, REQ-M1-R14, REQ-M1-R16

Overview:
SPIRE server is the authoritative control-plane service for node and workload registration state. It is the system of record for node admission and the trust anchor used by the rest of the SPIFFE domain.

Trust/Responsibility:
It is the primary authority for attestation acceptance and server-side admission state. When a requirement depends on proving whether a node was admitted, this component is the authoritative evidence source.

Interactions:
It accepts node attestation from agents, stores registration state, and is queried by the harness during M1 verification.

## ARCH-009 SPIRE Token Init

Type: Component
Satisfies: REQ-M1-R6, REQ-M1-R13

Overview:
The token-init component prepares bootstrap material for the local lab topology. It is a bootstrap helper that makes admission material available to the intended node path.

Trust/Responsibility:
Its responsibility is limited to explicit bootstrap setup. It matters because new valid bootstrap paths must exist only through operator-controlled changes.

Interactions:
It writes join-token material into the shared bootstrap location consumed by the legitimate SPIRE agent flow.

## ARCH-010 SPIRE Agent

Type: Component
Satisfies: REQ-M1-R4, REQ-M2-R1, REQ-M2-R2, REQ-M2-R3, REQ-M2-R6

Overview:
SPIRE agent mediates workload attestation and exposes the Workload API used by workloads to fetch X.509 SVIDs. It is the local identity issuer surface seen by the workloads in this lab.

Trust/Responsibility:
It is responsible for enforcing the separation between socket presence and actual identity issuance. A mounted socket is not itself authorization to receive an SVID without matching workload registration.

Interactions:
It connects local workloads to the SPIRE server and provides the Workload API socket mounted into the appropriate containers.

## ARCH-011 capability-issuer-envoy

Type: Component
Satisfies: REQ-M2-R19, REQ-M2-R20, REQ-M2-R21, REQ-M25-R1, REQ-M25-R2, REQ-M25-R3, REQ-M25-R4, REQ-M25-R5, REQ-M3-R8, REQ-M3-R9

Overview:
This Envoy instance is the trusted ingress boundary for the capability issuer. It terminates mTLS, derives verified caller identity, and forwards requests inward on the isolated app network.

Trust/Responsibility:
Its responsibility is to ensure that issuer identity input is boundary-derived rather than caller-supplied. That makes the issuer’s policy decisions dependent on authenticated identity instead of spoofable request metadata.

Interactions:
It accepts external mint requests, forwards them to the capability issuer service, and carries the verified identity model into the issuer path.

## ARCH-012 capability-issuer

Type: Component
Satisfies: REQ-M3-R3, REQ-M3-R4, REQ-M3-R5, REQ-M3-R6, REQ-M3-R7, REQ-M3-R10, REQ-M3-R11, REQ-M3-R12, REQ-M3-R13, REQ-M3-R14, REQ-M3-R15, REQ-M3-R25, REQ-M4-D1, REQ-M4-D2, REQ-M4-D3, REQ-M4-D4, REQ-M4-B7, REQ-M4-P1, REQ-M4-E3, REQ-M4-O2

Overview:
The capability issuer is the central authority that mints root and resource-scoped capability tokens. It translates allowed policy outcomes into explicit signed authority artifacts and enforces the current M4 new-resource mint-rate rule.

Trust/Responsibility:
It owns mint-time validation, required token fields, delegated token metadata, current M4 registry-gated resource minting, and current M4 new-resource mint-rate enforcement. It is also the current source for mint-decision logging and must emit one final mint-decision event for every mint exit path. In the canonical-resource cleanup slice it is responsible for rejecting non-canonical mint requests instead of silently preserving compatibility aliases.

Interactions:
It receives verified identity from Envoy, queries OPA for mint policy, reads and writes shared state where needed, enforces the new-resource mint-rate against Redis-backed state, emits structured JSON mint-decision events to stdout for container-log capture, and returns signed tokens to callers.

## ARCH-013 OPA

Type: Component
Satisfies: REQ-M3-R3, REQ-M3-R4, REQ-M3-R5, REQ-M3-R6, REQ-M3-R7

Overview:
OPA provides the current policy decision point for capability minting. It turns requested authority plus verified caller identity into an explicit allow or deny result.

Trust/Responsibility:
Its responsibility is to provide policy-gated decisions and to fail closed when policy is unavailable or invalid. It prevents minting from degrading into a local allow shortcut. For M4 canonical-resource enforcement, policy inputs are expected to use canonical `tool-b:/...` resource strings only.

Interactions:
It is called by the capability issuer over the internal app network and is deliberately isolated from edge callers.

## ARCH-014 tool-b-envoy

Type: Component
Satisfies: REQ-M2-R7, REQ-M2-R8, REQ-M2-R9, REQ-M2-R12, REQ-M2-R19, REQ-M2-R20, REQ-M2-R21, REQ-M25-R1, REQ-M25-R2, REQ-M25-R3, REQ-M25-R4, REQ-M25-R5, REQ-M4-E4, REQ-M4-E5

Overview:
This Envoy instance is the trusted ingress boundary for tool-b. It terminates mTLS, forwards verified caller identity inward, and keeps the application off the untrusted edge network.

Trust/Responsibility:
Its responsibility is to preserve the trusted-header model by ensuring headers are injected only by the isolated boundary. It also enforces the boundary pattern that protects tool-b from direct edge access.

Interactions:
It accepts edge requests from clients, forwards them to tool-b on the internal app network, and participates in the request-time identity contract enforced by tool-b.

## ARCH-015 tool-b

Type: Component
Satisfies: REQ-M2-R12, REQ-M2-R14, REQ-M2-R15, REQ-M2-R16, REQ-M2-R17, REQ-M2-R18, REQ-M3-R1, REQ-M3-R2, REQ-M3-R16, REQ-M3-R17, REQ-M3-R18, REQ-M3-R19, REQ-M3-R20, REQ-M3-R21, REQ-M3-R22, REQ-M3-R23, REQ-M3-R24, REQ-M3-R26, REQ-M3-R27, REQ-M4-CH1, REQ-M4-DL1, REQ-M4-DL2, REQ-M4-B2, REQ-M4-B3, REQ-M4-B4, REQ-M4-B5, REQ-M4-P2, REQ-M4-P3, REQ-M4-P4, REQ-M4-E1, REQ-M4-E3, REQ-M4-E4, REQ-M4-O1, REQ-M4-O3, REQ-M4-O4

Overview:
tool-b is the current protected resource server and the main request-time enforcement point. It applies endpoint authorization, verifies capability tokens, and performs the current M4 governance checks during protected requests.

Trust/Responsibility:
It is responsible for enforcing that identity alone is not enough, that tokens are valid for the caller and requested action, and that the M4 chain, budget, and discovery behaviors are checked during actual use. In the canonical-resource cleanup slice it is responsible for mapping request paths to canonical `tool-b:/...` resource identifiers before authorization.

Interactions:
It receives verified caller identity from tool-b-envoy, consults Redis during M4 enforcement, and writes discovery records for the current registry-based flow.

## ARCH-016 Redis

Type: Component
Satisfies: REQ-M4-B2, REQ-M4-B3, REQ-M4-B4, REQ-M4-B5, REQ-M4-B6, REQ-M4-B7, REQ-M4-P2, REQ-M4-P3, REQ-M4-P4, REQ-M4-O3, REQ-M4-O4

Overview:
Redis is the trusted shared state used by the current M4 slice. It stores request budget and rate information, the new-resource mint-rate state used by capability-issuer, and the discovery registry that binds new resources to a root token context.

Trust/Responsibility:
Its responsibility is to provide shared authoritative state for governance checks that cannot be delegated to agents. It is also the failure point that drives fail-closed behavior when trusted state becomes unavailable.

Interactions:
It is accessed by capability-issuer and tool-b over the internal networks for budget initialization, mint-rate consumption, request consumption, and registry lookups or writes.

Authoritative State:
This component currently stores:
- `m4:registry:<root_token_id>`:
  - writer: tool-b
  - readers: capability-issuer
  - purpose: discovery-backed proof that a newly requested resource was previously discovered under the same root token context
  - note: root mint no longer seeds this set with the root token's starting resource
- `m4:budget:<root_token_id>` and associated request-rate keys:
  - writer/reader: tool-b, with root-budget initialization from capability-issuer
  - purpose: per-root-token governance truth for request spending and rate limiting
- `m4:mint_rate:<root_token_id>`:
  - writer/reader: capability-issuer
  - purpose: per-root-token consumed count for the new-resource mint-rate rule `max(1, floor(root_token_lifetime_seconds / 20))`
  - note: the key TTL is bounded to the remaining root-token lifetime
- `m4:capiss_minted:<token_id>`:
  - writer: capability-issuer
  - readers: capability-issuer, tool-b
  - purpose: issuer-provenance marker for delegated or resource-scoped child tokens in the current M4 implementation

## ARCH-020 Shared Enforcement Contract

Type: Component
Satisfies: REQ-M4-D1, REQ-M4-D3, REQ-M4-D4, REQ-M4-CH1, REQ-M4-DL1, REQ-M4-DL2, REQ-M4-E2

Overview:
This component is the in-process shared enforcement module imported by both capability-issuer and tool-b. It is not a network service. It centralizes the current M4 token-chain contract so both services evaluate the same chain structure, derived depth, and attenuation semantics.

Trust/Responsibility:
Its responsibility is to eliminate semantic drift between mint-time and request-time chain validation. It owns required chain metadata checks, parent-link continuity, derived depth calculation, and the shared non-amplification rules used by both services.

Interactions:
It is loaded directly into the capability-issuer and tool-b Python processes at startup. Service-local policy evaluation, Redis lookups, identity binding, signature verification, and HTTP response handling remain outside this component.

Authoritative State Boundary:
This component does not own shared mutable state itself. It consumes token-chain contents directly and accepts service-local callbacks when a chain decision depends on authoritative state outside the token. In the current M4 slice, the main external-state dependency is the Redis-backed `m4:capiss_minted:<token_id>` issuer-provenance marker used to allow the `/search` to `tool-b:/read-file:*` resource transition only when the child token was minted through the trusted capability-issuer path.

## ARCH-017 capability-issuer-no-opa-envoy

Type: Component
Satisfies: REQ-M3-R6, REQ-M3-R7

Overview:
This test-only Envoy path forwards to a capability issuer configured with an unavailable OPA endpoint. It exists solely to prove that minting fails closed when policy evaluation cannot complete.

Trust/Responsibility:
Its responsibility is evidentiary rather than production-serving. It provides a deterministic boundary path for proving fail-closed mint behavior.

Interactions:
It is used only by the rogue test harness during fail-closed capability issuance scenarios.

## ARCH-018 agent-a

Type: Component
Satisfies: REQ-M2-R10, REQ-M2-R11

Overview:
agent-a is the current intended client workload used to exercise legitimate calls through both the capability issuer and tool-b. It represents the expected in-domain caller for positive-path flows.

Trust/Responsibility:
Its responsibility in the architecture is to act as a real client that verifies server identity through the configured trust bundle and expected target identity rather than bypassing transport verification.

Interactions:
It connects to capability-issuer-envoy and tool-b-envoy over mTLS using workload identity fetched from SPIRE agent.

## ARCH-019 rogue-tests Harness

Type: Component
Satisfies: REQ-G-R4, REQ-G-R5, REQ-M1-R15, REQ-X-R3, REQ-X-R4, REQ-X-R5, REQ-T-R1, REQ-T-R2, REQ-T-R3, REQ-T-R4, REQ-T-R5, REQ-T-R6, REQ-T-R7, REQ-T-R8

Overview:
The rogue-tests harness is the executable security verification layer for the integration and end-to-end suite. It drives adversarial scenarios, captures guard evidence, and writes the report and artifact set used for false-green analysis.

Trust/Responsibility:
It is responsible for proving that the intended negative or positive path was actually exercised and for preserving the evidence needed to distinguish real enforcement outcomes from harness errors.

Interactions:
It orchestrates Docker-based scenarios, records evidence under `artifacts/rogue-tests`, and writes the summarized run output into `test_report.log`.
