# Plan review — ci-evidence-trace

Independent review of [`plan.md`](plan.md) and [`test_plan.md`](test_plan.md) before the user sees
them (`AGENTS.md`, Independent review). Reviewer: Codex (`codex exec -m gpt-6.1-sol --sandbox
read-only --ephemeral`), which never sees the author's reasoning. Review loop: no round limit;
each finding is answered as fixed or rejected with a reason.

## Round 1 (2026-10-30)
Reviewed files (SHA-256, at commit `4b6969e`):
- `plan.md` `198e24099f782ef08d0cfd5da00a2f751cc9634449a09b33ab48d24962277ef1`
- `test_plan.md` `576d9bf58e43a8723c802c81d3ab862b9b831fbec54b707f6f7135704f9d79fe`

Verdict: **no** — R1-B1 to R1-B6.

### Author answers, round 1
| Finding | Answer | Where |
| --- | --- | --- |
| R1-B1 job of a gate's name running another command | Fixed: each gate job must run `make <its name>`; V10 fixture `qa-deploy` running `make docs-check`. | plan D8, M5; test_plan V10 |
| R1-B2 raw base64 private key (`root_key.b64`) has no shape | Fixed, differently from the suggestion: a 44-character base64 rule would flag every hash, so the check also scans for the exact values (plain and base64) of the restricted assets the register lists, readable where it runs. The shape rule is fixed in the plan (run ≥ 200 characters with ≥ 20 distinct; measured: tokens ≥ 600, other evidence < 100, M5-T53 padding is one repeated character). | plan D3, M6, Known limits; test_plan V2 |
| R1-B3 only requirement gaps tested | Fixed: V9 adds one fixture per gap category. | plan D7; test_plan V9 |
| R1-B4 missing base read as push mode | Fixed: explicit `--mode pr --base` / `--mode push`; PR mode fails closed on an unresolvable or unreadable base; full history; merge-base fixture. | plan D7; test_plan V9 |
| R1-B5 skipped image inspection proving D2 | Fixed: the report records whether image users were inspected; D2 `not_checked` when skipped; `qa-evidence` accepts only a complete report; the `qa-deploy` job's report is not evidence. | plan D5; test_plan V5, V6 |
| R1-B6 M8 overclaims (Dockerfile bases float) | Fixed by narrowing M8 to the two compose images the user chose to pin; base images listed under Known limits as not decided. | plan M8, Known limits; test_plan V3 |
| R1-A2 report schema | Taken: malformed, missing requirement, unknown status fixtures. | test_plan V6 |
| R1-A3 parent `artifacts/` ownership | Taken. | test_plan V1 |
| R1-A4 upload only after the secret check; no value in diagnostics | Taken. | plan D3; test_plan V2 |
| R1-A6 OPL-009 mitigation text | Taken (Increment B). | plan In scope B |
| R1-A7 ARCH-007/018/019 are scripts, not configuration | Taken: D6 covers files without DD-tagged functions; each of the 13 is reviewed, any left stays a gap. | plan D6, success criterion 5 |
| R1-A8 name the job | Taken: `gate-consistency`. | plan D8 |
| R1-A9 synthetic fixtures | Taken. | test_plan Assumptions |
| R1-A10 scanner contract documented with A | Taken: `AGENTS.md` gate row of `qa-evidence` in A. | plan In scope A |
| R1-A13 assets wording | Taken. | plan Assets and holders |
| R1-A14 gap swap | Taken. | test_plan V9 |
| R1-A1 workflow failure-propagation test | Rejected: CI steps run with `bash -e` and the job's conclusion is the result (M10); the implementation review reads the workflow. A test of GitHub's step semantics adds a fixture without catching a mistake the review misses. | — |
| R1-A5 documentary check for D9 | Rejected: `docs-check` cannot judge rule text; the implementation review checks the `AGENTS.md` diff against D9. | — |
| R1-A11 rollback note | Rejected: each increment reverts with `git revert`; the only external step (required checks) is listed in the review notes. | — |
| R1-A12 enumerate harness IDs in A's PR | Already planned (test_plan, E2E test plan); no change. | — |

