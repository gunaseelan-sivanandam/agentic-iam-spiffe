#!/bin/sh
# Evidence model: Premise proves inputs/env are as expected, Exercise proves the SUT
# was actually invoked, Outcome proves expected result and fails on harness errors.
# Evidence artifacts are stored under /tmp/rogue-tests/<TEST_ID>_<slug>/.
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
EVDIR=""

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

RUN_M1=1
RUN_M2=1
RUN_M25=1
RUN_M3=1

if [ -n "${TEST_MILESTONES:-}" ]; then
  RUN_M1=0
  RUN_M2=0
  RUN_M25=0
  RUN_M3=0
  for token in $(printf '%s' "$TEST_MILESTONES" | tr ',' ' '); do
    case "$token" in
      m1|M1) RUN_M1=1 ;;
      m2|M2) RUN_M2=1 ;;
      m25|M2.5|M2_5) RUN_M25=1 ;;
      m3|M3) RUN_M3=1 ;;
    esac
  done
fi

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

should_run_test() {
  full_id="$1"
  if [ -z "${TEST_ONLY:-}" ]; then
    return 0
  fi
  for token in $(printf '%s' "$TEST_ONLY" | tr ',' ' '); do
    if [ "$token" = "$full_id" ]; then
      return 0
    fi
  done
  return 1
}

run_test() {
  id="$1"
  name="$2"
  shift 2
  full_id="${TEST_PREFIX:-}"
  if [ -n "$full_id" ]; then
    full_id="${full_id}-${id}"
  else
    full_id="$id"
  fi
  if ! should_run_test "$full_id"; then
    return 0
  fi
  start_ts="$(date +%s)"
  TOTAL=$((TOTAL + 1))
  FAIL_REASON=""
  GUARD_FAILED=0
  if "$@"; then
    rc=0
  else
    rc=1
  fi
  if [ "${GUARD_FAILED:-0}" -ne 0 ]; then
    rc=1
    if [ -z "${FAIL_REASON:-}" ]; then
      FAIL_REASON="Guard failed"
    fi
  fi
  if [ "$rc" -eq 0 ]; then
    PASSED=$((PASSED + 1))
    print_result "$id" "$name" "PASS" "$GREEN"
  else
    FAILED=$((FAILED + 1))
    print_result "$id" "$name" "FAIL" "$RED"
    if [ -n "$FAIL_REASON" ]; then
      printf '  Reason: %s\n' "$FAIL_REASON"
    fi
  fi
  end_ts="$(date +%s)"
  duration=$((end_ts - start_ts))
  printf '  Duration: %ss\n' "$duration"
  if [ -n "${EVDIR:-}" ]; then
    printf 'duration_seconds=%s\n' "$duration" >"${EVDIR}/duration.txt" 2>/dev/null || true
  fi
}

set_reason() {
  FAIL_REASON="$1"
  if [ -n "${EVDIR:-}" ]; then
    printf '%s\n' "$FAIL_REASON" >"${EVDIR}/fail_reason.txt" 2>/dev/null || true
  fi
}

begin_test_evidence() {
  ev_test_id="$1"
  ev_slug="$2"
  base="${ROGUE_TEST_EVIDENCE_DIR:-/tmp/rogue-tests}"
  EVDIR="${base}/${ev_test_id}_${ev_slug}"
  rm -rf "$EVDIR"
  mkdir -p "$EVDIR"
  export EVDIR
}

ev_note() {
  note="$1"
  if [ -n "${EVDIR:-}" ]; then
    printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$note" >>"${EVDIR}/notes.txt"
  fi
}

ev_save_cmd() {
  ev_name="$1"
  cmd="$2"
  if [ -n "${EVDIR:-}" ]; then
    printf '%s\n' "$cmd" >"${EVDIR}/cmd_${ev_name}.txt"
  fi
}

ev_copy_if_exists() {
  src="$1"
  dest_name="${2:-}"
  if [ -z "${EVDIR:-}" ]; then
    return 0
  fi
  if [ ! -e "$src" ]; then
    return 0
  fi
  if [ -z "$dest_name" ]; then
    dest_name="$(basename "$src")"
  fi
  cp "$src" "${EVDIR}/${dest_name}" 2>/dev/null || true
}

premise_guard() {
  msg="$1"
  cmd="$2"
  if [ -z "${EVDIR:-}" ]; then
    set_reason "PREMISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  idx="$(ls "${EVDIR}"/premise_*.txt 2>/dev/null | wc -l | tr -d ' ')"
  idx=$((idx + 1))
  guard_out="${EVDIR}/premise_${idx}.txt"
  ev_save_cmd "premise_${idx}" "$cmd"
  eval "$cmd" >"$guard_out" 2>&1
  if [ $? -ne 0 ]; then
    set_reason "PREMISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  return 0
}

exercise_guard() {
  msg="$1"
  cmd="$2"
  if [ -z "${EVDIR:-}" ]; then
    set_reason "EXERCISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  idx="$(ls "${EVDIR}"/exercise_*.txt 2>/dev/null | wc -l | tr -d ' ')"
  idx=$((idx + 1))
  guard_out="${EVDIR}/exercise_${idx}.txt"
  ev_save_cmd "exercise_${idx}" "$cmd"
  eval "$cmd" >"$guard_out" 2>&1
  if [ $? -ne 0 ]; then
    set_reason "EXERCISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  return 0
}

