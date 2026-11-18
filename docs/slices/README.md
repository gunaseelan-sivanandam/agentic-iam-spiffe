# Slice Bundles

A slice bundle is the review record for one milestone or security-relevant change: the agreed design,
requirement and architecture changes, hidden-state decisions, the UT/E2E proof plan, and the user's
decision page, which holds everything that needs the user and which the PR body links.
The workflow that produces and closes a bundle is defined in [`AGENTS.md`](../../AGENTS.md#slice-workflow).

- New bundle: copy [`_template/`](_template/) to `docs/slices/<slice-id>/` (`plan.md`, `test_plan.md`
  and `decisions.md`).
- Once a slice is implemented its bundle is a **frozen record**. Do not edit it to match later
  reality; record later changes in a new slice or in `docs/history/implementation_log.md`.
- Add a row to the index below when a bundle is created, and update its status when it closes.

## Index

| Slice | Milestone | Status | Dates | Notes |
| --- | --- | --- | --- | --- |
| [agentic-sdlc-poc](agentic-sdlc-poc/) | — | Slices 1–3 merged (PR #34, #35, #37); slice 4 split into the six bundles below, built in this order: 4.1, 4.2, 4.3, 4.5a (identity, configurations, cases), 4.4, 4.5b (runs and report), 4.6; then the owner's rounds 2 and 3 on the slice 4 branch, round 3 (2026-11-17) built and measured, then decision concern 18 decided by the owner (option (b)) and built; its review unit `round-3` ended after round 2 (approvable), so round 3 is built, measured and reviewed; round 4 (2026-11-17, from the owner's decisions of that day) built and measured: discovered issues 56, 57 and 60 fixed, the recheck and final mandates shipped, its review unit `owner-decisions-3` ended after round 2 (approvable, every answer accepted); the initial mandate shipped by the owner's decision 8 (2026-11-18), its review unit `owner-decisions-4` ended after round 1 (approvable, one low finding fixed); the owner's decisions of 2026-11-18 recorded (decision concern 19 decided, growth proposal 12 withdrawn, discovered issue 53 closed); open before slice 4 closes: decision concern 16, the push and the final PR, the final review run again after the owner's reset, the owner's actions of decisions 3 and 4 ([decision page](agentic-sdlc-poc/slice_4_decisions.md)). Launcher fixes found by slice 4's plan reviews: [plan](agentic-sdlc-poc/plan_launcher_fixes.md) | 2026-11-07, 2026-11-08 | Agent-run delivery PoC: rules, review launcher and benchmark, changed-files lint; slices 4–8 and #21 (outline) follow the benchmark report. Supersedes PR #26 |
| [poc-4-1-review-prompts](poc-4-1-review-prompts/) | — | Plan merged (PR #48); implemented on the slice 4 branch, in review; final PR pending | 2026-11-08, 2026-11-09 | Slice 4.1 of agentic-sdlc-poc (#38): open mandate first, bounded rechecks, severity order |
| [poc-4-2-review-inputs](poc-4-2-review-inputs/) | — | Plan merged (PR #48); implemented on the slice 4 branch, in review; final PR pending | 2026-11-08, 2026-11-09 | Slice 4.2 of agentic-sdlc-poc (#39): files from the diff, upstream items, evidence computed by tools |
| [poc-4-3-review-records](poc-4-3-review-records/) | — | Plan merged (PR #48); implemented on the slice 4 branch, in review; final PR pending | 2026-11-08 | Slice 4.3 of agentic-sdlc-poc (#40): review records written by the launcher and checked by `docs-check` |
| [poc-4-4-stage-checklists](poc-4-4-stage-checklists/) | — | Plan merged (PR #48); implemented on the slice 4 branch, critiqued, in review; final PR pending | 2026-11-08, 2026-11-10 | Slice 4.4 of agentic-sdlc-poc (#41): stage checklists and blocking criteria from industry review practice |
| [poc-4-5-benchmark](poc-4-5-benchmark/) | — | Plan merged (PR #48); 4.5a (mechanics) and 4.5b (runs, report) implemented on the slice 4 branch, in review; final PR pending | 2026-11-08 | Slice 4.5 of agentic-sdlc-poc (#42): screening study of the review setup and the mandate wording |
| [poc-4-6-stage-rules](poc-4-6-stage-rules/) | — | Plan merged (PR #48); implemented on the slice 4 branch, in review; final PR pending | 2026-11-08 | Slice 4.6 of agentic-sdlc-poc (#43): seven stages in the slice workflow, handoff of discovered issues |
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
