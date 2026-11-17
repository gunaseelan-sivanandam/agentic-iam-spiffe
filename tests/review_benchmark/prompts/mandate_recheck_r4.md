# Round-4 recheck mandate of the review benchmark

The recheck mandate the owner approved in round 4 of slice 4 (R4-1 of `docs/slices/agentic-sdlc-poc/slice_4_decisions.md`), which the benchmark's configuration recheck-R4 puts in place of the launcher's own, so that it is measured before it ships (R4-4). It is R4-1's text verbatim, one line per paragraph; the runner sends only the text under the heading below.

## Mandate

Verify every author answer to your earlier findings against the owner-approved plan and the owner's recorded decisions (for a plan review, the owner's request) and the actual files and evidence. Read every file an answer names or cites and the relevant tests. Read the surrounding implementation, dependencies and documentation to understand the effects of the fixes.

Existing behavior, implementation choices and the author's explanations do not establish approval. Neither your earlier finding nor the author's response is automatically correct. Accept an answer when the lines you read show it is right; re-raise the finding under its existing ID when they show the problem remains, and say what remains; report cannot determine when they show neither. Account for every answer.

Report problems introduced or exposed by the fixes, including departures from the plan. Refer unresolved material design decisions to the owner. A recheck that raises no new findings is valid.
