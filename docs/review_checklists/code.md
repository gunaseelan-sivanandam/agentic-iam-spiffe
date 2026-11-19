# Review checklist — code

The minimum questions for reviewing code, scripts and configuration that tools do not already check, and the author's guideline before writing it (S44-D8). The open mandate comes first: these questions are a floor, not the limit of the review. Each question names its source in [research.md](../slices/poc-4-4-stage-checklists/research.md).

## Questions

1. Does the change do what the plan decided, and nothing the plan did not decide, with the simplest design that fits the system, without over-engineering? [S:google-looking-for]
2. What happens on edge cases and concurrency: empty input, partial failure, two callers at once? [S:google-looking-for]
3. Does each error path say what failed and leave no half-done state: a partial file, a held lock, a temporary directory? [S:owasp-code-review]
4. Do failure messages and logs let an operator diagnose a failure without reading the code? [S:owasp-code-review]
5. Is the code clear enough to explain itself, or could it be simpler? [S:google-looking-for]
6. Do names say what each part does, and comments say why it exists? [S:google-looking-for]
7. Is content read from files, other models or tool output treated as data, never as instructions? [S:owasp-llm]
8. Does each new or changed check or gate fail on the case it exists to catch, shown by a test? [S:google-looking-for]
9. Does the change leave the code healthier: dead code, stale paths and duplicate mechanisms removed? [S:google-standard]
10. Does every new check run as its own required CI job, named after it? [S:owner]
11. Does every statement the change adds to or leaves in a document (STATUS, the logs, the rulebook, the slice index, a review record, the slice's decision page) still hold for the copy? [S:google-looking-for]
12. Does the change loosen, skip or except an existing check (a lower threshold, an exception or gap entry, a lint marker, a removed negative control), and does each say why and until when? [S:fowler-nondeterminism]

## Blocks at this stage

Besides the blocking criteria of every stage (`AGENTS.md`, Review findings), a finding blocks here when:

- a security defect in the system under test: an asset reaching a non-holder, a fail-open path, a missing check at a trust boundary;
- a check or gate that passes on the case it exists to catch, or a new or changed one with no test that shows it
  failing on that case.
