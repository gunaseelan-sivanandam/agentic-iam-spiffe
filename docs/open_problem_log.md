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

## OPL-003: Compatibility mint endpoint should be retired after root-mint migration

- Status: Open
- First observed: 2026-05-14
- Area: capability issuance API lifecycle
- Related slice:
  - `docs/slices/m4a-jira-project-access/`
- Related endpoint:
  - `/capabilities/mint`
  - `/capabilities/root-mint`

### Problem
- `capiss` still exposes `/capabilities/mint` as a backward-compatible path that dispatches to root mint.
- New M4a docs and tests should use `/capabilities/root-mint`, but existing M3/M4 paths still depend on the compatibility endpoint.
- Keeping both endpoints indefinitely weakens API clarity and can make examples or tests ambiguous about root minting versus delegated/resource minting.

### Current understanding
- The compatibility endpoint is intentionally retained for existing evidence paths.
- Retiring it is outside M4a because the Jira slice should not disturb existing M3/M4 proof while adding a new connector.

### Meaningful fix options to evaluate
1. Migrate all existing docs, helpers, and tests to `/capabilities/root-mint`.
2. Add a deprecation warning or audit marker on `/capabilities/mint` before removal.
3. Remove `/capabilities/mint` after all black-box evidence paths use `/capabilities/root-mint`.

### Closure criteria
- No tests, docs, scripts, or demos depend on `/capabilities/mint`.
- `/capabilities/mint` is removed or explicitly deprecated with a planned removal window.
- Full E2E, unit, QA trace, and evidence gates pass after migration.

## OPL-004: capiss policy hash is static rather than computed from OPA policy source

- Status: Open
- First observed: 2026-05-14
- Area: auditability / policy provenance
- Related slice:
  - `docs/slices/m4a-jira-project-access/`
- Related audit event:
  - `capiss_mint_decision`

### Problem
- `capiss_mint_decision` events include a policy id/hash, but the hash is currently a static version string rather than a digest computed from the actual OPA policy source and data.
- M4a intentionally advances the static policy version for Jira semantics, but it does not implement real policy hashing.
- Static version strings are useful for coarse audit continuity, but they do not prove exactly which policy content produced a mint decision.

### Current understanding
- Real policy hashing is an observability hardening task, not required to prove M4a Jira project access.
- Implementing it requires deciding which policy/data files are in the hash boundary and how `capiss` obtains that digest reliably.

### Meaningful fix options to evaluate
1. Compute a deterministic digest from mounted OPA policy/data files at service startup.
2. Have OPA expose a policy bundle revision or digest that `capiss` records in mint-decision events.
3. Store an operator-supplied policy bundle version and treat it as advisory until real hashing is implemented.

### Closure criteria
- Mint-decision audit events include a policy provenance value derived from actual policy content or a documented policy bundle revision.
- The hash/version boundary is documented in architecture.
- Tests prove the audit field changes when policy content or bundle revision changes.
