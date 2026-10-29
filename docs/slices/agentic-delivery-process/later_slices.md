# Later slices — drafts for slices 2 and 3 (not approved)

Status: **draft input** (2026-10-29). Merging the slice-1 plan does **not** approve anything here.
Each slice starts with its own grill-me, which uses this file as input, and gets its own
`plan.md`, `test_plan.md` and independent review under the D17 acceptance bar and the D18 threat
model. The designs below are the state reached in the slice-1 review; the findings listed against
them are open and must be resolved, or answered by D18, in that slice's plan.

## Carried review findings
IDs refer to [`plan_review.md`](plan_review.md).

| Finding | Topic | Slice | PoC-proportion recommendation (2026-10-29) |
| --- | --- | --- | --- |
| PR-01, PR-21, PR-22 | PR code on the runner can take it over or forge results | 2 | Out of model (D18, OPL-009). Drop the five-job model and the Docker controller below: one CI job that runs the full E2E suite and `qa-evidence` with no secrets is enough. |
| PR-12, PR-31, PR-32 | contract delta: review coverage, thresholds as approved data | 2 | Drop `contract_delta.yaml`; the user reviews the plan and the implementation diff, and a threshold change is stated in the plan. |
| PR-17, PR-18 | lane cap, ratchet | 2 | Keep the cap as a lane selector; the ratchet is already simplified in D17. |
| PR-23 | existing tests cannot evolve if `main`'s harness is authoritative | 2 | Drop the "`main`'s harness runs existing tests" rule; the finding disappears with it. |
| PR-27 | check removal scope | 2 | Start with the decision points a PR touches; nightly over everything is optional. |
| PR-08, PR-30 | agent identity, merge reserved to the owner | 3 | Keep only "the agent cannot merge" (a ruleset reserving merges to the owner); a separate machine identity is optional. |
| PR-14, PR-29 | run ledger authenticity | 3 | Drop the ledger branch; TCR, DEV and round counts live in the run records and are checked at the PR. |
| PR-15, PR-19 | review binding, calibration | 3 | Digests in the report (done in slice 1); calibration optional. |
| PR-24 | the commit hook forbids phase and WIP commits | 3 | Keep: a real contradiction, cheap to fix. |
| PR-25, PR-28, PR-09 | Redis mechanism for REQ-SEC-S1 | pilot | Keep: the pilot chooses the mechanism. |

The drafts below still describe the heavier designs; each slice's grill-me decides with these
recommendations as the starting point.

## Deferred from slice 1 (D20, 2026-10-29)
The user cut slice 1 to its core. These parts of the earlier slice-1 draft are not approved; a later
slice picks one up only if the reviews or an escaped defect show it is needed, and asks first.

| Item | What it was | Replaced for now by |
| --- | --- | --- |
| Runtime asset scan and invariant matrix | in-container checks that holders have their key, non-holders cannot read key paths, a content scan for private keys under other names, and a planted canary | the one-time baseline look and the key question in the implementation-PR review |
| Wrong-failure replay and kind registry | an offline tool running each outcome check against recorded evidence of other failures, per outcome kind (16 kinds), with `expect:` blocks and `observed_signature.json` for every test | the test question in the implementation-PR review |
| Tiers and fault injection | gate-derived controls per test; live runs that remove a protection and show the outcome flips | positive twins only |
| Provenance enforcement | a gate checking that `probe@`/`existing@` commits are the merge-base and that probes precede service changes | the `Source` column, reviewed in the PR |
| Derivation checklist | fixed evasion and wrong-reason columns for every test-plan row, with an appendix | the review questions |
| Live outcome guards | moving the 4 guards that call `docker` or `redis-cli` to evidence-only checks | unchanged |
| Earlier test drafts | T-1 to T-6, T-21, T-23 to T-27, T-42 | — |

## Proposed slice — `asset-classification` (draft, 2026-10-29)
Not approved; it starts with its own short grill-me, before or alongside slice 2. It would replace
the smaller idea of requiring only every `secret_env` name to be an asset.

**Problem.** `qa-deploy` (1B) checks only the assets it is told about. A new service, mount, env var
or privilege fails until it is registered, but a brand-new asset (a new key, socket or credential
file in a new place) can be registered as an ordinary mount, and a secret env var can be registered
as plain `secret_env`, without anything requiring holders or a `REQ-SEC`. A secret whose name does
not match the secret pattern is not flagged at all. Recognising that something is an asset is left
to grill-me, the review and the user.

**Idea: classify everything that enters a container.** Unclassified fails, so nobody has to remember
to add an asset; the author must choose a class. Field practice: an asset inventory with information
classification (ISO 27001 asset inventory and classification, CIS Controls 1 and 3, FIPS 199 impact
levels).

- **Resources:** every mount source (path or socket), every env var name, every compose secret and
  config; later, shared state stores such as Redis.
- **Classes:**

  | Class | Means | Examples | Required controls |
  | --- | --- | --- | --- |
  | `public` | harmless if anyone reads it | capiss public key, OPA policy, Envoy config | none |
  | `internal` | not secret, not for outsiders | audit and log directories, mock data, URLs, `REDIS_URL` | per-service allowlist (as today) |
  | `restricted` | confidential or grants authority | private keys, tokens, join tokens, SPIRE admin socket, Docker socket, Workload API socket | holders and a `REQ-SEC` requirement, consistency checked (as today) |

