# Open Problem Log

Purpose:
- Track real runtime or trust-model problems that were discovered through black-box validation but are not yet fixed.
- Keep these problems independent from slice-progress notes so they remain visible until closed.

Usage:
- Add one entry per distinct problem.
- Prefer evidence-backed statements only.
- Link to the relevant requirement, architecture, test, and evidence artifacts when available.
- Mark an entry closed only after the fix is implemented and validated.

## OPL-001: Test-profile Envoy can serve an expired SVID during verified-TLS runs

- Status: Open
- First observed: 2026-04-26
- Area: `M2` / `M3` verified TLS request path
- Affected service:
  - `capability-issuer-no-opa-envoy`
- Related tests:
  - `M3.S2-T4`
- Related requirement:
  - `REQ-M2-R10`
  - `REQ-M2-R11`

### Problem
- Verified-TLS runs can intermittently fail because `capability-issuer-no-opa-envoy` serves an expired SPIFFE SVID.
- When that happens, the verified request helper correctly rejects the server certificate before HTTP response parsing.
- The older curl-based header capture can still appear healthy because it uses `--insecure`, which masks the expired-cert condition.

### Evidence
- In a failing `M3.S2-T4` full milestone run:
  - `verified_capiss_spiffe_id.txt` contained `spiffe://example.org/capability-issuer-no-opa-envoy`
  - `verified_capiss_result.txt` contained `fail`
  - `status.txt` and `mint_body.json` were empty because TLS verification failed before a valid HTTP response was accepted
- Header capture from the same run showed the server certificate expiry had already passed:
  - request time: `Sun, 26 Apr 2026 10:21:47 GMT`
  - certificate expiry: `Apr 26 10:21:05 2026 GMT`

### Current understanding
- Envoy entrypoints refresh SVID files periodically from SPIRE agent output, but the current setup does not give a reliable end-to-end guarantee that the serving Envoy process starts using the renewed cert before expiry.
- Test-profile services are easier to leave stale because:
  - core stack startup does not necessarily recreate `tests` profile services
  - targeted or milestone test runs can reuse already-running test-profile containers

### Why this matters
- This is a real trust-path problem, not a harness-only false red.
- Verified TLS is supposed to reject expired server identity.
- If the test-only Envoy can serve an expired cert, black-box validation becomes intermittent and the repo cannot claim reliable verified-TLS behavior on that path.

### Immediate mitigation
- Recreate test-profile services before verified-TLS test runs when freshness is in doubt.

### Meaningful fix options to evaluate
1. Make test-profile service lifecycle deterministic for verified-TLS runs:
   - force recreation of `capability-issuer-no-opa` and `capability-issuer-no-opa-envoy` before the affected tests
2. Prove or improve live certificate reload in the Envoy setup:
   - verify whether Envoy actually starts serving refreshed SVID files after rotation
   - if not, add an explicit reload strategy that is compatible with the current SPIRE file-refresh model
3. Strengthen black-box guard coverage:
   - add an explicit freshness/expiry guard for test-profile Envoy identity before the affected verified-TLS tests run

### Closure criteria
- Verified-TLS runs no longer fail intermittently due to expired server certs on `capability-issuer-no-opa-envoy`
- The chosen fix is documented
- `M3.S2-T4` passes reliably in repeated full and targeted runs without relying on `--insecure` behavior
