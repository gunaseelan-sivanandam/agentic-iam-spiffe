# Review record — poc-4-4-stage-checklists, unit `critique`

The record of the review unit `critique`: the launcher writes each attempt's task prompt, evidence and report verbatim, and the author answers every finding under `#### Answers to <attempt id>`. `make docs-check` checks it against the attempt log, `review_attempts.jsonl`.

## Round 1

### Attempt critique/c1/r1/A/1

Reviewer `A`: `claude-opus-5-5`, effort high, mode initial, commit `0e0a201c783a`, base `3347754ef038`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
# Critique of slice 4.4's draft stage checklists and draft mandates (issue #41), reviewer A

## Intent

The approved plan and test plan are `docs/slices/poc-4-4-stage-checklists/plan.md` (decisions S44-D1 to S44-D13)
and `test_plan.md`, merged into `poc/agentic-sdlc` by plan PR #48 (the base of this review). Slice 4.4 researches
established review practice per artifact type and writes a short list of questions, with what blocks at that stage,
for each of six types: plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code.
The lists are in `docs/review_checklists/`; the research behind them, the mapping of the delivery problem log
(DPL-001 to DPL-011) to the lists, and the drafts of the three review mandates are in `research.md` of the bundle.
The launcher gains `--stage`, which gives a review its stage's list from the base commit. Each list is also the
author's guideline for its stage (S44-D8).

This review is the critique unit of S44-D10: two models review the draft lists and the draft mandates from
different angles, before 4.4's implementation review and before slice 4.5 measures the lists and the drafts in its
benchmark. The reviewed commit also holds slices 4.1 to 4.3 and 4.5's first part, each reviewed in its own unit;
4.4's own commit is `1750c8d`.

## Your angle (where to start, not where to stop)

Which known class of defect would pass every question of the list for its stage, and every "Blocks at this stage"
criterion? Draw on the sources in `research.md`, on the delivery problem log (`docs/delivery_problem_log.md`), and on
what you know of reviewing requirements, designs, tests and code. For each such class, say at which stage it would
be made, give a concrete example of the kind of change this repository makes, and say what question (with a source
that supports it) would catch it, or why no question should. Also: would a sentence of a draft mandate lead a
reviewer to miss something, to overrate it, or to report noise; and does a list ask a question that only adds noise?

## The author's self-review of slice 4.4 (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.**
   - The sources: every page `research.md` quotes was read on 2026-11-09 with a web-fetch tool; its Method section
     says how quotes were taken. Three sources could not be read and give no item: SEI CERT's page (the connection
     was reset on four attempts), INCOSE's summary sheet (HTTP 403; the guide itself is sold) and the ISTQB syllabus
     (a PDF no available tool could read); each section says so. Three paid standards (ISO/IEC/IEEE 29148, IEEE 1028, IEEE 1044) are cited by title only, and
     NASA's public checklist and ReqView's public 29148 templates stand in for the requirements sources.
   - The base has no lists: `git ls-tree -r --name-only origin/poc/agentic-sdlc docs/review_checklists` prints
     nothing, so every review of slice 4 runs with "No checklist at base <commit>", as S44-D7 says.
   - Reviewers have no web access (the launcher offers only Read, Grep and Glob), so every quote a list rests on is
     in `research.md` itself.
2. **Each check added or changed, the case it catches, and its test** (in `tests/tools/test_stage_checklists.py`).
   - A list without a title and purpose, with more than 12 questions, with an untagged question, a tag that names no
     source section, a DPL entry as a source, or no "Blocks at this stage" section:
     `test_every_list_has_the_agreed_form_and_cites_researched_sources`, and one negative case per kind in
     `test_the_form_check_fails_on_each_kind_of_violation`.
   - A list for a type the plan does not name, or a final-review or handoff list: `test_exactly_the_six_artifact_types_have_a_list`.
   - The two questions for what is missing in the wrong lists: `test_the_two_questions_for_what_is_missing_sit_where_the_misses_happen`.
   - A coding rule repeated in the code list: `test_the_code_list_repeats_no_coding_rule` (five phrases only).
   - A planned source without a section, or a paid standard not marked title only:
     `test_the_research_record_has_a_section_for_every_planned_source`, `test_a_planned_source_without_a_section_fails`.
   - A DPL entry left unmapped: `test_every_dpl_entry_is_mapped`.
   - A draft mandate sentence without a source tag or a named failure mode:
     `test_each_draft_mandate_sentence_has_a_source_and_names_its_failure_mode`, `test_a_draft_sentence_without_a_tag_fails_the_check`.
   - The benchmark measuring a mandate other than the research draft: `test_the_benchmarks_draft_mandates_are_the_research_drafts`.
   - `--stage`: a change that rewrites its own list (`test_a_stage_gets_the_base_commits_list_even_when_the_change_rewrites_it`);
     an unknown name, a missing `--stage` where the base has lists, a `--stage` on a base without lists, and a final
     review with a stage, each refused before any call; a final review without a list; a base without lists, said in
     the prompt and the start entry. 25 tests pass.
3. **Claims and what checks them mechanically.** "A change cannot rewrite the list it is reviewed against": the
   rewrite test. "Every question cites a researched source": the form test (it checks that the key exists, not that
   the source supports the question). "The code list repeats no coding rule": five phrases only. Not mechanical: that
   each quote is what its source says, that each question is specific to its type and answerable from the copy and
   the evidence, that the DPL mapping names the right stage, question and gate, and that no known class of defect
   passes every list. These are what this critique and 4.4's implementation review are for.
4. **Fixes and their upstream choice.** No reviewer findings yet. The author's own: the proof question first had
   different wordings in different lists, so the placement test could not find it; one wording now.
5. **Tried the way the next user runs it.** `--stage` was run through the launcher with the fake `claude` on a
   throwaway repository whose base holds lists; the benchmark's dry run built every case's prompt with the lists and
   the drafted mandates from this commit. No live review has used a list yet: the base has none.
6. **Where each rule lives.** `AGENTS.md`: the Start here row, per-stage blocking under "Review findings", and the
   "Stage checklists" bullet (the lists' use, `--stage`, the author's guideline, the learning loop). The lists in
   `docs/review_checklists/`. Why each item is in or out: `research.md`.
7. **What was removed, and its review.** Nothing is retired. The draft final-review and handoff lists of the plan
   draft were never written (S44-D1). Stage A's benchmark prompts stay as measured.

## Questions (a minimum, from the test plan)

1. *Lists:* is every question specific to its artifact type and answerable from the copy and the evidence, with at
   most 12 per list? Does a "Blocks at this stage" criterion let a requirement or a test defect through, or block
   what should not block?
2. *DPL mapping:* does every DPL entry name a question at the stage where the miss happened, or a reason why none,
   and the gate or computed evidence that now catches it, or "none" (S44-D9)?
3. *Citations:* do the quotes a question rests on support it? Is any clause of a paid standard used beyond its title?
4. *Author's guideline:* where does `AGENTS.md` say that an author reads the stage's list before writing that stage's
   artifact, and does the code list repeat a rule `make lint` or the coding rules already enforce?
