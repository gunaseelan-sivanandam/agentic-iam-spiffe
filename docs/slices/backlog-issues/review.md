# Independent review — backlog-issues

Reviewer: Codex (`codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral`), not the author, with
no network, so it read the six issue bodies from the prompt. Two rounds; round 2 is approvable within
the threat model.

## Author's answers to round 1
- BI-B1 (issue #14 overstated `qa-deploy` env checks): fixed in #14's body; only names matching
  `SECRET_ENV_RE` fail until registered.
- BI-B2 (slice index still said "slices 2–3 drafted"): fixed in `docs/slices/README.md`.
- BI-B3 (implementation log said no unit gates while `qa-quality` runs the unit guard check): fixed;
  the entry lists what `qa-quality` ran and what was not run.
- Advisories: #16 names the Increment 1C ideas as historical input and says the environment-facts
  collection script is not built; the plan says the pushed `later/gate-register` branch is deleted
  once the user agrees (local copy deleted).

## Round 1 report (verbatim)

### Round 1

## Answers

Reviewer: Codex, acting independently in the requested read-only, offline review. No files were modified, Docker or services started, or sensitive values printed.

Local `main` is stale (`b2448ad`); `HEAD` and `origin/main` are `aa1f0d4`, the PR #12 merge. I isolated the uncommitted slice against that commit.

1. **Completeness:** No content was dropped: the original `later_slices.md` remains verbatim beneath the freeze note.

   | Work | Destination |
   | --- | --- |
   | Gate register and D8 limitations | #13 |
   | Asset classification | #14 |
   | Coverage and covered-lines mutation decision | #15 |
   | Review design, orchestration, deferred lanes and carried findings | #16 and pinned drafts |
   | OPL-005 through OPL-008 isolation pilot | #17 |
   | Automatic branch deletion / DPL-008 | #18 |

   D20’s conditional ideas are explicitly left in the frozen record rather than made tasks. Older unapproved Increment 1C designs and test drafts also remain there; their disposition could be clearer, as noted below.

2. **Consistency:** Mostly, with the contradictions BI-B2 and BI-B3 below. Issue numbers match throughout, all 12 supplied pinned backlog anchors resolve at `aa1f0d4`, and slice 2’s implementation agrees with the merge history. DPL-008 correctly remains open pending the setting change. Issues track work while plans hold decisions and OPL/DPL files retain their authoritative records; that respects one home per fact.

   Live issue existence, labels and repository settings were not independently verified because network use was prohibited. Their stated state is taken from the supplied review input and recorded probes.

3. **False statements or public secrets:** Issue #14 overstates current environment-variable enforcement (BI-B1). I found no secrets, credentials or key material in the six supplied bodies. Descriptions of existing isolation problems already point to the repository’s public OPL records.

4. **New secret reachability:** No. The uncommitted change contains documentation only; it changes no mounts, environment configuration, images, entrypoints or runtime copying behavior.

Verification: `python3 -B scripts/check_docs.py` and `git diff --check` passed. I did not rerun `qa-quality`, which invokes tests and Docker inspection.

## Blocking findings

- **BI-B1 — Issue #14, Problem paragraph.**  
  **Criterion:** Contradiction with repository behavior.  
  **Failure scenario:** The body says a new “env var” fails until registered. [`_entry_errors`](/home/guna/projects/agentic_iam_spiffe/scripts/qa_deploy.py:250) checks only names matching `SECRET_ENV_RE`. An in-memory probe confirmed that adding an unregistered ordinary environment-variable name produces no allowlist error. A planner could therefore rely on completeness the current gate does not provide.  
  **Simplest fix:** Say “secret-pattern env var” and explicitly distinguish ordinary environment names.

- **BI-B2 — Slice index retains slice 2 as drafted.**  
  **Where:** [`docs/slices/README.md:18`](/home/guna/projects/agentic_iam_spiffe/docs/slices/README.md:18).  
  **Criterion:** Contradiction.  
  **Failure scenario:** The parent row says “slices 2–3 drafted,” while the adjacent row, STATUS and history correctly say slice 2 is implemented. Readers can mistake completed work for outstanding work—the ambiguity this migration should remove.  
  **Simplest fix:** Update the live index note to distinguish implemented slice 2 from proposed slice 3.

- **BI-B3 — Validation account contradicts the Makefile.**  
  **Where:** [`implementation_log.md:20`](/home/guna/projects/agentic_iam_spiffe/docs/history/implementation_log.md:20).  
  **Criterion:** Contradiction.  
  **Failure scenario:** The entry claims `make qa-quality` passed, then says “No tests … or unit gates.” [`qa-quality`](/home/guna/projects/agentic_iam_spiffe/Makefile:100) requires `unit-guard-check`, which runs pytest over `tests/unit`. The verification record consequently gives incompatible accounts of what ran.  
  **Simplest fix:** Distinguish “no new tests” and “no additional unit commands” from the tests included in `qa-quality`, using the actual execution record.

## Advisory

- Explicitly identify the older Increment 1C ideas retained only as historical input: gate-code mutation, check-removal mapping, escape-corpus checks, and automated plan/close-out validators. Preservation is complete, but their tracking status is less clear than the six principal items.
- The plan lists `later/gate-register` as deleted, but that local branch still exists. Clarify that deletion is pending if this is a retirement instruction.
- In #16, distinguish the environment-facts rule now in `AGENTS.md` from the earlier proposed collection script; the script is not implemented.

## Simpler alternatives

The six issues plus a frozen historical record are sufficient. No additional backlog document or issue-validation gate is needed.

## Decision concerns

None for the tracking decision. The mechanisms proposed in #13–#17 remain draft input and require their own reviewed plans.

## Verdict

Approvable within the threat model: no — BI-B1, BI-B2, BI-B3.
## Round 2 report (verbatim)

### Round 2

## Answers

Reviewer: Codex, acting independently as requested. Review remained read-only and offline; no Docker, services or sensitive values were accessed.

Local `main` remains at `b2448ad`; `HEAD` and `origin/main` are `aa1f0d4` (PR #12). I reviewed the uncommitted slice against `aa1f0d4`, separating it from already merged changes.

1. **Completeness: yes. Nothing was dropped.**

   | Work | Disposition |
   | --- | --- |
   | Gate register and D8 limitations | #13 |
   | Asset classification | #14 |
   | Coverage and covered-lines mutation decision | #15 |
   | Review design, orchestration, deferred lanes and carried slice-3 findings | #16 |
   | OPL-005 through OPL-008 isolation pilot and carried pilot findings | #17 |
   | Automatic branch deletion / DPL-008 | #18 |
   | Conditional D20 ideas and older Increment 1C designs/tests | Deliberately retained as historical input, explicitly identified in #16 |

   The original `later_slices.md` content is preserved exactly beneath the five-line freeze note.

2. **Consistency: yes, within the available offline evidence.** Issue numbers and destinations agree across the changed documents. All 14 unique pinned backlog anchors resolve at `aa1f0d4`. Slice 2 is consistently recorded as implemented; DPL-008 remains open pending automatic branch deletion. Issues track work, plans hold decisions, and OPL/DPL files retain their authoritative records.

   Round-1 answers accepted:
   
   - **BI-B1:** #14 now correctly limits environment-name enforcement to `SECRET_ENV_RE`, matching `_entry_errors`.
   - **BI-B2:** The slice-index parent row now distinguishes implemented slice 2 from draft slice 3.
   - **BI-B3:** The implementation log correctly lists `qa-quality` prerequisites, including the unit guard check, and distinguishes unchanged tests from commands not run.
   - **Historical 1C ideas:** #16 explicitly identifies them as historical input.
   - **Branch retirement:** The local `later/gate-register` branch is absent; the plan accurately leaves pushed-branch deletion pending user agreement.
   - **Environment facts:** #16 correctly distinguishes the existing rule from the unbuilt collection script.

3. **False repository claims or public secrets: none found in the supplied issue bodies.** Current repository claims checked against the Makefile, gate implementations, configuration records and OPL/DPL entries agree. The bodies contain planning text and resource names, without credentials or key material.

   Issue existence, labels, repository settings and historical measurements were not independently verified live; network access was prohibited. Issue numbering follows the supplied review input.

4. **New secret reachability: no.** This slice changes documentation only. It changes no runtime configuration, mounts, images, environment delivery or service access.

Verification: `python3 -B scripts/check_docs.py`, additional new-bundle link checks, frozen-record comparison, pinned-anchor checks and `git diff --check` passed. I did not rerun `qa-quality`, which invokes Docker and writes reports.

## Blocking findings

None. BI-B1, BI-B2 and BI-B3 are resolved.

## Advisory

All round-1 advisory answers are accepted. No new advisory findings.

## Simpler alternatives

The six issues and frozen historical record are sufficient; no additional backlog register or validation gate is needed.

## Decision concerns

None for this tracking change. The mechanisms proposed in #13–#17 remain draft input requiring their own reviewed plans.

## Verdict

Approvable within the threat model: yes
## Reviewer prompt, round 1 (verbatim)

Round 2 used the same text up to "## Issue bodies", then the author's answers above, the round 1 report and
the corrected issue bodies.

````markdown
You are the independent reviewer for a change in the repository at the current working directory.
You did not write it. Review read-only: do not modify files, run docker, start services or use the
network. Never print key material, tokens or environment variable values.

## What is under review
Slice `backlog-issues`: the uncommitted working-tree change against `main` (`git status`,
`git diff`, and the new directory `docs/slices/backlog-issues/`), plus six GitHub issues whose
bodies are reproduced below (they are not in the repository; the user creates them as #13 to #18 in
this order). The intent is the user's request: "This later slices list is growing, should we start
using github issues to reliably track the open tasks?", followed by approval of the proposal now
written in `docs/slices/backlog-issues/plan.md`. Read `AGENTS.md` first, in particular "PoC scope
and proportion" (threat model, blocking criteria) and "Independent review". You may read the whole
repository, including `git show aa1f0d4:docs/slices/agentic-delivery-process/later_slices.md`.

## Questions (answer each; "n/a" needs a reason)
1. Completeness: is every open item of `later_slices.md` either in one of the six issues or
   deliberately left in the frozen record? Name anything that was dropped.
2. Consistency: do `AGENTS.md`, `docs/STATUS.md`, `docs/slices/README.md`, the implementation log,
   the plan and the issue bodies agree with each other and with the repository (issue numbers,
   links and anchors, slice 2 status, DPL-008, the one-home-per-fact rule)?
3. Does any issue body state something false about the repository, or contain anything that must
   not be public (secrets, credentials)?
4. Does the change make a key, socket or secret reachable by a service outside its holders?

## Output (markdown only)
# Review — backlog-issues, round 1
## Answers
## Blocking findings
(id BI-B1..., where, criterion, failure scenario, simplest fix) or "None".
## Advisory
## Simpler alternatives
## Decision concerns
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".

## Issue bodies

### Issue #13 (gate)
```markdown
Draft input, not approved. When the slice starts, its grill-me uses this issue as input and the decisions go into the slice's `plan.md` (the independent reviewer reads the repository, not issues). Close this issue from the PR that completes the slice (`Closes #N`).

Proposed by the user in the `ci-evidence-trace` Increment B review (PR #12, merged 2026-10-31). It would replace slice 2's D8 gate-consistency check, which stays until then: the register replaces its input and undoes nothing.


**Problem.** `make gate-consistency` (D8) takes the `AGENTS.md` quality-gates table as the
authority, and only its rows enforced by CI. It compares them with the `ci.yml` jobs and the
`main` ruleset. It does not notice:

- a gate added only to the `Makefile` (a known limit of D8);
- local gates: step 4 requires `make e2e`, `make qa-evidence` and `make qa-quality`, but nothing
  checks that this list is complete;
- what an aggregate target runs: `qa-quality` and `unit-trust` members are not checked;
  `traceability-check` runs in `qa-quality` but has no row (an open decision of slice 2);
- targets that nothing uses: `unit-boundary` is in no aggregate target and has no CI job (its tests
  still run inside `unit-cov`).

The authority is prose parsed with a regex, any PR may edit it, and the naming rule (CI job = make
target) is stated only in the table's introduction. The `Makefile` has 23 targets today; none is
classified.

**Idea: a gate register with default deny,** the same pattern as `security/invariants.yaml` and
`make qa-deploy` for keys.

- **One machine-readable register** (for example `qa/gates.yaml`) lists every `Makefile` target with
  a role: CI gate (and whether it is a required check), local gate (required in step 4), member of
  an aggregate target, or helper (for example `unit-cov`, `print-publication-set`).
- **Closed world:** a target, CI job, required check or aggregate member that the register does not
  list fails. Nobody has to remember to add a gate; the author must choose its role.
- **`gate-consistency` checks** the `Makefile` targets and aggregate prerequisites, each `ci.yml` job
  and the command it runs, the ruleset's required checks, and the `AGENTS.md` table against the
  register (two sources kept equal, as register holders and the `REQ-SEC` `Holders:` lines are).
- **Naming convention:** keep "CI job = make target"; agree a convention for new gates in the
  grill-me. Renaming the existing targets is not needed, because default deny already catches a new
  one.
- **Changes need the user's approval.** GitHub cannot enforce this for one file with one account
  (`CODEOWNERS` review needs a second person, and an agent's `gh` login may be the owner's). Under
  the honest-mistake threat model: the register's header says it changes only through a plan the
  user approves; the `gate-consistency` job lists every register change in its output, so the change
  is visible in the PR's checks; the user's merge is the approval.

**Cost.** A new register file; `scripts/check_gate_consistency.py` extended to read the `Makefile`
and the register; a one-time classification of the 23 targets, proposed by the agent and approved by
the user. It changes slice 2's approved D8.

**Order with the 100% coverage slice.** The user runs 100% coverage as its own slice, which may
remove `unit-diff-cov`. If the register lands first, that removal is a visible, deliberate register
change.

**Decisions for its grill-me:** the register's file and format; the roles a target can have;
whether the `AGENTS.md` table is generated from the register or checked against it; the naming
convention for new gates; the fate of `traceability-check` (own row, or only a member of
`qa-quality`) and of `unit-boundary` (gate, member or removed); how a register change is shown in
CI.

```

### Issue #14 (asset)
```markdown
Draft input, not approved. When the slice starts, its grill-me uses this issue as input and the decisions go into the slice's `plan.md` (the independent reviewer reads the repository, not issues). Close this issue from the PR that completes the slice (`Closes #N`).

Drafted 2026-10-29 (moved here from `later_slices.md`). It would replace the smaller idea of requiring only every `secret_env` name to be an asset.

**Problem.** `qa-deploy` (1B) checks only the assets it is told about. A new service, mount, env var
or privilege fails until it is registered, but a brand-new asset (a new key, socket or credential
file in a new place) can be registered as an ordinary mount, and a secret env var can be registered
as plain `secret_env`, without anything requiring holders or a `REQ-SEC`. A secret whose name does
not match the secret pattern is not flagged at all. Recognising that something is an asset is left
to grill-me, the review and the user.

**Idea: classify everything that enters a container.** Unclassified fails, so nobody has to remember
to add an asset; the author must choose a class. Field practice: an asset inventory with information
classification (ISO 27001 asset inventory and classification, CIS Controls 1 and 3, FIPS 199 impact
levels).

- **Resources:** every mount source (path or socket), every env var name, every compose secret and
  config; later, shared state stores such as Redis.
- **Classes:**

  | Class | Means | Examples | Required controls |
  | --- | --- | --- | --- |
  | `public` | harmless if anyone reads it | capiss public key, OPA policy, Envoy config | none |
  | `internal` | not secret, not for outsiders | audit and log directories, mock data, URLs, `REDIS_URL` | per-service allowlist (as today) |
  | `restricted` | confidential or grants authority | private keys, tokens, join tokens, SPIRE admin socket, Docker socket, Workload API socket | holders and a `REQ-SEC` requirement, consistency checked (as today) |

- **Mechanical rules in `qa-deploy`:**
  - completeness: a resource without a class fails;
  - consistency: `restricted` without holders or a `REQ-SEC` fails; holders on a `public` resource
    are inconsistent;
  - plausibility (anti-downgrade): name heuristics (`*.key`, `*token*`, `*.sock`, `keys.json`,
    `*SECRET*`, the Docker socket) and, locally, content heuristics (PEM private-key headers) give a
    minimum class; declaring a lower class fails unless the entry carries a one-line reason. This
    is the OPL-005 pattern: a key directory thought of as "the public key".
- **Judgment by reviewers:** `qa-deploy` prints the resources added or reclassified by a change; that
  list is an environment fact for the plan reviewer and the security lens, who judge each class.
  Grill-me asks the author to classify what a slice will add.
- **What remains:** a confident misclassification of a file whose name and content look harmless.
  Under the honest-mistake threat model that is rare; forgetting, the common failure, is fully
  covered by completeness.

**Cost.** One-time classification of about 30 mount sources and 40 env names (most env vars are
`internal`), proposed by the agent and approved by the user; then one register line per new
resource. It changes the register's shape and `qa-deploy`'s rules.

**Decisions for its grill-me:** the classes and their names; what counts as a resource (are
networks and published ports resources, or stay allowlist facts?); the plausibility heuristics and
the downgrade-reason rule; whether content heuristics run only locally; how state stores are
classified and whether this slice or the pilot adds REQ-SEC-S1.

```

### Issue #15 (coverage)
```markdown
Draft input, not approved. When the slice starts, its grill-me uses this issue as input and the decisions go into the slice's `plan.md` (the independent reviewer reads the repository, not issues). Close this issue from the PR that completes the slice (`Closes #N`).

The user runs this slice (decided 2026-10-31, during `ci-evidence-trace`): raise the unit-test coverage rule from the current thresholds (total line ≥ 85%, branch ≥ 75% on capiss and tool-b, diff coverage ≥ 90%) to 100%.

**Analysis given on 2026-10-31 (re-measure first):**
- Coverage then: capiss 97.7% line / 94.7% branch (11 lines missing); tool-b 95.0% / 85.1% (13); `shared/enforcement_contract` 91.6% / 82.0% (8); jira-tool 87.0%; jira-mcp-gateway 72.9% / 58.2% (111 lines); total 86.7%.
- At 100% on the mutated files, mutmut's `mutate_only_covered_lines` no longer matters (closes the open mutation decision), and `unit-diff-cov` becomes redundant and can be removed.
- A threshold does not catch a gate that measures nothing (DPL-009): it needs a negative control for a missing file, and a ban on `# pragma: no cover` in measured files.

**Interactions:** slice 2 D8 gave `unit-diff-cov` its own CI job and required check; removing it changes the `AGENTS.md` gate table, `ci.yml` and the ruleset together. If the gate register (#13) lands first, the removal is a visible register change.
```

### Issue #16 (slice3)
```markdown
Draft input, not approved. When the slice starts, its grill-me uses this issue as input and the decisions go into the slice's `plan.md` (the independent reviewer reads the repository, not issues). Close this issue from the PR that completes the slice (`Closes #N`).

Slice 3 of `agentic-delivery-process`. Its drafts are long; they stay in the frozen `later_slices.md` record and are linked here at the commit where they were last edited.

**1. Review design (the grill-me starts here).** User, 2026-10-30: industry practice is for a reviewer to take the role that fits the artifact under review (requirements, architecture, security, tests, overall quality); it is not clear how three lenses or three agents map onto that. Start from this question, not from the three-lens draft.
- Inputs: [slice 2 grill-me outcome](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#slice-2-grill-me-outcome-2026-10-30), [review template](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#review-template-input-from-the-1a-review-discussion-2026-10-29), [review lenses and gates](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#review-lenses-and-gates-input-from-the-1b-review-discussion-2026-10-29), [review misses after 1B](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#review-misses-after-the-1b-review-input-2026-10-29).
- Of the six review-miss changes, 1 (no author scoping), 2 (environment facts) and 3 (gate–job–check consistency) are in place (`AGENTS.md` independent review and step 1; `make gate-consistency`); 4 to 6 (questions as the review, a usability and fit question, a budget for quality findings) are open.

**2. Orchestration.** `/deliver`, role subagents, phases, hooks, run state, credentials: [scope draft](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#scope-draft-was-increments-2-and-3), [pipeline credentials](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#pipeline-credentials), [process state](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#process-state-draft), [user actions](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#user-actions-draft), [pipeline self-tests](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#pipeline-self-test-drafts). Carried findings for slice 3 (PR-08/30, PR-14/29, PR-15/19, PR-24) with recommendations: [carried review findings](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#carried-review-findings).

**3. Lanes (deferred).** User decision: one process for every change for now; lanes return when automation makes small changes frequent. The user's gaps list for a future lane design is in the [slice 2 grill-me outcome](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#slice-2-grill-me-outcome-2026-10-30); the earlier draft is [Lanes (D9)](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#lanes-d9).

**Not tasks:** the [items deferred from slice 1](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#deferred-from-slice-1-d20-2026-10-29) are picked up only if a review or an escaped defect shows they are needed, and the user is asked first.

The pilot that fixes OPL-005 to OPL-008 is #17.
```

### Issue #17 (pilot)
```markdown
Draft input, not approved. When the slice starts, its grill-me uses this issue as input and the decisions go into the slice's `plan.md` (the independent reviewer reads the repository, not issues). Close this issue from the PR that completes the slice (`Closes #N`).

Fix the key and state isolation problems, the project's highest-priority open problems: [OPL-005](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/main/docs/open_problem_log.md) (capiss root signing key readable by verifiers, agent-a and rogue), OPL-006 (SPIRE agent key store readable by every workload), OPL-007 (unauthenticated writes to Redis authorization state), OPL-008 (spire-token-init mounts the whole SPIRE server data directory). The OPL entries in `docs/open_problem_log.md` stay the authoritative record; the register's `known_violations` rows and the `REQ-SEC-K1`, `K2`, `K4` statuses close with them.

Draft (2026-10-29): run `opl-005-006-007-isolation` as a full slice through the slice 3 pipeline (#16). Its content (public-key-only mounts, Workload-API-socket-only mounts, Redis ACLs, removal of the agent-a and rogue key mounts, `M2-T7` corrected to check the deployed rogue, and the Redis mechanism for REQ-SEC-S1, carried findings PR-25, PR-28, PR-09) is decided in its own grill-me. Draft: [pilot scope](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/aa1f0d4/docs/slices/agentic-delivery-process/later_slices.md#scope-draft-was-increments-2-and-3). Whether it waits for the pipeline is the user's call.
```

### Issue #18 (autodelete)
```markdown
Only the user can do this (repository settings).

Turn on **Settings → General → Pull Requests → "Automatically delete head branches"**. Then a merged PR's branch is deleted and GitHub retargets any PR stacked on it to `main`, which prevents [DPL-008](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/main/docs/delivery_problem_log.md) (a stacked PR merged into its stale base branch). Checked 2026-10-31: `deleteBranchOnMerge` is `false`.

When it is on, an agent closes DPL-008 in `docs/delivery_problem_log.md` and `docs/STATUS.md` in a PR that says `Closes #N`.
```
````
