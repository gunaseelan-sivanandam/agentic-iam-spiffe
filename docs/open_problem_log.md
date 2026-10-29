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
  - `verified_capiss_spiffe_id.txt` contained `spiffe://varambu.org/capability-issuer-no-opa-envoy`
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
  - `docs/slices/archive/m4a-jira-project-access/`
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
  - `docs/slices/archive/m4a-jira-project-access/`
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

## OPL-005: capiss root signing key is readable by verifiers and by the rogue test container

- Status: Open
- First observed: 2026-10-27
- Area: capability issuance trust root / key isolation
- Affected configuration:
  - `compose/spiffe.compose.yml`: the host directory `capiss_keys/` (holding both `root_key.b64` and `root_public_key.b64`) is bind-mounted read-only into `tool-b`, `jira-tool`, `jira-mcp-gateway`, `agent-a`, and `rogue`
  - no service image sets a non-root `USER`
- Related requirements:
  - `REQ-M3-R22` (capability authenticity verification) and the M1/M2 rogue isolation requirements
- Related document:
  - the archived `docs/archive/SECURITY_MODEL.md` claimed "the private key never leaves the issuer container"; that claim is false

### Problem
- The capiss private signing key file is present in every verifier container and in the `rogue` test container, and all of them run as root, so the 0600 file mode does not protect it.
- Anything that can read the private key can sign arbitrary Biscuit capabilities. That bypasses OPA and capiss entirely: a compromised verifier, or the rogue workload the suite models as an attacker, could mint any authority.
- No E2E test covers this; `M2-T7` checks SVID key isolation, not the capiss signing key.

### Evidence (2026-10-27, running stack after a clean full E2E run)
- `capiss_keys/root_key.b64` on the host: owner `root`, mode `600`.
- `docker exec <container> id -u` returned `0`, and `test -r /var/lib/capiss/keys/root_key.b64` succeeded, in `spiffe-tool-b`, `spiffe-jira-tool`, and `spiffe-jira-mcp-gateway`.
- `docker compose --profile tests run --rm --no-deps --entrypoint sh rogue -c 'id -u; test -r /var/lib/capiss/keys/root_key.b64'` returned uid `0` and "readable".
- The key contents were not read or printed during this check.

### Evidence (2026-10-28, forgery confirmed on the running stack)
- The private key was read as uid 0 inside `capability-issuer`, `tool-b`, `jira-tool`, `jira-mcp-gateway`, and a one-off `rogue` container; all five SHA-256 hashes match. Only hashes were printed.
- Inside `tool-b`, a script loaded the key and called tool-b's own `verify_biscuit` (the function the HTTP handler uses) with the real public key and the real Redis:
  - the private key derives exactly the public key tool-b trusts, so it is the live signing key;
  - a forged root token for `/secret` (`act=read`, subject `spiffe://varambu.org/agent-a`) with an unknown root id passed signature and chain checks and was refused only with `budget_exceeded` (no Redis budget for that id);
  - the same forged token, with a budget for its root id present in Redis, was **allowed**.
  - The script deleted the Redis keys it created; none remained.
- The only non-cryptographic barrier is the Redis budget keyed on `root_token_id`. Redis has no authentication and every verifier can write it (OPL-007), so a compromised verifier can forge and fund any capability. `agent-a` and `rogue` are not on a Redis network; they could likely reuse the root id of a token they legitimately hold to forge a different `act`/`res`, but that path was not demonstrated.
- tool-b still requires the token subject to match the caller's mTLS SPIFFE ID, so a forger acts under an identity it already has.

### How it was introduced
- `07520d7` (2026-01-05) mounted the whole `capiss_keys/` directory into `tool-b`, although the code already separated the keys (private `0600`, public `0644`, tool-b opens only the public file). Every container runs as root, so the file mode never protected anything.
- The volume block was copied into `agent-a` and `rogue` (`4b808cb`, 2026-03-03), `jira-tool` (`16072e0`, 2026-05-15) and `jira-mcp-gateway` (`1b84bc4`, 2026-05-16).
- No requirement named who may hold the signing key, no test inspected container filesystems, the M3 red team modelled only a network attacker, and the security model asserted the opposite. The process changes that respond to this are in the [agentic-delivery-process](slices/agentic-delivery-process/plan.md) slice.

