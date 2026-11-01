# AGENTS.md — Repository Rulebook

This file is the single rulebook for this repository, for human contributors and coding agents.
Where it conflicts with a global or personal convention (for example `~/.claude/CLAUDE.md`), **this
file wins inside this repo**. Unit-test specifics are in [`tests/unit/AGENTS.md`](tests/unit/AGENTS.md),
which is part of this rulebook.

Every rule here is meant to be true of the repo today. If you find one that is not, fix the rule or
the repo in the same change — do not leave them disagreeing.

## Start here

| Question | Read | Kind |
| --- | --- | --- |
| What is this project, how do I run it? | [`README.md`](README.md) | overview |
| Where does the project stand right now? | [`docs/STATUS.md`](docs/STATUS.md) | current state |
| What must the system do? | [`docs/requirements.md`](docs/requirements.md) | authoritative |
| How is it built, which runtime state exists? | [`docs/architecture.md`](docs/architecture.md) | authoritative |
| What is the trust model, on one page? | [`docs/architecture.md` — Security model summary](docs/architecture.md#security-model-summary) | summary of the ARCH sections |
| Which test proves which requirement? | [`trace/tests.yaml`](trace/tests.yaml) | authoritative |
| What does each E2E or static test do, in plain English? | [`docs/test_spec.md`](docs/test_spec.md) | hand-written spec |
| Unit-test requirement matrix (M4 trust gates) | [`docs/unit_test_spec.md`](docs/unit_test_spec.md) | authoritative, read by `make traceability-check` |
| Known unfixed runtime/trust problems | [`docs/open_problem_log.md`](docs/open_problem_log.md) | authoritative |
| Which delivery mistakes were made, and what changed because of them? | [`docs/delivery_problem_log.md`](docs/delivery_problem_log.md) | authoritative |
| Who may hold which key, socket or secret; what each service may be | [`security/invariants.yaml`](security/invariants.yaml) with the `REQ-SEC` requirements | authoritative, checked by `make qa-deploy` |
| What is planned or waiting (proposed slices, actions only the user can take)? | [GitHub issues](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues), labels `slice` and `user-action` | tracking; a slice's decisions move into its `plan.md`, because reviewers read the repository, not issues |
| How was a past slice designed? | [`docs/slices/`](docs/slices/README.md) | frozen records |
| What happened, when? | [`docs/history/`](docs/history/) | history |
| Retired documents | `docs/archive/`, `docs/slices/archive/` | archive, do not follow |

## PoC scope and proportion

This repo is a proof of concept. Its goal is in [`README.md`](README.md): show that workload identity
is not permission, with tests that prove each boundary. It is not production hardening. The rules
below apply to every agent that plans, implements or reviews here, and hold until the user changes
them.

- **Delivery threat model.** Agents make honest mistakes: loose or wrong tests, weakened checks,
  skipped steps, stale evidence, wrong configuration. They do not deliberately attack CI, the
  gates, the evidence or the repo; that residual is accepted
  ([OPL-009](docs/open_problem_log.md)). This is about *how we deliver*. The *system under test*
  still defends against rogue workloads; that is what the PoC demonstrates.
- **Accepted PoC simplifications.** Keys and credentials live in files and environment variables
  on one Docker host. A design where each secret is visible only to the services that hold it is
  enough. KMS, HSM, Vault, per-key ownership proofs, CI-runner isolation and supply-chain controls
  are out of scope unless the user asks.
- **Ask before growing.** If a change makes the process bigger or more complex (a new gate, job,
  document, register, exception class or review step), say so and ask the user first. Prefer the
  smallest check that catches an honest mistake.
- **Few exceptions.** Fix rather than except. Do not open an OPL, exception entry or plan note for a
  finding outside the threat model; one line in the review report is enough. Every exception must
  fit on one line and have an expiry.
- **Review findings.** Give reviewers this section as context. Only these block:
  - a concrete false green or an OPL-005-class miss inside the threat model, with a failure scenario;
  - a contradiction;
  - an approved decision without a test.

  Everything else is advisory. It is listed once and is not fixed by default. Implementation details
  become notes for the implementation PR. Reviewers should expect production-hardening ideas (see
  the simplifications above) and report them as advisory at most.
- **Review loop.** There is no round limit: review rounds continue until no blocking finding is
  open. The author (the fixer) answers every finding in writing, either fixed (where) or rejected
  (why). A rejection needs a reason the reviewer can check, for example: the failure scenario does
  not happen (with the evidence), it is outside the threat model, it is already covered by a named
  test or gate, or it does not meet the blocking criteria above. A finding labelled blocking that
  does not meet them is not fixed by default. The next round sees each rejection and either accepts
  it or re-raises it with new evidence; a finding still disputed after that goes to the user, who
  decides. The review ends when every blocking finding is fixed, accepted as rejected, or decided by
  the user.

## Operating model (black-box first)
- Treat the system as a black box first:
  - authored intent in `docs/requirements.md`
  - authored runtime/system model in `docs/architecture.md`
  - runtime-visible proof in `trace/tests.yaml` plus E2E evidence artifacts
- `DD-*`, `UT-*`, source helpers, and local test doubles are engineering controls, not the primary
  proof of system behavior.
- If a security-relevant behavior depends on hidden state, author it before implementation in the
  slice `plan.md` and, when runtime behavior changes, in the state inventory of `docs/architecture.md`.
- Do not introduce or keep runtime-significant behavior that exists only in code.

## Traceability model and IDs

Every requirement is traced the same way: requirement → test ID in `trace/tests.yaml` → entry in
[`docs/test_spec.md`](docs/test_spec.md) → implementation → stored, checked result. A test is an E2E
test (the harness runs it; its evidence is checked by `make qa-evidence`) or a static test (a gate
proves it on every run; see below).

Allowed links only: `REQ → ARCH` (architecture `Satisfies:`), `ARCH → DD` (DD `Implements:`) or
`ARCH → files` (architecture `Implemented by:`), `DD → UT` (UT `Covers DD:`), `REQ → E2E` and
`REQ → static test` (`trace/tests.yaml` `source_requirements`), and `ARCH → IT` (`trace/tests.yaml`
`source_architecture`; no integration cases exist yet).

| ID | Where it lives | Format (as enforced by `scripts/validate_traceability.py`) |
| --- | --- | --- |
| `REQ` | `docs/requirements.md` headings | `## REQ-<scope>-<code><n> — <title>`, e.g. `REQ-M1-R1`, `REQ-M4A-J3`, `REQ-M5-FT7`, `REQ-G-R2` |
| `ARCH` | `docs/architecture.md` headings | `## ARCH-NNN <title>` followed by `Satisfies: REQ-…` |
| `DD` | comment block above the implementing function in `services/**` or `scripts/**` | `# DD: DD-NNN` / `# Implements: ARCH-NNN` / `# Title: …` |
| `UT` | comment block above the test in `tests/unit/**` | `# UT: UT-NNN` / `# Test Description:` / `# Precondition:` / `# Expected Output:` / `# Covers DD:` |
| E2E test | `scripts/rogue_node_tests.sh` | harness IDs such as `M1-T1`, `M3.S4-T2`, `M5-T49`; mapped in `trace/tests.yaml` as `e2e_suite` / `e2e_case` entries |
| Static test | `trace/tests.yaml` (`type: static_test`) and a `docs/test_spec.md` heading | `<NAME>-<CODE>`, e.g. `DEPLOY-K1`, `EVID-T1`; names `source_requirements`, `gate: make <target>`, `negative_controls` (`<file>::<test>` tooling tests that show the gate fails on each kind of violation) and `result` (the stored report) |

- An ARCH section implemented by files that carry no DD-tagged functions (configuration such as
  Envoy or SPIRE files, the deployment register, a test or demo script) names them on an
  `Implemented by:` line; `make qa-trace` checks they exist. QA gate code carries no DD tags.
- IDs are never reused. Do not delete a requirement or architecture ID; mark it retired with the
  reason. Retired DD and test IDs are listed under `retired_ids` in `trace/tests.yaml`; reusing one
  fails `make qa-trace`.
- A requirement's status comes from its proofs and the deployment register, never from a run: it is
  not proved without a test, while an asset it protects has a `known_violations` row, or (the
  non-root rule, `REQ-SEC-D2`) within its grace date. A requirement that is not proved is a
  `requirements_without_proof` gap.
- `make qa-trace` fails on structural errors (unknown IDs, wrong link direction, missing fields,
  duplicates, missing files). On a PR it also fails on a coverage gap the PR adds compared with its
  merge-base (the gap gate); a gap added on purpose needs a one-line `accepted_gaps` entry in
  `trace/tests.yaml` with a reason and an expiry. Older gaps are reported, not failed.

## Slice workflow

Every change follows this workflow, scaled to its size: a small fix still gets a plan (it may be a
few lines), tests first, an independent review and the close-out, but not every section of the
template needs more than "none". A slice bundle lives in `docs/slices/<slice-id>/`, starts from
`docs/slices/_template/`, and gets a row in the [slice index](docs/slices/README.md).

1. **Plan and review.** Run the `grill-me` skill and resolve design choices one branch at a time.
   Grill-me always asks which keys, sockets and secrets the slice touches and who may hold them,
   against the holders in `security/invariants.yaml`.
   Write `plan.md` (decisions, requirements to add or change, hidden-state decisions, assets and
   holders, environment facts, rulebook changes, scope, out-of-scope, retirement) and
   `test_plan.md` (UT and E2E derived from the decisions). A decision that depends on a fact outside
   the repository (file ownership, an API, CI history) records the probe and its result under
   environment facts; never assume it. An [independent review](#independent-review) of both runs
   before the user sees them. The user approves the plan by merging the plan PR; implement only from
   the plan as merged on `origin/main`.
2. **Tests first.** Add UT/E2E only from the reviewed `test_plan.md`. Update requirements,
   architecture, and `trace/tests.yaml` before making runtime code pass. If a test needs a new
   assumption, return to step 1.
   - Each expected outcome comes from the approved plan, from a probe of the stack *before* the
     change (`probe@<commit>`), or from an existing assertion (`existing@<commit>`); never from
     watching the new implementation run. If a probe contradicts a value the plan approved, stop
     and ask the user; do not adjust the row.
   - Every negative E2E test names a positive twin: the allowed case on the same route, which must
     pass in the same run (another test ID, or `internal` when a premise of the same test performs
     it).
   - A requirement may be proved statically, by a gate whose tooling tests show it fails on each
     kind of violation (as `make qa-deploy` proves the `REQ-SEC` requirements), where a runtime
     test would add nothing; the plan says which. It gets a static test entry in `trace/tests.yaml`
     and a heading in `docs/test_spec.md`.
3. **Implement.** Only approved behavior. Remove the dead code, stale paths, and artifacts that
   `plan.md` lists for retirement.
4. **Verify and close.** All of the following, in the same change:
   - run `make qa-quality` (includes `qa-trace`, `docs-check`, `test-lint` and `qa-deploy`), the full E2E suite on a clean
     stack (`scripts/clean_stack.sh`, then `make e2e`), and `make qa-evidence`; the `e2e` CI check runs the same
     suite on the PR;
   - **update `docs/test_spec.md` by hand** for every E2E or static test added or changed — plain
     English, not code: what it tests, how (premise, exercise, outcome, or the gate's check), and
     the evidence or result it leaves. Each test gets a heading `### <ID> — “<name>”`; `make
     docs-check` fails on a missing or stale heading, but it cannot judge the prose, so review it;
   - add a dated entry to `docs/history/implementation_log.md` (what changed, validation results,
     what was not run and why);
   - update `docs/STATUS.md` and the slice's row in `docs/slices/README.md`;
   - add or close entries in `docs/open_problem_log.md` for problems found or fixed, and in
     `docs/delivery_problem_log.md` for delivery misses (a step skipped, a false claim, a review
     miss) found or fixed;
   - open a GitHub issue for work found but not done (label `slice` or `user-action`), and close the
     issues the change finishes (`Closes #N` in the PR body);
   - put the independent review's answers to the implementation questions in the PR body.

### Independent review
- **Reviewer.** Never the author. Use `codex exec` in a read-only sandbox; if Codex is unavailable,
  a Claude model with a clean context. The report says which reviewer ran and why. The reviewer
  gets the intent (the approved plan, or the request), the change, and this file, and may read the
  whole repository; it never gets the author's reasoning. The prompts used so far are recorded
  verbatim in the slice review records (for example
  [`review_1b.md`](docs/slices/agentic-delivery-process/review_1b.md#reviewer-prompts-verbatim)).
- **Plan review** (step 1). The reviewer reviews `plan.md` and `test_plan.md` for security, test
  adequacy and consistency, under [PoC scope and proportion](#poc-scope-and-proportion).
  `docs/slices/<id>/plan_review.md` keeps each round's report verbatim, the SHA-256 of the files
  reviewed, and the author's answers (fixed or rejected, with the reason) separately. Each round ends
  with "approvable within the threat model: yes or no"; from round 2 a new finding counts only if it
  blocks, except simpler alternatives and decision concerns (below), which every round may report.
  The plan states the threat model the reviewer judges against: the
  [delivery threat model](#poc-scope-and-proportion) applied to the slice's own change, and the
  system-under-test threat the slice touches.
- **Implementation review** (step 4). The reviewer answers the questions in the test-plan template
  (`docs/slices/_template/test_plan.md`: which wrong failure would still pass each new or changed
  test, and whether a key, socket or secret now reaches a service outside its holders) in the PR
  body. A "yes" blocks, under the same review loop.
- **Fixes stay within the agreed decisions** (the plan's decisions, or the request, and this file).
  Before answering a finding with a new mechanism, the author names the upstream choice that causes
  it and weighs changing that choice; removing or changing a mechanism is preferred over adding one.
  A fix that would change an agreed decision goes to the user as a question before it is applied.
- **Report sections.** Besides blocking and advisory findings, every round may report *simpler
  alternatives* (a mechanism that could be removed or simplified within the agreed decisions;
  non-blocking) and *decision concerns* (an agreed decision that itself seems to cause a problem;
  for the user, never applied by the author). The reviewer may check metadata of secret files
  (existence, owner, mode, readability), never their content.

Hidden-state rule: if a decision depends on hidden state, `plan.md` lists the state/key name, store,
writer, reader, TTL or lifecycle, decision impact, and whether it is authoritative or advisory.
Mandatory for security-relevant Redis, file, cache, policy, or derived state.

Retirement rule: every `plan.md` states what old logic is removed, what compatibility behavior is kept
temporarily (if any), and which docs/tests/artifacts are deleted or archived. If nothing is retired,
say so.

## Quality gates

Every CI gate is a job named after its make target in `.github/workflows/ci.yml` (workflow `CI`).
A gate's result is its CI job's conclusion on GitHub; a local or offline rerun is a diagnosis and
never replaces it.

| Gate | Command | Enforced by | Threshold |
| --- | --- | --- | --- |
| Trace model | `make qa-trace` | CI, every push/PR | zero structural failures; on a PR (`--mode pr --base <base>`), no coverage gap the PR adds compared with its merge-base unless `accepted_gaps` in `trace/tests.yaml` lists it with a reason and an unexpired date (an expired or stale entry fails); a merge-base that cannot be resolved or read fails. On `main` (`--mode push`) gaps are reported |
| Documentation | `make docs-check` | CI | every harness test and every static test in `trace/tests.yaml` has a `docs/test_spec.md` heading and vice versa; relative links and `#anchors` in live docs resolve; every tracked image in `docs/` is referenced and every `.puml` has its `.svg`; every slice bundle is in the slice index; `TEST_ONLY=` examples name real tests |
| QA tooling tests | `make tooling-test` | CI | `tests/tools/` (pytest) and `tests/shell/` pass |
| E2E outcome lint | `make test-lint` | CI | no outcome guard in `scripts/rogue_node_tests.sh` accepts several outcomes (`assert_file_any`, broad error regexes, `!= 200`), swallows failure (`\|\| true`), checks only a non-zero exit, or is a test of negative greps only; a multi-outcome guard needs `# test-lint: alternate: <reason>` |
| Deployment register | `make qa-deploy` | CI (without image inspection; the `e2e` job runs it with image users inspected) | every service's image, user, networks, ports, mounts, secret env names and privileges match `security/invariants.yaml`; every protected asset reaches only its holders, except unexpired known violations of open OPLs; register holders equal the `REQ-SEC` `Holders:` lines; non-root except the grandfathered baseline until 2027-01-31 |
| Unit guard integrity | `make unit-guard-check` | CI | every unit test has premise, exercise, outcome guards |
| Unit trust bundle | `make unit-trust` | CI | total line coverage ≥ 85%; branch coverage ≥ 75% on `services/capability-issuer/app.py` and `services/tool-b/server.py`; unit traceability check; invariant, negative-control, hybrid-critical suites; invariant flake check ×5 |
| Diff coverage | `make unit-diff-cov` | CI, PRs only (own job) | ≥ 90% of changed lines in `services/capability-issuer/` and `services/tool-b/` |
| Mutation | `make unit-mutation` | CI | score ≥ 70% (capiss and tool-b), counting untested and skipped mutants as not killed; an empty run fails |
| Gate consistency | `make gate-consistency` | CI | every row this table marks as enforced by CI has a CI job of the same name that runs `make <name>`; every CI job has such a row; every CI job is a required check of the `main` ruleset and every required check is a job; the ruleset requires at least one approving review (the ruleset is read from the public GitHub API; a failed read fails) |
| Full E2E suite | `make e2e` | CI, every push/PR; and local on a clean stack, required in step 4 | all pass; warnings reviewed. The CI job then runs `make qa-deploy` with image users inspected and `make qa-evidence`, and uploads the publication set for 14 days only if the secret check found nothing |
| E2E evidence | `make qa-evidence` | in the CI `e2e` job; local, after the E2E run | every test has premise/exercise/outcome evidence and a PASS line; no file of the publication set (`PUBLICATION_SET` in the `Makefile`: `test_report.log`, `artifacts/rogue-tests/`, `artifacts/quality/`) holds a secret by shape: a PEM private key, a base64 PKCS#8 private key, base64 of a PEM private key, a base64 or base64url run of ≥ 200 characters with ≥ 20 distinct ones outside certificates, a `JIRA_API_TOKEN=` or `Authorization:` line with a value, or an Atlassian API token; an unreadable file fails; a finding names the file and kind, never the value |

Standards that are **not** gated yet (follow them for new and changed code):
- `ruff check services scripts` stays clean.
- Cyclomatic complexity ≤ 10 per new or changed function (`radon cc`). Existing functions above the
  limit are tracked as debt in `docs/STATUS.md`; do not make them worse.
- `mypy` and `bandit` are not configured in this repo.

## Coding rules
1. No secrets in source, config, logs, or evidence. Credentials come from the environment at runtime.
2. No Python `eval()`, `exec()`, or `__import__()` on dynamic input. (Redis `EVAL` of fixed Lua scripts is fine.)
3. Validate and reject external input at service boundaries; internal functions trust their callers.
4. Fail closed: any unexpected error in a security decision path denies.
5. No broad `except Exception` in enforcement or validation paths; catch specific exceptions.
6. Audit events never contain token values, passwords, or key material; E2E tests assert this.
7. Secrets this repository creates are stored in a standard, recognisable format (private keys as
   PKCS#8 PEM), so the evidence secret check finds them by shape. Secrets created by others (SPIRE
   key stores, join tokens, Jira tokens) keep their format.

## Documentation rules
- One home per fact. Before adding a document, check the [Start here](#start-here) table; extend the
  owning document instead of creating a parallel one.
- `docs/test_spec.md` is hand-written and must describe every E2E test the harness runs.
- Implemented slice bundles are frozen records; do not rewrite them to match later reality.
- Tests for QA tooling (`scripts/check_docs.py` and similar) live in `tests/tools/`; shell-level tests
  live in `tests/shell/`. The unit-test rules in `tests/unit/AGENTS.md` apply only to `tests/unit/`.
- Retire documents with `git mv` into `docs/archive/` (or `docs/slices/archive/`); never delete them.
- Architecture diagrams use a C4-style, grid-aligned layout: group by trust boundary or network zone,
  flows left-to-right or top-to-bottom, orthogonal connectors with few crossings, planned components
  labeled as such.

## Git rules
- No `Co-Authored-By` trailers for AI assistants in commit messages.
- Agents act on GitHub as the machine user `gunaseelan-agent`; only the owner
  (`gunaseelan-sivanandam`) approves and merges into `main`. The `main` ruleset requires one
  approving review, which GitHub never lets a pull request's author give, so an agent cannot merge
  its own; `make gate-consistency` fails if that requirement is removed.
- An agent session gets the bot identity from the `env` block of the gitignored
  `.claude/settings.local.json` (`GH_CONFIG_DIR` for the bot's `gh` login, `GIT_AUTHOR_*` and
  `GIT_COMMITTER_*` for commits); `origin` is the HTTPS URL, so `git push` uses the bot's token
  through `gh` as git's credential helper. Before a GitHub write, check that `gh api user --jq
  .login` prints `gunaseelan-agent`; if not, stop and tell the user.
- Open pull requests against `main`; avoid stacking. A stacked PR is merged only after its base
  shows `main` (GitHub retargets it when the base branch is deleted) ([DPL-008](docs/delivery_problem_log.md#dpl-008-a-stacked-pr-was-merged-into-its-stale-base-branch-instead-of-main)).

## Environment
- Docker Engine + Docker Compose v2. Linux, or macOS with Rancher Desktop.
- Run every command from the repo root.

## Quick start
1. Preflight:
   ```bash
   docker info >/dev/null
   docker compose version
   docker context ls
   scripts/clean_stack.sh --check
   ```
2. Clean state when needed: `scripts/clean_stack.sh` (run it again if the first pass reports a
   permission warning on a root-owned file).
3. Bring the core stack up:
   ```bash
   docker compose -f compose/spiffe.compose.yml up -d --build
   ```
4. Inspect SPIRE agent logs for workload SVID activity:
   ```bash
   docker compose -f compose/spiffe.compose.yml logs -f --tail=200 spire-agent
   ```
5. Tear down:
   ```bash
   docker compose --profile tests -f compose/spiffe.compose.yml down --remove-orphans
   docker compose -f compose/spiffe.compose.yml down --remove-orphans
   ```

## Test commands
- Full suite (writes `test_report.log` and evidence under `artifacts/rogue-tests/`, builds every image, and gives
  the root-owned output back to you so `make qa-evidence` can run):
  ```bash
  scripts/clean_stack.sh
  make e2e
  ```
- Specific test IDs:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build \
    -e TEST_ONLY=M3.S3-T3,M3.S4-T2 rogue-tests
  ```
- Selected milestones:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build \
    -e TEST_MILESTONES=m1,m2,m25,m3 rogue-tests
  ```
- Keep `--build`: `scripts/rogue_node_tests.sh` is copied into the `rogue-tests` image, so without it
  a run silently uses the harness from the last build. (The `varambu` wrapper is bind-mounted and needs
  no rebuild.)
- A targeted run overwrites `test_report.log`, so `make qa-evidence` needs a full run to pass.
- Live Jira tests (`M5-T55`, `make jira-live-smoke`) need explicit live configuration; default runs
  use deterministic mocks.

Profiling is on by default (`TEST_PROFILE=1`); timings go to `artifacts/rogue-tests/guard_timings.tsv`
and `guard_timings_top25.txt`. Disable with `-e TEST_PROFILE=0`.

## Evidence checks (false-green guard)
After a full run, `make qa-evidence` validates the evidence. Evidence holds no token values: guards work in a
scratch directory, and the harness publishes it with every token-shaped value replaced by its SHA-256 fingerprint.
To inspect by hand:
```bash
find artifacts/rogue-tests -maxdepth 1 -mindepth 1 -type d | sort
grep -Eq 'Failed: [1-9]' test_report.log && find artifacts/rogue-tests -name fail_reason.txt -print -exec cat {} \;
find artifacts/rogue-tests -name 'warning_reason_*.txt' -print -exec cat {} \;
find artifacts/rogue-tests -name skip_reason.txt -print -exec cat {} \;
```
- `fail_reason.txt`: terminal guard failure for that test.
- `warning_reason_*.txt`: the test passed through an accepted alternate path; review the condition.
- `skip_reason.txt`: an env-gated test did not run its exercise (for example `M5-T55` without live
  Jira). `make qa-evidence` counts it as skipped, never as validated, and only if the suite declares
  the gate for that test in `trace/tests.yaml` (`env_gates`), the gate check left premise evidence,
  and no exercise or outcome artifacts exist. The test still prints `PASS` in `test_report.log`.

## Docker guardrails
- Never run Docker lifecycle commands in parallel. Serialize `scripts/clean_stack.sh` and
  `docker compose … up/down/run`; run `ps`/`logs` only after the mutating command finishes.
- `capability-issuer-no-opa-envoy` is test-only (`tests` profile); never use it outside tests.
- Prefer `scripts/clean_stack.sh` over manual cleanup.
- Keep evidence under `artifacts/rogue-tests/` unless you deliberately set `ROGUE_TEST_EVIDENCE_DIR`.
- macOS / Rancher Desktop: point the Docker CLI at the `rancher-desktop` context
  (`docker context use rancher-desktop`). On socket/context mismatches or permission-constrained
  bind mounts under `tmp_svid/` or `artifacts/`, confirm `docker info` works and rerun
  `scripts/clean_stack.sh`.
