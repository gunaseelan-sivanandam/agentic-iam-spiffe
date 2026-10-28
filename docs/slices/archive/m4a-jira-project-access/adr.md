# ADR

## Architecture decision
Introduce M4a as a Jira-specific real-world connector milestone: `jira-tool` holds the broad Jira credential and enforces narrower capiss/OPA project authority for a SPIFFE-authenticated agent workload.

## Alternatives considered
- Extend `tool-b` into a Jira adapter:
  - pros: fewer services
  - cons: mixes lab baseline with real connector behavior and risks M4 regressions
- Add generic Atlassian/Confluence-ready connector now:
  - pros: broader future shape
  - cons: premature abstraction and semantic trace risk
- Add separate `jira-tool` and `jira-tool-envoy`:
  - pros: preserves M4 baseline, isolates Jira semantics, clear proof boundary
  - cons: new compose/SPIRE/test surface

## Chosen option
Add separate `jira-tool` and `jira-tool-envoy` components. The connector enforces Jira project authority locally before using the upstream API credential.

## Rejected options
- Transparent Jira proxy is rejected because forwarding arbitrary requests with a broad API credential would bypass the intended local authorization boundary.
- Human-user/OAuth authorization is rejected for M4a because the current project subject is workload SPIFFE identity.
- Confluence placeholders are rejected to avoid semantic trace over-claiming.
