# Slice Test Plan — backlog-issues

## Goal
- None: the change moves planning text and adds two rulebook lines; no behaviour or gate changes.

## Inputs
- [`plan.md`](plan.md).

## Unit test plan
- None.

## E2E test plan
- None.

## Assumptions and fixtures
- None.

## Planned verification commands
- `make docs-check` (links in the changed documents resolve).
- `make qa-quality` (nothing else is affected).
- Check by hand that every open item of `later_slices.md` is in an issue or deliberately left in
  the frozen record.

## Review notes
- None.
