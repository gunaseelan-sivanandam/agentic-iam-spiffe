# Unit Test Specification (M4 Trust Gates)

Status of this document:
- This is an internal engineering support matrix for unit-test planning and review.
- It is not the primary black-box proof source for requirement satisfaction.
- Requirement satisfaction should be argued first through authored runtime mappings and evidence.

This document specifies unit-test trust controls for the M4 slice and maps
requirements to concrete tests. It complements integration specs in
`docs/test_spec.md` and `docs/test_spec_detailed.md`.

## Quality Gates

- `make unit-guard-check`
  - all tests under `tests/unit/**` must execute explicit `premise`, `exercise`, and `outcome` guard phases
  - any missing phase is a hard failure
- `make unit-cov`
  - total line coverage `>= 85%`
  - branch coverage `>= 75%` for:
    - `services/capability-issuer/app.py`
    - `services/tool-b/server.py`
- `make unit-invariants` (must pass 100%)
- `make unit-negative-controls` (must pass 100%)
- `make unit-hybrid-critical` (must pass 100%)
- `make unit-flake` (`invariant` suite repeated 5x, no failures)
- `make unit-diff-cov` (PR diff coverage threshold `>= 90%` for critical modules)
- `make unit-mutation` (mutation score threshold `>= 70%`)
- `make traceability-check` validates this matrix against `docs/requirements.md`

## Unit Guard Integrity

- Unit tests use the `guard` fixture from `tests/unit/conftest.py`.
- Required phase minimum per test:
  - `premise >= 1`
  - `exercise >= 1`
  - `outcome >= 1`
- Evidence is attached to test reports via user properties:
  - `guard_premise_count`
  - `guard_exercise_count`
  - `guard_outcome_count`
  - `guard_complete`
  - `guard_trace_json`
- `guard_exempt` exists only for exceptional local debugging and is disallowed by default.

## Requirement-to-Unit-Test Matrix