### Current understanding
- Verifiers only need the public key: `tool-b`, `jira-tool`, and `jira-mcp-gateway` open `CAPISS_PUBLIC_KEY_PATH` (`root_public_key.b64`) and nothing else.
- Nothing in `agent-a` or `rogue` reads this directory; no script or harness code references it there.

### Meaningful fix options to evaluate
1. Publish the public key separately (its own file mount or volume) and stop mounting `capiss_keys/` into anything except `capability-issuer` and `capability-issuer-no-opa`.
2. Run services as a non-root user so file permissions protect the private key as a second layer.
3. Add an E2E negative test: the rogue and every verifier cannot read the private key, while verifiers can still read the public key.

### Closure criteria
- The private key file exists only in the capiss containers.
- An E2E test proves the rogue and the verifiers cannot read it, and the full suite still passes.
- `docs/architecture.md` (security model summary) is updated to remove the caveat.

## OPL-006: SPIRE agent private key store is readable by every workload that mounts the agent directory

- Status: Open
- First observed: 2026-10-28
- Introduced: `bed2d0e` (2025-12-26), when the agent `data_dir` was placed inside the directory shared with workloads for the Workload API socket
- Area: workload identity trust root / key isolation
- Affected configuration:
  - `spire/agent/agent.conf`: `data_dir = "/run/spire/agent/data"`, `socket_path = "/run/spire/agent/private/api.sock"`
  - `compose/spiffe.compose.yml`: host `spire/agent/` is mounted at `/run/spire/agent` (read-only) into `tool-b`, `tool-b-envoy`, `jira-tool`, `jira-tool-envoy`, `jira-mcp-gateway`, `jira-mcp-envoy`, `capability-issuer-envoy`, `capability-issuer-no-opa-envoy`, `codex-jira-mcp-adapter`, `agent-a`, `rogue`, and `rogue-socket`
- Related requirements:
  - `REQ-M2-R5` (workload private key isolation) — violated; it has no E2E link (`E2E-M2-SUITE` lists no `source_requirements`)

### Problem
- Workloads need only the Workload API socket, but they receive the agent's whole runtime directory, including `data/keys.json` (the agent's private key store) and `data/agent-data.json`.
- All containers run as root, so the directory mode `0750 root:root` does not protect it.
- `M2-T7` ("Rogue cannot read SVIDs or keys") does not detect this: it starts a temporary rogue container *without* the agent mount and checks that one. The deployed `rogue` service does mount it.

### Evidence (2026-10-28, running stack)
- `/run/spire/agent/data/keys.json` was readable as uid 0 in `tool-b`, `jira-tool`, `jira-mcp-gateway`, `codex-jira-mcp-adapter`, and `tool-b-envoy`; all five SHA-256 hashes match (only hashes and the top-level JSON field name `keys` were printed).

### Current understanding
- With the agent's private key and its SVID, a container could likely act as the node agent towards the SPIRE server and obtain SVIDs for every workload registered under that node, which would defeat mTLS identity, not only authorization. This was not demonstrated.

### Meaningful fix options to evaluate
1. Mount only the socket directory (`/run/spire/agent/private`) into workloads, and keep `data_dir` outside any shared mount.
2. Run services as non-root (REQ-SEC-D2).
3. Correct `M2-T7` to check the deployed `rogue` container, and add the runtime invariant matrix for REQ-SEC-K2.

### Closure criteria
- `keys.json` and `agent-data.json` exist only in `spire-agent`.
- An E2E test on the deployed containers proves no workload can read them, and the full suite still passes.

## OPL-007: Redis authorization state accepts unauthenticated writes from every verifier network

