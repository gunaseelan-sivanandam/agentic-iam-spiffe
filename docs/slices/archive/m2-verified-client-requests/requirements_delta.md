# Requirements Delta

## Requirement changes
- Tighten `REQ-M2-R10` so runtime client requests that are part of security proof must validate the server certificate chain during the actual request path.
- Tighten `REQ-M2-R11` so runtime client requests that are part of security proof must verify the expected service identity using the server SPIFFE URI SAN during the actual request path.
- Clarify that verification on one connection and request execution on another does not satisfy these requirements.
- Clarify that coarse readiness checks are not evidence of verified server identity.

## Ambiguities removed
- Remove the ambiguity that a separate negative TLS test is enough to satisfy ordinary verified request behavior.
- Remove the ambiguity that `curl --cacert` without explicit SPIFFE URI SAN verification would satisfy expected service identity verification.
- Remove the ambiguity that IP-pinned HTTPS requests with `Host:` headers are an acceptable proof path for verified service identity.

## Black-box contract
- A successful black-box client request to `tool-b-envoy` or `capability-issuer-envoy` must prove, in the same request path:
  - the server certificate chains to the trusted SPIFFE bundle
  - the server presents the expected SPIFFE URI SAN
  - the HTTP response is returned on that verified connection
- If certificate validation or expected service identity verification fails, the request must fail and must not be reported as a valid proof of behavior.
