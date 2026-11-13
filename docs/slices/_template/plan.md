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
| Final review | yes, or none, small slice | final mode, no list |
| Handoff | yes | the user's approval |

## Small slice
- Small: yes or no. Yes only when all four conditions of `AGENTS.md` (slice workflow,
  [small slices](../../../AGENTS.md#small-slices)) hold; say for each why it holds:
  1. no requirement, architecture section, `security/invariants.yaml` entry or `trace/tests.yaml`
     entry is added or changed:
  2. no test, E2E harness, gate or QA tooling, CI, rulebook, review checklist, slice template, review
     launcher or brief is touched:
  3. no security decision path is touched (capability-issuer, tool-b and the other verifiers, OPA
     policies, Envoy or SPIRE configuration, compose files):
  4. at most about 50 changed lines in at most 5 files: <lines> lines in <files> files.
- A small slice is one PR with this plan, its test plan, its decision page and the change; the stage
  table marks Requirements, Architecture and interfaces and Tests first "none" (conditions 1 and 2)
  and the Final review "none, small slice". If a condition breaks during the work, the slice returns
  to the full stages.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| <slice>-D1 | One decision per row; with a grill-me, the agreed answer to each question it resolved. | the user, <date>, <link> ("<the user's words>"); or default by the author: <reason> |

## Threat model
- The threat model the reviews judge against: the delivery threat model of `AGENTS.md` (PoC scope and
  proportion) applied to this slice's change, and the system-under-test threat the slice touches. A change
  to an approved threat model goes to the user.

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
