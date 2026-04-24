# Agentic IAM with SPIFFE — Normative requirements

This document defines the authoritative requirements for:

- Milestone 1 - Trust domain and node identity
- Milestone 2 - Workload identity and mTLS authorization
- Milestone 3 - Capability issuance and enforcement
- Milestone 4 - Delegation of capability tokens 

These requirements are written as normative statements.  
They define what the system shall enforce, independent of specific implementation details.

---

# 1. Global requirements

## REQ-G-R1 — Identity and authority separation
The system shall treat workload identity and authority as separate concerns.  
A valid workload identity shall not, by itself, grant authority to perform protected actions unless explicitly allowed by milestone-specific policy.

## REQ-G-R2 — Default deny
The system shall deny any connection, request, minting attempt, or resource access unless the required checks complete successfully.

## REQ-G-R3 — Fail closed
The system shall deny access or minting when a required dependency, policy decision, trust input, validation input, or enforcement check is unavailable, invalid, or incomplete.

## REQ-G-R4 — Evidence-based verification
The project shall treat security properties as satisfied only when supported by direct evidence from the authoritative component or enforcement point.

## REQ-G-R5 — Invariant preservation across refactoring
The system may change implementation, topology, or component choices, but it shall continue to satisfy the requirements in this document.

---

# 2. Milestone 1 — Trust domain and node identity

## Goal
Establish a functioning SPIFFE/SPIRE trust domain in which only explicitly authorized nodes can join and obtain node identity.

## REQ-M1-R1 — Trust domain integrity
The system shall issue identities only within the configured trust domain.

## REQ-M1-R2 — Trust root integrity
The system shall validate issued identities against the authoritative root of trust for the configured trust domain.

## REQ-M1-R3 — Rejection of foreign trust domains
The system shall not accept identities from outside the configured trust domain as equivalent to in-domain identities.

## REQ-M1-R4 — Node attestation enforcement
The system shall issue node identity only after successful completion of the configured node attestation flow.

## REQ-M1-R5 — No admission by mere reachability
The system shall not grant node identity merely because a node can start, connect, or reach SPIRE components.

## REQ-M1-R6 — Explicit bootstrap authorization
The system shall require valid bootstrap authorization before admitting a node when bootstrap material such as join tokens is used.

## REQ-M1-R7 — Forged bootstrap denial
The system shall deny node admission when presented bootstrap authorization is forged or otherwise invalid.

## REQ-M1-R8 — Replay resistance for bootstrap authorization
The system shall deny node admission when previously consumed bootstrap authorization is replayed.

## REQ-M1-R9 — No-bootstrap denial
The system shall deny node admission when required bootstrap authorization is absent.

## REQ-M1-R10 — Bootstrap secret isolation
The system shall ensure that bootstrap secrets are accessible only to explicitly authorized components.

## REQ-M1-R11 — Rogue isolation from bootstrap material
The system shall prevent rogue or unrelated workloads from reading bootstrap material unless access is explicitly granted.

## REQ-M1-R12 — Policy hygiene for node authorization
The system shall treat duplicate or stale authorization paths that mint the same node identity as policy drift requiring correction.

## REQ-M1-R13 — Explicit authorization changes only
The system shall permit creation of new valid node admission paths only through explicit operator action.

## REQ-M1-R14 — Server-side state as source of truth
The project shall use SPIRE server state as the authoritative source of truth for node admission and authorization drift.

## REQ-M1-R15 — No trust in client-side pass alone
The project shall not treat client-side logs or test harness PASS results as sufficient proof of correct node admission behavior without authoritative corroboration.

## REQ-M1-R16 — Rogue node denial
The system shall prevent rogue nodes from joining the trust domain using invalid, absent, replayed, or unauthorized admission material.

---

# 3. Milestone 2 — Workload identity and mTLS authorization

## Goal
Establish workload identity, authenticated transport, and identity-based authorization between workloads such as agent-a and tool-b.

## REQ-M2-R1 — Explicit workload authorization for identity issuance
The system shall issue a workload SVID only when an explicit workload authorization rule exists for that workload.

## REQ-M2-R2 — No identity from socket access alone
The system shall not treat access to the Workload API socket as sufficient to obtain workload identity.

## REQ-M2-R3 — No SVID without matching entry
The system shall deny SVID issuance to workloads that do not match an authorized registration entry.

