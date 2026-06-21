# M5 Full-Chain Audit Trace — Test Plan

## Phase Status
`Phase 1: plan and review`. No test here is accepted until this plan and `plan.md` are approved.
Tests are written in Phase 2 strictly from this document; if a test needs a new assumption, stop
and update the slice bundle first.

## Test Strategy (ASIL-D)
Requirements (`REQ-M5-FT*`) are proven by black-box E2E (`M5-T49..T57`). Detailed design
(`DD-910..921`) is proven by exhaustive UTs. UT rigor is **exhaustive condition coverage**
(2^N combinations per decision) and **boundary value analysis** (B-1, B, B+1, limits exclusive)
per the process standard. Coverage targets: 100% statement/branch/condition, CC ≤ 10 per
function (refactor extractor/assembler into small helpers to hold this). No runtime-significant
behavior may exist only in code — every behavior below traces to a `DD` and a requirement.

## Inputs
- Approved `plan.md` (this slice).
- Validated codex-cli 0.139.0 rollout structure (see plan "Join Algorithm").
- Existing sources: `scripts/varambu_audit.py`, `services/codex-jira-mcp-adapter/server.py`,
  `services/jira-mcp-gateway/server.py`, `varambu`, `compose/spiffe.compose.yml`.
- Existing UT homes: `tests/unit/test_varambu_audit.py`, `tests/unit/jiramcp/test_adapter.py`
  (new: `tests/unit/test_varambu_trace.py` for assembler/extractor/renderer/CLI).

---

## Unit Test Plan

### DD-910 `normalize_gateway_event` (gateway leg normalizer)
Mirror the proven capiss-normalizer rigor.
| Area | Cases | Expected |
| --- | --- | --- |
| Event-type gate | event_type=`jiramcp_gateway_decision`; event_type=other; missing event_type | accept; `None`; `None` |
| Field allowlist | all approved fields; one unknown field added | kept in stable order; unknown dropped + warn |
| Forbidden field names | each of `token`,`Authorization`,`cookie`,`jira_api_token` present | dropped + warn |
| Forbidden value markers | value containing `Bearer `; `Basic `; `biscuit` (nested in dict/list) | record dropped/field dropped + warn |
| Decision shapes | `decision=allow` with `upstream_called/operation/status`; `decision=deny` (no upstream) | both normalize with correct fields; deny omits upstream fields when absent |

### DD-911 `normalize_adapter_event` (adapter leg normalizer)
| Area | Cases | Expected |
| --- | --- | --- |
| Event-type gate | `adapter_request`; `adapter_decision`; unrelated | accept both adapter types; reject unrelated → `None` |
| Allowlist + unknown | approved fields only; extra field | kept; extra dropped + warn |
| Forbidden names/markers | token/Authorization/cookie; `Bearer `/`Basic `/`biscuit` value | dropped + warn |
| Token metadata retained | `token_id`,`root_token_id` present, biscuit value absent | metadata kept; **no** raw token value ever present |
| Dangling request | `adapter_request` with no later `adapter_decision` for same `correlation_id` | normalizes; assembler later marks decision leg missing |

### DD-912 `extract_correlation_id` (from rollout records)
2 sources × content variants.
| Case | Input | Expected |
| --- | --- | --- |
| response_item, present | `function_call_output.output` string embedding `"correlation_id":"<uuid>"` | returns `<uuid>` |
| mcp_tool_call_end, present | `result.Ok.content[0].text` embedding the id | returns `<uuid>` |
| Absent | output with no `correlation_id` | returns `None` |
| Malformed JSON wrapper | output is non-JSON noise but contains the id literal | returns `<uuid>` (regex path) |
| Malformed + absent | non-JSON, no id | returns `None` |
| Multiple ids in one output | two `correlation_id` literals | returns the first / raises defined error (pin the contract) |
| Empty output | `""` / missing key | returns `None` |

### DD-913 `find_intent_triple` (rollout join) — **exhaustive condition coverage**
Decision gate conditions: `C1 = correlation_id located in a function_call_output`,
`C2 = call_id resolves to a function_call`, `C3 = function_call.name ∈ {read_project_summary,
create_story}`, `C4 = a user_message precedes that function_call`. Output is a complete triple
only when C1∧C2∧C3∧C4; otherwise a partial result with explicit missing markers. Enumerate all
2^4 = 16 combinations:

