# Research — what industry practice says each delivery-stage agent must do

This document collects industry best practice for the roles behind the PoC's seven stages (requirements
engineer, requirements reviewer, software architect, architecture reviewer, test engineer, implementer, code
reviewer, final reviewer), and the published evidence on role-based multi-agent software engineering, so that the
agents behind each stage can be defined from a body of knowledge rather than from prompting skill alone. It builds
on, and does not repeat, the slice 4.4 research behind the review checklists
([`research.md`](../../../docs/slices/poc-4-4-stage-checklists/research.md), cited below as `[4.4:<key>]`), and it
judges every practice against the PoC's delivery threat model (honest agent mistakes, no deliberate attacks;
production hardening out of scope, `AGENTS.md` "PoC scope and proportion"). Nothing here is approved: every
"take" below is a candidate for the user's decision under "Ask before growing".

## Method

- Pages were read on 2026-11-19 through a web-fetch tool that runs a small model over the page; quotes are as that
  tool returned them, short, and were not re-checked character by character against the page. Where the tool said
  it paraphrased (for example table numbers), this document says so.
- A paid or account-only standard whose text could not be read is marked **not read**, and nothing of its text is
  used; a structure seen only in a search result is marked **search result only**.
- Web searches used generic queries only.
- What the repository already has was checked by reading `AGENTS.md`, the Goal section of
  `docs/slices/agentic-sdlc-poc/plan.md`, the slice 4.4 research and the heads of `docs/review_checklists/*.md`.
  Two facts matter below: each checklist is already "the author's guideline before writing it (S44-D8)", and the
  repository defines no subagents (`.claude/agents/` does not exist; the only skill is `grill-me`).

## 1. What each role must do and produce, and what makes its output good

### 1.1 Requirements engineer (stage 2; discovery feeds it)

- **ISO/IEC/IEEE 29148:2018** — **not read** (paid; the sample PDF could not be decoded). **Search result only:**
  its table of contents separates "5.2.5 Characteristics of individual requirements" from "5.2.6 Characteristics
  of a set of requirements" (reseller previews listed at
  <https://standards.iteh.ai/catalog/standards/iso/8cf2bc2b-8b5e-4907-a82a-d1c5676c9e85/iso-iec-ieee-29148-2018>).
  The point that matters: a good requirement set is judged twice, each requirement alone and the set as a whole.
