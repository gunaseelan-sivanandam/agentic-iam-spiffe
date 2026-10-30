# Plan review — ci-evidence-trace

Independent review of [`plan.md`](plan.md) and [`test_plan.md`](test_plan.md) before the user sees
them (`AGENTS.md`, Independent review). Reviewer: Codex (`codex exec -m gpt-6.1-sol --sandbox
read-only --ephemeral`), which never sees the author's reasoning. Review loop: no round limit;
each finding is answered as fixed or rejected with a reason.

**Outcome:** approvable within the threat model after 3 rounds (2026-10-30). 7 blocking findings,
all fixed; 14 advisories: 10 taken, 3 rejections accepted by the reviewer, 1 already planned.

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

## Round 2 (2026-10-30)
Reviewed files (SHA-256, at commit `b1879e0`):
- `plan.md` `d71716fdfc340f6c3be5c80a97aff16b5da9e509d7a97db6d87abf7c1a7a2ccd`
- `test_plan.md` `70c550f2c1e7fb3e34829677e49921de8512ea3347ae3f1687a374c9ff4c11f0`

Verdict: **no** — R1-B5 (partly fixed), R2-B1. Rejections of R1-A1, R1-A5, R1-A11 accepted.

### Author answers, round 2
| Finding | Answer | Where |
| --- | --- | --- |
| R1-B5 how `qa-trace` gets static results in a clean checkout | Fixed: `qa-trace` never reads a run report. A static link counts as proof structurally (as an E2E link does), and the status comes from the register: a `known_violations` row gives "not proved: known violation OPL-xxx", D2 within its grace date "not proved: grace"; both are gaps. `qa-evidence` checks that the run's report agrees with the register. Clean-checkout fixture added. | plan D5, success criterion 3; test_plan V6, V7 |
| R2-B1 Makefile-only gate not observable | Fixed by narrowing M5 to the `AGENTS.md` CI table, as suggested. A wider rule (every `qa-quality` prerequisite has a row) is listed under Known limits: it would flag `traceability-check` at once and needs its own decision. | plan M5, Known limits |
| R1-A2 unreadable report | Taken. | test_plan V6 |
| R1-A4 exact upload paths | Taken. | plan D1 |
| (author) gap identity across categories | Added: both sides computed by the PR's `qa-trace` on a merge-base checkout; a gap is identified by kind and ID, so recategorised old gaps do not look new. | plan D7; test_plan V9 |

### Round 2 prompt (verbatim)
````markdown
You are the independent plan reviewer for a slice plan in the repository at the current working
directory. You did not write it. Review read-only: do not modify files, run docker, start services
or use the network. Never print key material, tokens or environment variable values.

## What is under review
The slice plan `docs/slices/ci-evidence-trace/plan.md` and its test plan
`docs/slices/ci-evidence-trace/test_plan.md` (commit `HEAD`; `git log -3` and `git diff HEAD~2` show the plan commit and the round-1 changes). They are the plan for slice 2 of the agentic-delivery-process programme. The user
has not seen them yet; your review comes first.

The intent they must serve: the user's decisions from the slice's grill-me, recorded in the plan's
decision table (D1–D11), and the repository's rules in `AGENTS.md`. Earlier input for this slice is
`docs/slices/agentic-delivery-process/later_slices.md`; the plan says which parts of it were moved
to slice 3, and that move is a user decision.

You may read the whole repository. Decide yourself where to look; you are not given a list of files.

## This is round 2
Round 1's prompt, report and the author's answers are in
`docs/slices/ci-evidence-trace/plan_review.md`. For each round-1 finding: say whether the fix is
correct and complete; for each rejected finding, accept the rejection or re-raise it with new
evidence. From this round, a new finding counts only if it meets the blocking criteria; do not add
advisories that are not new.

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
# Plan review — ci-evidence-trace, round 2
## Round-1 findings
(one line per finding: fixed / not fixed, or rejection accepted / re-raised, with the reason)
## Answers
(one section per question above; brief where nothing changed since round 1)
## Blocking findings
New only, each with id (R2-B1, ...), where (file:line), the blocking criterion it meets, failure
scenario, smallest fix. "None" if none.
## Advisory
New only, each with id (R2-A1, ...), one or two lines. No limit, but list each point once.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
## Not checked
````

