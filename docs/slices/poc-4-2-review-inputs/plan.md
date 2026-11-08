# Slice Plan — poc-4-2-review-inputs: review inputs and evidence computed by tools

Plan of slice 4.2 of the agentic-SDLC PoC (issue #39, part of slice 4, #33): the launcher, not the
author, decides which files a reviewer must examine, names the upstream items a change traces to,
and computes the evidence the reviewer gets.

Status: draft, 2026-11-08, revised after plan review round 2. Approved when the owner merges slice
4's single plan PR.

**Order of work:** after 4.1, whose upstream and evidence sections and `accounted` list this slice
fills; before 4.3, which writes the evidence into the record. The whole order is in the
[slice index](../README.md).

## Goal

DPL-005 slipped through because the author's file list left out the workflow file. DPL-010 slipped
through because the reviewer had no coverage evidence and the rechecks took the author's word.
DPL-004 showed a review that never asked where a problem started. This slice makes the review's
inputs deterministic:
- the files under review come from the diff, deleted files included;
- the governing plan and the upstream requirements and architecture items are named in the prompt;
- the evidence is computed by tools, and the reviewer accounts for every entry: uncovered changed
  lines, trace gaps among the upstream items, and the CI results of the reviewed commit.

## Threat model

- **Delivery** (honest mistakes):
  - a changed or deleted file left out of the review;
  - a reviewer judging without coverage or traceability evidence, or ignoring it;
  - evidence the author summarised wrongly, or stale evidence from another commit;
  - a problem fixed where it surfaced while its cause sits upstream;
  - an operational detail (a local path, an account) reaching a public record through the evidence.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S42-D1 | **Files under review come from the diff.** The launcher computes them with `git diff --name-status <merge-base> <commit>`, without the withheld files. Added, modified and renamed files are listed to open. Deleted files are listed in their own part, "deleted by the change: examine in `change.diff`". `--path` becomes optional. A given `--path` must be in the diff and only orders the list (named files first); it never narrows it. | owner, [reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090); plan review round 2, B1 (deleted files) |
| S42-D2 | **Open every file under review** (owner: "keep the rule"). The paths section says so; in a recheck it says to open the files each answer names first (4.1's recheck mandate). The empty-review rule stays: a review fails when it opened none of the `--path` files, or, without `--path`, none of the listed files. The listed files the reviewer did not open go into the end entry (`paths_not_read`) and the record. | owner, [decision 1](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672); default (the hint files carry the empty-review rule; unopened files are shown, not failed) |
| S42-D3 | **Upstream items,** each with where it was found: (a) the governing plan: the bundle of `--record` (`docs/slices/<id>/plan.md`) and its decision IDs, always; (b) the plans of other slice bundles the change touches; (c) from the trace model at the reviewed commit (`scripts/validate_traceability.py`), the `ARCH` and `REQ` items linked to changed files (`Implemented by:` lines, `DD` tags anywhere in a changed file); (d) the `REQ` and `ARCH` headings the diff changes, and the test IDs whose `trace/tests.yaml` entries it changes, with their requirements. | owner, [#39](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/39) ("the task names the upstream items the change traces to: its requirement and architecture IDs … and the plan's decisions"); plan review round 2, B2 and A5; default (the trace model as the source) |
| S42-D4 | **The upstream question,** in every prompt: "Does any problem you find originate upstream (a requirement, the architecture, the plan)? If so, name the document and section." | owner, [reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090) |
| S42-D5 | **Computed evidence,** numbered entries in 4.1's evidence section, each with the command that produced it. (a) **Uncovered changed lines:** for each changed Python file under `scripts/`, the changed lines and branches the tooling tests did not run, measured in-process. A fixed note says that a script the tests run as a subprocess shows as uncovered (#44). Each changed Python file under `services/` gets one line naming the gate that covers it, or "no coverage gate". (b) **Trace gaps** among the change's upstream items, each marked new (against the merge-base), existing, or accepted (`accepted_gaps`). (c) **CI results:** each job of the workflow runs whose head is the reviewed commit, with its status and conclusion (a queued or running job says so), read from the public API without a token, or "no CI run for this commit". | owner, [#39](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/39) ("coverage of new code", "requirements without a test (`qa-trace`)", CI results); plan review round 2, B4, A1, A2 and A9; default (the items and their form) |
| S42-D6 | **The reviewer accounts for every evidence entry.** Each entry appears in the report's `accounted` list (4.1, S41-D8) with status `explained` (a note why it is fine) or `flagged` (the ID of the finding it raised). A report that leaves an entry out fails, like an empty review. | owner, [#39](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/39) ("The reviewer explains or flags every entry"); [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147), item 3 |
| S42-D7 | **Evidence failures are visible.** A command that cannot run is shown as "failed: <command>: <reason>", never as no entries. A test run with failing tests shows the coverage and the names of the failing tests. Each item's status (`ok` or `failed`) goes into the start entry. | default (the review stays useful; nothing pretends) |
| S42-D8 | **Evidence from a clean environment.** The commands run in a scratch checkout of the reviewed commit with only `PATH`, `LANG` and a scratch `HOME`. Paths in their output are made relative to the checkout, and the author's `HOME` path and the interpreter's prefix are replaced by `<home>` and `<python>`, so a traceback through site-packages stays usable. The CI call uses no token. Before the prompt is built, the evidence text is checked: it may not contain the author's `HOME` path or the scratch root after the replacement, and on a match the launcher refuses before any call. | plan review round 2, A8; owner rule: no operational details in the public repository |
| S42-D9 | **The evidence is kept.** Its text goes into the record verbatim (4.3) and its SHA-256 into the start entry, so a rebuild and a later reader see what the reviewer got. | plan review round 2, A3 |
| S42-D10 | **`diff_base` becomes required** in `make_frozen_copy`, `build_prompt` and `invocation_from_entry`, as a keyword argument without a default. The `has_diff` branches go, and every prompt names `change.diff`. | owner, [R5-S1](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196) ("the optional diff_base branch in make_frozen_copy, build_prompt and invocation_from_entry can go") |
| S42-D11 | **The benchmark** passes a case's answer-key paths as the ordering hint, and the diff decides the rest. Upstream items are computed at the case's commit as for any review. Computed evidence is off in the benchmark: planted commits have no CI run, and coverage at an old commit measures another tree. 4.5's report says that the measured setup leaves out 4.2's computed evidence. | default (the measurement stays fair; what it leaves out is stated) |

## Requirements

None added (POC-D9).

## Success criteria

- A review of a change that touches or deletes a file not given with `--path` lists that file.
- The prompt names the governing plan and its decisions, and the other upstream items found.
- The evidence section shows uncovered changed lines, trace gaps and CI results of the reviewed
  commit, each with its command; a failed command is shown as failed; no absolute local path appears.
- A report that leaves an evidence entry unaccounted fails.

## In scope

`scripts/run_independent_review.py` (file list, upstream items, evidence, `paths_not_read`, the
required `diff_base`), `scripts/run_review_benchmark.py` (paths as hints, upstream items, evidence
off), the tooling tests, `AGENTS.md` (Independent review: what the reviewer receives).

## Out of scope

- The section layout and the `accounted` list (4.1, #38).
- The checklist content (4.4, #41).
- Coverage of services: `make unit-trust` and `make unit-diff-cov` gate capability-issuer and tool-b;
  the evidence names that gate or says there is none.
- Measuring scripts that tests run as a subprocess (#44).

## Assets and holders

None touched. Evidence is computed from tracked files at the reviewed commit, with a minimal
environment, and checked for local paths before it enters the prompt (S42-D8). CI results come from
the public API without a token.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Trace links available | `scripts/validate_traceability.py` at `c325e7d` (`make qa-trace`, 2026-11-08) | Reports requirements, architecture items, `DD` tags (file and line of the tag) and `Implemented by:` files: 170 requirements, 34 architecture items, 131 DDs |
| Coverage of the lint gate | `pytest --cov` over its tests at `c325e7d` (2026-11-08) | 0%, because its tests run it as a subprocess (#44) |
| CI results readable without a token | `GET /repos/{owner}/{repo}/actions/runs?head_sha=<sha>` and `…/runs/<id>/jobs` on the public repository (2026-11-08) | Readable |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Computed evidence and upstream items | prompt; verbatim in the record (4.3); SHA-256 and item status in the start entry | launcher | reviewer, owner | per attempt | what the reviewer weighs | advisory: the reviewer accounts for each entry; a failed command is shown as failed |
| Scratch checkout for evidence | temporary directory | launcher | launcher | deleted after the round | where evidence is computed | not authoritative; rebuilt per round |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests.
- Rulebook: `AGENTS.md`, Independent review (the inputs, the upstream question, evidence entries).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| File list from the diff | A changed or deleted file left out of the review (DPL-005) | One `git diff` per round | Author's list: it failed |
| Computed evidence, every entry accounted | A reviewer without coverage or trace evidence, or ignoring it (DPL-010) | A test run, a trace run and two API calls per round, about a minute; one list in the report | Author's summary: it can be wrong; evidence without accounting: it can be ignored |
| Local-path check on the evidence | An operational detail reaching a public record | One string search | The secret scanner: it knows secret shapes, not paths |

## Retirement and compatibility

- The author-chosen `--path` list stops being the scope; `--path` stays as an ordering hint.
- The optional `diff_base` branches and `has_diff` are removed.
- The draft's evidence item "changed files outside the list" is dropped: after S42-D1 it could only
  show the withheld record and log.
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm: S42-D2 (the empty-review rule on hint files;
unopened files shown), S42-D3 (the trace model as the source), S42-D5 (the form of the three items),
S42-D7, S42-D11 (evidence off in the benchmark).
