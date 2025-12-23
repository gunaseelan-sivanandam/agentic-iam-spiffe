#!/bin/sh
# Placeholder for rogue agent script (implementation to be added later).
set -e

if [ -z "$TOOL_B_URL" ]; then
  echo "ERROR: TOOL_B_URL is not set"
  exit 1
fi

echo "Waiting for tool-b to startup..."
ready=0
for i in $(seq 1 40); do
  if curl -sS --fail "$TOOL_B_URL/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 0.2
done

if [ "$ready" -ne 1 ]; then
  echo "ERROR: tool-b not reachable at $TOOL_B_URL after 40 attempts"
  exit 1
fi

echo "Calling: $TOOL_B_URL/health"
if ! curl -sS --fail "$TOOL_B_URL/health"; then
  echo "ERROR: curl failed for $TOOL_B_URL/health"
  exit 1
fi
echo ""

echo "Calling: $TOOL_B_URL/secret"
if ! curl -sS --fail "$TOOL_B_URL/secret"; then
  echo "ERROR: curl failed for $TOOL_B_URL/secret"
  exit 1
fi
echo ""
