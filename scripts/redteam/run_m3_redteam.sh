#!/bin/sh
set -eu

ROGUE_CONTAINER="${ROGUE_CONTAINER:-spiffe-rogue}"
AGENT_CONTAINER="${AGENT_CONTAINER:-spiffe-agent-a}"

CAPISS_MINT_URL="https://capability-issuer-envoy:9443/capabilities/mint"
CAPISS_NO_OPA_URL="https://capability-issuer-no-opa-envoy:9444/capabilities/mint"
CAPISS_NO_OPA_HEALTH_URL="https://capability-issuer-no-opa-envoy:9444/health"
TOOLB_SECRET_URL="https://tool-b-envoy:8443/secret"

MINT_BODY='{"aud":"tool-b","act":"read","res":"/secret"}'

log() {
  printf '%s\n' "$*"
}

run_in() {
  container="$1"
  shift
  docker exec "$container" sh -c "$*"
}

encode_body() {
  printf '%s' "$1" | base64 | tr -d '\n'
}

prep_svid() {
  container="$1"
  run_in "$container" 'set -e
    mkdir -p /tmp/rt_svid
    /opt/spire/bin/spire-agent api fetch x509 -socketPath /run/spire/agent/private/api.sock -write /tmp/rt_svid >/dev/null 2>&1
    ln -sf /tmp/rt_svid/svid.0.pem /tmp/rt_svid/svid.pem
    ln -sf /tmp/rt_svid/svid.0.key /tmp/rt_svid/svid.key
    ln -sf /tmp/rt_svid/bundle.0.pem /tmp/rt_svid/bundle.pem
  '
}

