# Review checklist — E2E tests

The minimum questions for reviewing the E2E harness, `trace/tests.yaml` and `docs/test_spec.md`, and the author's guideline before writing it (S44-D8). The open mandate comes first: these questions are a floor, not the limit of the review. Each question names its source in [research.md](../slices/poc-4-4-stage-checklists/research.md).

## Questions

1. Can each outcome guard fail? Name the wrong outcome that would still pass it: another status, another component answering, an empty file read as success. [S:google-looking-for]
2. Does every new or changed requirement have a test or check that proves it: an E2E or static test in `trace/tests.yaml`? [S:owner]
3. Does each negative test have a positive twin on the same route that passes in the same run? [S:google-looking-for]
4. Is the test deterministic: no bare sleeps, and no dependence on another test's state? [S:fowler-nondeterminism]
5. Does any evidence a test leaves hold a secret, a token value or key material? [S:owasp-code-review]
6. Does the test exercise the system through its real boundary (the proxy and its mutual TLS), not around it? [S:fowler-pyramid]
7. Is the test isolated from live external services unless it is an explicitly gated live test? [S:fowler-pyramid]
8. Does each trace entry name only requirements the test proves, and does any requirement lose its only runtime proof? [S:reqview-29148] [S:owner]
9. Does a guard accept several outcomes, or check a condition that is always true? [S:test-smells]
10. Does each new or changed entry of `docs/test_spec.md` say what the test really does: its premise, exercise, outcome and evidence? [S:google-looking-for]
11. Does the change loosen, skip or quarantine an existing guard or test (an `alternate` marker, a removed negative case, an `accepted_gaps` row), and does each say why and until when? [S:fowler-nondeterminism]

## Blocks at this stage

Besides the blocking criteria of every stage (`AGENTS.md`, Review findings), a finding blocks here when:

- a test that can pass while the behaviour it claims to prove is broken;
- a requirement loses its only proof;
- a secret, token value or key in evidence.
