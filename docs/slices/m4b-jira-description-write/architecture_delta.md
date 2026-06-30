# Architecture Delta

## Runtime Changes
- Extend OPA/capiss Jira authority issuance to allow `act=write` only for `spiffe://varambu.org/agent-a` and `jira-tool:/project:IAM`.
- Extend `jira-tool` action semantics:
  - `GET /jira/rest/api/3/issue/<ISSUE_KEY>` accepts `act=read` or `act=write`.
  - `PUT /jira/rest/api/3/issue/<ISSUE_KEY>` requires `act=write`.
- Add a narrow description update adapter in `jira-tool` that accepts only `{"description":"..."}` and sends Jira REST v3 ADF under `fields.description`.
- Extend `jira-mock` to store description updates and log GET/PUT upstream calls.

## Authoritative State Inventory
| State | Store/System | Writer | Reader | TTL/Lifecycle | Decision Impact | Classification |
| --- | --- | --- | --- | --- | --- | --- |
| Jira write allow tuple | OPA policy/data | Operator/repo config | OPA during capiss root mint | Deployment lifecycle | Determines whether `agent-a` may mint IAM write authority | Authoritative |
| `m4:budget:<root_token_id>` | Redis | capiss initializes; `jira-tool` consumes | `jira-tool` | Root-token TTL bounded | Denies read/write when budget is missing, invalid, exhausted, or store unavailable | Authoritative |
| M4 request-rate key | Redis | `jira-tool` | `jira-tool` | Rate window/root-token TTL bounded | Denies read/write on rate limit or store error | Authoritative |
| Jira issue description | Jira Cloud or `jira-mock` | `jira-tool` after local authorization | Jira upstream and protected GET path | Upstream lifecycle | Stores the M4b mutation | Upstream state |
| Jira mock request log | `jira-mock` memory | `jira-mock` | test harness | Test lifecycle | Proves whether upstream was called | Test evidence |

## Network
No new networks are added. M4b reuses the M4a `jira-tool-envoy`, `jira-tool`, Redis, and `jira-mock` topology.
