# Slice Bundles

Use a per-slice review bundle for milestone and security-relevant changes.

## Goal
Make security-relevant behavior visible in authored records before it exists in code.

Each slice bundle is the review unit for:
- requirement changes
- architecture changes
- authoritative state inventory
- ADR/DDR decisions
- implementation contract
- retirement and cleanup contract

## Folder layout
Create one folder per slice, for example:

```text
docs/slices/m4-capiss-observability/
```

Start from:

```text
docs/slices/_template/
```

## Implemented slice bundles
- `docs/slices/m4a-jira-project-access/`: implemented M4a bundle for Jira project reads with a broad upstream credential narrowed by capiss, OPA, and `jira-tool`.
- `docs/slices/m4b-jira-description-write/`: implemented M4b bundle for project-scoped Jira description writes using the M4a Jira boundary.

## Required files
- `plan.md`
- `requirements_delta.md`
- `architecture_delta.md`
- `adr.md`
- `ddr.md`
- `implementation_contract.md`
- `retirement_contract.md`
- `validation.md`

## 4-phase workflow
1. `Phase 1: plan and review`
   - complete the slice bundle
   - do not implement before review
2. `Phase 2: tests`
   - create UT/E2E from the approved bundle
   - if tests require a new assumption, return to Phase 1
3. `Phase 3: implementation`
   - implement only approved behavior
   - remove obsolete logic and artifacts listed in the retirement contract
4. `Phase 4: verification`
   - run trace, quality, E2E, and evidence checks
   - summarize the result in `docs/local_status_capture/implementation_status.md`

## Authoritative state inventory rule
If a decision depends on hidden state, `architecture_delta.md` must list:
- state/key name
- store/system
- writer
- reader
- TTL or lifecycle
- decision impact
- authoritative vs advisory

This is mandatory for security-relevant Redis, file, cache, policy, or derived-state behavior.

## Retirement rule
Every slice must explicitly state:
- what old logic is being removed
- what compatibility behavior is being kept temporarily, if any
- what stale docs/tests/artifacts must be deleted or archived

If nothing is retired, say so explicitly in `retirement_contract.md`.