| # | C1 | C2 | C3 | C4 | Expected |
| --- | --- | --- | --- | --- | --- |
| 1 | F | F | F | F | no triple (intent `not available`); no crash |
| 2 | F | F | F | T | no triple (correlation not found dominates) |
| 3 | F | F | T | F | no triple |
| 4 | F | F | T | T | no triple |
| 5 | F | T | F | F | no triple |
| 6 | F | T | F | T | no triple |
| 7 | F | T | T | F | no triple |
| 8 | F | T | T | T | no triple |
| 9 | T | F | F | F | no triple (output present but no resolvable call_id) |
| 10 | T | F | F | T | no triple |
| 11 | T | F | T | F | no triple |
| 12 | T | F | T | T | no triple |
| 13 | T | T | F | F | filtered out (name is `exec_command`) → no triple |
| 14 | T | T | F | T | filtered out (name not ours) → no triple |
| 15 | T | T | T | F | action present, intent `not available` (no preceding user_message) |
| 16 | T | T | T | T | full triple {user_message, name, arguments, correlation_id} |

Attribution sub-matrix (all with C1..C4=T):
| Scenario | Setup | Expected |
| --- | --- | --- |
| Nearest-preceding | two user_messages before the call | the **nearest** is chosen |
| One turn → both tools | single user_message, then `read_project_summary` + `create_story` (two call_ids, two correlation_ids) | **two triples**, both attributing the same user_message |
| Interleaved turns | user_msg A → callA; user_msg B → callB | A↔callA, B↔callB (no cross-attribution) |
| exec_command noise between | our call, then `exec_command` calls under same turn | exec calls excluded; our call retains correct intent |
| mcp_tool_call_end corroboration | response_item present + mcp_tool_call_end present; then mcp_tool_call_end absent | identical triple both times (corroboration optional) |

### DD-914 `scrub_and_bound_triple` — **BVA (limits exclusive)**
`MAX_USER_MESSAGE = 2048` B, `MAX_TEXT = 1024` B (summary/description). Retained iff
`len < limit`; at/over limit ⇒ truncate to fit + append `…[truncated]`.
| Field | B-1 | B | B+1 | Expected |
| --- | --- | --- | --- | --- |
| user_message | 2047 B | 2048 B | 2049 B | kept whole; truncated+marker; truncated+marker |
| summary | 1023 B | 1024 B | 1025 B | kept whole; truncated+marker; truncated+marker |
| description | 1023 B | 1024 B | 1025 B | kept whole; truncated+marker; truncated+marker |

Plus scrub cases: forbidden field names removed; `Bearer `/`Basic `/`biscuit` values removed;
only `{correlation_id,user_message,tool_name,arguments,result(ok/reason/key/status)}` persisted;
reasoning / `exec_command` output / unrelated records **never** present in `trace.jsonl`;
idempotent re-write produces identical bytes for the same inputs.

### DD-915 `assemble_chains` — **exhaustive missing-leg + grouping + anchor + ordering**
Legs (canonical order): `intent, action, adapter_request, mint, gateway, adapter_decision`.
| Area | Cases | Expected |
| --- | --- | --- |
| Complete chain | all 6 legs present for one `correlation_id` | one chain, legs in canonical order |
| Single-leg-missing | each leg removed in turn (6 cases) | that slot rendered `not yet available`; others intact |
| Denied mint partial | intent, action, adapter_request, mint=DENY; no gateway/adapter_decision | partial chain ends at mint deny; later legs absent (not error) |
| Grouping | events for 2+ correlation_ids interleaved | distinct chains, zero cross-leg leakage |
| Out-of-order capture | feed legs in reverse/scrambled order | output still canonical leg order (not wall-clock sorted) |
| Duplicate leg | two records for same (correlation_id, leg) | deterministic single leg (pin first-wins/last-wins) |
| Unknown correlation in rollout only | rollout triple with id never seen in M5 sources | not surfaced |
| **Anchor rule** | id in `adapter_audit`/`gateway_audit`; id in **capiss-only** (tool-b style); id in M5 rollout action only | first two surfaced; **capiss-only NOT surfaced**; rollout-only not surfaced (no in-boundary anchor) |
| **Chain listing order** | three chains with different earliest in-boundary timestamps, captured out of order | chains listed in **request-start ascending** order |

