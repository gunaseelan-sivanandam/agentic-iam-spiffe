# The PoC's goal at the level of its agents (draft)

The working document behind the [decision page](decisions.md) of slice `poc-5-agent-roles`: what each delivery
role does, where its competence comes from, how it is started, how its reliability is measured and the bar it must
meet, and one change walked through every role. It is the author's draft for the owner to correct; the owner's
decisions are on the decision page, and the evidence is in [`research_roles.md`](research_roles.md) and
[`research_reliability.md`](research_reliability.md). Everything not quoted from the owner is the author's proposal.

## What "360°" and "like a senior engineer" mean here

The sources read do not use "360°". They describe the same idea as angles from which a requirement set must be
complete ([research_roles.md, section 2](research_roles.md#2-what-looking-360-from-the-plan-means-for-a-requirements-engineer)):

| Angle | Question a requirements engineer asks of the plan |
| --- | --- |
| Stakeholders and sources | Whose need is this, and where was it stated? |
| Context and scope | What is inside the boundary, what outside, which neighbours does it talk to? |
| Constraints | What may not be chosen freely? |
| Quality attributes | Which qualities matter, each as a *quality scenario*: a stimulus, its source, and a measurable response? |
| Failure and abuse | What happens when a dependency, input or step fails? How could the feature be used against its intent (an *abuse case*), and which must be defended? |
| Operation | How is it deployed, run, observed and retired? |
| Assumptions | Which facts are assumed rather than probed? |
| Verifiability | How would each requirement be shown to hold, and by which method? |
| Clarification | What is unclear enough that the agent must ask instead of guess? |

**"Like a senior engineer" cannot come from a persona line.** "Adding personas in system prompts does not improve
model performance" (measured on factual questions), and a strong single prompt matched multi-agent discussion
([Evidence](research_roles.md#evidence-on-role-definitions-versus-a-single-general-agent)). The sources support what
a role is given: a procedure and checklist from its body of knowledge, a structured artifact for the next role, a
check it can run with a bounded retry, a fresh context wherever it judges others' work, and tool limits the harness
enforces ([What this means](research_roles.md#what-this-means-for-defining-the-agents)). No study shows agents
defined from a body of knowledge beat persona agents ([Gaps](research_roles.md#gaps-what-this-research-did-not-find-or-could-not-verify)).
So, to "based on your prompting capability": the definition says what a role must do; only a measurement against a
bar shows that it does. A role is "senior" when it meets its bar, not because its file says so.

## Roles

Detail and quotes: [research_roles.md, section 1](research_roles.md#1-what-each-role-must-do-and-produce-and-what-makes-its-output-good)
and its [role table](research_roles.md#role--standard--what-good-output-looks-like--poc-fit). "Read" means the source
text was read; "summary", only a public summary; "not read", nothing of its text is used.

| Role (exists today?) | Stage | Produces | Competence source (read?) | Good output, in one line | Must not see or do |
| --- | --- | --- | --- | --- | --- |
| [Requirements engineer](research_roles.md#11-requirements-engineer-stage-2-discovery-feeds-it) (no) | 2 | `REQ` items, their `trace/tests.yaml` entries | NASA SE Handbook App. C, arc42 §10, OWASP abuse cases (read); INCOSE GtWR v4 (names only); ISO/IEC/IEEE 29148, IREB, SWEBOK (not read) | each requirement necessary, singular, unambiguous, verifiable by a stated method, with source and rationale; quality and security needs as scenarios | no design or code ("what, not how"); no guessing where it should ask |
| [Requirements reviewer](research_roles.md#12-requirements-reviewer) (launcher, list `requirements`) | 2 | findings with severity | Fagan inspection (summary); NASA App. C (read); IEEE 1028 (not read) | each defect tied to the characteristic it violates and its requirement; a verdict | never the author's reasoning; read-only; does not rewrite |
| [Architect](research_roles.md#13-software-architect-stage-3) (no) | 3 | `ARCH` sections, state inventory, `security/invariants.yaml` | arc42, C4, Nygard ADR, threat modeling manifesto, OWASP, STRIDE (read); ISO/IEC/IEEE 42010 (summary) | each significant decision as an ADR; quality scenarios answered; threats per trust boundary, each with a response | does not change requirements (asks); no code |
| [Architecture reviewer](research_roles.md#14-architecture-reviewer) (launcher, list `architecture-and-interfaces`) | 3 | findings | manifesto, OWASP (read); SEI ATAM (abstract only) | each quality scenario walked through the design, risks named, missing threats | as the requirements reviewer |
| [Test engineer](research_roles.md#15-test-engineer-unit-and-e2e-tests-first-stage-4) (no) | 4 | unit and E2E tests, `docs/test_spec.md` entries | Fowler TDD, AgentCoder, OWASP (read); ISO/IEC/IEEE 29119 (part titles); ISTQB (not read) | a test list from the requirements and abuse cases before code; each test fails first for its reason; oracles from the requirement | is not the implementer; never takes an expected value from the new code |
| Tests-first reviewer (launcher, lists `unit-tests`, `e2e-tests`) | 4 | findings | the slice 4.4 sources behind those lists (no section of its own in the research) | for each test, a wrong implementation that would still pass it, or none | as the requirements reviewer |
| [Implementer](research_roles.md#16-implementer-stage-5) (no) | 5 | code and configuration | Google eng-practices, MetaGPT, Claude Code best practices (read); CERT, ASVS via slice 4.4 | only approved behaviour, one self-contained change, every gate passing before "done" | does not edit the reviewed tests to pass them; bounded retries |
| [Code reviewer](research_roles.md#17-code-reviewer) (launcher, list `code`) | 5 | findings, the three test-plan questions | Google eng-practices, Claude Code best practices (read) | correctness findings with severity and evidence, against the spec | fresh context; tools `Read, Grep, Glob` only, enforced by the harness |
| [Final reviewer](research_roles.md#18-final--integrated-reviewer-stage-6) (launcher, final mode) | 6 | findings | MAST (read in part); IEEE 1028 (not read) | the whole change against the owner's recorded intent: requirements realised and tested, plan departures, documents made false | no question list; read-only |

*ADR* (architecture decision record): one or two pages per significant decision: context, decision, consequences.
*C4*: architecture views from system context down to code. *STRIDE*: six threat categories (spoofing, tampering,
repudiation, information disclosure, denial of service, elevation of privilege) used as prompts. *ATAM*: the SEI's
Architecture Tradeoff Analysis Method. *MAST*: a study of where multi-agent systems fail.

**Discovery.** Today the main session (the author) runs grill-me with the owner and writes `plan.md`, `test_plan.md`
and the decision page; the plan review is a launcher role. Proposed: the main session keeps discovery, since the owner's words
live in that conversation, and every later stage is a defined role started fresh, as Claude Code's best practices
advise ("Interview me until you could write the spec", then "start a fresh session to build from it";
[1.1](research_roles.md#11-requirements-engineer-stage-2-discovery-feeds-it)); [decision 3](decisions.md#decisions-to-make).

### Orchestration and fixes

The main session runs the stages in order: it starts each role through the launcher, passes nothing the launcher did
not compute, writes nothing a role produces, and takes `owner:` answers and decision concerns to the owner. When a
reviewer reports findings, the role that wrote the artifact fixes them, as in an inspection (the reviewer finds, the
author fixes): it is started again, fresh, with the findings and the review record as computed inputs, and answers
each finding in the review loop's table. Today the main session does both. This is the author's reasoning from the
inspection split in [research_roles.md, 1.2](research_roles.md#12-requirements-reviewer), not a measured result;
[decision 12](decisions.md#decisions-to-make).

## How a role is started

**The role** is fixed by a versioned definition in the repository: procedure, checklist, output form, tools, full
model ID and effort. **Its inputs** are fixed by a tool that computes them, as `scripts/run_independent_review.py`
does for reviewers today. A Claude Code subagent receives only what its caller writes: "The only content you pass
from parent to subagent is the Agent tool's prompt string"
([research_reliability.md, section 2](research_reliability.md#2-defining-agent-roles-so-that-every-start-gets-the-same-agent));
so a definition file alone fixes the role but not its inputs. **Each run records** the definition's hash, the model
ID, the effort and the CLI version (the launcher already records the mandate's hash per attempt).

| Option | How | For | Against |
| --- | --- | --- | --- |
| A. Extend the launcher | One definition file per role, read from the base branch (as the owner's direction of 2026-11-18 says for reviewers); the launcher computes inputs and records every run, for authoring roles too | inputs computed, every run recorded, one way for all roles; follows the recorded direction | authoring roles write files, so they need a working copy, not the reviewer's read-only frozen copy; the launcher grows |
| B. Claude Code agent files | `.claude/agents/<role>.md` (front matter: tools, model, effort; body: the procedure), started by the main session with the Agent tool | native, versioned; tool limits enforced | the caller chooses the inputs; a same-named definition elsewhere wins; an environment variable can override effort; runs are not recorded |
| C. Headless run per role | a thin script runs `claude -p --bare` with the role's file and a JSON schema for its output | "the same result on every machine"; checkable output | a second launcher; bare mode reads no OAuth credentials and needs an API key, a key helper or cloud-provider credentials |

Recommendation: **A, with the file form of B**: author and reviewer roles defined and started the same way, and no
caller picks a role's inputs. Unknowns ([Gaps](research_reliability.md#gaps-what-this-research-did-not-find-or-could-not-verify)):
temperature or seed control (if none, repeats are the only handle on variance); bare mode in the PoC's setup and
against the launcher's confinement; how a writing role is confined (the author's question). [decision 4](decisions.md#decisions-to-make).

## How reliability is measured, and the bar

**Terms.** `pass@k` is the chance that at least one of k runs succeeds; `pass^k`, that all k runs succeed
([1](research_reliability.md#reliability-is-consistency-over-repeated-runs-not-one-success)). A stage must work every
time, so the reading here is `pass^k` (an inference, the research says); 90% per run gives `pass^3` = 0.73. A *miss*:
a case's defect not reported as blocking, high or medium. A *false blocker*: a blocking, high or medium finding on a
clean case, since `AGENTS.md` has all three fixed (the author's reading; slice 4's key version 5 counted a medium the
same way). A *decoy*: a clean case that looks wrong but is not.

**Reviewer roles** ([Recommended measurement](research_reliability.md#recommended-measurement-for-the-poc)):

1. A frozen case set per role, hashed before any run: 20 defect cases (at least half real past misses from the
   repository's review records, since planted defects skew easy) and 10 clean cases (at least 2 decoys). No case
   shapes the role's text; cases from one file or slice count as one cluster.
2. The bar, decided one-sided at 95%: at most 2 misses in 20 shows a miss rate below 30%; 0 false blockers in 10 shows
   a false-blocker rate below 26%. Any other result is "bar not met": read the transcripts, fix the role, rerun.
3. Consistency: 3 runs on 10 of the cases (5 defect, 5 clean), with `pass^3` and every flipped verdict reported per
   case. With 10 cases this describes; it does not decide.

**Authoring roles** ([3](research_reliability.md#3-evaluating-agents-that-author-artifacts)): graded by outcome, first
by the existing deterministic gates (the artifact passes its stage's checks; a new test fails on the base code;
mutants are killed), then by the independent review's round-1 blocking, high and medium findings. A reviewer grades an authoring role only
once it has met its own bar, so each stage's reviewer is measured before its author (the author's reasoning). About 10 past
tasks per role with a reference answer, 3 runs each; the owner grades pass or fail where no gate decides. No LLM
judge (a model grading another's output) acts as a gate: judges show "self-enhancement" bias, and author, reviewer
and judge are all Claude; calibrating one needs about 100 labelled examples per failure mode, and below 60 the confidence intervals are
often too wide. The research gives no numeric bar
here. *The author's proposal:* a run passes when every gate passes and round 1 raises no blocking or high finding;
the bar is 10 of 10 tasks passing on their first run (failure rate below 26% at 95%), `pass^3` reported per task.

**Rerun trigger.** A role's frozen set reruns when its definition hash, model ID or CLI version changes.

**What the bar does not show.** "Below 30%" is loose: the role may still miss one defect in four. Below 20% needs 30
defect cases, below 10% 46 to 61 ([Statistics](research_reliability.md#statistics-error-bars-pairing-repeats-and-power)).
It shows a role is good enough to rely on, not which wording is better: a 20-point difference needs about 40 to 60
paired cases (at slice 4's 15 cases, 7 of 8 comparisons were within chance), so wordings are chosen by research.

**Cost.** Assumption: about USD 0.67 per reviewer call, slice 4's observed cost (105 calls, about USD 70). A reviewer
role takes about 50 runs (30 + 20), about USD 34; an authoring role 30 to 50 runs, about USD 20 to 34 if a run costs
what a review call costs (not measured; an implementer run likely costs more). All nine roles: about 370 to 450 runs,
USD 250 to 300, or about USD 380 if every authoring run is also graded by a review call (the author's arithmetic).
**Smaller first step:** the owner's three examples (requirements engineer, requirements reviewer, architect), about
110 to 150 runs, USD 75 to 100; the requirements reviewer alone, which the launcher already starts, about USD 34.

## Walk-through of one change: OPL-004

[OPL-004](../../open_problem_log.md#opl-004-capiss-policy-hash-is-static-rather-than-computed-from-opa-policy-source):
the capability issuer writes a fixed string (`CAPISS_POLICY_HASH`) as the `policy_hash` of every mint-decision audit
event, so the log cannot show which policy content made a decision. Proposed (POC-D16 takes only items the owner wrote or labelled; [decision 11](decisions.md#decisions-to-make)) because it is small, open, inside the
system under test, and its closure criteria need every stage: a requirement (provenance from actual policy content),
architecture (the hash boundary "documented in architecture"), tests ("the audit field changes when policy content
... changes") and code. It touches the capability issuer, so it is not a small slice and passes all seven stages.

0. **Discovery (main session, with the owner).** From OPL-004 and grill-me: `plan.md` (the files inside the hash,
   OPL-004's option 1 or 2, what an unreadable file does, the digest as hidden state), `test_plan.md`, the decision
   page; the plan review, `make docs-check`, `make lint`. **The owner decides** by merging the plan PR.
1. **Requirements engineer.** Receives from the launcher (option A) the merged plan, OPL-004's closure criteria and
   the audit requirements (`policy_id`, `policy_hash` in `docs/requirements.md`). Writes a requirement with source,
   rationale, verification method (an E2E test) and failure case, and its trace entry; `make qa-trace`. A miss such
   as "the hash of the policy", without saying which files, is caught next.
2. **Requirements reviewer** (`--stage requirements`). Reports it as ambiguous and not verifiable; the requirements engineer,
   started again with the findings, fixes ([orchestration](#orchestration-and-fixes)). Only `owner:` answers reach the owner.
3. **Architect.** Receives the reviewed requirement, the plan, the issuer's architecture sections, the state inventory
   and the deployment register. Writes the hash boundary, an ADR (where the digest is computed; consequences, such as
   whether OPA, the Open Policy Agent, and the issuer can read different policy versions), a state-inventory row and
   a STRIDE pass (repudiation, tampering). A read-only mount of the policy files for the issuer (OPA mounts them
   today) is a register change that `make qa-deploy` checks.
4. **Architecture reviewer** (`--stage architecture-and-interfaces`). Walks "an auditor tells two decisions under
   different policies apart" through the design; catches a version gap the ADR left out.
5. **Test engineer.** From the reviewed test plan, requirement, architecture and an interface skeleton: unit tests
   (same content, same digest; one changed byte changes it; an unreadable file fails as planned), an E2E test (change
   the policy, mint, the field differs), their `docs/test_spec.md` entries. Each fails on the base code, as the
   implementation log records; `make tooling-test`, `make test-lint`, `make unit-guard-check`.
6. **Tests-first reviewer** (lists `unit-tests` and `e2e-tests`). Which wrong implementation still passes: a digest of
   the file names, not their content; a test that only checks the field is not empty.
7. **Implementer.** Replaces the constant in `services/capability-issuer/app.py`; every gate, among them
   `make unit-mutation` (a mutant returning the old constant must be killed), `make e2e`, `make qa-evidence`.
8. **Code reviewer** (`--stage code`). The three test-plan questions: a wrong failure that still passes, a key that
   reaches a non-holder, names and purpose comments.
9. **Final reviewer** (final mode). The whole change against OPL-004's closure criteria and the owner's words, and the
   documents made false (the OPL-004 entry, `docs/STATUS.md`).
10. **Handoff.** **The owner** reads the decision page, its brief and every discovered issue, and merges.

## Industry practice and where the PoC departs

From [research_roles.md, section 4](research_roles.md#4-what-fits-the-poc-under-its-threat-model-and-what-is-production-weight):
a practice is left out when it serves many stakeholders, regulators or an organisation that a one-owner PoC lacks.

| Role | Take | Leave, and why under the threat model |
| --- | --- | --- |
| Requirements engineer | the individual and set characteristics as a checklist; verification method and source per requirement; quality and security needs as scenarios; abuse cases; ask, not guess | 29148's separate specification documents, requirement tools, change boards: one stakeholder and one trace model exist |
| Requirements reviewer | the reviewer finds, the author fixes; exit criteria; the characteristics as defect classes | inspection meetings, moderator roles, rate metrics: one reviewer per round, and the review loop is the exit rule |
| Architect | ADR per significant decision; quality scenarios answered; STRIDE per trust boundary with a response; C4 context and containers | full 42010 conformance and all twelve arc42 sections per change: built for many stakeholder groups and long-lived systems |
| Architecture reviewer | ATAM's core question (does each decision meet its scenario, where are the risks) | ATAM's multi-day workshop and stakeholder voting: needs many stakeholders |
| Test engineer | a test list before code; the designer is not the implementer; each test fails first | 29119-3's document set: `test_plan.md`, `trace/tests.yaml` and `docs/test_spec.md` hold that content |
| Implementer | one self-contained change with its tests; a check before "done"; bounded retries | full CERT and ASVS levels, supply-chain controls: outside the accepted simplifications |
| Code reviewer | fresh context; read-only tools enforced by the harness | several reviewers per change: no source read shows they catch more honest mistakes, and each costs tokens |
| Final reviewer | the whole change against the recorded intent (missing or wrong verification is one of MAST's three failure categories, and adding a check of the task's objective gave ChatDev +15.6%) | IEEE 1028 audits: they check an organisation's compliance, not a change |
| Measurement | a frozen set, a one-sided bar, real misses first | 1,000-case eval sets, 100 labels per failure mode, evaluation on every change, adversarial reviewer tests: built to compare models or for teams; the last is outside the threat model ([research_reliability.md, 4](research_reliability.md#4-a-proportionate-bar-and-measurement-for-this-poc)) |

## What this would add (growth proposals)

Each is a proposal under [Ask before growing](../../../AGENTS.md#poc-scope-and-proportion); [decision 9](decisions.md#decisions-to-make).

| # | Addition | Failure it catches | Cost | Simpler alternative |
| --- | --- | --- | --- | --- |
| G1 | One definition file per role | a role that differs between starts because a caller wrote its instructions afresh | nine files to write, review and keep current | the stage checklists as the author's guideline (today, S44-D8) |
| G2 | The launcher starts authoring roles | a caller that picks or summarises a role's inputs | launcher work for roles that write files | option B: agent files started by the main session |
| G3 | A frozen case set per role | a role relied on without evidence | about 30 cases per reviewer, 10 tasks per author; the owner's grading time | live figures from the attempt logs only: free, but cannot decide before use |
| G4 | One measured run per role against the bar | "reliable" left undefined | see Cost above | report counts without a bar |
| G5 | Per-run record and the rerun trigger | a role silently changed by a model, CLI or definition change | a few fields per attempt; about USD 34 per reviewer rerun | record only, never rerun |

## Proposed roadmap re-cut

The [roadmap](../agentic-sdlc-poc/plan.md#roadmap-slices-48-outline-not-approved-by-this-plan) puts one real cycle by
hand next. The author proposes defining and measuring the roles first, then running the cycle with them:

| Slice | Today's roadmap | Proposed |
| --- | --- | --- |
| 5 | One real cycle by hand | This slice: DPL-016's corrective actions, then the first roles ([decision 2](decisions.md#decisions-to-make)) defined and measured; folds in the author-prompts slice (#50) |
| 6 | Gates the run shows | The other roles defined and measured |
| 7 | Delivery loop | One real cycle with the defined roles: OPL-004 through every stage, the trial of the goal |
| 8 | Evaluation | Gates and the delivery loop only where slice 7 shows a need; the end-to-end evaluation against the bars already set |

Publication scanning (#21) and the QA-tooling gaps (#44, hidden; discovered issue 66 is tracked in #53), which
`docs/STATUS.md` puts before slice 5 when slice 5 was the real cycle, stay before the first real cycle;
the reviewer that runs tests (#52) keeps its own slice.

## What the research could not establish

- **Standards not read:** ISO/IEC/IEEE 29148, 42010, 29119, IEEE 1028, ISTQB, IREB, SWEBOK; INCOSE by names only; ATAM
  by its abstract. **Quotes** came from a fetch tool that runs a model over each page, not checked character by
  character. **No benchmark of requirements or architecture agents** was read, and no study compares body-of-knowledge
  agents with persona agents. **Not checked:** temperature or seed control, bare mode in the PoC's setup, how a
  writing role is confined, the cost of an authoring run.
