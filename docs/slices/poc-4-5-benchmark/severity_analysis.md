# Why reviewers mis-rate severity: analysis for decision concern 8

This note is for the owner. It looks at every finding in the slice 4.5 benchmark whose severity decided whether
it counted, finds the patterns behind the wrong ratings, proposes at most two general wording changes, and
plans one measurement of them. It is a read-only analysis. Nothing in the repository was changed, and no
reviewer or model was called.

It is step 1 of decision concern 8 (slice 4's decision page), written before the measurement of step 3, whose
result is in the [benchmark report](benchmark_report.md#severity-decision-concern-8): candidate 1 was
measured and not adopted. It is kept here as written, except one corrected count (46 completed reviews,
not 45).

Sources: `docs/slices/poc-4-5-benchmark/benchmark_report.md`, `benchmark_results_B.jsonl` (306 findings in 46
completed reviews), the `confirmation_*.jsonl` files, `tests/review_benchmark/answer_key.yaml` and its plants, the
prompt builder in `scripts/run_review_benchmark.py` and `scripts/run_independent_review.py` as they were at
`0727670`, the commit of the runs, the stage lists at `04f8df4`, and the `AGENTS.md` each case received.

---

## 1. The short answer

- **Seen but rated below high: 7 findings in 7 reviews.** These are RM-3 three times, RM-4 three times and
  FS-2 once. In all 7 the reviewer's failure scenario stops at a visible symptom: "the trace report gives a
  misleading picture", "a failure shows up in the wrong job", "a slower runner gets less tolerance". None
  follows the gap to what it lets merge. In 6 of the 7, the rules the reviewer was given supported the low
  rating (more on this in section 2). In all 7, the stage list's "Blocks at this stage" section is narrower
  than the list question that found the defect.
- **Blocking or high but matching no planted defect: 104 findings** (40 blocking, 64 high). I judge all 104 to
  be real problems of the reviewed commits. The benchmark's "false blockers" are mostly not false. For example,
  RM-5's change really does mount the issuer's private-key directory into the rogue container. Of the 104:
  - 71 are rated within what the rule text supports;
  - 3 have the right severity but the wrong line or ID;
  - **20 are rated above it:** 9 contradictions with no harmful outcome, 6 gate gaps that need a later,
    unforeseen mistake, 2 gaps that a CI gate already fails on, and 3 others;
  - **10 are rated below it:** 8 requirements that lose their only working proof, and 2 tests that pass
    without exercising what they claim.
- **The same defect gets different severities in different reviews.** This happened for 16 of the 39 defects
  that more than one review found. In 15 of those the difference crosses a line that changes what must be
  fixed.
- **The author's hypothesis holds for RM-3 and RM-4, but not as a general rule.** In those six reviews, the
  present gap was rated medium or low. The ten blocking findings in the same reviews were gate gaps that need
  a later mistake (6) or text contradictions (4). Across the whole benchmark, though, most blockers describe
  present defects, and future-mistake scenarios were often rated high, not blocking.
- **A refined version fits all of the data.** Reviewers rate the *last sentence of the scenario they write*,
  and match it to the nearest phrase of the severity text. 34 of the 60 blocking findings quote a blocking
  phrase ("contradict" 19 times, "false green" 8 times, the stage's block 8 times). Only 10 of 73 high findings
  and 11 of 109 medium findings do.
  - A gate gap's first-order effect is already "CI stays green while X", which reads as blocking.
  - An enforcement or recording gap's first-order effect is only "a report shows it" or "a job is mislabelled".
    Its real effect, that an unproved requirement or a red gate merges, is one step further. The reviewers do
    not take that step.
- **Where the problem lies: mostly the wording and the inputs, with judgement noise on top.** All three mandates
  gave the same RM-3 and RM-4 ratings, so the mandate is not the lever. The drafted mandate (`open-B+list`)
  already says "at the severity its consequence earns", and it changed nothing.
- **Candidate 1 (recommended): "finish the scenario".** A procedure in the launcher's output section: rate the
  end of the scenario, not its first symptom, and count only checks you can point to as stopping it.
- **Candidate 2: "start from the commit as it stands".** It caps future-mistake scenarios and bare
  contradictions at high.
- **Measurement:** add candidate 1 to `open+list` only, and run the same 15 initial-review cases. That costs
  about USD 12–13 (the baseline cost USD 12.2 and took about 36 reviewer-minutes). Compare against
  `open+list`'s first runs. Fifteen runs can show a large harm or the mechanism working. They cannot prove a
  better detection rate.

---

## 2. What the reviewers were told about severity

Every review got the same **output section** from the launcher. At the commit of the runs it said, verbatim:

> `severity`: `blocking` meets the blocking criteria of the approved rules and is fixed before merge, or the
> owner decides. `high` is a real defect or false claim below that bar, for example a misleading document, new
> behaviour without a test or an untested fail-closed path; it is fixed in the same PR unless the owner defers
> it. `medium` has clear value (robustness, diagnosability, naming) and is fixed, or deferred with a tracking
> issue. `low` (style, preference) is the author's choice.

**The "approved rules" were each case's own `AGENTS.md` at its base commit** (`prepare_case` in
`scripts/run_review_benchmark.py`: "Every case gets the rules of its base"). No case got today's text, which
has four severity levels, blocking for "a secret written into logs", and the rule that a checklist's "Blocks"
section also blocks.

| Cases | Base | Severity text in the rules the reviewer got |
| --- | --- | --- |
| RM-1, RM-2, CL-3 | `6e8b2cb`, `7d0de8b`, `6feedfa~1` | **None**: no `AGENTS.md` existed, so the prompt said "(no rule files at this commit)". "The blocking criteria of the approved rules" pointed at nothing; only the list's Blocks section was left. |
| RM-5 | `e11d780` | An `AGENTS.md` with no review or severity section at all. |
| RM-3, RM-4 | `8faeea9`, `f6a9524` | "Only these block: a concrete false green or an OPL-005-class miss inside the threat model, with a failure scenario; a contradiction; an approved decision without a test. **Everything else is advisory. It is listed once and is not fixed by default.**" RM-3's base also says: "**Coverage gaps are reported but do not fail the build.**" |
| RM-6, PB-*, FS-*, RC-1, DC-1, CL-1, CL-2 | `c4f9ca2`, `e842e97`, `d9395cf`, `dc4376e` | The same three criteria and "everything else is advisory". From `e842e97` on, the rules also hold the gap gate ("on a PR it also fails on a coverage gap the PR adds"). |

The **stage lists** (at `04f8df4`) each end with "Blocks at this stage". The bullets that matter here:

- requirements: "a requirement no test or check could verify"; "a new or changed requirement has no proof
  **while the change claims it is proved**". Question R5 asks more broadly: does *every* new requirement have a
  proof in `trace/tests.yaml`?
- code: "an asset reaching a non-holder, a fail-open path, a missing check at a trust boundary"; "a check or gate
  that passes on the case it exists to catch, or a new or changed one with no test that shows it failing".
  Question C10 ("does every new check run as its own required CI job?") has no Blocks bullet.
- plan-and-test-plan: "a decision or new requirement has no test, gate or named review question"; "a decision
  contradicts another…"; nothing on determinism.
- e2e-tests: "a test that can pass while the behaviour … is broken"; "**a requirement loses its only proof**";
  "a secret … in evidence".

The **mandates** say nothing about severity, with one exception: `open-B+list` says "Report each defect once, at
the severity its consequence earns; a preference never blocks." It rated RM-3 and RM-4 exactly as the other two
setups did.

---

## 3. Case labels used below

| Label | Kind | What it is |
| --- | --- | --- |
| RM-1 … RM-6 | historical miss | Real commits where earlier reviews missed a defect, replayed. RM-1: issuer key mounted into services that need only the public key (DPL-001). RM-2: token values in E2E evidence (DPL-002). RM-3: ten requirements added without proof (DPL-004). RM-4: a new gate run inside another CI job (DPL-005). RM-5: the diff-coverage gate's `--include` given twice, so the issuer was never measured (DPL-009). RM-6: untested refusal paths of the review launcher (DPL-010). |
| PB-1, PB-2, PB-3 | planted | PB-1: a requirement no test could verify. PB-2: a design hands the signing key to a non-holder. PB-3: a test plan retires a requirement's only proof. |
| FS-1, FS-2 | planted, from research sources | FS-1: an audit event would log the Jira credential. FS-2: a test plan waits for an asynchronous event with a bare `sleep 5`. |
| RC-1 | recheck | A false `fixed:` answer that the recheck must re-raise. |
| CL-1, CL-2, CL-3 | clean (no planted defect) | Real small commits: a new AGENTS.md rule (lock new issues), closing DPL-008, a README path fix. |
| DC-1 | decoy | A teardown with `|| true` that looks like a swallowed failure but is correct. |
| `short+list`, `open+list`, `open-B+list` | initial-review setups | Stage A's short three-question prompt; 4.1's open mandate (the launcher's default); 4.4's drafted mandate. All carry the case's stage list. |

Severity is shortened to B (blocking), H (high), M (medium) and L (low). "Detected" means a blocking or high
finding that confirmation matched to the planted defect.

---

## 4. Seen, but rated below high

These are the findings that describe the planted defect but were rated medium or low. Blind confirmation judged
only blocking and high findings, so these are the automatic scorer's "seen" matches; I read each one. In all 7
reviews, no other finding detected the defect.

| # | Case, setup, finding | Given | The reviewer's failure scenario | The real consequence | The text supports | Why it differs |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | RM-3 `open+list` F5 (`docs/requirements.md:292`) | M | The proof map shows REQ-SEC as unproved, or a later change drops the qa-deploy tests and nobody notices. | DPL-004: ten requirements merged with no recorded proof, and CI and review stayed green. Several of the ten are *not* checked by qa-deploy at all; the same reviews found K5, D2 and the "default deny" claim unproved. | At least **H** ("new behaviour without a test"). **B** under "an approved decision without a test", and under the requirements Blocks bullet "no proof while the change claims it is proved" (the change says "`make qa-deploy` checks both"). | It rates the symptom, a misleading map. The base rules said gaps do not fail. It took qa-deploy as the proof without connecting its own findings. |
| 2 | RM-3 `short+list` F7 (`requirements.md:299`) | M | qa-trace lists REQ-SEC as uncovered. A later reader cannot tell which check proves them; if qa-deploy is dropped, nothing shows the loss. | Same as row 1. | Same as row 1. | Same as row 1. It even notes "the change claims they are checked by make qa-deploy" and still rates M. |
| 3 | RM-3 `open-B+list` F8 (`trace/tests.yaml:1`) | M | "Anyone auditing coverage gets a misleading picture." | Same as row 1. | Same as row 1. | Same. It cites the base rule: "AGENTS.md says coverage gaps are reported but do not fail." |
| 4 | RM-4 `open+list` F11 (`unit-trust.yml:60`) | L | A test-lint failure shows up as a red `docs-check` job, harder to see and to make required. | DPL-005: gates ran inside a misleadingly named job, and no check was required to merge, so a red gate could be merged. Nothing in the copy shows that `docs-check` blocks a merge. | **H**: a real defect against the owner's question C10, and a misleading job name. **B** only if you follow it to "a red gate can merge", which needs a fact the copy does not show. | It rates the symptom (visibility, naming). The base rules had no own-job rule (DPL-005's own root cause: "placement and naming could at best be an advisory"). The Blocks section is silent. |
| 5 | RM-4 `short+list` F8 | M | "Branch protection requires 'docs-check'." A failure there reads as a documentation failure, and nobody can require test-lint on its own. | Same as row 4. In fact no check was required. | Same as row 4. | Same as row 4, plus **it assumed a fact outside the copy**: that branch protection exists. |
| 6 | RM-4 `open-B+list` F8 | M | The owner cannot see that test-lint is enforced; splitting `docs-check` later would drop the lint. | Same as row 4. | Same as row 4. | Same as row 4. |
| 7 | FS-2 `short+list` run 1, F3 (and F4, the same defect offered as a simpler alternative, L) | M | A fixed 5 s wait replaces a 30 s bounded poll, so a slow runner fails, and a missing event gives a confusing failure. | The test's result depends on timing. On a loaded runner, M5-T49 fails at random, and M5-T57 passes with its gateway leg missing. | **H** ("a real defect"; E2E question E4 says "no bare sleeps"). But medium's own example, "robustness", also fits, so the text is ambiguous. | It rates the symptom (robustness, diagnosability). The plan list's Blocks has no determinism bullet. In its repeat, the same setup rated the same defect **B**. |

Findings the scorer counted as "seen" that are really a different defect (shown for completeness):

- RM-3 `open-B+list` F6 and `short+list` F8 (M): REQ-SEC-K5's "limited to … at bootstrap" can never be checked.
  This is a PB-1-type defect, and the requirements Blocks bullet "a requirement no test or check could verify"
  makes it **B**. It is under-rated, although its scenario is a *future* change. That is a counter-example to
  the hypothesis.
- RM-3 `open+list` F4 and `short+list` F6 (M): REQ-SEC-D2's non-root lock is not enforced. A requirement with no
  working proof again, rated M.
- RM-6 `short+list` run 2, RM6-8 (L): interrupted log entries lack fields. It matched only through the key's
  loose "absence" clause ("no test" plus the file name). It is not the untested refusal paths, so L is fine.
- Medium and low findings in reviews that *did* detect their defect (PB-2 three times, PB-3 F5, FS-1 F3, FS-2
  `open+list` F6, RM-6 RM6-5, -L1 and -L2) are side points or duplicates, not misses.

**Factor counts for the 7:**

| Factor | Count | Which |
| --- | --- | --- |
| Rated the first symptom, not the consequence | 7 | all |
| Stage list asks the question, but its Blocks section is narrower or silent | 7 | R5 vs "while the change claims it is proved" (3); C10 has no Blocks bullet (3); no determinism bullet (1) |
| The rules at the case's base supported the low rating | 6 | RM-3 "gaps do not fail" (3, one cites it); RM-4 has no own-job rule (3) |
| Assumed something else proves or enforces it | 4 | qa-deploy taken as the proof (3); branch protection assumed (1) |
| Medium's examples matched the reviewer's wording (robustness, diagnosability, naming) | 4 | RM-4 (3), FS-2 (1) |
| Needs a further future mistake; outside the threat model | 0 | none: these are all present gaps |

---

## 5. Blocking or high findings that match no planted defect

### 5a. The 20 "false blocker" candidates of the first runs

These are blocking findings at no expected place, the report's count of 6, 7 and 7.

| Defect (cluster) | Findings | Real? | The text supports | Verdict |
| --- | --- | --- | --- | --- |
| c24: RM-5's change mounts the issuer's key directory, private key included, into `agent-a` and `rogue` | `short` F2, `open` F1, `open-B` F2 | **Yes.** Checked: the diff `e11d780..4b808cb` adds `../capiss_keys` to both services. This is the DPL-001 class. | B (asset at a non-holder) | correct ×3 |
| c23: RM-5: tool-b accepts a block that widens `res` whenever its own `token_id` carries an issuer marker, so any holder can reuse a known id and reach `/secret` | `short` F1, `open` F2, `open-B` F1 | Yes. Checked: `server.py:244–249` looks up the block's own `token_id`. Three independent reviews agree. | B (fail-open in a security decision) | correct ×3 |
| c25: RM-5: none of the new gates has a test that shows it failing | `short` F3, `open` F3, `open-B` F3 | Yes. This is DPL-009's own root cause. | B (code Blocks: "no test that shows it failing") | correct ×3 |
| c1: RM-1: tool-b's new signature and authority checks have no rejecting test | `open` F2 | Yes | B under code Blocks, if "check" covers the system's own checks; H if it means only QA gates | defensible (the text is ambiguous) |
| c12: RM-3: qa-deploy reads only some compose keys (no `volumes_from`, `secrets`, `configs`, `service:` namespaces), so "default deny" is overclaimed | `open-B` F1, `short` F1, `open` F1 | Yes. Checked in `qa_deploy.py` at `ce465a8`. | H: a false claim now; the false green needs a later change that uses a key the repo never uses | **over ×3** (future mistake) |
| c13: RM-3: named volumes are parsed from the wrong field | `open-B` F2 | Yes | H (harm needs a later named volume at an asset path) | **over** (future mistake) |
| c17: RM-4: test-lint sees only loose regexes written as `'(…|…)'` | `open` F1, `open-B` F1 | Yes | B by the code Blocks bullet ("passes on the case it exists to catch"); H by proportion, since the harm needs a later check written in the other form | borderline ×2 |
| c18: RM-4: the lint lets through undeclared alternations that D3 forbids, and the harness still has some | `short` F1 | Yes, but the change's own "Known limits" says so | H | **over** (contradiction) |
| c19: RM-4: the slice template says test-lint rejects `401|403`, but it does not | `open` F2 | Yes | H ("a misleading document"); B only by the letter of "a contradiction". The other two setups rated it H. | **over** (contradiction) |
| c46: CL-1: a rule added without a plan, a recorded user request, a review or a log entry | `short` F1 | Yes | H: none of the blocking criteria | **over** (process step taken as blocking) |
| c47: CL-1: the new rule has no test, gate or review question | `open-B` F1 | True but minor | L–M: the plan list's Blocks bullet applied word for word to one rulebook sentence | **over** (Blocks applied literally) |

So of the 20: **9 are correct, 1 is defensible, 2 are borderline, and 8 are over-rated. None is a non-defect.**

### 5b. All 104 unmatched blocking or high findings, grouped by defect

The table below covers every finding, including repeats (r2) and the no-defect cases. "Real?" is my judgement. I
checked five clusters in the repository (c6, c7, c12, c23, c24); for the rest I relied on the evidence the
reviewers quote and on agreement between independent reviews.

| Cluster | Case | Findings (setup, severity) | Paraphrase | Real? | Supported | Why the rating differs |
| --- | --- | --- | --- | --- | --- | --- |
| c1 | RM-1 | open F2 B; short F5 H; open-B F4 H | tool-b's new token checks have no rejecting test | yes | B or H | ambiguous "check or gate"; **inconsistent** |
| c2 | RM-1 | open F3, short F2, open-B F2: H | the agent-a demo client still calls `/secret` without a token and exits | yes | H | — |
| c3 | RM-1 | short F3, open-B F3: H | the rogue demo client expects 403 and now exits | yes | M–H | — |
| c4 | RM-1 | open F4, short F4: H | identity tests loosened to accept 401 now pass on "missing token" and never exercise identity | yes, now | **B** (a test passing while what it claims is not exercised) | **under**: the scenario is told as a future regression |
| c5 | RM-2 | open-B F1, open F1, short F1: B | M2-T5/T7 probe a fresh container with no mounts, so they pass by construction | yes | B | — |
| c6 | RM-2 | open-B F2 B; open F4 B; short F4 H | M3 guards run `$(…)` with literal quotes, so every M3 test fails and the M3 requirements lose their working proof | yes (checked) | B (E2E Blocks: "loses its only proof") | short **under**; inconsistent |
| c7 | RM-2 | open-B F3, open F2, short F2: B | guards end in `echo`/`printf`, so they always pass | yes (checked) | B | — |
| c8 | RM-2 | open-B F5, open F5, short F5, short F6: H | M2.5-T1/T3 fail exactly when the boundary works; T2 never runs its script | yes | **B** (a requirement loses its only working proof) | **under ×4**: a red test reads as "someone will notice" |
| c9 | RM-2 | open-B F6, open F7, short F9: H | M1-T4's read attempt removed, guard weakened | yes | H | — |
| c10 | RM-2 | open-B F9, open F8, short F10: H | the Envoy SVID "refresh" rewrites files Envoy never reloads | likely (not run) | H | — |
| c11 | RM-2 | open F6, short F7: H | server-log guards not tied to this test's attempt | yes | H | — |
| c12 | RM-3 | three B (see 5a) | qa-deploy is not default deny | yes | H | **over** (future mistake) |
| c13 | RM-3 | open-B F2 B; short F3 H | volume target parsed from the wrong field | yes | H | open-B **over** |
| c14 | RM-3 | short F2 B; open F2 B (open-B F5: M) | holder lists contradict: Docker-socket holders reach every asset, yet K1–K7 leave out spire-agent | yes | H by consequence; B by the letter of "a contradiction" | **over ×2** (contradiction); inconsistent |
| c15 | RM-3 | open-B F3 H | a mount of a file inside a directory asset is not detected | yes | M–H | — |
| c16 | RM-3 | open F3 H (open-B F9, short F9: M) | close-out missing; STATUS still says 1B is next | yes | H (misleading document) | inconsistent |
| c17 | RM-4 | open F1, open-B F1: B | lint misses the plain regex form | yes | B or H | borderline |
| c18 | RM-4 | short F1 B | undeclared alternations pass despite D3 | yes, disclosed | H | **over** (contradiction) |
| c19 | RM-4 | open F2 B; short F2 H; open-B F2 H | the template overclaims what the lint rejects | yes | H | open **over**; inconsistent |
| c20 | RM-4 | open F3 H; short F3 H (open-B F5: M) | T-22 claims 24 tests, but the test asserts 23 | yes | H | inconsistent |
| c21 | RM-4 | open F5, short F4, open-B F3: H | close-out missing, with no E2E run or mutation score recorded | yes | H | — |
| c22 | RM-4 | open F6, short F5: H (open-B F6: M) | positive twins required by D5 are missing | yes | H (B arguable) | inconsistent |
| c23 | RM-5 | three B | `res` widening by reusing a marked `token_id` | yes (checked) | B | — |
| c24 | RM-5 | three B | private-key directory mounted into rogue and agent-a | yes (checked) | B | — |
| c25 | RM-5 | three B | new gates have no failing test | yes | B | — |
| c26 | RM-5 | short F4 H | the unit-traceability gate never checks that named tests exist | yes | H | — |
| c27 | RM-5 | short F7 H | the spec marks M4-CH1/D1 covered despite c23 | yes | H | — |
| c28 | RM-5 | open F4, open-B F5: H | the diff-coverage step has no merge base on a shallow checkout | likely (not run) | H | — |
| c29 | RM-5 | open F5 H | the mutation score drops untested mutants (today's gate counts them) | yes | H (B arguable) | — |
| c30 | RM-5 | open F9, open-B F6: H | the delegation path has no test | yes | H | — |
| c31 | RM-5 | open-B F4 H | **the planted defect itself** (`--include` twice), named at line 1791 | yes | H | right severity, wrong line |
| c32 | RM-6 | open RM6-1 H (three other reviews: M) | close-out missing, and half of slice 2 is absent | yes | H | inconsistent |
| c33 | RM-6 | short r2 RM6-1 H (three others: M) | the warning status `allowed_warning` was never probed; the launcher fails closed | yes | M | **over** (fails closed) |
| c36 | PB-1 | open-B F2 B; open F2 B; short F3 H | the new requirement has no proof entry | yes | H: the gap gate in CI fails on it, and the rules the reviewer had say so | **over ×2**: a gate already stops it (the inverse of RM-3) |
| c37 | PB-3 | open F3 H | the retirement also removes REQ-M2-R10/R11's proof and the only positive twin | yes | **B** (a requirement loses its only proof) | **under** |
| c38 | PB-3 | open F4, short F2: H | expiry (R16), missing-token and bad-request requirements lose their only proof | yes | **B**: the same class as the planted defect, which these reviews rated B | **under ×2** |
| c39 | PB-3 | short F3 H | retired IDs not listed; an AGENTS.md example breaks | yes | M–H (docs-check catches part) | — |
| c40 | FS-1 | open-B F2, short F2: H | ARCH-030 describes behaviour with no plan, requirement or test | yes | H | — |
| c41 | FS-2 | open-B F1, open F1, open r2 F3: B | H4 ("one JSON render") contradicts H1 ("a separate `--cid` render") | yes | B by the plan list's letter; H by consequence (an implementer must pick) | **over ×3** (contradiction) |
| c42 | FS-2 | short r1 F1 B; short r2 F2 B; open-B F3, open F2, open r2 F1: H | the "5 s covers the slowest flush seen" claim has no probe and contradicts the run's record | yes | H | **over ×2** |
| c43 | FS-2 | short r2 F1 B; short r1 F2, open F4, open r2 F4: H | M5-T57 has no presence check, so a missing gateway leg passes (pre-existing) | yes | B or H (a false green, but not new) | inconsistent |
| c44 | FS-2 | open r2 F5 H | M5-T50's "gateway absent" assertion passes by timing | yes | H | — |
| c45 | RC-1 | recheck-A, recheck-B: R2-1 B | the false fix, reported under a new ID instead of re-raising R1-1 | yes | B | right severity, wrong ID |
| c46 | CL-1 | short F1 B; open F1 H; open-B F2 H | a rule added without a plan, a recorded request or a log entry | yes | H | short **over** |
| c47 | CL-1 | open-B F1 B | the new rule has no test or review question | minor | L–M | **over** (Blocks applied literally) |
| c48 | CL-1 | open-B F3 H | the rule depends on an unprobed GitHub permission | plausible | M–H | — |
| c49 | CL-2 | short F1, open CL2-F1, open-B F1: H | DPL-008 closed on a GitHub setting with no recorded probe | yes | H | — |

CL-3 and the decoy DC-1 drew no blocking or high finding. On DC-1, the closest call was `short+list` F1 (L): a
leftover temp file holding the bearer token. The reviewer itself reasoned it down: the file stays in an
ephemeral container and never reaches the evidence. Any wording change must keep that reasoning.

### 5c. Counts

| Category | Blocking (40) | High (64) | Total |
| --- | --- | --- | --- |
| Real, rated within what the text supports | 19 | 52 | 71 |
| Right severity, wrong line or ID | 2 | 1 | 3 |
| **Over: a contradiction or misleading text with no harmful outcome** | 9 | — | 9 |
| **Over: a gate gap whose harm needs a later, unforeseen mistake** (2 of them borderline) | 6 | — | 6 |
| **Over: a gap that a CI gate already fails on** | 2 | — | 2 |
| Over: a Blocks bullet applied word for word | 1 | — | 1 |
| Over: a skipped process step taken as blocking | 1 | — | 1 |
| Over: fails closed, yet rated high | — | 1 | 1 |
| **Under: a requirement loses its only working proof** (a Blocks bullet names it) | — | 8 | 8 |
| **Under: a test passes without exercising what it claims** | — | 2 | 2 |
| Outside the threat model or production hardening | 0 | 0 | 0 |

"Outside the threat model" did not drive any rating in these two sets. The one hardening-style blocker, RM-6
`open+list` run 2 RM6-B1, is a confirmed match, so it is not counted here. Its scenario needs both a permissive
settings rule and an instruction planted in the copy, so it would be H at most.

---

## 6. The hypothesis, tested

The hypothesis: for a gap that exists now, reviewers write the mildest symptom; for a hypothetical future change
that slips past a check, they write the worst case and rate it blocking.

- **Confirmed for RM-3 and RM-4,** the two cases the owner named. In those six reviews:
  - every present gap got a symptom-level scenario and M or L;
  - the 10 blocking findings in the same reviews were 6 gate gaps that need a later mistake (c12 ×3, c13, c17
    ×2) and 4 contradictions (c14 ×2, c18, c19);
  - none was a present failure of the system.
- **Confirmed for all 7 seen-but-under-rated findings:** all are present gaps, and all stop at a symptom.
- **Not general:**
  - Of the 40 unmatched blockers, only 6 rest on a future mistake. 19 are present defects, correctly blocked
    (c5, c7, c23, c24, c25 …). The largest over-rated group is contradictions (9), which are present, not
    future.
  - Future-mistake scenarios were rated H at least ten times: c1 twice, c4 twice, c9 three times, c13, c15 and
    c26. The K5 finding was rated M with a future scenario.
  - Present defects whose failure is visible were rated H where a Blocks bullet makes them B (c8 ×4, c6, c37,
    c38 ×2).
- **Refined hypothesis:** the rating follows the end of the scenario the reviewer writes, matched to the nearest
  phrase of the severity text, whether the gap is present or future.
  - Ends that hit a named blocking phrase are rated B: "CI stays green while X", "the key reaches Y", "two texts
    disagree". 34 of the 60 blocking findings use such a phrase; only 21 of the 182 high and medium findings do.
  - Ends phrased as "a report shows the gap", "a job is mislabelled", "the suite is red" or "a reader is misled"
    are rated H or M.
  - A gate gap's *first* consequence is already a silent pass. A gap in enforcement or recording (a proof not
    recorded, a gate not separately required, a timing-dependent wait) has a first consequence that is only a
    visible signal. Its real consequence, an unproved requirement or a red gate merging, is a step the reviewers
    did not take, or took on an assumption (row 5's "branch protection requires docs-check").
- **An inversion supports this.** PB-1's "requirement without proof" was rated B twice: the reviewer could cite a
  rule the gap breaks now (the gap gate fails it). RM-3's identical class was rated M three times: the base rule
  said gaps do not fail. The ratings follow citable rule phrases, not what would merge unnoticed.

---

## 7. Wording, prompt, or judgement?

All three contribute. The wording and the inputs explain the systematic part; judgement explains the noise.

**Rule wording**

1. The severity examples name *kinds of symptom*: "misleading document", "robustness, diagnosability, naming".
   A reviewer who names the symptom finds a matching example. Rows 4–7 used medium's words.
2. "A concrete false green … with a failure scenario" does not say whether a scenario that needs a later mistake
   is "concrete". Every gate gap can be written as one (c12, c13, c17).
3. "A contradiction" blocks with no bar on its consequence, and it overlaps high's "a misleading document". The
   word appears in 19 blocking, 4 high, 9 medium and 2 low findings. For example, the README contradicting the
   code was rated M (RM-1 `open-B` F9), while a template contradicting a test plan was rated B, H and H (c19).
4. RM-3's base rules said "coverage gaps are reported but do not fail the build" and "everything else is
   advisory … not fixed by default". Under those rules M is a fair reading; it is DPL-004's own root cause.
   RM-4's base rules had nothing that made placement more than advisory (DPL-005's root cause).

**Prompt and inputs**

1. The same output section with three different mandates gave the same RM-3 and RM-4 ratings, so the mandate is
   not the lever. `open-B+list`'s "at the severity its consequence earns" changed nothing.
2. The lists ask the right questions, but their Blocks sections are narrower: R5 against "while the change claims
   it is proved"; C10 with no Blocks bullet at all.
3. The benchmark gave historical cases their base's rules. RM-1, RM-2 and CL-3 had none; no case had today's text.
   So the benchmark measures severity under a mix of rule texts. A change made only in `AGENTS.md` would not
   reach the historical cases.

**Reviewer judgement, where the rules are clear**

1. The e2e list says "a requirement loses its only proof" blocks, yet c8 and c38 were rated H eight times in
   total.
2. RM-3's reviewers found K5, D2 and the "default deny" claim unproved, but did not connect those findings to
   the "checked by qa-deploy" claim, which makes the requirements Blocks bullet apply.
3. The same defect got different severities in 16 of the 39 defects found more than once. Between two identical
   runs, 2 of 3 repeated pairs rated their defect differently; FS-2 under `short+list` went from M to B with
   nothing changed.

**Conclusion:** the fix belongs in *how* severity is decided, as a procedure every review receives, not in more
Blocks bullets. Some judgement noise will remain whatever the wording.

---

## 8. Candidate changes (at most two, both general)

Both would go in the launcher's output section, after the `severity` bullet (`_output_section()` in
`scripts/run_independent_review.py`). That is the only severity text every review receives identically, whatever
`AGENTS.md` its base holds. If adopted, the same text belongs in `AGENTS.md`, under "Review findings", as its home;
the output section already restates that section. For the measurement, only the output section changes.

### Candidate 1 (recommended): finish the scenario

Exact text:

> Choose the severity from the end of the failure scenario, not its first symptom. Start from the reviewed
> commit as it stands and follow the scenario to what it lets reach the integration branch, the published
> evidence or a non-holder if nobody fixes it. The ends that matter: a requirement or decision left without a
> working proof; a test, gate or check that would pass while what it proves is broken, or whose failure would
> not stop the merge; a key, secret or token at a non-holder. A report that lists the gap, a failure under
> another job's name, or a reader who might notice is a symptom, not a stop. Something stops the problem only if
> you can point to it in the copy or the evidence: a test, a gate with the CI job that runs it, a required check.
> A finding with one of those ends is high at least, and blocking when it meets a blocking criterion.

Expected to rate **up**:

- the targets, RM-3 ×3 and RM-4 ×3: an unproved requirement merges; a red lint may not stop the merge, because
  nothing in the copy makes `docs-check` required;
- c8 ×4, c6 (short), c37 and c38 ×2, from H to B;
- c4 ×2, from H to B;
- RM-3's K5 and D2 findings, from M to H;
- possibly FS-2 row 7, if the reviewer follows the wait to M5-T57 passing without its gateway leg.

Expected to rate **down**:

- c36 ×2, from B to H: the CI gap gate stops it;
- c39, from H to M: docs-check catches it;
- c33, from H to M: it fails closed, so nothing wrong merges.

Could break (watch these):

- On DC-1, CL-1 and CL-2, the medium "no close-out record" findings could be stretched into "a decision without
  proof". That would add false alarms.
- c2, c3 and c10 (broken but untested demo behaviour, H) could be stretched to B. The list of ends leaves them
  out on purpose: no test claims those behaviours.
- No baseline detection depends on a rating this would lower.

### Candidate 2: start from the commit as it stands

Exact text:

> A blocking scenario starts from the reviewed commit as it stands, or from a next step the plan or task names.
> When the harm needs a further mistake that nothing in the copy foresees (a later change adds an unusual
> mount, a later edit drops a check), the finding is a real gap and is high at most, unless the stage
> checklist's Blocks section names it. A test, gate or check that cannot fail on the case it exists for is wrong
> today, even when the harm it hides comes later. A contradiction blocks only when acting on one of its
> statements leads to one of the ends above; one that only misleads a reader is a misleading document, high.

Expected to rate **down** from B to H:

- c12 ×3, c13 (open-B), c14 ×2, c18, c19 (open), and c42 twice;
- the matched RM6-B1: RM-6 run 2 stays detected through its high RM6-H1.

Probably unchanged: c41 (acting on H4 drops a guard) and c17 (the code Blocks names it).

Unchanged correct blockers:

- c5 and c7, through the "cannot fail on its case" sentence;
- c23 and c24 (present defects); c25 and c1 (named in a Blocks section);
- every planted detection.

Limits:

- It does not fix c46 or c47.
- It changes "false blockers" and "detected by a blocking finding" only. The benchmark's detections and false
  alarms count high as well, so they would not move. Measuring it needs a hand-judged blocker count.

### Alternatives considered and rejected

- **Make R5 and C10 blocking.** This is the case-specific fix the owner rejected. It reaches 6 of the 7 seen
  findings and none of the 10 other under-rated or 20 over-rated findings.
- **"A 'no' to any `[S:owner]` checklist question is high at least."** General in form, but still tied to the
  lists. It would not reach c8, c38 or c4.
- **"Anything wrong today is high at least."** It would catch rows 1–7, but it would also lift most of the 109
  medium findings, which are present small deviations, including DC-1's and CL-2's. That means more false
  alarms.
- **A one-line "rate by consequence".** It already failed in `open-B+list`.

---

## 9. Measurement plan

| Item | Plan |
| --- | --- |
| Variable (one) | Candidate 1's paragraph added to the output section. The runner today swaps only mandates (`configuration()`), so it needs a small option to add this text, with its own tooling test. |
| Configuration | `open+list` (the launcher's default), run as a new configuration, for example `open+list+sev`. Everything else fixed: 4.1's mandate, lists at `04f8df4`, answer key v2 and match rule, `claude-opus-5-5` at high effort, each case's base rules, evidence off, the same CLI version as the canary (the runner refuses otherwise; if the CLI has changed, rerun one canary pair first). |
| Cases | All 15 initial-review cases `open+list` ran: RM-1 to RM-6, PB-1 to PB-3, FS-1, FS-2, CL-1, CL-2, CL-3, DC-1. The no-defect cases count detections and false alarms together. Not RC-1, which is a recheck. |
| Baseline | `open+list` first runs: detected 7 of 11 (5 by blocking); seen 9 of 11; false alarms 2 in 4 no-defect reviews (CL-1 F1 H, CL-2 CL2-F1 H; none on CL-3 or DC-1); 7 false-blocker candidates; FS-1 withheld by the publication check. |
| Confirmation | The same match rule. Re-export the baseline's and the new run's blocking and high findings together, under fresh tokens, and confirm all of them blind. If only new findings are exported, the confirmer knows which setup produced every one of them. Add a Sonnet second confirmer on 10 findings (2 calls). |
| Cost | The baseline's 15 reviews cost USD 12.2 by the runs' own estimate: USD 0.10 (CL-3) to 1.93 (RM-3), mean 0.81, about 36 reviewer-minutes. The six historical cases took about USD 9 of that. Plan USD 12–13, with a cap of USD 15 to cover one retry of a failed or withheld review (1 of 15 last time). |
| "Better", fixed before the run | (1) RM-3 and RM-4 both detected by a confirmed match; the baseline had 0 of 6 such reviews at high across all three setups. (2) No baseline detection lost (RM-1, RM-2, RM-6, PB-1, PB-2, PB-3, FS-2); a failed or withheld review is rerun once. (3) No blocking or high finding on DC-1 or CL-3. (4) No more than one extra blocking or high finding on CL-1 and CL-2 together, each read by hand. |
| Outcomes | **Worse:** (2) or (3) broken. **Inconclusive:** one of RM-3 and RM-4 detected and the guards hold; then repeat RM-3, RM-4, DC-1 and CL-2 once (about USD 4.5) before the owner decides. Also record by hand the new severities of the recurring under-rated (c8, c38, c4) and over-rated clusters, as a diagnostic. |

**What about 15 reviews can and cannot show**

- **It cannot prove a better detection rate.** A rise from 7 to 9 of 11 still has overlapping intervals (31–89%
  against 59–98%). Paired by case, 2 new detections and none lost gives a one-sided p of 0.25; even 4 gives
  0.06.
- **A single flip is within noise.** Two identical runs disagreed on 2 of 3 repeated pairs.
- **It can show a large harm:** new alarms on the decoy, or lost detections.
- **It can show whether the mechanism works:** whether the RM-3 and RM-4 scenarios now name the end ("an unproved
  requirement merges", "a red lint can merge") instead of the symptom. Both flipping, against 0 of 6 before, is
  consistent with the mechanism, but it is not proof.
- **It cannot show:**
  - the false-alarm rate, from 4 no-defect reviews;
  - the effect under today's `AGENTS.md`, because historical cases still get their base's rules;
  - the effect with the other mandates;
  - whether it carries over to other kinds of defect.
- **A cheaper complementary check, not a replacement:** give each baseline finding's text to a fresh session with
  the new paragraph, and ask only for a severity. It isolates the wording from which findings a review happens
  to make, but it cannot test "finish the scenario" against the copy.

---

## 10. Where I was unsure

- **Whether each finding is real.** I checked c6, c7, c12, c23 and c24 in the repository. For the others I relied
  on the evidence the reviewers quote and on agreement between independent reviews. c10 (Envoy reloads) and c28
  (shallow checkout) rest on tool behaviour I did not run.
- **The "seen" findings were never blind-confirmed.** Only blocking and high findings were exported. I read each
  seen match; the scorer's absence clause produces at least one mechanical match (RM6-8).
- **"Supported severity" is my reading of texts the reviewers themselves read differently.** Where the letter and
  the consequence disagree (c1, c14, c17, c41, c43), the table gives both.
- **The grouping into clusters, and the up and down predictions for both candidates, are my judgement,** not
  measurements.
- **Context:** today's repository has gates for both historical misses: the gap gate (DPL-004) and
  `gate-consistency` (DPL-005). The benchmark asks whether a reviewer catches these classes without those gates.
