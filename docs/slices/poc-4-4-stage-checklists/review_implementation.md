# Review record — poc-4-4-stage-checklists, unit `implementation`

The record of the review unit `implementation`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt implementation/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `b8b129601c6e`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Implementation review of slice 4.4 (stage checklists, issue #41)

## Intent

The approved plan and test plan are `docs/slices/poc-4-4-stage-checklists/plan.md` (decisions S44-D1 to S44-D13)
and `test_plan.md`, merged into `poc/agentic-sdlc` by plan PR #48 (the base of this review). Slice 4.4 researches
established review practice per artifact type and writes, for each of six types, a short list of questions with what
blocks at that stage (`docs/review_checklists/`); the research, the DPL mapping and the drafts of the three review
mandates are in `research.md` of the bundle; the launcher gains `--stage`. Two models critiqued the drafts as the
plan's critique unit (S44-D10); their findings and the author's answers are in `review_critique.md` of the bundle,
and the lists and drafts were revised from them. S44-D10 says the fixes to the critique's blocking findings are
rechecked here: the blocking one was C-1 (the draft recheck mandate). The reviewed commit also holds slices 4.1 to
4.3 and 4.5's first part, each reviewed in its own unit; 4.4's commits are `1750c8d`, `0e0a201` and `b8b1296`.

## The author's self-review of slice 4.4 (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.**
   - The sources: every page `research.md` quotes was read on 2026-11-09 with a web-fetch tool; its Method section
     says how quotes were taken. Three sources could not be read and give no item: SEI CERT's page (the connection
     was reset on four attempts), INCOSE's summary sheet (HTTP 403; the guide itself is sold) and the ISTQB syllabus
     (a PDF no available tool could read); each section says so. Three paid standards (ISO/IEC/IEEE 29148, IEEE 1028, IEEE 1044) are cited by title only, and
     NASA's public checklist and ReqView's public 29148 templates stand in for the requirements sources. After the
     critique, five more quotes were fetched on 2026-11-10 (Google's functionality and documentation items, Fowler's
     quarantine and clock sections, the test pyramid's fake-server section, OWASP's threat model kept alongside the
     system); each new question rests on one of them.
   - The base has no lists: `git ls-tree -r --name-only origin/poc/agentic-sdlc docs/review_checklists` prints
     nothing, so every review of slice 4 runs with "No checklist at base <commit>", as S44-D7 says.
   - Reviewers have no web access (the launcher offers only Read, Grep and Glob), so every quote a list rests on is
     in `research.md` itself.
2. **Each check added or changed, the case it catches, and its test** (in `tests/tools/test_stage_checklists.py`).
   - A list without a title and purpose, with more than 12 questions, with an untagged question, a tag that names no
     source section or a source that gave nothing (unread, unreachable, or title only), a question that is not
     numbered, a DPL entry as a source, or no "Blocks at this stage" section:
     `test_every_list_has_the_agreed_form_and_cites_researched_sources`, and one negative case per kind in
     `test_the_form_check_fails_on_each_kind_of_violation`.
   - A list for a type the plan does not name, or a final-review or handoff list: `test_exactly_the_six_artifact_types_have_a_list`.
   - The two questions for what is missing in the wrong lists: `test_the_two_questions_for_what_is_missing_sit_where_the_misses_happen`.
   - A coding rule repeated in the code list: `test_the_code_list_repeats_no_coding_rule` (five phrases only).
   - A planned source without a section, or a paid standard not marked title only:
     `test_the_research_record_has_a_section_for_every_planned_source`, `test_a_planned_source_without_a_section_fails`.
   - A DPL entry left unmapped: `test_every_dpl_entry_is_mapped`; a question ID named in the candidate table or the
     mapping that no list has: `test_every_question_the_research_record_names_exists` and its negative case.
   - A draft mandate sentence without a source tag or a named failure mode:
     `test_each_draft_mandate_sentence_has_a_source_and_names_its_failure_mode`, `test_a_draft_sentence_without_a_tag_fails_the_check`.
   - The benchmark measuring a mandate other than the research draft: `test_the_benchmarks_draft_mandates_are_the_research_drafts`.
   - `--stage`: a change that rewrites its own list (`test_a_stage_gets_the_base_commits_list_even_when_the_change_rewrites_it`);
     an unknown name, a missing `--stage` where the base has lists, a `--stage` on a base without lists, and a final
     review with a stage, each refused before any call; a final review without a list; a base without lists, said in
     the prompt and the start entry. 30 tests pass; the whole tooling suite, 711.
