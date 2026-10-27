# M4b Jira Description Write Plan

## Goal
Add a traceable M4b slice that lets `agent-a` update Jira issue descriptions only in the OPA-allowed `IAM` project through `capiss` and `jira-tool`.

## Scope
- Keep M4a read-only.
- Add `act=write` for `aud=jira-tool`, `res=jira-tool:/project:IAM`.
- Treat `act=write` as project-scoped read plus description replacement only.
- Deny `act=read` writes, NAS write minting, NAS writes with an IAM token, malformed bodies, and unrelated fields.
- Preserve credential non-disclosure in demo, live smoke, logs, and evidence.

## Non-Goals
- Comments, transitions, attachments, search, delete, arbitrary field updates, issue-level attenuation, human-user OAuth, or Confluence.
- Adding new Jira network topology.
- Exposing Jira credentials to agents.

## Validation
- Unit tests for capiss Jira write mint tuple and jira-tool read/write method behavior.
- M4b E2E tests for write mint, update, readback, read-token denial, NAS deny, body validation, and audit reconstruction.
- Optional live smoke mutates and leaves the allowed Jira issue description changed.
