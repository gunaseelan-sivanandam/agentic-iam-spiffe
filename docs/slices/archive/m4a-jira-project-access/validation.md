# Validation

## Planned checks
- `make unit-guard-check`
- `make unit-trust`
- Targeted M4a E2E with `TEST_MILESTONES=m4a`
- Full deterministic E2E suite
- `make qa-trace`
- `make qa-quality`
- `make qa-evidence`
- Optional live smoke target when Jira live inputs are available

## Runtime proof
- M4a E2E evidence must show broad upstream mock access exists independently of `jira-tool`.
- Optional live-smoke evidence, when run, must show the live API credential can directly read both an `IAM-*` issue and a `NAS-*` issue before evaluating the protected capiss/jira-tool path.
- M4a E2E evidence must show OPA/capiss mint deny for a non-allowed project.
- M4a E2E evidence must show request-time project mismatch deny before upstream call.
- M4a E2E evidence must show rogue mint deny and stolen-token subject-binding deny.
- M4a E2E evidence must show shared budget consumption and default-budget exhaustion denial before upstream call.
- M4a E2E evidence must show upstream project mismatch/unverifiable response denial without body return.
- M4a E2E evidence must show correlated `capiss_mint_decision` and `jiratool_enforcement_decision` events.
- M4a E2E evidence must show edge clients reach the Jira facade through `jira-tool-envoy`, not by direct access to `jira-tool` or `jira-mock`.
- M4a E2E evidence must show mock request-log/reset endpoints are used only through test/internal access, not through the agent edge path.
- Agent-demo evidence must not include bearer tokens or Jira API credentials.
- Local authorization-deny evidence must show standardized local deny bodies rather than upstream project-existence details.

## Semantic trace review
- Each M4a requirement must map to Jira-specific architecture responsibility and at least one black-box M4a E2E case where feasible.
- M4 primitives such as subject binding, token authenticity, budget/rate, and fail-closed behavior may be referenced instead of restated, but M4a must prove the new Jira enforcement point actually participates in those primitives.

## Completion notes
- Fill in after implementation:
  - targeted unit/E2E results
  - full QA results
  - live-smoke result if run
  - warnings or deferred follow-ups
