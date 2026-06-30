# Brainstorm — Generic Capability Verifier + Full-Chain Audit Architecture

> STATUS: **BRAINSTORM / NOT APPROVED.** Captured design exploration to revisit
> later. This is NOT a `plan.md` and has not been through grill-me review. Do not
> write tests or code from this document. When we resume, promote the agreed
> parts into `plan.md` + `test_plan.md` per the AGENTS.md slice workflow.
>
> Companion doc: `docs/slices/m5-full-chain-audit-trace/brainstorm.md`
> (the audit-trace thread that started this conversation). This document
> supersedes/extends it with the broader product architecture.
>
> Date captured: 2026-06-14. Verified against repo state on 2026-06-13/14.

---

## 0. How this conversation started, and where it arrived

It began as an **audit** request: today the Varambu audit shows only the capiss
mint decision; for complete auditability an auditor should follow one request
end to end — user intent → action → mint → gateway checks → upstream call →
upstream return.

Pulling that thread exposed a deeper architectural question: the current
`jira-mcp-gateway` is a **bespoke, per-SaaS PEP**. Writing one of those per SaaS
does not scale. That led to the real target architecture captured here:

- a **transparent adapter proxy** in front of the agent,
- a **generic, stateless, open-source capability verifier** (not a per-SaaS gateway),
- mounted **in front of OR plugged into** an off-the-shelf MCP gateway/server,
- with **capiss + OPA + Redis + audit as the proprietary product** (the authority
  + governance + evidence plane),
- bound together by a small number of **published contracts**.

Both threads converge: the verifier is one **event source** for the audit plane,
and the audit plane (product) is the **correlator** that reconstructs the chain.

---

## 1. Current state (verified)

### 1.1 Components in the M5 path
- **adapter** `services/codex-jira-mcp-adapter/server.py` — MCP (stdio) server
  facing Codex. Exposes exactly **two** tools (`read_project_summary`,
  `create_story`), maps tool→action via a fixed `TOOL_ACTIONS` dict, mints a
  fresh capiss token per call, calls the gateway. Emits a terminal
  `adapter_decision` event to **stderr** only (mint metadata + ok/reason). It
  does NOT currently log the inbound request or intent→action as a step.
- **capiss** `services/capability-issuer/app.py` — Authorization Server. Mints
  Biscuit tokens. Calls **OPA over HTTP** (`OPA_URL=http://opa:8181/v1/data/capiss/allow`)
  for the mint policy decision. Emits `capiss_mint_decision` to stdout. Holds the
  root signing key. **Consumes budget at mint time.**
- **gateway** `services/jira-mcp-gateway/server.py` — current per-SaaS PEP.
  Verifies the Biscuit (subject/aud/act/res/exp), enforces budget/rate via Redis
  Lua, holds the upstream Jira credential, does **Jira-specific REST translation**
  (ADF conversion, endpoint routing, summary shaping, epic verification). Emits
  `jiramcp_gateway_decision` to stdout incl. `upstream_called` / `upstream_status`.
- **mock** `services/jira-mcp-mock/server.py` — deterministic upstream. Records
  requests **in memory only** (`REQUEST_LOG`), queryable via `/__test__/requests`;
  prints nothing to stdout.
- **Envoy sidecars** — do **mTLS + SPIFFE identity only** (require client cert,
  match SAN allowlist, inject `x-spiffe-id: %DOWNSTREAM_PEER_URI_SAN%`). They do
  **NOT** do ext_authz. All authz decisions live in services.
- **audit tooling** `scripts/varambu_audit.py` — tails a **single** container
  (`spiffe-capability-issuer`), keeps only `capiss_mint_decision`, allowlist-
  scrubs forbidden/secret fields, writes `capiss_audit.jsonl` + `.log`.

### 1.2 The key fusion problem
`jira-mcp-gateway` fuses four responsibilities:
1. capability verification (generic)
2. governance / budget-rate (generic pattern)
3. upstream credential custody (generic pattern, specific value)
4. **Jira REST translation (bespoke — this is what doesn't scale)**

The pivot: delete #4 from our code (a vendor Jira MCP server already implements
it), keep #1 as the reusable verifier, and re-home #2/#3 per the decisions below.

