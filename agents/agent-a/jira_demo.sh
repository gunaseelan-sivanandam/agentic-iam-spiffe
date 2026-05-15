#!/bin/sh
set -eu

SPIRE_SOCKET="${SPIRE_AGENT_SOCKET:-/run/spire/agent/private/api.sock}"
SVID_DIR="${SPIRE_SVID_DIR:-/run/spire/svid}"
CAPISS_URL="${CAPABILITY_ISSUER_URL:-https://capability-issuer-envoy:9443}"
JIRA_URL="${JIRA_TOOL_URL:-https://jira-tool-envoy:10443}"
CAPISS_EXPECTED_SPIFFE_ID="${CAPABILITY_ISSUER_SPIFFE_ID:-spiffe://example.org/capability-issuer-envoy}"
JIRA_EXPECTED_SPIFFE_ID="${JIRA_TOOL_SPIFFE_ID:-spiffe://example.org/jira-tool-envoy}"
JIRA_ALLOWED_ISSUE="${JIRA_ALLOWED_ISSUE:-IAM-1}"
JIRA_NON_ALLOWED_ISSUE="${JIRA_NON_ALLOWED_ISSUE:-NAS-1}"
JIRA_ALLOWED_PROJECT="${JIRA_ALLOWED_PROJECT:-${JIRA_ALLOWED_ISSUE%%-*}}"
JIRA_NON_ALLOWED_PROJECT="${JIRA_NON_ALLOWED_PROJECT:-${JIRA_NON_ALLOWED_ISSUE%%-*}}"

mkdir -p "$SVID_DIR"
while [ ! -S "$SPIRE_SOCKET" ]; do
  sleep 0.5
done

for i in $(seq 1 40); do
  if /opt/spire/bin/spire-agent api fetch x509 -socketPath "$SPIRE_SOCKET" -write "$SVID_DIR" >/dev/null 2>/tmp/spire_fetch.err; then
    break
  fi
  sleep 0.5
done

if [ -f "$SVID_DIR/svid.0.pem" ] && [ -f "$SVID_DIR/svid.0.key" ] && [ -f "$SVID_DIR/bundle.0.pem" ]; then
  ln -sf "$SVID_DIR/svid.0.pem" "$SVID_DIR/svid.pem"
  ln -sf "$SVID_DIR/svid.0.key" "$SVID_DIR/svid.key"
  ln -sf "$SVID_DIR/bundle.0.pem" "$SVID_DIR/bundle.pem"
fi

json_string() {
  key="$1"
  file="$2"
  tr -d '\n' <"$file" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"
}

json_reason() {
  json_string "reason" "$1"
}

