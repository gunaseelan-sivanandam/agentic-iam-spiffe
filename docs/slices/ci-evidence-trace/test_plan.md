# Slice Test Plan — ci-evidence-trace

Status: **draft for plan review** with [`plan.md`](plan.md) (2026-10-30).

## Goal
Prove that each check this slice adds fails on the honest mistake it exists to catch (M1–M10 in the
plan's threat model), with a negative control per check, and that the CI E2E job produces the same
verdict as the local run.

## Inputs
- [`plan.md`](plan.md): decisions D1–D11, the threat model and blocking criteria, REQ-T-R9, the
  `REQ-SEC` static tests.
- The CI trial of 2026-10-30 (runs `40999541906`, failed in `qa-evidence` on root-owned output;
  `41000278717`, passed after taking ownership).

## Unit test plan
None. This slice changes QA tooling and the harness, not services; QA tooling is tested in
`tests/tools/` (`AGENTS.md`, documentation rules). Existing unit tests and their gates are unchanged.

## Tooling tests (`tests/tools/`, each with a negative control)
IDs V1–V12 are local to this test plan.

**Increment A — CI evidence**
- **V1 `make e2e` output ownership** (D1, M10): after the target, `artifacts/` (including
  `artifacts/rogue-tests/`) and `test_report.log` are owned by the invoking user, and
  `make qa-evidence` can create `artifacts/quality/` (the trial's failure); the target exits with the harness's exit code,
  so a failed suite fails the target (fixture: a harness stub exiting 1).
- **V2 Evidence secret check** (D3, REQ-T-R9, M6), one fixture each, all fail `qa-evidence`:
  - a Biscuit-shaped token (base64url, the length of a real capiss token) in a `.txt` file;
  - the same token inside a JSON field;
  - a PEM `PRIVATE KEY` block;
  - a `JIRA_API_TOKEN=` or `Authorization: Bearer` line with a value;
  - the exact value of a registered restricted asset (a synthetic `root_key.b64`: raw base64 of 32
    random bytes, no recognisable shape) in plain form, and the same value base64-encoded;
  - a registered asset file that exists but cannot be read (fails closed).

  The failure message names the file and the kind of secret, never the value (asserted).

  Accepted (positive controls): a SHA-256 hex fingerprint; a PEM `CERTIFICATE` block (SVID
  certificates); SPIRE `request_id` and correlation IDs; a 3000-character run of one repeated
  character (M5-T53's padding). Boundaries of the shape rule (plan D3): a varied run of 199
  characters is accepted, 200 and 201 are rejected; a 200-character run with 19 distinct
  characters is accepted, with 20 rejected.
- **V3 Pinned tags** (D2, M8 as narrowed): `security/invariants.yaml` and compose name the same
  exact tags for `opa` and `redis`, and neither is `latest`; `qa-deploy` reports a compose tag that differs from the register (existing
  default-deny rule, one fixture).

**Increment B — trace model**
- **V4 Static test entries** (D4, D5): a static entry that links `source_requirements` and names a
  gate and its negative-control tests passes; a listed test file or selector that does not exist is
  a structural failure; a static entry with no `test_spec.md` heading fails `docs-check`, and so
  does a static heading with no entry.
- **V5 `qa-deploy` report** (D5, M3, M4): on fixtures, the report gives `holds` for a requirement
  with no violation, `known_violation` with its OPL for one covered by a known-violation row, and
  `grace` for D2 with a grandfathered root service before 2027-01-31 (and an error after, as today).
  With `--skip-image-users`, D2 is `not_checked` and the report says image users were not
  inspected. The report contains no env values. On today's compose with image inspection: K1, K2,
  K4 `known_violation` (OPL-005, -006, -008), D2 `grace`, the other six `holds`.
- **V6 Static evidence in `qa-evidence`** (D5, M4), each fails: a missing report; an unreadable
  report; malformed JSON;
  a report missing a `REQ-SEC`; an unknown status; a report made with `--skip-image-users`
  (matching digests, inspection skipped); a compose or register digest that differs from the files
  on disk; a report whose status for a requirement disagrees with the register (for example K1
  `holds` while the register has an OPL-005 row). A complete, matching report passes.
- **V7 Trace status** (D5, M3): `qa-trace` takes the status from the register, never from a run
  report. A requirement whose only proof is a static test and whose asset has a `known_violations`
  row appears as "not proved: known violation OPL-xxx" and counts as a gap; without such a row it
  counts as proved statically; D2 before its grace date is "not proved: grace" and counts as a
  gap. Clean-checkout case: with no
  `artifacts/` directory at all, `qa-trace` gives the same statuses, on the head and on the
  merge-base fixture.
- **V8 Config-implemented ARCH** (D6, M9): an ARCH section with `Implemented by:` naming existing
  files counts as implemented; a named file that does not exist is a structural failure; a section
  with neither a DD nor `Implemented by:` stays a gap.
- **V9 Gap gate** (D7, M1, M2), on base/head fixture pairs:
  - head adds a gap in each category, one fixture each — a requirement without proof, an ARCH
    section without DD or `Implemented by:`, a DD without UT, a test linked to no requirement →
    fails, naming the gap;
  - head closes one old gap and adds a different one (total unchanged) → fails;
  - the same with an `accepted_gaps` entry → passes;
  - the entry is valid through its expiry date (23:59:59 UTC) and fails one second later (clock
    injected);
  - an entry whose gap does not exist on head (stale) fails;
  - an entry without a reason or expiry fails;
  - head closes an old gap → passes;
  - a gap present on base and head → passes (old gaps do not fail);
  - `--mode push` reports and passes;
  - `--mode pr` with a base that cannot be resolved (shallow history, unknown ref) or whose trace
    inputs cannot be read → fails, never falls back to push mode;
  - diverged history: the base is the merge-base, not the tip of `main`.
  - the head renames a gap category (as Increment B does): an old gap under its new category name
    still matches its base entry and passes.
- **V10 Gate consistency** (D8, M5), one fixture each, all fail:
  - a gate the `AGENTS.md` table marks as CI with no job of that name in `ci.yml`;
  - a job in `ci.yml` that is not in the table;
  - a job that is not a required check in a ruleset fixture;
  - a job with a gate's name whose steps run another make target (for example `qa-deploy` running
    `make docs-check`);
  - a ruleset fixture that cannot be read or parsed (fails closed, never passes).

  Positive control: today's table, workflow and ruleset after this slice's changes and the user's
  ruleset update.
- **V11 Retirement** (D6): `qa-trace` on the merged result reports no DD-925 to DD-930 tags and no
  `IT-DEPLOY-*` entries, and the retired IDs are marked retired, not reused.
- **V12 Historical replay of the 1B miss** (D7, M1): `qa-trace` gap comparison of 1B's head
  (`0dbd27b`) against its base (`8faeea9`), run on those commits' trace inputs, fails on the ten new
  `REQ-SEC` gaps.

## E2E test plan
No E2E test changes its premise, exercise or outcome; the expected-outcome table has no rows. The
tests that write token values into evidence change only where they keep the token: every test that
writes `token.txt`, `token1.txt`, `token2.txt`, `create_token.txt`, `read_token.txt`,
`tampered_token.txt` or a `*_mint.json` with a `token` field (M3, M4, M4b and M5 tests; the exact
list is in the Increment A PR). For each, `docs/test_spec.md` names the fingerprint instead of the
token file.

| Test | By | Signature | Twin | Source | Replaces |
| --- | --- | --- | --- | --- | --- |
| — | — | — | — | — | — |

**Static tests** (spec entries in `docs/test_spec.md`, Increment B):
- `DEPLOY-K1` … `DEPLOY-K8`, `DEPLOY-D1`, `DEPLOY-D2`: what each requirement demands, how
  `qa-deploy` checks it on every PR, which `tests/tools/test_qa_deploy.py` tests show the gate fails
  on each kind of violation, and the report status that is the result.
- `EVID-T1` (Increment B; its check lands in A): the `qa-evidence` secret check over every run's
  evidence; its negative controls are V2.

## Assumptions and fixtures
- Default E2E mode uses deterministic mocks; `M5-T55` stays env-gated and is skipped in CI.
- Ruleset fixtures are JSON copies of the GitHub API response; the live read happens only in CI.
- Time-dependent checks (accepted-gap expiry, D2 grace) take an injectable clock.
- All secret fixtures are synthetic (random values made by the test); no fixture is derived from
  the trial artifacts or a real key.
- V12 reads the trace inputs of old commits with `git show`; it does not check out old code.

## Planned verification commands
- `make tooling-test`, `make qa-trace`, `make docs-check`, `make qa-deploy`, `make test-lint`
- `make qa-quality`
- Full E2E on a clean stack locally, `make qa-evidence`
- The `e2e` and gate-consistency jobs green on the implementation PRs (GitHub)

## Review notes
- V2's shape rule is fixed in plan D3; the Increment A PR states it in the `AGENTS.md` gate row of
  `qa-evidence`, and Increment B in `docs/test_spec.md` under `EVID-T1`.

## Independent review at the implementation PR
A reviewer that is not the author (Codex, or a clean-context Claude) answers in the PR body:
1. *Tests:* for each new or changed test, which wrong failure would still pass it (service down,
   another status, the right status with another reason, another component answering, a missing
   value or empty file read as success)? Does its assertion match the expected-outcome row?
2. *Keys:* does the change make a key, socket or secret reachable by a service outside the holder
   list, through a compose mount, an env var, a Dockerfile `COPY`, an entrypoint or script that
   copies or writes it, or a shared volume?

A "yes" to either blocks, under [AGENTS.md — PoC scope and proportion](../../../AGENTS.md#poc-scope-and-proportion).
