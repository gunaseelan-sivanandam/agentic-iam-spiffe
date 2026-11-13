# Review record — agentic-sdlc-poc, unit `growth`

The record of the review unit `growth`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt growth/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `a8142714cd02`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Review of the owner-approved growth to slice 4's review launcher (2026-11-13)

## Intent

The owner approved three additions after slice 4's final review, in the owner's words: "yes, replace it and
implement both with proposal 9" (2026-11-13), recorded on the decision page
`docs/slices/agentic-sdlc-poc/slice_4_decisions.md` ("Decisions made", growth rows 5 and 9, decision concern 1):

1. A recheck must read every file a `rejected:` answer cites, as it must for a `fixed:` answer; an acceptance of a
   rejection rests on what it cites. This resolves decision concern 1.
2. A reviewer lists files it only searched (Grep, Glob) under an optional `searched` field, so `opened` stays a claim
   the launcher checks; a file under `opened` that the session did not Read still fails the review.
3. A finding may name the stage-checklist question that prompted it, in an optional `question` field (the list's
   name and the question's number, for example `code:10`); the benchmark report counts the findings that do.

The owner rejected an earlier proposal to drop unread files from `opened` instead of failing, because a review whose
acceptances rest on files the reviewer never read must not count. The change is the commit `a814271` on top of
slice 4; slice 4 itself was reviewed in its own units, and its final review predates this change.

## The author's self-review (claims to verify, not facts)

1. **Facts outside the repository.** None new: the CLI's structured output accepts optional properties of a JSON
   schema, as the existing optional evidence statuses already rely on; not probed again.
2. **Checks added or changed, and their tests** (`tests/tools/test_run_independent_review.py`, `tests/tools/test_run_review_benchmark.py`):
   `test_a_rejection_counts_only_when_the_files_it_cites_were_read` (a cited file not read fails; read passes; a cited
   path the copy does not hold and a rejection citing nothing pass), `test_cited_paths_keep_only_files_the_copy_holds`,
   `test_a_searched_file_need_not_be_read_but_an_opened_one_must`, `test_a_finding_may_name_the_checklist_question_that_prompted_it`
   (good and bad forms), `test_the_schema_offers_the_question_and_searched_fields_as_optional`,
   `test_an_entry_logged_with_an_earlier_schema_is_not_rebuilt`, `test_the_report_counts_findings_that_name_their_checklist_question`.
   The rejection test fails when the new rule is removed (checked by editing the launcher). 783 tooling tests pass.
3. **Claims checked mechanically.** The rules by the tests above. Not mechanical: whether reviewers will use
   `searched` and `question` as asked; no live review has run with them yet.
4. **Fixes and their upstream choice.** The repeated read-check failures came from the reviewer having no honest place
   for a file it only searched; `searched` changes that choice instead of loosening the check.
5. **Tried the way the next user runs it.** Through the launcher with the fake reviewer in the tests; this review is
   the first live run with the new output rules.
6. **Where each rule lives.** `AGENTS.md`, Independent review (Modes and prompts; Stage checklists); the launcher's
   `OPENED_RULE`, `QUESTION_RULE` and schema; the decision page.
7. **What was removed.** Nothing; an entry logged with the earlier schema can no longer be rebuilt, with a message.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 177, 769, 925, 983-984; branches not taken: 767->769, 924->925, 1452->1454 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_brief.py: changed lines not run: 43, 317, 321; branches not taken: 42->43, 227->222, 320->321 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/run_review_benchmark.py: changed lines not run: 313, 359, 634, 868, 1108, 1437-1438; branches not taken: 312->313, 316->315, 358->359, 438->442, 633->634, 801->798, 807->801, 866->868, 903->906, 1089->1087, 1250->1253, 1436->1437 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/lint_changed_files.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "Line 769 (the `searched` type check) is new in this growth and untested: finding G1-6. Lines 177, 925 and 983-984 are defensive paths from slice 4 (module load failure, a log without a record, a ValueError while completing a record in recover). Branch 1452->1454 (HOME is `/`) depends on the environment. These older paths are tracked as untested launcher paths in issue #45 (STATUS line 36).",
      "opened": [
        "scripts/run_independent_review.py",
        "docs/STATUS.md"
      ],
      "status": "flagged"
    },
    {
      "item": "EV2",
      "note": "Line 215 runs only when importlib cannot build a spec for `scripts/check_review_records.py`, a file that always ships next to it. It is a defensive fail-closed message, and the growth did not change it.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Line 43 is the defensive failure to load the launcher. Lines 203-210 are `main()` and the `__main__` guard, which run only when the script runs as a subprocess. The prompt notes that in-process coverage does not see subprocess runs (issue #44). None of this changed in the growth.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "Line 43 is the defensive load failure. Lines 317 and 321 are main's success return and the `__main__` guard, reached as a subprocess (issue #44). Branch 227->222 is an accounted entry whose status is explained or flagged, which correctly falls through the loop. Slice-4 code, unchanged by the growth.",
      "opened": [
        "scripts/review_brief.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Line 286 runs when the interpreter has no user site-packages directory, which depends on the machine running the tests. It returns without linking anything, which is the safe outcome.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "Branch 189->191 is a section without a status line. Branch 228->230 is an unlogged tail whose preceding line is not a round heading. Both are benign shapes of a record; no changed line goes unrun.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "These are slice-4.5 runner paths: a missing expected file (313), a case without a list (359), recording with no sink (634), a refused case already logged (868), the stage-A fallback for false alarms (1108) and the CLI path of `--sample-confirmation` (1437-1438). The benchmark's runs are over, and the untested benchmark paths are tracked in issue #45. The growth's `question_line` is covered by `test_the_report_counts_findings_that_name_their_checklist_question`.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/tools/test_run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The implementation log says the branch is local and not pushed, so CI has not run on this commit. The CI result of the PR head belongs in the handoff brief once the branch is pushed. No CI pass is claimed. The local validation record for this commit is a separate gap, raised as G1-5.",
      "opened": [
        "docs/history/implementation_log.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "scripts/run_independent_review.py:1144 `CITED_PATH = re.compile(r\"(?<![\\w./-])((?:[\\w.-]+/)+[\\w.-]+\\.\\w+)...\")` requires a slash. `fixed_paths` (line 1134) has no such limit, so `fixed: AGENTS.md: \u2026` is enforced. tests/tools/test_run_independent_review.py:1112-1114: `held = {\"tests/tools/test_a.py\", \"docs/b.md\"}`, and the expected result leaves out AGENTS.md without showing why. AGENTS.md:314-316 states the rule without this limit.",
      "failure_scenario": "An author answers a high finding `rejected: outside the threat model, see AGENTS.md (PoC scope)`, or `rejected: already gated by the unit-diff-cov target in Makefile`. The recheck greps or reads nothing at the root, accepts the rejection and completes. The launcher reports no read problem, so the acceptance rests on a file the reviewer never opened. Decision concern 1 was meant to close exactly this case. Note that the copy's AGENTS.md can differ from the base AGENTS.md that the prompt quotes.",
      "file": "scripts/run_independent_review.py",
      "id": "G1-1",
      "kind": "defect",
      "line": 1144,
      "origin_stage": "implementation",
      "problem": "The new rule says a recheck must read every file a `rejected:` answer cites. In practice only paths with at least one directory part count. `CITED_PATH` needs `(?:[\\w.-]+/)+` before the file name, so a rejection that cites a root-level file (`AGENTS.md`, `README.md`, `Makefile`, `ruff_changed_files.toml`) adds nothing to `must_read`. The test meant to cover this hides the gap: `test_cited_paths_keep_only_files_the_copy_holds` puts \"see AGENTS.md\" in the answer, but its `held` set does not contain AGENTS.md. The test passes whether the regex dropped the path or the existence filter did. `AGENTS.md` (Modes and prompts) and the decision page (growth row 5) both say \"every file a `rejected:` answer cites\", so they overclaim.",
      "severity": "high"
    },
    {
      "evidence": "`cited_paths` returns `[p for p in \u2026 if exists(p)]` (line 1150). `check_answers` refuses a missing `fixed:` path (lines 1220-1222) but has no matching branch for `rejected:` (lines 1226-1227). The test case `cited-path-not-in-the-copy` (tests/tools/test_run_independent_review.py:1095) checks that such an answer passes.",
      "failure_scenario": "The author answers `rejected: covered by tests/tools/test_run_review_benchmark.py::test_x` but means test_run_independent_review.py. The cited file does not exist, so nothing must be read, and the recheck can accept on the author's word. A one-line note in the prompt or the end entry (\"cited, not in the copy: \u2026\") would let the reviewer see the missing citation.",
      "file": "scripts/run_independent_review.py",
      "id": "G1-2",
      "kind": "defect",
      "line": 1150,
      "origin_stage": "implementation",
      "problem": "When a `rejected:` answer cites a path the copy does not hold, the launcher drops it silently. A `fixed:` answer that names a missing path makes the launcher refuse the recheck. So a rejection resting on a test file that does not exist (a typo, or a test never written) needs no read and gets no warning. The exemption is meant for retired files, but the launcher cannot tell a retired file from a wrong citation. The owner's decision does not ask for the exemption; it is the author's default.",
      "severity": "medium"
    },
    {
      "evidence": "scripts/run_review_benchmark.py:1382 inserts `question_line(lines)` into `report_stage_b`. benchmark_report.md:199-200 runs straight from `Repeats \u2026` to `Second confirmer: \u2026`. slice_4_decisions.md:292 says \"Done: the launcher's schema and output section, `AGENTS.md` (Stage checklists), the benchmark report\". implementation_log.md:33 says \"which the benchmark report counts\".",
      "failure_scenario": "The owner reads the decision page as \"done\" and the report as the runner's verbatim output. Rerunning `--report --stage B` gives text that differs from the stored block, and the report's statement about the schema contradicts the launcher. One line dating the report before the field, plus a correction of row 9's \"Done\", would fix it.",
      "file": "docs/slices/poc-4-5-benchmark/benchmark_report.md",
      "id": "G1-3",
      "kind": "defect",
      "line": 94,
      "origin_stage": "implementation",
      "problem": "The decision page and the implementation log say the benchmark report counts the findings that name their question. The committed report does not. Line 94 says \"The reviewer schema has no field for the question\", which this change made false. The runner's report, \"kept verbatim\" at lines 179-200, lacks the line `question_line` now emits between the Repeats and Second-confirmer lines. Only the runner function counts the findings; no committed report does.",
      "severity": "medium"
    },
    {
      "evidence": "docs/STATUS.md:3 `Last updated: 2026-11-10`, and docs/STATUS.md:16-18 `\u2026 one dry slice ran; the final review and the handoff are next.` docs/slices/agentic-sdlc-poc/slice_4_decisions.md:95: Final review \"Ended after round 2\". A Grep of STATUS.md for growth, rejected and question found no mention of the growth.",
      "failure_scenario": "The owner or the next agent reads STATUS to see where slice 4 stands. They conclude the final review has not run, and they do not learn that the launcher's report schema and read check changed after it.",
      "file": "docs/STATUS.md",
      "id": "G1-4",
      "kind": "defect",
      "line": 18,
      "origin_stage": "implementation",
      "problem": "`docs/STATUS.md` is stale for this change. It still says \"the final review and the handoff are next\" and \"Last updated: 2026-11-10\", but the decision page records the final review as ended after round 2. The owner-approved growth and its review unit `growth` are not mentioned. Step 4 of the slice workflow requires STATUS to be updated in the same change.",
      "severity": "medium"
    },
    {
      "evidence": "docs/history/implementation_log.md:8 heading `## 2026-11-10 \u2026`; lines 31-34 add the 2026-11-13 growth; lines 38-43 still say 764 passed and do not mention the growth's own runs (qa-quality, lint, docs-check after the schema change).",
      "failure_scenario": "A later reader takes the 764-test validation as covering the growth commit. Nothing records that `make qa-quality`, `make lint` or `make docs-check` were run on a814271, and nothing says they were not.",
      "file": "docs/history/implementation_log.md",
      "id": "G1-5",
      "kind": "defect",
      "line": 31,
      "origin_stage": "implementation",
      "problem": "The growth is recorded as a bullet inside the 2026-11-10 entry, not as a dated entry, and it has no validation results of its own. The entry's validation line still reports `make tooling-test` 764 passed. The task text claims 783 tooling tests pass after the growth. The rules ask each change's entry to give what changed, the validation results and what was not run and why.",
      "severity": "medium"
    },
    {
      "evidence": "EV1: line 769 not run, and branch 767->769 not taken. A Grep of tests/tools for `searched is not` found nothing.",
      "failure_scenario": "A refactor drops or inverts the `searched` type check, and no test fails. A reply with `searched: \"docs/x.md\"` (a string) would then pass `validate_report`, and anything that iterates over `searched` would read single characters as paths.",
      "file": "scripts/run_independent_review.py",
      "id": "G1-6",
      "kind": "defect",
      "line": 769,
      "origin_stage": "tests first",
      "problem": "No tooling test triggers the new refusal path for a malformed `searched` field (a non-list, or a list holding a non-string). `test_a_searched_file_need_not_be_read_but_an_opened_one_must` covers only a well-formed `searched`. The CLI's JSON schema enforces the shape first, so this path matters mainly when the reply comes through `result` text instead of `structured_output`. Either way it is a new validation branch with no test.",
      "severity": "medium"
    },
    {
      "evidence": "QUESTION_PATTERN = r\"^[a-z0-9-]+:[1-9][0-9]?$\" (line 69). `_output_section` (lines 468-496) is the same for every mode. `question_line` (run_review_benchmark.py:1323-1332) counts any non-empty value.",
      "failure_scenario": "A reviewer writes `plan:5` for `plan-and-test-plan:5`. The finding validates, and the benchmark count names a list that does not exist.",
      "file": "scripts/run_independent_review.py",
      "id": "G1-7",
      "kind": "defect",
      "line": 69,
      "origin_stage": "implementation",
      "problem": "`QUESTION_PATTERN` checks only the form `name:number`, not that the list exists or that it has a question with that number. `foo:12` or `code:13` (the code list has 12 questions) are accepted, and the benchmark's `question_line` counts them. Also, the final review gets no list but still receives `QUESTION_RULE` in its output section.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to growth/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| G1-1 | high | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py: a cited path no longer needs a directory part, so a rejection citing `AGENTS.md`, `README.md` or `Makefile` must have it read; a plain word that names no file of the copy is prose. `test_a_rejection_citing_a_root_level_file_must_read_it`, and the cited-path test now holds the root files it names, so it fails when the regex drops them. The origin was a pattern written for `dir/file.ext`, and a test whose held set let either filter pass; the `fixed:` path rule was checked for the same cause and has no directory requirement |
| G1-2 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py: a `rejected:` answer citing a path (with a directory part) that the copy does not hold is refused before any call, as a `fixed:` answer naming a missing file is; a cited file the change deletes is read through the change's diff (`test_a_rejection_citing_a_path_the_copy_lacks_is_refused_before_any_call`). Two tooling tests whose rejections cited files their fixtures lack now cite real ones |
| G1-3 | medium | fixed: docs/slices/poc-4-5-benchmark/benchmark_report.md: the sentence says the schema had no question field when the reviews ran and that the field came after them, and the runner's verbatim report is rebuilt with its new line (0 of 306 findings name a question) |
| G1-4 | medium | fixed: docs/STATUS.md: dated 2026-11-13; the final review ended after round 2, the growth is implemented and reviewed, the owner's push is next |
| G1-5 | medium | fixed: docs/history/implementation_log.md: the growth has its own dated entry, 2026-11-13, with its own validation results and what was not run, and the bullet left in the 2026-11-10 entry is removed |
| G1-6 | medium | fixed: tests/tools/test_run_independent_review.py: `test_a_searched_field_that_is_not_a_list_of_paths_fails` (a string, and a list holding a number) |
| G1-7 | low | rejected: the schema checks the form, and a wrong list name or number is visible as given in the record and in the benchmark's count; checking it against the review's lists would carry the stage lists into report validation for a low finding. The final review's output section names `question` "where a question of the stage checklist prompted it", which never applies without a list |

## Round 2

### Attempt growth/c1/r2/A/1

Reviewer `A`: `claude-opus-5-5`, effort medium, mode recheck, commit `a1677ec2418b`, base `3347754ef038`.

Status: failed (the report does not account for what it was given: G1-3 names an opened file the attempt did not read; docs/slices/poc-4-5-benchmark/benchmark_report.md is named in a fixed: or rejected: answer and was not read).

#### Prompt

```markdown
# Recheck of the owner-approved growth to slice 4's review launcher, round 2

The intent is unchanged from round 1: the three additions the owner approved on 2026-11-13 (a recheck reads every
file a `rejected:` answer cites, as for a `fixed:` answer; a `searched` list for files only searched; an optional
`question` on each finding, counted by the benchmark report). Round 1's report and the author's answers are below;
the fixes are what the reviewed commit adds after `a814271`. Among them: a cited path no longer needs a directory part,
a cited path the copy lacks is refused before any call, the benchmark report and STATUS are current, and the growth
has its own dated implementation-log entry.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 177, 925, 983-984; branches not taken: 924->925, 1467->1469 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_brief.py: changed lines not run: 43, 317, 321; branches not taken: 42->43, 227->222, 320->321 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/run_review_benchmark.py: changed lines not run: 313, 359, 634, 868, 1108, 1437-1438; branches not taken: 312->313, 316->315, 358->359, 438->442, 633->634, 801->798, 807->801, 866->868, 903->906, 1089->1087, 1250->1253, 1436->1437 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/lint_changed_files.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```


### Attempt growth/c1/r2/A/2

Reviewer `A`: `claude-opus-5-5`, effort medium, mode recheck, commit `a1677ec2418b`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Recheck of the owner-approved growth to slice 4's review launcher, round 2

The intent is unchanged from round 1: the three additions the owner approved on 2026-11-13 (a recheck reads every
file a `rejected:` answer cites, as for a `fixed:` answer; a `searched` list for files only searched; an optional
`question` on each finding, counted by the benchmark report). Round 1's report and the author's answers are below;
the fixes are what the reviewed commit adds after `a814271`. Among them: a cited path no longer needs a directory part,
a cited path the copy lacks is refused before any call, the benchmark report and STATUS are current, and the growth
has its own dated implementation-log entry.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 177, 925, 983-984; branches not taken: 924->925, 1467->1469 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_brief.py: changed lines not run: 43, 317, 321; branches not taken: 42->43, 227->222, 320->321 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: scripts/run_review_benchmark.py: changed lines not run: 313, 359, 634, 868, 1108, 1437-1438; branches not taken: 312->313, 316->315, 358->359, 438->442, 633->634, 801->798, 807->801, 866->868, 903->906, 1089->1087, 1250->1253, 1436->1437 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV8: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

Every changed line and branch run by the tooling tests: scripts/lint_changed_files.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "G1-1",
      "note": "CITED_PATH (line 1144) now allows zero directory parts, and `cited_paths` keeps every token that names a blob of the copy (`file_at` uses `git cat-file blob`, so directories do not count). `test_a_rejection_citing_a_root_level_file_must_read_it` fails a recheck that cites AGENTS.md without reading it. The cited-path unit test now holds AGENTS.md and Makefile and expects both, so it would fail if the regex dropped root files.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "G1-2",
      "note": "`_rejection_reads` (lines 1235-1243) refuses a cited path that has a directory part and that the copy lacks, unless the change deletes it; a deleted file is read through change.diff. `test_a_rejection_citing_a_path_the_copy_lacks_is_refused_before_any_call` checks exit 2, the message, and that no call was made. A side effect is that prose with a slash is also refused (G2-1, low).",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "G1-3",
      "note": "benchmark_report.md:94-96 now says the schema had no question field when the runs happened and that the field came later (0 of these runs' findings). The verbatim runner block includes `Findings that name their checklist question: 0 of 306 (none).` at line 201, between Repeats and Second confirmer, which is where question_line puts it.",
      "opened": [
        "docs/slices/poc-4-5-benchmark/benchmark_report.md"
      ],
      "status": "accepted"
    },
    {
      "item": "G1-4",
      "note": "STATUS.md:3 is dated 2026-11-13. Lines 18-20 record that the final review ended after round 2, that the growth (unit `growth`) is implemented and reviewed, and that the owner's push and the final PR are next.",
      "opened": [
        "docs/STATUS.md"
      ],
      "status": "accepted"
    },
    {
      "item": "G1-5",
      "note": "implementation_log.md:8-22 is now a separate dated entry for 2026-11-13. It records what changed, its own validation (786 tooling tests, qa-quality, PR-mode trace, lint) and what was not run (E2E, CI), each with a reason. The bullet about the growth is gone from the 2026-11-10 entry (lines 24-55).",
      "opened": [
        "docs/history/implementation_log.md"
      ],
      "status": "accepted"
    },
    {
      "item": "G1-6",
      "note": "`test_a_searched_field_that_is_not_a_list_of_paths_fails` sends a string and a list holding a number through validate_report and expects 'searched is not a list of paths' (line 769). Both halves of the condition are exercised.",
      "opened": [
        "tests/tools/test_run_independent_review.py",
        "scripts/run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "G1-7",
      "note": "This is a low finding, so the fix is the author's choice. The reason holds: the value is visible as written in the record and in the benchmark count. Checking it against the stage lists would bring the lists into report validation. The rejection cites no file of the copy.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "accepted"
    },
    {
      "item": "EV1",
      "note": "Line 769 is no longer in the not-run list, because G1-6's test covers it. What remains is defensive slice-4 code: line 177 (module load), 925 (a log without a record) and 983-984 (recover). Branch 1467->1469 is the HOME-is-`/` case in local_paths, which depends on the environment. These are tracked in issue #45.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "Line 215 is a defensive fail-closed message for when importlib cannot build a spec for a sibling script that always ships with it.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Line 43 is a defensive load failure. Lines 203-210 are main() and the __main__ guard, which run only as a subprocess (issue #44).",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "Line 43 is a defensive load failure. Lines 317 and 321 are main's return and the __main__ guard, run only as a subprocess. Branch 227->222 is an explained or flagged entry falling through the loop, which is correct.",
      "opened": [
        "scripts/review_brief.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Line 286 runs on a machine with no user site-packages directory. It returns without linking anything, which is safe.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "Branch 189->191 is a section without a status line. Branch 228->230 is a tail whose previous line is not a round heading. Both are benign shapes of a record, and every changed line runs.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "These are slice-4.5 benchmark runner paths: CLI branches such as --sample-confirmation at 1437-1438, and refusal and fallback paths. The benchmark runs are finished, and the paths are tracked in issue #45. The growth's question_line is tested.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The branch is not pushed, and the implementation log says that CI was not run for this reason. No CI pass is claimed. The CI result belongs in the PR handoff after the push.",
      "opened": [
        "docs/history/implementation_log.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "`CITED_PATH` (line 1144) matches `(?:[\\w.-]+/)*[\\w.-]+`, and `cited_paths` returns `[p for p in tokens if \"/\" in p and p not in held]` as missing (line 1154). `_rejection_reads` raises `ReviewRefusedError` on any of them (lines 1239-1242). No test covers prose with a slash; searched tests/tools/test_run_independent_review.py for `and/or` and for slash-joined words.",
      "failure_scenario": "An author answers `rejected: the finding is outside the threat model and/or covered by AGENTS.md`. The launcher refuses the recheck before any call. The author has to work out that `and/or` was taken as a path and reword the answer.",
      "file": "scripts/run_independent_review.py",
      "id": "G2-1",
      "kind": "defect",
      "line": 1154,
      "origin_stage": "implementation",
      "problem": "The G1-2 fix treats any slash-joined word in a `rejected:` answer as a cited path. If the copy has no file at that path, the launcher refuses the recheck. Ordinary prose such as `and/or`, `fixed/rejected` or `S41-D7/S41-D8` therefore stops a recheck with \"cites a path that is not in the copy\". This fails closed: nothing is accepted that should not be, and the message names the token, so the author can reword the answer. It is friction, not a false green.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to growth/c1/r2/A/2

| ID | Severity | Answer |
| --- | --- | --- |
| G2-1 | low | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py: a slash-joined word counts as a missing cited path only when it ends in a file extension, so prose such as `and/or` or `S41-D7/S41-D8` stays prose; the cited-path test holds both |
