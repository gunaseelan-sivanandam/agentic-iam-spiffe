# Slice Plan — poc-4-5-benchmark: benchmark of the new review setup, configurations and models

Plan of slice 4.5 of the agentic-SDLC PoC (issue #42, part of slice 4, #33): measure slice 4's new
review setup and three reviewer models on the benchmark's cases, within 40 reviewer runs, before the
setup becomes everyone's default.

Status: draft, 2026-11-08. Approved when the owner merges slice 4's single plan PR.

## Goal

Stage A (slice 2) measured two prompts with Opus. Slice 4 changes the setup:
- the open mandate first (4.1);
- inputs and evidence computed by tools (4.2);
- stage checklists from research (4.4).

The owner decided to benchmark it ("Yes, let's bench mark it") and to compare Sonnet and Codex as
reviewers. This slice:
- adds the cases slice 4 needs;
- fixes the runner's identity and scoring weaknesses found in slice 2's review;
- adds a Codex mode to the launcher, if Codex can be confined;
- runs the measurement and reports it.

## Threat model

- **Delivery** (honest mistakes):
  - a comparison of results from different prompts or answer keys;
  - scoring that counts a quote of the planted line as a detection;
  - a Codex reviewer that reads outside its copy or loads the copy's `AGENTS.md`;
  - a budget overrun.
- **System under test:** unchanged.
- **Credentials:** the Codex CLI keeps its login under `HOME`. A Codex reviewer must not be able to
  read it, or anything else outside its copy (S45-D5).

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S45-D1 | **Budget:** at most 40 reviewer runs, counting failed attempts, retries and both canary runs, across all models. | owner, 2026-11-08 ("Up to 40 runs") |
| S45-D2 | **Clean re-measurement:** results carry a stage ID (`B` for this run) and the prompt's SHA-256 in their identity. Each stage writes its own results file (`benchmark_results_<stage>.jsonl`). The budget counts per stage. `--report` reads one stage, or compares stages. Stage A's file and report stay as they are. | [R5-A2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196) |
| S45-D3 | **Tighter scoring of planted defects:** leak terms identify each plant (its case wording, not the generic `PLANT-`), and expected terms describe the defect without quoting the planted line ("weakened", "accepts 401", "always passes", "non-holder"). Stage A's results are re-scored with the new key for comparison only; stage A's report stands. | [R5-A7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196) |
| S45-D4 | **New cases:** three stage-document cases planted on `e842e97`: a requirement no test could verify, an E2E test whose outcome guard accepts any status, and an architecture section whose new data flow gives a non-holder an asset. Plus the DPL-010 case: slice 2's change (`c4f9ca2..5a5aba7`, the launcher with its untested refusal paths, which are still untested), reviewed once with round 1's narrow question and once with the open mandate. | #33's description; [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147) |
| S45-D5 | **Codex only if confined.** First a probe (Environment facts) of whether `codex exec` can be kept from reading outside its copy and from loading the copy's `AGENTS.md` and its own user configuration. If the CLI's sandbox does not deny reads outside the copy, Codex runs inside a container that mounts only the copy and its login file, with no network except the model API. If neither works, Codex drops out of this stage, and that is reported to the owner as a decision concern, not worked around. A Codex review passes the same checks as a Claude review: the report schema, the empty-review rule, no outside reads and the publication check. | owner, 2026-11-08 (Codex, exception to POC-D2); POC-D3 (confinement); default (the container fallback and the stop) |
| S45-D6 | **Which runs, within 40:** Opus with the new setup on all 11 stage-A cases, the 3 stage-document cases and the DPL-010 case (15 runs). Opus with stage A's short prompt on the 4 new cases (4 runs); for the 11 old cases, stage A's short-prompt results are the baseline. Sonnet and Codex with the new setup on the 5 real misses and the 3 stage-document cases (8 runs each, 16 in all). The canary and its twin (2 runs). Total 37, with 3 left for retries. | default (the split), within the owner's budget |
| S45-D7 | **Decision rules, committed before the run:** (a) the new setup stays the default unless it detects fewer real and planted defects than the short prompt, or gives more than one false blocker per clean case; in either case the owner decides. (b) The default reviewer model is the cheapest one whose confirmed detections are within one of the best on the real misses and stage cases, with no more false blockers. Codex counts only if S45-D5 confined it. | owner (benchmark first); default (the rules) |
| S45-D8 | **The canary's twin is stronger:** its prompt tells it to act on the instruction files it finds, so the claim that instruction files do not reach a confined reviewer is measured, not only the claim about settings. The canary and the failed-Read probe are re-run whenever the CLI version in the attempt log changes, and the report records the versions. | [#42 comment](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/42#issuecomment-6725809234); [R6-7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844) |
| S45-D9 | **Order inside slice 4:** the Codex mode and its probe come first, so 4.4's critique can use Codex. The measurement runs after 4.1 to 4.4 are implemented. | default (4.4 needs Codex; the measurement needs the setup) |

## Requirements

None added (POC-D9).

## Success criteria

- At most 40 runs; every run, refusal and failure appears in the report.
- The report compares the new setup with stage A's short prompt, and Opus with Sonnet and Codex (or
  says why Codex dropped out), with hand-confirmed detections, and applies S45-D7.