### DD-916 `render_chain` / `render_chain_json` — **full audit trace**
| Area | Cases | Expected |
| --- | --- | --- |
| Mint leg reuse | allowed mint; denied mint | mint leg output **byte-identical** to existing `render_record` (`MINTED OK` / `DENIED: Reason …` + all capiss fields) |
| Full fields per leg | every leg present | each leg shows its full normalized fields (no concise truncation) |
| Leg header + Δ | complete chain | each leg headed `<LABEL> <local time> (+Δ since chain start)`; Δ labeled advisory; chain header shows start-local + `correlation_id` |
| Local-time display | session `VARAMBU_TZ` set; invalid TZ | local time rendered in TZ; invalid TZ falls back to UTC (no crash) |
| Δ across sources | rollout (host ms-UTC) + container legs | Δ computed from normalized UTC; never reorders legs |
| Human partial | missing legs | explicit `not yet available` lines; present legs still full |
| Live-mode upstream | mode=live | gateway leg labeled gateway-attested; no independent upstream voice |
| JSON | complete + partial | valid JSON; legs array canonical order; each leg carries `timestamp_utc`,`timestamp_local`,`sequence`; missing legs explicit |
| Render-time scrub | inject forbidden value into a leg | not emitted in either renderer |

### DD-917 `trace` CLI
| Area | Cases | Expected |
| --- | --- | --- |
| Default | current session, ≥1 chain | renders current session chains |
| `--cid <id>` | matching / non-matching id | one chain / friendly empty message |
| `--all` | two sessions | both, in session order, no dedupe |
| `--json` | any | machine-readable assembled chains |
| No session | no `current` | friendly "run varambu start" message, non-crash |
| Stale source | gateway/adapter tailer PID dead | advisory warning (parallels audit); `--strict` fails (if adopted) |
| Audit non-regression | run `varambu audit*` paths unchanged | identical to pre-slice behavior |

### DD-919 adapter `emit_adapter_event` (in `tests/unit/jiramcp/test_adapter.py`)
| Area | Cases | Expected |
| --- | --- | --- |
| Ordering | normal allowed call | `adapter_request` written before mint; `adapter_decision` after gateway |
| Crash visibility | exception between mint and gateway | `adapter_request` persists with no paired `adapter_decision` |
| Path wiring | `VARAMBU_SESSION_REL` set / unset | writes to `<session>/adapter_audit.jsonl` / safe no-op or default path (pin) |
| Secret discipline | minted token present in memory | file contains `token_id` metadata only, never the biscuit |
| correlation stamping | each event | carries the same `correlation_id` as the request |

### DD-918 / DD-920 / DD-921 (shell-level, in the rogue harness or a shell test)
| Decision | Cases | Expected |
| --- | --- | --- |
| Per-session CODEX_HOME (DD-920) | `varambu start` | `<session>/codex-home/` created; MCP registered into it; `CODEX_HOME=…` launch line printed |
| Bind mount + env (DD-921) | compose up | adapter has `/var/audit` mount + `VARAMBU_SESSION_REL=<stamp>` |
| Gateway tailer (DD-918/921) | start | second `docker logs --follow spiffe-jira-mcp-gateway` tailer alive; `gateway_tailer.pid` recorded |
| Trace dispatch | `varambu trace …` | routes to `varambu_audit.py trace` |

---

## E2E Test Plan (`M5-T49..T57`, default deterministic `--mock`)

### M5-T49 — Full chain, allowed (REQ-M5-FT1, FT2, FT3, FT9)
Premise: M5 mock path up; per-session CODEX_HOME; capiss+gateway tailers alive; adapter file
mounted; a rollout containing the verbatim prompt + `create_story` call + result is present.
Exercise: allowed `create_story` for `IAM`; run `varambu trace --json` and `varambu trace`.
Outcome: exactly one chain for the request's `correlation_id`; six legs in canonical order;
intent leg equals the verbatim prompt; every leg carries the same `correlation_id`; human render
readable. Evidence: `trace.jsonl`, `adapter_audit.jsonl`, `gateway_audit.jsonl`,
`capiss_audit.jsonl`, `varambu_trace.out`, `varambu_trace_json.out`, MCP req/resp.