---

## 2. Target architecture

```
                         AUTHORITY PLANE  (proprietary product)
                         ┌───────────────────────────────────────────────┐
                         │  capiss (AS, signing key, mint, budget consume) │
                         │  OPA (policy: who may mint what)                │
                         │  Redis (budget/rate/delegation state)           │
                         │  Audit (correlated evidence plane)              │
                         └───────────────▲───────────────────────────────┘
                                         │ mint (challenge-driven)
 Codex --stdio MCP--> [Adapter: transparent MCP proxy + capability client]
                                         │ forward JSON-RPC (+ Biscuit on retry)
                                         v
                         [Generic Verifier]  (open source, STATELESS)
                         · verify sig/exp/aud/subject                       ← code
                         · BIND used (act,res) == granted (act,res)         ← code
                         · derivation rule per tool (res = f(args))         ← data
                         · challenge on missing/insufficient token
                                         │ on ALLOW: strip token, forward
                                         v
                         [Off-the-shelf MCP gateway / MCP server]  (vendor)
                         · holds broad upstream credential                  ← isolated
                         · network-reachable ONLY via the verifier
                                         v
                                     SaaS API
```

Adopter chooses how the verifier is mounted (see §5). The agent never sees
upstream credentials or capiss signing material.

---

## 3. Decisions locked in this conversation

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | **Tool surface stays narrow & explicit** (currently 2 tools, IAM only). Broadening is a deliberate per-tool slice (action + OPA row + verifier rule), never "support everything." | Least-privilege thesis: authority must be the minted scope, not the breadth of the upstream API key. |
| D2 | **Mint via challenge/response** (OAuth/MCP-auth `401 → mint → retry`), not adapter-proactive minting. | Keeps the adapter a SaaS-agnostic dumb proxy; per-SaaS scope derivation lives in ONE place (the verifier). |
| D3 | **Stay with Biscuit** tokens (not bridge to OAuth/JWT scopes). | Fine-grained per-`(act,res)` capabilities + attenuation/delegation are the lab's whole point; OAuth scopes can't express them. Consequence: no off-the-shelf product verifies our token — we own the verifier regardless. |
| D4 | **Verifier = open-source SDK + reference SaaS verifiers + template/example.** Adopter forks/adapts. | OSS adoption + auditable enforcement point. The verifier holds NO secrets (only capiss public key), so it is safe to publish and to deploy in adopter infra. |
| D5 | **Deployment mode (plugin vs. in-front) is the ADOPTER's choice.** Verifier supports both mounts; product is indifferent. | "If the MCP gateway has pluggable authz, plug in; else front it — without reinventing the gateway." |
| D6 | **Product = capiss + OPA + Redis + audit** (authority + governance + evidence). **Verifier = stateless verification only.** | Clear moat/OSS line: product owns all state & authority lifecycle; verifier owns stateless checks. |
| D7 | **Budget consumed at MINT (capiss), not at verifier.** No offline delegation today — all delegation round-trips capiss — so governance is controlled at the single mint chokepoint. The verifier never touches Redis/budget. | Simplifies the verifier to fully stateless; no governance protocol leaks into OSS. |
| D8 | **The verifier's CORE duty is binding the actual call's `(act,res)` to the token's `(act,res)`.** | Validity (sig/exp/aud) is necessary but not sufficient; binding prevents a valid token being used for a different/illegal action or resource. |
| D9 | **Audit is a product capability fed by event sources via a published schema, correlated by `correlation_id`.** Verbatim user intent is sourced from Codex rollout logs. | Value is owning the correlated evidence across components you may not even have deployed. |

---

## 4. Challenge/response mint flow (D2) and why it is sound

```
1. Codex --stdio--> Adapter: tools/call {name, arguments}
2. Adapter --HTTP/mTLS--> Verifier: forwards JSON-RPC unchanged   (adapter has ZERO SaaS knowledge)
3. Verifier derives (act, res) from its per-tool rule, sees no token,
   replies 401 + challenge { aud, act, res }
4. Adapter --HTTP/mTLS--> capiss: root-mint {aud, act, res}        (copied verbatim from challenge)
5. capiss re-checks OPA: may THIS subject mint THIS (act,res)?     (the backstop)
        deny  -> adapter never gets a token; call dies
        allow -> capiss mints Biscuit scoped to exactly (aud,act,res); budget consumed here (D7)
6. Adapter retries step 2 WITH the Biscuit
7. Verifier verifies authenticity AND binds (act,res) of the ACTUAL call to the
   token (D8), then strips the token and forwards JSON-RPC to the vendor MCP server
```

