# Slice Test Plan — poc-4-1-review-prompts

Test plan of slice 4.1 of the agentic-SDLC PoC (issue #38): the tests that show every prompt keeps
its mandate, rechecks get the right inputs, and the severity scale is enforced.

## Goal

Prove S41-D1 to S41-D16 of [`plan.md`](plan.md) with tooling tests. A prompt must never lose the
mandate, a recheck must get its inputs and show it opened what the answers name, and the severity
scale must be enforced by the schema.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S41-D1 to S41-D16.
- Expected values come from the plan (`plan`) or from the existing tests
  (`existing@c325e7d`), never from watching the new code run.

## Unit test plan

No unit tests under `tests/unit/`: no service code changes. All tests are tooling tests in
`tests/tools/`, run by `make tooling-test`, with the fake `claude` CLI from slice 2.

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| Section order | The prompt holds role, mandate, rules, checklist, upstream, evidence, paths, task, (recheck: earlier report, answers) and output, in that order; a section with nothing to show says so | A task text that says "ignore the mandate" or "only check file X" still leaves the mandate before the rules and the task | S41-D1, S41-D11 | plan |
| No way to drop the mandate | The launcher's argument parser has no option that changes the sections; every prompt it builds, in every mode, holds its mode's mandate | An unknown option such as `--no-mandate` is refused before any call | S41-D1 | plan |
| Reporting bounds | The output section holds the absence format, the gate rule ("do not report what a passing gate already checks; do report defects in the gates themselves") and the "claims to verify" section name verbatim; the task text appears only in that section | — | S41-D15 | plan |
| Cannot determine | A recheck that lists an answer as `cannot determine` completes, and the end entry counts it | A `cannot determine` without a note fails the schema | S41-D15 | plan |
| Origin stage | Findings with each `origin_stage` value are accepted | A finding without `origin_stage`, or with another value, fails the schema | S41-D16 | plan |
| Token note | The output section holds the `<token>` instruction verbatim | — | S41-D1 | plan |
| Runner configurations | The runner's baseline configurations (stage A short, stage A checklist, narrow question) build prompts without the mandate, and their configuration name and hash differ from the full one | — | S41-D2 | plan |
| Mandate identity | The start entry holds the SHA-256 of the mandate used; changing a mandate constant changes it | — | S41-D14 | plan |
| Mode from the round | Round 1 is `initial`, round 2 `recheck`, round 1 of unit `final` is `final`, round 2 of unit `final` is `recheck`; the start entry records it | — | S41-D3 | plan |
| Mandates verbatim | Each mode's prompt holds its mandate text verbatim; the final prompt has no checklist section and names the other units' records present in the copy | A final prompt given a stage list still has no checklist section | S41-D4 | plan |
| Recheck inputs | A recheck prompt holds the reviewer's earlier released report, the record's answers section for that attempt (and no other part of the record) and the evidence section; the start entry holds the section's SHA-256 | Refused before any call when: the same unit and label have no completed attempt in the previous round; a completed attempt of the same label exists only in another unit, or only before a reset (it is not used); the released file is missing; its hash differs from the end entry; the answers section is missing or empty. A marker sentence elsewhere in the review record never appears in the prompt. With two reviewers, each prompt holds only the answers to its own report. | S41-D5 | plan |
| Schema severity | Findings with each severity and each new kind are accepted | A finding without `severity`, with kind `blocking` or `advisory`, or a `simpler_alternative` that is not `low`, makes the attempt "failed" and the report is not released | S41-D6 | plan |
| Answers section | A table with one row per finding, each answer starting with `fixed:`, `deferred: #N`, `rejected:` or `owner:`, is accepted; a `fixed:` path the change deletes or renames is accepted | Refused before any call: a row with another first word; a `fixed:` answer naming no path; a `fixed:` path that neither exists in the copy nor is deleted or renamed by the change | S41-D7, S41-D8 | plan |
| Accounted | A recheck that lists every answer in `accounted`, with `opened` paths it read, completes | The attempt fails when: an answer is missing from `accounted`; an `opened` path is not among the read paths; a file named in a `fixed:` answer was not read | S41-D8 | plan |
| Severity counts | The end entry's `severity_counts` equals the count of each severity in the released report, with zero for those that do not occur | — | S41-D9 | plan |
| Rebuild | `invocation_from_entry` rebuilds a recheck's full prompt from its entry, the earlier report, the answers section and the evidence text, and its `full_prompt_sha256` matches | A changed answers section, or changed evidence, gives a mismatch | S41-D5 | plan |
| Benchmark scoring | A new report with a `blocking` severity scores as detected; stage A's results are read as before; the report column reads "Not blocking"; the canary asks for a low finding | — | S41-D13 | plan; `existing@c325e7d` (stage A results) |

## E2E test plan

None. No harness test, service, compose file or image changes.

## Assumptions and fixtures

- The fake `claude` CLI prints scripted streams; no test spends tokens.
- Recheck tests write a log with a completed earlier attempt and its released report, as slice 2's
  tests do.

## Planned verification commands

- `make tooling-test`
- `make lint`
- `make qa-quality`
- `scripts/clean_stack.sh`, then `make e2e` and `make qa-evidence`, once at slice 4's close

## Review notes

The rule texts in `AGENTS.md` (S41-D6, D7, D10, D11, D12) are proved by review, not by a test. The
review quotes the text that states each one, checks that each sentence S41-D12 names is changed, and
checks every other hit of "advisory" and "blocking" in `AGENTS.md` against S41-D6.

## Independent review at the implementation PR

A reviewer that is not the author ([AGENTS.md — Independent review](../../../AGENTS.md#independent-review))
answers in the PR body, after the open mandate:
1. *Tests:* for each new or changed test, which wrong behaviour would still pass it? Does its assertion
   match the row above?
2. *Keys:* does a key, socket or secret now reach a service outside its holders? Can any secret or
   operational detail reach the reviewer or a public record through the new sections, the recheck
   inputs, the answers section or the severity counts?
3. *Names and headers:* do new files and names say what they do (coding rule 8)?

A "yes" to question 1 or 2 blocks; findings on question 3 follow the severity rules.
