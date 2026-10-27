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
| What does each E2E test do, in plain English? | [`docs/test_spec.md`](docs/test_spec.md) | hand-written spec |
| Unit-test requirement matrix (M4 trust gates) | [`docs/unit_test_spec.md`](docs/unit_test_spec.md) | authoritative, read by `make traceability-check` |
| Known unfixed runtime/trust problems | [`docs/open_problem_log.md`](docs/open_problem_log.md) | authoritative |
| How was a past slice designed? | [`docs/slices/`](docs/slices/README.md) | frozen records |
| What happened, when? | [`docs/history/`](docs/history/) | history |
| Retired documents | `docs/archive/`, `docs/slices/archive/` | archive, do not follow |

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

Allowed links only: `REQ → ARCH` (architecture `Satisfies:`), `ARCH → DD` (DD `Implements:`),
`DD → UT` (UT `Covers DD:`), `REQ → E2E` (`trace/tests.yaml` `source_requirements`), and
`ARCH → IT` (`trace/tests.yaml` `source_architecture`; no integration cases exist yet).

| ID | Where it lives | Format (as enforced by `scripts/validate_traceability.py`) |
| --- | --- | --- |
| `REQ` | `docs/requirements.md` headings | `## REQ-<scope>-<code><n> — <title>`, e.g. `REQ-M1-R1`, `REQ-M4A-J3`, `REQ-M5-FT7`, `REQ-G-R2` |
| `ARCH` | `docs/architecture.md` headings | `## ARCH-NNN <title>` followed by `Satisfies: REQ-…` |
| `DD` | comment block above the implementing function in `services/**` or `scripts/**` | `# DD: DD-NNN` / `# Implements: ARCH-NNN` / `# Title: …` |
| `UT` | comment block above the test in `tests/unit/**` | `# UT: UT-NNN` / `# Test Description:` / `# Precondition:` / `# Expected Output:` / `# Covers DD:` |
| E2E test | `scripts/rogue_node_tests.sh` | harness IDs such as `M1-T1`, `M3.S4-T2`, `M5-T49`; mapped in `trace/tests.yaml` as `e2e_suite` / `e2e_case` entries |

- IDs are never reused. Do not delete a requirement or architecture ID; mark it retired with the reason.
- `make qa-trace` fails on structural errors (unknown IDs, wrong link direction, missing fields,
  duplicates, missing files). Coverage gaps are reported but do not fail the build.

## Slice workflow

Required for milestone and security-relevant changes. A slice bundle lives in
`docs/slices/<slice-id>/`, starts from `docs/slices/_template/`, and gets a row in the
[slice index](docs/slices/README.md).

1. **Plan and review.** Run the `grill-me` skill and resolve design choices one branch at a time.
   Write `plan.md` (decisions, requirements to add or change, hidden-state decisions, scope,
   out-of-scope, retirement) and `test_plan.md` (UT and E2E derived from the decisions). Do not
   implement before review.
2. **Tests first.** Add UT/E2E only from the reviewed `test_plan.md`. Update requirements,
   architecture, and `trace/tests.yaml` before making runtime code pass. If a test needs a new
   assumption, return to step 1.
3. **Implement.** Only approved behavior. Remove the dead code, stale paths, and artifacts that
   `plan.md` lists for retirement.
4. **Verify and close.** All of the following, in the same change:
   - run `make qa-quality` (includes `qa-trace` and `docs-check`), the full E2E suite on a clean
     stack, and `make qa-evidence`;
   - **update `docs/test_spec.md` by hand** for every E2E test added or changed — plain English,
     not code: what it tests, how (premise, exercise, outcome), and the evidence it leaves. Each
     test gets a heading `### <harness ID> — “<name>”`; `make docs-check` fails on a missing or
     stale heading, but it cannot judge the prose, so review it;
   - add a dated entry to `docs/history/implementation_log.md` (what changed, validation results,
     what was not run and why);
   - update `docs/STATUS.md` and the slice's row in `docs/slices/README.md`;
   - add or close entries in `docs/open_problem_log.md` for problems found or fixed.

Hidden-state rule: if a decision depends on hidden state, `plan.md` lists the state/key name, store,
writer, reader, TTL or lifecycle, decision impact, and whether it is authoritative or advisory.
Mandatory for security-relevant Redis, file, cache, policy, or derived state.

Retirement rule: every `plan.md` states what old logic is removed, what compatibility behavior is kept
temporarily (if any), and which docs/tests/artifacts are deleted or archived. If nothing is retired,
say so.

## Quality gates

| Gate | Command | Enforced by | Threshold |
| --- | --- | --- | --- |
| Trace model | `make qa-trace` | CI, every push/PR | zero structural failures |
| Documentation | `make docs-check` | CI | every harness test has a `docs/test_spec.md` heading and vice versa; relative links and `#anchors` in live docs resolve; every tracked image in `docs/` is referenced and every `.puml` has its `.svg`; every slice bundle is in the slice index; `TEST_ONLY=` examples name real tests |
| QA tooling tests | `make tooling-test` | CI | `tests/tools/` (pytest) and `tests/shell/` pass |
| Unit guard integrity | `make unit-guard-check` | CI | every unit test has premise, exercise, outcome guards |
| Unit trust bundle | `make unit-trust` | CI | total line coverage ≥ 85%; branch coverage ≥ 75% on `services/capability-issuer/app.py` and `services/tool-b/server.py`; unit traceability check; invariant, negative-control, hybrid-critical suites; invariant flake check ×5 |
| Diff coverage | `make unit-diff-cov` | CI, PRs only | ≥ 90% of changed lines in `services/capability-issuer/` and `services/tool-b/` |
| Mutation | `make unit-mutation` | CI | score ≥ 70% (capiss and tool-b) |
| Full E2E suite | see [Test commands](#test-commands) | local, required in step 4 | all pass; warnings reviewed |
| E2E evidence | `make qa-evidence` | local, after the E2E run | every test has premise/exercise/outcome evidence and a PASS line |

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
- Full suite (writes `test_report.log` and evidence under `artifacts/rogue-tests/`):
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
  ```
- Specific test IDs:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
    -e TEST_ONLY=M3.S3-T3,M3.S4-T2 rogue-tests
  ```
- Selected milestones:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
    -e TEST_MILESTONES=m1,m2,m25,m3 rogue-tests
  ```
- A targeted run overwrites `test_report.log`, so `make qa-evidence` needs a full run to pass.
- Live Jira tests (`M5-T55`, `make jira-live-smoke`) need explicit live configuration; default runs
  use deterministic mocks.

Profiling is on by default (`TEST_PROFILE=1`); timings go to `artifacts/rogue-tests/guard_timings.tsv`
and `guard_timings_top25.txt`. Disable with `-e TEST_PROFILE=0`.

## Evidence checks (false-green guard)
After a full run, `make qa-evidence` validates the evidence. To inspect by hand:
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