verified_https_request() {
  url="$1"
  expected_spiffe_id="$2"
  method="$3"
  body="$4"
  bearer="$5"

  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\([^/:]*\).*#\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\([0-9]*\).*#\1#p')"
  path="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/]*\(/.*\)$#\1#p')"
  [ -n "$port" ] || port="443"
  [ -n "$path" ] || path="/"

  tmpdir="$(mktemp -d)"
  req_file="$tmpdir/request.txt"
  body_file="$tmpdir/body.txt"
  http_file="$tmpdir/http.txt"
  diag_file="$tmpdir/diag.txt"
  cert_file="$tmpdir/server.pem"
  response_file="$tmpdir/response_body.txt"

  if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
    printf '%s' "$body" >"$body_file"
  else
    : >"$body_file"
  fi
  body_len="$(wc -c <"$body_file" | tr -d ' ')"

  {
    printf '%s %s HTTP/1.1\r\n' "$method" "$path"
    printf 'Host: %s\r\n' "$host"
    printf 'Connection: close\r\n'
    if [ -n "$bearer" ]; then
      printf 'Authorization: Bearer %s\r\n' "$bearer"
    fi
    if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
      printf 'Content-Type: application/json\r\n'
      printf 'Content-Length: %s\r\n' "$body_len"
    fi
    printf '\r\n'
    if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
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
  if ! awk 'BEGIN{p=0} /BEGIN CERTIFICATE/{p=1} p{print} /END CERTIFICATE/{exit}' "$http_file" >"$cert_file" 2>/dev/null || [ ! -s "$cert_file" ]; then
    awk 'BEGIN{p=0} /BEGIN CERTIFICATE/{p=1} p{print} /END CERTIFICATE/{exit}' "$diag_file" >"$cert_file" 2>/dev/null || true
  fi
  if [ -s "$cert_file" ]; then
    actual_spiffe_id="$(openssl x509 -in "$cert_file" -noout -ext subjectAltName 2>/dev/null | sed -n 's/.*URI:\(spiffe:[^,]*\).*/\1/p' | head -n 1)"
  fi
  verify_marker=0
  if grep -Eq 'Verification: OK|Verify return code: 0 \(ok\)' "$diag_file" "$http_file" 2>/dev/null; then
    verify_marker=1
  fi

  if [ "$rc" -ne 0 ] || { [ "$verify_marker" -ne 1 ] && [ "$rc" -ne 0 ]; } || [ "$actual_spiffe_id" != "$expected_spiffe_id" ]; then
    echo "ERROR: verified request failed for $host" >&2
    echo "ERROR: rc=$rc actual_spiffe_id=${actual_spiffe_id:-missing} expected_spiffe_id=$expected_spiffe_id" >&2
    grep -E 'Verification:|Verify return code:' "$diag_file" "$http_file" >&2 || true
    exit 1
  fi

  VERIFIED_HTTP_STATUS="$(tr -d '\r' <"$http_file" | awk '/^HTTP\//{print $2; exit}')"
  tr -d '\r' <"$http_file" | awk '
    BEGIN {http=0; body=0}
    /^HTTP\// {http=1; next}
    http && body==0 && /^$/ {body=1; next}
    http && body==1 {print}
  ' >"$response_file"
  VERIFIED_HTTP_BODY_FILE="$response_file"
}

iam_mint_body="{\"aud\":\"jira-tool\",\"act\":\"read\",\"res\":\"jira-tool:/project:${JIRA_ALLOWED_PROJECT}\"}"
iam_write_mint_body="{\"aud\":\"jira-tool\",\"act\":\"write\",\"res\":\"jira-tool:/project:${JIRA_ALLOWED_PROJECT}\"}"
nas_mint_body="{\"aud\":\"jira-tool\",\"act\":\"read\",\"res\":\"jira-tool:/project:${JIRA_NON_ALLOWED_PROJECT}\"}"
nas_write_mint_body="{\"aud\":\"jira-tool\",\"act\":\"write\",\"res\":\"jira-tool:/project:${JIRA_NON_ALLOWED_PROJECT}\"}"

verified_https_request "$CAPISS_URL/capabilities/root-mint" "$CAPISS_EXPECTED_SPIFFE_ID" POST "$iam_mint_body" ""
iam_body="$VERIFIED_HTTP_BODY_FILE"
iam_status="$VERIFIED_HTTP_STATUS"
iam_token="$(json_string token "$iam_body")"
iam_root="$(json_string root_token_id "$iam_body")"
iam_token_id="$(json_string token_id "$iam_body")"
echo "jira mint project=$JIRA_ALLOWED_PROJECT act=read status=$iam_status root_token_id=$iam_root token_id=$iam_token_id"

verified_https_request "$CAPISS_URL/capabilities/root-mint" "$CAPISS_EXPECTED_SPIFFE_ID" POST "$iam_write_mint_body" ""
iam_write_body="$VERIFIED_HTTP_BODY_FILE"
iam_write_status="$VERIFIED_HTTP_STATUS"
iam_write_token="$(json_string token "$iam_write_body")"
iam_write_root="$(json_string root_token_id "$iam_write_body")"
iam_write_token_id="$(json_string token_id "$iam_write_body")"
echo "jira mint project=$JIRA_ALLOWED_PROJECT act=write status=$iam_write_status root_token_id=$iam_write_root token_id=$iam_write_token_id"

verified_https_request "$JIRA_URL/jira/rest/api/3/issue/$JIRA_ALLOWED_ISSUE" "$JIRA_EXPECTED_SPIFFE_ID" GET "" "$iam_token"
iam_read_body="$VERIFIED_HTTP_BODY_FILE"
iam_read_status="$VERIFIED_HTTP_STATUS"
iam_read_project=""
if [ "$iam_read_status" = "200" ]; then
  iam_read_project="$JIRA_ALLOWED_PROJECT"
fi
echo "jira read issue=$JIRA_ALLOWED_ISSUE status=$iam_read_status project=$iam_read_project"

marker="$(date -u '+%d.%m.%y %H.%M.%S UTC - Description updated by SPIRE service jira-tool')"
write_body="$(printf '%s' "$marker" | sed 's/\\/\\\\/g; s/"/\\"/g' | sed 's/.*/{"description":"&"}/')"

verified_https_request "$JIRA_URL/jira/rest/api/3/issue/$JIRA_ALLOWED_ISSUE" "$JIRA_EXPECTED_SPIFFE_ID" PUT "$write_body" "$iam_token"
read_token_write_body="$VERIFIED_HTTP_BODY_FILE"
read_token_write_status="$VERIFIED_HTTP_STATUS"
read_token_write_reason="$(json_reason "$read_token_write_body")"
echo "jira write issue=$JIRA_ALLOWED_ISSUE act=read-token status=$read_token_write_status reason=$read_token_write_reason"

verified_https_request "$JIRA_URL/jira/rest/api/3/issue/$JIRA_ALLOWED_ISSUE" "$JIRA_EXPECTED_SPIFFE_ID" PUT "$write_body" "$iam_write_token"
iam_write_response_body="$VERIFIED_HTTP_BODY_FILE"
iam_write_response_status="$VERIFIED_HTTP_STATUS"
echo "jira write issue=$JIRA_ALLOWED_ISSUE act=write status=$iam_write_response_status project=$JIRA_ALLOWED_PROJECT"

verified_https_request "$JIRA_URL/jira/rest/api/3/issue/$JIRA_ALLOWED_ISSUE" "$JIRA_EXPECTED_SPIFFE_ID" GET "" "$iam_write_token"
iam_write_readback_body="$VERIFIED_HTTP_BODY_FILE"
iam_write_readback_status="$VERIFIED_HTTP_STATUS"
if grep -Fq "$marker" "$iam_write_readback_body"; then
  marker_match="matched"
else
  marker_match="not_matched"
fi
echo "jira readback issue=$JIRA_ALLOWED_ISSUE status=$iam_write_readback_status marker=$marker_match"

verified_https_request "$CAPISS_URL/capabilities/root-mint" "$CAPISS_EXPECTED_SPIFFE_ID" POST "$nas_mint_body" ""
nas_mint_body_file="$VERIFIED_HTTP_BODY_FILE"
nas_mint_status="$VERIFIED_HTTP_STATUS"
nas_reason="$(json_reason "$nas_mint_body_file")"
echo "jira mint project=$JIRA_NON_ALLOWED_PROJECT act=read status=$nas_mint_status reason=$nas_reason"

verified_https_request "$CAPISS_URL/capabilities/root-mint" "$CAPISS_EXPECTED_SPIFFE_ID" POST "$nas_write_mint_body" ""
nas_write_mint_body_file="$VERIFIED_HTTP_BODY_FILE"
nas_write_mint_status="$VERIFIED_HTTP_STATUS"
nas_write_reason="$(json_reason "$nas_write_mint_body_file")"
echo "jira mint project=$JIRA_NON_ALLOWED_PROJECT act=write status=$nas_write_mint_status reason=$nas_write_reason"

verified_https_request "$JIRA_URL/jira/rest/api/3/issue/$JIRA_NON_ALLOWED_ISSUE" "$JIRA_EXPECTED_SPIFFE_ID" GET "" "$iam_token"
nas_read_body="$VERIFIED_HTTP_BODY_FILE"
nas_read_status="$VERIFIED_HTTP_STATUS"
nas_read_reason="$(json_reason "$nas_read_body")"
echo "jira read issue=$JIRA_NON_ALLOWED_ISSUE status=$nas_read_status reason=$nas_read_reason"

verified_https_request "$JIRA_URL/jira/rest/api/3/issue/$JIRA_NON_ALLOWED_ISSUE" "$JIRA_EXPECTED_SPIFFE_ID" PUT "$write_body" "$iam_write_token"
nas_write_body="$VERIFIED_HTTP_BODY_FILE"
nas_write_status="$VERIFIED_HTTP_STATUS"
nas_write_use_reason="$(json_reason "$nas_write_body")"
echo "jira write issue=$JIRA_NON_ALLOWED_ISSUE act=write status=$nas_write_status reason=$nas_write_use_reason"
