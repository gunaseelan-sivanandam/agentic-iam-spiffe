# Implementation Log

Historical per-slice implementation and verification record. Until 2026-10-27 this lived in the
gitignored `docs/local_status_capture/implementation_status.md`; older entries still cite that path.
Current state is summarized in `docs/STATUS.md`. Entries are not in strict date order (the newest
is first); every heading carries its date.

## 2026-10-30 Slice 1 standing rules moved into the rulebook

- Docs-only change on `docs/durable-slice1-rules`, before slice 2 starts. A sweep of slice 1's
  `plan.md` and `test_plan.md` found twelve rules or decisions that lived only in frozen slice
  records (or in an agent's private notes), where future agents do not read them.
- `AGENTS.md`: grill-me asks the key, socket and secret question (D16); plan approval by merging the
  plan PR (D8); expected-outcome sources and the stop when a probe contradicts the plan (D4, plan
  review note 4); positive twins (D5); static proofs (1B user decision); a new "Independent review"
  section (D11, D17: reviewer, inputs, plan-review record, implementation questions); only the user
  merges (D15), with the note that the `main` ruleset requires no approving review, so GitHub does
  not enforce it.
- Templates: an "Assets and holders" section and a "Rulebook" line in `plan.md`; the twin and probe
  rules next to the expected-outcome table in `test_plan.md`.
- `docs/STATUS.md`: slice 1 complete, slice 2 next; the open mutation decision
  (`mutate_only_covered_lines`) recorded.
- Validation: `make docs-check` and `make qa-trace`. No code or test changed, so no E2E run.

## 2026-10-29 Increment 1B: deployment register and qa-deploy

- Slice `agentic-delivery-process` 1B on branch `slice/agentic-delivery-process-1b`, after 1A merged
  as PR #5.
- New `REQ-SEC-K1` to `-K8`, `-D1`, `-D2` in `docs/requirements.md`; `security/invariants.yaml`
  (asset locations and holders, the per-service allowlist over every profile, three known-violation
  rows for OPL-005, OPL-006 and OPL-008 expiring 2026-12-31); `scripts/qa_deploy.py` and
  `make qa-deploy` (in `qa-quality`; in CI without image inspection); ARCH-034; tooling tests T-8 to
  T-13 in `tests/tools/test_qa_deploy.py`, including the `07520d7` replay (reports the capiss key in
  `tool-b`).
- User decisions: `rogue-tests` is a declared test-only holder (whole-repo mount plus the Docker
  socket), extended to K7 for the SVIDs it exports into `tmp_svid/`; Python instead of the planned
  Rego.
- Baseline look at Dockerfiles, entrypoints and scripts: no key copies other than the compose
  mounts and the harness exports above (which the first pass missed; review finding C3).
- `AGENTS.md`: quality-gate rows for `make test-lint` (missed in 1A) and `make qa-deploy`, the new
  mutation rule, and the register in "Start here".
- Independent review (Codex, two rounds, `review_1b.md`): C1–C4 fixed; round 2 "approvable". The
  eight generic review questions were tried as part B.
- Validation: full E2E on a clean stack at `ce465a8` 120/120 (1 warning, M5-T55 env-gated skip),
  `make qa-evidence` PASSED; after the review fixes (no runtime or harness change) `make qa-quality`
  PASSED (`qa-deploy`: 18 known violations, 22 root warnings), `make tooling-test` PASSED,
  `ruff check services scripts` clean. Not rerun: the full E2E suite after the review fixes, since
  they change only `qa-deploy`, the register and docs.

## 2026-10-29 Increment 1A: exact E2E outcomes, test-lint, mutation scoring

- Slice `agentic-delivery-process` 1A on branch `slice/agentic-delivery-process-1a`, from the plan
  merged as PR #4 (`f6a9524`).
- Probed the unchanged harness on a clean stack at `f6a9524` (all rows passed) and pinned the
  observed outcomes; the probe record is in the slice `test_plan.md`.
- Tightened 24 E2E outcome checks to exact statuses, reasons, exit codes and messages: the 15
  planned rows plus 9 that the new lint found (M2-T3, M2-T5, M2-T6, M2-T7, M5-T4, M5-T24, M5-T26,
  M5-T28, M5-T46). `assert_file_any` and the "no network error" greps are gone; the M3.S2-T3/T5
  warning alternates became "does not resolve" plus "pinned IP times out in the connect phase".
  The network isolation tests got in-test positive controls (the app answers 200 from inside its
  network). M1-T2/T3 read the server log from the attempt's start time.
- Found and corrected: M2-T3 never tested expiry (its certificate is from an untrusted CA, so Envoy
  answers `unknown ca`); renamed to what it tests, expiry stays with M2-T9. M5-T4, M5-T26 and M5-T28
  could pass on a missing or empty evidence file; each now checks a positive anchor first.
- New `scripts/test_lint.py` and `make test-lint` (in `qa-quality` and the CI docs-check job, which
  now fetches full history for the baseline test); tooling tests T-7, T-22, T-41 in `tests/tools/`.
- `scripts/mutation_gate.py` counts `no_tests` and `skipped` as not killed and fails an empty run.
  Score under the new rule: 85.58% (1240 of 1449; 0 untested, 0 skipped), unchanged, because
  `mutate_only_covered_lines = true` never creates mutants for uncovered lines.
- Independent review (Codex, three rounds, `review_1a.md`): B1–B6 fixed; B6 after the round limit,
  checked offline, not re-reviewed. Key question answered "no" in round 1.
- Validation: full E2E on a clean stack 120/120 (1 warning, the M5-T55 env-gated skip; the two
  M3.S2 warnings are gone), `make qa-evidence` PASSED, `make qa-quality` PASSED, `make tooling-test`
  PASSED, `make unit-mutation` PASSED, `ruff check services scripts` clean.

## 2026-10-29 Delivery-process plan reviewed, escalated and split into three slices

- Plan PR #4 review comments addressed (terms, D16 security coverage of grill-me, lane home, CI
  trust), then D17 (test adequacy, independent plan review before the user's review).
- Independent review by Codex CLI (`gpt-6.1-sol`; the configured `gpt-5.5` is refused for a ChatGPT
  login, and an expired login first failed every request with HTTP 401). Round 1: 20 findings, all
  resolved. Round 2: 9 partial and 13 new; the repeated findings triggered the D10 stop and an
  escalation.
- User decisions: D18 threat model (fallible agent, not an attacker of the CI infrastructure;
  residual accepted as OPL-009), D19 split into three slices, and an acceptance bar for reviews
  (only in-model blockers and majors in scope are fixed; at most three rounds).
- `plan.md` and `test_plan.md` now cover slice 1 only; slice 2 and 3 drafts and carried findings
  are in `later_slices.md`. Real errors fixed: M5-T21's expected outcome, the mutation-gate
  denominator, the Redis writer model and an unenforceable ACL rule, matrix detectors per asset
  class. New OPL-008 (`spire-token-init` mounts the SPIRE server data directory); OPL-007's fix
  option corrected.
- PoC rules added to `AGENTS.md` ("PoC scope and proportion"): honest-mistake threat model,
  accepted simplifications, ask before growing, few exceptions, which review findings block.
- D20 lean cut of slice 1 (user decision): kept exact outcomes, twins, `test-lint`, the holder list
  with `qa-deploy`, mutation scoring and the independent review. The runtime asset scan became a
  one-time baseline look plus a review question; the replay tool became a test review question;
  kinds, tiers, fault injection, provenance enforcement and the derivation checklist were deferred
  to `later_slices.md`; REQ-SEC-S1 moved to the pilot.
- Not run: documentation only; `make docs-check` and `make qa-trace` were run.

## 2026-10-28 CI mutation gate broken by pytest 9.2.0; pytest pinned

- PR #3 (`docs/consolidation`) failed `unit-trust / mutation-trust` with
  `AttributeError: 'Function' object has no attribute '_nodeid'` before any mutant ran.
- Cause: `requirements-dev.txt` left `pytest` unpinned. pytest 9.2.0 (published 2026-10-27 21:30 UTC,
  after `main`'s last green run at 20:09 UTC) removed the private `Node._nodeid`, which mutmut 3.5.0
  reads directly. `main` is affected the same way.
- Fix: `pytest==9.1.1`. Upgrading to mutmut 3.8.1 (2026-10-28, uses the public `item.nodeid`) is left
  for a separate dependency change.
- Validation in a fresh Python 3.11 virtualenv built from `requirements-dev.txt` (pytest 9.1.1, mutmut
  3.5.0): `qa-trace`, `docs-check`, `tooling-test`, `unit-guard-check`, `unit-trust` and
  `unit-mutation` (score 85.58%) all PASSED.

## 2026-10-28 OPL-005 verified by forgery; OPL-006, OPL-007 found; delivery-process slice planned

- OPL-005 re-checked on the running stack at the user's request. The private key was read (hashes
  only) in `capability-issuer`, `tool-b`, `jira-tool`, `jira-mcp-gateway` and a one-off `rogue`;
  all match. A token forged inside `tool-b` with that key passed tool-b's own `verify_biscuit` once a
  Redis budget existed for its root id. History traced to `07520d7` (2026-01-05) and the copied
  volume blocks.
- New: OPL-006 (SPIRE agent `data/keys.json` readable by every workload that mounts the agent
  directory; `M2-T7` checks a container without that mount) and OPL-007 (Redis without
  authentication, writable from every verifier network).
- Root-cause review of why six layers missed OPL-005, followed by a grill-me that produced the
  [agentic-delivery-process](../slices/agentic-delivery-process/plan.md) plan (D1–D15) and test plan.
  The plan includes an audit of about 20 loose E2E assertions.
- Not run: no code, harness or compose change was made, so no E2E or unit run was needed;
  `make docs-check` and `make qa-trace` were run on the documentation changes.

## 2026-10-27 Docs consolidation, Increments 2 and 3; harness PR merged

- `fix/m5-evidence-harness-hardening` merged to `main` as PR #2 (`fe86c35`). Full E2E on `main`, clean
  stack: 120/120, 3 warnings (M3.S2-T3, M3.S2-T5 accepted isolation; M5-T55 env-gated skip).
  `make qa-evidence` PASSED (validated 119, skipped 1).
- Increment 2: `docs/test_spec.md` now describes all 120 E2E tests. All 58 M5 tests were written by
  hand from the guard code; five entries note where a title claims more than the guards check. All
  headings use full harness IDs.
- Increment 3:
  - `scripts/check_docs.py` (`make docs-check`): spec covers every harness test and vice versa;
    links and anchors in live docs resolve; tracked images are referenced and `.puml` sources have
    their `.svg`; every slice bundle is indexed; `TEST_ONLY=` examples name real tests.
  - `make docs-check` is in `make qa-quality` and a new CI job, with `make tooling-test`
    (`tests/tools/`, 16 negative controls; `tests/shell/test_varambu_output.sh`, previously unwired).
  - `SECURITY_MODEL.md` folded into a "Security model summary" in `docs/architecture.md` and archived.
- Security finding while verifying the old security model: the capiss root signing key is readable as
  root inside `tool-b`, `jira-tool`, `jira-mcp-gateway`, and the `rogue` test container. Recorded as
  OPL-005 with evidence; not fixed (runtime change, needs its own slice).
- Validation: `make qa-quality` PASSED (qa-trace unchanged at requirements=159, architecture=33,
  design=131, tests=371; 348 unit tests; docs-check); `make tooling-test` PASSED; ruff clean;
  no new function above complexity 10.

## 2026-10-27 Docs consolidation, Increment 1

Slice bundle: `docs/slices/docs-consolidation/`.
- `AGENTS.md` rewritten as the single rulebook, checked against `Makefile` and CI; repo `CLAUDE.md` imports it.
- Status log tracked as this file (secret-scanned); new `docs/STATUS.md`.
- One hand-written E2E spec: `docs/test_spec.md` (was `test_spec_detailed.md`); guard listing and readable
  table archived. Phase 4 now requires updating it.
- Legacy slice bundles, `REDTEAM_M3.md`, and the unreferenced `container_architecture` diagram archived
  with `git mv`; slice index rebuilt.
- README corrected: invalid `TEST_ONLY` example, wrong `qa-quality`/unit target descriptions, stale
  Varambu "not implemented" note, doc map.
- Checks C1–C9 in the slice `test_plan.md`: all passed. No runtime, requirement, or test changes.

## 2026-10-27 Full-suite re-baseline and evidence-harness hardening

- First full E2E run since 2026-05-16 (clean stack): `119/120`, `M5-T49` FAIL, `make qa-evidence` FAILED.
  - `M5-T49`: intent assertion used `first(.[])`; the preceding `M5-T48` request landed in the same
    `since` second, so T49's session held a second chain. Product output was correct for T49's cid.
  - `M5-T43..T48`: never printed `EVIDENCE_DIR=`, so `qa-evidence` could not bind their PASS lines.
  - `M5-T55`: mock-mode skip left no premise/exercise/outcome evidence.
- Fix on branch `fix/m5-evidence-harness-hardening` (PR pending at time of writing; slice bundle `m5-full-chain-audit-trace/test_plan.md`, Increment 3, H1-H3):
  - chain-specific outcomes in `M5-T49/T50/T51/T54/T58` select by the test's own cid; human renders use `--cid`;
  - `M5-T43..T48` emit `EVIDENCE_DIR=`;
  - `M5-T55` records the gateway upstream mode as premise evidence and writes `skip_reason.txt`;
    `qa-evidence` accepts a skip only for a prefix declared in the suite's `env_gates` map, with gate
    premise evidence and no exercise/outcome artifacts; skipped prefixes are reported separately.
- Negative controls (scratch, not committed): 31/31 against the failing-run evidence plus mutations, and
  12/12 validator skip-rule cases including undeclared, other-prefix, malformed, wrong-gate, and silent skips.
- Validation after fix (clean stack):
  - full E2E: `120/120` passed, warnings `3` (`M3.S2-T3`, `M3.S2-T5` accepted isolation; `M5-T55` env-gated skip).
  - `make qa-evidence`: PASSED, `validated=119/120, skipped=1, warnings=3`.
  - `make qa-trace`: PASSED. `make qa-quality`: PASSED (`348` unit tests). `ruff` clean on the validator.
- Open: `M5-T55` still prints `PASS` in `test_report.log` when skipped (harness has no SKIP status);
  `validate_e2e_evidence.py:main` cyclomatic complexity 32 (pre-existing, unchanged).

## 2026-06-21 Increment 3: relay scrubbed upstream (Jira) error detail

Motivation: a failed upstream call showed only the bare HTTP status, and worse, Jira Cloud returns an
**ambiguous** status (e.g. an expired API token → **404**, because Jira returns 404 for unauthorized
resource access to avoid enumeration). So the status-only render said "project missing / verify it
exists" when the real cause was an expired credential — not actionable. Root limitation: the gateway
discarded the upstream response body, keeping only the status.

Re-entered the V-model (changes gateway behavior + the `jiramcp_gateway_decision` schema):
- **REQ-M5-FT7** extended: on upstream failure the gateway SHALL relay the upstream error as
  faithfully as possible (redacting only credential-bearing material, bounded), the trace SHALL
  surface it on the upstream leg and re-screen for secrets at read time, and the presentation SHALL
  NOT assert a single cause from an ambiguous status code (e.g. 404).
- **ARCH-033** updated (gateway `summarize_upstream_error` → `upstream_error_detail`; trace `Jira`
  row + read-time re-screen; ambiguous-status messaging).
- **DD-517** (`summarize_upstream_error`, gateway): extracts the message from common Jira shapes
  (`errorMessages`/`errors`/`message`/`error`/non-dict/fallback JSON), redacts `Basic `/`Bearer `
  credential blobs → `[redacted-credential]`, bounds to 512 B (limit exclusive, `…[truncated]`).
  Wired into both upstream-failure `_deny` sites via `_event_fields`/`_deny` new
  `upstream_error_detail` param. CC: all new gateway fns A/B (`_extract_upstream_message` refactored
  to B(9) via `_first_str_field`).
- Trace side (`scripts/varambu_audit.py`): `upstream_error_detail` added to `GATEWAY_FIELD_ORDER`
  (allowlisted + read-time scrubbed by the existing `Bearer `/`Basic `/`biscuit` screen),
  `derive_gateway_upstream` copies it onto the upstream leg, and `_detail_upstream` **passes the
  relayed Jira message through verbatim** as a single `Jira` row. Human-view only; `--json` keeps the
  raw field. Decision (2026-06-21, per operator): **dropped the constructed status interpretation** —
  no `_UPSTREAM_STATUS_HELP` table, no `Error`/`Action` rows. Rationale: relaying Jira's own words is
  simpler and avoids asserting a single cause from an ambiguous status code (Jira's message itself
  resolves e.g. a 404 that is really an expired/unauthorized credential). On a failure with no relayed
  detail the leg is just the `Call` row (status still shown in the row + STATUS column).
- Tests: gateway **UT-343** (shapes + Basic/Bearer redaction + BVA on the 512 B limit); trace
  **UT-344** (normalizer keeps the field, upstream leg renders `Jira`, a `Bearer `-bearing detail is
  dropped at read time); **UT-342** rewritten to pin the verbatim pass-through (Call→Jira only, no
  Error/Action; detail-less failure and success are Call-only). **346 unit tests pass**, guard
  offenders=0; radon all A/B; ruff clean; `make qa-trace` PASSED (design 131, DD-517).
- E2E: **M5-T59** fixture carries `upstream_error_detail`; outcome asserts the human view relays the
  Jira detail verbatim, that no constructed `Action` row is present, and that `--json` carries the
  field on the upstream leg. Full trace suite **M5-T49..T59 = 10/10 PASS**.
- Deployment note: the deterministic suite proves the relay via UT + the synthetic T59 fixture (mock
  mode never triggers a real upstream failure — NAS is denied at the gateway before upstream). The
  **live** gateway emission of `upstream_error_detail` runs only under `M5-T55` (real Jira, env-gated)
  and requires rebuilding the gateway image (`docker compose ... up --build jira-mcp-gateway`); the
  running stack still has the pre-change gateway until then.

## 2026-06-20 Increment 2: M5 trace display redesign (7-leg table)

Re-entered the V-model for a presentation + leg-model change (no enforcement/capiss/gateway/adapter
authorization change). Locked design after live testing.

Phase 1 — docs:
- `plan.md`/`test_plan.md` "Increment 2"; `REQ-M5-FT7` (upstream is a leg distinct from gateway
  enforcement), `REQ-M5-FT9` (single aligned detailed table; mint = same fields, not byte-identical;
  full untruncated identifiers); `ARCH-033` (7 legs, gateway/upstream derivation, renderer).

Phase 2/3 — code + tests (green):
- `scripts/varambu_audit.py`: `derive_gateway_upstream` (DD-924) splits one
  `jiramcp_gateway_decision` into a gateway-enforcement leg and an upstream-call leg
  (gateway ALLOW iff it reached the upstream call or recorded allow; a deny-with-upstream_called is an
  **upstream** failure, not a gateway denial); 7-leg `CHAIN_LEG_ORDER`
  (`…, gateway, upstream, adapter_decision`); a new aligned table `render_chain` (fixed
  `# · LEG · TIME · STATUS` spine + grouped detail, colour TTY-only, full ids wrap-not-truncate,
  local-zone times, `FROM CODEX`/`GATEWAY`/`UPSTREAM`/`RETURN TO CODEX` labels); `render_chain_json`
  with the upstream leg + per-leg advisory offset; `capiss_reason` added to the adapter allowlist.
- UTs: `tests/unit/test_varambu_trace.py` updated to the 7-leg contract; mint "byte-identical" UT →
  "fields present"; **exhaustive-condition + BVA UTs for `derive_gateway_upstream`** (UT-335..340);
  layout/label/full-id UTs. **342 unit tests pass**, guard offenders=0.
- Static gates: `radon` CC ≤ 10 (no grade C), `ruff` clean, `make qa-trace` PASSED (design 130).

Phase 4 — E2E:
- E2E updated to the 7-leg model (T49/T50/T55/T57/T58) + **new M5-T59** (the motivating case:
  gateway ALLOW + upstream 401 FAIL rendered as upstream failure, not gateway denial), mapped in
  `trace/tests.yaml` to REQ-M5-FT7.
- **M5-T56 and M5-T59 PASS** end-to-end through the real `varambu trace` CLI (synthetic fixtures, no
  mock/MCP network dependency) — these directly prove the redesign incl. the gateway/upstream split.
- **E2E now run green (2026-06-21).** With a healthy Docker network the full trace suite passes:
  `TEST_ONLY=M5-T49,M5-T50,M5-T51,M5-T52,M5-T53,M5-T54,M5-T56,M5-T57,M5-T58,M5-T59` → **10/10 PASS**
  (T55 live-Jira-gated, auto-skips in mock). Existing audit E2E `M5-T42..T48` re-run **7/7 PASS**
  (no regression). The prior WSL2 Docker multi-network attach flake did not recur.
- One harness fix surfaced on the first real run of `M5-T49`: its human-render outcome grepped the
  verbatim prompt as a single line, but the redesigned renderer **wraps** the intent detail cell
  (Increment 2 locked decision #5, wrap-not-truncate), so the prompt spans two lines. The exact
  verbatim intent is already proven byte-for-byte by the JSON outcome (`intent leg equals the
  verbatim prompt`); the human-render check now collapses whitespace (`tr '\n' ' ' | tr -s ' '`)
  before grepping, so it is wrap-robust. Implementation unchanged (renderer is correct by design).
- Re-run command (rebuild the rogue-tests image first; T55 is live-Jira-gated):
  `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M5-T49,M5-T50,M5-T51,M5-T52,M5-T53,M5-T54,M5-T56,M5-T57,M5-T58,M5-T59 rogue-tests`
- Mint-leg fidelity fix (REQ-M5-FT9 "same fields as `varambu audit`"): the trace MINT block was
  missing the subject identity (`varambu audit` shows it as `Subject:`, its first field). Added a
  leading `From  <subject_spiffe_id>` row to `_detail_mint` so the mint leg no longer reads as
  incomplete; subject was already carried in the normalized mint leg + `--json`, only the human view
  dropped it. UT-311 updated to assert the subject identity; CC/ruff/qa-trace green, E2E re-run green.
- Gateway-leg fidelity fix (render-what's-there): the gateway ALLOW leg printed a hardcoded literal
  `Checks  token · aud · act · project · budget ok` that asserted a per-check breakdown the
  `jiramcp_gateway_decision` event never contains (it only attests the aggregate `decision=allow,
  reason_code=ok`) and silently omitted `subject` (which the gateway does enforce). Replaced with
  event-grounded rows: `Verified aud … · act …`, `Project request <project_key> = token
  <token_project>` (the actual project check — `project_mismatch` is enforced at
  `services/jira-mcp-gateway/server.py` by comparing the token's resource project to the request),
  and `Budget remaining …`. New UT-341 pins the grounded render and forbids the old literal; the
  `_full_chain` gateway fixture now carries the real `aud/project_key/token_project/budget_remaining`.
  343 unit tests pass; CC/ruff/qa-trace green; E2E re-run green.
- Remaining-leg scrutiny (render-what's-attested audit of every leg): `intent` (verbatim
  agent-attested prompt), `action` (rollout `tool_name`/`arguments`), `adapter_request`
  (`tool_name → res`, both in the adapter event), `upstream` (`upstream_operation`/`upstream_status`
  from the gateway event; `gateway-attested` label is accurate, run-mode is CLI context by REQ-M5-FT7
  design), and `adapter_decision` (`ok`/`reason`/`capiss_reason`/`key`, all conditional on the
  adapter event) were each verified to derive only from their source event — no further manufactured
  literals beyond the mint/gateway ones already fixed.
- Label change (demo clarity): leg 3 `adapter_request` display label reverted `FROM CODEX` → `ADAPTER`
  (JSON leg/event_type keys unchanged — still `adapter_request`, schema stable). `RETURN TO CODEX`
  (leg 7) kept. Updated `LEG_LABELS`, UT-312 assertion + docstring, the M5-T49 E2E grep (now matches
  the `N  ADAPTER ` leg row, not the lowercase spiffe-id substring), `ARCH-033`/architecture.md, and
  the slice plan/test_plan label references. `_full_chain` gateway fixture and `mod_request` adapter
  fixture were made realistic (carry `aud/project_key/token_project/budget_remaining` and `act/res/
  project_key`) so UTs render the same fields the live events carry. 343 UTs + 10/10 trace E2E green.
- Upstream-failure actionability: a failed `upstream` leg now self-explains. `_detail_upstream` adds
  an `Error  HTTP <status> <meaning>` row and an `Action  <remediation>` row, derived from the
  gateway-attested `upstream_status` via `_upstream_status_help` (401 → credential invalid/expired →
  refresh the Jira auth token; 403 → permission; 404 → missing project/issue; 409 → conflict;
  429 → rate limited; 5xx → Jira server error → retry; generic 4xx/unknown fallbacks). The status is
  attested; the meaning/action are standard-HTTP advisory help (same role as `_humanize_reason`),
  human-view only — `--json` keeps the raw `upstream_status`. Successful (2xx) legs stay the single
  `Call` row. New UT-342 (401/5xx/unmapped/2xx) + an M5-T59 outcome asserting the human view explains
  the 401 and names the credential-refresh action. 344 UTs + 10/10 trace E2E green; CC/ruff/qa-trace
  green. Limitation: the gateway's `call_upstream` discards the upstream response body (returns only
  the HTTP status), so Jira's own error text is not available to surface — capturing a bounded,
  scrubbed upstream error body at the gateway would be a separate gateway-schema slice (REQ/ARCH/DD
  + secret hygiene), out of scope for this renderer-only change.

## 2026-06-19 Slice: M5 Full-Chain Audit Trace (`varambu trace`)

Slice bundle: `docs/slices/m5-full-chain-audit-trace/` (plan.md + test_plan.md, grill-me approved).
Authoritative docs already authored before this work: `REQ-M5-FT1..FT9`, `ARCH-033`, `ARCH-032`
state extension.

Phase 2 — tests-first (complete, green):
- New `tests/unit/test_varambu_trace.py`: 77 UTs (`UT-248..UT-324`) covering DD-910..917, DD-922,
  DD-923. Rigor: exhaustive 2^4 condition coverage for `find_intent_triple` (DD-913, UT-265..280),
  BVA (B-1/B/B+1, limits exclusive) for `scrub_and_bound_triple` (DD-914, UT-286..294), exhaustive
  missing-leg/anchor/ordering for `assemble_chains` (DD-915).
- `tests/unit/jiramcp/test_adapter.py`: 5 new UTs (`UT-325..329`) for the adapter independent voice
  (DD-919): request-before-mint / decision-after-gateway ordering, crash visibility, path wiring,
  secret discipline, correlation stamping.
- `tests/unit/test_varambu_audit.py`: `UT-330` for the gateway-source tailer branch (DD-903).
- Failing baseline recorded: before implementation, 77 trace UTs + 5 adapter UTs failed (no impl);
  the 8 prior adapter UTs passed.

Phase 3 — implementation (complete for the unit-testable + deterministic surface):
- `scripts/varambu_audit.py`: `normalize_gateway_event` (DD-910), `normalize_adapter_event`
  (DD-911), `extract_correlation_id` (DD-912), `find_intent_triple` (DD-913),
  `scrub_and_bound_triple` (DD-914), `write_trace_file` (DD-923), `assemble_chains` (DD-915),
  `render_chain` (DD-916), `render_chain_json` (DD-922), `trace` CLI (DD-917); plus a `--source`
  option on `tail` so the same tailer serves the gateway leg with no capiss-path regression.
- `services/codex-jira-mcp-adapter/server.py`: `emit_adapter_event` (DD-919) wired into
  `invoke_tool` — `adapter_request` before mint, `adapter_decision` at each terminal; existing
  stderr line retained; no-op when `VARAMBU_SESSION_REL` is unset (keeps MCP stdout clean).
- `varambu` launcher: `start_gateway_tailer` (DD-918), `provision_codex_home` (DD-920) +
  `CODEX_HOME=` launch line, `run_trace` dispatch (DD-921), per-session `mode` file; exports
  `VARAMBU_SESSION_REL` for the adapter container.
- `compose/spiffe.compose.yml`: adapter `../artifacts/varambu-demo:/var/audit` bind mount +
  `VARAMBU_AUDIT_ROOT` / `VARAMBU_SESSION_REL` env.

Phase 4 — verification completed in this environment:
- `python3 -m pytest -q tests/unit`: **332 passed**, unit guard `offenders=0`.
- `radon cc scripts/varambu_audit.py services/codex-jira-mcp-adapter/server.py -n C`: empty
  (all functions CC ≤ 10; the at-limit normalizer was refactored down to CC 7).
- `make qa-trace`: PASSED. `make unit-guard-check`: PASSED (332). `ruff`: clean on touched files.
  `bandit`: High=0 (the Low/Medium findings are pre-existing in untouched subprocess/urlopen code).
- Functional end-to-end of the read path on a synthetic session (no Docker): `varambu_audit.py
  trace` rendered the full six-leg chain in canonical order, reused the capiss `render_record`
  verbatim for the mint leg, showed local time + advisory deltas, and persisted a minimal scrubbed
  `trace.jsonl`.

E2E layer — authored, mapped, and run green against the live stack (2026-06-20):
- `scripts/rogue_node_tests.sh`: added `M5-T49..T58` (full chain, denied-mint partial, intent
  pending→converge, multi-tool attribution, secret hygiene+bounds, agent-tamper detection, honest
  live upstream, CLI surface + audit non-regression, canonical ordering + join integrity, anchor
  rule + mint reuse + timezone) plus helpers (`mcp_tool_call_traced` injecting
  `VARAMBU_SESSION_REL` per exec, capiss/gateway tailer starters, synthetic codex-rollout builders,
  `write_synth_trace_session`).
- `trace/tests.yaml`: added `E2E-M5-FT-TRACE-SUITE` + `E2E-M5-T49..T58` mapping to `REQ-M5-FT*`
  (all nine FT requirements now have E2E coverage; coverage_gaps 131→122).
- Run result (mock mode, real SPIRE/Envoy/capiss/gateway/adapter stack):
  `TEST_ONLY=M5-T49..T58` → **10/10 PASS** (T55 is live-gated and auto-skips in mock with a
  recorded `warning_reason`). Existing `M5-T42..T48` audit E2E re-run **7/7 PASS** (no regression
  from the `tail --source`/helper changes).
- One code fix surfaced by the E2E: the adapter mint-deny path emits a legitimate `capiss_reason`
  field; added it to `ADAPTER_FIELD_ORDER` so the trace normalizer keeps it instead of warning.
  Regression-covered by new UT-332.
- Stack lifecycle note: a stale prior-run SPIRE CA had expired (issued 2026-06-18, expired
  2026-06-19); `scripts/clean_stack.sh` wiped `/run/spire/server/data` and a fresh
  `up --build` issued SVIDs in ~5s. The `rogue-tests` image bakes the harness script, so it must be
  rebuilt (`docker compose --profile tests build rogue-tests`) after harness edits;
  `scripts/varambu_audit.py` is read live from the `/repo` mount.

Operator ergonomics (added 2026-06-20 after live Codex testing):
- `varambu codex [args...]` subcommand: launches Codex against the **current** session's
  `codex-home` (resolved via the `current` symlink), seeding the env so the operator no longer sets
  `CODEX_HOME` by hand. Flow is now `varambu start` → `varambu codex`.
- Credential seeding: `provision_codex_home` and `varambu codex` **symlink** `~/.codex/auth.json`
  into the per-session home so a freshly provisioned home does not force a Codex re-login. A symlink
  (not a copy) keeps the credential in `~/.codex` — it never enters the `artifacts/` session bundle,
  and `varambu trace` reads only `rollout-*.jsonl`, never `auth.json`. `artifacts/varambu-demo` is
  gitignored (verified). Authored in REQ-M5-FT5 + ARCH-033.
- Extractor hardening (from the same live test): `extract_correlation_id` now recovers the id from
  escaped JSON-in-JSON and structured-object tool results (real Codex MCP result shapes), not just
  the flat string my synthetic fixture used; `adapter_audit` `capiss_reason` added to the allowlist.
  Covered by UT-332/333/334. Root cause of the operator's "intent not yet available" was launching a
  plain `codex` (rollout landed in `~/.codex`, not the session tree) — addressed by `varambu codex`.

Remaining / deferred:
- `M5-T55` (live upstream) only exercises its assertions with real Jira env
  (`JIRA_MCP_UPSTREAM_MODE=live` + `.env`); in mock it auto-skips with a warning. Run with
  `make jira-live-smoke`-style live env when available.
- The launcher (`varambu start`) gateway-tailer / CODEX_HOME provisioning is `bash -n` verified and
  its building blocks (gateway `tail --source gateway`, per-session adapter audit, `trace` dispatch)
  are all exercised by the E2E, but a full interactive `varambu start` + real `codex` agent run was
  not performed here.
- `DD-918/920/921` remain reported `dd_without_ut` gaps (shell-level launcher wiring; proven via
  E2E rather than unit tests, per the black-box model in AGENTS.md).

Decisions / deviations (reviewed 2026-06-20 — resolved):
- **Anchor rule vs REQ-M5-FT8 wording — RESOLVED (REQ tightened).** REQ-M5-FT8 and ARCH-033
  Interactions and the plan.md anchor rule were edited to drop "or an M5 model tool call" as an
  anchor: only the adapter/gateway in-boundary evidence anchors a chain; the untrusted rollout
  intent is *attached* to an already-anchored chain, never used to surface one. Implementation
  already matched this (`_anchor_cids`); the docs now agree.
- **Multiple correlation-ids in one rollout output — RESOLVED (now noticeable).** Confirmed no valid
  flow produces two distinct ids in one output (the adapter/gateway result carries exactly one; user
  content is not echoed). The only causes are a future schema change or a forged/tampered rollout.
  `extract_correlation_id` keeps the deterministic first-match contract (never raises, never blocks)
  but now emits a `warn(...)` when it sees 2+ *distinct* ids, pointing at a possible forged rollout,
  so an auditor can dive to root cause. Identical repeats stay silent. New/updated UT-263, UT-331.
- **Dual Codex MCP registration — RESOLVED (global removed).** The global `configure_codex_mcp`
  function and its "Configure Codex" phase were deleted. Registration is now per-session only
  (`provision_codex_home` into the session `CODEX_HOME`), so intent capture is confined to the
  deterministic session tree (REQ-M5-FT5). `--no-codex-config` and codex-CLI-absent still degrade
  gracefully with the launcher-script pointer. Behavior change: a bare `codex` (without the printed
  `CODEX_HOME=…` launch line) no longer has the MCP registered.
- **Pinned Phase-2 contracts** (in `test_plan.md` "Pinned decisions"), unchanged: duplicate-leg =
  first-wins by sequence; multiple correlation-ids = first match (now + warning); `--strict` for
  trace = deferred; gateway already carries `act`/`res` (no gateway change).
- **Unique-DD-id rule** forced splitting two plan items into their own ids: `write_trace_file` =
  DD-923 (under DD-914's intent), `render_chain_json` = DD-922 (under DD-916's intent). Accepted.

## 2026-05-16 Slice Implemented: M5 Codex Jira MCP Slice 1

- Added a local Codex-to-container MCP launcher path with `scripts/codex_jira_mcp.sh` and `codex-jira-mcp-adapter`.
- The adapter exposes exactly `read_project_summary` and `create_story`, mints fresh `aud=jira-mcp-gateway` capiss tokens, and calls the protected gateway through `jira-mcp-envoy`.
- Added the distinct M5 authority family: `aud=jira-mcp-gateway`, `act=read_project_summary|create_story`, and `res=jira-mcp:/project:IAM`.
- Added `jira-mcp-gateway` as the request-time PEP for token, Envoy identity, action, resource, project, payload, optional epic, budget/rate, upstream, and audit enforcement.
- Added `jira-mcp-mock` as the deterministic upstream Jira Cloud substitute with broad IAM and NAS fixture data. Protected MCP behavior narrows access to IAM.
- Updated requirements, architecture, architecture diagram source, trace mappings, README, slice docs, unit tests, E2E harness, and evidence validation.
- Validation completed:
  - `make unit-guard-check`: 224 passed
  - `make unit-trust`: passed, coverage gate 85.06%
  - `make qa-trace`: passed
  - `make qa-quality`: passed
  - `TEST_MILESTONES=m5`: 40 passed, 0 failed
  - full rogue-tests suite: 102 passed, 0 failed, 2 accepted alternate isolation warnings
  - `make qa-evidence`: passed, validated 102/102 with the same two accepted warnings
- Note: `docs/architecture_diagram.puml` is the updated diagram source. No local PlantUML renderer is installed in this environment, so generated SVG/PNG regeneration was not performed in this turn.

## 2026-05-15 Slice Implemented: M4b Jira Description Write

- Added M4b as a project-scoped Jira description write slice.
- `act=write` for `jira-tool:/project:IAM` now means read plus description replacement only.
- `act=read` remains read-only.
- `jira-tool` rejects NAS writes before upstream use, rejects malformed or overbroad write bodies before upstream use, converts accepted plain text to Jira ADF, and returns `204` on successful update.
- M4b E2E evidence is authored as `M4b-T1` through `M4b-T6`.
- Optional live smoke intentionally leaves the allowed Jira issue description changed and checks demo output for credential-like material.

## 2026-04-12 Black-Box Trust Model

- Primary confidence goal:
  - a reviewer should be able to understand security-relevant behavior from authored docs and runtime evidence without discovering it accidentally from code
- Repo policy going forward:
  - requirements describe what must hold
  - architecture describes component responsibility and authoritative state
  - each slice starts with `grill-me`, then records the agreed design choices, requirements, hidden-state decisions, scope, and retirement expectations in `plan.md`
  - each slice then records the approved UT and E2E strategy in `test_plan.md`
- Internal design and unit artifacts remain useful, but they are not sufficient by themselves to explain hidden governance behavior.
- This process change is intended to prevent future surprises such as undocumented Redis-backed governance or provenance rules surfacing first from implementation details.

## 2026-03-03

### Implemented M4 Vertical Slice

- Tool-b focused vertical slice for checkpointed delegation and governance truth.
- Root and delegated token chain metadata implemented: `root_token_id`, `token_id`, `parent_token_id`, `delegator_spiffe_id`, `subject_spiffe_id`, `delegation_depth`.
- Chain integrity verification and derived depth enforcement implemented with `effective_depth = chain_length - 1` and max depth `N=3`.
- Discovery flow implemented at `tool-b:/search`, writing canonical discovered resources to Redis registry keyed by `root_token_id`.
- Registry-gated resource minting implemented at `capiss` via `POST /capabilities/resource-mint` for new resources (for example `tool-b:/read-file:fileA`).
- Per-request budget and request-rate enforcement implemented in tool-b using Redis, keyed by `root_token_id`.
- Fail-closed behavior implemented on trusted-store/policy errors in enforcement and minting paths.
- Test harness coverage implemented for this slice as M4 T1-T5 in `scripts/rogue_node_tests.sh`, with corresponding test spec entries in docs.

### M4 Review Findings (Requirements Coverage)

1. Missing "new resource mint rate" enforcement at `capiss` (High)
- Requirement explicitly calls for this: `docs/requirements.md:10`.
- `resource_mint` does registry check + policy + mint, but no mint-rate limiter/counter path exists: `services/capability-issuer/app.py:578`, `services/capability-issuer/app.py:621`, `services/capability-issuer/app.py:665`.
- No corresponding config/env in compose for capiss mint-rate control: `compose/spiffe.compose.yml:127`.

2. `capiss` does not log every mint decision path (High)
- Requirement says every mint request should be logged with provenance: `docs/requirements.md:172`.
- Several deny/error exits return without `capiss_mint_decision` logging, e.g. payload/canonical validation and early auth/chain checks:
  - `services/capability-issuer/app.py:472`
  - `services/capability-issuer/app.py:478`
  - `services/capability-issuer/app.py:588`
  - `services/capability-issuer/app.py:596`
  - `services/capability-issuer/app.py:599`
  - `services/capability-issuer/app.py:602`
  - `services/capability-issuer/app.py:616`
  - `services/capability-issuer/app.py:623`

3. Canonical resource contract is inconsistent for `/secret` (Medium)
- Requirements define canonical `res` as `tool-b:/...`: `docs/requirements.md:215`.
- Implementation keeps backward compatibility with raw `/secret`: `services/capability-issuer/app.py:182`.
- OPA root-mint policy allows `/secret` (non-canonical) but not `tool-b:/secret`: `services/opa/policy.rego:5`.
- This deviates from strict "canonical only" requirement intent (`docs/requirements.md:48`).

4. "Single enforcement contract" is not implemented as shared component (Medium)
- Requirement: shared enforcement contract/library/service across PEPs/tools: `docs/requirements.md:139`.
- Chain/depth enforcement logic is duplicated in two different services:
  - `services/capability-issuer/app.py:251`
  - `services/tool-b/server.py:197`
- Functionally similar, but not a single shared contract artifact.

5. M4 test coverage misses multiple requirement areas (Medium)
- Current M4 suite has only T1-T5: `scripts/rogue_node_tests.sh:2593`.
- Missing explicit tests for:
  - chain tamper/integrity denial (`M4-CH1`, `docs/requirements.md:68`)
  - depth limit > N denial (`M4-DL2`, `docs/requirements.md:82`)
  - fail-closed on store errors in M4 paths (`docs/requirements.md:12`)
  - audit/observability requirements (`M4-O1..O4`, `docs/requirements.md:161`)
  - capiss new-resource mint-rate requirement (`docs/requirements.md:10`)

### Areas That Look Covered

- Registry-gated resource minting and budget/rate enforcement per `root_token_id` are implemented and tested (M4 T2-T5).

## 2026-04-03

### Slice Started: Shared Enforcement Contract

- Goal: remove semantic drift between mint-time and request-time M4 chain validation by introducing one shared in-process enforcement contract.
- Scope of this slice:
  - shared chain integrity, derived depth, and attenuation semantics
  - thin caller adapters in `capiss` and `tool-b`
  - traceability updates for requirements, architecture, DD, UT, and E2E
- Explicitly out of scope for this slice:
  - mint-rate enforcement
  - full mint-decision logging closure
  - canonical resource contract cleanup
  - broader observability closure beyond this slice's new tests and trace

### Slice Implemented: Shared Enforcement Contract

- Added a shared in-process Python module for M4 chain validation semantics under `services/shared/enforcement_contract.py`.
- `capiss` and `tool-b` now call the same shared contract for:
  - required chain metadata checks
  - parent-link continuity
  - effective depth derivation
  - depth limit enforcement
  - common attenuation rules for `aud`, `act`, and `exp`
- `tool-b` keeps the resource-transition marker/store decision as a thin local hook layered on top of the shared contract.
- Added a dedicated architecture component for the shared contract in `docs/architecture.md`.
- Tightened `REQ-M4-E2` to make the shared implementation expectation explicit in `docs/requirements.md`.

### Slice Traceability Updates

- Added new source-owned DD for the shared contract:
  - `DD-220`
- Added source-owned UT coverage for the shared contract and thin adapters:
  - `UT-118` to `UT-127`
- Added new M4 E2E coverage and trace updates for:
  - tampered token denial
  - depth-limit denial on repeated delegation chain extension

### Slice Validation Notes

- Initial runtime validation exposed one issuer-side integration bug:
  - `capiss` accepted the shared contract, but its adapter did not allow previously `capiss`-minted resource transitions during later delegated mint hops.
  - Symptom: repeated delegation failed as `invalid_token` before reaching `depth_exceeded`.
- Fixed by adding the same capiss-minted marker check to the `capiss` adapter hook that `tool-b` already used for allowed resource transitions.
- Added `UT-127` to pin this behavior at the adapter level.
- Final validation after the fix:
  - `pytest tests/unit/shared/test_enforcement_contract.py tests/unit/capiss/test_chain_and_policy.py tests/unit/toolb/test_canonical_and_chain.py`
  - `make qa-trace`
  - `make qa-quality`
  - full E2E suite: `39/39` passed
  - `make qa-evidence`: passed with the expected two accepted-warning cases only

### Authoritative State Inventory Notes

- The Redis-backed `m4:capiss_minted:<token_id>` marker was not introduced by this slice. It already existed in the original M4 delegation implementation from commit `4b808cb`.
- What this slice exposed is that the rule was previously implicit and asymmetric:
  - capability-issuer wrote the marker
  - tool-b enforced it for resource-changing delegated tokens
  - the docs did not explicitly describe this as an authoritative state dependency
- The current M4 Redis-backed authoritative state now needs to be read as:
  - `m4:registry:<root_token_id>`:
    - writer: tool-b
    - reader: capability-issuer
    - purpose: discovery-backed permission to mint a new resource-scoped token
  - `m4:budget:<root_token_id>` and related request-rate keys:
    - writer/reader: tool-b, with root-budget initialization from capability-issuer
    - purpose: request-time governance truth
  - `m4:capiss_minted:<token_id>`:
    - writer: capability-issuer
    - readers: capability-issuer, tool-b
    - purpose: issuer-provenance marker for the current M4 resource-transition delegation rule

### 2026-04-03 Follow-up: Registry Seeding Cleanup

- Removed the old capability-issuer behavior that seeded `m4:registry:<root_token_id>` during root mint.
- `ensure_root_budget(...)` now initializes only `m4:budget:<root_token_id>`.
- Resulting state model is cleaner:
  - discovery registry entries come only from tool-b discovery
  - root-token starting authority remains in the token itself
  - capability-issuer still reads the registry only when a delegated mint asks for a different resource than the parent token

### 2026-04-04 Known Shortcuts and Overloads Still Present

1. Canonical resource compatibility remains inconsistent
- `capiss` still preserves raw `/secret` as a compatibility case rather than forcing canonical `tool-b:/...` resources.
- `tool-b` still accepts either raw `/secret` or canonical `tool-b:/secret` for the same protected request.
- OPA policy still reasons over the raw `/secret` form.
- This is the clearest remaining compatibility shortcut and should be removed in the canonical-resource cleanup slice.

2. Redis-backed mint provenance remains part of the M4 security model
- `m4:capiss_minted:<token_id>` is still required to prove that a resource-changing child token came from the trusted issuer path.
- This behavior is now documented, but it is still an implementation-specific governance shortcut rather than a purely token-self-contained proof model.

3. Shared enforcement still depends on service-local hooks
- The shared enforcement contract now owns the common chain/depth semantics, but legal resource transitions are still decided via service-local callbacks in `capiss` and `tool-b`.
- This is acceptable for the reduced M4 slice, but it means the shared contract is not fully self-sufficient.

4. `registry_hit` is still slightly overloaded in mint policy/logging
- When a delegated mint keeps the same resource as the parent token, `capiss` sets `registry_hit=True` without performing a registry lookup.
- Operationally this means “registry proof not needed” rather than “registry checked and hit”.
- The field name should be clarified or split later to avoid misleading logs and policy input semantics.

5. Old chain-parsing helpers remain duplicated in service files
- The active enforcement path now lives in `services/shared/enforcement_contract.py`.
- Older copies of chain/fact parsing helpers still remain in `capiss` and `tool-b`.
- They are now drift risk unless explicitly retired or justified.

6. Provenance check path still mutates TTL on read
- `tool-b` shortens the TTL of `m4:capiss_minted:<token_id>` when the stored TTL exceeds the token TTL.
- That means what looks like a read/check helper still has a state-mutating side effect.
- This should remain visible as an intentional behavior rather than hidden helper logic.

7. Governance ownership is still split across services
- `capiss` initializes root budget context.
- `tool-b` consumes and enforces the request-time spend/rate limits.
- This is workable, but it is a cross-service governance design that must stay explicit in docs and tests.

### 2026-04-04 Slice Started: Canonical Resource Cleanup

- Goal: remove the remaining raw `/secret` compatibility shortcuts and make M4 mint-time and request-time behavior use canonical `tool-b:/...` resource strings only.
- Scope of this slice:
  - capability-issuer canonicalization
  - OPA root-mint policy input alignment
  - tool-b request-path to canonical-resource mapping
  - unit and E2E updates for canonical `tool-b:/secret`
- Explicitly out of scope for this slice:
  - changing the external HTTP path `/secret`
  - redesigning the Redis-backed provenance rule
  - mint-rate enforcement
  - broader observability closure

### Remaining M4 Work After This Slice

- new-resource mint-rate enforcement at `capiss`
- full mint-decision provenance logging on every `capiss` exit path
- strict canonical-resource contract cleanup
- broader M4 observability/reconstruction closure

## 2026-04-08 Slice Started: capiss New-Resource Mint-Rate Enforcement

- Goal: add the missing M4 governance control that bounds how many new canonical resources can be minted under one `root_token_id`.
- Scope of this slice:
  - refine the requirement into a formula-based mint-rate rule
  - add Redis-backed authoritative state for mint-rate consumption
  - enforce the rule only on `resource_mint` when `canonical_res != parent_res`
  - add unit and E2E proof for allow, deny, and fail-closed behavior
- Locked contract for this slice:
  - keying: `root_token_id`
  - rule: `max(1, floor(root_token_lifetime_seconds / 20))`
  - current default: `60s` root lifetime -> `3` allowed new-resource mints
  - same-resource remints do not consume allowance
  - store errors fail closed
- Explicitly out of scope for this slice:
  - redesigning request-time budget/rate enforcement
  - redesigning Redis-backed mint provenance
  - broader mint-decision logging closure outside the new mint-rate path

## 2026-04-08 Slice Implemented: capiss New-Resource Mint-Rate Enforcement

- Requirements and architecture were refined first:
  - added `REQ-M4-B7` as an explicit requirement for formula-based new-resource mint-rate enforcement at `capiss`
  - documented the new Redis key family `m4:mint_rate:<root_token_id>` in architecture as authoritative state written and read only by `capability-issuer`
- Implementation updates applied:
  - added `consume_mint_rate(...)` in `services/capability-issuer/app.py`
  - rule implemented as `max(1, floor(root_token_lifetime_seconds / 20))`
  - current default remains `M4_ROOT_TTL_SECONDS=60`, so the effective allowance is `3`
  - enforcement runs only on `resource_mint` when `canonical_res != parent_res`
  - same-resource remints do not consume mint-rate allowance
  - store failures fail closed as `store_unavailable`
  - over-limit mints deny as `mint_rate_exceeded`
- Redis state introduced by this slice:
  - `m4:mint_rate:<root_token_id>`
    - writer/reader: `capability-issuer`
    - value: consumed new-resource mint count
    - TTL: bounded to the remaining root-token lifetime
- Trace/test updates applied:
  - added `DD-221` for the mint-rate helper
  - added `UT-129` through `UT-137`
  - added `M4-T8` for the fourth new-resource mint denial case
  - updated `trace/tests.yaml` and unit/E2E spec docs
  - updated `docs/unit_test_spec.md` so `M4-B7` is explicitly mapped to unit coverage
- Validation completed and passing:
  - focused capiss mint-rate unit slice: `9 passed`
  - capiss unit files touched by the slice: `42 passed`
  - `make qa-trace`: passed (`requirements=118`, `architecture=20`, `design=46`, `tests=144`)
  - `make qa-quality`: passed (`157 passed`)
  - targeted `M4-T8` run: passed
  - full E2E suite: `40 passed`, `0 failed`
  - `make qa-evidence`: passed (`validated=40/40`, expected 2 warnings only)

### Remaining M4 Work After This Slice

- full mint-decision provenance logging on every `capiss` exit path
- broader M4 observability/reconstruction closure

## 2026-04-09 Slice Started: capiss Mint-Decision Logging Closure

- Goal: close `REQ-M4-O2` by making every `capiss` mint request exit emit one final `capiss_mint_decision` event with stable provenance fields.
- Scope of this slice:
  - tighten the final mint-decision event contract in requirements and architecture
  - add one shared mint-decision logging helper in `capability-issuer`
  - close remaining unlogged `root_mint` and `resource_mint` branches
  - add unit coverage for exact final-event payloads on representative allow, deny, and fail-closed exits
- Locked behavior for this slice:
  - logging remains append-only JSON on stdout
  - container logs remain the immediate runtime sink
  - `subject_spiffe_id` is the only identity field in final mint logs for the current offline-delegation model
  - no new storage or visualization subsystem is introduced here
- Follow-up note:
  - observability presentation/visualization should be revisited in a later slice without changing the current enforcement or logging path

## 2026-04-12 Slice Started: Reduced-Scope M4 Observability and Reconstruction Closure

- Goal: close the remaining reduced-scope M4 observability work (`REQ-M4-O1`, `REQ-M4-O3`, `REQ-M4-O4`) without adding a new storage subsystem.
- Review bundle created under:
  - `docs/slices/m4-observability-closure/`
- Locked direction for this slice:
  - keep stdout JSON as the runtime audit stream
  - capture observability proof through harness-collected container logs and evidence artifacts
  - align final `tool-b` enforcement events to the authored requirement schema
  - add the missing reconstruction fields needed for current reduced-scope offline delegation
  - retire obsolete audit-field names and duplicated inline payload assembly
- No tests or implementation started yet for this slice because the new process requires Phase 1 review first.

## 2026-04-09 Slice Implemented: capiss Mint-Decision Logging Closure

- Requirements and architecture were refined first:
  - `REQ-M4-O2` now explicitly requires one final mint-decision event per mint request outcome
  - `ARCH-012` now states that `capability-issuer` owns complete mint-decision logging for every mint exit and that current storage is structured JSON on stdout captured by container logs
- Implementation updates applied:
  - added `log_mint_decision(...)` in `services/capability-issuer/app.py`
  - added `DD-222` for the final mint-decision logging seam
  - refactored `root_mint(...)` and `resource_mint(...)` so all current exits emit exactly one final `capiss_mint_decision`
  - helper policy events (`capiss_policy_error`, `capiss_policy_decision`) remain secondary events, but `REQ-M4-O2` proof now comes from the final mint-decision event
- Unit/trace updates applied:
  - added `UT-138` through `UT-141`
  - extended existing endpoint tests to assert exact final mint-decision payloads on:
    - early auth/identity failures
    - payload and canonical-resource rejects
    - policy deny
    - registry/store/mint-rate fail-closed paths
    - success paths
  - updated `docs/unit_test_spec.md` so `M4-O2` is now marked covered
- Validation completed and passing:
  - `pytest tests/unit/capiss/test_endpoints.py -q`: `23 passed`
  - `pytest tests/unit/capiss/test_chain_and_policy.py -q`: `19 passed`
  - `make qa-trace`: passed (`requirements=118`, `architecture=20`, `design=47`, `tests=148`)
  - `make qa-quality`: passed (`161 passed`)
- Storage model remains unchanged:
  - append-only structured JSON on stdout
  - container logs remain the immediate runtime sink
  - better observability presentation/visualization remains deferred to a later slice

### Remaining M4 Work After This Slice

- broader M4 observability/reconstruction closure (`REQ-M4-O1`, `REQ-M4-O3`, `REQ-M4-O4`)

### 2026-04-04 Slice Progress: Canonical Resource Cleanup

- Requirements and architecture were aligned first for canonical `tool-b:/...` resource strings.
- Implementation updates applied:
  - `capability-issuer` now canonicalizes `/secret` to `tool-b:/secret` and returns canonical `res` values from mint endpoints.
  - `tool-b` now maps request path `/secret` to canonical required resource `tool-b:/secret` and removed the raw `/secret` token-acceptance compatibility branch.
  - OPA mint policy now reasons over canonical `tool-b:/secret` instead of raw `/secret`.
- Trace/test updates applied:
  - unit tests were updated to use canonical resource values while keeping the external HTTP path `/secret` unchanged.
  - E2E harness request bodies and spec docs were updated so mint requests use canonical `tool-b:/secret`.
  - detailed/readable spec text now distinguishes token resource `tool-b:/secret` from HTTP path `/secret`.
- Validation completed and passing:
  - focused canonical-resource unit tests: `52 passed`
  - `make qa-trace`: passed
  - `make qa-quality`: passed (`148 passed`)
- Runtime validation status:
  - targeted `docker compose run` M3/M4 checks were inconclusive because the run path showed a separate harness/material issue (`curl --key` blank argument).
  - clean full-suite validation is currently blocked by a broader stack startup regression affecting M1/M2 before canonical-slice checks become trustworthy.
  - observed unrelated failures include missing legit SPIRE attestation readiness and unexpected TLS/entry-list outcomes in M1/M2 after clean startup.
- Slice status:
  - implementation and local/unit traceability are complete
  - full E2E validation is blocked by unrelated stack/harness startup issues and is not yet a trustworthy acceptance signal for this slice
- Next action requires explicit direction:
  - either debug the broader stack startup regression first
  - or accept the canonical slice as code-complete pending later E2E revalidation

### 2026-04-12 Slice Progress: Reduced-Scope M4 Observability and Reconstruction Closure

- Phase 1 bundle was created under `docs/slices/m4-observability-closure/`.
- Phase 2 test authoring is now in progress:
  - unit tests were added to pin the target final-event schema for `tool-b` allow/deny audit events and delegated `capiss_mint_decision` provenance.
  - new M4 E2E cases `M4-T9` and `M4-T10` were authored to capture container logs into evidence and assert correlated audit events for one allow flow and one deny flow.
  - trace/spec artifacts were updated so the observability slice is represented at the black-box proof layer before implementation begins.
- Intended failing baseline for Phase 2:
  - `tool-b` still emits `caller_subject_spiffe_id` instead of the requirement-aligned `subject_spiffe_id`.
  - `tool-b` final enforcement events do not yet carry `delegator_spiffe_id`.
  - `capiss_mint_decision` does not yet carry `delegator_spiffe_id` on delegated/resource-mint paths.
- No service implementation changes were made as part of Phase 2.

### 2026-04-12 Slice Progress Update: Reduced-Scope M4 Observability and Reconstruction Closure

- Phase 3 implementation is now applied:
  - `tool-b` final enforcement events are assembled through one shared schema helper.
  - obsolete `caller_subject_spiffe_id` was retired from final `toolb_enforcement_decision` events.
  - final `toolb_enforcement_decision` events now emit `subject_spiffe_id`.
  - final `toolb_enforcement_decision` events now emit `delegator_spiffe_id` when present in verified claims.
  - `capiss_mint_decision` now accepts and emits optional `delegator_spiffe_id`.
  - `resource_mint(...)` now routes its final audit events through a local helper that consistently includes delegator provenance for delegated/resource-mint paths.
- Phase 3 retirement applied:
  - duplicated inline tool-b enforcement-event payload assembly was removed.

### 2026-04-26 Open Problem Tracking

- Added `docs/open_problem_log.md` for runtime and trust-path problems that need follow-up independent of slice-progress notes.
- Current tracked problem:
  - `OPL-001`: test-profile `capability-issuer-no-opa-envoy` can intermittently serve an expired SPIFFE SVID during verified-TLS runs, causing `M3.S2-T4` to fail for the right trust reason while insecure curl-based capture still appears healthy.
  - the obsolete final-event field name `caller_subject_spiffe_id` is no longer used in service code for enforcement decisions.
- Focused sanity checks completed:
  - delegated capiss mint-provenance UT: passed
  - tool-b final allow/deny schema UTs: passed
  - `make qa-trace`: passed
- This phase-4 note is superseded by later completed full-suite runs and by the 2026-05-08 M4 semantic trace closure slice below.


## 2026-04-24 Slice Started: Verified Client Requests

- Goal: remove `--insecure` from normal HTTPS request execution paths that are used as black-box proof in M2/M3, and replace them with a single verified TLS request model.
- Scope of this slice:
  - harness HTTPS request helpers in `scripts/rogue_node_tests.sh`
  - demo client HTTPS request helpers in `agents/agent-a/client.sh`
  - authored requirement and architecture deltas for verified client requests
  - E2E/spec proof paths that currently depend on those helpers
- Locked design decisions for this slice:
  - the final HTTPS request must use one verified TLS connection
  - the helper must verify both trust chain and expected SPIFFE URI SAN
  - the final request path must not depend on IP pinning or `Host:` header spoofing
  - DNS/TCP readiness checks may remain, but they are not treated as proof of verified service identity
- Explicitly out of scope:
  - service runtime topology changes
  - Envoy trust policy changes
  - Redis/OPA/runtime service-to-service trust model changes
  - adding a second parallel request mechanism

- Phase 2 test design applied:
  - representative black-box proof paths tightened on existing cases:
    - `M3.S2-T1` now requires issuer verified-identity evidence
    - `M3.S4-T2` now requires tool-b verified-identity evidence
  - `trace/tests.yaml` now maps these proof cases to:
    - `REQ-M2-R10`
    - `REQ-M2-R11`
- Expected failing baseline before implementation:
  - current helpers do not yet emit `verified_capiss_spiffe_id.txt` / `verified_capiss_result.txt`
  - current helpers do not yet emit `verified_toolb_spiffe_id.txt` / `verified_toolb_result.txt`
  - therefore the tightened proof cases should fail until the verified request helper is implemented

## 2026-04-26 Harness Fix: M1 Rogue Attestation False Negatives

- Problem found:
  - `M1-T1`, `M1-T2`, and `M1-T3` were failing even though rogue attestation was correctly denied by SPIRE.
  - The failure was in harness classification, not in M1 security behavior.
- Root cause:
  - `run_rogue_attest_should_fail(...)` in `scripts/rogue_node_tests.sh` was using fragile live log polling.
  - The helper previously mixed timeout budgets, then still depended on seeing denial text before the rogue agent process had fully exited and flushed its final log lines.
- Fix applied:
  - give the helper one local 60-second wait budget
  - wait for the rogue agent process to exit
  - classify the final copied log after process exit instead of polling for denial strings live
- Validation:
  - rebuilt `rogue-tests`
  - reran targeted tests with the documented command:
    - `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M1-T1,M1-T2,M1-T3 rogue-tests`
  - result:
    - `Total: 3`
    - `Passed: 3`
    - `Failed: 0`

## 2026-04-26 No-OPA Test Runtime Fix

- Problem found:
  - `M3.S2-T4` was still failing after the verified-request helper fixes.
  - The remaining failure was a real runtime mismatch: the no-OPA path returned Envoy `504 upstream request timeout` instead of the authored fail-closed JSON body.
- Root cause:
  - the test-only `capability-issuer-no-opa` service used `OPA_URL=http://opa-missing:8181/...`
  - that unresolvable hostname caused slow DNS failure inside `urllib`
  - `capiss` eventually produced `{"error":"denied","reason":"opa_unavailable"}`, but only after Envoy's `15s` upstream timeout had already returned `504`
- Fix applied:
  - changed the test-only `OPA_URL` to a resolvable closed-port target on the same app network:
    - `http://redis:8181/v1/data/capiss/allow`
  - this preserves the same unavailable-OPA semantics while making failure fast and deterministic

## 2026-05-08 M4 Semantic Trace Closure Slice

- Problem found:
  - Several active M4 requirements were semantically implemented but were not represented by focused black-box E2E proof.
  - `REQ-M4-P5` described future signed discovery receipts as if it were an active M4 requirement.
  - `REQ-M4-E2` mixed black-box requirement wording with the architecture choice of a shared in-process implementation.
- Phase 1 authored:
  - Created `docs/slices/m4-semantic-trace-closure/` with plan, requirements delta, architecture delta, ADR, DDR, implementation contract, retirement contract, and validation notes.
- Requirements and architecture updates:
  - Moved signed discovery receipts out of active M4 scope and into future scope.
  - Reworded `REQ-M4-E2` to require consistent observable PEP enforcement semantics.
  - Kept the shared in-process implementation as an architecture/design choice, not as the black-box requirement itself.
  - Removed the inactive signed-receipt requirement from `ARCH-006`.
- Black-box proof updates:
  - Added focused M4 E2E cases:
    - `M4-T11`: delegated mint authority amplification is denied.
    - `M4-T12`: wildcard/non-concrete delegated resource mint is denied.
    - `M4-T13`: Redis budget and registry TTLs are bounded by root token expiry.
    - `M4-T14`: protected resource use with an already-minted token does not require capiss on the hot path.
  - Updated `trace/tests.yaml` so M4 requirement coverage is represented through suite/case evidence instead of relying on unit-level proof.
  - Updated readable, detailed, and command-level test specifications for the new M4 cases.
- Artifact cleanup:
  - Removed the stale `M4-P5` row from `docs/unit_test_spec.md` after signed receipts were moved out of active requirements.
- Validation completed:
  - `sh -n scripts/rogue_node_tests.sh`: passed.
  - `make qa-trace`: passed.
  - Targeted M4 E2E: passed, `14/14`.
  - Clean full E2E: passed, `46/46`, with two accepted alternate-isolation warnings:
    - `M3.S2-T3`: DNS resolution timeout while reaching OPA from edge.
    - `M3.S2-T5`: DNS resolution timeout while reaching capability-issuer from edge.
  - `make qa-evidence`: passed, `validated=46/46`, `warnings=2`.
  - `make qa-quality`: passed, unit baseline `164 passed`.

## 2026-05-14 M4a Jira Project Access Slice

- Implemented the M4a mock-default Jira project access slice:
  - `capiss` canonicalizes `aud=jira-tool`, `act=read`, `res=jira-tool:/project:<PROJECT_KEY>`.
  - OPA allows only `spiffe://example.org/agent-a` to mint `jira-tool:/project:IAM`.
  - `jira-tool-envoy` is the mTLS edge boundary for Jira-shaped issue reads.
  - `jira-tool` verifies root Jira tokens, binds token subject to the Envoy caller identity, enforces project scope before upstream use, consumes Redis budget/rate state, verifies successful upstream project fields, and emits `jiratool_enforcement_decision`.
  - `jira-mock` provides deterministic broad-upstream fixtures for `IAM-*` and `NAS-*`.
  - `agents/agent-a/jira_demo.sh` and `scripts/jira_live_smoke.sh` are explicit operator actions and do not run automatically.
- Review findings fixed during closure:
  - corrected the `M4a-T9` mock-log jq assertion that caused a false failure;
  - added capiss mTLS `/health` readiness after the existing `M4-T14` capiss restart path;
  - added M4a mint short-circuits so downstream protected reads do not hide mint setup failures;
  - added Jira-tool unit coverage to satisfy the existing `make unit-trust` coverage gate.
- Validation completed:
  - `pytest tests/unit/jiratool/test_authorization.py`: passed, `17 passed`.
  - `make unit-trust`: passed, `194 passed`, total line coverage `89.62%`.
  - targeted M4a E2E: passed, `10/10`.
  - clean full E2E: passed, `56/56`, with the two accepted existing M3 isolation warnings:
    - `M3.S2-T3`: DNS resolution timeout while reaching OPA from edge.
    - `M3.S2-T5`: DNS resolution timeout while reaching capability-issuer from edge.
  - `make qa-trace`: passed, report at `artifacts/quality/traceability_report.json`.
  - `make qa-evidence`: passed, `validated=56/56`, `warnings=2`, report at `artifacts/quality/evidence_report.json`.
  - `make qa-quality`: passed, unit baseline `194 passed`.
- Evidence paths:
  - deterministic E2E evidence: `artifacts/rogue-tests/M4a-*`
  - timing artifacts: `artifacts/rogue-tests/guard_timings.tsv`, `artifacts/rogue-tests/guard_timings_top25.txt`
  - trace/evidence reports: `artifacts/quality/traceability_report.json`, `artifacts/quality/evidence_report.json`
- Remaining note:
  - live Jira smoke was not run in this environment because live Jira configuration was not provided; it remains explicit opt-in via `make jira-live-smoke` and writes to `artifacts/jira-live-smoke/`.

## 2026-06-06 M5 Varambu Audit Demo Slice

- Implemented the Varambu audit demo flow:
  - added top-level `varambu` CLI with `start`, `audit`, `show-audit-logs`, and `audit-file`;
  - retained `start_Varambu` as a compatibility wrapper around `varambu start`;
  - added active capiss audit tailing into per-session `artifacts/varambu-demo/<session>/capiss_audit.jsonl` and `capiss_audit.log`;
  - added current-session selection through `artifacts/varambu-demo/current`;
  - added local-time audit formatting through `VARAMBU_TZ`, with UTC fallback;
  - enriched authoritative `capiss_mint_decision` events with subject, resource context, correlation, issued/expires/logged UTC and local times, TTL, token IDs, and policy metadata;
  - kept bearer token values and upstream secret material out of capiss audit events and Varambu audit artifacts.
- Authored requirements, architecture, slice plan, test plan, and trace updates:
  - `REQ-M4-O2` extended for enriched mint-decision audit fields and secret exclusion;
  - `REQ-M5-VA1` added for Varambu session audit artifacts and command-line display;
  - `ARCH-032` added for Varambu demo audit session state and active tailing;
  - `M5-T42` added for runtime Varambu audit-file proof.
- Validation completed in this environment:
  - `make unit-trust`: passed, `244 passed`, total line coverage `86.40%`.
  - `make qa-trace`: passed, report at `artifacts/quality/traceability_report.json`.
  - `make qa-quality`: passed, unit baseline `244 passed`.
  - `bash -n varambu start_Varambu scripts/rogue_node_tests.sh`: passed.
  - `python3 -m py_compile scripts/varambu_audit.py services/capability-issuer/app.py services/codex-jira-mcp-adapter/server.py scripts/validate_traceability.py`: passed.
  - `./varambu audit-file`: passed and resolved current session audit artifact paths.
- Validation not completed in this environment:
  - Docker-backed targeted E2E `M5-T42` was not run because this process cannot connect to `/var/run/docker.sock` (`permission denied while trying to connect to the docker API`).
  - Run when Docker daemon access is available:
    - `docker compose --profile tests -f compose/spiffe.compose.yml run --rm -e TEST_ONLY=M5-T42 rogue-tests`
    - `make qa-evidence`
