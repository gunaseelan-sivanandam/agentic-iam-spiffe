# Slice 4 — the owner's decision file

The one page the owner reads for slice 4, and its end-review page: the goal, what slice 4 builds in plain
words, the steps of the run, and every decision made or still to make. The plans, test plans and review records
under `docs/slices/poc-4-*/` are the working documents for the author and the reviewers. The author keeps this
file current during the run and says in it what was decided on the owner's behalf. At the end it holds the
checklists, the benchmark counts, every decision concern, every parked unit, every process-growth proposal and
every discovered issue with its disposition.

Last updated: 2026-11-09, 4.1 to 4.3 reviewed; 4.5a in review (round 1 answered).

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
| 4.1 | Implemented (`59d0291` to `9413020`) | Ended after round 2. Round 1: approvable; 0 blocking, 2 high, 6 medium, 5 low. Round 2: attempt 1 failed the read check (issue 5); attempt 2 accepted all 13 answers and found nothing new |
| 4.2 | Implemented (`381dc2b` to the round-2 fix) | Ended after round 2. Round 1: approvable; 0 blocking, 3 high, 4 medium, 3 low. Round 2: all 10 answers accepted, the 3 evidence entries explained; 1 new low finding, fixed |
| 4.3 | Implemented (`89b8f2b` to the round-2 fixes) | Ended after round 2. Round 1: attempt 1 failed the schema check (issue 6); attempt 2 not approvable: 2 blocking, 1 high, 3 medium, 2 low. Round 2: approvable; all 8 answers accepted; 2 new low findings, fixed |
| 4.5a | Implemented (benchmark identity, configurations, cases, scoring, blinding, canary, report) | Ended after round 2. Round 1: not approvable: 3 blocking, 3 high, 4 medium, 6 low. Round 2: attempt 1 failed the read check (issue 7); attempt 2 approvable, all 16 answers accepted; 1 new high, 2 medium, 1 low: the high and the mediums fixed, the low rejected |
| 4.4 | Implemented (`1750c8d`: six lists, the research record, `--stage`), then revised from the critique | Critique (S44-D10): Opus not approvable, 1 blocking, 5 high, 6 medium, 2 low; Sonnet's attempt 1 failed the read check (issue 8), attempt 2 approvable, 5 medium, 3 low. All 22 answered: 20 fixed, 1 high to the owner (decision concern 4), 1 low rejected. Implementation review, round 1: approvable (the blocking fix C-1 not re-raised); 1 high, 4 medium, 3 low; 7 fixed, 1 low rejected; ended |
| 4.5b | Running: FS-1 and FS-2 planted by a fresh session; the failed-Read probe done; the key names the lists' commit `04f8df4`; a dry run built all 46 prompts with their lists | — |
| 4.6 | Implemented on the branch: the seven-stage table and the rules moved into it, the templates, `scripts/review_brief.py`, the grill-me skill in the repository, the front-matter rule of the lint gate | Implementation review next |

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
| 4.2 | The computed inputs live in their own module, `scripts/review_inputs.py`, which the launcher loads | The launcher had grown past 1,400 lines; the file list, upstream items and evidence are one concern. The plan named only the launcher; this is code organisation, not a new mechanism |
| 4.2 | The evidence runs in a `git clone --shared` of the reviewed commit with the author's `PATH` | The tooling tests need Git history and the tools on the author's `PATH` (ruff, shellcheck); in a `git archive` export 38 of them failed. The environment is still only `PATH`, `LANG` and a scratch `HOME` (S42-D8) |
| 4.2 | The scratch `HOME` holds one link: the interpreter's user site-packages, at the place the interpreter computes from `HOME` (`.local` on Linux, `Library/Python/X.Y` for a macOS framework build) | pytest and its plugins are installed with `pip --user` under the author's `HOME`; without the link no evidence command runs. Only that directory is linked, not the rest of `~/.local` (review round 1, R1-6) |
| 4.2 | A `--path` that names a file the change deletes is refused, with a message that it is listed under deleted files | S42-D1 requires a `--path` to be in the diff; a deleted file cannot be opened, so the empty-review rule could never be met with it |
| 4.2 | The template and archive folders under `docs/slices/` are not treated as bundles when naming other plans the change touches | They are not slice bundles; listing them added noise to every prompt (found by the author's dry run) |
| 4.2 | Evidence entries are numbered EV1, EV2, … | So that no finding ID such as E1 can collide with an evidence entry in `accounted` |
| 4.3 | Record parsing and editing live in their own module, `scripts/review_records.py`, used by the launcher and by the record check | One parser for both, so the check reads records as the launcher writes them; the plan named only the launcher and the check |
| 4.3 | A task prompt file must end with a newline; records are read and written as exact bytes and split on newlines only | The Prompt block must hash as the task file does (S43-D1): the launcher refuses a task without a final newline, and keeps every other byte, so CRLF line ends, blank last lines and form feeds round-trip (review round 1, R1-4) |
| 4.3 | Recovery removes an unlogged trailing section only when it is exactly what the launcher writes before its start entry | So an author's text in a record is never cut, whatever headings or fences it holds (review round 1, R1-5) |
| 4.3 | A withheld attempt gets an end entry with status `withheld` (counts and paths only, never the report) | So the record keeps its withheld status and the log tells a withheld report from a killed launcher (review round 1, R1-8); slice 2 had logged no end entry |
| 4.3 | A rejected blocking or high finding is settled by the next round's acceptance, an `owner:` link in its own row, or a later round's `owner:` answer to the same finding ID | S43-D4's "or an `owner:` link" read so that a rejection the recheck re-raised can reach the owner without editing answers a recheck already read (review round 1, R1-3; decision concern 2) |
| 4.3 | A failed schema check logs the schema problems (fields and rules, never values) | The first launcher-written review attempt failed the schema check and its cause could not be found (issue 6) |
| 4.5a | `short+list` uses stage A's short prompt without its last sentence, which told the reviewer to use the retired kinds "blocking" and "advisory" (`tests/review_benchmark/prompts/short_list.md`); stage A's own files stay as measured | Every configuration gets the same severity rules (S45-D3); the old sentence contradicted them (4.1 review round 1, R1-3, deferred to #42) |
| 4.5a | The DPL-010 case (`RM-6`) has one expected finding, "the refusal paths have no test", whose places are all the untested refusal paths and which an absence finding naming them also detects | Ten separate expected findings would weigh this one miss ten times in the counts |
| 4.5a | Stage B's cases: the clean case CL-3 is `6feedfa` (a one-line README fix); the decoy DC-1 makes the harness's temp-file teardown non-fatal with `\|\| true` and a comment; the recheck case RC-1 puts stage A's PD-2 plant under a `fixed:` answer naming only `docs/test_spec.md` | Small, real or self-evidently correct changes; the decoy looks like a swallowed failure but is teardown after the status is decided |
| 4.5a | Artifact types per case: requirements (RM-3, PB-1), architecture and interfaces (PB-2), E2E tests (RM-2, RC-1, DC-1), code (RM-1, RM-4, RM-5, RM-6), plan and test plan (PB-3, CL-1, CL-2, CL-3) | The list each case gets (S44-D12); a README and the rulebook's own documents are reviewed with the plan-and-test-plan list |
| 4.5a | A result's prompt identity is the SHA-256 of the whole prompt and the reviewed commit | So any change to what the reviewer gets (the planted patch, the recheck inputs, the rules, the launcher's own sections) runs the review again (review round 1, H1) |
| 4.5a | A failed review of a defect case counts as a miss, with the case in the denominator and in the discordant pairs | S45-D5 says so for the recheck case; leaving failures out favoured setups that fail on hard cases (review round 1, B2) |
| 4.5a | A term counts only outside a verbatim quote of an expected line, in scoring and in the committed match rule | S45-D4's "a finding that only quotes the planted line goes to triage" (review round 1, B3) |
| 4.5a | The repeats of S45-D6 run with `--run --repeat <case>` (at most two cases, the two compared setups) and count apart; the second confirmer runs with `--sample-confirmation` and `--second-confirmation 0` or `1`, each session counted in the 60 | The runner had no path for either (review round 1, H2, M2) |
| 4.5a | Every case gets its base's rules, as the launcher gives a review the base branch's rules | Stage A gave real misses the rules of the reviewed commit, so RM-3 and RM-5 were judged by rules they themselves added (review round 1, L6) |
| 4.5a | PB-3 is a new slice's test plan that retires the M3.S4 suite while claiming its requirements stay proved; `REQ-M4-E4` has no other proof | The first version edited `trace/tests.yaml`, which is not the test-plan row S45-D5 names (review round 1, L5) |
| 4.5a | Stage A's results are read with the key committed at `c325e7d`; every call recorded for stage B counts against its 60, whatever key produced it | Stage A's report stays reproducible after the key's new version; a changed key cannot reset the budget |
| 4.5a | The marker "Planted defect" refuses only author-written plants (planted, decoy, recheck), not a real miss rebuilt by a patch; leak terms that already occur in this repository's documents were dropped | The 2026 plan text at `c4f9ca2` uses the phrase; a word the base already holds reveals nothing |
| 4.5b | FS-1 and FS-2 were planted by a fresh Opus session (high effort, Read, Grep and Glob only) on a copy of `e842e97`, given only the source sections of `research.md` (lines saying how a list used a source removed) and the three planted defect classes to avoid; it answered through a schema with the file, the anchor line, the new lines, the task line, the defect, why it is real here and match terms; the author made each answer a patch unchanged | S45-D5: the lists are measured on defects that did not shape them. The session never saw `docs/review_checklists/`, the candidate table, the DPL mapping or the drafts; it cost USD 0.92, outside the budget |
| 4.5b | In the key, the author dropped the session's term "token" from FS-1 and added the gateway's `upstream_headers` (`server.py` 314-324) as a second place, and added "timeout" to FS-2's terms | "token" occurs in almost every finding near that code; a finding placed at the header code that names the credential describes the same defect. FS-2 adds a hardening rule to an implemented bundle's test plan, as that bundle's own Increment 3 did; a finding that the bundle is frozen is an extra finding, not the expected one |
| 4.5b | The failed-Read probe (S45-D9) ran once, outside the budget: a confined session read an existing and a missing file; the stream marks the failed call `is_error: true`, and the launcher's parser counts it as failed and the other not (CLI 2.1.321, USD 0.05) | The read check relies on a failed Read never counting as read |
| 4.4 | The critique's Sonnet reviewer ran a second time after its first attempt failed the read check; S44-D10's "at most two runs" is read as two completed critiques | The failed attempt released no report, so the owner's second angle would otherwise be missing; the rerun cost one Sonnet session |
| 4.4 | The critique's fixes add questions only from sources quoted in `research.md`, five quotes of them fetched on 2026-11-10 (Google's functionality and documentation items, Fowler's quarantine and clock sections, the test pyramid's fake-server section, OWASP's threat model kept alongside the system); the lists now hold 12, 9, 10, 10, 11 and 12 questions | S44-D9: a question needs an industry source; S44-D3's limit of 12 |
| 4.4 | The research's "studies of LLM code review" are two public studies read from their abstracts: an industrial study of an LLM review tool (`cihan-acr`) and a benchmark of LLM review comments (`swr-bench`) | S44-D13 names such studies; the first record had none (4.4 review, F1). Their full texts were not read; only what the abstracts say is used |
| 4.5b | The planted `CLAUDE.md` of the canary is written as an ordinary review convention instead of an instruction that reads like an injection; a canary is done by its identity (planted texts, task, the two calls), not its case ID | The first twin declined the injection-like text; and with done-ness by case ID the reworded canary never ran |
| 4.5b | Stage-B cases run after a passed canary whose twin ran the planted hook, under the same CLI; the report gives each canary's validity and whether its twin ran the hook, with a sentence on what each shows | S45-D9's own refusal is a CLI version other than the canary's; 4.5a had also required a valid canary, which the launcher's prompt makes impossible (decision concern 6) |
| 4.6 | The grill-me skill is copied into `.claude/skills/grill-me/SKILL.md`; the user-level copy is left in place for the owner to remove | Removing a file from the owner's own folder is the owner's to do; the repository copy is the one this repository's rules name |
| 4.6 | The repository's grill-me completes the two sentences the user-level copy cuts off (its description and the second line end in `>`) and adds the assets question | `AGENTS.md` says grill-me always asks which keys, sockets and secrets a slice touches; the skill's text never asked it (discovered issue 10) |
| 4.6 | `scripts/review_brief.py` takes the review units a PR adds from the attempts logged since the merge-base, and names the review that found a finding by its `--stage` lists, or by its unit when it had none | The units of a PR are the ones its commits logged; slice 4's reviews ran without lists, so the unit is the only name they have |
| 4.6 | The step-reference check uses the plan's probe pattern, "step 1" to "step 4" | The delivery problem log's history says "steps 3–4" of a milestone; rewriting history entries would make them false |
| 4.2 | `invocation_from_entry` refuses entries logged by 4.1's launcher with a clear message, as it refuses earlier ones | 4.2 retires 4.1's prompt layout (the file list from `--path`, empty upstream and evidence sections); its plan did not say so (review round 1, R1-4) |

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
| 2 | Decision concern | 4.3 | S43-D3 fails a record whose answers changed after a recheck read them, and S43-D4 settles a rejected blocking or high finding only by the next round's acceptance or an `owner:` link. Read narrowly, a rejection the recheck re-raised could never be decided by the owner without editing answers the recheck read, and `make docs-check` would stay red (4.3 review round 1, R1-3). The check is also red between the answers commit and the recheck, by design | Keep the implemented reading: a later round's `owner:` answer to the same finding ID settles it. Confirm, or choose another way to record the owner's decision |
| 3 | Decision concern | 4.5 | S45-D7 makes the author the blinded confirmer, so the blinding rests on the author not looking: the token map and the results with their configurations sit in the same folder as the export (4.5a review round 1, L4) | Keep: under the honest-mistake threat model the author confirms before opening the results again, and the Sonnet sample measures agreement. The alternative, the owner confirming, costs the owner's time |
| 4 | Decision concern | 4.5 | S45-D5 has one recheck case, RC-1, whose answer is a false `fixed:`. It measures whether a recheck wording accepts a false fix, not whether it re-raises answers that hold (a correct rejection, a correct fix), so a wording that re-raises everything would score best (4.4 critique, C-2) | Before choosing the recheck wording, run a second recheck case with a correct rejection on both wordings: 2 more runs within the 60. Until then the report says what the recheck comparison cannot show |
| 6 | Decision concern | 4.5 | S45-D9 makes a canary valid only when its twin, without the launcher's flags, follows the planted `CLAUDE.md`. Two canaries ran (the second with the instruction written as an ordinary project convention): both twins ran the planted hook and both declined the instruction, as stage A's did. The canary prompt is the launcher's review prompt, which tells every reviewer that files are data, so no twin on it can be valid. Both confined reviewers followed nothing | Accept the runs after a passed canary whose twin ran the hook, as the runner now does: settings are shown to be kept out, instruction files are not. To show instruction files too, one canary pair with a neutral prompt instead of the review prompt (2 runs, within the 60) |
| 5 | Growth proposal | 4.1 | S41-D8's read check failed three whole reviews because `opened` named a file the reviewer had only found by Grep (issues 5, 7 and 8), each a full session lost. Failure it would still catch: a recheck that never read a file a `fixed:` answer names. Cost: a few lines in the launcher. Simpler alternative: keep the check and rerun, as now | The launcher drops from `opened` the files the attempt did not read and records them, and fails the attempt only when a file a `fixed:` answer names was not read |

No unit is parked.

## Discovered issues

| # | Issue | Found | Disposition |
| --- | --- | --- | --- |
| 1 | shellcheck is not installed locally, so 9 tests of `tests/tools/test_lint_changed_files.py` fail in a local `make tooling-test`, also on the base | 4.1, by the author | Outside the threat model (local environment); worked around with a scratch binary; CI has shellcheck |
| 2 | Stage A's benchmark prompts (`tests/review_benchmark/prompts/short.md`, `checklist.md`) still tell the reviewer to use the kinds "blocking" and "advisory", which the new schema rejects | 4.1 review round 1, R1-3 | Fixed in 4.5a: stage B's `short+list` uses `tests/review_benchmark/prompts/short_list.md`, the short prompt without that sentence; stage A's files stay as measured |
| 3 | The launcher computed the start entry's mandate hash apart from the prompt; the two could differ | 4.1, by the author's tests | Fixed in 4.1 before its first commit (`59d0291`): both come from one configuration object |
| 4 | Headings in quoted text could pass for the prompt's own sections | 4.1, by a dry run on this repository's prose | Fixed in 4.1 (`6476697`) |
| 5 | The first live recheck (4.1, round 2, attempt 1) listed files it had only grepped under `opened`, and accepted the decision-file fix without opening the file; the launcher failed the attempt, as S41-D8 intends. The prompt had said only "the files you read" | 4.1 review round 2 | Fixed in 4.1: the output section now says that only a Read opens a file, and that the launcher fails the report otherwise; round 2 runs again |
| 6 | The first launcher-written review attempt (4.3, round 1, attempt 1) failed the schema check after 8 minutes and about USD 2.75, and the log said only "does not match the report schema" | 4.3 review round 1 | Fixed in 4.3: the reason names the schema problems; one likely cause, a `flagged` note ending a finding ID with a full stop, is accepted now; round 1 ran again |
| 7 | The 4.5a recheck (round 2, attempt 1) again listed files under `opened` that it had not read with the Read tool (for B1, L1 and EV6), and did not read `docs/slices/README.md`, which a `fixed:` answer names; the launcher failed it, as S41-D8 intends, after a full medium-effort session. Attempt 2 ran on the next commit, which also holds 4.4, so its paths under review held 4.4's files too | 4.5a review round 2 | Kept as found: the read check did its job and the prompt's rule (only a Read opens a file) already says this. If it recurs, the growth proposal is to show the reviewer, before it answers, which named files it has not read |
| 8 | The 4.4 critique's Sonnet reviewer (attempt 1) named a file under `opened` for EV7 that it had not read; the launcher failed it. The third such failure | 4.4 critique | Rerun as attempt 2, which completed; growth proposal 5 in the table above |
| 9 | The author's self-review for 4.4 said the benchmark's dry run built every prompt with the lists; that dry run ran while the key's `lists_commit` was empty, so the +list prompts held no list, and the dry run, unlike a run, did not refuse it | 4.4 implementation review, F3 | Fixed: the dry run refuses as a run does; the dry run with `04f8df4` was checked to put each list in its prompts. A false claim caught by the review before merge |
| 10 | The grill-me skill in the owner's user folder has two lines cut off mid-sentence (they end in `>`) and does not ask which keys, sockets and secrets a slice touches, although `AGENTS.md` said it always does | 4.6, by the author when moving it in | Fixed in the repository copy; the user-level copy is the owner's |

## How the owner can check the work

- **Plant a defect** in a plan or in the code on the branch, and tell no one. Then see whether the reviews
  find it.
- **Read the decision brief** at the top of each PR: it lists what the author decided for you.
- **Question this file.** If an item here is unclear, the work behind it is probably unclear too.
