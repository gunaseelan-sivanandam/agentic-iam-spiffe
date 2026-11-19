# Review checklist — requirements

The minimum questions for reviewing changes to `docs/requirements.md`, and the author's guideline before writing it (S44-D8). The open mandate comes first: these questions are a floor, not the limit of the review. Each question names its source in [research.md](../slices/poc-4-4-stage-checklists/research.md).

## Questions

1. Is each new or changed requirement verifiable: can the criteria for its verification be stated, and is it free of unverifiable terms such as flexible, easy, sufficient, safe or adequate? [S:nasa-req]
2. Does each requirement state what is needed, not how to provide it? [S:nasa-req]
3. Is each requirement clear and unambiguous, without indefinite pronouns or ambiguous terms? [S:nasa-req]
4. Does a requirement contradict another requirement, the threat model, or a requirement of a related part? [S:nasa-req]
5. Does every new or changed requirement have a test or check that proves it in `trace/tests.yaml`? [S:owner]
6. Does each requirement have a source and a rationale, the reason it is needed? [S:reqview-29148]
7. Are the assumptions a requirement rests on stated? [S:nasa-req]
8. Is the terminology the same as in the rest of `docs/requirements.md`? [S:nasa-req]
9. Does a security requirement name the asset and its holders, so that a deployment check can test it? [S:stride]

## Blocks at this stage

Besides the blocking criteria of every stage (`AGENTS.md`, Review findings), a finding blocks here when:

- a requirement no test or check could verify;
- a requirement contradicts another or the threat model;
- a new or changed requirement has no proof while the change claims it is proved.
