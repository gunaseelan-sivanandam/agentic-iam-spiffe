# Independent review — agent-identity

Reviewer: Codex (`codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral`), not the author, with
no network. It reviewed the branch against `origin/main`; round 1 at commit `5b33b79`, round 2 at
`34a285f`. Two rounds; round 2 is approvable within the threat model.

## Author's answers to round 1
- AI-B1 (a disabled ruleset still passed the approval check): fixed. `check()` fails when
  `enforcement` is not `active`; test V4 (`disabled`, `evaluate`); the fixtures carry
  `enforcement: active`; `AGENTS.md` row and Git rule updated.
- AI-B2 (D4 and D5 had no explicit manual check): fixed. Test plan M1 (outside the session `env`
  block, `gh` and git act as the owner) and M2 (empty bypass list, read with the owner's login, since
  the public API and the bot cannot see it); results under the plan's environment facts.
- Advisory, boolean or other non-integer counts: fixed (`true` is rejected; V1 covers `true` and
  `"1"`); a count on another rule type is pinned by V3.
- Advisory, validation results in the implementation log: fixed.
- Advisory and decision concern, "only the owner" overstated given two write collaborators: the
  `docs/STATUS.md` line now says the owner approves every merge; `AGENTS.md` states the rule (only the
  owner approves and merges). The collaborators were accepted by the owner (plan, last grill-me
  bullet; the owner says no one else works on the repository).

## Round 1 report (verbatim)

### Round 1

## Answers

Reviewer: Codex, independently reviewing commit `5b33b79` against `origin/main`, as requested. Review stayed read-only and offline; no Docker, services or credential contents were accessed.

1. **Plan:** Security scope is proportionate: delivery credentials remain outside the stack, holders are named, and owner-credential access is explicitly deferred. Combining plan and implementation is an approved exception. Test coverage is incomplete:

   | Decision | Coverage |
   | --- | --- |
   | D1 | Recorded bot-login probe; planned manual PR-author check. |
   | D2 | Recorded identity; branch commit author and committer match the approved bot identity. |
   | D3 | Recorded helper, token scopes and expiry; manual verification is reasonable for local configuration. Extra scopes are disclosed. |
   | D4 | Bot-session checks are planned, but no explicit check proves the owner’s terminal and clone identity remain the owner. |
   | D5 | Approval-count tests exist. Active enforcement and absence of bypass actors are not established by those tests; no explicit no-bypass manual check is recorded. |
   | D6 | The required Git rules are present and directly reviewable. |

   Thus, every decision is **not yet** tested or explicitly checked by hand with sufficient coverage. See AI-B1–AI-B2.

2. **Tests:** The following wrong implementations could still pass the added tests and changed positive fixtures:

   | Test/control | Wrong implementation still passing |
   | --- | --- |
   | `test_ruleset_without_a_required_approval_fails(None)` | Reading approval counts from any rule type; accepting non-integer counts; accepting missing `rules` as success. Those inputs are absent. |
   | Same test, count `0` | Checking count truthiness rather than a positive integer on a `pull_request` rule. |
   | `test_pull_request_rule_without_parameters_fails` | Rejecting absent parameters while accepting an empty parameter mapping or missing count; accepting counts on another rule type. |
   | `test_agreeing_lists_pass`, using the changed fixture | Accepting any positive count anywhere, or ignoring enforcement and bypass actors. |
   | `test_repository_table_and_workflow_agree_with_the_planned_required_checks`, using the changed fixture | The same approval errors; it uses constructed ruleset data, not the live configuration. |

   Other existing tests now receive an approval-bearing fixture but add no approval-specific discrimination.

   Actual code correctly rejects approval counts on another rule type, string counts, and missing `rules`. It accepts JSON `true` as count one because Python treats booleans as integers. None of the tests catches that.

   **Live read:** `make gate-consistency` calls the fixed public API URL for ruleset `26054924`, without authentication, matching the plan’s recorded source. It does not discover the effective rules for `main` or verify enforcement, branch applicability or bypass actors. Network restrictions prevented live confirmation.

3. **Consistency:** The status page, slice index, DPL-008 closure and plan agree about implementation status and automatic branch deletion. The Git rules and quality-gates row agree with the intended approval-count check, subject to AI-B1. Two qualifications remain:
   
   - “Only the owner can let a PR merge” overstates enforcement: the plan explicitly accepts two other collaborators whose approvals count.
   - The implementation log refers validation results to the PR rather than recording them locally, so those results cannot be assessed from this offline review.