### Round 2 report (verbatim)
````markdown
# Plan review — ci-evidence-trace, round 2

Reviewed independently by Codex, read-only and offline, at `b1879e0bb5338d4d00f7682be9bf3c1c7f54f63e`. External environment facts are accepted as supplied.

## Round-1 findings

- **R1-B1 — fixed:** D8 now checks the executed make target; V10 includes a same-name/wrong-command fixture.
- **R1-B2 — fixed:** D3 and V2 now cover the registered raw Base64 issuer key through exact-value matching, including its Base64 encoding, with synthetic fixtures and diagnostics that omit values.
- **R1-B3 — fixed:** V9 now exercises requirement, ARCH, DD and unlinked-test gaps separately.
- **R1-B4 — fixed:** Explicit PR/push modes, full history, unreadable/unresolvable-base failures and a merge-base fixture address the fallback scenario.
- **R1-B5 — not fixed completely:** Inspection completeness and rejection of partial reports are correctly specified; delivery of validated results to `qa-trace`, and clean-checkout verification of that dependency, remain unspecified.
- **R1-B6 — fixed:** M8 now covers only the two compose images selected by D2; floating Dockerfile bases are explicitly outside that claim.
- **R1-A1 — rejection accepted:** V1 checks target failure propagation; implementation review can verify ordinary workflow failure semantics without testing GitHub itself.
- **R1-A2 — partly fixed:** V6 adds malformed, incomplete and unknown-status reports; unreadable-report rejection is not explicitly exercised. This remains the existing advisory.
- **R1-A3 — fixed:** V1 includes parent-directory ownership and creation of `artifacts/quality/`.
- **R1-A4 — partly fixed:** Successful secret validation is explicitly required before publication, and diagnostics are tested; exact upload paths remain unspecified.
- **R1-A5 — rejection accepted:** Manual implementation review can verify D9’s documentary replacement; an automated prose check is unnecessary.
- **R1-A6 — fixed in the plan:** Increment B explicitly updates OPL-009’s obsolete lane/nightly mitigations.
- **R1-A7 — fixed:** D6 now includes scripts without DD-tagged functions; each uncovered ARCH section is reviewed rather than automatically exempted.
- **R1-A8 — fixed:** The job and target are named `gate-consistency`.
- **R1-A9 — fixed:** Fixtures must be synthetic and independent of trial artifacts.
- **R1-A10 — fixed:** Increment A documents the scanner contract in `AGENTS.md`, before B adds `EVID-T1`.
- **R1-A11 — rejection accepted:** Reverts plus coordinated required-check changes suffice at this scale; rollback dependencies are explained below.
- **R1-A12 — disposition accepted:** Enumerating affected harness IDs in A’s PR is already explicit in the test plan.
- **R1-A13 — fixed:** The assets section acknowledges the move into scratch.
- **R1-A14 — fixed:** V9 includes a gap swap with unchanged aggregate count.

## Answers

### 1. Intent

The revised plan preserves the main decisions:

| Decisions | Assessment |
| --- | --- |
| D1–D3 | CI E2E, continued local verification, two pinned images, scratch token hand-offs, fingerprints and publication after secret validation are represented. |
| D4–D5 | Static mappings and per-requirement results are represented, but the result-consumption path remains incomplete under R1-B5. |
| D6 | File-backed ARCH implementation and retirement have direct controls in V8/V11. |
| D7 | Gap identities, accepted gaps, expiry, stale entries and explicit PR-base failure now have appropriate fixtures. |
| D8 | Three-list agreement and job commands are tested. M5 still promises additional Makefile coverage absent from that mechanism: R2-B1. |
| D9 | The universal workflow replacement is explicit and can be checked in implementation review. |
| D10 | Review design and lanes remain deferred; `later_slices.md` preserves the user’s input without importing its older draft as approved scope. |
| D11 | A precedes B, and the scanner precedes publication. The later introduction of `REQ-T-R9`/`EVID-T1` is explicit. |

