#!/bin/sh
set -eu

ROGUE_CONFIG="/run/spire/rogue/agent.conf"
ROGUE_DIR="/run/spire/rogue"
REAL_TOKEN_FILE="/run/spire/shared/join_token"
MISSING_TOKEN_FILE="/run/spire/rogue/missing_token"
FAKE_TOKEN_FILE="/run/spire/rogue/fake_token"

PASS_COUNT=0
FAIL_COUNT=0

TIMEOUT_BIN="timeout"
if ! command -v timeout >/dev/null 2>&1; then
  if command -v busybox >/dev/null 2>&1; then
    TIMEOUT_BIN="busybox timeout"
  else
    echo "FAIL precondition: timeout not available"
    exit 1
  fi
fi

pass() {
  echo "PASS $1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
  echo "FAIL $1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

require() {
  if ! "$@"; then
    return 1
  fi
}

wait_for_legit_attestation() {
  i=0
  while [ $i -lt 30 ]; do
    if docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock -output json 2>/dev/null | grep -Fq '"agents":[{' ; then
      return 0
    fi
    i=$((i + 1))
    sleep 1
  done
  return 1
}

run_rogue_attempt() {
  label="$1"
  token="$2"
  log_file="/tmp/rogue_${label}.log"
  temp_dir="/tmp/rogue_${label}"
  temp_config="/tmp/rogue_${label}.conf"

  rm -f "$log_file"
  mkdir -p "$temp_dir"
  sed "s#/run/spire/rogue#${temp_dir}#g" "$ROGUE_CONFIG" > "$temp_config"
  set +e
  $TIMEOUT_BIN 6s /opt/spire/bin/spire-agent run -config "$temp_config" -joinToken "$token" >"$log_file" 2>&1
  rc=$?
  set -e

  if grep -q "Node attestation was successful" "$log_file"; then
    fail "$label"
    return 0
  fi

  if [ $rc -eq 0 ]; then
    fail "$label"
    return 0
  fi

  pass "$label"
}

# Preconditions
mkdir -p "$ROGUE_DIR"
rm -f "$MISSING_TOKEN_FILE" "$FAKE_TOKEN_FILE"

if ! wait_for_legit_attestation; then
  echo "FAIL precondition: legitimate agent did not attest"
  exit 1
fi

if [ ! -s "$REAL_TOKEN_FILE" ]; then
  echo "FAIL precondition: real join token missing"
  exit 1
fi

# C1: Rogue without join token file must not attest
MISSING_TOKEN="$(cat "$MISSING_TOKEN_FILE" 2>/dev/null || true)"
run_rogue_attempt "C1" "$MISSING_TOKEN"

# C2: Rogue with forged token must not attest
echo "not-a-real-token" > "$FAKE_TOKEN_FILE"
run_rogue_attempt "C2" "$(cat "$FAKE_TOKEN_FILE")"

# C3: Rogue reusing real token after legit agent attested must not attest
REAL_TOKEN="$(cat "$REAL_TOKEN_FILE")"
run_rogue_attempt "C3" "$REAL_TOKEN"

# C4: Rogue agent must not read the real join token (no shared mount)
mounts="$(docker inspect -f '{{range .Mounts}}{{.Destination}} {{end}}' spiffe-spire-rogue-agent 2>/dev/null || true)"
if echo "$mounts" | grep -q "/run/spire/shared"; then
  echo "FAIL C4 (unexpected shared mount)"
  FAIL_COUNT=$((FAIL_COUNT + 1))
else
  set +e
  cat_output=$(docker exec spiffe-spire-rogue-agent cat /run/spire/shared/join_token 2>&1)
  cat_rc=$?
  set -e
  if [ $cat_rc -eq 0 ]; then
    echo "FAIL C4 (unexpected access): $cat_output"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    pass "C4"
  fi
fi

# C5: Only intended nodes are registered (compare labeled containers to server agents)
expected_nodes=$(docker ps -q --filter "label=spiffe.node=true" | wc -l | tr -d ' ')
agents_json=$(docker exec spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock -output json 2>/dev/null)
actual_nodes=$(echo "$agents_json" | grep -o '"id"' | wc -l | tr -d ' ')
if [ "$actual_nodes" -eq "$expected_nodes" ]; then
  pass "C5"
else
  echo "FAIL C5 (expected ${expected_nodes}, got ${actual_nodes})"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

if [ $FAIL_COUNT -ne 0 ]; then
  echo "FAILED: ${FAIL_COUNT} checks failed"
  exit 1
fi

echo "OK: ${PASS_COUNT} checks passed"
