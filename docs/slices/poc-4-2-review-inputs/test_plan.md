# Slice Test Plan — poc-4-2-review-inputs

Test plan of slice 4.2 of the agentic-SDLC PoC (issue #39): the tests that show the launcher picks
every changed file, names upstream items and computes evidence without the author's help.

## Goal

Prove S42-D1 to S42-D11 of [`plan.md`](plan.md):
- no changed or deleted file can be left out of the review;
- the governing plan and the other upstream items are named;
- evidence comes from tools, for the reviewed commit, with failures shown as failures and every entry
  accounted for.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S42-D1 to S42-D11.
- Expected values come from the plan or from probes before the change, never from the new code.

## Unit test plan

Tooling tests in `tests/tools/` with the fake `claude` CLI and throwaway Git repositories, as in
slice 2.

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| File list | Without `--path`, every file the change adds, modifies or renames is listed to open, and every deleted file is listed under "deleted by the change". With `--path`, the named files come first and the rest follow. | A `--path` not in the diff is refused before any call. The withheld files are never listed. | S42-D1 | plan |
| Open every file | The paths section says every listed file must be opened; a recheck's says to open the answered files first. `paths_not_read` in the end entry lists the listed files the stream shows unread. | A review that opened none of the `--path` files fails, even when it opened other listed files | S42-D2 | plan; `existing@c325e7d` |
| Governing plan | A change that touches no file of its own bundle still names the plan of the `--record` bundle and its decision IDs | — | S42-D3 | plan |
| Upstream items | A changed file on an `Implemented by:` line, or with a `DD` tag, names its `ARCH` and `REQ`. A changed `REQ` heading and a changed `trace/tests.yaml` entry are named, the latter with its requirements. A changed file in another bundle names that bundle's plan. | — | S42-D3 | plan |
| Upstream question | Every prompt contains the question verbatim | — | S42-D4 | plan |
| Uncovered lines | A changed script with an untested new branch lists that branch's lines; the #44 note is present; a changed `services/` file names its gate, or "no coverage gate" | — | S42-D5 | plan |
| Trace gaps | A gap on an upstream item is listed and marked new, existing or accepted | — | S42-D5 | plan |
| CI results | The jobs of a run whose head is the reviewed commit are shown, from a fake API response | A run of another commit is never shown; no matching run shows "no CI run for this commit" | S42-D5 | plan |
| Evidence from the commit | An uncommitted edit in the working tree does not change the evidence | — | S42-D5 | plan |
| Accounted entries | A report listing every evidence entry as `explained` or `flagged` completes | A report that leaves out an entry fails; a `flagged` entry naming no finding of the report fails | S42-D6 | plan |
| Failures shown | A failing command shows "failed: <command>: <reason>"; a test run with a failing test shows coverage and the test's name; the start entry holds each item's status | A failed coverage run never shows "100%" or no entries | S42-D7 | plan |
| Clean environment | The evidence commands see only `PATH`, `LANG` and a scratch `HOME`; output paths are relative | Evidence holding the author's `HOME` path or the scratch root is refused before any call | S42-D8 | plan |
| Evidence hash | The start entry's evidence SHA-256 matches the evidence text in the prompt | — | S42-D9 | plan |
| Required diff base | Calling `make_frozen_copy`, `build_prompt` or `invocation_from_entry` without `diff_base` raises `TypeError`; every prompt names `change.diff` | — | S42-D10 | plan |
| Benchmark inputs | A case's paths come first, the rest of the diff follows, upstream items are named, and no evidence section entries appear | — | S42-D11 | plan |

## E2E test plan

None.

## Assumptions and fixtures

- CI results come from a fake API response in tests; the live call runs once, at slice 4's close.
- Coverage tests use a throwaway repository with a script imported by its test, and one run as a
  subprocess.

## Planned verification commands

- `make tooling-test`
- `make lint`
- `make qa-quality`

## Independent review at the implementation PR

After the open mandate, the reviewer answers in the PR body:
1. *Tests:* for each new or changed test, which wrong behaviour would still pass it?
2. *Keys:* does a key, socket or secret now reach a service outside its holders? Can the evidence or
   the upstream list carry a secret or an operational detail (a local path, an account) into a prompt
   or a public record?
3. *Names and headers:* do new names and files say what they do?

A "yes" to question 1 or 2 blocks; findings on question 3 follow the severity rules.