The expanded scanner contract directly addresses R1-B2. Its documented limits avoid introducing an unrestricted secret-classification programme.

### 2. Claims and evidence

**Success criteria**

| Criterion | Planned proof | Could proof pass while the claim is false? |
| --- | --- | --- |
| 1: Required CI E2E, deployment inspection and evidence validation | V1, implementation-PR CI runs, required-check update, local full run | Tooling fixtures alone cannot prove live triggers or required checks; operational acceptance must inspect those settings and job steps. |
| 2: Secret-free evidence | V2, changed harness evidence, full-run `qa-evidence` | Covered for D3’s declared detection contract. Arbitrary unregistered, unrecognisable credentials remain an explicitly documented limit. |
| 3: Accurate static requirement statuses | V5 produces statuses; V7 interprets them; V6 validates reports | Yes: fixtures supply a report, while the actual `qa-trace` execution has no specified report-delivery path. R1-B5 remains open. |
| 4: New-gap rejection and accepted-gap handling | V9 and historical replay V12 | The listed category, identity and date controls address the original misses. |
| 5: ARCH review and retirement | V8/V11 plus review of the thirteen sections | File existence cannot prove semantic implementation; reviewing each declaration remains necessary and is explicitly planned. |
| 6: Gate consistency | V10 and the post-update positive control | Adequate for the three named lists and commands; insufficient for M5’s Makefile-only addition claim. |

**Threat-model claims**

| Row | Evidence and assessment |
| --- | --- |
| M1 | V9 covers each stated addition category; V12 reproduces the historical requirement miss. Static-result availability remains relevant under R1-B5. |
| M2 | V9 covers missing reasons/expiry, expiry boundaries and stale acceptances. |
| M3 | V5/V7 cover known violations when a report is supplied. They do not establish correct behaviour when the real trace job lacks that report. |
| M4 | V6 rejects missing, malformed, incomplete, partial and digest-mismatched deployment reports in `qa-evidence`. This matches the specifically stated compose/register freshness claim. |
| M5 | V10 now catches wrong commands as well as name disagreement. It does not observe Makefile-only additions: R2-B1. |
| M6 | V2 covers token shapes, PEM keys, credential lines, registered raw key values, encoding and non-disclosing diagnostics. Full-run verification checks the resulting evidence. |
| M7 | The required `e2e` check and live workflow acceptance provide the proof. Unit fixtures cannot substitute for checking the external ruleset. |
| M8 | V3 checks the two exact image tags and compose/register agreement. The narrowed claim is consistent with D2. |
| M9 | V8 directly tests existing and missing implementation files. |
| M10 | V1 tests harness failure propagation. Workflow review must confirm subsequent tooling commands remain failure-propagating and uploads require successful validation. The rejection of R1-A1 is acceptable. |

**Requirement proofs**

- **REQ-T-R9:** V2 provides concrete negative and positive controls for the declared scanner contract; `EVID-T1` supplies its trace/specification home. This is a bounded detection mechanism, not exhaustive recognition of every possible credential.
- **REQ-SEC-K1, K2 and K4:** V5/V7 must preserve their known-violation statuses and gap classification. Merely mapping them to static tests must never make them proved.
- **REQ-SEC-K3 and K5–K8:** Existing deployment tests cover environment grants, ancestor mounts, container paths and holder consistency. The planned static entries must identify the relevant existing negative-control selectors, as the test plan requires.
- **REQ-SEC-D1:** Existing default-deny fixtures cover registered service facts; reusing them is proportionate.
- **REQ-SEC-D2:** V5/V6 now distinguish inspected results from `not_checked`; existing controls cover effective-user selection, forbidden root, unknown users and grace expiry. V7 does not explicitly exercise rendering `grace` or `not_checked`; that remains implementation-review detail unless the missing-result problem is resolved by defaulting to proof.
- **REQ-M4B-W8 and REQ-M5-CJ2:** Their evidence clauses remain intact. Scratch storage, redacted mint responses and evidence validation address the admitted leak without changing authorization outcomes.

