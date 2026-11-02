# Slice Plan — delivery-orchestration

Status: Draft from the grill-me session, 2026-11-01. Not approved for implementation.
Tracks GitHub issue #16. Historical input is the frozen
[`agentic-delivery-process/later_slices.md`](../agentic-delivery-process/later_slices.md),
not an approved design to implement wholesale. Fixture validation precedes the OPL-005–008 pilot
(issue #17). This plan does not approve the pilot's security design.

## Goal

Use Codex to orchestrate approved feature delivery, with Claude independently reviewing each
artifact and the integrated result. Reduce dependence on the user during execution without
letting agents approve changes to requirements, design, behavior, scope or security guarantees.
Every decision, review and fix starts from the actual problem, its causes and system context.
Exercise the orchestration on an isolated fixture branch, then improve it through the real
key/state-isolation pilot.

### Observed delivery failures this addresses

The root causes are recorded in the [delivery problem log](../../delivery_problem_log.md):
DPL-003 put standing rules in temporary/frozen plans; DPL-004 let an approved plan and green
trace structure hide missing proof; DPL-005 confused running checks with merge enforcement;
DPL-006 substituted local diagnosis for a failed CI conclusion; DPL-007 repeatedly patched
detectors instead of upstream causes; DPL-008 merged to the wrong base; and DPL-009 measured
less than its gate claimed. DPL-001/002 demonstrate untested key-holder claims and publication
leaks. This slice makes decisions, evidence, review and handoff accountable; it does not claim
to fix the runtime isolation OPLs or the separately deferred scanner.

## Threat model

This slice applies the existing [PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion)
without expanding or narrowing it:

- **Delivery process:** Codex, Claude and the controller may make honest mistakes: skipped or
  misconfigured checks, weak tests, unsupported review conclusions, stale inputs/evidence,
  incorrect approval interpretation or unintended tool actions. Guidelines, review, controller
  checks and explicit assurance labels address those errors.
- **System under test:** the existing rogue-workload and protected-service trust boundaries remain
  in scope when exercised by tests. This slice does not fix or claim to fix the pilot's OPLs.
  Docker/socket access retains the existing host-level effects; worktrees are not runtime isolation.
- **Accepted residual:** deliberate attacks by agents on their own CI, evidence or orchestration
  infrastructure remain outside the delivery model under OPL-009. Same-user host execution is
  not represented as malicious-agent containment. Existing single-host/file-based PoC
  simplifications and production-hardening exclusions remain unchanged.

Every review uses this application of the approved model. Proposed changes are decision concerns
for the user, not new blocking obligations. Environment probes record metadata only and never
credential contents; tool configuration, post-run detection and OS enforcement are distinguished.

## Grill-Me Review Summary

The following records the user's agreements in this session. Implementation choices remain subject
to independent plan/test-plan review and the user's plan approval. Current review status and cycle
accounting live in `plan_review.md`; this document does not grant itself approval.

| ID | Agreed decision |
| --- | --- |
| D1 | Codex orchestrates and authors/fixes; Claude independently reviews with fresh context. Reviewers use a different model from the author/fixer. Guidelines and checklist formats remain runtime-independent. |
| D2 | Every feature begins with grill-me covering the problem, alternatives, constraints, behavior, security, failure modes and relevant product qualities. Split into slices; individual slices receive further grill-me when necessary. |
| D3 | Produce plan and test plan, independently review and fix them before the user's plan PR. The user approves by merging; no implementation before approval. One plan PR may authorize multiple fully specified slices in dependency order. Unresolved slices remain unapproved. |
| D4 | Each approved slice proceeds through requirements and requirements review, architecture and architecture review, tests and tester-focused review, implementation and implementation review, validation and fresh integrated review, then the user's implementation PR. Requirements and architecture stay in today's authoritative documents. |
| D5 | Each stage focuses on its artifact but considers the whole feature and may challenge upstream assumptions. Corrections reopen dependent artifacts, reviews and validation; an independent reviewer checks the impact analysis. Previous approvals do not approve changed content. |
| D6 | Automatic corrections must preserve approved requirements, design, behavior, feature scope and security guarantees. Simplicity never justifies weakened protection or proof. Tests/docs cannot be adjusted to legitimize an unauthorized implementation. |
| D7 | A baseline conflict or uncertainty about compliance pauses affected delivery work. Investigate autonomously; present an amendment, defer explicitly, or build isolated comparison variants. Only the user can approve adoption. Continue unaffected authorized work. |
| D8 | Up to three variants per unresolved decision. Variants remain experiments, with comparable evidence and trade-offs, and cannot silently enter the delivery branch. Preserve a compliant implementation where feasible. |
| D9 | The orchestrator triggers all mandatory reviews. A primary reviewer is accountable for each artifact; additional specialist reviews follow explicit artifact/risk triggers. Extra reviews may be added, but required ones cannot be skipped. |
| D10 | Independent reviewers initially do not see other reviewers' reports or the author's persuasive narrative. They receive the original problem, agreed decisions, approved baseline, current artifact/revision, upstream artifacts, applicable rules/checklists, repository access and environment evidence. Factual assumptions/rationale belong in artifacts. |
| D11 | Consolidation only groups duplicates and assembles records. Preserve every original finding, attribution, severity and distinct failure scenario. Disputed duplicates remain separate. Consolidation cannot adjudicate or silently resolve findings. |
| D12 | The originating reviewer accepts or rejects each proposed resolution with a reason. It may downgrade its own finding with a reason; upgrading an advisory in a later round requires identified new evidence. Authors cannot close blockers as won't-fix. Only the user may waive a blocker, with recorded scope, rationale and expiry; waived is not fixed. |
| D13 | One initial review, then up to three fix-and-recheck cycles per artifact. A cycle is an author's fix/response submission followed by assessment from all required reviewers; parallel reviewers collectively count as one cycle. After three unsuccessful cycles, unresolved blockers escalate to the user. Escalate earlier for baseline conflicts or repeated lack of progress. New findings, revisions and upstream corrections do not silently reset the counter; only the user may authorize additional cycles. Exhaustion never relaxes acceptance criteria. Incomplete/unavailable reviews consume execution budget, not a completed fix cycle. |
| D14 | Reports use a fixed finding schema: stable ID, reviewer/role/model/round, artifact revision, classification/checklist criterion/threat-model applicability, location, concrete problem, evidence, consequence, baseline relationship, and resolution criteria. Suggested fixes are optional and not binding. Responses record cause, disposition, fix/evidence and baseline/security effects; reviewer dispositions carry reasons. |
| D15 | Preserve and report every discovered issue at the final handoff, whether pre-existing, introduced, unrelated or out of model. Reporting alone neither blocks delivery nor authorizes a fix. Relevant pre-existing problems that prevent an approved guarantee or meaningful validation can block; that relationship requires evidence. |
| D16 | Mere discovery is not new exposure. New exposure means the change makes the issue reachable, exploitable or observable where it was not before. Regardless of this classification or current-slice consequence, preserve and report it. Out-of-model concerns that challenge the model go to the user as decision concerns. |
| D17 | Keep the existing delivery/system-under-test threat-model distinction and PoC boundaries. Start with a rule in AGENTS.md: no agent changes, expands or narrows the approved model in any phase or review round without explicit user approval. No new threat-model file or qa_decisions approval mechanism is authorized here. |
| D18 | Both checklist layers are mandatory: shared holistic reasoning and artifact-specific checks. Artifact types determine the complete matching set, including every type in mixed artifacts. Record classifications and checklist versions; the orchestrator cannot choose a subset. |
| D19 | N/A needs evidence and explicit confirmation by the accountable reviewer during consolidation. On security-relevant slices, protection removed/weakened, trust boundaries, evidence of security properties, and baseline relationship are explicitly never N/A. |
| D20 | Every checklist answer references a concrete location, assertion/result, probe or quoted passage that actually supports it. Unsupported answers are not verified, never filled with boilerplate. The integrated reviewer flags superficial near-identical answers as process findings, distinguishing legitimate shared evidence. |
| D21 | An uncovered blocker follows normal blocking rules and produces a process finding proposing a checklist addition. The user approves the addition in the final PR; it does not silently expand the current checklist, design or threat model. |
| D22 | Security relevance is recorded in grill-me and the approved plan. Identity, authorization, secrets, trust boundaries, protected state, security controls and their tests/evidence require security treatment. If discovered later, add required checks and record why; never downgrade an approved classification without user approval. This slice is security-relevant. |
| D23 | The integrated reviewer starts fresh from the original problem, approved plan and complete delivered artifacts/evidence, assessing the result before consulting previous review conclusions. A second pass examines finding history, baseline drift and unresolved issues. |
| D24 | One review document per artifact, organized into complete round sections. Each round contains original reports by reviewer, author responses/fixes and originating-reviewer dispositions. A top summary records status and provenance. Stable IDs link rounds; append new rounds without rewriting original reports. Record user escalations/decisions in sequence. |
| D25 | The final PR summarizes result, validation, review provenance, findings/fixes, rejected resolutions, waivers, deferred issues, variants and remaining decisions, with links to durable records. Record actual model identity/version as available, prompts/checklist versions, commits and artifact hashes; never private model reasoning or secrets. |
| D26 | Unattended authority covers code/branches, tests, local test-stack management, pushes, PR creation/updates and GitHub reads. The user retains merges, self-approval prevention, repository permissions/rules and credential changes. Live Jira use and external live mutations need explicit authorization. |
| D27 | Persist checkpoints after artifacts, review rounds and validation. Resume verifies baseline, revisions, finding states and Git/CI facts; changed inputs invalidate affected approvals. Check incomplete operations before retrying; reconstruct missing/inconsistent state from evidence, never assumed approval. |
| D28 | Reviewer unavailability gets bounded retries, then review-pending checkpointing; independent work may continue. Codex cannot substitute its own review or count partial output as approval. Failed attempts consume execution budget, not a completed review-fix cycle. |
| D29 | Interface supports start (interactive discovery/plan review/plan PR), continue (verify merged approval and execute), status and resume. Decision requests are durable. Initial user communication is terminal output and PR records, without external notification integrations. |
| D30 | Default unattended execution budget is eight hours, configurable at start/resume. Execution, retries, tests and experiments consume it; waiting for user approval does not. Exhaustion checkpoints and produces a handoff, without weakening gates. |
| D31 | One delivery slice executes at a time. Independent reviewers may run in parallel on the same frozen revision. Variants use separate worktrees. Docker lifecycle operations and runtime tests are serialized. |
| D32 | Bootstrap manually using the agreed stages, Codex authorship and Claude review. An unfinished controller cannot certify its own development. Unimplemented enforcement remains an explicit manual step. |
| D33 | Require a fixture trial before the isolation pilot. Fixture plans, implementation and review records stay off main, on a dedicated authoritative integration branch created from a recorded orchestration revision. The user merges fixture plan/implementation PRs into that branch. General orchestration improvements use separate PRs to main without fixture content. |
| D34 | Use both agent instructions and controller enforcement. A small Python controller was proposed for mechanical workflow rules, with versioned guidelines for agent reasoning; detailed component design remains to be reviewed. |
| D35 | Record observed rule deviations: rule/version, role/model/stage/revision, action/output evidence, whether enforcement caught it or it escaped, correction/outcome/escalation. Include these in run review records and final PR summaries. Significant delivery failures may become DPLs; do not infer intent. |
| D36 | For a first recoverable violation, reject the action and permit autonomous correction within budgets. Baseline/security changes still require approval; a violation never grants authority. |
| D37 | Reviewers are instructed/configured for read-only reviewed inputs and disposable probe workspaces; privileged runtime validation is routed through the orchestrator. These are not assumed security guarantees. Probe restrictions and label each boundary enforced, detected afterward, instruction-only or unverified. Worktrees are not sandboxes; same-user execution may retain host/credential access. No malicious-agent containment or extensive sandbox infrastructure is authorized by this honest-mistake PoC. |
| D38 | The tests stage writes executable tests from the approved plan/requirements/design before behavior implementation. Use minimal interface skeletons derived from approved detailed design, so red results are meaningful rather than import errors. Record red output, failure type and intended cause; passing positive controls; and, for security-relevant paths, evidence that a targeted protection-removal/weakening mutant makes the test fail for the intended reason. Verify the mutant reaches the exercised path; mutation is evidence of sensitivity to that fault, not complete security proof. Lock reviewed assertions to accepted revisions/hashes. Implementers cannot silently change them; a genuine defect returns to the tests stage for within-baseline correction and independent re-review. Hash checks detect changes rather than preventing writes. If runtime proof is genuinely unavailable before implementation, allow explicitly provisional acceptance with outstanding evidence recorded; mocks are not deployed proof. Final acceptance requires outstanding positive-control and targeted mutation evidence. |
| D39 | The architecture stage includes detailed interface contracts: inputs/outputs, errors, state transitions and security responsibilities, at enough detail to derive skeletons/tests without inventing behavior. Review these before the tests stage. Use the existing authoritative architecture document and source-level DD conventions; do not add a separate detailed-design stage or parallel authoritative document. |
| D40 | A successful fixture trial is required for the user's final orchestration PR approval, not just before the OPL pilot. Bind the trial to the exact tested candidate orchestration revision, with later record-only changes qualified by D53, and include results, observed deviations and remaining limitations in the PR. Fixture design, implementation and review records remain on their dedicated branch. |
| D41 | Initial artifact-specific checklists cover feature/slice plans, test plans, requirements, architecture/detailed design, unit tests, E2E tests, implementation code, configuration/deployment, documentation/operational instructions, and process rules/checklists/orchestration definitions. Plan review checks problem/scope, decisions/alternatives, slice dependencies, approval boundaries, assumptions, success criteria, assets/risks and retirement. Test-plan review checks proof coverage and test levels, independent expected outcomes, fixtures and evidence. UT and E2E have separate maturity/acceptance criteria; neither substitutes for an obligation at the other level without an approved proof-strategy change. One test_plan.md may contain both, receiving all applicable planning checks. UT often supports meaningful red through approved skeletons; E2E runtime proof may remain explicitly provisional until deployment. Every artifact also receives the mandatory shared holistic layer. |
| D42 | Keep a compact machine-readable checkpoint alongside each slice's review documents, versioned in Git, recording stages, counters, pending evidence, reviewed revisions and user decisions awaited. No credentials or raw session transcripts. Human review documents remain the readable history. A checkpoint cannot grant approval: resume reconciles it against review records, Git and CI. Recovery must not depend on one machine's temporary files. |
| D43 | Originating reviewer means a stable per-artifact identity comprising role, model and versioned review instructions, not one immortal process/session. A fresh session may continue using its own original findings, subsequent responses and reviewed revisions. A replacement model cannot silently inherit disposition authority; unavailability follows the retry/escalation policy. |
| D44 | Assess fixture confidence separately for delivery capability, safety, review effectiveness, recovery and decision quality. A clean approved feature must reach a working implementation PR; blanket refusal cannot pass. Distinguish reviewer detection, controller containment and root-cause resolution. A missed defect caught by enforcement proves containment, not reviewer effectiveness. Expected outcomes are independently established before execution. Include scenarios for misleading passing tests, locally plausible root-cause patches, unnecessary mechanisms and genuine baseline conflicts. Expected user approvals are not manual rescue; a rescued attempt is unsuccessful and retained, then improvements require a new candidate and rerun. Fixture success permits the supervised OPL pilot, not a claim of mature orchestration or proof of OPL fixes. |
| D45 | Include two or three independently prepared novel seeds, not cosmetic variations of recorded case law or DPL examples. Novelty is relative to the supplied case law and evaluated agents' context, not a claim about model training data. Freeze expected outcomes and pass thresholds before the run. Keep seed descriptions/answer keys out of supplied reviewer inputs; accidental disclosure invalidates that seed as independent-detection evidence. Access assurance follows D37, not an assumed secret store. Fixture-specific seeds, answer keys and reviews stay off main under D33. |
| D46 | Trial verdict: safety and delivery must pass. Review effectiveness, recovery and decision quality may be partial only where no mandatory obligation is violated, no blocker remains unresolved, and the shortfall is explicitly reported. Safety failures cannot be averaged away as partial reviewer/recovery scores. Report detection, containment, root-cause resolution, false blockers and unnecessary changes separately for each novel seed. Report a missed defect regardless of whether the trial passes; reporting alone is not success. |
| D47 | Recovery must preserve completed review-fix counts and in-progress cycles. Reject silent counter rollback; replayed reviewer results count once. Test interruption between reviewer completion and checkpoint persistence. Cycle three is permitted; unresolved blockers afterward escalate rather than start cycle four. Revisions, new findings and upstream corrections do not reset counters. Only explicit user authorization extends the limit, and that authorization must itself survive restart. Counter failure is a mandatory safety failure, not an acceptable partial recovery result. |
| D48 | Fixture acceptance uses applicable existing validation checks, fixed in the approved trial matrix. The controller verifies successful GitHub conclusions against the reviewed/tested revision and intended PR base; failed, missing or stale checks cannot count as a successful trial, even if the PR was merged. This verifies acceptance rather than preventing direct merges by the user or an agent sharing credentials. No new fixture-branch ruleset is required initially. |
| D49 | Plans/amendments require a verified GitHub merge attributed to the configured user account, into the intended branch and bound to approved artifact revisions. Waivers, decision answers and review-cycle extensions require an explicit GitHub comment from that account identifying the decision, affected baseline, scope and expiry where applicable. Agent-written checkpoints/summaries cannot grant approval. Shared credentials establish account attribution, not proof of human action: outside controller-routed operations, the prohibition on agent approval/merge remains instruction-only until separate identity controls exist. Do not silently assume issue #20 is implemented. D58 is the specific user-authorized exception: a verified user merge of this plan/amendment carrying that waiver's exact scope, rationale and expiry is also valid evidence for D58 only. A generic plan mention, agent-written text or agent merge does not activate any waiver; other waivers retain the explicit-comment requirement. |
| D50 | Supply the plan, test plan, applicable authoritative documents and relevant source whenever needed for review, with exact wording, revision provenance and approval status. Do not hide agreed plans/designs or replace them with author-generated summaries to avoid review-history exposure. The withheld material is the slice's review-comment documents, including plan-review comments and author responses, during a fresh independent first pass. Re-review receives the originating reviewer's own findings and corresponding responses/fixes; integrated review receives complete history in its second pass. Substantive decisions reached during review must enter the approved plan/authoritative documents, not remain authoritative only inside review comments. This supersedes the proposed broader exclusion of checkpoints/Git history as a blanket rule; the concrete input assembly must preserve authoritative context while respecting D10/D23 and label its actual assurance under D37. |
| D51 | The user requested publication secret scanning as its own proposed slice, tracked in issue #21, not scanner implementation within delivery-orchestration. Propose automatic coverage of publishable repository content, existing evidence outputs and generated PR text without per-file registration. The separate slice requires its own grill-me, reviewed plan/test plan and user approval. PLN-008 remains open: issue creation is neither implementation nor waiver, and publication integration/sequencing must be resolved before claiming the gap addressed. |
| D52 | The orchestrator manages only test stacks it created or the user explicitly authorized it to take over. Existing unowned/unknown-ownership stacks require explicit takeover approval before lifecycle operations; pause affected runtime work and continue independent authorized work. Resume verifies ownership against checkpoints and Docker metadata. Preserve each run/variant's evidence before resetting an owned stack. Serialization alone does not establish ownership; outside controller-routed commands the restriction is instruction-only unless separately enforced. |
| D53 | Define a narrow allowlist of record paths, frozen with the user-approved trial baseline, instead of enumerating tested input types. Every candidate repository path outside that allowlist is a tested input by default. Acceptance compares its identity/content hash, executable mode and symlink target against the exact tested commit, including additions, deletions and renames; missing/unreadable comparison inputs cannot pass. New folders/file types outside the allowlist therefore invalidate the trial automatically. The candidate cannot widen/change its own comparison exceptions: changing the allowlist requires approval and invalidates the previous comparison/trial. Record directories cannot supply executable code, standing prompts, checklists, configuration or approved plans/designs. Later record-only changes may preserve the trial when non-record inputs match and an independent reviewer confirms record-only status; keep the original tested commit and comparison evidence. This proves repository-input equivalence, not unchanged external services, environment variables or images, and waives no other review, CI or publication requirement. Implement the check within existing controller acceptance verification where suitable, not necessarily as a new standalone CI job. |
| D54 | The user directed adding an expiry to the separate publication-scanning tracker and proceeding, rather than making it a new hard orchestration prerequisite. The agent selected a 30-day default: review/expiry 2026-12-01, recorded in issue #21. Preserve the missing additional scan coverage as a dated user-directed deferral, not a fixed finding or implemented protection. Existing no-secrets rules remain in force; no permission to publish secrets or claim comprehensive scanning is granted. Revisit at expiry, without silent renewal or automatic closure. |
| D55 | Blind fixture trials use a separate task workspace with complete fixed/seeded fixture feature authority, not this orchestration meta-plan. Evaluated agents receive applicable process rules/checklists and all fixture problem, plan, test-plan, requirements, design and source inputs relevant to their stage. The independently prepared evaluation matrix/answer key is held separately by the trial coordinator, approved and hash-committed before execution, and withheld from evaluated agents. Expected findings must follow visible fixture authority, not hidden requirements. Fixed-baseline defects or contradictions must be reported/escalated rather than silently rewritten. Preparation/evaluation contexts are distinct; record actual supplied inputs and tool reads, invalidate independent-detection credit on known or uncertain disclosure, and make no OS-isolation claim. Fixture-specific content and evaluation records stay off main. This is a narrow trial-context exception; normal D50 review context remains complete. |
| D56 | Revision binding is a general delivery guarantee, not a fixture-only safeguard. Every authoring, fixing, test and review operation uses designated authoritative documents, process rules/checklists and task-source revisions, recording actual input identities/approval status and output revisions. Latest branch state or a pull is not evidence of the correct approved baseline. Check input identity at start and result/dependency applicability before acceptance; missing or uncertain binding stays pending, and relevant changes reopen affected work/reviews without resetting counters. Expected output edits do not authorize baseline changes. The fixture tests this same guarantee, including stale loaded instructions before a run or on rerun against a newer candidate. The user agreed this generalization; it does not itself authorize another exhausted review cycle or waive findings. |
| D57 | Following the fixture-scope audit, generalize evidence reuse/approved record-policy ownership, applicable CI conclusions, independent verification of initial and later changed acceptance logic, separate detection/containment/root-cause outcomes, and honest human-assistance/autonomy reporting to ordinary delivery. The approved feature/slice baseline owns the shared record policy; missing approval grants no exclusions. Every holistic/fix review checks the underlying failure class for other stages/artifacts, with a concrete counterpart or justified local scope; generally applicable corrections belong in general authority and fixture tests exercise them. This does not expand approved design/threat scope or authorize unrelated fixes. Assisted normal delivery may pass normal review/validation without qualifying as autonomous success. Hidden seeds/answer keys, dedicated fixture branches and rescue-fails-trial scoring stay evaluation-specific. No finding waiver, cycle reset or additional review cycle is implied. |
| D58 | The user grants the temporary missing-publication-scan-coverage waiver for all new folders and documents we create outside the current checked paths (test_report.log, artifacts/rogue-tests/, artifacts/quality/), including new contents in those folders. Reason: the broader scanner remains its separate deferred slice. Expiry stays 2026-12-01 end of day UTC. Existing no-secrets obligations and current checks remain mandatory; this grants neither actual secret publication nor a scanner-implementation claim. Pre-existing unscanned content is not automatically included by editing it. This direct session decision grants current manual-work authority; future controller admission binds to D49 user-approved evidence, including user merge of the plan recording the waiver, not an agent-created GitHub approval. Preserve the known finding as scoped/time-limited user-waived, not fixed; no silent renewal. |
| D59 | The user requests per-review cost/usage visibility and deliberate high/medium effort instead of an unknown default or routine extra-high. Explicitly pass medium for routine focused reviews/rechecks and high for initial plan, security, architecture/state/trust-boundary and integrated reviews; record rationale for high on broader rechecks. Other effort levels need explicit user decision. Collect metadata-only per-attempt requested/reported model/effort, duration, turns/tool calls, uncached/cache-read/cache-write/output tokens and provider USD estimate, including failed/retried/probe calls. Deduplicate invocations and token subsets, preserve missing data and historical effort as unknown, and distinguish estimates from actual subscription billing/quota. Backfill available logs now and pin effort in the next launcher; this authorizes narrow manual-review telemetry support, not stage-controller or feature implementation. |

## Requirements

The plan PR approves the behavior obligations below and decisions D1–D59. The requirements stage
formalizes those obligations in `docs/requirements.md`; it does not authorize inventing new
behavior. Architecture and executable tests similarly elaborate the approved baseline. Every
normative addition must trace to an approved obligation; ambiguity or a changed guarantee follows
D7/D49 rather than being legitimized by a stage review. Allocate final REQ/ARCH/DD/test IDs during
the relevant stages without reusing existing IDs.

| Obligation area | Required behavior | Decision sources |
| --- | --- | --- |
| Discovery and approval | Feature discovery, explicit slice authorization/dependencies, exact branch/revision approval and no agent-granted authority | D2–D3, D6–D8, D26, D29, D33, D49 |
| Staged delivery | Requirements, architecture/interfaces, executable tests, implementation and integrated review; invalidated dependencies reopen | D4–D5, D32, D38–D39 |
| Review integrity | Different author/reviewer models; mandatory primary/specialist coverage; deduplication without suppression; attributable dispositions, bounded cycles, user-only waivers and independent verification of changed acceptance logic | D1, D9–D14, D23–D25, D28, D43, D47, D57 |
| Checklist completeness | Both complete layers, typed/mixed artifact coverage, evidence-specific answers, reviewer-confirmed N/A, no unauthorized downgrade, failure-class scope check and user-approved learning | D18–D22, D41, D57 |
| Records and authority | Preserve all issues, input/provenance records and user decisions; bind stages to designated revisions and reuse policy; distinguish outcomes/assistance; collect per-invocation effort/usage/cost with honest unknowns; checkpoints do not grant approval | D15–D17, D24–D25, D27, D35–D37, D42, D49–D50, D56–D57, D59 |
| Execution limits | Configurable active-time budget, persistent retries/cycles/variants, one active slice and serialized owned-stack runtime operations | D8, D13, D28–D31, D47, D52 |
| Accepted tests | Approved interfaces, meaningful red, positive controls and targeted security mutants; provisional evidence and controlled test corrections | D38–D39 |
| Trial and confidence | Off-main fixture, independent seeds, predeclared thresholds, clean delivery, safety, honest partial results, tested-input equivalence and complete fixed fixture authority separated from the evaluation key/meta-plan | D33, D40, D44–D48, D53, D55 |
| Publication boundary | No secrets/private reasoning in records; additional scanning remains a separate slice with a dated user-directed deferral and D58 scoped user waiver, not implemented protection | D25–D26, D42, D51, D54, D58 |

These are the requirements to add or change at the subsequent specification stage, not a claim
that the runtime or its proofs already exist. Existing service requirements and security
guarantees remain unchanged.

## Success criteria

- Approved slices proceed unattended to an inspectable implementation PR, with mandatory reviews
  and validation bound to exact input versions and recorded revision/proof provenance.
- Controller-routed execution cannot grant approval from its own writes, unresolved blockers or
  incomplete required proof. Direct same-account actions remain the explicitly instruction-only
  residual; tests must not claim mechanical prevention outside that boundary.
- The user can inspect each artifact's review history in one document and all discovered issues
  in the final handoff, including issues deferred or outside the threat model.
- Interruptions, unavailable reviewers and budget exhaustion preserve accurate resumable state.
- Instructions and enforcement expose concrete deviations instead of silently repairing the record.
- A live Codex–Claude fixture trial demonstrates the workflow on its dedicated branch, before
  the isolation pilot. A fixture success is not evidence that OPL-005–008 are fixed.
- Freeze the trial acceptance matrix before execution. Safety and delivery must pass; report
  other confidence dimensions separately under D44–D46. A clean case must complete, all seeded
  blockers must be detected or safely contained before acceptance, and no unauthorized baseline
  change or false approval is accepted. Manual rescue makes that attempt unsuccessful, except
  for expected user approvals. Recovery-counter failures are always safety failures.
- Include two or three novel seeds with independently established outcomes; disclosed seeds
  cannot count as independent-detection evidence. No fixture-specific content enters main.
- Fixture acceptance verifies applicable existing CI conclusions against the intended PR base
  and reviewed/tested revision. Merge state alone cannot establish passing validation; the
  controller does not claim to prevent direct merges without repository enforcement.
- Trial reuse after later record additions requires D53's default-input comparison and independent
  confirmation, not an author's assertion that a change is harmless. All non-record content must
  match the tested commit; other CI, review and publication obligations still apply.

### Evidence reuse and trial invalidation

D57 generalizes D48's CI-applicability rule and D53's record-policy ownership to all deliveries.
D53's strict trial comparison still applies when trial reuse is claimed; ordinary implementation
does not require an identical whole repository while making its approved output changes.

The approved feature/slice delivery baseline owns a narrow record-path allowlist for review,
accepted-test and validation bindings; a fixture trial uses that same approved authority. Exact
paths must be included in the user's plan PR or a user-merged plan amendment under D49 before
use. Design review may propose changes but cannot grant user approval. An absent policy grants
no inferred exclusions. Examples such as `trials/<id>/reports/` and `trials/<id>/evidence/` describe
record-only directories, not permission to relocate existing authoritative documents or put
fixture content on main. Exact review-record file paths may be used to retain the agreed layout.
For this orchestration delivery, merging this plan approves exactly
`docs/slices/delivery-orchestration/plan_review.md` and
`docs/slices/delivery-orchestration/checkpoint.json`, plus the metadata-only
`docs/slices/delivery-orchestration/review_usage.json`, as record-only paths. No directory-wide
exception is granted. Other records, including trial-specific paths, need their relevant approved
plan/amendment; this does not bring fixture contents onto main. These paths cannot supply standing
instructions or executable inputs, and new findings/decisions still require review and disposition.
Ordinary review bindings are default-inclusive over task inputs, not a reviewer-selected subset;
the recorded manifest describes that inventory rather than excluding unlisted paths implicitly.

The acceptance check uses the baseline's allowlist, never an unapproved candidate replacement.
Everything outside it defaults to a tested input, regardless of folder or extension. Compare
candidate repository content against the tested commit for path membership, content hashes,
executable modes and symlink targets. Additions, removals and renames count as changes, and a
comparison that cannot read required inputs is not successful. Changes outside the allowlist
require a new trial; changing the allowlist requires approval and a new trial as well.

Record-only additions/updates do not force a rerun when all tested inputs still match and an
independent reviewer confirms the changes contain only records. Code, standing instructions,
checklists, configuration and approved plans/design cannot gain exemption by placement in a
record directory; implementations must not use those directories as sources for those purposes.
Retain the exact tested commit plus the later candidate/comparison provenance. This is not a
claim of identical external dependencies or runtime state, nor permission to skip validation
of the new records themselves. D48's applicable CI requirements remain in force. D51/D54 record
the dated publication-coverage deferral, not a new scanner-completion prerequisite.

### Execution identity, comparisons and final acceptance

These implementation-design obligations are proposed for the user's plan approval, not claims
of existing enforcement. Merging this plan makes this section binding under the obligation areas
above: execution/comparison under trial and confidence/accepted tests, final admission under
discovery and approval, receipt/recovery under records and authority/execution limits, and
approval attribution under review integrity. Architecture may elaborate but not silently drop them.

**Designated revisions throughout delivery — D56.** Apply the same revision-binding rule to
ordinary feature development and fixture trials. Before every author/fixer/tester/reviewer
invocation, identify the designated authoritative problem/plan/design, process rules/checklists
and task-source revisions with approval status. Supply their actual contents and record resolved
paths, revisions and content identities, including automatically loaded instructions. Compare
actual inputs to the designated baseline before starting; do not equate latest branch state with
approved authority. Missing, mismatched or uncertain inputs keep the affected operation pending.

Identify immutable authority/dependencies separately from artifacts the stage is meant to change.
Record resulting output revisions; ordinary implementation edits do not themselves amend the
approved design. Before accepting a result, verify the reviewed/tested output identity and input
binding still apply. Relevant input changes reopen affected validation and originating reviews;
unaffected work may continue. Existing approved record-only equivalence remains narrow, and
current CI obligations remain in force. Restarts and upstream corrections do not reset counters.

**Governing authority versus rulebook outputs — every delivery.** Every invocation uses the
designated approved instruction/checklist revision plus explicit user instructions. If a stage
changes AGENTS.md, CLAUDE.md, nested instructions or checklists, those changed copies are task
artifacts to examine, never governing instructions for their own review or later unapproved stages.
Apply the two-source-domain separation to ordinary delivery too: use a separate authority context
and task-artifact view, or disable task-tree automatic loading and explicitly supply approved
authority. Verify/record which authority actually loads; merely changing the working directory
is insufficient if a CLI imports instructions from searched/read task paths. Missing assurance
keeps that invocation pending. Architecture specifies the CLI mechanism without a new workflow gate.
This permits rule-changing features to proceed under approved rules without adopting their outputs.

For the fixture, the designated process instructions are the pinned framework candidate's files
at their resolved paths, checked for path/hash/mode/link equality before and after invocation.
Missing counterparts or initial divergence invalidate proof, even without any mid-run edit.
Before rerunning against updated instructions, update the fixture base through the planned user
merge or a newly approved target; do not silently overwrite its integration ref. The fixture's
fixed feature documents remain its feature authority, not this meta-plan. A fixture feature that
changes loaded process instructions cannot certify the unchanged pinned framework under this setup.

**Two source domains.** Run the orchestration framework from a clean, pinned candidate checkout.
Run the fixture feature in its separate task checkout/branches. Record the framework executable,
resolved resource paths, candidate commit, clean state and actual code/instruction/checklist hashes
for every invocation; compare before/after execution. Do not execute a task checkout's modified
copy of the controller, or silently load its changed framework instructions. If loaded framework
inputs differ, invalidate the trial and rerun against a newly pinned candidate. Task artifacts and
their evolving source manifests are separately identified; fixture additions are not compared to
the orchestration candidate as if they were record-only changes. D53 compares the later main
candidate to the pinned orchestration commit actually exercised, never the fixture's feature tree.
Automatically loaded task-tree instructions (including AGENTS.md, CLAUDE.md and nested instruction
files applicable to each invocation) are framework inputs too. Record their resolved identities;
a task edit that changes loaded instructions invalidates the trial rather than silently changing rules.

**One comparison primitive, distinct obligations.** Use D53's path/hash/mode/link comparison for
review/trial input binding rather than a raw head-SHA equality that changes when records are
committed. Declare the immutable input manifest for each binding; all bindings use the same
user-approved record-path allowlist. No candidate/controller-created exception is permitted.
A reviewer-confirmed record-only follow-up preserves source review/trial applicability, not a new
CI conclusion. Gate-consumed files, including OPL statuses, test specifications and configuration,
remain inputs even if their names look like logs. Finalize those close-out files before freezing
the candidate, or rerun affected proof after changing them. Do not pre-write passing results.
Final CI must cover the actual candidate/tested merge, including records, and current target-base
identity; record-only source equivalence cannot substitute old CI for a new head or base.

For ordinary delivery as well as fixture trials, CI facts include candidate head, tested base and
merge/ref identity, not merely a matching branch
name. A base update makes old merge-context checks stale. Missing provenance requires the proper
CI run or a pending handoff, never treating a dispatch run in the wrong PR mode as equivalent.
Keep provider validation completion in its authoritative run/operation receipt; do not create an
endless new source commit solely to say that the previous head's CI finished. Git checkpoints are
reconciled caches; actual GitHub conclusions remain authoritative.

**Trigger, not a self-declared final flag.** The approved orchestration execution plan requires
a live trial at its final user-handoff transition. The controller reads that requirement from the
merged baseline, not from candidate text or the presence of a receipt. For this slice it is required.
A missing/failed/stale binding refuses that transition. Work-in-progress CI and nested fixture PRs
run the mechanical tests without requiring the outer trial to have completed, avoiding recursion.
The existing tooling job proves the acceptance verifier with positive/negative controls; it does
not mean every CI invocation is final delivery acceptance. The actual final transition inspects
real pinned trial records and CI facts. Manual bootstrap performs the same check independently.

Future changes to orchestration behavior/standing instructions require their approved plan to
declare a new trial; unrelated feature delivery is not a fresh certification of the orchestration
tool. Reuse of a previous trial, whenever claimed, still obeys D53's full default-input comparison.
Missing/ambiguous acceptance classification cannot default to no trial. The fixture integration
target is proposed as `trial/delivery-orchestration`, authorized by the user's merge of this plan;
its feature plan is separately merged there. A new target needs user approval.
This plan authorizes the creation-point rule, not a future literal SHA: the controller records the
clean pinned framework candidate commit in the execution manifest when creating the absent ref.

**Accepted-test inputs.** Apply the same primitive at tests acceptance. By default lock all
non-record repository inputs except specific implementation-owned paths identified in the reviewed
design. This permits the intended implementation but not silent edits to fixtures, helper loaders,
test configuration or trace/env gates. Unknown/new input paths are locked until re-reviewed; do
not derive exclusions merely from extensions or folder names. An implementation-owned exception
cannot include a test driver/configuration because that is a convenient place to weaken a test.
Review approves the classification; the controller checks recorded hashes. D53's trial comparison
has no implementation-owned exception: its only exemptions are approved record paths.

**Recovery and controller-owned comments.** Keep one machine-receipt comment on an explicitly
authorized stable feature issue, outside the author branch and independent of replacement PRs.
It contains completed/in-flight
review-cycle operation IDs, counters, source/report hashes and outbound agent-comment IDs, not
secret contents or raw reports. The pinned controller is its writer; use the existing GitHub
adapter/receipt channel, not a ledger branch or a new CI job. This proposed receipt-only write scope
must be exposed in the plan PR before enabling unattended execution.

Reconcile the remote receipt before advancing or updating a local checkpoint. Git reset/rebase/
force-push or a reverted review document cannot lower it; lost reports, conflicting values or an
unreachable receipt leave affected work pending rather than start a fresh budget. Serialize the
single-host writer and make publication/recovery idempotent. Stable approved artifact-bundle IDs
own counters across starts, renames and repartitioning.
An absent/deleted receipt is not evidence of a fresh bundle. Register the stable issue/bundle
identity before the first review; missing registered state or prior-round evidence leaves recovery
pending. Replacing a PR cannot replace the bundle's tracker or reset its counter.

Controller/agent-originated GitHub posts have a distinct machine/request kind, an operation ID
and recorded server comment ID. Reconcile a post by operation ID after a crash before saving its
returned ID. Exclude those IDs and machine envelopes from user approvals, including posts quoting
an approval template. Accept only an explicit decision envelope linked to the known request,
baseline and scope; ambiguous or quoted text is not approval. Direct posts outside the controller
remain the instruction-only shared-account residual, not a mechanically proven human distinction.

**Stack fingerprints.** Before lifecycle calls, require exact container IDs plus matching Compose
working_dir/config_files/service and mount sources for this approved task checkout. Match creation
or scoped user takeover receipts, not project/name alone. A replaced same-named container, another
checkout's mounts, or uncertain `--volumes-from` target pauses cleanup. The observed existing stack
belongs to the other checkout and has not been taken over. Preserve evidence independently before
a permitted reset. Do not introduce per-run project/name migrations or claim subprocess confinement.

**Outcome attribution and user interactions — every delivery.** Report reviewer detection,
controller containment and evidenced root-cause resolution separately, with unknowns explicit.
A contained defect is not proof that the reviewer detected it or that its cause was fixed;
originating-reviewer disposition remains mandatory. Record expected approvals/decisions separately
from human troubleshooting or source changes. An assisted ordinary feature may pass its normal
reviews/validation, but its run cannot be claimed as successful autonomous execution. The frozen
trial matrix additionally enumerates expected approvals, takeover permissions and unavailable-user
cases; hands-on rescue makes that fixture attempt unsuccessful, not ordinary planned approval.
Source/output comparisons and operation IDs must account for observed changes between invocations.
Any unexplained change or interactive intervention defaults to assisted/unknown, withholding the
autonomous-success claim. Record actual evidence and its limits: detection afterward cannot prove
human identity on shared credentials or prevent an out-of-band edit. This applies to fixture
scoring and ordinary-run reporting; expected user approvals have separate decision evidence.

**Independent verification of changed acceptance logic.** The first orchestration acceptance and
later changes to a gate/checker's decision logic, policy, input schema or verification configuration
receive independent examination against
known-good/known-bad evidence, including missing and stale proof. Independently recompute relevant
candidate comparisons and CI binding rather than trust only the candidate's own checker. Reuse
the existing tests and required reviews; this is not a new gate or a requirement to implement a
second full controller. Repeat affected verification when the acceptance behavior changes.
Routine new run evidence uses the existing verifier, not a new certification of unchanged logic.
The Codex orchestrator executes reviewer-requested recomputation using standard Git/path/hash and
GitHub API queries independently of candidate checker code; the originating reviewer specifies
or approves the probe and assesses its outputs/provenance. The bootstrap uses this same routed
executor/reviewer separation, not self-approval by the executor. The reviewer derives/accepts the
known-bad cases from approved obligations before implementation; the checker author cannot set
the expected verdict from observed candidate behavior. Record tool versions/commands, immutable
input identities, results and executor/reviewer attribution. Read-only review does not require
granting reviewers general shell/network access.

Classify checker and transitive helper/configuration/schema/policy/dependency-pin inputs during
design; absent or ambiguous classification defaults to requiring affected verification. Compare
their identities with the last independently verified checker record using the existing default-
inclusion primitive; do not trust an author's unchanged declaration or hash just the entrypoint.
A frozen trial acceptance matrix is decision policy; per-run observations are evidence. Changing
policy requires affected verification, while ordinary new observations use the established verifier.

**Failure-class scope check.** Both the mandatory shared holistic checklist and every fix review
ask whether the observed failure also affects ordinary delivery, other stages or artifact types.
Reference a concrete analogous path or justify local scope. Generally applicable rules live in
general process/design authority, with fixture cases testing them. Proposals that exceed approved
requirements/design/threat scope still go to the user; no automatic scope expansion follows.

## In scope

- Process guidelines, full shared/artifact checklists and structured review instructions.
- Minimal local orchestration, stage transitions, review routing, records and decision handoffs.
- Recovery, execution budgets, comparison-variant isolation and baseline-aware PR targets.
- Automated controller tests and a live fixture trial with explicit review of observed deviations.
- Relevant AGENTS.md/template changes and integration with existing validation commands.

## Out of scope

- Fixing OPL-005–008 before their own approved plan; changing the PoC threat model.
- Malicious-agent-resistant infrastructure, new secret-management systems or production hardening.
- qa_decisions, a separate threat-model document, parallel slice delivery or external notifications.
- Fixture design, runtime implementation or review records merged into main.
- Automatically fixing all discovered debt, automatically waiving blockers or agent merges.
- Implementing or accepting the separate publication-secret-scanning slice; see issue #21 below.

## Separate proposed slice — publication secret scanning

Tracking: [issue #21 — publication secret scanning](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21).
The user requested this scope separation during grill-me. This is a proposal, not approval to
implement a scanner, add a gate or weaken the existing publication requirements.

- **Problem:** The deferred review finding PLN-008 is missing secret-scan coverage for new review
  documents, checkpoints and PR bodies: today's evidence scan covers only its publication roots.
  Existing directory scans discover nested files automatically; no per-file register is proposed.
  Finding IDs are trace references, not hidden policy authority.
- **Proposed coverage:** all tracked repository files and non-ignored new files, including docs
  and review records; existing evidence publication directories even though Git ignores them;
  and generated PR text before submission.
- **Boundaries:** do not scan `.git` internals or intentional private local stores such as `.env`,
  `capiss_keys/` and SPIRE state merely to detect publication leaks. Working-tree scanning does
  not imply Git-history scanning. Source/example false positives need evaluation before approval.
- **Reuse:** evaluate the existing shape-based scanner. Its findings disclose location/type, not
  secret values. Preserve its stated limitations and define unreadable/missing-input behavior.
- **Independent delivery:** the scanner slice owns its requirements, design, implementation,
  positive/negative controls and any proposed gate changes through its own approved plan.
- **Orchestration relationship:** this plan references the publication control and must settle
  its actual integration in the scanner slice. The user subsequently directed a dated deferral
  under D54: review/expiry 2026-12-01, without a new hard orchestration prerequisite. Preserve
  PLN-008 as a known deferred gap, not a fixed finding or implemented protection. Existing
  no-secrets rules remain in force; no permission to publish secrets is inferred.
- **Upload safety:** today's `PUBLICATION_SET` also selects CI-uploaded artifacts. Broader scan
  coverage must not accidentally broaden uploads to source or private local files.

## Assets and holders

- Runtime K1–K8 assets and holders in `security/invariants.yaml` remain unchanged by this plan.
- Host Codex/Claude authentication and GitHub credentials are used through their tools, outside
  prompts, evidence and review records. Agents may not change credentials or repository authority.
- Reviewers need independent investigation with restricted writes. Probe the concrete execution
  design, including scratch-space probes and inherited tool integrations; record each boundary's
  enforcement category under D37 rather than claiming inaccessible host credentials or files.
- Docker access has host-level effects; retain existing serialized lifecycle rules and identify
  test-stack ownership before allowing execution under D52. An unknown/pre-existing stack is
  not implicit permission to clean it. Do not treat worktrees as runtime isolation.
- Live Jira credentials/actions are not authorized by this slice's unattended permission.

## Environment facts

Read-only probes performed during 2026-11-01/02; overnight observations are identified below:

| Probe | Result | Limit |
| --- | --- | --- |
| `git rev-parse --short HEAD` during orientation | `805cc03`, main | Future approval checks must use live revisions. |
| `command -v codex`; `codex --version`; `codex exec --help` | Codex CLI 0.165.0, non-interactive execution available; read-only PATH-alias warning | No successful model call or authentication established by these probes. |
| `command -v claude`; `claude --version`; `claude --help` | Claude Code 2.1.316, non-interactive execution available | No successful model call or authentication established by these probes. |
| `claude auth status --json`, filtered to status/method/provider only | Authenticated, claude.ai, firstParty | No credential values inspected or printed; status alone does not prove a working model call. |
| Tool-disabled Claude print-mode probe, restricted mode, empty MCP configuration, no session persistence, 45-second timeout | Sandboxed attempt timed out without output; one elevated retry returned `REVIEW_PROBE_OK`, reporting `claude-opus-5-5`, no permission denials | Establishes a working model call under elevated execution, not effectiveness of file/tool restrictions or completion of an artifact review. |
| Read AGENTS.md and CI/Makefile at base `805cc03` | Base rules assumed main, unlimited review rounds and Codex-first reviewers | The plan PR proposes explicit rulebook alignment; no controller enforcement is claimed. |
| `gh api user`, selecting account metadata only | Authenticated account is `gunaseelan-sivanandam` | Shared user/agent account attribution is not proof of human action. |
| Repository metadata API, selecting visibility/default branch/permissions only | Public repository, default branch main, current account has admin/push permission | No setting or credential changed; agent merge prevention is not a GitHub permission boundary here. |
| Ruleset 26054924 API, selecting conditions/enforcement/rule types | Active; includes only `refs/heads/main`; pull-request and required-status-check rules present | Does not establish fixture-branch protection; D48 verifies acceptance separately. |
| Complete initial Claude review with Read/Grep/Glob only and empty MCP config | CLI success, `claude-opus-5-5` in provider metadata, 418.096 seconds, no permission denials; input hashes unchanged | Working review and observed integrity, not proof of OS isolation or forbidden-access denial. |
| Overnight continuation probe, observed by 2026-11-02: `python3 --version` | Host Python 3.10.12 | Do not assume Python 3.11-only host modules; no dependency was installed. |
| Codex CLI configuration metadata plus explicit `--model gpt-6.1-sol` / `model_provider=openai`, ephemeral read-only probe | Exit 0, turn completed, exact `AUTHOR_PROBE_OK`, no command/MCP tool calls | Identity source is configured invocation, not prose; backend revision is not separately exposed. |
| Docker read-only ID/Compose-label/mount-path probe | Existing project compose uses `/home/guna/projects/agentic_iam_spiffe/compose` and mounts that other checkout; server ID starts `85e9c0345645`, agent ID `8e8694697884` | This checkout does not own that stack. No lifecycle or file-content operation was performed. |
| Docker ownership fields on existing server/agent | Compose working_dir/config_files/service labels, exact IDs and mount source/destination paths are available | Project/name alone are insufficient; controller must reconcile these fields and creation/takeover receipts. |
| Search repository for qa_decisions | No existing mechanism found | No such mechanism is planned. |

Do not inspect credential contents to complete environment facts. Record model-call feasibility,
reviewer permissions and non-main validation behavior through bounded, non-secret probes before
approving designs that depend on them.

## Hidden-state and trust decisions

All stores below are metadata/records, not credential stores. Git-versioned records support
honest recovery, not malicious-agent-resistant ledgers. Exact field schemas are architecture work;
writer, reader, lifecycle, decision impact and authority are fixed here.

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Approved baseline and PR target | User-merged plan/amendment plus GitHub merge evidence, pinned to branch/revisions | User approves; controller records evidence | Controller, agents, reviewers | Until approved replacement | Which behavior/slices/branches may execute | Authoritative user-merged artifacts; local copies do not approve themselves |
| Stage input/output binding | Per-invocation input manifest and result record with designated/actual paths, revisions, hashes and approval status | Controller assembles/checks; author/tester/reviewer records result; originating reviewer judges applicability | Stage agents, controller, integrated reviewer | Rechecked at start, acceptance and recovery; relevant dependency changes invalidate affected proof | Whether a result applies to current delivered output under designated authority | Approved authority plus verified identities; neither latest branch nor a successful checkout grants approval |
| Verified acceptance-checker identity | Approved input scope plus recorded identity/comparison and independent probe result, outside candidate-owned approval claims | Controller captures identities; separate originating reviewer accepts verification and corpus; Codex executes routed standard-tool recomputation | Controller, reviewers and user | Until relevant code/helper/schema/config/policy/dependency identity changes; unknown change classification triggers verification | Reuse unchanged checker verification versus require affected independent checks | Attributed reviewer acceptance and independent tool evidence, not candidate pass or author classification |
| Blind evaluation key and disclosure evidence | Key in coordinator-held off-main store outside task paths/refs/history; only approved hash in Git/decision record; supplied-input manifests and available tool-read records in trial evidence | Separate unevaluated coordinator/preparer role, identified in frozen trial matrix and distinct from evaluated Codex/Claude roles; invocation tools record observed reads | User/coordinator sees key; evaluated roles see complete fixture authority but no key; independent final reviewer checks evidence | Freeze key/hash before trial; retain disclosure evidence for acceptance/handoff; known or uncertain disclosure invalidates detection credit | Whether a seed counts as independent detection | User-approved hash plus actual supplied/read evidence, not evaluated agents' assurances; context separation is not OS isolation |
| Slice authorization/dependencies | Approved feature/slice plan and reconciled checkpoint | User approves scope; controller records accepted progress | Controller and reviewers | Feature delivery | Admission and dependency order | Approved scope plus independently evidenced progress |
| Review reports and finding states | Per-artifact review document, completed rounds plus upstream input identities | Attributed reviewer/author outputs; controller assembles | Relevant reviewers and user | Per reviewed inputs, with invalidation on affected upstream change | Stage acceptance or unresolved blockers; preserve applicability across record-only commits | Originating reviewer dispositions and dependency bindings; no author closure |
| Reviewer identity | Invocation/CLI metadata, standing instruction version and role in review provenance | Controller records provider metadata | Controller and reviewers | Per artifact across sessions | Different-model admission and disposition ownership | Verified invocation metadata, not a model's self-description |
| Review effort and usage | Per-attempt launch/usage metadata plus readable review table; historical backfill in review_usage.json | Manual launcher/controller records requested settings; extractor reads provider metadata; user approves policy | User, reviewers and orchestrator | Per attempt, retained across retries; unknown historical settings stay unknown | Cost visibility and deliberate medium/high selection without dropping required checks | Actual CLI request and reported metrics, not assumed backend effort, actual billing or quota share |
| Checklist versions/classifications | Approved guidance plus per-review input manifest | User approves standing changes; controller assembles; accountable reviewer confirms applicability/N/A | All reviewers and controller | Per reviewed revision | Complete review scope, never-N/A and specialist triggers | Approved checklist/classification rules; no unilateral downgrade |
| Accepted test lock | Accepted input manifest: default non-record inputs except specifically reviewed implementation-owned paths | Controller records; originating reviewer accepts scope/corrections | Implementer, controller, reviewer | Until reviewed within-baseline correction | Detect changed assertions, fixtures, helpers, configuration and trace/env gates, including new unknown paths | Accepted scope/hash/mode/link binding, not implementer-supplied exclusions |
| Waivers | Explicit scoped GitHub comment by configured user; for D58 only, verified user merge of this plan/amendment recording exact scope, rationale and expiry is also valid | User only; controller records attribution | Controller and reviewers | Scope/baseline/expiry from user evidence | Whether a specific blocker may be waived | Specific D49/D58 evidence, never generic plan text or agent writes; waived remains distinct from fixed |
| Decision requests/answers | Versioned request, GitHub comment evidence and outbound machine-comment receipts | Controller/agents request; user answers | Controller, agents, reviewers | Until answered/superseded | Pending choice or permitted next action; exclude all controller/agent-originated posts | Explicit user envelope under D49; a baseline amendment still requires merged plan |
| Cycle extensions | User GitHub comment plus checkpoint reference | User authorizes; controller records | Controller and originating reviewer | Specified artifact/baseline/extension | Whether another fix cycle may begin | Explicit user authorization; survives restart |
| Review cycle state | Git checkpoint/review records plus machine receipt on explicitly authorized tracker, outside the author branch | Pinned controller | Controller and reviewers | Stable artifact-bundle identity across resumes/rewrites | Cycle admission and escalation; remote completed cycles cannot be lowered by branch rewrites | Reconciled receipt is counter authority; checkpoint is a cache; uncertainty pauses |
| Time budget | Configured limit, active-operation measurements and reconciled checkpoint | Controller measures/records; user may set limits | Controller and status | Across interruption; explicit resume configuration | Continue, cancel or checkpoint | Measured active work; uncertain time cannot silently become zero |
| Retry state | Per-operation attempt metadata in checkpoint | Controller | Controller and status | Across retry/resume | Bounded retry or review-pending handoff | Operational state, never a review verdict |
| Variants | Branch/worktree registry, approved baseline and preserved evidence links | Controller | Controller, reviewers, user | Until selected/deferred/retired | Three-variant limit and isolation | Experimental only; selection does not itself amend approved design |
| Stack ownership/takeover | Checkpoint, Docker object metadata and scoped user takeover comment | Controller records creation; user authorizes takeover | Controller and reviewers | Revalidated before lifecycle operations/resume | Whether cleanup/rebuild is permitted | Reconciled ownership or explicit takeover, not an arbitrary checkpoint label |
| Fixture identity and trial result | Distinct pinned orchestration checkout and fixture task branch/creation revision, per-invocation resource hashes and off-main proof/CI references | User approves target/plans; controller records actual invocations and evidence | Controller, integrated reviewer, user | Per candidate/trial | Final handoff and pilot admission must match what actually executed | Verified loaded framework identity and frozen trial matrix, not requested branch alone |
| Record-path exceptions | User-approved feature/slice delivery baseline; fixture trial references that policy | User through approval; controller records policy identity | Controller and reviewers | Until approved change; invalidate affected bindings and rerun affected proof, including any required trial | Narrow exception set for review/test/validation input equivalence; absent policy grants no exclusions | Baseline policy, never candidate-supplied wider exclusions |
| Input comparison receipt | Run/review records with original/current revisions and comparison results | Controller; independent reviewer confirms record-only status at required review/handoff | Controller, originating/integrated reviewer, user | Per binding; stale after relevant input change | Whether earlier review/validation, including a trial when required, remains applicable | Input equivalence is not approval, a fresh CI conclusion or environment equivalence |
| Deviations/discovered issues and assistance | Run review records/final handoff with distinct detection, containment, root-cause resolution, unknowns and expected approvals versus human assistance | Controller/agents/reviewers record observed evidence; originating reviewer accepts resolution | User and integrated reviewer | Durable, including unsuccessful/assisted attempts | Corrections/escalation and honest defect-resolution/autonomy claims | Evidence, not permission to fix/waive; assisted delivery validity differs from autonomous-run success |
| Publication deferral and scoped waiver | Issue #21/D54 expiry plus direct user instruction recorded in D58/review record; future controller admission uses D49 approval evidence | User grants waiver; agent records scope without claiming a user-authored GitHub comment | Controller, reviewers, user | Through 2026-12-01 end of day UTC, no silent renewal | Missing additional scan coverage does not block covered new folders/documents during waiver; uncovered/expired scope remains pending | Direct session authorization for manual work; existing no-secrets rules/checks stay in force; waiver is not implementation or secret-publication permission |

Additional decision-significant states:
- **Final-acceptance requirement:** stored in the user-merged execution plan, written by user
  approval and read by the controller/reviewers. It lasts for that delivery baseline and decides
  whether the final handoff requires a live trial. It is authoritative; neither an omitted receipt
  nor candidate-declared finality can disable it.
- **Execution manifest:** controller-produced per invocation, with actual framework/resource hashes,
  candidate/task identities and relevant input/CLI metadata. It is evidence checked at acceptance,
  not permission to execute an unapproved candidate as production.
- **Outbound comment/cycle receipt:** on the explicitly authorized existing tracker, written only
  through the controller's serialized adapter, read before state advancement and on recovery.
  It survives author-branch rewrites and distinguishes machine posts from user decisions.
  Receipt-only issue/PR writes are a proposed scope for plan approval, not already exercised here.
- **Writer ownership:** one single-host controller writer per delivery scope, held for its active
  lifetime and released on termination. It prevents overlapping state/lifecycle operations;
  orphan/unknown operations need reconciliation, not a second writer or a reset budget.

## Authored source changes

- User-authorized manual telemetry now: `scripts/review_usage.py`,
  `scripts/run_manual_review.py`, `tests/tools/test_review_usage.py` and metadata-only
  `review_usage.json`. These small reporting/invocation helpers do not implement the stage
  controller. Record targeted/full tooling validation and remaining limits in the implementation
  log, STATUS and slice index before the plan PR; CI conclusions remain separate provider facts.
- Requirements: formalize the obligation matrix in `docs/requirements.md` after plan approval.
- Architecture: specify the host controller, reviewed interfaces, states and boundaries in
  `docs/architecture.md`; keep existing service architectures authoritative.
- Proof: use the existing static-test/gate model for mechanically verified orchestration
  requirements and their tooling negative controls. Deterministic controller tests are not Jira/
  SPIRE harness E2E. Pin actual live fixture evidence separately as described in the test plan.
- Rulebook in the plan PR: align reviewer selection, bounded fix cycles, explicit target branches,
  staged specification/design/tests, required evidence/N/A completion and finding disposition
  with the user's agreed workflow. These are proposed policy text, not proof of a working controller.
- Implementation after approval: versioned guidelines/checklists, controller, structured records,
  test/trace entries and existing-gate integration. No new standalone CI job is assumed.
- Templates: align plan/test-plan/review fields in implementation while preserving frozen slices.

## Manual telemetry usage

The frozen view contains source/shared/authority directories, each role's own history and prompt,
and a governing_review_authority.txt file. Preview the exact command with authority text redacted:

```sh
python3 scripts/run_manual_review.py /path/to/frozen-view --role primary --cycle 6 --attempt 1 --effort medium --effort-reason "Focused recheck" --dry-run
python3 scripts/review_usage.py /path/to/invocations.json --json-out /path/to/review_usage.json --markdown-out /path/to/review_usage.md
```

The invocation manifest is a JSON list of records with log path, role, cycle, attempt and requested
effort; include requested model, process exit/termination, timestamps and measured wall duration
when known. The wrapper creates an immutable request before launch and a complete per-attempt
usage receipt afterward. Actual invocation omits --dry-run only under the existing authorization;
existing attempt files must never be overwritten. Keep private raw streams outside publication.

## Retirement and compatibility

- Preserve completed slice records unchanged.
- The plan PR replaces the old Codex-first reviewer rule, unlimited review loop, main-only
  approval assumption and single pre-implementation tests step with the user's agreed workflow.
  Current bootstrap follows the user's explicit session instructions and all non-conflicting
  standing rules; the agreed process is executed manually until the controller is accepted.
- Record the reviewer-access trade-off explicitly: the previous rule specified Codex's read-only
  sandbox; the chosen Claude reviewer instead uses configured Read/Grep/Glob-only tools, restricted
  mode and instructions, with before/after input integrity checks. This is not a demonstrated
  equivalent OS sandbox. The user accepted accurate D37 assurance labels rather than assuming
  containment. No write/credential-inaccessibility guarantee is silently retained.
- Remove only superseded process text through review. Do not import the frozen draft's ledger
  branches, main-only assumptions or old removal-of-checks review exemptions.
- Correct OPL-009's promised GitHub merge-rights mitigation to current shared-account facts.
  No implemented protection is removed: GitHub identity separation is still a proposed issue #20
  slice, not delivered by this one. The accepted deliberate-attacker residual remains unchanged.
- Existing main service-security and quality gates remain effective. Fixture branch support and
  trial-reuse exceptions do not weaken them.
- No runtime capability, compatibility endpoint, service secret holder or security control is
  retired by this slice. Publication scanner implementation remains separate under D51.

## Review notes

### Bootstrap and artifact completion

The user's grill-me decisions govern this manual bootstrap as direct instructions; current
non-conflicting repository rules still apply. The plan PR carries the aligned AGENTS.md text,
including different-model reviews, one initial review plus three fix cycles, staged requirements/
architecture/tests and explicit approved branch targets. It does not claim those policies are
already mechanically enforced. Implementation still waits for the user's plan merge.

A review unit is a declared artifact or fixed bundle, such as the plan plus test plan. One
submission of that bundle consumes one shared cycle after all required reviewers assess it;
member count does not multiply the budget, and renamed/split units cannot reset it.

A required checklist item lacking supporting evidence, or an N/A lacking accountable-reviewer
confirmation, leaves that artifact incomplete. This is not permission to promote arbitrary
advisory improvements into blockers. Only D38's explicit provisional tests-stage acceptance may
carry named runtime evidence forward; final acceptance requires that evidence. The final PR
cannot describe provisional or unverified work as complete.

Authors may propose a reasoned rejection, with evidence, without closing the finding. The
originating reviewer accepts/rejects that response or revises its own classification with a reason.
Three unsuccessful fix cycles escalate; earlier lack-of-progress escalation requires an explicit,
evidenced reviewer judgment (for example repeated unchanged rejected reasoning), never an
orchestrator's silent deletion or a reset of counts.

One review document covers a declared artifact bundle, with every member's revision/hash and
matching checklists identified. The plan and test plan are the plan-review bundle in
`plan_review.md`; other stage bundles use their own review document. UT and E2E checks remain
distinct even when reported in typed subsections of one tests-stage document.

### Review assignment and scope

Every artifact has an accountable primary reviewer. Security-relevant slices require an additional
independent security reviewer; architecture/detailed-design and implementation changes involving
interfaces, authoritative state or cross-component failure behavior require an independent design/
maintainability perspective. The present slice meets both triggers. All reviewers receive both
mandatory layers and all matching artifact checklists, plus their role-specific emphasis; roles
cannot omit matching checks. Record every assignment and any classification uncertainty.

The accountable reviewer, not the consolidator, confirms N/A. Consolidation preserves findings,
duplicates, severity and disagreements. Fresh reviews withhold this slice's review-comment material
but preserve applicable plans/design/source; re-review receives the originating reviewer's history.
The integrated reviewer first assesses independently, then reconciles the complete history.

### Mechanical checks versus judgment

The controller checks identities, revisions, complete checklist selection/fields, required verdict
presence, counters, declared proof, branch/approval facts, hashes and configured action admission.
It does not infer semantic equivalence, adequate evidence, root causes, duplicate meaning or
security soundness from keywords. Those require attributed reviewer judgment. Controller tests
must show a missing/rejected verdict prevents advancement; live fixture evidence assesses judgment
quality separately. Direct host actions remain instruction-only unless a stronger boundary is probed.

### Execution details to specify in architecture

- Explicit review effort: routine/focused reviews and rechecks request medium; initial plan,
  security, architecture/state/trust-boundary and integrated reviews request high. A broader
  recheck may request high with its reason recorded. No implicit CLI default or silent xhigh/max.
  Preserve actual requested versus reported effort separately; absence of backend metadata is
  not proof of the effective level. The next primary focused recheck uses medium; security and
  this bundle's broad design/state review use high. This changes no mandatory checklist coverage.
- Every actual attempt produces a complete metadata-only JSON record and a compact row in
  plan_review.md. JSON retains role/stage/cycle/attempt, model, requested effort/reason and
  reported effort if exposed, provider
  and wall duration, turns/tools, input/cache-write/cache-read/output tokens and reported USD
  estimate. Keep retries/errors/probes visible and historical defaults unknown. Report known
  sums and missing metrics; cumulative final totals are not added to per-message or per-model
  duplicate totals, and thinking is a subset of output. Subscription bill/quota share is unknown.
  The compact table shows role/cycle/attempt, effort, status, duration and USD estimate and links
  the complete JSON. Backfill covers available supplied logs only; earlier feasibility probes
  without logs are excluded from row and missing-invocation counts, not assumed free.
  The user explicitly authorized a small manual-review usage extractor and metered launcher now;
  these do not implement stage orchestration, grant review approval or authorize feature runtime.
- Manual-review CLI feasibility: local Claude Code help documents `--safe-mode` as disabling
  CLAUDE.md/customization loading while preserving auth. A tool-free safe-mode/restricted probe
  returned `SAFE_MODE_PROBE_OK`, exit 0, provider model `claude-opus-5-5` (2026-11-02).
  Subsequent manual reviews run in a separate authority directory, supply the base rulebook and
  explicit user review instructions, and read candidate rules only as artifacts. This establishes
  configured loading behavior and connection availability, not OS isolation or future controller proof.
  D37 label: configured, with current reviewer in-session observations of no candidate auto-import,
  not a controlled tool-enabled canary test. Codex author-side instruction loading/isolation is
  unverified in the current bootstrap; direct user decisions guide this session and independent
  base-authority review controls acceptance. Architecture must probe author CLI loading and
  control of task-tree/nested instruction imports before claiming unattended separation; if it
  cannot establish designated authority for an invocation, that operation remains pending.
- Probe GitHub PR-run head, event, tested merge/base identity using metadata-only API reads before
  relying on ordinary CI applicability. If provenance is unavailable, keep handoff pending rather
  than use branch name or local reruns. Cancelled, failed, skipped or incomplete required checks
  are not success; no new CI job is authorized merely to avoid an unverified API assumption.
- Classify controller code as QA-gate or DD-tagged under existing conventions; do not silently
  change the standing rule that QA-gate code carries no DD tags.
- Classify each required close-out file (test specification, STATUS, slice index, implementation
  log, OPL and DPL) as gate input, approved record or pre-freeze pointer to run evidence. Resolve
  trial-derived result publication, including trial-found DPL entries, before execution; do not
  invent record exemptions, pre-write passing results or waive same-change obligations implicitly.
- Define checkpoint/output schemas and idempotent operation identifiers using the state inventory.
- Default reviewer calls may use a 15-minute bound (the successful initial review took 418 seconds),
  capped by remaining run time; allow at most two retries after an initial unavailable/incomplete
  call, without resetting the eight-hour budget or substituting reviewers. Classify active slow
  investigation separately from service failure; every attempt is recorded.
- Measure active intervals with a monotonic clock and persist reconciliation facts for restart.
  Unknown elapsed work or orphaned operations cannot silently disappear from accounting.
- Run independent work serially when a slice is paused: no two delivery slices are active together.
  Another explicitly approved slice may proceed only if its dependencies are accepted and it does
  not use the paused slice's unresolved artifacts or stack.
- Keep reviewer source inputs unchanged and record hashes before/after. Use restricted tool
  configuration and metadata-only probes; do not claim OS/credential isolation without proof.
  The extended live review demonstrated successful read/search calls and no permission denials,
  not denial of forbidden paths. Underlying CLI/provider/tool permissions must pass preflight for
  unattended operation; current-session escalation is not assumed absent in another environment.
- Verify model identity from invocation configuration and CLI/provider metadata, not its prose.
- Verify PR base at creation and again when accepting its merge; fixture and main are distinct targets.
- The fixture feature plan remains complete and visible under D55. Do not silently remove approved
  fixture design to manufacture blindness. Concrete trial scenarios cannot relax D44–D48/D53.

### Agreed blind-trial context boundary — D55

D55 resolves D45/D50 for blind trials. Evaluated agents receive a separate fixture task workspace
containing the complete fixed/seeded feature plan and supporting authority relevant to their stage,
plus applicable delivery rules and checklists. They do not receive this orchestration meta-plan
as their feature plan. The controller uses the pinned framework and approved orchestration
configuration separately; its evaluation instructions and answer key are not worker task authority.

An independent seed preparer works outside evaluated author/reviewer sessions. The coordinator
holds the separate user-approved evaluation matrix/answer key, with its hash committed before
execution. Only evaluation answers/seed locations are withheld, never fixture requirements needed
to justify a finding. Expected outcomes must be derivable from visible fixture authority and rules;
hidden requirements cannot be used to fail an agent. Seeded authority stays fixed: agents report
defects/conflicts and follow escalation, rather than silently repairing the baseline to fit a fix.
Approve only the key's hash through the D49 decision/merge channel; do not publish its contents
there. Keep the key outside supplied task paths and reachable task-repository refs/history. This
is a context-selection obligation, not a same-user filesystem access-control claim. Reachable or
uncertainly disclosed answers receive no independent-detection credit.

Record exact supplied-input identities and available tool-read logs. Known disclosure or insufficient
disclosure evidence invalidates independent-detection credit. Separate folders/context views are
not OS sandboxes. Preparation and evaluation contexts remain distinct even with the same model
family. Fixture documents, seeds, answer keys and fixture reviews stay off main under D33; actual
fixture content is not created by this planning change. D50 remains unchanged for normal reviews.
The frozen matrix also names each attempt's starting task revision. Prior-attempt fixes and
reachable reports count as disclosure for affected seeds; inherited fixes are not new detection.
Reruns need an approved starting revision with undisclosed seeds, or explicit loss of detection
credit. If mandatory criteria cannot then be met, pause for the required fixture decision rather
than overwrite the integration ref, silently recycle seeds or relabel the failed attempt.

### Publication scanning — dated user-directed deferral

The user rejected making the separate scanner a new hard orchestration dependency and directed
an expiry in its tracker, then continuation. Issue #21 records review/expiry 2026-12-01, selected
as a 30-day default on 2026-11-01. Preserve the finding and disclose the absent additional scan
coverage; do not claim it implemented, silently renew the deferral, or automatically close the
issue. Existing no-secrets obligations and available checks remain unchanged. The originating
reviewer must record the disposition of this user-directed scope decision rather than the author
closing PLN-008 as fixed. The plan PR exposes the deferral and the user's D58 waiver separately.

The user has now granted the temporary waiver in D58 for all new folders we create (including
their new contents) and new documents outside the current checked paths: test_report.log,
artifacts/rogue-tests/ and artifacts/quality/. This includes new review/checkpoint documents and
new PR descriptions as publication documents. It covers the missing additional scanner coverage,
not permission to publish secrets or to bypass existing checks. Existing unscanned content is not
automatically covered merely because it is edited. Reason: the broader scanner is a separate
deferred slice. Expiry remains 2026-12-01 end of day UTC; no renewal is inferred.
Edits to pre-existing tracked source/documents continue under the pre-existing publication rules;
this waiver introduces no new pause for ordinary baseline edits and grants no waiver for them.
The missing-additional-coverage pause concerns new publication that depends on that coverage,
outside the granted scope or after expiry. Existing no-secrets rules/checks always remain active.

The direct user instruction authorizes this waiver for current manual work. It is not an
agent-created approval or a claim that the user posted a GitHub comment. Future controller
admission must bind the waiver to user-approved evidence under D49, including the user's merge
of this plan recording D58; an agent's transcript summary alone does not satisfy that admission.
PLN-008 remains a known gap, waived only within this scope/time, never fixed. Out-of-scope or
expired publication pauses for the required decision while unaffected work may proceed.

Current originating-reviewer dispositions, outstanding findings, user decisions and review-cycle
accounting are recorded in `plan_review.md`. Stage-controller/feature implementation requires plan
approval; D59's narrow manual telemetry helpers were separately authorized by the user.
