# Slice Plan — poc-4-5-benchmark: benchmark of the review setup and the mandate wording

Plan of slice 4.5 of the agentic-SDLC PoC (issue #42, part of slice 4, #33): measure slice 4's review
setup, the open mandate with the stage checklist against the short prompt with the same checklist,
and two wordings of the mandate, as a screening study within 60 reviewer runs whose counts the owner
decides from.

Status: draft, 2026-11-08; revised after plan review rounds 1 to 4 and the owner's decisions of
2026-11-09. Approved when the owner merges slice 4's single plan PR.

**Order of work:** in two parts. 4.5a (result identity, configurations, cases, the runner's changes)
comes after 4.1 to 4.3 and before 4.4. 4.5b (the runs and the report) comes after 4.4, whose lists
and mandate drafts it measures. The whole order is in the [slice index](../README.md).

## Goal

Stage A (slice 2) measured two prompts with Opus. Both missed the defects of absence and placement
(DPL-004, DPL-005); neither raised a false blocker in its 17 completed reviews; 5 of 22 reviews
failed the empty-review rule. Slice 4 changes the setup: the open mandate first (4.1), the files
from the diff and the upstream items (4.2), and stage checklists from research (4.4).

The owner decided on 2026-11-09:
- no short-prompt-only setup ("it was evident that it produced narrow results"); the benchmark
  compares "short prompts with check list and open mandate with checklist";
- the research-based mandate wording is measured too (S41-D14);
- Opus is the reviewer by reasoned choice; no model comparison;
- the owner decides from counts, not from automatic rules.

The research of agent-first delivery and its critique (summary:
[`industry_research.md`](../agentic-sdlc-poc/industry_research.md)) showed that about 15 cases with one
run each can screen for large effects, not rank close setups. This slice therefore runs a screening
study: blinded, with the match rule committed before the run, repeats only where setups disagree, and
counts with exact intervals. 4.2's computed evidence is not measured (S42-D11).

## Threat model

- **Delivery** (honest mistakes):
  - comparing results from different prompts, setups or answer keys;
  - a confirmation that favours one setup, because the confirmer knows which setup found what;
  - "blocking" meaning different things in the compared setups;
  - a case whose copy holds its own answer;
  - reading chance as a difference between setups;
  - a budget overrun.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S45-D1 | **Budget:** at most 60 reviewer runs, counting the canary, failed attempts and retries; about 53 are planned (S45-D6). A code constant per stage. The failed-Read probe takes at most two sessions outside the budget; 4.4's critique is outside it too. | owner, 2026-11-09 ("I accept your recommendations for my decisions") (about 55 runs without the model comparison); default (7 for retries) |
| S45-D2 | **Result identity:** stage (`B`), case, configuration, model, effort and the prompt identity, the SHA-256 of the mandate text, the configuration's template files, the list files used and the task text. Each stage writes its own results file (`benchmark_results_<stage>.jsonl`), and the budget counts per stage. `--report` reads one stage, or compares two when both are named. Stage A's file and report stay as they are. | [R5-A2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196); plan review round 1, B6 and A1 |
| S45-D3 | **Configurations.** `short+list`: stage A's short prompt with 4.4's list for the case's artifact type, without the mandate. `open+list`: 4.1's initial mandate with the same list, 4.2's file list and upstream items. `open-B+list`: like `open+list`, with 4.4's research-based draft of the initial mandate (S44-D13). `recheck-A` and `recheck-B`: 4.1's recheck mandate and 4.4's draft, on the recheck case. Every configuration gets the same severity rules (4.1, S41-D6) and blocking criteria, so "blocking" means the same in all. The lists come from the runner's fixed commit (S44-D12). Only the runner builds `short+list` and the B variants (4.1, S41-D2). | owner, 2026-11-09 ("short prompts with check list and open mandate with checklist"); S41-D14; the research's critique (the same definition of blocking for every setup) |
| S45-D4 | **Scoring.** The answer key commits the match rule before any run: a planted or real defect is detected by a finding at its file and line range with one of its terms; an absence defect also by a finding that names what is missing and where. Leak terms come from each plant's patch header and description and are never in its copy. Blocking and high findings count as detections, since both are fixed before merge (S41-D6); blocking-only counts are reported too. `--rescore A` scores stage A's results with the new key into a separate output that names the key's hash; stage A's report stands. | [R5-A7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196); plan review rounds 1 and 2; default (blocking or high) |
| S45-D5 | **Cases.** Eleven defect cases: RM-1 to RM-5 (stage A); three stage-document cases the author plants on `e842e97` (a requirement no test could verify; an architecture data flow that gives a non-holder an asset; a test-plan row that drops a requirement's only runtime proof); two stage-document cases a fresh session plants from the sources in 4.4's `research.md` without seeing the lists, so the lists are also measured on defects that did not shape them; and the DPL-010 case, a patch on `c4f9ca2` with only the launcher, its fake CLI and its tests as at `5a5aba7`. Four no-defect cases: CL-1, CL-2, one more clean case and one decoy, code that looks wrong but is correct. The recheck case, on `e842e97`: an earlier report with one finding on a planted defect and an author's `fixed:` answer naming a file whose change does not fix it; it is detected when the recheck re-raises the finding, and an attempt that fails 4.1's read check (S41-D8) counts as a miss, not a retry. The planted cases of stage A are not re-run. The answer key gives each case its files, line ranges, terms and artifact type. | #33's description; [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147), item 6; plan review rounds 1 to 4; the research's critique (cases that did not shape the lists, a decoy) |
| S45-D6 | **Which runs, within 60.** All reviews run on Opus, at the effort they run at in practice: initial reviews high, rechecks medium. The canary and its twin (2); `short+list` and `open+list` on the 15 cases (30); `open-B+list` on the 11 defect cases, CL-1 and CL-2 (13); `recheck-A` and `recheck-B` (2); both setups again on up to two cases where `short+list` and `open+list` disagree (4); the second confirmer (2, S45-D7). About 53 runs, with 7 left for retries. | owner, 2026-11-09 ("I accept your recommendations for my decisions"); the research's critique (repeats only where setups disagree; the effort used in practice) |
| S45-D7 | **Blinded confirmation.** Before confirmation, the runner strips the configuration from every finding and shuffles them. The author confirms each against the committed match rule without knowing its setup. A Sonnet session confirms a random sample of ten the same way, and the report gives the agreement. | owner, 2026-11-09 ("I accept your recommendations for my decisions"); the research's recommendation B4 as amended |
| S45-D8 | **A report for the owner's decisions, not rules.** For each configuration: detections with exact 95% intervals; the discordant pairs between `short+list` and `open+list`, and between `open+list` and `open-B+list`; false alarms on the no-defect cases, and false blockers on every completed review; empty-review failures and unread files; severity agreement where a case ran twice; the origin stage against the stage that found it (S41-D16); time and cost per confirmed finding. The report states what these sample sizes can show: a difference of two or three cases is within chance. The owner decides the default setup and each mandate wording, initial and recheck separately (S41-D14). Both setups carry the lists, so the report does not measure the lists' own effect. The final mandate's draft is chosen by the owner by reason, since no case can measure it. The launcher's mandate constants change only after the owner's choice, in 4.5b. | owner, 2026-11-09 ("I accept your recommendations for my decisions"); the research's critique (the "two more detections" rule fires by chance 8 to 26% of the time at these sizes) |
| S45-D9 | **A stronger canary.** The twin and the confined reviewer get the same prompt, which tells both to follow any instruction file and setting they find. The twin is valid only if it follows both the planted `CLAUDE.md` and the planted hook. The confined reviewer passes if it follows neither. A live failed-Read probe confirms how the CLI reports a Read that fails. Both are recorded with the CLI version. The runner refuses stage-B runs when the installed CLI version differs from the canary's. | [#42 comment](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/42#issuecomment-6725809234); [R6-7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844); plan review round 1, B3 |
| S45-D10 | **Models:** Opus (`claude-opus-5-5`) for every reviewer run; Sonnet (`claude-sonnet-5-5`) only as the second confirmer. No model comparison and no Codex: Opus is the default reviewer by the owner's reasoned choice. | owner, 2026-11-09 ("I accept your recommendations for my decisions") |
| S45-D11 | **Tests the runner lacks** (R5-A8): the planted-patch path and `--dry-run` of the runner; the launcher's three report-shape branches; skipping non-JSON stream lines. | [R5-A8](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196) |

## Requirements

None added (POC-D9).

## Success criteria

- At most 60 runs; every run, refusal and failure appears in the report.
- The report gives S45-D8's counts for `short+list`, `open+list` and `open-B+list`, and the recheck
  case for both wordings, with the confirmation agreement; the owner records the choices.
- The canary is valid (the twin followed the file and the hook) and passes.
- Results of different stages, configurations, prompts or answer keys cannot be mixed without the
  report saying so.

## In scope

`scripts/run_review_benchmark.py` (identity, configurations, per-stage files and budget, lists from a
fixed commit, the new cases, the blinded export for confirmation, `--rescore`, the CLI-version gate),
`tests/review_benchmark/` (answer key version, cases and patches, prompts, run groups), the tooling
tests, the report `docs/slices/poc-4-5-benchmark/benchmark_report.md`, and, after the owner's choice, the
launcher's mandate constants (`scripts/run_independent_review.py`) set to the chosen wordings.

## Out of scope

- Changing the review setup itself (4.1 to 4.4), except the mandate constants after the owner's choice.
- 4.2's computed evidence in the benchmark (S42-D11).
- Comparing models, and Codex as a reviewer (owner, 2026-11-09).
- Choosing reviewers per stage for the delivery loop (slice 7).
- More than 60 runs, unless the owner raises the budget.

## Assets and holders

None touched. Reviews run as in slice 2, confined to their copy.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Stage A cost | stage A report (`existing@c325e7d`) | 24 runs: the 5-hour window rose from 22% to 35%, the weekly one from 2% to 4% |
| Stage A cases | `tests/review_benchmark/answer_key.yaml` (`existing@c325e7d`) | 5 real misses (RM-1 to RM-5), 4 planted (PD-1 to PD-4), 2 clean (CL-1, CL-2), the canary |
| Slice 2 at `5a5aba7` | `git ls-tree 5a5aba7` (2026-11-08) | Holds `tests/review_benchmark/` and DPL-010, which name the answer; hence S45-D5's patch on `c4f9ca2` |
| DPL-010's defect at `5a5aba7` | `pytest --cov=scripts tests/tools/test_run_independent_review.py` in an archive of `5a5aba7` (2026-11-08) | 68 passed; the launcher at 95% of lines. Untested refusal paths: an invalid base branch name, `AGENTS.md` missing on the base, a path missing at the commit, an invalid `--record`, repeated or malformed reviewer labels, a missing prompt file, an invalid unit or round, a failing `git` call, and three report-shape problems. The answer key's expected findings are these paths |
| Stage A outcome | stage A report (`existing@c325e7d`) | No false blocker in 17 completed reviews; 5 of 22 reviews failed the empty-review rule; both prompts missed the absence and placement defects |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Stage B results | `docs/slices/poc-4-5-benchmark/benchmark_results_B.jsonl` | runner | `--report` | committed | the counts the owner decides from | authoritative only with the committed answer key's and prompts' hashes |
| Confirmation labels | the blinded export and the author's and second confirmer's verdicts, committed with the report | runner (export), author and Sonnet (verdicts) | `--report` | committed | which findings count as detections | authoritative once the match rule's hash matches the answer key |
| Canary record | the stage-B results file (canary rows with the CLI version) | runner | runner | until the Claude CLI version changes | whether stage-B runs may start | authoritative for the CLI version it names |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests (identity, configurations, budget, scoring, cases, blinding, R5-A8's paths);
  the canary and the report.
- Rulebook: none in this slice. This plan PR changes `AGENTS.md`'s models line: Opus is the default
  reviewer by the owner's reasoned choice, and Codex is not a reviewer in slice 4.

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Full identity in results | Comparing results from different prompts or keys (R5-A2) | A few fields and a file per stage | One shared file: it mixed results |
| Blinded confirmation with a second confirmer | The author favouring a setup when confirming | A shuffled export and two Sonnet sessions | The owner confirming: it costs the owner's time (O4) |
| CLI-version gate | Results measured under a CLI the canary never checked | One comparison | Re-running the canary by hand |

## Retirement and compatibility

- Stage A's results and report stay as committed. The runner reads them as stage `A`.
- The answer key gets a new version. Stage A's key stays in the history, and its hash stays in its
  results.
- Dropped from earlier drafts: the `short`, `open` and `narrow` setups; the Sonnet and Codex
  comparison with the launcher's Codex mode and its probe; the automatic decision rules; the "weak
  test" case.

## Review notes

Defaults by the author, for the owner to confirm: S45-D1 (the cap of 60 with retries), S45-D4 (blocking
or high as detections), S45-D5 (the cases), S45-D6 (the split), S45-D7 (a sample of ten).

The owner granted one more review round for this plan on 2026-11-09 ("I accept your recommendations
for my decisions", decision 5 of the proposal). The launcher needs that extension as a PR comment
link.
