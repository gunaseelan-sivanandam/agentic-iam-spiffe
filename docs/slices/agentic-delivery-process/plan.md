# Slice Plan — agentic-delivery-process

Status: **plan for review** (2026-10-28). Approval = the user merges this plan as a PR (decision D8).
This slice runs under the current manual slice workflow in `AGENTS.md`; it cannot be delivered by the
pipeline it builds.

## Goal
Make agent-written changes trustworthy by construction. After grill-me, an agent pipeline takes an
approved plan to a pull request with no human steps, and every claim it makes is backed by
something an agent cannot fake: deterministic gates whose code comes from `main`, evidence produced
in CI, tests proven to fail on the wrong failure, a deployment checked against an approved
allowlist, and reviewers that never see the author's reasoning. The user is involved in grill-me,
plan PR merges, implementation PR merges, and escalations — nothing else.

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
| D4 | Expected outcomes | The user approves a fixed-format expected-outcome table in `test_plan.md`. The test author writes the matching `expect:` block in `trace/tests.yaml`, adding probed low-level values with their source (`plan` or `probe@<commit>`). A gate fails on any mismatch. The harness asserts exactly and writes `observed_signature.json`; `qa-evidence` compares observed with declared. A value is never pinned by watching the new implementation run. The implementer may not edit `expect:` blocks or tests. |
| D5 | Controls | Tier derived by the gate from `expect.kind` and `REQ-SEC` links, never chosen by an agent, the same for current and future tests. Every negative test: offline wrong-failure replay plus a named positive twin. `tls_reject`, `network_unreachable`, `dns_*` and `REQ-SEC` tests also get live fault injection. Outcome guards may read evidence only. |
| D6 | Invariant register | `REQ-SEC-*` requirements in `docs/requirements.md` plus machine-readable `security/invariants.yaml`, kept consistent by a gate. Feeds `qa-deploy` and a generated runtime E2E matrix. |
| D7 | Deployment check | Full per-service allowlist, default deny: mounts and mode, networks, published ports, secret env vars, runtime user, capabilities. Non-root: the 23 existing services are grandfathered as a warning until 2027-01-31; a new service running as root fails; a migrated service is locked as non-root. |
| D8 | Plan approval | The user merges the plan PR on GitHub. The pipeline runs only when the plan files on `origin/main` match the working copy. Requires branch protection on `main`. |
| D9 | Lanes | Four lanes, derived from the diff by gate code checked out from `main` (see below). |
| D10 | Stop limits | Stop on >3 accepted TCRs per slice or >2 on one test, >3 review-fix rounds or the same finding twice, >5 full gate runs without convergence, or any material deviation. On stop: WIP commit pushed to the slice branch, `escalation.md` with state, evidence and the exact question, push notification; resume from the recorded phase. |
| D11 | Reviewer independence | Red team via `codex exec` in a read-only sandbox, given only the running stack and `invariants.yaml`. Code-vs-plan and doc-claims reviewers are Claude subagents on a different model from the implementer. All with isolated context. If Codex is unavailable, a Claude model with clean context runs the red team and the report says so and why. |
| D12 | Deviations | Material (stop and ask): a plan decision, REQ/ARCH, `expect:`, invariants or allowlist, API (routes, reason codes, schemas), hidden state, scope or the retirement list; gate-detected where possible. Minor (DEV record, continue): internal choices the plan left open. The implementer files every DEV; the code-vs-plan reviewer, not the implementer, confirms "minor". A plan decision without code, or code without a plan decision or DEV, fails the close. |
| D13 | Authoritative E2E | CI. Every PR runs clean-stack full E2E, `qa-evidence` and the replay controls on a GitHub runner (~10 min) and uploads the evidence. Local runs are fast feedback only. Live-Jira tests stay env-gated. |
| D14 | Trigger | The user runs `/deliver <slice>`. Preflight checks the plan on `origin/main`. |
| D15 | Handoff | Pushed branch plus a PR body generated by a script from evidence and CI results; agent narrative only in a labelled section; push notification with the compare link. The agent opens the PR once `gh` uses the personal account, and never merges. |

### Lanes (D9)
| Lane | Triggered by | User involvement |
| --- | --- | --- |
| Full slice | a contract file changes (requirements, architecture, `invariants.yaml`, `sensitive_paths.yaml`, test_plan rows, `expect:` blocks, existing tests); new surface (HTTP route, `reason` code, env var, outbound host, mount, port, public function in a sensitive file); net removal of a decision point in a sensitive path (`if`/`elif`/`raise`/`except`/`assert`, early `return`, `_deny(...)`, Envoy filter or route, Rego rule), measured by a structural diff; gate, classifier, threshold or `.github/workflows/` changes; over the cap; major dependency bump | grill-me, plan PR, implementation PR |
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
   cap run in CI from `main`'s copy and fail on a PR that tries to reroute itself.
