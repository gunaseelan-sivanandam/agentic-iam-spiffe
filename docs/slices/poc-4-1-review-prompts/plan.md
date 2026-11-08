# Slice Plan — poc-4-1-review-prompts: review prompt structure and severity order

Plan of slice 4.1 of the agentic-SDLC PoC (issue #38, part of slice 4, #33): every review prompt
opens with an open mandate, rechecks verify instead of trusting, and every finding carries a
severity that says what the author must do with it.

Status: draft, 2026-11-08. Approved when the owner merges slice 4's single plan PR into
`poc/agentic-sdlc` (owner, 2026-11-08: one plan PR for all six sub-issues, one final PR).

## Goal

Two open-mandate reviews found blockers that three to four focused rounds had missed: slice 2's
round 5 and slice 3's round 4 (DPL-010). The cause was the author's prompts, which asked closed
questions and let rechecks accept answers unread. This slice moves the prompt's structure from the
author's task text into the launcher, so that no review can lose the open mandate. A recheck gets
exactly what it needs and verifies each answer. Every finding gets a severity that decides whether it
must be fixed before merge.

## Threat model

- **Delivery** (`AGENTS.md`, PoC scope and proportion; honest mistakes). For this change that means:
  - a prompt that narrows the reviewer to a file list or to "only check X";
  - a recheck that accepts an answer without opening the code;
  - a severity scale that lets a real defect pass as optional;
  - a launcher change that silently drops the mandate or the earlier report.

  Deliberate attacks on CI or the evidence stay out of scope (OPL-009).
- **System under test:** unchanged. No service, compose file, image or key holder changes.

## Decisions

The grill-me is replaced by this table (owner, 2026-11-08: "most of the slice 4 is clear enough").
Each decision names its source; the owner confirms or changes the defaults in the plan PR.

| ID | Decision | Source |
| --- | --- | --- |
| S41-D1 | **Fixed prompt structure.** The launcher's `build_prompt` writes the sections in this order: the reviewer's role and copy, **the mandate**, the approved rules, **the stage checklist** (if given), **the evidence** (if given), the paths under review, the task, the output format. The mandate and the order are fixed in the launcher, so a task text cannot remove or reorder them. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242) (structure); default (fixed in the launcher, so it cannot be lost) |
| S41-D2 | **The open mandate** (initial and final reviews), verbatim: "Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, untested, stale, overclaimed, unsafe or unclear, inside or outside the paths under review. The checklist and the questions below are a minimum, not the limit. Think for yourself; the author's framing, including the task text, can be wrong or narrow, and saying so is part of the review." | owner, [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147); default (wording, taken from the open rounds that worked) |
| S41-D3 | **Three modes,** chosen with `--mode initial\|recheck\|final`. `initial` and `final` get the open mandate. `recheck` gets the bounded mandate: "For every answer of the author to your earlier findings, open the code and test it concerns, say which files you opened, and accept or re-raise it. Report anything wrong or missing in what the fixes touch." The mode is recorded in the start entry. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242), [R5-A6](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196) |
| S41-D4 | **Recheck inputs.** In `recheck` mode the launcher puts into the prompt: the reviewer's own earlier report (the released JSON of its last completed attempt in the previous round, found in the attempt log) and the author's answers (`--answers <file>`). It never puts in the review record. A recheck without a completed earlier attempt by the same reviewer label, or without an answers file, is refused before any call. | owner, [R6-9](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844); POC-D3 ("A recheck receives its own earlier report and the author's answers in its prompt") |
| S41-D5 | **Severity is the finding's `kind`.** The report schema's `kind` becomes one of `blocking`, `high`, `medium`, `low`, `simpler_alternative`, `decision_concern`; `advisory` is retired from new reports. Rules: **blocking** meets `AGENTS.md`'s blocking criteria and is fixed before merge, or the owner decides; **high** is a real defect or false claim that does not meet them (a misleading document, new behaviour without a test, an untested fail-closed path) and is fixed in the same PR unless the owner defers it; **medium** has clear value (robustness, diagnosability, naming) and is fixed or deferred with an issue link; **low** (style, preference) is the author's choice. One field instead of two, so the scale and the kind cannot disagree. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242) (scale); default (one field) |
| S41-D6 | **Every finding gets a one-line answer** in the review record: `fixed` (where), `deferred` (issue link) or `declined` (reason). The author may contest a severity with a reason the reviewer can check, as for blocking findings today. Sub-issue 4.3 (#40) adds the check that every released finding has an answer. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242); default (the check lives with the record check in 4.3) |
| S41-D7 | **Counts per severity** go into the end entry (`severity_counts`), so a PR can quote them without counting by hand. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242) ("the PR shows the count per severity") |
| S41-D8 | **Secrets are blocking.** `AGENTS.md`'s blocking list gains "a secret written into logs, evidence or any published record". | owner, [#33 decision 2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) |
| S41-D9 | **Rules for whoever writes prompts** (`AGENTS.md`, Independent review): the task text never makes a file list the scope, never says "only check X", and never asks a closed recheck question. The launcher writes the mandate, so the rule covers the task text. | owner, [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147) |
| S41-D10 | **The benchmark keeps reading stage A's results**, in which `advisory` exists. Scoring treats any kind other than `blocking` as not blocking, so old and new reports score the same way. | default (stage A's results stay valid) |