- Status: Open
- First observed: 2026-10-28
- Area: authorization state integrity (budgets, rate limits, discovery registry)
- Affected configuration:
  - `compose/spiffe.compose.yml`: `redis-server --save '' --appendonly no`, no `requirepass` or ACLs
  - Redis is attached to `capiss_app_net`, `toolb_app_net`, `jiratool_app_net`, and `jiramcp_app_net`, so `capability-issuer`, `tool-b`, `jira-tool`, `jira-mcp-gateway`, their Envoys, `opa`, and `jira-mcp-mock` can reach it (plus the test-only `capability-issuer-no-opa` and its Envoy)
- Related requirements: `REQ-M4-*` budget and rate enforcement (proposed `REQ-SEC-S1`)

### Problem
- Any process on those networks can create, raise, or delete `m4:budget:*`, `m4:rate:*`, and `m4:registry:*` keys. Budgets are meant to be created only by capiss at mint time.
- Combined with OPL-005, a compromised verifier holds everything needed to forge and fund a capability.

### Evidence (2026-10-28)
- `redis-cli CONFIG GET requirepass` returned an empty value.
- The OPL-005 forgery check wrote and deleted a budget key from inside `tool-b` without credentials.

### Meaningful fix options to evaluate
1. Redis ACL users per service, limited to the key families each service writes in the ARCH-016 state inventory (capiss: budget initialisation, mint rate, `m4:capiss_minted:*`; tool-b: `m4:registry:*`, budget consumption, request rate); the default user is disabled. Redis checks commands run inside a Lua script against the caller's own permissions, so ACLs alone cannot make budget consumption script-only: a service allowed `DECRBY` can also call it directly with a negative amount. Budget integrity needs mediation or an accepted residual (see proposed `REQ-SEC-S1`).
2. Take Redis off networks that need no access (for example `jira-mcp-mock`, the Envoys, `opa`).

### Closure criteria
- Unauthenticated Redis commands are refused, and each service can perform only its documented operations.
- An E2E test proves a verifier cannot create a budget, and the full suite still passes.

## OPL-008: spire-token-init mounts the whole SPIRE server data directory

- Status: Open
- First observed: 2026-10-29 (independent plan review, finding PR-33)
- Area: SPIRE trust root confinement
- Affected configuration:
  - `compose/spiffe.compose.yml`: `spire-token-init` mounts `../spire/server:/run/spire/server` read-write
  - `spire/token-init/init.sh` needs only the admin socket `/run/spire/server/data/private/api.sock`
- Related requirements: proposed `REQ-SEC-K4` (server signing state) and `REQ-SEC-K5` (administration)

### Problem
- To reach the admin socket, `spire-token-init` also gets the server's signing keys (`data/keys.json`) and datastore (`data/datastore.sqlite3`), read-write.

### Evidence (2026-10-29)
- Compose line 17 mounts the directory; `init.sh` line 5 uses only the socket path inside it.

### Meaningful fix options to evaluate
1. Mount only the socket's directory (`data/private/`).
2. Move token and entry bootstrap into the server container's entrypoint and drop `spire-token-init`.

### Closure criteria
- The bootstrap step cannot read `keys.json` or the datastore, and the invariant matrix K4 row proves it on the deployed stack.

## OPL-009: The delivery pipeline does not resist a deliberately malicious PR

- Status: Accepted (decision D18, 2026-10-29)
- First observed: 2026-10-28 (independent plan review, findings PR-01, PR-21, PR-22, PR-29)
- Area: delivery process trust
- Related: [`plan.md` "Threat model"](slices/agentic-delivery-process/plan.md#threat-model-d18)

### Problem
- Code a PR runs during testing could, if written to do so, take over the test runner (for example through a Docker-socket-holding image), forge coverage or mutation statistics with matching identifiers, or append falsified run records.
- The pipeline is designed against a fallible, reward-seeking agent, not a deliberate attacker of its own infrastructure; there is no current reason to expect the latter.

### Mitigations
- Changes to the harness, tests, test config, compose and gate code take the full-slice lane and the user's review (slice 2).
- `main` reruns the full suite nightly (slice 2).
- Credentials and merge rights are enforced by GitHub, not by agent instructions (slice 3).

### Closure criteria
- Re-confirmed at each programme review, or the threat model changes and the delivery infrastructure gains trusted builders, authenticated run records and per-job isolation.
