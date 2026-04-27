# Implementation Contract

## Runtime behavior changes
- Normal HTTPS request execution paths in the harness and demo client will stop using `curl --insecure`.
- Requests to `tool-b-envoy`, `capability-issuer-envoy`, and `capability-issuer-no-opa-envoy` will execute on a verified TLS connection that:
  - validates the server chain against the SPIFFE bundle
  - extracts and checks the expected SPIFFE URI SAN
  - sends the HTTP request on that same connection
- DNS/TCP readiness checks remain separate and are not used as proof of verified service identity.

## Affected implementation areas
- Functions/modules expected to change:
  - `scripts/rogue_node_tests.sh`
  - `agents/agent-a/client.sh`
  - affected test-spec docs and trace mappings where the request mechanism is described as proof
- Functions/modules expected to be removed or retired:
  - internal `--insecure` request execution inside normal HTTPS helper flows
  - IP rewrite and `Host:` header identity workaround for verified request execution

## Exact contracts
- APIs/endpoints:
  - `https://tool-b-envoy:8443/health`
  - `https://tool-b-envoy:8443/secret`
  - `https://tool-b-envoy:8443/search`
  - `https://tool-b-envoy:8443/read-file/<id>`
  - `https://capability-issuer-envoy:9443/health`
  - `https://capability-issuer-envoy:9443/capabilities/mint`
  - `https://capability-issuer-envoy:9443/capabilities/resource-mint`
  - `https://capability-issuer-no-opa-envoy:9444/health`
  - `https://capability-issuer-no-opa-envoy:9444/capabilities/mint`
- Events/logs:
  - no new service audit events are introduced by this slice
  - harness evidence should record verification result and expected SPIFFE ID where relevant
- State keys:
  - none
- Reason codes:
  - no service reason-code changes are expected
- Failure modes:
  - request fails on trust-chain verification failure
  - request fails on expected SPIFFE URI SAN mismatch
  - request fails on connection/read timeout with explicit evidence capture

## Test intent
- UT to add:
  - only if helper parsing/extraction logic is split into testable shell/Python utility code; otherwise none
- E2E/integration to add:
  - update existing M2/M3 cases that currently rely on normal HTTPS request helpers so they prove verified request behavior instead of `--insecure` behavior
  - add or tighten evidence checks that the verified helper recorded expected service identity for representative success paths

## Explicit non-changes
- No change to service runtime topology or container wiring.
- No change to Envoy authorization policy.
- No change to Redis/OPA trust model.
- Existing negative TLS rejection tests may remain if they still provide useful complementary proof.
