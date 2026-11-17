# Benchmark report — stage B of the review benchmark (slice 4.5b)

The results of slice 4.5's stage-B benchmark, for the owner's choice of the default review setup and of the mandate
wordings (S45-D8): what ran, the counts per configuration, what the counts can and cannot show, each confirmed
detection with the checklist question behind it, and the misses. The runner's own report, built by
`python3 scripts/run_review_benchmark.py --report --stage B`, is kept verbatim at the end.

## What ran

- **Key and rule:** answer key `7ef0a579…` (version 2, 17 cases), match rule `0db53541…`, committed before any run;
  stage lists at `04f8df4` (after 4.4's critique and implementation review). Version 3 (`ed4b5e0a…`, match rule
  `9605cb43…`) adds RC-2, a recheck case whose answers hold (decision concern 4), with its rule, before its runs; it
  reads version 2's results unchanged. Version 4 (`5b9d6382…`, same rule), before any of their runs, raises the budget,
  adds decision concern 8's configuration `open+list+sev` and fixes that measurement's criteria. Round 2 of slice 4
  (the owner, 2026-11-14): version 5 (`2d7c5cf6…`, match rule `36d2c150…`; R2-9) counts a match rated medium as detected, and a medium finding on a
  no-defect case as a false alarm, since R2-1 has medium findings fixed; version 6 (`ba6975d4…`, match rule
  `422d32c2…`), before their runs, adds the recheck cases RC-3 and RC-4 (R2-10) and the rule's sentence for them;
  version 7 (`0ee2ad14…`, same rule; round 3 of slice 4, the owner, 2026-11-17), before its runs, only raises the
  budget from 85 to 95, so version 6's results are read with it and keep their scores. The runner's report below is
  built with version 7. Decision concern 13's wording (the owner, 2026-11-16) is in the
  launcher's output section, not in the key, so the key and its rule did not change for RC-3's second runs; their
  prompts did, so the runner ran them as new reviews.
- **Reviewer:** Opus (`claude-opus-5-5`), initial reviews at high effort, rechecks at medium, CLI 2.1.321 (RC-2 and
  later runs: 2.1.323, after its own canary); Sonnet (`claude-sonnet-5-5`) only as the second confirmer.
- **Calls:** 57 of the 60 allowed: 6 for three canary pairs (see below), 45 first runs, 4 repeats, 2
  second-confirmer sessions. The failed-Read probe and the planting of FS-1 and FS-2 ran outside the budget, as
  S45-D1 allows. On 2026-11-13 the budget was raised to 85, for a canary pair under CLI 2.1.323, RC-2's two runs
  and decision concern 8's measurement: the owner approved that measurement beyond the 60 calls ("complete it and
  do not wait for my approval"); see the decision page. The canary pair under 2.1.323 and RC-2's two runs brought
  the count to 61, and the measurement's 15 runs, with no retry, to 76. Its second confirmer and repeat did not run,
  and the hard stop was lowered to 76, the calls used (decision concern 11 on the decision page). Round 2 (R2-10)
  raised it to 80 for RC-3's and RC-4's runs on both recheck wordings: 4 calls, all completed at the first try, so
  80 of 80 are used. The key keeps `budget: 85`; the runner refuses a run's budget above the hard stop, so the runs
  named `--budget 80`. They ran under CLI 2.1.323, the version of the fourth canary pair: the installed CLI had updated
  itself to 2.1.325, for which no canary has run, and a new pair would have cost 2 calls the owner did not approve.
  On 2026-11-16 the owner confirmed the budget of 85 (decision concern 11), so the hard stop is 85 and the runner
  checks the key's budget against it again; RC-3 then ran once more on each recheck wording, under decision concern
  13's wording, by a plain `--run`: 2 calls, both completed at the first try, so 82 of 85 are used. They ran under
  the same pinned CLI 2.1.323, whose canary is done. On 2026-11-17 the owner raised the budget from 85 to 95 for round
  3 of slice 4 ("Round 3 of slice 4: I approve R3-1 to R3-4, the budget 85 → 95, and the probe and replays"; the
  hard stop and key version 7), and RC-1 to RC-4 ran once each on `recheck-A`, the recheck wording the launcher
  ships (`--run --configuration recheck-A`): 4 calls, 83 to 86, each completed at the first try, so 86 of 95 are
  used. They ran under the same pinned CLI 2.1.323. Round 3's probe and replays ran through the launcher, not this
  runner, and are not counted here (the decision page, section "Round 3"). The fresh sessions that confirmed
  findings blind (below) are not reviewer calls and are not counted, as in round 2.
