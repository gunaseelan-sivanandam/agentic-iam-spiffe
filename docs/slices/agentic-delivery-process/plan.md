# Slice Plan — agentic-delivery-process (slice 1: test precision and deployment invariants)

Status: **plan for review** (2026-10-29). Approval = the user merges this plan as a PR (D8). This is
slice 1 of three (D19); it runs under the manual slice workflow in `AGENTS.md`. Review history: the
user's plan-PR comments (D16, D17), independent Codex reviews and an escalation (D18, D19), all in
[`plan_review.md`](plan_review.md). Slices 2 and 3 are drafts with their carried review findings in
[`later_slices.md`](later_slices.md); merging this plan does not approve them.

## Goal
**Programme.** Make agent-written changes trustworthy by construction. After grill-me, an agent
pipeline takes an approved plan to a pull request with no human steps, and every claim it makes is
backed by deterministic gates, evidence, tests proven to fail on the wrong failure, a deployment
checked against an approved allowlist, and reviewers that never see the author's reasoning. The
user is involved in grill-me, plan PR merges, implementation PR merges and escalations.

**This slice.** Make every E2E outcome exact and proven to fail on the wrong failure, and make the
deployment facts (who holds which key, credential, socket and state) a checked contract, so that
neither the OPL-005 class nor the ~20 loose checks can pass a green run again.

## Threat model (D18)
The pipeline defends against a **fallible, reward-seeking agent**: one that makes mistakes, takes
shortcuts or optimises for a green result. In scope:
- loose, wrong or vacuous tests; tests that pass for the wrong reason or fail for the wrong one;
- weakened assertions, `expect:` blocks or thresholds; skipped steps;
- edited, stale or misattributed evidence, reports and run records;
- unplanned scope; misclassified or unlisted assets; untested security boundaries;
- honest errors in the gate code itself.

Out of scope: an agent that **deliberately attacks the delivery infrastructure**, for example a PR
that alters a Docker-socket-holding image to take over the CI runner, forges coverage or mutation
statistics with matching identifiers, or appends falsified events to a ledger. That residual is
accepted and logged as OPL-009. It is mitigated, not prevented: such changes touch sensitive paths,
so they take the full-slice lane and the user's review (slice 2); `main` reruns everything nightly
(slice 2); credentials and merge rights are enforced by GitHub, not by agent instructions (slice 3).
Review findings that matter only under the out-of-scope model are answered by this decision.

## Programme (D19)
| Slice | Scope | Decisions it delivers | Status |
| --- | --- | --- | --- |
| 1 (this plan) | 1A test precision, 1B deployment invariants, mutation scoring | D3–D7; D16 register, inventory and asset discovery; D17 derivation, complete sets, mutation scoring | plan for review |
| 2 `delivery-lanes-ci` | lanes, CI trust and authoritative CI E2E, check removal, ratchet, escape corpus, `plan-lint`, contract delta | D8 (CI part), D9, D13; D16 plan gate and plan-vs-diff; D17 measurement | draft |
| 3 `delivery-orchestration` | `/deliver`, roles, TCR and DEV routing, ledger, stop limits, hooks, credentials, `slice-grill`, review automation and calibration; then the pilot `opl-005-006-007-isolation` | D1, D10–D12, D14, D15; D16 security branch and threat review; D17 review automation | draft |

Until slice 2 lands, the authoritative evidence stays what `AGENTS.md` requires today: a full E2E
run on a clean stack plus `make qa-evidence`.

