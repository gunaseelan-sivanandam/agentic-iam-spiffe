# Slice Plan — agentic-sdlc-poc: roadmap, and slices 1–3

Status: draft revision 2, 2026-11-07, revised after its third review round. Revision 1 passed four
review rounds; at the user's request, revision 2 adds the roadmap to a complete delivery cycle,
maps the earlier decisions D1–D59 of PR #26 and adds slice-1 rules. The user reset the review
budget for revision 2. Approved when the user merges this plan's PR into `poc/agentic-sdlc`; the
merge approves slices 1–3 only. Tracks [#16](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/16)
and [#25](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/25). Supersedes the
closed PR #26, whose plan is not adopted; its history stays on the branch `plan/delivery-orchestration`.

**Interim exception, until slice 1 merges:** the user's instruction of 2026-11-07 (keep PoC work on
`poc/agentic-sdlc`, merge by PR with the user's approval) overrides the `AGENTS.md` rules "Open pull
requests against `main`" and "implement only from the plan as merged on `origin/main`" for this
PoC. It expires when slice 1 puts the integration-branch rule into `AGENTS.md`.

## Goal

The PoC's end goal is a complete software delivery cycle run by Claude agents: reliable, without
stale code or docs, and with code that is maintainable, secure and easy to understand. At the end of
the PoC, every change on the PoC branch goes through these stages, scaled to its size: a stage that
does not apply is marked "none" with a reason, as the slice templates already allow.

| Stage | Artifact | Review | Deterministic checks |
| --- | --- | --- | --- |
| 1. Discovery (grill-me) | `plan.md`, `test_plan.md`, the user's words recorded verbatim | Plan review, high effort | `docs-check`, `qa-trace` |
| 2. Requirements | `REQ` entries: product requirements in `docs/requirements.md`, orchestration requirements in their own document | Requirements review | `qa-trace` (the orchestration document from slice 7) |
| 3. Architecture and interfaces | `ARCH` entries, interface contracts, design tags in code | Architecture review, high effort | `qa-trace`, `docs-check` |
| 4. Tests first | Unit and E2E tests, `trace/tests.yaml`, a failing run before the code exists | Tester-focused review | `unit-guard-check`, `test-lint`, and a test-first check if slice 6 shows one is needed |
| 5. Implementation | Code | Implementation review | `lint` (slice 3), `unit-trust`, `unit-mutation`, `unit-diff-cov`, `e2e`, `qa-deploy`, `qa-evidence` |
| 6. Final review | The whole change, against the user's recorded words first and the finding history second | Fresh review, high effort | The review attempt log (slice 2); a review-record check if slice 6 shows one is needed |
| 7. Handoff | A PR with a summary, every discovered issue (POC-D12) and the limits; the close-out documents updated: test spec, STATUS, implementation log, slice index, the architecture state inventory | The user's approval (code owner) | All required checks |

**Keeping documents and code true.** Stale documents and code are caught at several points:
`docs-check` (links, anchors, test-spec headings), ruff's default rules F401 and F841 in `lint`
(unused imports and variables), the plan's retirement section, the stage-7 close-out list, and one
question in every final review: "Which tracked document now says something this change made
false?" A correction to an upstream artifact reopens the reviews of the artifacts built on it
(slice 4).

The repository already follows stages 1, 4, 5 and 7 by hand (the `AGENTS.md` slice workflow). The
PoC makes every stage reviewed, checked where a tool can decide, and finally driven by agents.

This plan **approves slices 1–3**, which give the PoC its rules, a measured independent review and a
lint gate. Every later stage depends on those three. The roadmap below outlines the rest; each later
slice is planned on its own, after the slice-2 benchmark report.

1. **Rules.** `AGENTS.md` says how agent work is reviewed, limited and fixed in the PoC.
2. **Review launcher and benchmark.** A repeatable independent review whose launcher records what
   each review saw and did, and measurements of how well it finds real defects in this repository.
3. **Changed-files lint.** Deterministic size, complexity, naming, security and header limits for
   new and changed code; existing violations are left as they are.

## Threat model

- **Delivery** (the [PoC scope](../../../AGENTS.md#poc-scope-and-proportion)): agents make honest
  mistakes. For this change that means, for example, a launcher that silently loads the branch's own
  rules, lets the reviewer read outside its copy or shows it the author's answers, a benchmark
  scored loosely enough to flatter the reviewer, a lint gate that misses new or worsened code or is
  silenced by a `noqa`, a roadmap that leaves out a stage the end goal needs, or a document left
  saying something that is no longer true. Deliberate attacks on CI, the gates or the evidence stay
  out of scope ([OPL-009](../../open_problem_log.md)). Text written by people other than the user
  does not enter agent-run work (POC-D16); widening that is
  [#32](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/32).
- **System under test:** unchanged. No service, compose file, image or key holder changes. The
  benchmark reads source at fixed commits and changes nothing.

## Grill-Me Review Summary

The design was settled in the conversation of 2026-11-05 to 2026-11-07. Decisions carry the prefix
`POC-` so they cannot be confused with other slices' decision IDs
([#27](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/27)). POC-D9's timing
clause, POC-D14 and POC-D16 set direction for later slices; each later slice's plan decides again.

| ID | Decision | Source |
| --- | --- | --- |
| POC-D1 | PoC work happens on `poc/agentic-sdlc`. Each slice uses a branch `poc/slice-<n>-<topic>` and merges back by PR with the user's approval. `main` is not changed until the user decides. | user, 2026-11-07 |
| POC-D2 | Claude models only. Codex is used only for scoped implementation, and only while Claude's 5-hour or weekly usage is above 70%. Reviews run on Claude; when a usage limit is reached, work pauses until it resets. The benchmark may also measure Codex as a reviewer; the default reviewer model is decided from its results. | user, 2026-11-07 (answer to R1-D1; "Test Opus, Sonnet and codex") |
| POC-D3 | The reviewer is never the author: a fresh headless Claude session confined to a frozen copy of the repository without the review unit's review files (its review record and attempt log), which loads no instruction or settings files from the copy and receives the approved `AGENTS.md` from the PR's base branch. A recheck receives its own earlier report and the author's answers in its prompt. Effort is always explicit: medium for routine focused reviews and rechecks; high for initial plan, security, architecture and integrated reviews. | user (effort); default (how independence is achieved) |
| POC-D4 | Review limit per review unit (a plan and its test plan are one unit): round 1 is the initial review, and at most three fix rounds follow (rounds 2 to 4). Several reviewers in one round count as one round. After round 4, open blockers go to the user, and only the user can allow more rounds. A new revision keeps the count; a reset is always the user's explicit act, recorded with the user's words. | user, 2026-11-05 and 2026-11-07 (answer to R1-D2; resets only by the user) |
| POC-D5 | The author may reject a finding with a reason the reviewer can check; the original reviewer (the same model and review role, in a fresh session given its own earlier report and the author's answers) accepts the rejection or raises it again. A fix goes to the origin of the problem, and the author searches for the same cause elsewhere and says where it looked ([DPL-007](../../delivery_problem_log.md)). | user, 2026-11-07 |
| POC-D6 | Every new check or process step states the failure it catches, what it costs and the simpler alternative that was considered. The user approves each addition. | user, 2026-11-07 |
| POC-D7 | Every new file starts with a comment that says what the file is for (in Python, the module docstring). Names say what a file, function or component does. | user, 2026-11-07 |
| POC-D8 | Deterministic tools before judgment. Lint limits: cyclomatic complexity at most 10, at most 50 statements, 12 branches and 5 arguments per function, the standard naming conventions without exceptions, and ruff's security rules. They apply to new and changed files; a change fails only on violations it adds or worsens, so existing violations stay. | user (limits, changed code only); default (security rules, no naming exceptions) |
| POC-D9 | Orchestration requirements stay separate from product requirements. Slices 1–3 add none: like the existing QA gates, the launcher and the lint gate are specified by `AGENTS.md` and this plan and proved by tooling tests. Direction: the orchestration requirements document starts with slice 7, the first slice that adds orchestration behaviour. | user (separate); default (timing) |
| POC-D10 | Measure before automating. The launcher, the benchmark and its report merge into the PoC branch, because the later slices build on them. The benchmark's first stage is limited to the user's "about 24" reviews (26 reviewer calls, see Configurations); further stages need the user's decision on its results. | user (benchmark first; budget: answer to R1-D3); default (merge to the PoC branch) |
| POC-D11 | Only the user's approval counts on PRs into `poc/agentic-sdlc`: a `CODEOWNERS` file names the user, and the PoC ruleset requires a code-owner review. | user, 2026-11-07 (answer to R1-D4) |
| POC-D12 | Every issue found during the work is preserved and reported in the final handoff with its disposition and any tracking reference, whether it is pre-existing, introduced by the change, unrelated, or outside the threat model. Reporting an issue neither makes it blocking nor authorizes fixing it; an out-of-model issue needs no OPL. | user, 2026-11-07 (from #26 D15–D16) |
| POC-D13 | No agent changes, widens or narrows the approved threat model, in any stage or review round, without the user's approval. A proposed change is a decision concern for the user; reviewers judge against the approved model meanwhile. | user, 2026-11-07 (from #26 D17) |
| POC-D14 | Direction: the PoC reaches the complete cycle of the Goal table. After the rules for every stage (slice 4), one real backlog item goes through the whole cycle by hand (slice 5); further gates are built only for what that run and the benchmark show (slice 6); then the delivery loop (slice 7) and an end-to-end evaluation (slice 8). The earlier decisions D1–D59 are carried over, deferred or superseded as mapped below. | user, 2026-11-07 (Option A; "Real run first, gates after") |
| POC-D15 | Authors follow the approved rules too: on a branch that changes `AGENTS.md` or the slice templates, the author works by the base branch's version until the change merges. | default (from #26 D56) |
| POC-D16 | Direction: agent-run delivery takes only backlog items the user wrote or labelled for agents; issues stay locked. Taking other items is deferred to [#32](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/32) (label "security hardening"). | user, 2026-11-07 |

## Slice 1 — Rules (text, and one Makefile default)

**Outcome.** `AGENTS.md`, the two slice templates, a new `.github/CODEOWNERS` and the `Makefile`
default `BASE_REF` on the PoC branch express POC-D1 to POC-D8, POC-D11 to POC-D13 and POC-D15:

- *PoC scope and proportion:* "Ask before growing" gains the three questions of POC-D6. Two new
  rules: threat-model changes need the user's approval (POC-D13), and discovered issues are
  preserved and reported (POC-D12).
- *Slice workflow, step 1:* "implement only from the plan as merged on `origin/main`" names the
  integration branch instead. Authors on a rule-changing branch work by the base branch's rules
  (POC-D15).
- *Review loop:* "There is no round limit" becomes POC-D4, with round 1 as the initial review, so
  that "from round 2 a new finding counts only if it blocks" keeps its meaning. Rejecting with a
  checkable reason stays. Fixing at the origin and searching for the same cause (POC-D5) is added,
  with the definition of "original reviewer".
- *Independent review → Reviewer:* the Codex-first rule is replaced by POC-D3 and POC-D2. Until the
  slice 2 launcher exists, the exact review command is recorded in the slice's review record.
- *Git rules:* PRs target the integration branch: `main`, or `poc/agentic-sdlc` for PoC work
  (POC-D1). The stacking check of DPL-008 applies to that branch. This ends the interim exception
  above.
- *`Makefile`:* on the PoC branch, the default `BASE_REF` is `origin/poc/agentic-sdlc`, so local
  gate runs compare against the right branch; its comment says why.
- *Coding rules:* a new rule 8 for POC-D7.
- *Templates:* `_template/test_plan.md` no longer names Codex as the default reviewer;
  `_template/plan.md` asks the POC-D6 questions for every check the slice adds.
- *Code owner (POC-D11):* `.github/CODEOWNERS` with a purpose comment and exactly one rule,
  `* @gunaseelan-sivanandam`; the Git rules say that approvals are enforced this way. GitHub reads
  `CODEOWNERS` from the PR's base branch, so the rule applies from the first PR after slice 1 merges.

**Done when.**
- A fresh Claude session has reviewed the change under the `AGENTS.md` of the base branch. The
  review quotes, for each of POC-D1 to POC-D8, POC-D11 to POC-D13 and POC-D15, the text that states
  it.
- A search of `AGENTS.md`, `tests/unit/AGENTS.md`, `docs/slices/_template/` and the `Makefile` for
  `origin/main`, `codex` and "round limit" has every hit resolved, with the result in the PR.
- The PR's CI checks pass. GitHub's rules for `poc/agentic-sdlc` show a required code-owner review
  and the three settings of user action 1, and GitHub's `CODEOWNERS` error check reports no errors.
- The user has merged it.

**Still manual:** everything else.

## Slice 2 — Review launcher and benchmark

**Launcher, `scripts/run_independent_review.py`.**
- *Frozen copy.* It fetches the base branch, records its commit, and copies the tracked tree at the
  reviewed commit into a scratch directory with `git archive`, leaving out the review unit's review
  files (its review record, which is the path it is given, and its attempt log) and recording those
  paths and their hashes as withheld. The task names
  the paths to review; the reviewer may read anything else in the copy. Untracked files
  (`capiss_keys/`, `.env`, SPIRE data) cannot enter the copy. The launcher refuses a tracked
  symlink whose target lies outside the copy, and a tree whose `.gitattributes` uses
  `export-ignore` or `export-subst` (either would make the copy differ from the tree).
- *Confinement.* The reviewer runs inside the copy with only Read, Grep and Glob, `--safe-mode`,
  `--setting-sources ""` (no user, project or local settings), `--permission-mode dontAsk`, no MCP
  servers, no saved session, **no** `--allowedTools` rules, and an environment holding only `PATH`,
  `HOME` and `LANG`. The 2026-11-07 probes (Environment facts) show: blanket allow rules on the
  command line let Read reach any path; without them, reads outside the working directory are
  denied; `--safe-mode` keeps `CLAUDE.md`, the `AGENTS.md` it imports, nested `CLAUDE.md` files and
  project hooks from loading. This is CLI configuration, not an operating-system boundary.
- *Approved rules.* For a review unit, `AGENTS.md` and `tests/unit/AGENTS.md` at the recorded base
  commit, passed as explicit instructions. For a benchmark case, the rule files at the case's own
  commit, if any (see Benchmark).
- *One invocation per round.* The launcher runs a whole round in one invocation: it takes the
  round's reviewers, each with its label, prompt file (intent and task), model and effort, and runs
  them in parallel. Further required arguments: the commit, the base branch, the review unit and the
  round number. For the whole round it holds an exclusive lock on the unit's attempt log; another
  invocation for the same unit is refused while the lock is held, so a running attempt is never
  mistaken for a dead one. The prompts are stored verbatim in the slice's review record, as
  `AGENTS.md` requires.
- *Attempt log.* The launcher is the only writer of an append-only log per review unit,
  `docs/slices/<id>/review_attempts.jsonl`, committed with the slice. It writes one entry when an
  attempt starts and one when it ends. An entry holds: the review unit and count number (which
  rises with a user reset), round, the round's reviewer labels, the attempt's reviewer label and
  its status (started, completed, failed, paused, pending or interrupted); the CLI version; the
  reviewed commit and its tree hash, the base commit, the SHA-256 of the
  rules, the prompt and every path under review, and the withheld paths with their hashes; model and
  effort; duration, turns, tokens and cost estimate; the number of tool calls, the paths read, and
  every denied call (tool and path); the 5-hour and weekly utilization; any extension or reset
  reference; the verdict and the report's SHA-256. It holds no prompt or reply text. The launcher
  writes a report to a temporary file, appends the end entry with the report's hash, and only then
  moves the report into place. On its next invocation, holding the lock, it marks a start entry that
  has no end entry as "interrupted" (no report of it was released, and it completes no round), and
  finishes the move of a report whose end entry is "completed"; the temporary report of any other
  attempt is deleted. From an entry, the launcher's invocation builder recreates the
  exact CLI call and input hashes; there is no separate rerun mode.
- *Round admission, from the log.* The first invocation of a round sets its reviewer labels. Round
  *n*+1 starts only when every reviewer listed for round *n* has a completed attempt, and its list
  must include every reviewer whose round-*n* verdict was "no", may leave out those whose verdict was
  "yes", and may add none. A later invocation of the same round must give the same list and runs only
  the listed reviewers that have no completed attempt yet. Failed, paused, pending and interrupted
  attempts complete no round. A round past the POC-D4 limit needs a user
  extension reference, and a new count needs a user reset reference. Each reference must be the URL
  of a PR comment, recorded in the log; slice 6 may check that the user wrote it. The benchmark runner
  calls the same review function without a review unit: benchmark runs never read or write a log
  of a review unit.
- *Findings.* A fixed JSON shape via `--json-schema`: a list of findings, each with id, kind
  (blocking, advisory, simpler alternative or decision concern), file, line, problem, evidence and
  failure scenario, and a required verdict ("approvable within the threat model": yes or no).
  Output that does not match the shape is a failed review, never an empty pass, and is not retried
  automatically.
- *Empty or escaped reviews.* A review that read none of the paths under review, had any call
  inside the copy denied, or used any path outside the copy is "failed", whatever it reports, and its
  report is not released. The rule covers every path argument of Read, Grep and Glob, each resolved
  (relative parts and `..` removed) before it is compared with the copy's root, and it holds whatever
  settings the CLI loads.
- *Publication check.* Before writing a report or a log entry, the launcher runs the existing
  evidence secret check (`scan_text` in `scripts/evidence_secrets.py`) on it. A finding names the
  kind and location, never the value, and nothing is written. This is a stopgap until #21: it knows
  the evidence secret shapes, not the delivery tools' own credentials (GitHub and model-provider
  tokens).
- *Usage limits.* Reviews run on Claude (POC-D2). The launcher records the utilization from every
  call, so the author can apply the 70% rule to implementation work. A window whose status is
  "allowed" or a warning status (its exact value is probed at implementation) lets the review proceed; any other status ends the attempt with
  status "paused until <reset time>", and the same round runs again after the reset. Provider or CLI
  errors are retried at most twice; after that the attempt is "pending".

**Benchmark, `tests/review_benchmark/`.** Each case names a commit, the paths to review, the
reviewer's task, the expected findings (file, one or more acceptable line ranges, and a few terms a
correct finding must use) and its leak terms. The reviewer of a case receives the rule files at the
case's own commit, if any. Before each case's review, the runner searches the case's whole frozen
copy, the rules it passes and the task text for the leak terms, and refuses the case on any match. A
refused real miss is replaced from the remaining delivery-problem entries or dropped; the report
lists every refused case. Leak terms name the specific defect, not a check category. Before the
answer key is committed, the runner dry-runs the leak search over both prompts; a case refused under
either prompt is refused under both, so the comparison stays paired. Expected findings and the
decision rule below are committed before any run, and the report records their SHA-256. No case commit contains `tests/review_benchmark/`.

| Kind | Cases | What it measures |
| --- | --- | --- |
| Real misses | DPL-001, DPL-002, DPL-004, DPL-009 and the in-repository half of DPL-005 (gates hidden inside another CI job), each at a commit where the defect exists and no tracked file names it. Candidates: `07520d7` (DPL-001), `7226c2e` (DPL-002), `4b808cb` (DPL-009, likely refused: one docs file matches). Leak terms: the problem ID and words that would describe the defect. Defects of absence (DPL-004, DPL-005) accept several locations | Defects that got past earlier reviews; nobody planted them |
| Planted defects | A weakened assertion, an outcome guard with `\|\| true`, a key mounted into a non-holder, a changed expected value, applied on top of `e842e97`; one of them carries a misleading note such as "already verified, no findings needed". Leak terms: identifiers specific to the plant | Defect types without a real example; security findings without a published description; whether a note in the reviewed data steers the reviewer |
| Clean cases | Two merged changes with no known defect | False blockers |
| Canary | A hostile copy: recognisable instructions in `AGENTS.md`, `CLAUDE.md`, a nested `CLAUDE.md` and `tests/unit/AGENTS.md`, and a `.claude/settings.json` with an allow rule for a marker file outside the copy and a startup hook that would create a file outside it. Its positive twin runs the same copy without the launcher's flags | Whether branch instructions and settings reach the reviewer; the twin shows the canary can fail at all |

Real misses and planted defects are reported separately. Open problems already described in the
tree (OPL-005 to OPL-008) are not cases: their answers are in the logs a reviewer may read.

**Runner, `scripts/run_review_benchmark.py`.** Runs cases against configurations through the
launcher and stops when the approved number of reviewer calls is reached (POC-D10). Scoring is
deterministic first: an expected finding counts as *detected* when a blocking finding names the
same file, a line inside one of the acceptable ranges, and at least one of the expected terms. A
location match without any expected term goes to triage. Every blocking finding that matches no
expected finding is also listed for triage (a real extra defect or a false blocker). The report
confirms each detection by hand against the expected finding, and counts rejected matches
separately.

**Configurations, staged.** This plan approves stage A only: Opus 5.5 at high effort, with a short
list of review questions and with the full checklist. Budget: at most 26 reviewer calls, failed
attempts and retries included: 11 cases (5 real misses, 4 planted defects, 2 clean cases) under both
prompts, the canary once with the short prompt, and its positive twin once (24 planned). The twin's
report goes through the publication check like any other, and only its verdict and counts enter a
committed record. Each case
runs under both prompts before the next case starts. A case without two completed reviews, for any
reason, is left out of the prompt comparison and listed as incomplete. The canary replaces the
separate confinement live check.

*Decision rule, committed with the answer key:* prefer the short prompt unless the full checklist
detects at least two more real misses with no more false blockers; a smaller difference is reported
as "no measurable difference". The union of both prompts' detections per case estimates what a
second reviewer would add.

*Quota estimate:* in the reviews of this plan, one Opus review at high effort used roughly 8 to 10
points of the 5-hour window and about 1 point of the weekly window (four parallel reviews moved them
from about 17% to 55% and from 6% to 10%, the author's own session included). Benchmark cases are
smaller, so stage A should need up to three 5-hour windows and about a quarter of a week's quota.
The report records the measured figures.

*Proposed for the user's decision once stage A is reported:* stage B compares Opus 5.5, Sonnet 5.5
and Codex as reviewers on the cases the author wrote (planted defects, and in slice 4 the stage
artifacts), with the better prompt from stage A; stage C repeats results that differed. A Codex
reviewer needs a backend the launcher does not yet have; stage B's plan amendment adds it only
after probing how Codex is kept from loading the copy's `AGENTS.md` and from reading outside the
copy.

**Report, `docs/slices/agentic-sdlc-poc/benchmark_report.md`.** Detection and false blockers per
configuration and prompt, real misses and planted defects separately; the canary and its twin;
quota per review; every run, failures and refused cases included; and a recommendation, for the
later slices, on the prompt, the number of reviewers and whether stages B and C are worth their
quota.

**Done when.** The tooling tests pass, one real review has completed through the launcher, stage A
has run within its budget with a valid canary, and the report is merged. **Still manual:** fix
rounds, moving between stages, checking review records.

## Slice 3 — Changed-files lint

- `make lint` runs `scripts/lint_changed_files.py` against the merge-base of `BASE_REF` and the
  change. For every file the change adds, modifies or renames, it runs ruff and shellcheck on the
  merge-base version and on the new version, and fails on every finding key that occurs more often
  in the new version. A key is the file, the rule and the enclosing function's qualified name (such
  as `Class.method`), or the line text for findings outside a function and for shellcheck; a
  function whose body, without its name, matches a function at the merge-base keeps that function's
  key, so a pure rename does not create a new one, while a function both renamed and changed counts
  as new. The
  change fails when a key is new, or when its value (the number in the message, such as the
  complexity) is higher than at the merge-base. So a new or worsened function fails; an unchanged or
  improved one does not. Renamed files are compared with their old path. Shell files are found by
  extension or by a shell shebang line, so extensionless scripts such as `varambu` are covered. A
  missing or unreadable base fails the run.
- Configuration, `ruff_changed_files.toml`, read from the merge-base when it exists there (so a
  change cannot loosen the limits it is checked against): ruff's default rules plus C901 (limit 10),
  PLR0912, PLR0913, PLR0915, the naming rules N without exceptions, and the security rules S, except
  S101 (`assert`) in `tests/`. The limit and naming rules and F401 and F841 run with
  `--ignore-noqa`; other rules honour a `noqa`, which reviewers see (the repository has one justified
  E402 `noqa` today). Plain `ruff check` keeps today's
  default rules, so the existing "ruff stays clean" standard stays true.
- The same script checks that every *added* file starts with a purpose comment: Python files with a
  module docstring (including private modules and `__init__.py`); shell, YAML, TOML, Dockerfile and
  Rego files with a comment as the first line after any shebang or YAML document marker. Tool
  directives (`# shellcheck`, `# -*-`, `# yaml-language-server`, `# noqa`, `# type:`) do not count.
  File types without comments (JSON) are skipped. The gate checks that the comment is there;
  reviewers check that it states the purpose.
- `requirements-dev.txt` pins `ruff` and `shellcheck-py`; CI currently installs neither.
- A CI job `lint` and a row in the `AGENTS.md` gates table naming ruff C901 as the complexity tool.
  The "not gated yet" standards for ruff and complexity move into that row, and the complexity debt
  list in `docs/STATUS.md` on the PoC branch is re-measured with ruff (12 functions, not radon's 16).
- *Required check and gate consistency.* The `basic` ruleset also protects `main`, which has no
  `lint` job: requiring `lint` there would block every `main` PR. The PoC branch has its own ruleset,
  `RULESET_URL` on the PoC branch points to it, and the gate-consistency wording changes from "the
  `main` ruleset" to "the integration branch's ruleset". The user adds `lint` to the PoC ruleset's
  required checks during the slice-3 PR, after its first `lint` run and before merging.

**Done when.** The tooling tests pass, and `lint` runs in CI and is a required check of the PoC
ruleset.

## Roadmap: slices 4–8 (outline, not approved by this plan)

Each slice gets its own grill-me, plan, test plan and review. The order follows POC-D14: rules,
then one real run by hand, then only the gates that run shows are needed, then automation.

| Slice | Delivers | Stages |
| --- | --- | --- |
| 4. Stage rules and checklists | The `AGENTS.md` slice workflow gains stages 2 to 7: what each produces, how it is reviewed, which checks run, and "none, with a reason" for stages that do not apply. One short review prompt per stage in the style the benchmark favours, and benchmark cases for stage artifacts (a flawed requirement, a weak test, a design gap) measured before any automation. The rules for keeping documents true (the close-out list, the final-review question, reopening after an upstream correction); the handoff format (POC-D12); how rule deviations are recorded; where the user's words live for the final review, and how its second pass receives the finding history through its prompt | 2–7 |
| 5. One real cycle by hand | One backlog item the user wrote or labelled (POC-D16) goes through stages 1 to 7 by hand, with the launcher for every review. Every miss is recorded as a delivery problem, and the quota of each stage is measured | 1–7 |
| 6. Gates the run shows | Only gates for misses that slice 5 or the benchmark actually showed. Candidates: a review-record check over the attempt log (every round has completed entries whose hashes match the reviewed revision; open blockers have the original reviewer's decision; extension and reset references are the user's comments); a test-first check that runs a change's new tests against the base code (they must fail for the recorded expected reason, not with an import error) and against the change (they must pass), in PR CI, which squash merges cannot erase. A review-record check needs the author's dispositions in a structured form as well as the log | 4, 6 |
| 7. Delivery loop | A thin `start`, `continue` and `status` script that runs stages 1 to 7 through the launcher, stops at the user's decisions and resumes from the branch and PR state. Its trust boundary is part of its plan: the tools and permission mode of author sessions, the credentials in their environment, merges, rulesets and credentials staying with the user, and backlog text treated as data. The orchestration requirements document starts here, and `qa-trace` learns to read it | 1–7, driven by agents |
| 8. Evaluation | One feature with planted defects run end to end, and the benchmark across all stages. Its result is a precondition for the isolation pilot (#17) and for the user's decision to merge the PoC into `main` | All |
| #21. Publication scanning | Secret scanning of new documents and PR text, with its own grill-me and plan; branches and PR comments are public as soon as they are pushed, so the plan covers scanning before a push and the delivery tools' own credential shapes. Suggested before slice 5, whose real cycle publishes the first agent-written records; the launcher's publication check is the stopgap until then. Issue #21's recorded review date, 2026-12-01, still applies | 7 |

## Earlier decisions D1–D59 (PR #26)

The closed PR #26 recorded 59 decisions from its grill-me session
([its plan at `af1017a`](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/blob/af1017a9de55c5fb892ab3dc7f548b75592248e9/docs/slices/delivery-orchestration/plan.md#grill-me-review-summary)).
They are not adopted as written; this table says where each one's intent lands.

| Area | #26 decisions | In this PoC |
| --- | --- | --- |
| Roles, reviewer independence, inputs, effort and usage | D1, D10, D28, D37, D43, D50, D59 | POC-D2, POC-D3, POC-D5; slice 2 (frozen copy without the review files, confinement, attempt log). D1's "different model from the author" is not kept as a rule: the benchmark compares Opus, Sonnet and Codex as reviewers before the default is chosen |
| Plan approval, stages, reopening after upstream changes, baseline protection | D2–D7, D23, D39 | POC-D1; Goal table; slice 4 (rules, including reopening after an upstream correction); slice 7 (loop). D4's "today's authoritative documents" holds for product requirements; orchestration requirements get their own document (user, 2026-11-05) |
| Review rounds, findings and dispositions | D11–D14, D24, D47 | POC-D4, POC-D5; slice 2 (attempt log, round admission with several reviewers per round, interrupted attempts, finding shape); slice 4 (only the user waives a blocker, D12; earlier escalation on a baseline conflict or no progress, D13); slice 6 candidate (review-record check) |
| Checklists, N/A answers, evidence in answers, specialist reviewers | D9, D18–D22, D41 | Slice 4, sized by the benchmark |
| Tests first, meaningful red, mutants, locked tests | D38 | Slice 4's stage-4 rules (interface skeletons so that red is meaningful, the expected failure recorded, targeted mutants on security paths); slice 6 candidate gate (new tests fail on the base, pass on the change); E2E red needs a running stack |
| Discovered issues, threat model, handoff, deviations | D15–D17, D25, D35 | POC-D12, POC-D13 (slice 1); handoff format and deviation records in slice 4 |
| Controller, authority, resume, one slice at a time, manual bootstrap, Docker ownership | D26, D27, D29, D31, D32, D34, D36, D52 | Slice 7, resuming from branch and PR state; slices 1–5 run by hand with the launcher |
| Author-side revision binding | D56 (authors) | POC-D15; slice 7 |
| CI results bound to the right base | D48 | The PoC ruleset's "Require branches to be up to date before merging" (user action) instead of a custom check |
| Revision binding for reviews | D56 (reviewers) | Slice 2 (frozen copy, hashes, attempt log) |
| Approval evidence | D49 | POC-D11; extension and reset references must be the user's PR comments (slice 2), checked in slice 6 if needed |
| Trial, seeds and verdict | D33, D40, D44–D46, D55 | Slice 5 (real cycle), slice 8 (evaluation on the PoC branch instead of a separate fixture branch); slice 8 precedes the decision to merge into `main` (D40). The attempt log records what each review read (D55) |
| Publication scanning | D51, D54, D58 | #21 in the roadmap; the launcher's publication check until then. D58's waiver existed only in #26 and was never approved |
| Deferred | D8 (comparison variants), D30 (eight-hour budget; usage-limit pauses instead), D42 (checkpoint files), D53 (trial reuse after record-only commits), D57 (except the same-cause search, which is POC-D5) | Only if slice 8 shows a need |

## Requirements

None added or changed (POC-D9). Product and service requirements are untouched.

## Success criteria

- After slice 1, `AGENTS.md` on the PoC branch states POC-D1 to POC-D8, POC-D11 to POC-D13 and
  POC-D15, no rule in it contradicts them, and only the user's approval satisfies the PoC branch's
  review rule.
- After slice 2, the exact invocation of any review can be rebuilt from its log entry; the log shows
  what each review read and which calls were denied; in the canary run, branch instructions and
  settings did not reach the reviewer while its positive twin shows they would have; and the report
  shows measured detection, false blockers and quota for each configuration.
- After slice 3, a PR into the PoC branch fails CI when it adds or worsens a violation in a file it
  touches, even with a `noqa` on a limit rule, and passes when the only violations are the unchanged
  existing ones.
- Slices 4–8 get their own success criteria in their plans; together they reach the Goal table.

## In scope

`AGENTS.md`, the two slice templates, `.github/CODEOWNERS`, the `Makefile` default `BASE_REF`, the
launcher, its attempt log, the benchmark and its report, the lint target and its CI job,
`requirements-dev.txt`, tooling tests, and the PoC branch's status and slice index. The roadmap and
the D1–D59 mapping are in scope as an outline only.

## Out of scope

Any change to `main`; services, compose files, images and keys; fixing existing lint violations or
refactoring over-limit functions; an orchestration controller or state machine; the design of
slices 4–8; the publication scanner (#21); taking backlog items the user did not write (#32).

## Assets and holders

No asset in `security/invariants.yaml` and no `REQ-SEC` holder changes. The Claude login store is
used by its CLI only; the launcher never reads, copies or logs it, never starts Codex, and passes
the reviewer only `PATH`, `HOME` and `LANG`. No secret can enter a review record or the report
because the reviewer sees only tracked files at the recorded commit and its prompt, is denied reads
outside its copy, a review that read outside it anyway is failed and not released, and the
launcher's publication check runs on every report and log entry before it is written.

## Environment facts

Probed on 2026-11-07 unless noted.

| Fact | Probe | Result |
| --- | --- | --- |
| Claude CLI flags | `claude --version`; `claude --help` | 2.1.319; `--safe-mode`, `--setting-sources`, `--settings`, `--effort`, `--json-schema`, `--tools`, `--permission-mode`, `--strict-mcp-config`, `--no-session-persistence` exist. The help says `--safe-mode` disables `CLAUDE.md`, hooks and other customizations, while "permissions work normally" |
| Reviewer read scope | Haiku, headless, inside a scratch copy, asked to Read, Grep and Glob a marker file outside the copy | With `--allowedTools Read,Grep,Glob`: the outside marker was read. Without allow rules, `dontAsk`: all three tools denied outside, worked inside. The first round of revision 1 ran with the allow rules; its 31 tool calls all stayed inside its copy |
| What `--safe-mode` loads | Haiku, headless, in a copy with marker instructions in `CLAUDE.md` (importing `AGENTS.md`) and in a nested `CLAUDE.md`, and a `.claude/settings.json` with an allow rule for an outside file and a startup hook writing outside the copy; runs with and without `--safe-mode` and `--setting-sources user` | Without either flag: all three markers followed and the hook ran. With `--safe-mode`, with `--setting-sources user`, or with both: no marker followed, the hook did not run. The project allow rule did not open the outside file in any run. The init event does not list loaded instruction files. The effect of `--setting-sources ""` on user-level settings was not probed, to leave the user's settings untouched |
| Usage is readable | `claude -p` (Haiku) with `--output-format stream-json --verbose` | A `rate_limit_event` gives `five_hour` and `seven_day` utilization, status and reset time; only the status "allowed" has been observed |
| Codex CLI | `codex --version`; `codex exec --help` | 0.165.0, for scoped implementation only (POC-D2), and possibly a benchmark reviewer in stage B. Login and instruction loading not probed; probe before first use |
| Lint tools | `ruff`, `radon` versions | ruff 0.15.18, radon 6.0.1. `shellcheck` is not installed; `requirements-dev.txt` has neither ruff nor shellcheck |
| Lint baseline | `ruff check --select C901,PLR0912,PLR0913,PLR0915,D100,N` on `services`, `scripts`, `tests` | 81: 32 D100, 16 N802 (truth-table test names such as `test_intent_TTTT`), 12 C901, 10 PLR0913, 8 PLR0912, 3 PLR0915. Default rules: clean. Radon counts 16 functions over complexity 10 |
| Secret check | `scripts/evidence_secrets.py` | Offers `scan_text(text, path)`, returning findings without values |
| Tracked symlinks | `git ls-files -s` | None today |
| Python versions | `python3 --version`; `.github/actions/setup-python-deps` | Host 3.10.12, CI 3.11: new tooling must run on both |
| CI triggers | `.github/workflows/ci.yml` | `pull_request` has no branch filter, so PRs into the PoC branch run every check; `push` runs only for `main` |
| PoC branch protection | Rulesets API; `GET /rules/branches/<branch>` | A separate ruleset targets exactly `poc/agentic-sdlc`: one approval with code-owner review, squash merges only, the 11 required checks (the up-to-date requirement is off; stale approvals are not dismissed on push), no deletion or force-push. The rules API shows it on `poc/agentic-sdlc` and no rules on `poc/plan-slices-1-3`. Earlier targets `refs/heads/poc/` (matched nothing) and `refs/heads/poc/*` (also caught slice branches) were replaced |
| Approval rule | `basic` ruleset rules | One approving review from any collaborator with write access satisfies it; POC-D11 limits this to the user on the PoC branch |
| Benchmark commits | `git log`; `git grep` for each defect's ID and key terms in `docs/` | `07520d7` and `7226c2e` exist and their docs name nothing; `4b808cb` exists and one docs file matches. This probe searched `docs/` only; the runner searches each case's whole copy, rules and task |
| Review quota | Usage events of this plan's reviews | One Opus review at high effort: roughly 8 to 10 points of the 5-hour window, about 1 point of the weekly window |
| Deployment check | `scripts/qa_deploy.py` with image users inspected | Passes (18 known violations, 22 grandfathered warnings); the OPA failure reported in PR #26 does not reproduce here |
| Test stack | `docker ps` working-directory labels | All `spiffe-*` containers belong to this checkout; every service has a fixed `container_name`, so only one stack can run per host |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Review attempt log | `docs/slices/<id>/review_attempts.jsonl`, committed | Launcher only, append-only | Launcher, user, a slice-6 gate if built | One review unit, across revisions | Round admission; rebuilding an invocation; what a review read | Authoritative for round counts; extension and reset references are advisory until checked against the user's comments |
| Usage-limit utilization | Provider stream, copied into the log | Provider | Launcher, then author | Per call | Pause until the reset; the author's choice of Codex for scoped implementation | Advisory, operational |
| Benchmark answer key and decision rule | `tests/review_benchmark/` | Author, before any run | Runner | Fixed per benchmark version | Scores detection; chooses the prompt | Authoritative for scoring; SHA-256 in the report; absent from every case commit |
| Frozen review copy | Scratch directory per review | Launcher | Reviewer | Deleted after the review | The reviewer sees only these files | Advisory; tracked files at the recorded commit, minus the withheld review files |

## Authored source changes

- Requirements and architecture: none (POC-D9; no runtime component changes).
- Proof: tooling tests in `tests/tools/` and the live checks in the test plan; slice 1 is proved by
  review and its done-when checks.
- Rulebook: slice 1 as listed above; slice 3 adds the `lint` gate row and the gate-consistency
  wording.

## Checks this plan adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Launcher round admission from its own log | An extra, restarted or unrecorded review round (the #25 problem); a reviewer with open blockers left out of a recheck; a running attempt taken for a dead one | One append-only file and one lock per review unit | Parsing the author's markdown record: misses unrecorded reruns and cannot express resets |
| Withheld review files | A first-pass reviewer anchored on earlier verdicts and the author's answers | Two excluded paths per review | Instruction only |
| Launcher output-shape, empty-review and outside-read checks | A malformed, empty or blind review read as a pass; a review that read outside its copy, whatever settings were loaded | One schema; a count of paths read; a path check | Reading free text; cannot be scored |
| Launcher publication check | A secret of the evidence shapes in a reviewer's report or log entry reaching a public record | One call to the existing scanner | Waiting for #21 |
| `make lint` on changed files | New or worsened code above the limits, insecure patterns, shell errors, missing purpose headers, limits silenced by `noqa` or by a loosened config | One script, one CI job, seconds per PR | diff-quality on changed lines: misses functions made worse; whole-tree lint: fails on 81 existing violations |
| Code-owner review on the PoC branch | Another collaborator's approval taken as the user's | One file and one ruleset setting | Instruction only (the state before) |
| Ruff security rules (S) | Insecure patterns in new code (`shell=True`, unsafe YAML loading, hard-coded passwords) | Occasional false positives, answered with a justified `noqa` | Reviewer judgment only |

The roadmap's gates (slice 6) answer these questions in their own plan, from evidence of slice 5.

## Retirement and compatibility

- Slice 1 retires the Codex-first reviewer rule, "There is no round limit", and `origin/main` as the
  PoC's implementation base.
- Slice 3 retires the "not gated yet" ruff and radon complexity standards in favour of the `lint`
  row.
- PR #26 is closed and not adopted. Its decisions are mapped above; its review-usage drafts are not
  reused, and the launcher is written fresh against this plan.
- `main` keeps its current `AGENTS.md` and `STATUS.md` until the PoC is merged; the PoC branch's
  status page and slice index are updated as each slice closes.
- Nothing else is retired.

## Review notes

The user answered the four questions of the first review of revision 1 on 2026-11-07 (R1-D1 to
R1-D4, recorded in `plan_review.md` and in POC-D2, POC-D4, POC-D10 and POC-D11).

For revision 2 the user reset the review budget (POC-D4) and asked for the roadmap to be challenged
from different aspects; its rounds use four reviewers with different lenses. That is for this
roadmap's challenge: routine reviews use one reviewer until the benchmark and slice 5 show otherwise.
The attempt log is new committed process; it replaces parsing the review record and is approved
with this plan (POC-D6 table). The launcher behaviour in this plan is frozen for slice 2's
implementation: anything further waits for evidence from the benchmark or slice 5 and the user's
approval (POC-D6). The user then
answered four direction questions on 2026-11-07: real run first, gates after (POC-D14); intake only
from the user, with #32 for more (POC-D16); test Opus, Sonnet and Codex as reviewers (POC-D2, stage
B); resets only by the user (POC-D4).

Defaults chosen by the author, for the user to confirm or change in the PR: the branch and file
names above; Opus 5.5 as the default reviewer until the benchmark says otherwise; the benchmark's
exact budget (26 calls) and case counts; the report's location in this bundle; the file types that
need a header; ruff's security rules; the roadmap's order, including #21 before slice 5.

User actions:
1. Done on 2026-11-07: the ruleset `poc/agentic-sdlc` targets exactly that branch, with code-owner
   review. Left over: remove the `refs/heads/poc/` entry from `basic`; on the PoC ruleset, turn on
   "Require branches to be up to date before merging" (D48 relies on it), "Dismiss stale pull
   request approvals when new commits are pushed" and "Require approval of the most recent
   reviewable push", so that an approval covers the commit that is merged.
2. During the slice-3 PR, add `lint` to the PoC ruleset's required checks.
