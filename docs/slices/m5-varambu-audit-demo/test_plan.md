# M5 Varambu Audit Demo Test Plan

## Phase Status
This test plan is part of `Phase 1: plan and review`.

No tests from this plan are accepted until the plan is approved. Any tests already present in the current working tree are part of the untrusted spike and must be reviewed, rewritten, or deliberately reused during Phase 2 only after approval.

## Test Strategy
Requirements are covered by black-box E2E tests. Detailed design is covered by UTs.

For this slice, UTs must cover decision branches and edge cases with the same rigor used in the previous safety-focused slices:

- allow and deny outcomes;
- missing, malformed, and optional inputs;
- boundary conditions for time, timezone, and TTL;
- secret-bearing field rejection;
- file append and empty-file behavior;
- tailer liveness/startup failure behavior;
- current-session and history selection behavior;
- no runtime-significant behavior existing only in code.

## Planned Requirements Coverage
One E2E case is not sufficient for this slice. `M5-T42` is only the main demo story. Requirement-level proof must be split across a focused E2E matrix so edge conditions are visible and independently diagnosable.

| Requirement intent | Planned E2E coverage |
| --- | --- |
| Enriched minted records include subject, action/resource/audience, result/reason, token identifiers, policy metadata, issued/expires/logged local and UTC time, and actual TTL | `M5-T42`, `M5-T47` |
| Denied records are present in the same audit view and omit issued-token validity fields | `M5-T42`, `M5-T47` |
| Both read and create M5 Jira MCP requests produce capiss audit evidence for allowed IAM and denied NAS decisions | `M5-T42` |
| New mint or deny requests append at the end of current-session files while the active tailer runs, without a post-processing step in `varambu audit` | `M5-T43` |
| `varambu audit` defaults to current session and reads persisted files instead of Docker logs | `M5-T43`, `M5-T44` |
| `varambu audit --all` shows historical sessions without dedupe | `M5-T44` |
| `varambu audit-file` exposes directly viewable JSONL and human log paths | `M5-T44` |
| Audit artifacts and CLI output contain no bearer token values, Basic auth, Jira API token material, cookies, or forbidden secret-bearing fields | `M5-T45` |
| Tailer liveness loss is visible to the operator; strict mode fails instead of silently presenting stale evidence | `M5-T46` |
| Local timezone selection and UTC fallback are observable in persisted audit records | `M5-T47` |
| Capiss audit enrichment applies uniformly to root mint and resource mint decisions, not only the M5 Jira MCP path | `M5-T48` |

## Planned Detailed Design UT Coverage

### Capiss Audit Event Schema
| Design decision | Planned UT coverage |
| --- | --- |
| Allow root mint emits one final allow decision with issued/expires/logged UTC and local time, actual TTL, token/root IDs, subject, resource attrs, optional correlation, policy metadata, and no bearer token value | New capiss UT |
| Allow resource mint emits one final allow decision with parent/root/depth context and minted-token validity fields | New or extended capiss UT |
| Denied root mint emits one final deny decision with subject/context where known and no issued/expires/TTL fields | New or extended capiss UT |
| Denied resource mint emits one final deny decision with parent/root/depth context when parsed and no issued/expires/TTL fields | New or extended capiss UT |
| Missing SPIFFE ID, invalid SPIFFE ID, bad payload, non-canonical resource, OPA deny, OPA unavailable, Redis unavailable, invalid parent token, missing bearer, blank bearer, registry miss, registry unavailable, mint-rate deny, marker-store failure all produce final audit decisions | Branch-complete capiss endpoint UTs |
| `issued_at` is the exact time used to compute expiry, and `ttl_seconds == expires_at - issued_at` | New capiss time UT |
| Invalid configured timezone falls back to UTC | New capiss timezone UT |
| Resource-specific fields are under `resource_attrs`, with no top-level Jira-only `project_key` | New capiss resource-attrs UT |
| Optional correlation header is included only when non-empty | New capiss correlation UT |

