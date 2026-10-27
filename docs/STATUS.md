# Project Status

Last updated: 2026-10-27. Update this page at the end of every slice (see `AGENTS.md`, Phase 4).
Detailed history: [`docs/history/implementation_log.md`](history/implementation_log.md).

## Where the project stands
- **Implemented milestones:** M1, M2, M2.5, M3, M4 (reduced scope), M4a, M4b, M5.
  M5 covers the Codex → Jira MCP path, the `varambu` demo CLI with capiss audit, and the
  full-chain audit trace (`varambu trace`). See the milestone table in [`README.md`](../README.md#milestones).
- **Next candidate slice:** generic capability verifier
  ([brainstorm](slices/m5-generic-verifier-architecture/brainstorm.md), not approved). Promote it to
  `plan.md` + `test_plan.md` before any tests or code.
- **Future milestones:** M6–M9 as listed in the README.

## Last verification
| Check | Date | Result |
| --- | --- | --- |
| Full E2E suite, clean stack, `main` | 2026-10-27 | 119/120. `M5-T49` fails on a harness timing fault, not product behavior |
| Full E2E suite, clean stack, branch `fix/m5-evidence-harness-hardening` | 2026-10-27 | 120/120; `make qa-evidence` PASSED (validated 119, skipped 1: `M5-T55` needs live Jira) |
| CI `unit-trust` on `main` | 2026-06-30 | passing |
| `make qa-trace` | 2026-10-27 | PASSED; 122 coverage gaps reported (non-blocking), incl. 87 requirements without E2E |

## Work in flight
| Branch | Purpose | State |
| --- | --- | --- |
| `fix/m5-evidence-harness-hardening` | Chain-scoped M5 trace assertions, env-gated `M5-T55` skip in `qa-evidence` | Pushed; PR to be opened |
| `docs/consolidation` | This documentation restructure ([slice](slices/docs-consolidation/plan.md)) | In progress |

## Open problems
Full entries in [`docs/open_problem_log.md`](open_problem_log.md).
- **OPL-001** Test-profile Envoy can serve an expired SVID during verified-TLS runs.
- **OPL-002** Traceability links are structurally valid but semantically over-claimed.
- **OPL-003** Compatibility mint endpoint should be retired after root-mint migration.
- **OPL-004** capiss policy hash is static rather than computed from the OPA policy source.

## Known gaps and debt
- `docs/test_spec.md` does not yet describe the 58 M5 tests (docs-consolidation, Increment 2).
- `M5-T55` (live Jira upstream) only runs with `JIRA_MCP_UPSTREAM_MODE=live`; default runs skip it.
  A skipped test still prints `PASS` in `test_report.log`.
- Functions above the complexity target of 10 (`radon cc services scripts -n C`): 18, the worst being
  `scripts/validate_traceability.py:main` (63), `scripts/validate_e2e_evidence.py:main` (32),
  `jira-mcp-gateway do_POST` (23), and capiss `log_mint_decision` (23).
- `make qa-trace` scans only `services/` and `scripts/` for DD tags, so `DD-918`, `DD-920`, and
  `DD-921` in the top-level `varambu` script are not indexed.
- Accepted test warnings: `M3.S2-T3` and `M3.S2-T5` (DNS-level isolation instead of TCP refusal).