Requirements are otherwise sufficiently concrete for this slice. The unresolved distinction is between **a valid proof mapping** and **a validated execution result** in `qa-trace`.

### 3. Design and quality

The mechanisms remain proportionate: existing make targets and validators are extended; tooling tests stay in `tests/tools/`; static specifications stay in `docs/test_spec.md`; accepted gaps stay beside trace mappings.

Separate job names and per-requirement statuses should make failures understandable. Known violations and grace must remain visible despite an overall deployment-gate PASS.

R1-B5 prevents approval of the current result flow. The existing `qa-trace` job is independent (`.github/workflows/ci.yml:20`), and `qa-quality` currently lists `qa-trace` before `qa-deploy` (`Makefile:83`). Naming `e2e` as the producer does not deliver its files to another job.

The smallest resolution is to specify where validated results are consumed and how standalone structural tracing behaves without them. No additional reporting framework is needed.

### 4. Failure and change

The revised contracts correctly reject:

- An unreadable or unparsable ruleset response.
- An unavailable PR base or unreadable historical trace input.
- Missing, malformed, incomplete, unknown-status, inspection-skipped or digest-mismatched deployment evidence.
- An existing registered asset that cannot be read.

Evidence-reading errors must likewise prevent publication; silently skipping unreadable evidence would violate D3.

The remaining R1-B5 scenario is concrete: a clean CI `qa-trace` job has neither the `e2e` report nor an inspected local deployment. Treating static entries as proved in that situation can hide K1/K2/K4’s known violations while V5–V7 still pass on supplied fixtures. Failing instead avoids that false green but leaves the advertised successful CI path unspecified.

Specify that flow and add a clean-checkout acceptance case, including missing-result behaviour and how the base/head comparison obtains comparable inputs.

A-before-B is sound. B can be reverted while retaining A’s scanner and E2E job, with corresponding required-check changes. Removing A while B remains requires unwinding B’s dependencies first. Any rollback restoring token-writing evidence must disable publication in the same operation. These are coordination steps, not grounds for a new migration mechanism.

### 5. Rules and new risks

The plan retains the local full E2E run, tests-first implementation, independent review, authored trace changes and frozen-record model. No service authorization behaviour or asset holder is intentionally changed.

New process state and flows are documented: CI artifacts and retention, deployment reports, accepted gaps, external required checks and scratch storage. The Docker-socket holder is already registered. The scanner’s additional reads are described without proposing new service access.

The register changes remain limited to two image tags. Known runtime problems are not represented as fixed, and OPL-009’s mitigation text is scheduled for correction.

Two obligations remain unresolved: D4/D5’s checked-result flow under R1-B5, and M5’s overstatement under R2-B1. I found no basis for adding production-hardening requirements.

### 6. Ripple

Most dependencies are accounted for:

| Change | Dependents covered |
| --- | --- |
| Evidence layout | Harness readers, fingerprints, mint JSON, scanner and hand-written evidence descriptions |
| Static tests | Trace schema/parser, specification headings, `docs-check`, deployment/evidence reports |
| ARCH implementation declarations | Trace parser, reviewed declarations and retirement |
| Gap gate | Historical inputs, full Git history, PR context and accepted-gap validation |
| CI gates | Make targets, workflow, rulebook table and external required checks |
| Process changes | D9’s workflow replacement, OPL-009 and deferred slice-3 input |

The missing dependency is report production **through to trace consumption**, including CI workspace separation and clean local execution. R1-B5’s fix is therefore only partial.

### 7. Durability

Decisions have appropriate intended homes: authoritative requirements/architecture, `AGENTS.md`, `trace/tests.yaml`, `docs/test_spec.md`, compose/register and the live OPL. Deferred user input is preserved in `later_slices.md`.

Synthetic fixtures eliminate dependence on expiring trial artifacts. A now has a durable scanner contract before B introduces its static specification. Exact required-check configuration remains external authoritative state, appropriately documented and checked by D8.

The report-consumption contract must live in the revised plan/test plan and then the relevant gate documentation, rather than being settled only in implementation discussion.

