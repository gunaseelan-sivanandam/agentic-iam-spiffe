# Validation

## Planned checks
- `make qa-trace`
- `make qa-quality`
- E2E or targeted test runs:
  - targeted M2 suite
  - targeted M3 suite sections that reuse the affected HTTPS helpers
  - full E2E run after targeted validation passes
- `make qa-evidence` when applicable

## Runtime proof
- A valid request to `tool-b-envoy` succeeds through a verified TLS request path and records evidence consistent with expected service identity.
- A valid request to `capability-issuer-envoy` succeeds through a verified TLS request path and records evidence consistent with expected service identity.
- Existing handshake rejection cases remain green.
- No runtime proof case still depends on `--insecure` for its ordinary HTTPS request execution path.

## Completion notes
- Fill in after implementation:
  - what passed
  - what warnings remained
  - what follow-up work is still open
