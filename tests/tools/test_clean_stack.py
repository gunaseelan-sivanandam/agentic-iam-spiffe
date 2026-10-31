"""Tests for scripts/clean_stack.sh emptying capiss_keys/ (slice ci-evidence-trace, test plan V13).

The script runs against a copy of the repository layout with a stub `docker` on PATH, so no real
container is touched.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# The stub logs each call. For `docker run -v <host>:/capiss_keys <image> <cmd...>` it runs the
# script's own command on the host with /capiss_keys replaced by <host>, so an ineffective command
# fails the test; STUB_FAIL_KEYS makes it fail. Every other call succeeds and `docker ps` lists no
# containers.
STUB = """#!/usr/bin/env bash
echo "$*" >> "$STUB_LOG"
if [ "$1" = "run" ]; then
  host=""
  for arg in "$@"; do
    case "$arg" in *:/capiss_keys) host="${arg%:/capiss_keys}" ;; esac
  done
  if [ -n "$host" ]; then
    [ -n "${STUB_FAIL_KEYS:-}" ] && exit 1
    while [ "$#" -gt 0 ] && [ "$1" != "alpine:3.19" ]; do shift; done
    shift
    cmd=()
    for arg in "$@"; do cmd+=("${arg//\/capiss_keys/$host}"); done
    exec "${cmd[@]}"
  fi
fi
exit 0
"""


def _layout(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "compose").mkdir()
    shutil.copy(ROOT / "scripts" / "clean_stack.sh", repo / "scripts" / "clean_stack.sh")
    (repo / "compose" / "spiffe.compose.yml").write_text("services: {}\n")
    keys = repo / "capiss_keys"
    keys.mkdir()
    for name in ("root_key.pem", "root_public_key.b64", "root_key.b64"):
        (keys / name).write_text("synthetic\n")
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    (stub_dir / "docker").write_text(STUB)
    (stub_dir / "docker").chmod(0o755)
    return repo


def _run(repo: Path, tmp_path: Path, *args: str, fail_keys: bool = False) -> subprocess.CompletedProcess:
    env = dict(os.environ, PATH=f"{tmp_path / 'bin'}:{os.environ['PATH']}", STUB_LOG=str(tmp_path / "docker.log"))
    env.pop("COMPOSE_FILE", None)
    if fail_keys:
        env["STUB_FAIL_KEYS"] = "1"
    return subprocess.run(["bash", str(repo / "scripts" / "clean_stack.sh"), *args],
                          env=env, capture_output=True, text=True, check=False)


def test_clean_stack_empties_capiss_keys(tmp_path):
    repo = _layout(tmp_path)
    result = _run(repo, tmp_path)
    assert result.returncode == 0, result.stderr
    assert (repo / "capiss_keys").is_dir()
    assert list((repo / "capiss_keys").iterdir()) == []
    assert "cleaned_capiss_keys=1" in result.stdout


def test_clean_stack_reports_failed_key_removal(tmp_path):
    repo = _layout(tmp_path)
    result = _run(repo, tmp_path, fail_keys=True)
    assert "failed to empty capiss_keys" in result.stdout
    assert "cleaned_capiss_keys=0" in result.stdout
    assert sorted(p.name for p in (repo / "capiss_keys").iterdir()) == ["root_key.b64", "root_key.pem", "root_public_key.b64"]


def test_clean_stack_check_changes_nothing(tmp_path):
    repo = _layout(tmp_path)
    result = _run(repo, tmp_path, "--check")
    assert result.returncode == 0, result.stderr
    assert len(list((repo / "capiss_keys").iterdir())) == 3
    assert not (tmp_path / "docker.log").exists()