### Round 1 prompt (verbatim)
````markdown
You are the independent plan reviewer for a slice plan in the repository at the current working
directory. You did not write it. Review read-only: do not modify files, run docker, start services
or use the network. Never print key material, tokens or environment variable values.

## What is under review
The slice plan `docs/slices/ci-evidence-trace/plan.md` and its test plan
`docs/slices/ci-evidence-trace/test_plan.md` (commit `HEAD`; `git show HEAD` shows everything this
commit changes). They are the plan for slice 2 of the agentic-delivery-process programme. The user
has not seen them yet; your review comes first.

The intent they must serve: the user's decisions from the slice's grill-me, recorded in the plan's
decision table (D1–D11), and the repository's rules in `AGENTS.md`. Earlier input for this slice is
`docs/slices/agentic-delivery-process/later_slices.md`; the plan says which parts of it were moved
to slice 3, and that move is a user decision.

You may read the whole repository. Decide yourself where to look; you are not given a list of files.

## How to judge
Read `AGENTS.md` first, in particular "PoC scope and proportion" (threat model, blocking criteria,
review loop) and "Slice workflow". Then read the plan's section "Threat model for this plan and its
reviews": it is the threat model you judge against. A finding blocks only if it meets the blocking
criteria there, with a concrete failure scenario. Everything else is advisory.

## Environment facts (collected by the author on 2026-10-30; facts outside the repository)
- The `main` ruleset `basic` requires these status checks: docs-check, qa-trace, unit-guard-check,
  tooling-test, test-lint, qa-deploy, unit-mutation, unit-trust; strict; 0 approving reviews.
- Latest CI runs: `CI` on push to `main` at `62d6b0c` (PR #7 merge): success. `E2E trial` (a
  throwaway workflow on branch `ci-trial/e2e`, since deleted): run `40999541906` failure (both jobs:
  the suite passed 120/120, then `make qa-evidence` failed with PermissionError on the root-owned
  `artifacts/` directory); run `41000278717` success after adding `sudo chown` of `artifacts/` and
  `test_report.log` before `qa-evidence` (both jobs: build 15–18 s, suite 177–188 s, 120/120 passed,
  `qa-evidence` PASSED, validated 119, skipped 1 for M5-T55). The trial uploaded evidence as public
  artifacts; it contains expired capability tokens.
- The ruleset can be read without authentication from the public GitHub API
  (`GET /repos/{owner}/{repo}/rulesets/{id}` returned HTTP 200 unauthenticated).
- `make qa-trace` on `main` today: coverage gaps 138 (requirements_without_e2e 97,
  architecture_without_dd 13, dd_without_ut 24, e2e_tests_without_requirements 4).
- `make qa-deploy` with image inspection on the local stack: PASSED (18 known violations, 22 warnings,
  all 22 "grandfathered until 2027-01-31").
- PR #8 (open, docs only) removes the review round limit; this branch is based on it, so `AGENTS.md`
  here already contains the review loop the user decided.

## Questions (answer each in depth; "n/a" needs a reason)
1. Intent: do the plan and test plan do what the decisions say, no more and no less? Is any decision
   missing, contradicted or quietly widened?
2. Claims and evidence: for each claim (success criteria, threat-model rows M1–M10, the "caught by"
   column, requirement proofs), what in the test plan proves it? Could that proof pass while the
   claim is false? Is each requirement verifiable and unambiguous?
3. Design and quality: is each mechanism the simplest that fits? Consistent with how the repository
   already does similar things? Are names, placement and structure what a newcomer would expect, and
   will the user be able to see what ran and what failed?
4. Failure and change: behaviour when an input is missing, malformed or unreadable (ruleset API,
   reports, base commit, evidence); fails closed? Ordering between the two increments; can each be
   rolled back?
5. Rules and new risks: does it keep every rule in `AGENTS.md`, the requirements, the register and
   the open problems? Does it add an asset, trust boundary, data flow or rule without registering it?
6. Ripple: what depends on what changes (CI, Makefile, `docs-check`, `qa-trace`, `qa-evidence`,
   `test_spec.md`, the harness, the register, other slices), and does the plan account for it?
7. Durability: does anything decided live only somewhere temporary? Where must it live?
8. Blind spots: what did you not check, and could it matter?

