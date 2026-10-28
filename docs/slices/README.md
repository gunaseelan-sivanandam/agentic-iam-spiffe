# Slice Bundles

A slice bundle is the review record for one milestone or security-relevant change: the agreed design,
requirement and architecture changes, hidden-state decisions, and the UT/E2E proof plan.
The workflow that produces and closes a bundle is defined in [`AGENTS.md`](../../AGENTS.md#slice-workflow).

- New bundle: copy [`_template/`](_template/) to `docs/slices/<slice-id>/` (`plan.md` + `test_plan.md`).
- Once a slice is implemented its bundle is a **frozen record**. Do not edit it to match later
  reality; record later changes in a new slice or in `docs/history/implementation_log.md`.
- Add a row to the index below when a bundle is created, and update its status when it closes.

## Index

| Slice | Milestone | Status | Dates | Notes |
| --- | --- | --- | --- | --- |
| [agentic-delivery-process](agentic-delivery-process/) | — | Plan for review | 2026-10-28 | Gates, agent pipeline, pilot fixing OPL-005/006/007; grill-me decisions D1–D15, review decision D16 |
| [docs-consolidation](docs-consolidation/) | — | Implemented, PR pending | 2026-10-27 | `AGENTS.md` rulebook, tracked status, complete E2E spec, `make docs-check` in CI |
| [m5-generic-verifier-architecture](m5-generic-verifier-architecture/) | M5+ | Brainstorm, not approved | 2026-06-14 | Generic capability verifier; next candidate slice |
| [m5-full-chain-audit-trace](m5-full-chain-audit-trace/) | M5 | Implemented | 2026-06-19 – 06-30 | `varambu trace`, `M5-T49..T59`; Increment 3 harness hardening merged 2026-10-27 (PR #2) |
| [varambu-audit-format](varambu-audit-format/) | M5 | Implemented | 2026-06-13 | Human audit log presentation (`d417568`) |
| [varambu-start-ux](varambu-start-ux/) | M5 | Implemented | 2026-06-13 | `varambu start` output (`d417568`) |
| [m5-varambu-audit-demo](m5-varambu-audit-demo/) | M5 | Implemented | 2026-06-06 | `varambu` CLI and capiss audit, `M5-T42..T48`. Its plan header still reads "untrusted spike"; implementation is recorded in the implementation log (2026-06-06) |
| [m5-codex-jira-mcp-slice-1](m5-codex-jira-mcp-slice-1/) | M5 | Implemented | 2026-05-16 | Codex → Jira MCP path, `M5-T1..T41` |

### Archived (legacy 8–9 file format, implemented)

| Slice | Milestone | Dates |
| --- | --- | --- |
| [m4b-jira-description-write](archive/m4b-jira-description-write/) | M4b | 2026-05-15 |
| [m4a-jira-project-access](archive/m4a-jira-project-access/) | M4a | 2026-05-14 |
| [m4-semantic-trace-closure](archive/m4-semantic-trace-closure/) | M4 | 2026-05-13 |
| [m2-verified-client-requests](archive/m2-verified-client-requests/) | M2 | 2026-04-27 |
| [m4-observability-closure](archive/m4-observability-closure/) | M4 | 2026-04-24 |
