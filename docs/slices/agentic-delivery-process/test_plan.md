# Slice Test Plan — agentic-delivery-process

Status: **for review** with [`plan.md`](plan.md) (2026-10-28).

## Goal
Prove that every gate this slice adds fails on the input it exists to catch (a negative control
per check), that the tightened E2E tests fail on the wrong failure, and that the pipeline stops or
refuses where the plan says it must. A gate without a failing negative control does not count as
delivered.

## Inputs
- Approved [`plan.md`](plan.md): decisions D1–D15, lanes, the `REQ-SEC-*` requirements.
- Existing requirement REQ-M2-R5.

## Expected-outcome table format (D4)
Every slice `test_plan.md` from now on uses this table for each E2E test it adds or changes. The
test author copies each row into the test's `expect:` block in `trace/tests.yaml`; a gate fails if
they disagree.

| Column | Meaning |
| --- | --- |
| Test | harness ID |
| Kind | one of `http_allow`, `http_denial`, `tls_reject`, `network_unreachable`, `dns_unresolvable`, `attestation_reject`, `file_unreadable`, `env_gated_skip` |
| By | the component that must produce the outcome (for example `tool-b`, `tool-b-envoy`, `spire-server`) |
| Signature | exact observable outcome: status + `reason` for HTTP; curl exit code + alert for TLS; resolver result for DNS; exact log line for attestation |
| Twin | positive control on the same route: a test ID, or `internal` when the test itself performs the allowed case first |
| Tier | derived by the gate, not chosen: `replay+twin`, or `replay+twin+fault` for `tls_reject`, `network_unreachable`, `dns_*` and `REQ-SEC` tests |
| Source | `plan` (decided here) or `probe` (pinned in the test phase by probing the stack as it was before the change, recorded as `probe@<commit>`) |

## E2E plan — Increment 1A: tighten the existing loose checks
Signatures marked *probe* are confirmed against the running stack in 1A and reviewed in the 1A PR
(plan review note 3). All others come from reading the service code.

| Test | Kind | By | Signature | Twin | Tier | Source | Replaces |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M1-T1 missing_join_token | attestation_reject | spire-server | exact rejection log line for a missing token | positive attestation test (named in 1A; added if none exists) | replay+twin | probe | regex `attestation.*fail\|fail.*attest\|…` |
| M1-T2 forged_token | attestation_reject | spire-server | exact rejection log line for an unknown token | same | replay+twin | probe | same regex |
| M1-T3 replayed_token | attestation_reject | spire-server | exact rejection log line for a used token | same | replay+twin | probe | same regex |
| M2.5-T1 toolb_app_not_reachable | network_unreachable | network (edge → toolb_app_net) | curl to the pinned tool-b IP times out (exit 28); never "refused" | new: same request from a container on `toolb_app_net` returns 200 | replay+twin+fault | probe | `refused\|timed out\|no route` |
| M3.S2-T3 opa_unreachable | dns_unresolvable + network_unreachable | edge network | `opa` does not resolve from the edge, **and** a request to OPA's pinned IP times out | new: `opa` resolves and answers from `capiss_app_net` | replay+twin+fault | probe | DNS-vs-TCP warning alternate |
| M3.S2-T5 issuer_app_not_reachable | dns_unresolvable + network_unreachable | edge network | `capability-issuer` does not resolve from the edge, **and** its pinned IP times out | new: resolves and answers from `capiss_app_net` | replay+twin+fault | probe | DNS-vs-TCP warning alternate |
| M3.S2-T4 opa_unavailable | http_denial | capability-issuer | 503, `error=denied`, `reason=opa_unavailable` | M3.S2-T1 | replay+twin | plan | `403\|503` |
| M3.S4-T1 identity_only_denied | http_denial | tool-b | 401, `reason=missing_token` | M3.S4-T2 | replay+twin | plan | `401\|403` + "no network error" grep |
| M3.S4-T3 rogue_no_token_denied | http_denial | tool-b | 401, `reason=missing_token` (tool-b-envoy admits the rogue SAN) | M3.S4-T2 | replay+twin | plan, probe confirms | `401\|403` + grep |
| M3.S4-T4 stolen_token_denied | http_denial | tool-b | 403, `reason=sub_mismatch` | M3.S4-T2 | replay+twin | plan | `401\|403`, `sub_mismatch or invalid_token` + grep |
| M3.S4-T5 expired_token_denied | http_denial | tool-b | 403, `reason=expired` | M3.S4-T2 | replay+twin | plan | `401\|403` + grep |
| M3.S4-T2 agent_a_token_access | http_allow | tool-b | 200, expected secret body | — | — | plan | "no network error" grep |
| M4-T5 budget_enforced_per_root_token | http_denial | tool-b | 11th call: 403, `reason=budget_exceeded`; calls 1–10: 200 | internal | replay+twin | plan | `401\|403` |
| M4-T6 tampered_token_denied | http_denial | tool-b | 401, `reason=invalid_token` | M3.S4-T2 | replay+twin | plan | `401\|403` |
| M5-T21 audience_mismatch_denied | http_denial | capability-issuer | 403, `error=denied`, `reason=policy` (payload passes validation; OPA denies) | M5 root-mint allow test (named in 1A) | replay+twin | plan, probe confirms | `400\|403` |