- **Mechanical rules in `qa-deploy`:**
  - completeness: a resource without a class fails;
  - consistency: `restricted` without holders or a `REQ-SEC` fails; holders on a `public` resource
    are inconsistent;
  - plausibility (anti-downgrade): name heuristics (`*.key`, `*token*`, `*.sock`, `keys.json`,
    `*SECRET*`, the Docker socket) and, locally, content heuristics (PEM private-key headers) give a
    minimum class; declaring a lower class fails unless the entry carries a one-line reason. This
    is the OPL-005 pattern: a key directory thought of as "the public key".
- **Judgment by reviewers:** `qa-deploy` prints the resources added or reclassified by a change; that
  list is an environment fact for the plan reviewer and the security lens, who judge each class.
  Grill-me asks the author to classify what a slice will add.
- **What remains:** a confident misclassification of a file whose name and content look harmless.
  Under the honest-mistake threat model that is rare; forgetting, the common failure, is fully
  covered by completeness.

**Cost.** One-time classification of about 30 mount sources and 40 env names (most env vars are
`internal`), proposed by the agent and approved by the user; then one register line per new
resource. It changes the register's shape and `qa-deploy`'s rules.

**Decisions for its grill-me:** the classes and their names; what counts as a resource (are
networks and published ports resources, or stay allowlist facts?); the plausibility heuristics and
the downgrade-reason rule; whether content heuristics run only locally; how state stores are
classified and whether this slice or the pilot adds REQ-SEC-S1.

## Slice 2 — `delivery-lanes-ci` (draft)

### Lanes (D9)
The approved content is this table. Its authoritative home after Increment 1C is
`security/lanes.yaml` (triggers, caps, sensitive paths), which the classifier reads, and a
"Delivery lanes" section in `AGENTS.md` that `docs-check` keeps in agreement with that file. This
slice bundle is frozen once implemented, so it is not the place anyone looks the lanes up.

| Lane | Triggered by | User involvement |
| --- | --- | --- |
| Full slice | a contract file changes (requirements, architecture, `invariants.yaml`, `lanes.yaml`, `grill_checklist.md`, test_plan rows, `expect:` blocks, existing tests); new surface (HTTP route, `reason` code, env var, outbound host, mount, port, public function in a sensitive file); net removal of a decision point in a sensitive path (`if`/`elif`/`raise`/`except`/`assert`, early `return`, `_deny(...)`, Envoy filter or route, Rego rule), measured by a structural diff; gate, classifier, threshold or `.github/workflows/` changes; over the cap; major dependency bump | grill-me, plan PR, implementation PR |
| Fix | contract-preserving, within the cap | merge `fix.md` as a plan PR, then the implementation PR |
| Dependency | minor or patch dependency update; lockfile lines excluded from the cap | merge `dep.md` (changelog and advisory review) as a plan PR, then the implementation PR |
| Docs | non-contract docs only (README, STATUS, history, test_spec prose) | implementation PR |