### M5-T50 — Denied mint, partial chain (REQ-M5-FT1, FT4)
Premise: as above. Exercise: `read_project_summary` for `NAS` (policy deny); `varambu trace`.
Outcome: partial chain — intent, action, adapter_request, mint=DENY present; gateway and
adapter_decision-success legs shown absent; rendered as partial, not an error. Evidence: trace
output + per-source files showing the deny.

### M5-T51 — Intent pending then converge (REQ-M5-FT4)
Premise: in-boundary legs captured; rollout intent withheld (simulating un-flushed Codex).
Exercise: `varambu trace` (intent absent) → then make the rollout triple available → re-run.
Outcome: first run shows in-boundary legs with `intent: not yet available`; second run shows the
verbatim intent; no blocking; idempotent. Evidence: both trace outputs.

### M5-T52 — Multi-tool-call attribution (REQ-M5-FT2)
Premise: one rollout turn (single `user_message`) drives `read_project_summary` + `create_story`,
each with its own `correlation_id`. Exercise: `varambu trace`.
Outcome: two chains; each attributes the **same** verbatim `user_message`; each has its own
`correlation_id` and its own in-boundary legs; `exec_command` records (if any) excluded. Evidence:
trace output, `trace.jsonl` (two entries).

### M5-T53 — Secret hygiene + bounds of trace evidence (REQ-M5-FT6)
Premise: at least one source event/fixture carries forbidden fields/values (`token`,
`Authorization`, `Bearer `, `Basic `, cookie, Jira token) and an over-limit `user_message`/`summary`.
Exercise: run trace; inspect `trace.jsonl`, all per-source files, CLI output.
Outcome: no bearer/Basic/Jira/cookie/forbidden values anywhere; token *identifiers* may remain;
`user_message`>2048 B and text>1024 B truncated with `…[truncated]`; no whole-rollout content
(no reasoning, no `exec_command` output) in `trace.jsonl`.

### M5-T54 — Independent adapter voice / agent-tamper detection (REQ-M5-FT3, FT7)
Premise: a rollout whose `function_call_output` is **forged** to disagree with reality (e.g.
claims `ok:true` while the request was denied), sharing the request's `correlation_id`.
Exercise: `varambu trace`.
Outcome: the in-boundary legs (adapter_decision, capiss mint, gateway) reflect the true outcome
and **contradict** the forged agent result; trace presents the in-boundary truth and the
contradiction is observable by `correlation_id` (the agent cannot rewrite the adapter/capiss/
gateway records). Evidence: trace output + independent per-source files.

### M5-T55 — Honest upstream leg in live mode (REQ-M5-FT8)
Premise: `--live` with valid Jira env (env-gated; if unavailable, record the exact environment
error rather than claim completion). Exercise: allowed `create_story`; `varambu trace`.
Outcome: upstream leg is gateway-attested and explicitly labeled; **no** independent upstream
voice is fabricated; chain shape identical to mock except the upstream-voice label.

### M5-T56 — Trace CLI surface + audit non-regression (REQ-M5-FT9)
Premise: two sessions with distinct chains; `current` → second. Exercise: `varambu trace`,
`varambu trace --cid <id>`, `varambu trace --all`, `varambu trace --json`; then full `varambu
audit`, `audit --all/--json/--follow`, `audit-file`.
Outcome: default shows current session only; `--cid` selects one; `--all` shows both in order
(no dedupe); `--json` machine-readable; **all `varambu audit*` outputs unchanged** vs pre-slice.

### M5-T57 — Canonical ordering + cross-source join integrity (REQ-M5-FT1, FT7)
Premise: in-boundary events captured out of wall-clock order across sources. Exercise: `varambu
trace --json`. Outcome: legs always in canonical causal order (not timestamp-sorted); the join is
by `correlation_id` only; no leg leaks across chains; per-leg timestamps preserved for audit; the
captured per-source files remain in arrival order (capture order ≠ display order); multiple chains
listed in request-start ascending order.

