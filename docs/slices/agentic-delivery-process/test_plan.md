# Slice Test Plan — agentic-delivery-process (slice 1)

Status: **for review** with [`plan.md`](plan.md) (2026-10-29). Slice 1 of three (D19); tests for
slices 2 and 3 are drafts in [`later_slices.md`](later_slices.md).

## Goal
Prove that every gate this slice adds fails on the input it exists to catch (a negative control
per check), and that the tightened E2E tests fail on the wrong failure. A gate without a failing
negative control does not count as delivered.

## Inputs
- Approved [`plan.md`](plan.md): decisions D1–D19, the threat model (D18), the `REQ-SEC-*`
  requirements and the known-violation table.
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
Every row of a slice `test_plan.md` (E2E, tooling and pipeline tests) also fills these columns;
"n/a" needs a reason. `plan-lint` enforces it from slice 2; until then the independent review does:

| Column | Question |
| --- | --- |
| Catches | Which defect or bad input does this test exist for? |
| Evasions | Was each of these considered: rename, delete, missing, empty, wrong source, wrong commit, wrong time? Which apply and which test covers them? |
| Missing vs zero | Can an absent value, file, counter or service read as the expected value? |
| Wrong-reason pass | What other failure could produce the same observable outcome? |
| Wrong-reason fail | Could the test fail for a reason other than the defect (in red phase, or on base for a fix)? |
| Boundary | Which limits apply, and are B-1, B and B+1 covered? |

