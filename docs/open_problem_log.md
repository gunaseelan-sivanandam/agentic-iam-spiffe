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

## OPL-002: Traceability links are structurally valid but semantically over-claimed

- Status: Open
- First observed: 2026-05-13
- Area: requirements / architecture / traceability
- Related command:
  - `make qa-trace`
- Related artifacts:
  - `docs/requirements.md`
  - `docs/architecture.md`
  - `trace/tests.yaml`
  - `artifacts/quality/traceability_report.json`

### Problem
- `qa-trace` validates trace structure, ID existence, and layer-correct usage, but it does not validate whether each `REQ -> ARCH` link is semantically correct.
- A requirement can therefore appear satisfied when an architecture section is only adjacent to, supporting, evidentiary for, or unrelated to the requirement.
- The current `Satisfies:` relation is too coarse because it does not distinguish direct satisfaction from support, context, evidence, or future/partial responsibility.

### Evidence
- `make qa-trace` can pass while still reporting non-blocking coverage gaps such as `requirements_without_e2e`.
- M4 semantic review found over-claimed `Satisfies:` links where shared state or Redis-backed storage was marked as satisfying requirements whose enforcing responsibility belongs to `capiss`, `tool-b`, or Envoy.
- Examples observed during review:
  - `REQ-M4-B7` requires mint-rate enforcement at `capiss`; Redis/shared state supports the counter but does not enforce the mint policy.
  - `REQ-M4-E3` requires `capiss` not to be in the protected-request hot path; issuer/shared-state participation in minting does not itself satisfy that requirement.
  - `REQ-M4-O1` requires enforcement audit events; shared governance state does not emit request enforcement decisions.

### Current understanding
- The current trace model is structurally useful but can create false confidence when a syntactically valid link is treated as semantic satisfaction.
- This is a proof-model problem rather than an implementation failure by itself.
- The issue likely affects more than M4 because the same `Satisfies:` mechanism is used across all milestones.

### Why this matters
- The project operating model depends on black-box trust in authored requirements, architecture, trace mappings, and evidence.
- If `REQ -> ARCH` links are semantically over-claimed, the trace graph can look complete while the real responsibility and proof path are unclear or wrong.
- This weakens review quality and can hide unimplemented or only partially implemented requirements.

### Immediate mitigation
- Treat current `Satisfies:` links as structurally valid but not automatically semantically trusted.
- Perform AI-assisted semantic review milestone by milestone before relying on trace completeness claims.
- During review, classify each link as direct, supporting, context/evidence, partial, or wrong.

### Meaningful fix options to evaluate
1. Add an authored semantic trace review artifact:
   - record direct vs supporting/context/evidence relationships for every `REQ -> ARCH` claim
2. Tighten architecture wording:
   - keep only direct responsibility in `Satisfies:`
   - move support-only relationships to a separate relation or prose
3. Update trace QA after review:
   - keep structural validation
   - add a blocking semantic-contract check only after the authored review is complete

### Closure criteria
- Complete semantic review for all milestones, starting with M4 and then covering global, M1, M2, M2.5, and M3 requirements.
- Reclassify or remove incorrect `Satisfies:` links.
- Document direct vs supporting architecture responsibility for each reviewed requirement.
- Update traceability rules or review process so semantic over-claims are not treated as satisfied requirements.
