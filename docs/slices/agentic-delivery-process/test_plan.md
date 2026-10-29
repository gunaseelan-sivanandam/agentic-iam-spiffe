# Slice Test Plan — agentic-delivery-process (slice 1)

Status: **for review** with [`plan.md`](plan.md) (2026-10-29), lean scope (D20). Tests for slices 2
and 3, and for the items D20 deferred, are drafts in [`later_slices.md`](later_slices.md).

## Goal
Prove that each check this slice adds fails on the input it exists to catch (a negative control per
check), and that each tightened E2E test asserts exactly one outcome and has a twin. A check without
a failing negative control does not count as delivered.

## Inputs
- Approved [`plan.md`](plan.md): the decisions, the threat model (D18), D20, the `REQ-SEC-*`
  requirements and the known-violation table.

## Expected-outcome table format (D4)
Every slice `test_plan.md` from now on uses this table for each E2E test it adds or changes. The
harness asserts the row exactly; the independent reviewer checks they match.

| Column | Meaning |
| --- | --- |
| Test | harness ID |
| By | the component that must produce the outcome (for example `tool-b`, `tool-b-envoy`, `spire-server`) |
| Signature | exact observable outcome: status + `reason` for HTTP; curl exit code for network; resolver result for DNS; exact log line for attestation |
| Twin | positive control on the same route: a test ID, `new` (added in this slice), or `internal` when the test itself performs the allowed case first |
| Source | `plan`, `probe` (observed on the stack before the change, `probe@<commit>`) or `existing` (`existing@<commit>`) |
| Replaces | the loose assertion it replaces |