5. *`--stage`:* can a review run without its list, or with a list the change itself wrote, and nothing shows it?
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 117->110, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_records.py: changed lines not run: 188; branches not taken: 187->188, 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 1418->1420 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_review_benchmark.py: changed lines not run: 295, 341, 616, 831, 835, 849, 1064, 1356-1357; branches not taken: 294->295, 298->297, 340->341, 615->616, 772->769, 778->772, 829->831, 848->849, 866->869, 1045->1043, 1204->1207, 1355->1356 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
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
      "note": "check_docs.py:214-215 handles a missing spec for a file that is always present: defensive and unreachable in normal use.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "Lines 43 and 203-210 are a defensive loader and the CLI main, which docs-check never runs in-process. Branch 117->110, an incomplete next-round attempt that must not count as acceptance, is a closed path of the gate with no test: C-14.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV3",
      "note": "review_inputs.py:285-286 is the branch for an interpreter without a user site-packages directory. It depends on the environment and is harmless.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "review_records.py:188 (ValueError when a section is missing) and branches 189->191 and 228->230 are defensive recovery paths. The launcher catches the ValueError at run_independent_review.py:964-965. Low risk.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV5",
      "note": "Lines 166 (loader), 906 (an attempt log without a record) and 964-965 (a ValueError swallowed in recovery) are defensive, as is 1418->1420 (HOME is '/'). None is in 4.4's `--stage` code, whose refusal paths test_stage_checklists.py covers.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV6",
      "note": "These are 4.5a runner paths: expected-line skips, a lists_commit guard behind earlier refusals (line 341 is reached only after run_benchmark already refuses an empty lists_commit), deduplication of refusals, and the stage-A refusal (849). They are untested but not security decisions. Recorded here and not raised as a 4.4 finding.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "There is no CI run for this commit, so the author's claim '25 tests pass' rests on a local run. I counted 25 test cases in test_stage_checklists.py, which matches the claim, but CI has not confirmed them. A gate's result is its CI job's conclusion, so this must be confirmed on the PR.",
      "opened": [
        "tests/tools/test_stage_checklists.py"
      ],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "research.md:365 and tests/review_benchmark/prompts/mandate_recheck_b.md:7 say 'Accept a finding only when the code now does what the finding asked'. AGENTS.md (Review loop) says the reviewer 'sees each rejection and either accepts it, re-raises it with new evidence, or answers that it cannot determine it', and lists checkable rejection reasons. AGENTS.md (Plan review) says 'from round 2 a new finding counts only if it is blocking or high'. test_the_benchmarks_draft_mandates_are_the_research_drafts pins the benchmark text to this draft.",
      "failure_scenario": "4.5 runs recheck-A and recheck-B on RC-1, whose only answer is a false `fixed:` (S45-D5). The draft's bias toward re-raising scores as a success there, so the owner adopts recheck-B in 4.5b. From then on, a recheck re-raises every rejection the author correctly answered with 'the scenario does not happen (evidence)', and every `deferred: #N` medium finding, with no new evidence. Each one goes to the user as disputed, and plan rechecks re-raise everything because no code changed. The rulebook and the launcher's mandate then say opposite things about what a recheck may accept.",
      "file": "docs/slices/poc-4-4-stage-checklists/research.md",
      "id": "C-1",
      "kind": "defect",
      "line": 365,
      "origin_stage": "implementation",
      "problem": "Sentence 2 of the draft recheck mandate, 'Accept a finding only when the code now does what the finding asked; otherwise re-raise it', contradicts the review loop in AGENTS.md. The review loop lets a recheck accept a rejection whose reason it can check (the failure scenario does not happen, outside the threat model, already covered by a named test or gate). It also allows `deferred:` and `owner:` answers, and it requires a re-raise to bring new evidence. Under the draft, every valid rejection, every deferral and every plan-review answer (a plan review changes no code) must be re-raised. Sentence 4 ('Report anything wrong or missing in what the fixes touched') also drops the rule that from round 2 a new finding counts only if it is blocking or high. The same text is the live benchmark configuration recheck-B.",
      "severity": "blocking"
    },
    {
      "evidence": "answer_key.yaml has one entry with `kind: recheck` (line 360; the others are canary, real_miss, planted, clean and decoy). RC-1_answers.md holds a single `fixed:` row described as 'a file whose change does not fix the finding'. 4.5 plan S45-D5 and S45-D8 say the owner decides each mandate wording, recheck separately.",
      "failure_scenario": "A recheck wording that re-raises everything gets a perfect score on RC-1 and is chosen. Nothing in the benchmark shows that it turns every correct rejection into a dispute for the owner. A recheck case with a correct rejection, or a correct fix, would show it. This goes to the owner because S45-D5 fixed the cases.",
      "file": "tests/review_benchmark/answer_key.yaml",
      "id": "C-2",
      "kind": "decision_concern",
      "line": 359,
      "origin_stage": "tests first",
      "problem": "The benchmark has a single recheck case, RC-1, and its answer is a false `fixed:`. It can measure only one failure mode, accepting a false fix. It cannot measure the opposite one: re-raising a correct fix or a valid rejection (the failure mode C-1 introduces, and the 'contrarian' side of sycophancy). The owner will choose the recheck wording from one run per wording (S45-D6: recheck-A and recheck-B, 2 runs).",
      "severity": "high"
    },
    {
      "evidence": "Searched all six lists in docs/review_checklists/ for document claims, test_spec prose and STATUS/log accuracy: none. e2e-tests.md says it covers `docs/test_spec.md`, but none of its questions asks whether the prose matches the test, although AGENTS.md says docs-check 'cannot judge the prose, so review it'. False claims in the DPL: DPL-001 ('the private key never leaves the issuer container', untested); DPL-006 (a failed run reported as passing); DPL-009 ('AGENTS.md and docs/STATUS.md said the gate holds changed lines\u2026 For capiss it never did'); DPL-010 R5-B2 (the 'verbatim' claim was false). research.md:324-327 maps DPL-006 to 'none' and DPL-009/DPL-010 only to C8/U6, which concern tests, not claims. Sources that support a question: owasp-threat's 'Does the DFD\u2026 accurately reflect the system?' (already used for A6), and google-looking-for's comments and documentation section.",
      "failure_scenario": "In an implementation review run with `--stage code`, the author updates STATUS.md to say a gate now covers a module that it does not cover (DPL-009 again). Every code-list question is answered correctly and no Blocks criterion applies, so the false claim merges, unless the open mandate happens to catch it. A question for the code list and the E2E list would catch it, for example 'Does every statement the change adds or leaves in a document (status, logs, test_spec, rulebook) hold in the copy?'",
      "file": "docs/review_checklists/code.md",
      "id": "C-3",
      "kind": "defect",
      "line": 5,
      "origin_stage": "implementation",
      "problem": "No list asks whether the claims a change makes in its documents are true. Examples are a status row, STATUS.md, the implementation log, AGENTS.md's gate table, a record's 'verbatim' claim, test_spec.md prose against what the guard does, and the PR body. False claims are the most frequent class in the delivery problem log, and the DPL mapping does not map that part to any question. The only sentence on stale documents is in the final mandate, which no review before the final one gets. This change shows the gap itself (see C-4).",
      "severity": "high"
    },
    {
      "evidence": "docs/slices/README.md:20. docs/review_checklists/*.md and research.md exist in the copy. A Grep of implementation_log.md for '4.4|S44|checklist' finds no 4.4 entry.",
      "failure_scenario": "The owner or the next agent reads the slice index (the step-4 close-out document) and concludes that 4.4 has not begun. The 4.5b runs that depend on 4.4 are then planned or ordered wrongly.",
      "file": "docs/slices/README.md",
      "id": "C-4",
      "kind": "defect",
      "line": 20,
      "origin_stage": "implementation",
      "problem": "The slice index row for poc-4-4-stage-checklists says 'Plan merged (PR #48); not started'. The reviewed commit holds 4.4's lists, research.md, `--stage` and the tests (4.4's own commit `1750c8d`), and the rows for 4.1, 4.2, 4.3 and 4.5a say 'implemented on the slice 4 branch, in review'. docs/history/implementation_log.md has no 4.4 entry either.",
      "severity": "medium"
    },
    {
      "evidence": "DPL-010 RC3: 'the fake CLI sent no tool results, so no test could show a failed Read. How the real CLI reports one was assumed, not probed.' DPL-011 RC3: 'How the CLI answers a call to a tool it does not offer was not probed.' DPL-011 RC4: 'No question asked how the next user would run it.' unit-tests.md and e2e-tests.md have no question on test doubles. tests/tools/fakes/fake_claude.py is changed in this very diff. The test plan (Independent review, question 1) says 'A gap in question 1 for a DPL entry \u2026 blocks' at the implementation review. fowler-pyramid (contract tests) supports such a question, but research.md says only 'the first part of the article was read'.",
      "failure_scenario": "In slice 5, fake_claude.py gains a new event shape that the real CLI never emits, and a launcher check passes against the fake. U1-U9 and E1-E9 all pass: the test fails when the code is broken, under the fake's behaviour. The same miss as DPL-010 and DPL-011 repeats. A question such as 'Does each fake or mock reproduce the real dependency's behaviour as a recorded probe showed it?' would catch it.",
      "file": "docs/slices/poc-4-4-stage-checklists/research.md",
      "id": "C-5",
      "kind": "defect",
      "line": 328,
      "origin_stage": "implementation",
      "problem": "The DPL mapping leaves out a root cause that recurs in two entries: a test double, or an assumption about an external tool, whose behaviour was never probed against the real one. Neither the unit-test list nor the E2E list asks whether a fake or mock behaves like the real dependency, with the probe that showed it. Plan question P6 covers facts a decision depends on, not test doubles written during tests first or implementation. The mapping gives DPL-010 'U6; C8' and DPL-011 'C2', but neither question catches these causes. DPL-011 RC2 (secret-check rules tested on log lines, then applied to prose) is also unmapped. That is the class 'a check used on an input domain it was never tested on'.",
      "severity": "high"
    },
    {
      "evidence": "Searched all six lists for exception, expiry, accepted_gaps, known_violations, alternate, threshold, loosen, weaken and remove: none. AGENTS.md: 'loose or wrong tests, weakened checks, skipped steps, stale evidence'; 'Every exception must fit on one line and have an expiry'. DPL-004: 'the cut was not re-reviewed on the reasoning that it \"only removes checks\"'.",
      "failure_scenario": "A change adds an `accepted_gaps` entry with a far-off expiry, or a `test-lint: alternate` marker on a negative E2E guard, so that a failing gate goes green. qa-trace and test-lint pass by design. Every list question can be answered 'yes', and the code list's Blocks criterion ('a check that passes on the case it exists to catch') does not apply, because the check was told to skip that case.",
      "file": "docs/review_checklists/code.md",
      "id": "C-6",
      "kind": "defect",
      "line": 5,
      "origin_stage": "implementation",
      "problem": "No list asks whether a change weakens an existing check or adds an exception. The delivery threat model names 'weakened checks', and DPL-004's lesson is 'Removing a check is a change like any other'. Examples of what no question covers: a lowered threshold, a new `accepted_gaps` or `known_violations` row, a `# test-lint: alternate:` marker, a `noqa`, a removed negative control, an exception without a one-line reason and an expiry ('Few exceptions'). Code question C8 asks only whether a new or changed check fails on its own case, which a loosened check still does. E8 covers only the loss of a requirement's last proof.",
      "severity": "high"
    },
    {
      "evidence": "code.md:7-16. research.md:24 quotes only the edge-case sentence of google-looking-for's Functionality section. AGENTS.md step 3: 'Implement. Only approved behavior.' Operating model: 'Do not introduce or keep runtime-significant behavior that exists only in code.'",
      "failure_scenario": "An implementation adds a fallback the plan never approved (for example, `--stage` silently taking the PR head's list when the base has none). The design is simple, edge cases are handled, names are clear and the tests fail on breakage. No code-list question asks whether the behaviour was approved.",
      "file": "docs/review_checklists/code.md",
      "id": "C-7",
      "kind": "defect",
      "line": 7,
      "origin_stage": "implementation",
      "problem": "The code list has no question on whether the code does what the plan decided, and only that. That is functional correctness against intent, plus the rule in step 3 that only approved behaviour is implemented. C1 asks whether the design fits, and C2 asks about edge cases. research.md quotes Google's 'Functionality' section only for edge cases and leaves out its first question, whether the CL does what the developer intended. Code that does something different from a decision, or more than it, passes every code question.",
      "severity": "medium"
    },
    {
      "evidence": "plan-and-test-plan.md has 9 questions, and none covers growth approval, threat-model changes, hidden state or retirement. AGENTS.md says 'Hidden-state rule \u2026 Mandatory for security-relevant Redis, file, cache \u2026' and 'Retirement rule: every plan.md states what old logic is removed'. Under 'Ask before growing' and 'Threat model changes': 'No agent changes, widens or narrows an approved threat model \u2026 without the user's approval'.",
      "failure_scenario": "A plan narrows its own threat model ('rogue workloads out of scope for this slice') to make a finding go away, and adds a new gate without its failure/cost/alternative row. No decision contradicts another, so P7 passes, and no other question asks.",
      "file": "docs/review_checklists/plan-and-test-plan.md",
      "id": "C-8",
      "kind": "defect",
      "line": 5,
      "origin_stage": "implementation",
      "problem": "The plan list leaves out several rules that a plan must satisfy and that reviewers have missed before. (a) Each new check or process step states the failure it catches, its cost and the simpler alternative, and the user approves it ('Ask before growing'). (b) No agent changes, widens or narrows the approved threat model. P7 checks for contradiction, not for a change. (c) The hidden-state rule: its fields are mandatory in plan.md, and A10 asks for them only at the architecture stage. (d) The retirement rule. The list has 9 questions, so S44-D3 leaves room for 3 more. Over-engineering (google-looking-for) and owasp-threat (data stores) already support (a) and (c).",
      "severity": "medium"
    },
    {
      "evidence": "AGENTS.md:71 and AGENTS.md:253-262 ('the tests-first stage takes unit-tests and e2e-tests; the final review takes none'; no rule for the implementation review). scripts/run_independent_review.py:1604-1622 accepts any combination of existing names, chosen by the author. Line 1573 is `--stage` with `action=\"append\"`. The ORIGIN_STAGES tuple is at line 63.",
      "failure_scenario": "An implementation review runs with `--stage code` only, because nothing names its stages until 4.6. It finds that a changed unit test can pass while the behaviour is broken. The code list's Blocks section does not include that case, and the unit-test list was never given, so the reviewer rates it high. The same finding blocks in a tests-first review. The same defect is blocking in one review and high in another, and the author's stage choice decides which.",
      "file": "AGENTS.md",
      "id": "C-9",
      "kind": "defect",
      "line": 71,
      "origin_stage": "discovery",
      "problem": "'A finding also blocks when it meets the \"Blocks at this stage\" section of its stage's checklist' does not say whose stage is meant: the review's stage (`--stage`), or the finding's origin_stage. A reviewer receives only the lists of its `--stage`. A finding that arose at another stage therefore cannot be judged by that stage's criteria. Examples: a requirement no test could verify, found in a code review, or a test that can pass while broken, found in a code-only review. The final review gets no list at all. The origin_stage names (discovery, tests first, implementation) also do not map one-to-one onto the list names (plan-and-test-plan, unit-tests plus e2e-tests, code). AGENTS.md does not say which lists an implementation review takes, so whether a finding blocks depends on which `--stage` the author chose.",
      "severity": "medium"
    },
    {
      "evidence": "research.md:37 (google-standard approval quote) against :355; :219 against :360; :23-31 against :367; :217-218 against :340-341. The author's claim 3 says the form test checks only that a tag's key exists.",
      "failure_scenario": "The owner picks the final draft 'by reason' (S45-D8), trusting that each sentence rests on its tagged source. One sentence rests on a source that argues the other way. The reasoning that research.md records cannot be checked by any reviewer, because reviewers have no web access.",
      "file": "docs/slices/poc-4-4-stage-checklists/research.md",
      "id": "C-10",
      "kind": "defect",
      "line": 355,
      "origin_stage": "implementation",
      "problem": "Several draft-mandate sentences cite sources that do not support them. This is the threat item 'a research record that cites a source wrongly'. (1) Initial S1 cites google-standard to counter 'approving because the change looks like an improvement while it still holds a defect'. The quoted rule says the opposite: 'reviewers should favor approving a CL once it is in a state where it definitely improves'. (2) Initial S6 cites zheng-judge's verbosity bias, which is about judges favouring longer answers by others, not about a reviewer padding its own report. (3) Recheck S4 cites google-looking-for, but none of its quotes concerns rechecks. (4) The 'Order of sections' reasoning cites position bias in pairwise judging as evidence about section order in a prompt.",
      "severity": "medium"
    },
    {
      "evidence": "code.md:16 (C8, 'shown by a test') and code.md:22-23 (Blocks). DPL-009: 'The gate had no tooling test with a negative control \u2026 A gate without a negative control can be silently empty.' Reviewers get only Read, Grep and Glob.",
      "failure_scenario": "A new gate with a filter bug like DPL-009's ships without a negative control. The reviewer cannot run it and so cannot show that it passes on its case. The finding is rated high and deferred by the owner, and the gate stays silently empty.",
      "file": "docs/review_checklists/code.md",
      "id": "C-11",
      "kind": "defect",
      "line": 24,
      "origin_stage": "implementation",
      "problem": "The code list's Blocks criterion 'a check or gate that passes on the case it exists to catch' requires the reviewer to show that the check passes on its case. A read-only reviewer usually cannot run it. The observable defect of DPL-009 was a new gate without a negative control test, and that is not blocking at any stage. C8 asks for the test, but missing it is only high.",
      "severity": "medium"
    },
    {
      "evidence": "tests/tools/test_stage_checklists.py:79-82 reads repository files by design. AGENTS.md coding rule 8. code.md:12.",
      "failure_scenario": "Reviewers with `--stage unit-tests` report a mystery-guest finding on every static-gate test. Authors answer them as noise, and real U-list findings get less attention.",
      "file": "docs/review_checklists/unit-tests.md",
      "id": "C-12",
      "kind": "defect",
      "line": 13,
      "origin_stage": "implementation",
      "problem": "Some list questions will mostly produce noise in this repository. U7 ('depend on external files') flags every tooling test that reads the live tree on purpose: the static gates' tests, and test_stage_checklists.py itself reading docs/review_checklists. U9 ('literal values \u2026 explained') flags exit codes and counts everywhere. C6 repeats coding rule 8 ('Names say what a file, function or component does'), although S44-D8 keeps such rules out of the code list (S44-D8 itself names names as an exception, so the overlap is partial).",
      "severity": "low"
    },
    {
      "evidence": "research.md:359. AGENTS.md: the evidence includes 'the CI results of the reviewed commit from the public API'.",
      "failure_scenario": "The evidence shows a failed CI job. The reviewer drops the finding because there is no file and line for it in the copy.",
      "file": "tests/review_benchmark/prompts/mandate_initial_b.md",
      "id": "C-13",
      "kind": "defect",
      "line": 7,
      "origin_stage": "implementation",
      "problem": "Initial-draft sentence 5, 'Report only what the copy supports: a file and line, or what you searched for and did not find', leaves out the computed evidence (CI results from the public API) and facts outside the copy. DPL-005 RC4 (a ruleset outside the repository) is an example of such a fact. A reviewer may drop findings that rest on the evidence section.",
      "severity": "low"
    },
    {
      "evidence": "EV2: branch 117->110 not taken. check_review_records.py:117 `if (logged.end or {}).get(\"status\") == \"completed\" and block:`.",
      "failure_scenario": "A recheck attempt is interrupted after it wrote a partial Report block, or one is edited in. A later edit loosens the condition to `or`. A rejected blocking finding then counts as accepted, and `make docs-check` stays green: a false green in the record check.",
      "file": "scripts/check_review_records.py",
      "id": "C-14",
      "kind": "defect",
      "line": 117,
      "origin_stage": "tests first",
      "problem": "No test covers the branch where the next round's attempt is not completed, or has no Report block, and so must not count as accepting a rejected blocking or high finding. This is the closed side of a check in the docs-check gate. If the condition were mutated (for example `and` changed to `or`), an interrupted or withheld recheck would settle a rejection, and no tooling test would fail.",
      "severity": "high"
    }
  ],
  "verdict": "no"
}
```


### Attempt critique/c1/r1/B/1

Reviewer `B`: `claude-sonnet-5-5`, effort high, mode initial, commit `0e0a201c783a`, base `3347754ef038`.

Status: failed (the report does not account for what it was given: EV7 names an opened file the attempt did not read).

#### Prompt

```markdown
# Critique of slice 4.4's draft stage checklists and draft mandates (issue #41), reviewer B

