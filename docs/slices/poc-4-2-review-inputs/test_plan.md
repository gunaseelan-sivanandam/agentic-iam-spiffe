# Slice Test Plan — poc-4-2-review-inputs

Test plan of slice 4.2 of the agentic-SDLC PoC (issue #39): the tests that show the launcher picks
every changed file, names upstream items and computes evidence without the author's help.

## Goal

Prove S42-D1 to S42-D8 of [`plan.md`](plan.md):
- no changed file can be left out of the review;
- upstream items are found or reported as absent;
- evidence comes from tools, with failures shown as failures.

## Inputs

- Plan: [`plan.md`](plan.md), decisions S42-D1 to S42-D8.
- Expected values come from the plan or from probes before the change, never from the new code.

## Unit test plan

Tooling tests in `tests/tools/` with the fake `claude` CLI and throwaway Git repositories, as in
slice 2.

| Area | Passes when | Fails or refuses when | Proves | Source |
| --- | --- | --- | --- | --- |
| File list | Without `--path`, every file the change adds, modifies or renames is under review. With `--path`, the named files come first and the rest follow. | A `--path` not in the diff is refused before any call. A file the change deletes is not listed. The withheld files are never listed. | S42-D1 | plan |
| Open every file | The paths section says every listed file must be opened | A review that opened none of them fails (the existing rule still holds) | S42-D2 | plan; `existing@c325e7d` |
| Upstream items | A change to a file named on an `Implemented by:` line, or to a function with a `DD` tag, names its `ARCH` and `REQ` items. A change inside a slice bundle names that bundle's `plan.md`. | A change with no link says "no upstream item found" instead of an empty section | S42-D3 | plan |
| Upstream question | Every prompt contains the question verbatim | — | S42-D4 | plan |
| Evidence | The evidence section shows the coverage of a changed script with its command, new trace gaps against the base, and the CI job conclusions of a named run (from a fake API response). Evidence is computed from the reviewed commit, not the working tree: an uncommitted edit does not change it. | A failing evidence command appears as "failed: <command>: <reason>", never as 100% or empty | S42-D5, S42-D6 | plan |
| Required diff base | `make_frozen_copy` without a diff base is a type error caught by the tests' call sites | — | S42-D7 | plan |
| Benchmark paths | A benchmark case's paths come first, and the rest of the diff follows | — | S42-D8 | plan |

## E2E test plan

None.

## Assumptions and fixtures

- CI results come from a fake API response in tests; the live call is exercised once, at slice 4's
  close.
- Coverage evidence for subprocess-run scripts reads "not measurable" until #44 is closed. A test
  pins that wording.

## Planned verification commands

- `make tooling-test`
- `make lint`
- `make qa-quality`

## Independent review at the implementation PR

After the open mandate, the reviewer answers in the PR body:
1. *Tests:* for each new test, which wrong behaviour would still pass it?
2. *Keys:* can the evidence or the upstream list carry a secret or an operational detail (a local path,
   an account) into a prompt or a public record?
3. *Names and headers:* do new names and files say what they do?

A "yes" to question 1 or 2 blocks.