**Why it is safe — the challenge cannot escalate authority:**
- The verifier *names* the scope, but **capiss/OPA independently decides** whether
  to mint it (step 5). A lying/compromised verifier can only challenge for scopes
  OPA still refuses.
- The verifier re-derives `(act,res)` from the **real call** at step 7, so a
  mismatched challenge just fails the binding check.
- The adapter stays a dumb generic proxy: forward → on 401 mint the named scope →
  retry. No tool→resource map anywhere in it.

**Cost:** one extra round trip on a cold call. Optimizations (adapter caches scope
per tool-shape; reuse still-valid Biscuit) exist but per-call freshness is a
design value — keep the simple version first.

**Standards note:** this *is* the OAuth/MCP-auth `401 → token endpoint → retry`
dance. We own both ends of adapter↔verifier, so the challenge can be a plain JSON
body now; it can later be reshaped as `WWW-Authenticate` + RFC 9728 Protected
Resource Metadata without changing the logic.

---

## 5. Verifier packaging: SDK core + one network service + two mounts (D4, D5)

### 5.1 Layered shape
**Layer 1 — verifier core (SDK / library).** Pure, dependency-injected, transport-agnostic:
```
authorize(ctx) -> Decision
   ctx = { caller_spiffe_id, mcp_method, tool_name, arguments, presented_biscuit? }
   Decision = ALLOW | CHALLENGE(aud, act, res) | DENY(reason)
   deps injected: capiss_public_key, per-SaaS derivation rules, clock
   (NO Redis, NO secrets — D6/D7)
```
This is the audited, mutation-tested, trusted unit. Everything else is glue.

**Layer 2 — wrap the SDK in ONE language-neutral network authz service (HTTP/gRPC).**
The same service serves both mounts; the only difference is whether it *also
forwards* or just *advises*:
- **Plugged in** (gateway has a hook): gateway calls the authz service per request
  → ALLOW/CHALLENGE/DENY → gateway enforces. (Envoy `ext_authz` shape — same
  structure as capiss calling OPA over HTTP.)
- **In front** (gateway has no hook): same service runs as a thin reverse proxy —
  calls `authorize()` itself, returns 401+challenge on CHALLENGE, forwards
  JSON-RPC on ALLOW.

### 5.2 Litmus test — when is a gateway's "pluggable authz" good enough to plug into?
Plugging in (vs. fronting) requires the hook to provide ALL of:
1. **Request body access** — `res` is derived from `arguments` in the JSON-RPC
   body. Header/path-only hooks force tool-granularity authz, which guts
   resource-level least privilege.
2. **Custom denial response** — challenge/response needs `401 + {aud,act,res}`.
   Boolean-only hooks can't carry the challenge.
3. **Header mutation** — to strip the Biscuit and/or inject upstream creds.
4. **Language neutrality (practical)** — in-process plugins need the SDK in the
   gateway's language (Go/TS). A **network callout is language-neutral**; prefer it.
   The front-proxy is the universal fallback; in-process plugins only for
   same-language or generic-exec hooks.

**Mechanical rule per gateway:** body-aware + custom-response + header-mutating
external-authz hook? Yes → plug in. No → front it. Same SDK + service either way.

### 5.3 Trust integrity when mounted in foreign hosts
The SDK **owns the decision**; the host **owns only execution**. Return a sealed
`Decision` with a single `enforce()` path, fail-closed by default, no host-side
"skip." Distributing the *deployment* of the verifier must not distribute
*discretion*. Network isolation still required: the vendor MCP server (holding the
broad credential) must be reachable ONLY through the verifier.

---

## 6. The verifier's core duty — call/token binding (D8)

