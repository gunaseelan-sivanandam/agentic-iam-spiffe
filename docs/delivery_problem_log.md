# Delivery Problem Log

Purpose:
- Track misses in how we deliver: a step skipped, a false claim, a review that missed something, a
  check that did not exist. Runtime and trust problems of the system under test belong in
  [`open_problem_log.md`](open_problem_log.md); one miss can have an entry in each.
- Keep the lessons where future agents read them, so a miss is not repeated slice after slice.

Usage:
- Add one entry per distinct miss, with the next free `DPL-NNN`. Never reuse or delete an ID.
- State what happened with evidence (commits, PRs, runs), not impressions.
- Root causes say why it happened and why it was not caught; one cause per line.
- Corrective actions fix this instance. Preventive actions change a rule in
  [`AGENTS.md`](../AGENTS.md), a template, a reviewer prompt or a gate, so the miss cannot recur
  unnoticed; each names where it lives.
- An entry is closed only when its preventive actions are merged; until then it stays open and
  names what is pending.

## DPL-001: The capiss key directory was mounted into services that only need the public key

- Status: Closed (preventive action merged in PR #6); the runtime problem stays open as
  [OPL-005](open_problem_log.md#opl-005-capiss-root-signing-key-is-readable-by-verifiers-and-by-the-rogue-test-container)
- Introduced: `07520d7` (2026-01-05, M3 steps 3–4), copied in `4b808cb` (2026-03-03), `16072e0`
  (2026-05-15), `1b84bc4` (2026-05-16)
- Found: 2026-10-27, during the agentic-delivery-process planning (OPL-005)

### What happened
- `tool-b` needed the capiss public key to verify tokens. The whole directory `capiss_keys/`, which
  holds both the private and the public key, was mounted into it.
- Each later change copied the same mount line: into `agent-a` and `rogue` (which read nothing from
  it), `jira-tool` and `jira-mcp-gateway`.
- All containers run as root, so the key file's mode `0600` protects nothing. A forged capability
  was confirmed on the running stack on 2026-10-28.

### Root causes
- One directory mixes the private and the public key and is mounted whole.
- A mount line was copied to each new service without asking what that service needs.
- Nothing checked which service can see which key; the archived security model claimed "the private
  key never leaves the issuer container" and nobody tested the claim.

### Actions
- Corrective: OPL-005 is open, with a known-violation row in `security/invariants.yaml` that expires
  on 2026-12-31.
- Preventive: `security/invariants.yaml`, the `REQ-SEC` requirements and `make qa-deploy` (slice 1B,
  PR #6): every protected asset may reach only its holders, checked on every PR.

### Lesson
Mount the narrowest thing a service needs, and keep a checked list of who may hold each secret.

## DPL-002: Capability token values were written into E2E evidence

- Status: Closed (preventive action merged with slice `ci-evidence-trace` Increment A); the
  requirement REQ-T-R9 and its static test follow in Increment B
- Introduced: `7226c2e` (2026-01-20, premise, exercise and outcome guards for M1 and M2), then
  copied into M3, M4, M4b and M5 tests
- Found: 2026-10-30, during the slice 2 CI trial

### What happened
- Outcome guards save the minted token as proof: `echo "$token" > "$EVDIR/token.txt"`, also
  `token1.txt`, `token2.txt`, `create_token.txt`, `read_token.txt`, `tampered_token.txt` and the
  `token` field of saved mint JSON. No later step reads them back.
- This breaks coding rule 1 in `AGENTS.md` and the evidence clauses of `REQ-M4B-W8` and
  `REQ-M5-CJ2`, whose E2E tests pass anyway (a false green).
- The CI trial uploaded the evidence as public artifacts (runs `40999541906`, `41000278717`). The
  tokens in it had expired (TTL ≤ 120 s); the artifacts were left to expire.

### Root causes
- A guard proved "a token was minted" by keeping the token, not a fingerprint of it.
- No check scanned the evidence for secrets; the tests of the no-secret requirements check named
  outputs (MCP responses, adapter logs, audit events, as in `M5-T26` and `M5-T27`), never the
  evidence directory itself.
- Evidence stayed local until CI was about to publish it, so nobody looked at it as published data.

### Actions
- Corrective: guards work in a per-test scratch directory; when a test ends the harness publishes it
  with every token-shaped value replaced by its SHA-256 fingerprint (slice 2 D3, Increment A).
- Preventive: the shape-only secret check in `make qa-evidence` over the whole publication set
  (`test_report.log`, `artifacts/rogue-tests/`, `artifacts/quality/`); the CI `e2e` job uploads
  evidence only after it found nothing.

### Lesson
Evidence is published data: record proof that a value existed, never the value.

## DPL-003: Review rules and prompts lived only in a slice plan

- Status: Closed (preventive actions merged in PR #7)
- Found: 2026-10-29, in the discussion of the slice 1A review

### What happened
- The 1A review asked only about the slice's own topics, inside the plan or diff, and from round 2
  only re-checked earlier findings. Nothing asked whether a decision reached the place future agents
  read.
- The independent-review step, who reviews and what the reviewer may see lived only in the
  agentic-delivery-process `plan.md` (D11, D17, D20); the reviewer prompts were not in the repository.

### Root causes
- Standing process rules were written into a slice plan, which freezes once implemented.
- The plan template had no line for rulebook changes, so no step asked whether a decision changes how
  every later slice works.

### Actions
- Corrective and preventive: PR #7 moved the rules into `AGENTS.md` ("Independent review", slice
  workflow steps 1, 2 and 4), added the "Rulebook" line to the plan template, and records the
  reviewer prompts verbatim in each slice's review file.

### Lesson
A rule that applies to every later change goes into `AGENTS.md`, not into the plan where it arose.

## DPL-004: Slice 1B added ten requirements without proof, and review and CI stayed green

- Status: Closed (preventive actions merged with slice `ci-evidence-trace` Increment B)
- Found: 2026-10-29, after the 1B review, not by it

### What happened
- 1B added the ten `REQ-SEC` requirements. A late plan cut (1B D20) removed their runtime proof and
  was not re-reviewed. `qa-trace` reported the new gaps (requirements without E2E went from 87 to
  97), but the build stayed green and the review approved.

### Root causes
- The review was anchored to an approved plan that already had the gap; the cut was not re-reviewed
  on the reasoning that it "only removes checks".
- `AGENTS.md` said coverage gaps do not fail the build, so the gap broke no rule.
- Nothing compared `qa-trace`'s gaps with `main`'s.
- A static proof (`qa-deploy`) could not be recorded as proof, so a real proof and a missing one
  looked the same.

### Actions
- Preventive: static tests as a trace entry type, with each requirement's status taken from the
  register (slice 2 D5), and the gap gate, which fails a PR that adds a gap unless an
  `accepted_gaps` entry names it (slice 2 D7). `tests/tools/test_trace_model.py` replays this miss
  (`0dbd27b` against `8faeea9`) and fails on the ten new `REQ-SEC` gaps.

### Lesson
Removing a check is a change like any other: review it, and make a new gap fail the build.

## DPL-005: Gates ran hidden inside another CI job, and no check was required to merge

- Status: Closed (preventive action merged with slice `ci-evidence-trace` Increment B)
- Found: 2026-10-29, by the user, after the 1B review

### What happened
- The new gates `test-lint` and `qa-deploy` ran inside the CI job `docs-check`; the workflow
  `unit-trust` had grown to run every gate under a misleading name.
- The `main` ruleset required no status checks, so a red gate could be merged, although `AGENTS.md`
  said any failure blocks merge.

### Root causes
- The reviewer prompt listed the files to review (the workflow was not among them) and narrowed the
  design question.
- Under the blocking criteria, placement and naming could at best be an advisory.
- No question took the view of the person reading the PR checks.
- The ruleset is outside the repository, where a read-only reviewer cannot see it; the author had
  read it and did not connect it.

### Actions
- Corrective: workflow `CI` with one job per make target (PR #6); the user made the eight jobs
  required checks on `main`.
- Preventive: reviewer prompts give only the intent and the change, never a file list (`AGENTS.md`
  "Independent review", PR #7). The `gate-consistency` CI job fails when a gate in `AGENTS.md`, a
  job in `ci.yml` (or the command it runs) and a required check disagree (slice 2 D8).

### Lesson
What runs in CI and what blocks a merge are facts to check by machine, not to assume from names.

## DPL-006: A failed CI run was reported as passing

- Status: Closed (preventive action merged in PR #9)
- Found: 2026-10-30, by the user, during the slice 2 CI trial

### What happened
- CI trial run `40999541906` failed: the suite passed 120/120, then `make qa-evidence` failed with
  `PermissionError` on the root-owned `artifacts/` directory.
- The author ran `qa-evidence` offline on the downloaded evidence, saw it pass, and reported the
  trial as passing. The user pointed out that the job had failed.

### Root causes
- A local re-check was taken as the result, instead of the job's conclusion on GitHub.

### Actions
- Corrective: `sudo chown` of the output before `qa-evidence`; rerun `41000278717` succeeded. Slice
  2 D1 builds the ownership step into `make e2e` (test V1).
- Preventive: `AGENTS.md` "Quality gates": a gate's result is its CI job's conclusion; a local or
  offline rerun never replaces it.

### Lesson
Report a CI result as CI shows it; a rerun elsewhere is a diagnosis, not a result.

## DPL-007: Plan review answered every finding by adding mechanisms

- Status: Closed (preventive actions merged in PR #9)
- Found: 2026-10-30, by the user, after plan review round 4 of slice `ci-evidence-trace`

### What happened
- Round 1 (R1-B2) found that the evidence secret check would miss the capiss key, stored as raw
  base64. The author answered with a check that reads every registered secret and compares values.
  It could not work: the secret files are root-owned. The simple fix, a recognisable key format and a
  rule that our secrets use one (slice 2 D12), came from the user.
- D12 then had capiss generate a new key instead of converting the old one. Round 4 (R4-B2) found
  the effect on running verifiers, and the author added a redeploy procedure. Again the simple fix
  came from the user (`clean_stack.sh` empties `capiss_keys/`).
- The author claimed the SPIRE key stores were unreadable; the check had in fact found nothing at the
  paths tried. Probed properly, the directories are `root:root 750`.
- Over four rounds `plan.md` grew from 2515 to 3783 words and `test_plan.md` from 1247 to 1831
  (about +50%). All nine blocking findings were answered by adding; no round removed anything.
- Two of these answers changed a design the user had agreed in grill-me, inside a review fix,
  without asking the user.

### Root causes
Why it happened:
- RC1: findings were fixed where they surfaced (the detector), not where they came from (the key
  format).
- RC2: a sentence the author wrote in the plan ("This slice changes no service") was treated as a
  constraint, so changing capiss was never considered.
- RC3: feasibility was not probed; one `test -r` would have shown the files were unreadable.
- RC4: design changes made inside review fixes did not go back to the user.

Why review did not catch it:
- RC5: the reviewer prompt asked for the "smallest fix", which for a detector finding is a detector
  change.
- RC6: under the blocking criteria "too complicated" cannot block, and from round 2 the prompt
  allowed only blocking findings, so a simplification could not be raised at all.
- RC7: the reviewer judged inside the plan's framing (whether the check works, not whether it should
  be needed).
- RC8: "never print key material" kept the reviewer away from harmless metadata (owner, mode,
  readability) that would have shown the problem.

### Actions
- Corrective: slice 2 D12 (PKCS#8 PEM, shape-only check), `clean_stack.sh` empties `capiss_keys/`,
  and a simplification pass that removed the double-computed requirement status and the redundant
  gap-identity rule; environment facts probed and recorded in the plan. Round 6 approved.
- Preventive (`AGENTS.md`, PR #9):
  - review fixes stay within the agreed decisions; before adding a mechanism the author names the
    upstream cause and weighs changing it, and prefers removing or changing a mechanism; a fix that
    would change an agreed decision goes to the user before it is applied;
  - every review round may report "Simpler alternatives" (non-blocking) and "Decision concerns"
    (never applied by the author);
  - the reviewer may check metadata of secret files, never their content;
  - a plan that depends on a fact outside the repository records the probe and its result (plan
    template "Environment facts").
- Later (2026-11-14): fixes kept growing the process while the first preventive action stayed rule text only;
  round 2 of slice 4 has a fix add no mechanism and asks it in every initial review and recheck
  ([DPL-013](#dpl-013-review-severity-decided-what-got-fixed-a-rejection-could-stand-on-the-authors-word-and-fixes-grew-the-process)).

### Lesson
Before fixing a finding, ask which upstream choice causes it and whether changing that choice removes
the problem. Prefer removing a mechanism to adding one, and keep review fixes inside the agreed
decisions.

## DPL-008: A stacked PR was merged into its stale base branch instead of `main`

- Status: Closed (git rule merged with slice `ci-evidence-trace` Increment A; automatic deletion of
  merged head branches turned on by the owner, [#18](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/18))
- Found: 2026-10-31, by the author, when implementation was to start

### What happened
- PR #9 (the slice 2 plan) was stacked on PR #8 (`docs/review-loop`). PR #8 merged, but its branch
  was not deleted, so GitHub did not retarget PR #9 to `main`.
- The author's attempt to retarget it failed (a GitHub GraphQL deprecation error, then a blocked
  REST call). The author told the user the base still had to be changed before merging; PR #9 was
  merged into `docs/review-loop`, so the approved plan was not on `main`.
- PR #10 brought the merge to `main` unchanged; implementation started only after it merged.

### Root causes
- A stacked PR keeps its base until the base branch is deleted; merged branches were not deleted
  automatically.
- The merge screen allows merging into any base; nothing flagged that the base was not `main`.
- The warning lived in a chat message and a PR body, not where the merge happens.

### Actions
- Corrective: PR #10.
- Preventive: `AGENTS.md` git rules: a stacked PR is merged only after its base shows `main`; agents
  avoid stacking where they can. The repository setting "Automatically delete head branches" is on,
  so GitHub retargets stacked PRs itself.

### Lesson
Fix the mechanism that makes the mistake possible (stale base branches), not only the warning about it.

## DPL-009: The diff-coverage gate never measured capiss

- Status: Closed (fix and its tooling test merged with slice `ci-evidence-trace` Increment A)
- Introduced: `4b808cb` (2026-03-03), when the gate was added
- Found: 2026-10-31, by the author, when the gate reported "No lines with coverage information" for a
  branch that changes 31 lines of `services/capability-issuer/app.py`

### What happened
- `scripts/diff_coverage_gate.sh` passed `--include "services/capability-issuer/*.py"` and then
  `--include "services/tool-b/*.py"`. diff-cover keeps only the last repeated `--include`, so only
  tool-b was measured; a capiss-only change had no measured lines and the gate passed.
- `AGENTS.md` and `docs/STATUS.md` said the gate holds changed lines in capiss and tool-b to 90%.
  For capiss it never did, in CI or locally (a false green for eight months).

### Root causes
- The gate had no tooling test with a negative control (a capiss change below the threshold must
  fail), so nothing showed it measured capiss at all.
- "No lines with coverage information" reads like "nothing to check", not like a broken filter.

### Actions
- Corrective: one `--include` with both patterns; this branch's capiss diff is measured (100% after
  covering the invalid-base64 branch of the key parser).
- Preventive: `tests/tools/test_diff_coverage_gate.py` asserts both patterns reach one `--include`;
  it fails on the old script.

### Lesson
A gate without a negative control can be silently empty. Prove each gate fails on the case it exists for.


## DPL-010: Slice 2's reviews accepted answers on the author's word, and closed questions let gaps through

- Status: Open; its preventive actions are implemented on the slice 4 branch and close it when slice 4's final PR
  merges: the open mandate first in every prompt and rechecks that must open what each answer names (4.1),
  computed evidence that every review accounts for (4.2), and review records written by the launcher and
  checked by `make docs-check` against the attempt log (4.3)
- Found: 2026-11-08, by the owner (untested refusal paths in the review launcher) and by slice 2's review
  round 5, an extra round the owner asked for before merging PR #35

### What happened
- The review launcher's defensive refusal paths have no test, for example refusing when `AGENTS.md`
  is missing on the base or when the record path is invalid. Review rounds 1 to 4 did not report it,
  and the slice was called done without measuring coverage. The owner found it by asking where the
  gaps were.
- A Read that failed (a file too large to read, a missing file) counted as reading a file under
  review. That is a false green in the launcher's rule that a review must open the files under
  review. Rounds 1 to 4 missed it (round 5, R5-B1).
- The review record claimed to keep every prompt and report verbatim, but held prompts with
  placeholders and reports only in rendered form. The attempt log's hashes therefore matched nothing
  in the repository. The claim was false in the very PR that added the `AGENTS.md` rule requiring it
  (R5-B2).
- Recheck rounds accepted answers without opening the changed code:
  - Round 2 accepted launcher fixes after opening only the benchmark files.
  - Round 4 accepted, in 17 seconds, an answer claiming an "Advisory only" report column that did not
    exist (R5-A1, R5-A6).

### Root causes
Why it happened:
- RC1: tests were derived only from the test plan's rows. Checks added during implementation got no
  test, and coverage was not measured before the slice was called done.
- RC2: the record was written for reading (rendered reports, placeholders), and its "verbatim" claim
  was never checked against the attempt log.
- RC3: the fake CLI sent no tool results, so no test could show a failed Read. How the real CLI
  reports one was assumed, not probed.

Why review did not catch it:
- RC4: the author's review prompts asked closed questions ("name any test-plan row that has no
  test", "accept or re-raise") and gave no open mandate to look for what is missing.
- RC5: rechecks accepted answers on the author's word; nothing asked them to open the changed code
  and its test.
- RC6: reviewers got no coverage report and cannot run one, and the review record and attempt log
  were withheld from every round, so no reviewer checked them.

### Actions
- Corrective (PR #35):
  - Failed Reads no longer count as reading a file, and a call to any tool other than Read, Grep or
    Glob fails the review.
  - Each call that names a path outside the copy is logged with its tool and whether it was denied.
  - The record keeps every prompt and report verbatim; each block's hash was checked against the
    attempt log.
  - The report gained an "Advisory only" column, with a test.
  - How the CLI reports a failed Read was probed on 2026-11-08 (CLI 2.1.319: an error result with the
    matching call ID).
  - By the owner's decision, the untested refusal paths stay as they are in this PR.
- Preventive (implemented on the slice 4 branch, issue #33):
  - every stage's prompt opens with an open mandate, and specific questions are a minimum (4.1);
  - every stage gets the evidence (coverage, tool-computed lists of what is missing), not the
    author's conclusions (4.2);
  - a recheck opens the changed code and tests for each answer it accepts, and says what it read (4.1);
  - an open final review (4.1, 4.6);
  - a check of review records against the attempt log (4.3, in `make docs-check`).

### Lesson
A question decides what an agent looks at. Give every stage the open mandate and the evidence, and
make rechecks verify the fix rather than trust the answer.


## DPL-011: Slice 2's launcher and the secret check broke on slice 4's parallel plan reviews

- Status: Open until slice 4's final PR merges: its fixes merged with slice 4's plan PR (#48), and its last
  preventive action, the `<token>` note of S41-D1, is in the slice 4 branch's launcher (`CREDENTIAL_NOTE`)
- Introduced: slice 2 (`5a5aba7`, PR #35), which wrote report paths from the unit name, added R5-A4's
  rule on other tools and applied the evidence secret check to review reports
- Found: 2026-11-08, by the author, when slice 4's six plan reviews ran in parallel through the
  launcher

### What happened
- Five of six round-1 plan reviews were lost. Every unit was named `plan`, and the report file name
  held only the unit and the attempt, so the six reviews wrote one file.
- A review failed because the reviewer called `Bash`, which the CLI does not offer; the call ran
  nothing. R5-A4's fix failed every call to another tool.
- The publication check withheld four reports that held no secret. Its credential rule read words
  after `Authorization:` in prose and code (a code span, a format string, an escaped newline) as
  values. A withheld report is never written, so the cause had to be inferred from the repository's
  own matching lines.
- The first fix, a code-span placeholder, hid a real value in "Authorization: `Bearer <token>`" (plan
  review 4.4, A9). The fixes review found two more such forms, and that an error result does not show
  that a call never ran.

### Root causes
Why it happened:
- RC1: slice 2's tests ran one review unit per slice; several slices at once, with the same unit
  name, were never tried.
- RC2: the secret check's rules were written and tested for log lines. Slice 2 applied them to review
  reports, which are prose about this repository, without a test on prose.
- RC3: R5-A4's fix keyed on the tool name only. How the CLI answers a call to a tool it does not
  offer was not probed.

Why review did not catch it:
- RC4: slice 2's reviews judged the launcher against its test plan, which had one unit per slice and
  no report quoting the repository. No question asked how the next user would run it.

### Actions
- Corrective ([plan](slices/agentic-sdlc-poc/plan_launcher_fixes.md)): the report path holds the
  slice directory (`f070669`); only a call to a tool the init event did not offer, answered with an
  error, is logged instead of failing (`8d80ce8`); a credential value must be token-like (`d56c69a`)
  and is found in code spans and quotes (`f8b6200`, `8d80ce8`).
- Preventive: tests for two slices with the same unit, for prose and quoted forms of the header, for
  the rulebook passing the check, and for offered and unoffered tools. Implemented in 4.1 (S41-D1) on the
  slice 4 branch: the launcher's output section tells reviewers to write `<token>` for any credential
  (`CREDENTIAL_NOTE`), so a review of the secret check is not withheld for a made-up example.

### Lesson
Try a tool the way its next user will run it: in parallel, with the same names, on its own prose.

## DPL-012: Slice 4's implementation run made claims and checks that did not hold

- Status: Open until slice 4's final PR merges; every miss below was found and fixed on the slice 4 branch
- Introduced: slice 4's implementation run (`poc/slice-4-implementation`, 2026-11-09 to 2026-11-10)
- Found: by the run's own reviews (4.4's implementation review, 4.5b's report review, the final review) and by
  its dry slice ([decision page](slices/agentic-sdlc-poc/slice_4_decisions.md), discovered issues 9, 12 and 13)

### What happened
- 4.4's self-review said the benchmark's dry run built every prompt with the lists. That dry run ran while the
  key named no lists commit, so its +list prompts held none, and the dry run did not refuse as a run does.
- The canary was built on the review prompt, whose data clause no twin could pass. The author blamed the plan's
  validity rule (S45-D9), loosened the runner's gate, and ran 51 reviews before the cause was found; a canary on its
  own prompt was valid at once.
- The benchmark report said RM-6 was detected twice: the runner's repeat line read automatic scores, while the
  counts read confirmed verdicts; the rating agreement paired two runs' findings by IDs each session chose itself.
- The author's blinded verdicts applied the match rule's absence clause to one RM-6 finding and not to two others
  that met it equally.
- `README.md` still called the workflow "four-phase" after 4.6 rewrote it; 4.6's step-reference test looked only
  for "step N", and its review relied on that test.
- Three rule edits were not recorded as the author's decisions, and one plan decision (the brief on plan PRs,
  S46-D13) had no rule text.
- The benchmark never gave a reviewer the `unit-tests` list, nor the tests-first pair with `e2e-tests`: the author
  gave no case a unit-test change, and neither the author nor any review checked that every list had a case. The
  owner found it by asking (2026-11-11).
- The author proposed to stop failing a review whose `opened` names a file it did not read (growth proposal 5),
  saying the rule had cost four review sessions, without checking what each failure guarded. One of the four had
  accepted five answers on files it never read; the proposal would have passed it. The owner's question stopped it
  (2026-11-13), and a stricter change replaced it.

### Root causes
Why it happened:
- RC1: claims in self-reviews and reports were written from the intended state, not from the output of the check
  that shows it.
- RC2: when an approved rule looked impossible, the author changed the mechanism around it before looking for the
  author's own choice that made it so.
- RC3: a data source added late (the confirmed verdicts) was not carried into every function that reports on the
  same results.
- RC4: a check for stale wording was written for the planned phrase only.
- RC6: the benchmark's cases were chosen per past miss and per plant, not checked against what the benchmark was
  meant to measure (every stage list).
- RC7: a proposal to loosen a check was argued from the cost of its failures, not from what each failure caught.

Why review did not catch it earlier:
- RC5: each miss was caught by the next review that looked at the claim itself, not by the author's self-review.

### Actions
- Corrective: the unit-test gap is recorded in the benchmark report, and measuring it is the owner's decision 5; the
  loosening was withdrawn, and the owner approved instead that rejections are read like fixes and that searched files
  have their own list (2026-11-13). The dry run refuses as a run does; the canary has its own prompt and the gate requires a valid
  canary again; the repeats and the rating agreement read the confirmed verdicts and pair runs by defect; RM-6's
  two findings were re-judged by the absence clause, said openly in the report; `README.md` is current; the
  rule edits are recorded on the decision page, and the plan-PR brief has its rule.
- Preventive: each fix has a test that fails without it (the dry run's refusal, the canary gate and prompt, the
  repeats, the rating pairing, the brief's final and unreviewed units, the merged plan reviews in the final review's
  history); the step-reference test also looks for "four-phase".

### Lesson
Write a claim from the check's output, not from the plan. When an approved rule seems impossible, look first for
the author's own choice that makes it so. Before loosening a check, look at what each of its failures caught.

## DPL-013: Review severity decided what got fixed, a rejection could stand on the author's word, and fixes grew the process

- Status: Open until slice 4's final PR merges; round 2's preventive actions (R2-1 to R2-8) are implemented on the
  slice 4 branch; RC-3's miss is answered by decision concern 13's wording (2026-11-16), measured on RC-3 alone, and
  what stays open is under Actions
- Introduced: the review rules, where severity has decided what gets fixed since "everything else is advisory … not
  fixed by default", kept in four levels by slice 4.1 (S41-D6, S41-D12); the rule against growth has been rule text
  only since [DPL-007](#dpl-007-plan-review-answered-every-finding-by-adding-mechanisms)
- Found: 2026-11-14, by the owner, after the review of the owner's decisions on slice 4's decision concerns
  ([decision page](slices/agentic-sdlc-poc/slice_4_decisions.md), section "Round 2")

### What happened
- The reviewer's severity decided what was fixed: a medium finding could be deferred to an issue, or rejected without
  a later round accepting the rejection. RM-3 of the benchmark (requirements added without proof, DPL-004's miss) was
  found by every review and rated medium, so under these rules it could merge unfixed. Severity is also the least
  reliable part of a review: 16 of the 39 defects that several reviews found got different severities
  ([severity analysis](slices/poc-4-5-benchmark/severity_analysis.md)).
- A rejection needed only "a reason the reviewer can check", and the recheck that judged it was the same reviewer
  reading the author's argument; LLM judges tend to give in to rebuttals
  ([industry research](slices/agentic-sdlc-poc/industry_research.md), finding 5). A dispute went to the owner only
  when rechecks re-raised the same finding in two rounds in a row, so it could loop or end on the author's word.
- Fixes grew the process: DPL-007's check that read every registered secret (the base64 case), 4.6's brief written
  again after CI and after every push (4.6 review F3's first fix, reverted; decision concern 10), and the benchmark's
  budget raised from 60 to 85 calls (decision concern 11). The rule against it was in `AGENTS.md`, but no review
  question asked it where a fix is written or judged.

### Root causes
Why it happened:
- RC1: severity did two jobs, saying how serious a finding is and deciding whether it is fixed.
- RC2: a rejection's reason had no required form, and nothing made the recheck show what the reason rests on.
- RC3: DPL-007's preventive action stopped at rule text; it put no question where a fix is written or judged.

Why review did not catch it:
- RC4: no review prompt asked whether a fix adds a mechanism, and a recheck did not see which process files the fixes
  had changed.
- RC5: a recheck could accept or re-raise a rejection without quoting the lines its decision rests on.

### Actions
- Corrective: the benchmark is re-scored under the new rule (R2-9: a match rated medium is detected, the earlier
  results re-scored apart and the new matches confirmed blind, by a fresh session: decision concern 16):
  `short+list` 9, `open+list` 8 and `open-B+list` 8 of 11 defect cases, against 6, 7 and 6 under the rule of the runs.
- Preventive (round 2 of slice 4, implemented on the slice 4 branch; the decision page names each one's tests):
  - R2-1: blocking, high and medium findings are fixed; only a low finding may be deferred (`AGENTS.md`, Review
    findings and Review loop; `ALLOWED_ANSWERS` in `scripts/run_independent_review.py`, which the launcher applies
    before a recheck and `make docs-check` after);
  - R2-2: a rejection of a blocking, high or medium finding cites a checkable fact, by its shape (`CHECKABLE_FACT`);
  - R2-3: one dispute round: a rejection the recheck re-raises or cannot determine is fixed or goes to the owner;
  - R2-4: a fix adds no mechanism, and a finding only a mechanism would answer goes to the owner with a one-line
    proposal (`AGENTS.md`, Fixes stay within the agreed decisions);
  - R2-5: the review prompt asks an initial review whether the change adds a mechanism, and a recheck the same of
    each fix (`MECHANISM_RULES`);
  - R2-6: a recheck's evidence lists the process files changed since the reviewed round (`PROCESS_FILES` in
    `scripts/review_inputs.py`);
  - R2-7: a recheck quotes the lines each rejection it accepts or re-raises rests on, and the launcher checks the
    quote in the copy;
  - R2-8: the decision brief lists medium findings answered `rejected`.
- Measured (R2-10, one run per case and recheck wording): both wordings re-raised RC-4's false rejection, and both
  accepted RC-3's fix that adds a step where leaving the CI result out would do.
- Found by round 2's own review (round 1, F1): a rulebook edit after the validation (`eb46b58`) was checked with
  `make docs-check` and `make lint` only and broke a tooling test that pins its text; fixed, and every gate rerun on
  `1f224d1`, after which the commits change only `docs/` ([DPL-012](#dpl-012-slice-4s-implementation-run-made-claims-and-checks-that-did-not-hold)'s lesson:
  a claim is written from the check's output).
- Corrective for RC-3's miss (decision concern 13, option B, the owner, 2026-11-16): the review prompt
  (`MECHANISM_RULES` and the output section's kind bullet in `scripts/run_independent_review.py`) and `AGENTS.md`
  (Fixes stay within the agreed decisions, Report sections) now count a step added or repeated and a second copy of a
  fact that must be kept current as mechanisms; an initial review reports an unapproved mechanism as a defect, not a
  simpler alternative, and a recheck re-raises a fix that adds one at the finding's severity. Run again once on each
  recheck wording, RC-3 was re-raised at high by both. That shows little beyond RC-3: the wording's example ("again
  after every push") is RC-3's own answer phrase, since the wording was written from that case; RC-3's reviewers got
  a base rulebook that only prefers removing a mechanism, so their prompt held two definitions; and one run per
  wording gives no rate.
- Found by the review of those decisions (unit `owner-decisions-2`, round 1, F2): the example went beyond the owner's
  option B, which names none. It is removed from the launcher and `AGENTS.md`, so RC-3's two re-raises ran under a
  wording that is no longer shipped, and the shipped wording is unmeasured (decision concern 17). The same review had
  an unapproved mechanism rated a defect of at least medium, so it is fixed (F1), and the benchmark's leak search read
  the whole prompt the reviewer gets, the output section included (F3).
- Open: whether decision concern 13's wording catches growth other than RC-3's (a recheck case with another growth
  fix would show it, for example DPL-007's base64 scan where changing the key format would do), still lets a recheck
  accept answers that hold (RC-2 did not run under it) and keeps initial reviews from over-reporting mechanisms (no
  initial case ran under it); whether the rule makes a recheck re-raise good fixes that add what another rule
  requires, such as a test for new behaviour, and whether to run RC-3 and RC-2 under the shipped wording (decision
  concern 17); the process files leave out the benchmark runner, its key and the skills (decision concern 15); the
  plan list's question 8 still states the rule before R2-4 (growth proposal 14).
- Round 3 of slice 4 (2026-11-17, approved by the owner): decision concern 15 is folded into R3-1 (`PROCESS_FILES`
  adds the benchmark runner, its key and the skills), growth proposal 14 is built as R3-4, and decision concern 17's
  carve-out as R3-3 (what an existing rule already requires of a fix is not an added mechanism). Run once each on
  `recheck-A`, RC-2 accepted its fix that adds tests, citing the carve-out, and RC-3 was re-raised at high under the
  shipped wording. Still open: a growth case other than RC-3, the initial cases under the wording, and decision
  concern 16 (decided 2026-11-18: both confirmers from the next benchmark on; the first two are inputs for that
  run, tracked in #51).

### Lesson
Let a rule, not the reviewer's rating, decide what gets fixed; make a rejection rest on a fact the recheck must quote;
and ask the growth question where the fix is written and judged. A rule that lives only in the rulebook is not yet a
question anyone asks.

## DPL-014: A blind-confirmation token was not tied to its result line

- Status: Open until slice 4's final PR merges; fixed on the slice 4 branch (`a9ec037`) before the runs it would
  have affected
- Introduced: slice 4.5a's blinding (`1cf8734`, 2026-11-09), where `read_tokens` in `scripts/run_review_benchmark.py`
  keyed a token by case, configuration and finding (the run was added later), never by the result line's prompt
  identity
- Found: 2026-11-17, by the author's lookup of the runner before round 3's RC-1 to RC-4 runs
  ([decision page](slices/agentic-sdlc-poc/slice_4_decisions.md), discovered issue 44)

### What happened
- A case is run again as a new `run: 1` line when its prompt identity changes (S45-D2). Round 3 was about to run RC-1
  to RC-4 again under a new recheck. RC-1's new line on `recheck-A` would re-raise R1-1 again, and its finding would
  have found the earlier line's token (T016) under the same key, so it would have taken that token's verdict without a
  blind confirmation of its own; `--export-rescore` would have skipped it as already held. The measurement could have
  reported a detection no one had confirmed.
- No result was affected: the defect was found and fixed before the runs, and the 2026-11-16 RC-3 reruns, whose
  earlier line held a token only for another finding, were judged blind as M147 and M148.

### Root causes
Why it happened:
- RC1: the token's key named the result by the fields that were unique when the blinding was built, one run per case
  and configuration, and was not widened when runs under new prompt identities became possible.

Why review did not catch it:
- RC2: no test had a second line of a case and configuration under another prompt identity with the same finding ID,
  and no committed results held one before round 3, so 4.5's reviews of the blinding had no case that showed it.

### Actions
- Corrective: `a9ec037` keys every token by the line's case, configuration, prompt identity, run and finding
  (`token_key`); every row of the three committed key files already held its line's prompt identity. `--export-rescore`
  keeps its own earlier rows with their tokens and gives new tokens, after the last, only to findings no export holds.
  The stage-B report was byte-identical afterwards and `--rescore B` gave all 62 recorded scores.
- Preventive: `test_a_new_line_under_another_prompt_takes_no_earlier_lines_token_and_its_findings_are_exported` and
  `test_the_third_export_keeps_its_rows_and_tokens_and_adds_a_new_lines_findings_after_the_last`
  (`tests/tools/test_run_review_benchmark.py`), each failing on the code before the fix.

### Lesson
A key that joins a verdict to a result must name everything that makes the result distinct, including what a later
rerun changes.

## DPL-015: A review run again under another prompt was counted beside the run it replaced, and two rechecks accepted the fix that left it

- Status: Open until slice 4's final PR merges; fixed on the slice 4 branch (`02281b0`, R4-3)
- Introduced: slice 4.5's runner, where stage-B results are only appended (`append_result`) and counted by case,
  configuration and run (`configuration_counts`), never by prompt identity; it first showed when RC-3 ran again on
  both recheck wordings (2026-11-16)
- Found: the effect on 2026-11-16, by the author (discovered issue 39); the cause on 2026-11-17, by round 3's second
  mechanics replay, H1 (high, re-raised) ([decision page](slices/agentic-sdlc-poc/slice_4_decisions.md), discovered
  issue 56)

### What happened
- A case is run again as a new `run: 1` line when its prompt identity changes (S45-D2). The runner counted the new
  line beside the one it replaced: after RC-3's reruns on both recheck wordings and round 3's runs of RC-1 to RC-4 on
  `recheck-A`, its stage-B report read, under R2-9, `recheck-B` 3 of 4 and `recheck-A` 6 of 7, where each case's last
  run gives 3 of 3 on both.
- Discovered issue 39 recorded the effect and left the runner unchanged; the benchmark report gave the counts per
  wording beside the runner's. Until R4-3, decision 2's options to the owner quoted the runner's wrong `3 of 4`, and
  the benchmark report its `recheck-A` 6 of 7.
- A finding of 4.5's mechanics review was answered by a fix that made the prompt identity cover the whole prompt and
  the commit, so a changed input runs again. Its recheck (A/2) and round 3's first mechanics replay accepted the fix;
  the second replay's H1 re-raised it: a changed input ran again, but the counts still held the line it replaced.

### Root causes
Why it happened:
- RC1: results are only appended and keyed by case, configuration and run, with no allowance for a rerun under a new
  prompt identity: the root of DPL-014, whose corrective action widened only the token key.
- RC2: when the effect showed (discovered issue 39), the author corrected the numbers in the report by hand, not the
  count in the runner, so the runner's numbers stayed wrong and were quoted to the owner.

Why review did not catch it earlier:
- RC3: the recheck A/2 and the first mechanics replay checked that a changed input runs again, which the fix did, not
  what the counts did with the line the rerun replaced; no test had two `run: 1` lines of one case and configuration.

### Actions
- Corrective: `02281b0` (R4-3): `rule_views` keeps, in both views, the last line in file order of each case,
  configuration and run (`current_lines`); results stay append-only. Under R2-9 `recheck-A` and `recheck-B` read 3 of
  3. `ebdb0e8` puts the rebuilt report in the benchmark report and corrects decision 2's options.
- Preventive: `test_a_review_run_again_under_another_prompt_replaces_the_earlier_line_in_the_counts` and
  `test_a_recheck_run_again_under_another_prompt_is_listed_once` (`tests/tools/test_run_review_benchmark.py`), each
  failing on the code before the fix.
- Same cause, searched on 2026-11-18 (review unit `owner-decisions-3`, F1) in every place of
  `scripts/run_review_benchmark.py` that groups, counts or keys result lines, and in the attempt-log readers of
  `scripts/review_brief.py` and `scripts/run_independent_review.py`. The committed stage-B results hold six replaced
  lines, five of them completed, all on `recheck-A` or `recheck-B`:
  - `configuration_counts`, `severity_agreement`, `repeats_table`, `measurement_rows`, `false_answer_line` and
    `holds_line` read a view's current lines only (`rule_views`), so no replaced line reaches them in the view under
    the key's rule. The view under the earlier rule takes the last line among the lines recorded under that rule, so
    it keeps RC-1's and RC-2's first `recheck-A` lines, which round 3's runs under the key's rule replaced; its title
    scopes it to the reviews recorded before the key's rule.
  - `origin_table` and `question_line` read every line: the five replaced completed lines' 7 findings (of 538; one
    names its question) are in the stage-B report's origin table and question line. `02281b0` left both unchanged
    (discovered issue 56); whether they should count each review once is not decided here.
  - `report_rows` lists every run, the replaced ones too, as the benchmark report says.
  - `--export-rescore` (`export_rescore`) exports the findings of every completed defect-case line that no export
    holds, a replaced line's too, and `--rescore B` (`rescore_stage_b`) re-scores every completed line recorded under
    an earlier rule, RC-1's replaced `recheck-A` line among its 62 rows. Neither reaches a count: a verdict counts only
    through a current line's token key, and a re-score only through a current line's `review_id`, both holding the
    prompt identity. Round 4's 85 exported rows come from its 13 completed defect-case lines, none replaced.
  - `_completed_reviews`, read by `--export-measurement` and stage A's comparison, keeps the first completed line of
    each case and configuration (or prompt), so a rerun would be read in place of the current line. No committed line
    reaches it: no stage-A case and prompt, and no `open+list` or `open+list+sev` case, has a second completed line.
    Latent; not changed.
  - `previous_state` sums every line's calls, the replaced ones too, as the budget should.
  - `finding_counts` and `last_verdicts` in `review_brief.py` and the launcher's `_round_state` key attempts by their
    unique attempt ID, round and reviewer; no attempt replaces another's line, so the cause does not apply.

### Lesson
When results are only appended, decide once which line is current and read every count through that rule. When a
count is seen to be wrong, fix it at its source, not the numbers in the report.

## DPL-016: Slice 4 was declared done before its goal was tested, so the owner found the gaps in three rounds after done

- Status: Open until the next slice's plan PR merges; that plan writes the six preventive actions below into
  `AGENTS.md` and the slice templates as its first change
- Introduced: slice 4's "Done when" (2026-11-09; [decision page](slices/agentic-sdlc-poc/slice_4_decisions.md),
  section "Goal (the owner's, 2026-11-09)"), which counted what was delivered, not the goal
- Found: by the owner's questions, which opened rounds 2, 3 and 4 (2026-11-14 to 2026-11-17) and the final review's
  rerun (2026-11-18); recorded from the author's retrospective of 2026-11-18, counted from `git log` and the seven
  attempt logs of slice 4's bundles

### What happened
- The goal was that the next slice "can run the review process end to end without the owner checking by hand", with
  one owner review at the end. "Done when" counted delivery: every decision implemented and proven, the benchmark run
  within 60 reviewer runs, a fresh reviewer with no open blocker, the records current, and one dry slice, whose reviews
  got the old rules and no stage list because slice 4 had not merged. The run met it on 2026-11-10, about 14 hours
  after the plan merged.
- The slice ran on to 2026-11-18, about 10 days in all: 189 commits, of which 129 of the implementation branch's 171
  (75%) came after the final review of 2026-11-10 and 76 of the 171 touch only `docs/`; 25 review units, 63 rounds,
  78 attempts (14 failed), about USD 90 of reviewer cost. The owner had seven decision rounds after 2026-11-10, where
  the plan had one, and 38 of the 49 quotes of the owner's words on the decision page are from 2026-11-13 on.
- Rounds 2, 3 and 4 each began with the owner's own question, not a review finding: "still 6 feels short sighted, it
  is not clear review severity word change has any impact …" (2026-11-14,
  [DPL-013](#dpl-013-review-severity-decided-what-got-fixed-a-rejection-could-stand-on-the-authors-word-and-fixes-grew-the-process));
  "Why wait till next slice, this slice 4 is to fix the review checklist, prompts and make sure the review part is
  reliably covered I still feel like we are missing that" (2026-11-17, refusing the author's proposal to close the
  slice); "I feel like you settled on the wording without making industry research or best practices" (2026-11-17).
- The wording measurement could not decide: 95 reviewer runs over 7 rounds, 105 benchmark calls (about USD 70) against
  the 60 planned, the budget raised five times; 7 of the 8 recorded conclusions were within chance, gave no rate or
  rested on a one-case difference. The author's own assessment for the owner on 2026-11-16 (given in conversation, not in
  the repository) concluded that late wording tuning should wait for live evidence or a measurement with more
  than one run per case. Round 4 still ran one run per case against a criterion without margin, which the initial
  wording failed by one false alarm, counted and never judged, so the owner had to decide it (decision 8).
- The process rules changed inside the slice that used them: the read check five times in five days (the `searched`
  list added on 2026-11-13 and removed on 2026-11-17), and the rule against growth and its wording from round 2 to
  round 3.
- The benchmark runner's counting defects (discovered issues 39 and 56, 44, 55 and 57;
  [DPL-014](#dpl-014-a-blind-confirmation-token-was-not-tied-to-its-result-line),
  [DPL-015](#dpl-015-a-review-run-again-under-another-prompt-was-counted-beside-the-run-it-replaced-and-two-rechecks-accepted-the-fix-that-left-it))
  were found by the author and by round 3's replays, not by the reviews of the runner; the owner was shown wrong
  recheck counts until 2026-11-17.
- The owner's page grew from 54 KB at the final review to 201 KB. The six plans were large: five of the six plan
  reviews ran to round 5 on an extension.
- Slice 4 added no requirement and no architecture section, so its own reviews never ran the requirements and
  architecture stages, and the benchmark had two cases per list, no clean case, and computed evidence off. On
  2026-11-19 the owner's question found that a requirements- or architecture-stage review gets few trace links around
  the change: 4.2's decision S42-D3 (`docs/slices/poc-4-2-review-inputs/plan.md:41`) links only through
  `Implemented by:` lines, DD tags and the edited headings, not the architecture that satisfies an edited requirement,
  its proofs, or the requirements an edited architecture section satisfies; and that two checklist questions have
  gaps ([decision page](slices/agentic-sdlc-poc/slice_4_decisions.md), decision 10).

### Root causes
Why it happened:
- RC1: "done" counted the units delivered and reviewed, not a trial of the goal; the one trial, the dry slice, ran
  under the old rules, so nothing showed a slice running the process without the owner.
- RC2: the measurement was planned, and run again, without checking that one run per case could show the difference
  that mattered at an affordable cost; when it could not, the budget was raised and the method kept.
- RC3: wordings and defaults were recommended from the counts and the author's view before any research (round 4's
  premise).
- RC4: what each round found was fixed inside the slice by changing the rules the slice was still using, so each
  change needed its own review and left new items for the owner.
- RC5: everything for the owner went on one page, the detail too, so what needed the owner was hard to find.
- RC6: the runner's counts were tested on data without reruns under a new prompt or repeats, so its counting defects
  showed only on the slice's own results.

Why review did not catch it:
- RC7: each review judged its unit against its plan, and the final review of 2026-11-10 the change against the plans;
  no review was asked whether the goal had been tried.

### Actions
- Corrective: none beyond slice 4's own rounds; the final review's rerun is recorded in
  [DPL-017](#dpl-017-round-4s-records-and-recommendations-that-a-review-or-the-owner-had-to-correct).
- Preventive: the six actions the owner adopted on 2026-11-18 ("yes, add both DPLs and adopt all corrective
  actions"). Action 4 freezes the process rules within a slice, so slice 4 does not write them; the next slice's plan
  writes them into `AGENTS.md` and the slice templates (`docs/slices/_template/`) as its first change, each where that
  plan names:
  1. a slice's done is a trial of its goal: one small real change through the whole process, with the owner
     hands-off, before the slice is declared done (RC1, RC7). (2026-11-19, the owner with the close-out: the trial
     goes through every stage, requirements and architecture included.)
  2. before any measurement, check that it can show the difference that matters at an affordable cost; if it cannot,
     decide by research and principle and watch live evidence (RC2);
  3. research before recommending a wording or a default (RC3);
  4. freeze the process rules during a slice: what is found goes to the next slice unless it blocks (RC4);
  5. one short page of what needs the owner, the detail in the records (RC5);
  6. test a measuring tool against realistic data (reruns, repeats) before showing its numbers (RC6).

### Lesson
A slice is done when its goal has been tried the way its next user will run it, not when every unit is delivered.
Before measuring, check that the measurement can decide; before recommending, research; and keep the rules still
while the slice uses them.

## DPL-017: Round 4's records and recommendations that a review or the owner had to correct

- Status: Open until slice 4's final PR merges and the owner decides the preventive action that the next slice's
  plan proposes (#50); (a), (b), (d), (f) and (g) are corrected on the slice 4 branch, (e) before the push, and (c)'s
  correction, the final review's rerun, has ended (final review count 2, rounds 1 and 2, on PR #49)
- Introduced: slice 4's round 4 and its handoff records (2026-11-17 to 2026-11-18); (d)'s stale rows since round 2
  (2026-11-14)
- Found: (a) by the review unit `owner-decisions-3`, round 1, F2 (medium); (b) and (c) by the owner's questions on
  2026-11-18 ([decision page](slices/agentic-sdlc-poc/slice_4_decisions.md), growth proposal 12 and the Progress row
  "Final review"); (d) and (g) by the final review count 2, round 1 (FR2-1, FR2-2); (e) by the author before the
  push (2026-11-18); (f) by the author's close-out audit (2026-11-19)

### What happened
- (a) The records of R4-4's blind confirmation (the benchmark report, the decision page, the implementation log) left
  out that a first pair of confirmer sessions, whose prompt added a test beyond the match rule, was stopped before it
  wrote a verdict, and that the committed rows (`6add324`) set `expected_id` to null on the 65 no-match rows where the
  sessions had named one. F2 found it; `ec4b2a4` adds both to each record.
- (b) The author recommended that the owner approve growth proposal 12 (resuming a review that failed the read check)
  or park it, without checking its premise again. The owner approved it ("GP 12 - Approved"), then asked "Sorry, is
  GP 12 still needed, …". The attempt logs showed no read-check failure since round 3's change to the check on
  2026-11-17 (0 in 5 live reviews and 23 benchmark runs, against 9 from 2026-11-09 to 2026-11-14), and the proposal
  was withdrawn (`a832737`).
- (c) The handoff records after `owner-decisions-3` (`b354446`) said round 4 was "built, measured and reviewed" and
  listed what remained for the owner without saying that the slice's final review, which ended on 2026-11-10,
  predated rounds 2 to 4. The owner was told when asking what was pending, and decided to run it again ("3. no we
  need a final review rerun").
- After this entry was written, the same class recurred:
  - (d) FR2-1 (high, final review count 2, round 1): the decision page's proof table "Decisions and their proof"
    and its status cells named tests, rule text and launcher behaviour that later rounds had changed; fixed in
    `ea4d440`.
  - (e) 2026-11-18: the handoff records, cherry-picked after unpushed commits were rewritten, held stale commit
    hashes and claimed a recheck finding that the rerun did not make; the author caught it before the push.
  - (f) 2026-11-19: `docs/STATUS.md` and the slice index rows 4.1 to 4.6 still described the branch as pushed by
    the owner, the final review as running and the final PR as pending, after the final review had ended. The
    author's close-out audit found it when the owner asked what was open; fixed in the close-out commit.
  - (g) FR2-2 (medium, final review count 2, round 1): work found but not done was not tracked in issues until the
    final review found it, a handoff step skipped; fixed in `d76035e`, the issues opened and the answers in
    `f7fd411`.

### Root causes
Why it happened:
- RC1: the records and the recommendation were written from the plan or memory, not from a check of the current
  state: the sessions and the committed rows (a), the attempt logs since the read check changed (b), the date of the
  last final review against the rounds since (c). The same class as
  [DPL-012](#dpl-012-slice-4s-implementation-run-made-claims-and-checks-that-did-not-hold)'s RC1.

Why review did not catch it earlier:
- RC2: a recommendation or an answer to the owner passes no review; the line of (c) was in the copy of the later
  review `owner-decisions-4` (reviewed commit `6ca3d60`), which did not raise it.

### Actions
- Corrective: (a) `ec4b2a4`; (b) withdrawn in `a832737`; (c) the unit `final` ran again over the whole slice under
  R4-1's final mandate after the owner's reset on PR #49, and count 2 ended after round 2 (decision page, Progress
  row "Final review"); (d) `ea4d440`; (e) the records corrected before the push; (f) the close-out commit;
  (g) `d76035e` and `f7fd411`.
- Preventive: at first none new, on the view that DPL-016's action 3 (research before recommending a wording or a
  default) and DPL-012's lesson that a claim is written from the check's output covered these misses. That did not
  hold: the class recurred in (d) to (f). The next slice's plan (#50) proposes one preventive action for the owner to
  approve.

### Lesson
Before writing a record, a recommendation or a list of what remains, check the current state it describes: the
sessions, the attempt logs, and the date of the last review against what changed since.

## DPL-018: Commits prepared for a push carried operational details of the agents' GitHub identity; the author's scan caught them before the push

- Status: Open until the next slice's plan PR merges; that plan proposes the preventive action below to the owner
  ([#50](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/50))
- Introduced: slice 4's handoff for the push (2026-11-18)
- Found: 2026-11-18, by the author's scan of the commits before the push

### What happened
- While preparing slice 4's handoff for the push, the author wrote into two public records, the rule-deviation row
  under "Decisions made" on the [decision page](slices/agentic-sdlc-poc/slice_4_decisions.md) and the
  [implementation log](history/implementation_log.md), details of how the agents' GitHub identity is set up.
- The author's scan of the commits before the push found them. The unpushed commits were rewritten without them
  before anything was published, and the first run of the final review's round-2 recheck, whose report quoted the
  text, was discarded with those commits (implementation log, 2026-11-18, the final review's rerun).
- Nothing reached GitHub.

### Root causes
Why it happened:
- RC1: the rule that operational details of identities, credentials and local setup stay out of the public
  repository, its issues and its PR bodies lives in the author's notes (and as a source of 4.2's S42-D8), not in
  `AGENTS.md`. Coding rule 1 covers secrets, and the evidence secret check (`make qa-evidence`) matches secrets by
  shape, so neither covers prose.

Why review did not catch it:
- RC2: no review or gate checks a record for operational details.

### Actions
- Corrective: the unpushed commits rewritten without the details, before the push (2026-11-18).
- Preventive: proposed to the owner in the next slice's plan (#50): a line in `AGENTS.md` that keeps operational
  details out of what is published, and the author's scan of what goes public before each push. Publication
  scanning is [#21](https://github.com/gunaseelan-sivanandam/agentic-iam-spiffe/issues/21).

### Lesson
Check what goes public before the push, for operational details as well as secrets.
