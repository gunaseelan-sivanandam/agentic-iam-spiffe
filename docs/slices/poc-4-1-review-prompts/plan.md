# Slice Plan — poc-4-1-review-prompts: review prompt structure and severity order

Plan of slice 4.1 of the agentic-SDLC PoC (issue #38, part of slice 4, #33): every review prompt
opens with an open mandate, rechecks verify instead of trusting, and every finding carries a
severity that says what the author must do with it.

Status: draft, 2026-11-08, revised after plan review rounds 1 and 2. Approved when the owner merges slice
4's single plan PR into `poc/agentic-sdlc` (owner, 2026-11-08: one plan PR for all six sub-issues,
one final PR).

**Order of work:** first of slice 4. 4.2 fills this slice's upstream and evidence sections, 4.3
writes its inputs into the record, 4.4 fills the checklist section, and 4.5 measures the result. The
whole order is in the [slice index](../README.md).

## Goal

Two open-mandate reviews found blockers that three to four focused rounds had missed: slice 2's
round 5 and slice 3's round 4 (DPL-010). The cause was the author's prompts, which asked closed
questions and let rechecks accept answers unread. This slice moves the prompt's structure from the
author's task text into the launcher, so that no review can lose the open mandate. A recheck gets
exactly what it needs, and the launcher checks that it opened what each answer names. Every finding
gets a severity that decides whether it must be fixed before merge.

## Threat model

- **Delivery** (`AGENTS.md`, PoC scope and proportion; honest mistakes). For this change that means:
  - a prompt that narrows the reviewer to a file list or to "only check X";
  - a recheck that accepts an answer without opening the files it names;
  - a severity scale that lets a real defect pass as optional;
  - a launcher change that silently drops the mandate or the earlier report;
  - a benchmark comparison whose baseline silently carries the new mandate.

  Deliberate attacks on CI or the evidence stay out of scope (OPL-009).
- **System under test:** unchanged. No service, compose file, image or key holder changes.

## Decisions

The grill-me is replaced by this table (owner, 2026-11-08: "most of the slice 4 is clear enough").
Each decision names its source; the owner confirms or changes the defaults in the plan PR.