Reviewed hashes:

| File | SHA-256 |
| --- | --- |
| `plan.md` | `d71716fdfc340f6c3be5c80a97aff16b5da9e509d7a97db6d87abf7c1a7a2ccd` |
| `test_plan.md` | `70c550f2c1e7fb3e34829677e49921de8512ea3347ae3f1687a374c9ff4c11f0` |

### 8. Blind spots

This review establishes plan adequacy, not implementation correctness. Future verification must establish actual scanner traversal, scratch/upload separation, workflow failure propagation, image selections and report handling.

I inspected repository rules, both plans and revisions, round-1 responses, deferred input, workflow, Makefile, trace/evidence/deployment validators, deployment tooling tests, relevant requirements/architecture, the register and OPLs, and harness evidence handling.

The read-only command `python3 -B scripts/check_docs.py` passed. It does not establish the proposed gates’ behaviour.

## Blocking findings

### R2-B1 — M5 promises detection of Makefile-only gates that D8 cannot observe

**Where:** `docs/slices/ci-evidence-trace/plan.md:41`, `plan.md:87`; `docs/slices/ci-evidence-trace/test_plan.md:85`.

**Blocking criterion:** Concrete M5 false green; contradiction between the “caught by” claim and the mechanism.

**Failure scenario:** An honest change adds a new quality-gate target to the Makefile but forgets its rulebook row, CI job and required check. D8’s three lists remain identical, and every V10 fixture can pass. The command check examines existing jobs, so it cannot discover the omitted gate. M5 expressly promises to catch a gate added to the Makefile.

**Smallest fix:** Narrow M5 to gates declared in the `AGENTS.md` CI table, matching D8’s approved mechanism. If Makefile-only discovery is intended, specify how gate targets are distinguished from helper targets and add the missing negative fixture.

R1-B5 remains open as explained above; it is not repeated as a new finding.

## Advisory

None new.

## Verdict

Approvable within the threat model: no — R1-B5, R2-B1.

## Not checked

- No file modifications, Docker commands, service starts or network access.
- No secret-bearing runtime files or environment variable values inspected.
- No live ruleset verification, CI execution or artifact downloads.
- No tooling, unit, E2E or historical-replay execution; some existing tooling tests invoke Docker.
- No independent reconstruction of grill-me; D1–D11 and the recorded deferrals were treated as authoritative intent.
- No exhaustive runtime security audit or verification of the proposed implementation, which does not yet exist.````

## Round 3 (2026-10-30)
Reviewed files (SHA-256, at commit `af5e819`):
- `plan.md` `fb15fda048d2eb6e2be420d70e949ce54f410de2124aad5c292d0dfc2ae731fc`
- `test_plan.md` `f018d78360c1b87ffde18459747abbfeefe3eeaf3b7c67384bdb27b59abd9781`

Verdict: **yes — approvable within the threat model.** R1-B5 and R2-B1 fixed; no new findings; the
rejections of R1-A1, R1-A5 and R1-A11 accepted. The review ends here: no blocking finding is open.

### Round 3 prompt (verbatim)
````markdown
You are the independent plan reviewer for a slice plan in the repository at the current working
directory. You did not write it. Review read-only: do not modify files, run docker, start services
or use the network. Never print key material, tokens or environment variable values.

## What is under review
The slice plan `docs/slices/ci-evidence-trace/plan.md` and its test plan
`docs/slices/ci-evidence-trace/test_plan.md` (commit `HEAD`; `git log -4` and `git diff HEAD~3` show the plan commit and the changes of rounds 1 and 2). They are the plan for slice 2 of the agentic-delivery-process programme. The user
has not seen them yet; your review comes first.

The intent they must serve: the user's decisions from the slice's grill-me, recorded in the plan's
decision table (D1–D11), and the repository's rules in `AGENTS.md`. Earlier input for this slice is
`docs/slices/agentic-delivery-process/later_slices.md`; the plan says which parts of it were moved
to slice 3, and that move is a user decision.

You may read the whole repository. Decide yourself where to look; you are not given a list of files.

