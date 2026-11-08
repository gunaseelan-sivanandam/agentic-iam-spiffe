# Slice Plan — poc-4-3-review-records: review records written and checked by tools

Plan of slice 4.3 of the agentic-SDLC PoC (issue #40, part of slice 4, #33): the launcher writes the
verbatim blocks of each review record, and `docs-check` fails when a record and its attempt log
disagree or a finding has no answer.

Status: draft, 2026-11-08. Approved when the owner merges slice 4's single plan PR.

## Goal

A review record must keep every task prompt and every report verbatim, so anyone can check what a
reviewer was asked and what it answered. In slices 2 and 3 the author built these blocks by hand and
got them wrong. Prompts held placeholders, reports were reformatted, and the attempt log's
fingerprints matched nothing (DPL-010). Since then the author checks records by hand before every
push. This slice removes the hand work at its origin and adds a deterministic check. The owner's
words: "can we make this deterministic instead of relaying on you everytime?"; decided "do it with
slice 4" ([#33](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725327080)).

## Threat model

- **Delivery** (honest mistakes):
  - a record that paraphrases or shortens what the reviewer saw or said;
  - a finding left without an answer;
  - a secret in a prompt that reaches a public record;
  - a check that passes an empty or malformed record.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S43-D1 | **The launcher writes the blocks.** After it releases a report, it appends to the review record, under a heading `### Attempt <attempt id>`: the task prompt verbatim, the full prompt's SHA-256, and the released report verbatim, each in a fenced block whose fence is one backtick longer than the longest backtick run inside it. A failed attempt gets its prompt and its status. The author writes only the answers, under `#### Answers to <attempt id>`. | owner, [#33](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725327080); default (heading and fence scheme) |
| S43-D2 | **Scan before publishing.** The launcher runs the evidence secret check on the task prompt before writing it into the record, as it already does for reports and log lines. On a finding it writes nothing into the record and names the kind and location, never the value. | owner, same |
| S43-D3 | **The record check** (`scripts/check_review_records.py`, run by `make docs-check`). For every `docs/slices/<id>/review_attempts.jsonl`: every attempt has its blocks in its record (the record path is the withheld non-log path of its start entry); every block's SHA-256 matches a `prompt_sha256` or `report_sha256` of that log; and no logged hash lacks a block. Blocks are found outermost first: the longest fences first. | owner, same; slice 2 review round 6, R6-2 |
| S43-D4 | **Every finding has an answer.** For every released report of a unit, every finding ID appears in that attempt's answers with a disposition: `fixed`, `deferred` (with a `#N` or issue URL) or `declined` (with a reason). Findings of kind `high` need `fixed`, or `deferred` with the words "owner deferred". | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242); sub-issue 4.1, S41-D6 |
| S43-D5 | **Records of earlier slices** (slices 2 and 3, written by hand) are converted once to the new layout, so the check covers them too. Slice 1's record and the plan reviews have no attempt log and are not checked. | default (one rule for every logged unit) |
| S43-D6 | **Whole-document secret scanning stays with #21.** The current shape scanner flags an `AGENTS.md` row that every prompt quotes ([#21](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21#issuecomment-6725809047)). | owner, same |
| S43-D7 | **Records stay readable.** The launcher may add a rendered view of a report next to the verbatim JSON. The check ignores rendered views. | default (slice 2's record format) |

## Requirements

None added (POC-D9).

## Success criteria

- A review run through the launcher leaves a record that the check passes, with no hand editing
  other than the answers.
- The check fails on:
  - a changed prompt or report;
  - a block with no logged hash;
  - a logged hash with no block;
  - a finding without an answer;
  - a `high` finding deferred without the owner.
- A prompt with a secret of the evidence shapes is never written into a record.

## In scope

`scripts/run_independent_review.py` (writing blocks, scanning the prompt),
`scripts/check_review_records.py` (new), `scripts/check_docs.py` (calls it), the `Makefile` target it
needs (if any), the tooling tests, `AGENTS.md` (the `docs-check` row and Independent review), the
conversion of `review_slice_2.md` and `review_slice_3.md`.

## Out of scope

- Whole-document secret scanning (#21).
- The content of answers.
- Records without an attempt log.

## Assets and holders

No asset changes. The prompt scan reduces what can reach a public record. Released reports already
pass the publication check.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Hand check of slices 2 and 3 | The author's script (2026-11-08) | Slice 2: 13 of 13 blocks match its log; slice 3: 8 of 8 |
| Nested fences | `review_slice_2.md`, `review_slice_3.md` | Recheck prompts embedded earlier records, so fences of 5 to 8 backticks are nested. With 4.1's recheck mode, prompts no longer embed records, so nesting stops for new rounds |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Review record blocks | `docs/slices/<id>/review_<unit>.md` | launcher (blocks), author (answers) | owner, reviewers of later units, the check | per slice, committed | what was asked and answered | authoritative when the check passes |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests in `tests/tools/test_check_review_records.py` (new) and
  `tests/tools/test_run_independent_review.py`.
- Rulebook: `AGENTS.md` (the `docs-check` row; Independent review: who writes which part of a
  record).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Record blocks match the attempt log | A record that does not hold exactly what the reviewer was asked and answered (slices 2 and 3) | One script in `docs-check`, seconds per run | The author's script by hand: it depends on memory |
| Every finding answered | A finding silently dropped, or a `high` one deferred without the owner | Same script | Reading the record by eye |
| Prompt scanned before publishing | A secret in a prompt reaching a public record | One call to the existing scanner | #21's document scanner, which is not built yet |

## Retirement and compatibility

- The hand-built record sections of slices 2 and 3 are converted (S43-D5). Their content stays
  verbatim; only the layout changes.
- The author's hand-run check is retired once this merges (a memory note says so).

## Review notes

Defaults by the author, for the owner to confirm: S43-D1 (layout), S43-D5 (converting slices 2 and 3),
S43-D7.
