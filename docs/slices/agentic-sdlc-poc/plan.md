# Slice Plan — agentic-sdlc-poc, slices 1–3

Status: draft, 2026-11-07, revised after review rounds 1 to 3. Approved when the user merges this plan's PR
into `poc/agentic-sdlc`. Tracks [#16](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/16)
and [#25](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/25). Supersedes the
closed PR #26, whose plan is not adopted; its history stays on the branch `plan/delivery-orchestration`.

**Interim exception, until slice 1 merges:** the user's instruction of 2026-11-07 (keep PoC work on
`poc/agentic-sdlc`, merge by PR with the user's approval) overrides the `AGENTS.md` rules "Open pull
requests against `main`" and "implement only from the plan as merged on `origin/main`" for this
PoC. It expires when slice 1 puts the integration-branch rule into `AGENTS.md`.

## Goal

The PoC's end goal is a complete software delivery cycle run by Claude agents: reliable, without
stale code or docs, and with code that is maintainable, secure and easy to understand. Five slices
get there. This plan approves the first three:

1. **Rules.** `AGENTS.md` says how agent work is reviewed, limited and fixed in the PoC.
2. **Review launcher and benchmark.** A repeatable independent review, and measurements of how well
   it finds real defects in this repository.
3. **Changed-files lint.** Deterministic size, complexity, naming, security and header limits for
   new and changed code; existing violations are left as they are.

Slices 4 (a check of review records) and 5 (a delivery loop used on a real backlog item) are outlined
at the end. They are planned after the benchmark report, because its results decide their shape.

## Threat model

- **Delivery** (the [PoC scope](../../../AGENTS.md#poc-scope-and-proportion)): agents make honest
  mistakes. For this change that means, for example, a launcher that silently loads the branch's own
  rules or lets the reviewer read outside its copy, a benchmark scored loosely enough to flatter the
  reviewer, a lint gate that misses new or worsened code, or a document left saying something that
  is no longer true. Deliberate attacks on CI, the gates or the evidence stay out of scope
  ([OPL-009](../../open_problem_log.md)).
- **System under test:** unchanged. No service, compose file, image or key holder changes. The
  benchmark reads source at fixed commits and changes nothing.

## Grill-Me Review Summary

The design was settled in the conversation of 2026-11-05 to 2026-11-07. Decisions carry the prefix
`POC-` so they cannot be confused with other slices' decision IDs
([#27](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/27)).

| ID | Decision | Source |
| --- | --- | --- |
| POC-D1 | PoC work happens on `poc/agentic-sdlc`. Each slice uses a branch `poc/slice-<n>-<topic>` and merges back by PR with the user's approval. `main` is not changed until the user decides. | user, 2026-11-07 |
| POC-D2 | Claude models only. Codex is used only for scoped implementation, and only while Claude's 5-hour or weekly usage is above 70%. Reviews always run on Claude; when a usage limit is reached, work pauses until it resets. | user, 2026-11-07 (Codex for implementation only: answer to R1-D1) |
| POC-D3 | The reviewer is never the author: a fresh headless Claude session confined to a frozen copy of the repository, which does not load the branch's instruction files and receives the approved `AGENTS.md` from the PR's base branch. Effort is always explicit: medium for routine focused reviews and rechecks; high for initial plan, security, architecture and integrated reviews. | user (effort); default (how independence is achieved) |
| POC-D4 | Review limit per review unit (a plan and its test plan are one unit): round 1 is the initial review, and at most three fix rounds follow (rounds 2 to 4). After round 4, open blockers go to the user, and only the user can allow more rounds. | user, 2026-11-05 and 2026-11-07 (answer to R1-D2) |
| POC-D5 | The author may reject a finding with a reason the reviewer can check; the original reviewer (the same model and review role, in a fresh session given its own earlier report and the author's answers) accepts the rejection or raises it again. A fix goes to the origin of the problem, and the author searches for the same cause elsewhere and says where it looked ([DPL-007](../../delivery_problem_log.md)). | user, 2026-11-07 |
| POC-D6 | Every new check or process step states the failure it catches, what it costs and the simpler alternative that was considered. The user approves each addition. | user, 2026-11-07 |
| POC-D7 | Every new file starts with a comment that says what the file is for (in Python, the module docstring). Names say what a file, function or component does. | user, 2026-11-07 |
| POC-D8 | Deterministic tools before judgment. Lint limits: cyclomatic complexity at most 10, at most 50 statements, 12 branches and 5 arguments per function, the standard naming conventions without exceptions, and ruff's security rules. They apply to new and changed files; a change fails only on violations it adds or worsens, so existing violations stay. | user (limits, changed code only); default (security rules, no naming exceptions) |
| POC-D9 | Orchestration requirements stay separate from product requirements. Slices 1–3 add none: like the existing QA gates, the launcher and the lint gate are specified by `AGENTS.md` and this plan and proved by tooling tests. The orchestration requirements document starts with slice 4. | user (separate); default (timing) |
| POC-D10 | Measure before automating. The launcher, the benchmark and its report merge into the PoC branch, because slices 4 and 5 build on them. The benchmark's first stage is limited to the user's "about 24" reviews (26 reviewer calls, see Configurations); further stages need the user's decision on its results. | user (benchmark first; budget: answer to R1-D3); default (merge to the PoC branch) |
| POC-D11 | Only the user's approval counts on PRs into `poc/agentic-sdlc`: a `CODEOWNERS` file names the user, and the PoC ruleset requires a code-owner review. | user, 2026-11-07 (answer to R1-D4) |

## Slice 1 — Rules (text only)

**Outcome.** `AGENTS.md`, the two slice templates and a new `.github/CODEOWNERS` on the PoC branch
express POC-D1 to POC-D8 and POC-D11:

- *PoC scope and proportion:* "Ask before growing" gains the three questions of POC-D6.
- *Review loop:* "There is no round limit" becomes POC-D4, with round 1 as the initial review, so
  that "from round 2 a new finding counts only if it blocks" keeps its meaning. Rejecting with a
  checkable reason stays. Fixing at the origin and searching for the same cause (POC-D5) is added,
  with the definition of "original reviewer".
- *Independent review → Reviewer:* the Codex-first rule is replaced by POC-D3 and POC-D2. Until the
  slice 2 launcher exists, the exact review command is recorded in the slice's review record.
- *Git rules:* PRs target the integration branch: `main`, or `poc/agentic-sdlc` for PoC work
  (POC-D1). The stacking check of DPL-008 applies to that branch. Local gate runs on PoC work use
  `BASE_REF=origin/poc/agentic-sdlc`. This ends the interim exception above.
- *Coding rules:* a new rule 8 for POC-D7.
- *Templates:* `_template/test_plan.md` no longer names Codex as the default reviewer;
  `_template/plan.md` asks the POC-D6 questions for every check the slice adds.
- *Code owner (POC-D11):* `.github/CODEOWNERS` with a purpose comment and `* @gunaseelan-sivanandam`;
  the Git rules say that approvals are enforced this way. GitHub reads `CODEOWNERS` from the PR's
  base branch, so the rule applies from the first PR after slice 1 merges.

**Done when.** A fresh Claude session has reviewed the change under the `AGENTS.md` of the base
branch, the PR's CI checks pass, GitHub's rules for `poc/agentic-sdlc` show a required code-owner
review, and the user has merged it. **Still manual:** everything else.

## Slice 2 — Review launcher and benchmark

**Launcher, `scripts/run_independent_review.py`.**
- *Frozen copy.* It fetches the base branch, records its commit, and copies the *whole tracked tree*
  at the reviewed commit into a scratch directory with `git archive`. The task names the paths to
  review; the reviewer may read anything in the copy, as `AGENTS.md` allows. Untracked files
  (`capiss_keys/`, `.env`, SPIRE data) cannot enter the copy. The launcher records the SHA-256 of
  every file.
- *Confinement.* The reviewer runs inside the copy with only Read, Grep and Glob, `--safe-mode`,
  `--permission-mode dontAsk`, no MCP servers, no saved session, and **no** `--allowedTools` rules.
  The 2026-11-07 probe (Environment facts) shows that blanket allow rules let Read reach any path,
  while without them reads outside the working directory are denied. This is CLI configuration,
  not an operating-system boundary.
- *Approved rules.* `AGENTS.md` and `tests/unit/AGENTS.md` are read from the recorded base commit
  and passed as explicit instructions; `--safe-mode` stops the CLI from loading `CLAUDE.md`,
  `AGENTS.md` or project settings from disk.
- *Inputs.* Required arguments: the commit, the base branch, the prompt file (intent and task), the
  model, the effort, the review record and the round number. The prompt is stored verbatim in the
  slice's review record, as `AGENTS.md` requires.
- *Round admission.* The launcher reads the review record and refuses the round unless the record's
  last completed round is exactly one less. A missing or unreadable record is refused for any round
  after the first. A round beyond the POC-D4 limit runs only with an argument naming where the user
  allowed it (a PR comment or the review record), and the record keeps that reference. Round
  admission belongs to the launcher's command-line entry, which serves review units. The benchmark
  runner calls the same review function without a review record: benchmark runs are not review
  units and never read or write one.
- *Findings.* A fixed JSON shape via `--json-schema`: id, severity (blocking or advisory), file,
  line, problem, evidence and failure scenario. Output that does not match the shape is a failed
  review, never an empty pass, and it is not retried automatically.
- *Record.* Per attempt, failures included: reviewed commit, base commit, SHA-256 of the rules, the
  prompt and every reviewed file, model, effort, duration, turns, tokens, cost estimate, exit
  status, and the 5-hour and weekly utilization from the stream's `rate_limit_event`; for a review
  unit also the round number and any user-extension reference, for a benchmark run the case and
  configuration. No prompt or reply text. From a record, the launcher's invocation builder recreates
  the exact CLI call and input hashes; there is no separate rerun mode.
- *Usage limits.* Reviews run on Claude only (POC-D2); the launcher has no other backend. It records
  the utilization from every call, so the author can apply the 70% rule to implementation work.
  When a window's status is not "allowed", the launcher exits with status "paused until <reset
  time>"; a paused attempt completes no round, so the same round runs again after the reset. Provider or CLI errors are retried at most twice; after that the
  review is "pending".

**Benchmark, `tests/review_benchmark/`.** Each case names a commit, the paths to review, the
reviewer's task, the expected findings (file, line range, and a few terms a correct finding must
use) and its leak terms: the problem ID and words that would describe the defect. Before each
case's review, the runner searches the case's whole frozen copy for them and refuses the case on
any match. Expected findings are committed before any run, and the report records their SHA-256.
No case commit contains `tests/review_benchmark/`.

| Kind | Cases | What it measures |
| --- | --- | --- |
| Real misses | DPL-001, DPL-002, DPL-004, DPL-009 and the in-repository half of DPL-005 (gates hidden inside another CI job), each at a commit where the defect exists and no tracked file names it. Candidates: `07520d7` (DPL-001), `7226c2e` (DPL-002), `4b808cb` (DPL-009, its docs need the check) | Defects that got past earlier reviews; nobody planted them |
| Planted defects | A weakened assertion, an outcome guard with `\|\| true`, a key mounted into a non-holder, a changed expected value, applied on top of `e842e97` | Defect types without a real example, and security findings without a published description |
| Clean cases | Two merged changes with no known defect | False blockers |
| Canary | Harmless, recognisable instructions planted in the copy's `AGENTS.md`, `CLAUDE.md`, a nested `CLAUDE.md`, `.claude/settings.json` and `tests/unit/AGENTS.md` | Whether the reviewer obeys branch instructions instead of the approved ones |

Open problems that are already described in the tree (OPL-005 to OPL-008) are not cases: their
answers are in the logs a reviewer may read.

**Runner, `scripts/run_review_benchmark.py`.** Runs cases against configurations through the
launcher and stops when the approved number of reviews is reached (POC-D10). Scoring is deterministic
first: an expected finding counts as *detected* when a blocking finding names the same file, a line
inside the expected range, and at least one of the expected terms. A location match without any
expected term goes to triage. Every blocking finding that matches no expected finding is also
listed for triage (a real extra defect or a false blocker). The report confirms each detection by
hand against the expected finding, and counts rejected matches separately.

**Configurations, staged.** This plan approves stage A only: Opus 5.5 at high effort, with a short
list of review questions and with the full checklist. Budget: at most 26 reviewer calls, failed
attempts and retries included, for 11 cases (5 real misses, 4 planted defects, 2 clean cases) under
both prompts and the canary once with the short prompt. Each case runs under both prompts before
the next case starts. If the cap falls in the middle of a pair (retries count), the report leaves
that case out of the prompt comparison and lists it as incomplete. The benchmark's canary case is
the slice's canary check; the other live checks are outside this budget. Proposed for
the user's decision once stage A is reported: stage B (Sonnet 5.5 at high effort and Opus 5.5 at
medium effort, with the better prompt from stage A) and stage C (repeats of results that differed).

**Report, `docs/slices/agentic-sdlc-poc/benchmark_report.md`.** Detection and false blockers per
configuration and prompt; the canary result; usage per review; every run, failures included; and a
recommendation, for the slices 4–5 plan, on the prompt and on whether stages B and C are worth
their quota.

**Done when.** The tooling tests pass, the live checks pass, stage A has run within its budget, and
the report is merged. **Still manual:** fix rounds, moving between stages, checking
review records.

## Slice 3 — Changed-files lint

- `make lint` runs `scripts/lint_changed_files.py` against `BASE_REF`. For every file the change
  adds, modifies or renames, it runs ruff (with `ruff_changed_files.toml`) and shellcheck on the
  base version and on the new version, and fails on every (file, rule, message) that occurs more
  often in the new version. Ruff's complexity message includes the complexity value, so a function
  made worse fails as well as a new one; unchanged existing violations do not. Renamed files are
  compared with their old path. Shell files are found by extension or by a shell shebang line, so
  extensionless scripts such as `varambu` are covered. A missing or unreadable base fails the run.
- `ruff_changed_files.toml` extends ruff's default rules with C901 (limit 10), PLR0912, PLR0913,
  PLR0915, the naming rules N without exceptions, and the security rules S, except S101 (`assert`)
  in `tests/`. Plain `ruff check` keeps today's default rules, so the existing "ruff stays clean"
  standard stays true.
- The same script checks that every *added* file starts with a purpose comment: Python files with a
  module docstring (including private modules and `__init__.py`); shell, YAML, TOML, Dockerfile and
  Rego files with a comment as the first line after any shebang. File types without comments (JSON)
  are skipped.
- `requirements-dev.txt` pins `ruff` and `shellcheck-py`; CI currently installs neither.
- A CI job `lint` and a row in the `AGENTS.md` gates table naming ruff C901 as the complexity tool.
  The "not gated yet" standards for ruff and complexity move into that row, and the complexity debt
  list in `docs/STATUS.md` on the PoC branch is re-measured with ruff (12 functions, not radon's 16).
- *Required check and gate consistency.* The `basic` ruleset also protects `main`, which has no
  `lint` job: requiring `lint` there would block every `main` PR. The PoC branch therefore has its
  own ruleset (user action), `RULESET_URL` on the PoC branch points to it, and the gate-consistency
  wording changes from "the `main` ruleset" to "the integration branch's ruleset". The user adds
  `lint` to the PoC ruleset's required checks during the slice-3 PR, after its first `lint` run and
  before merging.

**Done when.** The tooling tests below pass, `lint` runs in CI and is a required check of the PoC
ruleset.

## Slices 4–5 (outline, not approved by this plan)

- **4 — Review-record check.** A deterministic check that fails a PR when a blocker has no decision
  from the reviewer who raised it, the rounds exceed the limit, the reviewer was the author's own
  session, or the reviewed hashes don't match the change.
- **5 — Delivery loop.** Author, review, fix, re-review and a PR, with a one-label Docker ownership
  check, used on a real backlog item (#21, #27 or #30).

## Requirements

None added or changed (POC-D9). Product and service requirements are untouched.

## Success criteria

- After slice 1, `AGENTS.md` on the PoC branch states POC-D1 to POC-D8 and POC-D11, no rule in it
  contradicts them, and only the user's approval satisfies the PoC branch's review rule.
- After slice 2, the exact invocation of any review can be rebuilt from its record (same commit,
  base, rules, prompt, model and effort), the reviewer cannot read outside its copy or follow branch instructions, and the report
  shows measured detection, false blockers and usage for each configuration.
- After slice 3, a PR into the PoC branch fails CI when it adds or worsens a violation in a file it
  touches, and passes when the only violations are the unchanged existing ones.

## In scope

`AGENTS.md`, the two slice templates, `.github/CODEOWNERS`, the launcher, the benchmark and its
report, the lint target and its CI job, `requirements-dev.txt`, tooling tests, and the PoC branch's
status and slice index.

## Out of scope

Any change to `main`; services, compose files, images and keys; fixing existing lint violations or
refactoring over-limit functions; an orchestration controller or state machine; the details of
slices 4 and 5; the publication scanner (#21).

## Assets and holders

No asset in `security/invariants.yaml` and no `REQ-SEC` holder changes. The Claude login store is
used by its CLI only; the launcher never reads, copies or logs it, and never starts Codex. The reviewer's
copy holds tracked files only, and the reviewer is denied reads outside it (Environment facts).
Records hold metadata and hashes, and the verbatim prompt the author wrote, so no secret enters a
review record or the report.

## Environment facts

Probed on 2026-11-07 unless noted.

| Fact | Probe | Result |
| --- | --- | --- |
| Claude CLI flags | `claude --version`; `claude --help` | 2.1.319; `--safe-mode`, `--effort`, `--json-schema`, `--tools`, `--permission-mode`, `--strict-mcp-config`, `--no-session-persistence` exist |
| Reviewer read scope | Haiku, headless, inside a scratch copy, asked to Read, Grep and Glob a marker file outside the copy | With `--allowedTools Read,Grep,Glob`: the outside marker was read. Without allow rules, `dontAsk`: all three tools denied outside, worked inside. The round-1 plan review ran with the allow rules; its 31 tool calls all stayed inside its copy |
| Usage is readable | One `claude -p` call (Haiku) with `--output-format stream-json --verbose` | A `rate_limit_event` gives `five_hour` and `seven_day` utilization (0.11 and 0.01), status and reset time |
| Codex CLI | `codex --version`; `codex exec --help` | 0.165.0, for scoped implementation only (POC-D2). Login not probed this week; probe before its first use |
| Lint tools | `ruff`, `radon` versions | ruff 0.15.18, radon 6.0.1. `shellcheck` is not installed; `requirements-dev.txt` has neither ruff nor shellcheck |
| Lint baseline | `ruff check --select C901,PLR0912,PLR0913,PLR0915,D100,N` on `services`, `scripts`, `tests` | 81: 32 D100, 16 N802 (truth-table test names such as `test_intent_TTTT`), 12 C901, 10 PLR0913, 8 PLR0912, 3 PLR0915. Default rules: clean. Radon counts 16 functions over complexity 10 |
| Python versions | `python3 --version`; `.github/actions/setup-python-deps` | Host 3.10.12, CI 3.11: new tooling must run on both |
| CI triggers | `.github/workflows/ci.yml` | `pull_request` has no branch filter, so PRs into the PoC branch run every check; `push` runs only for `main` |
| PoC branch protection | Rulesets API; `GET /rules/branches/poc/agentic-sdlc` | `basic` lists `refs/heads/main` and `refs/heads/poc/`. GitHub applies **no** rule to `poc/agentic-sdlc`: the entry is taken literally. A pattern such as `poc/**` would also block pushes to slice branches, so the target must be exactly `poc/agentic-sdlc` |
| Approval rule | `basic` ruleset rules | One approving review from any collaborator with write access satisfies it; POC-D11 limits this to the user on the PoC branch |
| Benchmark commits | `git log`; `git grep` for each defect's ID and key terms in `docs/` | `07520d7` and `7226c2e` exist and their docs name nothing; `4b808cb` exists and one docs file matches. This probe searched `docs/` only; the runner searches each case's whole copy |
| Deployment check | `scripts/qa_deploy.py` with image users inspected | Passes (18 known violations, 22 grandfathered warnings); the OPA failure reported in PR #26 does not reproduce here |
| Test stack | `docker ps` working-directory labels | All `spiffe-*` containers belong to this checkout; every service has a fixed `container_name`, so only one stack can run per host |

## Hidden-state and trust decisions

| State | Store | Writer | Reader | Lifecycle | Decision impact | Authority |
| --- | --- | --- | --- | --- | --- | --- |
| Review rounds | The slice's review record, on the slice branch | Author | Launcher, reviewer, user | One review unit | Launcher admits or refuses a round | Advisory until slice 4 checks it; the user's merge decides |
| Review attempt record | JSON per attempt, summarised in the review record or report | Launcher | Author, user | Per attempt | Rebuilding the invocation; applying POC-D2 | Advisory |
| Usage-limit utilization | Provider stream | Provider | Launcher, then author | Per call | Pause until the reset; the author's choice of Codex for scoped implementation | Advisory, operational |
| Benchmark answer key | `tests/review_benchmark/` | Author, before any run | Runner | Fixed per benchmark version | Scores detection | Authoritative for scoring; SHA-256 in the report; absent from every case commit |
| Frozen review copy | Scratch directory per review | Launcher | Reviewer | Deleted after the review | The reviewer sees only these files | Advisory; tracked files at the recorded commit |

## Authored source changes

- Requirements and architecture: none (POC-D9; no runtime component changes).
- Proof: tooling tests in `tests/tools/` and the live checks in the test plan; slice 1 is proved by
  review.
- Rulebook: slice 1 as listed above; slice 3 adds the `lint` gate row and the gate-consistency
  wording.

## Checks this plan adds (POC-D6)

| Check | Failure it catches | Cost | Simpler alternative considered |
| --- | --- | --- | --- |
| Launcher round admission | An extra or restarted review round started by mistake (the #25 problem) | A few lines in the launcher | Instruction only; it already failed once |
| Launcher output-shape check | A malformed or empty review read as a pass | One schema | Reading free text; cannot be scored |
| `make lint` on changed files | New or worsened code above the limits, insecure patterns, shell errors, missing purpose headers | One script, one CI job, seconds per PR | diff-quality on changed lines: misses functions made worse; whole-tree lint: fails on 81 existing violations |
| Code-owner review on the PoC branch | Another collaborator's approval taken as the user's | One file and one ruleset setting | Instruction only (the state before) |
| Ruff security rules (S) | Insecure patterns in new code (`shell=True`, unsafe YAML loading, hard-coded passwords) | Occasional false positives, answered with a justified `noqa` | Reviewer judgment only |

## Retirement and compatibility

- Slice 1 retires the Codex-first reviewer rule and "There is no round limit".
- Slice 3 retires the "not gated yet" ruff and radon complexity standards in favour of the `lint`
  row.
- PR #26 is closed and not adopted. Its review-usage drafts are not reused; the launcher is written
  fresh against this plan.
- `main` keeps its current `AGENTS.md` and `STATUS.md` until the PoC is merged; the PoC branch's
  status page and slice index are updated as each slice closes.
- Nothing else is retired.

## Review notes

The user answered the four questions of review round 1 on 2026-11-07 (R1-D1 to R1-D4, recorded in
`plan_review.md` and in POC-D2, POC-D4, POC-D10 and POC-D11).

Defaults chosen by the author, for the user to confirm or change in the PR: the branch and file
names above; Opus 5.5 as the default reviewer until the benchmark says otherwise; the benchmark's
exact budget (26 calls) and case counts; the report's location in this bundle; the file types that need a header; ruff's security rules; a separate
ruleset for the PoC branch.

User actions:
1. Create a ruleset targeting exactly `poc/agentic-sdlc` with the same rules as `basic`, plus
   "Require review from Code Owners", and remove the `refs/heads/poc/` entry from `basic`.
2. During the slice-3 PR, add `lint` to that ruleset's required checks.
