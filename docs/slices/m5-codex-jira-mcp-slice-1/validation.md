# M5 Codex Jira MCP Slice 1 Validation

Date: 2026-05-16

## Deterministic Validation

- `python3 -m py_compile services/jira-mcp-gateway/server.py services/jira-mcp-mock/server.py services/codex-jira-mcp-adapter/server.py`: passed.
- `sh -n scripts/rogue_node_tests.sh scripts/codex_jira_mcp.sh services/codex-jira-mcp-adapter/entrypoint.sh services/jira-mcp-envoy/entrypoint.sh spire/token-init/init.sh`: passed.
- `docker compose -f compose/spiffe.compose.yml config`: passed.
- `pytest tests/unit/capiss/test_jira_mcp_mint.py tests/unit/jiramcp -q`: passed.
- `make unit-guard-check`: passed, 224 tests.
- `make unit-trust`: passed, total line coverage 85.06%.
- `make qa-trace`: passed.
- `make qa-quality`: passed.
- `docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build -e TEST_MILESTONES=m5 rogue-tests`: passed, 40/40.
- `docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests`: passed, 102/102.
- `make qa-evidence`: passed, validated 102/102 with 2 accepted alternate isolation warnings.

## Accepted Warnings

- `M3.S2-T3`: accepted alternate isolation mode, DNS resolution timeout while reaching OPA from edge.
- `M3.S2-T5`: accepted alternate isolation mode, DNS resolution timeout while reaching capability-issuer from edge.

## Live Validation

- Optional live Jira smoke was not run in this turn.
- Live mode remains explicit opt-in and is not required for deterministic M5 closure.