## Intent

The approved plan and test plan are `docs/slices/poc-4-4-stage-checklists/plan.md` (decisions S44-D1 to S44-D13)
and `test_plan.md`, merged into `poc/agentic-sdlc` by plan PR #48 (the base of this review). Slice 4.4 researches
established review practice per artifact type and writes a short list of questions, with what blocks at that stage,
for each of six types: plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code.
The lists are in `docs/review_checklists/`; the research behind them, the mapping of the delivery problem log
(DPL-001 to DPL-011) to the lists, and the drafts of the three review mandates are in `research.md` of the bundle.
The launcher gains `--stage`, which gives a review its stage's list from the base commit. Each list is also the
author's guideline for its stage (S44-D8).

This review is the critique unit of S44-D10: two models review the draft lists and the draft mandates from
different angles, before 4.4's implementation review and before slice 4.5 measures the lists and the drafts in its
benchmark. The reviewed commit also holds slices 4.1 to 4.3 and 4.5's first part, each reviewed in its own unit;
4.4's own commit is `1750c8d`.

## Your angle (where to start, not where to stop)

Is the research behind the lists right, and are the lists usable? Check a sample of the quotes in `research.md`
against what the named public source could say, and flag any quote that its source would not hold or that does not
support the question it is tagged on; flag any use of a paid standard beyond its title. Check the DPL mapping: for
each of DPL-001 to DPL-011, is the stage the right one, would the named question really have caught the miss, and is
the named gate or computed evidence real? Check each question: is it specific to its artifact type (a question that
fits every type belongs to the mandate, S44-D3), can a reviewer answer it from the frozen copy and the evidence alone,
and does the code list repeat a rule that `make lint` or the coding rules of `AGENTS.md` already enforce (S44-D8)?
Check that each draft mandate sentence's tag and named failure mode fit what the source says.

