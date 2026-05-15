# Slice Plan: M4a Jira Project Access

## Goal
M4a applies the M4 capability and governance model to a real-world Jira access-control problem: a trusted `jira-tool` holds a broad Jira API credential, but an agent can only read issues from the single Jira project authorized by OPA and minted by `capiss`. The slice proves that the upstream credential's broad access is narrowed by SPIFFE identity, OPA-gated capability issuance, and request-time enforcement in `jira-tool`.

## Success criteria
- `agent-a` can mint only `aud=jira-tool`, `act=read`, `res=jira-tool:/project:IAM` through `capiss` and OPA.
- `agent-a` can read `IAM-1` through `jira-tool-envoy` using the project token.
- Minting a token for any non-allowed project is denied by OPA/capiss; there is no disallowed-project policy list.
- A token for the allowed project cannot read a non-allowed issue such as `NAS-1`; `jira-tool` denies before calling Jira/mock.
- Rogue can reach the Jira Envoy boundary for proof, but cannot mint the allowed Jira token and cannot use a stolen agent token.
- Successful Jira reads consume the shared M4 request budget/rate state by `root_token_id`; budget exhaustion denies the 11th default-budget read before upstream use.
- Mock and optional live smoke prove the upstream Jira credential/data source is broader than the allowed project, while the capiss/jira-tool path narrows access.
- Jira API credentials are never exposed to the agent, tokens, normal logs, or evidence.

## In scope
- Add a new M4a requirements section for Jira-specific behavior and reference existing M4 primitives where applicable.
- Add architecture components for `jira-tool` and `jira-tool-envoy`; document Jira Cloud as an optional live-smoke dependency and `jira-mock` as test infrastructure.
- Add `jira-tool` as a new Python protected resource server using stdlib HTTP client and the existing shared chain contract.
- Add `jira-tool-envoy` following the same SPIFFE/mTLS/trusted-header pattern as `tool-b-envoy`.
- Add explicit Jira network segmentation: edge clients reach only `jira-tool-envoy`; `jira-tool` and `jira-mock` stay off the edge network; Redis joins the Jira app network for shared budget/rate governance.
- Add a simple Python stdlib `jira-mock` upstream with broad mock data for `IAM-1`, `IAM-2`, `NAS-1`, and `NAS-2`, plus test-only request log/reset endpoints.
- Extend `capiss` canonicalization for Jira project resources with a small explicit branch, not a plugin framework.
- Extend OPA policy so `spiffe://example.org/agent-a` can mint only the allowed Jira project token; all other projects deny by default.
- Advance static capiss policy version metadata for audit events, e.g. `capiss.allow.v3` and `sha256:capiss-policy-v3`.
- Add explicit `agent-a` Jira demo script triggered manually, not on normal stack startup.
- Add M4a E2E cases under a separate `M4a-T*` suite and support `TEST_MILESTONES=m4a`.
- Add optional live smoke as a separate script/Make target with evidence under `artifacts/jira-live-smoke/`.
- Add OPL entries for retiring `/capabilities/mint` and computing a real policy hash.

## Out of scope
- Confluence support.
- Human-user authorization or OAuth 3LO.
- Write, update, comment, or delete Jira operations.
- Issue-level least privilege or Jira resource-mint/delegation.
- Full generic Jira gateway compatibility.
- Jira response filtering/redaction beyond access-control project verification.
- Envoy-level method authorization for Jira.
- Pluggable tool canonicalization framework.
- Sharing/refactoring `tool-b` PEP code into a new helper.
- Retiring `/capabilities/mint` in this slice.

## Affected authored sources
- Requirements: add `M4a` Jira project-access requirements in `docs/requirements.md`.
- Architecture: add `jira-tool` and `jira-tool-envoy` components, state interactions, and optional Jira Cloud/live-smoke notes in `docs/architecture.md`.
- Runtime proof: add M4a E2E mappings in `trace/tests.yaml` with case-level requirement links.
- Status and follow-up: update `docs/open_problem_log.md`; update gitignored local implementation status during work.

