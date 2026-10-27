# DDR

## Design decision
Implement a minimal Jira issue-read facade with project-wide read tokens: `aud=jira-tool`, `act=read`, `res=jira-tool:/project:<PROJECT_KEY>`.

## Alternatives considered
- Issue-specific resource tokens:
  - pros: stronger least privilege
  - cons: requires discovery/resource-mint semantics and distracts from wide-credential project narrowing MVP
- Search plus issue read:
  - pros: closer to common Jira workflows
  - cons: adds JQL parsing and query-scope decisions outside this access-control demo
- Single issue-read path only:
  - pros: direct project-scope proof, simple deterministic parsing, fewer Jira URL nuances
  - cons: smaller Jira surface

## Chosen option
Support only `GET /jira/rest/api/3/issue/<ISSUE_KEY>` in M4a. Derive project from issue key prefix, compare it to the signed token project, deny mismatches before upstream, and verify `fields.project.key` on successful upstream responses before returning the body unchanged.

## Rejected options
- Full Jira proxy and raw URL forwarding are rejected.
- For M4a, write/delete action vocabulary is not implemented and non-GET Jira methods deny in the application. M4b later adds a separate `act=write` contract for description replacement only; this does not turn `jira-tool` into a general write proxy.
- Shared PEP helper extraction is deferred; `jira-tool` implements its own verifier using the existing shared chain contract while leaving `tool-b` unchanged.
