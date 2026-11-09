# Slice Plan

Plan of slice `<slice-id>`: one sentence on what the slice delivers and why. Replace this paragraph;
it is the document's purpose line (`AGENTS.md`, coding rule 8).

## Goal
- Describe the slice outcome in one paragraph.

## Stages

Each stage of `AGENTS.md`'s slice workflow applies, or is "none, with a reason".

| Stage | Applies | Review list or reason |
| --- | --- | --- |
| Discovery | yes | `plan-and-test-plan` |
| Requirements | yes, or none: <reason> | `requirements` |
| Architecture and interfaces | yes, or none: <reason> | `architecture-and-interfaces` |
| Tests first | yes, or none: <reason> | `unit-tests`, `e2e-tests` |
| Implementation | yes, or none: <reason> | `code` |
| Final review | yes | final mode, no list |
| Handoff | yes | the user's approval |

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| <slice>-D1 | One decision per row; with a grill-me, the agreed answer to each question it resolved. | the user, <date>, <link> ("<the user's words>"); or default by the author: <reason> |

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

## Checks this slice adds
- For every new check or process step (gate, job, document, register, exception class, review
  step): the failure it catches, what it costs, and the simpler alternative that was considered.
  The user approves each addition. If the slice adds none, say so explicitly.

## Rule deviations
- One line per rule of `AGENTS.md` this slice does not follow: the rule, the deviation, the user's words
  with the link, and the expiry. If none, say so explicitly.

## Retirement and compatibility
- List what old logic, compatibility behavior, docs, tests, or artifacts must be removed or kept temporarily.
- If nothing is retired, say so explicitly.

## Review notes
- Record any assumptions that must be approved before tests or code begin.