## REQ-M2-R4 — Identity isolation between workloads
The system shall prevent a workload from obtaining another workload’s identity artifacts.

## REQ-M2-R5 — Workload private key isolation
The system shall prevent unauthorized workloads from reading another workload’s private key material or equivalent identity secrets.

## REQ-M2-R6 — Distinct control surfaces
The system shall treat file-system access, socket access, and identity issuance as distinct controls and shall not allow one to implicitly grant the others.

## REQ-M2-R7 — Mandatory mTLS on protected paths
The system shall require mutual TLS for protected service communication paths.

## REQ-M2-R8 — Client certificate requirement
The system shall deny protected access when the client does not present a valid client certificate where mTLS is required.

## REQ-M2-R9 — Cryptographic transport identity
The system shall derive caller identity for protected access from authenticated transport rather than unauthenticated request metadata.

## REQ-M2-R10 — Server identity verification
The client side shall verify that the presented server identity chains to the expected trust bundle.

## REQ-M2-R11 — Expected service identity verification
The client side shall verify that the presented server identity matches the expected service identity.

## REQ-M2-R12 — Caller identity verification at enforcement
The protected service boundary shall verify the caller’s workload identity before authorizing protected actions.

## REQ-M2-R13 — Authorization not based on reachability
The system shall not grant protected access solely because a caller can reach the network listener or boundary.

## REQ-M2-R14 — Explicit allow list for protected actions
The protected service boundary shall allow protected actions only for explicitly authorized workload identities.

## REQ-M2-R15 — Valid identity is necessary but not universally sufficient
The system shall treat possession of a valid workload identity as necessary for protected access, but not sufficient unless policy explicitly allows that identity for the requested action.

## REQ-M2-R16 — Different identities, different outcomes
The system shall allow intended workload identities and deny non-authorized workload identities according to explicit policy.

## REQ-M2-R17 — Separate authorization classes for endpoints
The system shall allow non-sensitive and sensitive endpoints to have different authorization policies.

## REQ-M2-R18 — No escalation from health to secret
The system shall not allow access to a broader diagnostic endpoint, such as `/health`, to imply access to a protected endpoint, such as `/secret`.

## REQ-M2-R19 — Trusted boundary requirement for app isolation
When the architecture relies on a proxy or boundary component to verify identity and forward requests, the protected application shall not be directly reachable from untrusted client networks.

## REQ-M2-R20 — Trusted-header constraint
The application shall trust identity headers only when those headers are injected by a trusted and isolated boundary component.

## REQ-M2-R21 — Header spoofing resistance
The system shall prevent external callers from gaining privileges by manually supplying internal identity headers.

---

# 4. Milestone 2.5 — Boundary pattern requirements carried into Milestone 3

## REQ-M25-R1 — Edge and app trust-surface separation
The system shall separate edge-facing components from app-facing components when header-based identity propagation is used.

## REQ-M25-R2 — Edge clients limited to ingress boundary
The system shall ensure that edge clients can reach only the ingress boundary and not the protected application directly.

## REQ-M25-R3 — Boundary-enforced mTLS
The ingress boundary shall enforce mutual TLS before forwarding protected requests inward.

## REQ-M25-R4 — Connection-bound verified identity propagation
The ingress boundary shall inject verified caller identity only after successful transport authentication and shall bind that identity to the authenticated connection.

## REQ-M25-R5 — No privilege gain via spoofed internal headers
The system shall ensure that direct spoofing of trusted internal headers from edge clients is ineffective.

---

# 5. Milestone 3 — Capability issuance and enforcement

## Goal
Establish that identity alone is not authority, that authority is explicitly minted under policy as a capability artifact, and that tool-b enforces both identity and capability.

## REQ-M3-R1 — Identity-only access denial
The system shall deny protected authority-bearing operations when the caller has valid workload identity but no valid capability token.

## REQ-M3-R2 — Identity remains necessary
The system shall require valid caller identity for protected access even when a capability token is presented.

## REQ-M3-R3 — Policy-gated capability minting
The capability issuer shall mint capability tokens only when policy explicitly allows the requested authority.

## REQ-M3-R4 — No minting from caller-supplied intent alone
The capability issuer shall treat requested authority parameters as inputs to policy evaluation and not as automatically granted authority.

## REQ-M3-R5 — Denial of unauthorized authority requests
The capability issuer shall deny minting requests for authority outside the policy-defined allowed scope.