### Varambu Audit Normalizer And Renderer
| Design decision | Planned UT coverage |
| --- | --- |
| Normalizer accepts only `capiss_mint_decision` and ignores unrelated stdout events | New audit helper UT |
| Normalizer keeps only approved fields, adds session sequence, and drops unknown fields | New audit helper UT |
| Normalizer drops forbidden field names such as `token`, `Authorization`, cookies, and upstream secret fields | New audit helper UT |
| Normalizer drops values containing bearer/basic secret markers | New audit helper UT |
| Human renderer prints local time first and renders fields in stable demo order | New audit helper UT |
| Human renderer hides `resource_attrs` by default and shows it only in verbose mode | New audit helper UT |
| Human renderer prints denied records with dash placeholders for token validity | New audit helper UT |
| JSONL output preserves structured fields including `resource_attrs` | New audit helper UT |

### Varambu CLI And Session Behavior
| Design decision | Planned UT or E2E coverage |
| --- | --- |
| `varambu start` creates a new session directory and updates `current` only for the new session | E2E or shell-level test |
| `start_Varambu` delegates to `varambu start` | Shell-level test |
| Safe symlink creation updates `$HOME/.local/bin/varambu` only when safe and warns on existing non-symlink | Shell-level test |
| `varambu audit` defaults to current session | Shell-level test |
| `varambu audit --all` reads history without dedupe | Shell-level test |
| `varambu audit --json` prints persisted JSONL | E2E and shell-level test |
| `varambu audit --follow` follows the persisted current-session file and does not call Docker | Shell-level test |
| `varambu audit-file` prints JSON and human file paths | Shell-level test |
| Dead tailer PID causes a warning, or strict failure when strict mode is selected | Shell-level test |

### Tailer Behavior
| Design decision | Planned UT or E2E coverage |
| --- | --- |
| Tailer command uses `docker logs --since <session-start-utc> --follow spiffe-capability-issuer` | New audit helper UT |
| Tailer appends normalized JSONL and human records in observed order | New audit helper UT |
| Tailer ignores invalid JSON and non-mint-decision events | New audit helper UT |
| Tailer copies diagnostics to `audit_tailer.err` | New audit helper UT |
| Tailer startup retries up to 3 times and fails `varambu start` if no process survives the 2 second health window | Shell-level or E2E failure-injection test |
| No dedupe is performed | E2E append-order assertion |

## Planned E2E Cases

### M5-T42: Varambu capiss audit files
Premise:
- The M5 MCP path is ready in deterministic mock mode.
- A Varambu-style session directory and current pointer are prepared.
- A real audit tailer follows `spiffe-capability-issuer` logs from the session start UTC timestamp.

Exercise:
- Call `read_project_summary` for `IAM`.
- Call `create_story` for `IAM`.
- Call `read_project_summary` for `NAS`.
- Call `create_story` for `NAS`.
- Render persisted audit JSON through `varambu audit --json`.
- Resolve audit paths through `varambu audit-file`.

Outcome:
- JSONL contains minted and denied entries in append order.
- Minted entries include subject, token IDs, issued/expires/logged local and UTC fields, actual TTL, correlation when available, and policy metadata.
- Denied entries include subject/context and reason while omitting issued/expires/TTL.
- Resource-specific attributes, when present, are under `resource_attrs`.
- JSONL, human log, CLI output, tailer diagnostics, and copied evidence contain no bearer token values or upstream secrets.
- Human log is readable and contains `MINTED`, `DENIED`, and `Logged At`.

Required evidence artifacts:
- `capiss_audit.jsonl`
- `capiss_audit.log`
- `audit_tailer.err`
- `varambu_audit_json.out`
- `varambu_audit_file.out`
- MCP request/response files for IAM and NAS calls

### M5-T43: Active append without audit post-processing
Premise:
- A current Varambu session exists with an active audit tailer.
- The audit files are initially empty or have a known record count.

Exercise:
- Run one allowed mint request.
- Read `capiss_audit.jsonl` directly and record its line count.
- Run `varambu audit --json` and confirm it prints the same persisted content.
- Run a denied mint request.
- Read `capiss_audit.jsonl` directly again.

Outcome:
- The second request appears at the end of `capiss_audit.jsonl` before any second `varambu audit` processing step.
- `varambu audit --json` does not call Docker and does not synthesize missing entries.
- Event order matches request order.

