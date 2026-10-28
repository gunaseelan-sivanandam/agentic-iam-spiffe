# Slice Plan — agentic-delivery-process

Status: **plan for review** (2026-10-28). Approval = the user merges this plan as a PR (decision D8).
This slice runs under the current manual slice workflow in `AGENTS.md`; it cannot be delivered by the
pipeline it builds. Revised after the first plan-PR review (2026-10-28): terms defined, D16 added,
the authoritative home of the lanes named, and the CI trust model spelled out (review note 5).
Second review round: D17 (test adequacy and an independent plan review before the user's review).

## Goal
Make agent-written changes trustworthy by construction. After grill-me, an agent pipeline takes an
approved plan to a pull request with no human steps, and every claim it makes is backed by
something an agent cannot fake: deterministic gates whose code comes from `main`, evidence produced
in CI, tests proven to fail on the wrong failure, a deployment checked against an approved
allowlist, and reviewers that never see the author's reasoning. The user is involved in grill-me,
plan PR merges, implementation PR merges, and escalations — nothing else.

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
| D2 | Staging | Increment 1 gates → Increment 2 orchestration → Increment 3 pilot. |
| D3 | Existing loose checks | Tighten all (~20) in Increment 1. No baseline file. A multi-outcome check survives only as a declared alternate with a reason. |
| D4 | Expected outcomes | The user approves a fixed-format expected-outcome table in `test_plan.md`. The test author writes the matching `expect:` block in `trace/tests.yaml`, adding probed low-level values with their source (`plan`, `probe@<commit>`, or `existing@<commit>` for an assertion that is already exact). A gate fails on any mismatch. The harness asserts exactly and writes `observed_signature.json`; `qa-evidence` compares observed with declared. A value is never pinned by watching the new implementation run. The implementer may not edit `expect:` blocks or tests. |
| D5 | Controls | Tier derived by the gate from `expect.kind` and `REQ-SEC` links, never chosen by an agent, the same for current and future tests. Every negative test: offline wrong-failure replay plus a named positive twin. `tls_reject`, `network_unreachable`, `dns_*` and `REQ-SEC` tests also get live fault injection. Outcome guards may read evidence only. |
| D6 | Invariant register | `REQ-SEC-*` requirements in `docs/requirements.md` plus machine-readable `security/invariants.yaml`, kept consistent by a gate. Feeds `qa-deploy` and a generated runtime E2E matrix. |
| D7 | Deployment check | Full per-service allowlist, default deny: mounts and mode, networks, published ports, secret env vars, runtime user, capabilities. Non-root: the 23 existing services are grandfathered as a warning until 2027-01-31; a new service running as root fails; a migrated service is locked as non-root. |
| D8 | Plan approval | The user merges the plan PR on GitHub. The pipeline runs only when the plan files on `origin/main` match the working copy. Requires branch protection on `main`. |
| D9 | Lanes | Four lanes, derived from the diff by gate code checked out from `main` (see below). Authoritative home: `security/lanes.yaml` and `AGENTS.md`. |
| D10 | Stop limits | Stop on >3 accepted TCRs per slice or >2 on one test, >3 review-fix rounds or the same finding twice, >5 full gate runs without convergence, or any material deviation. On stop: WIP commit pushed to the slice branch, `escalation.md` with state, evidence and the exact question, push notification; resume from the recorded phase. |
| D11 | Reviewer independence | Red team via `codex exec` in a read-only sandbox, given only the running stack and `invariants.yaml`. Code-vs-plan and doc-claims reviewers are Claude subagents on a different model from the implementer. All with isolated context. If Codex is unavailable, a Claude model with clean context runs the red team and the report says so and why. |
| D12 | Deviations | Material (stop and ask): a plan decision, REQ/ARCH, `expect:`, invariants or allowlist, API (routes, reason codes, schemas), hidden state, scope or the retirement list; gate-detected where possible. Minor (DEV record, continue): internal choices the plan left open. The implementer files every DEV; the code-vs-plan reviewer, not the implementer, confirms "minor". A plan decision without code, or code without a plan decision or DEV, fails the close. |
| D13 | Authoritative E2E | CI. Every PR runs clean-stack full E2E, `qa-evidence` and the replay controls on a GitHub runner (~10 min) and uploads the evidence. Local runs are fast feedback only. Live-Jira tests stay env-gated. |
| D14 | Trigger | The user runs `/deliver <slice>`. Preflight checks the plan on `origin/main`. |
| D15 | Handoff | Pushed branch plus a PR body generated by a script from evidence and CI results; agent narrative only in a labelled section; push notification with the compare link. The agent opens the PR once `gh` uses the personal account, and never merges. |
| D16 | Security coverage of grill-me *(added in plan review, 2026-10-28)* | Security questions are not left to whoever runs grill-me. Every slice's grill-me walks a fixed asset-and-threat checklist that starts from the asset register and the deployed inventory; `plan.md` carries an "Assets and trust" table that a plan gate checks; an isolated reviewer looks for threats the plan does not answer. Two mechanical backstops (content-based asset discovery and a plan-vs-diff asset check) catch what all of that misses, without depending on anyone classifying the asset correctly. See below. |
| D17 | Test adequacy and independent plan review *(added in plan review, 2026-10-28)* | Tests are derived by a fixed checklist from complete sets, not from examples, and their adequacy is measured by the faults they catch: check-removal runs, a mutation ratchet and a corpus of escaped defects. An independent AI reviewer, never the author, reviews `plan.md` and `test_plan.md` before the user sees them; the plan PR is opened only with every finding resolved. See below. |

### Lanes (D9)
The approved content is this table. Its authoritative home after Increment 1C is
`security/lanes.yaml` (triggers, caps, sensitive paths), which the classifier reads, and a
"Delivery lanes" section in `AGENTS.md` that `docs-check` keeps in agreement with that file. This
slice bundle is frozen once implemented, so it is not the place anyone looks the lanes up.

| Lane | Triggered by | User involvement |
| --- | --- | --- |
| Full slice | a contract file changes (requirements, architecture, `invariants.yaml`, `lanes.yaml`, `grill_checklist.md`, test_plan rows, `expect:` blocks, existing tests); new surface (HTTP route, `reason` code, env var, outbound host, mount, port, public function in a sensitive file); net removal of a decision point in a sensitive path (`if`/`elif`/`raise`/`except`/`assert`, early `return`, `_deny(...)`, Envoy filter or route, Rego rule), measured by a structural diff; gate, classifier, threshold or `.github/workflows/` changes; over the cap; major dependency bump | grill-me, plan PR, implementation PR |
| Fix | contract-preserving, within the cap | merge `fix.md` as a plan PR, then the implementation PR |
| Dependency | minor or patch dependency update; lockfile lines excluded from the cap | merge `dep.md` (changelog and advisory review) as a plan PR, then the implementation PR |
| Docs | non-contract docs only (README, STATUS, history, test_spec prose) | implementation PR |

Every lane: a reproduction test the gate proves fails on the base commit (fix lane), 100% coverage
of changed lines, mutation testing on changed lines, the independent reviewers, and a cap of 60
changed non-test lines and 3 non-test files. Each surviving mutant is justified in `fix.md` and
listed in the PR. Sensitive paths: capiss, the verifiers, `services/shared`, the Envoys, OPA, SPIRE
config, compose, the MCP adapter, the mocks, `varambu` rendering, and the QA gates, harness and
validators. `fix.md` has required sections: the approved behavior it violates (REQ or `expect:`
reference), root cause vs symptom, what the reproduction test asserts and its signature, lane and
why, and what was not checked — each with the agent's answer and the reviewer's verdict.

### Security coverage (D16)
OPL-005 needed someone to ask "who can read the signing key?". Nobody did, and nothing else would
have noticed. D16 makes the question unavoidable and adds checks that work even when it is asked
and answered wrongly.

| Layer | What it does | Where | Increment |
| --- | --- | --- | --- |
| Asset register | Every protected asset (signing keys, SPIRE agent state, upstream credentials, authorization state, the Workload API socket) with its class and allowed holders, in `security/invariants.yaml`. | input to every grill-me | 1B |
| Deployed inventory | Before the first question, the agent shows who holds which asset *today*: the compose inventory and the latest asset-discovery report from CI. The conversation starts from deployed facts, not from the plan's story. | grill-me | 1B (reports), 2 (skill) |
| Security branch | A fixed checklist in `security/grill_checklist.md`, walked for every slice, not skippable. For each asset the slice creates, reads, moves, mounts or passes: its class, its allowed holders, how it reaches each container, what a holder could do with it (forge, impersonate, replay, change state), and which runtime test proves its confinement. STRIDE over every new or changed trust boundary. Run by a repo skill `slice-grill` that wraps the global `grill-me`. | grill-me | 2 |
| Plan gate | `plan.md` must contain an "Assets and trust" table (asset, class, holders, delivery path, `REQ-SEC` link, runtime proof). "None" needs a one-sentence reason. `make plan-lint` fails the plan PR otherwise. | CI on the plan PR | 1C |
| Plan threat review | The security lens of the independent plan review (D17): the reviewer reads the plan, the register and the inventory, and lists assets and threats the plan does not address. Each must be answered in `plan.md` before the plan reaches the user. | before the plan PR | 2 |
| Asset discovery | Scans every container's readable files and environment for key and credential material **by content, not by name or label**: PEM private keys, SPIRE `keys.json`, and any 32- or 64-byte value that derives a public key some verifier trusts. A hit outside the register's holder list fails `qa-deploy`, however the mount is classified. | `qa-deploy`, invariant matrix | 1B |
| Plan-vs-diff check | A diff that adds or changes a mount, secret env var, key path or network not named in the plan's asset table fails `slice-close`. | `slice-close` | 1C |

The first five layers make the question hard to skip. The last two catch the miss when it happens
anyway: on the `07520d7` compose, asset discovery fails on `root_key.b64` in `tool-b` even if the
register calls that mount "public key".

### Test adequacy and independent plan review (D17)
The first draft of this test plan covered each decision with the input it exists to catch and
missed the ways a gate can be fooled. It was fixed only because the user asked. D17 replaces that
luck with a method, a measurement and an independent reviewer.

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
  that one check and runs the E2E tests mapped to its file in `security/lanes.yaml`. At least one
  must fail with its declared signature. On a PR this runs for the decision points the PR touches;
  nightly it runs for all of them with the full suite, and a check killed only by an unmapped test
  fails until the mapping is corrected.
- *Mutation ratchet.* Gate code at least 80%. Services at least 75% after the pilot, then +5 points
  with each full slice until 85%. Thresholds live in `scripts/gates.yaml` on `main` and can only
  rise; lowering one is a full-slice change. Every surviving mutant has a reviewed justification.
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
- *Adversarial gate review, during delivery.* An independent reviewer gets each new gate's
  specification and tries to build an input that should fail but passes, or the reverse. Each
  success becomes a test before handoff; the PR body shows the attempts and how many found nothing.
- *Reviewer calibration.* The plan reviewer is run on a fixture plan with seeded gaps; its detection
  rate is recorded in every report, and a drop below the last accepted rate is investigated before
  the reviewer is trusted again.

## Requirements
Proposed security invariants, added to `docs/requirements.md` in Increment 1 (they are the contract
this plan PR approves):

- **REQ-SEC-K1 — Issuer signing key confinement.** The capiss root private key shall be readable
  only inside `capability-issuer` (and the test-only `capability-issuer-no-opa`). Verifiers receive
  the public key only.
- **REQ-SEC-K2 — SPIRE agent private state confinement.** The SPIRE agent data directory
  (`keys.json`, `agent-data.json`) shall be readable only by `spire-agent`. Workloads receive only
  the Workload API socket.
- **REQ-SEC-K3 — Upstream credential confinement.** `JIRA_API_TOKEN` shall be present only in the
  services that call Jira upstream (`jira-tool`, `jira-mcp-gateway`).
- **REQ-SEC-S1 — Authorization state integrity.** Budget, rate and registry state in Redis shall
  reject unauthenticated clients; only capiss may create budgets, and verifiers may only consume them.
- **REQ-SEC-D1 — Deployment allowlist.** Every service's mounts, networks, published ports, secret
  env vars, runtime user and capabilities shall match the approved register; anything else fails.
- **REQ-SEC-D2 — Non-root workloads.** Services shall run as non-root. Existing services are
  grandfathered until 2027-01-31; new services have no grace period.

Existing requirement this slice depends on: **REQ-M2-R5** (workload private key isolation), which
gets its first E2E link through the invariant matrix.

## Success criteria
1. Every negative E2E test declares an exact `expect:` signature, has a positive twin, passes its
   offline wrong-failure replay, and (by tier) has live fault injection; `qa-evidence` fails on any
   observed/declared mismatch.
2. `make test-lint` rejects every loose pattern listed in `test_plan.md`, and no existing test
   needs an exemption other than a declared alternate.
3. `make qa-deploy` fails on any compose fact outside `security/invariants.yaml`. Run against the
   compose file of `07520d7` (2026-01-05), it reports the signing key mounted into `tool-b`.
4. The lane classifier, reproduction-on-base check, structural diff, new-surface detector and size
   cap run in CI from `main`'s copy and fail on a PR that tries to reroute itself or change how its
   own CI jobs run.
5. CI runs the full E2E suite on a clean stack and the gate trusts only that evidence.
6. `/deliver <slice>` takes an approved plan to a pushed branch and generated report, or stops with
   `escalation.md`; role scopes, TCRs, DEVs and stop limits are enforced by the workflow, not by
   agent instructions.
7. The pilot (Increment 3) delivers the OPL-005/006/007 fixes through the pipeline, and every
   problem the pipeline shows in that run is fixed or logged.
8. A plan without an answered "Assets and trust" table fails its plan PR check, and asset discovery
   fails on the `07520d7` compose even when the key mount is registered as public.
9. Every plan PR carries an independent `plan_review.md` with no open finding; check-removal runs
   kill every sensitive decision point; mutation thresholds only rise; every fixture in the
   escaped-defect corpus is caught.

## In scope
**Increment 1 — Gates** (three sub-increments, each its own PR)
- **1A Test precision:** the `expect:` schema in `trace/tests.yaml` (including `twin` and
  `source`); the fixed-format expected-outcome table in the slice `test_plan.md` template and its
  consistency check; harness helpers that assert a signature and write `observed_signature.json`;
  signature comparison in `qa-evidence`; the offline replay tool with wrong-failure fixtures per
  `kind`; gate-derived tiers; `make test-lint`. Tighten the ~20 loose checks, and turn the 4 live
  outcome guards into ones that only read evidence. The derivation checklist columns in the slice
  `test_plan.md` template, and the complete-set coverage check (D17).
- **1B Deployment:** the `REQ-SEC` requirements; `security/invariants.yaml`; a compose inventory
  script; Rego rules under `policy/deploy/` run by a pinned OPA binary or image; `make qa-deploy`
  with the non-root warning, expiry and lock; a gate that keeps `REQ-SEC` and `invariants.yaml`
  consistent; a generated runtime invariant matrix in the E2E suite (every protected asset × every
  container); content-based asset discovery (D16).
- **1C Lanes, CI and close-out:** `security/lanes.yaml` (triggers, caps, sensitive paths) and the
  "Delivery lanes" section of `AGENTS.md`, kept in agreement by `docs-check`; the lane classifier
  with the structural diff, new-surface detector and size cap; the reproduction-on-base check; 100%
  changed-line coverage and changed-line mutation for every service, not only capiss and tool-b;
  `make slice-close` with the plan-vs-diff asset check (D16); `make plan-lint` and the "Assets and
  trust" table in `docs/slices/_template/plan.md`; templates for `fix.md`, `dep.md`, TCR and DEV
  records, with validators; a gate registry (`scripts/gates.yaml`, every gate with its negative
  controls) and mutation testing of the gate code; portable git hooks (`make hooks-install`: lint,
  `docs-check`, no `Co-Authored-By` trailer); CI as in review note 5: a gate job and a full-E2E job,
  both `pull_request_target` with job definitions and gate code from `main`, evidence uploaded and
  bound to the PR head commit, plus an advisory `pull_request` job for the PR's own tooling tests.
  D17: check-removal runs (per PR and nightly) with the decision-point-to-test mapping in
  `security/lanes.yaml`; the mutation ratchet in `scripts/gates.yaml`; the escaped-defect corpus in
  `tests/escapes/`; the escape-review check on closed OPL entries; `plan-lint` checks of the
  derivation columns.

**Increment 2 — Orchestration**
- `.claude/skills/deliver/` (`/deliver <slice>`), role subagents in `.claude/agents/` (test
  author, implementer, code-vs-plan reviewer, doc-claims reviewer, Claude red-team fallback), a
  saved workflow in `.claude/workflows/` with phases, per-role path-scope checks via
  `git diff --name-only`, TCR and DEV routing, and stop limits.
- `scripts/redteam_codex.sh` (`codex exec`, read-only sandbox) with the recorded fallback.
- D16: `security/grill_checklist.md` and the `slice-grill` skill in `.claude/skills/`, which ends
  by running the independent plan review and opens the plan PR only when it has no open finding.
- D17: the independent plan reviewer (`scripts/plan_review_codex.sh` plus a Claude fallback
  subagent), its seeded-gap calibration fixture, and the adversarial gate reviewer.
- Claude Code hooks in `.claude/settings.json`:
  - edits to `services/`, `compose/`, `policy/` or `spire/` are refused without an active approved slice;
  - `git commit` is refused until `make slice-close` has passed for the current tree;
  - edits to frozen slice bundles are refused;
  - `Co-Authored-By` trailers are refused.
- Run state in `docs/slices/<id>/run/`; `scripts/slice_report.py` builds the PR body from
  evidence; a push notification at a stop or at handoff.
- The rulebook (`AGENTS.md`) rewritten to describe the pipeline in place of the manual steps (the
  lanes section lands in 1C).

**Increment 3 — Pilot**
- Run `opl-005-006-007-isolation` as a full slice through the pipeline: grill-me, plan PR,
  `/deliver`. Its content (public-key-only mounts, Workload-API-socket-only mounts, Redis ACLs,
  removal of the agent-a/rogue key mounts, `M2-T7` corrected to check the deployed rogue) is decided
  in its own grill-me.
- Record every pipeline problem the pilot shows, and fix it or log it.

## Out of scope
- Designing the OPL-005/006/007 fixes themselves (pilot slice).
- Migrating the 23 existing services to non-root (tracked by the D7 expiry; follow-up slices).
- Live Jira in CI, the generic verifier, M6 and later.
- Reducing the existing complexity debt (18 functions above 10).

## Hidden-state and trust decisions
- **Runtime:** this slice adds or changes no runtime hidden state. Redis ACLs (REQ-SEC-S1) arrive
  with the pilot slice, which must list them under this rule.
- **Process state** (trust-relevant, so listed):

| State | Store | Writer | Reader | Lifecycle | Authority |
| --- | --- | --- | --- | --- | --- |
| Approved plan | `docs/slices/<id>/plan.md`, `test_plan.md` on `origin/main` | user, via PR merge | preflight, close | permanent | authoritative |
| Run state | `docs/slices/<id>/run/state.yaml` | workflow | workflow, hooks | per run, kept in git | advisory (CI re-derives) |
| Independent plan review | `docs/slices/<id>/plan_review.md` | plan reviewer (author answers inline) | plan PR check, user | permanent | authoritative for the plan PR |
| TCR, DEV, escalation records | `docs/slices/<id>/run/` | implementer, test author, reviewers | workflow, reviewers, user | permanent | authoritative for the review |
| Authoritative evidence | CI artifact of the E2E job | CI runner | gate job, user | GitHub artifact retention | authoritative |
| Local evidence | `artifacts/rogue-tests/` | harness on the agent's machine | the agent | per run | advisory only |
| Gate code and thresholds | `scripts/`, `security/`, `.github/workflows/` on `main` | full slices only | CI gate job | permanent | authoritative |

## Authored source changes
- Requirements: the `REQ-SEC-*` entries above.
- Architecture: a "Delivery trust model" section (where gates run, what counts as evidence) and the
  deployment allowlist added to the state inventory.
- Runtime proof: tightened E2E tests, `expect:` blocks and the invariant matrix in
  `trace/tests.yaml`; the kind registry `trace/expect_kinds.yaml`; tooling tests in `tests/tools/`.
- Rulebook: the "Delivery lanes" section of `AGENTS.md` (1C) and the pipeline description (2).
- Templates: the "Assets and trust" table in `docs/slices/_template/plan.md` (1C).

## Retirement and compatibility
- `assert_file_any` is removed from the harness; multi-outcome checks survive only as declared
  alternates.
- Negative-grep "no network error" checks are replaced by positive signature checks.
- The `M3.S2-T3`/`M3.S2-T5` DNS-vs-TCP warning alternates become exact `dns_unresolvable` plus
  IP-direct `network_unreachable` signatures.
- The manual steps in `AGENTS.md`'s slice workflow are replaced by the pipeline (Increment 2), and
  local E2E stops being authoritative (Increment 1C).
- `unit-diff-cov` widens from capiss and tool-b to all services.
- No documents are archived.

## Review notes (approve or change in the plan PR)
1. **Known violations while the pilot is pending.** `qa-deploy` and the invariant matrix would fail
   on OPL-005/006/007 from Increment 1B onward. Proposal: `invariants.yaml` may list a violation
   only with an OPL id and an expiry at the pilot's close; the gate shows each one in every report
   and fails on anything not listed. It is the only exception mechanism, and it is not a baseline
   for test precision (D3).
2. **`M2-T7`** is corrected in the pilot, not in Increment 1, because the corrected test fails
   until OPL-006 is fixed.
3. **Probed rows** in the Increment 1A expected-outcome table are pinned by probing the existing
   stack during 1A and reviewed in the 1A PR, under D4.
4. **User actions:** enable branch protection on `main` (PR required, no direct push) and make
   the CI gate and E2E jobs required checks, once they exist.
5. **CI trust (`pull_request_target`).** For a `pull_request_target` run, GitHub takes the workflow
   file from `main`, not from the PR. A PR that edits `.github/workflows/` or a gate script therefore
   changes nothing about how *that PR* is judged; the edit takes effect only after merge, and such a
   PR is in the full-slice lane. Both authoritative jobs use this trigger:
   - The workspace root is a checkout of `main`. The PR is checked out into `pr/` and is never used
     for the gate's scripts, config or local actions.
   - The gate job never executes PR code; it only reads the PR's diff and files.
   - The E2E job has to run the PR's services, harness and tests, because they are the system under
     test. Those files are contract files (full slice), so their changes reach the user's review;
     `main`'s `qa-evidence` and replay controls judge the evidence.
   - Hardening: same-repository PRs only (fork PRs refused), no secrets, `permissions: contents:
     read`, `persist-credentials: false`, no caches.
   - GitHub can count a required check as passed by its name, so a PR could add its own workflow
     with a job of the same name. The gate job fails any PR that adds a workflow job named like a
     required check.
   - The PR's own tooling tests (useful when the PR changes a gate) run in a separate
     `pull_request` job that is advisory only.
6. **Codex headless:** `codex exec` must work non-interactively with the user's login; if it
   cannot, Increment 2 records that and uses the Claude fallback until it does.
7. **CI cost:** about 10 runner minutes per PR push for the E2E job, plus the check-removal runs:
   on a PR, one mapped-test run per touched decision point; nightly, the full suite per decision
   point (a few hours of runner time, scheduled off-peak).
8. **This plan's own review.** This slice predates the plan reviewer it builds. Before this PR is
   merged, the independent plan review runs once by hand with the D17 inputs and lenses, and its
   report is committed as `plan_review.md`.
9. **Mutation targets** (for approval here): gate code 80%; services 75% after the pilot, +5 per
   full slice until 85%.
