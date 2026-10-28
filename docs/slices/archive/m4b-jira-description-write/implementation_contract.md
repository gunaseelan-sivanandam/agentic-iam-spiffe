# Implementation Contract

## Runtime Behavior
- OPA allows IAM write minting only for `spiffe://varambu.org/agent-a`.
- `capiss` canonicalizes Jira project resources exactly as in M4a and sends the full write tuple to OPA.
- `jira-tool` accepts write tokens for GET and PUT, but read tokens only for GET.
- `jira-tool` validates description update bodies before upstream calls.
- `jira-tool` converts plain text to Jira ADF and returns `204` on successful upstream update.
- `jira-tool` consumes the same Redis budget/rate state for reads and writes.
- `jira-mock` supports PUT description updates and request-log evidence.
- `agent-a/jira_demo.sh` and `scripts/jira_live_smoke.sh` print only statuses, reason codes, token metadata, project names, and sanitized marker-match results.

## Exact Authority
- Read: `aud=jira-tool`, `act=read`, `res=jira-tool:/project:IAM`.
- Write: `aud=jira-tool`, `act=write`, `res=jira-tool:/project:IAM`.
- Non-allowed NAS write minting must deny by policy.

## Evidence Expectations
- Allowed IAM write mint status `200`.
- Allowed IAM description update status `204`.
- Write token protected GET shows the marker.
- Read token write attempt denies with `insufficient_authority`.
- NAS write mint denies with `policy`.
- NAS write with IAM write token denies with `project_mismatch` before upstream.
- Audit evidence correlates capiss mint and jira-tool write/read decisions.
