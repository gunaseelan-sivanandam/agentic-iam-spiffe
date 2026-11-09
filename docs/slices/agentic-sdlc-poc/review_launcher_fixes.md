# Review — the launcher and secret-check fixes

Record of the review of the launcher and secret-check fixes found by slice 4's plan reviews in the agentic-SDLC PoC: every task prompt and every released report verbatim, and the author's answers to each finding.

- Reviewer: a fresh headless Claude session, `claude-opus-5-5`, started by `scripts/run_independent_review.py` on a frozen copy of the reviewed commit without this record and the attempt log; the effort of each attempt is given with it.
- Attempt log: [`review_attempts.jsonl`](review_attempts.jsonl). A start entry holds the commit and the SHA-256 of the files reviewed and of the task prompt; an end entry holds the status and the report's SHA-256.
- Every prompt and report block below was checked against the log before the push. A report lost to the report-path collision (DPL-011) or withheld by the publication check has no block.
- Until slice 4.1 adds the `accounted` field, a recheck lists the answers it accepted, and the files it opened, in a finding with ID `ACCOUNTED`.

## Round 1

### Attempt launcher_fixes/c1/r1/fixes/1

Commit `f070669`, effort high. Files reviewed (SHA-256): `scripts/evidence_secrets.py` `3a7d87106c46`, `scripts/run_independent_review.py` `1be9212e65a3`, `tests/tools/fakes/fake_claude.py` `95ab66b1af60`, `tests/tools/test_evidence_secrets.py` `e3673bd1e162`, `tests/tools/test_run_independent_review.py` `44ad947b9e3e`.

Status: interrupted (no end entry: the launcher stopped, or the publication check withheld the report).

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, untested, stale, overclaimed or unsafe, inside or outside the files under review. The questions below are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow.

## The change

Commit f070669 on the branch of slice 4's plans fixes three problems in code merged with slices 2 and 3. They were found when slice 4's six plan reviews ran in parallel through the review launcher (`scripts/run_independent_review.py`):
1. **Lost reports.** Every plan review used the unit name "plan", and the launcher named report files after the unit and attempt only, so the six reviews wrote one file (`artifacts/reviews/plan/plan_c1_r1_plan_1.json`) and five reports were lost. Fix: the report path includes the slice directory's name.
2. **A tool call that could not run failed a review.** One reviewer called `Bash`, which the CLI does not offer (it lists only Read, Grep and Glob; a probe on 2026-11-08 confirmed this), so the call returned an error and ran nothing. The rule from slice 2's review round 5 (R5-A4) failed every call to another tool. Fix: such a call fails the review only if it ran; a refused one is logged as `other_tools_failed`.
3. **The secret check withheld a correct report.** A review quoted `AGENTS.md`'s description of the evidence check ("`Authorization:` line with a value"), and the check read the backtick as a credential value. Fix: a value starting with a backtick (a Markdown code span) is not a credential. A test now asserts that `AGENTS.md` passes the check.

