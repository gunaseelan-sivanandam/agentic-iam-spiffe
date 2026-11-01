# Project Status

Last updated: 2026-11-01. Update this page at the end of every slice (see `AGENTS.md`, slice workflow step 4).
Detailed history: [`docs/history/implementation_log.md`](history/implementation_log.md).

## Where the project stands
- **Implemented milestones:** M1, M2, M2.5, M3, M4 (reduced scope), M4a, M4b, M5.
  M5 covers the Codex → Jira MCP path, the `varambu` demo CLI with capiss audit, and the
  full-chain audit trace (`varambu trace`). See the milestone table in [`README.md`](../README.md#milestones).
- **Highest-priority open problems:** key and state isolation.
  - [OPL-005](open_problem_log.md#opl-005-capiss-root-signing-key-is-readable-by-verifiers-and-by-the-rogue-test-container):
    the capiss root signing key is readable in the verifiers, `agent-a` and `rogue`; a forged
    capability was accepted by tool-b's verifier on 2026-10-28.
  - [OPL-006](open_problem_log.md#opl-006-spire-agent-private-key-store-is-readable-by-every-workload-that-mounts-the-agent-directory):
    the SPIRE agent's private key store is readable by every workload.
  - [OPL-007](open_problem_log.md#opl-007-redis-authorization-state-accepts-unauthenticated-writes-from-every-verifier-network):
    Redis authorization state accepts unauthenticated writes.
  - [OPL-008](open_problem_log.md#opl-008-spire-token-init-mounts-the-whole-spire-server-data-directory):
    the SPIRE bootstrap container can read the server's signing keys and datastore.
- **Last slice:** [agentic-delivery-process](slices/agentic-delivery-process/plan.md) slice 2 of 3,
  [`ci-evidence-trace`](slices/ci-evidence-trace/plan.md), is implemented: Increment A (CI E2E as a
  required check, no secrets in evidence) in PR #11, Increment B (static tests, status from the
  register, `Implemented by:`, the gap gate, gate consistency) in PR #12. Slice 1 (exact E2E outcomes,
  `make test-lint`, mutation scoring, `security/invariants.yaml` and `make qa-deploy`) merged in PR #5
  and PR #6.
- **Delivery identity:** agents work on GitHub as the machine user `gunaseelan-agent`; `main`
  requires one approving review, so only the owner can let a PR merge (slice
  [`agent-identity`](slices/agent-identity/plan.md)).
- **Next work** is tracked as [GitHub issues](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues) (label `slice`): the proposed `gate-register`
  ([#13](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/13)), `asset-classification` ([#14](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/14)) and 100% coverage ([#15](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/15)) slices,
  slice 3, review design and orchestration ([#16](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/16)), and the pilot that fixes OPL-005 to
  OPL-008 ([#17](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/17)). Later: the generic capability verifier
  ([brainstorm](slices/m5-generic-verifier-architecture/brainstorm.md), not approved).
- **Future milestones:** M6–M9 as listed in the README.

## Last verification
| Check | Date | Result |
| --- | --- | --- |
| Full E2E suite, clean stack, `make e2e` on `slice/ci-evidence-trace-b` | 2026-10-31 | 120/120 passed; 1 warning (M5-T55 env-gated skip) |
| `make qa-deploy` (image users inspected) and `make qa-evidence` after that run | 2026-10-31 | both PASSED; qa-evidence: validated 119, skipped 1, no secret findings, the qa-deploy report accepted (passed, inspected, digests match) |
| `make qa-quality` (qa-trace in `--mode pr --base origin/main`, unit traceability, unit guard, docs-check, test-lint, qa-deploy) | 2026-10-31 | PASSED; gap gate: 0 new gaps, 25 closed; 113 coverage gaps remain (91 requirements without proof, 18 DD without UT, 4 tests without requirements); REQ-SEC-K1, K2, K4 not proved (known violations OPL-005, -006, -008), D2 not proved (grace until 2027-01-31), the other six and REQ-T-R9 proved statically |
| `make tooling-test` | 2026-10-31 | PASSED (229 pytest, 9 shell) |
| `make unit-mutation` on `slice/ci-evidence-trace-a` | 2026-10-31 | PASSED, 85.34% |
| CI (`.github/workflows/ci.yml`, workflow `CI`, one job per gate) | 2026-10-29 | passing on `main` after the PR #6 merge (`b2448ad`) |

## Work in flight
| Branch | Purpose | State |
| --- | --- | --- |
| `slice/agent-identity` | Agents act as the machine user `gunaseelan-agent`; `main` requires the owner's approval (#20) | PR open |

## Open problems
Full entries in [`docs/open_problem_log.md`](open_problem_log.md).
- **OPL-001** Test-profile Envoy can serve an expired SVID during verified-TLS runs.
- **OPL-002** Traceability links are structurally valid but semantically over-claimed.
- **OPL-003** Compatibility mint endpoint should be retired after root-mint migration.
- **OPL-004** capiss policy hash is static rather than computed from the OPA policy source.
- **OPL-005** capiss root signing key is readable by verifiers and by the rogue test container.
- **OPL-006** SPIRE agent private key store is readable by every workload that mounts the agent directory.
- **OPL-007** Redis authorization state accepts unauthenticated writes from every verifier network.
- **OPL-008** spire-token-init mounts the whole SPIRE server data directory.
- **OPL-009** The delivery pipeline does not resist a deliberately malicious PR (accepted, D18).
- **OPL-010** The SPIRE agent can crash on its first start after a reset, so the suite never starts.

## Open delivery problems
Full entries, root causes and lessons in [`docs/delivery_problem_log.md`](delivery_problem_log.md).
- None. DPL-008 closed on 2026-11-01 (automatic head-branch deletion is on).

## Known gaps and debt
- `M5-T55` (live Jira upstream) only runs with `JIRA_MCP_UPSTREAM_MODE=live`; default runs skip it.
  A skipped test still prints `PASS` in `test_report.log` (the harness has no SKIP status).
- About 20 E2E assertions accept more than one outcome (for example `401|403`, `403|503`, or
  "refused or timed out or no route"), so a broken service can pass as a correct denial. Listed
  for tightening in the [agentic-delivery-process test plan](slices/agentic-delivery-process/test_plan.md).
- `M2-T7` checks a temporary rogue container without the agent mount, not the deployed `rogue`
  (OPL-006).
- Some test titles claim more than their guards check (`M5-T19`, `M5-T21`, `M5-T34`, `M5-T35`,
  `M5-T36`); `docs/test_spec.md` notes each one.
- Functions above the complexity target of 10 (`radon cc services scripts -n C`): 16, the worst being
  `scripts/validate_e2e_evidence.py:main` (32), `scripts/validate_traceability.py:_parse_unit_tests`
  (25), `jira-mcp-gateway do_POST` (23), and capiss `log_mint_decision` (23). The trace validator's
  `main` (63) was split in slice `ci-evidence-trace` B.
- `make qa-trace` scans only `services/` and `scripts/` for DD tags, so `DD-918`, `DD-920`, and
  `DD-921` in the top-level `varambu` script are not indexed.
- **Open decision (user):** mutation testing mutates covered lines only
  (`mutate_only_covered_lines = true` in `setup.cfg`), so untested lines cannot lower the score.
  With `false` the score measured 75.20% against 85.58% (2026-10-29); switching has not been decided.
- Accepted test warnings: `M3.S2-T3` and `M3.S2-T5` (DNS-level isolation instead of TCP refusal).