## Terms
| Term | Meaning |
| --- | --- |
| TCR | **Test Change Request.** The implementer may not edit tests or `expect:` blocks. When it believes a test is wrong, it files a TCR in `docs/slices/<id>/run/`: the test, the requested change, the reason and the evidence. The test author decides in its own context, with the approved `test_plan.md` as the contract: **accept** (consistent with the approved row; the anti-weakening check runs and the PR body lists the TCR), **reject** (the implementation must meet the test as written), or **escalate** (only a plan change would allow it, which is a material deviation, so the run stops and asks the user). Not Kent Beck's "test && commit \|\| revert". |
| DEV | **Deviation record.** An implementation choice the plan did not make or made differently. Minor: recorded, the run continues. Material: the run stops (D12). |
| Signature | The exact observable outcome a test expects, for example 403 with `reason=sub_mismatch` produced by `tool-b`, declared in the test's `expect:` block. |
| Kind | The class of outcome a signature describes. It fixes the signature fields, the wrong-failure fixtures and the tier; the registry is `trace/expect_kinds.yaml` (see `test_plan.md`). |
| Twin | The positive control of a negative test: the allowed case on the same route, which must pass in the same run. |
| Wrong-failure replay | An offline run of a test's outcome guard against recorded evidence of *other* failures (service down, wrong status, wrong reason, wrong component). The guard must reject every one. |
| Fault injection | A live run that removes the cause of a denial (for example attaches the caller to the target network) and shows the outcome flips, proving the denial came from that cause. |
| Tier | Which controls a test needs, derived by the gate from its kind and `REQ-SEC` links (D5). |
| Lane | The delivery path a change takes (full slice, fix, dependency, docs), derived from its diff (D9). |
| Sensitive path | A file whose change can weaken a security decision or a gate, listed in `security/lanes.yaml`. |
| Escalation | A stop: the run pushes its work in progress, writes `escalation.md` with the exact question and notifies the user (D10). |
| Known violation | A listed, expiring exception for an open OPL in `invariants.yaml` (review note 1). |

## Why (root cause, 2026-10-28)
The capiss signing key (OPL-005) and the SPIRE agent key store (OPL-006) were readable in
containers that must never hold them since 2026-01-05 (`07520d7`) and 2025-12-26 (`bed2d0e`), about
ten months each, while every gate was green. The defect passed six layers that shared one blind spot:

| Layer | Why it missed |
| --- | --- |
| grill-me | interrogates the plan it is given; no asset or key-holder question was ever asked |
| requirements | functional only; no requirement named who may hold the signing key |
| V-model trace | stops at code; compose files, mounts, users and networks are untraced |
| UT / mutation | code was correct; unit tests use temporary key directories |
| E2E | black-box over HTTP; `M2-T7` checks a temporary rogue container *without* the agent mount instead of the deployed one, and `E2E-M2-SUITE` links no requirement |
| red team (M3) | external-network attacker only; reported "NO FINDINGS" without listing what it did not test |
| docs | asserted "the private key never leaves the issuer container" with no check behind it |

Separately, about 20 E2E assertions accept more than one outcome (for example `403|503`, or
"refused or timed out or no route"), so a broken service can pass as a correct denial.