_review_inputs/change.diff is the change against the base (it also holds slice 4's six plans, which other review units cover; review the code change).

## Minimum questions

1. Can any of the three fixes let something through that should fail: an escaped or blind review passing, a real credential passing the secret check, a report still lost or overwritten, a recovery after a kill finding the wrong file?
2. Which wrong behaviour would still pass the new tests?
3. Did the same cause leave other places broken? For example, other paths built from the unit name, other code-span or Markdown forms the secret check misreads, other tools whose refusal looks like success.
4. Is the change to the evidence secret check (a shared gate, used by `make qa-evidence`) acceptable under the honest-mistake threat model?

Use kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low] (the owner's severity order, which slice 4 builds in).
```

#### Report

None: the publication check withheld it, so it was never written (DPL-011).

### Attempt launcher_fixes/c1/r1/fixes/2

Commit `d56c69a`, effort high. Files reviewed (SHA-256): `AGENTS.md` `6110bef757ea`, `docs/test_spec.md` `67117a2172c0`, `scripts/evidence_secrets.py` `27445de35f61`, `scripts/run_independent_review.py` `1be9212e65a3`, `tests/tools/fakes/fake_claude.py` `95ab66b1af60`, `tests/tools/test_evidence_secrets.py` `cf782270259a`, `tests/tools/test_run_independent_review.py` `44ad947b9e3e`, `trace/tests.yaml` `9ee7b5f94e5f`.

Status: interrupted (no end entry: the launcher stopped, or the publication check withheld the report).

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, untested, stale, overclaimed or unsafe, inside or outside the files under review. The questions below are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow.

## The change

Commits f070669 and d56c69a on the branch of slice 4's plans fix four problems in code merged with slices 2 and 3. They were found when slice 4's six plan reviews ran in parallel through the review launcher (`scripts/run_independent_review.py`):
1. **Lost reports.** Every plan review used the unit name "plan", and the launcher named report files after the unit and attempt only, so the six reviews wrote one file (`artifacts/reviews/plan/plan_c1_r1_plan_1.json`) and five reports were lost. Fix: the report path includes the slice directory's name.
2. **A tool call that could not run failed a review.** One reviewer called `Bash`, which the CLI does not offer (it lists only Read, Grep and Glob; a probe on 2026-11-08 confirmed this), so the call returned an error and ran nothing. The rule from slice 2's review round 5 (R5-A4) failed every call to another tool. Fix: such a call fails the review only if it ran; a refused one is logged as `other_tools_failed`.
3. **The secret check withheld a correct report.** A review quoted `AGENTS.md`'s description of the evidence check ("`Authorization:` line with a value"), and the check read the backtick as a credential value. Fix: a value starting with a backtick (a Markdown code span) is not a credential. A test now asserts that `AGENTS.md` passes the check.
4. **The secret check withheld two more correct reports** (commit d56c69a). The withheld text is never written, so the cause is inferred: the repository's own text naming the header matched the rule, for example "`Authorization: Bearer`" in `docs/test_spec.md` (value "Bearer`"), `printf 'Authorization: Bearer %s\r\n'` in the harness, `JIRA_API_TOKEN=\n` in a test, and JSON escaping (`\"`) made more values. Fix: a credential value counts only when it is 20 characters or longer or has a digit; the rulebook's E2E evidence row and `docs/test_spec.md` state the narrower rule, and `trace/tests.yaml` names the new boundary test as a negative control of EVID-T1.

_review_inputs/change.diff is the change against the base (it also holds slice 4's six plans, which other review units cover; review the code change).

## Minimum questions

1. Can any of the four fixes let something through that should fail: an escaped or blind review passing, a real credential passing the secret check, a report still lost or overwritten, a recovery after a kill finding the wrong file?
2. Which wrong behaviour would still pass the new tests?
3. Did the same cause leave other places broken? For example, other paths built from the unit name, other code-span or Markdown forms the secret check misreads, other tools whose refusal looks like success.
4. Is the change to the evidence secret check (a shared gate, used by `make qa-evidence`) acceptable under the honest-mistake threat model?

Use kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low] (the owner's severity order, which slice 4 builds in).
```

#### Report

None: the publication check withheld it, so it was never written (DPL-011).

### Attempt launcher_fixes/c1/r1/fixes/3

Commit `f8b6200`, effort high. Files reviewed (SHA-256): `AGENTS.md` `6110bef757ea`, `docs/test_spec.md` `67117a2172c0`, `scripts/evidence_secrets.py` `c53dbb2aac0a`, `scripts/run_independent_review.py` `1be9212e65a3`, `tests/tools/fakes/fake_claude.py` `95ab66b1af60`, `tests/tools/test_evidence_secrets.py` `32bd4712fb4f`, `tests/tools/test_run_independent_review.py` `44ad947b9e3e`, `trace/tests.yaml` `9ee7b5f94e5f`.

Status: completed; approvable within the threat model: yes.

#### Prompt

```markdown
## Your mandate

Find anything a working delivery process must catch in this change and has not caught yet: anything missing, wrong, untested, stale, overclaimed or unsafe, inside or outside the files under review. The questions below are a minimum, not the limit. Think for yourself; the author's framing, including this prompt, can be wrong or narrow.

## The change

Commits f070669, d56c69a and the commit under review on the branch of slice 4's plans fix five problems in code merged with slices 2 and 3. They were found when slice 4's six plan reviews ran in parallel through the review launcher (`scripts/run_independent_review.py`):
1. **Lost reports.** Every plan review used the unit name "plan", and the launcher named report files after the unit and attempt only, so the six reviews wrote one file (`artifacts/reviews/plan/plan_c1_r1_plan_1.json`) and five reports were lost. Fix: the report path includes the slice directory's name.
2. **A tool call that could not run failed a review.** One reviewer called `Bash`, which the CLI does not offer (it lists only Read, Grep and Glob; a probe on 2026-11-08 confirmed this), so the call returned an error and ran nothing. The rule from slice 2's review round 5 (R5-A4) failed every call to another tool. Fix: such a call fails the review only if it ran; a refused one is logged as `other_tools_failed`.
3. **The secret check withheld a correct report.** A review quoted `AGENTS.md`'s description of the evidence check ("`Authorization:` line with a value"), and the check read the backtick as a credential value. Fix: a value starting with a backtick (a Markdown code span) is not a credential. A test now asserts that `AGENTS.md` passes the check.
4. **The secret check withheld two more correct reports** (commit d56c69a). The withheld text is never written, so the cause is inferred: the repository's own text naming the header matched the rule, for example "`Authorization: Bearer`" in `docs/test_spec.md` (value "Bearer`"), `printf 'Authorization: Bearer %s\r\n'` in the harness, `JIRA_API_TOKEN=\n` in a test, and JSON escaping (`\"`) made more values. Fix: a credential value counts only when it is 20 characters or longer or has a digit; the rulebook's E2E evidence row and `docs/test_spec.md` state the narrower rule, and `trace/tests.yaml` names the new boundary test as a negative control of EVID-T1.
5. **The secret check missed a value in a code span or quotes** (found by plan review 4.4, A9): in "Authorization: `Bearer <token>`" the value read as "`Bearer", a placeholder. Fix: the rule skips an opening backtick or quote, also JSON-escaped, before or after the scheme; the code-span placeholder is removed.

_review_inputs/change.diff is the change against the base (it also holds slice 4's six plans, which other review units cover; review the code change).

## Minimum questions

1. Can any of the five fixes let something through that should fail: an escaped or blind review passing, a real credential passing the secret check, a report still lost or overwritten, a recovery after a kill finding the wrong file?
2. Which wrong behaviour would still pass the new tests?
3. Did the same cause leave other places broken? For example, other paths built from the unit name, other code-span or Markdown forms the secret check misreads, other tools whose refusal looks like success.
4. Is the change to the evidence secret check (a shared gate, used by `make qa-evidence`) acceptable under the honest-mistake threat model?

Use kind "blocking" for findings that meet AGENTS.md's blocking criteria. For advisory findings, start the problem text with [high], [medium] or [low] (the owner's severity order, which slice 4 builds in).

Write `<token>` for any credential value in your report, even a made-up example: the publication check withholds a report that holds a credential-shaped value, and two earlier attempts of this review were withheld that way.
```

#### Report

````json
{
  "findings": [
    {
      "evidence": "_other_tools splits calls only on `call_id in summary.failed_ids`. failed_ids is every tool_result with is_error (_failed_results, line 397). Nothing looks at the result text (for example the CLI's 'no such tool' message) or at permission_denials. Bash has no `path` argument, so tool_paths returns '.', and the call never counts in outside_calls. The new test test_call_to_a_tool_the_cli_does_not_offer_does_not_fail_the_review uses a fake error result, so it would also pass for a Bash call that ran and exited non-zero.",
      "failure_scenario": "A CLI update stops honouring `--tools Read,Grep,Glob`, or someone widens the invocation by mistake. That is the honest mistake R5-A4's backstop exists for. A reviewer then runs Bash with `cat ../../somefile; grep -r x ~ ; false`. The command runs and reads outside the copy, the result is is_error, the end entry shows other_tools=[] and other_tools_failed=['Bash'], and the escaped review counts as completed. Narrow the 'refused' case to a result whose text is the CLI's unavailable-tool error, or to a permission denial. Add a fake scenario where Bash ran, returned an error and still fails the review. This needs the CLI misconfiguration first, so it is advisory.",
      "file": "scripts/run_independent_review.py",
      "id": "A1",
      "kind": "advisory",
      "line": 453,
      "problem": "[medium] Fix 2 treats any tool call whose result has is_error as a call that did not run. is_error does not mean 'the tool was refused'. A call that ran and then returned an error, such as a Bash command with a non-zero exit, is also is_error. A call that ran and failed is now only logged as other_tools_failed, and the review completes."
    },
    {
      "evidence": "The value class now leaves out the backtick (`[^\\s'\"`]+`), and QUOTE skips only one opening backtick. On `Authorization: Bearer ``<token>``` the branch with the scheme cannot start a value at the second backtick. The regex backtracks, skips the optional scheme group and takes value='Bearer', which PLACEHOLDER accepts. A 32-character hex token is also under the 40-character BASE64_RUN floor, so no other rule finds it. Before this change the value was '``<token>``', which is not a placeholder, so it was flagged. No fixture covers double backticks or double escaping.",
      "failure_scenario": "A review report or a quality artifact quotes a captured header in Markdown as Authorization: Bearer ``<token>`` with a real 32-hex capiss or test token. check_publishable and qa-evidence both pass it, and it is published. Fix: let QUOTE skip a run of backticks (`` `+ ``) or several escape levels, and add both forms to SECRET_FIXTURES.",
      "file": "scripts/evidence_secrets.py",
      "id": "A2",
      "kind": "advisory",
      "line": 37,
      "problem": "[medium] Fixes 3\u20135 bring a new miss in the credential-line rule: a token inside a double-backtick Markdown code span is now read as the placeholder 'Bearer'. The old rule flagged it. Doubly JSON-escaped quotes (\\\\\\\") also shorten the value to a few backslashes, which are then judged by the length/digit rule."
    },
    {
      "evidence": "rogue_node_tests.sh:4252 builds a hostile rollout with `authorization:\\\"Bearer sk-leaked-secret\\\"`. Under the new regex the value is `sk-leaked-secret\\` (17 characters, no digit), so _is_credential_value returns False. Under the old rule this line was a finding.",
      "failure_scenario": "If the varambu redaction test's input or output is ever copied into evidence, the backstop no longer reports the fake secret that the test is about. Under the honest-mistake model this is acceptable: the real tokens (capiss, Jira, SVIDs) are long, and the publisher fingerprints token-shaped values first. Record it as an accepted limit of EVID-T1 rather than leave it implicit.",
      "file": "scripts/evidence_secrets.py",
      "id": "A3",
      "kind": "advisory",
      "line": 171,
      "problem": "[low] The new length-or-digit rule also lets through short credential-shaped values that the repository itself treats as leaked secrets. The harness's own fake leaked secret 'sk-leaked-secret' (16 characters, no digit) no longer counts. Neither does a short Basic credential such as base64 of a short user:pass, which can have no digit."
    },
    {
      "evidence": "run_independent_review.py:742 builds `REPORT_DIR / Path(spec.record).parent.name / spec.unit / ...`. plan.md:89 and :96 (the hidden-state row) give the old layout.",
      "failure_scenario": "An implementer of 4.1 follows the approved plan and looks for the earlier report at the old path. The recheck then finds no file, or a leftover file from a different slice, at the shared old path (the pre-fix collision). It should check against the start entry's report_path. This is a contradiction under the blocking criteria, but it belongs to the 4.1 plan's review unit: fix it there (one line) or point the plan at the start entry's report_path.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A4",
      "kind": "advisory",
      "line": 89,
      "problem": "[medium] Contradiction in the same branch: slice 4.1's plan still says released reports live at `artifacts/reviews/<unit>/<attempt>.json`. Fix 1 now writes them to `artifacts/reviews/<slice-dir>/<unit>/<attempt>.json`. The plan's recheck design reads this path."
    },
    {
      "evidence": "The implementation log's latest entries are slice 3 and slice 2 on 2026-11-08. A search of docs/ finds no other_tools_failed, MIN_CREDENTIAL_LENGTH or lost-report entry. The delivery problem log stops at DPL-010. AGENTS.md step 4 requires both in the same change.",
      "failure_scenario": "The branch merges with only the plans recorded. The reason EVID-T1 was narrowed, and why R5-A4 changed, is then held only in a review record withheld from this copy. Later reviewers then judge the gate without that context.",
      "file": "docs/history/implementation_log.md",
      "id": "A5",
      "kind": "advisory",
      "line": 8,
      "problem": "[medium] Close-out is missing for these five code fixes. There is no dated implementation-log entry, and no delivery-problem-log entry for the misses found: reports overwritten across slices, R5-A4 failing calls that never ran, and the secret check withholding correct reports. Slice 2's and 3's reviews let all of these through."
    },
    {
      "evidence": "The diff edits the rulebook's quality-gate row and the EVID-T1 description in docs/test_spec.md. _other_tools reverses R5-A4's 'a call to any tool other than Read, Grep or Glob fails the review' (review_slice_2.md:1703). The copy holds no record of the user's approval; review_launcher_fixes.md is withheld.",
      "failure_scenario": "If the user did not approve them, a shared gate and an agreed review rule were loosened without the owner's decision. Confirm the user approved both, and record their words in the PR.",
      "file": "AGENTS.md",
      "id": "D1",
      "kind": "decision_concern",
      "line": 262,
      "problem": "Two agreed decisions were changed as bug fixes. Fix 4 narrows the approved E2E-evidence gate row (the shared EVID-T1 rule) from 'a line with a value' to 'a token-like value'. Fix 2 relaxes R5-A4, a fix agreed in slice 2's review round 5. AGENTS.md says a fix that would change an agreed decision goes to the user as a question before it is applied."
    },
    {
      "evidence": "`Path(spec.record).parent.name` drops the rest of the path. The new test covers only two distinct leaf names, demo and other.",
      "failure_scenario": "This is rare in practice. Using the record's path relative to the repo, or the log path's parent, would remove it.",
      "file": "scripts/run_independent_review.py",
      "id": "A6",
      "kind": "advisory",
      "line": 742,
      "problem": "[low] The report path keeps only the record's parent directory name. Two records with the same unit name whose parent directories share a leaf name still collide: for example docs/slices/X and docs/slices/archive/X. So does any record not under a slice directory, where the leaf name is ''."
    }
  ],
  "verdict": "yes"
}
````

