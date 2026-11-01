#!/usr/bin/env python3
"""Check that the CI gates, the CI jobs and the required checks agree (slice ci-evidence-trace, D8).

Three lists must name the same gates:
- the rows of the AGENTS.md "Quality gates" table whose "Enforced by" starts with "CI";
- the jobs of .github/workflows/ci.yml, each of which must run `make <its own name>`;
- the required status checks of the `main` ruleset, read from the public GitHub API without a token
  (or from a JSON file in tests). A ruleset that cannot be read or parsed fails the check.

The ruleset must also be active and require at least one approving review (slice agent-identity):
agents work as the bot account, which cannot approve its own pull requests.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

TABLE_HEADING = "## Quality gates"
MAKE_TARGET_RE = re.compile(r"`make ([A-Za-z0-9_-]+)`")
ENFORCED_BY_CI_RE = re.compile(r"^CI\b")


def ci_gates(agents_text: str) -> list[str]:
    """Make targets of the quality-gates rows enforced by CI."""
    if TABLE_HEADING not in agents_text:
        raise ValueError(f"AGENTS.md has no '{TABLE_HEADING}' section")
    section = agents_text.split(TABLE_HEADING, 1)[1].split("\n## ", 1)[0]
    gates = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not ENFORCED_BY_CI_RE.match(cells[2]):
            continue
        target = MAKE_TARGET_RE.search(cells[1])
        if target:
            gates.append(target.group(1))
    return gates


def workflow_jobs(workflow_text: str) -> dict[str, list[str]]:
    """Job name -> the `run` scripts of its steps."""
    data = yaml.safe_load(workflow_text) or {}
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        raise ValueError("workflow has no jobs")
    return {name: [str(step.get("run", "")) for step in (job or {}).get("steps") or [] if isinstance(step, dict)]
            for name, job in jobs.items()}


def runs_own_target(name: str, runs: list[str]) -> bool:
    pattern = re.compile(rf"^\s*make {re.escape(name)}(\s|$)", re.MULTILINE)
    return any(pattern.search(run) for run in runs)


def required_checks(ruleset: object) -> list[str]:
    if not isinstance(ruleset, dict) or not isinstance(ruleset.get("rules"), list):
        raise ValueError("ruleset has no rules list")
    contexts = []
    for rule in ruleset["rules"]:
        if isinstance(rule, dict) and rule.get("type") == "required_status_checks":
            checks = (rule.get("parameters") or {}).get("required_status_checks") or []
            contexts += [str(check.get("context")) for check in checks if isinstance(check, dict)]
    return contexts


def required_approvals(ruleset: dict) -> int:
    """Highest required_approving_review_count of the ruleset's pull_request rules; 0 if none."""
    counts = [0]
    for rule in ruleset["rules"]:
        if isinstance(rule, dict) and rule.get("type") == "pull_request":
            count = (rule.get("parameters") or {}).get("required_approving_review_count")
            counts.append(count if isinstance(count, int) and not isinstance(count, bool) else 0)
    return max(counts)


def load_ruleset(url: str | None, path: str | None) -> object:
    try:
        if path:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        if not url:
            raise ValueError("no ruleset given (--ruleset-url or --ruleset-json)")
        request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310 - fixed https API URL
            return json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read the ruleset: {exc}") from exc


def check(agents_text: str, workflow_text: str, ruleset: object) -> list[str]:
    gates = set(ci_gates(agents_text))
    jobs = workflow_jobs(workflow_text)
    required = set(required_checks(ruleset))
    problems = [f"gate {g} is enforced by CI in AGENTS.md but has no CI job" for g in sorted(gates - set(jobs))]
    problems += [f"CI job {j} has no row enforced by CI in the AGENTS.md quality gates" for j in sorted(set(jobs) - gates)]
    problems += [f"CI job {j} does not run `make {j}`" for j in sorted(jobs) if not runs_own_target(j, jobs[j])]
    problems += [f"CI job {j} is not a required check of the main ruleset" for j in sorted(set(jobs) - required)]
    problems += [f"required check {c} is not a CI job" for c in sorted(required - set(jobs))]
    if ruleset.get("enforcement") != "active":
        problems.append(f"the main ruleset is not active (enforcement: {ruleset.get('enforcement')})")
    if required_approvals(ruleset) < 1:
        problems.append("the main ruleset does not require an approving review")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--agents", default="AGENTS.md")
    parser.add_argument("--workflow", default=".github/workflows/ci.yml")
    parser.add_argument("--ruleset-url")
    parser.add_argument("--ruleset-json", help="a saved copy of the ruleset API response (tests)")
    args = parser.parse_args()
    try:
        problems = check(Path(args.agents).read_text(encoding="utf-8"),
                         Path(args.workflow).read_text(encoding="utf-8"),
                         load_ruleset(args.ruleset_url, args.ruleset_json))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"[gate-consistency] FAILED: {exc}", file=sys.stderr)
        return 2
    if problems:
        print("[gate-consistency] FAILED", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("[gate-consistency] PASSED (AGENTS.md CI gates, CI jobs and required checks agree; the ruleset is active and requires an approving review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