- The canary is valid and passes with the stronger twin.
- Results of different stages, prompts or answer keys cannot be mixed without the report saying so.

## In scope

`scripts/run_review_benchmark.py` (stage identity, per-stage files and budget, the new cases),
`tests/review_benchmark/` (answer key version, new cases and patches, prompts), the launcher's Codex
mode (`scripts/run_independent_review.py`), the tooling tests, the report
`docs/slices/poc-4-5-benchmark/benchmark_report.md`.

## Out of scope

- Changing the review setup itself (4.1 to 4.4).
- Choosing reviewers per stage for the delivery loop (slice 7).
- More than 40 runs.

## Assets and holders

The Codex CLI's login is a credential under `HOME`. With S45-D5, the reviewer process cannot read it
(probe-checked). If the container route is used, only the login file and the copy are mounted. Before
anything is written, the publication check runs on Codex reports too. It knows the evidence secret
shapes, not OpenAI token shapes, so S45-D5's confinement, not the scanner, protects the login.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Codex CLI | `codex --version`; `codex exec --help` (2026-11-08) | 0.165.0. Flags: `--sandbox read-only\|workspace-write\|danger-full-access` (the sandbox limits *writes* of commands it runs); `--ignore-user-config`; `--ignore-rules` (execution-policy rules only); `--ephemeral`; `--output-schema <file>`; `--json` (JSONL events); `-C <dir>`. No flag to skip the project's `AGENTS.md`; whether a config key does (`project_doc_max_bytes`) is to be probed |
| Codex read confinement | to be probed at implementation, first step of this slice | Unknown. The read-only sandbox restricts writes; reads outside the working directory are expected to be possible, hence the container fallback |
| Stage A cost | stage A report | 24 runs: the 5-hour window rose from 22% to 35%, the weekly one from 2% to 4% |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Stage B results | `docs/slices/poc-4-5-benchmark/benchmark_results_B.jsonl` | runner | `--report` | committed | the comparison | authoritative only with the committed answer key's and prompts' hashes |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests (stage identity, per-stage budget, the new scoring, the Codex mode's checks with
  a fake `codex`); the canary and the report.
- Rulebook: `AGENTS.md` (Models and usage limits: the owner's Codex exception for benchmark reviews).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Stage and prompt identity in results | Comparing results from different prompts or keys (R5-A2) | Two fields and a file per stage | One shared file: it mixed results |
| Codex confinement probe and stop | A Codex reviewer reading the author's credentials | One probe; possibly a container | Trusting the read-only sandbox: it limits writes only |

## Retirement and compatibility

- Stage A's results and report stay as committed. The runner reads them as stage `A`.
- The answer key gets a new version. Stage A's key stays in the history, and its hash stays in its
  results.

## Review notes

Defaults by the author, for the owner to confirm: S45-D5 (the container fallback and the stop),
S45-D6 (the split of runs), S45-D7 (the rules), S45-D9 (the order).
