# Independent review — ci-evidence-trace Increment B

Implementation-PR review under [`AGENTS.md` — Independent review](../../../AGENTS.md#independent-review).
Reviewer: Codex CLI 0.165.0, `codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral`, run by hand; it saw
the repository, the merged plan and the change, never the author's reasoning.

| Round | Reviewed | Verdict | Findings |
| --- | --- | --- | --- |
| 1 | `origin/main..f592d13` | not approvable | B1-B1, B1-B2 (blocking); B1-A1 to B1-A4 (advisory); two simpler alternatives |
| 2 | fixes in `0195a8b` | not approvable | B1-B1 re-raised (an asset naming an unknown requirement); all else accepted |

## Author answers, round 1
| Finding | Answer | Where |
| --- | --- | --- |
| B1-B1 incomplete register data turns known violations into static proofs | Fixed: an existing register must have `assets`, `services` (maps) and `known_violations` (list), or `qa-trace` fails (exit 2); a known-violation row that names no register asset with a requirement is a structural failure, never skipped; a missing register is accepted only where no static test takes its status from it (trees older than the register). | `scripts/validate_traceability.py` `_load_register`, `_known_violation_reasons`, `_register_holds_back`; tests `test_register_without_assets_mapping_fails_closed`, `test_known_violation_row_naming_no_register_asset_fails`, `test_missing_register_with_static_tests_fails` |
| B1-B2 push mode passes expired and stale accepted gaps | Fixed: in `--mode push` the coverage comparison is still only reported, but an expired, stale or malformed `accepted_gaps` entry fails. | `gap_gate`; test `test_push_mode_fails_on_an_expired_or_stale_acceptance` |
| B1-A1 failed `qa-deploy` run and the validator's exit path | Taken: a failed and a broken `qa-deploy` run each write a report saying so; a failed report fails `qa-evidence` through its exit code, a passing one passes. | `test_qa_deploy.py` `test_failed_or_broken_run_writes_a_report_that_says_so`; `test_evidence_deploy_report.py` `test_failed_report_fails_qa_evidence_through_its_exit_code` |
| B1-A2 V7 contradictory run report; V6 unreadable report | Taken: a run report claiming success leaves a known violation unproved; an unreadable (mode 0) report fails. | `test_a_run_report_cannot_change_a_status`; `test_unreadable_report_fails` |
| B1-A3 complete the records after the E2E run | Taken: the clean-stack run passed (120/120, `qa-deploy` with image users and `qa-evidence` PASSED); `docs/STATUS.md` and the implementation log record it. CI and the ruleset update follow at the PR. | `docs/STATUS.md`, `docs/history/implementation_log.md` |
| B1-A4 gate command matched as text, even in an unexecuted branch | Rejected: outside the honest-mistake model as a blocker; a job that names its target only in a branch it never takes is a deliberate construction, and the job's own conclusion is still the gate's result (`AGENTS.md` "Quality gates"). The `qa-trace` job runs `make qa-trace` in both branches. | — |
| Simpler alternatives: parse `trace/tests.yaml` once; compute each digest once | Both taken. | `_load_inputs`, `_items`; `deploy_report_failures` |

## Author answers, round 2
| Finding | Answer | Where |
| --- | --- | --- |
| B1-B1 re-raised: a register asset whose `requirement` names no existing requirement drops its known violation | Fixed: every register asset must name a requirement that exists in `docs/requirements.md`, or `qa-trace` fails. | `_unknown_asset_requirements`; test `test_register_asset_naming_an_unknown_requirement_fails` |

## Round 1 report (verbatim)

### Implementation review — ci-evidence-trace Increment B, round 1

Reviewed by Codex as the independent reviewer, in a read-only, offline session. Scope: commit `f592d13`, `origin/main..HEAD`, against the plan and test plan on `origin/main`.

#### Answers

##### 1. Tests

The tests cover the main intended behaviors well, including individual gap identities, the correct merge-base, deployment-report digests, and the historical miss. They leave some failure paths untested. Two actual implementation failures are blocking below; other test limitations are advisory.

The assessment below distinguishes what an individual test establishes from what its companion negative controls establish.

**`tests/tools/test_trace_model.py`**

| Test | What it establishes; wrong implementation that could still pass | Test-plan match |
| --- | --- | --- |
| `test_static_entry_with_gate_and_negative_controls_proves_its_requirement` | Checks exact static/E2E statuses and absence of requirement gaps. Alone, a checker that ignores gate/control validity could pass; the following negative controls constrain that. | V4, V7 |
| `test_broken_static_entry_is_a_structural_failure` | All six cases require exit 1 and a specific diagnostic: missing control file, missing selector, missing controls, nonexistent target, invalid gate command, missing result. A checker that merely rejects every static entry is excluded by the positive control. It validates declarations, not whether the selected tooling test meaningfully exercises the gate. | V4 |
| `test_known_violation_row_makes_the_requirement_not_proved` | Checks the exact OPL reason and requirement gap. It would miss a checker that handles valid registers but silently drops violations when asset mappings are missing—the actual **B1-B1** failure. | V7 |
| `test_nonroot_requirement_is_not_proved_within_its_grace` | Tests both sides of the UTC boundary. It does not check the gap list explicitly. The post-expiry “proved: static” expectation matches the approved structural model; the deployment gate must still enforce non-root operation. | V7 |
| `test_repository_statuses_in_a_clean_copy_without_artifacts` | Checks the complete current security-status map without run artifacts. A checker that consults a run report **when present**, but falls back correctly when absent, would still pass. | V7; report-independence coverage is incomplete |
| `test_implemented_by_existing_files_counts_as_implemented` | Checks the actual declaration list and absence of an ARCH gap. Alone, ignoring file existence would pass. | V8 positive control |
| `test_implemented_by_missing_file_is_a_structural_failure` | Requires the missing-file error and failure exit. Together with the positive control, excludes always-pass/always-fail implementations. | V8 negative control |
| `test_arch_without_dd_or_implemented_by_stays_a_gap` | Requires the precise ARCH gap while push mode succeeds. A checker that treats every existing file declaration as sufficient remains possible, but existence is exactly D6’s automatic check. | V8 |
| `test_pr_adding_a_gap_fails_naming_it` | Four cases check exact new-gap identities and diagnostics: requirement, ARCH, DD, unlinked test. Rejects a gate that reads nothing or compares HEAD with itself. Does not exercise the integration-test gap category. | V9’s four listed fixtures |
| `test_closing_one_gap_and_adding_another_fails` | Checks both closed and new identities. Excludes comparing only total gap counts. | V9 |
| `test_accepted_gap_entry_lets_the_gap_pass` | Checks acceptance of the named DD gap. An implementation that exempts **all** new gaps whenever any valid acceptance exists could pass; there is no mixed accepted/unaccepted fixture. | V9, though not the exact close-one/add-another combination |
| `test_accepted_gap_is_valid_through_its_expiry_date` | Tests the last valid second and first invalid second, with a specific expiry diagnostic. Only exercises PR mode. | V9 |
| `test_stale_accepted_gap_fails` | Checks removal of an acceptance whose gap no longer exists. Only exercises PR mode. | V9 |
| `test_accepted_gap_without_reason_or_valid_expiry_fails` | Three cases reject missing reason, missing expiry, and invalid expiry. Does not cover malformed top-level containers or whitespace/non-string reasons. | V9’s listed missing-field cases |
| `test_closing_a_gap_passes_and_an_old_gap_passes` | Checks both no new gaps and retention of the remaining old gap. Excludes treating every existing gap as new. | V9 |
| `test_push_mode_reports_a_new_gap_and_passes` | Checks ordinary push-mode reporting. It would pass an implementation that suppresses acceptance-validation failures too—the actual **B1-B2** failure. | V9’s ordinary push case |
| `test_pr_mode_needs_an_explicit_mode_and_a_base` | Checks distinct failures for omitted mode and omitted base. Excludes accidental fallback to push mode. | V9 |
| `test_unresolvable_base_fails_and_never_falls_back` | Checks Git resolution failure and the appropriate diagnostic. Uses an unknown ref rather than a shallow-history fixture. | V9; same failure branch |
| `test_unreadable_base_trace_inputs_fail` | Uses an unparseable requirements document and checks the base-input failure. It does not test filesystem permission denial or every structurally invalid base. | V9, narrowly |
| `test_base_is_the_merge_base_not_the_tip_of_main` | Main closes a gap after divergence; the feature branch retains it. Comparing against main’s tip would fail this test. | V9 |
| `test_reusing_a_retired_id_fails` | Checks retired DD reuse and its reason. Does not directly test retired test-ID reuse. | V11 |
| `test_repository_retired_the_deploy_dds_and_integration_cases` | Checks the six removed tags and twelve retirement records by text. Alone, equivalent tags elsewhere or ineffective retirement enforcement could pass; full trace computation provides additional coverage. | V11 |
| `test_gap_gate_replay_of_1b_fails_on_the_ten_new_req_sec_gaps` | Uses historical trees and requires all ten gap identities. It permits additional gaps, appropriately. Alone, exit 1 could arise from another failure, but the reported new-gap assertions prevent an unrelated failure from being sufficient. | V12 |

I independently recomputed the historical trees in memory using the head validator: all ten expected REQ-SEC gaps appear. The current branch comparison also reproduces **0 new, 25 closed, 113 remaining**.

**`tests/tools/test_gate_consistency.py`**

| Test | What it establishes; remaining limitation | Test-plan match |
| --- | --- | --- |
| `test_agreeing_lists_pass` | Checks CI-row extraction and the positive three-list result. Alone, an always-empty result would pass; negative controls exclude that. | V10 |
| `test_ci_gate_without_job_fails` | Requires the exact omitted-job diagnostic. | V10 |
| `test_job_without_row_fails` | Requires the exact extra-job diagnostic while keeping required checks otherwise consistent. | V10 |
| `test_job_that_is_not_a_required_check_fails` | Isolates omission from required checks. | V10 |
| `test_required_check_without_job_fails` | Tests the reverse required-check relationship. | V10, useful additional coverage |
| `test_job_running_another_target_fails` | Excludes checking job names alone. Does not establish that a matching command actually executes. | V10 |
| `test_target_prefix_is_not_its_own_target` | Excludes accepting `qa-deploy-extra` as `qa-deploy`. | V10, additional boundary |
| `test_unreadable_or_unparsable_ruleset_fails_closed` | Exercises malformed JSON, a non-object, and an invalid rules field through the CLI. Despite its name, it does not exercise an unreadable file or network failure. | V10, partial failure-source coverage |
| `test_missing_ruleset_source_fails_closed` | Rejects omission of both sources. A live API error path is not exercised. | V10 |
| `test_repository_table_and_workflow_agree_with_the_planned_required_checks` | Checks the real repository against the intended post-update ruleset. It cannot establish the live ruleset state or a CI job conclusion. | V10 positive control |

The command check is lexical: a matching line inside a disabled shell branch would satisfy it. I found no such disabled or failure-swallowing gate command in this workflow.

**`tests/tools/test_evidence_deploy_report.py`**

| Test | What it establishes; wrong implementation that could still pass | Test-plan match |
| --- | --- | --- |
| `test_passing_inspected_matching_report_is_accepted` | Positive helper control. Alone, a helper that reads nothing would pass. | V6 |
| `test_report_that_failed_skipped_inspection_or_is_stale_fails` | Five cases independently reject failed/error verdicts, skipped inspection, and each wrong digest. A correct helper disconnected from the CLI could still pass every case. | V6 |
| `test_missing_unreadable_or_malformed_report_fails` | Tests a missing file, malformed JSON, and a non-object. It does **not** test unreadability. | V6, one planned case absent |
| `test_changed_register_after_the_run_makes_the_report_stale` | Changes the actual input after report creation, proving the comparison uses current file contents. | V6 |
| `test_makefile_qa_evidence_checks_the_deploy_report` | Checks both Makefile text and expanded invocation. It does not prove that the validator propagates a rejected report into its final exit status. | V6 wiring coverage |

Inspection confirms that the current CLI does propagate deployment-report failures. I also exercised its `PermissionError` handling and missing-input/`None` digest rejection with in-memory mocks; both reject correctly.

**Additions to `tests/tools/test_check_docs.py`**

| Test | Assessment | Test-plan match |
| --- | --- | --- |
| `test_static_spec_complete_has_no_problems` | Positive parity control; alone permits reading nothing. | V4 |
| `test_static_entry_without_heading_is_reported` | Requires the exact missing-heading result. | V4 |
| `test_static_heading_without_entry_is_reported` | Requires the reverse parity error. | V4 |
| `test_static_duplicate_heading_is_reported` | Checks duplicate rejection. | V4, additional coverage |

These exercise the helper rather than `run_checks`; a disconnected helper could pass them. The actual wiring is present, and I independently ran the read-only documentation checker successfully.

**Changes to `tests/tools/test_qa_deploy.py`**

| Test | Assessment | Test-plan match |
| --- | --- | --- |
| `test_repository_deployment_passes_with_known_violations_only` | Existing behavioral check now directs its report to temporary storage. This prevents tooling tests from overwriting run evidence. It remains a positive deployment case. | Supports V5 |
| `test_report_records_verdict_findings_inspection_and_digests` | Exact payload comparison covers both inspection-flag settings, warnings, known violations and both digests. Both cases supply `"passed"` and an empty error list, so an always-passing report producer would survive. | V5, incomplete failure-verdict coverage |
| `test_repository_run_writes_a_report_without_env_values_or_requirement_status` | Exercises `main`, checks current known violations and absence of status fields. The environment-value assertion is weak: it checks for `=` only in problems/known violations, without a sentinel value. A value leaked elsewhere could survive. | V5, partial non-disclosure coverage |

Overall, V4–V12 have substantial coverage. The main remaining test weaknesses are absence of contradictory run-report input for V7, incomplete report-production/CLI failure tests for V5–V6, and no push-mode expiry/staleness tests.

##### 2. Keys

I found no new service exposure path.

The diff changes no compose mounts, Dockerfiles, entrypoints, runtime services, asset locations, or holder lists. The new CI jobs run QA tooling without adding secret inputs. Deployment-report fields contain verdicts, findings, inspection flags and file digests; the existing inventory retains environment variable names rather than values.

Existing OPL-005, OPL-006 and OPL-008 exposures remain. With the current valid register, the trace correctly leaves K1, K2 and K4 unproved.

I did not inspect secret contents or publication artifacts, so this is an assessment of the changed paths and report construction, not a fresh secret scan.

##### 3. Intent

| Decision | Assessment |
| --- | --- |
| D4 | Implemented: static declarations, specification entries, gate/control references and stored results extend the common trace chain. |
| D5 | Implemented for valid inputs. Status comes from the register, not run reports; deployment evidence checks verdict, inspection and digests. Malformed register handling violates the intended status guarantee: **B1-B1**. |
| D6 | Implemented. The thirteen previously uncovered ARCH sections now name implementing files; ARCH-034 separately names register and compose. The six DD tags and six integration entries are retired. The declarations fit their described configuration, harness or demo responsibilities. |
| D7 | Individual gap comparison, explicit modes, full history, merge-base selection and PR acceptances are implemented. Push mode incorrectly suppresses acceptance-validation failures: **B1-B2**. |
| D8 | Implemented in the repository: separate jobs, three-list comparison, named-command checks, and public ruleset access. Operational completion awaits the user’s ruleset update and CI. |
| D9 | The rulebook now explicitly applies the scaled slice workflow to every change. Documentary review is appropriate; no artificial runtime test is needed. |

The head validator’s compatibility with older trees is necessary for V12. However, applying “missing register means empty register” generally, and accepting incomplete mappings, is broader than historical replay requires. That deviation is not explained in the implementation records.

Likewise, D7 says the **comparison** is not enforced on push; it separately says expired and stale acceptances fail. The implementation’s broader warning-only behavior is not recorded as an approved deviation.

Success criteria:

- **3:** Met on today’s valid register. Independently reproduced the three known-violation statuses, D2 grace status, and six static proofs.
- **4:** Covered by the PR fixtures and implemented as specified for those cases. Push acceptance handling remains defective.
- **5:** Met by repository inspection and trace computation: zero ARCH implementation gaps, with the specified retirements.
- **6:** Repository-side consistency passes against the planned ruleset. It is **not yet demonstrated operationally**: the supplied current ruleset lacks the two planned checks, and branch CI has not run.

There is no runtime authorization scope expansion.

##### 4. Failure behaviour

| Input | Assessment |
| --- | --- |
| Merge-base | Unknown refs and Git failures fail; there is no fallback to push mode. |
| Base tree | Archive/extraction and essential parse/read errors fail. The child’s exit 1 is accepted, so a parseable base with structural failures can still supply comparison gaps; this is not blanket validation of the base. The current and historical bases I recomputed have zero structural failures. |
| Register | Missing files become `{}`; incomplete mappings can silently remove status restrictions. Invalid top-level YAML/non-map inputs fail, but valid YAML with missing semantic fields can produce false proof statuses. **B1-B1**. |
| `accepted_gaps` | PR mode rejects the tested malformed, expired and stale entries. Push mode records those failures as warnings and returns success. **B1-B2**. |
| Ruleset | Missing/unreadable source, invalid JSON and missing required contexts cannot yield a successful comparison against the current jobs. Some malformed nested shapes may terminate with an uncaught exception, but still fail rather than pass. |
| Deployment report | Missing/unreadable/malformed/non-object reports reject; missing verdict or inspection fields reject. Missing or unreadable compose/register inputs reject even when the report also lacks their digests, preventing `None == None` success. |

**M3:** The current valid register gives the intended answer. However, removing its `assets` mapping while retaining all three known-violation rows produces **zero structural failures** and changes K1 to **“proved: static.”** I reproduced this by substituting the malformed register in memory. The independent deployment gate would reject that register, but the authoritative trace status is already wrong, contradicting D5.

##### 5. Ripple

The main dependencies are consistent:

- `qa-trace` CI fetches full history and supplies explicit PR/push modes. Local Makefile defaults use PR comparison.
- `unit-diff-cov` has its own job and still obtains coverage through its Makefile prerequisite.
- `gate-consistency` has its own job and target. Against the supplied current ruleset facts, it reports exactly the missing `gate-consistency` and `unit-diff-cov` requirements.
- `docs-check` invokes static-heading parity; all eleven new static entries have matching specification headings.
- `qa-deploy` writes the report that `qa-evidence` now checks. The E2E job preserves their required order.
- Deployment tooling tests direct reports to temporary paths, avoiding accidental replacement of the run’s report.
- Requirements, architecture, trace declarations, rulebook and static-test prose reflect the new model. Searches found no remaining live implementation references to the retired DD/integration entries.
- The new gap names have no stale tooling consumers in the searched repository paths.

Close-out records remain pending: there is no Increment B implementation-log entry or refreshed verification table yet. `docs/STATUS.md` still contains Increment A’s verification description and old trace counts. The delivery-log closures are written for the merged result; completion needs to include the actual ruleset update and CI results. The user’s supplied facts explicitly anticipate further records after E2E, so I treat this as unfinished close-out rather than an additional implementation blocker.

#### Blocking findings

##### B1-B1 — Incomplete register data can turn known violations into static proofs

**Where:** `scripts/validate_traceability.py:564`, `scripts/validate_traceability.py:587`.

**Criterion:** Concrete M3 false proof status and contradiction with D5’s register-derived status guarantee.

**Failure scenario:** An honest register edit drops the `assets` mapping while leaving `known_violations` intact. `_load_register` accepts the document; `_known_violation_reasons` substitutes an empty asset map and silently skips every unresolved row. On this repository’s inputs, computation reports zero structural failures and K1 as `"proved: static"` despite its retained OPL-005 row. K2 and K4 are similarly affected.

The unconditional missing-register fallback also treats missing authoritative input as an empty register. Other checks may catch particular manifestations, but they do not make the trace status correct.

**Simplest fix within D5/D7:** Reject incomplete register structures and unresolved known-violation asset/requirement references before computing statuses. Restrict missing-register compatibility to older trees that genuinely predate register-dependent requirements. Add negative controls for missing/incomplete mappings and an unresolved violation row.

##### B1-B2 — Push mode passes expired and stale accepted gaps

**Where:** `scripts/validate_traceability.py:784`, especially the return at line 790.

**Criterion:** M2 false green and contradiction with D7’s requirement that expired and stale acceptances fail.

**Failure scenario:** A valid acceptance passes PR checks shortly before expiry. After expiry, the merge or another main push runs `--mode push`. `check_accepted_gaps` finds the expired entry, but `gap_gate` discards its failures and returns success. I reproduced the same behavior for a stale entry.

D7 exempts push-mode **coverage comparison** from enforcement; it does not exempt invalid acceptance records.

**Simplest fix within D7:** Return acceptance-validation failures in push mode while continuing to report ordinary coverage gaps without failing. Extend the existing expiry and stale-entry tests to push mode.

#### Advisory

- **B1-A1:** V5–V6 would be stronger with a failed `qa-deploy` run that writes a failed report, and a rejected report exercised through the evidence validator’s final exit path. Current helper and invocation tests can survive disconnected enforcement.
- **B1-A2:** V7 lacks a contradictory run-report fixture; V6’s “unreadable” test never creates an unreadable input. Current implementation inspection supports both behaviors, but the committed tests do not fully establish them.
- **B1-A3:** Complete Increment B’s implementation/review records and refresh verification counts after the pending E2E run, ruleset update and CI conclusions.
- **B1-A4:** Gate command matching establishes textual presence. A matching command inside an unexecuted shell branch would pass; no such case exists in the reviewed workflow.

#### Simpler alternatives

- Parse `trace/tests.yaml` once in `_load_inputs`, rather than loading it separately for metadata and test entries.
- Compute each input digest once in `deploy_report_failures`, avoiding duplicate reads without changing the acceptance rule.

#### Decision concerns

None.

#### Verdict

Approvable within the threat model: **no — B1-B1, B1-B2**.

#### Not checked

- Full pytest/shell suites, `qa-quality`, Docker-dependent checks, or E2E execution. These would write files or violate the Docker restriction.
- Live GitHub API, ruleset enforcement, or CI conclusions. External facts were supplied by the user.
- Secret contents, existing evidence/report contents, or a fresh publication-set secret scan.
- Final close-out records that the author intends to add after the running E2E suite.

Independent verification comprised read-only documentation checking, diff checks, in-memory trace computations over current and historical Git trees, planned/current-fact gate comparisons, and synthetic failure-path probes. No files were modified.
## Round 2 report (verbatim)

### Implementation review — ci-evidence-trace Increment B, round 2

#### Round-1 findings

- **B1-B1 — re-raised with new evidence.** [validate_traceability.py:592](/home/guna/projects/agentic_iam_spiffe/scripts/validate_traceability.py:592) checks that a violation’s requirement reference is nonempty, but never checks that it resolves. In an in-memory reproduction, changing K1’s reference to nonexistent `REQ-SEC-K9`, while retaining OPL-005, produces **zero structural failures**, K1 **“proved: static”**, and **no PR gap-gate failures** against the actual main-tree gaps; K1 is counted as closed. This remains an M3 false proof and D5 contradiction. Simplest fix: reject references absent from the parsed requirements and add this typo negative control. The separate deployment gate’s rejection does not correct the authoritative trace status.
- **B1-B2 — accepted.** Push mode now returns acceptance-validation failures; independently reproduced rejection of expired and stale entries.
- **B1-A1 — accepted.** Added tests cover failed/error report production and evidence-validator exit propagation; in-memory probes confirmed report verdicts and failure exits.
- **B1-A2 — accepted.** Added contradictory-report and unreadable-report controls address both omissions; permission failures reject.
- **B1-A3 — accepted for this review stage.** STATUS and implementation records contain the supplied clean-stack results. Branch CI and ruleset updates remain pending and explicitly unverified.
- **B1-A4 — accepted as non-blocking.** Matching remains lexical; inspection found no inactive gate invocation in the current workflow. Acceptance does not endorse the broader claim that every conditional-command mistake requires deliberate construction.
- **Simpler alternative: parse trace YAML once — accepted.** `_load_inputs` now shares the parsed document.
- **Simpler alternative: compute each digest once — accepted.** `deploy_report_failures` now reads each input digest once.

#### New blocking findings

None. B1-B1 remains open as re-raised above.

#### Simpler alternatives

None.

#### Decision concerns

None.

#### Verdict

Approvable within the threat model: no — B1-B1.

#### Not checked

- Full pytest/shell suites, Docker-dependent checks, services, E2E execution, or publication-set scanning.
- Live GitHub ruleset configuration, required-check enforcement, or branch CI conclusions.
- Secret contents or existing runtime evidence/report contents.

Reviewed independently by Codex, read-only and offline, through `0195a8b`. Verification included documentation and diff checks, Python syntax checks, in-memory failure probes, and trace computations over current and historical Git inputs. Normal comparison reproduced **0 new, 25 closed, 113 remaining gaps**; historical replay found all ten expected REQ-SEC gaps. No files were modified.
## Reviewer prompts (verbatim)

### Round 1

````markdown
You are the independent implementation reviewer for a change in the repository at the current
working directory. You did not write it. Review read-only: do not modify files, run docker, start
services or use the network. Never print key material, tokens or environment variable values. You
may check metadata of secret files (existence, owner, mode, readability), never their content.

## What is under review
Increment B ("trace model") of slice `ci-evidence-trace`: the commits `origin/main..HEAD`
(`git log origin/main..HEAD`, `git diff origin/main...HEAD`).

The intent it must serve is the approved plan as merged on `main`:
`docs/slices/ci-evidence-trace/plan.md` and `docs/slices/ci-evidence-trace/test_plan.md`.
Increment B covers decisions D4 to D9 (plan, "In scope", Increment B); Increment A (D1, D2, D3, D12)
is already merged. The repository rules are in `AGENTS.md`, which you must read first, in particular
"PoC scope and proportion" (threat model, blocking criteria, review loop) and "Independent review".
The plan's section "Threat model for this plan and its reviews" is the threat model you judge
against.

You may read the whole repository. Decide yourself where to look; you are not given a list of files.

## Facts outside the repository (collected by the author, 2026-10-31)
- Locally on this branch: `make qa-quality` (with `make qa-trace` in `--mode pr --base origin/main`:
  0 new gaps, 25 closed, 113 remaining), `make tooling-test` (219 pytest + 9 shell) and
  `make qa-evidence` against the Increment A run's evidence with a fresh `make qa-deploy` report
  PASSED. A full clean-stack `make e2e` is running while you review; the author adds its result to
  the records afterwards. Increment B changes no harness or service code.
- The `main` ruleset (id 26054924, readable without a token) requires: docs-check, e2e, qa-deploy,
  qa-trace, test-lint, tooling-test, unit-guard-check, unit-mutation, unit-trust. `make
  gate-consistency` therefore fails today with "gate-consistency / unit-diff-cov is not a required
  check"; the user adds both at this PR (plan review note 1).
- The CI workflow has not run on this branch yet.

## Rules for findings
- Only these block (from `AGENTS.md`): a concrete false green or an OPL-005-class miss inside the
  threat model, with a failure scenario; a contradiction (with `AGENTS.md`, a requirement, the plan
  or its decisions); an approved decision without a test. Everything else is advisory.
- Fixes must stay within the agreed decisions (D1–D12 in the plan, and `AGENTS.md`). Propose the
  simplest fix within them; prefer removing or changing an existing mechanism over adding one.
- If you think an agreed decision itself causes a problem, say so under "Decision concerns" without
  a fix; that is for the author and the user to weigh.

## Questions (answer each in depth; "n/a" needs a reason)
1. *Tests:* for each new or changed test (`tests/tools/test_trace_model.py`, `test_gate_consistency.py`,
   `test_evidence_deploy_report.py`, the additions to `test_check_docs.py` and `test_qa_deploy.py`),
   which wrong implementation would still pass it (a check that reads nothing, a gate that compares
   the wrong base, a status taken from the wrong source, a missing value read as success)? Does each
   match its row in `test_plan.md` (V4 to V12)?
2. *Keys:* does the change make a key, socket or secret reachable by a service outside its holder
   list in `security/invariants.yaml`, or put a secret into a published file or report?
3. *Intent:* does the change do what D4 to D9 say, no more and no less? Where the implementation
   differs from the plan's wording, does it still meet the decision, and is that stated in the
   repository's records? Are the success criteria 3 to 6 met?
4. *Failure behaviour:* missing, unreadable or malformed inputs (merge-base, base tree, register,
   accepted_gaps, ruleset, qa-deploy report): does each fail closed? Can a requirement be reported
   as proved while it is violated under a known violation (M3)?
5. *Ripple:* what depends on what changed (CI jobs and required checks, Makefile, `docs-check`,
   `qa-evidence`, `docs/test_spec.md`, `AGENTS.md`, records), and is each kept consistent?

## Output (markdown only)
# Implementation review — ci-evidence-trace Increment B, round 1
## Answers
(one section per question above)
## Blocking findings
Each with id (B1-B1, ...), where (file:line), the blocking criterion it meets, failure scenario,
simplest fix within the agreed decisions. "None" if none.
## Advisory
Each with id (B1-A1, ...), one or two lines.
## Simpler alternatives
Non-blocking: places where a mechanism could be removed or simplified within the agreed decisions.
"None" if none.
## Decision concerns
"None" if none.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
## Not checked
````

### Round 2

````markdown
You are the independent implementation reviewer for a change in the repository at the current
working directory, round 2. You did not write it. Review read-only: do not modify files, run docker,
start services or use the network. Never print key material, tokens or environment variable values.
You may check metadata of secret files (existence, owner, mode, readability), never their content.

## What is under review
Increment B ("trace model") of slice `ci-evidence-trace`: the commits `origin/main..HEAD`. Round 1
reviewed up to `f592d13`; the commit after it answers round 1 (`git show HEAD`).

The intent is the approved plan as merged on `main` (`docs/slices/ci-evidence-trace/plan.md`,
`test_plan.md`; Increment B = D4 to D9) and the rules in `AGENTS.md` ("PoC scope and
proportion", "Independent review"). The plan's "Threat model for this plan and its reviews" is the
threat model you judge against.

Your round-1 report and the author's answers (fixed or rejected, with reasons) are in
`docs/slices/ci-evidence-trace/review_b.md`. Judge each answer: accept it, or re-raise it with new
evidence. You may read the whole repository.

## Facts outside the repository (collected by the author, 2026-10-31)
- After the round-1 fixes: `scripts/clean_stack.sh`, `make e2e`, `make qa-evidence` were rerun on a
  clean stack; the results are in `docs/STATUS.md` "Last verification" and the implementation log.
- The CI workflow has not run on this branch yet; `gate-consistency` and `unit-diff-cov` are not yet
  required checks (the user adds them at this PR), so `make gate-consistency` fails until then.

## Rules for findings
- Only these block: a concrete false green or an OPL-005-class miss inside the threat model, with a
  failure scenario; a contradiction (with `AGENTS.md`, a requirement, the plan or its decisions); an
  approved decision without a test. From round 2 a new finding counts only if it blocks.
- Fixes must stay within the agreed decisions (D1–D12, and `AGENTS.md`); propose the simplest fix
  within them; prefer removing or changing a mechanism over adding one.
- "Simpler alternatives" and "Decision concerns" may be reported in every round; a decision concern
  is never applied by the author.

## Output (markdown only)
# Implementation review — ci-evidence-trace Increment B, round 2
## Round-1 findings
One line each (B1-B1, B1-B2, B1-A1 to B1-A4, the simpler alternatives): accepted, or re-raised with
evidence.
## New blocking findings
Each with id (B2-B1, ...), where, criterion, failure scenario, simplest fix. "None" if none.
## Simpler alternatives
"None" if none.
## Decision concerns
"None" if none.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
## Not checked
````
