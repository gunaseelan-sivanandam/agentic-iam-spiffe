#!/bin/sh
# Placeholder for Agent A client script (implementation to be added later).
set -e

SPIRE_SOCKET="${SPIRE_AGENT_SOCKET:-/run/spire/agent/private/api.sock}"
SVID_DIR="${SPIRE_SVID_DIR:-/run/spire/svid}"
SERVER_EXPECTED_SPIFFE_ID="${TOOL_B_SPIFFE_ID:-spiffe://example.org/tool-b}"

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

CLIENT_SPIFFE_ID="$(openssl x509 -in "$SVID_DIR/svid.pem" -noout -ext subjectAltName | sed -n 's/.*URI:\(spiffe:[^,]*\).*/\1/p' | head -n 1)"
echo "agent-a SPIFFE ID: $CLIENT_SPIFFE_ID"

echo "Waiting for tool-b to startup..."
ready=0
for i in $(seq 1 40); do
  if curl -sS --fail --insecure --cert "$SVID_DIR/svid.pem" --key "$SVID_DIR/svid.key" "$TOOL_B_URL/health" >/dev/null 2>&1; then
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
if ! curl -sS --fail --insecure --cert "$SVID_DIR/svid.pem" --key "$SVID_DIR/svid.key" "$TOOL_B_URL/health"; then
  echo "ERROR: curl failed for $TOOL_B_URL/health"
  exit 1
fi
echo ""

request_secret_via_openssl() {
  tmpdir="$(mktemp -d)"
  fifo="$tmpdir/in"
  out="$tmpdir/out"
  : >"$out"
  mkfifo "$fifo"
  exec 3<>"$fifo"

  stdbuf -oL -eL openssl s_client \
    -connect tool-b:8443 \
    -cert "$SVID_DIR/svid.pem" \
    -key "$SVID_DIR/svid.key" \
    -CAfile "$SVID_DIR/bundle.pem" \
    -verify_return_error \
    -showcerts \
    -ign_eof \
    <"$fifo" >"$out" 2>&1 &
  pid="$!"

  i=0
  while [ $i -lt 50 ]; do
    if grep -q "BEGIN CERTIFICATE" "$out"; then
      break
    fi
    i=$((i + 1))
    sleep 0.1
  done
  if ! grep -q "BEGIN CERTIFICATE" "$out"; then
    echo "ERROR: did not receive server certificate" >&2
    kill "$pid" 2>/dev/null || true
    rm -rf "$tmpdir"
    exit 1
  fi

  awk 'BEGIN{p=0} /BEGIN CERTIFICATE/{p=1} p{print} /END CERTIFICATE/{exit}' "$out" >"$tmpdir/server.pem"
  SERVER_SPIFFE_ID="$(openssl x509 -in "$tmpdir/server.pem" -noout -ext subjectAltName | sed -n 's/.*URI:\(spiffe:[^,]*\).*/\1/p' | head -n 1)"
  echo "tool-b SPIFFE ID: $SERVER_SPIFFE_ID"

  i=0
  verified="unknown"
  while [ $i -lt 50 ]; do
    if grep -q "Verification: OK" "$out"; then
      verified="ok"
      break
    fi
    if grep -q "Verify return code:" "$out"; then
      if grep -q "Verify return code: 0 (ok)" "$out"; then
        verified="ok"
      else
        verified="fail"
      fi
      break
    fi
    i=$((i + 1))
    sleep 0.1
  done

  echo "tool-b verification result: $verified"
  if [ "$verified" != "ok" ]; then
    kill "$pid" 2>/dev/null || true
    rm -rf "$tmpdir"
    echo "ERROR: tool-b certificate verification failed" >&2
    exit 1
  fi

  if [ "$SERVER_SPIFFE_ID" != "$SERVER_EXPECTED_SPIFFE_ID" ]; then
    kill "$pid" 2>/dev/null || true
    rm -rf "$tmpdir"
    echo "ERROR: tool-b SPIFFE ID mismatch (got: $SERVER_SPIFFE_ID)" >&2
    exit 1
  fi
  echo "tool-b SPIFFE ID match: yes"
  printf 'GET /secret HTTP/1.1\r\nHost: tool-b\r\nConnection: close\r\n\r\n' >&3

  wait "$pid" || true

  status="$(tr -d '\r' <"$out" | grep -m1 '^HTTP/' | awk '{print $2}')"
  body="$(tr -d '\r' <"$out" | grep -m1 -o '{.*}')"

  if [ "$status" != "200" ]; then
    rm -rf "$tmpdir"
    echo "ERROR: tool-b /secret returned status $status" >&2
    exit 1
  fi
  echo "$body"

  exec 3>&-
  rm -rf "$tmpdir"
}

echo "Calling: $TOOL_B_URL/secret"
request_secret_via_openssl
echo ""
