# M5 Full-Chain Audit Trace — Slice Plan

## Phase Status
`Phase 4: verification` complete. Phases 1–2 (plan + test_plan grill-me approved; UTs authored
tests-first with a recorded failing baseline) and Phase 3 (trace
assembler/normalizers/extractor/renderers/CLI in `scripts/varambu_audit.py`, the adapter
independent voice, launcher/compose wiring) are done and green. Phase 4: full unit suite (334) +
qa-trace + CC + ruff green; E2E `M5-T49..T58` authored in `scripts/rogue_node_tests.sh`, mapped in
`trace/tests.yaml`, and run **10/10 PASS** against the live mock stack (T55 live-gated auto-skip);
existing audit E2E `M5-T42..T48` re-run 7/7 (no regression). Evidence and the live-run notes are in
`docs/local_status_capture/implementation_status.md`. Only the real-Jira `M5-T55` live path and a
full interactive `varambu start` + `codex` agent run remain environment-gated. The companion
`docs/slices/m5-generic-verifier-architecture/brainstorm.md` remains a separate, later slice and is
out of scope here.

## Goal
Let an auditor follow one M5 Codex→Jira request end to end as a single ordered chain,
joined by `correlation_id`: verbatim human intent → model action → adapter → capiss mint →
gateway verification + upstream call → adapter result. A new `varambu trace` command
assembles and renders these chains on demand from per-source evidence; the existing
capiss-only `varambu audit` is left unchanged. Each in-boundary component (adapter, capiss,
gateway) speaks for itself so a misbehaving agent cannot rewrite the record; the agent is
trusted only for the one leg no in-boundary source can produce — the verbatim user prompt.

## Grill-Me Review Summary
Decisions locked during review (several deliberately *reverse* the brainstorm, with stronger
rationale):

1. **Capture model = hybrid.** Live `docker logs` capture for the in-boundary HTTP services
   (capiss reused, gateway new); the adapter writes its own file (it cannot use `docker logs`,
   see below); the Codex rollout is read **post-hoc**. Rationale: the rollout's `correlation_id`
   only appears *after* the round-trip completes, so live-tailing it buys nothing.
2. **Render-what's-there, re-runnable.** `varambu trace` never blocks. Missing legs render as
   `not yet available`; re-running fills them once Codex flushes its rollout. Partial chains
   (e.g. a denied mint that never reaches the gateway) are first-class, not errors.
3. **Per-session `CODEX_HOME`.** `varambu start` provisions `<session>/codex-home/`, registers
   the MCP server into it, and prints a `CODEX_HOME=… codex …` launch line. Rationale: rollout
   discovery becomes a single deterministic tree; each session dir is a self-contained evidence
   bundle; `start` is already a hard reset so cross-start `codex resume` was never meaningful.
4. **Adapter has an independent voice (not agent-derived).** The adapter emits `adapter_request`
   (entry) and `adapter_decision` (exit) to a bind-mounted file. Rationale: deriving the adapter
   leg from the Codex `function_call_output` would mean the *agent* attests to the adapter's
   behavior, widening the trust placed in the agent beyond the unavoidable intent leg. An
   independent record lets a forged agent output be detected by contradiction (cross-checked by
   `correlation_id`).
5. **Adapter transport constraint (discovered in code).** The adapter is reached via
   `docker compose exec -T … python /app/server.py`; its stdout is the MCP JSON-RPC channel to
   Codex and its stderr goes to the exec caller (Codex). Neither reaches `docker logs`. Therefore
   the adapter cannot emit audit to stdout (would corrupt MCP) and cannot be `docker logs`-tailed;
   it must write to a host-visible bind-mounted file.
6. **Upstream leg = gateway-attested only; no mock theater.** The brainstorm's "log both sides"
   is reversed. In `--live` the upstream is real Jira and cannot emit our event; manufacturing an
   independent voice only in `--mock` would make the demo look more auditable than production.
   The upstream leg is the gateway's `upstream_called`/`upstream_status` in **both** modes. The
   mock is untouched.
7. **Trust model.** We trust in-boundary components (adapter, capiss, gateway) to speak for
   themselves, exactly as we already trust capiss's self-reported mint. We trust the agent
   **only** for the verbatim user-intent leg, because no in-boundary source observes it. The
   `correlation_id` cross-check exposes an agent that forges its own record.