## The author's self-review of slice 4.4 (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.**
   - The sources: every page `research.md` quotes was read on 2026-11-09 with a web-fetch tool; its Method section
     says how quotes were taken. Three sources could not be read and give no item: SEI CERT's page (the connection
     was reset on four attempts), INCOSE's summary sheet (HTTP 403; the guide itself is sold) and the ISTQB syllabus
     (a PDF no available tool could read); each section says so. Three paid standards (ISO/IEC/IEEE 29148, IEEE 1028, IEEE 1044) are cited by title only, and
     NASA's public checklist and ReqView's public 29148 templates stand in for the requirements sources.
   - The base has no lists: `git ls-tree -r --name-only origin/poc/agentic-sdlc docs/review_checklists` prints
     nothing, so every review of slice 4 runs with "No checklist at base <commit>", as S44-D7 says.
   - Reviewers have no web access (the launcher offers only Read, Grep and Glob), so every quote a list rests on is
     in `research.md` itself.
2. **Each check added or changed, the case it catches, and its test** (in `tests/tools/test_stage_checklists.py`).
   - A list without a title and purpose, with more than 12 questions, with an untagged question, a tag that names no
     source section, a DPL entry as a source, or no "Blocks at this stage" section:
     `test_every_list_has_the_agreed_form_and_cites_researched_sources`, and one negative case per kind in
     `test_the_form_check_fails_on_each_kind_of_violation`.
   - A list for a type the plan does not name, or a final-review or handoff list: `test_exactly_the_six_artifact_types_have_a_list`.
   - The two questions for what is missing in the wrong lists: `test_the_two_questions_for_what_is_missing_sit_where_the_misses_happen`.
   - A coding rule repeated in the code list: `test_the_code_list_repeats_no_coding_rule` (five phrases only).
   - A planned source without a section, or a paid standard not marked title only:
     `test_the_research_record_has_a_section_for_every_planned_source`, `test_a_planned_source_without_a_section_fails`.
   - A DPL entry left unmapped: `test_every_dpl_entry_is_mapped`.
   - A draft mandate sentence without a source tag or a named failure mode:
     `test_each_draft_mandate_sentence_has_a_source_and_names_its_failure_mode`, `test_a_draft_sentence_without_a_tag_fails_the_check`.
   - The benchmark measuring a mandate other than the research draft: `test_the_benchmarks_draft_mandates_are_the_research_drafts`.
   - `--stage`: a change that rewrites its own list (`test_a_stage_gets_the_base_commits_list_even_when_the_change_rewrites_it`);
     an unknown name, a missing `--stage` where the base has lists, a `--stage` on a base without lists, and a final
     review with a stage, each refused before any call; a final review without a list; a base without lists, said in
     the prompt and the start entry. 25 tests pass.
