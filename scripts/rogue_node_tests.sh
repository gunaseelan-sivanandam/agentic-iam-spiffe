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
CURRENT_TEST_ID=""
WARNING_TOTAL=0
WARNINGS_FILE="/tmp/rogue_test_warnings.tsv"

: > "$WARNINGS_FILE"

PROFILE_ENABLED="${TEST_PROFILE:-1}"
PROFILE_BASE="${ROGUE_TEST_EVIDENCE_DIR:-/tmp/rogue-tests}"
PROFILE_FILE="${PROFILE_BASE}/guard_timings.tsv"
PROFILE_SUMMARY_FILE="${PROFILE_BASE}/guard_timings_top25.txt"

if [ "$PROFILE_ENABLED" = "1" ]; then
  mkdir -p "$PROFILE_BASE"
  printf 'duration_ms\ttest_id\tguard_type\tstep_index\tstatus\tmessage\n' >"$PROFILE_FILE"
fi

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
RUN_M4=1
RUN_M4A=1
RUN_M4B=1
RUN_M5=1

if [ -n "${TEST_MILESTONES:-}" ]; then
  RUN_M1=0
  RUN_M2=0
  RUN_M25=0
  RUN_M3=0
  RUN_M4=0
  RUN_M4A=0
  RUN_M4B=0
  RUN_M5=0
  for token in $(printf '%s' "$TEST_MILESTONES" | tr ',' ' '); do
    case "$token" in
      m1|M1) RUN_M1=1 ;;
      m2|M2) RUN_M2=1 ;;
      m25|M2.5|M2_5) RUN_M25=1 ;;
      m3|M3) RUN_M3=1 ;;
      m4|M4) RUN_M4=1 ;;
      m4a|M4a|M4A) RUN_M4A=1 ;;
      m4b|M4b|M4B) RUN_M4B=1 ;;
      m5|M5) RUN_M5=1 ;;
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

epoch_ms() {
  ms="$(date +%s%3N 2>/dev/null || true)"
  case "$ms" in
    ''|*[!0-9]*)
      s="$(date +%s)"
      ms=$((s * 1000))
      ;;
  esac
  printf '%s\n' "$ms"
}

append_guard_timing() {
  guard_type="$1"
  idx="$2"
  status="$3"
  duration_ms="$4"
  msg="$5"
  safe_msg="$(printf '%s' "$msg" | tr '\t\r\n' '   ')"
  test_id="${CURRENT_TEST_ID:-unknown}"
  if [ -n "${EVDIR:-}" ]; then
    ev_timing="${EVDIR}/guard_timings.tsv"
    if [ ! -f "$ev_timing" ]; then
      printf 'duration_ms\ttest_id\tguard_type\tstep_index\tstatus\tmessage\n' >"$ev_timing"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$duration_ms" "$test_id" "$guard_type" "$idx" "$status" "$safe_msg" >>"$ev_timing"
  fi
  if [ "$PROFILE_ENABLED" = "1" ]; then
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$duration_ms" "$test_id" "$guard_type" "$idx" "$status" "$safe_msg" >>"$PROFILE_FILE"
  fi
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
  CURRENT_TEST_ID="$full_id"
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
  test_warnings_file="/tmp/rogue_test_current_warnings.txt"
  grep -F "${CURRENT_TEST_ID}	" "$WARNINGS_FILE" >"$test_warnings_file" 2>/dev/null || true
  warning_count="$(wc -l <"$test_warnings_file" | tr -d ' ')"
  if [ "$rc" -eq 0 ]; then
    PASSED=$((PASSED + 1))
    print_result "$id" "$name" "PASS" "$GREEN"
    if [ "$warning_count" -gt 0 ]; then
      printf '  Warnings: %s\n' "$warning_count"
      sed 's/^[^\t]*\t/  Warning: /' "$test_warnings_file"
    fi
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
  rm -f "$test_warnings_file"
  CURRENT_TEST_ID=""
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

text_matches() {
  file="$1"
  regex="$2"
  grep -Eq "$regex" "$file"
}

add_warning() {
  msg="$1"
  WARNING_TOTAL=$((WARNING_TOTAL + 1))
  printf '%s\t%s\n' "${CURRENT_TEST_ID:-unknown}" "$msg" >>"$WARNINGS_FILE"
  if [ -n "${EVDIR:-}" ]; then
    idx="$(ls "${EVDIR}"/warning_reason_*.txt 2>/dev/null | wc -l | tr -d ' ')"
    idx=$((idx + 1))
    printf '%s\n' "$msg" >"${EVDIR}/warning_reason_${idx}.txt" 2>/dev/null || true
    printf '[%s] WARNING: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" >>"${EVDIR}/notes.txt" 2>/dev/null || true
  fi
}

premise_guard() {
  guard_type="premise"
  msg="$1"
  cmd="$2"
  if [ -z "${EVDIR:-}" ]; then
    set_reason "PREMISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  idx="$(ls "${EVDIR}"/"${guard_type}"_*.txt 2>/dev/null | wc -l | tr -d ' ')"
  idx=$((idx + 1))
  guard_out="${EVDIR}/${guard_type}_${idx}.txt"
  ev_save_cmd "${guard_type}_${idx}" "$cmd"
  start_ms="$(epoch_ms)"
  if eval "$cmd" >"$guard_out" 2>&1; then
    end_ms="$(epoch_ms)"
    append_guard_timing "$guard_type" "$idx" "PASS" "$((end_ms - start_ms))" "$msg"
    return 0
  else
    end_ms="$(epoch_ms)"
    append_guard_timing "$guard_type" "$idx" "FAIL" "$((end_ms - start_ms))" "$msg"
    set_reason "PREMISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
}

exercise_guard() {
  guard_type="exercise"
  msg="$1"
  cmd="$2"
  if [ -z "${EVDIR:-}" ]; then
    set_reason "EXERCISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  idx="$(ls "${EVDIR}"/"${guard_type}"_*.txt 2>/dev/null | wc -l | tr -d ' ')"
  idx=$((idx + 1))
  guard_out="${EVDIR}/${guard_type}_${idx}.txt"
  ev_save_cmd "${guard_type}_${idx}" "$cmd"
  start_ms="$(epoch_ms)"
  if eval "$cmd" >"$guard_out" 2>&1; then
    end_ms="$(epoch_ms)"
    append_guard_timing "$guard_type" "$idx" "PASS" "$((end_ms - start_ms))" "$msg"
    return 0
  else
    end_ms="$(epoch_ms)"
    append_guard_timing "$guard_type" "$idx" "FAIL" "$((end_ms - start_ms))" "$msg"
    set_reason "EXERCISE FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
}

outcome_guard() {
  guard_type="outcome"
  msg="$1"
  cmd="$2"
  if [ -z "${EVDIR:-}" ]; then
    set_reason "OUTCOME FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
  idx="$(ls "${EVDIR}"/"${guard_type}"_*.txt 2>/dev/null | wc -l | tr -d ' ')"
  idx=$((idx + 1))
  guard_out="${EVDIR}/${guard_type}_${idx}.txt"
  ev_save_cmd "${guard_type}_${idx}" "$cmd"
  start_ms="$(epoch_ms)"
  if eval "$cmd" >"$guard_out" 2>&1; then
    end_ms="$(epoch_ms)"
    append_guard_timing "$guard_type" "$idx" "PASS" "$((end_ms - start_ms))" "$msg"
    return 0
  else
    end_ms="$(epoch_ms)"
    append_guard_timing "$guard_type" "$idx" "FAIL" "$((end_ms - start_ms))" "$msg"
    set_reason "OUTCOME FAILED: $msg"
    GUARD_FAILED=1
    return 1
  fi
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
  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\([^/:]*\).*#\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\([0-9]*\).*#\1#p')"
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
      jira-tool-envoy)
        container="spiffe-jira-tool-envoy"
        network_suffix="jiratool_edge_net"
        ;;
      jira-mock)
        container="spiffe-jira-mock"
        network_suffix="jiratool_upstream_net"
        ;;
      jira-mcp-envoy)
        container="spiffe-jira-mcp-envoy"
        network_suffix="jiramcp_edge_net"
        ;;
      jira-mcp-mock)
        container="spiffe-jira-mcp-mock"
        network_suffix="jiramcp_upstream_net"
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
  attestation_wait_retries=60

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

  # Wait up to 60s for the rogue agent process to finish, then classify the final log.
  i=0
  while [ $i -lt "$attestation_wait_retries" ]; do
    if ! kill -0 "$pid" >/dev/null 2>&1; then
      break
    fi
    i=$((i + 1))
    sleep 1
  done

  if kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    wait "$pid" >/dev/null 2>&1 || true
  else
    wait "$pid" >/dev/null 2>&1 || true
  fi

  ev_copy_if_exists "$log_file" "rogue_${label}.log"
  ev_copy_if_exists "$temp_config" "rogue_${label}.conf"

  if [ $i -ge "$attestation_wait_retries" ]; then
    ev_note "timed out waiting for attestation outcome (no explicit attestation success/failure observed)"
    set_reason "timed out waiting for attestation outcome (no explicit attestation success/failure observed)"
    return 1
  fi

  if text_contains "$log_file" "Node attestation was successful"; then
    set_reason "rogue attestation succeeded"
    return 1
  fi

  if text_contains "$log_file" "attestation failed" ||
    text_contains "$log_file" "permission denied" ||
    text_contains "$log_file" "invalid token" ||
    text_contains "$log_file" "unauthorized" ||
    text_contains "$log_file" "join token was not provided" ||
    text_contains "$log_file" "join token does not exist"; then
    return 0
  fi

  if text_contains "$log_file" "Agent crashed"; then
    set_reason "rogue agent crashed without explicit attestation denial"
    return 1
  fi

  set_reason "no explicit attestation denial observed"
  return 1
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
CAPISS_AGENT_BUNDLE=""
CAPISS_ROGUE_CERT=""
CAPISS_ROGUE_KEY=""
CAPISS_ROGUE_BUNDLE=""
JIRAMCP_READY=0
JIRAMCP_REASON=""
JIRAMCP_ADAPTER_CERT=""
JIRAMCP_ADAPTER_KEY=""
JIRAMCP_ADAPTER_BUNDLE=""
CAPISS_MINT_URL="https://capability-issuer-envoy:9443/capabilities/mint"
CAPISS_ROOT_MINT_URL="https://capability-issuer-envoy:9443/capabilities/root-mint"
CAPISS_RESOURCE_MINT_URL="https://capability-issuer-envoy:9443/capabilities/resource-mint"
CAPISS_NO_OPA_URL="https://capability-issuer-no-opa-envoy:9444/capabilities/mint"
TOOLB_SECRET_URL="https://tool-b-envoy:8443/secret"
TOOLB_SEARCH_URL="https://tool-b-envoy:8443/search"
TOOLB_READ_FILE_URL_PREFIX="https://tool-b-envoy:8443/read-file"
JIRA_TOOL_ISSUE_URL_PREFIX="https://jira-tool-envoy:10443/jira/rest/api/3/issue"
JIRA_MOCK_URL="http://jira-mock:8080"
CAPISS_MINT_BODY='{"aud":"tool-b","act":"read","res":"tool-b:/secret"}'
CAPISS_SEARCH_MINT_BODY='{"aud":"tool-b","act":"read","res":"tool-b:/search"}'
JIRA_IAM_MINT_BODY='{"aud":"jira-tool","act":"read","res":"jira-tool:/project:IAM"}'
JIRA_IAM_WRITE_MINT_BODY='{"aud":"jira-tool","act":"write","res":"jira-tool:/project:IAM"}'
JIRA_NAS_MINT_BODY='{"aud":"jira-tool","act":"read","res":"jira-tool:/project:NAS"}'
JIRA_NAS_WRITE_MINT_BODY='{"aud":"jira-tool","act":"write","res":"jira-tool:/project:NAS"}'
JIRA_MCP_URL="https://jira-mcp-envoy:11443"
JIRA_MCP_SUMMARY_URL="${JIRA_MCP_URL}/mcp/jira/project-summary"
JIRA_MCP_STORIES_URL="${JIRA_MCP_URL}/mcp/jira/stories"
JIRA_MCP_MOCK_URL="http://jira-mcp-mock:8080"
JIRA_MCP_IAM_SUMMARY_MINT_BODY='{"aud":"jira-mcp-gateway","act":"read_project_summary","res":"jira-mcp:/project:IAM"}'
JIRA_MCP_IAM_CREATE_MINT_BODY='{"aud":"jira-mcp-gateway","act":"create_story","res":"jira-mcp:/project:IAM"}'
JIRA_MCP_NAS_SUMMARY_MINT_BODY='{"aud":"jira-mcp-gateway","act":"read_project_summary","res":"jira-mcp:/project:NAS"}'
JIRA_MCP_UNSUPPORTED_MINT_BODY='{"aud":"jira-mcp-gateway","act":"update_story","res":"jira-mcp:/project:IAM"}'

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
  bundle="$tmpdir/${service_name}_bundle.pem"
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
  if [ -s "$outdir/bundle.pem" ]; then
    cp "$outdir/bundle.pem" "$bundle"
  elif [ -s "$outdir/bundle.0.pem" ]; then
    cp "$outdir/bundle.0.pem" "$bundle"
  else
    set_reason "missing trust bundle for ${service_name}"
    return 1
  fi

  CLIENT_CERT="$cert"
  CLIENT_KEY="$key"
  CLIENT_BUNDLE="$bundle"
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
  CAPISS_AGENT_BUNDLE="$CLIENT_BUNDLE"

  if ! prepare_client_material "rogue" "$tmpdir"; then
    CAPISS_READY=-1
    CAPISS_REASON="$FAIL_REASON"
    set_reason "$FAIL_REASON"
    return 1
  fi
  CAPISS_ROGUE_CERT="$CLIENT_CERT"
  CAPISS_ROGUE_KEY="$CLIENT_KEY"
  CAPISS_ROGUE_BUNDLE="$CLIENT_BUNDLE"

  CAPISS_READY=1
  ev_copy_if_exists "${CAPISS_AGENT_CERT:-}" "agent-a_svid.pem"
  ev_copy_if_exists "${CAPISS_ROGUE_CERT:-}" "rogue_svid.pem"
  return 0
}

ensure_jiramcp_material() {
  if [ "$JIRAMCP_READY" -eq 1 ]; then
    ev_copy_if_exists "${JIRAMCP_ADAPTER_CERT:-}" "codex-jira-mcp-adapter_svid.pem"
    return 0
  fi
  if [ "$JIRAMCP_READY" -eq -1 ]; then
    set_reason "$JIRAMCP_REASON"
    return 1
  fi

  tmpdir="/tmp/jiramcp_material"
  rm -rf "$tmpdir"
  mkdir -p "$tmpdir"

  if ! prepare_client_material "codex-jira-mcp-adapter" "$tmpdir"; then
    JIRAMCP_READY=-1
    JIRAMCP_REASON="$FAIL_REASON"
    set_reason "$FAIL_REASON"
    return 1
  fi
  JIRAMCP_ADAPTER_CERT="$CLIENT_CERT"
  JIRAMCP_ADAPTER_KEY="$CLIENT_KEY"
  JIRAMCP_ADAPTER_BUNDLE="$CLIENT_BUNDLE"

  JIRAMCP_READY=1
  ev_copy_if_exists "${JIRAMCP_ADAPTER_CERT:-}" "codex-jira-mcp-adapter_svid.pem"
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
  if [ -n "${CAPISS_AGENT_CERT:-}" ] && [ -n "${CAPISS_AGENT_KEY:-}" ]; then
    start="$(date +%s)"
    err_file="/tmp/capiss_health.err"
    echo "[gate] capability-issuer-envoy health check"
    while true; do
      status="$(curl -sS --insecure --cert "$CAPISS_AGENT_CERT" --key "$CAPISS_AGENT_KEY" \
        --resolve "capability-issuer-envoy:9443:${CAPISS_ENVOY_IP}" \
        -o /dev/null -w '%{http_code}' \
        https://capability-issuer-envoy:9443/health 2>"$err_file" || true)"
      if [ "$status" = "200" ]; then
        echo "[gate] capability-issuer-envoy health OK"
        return 0
      fi
      now="$(date +%s)"
      if [ $((now - start)) -ge 30 ]; then
        set_reason "capability-issuer-envoy health not ready in 30s: status=${status:-none} err=$(cat "$err_file" 2>/dev/null || true)"
        return 1
      fi
      sleep 0.5
    done
  fi
  return 0
}

ensure_jira_envoy_ready() {
  if ! wait_dns "jira-tool-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "jira-tool-envoy" "10443" 30; then
    return 1
  fi
  JIRA_ENVOY_IP="$(wait_resolve_ip "jira-tool-envoy" 30 || true)"
  if [ -z "${JIRA_ENVOY_IP:-}" ]; then
    set_reason "failed to resolve jira-tool-envoy IP"
    return 1
  fi
  return 0
}

ensure_jira_mcp_envoy_ready() {
  if ! wait_dns "jira-mcp-envoy" 30; then
    return 1
  fi
  if ! wait_tcp "jira-mcp-envoy" "11443" 30; then
    return 1
  fi
  JIRA_MCP_ENVOY_IP="$(wait_resolve_ip "jira-mcp-envoy" 30 || true)"
  if [ -z "${JIRA_MCP_ENVOY_IP:-}" ]; then
    set_reason "failed to resolve jira-mcp-envoy IP"
    return 1
  fi
  return 0
}

expected_spiffe_for_host() {
  case "$1" in
    capability-issuer-envoy) printf '%s\n' 'spiffe://varambu.org/capability-issuer-envoy' ;;
    capability-issuer-no-opa-envoy) printf '%s\n' 'spiffe://varambu.org/capability-issuer-no-opa-envoy' ;;
    tool-b-envoy) printf '%s\n' 'spiffe://varambu.org/tool-b-envoy' ;;
    jira-tool-envoy) printf '%s\n' 'spiffe://varambu.org/jira-tool-envoy' ;;
    jira-mcp-envoy) printf '%s\n' 'spiffe://varambu.org/jira-mcp-envoy' ;;
    *) return 1 ;;
  esac
}

record_verified_identity() {
  host="$1"
  result="$2"
  spiffe_id="$3"
  if [ -z "${EVDIR:-}" ]; then
    return 0
  fi
  case "$host" in
    capability-issuer-envoy|capability-issuer-no-opa-envoy)
      printf '%s' "$result" >"$EVDIR/verified_capiss_result.txt" 2>/dev/null || true
      printf '%s' "$spiffe_id" >"$EVDIR/verified_capiss_spiffe_id.txt" 2>/dev/null || true
      ;;
    tool-b-envoy)
      printf '%s' "$result" >"$EVDIR/verified_toolb_result.txt" 2>/dev/null || true
      printf '%s' "$spiffe_id" >"$EVDIR/verified_toolb_spiffe_id.txt" 2>/dev/null || true
      ;;
    jira-tool-envoy)
      printf '%s' "$result" >"$EVDIR/verified_jiratool_result.txt" 2>/dev/null || true
      printf '%s' "$spiffe_id" >"$EVDIR/verified_jiratool_spiffe_id.txt" 2>/dev/null || true
      ;;
    jira-mcp-envoy)
      printf '%s' "$result" >"$EVDIR/verified_jiramcp_result.txt" 2>/dev/null || true
      printf '%s' "$spiffe_id" >"$EVDIR/verified_jiramcp_spiffe_id.txt" 2>/dev/null || true
      ;;
  esac
}

write_verified_timing() {
  status="$1"
  duration_ms="$2"
  if [ -z "${CURL_TIMING_OUT:-}" ]; then
    return 0
  fi
  total_s="$(awk "BEGIN {printf \"%.3f\", ${duration_ms}/1000}")"
  printf 'http_code=%s time_namelookup=0 time_connect=0 time_appconnect=0 time_starttransfer=0 time_total=%s\n' \
    "$status" "$total_s" >"$CURL_TIMING_OUT" 2>/dev/null || true
  if [ -n "${CURL_TIMING_RAW_OUT:-}" ]; then
    cat "$CURL_TIMING_OUT" >"$CURL_TIMING_RAW_OUT" 2>/dev/null || true
  fi
  if [ -n "${CURL_STATUS_DEBUG:-}" ]; then
    {
      echo "parsed_status=${status}"
      echo "timing_out_path=${CURL_TIMING_OUT}"
      echo "timing_total_seconds=${total_s}"
    } >"$CURL_STATUS_DEBUG" 2>/dev/null || true
  fi
}

