# M5 Codex Jira MCP Slice 1 Implementation Review

Date: 2026-05-16

## Scope Reviewed

- Authored requirements, architecture, architecture diagram source, slice plan, slice test plan, and trace mappings.
- M5 capiss authority, OPA policy, SPIRE entries, Envoy boundaries, adapter, gateway, mock upstream, launcher, unit tests, and E2E harness.
- Regression surface for existing M4a/M4b Jira paths.

## Findings and Fixes

1. High: `codex-jira-mcp-adapter` could remain running without usable SPIFFE SVID files.
   - Evidence: M5-T3 initially failed when the adapter crashed while loading `/run/spire/svid/bundle.pem`.
   - Fix: adapter and `jira-mcp-envoy` entrypoints now require `svid.0.pem`, `svid.0.key`, and `bundle.0.pem` before declaring readiness or starting the long-running process.
   - Verification: full M5 suite passed after clean stack rebuild.

2. High: `jira-mcp-gateway` was reachable from the test/upstream inspection network.
   - Evidence: M5-T24 failed because `curl http://jira-mcp-gateway:8080/health` returned `{"status":"ok"}` from the test harness.
   - Fix: moved direct mock inspection to the mock service only. `jira-mcp-gateway` is attached to the private Jira MCP app network, while `jira-mcp-mock` is also attached to the test-only upstream inspection network.
   - Verification: targeted `TEST_ONLY=M5-T24` passed, then full M5 suite passed.

3. Medium: new M5 services lowered default unit coverage below `make unit-trust` gate.
   - Evidence: first `make unit-trust` run failed at total line coverage 69.49%.
   - Fix: added focused unit coverage for adapter protocol/transport paths, gateway handler/transport/budget branches, and mock GET/POST routes.
   - Verification: `make unit-trust` passed with total line coverage 85.06%.

## Final Verification

- `make unit-guard-check`: passed, 224 tests.
- `make unit-trust`: passed.
- `make qa-trace`: passed.
- `make qa-quality`: passed.
- `docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build -e TEST_MILESTONES=m5 rogue-tests`: passed, 40/40.
- `docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests`: passed, 102/102.
- `make qa-evidence`: passed, 102/102 validated, 2 accepted alternate isolation warnings.

## Residual Notes

- Optional live Jira smoke was not run. The slice remains mock-by-default and live mode is explicit opt-in.
- Component and network diagrams were refreshed after live M5 validation: `docs/only_arch.svg`, `docs/only_arch.puml`, `docs/architecture_diagram.svg`, `docs/architecture_diagram.png`, and `docs/architecture_diagram.puml`.
