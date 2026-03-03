#!/usr/bin/env python3
"""Validate mutation-testing score from mutmut CI/CD stats."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats", default="mutants/mutmut-cicd-stats.json")
    parser.add_argument("--min-score", type=float, default=70.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stats_path = Path(args.stats)
    if not stats_path.exists():
        print(f"[mutation-gate] missing stats file: {stats_path}", file=sys.stderr)
        return 2

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    total = int(stats.get("total", 0))
    killed = int(stats.get("killed", 0))
    skipped = int(stats.get("skipped", 0))
    no_tests = int(stats.get("no_tests", 0))

    denominator = total - skipped - no_tests
    if denominator <= 0:
        print(
            "[mutation-gate] invalid denominator for mutation score "
            f"(total={total}, skipped={skipped}, no_tests={no_tests})",
            file=sys.stderr,
        )
        return 2

    score = (killed / denominator) * 100.0
    if score < args.min_score:
        print(
            "[mutation-gate] FAILED "
            f"(score={score:.2f}% < required={args.min_score:.2f}%)",
            file=sys.stderr,
        )
        print(
            f"[mutation-gate] details: killed={killed}, total={total}, "
            f"skipped={skipped}, no_tests={no_tests}",
            file=sys.stderr,
        )
        return 1

    print(
        "[mutation-gate] PASSED "
        f"(score={score:.2f}%, required={args.min_score:.2f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