## This is round 3
The prompts, reports and the author's answers of rounds 1 and 2 are in
`docs/slices/ci-evidence-trace/plan_review.md`. For each finding still open after round 2 (R1-B5, R2-B1) and each change the author made in answer to round 2: say whether the fix is
correct and complete; for each rejected finding, accept the rejection or re-raise it with new
evidence. From this round, a new finding counts only if it meets the blocking criteria; do not add
advisories that are not new.

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
# Plan review — ci-evidence-trace, round 3
## Open findings
(one line per finding: fixed / not fixed, or rejection accepted / re-raised, with the reason)
## Answers
(one section per question above; brief where nothing changed since round 1)
## Blocking findings
New only, each with id (R3-B1, ...), where (file:line), the blocking criterion it meets, failure
scenario, smallest fix. "None" if none.
## Advisory
New only, each with id (R3-A1, ...), one or two lines. No limit, but list each point once.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
## Not checked
````

### Round 3 report (verbatim)
````markdown
# Plan review — ci-evidence-trace, round 3

Reviewed independently by Codex, read-only and offline, at `af5e819132dd9659b11c87e2799d4915cb5ddc2d`. External environment facts are accepted as supplied.

## Open findings

- **R1-B5 — fixed, correctly and completely:** D5 now separates structural tracing from execution evidence. `qa-trace` derives declared status from the register; `qa-evidence` validates the inspected deployment report. V6 rejects disagreement, and V7 exercises clean-checkout tracing on head and base without artifacts.
- **R2-B1 — fixed, correctly and completely:** M5 now describes gates declared in the rulebook’s CI table, matching D8’s mechanism. Makefile-only discovery is explicitly outside the claim.
- **R1-A2 — fixed:** V6 now explicitly rejects an unreadable report, completing the previously partial advisory fix.
- **R1-A4 — fixed at plan level:** D1 names the three upload paths and requires successful secret validation before publication. Implementation review must verify the actual upload configuration follows that contract.
- **Author’s gap-identity change — correct and complete at plan level:** D7 uses the head’s validator for both snapshots and identifies gaps by stable kind and ID. V9 adds a category-renaming fixture, addressing migration without concealing genuinely new gaps.
- **R1-A1 — rejection accepted:** V1 tests target failure propagation; workflow inspection can establish ordinary step failure propagation without reproducing GitHub’s execution engine.
- **R1-A5 — rejection accepted:** D9 is an explicit documentary change, appropriately verified through implementation review.
- **R1-A11 — rejection accepted:** Coordinated reverts and required-check updates suffice; a separate rollback mechanism is unnecessary.
- **R1-A12 — disposition accepted:** Enumerating affected harness IDs in Increment A’s PR remains explicitly planned.

Previously closed findings remain closed. No rejection is re-raised.

## Answers

### 1. Intent

The revised plan and test plan represent D1–D11 without a blocking omission or scope expansion.

| Decisions | Assessment |
| --- | --- |
| D1–D3 | CI E2E, continued local verification, two pinned compose images, scratch token storage, fingerprints, redaction and publication after secret validation are covered. |
| D4–D5 | Static tests receive trace entries, specification entries, implementations and checked results. Structural trace status and execution results now have distinct, workable sources. |
| D6 | File-backed ARCH implementation, review of the thirteen gaps and retirement of the previous QA-specific tags and integration entries remain covered. |
| D7 | Comparison uses the merge-base, stable gap identities and the same validator on both snapshots. Accepted gaps have reason, expiry and stale-entry controls. |
| D8 | Rulebook rows, workflow jobs, required checks and job commands are checked. The narrowed M5 accurately states that scope. |
| D9–D10 | One workflow replaces lanes for now. Review design and lane decisions remain recorded as slice-3 input rather than imported as approved implementation scope. |
| D11 | A precedes B; secret removal precedes publication. B introduces the static trace model and traces the scanner already delivered in A. |

The R1-B5 resolution is consistent with existing E2E tracing: a trace link establishes structural coverage; the separate evidence gate establishes an execution result. It does not require reports to cross CI job boundaries.

