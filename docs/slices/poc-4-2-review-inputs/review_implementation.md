# Implementation review — 4.2 (#39), review inputs and evidence

Record of the implementation review of slice 4.2 in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- The task prompt of round 1 holds the author's self-review: seven questions the owner asked, answered with evidence, given to the reviewer as claims to verify.
- The launcher of the reviewed branch ran these reviews (slice 4.1's prompt sections, modes and `accounted`); a recheck lists each answer under `accounted`.

## Round 1

### Attempt implementation/c1/r1/A/1

Commit `d2d8616`, effort high. Files reviewed (SHA-256): `AGENTS.md` `5306f1ec5801`, `docs/STATUS.md` `2edc6846e09a`, `docs/slices/README.md` `815cc538ac93`, `docs/slices/_template/test_plan.md` `b1b8a55b4802`, `docs/slices/agentic-sdlc-poc/slice_4_decisions.md` `520bde326c4e`, `docs/slices/poc-4-1-review-prompts/review_attempts.jsonl` `d8142117691a`, `docs/slices/poc-4-1-review-prompts/review_implementation.md` `c6f56911004a`, `scripts/review_evidence.py` `0aaef3d19e33`, `scripts/run_independent_review.py` `23da72461fd9`, `scripts/run_review_benchmark.py` `bc460a1f9173`, `tests/tools/fakes/fake_claude.py` `fca2c0f7f258`, `tests/tools/test_review_evidence.py` `b2f50e72b957`, `tests/tools/test_run_independent_review.py` `f78d0034f26d`, `tests/tools/test_run_review_benchmark.py` `579a5e6bc4bf`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Implementation review of slice 4.2 (review inputs and evidence computed by tools, issue #39)

## Intent

The approved plan and test plan are `docs/slices/poc-4-2-review-inputs/plan.md` (decisions S42-D1 to S42-D11)
and `docs/slices/poc-4-2-review-inputs/test_plan.md`, merged into `poc/agentic-sdlc` by plan PR #48 (the base of this
review). Slice 4 is one branch with six sub-issues; 4.1 (prompt sections, modes, recheck inputs, severity) was
implemented and reviewed before this one, and its review record is `docs/slices/poc-4-1-review-prompts/review_implementation.md`.
4.2 fills two of 4.1's sections (upstream items, evidence) and replaces the author's file list with the diff. 4.3 will
write the evidence into the review record verbatim (S42-D9's second half) and move the recheck's earlier report into
the record.

The change from the base is in `_review_inputs/change.diff`; it holds 4.1 too. The commits of 4.2 start at
`381dc2b`. The new module is `scripts/review_evidence.py`; the launcher loads it as it loads the secret check.

## The author's self-review (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.**
   - CI API: `curl` of `GET /repos/gunaseelan-sivanandam/agentic-iam-spiffe/actions/runs?head_sha=3347754…` returned
     200 with `total_count` 0; the unfiltered list showed that CI runs on pull requests and on pushes to `main`, not
     on pushes to `poc/agentic-sdlc`. `GET …/actions/runs/42677963330/jobs` returned 200 with 12 jobs, each with
     `status` and `conclusion`. No token was sent.
   - Where the interpreter finds pytest: `python3 -c "import pytest; print(pytest.__file__)"` shows the user site
     under the author's HOME (`~/.local/lib/python3.10/site-packages`); with a scratch HOME, `python3 -m pytest`
     printed "No module named pytest". So the scratch HOME links `.local` to `site.getuserbase()`, and the environment
     stays PATH, LANG and HOME (S42-D8).
   - Where the tooling tests can run: in a `git archive` export with a minimal PATH, 38 tests failed (they need Git
     history and `ruff`, which is in `~/.local/bin`); in a `git clone --shared` checkout with the author's PATH,
     505 passed in about 80 seconds. The evidence therefore runs in a shared clone with the author's PATH.
   - The trace tool needs `services/` and `tests/unit/` to exist and imports `scripts/qa_deploy.py`; found while
     building the test repository.
   - The tooling tests make no network calls (`grep` for `api.github.com` and `urlopen` in `tests/tools/` finds
     none; the gate-consistency test uses a fake ruleset).
2. **Each check added or changed, the case it catches, and its test.** In `tests/tools/test_review_evidence.py`
   unless named otherwise.
   - Files from the diff, deleted apart, withheld never listed: `test_files_come_from_the_diff_and_deleted_files_are_listed_apart`.
   - `--path` orders and never narrows; a hint outside the files to open is refused; a hint naming a deleted file is
     refused: `test_path_hints_come_first_and_never_narrow_the_list`,
     `test_a_path_hint_outside_the_files_to_open_is_refused_before_any_call`, `test_path_hint_naming_a_deleted_file_is_refused`.
   - The empty-review rule on hint files: `test_review_that_opened_none_of_the_hint_files_fails_even_when_it_opened_other_listed_files`
     (its last step, without `--path`, is the twin).
   - Upstream items (governing plan with decisions, other bundles' plans, `Implemented by:` and DD links, edited
     requirement sections and test entries): the two `test_upstream_names_…` tests; the question in every prompt:
     `test_every_prompt_holds_the_upstream_question`.
   - Uncovered changed lines and branches, the #44 note, the service gate line:
     `test_uncovered_changed_branch_is_listed_with_the_subprocess_note_and_a_service_gate_line`.
   - Trace gaps marked new or existing: `test_trace_gap_among_the_upstream_items_is_marked_new_or_existing`.
   - CI: a running job never shows a pass, another commit's run is never shown, no run says so, an unreadable API
     and a missing GitHub origin are failed: the three `ci` tests.
   - Every evidence entry accounted, `flagged` naming a finding: `test_report_must_account_for_every_evidence_entry`,
     `test_flagged_evidence_entry_naming_no_finding_of_the_report_fails`.
   - Failures shown as failed (failing tests named, coverage or trace that cannot run, commands that raise):
     `test_failing_tests_are_named_…`, `test_coverage_that_cannot_run_is_shown_as_failed`,
     `test_trace_model_that_cannot_run_is_shown_as_failed`, `test_coverage_and_trace_commands_that_raise_are_shown_as_failed`.
   - Clean environment and the path check: `test_evidence_commands_see_only_path_lang_and_a_scratch_home` (a probe
     test inside the evidence run), `test_sanitise_…`, `test_leak_check_in_compute_evidence_refuses`,
     `test_evidence_still_holding_a_local_path_is_refused_before_any_call`.
   - Evidence hash, required `diff_base`, rebuild with changed evidence: the last tests of the file.
   - Benchmark inputs (S42-D11): two tests at the end of `tests/tools/test_run_review_benchmark.py`.
3. **Claims and what checks them mechanically.** "The evidence comes from the reviewed commit, not the working
   tree": `test_uncommitted_edit_does_not_change_the_evidence`. "No absolute local path reaches a prompt":
   `leaked_paths`, refused before any call, with the tests above; in the dry runs below the prompts held no `/home/`
   or `/tmp/` string. "The CI call uses no token": `test_fetch_json_reads_json_without_a_token` serves the request
   locally with `GITHUB_TOKEN` set and finds no `Authorization` header. "The trace gaps are among the upstream items
   only": the IDs come from `Upstream.ids`. Not mechanical: whether a reviewer's `explained` note is sound.
4. **Fixes and their upstream choice.** No reviewer findings yet. Found by the author: a test that passed only when
   the repository's origin is GitHub (it failed inside the evidence clone; the test now injects the origin); the
   template and archive folders listed as bundles (the definition of a bundle now leaves them out); a scratch
   directory left behind when its clone or checkout fails (it is now removed there).
5. **Tried the way the next user runs it.** In a scratch clone of this repository at the branch, with the real base
   fetched, the real CI API and the fake CLI: a full round took about 80 seconds, almost all of it the tooling tests.
   Its evidence listed 29 changed lines of the new code that no test ran; the author then added tests until only the
   lines in 7 below remained. Two units of different bundles then ran in parallel (108 seconds): each got its own
   governing plan and its own scratch, and both evidence sections were the same. When the launcher ran without
   shellcheck on PATH, the evidence named the failing lint tests, so the evidence reflects the author's environment.
6. **Where each rule lives.** `AGENTS.md`, Independent review, "What the reviewer receives"; the module docstring;
   the tests above. Decisions made on the owner's behalf are in the decision file.
7. **What was removed, and its review.** The author-chosen `--path` list as the scope (now hints); `--path` is no
   longer required; `has_diff` and the optional `diff_base` of `make_frozen_copy`, `build_prompt` and
   `invocation_from_entry` (S42-D10, with a test that each raises `TypeError` without it). Left untested on purpose:
   the launcher's check that a script module cannot be loaded (`spec_from_file_location` never returns None for a
   `.py` path; kept from slice 2), a rename of a withheld file, and a user site base that is not a directory.

## Questions (a minimum, from the test plan)

1. *Tests:* for each new or changed test, which wrong behaviour would still pass it?
2. *Keys:* does a key, socket or secret now reach a service outside its holders? Can the evidence or the upstream
   list carry a secret or an operational detail (a local path, an account) into a prompt or a public record?
3. *Names and headers:* do new names and files say what they do?

Also: does every decision S42-D1 to S42-D11 have its implementation and proof, and does the change do anything no
decision asked for?
```

#### Report

```json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "Branch 181->179 (a DD tag outside the changed files is never skipped in a test) is raised as R1-3. Branch 84->86 (rename of a withheld file) is harmless: line 92 filters withheld paths again, which makes the check redundant (R1-9). Branch 264->269 (user base not a directory) is a benign skip of the `.local` link; the link itself is part of R1-6.",
      "opened": [
        "scripts/review_evidence.py",
        "tests/tools/test_review_evidence.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV2",
      "note": "Line 163 is the RuntimeError raised when spec_from_file_location returns None or a spec without a loader. For a `.py` path under scripts/ it always returns a SourceFileLoader spec, so the line is unreachable in practice, and it fails closed (an import-time error) if ever hit. It was kept from slice 2, as the self-review says.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Expected. Slice 4 runs locally until the owner pushes at the end (decision file, Goal), and CI runs on pull requests and on pushes to main, not on pushes to poc/agentic-sdlc. So the reviewed commit has no CI run, and the entry correctly says so instead of showing another commit's run. No CI verdict backs this review; R1-2 covers the untested display of completed jobs.",
      "opened": [
        "_review_inputs/change.diff",
        "docs/slices/agentic-sdlc-poc/slice_4_decisions.md"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "scripts/review_evidence.py:378-383 reads `gap_gate.accepted` and checks it before `new_gaps`. test_trace_gap_among_the_upstream_items_is_marked_new_or_existing tests only `existing` and `new`. Nothing exercises an `accepted_gaps` entry, either through the real trace tool or with a hand-built report.",
      "failure_scenario": "Suppose a later edit reads the wrong key (for example `gate.get(\"accepted_gaps\")`, which holds dicts, not gap IDs) or drops the accepted branch. Every accepted gap would then show as \"new\", and all tests still pass. Reviewers would flag gaps the owner has already accepted and push the author into needless fixes. If instead the mark were inverted for accepted gaps only, nothing would catch it either.",
      "file": "tests/tools/test_review_evidence.py",
      "id": "R1-1",
      "kind": "defect",
      "line": 253,
      "origin_stage": "tests first",
      "problem": "Trace gaps marked \"accepted\" have no test. S42-D5(b) and the approved test-plan row \"Trace gaps\" say each gap is marked new, existing or accepted. Searched test_review_evidence.py, test_run_independent_review.py and test_run_review_benchmark.py for 'accepted, against', 'accepted_gaps' entries and gap_gate fixtures. The only fixture has `accepted_gaps: []`, and the one direct trace_evidence call passes `gap_gate: {}`.",
      "severity": "high"
    },
    {
      "evidence": "scripts/review_evidence.py:427-431 appends `/conclusion` only when status is `completed`. The fake jobs response at test_review_evidence.py:279 always returns `in_progress`. No assertion checks text such as `lint: completed/failure`.",
      "failure_scenario": "A regression drops the conclusion, or shows the run's conclusion instead of the job's. A run whose `e2e` job failed then appears as `e2e: completed`, or as `completed/success` at run level. The reviewer marks the CI entry `explained` as 'CI completed', which is a false green on exactly the evidence S42-D5 added. Every current test still passes.",
      "file": "tests/tools/test_review_evidence.py",
      "id": "R1-2",
      "kind": "defect",
      "line": 265,
      "origin_stage": "tests first",
      "problem": "No test shows a completed CI job with its conclusion. S42-D5(c) and the test-plan row \"CI results\" say each job is shown \"with status and conclusion\". The parametrised CI test covers only an in-progress job and the no-run case. The only completed run in the test is another commit's, so it is filtered out. Searched tests/tools for 'conclusion', 'completed/' and 'failure'.",
      "severity": "high"
    },
    {
      "evidence": "EV1 lists branch 181->179 as not taken, i.e. `if where:` in trace_links is never false. That branch is not among the untested items the self-review lists in point 7. In test_trace_gap_among_the_upstream_items_is_marked_new_or_existing, REQ-T-R2 and REQ-T-R3 are both satisfied by ARCH-001, which is upstream, so the `item in ids` filter at review_evidence.py:380 never removes anything.",
      "failure_scenario": "A refactor drops the `if where:` or `item in ids` condition. On this repository (131 DDs and many existing gaps), every DD and every gap would then flood the upstream and evidence sections. Each gap becomes an EV entry the reviewer must account for, which buries the real one. All tests still pass.",
      "file": "tests/tools/test_review_evidence.py",
      "id": "R1-3",
      "kind": "defect",
      "line": 200,
      "origin_stage": "tests first",
      "problem": "No test checks that the upstream items and trace gaps leave out what is unrelated to the change. Every fixture has only upstream-relevant items: one ARCH, whose Implemented-by file is the changed file, and no DD outside a changed file. Every gap sits on an upstream ID. The author's claim 3 ('the trace gaps are among the upstream items only') and claim 5 (only the lines in 7 stay untested) do not hold for these branches. Searched the upstream and trace-gap tests for a DD or gap outside the change.",
      "severity": "medium"
    },
    {
      "evidence": "docs/slices/poc-4-1-review-prompts/review_attempts.jsonl:13 (and the other 4.1 implementation start entries) has `\"mode\": \"initial\"` and no `path_hints`. run_independent_review.py:1558 refuses only when `mode` is missing; line 1566 then reads `entry[\"path_hints\"]`.",
      "failure_scenario": "At 4.3, or at the owner's end review, someone rebuilds a 4.1 implementation attempt to check what the reviewer got. They get a bare `KeyError: 'path_hints'` instead of the 4.1-style message that the layout is retired and only the hashes identify the review. Even with a default added, the rebuilt prompt would differ silently, because the files now come from the diff.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-4",
      "kind": "defect",
      "line": 1566,
      "origin_stage": "architecture and interfaces",
      "problem": "invocation_from_entry crashes with KeyError on attempts logged by 4.1's launcher. Those entries have `mode` but no `path_hints`, `upstream_sha256` or `evidence_sha256`. 4.1 decided that a retired layout is refused with a clear message, and 4.2 retires 4.1's layout (file list from --path, placeholder upstream and evidence sections) without extending that refusal. The problem starts upstream: the 'Retirement and compatibility' section of docs/slices/poc-4-2-review-inputs/plan.md does not mention rebuilding 4.1-era entries. Searched test_run_independent_review.py: only the pre-4.1 case (no `mode`) is tested, at line 1193.",
      "severity": "medium"
    },
    {
      "evidence": "review_evidence.py:160-162: `yaml.safe_load(text or \"\") or {}` followed by `data.get(\"tests\")`. run_independent_review.py:1303 has `except ValueError`, and main() catches only ReviewRefusedError.",
      "failure_scenario": "An author's change has a YAML indentation error in trace/tests.yaml, which is exactly the kind of change that needs review. The launcher dies with a Python traceback, not 'REFUSED: \u2026' or an EV entry 'failed: \u2026'. No reviewer call is made (fail-closed), but the cause is unclear, and S42-D7's 'never pretends, shown as failed' does not hold for upstream computation.",
      "file": "scripts/run_independent_review.py",
      "id": "R1-5",
      "kind": "defect",
      "line": 1303,
      "origin_stage": "implementation",
      "problem": "compute_evidence catches only ValueError. upstream_items calls changed_tests, which calls yaml.safe_load on trace/tests.yaml at both commits. yaml.YAMLError is not a ValueError, and a non-mapping document raises AttributeError at `data.get`. A change that breaks the YAML of trace/tests.yaml therefore crashes the launcher with a traceback (exit 1). S42-D7 asks for a 'failed' entry, or else a clean refusal. The trace tool itself catches yaml.YAMLError and is shown as failed, but changed_tests runs regardless. Searched the tests for a malformed tests.yaml case: none.",
      "severity": "medium"
    },
    {
      "evidence": "review_evidence.py:263-265 links `home/.local` to `site.getuserbase()`. review_evidence.py:98-99 refuses deleted hints. slice_4_decisions.md:92-104 lists 4.1 rows only, and Progress says '4.2 | In progress'.",
      "failure_scenario": "At the end review the owner reads the decision file as the complete list of choices made for them. They never learn that the 'scratch HOME' sees their whole ~/.local, so evidence can depend on user-site plugins and differ from a truly clean run. The record also never shows that S42-D8 was interpreted rather than implemented as written.",
      "file": "docs/slices/agentic-sdlc-poc/slice_4_decisions.md",
      "id": "R1-6",
      "kind": "defect",
      "line": 92,
      "origin_stage": "implementation",
      "problem": "Self-review claim 6 says 'Decisions made on the owner's behalf are in the decision file', but the file's 'Decided by the author during the run' table has only 4.1 rows. The owner reviews only this page at the end, and 4.2 made several choices on the owner's behalf that are recorded nowhere. (1) The scratch HOME gets a `.local` symlink to the author's real user base (`site.getuserbase()`, the whole ~/.local tree), so the 'clean environment' of S42-D8 ('only PATH, LANG and a scratch HOME') exposes the author's user packages and data. (2) A `--path` naming a deleted file is refused, although S42-D1 only requires it to be in the diff. (3) `_template` and `archive` are excluded from bundles. (4) Evidence runs in a `git clone --shared` with the author's PATH. Searched slice_4_decisions.md (Decided by the author, Decision concerns, Discovered issues) and plan.md (Environment facts).",
      "severity": "high"
    },
    {
      "evidence": "docs/slices/README.md:17-18. AGENTS.md step 4 asks for the slice's row to be updated.",
      "failure_scenario": "A reader of the index takes 4.2 to be still at plan stage while its code is on the branch.",
      "file": "docs/slices/README.md",
      "id": "R1-7",
      "kind": "defect",
      "line": 18,
      "origin_stage": "implementation",
      "problem": "The slice index row for poc-4-2-review-inputs still says 'Plan under review (slice 4 plan PR)', although the plan merged in PR #48 and 4.2 is now implemented and in review. In the same change, 4.1's row was updated to 'Plan merged (PR #48); implemented \u2026 in review'.",
      "severity": "low"
    },
    {
      "evidence": "run_independent_review.py:17-20 versus line 1494 (`default=[]`, 'only orders the files').",
      "failure_scenario": "An author following the usage line keeps treating --path as the scope of the review, which is the habit S42-D1 retires (DPL-005).",
      "file": "scripts/run_independent_review.py",
      "id": "R1-8",
      "kind": "defect",
      "line": 20,
      "origin_stage": "implementation",
      "problem": "The module docstring's usage line still shows `--path <file under review> [--path ...]` as a required argument naming the files under review. After S42-D1, `--path` is optional and only orders the list.",
      "severity": "low"
    },
    {
      "evidence": "review_evidence.py:83-92. run_independent_review.py:1139-1147 and 1332.",
      "failure_scenario": "There is no failure. Two sources of 'what the change deletes' can drift apart; using inputs.deleted for the recheck and removing the redundant check leaves one.",
      "file": "scripts/review_evidence.py",
      "id": "R1-9",
      "kind": "simpler_alternative",
      "line": 84,
      "origin_stage": "implementation",
      "problem": "Two pieces of the file-list logic are redundant. (a) The `if deleted_path not in withheld` check in changed_files duplicates the withheld filter that line 92 applies to `deleted` anyway; this is the never-taken branch 84->86 in EV1. (b) changed_away in run_independent_review.py:1139 runs a second `git diff --name-status -M` to find deleted and renamed-away paths, which changed_files already computes as `ChangedFiles.deleted` (rename sources included) and which ReviewInputs carries as `inputs.deleted`.",
      "severity": "low"
    },
    {
      "evidence": "review_evidence.py:1-10. run_independent_review.py:171 (`_INPUTS = _load_script(\"review_evidence\")`) and 1278-1283.",
      "failure_scenario": "A maintainer looking for the diff-based file list or the upstream logic does not look in a module named 'evidence', and adds a parallel implementation.",
      "file": "scripts/review_evidence.py",
      "id": "R1-10",
      "kind": "defect",
      "line": 1,
      "origin_stage": "implementation",
      "problem": "The new module's name says less than it does (test-plan question 3). It is called review_evidence, but it also computes the files under review and the upstream items; its own docstring calls it 'Review inputs computed by tools', and the launcher binds it as `_INPUTS`. Likewise, `_sanitised_upstream` returns a 3-tuple that includes the trace report and its failure reason, not only the upstream text.",
      "severity": "medium"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to implementation/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| R1-1 | high | fixed: tests/tools/test_review_inputs.py: `test_accepted_trace_gap_is_marked_accepted` adds an `accepted_gaps` entry for the existing gap and runs the real trace tool; the gap is marked accepted. With the accepted branch removed from `trace_evidence`, this test fails (the author's hand mutation). Searched for other marks without a test: new and existing have one each |
| R1-2 | high | fixed: tests/tools/test_review_inputs.py: `test_completed_ci_job_shows_its_own_conclusion` checks a completed run with a successful job, a failed job and a queued job, and asserts each job's own conclusion; with the job conclusion removed, it fails (hand mutation). Searched for other CI text without a test: the run line's conclusion is asserted in the same test |
| R1-3 | medium | fixed: tests/tools/test_review_inputs.py: `test_items_unrelated_to_the_change_stay_out_of_upstream_and_evidence` adds an architecture item, a DD tag and an unproved requirement that the change does not touch; none appears in the upstream or evidence sections. Removing either the `item in ids` filter or the `if where:` condition makes it fail (hand mutations) |
| R1-4 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_review_inputs.py: `invocation_from_entry` refuses an entry without `path_hints` (logged by 4.1's launcher) with the same message as for entries before 4.1, naming 4.2; the retirement is recorded in the decision file. Test: `test_rebuild_of_an_entry_logged_by_4_1s_launcher_says_its_layout_is_retired` |
| R1-5 | medium | fixed: scripts/review_inputs.py, tests/tools/test_review_inputs.py: reading `trace/tests.yaml` for the upstream items raises a ValueError on invalid YAML or a document that is not a mapping, and the upstream section then says the entries are not available; the trace tool's own failure is already an evidence entry. Cause: the parser assumed a valid mapping; searched the module for other `yaml.safe_load` calls: this was the only one. Test: `test_unreadable_trace_tests_yaml_is_shown_not_a_crash` (two cases) |
| R1-6 | high | fixed: scripts/review_inputs.py, docs/slices/agentic-sdlc-poc/slice_4_decisions.md, AGENTS.md, tests/tools/test_review_inputs.py: the scratch HOME now links only the interpreter's user site-packages directory, not the whole `~/.local`, and `AGENTS.md` says so; the decision file records the 4.2 choices made on the owner's behalf (the module, the shared clone with the author's PATH, the site-packages link, refusing a deleted `--path`, leaving out template and archive folders, EV numbering, refusing 4.1-era rebuilds). Test: `test_scratch_home_links_only_the_user_site_packages` |
| R1-7 | low | fixed: docs/slices/README.md: the 4.2 row says the plan merged and the implementation is in review |
| R1-8 | low | fixed: scripts/run_independent_review.py: the usage line shows `--path` as optional and says what it does |
| R1-9 | low | fixed: scripts/review_inputs.py, scripts/run_independent_review.py: the redundant withheld check is gone, and the recheck's check of `fixed:` paths uses the change's deleted files from the review inputs; `changed_away` and its second `git diff` are removed |
| R1-10 | medium | fixed: scripts/review_inputs.py, tests/tools/test_review_inputs.py, scripts/run_independent_review.py: the module is renamed `review_inputs` (with its tests), and the helper `_upstream_and_trace` says that it returns the trace report too |
