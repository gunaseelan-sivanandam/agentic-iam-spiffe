# Varambu Audit Log Human-Format Slice

## Goal
Make the operator-facing audit log easier to read in demos: color minted vs denied decisions, uppercase the minted status, and de-ambiguate the denied header (`DENIED policy` reads like "denied the policy"). Structured evidence (JSONL) is unchanged; this is presentation only.

No new system behavior → **no new REQ/ARCH/DD IDs** (light-docs decision). The renderer keeps its existing `DD-902 / ARCH-032` annotations.

## Approved Grill-Me Decisions (2026-06-13)

### Human header format (`render_record`, written plain into `capiss_audit.log`)
| Decision | Approved behavior |
| --- | --- |
| Minted header | `#<seq> MINTED OK  <local time>` — the allow `reason_code` (`ok`) upper-cased. Not `MINTED: Reason OK`. |
| Denied header | `#<seq> DENIED: Reason <Reason>  <local time>` — replaces the misleading `DENIED policy`. |
| Reason transform | **Title-case, underscores→spaces** (Option B). `policy`→`Policy`, `sub_mismatch`→`Sub Mismatch`, `mint_rate_exceeded`→`Mint Rate Exceeded`. Applies to all ~14 deny `reason_code`s; zero-maintenance, no lookup table. |
| Layout | Unchanged otherwise: keep the `#<seq>` prefix, the trailing `  <local time>`, and all detail lines (`Subject:`, `Logged At:`, …). |

### Color
| Decision | Approved behavior |
| --- | --- |
| Where | **Display-time only**, in `varambu audit` / `show` (`_read_file`), gated on `sys.stdout.isatty()`. The persisted `capiss_audit.log` stays **plain text** (secret-free evidence; the e2e greps it; ANSI must never leak into the file or a pipe). Mirrors the `varambu start` "TTY color, plain log" decision. |
| Scope | **Whole header line** colored (Option A): green for `#… MINTED OK …`, **bold red** for `#… DENIED: Reason … …`. Detail lines stay uncolored. |
| Detection | A printed line is colored when it matches `^#\d+ MINTED` (green) or `^#\d+ DENIED` (red). |

### Tests (updated in lockstep; both suites stay green)
| Test | Change |
| --- | --- |
| `tests/unit/test_varambu_audit.py` | Exact-string expectations → `#1 MINTED OK …` (×2) and `startswith("#2 DENIED: Reason Policy …")`. |
| e2e T42 | greps `'MINTED OK'` / `'DENIED: Reason Policy'`. |
| e2e T44, T46 | **Synthetic fixtures** (hand-written `printf` audit lines, not live-captured) updated for hygiene → `#1 MINTED OK  -` / `#1 DENIED: Reason Policy  -`. They didn't strictly break (their asserts grep the `MINTED`/`DENIED` substrings), but the fabricated samples now match the real renderer. |
| e2e T47 | Header regex generalized to `^#[0-9]+ (MINTED\|DENIED).* <local time>` so it matches both `MINTED OK` and `DENIED: Reason <…>`. |

### Docs
Light (Option A): this slice doc records the decisions; no new REQ/ARCH/DD IDs; `detailed_design.md` not amended. See [[varambu-trust-domain-rename]] and the `varambu-start-ux` slice for related Varambu UX/operational notes.

## Verification
- Unit suite: 249/249 pass.
- Manual renders confirmed plain (non-TTY): `MINTED OK`, `DENIED: Reason Policy`, `DENIED: Reason Sub Mismatch`, `DENIED: Reason Mint Rate Exceeded`.
- TTY (pty): whole minted header green, whole denied header bold-red, detail lines plain.
- T47 regex matches all new headers.
- e2e (`109/109`) not re-run here (needs a docker bring-up that would reset the running stack); the touched assertions/fixtures are aligned with the new renderer.
