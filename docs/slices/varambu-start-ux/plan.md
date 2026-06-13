# Varambu `start` Output UX Slice

## Goal
Make `varambu start` produce **crisp, colored, demo-friendly output** by default — a short phase checklist ending in a `VARAMBU STARTED` banner — and move the existing verbose detail behind an explicit `--verbose` flag. The full detail is always preserved in the session log file.

This is a presentation refinement to an existing operator command. It introduces **no new system behavior**, so it adds **no new REQ/ARCH IDs** (light-docs decision below). It does not touch the unit suite or the docker e2e (which never exercise `varambu start`), so `109/109` stays green.

## Approved Grill-Me Decisions (2026-06-13)

### Output model
| Decision | Approved behavior |
| --- | --- |
| Default output | Phase-level checklist + final banner. No session paths, no demo prompt, no `codex -C …` next-commands in the crisp default. |
| Final banner | The word `VARAMBU STARTED` (not "Ready"), plain **bold-green** (not boxed/inverse). |
| Title | Just `Varambu` (bold/cyan). No tagline. |
| Mode display | A **dim subtitle** under the title: `mock mode` / `live mode` (Option A). Not in the title, not in the banner. |
| Log file | Always captures **full detail** (unchanged): every step, `key=value`, `ready:`/`svid_ready:`, compose/BuildKit output, command traces, MCP stderr, session/prompt block. |
| `--verbose` | Keeps **today's detailed stdout lines** (`key=value`, `[time]` steps, `ready:`/`svid_ready:`, MCP stderr, session/prompt block), **with the crisp checklist kept on top** for structure. Compose/BuildKit output stays log-only, as today. |
| `--verbose` placement | A flag alongside `--live`/`--mock`/`--timezone`/`--no-build`/`--no-codex-config`. |

### In-progress affordance (Option A)
| Decision | Approved behavior |
| --- | --- |
| Slow phases | Print `▶ <phase>…` when a phase begins, then **redraw the same line** to `✓ <phase>` on success. Static two-state, no spinner. |
| Non-TTY / piped | **Plain fallback**: one line per event (`▶` line, then `✓` line), no in-place redraw. |

### Colors / palette
| Decision | Approved behavior |
| --- | --- |
| Palette | Title cyan/bold; `▶` dim/yellow; `✓` green; `✗` bold red; `VARAMBU STARTED` bold green; phase text default color. |
| When applied | **Interactive TTY only.** No `--no-color` flag; no `NO_COLOR` gating needed. |
| Log + pipes | **Plain text — never leak ANSI escapes into the log file or piped output.** ("TTY color, plain log.") |

### Phase checklist (7 phases)
| Crisp phase line | Covers today's internal steps |
| --- | --- |
| `Preflight` | prepare `varambu` command; `docker info`/`compose version`/`context ls`; `clean_stack.sh --check` (read-only prerequisite check); live-env validation |
| `Reset environment` | stop previous audit tailer; `clean_stack.sh` |
| `Start SPIFFE/SPIRE stack` | `compose up -d --build`; wait for the 8 demo containers |
| `Issue workload identities (N SVIDs)` | wait for workload SVIDs; **count kept** on success |
| `Start audit capture` | start capiss audit tailer; set `current` symlink |
| `Verify MCP tools` | validate MCP stdio bridge via `tools/list`; **tool names NOT listed** |
| `Configure Codex` | `configure_codex_mcp`; **line omitted entirely** when `--no-codex-config` |
| (capture startup stack log) | log-only; **not a visible phase** |

### Failure UX
| Decision | Approved behavior |
| --- | --- |
| Failed phase | In-progress `▶` flips to red `✗ <phase> — <one-line reason>`. Always shown, even in default mode. |
| Reason | **One-line human reason** beside `✗` for guarded failures (missing live env, MCP tool discovery, audit tailer). Full detail in the log. |
| Footer | Red `Varambu start failed (exit N).` + `Details: <log_file>` (+ `Stack log: …` when captured). |
| Marker | Keep the literal `VARAMBU_ERROR` marker **in the log** for grep/operator use. |

### Testing & docs
| Decision | Approved behavior |
| --- | --- |
| Tests (1A) | Shell-level test of the **output layer** invariants (no live stack needed): default stdout = checklist + `VARAMBU STARTED` with no `key=value`/`ready:` lines; `--verbose` includes detail; log file always full; **non-TTY output contains no ANSI escapes**. Implemented by factoring the emit/color helpers into `scripts/varambu_output.sh` so they are exercisable without Docker. |
| Docs (2B) | Light: update `usage()` text only; **no new REQ/ARCH IDs**. This plan doc records the decisions. |
| `start_Varambu` | No change — it `exec`s `varambu start "$@"`, so `--verbose` flows through. |

## Implementation notes
- New `scripts/varambu_output.sh` owns the emit layer: TTY/color detection, `VARAMBU_VERBOSE`, `vb_detail` (log always; stdout iff verbose), `vb_phase`/`vb_phase_ok`/`vb_phase_fail`, `vb_title`, `vb_banner`, `vb_fail_footer`. Color is decided at source time from `[ -t 1 ]`; the log gets plain text only.
- `varambu` sources the lib after computing `LOG_FILE`/`VERBOSE`, redefines `say` as a thin `vb_detail` wrapper (so all existing `say "key=value"` calls become log/verbose-only), reroutes `wait_*` `ready:`/`svid_ready:` echoes through `say`, and rewrites the main start flow into the 7 phases above. `run()` and `compose up` keep sending raw output to the log only.
- See [[varambu-trust-domain-rename]] for related Varambu/e2e operational notes.
