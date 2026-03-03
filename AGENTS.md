# AGENTS.md

## Purpose
This file gives coding agents and contributors the minimum, correct operational context for this repo.
Use these commands first before inventing alternatives.

## Project map
- Compose file: `compose/spiffe.compose.yml`
- Main test harness: `scripts/rogue_node_tests.sh`
- Stack cleanup helper: `scripts/clean_stack.sh`
- Test report output: `test_report.log`
- Evidence artifacts on host: `artifacts/rogue-tests/`
- Unit-test agent guide: `tests/unit/AGENTS.md`

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

## Unit-test guardrails (summary)
- For unit-test implementation details and commands, use `tests/unit/AGENTS.md`.
- Unit tests under `tests/unit/**` must follow Premise/Exercise/Outcome guard style and pass:
  - `make unit-guard-check`
  - `make unit-trust`
