# Independent plan review — agentic-delivery-process

Manual run under plan review note 8; the CI `plan-review` job does not exist yet, so this report is
produced on the author's machine and is **not** bound the way D17 requires. Anyone can reproduce a
round with the command below.

| Round | Date | Reviewer | Model | Inputs (SHA-256 of plan.md / test_plan.md) |
| --- | --- | --- | --- | --- |
| 1 | 2026-10-28 | Codex CLI 0.142.5, `codex exec --sandbox read-only --ephemeral` | `gpt-6.1-sol` (the configured `gpt-5.5` is refused for a ChatGPT login) | `09770c43f829…` / `482cf084ff85…` at `c21a934` |

Reviewer inputs: the repository (read-only), the grill-me decision log and the compose inventory
(env var names only). The prompt forbids reading the author's session data; the sandbox restricts
writes, not reads, so that is an instruction, not an enforced boundary.

Command (from the repository root; `PROMPT.md`, the decision log and the inventory are in the
input directory):

```bash
codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral -C . --add-dir <inputs> -o round.md - < <inputs>/PROMPT.md
```

## Round 1 — author's resolutions
Every finding was checked against the code before it was accepted. All 20 are accepted; none is
answered with "no change".

| Finding | Severity | Resolution | Where |
| --- | --- | --- | --- |
| PR-01 PR code controls the runner that judges it | blocker | Confirmed: `rogue-tests` mounts the Docker socket and `..:/repo` read-write. New job model: static `qa-deploy` before bring-up; `main`'s harness runs existing tests while no PR container holds the socket or a writable checkout; Docker steps move to a controller from `main`; `verify` on a fresh runner. The residual (PR-run steps can fabricate their own results) is stated, with full-slice review and nightly recompute. | plan "CI trust model", REQ-SEC-K8, retirement; T-44 |
| PR-02 gate job cannot run execution checks | blocker | Split into `gate` (no PR code), `execute`, `verify`, `candidate-gate`; candidate gate code must pass `main`'s negative controls. | plan "CI trust model"; T-16, T-20 |
| PR-03 M5-T21 pins an impossible outcome | blocker | Confirmed (`canonicalize_resource` returns None, root mint answers 400 `bad_request`/`res` before OPA). Row corrected. | test_plan 1A table |
| PR-04 check-removal fixture already fails | blocker | Confirmed: old M3.S2-T4 asserts the reason. T-35 now uses a runner fixture plus the 503→403 status mutant, which the old test survives. | T-35 |
| PR-05 mutation denominator hides untested mutants | blocker | Confirmed in `scripts/mutation_gate.py`. New scoring rule; retirement of the subtraction; controls. | plan D17 "Mutation scoring"; T-41 |
| PR-06 runtime proofs have no test rows | major | Matrix assertion templates with holder-positive, non-holder, scan-sanity, socket, exception, fault-injection and S1 rows. | test_plan "Runtime invariant matrix" |
| PR-07 asset scope omits trust roots and sockets | major | REQ-SEC-K4 (SPIRE server keys, datastore), K5 (admin socket, `spire-token-init` exception), K6 (join tokens), K7 (workload keys), K8 (Docker socket). | plan Requirements |
| PR-08 pipeline credentials and merge authority | major | Agent machine identity, approving review required on `main`, credential table, hooks refuse credential reads; D15 amended. | plan "Pipeline credentials"; P-31, P-32 |
| PR-09 S1 leaves state families unspecified | major | Operation contract per principal and key family, including the negative-cost script case. | REQ-SEC-S1; matrix S1 row |
| PR-10 register consistency checks IDs only | major | `Holders:`/`Operations:` in each REQ-SEC compared with the register. | plan Requirements; T-12 |
| PR-11 compose does not establish runtime user | major | Effective user from image and running processes; unknown = root. | REQ-SEC-D2; T-11 |
| PR-12 approved contract data vs main-only rule | major | Executable policy from `main`; contract data from the PR only if it equals the approved `contract_delta.yaml`. | plan "CI trust model"; T-43 |
| PR-13 exceptions lack scope and deadline | major | Exact tuple, absolute expiry 2026-12-31 (for approval), void on OPL close, changes only via contract delta. | review note 1, 10; T-13 |
| PR-14 role scopes and counts from mutable records | major | Phase commits, clean-tree check, append-only ledger branch `run/<slice-id>` read by CI; ruleset on `run/*`. | plan Increment 2; P-29, P-30 |
| PR-15 review reports without provenance | major | Authoritative review is the CI `plan-review` job with input and output digests; local runs advisory. This report is such a local run and says so. | plan D17; P-33 |
| PR-16 provenance can be relabelled | major | Ancestor, artifact and assertion checks for `probe@` and `existing@`. | T-42 |
| PR-17 cap contradicts full-slice lane | major | The cap selects the lane only. | plan Lanes; T-14 |
| PR-18 ratchet permits decreases | major | Decrease only by an approved contract delta; +5 raise checked at close; ceiling and history tests. | plan D17; T-37 |
| PR-19 calibration accepts zero detection | major | Floor: every blocker-class seed and 80% of the rest (for approval). | plan D17, review note 11; P-26 |
| PR-20 plan exempts itself | major | Derivation appendix for this slice's rows; boundary-success rows for every stop limit and expiry. | test_plan "Derivation appendix"; P-5, P-13–P-15, P-28 |

