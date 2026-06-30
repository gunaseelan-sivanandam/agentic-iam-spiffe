#!/bin/sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-compose/spiffe.compose.yml}"
SERVICE="codex-jira-mcp-adapter"

case "$COMPOSE_FILE" in
  "$ROOT_DIR"/compose/spiffe.compose.yml)
    COMPOSE_FILE="compose/spiffe.compose.yml"
    ;;
esac

cd "$ROOT_DIR"

if ! container_id="$(docker compose -f "$COMPOSE_FILE" ps -q "$SERVICE" 2>&1)"; then
  printf '%s\n' "$container_id" >&2
  echo "failed to inspect codex-jira-mcp-adapter; verify Docker access and Codex trust rules" >&2
  exit 1
fi
if [ -z "$container_id" ]; then
  echo "codex-jira-mcp-adapter is not running; start the Docker/SPIFFE stack first" >&2
  exit 1
fi

if ! state="$(docker inspect -f '{{.State.Running}}' "$container_id" 2>&1)"; then
  printf '%s\n' "$state" >&2
  echo "failed to inspect codex-jira-mcp-adapter container state" >&2
  exit 1
fi
if [ "$state" != "true" ]; then
  echo "codex-jira-mcp-adapter container is not running" >&2
  exit 1
fi

exec docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE" python /app/server.py
