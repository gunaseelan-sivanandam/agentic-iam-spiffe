# Review checklist — a plan and its test plan

The minimum questions for reviewing a slice's `plan.md` and `test_plan.md`, and the author's guideline before writing it (S44-D8). The open mandate comes first: these questions are a floor, not the limit of the review. Each question names its source in [research.md](../slices/poc-4-4-stage-checklists/research.md).

## Questions

1. Does every decision name its source: the owner's words with the date and a link, or "default by the author" with a reason? [S:reqview-29148]
2. Does every new or changed requirement or decision have a test or check that proves it, named in the test plan? [S:owner]
3. Does every new check run as its own required CI job, named after it? [S:owner]
4. For each expected outcome in the test plan: does it come from the plan or a probe, and which wrong behaviour would still pass the test? [S:google-looking-for]
5. Which keys, sockets and secrets does the slice touch, and can any reach a service outside its holders in `security/invariants.yaml`? [S:stride]
6. Is every fact outside the repository that a decision depends on recorded with the probe that showed it? [S:nasa-req]
7. Do the decisions contradict each other, the requirements, the architecture or the approved threat model? [S:nasa-req]
8. Where a fix answers a review finding, does it change the upstream choice that caused it before adding a mechanism? [S:google-looking-for]
9. Can each success criterion be checked by someone other than the author, with what the plan names? [S:nasa-req]

## Blocks at this stage

Besides the blocking criteria of every stage (`AGENTS.md`, Review findings), a finding blocks here when:

- a decision or new requirement has no test or check that proves it;
- a decision contradicts another, the requirements, the architecture or the threat model;
- the plan lets a key, socket or secret reach a service outside its holders.