## Round 1 — reviewer report (verbatim)

### Round 1 report

#### Findings

##### PR-01 [blocker] PR code can control the runner that judges its evidence
- Lens: security
- Where: docs/slices/agentic-delivery-process/plan.md:320–335; test_plan.md:179–181
- Finding: Checking out gates from `main` does not protect them from the PR-controlled harness. That harness has the runner’s Docker socket and a writable repository mount. It can create another container with host mounts, alter the trusted checkout, or fabricate evidence carrying the correct current SHA and run ID.
- Evidence: `compose/spiffe.compose.yml:98–105` gives `rogue-tests` both mounts; its Dockerfile executes the PR’s harness. T-29 rejects mismatching identifiers but does not exercise fabrication with matching identifiers.
- Why it matters: A PR can produce authoritative green evidence without proving the deployed system’s behavior. Read-only socket mounting does not restrict Docker API operations.
- Suggested resolution: Isolate untrusted execution from the verifier, verifier checkout, and artifact publication credentials. Add a negative control where the harness attempts host access, verifier modification, and publication of fabricated current-run evidence.

##### PR-02 [blocker] The gate job cannot perform its promised execution checks
- Lens: consistency
- Where: docs/slices/agentic-delivery-process/plan.md:224–237, 326; test_plan.md:170–179
- Finding: The gate job “never executes PR code,” but reproduction-on-base must execute the PR’s regression test, changed-line coverage must execute candidate code, and mutation must execute modified candidate code. No separate authoritative execution job is assigned these duties.
- Evidence: T-16, T-17 and T-34 require execution. The E2E job is described as running services and the E2E harness; candidate tooling tests are explicitly advisory.
- Why it matters: Either the stated trust boundary is violated or mandatory checks are omitted. T-20 also expects an always-passing candidate gate to fail, although running the old gate only establishes its lane.
- Suggested resolution: Assign each execution check to an isolated authoritative job, specify its trusted controller, and require candidate gate tests before candidate gates can become authoritative.

##### PR-03 [blocker] M5-T21 pins an outcome the current implementation cannot produce
- Lens: consistency
- Where: docs/slices/agentic-delivery-process/test_plan.md:100, 276–278
- Finding: The plan requires 403/`denied`/`policy` and says this payload passes validation. It does not.
- Evidence: `M5_T21_test` sends `aud=jira-tool` with `res=jira-mcp:/project:IAM`. `canonicalize_resource` dispatches to the Jira-tool resource validator (`services/capability-issuer/app.py:300–305`), which rejects that resource. `root_mint` returns 400/`bad_request`/`res` before calling OPA (`:723–747`). Evaluating the selected canonicalization functions confirmed `None`.
- Why it matters: Increment 1A must escalate or change runtime validation merely to satisfy a test-precision change.
- Suggested resolution: Correct the approved row to the existing validation outcome, or explicitly approve a different stimulus that reaches the intended policy decision.

