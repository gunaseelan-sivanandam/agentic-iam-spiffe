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

### Lesson
Before fixing a finding, ask which upstream choice causes it and whether changing that choice removes
the problem. Prefer removing a mechanism to adding one, and keep review fixes inside the agreed
decisions.

## DPL-008: A stacked PR was merged into its stale base branch instead of `main`

- Status: Open; closes when the git rule below merges (slice `ci-evidence-trace` Increment A) and
  the repository deletes merged head branches
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
  avoid stacking where they can. Pending (user): the repository setting "Automatically delete head
  branches", so GitHub retargets stacked PRs itself.

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