> Primary responsibility, above sig/exp/aud: **re-derive `(act, res)` from the
> actual upstream call the verifier is about to place, and assert the token's
> `(act, res)` covers exactly that.** A token is authority for a specific action
> on a specific resource — never a bearer pass.

**Threat:** an agent legitimately mints a token for `(read, project:IAM)` (OPA
even allows it), then presents that valid, unexpired, correctly-audienced token
while calling `create_story` on `project:NAS`. Sig ✓ exp ✓ aud ✓ — but use exceeds
grant. Without binding this passes. Classic capability-confinement / confused-
deputy failure.

**Security property (composition):**
```
OPA at mint     ->  granted ⊆ policy        (can only mint what policy allows)
binding at use  ->  used    == granted      (can only use a token for its exact scope)
∴               ->  used    ⊆ policy        (least privilege holds at USE time, not just grant time)
```
Without binding you'd have grant-time policy only — a minted token becomes a
skeleton key. Binding is what makes the use-time guarantee real.

**Already present today:** `jira-mcp-gateway.verify_token(..., expected_act,
requested_project)` raises `act_mismatch` / `project_mismatch`. The generic
verifier must treat this as its *reason to exist*, not an incidental check.

**Two implementation consequences:**
1. **The resource-derivation rule is the binding oracle**, not just a
   mint/challenge convenience. Derive-and-compare = code (generic); per-tool
   derivation rule = data (per-SaaS). Adopters must review this rule hardest — a
   wrong rule is an enforcement hole.
2. **Derive → check → forward on ONE immutable copy (no TOCTOU).** Parse the body
   once, bind against that, forward that exact object. Never check one parse and
   forward a re-parse. (Current gateway already does this: validate → derive
   project → check → forward the validated `cleaned` payload.)

---

## 7. Code vs. data boundary (D6)

**Code (generic, SaaS-agnostic, in the OSS verifier core):**
- Biscuit signature validity
- `exp` expiry check
- **scope containment** (token `(act,res)` covers required `(act,res)`)
- `aud` match
- **subject binding** (token.subject == authenticated caller identity)
- the **derive-and-compare binding mechanism** (§6)
- challenge generation
- fail-closed default

**Data (per-SaaS / per-deployment, adopter-supplied):**
- audience string(s)
- allowed-scope / resource syntax (regex)
- capiss public-key location
- which upstream MCP server + network/identity bindings
- **per-tool resource-derivation rule** (`res = mcp:jira:/project:{args.project_key}`)

**The in-between (config-as-code):** resource derivation is data (template/JSONPath)
for the common 80%; a SaaS with an odd argument→resource shape needs a small code
hook. This is exactly why D4 ships "common SaaS verifiers + a template/example" —
data-driven for the common case, a tiny code extension point for the long tail.

**Identity:** the *check* (token.subject == caller) is code; *how identity arrives*
(e.g. Envoy `x-spiffe-id` injection) is deployment data.

---

## 8. The three published contracts (the real product surface)

Because the verifier is OSS and adopter-deployed, the product never touches it at
runtime — they bind only through interfaces. These ARE the product surface and the
only things to version carefully:

1. **Capability token claim schema** — Biscuit `(aud, act, res, exp, subject,
   delegation/depth, root_token_id, token_id, ...)`. How capiss (product) and
   verifier (OSS) agree.
2. **Challenge format** — the `401 + {aud, act, res}` the verifier returns so the
   adapter mints from capiss. (Optionally OAuth `WWW-Authenticate` + RFC 9728 later.)
3. **Audit event schema + `correlation_id`** — how every event source (verifier,
   capiss, adapter, mock/upstream) feeds the audit plane (product), which
   correlates and renders the chain.

Nail these three; everything else is swappable.

---

## 9. Full-chain audit (the originating thread)

### 9.1 Goal
Reconstruct one request end to end:
1. user request (intent) to Codex
2. Codex/adapter converts intent → structured action
3. mint request to capiss
4. minted token used to reach the verifier
5. verifier's enforcement checks (incl. binding)
6. upstream call (verifier → vendor MCP server)
7. upstream return