### 2. Claims and evidence

**Success criteria**

| Criterion | Planned proof and practical limit |
| --- | --- |
| 1. Required CI E2E succeeds | V1, implementation-PR CI, the required-check update and the local clean-stack run. Live acceptance must verify triggers, commands and ruleset configuration; fixtures alone cannot establish them. The declared M5-T55 skip remains visible. |
| 2. Evidence contains no tokens or private keys | V2 supplies detection controls and boundaries; changed harness evidence and the full-run scanner establish the resulting output. This is assessed against D3’s documented scanner contract and known limits. |
| 3. Correct static statuses | V5 proves report production, V6 validates execution evidence, and V7 derives structural status from the register without artifacts. K1/K2/K4 and D2 remain gaps rather than becoming proved through static mappings. |
| 4. New gaps rejected | V9 covers categories, identity, unchanged-count swaps, acceptance, expiry, stale entries and base failures. V12 reproduces the historical miss. |
| 5. ARCH review and retirement | V8 checks implementation-file existence; V11 checks retirement. Reviewing the thirteen declarations remains necessary because file existence cannot establish semantic implementation. |
| 6. Gate consistency | V10 supplies list-disagreement, wrong-command and API-read failure controls, plus a positive fixture. The merged configuration receives live acceptance. |

**Threat-model rows**

| Row | Proof and assessment |
| --- | --- |
| M1 | V9 exercises new requirement, ARCH, DD and unlinked-test gaps; V12 reproduces the ten-requirement miss. |
| M2 | V9 covers missing acceptance fields, expiry boundaries and stale acceptances. |
| M3 | V5/V7 preserve known-violation status; V6 prevents a report claiming `holds` from overriding the register’s declaration. |
| M4 | V6 rejects missing, unreadable, malformed, incomplete, inspection-skipped and digest-mismatched reports. This proves the stated compose/register binding. |
| M5 | V10 matches the revised three-list and job-command claim. Makefile-only gates are expressly excluded. |
| M6 | V2 covers token shapes, private-key blocks, credential lines, registered values and encoded values, with non-disclosing diagnostics. Full-run inspection must confirm scratch separation and scanner traversal of the published evidence. |
| M7 | The required `e2e` check, workflow inspection and implementation-PR execution establish independent CI execution. |
| M8 | V3 checks exact OPA/Redis tags and compose/register agreement. Floating Dockerfile bases remain an accepted limit. |
| M9 | V8 directly rejects a missing declared implementation file. |
| M10 | V1 proves harness failure reaches the target’s result. Workflow review must confirm later tooling failures also fail the job and publication requires successful validation. |

**Requirement proofs**

- **REQ-T-R9 / EVID-T1:** V2 provides concrete negative and positive controls. D3 defines the detection contract, including its boundaries; the requirement’s trace and specification home arrive in B.
- **REQ-SEC-K1, K2 and K4:** V5/V7 retain their known-violation classification and OPL attribution. Mapping them to static tests cannot erase those gaps.
- **REQ-SEC-K3 and K5–K8:** Existing deployment controls cover environment grants, ancestor mounts, container paths, socket mounts and holder consistency. The planned static specifications must name the relevant existing negative-control selectors.
- **REQ-SEC-D1:** Existing default-deny fixtures exercise service facts, mount modes, unregistered services and stale entries.
- **REQ-SEC-D2:** Existing controls cover effective-user selection, root and unreadable users, forbidden grandfathering and grace expiry. V5/V6 distinguish inspected evidence from `not_checked`; V7 preserves declared grace as an unproved requirement.
- **REQ-M4B-W8 and REQ-M5-CJ2:** Their evidence clauses remain intact. Moving hand-offs and redacting saved responses changes evidence handling without changing authorization outcomes.

No planned proof depends on treating the overall deployment-gate PASS as proof that every requirement holds.

### 3. Design and quality

The revised design is proportionate. It extends existing validators, make targets and tooling tests, and keeps specifications in `docs/test_spec.md`. It avoids adding report downloads or CI job dependencies merely to make structural tracing work.