outcome_guard() {
  msg="$1"
  cmd="$2"
  if [ -z "${EVDIR:-}" ]; then
    set_reason "OUTCOME FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  idx="$(ls "${EVDIR}"/outcome_*.txt 2>/dev/null | wc -l | tr -d ' ')"
  idx=$((idx + 1))
  guard_out="${EVDIR}/outcome_${idx}.txt"
  ev_save_cmd "outcome_${idx}" "$cmd"
  eval "$cmd" >"$guard_out" 2>&1
  if [ $? -ne 0 ]; then
    set_reason "OUTCOME FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  return 0
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

resolve_service_ip() {
  svc_name="$1"
  ip=""
  if command -v getent >/dev/null 2>&1; then
    ip="$(getent hosts "$svc_name" 2>/dev/null | awk 'NR==1{print $1}')"
  fi
  if [ -z "$ip" ] && command -v nslookup >/dev/null 2>&1; then
    ip="$(nslookup "$svc_name" 127.0.0.11 2>/dev/null | awk '/^Address: /{print $2; exit}')"
  fi
  if [ -z "$ip" ] && command -v ping >/dev/null 2>&1; then
    ip="$(ping -c1 "$svc_name" 2>/dev/null | awk -F'[()]' 'NR==1{print $2; exit}')"
  fi
  if [ -n "$ip" ]; then
    printf '%s\n' "$ip"
    return 0
  fi
  return 1
}

wait_resolve_ip() {
  svc_name="$1"
  timeout="${2:-10}"
  i=0
  while [ $i -lt "$timeout" ]; do
    ip="$(resolve_service_ip "$svc_name" || true)"
    if [ -n "$ip" ]; then
      if [ -n "${EVDIR:-}" ]; then
        printf '%s\n' "$ip" >"${EVDIR}/resolve_${svc_name}.txt" 2>/dev/null || true
        ev_note "resolved ${svc_name} -> ${ip}"
      fi
      printf '%s\n' "$ip"
      return 0
    fi
    i=$((i + 1))
    sleep 0.2
  done
  if [ -n "${EVDIR:-}" ]; then
    ev_note "resolve ${svc_name} failed after ${timeout}s"
  fi
  return 1
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
      target="$host"
      if ! printf '%s' "$host" | grep -Eq '^[0-9.]+$'; then
        target="$(wait_resolve_ip "$host" 1 2>/dev/null || true)"
      fi
      if [ -n "$target" ] && nc -z -w1 "$target" "$port" >/dev/null 2>&1; then
        if [ -n "${EVDIR:-}" ]; then
          printf '%s:%s\n' "$target" "$port" >"${EVDIR}/tcp_${host}_${port}.txt" 2>/dev/null || true
          ev_note "tcp reachable ${host}:${port} via ${target}"
        fi
        echo "[gate] TCP OK ${host}:${port}"
        return 0
      fi
    else
      target="$host"
      if ! printf '%s' "$host" | grep -Eq '^[0-9.]+$'; then
        target="$(wait_resolve_ip "$host" 1 2>/dev/null || true)"
      fi
      last_out="$(timeout 2s openssl s_client -connect "${target}:${port}" -servername "$host" < /dev/null 2>&1 || true)"
      if printf '%s' "$last_out" | grep -Fq "CONNECTED"; then
        if [ -n "${EVDIR:-}" ]; then
          printf '%s:%s\n' "$target" "$port" >"${EVDIR}/tcp_${host}_${port}.txt" 2>/dev/null || true
          ev_note "tcp reachable ${host}:${port} via ${target}"
        fi
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
    if [ -z "$ip" ] && command -v nslookup >/dev/null 2>&1; then
      ip="$(nslookup "$host" 127.0.0.11 2>/dev/null | awk '/^Address: /{print $2; exit}')"
    fi
    if [ -z "$ip" ] && command -v ping >/dev/null 2>&1; then
      ip="$(ping -c1 "$host" 2>/dev/null | awk -F'[()]' 'NR==1{print $2; exit}')"
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

generate_fake_join_token() {
  if command -v python >/dev/null 2>&1; then
    python - <<'PY'
import uuid
print(uuid.uuid4())
PY
  else
    cat /proc/sys/kernel/random/uuid 2>/dev/null || true
  fi
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

assert_file_eq() {
  file="$1"
  expected="$2"
  actual="$(cat "$file" 2>/dev/null || true)"
  if [ "$actual" != "$expected" ]; then
    fail_with_body "expected $file=$expected got $actual" "$file"
    return 1
  fi
  return 0
}

assert_file_any() {
  file="$1"
  shift
  actual="$(cat "$file" 2>/dev/null || true)"
  for expected in "$@"; do
    if [ "$actual" = "$expected" ]; then
      return 0
    fi
  done
  fail_with_body "expected $file to be one of: $* (got $actual)" "$file"
  return 1
}

assert_expires_at_near() {
  file="$1"
  out_file="$2"
  max_delta="$3"
  token="$(jq -r '.token' "$file" 2>/dev/null || true)"
  expires_at="$(jq -r '.expires_at' "$file" 2>/dev/null || true)"
  if [ -z "$token" ] || [ "$token" = "null" ]; then
    fail_with_body "missing .token" "$file"
    return 1
  fi
  case "$expires_at" in
    ""|null|*[!0-9]*)
      fail_with_body "invalid .expires_at" "$file"
      return 1
      ;;
  esac
  now="$(date +%s)"
  delta=$((expires_at - now))
  printf 'now=%s expires_at=%s delta=%s\n' "$now" "$expires_at" "$delta" >"$out_file"
  if [ "$delta" -le 0 ] || [ "$delta" -gt "$max_delta" ]; then
    fail_with_body "expires_at delta out of range" "$file"
    return 1
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

start_temp_rogue_container() {
  tmp_name="rogue-test-$$-$RANDOM"
  if docker run -d --rm --name "$tmp_name" --entrypoint sleep compose-rogue:latest infinity >/dev/null 2>&1; then
    echo "$tmp_name"
    return 0
  fi
  return 1
}

wait_for_legit_attestation() {
  max_retries="${SVID_FETCH_RETRIES:-20}"
  i=0
  while [ $i -lt "$max_retries" ]; do
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
  outcome_marker=0

  rm -f "$log_file"
  mkdir -p "$temp_dir"
  # Ensure a minimal WorkloadAttestor so the agent can attempt attestation.
  # Inject into the existing plugins block and rewrite data_dir paths.
  awk -v tmp="$temp_dir" '
    { gsub("/run/spire/rogue", tmp) }
    ($1 == "plugins" && $2 == "{") {
      in_plugins=1
      print
      if (!inserted) {
        print "  WorkloadAttestor \"docker\" {"
        print "    plugin_data {"
        print "      docker_socket_path = \"unix:///var/run/docker.sock\""
        print "    }"
        print "  }"
        inserted=1
      }
      next
    }
    {
      print
      if (in_plugins && $1 == "}") { in_plugins=0 }
    }
    END {
      if (!inserted) {
        print "plugins {"
        print "  WorkloadAttestor \"docker\" {"
        print "    plugin_data {"
        print "      docker_socket_path = \"unix:///var/run/docker.sock\""
        print "    }"
        print "  }"
        print "}"
      }
    }
  ' /run/spire/rogue/agent.conf > "$temp_config"

  set +e
  /opt/spire/bin/spire-agent run -config "$temp_config" -joinToken "$token" \
    >"$log_file" 2>&1 &
  pid=$!
  set -e

  # Wait up to 60s for an explicit attestation outcome.
  i=0
  while [ $i -lt 60 ]; do
    if text_contains "$log_file" "Node attestation was successful"; then
      set_reason "rogue attestation succeeded"
      kill "$pid" >/dev/null 2>&1 || true
      wait "$pid" >/dev/null 2>&1 || true
      ev_copy_if_exists "$log_file" "rogue_${label}.log"
      ev_copy_if_exists "$temp_config" "rogue_${label}.conf"
      return 1
    fi
    if text_contains "$log_file" "attestation failed" ||
      text_contains "$log_file" "permission denied" ||
      text_contains "$log_file" "invalid token" ||
      text_contains "$log_file" "unauthorized" ||
      text_contains "$log_file" "join token was not provided" ||
      text_contains "$log_file" "join token does not exist"; then
      outcome_marker=1
      break
    fi
    if text_contains "$log_file" "Agent crashed"; then
      if [ "$outcome_marker" -eq 1 ]; then
        break
      fi
      set_reason "rogue agent crashed without explicit attestation denial"
      kill "$pid" >/dev/null 2>&1 || true
      wait "$pid" >/dev/null 2>&1 || true
      ev_copy_if_exists "$log_file" "rogue_${label}.log"
      ev_copy_if_exists "$temp_config" "rogue_${label}.conf"
      return 1
    fi
    i=$((i + 1))
    sleep 1
  done

  kill "$pid" >/dev/null 2>&1 || true
  wait "$pid" >/dev/null 2>&1 || true

  ev_copy_if_exists "$log_file" "rogue_${label}.log"
  ev_copy_if_exists "$temp_config" "rogue_${label}.conf"

  if [ $i -ge "$max_retries" ]; then
    ev_note "timed out waiting for attestation outcome (no explicit attestation success/failure observed)"
    set_reason "timed out waiting for attestation outcome (no explicit attestation success/failure observed)"
    return 1
  fi

  if [ "$outcome_marker" -ne 1 ]; then
    set_reason "no explicit attestation denial observed"
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
    if [ ! -s "${TOOLB_CERT:-}" ] || [ ! -s "${TOOLB_KEY:-}" ] || [ ! -s "${TOOLB_BUNDLE:-}" ]; then
      TOOLB_READY=0
    else
    ev_copy_if_exists "${TOOLB_CERT:-}" "toolb_svid.pem"
    ev_copy_if_exists "${TOOLB_BUNDLE:-}" "toolb_bundle.pem"
    return 0
    fi
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
  ev_copy_if_exists "${TOOLB_CERT:-}" "toolb_svid.pem"
  ev_copy_if_exists "${TOOLB_BUNDLE:-}" "toolb_bundle.pem"
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
  max_retries="${SVID_FETCH_RETRIES:-20}"
  i=0
  while [ $i -lt "$max_retries" ]; do
    i=$((i + 1))
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
    sleep 1
  done
  if [ $i -ge "$max_retries" ]; then
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
    ev_copy_if_exists "${CAPISS_AGENT_CERT:-}" "agent-a_svid.pem"
    ev_copy_if_exists "${CAPISS_ROGUE_CERT:-}" "rogue_svid.pem"
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
  ev_copy_if_exists "${CAPISS_AGENT_CERT:-}" "agent-a_svid.pem"
  ev_copy_if_exists "${CAPISS_ROGUE_CERT:-}" "rogue_svid.pem"
  return 0
}

ensure_toolb_envoy_ready() {
  if ! wait_dns "tool-b-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "tool-b-envoy" "8443" 30; then
    return 1
  fi
  TOOLB_ENVOY_IP="$(wait_resolve_ip "tool-b-envoy" 30 || true)"
  if [ -z "${TOOLB_ENVOY_IP:-}" ]; then
    set_reason "failed to resolve tool-b-envoy IP"
    return 1
  fi
  return 0
}

ensure_capiss_envoy_ready() {
  if ! wait_dns "capability-issuer-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "capability-issuer-envoy" "9443" 30; then
    return 1
  fi
  CAPISS_ENVOY_IP="$(wait_resolve_ip "capability-issuer-envoy" 30 || true)"
  if [ -z "${CAPISS_ENVOY_IP:-}" ]; then
    set_reason "failed to resolve capability-issuer-envoy IP"
    return 1
  fi
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
  ip=""
  if [ "$host" = "capability-issuer-envoy" ] && [ -n "${CAPISS_ENVOY_IP:-}" ]; then
    ip="$CAPISS_ENVOY_IP"
  elif [ "$host" = "capability-issuer-no-opa-envoy" ] && [ -n "${CAPISS_NO_OPA_ENVOY_IP:-}" ]; then
    ip="$CAPISS_NO_OPA_ENVOY_IP"
  else
    ip="$(resolve_ip_for_host "$host" || true)"
  fi
  curl_url="$url"
  host_header=""
  if [ -n "$ip" ] && [ -n "$port" ]; then
    curl_url="$(printf '%s' "$url" | sed "s#^\\(https\\?://\\)[^/]*#\\1${ip}:${port}#")"
    host_header="Host: ${host}"
  fi
  if [ "${DEBUG_RESOLVE:-}" = "1" ]; then
    printf '[debug] mint_with_cert url=%s host=%s port=%s ip=%s resolve_arg=%s host_header=%s curl_url=%s\n' \
      "$url" "$host" "$port" "${ip:-}" "$resolve_arg" "$host_header" "$curl_url" >&2
  fi
  if [ -n "$host_header" ]; then
    status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
      -H "$host_header" -H "Content-Type: application/json" -d "$CAPISS_MINT_BODY" "$curl_url" || true)"
  else
    status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
      -H "Content-Type: application/json" -d "$CAPISS_MINT_BODY" "$curl_url" || true)"
  fi
  printf '%s' "$status"
}

mint_with_cert_to_file() {
  cert="$1"
  key="$2"
  url="$3"
  out="$4"
  status_file="$5"
  status="$(mint_with_cert "$cert" "$key" "$url" "$out")"
  printf '%s' "$status" >"$status_file"
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
  ip=""
  if [ "$host" = "capability-issuer-envoy" ] && [ -n "${CAPISS_ENVOY_IP:-}" ]; then
    ip="$CAPISS_ENVOY_IP"
  elif [ "$host" = "capability-issuer-no-opa-envoy" ] && [ -n "${CAPISS_NO_OPA_ENVOY_IP:-}" ]; then
    ip="$CAPISS_NO_OPA_ENVOY_IP"
  else
    ip="$(resolve_ip_for_host "$host" || true)"
  fi
  curl_url="$url"
  host_header=""
  if [ -n "$ip" ] && [ -n "$port" ]; then
    curl_url="$(printf '%s' "$url" | sed "s#^\\(https\\?://\\)[^/]*#\\1${ip}:${port}#")"
    host_header="Host: ${host}"
  fi
  if [ "${DEBUG_RESOLVE:-}" = "1" ]; then
    printf '[debug] mint_with_body url=%s host=%s port=%s ip=%s resolve_arg=%s host_header=%s curl_url=%s\n' \
      "$url" "$host" "$port" "${ip:-}" "$resolve_arg" "$host_header" "$curl_url" >&2
  fi
  if [ -n "${CURL_TIMING_OUT:-}" ]; then
    tmp_out="$(mktemp)"
    if [ -n "$host_header" ]; then
      curl -sS -o "$out" --insecure $resolve_arg --cert "$cert" --key "$key" \
        -H "$host_header" -H "Content-Type: application/json" -d "$body" "$curl_url" \
        -w "http_code=%{http_code} time_namelookup=%{time_namelookup} time_connect=%{time_connect} time_appconnect=%{time_appconnect} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
        >"$tmp_out" || true
    else
      curl -sS -o "$out" --insecure $resolve_arg --cert "$cert" --key "$key" \
        -H "Content-Type: application/json" -d "$body" "$curl_url" \
        -w "http_code=%{http_code} time_namelookup=%{time_namelookup} time_connect=%{time_connect} time_appconnect=%{time_appconnect} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
        >"$tmp_out" || true
    fi
    status="$(awk -F'[= ]' 'NR==1{print $2}' "$tmp_out" 2>/dev/null | tail -n 1)"
    cat "$tmp_out" >"$CURL_TIMING_OUT" 2>/dev/null || true
    if [ -n "${CURL_TIMING_RAW_OUT:-}" ]; then
      cat "$tmp_out" >"$CURL_TIMING_RAW_OUT" 2>/dev/null || true
    fi
    if [ -z "$status" ] && [ -s "$CURL_TIMING_OUT" ]; then
      status="$(awk -F'[= ]' 'NR==1{print $2}' "$CURL_TIMING_OUT" 2>/dev/null | tail -n 1)"
    fi
    if [ -n "${CURL_STATUS_DEBUG:-}" ]; then
      {
        echo "parsed_status=${status}"
        echo "timing_out_path=${CURL_TIMING_OUT}"
        echo "sed_path=$(command -v sed 2>/dev/null || echo missing)"
        echo "awk_out=$(awk -F'[= ]' 'NR==1{print $2}' "$CURL_TIMING_OUT" 2>/dev/null | tail -n 1)"
      } >"$CURL_STATUS_DEBUG" 2>/dev/null || true
    fi
    rm -f "$tmp_out"
  else
    if [ -n "$host_header" ]; then
      status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
        -H "$host_header" -H "Content-Type: application/json" -d "$body" "$curl_url" || true)"
    else
      status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
        -H "Content-Type: application/json" -d "$body" "$curl_url" || true)"
    fi
  fi
  printf '%s' "$status"
}

