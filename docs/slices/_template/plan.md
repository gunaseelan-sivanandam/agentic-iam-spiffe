# Slice Plan

## Goal
- Describe the slice outcome in one paragraph.

## Grill-Me Review Summary
- Record the agreed design choices from the `grill-me` session.
- Capture the important questions that were resolved and the final answer for each one.

## Requirements
- List the requirements that this slice adds, changes, narrows, or depends on.
- For each requirement, describe the runtime-visible behavior that must be true.

## Success criteria
- List the externally visible behaviors that must be true when the slice is complete.

## In scope
- List what this slice changes.

## Out of scope
- List what this slice does not change.

## Assets and holders
- Which keys, sockets and secrets this slice touches, adds or moves, and who may hold each one
  (`security/invariants.yaml` and the `REQ-SEC` requirements). If none, say so explicitly.

## Environment facts
- Facts outside the repository that a decision depends on (file ownership and modes, APIs, CI
  history, runtime behaviour), each with the probe that established it and its result. If none, say
  so explicitly.

## Governing rules and task artifacts
- Identify the approved authority revision and instruction/checklist sources for each stage,
  including automatically loaded files. Record their user-approval provenance separately from
  in-progress artifact status; proposed rules cannot govern their own review.
- List rulebook/checklist files this slice changes as output artifacts and specify how invocations
  receive approved rules while reading those changes as data. If loading cannot be verified,
  the operation remains pending; do not designate the unapproved task tree as authority.

## Evidence reuse and acceptance verification
- List exact record-path exclusions for the user's plan-PR approval, or explicitly state none.
  Later exceptions require a user-merged plan amendment before use; design review is not approval.
  Review bindings include all task inputs by default; existing test-lock implementation exceptions
  are a separate reviewed classification, not trial/review record exclusions.
- Identify checker logic and transitive verification configuration/policy/schema/helper inputs
  affected by the slice. Unknown checker-input changes require verification; routine new evidence
  alone does not. Name the independent review and recomputation tools/evidence provenance.

## Hidden-state and trust decisions
- If the slice depends on hidden state, list:
  - state/key name
  - store/system
  - writer
  - reader
  - TTL or lifecycle
  - decision impact
  - authoritative vs advisory
- If no hidden state is introduced or changed, say so explicitly.

## Authored source changes
- Requirements:
- Architecture:
- Runtime proof:
- Rulebook (`AGENTS.md`): process rules this slice adds or changes, or none.

## Retirement and compatibility
- List what old logic, compatibility behavior, docs, tests, or artifacts must be removed or kept temporarily.
- If nothing is retired, say so explicitly.

## Review notes
- Record any assumptions that must be approved before tests or code begin.
