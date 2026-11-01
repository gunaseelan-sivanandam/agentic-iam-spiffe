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
- **V1** `test_ruleset_without_a_required_approval_fails`: a ruleset with no `pull_request` rule, and
  one with `required_approving_review_count: 0`, each yield exactly the problem "the main ruleset does
  not require an approving review".
- **V2** `test_pull_request_rule_without_parameters_fails`: a `pull_request` rule without parameters
  yields the same problem (a missing count is read as 0).
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
- By hand: `gh api user --jq .login` prints `gunaseelan-agent` in the agent session; the PR's author
  and commits show the bot.
- No E2E run: nothing in the stack changes.

## Review notes
- None.