## E2E plan — Increment 1A: tighten the existing loose checks
Signatures marked *probe* are confirmed against the stack before any change and shown in the 1A PR
(plan review note 4); the others come from reading the service code. If `test-lint` on the pre-1A
harness flags a loose check this table misses (for example `M5-T46` asserts only "the strict run
exits non-zero"), the 1A PR adds its row.

| Test | By | Signature | Twin | Source | Replaces |
| --- | --- | --- | --- | --- | --- |
| M1-T1 missing_join_token | spire-server | exact rejection log line for a missing token | positive attestation test (named in 1A; new if none exists) | probe | regex `attestation.*fail\|fail.*attest\|…` |
| M1-T2 forged_token | spire-server | exact rejection log line for an unknown token | same | probe | same regex |
| M1-T3 replayed_token | spire-server | exact rejection log line for a used token | same | probe | same regex |
| M2.5-T1 toolb_app_not_reachable | network (edge → toolb_app_net) | curl to the pinned tool-b IP times out (exit 28); never "refused" | new: the same request from a container on `toolb_app_net` returns 200 | probe | `refused\|timed out\|no route` |
| M3.S2-T3 opa_unreachable | edge network | `opa` does not resolve from the edge, **and** a request to OPA's pinned IP times out | new: `opa` resolves and answers from `capiss_app_net` | probe | DNS-vs-TCP warning alternate |
| M3.S2-T5 issuer_app_not_reachable | edge network | `capability-issuer` does not resolve from the edge, **and** its pinned IP times out | new: resolves and answers from `capiss_app_net` | probe | DNS-vs-TCP warning alternate |
| M3.S2-T4 opa_unavailable | capability-issuer | 503, `error=denied`, `reason=opa_unavailable` | M3.S2-T1 | plan | `403\|503` |
| M3.S4-T1 identity_only_denied | tool-b | 401, `reason=missing_token` | M3.S4-T2 | plan | `401\|403` + "no network error" grep |
| M3.S4-T3 rogue_no_token_denied | tool-b | 401, `reason=missing_token` (tool-b-envoy admits the rogue SAN) | M3.S4-T2 | plan, probe confirms | `401\|403` + grep |
| M3.S4-T4 stolen_token_denied | tool-b | 403, `reason=sub_mismatch` | M3.S4-T2 | plan | `401\|403`, `sub_mismatch or invalid_token` + grep |
| M3.S4-T5 expired_token_denied | tool-b | 403, `reason=expired` | M3.S4-T2 | plan | `401\|403` + grep |
| M3.S4-T2 agent_a_token_access | tool-b | 200, expected secret body | — | plan | "no network error" grep |
| M4-T5 budget_enforced_per_root_token | tool-b | 11th call: 403, `reason=budget_exceeded`; calls 1–10: 200 | internal | plan | `401\|403` |
| M4-T6 tampered_token_denied | tool-b | 401, `reason=invalid_token` | M3.S4-T2 | plan | `401\|403` |
| M5-T21 audience_mismatch_denied | capability-issuer | 400, `error=bad_request`, `reason=res`: `aud=jira-tool` with a `jira-mcp:` resource fails resource canonicalization (`canonicalize_resource`) before OPA is called | M5 root-mint allow test (named in 1A) | plan (from code) | `400\|403` |

Also in 1A: `M5-T55`'s skip stays env-gated as today; the other `add_warning` alternates become
exact checks above, or declared alternates with a reason.

## Tooling tests (`tests/tools/`, each with a negative control)
Numbers are kept from earlier drafts; the gaps are tests D20 deferred.

**1A — honest tests**
- T-7 `test-lint` rejects each of these in a guard command, one fixture each:
  - `|| true`;
  - a check on a non-zero exit code alone;
  - `assert_file_any` outside a declared alternate;
  - a broad error regex (`error|fail`, `refused|timed out`);
  - a negative grep used as the only success check;
  - `!= 200` as an assertion.

  It accepts `|| true` in evidence-writing plumbing outside guard strings, and a declared alternate
  with a reason.
- T-22 Lint on the old harness: `test-lint` on the harness at `20c074e` flags every row of the 1A
  table; after 1A it flags nothing.
- T-41 Mutation scoring: 1 killed and 99 `no_tests` fails; `skipped` mutants count as not killed;
  a total of 0 fails; 70.00% passes and 69.99% fails.

**1B — key confinement**
- T-8 Inventory: `docker compose config` facts are extracted per service (image, mounts and mode,
  networks, ports, secret env vars, user, capabilities), for services in every profile; a
  `tests`-profile service with a key mount is caught. A `docker compose config` failure is an error,
  not an empty inventory.
- T-9 Default deny, one fixture each: an image reference not in the register (an approved image
  passes); an extra mount, network, port, secret env var or capability; a mount changed from
  read-only to read-write; a user change; `privileged`, `network_mode: host`, `pid: host`, a Docker
  socket mount, `devices`.
- T-10 Historical check: against `compose/spiffe.compose.yml` of `07520d7` (via `git show`),
  `qa-deploy` reports `capiss_keys` mounted into `tool-b`. Against today's compose it reports
  exactly the known violations, and fails if any row is removed.
- T-11 Non-root rules:
  - a grandfathered root service is a warning at 2027-01-31 23:59:59 UTC and a failure one second
    later (clock injected);
  - a new root service fails;
  - a migrated service that reverts to root fails;
  - the effective user comes from compose `user`, else the built image's `USER`; `root` or UID 0 is
    root; a user that cannot be read counts as root.
- T-12 Register consistency: a `REQ-SEC` with no `invariants.yaml` entry fails, and so does an entry
  with no `REQ-SEC`; adding `tool-b` to K1's holders in `invariants.yaml` while REQ-SEC-K1's
  `Holders:` line is unchanged fails.
- T-13 Known violations: an entry without (OPL, asset, service) or expiry fails; a violation
  matching an entry is reported as known; the same OPL with another service or asset fails; an
  entry whose OPL is closed fails; expiry is valid at 2026-12-31 23:59:59 UTC and fails at
  2027-01-01 00:00:00 UTC.

## Independent review at the implementation PR (D20)
Each of the 1A and 1B PRs carries the reviewer's answers to the two questions in
[`plan.md`](plan.md#independent-review-d17-d20): which wrong failure would still pass each new or
changed test, and whether the change makes a key, socket or secret reachable outside the holder
list. For 1B, the reviewer also checks the baseline look at entrypoints, scripts and Dockerfiles.

## Known limits
Stated so they are not taken for coverage:
- `qa-deploy` sees compose and image facts only. A key copied at runtime (an entrypoint, a script,
  a shared volume) is caught only by the baseline look and the review question.
- The review is judgment, not a mechanical guarantee.
- A deliberately malicious change is outside the threat model (D18, OPL-009).
- Mutation testing mutates covered lines only (`mutate_only_covered_lines = true`).

## Assumptions and fixtures
- Default E2E mode uses deterministic mocks; live Jira stays env-gated (`M5-T55`).
- The new twins for M2.5-T1, M3.S2-T3 and M3.S2-T5 run from a container already on the target
  network; no network is changed during the run.
- The time-dependent checks (non-root expiry, exception expiry) take an injectable clock.
- The `07520d7` check uses `git show` of the compose file; it does not check out old code.

## Planned verification commands
- `make tooling-test`, `make test-lint`, `make qa-deploy`
- `make qa-quality` (`qa-trace`, traceability, unit guard, `docs-check`)
- `make unit-trust` and `make unit-mutation` (new scoring)
- Full E2E on a clean stack and `make qa-evidence`

## Review notes
- New twin tests get `docs/test_spec.md` entries in the same change.