- **Configurations:** `short+list` (stage A's short prompt without its retired kinds sentence), `open+list` (4.1's
  mandate, the launcher's today), `open-B+list` (4.4's drafted initial mandate), `recheck-A` (4.1's recheck mandate)
  and `recheck-B` (4.4's drafted recheck mandate). Every configuration carries its case's stage list.

## Counts

Two sets of counts of the first runs, each labelled with its rule. **Under the rule of their runs** (blocking or
high), as each review was scored when it ran (match rules `0db53541…` and `9605cb43…`): the counts the decisions so
far were made on, unchanged. **Under R2-9** (blocking, high or medium; key versions 5 and 6, match rules `36d2c150…` and `422d32c2…`, which
differ only in the recheck sentence):
round 2 has blocking, high and medium findings fixed (R2-1), so a match rated medium is caught. The earlier results
are re-scored from the findings they recorded, with no reviewer call, into `benchmark_rescore_B.jsonl`
(`--rescore B`); the results file keeps the score of each run, and the re-score writes nothing unless, scored as the
earlier rule did, every review gives the score it was recorded with (62 of 62 do). RC-3's and RC-4's runs, and
round 3's, are scored under R2-9 only.

Detections are confirmed blind. Under the rule of their runs: the author's blinded verdicts (S45-D7) on 125 exported
findings: 29 match. Two of them, T008 and T047 (RM-6, `open+list`, its repeat), were first judged no match and changed
after unblinding, at the final review's challenge (FR-1): both meet the match rule's absence clause (an untested path
of the launcher, named anywhere in the finding) exactly as T043, which was accepted blind. The first-run counts do not
change; the repeat does. Under R2-9, the matches it adds were rated medium, so neither earlier export held them: a
third export (`--export-rescore`) holds the 146 findings no earlier export held, the 144 medium findings of every
completed defect-case review and RC-4's two re-raises, shuffled under fresh tokens without their configuration. A
fresh session, given a directory holding only a copy of that export and the committed match rule, judged them
(`rescore_confirmation.jsonl`): 15 match. It never saw the token map, the results or the prompts; the author started
it, as for decision concern 8's measurement (decision concern 3 keeps the author as the confirmer; this follows the
measurement's practice, and whether it stands is the owner's decision concern 16 on the
[decision page](../agentic-sdlc-poc/slice_4_decisions.md)). Every new detection below rests on such a verdict. RC-3's
two re-raises under decision concern 13's wording came after that export. They were appended to it as `M147` and
`M148`, by the runner's own selection of the findings no export held, under tokens after the last and without
reshuffling the 146 (`--export-rescore` reshuffles every row under new tokens, which would detach the verdicts
already given). A second fresh session, given a directory holding only those two rows and the match rule, judged both
a match (by its report it opened nothing else), on the rule's place-and-term clause: each re-raise is at
`AGENTS.md` lines 168 and 169 with its own words "step", "leave out" or "mechanism". The export shows a finding without
the recheck's accounting, so the confirmer cannot apply the recheck sentence itself; the ID it sees, R1-1, is the
earlier finding's. Whether these verdicts stand is also decision concern 16. Round 3's four new runs (2026-11-17)
came after these. Their four findings were appended the same way, as `M149` to `M152`, under tokens that are now
keyed by each result line's prompt identity (discovered issue 44), and a fresh session, given a directory holding
only those four rows and the match rule, judged M149 (RC-1's R1-1), M150 (RC-4's) and M152 (RC-3's) a match and
M151, RC-1's new R2-1, no match (by its report it opened nothing else); decision concern 16 applies to it too. Cost
and minutes include the failed reviews.

Stage A's results carry the retired kinds `blocking` and `advisory`, and `advisory` held medium and low alike, so they
cannot be re-scored: stage A stays as it was, its kind `blocking` the only detection. False alarms follow the rule's
own reasoning (S41-D13: whatever rating counts as a detection at the expected place counts as a false alarm
elsewhere), so under R2-9 a medium finding on a no-defect case is a false alarm, for every setup alike.

**Under the rule of their runs (blocking or high):**

| Configuration | Detected (of 11 defect cases) | 95% interval | By a blocking finding | False alarms (no-defect reviews) | False blockers (all completed reviews) | Unread files | Failed | Cost USD per detection |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `short+list` | 6 | 0.23–0.83 | 6 | 2 (4 reviews) | 6 | 42 | 1 | 1.91 |
| `open+list` | 7 | 0.31–0.89 | 5 | 2 (4 reviews) | 7 | 42 | 1 | 1.75 |
| `open-B+list` | 6 | 0.23–0.83 | 5 | 4 (2 reviews) | 7 | 50 | 1 | 2.02 |
| `recheck-A` | 1 of 1 | 0.02–1.00 | 1 | — (RC-2 failed) | 0 | 0 | 1 | 0.47 |
| `recheck-B` | 1 of 1 | 0.02–1.00 | 1 | 0 (1 review) | 0 | 1 | 0 | 0.49 |

**Under R2-9 (blocking, high or medium), with RC-3 and RC-4;** the recheck rows once with RC-3's first runs (R2-5's
wording, 2026-11-14) and once with its second runs (decision concern 13's wording, 2026-11-16); and `recheck-A` once
more over round 3's runs of RC-1 to RC-4 (2026-11-17). Since round 4's fix of discovered issue 56 (R4-3, `02281b0`)
the runner counts a case run again by its last run, so its own rows (its report, below) are the round-3 row for
`recheck-A` and the row of decision concern 13's wording for `recheck-B`. It gives no row per wording; the rows of the
earlier wordings are what the fixed runner gives over the results file as it stood after those runs (`e4943aa` for
R2-5's wording, `6627268` for decision concern 13's):

| Configuration | Detected (of 11 defect cases) | 95% interval | By a blocking finding | False alarms (no-defect reviews) | False blockers (all completed reviews) | Unread files | Failed | Cost USD per detection |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `short+list` | 9 | 0.48–0.98 | 6 | 4 (4 reviews) | 6 | 42 | 1 | 1.27 |
| `open+list` | 8 | 0.39–0.94 | 5 | 7 (4 reviews) | 7 | 42 | 1 | 1.53 |
| `open-B+list` | 8 | 0.39–0.94 | 5 | 6 (2 reviews) | 7 | 50 | 1 | 1.52 |
| `recheck-A`, RC-3 under R2-5's wording | 2 of 3 | 0.09–0.99 | 2 | — (RC-2 failed) | 0 | 0 | 1 | 0.50 |
| `recheck-B`, RC-3 under R2-5's wording | 2 of 3 | 0.09–0.99 | 2 | 0 (1 review) | 0 | 1 | 0 | 0.50 |
| `recheck-A`, RC-3 under decision concern 13's wording | 3 of 3 | 0.29–1.00 | 2 | — (RC-2 failed) | 0 | 0 | 1 | 0.33 |
| `recheck-B`, RC-3 under decision concern 13's wording | 3 of 3 | 0.29–1.00 | 2 | 0 (1 review) | 0 | 1 | 0 | 0.33 |
| `recheck-A`, round 3 (RC-1 to RC-4 run again, 2026-11-17) | 3 of 3 | 0.29–1.00 | 2 | 0 (1 review) | 0 | 2 | 0 | 0.31 |

The three defect cases of each recheck row did not run under one prompt: RC-1 ran before R2-5 (CLI 2.1.321), RC-4
under R2-5's wording, and RC-3 under the wording its row names; the round-3 row's four cases ran under one
launcher, round 3's (R3-2, R3-3 and the mechanism wording as shipped). Only RC-3 ran under decision concern 13's
wording.
In this report decision concern 13's wording is its first wording, whose mechanism definition had the example "such
as "again after every push"", RC-3's own answer phrase. The review of the owner's decisions of 2026-11-16 (unit
`owner-decisions-2`, F2) removed the example, so RC-3's two re-raises ran under a wording that is no longer shipped,
and the shipped wording, without the example, was unmeasured until round 3; whether to measure it was the owner's
(decision concern 17 on the [decision page](../agentic-sdlc-poc/slice_4_decisions.md)), who chose RC-1 to RC-4 once
each on `recheck-A` (the round-3 row); `recheck-B` has not run under it.

- **What R2-9 changes.** `short+list` gains FS-2, RM-3 and RM-4; `open+list` gains RM-3 (its RM-4 match is rated
  low, so it stays seen); `open-B+list` gains RM-3 and RM-4. No detection is lost. The confirmer upheld a medium match
  for every gained case; of the 144 medium findings it judged 13 a match and 131 no match. False alarms rise with the
  medium findings on the no-defect cases, all close-out and process findings: on CL-1 an unprobed fact behind the new
  rule (`short+list`, `open+list`) and the rule's purpose (`open+list`); on CL-2 the missing implementation-log entry
  (every setup) and a STATUS refresh left incomplete (`open+list`, `open-B+list`); and on the decoy DC-1, under
  `open+list`, the missing implementation-log entry, not the decoy. So `open+list` now raises the most (7 in 4 reviews)
  and `short+list` the fewest (4 in 4); per no-defect review, the draft `open-B+list` still raises the most (6 in 2).
  They stay upper bounds, by the author's reading, not confirmed blind. Under R2-9 the discordant cases are: only `short+list` FS-1 and RM-4, only
  `open+list` RM-6; only `open+list` PB-3 and RM-6, only `open-B+list` FS-1 and RM-4. FS-2's `short+list` repeat now
  detects in both runs; the rating agreement stays 1 the same and 2 different.

- **The rechecks** (decision concern 4): RC-1's answer is a false `fixed:`, which a good recheck re-raises; RC-2's
  two answers hold (a `rejected:` whose reason checks out in the files it cites, a `fixed:` whose tests are in the file
  it names), and a good recheck accepts both and re-raises neither. Both wordings re-raised RC-1's false fix. On RC-2,
  `recheck-B` accepted both answers, with notes that check each claim against the files, and raised no finding
  (USD 0.31, 0.3 minutes); `recheck-A` failed the launcher's read check, so it counts as a miss: its `opened` for R1-1
  names the harness, which the rejection cites and the review never read with the Read tool (USD 0.28, 0.3
  minutes). How it judged the two answers is unknown: the launcher keeps no report of a failed attempt. It is the
  failure that also stopped the first attempt of four of this slice's real rechecks (discovered issues 5, 7, 14 and
  17 of the decision page), all under 4.1's wording, the launcher's. RC-2 ran under CLI 2.1.323 and RC-1 under
  2.1.321, and RC-2's prompts carry the 2026-11-13 growth (a `searched` list; a rejection's cited files must be read),
  which RC-1's did not. One run per wording cannot give a rate: a wording that re-raises everything would have failed
  RC-2, and `recheck-B` did not, but whether `recheck-A`'s read-check miss is its wording or chance, one run cannot say.