Every lane: a reproduction test the gate proves fails on the base commit with its declared
signature (fix lane), 100% coverage of changed lines, mutation testing on changed lines, and the
independent reviewers. The cap (at most 60 changed non-test lines and 3 non-test files) only
selects the lane: a change within it may take the fix, dependency or docs lane, a change over it is
a full slice. A full slice has no size cap; each increment is its own PR. Each surviving mutant is
justified in `fix.md` (or the slice's run records) and listed in the PR. Sensitive paths: capiss, the verifiers, `services/shared`, the Envoys, OPA, SPIRE
config, compose, the MCP adapter, the mocks, `varambu` rendering, and the QA gates, harness and
validators. `fix.md` has required sections: the approved behavior it violates (REQ or `expect:`
reference), root cause vs symptom, what the reproduction test asserts and its signature, lane and
why, and what was not checked — each with the agent's answer and the reviewer's verdict.


### Review template (input from the 1A review discussion, 2026-10-29)
Not approved; slice 2's grill-me decides it together with the lanes, because each lane says which
review it gets. Slice 3 then runs the reviewer automatically from the same template.

**Why.** The 1A review showed the reviews were short-sighted: the prompts asked about this slice's
topics (wrong failures, keys) and only inside the plan or diff, and from round 2 only re-checked
earlier findings. Nothing asked whether a decision reached the place future agents read. Gaps found:
- the slice workflow in `AGENTS.md` (steps 1 and 4) does not say that plans and implementations get
  an independent review, who reviews, or what the reviewer may see; that lives only in this slice's
  `plan.md` (D11, D17, D20);
- the reviewer prompts used for the plan and 1A are not in the repository;
- the plan template's "Authored source changes" has no line for rulebook (`AGENTS.md`) changes, so
  no step asks whether a decision changes how every future slice works;
- the blocking list in `AGENTS.md` "PoC scope and proportion" does not name a security defect in the
  system under test or a correctness bug.

**Proposed generic questions**, one template for every review (plan, feature, patch, doc, process),
so that the specific checks come from the repository's own rules rather than from the prompt:

*Entry (author):* automated gates pass; the author reviewed their own change; the change is small
enough to review, otherwise split.

1. **Intent.** Does it do what was asked or approved, no more and no less?
2. **Claims and evidence.** For each claim (test, doc, PR text, requirement), what proves it? Could
   the proof hold while the claim is false? Is each requirement verifiable and unambiguous?
3. **Design and quality.** Simplest design that fits, consistent with its surroundings, readable and
   maintainable; real alternatives considered; each relevant quality (reliability, performance,
   operability and diagnosability, usability of docs or CLI, compatibility) no worse than before.
4. **Failure and change.** Behaviour on invalid input, dependency failure, partial failure, timing or
   concurrency; fails safe; can be rolled back or migrated.
5. **Rules and new risks.** Keeps every standing rule and invariant (`AGENTS.md`, requirements, asset
   holder list, open problems); registers and threat-checks any new asset, trust boundary, data
   flow, dependency or rule it adds.
6. **Ripple.** What depends on what changed, and is each dependent still correct or updated?
7. **Durability.** Does anything decided or learned live only somewhere temporary (chat, scratch, a
   frozen slice record, a PR comment)? Where must it live?
8. **Blind spots.** What was not checked, and could it matter?

Severity: 1, 2, 4 and 5 can block, with a concrete failure inside the threat model; 3, 6 and 7 are
fix-or-defer and the user decides; 8 is information. Every question is answered; "n/a" needs a
reason. The 3-round limit and the threat model in `AGENTS.md` apply. The reviewer reads the intent
source, the change, `AGENTS.md` and the whole repository (read-only), never the author's reasoning.
When a defect escapes, the escape review asks which question should have caught it and sharpens that
question; it never adds a topic-specific question.

**Field practice it draws on:** Google engineering practices for code review (design, complexity,
tests, consistency, docs); ISO/IEC 25010 quality characteristics; failure-mode thinking (SRE
production-readiness reviews, FMEA); threat modelling (STRIDE, OWASP) for new boundaries; IEEE 29148
requirement qualities; IEEE 1028 and Fagan inspections (entry and exit criteria, checklists that
learn from defects); review-size findings (about 200–400 lines per review, author self-review first);
architecture decision records; blameless escape analysis. Not adopted for the PoC: separate reviewer
passes per perspective (a second, security-focused pass is an option for security-relevant slices)
and review metrics.

**Proposed homes:** the template as `docs/review_prompt.md`, approved by the user; `AGENTS.md` slice
workflow steps 1 and 4 run it on the plan and on the implementation, and lanes outside a full slice
run it too; a "Rulebook (`AGENTS.md`): process rules this slice adds or changes, or none" line in the
plan template; the two extra blocking items in the PoC section.

**Interim (slice 1B):** the 1B review gets these questions informally, alongside the slice's two
questions, to try them before slice 2 makes them a rule.

### Review lenses and gates (input from the 1B review discussion, 2026-10-29)
Not approved; the user is not yet sure the lenses and their jobs are the right ones, and slice 2's
grill-me decides. Adds to the review template above.

**Why.** After the generic questions were tried in 1B, the review still missed that the 10 new
REQ-SEC requirements had no E2E proof. Causes: the review was anchored to an approved plan that
already had the gap (the D20 cut removed the runtime proof and was not re-reviewed, on the reasoning
that it "only removes checks"); `AGENTS.md` says coverage gaps do not fail the build, so the gap
broke no repository rule; the generic questions were a brief side part of the prompt; and
`qa-trace` reported the new gaps (87 → 97 requirements without E2E) but nothing compared them with
`main`.

**User decisions (2026-10-29):** static tests are acceptable wherever they make sense; reviews
should use several reviewers, each with its own lens, because one generic reviewer will keep
leaving gaps.

**Layer 1, gates for facts a machine can see:**
- `qa-trace` compares its coverage gaps with `main`'s and fails on a new gap (a requirement without
  proof, an architecture section without design or integration test) unless the plan accepts it
  with a reason;
- a static-proof kind in `trace/tests.yaml`, so a requirement can be proved by a static check such
  as `qa-deploy`, visibly labelled (the REQ-SEC requirements and DD-925 to DD-930 need it);
- `docs-check` fails when a make gate is not listed in the `AGENTS.md` quality gates (1A missed
  `test-lint` there).

**Layer 2, reviewers with separate lenses** (proposal, not settled):

| Lens | Job | Reads | Would have caught |
| --- | --- | --- | --- |
| Goal and evidence (product owner) | serves the PoC goal; challenges the plan itself; what is missing; which test proves each requirement and at which level; decisions recorded where future agents read them | plan, requirements, the trace-gap report, `AGENTS.md`, the change | unproved REQ-SEC; the review step missing from the rulebook |
| Security (adversary) | threat model, assets, trust boundaries, new risks; builds a concrete bypass | change, register, compose, threat model | 1B C1, C3, C4; 1A false greens |
| Engineering quality (maintainer) | design, simplicity, failure modes, test adequacy, ripple through code and CI | change and surrounding code | 1B C2; 1A B-series |

- Different models for different lenses where it matters (for example Codex for security, a
  clean-context Claude for the others), to reduce shared blind spots.
- At most 3 blockers and 3 advisories per lens; one synthesis step removes duplicates, applies the
  acceptance rule and gives the user one list, so more lenses do not mean endless findings.
- Scaled by lane: a doc or patch change gets one combined review; a feature or security slice gets
  every lens.
- A plan change, including a removal, is re-reviewed with "which requirement or decision loses its
  evidence?".
