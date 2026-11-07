# Test Plan — delivery-orchestration

Status: Revised planning draft, 2026-11-07. No executable tests or runtime changes in this PR.
Authority: [plan.md](plan.md). Original review evidence remains in [plan_review.md](plan_review.md);
previous candidate approvals/results do not certify this revision.

## Proof strategy

Prove each capability when it is introduced, with passing positive controls paired with concrete
negative cases. Mechanical tests exercise the actual controller/launcher/adapters with simulated
agent outputs where appropriate. They prove admission and routing, not model judgment. Real
review calls start in slice 1; live delivery is slice 5; independent failure evaluation is slice 6.
No deterministic substitute or schema-only pass satisfies a live or semantic-proof obligation.

Each implementation slice derives expected outcomes from the approved plan and reviewed contracts,
existing assertions or identified pre-implementation probes. Do not infer them from candidate
behavior. Assign executable test/trace IDs at its tests stage. Meaningful red, applicable positive
controls and targeted security mutants must have attributable evidence before final acceptance.
No new CI job or parallel trace system is proposed.

## Slice 0 — Rulebook and templates

| Proof | Required observation |
| --- | --- |
| Decision consistency | AGENTS.md/templates express user-selected roles, both cross-model review directions, no same-model fallback, review limit, effort, threat-model boundary, issue preservation and finding/review-record formats. |
| Authority separation | Slice-0 edits are reviewed under the pre-change approved authority plus explicit user instructions, not their own unmerged text. |
| Scope | Only approved text outputs change; runtime/helper changes cannot be counted as text-only completion. |
| Quality and adoption | `make qa-quality` passes, and slice-1 plan review uses the actual merged rule revision. No local claim substitutes for merge provenance. |

The previously observed OPA image-user failure is an outstanding verification issue, not an
accepted quality result. Resolve its cause or obtain explicit user disposition without silently
expanding slice 0. Text review is the behavior proof here; no invented runtime tests.

## Slice 1 — Review invocation and guidelines

| Area | Positive control | Negative control / required response |
| --- | --- | --- |
| Both directions | Actual Claude review of identified Codex-authored work and actual Codex review of Claude-authored work produce attributable complete reports. | Self/same-model review or an unsupported role assignment cannot count; unavailable counterpart leaves review pending. |
| Authority loading | Both launchers demonstrably load designated approved rules and relevant artifact context. | Task-branch AGENTS.md, nested instructions or CLAUDE.md containing a distinguishable conflicting instruction cannot govern the review. Configuration flags alone are insufficient proof. |
| Revision binding | Fixed artifact commit and resolved input paths/hashes match before/after the invocation. | Wrong rules, missing input, initial mismatch or input change during review leaves result unaccepted. |
| Review completeness | Shared holistic and all matching artifact checklists, required specialists and supported findings/verdicts are present. | Missing/partial output, unsupported N/A, reviewer error or an omitted applicable checklist cannot become acceptance. |
| Limit admission | Initial review and permitted cycles launch with recorded stable unit identity/count; third fix cycle is allowed. | Exhausted, missing or inconsistent accounting refuses launch; retries do not reset counts. Until slice 3, uncertainty needs manual reconciliation. |
| Effort and usage | Explicit medium/high setting and rationale; complete per-attempt metadata and honest unknowns. | Silent CLI defaults, unapproved levels, retries omitted, duplicate invocations/thinking counted twice, estimates represented as billing or private streams in telemetry fail acceptance. |
| Trace integration | Existing tooling reads valid controller and service requirements/architecture. | Cross-domain duplicate/unknown IDs, broken links or new unaccepted coverage gaps fail existing checks. |

Run authority-loading probes with harmless distinguishable instructions and record observed
loading/tool behavior; do not claim forbidden-path or OS isolation from a successful invocation.
Reports cannot independently advance delivery or adopt findings as fixes. All fix coordination
remains manual at this slice. Checklists cover the artifact types listed in the plan.

## Slice 2 — One stage and originating-reviewer fix cycles

| Area | Positive control | Negative control / required response |
| --- | --- | --- |
| Stage scope | Explicitly approved requirements or design task changes its named output artifacts, receives review and stops at handoff. | Wrong stage, unauthorized file change or early next-stage invocation is detected/refused and acceptance stays pending. |
| Planning regression | Approved authority remains loaded while reviewing task artifacts. | AGENTS.md edited during planning is detected as an unauthorized output and cannot govern its own review or a later stage. No write-prevention claim. |
| Role/identity | User-selected orchestrator and author/reviewer identities remain recorded throughout fixes. | Changing author/model cannot bypass independence or silently transfer originating-reviewer authority; pending findings/counters survive. |
| Finding handling | Fix or evidence-backed disagreement receives originating-reviewer disposition with reason. | Author/consolidator closes or downgrades a blocker; distinct findings or disagreements disappear; acceptance is refused. |
| Waiver | Explicit authorized-user evidence identifies baseline, scope, rationale and expiry. | Agent-authored summary, ambiguous decision, missing fields, expired/out-of-scope waiver or wrong user cannot grant authority. |
| Cycle boundary | Initial review plus up to three collectively assessed fix cycles; success on cycle three allowed. | Open blockers after cycle three escalate; no fourth cycle, rename reset or multiplication by parallel reviewer count. |
| Review quality record | Evidence supports checklist answers and issues retain dispositions, including deferred advisories. | Boilerplate/string presence substitutes for semantic judgment, author-only N/A or automatic advisory fixes cannot establish completion. |

