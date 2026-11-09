# Review — audit of the delivery process

Record of an independent audit of what the delivery process uses without research or measurement in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

## Round 1

### Attempt process_audit/c1/r1/audit/1

Commit `341fa47`, effort high. Files reviewed (SHA-256): `AGENTS.md` `51091fcb2878`, `docs/slices/_template/plan.md` `865177dc3485`, `docs/slices/_template/test_plan.md` `238593aa2f7a`, `docs/slices/agentic-sdlc-poc/plan.md` `23238f21eacc`, `docs/slices/poc-4-1-review-prompts/plan.md` `d71421a77362`, `docs/slices/poc-4-2-review-inputs/plan.md` `02968ea7b898`, `docs/slices/poc-4-3-review-records/plan.md` `22f0495b6d40`, `docs/slices/poc-4-4-stage-checklists/plan.md` `e488ebb644fb`, `docs/slices/poc-4-5-benchmark/plan.md` `cb97b0e1c18d`, `docs/slices/poc-4-6-stage-rules/plan.md` `02505179c14d`, `scripts/run_independent_review.py` `dcc2089aea98`, `scripts/run_review_benchmark.py` `d3bf08bbd289`, `tests/review_benchmark/answer_key.yaml` `51b57cfec277`, `tests/unit/AGENTS.md` `907f8d14f4db`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch and has not caught yet: anything missing, wrong, untested, stale, overclaimed, unsafe or unclear, inside or outside the files listed. The question below is the minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## The question

