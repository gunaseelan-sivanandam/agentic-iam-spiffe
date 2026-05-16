#!/bin/sh
set -eu

SPIRE_BIN="/opt/spire/bin/spire-server"
SOCKET="/run/spire/server/data/private/api.sock"
TOKEN_FILE="/run/spire/shared/join_token"
NODE_SPIFFE_ID="spiffe://example.org/agent/spire-agent"
TOOL_B_SPIFFE_ID="spiffe://example.org/tool-b"
TOOL_B_ENVOY_SPIFFE_ID="spiffe://example.org/tool-b-envoy"
CAPISS_ENVOY_SPIFFE_ID="spiffe://example.org/capability-issuer-envoy"
CAPISS_NO_OPA_ENVOY_SPIFFE_ID="spiffe://example.org/capability-issuer-no-opa-envoy"
JIRA_TOOL_SPIFFE_ID="spiffe://example.org/jira-tool"
JIRA_TOOL_ENVOY_SPIFFE_ID="spiffe://example.org/jira-tool-envoy"
CODEX_JIRA_MCP_ADAPTER_SPIFFE_ID="spiffe://example.org/codex-jira-mcp-adapter"
JIRA_MCP_GATEWAY_SPIFFE_ID="spiffe://example.org/jira-mcp-gateway"
JIRA_MCP_ENVOY_SPIFFE_ID="spiffe://example.org/jira-mcp-envoy"
AGENT_A_SPIFFE_ID="spiffe://example.org/agent-a"
ROGUE_SPIFFE_ID="spiffe://example.org/rogue"

while [ ! -S "$SOCKET" ]; do
  sleep 0.5
done

if [ ! -s "$TOKEN_FILE" ]; then
  umask 077
  TOKEN="$($SPIRE_BIN token generate -spiffeID "$NODE_SPIFFE_ID" -socketPath "$SOCKET" -output json | sed -n 's/.*"value":"\([^"]*\)".*/\1/p')"
  printf "%s" "$TOKEN" > "$TOKEN_FILE"
else
  TOKEN="$(cat "$TOKEN_FILE")"
fi

if [ -z "$TOKEN" ]; then
  echo "join token is empty" >&2
  exit 1
fi

ENTRY_JSON="$($SPIRE_BIN entry show -spiffeID "$NODE_SPIFFE_ID" -socketPath "$SOCKET" -output json)"
if echo "$ENTRY_JSON" | grep -q '"entries":\[\]'; then
  $SPIRE_BIN entry create -node -spiffeID "$NODE_SPIFFE_ID" -selector "join_token:${TOKEN}" -socketPath "$SOCKET"
fi

wait_for_node_entry() {
  i=0
  while [ $i -lt 30 ]; do
    entry_json="$($SPIRE_BIN entry show -spiffeID "$NODE_SPIFFE_ID" -socketPath "$SOCKET" -output json)"
    if echo "$entry_json" | grep -Fq '"entries":[{'; then
      return 0
    fi
    i=$((i + 1))
    sleep 1
  done
  return 1
}

create_workload_entry() {
  spiffe_id="$1"
  selector="$2"
  entry_json="$($SPIRE_BIN entry show -spiffeID "$spiffe_id" -socketPath "$SOCKET" -output json)"
  if echo "$entry_json" | grep -q '"entries":\[\]'; then
    $SPIRE_BIN entry create -parentID "$NODE_SPIFFE_ID" -spiffeID "$spiffe_id" -selector "$selector" -socketPath "$SOCKET"
  fi
}

if ! wait_for_node_entry; then
  echo "node entry not available for ${NODE_SPIFFE_ID}" >&2
  exit 1
fi

create_workload_entry "$TOOL_B_SPIFFE_ID" "docker:label:com.docker.compose.service:tool-b"
create_workload_entry "$TOOL_B_ENVOY_SPIFFE_ID" "docker:label:com.docker.compose.service:tool-b-envoy"
create_workload_entry "$CAPISS_ENVOY_SPIFFE_ID" "docker:label:com.docker.compose.service:capability-issuer-envoy"
create_workload_entry "$CAPISS_NO_OPA_ENVOY_SPIFFE_ID" "docker:label:com.docker.compose.service:capability-issuer-no-opa-envoy"
create_workload_entry "$JIRA_TOOL_SPIFFE_ID" "docker:label:com.docker.compose.service:jira-tool"
create_workload_entry "$JIRA_TOOL_ENVOY_SPIFFE_ID" "docker:label:com.docker.compose.service:jira-tool-envoy"
create_workload_entry "$CODEX_JIRA_MCP_ADAPTER_SPIFFE_ID" "docker:label:com.docker.compose.service:codex-jira-mcp-adapter"
create_workload_entry "$JIRA_MCP_GATEWAY_SPIFFE_ID" "docker:label:com.docker.compose.service:jira-mcp-gateway"
create_workload_entry "$JIRA_MCP_ENVOY_SPIFFE_ID" "docker:label:com.docker.compose.service:jira-mcp-envoy"
create_workload_entry "$AGENT_A_SPIFFE_ID" "docker:label:com.docker.compose.service:agent-a"
create_workload_entry "$ROGUE_SPIFFE_ID" "docker:label:com.docker.compose.service:rogue"