## REQ-M3-R6 — Fail-closed minting on policy failure
The capability issuer shall deny minting when the policy decision point is unavailable, unreachable, errors, or returns no valid decision.

## REQ-M3-R7 — No allow fallback
The capability issuer shall not fall back to allow behavior when policy evaluation fails.

## REQ-M3-R8 — Trusted identity propagation into issuer
When the capability issuer relies on a trusted boundary component to supply caller identity, it shall trust that identity only within the isolated trusted-boundary model.

## REQ-M3-R9 — No external spoofing of issuer identity input
The system shall prevent external callers from spoofing the verified identity input used by the capability issuer for minting decisions.

## REQ-M3-R10 — Capability as explicit authority artifact
The capability token shall encode explicit authority rather than only caller identity.

## REQ-M3-R11 — Required capability subject field
The capability token shall carry an enforceable subject field identifying the workload for which the token was minted.

## REQ-M3-R12 — Required capability audience field
The capability token shall carry an enforceable audience field identifying the intended target service or audience.

## REQ-M3-R13 — Required capability action field
The capability token shall carry an enforceable action field identifying the authorized action.

## REQ-M3-R14 — Required capability resource field
The capability token shall carry an enforceable resource field identifying the authorized resource.

## REQ-M3-R15 — Required capability expiry field
The capability token shall carry an enforceable expiry field limiting the token’s validity window.

## REQ-M3-R16 — Capability TTL enforcement
The resource server or effective enforcement point shall deny expired capability tokens.

## REQ-M3-R17 — Subject binding enforcement
The resource server shall deny use of a capability token when the authenticated caller identity does not match the token subject.

## REQ-M3-R18 — Replay resistance across identities
The system shall deny successful use of a stolen capability token by a different workload identity.

## REQ-M3-R19 — Audience enforcement
The resource server shall deny capability use when the token audience does not match the intended target service or audience.

## REQ-M3-R20 — Action enforcement
The resource server shall deny capability use when the token action does not match the requested action.

## REQ-M3-R21 — Resource enforcement
The resource server shall deny capability use when the token resource does not match the requested resource.

## REQ-M3-R22 — Capability authenticity verification
The resource server shall verify the authenticity and integrity of the capability token before using it for authorization.

## REQ-M3-R23 — Denial of tampered or invalid tokens
The resource server shall deny tokens that are malformed, tampered, unverifiable, or otherwise invalid.

## REQ-M3-R24 — Full enforcement at point of use
The resource server shall enforce capability validity at request time, including at minimum authenticity, expiry, subject, audience, action, and resource.

## REQ-M3-R25 — Parameter completeness checks
The capability issuer shall reject minting requests that omit required authority parameters when those parameters are mandatory for evaluation and issuance.

## REQ-M3-R26 — No trust in token presence alone
The system shall not treat the mere presence of a returned token string as proof of correct capability issuance or authorization.

## REQ-M3-R27 — Independent verification at resource server
The resource server shall independently verify the capability token at use time and shall not blindly trust that successful issuance implies successful authorization.

---

# 6. Cross-cutting security requirements

## REQ-X-R1 — Explicit security controls only
The project shall treat a security control as present only when it is explicitly implemented and verifiably enforced.

## REQ-X-R2 — No reliance on implicit platform handling
The project shall not assume that a framework, proxy, library, or component enforces a security check unless that enforcement is explicitly verified.

## REQ-X-R3 — Authoritative evidence preference
The project shall prefer evidence from the authoritative control plane, enforcement point, or server-side state over optimistic harness output when determining whether a requirement is satisfied.

## REQ-X-R4 — Correct failure classification
The project shall distinguish infrastructure or harness failures from genuine security denials.

## REQ-X-R5 — No false proof from harness errors
The project shall not treat DNS failures, file errors, network failures, mount issues, or readiness problems as proof that a security control worked.

## REQ-X-R6 — Separation of security concerns
The project shall preserve the distinction between identity issuance, policy decision, capability issuance, and resource enforcement in both design and evaluation.

## REQ-X-R7 — Operator-defined hygiene as security input
The project shall treat topology shortcuts, duplicate authorization paths, permissive defaults, and policy drift as security-relevant conditions requiring explicit evaluation.

---
# 7. Milestone 4 Invariants — Checkpointed delegation with governance truth

