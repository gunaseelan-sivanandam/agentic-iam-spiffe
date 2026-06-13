# M5 Codex Jira MCP Slice 1 Plan

## Goal
Prototype real-world Jira use through MCP while preserving the repo's capability and boundary model. Codex on WSL is an untrusted agent. It talks to a real MCP adapter, never receives Jira API credentials, never receives capiss bearer tokens, and never talks to Jira directly. The SPIFFE-resident adapter obtains narrow capiss tokens per MCP tool call and sends them through a Jira MCP Envoy boundary to a protected gateway. The gateway is the request-time PEP and is the only M5 component allowed to call the Jira upstream or the deterministic Jira MCP mock.

Slice 1 proves two useful Jira operations for the allowed `IAM` project:
- bounded project summary read
- story creation with optional same-project epic link

The larger direction is powerful Codex-assisted Jira work through MCP, but this slice proves the first controls before adding broader Jira actions.

## Grill-Me Review Summary
- Codex on WSL is untrusted input. It is not given Jira API keys, capiss tokens, direct Jira URLs, or direct access to Jira Cloud.
- The Codex-facing component is a real MCP server named `codex-jira-mcp-adapter`.
- `codex-jira-mcp-adapter` is a SPIFFE workload and is the only M5 subject allowed to mint Slice 1 MCP Jira tokens.
- The adapter is not the PDP or PEP. It performs MCP translation and minimal schema/type validation only.
- `capiss` is the mint-time authority gate. It permits only explicitly allowed M5 authority tuples.
- `jira-mcp-gateway` is the request-time PEP. It verifies capiss tokens, Envoy-verified caller identity, audience, action, resource, project, payload shape, optional epic, budget/rate, and only then calls upstream.
- `jira-mcp-gateway` has its own Envoy boundary, `jira-mcp-envoy`.
- The adapter calls `capability-issuer-envoy` and `jira-mcp-envoy`; it does not call protected app services directly.
- The existing M4a/M4b `jira-tool`, `jira-tool-envoy`, Jira demo, and policy branch remain untouched.
- M5 uses a new authority family: `aud=jira-mcp-gateway`, `res=jira-mcp:/project:<KEY>`.
- Slice 1 uses two actions: `read_project_summary` and `create_story`.
- The concrete allowed project is `IAM`. `NAS` is the concrete non-allowed proof project and is denied by default because it is not listed in policy.
- Each MCP tool maps to exactly one capiss action. Codex chooses an MCP tool, not a free-form token action.
- Each MCP tool call mints a fresh capiss token. There is no adapter token cache.
- The local MCP launcher starts one adapter MCP process per Codex MCP server session. A single session can contain many MCP tool calls.
- The Docker/SPIFFE stack stays running outside the MCP session. When the MCP session ends, the adapter process exits and the stack remains running.
- The local launcher uses `docker compose exec -T` into the already-running adapter container and must not print protocol-corrupting output to stdout.
- The adapter has no inbound Envoy in Slice 1 because Codex reaches it through local stdio MCP.
- The adapter calls the gateway with internal HTTPS/JSON through `jira-mcp-envoy`; the gateway itself is not MCP-native in Slice 1.
- A future slice may make the gateway MCP-native if that becomes useful, but Slice 1 keeps the gateway as a protected HTTP enforcement service.
- `jira-mcp-mock` is separate from the existing M4a/M4b `jira-mock`. It models upstream Jira Cloud for M5 and is called only by `jira-mcp-gateway`.
- Deterministic proof defaults to mock mode. Live Jira smoke is explicit opt-in only.

