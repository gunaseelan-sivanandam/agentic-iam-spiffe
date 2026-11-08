# Slice Plan — poc-4-4-stage-checklists: stage checklists from industry review practice

Plan of slice 4.4 of the agentic-SDLC PoC (issue #41, part of slice 4, #33): research established
review practice for each artifact type, write a short checklist with blocking criteria for each, check
the lists against the delivery problem log, and give each review its stage's list as the minimum.

Status: draft, 2026-11-08, revised after plan review rounds 1 and 2. Approved when the owner merges slice
4's single plan PR.

**Order of work:** after 4.1 (the checklist section, the severity rules), 4.2 and 4.3, and after 4.5's
first part (the Codex mode and its probe), which the critique may use; before 4.5's runs, which
measure the lists, and 4.6, which names them per stage. The whole order is in the
[slice index](../README.md).

## Goal

The benchmark showed that the reviewer finds code defects well, but misses defects of absence and
placement that no question asked about. The owner rejected building checklists only from our own
past misses: "we are basically reinventing the wheel by facing issues and updating the checklist".
They also found that the blocking criteria are written for code only: "what about, architecture or
requirements or tests?" This slice researches established review practice for each artifact type
and turns it into short, specific questions and blocking criteria. It then checks the lists against
the DPL entries and gives them to the launcher as each stage's minimum. The open mandate (4.1) stays
on top: "checklist alone is not completely reliable" (owner).

## Threat model

- **Delivery** (honest mistakes):
  - a checklist so generic that it adds nothing (stage A's eight-question checklist);
  - a list that misses a known class of defect;
  - blocking criteria that let a requirement or a test defect through;
  - a change that rewrites the checklist it is reviewed against;
  - a review that runs without its list and nothing shows it;
  - a research record that cites a source wrongly, which no reviewer can open.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S44-D1 | **Research first, per artifact type:** plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code. The final review gets no list (owner: "no question list"; 4.1, S41-D4), and the handoff review is the owner's approval (the PoC plan's Goal table), so neither gets one. Candidate sources: ISO/IEC/IEEE 29148 (requirements), INCOSE's Guide for Writing Requirements, SEI's ATAM and threat modelling (STRIDE, OWASP) for architecture, ISTQB and research on test smells for tests, Google's code review guide, OWASP's code review guide and ASVS and SEI CERT for code, IEEE 1028 for reviews in general, and OWASP's Top 10 for LLM applications, because the reviewers are AI agents. A public source is cited with its URL, its section and a short quote. A paid standard is cited only by a clause title from its public table of contents, marked "title only", and never copied. | owner, [#33 decision 4](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672); [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147), item 5; plan review round 1, B1, A2 |
| S44-D2 | **Research record:** `research.md` in this bundle has a section for each source named in S44-D1. It lists, for each artifact type, every candidate item, its source key and citation, and its outcome: a question in the list, merged into another, or "not applicable to this PoC" with a reason. | default (the owner can see why each item is in or out) |
| S44-D3 | **Short, specific lists.** At most 12 questions per artifact type, each answerable from the copy and the evidence, and each specific to its type: a question that would apply to every type belongs to the mandate, not a list. Stage A's eight-question list failed because it was generic, not because of its length; 4.5 measures whether the new lists add anything. | benchmark report, stage A; default (the limit and the specificity rule) |
| S44-D4 | **Blocking criteria per stage.** A finding blocks when it meets `AGENTS.md`'s criteria for every stage (today's three, plus 4.1's secret rule) or the "Blocks at this stage" section of its stage's list. That section names the stage's own cases, for example: a requirement no test could verify, a requirement that contradicts another or the threat model, a design that lets an asset reach a non-holder, a test that can pass while the behaviour is broken, a security defect in the system under test. `AGENTS.md`'s "Review findings" says so. | owner, [#33 decision 2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) ("what about, architecture or requirements or tests?") |
| S44-D5 | **The two questions for what is missing** are in the lists where the misses happen. "Does every new or changed requirement have a test or check that proves it?" is in the plan-and-test-plan, requirements, unit-test and E2E-test lists; DPL-004 happened at the plan stage. "Does every new check run as its own required CI job, named after it?" is in the plan-and-test-plan and code lists, because plans declare new checks. | owner, [#33 decision 2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672); plan review round 1, A5 |
| S44-D6 | **Where the lists live:** `docs/review_checklists/<artifact type>.md`, one short file each, each starting with a purpose paragraph. `AGENTS.md` points to them and says how they are used. They are not inside `AGENTS.md`, because each review gets only its own stage's list. | #33's description (home question); default (small files) |
| S44-D7 | **`--stage` reads the list from the base commit,** like the approved rules, so a change cannot rewrite the list it is reviewed against. It may be given more than once: the tests-first stage takes the unit-test and E2E-test lists. A name must match a list file at the base commit, or the review is refused before any call. When the base has `docs/review_checklists/`, an initial review or recheck without `--stage` is refused. The final review takes none (4.1). When the base has no such directory, as for every review of slice 4 itself, the review runs without a list, and the prompt and the start entry say "no checklist at base <commit>". The start entry records each stage and its list's SHA-256. | default (the same reason as POC-D3 for the rules); plan review round 1, A1 |
| S44-D8 | **A short coding guideline** holds only what tools cannot check: error handling, logging, structure, maintainability, whether a name says what it does. It is the code list itself, read by authors before writing and by reviewers as the minimum. What `make lint` and the coding rules already enforce stays out. | #33's description |
| S44-D9 | **The DPL entries test the lists.** For DPL-001 to DPL-011, `research.md` records which question would have caught each miss at the stage where it happened. If no question would, the author adds one only if an industry source supports it, tagged with that source; otherwise `research.md` records why not. The DPL entries test the lists; they are never a question's source. A question's source tag is `[S:<key>]`, where the key names a source section of `research.md`. | owner, [#33 decision 4](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) ("they are not the lists' source"); plan review round 1, A8 |
| S44-D10 | **Several models critique the draft lists** from different angles, with the open mandate, as their own review unit `critique` in this bundle: one round with Opus and Sonnet, plus Codex if 4.5's probe confined it. If it did not, the record says why Codex is missing, and the critique runs with two models. At most three runs, outside 4.5's 40. Every finding gets an answer under 4.1's severity rules; the fixes to blocking findings are rechecked in 4.4's implementation-review unit. The rulebook's Codex exception covers this critique (`AGENTS.md`, Models and usage limits, changed by this plan PR). | owner, [#33 decision 4](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) ("different models input might be good"); default (Codex here, the unit and the bound) |
| S44-D11 | **Learning loop** (`AGENTS.md`): when an open review finds a class of defect a stage list lacks, the author proposes an item in the PR, and the owner approves it (POC-D6). | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242), item 5 |
| S44-D12 | **Lists for the benchmark.** 4.5's cases take the lists from the runner's own tree at a fixed commit, recorded in each result's identity, not from the case's base, which predates the lists. The answer key names each case's artifact type. | plan review round 1, B3 (cross-plan with 4.5) |

## Requirements

None added (POC-D9).

## Success criteria

- `docs/review_checklists/` holds a list for each of the six artifact types. Each list has at most 12
  specific questions and a "Blocks at this stage" section, and every question cites a source key of
  `research.md`.
- `research.md` has a section for every source of S44-D1, and maps every DPL entry to the question
  that would have caught it, or records why none would.
- A review started with `--stage <type>` gets that list, read from the base commit, as its minimum
  section; a review whose base has no lists says so.
- Two or three models have critiqued the drafts, and their findings are answered in the critique's
  record.

## In scope

`docs/review_checklists/` (new), `docs/slices/poc-4-4-stage-checklists/research.md` (new),
`scripts/run_independent_review.py` (`--stage`), `scripts/run_review_benchmark.py` (lists from a
fixed commit), the tooling tests, `AGENTS.md` (Review findings, Independent review, the learning loop,
the pointer to the lists).

## Out of scope

- Measuring the lists (4.5, #42).
- The slice workflow's stages (4.6, #43), which use these lists.
- Changing the gates that already enforce code rules.

## Assets and holders

None touched. The research reads public sources. No key or secret is involved.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Web research tools | the session's web search and fetch tools (2026-11-08) | Available to the author. The reviewer has no web access (Read, Grep and Glob only), so `research.md` must carry the quotes the reviewer needs to check |
| Lists at the base | `git ls-tree poc/agentic-sdlc docs/review_checklists` (2026-11-08) | Absent; it appears when slice 4's final PR merges |
| Codex reviewer | 4.5's probe (#42) | Pending; S44-D10's Codex critique runs only after it passes |

## Hidden-state and trust decisions

None. The lists are tracked files, read from the base commit (the benchmark: from a fixed commit).

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests (the form of the lists, the sources in `research.md`, `--stage`); the rule
  texts, the code list's content, the critiques and the DPL mapping by review.
- Rulebook: `AGENTS.md` (Review findings per stage, the learning loop, the pointer to the lists; the
  Codex exception, already in this plan PR).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Stage list as each review's minimum | Questions nobody asked (DPL-004, DPL-005) | One short file per stage; a few hundred words per prompt | The open mandate alone: the benchmark shows unasked questions get missed |
| A tooling test for the lists' form and sources | A list that grows past 12 questions, a question without a source, a source never researched | One test | Review by eye |
| The critique unit | Lists shaped by one model's blind spots | At most three runs | One critique by Opus: the owner asked for different angles |

## Retirement and compatibility

- The benchmark's two stage-A prompts stay as they are, for comparison; 4.5 measures the new lists
  against them.
- The draft's final-review and handoff lists are dropped (S44-D1).
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm: S44-D2 (research record), S44-D3 (at most 12
specific questions), S44-D6 (small files), S44-D7 (from the base branch; no list during slice 4),
Codex in S44-D10, S44-D12.
