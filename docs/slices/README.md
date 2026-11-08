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
| [agentic-sdlc-poc](agentic-sdlc-poc/) | — | Slices 1–3 merged (PR #34, #35, #37); slice 4 split into the six bundles below, built in this order: 4.1, 4.2, 4.3, 4.5a (identity, configurations, cases, Codex mode and probe), 4.4, 4.5b (runs and report), 4.6. Launcher fixes found by slice 4's plan reviews: [plan](agentic-sdlc-poc/plan_launcher_fixes.md) | 2026-11-07, 2026-11-08 | Agent-run delivery PoC: rules, review launcher and benchmark, changed-files lint; slices 4–8 and #21 (outline) follow the benchmark report. Supersedes PR #26 |
| [poc-4-1-review-prompts](poc-4-1-review-prompts/) | — | Plan under review (slice 4 plan PR) | 2026-11-08 | Slice 4.1 of agentic-sdlc-poc (#38): open mandate first, bounded rechecks, severity order |
| [poc-4-2-review-inputs](poc-4-2-review-inputs/) | — | Plan under review (slice 4 plan PR) | 2026-11-08 | Slice 4.2 of agentic-sdlc-poc (#39): files from the diff, upstream items, evidence computed by tools |
| [poc-4-3-review-records](poc-4-3-review-records/) | — | Plan under review (slice 4 plan PR) | 2026-11-08 | Slice 4.3 of agentic-sdlc-poc (#40): review records written by the launcher and checked by `docs-check` |
| [poc-4-4-stage-checklists](poc-4-4-stage-checklists/) | — | Plan under review (slice 4 plan PR) | 2026-11-08 | Slice 4.4 of agentic-sdlc-poc (#41): stage checklists and blocking criteria from industry review practice |
| [poc-4-5-benchmark](poc-4-5-benchmark/) | — | Plan under review (slice 4 plan PR) | 2026-11-08 | Slice 4.5 of agentic-sdlc-poc (#42): benchmark of the new setup, Opus, Sonnet and Codex |
| [poc-4-6-stage-rules](poc-4-6-stage-rules/) | — | Plan under review (slice 4 plan PR) | 2026-11-08 | Slice 4.6 of agentic-sdlc-poc (#43): seven stages in the slice workflow, handoff of discovered issues |
| [backlog-issues](backlog-issues/) | — | Implemented (PR #19) | 2026-10-31 | Open items of `later_slices.md` moved to GitHub issues (labels `slice`, `user-action`); `AGENTS.md` start-here row and close-out rule |
| [ci-evidence-trace](ci-evidence-trace/) | — | Implemented (PR #11, #12) | 2026-10-31 | Slice 2 of agentic-delivery-process: CI E2E as a required check, no secrets in evidence, static tests and gap gate in the trace model |
| [agentic-delivery-process](agentic-delivery-process/) | — | Implemented (slice 1 of 3; PR #5, #6) | 2026-10-29 | Slice 1 (lean, D20): exact E2E outcomes, key-holder list and `qa-deploy`; decisions D1–D20. Slice 2 became `ci-evidence-trace`; slice 3 is a draft (GitHub issue #16) |
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
