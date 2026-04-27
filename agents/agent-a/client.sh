#!/bin/sh
set -e

SPIRE_SOCKET="${SPIRE_AGENT_SOCKET:-/run/spire/agent/private/api.sock}"
SVID_DIR="${SPIRE_SVID_DIR:-/run/spire/svid}"
SERVER_EXPECTED_SPIFFE_ID="${TOOL_B_SPIFFE_ID:-spiffe://example.org/tool-b-envoy}"
CAPISS_EXPECTED_SPIFFE_ID="${CAPABILITY_ISSUER_SPIFFE_ID:-spiffe://example.org/capability-issuer-envoy}"

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

verified_https_request() {
  url="$1"
  expected_spiffe_id="$2"
  method="$3"
  body="$4"

  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\([^/:]*\).*#\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\([0-9]*\).*#\1#p')"
  path="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/]*\(/.*\)$#\1#p')"
  if [ -z "$port" ]; then
    port="443"
  fi
  if [ -z "$path" ]; then
    path="/"
  fi

  tmpdir="$(mktemp -d)"
  req_file="$tmpdir/request.txt"
  body_file="$tmpdir/body.txt"
  http_file="$tmpdir/http.txt"
  diag_file="$tmpdir/diag.txt"
  cert_file="$tmpdir/server.pem"

  if [ "$method" = "POST" ]; then
    printf '%s' "$body" >"$body_file"
    body_len="$(wc -c <"$body_file" | tr -d ' ')"
  else
    : >"$body_file"
    body_len="0"
  fi

  {
    printf '%s %s HTTP/1.1\r\n' "$method" "$path"
    printf 'Host: %s\r\n' "$host"
    printf 'Connection: close\r\n'
    if [ "$method" = "POST" ]; then
      printf 'Content-Type: application/json\r\n'
      printf 'Content-Length: %s\r\n' "$body_len"
    fi
    printf '\r\n'
    if [ "$method" = "POST" ]; then
      cat "$body_file"
    fi
  } >"$req_file"

  set +e
  timeout 15s openssl s_client \
    -connect "${host}:${port}" \
    -servername "$host" \
    -cert "$SVID_DIR/svid.pem" \
    -key "$SVID_DIR/svid.key" \
    -CAfile "$SVID_DIR/bundle.pem" \
    -verify_return_error \
    -showcerts \
    -ign_eof \
    <"$req_file" >"$http_file" 2>"$diag_file"
  rc=$?
  set -e

  actual_spiffe_id=""
  if awk 'BEGIN{p=0} /BEGIN CERTIFICATE/{p=1} p{print} /END CERTIFICATE/{exit}' "$diag_file" >"$cert_file" 2>/dev/null && [ -s "$cert_file" ]; then
    actual_spiffe_id="$(openssl x509 -in "$cert_file" -noout -ext subjectAltName 2>/dev/null | sed -n 's/.*URI:\(spiffe:[^,]*\).*/\1/p' | head -n 1)"
  fi

  verify_result="fail"
  if [ "$rc" -eq 0 ] &&
    grep -Eq 'Verification: OK|Verify return code: 0 \(ok\)' "$diag_file" &&
    [ "$actual_spiffe_id" = "$expected_spiffe_id" ]; then
    verify_result="ok"
  fi

  echo "$host SPIFFE ID: $actual_spiffe_id"
  echo "$host verification result: $verify_result"

  if [ "$verify_result" != "ok" ]; then
    rm -rf "$tmpdir"
    echo "ERROR: verified request failed for $host" >&2
    exit 1
  fi

  VERIFIED_HTTP_STATUS="$(tr -d '\r' <"$http_file" | awk '/^HTTP\//{print $2; exit}')"
  tr -d '\r' <"$http_file" | awk '
    BEGIN {http=0; body=0}
    /^HTTP\// {http=1; next}
    http && body==0 && /^$/ {body=1; next}
    http && body==1 {print}
  ' >"$tmpdir/response_body.txt"
  VERIFIED_HTTP_BODY_FILE="$tmpdir/response_body.txt"
}

wait_for_verified_health() {
  url="$1"
  expected_spiffe_id="$2"
  ready=0
  for i in $(seq 1 40); do
    if verified_https_request "$url/health" "$expected_spiffe_id" GET "" >/dev/null 2>&1 && [ "$VERIFIED_HTTP_STATUS" = "200" ]; then
      ready=1
      break
    fi
    sleep 0.2
  done
  if [ "$ready" -ne 1 ]; then
    echo "ERROR: verified health check failed for $url after 40 attempts" >&2
    exit 1
  fi
}

echo "Waiting for tool-b-envoy to startup..."
wait_for_verified_health "$TOOL_B_URL" "$SERVER_EXPECTED_SPIFFE_ID"

echo "Calling: $TOOL_B_URL/health"
verified_https_request "$TOOL_B_URL/health" "$SERVER_EXPECTED_SPIFFE_ID" GET ""
if [ "$VERIFIED_HTTP_STATUS" != "200" ]; then
  echo "ERROR: tool-b-envoy /health returned status $VERIFIED_HTTP_STATUS" >&2
  exit 1
fi
cat "$VERIFIED_HTTP_BODY_FILE"
echo ""

echo "Calling: $TOOL_B_URL/secret"
verified_https_request "$TOOL_B_URL/secret" "$SERVER_EXPECTED_SPIFFE_ID" GET ""
if [ "$VERIFIED_HTTP_STATUS" != "200" ]; then
  echo "ERROR: tool-b-envoy /secret returned status $VERIFIED_HTTP_STATUS" >&2
  exit 1
fi
cat "$VERIFIED_HTTP_BODY_FILE"
echo ""

if [ -n "${CAPABILITY_ISSUER_URL:-}" ]; then
  echo "Waiting for capability-issuer-envoy to startup..."
  wait_for_verified_health "$CAPABILITY_ISSUER_URL" "$CAPISS_EXPECTED_SPIFFE_ID"

  echo "Calling: $CAPABILITY_ISSUER_URL/capabilities/mint"
  verified_https_request "$CAPABILITY_ISSUER_URL/capabilities/mint" "$CAPISS_EXPECTED_SPIFFE_ID" POST '{"aud":"tool-b","act":"read","res":"tool-b:/secret"}'
  if [ "$VERIFIED_HTTP_STATUS" != "200" ]; then
    echo "ERROR: capability-issuer mint returned status $VERIFIED_HTTP_STATUS" >&2
    exit 1
  fi
  cat "$VERIFIED_HTTP_BODY_FILE"
  echo ""
fi