### 9.2 Binding key already exists
`docs/architecture.md` (ARCH-032 evidence) already declares the M5
`correlation_id` is meant to "reconstruct mint, enforcement, upstream, and
Codex-visible result." Every link already stamps `X-Correlation-ID`. It is just
never assembled into one view.

### 9.3 Key finding — verbatim user intent joins for free via Codex rollout logs
The raw Codex prompt never crosses the MCP stdio boundary (the adapter receives
only `tools/call {name, arguments}`; MCP has no standard field forwarding the
originating user message; Codex does not put it in `params._meta`). BUT Codex
(verified codex-cli 0.139.0) writes a full **rollout JSONL** per session under
`$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl`. A real past demo shows three
linkable records:
```
event_msg:user_message              "create a new story ... Created with varambu guard"   <- verbatim human prompt
response_item:function_call          create_story {project_key:IAM, ...}  call_id=Y        <- model's materialized action
response_item:function_call_output (call_id=Y)
        output -> {"ok":true,"correlation_id":"c103f5ee-...","key":"IAM-5",...}             <- OUR correlation_id
```
Because the adapter ALREADY echoes `correlation_id` in its tool result, and Codex
ALREADY records that result in its rollout, the verbatim user prompt joins cleanly
to the rest of the chain by `correlation_id`. No protocol injection or model-
supplied "intent" field needed — this is the faithful version (human's actual
words). Codex 0.139 lists MCP tools under bare names (`create_story`,
`read_project_summary`).

### 9.4 "A destination we control"
Today rollouts land in shared `~/.codex` (noisy; discovered by guesswork).
Proposed: `varambu start` provisions a **dedicated `CODEX_HOME`** (e.g.
`artifacts/varambu-demo/codex-home`, stable so `config.toml` / `codex mcp add`
persists), registers the MCP server there, and prints the launch line as
`CODEX_HOME=... codex -C ...`. Then every rollout lands in a varambu-owned tree we
fully control and can tail deterministically. Alternative to weigh: tail existing
`~/.codex/sessions` and locate the right rollout by scanning for the known
`correlation_id` in `function_call_output` records (no launch change, less control).

### 9.5 Assembled chain (per correlation_id)
| # | Source | Event | Auditor sees |
|---|--------|-------|--------------|
| 1 | Codex rollout | `user_message` | verbatim human request |
| 2 | Codex rollout | `function_call` | tool + arguments the model chose (intent→action) |
| 3 | adapter (NEW) | `adapter_request` | adapter received call, started mint |
| 4 | capiss | `capiss_mint_decision` | mint allow/deny under OPA (already captured) |
| 5 | verifier | `verifier_decision` (was `jiramcp_gateway_decision`) | sig/exp/aud/subject + **binding** checks |
| 6 | upstream (NEW stdout) | `upstream_request` | upstream's own record: received from verifier, returned status |
| 7 | verifier | (same allow event) | `upstream_called`/`upstream_status` + agent-visible result |