## Grill-Me Review Summary (2026-10-28)
| # | Question | Decision |
| --- | --- | --- |
| D1 | Which runtimes | Claude Code drives the pipeline (skill, role subagents, workflow, hooks). Every hard gate lives in `make`, git hooks and CI, so a Codex or manual change cannot skip it. |
| D2 | Staging | Increment 1 gates → Increment 2 orchestration → Increment 3 pilot; mapped to three slices by D19. |
| D3 | Existing loose checks | Tighten all (~20) in Increment 1. No baseline file. A multi-outcome check survives only as a declared alternate with a reason. |
| D4 | Expected outcomes | The user approves a fixed-format expected-outcome table in `test_plan.md`. The test author writes the matching `expect:` block in `trace/tests.yaml`, adding probed low-level values with their source (`plan`, `probe@<commit>`, or `existing@<commit>` for an assertion that is already exact). A gate fails on any mismatch. The harness asserts exactly and writes `observed_signature.json`; `qa-evidence` compares observed with declared. A value is never pinned by watching the new implementation run. The implementer may not edit `expect:` blocks or tests. |
| D5 | Controls | Tier derived by the gate from `expect.kind` and `REQ-SEC` links, never chosen by an agent, the same for current and future tests. Every negative test: offline wrong-failure replay plus a named positive twin. `tls_reject`, `network_unreachable`, `dns_*` and `REQ-SEC` tests also get live fault injection. Outcome guards may read evidence only. |
| D6 | Invariant register | `REQ-SEC-*` requirements in `docs/requirements.md` plus machine-readable `security/invariants.yaml`, kept consistent by a gate. Feeds `qa-deploy` and a generated runtime E2E matrix. |
| D7 | Deployment check | Full per-service allowlist, default deny: mounts and mode, networks, published ports, secret env vars, runtime user, capabilities. Non-root: the 23 existing services are grandfathered as a warning until 2027-01-31; a new service running as root fails; a migrated service is locked as non-root. |
| D8 | Plan approval | The user merges the plan PR on GitHub. The pipeline runs only when the plan files on `origin/main` match the working copy. Requires branch protection on `main`. |
| D9 | Lanes | Four lanes, derived from the diff by gate code checked out from `main` (draft in [`later_slices.md`](later_slices.md)). Authoritative home: `security/lanes.yaml` and `AGENTS.md`. |
| D10 | Stop limits | Stop on >3 accepted TCRs per slice or >2 on one test, >3 review-fix rounds or the same finding twice, >5 full gate runs without convergence, or any material deviation. On stop: WIP commit pushed to the slice branch, `escalation.md` with state, evidence and the exact question, push notification; resume from the recorded phase. |
| D11 | Reviewer independence | Red team via `codex exec` in a read-only sandbox, given only the running stack and `invariants.yaml`. Code-vs-plan and doc-claims reviewers are Claude subagents on a different model from the implementer. All with isolated context. If Codex is unavailable, a Claude model with clean context runs the red team and the report says so and why. |
| D12 | Deviations | Material (stop and ask): a plan decision, REQ/ARCH, `expect:`, invariants or allowlist, API (routes, reason codes, schemas), hidden state, scope or the retirement list; gate-detected where possible. Minor (DEV record, continue): internal choices the plan left open. The implementer files every DEV; the code-vs-plan reviewer, not the implementer, confirms "minor". A plan decision without code, or code without a plan decision or DEV, fails the close. |
| D13 | Authoritative E2E | CI. Every PR runs clean-stack full E2E, `qa-evidence` and the replay controls on a GitHub runner (~10 min) and uploads the evidence. Local runs are fast feedback only. Live-Jira tests stay env-gated. |
| D14 | Trigger | The user runs `/deliver <slice>`. Preflight checks the plan on `origin/main`. |
| D15 | Handoff | Pushed branch plus a PR body generated by a script from evidence and CI results; agent narrative only in a labelled section; push notification with the compare link. The agent opens the PR with its own machine identity, never the user's account (amended by review finding PR-08, see "Pipeline credentials" in [`later_slices.md`](later_slices.md)), and cannot merge: `main` requires the owner's approving review. |
| D16 | Security coverage of grill-me *(added in plan review, 2026-10-28)* | Security questions are not left to whoever runs grill-me. Every slice's grill-me walks a fixed asset-and-threat checklist that starts from the asset register and the deployed inventory; `plan.md` carries an "Assets and trust" table that a plan gate checks; an isolated reviewer looks for threats the plan does not answer. Two mechanical backstops (content-based asset discovery and a plan-vs-diff asset check) catch what all of that misses, without depending on anyone classifying the asset correctly. See below. |
| D17 | Test adequacy and independent plan review *(added in plan review, 2026-10-28)* | Tests are derived by a fixed checklist from complete sets, not from examples, and their adequacy is measured by the faults they catch: check-removal runs, a mutation ratchet and a corpus of escaped defects. An independent AI reviewer, never the author, reviews `plan.md` and `test_plan.md` before the user sees them; the plan PR is opened only with every finding resolved. See below. |
| D18 | Threat model *(escalation answer, 2026-10-29)* | The pipeline defends against a fallible, reward-seeking agent, not one that deliberately attacks the delivery infrastructure. See "Threat model". |
| D19 | Scope *(escalation answer, 2026-10-29)* | Three slices. This plan is slice 1 (test precision, deployment invariants); drafts for slices 2 and 3 are in [`later_slices.md`](later_slices.md). D2's increments map to slices: 1A and 1B → slice 1, 1C → slice 2, Increments 2 and 3 → slice 3. |