#### Answers to launcher_fixes/c1/r1/fixes/3

| ID | Severity | Answer |
| --- | --- | --- |
| A1 | medium | fixed: `8d80ce8` (only a call to a tool the session's init event did not offer, answered with an error, is logged as `other_tools_not_offered`; an offered tool, or a stream without a tool list, fails); tests `test_offered_tool_that_ran_with_an_error_still_fails` and `test_without_an_offered_tool_list_an_erroring_call_still_fails` |
| A2 | medium | fixed: `8d80ce8` (code spans of any fence length; quotes escaped any number of times); fixtures "double-backtick code span" and "twice JSON-escaped header", both missed by `f8b6200` |
| A3 | low | fixed: `AGENTS.md`'s E2E evidence row and the plan's F3 state the limit (20 characters or more, or a digit) |
| A4 | medium | fixed: 4.1 S41-D5(a) reads the earlier report at the start entry's `report_path`; 4.1's environment fact names the slice-directory layout |
| A5 | medium | fixed: `docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md`, an implementation-log entry, and DPL-011 |
| A6 | low | rejected: reviewed records sit directly in `docs/slices/<id>/`, and archived bundles are frozen and not reviewed again, so the leaf name is unique among the bundles that run reviews |
| D1 | decision_concern | owner: asked in the plan PR (the plan's section "For the owner"); F2 now keeps R5-A4 for every call that can have run |

## Round 2

### Attempt launcher_fixes/c1/r2/fixes/1

Commit `ebb1029`, effort medium. Files reviewed (SHA-256): `docs/delivery_problem_log.md` `ba2309bda54a`, `docs/history/implementation_log.md` `faff648055bd`, `docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md` `a98620ff6c71`, `scripts/evidence_secrets.py` `29e6ce6159d8`, `scripts/run_independent_review.py` `dcc2089aea98`, `tests/tools/fakes/fake_claude.py` `a6af0b224404`, `tests/tools/test_evidence_secrets.py` `160df3aaaac6`, `tests/tools/test_run_independent_review.py` `a5c0ba190337`.

Status: completed; approvable within the threat model: yes.

#### Prompt

````markdown
## Your mandate (recheck)

This is round 2 of the review of the fixes to the review launcher and the secret check (unit `launcher_fixes`), a recheck of your earlier report (round 1, attempt 3). The commit under review adds `8d80ce8` (the fixes to your A1 and A2), `ebb1029` (a credential value now ends at a backslash, because the widened rule read a JSON-escaped ellipsis after the header name as a value) and `ced9658` (the plan of these fixes, `docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md`, an implementation-log entry, DPL-011 and the revised slice-4 plans). For every answer of the author below, open the files the answer names and the tests that cover them, and accept it or re-raise the finding. Report anything wrong or missing in what the fixes touch. From round 2 a new finding counts only if it is blocking, except simpler alternatives and decision concerns; report new high findings as well, marked `[high]`.

## How to report

- A re-raised finding keeps its earlier ID, with the reason the fix does not hold.
- Add one advisory finding with ID `ACCOUNTED`, problem text "[low] accounted answers", and in its evidence one line per answer: `<ID>: accepted` or `<ID>: re-raised`, followed by the files you opened for it.
- For advisory findings, start the problem text with [high], [medium] or [low].
- Write `<token>` for any credential value, even a made-up example: the publication check withholds a report that holds one.

## Your earlier report (round 1, attempt 3)

```json
{
  "findings": [
    {
      "evidence": "_other_tools splits calls only on `call_id in summary.failed_ids`. failed_ids is every tool_result with is_error (_failed_results, line 397). Nothing looks at the result text (for example the CLI's 'no such tool' message) or at permission_denials. Bash has no `path` argument, so tool_paths returns '.', and the call never counts in outside_calls. The new test test_call_to_a_tool_the_cli_does_not_offer_does_not_fail_the_review uses a fake error result, so it would also pass for a Bash call that ran and exited non-zero.",
      "failure_scenario": "A CLI update stops honouring `--tools Read,Grep,Glob`, or someone widens the invocation by mistake. That is the honest mistake R5-A4's backstop exists for. A reviewer then runs Bash with `cat ../../somefile; grep -r x ~ ; false`. The command runs and reads outside the copy, the result is is_error, the end entry shows other_tools=[] and other_tools_failed=['Bash'], and the escaped review counts as completed. Narrow the 'refused' case to a result whose text is the CLI's unavailable-tool error, or to a permission denial. Add a fake scenario where Bash ran, returned an error and still fails the review. This needs the CLI misconfiguration first, so it is advisory.",
      "file": "scripts/run_independent_review.py",
      "id": "A1",
      "kind": "advisory",
      "line": 453,
      "problem": "[medium] Fix 2 treats any tool call whose result has is_error as a call that did not run. is_error does not mean 'the tool was refused'. A call that ran and then returned an error, such as a Bash command with a non-zero exit, is also is_error. A call that ran and failed is now only logged as other_tools_failed, and the review completes."
    },
    {
      "evidence": "The value class now leaves out the backtick (`[^\\s'\"`]+`), and QUOTE skips only one opening backtick. On `Authorization: Bearer ``<token>``` the branch with the scheme cannot start a value at the second backtick. The regex backtracks, skips the optional scheme group and takes value='Bearer', which PLACEHOLDER accepts. A 32-character hex token is also under the 40-character BASE64_RUN floor, so no other rule finds it. Before this change the value was '``<token>``', which is not a placeholder, so it was flagged. No fixture covers double backticks or double escaping.",
      "failure_scenario": "A review report or a quality artifact quotes a captured header in Markdown as Authorization: Bearer ``<token>`` with a real 32-hex capiss or test token. check_publishable and qa-evidence both pass it, and it is published. Fix: let QUOTE skip a run of backticks (`` `+ ``) or several escape levels, and add both forms to SECRET_FIXTURES.",
      "file": "scripts/evidence_secrets.py",
      "id": "A2",
      "kind": "advisory",
      "line": 37,
      "problem": "[medium] Fixes 3\u20135 bring a new miss in the credential-line rule: a token inside a double-backtick Markdown code span is now read as the placeholder 'Bearer'. The old rule flagged it. Doubly JSON-escaped quotes (\\\\\\\") also shorten the value to a few backslashes, which are then judged by the length/digit rule."
    },
    {
      "evidence": "rogue_node_tests.sh:4252 builds a hostile rollout with `authorization:\\\"Bearer sk-leaked-secret\\\"`. Under the new regex the value is `sk-leaked-secret\\` (17 characters, no digit), so _is_credential_value returns False. Under the old rule this line was a finding.",
      "failure_scenario": "If the varambu redaction test's input or output is ever copied into evidence, the backstop no longer reports the fake secret that the test is about. Under the honest-mistake model this is acceptable: the real tokens (capiss, Jira, SVIDs) are long, and the publisher fingerprints token-shaped values first. Record it as an accepted limit of EVID-T1 rather than leave it implicit.",
      "file": "scripts/evidence_secrets.py",
      "id": "A3",
      "kind": "advisory",
      "line": 171,
      "problem": "[low] The new length-or-digit rule also lets through short credential-shaped values that the repository itself treats as leaked secrets. The harness's own fake leaked secret 'sk-leaked-secret' (16 characters, no digit) no longer counts. Neither does a short Basic credential such as base64 of a short user:pass, which can have no digit."
    },
    {
      "evidence": "run_independent_review.py:742 builds `REPORT_DIR / Path(spec.record).parent.name / spec.unit / ...`. plan.md:89 and :96 (the hidden-state row) give the old layout.",
      "failure_scenario": "An implementer of 4.1 follows the approved plan and looks for the earlier report at the old path. The recheck then finds no file, or a leftover file from a different slice, at the shared old path (the pre-fix collision). It should check against the start entry's report_path. This is a contradiction under the blocking criteria, but it belongs to the 4.1 plan's review unit: fix it there (one line) or point the plan at the start entry's report_path.",
      "file": "docs/slices/poc-4-1-review-prompts/plan.md",
      "id": "A4",
      "kind": "advisory",
      "line": 89,
      "problem": "[medium] Contradiction in the same branch: slice 4.1's plan still says released reports live at `artifacts/reviews/<unit>/<attempt>.json`. Fix 1 now writes them to `artifacts/reviews/<slice-dir>/<unit>/<attempt>.json`. The plan's recheck design reads this path."
    },
    {
      "evidence": "The implementation log's latest entries are slice 3 and slice 2 on 2026-11-08. A search of docs/ finds no other_tools_failed, MIN_CREDENTIAL_LENGTH or lost-report entry. The delivery problem log stops at DPL-010. AGENTS.md step 4 requires both in the same change.",
      "failure_scenario": "The branch merges with only the plans recorded. The reason EVID-T1 was narrowed, and why R5-A4 changed, is then held only in a review record withheld from this copy. Later reviewers then judge the gate without that context.",
      "file": "docs/history/implementation_log.md",
      "id": "A5",
      "kind": "advisory",
      "line": 8,
      "problem": "[medium] Close-out is missing for these five code fixes. There is no dated implementation-log entry, and no delivery-problem-log entry for the misses found: reports overwritten across slices, R5-A4 failing calls that never ran, and the secret check withholding correct reports. Slice 2's and 3's reviews let all of these through."
    },
    {
      "evidence": "The diff edits the rulebook's quality-gate row and the EVID-T1 description in docs/test_spec.md. _other_tools reverses R5-A4's 'a call to any tool other than Read, Grep or Glob fails the review' (review_slice_2.md:1703). The copy holds no record of the user's approval; review_launcher_fixes.md is withheld.",
      "failure_scenario": "If the user did not approve them, a shared gate and an agreed review rule were loosened without the owner's decision. Confirm the user approved both, and record their words in the PR.",
      "file": "AGENTS.md",
      "id": "D1",
      "kind": "decision_concern",
      "line": 262,
      "problem": "Two agreed decisions were changed as bug fixes. Fix 4 narrows the approved E2E-evidence gate row (the shared EVID-T1 rule) from 'a line with a value' to 'a token-like value'. Fix 2 relaxes R5-A4, a fix agreed in slice 2's review round 5. AGENTS.md says a fix that would change an agreed decision goes to the user as a question before it is applied."
    },
    {
      "evidence": "`Path(spec.record).parent.name` drops the rest of the path. The new test covers only two distinct leaf names, demo and other.",
      "failure_scenario": "This is rare in practice. Using the record's path relative to the repo, or the log path's parent, would remove it.",
      "file": "scripts/run_independent_review.py",
      "id": "A6",
      "kind": "advisory",
      "line": 742,
      "problem": "[low] The report path keeps only the record's parent directory name. Two records with the same unit name whose parent directories share a leaf name still collide: for example docs/slices/X and docs/slices/archive/X. So does any record not under a slice directory, where the leaf name is ''."
    }
  ],
  "verdict": "yes"
}
```

## The author's answers

| ID | Severity | Answer |
| --- | --- | --- |
| A1 | medium | fixed: `8d80ce8` (only a call to a tool the session's init event did not offer, answered with an error, is logged as `other_tools_not_offered`; an offered tool, or a stream without a tool list, fails); tests `test_offered_tool_that_ran_with_an_error_still_fails` and `test_without_an_offered_tool_list_an_erroring_call_still_fails` |
| A2 | medium | fixed: `8d80ce8` (code spans of any fence length; quotes escaped any number of times); fixtures "double-backtick code span" and "twice JSON-escaped header", both missed by `f8b6200` |
| A3 | low | fixed: `AGENTS.md`'s E2E evidence row and the plan's F3 state the limit (20 characters or more, or a digit) |
| A4 | medium | fixed: 4.1 S41-D5(a) reads the earlier report at the start entry's `report_path`; 4.1's environment fact names the slice-directory layout |
| A5 | medium | fixed: `docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md`, an implementation-log entry, and DPL-011 |
| A6 | low | rejected: reviewed records sit directly in `docs/slices/<id>/`, and archived bundles are frozen and not reviewed again, so the leaf name is unique among the bundles that run reviews |
| D1 | decision_concern | owner: asked in the plan PR (the plan's section "For the owner"); F2 now keeps R5-A4 for every call that can have run |
````

#### Report

```json
{
  "findings": [
    {
      "evidence": "A1: accepted \u2014 scripts/run_independent_review.py:372-376 (init tools parsed), :457-464 (_other_tools keeps a call in other_tools unless the tool was not offered AND its result was an error), :544 (non-empty other_tools fails); tests/tools/test_run_independent_review.py:571-594 (offered Bash erroring still fails; no tool list still fails); tests/tools/fakes/fake_claude.py:61-62. If the CLI stops honouring --tools, init lists Bash, so the escaped call fails the review.\nA2: accepted \u2014 scripts/evidence_secrets.py:34-43 (QUOTE `(?:`+|\\\\*['\"])?`, value stops at a backslash); tests/tools/test_evidence_secrets.py:91-92 (double-backtick code span; twice JSON-escaped header with a 32-hex value, which has digits). Traced by hand: for Authorization: Bearer ``<token>`` the scheme branch now matches and the value is the token, not 'Bearer'.\nA3: accepted \u2014 AGENTS.md:263 (E2E evidence row states the limit), scripts/evidence_secrets.py:46-49,173-176, tests/tools/test_evidence_secrets.py:155.\nA4: accepted \u2014 docs/slices/poc-4-1-review-prompts/plan.md:47 (S41-D5 reads the start entry's report_path) and :99 (environment fact).\nA5: accepted \u2014 docs/history/implementation_log.md:8-26, docs/delivery_problem_log.md:368-409 (DPL-011), docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md.\nA6: accepted (rejection) \u2014 reviewed records live directly under docs/slices/<id>/, and archived bundles are frozen and not reviewed again; low severity, not blocking.\nD1: accepted as routed to the owner \u2014 the plan's 'For the owner' section asks it; F2 now keeps R5-A4 for every call that can have run, so most of the R5-A4 concern is gone. The EVID-T1 narrowing still needs the owner's recorded approval in the PR.",
      "failure_scenario": "None; this entry only accounts for the answers.",
      "file": "docs/slices/agentic-sdlc-poc/plan_launcher_fixes.md",
      "id": "ACCOUNTED",
      "kind": "advisory",
      "line": 0,
      "problem": "[low] accounted answers"
    }
  ],
  "verdict": "yes"
}
```

#### Answers to launcher_fixes/c1/r2/fixes/1

| ID | Severity | Answer |
| --- | --- | --- |
| ACCOUNTED | low | rejected: the stand-in that carries the accounted answers until S41-D8's field exists, not a finding |