## Output (markdown only)
# Plan review — ci-evidence-trace, round 1
## Answers
(one section per question above)
## Blocking findings
Each with id (R1-B1, R1-B2, ...), where (file:line), the blocking criterion it meets, failure
scenario, smallest fix. "None" if none.
## Advisory
Each with id (R1-A1, ...), one or two lines. No limit, but list each point once.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
## Not checked
````

### Round 1 report (verbatim)
````markdown
# Plan review — ci-evidence-trace, round 1

## Answers

Reviewer: **Codex**, acting independently in the supplied read-only environment, as required by `AGENTS.md`. Reviewed commit `4b6969e184e199651b5c2e222cd6b1bc8ffacb60`; the reviewed files match `HEAD`.

### 1. Intent

The plan largely preserves D1–D11 and keeps the slice proportionate. It adds CI evidence, repairs evidence disclosure, and extends existing trace tooling rather than introducing the heavier delivery machinery from the earlier draft.

| Decisions | Assessment |
| --- | --- |
| D1 | The required `e2e` job, image inspection, evidence validation, retention, and continued local clean-stack run are represented. V1 tests target failure propagation; implementation-PR CI verification covers the successful job path. |
| D2 | The scope consistently names the two direct compose images, OPA and Redis. M8 nevertheless promises protection against floating image tags generally; Dockerfile base images still float. **R1-B6.** |
| D3 | Scratch hand-offs, fingerprints, redacted mint JSON, evidence scanning, and spec updates are represented. V2 omits the repository’s actual raw private-key encoding. **R1-B2.** |
| D4–D5 | Static entries, specification entries, gate implementations, negative controls, and stored reports form a reasonable trace chain. The distinction between a partial deployment check and authoritative proof is missing. **R1-B5.** |
| D6 | File-backed implementation declarations and retirement are covered by V8 and V11. Some of the thirteen currently uncovered ARCH sections describe executable harness or agent behavior, so calling all thirteen “config-implemented” is misleading. |
| D7 | The intended comparison is clear: fail on individual new gaps, preserve old gaps, permit expiring acceptances. V9 does not test new ARCH/DD gaps or the missing-base PR path. **R1-B3, R1-B4.** |
| D8 | The three-list comparison and separate `unit-diff-cov` job are represented. Name agreement does not prove a job executes its named gate. **R1-B1.** |
| D9 | The exact rulebook replacement is stated. Its verification should be an explicit documentary acceptance check. |
| D10 | The move to slice 3 is respected. `later_slices.md` records the user’s questions and lane constraints; this slice does not silently adopt its older lane or three-lens designs. |
| D11 | A precedes B, and the secret check lands before CI publication. Deferring `EVID-T1` and REQ-T-R9 until the static-entry mechanism exists in B is explicit and coherent. |

I found no justification to revive the deferred runner isolation, provenance, lane classification, or review orchestration work. Those would exceed the approved scope.

### 2. Claims and evidence

The test plan provides useful negative controls, but several claims remain broader than their proof.

**Success criteria**

| Criterion | Planned proof | Could that proof pass while the claim is false? |
| --- | --- | --- |
| 1: required CI E2E, 120 tests, deployment inspection and evidence validation | V1; full local run; implementation-PR `e2e` job; ruleset update and V10 | V1 alone proves neither workflow triggers nor execution of all three commands. Successful CI verification must inspect those facts, including the 119 validated / 1 skipped distinction. |
| 2: evidence contains no token or private key | V2 plus the full run after the harness changes | Yes: V2 covers long token-shaped strings and PEM keys, but not the issuer’s raw Base64 private-key file. **R1-B2.** |
| 3: honest per-requirement static status | V5 and V7, with V6 validating the report | Yes: a partial `--skip-image-users` report can match both digests without proving D2. **R1-B5.** |
| 4: new gaps fail; valid acceptances pass; expired/stale acceptances fail | V9 and V12 | Good requirement-gap and expiry coverage. ARCH/DD additions and unavailable PR bases remain untested. **R1-B3, R1-B4.** |
| 5: implementation declarations and retirement | V8 and V11; merged-result verification | Adequate for file existence and retirement. File existence establishes a declared implementation location, not behavioral correctness; the plan should retain that distinction. |
| 6: three gate lists agree | V10 and live implementation-PR verification | Adequate for the listed name discrepancies, insufficient for the additional M5 promise about what jobs execute. **R1-B1.** |

