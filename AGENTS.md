# AGENTS.md

## Purpose
This file gives coding agents and contributors the minimum, correct operational context for this repo.
Use these commands first before inventing alternatives.

## Operating model (black-box first)
- Treat the system as a black box first:
  - authored intent in `docs/requirements.md`
  - authored runtime/system model in `docs/architecture.md`
  - runtime-visible proof in `trace/tests.yaml` plus evidence artifacts
- Internal implementation artifacts such as `DD-*`, `UT-*`, source helpers, or local test doubles are engineering controls, not the primary proof model for system behavior.
- If a security-relevant behavior depends on hidden state, that behavior must be authored before implementation in:
  - architecture state inventory
  - slice ADR/DDR
  - implementation contract
- Do not introduce or retain runtime-significant behavior that exists only in code.

## Project map
- Compose file: `compose/spiffe.compose.yml`
- Main test harness: `scripts/rogue_node_tests.sh`
- Stack cleanup helper: `scripts/clean_stack.sh`
- Test report output: `test_report.log`
- Evidence artifacts on host: `artifacts/rogue-tests/`
- Unit-test agent guide: `tests/unit/AGENTS.md`
- Slice workflow and templates: `docs/slices/`

## Slice workflow (required for security-relevant work)
Use the 4-phase flow for milestone and security-relevant changes.

1. `Phase 1: plan and review`
   - create a per-slice bundle under `docs/slices/<slice-id>/`
   - update requirements and architecture deltas
   - record ADR/DDR decisions
   - write the implementation and retirement contracts
2. `Phase 2: tests from the approved bundle`
   - add UT/E2E only from the reviewed slice contract
   - if tests require a new assumption, stop and update the slice docs first
3. `Phase 3: implementation and retirement`
   - implement only approved behavior
   - remove dead code, stale compatibility paths, and obsolete artifacts called out in the retirement contract
4. `Phase 4: independent verification`
   - run trace, quality, E2E, and evidence checks
   - record the result in `docs/local_status_capture/implementation_status.md`

Mandatory authoring in every slice bundle:
- authoritative state inventory
- ADR for architecture/runtime trust choices
- DDR for design/implementation-shape choices
- implementation contract
- retirement contract

## Environment assumptions
- Docker Engine + Docker Compose v2 available.
- Works on Linux and macOS with Rancher Desktop.
- Run commands from repo root.

## Quick start (recommended sequence)
1. Preflight:
   ```bash
   docker info >/dev/null
   docker compose version
   docker context ls
   scripts/clean_stack.sh --check
   ```
2. Clean state when needed:
   ```bash
   scripts/clean_stack.sh
   ```
3. Bring core stack up:
   ```bash
   docker compose -f compose/spiffe.compose.yml up -d --build
   ```
4. Inspect SPIRE agent logs for workload SVID activity:
   ```bash
   docker compose -f compose/spiffe.compose.yml logs -f --tail=200 spire-agent
   ```
5. Run full tests:
   ```bash
   docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
   ```
6. Tear down if needed:
   ```bash
   docker compose --profile tests -f compose/spiffe.compose.yml down --remove-orphans
   docker compose -f compose/spiffe.compose.yml down --remove-orphans
   ```

## Test commands
- Full suite (default path):
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
  ```
- Run specific test IDs only:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
    -e TEST_ONLY=M3.S3-T3,M3.S4-T2 rogue-tests
  ```
- Run selected milestones only:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
    -e TEST_MILESTONES=m1,m2,m25,m3 rogue-tests
  ```

## Profiling behavior
- Profiling is enabled by default by the harness (`TEST_PROFILE=1` when unset).
- Full run timing files:
  - `artifacts/rogue-tests/guard_timings.tsv`
  - `artifacts/rogue-tests/guard_timings_top25.txt`
- Disable profiling explicitly:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm \
    -e TEST_PROFILE=0 rogue-tests
  ```

## Evidence validity checks (false-green guard)
After a test run, validate that evidence directories were produced and contain guard artifacts.

- List evidence dirs:
  ```bash
  find artifacts/rogue-tests -maxdepth 1 -mindepth 1 -type d | sort
  ```