### M5-T58 — Anchor rule + mint-leg reuse + timestamp display (REQ-M5-FT1, FT8, FT9)
Premise: a session where capiss also mints a **non-M5** token (e.g. a tool-b style root mint with
its own `correlation_id`) alongside one M5 `create_story`. `VARAMBU_TZ` set to a non-UTC zone.
Exercise: `varambu trace` and `varambu trace --json`.
Outcome: the M5 request is surfaced as a chain; the **capiss-only** non-M5 mint is **not** surfaced
as a trace chain (anchor rule); the mint leg of the surfaced chain is byte-identical to that mint's
`varambu audit` `render_record` output (`MINTED OK` + fields); each leg shows local time in the
configured TZ with an advisory `+Δ`; `--json` carries `timestamp_utc`/`timestamp_local`/`sequence`
per leg. Evidence: `varambu_trace.out`, `varambu_trace_json.out`, `capiss_audit.log` for the
byte-identical comparison.

---

## Assumptions and fixtures
- Default mode `--mock` (deterministic). `--live` only for M5-T55 and gated on real Jira env.
- Rollout fixtures are minimized JSONL shaped per the validated 0.139.0 structure; forged-output
  and over-limit fixtures are authored for M5-T53/T54.
- UTs are pure (no Docker): normalizers/extractor/assembler/renderer/scrub run on in-memory
  records and temp files; adapter emit UT uses a temp session dir via `VARAMBU_SESSION_REL`.
- E2E uses the rogue-tests harness with Premise/Exercise/Outcome evidence artifacts under
  `artifacts/rogue-tests/`.

## Failing baseline (before Phase 3)
1. Add all UTs and E2E `M5-T49..T57` from this plan.
2. Run targeted UTs and (if Docker available) targeted E2E; record the failing baseline.
3. Only then implement (Phase 3). If a test needs a new assumption, stop and update the bundle.

## Planned verification commands
Phase 2 failing baseline:
```bash
pytest -q tests/unit/test_varambu_audit.py tests/unit/test_varambu_trace.py tests/unit/jiramcp/test_adapter.py
make unit-guard-check
docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
  -e TEST_ONLY=M5-T49,M5-T50,M5-T51,M5-T52,M5-T53,M5-T54,M5-T56,M5-T57 rogue-tests
```
Phase 4 final verification:
```bash
make unit-trust
make qa-trace
make qa-quality
radon cc scripts/varambu_audit.py services/codex-jira-mcp-adapter/server.py -n B   # must be empty
docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
  -e TEST_ONLY=M5-T49,M5-T50,M5-T51,M5-T52,M5-T53,M5-T54,M5-T56,M5-T57 rogue-tests
make qa-evidence
```
Docker-backed E2E may be blocked without `/var/run/docker.sock`; if blocked, record the exact
environment error instead of claiming E2E completion. M5-T55 runs only with live Jira env.

## Approval Gates
- Phase 1 approval: this plan and `plan.md`.
- Authoritative docs approval: `REQ-M5-FT*`, `ARCH-033` + `ARCH-032` state extension, README,
  `trace/tests.yaml`.
- Phase 2 approval: tests and failing baseline.
- Phase 3 approval: implementation.
- Phase 4 closure: `make qa-trace`/`qa-quality`/`qa-evidence`, status capture in
  `docs/local_status_capture/implementation_status.md`.

## Review notes
- Pin the duplicate-leg policy (first-wins vs last-wins) and the multi-`correlation_id`-in-one-output
  contract before Phase 2.
- Confirm whether `--strict` is in scope for `varambu trace` (mirrors `audit --strict`) or deferred.
- Confirm gateway event already carries `act`/`res`; if not, the minimal echo is added under DD
  with no behavior change.

## Pinned decisions (resolved before Phase 2)
These resolve the four review notes above so Phase-2 tests derive from a fixed contract:
- **Duplicate-leg policy = first-wins.** When two records exist for the same
  `(correlation_id, leg)`, the **first captured** (lowest `sequence`/arrival) is authoritative.
  Rationale: arrival order is itself evidence (REQ-M5-FT8); the first in-boundary attestation
  is the one that cannot be retroactively rewritten.