**Threat-model rows and their “caught by” claims**

| Row | Proof in the test plan | Assessment |
| --- | --- | --- |
| M1 | V9, V12; V8 for absent implementation declarations | Requirement additions are covered. New ARCH and DD gaps need their own negative controls. |
| M2 | V9: reason/expiry validation, boundary clock, stale acceptance | Substantially covered. Keep the distinction between “valid through the expiry date” and expired precise, as the test plan does. |
| M3 | V5 status production and V7 trace interpretation | The known-violation path is covered. Partial-check reports must not become complete proof. |
| M4 | V6: missing report and compose/register digest mismatches | Covers the specifically promised file mismatches. Malformed, incomplete, and partial reports have no rejection fixtures. |
| M5 | V10 | Covers names, not execution under those names. **R1-B1.** |
| M6 | V2 plus harness changes and a full run | Good coverage of the original token leak; insufficient coverage of the private-key claim. **R1-B2.** |
| M7 | Live required-check configuration and successful implementation-PR runs | Primarily an operational acceptance check, not a tooling-unit test. Verify the job actually runs on PRs and pushes and that required-check configuration is active. |
| M8 | V3 | Covers OPA/Redis tag agreement and a compose/register mismatch. It cannot establish the broader image-consistency claim. **R1-B6.** |
| M9 | V8 | Directly covered by existing-file and missing-file controls. |
| M10 | V1 and successful CI execution | V1 covers a failed harness target. It does not exercise a failed deployment or evidence step in the workflow; add those to the workflow acceptance checks. |

**Requirement proofs**

- **REQ-T-R9:** Its intended property is clear, but “credentials” is broader than V2’s finite pattern list. At minimum, the approved detection contract must cover the repository’s actual secret formats. Threshold-boundary tests prove consistency with a threshold; they do not establish that the threshold catches those secrets.
- **REQ-SEC-K1–K8:** The existing gate has reusable negative controls for parent-directory mounts, environment grants, container-path mounts, holder consistency, and accepted violations. The proposed individual `DEPLOY-K*` entries should name the relevant selectors rather than merely the whole test file. K1, K2 and K4 must remain explicitly unproved under their current known violations.
- **REQ-SEC-D1:** Existing default-deny fixtures cover the registered deployment facts, including profiles, mount modes, privileges and secret environment names. Reusing these is proportionate.
- **REQ-SEC-D2:** Existing tests cover effective-user precedence, unknown users, forbidden root, grandfathering, and expiry. The new report must preserve the distinction between an inspected user and an inspection that was skipped. **R1-B5.**
- **REQ-M4B-W8 and REQ-M5-CJ2:** Their evidence clauses remain in force. Updating token storage and checking the resulting evidence addresses the admitted false green without weakening those clauses.

The test plan’s assertion that every tooling check has a negative control is therefore premature.

### 3. Design and quality

The main mechanisms fit the repository:

- `make e2e` gives the workflow and local operator a recognizable entry point.
- QA tooling tests belong in `tests/tools/`.
- Extending `trace/tests.yaml` and `docs/test_spec.md` preserves one home per trace mapping and specification.
- Per-requirement results make accepted violations visible without changing the existing deployment gate’s verdict.
- File-backed ARCH declarations are simpler than manufacturing DD tags for configuration.
- Comparing individual gap identities is more useful than comparing aggregate counts.

The user should be able to see which gate failed through the separate CI job names. Reports should also distinguish **mapped**, **proved**, **known violation**, **grace**, and unavailable evidence where applicable; “PASSED” for a structural trace check must not imply every requirement holds.

Two design details need clarification before implementation:

1. The report flow between independent CI jobs and local make targets is unspecified. Today, `qa-trace` runs independently, and `qa-quality` lists it before `qa-deploy`.
2. The gate-consistency job needs a concrete name and a checked relationship to its executed make target. Comparing labels alone reproduces the mistake M5 describes.

No additional production-hardening machinery is warranted.

### 4. Failure and change