TTL is acceptable in this milestone; explicit revocation is not required.

**Core decisions baked into M4 (reduced scope):**
- **Checkpointed delegation in reduced scope:** request-time token-chain verification is enforced at PEP/tool, but resource-changing delegation is not pure offline delegation. New resource-scoped child tokens MUST be minted by `capiss` after policy, registry, and governance checks.
- **No wildcard resources** in delegated permissions: always scoped to **canonical resources**.
- **Depth limit:** token chains may delegate up to **N = 3** hops; **no extensions/renewals** in M4 reduced scope.
- **Budget + request rate:** enforced **per request** and consumed **per `root_token_id`** (global across tools), using a trusted store (e.g., Redis). Agents never decrement.
- **New resource mint rate:** enforced at `capiss` for new-resource mints, at **1 mint per 20 seconds of root-token lifetime** with a minimum allowance of **1**.
- **Discovery-time expansion:** Option A registry now; later evolve to signed receipts while keeping `capiss` central.
- **Fail closed** on any enforcement/store error.
- **Full logging** from trusted components for every relevant step.

---

## Definitions

- **PEP**: Policy Enforcement Point (Envoy/tool gateway or equivalent).
- **capiss**: Capability Issuer; the **central authority** that mints root tokens and resource-scoped tokens.
- **Spend/rate store**: Trusted shared state used by PEPs/tools to enforce spend budgets and request rate (e.g., Redis).
- **Discovery Registry**: Trusted registry keyed by `root_token_id` recording discovered canonical resources (Option A).
- **Token chain**: Lineage of tokens linked by `parent_token_id` back to a `root_token_id`.
- **Checkpointed delegation**: In the current M4 reduced scope, resource-changing child tokens are minted by `capiss` under policy and discovery-governed checks. The resulting token chain is then verified locally by PEP/tool at request time.
- **Hop / depth**: One delegation edge increments `delegation_depth` by 1. Depth is a property of a *token chain*, not an agent.
- **Root token**: The chain anchor minted by `capiss`, **one per request** (M4 default), with **TTL = 60 seconds**.
- **Canonical resource**: A deterministic, non-ambiguous identifier for the protected object/endpoint within a tool/service.

---

## A. Delegation mechanics and chain correctness

### REQ-M4-D1 — Delegation must not increase authority (reduced scope: same-subject only)
A delegated token MUST NOT increase authority relative to its parent.

Current reduced-scope M4 behavior:
- `subject_spiffe_id` MUST remain equal to the parent token subject.
- `subject_spiffe_id` MUST remain equal to the authenticated mint caller at `capiss`.
- `delegation_depth` MUST increment by 1.

Authority constraints:
- `aud` may only narrow (remove audiences) or remain equal.
- `act` may only narrow (remove actions) or remain equal.
- `res` may only narrow (remove resources) or remain equal.
- `exp` MUST NOT exceed parent expiry (may shorten or remain equal).

In short: **same-subject attenuation is allowed; privilege amplification is not.**

Deferred broader scope:
- Cross-subject delegation (`subject_spiffe_id` changing from parent to child) is NOT part of the current reduced-scope M4 implementation.
- Broader subject-transfer delegation is deferred for future design and implementation and MUST NOT be claimed by the current system behavior.

### REQ-M4-D2 — Canonical resources only (no wildcards)
Delegation MUST reference **canonical resources** only.
- Wildcards, prefixes, regex, “all”, “*”, path globs, and equivalent pattern semantics are **rejected**.
- Canonicalization MUST be deterministic and identical at mint-time and enforce-time.

### REQ-M4-D3 — Chain metadata is mandatory
Every token used for enforcement MUST carry:
- `root_token_id`
- `token_id`
- `parent_token_id` (absent or null only for the root)
- `delegator_spiffe_id` (absent only for the root)
- `subject_spiffe_id`
- `delegation_depth` (root depth = 0)

### REQ-M4-D4 — Depth is per chain, not per agent
Depth enforcement applies to **token lineage**. An agent may hold multiple tokens of different depths; enforcement uses the depth of the token presented.

---

## B. Token chain integrity and depth (no extensions in reduced scope)

### REQ-M4-CH1 — Chain integrity must be verified at PEP/tool
The enforcement layer MUST verify the token’s full append-only chain integrity (e.g., Biscuit blocks):
- Root issuance authenticity (issued by `capiss`), and
- Tamper-evidence of appended blocks (no modification/insertion/deletion/reordering).

