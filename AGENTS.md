# AGENTS.md — Repository Rulebook

This file is the single rulebook for this repository, for human contributors and coding agents.
Where it conflicts with a global or personal convention (for example `~/.claude/CLAUDE.md`), **this
file wins inside this repo**. Unit-test specifics are in [`tests/unit/AGENTS.md`](tests/unit/AGENTS.md),
which is part of this rulebook.

Every rule here is meant to be true of the repo today. If you find one that is not, fix the rule or
the repo in the same change — do not leave them disagreeing.

## Start here

| Question | Read | Kind |
| --- | --- | --- |
| What is this project, how do I run it? | [`README.md`](README.md) | overview |
| Where does the project stand right now? | [`docs/STATUS.md`](docs/STATUS.md) | current state |
| What must the system do? | [`docs/requirements.md`](docs/requirements.md) | authoritative |
| How is it built, which runtime state exists? | [`docs/architecture.md`](docs/architecture.md) | authoritative |
| What is the trust model, on one page? | [`docs/architecture.md` — Security model summary](docs/architecture.md#security-model-summary) | summary of the ARCH sections |
| Which test proves which requirement? | [`trace/tests.yaml`](trace/tests.yaml) | authoritative |
| How do I run a review, and where do its records live? | [Independent review](#independent-review): `scripts/run_independent_review.py`; each bundle's `review_attempts.jsonl` (attempt log) and `plan_review.md` or `review_<unit>.md` (review record); `scripts/review_brief.py` for the PR's decision brief | how-to |
| What must each stage's review ask at least? | [`docs/review_checklists/`](docs/review_checklists/) | authoritative, read by the review launcher from the base branch |
| What does each E2E or static test do, in plain English? | [`docs/test_spec.md`](docs/test_spec.md) | hand-written spec |
| Unit-test requirement matrix (M4 trust gates) | [`docs/unit_test_spec.md`](docs/unit_test_spec.md) | authoritative, read by `make traceability-check` |
| Known unfixed runtime/trust problems | [`docs/open_problem_log.md`](docs/open_problem_log.md) | authoritative |
| Which delivery mistakes were made, and what changed because of them? | [`docs/delivery_problem_log.md`](docs/delivery_problem_log.md) | authoritative |
| Who may hold which key, socket or secret; what each service may be | [`security/invariants.yaml`](security/invariants.yaml) with the `REQ-SEC` requirements | authoritative, checked by `make qa-deploy` |
| What is planned or waiting (proposed slices, actions only the user can take)? | [GitHub issues](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues), labels `slice` and `user-action` | tracking; a slice's decisions move into its `plan.md`, because reviewers read the repository, not issues |
| How was a past slice designed? | [`docs/slices/`](docs/slices/README.md) | frozen records |
| What happened, when? | [`docs/history/`](docs/history/) | history |
| Retired documents | `docs/archive/`, `docs/slices/archive/` | archive, do not follow |

## PoC scope and proportion

This repo is a proof of concept. Its goal is in [`README.md`](README.md): show that workload identity
is not permission, with tests that prove each boundary. It is not production hardening. The rules
below apply to every agent that plans, implements or reviews here, and hold until the user changes
them.

- **Delivery threat model.** Agents make honest mistakes: loose or wrong tests, weakened checks,
  skipped steps, stale evidence, wrong configuration. They do not deliberately attack CI, the
  gates, the evidence or the repo; that residual is accepted
  ([OPL-009](docs/open_problem_log.md)). This is about *how we deliver*. The *system under test*
  still defends against rogue workloads; that is what the PoC demonstrates.
- **Accepted PoC simplifications.** Keys and credentials live in files and environment variables
  on one Docker host. A design where each secret is visible only to the services that hold it is
  enough. KMS, HSM, Vault, per-key ownership proofs, CI-runner isolation and supply-chain controls
  are out of scope unless the user asks.
- **Ask before growing.** If a change makes the process bigger or more complex (a new gate, job,
  document, register, exception class or review step), say so and ask the user first. Every new
  check or process step states the failure it catches, what it costs and the simpler alternative
  that was considered; the user approves each addition. Prefer the smallest check that catches an
  honest mistake.
- **Threat model changes.** No agent changes, widens or narrows an approved threat model (this
  section's, or a plan's), in any stage or review round, without the user's approval. A proposed
  change is a decision concern for the user; reviewers judge against the approved model meanwhile.
- **Few exceptions.** Fix rather than except. Do not open an OPL, exception entry or plan note for a
  finding outside the threat model; such a finding is low, and one line in the review report is
  enough. Every exception must fit on one line and have an expiry.
- **Discovered issues.** Every issue found during the work is preserved and reported in the final
  handoff (the PR body) with its disposition and any tracking reference, whether it is
  pre-existing, introduced by the change, unrelated, or outside the threat model. Reporting an issue
  neither makes it blocking nor authorizes fixing it; an issue outside the threat model needs no
  OPL.
- **Review findings.** Give reviewers this section as context. Every finding carries a severity:
  blocking, high, medium or low. Only these are blocking:
  - a concrete false green or an OPL-005-class miss inside the threat model, with a failure scenario;
  - a contradiction;
  - an approved decision without a test;
  - a secret written into logs, evidence or any published record.

  A finding also blocks when it meets the "Blocks at this stage" section of a checklist the review
  received (its `--stage`) in [`docs/review_checklists/`](docs/review_checklists/): for example a
  requirement no test could verify, a design that lets an asset reach a non-holder, or a test that
  can pass while the behaviour is broken.

  A blocking finding is fixed before merge, or the user decides. **High** is a real defect or false
  claim below that bar, for example a misleading document, new behaviour without a test or an
  untested fail-closed path outside the system under test's security decisions; it is fixed in the
  same PR unless the user defers it. **Medium** has clear value (robustness, diagnosability, naming)
  and is fixed, or deferred with a tracking issue.
  **Low** (style, preference) is the author's choice. A simpler alternative is always low; a decision
  concern goes to the user, whatever its severity. Implementation details become notes for the
  implementation PR. Reviewers should expect production-hardening ideas (see the simplifications
  above) and report them as low at most.
- **Review loop.** A review unit (one change under review; a plan and its test plan are one unit)
  gets an initial review, round 1, and at most three fix rounds, rounds 2 to 4. Several reviewers in
  one round count as one round. Rounds continue until no blocking or high finding is open; after
  round 4, open blocking and high findings go to the user, and only the user can allow more rounds.
  A new revision keeps the count; only the user resets it, by an explicit act recorded with the
  user's words. The author (the fixer) answers every finding in writing, one table row per finding
  (`| <finding id> | <severity> | <answer> |`) in the review record's section
  `#### Answers to <attempt id>`, and the answer starts with one of four words:
  `fixed: <path>[, <path>…]: <what changed>`, naming at least one repository path; `deferred: #N`;
  `rejected:` with a reason the reviewer can check; or `owner:` with a link to where the user decides
  or was asked. Blocking and high findings take `fixed`, `rejected` (it stands only when the next
  round accepts it) or `owner`; medium and low findings take any of the four; a decision concern is
  always answered `owner:`. A rejection needs a reason the reviewer can check, for example: the
  failure scenario does not happen (with the evidence), it is outside the threat model, it is already
  covered by a named test or gate, or it does not meet the blocking criteria above. A finding
  labelled blocking that does not meet them is answered at the severity it does meet. In the next
  round the original reviewer (the same model and review role, in a fresh session given its own
  earlier report and the author's answers) sees each rejection and either accepts it, re-raises it
  with new evidence, or answers that it cannot determine it, which goes to the user; a finding still
  disputed after that goes to the user, who decides. A fix goes to the origin of the problem, and the
  author searches for the same cause elsewhere and says where it looked
  ([DPL-007](docs/delivery_problem_log.md#dpl-007-plan-review-answered-every-finding-by-adding-mechanisms)).
  The review ends when every blocking and high finding is fixed, accepted as rejected, or decided by
  the user. Only the user waives a blocker that is still disputed. The author asks the user before
  round 4 when a finding conflicts with an approved decision, or when rechecks re-raise the answer to
  the same finding in two rounds in a row (status `re-raised` under `accounted`; a re-raised finding
  keeps its ID).

## Operating model (black-box first)
- Treat the system as a black box first:
  - authored intent in `docs/requirements.md`
  - authored runtime/system model in `docs/architecture.md`
  - runtime-visible proof in `trace/tests.yaml` plus E2E evidence artifacts
- `DD-*`, `UT-*`, source helpers, and local test doubles are engineering controls, not the primary
  proof of system behavior.
- If a security-relevant behavior depends on hidden state, author it before implementation in the
  slice `plan.md` and, when runtime behavior changes, in the state inventory of `docs/architecture.md`.
- Do not introduce or keep runtime-significant behavior that exists only in code.

## Traceability model and IDs

Every requirement is traced the same way: requirement → test ID in `trace/tests.yaml` → entry in
[`docs/test_spec.md`](docs/test_spec.md) → implementation → stored, checked result. A test is an E2E
test (the harness runs it; its evidence is checked by `make qa-evidence`) or a static test (a gate
proves it on every run; see below).

Allowed links only: `REQ → ARCH` (architecture `Satisfies:`), `ARCH → DD` (DD `Implements:`) or
`ARCH → files` (architecture `Implemented by:`), `DD → UT` (UT `Covers DD:`), `REQ → E2E` and
`REQ → static test` (`trace/tests.yaml` `source_requirements`), and `ARCH → IT` (`trace/tests.yaml`
`source_architecture`; no integration cases exist yet).

| ID | Where it lives | Format (as enforced by `scripts/validate_traceability.py`) |
| --- | --- | --- |
| `REQ` | `docs/requirements.md` headings | `## REQ-<scope>-<code><n> — <title>`, e.g. `REQ-M1-R1`, `REQ-M4A-J3`, `REQ-M5-FT7`, `REQ-G-R2` |
| `ARCH` | `docs/architecture.md` headings | `## ARCH-NNN <title>` followed by `Satisfies: REQ-…` |
| `DD` | comment block above the implementing function in `services/**` or `scripts/**` | `# DD: DD-NNN` / `# Implements: ARCH-NNN` / `# Title: …` |
| `UT` | comment block above the test in `tests/unit/**` | `# UT: UT-NNN` / `# Test Description:` / `# Precondition:` / `# Expected Output:` / `# Covers DD:` |
| E2E test | `scripts/rogue_node_tests.sh` | harness IDs such as `M1-T1`, `M3.S4-T2`, `M5-T49`; mapped in `trace/tests.yaml` as `e2e_suite` / `e2e_case` entries |
| Static test | `trace/tests.yaml` (`type: static_test`) and a `docs/test_spec.md` heading | `<NAME>-<CODE>`, e.g. `DEPLOY-K1`, `EVID-T1`; names `source_requirements`, `gate: make <target>`, `negative_controls` (`<file>::<test>` tooling tests that show the gate fails on each kind of violation) and `result` (the stored report) |

- An ARCH section implemented by files that carry no DD-tagged functions (configuration such as
  Envoy or SPIRE files, the deployment register, a test or demo script) names them on an
  `Implemented by:` line; `make qa-trace` checks they exist. QA gate code carries no DD tags.
- IDs are never reused. Do not delete a requirement or architecture ID; mark it retired with the
  reason. Retired DD and test IDs are listed under `retired_ids` in `trace/tests.yaml`; reusing one
  fails `make qa-trace`.
- A requirement's status comes from its proofs and the deployment register, never from a run: it is
  not proved without a test, while an asset it protects has a `known_violations` row, or (the
  non-root rule, `REQ-SEC-D2`) within its grace date. A requirement that is not proved is a
  `requirements_without_proof` gap.
- `make qa-trace` fails on structural errors (unknown IDs, wrong link direction, missing fields,
  duplicates, missing files). On a PR it also fails on a coverage gap the PR adds compared with its
  merge-base (the gap gate); a gap added on purpose needs a one-line `accepted_gaps` entry in
  `trace/tests.yaml` with a reason and an expiry. Older gaps are reported, not failed.

## Slice workflow

Every change follows this workflow, scaled to its size: a small fix still gets a plan (it may be a
few lines) and its review, tests first when it changes behaviour, the final review and the
close-out, but not every section of the template needs more than "none". A slice bundle lives in `docs/slices/<slice-id>/`, starts from
`docs/slices/_template/`, and gets a row in the [slice index](docs/slices/README.md).

A slice passes seven stages, in this order. The plan's stage table says for each whether it applies;
a stage that does not apply is marked "none, with a reason". Each review is an
[independent review](#independent-review) with the stage's checklist from
[`docs/review_checklists/`](docs/review_checklists/) (`--stage`), and each review unit has its own round
limit (the [review loop](#poc-scope-and-proportion)).

| Stage | Produces | Review | Checks | Exit |
| --- | --- | --- | --- | --- |
| Discovery | `plan.md` and `test_plan.md` | plan review, list `plan-and-test-plan` | `make docs-check`, `make lint` | the plan review has no blocking or high finding open, and the user merges the plan PR |
| Requirements | new or changed `REQ` items in `docs/requirements.md` and their entries in `trace/tests.yaml` | requirements review, list `requirements` | `make qa-trace`, `make docs-check` | the review has no blocking or high finding open |
| Architecture and interfaces | `ARCH` sections and the state inventory of `docs/architecture.md`, and `security/invariants.yaml` | architecture review, list `architecture-and-interfaces` | `make qa-trace`, `make qa-deploy` | the review has no blocking or high finding open |
| Tests first | unit and E2E tests from the reviewed test plan, and their `docs/test_spec.md` entries | tests-first review, lists `unit-tests` and `e2e-tests` | `make tooling-test`, `make test-lint`, `make unit-guard-check`, `make docs-check`: the new tests fail as planned, every other test and check passes | each new test fails on the base code for the reason it exists, and the review has no blocking or high finding open |
| Implementation | the code and configuration the plan approved, with what it retires removed | implementation review, list `code` | every gate of [Quality gates](#quality-gates), the full E2E suite on a clean stack, `make qa-evidence` | every gate's CI job passes on the PR, and the review has no blocking or high finding open |
| Final review | the record of the unit `final` | final review, 4.1's final mode, no list | the decision brief, `scripts/review_brief.py` | no blocking or high finding open |
| Handoff | the PR body: the decision brief, the review answers, every discovered issue with its disposition | the user's approval | the CI result of the PR's head commit | the user merges |

### Discovery

- When the design or approach is not clear, run the grill-me skill
  ([`.claude/skills/grill-me/SKILL.md`](.claude/skills/grill-me/SKILL.md)) and resolve design choices one
  branch at a time; it is a prompt, versioned and reviewed like any other. Grill-me always asks which
  keys, sockets and secrets the slice touches and who may hold them, against the holders in
  `security/invariants.yaml`. When the design is clear, no grill-me is needed: the plan lists every
  decision with its source, either the user with the date, a link and the user's words quoted
  (reviewers cannot open GitHub), or "default by the author" with a reason, and the user confirms
  the defaults by approving the plan. The plan's "Assets and holders" section answers the keys,
  sockets and secrets question either way.
- Write `plan.md` (the stage table, decisions with their sources, requirements to add or change,
  hidden-state decisions, assets and holders, environment facts, rulebook changes, rule deviations,
  scope, out-of-scope, retirement) and `test_plan.md` (unit and E2E tests derived from the
  decisions, and each stage's list). A decision that depends on a fact outside the repository (file
  ownership, an API, CI history) records the probe and its result under environment facts; never
  assume it. A rule the slice does not follow is one line under "Rule deviations": the rule, the
  deviation, the user's words with the link, and the expiry.
- The plan review of both files runs before the user sees them. The plan PR's body opens with the
  decision brief, built by `scripts/review_brief.py` as at handoff. The user approves the plan by
  merging the plan PR; implement only from the plan as merged on the integration branch (see
  [Git rules](#git-rules)). On a branch that changes the rulebook (this file, `tests/unit/AGENTS.md`)
  or the slice templates, the author works by the base branch's version until the change merges.
- When the user chooses it for a slice, a slice may hold several sub-issues. They share one plan PR,
  which the user approves once, and one final PR with a section per sub-issue. Each sub-issue keeps
  its own review units (plan, implementation) with their own round limits, and the slice has one
  final review unit.

### Requirements, and architecture and interfaces

- Requirements and architecture are written and reviewed at their own stage, before tests and code
  are built on them; requirements, architecture and `trace/tests.yaml` are updated before runtime
  code is made to pass.
- When an upstream document is corrected after a downstream unit reviewed it, that unit's next round
  reviews the correction. The round counts against its limit, since a new revision keeps the count;
  a unit that had ended reopens with its next round number, and beyond round 4 the user decides, as
  for any extension. The reopened unit's review record notes the reopening and the corrected
  document.

### Tests first

- Add unit and E2E tests only from the reviewed `test_plan.md`. If a test needs a new assumption,
  return to discovery.
- Interface skeletons exist before the tests, so a red test fails for the reason it exists. The
  implementation log lists, for each new test, the failure it showed on the base code (the command
  and the first failure line).
- Each expected outcome comes from the approved plan, from a probe of the stack *before* the change
  (`probe@<commit>`), or from an existing assertion (`existing@<commit>`); never from watching the
  new implementation run. If a probe contradicts a value the plan approved, stop and ask the user;
  do not adjust the row.
- Every negative E2E test names a positive twin: the allowed case on the same route, which must pass
  in the same run (another test ID, or `internal` when a premise of the same test performs it).
- Every fail-closed path of a security decision gets a test that triggers it, and in
  capability-issuer and tool-b a mutant that the tests kill (`make unit-mutation`).
- A requirement may be proved statically, by a gate whose tooling tests show it fails on each kind
  of violation (as `make qa-deploy` proves the `REQ-SEC` requirements), where a runtime test would
  add nothing; the plan says which. It gets a static test entry in `trace/tests.yaml` and a heading in
  `docs/test_spec.md`.
- **Update `docs/test_spec.md` by hand** for every E2E or static test added or changed — plain
  English, not code: what it tests, how (premise, exercise, outcome, or the gate's check), and the
  evidence or result it leaves. Each test gets a heading `### <ID> — “<name>”`; `make docs-check`
  fails on a missing or stale heading, but it cannot judge the prose, so review it.

### Implementation

- Only approved behavior. Remove the dead code, stale paths, and artifacts that `plan.md` lists for
  retirement.
- Run `make qa-quality` (includes `qa-trace`, `docs-check`, `test-lint` and `qa-deploy`), the full E2E
  suite on a clean stack (`scripts/clean_stack.sh`, then `make e2e`), and `make qa-evidence`; the
  `e2e` CI check runs the same suite on the PR.

### Final review

- One unit `final` per slice, run in 4.1's final mode: the open question "What did everyone before
  you miss?", including any tracked document the change made false, with all the evidence and no
  question list. Its finding history is the other units' review records, which are in its copy. Its
  later rounds are rechecks.

### Handoff

All of the following, in the same change:
- add a dated entry to `docs/history/implementation_log.md` (what changed, validation results, what
  was not run and why);
- update `docs/STATUS.md`, which shows the open PoC work in its "needed before" order, and the
  slice's row in `docs/slices/README.md`;
- add or close entries in `docs/open_problem_log.md` for problems inside the threat model found or
  fixed, and in `docs/delivery_problem_log.md` for delivery misses (a stage skipped, a false claim, a
  review miss) found or fixed;
- turn work found but not done into a GitHub issue (label `slice` or `user-action`) whose body starts
  with "Needed before: <point>" and whose conversation is locked right away, or into a comment on the
  issue it belongs to; findings fixed or rejected in the PR, and notes outside the threat model, are
  not issues ("Few exceptions"). Close the issues the change finishes (`Closes #N` in the PR body);
- open the PR body with the decision brief that `scripts/review_brief.py` builds from the attempt logs
  and review records of the units in the PR (each unit's last verdict and severity counts; every
  `owner:` answer, decision concern, `cannot determine` answer and finding still disputed; every
  blocking or high finding answered `rejected`, with its reason; the origin stage against the stage
  that found each finding; the CI result of the PR's head commit). The user reads the plans and
  records where the brief points;
- put the implementation review's answers to the test-plan questions, every discovered issue with
  its disposition (see [PoC scope and proportion](#poc-scope-and-proportion)) and each issue's link in
  the PR body. The issue is the home of its status; the PR body is a snapshot and is not updated
  later.

### Independent review
- **Reviewer.** Never the author: a fresh headless Claude session confined to a frozen copy of the
  repository at the reviewed commit, without the review unit's review files (its review record
  and attempt log). It loads no instruction or settings files from the copy and receives the
  approved `AGENTS.md` and `tests/unit/AGENTS.md` from the PR's base branch. A recheck receives its
  own earlier report and the author's answers in its prompt. Effort is always explicit: medium for
  routine focused reviews and rechecks; high for initial plan, security, architecture and
  integrated reviews. The report says which reviewer ran, with which model and effort. The reviewer
  gets the intent (the approved plan, or the request), the change, and the approved rules, and may
  read the whole frozen copy; it never gets the author's reasoning. Reviews run through
  `scripts/run_independent_review.py`, which builds the reviewer's call and prompt and records every
  attempt, and the round it belongs to, in the slice's `review_attempts.jsonl`. The slice's review
  record (`plan_review.md` for a plan, `review_<unit>.md` for an implementation) keeps each task
  prompt, evidence and report verbatim with the author's answers. The launcher writes the record:
  under `### Attempt <attempt id>` a status line and the Prompt and Evidence blocks before the call,
  and the Report block after release, under the attempt log's lock; it scans the whole prompt with
  the evidence secret check, and for local paths, before anything is written or sent. The author
  writes only `#### Answers to <attempt id>`. `make docs-check` proves every record the launcher
  wrote against its attempt log, which replaces the author's hand check of earlier slices (earlier
  records hold the exact command, for example
  [`review_1b.md`](docs/slices/agentic-delivery-process/review_1b.md#reviewer-prompts-verbatim)).
- **Modes and prompts.** The launcher writes every prompt in a fixed order of sections, opening with
  the mandate of the review's mode, which follows the round: round 1 is the initial review (the
  final review for the unit named `final`), and every later round is a recheck. No launcher option
  and no task text removes or reorders a section, and the task text reaches the reviewer as claims to
  verify. A recheck gets the reviewer's own earlier report and the author's answers to it (only that
  section of the record, never the whole record); it lists every answer under `accounted` with the
  files it opened for it (a file it only searched goes under `searched`), and the launcher fails it
  when it leaves an answer out, names an opened file it did not read, or did not read a file that a
  `fixed:` answer names or a `rejected:` answer cites. Whoever writes a task text never
  makes a file list the scope, never says "only check X", and never asks a closed recheck question.
- **What the reviewer receives.** The launcher computes the review's inputs; the author does not
  choose or summarise them. The files under review come from the diff between the merge-base and
  the reviewed commit, deleted files apart; `--path` only puts files first and carries the
  empty-review rule. The upstream items are the governing plan (the bundle of the review record)
  with its decision IDs, the plans of other bundles the change touches, and the requirement,
  architecture and test items the trace model links to it, each with where it was found, followed
  by the question whether a problem originates upstream. The evidence is computed in a scratch
  clone of the reviewed commit with only `PATH`, `LANG` and a scratch `HOME` (which links only the
  interpreter's user site-packages): the changed script lines and branches the tooling tests do not
  run, the trace gaps among the upstream items, and the CI results of the reviewed commit from the
  public API. A command that cannot run is shown as failed, and the reviewer accounts for every
  numbered evidence entry under `accounted`, as `explained` or `flagged` with the finding it raised.
- **Stage checklists.** Each review gets its stage's list from
  [`docs/review_checklists/`](docs/review_checklists/) as the minimum, never the limit: `--stage
  <type>` reads the list from the base commit, so a change cannot rewrite the list it is reviewed
  against; the tests-first stage takes `unit-tests` and `e2e-tests`; the final review takes none.
  When the base has lists, a review without `--stage` is refused. The author reads the stage's list
  before writing that stage's artifact. A finding names the list question that prompted it, where one
  did (`question`, for example `code:10`). The research behind the lists, with each source quoted, is
  [`research.md`](docs/slices/poc-4-4-stage-checklists/research.md) of slice 4.4. When an open review
  finds a class of defect a list lacks, or a mandate wording that misled a reviewer, the author
  proposes the list item or the wording in the PR, and the user approves it.
- **Models and usage limits.** Agents use Claude models. Codex is used only for scoped
  implementation, and only while Claude's 5-hour or weekly usage is above 70%. Reviews run on
  Claude; when a usage limit is reached, work pauses until it resets. The default reviewer model is
  Claude Opus, by the user's reasoned choice of 2026-11-09; slice 4's benchmark measures prompts, not
  models.
- **Plan review** (discovery). The reviewer reviews `plan.md` and `test_plan.md` for security, test
  adequacy and consistency, under [PoC scope and proportion](#poc-scope-and-proportion).
  `docs/slices/<id>/plan_review.md` keeps each round's report verbatim, the SHA-256 of the files
  reviewed, and the author's answers (in the review loop's table) separately. Each round ends with
  "approvable within the threat model: yes or no"; from round 2 a new finding counts only if it is
  blocking or high, except simpler alternatives and decision concerns (below), which every round may
  report.
  The plan states the threat model the reviewer judges against: the
  [delivery threat model](#poc-scope-and-proportion) applied to the slice's own change, and the
  system-under-test threat the slice touches.
- **Implementation review** (implementation). The reviewer answers the questions in the test-plan template
  (`docs/slices/_template/test_plan.md`: which wrong failure would still pass each new or changed
  test, whether a key, socket or secret now reaches a service outside its holders, and whether each
  new file's purpose comment and names say what it does) in the PR body. A "yes" to the first two
  blocks, under the same review loop; findings on purpose comments and names are medium.
- **Fixes stay within the agreed decisions** (the plan's decisions, or the request, and this file).
  Before answering a finding with a new mechanism, the author names the upstream choice that causes
  it and weighs changing that choice; removing or changing a mechanism is preferred over adding one.
  A fix that would change an agreed decision goes to the user as a question before it is applied.
- **Report sections.** Besides findings of each severity, every round may report *simpler
  alternatives* (a mechanism that could be removed or simplified within the agreed decisions; always
  low) and *decision concerns* (an agreed decision that itself seems to cause a problem; for the
  user, never applied by the author). The reviewer may check metadata of secret files
  (existence, owner, mode, readability), never their content.

Hidden-state rule: if a decision depends on hidden state, `plan.md` lists the state/key name, store,
writer, reader, TTL or lifecycle, decision impact, and whether it is authoritative or advisory.
Mandatory for security-relevant Redis, file, cache, policy, or derived state.

Retirement rule: every `plan.md` states what old logic is removed, what compatibility behavior is kept
temporarily (if any), and which docs/tests/artifacts are deleted or archived. If nothing is retired,
say so.

## Quality gates

Every CI gate is a job named after its make target in `.github/workflows/ci.yml` (workflow `CI`).
A gate's result is its CI job's conclusion on GitHub; a local or offline rerun is a diagnosis and
never replaces it.

| Gate | Command | Enforced by | Threshold |
| --- | --- | --- | --- |
| Trace model | `make qa-trace` | CI, every push/PR | zero structural failures; on a PR (`--mode pr --base <base>`), no coverage gap the PR adds compared with its merge-base unless `accepted_gaps` in `trace/tests.yaml` lists it with a reason and an unexpired date (an expired or stale entry fails); a merge-base that cannot be resolved or read fails. On `main` (`--mode push`) gaps are reported |
| Documentation | `make docs-check` | CI | every harness test and every static test in `trace/tests.yaml` has a `docs/test_spec.md` heading and vice versa; relative links and `#anchors` in live docs resolve; every tracked image in `docs/` is referenced and every `.puml` has its `.svg`; every slice bundle is in the slice index; `TEST_ONLY=` examples name real tests; every review record the launcher writes holds exactly the Prompt, Evidence and Report blocks its attempt log names, a recheck's answers are unchanged since it read them, and every finding of a released report has an answer its severity and kind allow (`scripts/check_review_records.py`) |
| QA tooling tests | `make tooling-test` | CI | `tests/tools/` (pytest) and `tests/shell/` pass; one of them runs `ruff check services scripts` (ruff's default rules, without `ruff_changed_files.toml`), so the whole tree stays clean |
| E2E outcome lint | `make test-lint` | CI | no outcome guard in `scripts/rogue_node_tests.sh` accepts several outcomes (`assert_file_any`, broad error regexes, `!= 200`), swallows failure (`\|\| true`), checks only a non-zero exit, or is a test of negative greps only; a multi-outcome guard needs `# test-lint: alternate: <reason>` |
| Changed-files lint | `make lint` | CI, PRs only (own job) | in every file the PR adds, modifies or renames, no ruff or shellcheck finding that is new or worse than at the merge-base (a finding is keyed by file, rule and enclosing function, or line text, and compared by count and value, so existing violations stay and a pure rename is not new): ruff's default rules, complexity C901 ≤ 10, at most 12 branches, 5 arguments and 50 statements per function (PLR0912, PLR0913, PLR0915), naming (N) without exceptions, security (S, except `assert` in `tests/`); the limit, naming, F401 and F841 rules ignore `noqa`; the configuration `ruff_changed_files.toml` is read from the merge-base, so a change cannot loosen it; every added `.py` file, shell script (by extension or shebang), YAML, TOML, Dockerfile or Rego file starts with a purpose comment (tool directives do not count), and every added Markdown file with a `#` title and a paragraph, after a leading YAML front-matter block if it has one, as a skill file needs (coding rule 8; other formats are left to the review); a missing base or tool fails |
| Deployment register | `make qa-deploy` | CI (without image inspection; the `e2e` job runs it with image users inspected) | every service's image, user, networks, ports, mounts, secret env names and privileges match `security/invariants.yaml`; every protected asset reaches only its holders, except unexpired known violations of open OPLs; register holders equal the `REQ-SEC` `Holders:` lines; non-root except the grandfathered baseline until 2027-01-31 |
| Unit guard integrity | `make unit-guard-check` | CI | every unit test has premise, exercise, outcome guards |
| Unit trust bundle | `make unit-trust` | CI | total line coverage ≥ 85%; branch coverage ≥ 75% on `services/capability-issuer/app.py` and `services/tool-b/server.py`; unit traceability check; invariant, negative-control, hybrid-critical suites; invariant flake check ×5 |
| Diff coverage | `make unit-diff-cov` | CI, PRs only (own job) | ≥ 90% of changed lines in `services/capability-issuer/` and `services/tool-b/` |
| Mutation | `make unit-mutation` | CI | score ≥ 70% (capiss and tool-b), counting untested and skipped mutants as not killed; an empty run fails |
| Gate consistency | `make gate-consistency` | CI | every row this table marks as enforced by CI has a CI job of the same name that runs `make <name>`; every CI job has such a row; every CI job is a required check of the integration branch's ruleset (`RULESET_URL` in the `Makefile`) and every required check is a job (the ruleset is read from the public GitHub API; a failed read fails) |
| Full E2E suite | `make e2e` | CI, every push/PR; and local on a clean stack, required at the implementation stage | all pass; warnings reviewed. The CI job then runs `make qa-deploy` with image users inspected and `make qa-evidence`, and uploads the publication set for 14 days only if the secret check found nothing |
| E2E evidence | `make qa-evidence` | in the CI `e2e` job; local, after the E2E run | every test has premise/exercise/outcome evidence and a PASS line; no file of the publication set (`PUBLICATION_SET` in the `Makefile`: `test_report.log`, `artifacts/rogue-tests/`, `artifacts/quality/`) holds a secret by shape: a PEM private key, a base64 PKCS#8 private key, base64 of a PEM private key, a base64 or base64url run of ≥ 200 characters with ≥ 20 distinct ones outside certificates, a `JIRA_API_TOKEN=` or `Authorization:` line with a token-like value (20 characters or more, or a digit), or an Atlassian API token; an unreadable file fails; a finding names the file and kind, never the value |

Standards that are **not** gated yet (follow them for new and changed code):
- Functions above the complexity limit (ruff C901, as `make lint` measures it) are tracked as debt
  in `docs/STATUS.md`; do not make them worse.
- `mypy` and `bandit` are not configured in this repo.

## Coding rules
1. No secrets in source, config, logs, or evidence. Credentials come from the environment at runtime.
2. No Python `eval()`, `exec()`, or `__import__()` on dynamic input. (Redis `EVAL` of fixed Lua scripts is fine.)
3. Validate and reject external input at service boundaries; internal functions trust their callers.
4. Fail closed: any unexpected error in a security decision path denies.
5. No broad `except Exception` in enforcement or validation paths; catch specific exceptions.
6. Audit events never contain token values, passwords, or key material; E2E tests assert this.
7. Secrets this repository creates are stored in a standard, recognisable format (private keys as
   PKCS#8 PEM), so the evidence secret check finds them by shape. Secrets created by others (SPIRE
   key stores, join tokens, Jira tokens) keep their format.
8. Every new file starts with a comment that says what the file is for: in Python the module
   docstring; in Markdown a `#` title followed by a paragraph that says what the document is for
   (after its YAML front matter, in a skill file);
   in every other format with comments (shell, YAML, TOML, Dockerfile, Rego, patches, text and
   others) a first comment or line after any shebang or YAML document marker. Only formats without
   comment syntax (JSON, JSONL) and binary files are exempt. Names say what a file, function or
   component does.

## Documentation rules
- One home per fact. Before adding a document, check the [Start here](#start-here) table; extend the
  owning document instead of creating a parallel one.
- `docs/test_spec.md` is hand-written and must describe every E2E test the harness runs.
- Implemented slice bundles are frozen records; do not rewrite them to match later reality.
- Tests for QA tooling (`scripts/check_docs.py` and similar) live in `tests/tools/`; shell-level tests
  live in `tests/shell/`. The unit-test rules in `tests/unit/AGENTS.md` apply only to `tests/unit/`.
- Retire documents with `git mv` into `docs/archive/` (or `docs/slices/archive/`); never delete them.
- Architecture diagrams use a C4-style, grid-aligned layout: group by trust boundary or network zone,
  flows left-to-right or top-to-bottom, orthogonal connectors with few crossings, planned components
  labeled as such.

## Git rules
- No `Co-Authored-By` trailers for AI assistants in commit messages.
- Agents act on GitHub as `gunaseelan-agent` and open pull requests; only the user approves and
  merges into the integration branch. Before a GitHub write, check that `gh api user --jq .login`
  prints `gunaseelan-agent`; if not, stop and tell the user.
- Open pull requests against the integration branch: `main`, or `poc/agentic-sdlc` for work on the
  agentic-SDLC PoC. PoC work happens on `poc/agentic-sdlc`; each slice uses a branch
  `poc/slice-<n>-<topic>` and merges back by PR with the user's approval. `main` is not changed by
  the PoC until the user decides.
- Avoid stacking. A stacked PR is merged only after its base shows the integration branch (GitHub
  retargets it when the base branch is deleted) ([DPL-008](docs/delivery_problem_log.md#dpl-008-a-stacked-pr-was-merged-into-its-stale-base-branch-instead-of-main)).
- On `poc/agentic-sdlc` only the user's approval counts: `.github/CODEOWNERS` names the user, and
  the branch's ruleset requires a code-owner review.

## Environment
- Docker Engine + Docker Compose v2. Linux, or macOS with Rancher Desktop.
- Run every command from the repo root.

## Quick start
1. Preflight:
   ```bash
   docker info >/dev/null
   docker compose version
   docker context ls
   scripts/clean_stack.sh --check
   ```
2. Clean state when needed: `scripts/clean_stack.sh` (run it again if the first pass reports a
   permission warning on a root-owned file).
3. Bring the core stack up:
   ```bash
   docker compose -f compose/spiffe.compose.yml up -d --build
   ```
4. Inspect SPIRE agent logs for workload SVID activity:
   ```bash
   docker compose -f compose/spiffe.compose.yml logs -f --tail=200 spire-agent
   ```
5. Tear down:
   ```bash
   docker compose --profile tests -f compose/spiffe.compose.yml down --remove-orphans
   docker compose -f compose/spiffe.compose.yml down --remove-orphans
   ```

## Test commands
- Full suite (writes `test_report.log` and evidence under `artifacts/rogue-tests/`, builds every image, and gives
  the root-owned output back to you so `make qa-evidence` can run):
  ```bash
  scripts/clean_stack.sh
  make e2e
  ```
- Specific test IDs:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build \
    -e TEST_ONLY=M3.S3-T3,M3.S4-T2 rogue-tests
  ```
- Selected milestones:
  ```bash
  docker compose --profile tests -f compose/spiffe.compose.yml run --rm --build \
    -e TEST_MILESTONES=m1,m2,m25,m3 rogue-tests
  ```
- Keep `--build`: `scripts/rogue_node_tests.sh` is copied into the `rogue-tests` image, so without it
  a run silently uses the harness from the last build. (The `varambu` wrapper is bind-mounted and needs
  no rebuild.)
- A targeted run overwrites `test_report.log`, so `make qa-evidence` needs a full run to pass.
- Live Jira tests (`M5-T55`, `make jira-live-smoke`) need explicit live configuration; default runs
  use deterministic mocks.

Profiling is on by default (`TEST_PROFILE=1`); timings go to `artifacts/rogue-tests/guard_timings.tsv`
and `guard_timings_top25.txt`. Disable with `-e TEST_PROFILE=0`.

## Evidence checks (false-green guard)
After a full run, `make qa-evidence` validates the evidence. Evidence holds no token values: guards work in a
scratch directory, and the harness publishes it with every token-shaped value replaced by its SHA-256 fingerprint.
To inspect by hand:
```bash
find artifacts/rogue-tests -maxdepth 1 -mindepth 1 -type d | sort
grep -Eq 'Failed: [1-9]' test_report.log && find artifacts/rogue-tests -name fail_reason.txt -print -exec cat {} \;
find artifacts/rogue-tests -name 'warning_reason_*.txt' -print -exec cat {} \;
find artifacts/rogue-tests -name skip_reason.txt -print -exec cat {} \;
```
- `fail_reason.txt`: terminal guard failure for that test.
- `warning_reason_*.txt`: the test passed through an accepted alternate path; review the condition.
- `skip_reason.txt`: an env-gated test did not run its exercise (for example `M5-T55` without live
  Jira). `make qa-evidence` counts it as skipped, never as validated, and only if the suite declares
  the gate for that test in `trace/tests.yaml` (`env_gates`), the gate check left premise evidence,
  and no exercise or outcome artifacts exist. The test still prints `PASS` in `test_report.log`.

## Docker guardrails
- Never run Docker lifecycle commands in parallel. Serialize `scripts/clean_stack.sh` and
  `docker compose … up/down/run`; run `ps`/`logs` only after the mutating command finishes.
- `capability-issuer-no-opa-envoy` is test-only (`tests` profile); never use it outside tests.
- Prefer `scripts/clean_stack.sh` over manual cleanup.
- Keep evidence under `artifacts/rogue-tests/` unless you deliberately set `ROGUE_TEST_EVIDENCE_DIR`.
- macOS / Rancher Desktop: point the Docker CLI at the `rancher-desktop` context
  (`docker context use rancher-desktop`). On socket/context mismatches or permission-constrained
  bind mounts under `tmp_svid/` or `artifacts/`, confirm `docker info` works and rerun
  `scripts/clean_stack.sh`.