3. **Claims and what checks them mechanically.** "A change cannot rewrite the list it is reviewed against": the
   rewrite test. "Every question cites a researched source": the form test (it checks that the key exists, not that
   the source supports the question). "The code list repeats no coding rule": five phrases only. Not mechanical: that
   each quote is what its source says, that each question is specific to its type and answerable from the copy and
   the evidence, that the DPL mapping names the right stage, question and gate, and that no known class of defect
   passes every list. These are what this critique and 4.4's implementation review are for.
4. **Fixes and their upstream choice.** No reviewer findings yet. The author's own: the proof question first had
   different wordings in different lists, so the placement test could not find it; one wording now.
5. **Tried the way the next user runs it.** `--stage` was run through the launcher with the fake `claude` on a
   throwaway repository whose base holds lists; the benchmark's dry run built every case's prompt with the lists and
   the drafted mandates from this commit. No live review has used a list yet: the base has none.
6. **Where each rule lives.** `AGENTS.md`: the Start here row, per-stage blocking under "Review findings", and the
   "Stage checklists" bullet (the lists' use, `--stage`, the author's guideline, the learning loop). The lists in
   `docs/review_checklists/`. Why each item is in or out: `research.md`.
7. **What was removed, and its review.** Nothing is retired. The draft final-review and handoff lists of the plan
   draft were never written (S44-D1). Stage A's benchmark prompts stay as measured.

## Questions (a minimum, from the test plan)

1. *Lists:* is every question specific to its artifact type and answerable from the copy and the evidence, with at
   most 12 per list? Does a "Blocks at this stage" criterion let a requirement or a test defect through, or block
   what should not block?
2. *DPL mapping:* does every DPL entry name a question at the stage where the miss happened, or a reason why none,
   and the gate or computed evidence that now catches it, or "none" (S44-D9)?
3. *Citations:* do the quotes a question rests on support it? Is any clause of a paid standard used beyond its title?
4. *Author's guideline:* where does `AGENTS.md` say that an author reads the stage's list before writing that stage's
   artifact, and does the code list repeat a rule `make lint` or the coding rules already enforce?
5. *`--stage`:* can a review run without its list, or with a list the change itself wrote, and nothing shows it?
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 117->110, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_records.py: changed lines not run: 188; branches not taken: 187->188, 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 1418->1420 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_review_benchmark.py: changed lines not run: 295, 341, 616, 831, 835, 849, 1064, 1356-1357; branches not taken: 294->295, 298->297, 340->341, 615->616, 772->769, 778->772, 829->831, 848->849, 866->869, 1045->1043, 1204->1207, 1355->1356 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV7: no CI run for this commit (GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token))