## Requirements
- M5 shall keep Codex separated from Jira API credentials. Codex-visible MCP requests, responses, logs, and evidence shall not contain Jira API keys.
- M5 shall keep Codex separated from capiss bearer tokens. Tokens are adapter-internal and shall not be returned through MCP responses, launcher output, normal logs, or evidence.
- M5 shall use a real MCP server at the Codex-facing boundary.
- M5 shall treat `codex-jira-mcp-adapter` as an untrusted-request translator, not as an authorization decision point.
- M5 shall require `codex-jira-mcp-adapter` to mint tokens through `capability-issuer-envoy`.
- M5 shall require `codex-jira-mcp-adapter` to call `jira-mcp-gateway` through `jira-mcp-envoy`.
- M5 shall require `jira-mcp-gateway` to verify both the capiss token and the Envoy-verified caller identity.
- M5 shall deny when token `subject_spiffe_id` does not match the Envoy-verified caller identity.
- M5 shall add a distinct capiss policy branch for `aud=jira-mcp-gateway`, `res=jira-mcp:/project:<KEY>`, and the Slice 1 actions.
- M5 shall allow only `spiffe://varambu.org/codex-jira-mcp-adapter` to mint Slice 1 tokens.
- M5 shall allow only `res=jira-mcp:/project:IAM` for Slice 1.
- M5 shall deny `jira-mcp:/project:NAS` at capiss mint time.
- M5 shall enforce strict project-key syntax for `jira-mcp:/project:<KEY>` and request `project_key`. No wildcards, lists, aliases, lowercase normalization, URLs, spaces, or slashes are allowed.
- M5 shall expose only two Codex-facing MCP tools in Slice 1: `read_project_summary` and `create_story`.
- `read_project_summary` shall map only to `act=read_project_summary`.
- `create_story` shall map only to `act=create_story`.
- `jira-mcp-gateway` shall bind expected action to the internal endpoint, not to adapter-supplied MCP metadata.
- `read_project_summary` shall return bounded metadata for the requested allowed project.
- `read_project_summary` shall not return issue descriptions, comments, assignees, sprint data, board data, raw JQL, arbitrary search results, raw Jira URLs, Jira credentials, or capiss tokens.
- `create_story` shall accept only `project_key`, `summary`, `description`, optional `acceptance_criteria`, and optional `epic_key`.
- `create_story` shall not accept assignee, sprint, priority, labels, components, custom fields, raw Jira `fields`, raw Jira ADF, status transitions, comments, attachments, arbitrary issue links, or raw Jira REST payloads.
- `create_story` shall set issue type to `Story` internally.
- `create_story` shall accept plain text only. The gateway converts plain text to Jira ADF mechanically.
- `acceptance_criteria` shall be optional and stored in the generated description body when supplied.
- Slice 1 shall not enforce story-quality rules. It may enforce defensive type and length bounds.
- `epic_key` shall be optional. If supplied, it must use strict `<PROJECT>-<NUMBER>` syntax, must match the token project, and must be verified by the gateway as an existing same-project Epic before story creation.
- Invalid or cross-project `epic_key` shall fail closed and shall not create an unlinked story.
- `jira-mcp-gateway` shall consume existing M4 budget/rate governance before upstream summary reads and story creation.
- Pre-authorization and pre-validation denials shall not consume budget.
- If upstream story creation fails after budget is consumed, Slice 1 shall not refund budget.
- The adapter shall not retry read or create operations automatically.
- Slice 1 shall return standardized local error responses to Codex for authorization, validation, budget, rate, gateway, and upstream failures.
- Authorization denials shall not reveal whether a non-allowed Jira project or issue exists upstream.
- Slice 1 shall emit correlated adapter, capiss, gateway, and mock/live evidence using a correlation ID.

## Success Criteria
- Codex can start a local MCP session through the launcher and see exactly the approved Slice 1 MCP tools.
- Codex can request `read_project_summary` for `IAM` and receive only bounded project, issue, and epic metadata.
- Codex can request `create_story` for `IAM` and receive only bounded creation metadata.
- Codex can optionally include an `IAM-*` epic key, and the gateway verifies it before creating and linking the story.
- Codex cannot read or create in `NAS`.
- Codex cannot use MCP inputs to cause arbitrary Jira operations, arbitrary fields, JQL/search, issue descriptions, comments, assignment, sprint actions, or raw Jira payloads.
- Capiss denies unauthorized M5 mint attempts for `NAS`, unsupported actions, wrong subjects, wrong audiences, and malformed resources.
- The gateway denies wrong action, wrong audience, wrong resource, wrong project, wrong subject, expired/invalid token, arbitrary fields, cross-project epics, invalid epics, budget exhaustion, and rate limiting before upstream use when applicable.
- Only `jira-mcp-gateway` calls `jira-mcp-mock` or live Jira upstream.
- Codex-visible outputs and evidence contain no Jira API keys and no capiss bearer tokens.
- Existing M4a/M4b Jira demo components and behavior remain undisturbed.

