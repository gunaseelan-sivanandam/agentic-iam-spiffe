# M5 Codex Jira MCP Slice 1 Test Plan

## Goal
Prove that Codex can use a real MCP Jira adapter to read bounded project context and create Jira stories in the allowed `IAM` project, while Jira API credentials, capiss bearer tokens, direct Jira access, and non-allowed `NAS` authority remain unavailable to Codex. The tests must prove the full Slice 1 control chain: MCP launcher, adapter translation, capiss mint policy, Envoy boundaries, gateway enforcement, mock/live upstream use, budget/rate governance, and audit evidence.

This is not a minimum smoke plan. It is the full reasonable UT and E2E plan for the approved Slice 1 design in `plan.md`.

## Inputs
- Approved design: `docs/slices/m5-codex-jira-mcp-slice-1/plan.md`
- Existing requirements source: `docs/requirements.md`
- Existing architecture source: `docs/architecture.md`
- Existing E2E trace map: `trace/tests.yaml`
- Existing unit-test guard style: `tests/unit/AGENTS.md`
- Existing M4 governance model: capiss-issued tokens, Envoy-verified caller identity, subject binding, budget/rate state, audit evidence, and mock-by-default deterministic proof.

## Unit Test Plan
### Adapter Unit Tests
Adapter tests prove the MCP boundary and translation behavior without treating the adapter as PDP/PEP.

- MCP tool list exposes exactly `read_project_summary` and `create_story`.
- `read_project_summary` maps to exactly `act=read_project_summary`.
- `create_story` maps to exactly `act=create_story`.
- Adapter does not accept a free-form `act` value from Codex.
- Adapter passes requested `project_key` into capiss resource construction without project allowlist authorization.
- Adapter constructs `res=jira-mcp:/project:<KEY>` using the request project key and leaves authorization to capiss/gateway.
- Adapter performs only minimal schema/type validation needed to translate MCP requests.
- Adapter rejects malformed JSON or wrong primitive types as protocol errors, not as project authorization decisions.
- Adapter forwards `project_key=NAS` to capiss and reports capiss denial instead of denying locally.
- Adapter requests a fresh capiss token for every MCP tool call.
- Adapter does not cache capiss tokens across MCP calls.
- Adapter sends internal HTTPS/JSON requests to `jira-mcp-envoy`, not direct gateway app URLs.
- Adapter includes the capiss token only in the internal gateway request.
- Adapter never includes bearer token strings in MCP success responses.
- Adapter never includes bearer token strings in MCP error responses.
- Adapter never logs bearer token strings in normal output.
- Adapter never requires or reads Jira API credential environment variables.
- Adapter normalizes capiss mint failures into standardized MCP errors with `reason=mint_denied`.
- Adapter normalizes gateway failures without inventing its own authorization reason.
- Adapter propagates or creates a correlation ID for capiss and gateway calls.
- Adapter does not retry `read_project_summary` automatically.
- Adapter does not retry `create_story` automatically.
- Adapter sends diagnostics to stderr only when running under the launcher path.
- Adapter stdout remains MCP protocol clean.

Expected traceability:
- New UT blocks should cover M5 adapter design IDs for tool exposure, action mapping, no local authorization, token non-disclosure, no retries, and correlation propagation.

### Launcher Unit or Script Tests
Launcher tests prove the Codex-facing process behavior without starting the full stack when unit-level validation is enough.

- Launcher checks that the adapter container exists or is running before executing into it.
- Launcher uses `docker compose exec -T`.
- Launcher does not run `docker compose up`, rebuild images, or mutate stack lifecycle.
- Launcher passes stdio through to the adapter process.
- Launcher emits diagnostics to stderr only.
- Launcher does not include Jira credentials or capiss tokens in environment or output.
- Launcher fails clearly when the stack or adapter container is unavailable.

Expected traceability:
- Script-level checks may be shell syntax tests plus focused assertions if a shell-test harness is introduced.

### Capiss and Policy Unit Tests
Capiss/policy tests prove the new M5 authority family is distinct from M4a/M4b.

