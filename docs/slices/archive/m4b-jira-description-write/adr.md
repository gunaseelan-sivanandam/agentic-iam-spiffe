# ADR: Project-Scoped Jira Description Write

## Decision
Represent Jira description update authority as `aud=jira-tool`, `act=write`, `res=jira-tool:/project:<PROJECT_KEY>`.

## Rationale
Project scope matches the M4a proof model and keeps non-allowed issue keys as test inputs rather than policy deny-list entries. A separate write action makes read-only and write-capable tokens distinguishable at request time.

## Rejected Options
- Transparent Jira proxy: rejected because it would let the broad upstream credential escape the local authorization boundary.
- Arbitrary `fields` update payloads: rejected because M4b only needs description replacement and broader writes would require new requirements and evidence.
- Issue-level resources: deferred because the existing slice proves project-scoped authority only.

## Consequences
- A write token can read back the marker for the same project.
- A read token cannot update descriptions.
- Live smoke intentionally mutates and leaves the allowed Jira issue description changed.