- **INCOSE Guide to Writing Requirements v4** — the summary sheet
  (<https://www.incose.org/docs/default-source/working-groups/requirements-wg/guidetowritingrequirements/incose_rwg_gtwr_v4_summary_sheet.pdf>)
  returned HTTP 403 again. **Search result only** (secondary sources): the nine characteristics of an individual
  requirement are C1 Necessary, C2 Appropriate, C3 Unambiguous, C4 Complete, C5 Singular, C6 Feasible,
  C7 Verifiable, C8 Correct, C9 Conforming, with further characteristics for sets (C10 onward). Definitions were not
  read from INCOSE and are not quoted.
- **NASA Systems Engineering Handbook, Appendix C** (public; already in `[4.4:nasa-req]`,
  <https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/>): "Can the criteria for verification
  be stated?"; "Have all assumptions been explicitly stated?"; "Are requirements free of implementation specifics?
  (Requirements should state what is needed, not how to provide it.)"
- **Requirement attributes** (`[4.4:reqview-29148]`, <https://www.reqview.com/doc/iso-iec-ieee-29148-templates/>):
  "Verification method — Test, Demonstration, Inspection or Analysis"; "Rationale": "Explanation of the reason why
  the requirement is needed"; "Source of the requirements".
- **Quality requirements as scenarios** (arc42 section 10, <https://docs.arc42.org/section-10/>): "Quality scenarios
  make quality requirements concrete and allow to decide whether they are fulfilled"; "Ensure that your scenarios
  are specific and measurable."; a scenario names its "Source/Stimulus: Who or what initiates or triggers a
  behaviour, reaction or action." and its "Metric/Acceptance Criteria: A response including a _measure_ or
  _metric_".
- **Security requirements from abuse cases** (OWASP Abuse Case Cheat Sheet,
  <https://cheatsheetseries.owasp.org/cheatsheets/Abuse_Case_Cheat_Sheet.html>): an abuse case is "A way to use a
  feature that was not expected by the implementer, allowing an attacker to influence the feature"; "the abuse
  cases selected to be addressed must become security requirements in each feature specification section".
- **IREB CPRE Foundation Level** — **not read**: the handbook needs an IREB account (redirect to
  `cockpit.ireb.org`) and the syllabus mirror failed TLS verification. **SWEBOK v4** — **not read**: the PDF of its
  chapters could not be decoded by the tool; a search summary says its Software Requirements knowledge area covers
  "eliciting, analyzing, specifying, validating, and managing software requirements" (search result only,
  <https://computer.org/education/bodies-of-knowledge/software-engineering/topics>).
- **Agent practice** (Anthropic, Claude Code best practices, <https://code.claude.com/docs/en/best-practices>): the
  recommended spec step is an interview, "Interview me until you could write the spec, then write it to SPEC.md.",
  after which "start a fresh session to build from it, so the build begins with a clean context and a written
  definition of done."

**Good output:** each requirement is necessary, singular, unambiguous, verifiable (with a stated verification
method), free of implementation, traced to its source with a rationale; quality and security requirements are
measurable scenarios; assumptions are explicit; the set is complete and consistent as a whole.

### 1.2 Requirements reviewer

- **IEEE 1028-2008** — **not read** (paid; as in `[4.4:ieee1028]`).
- **Inspection** (public summary of Fagan inspection, <https://en.wikipedia.org/wiki/Software_inspection>): "The
  goal of the inspection is to identify defects."; "The process should have entry criteria that determine if the
  inspection process is ready to begin."; "The process is ended by the moderator when it satisfies some predefined
  exit criteria."; "The author makes changes to the work product according to the action plans from the inspection
  meeting." (The reviewer finds; the author fixes.)
- **Criteria:** the same characteristics the author writes to (1.1), read as defect classes: NASA's "Are the
  requirements clear and unambiguous?" and "Are the requirements stated consistently without contradicting
  themselves or the requirements of related systems?" (`[4.4:nasa-req]`).
- The repository's [`requirements` checklist](../../../docs/review_checklists/requirements.md) already rests on
  these sources.

**Good output:** defects, each tied to the characteristic it violates and the requirement it is in; no rewrite of
the requirement by the reviewer; a verdict against stated exit criteria.

### 1.3 Software architect (stage 3)

- **ISO/IEC/IEEE 42010** — **not read** (paid; the public conceptual-model site refused the connection). Public
  summary (<https://en.wikipedia.org/wiki/ISO/IEC_42010>): it "defines requirements on the description of system,
  software and enterprise architectures."; "the standard makes a strict distinction between architectures and
  architecture descriptions."; its revision aimed at "architecture decision capture; and correspondences for model
  and view consistency." (Stakeholders, concerns, viewpoints and views are the standard's known terms, but their
  definitions were not read.)
- **arc42** (<https://docs.arc42.org/section-10/>, which lists the template's sections): "01 Introduction and Goals",
  "02 Constraints", "03 Context and Scope", "04 Solution Strategy", "05 Building Block View", "06 Runtime View",
  "07 Deployment View", "08 Crosscutting Concepts", "09 Architecture Decisions", "10 Quality Requirements",
  "11 Risks and Technical Debt", "12 Glossary"; and "quality requirements will have a lot of influence on
  architectural decisions".
- **C4 model** (<https://c4model.com/>): "A set of hierarchical abstractions - software systems, containers,
  components, and code."; "An additional set of supporting diagrams - system landscape, dynamic, and deployment.";
  "Notation independent".
- **Architecture decision records** (Nygard, <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>):
  architecturally significant decisions are those that affect "the structure, non-functional characteristics,
  dependencies, interfaces, or construction techniques."; Context "describes the forces at play"; Decision
  "describes our response to these forces."; a later decision marks an earlier one "superseded" with a reference;
  "The whole document should be one or two pages long."
- **Threat modeling** (<https://www.threatmodelingmanifesto.org/>): "What are we working on?", "What can go
  wrong?", "What are we going to do about it?", "Did we do a good enough job?"; it values "Continuous refinement"
  over a single delivery. OWASP adds the model's content: "trust boundaries, data flows, data stores, processes"
  and "Each threat identified earlier must have a response." (`[4.4:owasp-threat]`); STRIDE's six categories serve
  as prompts (`[4.4:stride]`).

**Good output:** context and scope; building blocks with their interfaces; runtime views of the security-relevant
flows; deployment; each significant decision with its forces, choice and consequences; quality scenarios the
design answers; per trust boundary touched, the threats (STRIDE as prompts) each with a response.

### 1.4 Architecture reviewer

- **ATAM** (`[4.4:atam]`, <https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/>): decisions must
  be ones that "are advisable ones that appropriately mitigate risks", against quality attributes "such as
  performance, availability, security, and modifiability". The report's full method was not read.
- **Threat model review:** the manifesto's fourth question, "Did we do a good enough job?", and OWASP's "Does the
  DFD (or comparable) accurately reflect the system?" (`[4.4:owasp-threat]`).

**Good output:** each quality scenario walked through the design, with the decisions it depends on and the risks
where it fails; the model checked against the system as built; missing threats or responses.

### 1.5 Test engineer, unit and E2E, tests first (stage 4)

- **ISO/IEC/IEEE 29119** — **not read** beyond its part titles (<https://softwaretestingstandard.org/>): "Part 1:
  Concepts and Definitions", "Part 2: Test Processes", "Part 3: Test Documentation", "Part 4: Test Techniques".
  **ISTQB CTFL v4** — **not read** (as in `[4.4:istqb]`).
- **Tests first** (Fowler, <https://martinfowler.com/bliki/TestDrivenDevelopment.html>): "there's also a vital
  initial step where we write out a list of test cases first."; "Write a test for the next bit of functionality
  you want to add."; "thinking about the test first forces us to think about the interface to the code first."
- **A test designer separate from the programmer** (AgentCoder, <https://arxiv.org/abs/2312.13010>): three agents,
  "the programmer agent, the test designer agent, and the test executor agent."; "AgentCoder (GPT-4) achieves 96.3%
  and 91.8% pass@1 in HumanEval and MBPP datasets" against "state-of-the-art obtains only 90.2% and 78.9% pass@1".
- **Negative tests from abuse cases** (OWASP Abuse Case Cheat Sheet, above): "Use abuse-case models for an
  application to serve as fuel for identification of concrete security tests".
- Test quality (smells, pyramid, non-determinism) is in `[4.4:test-smells]`, `[4.4:fowler-pyramid]`,
  `[4.4:fowler-nondeterminism]`.

**Good output:** a test list derived from the requirements and the abuse cases before any code; each test fails
first for the reason it exists; each test's oracle comes from the requirement, not from the implementation.

### 1.6 Implementer (stage 5)

- **Small, self-contained changes with their tests** (Google eng-practices,
  <https://google.github.io/eng-practices/review/developer/small-cls.html>): "the right size for a CL is one
  self-contained change"; "The CL makes a minimal change that addresses just one thing."; "A CL that adds or changes
  logic should be accompanied by new or updated tests for the new behavior."
- **A check to run** (Claude Code best practices, above): the commonest failure is "Claude said it was done and it
  wasn't quite, usually because it had no way to check its own work."
- **Executable feedback** (MetaGPT, <https://arxiv.org/html/2308.00352>, section 3.3): "we introduce an executable
  feedback mechanism to improve the code iteratively."; "This iterative testing process continues until the test is
  passed or a maximum of 3 retries is reached."
- Secure coding: `[4.4:cert]`, `[4.4:asvs]`.

**Good output:** only the approved behaviour, in small changes, each with its tests and the gates passing before it
is called done.

### 1.7 Code reviewer

- The standard and what to look for are in `[4.4:google-standard]` and `[4.4:google-looking-for]`.
- **Independence** (Claude Code best practices, above): a review "By someone who didn't write the code ... in a
  fresh subagent that never saw your conversation. It isn't swayed by the reasoning that produced the code."; "A
  fresh reviewer does help, because it hasn't seen your reasoning, which is a different thing from delegating."
- **Scope and tools:** "A reviewer that's asked to find problems will always find *something*. If you fix every
  finding, you end up with extra abstraction layers and tests for cases that can't happen."; give the reviewer
  "only `tools: Read, Grep, Glob`. Now it's a reviewer that can't edit anything, and that limit is enforced by
  Claude Code rather than requested in a prompt."

**Good output:** findings that affect correctness or the approved design, each with severity and evidence, against
the spec the code was built from.

### 1.8 Final / integrated reviewer (stage 6)

- **IEEE 1028** (audits, technical reviews) — **not read**.
- **Verification is where multi-agent systems fail most** (MAST, <https://arxiv.org/html/2503.13657>): "No or
  incomplete verification" (FM-3.2, 8.20%) and "Incorrect verification" (FM-3.3, 9.10%); a +15.6% gain on ProgramDev
  came from adding a high-level verification step (the tool's summary of section 4).
- **Against the spec** (Claude Code best practices, the example reviewer): "Compare the changed files against the
  spec you're given, check that every requirement is implemented and the listed edge cases have tests".

**Good output:** the whole change against the user's recorded intent: every requirement realised and tested,
departures from the plan, and documents the change made false (as the plan's Goal section already asks).

## 2. What "looking 360° from the plan" means for a requirements engineer

The literature read here does not use "360°"; it covers the same idea as a set of angles from which a requirement
set must be complete. Each angle below has a public source and a question a requirements agent can ask of a plan.

| Angle | Question to ask of the plan | Source and quote |
| --- | --- | --- |
| Stakeholders and sources | Whose need is this, and where was it stated? | ReqView attribute "Source of the requirements" (`[4.4:reqview-29148]`); 42010's stakeholders and concerns (not read) |
| Context and scope | What is inside the system boundary, what outside, which neighbours does it talk to? | arc42 "03 Context and Scope"; C4 "system context" (<https://c4model.com/>) |
| Constraints | What may not be chosen freely (platform, rules, budget)? | arc42 "02 Constraints" |
| Quality attributes | Which qualities matter, each as a measurable scenario? | ISO/IEC 25010: "The product quality model defined in ISO/IEC 25010 comprises the nine quality characteristics" (<https://iso25000.com/index.php/en/iso-25000-standards/iso-25010>; only four names were readable: "Functional Suitability", "Performance Efficiency", "Compatibility", "Interaction Capability"); arc42 quality scenarios (1.1) |
| Failure | What happens when a dependency, input or step fails? | arc42 tip "Consider fault/error/failure (quality) scenarios!!" (<https://docs.arc42.org/section-10/>); the rulebook's fail-closed rule |
| Abuse | How could a feature be used against its intent, and which of those must be defended? | OWASP abuse cases (1.1); STRIDE as prompts (`[4.4:stride]`) |
| Operation | How is it deployed, run, observed and retired? | arc42 "07 Deployment View"; the plan template's hidden-state and retirement sections |
| Assumptions | Which facts are assumed rather than probed? | NASA "Have all assumptions been explicitly stated?" (`[4.4:nasa-req]`) |
| Verifiability | How would each requirement be shown to hold, and by which method? | NASA "Can the criteria for verification be stated?"; ReqView "Verification method" |
| Clarification | What is unclear enough that the agent must ask rather than guess? | MAST FM-2.2 "Fail to ask for clarification" (6.80%): "Inability to request additional information when faced with unclear or incomplete data" (<https://arxiv.org/html/2503.13657>); `[4.4:ambig-swe]`; Claude Code's interview-to-spec step (1.1) |

**Checklists that exist and were read:** NASA Appendix C (writing and reviewing requirements); OWASP's abuse-case
method; arc42's twelve sections and quality-scenario form; STRIDE and the threat modeling manifesto's four
questions. **Named but not read:** INCOSE GtWR's rules, IREB's elicitation techniques, 29148's clause 5.2,
SWEBOK's elicitation section, Volere's template (see Gaps).

**Against the repository:** the plan template already covers several angles (assets and holders, environment facts
for assumptions, hidden state and retirement for operation, the threat model); the angles with no home yet are an
explicit stakeholder or source line per requirement, quality attributes written as measurable scenarios, and abuse
cases tied to each security requirement. Whether to add any of them is the user's decision.

## 3. How role-based multi-agent software-engineering systems define their agents

### Published systems

- **MetaGPT** (<https://arxiv.org/html/2308.00352>): roles come from standard operating procedures: "These SOPs play
  a critical role in supporting task decomposition and effective coordination."; "we specify the agent's profile,
  which includes their name, profile, goal, and constraints for each role."; "We define five roles in our software
  company: Product Manager, Architect, Project Manager, Engineer, and QA Engineer"; "agents in MetaGPT communicate
  through documents and diagrams (structured outputs) rather than dialogue."; "The structured PRD is then passed to
  the Architect, who translates the requirements into system design components". Ablation (section 4.4): "the
  addition of roles different from just the Engineer consistently improves both revisions and executability."
  Table 3 as the tool paraphrased it: Engineer only, executability 1.0 and 10 human revisions; all four roles, 4.0
  and 2.5, at $1.385 against $0.915. Against ChatDev (Table 1, paraphrased): executability 3.75 against 2.25.
- **ChatDev** (<https://arxiv.org/abs/2307.07924>): agents "are guided in what to communicate (via chat chain) and how
  to communicate (via communicative dehallucination)" through "the design, coding, and testing phases"; "communicating
  in programming language proves helpful in debugging".
- **AgentCoder** (<https://arxiv.org/abs/2312.13010>): a test designer separate from the programmer (1.5).

### Evidence on role definitions versus a single general agent

- **Personas alone do not help** (Zheng et al., EMNLP Findings 2024, <https://arxiv.org/abs/2311.10054>): "adding
  personas in system prompts does not improve model performance"; "the effect of each persona can be largely
  random". (Measured on factual questions, not software engineering.)
- **A strong single prompt matches multi-agent discussion** (<https://arxiv.org/abs/2402.18272>): "a single-agent LLM
  with strong prompts can achieve almost the same performance as the best existing discussion approach";
  discussion helped "only when there is no demonstration in the prompt."
- **A simple pipeline can beat complex agents** (Agentless, <https://arxiv.org/abs/2407.01489>): "Do we really have to
  employ complex autonomous software agents?"; its "simplistic three-phase process of localization, repair, and
  patch validation" reached "the highest performance (32.00%, 96 correct fixes)" on SWE-bench Lite.
- **Where multi-agent systems fail** (MAST, <https://arxiv.org/abs/2503.13657> and its HTML): failures "clustered into
  3 categories: (i) system design issues, (ii) inter-agent misalignment, and (iii) task verification."; "Disobey task
  specification" (11.8%), "Step repetition" (15.7%), "Unaware of termination conditions" (12.4%) and "Disobey role
  specification" (1.5%, "Failure to adhere to the defined responsibilities and constraints of an assigned role").
  Better role specifications gave "+9.4% success rate increase for ChatDev" (the paper also attributes +9.4% to a
  workflow change, so the attribution is inconsistent), and "not all failure modes are resolved, and task completion
  rates still remain low."

### Anthropic's guidance

- **Start simple** (<https://www.anthropic.com/engineering/building-effective-agents>): "we recommend finding the
  simplest solution possible, and only increasing complexity when needed."; "Workflows are systems where LLMs and
  tools are orchestrated through predefined code paths."; prompt chaining, where "each LLM call processes the output
  of the previous one."; the evaluator-optimizer fits when "we have clear evaluation criteria, and when iterative
  refinement provides measurable value."; principles: "Maintain simplicity in your agent's design." and "Prioritize
  transparency by explicitly showing the agent's planning steps."
- **What a delegated agent must be told** (<https://www.anthropic.com/engineering/multi-agent-research-system>):
  "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task
  boundaries."; "Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary
  information."; "multi-agent systems use about 15× more tokens than chats."; "most coding tasks involve fewer truly
  parallelizable tasks than research"; evaluation by "an LLM judge that evaluated each output against criteria in a
  rubric", starting "with small-scale testing right away with a few examples".
- **How a Claude Code subagent is defined** (<https://code.claude.com/docs/en/sub-agents>): "The frontmatter defines
  the subagent's metadata and configuration. The body becomes the system prompt"; "Only `name` and `description` are
  required."; tools default: "Inherits every tool available to subagents if omitted."; "Each subagent starts with a
  fresh, isolated context window."; "Check them into version control so your team can use and improve them
  collaboratively."
- **What a subagent does and does not buy** (<https://code.claude.com/docs/en/best-practices>): "Handing the same task
  to a subagent doesn't make the answer any better. A fresh reviewer does help, because it hasn't seen your
  reasoning"; by default "it's the same model (or a smaller one) on the same task. You get parallelism or a fresh
  pair of eyes out of it, but not a smarter answer."

### What this means for defining the agents

Across these sources, a role works through what it is given, not what it is called. The parts with evidence are:
(a) a procedure and a quality checklist for its artifact, taken from the role's body of knowledge (MetaGPT's SOPs;
Anthropic's "objective, an output format ... clear task boundaries"); (b) a structured artifact handed to the next
role instead of a conversation (MetaGPT); (c) a check to run and a bounded retry (MetaGPT's executable feedback;
Claude Code's "a check to run"); (d) a fresh context wherever judgment of someone else's work is needed (Claude Code
best practices; AgentCoder's separate test designer); (e) tool limits enforced by the harness, not asked for in a
prompt. A persona line such as "you are a senior architect" has no support on its own (the persona study), and
adding agents has a cost (about 15× tokens) that a single well-specified agent with a strong prompt may not need to
pay (2402.18272, Agentless). The reliability question the user asked, "how reliably different sub agents can be
spinned", is answered in the literature by measurement against a rubric on a few examples (Anthropic) and by the
verification failures MAST counts, not by role names.

## 4. What fits the PoC under its threat model, and what is production weight

The threat model is honest agent mistakes: an ambiguous requirement, a missed abuse case, a decision without its
reason, a test written to the code, a reviewer swayed by the author's reasoning. A practice fits when it catches one
of those cheaply; it is production weight when it serves many human stakeholders, regulatory evidence, or
organisational control that a one-user PoC does not have.

| Role | Take (catches an honest mistake) | Leave out (production weight), and why |
| --- | --- | --- |
| Requirements engineer | The INCOSE/29148 individual and set characteristics as the authoring checklist; a verification method and a source for each requirement; quality and security needs as measurable scenarios; abuse cases for each security requirement; ask rather than guess (MAST FM-2.2) | 29148's separate stakeholder, system and software specification documents, requirement-management tooling and change boards: one stakeholder (the user) and one trace model already exist |
| Requirements reviewer | Inspection's split (reviewer finds, author fixes) and exit criteria; the characteristics as defect classes | The inspection meeting with moderator, reader and recorder roles, and inspection-rate metrics: one reviewer per round already, and the review loop is the exit rule |
| Architect | ADR form (context, decision, consequences, superseded) for each significant decision; quality scenarios the design answers; STRIDE prompts per trust boundary touched with a response for each; C4 context and container views | Full 42010 conformance (viewpoint library, correspondence rules) and all twelve arc42 sections for every change: they serve many stakeholder groups and long-lived systems; a PoC change touches few concerns |
| Architecture reviewer | ATAM's core question (does each decision meet its quality scenario, where are the risks) and the manifesto's "Did we do a good enough job?" | ATAM's multi-day phases, stakeholder utility-tree voting and evaluation team: they need many stakeholders |
| Test engineer | A test list from requirements and abuse cases before code; the test designer is not the implementer; each test fails first for its reason | 29119-3's full document set (test plan, design and case specifications, completion report) and ISTQB test-management process: `test_plan.md`, `trace/tests.yaml` and `docs/test_spec.md` already hold that content |
| Implementer | One self-contained change with its tests; a check to run before "done"; bounded retries on failing checks | Full CERT/ASVS verification levels and supply-chain controls: outside the accepted simplifications |
| Code reviewer | A fresh context that never saw the author's reasoning; read-only tools enforced by the harness; findings that affect correctness, with severity | Several reviewers per change and reviewer-rotation policies: none of the sources read shows they catch more honest mistakes, and each reviewer costs tokens |
| Final reviewer | The whole change against the recorded intent; the verification step MAST shows is the commonest gap | IEEE 1028 audits and formal configuration audits: they verify an organisation's compliance, not a change |

## Role → standard → what good output looks like → PoC fit

| Role | Standard or body of knowledge (read?) | What good output looks like | PoC fit |
| --- | --- | --- | --- |
| Requirements engineer | ISO/IEC/IEEE 29148 (not read); INCOSE GtWR v4 (names only); NASA SE Handbook App. C (read); arc42 §10 (read); OWASP abuse cases (read); IREB CPRE, SWEBOK v4 (not read) | Necessary, singular, unambiguous, verifiable requirements with source, rationale and verification method; quality needs as measurable scenarios; abuse cases as security requirements; assumptions explicit; set complete and consistent | Take the characteristics, scenarios and abuse cases as the author's checklist; leave the 29148 document set and tooling |
| Requirements reviewer | IEEE 1028 (not read); Fagan inspection (public summary); NASA App. C | Defects tied to the violated characteristic and the requirement; no rewriting; verdict against exit criteria | Take; leave the meeting roles and metrics |
| Software architect | ISO/IEC/IEEE 42010 (summary only); arc42; C4; ADR (Nygard); threat modeling manifesto, OWASP, STRIDE | Context and scope, building blocks and interfaces, runtime views of security flows, decisions with forces and consequences, quality scenarios answered, threats per trust boundary each with a response | Take ADR form, scenarios, STRIDE per boundary, C4 context and containers; leave full 42010 and arc42 |
| Architecture reviewer | SEI ATAM (abstract only); threat modeling manifesto; OWASP | Each quality scenario walked through the design, risks named, model checked against the built system, missing threats | Take the core question; leave the ATAM workshop |
| Test engineer | ISO/IEC/IEEE 29119 (part titles only); ISTQB (not read); TDD (Fowler); AgentCoder; OWASP abuse cases | A test list before code from requirements and abuse cases; tests that fail first for their reason; oracles from the requirement | Take, with the test designer independent of the implementer; leave the 29119-3 document set |
| Implementer | Google eng-practices (small CLs); MetaGPT executable feedback; Claude Code best practices | Small self-contained change with its tests; gates pass before "done" | Take; leave full CERT/ASVS levels |
| Code reviewer | Google eng-practices (`[4.4]`); Claude Code best practices | Correctness findings with severity and evidence against the spec, from a fresh, read-only context | Take; leave multi-reviewer policies |
| Final reviewer | IEEE 1028 (not read); MAST (verification failures); Claude Code best practices | The whole change against the recorded intent: requirements realised and tested, plan departures, documents made false | Take; leave audits |

## Gaps: what this research did not find or could not verify

- **Standards not read:** ISO/IEC/IEEE 29148 (paid; the sample PDF could not be decoded; no PDF text tool was
  available), ISO/IEC/IEEE 42010 (paid; its public site refused the connection), ISO/IEC/IEEE 29119 (only part
  titles), IEEE 1028 (paid), ISTQB CTFL v4 (not attempted again after `[4.4:istqb]`), IREB CPRE (account wall; the
  mirror failed TLS), SWEBOK v4 (PDF unreadable; one search summary only), SEI ATAM (abstract only). The roles'
  duties from these standards rest on public summaries and the read sources above.
- **INCOSE:** only the characteristic names, from secondary sources via a search; no definition or rule (R1 onward)
  was read from INCOSE.
- **ISO/IEC 25010:** only four of the nine characteristic names were readable; the edition was not stated.
- **Not looked at within the call budget:** Volere's requirements template, the SEI Quality Attribute Workshop,
  viewpoint-oriented requirements methods, the SEI quality-attribute scenario report itself, and OWASP's own
  threat-modeling process beyond `[4.4:owasp-threat]`.
- **Evidence gaps:** no study was found that compares software-engineering agents defined from a body of knowledge
  with persona-only agents; the persona study measures factual questions. MetaGPT's ablation adds documents and
  steps together with roles, so it does not isolate the role definition; its table numbers are the tool's
  paraphrase. MAST attributes its +9.4% to two different interventions. No benchmark of LLM requirements elicitation
  or architecture quality was read, so how reliably a requirements or architect agent performs remains unmeasured
  here; the repository's own benchmark measures reviewers only.
- **Truncation:** the Claude Code subagents page and the MetaGPT and MAST HTML pages were read only to their first
  100,000 characters; MAST's appendix with the prompt case studies was not read.
- **Quotes:** returned by a web-fetch tool that runs a model over the page; they were not checked character by
  character against the original pages.
