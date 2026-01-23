#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/compose/spiffe.compose.yml}"
CHECK_ONLY=0
STOPPED_STACK=0
STARTED_SPIRE=0
WARNINGS=()
CLEANED_TMP=0
CLEANED_SPIDATA=0

if [ "${1:-}" = "--check" ]; then
  CHECK_ONLY=1
fi

if [ -z "${ROOT_DIR:-}" ] || [ "$ROOT_DIR" = "/" ]; then
  echo "ERROR: invalid repo root: '$ROOT_DIR'" >&2
  exit 1
fi
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "ERROR: compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not found in PATH" >&2
  exit 1
fi
if [ "$CHECK_ONLY" -eq 1 ]; then
  echo "OK: prerequisites look good"
  exit 0
fi

safe_rm_rf() {
  target="$1"
  if [ -z "$target" ]; then
    WARNINGS+=("skip empty delete target")
    return 1
  fi
  case "$target" in
    "$ROOT_DIR"/*) ;;
    *) WARNINGS+=("refuse delete outside repo: $target"); return 1 ;;
  esac
  if ! rm -rf "$target" 2>"/tmp/clean_stack_rm.err"; then
    if [ -s /tmp/clean_stack_rm.err ]; then
      WARNINGS+=("rm failed for $target: $(tail -n 1 /tmp/clean_stack_rm.err)")
    else
      WARNINGS+=("rm failed for $target")
    fi
    rm -f /tmp/clean_stack_rm.err >/dev/null 2>&1 || true
    return 1
  fi
  rm -f /tmp/clean_stack_rm.err >/dev/null 2>&1 || true
  return 0
}

container_running() {
  name="$1"
  docker ps --format '{{.Names}}' | grep -Fxq "$name"
}

compose_running_ids() {
  docker compose -f "$COMPOSE_FILE" ps -q 2>/dev/null || true
}

echo "Bringing stack down (if running)..."
if docker compose -f "$COMPOSE_FILE" down --remove-orphans >/dev/null 2>&1; then
  STOPPED_STACK=1
fi

running_ids="$(compose_running_ids)"
if [ -n "$running_ids" ]; then
  echo "Stack still running; forcing container stop..."
  docker rm -f $running_ids >/dev/null 2>&1 || WARNINGS+=("failed to force-remove some containers")
  docker compose -f "$COMPOSE_FILE" down --remove-orphans >/dev/null 2>&1 || true
fi

if ! container_running "spiffe-spire-server" || ! container_running "spiffe-spire-agent"; then
  echo "Starting spire-server/spire-agent to clean mounted data..."
  if docker compose -f "$COMPOSE_FILE" up -d spire-server spire-agent >/dev/null 2>&1; then
    STARTED_SPIRE=1
  else
    WARNINGS+=("failed to start spire-server/spire-agent for cleanup")
  fi
fi

if container_running "spiffe-spire-server"; then
  echo "Cleaning SPIRE server data + join token..."
  docker run --rm --volumes-from spiffe-spire-server alpine:3.19 \
    sh -lc 'rm -rf /run/spire/server/data/* /run/spire/shared/join_token || true' >/dev/null 2>&1 || true
  CLEANED_SPIDATA=1
fi

if container_running "spiffe-spire-agent"; then
  echo "Cleaning SPIRE agent data + join token..."
  docker run --rm --volumes-from spiffe-spire-agent alpine:3.19 \
    sh -lc 'rm -rf /run/spire/agent/data/* /run/spire/shared/join_token || true' >/dev/null 2>&1 || true
  CLEANED_SPIDATA=1
fi

echo "Bringing stack down..."
docker compose -f "$COMPOSE_FILE" down --remove-orphans >/dev/null 2>&1 || true

echo "Cleaning local temp folders..."
if safe_rm_rf "$ROOT_DIR/tmp_svid"; then
  CLEANED_TMP=1
else
  if docker run --rm -v "$ROOT_DIR/tmp_svid:/tmp_svid" alpine:3.19 \
    sh -lc 'rm -rf /tmp_svid/*' >/dev/null 2>&1; then
    CLEANED_TMP=1
  else
    WARNINGS+=("failed to clean tmp_svid (permission denied)")
  fi
fi
rm -rf /tmp/rogue-tests >/dev/null 2>&1 || true

echo "Summary:"
echo "  stopped_stack=$STOPPED_STACK started_spire_cleanup=$STARTED_SPIRE cleaned_spire_data=$CLEANED_SPIDATA cleaned_tmp_svid=$CLEANED_TMP"
if [ "${#WARNINGS[@]}" -gt 0 ]; then
  echo "Warnings:"
  for w in "${WARNINGS[@]}"; do
    echo "  - $w"
  done
fi
