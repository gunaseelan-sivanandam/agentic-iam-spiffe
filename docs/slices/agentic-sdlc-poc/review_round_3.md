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