Any chain verification failure MUST result in denial.

## B. Depth limit (no extensions in reduced scope)

### REQ-M4-DL1 — Depth is derived from the token chain (do not trust agent-written depth)
Depth MUST be derived by the verifier from the token’s append-only chain structure (e.g., Biscuit blocks). Agents MUST NOT be trusted to set `delegation_depth` correctly.
- Define `effective_depth = chain_length - 1` (root-only token has depth 0).

### REQ-M4-DL2 — Depth limit enforced at PEP/tool
A request MUST be denied if `effective_depth > N` (N = 3).

### REQ-M4-DL3 — No depth renewal in M4 reduced scope
There is **no** mechanism to extend/renew depth beyond N in this milestone. A new root token/request context is required.

---

## C. Spend budget and rate control (per root token)

### REQ-M4-B1 — Agents never decrement budgets
Budgets MUST NOT rely on agents decrementing counters or “updating remaining budget” inside tokens.

### REQ-M4-B2 — Spend is enforced per request by a trusted service
Each protected request MUST consume spend budget.
- Budget enforcement MUST be performed by a trusted spend service (or an equivalent trusted enforcement component) that PEPs/tools consult.

### REQ-M4-B3 — Spend is keyed by `root_token_id`
Spend budget MUST be tracked and enforced by **`root_token_id`** (global across tools/audiences by default).

### REQ-M4-B4 — Atomic decrement and deterministic deny
Spend consumption MUST be atomic.
- If budget would go below zero, enforcement MUST deny.
- Deny behavior MUST be deterministic and logged.

### REQ-M4-B5 — Budget lifetime is bounded by TTL
Spend budget MUST expire no later than the root token expiry.
- If the root token expires, the associated spend budget MUST be invalid/irrelevant.

### REQ-M4-B6 — No budget renewal in M4 reduced scope
There is **no** mechanism to replenish/increase spend budget within the same `root_token_id` in this milestone. A new root token/request context is required.

### REQ-M4-B7 — New-resource mint rate is enforced at `capiss`
`capiss` MUST enforce a mint-rate allowance for delegated mints that request a canonical `res` different from the parent token resource.
- The allowance MUST be keyed by `root_token_id`.
- The allowance MUST be `max(1, floor(root_token_lifetime_seconds / 20))`.
- Same-resource child remints MUST NOT consume this allowance.
- If the allowance is exhausted, minting MUST deterministically deny with a machine-readable reason.
- If the trusted store for this decision is unavailable or malformed, minting MUST fail closed.

---

## D. Proof-of-derivation for discovery-time expansion (Option A: registry)

### REQ-M4-P1 — New resources require registry proof
`capiss` MUST NOT mint a capability for a *new* canonical `res` unless the mint request includes verifiable proof that `res` is associated with the same `root_token_id` via the **Discovery Registry**.

### REQ-M4-P2 — Discovery Registry is authoritative for “discovered under this root”
The Discovery Registry MUST record discovered canonical resources keyed by `root_token_id` (and MAY include `subject_spiffe_id`, discovery endpoint, timestamp, and expiry).

### REQ-M4-P3 — Only trusted producers may write the registry
Only trusted components (PEP/tool boundary or discovery-enabled tools) may write discovery records. Agents MUST NOT be treated as authoritative producers.

### REQ-M4-P4 — Registry entries are TTL-bounded
Registry entries MUST expire no later than the root token expiry (or earlier).

### REQ-M4-P5 — Registry-based gating is a stepping stone to signed receipts
This registry model is the **Option A** implementation. A future evolution may replace/augment registry proof with **signed discovery receipts**, while keeping `capiss` as the central authority.

---

## D. Enforcement placement and trust boundaries

### REQ-M4-E1 — Enforcement does not depend on agent honesty
All security-relevant checks (attenuation rules, identity binding, depth window, extension validation, spend budget) MUST be enforced by trusted components (PEP/tool + shared enforcement path), not by agents.

### REQ-M4-E2 — PEPs share a single enforcement contract
All PEPs/tools MUST use the same enforcement contract (shared library/service) for:
- token validation + claims extraction
- identity binding check
- depth + extension check
- spend budget check

