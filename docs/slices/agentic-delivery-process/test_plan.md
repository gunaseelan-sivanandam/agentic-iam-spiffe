# Slice Test Plan — agentic-delivery-process

Status: **for review** with [`plan.md`](plan.md) (2026-10-28).

## Goal
Prove that every gate this slice adds fails on the input it exists to catch (a negative control
per check), that the tightened E2E tests fail on the wrong failure, and that the pipeline stops or
refuses where the plan says it must. A gate without a failing negative control does not count as
delivered.

## Inputs
- Approved [`plan.md`](plan.md): decisions D1–D17, lanes, the `REQ-SEC-*` requirements.
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

## Test derivation checklist (D17)
From Increment 1C on, every row of a slice `test_plan.md` (E2E, tooling and pipeline tests) also
fills these columns, and `plan-lint` rejects an empty one ("n/a" needs a reason):

| Column | Question |
| --- | --- |
| Catches | Which defect or bad input does this test exist for? |
| Evasions | Was each of these considered: rename, delete, missing, empty, wrong source, wrong commit, wrong time? Which apply and which test covers them? |
| Missing vs zero | Can an absent value, file, counter or service read as the expected value? |
| Wrong-reason pass | What other failure could produce the same observable outcome? |
| Wrong-reason fail | Could the test fail for a reason other than the defect (in red phase, or on base for a fix)? |
| Boundary | Which limits apply, and are B-1, B and B+1 covered? |