- The reviewer receives the gate outputs, including the trace-gap difference.
- An escaped defect sharpens the lens that should have caught it; no topic-specific questions.

**Expected limits:** perspective-based review finds more distinct defects than one shared checklist,
but lenses anchored to the same plan share its blind spots, and the same model with different
prompts shares blind spots too. The aim is fewer and cheaper escapes caught before merge, not zero.

### Review misses after the 1B review (input, 2026-10-29)
Not approved; slice 2's grill-me decides, together with the lenses above.

**What was missed.** The user, not a reviewer, found that the new gates `test-lint` and `qa-deploy`
ran hidden inside the CI job `docs-check`, that the workflow `unit-trust` had grown into every gate
under a misleading name, and that the `main` ruleset required no status checks, so a red gate could
still be merged although `AGENTS.md` said any failure blocks merge. All three are fixed (workflow
`CI`, one job per make target; the user made the eight jobs required checks).

**Why:** the author's prompt listed the files to review (the workflow was not among them) and
narrowed the design question to "consistent with the other QA scripts"; the acceptance rule let only
false greens, contradictions and missing tests block, so placement and naming could at best be one
of a few advisories and were crowded out; the misleading name pre-dated the change and nothing asked
whether the surroundings still fit; no question took the view of the person reading the PR checks;
and the ruleset is outside the repository, where a read-only reviewer without network cannot see
it. The author had read that ruleset earlier and did not connect it.

**Six proposed changes** (the second and third are mechanical, the rest are review design):
1. **Fixed prompt template, no author scoping.** The author supplies only the intent and the change,
   never a list of files to focus on or narrowed questions; the reviewer decides where to look.
2. **Environment facts as input.** A read-only script collects facts outside the repository: the
   branch ruleset and its required checks, the latest CI run's jobs and results, and the `qa-trace`
   gap difference against `main`. The reviewer judges the repository's claims against them.
3. **Gate–job–check consistency as a mechanical check.** Every gate in the `AGENTS.md` quality-gates
   table has a CI job of the same name, and every such job is a required check on `main` (the
   ruleset part reads the environment facts above).
4. **The generic questions are the review,** answered in depth, not a brief side part; where lenses
   apply, each lens owns its questions.
5. **An operator-usability and fit question:** "Are names, placement and structure what a newcomer
   would expect? Can the user see what ran and what failed? After this change, do the surrounding
   names, groupings and files still describe what they contain?"
6. **A separate budget for quality and usability findings:** capped and fix-or-defer for the user to
   decide, so they are neither crowded out by blockers nor allowed to become endless findings.

### CI trust model
Resolves review findings PR-01, PR-02, PR-12 and PR-15. Every job definition comes from `main` via
`pull_request_target`; the workspace root is a checkout of `main` and the PR is checked out into
`pr/`, never used for the gate's scripts, config or local actions. Only same-repository PRs run.

| Job | Runs PR code | Credentials | Produces | Trusted for |
| --- | --- | --- | --- | --- |
| `gate` | no; reads the PR's diff and files as data | read-only token | lane, structural diff, contract-delta check, static `qa-deploy`, `test-lint`, `plan-lint`, required-check name collision check | its verdict |
| `plan-review` | no; plan files as data | a model API key, scoped to this job | the authoritative plan review with input digests | the plan PR verdict |
| `execute` | yes, on its own runner | none (read-only token, no secrets, no caches) | unit, coverage, mutation and reproduction-on-base results; E2E evidence | nothing until `verify` judges it |
| `verify` | no; fresh runner, `main`'s code | read-only token | the verdict on `execute`'s artifacts (thresholds, signatures, replay) | its verdict |
| `candidate-gate` | yes, the PR's gate code | none | `main`'s registered negative controls run against the PR's gate code | required when a PR changes gate code |

The `execute` job, in order:
1. `main`'s static `qa-deploy` checks the PR's compose before anything starts. A PR that gives any
   service the Docker socket, a host mount, `privileged`, host networking or an image not pinned by
   digest outside the register fails here, before PR code runs.
2. The PR's stack comes up and **`main`'s** harness runs every test that exists on `main`; that
   evidence is uploaded at once. During this phase no PR-controlled container holds the Docker
   socket or a writable repository mount: `rogue-tests` loses both, and Docker-level steps (fault
   injection, log capture, `docker exec` probes, process users) move to a controller from `main`
   that runs on the runner and writes an evidence directory the harness cannot write.
3. The PR's harness runs new and changed tests. Their evidence is reviewed and replayed before
   merge and becomes authoritative from the first nightly run on `main` after the merge.

Executable policy versus contract data. Gate code and thresholds come only from `main`. Contract
data (`invariants.yaml`, `expect:` blocks, kinds, the lane and decision-point mapping) comes from
the PR, but `gate` accepts a change to it only if it equals the contract delta of the approved plan:
every plan carries `docs/slices/<id>/contract_delta.yaml` (the exact entries added, changed or
removed), and `gate` compares the PR's change with that file at the plan's merge commit on `main`.
Anything outside the delta, or a delta from another plan revision, fails.

What this does not prevent: code the PR runs in `execute` can fabricate the results of the steps
that run it (its own unit tests, coverage, mutation statistics, new E2E tests). Those inputs
(tests, `conftest.py`, test and mutation config, harness) are sensitive paths, so such a PR is a
full slice that the user reviews, and the nightly run on `main` recomputes every result after the
merge.


