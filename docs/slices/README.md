# Slice Bundles

Use a per-slice review bundle for milestone and security-relevant changes.

## Goal
Make security-relevant behavior visible in authored records before it exists in code.

Each slice bundle is the review unit for:
- requirement changes
- architecture changes
- agreed design choices
- hidden-state decisions
- UT and E2E proof planning

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
- `docs/slices/m4a-jira-project-access/`: implemented M4a bundle for Jira project reads with a broad upstream credential narrowed by capiss, OPA, and `jira-tool`. This slice predates the simplified two-document Phase 1 workflow and still contains legacy planning artifacts.
- `docs/slices/m4b-jira-description-write/`: implemented M4b bundle for project-scoped Jira description writes using the M4a Jira boundary. This slice predates the simplified two-document Phase 1 workflow and still contains legacy planning artifacts.
- `docs/slices/m5-codex-jira-mcp-slice-1/`: M5 Slice 1 bundle for Codex-to-Jira MCP project summaries and story creation through a separate adapter, capiss authority family, Envoy boundary, gateway PEP, and deterministic `jira-mcp-mock`.

## Required files
- `plan.md`
- `test_plan.md`

## 4-phase workflow
1. `Phase 1: plan and review`
   - start with the `grill-me` skill
   - ask and resolve design questions one branch at a time until the slice choices are agreed
   - capture the final design choices, requirements to change or add, hidden-state decisions, in-scope work, out-of-scope work, and retirement expectations in `plan.md`
   - create `test_plan.md` with UT and E2E coverage derived from the agreed choices and requirements
   - do not implement before review
2. `Phase 2: tests`
   - create UT/E2E from the approved `test_plan.md`
   - if tests require a new assumption, return to Phase 1
   - update authored requirements, architecture, trace mappings, and process docs before making runtime code pass the tests
3. `Phase 3: implementation`
   - implement only approved behavior
   - remove obsolete logic and artifacts listed in `plan.md`
4. `Phase 4: verification`
   - run trace, quality, E2E, and evidence checks
   - summarize the result in `docs/local_status_capture/implementation_status.md`

## Hidden-state rule
If a decision depends on hidden state, `plan.md` must list:
- state/key name
- store/system
- writer
- reader
- TTL or lifecycle
- decision impact
- authoritative vs advisory

This is mandatory for security-relevant Redis, file, cache, policy, or derived-state behavior.

## Retirement rule
Every `plan.md` must explicitly state:
- what old logic is being removed
- what compatibility behavior is being kept temporarily, if any
- what stale docs/tests/artifacts must be deleted or archived

If nothing is retired, say so explicitly in `plan.md`.