Tests inspect actual controller decisions and output changes, not only prompts. Interrupted runs
remain pending for manual reconciliation; automatic resume is not an acceptance obligation yet.

## Slice 3 — Recovery and budgets

Exercise interruption immediately before and after launch, result capture, local result
publication and checkpoint persistence. Simulate a lost response after an action completes.

| Positive control | Negative control / required response |
| --- | --- |
| Reconcile evidence and continue from the correct pending operation. | Blind retry duplicates execution; incomplete evidence is treated as success; leave pending instead. |
| Replayed result is attributed and counted once. | Crash between assessment and persistence drops or doubles a completed cycle. |
| Findings, decisions, completed/in-progress counts and consumed active time survive restart. | Stale checkpoint lowers counts, a fresh budget erases consumed time, or missing time grants unlimited work. |
| Bounded reviewer retries end in review-pending state. | Failure produces same-model fallback, partial approval or unlimited retries. |
| Expected user wait does not consume active execution time. | Unknown elapsed execution silently disappears or budget exhaustion relaxes acceptance. |
| Missing/conflicting ordinary records require manual reconciliation. | Missing history grants a fresh review unit or an unsupported rollback-resistant guarantee. |

Publication here is local review/result recording. No machine-receipt comments, GitHub mutation
adapter or force-push-resistant counter authority is required. Test compact checkpoint schemas
against raw prompt/reply/environment payloads; schema checks alone do not prove all records secret-free.

## Slice 4a — Stage dependencies, tests and implementation

| Area | Positive control | Negative control / required response |
| --- | --- | --- |
| Connected stages | Simulated agents complete requirements → reviewed design → accepted tests → implementation through real controller routing. | Missing/rejected artifact or unresolved blocker cannot be skipped; refusing every flow cannot pass. |
| Upstream invalidation | A changed consumed input reopens affected reviews/validation while unaffected work remains usable. | Old verdict reused after a relevant authority/design change; apparent latest branch treated as approved baseline. |
| Tests first | Approved interfaces/skeletons yield meaningful red, then passing positive controls and implemented behavior. | Import/environment errors called intended red or expectations derived from candidate output cannot pass. |
| Accepted-test lock | Reviewed implementation-owned outputs may change while assertions and their execution inputs remain fixed. | Modified test, fixture, helper, conftest, loader, configuration or trace/env gate is detected; unknown new inputs cannot silently bypass the lock. |
| Security sensitivity | Targeted removal/weakening mutant reaches each introduced security-control path and its negative test fails for the intended reason. | Unexecuted mutant, argument-only mock or unrelated failure claimed as sensitivity proof. |
| Provisional proof | Explicit tests-stage provisional acceptance records named outstanding runtime proof. | Implementation/final acceptance treats provisional assertions as completed positive/mutation/runtime evidence. |

Semantic judgments remain attributed reviewer decisions. No comprehensive automated transitive
checker-dependency certification is required, but known consumed configuration/helper changes
cannot preserve stale proof. Controller acceptance logic itself receives independent known-good/bad
checks as it is introduced; candidate self-report is not its sole verification.

## Slice 4b — Validation, external actions and handoff

| Area | Positive control | Negative control / required response |
| --- | --- | --- |
| GitHub identity/approval | Verified `gunaseelan-agent` performs a scoped authorized write to the intended repository/base. | Wrong actor, target, approval branch or agent-written approval text cannot grant permission. No agent merge. |
| CI applicability | Required successful conclusions bind to actual head, tested base/merge and appropriate event/mode. | Failed, missing, cancelled, skipped, wrong-mode or stale-base proof remains pending; local rerun/merge status is not a replacement. |
| Docker ownership | Exact object IDs, Compose paths/labels and mounts match creation or scoped takeover evidence; lifecycle is serialized. | Same-name/project objects from another checkout, replaced IDs, uncertain mounts or volumes-from cleanup targets pause affected work. |
| Evidence preservation | Owned-stack reset retains independent run evidence first. | Cleanup destroys only evidence copy or unknown ownership is assumed. |
| Integrated review | Fresh assessment of original intent/delivered artifacts precedes full finding-history reconciliation. | Prior persuasive conclusions anchor the first pass, or unresolved history disappears from handoff. |
| Final handoff | PR contains validation, provenance, dispositions, unresolved issues, assistance, waivers and decisions. | Missing required proof or rejected findings hidden; expected approval confused with manual rescue. |

