# Slice Plan — poc-4-3-review-records: review records written by the launcher and checked

Plan of slice 4.3 of the agentic-SDLC PoC (issue #40, part of slice 4, #33): the launcher writes the
verbatim blocks of every review record, scans each prompt before it is sent or written, and `make
docs-check` checks that every new record matches its attempt log and that every finding is answered.

Status: draft, 2026-11-08, revised after plan review round 2. Approved when the owner merges slice
4's single plan PR.

**Order of work:** after 4.1 (severities, answers, recheck inputs) and 4.2 (evidence), whose parts
this slice writes into the record. The whole order is in the [slice index](../README.md).

## Goal

A review record must keep every prompt part and every report verbatim, so anyone can check what a
reviewer was asked and what it answered. In slices 2 and 3 the author built these blocks by hand and
got them wrong. Prompts held placeholders, reports were reformatted, and the attempt log's
fingerprints matched nothing (DPL-010). Since then the author checks records by hand before every
push. This slice removes the hand work at its origin and adds a deterministic check. The owner's
words: "can we make this deterministic instead of relaying on you everytime?"; decided "do it with
slice 4" ([#33](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725327080)).

## Threat model

- **Delivery** (honest mistakes):
  - a record that paraphrases or shortens what the reviewer saw or said;
  - answers edited after the recheck that read them;
  - a finding left without an answer, or answered in a way its severity does not allow;
  - a secret or a local path in a prompt that reaches the reviewer or a public record;
  - a check that passes an empty, misplaced or malformed block.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S43-D1 | **The launcher writes the blocks.** Under `### Attempt <attempt id>` it writes `#### Prompt` (the task prompt verbatim), `#### Evidence` (4.2's evidence verbatim) and `#### Report` (the released report verbatim). Each is a fenced block whose fence is one backtick longer than the longest backtick run inside it. Prompt and evidence are written before the call, the report after release. A failed, withheld or interrupted attempt keeps its prompt and evidence and gets a status line. The start entry is appended first and the blocks after it, both under the attempt log's lock, so a killed launcher leaves no heading without a logged attempt and parallel reviewers cannot interleave. The author writes only `#### Answers to <attempt id>`, the table of 4.1's S41-D7. The start entry carries `evidence_sha256`, and a recheck's start entry the SHA-256 of the answers section it read (4.1). | owner, [#33](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725327080) ("the launcher writes the blocks"); plan review round 2, B3, B4 and A9; default (labels and fences) |
| S43-D2 | **Scan before the call.** The launcher builds the full prompt (task, answers, evidence, earlier report) and runs the evidence secret check on it before the start entry and before any call. It also refuses text that holds the author's `HOME` path or the scratch root. On a finding it refuses with exit 2, logs and writes nothing, and names the kind and location, never the value. | owner, same ("the prompt is scanned"); plan review round 2, B4 and A6 |
| S43-D3 | **The record check** (`scripts/check_review_records.py`, run by `make docs-check`) covers every attempt whose start entry has `record_blocks: 1`, the field this slice's launcher writes. For each one: its `### Attempt` heading is in the record (the record path is the withheld non-log path of its start entry); its Prompt block's SHA-256 equals its `prompt_sha256`, its Evidence block's its `evidence_sha256`, and, when its end entry has a `report_sha256`, its Report block's equals that; a recheck's logged answers hash equals the hash of the answers section it names. A block under an attempt heading with no logged attempt fails. A block is the fenced block right after a `#### Prompt`, `#### Evidence` or `#### Report` label under an attempt heading; any other fence, for example in answers, is not a block. | owner, same; slice 2 review round 6, R6-2; plan review round 2, A3 and A4 (binding per attempt, block labels) |
| S43-D4 | **Every finding has an allowed answer.** For each released report of a checked attempt, every finding ID has a row in `#### Answers to <attempt id>`, and the answer is allowed for its severity (4.1's S41-D7). A `rejected` blocking or high finding needs the next round's report to list it as `accepted` under `accounted`, or an `owner:` link. A `decision_concern` must be answered `owner:`, whatever its severity. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242) (every finding gets an answer; the rules per severity); default (the check runs in `docs-check`) |
| S43-D5 | **Earlier records stay as they are.** Attempts logged before this slice (slices 2 and 3, slice 4's plan reviews) carry no `record_blocks` field and are not checked. Their records are frozen. They were checked by hand: slices 2 and 3 matched 13 of 13 and 8 of 8 blocks, and slice 4's plan-review records are checked before the plan PR is pushed. Nothing is converted. | default (frozen records stay frozen; plan review round 2, B1, B2, S1 and DC1) |
| S43-D6 | **A recheck reads the earlier report from the record.** The launcher takes the Report block of the earlier attempt and checks its hash, instead of the git-ignored released file (4.1, S41-D5). A recheck then works from a fresh clone. | default (the record is the committed home of the report) |
| S43-D7 | **Whole-document secret scanning stays with #21.** | owner, [#21](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21#issuecomment-6725809047) |
| S43-D8 | **The hand check ends in the repository.** `AGENTS.md`'s Independent review says that the record check replaces the author's hand check, and DPL-010's status names this slice's preventive action. | plan review round 2, A8 |

## Requirements

None added (POC-D9).

## Success criteria

- A review run through the launcher leaves a record that the check passes, with no hand editing
  other than the answers.
- The check fails on:
  - a changed prompt, evidence or report block;
  - a block under the wrong attempt heading;
  - a block with no logged attempt, or a logged hash with no block;
  - answers changed after the recheck that read them;
  - a finding without an answer, or with an answer its severity does not allow.
- A prompt with a secret of the evidence shapes, or a local path, is never sent or written.

## In scope

`scripts/run_independent_review.py` (writing blocks, scanning the full prompt, the earlier report
from the record), `scripts/check_review_records.py` (new), `scripts/check_docs.py` (calls it), the
tooling tests, `AGENTS.md` (the `docs-check` row; Independent review: who writes which part of a
record, the end of the hand check), `docs/delivery_problem_log.md` (DPL-010's status).

## Out of scope

- Whole-document secret scanning (#21).
- The content of answers, beyond their first word.
- Attempts logged before this slice.

## Assets and holders

No asset changes. The prompt scan reduces what can reach the reviewer or a public record. Released
reports already pass the publication check.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Hand check of slices 2 and 3 | The author's script (2026-11-08) | Slice 2: 13 of 13 blocks match its log; slice 3: 8 of 8 |
| Slice 4's plan-review logs | `docs/slices/poc-4-*/review_attempts.jsonl` (2026-11-08) | Logged by the launcher before this slice. Five round-1 reports were lost to the report-path collision fixed in `f070669`, so their records cannot hold those blocks |
| Start entry order | `run_attempts` at `d56c69a` | The start entry is appended before the reviewer call, so a scan must come before it |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Review record blocks | `docs/slices/<id>/<record>.md` | launcher (blocks), author (answers) | owner, reviewers of later units, rechecks, the check | per slice, committed | what was asked and answered | authoritative when the check passes |
| `record_blocks` | start entry | launcher | the check | per attempt | which attempts are checked | authoritative (written only by this slice's launcher) |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests in `tests/tools/test_check_review_records.py` (new) and
  `tests/tools/test_run_independent_review.py`.
- Rulebook: `AGENTS.md` (the `docs-check` row; Independent review).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Record blocks match the attempt log, per attempt | A record that does not hold exactly what the reviewer was asked and answered (slices 2 and 3) | One script in `docs-check`, seconds per run | The author's script by hand: it depends on memory |
| Every finding answered as its severity allows | A finding silently dropped, or a blocking or high one waved through | Same script; `docs-check` is red between a released report and its answers | Reading the record by eye |
| Full prompt scanned before the call | A secret or local path reaching the reviewer or a public record | One call to the existing scanner and a string search | #21's document scanner, which is not built yet |

## Retirement and compatibility

- The author's hand-run check is retired for attempts this slice's launcher logs (S43-D8).
- The draft's one-time conversion of slices 2 and 3 is dropped (S43-D5).
- The draft's rendered report views are dropped: the verbatim JSON is indented and readable.
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm: S43-D1 (labels and fences), S43-D4 (the check runs
in `docs-check`), S43-D5 (earlier records not checked, no conversion), S43-D6.