##### PR-04 [blocker] The check-removal calibration fixture already fails before tightening
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/test_plan.md:187
- Finding: T-35 requires pre-1A `M3.S2-T4` to survive removal of `opa_unavailable`. Its existing reason assertion already detects that removal.
- Evidence: Both the current harness and `20c074e` assert `.error == denied` and `.reason == opa_unavailable` immediately after accepting `403|503`. Removing the issuer’s unavailable branch falls through to a different denial or otherwise changes the response; accepting two statuses does not waive the reason assertion.
- Why it matters: The proposed negative control cannot demonstrate the claimed improvement and is infeasible as specified.
- Suggested resolution: Specify the exact mutant and demonstrate that the complete old test survives it while the complete tightened test kills it.

##### PR-05 [blocker] Mutation percentages can hide almost entirely untested mutants
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/plan.md:133–135; test_plan.md:171, 186, 189
- Finding: The new thresholds have no denominator-integrity test. The existing scoring code excludes both `skipped` and `no_tests`, and mutation generation currently excludes uncovered lines.
- Evidence: `scripts/mutation_gate.py:26–41` subtracts those categories. A read-only synthetic invocation with 100 total, one killed and 99 `no_tests` printed `PASSED (score=100.00%, required=80.00%)`. `setup.cfg:15` sets `mutate_only_covered_lines = true`.
- Why it matters: The ratchet can report excellent adequacy while nearly every generated mutant lacks a test.
- Suggested resolution: Define denominator and collection rules, reject unexplained skipped/untested mutants, and add controls for empty selection, missing modules, and incomplete mutation runs.

##### PR-06 [major] Runtime security proofs have no reviewable test rows
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/plan.md:219–223; test_plan.md:140–155, 258–259
- Finding: The invariant matrix is promised without expected outcomes, stimuli, positive controls, or fault-injection procedures for K1/K2/K3/S1. T-27 proves row generation and deletion detection, not confinement. The pilot later authors K1/K2/S1 rows even though the matrix arrives in 1B.
- Evidence: The only detailed deployment rows are tooling tests. There is no row requiring a real key to exist in its authorized holder, matching public-key provenance, rejection of reads from a wrong path/container, or an authenticated Redis operation that must remain allowed.
- Why it matters: A complete-looking matrix can pass because keys were never generated, the wrong container was inspected, or expected files were renamed.
- Suggested resolution: Approve the matrix’s assertion templates and controls now, including holder-positive checks, scan failures, wrong paths, missing assets, and each exception’s expected result.

##### PR-07 [major] The asset scope omits existing trust roots and authority-bearing sockets
- Lens: security
- Where: docs/slices/agentic-delivery-process/plan.md:101, 169–182
- Finding: The proposed requirements omit SPIRE server signing state, registration data and administrative socket, join tokens, and each workload’s issued private key. Docker socket authority is also not represented as an asset with permitted operations.
- Evidence: `spire/server/server.conf:19–26` names the datastore and disk key store; `:11` names the administrative socket. `spire-token-init` mounts the entire server directory and uses that socket. Workload entrypoints write SVID private keys. The supplied inventory identifies Docker socket holders.
- Why it matters: Another mount can disclose a different signing root or grant identity-administration authority while satisfying every proposed named confinement requirement.
- Suggested resolution: Enumerate these assets and their allowed holders/operations, including explicitly trusted administrative exceptions, before approving the register’s scope.

