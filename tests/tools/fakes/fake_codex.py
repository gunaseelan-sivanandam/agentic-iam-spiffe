#!/usr/bin/env python3
"""Fake `codex` CLI for the review launcher's tooling tests: records that it was called, so a test can
show the launcher never starts Codex (POC-D2)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    Path(os.environ["HOME"], "codex_called").write_text(" ".join(sys.argv[1:]), encoding="utf-8")
    sys.exit(0)
