# Requirements Delta

## Requirement changes
- Add M4a Jira-specific requirements proving that a broad Jira API credential held by `jira-tool` does not grant broad agent authority.
- Require OPA/capiss to mint Jira project authority only for explicitly allowed projects and deny all other project mint requests by default.
- Require `jira-tool` to enforce the signed Jira project token at request time before using the upstream Jira credential.
- Require `jira-tool` to deny non-allowed issue reads before upstream use when the issue key project does not match the token project.
- Require successful Jira reads to participate in existing M4 subject binding, token verification, budget/rate governance, audit logging, and fail-closed behavior.
- Require live Jira credentials to remain hidden from the agent and absent from tokens, normal logs, and evidence.
- Require local authorization denials to avoid revealing whether the requested Jira project exists upstream.
- Require the optional live smoke to prove the broad Jira credential can read both an allowed `IAM-*` issue and a non-allowed `NAS-*` issue before proving local narrowing.

## Ambiguities removed
- M4a authorizes workload identity, not human users.
- M4a supports project-wide read only; write/delete and issue-level attenuation are deferred.
- OPA stores allowed projects only; non-allowed project keys used by tests are inputs, not policy.
- Jira mock is broad upstream test infrastructure and must not be the component enforcing demo scope.
- The concrete allowed project for M4a is `IAM` in Jira space `agentic-iam-spiffe`; the concrete non-allowed test/demo project is `NAS` in Jira space `No-Agent-Space`.

## Black-box contract
- An agent with an allowed Jira project token can read an issue in that project through the protected facade.
- The same agent cannot mint or use authority for another Jira project even if the upstream API credential can access that project.
- Rogue cannot mint Jira authority or replay a stolen agent token.
- Evidence shows whether denial happened before upstream use and whether successful reads consumed shared budget.