mint_with_body_to_file() {
  cert="$1"
  key="$2"
  url="$3"
  body="$4"
  out="$5"
  status_file="$6"
  status="$(mint_with_body "$cert" "$key" "$url" "$body" "$out")"
  printf '%s' "$status" >"$status_file"
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
  ip=""
  if [ "$host" = "tool-b-envoy" ] && [ -n "${TOOLB_ENVOY_IP:-}" ]; then
    ip="$TOOLB_ENVOY_IP"
  else
    ip="$(resolve_ip_for_host "$host" || true)"
  fi
  curl_url="$TOOLB_SECRET_URL"
  host_header=""
  if [ -n "$ip" ] && [ -n "$port" ]; then
    curl_url="$(printf '%s' "$TOOLB_SECRET_URL" | sed "s#^\\(https\\?://\\)[^/]*#\\1${ip}:${port}#")"
    host_header="Host: ${host}"
  fi
  if [ "${DEBUG_RESOLVE:-}" = "1" ]; then
    printf '[debug] toolb_request url=%s host=%s port=%s ip=%s resolve_arg=%s host_header=%s curl_url=%s\n' \
      "$TOOLB_SECRET_URL" "$host" "$port" "${ip:-}" "$resolve_arg" "$host_header" "$curl_url" >&2
  fi
  if [ -n "${CURL_TIMING_OUT:-}" ]; then
    tmp_out="$(mktemp)"
    if [ -n "$token" ]; then
      if [ -n "$host_header" ]; then
        curl -sS -o "$out" --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" -H "$host_header" -H "Authorization: Bearer ${token}" "$curl_url" \
          -w "http_code=%{http_code} time_namelookup=%{time_namelookup} time_connect=%{time_connect} time_appconnect=%{time_appconnect} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
          >"$tmp_out" || true
      else
        curl -sS -o "$out" --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" -H "Authorization: Bearer ${token}" "$curl_url" \
          -w "http_code=%{http_code} time_namelookup=%{time_namelookup} time_connect=%{time_connect} time_appconnect=%{time_appconnect} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
          >"$tmp_out" || true
      fi
    else
      if [ -n "$host_header" ]; then
        curl -sS -o "$out" --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" -H "$host_header" "$curl_url" \
          -w "http_code=%{http_code} time_namelookup=%{time_namelookup} time_connect=%{time_connect} time_appconnect=%{time_appconnect} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
          >"$tmp_out" || true
      else
        curl -sS -o "$out" --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" "$curl_url" \
          -w "http_code=%{http_code} time_namelookup=%{time_namelookup} time_connect=%{time_connect} time_appconnect=%{time_appconnect} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
          >"$tmp_out" || true
      fi
    fi
    status="$(awk -F'[= ]' 'NR==1{print $2}' "$tmp_out" 2>/dev/null | tail -n 1)"
    cat "$tmp_out" >"$CURL_TIMING_OUT" 2>/dev/null || true
    if [ -n "${CURL_TIMING_RAW_OUT:-}" ]; then
      cat "$tmp_out" >"$CURL_TIMING_RAW_OUT" 2>/dev/null || true
    fi
    if [ -z "$status" ] && [ -s "$CURL_TIMING_OUT" ]; then
      status="$(awk -F'[= ]' 'NR==1{print $2}' "$CURL_TIMING_OUT" 2>/dev/null | tail -n 1)"
    fi
    if [ -n "${CURL_STATUS_DEBUG:-}" ]; then
      {
        echo "parsed_status=${status}"
        echo "timing_out_path=${CURL_TIMING_OUT}"
        echo "sed_path=$(command -v sed 2>/dev/null || echo missing)"
        echo "awk_out=$(awk -F'[= ]' 'NR==1{print $2}' "$CURL_TIMING_OUT" 2>/dev/null | tail -n 1)"
      } >"$CURL_STATUS_DEBUG" 2>/dev/null || true
    fi
    rm -f "$tmp_out"
  else
    if [ -n "$token" ]; then
      if [ -n "$host_header" ]; then
        status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" -H "$host_header" -H "Authorization: Bearer ${token}" "$curl_url" || true)"
      else
        status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" -H "Authorization: Bearer ${token}" "$curl_url" || true)"
      fi
    else
      if [ -n "$host_header" ]; then
        status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" -H "$host_header" "$curl_url" || true)"
      else
        status="$(curl -sS -o "$out" -w '%{http_code}' --insecure $resolve_arg --cert "$cert" --key "$key" \
          --cacert "$TOOLB_BUNDLE" "$curl_url" || true)"
      fi
    fi
  fi
  printf '%s' "$status"
}

