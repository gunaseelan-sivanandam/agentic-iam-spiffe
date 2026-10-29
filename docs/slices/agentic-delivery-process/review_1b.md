# Independent review — Increment 1B

Implementation-PR review under D17/D20 and the [AGENTS.md PoC rules](../../../AGENTS.md#poc-scope-and-proportion).
Part A asked the slice's two questions (tests, keys); part B tried the eight generic questions
proposed as slice 2 input ([`later_slices.md`](later_slices.md), "Review template"). Reviewer: Codex
CLI 0.142.5, `codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral`, run by hand; it saw the
repository and its own earlier report, never the author's reasoning.

| Round | Reviewed | Verdict | Findings |
| --- | --- | --- | --- |
| 1 | `main..ce465a8` | not approvable | C1–C4 (blockers); 3 advisories |
| 2 | fixes in `540691e` | **approvable within the threat model** | C1–C4 closed; none new |

## Resolutions
| Finding | Fix |
| --- | --- |
| C1 compose `secrets`, `configs` and `volumes_from` were not inventoried, so a key granted through them was invisible | secrets and configs count as read-only mounts of their source file; `volumes_from` is a privilege; negative controls go through the inventory extraction |
| C2 an explicit `image` on a build service was ignored | kept in the image fact and used for the USER inspection |
| C3 the baseline said "no key copies", but the harness exports workload SVIDs and keys into `tmp_svid/` (the first pass left the harness out of the search) | baseline record corrected; `tmp_svid` registered as a K7 location only `rogue-tests` may reach, applying the user's holder decision for `rogue-tests` with the same reason; REQ-SEC-K7 says so |
| C4 a test-only holder could lose its `tests` profile unnoticed | `profiles` are part of every service's allowlist |
| Advisory: status, slice index and history not updated | updated in this PR |
| Advisory: malformed register shapes raise tracebacks | left: the check still exits non-zero |
| Advisory: the malformed-compose test passes trivially without Docker | left: Docker is present locally and in CI, where the real path runs |

**Trial of the generic questions (part B).** Questions 6 and 7 found the missing status and history
updates; question 2 found the false baseline claim (C3) that the slice's two questions alone would
have reached only through the key question. That is evidence for slice 2's template decision.

## Round 1 report (verbatim)

### Independent review — Increment 1B

#### A1. Tests

**45 cases passed; five Docker-dependent cases were excluded.** The requirement/register holder consistency check passes. A separate read-only examination of historical YAML confirms the K1 mount into `tool-b`.

The table covers every test function in `tests/tools/test_qa_deploy.py`; names omit the `test_` prefix.

| Plan | Tests | Wrong input or failure that could still pass |
|---|---|---|
| T-8 | `inventory_extracts_every_fact_and_no_env_values` | Extracted fields match exactly, including exclusion of the dummy token value. Unexamined compose fields disappear: alternative mount mechanisms, explicit image alongside build, and profiles. C1, C2, C4. |
| T-8 | `live_inventory_covers_every_profile` | Checks four representative services, rather than every service. It could pass while another service is omitted. Other allowlist checks provide additional coverage. Not executed here. |
| T-8 | `compose_config_failure_is_an_error` | Missing Docker satisfies the expected exception without exercising malformed-compose handling. Empty output and invalid JSON have implementation guards but no direct fixtures. Not executed here. |
| T-9 | `matching_register_passes` | A positive control for the allowlist comparison only; does not establish asset confinement or non-root behavior. Appropriate scope. |
| T-9 | `each_unregistered_fact_fails` | Covers the listed changes to constructed `Service` objects. It still passes if compose extraction silently drops the offending fact. C1 and C2. |
| T-9 | `mount_mode_change_fails`, `docker_socket_mount_is_a_mount_fact` | Correctly reject constructed mount differences; neither exercises extraction of alternative mount mechanisms. C1. |
| T-9 | `unregistered_service_and_stale_entry_fail` | Both directions are asserted. No wrong input identified within its stated scope. |
| T-10 | `asset_reached_by_ancestor_mount_and_env_and_container_path` | Exact expected violation set is asserted. Grants through `secrets`, `configs` or `volumes_from` remain invisible upstream. C1. |
| T-10 | `historical_compose_reports_signing_key_in_tool_b` | Asserts the required historical pair. Matches T-10; not executed through Compose here. |
| T-10 | `current_compose_reports_exactly_the_known_violations` | Compares against the register’s current exception tuples, rather than independently pinning the approved list. It also excludes runtime key copies. C3. Not executed here. |
| T-10 | `removing_a_known_violation_row_fails` | Starts with no exception instead of removing each actual row. It proves an uncovered tuple fails, which exercises the relevant matching rule. |
| T-11 | `grandfathered_root_warns_until_expiry` | Checks warnings and errors across the exact deadline. Matches the plan. |
| T-11 | `new_service_cannot_be_grandfathered` | Tests attempted grandfathering of a new service; ordinary forbidden-root handling is covered separately. |
| T-11 | `locked_service_running_as_root_or_unknown_fails`, `locked_service_as_non_root_passes` | Cover root spellings, unreadable user and a non-root positive control. Match the planned policy cases. |
| T-11 | `effective_user_prefers_compose_user_over_image` | Correct helper precedence, but mocked image lookup cannot catch inspection of the wrong image in `run()`. C2. |
| T-12 | `consistent_register_passes`, `widened_holders_without_requirement_change_fails`, `requirement_without_asset_and_asset_without_requirement_fail` | Cover the stated requirement/asset and holder-set comparisons. They do not prove the declared locations describe every actual key location. C3. |
| T-13 | `matching_known_violation_is_reported_as_known` | Requires no errors and a known-violation report. Matches the plan. |
| T-13 | `invalid_or_mismatched_known_violation_fails` | Covers missing expiry/services, another asset/service, closed and unknown OPLs. Missing OPL/asset fields are not separately exercised. |
| T-13 | `known_violation_expiry_boundary`, `opl_status_parsing` | Exact expiry boundary and representative status parsing are covered. No wrong input identified within those fixtures. |
| Integration | `repository_deployment_passes_with_known_violations_only` | Requires exit zero, PASS and OPL-005, but does not independently assert all expected known violations or warnings. Uses the approved image-inspection skip. Not executed here. |

For **`qa-deploy` itself**, offline probes using normalized compose-shaped input reproduced zero errors after adding a secret-file grant, adding inherited issuer mounts, specifying an unregistered image alongside `build`, or removing the harness’s test profile. These are C1, C2 and C4. The unchanged simulated baseline produced 18 known violations.

#### A2. Keys

The diff changes no runtime mounts, entrypoints or Dockerfiles. The added `rogue-tests` holders for K1, K2, K4, K5 and K6 match the user decision recorded in the implementation notes.

However, the baseline statement that there are no additional key copies is false: existing harness helpers export workload private keys and write SVID keys under repository-backed `tmp_svid`. That contradicts the newly authored K7 confinement claim; the recorded holder decision does not include K7. See C3.

No real secret literal was identified in the reviewed diff. The test token is synthetic. Existing harness operations record private-key files; their contents were not read.

#### B. Generic questions

1. **Intent:** The Python implementation, grouped exceptions, harness holders and CI image-inspection skip match recorded decisions. C1–C4 prevent it from delivering the approved confinement and default-deny claims completely.

2. **Claims and evidence:** T-8–T-13 provide useful negative controls, but many begin after extraction. Their proof can hold while compose grants are omitted. The baseline claim is directly contradicted by harness source.

3. **Design and quality:** One Python script is proportionate and readable, with clear separation between extraction and checks. The main weakness is treating a partial inventory as complete.

4. **Failure and change:** Missing Docker, failed compose commands, invalid JSON and no services produce errors. Missing image-user information counts as root locally, subject to the approved grace period; CI deliberately skips it. Some malformed register shapes produce uncaught exceptions, but fail nonzero.

5. **Rules and new risks:** No new runtime authority is introduced. The newly authoritative K7 requirement disagrees with existing behavior, and test-only holder restrictions are not checked.

6. **Ripple:** Makefile and CI integration are present. `docs/STATUS.md`, the slice index and implementation history still describe 1B as pending or omit its completion and validation.

7. **Durability:** Decisions and deviations are recorded in tracked files. Completion and validation evidence still need the normal durable closeout entry.

8. **Blind spots:** This review establishes source behavior and offline checker results, not actual Compose normalization, built-image users or runtime confinement.

#### Blocking findings

**C1 — Alternative mount mechanisms bypass both checks.**  
Where: [scripts/qa_deploy.py:132](../../../scripts/qa_deploy.py), [scripts/qa_deploy.py:160](../../../scripts/qa_deploy.py).  
Failure scenario: grant `jira-mcp-mock` a Compose secret sourced from `capiss_keys/root_key.b64`, or add `volumes_from: [capability-issuer:ro]`. Neither reaches the inventory, so the unchanged register passes while a non-holder receives K1. Offline probes reproduced both. Compose `configs` have the same omission.  
Smallest fix: reject currently unused `secrets`, `configs` and `volumes_from` grants, or resolve them into checked mount facts. Add negative controls through `inventory_from_config`, rather than constructing `Service` objects.

**C2 — An explicit image is ignored whenever build exists.**  
Where: [scripts/qa_deploy.py:125](../../../scripts/qa_deploy.py), [scripts/qa_deploy.py:405](../../../scripts/qa_deploy.py).  
Failure scenario: add an unregistered `image` to an existing build service. Its registered image fact remains unchanged, and local inspection targets the generated project/service image instead of the explicit runtime reference. The offline allowlist probe remained green.  
Smallest fix: retain and check both explicit image and build facts; inspect the explicit image when provided. Test extraction and inspection-reference selection.

**C3 — The clean baseline and K7 claim contradict existing key exports.**  
Where: [test_plan.md:140](../../../docs/slices/agentic-delivery-process/test_plan.md), [docs/requirements.md:322](../../../docs/requirements.md).  
Failure scenario: `prepare_toolb_material` exports the Envoy private key into the harness ([scripts/rogue_node_tests.sh:1006](../../../scripts/rogue_node_tests.sh)); `prepare_client_material` writes SVID material into repository-backed `tmp_svid` and copies its private key ([scripts/rogue_node_tests.sh:1122](../../../scripts/rogue_node_tests.sh), [scripts/rogue_node_tests.sh:1167](../../../scripts/rogue_node_tests.sh)). K7 says keys remain inside their workload containers, while the baseline reports no additional copies.  
Smallest fix: correct the baseline record and resolve the existing exports against K7—either remove them or record an explicitly approved test-only accommodation with matching requirement/register coverage and a test.

**C4 — Test-only authority can move into the default deployment unnoticed.**  
Where: [scripts/qa_deploy.py:160](../../../scripts/qa_deploy.py), [docs/requirements.md:331](../../../docs/requirements.md).  
Failure scenario: remove `profiles: [tests]` from `rogue-tests`. The checker remains green although the Docker-socket-holding harness now starts with the default deployment, contradicting its declared test-only accommodation. An offline probe reproduced this. No test checks that restriction.  
Smallest fix: retain and validate profile restrictions for declared test-only services, with a negative fixture removing the restriction.

#### Advisory (at most five)

- Update the existing status, slice-index and implementation-history entries with 1B’s result and validation.
- Validate register collection shapes to produce concise errors instead of tracebacks; current failures remain nonzero.
- The malformed-compose test can pass because Docker is absent. Add a mocked command-result fixture that proves the intended failure path.

#### Verdict

Approvable within the threat model: no — C1, C2, C3, C4.

#### Not checked

Docker commands, services, network access, actual image contents/users, runtime permissions, full E2E, full tooling suite and complete quality gates. Five Docker-dependent test cases were excluded. Offline probes substituted normalized configuration and image-user responses. No files were modified, and no key, token or environment values were inspected.
## Round 2 report (verbatim)

### Independent review — Increment 1B, round 2

#### Round-1 findings

| Finding | closed/open | reason (file:line) |
|---|---|---|
| C1 | closed | Secrets/configs become checked mounts; `volumes_from` becomes a checked privilege. Offline probes reject all three against the unchanged allowlist. `scripts/qa_deploy.py:142`, `scripts/qa_deploy.py:180`. |
| C2 | closed | Build services retain explicit images; `run()` inspects that reference. Both rejection and inspection selection verified offline. `scripts/qa_deploy.py:126`, `scripts/qa_deploy.py:440`. |
| C3 | closed | Baseline corrected. Extending the harness holder decision to K7 is consistent with its recorded host-root rationale. K7 explicitly accommodates the harness; `tmp_svid` is registered, and a child mount by a non-holder is rejected. `docs/slices/agentic-delivery-process/test_plan.md:140`, `docs/requirements.md:322`, `security/invariants.yaml:49`, `scripts/qa_deploy.py:247`. |
| C4 | closed | Profiles are extracted and compared with the register; removing `tests` fails. The harness remains registered only under `tests`. `scripts/qa_deploy.py:46`, `scripts/qa_deploy.py:199`, `security/invariants.yaml:250`. |

Validation: 48 offline tests passed; five Docker-dependent tests excluded. Independent offline probes passed. No files changed; no Docker or network used.

#### New blocking findings

None

#### Verdict

Approvable within the threat model: yes

## Reviewer prompts (verbatim)
Recorded so a review can be rerun the same way. Command, from the repository root:
`codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral -C . [--add-dir <dir with earlier reports>] -o round.md - < PROMPT.md`.

### Round 1

````markdown
You are the independent reviewer of an implementation change in the repository at the current
working directory. You did not write it. Review read-only: do not modify files, run docker, start
services or use the network. Never print key material, tokens or environment variable values.

## What to review
The commit range `main..HEAD` (`git diff main..HEAD`, `git log main..HEAD`): Increment 1B of slice
`agentic-delivery-process`, the deployment register `security/invariants.yaml`, the check
`scripts/qa_deploy.py` (`make qa-deploy`), its tests `tests/tools/test_qa_deploy.py`, the
`REQ-SEC` requirements in `docs/requirements.md`, ARCH-034, and rulebook changes in `AGENTS.md`.
The approved intent is `docs/slices/agentic-delivery-process/plan.md` (Increment 1B, REQ-SEC,
known violations, success criteria) and `test_plan.md` (T-8 to T-13 and "1B implementation notes",
which record the user's decisions and the deviations). You may read the whole repository, including
`compose/spiffe.compose.yml`, Dockerfiles, entrypoints and `docs/open_problem_log.md`.

## Rules for findings
Read `AGENTS.md`, section "PoC scope and proportion", first. This is a proof of concept; the threat
model is honest mistakes by an agent, not deliberate attacks on CI or the gates. Only these block: a
concrete false green (the check can pass while what it protects is broken), a contradiction with the
approved plan or the user's recorded decisions, or an approved decision without a test. Everything
else is advisory: list it once, briefly. Production-hardening ideas are advisory at most.

## Part A: the slice's two questions
1. Tests: for each tooling test and for `qa-deploy` itself, which wrong input would still pass (a
   compose fact, mount, env var or privilege that should fail but does not; a missing or empty
   input read as success)? Does each test match its T-8..T-13 description?
2. Keys: does the change make a key, socket or secret reachable by a service outside the holder
   list, or does the register or a requirement declare a holder the plan and the recorded decisions
   do not support? Does any output, test or file record a secret value?

## Part B: generic questions (a trial for a future review template; answer each briefly)
1. Intent: does it do what was approved, no more and no less?
2. Claims and evidence: for each claim (docs, requirements, comments), what proves it, and could the
   proof hold while the claim is false?
3. Design and quality: simplest design that fits, readable, consistent with the repo's other QA
   scripts; relevant qualities no worse.
4. Failure and change: behaviour on unreadable or malformed input, missing docker, an image that is
   not built; fails safe?
5. Rules and new risks: keeps AGENTS.md rules and existing requirements; adds anything that should
   itself be registered?
6. Ripple: what else depends on what changed (CI, Makefile, docs, other slices), and is it updated?
7. Durability: anything decided or learned that lives only somewhere temporary?
8. Blind spots: what did you not check?

## Output (markdown only)
# Independent review — Increment 1B
## A1. Tests
## A2. Keys
## B. Generic questions
(one short paragraph or "none" per question)
## Blocking findings
Each with id (C1, C2, ...), where (file:line), failure scenario, smallest fix. "None" if none.
## Advisory (at most five)
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
## Not checked
````

### Round 2

````markdown
You are the independent reviewer of Increment 1B in the repository at the current working
directory (read-only: no file changes, no docker, no network; never print key material, tokens or
env values). Your round-1 report is round1.md in the extra directory; it found C1-C4. The author's
fixes are in commit HEAD (`git show HEAD`). For C3, the author applied the user's recorded holder
decision for `rogue-tests` (test_plan.md, "1B implementation notes") to K7 as well, with the same
reason, and registered `tmp_svid` as a K7 location; judge whether that is consistent with the
recorded decision and the requirement text, and flag it for the user if not.

Rules: AGENTS.md "PoC scope and proportion". Re-check only C1-C4. In this round a new finding is
allowed only if it is a blocker (a concrete false green inside the honest-mistake threat model, with
a failure scenario). Do not repeat advisories.

Output, markdown only:
# Independent review — Increment 1B, round 2
## Round-1 findings
Table: Finding | closed/open | reason (file:line)
## New blocking findings
"None", or each with id, where, failure scenario and smallest fix.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
````

