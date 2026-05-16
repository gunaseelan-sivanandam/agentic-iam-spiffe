#!/bin/sh
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-compose/spiffe.compose.yml}"
SERVICE="codex-jira-mcp-adapter"

container_id="$(docker compose -f "$COMPOSE_FILE" ps -q "$SERVICE" 2>/dev/null || true)"
if [ -z "$container_id" ]; then
  echo "codex-jira-mcp-adapter is not running; start the Docker/SPIFFE stack first" >&2
  exit 1
fi

state="$(docker inspect -f '{{.State.Running}}' "$container_id" 2>/dev/null || true)"
if [ "$state" != "true" ]; then
  echo "codex-jira-mcp-adapter container is not running" >&2
  exit 1
fi

exec docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE" python /app/server.py