4. **Keys:** No new exposure found. The diff changes no Compose mounts, Dockerfiles, service environment configuration, shared volumes or publication paths. Existing Dockerfile copies do not introduce the external bot credential directory. No credential value appears in the reviewed diff; `.claude/settings.local.json` is ignored. Local token contents and effective session settings were deliberately not inspected.

Validation: **12 non-writing test cases passed** by direct invocation. Three existing temporary-file cases were inspected but not run. In-memory probes confirmed the false greens below. Full tooling, live gate and E2E runs were not performed under the review restrictions.

## Blocking findings

- **AI-B1 — Disabled ruleset still produces an approval green.**  
  **Where:** `scripts/check_gate_consistency.py:96–107`; approval fixtures in `tests/tools/test_gate_consistency.py:44–50`.  
  **Criterion:** Concrete false green inside the honest-mistake threat model.  
  **Failure scenario:** An owner accidentally disables the ruleset while leaving its required checks and approval count intact. Supplying that response with `enforcement: "disabled"` returns `[]`. The gate reports that approval is required although this ruleset enforces none.  
  **Simplest fix:** Require active enforcement in the existing check, include it in positive fixtures, and add a disabled-enforcement negative control. This implements D5 without adding a gate.

- **AI-B2 — Approved local-configuration decisions lack explicit manual checks.**  
  **Where:** `docs/slices/agent-identity/plan.md:20–26,44,71–87`; `test_plan.md:32–35`.  
  **Criterion:** Approved decision without a test or explicit manual verification.  
  **Failure scenario:** The bot login and commit checks pass even if the owner’s ordinary terminal was also switched to the bot, or a bypass actor remains configured. Neither result proves D4’s session separation or D5’s no-bypass decision. An in-memory ruleset with a write-role bypass also passes the gate.  
  **Simplest fix:** Add and record secret-free manual checks for the owner-terminal/clone identity and the ruleset’s empty bypass list, with the stated reason that these are external configuration. No new automated mechanism is necessary.

## Advisory

- Add small negative controls for wrong-rule placement, missing count, non-integer count and missing `rules`. Reject booleans explicitly if validating integer shape; GitHub normally supplies an integer, so this alone is not blocking.
- Record validation commands and outcomes in the implementation log.
- Qualify owner-only enforcement claims with the already accepted collaborator exception.

## Simpler alternatives

Keep D1–D4 as local configuration with a short manual verification checklist. A GitHub App, credential-isolation mechanism or new CI job is unnecessary for this slice.

## Decision concerns

The retained collaborators mean GitHub enforces approval by an eligible non-author, rather than exclusively by the owner. The plan explicitly accepts this; changing that decision belongs to the user.

## Verdict

Approvable within the threat model: no — AI-B1, AI-B2.

## Round 2 report (verbatim)

### Round 2

## Answers

Reviewer: Codex, independently reviewing commits `5b33b79` and `34a285f` against `origin/main`. Review remained read-only and offline. No Docker, services, credential contents or environment variable values were accessed.

1. **Plan:** `plan.md` and `test_plan.md` adequately cover security, testing and consistency within the PoC threat model.

   | Decision | Verification |
   | --- | --- |
   | D1 machine user | Recorded login probe and manual M0. |
   | D2 identity | Recorded account details; both branch commits have the approved bot author and committer. |
   | D3 token and HTTPS helper | Recorded scope, expiry and helper probes; manual verification is appropriate for external configuration. |
   | D4 session separation | M1 and recorded owner-terminal results. |
   | D5 approval and no bypass | V1–V4, positive controls, recorded live run, and manual M2 for bypass actors. |
   | D6 Git rules | Direct inspection confirms the required instructions are present. |

   The external configuration results are recorded evidence, not independently refreshed during this offline review.