### Security coverage (D16)
OPL-005 needed someone to ask "who can read the signing key?". Nobody did, and nothing else would
have noticed. D16 makes the question unavoidable and adds checks that work even when it is asked
and answered wrongly.

| Layer | What it does | Where | Slice |
| --- | --- | --- | --- |
| Asset register | Every protected asset (signing keys, SPIRE agent state, upstream credentials, authorization state, the Workload API socket) with its class and allowed holders, in `security/invariants.yaml`. | input to every grill-me | 1 |
| Deployed inventory | Before the first question, the agent shows who holds which asset *today*: the compose inventory and the latest asset-discovery report from CI. The conversation starts from deployed facts, not from the plan's story. | grill-me | 1 (reports), 3 (skill) |
| Security branch | A fixed checklist in `security/grill_checklist.md`, walked for every slice, not skippable. For each asset the slice creates, reads, moves, mounts or passes: its class, its allowed holders, how it reaches each container, what a holder could do with it (forge, impersonate, replay, change state), and which runtime test proves its confinement. STRIDE over every new or changed trust boundary. Run by a repo skill `slice-grill` that wraps the global `grill-me`. | grill-me | 3 |
| Plan gate | `plan.md` must contain an "Assets and trust" table (asset, class, holders, delivery path, `REQ-SEC` link, runtime proof). "None" needs a one-sentence reason. `make plan-lint` fails the plan PR otherwise. | CI on the plan PR | 2 |
| Plan threat review | The security lens of the independent plan review (D17): the reviewer reads the plan, the register and the inventory, and lists assets and threats the plan does not address. Each must be answered in `plan.md` before the plan reaches the user. | before the plan PR | 3 |
| Asset discovery | Scans every running container for private-key material **by content, not by name or label** (PEM private keys, SPIRE `keys.json`, a raw Ed25519 key that derives the trusted public key), as a backstop to the static mount check. A hit outside the register's holder list fails `qa-deploy`, however the mount is classified. | `qa-deploy`, invariant matrix | 1 |
| Plan-vs-diff check | A diff that adds or changes a mount, secret env var, key path or network not named in the plan's asset table fails `slice-close`. | `slice-close` | 2 |

The first five layers make the question hard to skip. The last two catch the miss when it happens
anyway: on the `07520d7` compose, asset discovery fails on `root_key.b64` in `tool-b` even if the
register calls that mount "public key".

### Test adequacy and independent plan review (D17)
The first draft of this test plan covered each decision with the input it exists to catch and
missed the ways a gate can be fooled. It was fixed only because the user asked. D17 replaces that
luck with a method, a measurement and an independent reviewer.

Delivered in slice 1: the derivation template, complete-set coverage for the E2E suite, mutation
scoring, and this plan's own independent review (run by hand). Slice 2: check removal, the ratchet,
the escape corpus, the escape review and `plan-lint`. Slice 3: review automation. The measurement and review designs below are the approved direction; the
later slices refine them in their own plans.

**Derivation (how tests are written).**
- *Derivation checklist.* Every `test_plan.md` row fills fixed columns: what it catches, evasions
  considered (rename, delete, missing, empty, wrong source, wrong commit, wrong time), wrong-reason
  pass, wrong-reason fail, boundary. "n/a" needs a reason. `plan-lint` rejects empty columns.
- *Complete sets.* Rows are generated from enumerated sets (every test, every service in every
  profile, every decision point in a sensitive path, every kind, every `REQ-SEC`), and a gate
  checks that each set is fully covered.

