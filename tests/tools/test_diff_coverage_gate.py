"""scripts/diff_coverage_gate.sh must measure both services (DPL-009).

diff-cover keeps only the last of repeated --include options, so the capiss pattern was silently
dropped and capiss changes were never measured. A stub diff-cover records the arguments it gets.
"""

from __future__ import annotations

import os
import subprocess  # nosec B404 - fixed argv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_gate_passes_both_service_patterns_to_one_include(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "diff-cover").write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "$ARGS_LOG"\n')
    (bin_dir / "diff-cover").chmod(0o755)
    work = tmp_path / "work"
    work.mkdir()
    (work / "coverage.xml").write_text("<coverage/>\n")
    log = tmp_path / "args.txt"
    env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}", ARGS_LOG=str(log))
    subprocess.run(["bash", str(ROOT / "scripts" / "diff_coverage_gate.sh"), "origin/main", "90"],
                   cwd=work, env=env, check=True, capture_output=True)
    args = log.read_text().splitlines()
    assert args.count("--include") == 1
    start = args.index("--include") + 1
    assert args[start:start + 2] == ["services/capability-issuer/*.py", "services/tool-b/*.py"]