2. **Tests:** Each control has limits when considered alone:

   | New or changed control | Wrong implementation that would still pass it |
   | --- | --- |
   | V1: absent rule, zero, boolean or string count | Accepting fractional counts, counts on other rule types, or missing `rules` as success. |
   | V2: absent parameters | Rejecting absent parameters but accepting an empty mapping or a mapping without the count. |
   | V3: count on another rule type | Special-casing `deletion` while accepting counts from other unrelated rule types. |
   | V4: disabled/evaluate enforcement | Rejecting those two values but accepting missing or unknown enforcement. |
   | `test_agreeing_lists_pass` | Ignoring approval validation entirely or accepting any truthy count. |
   | Repository table/workflow positive control | The same approval errors; its ruleset is constructed, not fetched. |
   | Existing gate/job/target negative controls using the changed fixture | Ignoring approval and enforcement while retaining the existing list/command checks. |

   Collectively, the tests catch the intended regressions. Code inspection and additional in-memory probes confirmed rejection of missing/null `rules`, fractional/negative counts, empty parameters, missing count and missing enforcement.

   **Live read:** The Makefile supplies the public URL for ruleset `26054924`; the script reads it without authentication. This matches the plan. It checks that specific ruleset’s required checks, active enforcement and approval count; it does not discover effective branch rules or verify bypass actors. M2 explicitly covers bypass actors manually. No network request was made.

3. **Consistency:** The listed documents agree on bot identity, session configuration, approval checks, implementation status and DPL-008 closure. The implementation log records validation outcomes and explains omitted runtime testing. Its live results and automatic branch-deletion setting remain recorded claims in this review.

   The Git rules prescribe owner approval and merging. GitHub’s approval mechanism also accepts the two retained collaborators, as the plan explicitly acknowledges; owner exclusivity therefore remains a process rule under the accepted decision.

4. **Keys:** No new exposure found. The change adds no service mounts, Dockerfile copies, shared volumes, service environment configuration or credential publication paths. No credential value appears in the reviewed diff. The session settings file is ignored and untracked; the bot credential store remains outside the repository. Credential contents were not inspected.

Validation: **17 non-writing test cases passed**, plus the in-memory probes described above. Three existing temporary-file cases were inspected but not run. Full tooling, live gate and E2E runs were not performed.

## Blocking findings

None.

- **AI-B1 — Fix accepted.** Active enforcement is now required; V4 tests both `disabled` and `evaluate`.
- **AI-B2 — Fix accepted.** M1 and M2 explicitly cover session separation and no bypass, with reasons for manual verification and recorded results.

## Advisory

No new advisory findings in round 2.

## Simpler alternatives

None needed. The existing gate and short manual checklist remain proportionate.

## Decision concerns

The accepted collaborators can provide qualifying approvals. GitHub therefore enforces eligible non-author approval, while owner-only approval remains the repository’s operating rule. No change to that decision is proposed.

## Verdict

Approvable within the threat model: yes

## Reviewer prompt, round 1 (verbatim)

Round 2 used the same text with "round 2" in the heading, the commit range unchanged, and the author's
answers above appended.

````markdown
You are the independent reviewer for a change in the repository at the current working directory.
You did not write it. Review read-only: do not modify files, run docker, start services or use the
network. Never print key material, tokens or environment variable values.

## What is under review
Slice `agent-identity` (GitHub issue #20): the commits on the current branch against `origin/main`
(`git log origin/main..HEAD`, `git diff origin/main...HEAD`). The intent is the user's request to give
agents their own GitHub identity and require the owner's approval on `main`, with the decisions the
user approved now written in `docs/slices/agent-identity/plan.md` (plan and implementation are in one
PR by the user's decision). The bot account, its token and the session settings are local
configuration outside the repository; the plan's environment facts record the probes. Read
`AGENTS.md` first, in particular "PoC scope and proportion" (threat model, blocking criteria) and
"Independent review". You may read the whole repository.

## Questions (answer each; "n/a" needs a reason)
1. Plan: do `plan.md` and `test_plan.md` cover security, test adequacy and consistency under the
   PoC scope? Is every decision (D1–D6) either tested or explicitly checked by hand with a reason?
2. Tests: for each new or changed test in `tests/tools/test_gate_consistency.py`, which wrong
   implementation would still pass it (for example a ruleset with the approval in another rule type,
   a non-integer count, a missing `rules` entry read as success)? Does the live
   `make gate-consistency` read what the plan says it reads?
3. Consistency: do `AGENTS.md` (Git rules, quality-gates row), `docs/STATUS.md`,
   `docs/slices/README.md`, the implementation log, `docs/delivery_problem_log.md` (DPL-008) and the
   plan agree with each other and with the code?
4. Keys: does the change make a key, socket or secret reachable by a service outside its holders
   (compose mount, env var, Dockerfile `COPY`, script, shared volume), or put a credential into the
   repository, CI or evidence?

## Output (markdown only)
# Review — agent-identity, round 1
## Answers
## Blocking findings
(id AI-B1..., where, criterion, failure scenario, simplest fix) or "None".
## Advisory
## Simpler alternatives
## Decision concerns
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
````