8. **Join algorithm = docker-anchored, response_item-primary, name-filtered, nearest-preceding.**
   Validated against a real codex-cli 0.139.0 rollout (see Join Algorithm below).
9. **Scope = M5 only.** tool-b/jira-tool (M3/M4) emit structured events but carry **no
   `correlation_id`** and have no Codex/human leg. Extending the trace there would require adding
   the join key as new plumbing only to produce a headline-less chain of things already audited
   by the rogue-tests evidence. Confirmed cost-without-value.
10. **Assemble-on-read.** `varambu trace` recomputes chains each run from per-source artifacts.
    Only the **scrubbed intent triple** is persisted (`<session>/trace.jsonl`), so durable
    evidence survives rollout cleanup while never duplicating per-leg data or going stale.
11. **Secret hygiene = surgical + bounded.** Persist only `{correlation_id, user_message,
    tool_name, arguments, result(ok/reason/key/status)}`; never persist reasoning, `exec_command`
    output, or whole rollout records. `user_message` ≤ 2048 bytes; `summary`/`description`
    ≤ 1024 bytes; `…[truncated]` marker. All sources re-scrubbed at read time through the existing
    allowlist (`FORBIDDEN_FIELD_NAMES`, `FORBIDDEN_TEXT`).
12. **CLI shape.** `varambu trace [--cid <id>] [--all] [--json]`; **no `--follow`** (post-hoc).
    Canonical causal leg order with per-leg timestamps; never wall-clock sorted across sources.

## Join Algorithm (validated against codex-cli 0.139.0)
Each rollout line is `{type, timestamp, payload}` (ISO-ms timestamps). Relevant records:

| Record | Path | Carries |
| --- | --- | --- |
| `event_msg/user_message` | `payload.message` | verbatim human prompt |
| `response_item/function_call` | `payload.{name, call_id, arguments, namespace}` | tool + args; `namespace` present for MCP tools |
| `response_item/function_call_output` | `payload.{call_id, output}` | output string with our `correlation_id` (escaped) |
| `event_msg/mcp_tool_call_end` | `payload.{call_id, invocation{server,tool,arguments}, result.Ok.content[].text}` | clean `server:"jira-mcp"` + result JSON with `correlation_id` |

Algorithm:
1. **Docker-anchored, M5-scoped.** The authoritative set of `correlation_id`s is the captured
   **M5-specific** in-boundary events (`adapter_audit`/`gateway_audit`), not capiss-only mints
   (see Anchor rule). For each, scan the session rollout tree for the `function_call_output` (or
   `mcp_tool_call_end`) whose text contains that `correlation_id` → obtain `call_id`.
2. Resolve the `function_call` by `call_id`; keep only `name ∈ {read_project_summary,
   create_story}` (corroborated by `namespace` present / `mcp_tool_call_end.server=="jira-mcp"`).
   This drops Codex built-in `exec_command` noise.
3. **Nearest-preceding `user_message`** (by record order/timestamp) is the verbatim intent.
   Empirically: one human turn producing several tool calls correctly attributes the same
   `user_message` to each — which is correct (one utterance caused them).
4. `response_item` records are primary (canonical, resume-stable). `mcp_tool_call_end`
   (`event_msg`) is optional corroboration only; never required (it may be version-dependent).

## Capture vs Display Specification
The captured files and the CLI are **not** the same thing: files are raw per-source evidence in
capture order; `varambu trace` is an assembled, joined, ordered *view* over them.