The register-derived trace status is simpler and more reproducible than consuming a local run report: clean checkout, PR and merge-base analysis use the same rule. Execution evidence remains checked separately.

Job names, per-requirement statuses, named gap diagnostics and retained reports should make failures understandable. Known violations and grace remain visible even when an overall gate passes.

### 4. Failure and change

The planned contracts reject unavailable or unparsable ruleset input; unresolved or unreadable PR bases; missing, unreadable, malformed, incomplete or mismatched deployment evidence; and unreadable existing registered asset files.

Missing execution evidence no longer creates an ambiguous `qa-trace` dependency: tracing does not consume it, while `qa-evidence` requires it. Evidence-reading failures must likewise prevent successful validation and publication under D3.

A-before-B remains sound. B can be reverted while retaining A’s scanner and E2E job, with corresponding required-check changes. Removing A while retaining B requires unwinding B’s dependencies. Any rollback restoring token-bearing evidence must disable publication in the same coordinated change.

### 5. Rules and new risks

The plan retains tests-first implementation, user approval through the plan merge, independent review, local clean-stack verification and hand-written evidence specifications.

The new process state and flows are described: public CI artifacts and retention, deployment reports, accepted gaps, external required checks and harness scratch storage. No service authorization behavior or holder list is intentionally changed. The Docker-socket holder already exists in the register.

The register changes remain limited to image tags. OPL-005 through OPL-008 are not presented as fixed; OPL-009’s obsolete lane/nightly mitigations are explicitly scheduled for correction. The new gates and documentary changes are user decisions recorded in D1–D11, rather than unsolicited process growth.

### 6. Ripple

The plan accounts for the material dependencies:

| Change | Dependents covered |
| --- | --- |
| Token storage and redaction | Harness readers, fingerprints, saved responses, scanner and evidence descriptions |
| Static tests | Trace schema, validator, specification headings, `docs-check` and evidence validation |
| Deployment report | Inspected production in E2E/local verification, completeness, digests and register agreement |
| ARCH declarations | Parser changes, reviewed file declarations and retirement |
| Gap comparison | Historical inputs, full history, merge-base selection, stable identities and accepted gaps |
| CI gates | Make targets, workflow jobs, rulebook table and external required checks |
| Process decisions | D9’s replacement wording, OPL-009 and preserved slice-3 input |

The previous missing report-to-trace dependency is resolved by removing that dependency explicitly.

### 7. Durability

Decisions have appropriate durable homes: requirements, architecture, `AGENTS.md`, the register, trace mappings, hand-written specifications and the live OPL. Deferred user decisions remain recorded in `later_slices.md`.

The scanner contract lands with A, so it does not depend on B’s later static specification. Synthetic fixtures avoid dependence on expiring trial artifacts. Required checks remain external authoritative state, with a planned consistency check.

The 14-day artifacts are execution evidence, not the sole record of design decisions. Review reports, hashes and author dispositions belong in `plan_review.md`.

### 8. Blind spots

This establishes plan adequacy, not implementation correctness. Actual scanner traversal, publication paths, workflow failure behavior, historical snapshot handling and deployment-report production still require implementation review and the planned acceptance runs.

No new blocking scenario was established within M1–M10.

## Blocking findings

None.

## Advisory

None new.

## Verdict

Approvable within the threat model: yes

## Not checked

- No modifications, Docker commands, service starts or network access.
- No runtime secret files, token values or environment values inspected.
- No live ruleset verification, CI execution or artifact downloads.
- No tooling, unit, E2E or historical-replay execution. Some existing tooling tests invoke Docker.
- No independent reconstruction of grill-me; D1–D11 and recorded deferrals were treated as authoritative intent.
- No exhaustive service-code security audit.

Read-only verification: `python3 -B scripts/check_docs.py` passed.

Reviewed SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `plan.md` | `fb15fda048d2eb6e2be420d70e949ce54f410de2124aad5c292d0dfc2ae731fc` |
| `test_plan.md` | `f018d78360c1b87ffde18459747abbfeefe3eeaf3b7c67384bdb27b59abd9781` |````