verified_https_request() {
  cert="$1"
  key="$2"
  cafile="$3"
  url="$4"
  method="$5"
  body="$6"
  bearer="$7"
  out="$8"
  : >"$out"

  host="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://\([^/:]*\).*#\1#p')"
  port="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/:]*:\([0-9]*\).*#\1#p')"
  path="$(printf '%s' "$url" | sed -n 's#^[a-zA-Z]*://[^/]*\(/.*\)$#\1#p')"
  if [ -z "$path" ]; then
    path="/"
  fi

  expected_spiffe="$(expected_spiffe_for_host "$host" || true)"
  if [ -z "$expected_spiffe" ]; then
    record_verified_identity "$host" "fail" ""
    printf '%s' ""
    return 0
  fi
  if [ ! -s "$cafile" ] || [ -z "$cert" ] || [ -z "$key" ]; then
    record_verified_identity "$host" "fail" ""
    printf '%s' ""
    return 0
  fi

  req_file="$(mktemp)"
  body_file="$(mktemp)"
  http_file="$(mktemp)"
  http_norm_file="$(mktemp)"
  diag_file="$(mktemp)"
  server_cert="$(mktemp)"

  if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
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

  if [ "${DEBUG_RESOLVE:-}" = "1" ]; then
    printf '[debug] verified_https_request url=%s host=%s port=%s path=%s expected_spiffe=%s\n' \
      "$url" "$host" "$port" "$path" "$expected_spiffe" >&2
  fi

  start_ms="$(epoch_ms)"
  set +e
  $TIMEOUT_BIN 20s openssl s_client $TLS_CLIENT_ARGS \
    -connect "${host}:${port}" \
    -servername "$host" \
    -cert "$cert" \
    -key "$key" \
    -CAfile "$cafile" \
    -verify_return_error \
    -showcerts \
    -ign_eof \
    <"$req_file" >"$http_file" 2>"$diag_file"
  rc=$?
  set -e
  end_ms="$(epoch_ms)"

  actual_spiffe=""
  if awk 'BEGIN{p=0} /BEGIN CERTIFICATE/{p=1} p{print} /END CERTIFICATE/{exit}' "$diag_file" >"$server_cert" 2>/dev/null &&
    [ -s "$server_cert" ]; then
    actual_spiffe="$(openssl x509 -in "$server_cert" -noout -ext subjectAltName 2>/dev/null | sed -n 's/.*URI:\(spiffe:[^,]*\).*/\1/p' | head -n 1)"
  elif awk 'BEGIN{p=0} /BEGIN CERTIFICATE/{p=1} p{print} /END CERTIFICATE/{exit}' "$http_file" >"$server_cert" 2>/dev/null &&
    [ -s "$server_cert" ]; then
    actual_spiffe="$(openssl x509 -in "$server_cert" -noout -ext subjectAltName 2>/dev/null | sed -n 's/.*URI:\(spiffe:[^,]*\).*/\1/p' | head -n 1)"
  fi

  verify_result="fail"
  if [ "$rc" -eq 0 ] &&
    grep -Eq 'Verification: OK|Verify return code: 0 \(ok\)' "$diag_file" "$http_file" &&
    [ "$actual_spiffe" = "$expected_spiffe" ]; then
    verify_result="ok"
  fi
  record_verified_identity "$host" "$verify_result" "$actual_spiffe"

  tr -d '\r' <"$http_file" >"$http_norm_file" 2>/dev/null || true

  status="$(awk '/^HTTP\//{print $2; exit}' "$http_norm_file")"
  if [ -z "$status" ]; then
    status="$(tr -d '\r' <"$diag_file" | awk '/^HTTP\//{print $2; exit}')"
  fi
  write_verified_timing "$status" "$((end_ms - start_ms))"

  body_start_line="$(awk '
    BEGIN {http=0}
    /^HTTP\// {http=1; next}
    http && /^$/ {print NR + 1; exit}
  ' "$http_norm_file")"
  content_length="$(awk '
    BEGIN {IGNORECASE=1}
    /^Content-Length:/ {gsub(/^[^:]*:[[:space:]]*/, "", $0); print $0; exit}
  ' "$http_norm_file")"

  if [ -n "$body_start_line" ] && printf '%s' "$content_length" | grep -Eq '^[0-9]+$'; then
    tail -n +"$body_start_line" "$http_norm_file" | head -c "$content_length" >"$out" 2>/dev/null || true
  fi

  if [ ! -s "$out" ]; then
    awk '
      BEGIN {http=0; body=0}
      /^HTTP\// {http=1; next}
      http && body==0 && /^$/ {body=1; next}
      http && body==1 {print}
    ' "$http_norm_file" >"$out" 2>/dev/null || true
  fi

  if [ ! -s "$out" ]; then
    tr -d '\r' <"$diag_file" | awk '
      BEGIN {http=0; body=0}
      /^HTTP\// {http=1; next}
      http && body==0 && /^$/ {body=1; next}
      http && body==1 {print}
    ' >"$out" 2>/dev/null || true
  fi

  rm -f "$req_file" "$body_file" "$http_file" "$http_norm_file" "$diag_file" "$server_cert"
  printf '%s' "$status"
}

