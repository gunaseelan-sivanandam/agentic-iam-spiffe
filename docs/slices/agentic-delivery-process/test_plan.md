# Slice Test Plan — agentic-delivery-process

Status: **for review** with [`plan.md`](plan.md) (2026-10-28).

## Goal
Prove that every gate this slice adds fails on the input it exists to catch (a negative control
per check), that the tightened E2E tests fail on the wrong failure, and that the pipeline stops or
refuses where the plan says it must. A gate without a failing negative control does not count as
delivered.

## Inputs
- Approved [`plan.md`](plan.md): decisions D1–D16, lanes, the `REQ-SEC-*` requirements.
- Existing requirement REQ-M2-R5.

## Expected-outcome table format (D4)
Every slice `test_plan.md` from now on uses this table for each E2E test it adds or changes. The
test author copies each row into the test's `expect:` block in `trace/tests.yaml`; a gate fails if
they disagree.

| Column | Meaning |
| --- | --- |
| Test | harness ID |
| Kind | a kind from the registry below; a test with a compound outcome has one row per clause (for example M5-T14: `http_denial` 400 `payload_invalid` **and** `upstream_calls` 0) |
| By | the component that must produce the outcome (for example `tool-b`, `tool-b-envoy`, `spire-server`) |
| Signature | exact observable outcome: status + `reason` for HTTP; curl exit code + alert for TLS; resolver result for DNS; exact log line for attestation |
| Twin | positive control on the same route: a test ID, or `internal` when the test itself performs the allowed case first |
| Tier | derived by the gate, not chosen: `replay+twin`, or `replay+twin+fault` for `tls_reject`, `network_unreachable`, `dns_*` and `REQ-SEC` tests |
| Source | `plan` (decided here), `probe` (pinned in the test phase by probing the stack as it was before the change, recorded as `probe@<commit>`), or `existing` (copied from an assertion that is already exact, recorded as `existing@<commit>`, and still subject to the replay) |

### Kind registry (`trace/expect_kinds.yaml`)
The first draft listed only the kinds the 15 loose checks needed. The registry must cover every
outcome the 120 tests check, positive ones included, so that the same precision applies to all of
them. Kinds are a closed vocabulary: a test may not use an unregistered kind, and adding or changing
a kind is a full-slice contract change that ships with its wrong-failure fixtures and a tooling test
(T-21). Initial set:

| Kind | Signature fields | Wrong failures the replay must reject | Example tests |
| --- | --- | --- | --- |
| `http_allow` | status, `by`, body or key fields | any non-2xx; 200 from the wrong component; empty body | M3.S4-T2, M5-T3 |
| `http_denial` | status, `error`, `reason`, `by` (service or Envoy) | right status with another reason; same reason from another component; 5xx; connection failure | M3.S4-T4, M3.S2-T2, M5-T21 |
| `mcp_result` | JSON-RPC result or error object, tool list or `isError` and message | non-JSON-RPC output; diagnostics on stdout; another error | M5-T1, M5-T2 |
| `tls_reject` | curl exit code, TLS alert, rejecting `by` | timeout; refused; an HTTP status after a completed handshake | M2-T2, M2-T3, M2-T9 |
| `network_unreachable` | curl exit 28 to a pinned IP | refused; DNS failure; any HTTP response | M2.5-T1 |
| `dns_unresolvable` | resolver result (NXDOMAIN or no answer) for a name | resolves but refused; resolver down | M3.S2-T3, M3.S2-T5 |
| `attestation_reject` | exact SPIRE server log line | another attestation error; server down | M1-T1..T4 |
| `svid_unavailable` | exact Workload API error and its cause (no socket, no entry) | the other cause; agent down | M1-T5, M2-T5, M2-T6 |
| `file_unreadable` | path absent or permission denied, as declared | the other of the two; container not running | M2-T7 |
| `secret_absent` | stream checked, forbidden patterns, and a canary the detector must find in the same stream | empty or missing stream; a detector that finds nothing, canary included | M5-T26, M5-T27, M5-T28, M5-T45, M5-T53 |
| `state_equals` | store, key, exact value or TTL bound, or "unchanged" | missing key read as zero; store down; value from another root token | M2-T8, M4-T2, M4-T13, M5-T34, M5-T35 |
| `upstream_calls` | exact call count at the mock, per route | counter missing or mock down read as zero | M4a-T4, M4b-T4, M5-T25 |
| `audit_event` | event type, required fields, correlation ids | event from another request; missing field; stale file | M4-T9, M4-T10, M5-T36..T38 |
| `response_shape` | exact key set and size bounds | extra keys; truncated or empty response | M5-T4, M5-T5 |
| `process_exit` | exit code **and** message | another exit code; crash with a trace; a non-zero exit alone | M5-T46 |
| `env_gated_skip` | the declared gate and its premise evidence | an exercise artifact present; gate not declared | M5-T55 |