## In Scope
- Add `docs/slices/m5-codex-jira-mcp-slice-1/plan.md` and `test_plan.md`.
- Add M5 requirements and architecture sections for Codex Jira MCP Slice 1.
- Add trace mappings for M5 E2E proof.
- Add `codex-jira-mcp-adapter` as a new Python service/container that runs a real MCP stdio server process.
- Add a local launcher script for Codex MCP config that uses `docker compose exec -T` into the adapter container.
- Add checked-in Codex MCP config documentation or example without secrets.
- Add `jira-mcp-envoy` as the M5 gateway boundary.
- Add `jira-mcp-gateway` as a separate protected Python HTTP service.
- Add `jira-mcp-mock` as a separate deterministic upstream mock for M5.
- Extend capiss resource canonicalization and policy for the M5 authority family.
- Add SPIRE workload entries and compose topology needed for the new adapter, gateway, Envoy, and mock.
- Add deterministic E2E tests for the full reasonable Slice 1 behavior set in `test_plan.md`.
- Add unit tests for adapter, capiss/policy, gateway, and mock behavior in `test_plan.md`.
- Reuse existing shared token verification and M4 governance helpers where they fit cleanly.
- Reuse existing M4 budget/rate governance state for gateway enforcement.
- Add optional live smoke for the same Slice 1 controls when live Jira credentials/config are explicitly provided.

## Out of Scope
- Giving Codex a Jira API key.
- Giving Codex capiss bearer tokens.
- Codex calling Jira Cloud directly.
- Codex calling capiss or `jira-mcp-gateway` directly outside the MCP adapter path.
- Reusing or disturbing the existing `jira-tool`, `jira-tool-envoy`, M4a/M4b demo scripts, or existing Jira policy branch.
- Making `jira-mcp-gateway` MCP-native in Slice 1.
- Exposing `codex-jira-mcp-adapter` as a shared host HTTP service.
- Adding an inbound Envoy for the stdio MCP adapter.
- Per-human or per-user identity.
- Remote MCP clients or multi-user adapter authorization.
- Adapter token caching.
- Long-running adapter MCP daemon multiplexing stdio sessions.
- Automatic retries for reads or mutations.
- Dry-run or preview story creation.
- Idempotency keys or duplicate-create suppression.
- Story quality enforcement.
- Raw JQL or search.
- Reading full issue descriptions.
- Reading comments.
- Reading assignees, boards, or sprints.
- Creating or updating comments.
- Updating existing stories.
- Creating epics.
- Creating subtasks.
- Creating bug tickets.
- Assigning issues to people.
- Moving issues to sprints.
- Creating sprints.
- Setting priority, labels, components, custom fields, or status transitions.
- Arbitrary Jira REST gateway behavior.
- Generic Jira gateway/plugin framework.
- Refund logic for upstream failures after budget consumption.

## Deferred Future Slices
- `read_issue_details`: read selected `IAM-*` issue descriptions with a distinct capiss action and bounded response.
- `search_issues`: controlled Jira search or JQL replacement for `IAM`, with its own action, query limits, and response bounds.
- `update_story`: edit approved story fields only, with field-level allowlisting and audit proof.
- `comment`: add comments to allowed `IAM` issues.
- `create_epic`: create epics in `IAM`.
- `link_story_to_epic`: link existing stories to same-project epics.
- `create_subtask`: create subtasks only under allowed same-project parent issues.
- `create_bug`: create bug tickets in `IAM`.
- `assign_issue`: assign issues only to allowed users or groups.
- `sprint_assignment`: move issues into allowed existing sprints.
- `create_sprint`: create sprints only on allowed boards.
- MCP-native protected gateway if internal HTTPS/JSON becomes a limitation.
- Adapter daemon/session optimization if per-session process startup becomes too expensive.
- Per-user identity and human authorization.

## Architecture Model
### Runtime Components
- `Codex on WSL`: untrusted MCP client. It provides Jira work requests and story content but receives no Jira API credential and no capiss token.
- `codex-jira-mcp-launcher`: local script used by Codex MCP config. It connects Codex stdio to the adapter process inside the already-running container with `docker compose exec -T`.
- `codex-jira-mcp-adapter`: SPIFFE workload and real MCP stdio server. It exposes `read_project_summary` and `create_story`, maps each tool to a fixed capiss action, obtains a fresh capiss token per MCP call, and forwards HTTPS/JSON requests to `jira-mcp-envoy`.
- `capability-issuer-envoy`: existing capiss boundary used for all M5 token minting.
- `capiss`: existing capability issuer extended with the M5 authority family.
- `jira-mcp-envoy`: new M5 gateway boundary. It terminates mTLS, verifies caller identity, injects trusted identity headers, and forwards to `jira-mcp-gateway`.
- `jira-mcp-gateway`: protected M5 PEP and Jira client. It verifies the capiss token and Envoy caller identity, enforces endpoint-bound action and resource scope, validates payloads, consumes budget/rate, and calls upstream only after all gates pass.
- `jira-mcp-mock`: deterministic mock of upstream Jira Cloud for M5 tests. It includes broad `IAM` and `NAS` data and request logs but is reachable only from `jira-mcp-gateway` and test harness paths.
- Jira Cloud: optional live upstream used only when live smoke credentials/config are explicitly provided.