**Measurement (what counts as enough).**
- *Check removal.* For each decision point in a sensitive path (the D9 list: `if`/`elif`/`raise`/
  `except`/`assert`, early `return`, `_deny(...)`, Envoy filter or route, Rego rule), CI removes
  that one check and runs the tests mapped to its file in `security/lanes.yaml`: E2E tests for
  runtime services, policy and Envoy config; tooling tests for QA tools. At least one must fail with
  its declared signature; a removal that is behaviourally equivalent is justified individually, like
  an equivalent mutant (review finding PR-27). On a PR this runs for the decision points the PR touches;
  nightly it runs for all of them with the full suite, and a check killed only by an unmapped test
  fails until the mapping is corrected.
- *Mutation scoring.* `no_tests` and `skipped` mutants count as not killed, and an empty run fails
  instead of scoring. (Today
  `scripts/mutation_gate.py` subtracts `skipped` and `no_tests` from the denominator, so 1 killed
  and 99 untested mutants scores 100%; this is fixed in 1A.)
- *Mutation ratchet.* Gate code at least 80%. Services at least 75% after the pilot, raised toward
  85% as later slices propose. A threshold is lowered only by a plan the user approves. Every
  surviving mutant has a reviewed justification.
- *Escaped-defect corpus.* `tests/escapes/` holds a fixture for every defect that passed the gates:
  the `07520d7` compose (OPL-005), the SPIRE agent mount (OPL-006), unauthenticated Redis (OPL-007),
  the pre-1A harness with its loose checks, and unpinned dev dependencies (the pytest 9.2.0 break).
  The suite must catch every one, and a fixture cannot be removed outside a full slice.
- *Escape review.* Closing an OPL requires a "why no test caught it" section and the checklist
  question it adds to the derivation or security checklist.

**Independent review (who checks the tests).**
- *Independent plan review, before the user.* After grill-me, the plan author writes `plan.md`
  and `test_plan.md`; then a reviewer that is not the author reviews both. It runs as `codex exec`
  in a read-only sandbox, or, if Codex is unavailable, a Claude model different from the author's
  with clean context (the report says which and why, as in D11). Its inputs are the plan, the test
  plan, the grill-me decision log, the asset register, the inventory, both checklists and the
  escape corpus; never the author's reasoning or transcript. It reviews through three lenses:
  security (D16), test adequacy (the derivation checklist and complete sets, plus an attempt to
  find an evasion each row misses), and consistency (every decision has tests and an increment,
  every test traces to a decision or requirement, no contradiction with `requirements.md` or
  `architecture.md`). The author fixes each finding in the plan or answers it with a reason; the
  reviewer re-checks the answers. More than 3 rounds, or the same finding twice, stops with an
  escalation (D10). The report (`docs/slices/<id>/plan_review.md`: findings, resolutions, vendor or
  fallback, what was not checked) is part of the plan PR, and the plan PR check fails while any
  finding is open. The user reviews a plan that has already survived this.
- *Report integrity.* `plan_review.md` records the SHA-256 of the files each round reviewed and
  keeps the reviewer's report verbatim, with the author's answers in a separate section. A plan
  changed after the last round says so, and the user decides whether that needs another round.
- *Acceptance bar.* The reviewer judges the plan against the threat model (D18) and this plan's
  scope only. A finding blocks approval only if it is a **blocker** (a concrete false green, an
  OPL-005-class miss, or an infeasible step, each with a failure scenario inside the threat model)
  or a **major** (a contradiction, or an approved decision or success criterion without a test).
  Implementation details the plan need not settle in advance are notes for the implementation PR,
  which has its own gates. Minor findings never block; out-of-model findings are answered by D18.
  From round 2 on, new findings must be blocker or major with a failure scenario. Every round ends
  with an explicit verdict, "approvable within the threat model: yes or no", and after round 3 any
  remaining major goes to the user with the author's recommendation instead of a fourth round.
  "Good enough" is the user's decision; the reviewer informs it.
- *Adversarial gate review, during delivery.* An independent reviewer gets each new gate's
  specification and tries to build an input that should fail but passes, or the reverse. Each
  success becomes a test before handoff; the PR body shows the attempts and how many found nothing.