toolb_request_to_file() {
  cert="$1"
  key="$2"
  token="$3"
  out="$4"
  status_file="$5"
  status="$(toolb_request "$cert" "$key" "$token" "$out")"
  printf '%s' "$status" >"$status_file"
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
  begin_test_evidence "M1-T1" "missing_join_token"
  echo "EVIDENCE_DIR=$EVDIR"
  mkdir -p /run/spire/rogue
  : > /run/spire/rogue/missing_token
  premise_guard "spire-server container running" \
    "docker ps --format '{{.Names}}' | grep -Fxq spiffe-spire-server"
  premise_guard "spire-server resolves" \
    "spire_server_ip=\"\$(wait_resolve_ip spire-server 30)\"; test -n \"\${spire_server_ip:-}\"; echo \"\${spire_server_ip}\" >\"$EVDIR/spire_server_ip.txt\""
  premise_guard "spire-server tcp reachable" \
    "wait_tcp \"$spire_server_ip\" 8081 30"
  premise_guard "spire-agent container running" \
    "docker ps --format '{{.Names}}' | grep -Fxq spiffe-spire-agent"
  premise_guard "agent socket present" \
    "docker exec spiffe-spire-agent test -S /run/spire/agent/private/api.sock"
  premise_guard "legit attestation present" \
    "docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock -output json | jq -e '.agents and (.agents|length>0)' >/dev/null"
  premise_guard "join token present" "test -s /run/spire/shared/join_token"
  premise_guard "missing token file present" "test -f /run/spire/rogue/missing_token"
  missing_token="$(cat /run/spire/rogue/missing_token 2>/dev/null || true)"
  exercise_guard "rogue attestation attempt with missing token" \
    "run_rogue_attest_should_fail \"M1-T1\" \"${missing_token}\""
  outcome_guard "attestation failed as expected" \
    "test -s \"$EVDIR/rogue_M1-T1.log\" && grep -Fq 'Starting node attestation' \"$EVDIR/rogue_M1-T1.log\" && grep -Eiq '(attestation.*fail|fail.*attest|attestation failed|permission denied|invalid token|unauthorized|join token was not provided|join token does not exist)' \"$EVDIR/rogue_M1-T1.log\""
  return 0
}

# M1-T2
c2_test() {
  begin_test_evidence "M1-T2" "forged_token"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "spire-server container running" \
    "docker ps --format '{{.Names}}' | grep -Fxq spiffe-spire-server"
  premise_guard "spire-server resolves" \
    "spire_server_ip=\"\$(wait_resolve_ip spire-server 30)\"; test -n \"\${spire_server_ip:-}\"; echo \"\${spire_server_ip}\" >\"$EVDIR/spire_server_ip.txt\""
  premise_guard "spire-server tcp reachable" \
    "wait_tcp \"$spire_server_ip\" 8081 30"
  premise_guard "spire-agent container running" \
    "docker ps --format '{{.Names}}' | grep -Fxq spiffe-spire-agent"
  premise_guard "agent socket present" \
    "docker exec spiffe-spire-agent test -S /run/spire/agent/private/api.sock"
  premise_guard "legit attestation present" \
    "docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock -output json | jq -e '.agents and (.agents|length>0)' >/dev/null"
  premise_guard "join token present" "test -s /run/spire/shared/join_token"
  premise_guard "rogue config directory present" "test -d /run/spire/rogue"
  exercise_guard "rogue attestation attempt with forged token" \
    "generate_fake_join_token > /run/spire/rogue/fake_token; run_rogue_attest_should_fail \"M1-T2\" \"\$(cat /run/spire/rogue/fake_token)\""
  exercise_guard "capture spire-server attestation logs" \
    "docker logs --tail=200 spiffe-spire-server > \"$EVDIR/spire_server.log\" 2>&1"
  outcome_guard "attestation failed as expected" \
    "test -s \"$EVDIR/rogue_M1-T2.log\" && grep -Fq 'Starting node attestation' \"$EVDIR/rogue_M1-T2.log\" && grep -Eiq '(attestation.*fail|fail.*attest|attestation failed|permission denied|invalid token|unauthorized|join token does not exist)' \"$EVDIR/rogue_M1-T2.log\""
  outcome_guard "server recorded attestation failure" \
    "test -s \"$EVDIR/spire_server.log\" && grep -Eiq 'AttestAgent|attestation request' \"$EVDIR/spire_server.log\" && grep -Eiq 'join token does not exist|has already been used' \"$EVDIR/spire_server.log\""
  return 0
}

# M1-T3
c3_test() {
  begin_test_evidence "M1-T3" "replayed_token"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "spire-server container running" \
    "docker ps --format '{{.Names}}' | grep -Fxq spiffe-spire-server"
  premise_guard "spire-server resolves" \
    "spire_server_ip=\"\$(wait_resolve_ip spire-server 30)\"; test -n \"\${spire_server_ip:-}\"; echo \"\${spire_server_ip}\" >\"$EVDIR/spire_server_ip.txt\""
  premise_guard "spire-server tcp reachable" \
    "wait_tcp \"$spire_server_ip\" 8081 30"
  premise_guard "spire-agent container running" \
    "docker ps --format '{{.Names}}' | grep -Fxq spiffe-spire-agent"
  premise_guard "agent socket present" \
    "docker exec spiffe-spire-agent test -S /run/spire/agent/private/api.sock"
  premise_guard "legit attestation present" \
    "docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock -output json | jq -e '.agents and (.agents|length>0)' >/dev/null"
  premise_guard "join token present" "test -s /run/spire/shared/join_token"
  exercise_guard "rogue attestation attempt with replayed token" \
    "run_rogue_attest_should_fail \"M1-T3\" \"\$(cat /run/spire/shared/join_token)\""
  exercise_guard "capture spire-server attestation logs" \
    "docker logs --tail=200 spiffe-spire-server > \"$EVDIR/spire_server.log\" 2>&1"
  outcome_guard "attestation failed as expected" \
    "test -s \"$EVDIR/rogue_M1-T3.log\" && grep -Fq 'Starting node attestation' \"$EVDIR/rogue_M1-T3.log\" && grep -Eiq '(attestation.*fail|fail.*attest|attestation failed|permission denied|invalid token|unauthorized|join token does not exist)' \"$EVDIR/rogue_M1-T3.log\""
  outcome_guard "server recorded attestation failure" \
    "test -s \"$EVDIR/spire_server.log\" && grep -Eiq 'AttestAgent|attestation request' \"$EVDIR/spire_server.log\" && grep -Eiq 'join token does not exist|has already been used' \"$EVDIR/spire_server.log\""
  return 0
}

# M1-T4
c4_test() {
  begin_test_evidence "M1-T4" "join_token_read"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "rogue agent container exists" \
    "docker inspect spiffe-spire-rogue-agent >/dev/null 2>&1"
  premise_guard "spire-server resolves" \
    "spire_server_ip=\"\$(wait_resolve_ip spire-server 30)\"; test -n \"\${spire_server_ip:-}\"; echo \"\${spire_server_ip}\" >\"$EVDIR/spire_server_ip.txt\""
  premise_guard "spire-server tcp reachable" \
    "wait_tcp \"$spire_server_ip\" 8081 30"
  premise_guard "join token present" "test -s /run/spire/shared/join_token"
  exercise_guard "capture rogue agent mounts" \
    "docker inspect -f '{{range .Mounts}}{{.Destination}} {{end}}' spiffe-spire-rogue-agent > \"$EVDIR/rogue_token_mounts.txt\" 2>&1"
  outcome_guard "join token not mounted into rogue agent" \
    "test -s \"$EVDIR/rogue_token_mounts.txt\" && ! grep -Fq /run/spire/shared \"$EVDIR/rogue_token_mounts.txt\""
  return 0
}

# M1-T5
c5_test() {
  begin_test_evidence "M1-T5" "node_entries"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "spire-server container running" \
    "docker ps --format '{{.Names}}' | grep -Fxq spiffe-spire-server"
  premise_guard "spire-server resolves" \
    "spire_server_ip=\"\$(wait_resolve_ip spire-server 30)\"; test -n \"\${spire_server_ip:-}\"; echo \"\${spire_server_ip}\" >\"$EVDIR/spire_server_ip.txt\""
  premise_guard "spire-server tcp reachable" \
    "wait_tcp \"$spire_server_ip\" 8081 30"
  premise_guard "baseline entry list exists" "test -s \"$ENTRY_BEFORE\""
  exercise_guard "capture agent list" \
    "docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock -output json > \"$EVDIR/m1_t5_agents.json\""
  outcome_guard "agent list matches expected nodes" \
    "test \"\$(docker ps -q --filter \"label=spiffe.node=true\" | wc -l | tr -d ' ')\" -ne 0 && test \"\$(grep -o '\"id\"' \"$EVDIR/m1_t5_agents.json\" | wc -l | tr -d ' ')\" -eq \"\$(docker ps -q --filter \"label=spiffe.node=true\" | wc -l | tr -d ' ')\""
  return 0
}