This slice's own tooling and pipeline rows carry the columns in the
[derivation appendix](#derivation-appendix) (resolves PR-20).

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
| M5-T21 audience_mismatch_denied | http_denial | capability-issuer | 400, `error=bad_request`, `reason=res`: `aud=jira-tool` with a `jira-mcp:` resource fails resource canonicalization (`canonicalize_resource`) before OPA is called | M5 root-mint allow test (named in 1A) | replay+twin | plan (from code; corrected by review PR-03) | `400\|403` |

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
  - a grandfathered root service is a warning on 2027-01-31 23:59:59 UTC and a failure at 2027-01-31 + 1 s (clock injected; one second earlier is also a warning);
  - a new root service fails;
  - a migrated service that reverts to root fails;
  - effective user (PR-11): no compose `user` and image `USER root` is root; a named user that maps to UID 0 is root; an entrypoint that drops privileges is judged by the runtime UID of every process (`docker top` from the controller); missing image metadata or a controller error is "unknown", which counts as root.
- T-12 Register consistency: a `REQ-SEC` with no `invariants.yaml` entry fails, and so does an entry with no `REQ-SEC`. Semantics (PR-10): `invariants.yaml` adding `tool-b` to K1's holders while REQ-SEC-K1's `Holders:` line is unchanged fails; widening an S1 operation the same way fails.
- T-13 Known-violation exceptions (PR-13): an entry without an exact tuple (OPL id, asset, service, path or key family, operation) or expiry fails; an observed violation matching a tuple is reported as known; the same OPL with another service, asset, path or operation fails; an exception whose OPL is closed fails; a new, widened or renewed tuple outside a full slice's contract delta fails; expiry is valid at 2026-12-31 23:59:58 and 23:59:59 UTC and fails at 2027-01-01 00:00:00 UTC.
- T-26 Asset discovery (D16): on the `07520d7` compose with the `tool-b` key mount registered as
  "public key", discovery still fails on `root_key.b64`; one canary per detected format (PEM private
  key, SPIRE `keys.json`, raw Ed25519 key that derives a trusted public key) is found; a public key
  alone is not reported.
- T-27 Invariant matrix generation: a container added to compose gets matrix rows with no hand
  edit; a row removed by hand fails the consistency check.

### Runtime invariant matrix (1B) — assertion templates (resolves PR-06)
Generated for every asset in REQ-SEC-K1–K8 × every running container. Each row's evidence records
the container ID and image digest inspected, checked against the running compose project, so a row
cannot pass by inspecting the wrong container.

| Template | Applies to | Assertion | Wrong failure it rejects |
| --- | --- | --- | --- |
| Holder positive | each allowed holder | the asset exists and is genuine: K1 private key derives the public key verifiers trust; K2/K4 `keys.json` parses and holds a private key; K3 env var present, its SHA-256 equals the injected value's (value never printed); K7 SVID key matches its certificate | assets never generated; renamed file; empty env var |
| Non-holder negative | every other container | a content scan of every readable path (not just the expected one) and the environment finds no instance (K3 by hash) | scan of only the expected path; asset copied to another path |
| Scan sanity | per run | canaries of each format (generated per run, trusted by nothing) planted in the test-only `rogue` container are found; otherwise the matrix fails | blind scanner; wrong container; empty filesystem view |
| Socket rows (K5, K8) | every container | non-holders have no Unix socket that answers the SPIRE admin API or the Docker API, at any path | socket mounted under another path |
| Known violation | listed tuples | a violation matching a tuple exactly is reported with its OPL and expiry; anything else fails | an exception hiding a new holder |
| Fault injection (REQ-SEC tier) | K1–K8 | a test-only overlay mounts a canary into `tool-b`; the matrix must fail, then pass again once removed | a matrix that can never fail |
| S1 (pilot) | each principal | unauthenticated `PING` → `NOAUTH`; each allowed operation in REQ-SEC-S1 succeeds (twin); each forbidden one (raw `SET`/`INCRBY`/`DECRBY`/`DEL` on budget, registry or marker keys, a verifier writing `m4:capiss_minted:*`, `FLUSHALL`, `CONFIG`, a negative-cost script call) fails with `NOPERM` or the script's error | allowed by accident; denied for an unrelated reason (Redis down) |

Until the pilot, the S1 rows run against the OPL-007 known-violation tuple.

**1C — lanes, CI, close-out**
- T-14 Lane classifier, one fixture diff per trigger:
  - each contract file;
  - each new-surface kind;
  - removal of each decision-point kind in a sensitive path;
  - gate, threshold or workflow change;
  - 60 non-test lines and 3 non-test files (fix lane); 61 lines, or 4 files (full slice); a full slice over the cap is not rejected for size (PR-17);
  - major dependency bump;
  - a sensitive file renamed to a non-sensitive path, a deleted test or `expect:` block, a symlink
    into a sensitive path, a file-mode change (classified by both old and new path).

  The expected lane must be exact for each.
- T-15 Self-rerouting: a PR fixture that edits the classifier's thresholds is classified by `main`'s copy and lands in the full-slice lane.
- T-16 Reproduction on base: a fix-lane regression test that passes on the base commit fails the check, and so does one that fails on base for a reason other than its declared signature (import error, timeout, wrong reason). Runs in `execute`, judged by `verify`.
- T-17 Changed-line coverage and mutation: one uncovered changed line fails; an unjustified surviving mutant fails; a justified one passes and is listed.
- T-18 `slice-close`: each missing close-out item fails on its own:
  - `test_spec` heading;
  - implementation log entry;
  - STATUS update;
  - red-team report or its "not checked" section;
  - a DEV without the reviewer's confirmation.
- T-19 Git hooks: a commit message with a `Co-Authored-By` trailer is rejected.
- T-20 Candidate gates (PR-02): a test PR that edits a gate to always pass is judged by `main`'s gate, and `candidate-gate` runs `main`'s registered negative controls against the PR's gate, which fails them; a correct candidate passes them (verified on GitHub in 1C).
- T-28 CI jobs: a test PR that edits the workflows to skip the suite still runs `main`'s jobs; a PR that adds a workflow job named like a required check fails `gate`; a fork PR is refused (verified on GitHub in 1C).
- T-29 Evidence binding: evidence whose commit SHA or CI run id differs from the PR head and the current run is rejected; local `artifacts/` committed in the PR are ignored.
- T-41 Mutation scoring (PR-05): 1 killed and 99 `no_tests` fails; `skipped`, timeout and suspicious mutants count as not killed unless individually justified; total 0 fails; a module in the gate list missing from the run fails; an interrupted run fails; a justified equivalent mutant is excluded and listed.
- T-42 Outcome provenance (PR-16): `probe@<c>` where `c` is not an ancestor of the PR base, or whose probe artifact records another commit or other image digests, fails; a probe recorded after the first implementation commit fails; `existing@<c>` where the harness at `c` does not contain that exact assertion, or contains one `test-lint` rejects, fails.
- T-43 Contract delta (PR-12): a PR whose contract-data change equals the approved `contract_delta.yaml` on `main` passes; one extra entry, a changed holder, or a delta from an earlier plan revision fails.
- T-44 Execution isolation (PR-01): in `execute`, the harness container has no Docker socket and cannot write the controller's evidence directory or the repository; a PR compose adding the Docker socket, a host mount, `privileged` or an unpinned image to any service fails static `qa-deploy` before bring-up; evidence the PR harness writes for a test that exists on `main` is ignored in favour of `main`'s harness evidence.
- T-30 Lanes documentation: the `AGENTS.md` lane table disagreeing with `security/lanes.yaml` fails `docs-check`.
- T-31 Plan gate (D16): a `plan.md` without the "Assets and trust" table, or with a row missing class, holders, `REQ-SEC` link or runtime proof, or "none" without a reason, fails `plan-lint`.
- T-32 Plan-vs-diff (D16): a slice diff adding a mount, secret env var, key path or network not in the plan's asset table fails `slice-close`.
- T-33 Gate registry: a gate in the Makefile or `scripts/` not in `scripts/gates.yaml`, or registered without a negative-control test, fails.
- T-34 Gate mutation: mutation score of the gate code (lane classifier, `qa-evidence`, `qa-deploy`, `test-lint`, replay, `slice-close`, `plan-lint`) at or above 80%; each survivor justified.
- T-35 Check removal (corrected by review PR-04): the runner fails when a removed decision point is killed by no mapped test (fixture service and test pair); on capiss, changing the `opa_unavailable` response from 503 to 403 with the same reason is survived by the pre-1A `M3.S2-T4` (it accepts `403|503` and checks only the reason) and killed by the tightened one (exact 503).
- T-36 Mapping drift: a decision point killed only by a test not mapped to its file fails the nightly run until the mapping is corrected.
- T-37 Mutation ratchet (PR-18): lowering a threshold fails outside the full-slice lane and inside it unless the approved contract delta names the decrease; a full slice that closes without the +5 service raise fails, one that raises past 85% fails, one at 85% stays; missing threshold history fails.
- T-38 Escape corpus: a corpus fixture the suite does not catch fails; removing a fixture outside the full-slice lane fails.
- T-39 Escape review: an OPL entry marked closed without a "why no test caught it" section and its checklist addition fails `docs-check`.
- T-40 Derivation and complete sets: a `test_plan.md` row with an empty derivation column fails `plan-lint`; a test, service, decision point, kind or `REQ-SEC` missing from its enumerated coverage fails.

## Pipeline self-tests — Increment 2 (seeded faults, run on a fixture slice)
Each seeded fault must end in a stop or a failure at the named point, never in a handoff.

| # | Seeded fault | Must be caught by |
| --- | --- | --- |
| P-1 | implementer edits a test file | path-scope check after the implement phase |
| P-2 | implementer edits an `expect:` block | path-scope check |
| P-3 | test author's new test fails for the wrong red-phase reason | test-phase exit gate |
| P-4 | a TCR loosening an assertion is accepted | anti-weakening check (base rerun or weakened-assertion list); the PR body shows it |
| P-5 | 3rd accepted TCR in a slice / 4th | the run continues / stop limit, `escalation.md` written, notification sent |
| P-6 | a plan decision has no implementation | code-vs-plan reviewer, close fails |
| P-7 | a material deviation filed as minor | code-vs-plan reviewer reclassifies it, the run stops |
| P-8 | compose gains a key mount | `qa-deploy` |
| P-9 | plan files differ from `origin/main` | preflight refuses to start |
| P-10 | Codex unavailable | the Claude fallback runs; the report names the fallback and the reason |
| P-11 | the agent edits `services/` with no active approved slice | Claude Code hook refuses |
| P-12 | the agent commits before `slice-close` passes | Claude Code hook refuses |
| P-13 | 2nd accepted TCR on the same test / 3rd | continues / stop limit |
| P-14 | 3rd review-fix round / 4th, or the same finding raised twice | continues / stop limit |
| P-15 | 5th full gate run without convergence / 6th | continues / stop limit |
| P-16 | run resumed after an escalation answer | restarts at the recorded phase; no phase skipped or repeated (state checked against CI) |
| P-17 | the agent edits a frozen slice bundle | Claude Code hook refuses |
| P-18 | a commit message with a `Co-Authored-By` trailer | Claude Code hook and git hook refuse |
| P-19 | a reviewer's input includes the implementer's reasoning or the run directory | isolation check fails the run |
| P-20 | the code-vs-plan reviewer is configured with the implementer's model | preflight refuses |
| P-21 | the agent's narrative contradicts the evidence (for example "0 TCRs" with 2 filed) | the report uses evidence values and flags the contradiction |
| P-22 | the plan threat reviewer raises a question the plan does not answer | plan PR check fails |
| P-23 | the implementation adds a key mount the plan's asset table does not list | `slice-close` fails (and `qa-deploy`) |
| P-24 | the plan PR is opened while `plan_review.md` has an open finding, or without `plan_review.md` | `slice-grill` refuses; the plan PR check fails |
| P-25 | the plan reviewer's input includes the author's reasoning or transcript, or the reviewer is the author's model | isolation check fails the review |
| P-26 | a fixture plan with seeded gaps (a missing evasion, an untested decision, an unlisted asset, a contradiction with `requirements.md`) | the reviewer must find every blocker-class gap and at least 80% of the rest; a lower rate, zero, or a missing result blocks its use (PR-19) |
| P-27 | the adversarial gate reviewer finds an evasion | handoff is blocked until a test for it exists and fails without the fix |
| P-28 | the 3rd plan review round / 4th, or the same plan finding twice | continues / stop limit, `escalation.md` |
| P-29 | the implementer stages, commits or leaves untracked a test change; deletes a TCR record; force-pushes the ledger | phase-commit scope check; clean-tree check; counts from the ledger; ruleset refuses (PR-14) |
| P-30 | the ledger branch is missing or unreadable | the run stops |
| P-31 | the agent identity tries to approve or merge its own PR | GitHub refuses (PR-08) |
| P-32 | an agent role reads the owner's credential files | hook refuses |
| P-33 | `plan_review.md` edited after the review; plan files changed after the last round; a finding marked resolved without a reviewer round | `plan-review` check fails (PR-15) |
| P-34 | the reviewer errors (expired login, refused model, empty output) | recorded as "review did not run", never as "no findings"; fallback per D11 |

## Test adequacy
A list of tests cannot show it is complete, so adequacy is measured by the faults it catches (D17):
- removing any single decision point in a sensitive path must fail a mapped E2E test with its
  declared signature (T-35, T-36);
- mutation thresholds never fall except by an approved contract delta: gate code 80%, services 75%
  after the pilot and +5 per full slice until 85%, scored without hiding untested mutants (T-34,
  T-37, T-41);
- every escaped defect stays in a corpus the suite must catch (T-38), and each closed OPL adds the
  question that would have caught it (T-39);
- every gate is registered with its negative controls (T-33), and `test-lint` must find every loose
  check already known (T-22);
- an independent reviewer checks the plan and test plan before the user does, and its detection
  rate on seeded gaps is tracked (P-24..P-26).

Known limits, stated so they are not taken for coverage:
- The E2E harness in a PR is code under test. A harness changed to fabricate evidence is caught by
  the full-slice lane, the user's review and the replay controls; it is not made impossible.
- The LLM reviewers (independent plan review, adversarial gate review, code-vs-plan, red team) are
  defence in depth, not gates. A finding counts only once it becomes a test, a gate or a plan
  change; calibration (P-26) shows how much they catch, not that they catch everything.
- Check removal covers the decision points it can enumerate. Behaviour that comes from
  configuration values rather than a removable check (a timeout, a TTL) is covered by the mutation
  ratchet and boundary rows instead.
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

## Derivation appendix
The D17 columns for this slice's own tooling and pipeline rows. "Catches" is the row's text above.
Evasion codes: **rn** rename, **del** delete, **mis** missing, **emp** empty, **src** wrong source,
**cmt** wrong commit, **tm** wrong time. "n/a" carries its reason.

| Test | Evasions considered → covered by | Missing vs zero | Wrong-reason pass | Wrong-reason fail | Boundary |
| --- | --- | --- | --- | --- | --- |
| T-1 | rn/del of `expect:` keys → schema rejects unknown and missing keys; emp signature → rejected | missing block on a negative test fails, never defaults | schema accepts a typo'd key: unknown keys rejected | n/a: static parse | n/a: no numeric limit |
| T-2 | src (row edited only in `tests.yaml`) → both sides compared; del of a row → T-40 sets | missing row ≠ match | whitespace or case differences: compared after one normalisation, listed in the test | n/a: static | n/a |
| T-3 | src (observed file from another test) → test ID inside the file checked; cmt → T-29 | missing `observed_signature.json` fails | equal status, other reason → fixture | malformed JSON reported as malformed, not as mismatch | n/a |
| T-4 | emp evidence; evidence of another test → fixtures per kind | empty evidence directory fails the guard | each wrong-failure fixture per kind | true evidence must still pass (positive control) | n/a |
| T-5 | rn of kind without plan change → fixture; del of fault evidence → fixture | missing fault evidence fails | fault run that did not flip → T-25 | n/a: static derivation | n/a |
| T-6 | src (twin from an earlier run) → run ID compared | twin absent from the run fails | twin passed on another route → route compared | n/a | n/a |
| T-7 | one fixture per pattern; pattern split across lines; via a helper function → helper bodies linted | n/a: lint over text | `|| true` in plumbing must pass (positive control) | n/a | n/a |
| T-8 | profiles → all-profile config; override files → same merged config the stack uses | a service missing from the inventory fails against the compose service list | n/a | `docker compose config` failure is an error, not an empty inventory | n/a |
| T-9 | rn of a mount target → compared by source and target; mode change → fixture | missing register entry for a service fails | n/a | n/a | n/a |
| T-10 | cmt → `git show` of a named commit, hash checked | missing exception entry → failure expected and asserted | n/a | `git show` failure is an error, not a pass | n/a |
| T-11 | src of user (compose vs image vs process) → all three; tm → injected clock | unknown user = root | n/a | controller error counts as unknown, reported | 2027-01-31 23:59:58/59 warning, +1 s fail |
| T-12 | widened holder without requirement change → fixture | REQ without entry and entry without REQ both fail | n/a | n/a | n/a |
| T-13 | widened tuple, renewed tuple, closed OPL → fixtures; tm → injected clock | missing expiry fails | n/a | n/a | 2026-12-31 23:59:58/59 valid, 2027-01-01 00:00:00 fail |
| T-14 | rn, del, symlink, mode change → fixtures | n/a: every diff gets a lane | n/a | n/a | 60/3 fix; 61 or 4 full slice |
| T-15 | src (PR copy of the classifier) → `main`'s copy used | n/a | n/a | n/a | n/a |
| T-16 | src (test passes on base because it was never run) → run evidence required | missing base run fails | fails on base for another reason → fixture | flaky failure → rerun once, both must fail the same way | n/a |
| T-17 | del of covered lines (deletions) → structural diff, not line coverage, judges them | missing coverage data fails | n/a | n/a | 100% required: 1 uncovered line fails |
| T-18 | one fixture per missing item; emp sections → fixture | missing file fails | n/a | n/a | n/a |
| T-19 | trailer in body vs footer, other casing → fixtures | n/a | n/a | n/a | n/a |
| T-20 | candidate gate that passes only on the fixtures → registry negatives are kept on `main` only | missing negative-control result fails | n/a | candidate gate crashing counts as failing its controls | n/a |
| T-21 | rn of kind; kind added without fixtures → fixture | missing registry fails | n/a | n/a | n/a |
| T-22 | baseline harness from another commit → hash pinned | missing finding or extra finding both fail | n/a | n/a | exact set equality |
| T-23 | emp stream, wrong file, blind detector → fixtures | missing stream fails | canary found in another stream → stream path compared | n/a | n/a |
| T-24 | mock down, counter missing → fixtures | missing ≠ 0, the point of the test | n/a | n/a | count 0 vs 1 |
| T-25 | no flip, no restore → fixtures | missing restore evidence fails | flip caused by another change → only the injected fault differs between runs | n/a | n/a |
| T-26 | rn of key file, label "public" → content scan | missing canary detection fails | public key alone must not be reported (positive control) | n/a | 32- and 64-byte keys; 31 and 33 bytes not keys |
| T-27 | del of a row by hand → fixture | missing container fails | n/a | n/a | n/a |
| T-28 | workflow skip, name collision, fork → GitHub fixtures | n/a | n/a | GitHub outage → job error, never pass | n/a |
| T-29 | cmt, other run, committed artifacts → fixtures | missing SHA or run id fails | n/a | n/a | n/a |
| T-30 | rn of section → anchored heading | missing section fails | n/a | n/a | n/a |
| T-31 | emp table, "none" without reason → fixtures | missing table fails | n/a | n/a | n/a |
| T-32 | asset added under a new name → content (T-26) and diff both checked | n/a | n/a | n/a | n/a |
| T-33 | gate added under a new Makefile name → registry built from the Makefile | missing registration fails | n/a | n/a | n/a |
| T-34 | survivors relabelled equivalent → each needs a reviewed justification | see T-41 | n/a | n/a | 79.99% fails, 80% passes |
| T-35 | mapping that points at an always-failing test → the killing test must fail with its declared signature | no mapped test = failure | killed by a crash → signature checked | n/a | n/a |
| T-36 | test mapped to the wrong file → nightly full-suite comparison | missing mapping fails | n/a | n/a | n/a |
| T-37 | decrease inside a full slice without delta → fixture; tm (history rewritten) → history from `main` | missing history fails | n/a | n/a | 84→85 ok, 85→85 ok, 85→90 fails |
| T-38 | fixture removed or renamed → corpus list on `main` | missing fixture fails | n/a | n/a | n/a |
| T-39 | section present but empty → fixture | missing section fails | n/a | n/a | n/a |
| T-40 | emp column, "n/a" without reason → fixtures | missing set member fails | n/a | n/a | n/a |
| T-41 | relabelled skipped/no_tests, partial run → fixtures | 0 total fails | n/a | n/a | 1 of 100 killed with 99 no_tests fails |
| T-42 | cmt (non-ancestor), probe of candidate, broad existing → fixtures | missing probe artifact fails | n/a | n/a | probe at first implementation commit fails, at its parent passes |
| T-43 | extra entry, changed holder, older plan revision → fixtures | missing delta file fails any contract-data change | n/a | n/a | n/a |
| T-44 | Docker socket under another path, host mount, privileged, unpinned image → fixtures | n/a | PR harness evidence for an existing test → ignored | controller failure is an error, not a pass | n/a |
| P-1, P-2, P-29 | staged, committed, untracked, deleted, force-pushed → P-29 | missing ledger → P-30 | n/a | n/a | n/a |
| P-3 | red phase failing on import error → signature compared | missing red evidence fails | n/a | n/a | n/a |
| P-4 | loosened assertion hidden in a helper → base rerun | n/a | n/a | n/a | n/a |
| P-5, P-13, P-14, P-15, P-28 | counter reset by deleting records → ledger | missing ledger → stop | n/a | n/a | at limit continues, limit + 1 stops |
| P-6, P-7 | decision implemented in an unrelated file → reviewer maps decision to code | n/a | n/a | n/a | n/a |
| P-8, P-23 | mount added under a new name → content scan | n/a | n/a | n/a | n/a |
| P-9 | plan edited after merge on the branch → digest compare | missing plan on `main` refuses | n/a | n/a | n/a |
| P-10, P-34 | reviewer error read as "no findings" → P-34 | empty output = did not run | n/a | n/a | n/a |
| P-11, P-12, P-17, P-18, P-32 | edits via shell instead of the edit tool → hooks on shell commands too | n/a | n/a | n/a | n/a |
| P-16 | resume at a later phase → ledger | missing ledger → stop | n/a | n/a | n/a |
| P-19, P-20, P-25 | reasoning passed via a file in the input set → input list fixed by the script | n/a | n/a | n/a | n/a |
| P-21 | narrative numbers in a table → every number from evidence | n/a | n/a | n/a | n/a |
| P-22, P-24, P-33 | report edited, stale digest → P-33 | missing report fails | n/a | n/a | n/a |
| P-26 | rate computed over fewer seeds → seed list on `main` | missing result blocks | n/a | n/a | 80% passes, below fails; any blocker-class miss fails |
| P-27 | evasion test added but passing without the fix → must fail without it | n/a | n/a | n/a | n/a |
| P-30 | n/a | the point of the test | n/a | n/a | n/a |
| P-31 | approval through the API vs UI → both refused by the ruleset | n/a | n/a | n/a | n/a |