In the current reduced-scope implementation, this shared enforcement contract MUST be a single authoritative implementation of chain validation, effective-depth derivation, and attenuation checks reused by both mint-time and request-time validation paths. Service-local policy calls, store lookups, and HTTP response shaping MAY remain outside that shared contract.

### REQ-M4-E3 — capiss is not in the hot path for every protected request
`capiss` MUST NOT be required for every protected request.
- `capiss` is used to mint root tokens and resource-scoped tokens (on-demand path), and to log those mint decisions.
- Per-request enforcement (depth limit, spend budget, request-rate checks, identity binding) is performed at PEP/tool using the shared enforcement contract and the spend/rate store.
- The current reduced-scope implementation therefore supports offline verification at use time, but not pure offline creation of new resource-scoped delegated tokens.

### REQ-M4-E4 — Identity binding is mandatory
A request MUST be denied unless the presented token’s `subject_spiffe_id` matches the authenticated caller identity asserted by the PEP (e.g., via SPIFFE mTLS and a trusted identity header).

### REQ-M4-E5 — Header trust requires network boundary
If identity is delivered via header (e.g., `x-spiffe-id`), that header MUST be trusted only across an enforced network boundary such that clients cannot spoof it (edge/app net isolation).

---

## E. Observability, auditability, and “why allowed?”

### REQ-M4-O1 — Every enforcement decision emits an audit event
For every protected request, the enforcement layer MUST emit an audit event containing at least:
- timestamp
- caller `subject_spiffe_id`
- `root_token_id`, `token_id`, `parent_token_id`
- `delegation_depth`
- evaluated `aud`, `act`, `res`
- spend budget result (before/after or remaining)
- allow/deny
- structured reason code

### REQ-M4-O2 — capiss logs every mint decision with provenance
For every mint request (root token mint or resource token mint), `capiss` MUST emit exactly one final mint-decision audit event containing:
- allow/deny
- `policy_id` and `policy_hash`
- structured `reason_code`
- `subject_spiffe_id` when known from the request
- requested `aud`, `act`, `res` when truthfully known from the request
- `root_token_id` when a root token context exists for that decision
- `token_id` when a token was successfully created before a later fail-closed step
- `parent_token_id` and `delegation_depth` for delegated/resource mint decisions when those values are available
- `registry_hit` yes/no for resource mint decisions governed by the Discovery Registry
- `error` for fail-closed/store-transport cases when implementation detail is available

### REQ-M4-O3 — Chain reconstruction is always possible
From audit events + DA logs, it MUST be possible to reconstruct:
- who delegated to whom (delegator → subject)
- what authority was held at each hop (aud/act/res)
- where checkpoints occurred (extensions)
- why continuation was allowed (policy hash + reason code)

### REQ-M4-O4 — Drift visibility is mandatory
The system MUST provide enough data to detect boundary erosion patterns, including:
- number of distinct subjects under a `root_token_id`
- delegation depth distribution
- request volume under a `root_token_id`
- denied extension attempts and denial reasons

---

## F. Explicit non-goals (Milestone 4 reduced scope)

- No explicit revocation beyond TTL.
- No proof-of-possession / cnf binding hardening.
- No semantics-to-mechanics enforcement (intent text is not authority).
- No wildcard resource delegation.
- **No depth extensions/renewals** beyond N.
- **No budget extensions/renewals** for a `root_token_id`.

---

## Appendix: Canonical `res` contract (M4 minimal v1)

**Goal:** Freeze a minimal, enforceable `res` scheme for M4 (no wildcards), without committing to the final, future resource model.

### M4 v1 rules
- `aud` identifies the tool/service (e.g., `tool-b`).
- `res` is a canonical string in one of these forms:
  - **Endpoint-level:** `tool-b:/<endpoint>`
  - **Endpoint + object-id:** `tool-b:/<endpoint>:<object_id>`
- `<object_id>` MUST be an exact identifier (no `*`, globs, prefixes, regex, or ranges).
- Canonicalization MUST be deterministic and identical at mint-time and enforce-time.

### Examples (M4)
- `aud=tool-b`, `res=tool-b:/read-file:fileA`
- `aud=tool-b`, `res=tool-b:/review-log:logY`
- `aud=tool-b`, `res=tool-b:/secret`

### Non-goals (for M4)
- No tag-based selection in `res`.
- No wildcard/pattern matching.
- No cross-tool composite resources.

---

# 8. Test contract requirements

These requirements are mandatory for negative security tests.