The plan explicitly fails closed on an unreadable ruleset, a missing deployment report, and mismatched compose/register digests. It also specifies useful date-boundary behavior for accepted gaps and non-root grace.

Important missing cases are:

- **PR base unavailable:** V9’s “no PR base” push case must not become the fallback for an actual PR whose fetch or merge-base resolution failed. **R1-B4.**
- **Partial deployment evidence:** A parseable report with matching digests can still omit image inspection. **R1-B5.**
- **Malformed/incomplete reports:** No fixture requires rejection of missing requirement results, unknown statuses, or malformed report data.
- **Unreadable evidence:** The scanner must fail, not silently skip a file it cannot read. This is an implementation acceptance detail worth stating.
- **Tooling failures after E2E:** V1 does not establish propagation of `qa-deploy` and `qa-evidence` failures through the actual job.

A-before-B is the correct order. Within A, publication must remain downstream of successful secret validation; moving the files and adding the scanner in the same PR makes that reviewable.

Rollback needs an operational note:

- Reverting B while retaining A is feasible, but required checks and static trace/schema changes must be reverted together.
- Reverting A after B requires first removing B’s dependencies on A’s secret check and evidence path.
- A rollback must disable publication before restoring the old token-writing harness.
- Required-check names cannot be left pointing at removed jobs, or subsequent PRs will be blocked.

These are coordination details, not reasons to introduce a migration framework.

### 5. Rules and new risks

The plan follows the repository’s PoC threat model and retains the required local E2E run. It documents the new process state and avoids pretending to fix OPL-005 through OPL-008.

The Docker socket remains with an existing declared holder. Moving token hand-offs into harness-local scratch does not inherently widen service access. The actual scratch path and upload paths still need review to confirm that statement.

The plan identifies the new artifact flow, retention period, ruleset dependency, and accepted-gap state. No new service or holder is proposed. The phrase “none added or moved” in the assets section should nevertheless acknowledge that bearer-token storage moves to scratch.

Two standing-rule issues deserve attention:

- The claim of private-key-free evidence lacks a negative control for the actual issuer-key encoding. **R1-B2.**
- D9 changes the universal workflow rule, but its test plan has no explicit documentary check that the old scope restriction is removed.

`OPL-009` still describes a nightly full-suite rerun as a slice-2 mitigation. This plan promises PR and push runs, not nightly runs. Update the live OPL mitigation to the approved mechanism; do not import the old nightly design by implication.

The existing source/register limitations of static deployment checking remain accepted. This slice should not represent a static proof as proof against runtime key copying.

### 6. Ripple

The plan accounts for most direct dependencies:

| Changed area | Dependents accounted for |
| --- | --- |
| Harness evidence layout | Scratch readers, fingerprints, mint JSON, evidence lists in `test_spec.md` |
| New static trace entries | Trace parser, specification headings, `docs-check`, retirement of `IT-DEPLOY-*` |
| Deployment report | `qa-deploy`, `qa-evidence`, `qa-trace`, uploaded quality evidence |
| Image tags | Compose and register |
| New gates/jobs | Makefile, workflow, `AGENTS.md`, external required checks |
| Universal slice workflow | `AGENTS.md` |
| Deferred work | Recorded user input in `later_slices.md` |

The largest unresolved dependency is **report production before consumption**. The present CI jobs do not share a workspace, and the present `qa-quality` dependency list does not establish the new report ordering. A clean-checkout verification must exercise the intended arrangement.

The gap comparison also needs enough Git history and explicit PR context. The current `qa-trace` checkout does not request full history.

The harness change inventory is deferred to A’s PR. That is workable for evidence-only edits, but the PR must enumerate every affected harness ID and its spec update so reviewers can verify that no premise, exercise, or outcome changed.

Retirement should check references beyond the trace file, including generated design/report consumers and live prose. Existing unit traceability does not appear to depend on DD-925–DD-930.

### 7. Durability

Most decisions have suitable durable homes:

- Workflow rules and gate contracts: `AGENTS.md`.
- Requirement and architecture changes: their authoritative documents.
- Static mappings and accepted gaps: `trace/tests.yaml`.
- Test behavior and evidence descriptions: `docs/test_spec.md`.
- Image approval: compose plus the deployment register.
- Deferred user input: the explicitly draft `later_slices.md`.

