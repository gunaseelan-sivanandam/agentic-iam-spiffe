# Code Review Log

## Slice 1: Jira Authority Issuance

Review status: completed.

Finding:
- Slice ID: M4a-S1
- Severity: Medium
- Description: capiss mint-decision policy metadata still used the M4 `capiss.allow.v2` static version after the Jira OPA rule was added.
- Affected behavior/files: `services/capability-issuer/app.py`, `tests/unit/capiss/test_endpoints.py`, `tests/unit/capiss/test_chain_and_policy.py`
- Fix made: introduced `CAPISS_POLICY_ID=capiss.allow.v3` and `CAPISS_POLICY_HASH=sha256:capiss-policy-v3`, then updated unit expectations.
- Verification command/evidence: `pytest tests/unit/capiss/test_canonicalize_resource.py tests/unit/capiss/test_jira_mint.py tests/unit/jiratool/test_authorization.py`; `python3 scripts/validate_traceability.py --requirements-doc docs/requirements.md --architecture-doc docs/architecture.md --tests trace/tests.yaml --report-json /tmp/trace-pre.json --design-report-json /tmp/design-pre.json`

## Slice 2: Jira Mock + Protected Happy Path

Review status: completed.

Finding:
- Slice ID: M4a-S2
- Severity: Medium
- Description: unit trace IDs initially collided with an existing `UT-144`, which would create false trace ambiguity.
- Affected behavior/files: `tests/unit/capiss/test_canonicalize_resource.py`, `tests/unit/capiss/test_jira_mint.py`, `tests/unit/jiratool/test_authorization.py`
- Fix made: renumbered the new M4a unit tests to `UT-158` through `UT-171`.
- Verification command/evidence: `python3 scripts/validate_traceability.py --requirements-doc docs/requirements.md --architecture-doc docs/architecture.md --tests trace/tests.yaml --report-json /tmp/trace-pre.json --design-report-json /tmp/design-pre.json`

## Slice 3: Deny Paths and No-Upstream Proof

Review status: completed.

Finding:
- Slice ID: M4a-S3
- Severity: High
- Description: M4a deny-path evidence could accidentally persist raw bearer tokens if mint responses were copied directly into evidence directories.
- Affected behavior/files: `scripts/rogue_node_tests.sh`
- Fix made: M4a E2E tests now keep raw mint responses in `/tmp`, write only token-stripped mint metadata into evidence, and pass bearer tokens through temporary files rather than command-captured literals.
- Verification command/evidence: `sh -n scripts/rogue_node_tests.sh`; targeted unit run listed above.

## Slice 4: Governance Exhaustion and Response Safety

Review status: completed.

Finding:
- Slice ID: M4a-S4
- Severity: Medium
- Description: architecture and README text still described M4a as planned/target-state after implementation files were added.
- Affected behavior/files: `docs/architecture.md`, `README.md`, `docs/only_arch.puml`, `docs/architecture_diagram.puml`
- Fix made: updated runtime documentation to describe M4a as implemented rather than planned.
- Verification command/evidence: `python3 scripts/validate_traceability.py --requirements-doc docs/requirements.md --architecture-doc docs/architecture.md --tests trace/tests.yaml --report-json /tmp/trace-pre.json --design-report-json /tmp/design-pre.json`

## Slice 5: Agent Demo and Live/Mock Test Selection

Review status: completed.

Finding:
- Slice ID: M4a-S5
- Severity: High
- Description: the agent demo and live smoke paths needed explicit output safeguards so bearer tokens and live Jira credentials are not printed into operator-facing evidence.
- Affected behavior/files: `agents/agent-a/jira_demo.sh`, `scripts/jira_live_smoke.sh`
- Fix made: demo output prints only statuses, reason codes, and token metadata; live smoke stores direct Jira precondition status/project keys only and scans protected demo output for credential-like material.
- Verification command/evidence: `sh -n agents/agent-a/jira_demo.sh`; `sh -n scripts/jira_live_smoke.sh`

## Slice 6: Full Traceability, Retirement, and QA Closure

Review status: completed.

Finding:
- Slice ID: M4a-S6
- Severity: Low
- Description: no obsolete Jira scaffolding or compatibility paths were found after the M4a implementation pass.
- Affected behavior/files: `services/jira-tool/**`, `services/jira-tool-envoy/**`, `services/jira-mock/**`, `scripts/rogue_node_tests.sh`
- Fix made: no retirement change required.
- Verification command/evidence: `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_MILESTONES=m4a rogue-tests`; `docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests`; `make unit-trust`; `make qa-trace`; `make qa-evidence`; `make qa-quality`.

Finding:
- Slice ID: M4a-S6
- Severity: Medium
- Description: the `M4a-T9` mock request-log assertion used a jq pipe expression that evaluated the issue-key check against the request array rather than the root evidence object, creating a false failure even when the mock log showed exactly one `IAM-999` upstream call.
- Affected behavior/files: `scripts/rogue_node_tests.sh`
- Fix made: parenthesized the jq expression so length and issue-key checks both evaluate against the intended JSON structure.
- Verification command/evidence: targeted M4a E2E passed `10/10`; full E2E passed `56/56`.

Finding:
- Slice ID: M4a-S6
- Severity: Medium
- Description: the full suite exposed an order-dependent readiness race after `M4-T14` restarted `capability-issuer`; `M4a-T2` could observe `capability-issuer-envoy` TCP readiness before capiss `/health` was serving, producing a transient `503` mint and a cascading missing-token read.
- Affected behavior/files: `scripts/rogue_node_tests.sh`
- Fix made: `ensure_capiss_envoy_ready` now requires an mTLS `/health` `200` through `capability-issuer-envoy` when client material is available, and critical M4a mint outcomes short-circuit before protected reads.
- Verification command/evidence: clean full E2E passed `56/56`; `make qa-evidence` passed with two accepted pre-existing M3 isolation warnings.

Finding:
- Slice ID: M4a-S6
- Severity: Medium
- Description: adding `jira-tool` reduced aggregate service unit coverage below the existing `make unit-trust` coverage gate.
- Affected behavior/files: `tests/unit/jiratool/test_authorization.py`, `services/jira-tool/server.py`
- Fix made: added focused Premise/Exercise/Outcome unit coverage for issuer key loading, Redis budget/rate mapping, upstream URL/call helpers, local authorization status mapping, GET dispatch, standardized deny responses, and unsupported methods.
- Verification command/evidence: `make unit-trust` passed with `194 passed`, total line coverage `89.62%`, and `jira-tool` line coverage `87%`.
