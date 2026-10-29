# Slice Plan — agentic-delivery-process (slice 1: honest tests and key confinement)

Status: **plan for review** (2026-10-29), cut to a lean scope by the user (D20). Approval = the user
merges this plan as a PR (D8). This is slice 1 of three (D19); it runs under the manual slice
workflow in `AGENTS.md` and the [PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion)
rules. Review history: the user's plan-PR comments (D16, D17), independent Codex reviews, an
escalation (D18, D19) and the lean cut (D20), all in [`plan_review.md`](plan_review.md). Slices 2
and 3, and everything deferred from this slice, are drafts in [`later_slices.md`](later_slices.md);
merging this plan does not approve them.

## Goal
**Programme.** Agents take an approved plan to a pull request, and the user is involved only in
grill-me, merges and escalations. That works only if a green run can be trusted.

**This slice.** Two things a green run could not be trusted on before:
1. **Honest tests.** About 20 E2E checks accept more than one outcome, so a broken service can pass
   as a correct denial. Each becomes an exact expected outcome, and a lint stops loose checks coming
   back.
2. **Key confinement.** Nothing checked which service can see which key, so OPL-005 stayed green for
   ten months. A short holder list and a static compose check (`qa-deploy`) now fail when a key,
   socket or secret reaches any other service.

Both are backed by an independent reviewer at the implementation PR, and the mutation gate stops
hiding untested code.

## Threat model (D18)
The repo-wide rule is [AGENTS.md — PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion).
Applied to this slice: the checks catch **honest mistakes** by an agent (loose or wrong tests,
weakened checks, a key mounted or copied where it does not belong, stale evidence). An agent that
deliberately attacks CI, the gates or the evidence is out of scope; that residual is accepted as
OPL-009.

## Programme (D19)
| Slice | Scope | Status |
| --- | --- | --- |
| 1 (this plan) | exact outcomes for the loose tests, positive twins, `test-lint`, key-holder list and `qa-deploy`, mutation scoring, independent review at the PR | plan for review |
| 2 `delivery-lanes-ci` | lanes, CI as the authoritative E2E runner; items deferred from slice 1 if still needed | draft |
| 3 `delivery-orchestration` | the agent pipeline (roles, TCR, DEV, stop limits, hooks); then the pilot that fixes OPL-005 to OPL-008 | draft |

Until slice 2 lands, the authoritative evidence stays what `AGENTS.md` requires today: a full E2E
run on a clean stack plus `make qa-evidence`.

## Terms
| Term | Meaning |
| --- | --- |
| Expected outcome | The exact observable result a test must produce, for example 403 with `reason=sub_mismatch` from `tool-b`. Recorded in the `test_plan.md` table and asserted exactly by the harness. |
| Source | Where an expected value came from: `plan` (decided in the test plan), `probe@<commit>` (observed on the stack *before* the change) or `existing@<commit>` (copied from an assertion that is already exact). |
| Twin | The positive control of a negative test: the allowed case on the same route, which must pass in the same run. |
| Holder list | Which services may hold each protected key, socket or secret: the `REQ-SEC` requirements, in machine form in `security/invariants.yaml`. |
| Known violation | A one-line, expiring exception for an open OPL in `invariants.yaml`. |
| TCR, DEV, Lane, Escalation | Slice 2 and 3 terms; see [`later_slices.md`](later_slices.md). |

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
Decisions as recorded. Rows marked *(amended by D20)* are narrowed for slice 1; the deferred parts
are in [`later_slices.md`](later_slices.md).