### Request Flow
1. Codex starts an MCP server session by running the local launcher command from its MCP config.
2. The launcher checks that the Docker/SPIFFE stack is already running.
3. The launcher runs `docker compose exec -T codex-jira-mcp-adapter <adapter-mcp-command>`.
4. The adapter MCP process starts inside the adapter container and speaks stdio MCP with Codex.
5. Codex calls `read_project_summary` or `create_story`.
6. The adapter performs minimal type/schema validation and derives the fixed capiss action for the selected MCP tool.
7. The adapter calls `capability-issuer-envoy` over mTLS and requests a fresh token for the requested action and `jira-mcp:/project:<project_key>`.
8. Capiss allows only the configured M5 authority tuple for `spiffe://varambu.org/codex-jira-mcp-adapter`; otherwise it denies.
9. The adapter sends an internal HTTPS/JSON request through `jira-mcp-envoy` with the capiss token.
10. `jira-mcp-gateway` verifies token signature, expiry, subject, audience, endpoint-bound action, resource, project, and Envoy caller identity.
11. The gateway validates allowed payload fields and defensive type/length bounds.
12. If `epic_key` is supplied, the gateway verifies same-project syntax and upstream epic type before story creation.
13. The gateway consumes budget/rate immediately before upstream summary use or story creation.
14. The gateway calls `jira-mcp-mock` or Jira Cloud only after all gates pass.
15. The gateway returns bounded success metadata or standardized local errors.
16. The adapter returns the MCP response to Codex without exposing bearer tokens or Jira credentials.
17. When the Codex MCP server session ends, the adapter process exits; the Docker/SPIFFE stack remains running.

### Gateway Enforcement Order
For both endpoints:
1. Parse route/body only enough to process the request.
2. Verify capiss token signature and required token fields.
3. Verify token subject matches Envoy-verified caller identity.
4. Verify `aud=jira-mcp-gateway`.
5. Verify endpoint-bound action:
   - `POST /mcp/jira/project-summary` requires `act=read_project_summary`
   - `POST /mcp/jira/stories` requires `act=create_story`
6. Verify `res=jira-mcp:/project:<KEY>` and strict project syntax.
7. Enforce payload project matches token project.
8. Validate allowed payload fields and defensive bounds.
9. Verify optional same-project epic for `create_story`.
10. Consume budget/rate immediately before upstream use.
11. Call upstream mock/live Jira.
12. Emit final gateway decision event.

### MCP Tool Contracts
#### `read_project_summary`
Request:
```json
{
  "project_key": "IAM"
}
```

Response:
```json
{
  "project": {
    "key": "IAM",
    "name": "...",
    "issue_count": 123
  },
  "issues": [
    {
      "key": "IAM-123",
      "summary": "...",
      "status": "...",
      "issue_type": "Story",
      "epic_key": "IAM-10"
    }
  ],
  "epics": [
    {
      "key": "IAM-10",
      "summary": "...",
      "status": "..."
    }
  ]
}
```

Bounds:
- latest 50 non-epic issues across statuses
- latest 25 epics across statuses
- server-controlled ordering
- no descriptions, comments, assignees, sprints, boards, raw JQL, or raw search

#### `create_story`
Request:
```json
{
  "project_key": "IAM",
  "summary": "...",
  "description": "...",
  "acceptance_criteria": ["..."],
  "epic_key": "IAM-123"
}
```

Required fields:
- `project_key`
- `summary`
- `description`

Optional fields:
- `acceptance_criteria`
- `epic_key`

Success response:
```json
{
  "key": "IAM-456",
  "self": "...",
  "project_key": "IAM",
  "issue_type": "Story",
  "epic_key": "IAM-123"
}
```

Rules:
- issue type is always `Story`
- `summary` and `description` are plain text
- `acceptance_criteria` is optional plain text and is folded into the generated description body
- Jira ADF conversion is mechanical and gateway-owned
- no raw ADF from Codex
- no semantic rewriting by adapter or gateway
- invalid `epic_key` means no story is created

### Standard Error Contract
Authorization, validation, and upstream failures return standardized local errors:
```json
{
  "ok": false,
  "reason": "project_mismatch",
  "correlation_id": "..."
}
```