1A assigns every one of the 120 tests a kind. A test that fits none stops 1A with an escalation
that proposes a new kind; it is not forced into the nearest one.

## E2E plan — Increment 1A: tighten the existing loose checks
Every test gets an `expect:` block in 1A, not only the loose ones below. A test whose current
assertion is already exact gets it copied as `existing@<commit>`; that list is generated in 1A and
reviewed in the 1A PR. The table below covers the checks that change. Signatures marked *probe*
are confirmed against the running stack in 1A and reviewed in the 1A PR (plan review note 3). All
others come from reading the service code. The lint baseline replay (T-22) may find loose checks
this table misses (for example `M5-T46` asserts "the strict run exits non-zero"); each one found
is added to the 1A PR with its row.

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
- T-21 Kind registry: an `expect:` with an unregistered kind fails; a registered kind without
  wrong-failure fixtures or without a tooling test fails.
- T-22 Lint baseline replay: `test-lint` on the harness at `20c074e` reports exactly the loose
  checks the 1A PR lists, no more and no fewer; after 1A it reports none.
- T-23 Absence checks: a `secret_absent` test fails when its canary is not found in the same
  stream (empty log, wrong file, blind detector).
- T-24 Zero counts: an `upstream_calls: 0` or `state_equals: unchanged` test fails when the counter
  or key is missing or the mock or store is down; missing is never read as zero.
- T-25 Fault-injection flip: the fault run's evidence must show the outcome flipping (for example
  the edge container attached to `toolb_app_net` gets 200) and the network restored afterwards; a
  fault run with no flip or no restore fails.

**1B — deployment**
- T-8 Inventory: `docker compose config` facts are extracted per service (mounts and mode, networks, ports, secret env vars, user, capabilities), for services in every profile; a `tests`-profile service with a key mount is caught.
- T-9 Default deny, one fixture each: an extra mount, network, port, secret env var or capability not in `invariants.yaml`; a mount changed from read-only to read-write; a user change; `privileged`, `network_mode: host`, `pid: host`, a Docker socket mount, `devices`.
- T-10 Historical replay: run against `compose/spiffe.compose.yml` of `07520d7`, `qa-deploy` reports `capiss_keys` mounted into `tool-b`. Run against today's compose, it reports OPL-005 and OPL-006 as listed known violations, and fails if their exception entries are removed.
- T-11 Non-root rules:
  - a grandfathered root service is a warning before 2027-01-31 and a failure after it (clock injected);
  - a new root service fails;
  - a migrated service that reverts to root fails.
- T-12 Register consistency: a `REQ-SEC` with no `invariants.yaml` entry fails, and so does an entry with no `REQ-SEC`.
- T-13 Known-violation exceptions: an entry without an OPL id or expiry fails, and so does a past expiry.
- T-26 Asset discovery (D16): on the `07520d7` compose with the `tool-b` key mount registered as
  "public key", discovery still fails on `root_key.b64`; one canary per detected format (PEM private
  key, SPIRE `keys.json`, raw Ed25519 key that derives a trusted public key) is found; a public key
  alone is not reported.
- T-27 Invariant matrix generation: a container added to compose gets matrix rows with no hand
  edit; a row removed by hand fails the consistency check.

**1C — lanes, CI, close-out**
- T-14 Lane classifier, one fixture diff per trigger:
  - each contract file;
  - each new-surface kind;
  - removal of each decision-point kind in a sensitive path;
  - gate, threshold or workflow change;
  - 61 non-test lines, or 4 non-test files;
  - major dependency bump;
  - a sensitive file renamed to a non-sensitive path, a deleted test or `expect:` block, a symlink
    into a sensitive path, a file-mode change (classified by both old and new path).

  The expected lane must be exact for each.
