#!/usr/bin/env bash
# Full E2E suite, as the CI `e2e` job and the local step-4 run use it (`make e2e`): build every
# image, run the suite, then give the root-owned output back to the invoking user so `make
# qa-evidence` can read it and write artifacts/quality/. Exits with the suite's exit code; a failed
# reset, build or ownership step also fails. Start from a clean stack (scripts/clean_stack.sh).
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/compose/spiffe.compose.yml"

# A run that never starts must not leave the previous run's report and evidence for qa-evidence to
# pass on. They may be root-owned, so they are removed through a container.
if ! docker run --rm -v "$ROOT_DIR:/repo" alpine:3.19 sh -c \
  "rm -rf /repo/test_report.log /repo/artifacts/rogue-tests && mkdir -p /repo/artifacts/rogue-tests && chown $(id -u):$(id -g) /repo/artifacts/rogue-tests"; then
  echo "[e2e] FAILED: could not remove the previous run's report and evidence" >&2
  exit 1
fi

if ! docker compose --profile tests -f "$COMPOSE_FILE" build; then
  echo "[e2e] FAILED: image build" >&2
  exit 1
fi

docker compose --profile tests -f "$COMPOSE_FILE" up --abort-on-container-exit --exit-code-from rogue-tests rogue-tests
rc=$?

# rogue-tests runs as root and writes test_report.log and artifacts/rogue-tests/.
if ! docker run --rm -v "$ROOT_DIR:/repo" alpine:3.19 sh -c \
  "for p in /repo/artifacts /repo/test_report.log; do [ ! -e \"\$p\" ] || chown -R $(id -u):$(id -g) \"\$p\" || exit 1; done"; then
  echo "[e2e] FAILED: could not take ownership of artifacts/ and test_report.log" >&2
  [ "$rc" -ne 0 ] || rc=1
fi

echo "[e2e] suite exit code: $rc"
exit "$rc"
