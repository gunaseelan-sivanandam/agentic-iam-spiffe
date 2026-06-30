# Slice Brainstorm — Full-Chain Audit Trace (M5)

> STATUS: **BRAINSTORM / NOT APPROVED.** This is a captured design exploration to
> revisit later. It is not a `plan.md` and has not been through grill-me review.
> Do not write tests or code from this document. When we resume, promote the
> agreed parts into `plan.md` + `test_plan.md` per the AGENTS.md slice workflow.

## Problem / motivation

Today the Varambu audit shows only **one link** of the chain: the `capiss`
mint decision. For complete auditability we want an auditor to follow a single
request end to end:

1. user request (intent) to Codex
2. Codex / adapter converts intent into a structured action
3. mint request to `capiss`
4. minted token used to reach the gateway
5. gateway's own enforcement checks
6. upstream call (gateway -> mock/Jira)
7. upstream return

The binding key already exists: `docs/architecture.md` (ARCH-032 evidence row)
already declares the M5 correlation ID is meant to "reconstruct mint,
enforcement, upstream, and Codex-visible result." It is just never assembled
into one view.

## Current state (verified 2026-06-13)

- `scripts/varambu_audit.py tail` tails a **single** container
  (`spiffe-capability-issuer`) and keeps only `capiss_mint_decision` events.
- **adapter** (`services/codex-jira-mcp-adapter/server.py`) emits a terminal
  `adapter_decision` event to **stderr** only, carrying mint metadata + ok/reason.
  It does NOT log the inbound request (tool + arguments) or the intent->action
  mapping as a distinct step.
- **capiss** emits `capiss_mint_decision` to stdout (the one thing audited today).
- **gateway** (`services/jira-mcp-gateway/server.py`) emits
  `jiramcp_gateway_decision` to stdout — already carries its checks plus
  `upstream_called` / `upstream_operation` / `upstream_status`.
- **mock** (`services/jira-mcp-mock/server.py`) records requests only in memory
  (`REQUEST_LOG`, queryable via `/__test__/requests`); prints nothing to stdout.
- Every link already stamps a shared `X-Correlation-ID`.

## Decisions captured so far

- **Upstream leg:** log BOTH sides. Add stdout logging to the mock (its own
  receipt + response) AND keep the gateway's `upstream_called`/`upstream_status`.
  The upstream gets an independent audit voice instead of trusting the gateway's
  account alone.
- **Presentation:** add a NEW correlation-grouped view (e.g. `varambu trace`)
  that collects all event types from all containers, groups by `correlation_id`,
  and renders the chain in order. Keep the existing capiss-only `varambu audit`
  intact.
- **User intent:** capture the **verbatim** human prompt (not a model paraphrase),
  sourced from Codex's own logs. See next section.

## Key finding — the NL prompt join is already available

The raw Codex prompt never crosses the MCP stdio boundary (the adapter only ever
receives a JSON-RPC `tools/call` with `{name, arguments}`; MCP has no standard
field where Codex forwards the originating user message, and Codex does not put
it in `params._meta`). So passive reading at the adapter cannot recover it.

BUT Codex (verified with codex-cli 0.139.0) writes a full **rollout JSONL** per
session under `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl`. A real past demo
session shows the three linkable records:

```
event_msg:user_message        "create a new story ... Created with varambu guard"   <- verbatim human prompt
response_item:function_call     create_story {project_key:IAM, summary:..., ...}  call_id=Y   <- model's materialized action
response_item:function_call_output (call_id=Y)
        output -> {"ok":true,"correlation_id":"c103f5ee-...","key":"IAM-5",...}      <- OUR correlation_id
```

Because the adapter **already** echoes `correlation_id` in its tool result, and
Codex **already** records that result in its rollout, the verbatim user prompt
joins cleanly to the rest of the chain by `correlation_id`. No protocol
injection or model-supplied "intent" field is needed. This is the faithful
version: the human's actual words, joined cryptographically-by-id to mint →
gateway → upstream.

Observed in `~/.codex/sessions` (examples):
- prompt "use jira tools to read project IAM" -> `read_project_summary {IAM}`
  -> output `{"ok":true,"correlation_id":"cc718b27-...",...}`
- prompt "Now read NAS project" -> `read_project_summary {NAS}`
  -> output `{"ok":false,"reason":"mint_denied","correlation_id":"d0855b67-...","status":403,"capiss_reason":"policy"}`