Also in 1A:
- The 4 outcome guards that call `docker` or `redis-cli` (`M1-T5`, `M2-T5`, `M2-T6`, `M4-T2`)
  move their live call into the exercise and assert on the captured evidence.
- `M5-T55`'s skip stays as a declared `env_gated_skip`.
- The other `add_warning` alternates become exact signatures above, or declared alternates with a
  reason.

## Tooling tests (`tests/tools/`, each with a negative control)
**1A — test precision**
- T-1 `expect:` schema: a missing `kind`, `by`, `signature` or `twin` on a negative test fails.
- T-2 Plan/expect consistency: a `test_plan.md` row that differs from its `expect:` block in any column fails.
- T-3 `qa-evidence` signature check: observed 403/`policy` against a declared 403/`sub_mismatch` fails; an exact match passes.
- T-4 Offline replay: for every `kind`, a deliberately loose outcome guard (for example `assert_file_any 403 503`) is caught by the wrong-failure fixture; the tightened guard rejects every fixture and accepts the true evidence.
- T-5 Tier derivation: a `tls_reject` or `REQ-SEC` test without fault-injection evidence fails, and so does relabelling its `kind` without a plan change.
- T-6 Twin check: a negative test whose twin did not run, or did not pass in the same run, fails.
- T-7 `test-lint` rejects each of these in a guard command, one fixture each:
  - `|| true`;
  - a check on a non-zero exit code alone;
  - `assert_file_any` outside a declared alternate;
  - a broad error regex (`error|fail`, `refused|timed out`);
  - a negative grep used as the only success check;
  - `pytest.raises(Exception)`;
  - `!= 200` as an assertion;
  - an outcome guard that calls `docker`, `curl` or `redis-cli`.

  It accepts `|| true` in evidence-writing plumbing outside guard strings.

**1B — deployment**
- T-8 Inventory: `docker compose config` facts are extracted per service (mounts and mode, networks, ports, secret env vars, user, capabilities).
- T-9 Default deny: an extra mount, network, port, secret env var or capability not in `invariants.yaml` fails, one fixture each.
- T-10 Historical replay: run against `compose/spiffe.compose.yml` of `07520d7`, `qa-deploy` reports `capiss_keys` mounted into `tool-b`. Run against today's compose, it reports OPL-005 and OPL-006 as listed known violations, and fails if their exception entries are removed.
- T-11 Non-root rules:
  - a grandfathered root service is a warning before 2027-01-31 and a failure after it (clock injected);
  - a new root service fails;
  - a migrated service that reverts to root fails.
- T-12 Register consistency: a `REQ-SEC` with no `invariants.yaml` entry fails, and so does an entry with no `REQ-SEC`.
- T-13 Known-violation exceptions: an entry without an OPL id or expiry fails, and so does a past expiry.