This slice's rows (tooling tests, the 1A E2E rows and the matrix templates) carry the columns in
the [derivation appendix](#derivation-appendix) (resolves PR-20).

## E2E plan — Increment 1A: tighten the existing loose checks
Every test gets an `expect:` block in 1A, not only the loose ones below. A test whose current
assertion is already exact gets it copied as `existing@<commit>`; that list is generated in 1A and
reviewed in the 1A PR. The table below covers the checks that change. Signatures marked *probe*
are confirmed against the running stack in 1A and reviewed in the 1A PR (plan review note 4). All
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

- T-41 Mutation scoring (PR-05): 1 killed and 99 `no_tests` fails; `skipped`, timeout and suspicious mutants count as not killed unless individually justified; total 0 fails; a module in the gate list missing from the run fails; an interrupted run fails; a justified equivalent mutant is excluded and listed.
- T-42 Outcome provenance (PR-16): the commit in `probe@<c>` and `existing@<c>` must be the PR's merge-base with `main`; a probe artifact must be committed in a commit whose diff from the merge-base touches nothing under `services/`, `compose/`, `policy/`, `spire/` or the Envoy configs, and which precedes every commit that does; `existing@<c>` fails when the harness at `c` does not contain that exact assertion or contains one `test-lint` rejects. Fixtures: another commit, a probe taken after a service change, a broad existing assertion.

**1B — deployment**
- T-8 Inventory: `docker compose config` facts are extracted per service (image, mounts and mode, networks, ports, secret env vars, user, capabilities), for services in every profile; a `tests`-profile service with a key mount is caught.
- T-9 Default deny, one fixture each: an image reference or digest not in the register (an approved image passes, PR-36); an extra mount, network, port, secret env var or capability not in `invariants.yaml`; a mount changed from read-only to read-write; a user change; `privileged`, `network_mode: host`, `pid: host`, a Docker socket mount, `devices`.
- T-10 Historical replay: run against `compose/spiffe.compose.yml` of `07520d7`, `qa-deploy` reports `capiss_keys` mounted into `tool-b`. Run against today's compose, it reports the OPL-005, OPL-006 and OPL-008 tuples as known violations, and fails if any tuple is removed.
- T-11 Non-root rules:
  - a grandfathered root service is a warning on 2027-01-31 23:59:59 UTC and a failure at 2027-01-31 + 1 s (clock injected; one second earlier is also a warning);
  - a new root service fails;
  - a migrated service that reverts to root fails;
  - effective user (PR-11): no compose `user` and image `USER root` is root; a named user that maps to UID 0 is root; an entrypoint that drops privileges is judged by the runtime UID of every process (`docker top`, run by the harness); missing image metadata or a `docker` error is "unknown", which counts as root.
- T-12 Register consistency: a `REQ-SEC` with no `invariants.yaml` entry fails, and so does an entry with no `REQ-SEC`. Semantics (PR-10): `invariants.yaml` adding `tool-b` to K1's holders while REQ-SEC-K1's `Holders:` line is unchanged fails; widening an S1 operation the same way fails.
- T-13 Known-violation exceptions (PR-13): an entry without an exact tuple (OPL id, asset, service, path or key family, operation) or expiry fails; an observed violation matching a tuple is reported as known; the same OPL with another service, asset, path or operation fails; an exception whose OPL is closed fails; a new, widened or renewed tuple without an approved plan change fails; expiry is valid at 2026-12-31 23:59:58 and 23:59:59 UTC and fails at 2027-01-01 00:00:00 UTC.
- T-26 Asset discovery (D16): on the `07520d7` compose with the `tool-b` key mount registered as
  "public key", discovery still fails on `root_key.b64`. One unauthorized-copy fixture per asset
  class K1–K8 (each detector in the matrix section) is found, including a renamed copy; also found:
  an asset present only in a stopped container's bind mount, another agent's key-manager file inside
  an allowed K2 holder, and another workload's private key copied without its certificate; a public
  key alone is not reported; a canary key is found because its public key is in the run's trusted
  set (resolves PR-26).
- T-27 Invariant matrix generation: a container added to compose gets matrix rows with no hand
  edit; a row removed by hand fails the consistency check.

### Runtime invariant matrix (1B) — assertion templates (resolves PR-06, PR-26)
Generated for every asset class in REQ-SEC-K1–K8 × every configured service in every profile and
lifecycle state. Running containers are inspected through `docker exec`; exited ones (for example
`spire-token-init`) through `docker export` of the stopped container **and** the contents of every
mount source from the inventory, since an export omits mounts (PR-34); services that do not run by
default through their mount sources, reported as "static only". An unreadable mount source is an
error, never a pass. Each row records
the container ID and image digest, checked against the compose project, so a row cannot pass by
inspecting the wrong container.

Detectors work by content, never by file name:

| Class | Detector | Genuine-holder check |
| --- | --- | --- |
| K1 issuer key | a 32- or 64-byte value (raw or base64) that derives a public key in the run's trusted set: the key verifiers trust plus this run's canary public keys | the holder's key derives the public key verifiers trust |
| K2, K4 SPIRE keys | JSON with the SPIRE key-manager structure holding private keys | parses, and every key fingerprint appears in exactly one holder: the agent or server that owns that data directory (PR-35) |
| K4 datastore | an SQLite file whose schema has SPIRE's registration-entry and node tables (any size) | opens and contains the bootstrap entries |
| K3 credential | the SHA-256 of the injected value, across the environment and files up to 1 MiB | env var present, hash equal |
| K6 join token | the SHA-256 of each token issued in this run (read from `spire-token-init`'s output), across files up to 1 MiB | present in the issuer and the agent |
| K7 workload key | any PEM or DER private key that does not match the container's own SVID certificate and is not a registered asset; a key copied without its certificate is reported too (PR-35) | each workload's key matches its own SVID |
| K5, K8 sockets | a Unix socket at any path that answers a SPIRE server API probe or Docker `/_ping` | answers in the holder |

| Template | Applies to | Assertion | Wrong failure it rejects |
| --- | --- | --- | --- |
| Holder positive | each allowed holder | the genuine-holder check passes | asset never generated; renamed file; empty env var |
| Non-holder negative | every other service | the class detector finds nothing | scan of only the expected path; asset copied elsewhere |
| Scan sanity | per run | one canary per class, planted in the test-only `rogue` container, is found; otherwise the matrix fails | blind detector; wrong container; empty filesystem view |
| Known violation | listed tuples | a violation matching a tuple exactly is reported with its OPL and expiry; anything else fails | an exception hiding a new holder |
| Fault injection (REQ-SEC tier) | K1–K8 | a test-only overlay mounts a canary into `tool-b`; the matrix fails, then passes once it is removed | a matrix that can never fail |
| S1 | each service | unauthenticated `PING` → `NOAUTH`; each key family a service writes per ARCH-016 can be written (twin) and every other family cannot; the pilot adds rows for its budget-consumption mechanism, including a negative `DECRBY` and an attacker-supplied script run with the verifier's credentials | allowed by accident; denied for an unrelated reason (Redis down) |

Until the pilot, the S1 rows run against the OPL-007 tuple.

## Test adequacy
For this slice, adequacy is measured by:
- `test-lint` finding exactly the loose checks already known (T-22);
- the deployment gates finding the defect that started this programme (T-10, T-26), with one
  unauthorized-copy fixture per asset class;
- mutation scoring that cannot hide untested mutants (T-41);
- the derivation appendix and the independent review under the D17 acceptance bar.

Check removal, the ratchet and the escape corpus arrive with slice 2.

Known limits, stated so they are not taken for coverage:
- A deliberately malicious harness or test change is outside the threat model (D18, OPL-009).
- The detectors recognise the asset classes K1–K8; a secret in a format no detector knows still
  depends on a register entry.
- Services that do not run by default are checked through their mount sources only ("static only"
  rows).

## Assumptions and fixtures
- Default E2E mode uses deterministic mocks; live Jira stays env-gated (`M5-T55`).
- The fault injections attach or detach a container from a network (`docker network connect`/`disconnect`), stop a service, or mount a test-only overlay, and restore it in a trap. They run only in the `tests` profile.
- The time-dependent checks (non-root expiry, exception expiry) take an injectable clock.
- The `07520d7` replay uses `git show` of the compose file; it does not check out old code.
- Canary keys and tokens are generated per run, trusted by no verifier, and deleted at the end.

## Planned verification commands
- `make tooling-test`, `make test-lint`, `make qa-deploy`
- `make qa-quality` (`qa-trace`, traceability, unit guard, `docs-check`)
- `make unit-trust` and `make unit-mutation` (new scoring)
- Full E2E on a clean stack and `make qa-evidence`

## Review notes
- Rows marked *probe* are pinned against the stack as it was before the change and shown in the
  1A PR with the probe output; if a probe contradicts a *plan* row, the test author escalates
  instead of adjusting the row.
- New twin tests (for M2.5-T1, M3.S2-T3, M3.S2-T5, and an M1 positive attestation if none exists)
  get `docs/test_spec.md` entries in the same change.

## Derivation appendix
The D17 columns for this slice's rows. "Catches" is the row's text above. Evasion codes: **rn**
rename, **del** delete, **mis** missing, **emp** empty, **src** wrong source, **cmt** wrong commit,
**tm** wrong time. Every "n/a" carries its reason. Rows for slices 2 and 3 moved to
[`later_slices.md`](later_slices.md).

### Tooling tests
| Test | Evasions considered → covered by | Missing vs zero | Wrong-reason pass | Wrong-reason fail | Boundary |
| --- | --- | --- | --- | --- | --- |
| T-1 | rn or del of `expect:` keys → unknown and missing keys rejected; emp signature → rejected | a negative test without a block fails, never defaults | a typo'd key: unknown keys rejected | n/a — static parse, no runtime failure mode | n/a — no numeric limit |
| T-2 | src (row edited only in `tests.yaml`) → both sides compared; del of a row → T-40's sets (slice 2) and the 1A set check | a missing row is a mismatch | whitespace or case: one normalisation, listed in the test | n/a — static comparison | n/a — no numeric limit |
| T-3 | src (observed file from another test) → test ID inside the file checked | missing `observed_signature.json` fails | same status, other reason → fixture | malformed JSON reported as malformed, not as mismatch | n/a — exact equality |
| T-4 | emp evidence, evidence of another test → fixtures per kind | an empty evidence directory fails the guard | one wrong-failure fixture per kind | the true evidence must still pass (positive control) | n/a — no numeric limit |
| T-5 | rn of kind without a plan change, del of fault evidence → fixtures | missing fault evidence fails | a fault run without a flip → T-25 | n/a — static derivation | n/a — no numeric limit |
| T-6 | src (twin from another run) → run ID compared | twin absent from the run fails | twin passed on another route → route compared | n/a — reads recorded results | n/a — no numeric limit |
| T-7 | one fixture per pattern; a pattern split over lines; a pattern inside a helper → helper bodies linted | n/a — lint reads text, nothing to be missing | `|| true` in plumbing must pass (positive control) | n/a — static lint | n/a — no numeric limit |
| T-21 | rn of a kind; a kind without fixtures → fixtures | a missing registry fails | n/a — schema check | n/a — static | n/a — no numeric limit |
| T-22 | baseline harness from another commit → content hash pinned | a missing or an extra finding fails | n/a — set comparison | n/a — static | exact set equality |
| T-23 | emp stream, wrong file, blind detector → fixtures | a missing stream fails | canary found in another stream → stream path compared | n/a — reads recorded streams | n/a — no numeric limit |
| T-24 | mock down, counter missing → fixtures | missing is never zero: the point of the test | n/a — counts compared exactly | n/a — reads recorded counts | 0 vs 1 |
| T-25 | no flip, no restore → fixtures | missing restore evidence fails | a flip caused by another change → only the injected fault differs between the two runs | n/a — reads recorded runs | n/a — no numeric limit |
| T-41 | relabelled `skipped` or `no_tests`, partial run → fixtures | 0 total fails | n/a — arithmetic over the stats file | a missing stats file is an error, not a score | 1 of 100 killed with 99 `no_tests` fails; 70.00% passes, 69.99% fails |
| T-42 | cmt (another commit), probe after a service change, broad existing assertion → fixtures | a missing probe artifact fails | n/a — commit-graph check | n/a — static | probe commit before the first service change passes, at or after it fails |
| T-8 | profiles → all-profile config; override files → the same merged config the stack uses | a service missing from the inventory fails against the compose service list | n/a — fact extraction | a `docker compose config` failure is an error, not an empty inventory | n/a — no numeric limit |
| T-9 | rn of a mount target → compared by source and target; mode change → fixture | a service without a register entry fails | n/a — default deny | n/a — static | n/a — no numeric limit |
| T-10 | cmt → `git show` of a named commit, hash checked | a removed tuple must make it fail (asserted) | n/a — static replay | a `git show` failure is an error, not a pass | n/a — no numeric limit |
| T-11 | src of the user (compose, image, process) → all three; tm → injected clock | unknown user counts as root | n/a — UID compared | a `docker` error is "unknown", reported | 2027-01-31 23:59:58 and 23:59:59 warn, +1 s fails |
| T-12 | widened holder or operation without a requirement change → fixture | REQ without entry and entry without REQ both fail | n/a — set comparison | n/a — static | n/a — no numeric limit |
| T-13 | widened, renewed or closed-OPL tuple → fixtures; tm → injected clock | a missing expiry fails | n/a — exact tuple match | n/a — static | 2026-12-31 23:59:58 and 23:59:59 valid, 2027-01-01 00:00:00 fails |
| T-26 | rn of a key file, a "public" label → content detection; one unauthorized copy per class | a canary that is not found fails the run | a public key alone must not be reported (positive control) | n/a — detectors read content | 32- and 64-byte keys detected; 31 and 33 bytes are not keys |
| T-27 | a row deleted by hand → fixture | a missing service fails | n/a — generation check | n/a — static | n/a — no numeric limit |

### 1A E2E rows
| Test | Evasions considered → covered by | Missing vs zero | Wrong-reason pass | Wrong-reason fail | Boundary |
| --- | --- | --- | --- | --- | --- |
| M1-T1–T3 | src (log line from another attempt) → line matched with the attempt's node ID | no log line fails, never passes | another attestation error → exact line | SPIRE server down → its own signature, not this one | n/a — no numeric limit |
| M2.5-T1 | src (wrong IP) → pinned IP from inventory | n/a — curl always exits with a code | refused or DNS failure → only exit 28 accepted | tool-b down also times out → twin from `toolb_app_net` must return 200 | timeout value pinned; exit 28 only |
| M3.S2-T3, T5 | src (resolver of another network) → run from the edge container | a resolver that is down → its own error, not NXDOMAIN | resolves but refused → both clauses required | OPA or issuer down → twin from `capiss_app_net` must answer | n/a — no numeric limit |
| M3.S2-T4 | status 403 with the same reason → exact 503 | n/a — HTTP always returns a status | other 503 reason → reason exact | OPA genuinely up → test stops OPA first (premise evidence) | n/a — no numeric limit |
| M3.S4-T1, T3 | src (Envoy 401 vs tool-b 401) → `by` checked from the response body | n/a — HTTP always returns a status | 401 `invalid_token` → reason exact | tool-b down → twin M3.S4-T2 | n/a — no numeric limit |
| M3.S4-T4 | src (token from another subject) → premise records the minted subject | n/a — HTTP always returns a status | `invalid_token` instead of `sub_mismatch` → reason exact | expired token → premise checks expiry | n/a — no numeric limit |
| M3.S4-T5 | tm (token not yet expired) → premise checks `exp` < now | n/a — HTTP always returns a status | `invalid_token` → reason exact | clock skew → premise records both clocks | expiry one second past `exp` |
| M3.S4-T2 | src (body from cache or another route) → body content checked | an empty body fails | 200 from Envoy without tool-b → body content | n/a — positive test, no wrong-reason failure to separate | n/a — no numeric limit |
| M4-T5 | src (another root token's budget) → root ID recorded | budget key missing → T-24 rule | 403 `policy` on call 11 → reason exact | rate limit hit first → calls spaced, rate key recorded | calls 10 (200) and 11 (403) |
| M4-T6 | tampering that leaves the signature valid → tamper bytes in the signed block | n/a — HTTP always returns a status | `sub_mismatch` → reason exact | n/a — any other outcome is a wrong reason, which the exact reason catches | n/a — no numeric limit |
| M5-T21 | src (OPA denial) → reason `res` proves canonicalisation denied before OPA | n/a — HTTP always returns a status | 403 `policy` → status and reason exact | n/a — exact status and reason separate every other cause | n/a — no numeric limit |

### Matrix templates
| Template | Evasions considered → covered by | Missing vs zero | Wrong-reason pass | Wrong-reason fail | Boundary |
| --- | --- | --- | --- | --- | --- |
| Holder positive | rn → content detector; src (wrong container) → container ID and image digest | an absent asset fails | a public key mistaken for a private key → derivation check | `docker exec` error → error, not pass | n/a — no numeric limit |
| Non-holder negative | rn, copy elsewhere → full readable filesystem; stopped container → `docker export` | n/a — "found nothing" is the assertion, guarded by scan sanity | n/a — guarded by scan sanity | `docker` error → error, not pass | hash scan up to 1 MiB; SQLite and socket detectors unlimited |
| Scan sanity | canary in the wrong container → canary location recorded | a canary not found fails | n/a — positive control | n/a — positive control | one canary per class |
| Known violation | widened tuple → exact match | n/a — matches recorded tuples | n/a — exact match | n/a — static | expiry as T-13 |
| Fault injection | overlay left in place → second run must pass | n/a — compares two runs | n/a — compares two runs | overlay failed to mount → premise evidence | n/a — no numeric limit |
| S1 | src (another service's credentials) → per-service credentials recorded | Redis down → `PING` premise fails first | denied for another reason → error text compared | Redis down → premise | n/a — no numeric limit |
