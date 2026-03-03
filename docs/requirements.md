# Milestone 4 Invariants (M4)

**Milestone theme:** *Checkpointed delegation with governance truth* (TTL is acceptable; no explicit revocation required).

**Core decisions baked into M4 (reduced scope):**
- **Offline delegation** is allowed (attenuation-only) and enforced at PEP/tool.
- **No wildcard resources** in delegated permissions: always scoped to **canonical resources**.
- **Depth limit:** token chains may delegate up to **N = 3** hops; **no extensions/renewals** in M4 reduced scope.
- **Budget + request rate:** enforced **per request** and consumed **per `root_token_id`** (global across tools), using a trusted store (e.g., Redis). Agents never decrement.
- **New resource mint rate:** enforced at `capiss` when minting new resource-scoped tokens.
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
- **Hop / depth**: One delegation edge increments `delegation_depth` by 1. Depth is a property of a *token chain*, not an agent.
- **Root token**: The chain anchor minted by `capiss`, **one per request** (M4 default), with **TTL = 60 seconds**.
- **Canonical resource**: A deterministic, non-ambiguous identifier for the protected object/endpoint within a tool/service.

---

## A. Delegation mechanics and chain correctness

### M4-D1 — Delegation must not increase authority (permissive: subject change allowed)
A delegated token MUST NOT increase authority relative to its parent.

Allowed changes:
- `subject_spiffe_id` may change (delegating to a different identity). **This is permitted even if** `aud/act/res/exp` remain unchanged.
- `delegation_depth` MUST increment by 1.

Authority constraints:
- `aud` may only narrow (remove audiences) or remain equal.
- `act` may only narrow (remove actions) or remain equal.
- `res` may only narrow (remove resources) or remain equal.
- `exp` MUST NOT exceed parent expiry (may shorten or remain equal).

In short: **subject transfer is allowed; privilege amplification is not.**

### M4-D2 — Canonical resources only (no wildcards)
Delegation MUST reference **canonical resources** only.
- Wildcards, prefixes, regex, “all”, “*”, path globs, and equivalent pattern semantics are **rejected**.
- Canonicalization MUST be deterministic and identical at mint-time and enforce-time.

### M4-D3 — Chain metadata is mandatory
Every token used for enforcement MUST carry:
- `root_token_id`
- `token_id`
- `parent_token_id` (absent or null only for the root)
- `delegator_spiffe_id` (absent only for the root)
- `subject_spiffe_id`
- `delegation_depth` (root depth = 0)

### M4-D4 — Depth is per chain, not per agent
Depth enforcement applies to **token lineage**. An agent may hold multiple tokens of different depths; enforcement uses the depth of the token presented.

---

## B. Token chain integrity and depth (no extensions in reduced scope)

### M4-CH1 — Chain integrity must be verified at PEP/tool
The enforcement layer MUST verify the token’s full append-only chain integrity (e.g., Biscuit blocks):
- Root issuance authenticity (issued by `capiss`), and
- Tamper-evidence of appended blocks (no modification/insertion/deletion/reordering).

Any chain verification failure MUST result in denial.

## B. Depth limit (no extensions in reduced scope)

### M4-DL1 — Depth is derived from the token chain (do not trust agent-written depth)
Depth MUST be derived by the verifier from the token’s append-only chain structure (e.g., Biscuit blocks). Agents MUST NOT be trusted to set `delegation_depth` correctly.
- Define `effective_depth = chain_length - 1` (root-only token has depth 0).

### M4-DL2 — Depth limit enforced at PEP/tool
A request MUST be denied if `effective_depth > N` (N = 3).

### M4-DL3 — No depth renewal in M4 reduced scope
There is **no** mechanism to extend/renew depth beyond N in this milestone. A new root token/request context is required.

---

## C. Spend budget and rate control (per root token)

### M4-B1 — Agents never decrement budgets
Budgets MUST NOT rely on agents decrementing counters or “updating remaining budget” inside tokens.

### M4-B2 — Spend is enforced per request by a trusted service
Each protected request MUST consume spend budget.
- Budget enforcement MUST be performed by a trusted spend service (or an equivalent trusted enforcement component) that PEPs/tools consult.