- Allows `spiffe://example.org/codex-jira-mcp-adapter` to mint `aud=jira-mcp-gateway`, `act=read_project_summary`, `res=jira-mcp:/project:IAM`.
- Allows `spiffe://example.org/codex-jira-mcp-adapter` to mint `aud=jira-mcp-gateway`, `act=create_story`, `res=jira-mcp:/project:IAM`.
- Denies `res=jira-mcp:/project:NAS`.
- Denies unsupported M5 actions such as `read_issue_details`, `search_issues`, `update_story`, `comment`, `create_epic`, `create_subtask`, `create_bug`, `assign_issue`, `move_to_sprint`, and `create_sprint`.
- Denies old `spiffe://example.org/agent-a` for the M5 audience/resource.
- Denies `spiffe://example.org/codex-jira-mcp-adapter` for old `aud=jira-tool` when requesting M5 resources.
- Denies `aud=jira-tool` with `res=jira-mcp:/project:IAM`.
- Denies `aud=jira-mcp-gateway` with `res=jira-tool:/project:IAM`.
- Denies malformed resources.
- Denies wildcard, list, lowercase, slash, URL, space, or alias project resources.
- Canonicalizes only strict `jira-mcp:/project:<KEY>` resources.
- Keeps existing M4a/M4b `jira-tool` policy behavior unchanged.
- Emits mint-decision metadata with M5 `aud`, `act`, `res`, subject, decision, reason, and token identifiers when applicable.

Expected traceability:
- New UT blocks should cover M5 capiss resource canonicalization and OPA decision behavior.
- Existing M4a/M4b policy tests should continue to pass unchanged.

### Gateway Unit Tests
Gateway tests prove request-time enforcement and upstream gating.

- Requires a capiss bearer token for every protected endpoint.
- Verifies capiss token signature using the capiss public key.
- Denies expired tokens.
- Denies malformed tokens.
- Denies missing required token fields.
- Denies `aud` mismatch.
- Denies endpoint/action mismatch.
- Denies `read_project_summary` token on `POST /mcp/jira/stories`.
- Denies `create_story` token on `POST /mcp/jira/project-summary`.
- Denies resource mismatch.
- Denies malformed `jira-mcp:/project:<KEY>` resource.
- Denies payload project mismatch with token resource.
- Denies token subject mismatch with Envoy-verified caller identity.
- Denies missing Envoy-verified caller identity.
- Enforces strict project-key syntax.
- Enforces strict `epic_key` syntax when supplied.
- Denies cross-project `epic_key` before upstream create.
- Verifies supplied same-project `epic_key` exists upstream and is an Epic before story creation.
- Denies invalid same-project epic and creates no story.
- Does not expose full epic body during epic verification.
- Allows `read_project_summary` with `project_key=IAM`.
- Bounds `read_project_summary` to latest 50 non-epic issues and latest 25 epics.
- Omits descriptions from `read_project_summary`.
- Omits comments from `read_project_summary`.
- Omits assignees from `read_project_summary`.
- Omits sprints and boards from `read_project_summary`.
- Omits raw JQL and raw Jira URLs from `read_project_summary`.
- Allows `create_story` with `project_key`, `summary`, and `description`.
- Allows optional `acceptance_criteria`.
- Allows optional valid same-project `epic_key`.
- Rejects arbitrary fields including assignee, sprint, priority, labels, components, custom fields, raw Jira `fields`, raw ADF, transitions, comments, attachments, and arbitrary links.
- Applies defensive type and length validation to `summary`, `description`, and optional `acceptance_criteria`.
- Does not enforce acceptance criteria as a story-quality requirement.
- Converts plain text description and optional acceptance criteria into Jira ADF mechanically.
- Does not semantically rewrite story intent, requirements, or acceptance criteria.
- Sets issue type to `Story` internally.
- Strips or ignores client-supplied `Authorization`, Jira auth, and impersonation headers before upstream calls.
- Consumes budget/rate before upstream story create.
- Consumes budget/rate before upstream summary use.
- Does not consume budget on missing/invalid token.
- Does not consume budget on subject, audience, action, resource, or project mismatch.
- Does not consume budget on invalid payload.
- Does not consume budget on invalid or cross-project epic.
- Does not refund budget when upstream create fails after budget consumption.
- Normalizes upstream failures into standardized local errors.
- Does not leak raw Jira error details to Codex.
- Emits gateway enforcement decision events for every terminal path.
- Gateway event includes `subject_spiffe_id`, `aud`, `act`, `res`, `project_key`, `mcp_tool` or endpoint, `decision`, `reason`, `upstream_called`, `upstream_operation`, `issue_key` when created, `epic_key` when supplied, `root_token_id`, `token_id`, and `correlation_id`.

