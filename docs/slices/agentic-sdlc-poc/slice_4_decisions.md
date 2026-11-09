# Slice 4 — the owner's decision file

The one page the owner reads for slice 4, and its end-review page: the goal, what slice 4 builds in plain
words, the steps of the run, and every decision made or still to make. The plans, test plans and review records
under `docs/slices/poc-4-*/` are the working documents for the author and the reviewers. The author keeps this
file current during the run and says in it what was decided on the owner's behalf. At the end it holds the
checklists, the benchmark counts, every decision concern, every parked unit, every process-growth proposal and
every discovered issue with its disposition.

Last updated: 2026-11-09, during 4.1's implementation review (round 1 answered, round 2 next).

## Goal (the owner's, 2026-11-09)

Deliver slice 4 (#33, sub-issues #38–#43) as approved in plan PR #48, on `poc/agentic-sdlc`, so that the next
slice can run the review process end to end without the owner checking by hand. The author works without
stopping for the owner; the owner reviews once at the end, with the benchmark counts in hand. While GitHub writes
go through the owner, all work stays local: local gates count during the run, CI's verdict counts when the owner
pushes at the end, and the author gives the exact push and PR commands then.

The author owns the how: the order of sub-slices, how to cut branches, what to probe first, when to use the new
launcher on later sub-slices. `AGENTS.md` and the six plans stay as written; a decision the author would change
becomes a decision concern. The owner's additions to the plans: each benchmark finding names the checklist
question that prompted it, where one did; and the launcher keeps 4.1's mandate wording until the owner chooses
from the counts at the end.

**Self-review before each independent review**, against the ways this repository has failed before
(`docs/delivery_problem_log.md`), answered in writing with the evidence for every sub-slice, in its review record.
The independent reviewer gets the answers as claims to verify, not as facts:
1. Which facts outside the repository did this depend on, and how was each probed (a command and its output, not
   a belief)?
2. For every check added or changed: what is the case it exists to catch, and where is the test that shows it
   fails on that case?
3. For every claim the plan or the record makes ("verbatim", "never", "always", "the launcher writes"): what
   checks it, mechanically?
4. For every finding fixed: which upstream choice caused it, and would changing that choice remove the mechanism
   instead of adding one?
5. How was this tried the way its next user will run it: in parallel, on real prose from this repository, from a
   clean session with only what the repository holds?
6. Does every rule, warning or decision written live where it will be read and survive this slice (`AGENTS.md`, a
   check, a record), not in a PR body or a plan note?
7. What was removed, and did it get the same review as what was added?

**Done when:**
- every decision ID in the six plans is implemented and proven, or marked rule-text-only with its `AGENTS.md`
  line; every retirement item is done;
- the 4.5b benchmark has run on the draft checklists and both mandate wordings, within 60 reviewer runs, each
  finding tied to the checklist question that prompted it where one did;
- a fresh reviewer with only the plans, the diff and the self-review answers reports no open blocker against the
  open mandate "what does the plan promise that the change does not do, and what does the change do that no plan
  asked for";
- this page holds the checklists, the counts, every decision concern, every parked unit, every process-growth
  proposal and every discovered issue with its disposition; `docs/STATUS.md` and the slice index are current; and
  one dry slice has run through the new process from a clean session, with what the next user would trip on
  recorded.

**Never stop for the owner; park instead:** a round-4 blocker is parked on its own branch and left out of the
final PR; a wrong-looking decision is implemented as written and recorded; growth is proposed, not added. The run
pauses only at a usage limit (and at 80% of the weekly limit) and resumes after the reset. No threat model
changes, no reading of frozen records except to check a claim, and OPL-005 to OPL-008 stay untouched.

## What slice 4 builds

| Part | In plain words |
| --- | --- |
| 4.1 Review prompts | The launcher writes every review prompt in a fixed order, opening with the open mandate, so no task text can narrow it. Rechecks must show which files they opened for each fix. Every finding gets a severity (blocking, high, medium, low) that says what must be fixed, and the stage where the problem started. |
| 4.2 Review inputs | The files to review come from the actual change, so none can be left out. The reviewer is told the plan and requirements the change belongs to. Tools compute untested lines, missing proofs and CI results, and the reviewer must account for every entry. |
| 4.3 Review records | The launcher writes the review records itself, and `docs-check` proves that each record matches what the reviewer saw and said, and that every finding has an allowed answer. |
| 4.4 Stage checklists | Short researched checklists for six kinds of work: plan, requirements, architecture, unit tests, E2E tests, code. Each says what blocks at that stage, and also serves as the author's guide. The research also drafts better mandate wording. |
| 4.5 Benchmark | Measures the short prompt with a checklist against the open mandate with a checklist, and today's mandate wording against the research-based draft, on about 15 cases, with blinded confirmation. At most 60 reviewer runs. |
| 4.6 Stage rules | The rulebook describes the seven delivery stages, every PR opens with a decision brief, and the grill-me skill moves into the repository. |

## The run

| Step | What happens | Needs the owner? |
| --- | --- | --- |
| 1 | 4.1, 4.2 and 4.3, each with its self-review and independent review | No |
| 2 | 4.5's first part (benchmark mechanics), then 4.4 (research, checklists, a critique by two models) | No |
| 3 | 4.5's benchmark runs and report: the draft checklists and both mandate wordings, within 60 reviewer runs | No |
| 4 | 4.6; the fresh end reviewer; one dry slice from a clean session | No |
| 5 | The owner's end review: push, PR, merge, and choose the default setup and the mandate wordings from the counts (the wording change follows in its own commit) | **Yes, once** |

Parked units, decision concerns and growth proposals collect below as the run goes.

### Progress

| Part | State | Review |
| --- | --- | --- |
| 4.1 | Implemented (`59d0291` to `6476697`; round-1 fixes in the next commit) | Round 1: approvable; 0 blocking, 2 high, 6 medium, 5 low; all answered; round 2 (recheck) next |
| 4.2 to 4.6 | Not started | — |

## Decided by the author during the run

What the author decided on the owner's behalf. Each stays within the plans; a change to a plan's decision would be
a decision concern below instead.

| Part | Decision | Why |
| --- | --- | --- |
| 4.1 | 4.1's own implementation review runs with the branch's launcher, the one under review, not with the base's | This is how the next user runs it, and it was the launcher's first live run with the new schema. The circularity is limited: the rules come from the base branch, the mandate texts were compared with the plan by a script, and the reviewer reads the launcher's code |
| 4.1 | Text quoted from a file or the author (the rules, the task text, the answers) is a fenced block in the prompt | A dry run on this repository's own prose showed that its `## ` headings read like the prompt's sections, so a task text could imitate a Mandate or Output section. This is how S41-D1's fixed sections are kept, not a new mechanism |
| 4.1 | A recheck is refused before any call when its answers table does not answer the earlier report: a finding without a row, a row for an unknown ID, a changed severity, an answer the severity does not allow | Review round 1 (R1-4): the plan put this check only in 4.3's record check, so rechecks run before 4.3 exists could drop a finding. One function holds the rule, and 4.3's check will use it too |
| 4.1 | An `owner:` answer may link to a tracked document, such as this file, as well as to a URL | While GitHub writes go through the owner, this file is where the owner decides |
| 4.1 | `invocation_from_entry` refuses an attempt logged before 4.1 with a clear message instead of rebuilding it | The old prompt layout is retired with S41-D1; its hashes still identify what was reviewed (R1-7). The plan's retirement list did not name this; it is recorded here |
| 4.1 | The benchmark report shows blocking-only detections beside all detections, and counts an unmatched high finding on a clean case as a false alarm | S41-D13 counts high findings as detections, so the penalty must count them too (R1-1, R1-2). Stage A's values stay as they were |
| 4.1 | Local runs of `make tooling-test` use a shellcheck 0.10.0 binary taken from the `shellcheck-py` wheel into a scratch directory | shellcheck is not installed on this machine; without it 9 lint tests fail (on the base too). CI's runner has it |

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
| 2026-11-09 | This file as the owner's one page; planted defects as the owner's own check | "Yes" |
| 2026-11-09 | The goal above: work without stopping, review once at the end; checklist question per benchmark finding; 4.1's mandate wording kept until the owner chooses; a dry slice at the end instead of a real cycle after 4.3 | "save the revised goal" |

## Decisions to make

| # | Decision | When | Options | Recommendation |
| --- | --- | --- | --- | --- |
| 1 | The evidence secret check: a credential value must look like a token (20 characters or more, or a digit), and values in code spans and quotes are found | At the end; already in effect since #48 | Keep; change | Keep: every credential here looks like a token, and CI's full E2E run passed |
| 2 | Default review setup and mandate wordings (initial, recheck, final) | At the end | From the benchmark's counts | Given with the counts |
| 3 | Recreate the hidden issues under the owner's account if GitHub has not answered | At the end, or about 2026-11-23 if the owner is around | Recreate the open ones; keep waiting | Recreate the open ones |

## Parked units, decision concerns and growth proposals

| # | Kind | Part | Item | The author's recommendation |
| --- | --- | --- | --- | --- |
| 1 | Decision concern | 4.1 | S41-D8 makes a recheck read only the files a `fixed:` answer names. A `rejected:` answer that rests on a file ("already covered by `tests/…::test_x`") can be accepted without opening it, though the recheck mandate says to open "the tests that cover them" (4.1 review round 1, R1-5) | Extend the read check to every repository path any answer names; it is a few lines on data the launcher already has. Implemented as written until the owner decides |

No unit is parked, and no process growth is proposed yet.

## Discovered issues

| # | Issue | Found | Disposition |
| --- | --- | --- | --- |
| 1 | shellcheck is not installed locally, so 9 tests of `tests/tools/test_lint_changed_files.py` fail in a local `make tooling-test`, also on the base | 4.1, by the author | Outside the threat model (local environment); worked around with a scratch binary; CI has shellcheck |
| 2 | Stage A's benchmark prompts (`tests/review_benchmark/prompts/short.md`, `checklist.md`) still tell the reviewer to use the kinds "blocking" and "advisory", which the new schema rejects | 4.1 review round 1, R1-3 | Deferred to 4.5a (#42), which builds stage B's `short+list` from the short prompt; stage A's files stay as measured |
| 3 | The launcher computed the start entry's mandate hash apart from the prompt; the two could differ | 4.1, by the author's tests | Fixed in 4.1 before its first commit (`59d0291`): both come from one configuration object |
| 4 | Headings in quoted text could pass for the prompt's own sections | 4.1, by a dry run on this repository's prose | Fixed in 4.1 (`6476697`) |

## How the owner can check the work

- **Plant a defect** in a plan or in the code on the branch, and tell no one. Then see whether the reviews
  find it.
- **Read the decision brief** at the top of each PR: it lists what the author decided for you.
- **Question this file.** If an item here is unclear, the work behind it is probably unclear too.