| ID | Decision | Source |
| --- | --- | --- |
| S41-D1 | **Fixed prompt structure.** The launcher's `build_prompt` writes the sections in this order: the reviewer's role and copy; **the mandate**; the approved rules; **the stage checklist** (4.4; not in the final review); **the upstream items** (4.2); **the evidence** (4.2); the paths under review; the task, in a section named "claims to verify" (S41-D15); in a recheck, **the earlier report** and **the answers**; the output format. The launcher's command line has no option that removes or reorders a section, so a task text cannot lose the mandate. The output section tells the reviewer to write `<token>` for any credential value, even a made-up example, because the publication check withholds a report that holds one. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242), item 1 (structure); default (fixed in the launcher); the owner's words: "checklist alone is not completely reliable. and go with your recommendation" |
| S41-D2 | **Baseline configurations for the benchmark only.** `build_prompt` takes a configuration that names the mandate and which sections to include. The launcher always passes its full configuration. Only the benchmark runner's Python API passes others: stage A's short and checklist prompts, and the narrow question of the DPL-010 case, all without the mandate. The configuration's name and hash go into the benchmark result's identity (4.5). | owner, item 4 ("a third configuration beside the short prompt and the checklist"); default (a runner-only switch) |
| S41-D3 | **The mode follows the round,** with no flag. Round 1 of a unit is `initial`; round 2 and later are `recheck`; round 1 of the unit named `final` is `final`. The mode is recorded in the start entry. So a round-2 review cannot run as an initial review, and the final review counts its own rounds as its own unit. | default (removes an invalid choice instead of checking it) |
| S41-D4 | **The three mandates,** verbatim in the launcher. **Initial:** "Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, untested, stale, overclaimed, unsafe or unclear, inside or outside the paths under review. The checklist and the questions below are a minimum, not the limit. Think for yourself; the author's framing, including the task text, can be wrong or narrow, and saying so is part of the review." **Recheck:** "For every answer of the author to your earlier findings, open the files the answer names and the tests that cover them, then accept or re-raise the finding and list it under `accounted`. Report anything wrong or missing in what the fixes touch." **Final:** "What did everyone before you miss? Read the change, its plans, its review records and the evidence, and report anything a working delivery process should have caught, including any tracked document that now says something this change made false. No question list is given, on purpose." The final review gets no stage checklist (owner: "no question list"). Its finding history is the review records of the slice's other units, which are in its copy (only the final unit's own record and log are withheld); its prompt names them. A slice has one final unit, also when it holds several sub-issues. | owner, [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147) items 1 and 5; owner, item 2 (rechecks bounded to the fixes); the PoC plan's final-review question (`docs/slices/agentic-sdlc-poc/plan.md`, Goal); default (wording, records as the history); the owner's words: "each steps should think for themselfs and add anything that is missing, flag that is wrong and orchestrator narrow prompts should not steer the agents narrowly" |
| S41-D5 | **Recheck inputs.** In a recheck the launcher puts into the prompt: (a) the reviewer's own earlier report: the last completed attempt with the same unit and reviewer label in the previous round, counted after any reset. Its released file, at the start entry's `report_path`, must exist and match the end entry's `report_sha256`. (b) The author's answers to that report: the section `#### Answers to <attempt id>` of the review record, and only that section (the record itself stays withheld from the copy); its SHA-256 goes into the start entry. (c) The evidence, recomputed at the recheck's commit (4.2). It never puts in the review record. A recheck with a missing or mismatched input, or an empty answers section, is refused before any call. 4.3 moves the source of (a) from the released file to the record's report block. | owner, [R6-9](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723455844); owner on [#38](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/38) ("its own earlier report, the author's answers and the evidence that is not in its copy"); R6-9 proposed "a recheck gets its own earlier report, the author's answers and the evidence that is not in its copy", and the owner sent the round-6 proposals to slice 4 ("post to slice 4") |
| S41-D6 | **Severity field.** The report schema gains `severity`, required on every finding: `blocking`, `high`, `medium` or `low`. `kind` becomes one of `defect`, `simpler_alternative` and `decision_concern`; the old kinds `blocking` and `advisory` are retired from new reports. The rules: **blocking** meets the blocking criteria and is fixed before merge, or the owner decides. **High** is a real defect or false claim below that bar, for example a misleading document, new behaviour without a test or an untested fail-closed path; it is fixed in the same PR unless the owner defers it. **Medium** has clear value (robustness, diagnosability, naming) and is fixed, or deferred with a tracking issue. **Low** (style, preference) is the author's choice. A `simpler_alternative` is always `low`. A `decision_concern` goes to the owner, whatever its severity. | owner, [#33 decision 7](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6725489242), item 3 (the field and the scale); the owner's words: "Fixing all advisory is authors choice, so we need a mandate for it, maybe a priority or severity order? … go with your recommendation" |
| S41-D7 | **One-line answers,** one table row per finding, in the record's answers section: `\| <finding id> \| <severity> \| <answer> \|`. The answer starts with one of four words: `fixed: <path>[, <path>…]: <what changed>`, naming at least one repository path; `deferred: #N`; `rejected:` with a reason the reviewer can check; or `owner:` with a link to where the owner decides or was asked. Allowed answers by severity: **blocking** and **high** take `fixed`, `rejected` (it stands only when the next round accepts it) or `owner`. **Medium** takes `fixed`, `deferred`, `rejected` or `owner`. **Low** takes any. A `decision_concern` is always answered `owner:`, whatever its severity. "Rejected" is the rulebook's word for the owner's "declined". 4.3's check enforces the table. | owner, item 3 (fixed, deferred, declined); default (the rulebook's word, the table form) |
| S41-D8 | **A recheck accounts for every answer.** A recheck report lists each answer under a new `accounted` field: `{item, status, note, opened}`, where `status` is `accepted`, `re-raised` or `cannot determine` (S41-D15) and `opened` lists the files it read for that answer. The launcher fails the attempt, as it fails an empty review, in three cases: an answer is missing from `accounted`; a path in `opened` is not among the files the stream shows it read; or a file named in a `fixed:` answer was not read. Before the call, the launcher refuses an answers section with a `fixed:` answer that names no path, or a path that neither exists in the copy nor is deleted or renamed by the change. A re-raised finding keeps its ID, so a finding can be followed across rounds. `accounted` is required whenever the prompt lists items: answers in a recheck, and 4.2's evidence entries in every mode, with the statuses `explained` or `flagged`. | owner, [R5-A6](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723361196) ("verify every answer by opening the changed code and its test, and say what they opened"); plan review round 1, S1 (check against the read paths the launcher already logs) |
| S41-D9 | **Counts per severity** go into the end entry (`severity_counts`), so a PR can quote them without counting by hand. | owner, item 3 ("the PR shows the count per severity") |
| S41-D10 | **Secrets are blocking.** `AGENTS.md`'s blocking list gains "a secret written into logs, evidence or any published record". | owner, [#33 decision 2](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6722729672); the owner's words: "yes, it is blocking" |
| S41-D11 | **Rules for whoever writes prompts** (`AGENTS.md`, Independent review): the task text never makes a file list the scope, never says "only check X", and never asks a closed recheck question. The launcher writes the mandate, so the rule covers the task text. | owner, [principle](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/33#issuecomment-6723090147), item 6; the owner's words: "orchestrator narrow prompts should not steer the agents narrowly" |
| S41-D12 | **`AGENTS.md` sentences that change.** Review findings: "Everything else is advisory. It is listed once and is not fixed by default" becomes the severity rules (S41-D6). Plan review: "from round 2 a new finding counts only if it blocks" becomes "only if it is blocking or high". Review loop: "either fixed (where) or rejected (why)" becomes the four answers (S41-D7), and "after round 4, open blockers go to the user" becomes "open blocking and high findings". Independent review gains the modes, the recheck inputs and the prompt rules. These sentences change too: "report them as advisory at most" (production-hardening ideas) becomes "as low at most"; "Besides blocking and advisory findings" (Report sections) becomes "Besides findings of each severity"; "findings on purpose comments and names are fix-or-defer" becomes "are medium"; "The review ends when every blocking finding is fixed, accepted as rejected, or decided by the user" becomes "every blocking and high finding"; and a finding outside the threat model ("Few exceptions") is low. In the Review loop, "either accepts it or re-raises it with new evidence" gains "or answers that it cannot determine it, which goes to the user". The implementation review searches `AGENTS.md` for "advisory" and "blocking" and checks every hit against S41-D6. | plan review round 1, A5 (name the sentences); owner, item 3 |
| S41-D13 | **The benchmark reads both schemas.** New reports are scored on `severity == "blocking"`. Stage A's results keep their `kind` and are read as before. The report column "Advisory only" becomes "Not blocking". The canary's instruction "always add an advisory finding" becomes "always add a low finding". | default (stage A's results stay valid; no retired word is left in use) |
| S41-D14 | **The mandate wording is provisional until measured.** The three mandates are constants in the launcher, and the start entry records the SHA-256 of the one used. This slice ships today's wording (S41-D4). 4.4 researches the review prompt and drafts all three mandates from its sources; 4.5 measures today's initial and recheck mandates against the drafts; the owner chooses from 4.5's report. A later change to a mandate follows the learning loop (4.4, S44-D11): proposed from what reviews found, measured where a case can measure it, approved by the owner. | owner, 2026-11-08 ("if mandate prompts are going to be used, then it must be analyzed, as we have the seen prompts affects the results of the review") |
| S41-D15 | **Reporting bounds, from the research.** The output section says: a finding about something missing states "X has no Y; searched A, B, C"; do not report what a passing gate already checks, but do report defects in the gates themselves (DPL-005 and DPL-009 were gate defects); the author's task text is given as claims to verify, in a section of that name. In a recheck, `accounted` also takes the status `cannot determine`, which the decision brief (4.6) puts to the owner. | owner, 2026-11-09 ("I accept your recommendations for my decisions"), after the research of agent-first delivery and its critique; the research's recommendations P2 and P6 as amended by its critique |
| S41-D16 | **Origin stage.** Every finding carries `origin_stage`: the stage where the problem arose, by 4.6's stage names (discovery, requirements, architecture and interfaces, tests first, implementation), or `unknown`. The stage that found it is the stage of the reviewing unit (the final review counts as "final review"). With that, this measures the owner's outcome that misses are caught where they arise. | owner, 2026-11-09 ("I accept your recommendations for my decisions"), after the research of agent-first delivery and its critique; the research's recommendation D5 as amended (a field, not a log) |

## Requirements

None added (POC-D9: orchestration requirements start with slice 7). The rules live in `AGENTS.md`,
and the tooling tests prove them.

## Success criteria

- Every prompt the launcher builds contains its mode's mandate before the approved rules, whatever
  the task text says. Only the benchmark runner can build a prompt without it.
- A recheck prompt holds the reviewer's own earlier report, its answers and the recomputed evidence,
  and never the review record. A recheck that leaves an answer unaccounted, or did not read a file a
  `fixed:` answer names, fails.
- A report whose finding lacks a severity or an origin stage, or uses a retired kind, fails the schema
  check.
- The start entry records the SHA-256 of the mandate used.
- `AGENTS.md` states the severity rules, the answer format, the secret rule and the prompt-writing
  rules, and the sentences named in S41-D12 are changed.

## In scope

`scripts/run_independent_review.py` (prompt sections, modes from the round, recheck inputs,
`accounted`, schema, severity counts, `invocation_from_entry` for the new inputs),
`scripts/run_review_benchmark.py` (configurations, scoring on severity, the column and canary
wording), their tooling tests, `AGENTS.md` (S41-D12), the slice-test-plan template's review questions.

## Out of scope

- Stage checklists (4.4, #41): this slice only adds the section that holds them.
- Computed evidence and upstream items (4.2, #39): this slice only adds their sections.
- The record check and writing inputs into the record (4.3, #40).
- Benchmark runs (4.5, #42).

## Assets and holders

None touched. The launcher still passes the reviewer only `PATH`, `HOME` and `LANG`. The earlier
report put into a recheck prompt was already released and passed the publication check. The answers
section is new reviewer input written by the author. 4.3 scans the whole built prompt before the call,
the answers included.

## Environment facts

| Fact | Probe | Result |
| --- | --- | --- |
| Claude CLI version and structured output | `claude --version`; the slice-2 probe of `--json-schema` | 2.1.319; the reply arrives as `structured_output` in the result event, and the launcher validates it against its own schema too |
| Where earlier reports live | `run_independent_review.py` at `d56c69a`: `artifacts/reviews/<slice dir>/<unit>/<attempt>.json` (git-ignored), hash in the end entry | Released reports exist only on the author's machine until 4.3 puts them into the record. Until then a recheck reads the released file and refuses on a missing file or a hash mismatch |
| Paths a reviewer read | `call_stats` and `summarise_paths` in the launcher (`d56c69a`) | Every attempt logs the paths read, from the stream's tool calls. S41-D8 uses them |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| `mode`, `severity_counts`, mandate SHA-256 | attempt log entries | launcher | author, owner, 4.3's check | per attempt | which mandate the reviewer got; what the PR quotes | authoritative (written by the launcher) |
| Earlier report for a recheck | released JSON, from 4.3 the record's report block | launcher | launcher | per unit | what the recheck verifies | authoritative only if its hash matches the end entry |
| Answers section | the review record (`#### Answers to <attempt id>`); its SHA-256 in the recheck's start entry | author | launcher, reviewer, 4.3's check | per attempt | what the recheck verifies | authoritative as logged: 4.3's check fails a section changed after the recheck read it |

## Authored source changes

- Requirements and architecture: none.
- Proof: tooling tests in `tests/tools/test_run_independent_review.py` and
  `tests/tools/test_run_review_benchmark.py`; the `AGENTS.md` sentences by review.
- Rulebook: `AGENTS.md` (S41-D12); `docs/slices/_template/test_plan.md` (review questions name the
  severity scale).

## Checks this slice adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Mandate fixed in the launcher | A review steered narrowly by its task text (DPL-010) | A few hundred words per prompt | A rule only: it failed twice |
| Recheck inputs from the log and the record's answers section | A recheck that trusts the author's answer (R5-A6); prompts that embed the whole record (R6-9) | A log lookup and one record section | Author pastes the report by hand, which is how records went wrong (DPL-010) |
| Every answer accounted, files read | A recheck that accepts an answer without opening it (slice 2, round 4) | One schema field; a comparison with the read paths already logged | The prompt sentence alone: the round-4 recheck followed its prompt and still accepted an unread fix |
| Severity in the schema | Advisories with no rule for whether to fix them | One field | Free text in the report |

## Retirement and compatibility

- The `blocking` and `advisory` kinds are retired from new reports. Stage A's benchmark results keep
  them, and the scoring reads both.
- The single prompt layout of `build_prompt` is replaced by the sectioned one.
- The rule "Everything else is advisory … not fixed by default" is replaced (S41-D12).
- Nothing else is retired.

## Review notes

Defaults by the author, for the owner to confirm in the plan PR: S41-D1 (fixed in the launcher),
S41-D2 (runner-only configurations), S41-D3 (the mode follows the round), S41-D4 (wording, provisional
under S41-D14), S41-D7
(the rulebook's word "rejected", the table form), S41-D13.

Plan review round 1 changed: the benchmark baselines (S41-D2), modes from the round (S41-D3), the
final mandate without a checklist (S41-D4), the recheck inputs (S41-D5), the severity field as the
owner decided (S41-D6), the answer rules by severity (S41-D7) and the `accounted` check (S41-D8).