Expected traceability:
- New UT blocks should cover M5 gateway token checks, endpoint-bound action, payload allowlist, epic verification, budget ordering, header stripping, error normalization, and audit events.

### Mock Unit Tests
Mock tests prove deterministic upstream behavior and evidence capture.

- Mock contains broad `IAM` and `NAS` project data.
- Mock can return project summary data for `IAM`.
- Mock can return project summary data for `NAS` through direct test/internal access.
- Mock stores created stories.
- Mock records story creation requests.
- Mock supports valid same-project Epic fixtures.
- Mock supports invalid same-project non-Epic fixtures.
- Mock supports cross-project `NAS` Epic fixtures for negative proof.
- Mock request log records method, path, project key, issue key, request fields, status, and correlation ID when supplied.
- Mock request log can be reset between tests.
- Mock can inject upstream create failures.
- Mock can inject upstream summary failures.
- Mock never performs authorization itself; authorization is tested at capiss/gateway.

Expected traceability:
- Mock UTs are support controls, not primary proof of M5 security requirements.

## E2E Test Plan
### Launcher and MCP Session
#### M5-T1: MCP launcher starts adapter session
Premise: Docker/SPIFFE stack is running and adapter container exists.
Exercise: run the local Codex MCP launcher path with MCP tool discovery.
Outcome: launcher uses `docker compose exec -T`, adapter serves MCP tool metadata, stdout is valid MCP, diagnostics are stderr-only.
Evidence: launcher command capture, stderr diagnostics, tool metadata, adapter container identity, no stdout banner/noise.

#### M5-T2: MCP tool surface is exactly Slice 1
Premise: adapter MCP session is active.
Exercise: list MCP tools.
Outcome: only `read_project_summary` and `create_story` are exposed.
Evidence: MCP tools response, adapter logs without tokens.

### Read Project Summary
#### M5-T3: IAM project summary succeeds
Premise: mock has `IAM` project data with issues and epics.
Exercise: Codex-facing MCP call `read_project_summary` with `project_key=IAM`.
Outcome: response contains project key/name/count, bounded issues, and bounded epics.
Evidence: MCP request/response, capiss mint event, gateway enforcement event, mock request log.

#### M5-T4: Summary response contains only allowed fields
Premise: mock `IAM` data includes descriptions, comments, assignees, and sprint/board-like data.
Exercise: call `read_project_summary`.
Outcome: response excludes descriptions, comments, assignees, sprint data, board data, raw JQL, raw Jira URLs, Jira credentials, and bearer tokens.
Evidence: response JSON, negative field checks, token/credential scan output.

#### M5-T5: Summary response is bounded
Premise: mock has more than 50 non-epic issues and more than 25 epics.
Exercise: call `read_project_summary`.
Outcome: response includes at most 50 non-epic issues and at most 25 epics with server-controlled ordering.
Evidence: response counts, mock fixture metadata, gateway event.

#### M5-T6: NAS project summary denies at capiss
Premise: mock has `NAS` project data to prove upstream breadth.
Exercise: MCP call `read_project_summary` with `project_key=NAS`.
Outcome: capiss denies mint; gateway is not called; upstream is not called.
Evidence: capiss denial event, adapter MCP error with `reason=mint_denied`, gateway/mock request logs showing no call.

### Create Story
#### M5-T7: IAM story creation succeeds with required fields only
Premise: mock accepts story create for `IAM`.
Exercise: MCP call `create_story` with `project_key=IAM`, `summary`, and `description`.
Outcome: created story metadata returns bounded fields only; mock log shows exactly one upstream create.
Evidence: MCP response, capiss event, gateway event, mock request log, created mock issue record.

#### M5-T8: IAM story creation succeeds with optional acceptance criteria
Premise: mock accepts story create for `IAM`.
Exercise: MCP call `create_story` with optional `acceptance_criteria`.
Outcome: gateway converts plain text into generated description body; bounded metadata returns; no custom field is used.
Evidence: mock captured upstream payload, gateway event, response metadata.