A script the tooling tests run only as a subprocess shows as not run here, because coverage is measured in-process (issue #44).
No trace gap among the upstream items (python3 scripts/validate_traceability.py --mode pr --base <merge-base> --report-json <scratch>/trace.json --design-report-json <scratch>/design.json).
```


### Attempt critique/c1/r1/B/2

Reviewer `B`: `claude-sonnet-5-5`, effort high, mode initial, commit `0e0a201c783a`, base `3347754ef038`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
# Critique of slice 4.4's draft stage checklists and draft mandates (issue #41), reviewer B

## Intent

The approved plan and test plan are `docs/slices/poc-4-4-stage-checklists/plan.md` (decisions S44-D1 to S44-D13)
and `test_plan.md`, merged into `poc/agentic-sdlc` by plan PR #48 (the base of this review). Slice 4.4 researches
established review practice per artifact type and writes a short list of questions, with what blocks at that stage,
for each of six types: plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code.
The lists are in `docs/review_checklists/`; the research behind them, the mapping of the delivery problem log
(DPL-001 to DPL-011) to the lists, and the drafts of the three review mandates are in `research.md` of the bundle.
The launcher gains `--stage`, which gives a review its stage's list from the base commit. Each list is also the
author's guideline for its stage (S44-D8).

This review is the critique unit of S44-D10: two models review the draft lists and the draft mandates from
different angles, before 4.4's implementation review and before slice 4.5 measures the lists and the drafts in its
benchmark. The reviewed commit also holds slices 4.1 to 4.3 and 4.5's first part, each reviewed in its own unit;
4.4's own commit is `1750c8d`.

## Your angle (where to start, not where to stop)

Is the research behind the lists right, and are the lists usable? Check a sample of the quotes in `research.md`
against what the named public source could say, and flag any quote that its source would not hold or that does not
support the question it is tagged on; flag any use of a paid standard beyond its title. Check the DPL mapping: for
each of DPL-001 to DPL-011, is the stage the right one, would the named question really have caught the miss, and is
the named gate or computed evidence real? Check each question: is it specific to its artifact type (a question that
fits every type belongs to the mandate, S44-D3), can a reviewer answer it from the frozen copy and the evidence alone,
and does the code list repeat a rule that `make lint` or the coding rules of `AGENTS.md` already enforce (S44-D8)?
Check that each draft mandate sentence's tag and named failure mode fit what the source says.

## The author's self-review of slice 4.4 (claims to verify, not facts)

1. **Facts outside the repository, and how each was probed.**
   - The sources: every page `research.md` quotes was read on 2026-11-09 with a web-fetch tool; its Method section
     says how quotes were taken. Three sources could not be read and give no item: SEI CERT's page (the connection
     was reset on four attempts), INCOSE's summary sheet (HTTP 403; the guide itself is sold) and the ISTQB syllabus
     (a PDF no available tool could read); each section says so. Three paid standards (ISO/IEC/IEEE 29148, IEEE 1028, IEEE 1044) are cited by title only, and
     NASA's public checklist and ReqView's public 29148 templates stand in for the requirements sources.
   - The base has no lists: `git ls-tree -r --name-only origin/poc/agentic-sdlc docs/review_checklists` prints
     nothing, so every review of slice 4 runs with "No checklist at base <commit>", as S44-D7 says.
   - Reviewers have no web access (the launcher offers only Read, Grep and Glob), so every quote a list rests on is
     in `research.md` itself.
2. **Each check added or changed, the case it catches, and its test** (in `tests/tools/test_stage_checklists.py`).
   - A list without a title and purpose, with more than 12 questions, with an untagged question, a tag that names no
     source section, a DPL entry as a source, or no "Blocks at this stage" section:
     `test_every_list_has_the_agreed_form_and_cites_researched_sources`, and one negative case per kind in
     `test_the_form_check_fails_on_each_kind_of_violation`.
   - A list for a type the plan does not name, or a final-review or handoff list: `test_exactly_the_six_artifact_types_have_a_list`.
   - The two questions for what is missing in the wrong lists: `test_the_two_questions_for_what_is_missing_sit_where_the_misses_happen`.
   - A coding rule repeated in the code list: `test_the_code_list_repeats_no_coding_rule` (five phrases only).
   - A planned source without a section, or a paid standard not marked title only:
     `test_the_research_record_has_a_section_for_every_planned_source`, `test_a_planned_source_without_a_section_fails`.
   - A DPL entry left unmapped: `test_every_dpl_entry_is_mapped`.
   - A draft mandate sentence without a source tag or a named failure mode:
     `test_each_draft_mandate_sentence_has_a_source_and_names_its_failure_mode`, `test_a_draft_sentence_without_a_tag_fails_the_check`.
   - The benchmark measuring a mandate other than the research draft: `test_the_benchmarks_draft_mandates_are_the_research_drafts`.
   - `--stage`: a change that rewrites its own list (`test_a_stage_gets_the_base_commits_list_even_when_the_change_rewrites_it`);
     an unknown name, a missing `--stage` where the base has lists, a `--stage` on a base without lists, and a final
     review with a stage, each refused before any call; a final review without a list; a base without lists, said in
     the prompt and the start entry. 25 tests pass.
3. **Claims and what checks them mechanically.** "A change cannot rewrite the list it is reviewed against": the
   rewrite test. "Every question cites a researched source": the form test (it checks that the key exists, not that
   the source supports the question). "The code list repeats no coding rule": five phrases only. Not mechanical: that
   each quote is what its source says, that each question is specific to its type and answerable from the copy and
   the evidence, that the DPL mapping names the right stage, question and gate, and that no known class of defect
   passes every list. These are what this critique and 4.4's implementation review are for.
4. **Fixes and their upstream choice.** No reviewer findings yet. The author's own: the proof question first had
   different wordings in different lists, so the placement test could not find it; one wording now.
5. **Tried the way the next user runs it.** `--stage` was run through the launcher with the fake `claude` on a
   throwaway repository whose base holds lists; the benchmark's dry run built every case's prompt with the lists and
   the drafted mandates from this commit. No live review has used a list yet: the base has none.
6. **Where each rule lives.** `AGENTS.md`: the Start here row, per-stage blocking under "Review findings", and the
   "Stage checklists" bullet (the lists' use, `--stage`, the author's guideline, the learning loop). The lists in
   `docs/review_checklists/`. Why each item is in or out: `research.md`.
7. **What was removed, and its review.** Nothing is retired. The draft final-review and handoff lists of the plan
   draft were never written (S44-D1). Stage A's benchmark prompts stay as measured.

## Questions (a minimum, from the test plan)

1. *Lists:* is every question specific to its artifact type and answerable from the copy and the evidence, with at
   most 12 per list? Does a "Blocks at this stage" criterion let a requirement or a test defect through, or block
   what should not block?
2. *DPL mapping:* does every DPL entry name a question at the stage where the miss happened, or a reason why none,
   and the gate or computed evidence that now catches it, or "none" (S44-D9)?
3. *Citations:* do the quotes a question rests on support it? Is any clause of a paid standard used beyond its title?
4. *Author's guideline:* where does `AGENTS.md` say that an author reads the stage's list before writing that stage's
   artifact, and does the code list repeat a rule `make lint` or the coding rules already enforce?
5. *`--stage`:* can a review run without its list, or with a list the change itself wrote, and nothing shows it?
```

#### Evidence

```text
Each numbered entry must be listed under `accounted`.

EV1: scripts/check_docs.py: changed lines not run: 215; branches not taken: 214->215 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV2: scripts/check_review_records.py: changed lines not run: 43, 203-206, 210; branches not taken: 42->43, 117->110, 204->205, 204->206, 209->210 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV3: scripts/review_inputs.py: changed lines not run: 286; branches not taken: 285->286 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV4: scripts/review_records.py: changed lines not run: 188; branches not taken: 187->188, 189->191, 228->230 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV5: scripts/run_independent_review.py: changed lines not run: 166, 906, 964-965; branches not taken: 905->906, 1418->1420 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
EV6: scripts/run_review_benchmark.py: changed lines not run: 295, 341, 616, 831, 835, 849, 1064, 1356-1357; branches not taken: 294->295, 298->297, 340->341, 615->616, 772->769, 778->772, 829->831, 848->849, 866->869, 1045->1043, 1204->1207, 1355->1356 (python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch --cov-report=json:<scratch>/coverage.json)
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
      "note": "scripts/check_docs.py:215 is the 'cannot load check_review_records.py' return, a defensive branch for a missing file that the tooling tests never trigger. It fails closed with a message. It is not part of the 4.4 lists and I raised no finding.",
      "opened": [
        "scripts/check_docs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV2",
      "note": "Lines 43 and 203-206, 210 are the launcher-load failure and `main`/`__main__` of check_review_records.py, which the tests run as a subprocess (issue #44). Branch 117->110 and 204->205/206 are loop and exit paths. I read the visible ones and found them unremarkable. They sit outside 4.4's angle; CR-B8 covers the related recovery paths.",
      "opened": [
        "scripts/check_review_records.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV3",
      "note": "scripts/review_inputs.py:286 is `_link_user_site` returning when the user site-packages directory is absent. This is an environment-dependent path, harmless in effect, and not a fail-closed security path.",
      "opened": [
        "scripts/review_inputs.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV4",
      "note": "review_records.py:188 (`finish` raising on a missing section) and 228-230 (`truncate_unlogged_tail` dropping the '## Round' heading) are untested recovery logic; raised as CR-B8.",
      "opened": [
        "scripts/review_records.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV5",
      "note": "Line 166 is a load-failure branch. Lines 906 and 964-965 are the 'no review record' error and the swallowed ValueError in `_complete_record`; raised as CR-B8. The `--stage` code at 1593-1628 is not in the uncovered list, and test_stage_checklists.py exercises it.",
      "opened": [
        "scripts/run_independent_review.py"
      ],
      "status": "flagged"
    },
    {
      "item": "EV6",
      "note": "Lines 295, 341, 616, 831, 835, 849, 1064 and 1356-1357 in run_review_benchmark.py are skip, dedupe and refusal branches of the benchmark runner (4.5a). 831 and 849 are mentioned in CR-B8. The rest are minor, and the runner is not 4.4's subject. I read 290-300, 826-851 and 1350-1359 and did not open 341, 616 or 1064.",
      "opened": [
        "scripts/run_review_benchmark.py"
      ],
      "status": "explained"
    },
    {
      "item": "EV7",
      "note": "There is no CI run for this commit, so no CI job conclusion exists for any gate. Under AGENTS.md a gate's result is its CI job's conclusion; I did not run anything and cannot confirm the tooling tests or `make docs-check` pass. This is a process fact, not a defect in the change; it needs a pushed commit.",
      "opened": [],
      "status": "explained"
    }
  ],
  "findings": [
    {
      "evidence": "research.md:355 vs :37 (google-standard quote), :219 (verbosity bias quote), :236-239 (anthropic quotes), :371, :374; the test at tests/tools/test_stage_checklists.py:139-144 only checks that a tag key exists and that '\u2014 counters: ' is present. Searched research.md for any quote on anchoring or on admitting uncertainty and found none.",
      "failure_scenario": "Slice 4.5 measures these wordings and the owner picks the final mandate 'by reason'. The reasons shown as sourced are not supported by the sources, so a wording is kept or dropped on a false basis, and the claim 'each sentence carries its source and names the failure mode it counters' (S44-D13) overstates what the research shows.",
      "file": "docs/slices/poc-4-4-stage-checklists/research.md",
      "id": "CR-B1",
      "kind": "defect",
      "line": 355,
      "origin_stage": "discovery",
      "problem": "Several draft-mandate sentences carry a source tag that does not support the failure mode they name. Initial 1 cites google-standard, whose rule is to favour approving once a change definitely improves the code ('even if the CL isn't perfect'), against the failure 'approving because it looks like an improvement'. Initial 6 cites zheng-judge, whose verbosity bias is a judge preferring longer answers, not a reviewer padding its own report. Recheck 3 cites anthropic-prompting for 'say cannot determine'; no quoted line speaks to admitting uncertainty. Final 1 ('anchoring on earlier verdicts') has no source that treats anchoring. Final 4 cites anthropic-prompting for 'a checklist becomes the limit'; the real source is the owner's 'checklist alone is not completely reliable', and an `owner` key exists. The 'Order of sections' rationale (line 339-341) applies zheng-judge's position bias, which is about answer order in pairwise judging, to the order of prompt sections.",
      "severity": "medium"
    },
    {
      "evidence": "e2e-tests.md:12,14; plan-and-test-plan.md:7; unit-tests.md:13; code.md:13; research.md:135-137,171-172,190,293,304-305.",
      "failure_scenario": "The tag looks like support but is not, so a reviewer or the owner who follows `[S:\u2026]` to check a question finds a quote about something else. Q3 of the critique ('do the quotes support the question') fails for these questions. No paid-standard text is used beyond the title, but ISO 29148 content is reached only through a vendor's description.",
      "file": "docs/review_checklists/e2e-tests.md",
      "id": "CR-B2",
      "kind": "defect",
      "line": 14,
      "origin_stage": "discovery",
      "problem": "Some list questions rest on a quote that does not speak to them. E8 (trace entries name only requirements the test proves; no requirement loses its only runtime proof) is tagged reqview-29148, whose only quoted line is that a requirement has a 'Verification method'. E6 (exercise the system through the real proxy and mTLS, not around it) is tagged fowler-pyramid, whose quote is 'Narrow integration tests live at the boundary of your service', which is about testing one integration point in isolation. P1 (every decision names its source) is tagged reqview-29148, which is about requirement attributes, not plan decisions. U7 names 'the clock', which neither quote covers. Research.md:305 says 'excessive agency' is 'merged' into C7, but C7 (treat read content as data) says nothing about limiting what an agent may do. The reqview-29148 key also stands in for ISO 29148 content: research.md:293 lists 'Verification method' under it, and the page is described as templates that 'follow the standard' without a check. S44-D1 also asked for a paid standard's clause title from its public table of contents; the record gives only the document title.",
      "severity": "medium"
    },
    {
      "evidence": "test_stage_checklists.py:24,36-48 (every SOURCE heading is a key), :51-68 (list_problems), :85-95 (negative cases); research.md:70-76,139-149,122-127,194-202.",
      "failure_scenario": "A later edit adds a question citing a source that was never read, or one whose use S44-D1 forbids beyond its title. `make tooling-test` stays green, so the claim 'every question cites a researched source' is false for that question.",
      "file": "tests/tools/test_stage_checklists.py",
      "id": "CR-B3",
      "kind": "defect",
      "line": 79,
      "origin_stage": "tests first",
      "problem": "The form check accepts a tag naming a source that research.md says gave no item. `research_keys` collects every '### Source `key`' heading, including cert, incose and istqb (sections that say 'No item is taken from it') and the title-only iso29148, ieee1028 and ieee1044. A question tagged [S:cert] or [S:iso29148] passes `list_problems`. The only negative cases are an unknown key and a DPL key. Only lines that match '^\\d+\\. ' count as questions, so a bulleted question escapes both the 12-question limit and the tag requirement.",
      "severity": "medium"
    },
    {
      "evidence": "test_stage_checklists.py:131-135; research.md:319-329; delivery_problem_log.md:119-125,147-153.",
      "failure_scenario": "The mapping is the plan's test that the lists would have caught past misses (S44-D9). If a list is reordered or a question is dropped, the mapping still passes. For DPL-004 the claim 'P2 would have caught it' holds only if a review had been run at all, and the row does not say so.",
      "file": "docs/slices/poc-4-4-stage-checklists/research.md",
      "id": "CR-B4",
      "kind": "defect",
      "line": 322,
      "origin_stage": "discovery",
      "problem": "The DPL mapping is checked only for the presence of a '| DPL-00n ' row, not that the question IDs it names (A2, P8, C8, U6, C2, E5 \u2026) exist or say what the row claims. Renumbering a list leaves the mapping stale and green. DPL-004 is mapped to P2/R5, but the log's root causes are that a late plan cut was never re-reviewed and that the review was anchored to a plan that already had the gap. The question asks what a re-review would ask, not why none happened; the row does not say so. DPL-005 maps to P3/C10, which ask whether the job is 'required'. The ruleset is outside the repository (DPL-005 root cause 4), so only `make gate-consistency` and the CI evidence can show it.",
      "severity": "low"
    },
    {
      "evidence": "docs/slices/README.md:20; AGENTS.md 'Start here' row for docs/review_checklists/ and the 'Stage checklists' bullet; grep of docs/STATUS.md for '4.4', 'checklist' and 'lists' finds only the issue list at lines 12 and 31.",
      "failure_scenario": "A reader of the index or STATUS.md believes 4.4 has not started while AGENTS.md tells them to use its lists. An agent starting 4.4 again, or 4.5b measuring 'the lists', works from the wrong state.",
      "file": "docs/slices/README.md",
      "id": "CR-B5",
      "kind": "defect",
      "line": 20,
      "origin_stage": "implementation",
      "problem": "The slice index row for 4.4 says 'Plan merged (PR #48); not started', but this commit adds the six lists, research.md, the `--stage` launcher change, its tests, and AGENTS.md rules that call the lists authoritative. The close-out step requires updating the slice's row and docs/STATUS.md; STATUS.md names no 4.4 progress either. The same commit moves the rows of 4.1, 4.2, 4.3 and 4.5 to 'implemented \u2026 in review'.",
      "severity": "medium"
    },
    {
      "evidence": "run_independent_review.py:1604-1622,1725; grep of scripts/check_review_records.py for 'stages|checklist' finds nothing.",
      "failure_scenario": "An honest slip (--stage code on an E2E change, or only unit-tests for a tests-first review) runs, is logged, and no gate or reviewer notices; the review has the wrong minimum. Q5 of the critique: a review can run with the wrong list and nothing shows it.",
      "file": "scripts/run_independent_review.py",
      "id": "CR-B6",
      "kind": "defect",
      "line": 1604,
      "origin_stage": "implementation",
      "problem": "`--stage` takes any name that exists at the base. Nothing ties the name to the unit or the paths, so a review can run with a wrong list, or with only one of the two that AGENTS.md says the tests-first stage takes (unit-tests and e2e-tests). A recheck may also be started with different `--stage` values than round 1 without a signal. The start entry records the stages, but `check_review_records.py` reads neither `stages` nor `checklist_sha256`.",
      "severity": "low"
    },
    {
      "evidence": "code.md:11,12; e2e-tests.md:11,15; unit-tests.md:10; AGENTS.md coding rules 1, 6, 8 and the gates table; test_stage_checklists.py:110-113; research.md:267,320.",
      "failure_scenario": "The lists carry questions that cost reviewer attention for checks a tool already makes, and the test that guards this rule cannot detect it.",
      "file": "docs/review_checklists/code.md",
      "id": "CR-B7",
      "kind": "defect",
      "line": 9,
      "origin_stage": "discovery",
      "problem": "Several questions repeat what a gate or coding rule already enforces, which S44-D8 and S44-D9 say a question should not do. C6 'names say what each part does' repeats coding rule 8, last sentence. C4 'disclosing nothing sensitive' repeats coding rules 1 and 6. E9 'a guard accepts several outcomes' is the rule `make test-lint` enforces. E5 duplicates the `make qa-evidence` secret check, and research.md:320 names that check as the gate for DPL-002. U4 overlaps `make unit-guard-check`. `test_the_code_list_repeats_no_coding_rule` checks five absent phrases only, so a reworded repeat passes.",
      "severity": "low"
    },
    {
      "evidence": "EV4, EV5, EV6; scripts/review_records.py:187-191,228-230; scripts/run_independent_review.py:962-965; scripts/run_review_benchmark.py:849.",
      "failure_scenario": "A launcher killed mid-write leaves a record the recovery path mishandles, and the swallowed ValueError hides it until the record check runs. This is the DPL-010 pattern (untested refusal paths).",
      "file": "scripts/review_records.py",
      "id": "CR-B8",
      "kind": "defect",
      "line": 228,
      "origin_stage": "implementation",
      "problem": "Evidence entries EV2, EV4, EV5 and EV6 show fail-closed or recovery paths with no tooling test: `truncate_unlogged_tail` removing the '## Round' heading (228-230), `finish` refusing a missing section (188), `_complete_record` swallowing that ValueError (run_independent_review.py:964-965), the 'stage A is closed' refusal (run_review_benchmark.py:849), and the 'cannot load' branches. These belong to 4.1\u20134.3 and 4.5a and not to 4.4's lists, which are covered.",
      "severity": "low"
    }
  ],
  "verdict": "yes"
}
```


#### Answers to critique/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| C-1 | blocking | fixed: docs/slices/poc-4-4-stage-checklists/research.md, tests/review_benchmark/prompts/mandate_recheck_b.md: the draft recheck mandate's second sentence now accepts what the review loop lets a recheck accept: a `fixed:` answer whose named files do what the finding asked, a `rejected:` answer whose reason checks out in the copy, and a `deferred:` or `owner:` answer that names where the finding is tracked or decided; otherwise it re-raises the finding with what it saw. The origin was a draft written for the false-fix case only; the other drafts were checked against the review loop for the same cause, and none restricts what may be accepted. The round-2 rule for new findings is a plan-review rule (`AGENTS.md`, Plan review), which the prompt's approved rules carry; sentence 4 does not contradict it. The draft has not run yet, so the benchmark measures the corrected text |
| C-2 | high | owner: docs/slices/agentic-sdlc-poc/slice_4_decisions.md: decision concern 4. S45-D5 fixes one recheck case, a false `fixed:`; the benchmark report will say that the recheck comparison measures only the acceptance of a false fix, not the re-raising of answers that hold. Recommendation: before choosing the recheck wording, run a second recheck case with a correct rejection (2 more runs, within the 60) |
| C-3 | high | fixed: docs/review_checklists/code.md, docs/review_checklists/e2e-tests.md, docs/slices/poc-4-4-stage-checklists/research.md: code question 11 asks whether every statement the change adds to or leaves in a document (STATUS, the logs, the rulebook, the slice index, a review record, the PR body) still holds for the copy, and E2E question 10 whether each `docs/test_spec.md` entry says what the test really does; both rest on Google's documentation item, quoted in the research record. The DPL mapping now names C11 for DPL-001, DPL-006 (where the claim is in a document), DPL-009 and DPL-010 |
| C-4 | medium | fixed: docs/slices/README.md: 4.4's row says it is implemented on the slice 4 branch, critiqued and in review. The implementation log gets one dated entry for slice 4 at its close-out, in the same final PR, as 4.1 to 4.3 will (none of them has one yet) |
| C-5 | high | fixed: docs/review_checklists/unit-tests.md, docs/slices/poc-4-4-stage-checklists/research.md: unit-test question 10 asks whether each fake, stub or mock behaves like the real dependency in what the test relies on, as a recorded probe or a contract test shows, and whether each check gets the kinds of input it will meet in use. Its source is the test-pyramid article's section on integration with separate services (quoted, read 2026-11-10). The DPL mapping names U10 for DPL-010 RC3 and for DPL-011 RC2 and RC3 |
| C-6 | high | fixed: docs/review_checklists/code.md, docs/review_checklists/e2e-tests.md, docs/slices/poc-4-4-stage-checklists/research.md: code question 12 and E2E question 11 ask whether the change loosens, skips or excepts an existing check or guard (a lower threshold, an exception or gap entry, a lint or `alternate` marker, a removed negative control or case), and whether each says why and until when. The source is Fowler's quarantine section (a quarantined test no longer helps regression coverage and must not stay too long), quoted. DPL-004's mapping names C12 |
| C-7 | medium | fixed: docs/review_checklists/code.md, docs/slices/poc-4-4-stage-checklists/research.md: code question 1 now asks whether the change does what the plan decided, and nothing the plan did not decide, before the design question; the research record quotes Google's "Does this CL do what the developer intended?" |
| C-8 | medium | fixed: docs/review_checklists/plan-and-test-plan.md, docs/slices/poc-4-4-stage-checklists/research.md: plan questions 10 (each new check or step states its failure, cost and simpler alternative, and solves a problem known now), 11 (the plan states its threat model, and a change to it goes to the user) and 12 (hidden state and retirement), each with a quoted source (Google's complexity and documentation items, OWASP's threat model kept alongside the system and its data stores); a change to the approved threat model without the user's approval now blocks at this stage. The list has 12 questions, the limit |
| C-9 | medium | fixed: AGENTS.md: a finding blocks by the "Blocks at this stage" section of a checklist the review received (its `--stage`). The scenario's test that passes while the behaviour is broken is a false green, which blocks at every stage by `AGENTS.md`'s first criterion, whatever list the review got. Which lists each stage's review takes is S46-D1, written into `AGENTS.md` by 4.6 (implementation: the code list; tests first: the unit-test and E2E lists) |
| C-10 | medium | fixed: docs/slices/poc-4-4-stage-checklists/research.md, tests/review_benchmark/prompts/mandate_initial_b.md: (1) initial sentence 1 now counters approving a change that improves the system overall while a part of it still holds a defect, which `google-standard`'s rule against changes that worsen code health supports; (2) sentence 6 rests on `conventional-comments` (a preference never blocks) instead of the judge's verbosity bias; (3) recheck sentence 4 rests on `google-standard`'s reviewer ownership; (4) the order of sections says position bias was measured for answers compared in pairs, not prompt sections, so the order is a reasoned default |
| C-11 | medium | fixed: docs/review_checklists/code.md: the code list's Blocks section now also blocks a new or changed check or gate with no test that shows it failing on the case it exists to catch, which a read-only reviewer can observe; DPL-009's mapping names it |
| C-12 | low | fixed: docs/review_checklists/unit-tests.md: U7 now excludes the repository files a test exists to check. U9 and C6 stay: boundary values are this repository's own test rule (`tests/unit/AGENTS.md`), and S44-D8 names "whether a name says what it does" as part of the code list |
| C-13 | low | fixed: docs/slices/poc-4-4-stage-checklists/research.md, tests/review_benchmark/prompts/mandate_initial_b.md: initial sentence 5 now reads "what the copy or the evidence supports: a file and line, an evidence entry, or what you searched for and did not find" |
| C-14 | high | fixed: tests/tools/test_check_review_records.py: `test_an_acceptance_in_a_next_round_attempt_that_did_not_complete_settles_nothing` puts an accepting Report block into a failed next-round attempt's section; the check still reports the rejected blocking finding as unsettled, and the test fails when the condition is loosened to `or` (checked by editing the check) |

#### Answers to critique/c1/r1/B/2

| ID | Severity | Answer |
| --- | --- | --- |
| CR-B1 | medium | fixed: docs/slices/poc-4-4-stage-checklists/research.md, tests/review_benchmark/prompts/mandate_initial_b.md: the same cause as reviewer A's C-10, fixed there for initial sentences 1 and 6 and the order of sections; in addition recheck sentence 3 now rests on `owasp-llm`'s human oversight (a `cannot determine` goes to the owner), final sentence 1 on `google-standard`'s reviewer ownership, and final sentence 4 on the owner's words, which the `owner` section now quotes ("checklist alone is not completely reliable"; the final review gets "no question list") |
| CR-B2 | medium | fixed: docs/slices/poc-4-4-stage-checklists/research.md, docs/review_checklists/e2e-tests.md: E8 also cites the owner's proof question, and its candidate row says why a requirement that loses its only proof loses its verification method; E6's row now rests on the end-to-end test quote (the proxy and its mutual TLS are the application's boundary); P1's row says a plan decision carries a source as a requirement does; U7's clock is quoted from Fowler's Time section (read 2026-11-10); excessive agency is no longer said to be merged into C7 (the launcher limits the reviewer's tools); `reqview-29148` says that its claim to follow the standard was not checked. Clause titles: S44-D1 asks for paid standards by title only, and ISO's catalogue page refused the fetch, as its section says |
| CR-B3 | medium | fixed: tests/tools/test_stage_checklists.py: a question may cite only a source that gave something, so a tag naming `cert`, `incose`, `istqb`, `iso29148`, `ieee1028` or `ieee1044` fails, and a line under "Questions" that is not a numbered question fails; a negative case for each (`source-that-gave-nothing`, `title-only-standard`, `bulleted-question`) |
| CR-B4 | low | fixed: tests/tools/test_stage_checklists.py, docs/slices/poc-4-4-stage-checklists/research.md: every question ID that the candidate table or the DPL mapping names must exist in its list, with a negative case; DPL-004's row says its questions would have caught it only had the cut been reviewed; DPL-005's row says that whether a job is required lives in the ruleset, which only `make gate-consistency` and 4.2's CI evidence show |
| CR-B5 | medium | fixed: docs/slices/README.md, docs/STATUS.md: 4.4's row and STATUS's slice-4 item now say where slice 4 stands (the same row as reviewer A's C-4) |
| CR-B6 | low | rejected: S44-D7 has the author name the stage, and 4.6 (S46-D1) writes into `AGENTS.md` which lists each stage's review takes; the start entry and the record's Prompt block show which list a review got. A check tying `--stage` to the unit or the paths would be a new check, which needs the owner's approval ("Ask before growing") |
| CR-B7 | low | fixed: docs/review_checklists/code.md: C4 no longer repeats coding rules 1 and 6 ("disclosing nothing sensitive" removed). The rest stay: S44-D8's rule against repeating tools is for the code list only, and S44-D8 itself names "whether a name says what it does" (C6) as part of the code list; E9 asks about guards that `make test-lint`'s patterns cannot see |
| CR-B8 | low | fixed: tests/tools/test_check_review_records.py, tests/tools/test_run_review_benchmark.py: tests for recovery removing the round heading written with its first unlogged section, for `finish` refusing a record without the attempt's section, and for `--run` refusing stage A. The launcher's recovery catches that refusal on purpose: a missing section is left to the record check, which reports it (`_complete_record`'s docstring) |