- *Reviewer calibration* (optional; slice 3 decides). Run the reviewer once on a plan with seeded
  gaps to see what it catches.

## Requirements
Proposed security invariants, added to `docs/requirements.md` in Increment 1B. They are the
contract this plan PR approves. Each `REQ-SEC` carries a `Holders:` line (and S1 an operations
statement) that the register consistency gate compares with `invariants.yaml`; widening a holder
set or an operation means changing the requirement (resolves PR-10).

- **REQ-SEC-K1 — Issuer signing key confinement.** The capiss root private key shall be readable
  only inside the issuer. Verifiers receive the public key only. Holders: `capability-issuer`,
  `capability-issuer-no-opa` (test-only).
- **REQ-SEC-K2 — SPIRE agent private state confinement.** Each SPIRE agent's data directory
  (`keys.json`, `agent-data.json`) shall be readable only by that agent. Workloads receive only the
  Workload API socket. Holders: `spire-agent`, `spire-rogue-agent` (each its own).
- **REQ-SEC-K3 — Upstream credential confinement.** `JIRA_API_TOKEN` shall be present only in the
  services that call Jira upstream. Holders: `jira-tool`, `jira-mcp-gateway`.
- **REQ-SEC-K4 — SPIRE server signing state confinement.** The SPIRE server's signing keys
  (`data/keys.json`) and datastore (`data/datastore.sqlite3`) shall be readable only by the server.
  Holders: `spire-server`.
- **REQ-SEC-K5 — SPIRE administration confinement.** The SPIRE server admin socket
  (`data/private/api.sock`) shall be reachable only by `spire-server` and by `spire-token-init`,
  a declared administrative holder limited to join-token generation and registration-entry
  management at bootstrap.
- **REQ-SEC-K6 — Join token confinement.** A join token shall be readable only by the services that
  issue, store and use it. Holders: `spire-token-init` (writer), `spire-server`, `spire-agent`, and
  `rogue-tests` (test-only, for the M1 replay test).
- **REQ-SEC-K7 — Workload key confinement.** A workload's SVID private key shall be readable only
  inside that workload's container. Holders: each workload, its own key only.
- **REQ-SEC-K8 — Docker socket confinement.** Holding the Docker socket is host-root authority (a
  read-only bind mount does not restrict the Docker API). Holders: `spire-agent` (Docker workload
  attestation) and `rogue-tests` (test-only harness; slice 2 revisits it).
- **REQ-SEC-S1 — Authorization state integrity.** Redis shall reject unauthenticated clients, and
  each service shall be able to change only the key families the ARCH-016 state inventory names it
  as writer of: `capability-issuer` — budget initialisation, `m4:mint_rate:*`,
  `m4:capiss_minted:*`; `tool-b` — `m4:registry:*`, budget consumption and its request-rate keys;
  `jira-tool` and `jira-mcp-gateway` — budget consumption and their request-rate keys; every other
  service — nothing (resolves PR-09, PR-28). A known limit decides the mechanism: Redis checks the
  commands a Lua script runs against the caller's own permissions, so a service allowed to run the
  consume script's `DECRBY` can also run it directly, including with a negative amount that raises
  a budget (PR-25). The pilot chooses how budget consumption is protected (for example mediation
  through one service, or an accepted and logged residual) and adds its tests.
- **REQ-SEC-D1 — Deployment allowlist.** Every service's mounts, networks, published ports, secret
  env vars, runtime user, capabilities and images shall match the approved register; anything else
  fails.
- **REQ-SEC-D2 — Non-root workloads.** Services shall run as non-root. Existing services are
  grandfathered until 2027-01-31; new services have no grace period. The effective user is the
  compose `user`, else the image's `USER`; a user that cannot be read counts as root (PR-11).

Existing requirement this slice depends on: **REQ-M2-R5** (workload private key isolation), which
gets its first E2E link through the invariant matrix.