#### M5-T9: IAM story creation succeeds with valid same-project epic
Premise: mock contains `IAM-*` issue typed as Epic.
Exercise: MCP call `create_story` with `epic_key=IAM-<number>`.
Outcome: gateway verifies epic before create, creates story, links to epic, returns bounded metadata with `epic_key`.
Evidence: mock request log showing epic verification then create, gateway event, created story metadata.

#### M5-T10: Invalid same-project epic denies and creates no story
Premise: mock contains an `IAM-*` issue that is missing or not an Epic.
Exercise: MCP call `create_story` with that `epic_key`.
Outcome: gateway returns `epic_invalid`, no story create upstream call occurs.
Evidence: gateway event, mock request log, created issue count unchanged.

#### M5-T11: NAS project story creation denies at capiss
Premise: mock has `NAS` data to prove upstream breadth.
Exercise: MCP call `create_story` with `project_key=NAS`.
Outcome: capiss denies mint; gateway and upstream are not called.
Evidence: capiss denial event, adapter MCP error, gateway/mock logs showing no call.

#### M5-T12: IAM token with NAS payload denies at gateway before upstream
Premise: test harness obtains or simulates an IAM create token through the approved path.
Exercise: send gateway request with token resource `IAM` but payload `project_key=NAS`.
Outcome: gateway denies `project_mismatch`; upstream is not called.
Evidence: gateway event, mock request log length unchanged.

#### M5-T13: IAM token with NAS epic denies before upstream create
Premise: mock contains `NAS-*` Epic and no story should be created.
Exercise: MCP or internal harness call attempts `project_key=IAM` with `epic_key=NAS-<number>`.
Outcome: gateway denies before create; no story is created.
Evidence: gateway event, mock request log proving no create, response reason.

#### M5-T14: Arbitrary create fields are rejected
Premise: valid IAM create token path exists.
Exercise: attempt create with assignee, sprint, priority, labels, components, custom fields, raw Jira `fields`, raw ADF, transitions, comments, attachments, and arbitrary links.
Outcome: gateway returns `payload_invalid` and does not call upstream create.
Evidence: per-field request/response artifacts, gateway events, mock request log.

#### M5-T15: Plain text only; raw ADF rejected
Premise: valid IAM create path exists.
Exercise: attempt create with raw ADF payload or non-string description.
Outcome: gateway returns `payload_invalid`; upstream not called.
Evidence: response, gateway event, mock request log.

### Authorization and Boundary Denials
#### M5-T16: Adapter does not authorize NAS locally
Premise: adapter can process MCP request and capiss policy denies NAS.
Exercise: call adapter with `project_key=NAS`.
Outcome: evidence shows adapter forwarded mint request to capiss and reported capiss denial rather than local allowlist denial.
Evidence: adapter log/correlation ID, capiss denial event, absence of adapter-local authorization reason.

#### M5-T17: Unsupported action cannot be minted
Premise: capiss M5 branch is installed.
Exercise: attempt to mint future actions such as `update_story`, `comment`, `create_epic`, or `create_sprint`.
Outcome: capiss denies all unsupported actions.
Evidence: capiss denial events and responses.

#### M5-T18: Old Jira tool authority cannot satisfy M5 gateway
Premise: existing M4a/M4b `jira-tool` token path still exists.
Exercise: present `aud=jira-tool` or `res=jira-tool:/project:IAM` token to M5 gateway.
Outcome: gateway denies `aud_mismatch` or `project_mismatch`; upstream not called.
Evidence: gateway event, mock request log.

#### M5-T19: M5 authority does not disturb existing jira-tool demo
Premise: existing M4a/M4b tests or targeted smoke path are available.
Exercise: run targeted existing Jira demo/E2E checks after M5 additions.
Outcome: existing `jira-tool` behavior still passes.
Evidence: targeted test output and trace/evidence references.

#### M5-T20: Gateway endpoint-bound action is enforced
Premise: valid read and create tokens are available.
Exercise: use read token on create endpoint and create token on summary endpoint.
Outcome: both deny before upstream use.
Evidence: gateway events, mock request log.

#### M5-T21: Audience mismatch denies
Premise: token with wrong audience is available or forged in test harness.
Exercise: call gateway with wrong audience.
Outcome: gateway denies before upstream.
Evidence: gateway event and mock request log.