# M2-T1
T1_test() {
  begin_test_evidence "M2-T1" "missing_client_cert"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b material present" "ensure_toolb_material"
  premise_guard "tool-b bundle present" "test -s \"${TOOLB_BUNDLE:-}\""
  premise_guard "resolve tool-b-envoy" \
    "toolb_ip=\"\$(wait_resolve_ip tool-b-envoy 30)\" && printf '%s\n' \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\""
  premise_guard "tool-b-envoy tcp reachable" "wait_tcp \"\$toolb_ip\" 8443 30"
  ev_note "target tool-b-envoy ${toolb_ip}:8443"
  if [ -s "${TOOLB_BUNDLE:-}" ]; then
    cp "$TOOLB_BUNDLE" "$EVDIR/toolb_bundle.pem" 2>/dev/null || true
  fi
  out="${EVDIR}/mtls_trace.txt"
  exercise_guard "openssl without client cert" \
    "set +e; $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -state -msg -tlsextdebug -brief -connect ${toolb_ip}:8443 -servername tool-b-envoy -CAfile \"${TOOLB_BUNDLE:-}\" -verify_return_error < /dev/null >\"$out\" 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; test -s \"$out\" && grep -Fq \"CertificateRequest\" \"$out\""
  outcome_guard "missing client cert rejected" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! grep -Eq '(could not resolve|no route to host|connection refused)' \"$out\" && assert_text_matches \"$out\" '(handshake failure|certificate required|no peer certificate)'"
  return 0
}

# M2-T2
T2_test() {
  begin_test_evidence "M2-T2" "invalid_client_cert"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b material present" "ensure_toolb_material"
  premise_guard "tool-b bundle present" "test -s \"${TOOLB_BUNDLE:-}\""
  premise_guard "resolve tool-b-envoy" \
    "toolb_ip=\"\$(wait_resolve_ip tool-b-envoy 30)\" && printf '%s\n' \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\""
  premise_guard "tool-b-envoy tcp reachable" "wait_tcp \"\$toolb_ip\" 8443 30"
  ev_note "target tool-b-envoy ${toolb_ip}:8443"
  tmpdir="/tmp/toolb_material"
  openssl req -x509 -newkey rsa:2048 -nodes -keyout "$tmpdir/bad.key" \
    -out "$tmpdir/bad.pem" -days 1 -subj "/CN=rogue" >/dev/null 2>&1
  cp "$tmpdir/bad.pem" "$EVDIR/bad.pem" 2>/dev/null || true
  if [ -s "${TOOLB_BUNDLE:-}" ]; then
    cp "$TOOLB_BUNDLE" "$EVDIR/toolb_bundle.pem" 2>/dev/null || true
  fi
  out="${EVDIR}/mtls_trace.txt"
  exercise_guard "openssl with invalid client cert" \
    "set +e; $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -state -msg -tlsextdebug -brief -connect ${toolb_ip}:8443 -servername tool-b-envoy -cert \"$tmpdir/bad.pem\" -key \"$tmpdir/bad.key\" -CAfile \"${TOOLB_BUNDLE:-}\" -verify_return_error < /dev/null >\"$out\" 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; test -s \"$out\" && grep -Fq \"CertificateRequest\" \"$out\" && grep -Fq \"write client certificate\" \"$out\""
  outcome_guard "invalid client cert rejected" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! grep -Eq '(could not resolve|no route to host|connection refused)' \"$out\" && assert_text_matches \"$out\" '(unknown ca|bad certificate|certificate unknown)'"
  return 0
}

# M2-T3
T3_test() {
  begin_test_evidence "M2-T3" "expired_client_cert"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b material present" "ensure_toolb_material"
  premise_guard "tool-b bundle present" "test -s \"${TOOLB_BUNDLE:-}\""
  premise_guard "resolve tool-b-envoy" \
    "toolb_ip=\"\$(wait_resolve_ip tool-b-envoy 30)\" && printf '%s\n' \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\""
  premise_guard "tool-b-envoy tcp reachable" "wait_tcp \"\$toolb_ip\" 8443 30"
  ev_note "target tool-b-envoy ${toolb_ip}:8443"
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
  ev_copy_if_exists /tmp/exp_ca.log "exp_ca.log"
  if [ ! -s "$tmpdir/exp.pem" ]; then
    set_reason "expired cert not created"
    return 1
  fi
  if ! openssl x509 -noout -enddate -in "$tmpdir/exp.pem" >"$tmpdir/exp_end.txt" 2>/tmp/exp_end.err; then
    set_reason "failed to read expired cert enddate: $(cat /tmp/exp_end.err)"
    return 1
  fi
  ev_copy_if_exists "$tmpdir/exp_end.txt" "exp_end.txt"
  ev_copy_if_exists /tmp/exp_end.err "exp_end.err"
  if ! assert_text_matches "$tmpdir/exp_end.txt" 'notAfter=.* 2000 GMT$'; then
    set_reason "expired cert enddate not in the past: $(cat "$tmpdir/exp_end.txt")"
    return 1
  fi
  cp "$tmpdir/exp.pem" "$EVDIR/exp.pem" 2>/dev/null || true
  cp "$ca_dir/certs/ca.pem" "$EVDIR/exp_ca.pem" 2>/dev/null || true
  if [ -s "${TOOLB_BUNDLE:-}" ]; then
    cp "$TOOLB_BUNDLE" "$EVDIR/toolb_bundle.pem" 2>/dev/null || true
  fi
  out="${EVDIR}/mtls_trace.txt"
  exercise_guard "openssl with expired client cert" \
    "set +e; $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -state -msg -tlsextdebug -brief -connect ${toolb_ip}:8443 -servername tool-b-envoy -cert \"$tmpdir/exp.pem\" -key \"$tmpdir/exp.key\" -CAfile \"${TOOLB_BUNDLE:-}\" -verify_return_error < /dev/null >\"$out\" 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; test -s \"$out\" && grep -Fq \"CertificateRequest\" \"$out\" && grep -Fq \"write client certificate\" \"$out\""
  outcome_guard "expired client cert rejected" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! grep -Eq '(could not resolve|no route to host|connection refused)' \"$out\" && assert_text_matches \"$out\" '(alert unknown ca|unknown ca|unable to get local issuer certificate|verify error:num=20)'"
  return 0
}

# M2-T9
T9_test() {
  begin_test_evidence "M2-T9" "expired_short_lived_svid"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b material present" "ensure_toolb_material"
  premise_guard "resolve tool-b-envoy" \
    "toolb_ip=\"\$(wait_resolve_ip tool-b-envoy 30)\" && printf '%s\n' \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\""
  premise_guard "tool-b-envoy tcp reachable" "wait_tcp \"\$toolb_ip\" 8443 30"
  ev_note "target tool-b-envoy ${toolb_ip}:8443"

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
  ev_copy_if_exists /tmp/short_entry.err "short_entry.err"
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
    ev_copy_if_exists /tmp/short_entry.err "short_entry_retry.err"
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
  ev_copy_if_exists /tmp/short_fetch.err "short_fetch.err"

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
  cp "$short_dir/svid.0.pem" "$EVDIR/short_svid.pem" 2>/dev/null || true
  cp "$short_dir/bundle.pem" "$EVDIR/short_bundle.pem" 2>/dev/null || true

  out="${EVDIR}/mtls_trace.txt"
  exercise_guard "openssl with expired short-lived SVID" \
    "set +e; $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -state -msg -tlsextdebug -brief -connect ${toolb_ip}:8443 -servername tool-b-envoy -cert \"$short_dir/svid.0.pem\" -key \"$short_dir/svid.0.key\" -CAfile \"$short_dir/bundle.pem\" -verify_return_error < /dev/null >\"$out\" 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; test -s \"$out\" && grep -Fq \"CertificateRequest\" \"$out\" && grep -Fq \"write client certificate\" \"$out\""
  cleanup_entry

  outcome_guard "expired short-lived SVID rejected" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! grep -Eq '(could not resolve|no route to host|connection refused)' \"$out\" && assert_text_matches \"$out\" '(expired|certificate has expired|verify error:num=10|verify return code: 10)'"
  return 0
}

