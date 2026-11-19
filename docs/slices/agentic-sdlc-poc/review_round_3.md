# Review record — agentic-sdlc-poc, unit `round-3`

The record of the review unit `round-3`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt round-3/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `af9ba98cb1f8`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Review of round 3 of slice 4: rechecks that look before they accept (2026-11-17)

## Intent

After the review of the owner's decisions of 2026-11-16 ended, the author proposed to close slice 4 and leave the
recheck's reliability to the next slice. The owner, 2026-11-17: "Why wait till next slice, this slice 4 is to fix the
review checklist, prompts and make sure the review part is reliably covered I still feel like we are missing that";
and, on the author's proposal: "Round 3 of slice 4: I approve R3-1 to R3-4, the budget 85 → 95, and the probe and
replays". The approved intent is the decision page `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`, section
"Round 3: rechecks that look before they accept (2026-11-17)": its problem statement, the table of changes R3-1 to
R3-4, the four measurements with the criteria fixed before any run, and the stop rule; with the two "Decisions made"
rows of 2026-11-17. Within round 3 the owner also decided decision concern 18, option (b), "Count diff lines
(Recommended)" when asked, and then "I choose your recommendation": lines a recheck read in `change.diff` count as
seen lines of the files they belong to (each hunk's line numbers), a quote still names the file and its text must be
at that place, and the `mechanics` replay runs once more and is reported whatever it shows; this changes R3-2's
"seen" and the round's stop rule for this one change. The section's "Not in round 3" paragraph says what is out of
scope (rewording the recheck mandate; growth proposal 12).

The change is the commits after `292f270` (the decision page with the owner's approval of round 3) up to the reviewed
commit: R3-1 in `scripts/run_independent_review.py`, `scripts/review_inputs.py` and `AGENTS.md` (What the reviewer
receives); R3-2 and decision concern 18 (b) in `scripts/run_independent_review.py` and `AGENTS.md` (Modes and
prompts), with `29061a7` and `5627de7` the output section's wording-only commits (decision 2); R3-3 in the launcher's
wording (`9a57a88`) and `AGENTS.md` (`de44fdd`); R3-4 in `docs/review_checklists/plan-and-test-plan.md`; the stage-B
budget of 95 and the blind-confirmation token in `scripts/run_review_benchmark.py` and
`tests/review_benchmark/answer_key.yaml`; the runs' results in `docs/slices/poc-4-5-benchmark/`; and the records on
the decision page, `docs/delivery_problem_log.md` (DPL-014), `docs/history/implementation_log.md` (the two entries of
2026-11-17), `docs/STATUS.md` and `docs/slices/README.md`. The work before `292f270` was reviewed in its own units.
This is the initial review of the unit `round-3`, measurement 4 of the section; its recheck will run under R3-1 and
R3-2 as decision concern 18 changed them.

## The author's self-review (claims to verify, not facts)

1. **What was built.** R3-1: a recheck's `change.diff`, files under review, upstream items other than the governing
   plan, changed script lines and trace gaps come from the commits since the commit the unit's previous round
   reviewed, as the attempt log records it (their common ancestor when that round's reviewers reviewed different
   commits); the copy holds the whole branch and the CI results stay those of the reviewed commit. The launcher
   refuses a recheck whose reviewed round's commit is not an ancestor of the reviewed commit, drops a `--path` outside
   the range, and runs a recheck whose range changes no file. `PROCESS_FILES` adds the benchmark runner, its answer
   key and `.claude/skills/` (decision concern 15). R3-2: the launcher keeps each tool call's output and computes the
   lines an attempt was shown (a successful Read's window; the lines a content-mode Grep printed; none for a Grep that
   lists files or counts); every file a `fixed:` answer names or a `rejected:` answer cites must be seen; every such
   answer a recheck accepts or re-raises is quoted from a file the answer names or cites, as the file is in the copy
   (from `change.diff` only for a named file the range deletes), and a quote counts only within two lines of a line
   the attempt was shown; `opened` is no longer checked, and `searched` is gone from the schema. Decision concern 18
   (b): each shown line of `change.diff` maps to the file line it shows (`diff_places`): a context or added line at
   its new path and line, a removed line only for a file the diff deletes, at its old line, a header line nowhere.
   R3-3: the recheck's mechanism question, the output section's kind bullet and `AGENTS.md` (Fixes stay within the
   agreed decisions) say that what an existing rule already requires of a fix, such as a test for new behaviour or a
   handoff record, is not an added mechanism. R3-4: question 8 of the plan list asks the fix rule since R2-4, and its
   "Blocks at this stage" gains a clause for a false small-slice claim; the list keeps 12 questions. The runner: the
   stage-B hard stop (`BUDGETS`) and the key's `budget:` are 95, the key is version 7 and names version 6's hash, and
   a blind-confirmation token is keyed by case, configuration, prompt identity, run and finding (`token_key`).
2. **The probe's details and the author's choices.** The probe's result set R3-2's details (a) to (d), which the
   decision page states were chosen by the author; detail (b), a quote counts only where its lines were shown, is
   stated there as the author's reading of "a file counts as seen", which the owner may narrow back to whole files.
   The author also chose one definition of "seen" for every mode, so an initial review's empty-review rule
   (`_confinement_failure`) counts diff lines too, while the owner approved (b) for rechecks; two tests pin it
   (`f75bc7a`). The probe's and the replays' analyses are not tracked; the decision page and the implementation log
   carry their results.
3. **Facts outside the repository.** The probe: one recheck on the launcher at `292f270` of a scratch record, USD
   0.49, CLI 2.1.326, Opus at medium. The replays: the three rechecks that failed the old read check, on the launcher
   at `3df47b7`, one call each and no retry, the pinned CLI 2.1.323, USD 3.07, each in a scratch clone, so the
   repository's records are untouched; the criterion was not met (`mechanics` failed: decision concern 18). After
   (b), `mechanics` ran once more on the launcher at `5627de7`, one call, USD 1.37: completed and approvable, 15
   accepted, 1 re-raised (H1), with a counterfactual of both launchers' accounting checks on both attempts. RC-1 to
   RC-4 on `recheck-A`: calls 83 to 86 of 95, one try each, the pinned CLI 2.1.323, USD 0.94, in
   `docs/slices/poc-4-5-benchmark/benchmark_results_B.jsonl`; their four findings were exported as M149 to M152 and
   judged blind by a fresh session given only those rows and the match rule (`fa7953f`); criterion met on confirmed
   verdicts. Costs and minutes come from the runs' own stats. This review runs on the installed CLI 2.1.326.
4. **Checks added or changed, and their tests.** The tests the section "Round 3" names under each "As built"
   paragraph, in `tests/tools/test_run_independent_review.py`, `tests/tools/test_review_inputs.py`,
   `tests/tools/test_run_review_benchmark.py` and `tests/tools/test_stage_checklists.py`, with changes to
   `tests/tools/test_check_review_records.py` and the fake CLI `tests/tools/fakes/fake_claude.py`. Each new test's
   failure on the code before its change is in the implementation log entries of 2026-11-17; G2-1's test and the twin
   of `f75bc7a`'s test passed on the unchanged code, which the log states.
5. **Claims checked mechanically.** At `f75bc7a`, locally: `make lint`, `make docs-check`, `make qa-trace`,
   `make test-lint`, `make unit-guard-check` (357), `make qa-deploy` and `make tooling-test` (976 passed; shell 9)
   passed. The records released before R3-2 still pass the record check
   (`test_the_repository_records_released_with_searched_and_unquoted_fixes_still_pass_the_record_check`). After
   `a9ec037` the stage-B report was byte-identical to the one before it, `--rescore B` gave all 62 recorded scores,
   and `--export-rescore` on the results committed before the runs exported nothing. Not run: the E2E suite,
   `make gate-consistency`, `make unit-trust`, `make unit-mutation`, `make unit-diff-cov`, and CI (the branch is not
   pushed). Not mechanical: the wording of R3-3 and R3-4, the blind verdicts on M149 to M152, the readings of the
   probe and the replays, and the decision page's prose.
6. **Fixes and their upstream choice.** DPL-014: a blind-confirmation token was keyed without the result line's
   prompt identity, so a new `run: 1` line could take an earlier line's verdict; the key now names it, fixed
   (`a9ec037`) before the runs it would have affected. Decision concern 18 (b) changes what "seen" covers; the
   must-see check, the quote's file rule, the place check and its two-line tolerance are unchanged.
7. **Where each rule lives.** `AGENTS.md` (Modes and prompts, What the reviewer receives, Fixes stay within the
   agreed decisions); the launcher's output section (`SEEN_RULE`, `QUOTE_RULE`, the mechanism question, the kind
   bullet) and its accounting and quote checks; `PROCESS_FILES` in `scripts/review_inputs.py`; the plan list; the
   runner's `BUDGETS` and the key's `budget:`; the decision page.
8. **What was removed.** From `AGENTS.md`: the `searched` list, the failure for an opened file the recheck did not
   read, and "read" as the test for a file an answer names or cites. From the launcher: `searched` in the schema and
   its check, `OPENED_RULE`, and the check that every file under `opened` was read. They are in this review's change
   like the additions.

Known and put to the owner on the decision page: measurement 2's criterion was not met by the first replays, and
the second `mechanics` replay is one run, with 4 evidence entries instead of 5 (discovered issue 59); RC-1's quote of
the harness is not verified, since the runner keeps no stream (discovered issue 45); H1 and N1 of the second replay
still hold in slice 4.5's runner (discovered issues 56 and 57); decision concern 16 is open; growth proposal 12
stays open; the author's choice of one "seen" for every mode, which the owner may restrict to rechecks.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 239, 773, 931, 1250, 1308-1309; branches not taken: 772->773, 930->931, 1249->1250, 1922->1924 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/review_inputs.py: changed lines not run: 307; branches not taken: 306->307 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/run_review_benchmark.py: changed lines not run: 354, 401, 718, 962, 1282, 1811-1812; branches not taken: 353->354, 357->356, 400->401, 492->496, 717->718, 887->884, 893->887, 960->962, 1011->1014, 1263->1261, 1810->1811 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/check_review_records.py: changed lines not run: 48, 227-230, 234; branches not taken: 47->48, 228->229, 228->230, 233->234 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/review_brief.py: changed lines not run: 43, 301, 305; branches not taken: 42->43, 233->226, 304->305 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
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
      "note": "Line 773 (`_result_text` list branch) is new R3-2 parsing that no test runs; raised as F3. Lines 239, 1250 and 1308-1309 are defensive paths that existed before round 3 (module load failure, a log without a record, a missing record section). Line 931 and branch 930->931 cover a Grep whose path lies outside the copy, which `_confinement_failure` already fails as an outside call. Branch 1922->1924 is a HOME equal to '/'.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/fakes/fake_claude.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV2",
      "note": "Line 307 is the early return when the interpreter has no user site-packages directory. It depends on the environment, works on the scratch HOME only, and is not round-3 logic.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "The lines not run are defensive or environment branches of the runner: an expected location missing from the copy (354), a case without an artifact type (401), a state without a sink (718), a refused case already recorded (962), and loop and branch exits. The round-3 runner changes, BUDGETS 95 and `token_key`, are run, and named tests cover them.",
      "opened": [
        "scripts/run_review_benchmark.py",
        "tests/review_benchmark/answer_key.yaml"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "Line 215 is the failure message when check_review_records.py cannot be loaded, a defensive path, not round-3 behaviour.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Line 48 is the launcher-load failure. Lines 227-230 and 234 are `main()` and the `__main__` guard, which make docs-check runs as a subprocess. In-process coverage does not see those (issue #44, stated in the evidence).",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "Line 43 is the module-load failure. Lines 301 and 305 are `main()`'s success return and the `__main__` guard, run as a subprocess. Branch 233->226 is an accounted entry with an evidence status, which the loop correctly skips.",
      "opened": [
        "scripts/review_brief.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "Only two partial branches of the record helpers are not taken, and no changed line is unrun. They are not part of the round-3 checks.",
      "opened": [],
      "status": "explained"
    },
    {
      "item": "EV8",
      "note": "The branch is not pushed, as the task text says, so no CI result exists for this commit. The local gate runs it lists are a diagnosis and do not replace CI. CI must still run on the PR, and gate-consistency, unit-trust, unit-mutation, unit-diff-cov and E2E were not run locally. Known and disclosed; no finding.",
      "opened": [
        "docs/history/implementation_log.md",
        "docs/STATUS.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "run_independent_review.py:1177-1178 `shown = lines_shown(summary, copy_root)` / `failure = _confinement_failure(stats, review_paths, set(shown))` runs for every mode; :841 `return _with_diff_lines(shown, copy_root)`. slice_4_decisions.md:574-579 calls it 'The author's choice ... one definition of \"seen\" for every mode ... The owner approved (b) for rechecks and may restrict it to them'. AGENTS.md:359-363 describes it for rechecks only. The base rulebook says: 'A fix that would change an agreed decision goes to the user as a question before it is applied', and 'Do not introduce or keep runtime-significant behavior that exists only in code'.",
      "failure_scenario": "An initial plan or implementation review with `--path plan.md` reads only the first hunk of change.diff that touches plan.md, plus other files. It no longer fails the empty-review rule, which S42-D2 kept so that hinted files are opened. A reader of AGENTS.md cannot tell that this changed. If the owner later restricts (b) to rechecks, as the decision page offers, the rulebook gives no sign that initial reviews ever behaved differently. Fix: ask the owner first and state the rule in AGENTS.md, or restrict diff-line seeing to rechecks.",
      "file": "scripts/run_independent_review.py",
      "id": "F1",
      "kind": "defect",
      "line": 1164,
      "origin_stage": "implementation",
      "problem": "The empty-review rule for initial (and final) reviews now counts change.diff lines as 'seen' (decision concern 18 (b)). The owner did not approve that, and the rulebook does not say it. The owner decided (b) for rechecks: 'lines a recheck read in change.diff count as seen lines'. S42-D2's empty-review rule says 'a review that read none of the paths under review fails'. `classify` passes `set(lines_shown(...))`, diff lines included, to `_confinement_failure` in every mode. So an initial review that read only a hunk of `_review_inputs/change.diff` now meets the rule, where before it had to Read a path under review. In `AGENTS.md` (Modes and prompts, lines 359-363) diff-line seeing is a recheck rule ('the lines of the change's diff the recheck was shown'). 'What the reviewer receives' only says `--path` 'carries the empty-review rule'. So the wider initial-review behaviour is recorded only in the code, the decision page and the implementation log.",
      "severity": "medium"
    },
    {
      "evidence": "main(): `since = earlier_commits(log.entries(), spec, admission.to_run)` then `recheck_inputs(repo, inputs, since)` (:2247-2248), which uses `merge-base --octopus` when there are several (:460). invocation_from_entry: `inputs = recheck_inputs(repo, inputs, (_entry_earlier(entry, repo, record)[0]['commit'],))` (:2205), a single commit; diff_sha256 at :2221 uses `inputs.since`. The only recheck rebuild test, `test_recheck_prompt_is_rebuilt_from_its_entry_and_a_changed_answers_section_mismatches` (tests/tools/test_run_independent_review.py:1264), has one reviewer. `test_a_recheck_whose_reviewers_reviewed_different_commits_starts_at_their_common_ancestor` calls `recheck_inputs` directly and never rebuilds.",
      "failure_scenario": "Round 1 has reviewers A (at commit X) and B (at a later commit Y). Round 2 rechecks both, so change.diff starts at merge-base(X, Y) = X. Rebuilding B's start entry uses Y and reports diff_sha256, paths_sha256, upstream_sha256 and full_prompt_sha256 as mismatched, although the logged prompt was right. A record that the launcher wrote correctly then looks altered, and the docstring's 'the launcher and invocation_from_entry build them the same way' is false for this case.",
      "file": "scripts/run_independent_review.py",
      "id": "F2",
      "kind": "defect",
      "line": 2205,
      "origin_stage": "implementation",
      "problem": "`invocation_from_entry` rebuilds a recheck from only the entry's own earlier attempt commit. The launcher starts the range at the common ancestor (`merge-base --octopus`) of all the commits that the round's reviewers reviewed. When reviewers reviewed different commits, the rebuild uses another range, so its hashes cannot match the logged entry. No test covers a rebuild of a multi-reviewer recheck.",
      "severity": "medium"
    },
    {
      "evidence": "EV1 lists line 773 not run. fake_claude.py:62 `content = \"error\" if is_error else str((result or {}).get(\"content\", \"ok\"))`. `_grep_lines` (:927) parses `output.text`, which `_result_text` produces.",
      "failure_scenario": "A CLI version returns a content-mode Grep result as `[{\"type\": \"text\", \"text\": \"path:12:...\"}]`. If the join, or a block holding no `text` key, behaves differently than intended, the Grep's lines are not counted. A recheck that looked through Grep then fails 'was not seen' or 'lines the attempt was not shown'. Each such case costs a failed session, which round 3 was meant to stop. It is a false failure, not a false green.",
      "file": "scripts/run_independent_review.py",
      "id": "F3",
      "kind": "defect",
      "line": 773,
      "origin_stage": "tests first",
      "problem": "R3-2 builds the seen lines from each tool result's text. `_result_text` has a branch for content given as a list of blocks, and no test runs it (evidence EV1: line 773 and branch 772->773 not run). The fake CLI always emits tool_result content as a string (tests/tools/fakes/fake_claude.py:62-64), so a list-shaped Grep or Read result is never exercised through `lines_shown`.",
      "severity": "medium"
    },
    {
      "evidence": ":891-892 `elif kind == \"-\" and self.new_path is None and self.old_path is not None: place = (self.old_path, self.old)`. :1651-1653 and :1667 add change.diff for away files. :1116-1117 'quotes a file that is not in the copy'.",
      "failure_scenario": "No failure. It is a mechanism with a test (`test_a_shown_removed_line_is_a_seen_line_only_of_a_file_the_change_deletes_at_its_old_line`) that keeps a rule no check uses, and readers may think a deleted file's quote is checked through it.",
      "file": "scripts/run_independent_review.py",
      "id": "F4",
      "kind": "simpler_alternative",
      "line": 891,
      "origin_stage": "implementation",
      "problem": "Mapping a removed line of a deleted file to its old path and line has no effect on any check. For a deleted file, `check_answers` and `_rejection_reads` put `_review_inputs/change.diff` into `must_read`, not the deleted path. `_quote_place_problem` refuses any quote of a file that is not in the copy. Deleted files are never paths under review. So `shown[<deleted path>]` is never read. The owner's option (b) named 'the old side for a deleted file', so dropping it would need the owner. It would remove one branch of `_DiffCursor.hunk_line` and one test.",
      "severity": "low"
    },
    {
      "evidence": ":1976-1977 `read = set(outcome.stats.get(\"paths_read\", []))` / `paths_not_read = [... if path not in read]`. `test_an_initial_review_that_saw_its_only_path_under_review_only_as_a_hunk_of_the_change_diff_completes` asserts `paths_read == ['_review_inputs/change.diff']` on a completed review.",
      "failure_scenario": "The owner reads an end entry whose `paths_not_read` lists every path under review, while the review completed because it saw them in change.diff. The diagnostic suggests a blind review that the check did not fail.",
      "file": "scripts/run_independent_review.py",
      "id": "F5",
      "kind": "defect",
      "line": 1977,
      "origin_stage": "implementation",
      "problem": "The end entry's `paths_not_read` still counts only successful Reads. Since R3-2, the checks judge a file by whether it was seen (Read window, content Grep, change.diff hunks). The record and attempt log can list a file as not read that the launcher's own checks counted as seen, and nothing says which definition applies.",
      "severity": "low"
    },
    {
      "evidence": ":877 `path = None if name == \"/dev/null\" else name[2:] if name.startswith((\"a/\", \"b/\")) else name`. :490 `git(repo, \"diff\", merge_base, commit, \"--\", \".\", *excludes)`.",
      "failure_scenario": "With `diff.noprefix=true`, or a non-ASCII file name that git writes as `\"b/\\303\\251.md\"`, a hunk maps to a path the copy does not hold. A recheck that saw the fix only in change.diff then fails 'was not seen'. This is a false failure, outside the delivery threat model's false greens.",
      "file": "scripts/run_independent_review.py",
      "id": "F6",
      "kind": "defect",
      "line": 877,
      "origin_stage": "implementation",
      "problem": "`diff_places` expects git's default diff format: `a/`/`b/` prefixes, unquoted names, no colour, no external diff driver. `change_diff` runs `git diff merge_base commit` under the author's git configuration, without `--no-ext-diff --no-color --src-prefix=a/ --dst-prefix=b/` and without `-c core.quotePath=false`.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to round-3/c1/r1/A/1

| Finding | Severity | Answer |
| --- | --- | --- |
| F1 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py, tests/tools/test_run_review_benchmark.py, docs/slices/agentic-sdlc-poc/slice_4_decisions.md, docs/history/implementation_log.md: asked, the owner decided "Rechecks only" (decision page, Decisions made, 2026-11-17); `lines_shown` maps `change.diff` lines to seen lines of their files only when the mode is recheck, and the mode travels in `Accounting` (`recheck_accounting` sets it for the launcher and the benchmark, `plan_reviews` sets the round's mode), so an initial or final review that saw its paths only as diff hunks fails the empty-review rule again (`test_an_initial_or_final_review_that_saw_its_only_path_under_review_only_as_a_hunk_of_the_change_diff_fails`, the test of `f75bc7a` turned round). `AGENTS.md` already states the rule inside the recheck paragraph only. Searched: every use of `lines_shown`, `diff_places` and `Accounting(` in `scripts/` and `tests/tools/`, and the diff-line wording in `AGENTS.md`, `docs/test_spec.md`, `docs/STATUS.md` and the checklists; no other place applies diff lines outside a recheck |
| F2 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py, docs/history/implementation_log.md: `invocation_from_entry` and the launcher both take a recheck's range from `earlier_commits` over every reviewer of the round (the entry's `round_reviewers`, the launcher's `spec.reviewers`), so a rebuild computes the launcher's range (`test_a_recheck_of_reviewers_who_reviewed_different_commits_is_rebuilt_from_its_entry_with_no_mismatch`). Searched: `main()` had the same cause, since a reviewer run again in the same round got the range of the reviewers being run rather than the round's, and the same change fixes it; `process_file_evidence` takes the same `since`; `check_review_records.py` (`_answers_problems`, `plan_recheck`, `_entry_recheck`) uses each reviewer's own earlier attempt, which is right there |
| F3 | medium | fixed: tests/tools/test_run_independent_review.py, docs/history/implementation_log.md: a test sends Read and content-Grep results whose content is a list of blocks (text blocks, a block without text, a part that is no block) and a content Grep of a path outside the copy, and asserts the lines shown (`test_a_tool_result_given_as_a_list_of_blocks_shows_the_lines_of_its_text_blocks`). Searched: a branch-coverage run of the launcher's tests found one more round-3 stream branch no test ran (`_grep_lines`, a path outside the copy), which the same test now runs; the other unrun branches near them are older than round 3 |
| F4 | low | rejected: the mapping of a deleted file's removed lines to its old path and line is part of the owner's decision concern 18, option (b) ("the old side for a deleted file", docs/slices/agentic-sdlc-poc/slice_4_decisions.md:672); removing it would change an approved choice, as the finding itself notes |
| F5 | low | rejected: `paths_read` and `paths_not_read` record the paths under review that the attempt opened with Read, as S42-D2 defines them and their names say (scripts/run_independent_review.py:1989); no check reads them, since the checks use the seen lines; and the benchmark keeps its own copy of the field and counts it as "Unread files" in every earlier result line (scripts/run_review_benchmark.py:783, scripts/run_review_benchmark.py:1396), so counting seen lines there would change what the recorded counts mean |
| F6 | low | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py, docs/slices/agentic-sdlc-poc/slice_4_decisions.md, docs/history/implementation_log.md: `change_diff` runs `git diff` with `--no-ext-diff --no-textconv --no-color --src-prefix=a/ --dst-prefix=b/`, `core.quotePath=false` and `diff.suppressBlankEmpty=false`, so the diff is in git's default format whatever the repository configures (`test_change_diff_has_git_default_format_whatever_the_repository_configures`); the 89 logged ranges give the same bytes as before, so no recorded hash changes. Searched: three places read git's file lists the same way (`changed_files`, `final_records`, `process_file_evidence`), a false refusal of a non-ASCII name rather than a false green, recorded as discovered issue 60 |

## Round 2

### Attempt round-3/c1/r2/A/1

Reviewer `A`: `claude-opus-5-5`, effort medium, mode recheck, commit `35dbead10e2d`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Recheck of round 3 of slice 4, review unit round-3

The intent is unchanged from round 1: the owner's approved round 3, the decision page
`docs/slices/agentic-sdlc-poc/slice_4_decisions.md`, section "Round 3: rechecks that look before they accept
(2026-11-17)", with the "Decisions made" rows of 2026-11-17 and decision concern 18, option (b). One owner decision is
new since round 1: asked about F1, the owner chose "Rechecks only" (the decision page, "Decisions made", 2026-11-17):
decision concern 18 (b) counts lines of `change.diff` as seen lines only in a recheck, as approved, and the author's
choice to apply it to every mode is reversed, so an initial or final review that saw its paths only as hunks of
`change.diff` fails the empty-review rule again.

Round 1's report and the author's answers to every one of its findings are below; the fixes are what the reviewed
commit adds after `af9ba98`, round 1's commit. Among them: the owner's decision on F1 recorded (`a6943e6`); F2, a
recheck's rebuild and a reviewer run again in the same round take the range from every reviewer of the round
(`1d728fd`); F3, a test of tool results given as a list of blocks (`06857a7`); F6, `change_diff` runs `git diff` in
git's default format (`8ec83b6`); F1, diff lines count as seen lines in rechecks only (`c105c9d`); and the answers with
the records of the fixes (`35dbead`). F4 and F5 are answered `rejected:`. This is the recheck of the unit `round-3`
(measurement 4 of the section), run by the launcher at the reviewed commit.

The author's claims to verify: each new test's first failure on the code before it is in the implementation log's
entry for this review (F3's test passed there, which the entry states); at `c105c9d`, `make lint` and `make qa-trace`
passed, and `make docs-check` and `make tooling-test` failed only on the round's missing answers, which the reviewed
commit's answers end; F6's change gives the same bytes for the 89 ranges the attempt logs record, so no recorded hash
changes; F6's search for the same cause found discovered issue 60.
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))
EV2: process file changed since the reviewed round: scripts/run_independent_review.py, +45 -25 lines (af9ba98cb1f8 to 35dbead10e2d; git diff --numstat --no-renames <earlier attempt's commit> <commit>)

Every changed line and branch run by the tooling tests: scripts/run_independent_review.py.
A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "F1",
      "note": "`lines_shown` adds diff lines only when the mode is recheck. `recheck_accounting` sets the mode to recheck, `plan_reviews` passes the round's mode, and `classify` defaults to initial. The benchmark's non-recheck cases pass no accounting, so they take the initial mode, which matches the owner's 'Rechecks only'. The test was turned round and parametrised for initial and final. The owner's decision is recorded in the Decisions made table. One remnant: row 18 of the discovered-issues table (:672) still says 'for every mode by the author's choice'. It is a done-history note, and the As built text at :579-583 states the reversal, so I raise no finding.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py",
        "tests/tools/test_run_review_benchmark.py",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
        "docs/history/implementation_log.md",
        "scripts/run_review_benchmark.py",
        "_review_inputs/change.diff"
      ],
      "quotes": [
        {
          "end_line": 848,
          "file": "scripts/run_independent_review.py",
          "line": 848,
          "text": "    return _with_diff_lines(shown, copy_root) if mode == \"recheck\" else shown"
        },
        {
          "end_line": 1630,
          "file": "scripts/run_independent_review.py",
          "line": 1630,
          "text": "    return Accounting(items, must_read, quoted, \"recheck\")"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "F2",
      "note": "`invocation_from_entry` now calls `earlier_commits` over the entry's `round_reviewers`. That field is required on every start entry, since `_round_state` reads it. `main` passes every reviewer of the round, and `admit_round` already makes them equal to the round's reviewers. A new test rebuilds both rechecks of reviewers who reviewed different commits and asserts no mismatch.",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py",
        "_review_inputs/change.diff"
      ],
      "quotes": [
        {
          "end_line": 2223,
          "file": "scripts/run_independent_review.py",
          "line": 2223,
          "text": "                                list(entry[\"round_reviewers\"]))"
        },
        {
          "end_line": 2267,
          "file": "scripts/run_independent_review.py",
          "line": 2267,
          "text": "                                    [r.label for r in spec.reviewers])"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "F3",
      "note": "The new test sends Read and Grep results whose content is a list of blocks: text blocks, an image block and a part that is no block. It also runs a content Grep outside the copy, and it asserts the exact lines shown. The implementation log says the test passed on the earlier code, by design.",
      "opened": [
        "tests/tools/test_run_independent_review.py",
        "docs/history/implementation_log.md",
        "_review_inputs/change.diff"
      ],
      "quotes": [
        {
          "end_line": 1928,
          "file": "tests/tools/test_run_independent_review.py",
          "line": 1928,
          "text": "    shown = launcher.lines_shown(launcher.parse_stream(\"\\n\".join(lines)), root, \"initial\")"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "F4",
      "note": "The rejection holds. The old-side mapping for a deleted file is written into option (b), which the owner chose, and my finding was only a simpler alternative that needs the owner.",
      "opened": [
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "quotes": [
        {
          "end_line": 672,
          "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
          "line": 672,
          "text": "| 18 | Decision concern, decided, done | Round 3 | The replay of 4.5's `mechanics` round 2 failed the new recheck on two causes. (1) M4's `fixed:` answer names seven files; the reviewer read three and saw the other four (`PB-2.patch`, `RC-1.patch`, `DC-1.patch` and `RM-6.patch` of `tests/review_benchmark/plants/`) only as their hunks in `change.diff` (lines 898 to 1015, within the lines 1 to 1099 it read), which under R3-1 holds exactly the fix; the rule that every file an answer names must be seen (kept from before R3-2, where it said \"read\") fails it. The original retry passed because its reviewer read all six patches. (2) L1's quote of `docs/slices/README.md:21` carries 2026-11-09, the date the author's answer gives for the decision file, where the file says 2026-11-08; the acceptance was right, the quote false, and the quote check failed it as R3-2 means it to, the first live case. So measurement 2's criterion is not met, and the stop rule says the results are reported, not tuned on this branch | Options: (a) keep R3-2 as built and close slice 4 by the stop rule, carrying (b) to the next slice's plan; (b) count the lines a recheck read in `change.diff` as seen lines of the files they belong to (each hunk's new-side line numbers; the old side for a deleted file), so a fix seen in the diff counts as seen, while a quote still names the file and its text must be at that place; then replay `mechanics` once more (about USD 1.7) and report whatever it shows (L1's misquote may fail it again); this changes R3-2's approved \"seen\" and the stop rule, so it is the owner's; (c) report a misquote instead of failing the attempt: not recommended, since a quote is the evidence an acceptance rests on. Recommendation: (b), because R3-1 made the diff the fix itself, so the diff is where a recheck looks, and each such look would otherwise cost a failed session; it changes a choice (what \"seen\" covers) and adds no mechanism. Decided by the owner on 2026-11-17: (b), the author's recommendation (\"I choose your recommendation\"); the `mechanics` replay runs once more after it is built. Done: (b) built (`04a0ae3` tests first, `753fc3e`, `5627de7`; section \"Round 3\", As built), for every mode by the author's choice; the `mechanics` replay ran once more and passed the new recheck (completed, approvable; 15 accepted, H1 re-raised), and on that attempt the earlier check still fails M4 while the new one does not (section \"Round 3\", measurement 2) |"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "F5",
      "note": "The rejection holds. `paths_not_read` is the S42-D2 diagnostic of Reads, and no check reads it. The benchmark's 'Unread files' counts depend on what the field means now. The finding was low.",
      "opened": [
        "scripts/run_independent_review.py",
        "scripts/run_review_benchmark.py"
      ],
      "quotes": [
        {
          "end_line": 1989,
          "file": "scripts/run_independent_review.py",
          "line": 1989,
          "text": "        outcome.stats[\"paths_not_read\"] = [path for path in ctx.inputs.review_paths if path not in read]  # S42-D2"
        },
        {
          "end_line": 1396,
          "file": "scripts/run_review_benchmark.py",
          "line": 1396,
          "text": "    c.unread_files += len(stats.get(\"paths_not_read\", []))"
        }
      ],
      "status": "accepted"
    },
    {
      "item": "F6",
      "note": "`change_diff` now pins git's default format with flags and `-c` settings. The new test sets every conflicting configuration and asserts the same bytes and the same places, a non-ASCII name included. I cannot verify the claim that the 89 logged ranges give the same bytes, because the copy has no git metadata. The same-cause search missed `changed_lines` in review_inputs.py, raised as N1 (low).",
      "opened": [
        "scripts/run_independent_review.py",
        "tests/tools/test_run_independent_review.py",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
        "docs/history/implementation_log.md",
        "scripts/review_inputs.py",
        "_review_inputs/change.diff"
      ],
      "quotes": [
        {
          "end_line": 494,
          "file": "scripts/run_independent_review.py",
          "line": 494,
          "text": "    return git(repo, \"diff\", \"--no-ext-diff\", \"--no-textconv\", \"--no-color\", \"--src-prefix=a/\", \"--dst-prefix=b/\","
        }
      ],
      "status": "accepted"
    },
    {
      "item": "EV1",
      "note": "This commit has no CI run, because the branch is not pushed. The local gate runs in the implementation log are a diagnosis only. CI must still run on the PR. Disclosed, so no finding.",
      "opened": [
        "docs/history/implementation_log.md"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "I reviewed the process-file change to run_independent_review.py in full through change.diff: the mode in Accounting, the `git` config parameter, `change_diff` flags, and `earlier_commits` over the round's reviewers. The evidence says every changed line and branch is run by the tooling tests. The only problem I found is N1, in a neighbouring file.",
      "opened": [
        "scripts/run_independent_review.py",
        "_review_inputs/change.diff"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "review_inputs.py:335 `for line in _git(repo, \"diff\", \"-U0\", merge_base, commit, \"--\", path).splitlines():`, then `HUNK.match(line)`. run_independent_review.py:494 now passes `--no-ext-diff --no-textconv --no-color --src-prefix=a/ --dst-prefix=b/` for `change_diff` only. The F6 answer's 'Searched' names `changed_files`, `final_records` and `process_file_evidence`, not `changed_lines`.",
      "failure_scenario": "An author's git sets `diff.external` or `color.diff=always`. The hunk headers then do not match `HUNK`, so `changed_lines` returns an empty set. The evidence line 'Every changed line and branch run by the tooling tests' could then be vacuously true. This needs an unusual local git configuration, so it is low. The fix is to pass the same flags as `change_diff`, or to record it with issue 60.",
      "file": "scripts/review_inputs.py",
      "id": "N1",
      "kind": "defect",
      "line": 335,
      "origin_stage": "implementation",
      "problem": "F6's search for the same cause missed one place. `changed_lines` parses hunk headers from `git diff -U0 merge_base commit -- path` under the repository's own git configuration, with no `--no-ext-diff`, `--no-color` or `core.quotePath=false`. That is the cause F6 fixed in `change_diff`. The author's search listed only the three readers of git file lists (issue 60).",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to round-3/c1/r2/A/1

| Finding | Severity | Answer |
| --- | --- | --- |
| N1 | low | fixed: scripts/review_inputs.py, scripts/run_independent_review.py, tests/tools/test_review_inputs.py, docs/history/implementation_log.md: git's default diff format is defined once in `review_inputs` (`DEFAULT_DIFF_OPTIONS` with F6's flags, `DEFAULT_DIFF_CONFIG` with its `-c` settings), its `_git` takes `config=` as the launcher's `git` does, and both `changed_lines` and `change_diff` use that definition (`test_changed_lines_reads_git_default_format_whatever_the_repository_configures`); `change_diff`'s git arguments are unchanged, and every distinct range of the attempt logs (78, recounted for this fix; F6's answer said 89, counted another way) gives the same bytes as before. Searched: every `git diff`, `git show` and `git log` call in `scripts/`; only `changed_lines` and `change_diff` parse diff hunks; the places that read git's file lists stay discovered issue 60 |