##### PR-08 [major] The pipeline’s own credentials and merge authority are outside its threat model
- Lens: security
- Where: docs/slices/agentic-delivery-process/plan.md:64, 68, 273–286, 337–338
- Finding: The pipeline uses the owner’s Codex login and personal `gh` account but specifies no credential boundary between implementer, reviewers, notification sender, and merge authority. “Never merges” remains an instruction.
- Evidence: D15 waits for `gh` to use the personal account; review note 6 uses the user’s login. The process-state table does not inventory these credentials. Architecture ARCH-033 already documents a credential symlink used by demo sessions.
- Why it matters: An implementer can potentially exercise the same identity that D8 treats as the approving human, or expose credentials through reviewer inputs and run artifacts.
- Suggested resolution: Inventory pipeline credentials and permissions, isolate them from untrusted execution, and make owner approval distinguishable from agent actions. Test attempted credential access and agent-initiated approval/merge.

##### PR-09 [major] Authorization-state integrity leaves critical state families unspecified
- Lens: security
- Where: docs/slices/agentic-delivery-process/plan.md:177–178; test_plan.md:258–259
- Finding: S1’s concrete restriction covers budget creation and consumption but gives no operation-level contract for rate state, discovery registry entries, or issuer-provenance markers.
- Evidence: `docs/architecture.md:291–306` assigns distinct writers to registry, request-rate, mint-rate and `m4:capiss_minted:*` state. The latter marker participates in authorization. Existing consumer Lua uses `DECRBY`; allowing that command does not itself prevent a negative decrement from increasing a budget.
- Why it matters: Rejecting unauthenticated access and direct budget creation can pass while an authenticated verifier funds itself, resets limits, or fabricates provenance.
- Suggested resolution: Define permitted operations and key families per principal, then require adversarial command/script tests and allowed-operation twins in the pilot contract.

##### PR-10 [major] Register consistency tests check IDs rather than invariant meaning
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/test_plan.md:148, 150–153
- Finding: T-12 checks only that requirement IDs and register entries exist. It does not reject a register that names `tool-b` as an authorized private-key holder despite K1.
- Evidence: Asset discovery fails only outside the register’s holder list. T-26 tests a misleading mount classification, but not an incorrectly expanded holder list.
- Why it matters: Static allowlisting and content discovery can agree with each other while both contradict the approved confinement requirement.
- Suggested resolution: Make the approved holder/operation constraints mechanically comparable and add a negative control that expands K1’s holders without changing its requirement.

##### PR-11 [major] Compose facts do not establish the effective runtime user
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/plan.md:60; test_plan.md:141–147
- Finding: T-8 extracts `docker compose config`, which cannot establish an omitted user inherited from an image or an entrypoint’s eventual process identity. T-11 does not cover either case.
- Evidence: All 23 services omit Compose `user`; several Dockerfiles explicitly set `USER root`, while others inherit image defaults.
- Why it matters: A service can be classified as non-root or unknown using incomplete configuration facts, then run as root.
- Suggested resolution: Define how effective image/runtime identity is established, fail closed on unknown identity, and test image-default changes, named users, UID zero and entrypoint behavior.

##### PR-12 [major] Approved contract updates conflict with the main-only configuration rule
- Lens: consistency
- Where: docs/slices/agentic-delivery-process/plan.md:59, 224–234, 324–325
- Finding: The PR checkout may never supply gate configuration, yet approved implementation PRs introduce `invariants.yaml`, kind entries, thresholds and decision-point mappings. The plan never specifies which approved candidate data the trusted gate may consume.
- Evidence: The relevant files are planned but absent today. D9 also makes later changes to them full-slice changes; routing a change does not explain how its new approved configuration is validated before merge.
- Why it matters: Strictly following the rule rejects legitimate approved changes; relaxing it informally permits a PR to weaken its own inputs.
- Suggested resolution: Separate trusted executable policy from candidate contract data and bind permitted candidate changes to an immutable approved plan revision. Test both approved and unapproved changes.

