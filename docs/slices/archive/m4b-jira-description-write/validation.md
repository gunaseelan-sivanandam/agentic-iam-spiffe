# Validation

## Required Checks
- `pytest tests/unit/capiss/test_canonicalize_resource.py tests/unit/capiss/test_jira_mint.py tests/unit/jiratool/test_authorization.py`
- `sh -n scripts/rogue_node_tests.sh`
- `sh -n agents/agent-a/jira_demo.sh`
- `sh -n scripts/jira_live_smoke.sh`
- `TEST_MILESTONES=m4b docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests`
- `make qa-trace`
- `make qa-evidence` after an E2E run

## Live Smoke Guard
- `make jira-live-smoke` requires live Jira inputs in `.env`.
- The running `spiffe-jira-tool` container must have `JIRA_UPSTREAM_MODE=live`; the smoke fails before the protected demo if the container is still in mock mode.
- The smoke records direct Jira credential breadth first, then runs the protected M4b write/readback path and leaves the allowed Jira issue description changed.

## Evidence
- `M4b-T1` allowed write mint, update, and readback.
- `M4b-T2` read token write denial.
- `M4b-T3` NAS write mint denial.
- `M4b-T4` NAS write use denial before upstream.
- `M4b-T5` malformed and overbroad body denial before upstream.
- `M4b-T6` capiss and jira-tool audit reconstruction.
