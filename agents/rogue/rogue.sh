#!/bin/sh
# Placeholder for rogue agent script (implementation to be added later).
set -e

SPIRE_SOCKET="${SPIRE_AGENT_SOCKET:-/run/spire/agent/private/api.sock}"
SVID_DIR="${SPIRE_SVID_DIR:-/run/spire/svid}"

if [ -z "$TOOL_B_URL" ]; then
  echo "ERROR: TOOL_B_URL is not set"
  exit 1
fi

mkdir -p "$SVID_DIR"
while [ ! -S "$SPIRE_SOCKET" ]; do
  sleep 0.5
done

ready=0
last_err=""
for i in $(seq 1 40); do
  if /opt/spire/bin/spire-agent api fetch x509 -socketPath "$SPIRE_SOCKET" -write "$SVID_DIR" >/dev/null 2>"/tmp/spire_fetch.err"; then
    ready=1
    break
  fi
  last_err="$(cat /tmp/spire_fetch.err 2>/dev/null || true)"
  sleep 0.5
done

if [ "$ready" -ne 1 ]; then
  echo "ERROR: failed to fetch SVID from SPIRE agent: $last_err" >&2
  exit 1
fi

if [ -f "$SVID_DIR/svid.0.pem" ] && [ -f "$SVID_DIR/svid.0.key" ] && [ -f "$SVID_DIR/bundle.0.pem" ]; then
  ln -sf "$SVID_DIR/svid.0.pem" "$SVID_DIR/svid.pem"
  ln -sf "$SVID_DIR/svid.0.key" "$SVID_DIR/svid.key"
  ln -sf "$SVID_DIR/bundle.0.pem" "$SVID_DIR/bundle.pem"
fi

echo "Waiting for tool-b-envoy to startup..."
ready=0
for i in $(seq 1 40); do
  status="$(curl -sS -o /dev/null -w '%{http_code}' --insecure \
    --cert "$SVID_DIR/svid.pem" --key "$SVID_DIR/svid.key" "$TOOL_B_URL/health" || true)"
  if [ "$status" = "403" ] || [ "$status" = "200" ]; then
    ready=1
    break
  fi
  sleep 0.2
done

if [ "$ready" -ne 1 ]; then
  echo "ERROR: tool-b-envoy not reachable at $TOOL_B_URL after 40 attempts"
  exit 1
fi

expect_forbidden() {
  url="$1"
  echo "Calling: $url"
  status="$(curl -sS -o /tmp/rogue_out -w '%{http_code}' --insecure \
    --cert "$SVID_DIR/svid.pem" --key "$SVID_DIR/svid.key" "$url" || true)"
  echo "$(cat /tmp/rogue_out)"
  echo ""
  if [ "$status" != "403" ]; then
    echo "ERROR: expected 403 from $url, got $status" >&2
    exit 1
  fi
}

expect_forbidden "$TOOL_B_URL/health"
expect_forbidden "$TOOL_B_URL/secret"
