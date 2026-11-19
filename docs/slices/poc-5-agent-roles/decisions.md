# Slice decisions — poc-5-agent-roles

Decision page of slice `poc-5-agent-roles`: the owner's one page for the slice. It proposes the PoC's goal at the
level of its agents (each role, where its competence comes from, how it is started, how its reliability is measured
and the bar it must meet, and one change walked through every role), so that the owner can correct it before any
plan is written ([DPL-016, RC8](../../delivery_problem_log.md#dpl-016-slice-4-was-declared-done-before-its-goal-was-tested-so-the-owner-found-the-gaps-in-three-rounds-after-done)).
The detail behind each decision is in [`goal.md`](goal.md); the evidence is in [`research_roles.md`](research_roles.md)
and [`research_reliability.md`](research_reliability.md). Everything not quoted from the owner is the author's
proposal.

Last updated: 2026-11-19: goal page drafted for the owner's correction; no plan yet.

## Goal

The owner's words, in the working session of 2026-11-19 (also recorded in DPL-016, RC8):

1. "NO I think, we started the slice implementation without clear goal to be achieved and the internals of it and
   your decision where either short sighted and did not cover the goal we had in mind."
2. "Same goes for the complete SDLC setup and goal as well. We have not defined how relaibly different sub agents
   can be spinned (for example requirement agent who can create requirement like a requirement engineer looking at
   360 from the plan) or requirement review engieer or architect agent who architects the SW like an senior
   architects. Everything somehow feel like based on your prompting capability."
3. "Let's do this and we should use industry best practise all the time under our threat model."
4. "I am going to close this slice. All research goes into a new branch, is that okay?" (the author answered yes)

The PoC's goal today ([`plan.md`, Goal](../agentic-sdlc-poc/plan.md#goal)) names seven stages, their artifacts and
checks, and calls the cycle "reliable" without saying what that means or who does each stage.

**Proposed goal (the author's proposal, for the owner to correct).** It adds the agent level to the PoC's goal and
replaces none of it: the stages, artifacts and checks stay, and so does "without stale code or docs, maintainable,
secure and easy to understand". At the end of the PoC, each delivery role
([roles](goal.md#roles)) has a definition in the repository: a procedure and an output form taken from a named industry source, its
tools, and a pinned model ID and effort. Each role is started by one command whose inputs a tool computes, and each
run records the definition's hash, the model ID and the CLI version. Each role has met its reliability bar on a case
set frozen and hashed before its first measured run. One real open item (OPL-004, proposed in decision 11) has gone
through every role in order, with the owner deciding only what is the owner's (the plan, `owner:` answers, decision
concerns, the merge), and every miss is recorded with the stage that made it and the stage that caught it. Each
clause is true or false by reading the repository. "Reliable" then means: each role met its measured bar, and the
roles worked together once on a real change. One trial is one run, so it shows the cycle can work, not how often it
does; slice 8's evaluation (planted defects end to end) measures the cycle as a whole.

## What the slice builds

Proposed, no plan yet: (1) the six corrective actions of DPL-016 in `AGENTS.md` and the slice templates (decided on
2026-11-18), and what slice 4 left for the next slice's first change: decision 10's checklist wording and the Git
rules for the agent's new GitHub identity (#50); (2) a definition for each of the first roles (decision 2); (3) a
frozen case set for each, and one measured run against the bar (decision 5). The trial of the goal, OPL-004 through
every stage ([walk-through](goal.md#walk-through-of-one-change-opl-004)), comes in a later slice (decision 8).

## Decisions made

| When | Decision | The owner's words |
| --- | --- | --- |
| 2026-11-18 | Review prompts become agent definitions in files the launcher reads from the base branch, so author and reviewer agents are defined the same way ([direction](../agentic-sdlc-poc/slice_4_decisions.md#direction-for-the-next-slices-the-owner-2026-11-18), point 2) | "yes, record it" |
| 2026-11-18 | DPL-016's six corrective actions are adopted; the next slice's plan writes them into `AGENTS.md` and the templates first | "yes, add both DPLs and adopt all corrective actions" |
| 2026-11-19 | Slice 4 closes; all research goes into a new branch | "I am going to close this slice. All research goes into a new branch, is that okay?" (the author answered yes) |
| 2026-11-19 | Industry best practice throughout, within the threat model | "Let's do this and we should use industry best practise all the time under our threat model." |
| 2026-11-19 | Before any plan, the PoC's goal is defined at the level of its agents (DPL-016, RC8) | "We have not defined how relaibly different sub agents can be spinned …" (Goal, quote 2) |

## Decisions to make

| # | Decision | Options | Recommendation | Blocks |
| --- | --- | --- | --- | --- |
| 1 | Accept or correct the [proposed goal](#goal). At the end, someone checks: does the requirements engineer's definition exist, did its run meet the bar on a set hashed before the run, do OPL-004's records show each stage's role? | accept; correct the wording; replace it | accept: each clause is observable in the repository, and it says what "reliable" means | everything below |
| 2 | Which roles, and which first | (a) all nine at once; (b) the owner's three examples first: requirements engineer, requirements reviewer, architect; (c) (b) plus the architecture reviewer | (c): stages 2 and 3 then each have an author and a reviewer, so OPL-004 can be walked through them; the architecture reviewer already runs through the launcher and needs only a case set | the plan's scope |
| 3 | Who does discovery (plan, test plan, decision page) | (a) the main session, as today; (b) a defined role; (c) the main session interviews, a requirements role writes the plan | (a), with every later stage started fresh: the owner's words live in that conversation. RC8's cause sits here, in the author's default decisions, so the plan review gets this page's goal as intent and asks of each default whether it serves the goal | the requirements engineer's inputs |
| 4 | How a role is started ([options](goal.md#how-a-role-is-started)) | A launcher; B agent files; C headless script | A with B's file form: inputs computed, every run recorded, as the 2026-11-18 direction says for reviewers | the definition format |
| 5 | The bar and case counts. Example: a reviewer that misses 3 of 20 defects fails, even though it finds 17 | as [proposed](goal.md#how-reliability-is-measured-and-the-bar) (reviewers: 20 defect + 10 clean cases, at most 2 misses, 0 false blockers; authoring: 10 tasks × 3); tighter (30 defect cases, below 20%); counts without a bar | as proposed: the loosest bar 30 cases can decide, at a cost the PoC can carry; tighten later if the owner wants | the case sets |
| 6 | The budget | all nine roles, about USD 250 to 380; the first step, about USD 75 to 100 (USD 34 more with the architecture reviewer) | the first step, then decide the rest from its result | the measured runs |
| 7 | Paid standards (ISO/IEC/IEEE 29148, 42010, 29119, IEEE 1028) | the owner provides them and they are read in full; public summaries suffice, and each definition names the sources it rests on | summaries suffice: the take/leave choices rest on public sources that were read, and the bar, not the source, shows competence | the definitions' source lines |
| 8 | The [roadmap re-cut](goal.md#proposed-roadmap-re-cut) | as proposed; keep "one real cycle by hand" next | as proposed: a cycle run by undefined roles would repeat slice 4's gap | `plan.md`'s roadmap text |
| 9 | The additions G1 to G5 | approve each, or its simpler alternative | approve G1 to G5: without G3 and G4, "reliable" stays a claim | the plan |
| 10 | The owner's grading time for authoring roles where no gate decides | grade one run of each of the 10 tasks per role; grade all 30; no owner grading | one run per task (about 10 pass/fail verdicts per role): binary verdicts by the one expert, as the research advises | the authoring bar |
| 11 | The trial item for the real cycle ([walk-through](goal.md#walk-through-of-one-change-opl-004)). POC-D16 lets agent-run work take only items the owner wrote or labelled | OPL-004 (the issuer's static policy hash in audit events), labelled by the owner; another item the owner names | OPL-004: small, open, inside the system under test, and its closure criteria need a requirement, architecture, tests and code, so it passes all seven stages | the trial slice (decision 8) |
| 12 | Who answers and fixes a role's review findings, and who runs the stages ([orchestration](goal.md#orchestration-and-fixes)). Example: the requirements reviewer finds a requirement ambiguous | (a) the main session, as today; (b) the authoring role, started again fresh with the findings and the review record as computed inputs | (b) for findings: the role that wrote the artifact fixes it, as in an inspection, and no caller summarises the findings; the main session runs the stages in order and takes `owner:` answers and decision concerns to the owner | the authoring roles' definitions |

## Decision concerns

None yet.

## Discovered issues

None yet.

## Implementation review: the test-plan questions

At handoff.

## Review outcome

At handoff.

## How the user can check the work

At handoff. For this page: every external claim links to the research section it comes from.
