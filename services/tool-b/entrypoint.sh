#!/bin/sh
set -eu

SOCKET="${SPIRE_AGENT_SOCKET:-/run/spire/agent/private/api.sock}"
SVID_DIR="${SPIRE_SVID_DIR:-/run/spire/svid}"
SVID_CERT="${SPIFFE_SVID_CERT:-$SVID_DIR/svid.pem}"
SVID_KEY="${SPIFFE_SVID_KEY:-$SVID_DIR/svid.key}"
TRUST_BUNDLE="${SPIFFE_TRUST_BUNDLE:-$SVID_DIR/bundle.pem}"

mkdir -p "$SVID_DIR"
while [ ! -S "$SOCKET" ]; do
  sleep 0.5
done

ready=0
last_err=""
for i in $(seq 1 40); do
  if /opt/spire/bin/spire-agent api fetch x509 -socketPath "$SOCKET" -write "$SVID_DIR" >/dev/null 2>"/tmp/spire_fetch.err"; then
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

exec python -u /app/server.py
