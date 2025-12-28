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

container_running() {
  container_name="$1"
  docker ps --format '{{.Names}}' | grep -Fxq "$container_name"
}

wait_for_legit_attestation() {
  i=0
  while [ $i -lt 30 ]; do
    if docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list \
      -socketPath /run/spire/server/data/private/api.sock -output json 2>/dev/null | \
      grep -Fq '"agents":[{' ; then
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

  if grep -q "Node attestation was successful" "$log_file"; then
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
  while [ $i -lt 30 ]; do
    if docker exec spiffe-tool-b test -s /run/spire/svid/svid.pem 2>/dev/null; then
      break
    fi
    i=$((i + 1))
    sleep 1
  done

  if ! docker exec spiffe-tool-b test -s /run/spire/svid/svid.pem 2>/dev/null; then
    set_reason "tool-b SVID not available"
    return 1
  fi

  docker exec spiffe-tool-b cat /run/spire/svid/svid.pem >"$cert"
  docker exec spiffe-tool-b cat /run/spire/svid/svid.key >"$key"
  docker exec spiffe-tool-b cat /run/spire/svid/bundle.pem >"$bundle"

  if [ ! -s "$cert" ] || [ ! -s "$key" ] || [ ! -s "$bundle" ]; then
    set_reason "failed to copy tool-b cert material"
    return 1
  fi

  TOOLB_CERT="$cert"
  TOOLB_KEY="$key"
  TOOLB_BUNDLE="$bundle"
  return 0
}

expect_tls_fail() {
  out_file="$1"
  rc="$2"

  if [ $rc -ne 0 ]; then
    return 0
  fi

  if grep -Eiq 'alert|handshake|certificate required|bad certificate|no peer certificate' "$out_file"; then
    return 0
  fi

  return 1
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
  if echo "$mounts" | grep -q "/run/spire/shared"; then
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
  out="/tmp/toolb_material/t1.out"
  set +e
  $TIMEOUT_BIN 6s openssl s_client -connect tool-b:8443 -CAfile "$TOOLB_BUNDLE" \
    -verify_return_error < /dev/null >"$out" 2>&1
  rc=$?
  set -e
  if expect_tls_fail "$out" "$rc"; then
    return 0
  fi
  set_reason "TLS succeeded without client cert"
  return 1
}

# M2-T2
T2_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  tmpdir="/tmp/toolb_material"
  openssl req -x509 -newkey rsa:2048 -nodes -keyout "$tmpdir/bad.key" \
    -out "$tmpdir/bad.pem" -days 1 -subj "/CN=rogue" >/dev/null 2>&1
  out="/tmp/toolb_material/t2.out"
  set +e
  $TIMEOUT_BIN 6s openssl s_client -connect tool-b:8443 -cert "$tmpdir/bad.pem" \
    -key "$tmpdir/bad.key" -CAfile "$TOOLB_BUNDLE" -verify_return_error \
    < /dev/null >"$out" 2>&1
  rc=$?
  set -e
  if expect_tls_fail "$out" "$rc"; then
    return 0
  fi
  set_reason "TLS succeeded with invalid client cert"
  return 1
}

# M2-T3
T3_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  tmpdir="/tmp/toolb_material"
  start=$(date -u -d "2 days ago" +%Y%m%d%H%M%SZ)
  end=$(date -u -d "1 day ago" +%Y%m%d%H%M%SZ)
  openssl req -newkey rsa:2048 -nodes -keyout "$tmpdir/exp.key" \
    -out "$tmpdir/exp.csr" -subj "/CN=rogue-expired" >/dev/null 2>&1
  openssl x509 -req -in "$tmpdir/exp.csr" -signkey "$tmpdir/exp.key" \
    -set_serial 01 -out "$tmpdir/exp.pem" -startdate "$start" -enddate "$end" \
    >/dev/null 2>&1
  out="/tmp/toolb_material/t3.out"
  set +e
  $TIMEOUT_BIN 6s openssl s_client -connect tool-b:8443 -cert "$tmpdir/exp.pem" \
    -key "$tmpdir/exp.key" -CAfile "$TOOLB_BUNDLE" -verify_return_error \
    < /dev/null >"$out" 2>&1
  rc=$?
  set -e
  if expect_tls_fail "$out" "$rc"; then
    return 0
  fi
  set_reason "TLS succeeded with expired client cert"
  return 1
}

# M2-T4
T4_test() {
  if ! ensure_toolb_material; then
    return 1
  fi
  out="/tmp/toolb_material/t4.out"
  printf "GET /secret HTTP/1.1\r\nHost: tool-b\r\nConnection: close\r\n\r\n" | \
    $TIMEOUT_BIN 6s openssl s_client -connect tool-b:8443 -cert "$TOOLB_CERT" \
      -key "$TOOLB_KEY" -CAfile "$TOOLB_BUNDLE" -verify_return_error \
      -showcerts -ign_eof >"$out" 2>&1 || true
  if ! grep -q "Verify return code: 0 (ok)" "$out"; then
    set_reason "server verification did not succeed"
    return 1
  fi
  status=$(tr -d '\r' <"$out" | grep -m1 '^HTTP/' | awk '{print $2}')
  if [ "$status" != "403" ]; then
    set_reason "expected HTTP 403, got ${status:-none}"
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
  if echo "$mounts" | grep -q "/run/spire/svid"; then
    set_reason "workload SVID mount present"
    return 1
  fi
  if echo "$mounts" | grep -q "/run/spire/agent/data"; then
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

printf '\nTotal: %d  Passed: %d  Failed: %d\n' "$TOTAL" "$PASSED" "$FAILED"
if [ "$FAILED" -ne 0 ]; then
  exit 1
fi
