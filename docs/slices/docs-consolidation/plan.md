# Documentation Consolidation — Slice Plan

## Phase Status
Phase 1 approved 2026-10-27 (decisions below). Increment 1 in progress.
No runtime behavior changes in this slice; no requirement, architecture, DD, or test IDs change.

## Problem (measured 2026-10-27)
- 69 tracked Markdown files / 9,355 lines; three overlapping hand-written test specs, none covering
  M5 (58 of 120 E2E tests). No process document required updating them, so they drifted from 2026-05-16.
- The project status log lived in gitignored `docs/local_status_capture/`; no clone could see current state.
- Two slice formats (legacy 8–9 file bundles vs current `plan.md` + `test_plan.md`); the slice index
  listed 3 of 11 slices.
- The global `~/.claude/CLAUDE.md` and repo `AGENTS.md` prescribed conflicting conventions
  (ID scheme, paths, test layout, gate strictness).
- README examples referenced test IDs that do not exist (`M5.S1-T1`).

## Approved Decisions
| # | Decision |
| --- | --- |
| D1 | `AGENTS.md` is the single rulebook for this repo, rewritten to match what the repo actually enforces. Repo `CLAUDE.md` imports it and states it overrides global conventions here. `tests/unit/AGENTS.md` stays as the unit-test appendix. |
| D2 | The status log is tracked: moved to `docs/history/implementation_log.md` (secret-scanned first). A short tracked `docs/STATUS.md` answers "where are we". |
| D3 | One hand-written test spec: `docs/test_spec_detailed.md` becomes `docs/test_spec.md`. The other two are archived. Updating it becomes a Phase 4 rule. |
| D4 | Retired material is archived with `git mv`, never deleted. Measured history size is 2.1 MB compressed (docs 0.9 MB), so archiving has no meaningful clone cost. |

## Target Layout
```
README.md              humans: what/why, run the lab, doc map
AGENTS.md              rulebook (process, IDs, gates, commands, guardrails)
CLAUDE.md              imports AGENTS.md
docs/
  STATUS.md            current state
  requirements.md      authoritative (unchanged)
  architecture.md      authoritative (unchanged)
  test_spec.md         hand-written E2E spec (was test_spec_detailed.md)
  unit_test_spec.md    unit matrix (read by `make traceability-check`)
  open_problem_log.md  open runtime/trust problems
  SECURITY_MODEL.md    pending review in Increment 3
  history/             implementation_log.md, REDTEAM_M3.md
  archive/             retired test specs and unreferenced diagrams
  slices/              README index, _template/, current-format bundles, archive/ (legacy bundles)
```

## Hidden-State Decisions
None. No runtime, Redis, file, cache, or policy state is touched.

## Increments
1. **Rulebook and structure (this increment).** Rewrite `AGENTS.md`; add `CLAUDE.md` and `docs/STATUS.md`;
   track the log; archive two test specs, legacy slices, `REDTEAM_M3.md`, and the unreferenced
   `container_architecture` diagram; rename the detailed spec; rebuild the slice index; fix README
   (doc map, test ID example, status location); update `open_problem_log.md` and `unit_test_spec.md`
   references; fix `tests/unit/AGENTS.md` scope.
2. **Test spec completion.** Write the M5 section of `docs/test_spec.md` by hand (M5-T1..T59) and add a
   check that every harness test ID appears in it.
3. **Content review.** Fold still-true parts of `SECURITY_MODEL.md` into `architecture.md` and archive
   the rest; add a `make docs-check` (links resolve, renders referenced, slice index complete, spec
   ID completeness) to CI.

## In Scope / Out of Scope
- In: documentation files, `.gitignore` entry for the old status folder, `CLAUDE.md`.
- Out: requirement/architecture content changes; the 87 requirements without E2E (OPL-002);
  refactoring functions above the complexity target; editing implemented slice bundles (they are
  frozen records — their stale references to the old status path stay as written).

## Retirement
- Retired (archived, not deleted): `docs/test_spec.md` (guard listing) and `docs/test_spec_readable.md`
  → `docs/archive/`; legacy slices `m2-verified-client-requests`, `m4-observability-closure`,
  `m4-semantic-trace-closure`, `m4a-jira-project-access`, `m4b-jira-description-write` →
  `docs/slices/archive/`; `docs/container_architecture.{puml,svg}` → `docs/archive/diagrams/`;
  `docs/REDTEAM_M3.md` → `docs/history/`.
- Removed: the `docs/local_status_capture/` gitignore entry and folder (content moved, now tracked).
- No compatibility paths kept.