Mocked external responses test admission logic; approved disposable integration probes establish
adapter behavior. Do not mutate an existing stack or external resource merely to run a negative
control. Existing actual-head CI and required service/E2E/evidence gates retain their meaning.

## Slice 5 — Clean live fixture

Before execution, approve the off-main fixture plan/test plan, authority, expected approvals,
role-assignment matrix, starting revisions, run bounds and success criteria. Framework and task
source are separate; actual loaded framework code/resources match the pinned clean candidate.

- Complete a clean small feature using real Codex and Claude through a working implementation PR,
  with mandatory reviews and validation for each supported assignment. Do not infer an untested
  orchestrator/author assignment from a run in the other direction.
- Record commands/identities, inputs/outputs, expected approvals, interventions, usage and limitations.
  Unknown edits/assistance withhold autonomous-success credit; a rescued attempt remains assisted.
- Blanket refusal or endless escalation cannot satisfy delivery capability. Failed attempts remain
  visible; expected user approvals are part of normal delivery.
- Acceptance binds to the exact evaluated framework commit and task/CI evidence. No automatic
  record-only candidate equivalence or broader runtime/seed-effectiveness claim.

## Slice 6 — Failure evaluation

An independent preparer freezes dated, version-identified scenarios, expectations and thresholds
before the run, outside evaluated contexts. Two or three novel seeds supplement known regressions.
No hash-committed answer key is required. Evaluated agents receive all visible feature authority
needed to justify findings; hidden requirements cannot determine failure. Preparation/evaluation
contexts remain distinct, without an OS-isolation claim.

| Scenario | Required outcome |
| --- | --- |
| Misleading passing test or weakened protection | Defect detected or safely contained before acceptance; proof cannot be silently weakened to match implementation. |
| Plausible local patch or unnecessary mechanism | Review considers the actual cause and approved guarantees; report unresolved cause and unnecessary changes without automatic scope expansion. |
| Genuine baseline conflict | Preserve baseline and obtain user decision; automatic comparison variants are not required. |
| Reviewer outage/interruption | Pending state and accurate recovery preserve counters, findings, time and role independence. |
| Scope/rule drift | Planning-stage AGENTS.md edits cannot become authority; unauthorized output prevents acceptance. |
| Prior-attempt fixes or disclosed answers | Do not credit inherited fixes as fresh detection; uncertain starting state/provenance/disclosure keeps the affected verdict pending. |

Safety and delivery must pass. No unresolved blocker, false approval, unauthorized baseline change
or review-counter bypass can be averaged away. Report reviewer detection, controller containment,
root-cause resolution, false blockers and assistance separately. Other confidence dimensions may
be partial only without violating mandatory obligations.

Retain failed attempts; correct within baseline and rerun affected cases against the exact fixed
candidate and approved task starting revision. A new commit cannot inherit trial success using
a deferred record-only exception. Broader scope or new mechanisms return to user-approved planning.
Successful slice 6 gates the separately approved isolation pilot, not proof of an OPL fix.

## Deferred proof and existing obligations

No mandatory tests for automated variants, record-only trial reuse, force-push-resistant remote
receipts, comprehensive checker dependency certification or cryptographic answer-key commitment.
Instead, test the simpler boundaries in the plan: escalate, require fresh candidate proof,
manually reconcile rewritten/missing history, invalidate known changed dependencies and refuse
unsupported independent-detection credit. Deferral does not authorize stale evidence or dropped issues.

Publication scanner implementation stays in #21. Preserve the existing D58 scope and expiry in
the plan; test scoped user-waiver admission when introduced in slice 2. Existing no-secrets checks
remain mandatory. Protected-service tests remain their own harness proofs; controller/tooling tests
are not relabelled service E2E. No live Jira mutation is authorized by this plan.

## Validation and acceptance records

Use existing docs/trace/tooling/quality targets. Extend the current static-test model for controller
mechanics, with real positive/negative controls, candidate-bound results and handwritten test-spec
entries. Preserve existing coverage/gap checks when adding controller specification sources.

Each slice records applicable checks, results, reviewed inputs and outstanding proof. Required
clean-stack E2E/evidence checks run only on an owned or explicitly handed-over stack; unavailable
proof remains pending. Do not replace full checks with reduced diagnostics or claim CI from a
local run. Text-only and unavailable runtime evidence are classified explicitly through review.
No new model-review cycle is authorized by this document revision.