#### M5-T22: Subject mismatch denies stolen token
Premise: token minted for adapter exists and another SPIFFE workload can reach the gateway Envoy for negative proof.
Exercise: other workload presents adapter token to `jira-mcp-envoy`.
Outcome: gateway denies subject mismatch before upstream.
Evidence: Envoy caller identity, gateway event, mock request log.

#### M5-T23: Expired or invalid token denies
Premise: expired, malformed, or invalid-signature token can be supplied.
Exercise: call gateway with invalid token.
Outcome: gateway denies before upstream.
Evidence: gateway event, response reason, mock request log.

#### M5-T24: Direct app bypass is not available
Premise: network segmentation is active.
Exercise: from adapter or edge-accessible context, attempt direct capiss app and direct gateway app access.
Outcome: direct app paths are unreachable or rejected; approved path uses Envoys.
Evidence: network command outputs, container network inspection, successful Envoy path evidence.

#### M5-T25: Only gateway calls mock upstream
Premise: mock request log reset.
Exercise: run successful and denied MCP calls.
Outcome: mock requests appear only for authorized gateway upstream calls; no adapter-originated mock calls exist.
Evidence: mock request log source metadata, adapter logs, gateway logs.

### Credential and Token Isolation
#### M5-T26: Codex-visible MCP responses contain no capiss tokens
Premise: successful read and create calls run.
Exercise: scan MCP responses and captured stdout.
Outcome: no bearer token strings or Biscuit token material are present.
Evidence: token scan artifacts, responses.

#### M5-T27: Adapter logs/evidence contain no bearer tokens
Premise: adapter processes successful and denied calls.
Exercise: scan adapter logs and evidence artifacts.
Outcome: no bearer token strings are present; only metadata is logged.
Evidence: scan output and log excerpts.

#### M5-T28: Codex/launcher/adapter environment contains no Jira API key
Premise: stack is running in mock mode.
Exercise: capture sanitized environment from launcher/adapter context.
Outcome: no Jira credential variables exist in Codex-facing or adapter environment.
Evidence: sanitized env artifact and credential scan.

#### M5-T29: Gateway-only live credential boundary
Premise: live smoke config is explicitly supplied.
Exercise: inspect service environments or configured evidence paths.
Outcome: live Jira credential is present only for `jira-mcp-gateway`, not Codex, launcher, adapter, capiss, or Envoys.
Evidence: sanitized env artifacts with secrets redacted, service config proof.

#### M5-T30: Client-supplied auth headers are stripped
Premise: gateway receives a create request with client-supplied `Authorization` or impersonation-like headers.
Exercise: authorized create call includes those headers through internal harness path.
Outcome: upstream mock does not receive client-supplied auth/impersonation headers.
Evidence: mock captured headers, gateway event.

### Governance
#### M5-T31: Successful summary participates in budget/rate governance
Premise: token has budget/rate context.
Exercise: perform repeated summary calls until the configured limit is reached.
Outcome: allowed calls consume/log governance; exhausted call denies before upstream.
Evidence: gateway events, Redis/budget evidence when available, mock request count.

#### M5-T32: Successful create consumes budget before upstream mutation
Premise: budget is available.
Exercise: create story once.
Outcome: gateway consumes budget before upstream create and logs the order.
Evidence: gateway event timing/order fields, mock request log.

#### M5-T33: Budget exhaustion denies create before upstream
Premise: budget is exhausted for the token/root context.
Exercise: attempt create story.
Outcome: gateway returns `budget_exhausted`; mock sees no create.
Evidence: gateway event, mock request log.

#### M5-T34: Pre-validation denials do not consume budget
Premise: budget counter is observable in test context.
Exercise: attempt invalid payload or cross-project epic.
Outcome: budget remains unchanged; upstream not called.
Evidence: before/after budget evidence, gateway event, mock request log.

#### M5-T35: Upstream create failure after budget spend is not refunded
Premise: mock is configured to fail create after gateway authorization and budget consumption.
Exercise: create story.
Outcome: gateway returns standardized `upstream_error`; budget is not refunded.
Evidence: budget before/after, gateway event, mock failure log.

### Audit and Evidence
#### M5-T36: Capiss and gateway events correlate for successful read
Premise: successful summary call.
Exercise: collect capiss and gateway logs.
Outcome: events correlate by `correlation_id`, subject, `aud`, `act`, `res`, `token_id`, `root_token_id`, decision, and reason.
Evidence: extracted event JSON and correlation check.