### M4-B3 — Spend is keyed by `root_token_id`
Spend budget MUST be tracked and enforced by **`root_token_id`** (global across tools/audiences by default).

### M4-B4 — Atomic decrement and deterministic deny
Spend consumption MUST be atomic.
- If budget would go below zero, enforcement MUST deny.
- Deny behavior MUST be deterministic and logged.

### M4-B5 — Budget lifetime is bounded by TTL
Spend budget MUST expire no later than the root token expiry.
- If the root token expires, the associated spend budget MUST be invalid/irrelevant.

### M4-B6 — No budget renewal in M4 reduced scope
There is **no** mechanism to replenish/increase spend budget within the same `root_token_id` in this milestone. A new root token/request context is required.

---

## D. Proof-of-derivation for discovery-time expansion (Option A: registry)

### M4-P1 — New resources require registry proof
`capiss` MUST NOT mint a capability for a *new* canonical `res` unless the mint request includes verifiable proof that `res` is associated with the same `root_token_id` via the **Discovery Registry**.

### M4-P2 — Discovery Registry is authoritative for “discovered under this root”
The Discovery Registry MUST record discovered canonical resources keyed by `root_token_id` (and MAY include `subject_spiffe_id`, discovery endpoint, timestamp, and expiry).

### M4-P3 — Only trusted producers may write the registry
Only trusted components (PEP/tool boundary or discovery-enabled tools) may write discovery records. Agents MUST NOT be treated as authoritative producers.

### M4-P4 — Registry entries are TTL-bounded
Registry entries MUST expire no later than the root token expiry (or earlier).

### M4-P5 — Registry-based gating is a stepping stone to signed receipts
This registry model is the **Option A** implementation. A future evolution may replace/augment registry proof with **signed discovery receipts**, while keeping `capiss` as the central authority.

---

## D. Enforcement placement and trust boundaries

### M4-E1 — Enforcement does not depend on agent honesty
All security-relevant checks (attenuation rules, identity binding, depth window, extension validation, spend budget) MUST be enforced by trusted components (PEP/tool + shared enforcement path), not by agents.

### M4-E2 — PEPs share a single enforcement contract
All PEPs/tools MUST use the same enforcement contract (shared library/service) for:
- token validation + claims extraction
- identity binding check
- depth + extension check
- spend budget check

### M4-E3 — capiss is not in the hot path for every protected request
`capiss` MUST NOT be required for every protected request.
- `capiss` is used to mint root tokens and resource-scoped tokens (on-demand path), and to log those mint decisions.
- Per-request enforcement (depth limit, spend budget, request-rate checks, identity binding) is performed at PEP/tool using the shared enforcement contract and the spend/rate store.

### M4-E4 — Identity binding is mandatory
A request MUST be denied unless the presented token’s `subject_spiffe_id` matches the authenticated caller identity asserted by the PEP (e.g., via SPIFFE mTLS and a trusted identity header).

### M4-E5 — Header trust requires network boundary
If identity is delivered via header (e.g., `x-spiffe-id`), that header MUST be trusted only across an enforced network boundary such that clients cannot spoof it (edge/app net isolation).

---

## E. Observability, auditability, and “why allowed?”

### M4-O1 — Every enforcement decision emits an audit event
For every protected request, the enforcement layer MUST emit an audit event containing at least:
- timestamp
- caller `subject_spiffe_id`
- `root_token_id`, `token_id`, `parent_token_id`
- `delegation_depth`
- evaluated `aud`, `act`, `res`
- spend budget result (before/after or remaining)
- allow/deny
- structured reason code

### M4-O2 — capiss logs every mint decision with provenance
For every mint request (root token mint or resource token mint), `capiss` MUST log:
- allow/deny
- `policy_id` and/or `policy_hash`
- structured `reason_code`
- `root_token_id`
- `subject_spiffe_id`
- requested `aud`, `act`, `res`
- `registry_hit` yes/no (when minting a new resource scoped by the Discovery Registry)

### M4-O3 — Chain reconstruction is always possible
From audit events + DA logs, it MUST be possible to reconstruct:
- who delegated to whom (delegator → subject)
- what authority was held at each hop (aud/act/res)
- where checkpoints occurred (extensions)
- why continuation was allowed (policy hash + reason code)

### M4-O4 — Drift visibility is mandatory
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

