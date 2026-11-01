# Slice Test Plan — agent-identity

## Goal
- Prove that `make gate-consistency` fails when the `main` ruleset stops requiring an approving
  review (D5). The bot identity itself (D1–D4) is local configuration outside the repository; it is
  checked by hand (below) and by the AGENTS.md identity check before each GitHub write.

## Inputs
- [`plan.md`](plan.md), decisions D1–D6.

## Unit test plan
- None (no `services/**` change).

## Tooling tests (`tests/tools/test_gate_consistency.py`)
- **V1** `test_ruleset_without_a_required_approval_fails`: a ruleset with no `pull_request` rule, or
  with `required_approving_review_count` `0`, `true` or `"1"`, yields exactly the problem "the main
  ruleset does not require an approving review" (only a positive integer counts).
- **V2** `test_pull_request_rule_without_parameters_fails`: a `pull_request` rule without parameters
  yields the same problem (a missing count is read as 0).
- **V3** `test_approval_count_in_another_rule_type_fails`: a count on a rule that is not
  `pull_request` does not count.
- **V4** `test_ruleset_that_is_not_active_fails`: `enforcement` `disabled` or `evaluate` yields
  exactly "the main ruleset is not active (enforcement: …)" (review finding AI-B1).
- Positive twins: `test_agreeing_lists_pass` and
  `test_repository_table_and_workflow_agree_with_the_planned_required_checks` use a ruleset with one
  required approval and expect no problems; the live run of `make gate-consistency` passes on the
  ruleset as the owner set it.

## E2E test plan
- None (the system under test does not change).

## Assumptions and fixtures
- The public ruleset API returns the `pull_request` rule's parameters without a token (probed
  2026-11-01).

## Planned verification commands
- `make tooling-test`, `make gate-consistency`, `make qa-quality`.
- By hand (external configuration, no gate can read it; results in the PR body):
  - **M0** in the agent session, `gh api user --jq .login` prints `gunaseelan-agent`; the PR's author
    and commits show the bot (D1–D3).
  - **M1** without the session `env` block (`env -u GH_CONFIG_DIR …`), `gh api user --jq .login`
    prints `gunaseelan-sivanandam` and `git var GIT_AUTHOR_IDENT` names the owner (D4).
  - **M2** read with the owner's login, the ruleset's `bypass_actors` is empty (D5; the public API
    and the bot cannot see it).
- No E2E run: nothing in the stack changes.

## Review notes
- None.
