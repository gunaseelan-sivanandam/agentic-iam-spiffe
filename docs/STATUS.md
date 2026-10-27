# Project Status

Last updated: 2026-10-27. Update this page at the end of every slice (see `AGENTS.md`, slice workflow step 4).
Detailed history: [`docs/history/implementation_log.md`](history/implementation_log.md).

## Where the project stands
- **Implemented milestones:** M1, M2, M2.5, M3, M4 (reduced scope), M4a, M4b, M5.
  M5 covers the Codex → Jira MCP path, the `varambu` demo CLI with capiss audit, and the
  full-chain audit trace (`varambu trace`). See the milestone table in [`README.md`](../README.md#milestones).
- **Highest-priority open problem:** [OPL-005](open_problem_log.md#opl-005-capiss-root-signing-key-is-readable-by-verifiers-and-by-the-rogue-test-container)
  — the capiss root signing key is readable inside the verifier containers and the rogue test container.
- **Next candidate slices:** a fix slice for OPL-005; the generic capability verifier
  ([brainstorm](slices/m5-generic-verifier-architecture/brainstorm.md), not approved).
- **Future milestones:** M6–M9 as listed in the README.

## Last verification
| Check | Date | Result |
| --- | --- | --- |
| Full E2E suite, clean stack, `main` at `fe86c35` | 2026-10-27 | 120/120 passed; 3 warnings (M3.S2-T3, M3.S2-T5 accepted isolation; M5-T55 env-gated skip) |
| `make qa-evidence` after that run | 2026-10-27 | PASSED (validated 119, skipped 1) |
| `make qa-quality` (qa-trace, unit traceability, unit guard, docs-check) | 2026-10-27 | PASSED; qa-trace reports 122 non-blocking coverage gaps, incl. 87 requirements without E2E |
| CI `unit-trust` | 2026-10-27 | passing on PR #2 and `main` |

## Work in flight
| Branch | Purpose | State |
| --- | --- | --- |
| `docs/consolidation` | Documentation restructure, rulebook, complete E2E spec, `docs-check` in CI ([slice](slices/docs-consolidation/plan.md)) | Increments 1–3 committed; PR to be opened |

## Open problems
Full entries in [`docs/open_problem_log.md`](open_problem_log.md).
- **OPL-001** Test-profile Envoy can serve an expired SVID during verified-TLS runs.
- **OPL-002** Traceability links are structurally valid but semantically over-claimed.
- **OPL-003** Compatibility mint endpoint should be retired after root-mint migration.
- **OPL-004** capiss policy hash is static rather than computed from the OPA policy source.
- **OPL-005** capiss root signing key is readable by verifiers and by the rogue test container.

## Known gaps and debt
- `M5-T55` (live Jira upstream) only runs with `JIRA_MCP_UPSTREAM_MODE=live`; default runs skip it.
  A skipped test still prints `PASS` in `test_report.log` (the harness has no SKIP status).
- Some test titles claim more than their guards check (`M5-T19`, `M5-T21`, `M5-T34`, `M5-T35`,
  `M5-T36`); `docs/test_spec.md` notes each one.
- Functions above the complexity target of 10 (`radon cc services scripts -n C`): 18, the worst being
  `scripts/validate_traceability.py:main` (63), `scripts/validate_e2e_evidence.py:main` (32),
  `jira-mcp-gateway do_POST` (23), and capiss `log_mint_decision` (23).
- `make qa-trace` scans only `services/` and `scripts/` for DD tags, so `DD-918`, `DD-920`, and
  `DD-921` in the top-level `varambu` script are not indexed.
- Accepted test warnings: `M3.S2-T3` and `M3.S2-T5` (DNS-level isolation instead of TCP refusal).
