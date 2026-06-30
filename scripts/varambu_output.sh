# shellcheck shell=bash
# Varambu `start` output layer. Sourced by ./varambu and by tests/shell/test_varambu_output.sh.
#
# Contract:
#   - VARAMBU_VERBOSE=1 mirrors vb_detail() lines to stdout; default 0 keeps them log-only.
#   - Color is applied only on an interactive TTY (stdout). The log file and any
#     piped/redirected output stay PLAIN — ANSI escapes never leak into them.
#   - vb_phase / vb_phase_ok / vb_phase_fail render the crisp phase checklist.
#     On an interactive, non-verbose terminal the in-progress line is redrawn in
#     place (▶ -> ✓); otherwise each event is a separate plain line.
#   - The log file is VARAMBU_LOG_FILE (defaults to /dev/null when unset).

: "${VARAMBU_VERBOSE:=0}"
: "${VARAMBU_LOG_FILE:=/dev/null}"

if [ -t 1 ]; then _vb_color=1; else _vb_color=0; fi
if [ "$_vb_color" -eq 1 ]; then
  _C_TITLE=$'\033[1;36m'; _C_DIM=$'\033[2m'; _C_OK=$'\033[32m'
  _C_RUN=$'\033[33m'; _C_ERR=$'\033[1;31m'; _C_BANNER=$'\033[1;32m'; _C_RST=$'\033[0m'
else
  _C_TITLE=''; _C_DIM=''; _C_OK=''; _C_RUN=''; _C_ERR=''; _C_BANNER=''; _C_RST=''
fi
# Redraw the in-progress line in place only on an interactive, non-verbose terminal.
if [ "$_vb_color" -eq 1 ] && [ "$VARAMBU_VERBOSE" -eq 0 ]; then _vb_redraw=1; else _vb_redraw=0; fi

_VB_PHASE=""

_vb_log() { printf '%s\n' "$*" >>"$VARAMBU_LOG_FILE" 2>/dev/null || true; }

# vb_detail: full-detail line. Always to the log; to stdout only when verbose.
vb_detail() {
  _vb_log "$*"
  [ "$VARAMBU_VERBOSE" -eq 1 ] && printf '%s\n' "$*"
  return 0
}

vb_title() {
  _vb_log "=== Varambu ($1 mode) ==="
  printf '\n%sVarambu%s\n' "$_C_TITLE" "$_C_RST"
  printf '%s%s mode%s\n\n' "$_C_DIM" "$1" "$_C_RST"
}

vb_phase() {
  _VB_PHASE="$1"
  _vb_log "[$(date -u +%H:%M:%SZ)] PHASE $1"
  if [ "$_vb_redraw" -eq 1 ]; then
    printf '  %s▶%s %s…' "$_C_RUN" "$_C_RST" "$1"
  else
    printf '  %s▶%s %s…\n' "$_C_RUN" "$_C_RST" "$1"
  fi
}

# vb_phase_ok [suffix]   e.g. vb_phase_ok "(8 SVIDs)"
vb_phase_ok() {
  suffix=""
  [ "$#" -ge 1 ] && [ -n "$1" ] && suffix=" $1"
  _vb_log "[$(date -u +%H:%M:%SZ)] OK ${_VB_PHASE}${suffix}"
  if [ "$_vb_redraw" -eq 1 ]; then
    printf '\r\033[K  %s✓%s %s%s\n' "$_C_OK" "$_C_RST" "$_VB_PHASE" "$suffix"
  else
    printf '  %s✓%s %s%s\n' "$_C_OK" "$_C_RST" "$_VB_PHASE" "$suffix"
  fi
  _VB_PHASE=""
}

# vb_phase_fail reason
vb_phase_fail() {
  reason="${1:-failed}"
  _vb_log "[$(date -u +%H:%M:%SZ)] FAIL ${_VB_PHASE} — ${reason}"
  if [ -n "$_VB_PHASE" ]; then
    [ "$_vb_redraw" -eq 1 ] && printf '\r\033[K'
    printf '  %s✗%s %s — %s\n' "$_C_ERR" "$_C_RST" "$_VB_PHASE" "$reason"
  fi
  _VB_PHASE=""
}

vb_banner() {
  _vb_log "VARAMBU_STARTED"
  printf '\n%sVARAMBU STARTED%s\n' "$_C_BANNER" "$_C_RST"
}

# vb_fail_footer code
vb_fail_footer() {
  printf '\n%sVarambu start failed (exit %s).%s\n' "$_C_ERR" "$1" "$_C_RST" >&2
  printf '  Details: %s\n' "$VARAMBU_LOG_FILE" >&2
  [ -n "${VARAMBU_STACK_LOG_FILE:-}" ] && [ -s "${VARAMBU_STACK_LOG_FILE:-}" ] \
    && printf '  Stack log: %s\n' "$VARAMBU_STACK_LOG_FILE" >&2
  return 0
}
