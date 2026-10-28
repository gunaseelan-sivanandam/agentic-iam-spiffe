# ADR

## Architecture decision
- Verified client requests used as runtime proof must validate trust chain and expected SPIFFE URI SAN on the same TLS connection that carries the HTTP request.

## Alternatives considered
- Option A: keep `--insecure` request execution and rely on separate negative TLS tests
  - pros
    - minimal implementation work
    - no immediate test runtime change
  - cons
    - does not satisfy `REQ-M2-R10` / `REQ-M2-R11` on ordinary request paths
    - leaves black-box proof semantically false
- Option B: switch to `curl --cacert` only
  - pros
    - smaller code change than a new helper
    - preserves curl-based request ergonomics
  - cons
    - does not explicitly verify expected SPIFFE URI SAN identity
    - risks claiming server identity verification when only chain verification happened
- Option C: verify with one tool, then send the request with another
  - pros
    - easier incremental migration
  - cons
    - verification and request occur on different connections
    - adds latency and still weakens proof semantics
- Option D: one verified TLS connection that also carries the HTTP request
  - pros
    - semantically correct black-box proof
    - avoids IP pinning and host/header split
    - avoids double-handshake overhead
  - cons
    - requires a shared helper and careful parsing/stability work

## Chosen option
- Option D.
- The repo should prove verified service identity on the same connection used for the request. This is the smallest design that is both black-box-correct and operationally stable.

## Rejected options
- Options A, B, and C were rejected because they leave a semantic gap between “request succeeded” and “request proved the expected verified service identity.”
