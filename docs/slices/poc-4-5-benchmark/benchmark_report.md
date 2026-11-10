# Benchmark report — stage B of the review benchmark (slice 4.5b)

The results of slice 4.5's stage-B benchmark, for the owner's choice of the default review setup and of the mandate
wordings (S45-D8): what ran, the counts per configuration, what the counts can and cannot show, each confirmed
detection with the checklist question behind it, and the misses. The runner's own report, built by
`python3 scripts/run_review_benchmark.py --report --stage B`, is kept verbatim at the end.

## What ran

- **Key and rule:** answer key `7ef0a579…` (version 2, 17 cases), match rule `0db53541…`, committed before any run;
  stage lists at `04f8df4` (after 4.4's critique and implementation review).
- **Reviewer:** Opus (`claude-opus-5-5`), initial reviews at high effort, rechecks at medium, CLI 2.1.321; Sonnet
  (`claude-sonnet-5-5`) only as the second confirmer.
- **Calls:** 57 of the 60 allowed: 6 for three canary pairs (see below), 45 first runs, 4 repeats, 2
  second-confirmer sessions. The failed-Read probe and the planting of FS-1 and FS-2 ran outside the budget, as
  S45-D1 allows.
- **Configurations:** `short+list` (stage A's short prompt without its retired kinds sentence), `open+list` (4.1's
  mandate, the launcher's today), `open-B+list` (4.4's drafted initial mandate), `recheck-A` (4.1's recheck mandate)
  and `recheck-B` (4.4's drafted recheck mandate). Every configuration carries its case's stage list.

## Counts

Detections are the author's blinded verdicts (S45-D7) on 125 exported findings: 29 match. Two of them, T008 and T047
(RM-6, `open+list`, its repeat), were first judged no match and changed after unblinding, at the final review's
challenge (FR-1): both meet the match rule's absence clause (an untested path of the launcher, named anywhere in the
finding) exactly as T043, which was accepted blind. The first-run counts do not change; the repeat does. Cost and minutes include
the failed reviews.

| Configuration | Detected (of 11 defect cases) | 95% interval | By a blocking finding | False alarms (no-defect reviews) | False blockers (all completed reviews) | Unread files | Failed | Cost USD per detection |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `short+list` | 6 | 0.23–0.83 | 6 | 2 (4 reviews) | 6 | 42 | 1 | 1.91 |
| `open+list` | 7 | 0.31–0.89 | 5 | 2 (4 reviews) | 7 | 42 | 1 | 1.75 |
| `open-B+list` | 6 | 0.23–0.83 | 5 | 4 (2 reviews) | 7 | 50 | 1 | 2.02 |
| `recheck-A` | 1 of 1 | 0.02–1.00 | 1 | — | 0 | 0 | 0 | 0.19 |
| `recheck-B` | 1 of 1 | 0.02–1.00 | 1 | — | 0 | 0 | 0 | 0.18 |

- **Discordant cases,** `short+list` against `open+list`: only `short+list` FS-1; only `open+list` FS-2 and RM-6.
  `open+list` against `open-B+list`: only `open+list` PB-3 and RM-6; only `open-B+list` FS-1.
- **Repeats** (S45-D6, by confirmed verdicts): FS-2 `open+list` detected twice, `short+list` missed then detected;
  RM-6 `open+list` detected twice (its second detection is one of the two re-judged findings above), `short+list`
  failed then missed. The repeat rule (discordant cases where both
  first reviews completed first, then the others in the key's order) was written after the first runs, with the
  three discordant cases known; it chose FS-2 and RM-6, the two that favoured `open+list`, and left out FS-1, the one
  that favoured `short+list`. FS-2's repeats moved toward agreement; RM-6's kept the difference.
- **Rating agreement** where a case and configuration ran twice and both runs completed, by expected defect: the two
  runs rated it the same once and differently twice (detected or not, and at which severity).
- **Failed reviews count as misses** (4.5a): RM-6 `short+list` and PB-3 `open-B+list` read none of the files under
  review (the empty-review rule); FS-1 `open+list` was withheld because the publication check found a
  credential-shaped value in its report, although the prompt asks for `<token>`. FS-1's defect is a credential in an
  audit event, so a review that describes it concretely is the most likely to trip the check: this withheld review
  may well have been a detection, and it makes FS-1 the one discordant case that favours `short+list`.
- **False blockers and unread files.** Every setup raised 6 or 7 blocking findings at no expected place across its
  15 reviews, and left 42 to 50 files under review unread. These are candidates, counted automatically: stage A's
  author judged each such finding by hand and found none false in 17 reviews, while here none was judged, and some
  are real defects of the reviewed commits that the key does not list.
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
raised the most findings on the no-defect cases. The repeats were chosen after the first runs (see above), and the
recheck case cannot show the opposite failure of a recheck, re-raising answers that hold (decision concern 4).
Every configuration carries the lists, so the counts do not measure the lists' own effect.

## The canary

Three canary pairs ran under CLI 2.1.321, the version of every stage-B review. The first two used the launcher's
review prompt, whose mandate tells every reviewer to treat files as data; both twins ran the planted hook and
declined the planted `CLAUDE.md`, the second worded as an ordinary project convention. That was the author's 4.5a
choice of prompt, not S45-D9 (4.5b report review, B2). The third pair got its own prompt, which asks to follow the
instructions the session holds: its twin, without the launcher's flags, followed `CLAUDE.md` (CANARY-BRAVO) and ran
the hook, and the confined reviewer followed neither. So the canary is valid and passes, as S45-D9 asks, for the CLI
version the reviews ran under; the runner again requires that before any stage-B review. The failed-Read probe
confirmed that a Read that fails is marked as an error and never counts as read.

## Each confirmed detection and the checklist question behind it

Where the finding's own text cites a question of its stage list, that is given; otherwise the question that asks
about the defect, by the author's mapping after the fact, is marked *(author)*. The reviewer schema has no field for
the question, so most findings cite none (discovered issue 11).

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

## For the owner's choice

- **Default setup:** `short+list` or `open+list`; the counts do not separate them.
- **Initial mandate wording:** 4.1's (`open+list`) or the draft (`open-B+list`); 7 against 6 detections, 2 against
  4 false alarms, within chance.
- **Recheck mandate wording:** 4.1's or the draft; both detected the false fix; neither was tested on answers that hold.
- **Final mandate wording:** by reason; no case measures it (S45-D8).

The launcher's mandate constants stay 4.1's until the owner chooses (S45-D8).

## The runner's report, verbatim

````markdown
Stage B. Answer key SHA-256: `7ef0a57963ff33c5b8397eedcf145cedbf3807c8b4a6b7ac09cd29ab4706f899`; match rule SHA-256: `0db53541df45fbcfa09041d611f11aded4cbfe44b8b28474960add5abc874dcd`; lists at `04f8df4`.

Detections are confirmed by the author's blinded verdicts.

| Configuration | Detected | 95% interval | Detected (blocking) | False alarms (no-defect reviews) | False blockers | Failed | Unread files | Not yet confirmed | Cost USD per detection | Minutes per detection |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open+list | 7 of 11 | 0.31–0.89 | 5 | 2 (4) | 7 | 1 | 42 | 0 | 1.75 | 5.2 |
| open-B+list | 6 of 11 | 0.23–0.83 | 5 | 4 (2) | 7 | 1 | 50 | 0 | 2.02 | 5.9 |
| recheck-A | 1 of 1 | 0.02–1.00 | 1 | 0 (0) | 0 | 0 | 0 | 0 | 0.19 | 0.4 |
| recheck-B | 1 of 1 | 0.02–1.00 | 1 | 0 (0) | 0 | 0 | 0 | 0 | 0.18 | 0.4 |
| short+list | 6 of 11 | 0.23–0.83 | 6 | 2 (4) | 6 | 1 | 42 | 0 | 1.91 | 5.5 |

Discordant cases, short+list against open+list: `{"only short+list": ["FS-1"], "only open+list": ["FS-2", "RM-6"]}`
Discordant cases, open+list against open-B+list: `{"only open+list": ["PB-3", "RM-6"], "only open-B+list": ["FS-1"]}`
Rating agreement where a case ran twice, by expected defect: `{"same": 1, "different": 2}`
Origin stage of the findings against the list of the review that found them: `{"architecture and interfaces": {"architecture-and-interfaces": 11, "code": 13, "e2e-tests": 1, "requirements": 1}, "discovery": {"code": 1, "plan-and-test-plan": 13}, "implementation": {"code": 94, "e2e-tests": 15, "plan-and-test-plan": 16, "requirements": 15}, "requirements": {"code": 1, "e2e-tests": 1, "plan-and-test-plan": 10, "requirements": 27}, "tests first": {"code": 30, "e2e-tests": 32, "plan-and-test-plan": 23, "requirements": 1}, "unknown": {"architecture-and-interfaces": 1}}`
Canary: `[{"cli_version": "2.1.321 (Claude Code)", "valid": false, "passed": true, "twin_ran_hook": true}, {"cli_version": "2.1.321 (Claude Code)", "valid": false, "passed": true, "twin_ran_hook": true}, {"cli_version": "2.1.321 (Claude Code)", "valid": true, "passed": true, "twin_ran_hook": true}]`. A canary is valid when its twin, without the launcher's flags, followed the planted CLAUDE.md and ran the planted hook (S45-D9); one whose twin ran only the hook shows that the flags keep settings out, not that they keep instruction files out.
Repeats (detected in run 1, run 2): FS-2 open+list: True, True; FS-2 short+list: False, True; RM-6 open+list: True, True; RM-6 short+list: failed, False
Second confirmer: agrees with the author on 9 of 10 sampled findings.

What these sizes can show: with about 15 cases and one run each, a difference of two or three cases between two configurations is within chance; the intervals say how wide each count's uncertainty is. Both setups carry the stage lists, so the counts do not measure the lists' own effect. The owner decides from the counts; no rule decides.

Per-review rows: the automatic first pass, before confirmation; the counts above are confirmed.

| Case | Kind | Prompt | Status | Verdict | Detected | Detected (blocking) | Location only | Not blocking | Unmatched blocking | Unmatched (blocking or high) | Tries |
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

Detected: a blocking or high finding at the expected place with one of its terms; Detected (blocking): the same, by a blocking finding; Not blocking: a match rated medium or low (stage A: advisory); Unmatched blocking, and Unmatched (blocking or high): findings at no expected place, the false blockers and false alarms on a clean case.
````