# M2-T4
T4_test() {
  begin_test_evidence "M2-T4" "wrong_spiffe_id"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b material present" "ensure_toolb_material"
  premise_guard "tool-b cert present" "test -s \"${TOOLB_CERT:-}\""
  premise_guard "tool-b key present" "test -s \"${TOOLB_KEY:-}\""
  premise_guard "tool-b bundle present" "test -s \"${TOOLB_BUNDLE:-}\""
  premise_guard "resolve tool-b-envoy" \
    "toolb_ip=\"\$(wait_resolve_ip tool-b-envoy 30)\" && printf '%s\n' \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\""
  premise_guard "tool-b-envoy tcp reachable" "wait_tcp \"\$toolb_ip\" 8443 30"
  ev_note "target tool-b-envoy ${toolb_ip}:8443"
  if [ -s "${TOOLB_CERT:-}" ]; then
    cp "$TOOLB_CERT" "$EVDIR/toolb_cert.pem" 2>/dev/null || true
  fi
  if [ -s "${TOOLB_BUNDLE:-}" ]; then
    cp "$TOOLB_BUNDLE" "$EVDIR/toolb_bundle.pem" 2>/dev/null || true
  fi
  out="${EVDIR}/mtls_trace.txt"
  exercise_guard "openssl with wrong SPIFFE ID" \
    "set +e; printf \"GET /secret HTTP/1.1\\r\\nHost: tool-b-envoy\\r\\nConnection: close\\r\\n\\r\\n\" | $TIMEOUT_BIN 6s openssl s_client $TLS_CLIENT_ARGS -state -msg -tlsextdebug -brief -connect ${toolb_ip}:8443 -servername tool-b-envoy -cert \"${TOOLB_CERT:-}\" -key \"${TOOLB_KEY:-}\" -CAfile \"${TOOLB_BUNDLE:-}\" -verify_return_error -showcerts -ign_eof >\"$out\" 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; test -s \"$out\" && grep -Fq \"CertificateRequest\" \"$out\" && grep -Fq \"write client certificate\" \"$out\""
  outcome_guard "wrong SPIFFE ID rejected" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! grep -Eq '(could not resolve|no route to host|connection refused)' \"$out\" && assert_text_matches \"$out\" '(alert bad certificate|alert certificate unknown|bad certificate|certificate unknown|handshake failure)'"
  return 0
}

# M2-T5
T5_test() {
  begin_test_evidence "M2-T5" "no_workload_socket"
  echo "EVIDENCE_DIR=$EVDIR"
  temp_rogue=""
  premise_guard "start temp rogue container" \
    "temp_rogue=\"\$(start_temp_rogue_container)\"; test -n \"\$temp_rogue\"; echo \"\$temp_rogue\" >\"$EVDIR/temp_rogue_name.txt\""
  premise_guard "workload socket missing" \
    "! docker exec \"${temp_rogue}\" test -S /run/spire/agent/private/api.sock 2>/dev/null"
  exercise_guard "attempt fetch without socket" \
    "set +e; docker exec \"${temp_rogue}\" /opt/spire/bin/spire-agent api fetch x509 -socketPath /run/spire/agent/private/api.sock -write /tmp/rogue_svid >/tmp/rogue_fetch 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; cat /tmp/rogue_fetch >\"$EVDIR/rogue_fetch.txt\" 2>/dev/null || true"
  outcome_guard "fetch denied without socket" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! docker exec \"${temp_rogue}\" test -e /tmp/rogue_svid/svid.pem 2>/dev/null"
  if [ -n "${temp_rogue:-}" ]; then
    docker rm -f "$temp_rogue" >/dev/null 2>&1 || true
  fi
  return 0
}

# M2-T6
T6_test() {
  begin_test_evidence "M2-T6" "socket_no_entry"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "rogue-socket container running" "container_running spiffe-rogue-socket"
  premise_guard "workload socket present" \
    "docker exec spiffe-rogue-socket test -S /run/spire/agent/private/api.sock 2>/dev/null"
  exercise_guard "attempt fetch without entry" \
    "set +e; docker exec spiffe-rogue-socket /opt/spire/bin/spire-agent api fetch x509 -socketPath /run/spire/agent/private/api.sock -write /tmp/rogue_socket_svid >/tmp/rogue_socket_fetch 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; cat /tmp/rogue_socket_fetch >\"$EVDIR/rogue_socket_fetch.txt\" 2>/dev/null || true"
  outcome_guard "fetch denied without entry" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! docker exec spiffe-rogue-socket test -e /tmp/rogue_socket_svid/svid.pem 2>/dev/null"
  return 0
}

# M2-T7
T7_test() {
  begin_test_evidence "M2-T7" "no_svid_or_keys"
  echo "EVIDENCE_DIR=$EVDIR"
  temp_rogue=""
  premise_guard "start temp rogue container" \
    "temp_rogue=\"\$(start_temp_rogue_container)\"; test -n \"\$temp_rogue\"; echo \"\$temp_rogue\" >\"$EVDIR/temp_rogue_name.txt\""
  premise_guard "no SVID or agent data mounts" \
    "mounts=\"\$(docker inspect -f '{{range .Mounts}}{{.Destination}} {{end}}' \"${temp_rogue}\" 2>/dev/null || true)\"; ! text_contains_str \"\$mounts\" \"/run/spire/svid\" && ! text_contains_str \"\$mounts\" \"/run/spire/agent/data\""
  exercise_guard "attempt read of SVID and keys" \
    "set +e; docker exec \"${temp_rogue}\" cat /run/spire/svid/svid.pem >/tmp/rogue_svid_out 2>&1; rc_cert=\$?; docker exec \"${temp_rogue}\" cat /run/spire/svid/svid.key >/tmp/rogue_svid_key 2>&1; rc_key=\$?; docker exec \"${temp_rogue}\" cat /run/spire/agent/data/svid.0.pem >/tmp/rogue_node_svid 2>&1; rc_node_cert=\$?; docker exec \"${temp_rogue}\" cat /run/spire/agent/data/keys.json >/tmp/rogue_node_keys 2>&1; rc_node_key=\$?; set -e; echo \"\$rc_cert \$rc_key \$rc_node_cert \$rc_node_key\" >\"$EVDIR/rcs.txt\"; cat /tmp/rogue_svid_out >\"$EVDIR/rogue_svid_out.txt\" 2>/dev/null || true; cat /tmp/rogue_node_svid >\"$EVDIR/rogue_node_svid.txt\" 2>/dev/null || true; cat /tmp/rogue_node_keys >\"$EVDIR/rogue_node_keys.txt\" 2>/dev/null || true"
  outcome_guard "rogue cannot read SVID or keys" \
    "set -- \$(cat \"$EVDIR/rcs.txt\" 2>/dev/null || echo 0 0 0 0); rc_cert=\$1; rc_key=\$2; rc_node_cert=\$3; rc_node_key=\$4; [ \"\$rc_cert\" -ne 0 ] && [ \"\$rc_key\" -ne 0 ] && [ \"\$rc_node_cert\" -ne 0 ] && [ \"\$rc_node_key\" -ne 0 ]"
  if [ -n "${temp_rogue:-}" ]; then
    docker rm -f "$temp_rogue" >/dev/null 2>&1 || true
  fi
  return 0
}

# M2-T8
T8_test() {
  begin_test_evidence "M2-T8" "no_unintended_entries"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "baseline entry list exists" "test -s \"$ENTRY_BEFORE\""
  exercise_guard "capture entry list after tests" \
    "after=\"$EVDIR/entries_after.txt\"; capture_entries \"\$after\""
  outcome_guard "no unintended SPIRE entries" \
    "diff -u \"$ENTRY_BEFORE\" \"$EVDIR/entries_after.txt\" >/dev/null 2>&1"
  return 0
}

M25_T1_test() {
  begin_test_evidence "M2.5-T1" "toolb_app_not_reachable"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capture edge container context" \
    "hostname >\"$EVDIR/hostname.txt\" 2>&1; ip route >\"$EVDIR/ip_route.txt\" 2>&1 || true; cat /etc/resolv.conf >\"$EVDIR/resolv.conf\" 2>&1"
  premise_guard "pin tool-b app IP (toolb_app_net)" \
    "toolb_ip=\"\$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.NetworkID}} {{.IPAddress}}{{end}}' spiffe-tool-b 2>/dev/null | cut -d' ' -f2 | head -n1)\"; test -n \"\$toolb_ip\"; echo \"\$toolb_ip\" >\"$EVDIR/toolb_ip.txt\""
  out="$EVDIR/toolb_direct.out"
  exercise_guard "attempt direct tool-b app access from edge" \
    "set +e; toolb_ip=\"\$(cat \"$EVDIR/toolb_ip.txt\" 2>/dev/null || true)\"; curl -sS --max-time 2 http://\${toolb_ip}:8080/health >\"$out\" 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\""
  outcome_guard "tool-b app not reachable from edge network" \
    "grep -Eq '(Connection refused|timed out|No route to host)' \"$out\""
  return 0
}