### Scope draft (was Increment 1C)
- `security/lanes.yaml` (triggers, caps, sensitive paths) and the
  "Delivery lanes" section of `AGENTS.md`, kept in agreement by `docs-check`; the lane classifier
  with the structural diff, new-surface detector and size cap; the reproduction-on-base check; 100%
  changed-line coverage and changed-line mutation for every service, not only capiss and tool-b;
  `make slice-close` with the plan-vs-diff asset check (D16); `make plan-lint` and the "Assets and
  trust" table in `docs/slices/_template/plan.md`; templates for `fix.md`, `dep.md`, TCR and DEV
  records, with validators; a gate registry (`scripts/gates.yaml`, every gate with its negative
  controls) and mutation testing of the gate code; portable git hooks (`make hooks-install`: lint,
  `docs-check`, no `Co-Authored-By` trailer); CI as in "CI trust model": the `gate`, `execute`,
  `verify` and `candidate-gate` jobs, evidence bound to the PR head commit and run; the Docker
  controller from `main`, with the Docker socket and the writable repository mount removed from
  `rogue-tests`; `contract_delta.yaml` in the slice template and its check; the mutation scoring
  rules.
  D17: check-removal runs (per PR and nightly) with the decision-point-to-test mapping in
  `security/lanes.yaml`; the mutation ratchet in `scripts/gates.yaml`; the escaped-defect corpus in
  `tests/escapes/`; the escape-review check on closed OPL entries; `plan-lint` checks of the
  derivation columns.


### Test drafts (from the slice-1 review)
- T-14 Lane classifier, one fixture diff per trigger:
  - each contract file;
  - each new-surface kind;
  - removal of each decision-point kind in a sensitive path;
  - gate, threshold or workflow change;
  - 60 non-test lines and 3 non-test files (fix lane); 61 lines, or 4 files (full slice); a full slice over the cap is not rejected for size (PR-17);
  - major dependency bump;
  - a sensitive file renamed to a non-sensitive path, a deleted test or `expect:` block, a symlink
    into a sensitive path, a file-mode change (classified by both old and new path).

  The expected lane must be exact for each.
- T-15 Self-rerouting: a PR fixture that edits the classifier's thresholds is classified by `main`'s copy and lands in the full-slice lane.
- T-16 Reproduction on base: a fix-lane regression test that passes on the base commit fails the check, and so does one that fails on base for a reason other than its declared signature (import error, timeout, wrong reason). Runs in `execute`, judged by `verify`.
- T-17 Changed-line coverage and mutation: one uncovered changed line fails; an unjustified surviving mutant fails; a justified one passes and is listed.
- T-18 `slice-close`: each missing close-out item fails on its own:
  - `test_spec` heading;
  - implementation log entry;
  - STATUS update;
  - red-team report or its "not checked" section;
  - a DEV without the reviewer's confirmation.
- T-19 Git hooks: a commit message with a `Co-Authored-By` trailer is rejected.
- T-20 Candidate gates (PR-02): a test PR that edits a gate to always pass is judged by `main`'s gate, and `candidate-gate` runs `main`'s registered negative controls against the PR's gate, which fails them; a correct candidate passes them (verified on GitHub in 1C).
- T-28 CI jobs: a test PR that edits the workflows to skip the suite still runs `main`'s jobs; a PR that adds a workflow job named like a required check fails `gate`; a fork PR is refused (verified on GitHub in 1C).
- T-29 Evidence binding: evidence whose commit SHA or CI run id differs from the PR head and the current run is rejected; local `artifacts/` committed in the PR are ignored.
- T-43 Contract delta (PR-12): a PR whose contract-data change equals the approved `contract_delta.yaml` on `main` passes; one extra entry, a changed holder, or a delta from an earlier plan revision fails.
- T-44 Execution isolation (PR-01): in `execute`, the harness container has no Docker socket and cannot write the controller's evidence directory or the repository; a PR compose adding the Docker socket, a host mount, `privileged` or an unpinned image to any service fails static `qa-deploy` before bring-up; evidence the PR harness writes for a test that exists on `main` is ignored in favour of `main`'s harness evidence.
- T-30 Lanes documentation: the `AGENTS.md` lane table disagreeing with `security/lanes.yaml` fails `docs-check`.
- T-31 Plan gate (D16): a `plan.md` without the "Assets and trust" table, or with a row missing class, holders, `REQ-SEC` link or runtime proof, or "none" without a reason, fails `plan-lint`.
- T-32 Plan-vs-diff (D16): a slice diff adding a mount, secret env var, key path or network not in the plan's asset table fails `slice-close`.
- T-33 Gate registry: a gate in the Makefile or `scripts/` not in `scripts/gates.yaml`, or registered without a negative-control test, fails.
- T-34 Gate mutation: mutation score of the gate code (lane classifier, `qa-evidence`, `qa-deploy`, `test-lint`, replay, `slice-close`, `plan-lint`) at or above 80%; each survivor justified.
- T-35 Check removal (corrected by review PR-04): the runner fails when a removed decision point is killed by no mapped test (fixture service and test pair); on capiss, changing the `opa_unavailable` response from 503 to 403 with the same reason is survived by the pre-1A `M3.S2-T4` (it accepts `403|503` and checks only the reason) and killed by the tightened one (exact 503).
- T-36 Mapping drift: a decision point killed only by a test not mapped to its file fails the nightly run until the mapping is corrected.
- T-37 Mutation ratchet (PR-18): lowering a threshold fails outside the full-slice lane and inside it unless the approved contract delta names the decrease; a full slice that closes without the +5 service raise fails, one that raises past 85% fails, one at 85% stays; missing threshold history fails.
- T-38 Escape corpus: a corpus fixture the suite does not catch fails; removing a fixture outside the full-slice lane fails.
- T-39 Escape review: an OPL entry marked closed without a "why no test caught it" section and its checklist addition fails `docs-check`.
- T-40 Derivation and complete sets: a `test_plan.md` row with an empty derivation column fails `plan-lint`; a test, service, decision point, kind or `REQ-SEC` missing from its enumerated coverage fails.

