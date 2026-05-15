# Implementation Contract

## Runtime behavior changes
- `capiss` accepts syntactically valid Jira project resources for root mint requests and sends them to OPA for authorization.
- OPA allows `spiffe://example.org/agent-a` to mint only the configured allowed Jira project token and denies all other Jira project token requests by default.
- `jira-tool` accepts only root Jira project read tokens for M4a.
- `jira-tool` denies delegated Jira tokens with `delegation_not_supported`.
- In the M4a contract, `jira-tool` denies non-GET requests in application code. The current runtime is extended by M4b, which permits only the M4b description-write `PUT` path under the separate M4b contract.
- `jira-tool` denies project mismatch, subject mismatch, audience/action/resource mismatch, invalid token, expired token, Redis failure, budget exhaustion, and upstream project mismatch without exposing Jira credentials.
- `agent-a` gets an explicit Jira demo script that mints allowed Jira authority, reads allowed issue, attempts disallowed mint, and attempts disallowed issue read without printing bearer tokens.

## Affected implementation areas
- `services/capability-issuer/app.py`: Jira canonical resource branch and policy version metadata.
- `services/opa/policy.rego`: Jira root-mint allow rule for agent-a allowed project only.
- `services/jira-tool/**`: new protected resource server and Docker packaging.
- `services/jira-tool-envoy/**`: new Envoy boundary following tool-b pattern.
- `services/jira-mock/**`: new broad mock upstream and request-log endpoints.
- `compose/spiffe.compose.yml`: new services/networks/ports and Redis network attachment.
- `spire/token-init/init.sh`: new SPIFFE workload entries for `jira-tool` and `jira-tool-envoy`.
- `agents/agent-a/jira_demo.sh`: explicit Jira demo script.
- `scripts/rogue_node_tests.sh`: M4a E2E suite and milestone filter support.

## Exact contracts
- Token authority: `aud="jira-tool"`, `act="read"`, `res="jira-tool:/project:<PROJECT_KEY>"`.
- Concrete M4a demo authority: `aud="jira-tool"`, `act="read"`, `res="jira-tool:/project:IAM"`.
- Concrete Jira spaces/projects:
  - allowed space/project: `agentic-iam-spiffe`, project key `IAM`, issue examples `IAM-1`, `IAM-2`
  - non-allowed test/demo input space/project: `No-Agent-Space`, project key `NAS`, issue examples `NAS-1`, `NAS-2`
- MVP project key validation: strict uppercase Jira-style project key, no wildcards or list semantics.
- Agent-facing route: `GET /jira/rest/api/3/issue/<ISSUE_KEY>`.
- Current runtime extension: M4b also supports `PUT /jira/rest/api/3/issue/<ISSUE_KEY>` for description replacement only, and only with `act=write`.
- Upstream route: `/rest/api/3/issue/<ISSUE_KEY>`.
- Request project derivation: issue key prefix before first `-`.
- Required upstream success check: response `fields.project.key` equals requested/token project.
- Successful in-scope Jira issue responses pass through unchanged after project verification.
- Upstream Jira/mock errors for otherwise in-scope authorized requests pass through with upstream status/body.
- Local access-control denials use the local deny body and must not reveal whether the requested Jira project exists upstream.
- Audit event type: `jiratool_enforcement_decision`.
- Audit fields: `result`, `reason_code`, `subject_spiffe_id`, token IDs, `aud`, `act`, `res`, `jira_operation`, `requested_project`, `token_project`, `issue_key`, `upstream_called`, optional `upstream_status`, optional `budget_remaining`.
- Status codes: missing or invalid token uses `401`; valid-token authorization denies use `403`; unsupported non-GET methods use `405`; local trusted dependency failure uses `503`; upstream Jira/mock transport failure uses `502`.
- Mock test endpoints: request log/reset endpoints exist only on mock/internal test path.

## Credential and upstream contract
- Live mode constructs Jira Basic auth inside `jira-tool` from server-side live environment variables.
- Mock mode uses no real Jira API credential.
- The agent never receives, forwards, logs, or stores the Jira API credential.
- `jira-tool` strips client-supplied authorization/impersonation headers before calling upstream and constructs upstream auth itself in live mode.
- `jira-tool` is the only runtime component that selects mock versus live upstream; agent behavior is identical in both modes.

## Compose and network contract
- Add `jiratool_edge_net` and attach only `agent-a`, `rogue`, and `jira-tool-envoy`.
- Add `jiratool_app_net` and attach `jira-tool-envoy`, `jira-tool`, and Redis.
- Keep `jira-tool` off `jiratool_edge_net`.
- Keep `jira-mock` off `jiratool_edge_net` and off host ports.
- Make `jira-mock` reachable to `jira-tool` as upstream test infrastructure and reachable to the test harness only through internal/test access needed for evidence.
- Expose `jira-tool-envoy` on host port `10443` unless implementation discovers a documented conflict and stops for approval.
- Configure `jira-tool-envoy` with SPIFFE identity `spiffe://example.org/jira-tool-envoy`.
- Configure `jira-tool` with SPIFFE identity `spiffe://example.org/jira-tool`.
- Configure `jira-tool-envoy` mTLS client SAN allowlist to include `spiffe://example.org/agent-a` and `spiffe://example.org/rogue`.
- Attach `agent-a` and `rogue` to `jiratool_edge_net` for positive and negative proof.

## Test intent
- UT: capiss Jira canonicalization and OPA inputs; jira-tool request parsing; token verification; subject/audience/action/project checks; budget/rate fail closed; upstream mismatch denial; audit event fields.
- E2E: M4a-T1 through M4a-T10 from the slice plan.
- Live smoke: separate command/target with separate evidence directory.
- Live smoke precondition: direct Jira API-key calls must prove the upstream credential can read both an allowed `IAM-*` issue and a non-allowed `NAS-*` issue before proving capiss/jira-tool narrowing. When M4b is present, the same live smoke also verifies the protected description-write path.
- Agent demo: explicit script must mint `IAM`, read `IAM-1`, show mint denial for `NAS`, show request denial for `NAS-1`, and print only token metadata/status/reason information.

## Explicit non-changes
- Do not modify `tool-b` behavior.
- Do not add npm, axios, or new package dependencies.
- Do not retire `/capabilities/mint` in this slice.
- Do not add Confluence components, requirements, or trace IDs.
- Do not expose Jira API credentials to agent containers.