## REQ-T-R1 — Premise proof requirement
Each negative security test shall prove that the intended adversarial condition actually exists before drawing conclusions from the outcome.

## REQ-T-R2 — Exercise proof requirement
Each negative security test shall prove that the system under test was actually exercised through the intended path with the intended adversarial input.

## REQ-T-R3 — Outcome proof requirement
Each negative security test shall assert an outcome that specifically matches the intended security requirement being tested.

## REQ-T-R4 — No acceptance of “any failure”
Negative security tests shall not use “any failure” as a sufficient oracle for requirement satisfaction.

## REQ-T-R5 — Fail on unexpected success
Negative security tests shall fail when the protected action succeeds unexpectedly.

## REQ-T-R6 — Fail on harness error
Negative security tests shall fail when the test result is caused by harness, environment, or setup errors rather than by the intended control.

## REQ-T-R7 — Evidence capture requirement
Security-relevant tests shall preserve sufficient evidence to justify their conclusions.

## REQ-T-R8 — Accepted evidence forms
Evidence may include, as applicable, TLS transcripts, server-side entry snapshots, logs, token inspection results, denial markers, and before/after state diffs.

---

# 9. Milestone summaries

## Milestone 1 summary
The system shall allow only explicitly authorized nodes to join the trust domain and obtain node identity.  
Bootstrap authorization shall resist forgery, replay, and unintended exposure.  
SPIRE server state shall be the authoritative proof of node admission behavior.

## Milestone 2 summary
The system shall issue workload identity only to explicitly authorized workloads.  
Protected service communication shall require verified workload identity over mTLS.  
Authorization shall be based on authenticated identity and explicit policy, not on network reachability or caller-supplied headers.

## Milestone 3 summary
The system shall not treat identity as sufficient authority.  
Authority shall be explicitly minted under policy as a capability artifact.  
Protected access shall require both valid caller identity and a valid, enforced capability token.

---

# 10. Out of scope for these milestones

The following are intentionally out of scope for Milestones 1 through 3 and shall not be assumed to be provided by these milestones:

- Proof-of-possession or `cnf` hard binding as a formal milestone requirement
- Delegation
- Attenuation
- Governance, revocation strategy, and HITL constraints
- Intent-to-mechanics compilation

Future milestones may introduce additional requirements in these areas.

---

# 11. Completion rule

A milestone shall be considered complete only when its requirements are satisfied and supported by sufficient evidence.  
A working demo alone shall not be treated as proof of milestone completion.

## Appendix: Discovery Registry (Option A) — minimal v1 source of truth

**Purpose:** Bind discovery-time resource expansion to the original request context (`root_token_id`) while keeping `capiss` as the central authority.

### What counts as a discovery event (minimal v1)
Only *discovery endpoints* write to the registry. For M4 v1:
- `tool-b:/search` (or `tool-b:/list`) returns canonical resource IDs (references only, not contents).
- For every returned `res`, the trusted producer (tool-b or its PEP boundary) writes a registry entry under the caller’s `root_token_id`.

No other endpoints produce discovery records in M4 v1.

### Registry record schema (minimal v1)
One record per discovered canonical resource.

**Required fields:**
- `root_token_id` (string)
- `res` (canonical string, e.g., `tool-b:/read-file:fileA`)
- `producer` (string; e.g., `tool-b` or `tool-b-envoy`)
- `exp` (timestamp; MUST be <= root token expiry)

**Optional fields (audit convenience):**
- `subject_spiffe_id`
- `discovery_endpoint` (e.g., `tool-b:/search`)
- `ts` (write timestamp)

### Minimal storage model (implementation-agnostic)
A minimal representation is:
- Keyed by `root_token_id`
- Value is a set of discovered `res` strings
- TTL on the set/key bounded by root token TTL

### Minting rule (capiss; minimal v1)
`capiss` MUST deny any mint request for a *new* `res` under `root_token_id=R` unless:
1) `res` is canonical and wildcard-free, and
2) `res` is present in the Discovery Registry for `R`.

### Minimal logging (source of truth)
**On registry write (tool-b or PEP boundary):** log `root_token_id`, `subject_spiffe_id` (if available), `discovery_endpoint`, and `res_count`.

**On capiss mint/deny:** log `root_token_id`, `subject_spiffe_id`, requested `res`, `registry_hit` yes/no, and allow/deny + reason code.