### Capture (files) — raw evidence, never reordered
One append-only JSONL **per source**, in arrival order, each line a normalized event carrying a
session-local `sequence` (identical convention to today's `capiss_audit.jsonl`):

| File | Written by | Events | Order |
| --- | --- | --- | --- |
| `capiss_audit.jsonl` (existing, unchanged) | capiss docker-logs tailer | `capiss_mint_decision` | arrival |
| `gateway_audit.jsonl` (new) | gateway docker-logs tailer | `jiramcp_gateway_decision` | arrival |
| `adapter_audit.jsonl` (new) | adapter process (bind-mounted) | `adapter_request`, `adapter_decision` | arrival |
| `trace.jsonl` (new) | `varambu trace` on read | scrubbed intent triple (one per `correlation_id`) | by request start |

Arrival order is itself evidence and is never rewritten. The rollout tree is transient input, not
a captured file.

### Display (`varambu trace`) — assembled chain
- Group events by `correlation_id`; render the six legs in **fixed canonical order**
  (`intent → action → adapter_request → mint → verify+upstream → adapter_decision`); missing legs
  render explicitly (`not yet available`).
- **Chains are listed in request-start order** — ascending by each chain's earliest in-boundary
  leg timestamp.
- Leg order is **never** wall-clock-sorted. Timestamps are shown, not used for leg ordering.

### Leg ↔ captured-event mapping (each captured event maps to exactly one leg)
| Leg | Captured source event |
| --- | --- |
| intent | rollout `user_message` → `trace.jsonl` |
| action | rollout `function_call` → `trace.jsonl` |
| adapter_request | `adapter_audit.jsonl` |
| mint | `capiss_audit.jsonl` |
| verify + upstream | `gateway_audit.jsonl` |
| adapter_decision | `adapter_audit.jsonl` |

### Anchor rule (which `correlation_id`s become chains)
`capiss_audit.jsonl` carries **all** mints, including non-M5 ones (e.g. tool-b root mints share
the capiss stream). A `correlation_id` is surfaced as an M5 chain **iff it appears in an
M5-specific in-boundary source** — `adapter_audit` OR `gateway_audit`. The rollout is
agent-written/untrusted, so an M5 rollout action **alone does not anchor** a chain (the verbatim
intent is attached to an already-anchored chain, never used to surface one). A capiss-only mint is
**not** surfaced (keeps the M5-only scope honest, prevents phantom chains).

### Rendering detail — full audit trace (not a concise view)
- The trace shows **full fields per leg**. The **mint leg reuses the existing capiss
  `render_record` verbatim** — same `MINTED OK` / `DENIED: Reason …` header and every field
  (`Subject/Action/Resource/Audience/Decision/Token ID/Root/Depth/Issued/Expires/Logged/TTL/UTC/
  Correlation/Policy`). The other legs render their full normalized fields in the same style.
- Each leg block is headed by `<LABEL>  <local time>  (+Δ advisory since chain start)`.
- **Timestamps:** human view shows local time (`VARAMBU_TZ`, `YYYY-MM-DD HH:MM:SS ZZZ`) plus an
  **advisory** `+Δ` from the chain's first leg (labeled advisory — cross-source clocks, Codex host
  vs containers, can skew; never used for ordering). `--json` carries `timestamp_utc`,
  `timestamp_local`, and the source `sequence` per leg.
- No concise mode. `--json` emits the full structured chain.

## Requirements
The authoritative, normative requirements are authored in `docs/requirements.md` and are the
**single source of truth** — this plan does not restate their behavior (avoids drift). New family
`REQ-M5-FT*` (Full-chain Trace):

- **REQ-M5-FT1** — Full-chain audit trace reconstruction and `varambu trace` command.
- **REQ-M5-FT2** — Verbatim user intent leg (rollout-sourced, correlation-joined, name-filtered,
  nearest-preceding).
- **REQ-M5-FT3** — Independent in-boundary evidence and trust minimization (adapter request +
  decision; agent trusted only for intent; tamper detectable by cross-check).
- **REQ-M5-FT4** — Partial chains and re-runnable assembly.
- **REQ-M5-FT5** — Controlled per-session intent-capture destination + printed launch line.
- **REQ-M5-FT6** — Secret-free, bounded trace evidence (minimal triple; prompt ≤ 2048 B,
  summary/description ≤ 1024 B; re-screened at read time).
- **REQ-M5-FT7** — Honest, mode-consistent (gateway-attested) upstream leg.
- **REQ-M5-FT8** — Capture model (arrival order), display ordering, anchor rule, M5-only scope.
- **REQ-M5-FT9** — Full-audit-trace presentation (mint leg matches `varambu audit`), local-time
  first, advisory elapsed offset, fixed causal leg order.

Depends on (unchanged): `REQ-M5-CJ*` (M5 MCP enforcement path), `REQ-M5-VA1` / `ARCH-032`
(Varambu session/audit), `REQ-M4-O2` (observability).

## Success criteria
- `varambu trace` on a session that ran one allowed `create_story` for `IAM` prints one chain
  with all seven legs in canonical order, the verbatim prompt at the head, and the matching
  `correlation_id` on every leg.
- A denied `read_project_summary` for `NAS` prints a **partial** chain that stops at the mint
  deny, with later legs shown as absent — not as an error.