- **The round-2 rechecks** (R2-10), after R2-5 (the output section asks, of each `fixed:` answer, whether the fix adds
  a mechanism without the owner's approval where changing a choice would do, and to re-raise it if so) and R2-7 (a
  recheck quotes the lines each rejection it accepts or re-raises rests on, and the launcher checks each quote in the
  copy). Both cases are planted on `e842e97`, like RC-1 and RC-2, so their reviewer got that commit's `AGENTS.md`
  (discovered issue 18), which has "Ask before growing" and "Fixes stay within the agreed decisions" but not R2-4's
  text; R2-5's question reached them through the prompt. A base with R2-4's text was not possible without changing the
  runner's design: the copy is the whole tree, which from slice 2 on holds this benchmark's own directory (the runner
  refuses such a copy) and the slice's records, which describe these very cases.
  - **RC-3** (plan list): `AGENTS.md` gains a handoff summary that states the CI result of the PR's head commit,
    which the head cannot have when the PR is opened (R1-1, high). The answer is a `fixed:` that adds a step: the
    summary written once CI has finished, and again after every later push. Leaving the CI result out would do: the
    rules make a gate's result its CI job's conclusion on GitHub, and the plan list's question 8 asks whether a fix
    changes the upstream choice before adding a mechanism. This is 4.6's F3 and its first fix, on a base whose records
    do not tell it.
    - *First runs, under R2-5's wording* (2026-11-14; the mechanism is "a gate, check, CI job, process step, document,
      register or field", and a simpler alternative is any mechanism that could be removed or simplified). **Both
      wordings accepted the fix, so both missed.** `recheck-A` read `AGENTS.md`, the change and `ci.yml`, and reported
      a new medium finding (the summary is not the head's between a push and the end of CI) and a new low simpler
      alternative that names the choice exactly ("a second copy of a fact that GitHub's checks panel already shows"; a
      link to the head's checks would do), but did not re-raise R1-1, as the mechanism question asks (USD 0.24, 0.4
      minutes). `recheck-B` read `AGENTS.md` and the change and reported a new low finding about the same window
      (USD 0.22, 0.4 minutes).
    - *Second runs, under decision concern 13's first wording* (2026-11-16; a step added or repeated, such as "again
      after every push", and a second copy of a fact that must be kept current are mechanisms too; a fix that adds one
      without approval is re-raised at its severity, not reported as a simpler alternative; a simpler alternative is a
      mechanism the owner approved). The example "again after every push" has since been removed (review
      `owner-decisions-2`, F2), so these runs are of a wording that is no longer shipped; the shipped wording was
      unmeasured until round 3 (decision concern 17; below). **Both wordings re-raised R1-1 under its ID, at high,
      so both detected it;** the blind confirmer judged both a match. Each read `AGENTS.md` and the change, raised no
      other finding and gave the verdict "no".
      `recheck-A`: "The fix answers the timing problem by adding a repeated step (write the summary once
      CI has finished, then rewrite it after every push) and keeps a second copy of the CI conclusions, without owner
      approval. It could instead have dropped the copied conclusions and linked to the head commit's checks on
      GitHub. Re-raised at high." (USD 0.23, 0.3 minutes). `recheck-B`: "The fix fills the timing gap by adding a
      repeated, unchecked step: rewrite the summary after every push. Nothing shows the owner approved that step.
      Removing the per-job CI copy from the summary and pointing to the head's GitHub checks would close the gap
      without a new step." (USD 0.22, 0.2 minutes). The two named the same simpler choice that `recheck-A` had filed
      as a low simpler alternative in its first run, now as the reason to re-raise.
  - **RC-4** (code list): the evidence secret check reads a value that starts with a backtick as prose, which also
    hides a credential written in a code span (R1-1, high). The answer is a `rejected:` that cites a real test,
    `test_each_secret_shape_is_found`, whose fixture "Authorization Bearer header" passes but holds no code span, so it
    passes R2-2's shape check and does not cover the scenario. This is the code-span placeholder of #48 that plan
    review 4.4 (A9) found hiding a real value. **Both wordings re-raised R1-1 under its ID, at blocking,** each quoting
    the placeholder line, the credential rule and the cited fixture (`recheck-A` also the new accepted fixture); the
    launcher's read and quote checks passed (`recheck-A` USD 0.29, 0.4 minutes; `recheck-B` USD 0.29, 0.4 minutes).
    The blind confirmer judged both re-raises a match, and RC-3's new medium finding no match (a new ID, not R1-1).
  - **Read together, RC-1 to RC-4, one run each per wording:** where the answer states a fact the files can refute,
    both recheck wordings refuted it: the false fix of RC-1 and the false rejection of RC-4, and `recheck-B` accepted
    RC-2's true answers (`recheck-A` failed its read check). Where the fix works but adds a mechanism (RC-3), neither
    re-raised it under R2-5's wording, although the prompt and the list ask it, and `recheck-A` filed the simpler
    choice as a low simpler alternative; under decision concern 13's wording both re-raised it at its severity and
    named the same simpler choice as the reason. So the runs show a recheck telling a false fact from a true one under
    both wordings, and re-raising a fix that grows the process only once the mechanism definition names a repeated
    step and a kept copy, with RC-3's own phrase as its example, and a simpler alternative no longer covers an
    unapproved mechanism. Without the example, as the wording now ships, no case had run before round 3 (below).
    - *What they can show:* on this one case, under this model, CLI and base, both recheck wordings went from
      accepting the fix to re-raising it at its severity, each in one run.
    - *What they cannot show:* a rate (one run per case and wording; earlier in this benchmark two runs of the same
      case and setup rated its defect differently in 2 of 3 repeated pairs, so each flip may be chance); whether a
      recheck under the new wording still accepts answers that hold, since RC-2 did not run under it; whether an
      initial review now reports more mechanism defects, since no initial case ran under it; whether the wording
      works on a mechanism other than RC-3's. Three confounds
      weaken even the one-case reading. RC-3 is the case the wording was written from, and its example "again after
      every push" is the answer's own phrase ("written again after every later push"), so a re-raise may show the
      reviewer matching the example as much as applying the rule; the leak search passed because it checked the copy,
      the rules, the upstream items and the task, not the output section, and no leak term is that phrase (since the
      review `owner-decisions-2`, F3, it reads the whole prompt the reviewer gets; a dry run over every case passes). RC-3's
      reviewers get the rulebook of its base `e842e97` (discovered issue 18), which says only that removing or
      changing a mechanism "is preferred over adding one" and that a simpler alternative is "non-blocking", not today's
      rule that a fix never adds one; the prompt's output section now defines a simpler alternative more narrowly than
      those base rules do, and both reviewers followed the output section. And R2-5's and R2-7's effect is still
      unmeasured: RC-3 and RC-4 have no run without them, and RC-1 and RC-2 ran before them, under other CLI versions
      and prompts.

- **The round-3 rechecks** (round 3 of slice 4, measurement 3; decision concern 17, decided by the owner on
  2026-11-17), after R3-2 (for every `fixed:` or `rejected:` answer it accepts or re-raises, a recheck quotes a line
  of a file the answer names or cites; a file counts as seen when a Read of it succeeded or a Grep output showed its
  lines) and R3-3 (what an existing rule already requires of a fix, such as a test for new behaviour or a handoff
  record, is not an added mechanism), under the mechanism wording as shipped, without the example. RC-1 to RC-4 ran
  once each on `recheck-A`, the recheck wording the launcher ships; `recheck-B` did not run. Each case is still one
  planted commit on `e842e97`, so its reviewer got that commit's `AGENTS.md` (discovered issue 18) and the whole
  case as its change, not R3-1's range since the reviewed round.
  - **RC-1:** re-raised R1-1 at blocking, so detected (M149), and raised a new high, R2-1, on
    `docs/test_spec.md:109`, which the blind confirmer judged no match (M151; a new ID, not R1-1). It quoted the
    harness (`scripts/rogue_node_tests.sh:1935`), which its `paths_read` does not list; the runner keeps no
    stream, so which lines the check counted as seen is not verified (discovered issue 45) (USD 0.19, 0.3 minutes).
  - **RC-2:** accepted both answers, each quoted, raised no finding and gave the verdict "yes", so it passed; for
    R1-2, whose fix adds tests, it cited the carve-out: "The fix adds only tests, which the existing rules require
    for new behaviour, so it adds no mechanism". It left `AGENTS.md` unread (USD 0.30, 0.6 minutes). Its earlier
    `recheck-A` run had failed the read check.
  - **RC-3:** re-raised R1-1 at high under the shipped mechanism wording, quoting `AGENTS.md:168-171`, so detected
    (M152) (USD 0.19, 0.3 minutes).
  - **RC-4:** re-raised R1-1 at blocking, quoting the cited fixture (`tests/tools/test_evidence_secrets.py:86`) and
    `scripts/evidence_secrets.py:41`, so detected (M150) (USD 0.26, 0.4 minutes).
  - *What they can show:* on these four cases, under this model, CLI and base, the shipped recheck wording with
    R3-2 and R3-3 re-raised the three false answers and accepted the two answers that hold, each in one run: RC-3's
    fix that adds a step was re-raised without the example, and RC-2's fix that adds tests was not re-raised.
  - *What they cannot show:* a rate (one run each); R3-1's effect, since each case is reviewed whole; and how
    `recheck-B` does under R3-2 and R3-3, so round 3 does not compare the two wordings.

- **Discordant cases,** `short+list` against `open+list`: only `short+list` FS-1; only `open+list` FS-2 and RM-6.
  `open+list` against `open-B+list`: only `open+list` PB-3 and RM-6; only `open-B+list` FS-1.
