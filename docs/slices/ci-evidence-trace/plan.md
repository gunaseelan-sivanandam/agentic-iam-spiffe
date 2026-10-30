# Slice Plan — ci-evidence-trace (agentic-delivery-process, slice 2 of 3)

Status: **draft for plan review** (2026-10-30). Grill-me: 2026-10-30. Builds on slice 1's standing rules in `AGENTS.md`
(PR #7, merged) and the review loop without a round limit (PR #8).

## Goal
**Programme.** Agents take an approved plan to a pull request, and the user is involved only in
grill-me, merges and escalations. That works only if a green run can be trusted.

**This slice.** Three things a green run could not be trusted on after slice 1:
1. **Where the E2E proof comes from.** The full suite runs only on the author's machine. CI never
   runs it, so a PR can merge with E2E evidence nobody else produced. A CI trial on 2026-10-30
   (run `41000278717`) ran the full suite twice on GitHub-hosted runners: about 3.5 minutes per
   job, 120/120 passed, `qa-evidence` passed (119 validated, 1 skipped).
2. **What the evidence contains.** Since `7226c2e` (2026-01-20) the harness writes capability token
   values into evidence (`token.txt`, `create_token.txt`, `read_token.txt`, the `token` field of
   saved mint JSON). That breaks `AGENTS.md` coding rule 1 and the evidence clauses of
   `REQ-M4B-W8` and `REQ-M5-CJ2`, whose E2E tests pass anyway (a false green). Uploading evidence
   from CI on a public repository would publish it.
3. **What the trace says is proved.** Only an E2E entry counts as proof of a requirement, so the ten
   `REQ-SEC` requirements that `make qa-deploy` checks on every PR show as unproved. The workaround
   (DD tags on a QA script, `IT-DEPLOY-*` on ARCH-034) hides that three of them are violated today.
   Coverage gaps never fail, so slice 1B added ten unproved requirements unnoticed (87 → 97). And
   nothing keeps the `AGENTS.md` gate table, the CI jobs and the required checks in agreement; the
   1B review missed gates hidden in another job, and `unit-diff-cov` has no job of its own today.

## Threat model for this plan and its reviews
This section is what the plan reviewer and the implementation reviewer judge against. It applies
[`AGENTS.md` — PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion) to this
slice.

**Delivery threat: honest mistakes (in model).** An agent or a person changing this repository makes
mistakes in good faith. This slice's checks must catch these:

| # | Honest mistake | Caught by |
| --- | --- | --- |
| M1 | A requirement, ARCH section or DD is added without its proof | gap gate (D7) |
| M2 | A gap is accepted and forgotten, or its acceptance outlives its reason | `accepted_gaps` expiry and stale-entry check (D7) |
| M3 | A requirement is reported as proved while it is violated under an accepted known violation | per-requirement static status (D5) |
| M4 | A stale `qa-deploy` report (from another compose or register) is read as evidence | input digests in the report, checked by `qa-evidence` (D5) |
| M5 | A gate is added to the Makefile or `AGENTS.md` without a CI job or required check, or a job of a gate's name runs another command | gate consistency, including each job's command (D8) |
| M6 | A secret (capability token, a registered key or credential) is written into evidence and uploaded | harness fix and evidence secret check: token and private-key shapes, and the exact values of the register's restricted assets (D3) |
| M7 | E2E is not run, or run on the author's machine only, before merge | `e2e` required check (D1) |
| M8 | CI and the local run use different OPA or Redis images because their compose tag floats | pinned tags (D2). Not covered: Dockerfile base images (`python:3.11-slim`, `alpine:3.19`) still float within their minor version; see Known limits |
| M9 | An ARCH section claims an implementing file that does not exist | `Implemented by:` check (D6) |
| M10 | A CI job fails in a tooling step and is reported as passed | the job's own conclusion is the result; no step swallows a failure |

**Delivery threat: deliberate attack (out of model).** A PR written to defeat the gates — editing the
workflow or a gate to report green, forging evidence or reports, attacking the runner — is outside
the model and accepted as [OPL-009](../../open_problem_log.md). A reviewer may mention such a path as
advisory; it does not block. The same holds for supply-chain controls (pinning by digest,
provenance), runner isolation, GitHub API spoofing, and access control on CI artifacts beyond "they
contain no secrets".

**System under test.** This slice changes no service and no runtime authorization behaviour. It
touches:
- the harness (`scripts/rogue_node_tests.sh`) only where it writes evidence: token hand-offs move
  out of the evidence directory; every test's premise, exercise and outcome stay the same;
- the register (`security/invariants.yaml`) only to pin two image tags;
- `qa-deploy`'s output (a per-requirement report); its checks and verdict do not change.

The `rogue-tests` container holds the Docker socket on the CI runner, as it does locally (it is a
declared holder in the register). On a GitHub-hosted runner that is root on a throwaway VM whose job
has no secrets; this is accepted.

**Blocking criteria** (from `AGENTS.md`, made concrete for this slice). A finding blocks only if it
shows, with a failure scenario:
- a false green inside the model: one of M1–M10 still passes a check this plan says catches it;
- a contradiction with `AGENTS.md`, a requirement, or a decision below;
- a decision below without a test in `test_plan.md`.

Everything else is advisory. The review loop is the one in `AGENTS.md`: no round limit, the author
answers each finding as fixed or rejected with a checkable reason, and a finding still disputed
after the next round goes to the user.

## Grill-Me Review Summary (2026-10-30)

| # | Question | Decision |
| --- | --- | --- |
| D1 | CI E2E | A `make e2e` target (build every image, run the full suite, take ownership of the root-owned output) and a CI job `e2e` that runs it, then `make qa-deploy` with image inspection, then `make qa-evidence`, and uploads the evidence (14 days). It runs on every PR and every push to `main` and is a required check. Step 4 of the slice workflow **also** keeps the local full run on a clean stack. |
| D2 | Floating images | Pin `openpolicyagent/opa:latest` and `redis:7-alpine` to exact version tags (compose and register). Tags, not digests. |
| D3 | Tokens in evidence | Token hand-offs between guards move to a per-test scratch directory outside `artifacts/rogue-tests/`. Evidence keeps a SHA-256 fingerprint where a test needs one (for example "two mints differ"); saved mint JSON has its `token` replaced by the fingerprint. `qa-evidence` fails on a secret in evidence, so the mistake cannot come back. It looks for two things: token and private-key shapes — a base64 or base64url run of at least 200 characters with at least 20 distinct characters outside PEM `CERTIFICATE` blocks (capiss tokens are 600 or more; other evidence stays under 100, and M5-T53's long single-character padding is not a token), a PEM private-key block, a credential line (`JIRA_API_TOKEN=`, `Authorization:` with a value) — and the exact values of the restricted assets `security/invariants.yaml` lists that are readable where it runs (for example the capiss `root_key.b64`, which is raw base64 and has no recognisable shape), in plain and base64 form. It never prints a matched value. Evidence is uploaded only after this check passes. `docs/test_spec.md` evidence lists follow. |
| D4 | Trace model | Every requirement is traced the same way: requirement → test ID in `trace/tests.yaml` → entry in the test specification → implementation → stored, checked result. |
| D5 | Static tests | A new entry type for tests that prove a requirement statically. The ten `REQ-SEC` get one static test each, `DEPLOY-K1` … `DEPLOY-K8`, `DEPLOY-D1`, `DEPLOY-D2`, each with a spec entry. `make qa-deploy` writes a report with a status per requirement: `holds`, `known_violation` (with its OPL) or `grace` (D2's non-root grace period). The gate verdict does not change. A requirement whose only proof has status `known_violation` is reported as "not proved: known violation OPL-xxx", never as proved. The report records the SHA-256 of the compose file and register it checked, and whether image users were inspected; with `--skip-image-users`, D2's status is `not_checked`. `qa-evidence` accepts only a complete report (every `REQ-SEC` present with a known status, image users inspected, digests matching the files on disk). The `e2e` job and the local step-4 run produce it; the `qa-deploy` job's report (without image inspection) is not evidence. |
| D6 | Config-implemented ARCH | An ARCH section implemented by files that carry no DD-tagged functions — configuration (Envoys, SPIRE, the deployment register) or a test or demo script (the harness, `agent-a`) — names those files on an `Implemented by:` line. `qa-trace` checks those files exist and counts the section as implemented instead of expecting a DD. ARCH-034 is reworded as the deployment-register architecture. DD-925 to DD-930 are retired (QA gates carry no DD tags, like every other gate) and `IT-DEPLOY-*` are replaced by the static tests, which name `tests/tools/test_qa_deploy.py` as the gate's negative controls. The tooling tests do not change. |
| D7 | Gap gate | On a PR, `qa-trace` computes the coverage gaps of the PR and of its merge-base with `main`, and fails on a gap the PR adds, in every gap category (requirements, ARCH, DD, unlinked tests). The mode is explicit (`--mode pr --base <ref>` or `--mode push`): in PR mode, a base that cannot be resolved or read fails, never falls back to push mode; the CI job fetches full history. An intended gap is an `accepted_gaps` entry in `trace/tests.yaml`: gap ID, reason, expiry, one line. An expired entry fails, and so does an entry whose gap no longer exists. On a push to `main` the comparison is reported, not enforced. |
| D8 | Gate consistency | A CI job `gate-consistency` (`make gate-consistency`) checks three lists agree: the gates `AGENTS.md` says CI enforces, the jobs in `.github/workflows/ci.yml`, and the required checks of the `main` ruleset (read from the public GitHub API, no token). Each such job must run `make <its own name>`. A failure to read the ruleset fails the job. `unit-diff-cov` gets its own job. |
| D9 | One process | `AGENTS.md`: every change follows the slice workflow, scaled to its size; this replaces "required for milestone and security-relevant changes". |
| D10 | Moved to slice 3 | All review design (template, lenses or roles, environment facts, agent count, synthesis) and lanes, with the user's input recorded in [`later_slices.md`](../agentic-delivery-process/later_slices.md). |
| D11 | Increments | Two PRs. **A — CI evidence** (D1, D2, D3). **B — trace model** (D4 to D9). A goes first, because CI must not upload evidence before the token fix. REQ-T-R9 and its static test `EVID-T1` land in B, which adds the static test type; the secret check they trace to lands in A. |

## Requirements
- **New: REQ-T-R9 — Evidence non-disclosure.** Test evidence shall not contain bearer or capability
  token values, private key material, or credentials. A test that needs to relate tokens records a
  fingerprint. Proved statically by `EVID-T1` (D3), the `qa-evidence` secret check over every run's
  evidence. `REQ-M4B-W8` and `REQ-M5-CJ2` keep their own evidence clauses; this generalises them to
  every test.
- **Proved differently, not changed:** `REQ-SEC-K1` to `-K8`, `-D1`, `-D2`, by `DEPLOY-*` (D5).
- No requirement is added for the delivery gates themselves (gap gate, gate consistency, CI E2E);
  they are QA tooling, tested in `tests/tools/`, like `test-lint` and `docs-check`.

## Success criteria
1. The `e2e` job runs on the implementation PRs and on `main`, is a required check, and passes:
   120 tests, `qa-deploy` with image inspection, `qa-evidence`.
2. After a full run, no file under `artifacts/rogue-tests/` contains a token value or private key,
   and `EVID-T1` fails on a fixture that does.
3. `make qa-trace` reports each `REQ-SEC` as proved statically, except K1, K2 and K4, reported as
   "not proved: known violation" with OPL-005, OPL-006 and OPL-008, and D2 as "grace".
4. `make qa-trace` fails on a PR fixture that adds a requirement without proof, passes with a valid
   `accepted_gaps` entry, and fails on an expired or stale one.
5. Each of the 13 ARCH sections without a DD is reviewed: those implemented by files without
   DD-tagged functions name them on `Implemented by:`; any left is still reported as a gap. ARCH-034
   names the register and compose; DD-925 to DD-930 and `IT-DEPLOY-*` are retired.
6. The gate-consistency job fails when any of the three lists differs, and passes on the merged
   result.

## In scope
**Increment A — CI evidence**
- `make e2e`; the `e2e` CI job (D1).
- Pinned `opa` and `redis` tags in compose and `security/invariants.yaml` (D2).
- Harness token hand-offs through a scratch directory, fingerprints, redacted mint JSON; the
  `qa-evidence` secret check, its contract stated in the `AGENTS.md` gate row of `qa-evidence`;
  `test_spec.md` evidence lists (D3).

**Increment B — trace model**
- The static test type in `trace/tests.yaml` and `qa-trace`; `DEPLOY-*`; REQ-T-R9 with `EVID-T1`
  (the Increment A secret check as its implementation); the `qa-deploy` report;
  the `qa-evidence` check of that report (D4, D5).
- `test_spec.md` covers static tests (title, a "Static tests" part, `docs-check` heading parity for
  static IDs).
- `Implemented by:` for config-implemented ARCH sections; ARCH-034 reworded; DD-925 to DD-930 and
  `IT-DEPLOY-*` retired (D6).
- The gap gate and `accepted_gaps` (D7).
- The gate-consistency job; `unit-diff-cov` as its own job (D8).
- `AGENTS.md`: one process (D9); the trace model and allowed links; the quality-gates table.
- `docs/open_problem_log.md` OPL-009 mitigations: lanes and a nightly run are no longer planned;
  every change goes through the slice workflow and the `e2e` job runs on every push to `main`.

## Out of scope
- Review design and lanes (D10), automation of reviews (slice 3).
- Fixing OPL-005 to OPL-008 (the pilot); changing any service.
- Live Jira in CI (`M5-T55` stays env-gated and skipped in CI).
- Pinning by digest; supply-chain, runner and artifact-access controls (out of model).
- The open mutation decision (`mutate_only_covered_lines`, `docs/STATUS.md`).
- The older coverage gaps already on `main` (they do not fail; D7 only stops new ones).

## Assets and holders
- **Keys, sockets, secrets touched:** capability tokens the harness handles move from the evidence
  directory to a harness-local scratch directory that is never uploaded. The evidence secret check
  reads the restricted assets the register lists, to compare, and prints no value. No holder
  changes. `rogue-tests` holds the Docker socket on
  the CI runner as it does locally (declared holder). The CI jobs have no secrets
  (`permissions: contents: read`); the ruleset is read without a token.
- **Removed exposure:** capability token values leave the evidence (D3) before CI uploads it.
- **Register change:** two image tags pinned (D2); no holder changes.

## Hidden-state and trust decisions
- **Runtime:** none added or changed.
- **Process state:**

| State | Store | Writer | Reader | Lifecycle | Authority |
| --- | --- | --- | --- | --- | --- |
| CI E2E evidence | GitHub Actions artifact of the `e2e` job (public repository) | `e2e` job | user, reviewers | 14 days | authoritative for the PR together with the local run (D1) |
| `qa-deploy` report | `artifacts/quality/` (uploaded with the evidence in CI) | `make qa-deploy` | `qa-evidence`, `qa-trace` report, reviewers | per run; bound to the compose and register digests | authoritative for `DEPLOY-*` |
| Accepted gaps | `trace/tests.yaml` `accepted_gaps` | slice PRs the user merges | `qa-trace` | until expiry | authoritative |
| Required checks | GitHub ruleset `basic` on `main` (outside the repository) | the user | gate-consistency job | until the user changes it | authoritative |
| Harness scratch | per-test directory outside `artifacts/rogue-tests/` | harness | harness only | one run; never uploaded | none (not evidence) |

## Authored source changes
- Requirements: REQ-T-R9.
- Architecture: `Implemented by:` lines on the config-implemented sections; ARCH-034 reworded;
  ARCH-007 and ARCH-019 note that CI runs the harness.
- Runtime proof: `EVID-T1`, `DEPLOY-*` (static); no E2E outcome changes.
- Rulebook (`AGENTS.md`): one process (D9); the traceability model (static tests, config-implemented
  ARCH, `accepted_gaps`); the quality-gates table (`e2e`, gate consistency, `unit-diff-cov`); step 4
  names the `e2e` check besides the local run.

## Retirement and compatibility
- DD-925 to DD-930 retired (tags removed from `scripts/qa_deploy.py`, the IDs marked retired with
  the reason); `IT-DEPLOY-*` removed from `trace/tests.yaml`, replaced by `DEPLOY-*`.
- Token files and token values in evidence are removed; tests that read a token from `$EVDIR`
  read it from the scratch directory.
- `--skip-image-users` stays for the `qa-deploy` job; the `e2e` job runs without it.
- `test_spec.md` is renamed in its title from "E2E Test Specification" to "Test Specification"; the
  file path stays.
- No documents are archived.

## Known limits
- Dockerfile base images (`python:3.11-slim` for 7 images, `alpine:3.19` for 4) float within their
  minor version, so CI and a cached local build can differ there. Pinning them is not decided.
- The secret check finds token and key shapes and the values of registered assets readable where it
  runs; a secret that is neither (an unregistered credential with no recognisable shape) is left to
  the review question on keys.
- `qa-deploy` sees compose and image facts only (as in slice 1).

## Review notes (approve or change in the plan PR)
1. **User actions:** merge PR #8 (the review loop this plan's review follows). At the implementation PRs, add
   `e2e` (A), and `unit-diff-cov` and the gate-consistency job (B) to the `main` ruleset's required
   checks. The gate-consistency job fails on PR B until they are added.
2. **The four trial artifacts** of runs `40999541906` and `41000278717` contain expired capability
   tokens; the user chose to let them expire (7 days).
3. **Cost:** every PR gains about 4 minutes of CI for `e2e`; free on the public repository.