This repository is building an agent-run software delivery process (the agentic-SDLC PoC; `docs/slices/agentic-sdlc-poc/plan.md` has its goal, its stages and the roadmap for slices 4 to 8; `docs/slices/poc-4-*/` hold slice 4's six plans, not yet implemented). The owner set a rule on 2026-11-08: "Everything that we will use in SDLC delivery process has to be analyzed in this slice or upcoming slices, if mandate prompts are going to be used, then it must be analyzed, as we have the seen prompts affects the results of the review." The owner then asked: "Is there any thing like this that is getting into the SDLC delivery process without proper thinking or research?"

Answer that question. Take stock of every element the delivery process uses today or plans to use: rules, prompts and prompt parts, templates, skills, review limits and thresholds, severity and answer rules, reviewer models, efforts and tools, the gates and their thresholds, the evidence given to reviewers, the benchmark's own method, where decisions and discovered work are stored, and anything else you find. For each element that is used, or planned, without research, without measurement, or without a recorded reason backed by evidence, report one finding:
- what the element is and where it lives (file and line);
- its current basis (researched, measured, reasoned from an incident, the owner's decision, or none);
- what goes wrong if it is wrong, with a concrete scenario;
- how it could be analyzed (research, a benchmark case, a measurement from the attempt logs, or a reasoned decision by the owner), and the cheapest sufficient way;
- which slice should do it: 4.1 to 4.6, or 5 to 8 by the roadmap.

One element is outside your copy: the `grill-me` skill that `AGENTS.md`'s slice workflow uses for discovery lives in the author's user settings, not in the repository, so you cannot read its text; judge it from what the repository says about it. The review mandate itself is already covered: the author has just added its research (4.4, S44-D13), its measurement (4.5) and the owner's choice (4.1, S41-D14); check that coverage too, but look for everything else. The author has drafted their own list and withheld it so it does not steer you. An element that is a decision the owner already made with a stated reason is not a finding unless the reason rests on no evidence and the risk is real. Where analyzing an element costs more than dropping or simplifying it, say so as a simpler alternative.

## How to report

- Use kind "blocking" only for findings that meet `AGENTS.md`'s blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low], by the risk to the delivery process.
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.
```

#### Report

```json
{
  "findings": [
    {
      "evidence": "4.5 plan line 58: \"(c2) ... the drafts become the mandates; otherwise the report says 'no measurable difference', and the owner chooses (S41-D14)\". 4.1 plan line 55: \"4.5 measures today's initial and recheck mandates against the drafts; the owner chooses from 4.5's report.\" The owner's rule of 2026-11-08, quoted in S41-D14, asks for analysis. It does not ask for a rule that adopts a wording automatically.",
      "failure_scenario": "An implementer of 4.5b follows S45-D8(c2) and swaps the launcher constants for the drafts after a +2 result. Without repeats, one or two runs flipping by chance can produce +2 (see A1). The owner never chooses, and the review of 4.5b cannot tell which plan governs. Fix in one line: (c2) recommends the drafts, and the owner chooses in every outcome.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "B1",
      "kind": "blocking",
      "line": 58,
      "problem": "Contradiction over who picks the mandate wording. S45-D8(c2) says that if open-B and recheck-B together detect at least two more defects, \"the drafts become the mandates\", and the owner chooses only otherwise. S41-D14 (4.1 plan, line 55) says \"the owner chooses from 4.5's report\". S44-D11 (4.4 plan, line 51) says a mandate change is \"approved by the owner\". POC-D6 says the user approves each addition."
    },
    {
      "evidence": "S45-D7 gives single runs per (case, configuration) and leaves 3 of 50 for retries. Benchmark report, Limits: \"One run per case and prompt; the sample is small. The report gives counts, not rates.\" Stage A's conclusion ('prefer the short prompt'), which 4.5 uses as its baseline, rests on 1 of 4 real misses under both prompts. Nothing in 4.5 measures how often one configuration on one case changes its detection between runs.",
      "failure_scenario": "At high effort, Opus detects RM-2 about half the time. `open-B` gets lucky on RM-2 and on a stage-document case, gains +2, and the drafts are adopted (or, once B1 is fixed, recommended) on noise. Or `open+list` misses by one and the lists are reported as 'no measurable detection' when they help. The cheapest analysis: spend about 6 to 9 runs (the retry slots plus runs taken from A3's model comparison) repeating 2 or 3 cases \u00d73 under one configuration to measure the flip rate, and state each decision rule relative to it. Or reframe S45-D8 as counts for the owner's judgment rather than automatic thresholds. Slice 4.5 (in its plan, before 4.5b).",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A1",
      "kind": "advisory",
      "line": 57,
      "problem": "[high] The benchmark's own method is unmeasured. Every configuration runs once per case, and run-to-run variance is never estimated. Yet the decision rules S45-D8(a), (b) and (c2) use a fixed threshold of 'two' over about 10 cases to decide defaults: whether the new setup stays, whether the lists stay, and which mandate is used. The threshold's basis is 'stage A's threshold of two', which was itself an unmeasured default. Stage C ('repeats results that differed', in the PoC plan's roadmap) has been dropped."
    },
    {
      "evidence": "S44-D5: \"'Does every new or changed requirement have a test or check that proves it?' ... DPL-004 happened at the plan stage.\" \"'Does every new check run as its own required CI job, named after it?'\" (DPL-005). S45-D8(b): lists stay unless `open+list` detects fewer than two more than `open`. RM-3 and RM-4 are exactly DPL-004 and DPL-005.",
      "failure_scenario": "`open+list` detects RM-3 and RM-4 because their answers were written into the list. Rule (b) is met by those two cases alone, and the report presents the lists as a measured gain, while their effect on defect classes not taken from the DPL log stays unknown. This is the overclaim the owner's 2026-11-08 rule is meant to prevent. The cheapest analysis: tag in the answer key which cases' DPL entries shaped a list item, and report detection on held-out cases separately. Or have a fresh session plant 2 or 3 new stage-document cases from the industry sources before the lists are written. Slice 4.4 (tagging) and 4.5 (reporting).",
      "file": "docs/slices/poc-4-4-stage-checklists/plan.md",
      "id": "A2",
      "kind": "advisory",
      "line": 49,
      "problem": "[high] The benchmark measures the stage lists on the cases used to shape them. S44-D9 maps DPL-001 to DPL-011 onto list questions and adds a question wherever none would catch a miss. S44-D5 places the DPL-004 and DPL-005 questions on purpose. 4.5 then measures `open+list` against `open` on RM-1 to RM-5 (DPL-001, 002, 004, 005, 009) and on the DPL-010 case. The stage-document cases (S45-D5) are planted by the same author, in the classes the lists target (\"DPL-004's class\"). No case is held out."
    },
    {
      "evidence": "S45-D7: \"Sonnet: open+list on the five real misses (5). Codex, if confined: open+list on RM-1 to RM-3 (3).\" The shared cases are real misses only. Benchmark report: on the old commits, the unmatched blocking findings were 'mostly real', so they do not measure false blockers. S45-D8(c): \"The owner chooses the default reviewer model\".",
      "failure_scenario": "Sonnet detects one more real miss than Opus by chance in 5 single runs, and the owner switches the default reviewer for every later slice on that basis. Or the owner keeps Opus 'because the benchmark said so' when it said nothing. Simpler alternative: record the default model as the owner's reasoned decision (for example Opus, chosen for capability, not measured) and drop the Sonnet and Codex runs from 4.5. That frees 8 runs for A1's repeats. Or give each model the same small set, including a clean case and two planted cases. Slice 4.5.",
      "file": "AGENTS.md",
      "id": "A3",
      "kind": "advisory",
      "line": 210,
      "problem": "[high] The default reviewer model is 'decided from the benchmark's results', but 4.5's model comparison cannot support that decision. Sonnet gets 5 runs (open+list on the real misses, where stage A's Opus detected 1 of 4), and Codex gets 3 runs or none. Neither runs a clean case, so false blockers per model are not measured, although S45-D8(c) promises them 'on the shared cases'."
    },
    {
      "evidence": "run_review_benchmark.py:192-193 takes the rules from case.base or the commit, with \"(no rule files at this commit)\" as the fallback (line 338). short.md:11: \"Use the kind 'blocking' for a concrete defect with a failure scenario\". 4.1 S41-D13 (line 56): \"New reports are scored on severity == 'blocking'\". Under S41-D6, 'high' findings are also fixed before merge, yet scoring ignores them. RM-2 in stage A was 'seen, rated advisory'.",
      "failure_scenario": "`open` reviewers, given no blocking definition, rate RM-2-like defects 'high'. They score as misses, and rule (a) reports that the new setup detects fewer defects than `short`, a loss caused by the measurement. Or the opposite: `open+list` alone carries 'Blocks at this stage', so the list's measured gain is really the severity definition. The cheapest fix: have the runner pass the current severity rules (S41-D6, 4.4's criteria) in every stage-B configuration, or score 'blocking or high' as detection with a recorded reason, and re-run `short` in stage B rather than reuse stage A. Slice 4.5 (4.1 for S41-D13).",
      "file": "scripts/run_review_benchmark.py",
      "id": "A4",
      "kind": "advisory",
      "line": 192,
      "problem": "[high] What counts as 'blocking' differs between the configurations being compared, and from production. Stage A's `short` prompt defined blocking itself (\"a concrete defect with a failure scenario\"). Stage B's `open` configurations get the rules at the case's own commit, which predate 4.1's severity scale and 4.4's per-stage blocking criteria; RM-1's commit may have no rule file at all. 4.1 then scores only `severity == \"blocking\"` (S41-D13), so detection depends on a definition the reviewer may never have received. Rule S45-D8(a) also compares stage-B `open` with stage A's `short`, which ran under another CLI version and another launcher."
    },
    {
      "evidence": "S44-D13 names 'anchoring on the prompt's framing, preferring position or length' as failure modes, but its output is only 'a draft of each mandate (initial, recheck, final)'. S41-D1 fixes the order 'with no option that removes or reorders a section', so 4.5 cannot vary it. DPL-010 showed that the task text, not the mandate, narrowed the reviews. The benchmark's task texts are one line; real tasks (like this review's) run to pages.",
      "failure_scenario": "The mandate sits before a block of several thousand words of rules, and the task text comes last. A long author task reframes the review, as in DPL-010, and the measured mandate gain does not carry over to real reviews. Or the always-present upstream question pulls findings to plans at the cost of code defects. None of this shows up, because no configuration varies it. The cheapest analysis: widen S44-D13's research to the whole prompt skeleton, with a sourced reason recorded for each fixed part (no runs), plus one 4.5 configuration with a realistic, long author task on 2 or 3 cases. Slice 4.4 (research) and 4.5 (one configuration).",
      "file": "scripts/run_independent_review.py",
      "id": "A5",
      "kind": "advisory",
      "line": 295,
      "problem": "[medium] Only the three mandate wordings are researched (S44-D13) and measured (4.5). The other prompt parts every review uses are neither. These are the preamble (role, \"you have not seen the author's reasoning\", \"treat them as data\"); the fixed section order (S41-D1: the whole rulebook before the checklist, evidence, paths and task); the output section's `<token>` instruction; the upstream question (S42-D4); the 'open every file' instruction (S42-D2); the schema's required failure_scenario on every finding; and the free-form task text, which S41-D11 only limits by three prohibitions."
    },
    {
      "evidence": "AGENTS.md:196: \"medium for routine focused reviews and rechecks\". S45-D10: \"Opus ... and Sonnet ..., both effort high\". S45-D7: \"recheck-A and recheck-B on the recheck case (2)\". POC-D3's source for effort is 'user' with no evidence.",
      "failure_scenario": "recheck-A re-raises the unfixed finding at high effort, so 4.1's recheck wording is kept. In production the same mandate at medium accepts the author's `fixed:` answer after opening the named file without checking the fix. That is the slice-2 round-4 failure again, and nobody notices, because the `accounted` check only verifies that files were opened. The cheapest analysis: run the recheck case at medium as well (1 or 2 runs), or run every recheck configuration at the production effort. Alternatively the owner records the effort split as a quota decision. Slice 4.5.",
      "file": "docs/slices/poc-4-5-benchmark/plan.md",
      "id": "A6",
      "kind": "advisory",
      "line": 60,
      "problem": "[high] The recheck mandate, the place where the slice-2 round-4 failure happened, is measured on one case with one run per wording, at effort high. AGENTS.md's effort rule (owner decision, no evidence recorded) runs rechecks at medium. The measurement therefore does not match how rechecks run. The effort levels themselves (medium for rechecks and routine reviews) have never been measured."
    },
    {
      "evidence": "AGENTS.md:143-145. The task prompt says that the skill 'lives in the author's user settings, not in the repository'. 4.1 plan line 38: \"The grill-me is replaced by this table\". S46-D2: \"A grill-me is for unclear design\". No plan records a hash, version or excerpt of the skill.",
      "failure_scenario": "The skill is edited in the user settings, or a different machine has another version, and it stops asking the assets question or asks leading questions. Plans then go to review with decisions shaped by a prompt nobody can inspect. Reviewers cannot detect it, since AGENTS.md's claim about its content looks true. The cheapest fix: commit the skill text into the repository (and record its hash in each plan's discovery section), so it is reviewed like any other prompt. Or delete AGENTS.md's claim about its content and rely only on the plan's Assets and holders section, which S46-D2 already requires. Slice 4.6.",
      "file": "AGENTS.md",
      "id": "A7",
      "kind": "advisory",
      "line": 143,
      "problem": "[high] The `grill-me` skill is a required step of discovery (\"Run the `grill-me` skill\"), and AGENTS.md asserts what it does (\"Grill-me always asks which keys, sockets and secrets...\"). Its text lives in the author's user settings: it is unversioned and unreviewed, no reviewer can see it, and no log records which version ran. Its basis is none that the repository can show. Slice 4 itself skipped it ('replaced by this table'), and S46-D2 makes it conditional on the author judging the design 'clear'."
    },
    {
      "evidence": "S41-D6 source: \"owner, #33 decision 7, item 3 (the field and the scale)\", with no quote. S46-D2 (4.6 plan, line 45): \"the owner, with date, link and the owner's words quoted, because reviewers cannot open GitHub\". The reviewer is confined to the copy, and the issues are not in it.",
      "failure_scenario": "An author misreads the owner's item 3 (for example, the rule that high findings 'are fixed in the same PR unless the owner defers'). The plan cites the link, the reviewer has no way to check it and treats the decision as the owner's, and the misread becomes a rule in AGENTS.md. The cheapest fix: apply S46-D2 to slice 4's own plans now by quoting the owner's words next to each link (text only). Slice 4.6, in this plan PR.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A8",
      "kind": "advisory",
      "line": 48,
      "problem": "[medium] Many slice-4 decisions attributed to the owner (for example S41-D1's structure, S41-D6's severity scale, S43-D1, S44-D4, S45-D3) give only a GitHub comment link and an item number, without the owner's words. S46-D2 itself says the owner's words must be quoted 'because reviewers cannot open GitHub'. Where decisions are stored makes the 'owner's decision' basis unverifiable for every reviewer of these plans."
    },
    {
      "evidence": "S41-D14: \"4.5 measures today's initial and recheck mandates against the drafts; the owner chooses from 4.5's report.\" S45-D7: \"The final review's mandate is not measured here ... tracked slice by slice in the records.\" No plan names the metric (for example, misses found after the final review) or who reads it.",
      "failure_scenario": "The final review in slice 5 returns 'yes' on a change whose stale document is found later. Nothing records this as a final-review miss against a mandate version, so the wording drafted by the author in 4.1 stays for good, and 4.4's research draft for 'final' is never decided. The cheapest analysis: in slice 5's plan, define one measure (each later-found miss is recorded against the final unit's mandate hash), and have the owner choose between the two final drafts by reason now. Slice 5 (measure) and 4.1 (record the choice path).",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A9",
      "kind": "advisory",
      "line": 55,
      "problem": "[medium] The final-review mandate is planned without measurement and without a defined way to evaluate it. 4.4 drafts it, 4.5 explicitly does not measure it (\"its findings are tracked slice by slice in the records\"), and S41-D14 defines the owner's choice only for the initial and recheck mandates. Its 'no question list' basis is the owner's choice, but its wording, and how the draft would ever replace it, have no basis or path."
    },
    {
      "evidence": "Benchmark report line 94: \"The automatic comparison counted one more real miss for the checklist (RM-2); hand confirmation rejected it.\" 4.5 success criteria (line 74): \"with hand-confirmed detections\". The answer key's scoring text says only \"Each detection is confirmed by hand in the report.\"",
      "failure_scenario": "In 4.5b the author, having written 4.1's mandate and 4.4's lists, honestly confirms borderline matches for `open+list` and rejects them for `short`. Two such calls flip rule (b) or (c2). The cheapest fix: commit the confirmation criteria with the answer key before the run, and have a fresh reviewer session (or the owner) confirm the borderline matches blind to the configuration label. Slice 4.5.",
      "file": "docs/slices/agentic-sdlc-poc/benchmark_report.md",
      "id": "A10",
      "kind": "advisory",
      "line": 66,
      "problem": "[medium] Detection is confirmed by hand by the author, who also writes the configurations being compared, and the rule for confirming or rejecting is not committed with the answer key. In stage A, hand confirmation changed the outcome (it rejected RM-2 for the checklist, and set F8 aside as 'seen, rated advisory'). 4.5 keeps 'hand-confirmed detections' as a success criterion."
    },
    {
      "evidence": "Benchmark report lines 107-113 and recommendation 2. S42-D2: \"The listed files the reviewer did not open go into the end entry (paths_not_read)\". 4.5's success criteria and S45-D8 do not mention empty-review failures or paths_not_read.",
      "failure_scenario": "The new rule still fails about a quarter of the reviews, or passes reviews that skipped most of the listed files. The budget of 50 loses runs to it, and the default rule ships unmeasured. The cheapest analysis: report the failure count and paths_not_read per configuration in 4.5's report; the data is already in the results. Slice 4.5.",
      "file": "docs/slices/poc-4-2-review-inputs/plan.md",
      "id": "A11",
      "kind": "advisory",
      "line": 40,
      "problem": "[medium] The empty-review rule failed 5 of 22 stage-A reviews (23%), and stage A's recommendation 2 asked to 'measure the effect' of telling reviewers to open every path. 4.2 changes the rule (hint files, 'open every file' in the paths section, `paths_not_read`), but no 4.5 outcome or decision rule measures the failure rate or the share of listed files left unread."
    },
    {
      "evidence": "run_independent_review.py:45-46 (ROUND_LIMIT = 4, MAX_TRIES = 3). S46-D7 source: \"default (the trigger)\". S44-D3: \"default (the limit and the specificity rule)\". The slice-4 attempt logs already hold the round, verdict and status of 37 entries.",
      "failure_scenario": "A trigger set too late lets disputes use up rounds; one set too early sends the owner noise. Neither shows, because nobody counts. The cheapest analysis: in slice 5's close-out, count rounds-to-closure, re-raises and retries from the attempt logs and check each limit against them. Slice 5 (measure) and 6.",
      "file": "docs/slices/poc-4-6-stage-rules/plan.md",
      "id": "A12",
      "kind": "advisory",
      "line": 50,
      "problem": "[low] Several limits are defaults with no evidence, though the attempt logs could measure them. These are the round limit (4), MAX_TRIES (3), the escalation trigger 'two rounds in a row re-raised' (S46-D7), the cap of 12 questions per list (S44-D3) and the critique bound of 3 runs (S44-D10)."
    },
    {
      "evidence": "AGENTS.md quality gates table. No row cites the reason or the incident behind its threshold. F3 (20 characters or a digit) is an open decision concern for the owner (plan_launcher_fixes.md).",
      "failure_scenario": "A threshold that is too loose (for example, mutation at 70% counting skipped mutants) passes weak tests, and the review relies on the gate being green. The cheapest fix: one reasoned line per threshold, recorded by the owner, or left to slice 6, which builds gates only where slice 5 shows a need. Slice 6.",
      "file": "AGENTS.md",
      "id": "A13",
      "kind": "advisory",
      "line": 256,
      "problem": "[low] The unit-gate thresholds (line coverage 85%, branch coverage 75%, diff coverage 90%, mutation score 70%), the test-lint rules and the secret-shape constants (200 characters, 20 distinct characters, and now 20 characters or a digit) are inherited without a recorded reason in the rulebook's gate table. The PoC process relies on them as its deterministic checks."
    }
  ],
  "verdict": "no"
}
```

#### Answers to process_audit/c1/r1/audit/1

| ID | Severity | Answer |
| --- | --- | --- |
| B1 | blocking | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D8: the owner chooses each mandate from the report's counts; nothing is adopted automatically |
| A1 | high | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D6 and S45-D8: a screening study with repeats where the setups disagree, counts with exact intervals, and the owner's decision instead of fixed thresholds |
| A2 | high | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D5: two stage-document cases planted by a fresh session from 4.4's sources without seeing the lists |
| A3 | high | fixed: docs/slices/poc-4-5-benchmark/plan.md, AGENTS.md: S45-D10: the model comparison is dropped, and Opus is the default reviewer by the owner's reasoned choice (2026-11-09) |
| A4 | high | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D3: every configuration gets the same severity rules and blocking criteria, and the short prompt runs again in stage B instead of reusing stage A |
| A5 | medium | fixed: docs/slices/poc-4-4-stage-checklists/plan.md, docs/slices/poc-4-1-review-prompts/plan.md: S44-D13 researches the prompt around the mandate (preamble, order, task text, output rules), and S41-D15 gives the task text as claims to verify; a long-task benchmark setup is not added (owner, 2026-11-09) |
| A6 | high | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D6: initial reviews run at high effort and rechecks at medium, as in practice |
| A7 | high | fixed: docs/slices/poc-4-6-stage-rules/plan.md: S46-D14: the grill-me skill moves into the repository |
| A8 | medium | fixed: docs/slices/poc-4-1-review-prompts/plan.md, docs/slices/poc-4-2-review-inputs/plan.md, docs/slices/poc-4-3-review-records/plan.md, docs/slices/poc-4-4-stage-checklists/plan.md, docs/slices/poc-4-6-stage-rules/plan.md: every owner-sourced decision quotes the owner's words next to its link |
| A9 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md, docs/STATUS.md: S45-D8: the owner chooses the final mandate by reason; slice 5 records misses found after a final review against the mandate used |
| A10 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D7: blinded confirmation, with a second confirmer on a sample |
| A11 | medium | fixed: docs/slices/poc-4-5-benchmark/plan.md: S45-D8 reports empty-review failures and unread files per configuration |
| A12 | low | rejected: deferred to slice 5, which counts rounds, re-raises and retries from the attempt logs (docs/STATUS.md); an issue follows once the agent account is back |
| A13 | low | rejected: deferred to slice 6's candidates, one stated reason per gate threshold (docs/STATUS.md); an issue follows once the agent account is back |