### 9.6 Decisions already made on the audit thread
- **Upstream leg:** log BOTH sides (upstream gets an independent audit voice, not
  just the verifier's account).
- **Presentation:** add a NEW correlation-grouped view (e.g. `varambu trace`);
  leave the existing capiss-only `varambu audit` intact.
- **Intent:** capture verbatim human prompt via Codex rollout (§9.3), not a model
  paraphrase.

### 9.7 Audit as a contract, not bespoke collection
Since the verifier is OSS/adopter-deployed, the audit plane must *ingest* events
the verifier *emits* per contract #8.3. Audit being "core product" is right: the
value is **owning the correlated evidence** across components (verifier, vendor
MCP server) we may not have deployed.

---

## 10. Secret hygiene (must carry into plan.md)

- Codex rollout output and upstream logs must pass the same forbidden-field /
  `Bearer` / `Basic ` / `biscuit` allowlist scrubbing `varambu_audit.py`
  `normalize_event` already enforces.
- Story `description` / `summary` are user content (not secrets) but must be
  size-bounded when displayed/persisted.
- Extract ONLY the joined `user_message` + `function_call` + `function_call_output`
  triple for the matching `correlation_id`; never copy whole rollouts (they carry
  developer instructions, reasoning, unrelated tool calls) into evidence files.
- The OSS verifier holds **only capiss's public key** + public config — no signing
  key, no OPA, no Redis, no upstream credential. This no-secrets property is what
  makes OSS publication + adopter deployment safe (D4).

---

## 11. Threat model summary

| Threat | Defense | Where |
|--------|---------|-------|
| Agent gets a broad upstream API key's power | Authority is the minted scope, not the key; key stays in isolated vendor MCP server | product + isolation |
| Agent mints authority beyond policy | OPA at mint: granted ⊆ policy | capiss + OPA |
| Agent uses a valid token for a different/illegal action or resource | **Binding at use: used == granted** | verifier (D8) |
| Compromised/lying verifier escalates authority | Challenge cannot mint; capiss/OPA backstops every mint | capiss + OPA (D2) |
| TOCTOU between check and forward | Parse-once, derive-check-forward one immutable copy | verifier (§6) |
| Foreign host (3rd-party gateway) bypasses decision | Sealed decision, single fail-closed `enforce()`, network isolation | verifier (§5.3) |
| Secret leakage via OSS verifier | Verifier holds only public key material | design (§10) |
| Audit blind spots | Independent event from each source incl. upstream; correlated by id | audit plane (§9) |
| Replay across delegation / budget abuse | Budget consumed at mint; all delegation online via capiss | capiss + Redis (D7) |

---

## 12. Anticipated build surface (NOT a one-liner; for future planning)

- **adapter** — become a transparent MCP proxy: forward JSON-RPC unchanged,
  handle 401 challenge → mint → retry; emit `adapter_request` to stdout.
- **verifier** — extract the generic verifier from `jira-mcp-gateway` (drop Jira
  REST glue); SDK core + network authz service + front-proxy mode; per-SaaS
  derivation-rule data; rename event to `verifier_decision`.
- **vendor MCP server** — mount an off-the-shelf Jira MCP server behind the
  verifier, network-isolated; it holds the upstream credential.
- **upstream/mock** — print `upstream_request` to stdout for the audit voice.
- **`scripts/varambu_audit.py`** — biggest change: tail multiple containers + the
  Codex rollout tree; normalize 4–5 event types (new allowlists); group by
  `correlation_id`; render the ordered chain; new `varambu trace` subcommand;
  capiss-only audit left intact.
- **`varambu`** — provision dedicated `CODEX_HOME`, register MCP there, start the
  multi-source tailer, print `CODEX_HOME=...` launch line.
- **docs** — extend ARCH-027/030/031/032 + new REQ/DD for the generic verifier and
  the audit chain; then UT/IT/E2E with exhaustive condition + BVA coverage and
  traceability (V-model + AGENTS.md slice workflow).
- **contracts** — formally document the three published contracts (§8) as the
  product/OSS interface.

---

## 13. Open questions for when we resume

1. Dedicated `CODEX_HOME` vs. scan existing `~/.codex/sessions` by `correlation_id`.
2. Associating `user_message` with the right `function_call` when one user turn
   triggers multiple tool calls (order vs. nearest-preceding heuristic).
3. Should `varambu trace` also fold in M3/M4 `tool-b` / `jira-tool` chains or stay
   M5-only for the first cut?
4. Which off-the-shelf Jira (and later GitHub/Slack/...) MCP servers to adopt;
   their auth/credential model and network-isolation story.
5. **Web-search pending:** which MCP gateways expose a body-aware, custom-response,
   header-mutating external-authz hook (decides plug-in vs. front per gateway).
6. Biscuit claim schema versioning strategy across product/OSS releases.
7. Whether to ever support **offline delegation** (would move some governance out
   of capiss and require the verifier to verify delegation chains / budgets
   offline — currently explicitly out of scope; all delegation is online via capiss).
8. Retention/format of rollout-derived intent lines per session under
   `artifacts/varambu-demo/<ts>/`.

---

## 14. Next step (when resumed)

Promote the agreed parts into `plan.md` + `test_plan.md` via grill-me, then follow
Phase 2/3/4 of the AGENTS.md slice workflow. Likely split into at least two
slices: (A) full-chain audit trace; (B) generic verifier extraction + adapter
transparent proxy + vendor MCP server. Nothing here is approved for tests or code
yet.