**1C — lanes, CI, close-out**
- T-14 Lane classifier, one fixture diff per trigger:
  - each contract file;
  - each new-surface kind;
  - removal of each decision-point kind in a sensitive path;
  - gate, threshold or workflow change;
  - 61 non-test lines, or 4 non-test files;
  - major dependency bump.

  The expected lane must be exact for each.
- T-15 Self-rerouting: a PR fixture that edits the classifier's thresholds is classified by `main`'s copy and lands in the full-slice lane.
- T-16 Reproduction on base: a fix-lane regression test that passes on the base commit fails the check.
- T-17 Changed-line coverage and mutation: one uncovered changed line fails; an unjustified surviving mutant fails; a justified one passes and is listed.
- T-18 `slice-close`: each missing close-out item fails on its own:
  - `test_spec` heading;
  - implementation log entry;
  - STATUS update;
  - red-team report or its "not checked" section;
  - a DEV without the reviewer's confirmation.
- T-19 Git hooks: a commit message with a `Co-Authored-By` trailer is rejected.
- T-20 CI gate job: on a test PR, the job checks out gate code from `main` and fails when the PR edits a gate to always pass (verified on GitHub in 1C).

## Pipeline self-tests — Increment 2 (seeded faults, run on a fixture slice)
Each seeded fault must end in a stop or a failure at the named point, never in a handoff.

| # | Seeded fault | Must be caught by |
| --- | --- | --- |
| P-1 | implementer edits a test file | path-scope check after the implement phase |
| P-2 | implementer edits an `expect:` block | path-scope check |
| P-3 | test author's new test fails for the wrong red-phase reason | test-phase exit gate |
| P-4 | a TCR loosening an assertion is accepted | anti-weakening check (base rerun or weakened-assertion list); the PR body shows it |
| P-5 | 4th accepted TCR | stop limit, `escalation.md` written, notification sent |
| P-6 | a plan decision has no implementation | code-vs-plan reviewer, close fails |
| P-7 | a material deviation filed as minor | code-vs-plan reviewer reclassifies it, the run stops |
| P-8 | compose gains a key mount | `qa-deploy` |
| P-9 | plan files differ from `origin/main` | preflight refuses to start |
| P-10 | Codex unavailable | the Claude fallback runs; the report names the fallback and the reason |
| P-11 | the agent edits `services/` with no active approved slice | Claude Code hook refuses |
| P-12 | the agent commits before `slice-close` passes | Claude Code hook refuses |

## Increment 3 — pilot acceptance
- The pilot slice goes from grill-me to a pushed branch with no manual steps other than the plan
  PR merge.
- Its own test plan uses the expected-outcome table, including the corrected `M2-T7` and the
  invariant matrix rows for REQ-SEC-K1/K2/S1.
- Every place the pipeline stopped, misbehaved or needed help is recorded and fixed or logged.

## Assumptions and fixtures
- Default E2E mode uses deterministic mocks; live Jira stays env-gated (`M5-T55`).
- The fault injections attach or detach a container from a network (`docker network connect`/`disconnect`) or stop a service, and restore it in a trap. They run only in the `tests` profile.
- The time-dependent checks (non-root expiry, exception expiry) take an injectable clock.
- The `07520d7` replay uses `git show` of the compose file; it does not check out old code.

## Planned verification commands
- `make tooling-test`, `make test-lint`, `make qa-deploy`
- `make qa-quality` (`qa-trace`, traceability, unit guard, `docs-check`)
- `make unit-trust`
- Full E2E on a clean stack, locally and in the CI E2E job; `make qa-evidence` on both
- `make slice-close SLICE=agentic-delivery-process` once it exists (1C onward)

## Review notes
- Rows marked *probe* are pinned against the stack as it was before the change and shown in the
  1A PR with the probe output; if a probe contradicts a *plan* row, the test author escalates (TCR
  rules) instead of adjusting the row.
- New twin tests (for M2.5-T1, M3.S2-T3, M3.S2-T5, and an M1 positive attestation if none exists)
  get `docs/test_spec.md` entries in the same change.