5. CI runs the full E2E suite on a clean stack and the gate trusts only that evidence.
6. `/deliver <slice>` takes an approved plan to a pushed branch and generated report, or stops with
   `escalation.md`; role scopes, TCRs, DEVs and stop limits are enforced by the workflow, not by
   agent instructions.
7. The pilot (Increment 3) delivers the OPL-005/006/007 fixes through the pipeline, and every
   problem the pipeline shows in that run is fixed or logged.

## In scope
**Increment 1 — Gates** (three sub-increments, each its own PR)
- **1A Test precision:** the `expect:` schema in `trace/tests.yaml` (including `twin` and
  `source`); the fixed-format expected-outcome table in the slice `test_plan.md` template and its
  consistency check; harness helpers that assert a signature and write `observed_signature.json`;
  signature comparison in `qa-evidence`; the offline replay tool with wrong-failure fixtures per
  `kind`; gate-derived tiers; `make test-lint`. Tighten the ~20 loose checks, and turn the 4 live
  outcome guards into ones that only read evidence.
- **1B Deployment:** the `REQ-SEC` requirements; `security/invariants.yaml`; a compose inventory
  script; Rego rules under `policy/deploy/` run by a pinned OPA binary or image; `make qa-deploy`
  with the non-root warning, expiry and lock; a gate that keeps `REQ-SEC` and `invariants.yaml`
  consistent; a generated runtime invariant matrix in the E2E suite (every protected asset × every
  container).
- **1C Lanes, CI and close-out:** `security/sensitive_paths.yaml`; the lane classifier with the
  structural diff, new-surface detector and size cap; the reproduction-on-base check; 100%
  changed-line coverage and changed-line mutation for every service, not only capiss and tool-b;
  `make slice-close`; templates for `fix.md`, `dep.md`, TCR and DEV records, with validators;
  portable git hooks (`make hooks-install`: lint, `docs-check`, no `Co-Authored-By` trailer); CI:
  a `pull_request_target` gate job that runs `main`'s gate code with no secrets and a read-only
  token, plus a full-E2E job on the runner with the evidence uploaded.

**Increment 2 — Orchestration**
- `.claude/skills/deliver/` (`/deliver <slice>`), role subagents in `.claude/agents/` (test
  author, implementer, code-vs-plan reviewer, doc-claims reviewer, Claude red-team fallback), a
  saved workflow in `.claude/workflows/` with phases, per-role path-scope checks via
  `git diff --name-only`, TCR and DEV routing, and stop limits.
- `scripts/redteam_codex.sh` (`codex exec`, read-only sandbox) with the recorded fallback.
- Claude Code hooks in `.claude/settings.json`:
  - edits to `services/`, `compose/`, `policy/` or `spire/` are refused without an active approved slice;
  - `git commit` is refused until `make slice-close` has passed for the current tree;
  - edits to frozen slice bundles are refused;
  - `Co-Authored-By` trailers are refused.
- Run state in `docs/slices/<id>/run/`; `scripts/slice_report.py` builds the PR body from
  evidence; a push notification at a stop or at handoff.
- The rulebook (`AGENTS.md`) rewritten to describe the pipeline and lanes in place of the manual
  steps.

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
| TCR, DEV, escalation records | `docs/slices/<id>/run/` | implementer, test author, reviewers | workflow, reviewers, user | permanent | authoritative for the review |
| Authoritative evidence | CI artifact of the E2E job | CI runner | gate job, user | GitHub artifact retention | authoritative |
| Local evidence | `artifacts/rogue-tests/` | harness on the agent's machine | the agent | per run | advisory only |
| Gate code and thresholds | `scripts/`, `security/`, `.github/workflows/` on `main` | full slices only | CI gate job | permanent | authoritative |

## Authored source changes
- Requirements: the `REQ-SEC-*` entries above.
- Architecture: a "Delivery trust model" section (where gates run, what counts as evidence) and the
  deployment allowlist added to the state inventory.
- Runtime proof: tightened E2E tests, `expect:` blocks and the invariant matrix in
  `trace/tests.yaml`; tooling tests in `tests/tools/`.

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
5. **`pull_request_target`** runs with no secrets and a read-only token, and never runs PR code in
   the gate job; PR code runs only in the separate E2E job.
6. **Codex headless:** `codex exec` must work non-interactively with the user's login; if it
   cannot, Increment 2 records that and uses the Claude fallback until it does.
7. **CI cost:** about 10 runner minutes per PR push for the E2E job.