3. **Claims and what checks them mechanically.** "A change cannot rewrite the list it is reviewed against": the
   rewrite test. "Every question cites a researched source": the form test (it checks that the key exists, not that
   the source supports the question). "The code list repeats no coding rule": five phrases only. Not mechanical: that
   each quote is what its source says, that each question is specific to its type and answerable from the copy and
   the evidence, that the DPL mapping names the right stage, question and gate, and that no known class of defect
   passes every list. These are what this critique and 4.4's implementation review are for.
4. **Fixes and their upstream choice.** The critique (`review_critique.md`) had 22 findings, all answered there.
   The upstream choices behind them: the draft recheck mandate was written for the false-fix case only (C-1); the
   lists were built from the candidate items of the sources read first, and the DPL mapping was checked by stage, not
   root cause by root cause, so false document claims, test doubles never probed, and loosened checks had no question
   (C-3, C-5, C-6); several tags were chosen for the theme of a source, not for what its quote says (C-10, CR-B1,
   CR-B2); the form test trusted every source heading (CR-B3). Each fix went to the list, the record or the test, not
   to a new mechanism. The author's own earlier fix: the proof question had different wordings in different lists,
   so the placement test could not find it; one wording now.
5. **Tried the way the next user runs it.** `--stage` was run through the launcher with the fake `claude` on a
   throwaway repository whose base holds lists; the benchmark's dry run built all 46 prompts with the lists and the
   drafted mandates. Two live reviewers (the critique) read the lists and drafts as a reviewer would. No live review
   has run with a list in its prompt yet: the base has none; 4.5b's benchmark is the first.
6. **Where each rule lives.** `AGENTS.md`: the Start here row, per-stage blocking under "Review findings", and the
   "Stage checklists" bullet (the lists' use, `--stage`, the author's guideline, the learning loop). The lists in
   `docs/review_checklists/`. Why each item is in or out: `research.md`.
