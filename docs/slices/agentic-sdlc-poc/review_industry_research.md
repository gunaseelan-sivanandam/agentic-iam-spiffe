# Review — the research summary

Record of the review of the research summary on agent-first delivery in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

## Round 1

### Attempt industry_research/c1/r1/research/1

Commit `a99d4f8`, effort high. Files reviewed (SHA-256): `docs/slices/agentic-sdlc-poc/industry_research.md` `22d96cdbd0a0`.

Status: completed; approvable within the threat model: no.

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, unsupported, overclaimed, stale or unclear, inside or outside the files under review. The questions below are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow, and saying so is part of the review.

## What you are reviewing

`docs/slices/agentic-sdlc-poc/industry_research.md` is a one-page summary, new in this change, of a study of how the industry runs agent-first software delivery and of an independent critique of that study. The full study and critique are not in your copy. The summary claims that slice 4's plans (`docs/slices/poc-4-*/plan.md`) took specific decisions from the study. You have no web access, so you cannot open the sources.

## Minimum questions

1. Does each statement of the form "So slice 4 ..." match a decision that the named plan actually contains, with the same meaning?
2. Does the summary overclaim: a vendor recommendation or an inference presented as measured evidence, a small study presented as settled, or a number without its context?
3. Is anything in the summary contradicted by the plans, `AGENTS.md`, the stage-A benchmark report (`docs/slices/agentic-sdlc-poc/benchmark_report.md`) or the delivery problem log?
4. Does the page follow the repository's rules for a new document (coding rule 8, one home per fact), and does it hold any operational detail or secret that a public repository must not carry?

## How to report

