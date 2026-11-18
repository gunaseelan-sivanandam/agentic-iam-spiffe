# Project Status

Last updated: 2026-11-18. Update this page at the end of every slice (see `AGENTS.md`, slice workflow, handoff).
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
  1. now: slice 4 ([#33](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33), sub-issues #38–#43), implemented on
     the branch `poc/slice-4-implementation` for one final PR: 4.1 to 4.6 implemented and reviewed; 4.5b's
     benchmark ran (57 of 60 calls, then 76 under a budget raised to 85, then 80 of a hard stop of 80 in round 2,
     82 of 85 since the owner confirmed the budget of 85 on 2026-11-16, 86 of 95 in round 3, and 105 of 120 in round 4;
     [report](slices/poc-4-5-benchmark/benchmark_report.md)); one dry slice ran; the final review ended after
     round 2; the owner's growth of 2026-11-13 (rejections read like fixes, a `searched` list, the checklist
     question on findings) is implemented and reviewed (unit `growth`); the owner's decisions of 2026-11-13 on
     decision concerns 2, 3, 4, 7, 8 and 10 are implemented (small slices, the decision page, a second recheck
     case, a severity measurement that came out worse, so nothing is adopted) and reviewed (unit
     `owner-decisions`, ended after round 2). Round 2, from the owner's findings on review severity of 2026-11-14
     (R2-1 to R2-10), is implemented: blocking, high and medium findings are fixed, a rejection cites a checkable
     fact, one dispute round, a fix adds no mechanism and the review prompt asks it, a recheck sees the process
     files the fixes changed and quotes what each rejection rests on; the benchmark is re-scored with a medium match
     counted, and two more recheck cases ran. Its review (unit `round-2`) ran round 1 (not approvable: 2 high, 2
     medium, 3 low, all answered: 5 fixed, 1 to the owner as decision concern 16, 1 rejected); its recheck, round 2,
     was approvable and the review ended (1 new low, fixed). On 2026-11-16 the owner decided decision concerns 11 and 13,
     and both are implemented: the review prompt and `AGENTS.md` count a repeated step and a kept copy of a fact as
     mechanisms, and a fix that adds one is re-raised, not filed as a simpler alternative; RC-3, run again on both
     recheck wordings, was re-raised by both (one run each, on the case the wording was written from); the stage-B
     hard stop is the confirmed 85. Their review unit `owner-decisions-2` ran round 1 (approvable: 4 medium, 2 low,
     all answered): an unapproved mechanism is now a defect of at least medium, the mechanism definition lost its
     example "again after every push" (RC-3's runs had it, so the shipped wording is unmeasured), the benchmark's
     leak search reads the whole prompt, and decision concern 17 (whether good fixes are now re-raised, and running
     RC-3 and RC-2 under the shipped wording) goes to the owner; its recheck was approvable and the review ended.
     Round 3, approved by the owner on 2026-11-17 (R3-1 to R3-4), is built and measured: a recheck reviews only the
     commits since the reviewed round, quotes what it was shown from the files each answer names or cites, and is told
     that what an existing rule requires of a fix is not an added mechanism; the plan list asks the fix rule and blocks
     a false small-slice claim. Of its measurements, the replays of the three rechecks that failed the old read check
     did not meet their criterion (the `mechanics` replay failed the new recheck: decision concern 18), and RC-1
     to RC-4 on `recheck-A` met theirs on confirmed verdicts. The owner decided decision concern 18 as option (b) the
     same day, and it is built: the lines of the change's diff a review was shown count as seen lines of their files;
     the `mechanics` replay then ran once more and passed (completed, approvable, H1 re-raised; discovered issues 56 to
     59). Its review unit `round-3` ended after round 2: round 1 was approvable (3 medium, 3 low; F1, F2, F3 and F6
     fixed, F1 by the owner's decision "Rechecks only", F4 and F5 rejected), and the recheck, the first under round 3's
     whole recheck, was approvable (all six answers accepted with quotes; one new low, N1, fixed); the brief is rebuilt
     on the decision page. So round 3 is built, measured and reviewed.
     Round 4, from the owner's decisions of 2026-11-17 (decisions 1, 3, 4 and 5 accepted, decision 2 revisited; R4-1
     to R4-6), is built and measured: discovered issues 56, 57 and 60 are fixed, tests first; the research record of
     the mandates is written; R4-4's 19 calls ran (105 of 120) and were confirmed blind. The recheck wording met its
     criterion, and the launcher ships it with the final wording; `AGENTS.md`'s final review no longer states 4.1's
     question. The initial wording raised one more false alarm than the launcher's (8 against 7 in 4 no-defect
     reviews) while detecting 10 of 11 against 8, so it did not meet its criterion; the owner decided on 2026-11-18 to
     ship it anyway (decision 8: "yes, ship the R4-1 initial mandate and review it"), so the launcher ships all three of
     round 4's mandates; that change's review unit `owner-decisions-4`, the first live review under the new initial
     mandate, ended after round 1 (approvable; one low finding, F1, fixed). Round 4's review unit
     `owner-decisions-3` ended after round 2: round 1 was approvable (2 medium, 3 low; F1, F2, F4 and F5 fixed, among
     them DPL-015 for discovered issue 56; F3 rejected), and the recheck, the first under round 4's recheck mandate,
     was approvable (all five answers accepted, no new finding); the brief is rebuilt on the decision page. So round 4
     is built, measured and reviewed. Open for the owner before slice 4 closes, on the decision page: decision
     concerns 16 (R2-9's blind verdicts) and 19 (the `open+list` baseline ran
     under an older CLI); growth proposal 12 (resuming a review that failed the read check); discovered issue 53, open
     in part, and discovered issues 62 to 65, recorded; and the owner's actions of decisions 3 (recreate the hidden
     issues, about 2026-11-23) and 4 (remove the personal copy of the grill-me skill), outside the repository. Then
     the push and the final PR, which the owner does, since the agent account cannot write to GitHub.
     Progress and the owner's decisions: [`slice_4_decisions.md`](slices/agentic-sdlc-poc/slice_4_decisions.md);
     Next, before slice 5: a slice of author prompts and their benchmark (owner, 2026-11-09: "let's
     continue this slice for just review, after this let's run a new slice of author prompts and
     benchmark them, since the review prompts are finalized that would give us bit of data for
     selecting good author prompts");
  2. before slice 5: QA-tooling gaps ([#44](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/44)) and publication scanning ([#21](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21));
  3. slice 5 (one real backlog item through the whole cycle) and slice 6 (gates that run shows);
     inputs recorded on 2026-11-09 from the research of agent-first delivery (owner's decision; they
     become issues when they can be opened again):
     - slice 5: count rounds, re-raises and retries from the attempt logs and check the review limits
       against them (the authoring prompts move to the author-prompts slice); record misses found
       after a final review against the mandate used;
     - slice 6 candidates: a check that each plan's retirement list was carried out, and a check that
       the implementer did not change approved tests; one stated reason per gate threshold;
     - slice 7: what the orchestrator may keep outside the repository; slice 8: whether agents follow
       the rulebook, and, if the owner wants it, whether the stage lists help (reviews with and
       without them);
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
| `make docs-check`, `make tooling-test` on `poc/slice-4-implementation` (round 4's review handoff on `e6f78d3`: the review unit `owner-decisions-3` ended, the brief rebuilt; docs only) | 2026-11-18 | PASSED; 1000 pytest (with a scratch shellcheck), 9 shell. Not run: the E2E suite and the other gates (no service, policy, compose, harness, script or CI file changed) |
| `make docs-check`, `make qa-trace`, `make lint`, `make tooling-test` on `poc/slice-4-implementation` (round 4's handoff on `1f905a9`: discovered issues 56, 57 and 60 fixed, R4-4 measured, the recheck and final mandates shipped; docs only); at `1f905a9`, `make tooling-test`, `make docs-check`, `make lint` and `make gate-consistency`, as the commit records | 2026-11-18 | PASSED; qa-trace: 0 new gaps, 113 coverage gaps remain; lint 0 new or worsened; 1000 pytest (with a scratch shellcheck), 9 shell. Not run: the E2E suite (no service, policy, compose, harness or CI file changed; CI runs it on the PR) |
| `make docs-check`, `make qa-trace`, `make lint`, `make test-lint`, `make unit-guard-check`, `make qa-deploy`, `make tooling-test` on `poc/slice-4-implementation` (round 3's handoff on `faa6df4`: the review unit `round-3` ended, the brief rebuilt; docs only) | 2026-11-17 | PASSED; qa-trace: 0 new gaps, 113 coverage gaps remain; lint 0 new or worsened; unit guard 357; qa-deploy 18 known violations, 22 warnings; 981 pytest (with a scratch shellcheck), 9 shell. Not run: the E2E suite and gate-consistency (no service, policy, compose, harness or CI file changed) |
| `make lint`, `make docs-check`, `make qa-trace`, `make tooling-test` on `poc/slice-4-implementation` (`5627de7`, decision concern 18 built), as the build reported; `make qa-trace` and `make docs-check` rerun on its records | 2026-11-17 | PASSED; qa-trace: 0 new gaps, 113 coverage gaps remain. Not run: the E2E suite (no service, policy, compose, harness or CI file changed) and gate-consistency |
| `make tooling-test` on `poc/slice-4-implementation` (`fa7953f`, round 3 built and measured, in a clean worktree); `make qa-trace`, `make docs-check`, `make lint`, `make test-lint`, `make unit-guard-check`, `make qa-deploy` on round 3's records | 2026-11-17 | PASSED; 963 pytest (with a scratch shellcheck; 2 pre-existing deprecation warnings), 9 shell; qa-trace: 0 new gaps, 113 coverage gaps remain; lint 0 new or worsened; unit guard 357; qa-deploy 18 known violations, 22 warnings. Not run for round 3: the E2E suite (no service, policy, compose, harness or CI file changed) and gate-consistency |
| `make qa-quality` (qa-trace in `--mode pr --base origin/poc/agentic-sdlc`, docs-check, test-lint, qa-deploy), `make tooling-test`, `make lint`, `make unit-guard-check`, `make gate-consistency` on `poc/slice-4-implementation` (`f22bb89`, the fixes to round 1 of the review of the owner's decisions of 2026-11-16, in a clean worktree; the commits after it change only `docs/`) | 2026-11-16 | PASSED; gap gate: 0 new gaps, 113 coverage gaps remain; qa-deploy 18 known violations, 22 warnings; 932 pytest (with a scratch shellcheck; 2 pre-existing deprecation warnings), 9 shell; lint 0 new or worsened. The E2E suite was not run again: no service, policy, compose, harness or CI file changed |
| `make qa-quality` (qa-trace in `--mode pr --base origin/poc/agentic-sdlc`, docs-check, test-lint, qa-deploy), `make tooling-test`, `make lint`, `make unit-guard-check`, `make gate-consistency` on `poc/slice-4-implementation` (`03c02c0`, the owner's decisions of 2026-11-16; the commits after it change only `docs/`) | 2026-11-16 | PASSED; gap gate: 0 new gaps, 113 coverage gaps remain; qa-deploy 18 known violations, 22 warnings; 929 pytest (with a scratch shellcheck), 9 shell; lint 0 new or worsened. The E2E suite was not run again: no service, policy, compose, harness or CI file changed |
| `make qa-quality` (qa-trace in `--mode pr --base origin/poc/agentic-sdlc`, docs-check, test-lint, qa-deploy), `make tooling-test`, `make lint`, `make unit-guard-check`, `make gate-consistency` on `poc/slice-4-implementation` (`1f224d1`, round 2 with the fixes of its review's round 1, the answers and the brief's fix) | 2026-11-14 | PASSED; gap gate: 0 new gaps, 113 coverage gaps remain; qa-deploy 18 known violations, 22 warnings; 927 pytest (with a scratch shellcheck), 9 shell; lint 0 new or worsened. The E2E suite was not run again: round 2 changed no service, policy, compose, harness or CI file |
| Full E2E suite, clean stack, `make e2e` on `poc/slice-4-implementation` (`11667c5`) | 2026-11-10 | 120/120 passed; 1 warning (M5-T55 env-gated skip); `make qa-evidence` PASSED (validated 119, skipped 1) |
| `make qa-quality` (and qa-trace in `--mode pr --base origin/poc/agentic-sdlc`), `make lint`, `make tooling-test` on `poc/slice-4-implementation` | 2026-11-10 | PASSED; gap gate: 0 new gaps; 764 pytest (with a scratch shellcheck), 9 shell |
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
| `poc/slice-4-implementation` | agentic-sdlc-poc slice 4: the six sub-issues (#38–#43), on the plans merged with PR #48 | Implemented and reviewed, local; the owner's decisions of 2026-11-13 implemented and reviewed; round 2 (R2-1 to R2-10, 2026-11-14) implemented, its review unit `round-2` ended after round 2 (approvable; decision concern 16 to the owner); the owner's decisions of 2026-11-16 (decision concerns 11 and 13) implemented, their review unit `owner-decisions-2` ran round 1 (approvable; F1 to F3 fixed, decision concern 17 to the owner) and ended after its recheck, round 2; round 3 (R3-1 to R3-4, 2026-11-17) implemented and measured, then decision concern 18 decided by the owner (option (b)) and built, and the `mechanics` replay run once more (passed); its review unit `round-3` ended after round 2 (approvable; F1, F2, F3 and F6 fixed, F4 and F5 rejected; the recheck's one new low fixed); the owner's decisions of 2026-11-17 recorded (decisions 1, 3, 4 and 5 accepted, decision 2 revisited as round 4); round 4 (R4-1 to R4-6) built and measured: discovered issues 56, 57 and 60 fixed, the recheck and final mandates shipped; its review unit `owner-decisions-3` ended after round 2; the initial mandate shipped by the owner's decision 8 (2026-11-18), its review unit `owner-decisions-4` ended after round 1 (approvable; one low finding, fixed); open for the owner: decision concerns 16 and 19, growth proposal 12, discovered issues 62 to 65 as recorded, the actions of decisions 3 and 4; one final PR into `poc/agentic-sdlc` when the owner pushes |

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
  through; its preventive actions are on the slice 4 branch, closing it when slice 4 merges.
- **DPL-011** Slice 2's launcher and the secret check broke on slice 4's parallel plan reviews; fixed with
  PR #48 and on the slice 4 branch, closing it when slice 4 merges.
- **DPL-012** Slice 4's implementation run made claims and checks that did not hold; all fixed on the slice
  4 branch, closing it when slice 4 merges.
- **DPL-013** Review severity decided what got fixed, a rejection could stand on the author's word, and fixes
  grew the process; round 2's rules are on the slice 4 branch, closing it when slice 4 merges; RC-3's miss is
  answered by decision concern 13's wording (both rechecks re-raised it, one run each, on the case the wording was
  written from, under a first wording whose example has since been removed); in round 3, under the shipped wording
  and R3-3's carve-out, `recheck-A` re-raised RC-3 and accepted RC-2's fix that adds tests (one run each); open:
  whether the wording holds beyond RC-3, and who confirms R2-9's new matches and RC-3's re-raises (decision concern
  16).
- **DPL-014** A blind-confirmation token of the benchmark was not tied to its result line, so a rerun under a new
  prompt could have inherited an earlier verdict; fixed on the slice 4 branch before round 3's runs, closing it when
  slice 4 merges.
- DPL-008 closed on 2026-11-04.

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
