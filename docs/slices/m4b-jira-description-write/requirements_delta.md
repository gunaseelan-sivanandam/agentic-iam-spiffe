# Requirements Delta

## Added
- `REQ-M4B-W1` broad upstream Jira credential is not caller write authority.
- `REQ-M4B-W2` OPA may allow only `agent-a` to mint IAM write authority.
- `REQ-M4B-W3` `act=write` can read and write descriptions; `act=read` remains read-only.
- `REQ-M4B-W4` write body is exactly one plain-text `description` field converted to Jira ADF.
- `REQ-M4B-W5` write project mismatch denies before upstream use.
- `REQ-M4B-W6` successful writes return `204 No Content`; local denials remain local.
- `REQ-M4B-W7` M4 identity, token, budget, rate, and fail-closed primitives apply to writes.
- `REQ-M4B-W8` write decisions produce audit-safe evidence.
- `REQ-M4B-W9` mock and live smoke evidence prove allowed write and denied NAS/read-token paths.

## Refined
- M4a remains read-only. Jira description writes are explicitly M4b behavior.
- Jira write out-of-scope text now excludes only arbitrary writes, comments, transitions, attachments, search, delete, and issue-level attenuation.
