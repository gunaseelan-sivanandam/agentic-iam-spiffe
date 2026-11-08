# Slice Plan — poc-4-2-review-inputs: review inputs and evidence computed by tools

Plan of slice 4.2 of the agentic-SDLC PoC (issue #39, part of slice 4, #33): the launcher, not the
author, decides which files a reviewer must examine, names the upstream items a change traces to,
and computes the evidence the reviewer gets.

Status: draft, 2026-11-08. Approved when the owner merges slice 4's single plan PR.

## Goal

DPL-005 slipped through because the author's file list left out the workflow file. DPL-010 slipped
through because the reviewer had no coverage evidence and nothing asked where a problem started.
This slice makes the review's inputs deterministic:
- the files under review come from the diff;
- the upstream requirements, architecture items and plan decisions are named in the prompt;
- the evidence is computed by tools and placed in slice 4.1's evidence section: coverage of changed
  code, requirements without a test, changed files outside the list, and CI results when known.

## Threat model

- **Delivery** (honest mistakes):
  - a changed file left out of the review;
  - a reviewer judging without coverage or traceability evidence;
  - evidence the author summarised wrongly;
  - a problem fixed where it surfaced while its cause sits upstream.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S42-D1 | **Files under review come from the diff.** The launcher computes the list from `git diff --name-only <merge-base> <commit>`, without the withheld files and files deleted by the change. `--path` becomes optional; a given `--path` must be in the diff and only orders the list (the files named first), it never narrows it. | owner, [reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090) |
| S42-D2 | **Open every file under review** (owner: "keep the rule"). The prompt's paths section says so. The empty-review rule stays: a review that opened none of the files fails. | owner, [decision 1](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) |
| S42-D3 | **Upstream items.** The launcher runs the trace model (`scripts/validate_traceability.py`, as `make qa-trace` does) at the reviewed commit, and lists the `REQ` and `ARCH` items linked to changed files (`Implemented by:` lines, `DD` tags in changed functions). It also lists the slice bundles the change touches, so the prompt can name their `plan.md`. A change that touches none of them gets "no upstream item found", stated plainly. | owner, [reviewer inputs](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722850090); default (the trace model is the existing source of these links) |
| S42-D4 | **The upstream question,** in every prompt: "Does any problem you find originate upstream (a requirement, the architecture, the plan)? If so, name the document and section." | owner, same |
| S42-D5 | **Computed evidence** goes into slice 4.1's evidence section, each item with the command that produced it: (a) line and branch coverage of changed Python files under `scripts/`, from the tooling tests run in-process; (b) the trace model's gaps that the change adds against the base; (c) the changed files the review list leaves out (empty after S42-D1, unless a file is withheld); (d) when the author passes `--ci-run <run id>`, the CI job conclusions of that run, read from the public API. The evidence is computed at the reviewed commit in a separate scratch checkout, never from the author's working tree. | owner, [evidence](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147) ("evidence, not conclusions"); default (which items, and the scratch checkout) |
| S42-D6 | **Evidence failures fail closed, visibly.** If a command fails, the evidence section says which one and why, and the review still runs. A missing coverage report must not read as "100%". | default (the review stays useful; nothing pretends) |
| S42-D7 | **`diff_base` becomes required** in `make_frozen_copy`, because both callers always pass it ([R5-S1](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196)). | review round 5 of slice 2 |
| S42-D8 | **The benchmark keeps its own paths.** Benchmark cases name their paths in the answer key, because a case reviews a past commit against a fixed base. The runner passes them as the ordering hint (S42-D1), and the diff decides the rest. | default (cases stay comparable with stage A) |

## Requirements

None added (POC-D9).

## Success criteria

- A review of a change that touches a file not given with `--path` lists that file under review.
- The prompt names the upstream items, or says plainly that none was found.
- The prompt's evidence section shows coverage of changed scripts, new trace gaps and CI results
  (when a run is named), each with its command. A failed command is shown as failed.

## In scope

`scripts/run_independent_review.py` (file list, upstream items, evidence, the required `diff_base`),
`scripts/run_review_benchmark.py` (paths as hints), the tooling tests, `AGENTS.md` (Independent
review: what the reviewer receives).

## Out of scope

- The section layout (4.1, #38).
- The checklist content (4.4, #41).
- Evidence for services: their unit-test coverage is already gated by `make unit-trust`.

## Assets and holders

None touched. Evidence is computed from tracked files at the reviewed commit. CI results come from
the public API without a token. Nothing from the author's environment enters the prompt.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Trace links available | `scripts/validate_traceability.py` (`make qa-trace`) | Reports requirements, architecture items, `DD` tags and `Implemented by:` files; slice 3's run: 170 requirements, 34 architecture items, 131 DDs |
| Coverage of the lint gate | `pytest --cov` over its tests | 0%, because its tests run it as a subprocess (#44). Coverage evidence for such scripts reads "not measurable" until #44 is closed |
| CI results readable without a token | `GET /repos/.../actions/runs/<id>/jobs` (public repository) | Readable |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Computed evidence and upstream list | prompt, plus the evidence's SHA-256 in the start entry | launcher | reviewer | per attempt | what the reviewer weighs | advisory: the reviewer judges it; a failed command is shown as failed |
| Scratch checkout for evidence | temporary directory | launcher | launcher | deleted after the round | where evidence is computed | not authoritative; rebuilt per round |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests.
- Rulebook: `AGENTS.md`, Independent review (the inputs, the upstream question).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| File list from the diff | A changed file left out of the review (DPL-005) | One `git diff` per round | Author's list: it failed |
| Computed evidence | A reviewer without coverage or trace evidence (DPL-010) | A test run and a trace run per round, about a minute | Author's summary: it can be wrong |

## Retirement and compatibility

- The author-chosen `--path` list stops being the scope; `--path` stays as an ordering hint.
- The optional `diff_base` branch is removed.
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm: S42-D3 (trace model as the source), S42-D5 (the
four evidence items, the scratch checkout), S42-D6, S42-D8.
