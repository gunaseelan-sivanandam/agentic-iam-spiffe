# Architecture Delta

## Responsibility changes
- Add `jira-tool-envoy` as the trusted ingress boundary for Jira facade traffic. It follows the existing mTLS and `x-spiffe-id` trusted-header model.
- Add `jira-tool` as the protected resource server and request-time PEP for Jira issue reads. It verifies capiss-signed tokens locally, enforces subject/audience/action/project scope, consumes shared M4 budget/rate state, and only then calls Jira/mock with its server-side credential.
- Add `jira-mock` as broad upstream test infrastructure, not a production architecture component.
- Treat Jira Cloud as an optional external dependency for live smoke only.
- Extend Redis interaction so `jira-tool` reads/writes the same `m4:budget:<root_token_id>` and request-rate state as other tools.
- Add Jira-specific network segmentation so edge clients can reach only `jira-tool-envoy`, while `jira-tool`, Redis, and `jira-mock` remain on internal networks.
- Update the architecture diagrams to show the implemented M4a Jira components and networks explicitly. The current diagrams also include the M4b description-write extension on the same boundary.

## Network segmentation
- `jiratool_edge_net`:
  - members: `agent-a`, `rogue`, `jira-tool-envoy`
  - purpose: mTLS client access to the Jira facade boundary only
  - denied by design: direct access to `jira-tool`, `jira-mock`, Redis, OPA, or capiss app internals
- `jiratool_app_net`:
  - members: `jira-tool-envoy`, `jira-tool`, Redis
  - purpose: trusted boundary-to-application traffic and shared M4 budget/rate access
- Jira upstream side:
  - `jira-mock` is upstream-only test infrastructure reachable by `jira-tool` and test/internal access
  - edge clients and agents must not reach `jira-mock` directly
  - live Jira Cloud is reached only by `jira-tool` in live mode
- Host exposure:
  - expose only `jira-tool-envoy` for Jira facade traffic, default port `10443`
  - do not host-expose `jira-tool` or `jira-mock`
- Negative proof:
  - `jira-tool-envoy` allows mTLS from both `agent-a` and `rogue` so rogue failures prove authorization/token enforcement rather than transport-only blocking
  - mock request-log/reset endpoints are test-only and not edge-reachable

## Authoritative state inventory

| State / Key | Store / System | Writer | Reader | TTL / Lifecycle | Decision impact | Type |
|---|---|---|---|---|---|---|
| Jira allowed project set | OPA policy/data | Operator/repo config | OPA during capiss mint decision | Deployment lifecycle | Determines whether `agent-a` may mint `jira-tool:/project:<KEY>` | Authoritative |
| `m4:budget:<root_token_id>` | Redis | capiss initializes; tools consume | `jira-tool`, existing tools | Bounded by root token expiry | Denies Jira request when budget is missing, invalid, exhausted, or store unavailable | Authoritative |
| M4 request-rate key | Redis | `jira-tool`, existing tools | `jira-tool`, existing tools | Rate window/root TTL bounded | Denies Jira request on rate limit or store error | Authoritative |
| capiss signing public key | Mounted file | capiss | `jira-tool` | Key lifecycle | Verifies token authenticity before Jira credential use | Authoritative |
| Jira API credential | `jira-tool` live env | Operator/live smoke setup | `jira-tool` only | Live runtime | Enables upstream Jira call after local authorization; never grants agent authority | Sensitive secret |
| Jira mock request log | `jira-mock` memory | `jira-mock` | test harness | Test lifecycle | Evidence that pre-forward denials did not call upstream | Test evidence |

## Hidden behavior disclosure
- `jira-tool` derives the requested project from issue key prefix for `GET /jira/rest/api/3/issue/<ISSUE_KEY>`.
- `jira-tool` strips the local `/jira` facade prefix before calling upstream `/rest/api/3/issue/<ISSUE_KEY>`.
- `jira-tool` denies successful upstream issue responses that do not contain a matching `fields.project.key`.
- Mock/live upstream selection is controlled only by `jira-tool`; the agent is upstream-agnostic.