7. **What was removed, and its review.** Nothing is retired. The draft final-review and handoff lists of the plan
   draft were never written (S44-D1). Stage A's benchmark prompts stay as measured. From the lists the critique
   removed one clause (C4's "disclosing nothing sensitive", a repeat of coding rules 1 and 6), and the claim that
   excessive agency was merged into C7.

## Questions (a minimum, from the test plan)

1. *DPL mapping:* does every DPL entry have a question at the stage where the miss happened, or a reason why not, and
   name the gate or computed evidence that now catches it, or "none" (S44-D9)?
2. *Tests:* for each new or changed test, which wrong behaviour would still pass it?
3. *Keys:* does a key, socket or secret now reach a service outside its holders?
4. *Author's guideline:* quote the `AGENTS.md` text that says an author reads the stage's list before writing that
   stage's artifact; does the code list repeat a rule `make lint` or the coding rules already enforce?
5. *Names and headers:* do new files and names say what they do?
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 1418->1420 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/review_records.py: changed lines not run: none; branches not taken: 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_review_benchmark.py: changed lines not run: 295, 341, 616, 831, 835, 1064, 1356-1357; branches not taken: 294->295, 298->297, 340->341, 615->616, 772->769, 778->772, 829->831, 866->869, 1045->1043, 1204->1207, 1355->1356 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```

#### Report

```json
{
  "accounted": [
    {
      "item": "EV1",
      "note": "Line 166 (a spec that cannot be loaded) and line 906 (an AttemptLog without a record) are defensive guards against programming errors. Branch 1418->1420 is a HOME equal to '/' or empty. Lines 964-965: recovery deliberately swallows finish_record's ValueError for a missing section and leaves it to check_review_records, as `_complete_record`'s docstring says. This is not a security decision path, and the record check reports the missing section. There is no false green.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "check_docs.py:215 is the 'cannot load check_review_records.py' guard. It fails closed (it returns a problem) and only fires when the file cannot be loaded.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "Line 43 is the same defensive loader guard. Lines 203-206 and 210 are `main`, which the tooling tests run as a subprocess (issue #44), so in-process coverage cannot see them.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "review_inputs.py:286 returns early when the interpreter has no user site-packages directory, which depends on the environment. It is harmless: no link is made.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Branch 189->191: a section with no status line. Branch 228->230: an unlogged tail without a round heading before it. Both are benign variants of the record layout. The main paths are covered (CR-B8's tests).",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "Most lines are benign untested branches: 295 (an expected-location file is missing), 616 (no sink), the canary retry loops, 829-835 (a refused case already recorded), 1064 and 1204 (a failed non-defect case), and 1356-1357 (dispatch of --sample-confirmation). Line 341, the silent no-list path of `stage_list`, is the path a dry run on the committed key takes. It is raised as F3.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV7",
      "note": "The reviewed commit has no CI run, so the author's claim that 711 tooling tests pass, including the 30 in test_stage_checklists.py, is a local result only. Under the rules, a gate's result is its CI job's conclusion on the final PR. I counted the tests in test_stage_checklists.py: there are 30, matching the claim.",
      "opened": [
        "tests/tools/test_stage_checklists.py"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "plan.md:53 (S44-D13): \"Sources: prompting guidance for LLM reviewers; studies of LLM code review and of LLMs as judges ...\". research.md:18-267 has these sections: google-*, owasp-*, asvs, cert, stride, atam, nasa-req, iso29148, reqview-29148, incose, istqb, test-smells, fowler-*, owasp-llm, ieee1028, ieee1044, conventional-comments, zheng-judge (LLM as a judge), sharma-sycophancy, anthropic-prompting and owner. None of them is a study of LLM code review. tests/tools/test_stage_checklists.py:25-28 has no such key. Searched research.md, test_stage_checklists.py and review_critique.md's answers.",
      "failure_scenario": "Slice 4.5 measures mandate drafts whose failure modes come only from judge and sycophancy studies. Failure modes that LLM code-review studies document (for example noise, missed absence defects, hallucinated line references) have no mandate sentence. `test_the_research_record_has_a_section_for_every_planned_source` stays green, and the success criterion \"a section for every source\" looks met when it is not.",
      "file": "docs/slices/poc-4-4-stage-checklists/research.md",
      "id": "F1",
      "kind": "defect",
      "line": 18,
      "origin_stage": "discovery",
      "problem": "S44-D13 names \"studies of LLM code review\" as a source of the review-prompt research. `research.md` has no section for any such study, and nothing says it was searched for or could not be read. The test meant to catch a missing planned source cannot catch this one: its PLANNED_SOURCES set, whose comment says \"S44-D1 and S44-D13: every source the plan names\", leaves this source out. The test was written to fit the record, not the plan.",
      "severity": "high"
    },
    {
      "evidence": "run_independent_review.py:1675-1678: guards only for `mode` (4.1) and `path_hints` (4.2). Lines 1709-1711: the checklist is recomputed unconditionally. Line 1714: mismatches are compared with entry.get(name), which is None for pre-4.4 entries. Line 508: the placeholder used when checklist is None. The diff at change.diff:3369 shows a start entry without `checklist_sha256` or `stages`. No test rebuilds a pre-4.4 entry: test_run_independent_review.py:1207 covers only pre-4.1.",
      "failure_scenario": "An author or the final reviewer rebuilds an attempt from 4.1\u20134.3 to check what that reviewer was sent. They get mismatches on the checklist and full-prompt hashes, and conclude that the logged prompt cannot be reproduced or was tampered with, when only the layout changed.",
      "file": "scripts/run_independent_review.py",
      "id": "F2",
      "kind": "defect",
      "line": 1709,
      "origin_stage": "implementation",
      "problem": "`invocation_from_entry` now always rebuilds the checklist section through `stage_lists`, which gives \"No checklist at base <commit>: ...\" for a base without lists. Start entries logged by the 4.1\u20134.3 launcher (for example mechanics/c1/r1/A/1 and r2/A/1 in poc-4-5-benchmark's log, and the 4.1\u20134.3 logs) have no `checklist_sha256`. Their prompts carried the earlier placeholder \"None: this review has no stage checklist.\" A rebuild of such an entry therefore reports `checklist_sha256` and `full_prompt_sha256` as mismatches, as if its inputs had changed. The function gives the clear \"layout is retired\" message only for entries logged before 4.1 and 4.2, and has no such guard for 4.4.",
      "severity": "medium"
    },
    {
      "evidence": "answer_key.yaml:9 `lists_commit: ''`. run_review_benchmark.py:340-341 `if not key.lists_commit ...: return None, {}`. Lines 420-423 take this path for +list configurations. Lines 853-854 refuse it only in run_benchmark. Lines 880-895: dry_run calls case_prompt with no such check.",
      "failure_scenario": "Before 4.5b, the author runs `--dry-run` to confirm that the list prompts are right. It reports \"46 prompts built\" and exit 0 while every +list prompt lacks its list. The leak search also never sees the list text that the real run will send.",
      "file": "scripts/run_review_benchmark.py",
      "id": "F3",
      "kind": "defect",
      "line": 880,
      "origin_stage": "implementation",
      "problem": "`dry_run` does not apply `run_benchmark`'s refusal of +list configurations when the key has no `lists_commit`, and `stage_list` silently returns no list when `lists_commit` is empty. The committed answer key has `lists_commit: ''`. A dry run on the committed key therefore builds every +list prompt without a list, and its checklist section says \"None: this review has no stage checklist.\" Self-review claim 5 says \"the benchmark's dry run built all 46 prompts with the lists\". That cannot be reproduced from the committed key, and the claim does not say which key was used. The silent branch is untested (EV6: line 341 never runs).",
      "severity": "medium"
    },
    {
      "evidence": "unit-tests.md:24. AGENTS.md (change.diff:44-47): \"High is ... for example ... an untested fail-closed path\". research.md:354 maps DPL-010 (\"refusal paths untested\") to U6. Searched the six lists, AGENTS.md and research.md for a definition of \"security decision\"; there is none outside coding rule 4's \"security decision path\".",
      "failure_scenario": "Two reviewers of the same launcher change rate an untested refusal path differently, one as blocking and one as high. The round count and the merge decision then depend on which reviewer ran. 4.5's severity-agreement measure picks up noise that the lists themselves create.",
      "file": "docs/review_checklists/unit-tests.md",
      "id": "F4",
      "kind": "defect",
      "line": 24,
      "origin_stage": "discovery",
      "problem": "The unit-test list makes \"a fail-closed path of a security decision without a test that triggers it\" blocking. AGENTS.md (Review findings) gives \"an untested fail-closed path\" as an example of high. Neither text says what counts as a security decision. A reviewer holding both texts sees the same class of defect at two severities, with no rule for choosing between them. DPL-010's own case (the review launcher's untested refusal paths), the case U6 is mapped to, could fall on either side.",
      "severity": "medium"
    },
    {
      "evidence": "plan-and-test-plan.md:24 and Q2 (line 9). test_plan.md:33-47 (\"Review-based proof\" for S44-D4, S44-D6, S44-D8, S44-D11). AGENTS.md's static-test rule counts only a gate with tooling tests as a static proof.",
      "failure_scenario": "A plan reviewer given `--stage plan-and-test-plan` raises blocking findings on every review-proved decision of a process slice. Those findings must then be rejected round after round, using up the four-round budget. Or the author learns to call any review a \"check\", and decisions without real proof get through.",
      "file": "docs/review_checklists/plan-and-test-plan.md",
      "id": "F5",
      "kind": "defect",
      "line": 24,
      "origin_stage": "discovery",
      "problem": "The plan list blocks \"a decision or new requirement has no test or check that proves it\". Slice test plans, this slice's own included, prove some decisions by review: S44-D4, D6, D8 and D11 are \"Review-based proof\" in test_plan.md, and the template has a review-based proof section. The list does not say whether a named review counts as a \"check\". Read literally, it blocks this repository's own approved practice. Read loosely, it accepts any decision with a review note.",
      "severity": "medium"
    },
    {
      "evidence": "unit-tests.md:13; plan-and-test-plan.md:18; research.md:57, 87, 93.",
      "failure_scenario": "A reader checking the lists' sources finds a citation that does not support the question, which weakens trust in the rest of the research record (threat item: a research record that cites a source wrongly).",
      "file": "docs/review_checklists/unit-tests.md",
      "id": "F6",
      "kind": "defect",
      "line": 13,
      "origin_stage": "discovery",
      "problem": "Two tags still follow a source's theme rather than what its quote says. This is the cause of C-10, CR-B1 and CR-B2, which claim 4 says was searched for. U6 (a test for every fail-closed path) is tagged [S:owasp-code-review], whose quote is \"Fail-safe defaults: Default deny access policy\", a rule for code, not for tests. P11 (a change to the threat model goes to the user) is tagged [S:owasp-threat], whose quotes say to keep the model current, not who approves a change to it.",
      "severity": "low"
    },
    {
      "evidence": "test_stage_checklists.py:159-167 compare int(m.group(2)) > counts[letter] only.",
      "failure_scenario": "A new code question is inserted at position 3. research.md still maps DPL-009 to C8 and C11, which are now different questions, and `test_every_question_the_research_record_names_exists` passes.",
      "file": "tests/tools/test_stage_checklists.py",
      "id": "F7",
      "kind": "defect",
      "line": 157,
      "origin_stage": "tests first",
      "problem": "`named_question_problems` checks only that a question ID named in research.md is no higher than the number of questions in its list. If a list is renumbered (an item inserted or removed, which the learning loop S44-D11 expects), every ID can stay in range while pointing at a different question. The DPL mapping and the candidate table then go stale and the test stays green.",
      "severity": "low"
    },
    {
      "evidence": "test_stage_checklists.py:86-88; run_independent_review.py:1625-1628.",
      "failure_scenario": "A later editor reuses `_has_dir` for another directory, or misreads what `draft` returns.",
      "file": "tests/tools/test_stage_checklists.py",
      "id": "F8",
      "kind": "defect",
      "line": 86,
      "origin_stage": "implementation",
      "problem": "Naming (question 5): the helper `draft` has no docstring, and its name does not say that it returns the numbered sentences of a draft mandate. In the launcher, `_has_dir` checks only for `docs/review_checklists/` at a commit, but its name suggests any directory.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to implementation/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| F1 | high | fixed: docs/slices/poc-4-4-stage-checklists/research.md, tests/tools/test_stage_checklists.py: two studies of LLM code review now have source sections, read on 2026-11-10 from their abstracts: `cihan-acr` (an industrial study: 73.8% of comments resolved, with faulty reviews, unnecessary corrections and irrelevant comments, and longer closure times) and `swr-bench` (current systems underperform and do better on functional errors; aggregating several reviews helps). The review-prompt section says what they add, and initial sentences 5 and 6 cite `cihan-acr` for the failure modes they counter. The origin was the planned-source set, which was written from the record instead of the plan; it now names both studies, with a comment mapping the plan's phrases to keys |
| F2 | medium | fixed: scripts/run_independent_review.py, tests/tools/test_run_independent_review.py: `invocation_from_entry` refuses an entry without `stages`, logged before 4.4, with the same "layout is retired" message as for 4.1 and 4.2; the test is parametrized over the three layout changes |
| F3 | medium | fixed: scripts/run_review_benchmark.py, tests/tools/test_run_review_benchmark.py: the dry run applies the run's refusal (`check_lists_commit`), so it cannot report every prompt built while the +list prompts hold no list; `test_dry_run_is_refused_like_a_run_when_the_key_names_no_lists_commit`. The self-review's claim 5 was false: the dry run of 2026-11-10 ran with an empty `lists_commit`, so its +list prompts held no list. The dry run with the lists runs once the key names the lists' commit, before the benchmark |
| F4 | medium | fixed: docs/review_checklists/unit-tests.md, AGENTS.md: the unit-test list blocks an untested fail-closed path of a security decision of the system under test (an enforcement or validation path, coding rule 4), and `AGENTS.md`'s example of high is an untested fail-closed path outside those decisions, so the two texts no longer give the same case two severities |
| F5 | medium | fixed: docs/review_checklists/plan-and-test-plan.md: P2 says that a decision proved by review names the review question that answers it, and the Blocks entry blocks a decision with no test, gate or named review question, which is how this repository's test plans prove process decisions |
| F6 | low | fixed: docs/review_checklists/unit-tests.md, docs/review_checklists/plan-and-test-plan.md: U6 also cites `google-looking-for` (tests must fail when the code is broken); P11 now asks what `owasp-threat` says (the threat model kept current with the change), and the rule that a change goes to the user is `AGENTS.md`'s, which the reviewer gets |
| F7 | low | rejected: renumbering is the case the learning loop's own review covers (an item proposed in the PR, approved by the owner, S44-D11); a check that a mapped ID still means the same question would need the mapping to quote each question's text, a heavier format for a low finding |
| F8 | low | fixed: tests/tools/test_stage_checklists.py, scripts/run_independent_review.py: `draft` has a docstring that says it returns a draft mandate's numbered sentences with their tags, and `_has_dir` is now `_has_lists_dir`, with a docstring |