### M5-T44: Current session, history, and direct file access
Premise:
- Two Varambu-style sessions exist, each with distinct audit records.
- `artifacts/varambu-demo/current` points to the second session.

Exercise:
- Run `varambu audit`.
- Run `varambu audit --all`.
- Run `varambu audit-file`.
- Run `varambu audit-file --all`.

Outcome:
- Default audit output shows only the current session.
- `--all` shows both sessions in session order.
- No dedupe is attempted across sessions.
- `audit-file` outputs paths that exist and can be read directly.

### M5-T45: Secret exclusion in persisted audit evidence
Premise:
- Capiss emits mint-decision logs for allowed and denied paths.
- At least one source event or fixture includes forbidden fields or forbidden-looking values, such as `token`, `Authorization`, `Bearer `, `Basic `, cookies, or Jira API token names.

Exercise:
- Run the audit tailer.
- Inspect `capiss_audit.jsonl`, `capiss_audit.log`, `audit_tailer.err`, and CLI output.

Outcome:
- Bearer token values are absent.
- Basic auth values are absent.
- Jira API token material is absent.
- Cookie values are absent.
- Token identifiers such as `token_id`, `root_token_id`, and `parent_token_id` may remain.

### M5-T46: Tailer liveness and stale-evidence warning
Premise:
- A current session exists with an audit tailer PID file.

Exercise:
- Stop or replace the tailer process so the PID check fails.
- Run `varambu audit`.
- Run `varambu audit --strict`.

Outcome:
- Non-strict audit warns that the audit tailer is not running and still prints existing persisted evidence.
- Strict audit fails so stale evidence cannot be presented as fresh proof.

### M5-T47: Local and UTC timing semantics
Premise:
- A current session starts with an explicit timezone override.
- A separate run or fixture covers invalid timezone fallback.

Exercise:
- Mint an allowed token.
- Produce a denied request.
- Read persisted JSONL and human logs.

Outcome:
- Minted records include `issued_at_local`, `issued_at_utc`, `expires_at_local`, `expires_at_utc`, `timestamp_local`, `timestamp_utc`, `timezone`, and `ttl_seconds`.
- `ttl_seconds` equals `expires_at - issued_at`.
- Denied records include logged timestamps and timezone but omit issued/expires/TTL.
- Human output shows local time first.
- Invalid timezone falls back to UTC instead of failing audit emission.

### M5-T48: Uniform capiss mint-decision enrichment
Premise:
- The stack can exercise more than one capiss mint path.

Exercise:
- Perform an M5 Jira MCP root mint path.
- Perform an existing non-M5 root mint path, such as Tool-B root mint.
- Perform a resource mint path when a parent token is available.
- Produce representative denials for root and resource mint.

Outcome:
- All `capiss_mint_decision` records use the same enriched audit schema.
- Resource mint records include parent/root/depth context when available.
- Denied records remain complete but omit token-validity fields.
- No path logs bearer token values.

## Failing Baseline Requirement
After this test plan is approved and before implementation:

1. Add the planned UT and E2E tests.
2. Run the targeted UTs and targeted E2E if Docker is available.
3. Record the failing baseline.
4. Only then begin Phase 3 implementation.

If a test requires a new assumption or an unapproved behavior, stop and update this slice bundle before implementing.

## Planned Verification Commands
Phase 2 failing baseline:

```bash
pytest -q tests/unit/capiss tests/unit/test_varambu_audit.py
make unit-guard-check
docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M5-T42,M5-T43,M5-T44,M5-T45,M5-T46,M5-T47,M5-T48 rogue-tests
```

Phase 4 final verification:

```bash
make unit-trust
make qa-trace
make qa-quality
docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M5-T42 rogue-tests
docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M5-T43,M5-T44,M5-T45,M5-T46,M5-T47,M5-T48 rogue-tests
make qa-evidence
```

Docker-backed E2E may be blocked when the local process cannot access `/var/run/docker.sock`; if blocked, record the exact environment error instead of claiming E2E completion.

## Approval Gates
- Phase 1 approval: this plan and `plan.md`.
- Authoritative docs approval: requirements, architecture, README, and trace updates.
- Phase 2 approval: tests and failing baseline.
- Phase 3 approval: implementation.
- Phase 4 closure: canonical verification and status capture.
