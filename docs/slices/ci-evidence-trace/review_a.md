# Independent review — ci-evidence-trace Increment A

Implementation-PR review under [`AGENTS.md` — Independent review](../../../AGENTS.md#independent-review).
Reviewer: Codex CLI 0.165.0, `codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral`, run by hand; it saw
the repository, the merged plan and the change, never the author's reasoning.

| Round | Reviewed | Verdict | Findings |
| --- | --- | --- | --- |
| 1 | `origin/main..18823d6` | not approvable | A1-B1, A1-B2 (blocking); A1-A1 to A1-A4 (advisory); one simpler alternative |
| 2 | fixes in `4609e65` | **approvable within the threat model** | all round-1 answers accepted, including the three rejections; none new |

## Author answers, round 1
| Finding | Answer | Where |
| --- | --- | --- |
| A1-B1 failed publication leaves a green partial run | Fixed: publishing is all or nothing (built in a `.partial` sibling, renamed into place only when every file copied; on error the evidence directory stays empty, so `qa-evidence` fails on missing guard artifacts); the harness counts publish failures and exits non-zero at the end. | `scripts/evidence_secrets.py` `publish`; `scripts/rogue_node_tests.sh` `publish_test_evidence` and the final exit; tests `test_publish_that_fails_part_way_leaves_the_evidence_directory_empty`, `test_harness_counts_a_failed_publish_and_fails_the_run` |
| A1-B2 unlistable directory treated as a clean scan | Fixed: traversal uses `os.walk` with an error callback; an unlistable directory is a scan error (and a publish error). | `scripts/evidence_secrets.py` `_walk`; test `test_unlistable_directory_is_an_error_for_scan_publish_and_qa_evidence` |
| A1-A1 V1 checks command text; V13 stub ignores the command | V13 taken: the stub now runs the script's own cleanup command on the host path, so an ineffective command fails (checked with a no-op `find`). V1 rejected: a non-root test cannot create root-owned files to observe `chown`; the ownership effect is proven by the local run and the CI `e2e` job, where `qa-evidence` writes `artifacts/quality/` after `make e2e`. | `tests/tools/test_clean_stack.py` |
| A1-A2 strengthen UT-236 and UT-350 | UT-350 taken: it asserts the new `root_key.pem` holds a PEM private key. UT-236 rejected: the function never reads the cached key; it generates a new pair and, on `FileExistsError`, loads the file, so returning the generated key instead of the file's would already fail the "existing key loaded" outcome. | `tests/unit/capiss/test_utils.py` UT-350 |
| A1-A3 run every V2 shape through `qa-evidence` | Rejected: `qa-evidence` calls the same `scan` function; every shape is tested on `scan`, and the `qa-evidence` path is tested with a token in each of the three publication-set locations and with an unlistable directory. A per-shape copy adds no failure the existing tests miss. | — |
| A1-A4 report rescan can disagree with `secret_findings` | Fixed by removal: the report is no longer rescanned. Every value in it is copied from evidence files already scanned, so the rescan could only disagree with the saved `secret_findings` that CI's upload decision reads. | `scripts/validate_e2e_evidence.py` |
| Simpler alternative: upload only when `qa-evidence` succeeds | Not taken: it would drop the evidence of failed runs, which is what a failed CI run needs for diagnosis. With A1-A4 fixed, the report's `secret_findings` is complete, and the upload stays gated on it. | — |

## Round 1 report (verbatim)

### Implementation review — ci-evidence-trace Increment A, round 1

#### Answers

##### 1. Tests

Reviewed by Codex as the independent reviewer in a read-only sandbox. Scope: commits `7d33d88` and `18823d6`, compared with the approved plan and test plan read from `origin/main`.

**The tests cover the intended successful paths, but two failure paths can still produce green results: partial evidence publication and unreadable directory traversal.** These are A1-B1 and A1-B2 below.

HTTP status, denial reason and responding-component distinctions are not applicable to the new unit and tooling tests: they exercise functions, files, command orchestration and workflow configuration. They do not establish service availability. The harness diff changes evidence handling and printed evidence paths; it leaves the existing premise, exercise and outcome assertions unchanged.

###### Unit tests

All four new tests have guard phases, DD-111 traceability and the `invariant` marker.

| Test | What it establishes | Wrong implementation that could still pass |
| --- | --- | --- |
| **UT-035** | Creation, reload of the same key, and public-key update detection. The changed helper points it at `root_key.pem`. | A mutually compatible writer and reader using the wrong encoding or mode could pass this test alone. UT-347 supplies the independent encoding and mode checks. |
| **UT-236** | The `FileExistsError` branch returns the previously created key and reports `created=False`. | Returning `ROOT_PRIVATE_KEY` instead of reading the competing creator’s file could pass: the test explicitly sets that cache to the expected key. It also does not exercise malformed content on the race path. |
| **UT-347** | Independent PKCS#8 parsing, Ed25519 identity, matching private bytes, mode `0600`, public-key export, token signature verification and absence of a newly written legacy file. | A predictable signing key would pass; randomness is not tested. Also, the test overrides the production path, so its filename assertion cannot detect an incorrect production filename constant. Neither defect is present in the implementation reviewed. |
| **UT-348** | An independently encoded existing key is loaded with `created=False`, preserving its bytes. | Rewriting identical bytes could pass. Returning a newly generated or different cached key would fail. Empty content cannot satisfy the independent-key comparison. |
| **UT-349** | Seven malformed formats raise `ValueError`, preserve the input and leave no additional files. | An implementation rejecting every input would pass this negative test alone, but UT-347/348 reject that implementation. Empty and unreadable files are not explicit parameters. The approved outcome requires rejection, not a particular exception message. |
| **UT-350** | A legacy file is not reused as the signing key and remains unchanged. | Reading and discarding the legacy file would pass. Returning a fresh in-memory key without persisting the new PEM file would also pass this test: it does not assert the PEM file exists. |

Together, these substantially match the approved D12 unit-test list. The actual implementation uses the correct production filename, independently valid encoding and a shared parser for ordinary loads and race loads. The surviving implementations above are test-strength limitations, rather than demonstrated runtime defects.

###### Tooling tests

The table covers every new test function and the directly changed deployment-inventory test.

| Test or parameter group | Assessment and surviving wrong implementation |
| --- | --- |
| **V1 — `test_e2e_builds_runs_the_suite_and_takes_ownership`** | Checks reset/build/run/chown command ordering and important arguments. It does **not** establish actual ownership or the ability to create `artifacts/quality/`: Docker is a logging stub. Building only a subset of images, or an ineffective inner cleanup/ownership command retaining the checked text, could pass. Partial match to V1. |
| **V1 — `test_failed_suite_fails_the_target`** | Injects suite exit 1, requires target failure, checks the reported suite code and confirms ownership is attempted. It does not cover other suite codes or verify ownership effects. |
| **V1 — `test_failed_build_or_ownership_fails_the_target`** | Separate reset, build and ownership failures must produce nonzero results and their specific diagnostic. This prevents an unrelated failure from satisfying the test merely through its exit status. |
| **V2 — `test_each_secret_shape_is_found`** | All eleven fixtures require the corresponding finding kind. Covers text/JSON tokens, PEM, encoded PEM, both DER key types, credential lines and Atlassian tokens. These are scanner tests; only token fixtures also exercise the full validator. |
| **V2 — `test_finding_names_file_and_kind_never_the_value`** | Requires a readable file to be scanned, its path and kind to appear, and selected secret fragments to stay absent. It checks selected ends of the fixture, so disclosure of an unchecked middle fragment could escape the assertion. Actual finding objects contain no matched content. |
| **V2 — `test_accepted_shapes_pass`** | Covers fingerprints, certificates, correlation IDs, repeated padding and credential placeholders. A scanner rejecting everything would fail these positive controls. |
| **V2 — `test_token_shape_boundaries`** | Checks all five planned length/distinct-character boundaries. Correctly tests the agreed shape rule rather than only a typical long token. |
| **V2 — `test_scan_opens_no_file_outside_the_publication_set`** | Requires at least one open and confines recorded opens to the fixture publication tree. A scanner opening only one harmless file could still pass; complete traversal is not established. No symlink case is included. |
| **V2 — `test_unreadable_file_fails_closed`** | Covers an enumerated, unreadable regular file; skipped for root. It misses files hidden behind an unlistable directory: **A1-B2**. |
| **V2 — `test_qa_evidence_passes_a_clean_run`** | Supplies a positive control with guard artifacts and a matching PASS/report summary. Empty guard stdout can pass, appropriately: successful quiet commands produce empty guard captures. It does not validate arbitrary outcome-file contents independently of the harness. |
| **V2 — `test_qa_evidence_fails_on_a_token_anywhere_in_the_publication_set`** | All three locations require exit 1, the token finding kind and target path, and absence of the token from diagnostics and the generated report. An unrelated validation failure alone cannot pass. Matches the whole-set token cases. |
| **V2 — `test_makefile_qa_evidence_uses_the_publication_set`** | Checks the definition, validator argument and printed set. An unused occurrence of the expected argument text could satisfy the textual assertion, although the actual recipe invokes it correctly. |
| **V2 — `test_publish_replaces_tokens_with_fingerprints`** | Checks exact fingerprint replacement in text, JSON and binary data, preserved certificates and status/reason text, recursive copying, and a clean destination scan. Missing or empty expected files fail. It omits publication failures. |
| **V2 — `test_publish_cli_and_same_token_same_fingerprint`** | Requires successful CLI execution, matching replacements and removal of the original token. Alone, a constant replacement could pass; the preceding test checks the actual SHA-256 result. |
| **V2 — `test_ci_uploads_exactly_the_checked_set_and_only_after_the_check`** | Checks step ordering, shared path output and the upload condition. It checks configuration text, not execution of the report-based approval step or failure propagation. |
| **V3 — exact compose/register tags** | Requires equality and a full version tag for both images. Missing values, `latest` and partial versions fail. Image availability is outside this static test; the supplied local inspection/run facts support the selected versions. |
| **V3 — floating-tag parameters** | Rejects all four listed floating/missing-tag examples. Tests the predicate rather than a complete repository fixture. |
| **V3 — differing compose/register tag** | Requires an image-related deployment error for mismatched exact tags. An unrelated deployment error cannot satisfy it. Matches V3. |
| **V13 — `test_clean_stack_empties_capiss_keys`** | Checks all three synthetic files disappear and the directory remains. However, the stub deletes files whenever it sees the mount, regardless of the container command. An inert command with the same mount could pass. |
| **V13 — failed removal** | Requires the warning, unsuccessful cleanup flag and retained filenames. V13 requires reporting, so a warning without nonzero exit is consistent with this row. |
| **V13 — `--check`** | Requires no Docker invocation and retained file count. Rewriting file contents without changing the count could pass. The actual check returns before cleanup. |
| **Changed `test_secrets_configs_and_volumes_from_are_inventoried`** | Follows the renamed key path and still checks the secret/config mounts, `volumes_from` privilege and specifically a K1 exposure to `mock`. Other deployment tests inherit the renamed fixture asset without changed assertions. |
| **Diff-coverage regression test** | Establishes that both service patterns reach one `--include`, rejecting the previous argument bug. It does not run a below-threshold coverage fixture, so a separate threshold-propagation defect could pass. The current script retains `pipefail`. |

V2 does not literally run every secret-shape fixture through `qa-evidence`, as its row specifies. Shared scanner integration currently handles those findings uniformly, so this is advisory. More materially, neither the publication tests nor V1 exercise a publisher that fails **after** copying sufficient guard files.

I ran the 22 in-memory shape, positive-control and boundary cases successfully. I did not run filesystem-writing pytest suites.

##### 2. Keys

**I found no newly exposed registered service.**

The compose and register changes pin OPA/Redis images and rename K1’s location. They add no service mount, credential environment variable, network or holder. Dockerfiles are unchanged; their explicit `COPY` instructions do not introduce a key-directory copy. The capiss implementation writes the new PEM inside the existing key mount.

The existing exposures remain:

- K1 reaches the services recorded under OPL-005 through the directory mount.
- K2 and K4 retain the recorded OPL-006/OPL-008 exposures.
- `rogue-tests` retains its declared repository and Docker-socket access.

The cleanup and ownership helper containers receive mounts needed for the approved D12/D1 operations; they do not add a persistent service holder.

On normal successful publication, token handoffs remain in container-local scratch, and published token-shaped values become fingerprints. Guards inspect the original scratch contents before redaction, preserving the existing audit non-disclosure assertions.

The secret scanner covers the three publication roots and reports finding metadata rather than matched values. **I cannot conclude that every published file is checked**, because of A1-B2. I also did not inspect live evidence or secret-file contents. Consequently, the supplied “no secret findings” result remains author-provided evidence, not an independent content audit.

##### 3. Intent

| Decision | Implementation assessment |
| --- | --- |
| **D1** | Adds the shared publication-set variable, `make e2e`, complete image build, explicit suite exit-code selection, ownership recovery and the CI job. The job runs inspected `qa-deploy`, then `qa-evidence`, with a 14-day upload. Required-check configuration and the branch’s CI run remain pending external actions. |
| **D2** | Compose and register consistently use `openpolicyagent/opa:1.13.2` and `redis:7.4.8-alpine`. Matches the exact-tag decision. |
| **D3** | Uses a central scratch-to-publication transformation rather than individually rewriting every token handoff. This preserves the decision’s observable behavior and is explicitly recorded in the implementation log. Failure handling is incomplete: A1-B1 and A1-B2. |
| **D12** | Uses `root_key.pem`, PKCS#8 Ed25519 encoding and mode `0600` on creation. Existing invalid content raises without regeneration; legacy content is not read. Cleanup empties the key directory. Matches the approved decision. |

D4–D9 functionality is appropriately absent. In particular, the inspected deployment report’s digest binding and validation belong to Increment B.

The diff-coverage repair and stacking rule are additional corrective work, recorded under DPL-009 and DPL-008. Moving OPL-005’s filename update forward from B keeps the current record accurate alongside D12. None changes runtime authorization behavior.

##### 4. Failure behaviour

| Input or failure | Result |
| --- | --- |
| **Absent private key** | Creates a fresh key using exclusive creation. |
| **Unreadable, empty or malformed existing private key** | Read/parse errors propagate during module initialization; capiss does not regenerate over it. The concurrent-reader branch uses the same parser. |
| **Missing evidence directory or required guard artifacts** | Validator fails. |
| **Missing, unreadable or malformed test report** | Missing statuses/summary fail validation; read errors terminate nonzero. |
| **Unreadable enumerated publication file** | Scanner records an error and validation fails. |
| **Unlistable publication directory** | Can be silently omitted: **A1-B2**. |
| **Missing publication root** | Scanner silently skips it. Required evidence/report paths are checked separately; missing optional quality output can therefore be created afterward. Absence alone is not proof that a complete set was scanned. |
| **Failed reset, build, suite or ownership recovery** | `make e2e` fails. CI does not suppress that failed step. |
| **Failed evidence publication** | Logged and swallowed; partial publication can pass subsequent validation: **A1-B1**. |
| **Missing/malformed upload-approval report or nonempty findings** | The approval step fails and upload is withheld. |
| **Failed artifact upload** | The CI step/job fails; there is no `continue-on-error`. |

**Can stale evidence pass `make qa-evidence`? Yes, when invoked alone.** Freshness checking defaults to disabled, and the validator does not bind a run to a commit. The new runner removes prior suite evidence and the report before building, which addresses the ordinary never-started-run case. If that removal itself fails, the target fails, but old evidence may remain available to a separately invoked validator.

A fresh partial publication can also pass, as A1-B1 demonstrates. Neither the provided 120/120 run nor the clean secret-shape controls exercise that path.

##### 5. Ripple

The main dependencies are kept aligned:

- **CI and Makefile:** the new job uses the shared E2E runner and publication-set definition. Existing standalone gates remain.
- **Key consumers:** capiss alone changes its private-key format; consumers retain the unchanged public-key filename and format.
- **Deployment register:** image references and K1 location follow the implementation; holder lists and known violations remain unchanged.
- **`qa-deploy`:** its validation logic is unchanged. Fixture updates preserve key-exposure detection. Its richer report contract remains B work.
- **Test specification:** the global publication explanation and affected token/mint-response evidence entries describe fingerprints. Harness assertion behavior is unchanged.
- **Traceability:** new unit tests link to DD-111. Deferral of REQ-T-R9/static-test entries follows D11. The existing M4-focused unit specification does not require a new requirement row here.
- **Records:** STATUS, slice index, architecture and implementation history reflect Increment A. OPL-010 records the startup failure; DPL-009 records the coverage-filter repair.

The implementation history describes the central-publication departure from the plan’s more literal handoff-edit wording. That departure is reviewable and consistent with D3’s intent.

#### Blocking findings

##### A1-B1 — Failed evidence publication can leave a green partial run

**Where:** [scripts/rogue_node_tests.sh:237](/home/guna/projects/agentic_iam_spiffe/scripts/rogue_node_tests.sh:237), with PASS recorded earlier at line 188.

**Blocking criterion:** Concrete false green under M10; a tooling failure is swallowed.

**Failure scenario:** The publisher copies the command, premise, exercise and outcome files, then encounters an I/O error copying a later file. The harness logs the error, deletes scratch and continues with the already recorded PASS. The validator checks guard-file presence and report status; it neither requires the missing later file nor rejects the publication-error line. A clean partial destination can therefore pass `qa-evidence`.

Read-only probes confirmed that a failed publisher returns **0**, its error line leaves the parsed status **PASS**, and a partial copy containing the four required artifact categories produces no artifact-presence failures.

**Simplest fix:** Replace log-and-continue with a fatal nonzero exit on publication failure. Add a negative control where publication fails after copying the required guard artifacts; the run and subsequent evidence validation must fail.

##### A1-B2 — Unreadable directory traversal is treated as a clean scan

**Where:** [scripts/evidence_secrets.py:119](/home/guna/projects/agentic_iam_spiffe/scripts/evidence_secrets.py:119), consumed by `scan` at line 137.

**Blocking criterion:** Contradicts the approved fail-closed unreadability contract and permits a false-green secret check under M6.

**Failure scenario:** A publication subtree is unlistable to the checking user and contains an unreadable secret-bearing file. `Path.rglob()` suppresses the directory permission failure, so `_files()` omits the subtree. No file reaches `_read()`, and the scanner returns no error. With otherwise valid suite evidence, `qa-evidence` can report success without checking that subtree.

A read-only probe injecting a directory-listing `PermissionError` returned **zero findings and zero errors**. The existing unreadable-file test does not cover this case.

**Simplest fix:** Replace the silent traversal with traversal that reports directory-listing/stat failures as scan errors. Add an inaccessible nested-directory fixture and require `qa-evidence` to fail.

#### Advisory

- **A1-A1:** V1 verifies ownership-command text, not ownership effects or quality-directory creation. V13’s stub removes files based only on the mount, allowing an ineffective cleanup command to pass.
- **A1-A2:** Strengthen UT-236 with a competing on-disk key different from the cached key; strengthen UT-350 by asserting that the new PEM file exists and recording forbidden legacy-file opens.
- **A1-A3:** Parameterize the full `qa-evidence` negative control over every V2 secret shape, matching the approved row more directly.
- **A1-A4:** The generated-report rescan adds failures after `secret_findings` and the summary have been written. The saved report can therefore disagree with the process result used by reviewers and CI’s report-based upload approval.

#### Simpler alternatives

If failed-run artifact uploads are unnecessary, condition upload directly on a successful `qa-evidence` step. This removes the report-content approval check while retaining the shared publication-set definition and satisfying D1’s upload restriction.

#### Decision concerns

None.

#### Verdict

Approvable within the threat model: no — A1-B1, A1-B2.

#### Not checked

- No Docker commands, services, network access or filesystem modifications.
- No secret-file or live evidence contents inspected.
- Full tooling/unit suites, clean-stack E2E, mutation testing and actual image users were not independently rerun. Their stated results are author-provided facts.
- The branch’s CI execution and required-check update remain unverified and, per the supplied facts, pending.
- Verification performed: source/diff review, parsing nine changed Python files, shell syntax checks, 22 passing in-memory shape cases, and read-only failure-path probes.
## Round 2 report (verbatim)

### Implementation review — ci-evidence-trace Increment A, round 2

Reviewer: Codex, independent read-only review of `origin/main..4609e65`, against the approved plan and test plan on `origin/main`.

#### Round-1 findings

- **A1-B1 — accepted:** publication stages files before renaming; copy errors propagate, and the harness exits nonzero on publication failure. In-memory probes confirmed both failure paths.
- **A1-B2 — accepted:** directory-listing errors reach the scanner and prevent publication; the added regression test also exercises `qa-evidence`.
- **A1-A1 — accepted:** V13 now executes the cleanup command. V1’s ownership assertion remains indirect; accepting that limitation is proportionate given the supplied successful stack run.
- **A1-A2 — accepted as advisory:** UT-350 now checks persistence. UT-236’s cached-key blind spot remains, but the implementation reads the competing creator’s file; no blocking defect was demonstrated.
- **A1-A3 — accepted:** per-shape scanner tests plus validator integration tests cover the shared mechanism adequately.
- **A1-A4 — accepted:** removing the generated-report rescan eliminates the identified disagreement between the saved `secret_findings` and the process result.
- **Simpler alternative — accepted as declined:** retaining secret-free failed-run evidence serves diagnosis and remains within D1.

#### New blocking findings

None.

#### Simpler alternatives

None.

#### Decision concerns

None.

#### Verdict

Approvable within the threat model: yes

#### Not checked

- No files modified, Docker commands run, services started, or network accessed. No secret-file or live evidence contents inspected.
- Full tooling, unit, mutation and clean-stack E2E suites were not independently rerun. The supplied runtime results remain author-provided evidence.
- The branch’s CI execution and required-check configuration remain pending, as stated in the supplied facts.
- Independent verification comprised source/diff review, parsing nine changed Python files, syntax checks on four changed shell scripts, 22 passing in-memory shape/control cases, and mocked traversal, partial-publication and harness-exit probes.
## Reviewer prompts (verbatim)

### Round 1

````markdown
You are the independent implementation reviewer for a change in the repository at the current
working directory. You did not write it. Review read-only: do not modify files, run docker, start
services or use the network. Never print key material, tokens or environment variable values. You
may check metadata of secret files (existence, owner, mode, readability), never their content.

## What is under review
Increment A ("CI evidence") of slice `ci-evidence-trace`: the commits `origin/main..HEAD`
(`git log origin/main..HEAD`, `git diff origin/main...HEAD`).

The intent it must serve is the approved plan as merged on `main`:
`docs/slices/ci-evidence-trace/plan.md` and `docs/slices/ci-evidence-trace/test_plan.md`.
Increment A covers decisions D1, D2, D3 and D12 (plan, "In scope", Increment A); D4 to D9 are
Increment B and are not expected here. The repository rules are in `AGENTS.md`, which you must read
first, in particular "PoC scope and proportion" (threat model, blocking criteria, review loop) and
"Independent review". The plan's section "Threat model for this plan and its reviews" is the threat
model you judge against.

You may read the whole repository. Decide yourself where to look; you are not given a list of files.

## Facts outside the repository (collected by the author, 2026-10-31)
- Local runs on this branch: `scripts/clean_stack.sh` then `make e2e`: the first attempt never
  started the suite (the SPIRE agent exited with "bundle not found"; recorded as OPL-010); after a
  second clean, 120/120 passed. Then `make qa-deploy` (image users inspected) PASSED, `make
  qa-evidence` PASSED (validated 119, skipped 1, no secret findings), `make qa-quality`,
  `make tooling-test`, `make unit-trust`, `make unit-diff-cov BASE_REF=origin/main` PASSED.
  `make unit-mutation` was not run locally.
- The CI workflow has not run on this branch yet. The `main` ruleset requires docs-check, qa-trace,
  unit-guard-check, tooling-test, test-lint, qa-deploy, unit-mutation, unit-trust; `e2e` is not yet
  required (the user adds it at this PR, plan review note 1).
- The rogue-tests image is `docker:27.0.3-cli` with python3 installed; the repository is mounted at
  `/repo` and `artifacts/rogue-tests` at `/tmp/rogue-tests` in that container.

## Rules for findings
- Only these block (from `AGENTS.md`): a concrete false green or an OPL-005-class miss inside the
  threat model, with a failure scenario; a contradiction (with `AGENTS.md`, a requirement, the plan
  or its decisions); an approved decision without a test. Everything else is advisory.
- Fixes must stay within the agreed decisions (D1–D12 in the plan, and `AGENTS.md`). Propose the
  simplest fix within them; prefer removing or changing an existing mechanism over adding one.
- If you think an agreed decision itself causes a problem, say so under "Decision concerns" without
  a fix; that is for the author and the user to weigh.

## Questions (answer each in depth; "n/a" needs a reason)
1. *Tests:* for each new or changed test (unit tests UT-347 to UT-350 and the changed UT-035/UT-236;
   tooling tests in `tests/tools/`), which wrong implementation would still pass it (a service down,
   another status, the right status with another reason, another component answering, a missing
   value or empty file read as success, a check that scans nothing)? Does each test match its row
   in `test_plan.md` (V1, V2, V3, V13 and the unit-test list)?
2. *Keys:* does the change make a key, socket or secret reachable by a service outside its holder
   list in `security/invariants.yaml`, through a compose mount, an env var, a Dockerfile `COPY`, an
   entrypoint or script that copies or writes it, or a shared volume? Does any token value, private
   key or credential still reach a published file (`test_report.log`, `artifacts/rogue-tests/`,
   `artifacts/quality/`) or the CI upload?
3. *Intent:* does the change do what D1, D2, D3 and D12 say, no more and no less? Where the
   implementation differs from the plan's wording, does it still meet the decision, and is the
   difference stated in the repository's records?
4. *Failure behaviour:* missing, unreadable or malformed inputs (key file, evidence files, the
   report, the publication set, a failed build or suite, a failed publish step): does each fail
   closed? Can a stale or partial run pass `make qa-evidence`?
5. *Ripple:* what depends on what changed (CI jobs, Makefile targets, `docs/test_spec.md`, the
   register, `qa-deploy`, docs and records), and is each kept consistent?

## Output (markdown only)
# Implementation review — ci-evidence-trace Increment A, round 1
## Answers
(one section per question above)
## Blocking findings
Each with id (A1-B1, ...), where (file:line), the blocking criterion it meets, failure scenario,
simplest fix within the agreed decisions. "None" if none.
## Advisory
Each with id (A1-A1, ...), one or two lines.
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
Increment A ("CI evidence") of slice `ci-evidence-trace`: the commits `origin/main..HEAD`. Round 1
reviewed up to `18823d6`; the commit after it answers round 1 (`git show HEAD`).

The intent is the approved plan as merged on `main` (`docs/slices/ci-evidence-trace/plan.md`,
`test_plan.md`; Increment A = D1, D2, D3, D12) and the rules in `AGENTS.md` ("PoC scope and
proportion", "Independent review"). The plan's "Threat model for this plan and its reviews" is the
threat model you judge against.

Your round-1 report and the author's answers (fixed or rejected, with reasons) are in
`docs/slices/ci-evidence-trace/review_a.md`. Judge each answer: accept it, or re-raise it with new
evidence. You may read the whole repository.

## Facts outside the repository (collected by the author, 2026-10-31)
- After the round-1 fixes: `scripts/clean_stack.sh`, `make e2e`, `make qa-evidence` were rerun on a
  clean stack; the results are in `docs/STATUS.md` "Last verification" and the implementation log.
- The CI workflow has not run on this branch yet; `e2e` is not yet a required check (the user adds
  it at this PR).

## Rules for findings
- Only these block: a concrete false green or an OPL-005-class miss inside the threat model, with a
  failure scenario; a contradiction (with `AGENTS.md`, a requirement, the plan or its decisions); an
  approved decision without a test. From round 2 a new finding counts only if it blocks.
- Fixes must stay within the agreed decisions (D1–D12, and `AGENTS.md`); propose the simplest fix
  within them; prefer removing or changing a mechanism over adding one.
- "Simpler alternatives" and "Decision concerns" may be reported in every round; a decision concern
  is never applied by the author.

## Output (markdown only)
# Implementation review — ci-evidence-trace Increment A, round 2
## Round-1 findings
One line each (A1-B1, A1-B2, A1-A1 to A1-A4, the simpler alternative): accepted, or re-raised with
evidence.
## New blocking findings
Each with id (A2-B1, ...), where, criterion, failure scenario, simplest fix. "None" if none.
## Simpler alternatives
"None" if none.
## Decision concerns
"None" if none.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
## Not checked
````