The trial workflow and its artifacts are temporary. They must not be the only source for fixture data, secret-scanner positive controls, or the root-ownership regression. Preserve synthetic or sanitized fixtures in the tooling tests; preserve the observed trial results in the implementation record.

The scanner threshold is said to be fixed in A and documented under `EVID-T1`, but that entry lands only in B. A needs a durable description of its scanner contract when it merges.

The independent review record must preserve this report, the reviewed hashes, and separate author responses. The reviewed SHA-256 values are:

| File | SHA-256 |
| --- | --- |
| `plan.md` | `198e24099f782ef08d0cfd5da00a2f751cc9634449a09b33ab48d24962277ef1` |
| `test_plan.md` | `576d9bf58e43a8723c802c81d3ab862b9b831fbec54b707f6f7135704f9d79fe` |

### 8. Blind spots

This is a plan review, not implementation verification. I checked the existing workflow, make targets, trace and evidence validators, deployment gate and its tooling tests, relevant requirements and architecture, register, harness evidence mechanisms, slice templates, open problems, and deferred-slice input.

I ran only the read-only documentation validator: `python3 -B scripts/check_docs.py` **passed**.

The external environment facts were accepted as supplied. Their implementation-time verification matters because required-check configuration, API availability, trial artifacts, and selected image versions can change. The detailed exclusions are listed under **Not checked**.

## Blocking findings

### R1-B1 — Gate-name agreement does not catch execution under the wrong name

**Where:** [plan.md:41](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:41), [plan.md:87](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:87), [test_plan.md:69](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/test_plan.md:69).

**Criterion:** Concrete M5 false green; the stated “caught by” mechanism lacks the necessary test.

**Failure scenario:** An honest workflow edit leaves a job named `qa-deploy` but changes its command to `make docs-check`. The rulebook, job names, and required-check names still agree. Every listed V10 fixture can pass while gate consistency misses the incorrect execution.

**Smallest fix:** Extend the existing consistency check and V10 to verify each gate job invokes its designated make target. Include a same-name/wrong-command negative fixture.

### R1-B2 — The evidence-secret tests omit the repository’s private-key format

**Where:** [plan.md:93](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:93), [test_plan.md:27](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/test_plan.md:27).

**Criterion:** Concrete M6 false green and insufficient proof of REQ-T-R9.

**Failure scenario:** A diagnostic change copies the issuer’s `root_key.b64` into evidence. The issuer writes a raw Base64 Ed25519 private key, not PEM (`services/capability-issuer/app.py:157`). A scanner detecting PEM and long capability-token strings can pass every V2 fixture while accepting this shorter raw key.

**Smallest fix:** Define coverage for the repository’s actual private-key encoding and add a synthetic negative fixture in that format. Establish the detection contract before using implementation-selected thresholds as the expected result.

### R1-B3 — New ARCH and DD gaps have no negative controls

**Where:** [plan.md:37](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:37), [test_plan.md:59](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/test_plan.md:59).

**Criterion:** Approved D7/M1 behavior without a test.

**Failure scenario:** The gap comparison considers only requirement gaps. A PR adds an ARCH section without implementation, or a valid DD without a covering UT. V9 and V12 still pass because their additions concern requirements; V8 only establishes that the ARCH remains a gap.

**Smallest fix:** Parameterize V9 over requirement, ARCH, and DD additions and assert that each new gap fails the PR comparison.

### R1-B4 — Missing PR-base evidence can be mistaken for report-only push mode

**Where:** [plan.md:86](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:86), [test_plan.md:68](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/test_plan.md:68).

**Criterion:** Concrete M1 false-green path left untested.

**Failure scenario:** The PR checkout lacks the base history—consistent with today’s shallow `qa-trace` checkout—or fetching it fails. Code treats “no base” as push mode and passes a PR adding an unproved requirement. The existing base/head fixtures and the successful no-base push fixture do not catch this integration error.

**Smallest fix:** Specify explicit PR/push mode, fetch sufficient history, and require PR mode to fail when base resolution or base-input loading fails. Add that negative control and a diverged-history merge-base fixture.

### R1-B5 — A partial deployment report can be accepted as complete static proof

