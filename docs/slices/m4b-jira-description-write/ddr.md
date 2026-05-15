# DDR: Description Update Shape

## Decision
Accept only a JSON object with exactly one string field:

```json
{"description":"plain text"}
```

`jira-tool` converts the string to Jira Cloud Atlassian Document Format before calling upstream:

```json
{"fields":{"description":{"type":"doc","version":1,"content":[...]}}}
```

## Rationale
This keeps the agent-facing contract small, reviewable, and independent of Jira Cloud's full write API. It also lets tests reject unrelated fields before upstream use.

## Deny Reasons
- `malformed_body`: invalid JSON, non-object body, missing/non-string description, invalid length.
- `unsupported_fields`: any field other than `description`.
- `insufficient_authority`: valid token that lacks `act=write` for PUT.
- `project_mismatch`: token project differs from requested issue prefix.