#### M5-T37: Capiss and gateway events correlate for successful create
Premise: successful create call.
Exercise: collect capiss and gateway logs.
Outcome: events reconstruct mint and enforcement decision, upstream operation, and created issue key.
Evidence: extracted event JSON, mock request log, created issue metadata.

#### M5-T38: Deny paths produce final decision evidence
Premise: representative mint deny, gateway deny, payload deny, budget deny, and upstream error scenarios.
Exercise: run each scenario.
Outcome: each terminal path has an explicit final decision event with reason.
Evidence: per-scenario event artifacts.

#### M5-T39: Standardized local errors avoid upstream existence disclosure
Premise: `NAS` project and issues exist in mock.
Exercise: try NAS summary, NAS create, and NAS epic.
Outcome: Codex-facing errors are local standardized errors and do not reveal raw upstream details.
Evidence: responses, mock fixture proving NAS exists, absence of upstream body leakage.

### Mock and Live Breadth Proof
#### M5-T40: Mock upstream breadth precondition
Premise: deterministic mock is available.
Exercise: test/internal access proves mock has both `IAM` and `NAS` data.
Outcome: mock breadth is proven independently of protected MCP path.
Evidence: direct mock precondition artifact, with no Codex path to mock.

#### M5-T41: Protected path narrows broad mock
Premise: mock breadth is proven.
Exercise: run IAM allowed and NAS denied MCP calls.
Outcome: protected path allows only IAM despite broad upstream data.
Evidence: capiss/gateway events and mock request logs.

#### M5-T42: Optional live smoke proves broad live credential and protected narrowing
Premise: live Jira credentials/config are explicitly provided.
Exercise: operator-side direct live precondition proves same credential can access IAM and NAS; protected MCP path allows IAM and denies NAS.
Outcome: live credential breadth and protected narrowing are both proven without exposing credentials to Codex.
Evidence: live smoke status/project-key artifacts only, no issue bodies or secrets.

## Assumptions and Fixtures
- Deterministic test mode defaults to `jira-mcp-mock`.
- Live Jira smoke is explicit opt-in and never part of the default deterministic suite.
- Existing Docker/SPIFFE preflight and stack lifecycle commands remain the operator-managed path.
- The MCP launcher does not start or rebuild the stack.
- The adapter container must be running before the launcher starts a Codex MCP session.
- The adapter process starts fresh per Codex MCP server session.
- Each MCP tool call mints a fresh capiss token.
- The gateway, not the adapter, is the only M5 component with live Jira API credentials.
- Mock fixtures include:
  - allowed project `IAM`
  - non-allowed project `NAS`
  - more than 50 non-epic `IAM` issues
  - more than 25 `IAM` epics
  - issue/epic descriptions and comments to prove summary exclusion
  - valid `IAM` Epic
  - invalid same-project non-Epic
  - valid `NAS` Epic for cross-project denial
  - upstream failure injection controls
- Evidence must avoid raw bearer tokens, Jira API credentials, full live issue bodies, and raw secrets.

## Planned Verification Commands
- Unit guard integrity:
  ```bash
  make unit-guard-check
  ```
- Unit trust bundle:
  ```bash
  make unit-trust
  ```
- Targeted M5 E2E:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
    -e TEST_MILESTONES=m5 rogue-tests
  ```
- Full deterministic E2E:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
  ```
- Traceability:
  ```bash
  make qa-trace
  ```
- Quality:
  ```bash
  make qa-quality
  ```
- Evidence:
  ```bash
  make qa-evidence
  ```
- Optional live smoke:
  ```bash
  scripts/jira_mcp_live_smoke.sh
  ```

## Review Notes
- The E2E cases are intentionally broader than a minimum demo because the slice is proving a new MCP-based real-world usage model.
- Adapter tests should verify it does not become an authorization decision point.
- Gateway tests should verify it remains the authoritative request-time PEP.
- Capiss tests should verify M5 does not reuse or disturb M4a/M4b `jira-tool` authority.
- Credential and token scans are first-class proof, not incidental checks.
- Any new assumption discovered while writing tests must return to `plan.md` before implementation proceeds.