## Slice 3 — `delivery-orchestration` and the pilot (draft)

### Pipeline credentials
Resolves review finding PR-08.

| Credential | Holder | Permissions | Never available to |
| --- | --- | --- | --- |
| Agent GitHub identity (a machine account or GitHub App) | the pipeline | this repository only: push branches, open PRs, comment; not an admin, cannot bypass rulesets | CI `execute` |
| Owner GitHub account and tokens | the user | merge; the approving review `main` requires | every agent session (hooks refuse reads of `~/.config/gh`, `~/.ssh`, `~/.codex/auth.json` and the ARCH-033 credential links) |
| Codex login | the local plan and red-team reviewers | model access | implementer, test author, CI `execute` |
| CI model API key | the `plan-review` job | model access | every other job |

`main` requires one approving review, and a PR's author cannot approve it, so the owner's approval
is the human act and the agent identity cannot merge.


### Scope draft (was Increments 2 and 3)
**Orchestration**
- `.claude/skills/deliver/` (`/deliver <slice>`), role subagents in `.claude/agents/` (test
  author, implementer, code-vs-plan reviewer, doc-claims reviewer, Claude red-team fallback), a
  saved workflow in `.claude/workflows/` with phases, TCR and DEV routing, and stop limits.
- Phase boundaries are commits (resolves PR-14). At each phase end the workflow requires a clean
  tree (nothing staged, unstaged or untracked) and appends an event commit (phase end, TCR filed,
  verdict, review round, gate run) to the ledger branch `run/<slice-id>`. Role-scope checks diff
  the phase's start and end commits; stop counters are computed from the ledger, which CI reads, so
  deleting a record on the slice branch changes no count. A missing or unreadable ledger stops the
  run.
- The CI `plan-review` job and the agent identity and credential boundaries in "Pipeline
  credentials".
- `scripts/redteam_codex.sh` (`codex exec`, read-only sandbox) with the recorded fallback.
- D16: `security/grill_checklist.md` and the `slice-grill` skill in `.claude/skills/`, which ends
  by running the independent plan review and opens the plan PR only when it has no open finding.
- D17: the independent plan reviewer (`scripts/plan_review_codex.sh` plus a Claude fallback
  subagent), its seeded-gap calibration fixture, and the adversarial gate reviewer.
- Claude Code hooks in `.claude/settings.json`:
  - edits to `services/`, `compose/`, `policy/` or `spire/` are refused without an active approved slice;
  - `git commit` is refused until `make slice-close` has passed for the current tree;
  - edits to frozen slice bundles are refused;
  - `Co-Authored-By` trailers are refused;
  - reads of the owner's credential files are refused for every agent role.
- Run state in `docs/slices/<id>/run/`; `scripts/slice_report.py` builds the PR body from
  evidence; a push notification at a stop or at handoff.
- The rulebook (`AGENTS.md`) rewritten to describe the pipeline in place of the manual steps (the
  lanes section lands in 1C).


**Pilot**
- Run `opl-005-006-007-isolation` as a full slice through the pipeline: grill-me, plan PR,
  `/deliver`. Its content (public-key-only mounts, Workload-API-socket-only mounts, Redis ACLs,
  removal of the agent-a/rogue key mounts, `M2-T7` corrected to check the deployed rogue) is decided
  in its own grill-me.
- Record every pipeline problem the pilot shows, and fix it or log it.


### Process state draft
| State | Store | Writer | Reader | Lifecycle | Authority |
| --- | --- | --- | --- | --- | --- |
| Approved plan | `docs/slices/<id>/plan.md`, `test_plan.md` on `origin/main` | user, via PR merge | preflight, close | permanent | authoritative |
| Run state | `docs/slices/<id>/run/state.yaml` | workflow | workflow, hooks | per run, kept in git | advisory (CI re-derives) |
| Run ledger | branch `run/<slice-id>`, append-only | workflow | CI, stop limits, role-scope checks | permanent | authoritative for counts and phase boundaries |
| Approved contract delta | `docs/slices/<id>/contract_delta.yaml` on `main` | user, via plan PR merge | `gate` | permanent | authoritative for contract data |
| Pipeline credentials | see "Pipeline credentials" | user | as listed there | rotated by the user | authoritative |
| Independent plan review | `docs/slices/<id>/plan_review.md` plus the CI `plan-review` artifact | CI `plan-review` job (author answers in a separate section) | plan PR check, user | permanent | authoritative only when produced by CI and bound to the plan's digests |
| TCR, DEV, escalation records | `docs/slices/<id>/run/` | implementer, test author, reviewers | workflow, reviewers, user | permanent | authoritative for the review |
| Authoritative evidence | CI artifact of `execute`, judged by `verify` | CI runner | `verify`, user | GitHub artifact retention | authoritative for tests that exist on `main`; new tests from the first nightly run after merge |
| Local evidence | `artifacts/rogue-tests/` | harness on the agent's machine | the agent | per run | advisory only |
| Gate code and thresholds | `scripts/`, `security/`, `.github/workflows/` on `main` | full slices only | CI gate job | permanent | authoritative |