M25_T2_test() {
  begin_test_evidence "M2.5-T2" "missing_x_spiffe_id"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capture tool-b container context" \
    "docker exec spiffe-tool-b sh -lc 'hostname; ip route || true; cat /etc/resolv.conf' >\"$EVDIR/toolb_context.txt\" 2>&1"
  out="$EVDIR/toolb_missing_header.out"
  exercise_guard "call tool-b directly without x-spiffe-id header" \
    "docker exec -i spiffe-tool-b python - <<'PY' >\"$out\" 2>&1
import sys
import urllib.error
import urllib.request

try:
    urllib.request.urlopen(\"http://127.0.0.1:8080/secret\")
    print(\"unexpected success\")
    sys.exit(1)
except urllib.error.HTTPError as exc:
    code = exc.code
    print(code)
    sys.exit(0 if code == 401 else 1)
PY"
  outcome_guard "missing x-spiffe-id rejected by tool-b" \
    "grep -Fxq '401' \"$out\""
  return 0
}

M25_T3_test() {
  begin_test_evidence "M2.5-T3" "mismatched_x_spiffe_id"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capture edge container context" \
    "hostname >\"$EVDIR/hostname.txt\" 2>&1; ip route >\"$EVDIR/ip_route.txt\" 2>&1 || true; cat /etc/resolv.conf >\"$EVDIR/resolv.conf\" 2>&1"
  premise_guard "tool-b-envoy reachable" \
    "ensure_toolb_envoy_ready; echo \"${TOOLB_ENVOY_IP:-}\" >\"$EVDIR/toolb_envoy_ip.txt\""
  premise_guard "tool-b material available" \
    "ensure_toolb_material"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy reachable" \
    "ensure_capiss_envoy_ready; echo \"${CAPISS_ENVOY_IP:-}\" >\"$EVDIR/capiss_envoy_ip.txt\""
  mint_out="$EVDIR/mint_body.json"
  exercise_guard "mint capability as agent-a" \
    "mint_out=\"$mint_out\"; status=\"\$(mint_with_body \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_MINT_BODY\" \"\$mint_out\")\"; echo \"\$status\" >\"$EVDIR/mint_status.txt\""
  outcome_guard "mint allowed for agent-a" \
    "grep -Fxq '200' \"$EVDIR/mint_status.txt\""
  token="$(json_get '.token' "$mint_out")"
  echo "$token" >"$EVDIR/token.txt"
  out="$EVDIR/response.json"
  exercise_guard "call tool-b via envoy as rogue with agent-a token" \
    "token=\"$token\"; out=\"$out\"; status=\"\$(toolb_request \"\$CAPISS_ROGUE_CERT\" \"\$CAPISS_ROGUE_KEY\" \"\$token\" \"\$out\")\"; echo \"\$status\" >\"$EVDIR/status.txt\""
  outcome_guard "tool-b rejects mismatched x-spiffe-id/token sub" \
    "status=\"\$(cat \"$EVDIR/status.txt\" 2>/dev/null || true)\"; if [ \"\$status\" = \"403\" ]; then reason=\"\$(json_get '.reason' \"$out\")\"; [ \"\$reason\" = \"sub_mismatch\" ]; else false; fi"
  return 0
}

M3S2_T1_test() {
  begin_test_evidence "M3.S2-T1" "agent_a_mint_allowed"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint via envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint allowed 200" \
    "assert_file_eq \"$EVDIR/status.txt\" \"200\""
  out="$EVDIR/mint_body.json"
  outcome_guard "token non-empty" \
    "assert_json_present \"$out\" '.token' && jq -r '.token' \"$out\" >\"$EVDIR/token.txt\""
  outcome_guard "mint fields correct" \
    "assert_json_eq \"$out\" '.token_type' 'biscuit' && assert_json_present \"$out\" '.expires_at' && assert_json_eq \"$out\" '.issued_to' 'spiffe://example.org/agent-a' && assert_json_eq \"$out\" '.aud' 'tool-b' && assert_json_eq \"$out\" '.act' 'read' && assert_json_eq \"$out\" '.res' '/secret'"
  return 0
}

M3S2_T2_test() {
  begin_test_evidence "M3.S2-T2" "rogue_mint_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint via envoy (rogue)" \
    "mint_with_cert_to_file \"\$CAPISS_ROGUE_CERT\" \"\$CAPISS_ROGUE_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_ROGUE_CERT\" --key \"$CAPISS_ROGUE_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint denied 403" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\""
  out="$EVDIR/mint_body.json"
  outcome_guard "policy deny body" \
    "assert_json_eq \"$out\" '.error' 'denied' && assert_json_eq \"$out\" '.reason' 'policy'"
  return 0
}

M3S2_T3_test() {
  begin_test_evidence "M3.S2-T3" "opa_unreachable"
  echo "EVIDENCE_DIR=$EVDIR"
  exercise_guard "attempt OPA from edge" \
    "out=\"$EVDIR/opa_unreachable.out\"; expect_edge_unreachable \"http://opa:8181/v1/data/capiss/allow\" \"\$out\""
  outcome_guard "OPA not reachable from edge network" \
    "test -s \"$EVDIR/opa_unreachable.out\""
  return 0
}

M3S2_T4_test() {
  begin_test_evidence "M3.S2-T4" "opa_unavailable"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-no-opa-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-no-opa-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_no_opa_envoy_ip.txt\"; CAPISS_NO_OPA_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-no-opa-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_NO_OPA_ENVOY_IP}\" \"9444\" 30"
  premise_guard "capiss-no-opa-envoy health reachable" \
    "curl -sS --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-no-opa-envoy' https://${CAPISS_NO_OPA_ENVOY_IP}:9444/health >/dev/null 2>&1"
  exercise_guard "mint via no-opa envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_NO_OPA_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-no-opa-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_NO_OPA_ENVOY_IP}:9444/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint denied 403/503" \
    "assert_file_any \"$EVDIR/status.txt\" \"403\" \"503\""
  out="$EVDIR/mint_body.json"
  outcome_guard "opa unavailable body" \
    "assert_json_eq \"$out\" '.error' 'denied' && assert_json_eq \"$out\" '.reason' 'opa_unavailable'"
  return 0
}

M3S2_T5_test() {
  begin_test_evidence "M3.S2-T5" "issuer_app_not_reachable"
  echo "EVIDENCE_DIR=$EVDIR"
  exercise_guard "attempt direct issuer app access from edge" \
    "out=\"$EVDIR/capiss_app.out\"; expect_edge_unreachable \"http://capability-issuer:8000/health\" \"\$out\""
  outcome_guard "capability-issuer app not reachable from edge network" \
    "test -s \"$EVDIR/capiss_app.out\""
  return 0
}

M3S3_T1_test() {
  begin_test_evidence "M3.S3-T1" "mint_non_empty_token"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint via envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint allowed 200" \
    "assert_file_eq \"$EVDIR/status.txt\" \"200\""
  out="$EVDIR/mint_body.json"
  outcome_guard "token non-empty" \
    "assert_json_present \"$out\" '.token' && jq -r '.token' \"$out\" >\"$EVDIR/token.txt\""
  return 0
}

M3S3_T2_test() {
  begin_test_evidence "M3.S3-T2" "expires_at_near_future"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint via envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint allowed 200" \
    "assert_file_eq \"$EVDIR/status.txt\" \"200\""
  out="$EVDIR/mint_body.json"
  outcome_guard "expires_at present and near future" \
    "assert_expires_at_near \"$out\" \"$EVDIR/time.txt\" 120"
  delta="$(awk '/delta=/{print $3}' "$EVDIR/time.txt" 2>/dev/null | cut -d= -f2)"
  echo "M3.S3 T2 expires_at delta: ${delta}s"
  return 0
}

M3S3_T3_test() {
  begin_test_evidence "M3.S3-T3" "two_mints_different"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint twice via envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_1.json\" \"$EVDIR/status1.txt\"; mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_2.json\" \"$EVDIR/status2.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint allowed 200s" \
    "assert_file_eq \"$EVDIR/status1.txt\" \"200\" && assert_file_eq \"$EVDIR/status2.txt\" \"200\""
  out1="$EVDIR/mint_1.json"
  out2="$EVDIR/mint_2.json"
  outcome_guard "tokens present and different" \
    "jq -r '.token' \"$out1\" >\"$EVDIR/token1.txt\"; jq -r '.token' \"$out2\" >\"$EVDIR/token2.txt\"; [ -s \"$EVDIR/token1.txt\" ] && [ -s \"$EVDIR/token2.txt\" ] && ! cmp -s \"$EVDIR/token1.txt\" \"$EVDIR/token2.txt\"; cat \"$EVDIR/token1.txt\" \"$EVDIR/token2.txt\" >\"$EVDIR/token.txt\""
  return 0
}

M3S4_T1_test() {
  begin_test_evidence "M3.S4-T1" "identity_only_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; echo \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" \
    "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "call tool-b without token" \
    "toolb_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "no network/DNS errors" \
    "! grep -Eq '(Could not resolve host|Connection refused|No route to host)' \"$EVDIR/response.json\""
  outcome_guard "deny status 401/403" \
    "assert_file_any \"$EVDIR/status.txt\" \"401\" \"403\""
  out="$EVDIR/response.json"
  outcome_guard "reason missing_token" \
    "assert_json_eq \"$out\" '.reason' 'missing_token'"
  return 0
}

M3S4_T2_test() {
  begin_test_evidence "M3.S4-T2" "agent_a_token_access"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; echo \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" \
    "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint via envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/mint_status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint allowed 200" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\""
  mint_out="$EVDIR/mint_body.json"
  outcome_guard "mint token present" \
    "assert_json_present \"$mint_out\" '.token' && jq -r '.token' \"$mint_out\" >\"$EVDIR/token.txt\""
  token="$(json_get '.token' "$mint_out")"
  exercise_guard "call tool-b with token" \
    "toolb_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "no network/DNS errors" \
    "! grep -Eq '(Could not resolve host|Connection refused|No route to host)' \"$EVDIR/response.json\""
  outcome_guard "allow status 200" \
    "assert_file_eq \"$EVDIR/status.txt\" \"200\""
  out="$EVDIR/response.json"
  outcome_guard "secret value correct" \
    "assert_json_eq \"$out\" '.secret' 'super sensitive demo secret'"
  return 0
}

M3S4_T3_test() {
  begin_test_evidence "M3.S4-T3" "rogue_no_token_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; echo \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" \
    "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "rogue call tool-b without token" \
    "toolb_request_to_file \"\$CAPISS_ROGUE_CERT\" \"\$CAPISS_ROGUE_KEY\" \"\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "no network/DNS errors" \
    "! grep -Eq '(Could not resolve host|Connection refused|No route to host)' \"$EVDIR/response.json\""
  outcome_guard "deny status 401/403" \
    "assert_file_any \"$EVDIR/status.txt\" \"401\" \"403\""
  return 0
}

M3S4_T4_test() {
  begin_test_evidence "M3.S4-T4" "stolen_token_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; echo \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" \
    "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint via envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/mint_status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint allowed 200" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\""
  mint_out="$EVDIR/mint_body.json"
  outcome_guard "mint token present" \
    "assert_json_present \"$mint_out\" '.token' && jq -r '.token' \"$mint_out\" >\"$EVDIR/token.txt\""
  token="$(json_get '.token' "$mint_out")"
  exercise_guard "rogue uses stolen token" \
    "toolb_request_to_file \"\$CAPISS_ROGUE_CERT\" \"\$CAPISS_ROGUE_KEY\" \"\$token\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "no network/DNS errors" \
    "! grep -Eq '(Could not resolve host|Connection refused|No route to host)' \"$EVDIR/response.json\""
  outcome_guard "deny status 401/403" \
    "assert_file_any \"$EVDIR/status.txt\" \"401\" \"403\""
  out="$EVDIR/response.json"
  outcome_guard "reason sub_mismatch or invalid_token" \
    "jq -r '.reason' \"$out\" | grep -Eq '^(sub_mismatch|invalid_token)$'"
  return 0
}

M3S4_T5_test() {
  begin_test_evidence "M3.S4-T5" "expired_token_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; echo \"\$toolb_ip\" >\"$EVDIR/toolb_envoy_ip.txt\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" \
    "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint via envoy" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/mint_body.json\" \"$EVDIR/mint_status.txt\""
  exercise_guard "capture mint headers" \
    "req=\"$EVDIR/mint_request.json\"; printf '%s' \"\$CAPISS_MINT_BODY\" >\"\$req\"; curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d \"@\${req}\" https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "mint allowed 200" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\""
  mint_out="$EVDIR/mint_body.json"
  outcome_guard "mint token and expires_at present" \
    "assert_json_present \"$mint_out\" '.token' && assert_json_present \"$mint_out\" '.expires_at'"
  token="$(json_get '.token' "$mint_out")"
  expires_at="$(json_get '.expires_at' "$mint_out")"
  now="$(date +%s)"
  wait_seconds=$((expires_at - now + 1))
  if [ "$wait_seconds" -gt 0 ]; then
    sleep "$wait_seconds"
  fi
  exercise_guard "call tool-b with expired token" \
    "toolb_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "no network/DNS errors" \
    "! grep -Eq '(Could not resolve host|Connection refused|No route to host)' \"$EVDIR/response.json\""
  outcome_guard "deny status 401/403" \
    "assert_file_any \"$EVDIR/status.txt\" \"401\" \"403\""
  out="$EVDIR/response.json"
  outcome_guard "reason expired" \
    "assert_json_eq \"$out\" '.reason' 'expired'"
  return 0
}

M3S4_T6_test() {
  begin_test_evidence "M3.S4-T6" "mint_bad_request"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint with empty body" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" '{}' \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d '{}' https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "bad request 400" \
    "assert_file_eq \"$EVDIR/status.txt\" \"400\""
  out="$EVDIR/mint_body.json"
  outcome_guard "bad_request body" \
    "assert_json_eq \"$out\" '.error' 'bad_request' && assert_json_eq \"$out\" '.reason' 'aud'"
  return 0
}

M3S4_T7_test() {
  begin_test_evidence "M3.S4-T7" "mint_policy_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" \
    "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint with unapproved authority" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"write\",\"res\":\"/secret\"}' \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d '{\"aud\":\"tool-b\",\"act\":\"write\",\"res\":\"/secret\"}' https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "policy denied 403" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\""
  out="$EVDIR/mint_body.json"
  outcome_guard "policy deny body" \
    "assert_json_eq \"$out\" '.error' 'denied' && assert_json_eq \"$out\" '.reason' 'policy'"
  return 0
}

print_section "Milestone 1 - Server and agent connection and successful entry"
if [ "$RUN_M1" -eq 1 ]; then
  TEST_PREFIX="M1"
  run_test "T1" "Rogue missing join token rejects attestation" c1_test
  run_test "T2" "Rogue forged join token rejects attestation" c2_test
  run_test "T3" "Rogue replayed join token rejects attestation" c3_test
  run_test "T4" "Rogue cannot read join token" c4_test
  run_test "T5" "Only intended node entries exist" c5_test
fi

print_section "Milestone 2 - Workload identities security tests"
if [ "$RUN_M2" -eq 1 ]; then
  TEST_PREFIX="M2"
  run_test "T1" "Rogue without SVID cannot access /secret" T1_test
  run_test "T2" "Rogue with invalid client cert is rejected" T2_test
  run_test "T3" "Rogue with expired client cert is rejected" T3_test
  run_test "T4" "Rogue with wrong SPIFFE ID is rejected" T4_test
  run_test "T5" "Rogue without Workload API socket cannot fetch SVID" T5_test
  run_test "T6" "Rogue with socket but no entry cannot fetch SVID" T6_test
  run_test "T7" "Rogue cannot read SVIDs or keys" T7_test
  run_test "T8" "No unintended SPIRE entries created" T8_test
  run_test "T9" "Rogue with expired short-lived SVID is rejected" T9_test
fi

print_section "Milestone 2.5 - Envoy ingress boundary"
if [ "$RUN_M25" -eq 1 ]; then
  TEST_PREFIX="M2.5"
  run_test "T1" "tool-b app not reachable from edge network" M25_T1_test
  run_test "T2" "tool-b rejects missing x-spiffe-id header" M25_T2_test
  run_test "T3" "tool-b rejects mismatched x-spiffe-id header" M25_T3_test
fi

print_section "M3.S2 — OPA-gated capability minting"
if [ "$RUN_M3" -eq 1 ]; then
  TEST_PREFIX="M3.S2"
  run_test "T1" "agent-a can mint (allowed by OPA)" M3S2_T1_test
  run_test "T2" "rogue mint denied by policy" M3S2_T2_test
  run_test "T3" "OPA is not reachable from edge" M3S2_T3_test
  run_test "T4" "Fail closed when OPA is unavailable" M3S2_T4_test
  run_test "T5" "Issuer denies when x-spiffe-id missing (structural guard)" M3S2_T5_test
fi

print_section "M3.S3 — Biscuit minting"
if [ "$RUN_M3" -eq 1 ]; then
  TEST_PREFIX="M3.S3"
  run_test "T1" "mint returns non-empty token" M3S3_T1_test
  run_test "T2" "expires_at is present and in the near future" M3S3_T2_test
  run_test "T3" "two mints produce different tokens" M3S3_T3_test
fi

print_section "M3.S4 — tool-b enforces capability tokens"
if [ "$RUN_M3" -eq 1 ]; then
  TEST_PREFIX="M3.S4"
  run_test "T1" "identity-only access to /secret is denied" M3S4_T1_test
  run_test "T2" "agent-a can access /secret with minted capability" M3S4_T2_test
  run_test "T3" "rogue cannot access /secret without token" M3S4_T3_test
  run_test "T4" "stolen token replay by rogue is rejected" M3S4_T4_test
  run_test "T5" "expired token is rejected" M3S4_T5_test
  run_test "T6" "mint rejects missing parameters" M3S4_T6_test
  run_test "T7" "mint denies unapproved authority request" M3S4_T7_test
fi

printf '\nTotal: %d  Passed: %d  Failed: %d\n' "$TOTAL" "$PASSED" "$FAILED"
if [ "$FAILED" -ne 0 ]; then
  exit 1
fi