| Requirement ID | Requirement | Unit tests | Status | Notes |
|---|---|---|---|---|
| M4-D1 | Delegation must not increase authority | `tests/unit/capiss/test_chain_and_policy.py::test_verify_and_extract_chain_rejects_amplified_authority`, `tests/unit/capiss/test_endpoints.py::test_resource_mint_rejects_amplified_authority`, `tests/unit/capiss/test_negative_controls.py::test_resource_mint_amplification_exact_reason`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_rejects_amplification` | Covered | Enforces non-amplification and exact deny reasons. |
| M4-D2 | Canonical resources only | `tests/unit/capiss/test_canonicalize_resource.py::test_canonicalize_resource_matrix`, `tests/unit/capiss/test_canonicalize_resource.py::test_canonicalize_resource_rejects_wildcards` | Covered | Includes wildcard-like and malformed resource boundaries. |
| M4-D3 | Chain metadata is mandatory | `tests/unit/capiss/test_chain_and_policy.py::test_verify_and_extract_chain_missing_metadata`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_valid_root` | Covered | Validates required fields and metadata presence checks. |
| M4-D4 | Depth is per chain | `tests/unit/capiss/test_chain_and_policy.py::test_verify_and_extract_chain_valid_root`, `tests/unit/toolb/test_hybrid_critical.py::test_verify_biscuit_hybrid_delegated_chain_depth` | Covered | Effective depth evaluated from token chain presented. |
| M4-CH1 | Chain integrity verified at PEP/tool | `tests/unit/shared/test_enforcement_contract.py::test_verify_chain_contract_rejects_parent_mismatch`, `tests/unit/capiss/test_chain_and_policy.py::test_verify_and_extract_chain_rejects_parent_mismatch`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_rejects_res_change_without_marker`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_fail_closed_if_marker_store_unavailable` | Covered | Shared contract and both callers reject parent-link or transition integrity violations. |
| M4-DL1 | Depth derived from token chain | `tests/unit/shared/test_enforcement_contract.py::test_verify_chain_contract_rejects_invalid_depth_metadata`, `tests/unit/capiss/test_chain_and_policy.py::test_verify_and_extract_chain_rejects_invalid_depth_metadata`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_rejects_invalid_depth_metadata` | Covered | Shared contract rejects inconsistent depth metadata vs computed depth. |
| M4-DL2 | Depth limit enforced at PEP/tool | `tests/unit/shared/test_enforcement_contract.py::test_verify_chain_contract_enforces_depth_limit`, `tests/unit/capiss/test_chain_and_policy.py::test_verify_and_extract_chain_enforces_depth_limit`, `tests/unit/capiss/test_negative_controls.py::test_resource_mint_depth_exceeded_exact_reason`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_enforces_depth_limit` | Covered | Tests the shared contract boundary at `N` and `N+1`. |
| M4-DL3 | No depth renewal in reduced scope | `tests/unit/capiss/test_endpoints.py::test_resource_mint_enforces_depth_limit` | Partial | Ceiling enforced; no explicit renewal endpoint exists in current scope. |
| M4-B1 | Agents never decrement budgets | `tests/unit/toolb/test_budget_and_verify_biscuit.py::test_verify_biscuit_budget_reason_mapping`, `tests/unit/toolb/test_hybrid_critical.py::test_verify_biscuit_hybrid_root_secret_token` | Partial | Unit tests validate trusted-side decrement path, not agent internals. |
| M4-B2 | Spend enforced per request by trusted service | `tests/unit/toolb/test_budget_and_verify_biscuit.py::test_consume_budget_and_rate_ok`, `tests/unit/toolb/test_budget_and_verify_biscuit.py::test_verify_biscuit_budget_reason_mapping` | Covered | Budget checked during each verify path call. |
| M4-B3 | Spend keyed by `root_token_id` | `tests/unit/toolb/test_budget_and_verify_biscuit.py::test_consume_budget_and_rate_ok`, `tests/unit/capiss/test_hybrid_critical.py::test_resource_mint_hybrid_new_resource_with_registry` | Covered | Root token ID drives keying behavior and flow continuity. |
| M4-B4 | Atomic decrement and deterministic deny | `tests/unit/toolb/test_budget_and_verify_biscuit.py::test_verify_biscuit_budget_reason_mapping`, `tests/unit/toolb/test_negative_controls.py::test_verify_biscuit_budget_exceeded_exact_reason`, `tests/unit/toolb/test_negative_controls.py::test_verify_biscuit_rate_limited_exact_reason` | Covered | Exact deny reason mapping verified. |
| M4-B5 | Budget lifetime bounded by TTL | `tests/unit/toolb/test_utils.py::test_is_capiss_minted_token_hit_with_ttl_adjust` | Partial | TTL behavior partially tested; budget key TTL boundaries not exhaustively simulated. |
| M4-B6 | No budget renewal in reduced scope | `-` | Gap | Add explicit renewal-attempt denial test if renewal path is introduced. |
| M4-B7 | New-resource mint rate enforced at `capiss` | `tests/unit/capiss/test_utils.py::test_consume_mint_rate_allows_until_formula_limit_then_denies`, `tests/unit/capiss/test_utils.py::test_consume_mint_rate_uses_exact_key_allowance_and_ttl`, `tests/unit/capiss/test_utils.py::test_consume_mint_rate_formula_scales_and_floors_to_one`, `tests/unit/capiss/test_endpoints.py::test_resource_mint_new_resource_consumes_mint_rate_once`, `tests/unit/capiss/test_endpoints.py::test_resource_mint_denies_when_mint_rate_exceeded`, `tests/unit/capiss/test_endpoints.py::test_resource_mint_fail_closed_when_mint_rate_store_unavailable` | Covered | Formula-derived allowance, exact Redis keying, endpoint integration, deny, and fail-closed behavior are covered. |
| M4-P1 | New resources require registry proof | `tests/unit/capiss/test_endpoints.py::test_resource_mint_requires_registry_hit_for_new_resource`, `tests/unit/capiss/test_negative_controls.py::test_resource_mint_requires_registry_proof_exact_reason` | Covered | Includes exact `registry_miss` deny reason. |
| M4-P2 | Discovery registry authoritative under root | `tests/unit/capiss/test_hybrid_critical.py::test_resource_mint_hybrid_new_resource_with_registry`, `tests/unit/toolb/test_budget_and_verify_biscuit.py::test_record_discovery_fails_closed_on_store_error` | Partial | Unit coverage exists; full producer authority is integration/system concern. |
| M4-P3 | Only trusted producers may write registry | `tests/unit/toolb/test_handler_paths.py::test_do_get_search_success` | Partial | Path behavior covered; trust-boundary enforcement mostly integration-level. |
| M4-P4 | Registry entries are TTL-bounded | `tests/unit/toolb/test_utils.py::test_record_discovery_success` | Partial | Registry write path covered; explicit TTL boundary assertions remain limited. |
| M4-E1 | Enforcement independent of agent honesty | `tests/unit/capiss/test_chain_and_policy.py::test_run_policy_or_fail_fail_closed_when_opa_unavailable`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_fail_closed_if_marker_store_unavailable`, `tests/unit/toolb/test_budget_and_verify_biscuit.py::test_consume_budget_and_rate_fail_closed_on_redis_error` | Covered | Fail-closed behavior validated for key trusted components. |
| M4-E2 | Single shared enforcement contract | `tests/unit/shared/test_enforcement_contract.py::test_verify_chain_contract_valid_root`, `tests/unit/capiss/test_chain_and_policy.py::test_verify_and_extract_chain_uses_shared_contract`, `tests/unit/toolb/test_canonical_and_chain.py::test_verify_chain_and_claims_uses_shared_contract` | Covered | Shared module owns the chain contract and both services use thin adapters. |
| M4-E3 | capiss not in hot path for protected requests | `tests/unit/toolb/test_hybrid_critical.py::test_verify_biscuit_hybrid_root_secret_token` | Covered | Request-time checks done in tool-b verify path. |
| M4-E4 | Identity binding mandatory | `tests/unit/capiss/test_endpoints.py::test_resource_mint_rejects_subject_mismatch`, `tests/unit/toolb/test_negative_controls.py::test_verify_biscuit_subject_mismatch_exact_reason` | Covered | Exact mismatch deny behavior validated. |
| M4-E5 | Header trust requires network boundary | `-` | Gap | Network boundary trust is integration/envoy/system concern. |
| M4-O1 | Every enforcement decision emits audit event | `tests/unit/toolb/test_handler_paths.py::test_deny_writes_standard_payload` | Partial | Current unit checks validate payload shape indirectly; full audit event schema coverage can be expanded. |
| M4-O2 | capiss logs every mint decision with provenance | `tests/unit/capiss/test_endpoints.py::test_root_mint_requires_spiffe_id_logs_final_decision`, `tests/unit/capiss/test_endpoints.py::test_root_mint_policy_deny_logs_final_decision`, `tests/unit/capiss/test_endpoints.py::test_root_mint_success_logs_final_decision`, `tests/unit/capiss/test_endpoints.py::test_resource_mint_requires_bearer_token_logs_final_decision`, `tests/unit/capiss/test_endpoints.py::test_resource_mint_registry_miss_logs_final_decision`, `tests/unit/capiss/test_endpoints.py::test_resource_mint_success_logs_final_decision` | Covered | Final `capiss_mint_decision` payloads are asserted across root and resource allow/deny branches, including early exits and governed resource-mint paths. |
| M4-O3 | Chain reconstruction always possible | `-` | Gap | Requires cross-component event correlation tests. |
| M4-O4 | Drift visibility is mandatory | `-` | Gap | Requires aggregated telemetry validation beyond unit scope. |

## Current Gaps (Explicit)

- `M4-B6`: no explicit budget-renewal denial scenario test.
- `M4-E5`: network-boundary assurance belongs to integration/system tests.
- `M4-O3`, `M4-O4`: observability reconstruction/drift analytics need integration or log-pipeline tests.
