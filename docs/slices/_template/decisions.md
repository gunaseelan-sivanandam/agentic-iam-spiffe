# Slice Decisions

Decision page of slice `<slice-id>`: the user's one page for the slice, which the PR body links. It
holds everything that needs the user; the plans and review records are the working documents.
Replace this paragraph; it is the document's purpose line (`AGENTS.md`, coding rule 8). Keep the
page short: a small slice's page may be a few lines, and a section with nothing in it says "none".

Last updated: <date>: <where the slice stands>.

## Goal

The user's goal in the user's words, with the date and a link.

## What the slice builds

In plain words, a few lines or one row per part.

## Decisions made

| When | Decision | The user's words |
| --- | --- | --- |
| <date> | One decision per row, including the plan's defaults the user confirmed by merging it | "<the user's words>" |

## Decisions to make

| # | Decision | Options | Recommendation | Blocks |
| --- | --- | --- | --- | --- |
| 1 | What the user must decide, explained so that it can be decided from this page | <option>; <option> | the author's recommendation and why | what waits for it, or nothing |

## Decision concerns

Agreed decisions that themselves seem to cause a problem ([`AGENTS.md`, Independent review, Report
sections](../../../AGENTS.md#independent-review)); the author never applies one.

| # | Concern | Found by | The author's recommendation | Status |
| --- | --- | --- | --- | --- |
| 1 | The decision and the problem it causes | the review and finding, or the author | | open, or decided with the user's words |

## Discovered issues

Every issue found during the work, whether pre-existing, introduced by the change, unrelated or
outside the threat model ([`AGENTS.md`, PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion)).

| # | Issue | Found by | Disposition | Tracking |
| --- | --- | --- | --- | --- |
| 1 | What is wrong | the stage, review or person that found it | fixed, deferred, outside the threat model, … | the issue link, or none |

## Implementation review: the test-plan questions

The implementation review answers the three questions of `test_plan.md` as findings in its report.
For each question, the IDs of the findings that answer it, or "no finding":

1. *Tests:* <finding IDs, or no finding>
2. *Keys:* <finding IDs, or no finding>
3. *Names and headers:* <finding IDs, or no finding>

## Review outcome

At handoff, replace this paragraph with the output of
`python3 scripts/review_brief.py --base origin/<integration branch>`.

## How the user can check the work

- What the user can look at, run or plant to see that the slice does what it claims.
