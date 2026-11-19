# Review checklist — unit tests

The minimum questions for reviewing unit and tooling tests, and the author's guideline before writing it (S44-D8). The open mandate comes first: these questions are a floor, not the limit of the review. Each question names its source in [research.md](../slices/poc-4-4-stage-checklists/research.md).

## Questions

1. Will each new or changed test fail when the code it covers is broken? Name the wrong behaviour that would still pass it. [S:google-looking-for]
2. Does every new or changed requirement or decision have a test or check that proves it? [S:owner]
3. Does each test check observable behaviour rather than the code's internal structure? [S:fowler-pyramid]
4. Does each test assert something, and say what each assertion checks when it has several, with no assertion that is always true? [S:test-smells]
5. Does conditional logic inside a test change what it checks? [S:test-smells]
6. Does every fail-closed or refusal path of the new code have a test that triggers it? [S:owasp-code-review] [S:google-looking-for]
7. Does a test depend on files or services outside its own fixture (other than the repository files it exists to check), on the order of tests, on sleeps or on the clock? [S:fowler-nondeterminism] [S:test-smells]
8. Does a test assert an error path explicitly rather than catching and ignoring the error? [S:test-smells]
9. Are the literal values in assertions explained, for example as boundary values below, at and above a limit? [S:test-smells]
10. Does each fake, stub or mock behave like the real dependency in what the test relies on, as a recorded probe or a contract test shows, and does each check get the kinds of input it will meet in use? [S:fowler-pyramid]

## Blocks at this stage

Besides the blocking criteria of every stage (`AGENTS.md`, Review findings), a finding blocks here when:

- a test that can pass while the behaviour it claims to prove is broken (a false green);
- a decision of the approved plan without a test;
- a fail-closed path of a security decision of the system under test (an enforcement or validation path, coding
  rule 4) without a test that triggers it.
