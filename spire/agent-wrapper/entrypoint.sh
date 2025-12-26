#!/bin/sh
set -eu

SPIRE_AGENT_BIN="/opt/spire/bin/spire-agent"
TOKEN_FILE="/run/spire/shared/join_token"
CONFIG_FILE="/run/spire/agent/agent.conf"

while [ ! -s "$TOKEN_FILE" ]; do
  sleep 0.5
done

TOKEN="$(cat "$TOKEN_FILE")"
if [ -z "$TOKEN" ]; then
  echo "join token is empty" >&2
  exit 1
fi

exec "$SPIRE_AGENT_BIN" run -config "$CONFIG_FILE" -joinToken "$TOKEN"
