#!/bin/sh
set -eu

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

required=""
for name in JIRA_BASE_URL JIRA_EMAIL JIRA_API_TOKEN JIRA_ALLOWED_ISSUE JIRA_NON_ALLOWED_ISSUE; do
  eval "value=\${$name:-}"
  if [ -z "$value" ]; then
    required="$required $name"
  fi
done

if [ -n "$required" ]; then
  echo "missing required live Jira environment:$required" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required for live smoke evidence extraction" >&2
  exit 2
fi

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
evidence_root="${JIRA_LIVE_EVIDENCE_DIR:-artifacts/jira-live-smoke}"
evidence_dir="${evidence_root}/${stamp}"
mkdir -p "$evidence_dir"

direct_read() {
  issue="$1"
  label="$2"
  raw="/tmp/jira_live_${label}_$$.json"
  status_file="${evidence_dir}/${label}_status.txt"
  project_file="${evidence_dir}/${label}_project.txt"
  status="$(curl -sS \
    -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
    -H "Accept: application/json" \
    -o "$raw" \
    -w '%{http_code}' \
    "${JIRA_BASE_URL%/}/rest/api/3/issue/${issue}")"
  printf '%s\n' "$status" >"$status_file"
  if [ "$status" = "200" ]; then
    jq -r '.fields.project.key // ""' "$raw" >"$project_file"
  else
    : >"$project_file"
  fi
  rm -f "$raw"
}

direct_read "$JIRA_ALLOWED_ISSUE" "direct_allowed"
direct_read "$JIRA_NON_ALLOWED_ISSUE" "direct_non_allowed"

allowed_status="$(cat "$evidence_dir/direct_allowed_status.txt")"
non_allowed_status="$(cat "$evidence_dir/direct_non_allowed_status.txt")"
if [ "$allowed_status" != "200" ] || [ "$non_allowed_status" != "200" ]; then
  echo "direct live Jira precondition failed; evidence: $evidence_dir" >&2
  exit 1
fi

allowed_project="$(cat "$evidence_dir/direct_allowed_project.txt")"
non_allowed_project="$(cat "$evidence_dir/direct_non_allowed_project.txt")"

if docker ps --format '{{.Names}}' | grep -Fxq spiffe-jira-tool; then
  jira_tool_mode="$(
    docker inspect spiffe-jira-tool --format '{{range .Config.Env}}{{println .}}{{end}}' \
      | sed -n 's/^JIRA_UPSTREAM_MODE=//p' \
      | tail -n 1
  )"
  if [ "$jira_tool_mode" != "live" ]; then
    echo "protected live smoke requires spiffe-jira-tool to run with JIRA_UPSTREAM_MODE=live; current=${jira_tool_mode:-unset}; evidence: $evidence_dir" >&2
    exit 1
  fi
else
  echo "protected live smoke requires a running spiffe-jira-tool container in live mode; evidence: $evidence_dir" >&2
  exit 1
fi

if docker ps --format '{{.Names}}' | grep -Fxq spiffe-agent-a; then
  docker exec \
    -e "JIRA_ALLOWED_ISSUE=${JIRA_ALLOWED_ISSUE}" \
    -e "JIRA_NON_ALLOWED_ISSUE=${JIRA_NON_ALLOWED_ISSUE}" \
    -e "JIRA_ALLOWED_PROJECT=${allowed_project}" \
    -e "JIRA_NON_ALLOWED_PROJECT=${non_allowed_project}" \
    spiffe-agent-a /app/jira_demo.sh >"${evidence_dir}/protected_demo_output.txt" 2>"${evidence_dir}/protected_demo_error.txt"
else
  docker compose --env-file .env --profile clients -f compose/spiffe.compose.yml run --rm --no-deps \
    -e "JIRA_ALLOWED_ISSUE=${JIRA_ALLOWED_ISSUE}" \
    -e "JIRA_NON_ALLOWED_ISSUE=${JIRA_NON_ALLOWED_ISSUE}" \
    -e "JIRA_ALLOWED_PROJECT=${allowed_project}" \
    -e "JIRA_NON_ALLOWED_PROJECT=${non_allowed_project}" \
    agent-a /app/jira_demo.sh >"${evidence_dir}/protected_demo_output.txt" 2>"${evidence_dir}/protected_demo_error.txt"
fi

if grep -Eq '(JIRA_API_TOKEN|Basic [A-Za-z0-9+/=]+|Bearer [A-Za-z0-9._~+/-]+)' "${evidence_dir}/protected_demo_output.txt" "${evidence_dir}/protected_demo_error.txt"; then
  echo "protected demo output included credential-like material; evidence: $evidence_dir" >&2
  exit 1
fi

if ! grep -Eq "^jira mint project=${allowed_project} act=read status=200 " "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Eq "^jira mint project=${allowed_project} act=write status=200 " "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira read issue=${JIRA_ALLOWED_ISSUE} status=200 project=${allowed_project}" "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira write issue=${JIRA_ALLOWED_ISSUE} act=read-token status=403 reason=insufficient_authority" "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira write issue=${JIRA_ALLOWED_ISSUE} act=write status=204 project=${allowed_project}" "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira readback issue=${JIRA_ALLOWED_ISSUE} status=200 marker=matched" "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira mint project=${non_allowed_project} act=read status=403 reason=policy" "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira mint project=${non_allowed_project} act=write status=403 reason=policy" "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira read issue=${JIRA_NON_ALLOWED_ISSUE} status=403 reason=project_mismatch" "${evidence_dir}/protected_demo_output.txt" \
  || ! grep -Fxq "jira write issue=${JIRA_NON_ALLOWED_ISSUE} act=write status=403 reason=project_mismatch" "${evidence_dir}/protected_demo_output.txt"; then
  echo "protected demo authorization check failed; evidence: $evidence_dir" >&2
  exit 1
fi

printf 'evidence_dir=%s\n' "$evidence_dir"
printf 'direct_allowed_status=%s project=%s\n' "$allowed_status" "$allowed_project"
printf 'direct_non_allowed_status=%s project=%s\n' "$non_allowed_status" "$non_allowed_project"
