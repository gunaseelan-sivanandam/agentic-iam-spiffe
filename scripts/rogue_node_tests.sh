#!/bin/sh
set -eu

GREEN='\033[32m'
RED='\033[31m'
RESET='\033[0m'

LOG_FILE="${TEST_LOG_FILE:-/repo/test_report.log}"
LOG_PIPE="/tmp/rogue_test_log.pipe"

mkdir -p "$(dirname "$LOG_FILE")"
: > "$LOG_FILE"
date '+Test run started: %Y-%m-%dT%H:%M:%S%z (%Z)' >> "$LOG_FILE"
rm -f "$LOG_PIPE"
mkfifo "$LOG_PIPE"
tee -a "$LOG_FILE" <"$LOG_PIPE" &
TEE_PID=$!
exec >"$LOG_PIPE" 2>&1
trap 'rm -f "$LOG_PIPE"; kill "$TEE_PID" >/dev/null 2>&1 || true' EXIT

TOTAL=0
PASSED=0
FAILED=0
FAIL_REASON=""

TIMEOUT_BIN="timeout"
if ! command -v timeout >/dev/null 2>&1; then
  if command -v busybox >/dev/null 2>&1; then
    TIMEOUT_BIN="busybox timeout"
  else
    echo "timeout command not available"
    exit 1
  fi
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq command not available"
  exit 1
fi

TLS_CLIENT_ARGS="-tls1_2"

print_result() {
  id="$1"
  name="$2"
  status="$3"
  color="$4"
  printf '[%s] %-48s .... %b%s%b\n' "$id" "$name" "$color" "$status" "$RESET"
}

print_section() {
  title="$1"
  printf '\n%s\n' "$title"
}

run_test() {
  id="$1"
  name="$2"
  shift 2
  TOTAL=$((TOTAL + 1))
  FAIL_REASON=""
  if "$@"; then
    PASSED=$((PASSED + 1))
    print_result "$id" "$name" "PASS" "$GREEN"
  else
    FAILED=$((FAILED + 1))
    print_result "$id" "$name" "FAIL" "$RED"
    if [ -n "$FAIL_REASON" ]; then
      printf '  Reason: %s\n' "$FAIL_REASON"
    fi
  fi
}

set_reason() {
  FAIL_REASON="$1"
}

json_get() {
  key="$1"
  file="$2"
  jq -r "$key" "$file" 2>/dev/null
}

fail_simple() {
  set_reason "$1"
  return 1
}

is_json_file() {
  jq -e . "$1" >/dev/null 2>&1
}

fail_with_body() {
  msg="$1"
  file="$2"
  body="$(cat "$file" 2>/dev/null || true)"
  set_reason "${msg} body=${body}"
  return 1
}

wait_dns() {
  host="$1"
  timeout="${2:-30}"
  start="$(date +%s)"
  echo "[gate] DNS check ${host}"
  while true; do
    if command -v getent >/dev/null 2>&1; then
      if getent hosts "$host" >/dev/null 2>&1; then
        echo "[gate] DNS OK ${host}"
        return 0
      fi
    elif command -v nslookup >/dev/null 2>&1; then
      if nslookup "$host" >/dev/null 2>&1; then
        echo "[gate] DNS OK ${host}"
        return 0
      fi
    elif command -v ping >/dev/null 2>&1; then
      if ping -c1 -W1 "$host" >/dev/null 2>&1; then
        echo "[gate] DNS OK ${host}"
        return 0
      fi
    fi
    now="$(date +%s)"
    if [ $((now - start)) -ge "$timeout" ]; then
      set_reason "DNS did not resolve ${host} in ${timeout}s"
      return 1
    fi
    sleep 0.3
  done
}

wait_tcp() {
  host="$1"
  port="$2"
  timeout="${3:-30}"
  start="$(date +%s)"
  last_out=""
  echo "[gate] TCP check ${host}:${port}"
  while true; do
    if command -v nc >/dev/null 2>&1; then
      if nc -z -w1 "$host" "$port" >/dev/null 2>&1; then
        echo "[gate] TCP OK ${host}:${port}"
        return 0
      fi
    else
      last_out="$(timeout 2s openssl s_client -connect "${host}:${port}" -servername "$host" < /dev/null 2>&1 || true)"
      if printf '%s' "$last_out" | grep -Fq "CONNECTED"; then
        echo "[gate] TCP OK ${host}:${port}"
        return 0
      fi
    fi
    now="$(date +%s)"
    if [ $((now - start)) -ge "$timeout" ]; then
      set_reason "TCP not reachable ${host}:${port} in ${timeout}s: ${last_out:-none}"
      return 1
    fi
    sleep 0.3
  done
}

wait_http_ready() {
  url="$1"
  curl_args="$2"
  timeout="${3:-30}"
  start="$(date +%s)"
  err_file="/tmp/http_ready.err"
  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\\([^/:]*\\).*#\\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\\([0-9]*\\).*#\\1#p')"
  if [ -z "$port" ]; then
    case "$url" in
      https://*) port="443" ;;
      http://*) port="80" ;;
    esac
  fi
  resolved_ip=""
  if [ -n "$host" ] && command -v getent >/dev/null 2>&1; then
    resolved_ip="$(getent hosts "$host" | awk 'NR==1{print $1}')"
  fi
  echo "[gate] HTTP check ${url}"
  while true; do
    : >"$err_file"
    if [ -n "$resolved_ip" ] && [ -n "$port" ]; then
      status="$(sh -c "curl -sS ${curl_args} --max-time 2 --resolve ${host}:${port}:${resolved_ip} -o /dev/null -w '%{http_code}' '${url}'" 2>"$err_file" || true)"
    else
      status="$(sh -c "curl -sS ${curl_args} --max-time 2 -o /dev/null -w '%{http_code}' '${url}'" 2>"$err_file" || true)"
    fi
    if [ -n "$status" ] && [ "$status" != "000" ]; then
      echo "[gate] HTTP OK ${url}"
      return 0
    fi
    now="$(date +%s)"
    if [ $((now - start)) -ge "$timeout" ]; then
      set_reason "No HTTP response from ${url} in ${timeout}s: $(cat "$err_file" 2>/dev/null || true)"
      return 1
    fi
    sleep 0.3
  done
}

resolve_host_ip() {
  host="$1"
  if command -v getent >/dev/null 2>&1; then
    ip="$(getent hosts "$host" | awk '$1 ~ /^[0-9.]+$/{print $1; exit}')"
    if [ -n "$ip" ]; then
      printf '%s\n' "$ip"
      return 0
    fi
  fi
  if command -v nslookup >/dev/null 2>&1; then
    ip="$(nslookup "$host" 2>/dev/null | awk '/^Address: / && $2 ~ /^[0-9.]+$/{print $2; exit}')"
    if [ -n "$ip" ]; then
      printf '%s\n' "$ip"
      return 0
    fi
  fi
  if command -v ping >/dev/null 2>&1; then
    ip="$(ping -c1 -W1 "$host" 2>/dev/null | sed -n 's/.*(\\([0-9.]*\\)).*/\\1/p')"
    if [ -n "$ip" ]; then
      printf '%s\n' "$ip"
      return 0
    fi
  fi
  if command -v docker >/dev/null 2>&1; then
    case "$host" in
      tool-b-envoy)
        container="spiffe-tool-b-envoy"
        network_suffix="toolb_edge_net"
        ;;
      capability-issuer-envoy)
        container="spiffe-capability-issuer-envoy"
        network_suffix="capiss_edge_net"
        ;;
      capability-issuer-no-opa-envoy)
        container="spiffe-capability-issuer-no-opa-envoy"
        network_suffix="capiss_edge_net"
        ;;
      *)
        container=""
        network_suffix=""
        ;;
    esac
    if [ -n "$container" ]; then
      net_dump="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{println $k " " $v.IPAddress}}{{end}}' "$container" 2>/dev/null || true)"
      if [ -n "$network_suffix" ]; then
        ip="$(printf '%s\n' "$net_dump" | awk -v suf="$network_suffix" '$1 ~ suf "$" {print $2; exit}')"
      else
        ip="$(printf '%s\n' "$net_dump" | awk 'NF>=2{print $2; exit}')"
      fi
      if [ -n "$ip" ]; then
        printf '%s\n' "$ip"
        return 0
      fi
    fi
  fi
  return 1
}