## Known violations at gate activation
`qa-deploy` and the invariant matrix would fail on today's deployment. They start with exactly these
exception tuples (review note 1); the expiry of each is 2026-12-31, valid through 23:59:59 UTC.

| OPL | Asset | Services | Through |
| --- | --- | --- | --- |
| OPL-005 | K1 | `tool-b`, `jira-tool`, `jira-mcp-gateway`, `agent-a`, `rogue` | the `capiss_keys` mount (`root_key.b64`) |
| OPL-006 | K2 | `rogue-socket`, `tool-b`, `tool-b-envoy`, `jira-tool`, `jira-tool-envoy`, `jira-mcp-gateway`, `jira-mcp-envoy`, `codex-jira-mcp-adapter`, `capability-issuer-envoy`, `capability-issuer-no-opa-envoy`, `agent-a`, `rogue` | the `spire/agent` mount (`data/`) |
| OPL-007 | S1 | every service on a network with Redis | no authentication |
| OPL-008 | K4 | `spire-token-init` | the `spire/server` mount (`data/keys.json`, `datastore.sqlite3`) |

The first asset-discovery run in 1B, before the gate is switched on, reports every violation. Any
not in this table (for example a workload key found outside its workload) gets an OPL entry and an
exact tuple in the 1B PR, which the user approves; the gate is switched on only then (resolves
PR-33). The pilot (slice 3) fixes OPL-005 to OPL-008.

## Success criteria
1. Every E2E test has an `expect:` block of a registered kind. Every negative test has an exact
   signature and a twin, passes its offline wrong-failure replay and, by tier, has live fault
   injection; `qa-evidence` fails on any observed/declared mismatch.
2. `make test-lint` reports exactly the known loose checks on the pre-1A harness and none after 1A;
   no test needs an exemption other than a declared alternate.
3. `make qa-deploy` fails on any compose or image fact outside `security/invariants.yaml`. On the
   `07520d7` compose it reports the signing key in `tool-b`, and asset discovery fails there even
   when that mount is registered as public.
4. The runtime invariant matrix confirms on the running stack that non-holders cannot read the
   registered key paths, its content scan finds its canary and no unlisted private key, and every
   violation found is an approved tuple with an OPL.
5. The mutation gate counts untested and skipped mutants as not killed;
   capiss and tool-b meet the 70% threshold under that rule, or the 1A PR adds tests or escalates.
6. The full E2E suite passes on a clean stack and `make qa-evidence` passes.

## In scope
**Increment 1A — Test precision** (its own PR)
- The `expect:` schema in `trace/tests.yaml` (with `twin` and `source`) and the kind registry
  `trace/expect_kinds.yaml`.
- The expected-outcome table and the derivation columns in `docs/slices/_template/test_plan.md`,
  and the plan/expect consistency check.
- Harness helpers that assert a signature and write `observed_signature.json`; signature comparison
  in `qa-evidence`.
- The offline replay tool with wrong-failure fixtures per kind; gate-derived tiers; `make test-lint`.
- Tighten the loose checks; turn the 4 live outcome guards into ones that read evidence only; give
  every test an `expect:` block (`existing@` for assertions that are already exact).
- The complete-set coverage check (every test has a kind; every kind has fixtures) and the
  provenance checks for `probe@` and `existing@`.
- Mutation scoring in `scripts/mutation_gate.py` (D17).

**Increment 1B — Deployment invariants** (its own PR)
- The `REQ-SEC` requirements; `security/invariants.yaml` with holders, operations and exception
  tuples; the register consistency gate.
- A compose inventory script over every profile; Rego rules under `policy/deploy/` run by a pinned
  OPA binary or image; `make qa-deploy` with the non-root warning, expiry and lock.
- The effective runtime user from compose or the built image.
- The runtime invariant matrix in the E2E suite (holder, non-holder path, content scan with one
  canary, known violations).
- The first discovery run and the known-violation table; the deployment allowlist in the
  `docs/architecture.md` state inventory.

