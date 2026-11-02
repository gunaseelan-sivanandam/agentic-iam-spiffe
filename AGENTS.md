# AGENTS.md — Repository Rulebook

This file is the single rulebook for this repository, for human contributors and coding agents.
Where it conflicts with a global or personal convention (for example `~/.claude/CLAUDE.md`), **this
file wins inside this repo**. Unit-test specifics are in [`tests/unit/AGENTS.md`](tests/unit/AGENTS.md),
which is part of this rulebook.

Every rule here is meant to be true of the repo today. If you find one that is not, fix the rule or
the repo in the same change — do not leave them disagreeing.

## Start here

| Question | Read | Kind |
| --- | --- | --- |
| What is this project, how do I run it? | [`README.md`](README.md) | overview |
| Where does the project stand right now? | [`docs/STATUS.md`](docs/STATUS.md) | current state |
| What must the system do? | [`docs/requirements.md`](docs/requirements.md) | authoritative |
| How is it built, which runtime state exists? | [`docs/architecture.md`](docs/architecture.md) | authoritative |
| What is the trust model, on one page? | [`docs/architecture.md` — Security model summary](docs/architecture.md#security-model-summary) | summary of the ARCH sections |
| Which test proves which requirement? | [`trace/tests.yaml`](trace/tests.yaml) | authoritative |
| What does each E2E or static test do, in plain English? | [`docs/test_spec.md`](docs/test_spec.md) | hand-written spec |
| Unit-test requirement matrix (M4 trust gates) | [`docs/unit_test_spec.md`](docs/unit_test_spec.md) | authoritative, read by `make traceability-check` |
| Known unfixed runtime/trust problems | [`docs/open_problem_log.md`](docs/open_problem_log.md) | authoritative |
| Which delivery mistakes were made, and what changed because of them? | [`docs/delivery_problem_log.md`](docs/delivery_problem_log.md) | authoritative |
| Who may hold which key, socket or secret; what each service may be | [`security/invariants.yaml`](security/invariants.yaml) with the `REQ-SEC` requirements | authoritative, checked by `make qa-deploy` |
| What is planned or waiting (proposed slices, actions only the user can take)? | [GitHub issues](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues), labels `slice` and `user-action` | tracking; a slice's decisions move into its `plan.md`, because reviewers read the repository, not issues |
| How was a past slice designed? | [`docs/slices/`](docs/slices/README.md) | frozen records |
| What happened, when? | [`docs/history/`](docs/history/) | history |
| Retired documents | `docs/archive/`, `docs/slices/archive/` | archive, do not follow |

## PoC scope and proportion

This repo is a proof of concept. Its goal is in [`README.md`](README.md): show that workload identity
is not permission, with tests that prove each boundary. It is not production hardening. The rules
below apply to every agent that plans, implements or reviews here, and hold until the user changes
them.

- **Delivery threat model.** Agents make honest mistakes: loose or wrong tests, weakened checks,
  skipped steps, stale evidence, wrong configuration. They do not deliberately attack CI, the
  gates, the evidence or the repo; that residual is accepted
  ([OPL-009](docs/open_problem_log.md)). This is about *how we deliver*. The *system under test*
  still defends against rogue workloads; that is what the PoC demonstrates.
- **Accepted PoC simplifications.** Keys and credentials live in files and environment variables
  on one Docker host. A design where each secret is visible only to the services that hold it is
  enough. KMS, HSM, Vault, per-key ownership proofs, CI-runner isolation and supply-chain controls
  are out of scope unless the user asks.
- **Threat-model changes.** No agent may change, expand or narrow the approved threat model during
  planning, implementation, any review round or review fixes without the user's explicit approval.
  Proposed changes remain decision concerns; reviewers use the approved model until approval.
- **Preserve discovered issues.** Preserve every issue discovered during the work and report it to
  the user in the final handoff, regardless of whether it is pre-existing, introduced by the change,
  related to the current slice, or outside the approved threat model. Include its disposition and
  any existing tracking reference. Reporting an issue does not by itself make it blocking or
  authorize fixing it; out-of-model issues need no separate OPL or exception entry.
- **Ask before growing.** If a change makes the process bigger or more complex (a new gate, job,
  document, register, exception class or review step), say so and ask the user first. Prefer the
  smallest check that catches an honest mistake.
- **Few exceptions.** Fix rather than except. Do not open an OPL, exception entry or plan note for a
  finding outside the threat model; one line in the review report is enough. Every exception must
  fit on one line and have an expiry.
- **Review findings.** Judge within the approved PoC threat model. Blocking findings require
  a concrete unmet approved obligation or security/correctness failure, a false green, a
  contradiction, or missing required proof. Preferences and speculative hardening are advisory.
  Preserve pre-existing and out-of-model issues without automatically making them slice blockers;
  a claimed validation obstruction needs evidence. Threat-model changes go to the user.
  Required checklist evidence and accountable-reviewer confirmation of N/A are completion
  conditions, not permission to promote advisory preferences into blockers. Explicit provisional
  tests-stage acceptance may carry named runtime proof forward; final acceptance may not.
- **Review loop.** One initial review is followed by at most three fix-and-recheck cycles per
  declared artifact review unit: one artifact or a fixed bundle with identified members. Each cycle comprises one author fix/response submission and assessment by all
  required reviewers; parallel reviewers do not count separately. An incomplete review consumes
  execution time, not a completed cycle. Cycle three is allowed; remaining blockers then
  escalate. Revisions, new findings, restarts and upstream corrections do not reset counters.
  Only explicit user authorization extends the limit. A plan/test-plan bundle has one shared
  counter, not three cycles per member; renaming or repartitioning it cannot reset that counter.
  Authors answer each finding with a fix or an evidence-backed proposed rejection. They cannot
  close a blocker as won't-fix. The originating reviewer accepts/rejects each response with a
  reason; it may downgrade its own finding with a reason, and may upgrade an advisory in a
  later round only with new evidence. Only the user may waive a blocker, with scope, rationale
  and expiry; waived is not fixed. Earlier escalation requires a baseline conflict or an
  explicit, evidenced reviewer judgment of lack of progress. No consolidated report can silently
  suppress or downgrade findings.

## Operating model (black-box first)
- Treat the system as a black box first:
  - authored intent in `docs/requirements.md`
  - authored runtime/system model in `docs/architecture.md`
  - runtime-visible proof in `trace/tests.yaml` plus E2E evidence artifacts
- `DD-*`, `UT-*`, source helpers, and local test doubles are engineering controls, not the primary
  proof of system behavior.
- If a security-relevant behavior depends on hidden state, author it before implementation in the
  slice `plan.md` and, when runtime behavior changes, in the state inventory of `docs/architecture.md`.
- Do not introduce or keep runtime-significant behavior that exists only in code.

## Traceability model and IDs

Every requirement is traced the same way: requirement → test ID in `trace/tests.yaml` → entry in
[`docs/test_spec.md`](docs/test_spec.md) → implementation → stored, checked result. A test is an E2E
test (the harness runs it; its evidence is checked by `make qa-evidence`) or a static test (a gate
proves it on every run; see below).

Allowed links only: `REQ → ARCH` (architecture `Satisfies:`), `ARCH → DD` (DD `Implements:`) or
`ARCH → files` (architecture `Implemented by:`), `DD → UT` (UT `Covers DD:`), `REQ → E2E` and
`REQ → static test` (`trace/tests.yaml` `source_requirements`), and `ARCH → IT` (`trace/tests.yaml`
`source_architecture`; no integration cases exist yet).

| ID | Where it lives | Format (as enforced by `scripts/validate_traceability.py`) |
| --- | --- | --- |
| `REQ` | `docs/requirements.md` headings | `## REQ-<scope>-<code><n> — <title>`, e.g. `REQ-M1-R1`, `REQ-M4A-J3`, `REQ-M5-FT7`, `REQ-G-R2` |
| `ARCH` | `docs/architecture.md` headings | `## ARCH-NNN <title>` followed by `Satisfies: REQ-…` |
| `DD` | comment block above the implementing function in `services/**` or `scripts/**` | `# DD: DD-NNN` / `# Implements: ARCH-NNN` / `# Title: …` |
| `UT` | comment block above the test in `tests/unit/**` | `# UT: UT-NNN` / `# Test Description:` / `# Precondition:` / `# Expected Output:` / `# Covers DD:` |
| E2E test | `scripts/rogue_node_tests.sh` | harness IDs such as `M1-T1`, `M3.S4-T2`, `M5-T49`; mapped in `trace/tests.yaml` as `e2e_suite` / `e2e_case` entries |
| Static test | `trace/tests.yaml` (`type: static_test`) and a `docs/test_spec.md` heading | `<NAME>-<CODE>`, e.g. `DEPLOY-K1`, `EVID-T1`; names `source_requirements`, `gate: make <target>`, `negative_controls` (`<file>::<test>` tooling tests that show the gate fails on each kind of violation) and `result` (the stored report) |

- An ARCH section implemented by files that carry no DD-tagged functions (configuration such as
  Envoy or SPIRE files, the deployment register, a test or demo script) names them on an
  `Implemented by:` line; `make qa-trace` checks they exist. QA gate code carries no DD tags.
- IDs are never reused. Do not delete a requirement or architecture ID; mark it retired with the
  reason. Retired DD and test IDs are listed under `retired_ids` in `trace/tests.yaml`; reusing one
  fails `make qa-trace`.
- A requirement's status comes from its proofs and the deployment register, never from a run: it is
  not proved without a test, while an asset it protects has a `known_violations` row, or (the
  non-root rule, `REQ-SEC-D2`) within its grace date. A requirement that is not proved is a
  `requirements_without_proof` gap.
- `make qa-trace` fails on structural errors (unknown IDs, wrong link direction, missing fields,
  duplicates, missing files). On a PR it also fails on a coverage gap the PR adds compared with its
  merge-base (the gap gate); a gap added on purpose needs a one-line `accepted_gaps` entry in
  `trace/tests.yaml` with a reason and an expiry. Older gaps are reported, not failed.

## Slice workflow

Every change follows this workflow, scaled to its size: a small fix still gets a plan (it may be a
few lines), tests first, an independent review and the close-out, but not every section of the
template needs more than "none". A slice bundle lives in `docs/slices/<slice-id>/`, starts from
`docs/slices/_template/`, and gets a row in the [slice index](docs/slices/README.md).

1. **Plan and review.** Run the `grill-me` skill, covering the actual problem, causes,
   alternatives, relevant product qualities and slice dependencies. Always identify keys,
   sockets, secrets, holders and security relevance against `security/invariants.yaml`.
   Write `plan.md` with behavior obligations, decisions, requirements to add/change, state,
   assets, environment probes, retirement and rulebook changes; write `test_plan.md` from
   those obligations with distinct UT/E2E maturity and acceptance criteria. Independent review
   and fixes precede the user's plan PR. Approval is the user's merge into the designated
   branch: normally `main`, or an explicitly approved fixture integration branch. Verify the
   branch and artifact revisions, not merge state alone. One plan PR may authorize multiple
   fully specified slices; unresolved slices remain unapproved.
2. **Specify, design and test.** After plan approval, author the requirement specification in
   `docs/requirements.md`, then obtain requirements-focused review. Author architecture and
   detailed interface contracts in `docs/architecture.md`, then obtain architecture-focused
   review. These elaborate the approved obligations; they cannot introduce new behavior or
   weaken guarantees. Any ambiguity or baseline change returns to the user; independent work
   may continue and isolated variants may collect evidence without becoming the baseline.
   - Write executable tests from the approved test plan and reviewed contracts, using minimal
     interface skeletons where needed, then obtain tester-focused review. Distinguish UT and
     E2E evidence. Record red output and intended failure cause, positive controls and targeted
     protection-removal mutants for security-relevant paths. Import errors are not meaningful red.
   - Expected outcomes come from the approved plan, `probe@<commit>` observations made before
     implementation, or `existing@<commit>` assertions; never from the new implementation.
     A contradicting probe is a user decision, not permission to change the expectation.
   - Every negative E2E has a passing positive twin on the same route in the same run. Where
     runtime proof cannot yet execute, test review may explicitly accept assertions provisionally
     with named outstanding evidence. Final acceptance still requires that evidence.
   - Lock accepted tests together with their fixtures, helpers, configuration and trace/env gates.
     Use default inclusion outside reviewed implementation-owned and record paths; unknown inputs
     are not silently excluded. Genuine corrections return to tests-stage review; implementers
     cannot silently edit assertions or neutralize them through configuration. Hash checks detect changes rather
     than establish write prevention.
   - Update `trace/tests.yaml` before claiming implementation proof. A requirement may use a
     static test backed by a gate and real negative controls, where runtime proof adds nothing;
     the plan states the proof type. Tooling tests do not become harness E2E by naming.
3. **Implement and review.** Implement only approved behavior and retire agreed dead paths.
   Independent implementation review examines correctness, security, simplicity, maintainability
   and test strength. Corrections reopen affected upstream/downstream artifacts and evidence,
   with independently checked impact analysis. Finish with a fresh integrated review: first
   assess the original problem, approved plans, authoritative artifacts and delivered behavior;
   then reconcile the complete review history. Perform these stages manually until an approved
   controller implements their coordination; instructions are not claimed as enforcement.
4. **Verify and close.** All of the following, in the same change:
   - run `make qa-quality` (includes `qa-trace`, `docs-check`, `test-lint` and `qa-deploy`), the full E2E suite on a clean
     stack (`scripts/clean_stack.sh`, then `make e2e`), and `make qa-evidence`; the `e2e` CI check runs the same
     suite on the PR;
   - **update `docs/test_spec.md` by hand** for every E2E or static test added or changed — plain
     English, not code: what it tests, how (premise, exercise, outcome, or the gate's check), and
     the evidence or result it leaves. Each test gets a heading `### <ID> — “<name>”`; `make
     docs-check` fails on a missing or stale heading, but it cannot judge the prose, so review it;
   - add a dated entry to `docs/history/implementation_log.md` (what changed, validation results,
     what was not run and why);
   - update `docs/STATUS.md` and the slice's row in `docs/slices/README.md`;
   - add or close entries in `docs/open_problem_log.md` for problems found or fixed, and in
     `docs/delivery_problem_log.md` for delivery misses (a step skipped, a false claim, a review
     miss) found or fixed;
   - open a GitHub issue for work found but not done (label `slice` or `user-action`), and close the
     issues the change finishes (`Closes #N` in the PR body);
   - put the independent review's answers to the implementation questions in the PR body.

### Independent review
- **Roles and identity.** Never self-review. Codex authors/fixes; Claude independently reviews
  with clean context and a different model from the author/fixer. Record role, invocation/provider
  model identity, instruction/checklist versions and reviewed commit/file hashes. A stable
  originating-reviewer identity may continue in a fresh session with its own finding history;
  another model cannot silently inherit disposition authority.
- **Coverage.** Each artifact has an accountable primary reviewer. Security-relevant work also
  gets an independent security perspective; interface, authoritative-state or cross-component
  failure changes get an independent design/maintainability perspective. All reviewers use the
  shared holistic layer and every matching artifact checklist; mixed artifacts do not permit
  selecting a subset. The accountable reviewer confirms each N/A with supporting evidence.
  On security-relevant slices, protection removed/weakened, trust boundaries, security-property
  evidence and baseline relationship are never N/A.
- **Context.** Supply the agreed problem, plan, test plan, applicable authoritative documents,
  relevant source and environment evidence at identified revisions. Do not substitute summaries
  or hide agreed design. Initial independent reviews withhold this slice's review-comment
  material and persuasive author responses, not authoritative context. Re-review supplies the
  originating reviewer's own findings and corresponding responses/fixes. Integrated review
  receives complete history in its second pass. Decisions cannot remain authoritative only in
  review comments; baseline amendments still require the user's merged plan approval.
- **Revision binding — every delivery stage.** Before authoring, fixing, testing or reviewing,
  identify and supply the designated revisions of authoritative documents, applicable process
  rules/checklists and task source. Record approval status, actual resolved paths/revisions and
  content identities, including automatically loaded instruction files. Check actual inputs
  against that designation before starting; a pull of the latest branch is not sufficient.
  Record the output revision separately: expected implementation edits are outputs, not permission
  to change authoritative inputs. Before accepting a result, verify it applies to the delivered
  output and that its input/dependency binding remains valid. Relevant changed inputs reopen
  affected validation/reviews; missing or uncertain binding stays pending. Preserve existing
  counters, review independence and user-only baseline approval. The fixture tests this same rule.
- **Rules being changed are artifacts.** For every delivery, governing instruction/checklist
  content comes from the designated approved authority revision plus explicit user instructions,
  not edited task-tree copies. A change to AGENTS.md, CLAUDE.md, nested instructions or a
  checklist is reviewed as an output artifact; it cannot govern its own review. Separate the
  authority context from task artifacts or disable their automatic instruction loading and
  supply the approved authority explicitly. Verify and record the resolved authority before
  invocation; inability to establish that separation leaves the operation pending. Architecture
  specifies each CLI's loading method. Clean working-directory selection alone is not proof.
- **Evidence reuse.** The approved feature/slice plan owns the record-path allowlist used by
  review, accepted-test and validation bindings; a trial uses that delivery's approved policy,
  not a separate source of authority. Missing approval is not permission for an agent to invent
  exclusions. Reuse requires matching relevant input identities and independent confirmation
  of record-only status at the required review/handoff. Apply existing reviewed implementation
  exceptions only to accepted-test locks, never to trial equivalence. Record-only equivalence
  cannot substitute an old CI result for the actual head, tested base/merge and required PR mode.
  Exact exclusions are approved in the plan PR or a user-merged plan amendment under D49,
  before use. Design review can propose paths but cannot approve them on the user's behalf.
  Review bindings are default-inclusive under that policy, with their full input manifest
  recorded; no declared-file subset silently excludes other task inputs.
- **CI applicability.** For any delivery, accept required checks only when their GitHub job
  conclusions match the delivered head, intended target and tested base/merge identity, with the
  required event/mode. A merge, a green unrelated run or a local diagnostic is insufficient.
- **Acceptance-checker changes.** Whenever acceptance logic, decision policy, input schema or
  verification configuration changes,
  independent review checks the relevant decision with known-good and known-bad evidence,
  including missing/stale proof. For identity comparisons and CI binding, independently recompute
  the relevant facts; do not treat the candidate checker's own pass as its sole certification.
  This applies during bootstrap and later changes, using existing tests/reviews, not a new gate.
  The originating reviewer specifies/accepts probes and expected cases; Codex executes standard
  Git/hash/API recomputation independently of candidate checker helpers. Record commands/tool
  versions, immutable inputs/results and executor/reviewer attribution. This is executor-reported
  evidence assessed afterward, not elimination of shared honest mistakes.
  Routine new run evidence is checked by the existing verifier; it does not itself require
  recertifying unchanged acceptance logic.
  Classify checker code and transitive helpers/configuration/schema/policy in the reviewed design.
  Unknown or ambiguous changes to consumed checker inputs default to changed acceptance logic.
  Compare their actual identities against the last independently verified identity rather than
  trusting the author's classification. A changed trial acceptance matrix is policy; per-run
  observations are evidence. Record the distinction and repeat only affected verification.
- **Blind fixture trials.** Supply the complete fixed/seeded fixture feature authority in a
  separate task workspace, with applicable process rules and checklists. The orchestration
  meta-plan is not the evaluated agent's feature plan. Keep the independently prepared,
  user-approved, pre-run hash-committed evaluation key with the trial coordinator outside
  evaluated contexts. Expected findings must follow visible fixture authority; hidden requirements
  cannot determine failure. Report/escalate fixed-baseline defects instead of silently rewriting
  authority. Record actual supplied inputs and available tool reads; known or uncertain disclosure
  cannot earn independent-detection credit. Separate folders do not establish OS isolation.
  Fixture-specific content stays off main. This exception does not reduce normal review context.
- **Access and assurance.** Configure reviewers for read/search-only source access and disposable
  probes; route privileged validation through the orchestrator. Probe and label boundaries as
  enforced, detected afterward, instruction-only or unverified. Same-user processes and worktrees
  are not presumed OS sandboxes or credential isolation. Do not inspect secret contents.
  A missing reviewer or partial report cannot count as approval.
- **Records.** Keep one review document per declared artifact bundle, with complete round sections
  for original reviewer reports, author responses/fixes and originating-reviewer dispositions.
  The plan/test-plan bundle uses `plan_review.md`, naming both artifacts and their checksums.
  Preserve completed reports and prompts verbatim, attribution and stable finding IDs. The
  top summary gives current status and links; raw model reasoning/session transcripts and
  credentials are not review records.
- **Review effort and usage.** Every review invocation explicitly requests medium or high effort;
  never rely on the CLI default or silently request xhigh/max. Routine focused reviews and
  rechecks default to medium; initial plan, security, architecture/state/trust-boundary and
  integrated reviews use high. Record the selected level and reason; a broader recheck may use
  high with its reason recorded. Other levels require an explicit user decision.
  Record per-attempt role/stage/cycle, requested and reported model/effort, duration, turns/tool
  calls, uncached input, cache reads/writes, output and provider-reported cost where available.
  Include failures, retries and probes separately; missing is unknown, not zero. Deduplicate
  repeated copies of the same invocation. Output already includes thinking: do not add it twice.
  USD estimates are not subscription invoices or quota percentages. Keep metadata only, with
  one readable usage table in the review record; never publish raw prompts/replies/thinking as
  cost data. Historical effort stays unknown unless invocation evidence establishes it.
- **Finding schema.** Each comment identifies reviewer/role/model/round, reviewed revision,
  severity, checklist/threat-model criterion, exact location, concrete problem, supporting
  evidence, consequence, baseline relationship and resolution criteria. Suggested fixes are
  optional. Every checklist answer cites a supporting location, assertion/result, probe or
  quotation; otherwise it is not verified. Consolidation only groups actual duplicates and
  preserves all originals, severity and disagreements. The consolidator does not confirm N/A
  or accept resolutions on the reviewer's behalf.
- **Scope of findings and fixes.** For every finding, identify the underlying failure class
  and check whether it affects other stages, artifacts or ordinary delivery. Cite a concrete
  counterpart, or explain why the issue is local. Put a generally applicable correction in the
  general rule/design, with fixture scenarios proving it. This is mandatory in the holistic
  checklist layer and the fix review; it does not authorize scope/threat-model expansion or
  implementation of unrelated changes. Proposed broader baseline changes still need approval.
- **Outcome attribution.** In issue/run records, distinguish reviewer detection, controller
  containment and evidenced root-cause resolution. Record what was observed or remains unknown;
  containment does not prove reviewer effectiveness or close a finding. Record expected user
  approvals separately from human troubleshooting, source edits or other execution assistance.
  Assisted ordinary delivery can pass normal review/validation, but cannot be claimed as a
  successful autonomous run. A rescued fixture attempt still fails its autonomy evaluation.
  Trace source changes to recorded invocations and expected user decisions. Unexplained edits
  or interactive interventions default to assisted/unknown, with the autonomous-success claim
  withheld. This is post-run attribution evidence, not prevention or human authentication on
  shared credentials.
- **Plan review.** Review plan and test plan for intent, security, proof adequacy, consistency,
  feasibility and simplicity under the stated delivery and system-under-test threat models.
  Keep each round's reports, input hashes and responses in the bundle's review document. End
  with "approvable within the threat model: yes or no". Proposed checklist additions prompted
  by uncovered blockers remain proposals until the user approves them.
- **Implementation review.** Answer the test-plan questions: what wrong behavior could pass
  each changed test, and whether a key/socket/secret reaches an unauthorized holder through
  mounts, environment, copied files or shared state. The reviewer must examine concrete
  evidence and surrounding dependencies, not merely check that a requested edit appeared.
- **Fix discipline.** Name the actual problem and upstream cause before selecting a fix. Prefer
  simpler upstream corrections where they preserve every approved obligation; removing a
  protection or proof is not justified by simplicity. Changes or uncertainty about requirements,
  design, behavior, scope or security guarantees pause affected work for the user. Comparisons
  remain isolated experiments, never implicit approval.
- **Reports beyond blockers.** Preserve advisories, simpler alternatives, decision concerns and
  unverified areas in every round. Upgrading an advisory needs new evidence; changing the threat
  model requires user approval. The integrated reviewer flags superficial checklist boilerplate.
  Reviewer metadata probes may record existence, owner, mode and readability, never secret values.

Hidden-state rule: if a decision depends on hidden state, `plan.md` lists the state/key name, store,
writer, reader, TTL or lifecycle, decision impact, and whether it is authoritative or advisory.
Mandatory for security-relevant Redis, file, cache, policy, or derived state.

Retirement rule: every `plan.md` states what old logic is removed, what compatibility behavior is kept
temporarily (if any), and which docs/tests/artifacts are deleted or archived. If nothing is retired,
say so.

## Quality gates

Every CI gate is a job named after its make target in `.github/workflows/ci.yml` (workflow `CI`).
A gate's result is its CI job's conclusion on GitHub; a local or offline rerun is a diagnosis and
never replaces it.

| Gate | Command | Enforced by | Threshold |
| --- | --- | --- | --- |
| Trace model | `make qa-trace` | CI, every push/PR | zero structural failures; on a PR (`--mode pr --base <base>`), no coverage gap the PR adds compared with its merge-base unless `accepted_gaps` in `trace/tests.yaml` lists it with a reason and an unexpired date (an expired or stale entry fails); a merge-base that cannot be resolved or read fails. On `main` (`--mode push`) gaps are reported |
| Documentation | `make docs-check` | CI | every harness test and every static test in `trace/tests.yaml` has a `docs/test_spec.md` heading and vice versa; relative links and `#anchors` in live docs resolve; every tracked image in `docs/` is referenced and every `.puml` has its `.svg`; every slice bundle is in the slice index; `TEST_ONLY=` examples name real tests |
| QA tooling tests | `make tooling-test` | CI | `tests/tools/` (pytest) and `tests/shell/` pass |
| E2E outcome lint | `make test-lint` | CI | no outcome guard in `scripts/rogue_node_tests.sh` accepts several outcomes (`assert_file_any`, broad error regexes, `!= 200`), swallows failure (`\|\| true`), checks only a non-zero exit, or is a test of negative greps only; a multi-outcome guard needs `# test-lint: alternate: <reason>` |
| Deployment register | `make qa-deploy` | CI (without image inspection; the `e2e` job runs it with image users inspected) | every service's image, user, networks, ports, mounts, secret env names and privileges match `security/invariants.yaml`; every protected asset reaches only its holders, except unexpired known violations of open OPLs; register holders equal the `REQ-SEC` `Holders:` lines; non-root except the grandfathered baseline until 2027-01-31 |
| Unit guard integrity | `make unit-guard-check` | CI | every unit test has premise, exercise, outcome guards |
| Unit trust bundle | `make unit-trust` | CI | total line coverage ≥ 85%; branch coverage ≥ 75% on `services/capability-issuer/app.py` and `services/tool-b/server.py`; unit traceability check; invariant, negative-control, hybrid-critical suites; invariant flake check ×5 |
| Diff coverage | `make unit-diff-cov` | CI, PRs only (own job) | ≥ 90% of changed lines in `services/capability-issuer/` and `services/tool-b/` |
| Mutation | `make unit-mutation` | CI | score ≥ 70% (capiss and tool-b), counting untested and skipped mutants as not killed; an empty run fails |
| Gate consistency | `make gate-consistency` | CI | every row this table marks as enforced by CI has a CI job of the same name that runs `make <name>`; every CI job has such a row; every CI job is a required check of the `main` ruleset and every required check is a job (the ruleset is read from the public GitHub API; a failed read fails) |
| Full E2E suite | `make e2e` | CI, every push/PR; and local on a clean stack, required in step 4 | all pass; warnings reviewed. The CI job then runs `make qa-deploy` with image users inspected and `make qa-evidence`, and uploads the publication set for 14 days only if the secret check found nothing |
| E2E evidence | `make qa-evidence` | in the CI `e2e` job; local, after the E2E run | every test has premise/exercise/outcome evidence and a PASS line; no file of the publication set (`PUBLICATION_SET` in the `Makefile`: `test_report.log`, `artifacts/rogue-tests/`, `artifacts/quality/`) holds a secret by shape: a PEM private key, a base64 PKCS#8 private key, base64 of a PEM private key, a base64 or base64url run of ≥ 200 characters with ≥ 20 distinct ones outside certificates, a `JIRA_API_TOKEN=` or `Authorization:` line with a value, or an Atlassian API token; an unreadable file fails; a finding names the file and kind, never the value |

Standards that are **not** gated yet (follow them for new and changed code):
- `ruff check services scripts` stays clean.
- Cyclomatic complexity ≤ 10 per new or changed function (`radon cc`). Existing functions above the
  limit are tracked as debt in `docs/STATUS.md`; do not make them worse.
- `mypy` and `bandit` are not configured in this repo.

## Coding rules
1. No secrets in source, config, logs, or evidence. Credentials come from the environment at runtime.
2. No Python `eval()`, `exec()`, or `__import__()` on dynamic input. (Redis `EVAL` of fixed Lua scripts is fine.)
3. Validate and reject external input at service boundaries; internal functions trust their callers.
4. Fail closed: any unexpected error in a security decision path denies.
5. No broad `except Exception` in enforcement or validation paths; catch specific exceptions.
6. Audit events never contain token values, passwords, or key material; E2E tests assert this.
7. Secrets this repository creates are stored in a standard, recognisable format (private keys as
   PKCS#8 PEM), so the evidence secret check finds them by shape. Secrets created by others (SPIRE
   key stores, join tokens, Jira tokens) keep their format.

## Documentation rules
- One home per fact. Before adding a document, check the [Start here](#start-here) table; extend the
  owning document instead of creating a parallel one.
- `docs/test_spec.md` is hand-written and must describe every E2E test the harness runs.
- Implemented slice bundles are frozen records; do not rewrite them to match later reality.
- Tests for QA tooling (`scripts/check_docs.py` and similar) live in `tests/tools/`; shell-level tests
  live in `tests/shell/`. The unit-test rules in `tests/unit/AGENTS.md` apply only to `tests/unit/`.
- Retire documents with `git mv` into `docs/archive/` (or `docs/slices/archive/`); never delete them.
- Architecture diagrams use a C4-style, grid-aligned layout: group by trust boundary or network zone,
  flows left-to-right or top-to-bottom, orthogonal connectors with few crossings, planned components
  labeled as such.

## Git rules
- No `Co-Authored-By` trailers for AI assistants in commit messages.
- Only the user merges into designated approval branches: normally `main`, or the fixture
  integration branch explicitly authorized in the approved plan. Agents push work branches and
  open/update PRs; they do not push directly to approval branches or merge into them.
  Shared owner credentials do not enforce this outside controller-routed operations; record that
  instruction-only residual rather than claiming GitHub separates user and agent authority.
- One-time creation of a previously absent fixture integration ref is allowed only when the
  approved plan authorizes its name and creation-point rule: the clean pinned framework candidate
  commit recorded by the controller in the execution manifest at creation. Never overwrite an
  existing ref this way; subsequent approval-branch updates remain user merges only.
- Check the PR base against its approved target at creation and when accepting merge evidence.
  Avoid stacking. A stacked PR waits until its base is the intended approval branch; that may be
  `main` or an explicitly approved fixture branch, never a stale working branch
  ([DPL-008](docs/delivery_problem_log.md#dpl-008-a-stacked-pr-was-merged-into-its-stale-base-branch-instead-of-main)).
- Do not force-push, reset away or rewrite completed review records during normal fixes. A Git
  rewrite cannot reset review budgets; missing/conflicting history needs reconciliation, not a
  fresh counter. Controller-routed writes must preserve independent cycle receipts.

## Environment
- Docker Engine + Docker Compose v2. Linux, or macOS with Rancher Desktop.
- Run every command from the repo root.

## Quick start
1. Preflight:
   ```bash
   docker info >/dev/null
   docker compose version
   docker context ls
   scripts/clean_stack.sh --check
   ```
2. Clean state when needed: `scripts/clean_stack.sh` (run it again if the first pass reports a
   permission warning on a root-owned file).
3. Bring the core stack up:
   ```bash
   docker compose -f compose/spiffe.compose.yml up -d --build
   ```
4. Inspect SPIRE agent logs for workload SVID activity:
   ```bash
   docker compose -f compose/spiffe.compose.yml logs -f --tail=200 spire-agent
   ```
5. Tear down:
   ```bash
   docker compose --profile tests -f compose/spiffe.compose.yml down --remove-orphans
   docker compose -f compose/spiffe.compose.yml down --remove-orphans
   ```

## Test commands
- Full suite (writes `test_report.log` and evidence under `artifacts/rogue-tests/`, builds every image, and gives
  the root-owned output back to you so `make qa-evidence` can run):
  ```bash
  scripts/clean_stack.sh
  make e2e
  ```
- Specific test IDs:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build \
    -e TEST_ONLY=M3.S3-T3,M3.S4-T2 rogue-tests
  ```
- Selected milestones:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build \
    -e TEST_MILESTONES=m1,m2,m25,m3 rogue-tests
  ```
- Keep `--build`: `scripts/rogue_node_tests.sh` is copied into the `rogue-tests` image, so without it
  a run silently uses the harness from the last build. (The `varambu` wrapper is bind-mounted and needs
  no rebuild.)
- A targeted run overwrites `test_report.log`, so `make qa-evidence` needs a full run to pass.
- Live Jira tests (`M5-T55`, `make jira-live-smoke`) need explicit live configuration; default runs
  use deterministic mocks.

Profiling is on by default (`TEST_PROFILE=1`); timings go to `artifacts/rogue-tests/guard_timings.tsv`
and `guard_timings_top25.txt`. Disable with `-e TEST_PROFILE=0`.

## Evidence checks (false-green guard)
After a full run, `make qa-evidence` validates the evidence. Evidence holds no token values: guards work in a
scratch directory, and the harness publishes it with every token-shaped value replaced by its SHA-256 fingerprint.
To inspect by hand:
```bash
find artifacts/rogue-tests -maxdepth 1 -mindepth 1 -type d | sort
grep -Eq 'Failed: [1-9]' test_report.log && find artifacts/rogue-tests -name fail_reason.txt -print -exec cat {} \;
find artifacts/rogue-tests -name 'warning_reason_*.txt' -print -exec cat {} \;
find artifacts/rogue-tests -name skip_reason.txt -print -exec cat {} \;
```
- `fail_reason.txt`: terminal guard failure for that test.
- `warning_reason_*.txt`: the test passed through an accepted alternate path; review the condition.
- `skip_reason.txt`: an env-gated test did not run its exercise (for example `M5-T55` without live
  Jira). `make qa-evidence` counts it as skipped, never as validated, and only if the suite declares
  the gate for that test in `trace/tests.yaml` (`env_gates`), the gate check left premise evidence,
  and no exercise or outcome artifacts exist. The test still prints `PASS` in `test_report.log`.

## Docker guardrails
- Agents manage only stacks they created or the user explicitly authorized them to take over.
  Names or Compose project alone are not ownership. Before lifecycle/cleanup, reconcile exact
  object IDs, Compose working-directory/config-file labels and affected mount paths against the
  run receipt. Unknown, replaced or cross-checkout objects require user takeover approval.
  Check fixed-name and `--volumes-from` cleanup targets as well; preserve evidence before reset.
- Never run Docker lifecycle commands in parallel. Serialize `scripts/clean_stack.sh` and
  `docker compose … up/down/run`; run `ps`/`logs` only after the mutating command finishes.
- `capability-issuer-no-opa-envoy` is test-only (`tests` profile); never use it outside tests.
- Prefer `scripts/clean_stack.sh` over manual cleanup.
- Keep evidence under `artifacts/rogue-tests/` unless you deliberately set `ROGUE_TEST_EVIDENCE_DIR`.
- macOS / Rancher Desktop: point the Docker CLI at the `rancher-desktop` context
  (`docker context use rancher-desktop`). On socket/context mismatches or permission-constrained
  bind mounts under `tmp_svid/` or `artifacts/`, confirm `docker info` works and rerun
  `scripts/clean_stack.sh`.