**Where:** [plan.md:84](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:84), [plan.md:176](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:176), [test_plan.md:51](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/test_plan.md:51).

**Criterion:** Contradiction with REQ-SEC-D2 and D4’s checked-result requirement; a matching report is not necessarily sufficient proof.

**Failure scenario:** `qa-deploy --skip-image-users` produces a report. The existing implementation skips unknown image users in that mode; this compose declares no explicit service users. Both file digests match, satisfying V6, but interpreting “no root error” as `holds` falsely proves D2 without inspecting any image users.

**Smallest fix:** Require the report to identify inspection completeness. Partial results must not prove D2 or satisfy complete static-evidence validation. Add a matching-digests/inspection-skipped negative fixture and define the producer-before-consumer flow for clean CI and local runs.

### R1-B6 — M8 promises more image consistency than D2 provides

**Where:** [plan.md:44](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:44), [plan.md:81](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/plan.md:81), [test_plan.md:37](/home/guna/projects/agentic_iam_spiffe/docs/slices/ci-evidence-trace/test_plan.md:37).

**Criterion:** Concrete M8 false green and contradiction between the claim and approved mechanism.

**Failure scenario:** CI pulls a newer `python:3.11-slim` base while a local rebuild uses a cached older base. Both OPA and Redis tags match the register, so V3 passes while CI and local images differ because a version tag floats. Several Dockerfiles also use `alpine:3.19`.

**Smallest fix:** Narrow M8 to the two direct compose-image tags covered by D2. Broader base-image pinning would require an explicit scope decision; digest pinning remains out of scope.

## Advisory

- **R1-A1:** Add a workflow acceptance check that independently fails the deployment and evidence steps and confirms the `e2e` job fails. V1 covers only harness failure.
- **R1-A2:** Extend report fixtures to reject malformed JSON, missing requirement results, unknown statuses, and unreadable inputs; matching digests alone establish neither schema nor completeness.
- **R1-A3:** V1 should reproduce ownership of the parent `artifacts/` directory and creation of `artifacts/quality/`, where the supplied trial failed.
- **R1-A4:** State exact upload paths, require successful secret validation before publication, and ensure scanner diagnostics do not reproduce detected secret values.
- **R1-A5:** Add an explicit documentary acceptance check for D9’s rulebook replacement.
- **R1-A6:** Update OPL-009’s live mitigation text: its nightly-run statement does not describe the approved PR/push design.
- **R1-A7:** Describe the thirteen ARCH gaps accurately; ARCH-007, ARCH-018 and ARCH-019 include executable harness/agent behavior, not solely configuration.
- **R1-A8:** Give the gate-consistency job its final name so the rulebook and external required-check update are unambiguous.
- **R1-A9:** Preserve synthetic/sanitized trial-derived fixtures in the repository; temporary public artifacts must not become test dependencies.
- **R1-A10:** Document A’s scanner contract when A merges; its description cannot depend solely on B’s later `EVID-T1` entry.
- **R1-A11:** Add a short coordinated rollback note covering required checks, B’s dependency on A, and disabling uploads before restoring old evidence behavior.
- **R1-A12:** Enumerate affected harness IDs in A’s PR and review each corresponding evidence-spec update.
- **R1-A13:** Correct “none added or moved” in the asset section to acknowledge token storage moving into harness-local scratch.
- **R1-A14:** Include a gap-swap fixture: close one old gap and add a different gap, leaving the total unchanged. The new gap must still fail.

## Verdict

Approvable within the threat model: **no — R1-B1, R1-B2, R1-B3, R1-B4, R1-B5, R1-B6**.

## Not checked

- No Docker commands, services, network requests, or filesystem modifications.
- No live ruleset/API verification, CI rerun, or artifact download; external facts were accepted as supplied.
- No E2E, deployment, tooling, unit, or historical-replay execution. Some existing tooling tests invoke Docker, and the proposed mechanisms are not implemented yet.
- No secret-bearing files or runtime environment values inspected.
- No independent reconstruction of the grill-me conversation; D1–D11 were treated as the authoritative decisions.
- No exhaustive service-code security audit. Existing runtime vulnerabilities remain governed by their requirements and open problems.````
