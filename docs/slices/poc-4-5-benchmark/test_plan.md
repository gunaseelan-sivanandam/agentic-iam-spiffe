# Slice Test Plan — poc-4-5-benchmark

Test plan of slice 4.5 of the agentic-SDLC PoC (issue #42): the tests and live checks that show the
benchmark's results stay comparable, its scoring and confirmation are fair, and its report gives the
owner what the decisions need.

## Goal

Prove S45-D1 to S45-D11 of [`plan.md`](plan.md):
- the runner's identity, configurations, budget, cases, scoring and blinding with tooling tests;
- the canary with a twin that must follow both a file and a setting;
- the screening study in the report.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S45-D1 to S45-D11.
- Expected values come from the plan, stage A's committed results (`existing@c325e7d`), and probes
  before the change.

## Unit test plan

Tooling tests in `tests/tools/` with the fake `claude` CLI.

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| Identity | A result records stage, case, configuration, model, effort and prompt identity. `--report --stage B` reads stage B only. | A stage-B run after a change to the mandate, a template or a list does not count earlier results as done. `--report` refuses to compare two stages without naming both. | S45-D2 | plan |
| Prompt identity | The identity changes when the mandate text, a template, a list file or the task changes | — | S45-D2 | plan |
| Budget | Stage B stops at 60 runs, counting retries and canary runs | A stage-B run configured for more than 60 is refused before any review. Stage A's calls do not count against stage B. | S45-D1 | plan |
| Configurations | `short+list` holds the short prompt and the case's list and no mandate; `open+list` holds 4.1's mandate and the list; `open-B+list` holds 4.4's draft and the list; all three hold the same severity rules and blocking criteria | A configuration name the runner does not know is refused | S45-D3 | plan |
| Lists from the fixed commit | A case on a commit without lists gets the list of its artifact type from the runner's fixed commit, recorded in the identity | — | S45-D3 | plan |
| Match rule | A blocking or high finding at the planted file and range with a term is a detection; an absence finding naming what is missing and where is a detection; a finding that only quotes the planted line goes to triage | A detection is refused when the answer key's match-rule hash differs from the committed one | S45-D4 | plan |
| Leak terms | Every case's copy at its commit is free of its leak terms | A copy holding a plant's own description word, or "Planted defect", is refused | S45-D4 | plan |
| Re-score | `--rescore A` writes a separate output naming the new key's hash | Stage A's results file and report are unchanged | S45-D4 | plan; `existing@c325e7d` |
| Cases | The eleven defect cases, the four no-defect cases and the recheck case prepare, pass the leak search and review the right paths; the DPL-010 copy holds the launcher and its tests and no `tests/review_benchmark/` or DPL-010 text | — | S45-D5 | plan |
| Recheck case | The case's prompt holds its earlier report and the false `fixed:` answer; a recheck that re-raises the finding is scored detected | A recheck that accepts the answer, or fails 4.1's read check, is scored missed and not retried | S45-D5 | plan |
| Blinded export | The confirmation export holds no configuration name or prompt identity, and its order differs from the run order; the report joins verdicts back to configurations | — | S45-D7 | plan |
| Report | The report gives, per configuration, detections with exact intervals, discordant pairs, false alarms, false blockers, empty-review failures, severity agreement on repeated cases, origin against found stage, and time and cost per confirmed finding | A report that omits a configuration's counts fails the test | S45-D8 | plan |
| Canary validity | A twin that followed both the planted file and the hook makes the canary valid | A twin that followed only one makes it invalid, and the report says so | S45-D9 | plan |
| CLI-version gate | — | A stage-B run with a CLI version other than the canary's is refused | S45-D9 | plan |
| Runner paths (R5-A8) | `--dry-run` prepares every case and calls no reviewer; the planted-patch path applies a patch and the copy holds the planted line; the launcher's three report-shape branches and a non-JSON stream line are handled | — | S45-D11 | plan |
| Mandate constants | After the owner's choice, the launcher's initial and recheck constants equal the chosen texts, and a review's start entry records their SHA-256 | — | S45-D8 | plan |
| Stage-A compatibility | `--report --stage A` gives stage A's tables unchanged | — | S45-D2 | `existing@c325e7d` |

## Live checks (not in CI)

- **Canary and failed-Read probe** (S45-D9): the twin follows the file and the hook (valid); the
  confined reviewer follows neither (passes); a failed Read shows as an error result.
- **The screening study** within the budget, with blinded confirmation and the second confirmer's
  agreement, and the report (S45-D6 to S45-D8).

## E2E test plan

None.

## Planned verification commands

- `make tooling-test`
- `make lint`
- `make qa-quality` (includes `docs-check` for the report and the results file)
- `python3 scripts/run_review_benchmark.py --dry-run` (leak search) before the run

## Independent review at the implementation PR

After the open mandate, the reviewer answers in the PR body:
1. *Fairness:* can a configuration look better than it is, through scoring, case choice, confirmation,
   mixing of results or leaks?
2. *Tests:* for each new or changed test, which wrong behaviour would still pass it?
3. *Keys:* does a key, socket or secret now reach a service outside its holders? Can anything the
   runner writes publish one?
4. *Names and headers:* do new files and names say what they do?

A "yes" to question 1, 2 or 3 blocks; findings on question 4 follow the severity rules.
