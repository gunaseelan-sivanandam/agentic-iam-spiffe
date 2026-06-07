# M5 Varambu Audit Demo Plan

## Phase Status
This slice is in `Phase 1: plan and review`.

The current working-tree implementation is an untrusted spike. It may be used as reference material after review, but it is not accepted implementation evidence, is not proof of TDD, and must not be treated as authoritative behavior until the approved slice plan is followed by tests-first implementation.

Do not update `docs/requirements.md`, `docs/architecture.md`, README, source, trace mappings, or tests for this slice until this Phase 1 bundle is approved.

## Goal
Make the Varambu demo show every capiss token mint decision in one operator-facing audit view. The audit view must include both minted and denied requests, append new events as they happen, show local time for demo readability, preserve structured evidence, and avoid leaking bearer token values or other secrets.

The operator demo story should use one coherent interface:

- `varambu start`
- `varambu audit`
- `varambu show-audit-logs`
- `varambu audit-file`

## Approved Grill-Me Decisions

### Command Interface
| Decision | Approved behavior |
| --- | --- |
| Top-level command | Add a repo-level `varambu` command as the coherent demo entrypoint. |
| Compatibility | Keep `start_Varambu` as a compatibility wrapper around `varambu start`. |
| Bare command support | On `varambu start`, create or update `$HOME/.local/bin/varambu` when safe so the operator can run `varambu` instead of `./varambu`. If an existing non-symlink is present, warn and do not overwrite it. |
| Start command | `varambu start [--live|--mock] [--timezone ZONE] [--no-build] [--no-codex-config]`. |
| Audit command | `varambu audit` and alias `varambu show-audit-logs`. |
| Audit file command | `varambu audit-file` prints direct paths for the current session audit files. |
| Current session default | `varambu audit` and `varambu audit-file` default to the current session. |
| History option | `--all` shows historical session logs or file paths. No dedupe is required because every `varambu start` creates a new session. |
| JSON option | `varambu audit --json` reads the persisted JSONL file. |
| Human option | Default `varambu audit` reads the persisted human-readable log. |
| Follow option | `varambu audit --follow` follows the persisted current-session file. It does not scrape Docker logs or post-process historical output. |

### Session Model
| Decision | Approved behavior |
| --- | --- |
| Session start | Every successful `varambu start` begins a new demo session. |
| Session directory | Session artifacts live under `artifacts/varambu-demo/<session-id>/`. |
| Current pointer | `artifacts/varambu-demo/current` points to the current session. |
| Previous tailer | `varambu start` stops the previous session tailer before starting a new stack/session. |
| Tailer freshness | `varambu audit` warns when a PID file exists but the tailer is not live. A strict mode may fail instead of warning. |
| No post-processing | `varambu audit` only reads already-persisted files. New mint or deny requests must already be appended by the active tailer. |

### Active Audit Tailing
| Decision | Approved behavior |
| --- | --- |
| Audit source | Container stdout from `spiffe-capability-issuer` remains the authoritative source for `capiss_mint_decision`. |
| Varambu files | Varambu audit files are session evidence copies, not a new source of authorization truth. |
| Tail command | The tailer follows `docker logs --since <session-start-utc> --follow spiffe-capability-issuer`. |
| Tailer lifecycle | `varambu start` starts the tailer after capiss is available and before the demo asks the user to run MCP requests. |
| Tailer startup failure | Tailer startup failure fails `varambu start`. |
| Retry policy | Tailer startup may retry up to 3 attempts. Each attempt must prove the process remains live after a 2 second health window. |
| Ordering | The tailer appends normalized events to the end of the session files in observed log order. |
| Sequence numbers | Session-local sequence numbers are added by the tailer, not by capiss. |

### Audit Artifacts
| Artifact | Purpose |
| --- | --- |
| `capiss_audit.jsonl` | Structured append-only session evidence. |
| `capiss_audit.log` | Human-readable append-only session evidence. |
| `audit_tailer.pid` | Advisory tailer liveness check. |
| `audit_tailer.err` | Tailer diagnostics. |
| `start.log` | Varambu startup diagnostics. |

Both `capiss_audit.jsonl` and `capiss_audit.log` must be viewable directly from the filesystem.

### Capiss Event Schema
| Decision | Approved behavior |
| --- | --- |
| Event name | Extend the existing authoritative `capiss_mint_decision` event. Do not create a demo-only event. |
| Uniformity | Upgrade all capiss mint decision events uniformly, not only M5 Jira MCP paths. |
| Both outcomes | Emit complete records for both minted and denied requests. |
| Subject | Include `subject_spiffe_id` wherever known. |
| Correlation | Include `correlation_id` when provided by callers. Absence is allowed. |
| Generic fields | Keep generic fields top-level: result, reason, subject, audience, action, resource, token ids, policy, timing. |
| Resource-specific fields | Keep resource-specific derived attributes under `resource_attrs`; do not add Jira-specific top-level fields such as `project_key`. |
| Scope display | Keep `resource_attrs` in JSONL. Hide it in default human output unless verbose mode is explicitly requested, because scope duplicates resource for the current capiss-only demo. |
| Capiss only | This slice audits capiss mint decisions only. Gateway or database/confluence access logs are out of scope. |

