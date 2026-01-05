# agentic-iam-spiffe

Learning project:
Agentic IAM using SPIFFE / SPIRE

Goals:
- Understand workload identity (SPIFFE IDs)
- mTLS without OAuth tokens
- Compare against OAuth + mTLS + PoP lab

## Cleanup (stop all containers and reset data)

Stop all services and remove the join token + data dirs:
```bash
docker compose --profile tests --profile clients -f compose/spiffe.compose.yml down
sudo rm -rf spire/server/data spire/agent/data
rm -f spire/shared/join_token
```

Test report output location:
```text
test_report.log
```

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

Server logs only:
```bash
docker compose -f compose/spiffe.compose.yml logs -f spire-server
```

Node (agent) logs only:
```bash
docker compose -f compose/spiffe.compose.yml logs -f spire-agent
```

Check server entries and agents:
```bash
docker exec -it spiffe-spire-server /opt/spire/bin/spire-server entry show -socketPath /run/spire/server/data/private/api.sock
docker exec -it spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock
```

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

Check server entries and agents:
```bash
docker exec -it spiffe-spire-server /opt/spire/bin/spire-server entry show -socketPath /run/spire/server/data/private/api.sock
docker exec -it spiffe-spire-server /opt/spire/bin/spire-server agent list -socketPath /run/spire/server/data/private/api.sock
```

## Milestone 2 security tests (unified suite)

Run the full security test suite (includes Milestone 1 + Milestone 2 checks):
```bash
docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
```
Expected behavior: each test prints an ID, name, and a green PASS; the runner prints totals and exits 0 if all checks pass.

## Milestone 3: Envoy ingress (SPIFFE mTLS boundary)

Start SPIRE + tool-b + Envoy + clients:
```bash
docker compose --profile clients -f compose/spiffe.compose.yml up -d spire-server spire-token-init spire-agent tool-b tool-b-envoy agent-a rogue
```

What to look for:
- Envoy terminates SPIFFE mTLS and injects `x-spiffe-id`
- tool-b trusts `x-spiffe-id` only because it is isolated on `toolb_app_net`
- tool-b does not authenticate clients directly in this milestone

## Milestone 3 Step 1: Capability issuer (Envoy ingress)

Start SPIRE + tool-b + capability issuer + Envoy + clients:
```bash
docker compose --profile clients -f compose/spiffe.compose.yml up -d \
  spire-server spire-token-init spire-agent \
  tool-b tool-b-envoy \
  capability-issuer capability-issuer-envoy \
  agent-a rogue
```

What to look for:
- `agent-a` calls `POST /capabilities/mint` via `capability-issuer-envoy` and prints a JSON response
- `capability-issuer` rejects missing `x-spiffe-id` because it only trusts the header behind `capiss_app_net`

Policy boundary note:
OPA is deployed as a private, internal policy decision point with no externally
exposed ports. The capability issuer fails closed if OPA is unavailable. This setup
reflects common sidecar-style policy integration and is sufficient to demonstrate
the semantic separation of identity and authority.

## Milestone 3 Step 3: Biscuit minting

The capability issuer now mints real Biscuit tokens on allowed requests, with a
short, configurable TTL.
Tests now assert non-empty tokens and verify the expiry is short-lived.

## Milestone 3 Step 4: Capability enforcement at tool-b

tool-b now requires a capability token (Biscuit) in addition to identity.
Identity-only access is denied; capabilities are explicit, scoped, and short-lived.
For this lab, error responses include explicit reasons to make failures easy to observe.
In real-world deployments, those reasons are typically generalized to avoid leaking policy details.

## M3.S2 tests

Run the OPA-gated capability minting tests:
```bash
docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
```

### Note on test-only services

The service `capability-issuer-no-opa-envoy` exists **only for tests**.

Its purpose is to deterministically validate **fail-closed behavior**
of the Capability Issuer when the policy decision point (OPA) is
unavailable.

Key points:
- It is used exclusively in test profiles.
- It has a SPIRE workload entry solely so Envoy can enforce SPIFFE mTLS
  during tests.
- It is not intended as a production deployment pattern.

This service ensures that capability minting never succeeds without
an explicit policy decision.