- Use kind "blocking" only for findings that meet `AGENTS.md`'s blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.
```

#### Report

```json
{
  "findings": [
    {
      "evidence": "poc-4-5-benchmark/plan.md:52, S45-D3: the setups are `short+list`, `open+list`, `open-B+list`, `recheck-A` and `recheck-B`, and every one carries 4.4's list. plan.md:24 quotes the owner: \"short prompts with check list and open mandate with checklist\". poc-4-5-benchmark/test_plan.md has no row comparing a setup with and without a list; `--rescore A` writes a separate output and S45-D8 does not use it for a list comparison. poc-4-5-benchmark/plan_review.md:403 and :746 show the earlier `open` (no list) setup that measured this. poc-4-4-stage-checklists/plan.md:43 (S44-D3), and plan_review.md:324, which answers A6 with \"4.5's rule S45-D8(b) decides whether the lists stay\"; that rule no longer exists.",
      "failure_scenario": "The owner approves the slice-4 plan PR believing what this page, S44-D3 and S45-D8 say: that 4.5 will show whether the stage lists add anything. 4.5b runs and reports only short+list against open+list, which measures the mandate. The owner then decides \"whether the lists stay\" with no data on the lists' effect, and the lists stay in every review untested. This is a contradiction between the summary (and two plans) and 4.5's approved setups. Fix it at the source: either add a no-list setup to 4.5 within the 60-run budget, or change the summary, S44-D3 and S45-D8 to say the lists' effect is not measured.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R1",
      "kind": "blocking",
      "line": 26,
      "problem": "Finding 3 says the benchmark measures checklists against open instructions (\"The benchmark measures it (4.5)\"). The 4.5 plan the summary points to has no setup without a checklist, so it cannot measure this. 4.4's plan makes the same claim (S44-D3: \"4.5 measures whether the new lists add anything\"), and so does 4.5 S45-D8 (\"The owner decides ... whether the lists stay\"). That claim held for the round-3 version of 4.5, which had an `open` setup with no list. It stopped holding when the owner's 2026-11-09 decision left only list-bearing setups."
    },
    {
      "evidence": "Lines 24-26. The only source listed for the inspection claim is the Porter/Votta/Basili scenario paper (lines 64-65), whose title already names scenarios as the method studied. No replication or sample size is given.",
      "failure_scenario": "A later reader, or the owner deciding whether the lists stay (S45-D8), treats \"checklists don't help\" as established. Reasonable list designs, such as scenario-like stage questions, are then dropped on the strength of a single 1995 student experiment summarised by half its result.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R2",
      "kind": "advisory",
      "line": 25,
      "problem": "[medium] Small and contested evidence is stated as settled. \"In human inspections, checklists did not find more defects than unguided reading\" rests on one source, Porter, Votta and Basili (1995). The summary also leaves out that study's main result: scenario-based reading beat both checklists and ad hoc reading. That result is the one most relevant to 4.4's stage-specific lists. \"No study compares them for LLM reviewers\" is an absolute negative; the research can only support \"the research found none\"."
    },
    {
      "evidence": "Line 32: \"At this repository's comparison sizes, a 'two more detections' rule fires by chance 8 to 26% of the time.\" The full critique is \"kept outside the repository\" (line 10\u201311). poc-4-5-benchmark/plan.md:57 cites \"the research's critique (the 'two more detections' rule fires by chance 8 to 26% of the time at these sizes)\".",
      "failure_scenario": "A reviewer or the owner cannot check the number and cannot apply it to a different case count. A later slice reuses \"8\u201326%\" for another sample size where it does not hold.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R3",
      "kind": "advisory",
      "line": 32,
      "problem": "[medium] The figure \"fires by chance 8 to 26% of the time\" has no context. It does not say which case counts, which base detection rates or which test it assumes, or whether it comes from stage A's 4 real-miss cases or 4.5's 15 cases. It is the critique's own calculation, not a measured result, and the page does not say so. 4.5 S45-D8 cites this number as its reason, so it should be checkable in the repository."
    },
    {
      "evidence": "poc-4-1 plan.md:57 (S41-D15: \"recommendations P2 and P6 as amended by its critique\"); plan.md:58 (S41-D16: \"recommendation D5 as amended\"); poc-4-5 plan.md:56 (S45-D7: \"B4 as amended\"); poc-4-6 plan.md:56 (S46-D13: \"H2 as amended\"). A search of industry_research.md finds none of P2, P6, D5, B4 or H2, and nothing about origin_stage.",
      "failure_scenario": "A plan reviewer, or slice 8's evaluation, tries to check that S41-D15, S41-D16, S45-D7 and S46-D13 match their cited source. The source is not in the repository and the summary does not map to it, so the decisions' sources are not checkable. An amendment that changed meaning would go unnoticed.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R4",
      "kind": "advisory",
      "line": 13,
      "problem": "[medium] The page is the only in-repository record of the research, but it does not define the recommendation IDs the plans cite as decision sources, and it does not record what the critique amended. Several plan decisions name \"the research's recommendation(s) P2, P6, D5, B4, H2 as amended by its critique\". None of these IDs appears here. One adopted decision is missing entirely: S41-D16 (origin_stage, from the research's D5). AGENTS.md says reviewers read the repository, not outside material, and 4.4's own plan sets the standard that research records carry the quotes a reviewer needs (poc-4-4 plan.md:94). This page carries almost none: one unattributed quote and no per-claim citation."
    },
    {
      "evidence": "Lines 19-23 and 36-38. The key sources (lines 55-70) list Anthropic docs, arXiv papers, METR, Thoughtworks and B\u00f6ckeler, with no mapping from any claim to a source and no source for the default suppression of missing-test findings.",
      "failure_scenario": "A reader takes \"commercial reviewers suppress missing-test findings\" as a verified industry fact and reuses it, with no way to check it or tell that it is one vendor's default setting.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R5",
      "kind": "advisory",
      "line": 20,
      "problem": "[medium] Vendor claims have no source. \"Commercial reviewers suppress missing-test findings by default\" names no vendor or document. The quote \"will always find something\" is not attributed. \"Approvals that the human cannot really judge are a named anti-pattern\" (line 37) does not say who names it. All three are used as reasons for decisions (S41-D15, S46-D13), yet none is tied to a listed key source. They are also vendor or practitioner statements, not measured evidence, and the page does not say so."
    },
    {
      "evidence": "Line 27 and line 62 (the only bias source: Kim and Khashabi). poc-4-1 plan.md:47 (S41-D5(b): the author's answers go into the recheck prompt).",
      "failure_scenario": "Readers conclude that rebuttal sycophancy is handled by \"fresh sessions\". The recheck acceptance rate of author rejections is then never measured. 4.5 has one recheck case per wording, which cannot show it.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R6",
      "kind": "advisory",
      "line": 27,
      "problem": "[low] \"The largest measured biases are a reviewer taking on the author's framing, and giving in to an author's rebuttal\" ranks biases across studies. The listed sources do not support a ranking: one paper on rebuttal sycophancy, and none named for framing anchoring. Also, the recheck design (S41-D5) still puts the author's answers, which are the rebuttal, into the prompt. A fresh session is a partial mitigation, and the page should say so rather than imply the bias is addressed."
    },
    {
      "evidence": "AGENTS.md (base) step 4 \"Verify and close\" sets no order between the gates and the review. poc-4-2 plan.md:43: \"(a queued or running job says so)\" and \"no CI run for this commit\".",
      "failure_scenario": "The owner believes deterministic gates run before every AI review, as the vendors' pipeline has it, and does not ask for that ordering. Reviews then run on commits whose gates later fail.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R7",
      "kind": "advisory",
      "line": 18,
      "problem": "[low] \"The PoC already matches: ... gates come first\" overstates the current rules. AGENTS.md step 4 lists running the gates and the independent review together but does not order them. 4.2 has the reviewer read CI results that may still be queued or running (S42-D5(c)), so the AI review can run before the gates finish."
    },
    {
      "evidence": "benchmark_report.md:81 (CL-2 is the only completed clean case), :96-103 (\"mostly real, judged against the code at those commits; none is a false blocker\", judged by the author), :154 (\"One run per case and prompt; the sample is small\").",
      "failure_scenario": "The false-alarm side is treated as settled, and 4.5's false-alarm and decoy measurements get less weight when the owner decides.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R8",
      "kind": "advisory",
      "line": 47,
      "problem": "[low] \"No false blocker in 17 completed reviews\" is used to argue that reviewers miss defects rather than raise false alarms. Its basis is weak. Only one clean case completed (CL-2, two reviews). The other unmatched blocking findings were judged \"mostly real\" by the author alone, without blinding. The page gives the count without that context. It also says the reviews were \"failing the empty-review rule\" without saying that this was a launcher rule failure, not a review finding."
    },
    {
      "evidence": "poc-4-4-stage-checklists/plan.md:53 (S44-D13) and :42 (S44-D2) set up research.md as the research record. industry_research.md lines 24-30 cover the same ground.",
      "failure_scenario": "4.4's research.md later reaches a different conclusion on checklists or sycophancy. Two live documents then disagree, and readers do not know which one governs.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R9",
      "kind": "advisory",
      "line": 1,
      "problem": "[low] One home per fact. This page's findings 3 and 4 (LLM-as-judge biases, checklist evidence) overlap with 4.4's planned `research.md` \"Review prompt\" section. S44-D13 covers studies of LLMs as judges, their failure modes and checklist and severity evidence. The two will hold overlapping facts with no stated owner. Coding rule 8 itself is satisfied: there is a title and a purpose paragraph, and I found no secret or operational path. The owner's verbatim quote at line 5 keeps its typo, which is fine."
    },
    {
      "evidence": "Items 1-7 mix claims, inferences and decision links in prose; the sources are listed separately with no mapping to the claims.",
      "failure_scenario": "Without the mapping, each later reviewer has to re-derive which source supports which claim, as this review had to.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R10",
      "kind": "simpler_alternative",
      "line": 13,
      "problem": "The \"Findings that shaped slice 4\" list could be a table: finding, adopted decision ID, and the source key for the claim. That would make each \"So slice 4 ...\" link and each claim's citation checkable in one place, and would remove the need for the prose cross-references that R4 and R5 found missing."
    }
  ],
  "verdict": "no"
}
```

#### Answers to industry_research/c1/r1/research/1

| ID | Severity | Answer |
| --- | --- | --- |
| R1 | blocking | fixed: docs/slices/agentic-sdlc-poc/industry_research.md, docs/slices/poc-4-4-stage-checklists/plan.md, docs/slices/poc-4-5-benchmark/plan.md: row 4, S44-D3 and S45-D8 now say that both setups carry the lists by the owner's choice, so 4.5 measures the mandate and not the lists' own effect |
| R2 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 4 says the research found no study, and gives the 1995 study as small and old, with its main result that scenario-based reading beat both |
| R3 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 6 gives the assumptions (equal true rates of 60%, 5 to 11 paired cases, one direction) and labels it the critique's calculation |
| R4 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: the findings are a table with the study's recommendation IDs and the decisions they led to, including D5 to S41-D16 |
| R5 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: rows 2, 3 and 8 attribute the claims to sources 1, 2 and 10 and label them vendor or practitioner |
| R6 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 5 no longer ranks the biases and says the fresh session mitigates the rebuttal bias only in part |
| R7 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 1 says the PoC has the gates, not that they come first, and that reviews can run before CI finishes |
| R8 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: the corrections give stage A's count with its limits (one clean case completed; unblinded judgment; the launcher's rule) |
| R9 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: the method paragraph says 4.4's research.md will hold the detailed research and this page keeps the mapping |
| R10 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: adopted; the findings are a table |

## Round 2

### Attempt industry_research/c1/r2/research/1

Commit `41e784b`, effort medium. Files reviewed (SHA-256): `docs/slices/agentic-sdlc-poc/industry_research.md` `b0203806caa9`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 2 of the review of the research summary `docs/slices/agentic-sdlc-poc/industry_research.md`, a recheck of your earlier report (round 1, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch, including the changed decisions in `docs/slices/poc-4-4-stage-checklists/plan.md` (S44-D3) and `docs/slices/poc-4-5-benchmark/plan.md` (S45-D8). From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; report new high findings as well, marked `[high]`.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it.
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## Your earlier report (round 1, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "poc-4-5-benchmark/plan.md:52, S45-D3: the setups are `short+list`, `open+list`, `open-B+list`, `recheck-A` and `recheck-B`, and every one carries 4.4's list. plan.md:24 quotes the owner: \"short prompts with check list and open mandate with checklist\". poc-4-5-benchmark/test_plan.md has no row comparing a setup with and without a list; `--rescore A` writes a separate output and S45-D8 does not use it for a list comparison. poc-4-5-benchmark/plan_review.md:403 and :746 show the earlier `open` (no list) setup that measured this. poc-4-4-stage-checklists/plan.md:43 (S44-D3), and plan_review.md:324, which answers A6 with \"4.5's rule S45-D8(b) decides whether the lists stay\"; that rule no longer exists.",
      "failure_scenario": "The owner approves the slice-4 plan PR believing what this page, S44-D3 and S45-D8 say: that 4.5 will show whether the stage lists add anything. 4.5b runs and reports only short+list against open+list, which measures the mandate. The owner then decides \"whether the lists stay\" with no data on the lists' effect, and the lists stay in every review untested. This is a contradiction between the summary (and two plans) and 4.5's approved setups. Fix it at the source: either add a no-list setup to 4.5 within the 60-run budget, or change the summary, S44-D3 and S45-D8 to say the lists' effect is not measured.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R1",
      "kind": "blocking",
      "line": 26,
      "problem": "Finding 3 says the benchmark measures checklists against open instructions (\"The benchmark measures it (4.5)\"). The 4.5 plan the summary points to has no setup without a checklist, so it cannot measure this. 4.4's plan makes the same claim (S44-D3: \"4.5 measures whether the new lists add anything\"), and so does 4.5 S45-D8 (\"The owner decides ... whether the lists stay\"). That claim held for the round-3 version of 4.5, which had an `open` setup with no list. It stopped holding when the owner's 2026-11-09 decision left only list-bearing setups."
    },
    {
      "evidence": "Lines 24-26. The only source listed for the inspection claim is the Porter/Votta/Basili scenario paper (lines 64-65), whose title already names scenarios as the method studied. No replication or sample size is given.",
      "failure_scenario": "A later reader, or the owner deciding whether the lists stay (S45-D8), treats \"checklists don't help\" as established. Reasonable list designs, such as scenario-like stage questions, are then dropped on the strength of a single 1995 student experiment summarised by half its result.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R2",
      "kind": "advisory",
      "line": 25,
      "problem": "[medium] Small and contested evidence is stated as settled. \"In human inspections, checklists did not find more defects than unguided reading\" rests on one source, Porter, Votta and Basili (1995). The summary also leaves out that study's main result: scenario-based reading beat both checklists and ad hoc reading. That result is the one most relevant to 4.4's stage-specific lists. \"No study compares them for LLM reviewers\" is an absolute negative; the research can only support \"the research found none\"."
    },
    {
      "evidence": "Line 32: \"At this repository's comparison sizes, a 'two more detections' rule fires by chance 8 to 26% of the time.\" The full critique is \"kept outside the repository\" (line 10\u201311). poc-4-5-benchmark/plan.md:57 cites \"the research's critique (the 'two more detections' rule fires by chance 8 to 26% of the time at these sizes)\".",
      "failure_scenario": "A reviewer or the owner cannot check the number and cannot apply it to a different case count. A later slice reuses \"8\u201326%\" for another sample size where it does not hold.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R3",
      "kind": "advisory",
      "line": 32,
      "problem": "[medium] The figure \"fires by chance 8 to 26% of the time\" has no context. It does not say which case counts, which base detection rates or which test it assumes, or whether it comes from stage A's 4 real-miss cases or 4.5's 15 cases. It is the critique's own calculation, not a measured result, and the page does not say so. 4.5 S45-D8 cites this number as its reason, so it should be checkable in the repository."
    },
    {
      "evidence": "poc-4-1 plan.md:57 (S41-D15: \"recommendations P2 and P6 as amended by its critique\"); plan.md:58 (S41-D16: \"recommendation D5 as amended\"); poc-4-5 plan.md:56 (S45-D7: \"B4 as amended\"); poc-4-6 plan.md:56 (S46-D13: \"H2 as amended\"). A search of industry_research.md finds none of P2, P6, D5, B4 or H2, and nothing about origin_stage.",
      "failure_scenario": "A plan reviewer, or slice 8's evaluation, tries to check that S41-D15, S41-D16, S45-D7 and S46-D13 match their cited source. The source is not in the repository and the summary does not map to it, so the decisions' sources are not checkable. An amendment that changed meaning would go unnoticed.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R4",
      "kind": "advisory",
      "line": 13,
      "problem": "[medium] The page is the only in-repository record of the research, but it does not define the recommendation IDs the plans cite as decision sources, and it does not record what the critique amended. Several plan decisions name \"the research's recommendation(s) P2, P6, D5, B4, H2 as amended by its critique\". None of these IDs appears here. One adopted decision is missing entirely: S41-D16 (origin_stage, from the research's D5). AGENTS.md says reviewers read the repository, not outside material, and 4.4's own plan sets the standard that research records carry the quotes a reviewer needs (poc-4-4 plan.md:94). This page carries almost none: one unattributed quote and no per-claim citation."
    },
    {
      "evidence": "Lines 19-23 and 36-38. The key sources (lines 55-70) list Anthropic docs, arXiv papers, METR, Thoughtworks and B\u00f6ckeler, with no mapping from any claim to a source and no source for the default suppression of missing-test findings.",
      "failure_scenario": "A reader takes \"commercial reviewers suppress missing-test findings\" as a verified industry fact and reuses it, with no way to check it or tell that it is one vendor's default setting.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R5",
      "kind": "advisory",
      "line": 20,
      "problem": "[medium] Vendor claims have no source. \"Commercial reviewers suppress missing-test findings by default\" names no vendor or document. The quote \"will always find something\" is not attributed. \"Approvals that the human cannot really judge are a named anti-pattern\" (line 37) does not say who names it. All three are used as reasons for decisions (S41-D15, S46-D13), yet none is tied to a listed key source. They are also vendor or practitioner statements, not measured evidence, and the page does not say so."
    },
    {
      "evidence": "Line 27 and line 62 (the only bias source: Kim and Khashabi). poc-4-1 plan.md:47 (S41-D5(b): the author's answers go into the recheck prompt).",
      "failure_scenario": "Readers conclude that rebuttal sycophancy is handled by \"fresh sessions\". The recheck acceptance rate of author rejections is then never measured. 4.5 has one recheck case per wording, which cannot show it.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R6",
      "kind": "advisory",
      "line": 27,
      "problem": "[low] \"The largest measured biases are a reviewer taking on the author's framing, and giving in to an author's rebuttal\" ranks biases across studies. The listed sources do not support a ranking: one paper on rebuttal sycophancy, and none named for framing anchoring. Also, the recheck design (S41-D5) still puts the author's answers, which are the rebuttal, into the prompt. A fresh session is a partial mitigation, and the page should say so rather than imply the bias is addressed."
    },
    {
      "evidence": "AGENTS.md (base) step 4 \"Verify and close\" sets no order between the gates and the review. poc-4-2 plan.md:43: \"(a queued or running job says so)\" and \"no CI run for this commit\".",
      "failure_scenario": "The owner believes deterministic gates run before every AI review, as the vendors' pipeline has it, and does not ask for that ordering. Reviews then run on commits whose gates later fail.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R7",
      "kind": "advisory",
      "line": 18,
      "problem": "[low] \"The PoC already matches: ... gates come first\" overstates the current rules. AGENTS.md step 4 lists running the gates and the independent review together but does not order them. 4.2 has the reviewer read CI results that may still be queued or running (S42-D5(c)), so the AI review can run before the gates finish."
    },
    {
      "evidence": "benchmark_report.md:81 (CL-2 is the only completed clean case), :96-103 (\"mostly real, judged against the code at those commits; none is a false blocker\", judged by the author), :154 (\"One run per case and prompt; the sample is small\").",
      "failure_scenario": "The false-alarm side is treated as settled, and 4.5's false-alarm and decoy measurements get less weight when the owner decides.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R8",
      "kind": "advisory",
      "line": 47,
      "problem": "[low] \"No false blocker in 17 completed reviews\" is used to argue that reviewers miss defects rather than raise false alarms. Its basis is weak. Only one clean case completed (CL-2, two reviews). The other unmatched blocking findings were judged \"mostly real\" by the author alone, without blinding. The page gives the count without that context. It also says the reviews were \"failing the empty-review rule\" without saying that this was a launcher rule failure, not a review finding."
    },
    {
      "evidence": "poc-4-4-stage-checklists/plan.md:53 (S44-D13) and :42 (S44-D2) set up research.md as the research record. industry_research.md lines 24-30 cover the same ground.",
      "failure_scenario": "4.4's research.md later reaches a different conclusion on checklists or sycophancy. Two live documents then disagree, and readers do not know which one governs.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R9",
      "kind": "advisory",
      "line": 1,
      "problem": "[low] One home per fact. This page's findings 3 and 4 (LLM-as-judge biases, checklist evidence) overlap with 4.4's planned `research.md` \"Review prompt\" section. S44-D13 covers studies of LLMs as judges, their failure modes and checklist and severity evidence. The two will hold overlapping facts with no stated owner. Coding rule 8 itself is satisfied: there is a title and a purpose paragraph, and I found no secret or operational path. The owner's verbatim quote at line 5 keeps its typo, which is fine."
    },
    {
      "evidence": "Items 1-7 mix claims, inferences and decision links in prose; the sources are listed separately with no mapping to the claims.",
      "failure_scenario": "Without the mapping, each later reviewer has to re-derive which source supports which claim, as this review had to.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "R10",
      "kind": "simpler_alternative",
      "line": 13,
      "problem": "The \"Findings that shaped slice 4\" list could be a table: finding, adopted decision ID, and the source key for the claim. That would make each \"So slice 4 ...\" link and each claim's citation checkable in one place, and would remove the need for the prose cross-references that R4 and R5 found missing."
    }
  ],
  "verdict": "no"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| R1 | blocking | fixed: docs/slices/agentic-sdlc-poc/industry_research.md, docs/slices/poc-4-4-stage-checklists/plan.md, docs/slices/poc-4-5-benchmark/plan.md: row 4, S44-D3 and S45-D8 now say that both setups carry the lists by the owner's choice, so 4.5 measures the mandate and not the lists' own effect |
| R2 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 4 says the research found no study, and gives the 1995 study as small and old, with its main result that scenario-based reading beat both |
| R3 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 6 gives the assumptions (equal true rates of 60%, 5 to 11 paired cases, one direction) and labels it the critique's calculation |
| R4 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: the findings are a table with the study's recommendation IDs and the decisions they led to, including D5 to S41-D16 |
| R5 | medium | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: rows 2, 3 and 8 attribute the claims to sources 1, 2 and 10 and label them vendor or practitioner |
| R6 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 5 no longer ranks the biases and says the fresh session mitigates the rebuttal bias only in part |
| R7 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: row 1 says the PoC has the gates, not that they come first, and that reviews can run before CI finishes |
| R8 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: the corrections give stage A's count with its limits (one clean case completed; unblinded judgment; the launcher's rule) |
| R9 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: the method paragraph says 4.4's research.md will hold the detailed research and this page keeps the mapping |
| R10 | low | fixed: docs/slices/agentic-sdlc-poc/industry_research.md: adopted; the findings are a table |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "R1: accepted \u2014 industry_research.md (row 4, line 27), poc-4-4-stage-checklists/plan.md:43 (S44-D3), poc-4-5-benchmark/plan.md:52 (S45-D3), :57 (S45-D8)\nR2: accepted \u2014 industry_research.md (row 4, source 6)\nR3: accepted \u2014 industry_research.md (row 6), poc-4-5-benchmark/plan.md:57\nR4: accepted \u2014 industry_research.md (lines 9-10, table column 'Study's ID', row 9 D5 to S41-D16)\nR5: accepted \u2014 industry_research.md (rows 2, 3, 8 with [2], [1], [10] and kinds)\nR6: accepted \u2014 industry_research.md (row 5)\nR7: accepted \u2014 industry_research.md (row 1)\nR8: accepted \u2014 industry_research.md (lines 42-45)\nR9: accepted \u2014 industry_research.md (lines 12-14)\nR10: accepted \u2014 industry_research.md (table, lines 22-33)",
      "failure_scenario": "None; this is the accounting of the answers.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    },
    {
      "evidence": "poc-4-4 plan.md:51 (S44-D11 proposes items and wordings; it measures nothing); plan.md:43; industry_research.md:27.",
      "failure_scenario": "The owner reads \"track\" as \"measure\" and expects slice 8 to have data on the lists' effect. Unless slice 8 plans a no-list comparison, that data will not exist. This is not a contradiction: both plans now say plainly that 4.5 does not measure the lists' effect.",
      "file": "docs/slices/poc-4-4-stage-checklists/plan.md",
      "id": "N1",
      "kind": "advisory",
      "line": 43,
      "problem": "[low] S44-D3 says the lists' own effect is tracked by \"the learning loop (S44-D11) and slice 8's evaluation\". S44-D11 only adds items when an open review finds a missing class of defect. It does not measure whether the lists help. Row 4 of industry_research.md says the same thing (\"the learning loop and slice 8 track the lists\"). There is also a typo: \"length; The lists\"."
    }
  ],
  "verdict": "yes"
}
```