resolve_ip_for_host() {
  host="$1"
  i=0
  while [ $i -lt 10 ]; do
    ip=""
    if command -v getent >/dev/null 2>&1; then
      ip="$(getent hosts "$host" | awk 'NR==1{print $1}')"
    fi
    if [ -z "$ip" ] && command -v docker >/dev/null 2>&1; then
      net_dump="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{println $k " " $v.IPAddress}}{{end}}' "spiffe-${host}" 2>/dev/null || true)"
      ip="$(printf '%s\n' "$net_dump" | awk 'NF>=2{print $2; exit}')"
    fi
    if [ -n "$ip" ]; then
      printf '%s\n' "$ip"
      return 0
    fi
    i=$((i + 1))
    sleep 0.2
  done
  return 1
}

resolve_arg_for_url() {
  url="$1"
  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\\([^/:]*\\).*#\\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\\([0-9]*\\).*#\\1#p')"
  if [ -z "$port" ]; then
    case "$url" in
      https://*) port="443" ;;
      http://*) port="80" ;;
    esac
  fi
  if [ -n "$host" ] && [ -n "$port" ]; then
    ip="$(resolve_ip_for_host "$host" || true)"
    if [ -n "$ip" ]; then
      printf -- "--resolve %s:%s:%s" "$host" "$port" "$ip"
      return 0
    fi
  fi
  return 1
}

assert_json_eq() {
  file="$1"
  jq_expr="$2"
  expected="$3"
  actual="$(jq -r "$jq_expr" "$file" 2>/dev/null || printf "__JQ_ERROR__")"
  if [ "$actual" = "__JQ_ERROR__" ]; then
    fail_with_body "failed to parse json for $jq_expr" "$file"
    return 1
  fi
  if [ "$actual" != "$expected" ]; then
    fail_with_body "expected $jq_expr=$expected got $actual" "$file"
    return 1
  fi
  return 0
}

assert_json_present() {
  file="$1"
  jq_expr="$2"
  if ! jq -e "$jq_expr != null" "$file" >/dev/null 2>&1; then
    fail_with_body "missing $jq_expr" "$file"
    return 1
  fi
  if jq -e "$jq_expr | type == \"string\"" "$file" >/dev/null 2>&1; then
    if ! jq -e "$jq_expr | length > 0" "$file" >/dev/null 2>&1; then
      fail_with_body "empty $jq_expr" "$file"
      return 1
    fi
  fi
  return 0
}

assert_text_contains() {
  file="$1"
  pattern="$2"
  if ! grep -Fq "$pattern" "$file"; then
    fail_with_body "expected text to contain: $pattern" "$file"
    return 1
  fi
  return 0
}

assert_text_matches() {
  file="$1"
  regex="$2"
  if ! grep -Eq "$regex" "$file"; then
    fail_with_body "expected text to match: $regex" "$file"
    return 1
  fi
  return 0
}

text_contains() {
  file="$1"
  pattern="$2"
  grep -Fq "$pattern" "$file"
}

text_contains_str() {
  text="$1"
  pattern="$2"
  printf '%s' "$text" | grep -Fq "$pattern"
}

assert_contains_json_or_text() {
  file="$1"
  jq_check="$2"
  text_pattern="$3"
  if is_json_file "$file"; then
    if ! jq -e "$jq_check" "$file" >/dev/null 2>&1; then
      fail_with_body "JSON check failed: $jq_check" "$file"
      return 1
    fi
  else
    if ! assert_text_contains "$file" "$text_pattern"; then
      return 1
    fi
  fi
  return 0
}