- Running `varambu trace` before Codex flushes its rollout shows the in-boundary legs with
  `intent: not yet available`; re-running after flush shows the verbatim intent.
- A single human turn that triggers both tools yields two chains, each attributing the same
  verbatim `user_message`, each with its own `correlation_id`.
- `<session>/trace.jsonl`, all per-source files, and CLI output contain no secret-bearing values;
  `user_message`/`summary`/`description` are bounded with `…[truncated]` when over the limit.
- `varambu audit`, `varambu audit --all/--json/--follow`, and `varambu audit-file` behave exactly
  as before (no regression).
- In `--live`, the upstream leg renders gateway-attested with an explicit label and no fabricated
  independent voice.

## In scope
- `services/codex-jira-mcp-adapter/server.py` — emit `adapter_request` (entry) and
  `adapter_decision` (exit) as structured JSON to a bind-mounted audit file; keep existing stderr
  line for live MCP debugging.
- `services/jira-mcp-gateway/server.py` — no behavior change; its existing `jiramcp_gateway_decision`
  (incl. `upstream_called`/`upstream_operation`/`upstream_status`) is the gateway/upstream leg.
  (Confirm the event already carries everything needed; add `act`/`res` echo only if missing.)
- `scripts/varambu_audit.py` — add: gateway-event normalizer; adapter-event normalizer; rollout
  intent extractor + correlation extraction; intent scrub/bounding + `trace.jsonl` writer; chain
  assembler; trace renderer (human + `--json`); `trace` subcommand.
- `varambu` (launcher) — provision per-session `CODEX_HOME`, register MCP there, print
  `CODEX_HOME=…` launch line; start a second `docker logs` tailer for the gateway; add the
  `artifacts/varambu-demo`→`/var/audit` bind mount and `VARAMBU_SESSION_REL` env wiring; add
  `varambu trace` dispatch.
- `compose/spiffe.compose.yml` — add the adapter audit bind mount + `VARAMBU_SESSION_REL` env.
- Docs: `ARCH-033` (new) + extend `ARCH-032` state inventory; new `REQ-M5-FT*`; source-embedded
  `DD-910..921`; `trace/tests.yaml` mappings for new E2E and IT; README trace section.

## Out of scope
- The generic verifier extraction, challenge/response mint, call/token binding, vendor MCP server
  (the companion brainstorm — a separate slice).
- Any mock changes / independent upstream voice / live-mode interposer.
- Any M3/M4 (`tool-b`, `jira-tool`, `rogue`) `correlation_id` plumbing or trace coverage.
- Changing `varambu audit` semantics or the capiss audit schema/normalizer.
- A live/streaming `varambu trace --follow`.

## Hidden-state and trust decisions
New/changed state (also added to the `ARCH-032`/`ARCH-033` Authoritative State inventory):

| State/key | Store/system | Writer | Reader | TTL/lifecycle | Decision impact | Classification |
| --- | --- | --- | --- | --- | --- | --- |
| Adapter audit records | `<session>/adapter_audit.jsonl` (bind-mounted) | adapter process | `varambu trace` | Per session, append-only | Independent adapter leg; enables agent-tamper detection by contradiction | Evidence (in-boundary, authoritative for adapter behavior) |
| Gateway audit copy | `<session>/gateway_audit.jsonl` | gateway docker-logs tailer | `varambu trace` | Per session, append-only | Gateway verification + upstream leg | Evidence copy (authoritative source is gateway stdout) |
| Persisted intent triple | `<session>/trace.jsonl` | `varambu trace` (on read) | operators/tests | Per session; rewritten idempotently | Durable, scrubbed, bounded intent/result evidence | Evidence copy (derived from agent-attested rollout) |
| Per-session `CODEX_HOME` | `<session>/codex-home/` (`config.toml` + `sessions/`) | `varambu start` (+ Codex) | `varambu trace` | Per session | Deterministic rollout discovery; MCP registration | Untrusted input tree (agent-written rollouts) |
| `VARAMBU_SESSION_REL` | adapter container env | `varambu start` | adapter | Container lifetime | Selects the session dir the adapter writes its audit file into | Runtime config |
| Gateway tailer PID | `<session>/gateway_tailer.pid` | `varambu start` | `varambu trace`/operator | Session lifecycle | Warns when the gateway leg may be stale | Advisory |