- Check each evidence dir has premise/exercise/outcome artifacts:
  ```bash
  for d in artifacts/rogue-tests/*; do
    [ -d "$d" ] || continue
    ls "$d"/premise_*.txt "$d"/exercise_*.txt "$d"/outcome_*.txt >/dev/null 2>&1 \
      || echo "MISSING_GUARD_ARTIFACTS: $d"
  done
  ```
- Check for explicit test failures recorded by harness:
  ```bash
  if grep -Eq 'Failed: [1-9]' test_report.log; then
    find artifacts/rogue-tests -name fail_reason.txt -print -exec cat {} \;
  else
    echo "No failed tests recorded in test_report.log"
  fi
  ```
- Check for accepted alternate-success warnings recorded by harness:
  ```bash
  find artifacts/rogue-tests -name 'warning_reason_*.txt' -print -exec cat {} \;
  ```
- Evidence semantics:
  - `fail_reason.txt` means a terminal guard failure for that test.
  - `warning_reason_*.txt` means the test passed through an accepted alternate-success path and the condition should be reviewed.
  - `test_report.log` now prints a `Warnings:` count and `Warnings summary:` section when such cases occur.

## macOS with Rancher Desktop notes
- Ensure Docker CLI points to Rancher Desktop context before running tests:
  ```bash
  docker context ls
  if docker context ls --format '{{.Name}}' | grep -Fxq rancher-desktop; then
    docker context use rancher-desktop
  else
    echo "rancher-desktop context not present on this host"
  fi
  ```
- If Docker socket/context mismatches occur, confirm `docker info` works and rerun `scripts/clean_stack.sh`.
- If bind-mounted files under `tmp_svid/` or `artifacts/` become permission-constrained, rerun `scripts/clean_stack.sh` (it includes fallback cleanup paths).

## Known operational guardrails
- `capability-issuer-no-opa-envoy` is test-only (`tests` profile). Do not use it for non-test flows.
- Prefer `scripts/clean_stack.sh` over ad-hoc manual cleanup.
- Keep evidence under `artifacts/rogue-tests/`; do not redirect unless you intentionally set `ROGUE_TEST_EVIDENCE_DIR`.
- Architecture diagrams should use a C4-style, grid-aligned layout:
  - group components by trust boundary or network zone
  - keep flows mostly left-to-right or top-to-bottom
  - prefer orthogonal connectors with minimal crossings
  - label target-state or planned components explicitly
  - avoid ad-hoc diagrams with diagonal arrow clutter or ambiguous trust boundaries
- Never run Docker lifecycle commands in parallel in this repo.
  Serialize:
  - `scripts/clean_stack.sh`
  - `docker compose ... up ...`
  - `docker compose ... down ...`
  - `docker compose ... run ...`
  - only run `docker compose ... ps` or log inspection after the mutating command has completed

## Unit-test guardrails (summary)
- For unit-test implementation details and commands, use `tests/unit/AGENTS.md`.
- Unit tests under `tests/unit/**` must follow Premise/Exercise/Outcome guard style and pass:
  - `make unit-guard-check`
  - `make unit-trust`

## Traceability and quality commands
- Validate cross-layer traceability (`requirements -> architecture -> design -> tests`):
  ```bash
  make qa-trace
  ```
  - Uses `docs/requirements.md` as the authored requirement source and `docs/architecture.md` as the authored architecture source.
  - Uses layer-correct mapping only:
    - `REQ -> ARCH`
    - `ARCH -> DD`
    - `DD -> UT`
    - `REQ -> E2E`
    - future `ARCH -> IT`
  - Uses source-embedded `DD-*` tags on service implementation functions under `services/**`.
  - Uses source-embedded `UT-*` blocks on unit test functions under `tests/unit/**`.
  - `trace/tests.yaml` remains the authored non-unit test map:
    - `e2e_suite/e2e_case -> source_requirements`
    - `integration_case -> source_architecture`
  - For black-box trust, requirement satisfaction should be argued primarily through authored runtime mappings and evidence, not through unit-level implementation summaries.
  - Structural failures are blocking. Coverage gaps are reported but are not forced closed.
- Validate E2E evidence completeness (post test-run):
  ```bash
  make qa-evidence
  ```
  - Reports explicit warnings for accepted alternate-success paths.
  - Fails if any passing test still leaves `fail_reason.txt`.
- Run local quality baseline:
  ```bash
  make qa-quality
  ```
