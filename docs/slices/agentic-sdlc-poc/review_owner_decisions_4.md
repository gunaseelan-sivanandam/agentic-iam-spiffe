# Review record — agentic-sdlc-poc, unit `owner-decisions-4`

The record of the review unit `owner-decisions-4`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt owner-decisions-4/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `6ca3d60e36fe`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Review of the owner's decision 8 of slice 4: the launcher ships round 4's initial mandate (2026-11-18)

## Intent

Round 4 of slice 4 (the decision page `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`, section "Round 4: the
review mandates and the runner fixes (2026-11-17)") approved three new mandates (R4-1) and measured the initial and
recheck wordings before shipping them (R4-4). The recheck wording met R4-4's criterion and the final wording, which no
case can measure, was approved; both shipped. The initial wording did not meet the criterion (8 false alarms against 7
in 4 no-defect reviews, while detecting 10 of 11 defect cases against 8), so the launcher kept 4.1's initial mandate
and decision 8 asked the owner. The owner asked why no decision could be made from the wording runs, heard the
author's answer (recorded in the paragraph "Decision 8 (the owner, 2026-11-18)" of that section), and decided, in the
owner's words: "yes, ship the R4-1 initial mandate and review it". The approved intent is that decision, R4-1's
Initial text, and the round-4 section as it stood; the criterion's recorded outcome stays as it is.

The change is the commits after `b354446` (the end of the review unit `owner-decisions-3`, which reviewed round 4's
work up to there) up to the reviewed commit: `6ca3d60`, which puts R4-1's Initial text into the launcher's
`MANDATES`, extends the test that pins the launcher's mandates to all three modes, notes in the benchmark's
configurations that `open+list` now means that text, records decision 8 on the decision page (the decided row, the
paragraph, discovered issue 64's facts, "Last updated" and the Progress row), and updates the implementation log,
`docs/STATUS.md`, `docs/slices/README.md` and the benchmark report. The work up to `b354446` was reviewed in its own
units. This is the initial review of the unit `owner-decisions-4`, and the first live review under round 4's initial
mandate.

## The author's self-review (claims to verify, not facts)

1. `MANDATES["initial"]` is R4-1's Initial text verbatim, and the launcher's initial prompt is byte for byte the prompt
   `open-R4+list` measured: on the 15 initial cases the launcher's own initial prompt equals `open-R4+list`'s whole
   prompt, and `open-R4+list`'s prompt identity equals its recorded runs' (built with no reviewer call).
2. `test_the_launcher_ships_r4_1s_mandates_in_all_three_modes` reads R4-1 from the decision page and fails if any of
   the three mandates drifts; on `b354446` its initial case failed (`AssertionError: assert 'Find anythin...f the
   review.' == 'Find anythin...s is valid.\n'`) and the other two passed.
3. No other launcher section, `AGENTS.md` sentence or live document states 4.1's initial wording; frozen records that
   do were left as they are.
4. The decision page records the owner's words, keeps the criterion's outcome, and presents the author's answer as
   the author's, not as a rule or process change.
5. At `6ca3d60`, locally: `make tooling-test` (1001 passed; shell 9), `make docs-check`, `make lint` and
   `make qa-trace` passed. Not run: the E2E suite (no runtime change) and CI (the branch is not pushed).

Known and put to the owner on the decision page: decision concerns 16 and 19, growth proposal 12, discovered issues 62
to 65.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 265, 1285, 1343-1344; branches not taken: 1284->1285, 1961->1963 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/run_review_benchmark.py: changed lines not run: 362, 409, 742, 986, 1306, 1856-1857; branches not taken: 361->362, 365->364, 408->409, 500->504, 741->742, 911->908, 917->911, 984->986, 1035->1038, 1287->1285, 1855->1856 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/check_review_records.py: changed lines not run: 48, 227-230, 234; branches not taken: 47->48, 228->229, 228->230, 233->234 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_brief.py: changed lines not run: 43, 304, 308; branches not taken: 42->43, 236->229, 307->308 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/review_inputs.py: changed lines not run: 316; branches not taken: 315->316 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/lint_changed_files.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "None of these lines is part of decision 8's change, which only edits `MANDATES` (lines 105-147). Line 265 is the module loader's `spec is None` guard. Line 1285 is `_record_text` called without a record. Lines 1343-1344 are `except ValueError: return` in `_complete_record`; its docstring leaves a missing section to the record check. The branch 1961->1963 runs only when HOME is empty or `/`. All are defensive or environment branches from earlier, already-reviewed units.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "These are defensive and mode-dispatch branches from earlier units, not decision 8's: an expected file missing in a case copy (362), a case without a list commit (409), a `RunState` without a sink (742), an already-recorded refusal (986), a clean-case kind without `unmatched_detections` (1306), and `--sample-confirmation` dispatch (1856-1857). Decision 8 only changed a comment at lines 109-112 of this file.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Line 215 is the guard for when `check_review_records.py` cannot be loaded. Defensive code, not touched by decision 8.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "Line 48 is the launcher-loader guard. Lines 227-230 and 234 are the CLI `main` and `__main__` entry, which the tests drive in-process through `check_review_records` and not as a subprocess (issue #44). Not touched by decision 8.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Line 43 is the loader guard. Lines 304 and 308 are `main`'s success return and the `__main__` entry. Branch 236->229 is an `accounted` status other than the three handled ones. All defensive or CLI code, not touched by decision 8.",
      "opened": [
        "scripts/review_brief.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "Line 316 is the early return in `_link_user_site` when no user site-packages directory exists. It depends on the environment and is not touched by decision 8.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "Branch 189->191 is a section without a status line, and 228->230 is a truncated tail whose previous line is not a round heading. Both are edge branches from 4.3, not touched by decision 8.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "This matches the author's claim 5 and the implementation log (\"CI (not pushed)\"). Under the decision page's Goal, CI's verdict counts when the owner pushes at the end. It is not a false claim, and CI still has to run before merge.",
      "opened": [
        "docs/history/implementation_log.md",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "benchmark_report.md:46-48 reads: \"`open+list` (4.1's mandate, the launcher's until decision 8), `open-B+list` (4.4's drafted initial mandate), `recheck-A` (4.1's recheck mandate) and `recheck-B` (4.4's drafted recheck mandate)\". benchmark_report.md:553-555 and run_review_benchmark.py:109-112 do note that both `open+list` and `recheck-A` now mean round 4's text. mandate_initial_r4.md:3 still says \"which the benchmark's configuration open-R4+list puts in place of the launcher's own, so that it is measured before it ships (R4-4)\".",
      "failure_scenario": "Someone who reads only the report's Configurations bullet sees an incomplete list of configurations. They may also take `recheck-A` to mean 4.1's recheck text for any new run, but a new run would now use round 4's text. No count is affected, because `current_lines` and the recorded prompt identities keep the old runs distinct.",
      "file": "docs/slices/poc-4-5-benchmark/benchmark_report.md",
      "id": "F1",
      "kind": "defect",
      "line": 46,
      "origin_stage": "implementation",
      "problem": "The benchmark report's configuration list was edited for decision 8 but is still incomplete and uneven. It now says `open+list` is \"4.1's mandate, the launcher's until decision 8\", yet calls `recheck-A` just \"4.1's recheck mandate\", with no note that it was the launcher's mandate only until R4-1 / `1f905a9`. It also leaves out `open+list+sev`, `open-R4+list` and `recheck-R4`, which appear further down the same report. Separately, the purpose line of `tests/review_benchmark/prompts/mandate_initial_r4.md:3` still describes the file as the text `open-R4+list` uses \"in place of the launcher's own, so that it is measured before it ships\", but since this change it is the same text as the launcher's own.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```