mint_with_cert() {
  cert="$1"
  key="$2"
  url="$3"
  out="$4"
  verified_https_request "$cert" "$key" "${CAPISS_AGENT_BUNDLE:-${CAPISS_ROGUE_BUNDLE:-}}" \
    "$url" "POST" "$CAPISS_MINT_BODY" "" "$out"
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
  verified_https_request "$cert" "$key" "${CAPISS_AGENT_BUNDLE:-${CAPISS_ROGUE_BUNDLE:-}}" \
    "$url" "POST" "$body" "" "$out"
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

mint_with_body_auth() {
  cert="$1"
  key="$2"
  url="$3"
  body="$4"
  bearer="$5"
  out="$6"
  verified_https_request "$cert" "$key" "${CAPISS_AGENT_BUNDLE:-${CAPISS_ROGUE_BUNDLE:-}}" \
    "$url" "POST" "$body" "$bearer" "$out"
}

mint_with_body_auth_to_file() {
  cert="$1"
  key="$2"
  url="$3"
  body="$4"
  bearer="$5"
  out="$6"
  status_file="$7"
  status="$(mint_with_body_auth "$cert" "$key" "$url" "$body" "$bearer" "$out")"
  printf '%s' "$status" >"$status_file"
}

toolb_request() {
  toolb_request_url "$1" "$2" "$3" "$TOOLB_SECRET_URL" "$4"
}

toolb_request_url() {
  cert="$1"
  key="$2"
  token="$3"
  url="$4"
  out="$5"
  verified_https_request "$cert" "$key" "$TOOLB_BUNDLE" "$url" "GET" "" "$token" "$out"
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

jiratool_request_to_file() {
  cert="$1"
  key="$2"
  token="$3"
  issue_key="$4"
  out="$5"
  status_file="$6"
  status="$(verified_https_request "$cert" "$key" "${CAPISS_AGENT_BUNDLE:-${CAPISS_ROGUE_BUNDLE:-}}" \
    "${JIRA_TOOL_ISSUE_URL_PREFIX}/${issue_key}" "GET" "" "$token" "$out")"
  printf '%s' "$status" >"$status_file"
}

jiratool_put_to_file() {
  cert="$1"
  key="$2"
  token="$3"
  issue_key="$4"
  body="$5"
  out="$6"
  status_file="$7"
  status="$(verified_https_request "$cert" "$key" "${CAPISS_AGENT_BUNDLE:-${CAPISS_ROGUE_BUNDLE:-}}" \
    "${JIRA_TOOL_ISSUE_URL_PREFIX}/${issue_key}" "PUT" "$body" "$token" "$out")"
  printf '%s' "$status" >"$status_file"
}

jira_mock_reset() {
  curl -sS -X POST "${JIRA_MOCK_URL}/__test__/reset" >/dev/null
}

jira_mock_request_log() {
  out="$1"
  curl -sS "${JIRA_MOCK_URL}/__test__/requests" >"$out"
}

jira_mcp_mock_reset() {
  curl -sS -X POST "${JIRA_MCP_MOCK_URL}/__test__/reset" >/dev/null
}

jira_mcp_mock_request_log() {
  out="$1"
  curl -sS "${JIRA_MCP_MOCK_URL}/__test__/requests" >"$out"
}

jira_mcp_mock_created() {
  out="$1"
  curl -sS "${JIRA_MCP_MOCK_URL}/__test__/created" >"$out"
}

jira_mcp_mock_breadth() {
  out="$1"
  curl -sS "${JIRA_MCP_MOCK_URL}/__test__/breadth" >"$out"
}

jira_mcp_mock_fail_next_create() {
  curl -sS -X POST "${JIRA_MCP_MOCK_URL}/__test__/fail_next_create" >/dev/null
}

jira_mcp_mint_with_body_to_file() {
  body="$1"
  out="$2"
  status_file="$3"
  status="$(verified_https_request "$JIRAMCP_ADAPTER_CERT" "$JIRAMCP_ADAPTER_KEY" "$JIRAMCP_ADAPTER_BUNDLE" \
    "$CAPISS_ROOT_MINT_URL" "POST" "$body" "" "$out")"
  printf '%s' "$status" >"$status_file"
}

jira_mcp_request_to_file() {
  token="$1"
  url="$2"
  body="$3"
  out="$4"
  status_file="$5"
  status="$(verified_https_request "$JIRAMCP_ADAPTER_CERT" "$JIRAMCP_ADAPTER_KEY" "$JIRAMCP_ADAPTER_BUNDLE" \
    "$url" "POST" "$body" "$token" "$out")"
  printf '%s' "$status" >"$status_file"
}

jira_mcp_rogue_request_to_file() {
  token="$1"
  url="$2"
  body="$3"
  out="$4"
  status_file="$5"
  status="$(verified_https_request "$CAPISS_ROGUE_CERT" "$CAPISS_ROGUE_KEY" "$CAPISS_ROGUE_BUNDLE" \
    "$url" "POST" "$body" "$token" "$out")"
  printf '%s' "$status" >"$status_file"
}

mcp_launcher_message() {
  message="$1"
  out="$2"
  err="$3"
  (cd /repo && printf '%s\n' "$message" | COMPOSE_FILE=compose/spiffe.compose.yml scripts/codex_jira_mcp.sh >"$out" 2>"$err")
}

mcp_tool_call() {
  tool="$1"
  args_json="$2"
  out="$3"
  err="$4"
  msg="$(jq -cn --arg tool "$tool" --argjson args "$args_json" '{jsonrpc:"2.0",id:1,method:"tools/call",params:{name:$tool,arguments:$args}}')"
  mcp_launcher_message "$msg" "$out" "$err"
}

mcp_text_json_to_file() {
  in_file="$1"
  out_file="$2"
  jq -r '.result.content[0].text' "$in_file" | jq . >"$out_file"
}

# --- M5 full-chain trace (ARCH-033) E2E helpers ---------------------------
# Invoke an MCP tool through the adapter while injecting the per-session audit
# destination, so the adapter writes its independent adapter_request/decision
# legs into <session>/adapter_audit.jsonl (bind-mounted /var/audit/<rel>).
mcp_tool_call_traced() {
  tool="$1"
  args_json="$2"
  out="$3"
  err="$4"
  sess_rel="$5"
  msg="$(jq -cn --arg tool "$tool" --argjson args "$args_json" '{jsonrpc:"2.0",id:1,method:"tools/call",params:{name:$tool,arguments:$args}}')"
  (cd /repo && printf '%s\n' "$msg" \
    | docker compose -f compose/spiffe.compose.yml exec -T \
        -e VARAMBU_AUDIT_ROOT=/var/audit -e VARAMBU_SESSION_REL="$sess_rel" \
        codex-jira-mcp-adapter python /app/server.py >"$out" 2>"$err")
}

# Correlation id the adapter returned in the MCP tool result.
mcp_cid() {
  jq -r '.result.content[0].text | fromjson | .correlation_id' "$1"
}

# Reset the mock with a short retry: m5_ready performs an in-band `docker run`
# (SVID fetch) that can transiently flush the harness container's embedded DNS,
# so the immediately-following jira-mcp-mock resolution may need a moment.
trace_mock_reset() {
  i=1
  while [ "$i" -le 8 ]; do
    if curl -sS -X POST "${JIRA_MCP_MOCK_URL}/__test__/reset" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

# Start the capiss + gateway docker-logs tailers for one session.
trace_start_tailers() {
  sess="$1"
  since="$2"
  : >"$sess/capiss_audit.jsonl"; : >"$sess/capiss_audit.log"
  python3 /repo/scripts/varambu_audit.py tail --since "$since" \
    --jsonl "$sess/capiss_audit.jsonl" --human "$sess/capiss_audit.log" \
    --err "$sess/audit_tailer.err" >/dev/null 2>>"$sess/audit_tailer.err" &
  echo $! >"$sess/audit_tailer.pid"
  : >"$sess/gateway_audit.jsonl"; : >"$sess/gateway_audit.log"
  python3 /repo/scripts/varambu_audit.py tail --since "$since" \
    --jsonl "$sess/gateway_audit.jsonl" --human "$sess/gateway_audit.log" \
    --err "$sess/gateway_tailer.err" --container spiffe-jira-mcp-gateway --source gateway \
    >/dev/null 2>>"$sess/gateway_tailer.err" &
  echo $! >"$sess/gateway_tailer.pid"
  sleep 2
  kill -0 "$(cat "$sess/audit_tailer.pid")" && kill -0 "$(cat "$sess/gateway_tailer.pid")"
}

trace_stop_tailers() {
  sess="$1"
  kill "$(cat "$sess/audit_tailer.pid")" 2>/dev/null || true
  kill "$(cat "$sess/gateway_tailer.pid")" 2>/dev/null || true
}

# Synthetic codex-cli rollout records (validated 0.139.0 shape). The correlation
# id is templated from the live call so the agent-attested intent joins the real
# in-boundary legs by correlation_id.
rollout_user() {
  jq -cn --arg m "$1" '{type:"event_msg",timestamp:"2026-06-19T10:00:00.000Z",payload:{type:"user_message",message:$m}}'
}
rollout_call() {
  jq -cn --arg n "$1" --arg c "$2" --argjson a "$3" \
    '{type:"response_item",timestamp:"2026-06-19T10:00:01.000Z",payload:{type:"function_call",name:$n,call_id:$c,arguments:($a|tojson),namespace:"jira-mcp"}}'
}
rollout_output() {
  jq -cn --arg c "$1" --arg cid "$2" --argjson ok "$3" \
    '{type:"response_item",timestamp:"2026-06-19T10:00:02.000Z",payload:{type:"function_call_output",call_id:$c,output:({ok:$ok,correlation_id:$cid}|tojson)}}'
}

# Build a fully populated, isolated synthetic trace session (no shared docker
# log streams) for deterministic CLI-surface assertions. Mirrors the synthetic
# fixture approach used by the varambu audit CLI tests (M5-T44).
write_synth_trace_session() {
  sess="$1"
  cid="$2"
  prompt="$3"
  mkdir -p "$sess/codex-home/sessions/2026/06/19"
  jq -cn --arg c "$cid" '{event_type:"capiss_mint_decision",result:"allow",reason_code:"ok",subject_spiffe_id:"spiffe://varambu.org/codex-jira-mcp-adapter",act:"create_story",res:"jira-mcp:/project:IAM",aud:"jira-mcp-gateway",decision_type:"root_mint",token_id:"tok-1",root_token_id:"root-1",delegation_depth:0,issued_at_local:"2026-06-19 12:00:02 UTC",expires_at_local:"2026-06-19 12:01:02 UTC",timestamp_local:"2026-06-19 12:00:02 UTC",ttl_seconds:60,issued_at_utc:"2026-06-19T10:00:02Z",expires_at_utc:"2026-06-19T10:01:02Z",timestamp_utc:"2026-06-19T10:00:02Z",correlation_id:$c,policy_id:"capiss.allow.v3",policy_hash:"sha256:capiss-policy-v3"}' >"$sess/capiss_audit.jsonl"
  printf '#1 MINTED OK  2026-06-19 12:00:02 UTC\nCorrelation:  %s\n\n' "$cid" >"$sess/capiss_audit.log"
  jq -cn --arg c "$cid" '{event_type:"jiramcp_gateway_decision",decision:"allow",reason_code:"ok",correlation_id:$c,act:"create_story",res:"jira-mcp:/project:IAM",upstream_called:true,upstream_operation:"story_create",upstream_status:201,timestamp:"2026-06-19T10:00:03Z"}' >"$sess/gateway_audit.jsonl"
  { jq -cn --arg c "$cid" '{event_type:"adapter_request",correlation_id:$c,tool_name:"create_story",act:"create_story",res:"jira-mcp:/project:IAM",project_key:"IAM",timestamp:"2026-06-19T10:00:01Z"}'; jq -cn --arg c "$cid" '{event_type:"adapter_decision",correlation_id:$c,ok:true,token_id:"tok-1",root_token_id:"root-1",key:"IAM-9",timestamp:"2026-06-19T10:00:04Z"}'; } >"$sess/adapter_audit.jsonl"
  { rollout_user "$prompt"; rollout_call create_story call-X '{"project_key":"IAM","summary":"s","description":"d"}'; rollout_output call-X "$cid" true; } >"$sess/codex-home/sessions/2026/06/19/rollout-1.jsonl"
}

# Wait until both in-boundary capture files have at least one line (or timeout).
trace_wait_inboundary() {
  sess="$1"
  need_gateway="${2:-1}"
  i=1
  while [ $i -le 30 ]; do
    if [ -s "$sess/capiss_audit.jsonl" ]; then
      if [ "$need_gateway" -eq 0 ] || [ -s "$sess/gateway_audit.jsonl" ]; then
        break
      fi
    fi
    sleep 1
    i=$((i + 1))
  done
}

sanitize_token_response() {
  raw="$1"
  dest="$2"
  jq 'del(.token)' "$raw" >"$dest"
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

  spiffe_id="spiffe://varambu.org/rogue-socket-shortttl"
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
    -parentID spiffe://varambu.org/agent/spire-agent \
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
      -parentID spiffe://varambu.org/agent/spire-agent \
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
      -entryID "$entry_id" -socketPath /run/spire/server/data/private/api.sock >/dev/null 2>&1 || true
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
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! docker exec \"${temp_rogue}\" test -e /tmp/rogue_svid/svid.pem 2>/dev/null && assert_text_matches \"$EVDIR/rogue_fetch.txt\" '(No such file|no such file|socket|connect|failed|unable|Workload API)'"
  if [ -n "${temp_rogue:-}" ]; then
    docker rm -f "$temp_rogue" >/dev/null 2>&1 || true
  fi
  return 0
}

# M2-T6
T6_test() {
  begin_test_evidence "M2-T6" "socket_no_entry"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "rogue socket container running" \
    "container_running spiffe-rogue-socket"
  premise_guard "workload socket present" \
    "docker exec spiffe-rogue-socket test -S /run/spire/agent/private/api.sock 2>/dev/null"
  exercise_guard "attempt fetch without entry" \
    "set +e; docker exec spiffe-rogue-socket /bin/sh -lc 'printf \"%s\\n\" \"agent {\" \"  trust_domain = \\\"varambu.org\\\"\" \"  socket_path = \\\"/run/spire/agent/private/api.sock\\\"\" \"}\" > /tmp/rogue_socket_min.conf; SPIRE_AGENT_CONFIG=/tmp/rogue_socket_min.conf /opt/spire/bin/spire-agent api fetch x509 -socketPath /run/spire/agent/private/api.sock -write /tmp/rogue_socket_svid' >/tmp/rogue_socket_fetch 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/rc.txt\"; cat /tmp/rogue_socket_fetch >\"$EVDIR/rogue_socket_fetch.txt\" 2>/dev/null || true"
  outcome_guard "fetch denied without entry" \
    "rc=\$(cat \"$EVDIR/rc.txt\" 2>/dev/null || echo 0); [ \"\$rc\" -ne 0 ] && ! docker exec spiffe-rogue-socket test -e /tmp/rogue_socket_svid/svid.pem 2>/dev/null && assert_text_matches \"$EVDIR/rogue_socket_fetch.txt\" '(No identity issued|no identity|permission denied|unauthorized|not authorized|denied)'"
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
    "set -- \$(cat \"$EVDIR/rcs.txt\" 2>/dev/null || echo 0 0 0 0); rc_cert=\$1; rc_key=\$2; rc_node_cert=\$3; rc_node_key=\$4; [ \"\$rc_cert\" -ne 0 ] && [ \"\$rc_key\" -ne 0 ] && [ \"\$rc_node_cert\" -ne 0 ] && [ \"\$rc_node_key\" -ne 0 ] && assert_text_matches \"$EVDIR/rogue_svid_out.txt\" '(No such file|Permission denied|not found)' && assert_text_matches \"$EVDIR/rogue_node_svid.txt\" '(No such file|Permission denied|not found)' && assert_text_matches \"$EVDIR/rogue_node_keys.txt\" '(No such file|Permission denied|not found)'"
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
    "assert_json_eq \"$out\" '.token_type' 'biscuit' && assert_json_present \"$out\" '.expires_at' && assert_json_eq \"$out\" '.issued_to' 'spiffe://varambu.org/agent-a' && assert_json_eq \"$out\" '.aud' 'tool-b' && assert_json_eq \"$out\" '.act' 'read' && assert_json_eq \"$out\" '.res' 'tool-b:/secret'"
  outcome_guard "verified issuer identity recorded" \
    "assert_file_eq \"$EVDIR/verified_capiss_spiffe_id.txt\" \"spiffe://varambu.org/capability-issuer-envoy\" && assert_file_eq \"$EVDIR/verified_capiss_result.txt\" \"ok\""
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
  premise_guard "edge DNS resolves tool-b-envoy" \
    "printf '%s' tool-b-envoy >\"$EVDIR/premise_edge_dns_target.txt\"; out=\"$EVDIR/premise_edge_dns_out.txt\"; err=\"$EVDIR/premise_edge_dns_err.txt\"; resolve_host_ip tool-b-envoy >\"\$out\" 2>\"\$err\"; rc=\"\$?\"; printf '%s' \"\$rc\" >\"$EVDIR/premise_edge_dns_rc.txt\"; ip=\"\$(cat \"\$out\" 2>/dev/null || true)\"; [ \"\$rc\" -eq 0 ] && [ -n \"\$ip\" ]"
  premise_guard "edge context ready (tool-b-envoy reachable)" \
    "ensure_toolb_envoy_ready && tmpdir=\"/tmp/m3s2_premise_agent\"; rm -rf \"\$tmpdir\"; mkdir -p \"\$tmpdir\"; prepare_client_material \"agent-a\" \"\$tmpdir\"; echo \"\${TOOLB_ENVOY_IP:-}\" >\"$EVDIR/toolb_envoy_ip.txt\"; status=\"\$(curl -sS --insecure --cert \"\$CLIENT_CERT\" --key \"\$CLIENT_KEY\" --resolve tool-b-envoy:8443:\${TOOLB_ENVOY_IP} -o \"$EVDIR/premise_toolb_body.txt\" -w '%{http_code}' https://tool-b-envoy:8443/health || true)\"; printf '%s' \"\$status\" >\"$EVDIR/premise_toolb_status.txt\"; [ \"\$status\" = \"200\" ]"
  exercise_guard "attempt OPA from edge" \
    "res_rc=0; printf '%s' opa >\"$EVDIR/opa_resolve_target.txt\"; resolve_host_ip opa >\"$EVDIR/opa_resolve.txt\" 2>\"$EVDIR/opa_resolve.err\" || res_rc=\$?; printf '%s' \"\$res_rc\" >\"$EVDIR/opa_resolve_rc.txt\"; rc=0; status=\"\"; status=\"\$(curl -sS --max-time 3 -o \"$EVDIR/opa_body.txt\" -w '%{http_code}' http://opa:8181/v1/data/capiss/allow 2>\"$EVDIR/opa_err.txt\")\" || rc=\$?; printf '%s' \"\$rc\" >\"$EVDIR/opa_rc.txt\"; printf '%s' \"\$status\" >\"$EVDIR/opa_status.txt\""
  outcome_guard "OPA not reachable from edge network" \
    "rc=\"\$(cat \"$EVDIR/opa_rc.txt\" 2>/dev/null || echo 0)\"; status=\"\$(cat \"$EVDIR/opa_status.txt\" 2>/dev/null || true)\"; premise_status=\"\$(cat \"$EVDIR/premise_toolb_status.txt\" 2>/dev/null || true)\"; res_rc=\"\$(cat \"$EVDIR/opa_resolve_rc.txt\" 2>/dev/null || echo 1)\"; dns_allow=0; if [ \"\$premise_status\" = \"200\" ] && [ \"\$res_rc\" -ne 0 ] && text_matches \"$EVDIR/opa_err.txt\" '(Could not resolve host: *opa|name or service not known.*opa|temporary failure in name resolution.*opa|Resolving timed out)'; then dns_allow=1; fi; [ -s \"$EVDIR/opa_err.txt\" ] && [ \"\$status\" != \"200\" ] && [ \"\$rc\" -ne 0 ] && if text_matches \"$EVDIR/opa_err.txt\" '(Failed to connect|Connection refused|No route to host|Connection timed out|Operation timed out)'; then true; elif [ \"\$dns_allow\" -eq 1 ]; then if text_matches \"$EVDIR/opa_err.txt\" 'Resolving timed out'; then add_warning 'accepted alternate isolation mode: DNS resolution timeout while reaching opa from edge'; else add_warning 'accepted alternate isolation mode: DNS isolation while reaching opa from edge'; fi; else fail_with_body 'expected edge-isolation error pattern (connect denied or DNS isolation)' \"$EVDIR/opa_err.txt\"; fi"
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
  premise_guard "edge DNS resolves tool-b-envoy" \
    "printf '%s' tool-b-envoy >\"$EVDIR/premise_edge_dns_target.txt\"; out=\"$EVDIR/premise_edge_dns_out.txt\"; err=\"$EVDIR/premise_edge_dns_err.txt\"; resolve_host_ip tool-b-envoy >\"\$out\" 2>\"\$err\"; rc=\"\$?\"; printf '%s' \"\$rc\" >\"$EVDIR/premise_edge_dns_rc.txt\"; ip=\"\$(cat \"\$out\" 2>/dev/null || true)\"; [ \"\$rc\" -eq 0 ] && [ -n \"\$ip\" ]"
  premise_guard "edge context ready (tool-b-envoy reachable)" \
    "ensure_toolb_envoy_ready && tmpdir=\"/tmp/m3s2_premise_agent\"; rm -rf \"\$tmpdir\"; mkdir -p \"\$tmpdir\"; prepare_client_material \"agent-a\" \"\$tmpdir\"; echo \"\${TOOLB_ENVOY_IP:-}\" >\"$EVDIR/toolb_envoy_ip.txt\"; status=\"\$(curl -sS --insecure --cert \"\$CLIENT_CERT\" --key \"\$CLIENT_KEY\" --resolve tool-b-envoy:8443:\${TOOLB_ENVOY_IP} -o \"$EVDIR/premise_toolb_body.txt\" -w '%{http_code}' https://tool-b-envoy:8443/health || true)\"; printf '%s' \"\$status\" >\"$EVDIR/premise_toolb_status.txt\"; [ \"\$status\" = \"200\" ]"
  exercise_guard "attempt direct issuer app access from edge" \
    "res_rc=0; printf '%s' capability-issuer >\"$EVDIR/capiss_app_resolve_target.txt\"; resolve_host_ip capability-issuer >\"$EVDIR/capiss_app_resolve.txt\" 2>\"$EVDIR/capiss_app_resolve.err\" || res_rc=\$?; printf '%s' \"\$res_rc\" >\"$EVDIR/capiss_app_resolve_rc.txt\"; rc=0; status=\"\"; status=\"\$(curl -sS --max-time 3 -o \"$EVDIR/capiss_app_body.txt\" -w '%{http_code}' http://capability-issuer:8000/health 2>\"$EVDIR/capiss_app_err.txt\")\" || rc=\$?; printf '%s' \"\$rc\" >\"$EVDIR/capiss_app_rc.txt\"; printf '%s' \"\$status\" >\"$EVDIR/capiss_app_status.txt\""
  outcome_guard "capability-issuer app not reachable from edge network" \
    "rc=\"\$(cat \"$EVDIR/capiss_app_rc.txt\" 2>/dev/null || echo 0)\"; status=\"\$(cat \"$EVDIR/capiss_app_status.txt\" 2>/dev/null || true)\"; premise_status=\"\$(cat \"$EVDIR/premise_toolb_status.txt\" 2>/dev/null || true)\"; res_rc=\"\$(cat \"$EVDIR/capiss_app_resolve_rc.txt\" 2>/dev/null || echo 1)\"; dns_allow=0; if [ \"\$premise_status\" = \"200\" ] && [ \"\$res_rc\" -ne 0 ] && text_matches \"$EVDIR/capiss_app_err.txt\" '(Could not resolve host: *capability-issuer|name or service not known.*capability-issuer|temporary failure in name resolution.*capability-issuer|Resolving timed out)'; then dns_allow=1; fi; [ -s \"$EVDIR/capiss_app_err.txt\" ] && [ \"\$status\" != \"200\" ] && [ \"\$rc\" -ne 0 ] && if text_matches \"$EVDIR/capiss_app_err.txt\" '(Failed to connect|Connection refused|No route to host|Connection timed out|Operation timed out)'; then true; elif [ \"\$dns_allow\" -eq 1 ]; then if text_matches \"$EVDIR/capiss_app_err.txt\" 'Resolving timed out'; then add_warning 'accepted alternate isolation mode: DNS resolution timeout while reaching capability-issuer from edge'; else add_warning 'accepted alternate isolation mode: DNS isolation while reaching capability-issuer from edge'; fi; else fail_with_body 'expected edge-isolation error pattern (connect denied or DNS isolation)' \"$EVDIR/capiss_app_err.txt\"; fi"
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
  outcome_guard "verified tool-b identity recorded" \
    "assert_file_eq \"$EVDIR/verified_toolb_spiffe_id.txt\" \"spiffe://varambu.org/tool-b-envoy\" && assert_file_eq \"$EVDIR/verified_toolb_result.txt\" \"ok\""
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
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"write\",\"res\":\"tool-b:/secret\"}' \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mint headers" \
    "curl -sS -v --insecure --cert \"$CAPISS_AGENT_CERT\" --key \"$CAPISS_AGENT_KEY\" -H 'Host: capability-issuer-envoy' -H 'Content-Type: application/json' -d '{\"aud\":\"tool-b\",\"act\":\"write\",\"res\":\"tool-b:/secret\"}' https://${CAPISS_ENVOY_IP}:9443/capabilities/mint -o /dev/null 2>\"$EVDIR/mint_headers.txt\""
  outcome_guard "envoy handled mint request" \
    "grep -Ei '(server: envoy|x-envoy)' \"$EVDIR/mint_headers.txt\""
  outcome_guard "policy denied 403" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\""
  out="$EVDIR/mint_body.json"
  outcome_guard "policy deny body" \
    "assert_json_eq \"$out\" '.error' 'denied' && assert_json_eq \"$out\" '.reason' 'policy'"
  return 0
}

M4_T1_test() {
  begin_test_evidence "M4-T1" "root_mint_contains_chain_metadata"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; echo \"\$capiss_ip\" >\"$EVDIR/capiss_envoy_ip.txt\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" \
    "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint root token for discovery" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/mint_body.json\" \"$EVDIR/status.txt\""
  outcome_guard "mint allowed 200" \
    "assert_file_eq \"$EVDIR/status.txt\" \"200\""
  out="$EVDIR/mint_body.json"
  outcome_guard "metadata fields present" \
    "assert_json_present \"$out\" '.token' && assert_json_present \"$out\" '.root_token_id' && assert_json_present \"$out\" '.token_id' && assert_json_eq \"$out\" '.delegation_depth' '0' && jq -e '.parent_token_id == null' \"$out\" >/dev/null"
  outcome_guard "canonical search resource" \
    "assert_json_eq \"$out\" '.res' 'tool-b:/search'"
  return 0
}

M4_T2_test() {
  begin_test_evidence "M4-T2" "search_writes_discovery_registry"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  premise_guard "redis container running" "docker ps --format '{{.Names}}' | grep -Fxq spiffe-redis"
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" \
    "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token_id="$(json_get '.root_token_id' "$EVDIR/root_mint.json")"
  token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "call tool-b search with token" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" \
    "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  out="$EVDIR/search_response.json"
  outcome_guard "search returns canonical resources" \
    "jq -e '.resources | index(\"tool-b:/read-file:fileA\") != null' \"$out\" >/dev/null"
  outcome_guard "registry contains discovered fileA" \
    "test \"$(docker exec spiffe-redis redis-cli SISMEMBER m4:registry:${root_token_id} tool-b:/read-file:fileA | tr -d '\\r')\" = \"1\""
  return 0
}

M4_T3_test() {
  begin_test_evidence "M4-T3" "resource_mint_requires_registry_proof"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint root /secret token" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "resource mint without discovery proof" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/resource_mint.json\" \"$EVDIR/resource_status.txt\""
  outcome_guard "resource mint denied 403" "assert_file_eq \"$EVDIR/resource_status.txt\" \"403\""
  out="$EVDIR/resource_mint.json"
  outcome_guard "registry miss reason" "assert_json_eq \"$out\" '.reason' 'registry_miss'"
  return 0
}

M4_T4_test() {
  begin_test_evidence "M4-T4" "resource_mint_after_discovery"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  root_id="$(json_get '.root_token_id' "$EVDIR/root_mint.json")"
  exercise_guard "discover files via search" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$root_token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  exercise_guard "resource mint for read-file:fileA" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/resource_mint.json\" \"$EVDIR/resource_status.txt\""
  outcome_guard "resource mint allowed 200" "assert_file_eq \"$EVDIR/resource_status.txt\" \"200\""
  out="$EVDIR/resource_mint.json"
  outcome_guard "root token id preserved" "assert_json_eq \"$out\" '.root_token_id' \"$root_id\""
  resource_token="$(json_get '.token' "$EVDIR/resource_mint.json")"
  exercise_guard "read file using resource token" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$resource_token\" \"\$TOOLB_READ_FILE_URL_PREFIX/fileA\" \"$EVDIR/read_response.json\" >\"$EVDIR/read_status.txt\""
  outcome_guard "read allowed 200" "assert_file_eq \"$EVDIR/read_status.txt\" \"200\""
  out="$EVDIR/read_response.json"
  outcome_guard "returned file payload" "assert_json_eq \"$out\" '.id' 'fileA'"
  return 0
}

M4_T5_test() {
  begin_test_evidence "M4-T5" "budget_enforced_per_root_token"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint root /secret token" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "consume budget with repeated /secret calls" \
    "i=1; : >\"$EVDIR/statuses.txt\"; while [ \$i -le 11 ]; do toolb_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"$EVDIR/resp_\${i}.json\" \"$EVDIR/st_\${i}.txt\"; cat \"$EVDIR/st_\${i}.txt\" >>\"$EVDIR/statuses.txt\"; echo >>\"$EVDIR/statuses.txt\"; i=\$((i+1)); done"
  outcome_guard "first ten requests allowed" \
    "i=1; while [ \$i -le 10 ]; do assert_file_eq \"$EVDIR/st_\${i}.txt\" \"200\" || exit 1; i=\$((i+1)); done"
  outcome_guard "eleventh request denied" \
    "assert_file_any \"$EVDIR/st_11.txt\" \"401\" \"403\""
  out="$EVDIR/resp_11.json"
  outcome_guard "denied for budget" \
    "assert_json_eq \"$out\" '.reason' 'budget_exceeded'"
  return 0
}

M4_T6_test() {
  begin_test_evidence "M4-T6" "tampered_token_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint root /secret token" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  exercise_guard "tamper minted token bytes" \
    "token=\"\$(json_get '.token' \"$EVDIR/root_mint.json\")\"; prefix=\"\${token%?}\"; last=\"\${token#\"\$prefix\"}\"; repl='A'; [ \"\$last\" = 'A' ] && repl='B'; printf '%s' \"\${prefix}\${repl}\" >\"$EVDIR/tampered_token.txt\""
  exercise_guard "call tool-b /secret with tampered token" \
    "tampered_token=\"\$(cat \"$EVDIR/tampered_token.txt\")\"; toolb_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$tampered_token\" \"$EVDIR/tampered_response.json\" \"$EVDIR/tampered_status.txt\""
  outcome_guard "tampered token denied" \
    "assert_file_any \"$EVDIR/tampered_status.txt\" \"401\" \"403\""
  out="$EVDIR/tampered_response.json"
  outcome_guard "invalid token reason" \
    "assert_json_eq \"$out\" '.reason' 'invalid_token'"
  return 0
}

M4_T7_test() {
  begin_test_evidence "M4-T7" "depth_limit_enforced_on_repeated_delegation"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "discover files via search" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$root_token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  exercise_guard "mint delegated token depth 1" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/depth1_mint.json\" \"$EVDIR/depth1_status.txt\""
  outcome_guard "depth 1 mint allowed 200" "assert_file_eq \"$EVDIR/depth1_status.txt\" \"200\""
  token_1="$(json_get '.token' "$EVDIR/depth1_mint.json")"
  exercise_guard "mint delegated token depth 2" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$token_1\" \"$EVDIR/depth2_mint.json\" \"$EVDIR/depth2_status.txt\""
  outcome_guard "depth 2 mint allowed 200" "assert_file_eq \"$EVDIR/depth2_status.txt\" \"200\""
  token_2="$(json_get '.token' "$EVDIR/depth2_mint.json")"
  exercise_guard "mint delegated token depth 3" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$token_2\" \"$EVDIR/depth3_mint.json\" \"$EVDIR/depth3_status.txt\""
  outcome_guard "depth 3 mint allowed 200" "assert_file_eq \"$EVDIR/depth3_status.txt\" \"200\""
  token_3="$(json_get '.token' "$EVDIR/depth3_mint.json")"
  exercise_guard "attempt delegated token depth 4" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$token_3\" \"$EVDIR/depth4_mint.json\" \"$EVDIR/depth4_status.txt\""
  outcome_guard "depth 4 mint denied 403" "assert_file_eq \"$EVDIR/depth4_status.txt\" \"403\""
  out="$EVDIR/depth4_mint.json"
  outcome_guard "depth exceeded reason" \
    "assert_json_eq \"$out\" '.reason' 'depth_exceeded'"
  return 0
}

M4_T8_test() {
  begin_test_evidence "M4-T8" "new_resource_mint_rate_enforced"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "discover files via search" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$root_token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  exercise_guard "mint new resource fileA" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/fileA_mint.json\" \"$EVDIR/fileA_status.txt\""
  exercise_guard "mint new resource fileB" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileB\"}' \"\$root_token\" \"$EVDIR/fileB_mint.json\" \"$EVDIR/fileB_status.txt\""
  exercise_guard "mint new resource fileC" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileC\"}' \"\$root_token\" \"$EVDIR/fileC_mint.json\" \"$EVDIR/fileC_status.txt\""
  outcome_guard "first three new-resource mints allowed" \
    "assert_file_eq \"$EVDIR/fileA_status.txt\" \"200\" && assert_file_eq \"$EVDIR/fileB_status.txt\" \"200\" && assert_file_eq \"$EVDIR/fileC_status.txt\" \"200\""
  exercise_guard "attempt fourth new-resource mint under same root" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/fileA_again_mint.json\" \"$EVDIR/fileA_again_status.txt\""
  outcome_guard "fourth new-resource mint denied 403" \
    "assert_file_eq \"$EVDIR/fileA_again_status.txt\" \"403\""
  out="$EVDIR/fileA_again_mint.json"
  outcome_guard "mint-rate exceeded reason" \
    "assert_json_eq \"$out\" '.reason' 'mint_rate_exceeded'"
  return 0
}

M4_T9_test() {
  begin_test_evidence "M4-T9" "allow_flow_emits_correlatable_audit_events"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "record log capture start time" \
    "date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  root_id="$(json_get '.root_token_id' "$EVDIR/root_mint.json")"
  root_claim_token_id="$(json_get '.token_id' "$EVDIR/root_mint.json")"
  exercise_guard "discover files via search" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$root_token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  exercise_guard "resource mint for read-file:fileA" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/resource_mint.json\" \"$EVDIR/resource_status.txt\""
  outcome_guard "resource mint allowed 200" "assert_file_eq \"$EVDIR/resource_status.txt\" \"200\""
  resource_token="$(json_get '.token' "$EVDIR/resource_mint.json")"
  child_token_id="$(json_get '.token_id' "$EVDIR/resource_mint.json")"
  parent_token_id="$(json_get '.parent_token_id' "$EVDIR/resource_mint.json")"
  exercise_guard "read file using resource token" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$resource_token\" \"\$TOOLB_READ_FILE_URL_PREFIX/fileA\" \"$EVDIR/read_response.json\" >\"$EVDIR/read_status.txt\""
  outcome_guard "read allowed 200" "assert_file_eq \"$EVDIR/read_status.txt\" \"200\""
  exercise_guard "capture capiss and tool-b logs since flow start" \
    "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-capability-issuer >\"$EVDIR/capiss_container.log\" 2>&1; docker logs --since \"\$since\" spiffe-tool-b >\"$EVDIR/toolb_container.log\" 2>&1; grep -F '\"event_type\"' \"$EVDIR/capiss_container.log\" >\"$EVDIR/capiss_events.jsonl\" || :; grep -F '\"event_type\"' \"$EVDIR/toolb_container.log\" >\"$EVDIR/toolb_events.jsonl\" || :"
  outcome_guard "capiss root mint event correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$root_claim_token_id\" 'select(.event_type==\"capiss_mint_decision\" and .decision_type==\"root_mint\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .root_token_id==\$root and .token_id==\$token and .res==\"tool-b:/search\")' \"$EVDIR/capiss_events.jsonl\" >/dev/null"
  outcome_guard "capiss delegated mint event correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$child_token_id\" --arg parent \"\$parent_token_id\" 'select(.event_type==\"capiss_mint_decision\" and .decision_type==\"resource_mint\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .delegator_spiffe_id==\"spiffe://varambu.org/agent-a\" and .root_token_id==\$root and .token_id==\$token and .parent_token_id==\$parent and .res==\"tool-b:/read-file:fileA\")' \"$EVDIR/capiss_events.jsonl\" >/dev/null"
  outcome_guard "discovery registry write correlated" \
    "jq -e --arg root \"\$root_id\" 'select(.event_type==\"discovery_registry_write\" and .root_token_id==\$root and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .discovery_endpoint==\"tool-b:/search\" and (.res_count >= 1))' \"$EVDIR/toolb_events.jsonl\" >/dev/null"
  outcome_guard "tool-b allow event correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$child_token_id\" --arg parent \"\$parent_token_id\" 'select(.event_type==\"toolb_enforcement_decision\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .delegator_spiffe_id==\"spiffe://varambu.org/agent-a\" and .root_token_id==\$root and .token_id==\$token and .parent_token_id==\$parent and .res==\"tool-b:/read-file:fileA\" and .path==\"/read-file/fileA\")' \"$EVDIR/toolb_events.jsonl\" >/dev/null"
  return 0
}

M4_T10_test() {
  begin_test_evidence "M4-T10" "deny_flow_emits_correlatable_mint_audit_event"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "record log capture start time" \
    "date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  root_id="$(json_get '.root_token_id' "$EVDIR/root_mint.json")"
  root_claim_token_id="$(json_get '.token_id' "$EVDIR/root_mint.json")"
  exercise_guard "discover files via search" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$root_token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  exercise_guard "mint new resource fileA" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/fileA_mint.json\" \"$EVDIR/fileA_status.txt\""
  exercise_guard "mint new resource fileB" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileB\"}' \"\$root_token\" \"$EVDIR/fileB_mint.json\" \"$EVDIR/fileB_status.txt\""
  exercise_guard "mint new resource fileC" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileC\"}' \"\$root_token\" \"$EVDIR/fileC_mint.json\" \"$EVDIR/fileC_status.txt\""
  outcome_guard "first three new-resource mints allowed" \
    "assert_file_eq \"$EVDIR/fileA_status.txt\" \"200\" && assert_file_eq \"$EVDIR/fileB_status.txt\" \"200\" && assert_file_eq \"$EVDIR/fileC_status.txt\" \"200\""
  exercise_guard "attempt fourth new-resource mint under same root" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/fileA_again_mint.json\" \"$EVDIR/fileA_again_status.txt\""
  outcome_guard "fourth new-resource mint denied 403" \
    "assert_file_eq \"$EVDIR/fileA_again_status.txt\" \"403\""
  outcome_guard "mint-rate exceeded reason" \
    "assert_json_eq \"$EVDIR/fileA_again_mint.json\" '.reason' 'mint_rate_exceeded'"
  exercise_guard "capture capiss logs since flow start" \
    "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-capability-issuer >\"$EVDIR/capiss_container.log\" 2>&1; grep -F '\"event_type\"' \"$EVDIR/capiss_container.log\" >\"$EVDIR/capiss_events.jsonl\" || :"
  outcome_guard "capiss mint-rate deny event correlated" \
    "jq -e --arg root \"\$root_id\" --arg parent \"\$root_claim_token_id\" 'select(.event_type==\"capiss_mint_decision\" and .decision_type==\"resource_mint\" and .result==\"deny\" and .reason_code==\"mint_rate_exceeded\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .delegator_spiffe_id==\"spiffe://varambu.org/agent-a\" and .root_token_id==\$root and .parent_token_id==\$parent and .res==\"tool-b:/read-file:fileA\" and .registry_hit==true)' \"$EVDIR/capiss_events.jsonl\" >/dev/null"
  return 0
}

M4_T11_test() {
  begin_test_evidence "M4-T11" "amplified_delegated_mint_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint root secret token" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "attempt delegated mint with amplified action" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"write\",\"res\":\"tool-b:/secret\"}' \"\$root_token\" \"$EVDIR/amplified_mint.json\" \"$EVDIR/amplified_status.txt\""
  outcome_guard "amplified mint denied 403" "assert_file_eq \"$EVDIR/amplified_status.txt\" \"403\""
  outcome_guard "amplified authority reason" \
    "assert_json_eq \"$EVDIR/amplified_mint.json\" '.reason' 'amplified_authority'"
  return 0
}

M4_T12_test() {
  begin_test_evidence "M4-T12" "wildcard_resource_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  exercise_guard "mint root secret token" \
    "mint_with_cert_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "attempt delegated mint with wildcard resource" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:*\"}' \"\$root_token\" \"$EVDIR/wildcard_mint.json\" \"$EVDIR/wildcard_status.txt\""
  outcome_guard "wildcard resource rejected 400" "assert_file_eq \"$EVDIR/wildcard_status.txt\" \"400\""
  outcome_guard "resource validation reason" \
    "assert_json_eq \"$EVDIR/wildcard_mint.json\" '.reason' 'res'"
  return 0
}

M4_T13_test() {
  begin_test_evidence "M4-T13" "budget_and_registry_ttl_bounded"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  premise_guard "redis container running" "docker ps --format '{{.Names}}' | grep -Fxq spiffe-redis"
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  root_id="$(json_get '.root_token_id' "$EVDIR/root_mint.json")"
  root_exp="$(json_get '.expires_at' "$EVDIR/root_mint.json")"
  exercise_guard "discover files via search" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$root_token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  exercise_guard "capture redis TTLs" \
    "docker exec spiffe-redis redis-cli TTL \"m4:budget:${root_id}\" | tr -d '\\r' >\"$EVDIR/budget_ttl.txt\"; docker exec spiffe-redis redis-cli TTL \"m4:registry:${root_id}\" | tr -d '\\r' >\"$EVDIR/registry_ttl.txt\"; date +%s >\"$EVDIR/ttl_check_now.txt\""
  outcome_guard "budget ttl bounded by root expiry" \
    "ttl=\$(cat \"$EVDIR/budget_ttl.txt\"); now=\$(cat \"$EVDIR/ttl_check_now.txt\"); remaining=\$((root_exp - now + 1)); [ \"\$ttl\" -gt 0 ] && [ \"\$ttl\" -le \"\$remaining\" ]"
  outcome_guard "registry ttl bounded by root expiry" \
    "ttl=\$(cat \"$EVDIR/registry_ttl.txt\"); now=\$(cat \"$EVDIR/ttl_check_now.txt\"); remaining=\$((root_exp - now + 1)); [ \"\$ttl\" -gt 0 ] && [ \"\$ttl\" -le \"\$remaining\" ]"
  return 0
}

M4_T14_test() {
  begin_test_evidence "M4-T14" "protected_request_does_not_require_capiss"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "tool-b and capiss material available" \
    "ensure_toolb_material && ensure_capiss_material"
  premise_guard "capiss-envoy resolves" \
    "capiss_ip=\"$(wait_resolve_ip capability-issuer-envoy 30)\"; test -n \"\$capiss_ip\"; CAPISS_ENVOY_IP=\"\$capiss_ip\""
  premise_guard "capiss-envoy TCP reachable" "wait_tcp \"${CAPISS_ENVOY_IP}\" \"9443\" 30"
  premise_guard "tool-b-envoy resolves" \
    "toolb_ip=\"$(wait_resolve_ip tool-b-envoy 30)\"; test -n \"\$toolb_ip\"; TOOLB_ENVOY_IP=\"\$toolb_ip\""
  premise_guard "tool-b-envoy TCP reachable" "wait_tcp \"${TOOLB_ENVOY_IP}\" \"8443\" 30"
  exercise_guard "mint root search token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_MINT_URL\" \"\$CAPISS_SEARCH_MINT_BODY\" \"$EVDIR/root_mint.json\" \"$EVDIR/root_status.txt\""
  outcome_guard "root mint allowed 200" "assert_file_eq \"$EVDIR/root_status.txt\" \"200\""
  root_token="$(json_get '.token' "$EVDIR/root_mint.json")"
  exercise_guard "discover files via search" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$root_token\" \"\$TOOLB_SEARCH_URL\" \"$EVDIR/search_response.json\" >\"$EVDIR/search_status.txt\""
  outcome_guard "search allowed 200" "assert_file_eq \"$EVDIR/search_status.txt\" \"200\""
  exercise_guard "resource mint for read-file:fileA" \
    "mint_with_body_auth_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_RESOURCE_MINT_URL\" '{\"aud\":\"tool-b\",\"act\":\"read\",\"res\":\"tool-b:/read-file:fileA\"}' \"\$root_token\" \"$EVDIR/resource_mint.json\" \"$EVDIR/resource_status.txt\""
  outcome_guard "resource mint allowed 200" "assert_file_eq \"$EVDIR/resource_status.txt\" \"200\""
  resource_token="$(json_get '.token' "$EVDIR/resource_mint.json")"
  exercise_guard "stop capiss app before protected resource use" \
    "docker stop spiffe-capability-issuer >/dev/null"
  exercise_guard "read file using resource token while capiss is stopped" \
    "toolb_request_url \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$resource_token\" \"\$TOOLB_READ_FILE_URL_PREFIX/fileA\" \"$EVDIR/read_response.json\" >\"$EVDIR/read_status.txt\""
  exercise_guard "restart capiss app after proof" \
    "docker start spiffe-capability-issuer >/dev/null"
  outcome_guard "read allowed without capiss hot path" "assert_file_eq \"$EVDIR/read_status.txt\" \"200\""
  outcome_guard "returned file payload" "assert_json_eq \"$EVDIR/read_response.json\" '.id' 'fileA'"
  return 0
}

M4A_T1_test() {
  begin_test_evidence "M4a-T1" "mock_upstream_breadth"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "jira-mock health reachable from test harness" \
    "wait_http_ready \"${JIRA_MOCK_URL}/health\" \"\" 30"
  exercise_guard "direct mock read for IAM-1 and NAS-1" \
    "curl -sS -o \"$EVDIR/iam_1.json\" -w '%{http_code}' \"${JIRA_MOCK_URL}/rest/api/3/issue/IAM-1\" >\"$EVDIR/iam_1_status.txt\"; curl -sS -o \"$EVDIR/nas_1.json\" -w '%{http_code}' \"${JIRA_MOCK_URL}/rest/api/3/issue/NAS-1\" >\"$EVDIR/nas_1_status.txt\""
  outcome_guard "mock returns IAM issue" \
    "assert_file_eq \"$EVDIR/iam_1_status.txt\" \"200\" && assert_json_eq \"$EVDIR/iam_1.json\" '.fields.project.key' 'IAM'"
  outcome_guard "mock returns NAS issue" \
    "assert_file_eq \"$EVDIR/nas_1_status.txt\" \"200\" && assert_json_eq \"$EVDIR/nas_1.json\" '.fields.project.key' 'NAS'"
  return 0
}

M4A_T2_test() {
  begin_test_evidence "M4a-T2" "allowed_mint_and_iam_read"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t2_mint_$$.json"
  token_tmp="/tmp/m4a_t2_token_$$.txt"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy reachable" \
    "ensure_capiss_envoy_ready; echo \"${CAPISS_ENVOY_IP:-}\" >\"$EVDIR/capiss_envoy_ip.txt\""
  premise_guard "jira-tool-envoy reachable" \
    "ensure_jira_envoy_ready; echo \"${JIRA_ENVOY_IP:-}\" >\"$EVDIR/jira_envoy_ip.txt\""
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira mint allowed" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\" && assert_json_eq \"$EVDIR/mint_body.json\" '.aud' 'jira-tool' && assert_json_eq \"$EVDIR/mint_body.json\" '.act' 'read' && assert_json_eq \"$EVDIR/mint_body.json\" '.res' 'jira-tool:/project:IAM'" || return 1
  exercise_guard "read IAM-1 through jira-tool-envoy" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "IAM-1 read allowed" \
    "assert_file_eq \"$EVDIR/status.txt\" \"200\" && assert_json_eq \"$EVDIR/response.json\" '.fields.project.key' 'IAM'"
  outcome_guard "verified jira-tool identity recorded" \
    "assert_file_eq \"$EVDIR/verified_jiratool_spiffe_id.txt\" \"spiffe://varambu.org/jira-tool-envoy\" && assert_file_eq \"$EVDIR/verified_jiratool_result.txt\" \"ok\""
  return 0
}

M4A_T3_test() {
  begin_test_evidence "M4a-T3" "non_allowed_project_mint_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t3_mint_$$.json"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy reachable" \
    "ensure_capiss_envoy_ready; echo \"${CAPISS_ENVOY_IP:-}\" >\"$EVDIR/capiss_envoy_ip.txt\""
  exercise_guard "attempt NAS Jira root mint as agent-a" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_NAS_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\""
  outcome_guard "NAS mint denied by policy" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"403\" && assert_json_eq \"$EVDIR/mint_body.json\" '.reason' 'policy'"
  return 0
}

M4A_T4_test() {
  begin_test_evidence "M4a-T4" "nas_read_denied_before_upstream"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t4_mint_$$.json"
  token_tmp="/tmp/m4a_t4_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  exercise_guard "attempt NAS-1 read with IAM token" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"NAS-1\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "NAS-1 denied by local project mismatch" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\" && assert_json_eq \"$EVDIR/response.json\" '.reason' 'project_mismatch'"
  outcome_guard "mock saw no upstream request" \
    "jq -e '.requests | length == 0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M4A_T5_test() {
  begin_test_evidence "M4a-T5" "rogue_jira_mint_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t5_mint_$$.json"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy reachable" \
    "ensure_capiss_envoy_ready; echo \"${CAPISS_ENVOY_IP:-}\" >\"$EVDIR/capiss_envoy_ip.txt\""
  exercise_guard "attempt IAM Jira root mint as rogue" \
    "mint_with_body_to_file \"\$CAPISS_ROGUE_CERT\" \"\$CAPISS_ROGUE_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\""
  outcome_guard "rogue mint denied by policy" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"403\" && assert_json_eq \"$EVDIR/mint_body.json\" '.reason' 'policy'"
  return 0
}

M4A_T6_test() {
  begin_test_evidence "M4a-T6" "stolen_jira_token_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t6_mint_$$.json"
  token_tmp="/tmp/m4a_t6_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira root token as agent-a" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  exercise_guard "rogue uses stolen agent token" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_ROGUE_CERT\" \"\$CAPISS_ROGUE_KEY\" \"\$token\" \"IAM-1\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "stolen token denied by subject binding" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\" && assert_json_eq \"$EVDIR/response.json\" '.reason' 'sub_mismatch'"
  outcome_guard "mock saw no upstream request" \
    "jq -e '.requests | length == 0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M4A_T7_test() {
  begin_test_evidence "M4a-T7" "jira_budget_consumption"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t7_mint_$$.json"
  token_tmp="/tmp/m4a_t7_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  premise_guard "redis container running" "docker ps --format '{{.Names}}' | grep -Fxq spiffe-redis"
  exercise_guard "mint IAM Jira root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  root_id="$(json_get '.root_token_id' "$EVDIR/mint_body.json")"
  exercise_guard "read IAM-1 once" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture remaining root budget" \
    "docker exec spiffe-redis redis-cli GET \"m4:budget:${root_id}\" | tr -d '\\r' >\"$EVDIR/budget_remaining.txt\""
  outcome_guard "read allowed" "assert_file_eq \"$EVDIR/status.txt\" \"200\""
  outcome_guard "budget consumed once" "assert_file_eq \"$EVDIR/budget_remaining.txt\" \"9\""
  return 0
}

M4A_T8_test() {
  begin_test_evidence "M4a-T8" "jira_budget_exhaustion"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t8_mint_$$.json"
  token_tmp="/tmp/m4a_t8_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  exercise_guard "consume Jira budget with eleven reads" \
    "token=\"\$(cat \"$token_tmp\")\"; i=1; : >\"$EVDIR/statuses.txt\"; while [ \$i -le 11 ]; do jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" \"$EVDIR/resp_\${i}.json\" \"$EVDIR/st_\${i}.txt\"; cat \"$EVDIR/st_\${i}.txt\" >>\"$EVDIR/statuses.txt\"; echo >>\"$EVDIR/statuses.txt\"; i=\$((i+1)); done"
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "first ten reads allowed" \
    "i=1; while [ \$i -le 10 ]; do assert_file_eq \"$EVDIR/st_\${i}.txt\" \"200\" || exit 1; i=\$((i+1)); done"
  outcome_guard "eleventh read denied by budget" \
    "assert_file_eq \"$EVDIR/st_11.txt\" \"403\" && assert_json_eq \"$EVDIR/resp_11.json\" '.reason' 'budget_exceeded'"
  outcome_guard "mock saw only ten upstream calls" \
    "jq -e '.requests | length == 10' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M4A_T9_test() {
  begin_test_evidence "M4a-T9" "upstream_project_mismatch_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t9_mint_$$.json"
  token_tmp="/tmp/m4a_t9_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  exercise_guard "read IAM-999 with mismatched upstream project field" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-999\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "upstream mismatch denied locally" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\" && assert_json_eq \"$EVDIR/response.json\" '.reason' 'upstream_project_mismatch'"
  outcome_guard "upstream was called exactly once" \
    "jq -e '(.requests | length == 1) and (.requests[0].issue_key == \"IAM-999\")' \"$EVDIR/mock_requests.json\" >/dev/null"
  outcome_guard "upstream body not returned" \
    "! grep -Fq 'Mismatched upstream project fixture' \"$EVDIR/response.json\""
  return 0
}

M4A_T10_test() {
  begin_test_evidence "M4a-T10" "jira_audit_trace_reconstruction"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4a_t10_mint_$$.json"
  token_tmp="/tmp/m4a_t10_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "record log capture start time" \
    "date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  root_id="$(json_get '.root_token_id' "$EVDIR/mint_body.json")"
  token_id="$(json_get '.token_id' "$EVDIR/mint_body.json")"
  exercise_guard "read IAM-1 through jira-tool-envoy" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "IAM-1 read allowed" "assert_file_eq \"$EVDIR/status.txt\" \"200\""
  exercise_guard "capture capiss and jira-tool logs since flow start" \
    "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-capability-issuer >\"$EVDIR/capiss_container.log\" 2>&1; docker logs --since \"\$since\" spiffe-jira-tool >\"$EVDIR/jiratool_container.log\" 2>&1; grep -F '\"event_type\"' \"$EVDIR/capiss_container.log\" >\"$EVDIR/capiss_events.jsonl\" || :; grep -F '\"event_type\"' \"$EVDIR/jiratool_container.log\" >\"$EVDIR/jiratool_events.jsonl\" || :"
  outcome_guard "capiss Jira root mint event correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$token_id\" 'select(.event_type==\"capiss_mint_decision\" and .decision_type==\"root_mint\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .aud==\"jira-tool\" and .act==\"read\" and .res==\"jira-tool:/project:IAM\" and .root_token_id==\$root and .token_id==\$token and .policy_id==\"capiss.allow.v3\")' \"$EVDIR/capiss_events.jsonl\" >/dev/null"
  outcome_guard "jira-tool allow event correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$token_id\" 'select(.event_type==\"jiratool_enforcement_decision\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .root_token_id==\$root and .token_id==\$token and .aud==\"jira-tool\" and .act==\"read\" and .res==\"jira-tool:/project:IAM\" and .jira_operation==\"issue_read\" and .requested_project==\"IAM\" and .token_project==\"IAM\" and .issue_key==\"IAM-1\" and .upstream_called==true and .upstream_status==200 and (.budget_remaining|type)==\"number\")' \"$EVDIR/jiratool_events.jsonl\" >/dev/null"
  return 0
}

M4B_T1_test() {
  begin_test_evidence "M4b-T1" "allowed_write_update_and_readback"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4b_t1_mint_$$.json"
  token_tmp="/tmp/m4b_t1_token_$$.txt"
  body_file="/tmp/m4b_t1_body_$$.json"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira write root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_WRITE_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira write mint allowed" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\" && assert_json_eq \"$EVDIR/mint_body.json\" '.act' 'write' && assert_json_eq \"$EVDIR/mint_body.json\" '.res' 'jira-tool:/project:IAM'" || return 1
  marker="$(date -u '+%d.%m.%y %H.%M.%S UTC - Description updated by SPIRE service jira-tool')"
  printf '%s' "$marker" >"$EVDIR/marker.txt"
  exercise_guard "build sanitized description update body" \
    "jq -nc --arg description \"\$(cat \"$EVDIR/marker.txt\")\" '{description:\$description}' >\"$body_file\""
  exercise_guard "update IAM-1 description through jira-tool-envoy" \
    "token=\"\$(cat \"$token_tmp\")\"; body=\"\$(cat \"$body_file\")\"; jiratool_put_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" \"\$body\" \"$EVDIR/update_response.json\" \"$EVDIR/update_status.txt\""
  exercise_guard "read IAM-1 back with write token" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" \"$EVDIR/readback.json\" \"$EVDIR/readback_status.txt\""
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "description update returned no content" "assert_file_eq \"$EVDIR/update_status.txt\" \"204\""
  outcome_guard "write token can read back marker" \
    "assert_file_eq \"$EVDIR/readback_status.txt\" \"200\" && grep -Fq \"\$(cat \"$EVDIR/marker.txt\")\" \"$EVDIR/readback.json\""
  outcome_guard "mock saw PUT then GET for IAM-1" \
    "jq -e '.requests | length == 2 and .[0].method == \"PUT\" and .[0].issue_key == \"IAM-1\" and .[0].status == 204 and .[1].method == \"GET\" and .[1].issue_key == \"IAM-1\" and .[1].status == 200' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M4B_T2_test() {
  begin_test_evidence "M4b-T2" "read_token_write_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4b_t2_mint_$$.json"
  token_tmp="/tmp/m4b_t2_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira read root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira read mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  exercise_guard "attempt description write with read token" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_put_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-2\" '{\"description\":\"read token must not write\"}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "read token write denied" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\" && assert_json_eq \"$EVDIR/response.json\" '.reason' 'insufficient_authority'"
  outcome_guard "mock saw no write request" \
    "jq -e '.requests | length == 0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M4B_T3_test() {
  begin_test_evidence "M4b-T3" "nas_write_mint_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4b_t3_mint_$$.json"
  premise_guard "capiss material available" "ensure_capiss_material"
  premise_guard "capiss-envoy reachable" \
    "ensure_capiss_envoy_ready; echo \"${CAPISS_ENVOY_IP:-}\" >\"$EVDIR/capiss_envoy_ip.txt\""
  exercise_guard "attempt NAS Jira write root mint as agent-a" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_NAS_WRITE_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\""
  outcome_guard "NAS write mint denied by policy" \
    "assert_file_eq \"$EVDIR/mint_status.txt\" \"403\" && assert_json_eq \"$EVDIR/mint_body.json\" '.reason' 'policy'"
  return 0
}

M4B_T4_test() {
  begin_test_evidence "M4b-T4" "nas_write_denied_before_upstream"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4b_t4_mint_$$.json"
  token_tmp="/tmp/m4b_t4_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira write root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_WRITE_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira write mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  exercise_guard "attempt NAS-1 write with IAM write token" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_put_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"NAS-1\" '{\"description\":\"must not update NAS\"}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "NAS-1 write denied by local project mismatch" \
    "assert_file_eq \"$EVDIR/status.txt\" \"403\" && assert_json_eq \"$EVDIR/response.json\" '.reason' 'project_mismatch'"
  outcome_guard "mock saw no upstream request" \
    "jq -e '.requests | length == 0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M4B_T5_test() {
  begin_test_evidence "M4b-T5" "description_write_body_shape"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4b_t5_mint_$$.json"
  token_tmp="/tmp/m4b_t5_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira write root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_WRITE_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira write mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  exercise_guard "attempt malformed description write" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_put_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" '{' \"$EVDIR/malformed_response.json\" \"$EVDIR/malformed_status.txt\""
  exercise_guard "attempt unrelated-field write" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_put_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-1\" '{\"description\":\"ok\",\"summary\":\"bad\"}' \"$EVDIR/extra_response.json\" \"$EVDIR/extra_status.txt\""
  exercise_guard "capture mock request log" "jira_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "malformed body rejected" \
    "assert_file_eq \"$EVDIR/malformed_status.txt\" \"400\" && assert_json_eq \"$EVDIR/malformed_response.json\" '.reason' 'malformed_body'"
  outcome_guard "unrelated fields rejected" \
    "assert_file_eq \"$EVDIR/extra_status.txt\" \"400\" && assert_json_eq \"$EVDIR/extra_response.json\" '.reason' 'unsupported_fields'"
  outcome_guard "mock saw no invalid write request" \
    "jq -e '.requests | length == 0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M4B_T6_test() {
  begin_test_evidence "M4b-T6" "write_audit_trace_reconstruction"
  echo "EVIDENCE_DIR=$EVDIR"
  raw="/tmp/m4b_t6_mint_$$.json"
  token_tmp="/tmp/m4b_t6_token_$$.txt"
  premise_guard "capiss material and jira-tool available" \
    "ensure_capiss_material && ensure_capiss_envoy_ready && ensure_jira_envoy_ready"
  exercise_guard "record log capture start time" \
    "date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "reset jira mock request log" "jira_mock_reset"
  exercise_guard "mint IAM Jira write root token" \
    "mint_with_body_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$CAPISS_ROOT_MINT_URL\" \"\$JIRA_IAM_WRITE_MINT_BODY\" \"$raw\" \"$EVDIR/mint_status.txt\"; sanitize_token_response \"$raw\" \"$EVDIR/mint_body.json\"; jq -r '.token' \"$raw\" >\"$token_tmp\""
  outcome_guard "IAM Jira write mint allowed" "assert_file_eq \"$EVDIR/mint_status.txt\" \"200\"" || return 1
  root_id="$(json_get '.root_token_id' "$EVDIR/mint_body.json")"
  token_id="$(json_get '.token_id' "$EVDIR/mint_body.json")"
  exercise_guard "write IAM-2 description through jira-tool-envoy" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_put_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-2\" '{\"description\":\"M4b audit marker\"}' \"$EVDIR/write_response.json\" \"$EVDIR/write_status.txt\""
  exercise_guard "read IAM-2 with write token through jira-tool-envoy" \
    "token=\"\$(cat \"$token_tmp\")\"; jiratool_request_to_file \"\$CAPISS_AGENT_CERT\" \"\$CAPISS_AGENT_KEY\" \"\$token\" \"IAM-2\" \"$EVDIR/read_response.json\" \"$EVDIR/read_status.txt\""
  outcome_guard "write and read allowed" \
    "assert_file_eq \"$EVDIR/write_status.txt\" \"204\" && assert_file_eq \"$EVDIR/read_status.txt\" \"200\""
  exercise_guard "capture capiss and jira-tool logs since flow start" \
    "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-capability-issuer >\"$EVDIR/capiss_container.log\" 2>&1; docker logs --since \"\$since\" spiffe-jira-tool >\"$EVDIR/jiratool_container.log\" 2>&1; grep -F '\"event_type\"' \"$EVDIR/capiss_container.log\" >\"$EVDIR/capiss_events.jsonl\" || :; grep -F '\"event_type\"' \"$EVDIR/jiratool_container.log\" >\"$EVDIR/jiratool_events.jsonl\" || :"
  outcome_guard "capiss Jira write root mint event correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$token_id\" 'select(.event_type==\"capiss_mint_decision\" and .decision_type==\"root_mint\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .aud==\"jira-tool\" and .act==\"write\" and .res==\"jira-tool:/project:IAM\" and .root_token_id==\$root and .token_id==\$token and .policy_id==\"capiss.allow.v3\")' \"$EVDIR/capiss_events.jsonl\" >/dev/null"
  outcome_guard "jira-tool write allow event correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$token_id\" 'select(.event_type==\"jiratool_enforcement_decision\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .root_token_id==\$root and .token_id==\$token and .aud==\"jira-tool\" and .act==\"write\" and .res==\"jira-tool:/project:IAM\" and .jira_operation==\"issue_description_write\" and .requested_project==\"IAM\" and .token_project==\"IAM\" and .issue_key==\"IAM-2\" and .upstream_called==true and .upstream_status==204 and (.budget_remaining|type)==\"number\")' \"$EVDIR/jiratool_events.jsonl\" >/dev/null"
  outcome_guard "jira-tool read allow event with write token correlated" \
    "jq -e --arg root \"\$root_id\" --arg token \"\$token_id\" 'select(.event_type==\"jiratool_enforcement_decision\" and .result==\"allow\" and .reason_code==\"ok\" and .subject_spiffe_id==\"spiffe://varambu.org/agent-a\" and .root_token_id==\$root and .token_id==\$token and .aud==\"jira-tool\" and .act==\"write\" and .res==\"jira-tool:/project:IAM\" and .jira_operation==\"issue_read\" and .requested_project==\"IAM\" and .token_project==\"IAM\" and .issue_key==\"IAM-2\" and .upstream_called==true and .upstream_status==200 and (.budget_remaining|type)==\"number\")' \"$EVDIR/jiratool_events.jsonl\" >/dev/null"
  return 0
}

m5_ready() {
  ensure_capiss_material &&
    ensure_jiramcp_material &&
    ensure_capiss_envoy_ready &&
    ensure_jira_mcp_envoy_ready
}

m5_mint_token_file() {
  body="$1"
  token_file="$2"
  prefix="$3"
  jira_mcp_mint_with_body_to_file "$body" "$EVDIR/${prefix}_mint.json" "$EVDIR/${prefix}_mint_status.txt"
  assert_file_eq "$EVDIR/${prefix}_mint_status.txt" "200" || return 1
  jq -r '.token' "$EVDIR/${prefix}_mint.json" >"$token_file"
}

M5_T1_test() {
  begin_test_evidence "M5-T1" "mcp_launcher_session"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "adapter container is running" "container_running spiffe-codex-jira-mcp-adapter"
  premise_guard "launcher uses docker compose exec -T" "grep -Fq 'exec -T' /repo/scripts/codex_jira_mcp.sh && ! grep -Eq 'compose .* up|--build' /repo/scripts/codex_jira_mcp.sh"
  exercise_guard "list tools through launcher" \
    "mcp_launcher_message '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' \"$EVDIR/tools.json\" \"$EVDIR/launcher.err\""
  outcome_guard "stdout is valid MCP JSON" "jq -e '.jsonrpc==\"2.0\" and .result.tools' \"$EVDIR/tools.json\" >/dev/null"
  outcome_guard "diagnostics are stderr-only" "! grep -Eq 'codex-jira|adapter|ERROR' \"$EVDIR/tools.json\""
  return 0
}

M5_T2_test() {
  begin_test_evidence "M5-T2" "mcp_tool_surface"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "adapter container is running" "container_running spiffe-codex-jira-mcp-adapter"
  exercise_guard "list MCP tools" "mcp_launcher_message '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' \"$EVDIR/tools.json\" \"$EVDIR/launcher.err\""
  outcome_guard "only approved tools are exposed" \
    "jq -e '[.result.tools[].name] == [\"read_project_summary\",\"create_story\"]' \"$EVDIR/tools.json\" >/dev/null"
  return 0
}

M5_T3_test() {
  begin_test_evidence "M5-T3" "iam_summary_success"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path and mock ready" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "call IAM project summary through MCP" \
    "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/summary.json\""
  exercise_guard "capture mock request log" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "IAM summary succeeds" "jq -e '.ok==true and .project.key==\"IAM\" and (.issues|length)>0 and (.epics|length)>0' \"$EVDIR/summary.json\" >/dev/null"
  outcome_guard "mock called for summary" "jq -e '.requests[] | select(.path==\"/rest/api/3/project/IAM/summary\" and .gateway_marker==\"jira-mcp-gateway\")' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T4_test() {
  begin_test_evidence "M5-T4" "summary_allowed_fields"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready" "m5_ready"
  exercise_guard "call summary" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/summary.json\""
  outcome_guard "hidden Jira fields omitted" \
    "! grep -Eiq 'description|comments|assignee|sprint|board|raw_jql|atlassian.net|Bearer|token' \"$EVDIR/summary.json\""
  return 0
}

M5_T5_test() {
  begin_test_evidence "M5-T5" "summary_bounds"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "mock has excess IAM data" "jira_mcp_mock_breadth \"$EVDIR/breadth.json\" && jq -e '.iam_count > 75' \"$EVDIR/breadth.json\" >/dev/null"
  exercise_guard "call summary" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/summary.json\""
  outcome_guard "summary counts are bounded" "jq -e '(.issues|length)<=50 and (.epics|length)<=25' \"$EVDIR/summary.json\" >/dev/null"
  return 0
}

M5_T6_test() {
  begin_test_evidence "M5-T6" "nas_summary_mint_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "call NAS summary through adapter" "mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/error.json\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "mint denied locally to Codex" "jq -e '.ok==false and .reason==\"mint_denied\"' \"$EVDIR/error.json\" >/dev/null"
  outcome_guard "gateway/mock not called" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T7_test() {
  begin_test_evidence "M5-T7" "iam_story_create"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "create IAM story through MCP" \
    "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"M5 story\",\"description\":\"M5 description\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/create.json\""
  exercise_guard "capture created stories" "jira_mcp_mock_created \"$EVDIR/created.json\""
  outcome_guard "create returns bounded metadata" "jq -e '.ok==true and .project_key==\"IAM\" and .issue_type==\"Story\" and (.key|startswith(\"IAM-\")) and (has(\"fields\")|not)' \"$EVDIR/create.json\" >/dev/null"
  outcome_guard "mock stored one story" "jq -e '.created|length==1' \"$EVDIR/created.json\" >/dev/null"
  return 0
}

M5_T8_test() {
  begin_test_evidence "M5-T8" "iam_story_create_ac"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "create IAM story with acceptance criteria" \
    "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"M5 AC story\",\"description\":\"M5 description\",\"acceptance_criteria\":[\"AC one\",\"AC two\"]}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/create.json\""
  exercise_guard "capture created stories" "jira_mcp_mock_created \"$EVDIR/created.json\""
  outcome_guard "acceptance criteria folded into ADF description" "jq -e '.created[0].fields.description.content[].content[]?.text | select(test(\"Acceptance Criteria|AC one|AC two\"))' \"$EVDIR/created.json\" >/dev/null"
  return 0
}

M5_T9_test() {
  begin_test_evidence "M5-T9" "iam_story_create_epic"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "create IAM story with valid epic" \
    "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"M5 epic story\",\"description\":\"M5 description\",\"epic_key\":\"IAM-101\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/create.json\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "create linked to epic" "jq -e '.ok==true and .epic_key==\"IAM-101\"' \"$EVDIR/create.json\" >/dev/null"
  outcome_guard "epic checked before create" "jq -e '[.requests[].path] | index(\"/rest/api/3/issue/IAM-101\") < index(\"/rest/api/3/issue\")' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T10_test() {
  begin_test_evidence "M5-T10" "invalid_epic_no_create"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "attempt create with non-Epic IAM issue" \
    "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"bad epic\",\"description\":\"d\",\"epic_key\":\"IAM-900\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/error.json\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "epic invalid returned" "jq -e '.ok==false and .reason==\"epic_invalid\"' \"$EVDIR/error.json\" >/dev/null"
  outcome_guard "no create request occurred" "jq -e '[.requests[] | select(.method==\"POST\" and .path==\"/rest/api/3/issue\")] | length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T11_test() {
  begin_test_evidence "M5-T11" "nas_create_mint_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "attempt NAS create through MCP" "mcp_tool_call create_story '{\"project_key\":\"NAS\",\"summary\":\"NAS\",\"description\":\"d\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/error.json\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "mint denied" "jq -e '.ok==false and .reason==\"mint_denied\"' \"$EVDIR/error.json\" >/dev/null"
  outcome_guard "mock untouched" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T12_test() {
  begin_test_evidence "M5-T12" "iam_token_nas_payload_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/create_token.txt"
  premise_guard "M5 path ready and create token minted" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$token_file' create"
  exercise_guard "call create endpoint with NAS payload" "token=\"\$(cat '$token_file')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"NAS\",\"summary\":\"x\",\"description\":\"d\"}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "gateway denies project mismatch" "assert_file_eq \"$EVDIR/status.txt\" \"403\" && jq -e '.reason==\"project_mismatch\"' \"$EVDIR/response.json\" >/dev/null"
  outcome_guard "no upstream call" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T13_test() {
  begin_test_evidence "M5-T13" "cross_project_epic_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "attempt create with NAS epic" "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":\"d\",\"epic_key\":\"NAS-101\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/error.json\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "cross-project epic denied" "jq -e '.reason==\"epic_invalid\"' \"$EVDIR/error.json\" >/dev/null"
  outcome_guard "no upstream call for cross-project epic" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T14_test() {
  begin_test_evidence "M5-T14" "arbitrary_fields_rejected"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/create_token.txt"
  premise_guard "M5 path ready and create token minted" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$token_file' create"
  exercise_guard "send arbitrary assignee field to gateway" "token=\"\$(cat '$token_file')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":\"d\",\"assignee\":\"bad\"}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "payload rejected" "assert_file_eq \"$EVDIR/status.txt\" \"400\" && jq -e '.reason==\"payload_invalid\"' \"$EVDIR/response.json\" >/dev/null"
  outcome_guard "no upstream call" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T15_test() {
  begin_test_evidence "M5-T15" "raw_adf_rejected"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/create_token.txt"
  premise_guard "M5 path ready and create token minted" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$token_file' create"
  exercise_guard "send raw ADF description" "token=\"\$(cat '$token_file')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":{\"type\":\"doc\"}}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "raw ADF rejected" "assert_file_eq \"$EVDIR/status.txt\" \"400\" && jq -e '.reason==\"payload_invalid\"' \"$EVDIR/response.json\" >/dev/null"
  outcome_guard "no upstream call" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T16_test() {
  begin_test_evidence "M5-T16" "adapter_forwards_nas_to_capiss"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "call NAS summary through adapter" "mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/error.json\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "adapter reports capiss mint denial" "jq -e '.ok==false and .reason==\"mint_denied\"' \"$EVDIR/error.json\" >/dev/null"
  outcome_guard "adapter stderr records mint_denied, not local project denial" "grep -Fq 'mint_denied' \"$EVDIR/adapter.err\" && ! grep -Fq 'local_authorization' \"$EVDIR/adapter.err\""
  outcome_guard "upstream not called" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T17_test() {
  begin_test_evidence "M5-T17" "unsupported_action_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 capiss material ready" "m5_ready"
  exercise_guard "attempt unsupported M5 action mint" "jira_mcp_mint_with_body_to_file '$JIRA_MCP_UNSUPPORTED_MINT_BODY' \"$EVDIR/mint.json\" \"$EVDIR/status.txt\""
  outcome_guard "unsupported action denied" "assert_file_eq \"$EVDIR/status.txt\" \"403\" && jq -e '.reason==\"policy\"' \"$EVDIR/mint.json\" >/dev/null"
  return 0
}

M5_T18_test() {
  begin_test_evidence "M5-T18" "old_jira_authority_separated"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "capiss and M5 gateway ready" "m5_ready"
  exercise_guard "adapter cannot mint old jira-tool resource for M5 subject" "jira_mcp_mint_with_body_to_file '{\"aud\":\"jira-tool\",\"act\":\"read\",\"res\":\"jira-tool:/project:IAM\"}' \"$EVDIR/mint.json\" \"$EVDIR/status.txt\""
  outcome_guard "old authority denied for adapter" "assert_file_eq \"$EVDIR/status.txt\" \"403\" && jq -e '.reason==\"policy\"' \"$EVDIR/mint.json\" >/dev/null"
  return 0
}

M5_T19_test() {
  begin_test_evidence "M5-T19" "m4_jira_not_disturbed"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M4 Jira policy entries still present" "grep -Fq 'aud == \"jira-tool\"' /repo/services/opa/policy.rego && grep -Fq 'jira-tool:/project:IAM' /repo/services/opa/policy.rego"
  exercise_guard "M4 jira-tool health remains reachable" "ensure_capiss_material && ensure_jira_envoy_ready"
  outcome_guard "M4 jira-tool envoy identity verified" "test -n \"${JIRA_ENVOY_IP:-}\""
  return 0
}

M5_T20_test() {
  begin_test_evidence "M5-T20" "endpoint_bound_action"
  echo "EVIDENCE_DIR=$EVDIR"
  read_token="$EVDIR/read_token.txt"
  create_token="$EVDIR/create_token.txt"
  premise_guard "M5 tokens minted" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_SUMMARY_MINT_BODY' '$read_token' read && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$create_token' create"
  exercise_guard "use read token on create endpoint" "token=\"\$(cat '$read_token')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":\"d\"}' \"$EVDIR/read_on_create.json\" \"$EVDIR/read_on_create_status.txt\""
  exercise_guard "use create token on summary endpoint" "token=\"\$(cat '$create_token')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_SUMMARY_URL\" '{\"project_key\":\"IAM\"}' \"$EVDIR/create_on_read.json\" \"$EVDIR/create_on_read_status.txt\""
  outcome_guard "endpoint/action mismatches denied" "jq -e '.reason==\"act_mismatch\"' \"$EVDIR/read_on_create.json\" >/dev/null && jq -e '.reason==\"act_mismatch\"' \"$EVDIR/create_on_read.json\" >/dev/null"
  return 0
}

M5_T21_test() {
  begin_test_evidence "M5-T21" "audience_mismatch_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 capiss material ready" "m5_ready"
  exercise_guard "attempt wrong-audience M5 resource mint" "jira_mcp_mint_with_body_to_file '{\"aud\":\"jira-tool\",\"act\":\"read_project_summary\",\"res\":\"jira-mcp:/project:IAM\"}' \"$EVDIR/mint.json\" \"$EVDIR/status.txt\""
  outcome_guard "wrong audience/resource family denied" "assert_file_any \"$EVDIR/status.txt\" \"400\" \"403\""
  return 0
}

M5_T22_test() {
  begin_test_evidence "M5-T22" "stolen_token_subject_mismatch"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/read_token.txt"
  premise_guard "M5 read token minted" "m5_ready && ensure_capiss_material && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_SUMMARY_MINT_BODY' '$token_file' read"
  exercise_guard "rogue presents adapter token to gateway" "token=\"\$(cat '$token_file')\"; jira_mcp_rogue_request_to_file \"\$token\" \"$JIRA_MCP_SUMMARY_URL\" '{\"project_key\":\"IAM\"}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  outcome_guard "subject mismatch denied" "assert_file_eq \"$EVDIR/status.txt\" \"403\" && jq -e '.reason==\"subject_mismatch\"' \"$EVDIR/response.json\" >/dev/null"
  return 0
}

M5_T23_test() {
  begin_test_evidence "M5-T23" "invalid_token_denied"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 gateway ready" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "call gateway with invalid token" "jira_mcp_request_to_file 'not-a-token' \"$JIRA_MCP_SUMMARY_URL\" '{\"project_key\":\"IAM\"}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "invalid token denied" "assert_file_eq \"$EVDIR/status.txt\" \"401\" && jq -e '.reason==\"token_invalid\"' \"$EVDIR/response.json\" >/dev/null"
  outcome_guard "upstream not called" "jq -e '.requests|length==0' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T24_test() {
  begin_test_evidence "M5-T24" "direct_app_bypass_unavailable"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 edge path reachable" "m5_ready"
  exercise_guard "attempt direct gateway app from test harness" "set +e; curl -sS --max-time 2 http://jira-mcp-gateway:8080/health >\"$EVDIR/direct_gateway.out\" 2>&1; rc=\$?; set -e; echo \$rc >\"$EVDIR/direct_gateway_rc.txt\""
  outcome_guard "direct app path not available from edge/test context" "rc=\$(cat \"$EVDIR/direct_gateway_rc.txt\"); [ \"\$rc\" -ne 0 ] && grep -Eiq '(Could not resolve|timed out|No route|Failed to connect)' \"$EVDIR/direct_gateway.out\""
  return 0
}

M5_T25_test() {
  begin_test_evidence "M5-T25" "only_gateway_calls_mock"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "run allowed and denied MCP calls" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/iam.json\" \"$EVDIR/iam.err\"; mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/nas.json\" \"$EVDIR/nas.err\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "all mock requests carry gateway marker" "jq -e '(.requests|length)>0 and all(.requests[]; .gateway_marker==\"jira-mcp-gateway\")' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T26_test() {
  begin_test_evidence "M5-T26" "mcp_responses_no_tokens"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready" "m5_ready"
  exercise_guard "call summary and create" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/summary_mcp.json\" \"$EVDIR/summary.err\"; mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":\"d\"}' \"$EVDIR/create_mcp.json\" \"$EVDIR/create.err\""
  outcome_guard "Codex-visible stdout contains no bearer token material" "! grep -Eiq 'Bearer |token_type|\"token\"|Biscuit|JIRA_API_TOKEN' \"$EVDIR/summary_mcp.json\" \"$EVDIR/create_mcp.json\""
  return 0
}

M5_T27_test() {
  begin_test_evidence "M5-T27" "adapter_logs_no_tokens"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready" "m5_ready"
  exercise_guard "call summary and capture adapter stderr" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/summary_mcp.json\" \"$EVDIR/adapter.err\""
  outcome_guard "adapter stderr contains metadata but no bearer token" "grep -Fq 'adapter_decision' \"$EVDIR/adapter.err\" && ! grep -Eiq 'Bearer |\"token\"|token_type|Biscuit' \"$EVDIR/adapter.err\""
  return 0
}

M5_T28_test() {
  begin_test_evidence "M5-T28" "adapter_env_no_jira_secret"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "adapter container running" "container_running spiffe-codex-jira-mcp-adapter"
  exercise_guard "capture adapter environment" "docker exec spiffe-codex-jira-mcp-adapter env | sort >\"$EVDIR/adapter_env.txt\""
  outcome_guard "adapter has no Jira credential env" "! grep -E 'JIRA_API_TOKEN|JIRA_EMAIL|JIRA_BASE_URL' \"$EVDIR/adapter_env.txt\""
  return 0
}

M5_T30_test() {
  begin_test_evidence "M5-T30" "upstream_header_stripping"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and mock reset" "m5_ready && jira_mcp_mock_reset"
  exercise_guard "create story through gateway" "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"header\",\"description\":\"d\"}' \"$EVDIR/create_mcp.json\" \"$EVDIR/adapter.err\""
  exercise_guard "capture mock requests" "jira_mcp_mock_request_log \"$EVDIR/mock_requests.json\""
  outcome_guard "mock did not receive Authorization header in mock mode" "jq -e 'all(.requests[]; .authorization_present==false)' \"$EVDIR/mock_requests.json\" >/dev/null"
  return 0
}

M5_T31_test() {
  begin_test_evidence "M5-T31" "summary_budget_governance"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/read_token.txt"
  premise_guard "M5 read token minted" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_SUMMARY_MINT_BODY' '$token_file' read"
  exercise_guard "use same summary token until budget exhausted" "token=\"\$(cat '$token_file')\"; : >\"$EVDIR/statuses.txt\"; i=1; while [ \$i -le 11 ]; do jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_SUMMARY_URL\" '{\"project_key\":\"IAM\"}' \"$EVDIR/resp_\$i.json\" \"$EVDIR/status_\$i.txt\"; cat \"$EVDIR/status_\$i.txt\" >>\"$EVDIR/statuses.txt\"; echo >>\"$EVDIR/statuses.txt\"; i=\$((i+1)); done"
  outcome_guard "eleventh summary denied by budget" "test \"\$(grep -c '^200$' \"$EVDIR/statuses.txt\")\" -eq 10 && grep -Fxq '403' \"$EVDIR/status_11.txt\" && jq -e '.reason==\"budget_exhausted\"' \"$EVDIR/resp_11.json\" >/dev/null"
  return 0
}

M5_T32_test() {
  begin_test_evidence "M5-T32" "create_budget_before_upstream"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 ready and log baseline captured" "m5_ready && jira_mcp_mock_reset && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "create story" "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"budget\",\"description\":\"d\"}' \"$EVDIR/create_mcp.json\" \"$EVDIR/adapter.err\""
  exercise_guard "capture gateway logs" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-jira-mcp-gateway >\"$EVDIR/gateway.log\" 2>&1"
  outcome_guard "gateway allow event has budget remaining and upstream create" "grep -F 'jiramcp_gateway_decision' \"$EVDIR/gateway.log\" | jq -e 'select(.decision==\"allow\" and .upstream_operation==\"story_create\" and (.budget_remaining|type)==\"number\")' >/dev/null"
  return 0
}

M5_T33_test() {
  begin_test_evidence "M5-T33" "budget_exhaustion_denies_create"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/create_token.txt"
  premise_guard "M5 create token minted" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$token_file' create"
  exercise_guard "exhaust create token budget then attempt create" "token=\"\$(cat '$token_file')\"; i=1; while [ \$i -le 10 ]; do jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":\"d\"}' \"$EVDIR/create_\$i.json\" \"$EVDIR/status_\$i.txt\"; i=\$((i+1)); done; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":\"d\"}' \"$EVDIR/denied.json\" \"$EVDIR/denied_status.txt\""
  outcome_guard "exhausted create denied before upstream" "assert_file_eq \"$EVDIR/denied_status.txt\" \"403\" && jq -e '.reason==\"budget_exhausted\"' \"$EVDIR/denied.json\" >/dev/null"
  return 0
}

M5_T34_test() {
  begin_test_evidence "M5-T34" "prevalidation_no_budget_spend"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/create_token.txt"
  premise_guard "M5 create token minted" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$token_file' create"
  exercise_guard "send invalid payload before valid create" "token=\"\$(cat '$token_file')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":{\"type\":\"doc\"}}' \"$EVDIR/invalid.json\" \"$EVDIR/invalid_status.txt\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"valid\",\"description\":\"d\"}' \"$EVDIR/valid.json\" \"$EVDIR/valid_status.txt\""
  outcome_guard "invalid payload did not consume budget needed by valid create" "assert_file_eq \"$EVDIR/invalid_status.txt\" \"400\" && assert_file_eq \"$EVDIR/valid_status.txt\" \"201\""
  return 0
}

M5_T35_test() {
  begin_test_evidence "M5-T35" "upstream_failure_no_refund"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/create_token.txt"
  premise_guard "M5 create token minted and mock failure armed" "m5_ready && jira_mcp_mock_reset && jira_mcp_mock_fail_next_create && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$token_file' create"
  exercise_guard "authorized create hits injected upstream failure" "token=\"\$(cat '$token_file')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"fail\",\"description\":\"d\"}' \"$EVDIR/fail.json\" \"$EVDIR/fail_status.txt\""
  outcome_guard "upstream error is standardized after spend" "assert_file_eq \"$EVDIR/fail_status.txt\" \"502\" && jq -e '.reason==\"upstream_error\"' \"$EVDIR/fail.json\" >/dev/null"
  return 0
}

M5_T36_test() {
  begin_test_evidence "M5-T36" "read_audit_correlation"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and log baseline captured" "m5_ready && jira_mcp_mock_reset && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "call summary" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/summary.json\""
  exercise_guard "capture logs" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-capability-issuer >\"$EVDIR/capiss.log\" 2>&1; docker logs --since \"\$since\" spiffe-jira-mcp-gateway >\"$EVDIR/gateway.log\" 2>&1"
  outcome_guard "gateway read allow event present" "grep -F 'jiramcp_gateway_decision' \"$EVDIR/gateway.log\" | jq -e 'select(.decision==\"allow\" and .upstream_operation==\"project_summary\" and .aud==\"jira-mcp-gateway\" and .act==\"read_project_summary\")' >/dev/null"
  outcome_guard "capiss M5 mint event present" "grep -F 'capiss_mint_decision' \"$EVDIR/capiss.log\" | jq -e 'select(.result==\"allow\" and .aud==\"jira-mcp-gateway\" and .act==\"read_project_summary\")' >/dev/null"
  return 0
}

M5_T37_test() {
  begin_test_evidence "M5-T37" "create_audit_correlation"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "M5 path ready and log baseline captured" "m5_ready && jira_mcp_mock_reset && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "create story" "mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"audit\",\"description\":\"d\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/create.json\""
  exercise_guard "capture gateway logs" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-jira-mcp-gateway >\"$EVDIR/gateway.log\" 2>&1"
  outcome_guard "gateway create allow event present" "grep -F 'jiramcp_gateway_decision' \"$EVDIR/gateway.log\" | jq -e 'select(.decision==\"allow\" and .upstream_operation==\"story_create\" and .issue_key)' >/dev/null"
  return 0
}

M5_T38_test() {
  begin_test_evidence "M5-T38" "deny_decision_events"
  echo "EVIDENCE_DIR=$EVDIR"
  token_file="$EVDIR/create_token.txt"
  premise_guard "M5 token and log baseline ready" "m5_ready && jira_mcp_mock_reset && m5_mint_token_file '$JIRA_MCP_IAM_CREATE_MINT_BODY' '$token_file' create && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "trigger payload deny" "token=\"\$(cat '$token_file')\"; jira_mcp_request_to_file \"\$token\" \"$JIRA_MCP_STORIES_URL\" '{\"project_key\":\"IAM\",\"summary\":\"x\",\"description\":{\"type\":\"doc\"}}' \"$EVDIR/response.json\" \"$EVDIR/status.txt\""
  exercise_guard "capture gateway logs" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; docker logs --since \"\$since\" spiffe-jira-mcp-gateway >\"$EVDIR/gateway.log\" 2>&1"
  outcome_guard "deny decision event present" "grep -F 'jiramcp_gateway_decision' \"$EVDIR/gateway.log\" | jq -e 'select(.decision==\"deny\" and .reason_code==\"payload_invalid\")' >/dev/null"
  return 0
}

M5_T39_test() {
  begin_test_evidence "M5-T39" "standard_errors_no_existence_leak"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "mock proves NAS exists and M5 path ready" "jira_mcp_mock_breadth \"$EVDIR/breadth.json\" && jq -e '.projects | index(\"NAS\")' \"$EVDIR/breadth.json\" >/dev/null && m5_ready"
  exercise_guard "attempt NAS summary" "mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/mcp_response.json\" \"$EVDIR/adapter.err\" && mcp_text_json_to_file \"$EVDIR/mcp_response.json\" \"$EVDIR/error.json\""
  outcome_guard "standard local error has no upstream detail" "jq -e '.ok==false and .reason==\"mint_denied\" and (has(\"project\")|not) and (has(\"issues\")|not)' \"$EVDIR/error.json\" >/dev/null"
  return 0
}

M5_T40_test() {
  begin_test_evidence "M5-T40" "mock_breadth"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "jira-mcp-mock reachable" "wait_dns jira-mcp-mock 30"
  exercise_guard "capture mock breadth" "jira_mcp_mock_breadth \"$EVDIR/breadth.json\""
  outcome_guard "mock has IAM and NAS data" "jq -e '(.projects|sort)==[\"IAM\",\"NAS\"] and .iam_count>75 and .nas_count>=4' \"$EVDIR/breadth.json\" >/dev/null"
  return 0
}

M5_T41_test() {
  begin_test_evidence "M5-T41" "protected_path_narrows_mock"
  echo "EVIDENCE_DIR=$EVDIR"
  premise_guard "mock breadth and M5 path ready" "jira_mcp_mock_breadth \"$EVDIR/breadth.json\" && m5_ready && jira_mcp_mock_reset"
  exercise_guard "allowed IAM and denied NAS through MCP" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/iam_mcp.json\" \"$EVDIR/iam.err\" && mcp_text_json_to_file \"$EVDIR/iam_mcp.json\" \"$EVDIR/iam.json\"; mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/nas_mcp.json\" \"$EVDIR/nas.err\" && mcp_text_json_to_file \"$EVDIR/nas_mcp.json\" \"$EVDIR/nas.json\""
  outcome_guard "protected path allows IAM and denies NAS" "jq -e '.ok==true and .project.key==\"IAM\"' \"$EVDIR/iam.json\" >/dev/null && jq -e '.ok==false and .reason==\"mint_denied\"' \"$EVDIR/nas.json\" >/dev/null"
  return 0
}

M5_T42_test() {
  begin_test_evidence "M5-T42" "varambu_capiss_audit_files"
  echo "EVIDENCE_DIR=$EVDIR"
  session_dir="/repo/artifacts/varambu-demo/e2e-M5-T42"
  premise_guard "M5 path ready and audit session prepared" "m5_ready && jira_mcp_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "start Varambu capiss audit tailer" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; : >\"$session_dir/capiss_audit.jsonl\"; : >\"$session_dir/capiss_audit.log\"; python3 /repo/scripts/varambu_audit.py tail --since \"\$since\" --jsonl \"$session_dir/capiss_audit.jsonl\" --human \"$session_dir/capiss_audit.log\" --err \"$session_dir/audit_tailer.err\" >/dev/null 2>>\"$session_dir/audit_tailer.err\" & echo \$! >\"$session_dir/audit_tailer.pid\"; sleep 2; kill -0 \"\$(cat \"$session_dir/audit_tailer.pid\")\""
  exercise_guard "perform allowed and denied MCP requests" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/iam_read_mcp.json\" \"$EVDIR/iam_read.err\" && mcp_text_json_to_file \"$EVDIR/iam_read_mcp.json\" \"$EVDIR/iam_read.json\"; mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"audit e2e\",\"description\":\"d\"}' \"$EVDIR/iam_create_mcp.json\" \"$EVDIR/iam_create.err\" && mcp_text_json_to_file \"$EVDIR/iam_create_mcp.json\" \"$EVDIR/iam_create.json\"; mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/nas_read_mcp.json\" \"$EVDIR/nas_read.err\" && mcp_text_json_to_file \"$EVDIR/nas_read_mcp.json\" \"$EVDIR/nas_read.json\"; mcp_tool_call create_story '{\"project_key\":\"NAS\",\"summary\":\"denied\",\"description\":\"d\"}' \"$EVDIR/nas_create_mcp.json\" \"$EVDIR/nas_create.err\" && mcp_text_json_to_file \"$EVDIR/nas_create_mcp.json\" \"$EVDIR/nas_create.json\""
  exercise_guard "wait for audit entries and stop tailer" "i=1; while [ \$i -le 30 ]; do [ \"\$(wc -l <\"$session_dir/capiss_audit.jsonl\")\" -ge 4 ] && break; sleep 1; i=\$((i+1)); done; kill \"\$(cat \"$session_dir/audit_tailer.pid\")\" 2>/dev/null || true; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/capiss_audit.jsonl\"; cp \"$session_dir/capiss_audit.log\" \"$EVDIR/capiss_audit.log\""
  exercise_guard "render persisted audit through varambu cli" "bash /repo/varambu audit --json >\"$EVDIR/varambu_audit_json.out\""
  outcome_guard "audit file contains two minted and two denied entries in append order" "jq -s 'length>=4 and .[0].result==\"allow\" and .[0].act==\"read_project_summary\" and .[1].result==\"allow\" and .[1].act==\"create_story\" and .[2].result==\"deny\" and .[2].res==\"jira-mcp:/project:NAS\" and .[3].result==\"deny\" and .[3].res==\"jira-mcp:/project:NAS\"' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "minted rows include subject token validity local utc and correlation metadata" "jq -s '.[0].subject_spiffe_id==\"spiffe://varambu.org/codex-jira-mcp-adapter\" and (.[0].token_id|type)==\"string\" and (.[0].root_token_id|type)==\"string\" and (.[0].issued_at_local|type)==\"string\" and (.[0].expires_at_local|type)==\"string\" and (.[0].issued_at_utc|type)==\"string\" and (.[0].expires_at_utc|type)==\"string\" and (.[0].timestamp_local|type)==\"string\" and (.[0].ttl_seconds|type)==\"number\" and (.[0].correlation_id|type)==\"string\"' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "denied rows include reason and omit token validity" "jq -s '.[2].reason_code==\"policy\" and (.[2]|has(\"token_id\")|not) and (.[2]|has(\"issued_at_utc\")|not) and (.[2]|has(\"expires_at_utc\")|not) and (.[2].resource_attrs.project_key)==\"NAS\"' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "audit artifacts do not expose bearer token values or upstream secrets" "! grep -E '\"token\"|Bearer |Basic |JIRA_API_TOKEN' \"$EVDIR/capiss_audit.jsonl\" \"$EVDIR/capiss_audit.log\" \"$EVDIR/varambu_audit_json.out\""
  outcome_guard "human log is readable and includes logged time" "grep -Fq 'MINTED OK' \"$EVDIR/capiss_audit.log\" && grep -Fq 'DENIED: Reason Policy' \"$EVDIR/capiss_audit.log\" && grep -Fq 'Logged At:' \"$EVDIR/capiss_audit.log\""
  return 0
}

M5_T43_test() {
  begin_test_evidence "M5-T43" "varambu_audit_active_append"
  session_dir="/repo/artifacts/varambu-demo/e2e-M5-T43"
  premise_guard "M5 path ready and empty audit session prepared" "m5_ready && jira_mcp_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && sleep 2 && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "start audit tailer" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; : >\"$session_dir/capiss_audit.jsonl\"; : >\"$session_dir/capiss_audit.log\"; python3 /repo/scripts/varambu_audit.py tail --since \"\$since\" --jsonl \"$session_dir/capiss_audit.jsonl\" --human \"$session_dir/capiss_audit.log\" --err \"$session_dir/audit_tailer.err\" >/dev/null 2>>\"$session_dir/audit_tailer.err\" & echo \$! >\"$session_dir/audit_tailer.pid\"; sleep 2; kill -0 \"\$(cat \"$session_dir/audit_tailer.pid\")\""
  exercise_guard "perform one allowed mint request" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/iam_mcp.json\" \"$EVDIR/iam.err\""
  exercise_guard "wait for first entry and snapshot jsonl line count" "i=1; while [ \$i -le 15 ]; do [ \"\$(wc -l <\"$session_dir/capiss_audit.jsonl\")\" -ge 1 ] && break; sleep 1; i=\$((i+1)); done; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/after_first.jsonl\""
  exercise_guard "render audit through varambu cli after first request" "bash /repo/varambu audit --json >\"$EVDIR/varambu_after_first.out\""
  exercise_guard "perform one denied mint request" "mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/nas_mcp.json\" \"$EVDIR/nas.err\""
  exercise_guard "wait for second entry and stop tailer" "i=1; while [ \$i -le 15 ]; do [ \"\$(wc -l <\"$session_dir/capiss_audit.jsonl\")\" -ge 2 ] && break; sleep 1; i=\$((i+1)); done; kill \"\$(cat \"$session_dir/audit_tailer.pid\")\" 2>/dev/null || true; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/after_second.jsonl\""
  outcome_guard "first snapshot has exactly one entry" "[ \"\$(wc -l <\"$EVDIR/after_first.jsonl\")\" -eq 1 ]"
  outcome_guard "varambu cli output matches persisted first entry without synthesis" "diff -q \"$EVDIR/after_first.jsonl\" \"$EVDIR/varambu_after_first.out\" >/dev/null"
  outcome_guard "second entry appended after first in request order" "[ \"\$(wc -l <\"$EVDIR/after_second.jsonl\")\" -eq 2 ] && jq -rn '[inputs] | .[0].result' \"$EVDIR/after_second.jsonl\" | grep -q allow && jq -rn '[inputs] | .[1].result' \"$EVDIR/after_second.jsonl\" | grep -q deny"
  return 0
}

M5_T44_test() {
  begin_test_evidence "M5-T44" "varambu_audit_session_and_history"
  session1="/repo/artifacts/varambu-demo/e2e-M5-T44-s1"
  session2="/repo/artifacts/varambu-demo/e2e-M5-T44-s2"
  premise_guard "two synthetic sessions exist with distinct records and current points to session 2" "mkdir -p /repo/artifacts/varambu-demo && find /repo/artifacts/varambu-demo -mindepth 1 -maxdepth 1 -exec rm -rf {} + && mkdir -p \"$session1\" \"$session2\" && printf '{\"sequence\":1,\"result\":\"allow\",\"reason_code\":\"ok\"}\n' >\"$session1/capiss_audit.jsonl\" && printf '#1 MINTED OK  -\n' >\"$session1/capiss_audit.log\" && printf '{\"sequence\":1,\"result\":\"deny\",\"reason_code\":\"policy\"}\n' >\"$session2/capiss_audit.jsonl\" && printf '#1 DENIED: Reason Policy  -\n' >\"$session2/capiss_audit.log\" && ln -sfn \"$session2\" /repo/artifacts/varambu-demo/current"
  exercise_guard "show default current session audit" "bash /repo/varambu audit >\"$EVDIR/current.out\" 2>\"$EVDIR/current.err\""
  exercise_guard "show all sessions audit" "bash /repo/varambu audit --all >\"$EVDIR/all.out\" 2>\"$EVDIR/all.err\""
  exercise_guard "get current session audit file paths" "bash /repo/varambu audit-file >\"$EVDIR/paths.out\" 2>\"$EVDIR/paths.err\""
  exercise_guard "get all sessions audit file paths" "bash /repo/varambu audit-file --all >\"$EVDIR/paths_all.out\" 2>\"$EVDIR/paths_all.err\""
  outcome_guard "default audit shows only current session denied record" "grep -q 'DENIED' \"$EVDIR/current.out\" && ! grep -q 'MINTED' \"$EVDIR/current.out\""
  outcome_guard "all sessions audit shows both minted and denied records" "grep -q 'MINTED' \"$EVDIR/all.out\" && grep -q 'DENIED' \"$EVDIR/all.out\""
  outcome_guard "no cross-session deduplification" "[ \"\$(grep -c 'MINTED\|DENIED' \"$EVDIR/all.out\")\" -eq 2 ]"
  outcome_guard "audit-file paths point to existing readable files" "paths_ok=1; while IFS= read -r p; do p=\"\${p#*=}\"; [ -f \"\$p\" ] || { echo \"missing: \$p\"; paths_ok=0; }; done <\"$EVDIR/paths.out\"; [ \"\$paths_ok\" -eq 1 ]"
  outcome_guard "audit-file --all exposes paths for both sessions" "grep -c 'capiss_audit' \"$EVDIR/paths_all.out\" | grep -q '[2-9]'"
  return 0
}

M5_T45_test() {
  begin_test_evidence "M5-T45" "varambu_audit_secret_exclusion"
  session_dir="/repo/artifacts/varambu-demo/e2e-M5-T45"
  premise_guard "M5 path ready and audit session prepared" "m5_ready && jira_mcp_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "start audit tailer" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; : >\"$session_dir/capiss_audit.jsonl\"; : >\"$session_dir/capiss_audit.log\"; python3 /repo/scripts/varambu_audit.py tail --since \"\$since\" --jsonl \"$session_dir/capiss_audit.jsonl\" --human \"$session_dir/capiss_audit.log\" --err \"$session_dir/audit_tailer.err\" >/dev/null 2>>\"$session_dir/audit_tailer.err\" & echo \$! >\"$session_dir/audit_tailer.pid\"; sleep 2; kill -0 \"\$(cat \"$session_dir/audit_tailer.pid\")\""
  exercise_guard "perform allowed and denied MCP requests" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/iam_mcp.json\" \"$EVDIR/iam.err\"; mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"t45\",\"description\":\"d\"}' \"$EVDIR/iam_create_mcp.json\" \"$EVDIR/iam_create.err\"; mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/nas_mcp.json\" \"$EVDIR/nas.err\""
  exercise_guard "wait for entries and stop tailer" "i=1; while [ \$i -le 30 ]; do [ \"\$(wc -l <\"$session_dir/capiss_audit.jsonl\")\" -ge 3 ] && break; sleep 1; i=\$((i+1)); done; kill \"\$(cat \"$session_dir/audit_tailer.pid\")\" 2>/dev/null || true; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/capiss_audit.jsonl\"; cp \"$session_dir/capiss_audit.log\" \"$EVDIR/capiss_audit.log\"; cp \"$session_dir/audit_tailer.err\" \"$EVDIR/audit_tailer.err\""
  exercise_guard "render audit through varambu cli" "bash /repo/varambu audit --json >\"$EVDIR/varambu_audit.out\""
  outcome_guard "no bearer token values in jsonl evidence" "! grep -E 'Bearer |\"token\":\s*\"[A-Za-z0-9+/]{20,}' \"$EVDIR/capiss_audit.jsonl\""
  outcome_guard "no bearer token values in human log evidence" "! grep -E 'Bearer |Basic ' \"$EVDIR/capiss_audit.log\""
  outcome_guard "no upstream credentials in tailer diagnostics" "! grep -E 'Bearer |Basic |JIRA_API_TOKEN' \"$EVDIR/audit_tailer.err\""
  outcome_guard "no bearer token values in varambu cli output" "! grep -E 'Bearer |Basic ' \"$EVDIR/varambu_audit.out\""
  outcome_guard "token identifiers are present but contain only identifier chars" "jq -e 'select(.token_id != null) | .token_id | test(\"^[a-f0-9-]+$\")' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  return 0
}

M5_T46_test() {
  begin_test_evidence "M5-T46" "varambu_audit_stale_tailer_warning"
  session_dir="/repo/artifacts/varambu-demo/e2e-M5-T46"
  premise_guard "session with dead tailer PID prepared" "rm -rf \"$session_dir\" && mkdir -p \"$session_dir\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && printf '#1 MINTED OK  -\nLogged At:    -\n\n' >\"$session_dir/capiss_audit.log\" && printf '{\"sequence\":1,\"result\":\"allow\",\"reason_code\":\"ok\"}\n' >\"$session_dir/capiss_audit.jsonl\" && echo 99999999 >\"$session_dir/audit_tailer.pid\""
  exercise_guard "run non-strict audit with dead tailer" "bash /repo/varambu audit >\"$EVDIR/audit_warn.out\" 2>\"$EVDIR/audit_warn.err\""
  exercise_guard "capture strict audit exit code" "bash /repo/varambu audit --strict >\"$EVDIR/audit_strict.out\" 2>\"$EVDIR/audit_strict.err\"; echo \$? >\"$EVDIR/strict_rc.txt\""
  outcome_guard "non-strict audit emits stale tailer warning to stderr" "grep -qi 'WARNING.*tailer' \"$EVDIR/audit_warn.err\""
  outcome_guard "non-strict audit still prints persisted evidence" "grep -q 'MINTED' \"$EVDIR/audit_warn.out\""
  outcome_guard "strict audit exits with non-zero code" "[ \"\$(cat \"$EVDIR/strict_rc.txt\")\" != \"0\" ]"
  return 0
}

M5_T47_test() {
  begin_test_evidence "M5-T47" "varambu_audit_timing_semantics"
  session_dir="/repo/artifacts/varambu-demo/e2e-M5-T47"
  premise_guard "M5 path ready and audit session prepared" "m5_ready && jira_mcp_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "start audit tailer" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; : >\"$session_dir/capiss_audit.jsonl\"; : >\"$session_dir/capiss_audit.log\"; python3 /repo/scripts/varambu_audit.py tail --since \"\$since\" --jsonl \"$session_dir/capiss_audit.jsonl\" --human \"$session_dir/capiss_audit.log\" --err \"$session_dir/audit_tailer.err\" >/dev/null 2>>\"$session_dir/audit_tailer.err\" & echo \$! >\"$session_dir/audit_tailer.pid\"; sleep 2; kill -0 \"\$(cat \"$session_dir/audit_tailer.pid\")\""
  exercise_guard "perform allowed and denied mint requests" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/iam_mcp.json\" \"$EVDIR/iam.err\"; mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/nas_mcp.json\" \"$EVDIR/nas.err\""
  exercise_guard "wait for entries and stop tailer" "i=1; while [ \$i -le 20 ]; do [ \"\$(wc -l <\"$session_dir/capiss_audit.jsonl\")\" -ge 2 ] && break; sleep 1; i=\$((i+1)); done; kill \"\$(cat \"$session_dir/audit_tailer.pid\")\" 2>/dev/null || true; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/capiss_audit.jsonl\""
  outcome_guard "minted record includes utc and local timestamps and timezone" "jq -e 'select(.result==\"allow\") | (.timestamp_utc | endswith(\"Z\")) and (.timestamp_local | test(\" [A-Za-z]\")) and (.timezone | type)==\"string\"' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "minted record includes issued expires and actual ttl" "jq -e 'select(.result==\"allow\") | (.issued_at_utc | endswith(\"Z\")) and (.expires_at_utc | endswith(\"Z\")) and (.ttl_seconds | type)==\"number\" and .ttl_seconds > 0' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "denied record includes logged timestamps and omits token validity" "jq -e 'select(.result==\"deny\") | (.timestamp_utc | endswith(\"Z\")) and (.timezone | type)==\"string\" and (has(\"issued_at_utc\") | not) and (has(\"expires_at_utc\") | not) and (has(\"ttl_seconds\") | not)' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "human log shows local time in header" "grep -E '^#[0-9]+ (MINTED|DENIED).* [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' \"$session_dir/capiss_audit.log\" >/dev/null"
  return 0
}

M5_T48_test() {
  begin_test_evidence "M5-T48" "varambu_audit_uniform_enrichment"
  session_dir="/repo/artifacts/varambu-demo/e2e-M5-T48"
  premise_guard "M5 path ready and audit session prepared" "m5_ready && jira_mcp_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/log_since.txt\""
  exercise_guard "start audit tailer" "since=\"\$(cat \"$EVDIR/log_since.txt\")\"; : >\"$session_dir/capiss_audit.jsonl\"; : >\"$session_dir/capiss_audit.log\"; python3 /repo/scripts/varambu_audit.py tail --since \"\$since\" --jsonl \"$session_dir/capiss_audit.jsonl\" --human \"$session_dir/capiss_audit.log\" --err \"$session_dir/audit_tailer.err\" >/dev/null 2>>\"$session_dir/audit_tailer.err\" & echo \$! >\"$session_dir/audit_tailer.pid\"; sleep 2; kill -0 \"\$(cat \"$session_dir/audit_tailer.pid\")\""
  exercise_guard "perform M5 read and create requests and a denied request" "mcp_tool_call read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/iam_read_mcp.json\" \"$EVDIR/iam_read.err\"; mcp_tool_call create_story '{\"project_key\":\"IAM\",\"summary\":\"t48\",\"description\":\"d\"}' \"$EVDIR/iam_create_mcp.json\" \"$EVDIR/iam_create.err\"; mcp_tool_call read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/nas_mcp.json\" \"$EVDIR/nas.err\""
  exercise_guard "wait for entries and stop tailer" "i=1; while [ \$i -le 30 ]; do [ \"\$(wc -l <\"$session_dir/capiss_audit.jsonl\")\" -ge 3 ] && break; sleep 1; i=\$((i+1)); done; kill \"\$(cat \"$session_dir/audit_tailer.pid\")\" 2>/dev/null || true; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/capiss_audit.jsonl\""
  outcome_guard "all records share the same enriched schema fields" "jq -e '[inputs] | all(has(\"result\") and has(\"reason_code\") and has(\"timestamp_utc\") and has(\"timestamp_local\") and has(\"timezone\") and has(\"policy_id\") and has(\"policy_hash\"))' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "all minted records include token validity and no bearer values" "jq -e '[inputs] | map(select(.result==\"allow\")) | all(has(\"token_id\") and has(\"issued_at_utc\") and has(\"expires_at_utc\") and has(\"ttl_seconds\"))' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "all denied records omit token validity fields" "jq -e '[inputs] | map(select(.result==\"deny\")) | all((has(\"issued_at_utc\") | not) and (has(\"expires_at_utc\") | not) and (has(\"ttl_seconds\") | not))' \"$EVDIR/capiss_audit.jsonl\" >/dev/null"
  outcome_guard "no bearer token values in any audit record" "! grep -E 'Bearer |Basic ' \"$EVDIR/capiss_audit.jsonl\""
  return 0
}

M5_T49_test() {
  begin_test_evidence "M5-T49" "trace_full_chain_allowed"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T49"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  prompt="Use the Jira MCP tools to create a story in IAM."
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "allowed create_story for IAM with adapter audit" \
    "mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"trace e2e\",\"description\":\"full chain\"}' \"$EVDIR/mcp.json\" \"$EVDIR/adapter.err\" \"$sess_rel\""
  exercise_guard "extract correlation id" \
    "mcp_cid \"$EVDIR/mcp.json\" >\"$EVDIR/cid.txt\"; grep -Eq '^[0-9a-f-]{36}$' \"$EVDIR/cid.txt\""
  exercise_guard "synthesize codex rollout carrying verbatim intent" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; { rollout_user '$prompt'; rollout_call create_story call-X '{\"project_key\":\"IAM\",\"summary\":\"trace e2e\",\"description\":\"full chain\"}'; rollout_output call-X \"\$cid\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait for in-boundary legs and stop tailers" \
    "trace_wait_inboundary \"$session_dir\" 1; trace_stop_tailers \"$session_dir\"; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/capiss_audit.jsonl\"; cp \"$session_dir/gateway_audit.jsonl\" \"$EVDIR/gateway_audit.jsonl\"; cp \"$session_dir/adapter_audit.jsonl\" \"$EVDIR/adapter_audit.jsonl\""
  exercise_guard "render trace json and human" \
    "python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock >\"$EVDIR/trace.txt\" 2>>\"$EVDIR/trace.err\"; cp \"$session_dir/trace.jsonl\" \"$EVDIR/trace.jsonl\""
  outcome_guard "exactly one chain for the correlation id" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '[.[] | select(.correlation_id==\$c)] | length==1' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "legs render in fixed seven-leg canonical order" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | [.legs[].leg] == [\"intent\",\"action\",\"adapter_request\",\"mint\",\"gateway\",\"upstream\",\"adapter_decision\"]' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "all seven legs present including a distinct upstream leg" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | .legs | all(.[]; .present==true)' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "gateway leg is enforcement allow and upstream leg carries the upstream status" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | (.legs[]|select(.leg==\"gateway\")|.fields.leg_status==\"allow\") and (.legs[]|select(.leg==\"upstream\")|.fields.upstream_status==201)' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "intent leg equals the verbatim prompt" \
    "jq -e --arg p '$prompt' 'first(.[]) | .legs[] | select(.leg==\"intent\") | .fields.user_message==\$p' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "mint, gateway, and upstream legs carry the same correlation id" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | (.legs[]|select(.leg==\"mint\")|.fields.correlation_id==\$c) and (.legs[]|select(.leg==\"gateway\")|.fields.correlation_id==\$c) and (.legs[]|select(.leg==\"upstream\")|.fields.correlation_id==\$c)' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "human render shows the redesigned labels and verbatim intent" \
    "grep -Eq '[0-9]  ADAPTER ' \"$EVDIR/trace.txt\" && grep -Fq 'RETURN TO CODEX' \"$EVDIR/trace.txt\" && grep -Fq 'MINT' \"$EVDIR/trace.txt\" && tr '\n' ' ' < \"$EVDIR/trace.txt\" | tr -s ' ' | grep -Fq '$prompt'"
  return 0
}

M5_T50_test() {
  begin_test_evidence "M5-T50" "trace_denied_mint_partial"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T50"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "denied read_project_summary for NAS with adapter audit" \
    "mcp_tool_call_traced read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/mcp.json\" \"$EVDIR/adapter.err\" \"$sess_rel\""
  exercise_guard "extract correlation id" \
    "mcp_cid \"$EVDIR/mcp.json\" >\"$EVDIR/cid.txt\"; grep -Eq '^[0-9a-f-]{36}$' \"$EVDIR/cid.txt\""
  exercise_guard "synthesize codex rollout for the denied request" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; { rollout_user 'Read the NAS project summary.'; rollout_call read_project_summary call-X '{\"project_key\":\"NAS\"}'; rollout_output call-X \"\$cid\" false; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait for capiss deny and stop tailers" \
    "trace_wait_inboundary \"$session_dir\" 0; trace_stop_tailers \"$session_dir\"; cp \"$session_dir/capiss_audit.jsonl\" \"$EVDIR/capiss_audit.jsonl\"; cp \"$session_dir/adapter_audit.jsonl\" \"$EVDIR/adapter_audit.jsonl\""
  exercise_guard "render trace json and human" \
    "python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock >\"$EVDIR/trace.txt\" 2>>\"$EVDIR/trace.err\""
  outcome_guard "trace renders without error" \
    "test ! -s \"$EVDIR/trace.err\""
  outcome_guard "mint leg present and denied" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | .legs[] | select(.leg==\"mint\") | .present==true and .fields.result==\"deny\"' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "gateway and upstream legs shown absent (partial chain ends at deny)" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | (.legs[]|select(.leg==\"gateway\")|.present==false) and (.legs[]|select(.leg==\"upstream\")|.present==false)' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "adapter_request leg still present" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | .legs[] | select(.leg==\"adapter_request\") | .present==true' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "missing leg rendered as not yet available not an error" \
    "grep -Fq 'not yet available' \"$EVDIR/trace.txt\""
  return 0
}

M5_T51_test() {
  begin_test_evidence "M5-T51" "trace_intent_pending_converge"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T51"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  prompt="Create a story in IAM after the in-boundary legs are captured."
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "allowed create_story for IAM with adapter audit" \
    "mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"converge\",\"description\":\"d\"}' \"$EVDIR/mcp.json\" \"$EVDIR/adapter.err\" \"$sess_rel\""
  exercise_guard "extract correlation id and capture in-boundary legs" \
    "mcp_cid \"$EVDIR/mcp.json\" >\"$EVDIR/cid.txt\"; grep -Eq '^[0-9a-f-]{36}$' \"$EVDIR/cid.txt\"; trace_wait_inboundary \"$session_dir\" 1; trace_stop_tailers \"$session_dir\""
  exercise_guard "render trace before rollout exists (intent pending)" \
    "python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace_before.json\" 2>\"$EVDIR/trace_before.err\""
  exercise_guard "make the rollout available then re-render" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; { rollout_user '$prompt'; rollout_call create_story call-X '{\"project_key\":\"IAM\",\"summary\":\"converge\",\"description\":\"d\"}'; rollout_output call-X \"\$cid\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace_after.json\" 2>\"$EVDIR/trace_after.err\""
  outcome_guard "first run shows in-boundary legs with intent not yet available" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | (.legs[]|select(.leg==\"intent\")|.present==false) and (.legs[]|select(.leg==\"adapter_request\")|.present==true)' \"$EVDIR/trace_before.json\" >/dev/null"
  outcome_guard "second run incorporates the verbatim intent" \
    "jq -e --arg p '$prompt' 'first(.[]) | .legs[] | select(.leg==\"intent\") | .present==true and .fields.user_message==\$p' \"$EVDIR/trace_after.json\" >/dev/null"
  return 0
}

M5_T52_test() {
  begin_test_evidence "M5-T52" "trace_multi_tool_attribution"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T52"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  prompt="Use the Jira MCP tools to read IAM and then create a story in IAM."
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "allowed read then create for IAM with adapter audit" \
    "mcp_tool_call_traced read_project_summary '{\"project_key\":\"IAM\"}' \"$EVDIR/read.json\" \"$EVDIR/read.err\" \"$sess_rel\"; mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"two tools\",\"description\":\"d\"}' \"$EVDIR/create.json\" \"$EVDIR/create.err\" \"$sess_rel\""
  exercise_guard "extract both correlation ids" \
    "mcp_cid \"$EVDIR/read.json\" >\"$EVDIR/cid_a.txt\"; mcp_cid \"$EVDIR/create.json\" >\"$EVDIR/cid_b.txt\"; grep -Eq '^[0-9a-f-]{36}$' \"$EVDIR/cid_a.txt\" && grep -Eq '^[0-9a-f-]{36}$' \"$EVDIR/cid_b.txt\""
  exercise_guard "synthesize one-turn rollout driving both tool calls" \
    "cida=\"\$(cat \"$EVDIR/cid_a.txt\")\"; cidb=\"\$(cat \"$EVDIR/cid_b.txt\")\"; { rollout_user '$prompt'; rollout_call read_project_summary call-A '{\"project_key\":\"IAM\"}'; rollout_output call-A \"\$cida\" true; rollout_call create_story call-B '{\"project_key\":\"IAM\",\"summary\":\"two tools\",\"description\":\"d\"}'; rollout_output call-B \"\$cidb\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait then render trace" \
    "trace_wait_inboundary \"$session_dir\" 1; trace_stop_tailers \"$session_dir\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\"; cp \"$session_dir/trace.jsonl\" \"$EVDIR/trace.jsonl\""
  outcome_guard "two distinct chains surfaced" \
    "cida=\"\$(cat \"$EVDIR/cid_a.txt\")\"; cidb=\"\$(cat \"$EVDIR/cid_b.txt\")\"; jq -e --arg a \"\$cida\" --arg b \"\$cidb\" '([.[]|select(.correlation_id==\$a)]|length==1) and ([.[]|select(.correlation_id==\$b)]|length==1) and (\$a!=\$b)' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "both chains attribute the same verbatim prompt" \
    "cida=\"\$(cat \"$EVDIR/cid_a.txt\")\"; cidb=\"\$(cat \"$EVDIR/cid_b.txt\")\"; jq -e --arg a \"\$cida\" --arg b \"\$cidb\" --arg p '$prompt' '(.[]|select(.correlation_id==\$a)|.legs[]|select(.leg==\"intent\")|.fields.user_message==\$p) and (.[]|select(.correlation_id==\$b)|.legs[]|select(.leg==\"intent\")|.fields.user_message==\$p)' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "each chain keeps its own M5 tool action" \
    "cida=\"\$(cat \"$EVDIR/cid_a.txt\")\"; cidb=\"\$(cat \"$EVDIR/cid_b.txt\")\"; jq -e --arg a \"\$cida\" --arg b \"\$cidb\" '(.[]|select(.correlation_id==\$a)|.legs[]|select(.leg==\"action\")|.fields.tool_name==\"read_project_summary\") and (.[]|select(.correlation_id==\$b)|.legs[]|select(.leg==\"action\")|.fields.tool_name==\"create_story\")' \"$EVDIR/trace.json\" >/dev/null"
  return 0
}

M5_T53_test() {
  begin_test_evidence "M5-T53" "trace_secret_hygiene_bounds"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T53"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "allowed create_story for IAM with adapter audit" \
    "mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"hygiene\",\"description\":\"d\"}' \"$EVDIR/mcp.json\" \"$EVDIR/adapter.err\" \"$sess_rel\""
  exercise_guard "extract correlation id" \
    "mcp_cid \"$EVDIR/mcp.json\" >\"$EVDIR/cid.txt\"; grep -Eq '^[0-9a-f-]{36}$' \"$EVDIR/cid.txt\""
  exercise_guard "synthesize rollout with secrets, over-limit text, reasoning, and exec noise" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; bigmsg=\"\$(python3 -c \"print('U'*3000)\")\"; bigsum=\"\$(python3 -c \"print('S'*1500)\")\"; args=\"\$(jq -cn --arg s \"\$bigsum\" '{project_key:\"IAM\",summary:\$s,description:\"d\",token:\"biscuit-leak-value\",authorization:\"Bearer sk-leaked-secret\"}')\"; { rollout_user \"\$bigmsg\"; jq -cn '{type:\"response_item\",timestamp:\"2026-06-19T10:00:00.500Z\",payload:{type:\"reasoning\",text:\"SECRET model chain-of-thought reasoning\"}}'; rollout_call create_story call-X \"\$args\"; jq -cn '{type:\"response_item\",timestamp:\"2026-06-19T10:00:01.500Z\",payload:{type:\"function_call\",name:\"exec_command\",call_id:\"call-E\",arguments:\"{\\\"command\\\":\\\"cat /etc/shadow\\\"}\"}}'; rollout_output call-X \"\$cid\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait then render trace" \
    "trace_wait_inboundary \"$session_dir\" 1; trace_stop_tailers \"$session_dir\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock >\"$EVDIR/trace.txt\" 2>>\"$EVDIR/trace.err\"; cp \"$session_dir/trace.jsonl\" \"$EVDIR/trace.jsonl\""
  outcome_guard "no bearer/basic/biscuit/cookie/jira secret values anywhere" \
    "! grep -E 'Bearer |Basic |biscuit|sk-leaked-secret|JIRA_API_TOKEN|[Cc]ookie:' \"$EVDIR/trace.jsonl\" \"$EVDIR/trace.txt\" \"$session_dir/capiss_audit.jsonl\" \"$session_dir/gateway_audit.jsonl\" \"$session_dir/adapter_audit.jsonl\""
  outcome_guard "forbidden field names dropped from persisted arguments" \
    "jq -e '(has(\"token\")|not) and (.arguments | (has(\"token\")|not) and (has(\"authorization\")|not))' \"$EVDIR/trace.jsonl\" >/dev/null"
  outcome_guard "over-limit user_message truncated with marker" \
    "jq -r '.user_message' \"$EVDIR/trace.jsonl\" | grep -Fq '[truncated]' && [ \"\$(jq -r '.user_message' \"$EVDIR/trace.jsonl\" | wc -c)\" -le 2049 ]"
  outcome_guard "over-limit summary truncated with marker" \
    "jq -r '.arguments.summary' \"$EVDIR/trace.jsonl\" | grep -Fq '[truncated]'"
  outcome_guard "no reasoning or exec_command content persisted in trace evidence" \
    "! grep -E 'chain-of-thought|exec_command|/etc/shadow' \"$EVDIR/trace.jsonl\""
  return 0
}

M5_T54_test() {
  begin_test_evidence "M5-T54" "trace_agent_tamper_detection"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T54"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "denied read_project_summary for NAS with adapter audit" \
    "mcp_tool_call_traced read_project_summary '{\"project_key\":\"NAS\"}' \"$EVDIR/mcp.json\" \"$EVDIR/adapter.err\" \"$sess_rel\""
  exercise_guard "extract correlation id" \
    "mcp_cid \"$EVDIR/mcp.json\" >\"$EVDIR/cid.txt\"; grep -Eq '^[0-9a-f-]{36}$' \"$EVDIR/cid.txt\""
  exercise_guard "forge a rollout output claiming success for the denied request" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; { rollout_user 'Read the NAS project summary.'; rollout_call read_project_summary call-X '{\"project_key\":\"NAS\"}'; rollout_output call-X \"\$cid\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait then render trace" \
    "trace_wait_inboundary \"$session_dir\" 0; trace_stop_tailers \"$session_dir\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock >\"$EVDIR/trace.txt\" 2>>\"$EVDIR/trace.err\""
  outcome_guard "forged success claim is present in the agent rollout" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -r 'select(.payload.type==\"function_call_output\") | .payload.output' \"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\" | jq -e --arg c \"\$cid\" '.ok==true and .correlation_id==\$c' >/dev/null"
  outcome_guard "in-boundary mint leg reflects the true denial" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | .legs[] | select(.leg==\"mint\") | .fields.result==\"deny\"' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "in-boundary adapter decision reflects failure not the forged success" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '.[] | select(.correlation_id==\$c) | .legs[] | select(.leg==\"adapter_decision\") | .fields.ok==false' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "human trace presents the in-boundary truth (denied)" \
    "grep -Eq 'DENIED' \"$EVDIR/trace.txt\""
  return 0
}

M5_T55_test() {
  begin_test_evidence "M5-T55" "trace_live_upstream_attested"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T55"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  upstream_mode="$(docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' spiffe-jira-mcp-gateway 2>/dev/null | sed -n 's/^JIRA_MCP_UPSTREAM_MODE=//p')"
  if [ "${upstream_mode:-mock}" != "live" ]; then
    add_warning "M5-T55 skipped: gateway not in live Jira mode (JIRA_MCP_UPSTREAM_MODE=${upstream_mode:-unset}); live upstream leg not exercised"
    return 0
  fi
  premise_guard "M5 live path ready; session prepared" \
    "m5_ready && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "allowed create_story against live Jira with adapter audit" \
    "mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"live trace\",\"description\":\"d\"}' \"$EVDIR/mcp.json\" \"$EVDIR/adapter.err\" \"$sess_rel\""
  exercise_guard "extract correlation id and synthesize rollout" \
    "mcp_cid \"$EVDIR/mcp.json\" >\"$EVDIR/cid.txt\"; cid=\"\$(cat \"$EVDIR/cid.txt\")\"; { rollout_user 'Create a story in IAM.'; rollout_call create_story call-X '{\"project_key\":\"IAM\",\"summary\":\"live trace\",\"description\":\"d\"}'; rollout_output call-X \"\$cid\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait then render trace in live mode" \
    "trace_wait_inboundary \"$session_dir\" 1; trace_stop_tailers \"$session_dir\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode live >\"$EVDIR/trace.txt\" 2>\"$EVDIR/trace.err\""
  outcome_guard "upstream leg is gateway-attested and explicitly labeled live" \
    "grep -Fq 'gateway-attested, live' \"$EVDIR/trace.txt\""
  outcome_guard "no fabricated independent upstream voice present" \
    "! grep -Eq 'jiramcp_upstream_request|mock_upstream' \"$EVDIR/trace.txt\""
  return 0
}

M5_T56_test() {
  begin_test_evidence "M5-T56" "trace_cli_surface_and_audit_nonregression"
  echo "EVIDENCE_DIR=$EVDIR"
  root="/repo/artifacts/varambu-demo"
  s1="$root/e2e-M5-T56-s1"
  s2="$root/e2e-M5-T56-s2"
  cid1="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
  cid2="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
  echo "$cid1" >"$EVDIR/cid1.txt"
  echo "$cid2" >"$EVDIR/cid2.txt"
  premise_guard "two isolated synthetic trace sessions; current points to session two" \
    "rm -rf \"$s1\" \"$s2\" && write_synth_trace_session \"$s1\" \"$cid1\" 'First session prompt.' && write_synth_trace_session \"$s2\" \"$cid2\" 'Second session prompt.' && ln -sfn \"$s2\" \"$root/current\""
  exercise_guard "run trace default, cid, all, json" \
    "bash /repo/varambu trace >\"$EVDIR/trace_default.out\" 2>\"$EVDIR/trace_default.err\"; bash /repo/varambu trace --cid \"$cid2\" >\"$EVDIR/trace_cid.out\" 2>>\"$EVDIR/trace_default.err\"; bash /repo/varambu trace --all >\"$EVDIR/trace_all.out\" 2>>\"$EVDIR/trace_default.err\"; bash /repo/varambu trace --json >\"$EVDIR/trace_json.out\" 2>>\"$EVDIR/trace_default.err\""
  exercise_guard "run audit surfaces (non-regression)" \
    "bash /repo/varambu audit >\"$EVDIR/audit.out\" 2>\"$EVDIR/audit.err\"; bash /repo/varambu audit --all >\"$EVDIR/audit_all.out\" 2>>\"$EVDIR/audit.err\"; bash /repo/varambu audit --json >\"$EVDIR/audit_json.out\" 2>>\"$EVDIR/audit.err\"; bash /repo/varambu audit-file >\"$EVDIR/audit_file.out\" 2>>\"$EVDIR/audit.err\""
  outcome_guard "default trace shows the current session chain and not the other session" \
    "grep -Fq \"$cid2\" \"$EVDIR/trace_default.out\" && ! grep -Fq \"$cid1\" \"$EVDIR/trace_default.out\""
  outcome_guard "trace --cid selects exactly the requested chain" \
    "grep -Fq \"$cid2\" \"$EVDIR/trace_cid.out\""
  outcome_guard "trace --all shows both sessions" \
    "grep -Fq \"$cid1\" \"$EVDIR/trace_all.out\" && grep -Fq \"$cid2\" \"$EVDIR/trace_all.out\""
  outcome_guard "trace --json is machine readable" \
    "jq -e 'type==\"array\"' \"$EVDIR/trace_json.out\" >/dev/null"
  outcome_guard "audit current session shows only its record (non-regression)" \
    "grep -Fq 'MINTED OK' \"$EVDIR/audit.out\" && grep -Fq \"$cid2\" \"$EVDIR/audit.out\" && ! grep -Fq \"$cid1\" \"$EVDIR/audit.out\""
  outcome_guard "audit --json parses and audit-file resolves capiss paths (non-regression)" \
    "jq -e '.result==\"allow\"' \"$EVDIR/audit_json.out\" >/dev/null && grep -Eq 'capiss_audit' \"$EVDIR/audit_file.out\""
  return 0
}

M5_T57_test() {
  begin_test_evidence "M5-T57" "trace_canonical_join_integrity"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T57"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "two allowed create_story calls with adapter audit" \
    "mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"first\",\"description\":\"d\"}' \"$EVDIR/a.json\" \"$EVDIR/a.err\" \"$sess_rel\"; mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"second\",\"description\":\"d\"}' \"$EVDIR/b.json\" \"$EVDIR/b.err\" \"$sess_rel\""
  exercise_guard "extract correlation ids and synthesize two rollout turns" \
    "mcp_cid \"$EVDIR/a.json\" >\"$EVDIR/cid_a.txt\"; mcp_cid \"$EVDIR/b.json\" >\"$EVDIR/cid_b.txt\"; cida=\"\$(cat \"$EVDIR/cid_a.txt\")\"; cidb=\"\$(cat \"$EVDIR/cid_b.txt\")\"; { rollout_user 'First create.'; rollout_call create_story call-A '{\"project_key\":\"IAM\",\"summary\":\"first\",\"description\":\"d\"}'; rollout_output call-A \"\$cida\" true; rollout_user 'Second create.'; rollout_call create_story call-B '{\"project_key\":\"IAM\",\"summary\":\"second\",\"description\":\"d\"}'; rollout_output call-B \"\$cidb\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait then render trace json" \
    "trace_wait_inboundary \"$session_dir\" 1; trace_stop_tailers \"$session_dir\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode mock --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\""
  outcome_guard "every chain renders legs in fixed canonical order" \
    "jq -e 'all(.[]; [.legs[].leg] == [\"intent\",\"action\",\"adapter_request\",\"mint\",\"gateway\",\"upstream\",\"adapter_decision\"])' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "join is by correlation id with no cross-chain leg leakage" \
    "jq -e 'all(.[]; .correlation_id as \$c | (.legs[] | select(.leg==\"mint\" and .present) | .fields.correlation_id==\$c) and (.legs[] | select(.leg==\"gateway\" and .present) | .fields.correlation_id==\$c) and (.legs[] | select(.leg==\"adapter_request\" and .present) | .fields.correlation_id==\$c))' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "two chains present with distinct correlation ids" \
    "cida=\"\$(cat \"$EVDIR/cid_a.txt\")\"; cidb=\"\$(cat \"$EVDIR/cid_b.txt\")\"; jq -e --arg a \"\$cida\" --arg b \"\$cidb\" '([.[]|select(.correlation_id==\$a)]|length==1) and ([.[]|select(.correlation_id==\$b)]|length==1)' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "each present leg preserves its own utc timestamp and sequence" \
    "jq -e 'all(.[]; all(.legs[] | select(.present); has(\"timestamp_utc\") and has(\"sequence\")))' \"$EVDIR/trace.json\" >/dev/null"
  return 0
}

M5_T58_test() {
  begin_test_evidence "M5-T58" "trace_anchor_mint_reuse_timestamps"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T58"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  fakecid="00000000-0000-4000-8000-0000000000ff"
  premise_guard "M5 path and mock ready; session prepared" \
    "m5_ready && trace_mock_reset && rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && date -u +%Y-%m-%dT%H:%M:%SZ >\"$EVDIR/since.txt\""
  exercise_guard "start capiss and gateway tailers" \
    "trace_start_tailers \"$session_dir\" \"\$(cat \"$EVDIR/since.txt\")\""
  exercise_guard "allowed create_story for IAM with adapter audit" \
    "mcp_tool_call_traced create_story '{\"project_key\":\"IAM\",\"summary\":\"anchor\",\"description\":\"d\"}' \"$EVDIR/mcp.json\" \"$EVDIR/adapter.err\" \"$sess_rel\""
  exercise_guard "extract correlation id and synthesize rollout" \
    "mcp_cid \"$EVDIR/mcp.json\" >\"$EVDIR/cid.txt\"; cid=\"\$(cat \"$EVDIR/cid.txt\")\"; { rollout_user 'Create a story in IAM.'; rollout_call create_story call-X '{\"project_key\":\"IAM\",\"summary\":\"anchor\",\"description\":\"d\"}'; rollout_output call-X \"\$cid\" true; } >\"$session_dir/codex-home/sessions/2026/06/19/rollout-1.jsonl\""
  exercise_guard "wait, stop tailers, then inject a non-M5 capiss-only mint" \
    "trace_wait_inboundary \"$session_dir\" 1; trace_stop_tailers \"$session_dir\"; jq -cn --arg c '$fakecid' '{event_type:\"capiss_mint_decision\",result:\"allow\",reason_code:\"ok\",subject_spiffe_id:\"spiffe://varambu.org/agent-a\",aud:\"tool-b\",act:\"read\",res:\"tool-b:/secret\",correlation_id:\$c,timestamp_utc:\"2026-06-19T09:00:00Z\",timestamp_local:\"2026-06-19 11:00:00 Europe/Berlin\",timezone:\"Europe/Berlin\"}' >>\"$session_dir/capiss_audit.jsonl\""
  exercise_guard "render trace json and human in a non-UTC zone" \
    "python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz Europe/Berlin --mode mock --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz Europe/Berlin --mode mock >\"$EVDIR/trace.txt\" 2>>\"$EVDIR/trace.err\""
  outcome_guard "the M5 request is surfaced as a chain" \
    "cid=\"\$(cat \"$EVDIR/cid.txt\")\"; jq -e --arg c \"\$cid\" '[.[]|select(.correlation_id==\$c)]|length==1' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "the capiss-only non-M5 mint is NOT surfaced (anchor rule)" \
    "jq -e --arg c '$fakecid' '[.[]|select(.correlation_id==\$c)]|length==0' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "mint leg presents the same capiss fields (full token id and grant) as the audit record" \
    "tid=\"\$(jq -r 'select(.result==\"allow\") | .token_id' \"$session_dir/capiss_audit.jsonl\" | head -n1)\"; test -n \"\$tid\" && grep -Fq \"\$tid\" \"$EVDIR/trace.txt\" && grep -Fq 'MINT' \"$EVDIR/trace.txt\" && grep -Fq 'create_story' \"$EVDIR/trace.txt\""
  outcome_guard "json legs carry utc, local time, and sequence per leg" \
    "jq -e 'first(.[]) | all(.legs[] | select(.present); has(\"timestamp_utc\") and has(\"timestamp_local\") and has(\"sequence\"))' \"$EVDIR/trace.json\" >/dev/null"
  return 0
}

M5_T59_test() {
  begin_test_evidence "M5-T59" "trace_gateway_allow_upstream_deny"
  echo "EVIDENCE_DIR=$EVDIR"
  sess_rel="e2e-M5-T59"
  session_dir="/repo/artifacts/varambu-demo/$sess_rel"
  cid="cccccccc-cccc-4ccc-8ccc-cccccccccccc"
  premise_guard "session with a gateway-allow / upstream-deny fixture prepared" \
    "rm -rf \"$session_dir\" && mkdir -p \"$session_dir/codex-home/sessions/2026/06/19\" && ln -sfn \"$session_dir\" /repo/artifacts/varambu-demo/current && jq -cn --arg c \"$cid\" '{event_type:\"capiss_mint_decision\",result:\"allow\",reason_code:\"ok\",subject_spiffe_id:\"spiffe://varambu.org/codex-jira-mcp-adapter\",act:\"create_story\",res:\"jira-mcp:/project:IAM\",aud:\"jira-mcp-gateway\",token_id:\"tok-1\",root_token_id:\"root-1\",timestamp_utc:\"2026-06-19T10:00:02Z\",correlation_id:\$c}' >\"$session_dir/capiss_audit.jsonl\" && jq -cn --arg c \"$cid\" '{event_type:\"jiramcp_gateway_decision\",decision:\"deny\",reason_code:\"upstream_error\",correlation_id:\$c,act:\"create_story\",res:\"jira-mcp:/project:IAM\",token_id:\"tok-1\",root_token_id:\"root-1\",budget_remaining:19,upstream_called:true,upstream_operation:\"story_create\",upstream_status:401,upstream_error_detail:\"Unauthorized — the Jira credential was rejected\",timestamp:\"2026-06-19T10:00:03Z\"}' >\"$session_dir/gateway_audit.jsonl\" && { jq -cn --arg c \"$cid\" '{event_type:\"adapter_request\",correlation_id:\$c,tool_name:\"create_story\",res:\"jira-mcp:/project:IAM\",project_key:\"IAM\",timestamp:\"2026-06-19T10:00:01Z\"}'; jq -cn --arg c \"$cid\" '{event_type:\"adapter_decision\",correlation_id:\$c,ok:false,reason:\"upstream_error\",timestamp:\"2026-06-19T10:00:04Z\"}'; } >\"$session_dir/adapter_audit.jsonl\""
  exercise_guard "render trace json and human in live mode" \
    "python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode live --json >\"$EVDIR/trace.json\" 2>\"$EVDIR/trace.err\"; python3 /repo/scripts/varambu_audit.py trace --session \"$session_dir\" --tz UTC --mode live >\"$EVDIR/trace.txt\" 2>>\"$EVDIR/trace.err\""
  outcome_guard "gateway enforcement leg is ALLOW (the gateway did not deny)" \
    "jq -e --arg c \"$cid\" '.[] | select(.correlation_id==\$c) | .legs[] | select(.leg==\"gateway\") | .present==true and .fields.leg_status==\"allow\"' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "upstream leg carries the denial (401 fail), distinct from the gateway" \
    "jq -e --arg c \"$cid\" '.[] | select(.correlation_id==\$c) | .legs[] | select(.leg==\"upstream\") | .present==true and .fields.leg_status==\"fail\" and .fields.upstream_status==401' \"$EVDIR/trace.json\" >/dev/null"
  outcome_guard "human view separates gateway ALLOW from upstream 401 FAIL" \
    "grep -Eq 'GATEWAY .* ALLOW' \"$EVDIR/trace.txt\" && grep -Eq 'UPSTREAM .* 401 FAIL' \"$EVDIR/trace.txt\""
  outcome_guard "upstream leg is gateway-attested (no fabricated independent voice)" \
    "grep -Fq 'gateway-attested, live' \"$EVDIR/trace.txt\""
  outcome_guard "human view relays the gateway-attested Jira error detail verbatim (no constructed interpretation)" \
    "tr '\n' ' ' < \"$EVDIR/trace.txt\" | tr -s ' ' | grep -Fq 'Unauthorized — the Jira credential was rejected' && ! grep -Fq 'Action' \"$EVDIR/trace.txt\" && jq -e --arg c \"$cid\" '.[] | select(.correlation_id==\$c) | .legs[] | select(.leg==\"upstream\") | .fields.upstream_error_detail==\"Unauthorized — the Jira credential was rejected\"' \"$EVDIR/trace.json\" >/dev/null"
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

print_section "Milestone 4 — offline delegation and governance truth"
if [ "$RUN_M4" -eq 1 ]; then
  TEST_PREFIX="M4"
  run_test "T1" "root mint includes chain metadata" M4_T1_test
  run_test "T2" "search writes discovery registry entries" M4_T2_test
  run_test "T3" "resource mint requires registry proof" M4_T3_test
  run_test "T4" "resource mint after discovery allows read-file" M4_T4_test
  run_test "T5" "budget is enforced per root token" M4_T5_test
  run_test "T6" "tampered token is denied" M4_T6_test
  run_test "T7" "depth limit is enforced on repeated delegation" M4_T7_test
  run_test "T8" "new-resource mint rate is enforced at capiss" M4_T8_test
  run_test "T9" "allow flow emits correlatable audit events" M4_T9_test
  run_test "T10" "deny flow emits correlatable mint audit event" M4_T10_test
  run_test "T11" "amplified delegated mint is denied" M4_T11_test
  run_test "T12" "wildcard delegated resource is denied" M4_T12_test
  run_test "T13" "budget and registry TTLs are bounded by root expiry" M4_T13_test
  run_test "T14" "protected request does not require capiss hot path" M4_T14_test
fi

print_section "Milestone 4a — Jira project access with broad upstream credential"
if [ "$RUN_M4A" -eq 1 ]; then
  TEST_PREFIX="M4a"
  run_test "T1" "mock upstream can read IAM and NAS projects" M4A_T1_test
  run_test "T2" "agent-a can mint IAM Jira token and read IAM-1" M4A_T2_test
  run_test "T3" "non-allowed NAS project mint is denied" M4A_T3_test
  run_test "T4" "IAM token cannot read NAS-1 before upstream use" M4A_T4_test
  run_test "T5" "rogue cannot mint IAM Jira token" M4A_T5_test
  run_test "T6" "rogue cannot replay stolen Jira token" M4A_T6_test
  run_test "T7" "Jira read consumes shared root budget" M4A_T7_test
  run_test "T8" "Jira budget exhaustion denies eleventh read" M4A_T8_test
  run_test "T9" "upstream project mismatch is denied" M4A_T9_test
  run_test "T10" "Jira audit trace reconstructs mint and use" M4A_T10_test
fi

print_section "Milestone 4b — Jira project-scoped description write"
if [ "$RUN_M4B" -eq 1 ]; then
  TEST_PREFIX="M4b"
  run_test "T1" "write token updates IAM description and reads marker" M4B_T1_test
  run_test "T2" "read token cannot update Jira description" M4B_T2_test
  run_test "T3" "non-allowed NAS write mint is denied" M4B_T3_test
  run_test "T4" "IAM write token cannot update NAS before upstream use" M4B_T4_test
  run_test "T5" "description writes reject malformed or overbroad bodies" M4B_T5_test
  run_test "T6" "Jira write audit trace reconstructs mint and use" M4B_T6_test
fi

print_section "Milestone 5 — Codex Jira MCP Slice 1"
if [ "$RUN_M5" -eq 1 ]; then
  TEST_PREFIX="M5"
  run_test "T1" "MCP launcher starts adapter session" M5_T1_test
  run_test "T2" "MCP tool surface is exactly Slice 1" M5_T2_test
  run_test "T3" "IAM project summary succeeds" M5_T3_test
  run_test "T4" "Summary response contains only allowed fields" M5_T4_test
  run_test "T5" "Summary response is bounded" M5_T5_test
  run_test "T6" "NAS project summary denies at capiss" M5_T6_test
  run_test "T7" "IAM story creation succeeds" M5_T7_test
  run_test "T8" "IAM story creation accepts criteria" M5_T8_test
  run_test "T9" "IAM story creation accepts valid epic" M5_T9_test
  run_test "T10" "Invalid same-project epic denies" M5_T10_test
  run_test "T11" "NAS project story creation denies at capiss" M5_T11_test
  run_test "T12" "IAM token with NAS payload denies" M5_T12_test
  run_test "T13" "IAM token with NAS epic denies" M5_T13_test
  run_test "T14" "Arbitrary create fields are rejected" M5_T14_test
  run_test "T15" "Plain text only and raw ADF rejected" M5_T15_test
  run_test "T16" "Adapter forwards NAS to capiss" M5_T16_test
  run_test "T17" "Unsupported action cannot be minted" M5_T17_test
  run_test "T18" "Old Jira tool authority is separate" M5_T18_test
  run_test "T19" "M5 does not disturb existing jira-tool path" M5_T19_test
  run_test "T20" "Endpoint-bound action is enforced" M5_T20_test
  run_test "T21" "Audience mismatch denies" M5_T21_test
  run_test "T22" "Stolen token subject mismatch denies" M5_T22_test
  run_test "T23" "Invalid token denies" M5_T23_test
  run_test "T24" "Direct app bypass is unavailable" M5_T24_test
  run_test "T25" "Only gateway calls mock upstream" M5_T25_test
  run_test "T26" "MCP responses contain no capiss tokens" M5_T26_test
  run_test "T27" "Adapter logs contain no bearer tokens" M5_T27_test
  run_test "T28" "Adapter environment has no Jira API key" M5_T28_test
  run_test "T30" "Client auth headers are stripped upstream" M5_T30_test
  run_test "T31" "Summary participates in budget governance" M5_T31_test
  run_test "T32" "Create consumes budget before upstream" M5_T32_test
  run_test "T33" "Budget exhaustion denies create" M5_T33_test
  run_test "T34" "Pre-validation denials do not consume budget" M5_T34_test
  run_test "T35" "Upstream create failure is not refunded" M5_T35_test
  run_test "T36" "Read audit events correlate" M5_T36_test
  run_test "T37" "Create audit events correlate" M5_T37_test
  run_test "T38" "Deny paths produce final decision evidence" M5_T38_test
  run_test "T39" "Local errors avoid upstream existence leak" M5_T39_test
  run_test "T40" "Mock upstream breadth precondition" M5_T40_test
  run_test "T41" "Protected path narrows broad mock" M5_T41_test
  run_test "T42" "Varambu capiss audit files" M5_T42_test
  run_test "T43" "Varambu audit active append without post-processing" M5_T43_test
  run_test "T44" "Varambu audit current session history and file access" M5_T44_test
  run_test "T45" "Varambu audit secret exclusion in persisted evidence" M5_T45_test
  run_test "T46" "Varambu audit stale tailer warning and strict failure" M5_T46_test
  run_test "T47" "Varambu audit local and UTC timing semantics" M5_T47_test
  run_test "T48" "Varambu audit uniform capiss enrichment" M5_T48_test
  run_test "T49" "Varambu trace full chain allowed" M5_T49_test
  run_test "T50" "Varambu trace denied mint partial chain" M5_T50_test
  run_test "T51" "Varambu trace intent pending then converges" M5_T51_test
  run_test "T52" "Varambu trace multi tool-call attribution" M5_T52_test
  run_test "T53" "Varambu trace secret hygiene and bounds" M5_T53_test
  run_test "T54" "Varambu trace agent tamper detection" M5_T54_test
  run_test "T55" "Varambu trace honest live upstream leg" M5_T55_test
  run_test "T56" "Varambu trace CLI surface and audit non-regression" M5_T56_test
  run_test "T57" "Varambu trace canonical ordering and join integrity" M5_T57_test
  run_test "T58" "Varambu trace anchor rule mint reuse and timestamps" M5_T58_test
  run_test "T59" "Varambu trace separates gateway allow from upstream deny" M5_T59_test
fi

printf '\nTotal: %d  Passed: %d  Failed: %d\n' "$TOTAL" "$PASSED" "$FAILED"
if [ -s "$WARNINGS_FILE" ]; then
  printf 'Warnings: %d\n' "$WARNING_TOTAL"
  printf '\nWarnings summary:\n'
  sed 's/\t/ | /' "$WARNINGS_FILE"
fi
if [ "$PROFILE_ENABLED" = "1" ] && [ -s "$PROFILE_FILE" ]; then
  printf '\nSlowest guard steps (top 25):\n'
  awk -F '\t' 'NR>1 {printf "%8d ms | %-7s | %-10s | %s\n", $1, $2, $3, $6}' "$PROFILE_FILE" \
    | sort -nr | head -n 25 | tee "$PROFILE_SUMMARY_FILE"
  printf '\nTiming artifacts:\n  %s\n  %s\n' "$PROFILE_FILE" "$PROFILE_SUMMARY_FILE"
fi
if [ "$FAILED" -ne 0 ]; then
  exit 1
fi