Trust boundary: the per-session `CODEX_HOME` rollout tree is **agent-written / untrusted** — used
only for the intent leg and re-scrubbed/bounded on read. All other legs originate inside the trust
boundary. No secret material is added to any new file (the adapter logs token *metadata* only,
never the biscuit; trace re-scrubs regardless).

## Authored source changes
- **Requirements:** add `REQ-M5-FT1..FT9` to `docs/requirements.md`.
- **Architecture:** add `ARCH-033 Varambu Full-Chain Audit Trace` (Satisfies the `REQ-M5-FT*`
  family; depends on `ARCH-027` adapter, `ARCH-030/031` gateway/mint path, `ARCH-032` session);
  extend the `ARCH-032` Authoritative State table with the rows above.
- **Runtime proof:** `trace/tests.yaml` — map new E2E `M5-T49..T57` → `REQ-M5-FT*`, and new IT
  cases → `ARCH-033`; source-embedded `DD-910..921` tags on the new functions.

## Detailed design IDs (source-embedded `DD-9xx`)
- **DD-910** `normalize_gateway_event` — allowlist normalizer for `jiramcp_gateway_decision`.
- **DD-911** `normalize_adapter_event` — allowlist normalizer for `adapter_request`/`adapter_decision`.
- **DD-912** `extract_correlation_id` — pull `correlation_id` from `function_call_output.output`
  / `mcp_tool_call_end` result text (regex + nested-JSON fallback).
- **DD-913** `find_intent_triple` — docker-anchored rollout join: name-filter, call_id resolve,
  nearest-preceding `user_message`.
- **DD-914** `scrub_and_bound_triple` — surgical scrub + size bounds; writer of `trace.jsonl`.
- **DD-915** `assemble_chains` — group per-source events by `correlation_id`; **anchor rule**
  (surface only ids present in `adapter_audit`/`gateway_audit` in-boundary evidence, not capiss-only
  and not rollout-action-only);
  canonical leg order; chain listing in request-start order; partial/missing-leg handling.
- **DD-916** `render_chain` / `render_chain_json` — full-audit-trace renderers. Human view reuses
  the existing capiss `render_record` for the mint leg verbatim (`MINTED OK`/`DENIED: Reason …`),
  renders every leg's full fields, heads each leg with `<LABEL> <local time> (+Δ advisory)`; JSON
  view carries full fields + `timestamp_utc`/`timestamp_local`/`sequence` per leg.
- **DD-917** `trace` (CLI subcommand) — `--cid/--all/--json`, current-session default.
- **DD-918** gateway docker-logs tailer wiring (second tailer alongside the capiss tailer).
- **DD-919** adapter `emit_adapter_event` — `adapter_request`/`adapter_decision` to the
  bind-mounted session file.
- **DD-920** `varambu start` per-session `CODEX_HOME` provisioning + MCP registration + launch line.
- **DD-921** `varambu start` bind-mount + `VARAMBU_SESSION_REL` + second-tailer startup wiring.

## Retirement and compatibility
- Nothing in `varambu audit` / capiss audit path is removed; it is a strict superset (new `trace`
  alongside existing `audit`).
- The adapter's existing terminal `adapter_decision`-to-stderr line is **kept** for live MCP
  debugging; the new authoritative copy is the bind-mounted file. (Decide in Phase 3 whether to
  also keep stderr or route both through one emitter — no behavior depends on stderr.)
- No mock changes; `/__test__/requests` stays for existing E2E assertions.

## Review notes (assumptions to approve before Phase 2)
- A1: codex-cli rollout structure (validated on 0.139.0) is treated as stable for the demo
  environment; `response_item` records are primary and `mcp_tool_call_end` is optional. If the
  pinned Codex version changes the schema, the extractor's record selectors must be revisited.
- A2: two concurrent `docker logs --follow` read-subprocesses (capiss + gateway) are acceptable
  and are not "Docker lifecycle commands" under the AGENTS.md serialization rule.
- A3: bounding limits (`user_message` 2048 B, `summary`/`description` 1024 B) are treated as
  exclusive upper limits per the BVA convention (`len > limit ⇒ truncate + marker`).
- A4: gateway `jiramcp_gateway_decision` already carries every field the gateway/upstream leg
  needs; if `act`/`res` are not present they will be added as a minimal echo (no behavior change).