##### PR-13 [major] Known-violation exceptions lack precise scope and an independent deadline
- Lens: security
- Where: docs/slices/agentic-delivery-process/plan.md:309–313; test_plan.md:143, 149
- Finding: An exception requires an OPL ID and expiry, but no exact service, asset, access operation or observed violation tuple. “Expiry at the pilot’s close” is not an independently enforceable deadline.
- Evidence: T-13 tests missing and past expiry only. There is no control for broadening an exception, adding another holder under the same OPL, renewing it indefinitely, or leaving it after OPL closure. T-10 does not assert the S1 exception’s behavior.
- Why it matters: The exception needed to bootstrap the gates can also suppress a new key disclosure or remain effective indefinitely.
- Suggested resolution: Approve exact exception tuples and absolute deadlines; reject expansion, unauthorized renewal and closed-OPL exceptions. Test each boundary.

##### PR-14 [major] Role scopes and stop counts are derived from mutable local records
- Lens: security
- Where: docs/slices/agentic-delivery-process/plan.md:243–255, 281–283; test_plan.md:199–219
- Finding: `git diff --name-only` is not a complete role-scope check without explicit immutable comparison points. A default invocation misses staged changes, committed changes and untracked files. CI also cannot reconstruct deleted local TCRs or review rounds from the final tree.
- Evidence: P-1/P-2 cover an edit but not staging, committing, deleting records or rewriting history. Run state is advisory, while the records used for counts are stored in the writable checkout.
- Why it matters: An implementer can evade test ownership or reset escalation counters without a failing final-tree check.
- Suggested resolution: Define immutable phase snapshots and a trusted event ledger. Test staged, committed, untracked, deleted-record and history-rewrite evasions.

##### PR-15 [major] Review reports are authoritative without provenance or content binding
- Lens: security
- Where: docs/slices/agentic-delivery-process/plan.md:153–157, 282; test_plan.md:222–225
- Finding: The plan PR trusts a writable Markdown report’s finding status. Nothing binds that report to the reviewed plan/test-plan digests or authenticates its reviewer.
- Evidence: P-24 checks missing/open findings; P-25 checks reviewer inputs/model. Neither covers editing the report, marking findings resolved without re-review, or changing the plan after review.
- Why it matters: A stale or author-written “resolved” report satisfies the mechanical review requirement.
- Suggested resolution: Bind review results to exact input digests and trusted reviewer execution records; invalidate them after any reviewed-content change. Add tampering and stale-review controls.

##### PR-16 [major] Outcome provenance can be relabelled without being verified
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/plan.md:57; test_plan.md:28, 76–82, 111–115
- Finding: The tests compare declared source fields but do not verify that `probe@<commit>` predates implementation or that `existing@<commit>` contains the claimed exact assertion.
- Evidence: T-2 checks column agreement. No row rejects a fabricated commit, a probe of the candidate implementation, a stale probe, or a claimed existing assertion that was broad.
- Why it matters: An author can observe broken new behavior, label it as an approved baseline and make both declarations agree.
- Suggested resolution: Specify source-artifact validation against immutable pre-change revisions, with controls for wrong commit, wrong assertion and wrong probe time.

##### PR-17 [major] The full-slice lane contradicts the universal size cap
- Lens: consistency
- Where: docs/slices/agentic-delivery-process/plan.md:80–87
- Finding: Exceeding 60 non-test lines or three non-test files selects the full-slice lane, but the next paragraph imposes the same cap on every lane.
- Evidence: Increment 1C alone requires changes across the Makefile, scripts, workflows, security configuration, templates and rulebook.
- Why it matters: A compliant full slice is either rejected or requires an undocumented cap exemption.
- Suggested resolution: State whether the cap selects a lane or limits delivery, and add at-cap and over-cap fixtures for the intended behavior.