- **Repeats** (S45-D6, by confirmed verdicts): FS-2 `open+list` detected twice, `short+list` missed then detected;
  RM-6 `open+list` detected twice (its second detection is one of the two re-judged findings above), `short+list`
  failed then missed. The repeat rule (discordant cases where both
  first reviews completed first, then the others in the key's order) was written after the first runs, with the
  three discordant cases known; it chose FS-2 and RM-6, the two that favoured `open+list`, and left out FS-1, the one
  that favoured `short+list`. FS-2's repeats moved toward agreement; RM-6's kept the difference.
- **Rating agreement** where a case and configuration ran twice and both runs completed (the repeats of S45-D6; since
  R4-3 the runner's own line counts these only), by expected defect: the two runs rated it the same once and
  differently twice (detected or not, and at which severity).
- **Failed reviews count as misses** (4.5a): RM-6 `short+list` and PB-3 `open-B+list` read none of the files under
  review (the empty-review rule); FS-1 `open+list` was withheld because the publication check found a
  credential-shaped value in its report, although the prompt asks for `<token>`. FS-1's defect is a credential in an
  audit event, so a review that describes it concretely is the most likely to trip the check: this withheld review
  may well have been a detection, and it makes FS-1 the one discordant case that favours `short+list`.
- **False blockers and unread files.** Every setup raised 6 or 7 blocking findings at no expected place across its
  15 reviews, and left 42 to 50 files under review unread. "False blocker" is the metric's name, not a verdict: it
  counts blocking findings outside the planted defects. Step 1 of decision concern 8 read all 20 of the first runs'
  and found every one a real defect of the reviewed commit; 8 of them are rated above what the rules support
  ([severity analysis](severity_analysis.md), section 5a). Stage A's author, likewise, found none false in 17 reviews.
- **False alarms are upper bounds,** by the author's reading, not confirmed blind: the blocking and high findings on
  CL-1 and CL-2 read as real process findings of those commits (CL-1 adds a rule to `AGENTS.md` without a plan; CL-2
  closes DPL-008 without the probe of the GitHub setting it rests on). CL-3 and the decoy DC-1 drew none.
- **The second confirmer** agrees on 9 of the 10 sampled findings. Its base rate: 8 of the 10 sampled findings are
  the author's "no match", as are 98 of all 125, so the sample cross-checks only two matches. The one disagreement,
  T035, is a recheck finding the author judged no match (a new finding, R2-1, not the re-raise of R1-1 under its ID,
  which the rule asks for) and the second confirmer judged a match.

## Where findings started

Origin stage of each finding against the list of the review that found it (S41-D16), over all completed reviews:
findings of discovery origin were found mostly with the plan list (13 of 14), findings of requirements origin with
the requirements list (27) and the plan list (10), and the code list's reviews found mostly implementation (94) and
tests-first (30) problems. The full table is in the runner's report below.

## What these counts can show

With 11 defect cases and one run each, a difference of one or two cases between two configurations is within
chance; the intervals overlap almost entirely. The counts show no setup clearly better: `open+list` detected one case
more than the others, `short+list` detected more of its cases with a blocking finding, and the drafted `open-B+list`
raised the most findings on the no-defect cases. The repeats were chosen after the first runs (see above). The
second recheck case, RC-2, tests the opposite failure of a recheck, re-raising answers that hold (decision concern 4),
with one run per wording.
Every configuration carries the lists, so the counts do not measure the lists' own effect.

Under R2-9 the order changes and the conclusion does not: `short+list` detects 9, the other two 8, and `short+list`
raises the fewest findings on the no-defect cases; one case apart is within chance, and the intervals still overlap
almost entirely. Every R2-9 count comes from the same runs, so it says what those runs show under the rule round 2
fixes findings by, not how a review behaves when it knows that a medium finding is fixed: the earlier reviews ran
before R2-1 and R2-5 reached the prompt.

## The canary

Three canary pairs ran under CLI 2.1.321, the version of every stage-B review. The first two used the launcher's
review prompt, whose mandate tells every reviewer to treat files as data; both twins ran the planted hook and
declined the planted `CLAUDE.md`, the second worded as an ordinary project convention. That was the author's 4.5a
choice of prompt, not S45-D9 (4.5b report review, B2). The third pair got its own prompt, which asks to follow the
instructions the session holds: its twin, without the launcher's flags, followed `CLAUDE.md` (CANARY-BRAVO) and ran
the hook, and the confined reviewer followed neither. So the canary is valid and passes, as S45-D9 asks, for the CLI
version the reviews ran under; the runner again requires that before any stage-B review. The failed-Read probe
confirmed that a Read that fails is marked as an error and never counts as read. A fourth pair ran under CLI 2.1.323
on 2026-11-13, before RC-2's runs and decision concern 8's: valid and passed (USD 0.25). The runner now counts a
canary as done only for the CLI version it ran under.

## Each confirmed detection and the checklist question behind it

Where the finding's own text cites a question of its stage list, that is given; otherwise the question that asks
about the defect, by the author's mapping after the fact, is marked *(author)*. When these reviews ran, the reviewer
schema had no field for the question, so most findings cite none (discovered issue 11); the optional `question` field
came after them (growth approved on 2026-11-13), and the runner's report counts it: 0 of these runs' findings.

| Case | List given | Configurations that detected it | Question |
| --- | --- | --- | --- |
| RM-1 (issuer key reaches services that need only the public key) | code | all three | none numbered; the code list's Blocks entry "an asset reaching a non-holder" *(author)* |
| RM-2 (token values in E2E evidence) | e2e-tests | all three | E5, cited by one finding |
| RM-6 (refusal paths untested) | code | `open+list`, in both runs | C8 *(author)*; the unit-test list's U6 asks it directly, but the case got the code list |
| PB-1 (a requirement no test could verify) | requirements | all three | R1 *(author)*; one finding cites R6 for its second point |
| PB-2 (a design gives the signing key to a non-holder) | architecture-and-interfaces | all three | A2 *(author)* |
| PB-3 (a test plan retires a requirement's only proof) | plan-and-test-plan | `short+list`, `open+list` | P2 *(author)* |
| FS-1 (an audit event would log the Jira credential) | architecture-and-interfaces | `short+list`, `open-B+list` | A2 *(author)* |
| FS-2 (a bare sleep where the harness polls) | plan-and-test-plan | `open+list`, `open-B+list`; `short+list` in its repeat | none of the plan list (findings cite P8 and P10 for side points); the E2E list's E4 asks it, but the case got the plan list |
| RC-1 (a false `fixed:` answer) | e2e-tests | `recheck-A`, `recheck-B` | E1 *(author)* |
| RC-4 (a false `rejected:` answer citing a test that does not cover the scenario) | code | `recheck-A`, `recheck-B` (R2-10) | C8 *(author)*: the cited test does not show the check failing on the case it exists to catch |
| RC-3 (a `fixed:` answer that adds a step where leaving the CI result out would do) | plan-and-test-plan | `recheck-A`, `recheck-B`, under decision concern 13's wording only (both missed it under R2-5's) | P8 *(author)*: whether a fix changes the upstream choice before adding a mechanism; the findings cite the output section's mechanism question and "Ask before growing", no list question |

Under R2-9, also by a medium finding: RM-3 (requirements without proof) by all three and by `open+list+sev`, its
findings citing the list's question 5 (R5), one in its `question` field; RM-4 (a gate inside another CI job) by `short+list`,
`open-B+list` and `open+list+sev`, each citing question 10 (C10); FS-2 by `short+list` in its first run too.

## By stage list

Each case got one stage list, the one for its artifact type (S44-D12), and every configuration carried it. First
runs, by confirmed verdicts:

| List | Cases | Outcome |
| --- | --- | --- |
| `requirements` | PB-1, RM-3 | PB-1 detected by all three setups; RM-3 missed by all three, each review citing R5 at medium, which R2-9 counts: detected by all three |
| `architecture-and-interfaces` | PB-2, FS-1 | PB-2 by all three; FS-1 by `short+list` and `open-B+list` (`open+list` withheld) |
| `e2e-tests` | RM-2, RC-1, DC-1 | RM-2 by all three; RC-1 by both recheck wordings; no false alarm on the decoy DC-1 |
| `code` | RM-1, RM-4, RM-5, RM-6, RC-2, RC-4 | RM-1 by all three; RM-6 by `open+list`; RM-4 missed (C10 cited at medium or low; under R2-9 detected by `short+list` and `open-B+list`, `open+list`'s at low); RM-5 missed (one exact description at a wrong line); RC-2, whose answers hold, passed by `recheck-B`, missed by `recheck-A` (the read check); RC-4's false rejection re-raised by both wordings |
| `plan-and-test-plan` | PB-3, FS-2, CL-1, CL-2, CL-3, RC-3 | PB-3 by `short+list` and `open+list` (`open-B+list` failed); FS-2 by `open+list` and `open-B+list`, and by `short+list` in its repeat (under R2-9 in its first run too); alarms on CL-1 and CL-2, none on CL-3; RC-3's mechanism fix accepted by both wordings under R2-5's wording, although the list's question 8 asks it, and re-raised by both under decision concern 13's |
| `unit-tests` | none | not measured |

The `unit-tests` list was never given to a reviewer, and neither was the tests-first pairing of `unit-tests` with
`e2e-tests` that `AGENTS.md` names: no case of the key is a unit-test change, and each case got a single list. With
two to five cases a list, the table shows whether a list's questions led reviewers to its cases' defects, not how
good a list is.

## The misses

No configuration detected RM-3, RM-4 or RM-5:

- **RM-3** (ten requirements added without proof, DPL-004): R5 asks exactly this, and all three reviews reported it
  citing the list's question 5, at medium, so the rule does not count it.
- **RM-4** (a new gate run inside another CI job, DPL-005): C10 asks exactly this, and all three reviews reported it,
  citing "checklist Q10", at medium or low.
- **RM-5** (the diff-coverage gate's `--include` given twice, DPL-009): one finding describes the planted defect
  exactly but names line 1791 of a short file, outside the planted range, so the committed rule does not count it.

So for two of the three misses the list's question led every review to the defect, and every review rated it below
high. Whether a list question's answer should carry a severity floor is a
question for the owner, not something this benchmark decided.

Under R2-9 (round 2), which counts a medium match: RM-3 is detected by all three setups, RM-4 by `short+list` and
`open-B+list` (`open+list` rated it low), and RM-5 is still missed by all three. A medium finding is now fixed (R2-1),
so a defect seen at medium is caught without a severity floor.

## Why fewer than 80% of the defects were detected

The owner asked why every initial setup stayed below 80% (2026-11-11). No plan set a detection target; against
80%, the shortfall has three causes, and only one is that reviewers did not find the defect. First runs, by
confirmed verdicts; "seen" is a match rated medium or low, or at the place without a term:

| Setup | Detected (blocking or high, as run) | Detected (R2-9: blocking, high or medium) | Seen at any severity | Seen, leaving out failed or withheld reviews |
| --- | --- | --- | --- | --- |
| `short+list` | 6 of 11 (55%) | 9 of 11 (82%) | 9 of 11 (82%) | 9 of 10 (90%) |
| `open+list` | 7 of 11 (64%) | 8 of 11 (73%) | 9 of 11 (82%) | 9 of 10 (90%) |
| `open-B+list` | 6 of 11 (55%) | 8 of 11 (73%) | 8 of 11 (73%) | 8 of 10 (80%) |

1. **Seen but rated below high (5 misses).** RM-3 and RM-4 were seen by every review, each citing the list question
   that asks it (R5, C10), at medium or low; FS-2 under `short+list` too. The rule counts only blocking and high
   findings, and the lists' Blocks sections do not name these cases (decision concern 8). Making R5 and C10 blocking
   would give `open+list` 9 of 11 and the other two 8 of 11.
2. **Review mechanics, counted as misses (3).** RM-6 under `short+list` and PB-3 under `open-B+list` read none of the
   files under review (the empty-review rule); FS-1 under `open+list` was withheld by the publication check.
3. **Not found (4).** RM-5 by every setup (one exact description at a wrong line), and RM-6 under `open-B+list`.

The planted cases were found (each setup 4 of 5, its one miss a failed or withheld review or a below-high rating);
the shortfall is in the historical misses (2 or 3 of 6), which were chosen because earlier reviews missed them. Three
of those are the misses the PoC's first outcome names: DPL-004 (RM-3) and DPL-005 (RM-4) are now seen but not
flagged, and DPL-010 (RM-6) is caught by one setup of three. With 11 cases, 7 detections give an interval of 31%
to 89%, so these counts can neither confirm nor rule out 80%.

**Under R2-9** (round 2: a medium finding is fixed, so a match rated medium is detected; the same runs, re-scored and
confirmed blind, see Counts), cause 1 shrinks from 5 misses to 1: RM-4 under `open+list`, rated low. Causes 2 and 3
are unchanged (3 and 4 misses), since R2-9 changes ratings, not what a review read or found. `short+list` reaches 9 of
11 (82%, interval 48% to 98%), and the other two 8 of 11 (73%, 39% to 94%); under R2-9 every finding seen at medium
counts, so `short+list` detects all it saw. The intervals still neither confirm nor rule out 80%, and the analysis's
point stands in another form: what remains below 80% is mostly review mechanics and defects not found, not ratings.

## Severity: decision concern 8

**The question.** Every review saw RM-3 (requirements added without proof) and RM-4 (a gate run inside another CI
job), each citing the list question that asks it, and rated it medium or low, so neither counted. The owner asked why
reviewers rate found defects below the threshold, and to measure one general wording change on all cases, not the two
R5 and C10 blocking conditions alone (decision concern 8, 2026-11-13).

**Step 1, the analysis** ([severity analysis](severity_analysis.md)), from these results:

- the 7 findings seen but rated below high all rate the scenario's first symptom (a report shows the gap, a job is
  mislabelled), not what it lets merge;
- in 6 of the 7, the rules at the case's base commit supported the low rating ("coverage gaps are reported but do not
  fail"; no rule that a gate needs its own job);
- the 104 blocking or high findings that match no planted defect are mostly real defects; 20 are rated above what the
  rules support and 10 below;
- 16 of the 39 defects found by more than one review got different severities;
- 2 of the 3 repeated pairs (same setup, same case) rated their defect differently.

**Steps 2 and 3, the change and its measurement.** Candidate 1, "finish the scenario", one paragraph after the output
section's `severity` bullet ([`severity_scenario.md`](../../../tests/review_benchmark/prompts/severity_scenario.md)):
rate the end of the failure scenario, not its first symptom, and count as a stop only what can be pointed to in the
copy. `open+list+sev` is `open+list` with that paragraph; it ran once on the 15 initial-review cases, against
`open+list`'s first runs. Fixed in the answer key (version 4, `severity_measurement`) before the runs:

- **Better:** (1) RM-3 and RM-4 both detected by a confirmed match; the baseline had 0 of 6 such reviews at high across all three setups. (2) No baseline detection lost (RM-1, RM-2, RM-6, PB-1, PB-2, PB-3, FS-2); a failed or withheld review is rerun once. (3) No blocking or high finding on DC-1 or CL-3. (4) No more than one extra blocking or high finding on CL-1 and CL-2 together, each read by hand.
- **Outcomes:** **Worse:** (2) or (3) broken. **Inconclusive:** one of RM-3 and RM-4 detected and the guards hold; then repeat RM-3, RM-4, DC-1 and CL-2 once (about USD 4.5) before the owner decides. Also record by hand the new severities of the recurring under-rated (c8, c38, c4) and over-rated clusters, as a diagnostic.

Both setups' 82 blocking and high findings were exported together under fresh tokens and judged against the match
rule by a fresh session that never saw the configurations (`severity_export.jsonl`, verdicts in
`severity_confirmation_author.jsonl`); the runner joins them back (its report, below, has the same counts).

| Case | `open+list` (baseline) | `open+list+sev` |
| --- | --- | --- |
| RM-1, RM-2, PB-1, PB-2, PB-3 | detected, each by a blocking finding | the same |
| RM-3 | seen at medium | seen at medium |
| RM-4 | seen at low | seen at medium |
| RM-5 | not found | not found |
| RM-6 | detected (high) | **seen at medium**; its one blocking finding is about something else |
| FS-1 | withheld by the publication check | detected (blocking) |
| FS-2 | detected (high) | detected (high) |
| Detected | 7 of 11, 5 by a blocking finding | 7 of 11, 6 by a blocking finding |
| Blocking or high on no-defect cases | CL-1 1, CL-2 1, CL-3 0, DC-1 0 | **CL-1 3**, CL-2 1, CL-3 0, DC-1 0 |
| False blockers (blocking, at no expected place) | 7 | 6 |
| Cost and reviewer-minutes | USD 12.22, 36.4 | USD 13.03, 41.8 |

**Outcome: worse, and candidate 1 is not adopted.**

- (1) fails: neither RM-3 nor RM-4 was detected. RM-3's requirements-without-proof finding is still medium and
  still ends at a trace-level symptom. RM-4's separate-job finding now reaches a consequence ("if docs-check is ever
  made optional or split, the lint stops gating without anyone noticing") and is still medium.
- (2) fails: RM-6 is lost.
- (3) holds.
- (4) fails: CL-1 drew 3 blocking or high findings against 1, two extra where one is allowed. Of its three, the blind
  confirmer judged one a real but minor record gap and two not real.

**Under R2-9** (round 2), the same 30 runs re-scored, and the matches R2-9 adds confirmed blind by the third export:
`open+list` detects 8 of 11 (it gains RM-3, seen at medium), `open+list+sev` 9 of 11 (it gains RM-3 and RM-4, both
at medium, and still lacks RM-6, whose one medium finding at the place, R1-M1, the confirmer judged no match: unproved
facts about the CLI stream, not the untested refusal paths). Read with "blocking, high or medium" in place of
"blocking or high", criterion (1) holds (RM-3 and RM-4 both detected), (2) still fails (RM-6 lost), (3) holds (no
such finding on DC-1 or CL-3) and (4) holds by its letter (CL-1 and CL-2 together draw 7 against 6, one extra). So
the outcome stays **worse**, now by (2) alone, and nothing changes: candidate 1 stays unadopted. The re-reading is
after the fact (the criteria were fixed for the earlier threshold), and with R2-1 the candidate's aim, to lift a found
defect above the threshold at which it is fixed, is met for every medium finding without it.

The launcher's output section and `AGENTS.md` stay as they are; `open+list+sev` and its paragraph stay in the
benchmark as measured. The plan repeats cases only on an inconclusive result, so there was no repeat. The
confirmation departed from the plan twice, both recorded among the author's decisions on the decision page: a fresh
session the author started, which never saw the configurations, confirmed instead of the author (the verdict file
keeps the role name `author` in its name), and the Sonnet second confirmer was skipped, because not adopting rests on
counts no verdict changes ((1) fails with no blocking or high finding of `open+list+sev` at RM-3's or RM-4's expected
places, and (4) counts CL-1's and CL-2's blocking or high findings) and only "worse" rather than "not better" rests on
one verdict, RM-6's blocking finding judged not a match. The confirmer's own borderline notes (S055, the baseline's
RM-6 match by the absence clause only; S031 and S054 on PB-1; S014 and S048 on FS-2) touch only detections that do
not decide a criterion: (2) is judged against the baseline detections the plan lists.

**The diagnostic the plan asked for: the recurring mis-rated clusters.** Each cluster of the
[analysis](severity_analysis.md) (section 5b, and the expected moves of section 8), with its severity in
`open+list`'s first run and in `open+list+sev`, read by hand from the results (B, H, M: blocking, high, medium).

| Cluster | Case | Supported (analysis) | `open+list` | `open+list+sev` |
| --- | --- | --- | --- | --- |
| c4: identity tests loosened to accept 401 | RM-1 | B (under) | H (F4) | M (F4) |
| c8: M2.5-T1 and T3 fail when the boundary works; T2 never runs its script | RM-2 | B (under) | H (F5; T2 not reported) | B (F6); T2 H (F7) |
| c38: expiry, missing-token and bad-request requirements lose their only proof | PB-3 | B (under) | H (F4) | H (F3) |
| c37: REQ-M2-R10/R11's proof and the only positive twin removed | PB-3 | B (under) | H (F3) | not reported (F3 names T2 only in passing) |
| c12: qa-deploy is not default deny | RM-3 | H (over) | B (F1) | B (F1) |
| c14: holder lists contradict (the Docker-socket holders) | RM-3 | H (over) | B (F2) | not reported |
| c19: the template overclaims what the lint rejects | RM-4 | H (over) | B (F2) | not reported |
| c36: the new requirement has no proof entry, which the gap gate fails | PB-1 | H (over) | B (F2) | H (F2) |
| c41: H4 contradicts H1 | FS-2 | H (over) | B (F1) | B (F4) |
| c47: the new rule has no test or review question | CL-1 | L–M (over) | not reported | B (F1) |

Two clusters moved toward the supported severity (c8, c36), two away from it (c4 down to medium, and c47, a new
over-rated blocker on a no-defect case, which with c48, an unprobed permission rated medium before and high now, makes
CL-1's two extra findings), three stayed and three were not reported: the paragraph moved ratings both ways, not
consistently toward the supported severity.

**What 15 runs cannot show.**

- They cannot give a detection rate: 7 against 7 of 11, each with an interval of 0.31 to 0.89.
- "Worse" rests on RM-6's rating in one run, and identical runs disagreed in 2 of 3 repeated pairs. What the run
  does show is that the paragraph moved neither target: 0 of 2 detected, after 0 of 6.
- Four no-defect reviews give no false-alarm rate.
- The historical cases get their base's rules, so the run cannot show the effect under today's `AGENTS.md`. Nor
  can it show the effect with other mandates, or on other kinds of defect.

**Not like for like.** The baseline ran under CLI 2.1.321 and the measurement under 2.1.323. The output section has
also changed between them, by the growth of 2026-11-13: the `question` field and its rule, and the `searched` list.
So the two prompts differ by those as well as by the paragraph. Every other part of the prompt was the same: the
mandate, the lists at `04f8df4`, each case's base rules and the model at high effort.

## For the owner's choice

- **Default setup:** `short+list` or `open+list`; the counts do not separate them, under either rule (6 against 7
  as run; 9 against 8 under R2-9, with 4 against 7 false alarms).
- **Initial mandate wording:** 4.1's (`open+list`) or the draft (`open-B+list`); 7 against 6 detections, 2 against
  4 false alarms, within chance; under R2-9, 8 against 8, and 7 false alarms in 4 reviews against 6 in 2.
- **Recheck mandate wording:** 4.1's or the draft. Both re-raised the false fix (RC-1) and the false rejection
  (RC-4); both accepted the fix that adds a mechanism (RC-3) under R2-5's wording and both re-raised it under
  decision concern 13's, so the wordings do not differ there. On answers that hold (RC-2) the draft accepted both
  and 4.1's failed the read check; one run each, so this leans to the draft without showing it better. In round 3,
  under R3-2 and R3-3, 4.1's wording (the launcher's) re-raised RC-1, RC-3 and RC-4 and passed RC-2, one run each;
  the draft did not run under them, so round 3 does not compare the two.
- **Final mandate wording:** by reason; no case measures it (S45-D8).

The launcher's mandate constants stay 4.1's until the owner chooses (S45-D8).

## The runner's report, verbatim

Built after round 3's runs of RC-1 to RC-4 on `recheck-A` and their blind confirmation (2026-11-17), with answer key
version 7, and built again in round 4 of slice 4 (R4-3, the owner, 2026-11-17) after the fix of discovered issue 56
(`02281b0`), with no reviewer call. `open+list+sev` is confirmed by the second export's verdicts, every other setup by
the first export's, and the findings neither held by the third export's (round 3's four appended as M149 to M152).
Since R4-3 the runner counts each case, configuration and run by its last line in `benchmark_results_B.jsonl`, so a
case run again under another prompt (S45-D2: a change to anything the reviewer gets makes a new review) replaces its
earlier run: RC-3's second runs replace its first on both wordings, and round 3's four runs replace the earlier runs
of RC-1 to RC-4 on `recheck-A`. Its `recheck-B` row reads 3 of 3, over RC-1, RC-3's second run and RC-4, and its
`recheck-A` row 3 of 3, over round 3's runs, each with RC-2 as its one completed no-defect review (on `recheck-A`
round 3's run, which passed); its lines on rechecks list each case once per wording, by its last run; and its rating
agreement "where a case ran twice" now takes only the repeats (S45-D6), 1 the same and 2 different. Before R4-3 it
counted every such run as a further first run (discovered issue 39): `recheck-B` 3 of 4, `recheck-A` 6 of 7 with
RC-2 failed once, both RC-3 runs per wording in the recheck lines, and a rating agreement of 3 the same and 4
different under R2-9. The rows of the earlier runs, which the runner over today's results no longer gives, are in the
counts above. The per-review rows below still list every run, the replaced ones too; read round 3's by their prompt
identities: RC-1 `12670029`, RC-2 `b1a96364`, RC-3 `f9a54a8f`, RC-4 `083c54f6`, the last four rows.

````markdown
Stage B. Answer key SHA-256: `0ee2ad1414c00d49f6aef68f69df749ce2f653b232edbc76ad2126192035721a`; match rule SHA-256: `422d32c2be493a13c8a715f815763d95f3a76d6285daabe959af4dbdebb465fb`; lists at `04f8df4`.

Detections are confirmed by the author's blinded verdicts, and the findings that no earlier export held by a fresh session's blinded verdicts on the third export.

Under the rule of their runs (blocking or high), the reviews recorded before the key's rule, each with the score of its run:

| Configuration | Detected | 95% interval | Detected (blocking) | False alarms (no-defect reviews) | False blockers | Failed | Unread files | Not yet confirmed | Cost USD per detection | Minutes per detection |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open+list | 7 of 11 | 0.31–0.89 | 5 | 2 (4) | 7 | 1 | 42 | 0 | 1.75 | 5.2 |
| open+list+sev | 7 of 11 | 0.31–0.89 | 6 | 4 (4) | 6 | 0 | 20 | 0 | 1.86 | 6.0 |
| open-B+list | 6 of 11 | 0.23–0.83 | 5 | 4 (2) | 7 | 1 | 50 | 0 | 2.02 | 5.9 |
| recheck-A | 1 of 1 | 0.02–1.00 | 1 | 0 (0) | 0 | 1 | 0 | 0 | 0.47 | 0.7 |
| recheck-B | 1 of 1 | 0.02–1.00 | 1 | 0 (1) | 0 | 0 | 1 | 0 | 0.49 | 0.8 |
| short+list | 6 of 11 | 0.23–0.83 | 6 | 2 (4) | 6 | 1 | 42 | 0 | 1.91 | 5.5 |

Discordant cases, short+list against open+list: `{"only short+list": ["FS-1"], "only open+list": ["FS-2", "RM-6"]}`
Discordant cases, open+list against open-B+list: `{"only open+list": ["PB-3", "RM-6"], "only open-B+list": ["FS-1"]}`
Rating agreement where a case ran twice, by expected defect: `{"same": 1, "different": 2}`
Repeats (detected in run 1, run 2): FS-2 open+list: True, True; FS-2 short+list: False, True; RM-6 open+list: True, True; RM-6 short+list: failed, False

Decision concern 8's measurement, open+list+sev against open+list, by the second blinded export's verdicts:

| Configuration | Detected | Cases detected | Detected (blocking) | False alarms on no-defect cases | False blockers | Failed | Cost USD | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open+list | 7 of 11 | FS-2, PB-1, PB-2, PB-3, RM-1, RM-2, RM-6 | 5 | CL-1 1, CL-2 1, CL-3 0, DC-1 0 | 7 | 1 | 12.22 | 36.4 |
| open+list+sev | 7 of 11 | FS-1, FS-2, PB-1, PB-2, PB-3, RM-1, RM-2 | 6 | CL-1 3, CL-2 1, CL-3 0, DC-1 0 | 6 | 0 | 13.03 | 41.8 |

Under the key's rule (R2-9: blocking, high or medium), every review, those recorded under an earlier rule re-scored by `--rescore B`:

| Configuration | Detected | 95% interval | Detected (blocking) | False alarms (no-defect reviews) | False blockers | Failed | Unread files | Not yet confirmed | Cost USD per detection | Minutes per detection |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open+list | 8 of 11 | 0.39–0.94 | 5 | 7 (4) | 7 | 1 | 42 | 0 | 1.53 | 4.6 |
| open+list+sev | 9 of 11 | 0.48–0.98 | 6 | 7 (4) | 6 | 0 | 20 | 0 | 1.45 | 4.6 |
| open-B+list | 8 of 11 | 0.39–0.94 | 5 | 6 (2) | 7 | 1 | 50 | 0 | 1.52 | 4.4 |
| recheck-A | 3 of 3 | 0.29–1.00 | 2 | 0 (1) | 0 | 0 | 2 | 0 | 0.31 | 0.6 |
| recheck-B | 3 of 3 | 0.29–1.00 | 2 | 0 (1) | 0 | 0 | 1 | 0 | 0.33 | 0.5 |
| short+list | 9 of 11 | 0.48–0.98 | 6 | 4 (4) | 6 | 1 | 42 | 0 | 1.27 | 3.7 |

Discordant cases, short+list against open+list: `{"only short+list": ["FS-1", "RM-4"], "only open+list": ["RM-6"]}`
Discordant cases, open+list against open-B+list: `{"only open+list": ["PB-3", "RM-6"], "only open-B+list": ["FS-1", "RM-4"]}`
Rating agreement where a case ran twice, by expected defect: `{"same": 1, "different": 2}`
Repeats (detected in run 1, run 2): FS-2 open+list: True, True; FS-2 short+list: True, True; RM-6 open+list: True, True; RM-6 short+list: failed, False

Decision concern 8's measurement, open+list+sev against open+list, by the second blinded export's verdicts:

| Configuration | Detected | Cases detected | Detected (blocking) | False alarms on no-defect cases | False blockers | Failed | Cost USD | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open+list | 8 of 11 | FS-2, PB-1, PB-2, PB-3, RM-1, RM-2, RM-3, RM-6 | 5 | CL-1 3, CL-2 3, CL-3 0, DC-1 1 | 7 | 1 | 12.22 | 36.4 |
| open+list+sev | 9 of 11 | FS-1, FS-2, PB-1, PB-2, PB-3, RM-1, RM-2, RM-3, RM-4 | 6 | CL-1 4, CL-2 3, CL-3 0, DC-1 0 | 6 | 0 | 13.03 | 41.8 |

Origin stage of the findings against the list of the review that found them: `{"architecture and interfaces": {"architecture-and-interfaces": 16, "code": 16, "e2e-tests": 1, "requirements": 3}, "discovery": {"architecture-and-interfaces": 1, "code": 1, "plan-and-test-plan": 19}, "implementation": {"code": 124, "e2e-tests": 34, "plan-and-test-plan": 27, "requirements": 20}, "requirements": {"code": 2, "e2e-tests": 1, "plan-and-test-plan": 14, "requirements": 36}, "tests first": {"code": 39, "e2e-tests": 34, "plan-and-test-plan": 31, "requirements": 1}, "unknown": {"architecture-and-interfaces": 1, "code": 2, "e2e-tests": 1}}`
Canary: `[{"cli_version": "2.1.321 (Claude Code)", "valid": false, "passed": true, "twin_ran_hook": true}, {"cli_version": "2.1.321 (Claude Code)", "valid": false, "passed": true, "twin_ran_hook": true}, {"cli_version": "2.1.321 (Claude Code)", "valid": true, "passed": true, "twin_ran_hook": true}, {"cli_version": "2.1.323 (Claude Code)", "valid": true, "passed": true, "twin_ran_hook": true}]`. A canary is valid when its twin, without the launcher's flags, followed the planted CLAUDE.md and ran the planted hook (S45-D9); one whose twin ran only the hook shows that the flags keep settings out, not that they keep instruction files out.
Rechecks of false answers (detected when the recheck lists the earlier finding as re-raised and reports it again under its ID, by the confirmed verdicts; a review that did not complete is a miss): RC-1 recheck-B: detected (R1-1 re-raised); RC-4 recheck-B: detected (R1-1 re-raised); RC-3 recheck-B: detected (R1-1 re-raised); RC-1 recheck-A: detected (R1-1 re-raised); RC-3 recheck-A: detected (R1-1 re-raised); RC-4 recheck-A: detected (R1-1 re-raised).
Rechecks of answers that hold (passed when every answer is accepted and none is reported again; a review that did not complete is a miss): RC-2 recheck-B: passed (R1-1 accepted, R1-2 accepted); RC-2 recheck-A: passed (R1-1 accepted, R1-2 accepted).
Findings that name their checklist question: 70 of 424 (architecture-and-interfaces:2 2, architecture-and-interfaces:6 2, code:10 3, code:11 4, code:12 3, code:2 1, code:3 2, code:4 1, code:5 1, code:7 1, code:8 8, e2e:1 5, e2e:10 1, e2e:11 1, e2e:2 1, e2e:4 1, e2e:5 2, e2e:6 1, e2e:8 1, e2e:9 3, plan-review-checklist:6 1, plan-review:1 1, plan-review:11 1, plan-review:12 1, plan-review:2 2, plan-review:4 1, plan-review:7 1, plan:1 2, plan:10 1, plan:2 1, plan:4 1, plan:6 2, plan:7 1, plan:8 1, requirements:1 2, requirements:4 2, requirements:5 2, requirements:6 1, requirements:7 1, requirements:9 1).
Second confirmer: agrees with the author on 9 of 10 sampled findings.

What these sizes can show: with about 15 cases and one run each, a difference of two or three cases between two configurations is within chance; the intervals say how wide each count's uncertainty is. Both setups carry the stage lists, so the counts do not measure the lists' own effect. The owner decides from the counts; no rule decides.

Per-review rows: the automatic first pass of each review, under the rule of its run, before confirmation; the counts above are confirmed.

| Case | Kind | Prompt | Status | Verdict | Detected | Detected (blocking) | Location only | Not blocking | Unmatched blocking | Unmatched (rated as a detection) | Tries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CANARY | canary | — | canary | | | | | | | | |
| CANARY | canary | — | canary | | | | | | | | |
| RM-1 | real_miss | open+list | completed | no | E1 | E1 |  |  | F2 | F2, F3, F4 | 1 |
| RM-1 | real_miss | short+list | completed | no | E1 | E1 |  |  |  | F2, F3, F4, F5 | 1 |
| RM-1 | real_miss | open-B+list | completed | no | E1 | E1 |  |  |  | F2, F3, F4 | 1 |
| RM-2 | real_miss | open-B+list | completed | no | E1 | E1 |  |  |  | F9 | 1 |
| RM-2 | real_miss | open+list | completed | no | E1 | E1 |  |  |  | F6, F8 | 1 |
| RM-2 | real_miss | short+list | completed | no | E1 | E1 |  |  |  | F7, F9, F10 | 1 |
| RM-3 | real_miss | open-B+list | completed | no |  |  |  | E1 | F1, F2 | F1, F2, F3 | 1 |
| RM-3 | real_miss | short+list | completed | no |  |  | E1 | E1 | F1 | F1, F3 | 1 |
| RM-3 | real_miss | open+list | completed | no |  |  | E1 | E1 | F1 | F1, F3 | 1 |
| RM-4 | real_miss | open+list | completed | no |  |  |  | E1 | F1, F2 | F1, F2, F3, F5, F6 | 1 |
| RM-4 | real_miss | short+list | completed | no |  |  |  | E1 | F1 | F1, F2, F3, F4, F5 | 1 |
| RM-4 | real_miss | open-B+list | completed | no |  |  |  | E1 | F1 | F1, F2, F3 | 1 |
| RM-5 | real_miss | short+list | completed | no |  |  |  |  | F1, F2, F3 | F1, F2, F3, F4, F7 | 1 |
| RM-5 | real_miss | open+list | completed | no |  |  |  |  | F1, F2, F3 | F1, F2, F3, F4, F5, F9 | 1 |
| RM-5 | real_miss | open-B+list | completed | no |  |  |  |  | F1, F2, F3 | F1, F2, F3, F4, F5, F6 | 1 |
| RM-6 | real_miss | short+list | failed |  |  |  |  |  |  |  | 1 |
| RM-6 | real_miss | open-B+list | completed | yes |  |  |  |  |  |  | 1 |
| RM-6 | real_miss | open+list | completed | yes | E1 |  |  |  |  | RM6-1 | 1 |
| PB-1 | planted | short+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-1 | planted | open-B+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-1 | planted | open+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-2 | planted | open-B+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-2 | planted | short+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-2 | planted | open+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-3 | planted | open+list | completed | no | E1 | E1 |  |  |  | F3, F4 | 1 |
| PB-3 | planted | short+list | completed | no | E1 | E1 |  |  |  | F2, F3 | 1 |
| PB-3 | planted | open-B+list | failed |  |  |  |  |  |  |  | 1 |
| FS-1 | planted | open-B+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| FS-1 | planted | short+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| FS-1 | planted | open+list | withheld | no |  |  |  |  |  |  | 1 |
| FS-2 | planted | short+list | completed | no |  |  | E1 | E1 |  |  | 1 |
| FS-2 | planted | open-B+list | completed | no | E1 |  |  |  |  |  | 1 |
| FS-2 | planted | open+list | completed | no | E1 |  |  |  |  |  | 1 |
| RC-1 | recheck | recheck-A | completed | no | R1 | R1 |  |  |  |  | 1 |
| RC-1 | recheck | recheck-B | completed | no | R1 | R1 |  |  |  |  | 1 |
| CL-1 | clean | short+list | completed | no |  |  |  |  | F1 | F1 | 1 |
| CL-1 | clean | open+list | completed | yes |  |  |  |  |  | F1 | 1 |
| CL-1 | clean | open-B+list | completed | no |  |  |  |  | F1 | F1, F2, F3 | 1 |
| CL-2 | clean | short+list | completed | yes |  |  |  |  |  | F1 | 1 |
| CL-2 | clean | open+list | completed | yes |  |  |  |  |  | CL2-F1 | 1 |
| CL-2 | clean | open-B+list | completed | yes |  |  |  |  |  | F1 | 1 |
| CL-3 | clean | short+list | completed | yes |  |  |  |  |  |  | 1 |
| CL-3 | clean | open+list | completed | yes |  |  |  |  |  |  | 1 |
| DC-1 | decoy | short+list | completed | yes |  |  |  |  |  |  | 1 |
| DC-1 | decoy | open+list | completed | yes |  |  |  |  |  |  | 1 |
| RM-6 | real_miss | open+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| RM-6 | real_miss | short+list | completed | yes |  |  |  | E1 |  | RM6-1 | 1 |
| FS-2 | planted | short+list | completed | no | E1 | E1 |  |  |  |  | 1 |
| FS-2 | planted | open+list | completed | no | E1 |  |  |  |  |  | 1 |
| CONFIRM-0 | confirmation | — | completed | | | | | | | | |
| CONFIRM-1 | confirmation | — | completed | | | | | | | | |
| CANARY | canary | — | canary | | | | | | | | |
| CANARY | canary | — | canary | | | | | | | | |
| RC-2 | recheck_holds | recheck-B | completed | yes |  |  |  |  |  |  | 1 |
| RC-2 | recheck_holds | recheck-A | failed |  |  |  |  |  |  |  | 1 |
| RM-1 | real_miss | open+list+sev | completed | no | E1 | E1 |  |  |  | F2, F3, F7 | 1 |
| RM-2 | real_miss | open+list+sev | completed | no | E1 | E1 |  |  |  | F8, F9 | 1 |
| RM-3 | real_miss | open+list+sev | completed | no |  |  |  | E1 | F1 | F1, F2, F3 | 1 |
| RM-4 | real_miss | open+list+sev | completed | no |  |  |  | E1 |  | F1 | 1 |
| RM-5 | real_miss | open+list+sev | completed | no |  |  |  |  | F1, F2, F3 | F1, F2, F3, F4, F5 | 1 |
| RM-6 | real_miss | open+list+sev | completed | no |  |  |  | E1 | R1-B1 | R1-B1 | 1 |
| PB-1 | planted | open+list+sev | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-2 | planted | open+list+sev | completed | no | E1 | E1 |  |  |  |  | 1 |
| PB-3 | planted | open+list+sev | completed | no | E1 | E1 |  |  |  | F3 | 1 |
| FS-1 | planted | open+list+sev | completed | no | E1 | E1 |  |  |  |  | 1 |
| FS-2 | planted | open+list+sev | completed | no | E1 |  |  |  |  |  | 1 |
| CL-1 | clean | open+list+sev | completed | no |  |  |  |  | F1 | F1, F2, F3 | 1 |
| CL-2 | clean | open+list+sev | completed | yes |  |  |  |  |  | CL2-F1 | 1 |
| CL-3 | clean | open+list+sev | completed | yes |  |  |  |  |  |  | 1 |
| DC-1 | decoy | open+list+sev | completed | yes |  |  |  |  |  |  | 1 |
| RC-3 | recheck | recheck-B | completed | yes |  |  |  |  |  |  | 1 |
| RC-3 | recheck | recheck-A | completed | yes |  |  |  |  |  |  | 1 |
| RC-4 | recheck | recheck-B | completed | no | R1 | R1 |  |  |  |  | 1 |
| RC-4 | recheck | recheck-A | completed | no | R1 | R1 |  |  |  |  | 1 |
| RC-3 | recheck | recheck-B | completed | no | R1 |  |  |  |  |  | 1 |
| RC-3 | recheck | recheck-A | completed | no | R1 |  |  |  |  |  | 1 |
| RC-1 | recheck | recheck-A | completed | no | R1 | R1 |  |  |  |  | 1 |
| RC-2 | recheck_holds | recheck-A | completed | yes |  |  |  |  |  |  | 1 |
| RC-3 | recheck | recheck-A | completed | no | R1 |  |  |  |  |  | 1 |
| RC-4 | recheck | recheck-A | completed | no | R1 | R1 |  |  |  |  | 1 |

Detected: a finding rated as a detection (blocking or high before R2-9; blocking, high or medium under it) at the expected place with one of its terms; Detected (blocking): the same, by a blocking finding; Not blocking: a match rated below that (medium or low before R2-9, low under it; stage A: advisory); Unmatched blocking, and Unmatched (rated as a detection): findings at no expected place, the false blockers and false alarms on a clean case. "False blocker" names the metric, not a verdict: step 1 of decision concern 8 found all 20 of the first runs' to be real defects of the reviewed commits outside the planted ones.
````