## Implementation phases
1. Author M4a requirements, architecture delta, ADR/DDR, implementation contract, retirement contract, and validation plan before code.
2. Add unit tests first for Jira canonical resource validation, Jira token/request authorization, subject binding, budget/rate failure behavior, upstream project mismatch, and audit event fields.
3. Add deterministic M4a E2E tests and mock Jira evidence before implementation where practical.
4. Implement capiss/OPA Jira minting support, `jira-tool`, `jira-tool-envoy`, `jira-mock`, compose/SPIRE entries, agent demo, and live smoke script.
5. Update trace/test specs/README and run targeted UT/E2E, then full QA gates.

## Planned deterministic E2E cases
- `M4a-T1`: mock upstream breadth precondition proves direct mock can read `IAM-1` and `NAS-1`.
- `M4a-T2`: agent-a mints allowed Jira project token and reads `IAM-1` through `jira-tool-envoy`.
- `M4a-T3`: capiss/OPA denies mint for a non-allowed project.
- `M4a-T4`: allowed project token cannot read `NAS-1`; `jira-tool` denies before upstream and mock request log proves no call.
- `M4a-T5`: rogue cannot mint the allowed Jira project token.
- `M4a-T6`: rogue using a stolen agent token is denied by subject binding before upstream.
- `M4a-T7`: successful Jira read consumes/logs shared M4 budget.
- `M4a-T8`: default budget exhaustion with repeated `IAM-1` reads denies the 11th read and mock saw only 10 upstream calls.
- `M4a-T9`: upstream `200` with mismatched or missing `fields.project.key` is denied without returning the body.
- `M4a-T10`: audit trace reconstructs capiss mint and jira-tool enforcement events.

## Optional live smoke
- Separate command/target, not part of full deterministic E2E.
- Uses same SPIFFE/mTLS/Envoy path for capiss and `jira-tool`.
- Uses direct Jira API-key calls only as preconditions to prove the broad credential can read both the allowed issue and a non-allowed issue.
- Stores only status codes and extracted project keys, not issue bodies or bearer/API tokens.
- Proves allowed issue read, disallowed project mint deny, disallowed request deny with `upstream_called=false`, and rogue stolen-token denial if simple with existing test material.
- Direct live preconditions must prove the same API credential can read an `IAM-*` issue and a `NAS-*` issue before capiss/jira-tool narrowing is evaluated.

## Review notes
- OPA contains only allowed projects; disallowed project/issue values are test/demo inputs, not policy configuration.
- Local default allowed project is `IAM` for Jira space `agentic-iam-spiffe`; mock default non-allowed issue input is `NAS-1` from Jira space `No-Agent-Space`.
- Live demo can use env-provided issue keys for demo input, but authorization remains based only on the OPA allowed project list.
- No npm or axios is introduced.
- Agent Jira demo must not print bearer tokens; it prints only token metadata, HTTP status, and denial reasons.
- Successful in-scope Jira responses pass through unchanged after project verification; local access-control denies use local deny bodies and do not reveal project existence.

## Network segmentation contract
- `jiratool_edge_net` carries client-to-boundary traffic only. `agent-a`, `rogue`, and `jira-tool-envoy` join this network.
- `jiratool_app_net` carries boundary-to-app and app-to-shared-state traffic. `jira-tool-envoy`, `jira-tool`, and Redis join this network.
- `jira-mock` is upstream-only test infrastructure. It is reachable by `jira-tool` and test/internal access, but not by edge clients or agents.
- Only `jira-tool-envoy` is host-exposed for the Jira facade, on port `10443` unless implementation finds a documented port conflict.
- `jira-tool` and `jira-mock` are not host-exposed and are not attached to `jiratool_edge_net`.
- `jira-tool-envoy` accepts mTLS from `agent-a` and `rogue` to support positive and negative proof; capiss/jira-tool authorization remains the enforcement layer.
- Mock request-log/reset endpoints are not edge-reachable and exist only for deterministic evidence.
