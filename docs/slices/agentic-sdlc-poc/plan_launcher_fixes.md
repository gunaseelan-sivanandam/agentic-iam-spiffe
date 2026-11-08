# Plan — fixes to the review launcher and the secret check found by slice 4's plan reviews

Short plan of four commits on `poc/slice-4-plans` that fix code merged with slices 2 and 3. It was
written after the fixes, because plan review 4.6 (A12) and the fixes review (A5) pointed out that
every change needs a plan, however small. The owner approves it with slice 4's plan PR.

Status: implemented on `poc/slice-4-plans` (`f070669`, `d56c69a`, `f8b6200`, `8d80ce8` and the commit that adds this line), 2026-11-08;
reviewed as unit `launcher_fixes` ([`review_launcher_fixes.md`](review_launcher_fixes.md)).

## Problem

Slice 4's six plan reviews were the first to run in parallel through the launcher
(`scripts/run_independent_review.py`), with the same unit name, on prose about this repository. Three
defects showed up ([DPL-011](../../delivery_problem_log.md#dpl-011-slice-2s-launcher-and-the-secret-check-broke-on-slice-4s-parallel-plan-reviews)):
- five of six round-1 reports were lost, because every report of unit `plan` went to one file;
- a review failed because the reviewer called `Bash`, which the CLI does not offer, so it ran nothing;
- the publication check withheld four correct reports, because its credential rule
  (`scripts/evidence_secrets.py`) read words after `Authorization:` in prose and code as values.

## Threat model

The delivery threat model of `AGENTS.md` (honest mistakes). For this change: a lost or overwritten
report; a review failed for a call that never ran, or passed after one that ran; a correct report
withheld, or a real credential published.

## Decisions

| ID | Decision | Source |
| --- | --- | --- |
| F1 | The report path includes the record's slice directory: `artifacts/reviews/<slice dir>/<unit>/<attempt>.json`. | default (the slice directory already separates attempt logs) |
| F2 | A call to a tool other than Read, Grep and Glob fails the review, as R5-A4 decided, except a call to a tool that the session's init event did not offer, answered with an error: it cannot have run, so it is logged as `other_tools_not_offered`. A stream without a tool list fails closed. | R5-A4 (slice 2); fixes review round 1, A1; default (the init list as the evidence) |
| F3 | A credential line counts only when its value is token-like: 20 characters or longer, or with a digit. Every credential this system handles is (capiss and Jira tokens, SVIDs, Basic credentials). | default; decision concern for the owner (it narrows EVID-T1's rule) |
| F4 | The credential rule finds a value in a Markdown code span of any fence length, or in quotes escaped any number of times, before or after the scheme. A value ends at a backslash: no credential holds one, and JSON writes an ellipsis after the header name as `\u2026`, which has digits. | plan review 4.4, A9; fixes review round 1, A2; the author, when a released report quoting "Bearer …" failed the widened rule |

## Tests

`tests/tools/test_run_independent_review.py`: two slices with the same unit keep separate reports; a
call to a tool the CLI does not offer completes; an offered tool that ran with an error fails; a
stream without a tool list fails. `tests/tools/test_evidence_secrets.py`: prose and code forms of the
header are not credentials; boundary values for length and digit (EVID-T1's negative controls); code
spans, quotes and JSON-escaped values are found; `AGENTS.md` passes the check.

## Retirement

The draft's code-span placeholder (in `f070669`) is removed by F4. Nothing else is retired.

## For the owner

F3 narrows the rule that `AGENTS.md`'s E2E evidence row states, and F2 refines R5-A4. Both need the
owner's confirmation in the plan PR (fixes review round 1, D1).