- T-15 Self-rerouting: a PR fixture that edits the classifier's thresholds is classified by `main`'s copy and lands in the full-slice lane.
- T-16 Reproduction on base: a fix-lane regression test that passes on the base commit fails the check, and so does one that fails on base for a reason other than its declared signature (import error, timeout, wrong reason).
- T-17 Changed-line coverage and mutation: one uncovered changed line fails; an unjustified surviving mutant fails; a justified one passes and is listed.
- T-18 `slice-close`: each missing close-out item fails on its own:
  - `test_spec` heading;
  - implementation log entry;
  - STATUS update;
  - red-team report or its "not checked" section;
  - a DEV without the reviewer's confirmation.
- T-19 Git hooks: a commit message with a `Co-Authored-By` trailer is rejected.
- T-20 CI gate job: on a test PR, the job checks out gate code from `main` and fails when the PR edits a gate to always pass (verified on GitHub in 1C).
- T-28 CI E2E job: a test PR that edits the E2E workflow to skip the suite still runs `main`'s job; a PR that adds a workflow job named like a required check fails the gate job; a fork PR is refused (verified on GitHub in 1C).
- T-29 Evidence binding: evidence whose commit SHA or CI run id differs from the PR head and the current run is rejected; local `artifacts/` committed in the PR are ignored.
- T-30 Lanes documentation: the `AGENTS.md` lane table disagreeing with `security/lanes.yaml` fails `docs-check`.
- T-31 Plan gate (D16): a `plan.md` without the "Assets and trust" table, or with a row missing class, holders, `REQ-SEC` link or runtime proof, or "none" without a reason, fails `plan-lint`.
- T-32 Plan-vs-diff (D16): a slice diff adding a mount, secret env var, key path or network not in the plan's asset table fails `slice-close`.
- T-33 Gate registry: a gate in the Makefile or `scripts/` not in `scripts/gates.yaml`, or registered without a negative-control test, fails.
- T-34 Gate mutation: mutation score of the gate code (lane classifier, `qa-evidence`, `qa-deploy`, `test-lint`, replay, `slice-close`, `plan-lint`) at or above 80%; each survivor justified.

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
| P-13 | 3rd accepted TCR on the same test | stop limit |
| P-14 | 4th review-fix round, or the same finding raised twice | stop limit |
| P-15 | 6th full gate run without convergence | stop limit |
| P-16 | run resumed after an escalation answer | restarts at the recorded phase; no phase skipped or repeated (state checked against CI) |
| P-17 | the agent edits a frozen slice bundle | Claude Code hook refuses |
| P-18 | a commit message with a `Co-Authored-By` trailer | Claude Code hook and git hook refuse |
| P-19 | a reviewer's input includes the implementer's reasoning or the run directory | isolation check fails the run |
| P-20 | the code-vs-plan reviewer is configured with the implementer's model | preflight refuses |
| P-21 | the agent's narrative contradicts the evidence (for example "0 TCRs" with 2 filed) | the report uses evidence values and flags the contradiction |
| P-22 | the plan threat reviewer raises a question the plan does not answer | plan PR check fails |
| P-23 | the implementation adds a key mount the plan's asset table does not list | `slice-close` fails (and `qa-deploy`) |

## Test adequacy
A list of tests cannot show it is complete, so adequacy is also measured:
- every gate is registered with its negative controls, and an unregistered gate fails (T-33);
- the gate code is mutation-tested at 80%, a higher bar than the services' 70% because it is the
  trust root (T-34; threshold for approval in this PR);
- `test-lint` must find every loose check already known (T-22);
- the deployment gates must find the defect that started this slice (T-10, T-26).

Known limits, stated so they are not taken for coverage:
- The E2E harness in a PR is code under test. A harness changed to fabricate evidence is caught by
  the full-slice lane, the user's review and the replay controls; it is not made impossible.
- The LLM reviewers (code-vs-plan, red team, plan threat review) are defence in depth, not gates. A
  finding counts only once it becomes a test or a gate.
- The checklist and threat review make an omission in grill-me less likely. Asset discovery and the
  plan-vs-diff check catch omissions only for what they recognise: keys and credentials by content,
  mounts, env vars and networks. A secret in a format the scanner does not know still depends on a
  register entry.

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
- `make tooling-test`, `make test-lint`, `make qa-deploy`, `make plan-lint`
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