##### PR-18 [major] The mutation ratchet permits the decrease it claims to prohibit
- Lens: consistency
- Where: docs/slices/agentic-delivery-process/plan.md:133–135, 206–208; test_plan.md:189, 232–233
- Finding: “Can only rise” conflicts with allowing a decrease through the full-slice lane. T-37 tests only decreases outside that lane and does not test the automatic five-point increase.
- Evidence: Threshold edits already trigger the full-slice lane, so the tested rejection does not establish monotonicity.
- Why it matters: A full-slice PR can lower the threshold while the success criterion still claims the ratchet holds.
- Suggested resolution: Choose the approved decrease policy explicitly and test decreases within the full-slice lane, required increments, the 85% ceiling and missing threshold history.

##### PR-19 [major] Reviewer calibration accepts a reviewer that detects nothing
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/plan.md:161–163; test_plan.md:224
- Finding: Calibration blocks a decrease from the last accepted detection rate but sets no initial minimum. A first accepted rate of zero permits zero forever.
- Evidence: P-26 requires recording the rate and investigating a drop; it does not require detection of any seeded gap.
- Why it matters: The independent-review control can remain nominally calibrated while systematically missing all tested defects.
- Suggested resolution: Set an initial acceptance floor, require detection of specified critical gaps, and test zero detection, missing results and baseline tampering.

##### PR-20 [major] This plan exempts itself from the derivation controls it introduces
- Lens: adequacy
- Where: docs/slices/agentic-delivery-process/test_plan.md:59–73, 144–149, 199–226
- Finding: The current rows lack the required derivation columns, and several threshold tests specify only an over-limit stop. There are no explicit success cases at three accepted TCRs, two on one test, three review rounds or five gate runs; expiry equality is also unspecified.
- Evidence: P-5/P-13/P-14/P-15 test only the first prohibited count. The pre-existing-row exemption delegates missing analysis to this review instead of recording it in the approved test contract.
- Why it matters: An off-by-one implementation that escalates too early can pass all listed stop tests, and later authors cannot determine which evasions were actually resolved.
- Suggested resolution: Apply the derivation fields to this slice and add boundary-success cases, exact expiry semantics and missing-counter controls.

#### Claims verified

- `07520d7` exists and is dated **2026-01-05**; its Compose file mounts `capiss_keys` into `tool-b`.
- `bed2d0e` exists and is dated **2025-12-26**.
- `20c074e` exists and contains the pre-1A harness used by the proposed replay.
- The current Compose file defines **23 services**, including profiled services.
- `trace/tests.yaml` names **120 distinct E2E evidence IDs**, across 12 suite and 44 case records.
- The loose-check inventory contains eight `assert_file_any` call sites, five negative network-error grep checks, three broad attestation assertions and four DNS warning branches. These categories overlap; “about 20” is approximate.
- The four identified live outcome guards exist: `M1-T5`, `M2-T5`, `M2-T6` and `M4-T2`.
- Current thresholds are 85% total line coverage, 75% critical branch coverage, 90% critical diff coverage and 70% mutation score.
- `qa-quality` currently includes trace checks, unit guard integrity and documentation checks; `unit-trust` does not itself include mutation.
- `test-lint`, `qa-deploy`, `plan-lint`, `slice-close` and `hooks-install` are planned targets, absent today.
- The proposed registers, kind registry, gate registry and escape corpus are absent today.
- Synthetic mutation statistics reproduced the denominator false green described in PR-05.
- Static evaluation confirmed that M5-T21’s resource fails canonicalization before policy evaluation.

#### Not checked

- No Docker commands, services, live probes or network access were used.
- GitHub branch protection, required-check behavior, runner isolation, artifact permissions and actual CI timings were not verified live.
- Installed mutmut/OPA behavior, custom check-removal transformations and orchestration runtime support were not exercised.
- Runtime users inherited from images and deployed filesystem contents were not inspected.
- Actual credential contents and private-key files were not read.
- The planned gates cannot be executed because they do not yet exist.
- No files outside the repository and supplied extra input directory were read; no files were modified.
