# Independent review — Increment 1A

Implementation-PR review under D17/D20 and the [AGENTS.md PoC rules](../../../AGENTS.md#poc-scope-and-proportion):
the reviewer answers the two questions (tests: which wrong failure still passes; keys: does the
change expose a key, socket or secret) and only in-model blockers block. Reviewer: Codex CLI
0.142.5, `codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral`, run by hand; it saw the
repository and its own earlier reports, never the author's reasoning.

| Round | Reviewed | Verdict | Findings |
| --- | --- | --- | --- |
| 1 | `main..f9c6741` | not approvable | B1–B4 (blockers); 2 advisories |
| 2 | fixes in `539472e` | not approvable | B1–B4 closed; new B5 |
| 3 | fix in `6979abc` | not approvable | B5 closed; new B6 |
| — | fix in `2c22623` | not re-reviewed (round limit reached) | B6 fixed and checked offline |

## Resolutions
| Finding | Fix | Commit |
| --- | --- | --- |
| B1 M2-T7 ignored the workload-key read error | the key read's stderr is captured (never its content) and must say `No such file or directory` | `539472e` |
| B2 M3.S2-T3/T5 accepted any exit 28, including a stalled response after connecting | the by-IP outcome also requires `Connection timed out` (connect phase) | `539472e` |
| B3 M5-T26 accepted an MCP error result (`isError`, for example gateway down) | new `assert_mcp_ok`: JSON-RPC 2.0, not `isError`, decoded `ok` true | `539472e` |
| B4 `test-lint` missed an unparenthesised alternation (`'error\|fail'`) | the pattern match accepts both forms; negative control added | `539472e` |
| B5 an empty or whitespace MCP capture passed (`jq -e` can exit 0 on empty input) | the envelope must be exactly one JSON document | `6979abc` |
| B6 the same for empty decoded text | the decoded text must be exactly one document with `ok` true | `2c22623` |
| Advisory: M5-T21 twin "named in 1A" | named: M5-T3, the allowed mint and call on the M5 route | this PR |
| Advisory: M2-T7 inspects a temporary container | accepted until OPL-006 (plan review note 3) | — |

B6 was checked offline against the helper with jq 1.6 (the reviewer's version; the test container
has jq 1.7.1): empty, whitespace, `isError`, two-document, empty-text, whitespace-text and
`ok: false` captures fail; the recorded successful response passes.

## Round 1 report (verbatim)

### Independent review — Increment 1A

#### 1. Tests

Reviewed commit `f9c6741` in `main..HEAD`. “Matches” compares the assertion with the recorded outcome; matching a row does not exclude a false green.

| Test | Wrong failure that still passes (or “none found”) | Matches the test-plan row (yes/no) |
| --- | --- | --- |
| M1-T1 | none found | yes |
| M1-T2 | none found | yes |
| M1-T3 | none found | yes |
| M2-T3 | none found | yes |
| M2-T5 | none found | yes |
| M2-T6 | none found | yes |
| M2-T7 | Any nonzero workload-key read failure, including permission denied; its error evidence is never checked (B1) | no |
| M2.5-T1 | none found | yes |
| M3.S2-T3 | TCP connection succeeds but the HTTP response times out (B2) | yes |
| M3.S2-T4 | none found | yes |
| M3.S2-T5 | TCP connection succeeds but the HTTP response times out (B2) | yes |
| M3.S4-T1 | none found | yes |
| M3.S4-T2 | none found | yes |
| M3.S4-T3 | none found | yes |
| M3.S4-T4 | none found | yes |
| M3.S4-T5 | none found | yes |
| M4-T5 | none found | yes |
| M4-T6 | none found | yes |
| M5-T4 | none found | yes |
| M5-T21 | none found | yes |
| M5-T24 | none found | yes |
| M5-T26 | Gateway unavailable, represented as an MCP error result with text (B3) | yes |
| M5-T28 | none found | yes |
| M5-T46 | none found | yes |

The three isolation controls reject a service already down when the premise runs. M2.5-T1 also checks the same pinned IP and requires a connection-timeout message. The two M3 controls require HTTP 200 by name, but their IP outcomes check only exit 28; that also represents a response timeout after connection.

`test_lint.py`: 18 tests passed with temporary-file tests excluded; the current harness passes lint. The fixtures cover the declared rules, but miss an ordinary spelling of the prohibited broad regex (B4).

`mutation_gate.py`: no scoring finding. It divides killed mutants by total mutants, retaining `no_tests` and `skipped`, and rejects empty runs. Read-only, in-memory checks confirmed the six scenarios in `test_mutation_gate.py`, including 70.00% passing and 69.99% failing.

#### 2. Keys

No. The change adds no mounts, secret environment assignments, image copies, or key-copy paths; new evidence contains timestamps, IPs and diagnostics, with no newly introduced recording of credential values.

#### Blocking findings

- **B1 — Incomplete exact outcome for the workload key.** Where: [scripts/rogue_node_tests.sh:2307](../../../scripts/rogue_node_tests.sh). The exercise reads four paths, but captures and checks error evidence for only three. If `svid.key` exists but returns permission denied, while the other paths are absent, the test passes despite the approved “No such file or directory for each path” outcome. **Smallest fix:** capture the workload-key diagnostic and assert the expected message alongside the other three.

- **B2 — Response timeout passes as network isolation.** Where: [scripts/rogue_node_tests.sh:2465](../../../scripts/rogue_node_tests.sh) and [scripts/rogue_node_tests.sh:2512](../../../scripts/rogue_node_tests.sh). With edge DNS still isolated but direct IP connectivity accidentally enabled, a TCP connection followed by a stalled response returns 28 and passes. OPA’s `/health` control can succeed while its policy endpoint stalls. The outcome also ignores empty or missing IP-error evidence. **Smallest fix:** require the connection-timeout diagnostic as M2.5-T1 already does, distinguishing it from a timeout after connection.

- **B3 — MCP error results satisfy the new control.** Where: [scripts/rogue_node_tests.sh:3827](../../../scripts/rogue_node_tests.sh). The adapter represents gateway unavailability as JSON-RPC `result.content` text with `isError=true`. Both responses can therefore satisfy the shape checks and token grep without exercising successful responses. This was reproduced offline. **Smallest fix:** require successful results and decoded `.ok == true` for both calls before checking for leaked material; record that stronger outcome in the row.

- **B4 — Broad-regex lint misses ordinary syntax.** Where: [scripts/test_lint.py:25](../../../scripts/test_lint.py). `grep -Eq 'error|fail' "$f"` produces no lint finding, whereas `grep -Eq '(error|fail)' "$f"` does. An honest reintroduction of the prohibited loose assertion therefore passes the gate. Existing fixtures exercise only parenthesized patterns. **Smallest fix:** recognize unparenthesized alternatives and add that negative control.

#### Advisory (at most five)

- M5-T21’s twin remains “named in 1A” instead of naming an existing positive test.
- M2-T7’s temporary-container limitation remains explicitly accepted until OPL-006; it is not an additional blocker here.

#### Verdict

Approvable within the threat model: no — B1, B2, B3, B4.

#### Not checked

- No Docker, services or network used; no full E2E run, runtime evidence validation, mutation generation or current mutation scores verified.
- Temporary-file/CLI pytest cases were inspected, not executed. Mutation scenarios were exercised with in-memory file reads.
- Uncommitted documentation changes that appeared during review were excluded from `main..HEAD`.
## Round 2 report (verbatim)

### Independent review — Increment 1A, round 2

#### Round-1 findings

| Finding | closed/open | reason (file:line) |
| --- | --- | --- |
| B1 | closed | Captures workload-key stderr and requires `No such file or directory` for all four paths ([scripts/rogue_node_tests.sh:2316](../../../scripts/rogue_node_tests.sh)). |
| B2 | closed | Both IP outcomes now require exit 28 and `Connection timed out`, rejecting stalled-response timeouts and empty diagnostics ([scripts/rogue_node_tests.sh:2476](../../../scripts/rogue_node_tests.sh), [2523](../../../scripts/rogue_node_tests.sh)). |
| B3 | closed | Gateway-error results are rejected through `isError` and decoded `ok` checks; confirmed offline ([scripts/rogue_node_tests.sh:709](../../../scripts/rogue_node_tests.sh)). Separate empty-response blocker below. |
| B4 | closed | Recognizes unparenthesized alternatives and adds the reported negative control. Nineteen file-free lint tests passed ([scripts/test_lint.py:26](../../../scripts/test_lint.py), [tests/tools/test_test_lint.py:53](../../../tests/tools/test_test_lint.py)). |

#### New blocking findings

**B5 — Empty MCP responses pass the success guard.**

- **Where:** [scripts/rogue_node_tests.sh:709](../../../scripts/rogue_node_tests.sh), used at [3838](../../../scripts/rogue_node_tests.sh).
- **Failure scenario:** An adapter regression silently drops tool-call messages and exits successfully on stdin EOF, leaving empty captures. With local jq 1.6, both `jq -e` checks return zero on empty input. Offline reproduction confirmed that two empty captures pass both the success guard and token grep without successful MCP responses. Whitespace-only captures also pass.
- **Smallest fix:** Slurp the response and require exactly one JSON object before checking JSON-RPC fields and decoded `ok == true`. Add empty and whitespace-only negative controls.

#### Verdict

Approvable within the threat model: no — B5.
## Round 3 report (verbatim)

### Independent review — Increment 1A, round 3

#### B5

**Closed.** The document-count check rejects empty and whitespace-only captures ([scripts/rogue_node_tests.sh:710](../../../scripts/rogue_node_tests.sh)). Offline checks confirmed both rejection cases and acceptance of a valid success response.

#### New blocking findings

**B6 — Empty decoded MCP text still passes the success guard.**

- **Where:** [scripts/rogue_node_tests.sh:712](../../../scripts/rogue_node_tests.sh).
- **Failure scenario:** An adapter regression returns a JSON-RPC envelope with `isError:false` and `content[0].text:""` for both calls. Offline reproduction confirms `assert_mcp_ok` accepts this: the final `jq -e` receives empty input and exits zero. M5-T26 consequently passes its success and token-absence guards without successful application results ([scripts/rogue_node_tests.sh:3840](../../../scripts/rogue_node_tests.sh)).
- **Smallest fix:** Replace the final filter with `jq -se 'length == 1 and (.[0].ok == true)'`; check empty and whitespace-only decoded text as negative controls.

#### Verdict

Approvable within the threat model: no — B6.

## Reviewer prompts (verbatim)
Recorded so a review can be rerun the same way. Command, from the repository root:
`codex exec -m gpt-6.1-sol --sandbox read-only --ephemeral -C . [--add-dir <dir with earlier reports>] -o round.md - < PROMPT.md`.

### Round 1

````markdown
You are the independent reviewer of an implementation change in the repository at the current
working directory. You did not write it. Review it read-only: do not modify files, run docker,
start services or use the network. Never print key material, tokens or env var values.

## What to review
The commit range `main..HEAD` (run `git diff main..HEAD` and `git log main..HEAD`). It is
Increment 1A of slice `agentic-delivery-process`: exact outcomes for loose E2E checks in
`scripts/rogue_node_tests.sh`, a new lint `scripts/test_lint.py` (`make test-lint`), and mutation
scoring in `scripts/mutation_gate.py`. The approved contract is
`docs/slices/agentic-delivery-process/plan.md` and `test_plan.md` (the expected-outcome table,
the probe record and the deviations listed there).

## Rules for findings
Read `AGENTS.md`, section "PoC scope and proportion", first. This is a proof of concept. The threat
model is honest mistakes by an agent, not deliberate attacks on CI or the gates. Only these block:
a concrete false green (a test that can pass while what it protects is broken), a contradiction
with the approved test plan, or an approved decision without a test. Everything else is advisory:
list it once, briefly. Production-hardening ideas are advisory at most. Do not invent work.

## Answer exactly these two questions
1. **Tests.** For each E2E test changed in the diff, which wrong failure would still pass its new
   outcome check: the service down, another status, the right status with another reason, another
   component answering, a missing value or an empty or missing evidence file read as success?
   Does the assertion match its row in the test plan's expected-outcome table? Also check the new
   in-test controls (premise guards) for the network isolation tests, `scripts/test_lint.py` against
   its tests in `tests/tools/test_test_lint.py`, and `scripts/mutation_gate.py` against
   `tests/tools/test_mutation_gate.py`.
2. **Keys.** Does the change make a key, socket or secret reachable by a service that should not
   hold it, through a compose mount, an env var, a Dockerfile `COPY`, an entrypoint or script that
   copies or writes it, or a shared volume? Does any new evidence file or log record a token, key or
   credential value?

## Output
Markdown only, in this structure:

# Independent review — Increment 1A

## 1. Tests
A table: Test | Wrong failure that still passes (or "none found") | Matches the test-plan row (yes/no).
Then any finding about the lint or the mutation gate.

## 2. Keys
"No" with one line of reasoning, or each finding.

## Blocking findings
Each with: where (file:line), the failure scenario, and the smallest fix. "None" if none.

## Advisory (at most five)

## Verdict
"Approvable within the threat model: yes" or "no — <finding ids>".

## Not checked
````

### Round 2

````markdown
You are the independent reviewer of Increment 1A in the repository at the current working
directory (read-only: no file changes, no docker, no network; never print key material or tokens).
In round 1 you reported four blocking findings on commit f9c6741 (your report is in the extra
directory as round1.md). The author's fixes are in commit HEAD (`git show HEAD`).

Rules: AGENTS.md "PoC scope and proportion". Re-check only B1, B2, B3 and B4. In this round a new
finding is allowed only if it is a blocker (a concrete false green inside the honest-mistake threat
model, with a failure scenario). Do not repeat advisories.

Output, markdown only:
# Independent review — Increment 1A, round 2
## Round-1 findings
Table: Finding | closed/open | reason (file:line)
## New blocking findings
"None", or each with where, failure scenario and smallest fix.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
````

### Round 3

````markdown
You are the independent reviewer of Increment 1A in the repository at the current working
directory (read-only: no file changes, no docker, no network; never print key material or tokens).
Your round-2 report (round2.md in the extra directory) found B5. The fix is commit HEAD
(`git show HEAD`). Rules: AGENTS.md "PoC scope and proportion". Re-check only B5. This is the last
round: a new finding is allowed only if it is a blocker with a concrete failure scenario.

Output, markdown only:
# Independent review — Increment 1A, round 3
## B5
closed/open, with reason (file:line)
## New blocking findings
"None", or each with where, failure scenario and smallest fix.
## Verdict
"Approvable within the threat model: yes" or "no — <ids>".
````

