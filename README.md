# agentic-iam-spiffe

Learning project:
Agentic IAM using SPIFFE / SPIRE

Goals:
- Understand workload identity (SPIFFE IDs)
- mTLS without OAuth tokens
- Compare against OAuth + mTLS + PoP lab

## SPIRE (Milestone 1)

Start SPIRE + tool-b:
```bash
docker compose -f compose/spiffe.compose.yml up -d spire-server spire-token-init spire-agent tool-b
```

Check logs for successful startup:
```bash
docker compose -f compose/spiffe.compose.yml logs -f spire-server spire-token-init spire-agent
```
You should see the server listening on its API port, the token init container generating a join token (only when missing) and ensuring a node entry, and the agent connecting to `spire-server:8081` without fatal errors.

## Milestone 1.5: Rogue node checks

Run the rogue node checks:
```bash
docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
```
Expected behavior: all five checks print PASS and the `rogue-tests` container exits 0.

## Milestone 2: Workload identities (mTLS)

Start SPIRE + tool-b + agent-a:
```bash
docker compose -f compose/spiffe.compose.yml up -d spire-server spire-token-init spire-agent tool-b agent-a
```

What to look for in logs:
- `tool-b` prints its SPIFFE ID and only accepts `spiffe://example.org/agent-a`
- `agent-a` prints its SPIFFE ID and verifies `spiffe://example.org/tool-b`
- `rogue` should fail (no Workload API socket mount)

## Milestone 2 security tests (unified suite)

Run the full security test suite (includes Milestone 1 + Milestone 2 checks):
```bash
docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
```
Expected behavior: each test prints an ID, name, and a green PASS; the runner prints totals and exits 0 if all checks pass.
