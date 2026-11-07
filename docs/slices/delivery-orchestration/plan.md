# Slice Plan — delivery-orchestration

Status: Revised planning draft, 2026-11-07. Awaiting user approval; no implementation authorized.
Tracks [issue #16](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/16).
Proof obligations are in [test_plan.md](test_plan.md); historical findings, dispositions and
usage are preserved in [plan_review.md](plan_review.md). Earlier approvals cover earlier
candidates, not this revision.

## Goal

Deliver reliable orchestration in usable increments. The user chooses the orchestrator and role
assignment. Codex-authored work is reviewed by Claude; Claude-authored work is reviewed by Codex.
The result is a local controller that can carry an approved feature through reviewed artifacts,
implementation and validation to an inspectable implementation PR, without granting itself
approval or changing the approved baseline. Each increment states what it actually proves.

The concrete problems are unauthorized scope/stage advancement, unsupported review conclusions,
lost findings/counters, stale evidence and validation or handoff claims that exceed their proof.
The current session's premature AGENTS.md edits are a regression case, not a new delivery power.

## Planning-only approval boundary

This change contains only the plan, test plan, review records and slice-index registration.
AGENTS.md, templates, guidelines, specifications, helpers, executable tests and operational
records are changed only after the user merges the plan, through the applicable delivery stages.
Slice 0 is future text implementation; it is not permission to edit the rulebook in this PR.

A user merge approves the stated obligations and ordered capability boundaries. Each slice still
needs reviewed requirements, design/interfaces, tests, implementation and review, scaled to its
scope. A text-only slice states why runtime tests are inapplicable. Unresolved interfaces or
behavior cannot be invented during implementation; return to planning for the user's decision.
Fixture contents, seeds, expected outcomes and run limits need their separate reviewed plan and
user approval before execution. This plan does not approve the isolation pilot's security design.

## Ground rules

- **Roles:** Record the user-selected orchestrator, author/fixer, reviewer, model identity and
  approved authority revision at delivery start. Review assignment follows the author, not the
  orchestrator's name. There is no same-model fallback. An unavailable required reviewer leaves
  review pending. Changing roles does not reset counters or silently transfer finding authority.
- **Authority:** The user retains plan/baseline approval, merges, waivers and review extensions.
  No agent changes the threat model. A baseline conflict pauses affected work; investigation and
  independent authorized work may continue, but an agent cannot adopt an amendment.
  Before execution, verify the user's plan merge into the intended approval branch and the
  approved artifact revisions; latest branch state is not approval. Decision comments must be
  attributable to the configured user and identify the decision and affected baseline/scope.
- **Review scope:** Every artifact receives the shared holistic layer and all matching artifact
  checklists. Required specialists follow security/interface/state triggers. The author/fixer
  never reviews its own output; no consolidation can suppress original findings or disagreements.
- **Finding decisions:** Preserve and report every discovered issue with disposition, including
  pre-existing, advisory and out-of-model issues. Discovery does not authorize a fix. Blocking
  findings need a concrete unmet obligation, correctness/security failure, contradiction or
  missing required proof under the approved PoC model. Evidence-backed author disagreements
  go to the originating reviewer; only that reviewer accepts a resolution or revises its finding.
- **Limits:** One initial review plus at most three fix cycles per declared artifact/bundle.
  A cycle is a fix/response submission assessed by all required reviewers. Incomplete attempts
  do not count as completed cycles. Only the user extends the limit. Renames, upstream changes,
  role changes or implementation-slice boundaries cannot reset a review unit's consumed count.
- **Effort and resources:** Explicit medium/high effort on every model review. Focused rechecks
  use medium; initial plan, security, architecture/state and integrated reviews use high. Record
  the reason and requested/reported settings; missing effective effort is unknown. Default active
  execution budget is eight hours, configurable by the user; user-wait time is excluded. Allow
  at most two retries after an unavailable/incomplete call within the remaining budget.
- **Inputs:** Bind every invocation/result to designated authority, task inputs and output identity.
  Task-tree AGENTS.md, CLAUDE.md and nested instructions cannot replace approved authority.
  Missing or uncertain loading/binding leaves acceptance pending. Recheck affected evidence after
  input changes. Changed rule files are review artifacts until approved and adopted.
- **Proof:** Mechanical checks prove routing, identity and evidence admission, not semantic review
  quality. Record judgments with supporting evidence. N/A requires accountable-reviewer confirmation;
  security protections, trust boundaries and proof cannot be dismissed through unsupported N/A.
- **Action boundaries:** Each new action arrives with its controls. GitHub writes require actor,
  target and approval checks; implementation requires accepted-test locks; Docker requires exact
  ownership checks. Worktrees and tool configuration do not establish OS or credential isolation.
- **Execution:** One active delivery slice. Independent reviewers may share frozen inputs; Docker
  operations are serialized. No unattended continuation before slice 3. Before then, interruption
  requires manual reconciliation, never an automatic fresh start.
- **Records:** One review document per declared artifact/bundle, one finding format, metadata-only
  usage per attempt and durable decisions/handoffs. Preserve completed reports verbatim. Do not
  publish raw model reasoning, private streams, tokens or credentials.

## Delivery sequence

The dependency order is **0 → 1 → 2 → 3 → 4a → 4b → 5 → 6 → separately approved pilot**.
Completion means the slice's applicable obligations and proof pass, with no unresolved blocker
or missing mandatory evidence. Earlier capability completion is not overall autonomy readiness.

### Slice 0 — Rules match user decisions

**Outcome:** Text-only AGENTS.md/template alignment: user-selected roles; both author/reviewer
directions without same-model fallback; review limits; explicit medium/high effort; unchanged
threat model; preservation/reporting of issues; finding format and per-artifact/bundle records.

**Acceptance:** Rulebook/template review checks consistency with these user decisions and the
approved baseline. `make qa-quality` passes; slice 1's plan review subsequently uses the merged
rules. Edited rules cannot govern their own review: approved pre-change authority plus explicit
user instructions govern slice 0. Text checks do not claim runtime enforcement.

**Still manual:** All coordination, execution, finding handling and validation.

### Slice 1 — Reliable review in both directions

**Outcome:** A launcher with `--reviewer claude|codex` reviews one identified artifact at a fixed
commit, using explicit approved rules and a recorded author/reviewer assignment. Record resolved
input identities, loading method, before/after hashes, findings, outcome and per-attempt usage.
Configure source review for read/search-only access with disposable probes where needed; record
what was actually restricted rather than inferring confinement from unchanged source hashes.
Develop the shared holistic review guidelines and artifact-specific checklists for plans, test
plans, requirements, design/interfaces, unit tests, E2E tests, implementation, configuration,
documentation and process/orchestration changes. Version and review them before use.

Create separate controller requirements/architecture homes and extend existing trace tooling to
read both controller and service sources without weakening existing checks. These specifications
cover introduced behavior and interfaces; later slices extend them before enabling capabilities.

**Acceptance:** One real review of Codex-authored work by Claude and one of Claude-authored work
by Codex, with matching positive/negative controls. Probe both CLIs' authority loading, including
Codex's exclusion of task-branch AGENTS.md and nested instructions. Wrong rules, changed inputs,
partial output or reviewer failure cannot produce an accepted result. Review-unit identity and
cumulative cycle count are required; an exhausted budget is refused before launch. Unknown counts
require manual reconciliation. A report is evidence, not authority to advance a stage.

**Still manual:** Authoring/fixes, adjudication, review-cycle coordination and stage advancement.
Real calls establish invocation behavior, not the live delivery/evaluation claims of slices 5/6.

### Slice 2 — One controlled stage with fix cycles

**Outcome:** Run one explicitly authorized requirements or design stage: author, review, fixes,
originating-reviewer rechecks, then stop at handoff. Add authoring/fixing guidance for those
artifacts. Implement finding handling here, where the controller first coordinates fix cycles.

**Acceptance:** The intended artifact is produced and reviewed. Record permitted outputs separately
from immutable authority. Changes outside the authorized outputs are detected and leave acceptance
pending; do not claim write prevention. Include AGENTS.md-edited-during-planning as a regression:
the edit is an output violation and cannot become governing authority. Refuse early advancement
and agent-written approvals. Blockers require originating-reviewer dispositions; authors cannot
close them. Waivers require explicit authorized-user evidence, affected scope, rationale and
expiry. Open blockers after cycle three escalate to the user, without an automatic fourth cycle.

**Still manual:** Recovery after interruption, all other stages and external publication.

### Slice 3 — Interruption and recovery

**Outcome:** Resume slice-2 operations without losing findings, repeating completed actions or
resetting limits. Persist compact checkpoints, operation identities, reviewed inputs, result
status, counters and active time. Reconcile against recorded evidence before continuing.

**Acceptance:** Interrupt before/after launch, result capture, result publication and checkpoint
writes. Replayed results count once; orphaned operations require reconciliation before retry.
Counters and consumed time survive ordinary crashes. Missing/conflicting state remains pending.
Publication at this stage means local review/result records; controller-operated GitHub writes
are not introduced until 4b. History-rewrite-resistant accounting remains explicitly deferred.

**Still manual:** Connecting stages and all external publication.

### Slice 4a — Stages connected through implementation

**Outcome:** Connect requirements → design → tests → implementation using the accepted review
and recovery capabilities. Add test-authoring, implementation and fixing guidelines. Each stage
uses reviewed upstream contracts; relevant corrections reopen affected downstream reviews/proof.

**Acceptance:** Deterministic flows with simulated agents exercise the real controller. Tests
precede behavior implementation, with meaningful red results, positive controls and targeted
security-protection mutants; import errors are not meaningful red. Reviewer-approved assertions,
fixtures, helpers and configuration are locked. Silent changes, including new unclassified inputs,
are detected and require tests-stage review. Intended implementation output paths are explicitly
reviewed; an implementation exception cannot authorize weakening the tests or their driver.
Final implementation acceptance cannot omit provisionally outstanding runtime/mutation proof.

**Still manual:** Validation, Docker operations, integrated handoff and implementation PR.

### Slice 4b — Validation and handoff

**Outcome:** Add validation, fresh integrated review and an implementation PR. The integrated
review first assesses original intent and delivered artifacts, then reconciles finding history.
Add validation/handoff guidance. Introduce controller-operated external writes only with controls.

**Acceptance:** Required GitHub conclusions match the actual head, intended base/tested merge
and required event/mode. Failed, skipped, missing or stale checks cannot be replaced with a local
rerun or merge status. Writes use verified `gunaseelan-agent`, correct repository/base and scoped
authorization; agent-originated text cannot grant user approval. User merges remain permanent.
Docker lifecycle actions require exact object IDs, Compose working-directory/config labels and
mount paths matching a controller creation or explicit user takeover record. Unknown/replaced
objects pause affected work; preserve evidence before reset. Serialize lifecycle operations.

**Still manual:** User approvals and merges, permanently. Live effectiveness remains unproved.

### Slice 5 — Clean live delivery

**Outcome:** Deliver a small, separately approved fixture feature off main using actual Codex
and Claude calls. The user-approved fixture plan names supported orchestrator/author/reviewer
assignments, expected approvals, starting revisions, run bounds and acceptance thresholds.

**Acceptance:** A working implementation PR with all required reviews and validation for every
supported role assignment, including Codex authoring and Claude authoring when both are supported.
Do not infer support for an untested orchestrator/role assignment. Record interventions, usage,
limitations and failed attempts. Expected approvals are normal; troubleshooting or manual rescue
makes that attempt assisted and cannot earn autonomous-completion credit.

**Still manual:** User decisions/merges and preparation/evaluation of blind seeds. A clean run
proves delivery capability for that case, not resilience to unseen failures.

### Slice 6 — Failure evaluation and improvements

**Outcome:** Evaluate seeded defects, misleading evidence, outages, interruptions and genuine
baseline conflicts, then correct and rerun within the approved baseline. The independently
prepared fixture matrix freezes expected outcomes before execution, separately from evaluated
agent inputs. Include two or three novel seeds beyond known regression cases.

**Acceptance:** Safety and delivery must pass: a clean case completes; seeded blockers are detected
or safely contained before acceptance; no unresolved blocker, unauthorized baseline change,
false approval or counter bypass. Report reviewer detection, controller containment and evidenced
root-cause resolution separately. Report review effectiveness, recovery and decision quality
without averaging away mandatory failures. Failed/rescued attempts remain failed records.

For every rerun, pin the corrected framework and approved starting task revision. Earlier fixes
and reachable reports count as disclosure; inherited or disclosed fixes earn no fresh detection
credit. Missing starting-state/disclosure evidence leaves the relevant verdict pending. Fixes
within baseline may proceed; new scope/guarantees require the user's approved amendment.

**Gate:** Successful slice 6 is required before the separately approved isolation pilot
([issue #17](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/17)). It proves no
OPL-005–008 fix and does not claim mature or production-grade autonomy.

## Requirement, design and record ownership

- `docs/requirements.md` and `docs/architecture.md` retain service/product authority.
- Slice 1 creates `docs/orchestration_requirements.md` and `docs/orchestration_architecture.md`
  for controller obligations, interfaces, errors, state, assets and permission responsibilities.
  They are planned paths, not existing specifications. Use existing REQ/ARCH formats with unique
  IDs and the existing trace system; reject duplicates across both domains. No new CI job.
- AGENTS.md owns standing contributor rules; guidelines/checklists operationalize them without
  replacing requirements. Their versions are inputs to invocations, not author-written approvals.
- Each enabled capability names state, writers/readers, lifetime and invalidation: role assignment,
  approved revision, findings/dispositions, counters/time, operations, accepted tests and CI facts.
  Checkpoints reconstruct execution; they cannot independently grant approval.
- Findings record stable ID, role/model, reviewed revision, severity/criterion, exact location,
  problem, evidence, consequence, baseline relationship and resolution criteria. Responses record
  cause, fix or evidence-backed disagreement, and originating-reviewer decision with reason.
- Usage records include role/stage/review unit/cycle/attempt, model, requested/reported effort,
  duration, turns/tools, uncached/cache-read/cache-write/output tokens and provider cost if exposed.
  Include failures/retries/probes, deduplicate invocation copies, preserve unknowns, and do not
  double-count thinking already in output. Estimates are not subscription charges or quota shares.

## Deferred obligations and limits

These mechanisms are not prerequisites for slices 0–5. Slice 6 may expose a need, but does not
automatically authorize their addition. Any addition needs evidence, reviewed scope and user
approval. Some also catch honest mistakes; deferral is not proof they are solely anti-tampering.

| Deferred mechanism | Simpler behavior and unclaimed guarantee |
| --- | --- |
| D8 automated comparison variants | Investigate/escalate baseline conflicts without automatically constructing variants. No autonomous variant-selection claim. |
| D53 record-only trial reuse | Bind trial success to the exact evaluated framework commit. Another candidate needs fresh proof; do not carry success forward using an author-declared harmless change. |
| Machine-receipt GitHub comments surviving force-push | Use ordinary durable records for crash recovery. Rewritten, missing or inconsistent history requires manual reconciliation; do not claim independent rollback-resistant counters. |
| D57 exhaustive transitive checker-dependency verification | Defer comprehensive automated dependency certification. Review acceptance logic with known-good/bad cases; changes to known consumed helpers/configuration invalidate affected evidence. Do not claim only the entrypoint matters. |
| Hash-committed evaluation answer keys | Independently freeze dated, version-identified expectations outside evaluated contexts. Keep preparation/evaluation distinct; uncertain provenance or disclosure cannot earn independent-detection credit. No cryptographic precommitment claim. |

Other D57 obligations remain: applicable CI proof, honest attribution, issue preservation and
checking whether a fix's underlying failure affects other enabled stages. No general license to
reuse stale evidence follows from deferring dependency automation.

## Threat model, assets and scope

The approved PoC model remains honest delivery mistakes, not deliberate attacks by agents on
CI, evidence or orchestration infrastructure (OPL-009). The rogue-workload system-under-test
boundaries remain in scope. No agent may expand or narrow either model without user approval.

Runtime assets/holders in `security/invariants.yaml` remain unchanged. Host model/GitHub
credentials are used through tools, never copied into prompts or records. The user controls
credential/repository-authority changes. Probe CLI instruction loading and restrictions before
claiming them; label boundaries enforced, detected afterward, instruction-only or unverified.
Same-user processes and worktrees do not establish host/credential isolation.

Fixture authority, feature code, seeds and detailed trial records stay on the approved off-main
fixture target (proposed `trial/delivery-orchestration`); the user merges its plan/implementation
PRs. Before one-time target creation, record the clean framework commit as the creation point;
never overwrite an existing target. Run the framework from that pinned source separately from
the evolving fixture task tree. Agents receive complete visible fixture authority needed for
their task, not this meta-plan as feature authority or hidden evaluation answers. Main may retain
candidate-bound outcome summaries and evidence references, not fixture contents.

Out of scope: OPL isolation fixes, malicious-agent containment, production hardening, parallel
slice delivery, external notifications, automatic debt fixes, agent merges or self-granted waivers.

## Publication and validation

Publication scanning remains separate in
[issue #21](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21). Existing
no-secrets rules and publication checks stay mandatory. Historical D58 waives only missing
additional scan coverage for new folders/documents and their new contents outside the current
checked roots (`test_report.log`, `artifacts/rogue-tests/`, `artifacts/quality/`), because the broader
scanner is deferred. Expiry: **2026-12-01 end of day UTC**. It is waived, not fixed; no secret
publication, silent renewal or waiver for pre-existing unscanned content is inferred. Dependent
publication outside that scope or after expiry needs the user's decision. Preserve the historical
PLN-008 finding. This is not a new scanner prerequisite or permission to broaden uploads.

Use existing validation targets and applicable review/trace conventions. `make qa-quality`,
required E2E/evidence checks and actual-head CI keep their existing meanings; a reduced diagnostic
is not a full pass. Earlier OPA image-user inspection failed; establish the current cause and
resolve it or obtain an explicit user disposition before claiming slice-0 quality completion.
Do not silently add that deployment fix to the text-only slice or weaken its gate.

## Historical decision disposition

This plan replaces the earlier two-slice schedule and stale live-environment/CLI/version probes.
Prior decisions remain historical in Git and the preserved review record; they are not a second,
conflicting source of current instructions. The principal changes are:

| Earlier decisions | Current disposition |
| --- | --- |
| D1, D9, D43 | User-selected orchestrator; two-way cross-model review; stable originating-reviewer authority, with no silent replacement. |
| D2–D7, D17, D26, D32, D34, D39 | Retain discovery, staged review and approval boundaries; implement standing rules only in post-merge slice 0, then capabilities incrementally. |
| D8 | Automated variants deferred as listed above. |
| D10–D16, D18–D25, D28, D35–D38, D41, D59 | Preserve review independence, evidence, finding/disposition, issue and effort/usage obligations; introduce their controls with the consuming slices. |
| D27, D29–D31, D42, D47 | Recovery from slice 3; no earlier unattended continuation. Retain limits/serialization; history-rewrite-resistant receipts deferred. |
| D33, D40, D44–D46, D48, D50, D52, D55–D56 | Bind enabled operations to authority; add ownership/CI controls with 4b; clean trial in 5 and failure evaluation in 6. Pilot waits for 6. Cryptographic key commitment deferred. |
| D49 | User approval and scoped waiver admission remain; distinct agent/owner identities, not shared-account assumptions or host isolation claims. |
| D51, D54, D58 | Separate scanner and scoped/dated coverage waiver retained; no scanner implementation here. |
| D53, D57 | Apply the explicit deferral/retained-obligation boundaries above. |

Historical model approvals and usage totals are not current acceptance. Six completed fix cycles
remain consumed for this plan-review bundle; this schedule does not reset that counter or grant
another model review. Current implementation/runtime support remains unproved until delivered.