### User actions draft
On `main`, require a PR, one approving review and the `gate`, `verify` and (when present)
`candidate-gate` and `plan-review` checks; reserve updates to `main` to the owner; a ruleset
forbidding force-push and deletion on `run/*`; create the agent's GitHub identity; add the CI model
API key as a secret available only to the `plan-review` job's environment.

### Pipeline self-test drafts
#### Pipeline self-tests — Increment 2 (seeded faults, run on a fixture slice)
Each seeded fault must end in a stop or a failure at the named point, never in a handoff.

| # | Seeded fault | Must be caught by |
| --- | --- | --- |
| P-1 | implementer edits a test file | path-scope check after the implement phase |
| P-2 | implementer edits an `expect:` block | path-scope check |
| P-3 | test author's new test fails for the wrong red-phase reason | test-phase exit gate |
| P-4 | a TCR loosening an assertion is accepted | anti-weakening check (base rerun or weakened-assertion list); the PR body shows it |
| P-5 | 3rd accepted TCR in a slice / 4th | the run continues / stop limit, `escalation.md` written, notification sent |
| P-6 | a plan decision has no implementation | code-vs-plan reviewer, close fails |
| P-7 | a material deviation filed as minor | code-vs-plan reviewer reclassifies it, the run stops |
| P-8 | compose gains a key mount | `qa-deploy` |
| P-9 | plan files differ from `origin/main` | preflight refuses to start |
| P-10 | Codex unavailable | the Claude fallback runs; the report names the fallback and the reason |
| P-11 | the agent edits `services/` with no active approved slice | Claude Code hook refuses |
| P-12 | the agent commits before `slice-close` passes | Claude Code hook refuses |
| P-13 | 2nd accepted TCR on the same test / 3rd | continues / stop limit |
| P-14 | 3rd review-fix round / 4th, or the same finding raised twice | continues / stop limit |
| P-15 | 5th full gate run without convergence / 6th | continues / stop limit |
| P-16 | run resumed after an escalation answer | restarts at the recorded phase; no phase skipped or repeated (state checked against CI) |
| P-17 | the agent edits a frozen slice bundle | Claude Code hook refuses |
| P-18 | a commit message with a `Co-Authored-By` trailer | Claude Code hook and git hook refuse |
| P-19 | a reviewer's input includes the implementer's reasoning or the run directory | isolation check fails the run |
| P-20 | the code-vs-plan reviewer is configured with the implementer's model | preflight refuses |
| P-21 | the agent's narrative contradicts the evidence (for example "0 TCRs" with 2 filed) | the report uses evidence values and flags the contradiction |
| P-22 | the plan threat reviewer raises a question the plan does not answer | plan PR check fails |
| P-23 | the implementation adds a key mount the plan's asset table does not list | `slice-close` fails (and `qa-deploy`) |
| P-24 | the plan PR is opened while `plan_review.md` has an open finding, or without `plan_review.md` | `slice-grill` refuses; the plan PR check fails |
| P-25 | the plan reviewer's input includes the author's reasoning or transcript, or the reviewer is the author's model | isolation check fails the review |
| P-26 | a fixture plan with seeded gaps (a missing evasion, an untested decision, an unlisted asset, a contradiction with `requirements.md`) | the reviewer must find every blocker-class gap and at least 80% of the rest; a lower rate, zero, or a missing result blocks its use (PR-19) |
| P-27 | the adversarial gate reviewer finds an evasion | handoff is blocked until a test for it exists and fails without the fix |
| P-28 | the 3rd plan review round / 4th, or the same plan finding twice | continues / stop limit, `escalation.md` |
| P-29 | the implementer stages, commits or leaves untracked a test change; deletes a TCR record; force-pushes the ledger | phase-commit scope check; clean-tree check; counts from the ledger; ruleset refuses (PR-14) |
| P-30 | the ledger branch is missing or unreadable | the run stops |
| P-31 | the agent identity tries to approve or merge its own PR | GitHub refuses (PR-08) |
| P-32 | an agent role reads the owner's credential files | hook refuses |
| P-33 | `plan_review.md` edited after the review; plan files changed after the last round; a finding marked resolved without a reviewer round | `plan-review` check fails (PR-15) |
| P-34 | the reviewer errors (expired login, refused model, empty output) | recorded as "review did not run", never as "no findings"; fallback per D11 |


### Increment 3 — pilot acceptance
- The pilot slice goes from grill-me to a pushed branch with no manual steps other than the plan
  PR merge.
- Its own test plan uses the expected-outcome table, including the corrected `M2-T7` and the
  E2E tests on the deployed stack for REQ-SEC-K1, K2 and the Redis requirement (REQ-SEC-S1, added by
  the pilot).