Codex 0.139 lists MCP tools under their **bare** names (`create_story`,
`read_project_summary`), not namespaced.

## "A destination we always control"

Today rollouts land in the user's shared `~/.codex` — noisy (every unrelated
Codex session mixed in) and discovered by guesswork.

Proposed: `varambu start` provisions a **dedicated `CODEX_HOME`**
(e.g. `artifacts/varambu-demo/codex-home`, stable across sessions so
`config.toml` / `codex mcp add` registration persists), registers the MCP server
into that home, and prints the launch line as `CODEX_HOME=... codex -C ...`.
Then every rollout lands in a varambu-owned tree we fully own and can tail
deterministically.

Open alternative to weigh later: just tail the existing `~/.codex/sessions`
and locate the right rollout by scanning for the known `correlation_id` in
`function_call_output` records (works without changing how the user launches
Codex, but less "controlled").

## Proposed assembled chain (per correlation_id)

| # | Source | Event | Auditor sees |
|---|--------|-------|--------------|
| 1 | Codex rollout | `user_message` | verbatim human request |
| 2 | Codex rollout | `function_call` | tool + arguments the model chose (intent->action) |
| 3 | adapter (NEW) | `adapter_request` | adapter received call, mapped tool->act/res, started mint |
| 4 | capiss | `capiss_mint_decision` | mint allow/deny under OPA (already captured) |
| 5 | gateway | `jiramcp_gateway_decision` | token/subject/aud/act/project checks + budget/rate |
| 6 | mock (NEW stdout) | `jiramcp_upstream_request` | upstream's own record: received from gateway, returned status |
| 7 | gateway | (same allow event) | `upstream_called`/`upstream_status` + Codex-visible result |

## Anticipated build surface (not a one-liner)

- **adapter** `server.py` — emit explicit `adapter_request` step to **stdout**
  (currently only terminal `adapter_decision` on stderr).
- **mock** `server.py` — print `jiramcp_upstream_request` to stdout
  (currently in-memory only).
- **`scripts/varambu_audit.py`** — biggest change: tail MULTIPLE containers + the
  Codex rollout tree; normalize 4–5 event types with new allowlists; group by
  `correlation_id`; render the ordered chain. New `varambu trace` subcommand;
  capiss-only audit left intact.
- **`varambu`** — provision dedicated `CODEX_HOME`, register MCP there, start the
  multi-source tailer, print the `CODEX_HOME=...` launch line.
- **docs** — extend `ARCH-032` (currently capiss-only) + new REQ/DD; then
  UT/IT/E2E with exhaustive condition + BVA coverage and traceability.

## Secret-hygiene constraints (must carry into plan.md)

- Codex rollout output and mock logs must pass through the same forbidden-field /
  `Bearer` / `Basic ` / `biscuit` allowlist scrubbing that
  `normalize_event` already enforces in `varambu_audit.py`.
- Story `description` / `summary` are user content (not secrets) but must be
  size-bounded when displayed/persisted.
- The rollout contains far more than the prompt (developer instructions, reasoning,
  unrelated tool calls) — extract ONLY the joined `user_message` +
  `function_call` + `function_call_output` triple for the matching
  `correlation_id`; do not copy the whole rollout into evidence files.

## Open questions for when we resume

- Dedicated `CODEX_HOME` vs. scan existing `~/.codex/sessions` by correlation_id.
- How to associate `user_message` with the right `function_call` when a single
  user turn triggers multiple tool calls (order vs. nearest-preceding heuristic).
- Whether `varambu trace` should also fold in the M3/M4 `tool-b` / `jira-tool`
  chains or stay M5-only for the first cut.
- Retention: rollout-derived intent lines persisted per session under
  `artifacts/varambu-demo/<ts>/` alongside existing capiss audit files?

## Next step (when resumed)

Promote the agreed parts into `docs/slices/m5-full-chain-audit-trace/plan.md` +
`test_plan.md` via grill-me, then follow Phase 2/3/4 of the AGENTS.md slice
workflow. Nothing here is approved for tests or code yet.

## See also

`docs/slices/m5-generic-verifier-architecture/brainstorm.md` — the broader product
architecture (generic OSS verifier, capiss/OPA/Redis/audit as product,
challenge/response mint, call/token binding) that this audit thread grew into.
That document is the fuller end-to-end capture; this one is the audit-specific
detail.
