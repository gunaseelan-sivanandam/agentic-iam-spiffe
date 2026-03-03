#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${1:-origin/main}"
MIN_DIFF_COVERAGE="${2:-90}"

if [ ! -f coverage.xml ]; then
  echo "[diff-coverage] coverage.xml not found. Run unit-cov first." >&2
  exit 2
fi

echo "[diff-coverage] compare branch: ${BASE_REF}"
echo "[diff-coverage] threshold: ${MIN_DIFF_COVERAGE}%"

diff-cover coverage.xml \
  --compare-branch "${BASE_REF}" \
  --fail-under "${MIN_DIFF_COVERAGE}" \
  --include "services/capability-issuer/*.py" \
  --include "services/tool-b/*.py" | tee diff-coverage.txt