- Every place the pipeline stopped, misbehaved or needed help is recorded and fixed or logged.


### Derivation drafts for these tests
| Test | Evasions considered → covered by | Missing vs zero | Wrong-reason pass | Wrong-reason fail | Boundary |
| --- | --- | --- | --- | --- | --- |
| T-14 | rn, del, symlink, mode change → fixtures | n/a: every diff gets a lane | n/a | n/a | 60/3 fix; 61 or 4 full slice |
| T-15 | src (PR copy of the classifier) → `main`'s copy used | n/a | n/a | n/a | n/a |
| T-16 | src (test passes on base because it was never run) → run evidence required | missing base run fails | fails on base for another reason → fixture | flaky failure → rerun once, both must fail the same way | n/a |
| T-17 | del of covered lines (deletions) → structural diff, not line coverage, judges them | missing coverage data fails | n/a | n/a | 100% required: 1 uncovered line fails |
| T-18 | one fixture per missing item; emp sections → fixture | missing file fails | n/a | n/a | n/a |
| T-19 | trailer in body vs footer, other casing → fixtures | n/a | n/a | n/a | n/a |
| T-20 | candidate gate that passes only on the fixtures → registry negatives are kept on `main` only | missing negative-control result fails | n/a | candidate gate crashing counts as failing its controls | n/a |
| T-28 | workflow skip, name collision, fork → GitHub fixtures | n/a | n/a | GitHub outage → job error, never pass | n/a |
| T-29 | cmt, other run, committed artifacts → fixtures | missing SHA or run id fails | n/a | n/a | n/a |
| T-30 | rn of section → anchored heading | missing section fails | n/a | n/a | n/a |
| T-31 | emp table, "none" without reason → fixtures | missing table fails | n/a | n/a | n/a |
| T-32 | asset added under a new name → content (T-26) and diff both checked | n/a | n/a | n/a | n/a |
| T-33 | gate added under a new Makefile name → registry built from the Makefile | missing registration fails | n/a | n/a | n/a |
| T-34 | survivors relabelled equivalent → each needs a reviewed justification | see T-41 | n/a | n/a | 79.99% fails, 80% passes |
| T-35 | mapping that points at an always-failing test → the killing test must fail with its declared signature | no mapped test = failure | killed by a crash → signature checked | n/a | n/a |
| T-36 | test mapped to the wrong file → nightly full-suite comparison | missing mapping fails | n/a | n/a | n/a |
| T-37 | decrease inside a full slice without delta → fixture; tm (history rewritten) → history from `main` | missing history fails | n/a | n/a | 84→85 ok, 85→85 ok, 85→90 fails |
| T-38 | fixture removed or renamed → corpus list on `main` | missing fixture fails | n/a | n/a | n/a |
| T-39 | section present but empty → fixture | missing section fails | n/a | n/a | n/a |
| T-40 | emp column, "n/a" without reason → fixtures | missing set member fails | n/a | n/a | n/a |
| T-43 | extra entry, changed holder, older plan revision → fixtures | missing delta file fails any contract-data change | n/a | n/a | n/a |
| T-44 | Docker socket under another path, host mount, privileged, unpinned image → fixtures | n/a | PR harness evidence for an existing test → ignored | controller failure is an error, not a pass | n/a |
| P-1, P-2, P-29 | staged, committed, untracked, deleted, force-pushed → P-29 | missing ledger → P-30 | n/a | n/a | n/a |
| P-3 | red phase failing on import error → signature compared | missing red evidence fails | n/a | n/a | n/a |
| P-4 | loosened assertion hidden in a helper → base rerun | n/a | n/a | n/a | n/a |
| P-5, P-13, P-14, P-15, P-28 | counter reset by deleting records → ledger | missing ledger → stop | n/a | n/a | at limit continues, limit + 1 stops |
| P-6, P-7 | decision implemented in an unrelated file → reviewer maps decision to code | n/a | n/a | n/a | n/a |
| P-8, P-23 | mount added under a new name → content scan | n/a | n/a | n/a | n/a |
| P-9 | plan edited after merge on the branch → digest compare | missing plan on `main` refuses | n/a | n/a | n/a |
| P-10, P-34 | reviewer error read as "no findings" → P-34 | empty output = did not run | n/a | n/a | n/a |
| P-11, P-12, P-17, P-18, P-32 | edits via shell instead of the edit tool → hooks on shell commands too | n/a | n/a | n/a | n/a |
| P-16 | resume at a later phase → ledger | missing ledger → stop | n/a | n/a | n/a |
| P-19, P-20, P-25 | reasoning passed via a file in the input set → input list fixed by the script | n/a | n/a | n/a | n/a |
| P-21 | narrative numbers in a table → every number from evidence | n/a | n/a | n/a | n/a |
| P-22, P-24, P-33 | report edited, stale digest → P-33 | missing report fails | n/a | n/a | n/a |
| P-26 | rate computed over fewer seeds → seed list on `main` | missing result blocks | n/a | n/a | 80% passes, below fails; any blocker-class miss fails |
| P-27 | evasion test added but passing without the fix → must fail without it | n/a | n/a | n/a | n/a |
| P-30 | n/a | the point of the test | n/a | n/a | n/a |
| P-31 | approval through the API vs UI → both refused by the ruleset | n/a | n/a | n/a | n/a |