| # | Question | Decision |
| --- | --- | --- |
| D1 | Which runtimes | Claude Code drives the pipeline (skill, role subagents, workflow, hooks). Every hard gate lives in `make`, git hooks and CI, so a Codex or manual change cannot skip it. |
| D2 | Staging | Increment 1 gates → Increment 2 orchestration → Increment 3 pilot; mapped to three slices by D19. |
| D3 | Existing loose checks | Tighten all (~20) in Increment 1. No baseline file. A multi-outcome check survives only as a declared alternate with a reason. |
| D4 | Expected outcomes *(amended by D20)* | The user approves a fixed-format expected-outcome table in `test_plan.md`, with a source for each value. The harness asserts it exactly. A value is never pinned by watching the new implementation run. |
| D5 | Controls *(amended by D20)* | Every negative test has a named positive twin that passes in the same run. The wrong-failure question is answered by the independent test review (D20), not by a replay tool. |
| D6 | Invariant register *(amended by D20)* | `REQ-SEC-*` requirements in `docs/requirements.md` plus machine-readable `security/invariants.yaml`, kept consistent by a check. Feeds `qa-deploy`. |
| D7 | Deployment check | Full per-service allowlist, default deny: mounts and mode, networks, published ports, secret env vars, runtime user, capabilities. Non-root: the 23 existing services are grandfathered as a warning until 2027-01-31; a new service running as root fails; a migrated service is locked as non-root. |
| D8 | Plan approval | The user merges the plan PR on GitHub. The pipeline runs only when the plan files on `origin/main` match the working copy. Requires branch protection on `main`. |
| D9 | Lanes | Slice 2. |
| D10 | Stop limits | Slice 3. |
| D11 | Reviewer independence | Reviewers never see the author's reasoning: `codex exec` in a read-only sandbox, or, if Codex is unavailable, a Claude model with clean context, and the report says which and why. |
| D12 | Deviations | Slice 3. |
| D13 | Authoritative E2E | Slice 2 (CI). Until then, a local full run on a clean stack. |
| D14 | Trigger | Slice 3. |
| D15 | Handoff | Slice 3. The agent cannot merge: `main` requires the owner's approval. |
| D16 | Security coverage of grill-me *(added in plan review, 2026-10-28; amended by D20)* | Every slice asks "which keys, sockets and secrets does this touch, and who may hold them?" against the holder list. `qa-deploy` checks mounts and env vars mechanically; the independent review checks the rest (see below). |
| D17 | Test adequacy and independent review *(added in plan review, 2026-10-28; amended by D20)* | An independent reviewer, never the author, reviews `plan.md` and `test_plan.md` before the user sees them, and the tests in the implementation PR. The mutation gate counts untested mutants. See below. |
| D18 | Threat model *(escalation answer, 2026-10-29)* | Honest mistakes by a fallible agent, not deliberate attacks on the delivery infrastructure. See "Threat model". |
| D19 | Scope *(escalation answer, 2026-10-29)* | Three slices; this plan is slice 1. |
| D20 | Lean slice 1 *(user decision, 2026-10-29)* | Keep the parts that catch the two defects that started this: exact outcomes, twins, `test-lint`, the holder list with `qa-deploy`, mutation scoring. Replace the runtime asset scan with a review question plus a one-time baseline look, and the replay tool with an independent test review. Defer kinds, tiers, fault injection, provenance enforcement, the derivation checklist and the invariant matrix. |

### Key confinement (D16, D20)
| Check | What it catches | When | Who |
| --- | --- | --- | --- |
| Holder list | states who may hold each key, socket and secret | read by every grill-me and review | the user approves it in the plan |
| `qa-deploy` | a protected path, socket or secret env var mounted or passed into a service outside its holders, in any profile | every PR (CI) | automatic |
| Baseline look | a key copied by an entrypoint, script or Dockerfile today, which compose does not show | once, in 1B | the implementer, checked by the reviewer |
| Review question | the same for every later change: a key reaching a non-holder through a `COPY`, an entrypoint or script that copies or writes it, or a shared volume | every implementation PR | the independent reviewer |

On the `07520d7` compose, `qa-deploy` reports `capiss_keys` mounted into `tool-b`.

### Independent review (D17, D20)
- **Plan review, before the user.** A reviewer that is not the author reviews `plan.md` and
  `test_plan.md` through security, test adequacy and consistency, under the AGENTS.md acceptance
  rule. Its inputs are the plan, the test plan, the decision log, the holder list and the compose
  inventory; never the author's reasoning. `plan_review.md` keeps the report verbatim, the SHA-256
  of the reviewed files, and the author's answers separately. Each round ends with "approvable
  within the threat model: yes or no"; from round 2, new findings must block. After round 3 the user
  decides.