rogue_curl_tls() {
  method="$1"
  url="$2"
  body="${3:-}"
  header="${4:-}"
  if [ -n "$body" ]; then
    body_b64="$(encode_body "$body")"
  else
    body_b64=""
  fi
  run_in "$ROGUE_CONTAINER" "
    set -e
    if [ -n \"$body_b64\" ]; then
      body_b64='$body_b64'
      body=\$(printf '%s' \"\$body_b64\" | base64 -d)
      curl -sS -o /tmp/rt_body -w '%{http_code}' --insecure \\
        --cert /tmp/rt_svid/svid.pem --key /tmp/rt_svid/svid.key \\
        --cacert /tmp/rt_svid/bundle.pem \\
        -X $method -H 'Content-Type: application/json' $header \\
        -d \"\$body\" '$url'
    else
      curl -sS -o /tmp/rt_body -w '%{http_code}' --insecure \\
        --cert /tmp/rt_svid/svid.pem --key /tmp/rt_svid/svid.key \\
        --cacert /tmp/rt_svid/bundle.pem \\
        -X $method $header '$url'
    fi
  "
}

agent_curl_tls() {
  method="$1"
  url="$2"
  body="${3:-}"
  header="${4:-}"
  if [ -n "$body" ]; then
    body_b64="$(encode_body "$body")"
  else
    body_b64=""
  fi
  run_in "$AGENT_CONTAINER" "
    set -e
    mkdir -p /tmp/rt_svid
    /opt/spire/bin/spire-agent api fetch x509 -socketPath /run/spire/agent/private/api.sock -write /tmp/rt_svid >/dev/null 2>&1
    ln -sf /tmp/rt_svid/svid.0.pem /tmp/rt_svid/svid.pem
    ln -sf /tmp/rt_svid/svid.0.key /tmp/rt_svid/svid.key
    ln -sf /tmp/rt_svid/bundle.0.pem /tmp/rt_svid/bundle.pem
    if [ -n \"$body_b64\" ]; then
      body_b64='$body_b64'
      body=\$(printf '%s' \"\$body_b64\" | base64 -d)
      curl -sS -o /tmp/rt_body -w '%{http_code}' --insecure \\
        --cert /tmp/rt_svid/svid.pem --key /tmp/rt_svid/svid.key \\
        --cacert /tmp/rt_svid/bundle.pem \\
        -X $method -H 'Content-Type: application/json' $header -d \"\$body\" '$url'
    else
      curl -sS -o /tmp/rt_body -w '%{http_code}' --insecure \\
        --cert /tmp/rt_svid/svid.pem --key /tmp/rt_svid/svid.key \\
        --cacert /tmp/rt_svid/bundle.pem \\
        -X $method $header '$url'
    fi
  "
}

get_agent_token() {
  status="$(agent_curl_tls POST "$CAPISS_MINT_URL" "$MINT_BODY")"
  body="$(run_in "$AGENT_CONTAINER" 'cat /tmp/rt_body')"
  compact="$(printf '%s' "$body" | tr -d ' \r\n')"
  token="$(printf '%s' "$compact" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')"
  expires_at="$(printf '%s' "$compact" | sed -n 's/.*"expires_at":\([0-9][0-9]*\).*/\1/p')"
  if [ -z "$token" ]; then
    printf '%s\n' "C4 token parse failed, body=$body" >&2
  fi
  printf '%s|%s|%s\n' "$status" "$token" "$expires_at"
}

log "Preparing SVIDs..."
prep_svid "$ROGUE_CONTAINER"

log ""
log "A. Network boundary attacks"
if run_in "$ROGUE_CONTAINER" "curl -sS --max-time 2 http://opa:8181/v1/data/capiss/allow >/dev/null 2>&1"; then
  log "A1 FAIL: OPA reachable from rogue"
else
  log "A1 PASS: OPA not reachable from rogue"
fi
if run_in "$ROGUE_CONTAINER" "curl -sS --max-time 2 http://capability-issuer:8000/health >/dev/null 2>&1"; then
  log "A2 FAIL: capiss app reachable from rogue"
else
  log "A2 PASS: capiss app not reachable from rogue"
fi
if run_in "$ROGUE_CONTAINER" "curl -sS --max-time 2 http://tool-b:8080/health >/dev/null 2>&1"; then
  log "A3 FAIL: tool-b app reachable from rogue"
else
  log "A3 PASS: tool-b app not reachable from rogue"
fi

log ""
log "B. Mint endpoint abuse (rogue)"
status="$(rogue_curl_tls POST "$CAPISS_MINT_URL" "{}")"
log "B1 empty body status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
status="$(rogue_curl_tls POST "$CAPISS_MINT_URL" '{"aud":0,"act":"read","res":"/secret"}')"
log "B1 wrong type status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
status="$(rogue_curl_tls POST "$CAPISS_MINT_URL" '{"aud":"tool-b ","act":"read","res":"/secret"}')"
log "B3 aud trailing space status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
status="$(rogue_curl_tls POST "$CAPISS_MINT_URL" '{"aud":"tool-b","act":"READ","res":"/secret"}')"
log "B4 act case status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
status="$(rogue_curl_tls POST "$CAPISS_MINT_URL" '{"aud":"tool-b","act":"read","res":"/secret/"}')"
log "B2 res slash status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
status="$(rogue_curl_tls POST "$CAPISS_MINT_URL" '{"aud":"tool-b","act":"read","res":"/secret%2f.."}')"
log "B2 res encoding status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"

log "B5 high-rate minting (rogue, 20 attempts)"
success=0
for i in $(seq 1 20); do
  code="$(rogue_curl_tls POST "$CAPISS_MINT_URL" "$MINT_BODY")"
  if [ "$code" = "200" ]; then
    success=1
    break
  fi
done
if [ "$success" -eq 1 ]; then
  log "B5 FAIL: rogue minted capability"
else
  log "B5 PASS: rogue minting denied"
fi

log "B6 OPA unavailable (if test envoy present)"
if run_in "$ROGUE_CONTAINER" "curl -sS --max-time 2 --insecure --cert /tmp/rt_svid/svid.pem --key /tmp/rt_svid/svid.key $CAPISS_NO_OPA_HEALTH_URL >/dev/null 2>&1"; then
  status="$(rogue_curl_tls POST "$CAPISS_NO_OPA_URL" "$MINT_BODY")"
  log "B6 status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
else
  log "B6 SKIP: capability-issuer-no-opa-envoy not reachable"
fi

log ""
log "C. Token misuse against tool-b"
status="$(rogue_curl_tls GET "$TOOLB_SECRET_URL")"
log "C1 identity-only status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
status="$(rogue_curl_tls GET "$TOOLB_SECRET_URL" "" "-H 'Authorization: Bearer not-a-token'")"
log "C3 garbage token status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"

agent_token_info="$(get_agent_token)"
agent_status="$(printf '%s' "$agent_token_info" | cut -d'|' -f1)"
agent_token="$(printf '%s' "$agent_token_info" | cut -d'|' -f2)"
agent_exp="$(printf '%s' "$agent_token_info" | cut -d'|' -f3)"
log "C4 agent-a mint status: $agent_status"
if [ -n "$agent_token" ]; then
  status="$(rogue_curl_tls GET "$TOOLB_SECRET_URL" "" "-H 'Authorization: Bearer ${agent_token}'")"
  log "C4 stolen token replay status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
  tampered="${agent_token%?}x"
  status="$(rogue_curl_tls GET "$TOOLB_SECRET_URL" "" "-H 'Authorization: Bearer ${tampered}'")"
  log "C6 tampered token status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
  status="$(agent_curl_tls GET "$TOOLB_SECRET_URL" "" "-H 'Authorization: Bearer ${agent_token}'")"
  log "C4 agent-a token use status: $status body=$(run_in "$AGENT_CONTAINER" 'cat /tmp/rt_body')"
  if [ -n "$agent_exp" ]; then
    now="$(date +%s)"
    wait_seconds=$((agent_exp - now + 1))
    if [ "$wait_seconds" -gt 0 ]; then
      sleep "$wait_seconds"
    fi
    status="$(agent_curl_tls GET "$TOOLB_SECRET_URL" "" "-H 'Authorization: Bearer ${agent_token}'")"
    log "C5 expired token status: $status body=$(run_in "$AGENT_CONTAINER" 'cat /tmp/rt_body')"
  fi
fi

log ""
log "D. Header spoof attempts"
status="$(rogue_curl_tls GET "$TOOLB_SECRET_URL" "" "-H 'x-spiffe-id: spiffe://example.org/agent-a'")"
log "D1 spoofed x-spiffe-id status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"
status="$(rogue_curl_tls GET "$TOOLB_SECRET_URL" "" "-H 'x-spiffe-id: spiffe://example.org/agent-a' -H 'X-SPIFFE-ID: spiffe://example.org/agent-a'")"
log "D2 header case variants status: $status body=$(run_in "$ROGUE_CONTAINER" 'cat /tmp/rt_body')"

log ""
log "Red-team run complete."