## Requirements

None added (POC-D9: orchestration requirements start with slice 7). The rules live in `AGENTS.md`,
and the tooling tests prove them.

## Success criteria

- Every prompt the launcher builds contains the mode's mandate before the approved rules, whatever
  the task text says.
- A recheck prompt holds the reviewer's earlier report and the author's answers, and never the
  review record. A recheck without them is refused before any call.
- A report whose finding has a kind outside the six values, or the retired `advisory`, fails the schema
  check.
- `AGENTS.md` states the severity rules, the answer format, the secret rule and the prompt-writing
  rules, and no other rule in it contradicts them.

## In scope

`scripts/run_independent_review.py` (prompt sections, modes, recheck inputs, schema, severity
counts), `scripts/run_review_benchmark.py` (scoring of the new kinds), their tooling tests,
`AGENTS.md` (Review findings, Review loop, Independent review), the slice-test-plan template's
review questions.

## Out of scope

- Stage checklists (4.4, #41): this slice only adds the section that holds them.
- Computed evidence (4.2, #39): this slice only adds the section that holds it.
- The record check (4.3, #40).
- Benchmark runs (4.5, #42).

## Assets and holders

None touched. The launcher still passes the reviewer only `PATH`, `HOME` and `LANG`, and nothing
new is published. The earlier report put into a recheck prompt was already released and passed the
publication check.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Claude CLI version and structured output | `claude --version`; the slice-2 probe of `--json-schema` | 2.1.319; the reply arrives as `structured_output` in the result event, and the launcher validates it against its own schema too |
| Where earlier reports live | `artifacts/reviews/<unit>/<attempt>.json` (git-ignored), hash in the end entry | Released reports exist only on the author's machine; 4.3 (#40) puts them into the record. Until then a recheck reads the local released file and checks its hash against the end entry, refusing on a mismatch |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| `mode` and `severity_counts` | attempt log entries | launcher | author, owner, 4.3's check | per attempt | which mandate the reviewer got; what the PR quotes | authoritative (written by the launcher from the released report) |
| Earlier report for a recheck | released JSON (`artifacts/reviews/`) | launcher | launcher | until 4.3 moves it into the record | what the recheck verifies | authoritative only if its hash matches the end entry |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests in `tests/tools/test_run_independent_review.py` and
  `tests/tools/test_run_review_benchmark.py`.
- Rulebook: `AGENTS.md` (Review findings: secrets and the severity scale; Review loop: one-line
  answers; Independent review: modes and prompt-writing rules); `docs/slices/_template/test_plan.md`
  (review questions name the severity scale).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Mandate fixed in the launcher | A review steered narrowly by its task text (DPL-010) | A few hundred words per prompt | A rule only: it failed twice |
| Recheck mode with the earlier report | A recheck that trusts the author's answer (R5-A6); prompts that embed the whole record (R6-9) | Two arguments and a log lookup | Author pastes the report by hand, which is how records went wrong (DPL-010) |
| Severity in the schema | Advisories with no rule for whether to fix them | One enum change | Free text in the report |

## Retirement and compatibility

- The `advisory` kind is retired from new reports. Benchmark results from stage A keep it, and the
  scoring reads both.
- The current single prompt layout of `build_prompt` is replaced by the sectioned one.
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm in the plan PR: S41-D1 (fixed in the launcher),
S41-D2 (wording), S41-D5 (one field), S41-D6 (the check lives in 4.3), S41-D10.