- **Multiple `correlation_id`s in one rollout output = first match.** `extract_correlation_id`
  returns the **first** `correlation_id` literal found (regex order). In practice one
  `function_call_output` carries exactly one id; the first-match rule is deterministic and never
  raises.
- **`--strict` is deferred (out of scope).** The approved CLI shape (plan item 12) is
  `varambu trace [--cid <id>] [--all] [--json]` with no strict mode. The stale-source advisory
  warning is still emitted (parallels `audit`), but there is no failing strict path in this slice.
- **Gateway already carries `act`/`res`.** Confirmed in `jira-mcp-gateway` `_event_fields`
  (`aud`/`act`/`res` echoed from verified claims). No gateway behavior change is required (A4 holds).

---

## Increment 2 — Trace display redesign: test impact

The display redesign (plan.md Increment 2) changes the canonical leg model (6→7) and relaxes
REQ-M5-FT9, so tests change in lockstep. Tests-first: update/add below, record the failing baseline,
then implement.

### DD — new exhaustive-condition coverage
`derive_gateway_upstream` splits one `jiramcp_gateway_decision` into the gateway-enforcement and
upstream legs. Decision matrix (enumerate all, ASIL-D condition coverage):
| # | decision | upstream_called | upstream_status | Expected gateway leg | Expected upstream leg |
| --- | --- | --- | --- | --- | --- |
| 1 | allow | true  | 2xx        | ALLOW          | OK (status)          |
| 2 | deny  | true  | 4xx/5xx    | **ALLOW** (enforcement passed) | **FAIL** (status) ← the "who denied" case |
| 3 | deny  | false | (none)     | DENY (enforcement reason) | not reached (`—`) |
| 4 | allow | false | (none)     | ALLOW          | not reached (`—`) (defensive; allow implies a call) |
Plus BVA on the 2xx boundary for the upstream OK/FAIL split: status 200/201 → OK; 400/401/403/500 →
FAIL (representative below/at/above the 2xx band).

### UT changes (`tests/unit/test_varambu_trace.py`)
- `CHAIN_LEG_ORDER` 6→7 (`…, gateway, upstream, adapter_decision`): update every order/leg-count
  assertion (complete-chain, single-leg-missing set — add an `upstream`-missing case, out-of-order,
  JSON canonical order).
- **Mint reuse UT changes** (REQ-M5-FT9): the "mint leg byte-identical to `render_record`" UT becomes
  "mint leg presents the same fields" (token_id, root, aud/act/res, ttl, issued/expires, policy),
  full-length (no truncation).
- New layout UTs: spine columns aligned; labels `ADAPTER`/`UPSTREAM`/`RETURN TO CODEX`; full
  `token_id`/`correlation_id` present (wrap-not-truncate); status colour applied on a TTY and absent
  when not a TTY; `+Δ` absent from human view but present per-leg in `--json`.
- New `derive_gateway_upstream` UTs per the matrix above.
- `--json` UTs: legs array carries the new `upstream` leg with `timestamp_utc`/`sequence`; gateway
  leg no longer carries the upstream fields (they move to the upstream leg).

### E2E changes (`scripts/rogue_node_tests.sh` + `trace/tests.yaml`)
- **M5-T49 / M5-T57:** canonical order assertions 6→7; assert the `upstream` leg is present and
  distinct from `gateway`.
- **M5-T50:** mint-deny partial → assert **both** `gateway` and `upstream` legs absent.
- **M5-T55 (live):** the `gateway-attested (live)` label is asserted on the **upstream** leg.
- **M5-T58:** replace the mint "byte-identical diff" assertion with "mint fields present" in the
  table form.
- **New E2E (M5-T59):** gateway ALLOW + upstream FAIL renders as gateway `ALLOW` and upstream `FAIL`
  (not gateway deny) — the motivating case. Mock upstream cannot easily return 4xx, so this uses a
  synthetic `gateway_audit.jsonl` fixture (`decision=deny, upstream_called=true,
  reason=upstream_error, upstream_status=401`), mapped to REQ-M5-FT7 in `trace/tests.yaml`.

### Non-regression
- `varambu audit*` paths and the existing M5-T42..T48 audit E2E remain unchanged (the redesign does
  not touch the capiss audit renderer; `varambu audit` stays byte-exact).