#### Answers to industry_research/c1/r2/research/1

| ID | Severity | Answer |
| --- | --- | --- |
| N1 | low | fixed: docs/slices/poc-4-4-stage-checklists/plan.md, docs/slices/agentic-sdlc-poc/industry_research.md, docs/STATUS.md: S44-D3 and row 4 say nothing measures the lists' effect unless slice 8 compares reviews with and without them, and STATUS lists that as a slice-8 option; the typo is fixed |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |

## Round 3

### Attempt industry_research/c1/r3/research/1

Commit `a4082dd`, effort medium. Files reviewed (SHA-256): `docs/slices/agentic-sdlc-poc/industry_research.md` `c70811a176c5`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 3 of the review of the research summary `docs/slices/agentic-sdlc-poc/industry_research.md`, a recheck of your earlier report (round 2, attempt 1). For every answer of the author below, open the files the answer names and check the fix; accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch, including the changed decisions in `docs/slices/poc-4-4-stage-checklists/plan.md` (S44-D3) and `docs/slices/poc-4-5-benchmark/plan.md` (S45-D8). From round 2 a new finding counts only if it is blocking (`AGENTS.md`, Plan review), except simpler alternatives and decision concerns; report new high findings as well, marked `[high]`.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it.
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## The owner's request for this round

