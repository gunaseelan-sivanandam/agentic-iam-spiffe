# Project Status

Last updated: 2026-11-07. Update this page at the end of every slice (see `AGENTS.md`, slice workflow step 4).
Detailed history: [`docs/history/implementation_log.md`](history/implementation_log.md).

## Where the project stands
- **Agent-run delivery PoC** on the branch `poc/agentic-sdlc`, kept off `main`: the plan
  [agentic-sdlc-poc](slices/agentic-sdlc-poc/plan.md) (PR #31) approved slices 1–3, which are merged:
  rules (PR #34), the review launcher and benchmark (PR #35, [benchmark report](slices/agentic-sdlc-poc/benchmark_report.md)),
  and the changed-files lint (PR #37). Slice 4 ([#33](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33)) is split into six sub-issues, planned
  together in one plan PR: review prompts (#38), review inputs (#39), review records (#40), stage
  checklists (#41), benchmark (#42), stage rules (#43). Agents taking backlog items the owner did not
  write is [#32](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/32).
- **Open PoC work, in "needed before" order:**
  1. now: slice 4 ([#33](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33), sub-issues #38–#43);
  2. before slice 5: QA-tooling gaps ([#44](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/44)) and publication scanning ([#21](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21));
  3. slice 5 (one real backlog item through the whole cycle) and slice 6 (gates that run shows);
     inputs recorded on 2026-11-09 from the research of agent-first delivery (owner's decision; they
     become issues once the agent account is back):
     - slice 5: design the authoring agents' prompts from 4.4's research; count rounds, re-raises and
       retries from the attempt logs and check the review limits against them; record misses found
       after a final review against the mandate used;
     - slice 6 candidates: a check that each plan's retirement list was carried out, and a check that
       the implementer did not change approved tests; one stated reason per gate threshold;
     - slice 7: what the orchestrator may keep outside the repository; slice 8: whether agents follow
       the rulebook;
  4. before slice 7: untested launcher and benchmark paths ([#45](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/45)); slice 7 itself ([#36](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/36));
  5. slice 8 (evaluation); at the PoC merge into `main`: the reset list ([#46](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/46)).
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
- **Next work** is tracked as [GitHub issues](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues) (label `slice`): the proposed `gate-register`
  ([#13](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/13)), `asset-classification` ([#14](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/14)) and 100% coverage ([#15](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/15)) slices,
  slice 3, review design and orchestration ([#16](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/16)), and the pilot that fixes OPL-005 to
  OPL-008 ([#17](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/17)); publication secret scanning ([#21](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21)), deterministic
  orchestration review limits ([#25](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/25)) and names that say what a file, gate or decision is
  ([#27](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/27)). Later: the generic capability verifier
  ([brainstorm](slices/m5-generic-verifier-architecture/brainstorm.md), not approved).
- **Future milestones:** M6–M9 as listed in the README.

## Last verification
| Check | Date | Result |
| --- | --- | --- |
| Full E2E suite, clean stack, `make e2e` on `poc/slice-3-changed-files-lint` (`89c9cbe`; slice 2 at `642b840` gave the same) | 2026-11-08 | 120/120 passed; 1 warning (M5-T55 env-gated skip); `make qa-deploy` (image users inspected) and `make qa-evidence` PASSED after it |
| `make lint` and `make qa-quality` on slice 3 against `origin/poc/agentic-sdlc`; `make tooling-test` | 2026-11-08 | lint and qa-quality PASSED; tooling tests pass locally except the 9 shell cases, which need `shellcheck` and run in the PR's CI |
| Full E2E suite, clean stack, `make e2e` on `poc/slice-1-rules` (`7ab71c5`) | 2026-11-07 | 120/120 passed; 1 warning (M5-T55 env-gated skip) |
| `make qa-deploy` (image users inspected) and `make qa-evidence` after that run | 2026-11-07 | both PASSED; qa-evidence: validated 119, skipped 1 |
| `make qa-quality` (qa-trace in `--mode pr --base origin/poc/agentic-sdlc`) and `make tooling-test` on `poc/slice-1-rules` | 2026-11-07 | PASSED; gap gate: 0 new gaps, 113 coverage gaps remain; 230 pytest, 9 shell |
| Full E2E suite, clean stack, `make e2e` on `slice/ci-evidence-trace-b` | 2026-10-31 | 120/120 passed; 1 warning (M5-T55 env-gated skip) |
| `make qa-deploy` (image users inspected) and `make qa-evidence` after that run | 2026-10-31 | both PASSED; qa-evidence: validated 119, skipped 1, no secret findings, the qa-deploy report accepted (passed, inspected, digests match) |
| `make qa-quality` (qa-trace in `--mode pr --base origin/main`, unit traceability, unit guard, docs-check, test-lint, qa-deploy) | 2026-10-31 | PASSED; gap gate: 0 new gaps, 25 closed; 113 coverage gaps remain (91 requirements without proof, 18 DD without UT, 4 tests without requirements); REQ-SEC-K1, K2, K4 not proved (known violations OPL-005, -006, -008), D2 not proved (grace until 2027-01-31), the other six and REQ-T-R9 proved statically |
| `make tooling-test` | 2026-10-31 | PASSED (229 pytest, 9 shell) |
| `make unit-mutation` on `slice/ci-evidence-trace-a` | 2026-10-31 | PASSED, 85.34% |
| CI (`.github/workflows/ci.yml`, workflow `CI`, one job per gate) | 2026-11-04 | passing on `main` after the PR #28 merge (`dc4376e`) |

## Work in flight
| Branch | Purpose | State |
| --- | --- | --- |
| `poc/slice-4-plans` | agentic-sdlc-poc slice 4: the plans of its six sub-issues (#38–#43) | Plan reviews running; then one plan PR for the owner |

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
- **OPL-010** The SPIRE agent can crash on its first start after a reset, so the suite never starts ([#30](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/30))

## Open delivery problems
Full entries, root causes and lessons in [`docs/delivery_problem_log.md`](delivery_problem_log.md).
- **DPL-010** Slice 2's reviews accepted answers on the author's word, and closed questions let gaps
  through (preventive actions pending in slice 4, issue #33). DPL-008 closed on 2026-11-04.

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
- Functions above the complexity limit of 10, measured as `make lint` measures it (ruff C901 over
  `services`, `scripts` and `tests`, re-measured on 2026-11-08): 12, the worst being
  `scripts/validate_e2e_evidence.py:main` (19), capiss `resource_mint` (19),
  `scripts/validate_traceability.py:_parse_unit_tests` (18), `scripts/validate_unit_traceability.py:main`
  (17) and `services/shared/enforcement_contract.py:verify_chain_contract` (17). `make lint` fails a
  change that makes one of them worse. (Radon counted 16, with boolean operators.)
- `make qa-trace` scans only `services/` and `scripts/` for DD tags, so `DD-918`, `DD-920`, and
  `DD-921` in the top-level `varambu` script are not indexed.
- **Open decision (user):** mutation testing mutates covered lines only
  (`mutate_only_covered_lines = true` in `setup.cfg`), so untested lines cannot lower the score.
  With `false` the score measured 75.20% against 85.58% (2026-10-29); switching has not been decided.
- Accepted test warnings: `M3.S2-T3` and `M3.S2-T5` (DNS-level isolation instead of TCP refusal).
