# Research summary — agent-first software delivery in industry (2026-11-09)

What slice 4 took from a study of how the industry runs agent-first software delivery, and what an
independent critique of that study corrected. The owner asked for it before slice 4's plans were
finalized ("Maybe we should check first how indusctry approaches agent first Sw delivery").

**Method.** Five research topics, each researched separately: tool makers' workflows, independent
evidence, AI code review tools, research on language models as reviewers, and measuring reliability
with the known failure modes. One report combined them. A fresh session then critiqued the report: it
checked 67 claims against their sources and read this repository. The full report and critique are
kept outside the repository; this page records the conclusions and the key sources.

## Findings that shaped slice 4

1. **Process.** Tool makers describe a short pipeline: plan or spec, tests, deterministic gates, an AI
   review in a fresh read-only session, and a human merge, often with a human approval of the plan.
   Not every vendor approves plans; several skip planning for small tasks. The PoC already matches:
   the owner approves the plan PR, gates come first, reviewers are confined, tests come first.
2. **AI reviewers.** Mature review tools search broadly and then verify each finding. Commercial
   reviewers suppress missing-test findings by default, which is the class of defect this PoC most
   wants caught. Vendors also warn that a reviewer asked to find problems "will always find
   something". So slice 4 keeps the open mandate with the stage checklist, and bounds what it
   reports (4.1, S41-D15).
3. **Checklists against open instructions.** No study compares them for LLM reviewers. Checklists
   mainly make LLM judgments more consistent; in human inspections, checklists did not find more
   defects than unguided reading. The benchmark measures it (4.5).
4. **Biases.** The largest measured biases are a reviewer taking on the author's framing, and giving
   in to an author's rebuttal in a follow-up conversation. Judging in a fresh session framed as an
   evaluation helps. So the author's task text becomes "claims to verify" (S41-D15), and rechecks
   stay fresh sessions.
5. **Measurement.** About 15 cases with one run each can screen for large effects only. At this
   repository's comparison sizes, a "two more detections" rule fires by chance 8 to 26% of the time.
   So 4.5 is a blinded screening study whose counts the owner decides from (S45-D4 to S45-D8).
6. **Failures.** Editing the tests is the best-measured failure of coding agents. No delivery
   problem here shows it yet, so a check that approved tests are unchanged is a slice-6 candidate.
7. **The owner's time.** The capacity to review runs out before the capacity to generate, and
   approvals that the human cannot really judge are a named anti-pattern. So every plan PR and final
   PR opens with a decision brief generated from the records (4.6, S46-D13).

## Corrections from the critique

- The report missed that the owner already approves intent, by merging the plan PR.
- About half of its recommendations were already in place or planned.
- Collapsing the severity scale, and building checklists from this repository's own misses, would
  have reversed the owner's decisions; neither is adopted.
- The reviewer cannot run commands; the launcher computes the evidence instead (4.2, S42-D5).
- Stage A's own data (no false blocker in 17 completed reviews, missed defects of absence, 5 of 22
  reviews failing the empty-review rule) point to what reviewers miss, not to false alarms.

Not adopted: reordering the prompt so that files come first (the reviewer reads files by tool, so the
evidence does not apply); merging stages (a stage can already be "none, with a reason"); restarting
instead of a fourth round; comparing reviewer models (Opus is the reviewer by the owner's reasoned
choice).

## Key sources

- Anthropic, Claude Code best practices and Code Review docs (accessed 2026-11-09):
  <https://code.claude.com/docs/en/best-practices>, <https://code.claude.com/docs/en/code-review>
- Anthropic, "Demystifying evals for AI agents" (2026-01-09):
  <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- SWR-Bench, LLM code review on real pull requests (2025-09): <https://arxiv.org/abs/2509.01494>
- Kim and Khashabi, rebuttal sycophancy in LLM judges (2025): <https://arxiv.org/abs/2509.16533>
- CheckEval, checklist-based LLM evaluation: <https://arxiv.org/abs/2403.18771>
- Porter, Votta and Basili, scenario-based inspections (IEEE TSE, 1995):
  <https://www.cs.umd.edu/~aporter/html/scenarios.html>
- ImpossibleBench, test gaming by coding agents (2025-10): <https://arxiv.org/abs/2510.20270>
- METR, recent reward hacking (2025-06-05): <https://metr.org/blog/2025-06-05-recent-reward-hacking/>
- Thoughtworks Technology Radar, Vol. 35 (2026-11): <https://www.thoughtworks.com/radar/techniques>
- Böckeler, spec-driven development tools (2025-10-15):
  <https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html>