- **Test and change review, at the implementation PR.** The same kind of reviewer reads the diff,
  the approved test plan and the AGENTS.md PoC section, and answers two questions for the PR body:
  1. *Tests:* for each new or changed test, which wrong failure would still pass it (service down,
     another status, the right status with another reason, another component answering, a missing
     value or empty file read as success)? Does its assertion match the approved expected outcome?
  2. *Keys:* does the change make a key, socket or secret reachable by a service outside the holder
     list, through a compose mount, an env var, a Dockerfile `COPY`, an entrypoint or script that
     copies or writes it, or a shared volume?

  A "yes" to either is a blocker under the AGENTS.md rule. It is judgment, not a mechanical
  guarantee; that is accepted for the PoC.
- **Mutation scoring.** `no_tests` and `skipped` mutants count as not killed, and an empty run fails.
  Today `scripts/mutation_gate.py` subtracts them from the denominator, so 1 killed and 99 untested
  mutants scores 100%. Thresholds stay as they are (70% for capiss and tool-b).

## Requirements
Proposed security invariants, added to `docs/requirements.md` in Increment 1B. Each carries a
`Holders:` line that the consistency check compares with `invariants.yaml`, so widening a holder
set means changing the requirement.

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
  attestation) and `rogue-tests` (test-only harness).
- **REQ-SEC-D1 — Deployment allowlist.** Every service's mounts, networks, published ports, secret
  env vars, runtime user, capabilities and images shall match the approved register; anything else
  fails.
- **REQ-SEC-D2 — Non-root workloads.** Services shall run as non-root. Existing services are
  grandfathered until 2027-01-31; new services have no grace period. The effective user is the
  compose `user`, else the image's `USER`; a user that cannot be read counts as root.

Redis authorization state (proposed earlier as REQ-SEC-S1) is added by the pilot together with its
fix, because no slice-1 check can test it (OPL-007).

## Known violations at gate activation
`qa-deploy` would fail on today's compose. It starts with exactly these exceptions, each expiring
2026-12-31 (valid through 23:59:59 UTC):

| OPL | Asset | Services | Through |
| --- | --- | --- | --- |
| OPL-005 | K1 | `tool-b`, `jira-tool`, `jira-mcp-gateway`, `agent-a`, `rogue` | the `capiss_keys` mount (`root_key.b64`) |
| OPL-006 | K2 | `rogue-socket`, `tool-b`, `tool-b-envoy`, `jira-tool`, `jira-tool-envoy`, `jira-mcp-gateway`, `jira-mcp-envoy`, `codex-jira-mcp-adapter`, `capability-issuer-envoy`, `capability-issuer-no-opa-envoy`, `agent-a`, `rogue` | the `spire/agent` mount (`data/`) |
| OPL-008 | K4 | `spire-token-init` | the `spire/server` mount (`data/keys.json`, `datastore.sqlite3`) |

If the 1B baseline look finds anything else, it gets an OPL entry and a row here in the 1B PR,
which the user approves before the gate is switched on. The pilot (slice 3) fixes OPL-005 to
OPL-008.

## Success criteria
1. Every loose check in the 1A table asserts its exact expected outcome, every negative test there
   has a twin that passes in the same run, and the full E2E suite passes on a clean stack with
   `make qa-evidence`.
2. `make test-lint` flags every loose check of the 1A table on the pre-1A harness, and none after 1A;
   the only exemption is a declared alternate with a reason.
3. `make qa-deploy` fails on any compose or image fact outside `security/invariants.yaml`, in every
   profile. On the `07520d7` compose it reports the signing key in `tool-b`; on today's compose it
   reports exactly the known violations.
4. The mutation gate counts untested and skipped mutants as not killed. The 1A PR reports the new
   score for capiss and tool-b: at or above 70% it merges as normal; below 70% it is the trigger for
   a small follow-up slice (write unit tests or change the threshold), and no other PR is blocked
   meanwhile.
5. The 1A and 1B PRs each carry the independent review's answers to the two questions, with no
   unresolved "yes".

## In scope
**Increment 1A — Honest tests** (its own PR)
- The expected-outcome table format in `docs/slices/_template/test_plan.md`, and the two review
  questions in the slice template.
- Tighten the loose checks in the `test_plan.md` table to exact assertions; add the new twins.
- `make test-lint` over `scripts/rogue_node_tests.sh`, in `make qa-quality`.
- Mutation scoring in `scripts/mutation_gate.py`.

**Increment 1B — Key confinement** (its own PR)
- The `REQ-SEC` requirements; `security/invariants.yaml` with holders, the per-service allowlist and
  the known violations; the consistency check.