The owner, in a review comment on PR #48 (2026-11-09): "Run one additional review round to check your latest fixes". Your round 2 found one low finding; the author fixed it (answer below).

## Your earlier report (round 2, attempt 1)

```json
{
  "findings": [
    {
      "evidence": "R1: accepted \u2014 industry_research.md (row 4, line 27), poc-4-4-stage-checklists/plan.md:43 (S44-D3), poc-4-5-benchmark/plan.md:52 (S45-D3), :57 (S45-D8)\nR2: accepted \u2014 industry_research.md (row 4, source 6)\nR3: accepted \u2014 industry_research.md (row 6), poc-4-5-benchmark/plan.md:57\nR4: accepted \u2014 industry_research.md (lines 9-10, table column 'Study's ID', row 9 D5 to S41-D16)\nR5: accepted \u2014 industry_research.md (rows 2, 3, 8 with [2], [1], [10] and kinds)\nR6: accepted \u2014 industry_research.md (row 5)\nR7: accepted \u2014 industry_research.md (row 1)\nR8: accepted \u2014 industry_research.md (lines 42-45)\nR9: accepted \u2014 industry_research.md (lines 12-14)\nR10: accepted \u2014 industry_research.md (table, lines 22-33)",
      "failure_scenario": "None; this is the accounting of the answers.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    },
    {
      "evidence": "poc-4-4 plan.md:51 (S44-D11 proposes items and wordings; it measures nothing); plan.md:43; industry_research.md:27.",
      "failure_scenario": "The owner reads \"track\" as \"measure\" and expects slice 8 to have data on the lists' effect. Unless slice 8 plans a no-list comparison, that data will not exist. This is not a contradiction: both plans now say plainly that 4.5 does not measure the lists' effect.",
      "file": "docs/slices/poc-4-4-stage-checklists/plan.md",
      "id": "N1",
      "kind": "advisory",
      "line": 43,
      "problem": "[low] S44-D3 says the lists' own effect is tracked by \"the learning loop (S44-D11) and slice 8's evaluation\". S44-D11 only adds items when an open review finds a missing class of defect. It does not measure whether the lists help. Row 4 of industry_research.md says the same thing (\"the learning loop and slice 8 track the lists\"). There is also a typo: \"length; The lists\"."
    }
  ],
  "verdict": "yes"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| N1 | low | fixed: docs/slices/poc-4-4-stage-checklists/plan.md, docs/slices/agentic-sdlc-poc/industry_research.md, docs/STATUS.md: S44-D3 and row 4 say nothing measures the lists' effect unless slice 8 compares reviews with and without them, and STATUS lists that as a slice-8 option; the typo is fixed |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "N1: accepted. Opened docs/slices/poc-4-4-stage-checklists/plan.md:43 (S44-D3 now says \"Nothing measures that unless slice 8 compares reviews with and without the lists; the learning loop (S44-D11) only adds what reviews show missing\", and the typo is gone), docs/slices/agentic-sdlc-poc/industry_research.md:27 (row 4 says \"only a comparison without lists, a slice-8 option, could measure it\"), docs/STATUS.md:29-30 (slice 8 option: whether the stage lists help, reviews with and without them), docs/slices/poc-4-5-benchmark/plan.md:57 (S45-D8: \"Both setups carry the lists, so the report does not measure the lists' own effect\"). The four files agree.\nACCOUNTED: accepted. It is the accounting stand-in, not a finding.",
      "failure_scenario": "None; this is the accounting of the answers.",
      "file": "docs/slices/agentic-sdlc-poc/industry_research.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to industry_research/c1/r3/research/1

| ID | Severity | Answer |
| --- | --- | --- |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