## Out of scope
- Slices 2 and 3 ([`later_slices.md`](later_slices.md)), including CI as the authoritative runner.
- The OPL-005 to OPL-008 fixes (the pilot) and the Redis mechanism for REQ-SEC-S1.
- Migrating the 23 existing services to non-root (tracked by the D7 expiry).
- Defending against a deliberately malicious PR (D18, OPL-009).
- Live Jira in CI, the generic verifier, M6 and later; the complexity debt (18 functions above 10).

## Hidden-state and trust decisions
- **Runtime:** this slice adds or changes no runtime hidden state. REQ-SEC-S1's mechanism arrives
  with the pilot, which must list it under this rule.
- **Process state** (trust-relevant, so listed):

| State | Store | Writer | Reader | Lifecycle | Authority |
| --- | --- | --- | --- | --- | --- |
| Approved plan | `docs/slices/<id>/plan.md`, `test_plan.md` on `origin/main` | user, via PR merge | implementer, reviewers | permanent | authoritative |
| Asset register | `security/invariants.yaml` | slice PRs the user merges | `qa-deploy`, matrix, consistency gate | permanent | authoritative |
| Expected outcomes | `expect:` blocks in `trace/tests.yaml`, `trace/expect_kinds.yaml` | test author, from the approved test plan | `qa-evidence`, replay | permanent | authoritative |
| Evidence | `artifacts/rogue-tests/` from a full clean-stack run | harness | `qa-evidence`, user | per run | authoritative until slice 2 moves it to CI |
| Independent plan review | `docs/slices/<id>/plan_review.md` | Codex run by hand (author answers in a separate section) | user | permanent | advisory: produced on the author's machine, not bound (slice 3 binds it) |

## Authored source changes
- Requirements: the `REQ-SEC-*` entries above.
- Architecture: the deployment allowlist in the state inventory and a "Deployment invariants" line
  in the Security model summary.
- Runtime proof: tightened E2E tests, `expect:` blocks, the kind registry and the invariant matrix
  in `trace/tests.yaml`; tooling tests in `tests/tools/`.
- Templates: the expected-outcome table and derivation columns in `docs/slices/_template/test_plan.md`.

## Retirement and compatibility
- `assert_file_any` is removed from the harness; multi-outcome checks survive only as declared
  alternates.
- Negative-grep "no network error" checks are replaced by positive signature checks.
- The `M3.S2-T3`/`M3.S2-T5` DNS-vs-TCP warning alternates become exact `dns_unresolvable` plus
  IP-direct `network_unreachable` signatures.
- `scripts/mutation_gate.py` stops subtracting `skipped` and `no_tests` from the denominator.
- No documents are archived.

## Review notes (approve or change in the plan PR)
1. **Known violations.** An exception in `invariants.yaml` is a tuple (OPL id, asset, service)
   with an absolute expiry. It is void as soon as its OPL is
   closed, and is added, widened or renewed only by a plan PR the user merges. The gate shows each
   one in every report and fails on any observed violation that does not match a tuple exactly. It
   is the only exception mechanism and not a baseline for test precision (D3) (resolves PR-13).
2. **Exception expiry** (for approval): 2026-12-31 for the OPL-005 to OPL-008 tuples.
3. **`M2-T7`** is corrected in the pilot, because the corrected test fails until OPL-006 is fixed.
4. **Probed rows** in the 1A expected-outcome table are pinned by probing the existing stack during
   1A and reviewed in the 1A PR, under D4.
5. **Mutation scoring** may lower today's score (85.58% under the old rule); 1A measures it under
   the new rule first and reports the number in the 1A PR.
6. **User actions for this slice:** none beyond reviewing and merging; the `main` ruleset already
   requires a PR. Actions for later slices are listed in `later_slices.md`.
7. **This plan's own review** was run by hand with Codex (`gpt-6.1-sol`; the configured `gpt-5.5`
   was refused for a ChatGPT login, and an expired login failed every request with HTTP 401), under
   the D17 acceptance bar. The report is local and not bound to the plan's digests.