Allowed reason families:
- `mint_denied`
- `token_invalid`
- `subject_mismatch`
- `aud_mismatch`
- `act_mismatch`
- `project_mismatch`
- `payload_invalid`
- `epic_invalid`
- `budget_exhausted`
- `rate_limited`
- `gateway_unavailable`
- `upstream_error`

Raw Jira authorization or validation errors are normalized before returning to Codex.

## Hidden-State and Trust Decisions
| State / Secret / Input | Store / System | Writer | Reader | TTL / Lifecycle | Decision impact | Type |
|---|---|---|---|---|---|---|
| M5 allowed project/action policy | OPA policy/data | repo/operator config | capiss via OPA | deployment lifecycle | Determines whether adapter may mint `read_project_summary` or `create_story` for `IAM` | Authoritative |
| M5 capiss token | adapter process memory | capiss | adapter, gateway | short token TTL; one token per MCP call | Grants exactly one narrow action/resource authority for gateway use | Authoritative secret |
| Capiss signing public key | mounted file | capiss key setup | gateway | key lifecycle | Verifies token authenticity before upstream Jira use | Authoritative |
| Envoy verified caller identity | `jira-mcp-envoy` trusted header | Envoy | gateway | request lifecycle | Must match token subject before gateway uses upstream | Authoritative |
| `m4:budget:<root_token_id>` and request-rate state | Redis | capiss initializes; gateway consumes | gateway | bounded by root token expiry/rate window | Denies MCP Jira use when budget/rate is exhausted or unavailable | Authoritative |
| Jira API credential | gateway live environment only | operator/live setup | gateway | live runtime secret lifecycle | Enables live Jira upstream calls after local enforcement | Sensitive secret |
| MCP session process | adapter container process | local launcher | Codex over stdio | one Codex MCP server session | Carries MCP messages but no reusable authorization state | Runtime transport |
| Correlation ID | adapter/gateway logs and request headers | adapter or gateway | adapter, capiss, gateway, tests | request lifecycle | Ties MCP request, mint decision, enforcement decision, and upstream evidence | Evidence metadata |
| `jira-mcp-mock` request log | mock memory | mock | test harness | test lifecycle/reset per test | Proves upstream was or was not called | Test evidence |

## Credential Boundaries
- Codex receives no Jira API key.
- Codex receives no capiss bearer token.
- The local launcher receives no Jira API key.
- The adapter receives no Jira API key.
- Capiss receives no Jira API key.
- Envoys receive no Jira API key except whatever transport material they need for SPIFFE/mTLS.
- Only `jira-mcp-gateway` receives the live Jira API credential.
- In mock mode, no real Jira credential is configured anywhere.
- Client-supplied `Authorization`, Jira auth, or impersonation headers are stripped or ignored before upstream calls.
- Evidence may include token metadata such as `aud`, `act`, `res`, `token_id`, `root_token_id`, decisions, reasons, and correlation IDs, but not bearer token strings.

## Authored Source Changes
- Requirements: add M5 Codex Jira MCP requirements to `docs/requirements.md`.
- Architecture: add M5 components, session model, trust boundaries, and hidden-state inventory to `docs/architecture.md`.
- Runtime proof: add M5 E2E suite and case mappings to `trace/tests.yaml`.
- Slice docs: keep this `plan.md` and `test_plan.md` as the Phase 1 review bundle.
- Operational docs: document the Codex MCP launcher/config path without secrets.
- Status: update `docs/local_status_capture/implementation_status.md` after implementation and verification.

## Retirement and Compatibility
- No existing runtime component is retired in Slice 1.
- Existing M4a/M4b Jira services, policies, mocks, tests, live smoke, and demo remain compatible.
- Existing `jira-tool:/project:IAM` resources and `jira-tool` audience are not reused for M5.
- Existing Jira mock is not reused for M5.
- No compatibility bridge is added from M5 to M4a/M4b.

## Review Notes
- The phrase "Codex can use Jira powerfully" is the product direction, not the Slice 1 implementation scope.
- Slice 1 intentionally proves only the first controlled read/write pair.
- The adapter is trusted only as a SPIFFE workload that can request allowed tokens; it is not trusted to authorize Jira use.
- Capiss and the gateway are the only authorization decision points for Slice 1.
- Mock-by-default is mandatory for deterministic proof. Live smoke is optional and explicit.
- Any future need for issue descriptions, search, updates, comments, epics, subtasks, bugs, assignees, or sprints must be added as a separate capability with its own action and tests.