- A compose inventory script over every profile; `make qa-deploy` (policy in Rego under
  `policy/deploy/`, run by a pinned OPA) with the non-root warning, expiry and lock; the effective
  runtime user from compose or the built image.
- The one-time baseline look at entrypoints, scripts and Dockerfiles for key copies, recorded in the
  1B PR.
- The deployment allowlist in the `docs/architecture.md` state inventory.

## Out of scope
- Everything D20 defers, listed in [`later_slices.md`](later_slices.md): the kind registry and
  `expect:` blocks for all tests, the replay tool, tiers and fault injection, provenance enforcement,
  the derivation checklist, the runtime invariant matrix and content scan.
- Slices 2 and 3, including CI as the authoritative E2E runner.
- The OPL-005 to OPL-008 fixes (the pilot), REQ-SEC-S1 and the Redis mechanism.
- Migrating the 23 existing services to non-root (tracked by the D7 expiry).
- Defending against a deliberately malicious PR (D18, OPL-009).
- Live Jira in CI, the generic verifier, M6 and later; the complexity debt (18 functions above 10).

## Hidden-state and trust decisions
- **Runtime:** this slice adds or changes no runtime hidden state.
- **Process state** (trust-relevant, so listed):

| State | Store | Writer | Reader | Lifecycle | Authority |
| --- | --- | --- | --- | --- | --- |
| Approved plan | `docs/slices/<id>/plan.md`, `test_plan.md` on `origin/main` | user, via PR merge | implementer, reviewers | permanent | authoritative |
| Holder list and allowlist | `security/invariants.yaml` (and the `REQ-SEC` lines) | slice PRs the user merges | `qa-deploy`, consistency check, reviewers | permanent | authoritative |
| Expected outcomes | the `test_plan.md` table, asserted in `scripts/rogue_node_tests.sh` | test author, from the approved table | harness, reviewer | permanent | authoritative |
| Evidence | `artifacts/rogue-tests/` from a full clean-stack run | harness | `qa-evidence`, user | per run | authoritative until slice 2 moves it to CI |
| Independent review | `plan_review.md`; the review section of each implementation PR | Codex or a clean-context Claude, run by hand | user | permanent | advisory |

## Authored source changes
- Requirements: the `REQ-SEC-*` entries above.
- Architecture: the deployment allowlist in the state inventory and a "Deployment invariants" line
  in the Security model summary.
- Runtime proof: the tightened E2E tests and new twins; `docs/test_spec.md` for each.
- Templates: the expected-outcome table and the review questions in `docs/slices/_template/`.

## Retirement and compatibility
- `assert_file_any` is removed from the harness; multi-outcome checks survive only as declared
  alternates.
- Negative-grep "no network error" checks are replaced by positive outcome checks.
- The `M3.S2-T3`/`M3.S2-T5` DNS-vs-TCP warning alternates become exact "does not resolve" plus
  IP-direct "times out" checks.
- `scripts/mutation_gate.py` stops subtracting `skipped` and `no_tests` from the denominator.
- No documents are archived.

## Review notes (approve or change in the plan PR)
1. **Known violations.** An exception is (OPL, asset, service) with an absolute expiry. It is void
   once its OPL is closed, and is added, widened or renewed only by a plan PR the user merges. It is
   the only exception mechanism.
2. **Exception expiry** (for approval): 2026-12-31 for the OPL-005, OPL-006 and OPL-008 rows.
3. **`M2-T7`** is corrected in the pilot, because the corrected test fails until OPL-006 is fixed.
4. **Probed rows** in the 1A table are pinned by probing the existing stack *before* any change and
   shown with the probe output in the 1A PR; a probe that contradicts a *plan* row stops for the
   user instead of adjusting the row.
5. **Mutation scoring** may lower today's score (85.58% under the old rule); see success
   criterion 4. Known limit: `setup.cfg` sets `mutate_only_covered_lines = true`, so lines with no
   test are never mutated and still do not lower the score. Left as is for now.
6. **User actions for this slice:** none beyond reviewing and merging.
7. **This plan's own review** was run by hand with Codex (`gpt-6.1-sol`; the configured `gpt-5.5`
   was refused for a ChatGPT login). The lean cut (D20) only removes checks and was not re-reviewed.