---

## Increment 2 — Trace display redesign (locked 2026-06-20)

Follows live Codex/Jira testing. Pure presentation + leg-model refinement; **no enforcement, mint,
gateway, or capiss change**. Re-enters the V-model (REQ → ARCH → DD → UT/IT/E2E) because it changes a
normative requirement and the canonical leg model. Tests-first, not a patch.

### Motivation
- The single rendered chain is long and reads as a raw `key: value` dump; timestamps mix clean local
  zone (headers, mint block) with raw UTC (`…Z`) in leg bodies.
- The gateway leg conflates **gateway enforcement** with the **upstream call outcome**: when the
  gateway passes enforcement, calls upstream, and upstream fails (e.g. expired Jira token → 401), the
  one event is logged `decision=deny, reason=upstream_error`, so it reads as if the **gateway** denied
  when the gateway allowed and the **upstream** rejected ("who is denying?").
- No status colour parity with `varambu audit` (green minted / red denied).

### Locked decisions
1. **Seven legs** (was six): `intent, action, adapter_request, mint, gateway, upstream,
   adapter_decision`. The `gateway` and `upstream` legs are **derived from the single
   `jiramcp_gateway_decision` event** (no gateway change; A4 holds):
   - gateway leg = `ALLOW` iff `upstream_called==true` OR `decision==allow`; else `DENY` with the
     enforcement reason (`token_invalid`/`aud_mismatch`/`act_mismatch`/`project_mismatch`/
     `budget_exhausted`/`rate_limited`/`gateway_unavailable`/…).
   - upstream leg = present iff `upstream_called==true`; status from `upstream_status` (`OK` if 2xx,
     else `FAIL`); when not called, rendered as not-reached (`—`). Remains **gateway-attested** in
     both mock and live (REQ-M5-FT7) — the attestation label moves from the gateway leg to the
     upstream leg.
2. **Display labels:** leg 3 `adapter_request` → **`ADAPTER`** (reverted from `FROM CODEX` on
   2026-06-21 — `ADAPTER` is easier to demo and explain); leg 7 `adapter_decision` →
   **`RETURN TO CODEX`**. JSON `event_type`/leg keys stay `adapter_request`/`adapter_decision` and a
   new `upstream` key is added — schema stays stable and machine-greppable.
3. **One detailed table per chain** (a "log" = boxes stacked), not a summary+drill-in split. Each
   chain is a box: header states the outcome up front + the **full** `correlation_id` on its own
   line; rows share a fixed spine (`# · LEG · TIME(local) · STATUS`) with aligned, **grouped**
   label/value detail underneath (mint grouped identity → grant → validity → policy).
4. **Mint as a normal table row** with the same fields, **relaxing REQ-M5-FT9** from "byte-identical
   to `varambu audit` `render_record`" to "the mint leg presents the same fields." (`varambu audit`
   itself is unchanged and remains the byte-exact view.)
5. **Full identifiers, wrap-don't-truncate.** `correlation_id`, `token_id`, `root_token_id`,
   `policy_id` shown in full (they are non-secret correlation keys; the biscuit is the only secret and
   is never shown). Width handled by wrapping the detail cell, never by truncation.
6. **Colour parity** with `varambu audit`: green for `OK`/`ALLOW`, red for `DENY`/`FAIL`, dim `—`;
   TTY-only, plain when piped. Box-drawing on a TTY, plain aligned text when piped; `--json` keeps
   every field exact (now including the split `gateway`/`upstream` legs).
7. **`+Δ advisory`** dropped from the human view for width; retained per-leg in `--json`.

### Scope
- In scope: `scripts/varambu_audit.py` — new `derive_gateway_upstream` (DD), 7-entry
  `CHAIN_LEG_ORDER`, box/table `render_chain` + plain fallback, `render_chain_json` upstream leg,
  full-id formatting. Docs: REQ-M5-FT7/FT9 wording, ARCH-033 leg model + renderer, new DD ids.
  Tests: UT updates + new exhaustive-condition UTs for the derivation; E2E updates + one new case.
- Out of scope: any change to capiss, gateway, adapter enforcement, the mock, or `varambu audit`.

### Retirement
- The six-leg `CHAIN_LEG_ORDER` and the "byte-identical mint block" rendering are **retired**, with
  the REQ-M5-FT9 wording updated to match. `varambu audit` is untouched.
