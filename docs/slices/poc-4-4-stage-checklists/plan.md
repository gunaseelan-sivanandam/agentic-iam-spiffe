# Slice Plan — poc-4-4-stage-checklists: stage checklists from industry review practice

Plan of slice 4.4 of the agentic-SDLC PoC (issue #41, part of slice 4, #33): a short review
checklist and the blocking criteria for each stage of the delivery cycle. They are drawn from
established review practice, tested against this repository's past misses, and given to every review
as its minimum.

Status: draft, 2026-11-08. Approved when the owner merges slice 4's single plan PR.

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
  - a change that rewrites the checklist it is reviewed against.
- **System under test:** unchanged.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| S44-D1 | **Research first, per artifact type:** plan and test plan, requirements, architecture and interfaces, unit tests, E2E tests, code, final review, handoff. Candidate sources: ISO/IEC/IEEE 29148 (requirements), INCOSE's Guide for Writing Requirements, SEI's ATAM and threat modelling (STRIDE, OWASP) for architecture, ISTQB and research on test smells for tests, Google's code review guide, OWASP's code review guide and ASVS and SEI CERT for code, IEEE 1028 for reviews in general, and OWASP's Top 10 for LLM applications, because the reviewers are AI agents. The research uses public summaries and the standards' published outlines. Paid standards are cited by clause title, not copied. | owner, [#33 decision 4](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672); #33's description (artifact types) |
| S44-D2 | **Research record:** `research.md` in this bundle lists, for each artifact type, every candidate item, its source (title, clause or section, URL), and its outcome: a question in the list, merged into another, or "not applicable to this PoC" with a reason. | default (the owner can see why each item is in or out) |
| S44-D3 | **Short, specific lists.** At most 12 questions per artifact type, each answerable from the copy and the evidence. A long generic list did no better than three questions in stage A. | benchmark report, stage A; default (the limit) |
| S44-D4 | **Blocking criteria per stage.** Each list ends with "Blocks at this stage", for example: a requirement no test could verify, a requirement that contradicts another or the threat model, a design that lets an asset reach a non-holder, a test that can pass while the behaviour is broken, a secret in a published record, a security defect in the system under test. `AGENTS.md`'s "Review findings" says the stage list defines what blocks, and keeps today's three criteria for every stage. | owner, [#33 decision 2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) |
| S44-D5 | **The two questions for what is missing** are in the lists: "Does every new or changed requirement have a test or check that proves it?" (requirements, tests, final review) and "Does every new check run as its own required CI job, named after it?" (code, final review). | owner, same |
| S44-D6 | **Where the lists live:** `docs/review_checklists/<artifact type>.md`, one short file each, each starting with a purpose paragraph. `AGENTS.md` points to them and states how they are used. They are not inside `AGENTS.md`, because each review gets only its own stage's list. | #33's description (home question); default (small files) |
| S44-D7 | **The checklist comes from the base branch,** like the approved rules. The launcher reads it with `--stage <artifact type>` from the base commit, so a change cannot rewrite the list it is reviewed against. | default (same reason as POC-D3 for the rules) |
| S44-D8 | **A short coding guideline** holds only what tools cannot check: error handling, logging, structure, maintainability, whether a name says what it does. It is the code list itself, read by authors before writing and by reviewers as the minimum. What `make lint` and the coding rules already enforce stays out. | #33's description |
| S44-D9 | **The DPL entries test the lists.** For DPL-001 to DPL-010, `research.md` records which list question would have caught each miss at the stage where it happened. A miss with no such question gets one, or a recorded reason why not. The DPL entries test the lists; they are not their source. | owner, [#33 decision 4](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) |
| S44-D10 | **Several models critique the draft lists** from different angles: Opus, Sonnet and Codex each review the drafts and `research.md` through the launcher, with the open mandate. The Codex critique waits for 4.5's Codex mode and its confinement probe, so the order of work is: 4.5's Codex mode first, then this critique. | owner, [#33 decision 4](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672) and 2026-11-08 (Codex); default (the order) |
| S44-D11 | **Learning loop** (`AGENTS.md`): when an open review finds a class of defect a stage list lacks, the author proposes an item in the PR, and the owner approves it (POC-D6). | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242) |

## Requirements

None added (POC-D9).

## Success criteria

- `docs/review_checklists/` holds a list for each of the eight artifact types. Each list has at most
  12 questions and a "Blocks at this stage" section, and every question cites its source in
  `research.md`.
- `research.md` maps every DPL entry to the question that would have caught it, or records why none
  would.
- A review started with `--stage <type>` gets that list, read from the base commit, as its minimum
  section.
- Opus, Sonnet and Codex have each critiqued the drafts. Their findings are answered in this
  bundle's review record.

## In scope

`docs/review_checklists/` (new), `docs/slices/poc-4-4-stage-checklists/research.md` (new),
`scripts/run_independent_review.py` (`--stage`), the tooling tests, `AGENTS.md` (Review findings,
Independent review, the learning loop, the pointer to the lists).

## Out of scope

- Measuring the lists (4.5, #42).
- The slice workflow's stages (4.6, #43), which use these lists.
- Changing the gates that already enforce code rules.

## Assets and holders

None touched. The research reads public sources. No key or secret is involved.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Web research tools | the session's web search and fetch tools | Available to the author. The reviewer has no web access (Read, Grep and Glob only), so `research.md` must carry what the reviewer needs to check |
| Codex reviewer | 4.5's probe (#42) | Pending; S44-D10's Codex critique runs after it |

## Hidden-state and trust decisions

None. The lists are tracked files, read from the base commit.

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests (`--stage` picks the base commit's list; every list has its parts and sources);
  the critiques and the DPL mapping, reviewed.
- Rulebook: `AGENTS.md` (Review findings per stage, the learning loop, the pointer to the lists).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Stage list as each review's minimum | Questions nobody asked (DPL-004, DPL-005) | One short file per stage; a few hundred words per prompt | The open mandate alone: the benchmark shows unasked questions get missed |
| A tooling test for the lists' form | A list that grows past 12 questions, or a question without a source | One test | Review by eye |

## Retirement and compatibility

- The benchmark's two stage-A prompts stay as they are, for comparison; 4.5 measures the new lists
  against them.
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm: S44-D2 (research record), S44-D3 (at most 12
questions), S44-D6 (small files), S44-D7 (from the base branch), the order in S44-D10.