### Time Semantics
| Decision | Approved behavior |
| --- | --- |
| Local time | Human-readable audit output must show local time first. |
| UTC time | JSONL must also include UTC timestamps for unambiguous machine evidence. |
| Timezone default | `varambu start` should auto-detect host timezone. Recommended default is host local timezone when detectable, otherwise UTC. |
| Timezone override | `varambu start --timezone ZONE` explicitly sets the local display timezone. |
| Invalid timezone | Invalid or unavailable timezone falls back to UTC rather than failing audit emission. |
| Logged time | `timestamp_local` and `timestamp_utc` mean audit event emission time. |
| Issued time | For minted requests, `issued_at_*` means the exact token validity start time. |
| Expiry time | For minted requests, `expires_at_*` means token expiry time. |
| TTL | For minted requests, `ttl_seconds` is computed as `expires_at - issued_at`. |
| Denied validity | Denied requests must not include `issued_at_*`, `expires_at_*`, or `ttl_seconds` because no token was issued. |

### Secret Handling
| Decision | Approved behavior |
| --- | --- |
| No bearer token values | Do not log bearer capability token values in capiss stdout or Varambu artifacts. |
| No upstream secrets | Do not log Jira API tokens, Basic auth values, cookies, or other secret-bearing fields. |
| Token IDs allowed | Token IDs such as `token_id`, `root_token_id`, and `parent_token_id` are allowed because they are identifiers, not bearer values. |
| Tailer allowlist | The tailer must use an allowlist for persisted fields and must drop unknown or forbidden fields. |
| Forbidden content | If a field value contains bearer/basic secret markers, it must be dropped rather than persisted. |

## Requirements Intent For Next Approval Gate
The next phase should update authoritative requirements only after this plan is approved.

Planned requirement changes:

- Extend `REQ-M4-O2` so every `capiss_mint_decision` includes local/UTC decision time, optional correlation, safely derived resource attributes, minted-token validity fields, actual TTL, and secret-exclusion rules.
- Add `REQ-M5-VA1` for Varambu session audit artifacts and command-line display.
- Confirm whether `REQ-M5-CJ10` should explicitly reference correlated capiss audit evidence for M5 allow/deny demo paths.

## Architecture Intent For Next Approval Gate
The next phase should update authoritative architecture only after this plan is approved.

Planned architecture changes:

- Extend `ARCH-012` for enriched capiss mint-decision audit events.
- Add `ARCH-032` or equivalent Varambu demo audit session component/logical section covering:
  - current session pointer,
  - active tailer,
  - persisted JSONL/human audit files,
  - timezone propagation,
  - tailer liveness warning,
  - no new authorization state.

## README Intent For Next Approval Gate
README changes are not part of this Phase 1 edit.

Planned README changes after approval:

- Document the operator demo flow in concise form:
  - `varambu start --mock`
  - perform MCP read/create requests,
  - `varambu audit`
  - `varambu audit-file`
- Keep detailed design and traceability in the slice docs, not in README.

## Hidden-State and Trust Decisions
| State | Store/System | Writer | Reader | TTL or Lifecycle | Decision Impact | Classification |
| --- | --- | --- | --- | --- | --- | --- |
| Current Varambu session pointer | `artifacts/varambu-demo/current` symlink | `varambu start` | `varambu audit`, `varambu audit-file` | Replaced on successful start | Selects default audit files | Evidence metadata |
| Audit tailer PID | `artifacts/varambu-demo/<session>/audit_tailer.pid` | `varambu start` | `varambu audit`, operator | Session lifecycle | Warns if audit files may be stale | Advisory |
| Varambu audit JSONL | `artifacts/varambu-demo/<session>/capiss_audit.jsonl` | Audit tailer | operator/tests | Append-only for session | Structured evidence copied from capiss stdout | Evidence copy |
| Varambu human audit log | `artifacts/varambu-demo/<session>/capiss_audit.log` | Audit tailer | operator/tests | Append-only for session | Human-readable evidence copied from capiss stdout | Evidence copy |
| Tailer diagnostics | `artifacts/varambu-demo/<session>/audit_tailer.err` | Audit tailer | operator/tests | Session lifecycle | Debug only | Diagnostics |
| Audit timezone | `VARAMBU_TZ` environment | `varambu start` | `capiss` | Runtime config | Formats local display timestamps only | Evidence metadata |

No new authorization state is introduced. No hidden state may influence allow/deny decisions.

## In Scope
- Slice docs for the approved design.
- Later, after approval:
  - requirements, architecture, README, and trace updates;
  - tests-first UT and E2E;
  - implementation of capiss event enrichment and Varambu audit CLI/session behavior.

## Out of Scope
- New authoritative audit database.
- Web UI or dashboard.
- Gateway, Confluence, database, or Jira-tool protected-use audit display in `varambu audit`.
- Token cache, token replay, or authorization semantics changes.
- Dedupe across sessions.
- Formal ASIL-D certification claims.

## Retirement and Compatibility
- Retain `start_Varambu` as a compatibility wrapper.
- Retain existing `capiss_mint_decision` event name and extend it.
- Remove or avoid stale compatibility paths only when explicitly approved in Phase 3.

## Approval Gates
This slice requires explicit approval at each gate:

1. Approve this Phase 1 plan and test plan.
2. Approve requirements, architecture, README, and trace updates.
3. Approve Phase 2 tests and capture the failing baseline before implementation.
4. Approve Phase 3 implementation changes.
5. Complete Phase 4 verification and record status.
