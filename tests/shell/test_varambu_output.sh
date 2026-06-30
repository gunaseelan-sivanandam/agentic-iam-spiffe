#!/usr/bin/env bash
# Shell-level test for the varambu start output layer (scripts/varambu_output.sh).
# Verifies the crisp/verbose/plain-log invariants WITHOUT bringing up the stack.
# All cases run with stdout captured (a pipe), i.e. non-TTY, so color must be off.
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB="$ROOT_DIR/scripts/varambu_output.sh"
PASS=0
FAIL=0
ESC=$'\033'

ok()   { PASS=$((PASS+1)); printf '  ok   - %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL - %s\n' "$1"; }

# emit <verbose> <logfile> <commands...> : run the lib then the given shell snippet.
emit() {
  local verbose="$1" logf="$2" snippet="$3"
  VARAMBU_VERBOSE="$verbose" VARAMBU_LOG_FILE="$logf" \
    bash -c '. "$0"; '"$snippet" "$LIB"
}

contains()    { case "$2" in *"$1"*) return 0 ;; *) return 1 ;; esac; }
has_esc()     { case "$1" in *"$ESC"*) return 0 ;; *) return 1 ;; esac; }

tmplog="$(mktemp)"
trap 'rm -f "$tmplog"' EXIT

echo "== varambu_output.sh contract =="

# 1. Default (non-verbose, non-TTY): phase lines present, plain, no ANSI.
out="$(emit 0 /dev/null 'vb_phase "Preflight"; vb_phase_ok')"
contains '▶ Preflight' "$out" && contains '✓ Preflight' "$out" \
  && ok "default phase shows ▶ then ✓" || bad "default phase markers missing: [$out]"
has_esc "$out" && bad "default phase output leaked ANSI escapes" || ok "default phase output has no ANSI (non-TTY)"

# 2. Default: vb_detail is hidden from stdout.
out="$(emit 0 /dev/null 'vb_detail "repo_root=/x"; vb_detail "ready: spiffe-tool-b"')"
[ -z "$out" ] && ok "default hides detail/key=value/ready: from stdout" || bad "default leaked detail to stdout: [$out]"

# 3. Verbose: vb_detail is shown on stdout.
out="$(emit 1 /dev/null 'vb_detail "repo_root=/x"; vb_detail "svid_ready: spiffe-jira-mcp-envoy"')"
contains 'repo_root=/x' "$out" && contains 'svid_ready: spiffe-jira-mcp-envoy' "$out" \
  && ok "--verbose shows detail/ready: on stdout" || bad "--verbose did not show detail: [$out]"

# 4. Banner.
out="$(emit 0 /dev/null 'vb_banner')"
contains 'VARAMBU STARTED' "$out" && ! has_esc "$out" \
  && ok "banner prints plain VARAMBU STARTED (non-TTY)" || bad "banner wrong: [$out]"

# 5. Identities phase keeps the count suffix.
out="$(emit 0 /dev/null 'vb_phase "Issue workload identities"; vb_phase_ok "(8 SVIDs)"')"
contains '✓ Issue workload identities (8 SVIDs)' "$out" \
  && ok "identities phase keeps (N SVIDs) count" || bad "count missing: [$out]"

# 6. Failure shows ✗ with one-line reason.
out="$(emit 0 /dev/null 'vb_phase "Verify MCP tools"; vb_phase_fail "expected Jira MCP tools not returned"')"
contains '✗ Verify MCP tools — expected Jira MCP tools not returned' "$out" \
  && ok "failed phase shows ✗ with one-line reason" || bad "fail line wrong: [$out]"

# 7. Log file is always full AND plain (no ANSI), regardless of verbose.
: >"$tmplog"
emit 0 "$tmplog" 'vb_detail "k=v"; vb_phase "P"; vb_phase_ok; vb_banner' >/dev/null
logtext="$(cat "$tmplog")"
contains 'k=v' "$logtext" && contains 'VARAMBU_STARTED' "$logtext" \
  && contains 'PHASE P' "$logtext" && contains 'OK P' "$logtext" \
  && ok "log captures detail + markers even when stdout is quiet" || bad "log missing content: [$logtext]"
has_esc "$logtext" && bad "log file leaked ANSI escapes" || ok "log file is plain (no ANSI)"

echo "== summary: passed=$PASS failed=$FAIL =="
[ "$FAIL" -eq 0 ]
