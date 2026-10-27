# Slice Plan

## Goal
- Replace `--insecure` on normal HTTPS request execution paths in the harness and demo client with one verified TLS request model that proves both trust-chain validation and expected service SPIFFE URI SAN identity on the same connection.

## Success criteria
- Normal HTTPS request execution paths no longer rely on `curl --insecure`.
- The request path verifies the server trust chain and the expected SPIFFE URI SAN before accepting the response.
- The HTTP request is sent on the same verified TLS connection.
- Final verified request execution no longer depends on IP pinning or `Host:` header spoofing.
- Existing M2 and M3 runtime scenarios continue to pass with stable timing.

## In scope
- Harness HTTPS request helpers in `scripts/rogue_node_tests.sh`.
- Demo client HTTPS request helpers in `agents/agent-a/client.sh`.
- Requirements and architecture deltas for verified client request behavior.
- Test-spec updates for the affected M2/M3 runtime proof paths.

## Out of scope
- Service runtime topology changes.
- Envoy listener policy changes.
- Redis, OPA, or tool-b/capability-issuer internal trust model changes.
- Replacing coarse DNS/TCP readiness checks that are not used as identity proof.
- Changing existing negative TLS rejection tests unless needed to reuse the new helper safely.

## Affected authored sources
- Requirements:
  - `REQ-M2-R10`
  - `REQ-M2-R11`
  - adjacent M3 runtime proof text where those verified request paths are reused
- Architecture:
  - `ARCH-003`
  - `ARCH-007`
  - `ARCH-018`
  - `ARCH-019`
- Runtime proof:
  - `trace/tests.yaml` entries under M2 and M3 that currently depend on normal HTTPS request helpers
  - `docs/test_spec.md`
  - `docs/test_spec_readable.md`
  - `docs/test_spec_detailed.md`

## Review notes
- The verified request helper must connect by service hostname, not by pinned IP, for the final HTTPS request.
- The helper must verify the expected SPIFFE URI SAN explicitly; trust-chain verification alone is not sufficient.
- Readiness checks may continue to use DNS/TCP probes, but they must not be treated as proof of verified service identity.
- This slice does not add a second parallel request model. Existing request helpers should be replaced or consolidated.
