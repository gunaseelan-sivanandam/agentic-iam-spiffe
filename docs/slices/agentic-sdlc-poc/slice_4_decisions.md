# Slice 4 — the owner's decision file

The one page the owner reads for slice 4: its goal, what it builds in plain words, what happens next, and
every decision made or still to make. The plans, test plans and review records under `docs/slices/poc-4-*/`
are the working documents for the author and the reviewers. This file is updated after every sub-issue; each
update says what the author decided on the owner's behalf.

Last updated: 2026-11-09, before the implementation starts.

## Goal (draft for the owner to confirm)

1. **What it is for:** every review in the delivery process catches what the owner used to catch, the
   missing things above all (requirements without tests, gates in the wrong place, untested refusal paths).
2. **How:** an open mandate that no author can weaken, short research-based checklists as the minimum,
   inputs and evidence computed by tools, and review records the repository checks itself.
3. **Done when:** all of it is built and tested, a benchmark has measured it, and the owner has chosen the
   default setup and the mandate wording from the benchmark's counts.
4. **Out of scope:** prompts for authors (the next slice), comparing reviewer models, Codex.
5. **Proof the owner can trust:** results, not documents: the benchmark, a small real delivery cycle, and
   defects the owner plants without telling anyone.

## What slice 4 builds

| Part | In plain words |
| --- | --- |
| 4.1 Review prompts | The launcher writes every review prompt in a fixed order, opening with the open mandate, so no task text can narrow it. Rechecks must show which files they opened for each fix. Every finding gets a severity (blocking, high, medium, low) that says what must be fixed, and the stage where the problem started. |
| 4.2 Review inputs | The files to review come from the actual change, so none can be left out. The reviewer is told the plan and requirements the change belongs to. Tools compute untested lines, missing proofs and CI results, and the reviewer must account for every entry. |
| 4.3 Review records | The launcher writes the review records itself, and `docs-check` proves that each record matches what the reviewer saw and said, and that every finding has an allowed answer. |
| 4.4 Stage checklists | Short researched checklists for six kinds of work: plan, requirements, architecture, unit tests, E2E tests, code. Each says what blocks at that stage, and also serves as the author's guide. The research also drafts better mandate wording. |
| 4.5 Benchmark | Measures the short prompt with a checklist against the open mandate with a checklist, and today's mandate wording against the research-based draft, on about 15 cases, with blinded confirmation. At most 60 reviewer runs. |
| 4.6 Stage rules | The rulebook describes the seven delivery stages, every PR opens with a decision brief, and the grill-me skill moves into the repository. |

## What happens next

| Step | What happens | Needs the owner? |
| --- | --- | --- |
| 1 | 4.1, then 4.2, then 4.3, each built and independently reviewed | No |
| 2 | One small real delivery cycle, on a backlog item the owner picks, run through the reviews built so far | **Yes: pick the item** |
| 3 | 4.5's first part (benchmark mechanics), then 4.4 (research, checklists, a critique by two models) | No |
| 4 | 4.5's runs and report | **Yes: choose the default setup and the mandate wordings** |
| 5 | 4.6, then the final PR | **Yes: push, open, merge** (the agent account is suspended) |

The author stops between steps only where the owner is needed. Everything else is in this file after each step.

## Decisions made

| When | Decision | The owner's words |
| --- | --- | --- |
| 2026-11-08 | Slice 4 runs as sub-issues: one plan PR, one final PR | "Plan PR, then one final PR" |
| 2026-11-08 | The open mandate is the default; checklists are the minimum | "checklist alone is not completely reliable" |
| 2026-11-08 | Findings get a severity order | "maybe a priority or severity order?" |
| 2026-11-08 | Checklists come from industry research, not only from our own misses | "we have to look or research for industry best practice review checklist" |
| 2026-11-08 | Every review prompt, including the mandate, is researched and measured | "if mandate prompts are going to be used, then it must be analyzed" |
| 2026-11-09 | Research how the industry runs agent-first delivery before planning further | "Maybe we should check first how indusctry approaches agent first Sw delivery" |
| 2026-11-09 | No short-prompt-only setup; compare short prompt + checklist with open mandate + checklist | "I do not want short prompts, it was evident that it produced narrow results" |
| 2026-11-09 | Keep four severity levels; blinded screening benchmark, decided from counts; no model comparison; decision brief on every PR; two candidate gates for slice 6 | "I accept your recommendations for my decisions" |
| 2026-11-09 | Slice 4 is about reviews only; author prompts get their own slice next | "let's continue this slice for just review, after this let's run a new slice of author prompts and benchmark them" |
| 2026-11-09 | Plans merged (PR #48) | merged by the owner |
| 2026-11-09 | Goal, read-back, a small real cycle after 4.3, planted defects, this file | "Yes" |

## Decisions to make

| # | Decision | When | Options | Recommendation |
| --- | --- | --- | --- | --- |
| 1 | Confirm or change the goal above | Now | Confirm; change any line | Confirm |
| 2 | The backlog item for the small real cycle | Before step 2 | Any small item you wrote or labelled | Something you know well, so you can judge the result |
| 3 | The evidence secret check: a credential value must look like a token (20 characters or more, or a digit), and values in code spans and quotes are found | Any time; already in effect since #48 | Keep; change | Keep: every credential here looks like a token, and CI's full E2E run passed |
| 4 | Default review setup and mandate wordings (initial, recheck, final) | After step 4 | From the benchmark's counts | Decided then |
| 5 | Recreate the hidden issues under your account if GitHub has not answered | About 2026-11-23 | Recreate the open ones; keep waiting | Recreate the open ones |

## How the owner can check the work

- **Plant a defect** in a plan or in the code on the branch, and tell no one. Then see whether the reviews
  find it.
- **Read the decision brief** at the top of each PR: it lists what the author decided for you.
- **Question this file.** If an item here is unclear, the work behind it is probably unclear too.
