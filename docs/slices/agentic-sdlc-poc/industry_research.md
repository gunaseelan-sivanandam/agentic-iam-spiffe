# Research summary — agent-first software delivery in industry (2026-11-09)

What slice 4 took from a study of how the industry runs agent-first software delivery, and what an
independent critique of that study corrected. The owner asked for it before slice 4's plans were
finalized ("Maybe we should check first how indusctry approaches agent first Sw delivery").

**Method.** Five research topics, each researched separately: tool makers' workflows, independent
evidence, AI code review tools, research on language models as reviewers, and measuring reliability
with the known failure modes. One report combined them into recommendations with IDs: D (destination),
H (human checkpoints), P (prompts and checklists) and B (benchmark). A fresh session then critiqued
the report: it checked 67 claims against their sources and read this repository. The full report and
critique are kept outside the repository. This page holds the conclusions, the decisions they led to,
and the key sources. 4.4's `research.md` will hold the detailed research on reviewers and checklists;
this page then keeps only the mapping to decisions.

## Findings and the decisions they led to

Kinds: **vendor** (guidance from a company that sells the tool), **independent** (measured by a
party that does not sell it), **practitioner** (experienced individuals' opinion), **calculation**
(the critique's own arithmetic), **inference** (the study's reasoning).

| # | Finding | Kind | Study's ID | Slice-4 decision |
| --- | --- | --- | --- | --- |
| 1 | Tool makers describe a short pipeline: plan or spec, tests, deterministic gates, an AI review in a fresh read-only session, a human merge, often with a human approval of the plan. Several skip plan approval for small tasks. | vendor | H1 | None needed: the owner already approves the plan PR, and the PoC has the gates, confined reviewers and tests first. Reviews can run before CI finishes, so the brief shows CI status (S46-D13) |
| 2 | Commercial reviewers search broadly, then verify each finding. Claude Code Review's default covers correctness, "not formatting preferences or missing test coverage" [2]. | vendor | P1, P3 | Keep the open mandate with the stage checklist, aimed at the missing things these tools leave out (owner, 2026-11-09); the launcher computes evidence instead of the reviewer running commands (S42-D5) |
| 3 | "A reviewer that's asked to find problems will always find something" [1]. | vendor | P2 | Reporting bounds: the absence format, no reports of what a passing gate checks, defects in gates reported, `cannot determine` (S41-D15). The four severity levels stay (S41-D6) |
| 4 | The research found no study comparing checklists with open instructions for LLM reviewers. LLM checklists mainly make judgments more consistent [5]. In one 1995 inspection experiment with students, checklists found no more defects than ad hoc reading, and scenario-based reading beat both [6]. | independent, small and old | P5 | Short stage-specific questions (S44-D3). Both benchmark setups carry the lists by the owner's choice, so 4.5 measures the mandate, not the lists' own effect; the learning loop and slice 8 track the lists |
| 5 | LLM reviews of papers repeated the limitations the authors themselves stated far more than human reviews did [7]; LLM judges give in to an author's rebuttal in a conversational follow-up more than when judging afresh [4]. Measured on models before Claude 4.5. | independent | P4, P6 | The task text becomes "claims to verify" (S41-D15); rechecks stay fresh sessions. Rechecks still read the author's answers, so this mitigates the bias only in part, and 4.5's single recheck case cannot measure it |
| 6 | About 15 cases with one run each screen for large effects only. With equal true detection rates of 60% and 5 to 11 paired cases, a "two more detections" rule fires in a given direction 8 to 26% of the time. | calculation | B1–B7 | A blinded screening study whose counts the owner decides from (S45-D4 to S45-D8) |
| 7 | Editing the tests is the best-measured failure of coding agents, measured on tasks built to be impossible [8, 9]. | independent | D3 | No delivery problem here shows it yet: a check that approved tests are unchanged is a slice-6 candidate |
| 8 | The capacity to review runs out before the capacity to generate; Thoughtworks calls approvals the human cannot really judge "human-in-the-loop theater" [10]. | practitioner, observational | H2 | A decision brief generated from the records opens every plan PR and final PR (S46-D13) |
| 9 | No published evidence on single-owner, agent-majority delivery; recording where each defect arose and where it was caught would produce some. | inference | D5 | An origin stage on every finding (S41-D16) |
| 10 | Confirming detections while knowing which setup produced them can bias a comparison. | inference from standard practice | B4 | Blinded confirmation with a second confirmer on a sample (S45-D7) |

## Corrections from the critique

- The report missed that the owner already approves intent, by merging the plan PR.
- About half of its recommendations were already in place or planned.
- Collapsing the severity scale, and building checklists from this repository's own misses, would
  have reversed the owner's decisions. Neither is adopted.
- The reviewer cannot run commands; the launcher computes the evidence instead (4.2, S42-D5).
- Stage A's own data point to what reviewers miss rather than to false alarms, with limits. No
  blocking finding of its 17 completed reviews was a false alarm, but only one clean case completed,
  and the author judged the rest without blinding. The launcher's empty-review rule failed 5 of 22
  reviews.

Not adopted: reordering the prompt so that files come first (the reviewer reads files by tool, so the
evidence does not apply); merging stages (a stage can already be "none, with a reason"); restarting
instead of a fourth round; comparing reviewer models (Opus is the reviewer by the owner's reasoned
choice).

## Key sources

1. Anthropic, Claude Code best practices (accessed 2026-11-09):
   <https://code.claude.com/docs/en/best-practices>
2. Anthropic, Claude Code Review docs (accessed 2026-11-09): <https://code.claude.com/docs/en/code-review>
3. Anthropic, "Demystifying evals for AI agents" (2026-01-09):
   <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
4. Kim and Khashabi, rebuttal sycophancy in LLM judges (2025): <https://arxiv.org/abs/2509.16533>
5. CheckEval, checklist-based LLM evaluation: <https://arxiv.org/abs/2403.18771>
6. Porter, Votta and Basili, scenario-based inspections (IEEE TSE, 1995):
   <https://www.cs.umd.edu/~aporter/html/scenarios.html>
7. Ye et al., LLM reviews against authors' stated limitations (2024-12): <https://arxiv.org/abs/2412.01708>
8. ImpossibleBench, test gaming by coding agents (2025-10): <https://arxiv.org/abs/2510.20270>
9. METR, recent reward hacking (2025-06-05): <https://metr.org/blog/2025-06-05-recent-reward-hacking/>
10. Thoughtworks Technology Radar, Vol. 35 (2026-11): <https://www.thoughtworks.com/radar/techniques>
11. SWR-Bench, LLM code review on real pull requests (2025-09): <https://arxiv.org/abs/2509.01494>
12. Böckeler, spec-driven development tools (2025-10-15):
    <https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html>