extract_http_status() {
  file="$1"
  code=""
  while IFS= read -r line; do
    line="$(printf '%s' "$line" | tr -d '\r')"
    case "$line" in
      HTTP/*)
        set -- $line
        code="$2"
        break
        ;;
    esac
  done <"$file"
  if [ -z "$code" ]; then
    fail_with_body "no HTTP status line found" "$file"
    return 1
  fi
  printf '%s' "$code"
}

assert_http_code() {
  actual="$1"
  expected="$2"
  ctx="$3"
  case "$expected" in
    *"|"*)
      if ! printf '%s' "$actual" | grep -Eq "^(${expected})$"; then
        fail_simple "${ctx}: expected HTTP ${expected} got ${actual:-none}"
        return 1
      fi
      ;;
    *)
      if [ "$actual" != "$expected" ]; then
        fail_simple "${ctx}: expected HTTP ${expected} got ${actual:-none}"
        return 1
      fi
      ;;
  esac
  return 0
}

container_running() {
  container_name="$1"
  docker ps --format '{{.Names}}' | grep -Fxq "$container_name"
}

wait_for_legit_attestation() {
  i=0
  while [ $i -lt 60 ]; do
    out="/tmp/spire_agent_list.json"
    if docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list \
      -socketPath /run/spire/server/data/private/api.sock -output json >"$out" 2>/dev/null; then
      if assert_contains_json_or_text "$out" \
        '.agents and (.agents|type=="array") and (.agents|length>0)' \
        '"agents"'; then
        return 0
      fi
    fi
    i=$((i + 1))
    sleep 1
  done
  return 1
}

wait_for_agent_socket() {
  i=0
  while [ $i -lt 60 ]; do
    if docker exec spiffe-spire-agent test -S /run/spire/agent/private/api.sock 2>/dev/null; then
      return 0
    fi
    i=$((i + 1))
    sleep 1
  done
  return 1
}

run_rogue_attest_should_fail() {
  label="$1"
  token="$2"
  log_file="/tmp/rogue_${label}.log"
  temp_dir="/tmp/rogue_${label}"
  temp_config="/tmp/rogue_${label}.conf"

  rm -f "$log_file"
  mkdir -p "$temp_dir"
  sed "s#/run/spire/rogue#${temp_dir}#g" /run/spire/rogue/agent.conf > "$temp_config"

  set +e
  $TIMEOUT_BIN 6s /opt/spire/bin/spire-agent run -config "$temp_config" -joinToken "$token" \
    >"$log_file" 2>&1
  rc=$?
  set -e

  if text_contains "$log_file" "Node attestation was successful"; then
    set_reason "rogue attestation succeeded"
    return 1
  fi

  if [ $rc -eq 0 ]; then
    set_reason "rogue agent exited 0"
    return 1
  fi

  return 0
}

prepare_toolb_material() {
  tmpdir="$1"
  cert="$tmpdir/toolb_svid.pem"
  key="$tmpdir/toolb_svid.key"
  bundle="$tmpdir/toolb_bundle.pem"

  i=0
  while [ $i -lt 60 ]; do
    if docker exec spiffe-tool-b-envoy test -s /run/spire/svid/svid.pem 2>/dev/null; then
      break
    fi
    i=$((i + 1))
    sleep 1
  done

  if ! docker exec spiffe-tool-b-envoy test -s /run/spire/svid/svid.pem 2>/dev/null; then
    set_reason "tool-b-envoy SVID not available"
    return 1
  fi

  docker exec spiffe-tool-b-envoy cat /run/spire/svid/svid.pem >"$cert"
  docker exec spiffe-tool-b-envoy cat /run/spire/svid/svid.key >"$key"
  docker exec spiffe-tool-b-envoy cat /run/spire/svid/bundle.pem >"$bundle"

  if [ ! -s "$cert" ] || [ ! -s "$key" ] || [ ! -s "$bundle" ]; then
    set_reason "failed to copy tool-b-envoy cert material"
    return 1
  fi

  TOOLB_CERT="$cert"
  TOOLB_KEY="$key"
  TOOLB_BUNDLE="$bundle"
  return 0
}

capture_entries() {
  out_file="$1"
  docker exec spiffe-spire-server /opt/spire/bin/spire-server entry show \
    -socketPath /run/spire/server/data/private/api.sock -output json 2>/dev/null | \
    grep -o '"id":"[^"]*"' | sed 's/"id":"//; s/"$//' | sort >"$out_file"
}

PRECHECK_OK=1
PRECHECK_REASON=""
if ! container_running "spiffe-spire-server"; then
  PRECHECK_OK=0
  PRECHECK_REASON="spire-server container not running"
elif ! container_running "spiffe-spire-agent"; then
  PRECHECK_OK=0
  PRECHECK_REASON="spire-agent container not running"
elif ! wait_for_legit_attestation; then
  PRECHECK_OK=0
  PRECHECK_REASON="legitimate agent did not attest"
elif ! wait_for_agent_socket; then
  PRECHECK_OK=0
  PRECHECK_REASON="spire agent workload socket not ready"
elif [ ! -s /run/spire/shared/join_token ]; then
  PRECHECK_OK=0
  PRECHECK_REASON="join token missing"
fi

ENTRY_BEFORE="/tmp/entries_before.txt"
if [ $PRECHECK_OK -eq 1 ]; then
  capture_entries "$ENTRY_BEFORE" || true
fi

TOOLB_READY=0
TOOLB_REASON=""
CAPISS_READY=0
CAPISS_REASON=""
CAPISS_AGENT_CERT=""
CAPISS_AGENT_KEY=""
CAPISS_ROGUE_CERT=""
CAPISS_ROGUE_KEY=""
CAPISS_MINT_URL="https://capability-issuer-envoy:9443/capabilities/mint"
CAPISS_NO_OPA_URL="https://capability-issuer-no-opa-envoy:9444/capabilities/mint"
TOOLB_SECRET_URL="https://tool-b-envoy:8443/secret"
CAPISS_MINT_BODY='{"aud":"tool-b","act":"read","res":"/secret"}'

ensure_toolb_material() {
  if [ "$TOOLB_READY" -eq 1 ]; then
    return 0
  fi
  if [ "$TOOLB_READY" -eq -1 ]; then
    set_reason "$TOOLB_REASON"
    return 1
  fi
  tmpdir="/tmp/toolb_material"
  rm -rf "$tmpdir"
  mkdir -p "$tmpdir"
  if ! prepare_toolb_material "$tmpdir"; then
    TOOLB_READY=-1
    TOOLB_REASON="$FAIL_REASON"
    set_reason "$FAIL_REASON"
    return 1
  fi
  TOOLB_READY=1
  return 0
}

prepare_client_material() {
  service_name="$1"
  tmpdir="$2"
  outdir="/repo/tmp_svid/${service_name}_out"
  cert="$tmpdir/${service_name}_svid.pem"
  key="$tmpdir/${service_name}_svid.key"
  host_repo="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/repo"}}{{.Source}}{{end}}{{end}}' spiffe-rogue-tests 2>/dev/null || true)"
  if [ -z "$host_repo" ]; then
    host_repo="$(awk '$5=="/repo"{print $4; exit}' /proc/self/mountinfo 2>/dev/null || true)"
  fi

  rm -rf "$outdir"
  mkdir -p "$outdir"

  if [ -z "$host_repo" ]; then
    set_reason "failed to resolve host repo path"
    return 1
  fi

  err_log="/tmp/${service_name}_svid_fetch.err"
  i=0
  while [ $i -lt 60 ]; do
    if docker run --rm \
      --entrypoint /opt/spire/bin/spire-agent \
      -v "$host_repo/spire/agent":/run/spire/agent:ro \
      -v "$host_repo":/repo \
      -l "com.docker.compose.service=${service_name}" \
      ghcr.io/spiffe/spire-agent:1.9.0 \
      api fetch x509 -socketPath /run/spire/agent/private/api.sock -write "$outdir" \
      >"$err_log" 2>&1; then
      break
    fi
    i=$((i + 1))
    sleep 1
  done
  if [ $i -ge 60 ]; then
    set_reason "failed to fetch SVID for ${service_name}: $(tail -n 2 "$err_log" 2>/dev/null | tr '\n' ' ')"
    return 1
  fi

  if [ ! -s "$outdir/svid.0.pem" ] || [ ! -s "$outdir/svid.0.key" ]; then
    set_reason "missing SVID material for ${service_name}"
    return 1
  fi

  cp "$outdir/svid.0.pem" "$cert"
  cp "$outdir/svid.0.key" "$key"

  CLIENT_CERT="$cert"
  CLIENT_KEY="$key"
  return 0
}

ensure_capiss_material() {
  if [ "$CAPISS_READY" -eq 1 ]; then
    return 0
  fi
  if [ "$CAPISS_READY" -eq -1 ]; then
    set_reason "$CAPISS_REASON"
    return 1
  fi

  tmpdir="/tmp/capiss_material"
  rm -rf "$tmpdir"
  mkdir -p "$tmpdir"

  if ! prepare_client_material "agent-a" "$tmpdir"; then
    CAPISS_READY=-1
    CAPISS_REASON="$FAIL_REASON"
    set_reason "$FAIL_REASON"
    return 1
  fi
  CAPISS_AGENT_CERT="$CLIENT_CERT"
  CAPISS_AGENT_KEY="$CLIENT_KEY"

  if ! prepare_client_material "rogue" "$tmpdir"; then
    CAPISS_READY=-1
    CAPISS_REASON="$FAIL_REASON"
    set_reason "$FAIL_REASON"
    return 1
  fi
  CAPISS_ROGUE_CERT="$CLIENT_CERT"
  CAPISS_ROGUE_KEY="$CLIENT_KEY"

  CAPISS_READY=1
  return 0
}

ensure_toolb_envoy_ready() {
  if ! wait_dns "tool-b-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "tool-b-envoy" "8443" 30; then
    return 1
  fi
  TOOLB_ENVOY_IP="$(resolve_host_ip "tool-b-envoy")"
  return 0
}

ensure_capiss_envoy_ready() {
  if ! wait_dns "capability-issuer-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "capability-issuer-envoy" "9443" 30; then
    return 1
  fi
  CAPISS_ENVOY_IP="$(resolve_host_ip "capability-issuer-envoy")"
  return 0
}

mint_with_cert() {
  cert="$1"
  key="$2"
  url="$3"
  out="$4"
  : >"$out"
  resolve_arg="$(resolve_arg_for_url "$url" || true)"
  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\\([^/:]*\\).*#\\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\\([0-9]*\\).*#\\1#p')"
  ip="$(resolve_ip_for_host "$host" || true)"
  curl_url="$url"
  host_header=""
  if [ -n "$ip" ] && [ -n "$port" ]; then
    curl_url="$(printf '%s' "$url" | sed "s#^\\(https\\?://\\)[^/]*#\\1${ip}:${port}#")"
    host_header="-H Host: ${host}"
  fi
  status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
    $host_header -H "Content-Type: application/json" -d "$CAPISS_MINT_BODY" "$curl_url" || true)"
  printf '%s' "$status"
}

mint_with_body() {
  cert="$1"
  key="$2"
  url="$3"
  body="$4"
  out="$5"
  : >"$out"
  resolve_arg="$(resolve_arg_for_url "$url" || true)"
  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\\([^/:]*\\).*#\\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\\([0-9]*\\).*#\\1#p')"
  ip="$(resolve_ip_for_host "$host" || true)"
  curl_url="$url"
  host_header=""
  if [ -n "$ip" ] && [ -n "$port" ]; then
    curl_url="$(printf '%s' "$url" | sed "s#^\\(https\\?://\\)[^/]*#\\1${ip}:${port}#")"
    host_header="-H Host: ${host}"
  fi
  status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
    $host_header -H "Content-Type: application/json" -d "$body" "$curl_url" || true)"
  printf '%s' "$status"
}

toolb_request() {
  cert="$1"
  key="$2"
  token="$3"
  out="$4"
  : >"$out"
  resolve_arg="$(resolve_arg_for_url "$TOOLB_SECRET_URL" || true)"
  host="$(printf '%s' "$TOOLB_SECRET_URL" | sed -n 's#^[a-zA-Z]*://\\([^/:]*\\).*#\\1#p')"
  port="$(printf '%s' "$TOOLB_SECRET_URL" | sed -n 's#^[a-zA-Z]*://[^/:]*:\\([0-9]*\\).*#\\1#p')"
  ip="$(resolve_ip_for_host "$host" || true)"
  curl_url="$TOOLB_SECRET_URL"
  host_header=""
  if [ -n "$ip" ] && [ -n "$port" ]; then
    curl_url="$(printf '%s' "$TOOLB_SECRET_URL" | sed "s#^\\(https\\?://\\)[^/]*#\\1${ip}:${port}#")"
    host_header="-H Host: ${host}"
  fi
  if [ -n "$token" ]; then
    status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
      --cacert "$TOOLB_BUNDLE" $host_header -H "Authorization: Bearer ${token}" "$curl_url" || true)"
  else
    status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
      --cacert "$TOOLB_BUNDLE" $host_header "$curl_url" || true)"
  fi
  printf '%s' "$status"
}

expect_edge_unreachable() {
  url="$1"
  out="$2"
  set +e
  curl -sS --max-time 2 "$url" >"$out" 2>&1
  rc=$?
  set -e
  if [ $rc -ne 0 ]; then
    return 0
  fi
  return 1
}

# M1-T1
c1_test() {
  if [ $PRECHECK_OK -ne 1 ]; then
    set_reason "$PRECHECK_REASON"
    return 1
  fi
  missing_token="$(cat /run/spire/rogue/missing_token 2>/dev/null || true)"
  run_rogue_attest_should_fail "M1-T1" "$missing_token"
}

# M1-T2
c2_test() {
  if [ $PRECHECK_OK -ne 1 ]; then
    set_reason "$PRECHECK_REASON"
    return 1
  fi
  echo "not-a-real-token" > /run/spire/rogue/fake_token
  run_rogue_attest_should_fail "M1-T2" "$(cat /run/spire/rogue/fake_token)"
}

# M1-T3
c3_test() {
  if [ $PRECHECK_OK -ne 1 ]; then
    set_reason "$PRECHECK_REASON"
    return 1
  fi
  run_rogue_attest_should_fail "M1-T3" "$(cat /run/spire/shared/join_token)"
}

# M1-T4
c4_test() {
  mounts="$(docker inspect -f '{{range .Mounts}}{{.Destination}} {{end}}' spiffe-spire-rogue-agent 2>/dev/null || true)"
  if text_contains_str "$mounts" "/run/spire/shared"; then
    set_reason "shared token mount present"
    return 1
  fi
  set +e
  docker exec spiffe-spire-rogue-agent cat /run/spire/shared/join_token >/tmp/rogue_token_out 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "join token readable by rogue"
    return 1
  fi
  return 0
}

# M1-T5
c5_test() {
  expected_nodes=$(docker ps -q --filter "label=spiffe.node=true" | wc -l | tr -d ' ')
  agents_json=$(docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list \
    -socketPath /run/spire/server/data/private/api.sock -output json 2>/dev/null)
  actual_nodes=$(echo "$agents_json" | grep -o '"id"' | wc -l | tr -d ' ')
  if [ "$expected_nodes" -eq 0 ]; then
    set_reason "no running spiffe.node containers"
    return 1
  fi
  if [ "$actual_nodes" -ne "$expected_nodes" ]; then
    set_reason "expected ${expected_nodes}, got ${actual_nodes}"
    return 1
  fi
  return 0
}

# M2-T1
T1_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  if ! wait_dns "tool-b-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "tool-b-envoy" "8443" 30; then
    return 1
  fi
  out="/tmp/toolb_material/t1.out"
  set +e
  $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -connect tool-b-envoy:8443 -CAfile "$TOOLB_BUNDLE" \
    -verify_return_error < /dev/null >"$out" 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "TLS succeeded without client cert"
    return 1
  fi
  if ! assert_text_matches "$out" '(handshake failure|certificate required|no peer certificate)'; then
    set_reason "TLS failure did not indicate missing client cert: $(cat "$out")"
    return 1
  fi
  return 0
}

# M2-T2
T2_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  if ! wait_dns "tool-b-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "tool-b-envoy" "8443" 30; then
    return 1
  fi
  tmpdir="/tmp/toolb_material"
  openssl req -x509 -newkey rsa:2048 -nodes -keyout "$tmpdir/bad.key" \
    -out "$tmpdir/bad.pem" -days 1 -subj "/CN=rogue" >/dev/null 2>&1
  out="/tmp/toolb_material/t2.out"
  set +e
  $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -connect tool-b-envoy:8443 -cert "$tmpdir/bad.pem" \
    -key "$tmpdir/bad.key" -CAfile "$TOOLB_BUNDLE" -verify_return_error \
    < /dev/null >"$out" 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "TLS succeeded with invalid client cert"
    return 1
  fi
  if ! assert_text_matches "$out" '(unknown ca|bad certificate|certificate unknown)'; then
    set_reason "TLS failure did not indicate invalid client cert: $(cat "$out")"
    return 1
  fi
  return 0
}

# M2-T3
T3_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  if ! wait_dns "tool-b-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "tool-b-envoy" "8443" 30; then
    return 1
  fi
  tmpdir="/tmp/toolb_material"
  ca_dir="$tmpdir/ca"
  rm -rf "$ca_dir"
  mkdir -p "$ca_dir/certs" "$ca_dir/newcerts" "$ca_dir/private"
  : >"$ca_dir/index.txt"
  echo 1000 >"$ca_dir/serial"
  openssl req -x509 -newkey rsa:2048 -nodes -keyout "$ca_dir/private/ca.key" \
    -out "$ca_dir/certs/ca.pem" -days 365 -subj "/CN=toolb-test-ca" >/dev/null 2>&1
  cat >"$ca_dir/ca.conf" <<EOF
[ ca ]
default_ca = CA_default

[ CA_default ]
dir = $ca_dir
database = \$dir/index.txt
new_certs_dir = \$dir/newcerts
certificate = \$dir/certs/ca.pem
private_key = \$dir/private/ca.key
serial = \$dir/serial
default_md = sha256
policy = policy_any
x509_extensions = usr_cert
unique_subject = no

[ policy_any ]
commonName = supplied

[ usr_cert ]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
EOF
  start="20000101000000Z"
  end="20000102000000Z"
  openssl req -newkey rsa:2048 -nodes -keyout "$tmpdir/exp.key" \
    -out "$tmpdir/exp.csr" -subj "/CN=rogue-expired" >/dev/null 2>&1
  if ! openssl ca -batch -config "$ca_dir/ca.conf" -in "$tmpdir/exp.csr" \
    -startdate "$start" -enddate "$end" -out "$tmpdir/exp.pem" >/tmp/exp_ca.log 2>&1; then
    set_reason "failed to sign expired cert: $(cat /tmp/exp_ca.log)"
    return 1
  fi
  if [ ! -s "$tmpdir/exp.pem" ]; then
    set_reason "expired cert not created"
    return 1
  fi
  if ! openssl x509 -noout -enddate -in "$tmpdir/exp.pem" >"$tmpdir/exp_end.txt" 2>/tmp/exp_end.err; then
    set_reason "failed to read expired cert enddate: $(cat /tmp/exp_end.err)"
    return 1
  fi
  if ! assert_text_matches "$tmpdir/exp_end.txt" 'notAfter=.* 2000 GMT$'; then
    set_reason "expired cert enddate not in the past: $(cat "$tmpdir/exp_end.txt")"
    return 1
  fi
  out="/tmp/toolb_material/t3.out"
  set +e
  $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -connect tool-b-envoy:8443 -cert "$tmpdir/exp.pem" \
    -key "$tmpdir/exp.key" -CAfile "$TOOLB_BUNDLE" -verify_return_error \
    < /dev/null >"$out" 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "TLS succeeded with expired client cert"
    return 1
  fi
  if ! assert_text_matches "$out" '(alert unknown ca|unknown ca|unable to get local issuer certificate|verify error:num=20)'; then
    set_reason "TLS failure did not indicate unknown CA: $(cat "$out")"
    return 1
  fi
  return 0
}

# M2-T9
T9_test() {
  if ! ensure_toolb_material; then
    return 1
  fi

  spiffe_id="spiffe://example.org/rogue-socket-shortttl"
  selector="docker:label:com.docker.compose.service:rogue-socket"
  tmpdir="/tmp/toolb_material"
  short_dir="/tmp/short_svid"
  rm -rf "$short_dir"

  existing_id="$(docker exec spiffe-spire-server /opt/spire/bin/spire-server entry show \
    -spiffeID "$spiffe_id" -socketPath /run/spire/server/data/private/api.sock -output json 2>/dev/null | jq -r '.entries[0].id // empty')"
  if [ -n "$existing_id" ]; then
    docker exec spiffe-spire-server /opt/spire/bin/spire-server entry delete \
      -id "$existing_id" -socketPath /run/spire/server/data/private/api.sock >/dev/null 2>&1 || true
  fi

  entry_json="$(docker exec spiffe-spire-server /opt/spire/bin/spire-server entry create \
    -parentID spiffe://example.org/agent/spire-agent \
    -spiffeID "$spiffe_id" \
    -selector "$selector" \
    -x509SVIDTTL 20 \
    -socketPath /run/spire/server/data/private/api.sock \
    -output json 2>/tmp/short_entry.err || true)"
  entry_id="$(echo "$entry_json" | jq -r '.results[0].entry.id // empty')"
  status_code="$(echo "$entry_json" | jq -r '.results[0].status.code // empty')"
  if [ -z "$entry_id" ] && [ "$status_code" = "6" ]; then
    existing_json="$(docker exec spiffe-spire-server /opt/spire/bin/spire-server entry show \
      -spiffeID "$spiffe_id" -socketPath /run/spire/server/data/private/api.sock -output json 2>/dev/null)"
    entry_id="$(echo "$existing_json" | jq -r '.entries[0].id // empty')"
    existing_ttl="$(echo "$existing_json" | jq -r '.entries[0].x509_svid_ttl // empty')"
    if [ -n "$existing_ttl" ] && [ "$existing_ttl" != "20" ]; then
      docker exec spiffe-spire-server /opt/spire/bin/spire-server entry delete \
        -id "$entry_id" -socketPath /run/spire/server/data/private/api.sock >/dev/null 2>&1 || true
      entry_id=""
    fi
  fi
  if [ -z "$entry_id" ]; then
    err_msg="$(cat /tmp/short_entry.err 2>/dev/null || true)"
    set_reason "failed to create short-lived entry: status=${status_code:-none} err=${err_msg:-none}"
    return 1
  fi

  if [ "$status_code" = "6" ] && [ -z "$entry_id" ]; then
    entry_json="$(docker exec spiffe-spire-server /opt/spire/bin/spire-server entry create \
      -parentID spiffe://example.org/agent/spire-agent \
      -spiffeID "$spiffe_id" \
      -selector "$selector" \
      -x509SVIDTTL 20 \
      -socketPath /run/spire/server/data/private/api.sock \
      -output json 2>/tmp/short_entry.err || true)"
    entry_id="$(echo "$entry_json" | jq -r '.results[0].entry.id // empty')"
    status_code="$(echo "$entry_json" | jq -r '.results[0].status.code // empty')"
    if [ -z "$entry_id" ]; then
      err_msg="$(cat /tmp/short_entry.err 2>/dev/null || true)"
      set_reason "failed to recreate short-lived entry: status=${status_code:-none} err=${err_msg:-none}"
      return 1
    fi
  fi

  cleanup_entry() {
    docker exec spiffe-spire-server /opt/spire/bin/spire-server entry delete \
      -id "$entry_id" -socketPath /run/spire/server/data/private/api.sock >/dev/null 2>&1 || true
  }

  mkdir -p "$short_dir"
  docker exec spiffe-rogue-socket mkdir -p "$short_dir"
  fetched=0
  i=0
  while [ $i -lt 30 ]; do
    if docker exec spiffe-rogue-socket /opt/spire/bin/spire-agent api fetch x509 \
      -socketPath /run/spire/agent/private/api.sock -write "$short_dir" >/dev/null 2>/tmp/short_fetch.err; then
      fetched=1
      break
    fi
    i=$((i + 1))
    sleep 1
  done
  if [ "$fetched" -ne 1 ]; then
    err_msg="$(cat /tmp/short_fetch.err 2>/dev/null || true)"
    cleanup_entry
    set_reason "failed to fetch short-lived SVID: ${err_msg:-none}"
    return 1
  fi

  if ! docker exec spiffe-rogue-socket test -s "$short_dir/bundle.pem" 2>/dev/null; then
    if docker exec spiffe-rogue-socket test -s "$short_dir/bundle.0.pem" 2>/dev/null; then
      docker exec spiffe-rogue-socket cp "$short_dir/bundle.0.pem" "$short_dir/bundle.pem" >/dev/null 2>&1 || true
    fi
    if docker exec spiffe-rogue-socket test -s /run/spire/agent/bundle.pem 2>/dev/null; then
      docker exec spiffe-rogue-socket cp /run/spire/agent/bundle.pem "$short_dir/bundle.pem" >/dev/null 2>&1 || true
    fi
  fi
  if ! docker exec spiffe-rogue-socket test -s "$short_dir/bundle.pem" 2>/dev/null; then
    cleanup_entry
    set_reason "missing short-lived bundle.pem"
    return 1
  fi

  end_date="$(docker exec spiffe-rogue-socket openssl x509 -noout -enddate -in "$short_dir/svid.0.pem" | sed 's/notAfter=//')"
  end_epoch="$(docker exec spiffe-rogue-socket date -d "$end_date" +%s 2>/dev/null || true)"
  now_epoch="$(docker exec spiffe-rogue-socket date -u +%s)"
  if [ -z "$end_epoch" ]; then
    cleanup_entry
    set_reason "failed to parse SVID expiry"
    return 1
  fi
  sleep_for=$((end_epoch - now_epoch + 2))
  if [ "$sleep_for" -lt 1 ]; then
    sleep_for=1
  fi
  docker exec spiffe-rogue-socket sleep "$sleep_for"

  docker exec spiffe-rogue-socket cat "$short_dir/svid.0.pem" >"$short_dir/svid.0.pem"
  docker exec spiffe-rogue-socket cat "$short_dir/svid.0.key" >"$short_dir/svid.0.key"
  if docker exec spiffe-rogue-socket test -s "$short_dir/bundle.pem" 2>/dev/null; then
    docker exec spiffe-rogue-socket cat "$short_dir/bundle.pem" >"$short_dir/bundle.pem"
  else
    docker exec spiffe-rogue-socket cat "$short_dir/bundle.0.pem" >"$short_dir/bundle.pem"
  fi

  out="$short_dir/expired.out"
  set +e
  $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -connect tool-b-envoy:8443 -servername tool-b-envoy \
    -cert "$short_dir/svid.0.pem" -key "$short_dir/svid.0.key" \
    -CAfile "$short_dir/bundle.pem" -verify_return_error < /dev/null >"$out" 2>&1
  rc=$?
  set -e
  cleanup_entry

  if [ $rc -eq 0 ]; then
    set_reason "TLS succeeded with expired short-lived SVID"
    return 1
  fi
  if ! assert_text_matches "$out" '(expired|certificate has expired|verify error:num=10|verify return code: 10)'; then
    set_reason "TLS failure did not indicate expiry: $(cat "$out")"
    return 1
  fi
  return 0
}

# M2-T4
T4_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  if ! wait_dns "tool-b-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "tool-b-envoy" "8443" 30; then
    return 1
  fi
  out="/tmp/toolb_material/t4.out"
  set +e
  printf "GET /secret HTTP/1.1\r\nHost: tool-b-envoy\r\nConnection: close\r\n\r\n" | \
    $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -connect tool-b-envoy:8443 -cert "$TOOLB_CERT" \
      -key "$TOOLB_KEY" -CAfile "$TOOLB_BUNDLE" -verify_return_error \
      -showcerts -ign_eof >"$out" 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "TLS succeeded with wrong SPIFFE ID"
    return 1
  fi
  if ! assert_text_matches "$out" '(alert bad certificate|alert certificate unknown|bad certificate|certificate unknown|handshake failure)'; then
    set_reason "TLS failure did not indicate SPIFFE ID mismatch: $(cat "$out")"
    return 1
  fi
  return 0
}

# M2-T5
T5_test() {
  if docker exec spiffe-spire-rogue-agent test -S /run/spire/agent/private/api.sock 2>/dev/null; then
    set_reason "unexpected workload socket present"
    return 1
  fi
  set +e
  docker exec spiffe-spire-rogue-agent /opt/spire/bin/spire-agent api fetch x509 \
    -socketPath /run/spire/agent/private/api.sock -write /tmp/rogue_svid \
    >/tmp/rogue_fetch 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "fetch unexpectedly succeeded"
    return 1
  fi
  if docker exec spiffe-spire-rogue-agent test -e /tmp/rogue_svid/svid.pem 2>/dev/null; then
    set_reason "SVID file created"
    return 1
  fi
  return 0
}

# M2-T6
T6_test() {
  if ! container_running "spiffe-rogue-socket"; then
    set_reason "rogue-socket container not running"
    return 1
  fi
  if ! docker exec spiffe-rogue-socket test -S /run/spire/agent/private/api.sock 2>/dev/null; then
    set_reason "workload socket missing"
    return 1
  fi
  set +e
  docker exec spiffe-rogue-socket /opt/spire/bin/spire-agent api fetch x509 \
    -socketPath /run/spire/agent/private/api.sock -write /tmp/rogue_socket_svid \
    >/tmp/rogue_socket_fetch 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "fetch unexpectedly succeeded"
    return 1
  fi
  if docker exec spiffe-rogue-socket test -e /tmp/rogue_socket_svid/svid.pem 2>/dev/null; then
    set_reason "SVID file created"
    return 1
  fi
  return 0
}

# M2-T7
T7_test() {
  mounts="$(docker inspect -f '{{range .Mounts}}{{.Destination}} {{end}}' spiffe-spire-rogue-agent 2>/dev/null || true)"
  if text_contains_str "$mounts" "/run/spire/svid"; then
    set_reason "workload SVID mount present"
    return 1
  fi
  if text_contains_str "$mounts" "/run/spire/agent/data"; then
    set_reason "agent data mount present"
    return 1
  fi
  set +e
  docker exec spiffe-spire-rogue-agent cat /run/spire/svid/svid.pem >/tmp/rogue_svid_out 2>&1
  rc_cert=$?
  docker exec spiffe-spire-rogue-agent cat /run/spire/svid/svid.key >/tmp/rogue_svid_key 2>&1
  rc_key=$?
  docker exec spiffe-spire-rogue-agent cat /run/spire/agent/data/svid.0.pem >/tmp/rogue_node_svid 2>&1
  rc_node_cert=$?
  docker exec spiffe-spire-rogue-agent cat /run/spire/agent/data/keys.json >/tmp/rogue_node_keys 2>&1
  rc_node_key=$?
  set -e
  if [ $rc_cert -eq 0 ] || [ $rc_key -eq 0 ] || [ $rc_node_cert -eq 0 ] || [ $rc_node_key -eq 0 ]; then
    set_reason "rogue can read SVID or key material"
    return 1
  fi
  return 0
}

# M2-T8
T8_test() {
  after="/tmp/entries_after.txt"
  if ! capture_entries "$after"; then
    set_reason "failed to capture entry list"
    return 1
  fi
  if [ ! -s "$ENTRY_BEFORE" ]; then
    set_reason "baseline entry list missing"
    return 1
  fi
  if diff -u "$ENTRY_BEFORE" "$after" >/dev/null 2>&1; then
    return 0
  fi
  set_reason "SPIRE entries changed during tests"
  return 1
}

M25_T1_test() {
  out="/tmp/toolb_direct.out"
  set +e
  curl -sS --max-time 2 http://tool-b:8080/health >"$out" 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "tool-b app reachable from edge network"
    return 1
  fi
  return 0
}

M25_T2_test() {
  set +e
  docker exec spiffe-tool-b python - <<'PY'
import sys
import urllib.error
import urllib.request

try:
    urllib.request.urlopen("http://127.0.0.1:8080/secret")
    print("unexpected success")
    sys.exit(1)
except urllib.error.HTTPError as exc:
    code = exc.code
    print(code)
    sys.exit(0 if code == 401 else 1)
PY
  rc=$?
  set -e
  if [ $rc -ne 0 ]; then
    set_reason "missing x-spiffe-id not rejected by tool-b"
    return 1
  fi
  return 0
}

M25_T3_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  if ! wait_dns "tool-b-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "tool-b-envoy" "8443" 30; then
    return 1
  fi
  out="/tmp/toolb_material/m25_t3.out"
  set +e
  printf "GET /secret HTTP/1.1\r\nHost: tool-b-envoy\r\nConnection: close\r\n\r\n" | \
    $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -connect tool-b-envoy:8443 -cert "$TOOLB_CERT" \
      -key "$TOOLB_KEY" -CAfile "$TOOLB_BUNDLE" -verify_return_error \
      -showcerts -ign_eof >"$out" 2>&1
  rc=$?
  set -e
  if [ $rc -eq 0 ]; then
    set_reason "TLS succeeded with mismatched SPIFFE ID"
    return 1
  fi
  if ! assert_text_matches "$out" '(alert bad certificate|alert certificate unknown|bad certificate|certificate unknown|handshake failure)'; then
    set_reason "TLS failure did not indicate SPIFFE ID mismatch: $(cat "$out")"
    return 1
  fi
  return 0
}

M3S2_T1_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  out="/tmp/capiss_t1.out"
  status="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$out")"
  if [ "$status" != "200" ]; then
    set_reason "expected 200, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  if ! assert_json_eq "$out" '.token_type' 'biscuit'; then
    return 1
  fi
  if ! assert_json_present "$out" '.token'; then
    return 1
  fi
  if ! assert_json_present "$out" '.expires_at'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.issued_to' 'spiffe://example.org/agent-a'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.aud' 'tool-b'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.act' 'read'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.res' '/secret'; then
    return 1
  fi
  return 0
}

M3S2_T2_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  out="/tmp/capiss_t2.out"
  status="$(mint_with_cert "$CAPISS_ROGUE_CERT" "$CAPISS_ROGUE_KEY" "$CAPISS_MINT_URL" "$out")"
  if [ "$status" != "403" ]; then
    set_reason "expected 403, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  if ! assert_json_eq "$out" '.error' 'denied'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.reason' 'policy'; then
    return 1
  fi
  return 0
}

M3S2_T3_test() {
  out="/tmp/capiss_t3.out"
  if expect_edge_unreachable "http://opa:8181/v1/data/capiss/allow" "$out"; then
    return 0
  fi
  set_reason "OPA reachable from edge network"
  return 1
}

M3S2_T4_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! wait_dns "capability-issuer-no-opa-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "capability-issuer-no-opa-envoy" "9444" 30; then
    return 1
  fi
  resolve_arg="$(resolve_arg_for_url "https://capability-issuer-no-opa-envoy:9444/health" || true)"
  ready=0
  for i in $(seq 1 40); do
    if curl -sS --insecure $resolve_arg --cert "$CAPISS_AGENT_CERT" --key "$CAPISS_AGENT_KEY" \
      https://capability-issuer-no-opa-envoy:9444/health >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 0.2
  done
  if [ "$ready" -ne 1 ]; then
    set_reason "capability-issuer-no-opa-envoy not reachable"
    return 1
  fi
  out="/tmp/capiss_t4.out"
  status="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_NO_OPA_URL" "$out")"
  if [ "$status" != "503" ] && [ "$status" != "403" ]; then
    set_reason "expected 503/403, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  if ! assert_json_eq "$out" '.error' 'denied'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.reason' 'opa_unavailable'; then
    return 1
  fi
  return 0
}

M3S2_T5_test() {
  out="/tmp/capiss_t5.out"
  if expect_edge_unreachable "http://capability-issuer:8000/health" "$out"; then
    return 0
  fi
  set_reason "capability-issuer app reachable from edge network"
  return 1
}

M3S3_T1_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  out="/tmp/capiss_s3_t1.out"
  status="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$out")"
  if [ "$status" != "200" ]; then
    set_reason "expected 200, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  token="$(json_get '.token' "$out")"
  if [ -z "$token" ] || [ "$token" = "null" ]; then
    set_reason "token is empty"
    return 1
  fi
  return 0
}

M3S3_T2_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  out="/tmp/capiss_s3_t2.out"
  status="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$out")"
  if [ "$status" != "200" ]; then
    set_reason "expected 200, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  expires_at="$(json_get '.expires_at' "$out")"
  now="$(date +%s)"
  if [ -n "$expires_at" ] && [ "$expires_at" != "null" ]; then
    delta="$((expires_at - now))"
  else
    delta=""
  fi
  if [ -z "$delta" ]; then
    set_reason "expires_at missing"
    return 1
  fi
  if [ "$delta" -le 0 ] || [ "$delta" -gt 120 ]; then
    set_reason "expires_at delta out of range: ${delta}s"
    return 1
  fi
  echo "M3.S3 T2 expires_at delta: ${delta}s"
  return 0
}

M3S3_T3_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  out1="/tmp/capiss_s3_t3_1.out"
  out2="/tmp/capiss_s3_t3_2.out"
  status1="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$out1")"
  status2="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$out2")"
  if [ "$status1" != "200" ] || [ "$status2" != "200" ]; then
    set_reason "expected 200s, got ${status1:-none}/${status2:-none}"
    return 1
  fi
  token1="$(json_get '.token' "$out1")"
  token2="$(json_get '.token' "$out2")"
  if [ -z "$token1" ] || [ -z "$token2" ] || [ "$token1" = "null" ] || [ "$token2" = "null" ]; then
    set_reason "token missing in one of the responses"
    return 1
  fi
  if [ "$token1" = "$token2" ]; then
    set_reason "tokens are identical"
    return 1
  fi
  return 0
}

M3S4_T1_test() {
  if ! ensure_toolb_material || ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_toolb_envoy_ready; then
    return 1
  fi
  out="/tmp/toolb_s4_t1.out"
  status="$(toolb_request "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "" "$out")"
  if [ "$status" != "401" ] && [ "$status" != "403" ]; then
    set_reason "expected 401/403, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  reason="$(json_get '.reason' "$out")"
  if [ "$reason" != "missing_token" ]; then
    set_reason "expected reason missing_token, got ${reason:-none}"
    return 1
  fi
  return 0
}

M3S4_T2_test() {
  if ! ensure_toolb_material || ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  if ! ensure_toolb_envoy_ready; then
    return 1
  fi
  mint_out="/tmp/toolb_s4_t2_mint.out"
  status="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$mint_out")"
  if [ "$status" != "200" ]; then
    set_reason "mint expected 200, got ${status:-none}; body: $(cat "$mint_out")"
    return 1
  fi
  token="$(json_get '.token' "$mint_out")"
  if [ -z "$token" ] || [ "$token" = "null" ]; then
    set_reason "mint token missing"
    return 1
  fi
  out="/tmp/toolb_s4_t2.out"
  status="$(toolb_request "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$token" "$out")"
  if [ "$status" != "200" ]; then
    set_reason "expected 200, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  secret_value="$(json_get '.secret' "$out")"
  if [ "$secret_value" != "super sensitive demo secret" ]; then
    set_reason "expected secret value, got: $(cat "$out")"
    return 1
  fi
  return 0
}

M3S4_T3_test() {
  if ! ensure_toolb_material || ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_toolb_envoy_ready; then
    return 1
  fi
  out="/tmp/toolb_s4_t3.out"
  status="$(toolb_request "$CAPISS_ROGUE_CERT" "$CAPISS_ROGUE_KEY" "" "$out")"
  if [ "$status" != "401" ] && [ "$status" != "403" ]; then
    set_reason "expected 401/403, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  return 0
}

M3S4_T4_test() {
  if ! ensure_toolb_material || ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  if ! ensure_toolb_envoy_ready; then
    return 1
  fi
  mint_out="/tmp/toolb_s4_t4_mint.out"
  status="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$mint_out")"
  if [ "$status" != "200" ]; then
    set_reason "mint expected 200, got ${status:-none}; body: $(cat "$mint_out")"
    return 1
  fi
  token="$(json_get '.token' "$mint_out")"
  if [ -z "$token" ] || [ "$token" = "null" ]; then
    set_reason "mint token missing"
    return 1
  fi
  out="/tmp/toolb_s4_t4.out"
  status="$(toolb_request "$CAPISS_ROGUE_CERT" "$CAPISS_ROGUE_KEY" "$token" "$out")"
  if [ "$status" != "401" ] && [ "$status" != "403" ]; then
    set_reason "expected 401/403, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  reason="$(json_get '.reason' "$out")"
  if [ "$reason" != "sub_mismatch" ] && [ "$reason" != "invalid_token" ]; then
    set_reason "expected reason sub_mismatch or invalid_token, got ${reason:-none}"
    return 1
  fi
  return 0
}

M3S4_T5_test() {
  if ! ensure_toolb_material || ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  if ! ensure_toolb_envoy_ready; then
    return 1
  fi
  mint_out="/tmp/toolb_s4_t5_mint.out"
  status="$(mint_with_cert "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" "$mint_out")"
  if [ "$status" != "200" ]; then
    set_reason "mint expected 200, got ${status:-none}; body: $(cat "$mint_out")"
    return 1
  fi
  token="$(json_get '.token' "$mint_out")"
  expires_at="$(json_get '.expires_at' "$mint_out")"
  if [ -z "$token" ] || [ "$token" = "null" ] || [ -z "$expires_at" ] || [ "$expires_at" = "null" ]; then
    set_reason "mint token or expires_at missing"
    return 1
  fi
  now="$(date +%s)"
  wait_seconds=$((expires_at - now + 1))
  if [ "$wait_seconds" -gt 0 ]; then
    sleep "$wait_seconds"
  fi
  out="/tmp/toolb_s4_t5.out"
  status="$(toolb_request "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$token" "$out")"
  if [ "$status" != "401" ] && [ "$status" != "403" ]; then
    set_reason "expected 401/403, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  reason="$(json_get '.reason' "$out")"
  if [ "$reason" != "expired" ]; then
    set_reason "expected reason expired, got ${reason:-none}"
    return 1
  fi
  return 0
}

M3S4_T6_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  out="/tmp/capiss_s4_t6.out"
  status="$(mint_with_body "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" '{}' "$out")"
  if [ "$status" != "400" ]; then
    set_reason "expected 400, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  if ! assert_json_eq "$out" '.error' 'bad_request'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.reason' 'aud'; then
    return 1
  fi
  return 0
}

M3S4_T7_test() {
  if ! ensure_capiss_material; then
    return 1
  fi
  if ! ensure_capiss_envoy_ready; then
    return 1
  fi
  out="/tmp/capiss_s4_t7.out"
  status="$(mint_with_body "$CAPISS_AGENT_CERT" "$CAPISS_AGENT_KEY" "$CAPISS_MINT_URL" \
    '{"aud":"tool-b","act":"write","res":"/secret"}' "$out")"
  if [ "$status" != "403" ]; then
    set_reason "expected 403, got ${status:-none}; body: $(cat "$out")"
    return 1
  fi
  if ! assert_json_eq "$out" '.error' 'denied'; then
    return 1
  fi
  if ! assert_json_eq "$out" '.reason' 'policy'; then
    return 1
  fi
  return 0
}

print_section "Milestone 1 - Server and agent connection and successful entry"
run_test "T1" "Rogue missing join token rejects attestation" c1_test
run_test "T2" "Rogue forged join token rejects attestation" c2_test
run_test "T3" "Rogue replayed join token rejects attestation" c3_test
run_test "T4" "Rogue cannot read join token" c4_test
run_test "T5" "Only intended node entries exist" c5_test

print_section "Milestone 2 - Workload identities security tests"
run_test "T1" "Rogue without SVID cannot access /secret" T1_test
run_test "T2" "Rogue with invalid client cert is rejected" T2_test
run_test "T3" "Rogue with expired client cert is rejected" T3_test
run_test "T4" "Rogue with wrong SPIFFE ID is rejected" T4_test
run_test "T5" "Rogue without Workload API socket cannot fetch SVID" T5_test
run_test "T6" "Rogue with socket but no entry cannot fetch SVID" T6_test
run_test "T7" "Rogue cannot read SVIDs or keys" T7_test
run_test "T8" "No unintended SPIRE entries created" T8_test
run_test "T9" "Rogue with expired short-lived SVID is rejected" T9_test

print_section "Milestone 2.5 - Envoy ingress boundary"
run_test "T1" "tool-b app not reachable from edge network" M25_T1_test
run_test "T2" "tool-b rejects missing x-spiffe-id header" M25_T2_test
run_test "T3" "tool-b rejects mismatched x-spiffe-id header" M25_T3_test

print_section "M3.S2 — OPA-gated capability minting"
run_test "T1" "agent-a can mint (allowed by OPA)" M3S2_T1_test
run_test "T2" "rogue mint denied by policy" M3S2_T2_test
run_test "T3" "OPA is not reachable from edge" M3S2_T3_test
run_test "T4" "Fail closed when OPA is unavailable" M3S2_T4_test
run_test "T5" "Issuer denies when x-spiffe-id missing (structural guard)" M3S2_T5_test

print_section "M3.S3 — Biscuit minting"
run_test "T1" "mint returns non-empty token" M3S3_T1_test
run_test "T2" "expires_at is present and in the near future" M3S3_T2_test
run_test "T3" "two mints produce different tokens" M3S3_T3_test

print_section "M3.S4 — tool-b enforces capability tokens"
run_test "T1" "identity-only access to /secret is denied" M3S4_T1_test
run_test "T2" "agent-a can access /secret with minted capability" M3S4_T2_test
run_test "T3" "rogue cannot access /secret without token" M3S4_T3_test
run_test "T4" "stolen token replay by rogue is rejected" M3S4_T4_test
run_test "T5" "expired token is rejected" M3S4_T5_test
run_test "T6" "mint rejects missing parameters" M3S4_T6_test
run_test "T7" "mint denies unapproved authority request" M3S4_T7_test

printf '\nTotal: %d  Passed: %d  Failed: %d\n' "$TOTAL" "$PASSED" "$FAILED"
if [ "$FAILED" -ne 0 ]; then
  exit 1
fi
