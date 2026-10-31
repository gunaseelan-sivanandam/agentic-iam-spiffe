# Slice Plan — backlog-issues

## Goal
- Track open work (proposed slices, actions only the user can take) as GitHub issues instead of the
  growing `docs/slices/agentic-delivery-process/later_slices.md`, so each item has an open or closed
  state and a PR closes it on merge.

## Grill-Me Review Summary
- No grill-me: the user asked for this change (2026-10-31) and approved the proposal in the session
  ("merged", in reply to "Should I go ahead on that basis?" after PR #12). Plan and implementation
  share one PR because the change touches documents only.
- Issues track what is open; the repository keeps what reviews and gates read. The independent
  reviewer (Codex, read-only, no network) cannot read issues, so a slice's grill-me copies its issue
  into `plan.md`.
- The open problem log and the delivery problem log stay in the repository: the register's
  `known_violations` name open OPLs, and the DPL log is the learning record.
- `later_slices.md` is frozen with a note, not moved: it is part of the implemented
  `agentic-delivery-process` bundle, and frozen records link to it.
- Two labels: `slice` and `user-action`.

## Requirements
- None added or changed.

## Success criteria
- Issues #13 to #18 exist: `gate-register`, `asset-classification`, 100% coverage, slice 3 (review
  design and orchestration), the pilot (OPL-005 to OPL-008), and the "Automatically delete head
  branches" setting (DPL-008).
- `later_slices.md` says it is frozen and where its open items went; slice 3's issue links its
  drafts at commit `aa1f0d4`.
- `AGENTS.md` names issues in "Start here" and step 4; `docs/STATUS.md` links the issues for next
  work; slice 2 is shown as implemented.

## In scope
- The six issues and two labels; the `later_slices.md` note; `AGENTS.md`, `docs/STATUS.md`,
  `docs/slices/README.md`, the implementation log.

## Out of scope
- Moving OPL or DPL entries to issues; any gate checking issues; deciding any slice's content.

## Assets and holders
- None. Issues are public (the repository is public) and hold planning text only.

## Environment facts
- `gh repo view --json hasIssuesEnabled,isPrivate,deleteBranchOnMerge` (2026-10-31): issues enabled,
  public, automatic branch deletion off. No issues existed; the last PR was #12, so new issues start
  at #13.
- Labels `slice` and `user-action` created through the GitHub API (2026-10-31). Creating the issues
  from the agent session was refused by the session's permission check; the user runs
  `gh issue create` for the six prepared bodies.

## Hidden-state and trust decisions
- No hidden state is introduced or changed.

## Authored source changes
- Requirements: none.
- Architecture: none.
- Runtime proof: none.
- Rulebook (`AGENTS.md`): a "Start here" row for GitHub issues; step 4 opens an issue for work found
  but not done and closes finished issues with `Closes #N`.

## Retirement and compatibility
- `later_slices.md` is no longer updated (frozen note); the unmerged branch `later/gate-register`
  is replaced by issue #13; its local copy is deleted, and the pushed branch is deleted once the user
  agrees.

## Review notes
- None.
