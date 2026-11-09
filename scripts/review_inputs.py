"""Review inputs computed by tools (agentic-sdlc-poc slice 4.2, S42-D1 to S42-D9), used by the review launcher.

Three things the author no longer chooses or summarises:
- the files under review, taken from the diff between the merge-base and the reviewed commit (deleted files
  in their own list), with `--path` only ordering them;
- the upstream items the change traces to: the governing plan and its decisions, the plans of other bundles
  it touches, and the requirement, architecture and test items the trace model links to it;
- the evidence, computed in a scratch clone of the reviewed commit with a minimal environment: the changed
  script lines the tooling tests do not run, the trace gaps among the upstream items, and the CI results of the
  reviewed commit read from the public API without a token. A command that cannot run is shown as failed.

Every evidence entry is numbered (EV1, EV2, ...) so the reviewer can account for each one.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import site
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

COVERAGE_COMMAND = ("python3 -m pytest -q -p no:cacheprovider tests/tools --cov=scripts --cov-branch "
                    "--cov-report=json:<scratch>/coverage.json")
TRACE_COMMAND = ("python3 scripts/validate_traceability.py --mode pr --base <merge-base> "
                 "--report-json <scratch>/trace.json --design-report-json <scratch>/design.json")
CI_COMMAND = "GET https://api.github.com/repos/<owner>/<repo>/actions/runs?head_sha=<commit> (no token)"
SUBPROCESS_NOTE = ("A script the tooling tests run only as a subprocess shows as not run here, because coverage is "
                   "measured in-process (issue #44).")
GATED_SERVICES = {"services/capability-issuer/": "make unit-trust and make unit-diff-cov",
                  "services/tool-b/": "make unit-trust and make unit-diff-cov"}
UPSTREAM_QUESTION = ("Does any problem you find originate upstream (a requirement, the architecture, the plan)? If so, "
                     "name the document and section.")
DECISION_ROW = re.compile(r"^\|\s*((?:[A-Z][A-Z0-9]*-)?D\d+)\s*\|")
REQ_HEADING = re.compile(r"^#{2,3}\s+(REQ-[A-Z0-9.-]+)\s+—")
ARCH_HEADING = re.compile(r"^##\s+(ARCH-\d{3})\b")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
GITHUB_REMOTE = re.compile(r"github\.com[:/]([\w.-]+)/([\w.-]+?)(?:\.git)?$")
TIMEOUT_S = 600


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)  # noqa: S603, S607 - fixed argv, no shell
    if result.returncode != 0:
        raise ValueError(f"git {args[0]} failed: {result.stderr.strip()[:200]}")
    return result.stdout


def _show(repo: Path, commit: str, path: str) -> str | None:
    result = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, text=True,  # noqa: S603, S607 - fixed argv, no shell
                            check=False)
    return result.stdout if result.returncode == 0 else None


# --- Files under review (S42-D1) ---------------------------------------------------------------


@dataclass(frozen=True)
class ChangedFiles:
    """The change's files: those to open (added, modified, new names of renames) and those it deletes."""

    to_open: tuple[str, ...]
    deleted: tuple[str, ...]


def changed_files(repo: Path, merge_base: str, commit: str, withheld: list[str]) -> ChangedFiles:
    to_open, deleted = [], []
    for line in _git(repo, "diff", "--name-status", "-M", merge_base, commit).splitlines():
        fields = line.split("\t")
        status, paths = fields[0], fields[1:]
        if status.startswith("R"):
            deleted.append(paths[0])  # the old name of a rename
            to_open.append(paths[1])
        elif status == "D":
            deleted.append(paths[0])
        else:
            to_open.append(paths[-1])
    return ChangedFiles(tuple(sorted(p for p in to_open if p not in withheld)),
                        tuple(sorted(p for p in deleted if p not in withheld)))


def order_files(changed: ChangedFiles, hints: list[str]) -> list[str]:
    """The files to open, the `--path` hints first; a hint outside the files to open is refused."""
    for hint in hints:
        if hint in changed.deleted:
            raise ValueError(f"--path names a file the change deletes; it is listed under deleted files: {hint}")
        if hint not in changed.to_open:
            raise ValueError(f"--path is not a file the change adds, modifies or renames: {hint}")
    return list(dict.fromkeys(hints)) + [p for p in changed.to_open if p not in hints]


# --- Upstream items (S42-D3) -------------------------------------------------------------------


def decision_ids(plan_text: str) -> list[str]:
    """The decision IDs of a plan: the first cell of each decisions-table row, such as S41-D1 or POC-D9."""
    return list(dict.fromkeys(m.group(1) for line in plan_text.splitlines() if (m := DECISION_ROW.match(line))))


def _plan_line(repo: Path, commit: str, bundle: str, found: str) -> str:
    plan = f"{bundle}/plan.md"
    text = _show(repo, commit, plan)
    if text is None:
        return f"- {plan}: not at this commit ({found})"
    ids = decision_ids(text)
    return f"- {plan} ({found}); decisions: {', '.join(ids) if ids else 'none found'}"


def plan_lines(repo: Path, commit: str, record: str, changed: list[str]) -> list[str]:
    """(a) the governing plan, the bundle of the review record; (b) the plans of other bundles the change touches."""
    own = str(Path(record).parent) if record else ""
    lines = ([_plan_line(repo, commit, own, "the governing plan: the bundle of the review record")] if own else
             ["- Governing plan: none (this review has no review record; a benchmark case has none)"])
    touched: dict[str, str] = {}
    for path in changed:
        parts = Path(path).parts
        bundle_name = parts[2] if len(parts) >= 4 else ""
        if (parts[:2] == ("docs", "slices") and bundle_name and not bundle_name.startswith("_")
                and bundle_name != "archive" and str(Path(*parts[:3])) != own):
            touched.setdefault(str(Path(*parts[:3])), path)
    lines += [_plan_line(repo, commit, bundle, f"the change touches {first}") for bundle, first in sorted(touched.items())]
    return lines


def _sections(text: str | None, heading: re.Pattern[str]) -> dict[str, str]:
    """Each section of a document by the ID in its heading, up to the next heading of that pattern."""
    sections: dict[str, list[str]] = {}
    current = None
    for line in (text or "").splitlines():
        match = heading.match(line)
        if match:
            current = match.group(1)
            sections[current] = []
        if current is not None:
            sections[current].append(line)
    return {key: "\n".join(lines) for key, lines in sections.items()}


def changed_sections(repo: Path, merge_base: str, commit: str, path: str, heading: re.Pattern[str]) -> list[str]:
    """(d) the IDs whose section the change adds, removes or edits."""
    before, after = _sections(_show(repo, merge_base, path), heading), _sections(_show(repo, commit, path), heading)
    return sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))


def _test_entries(text: str | None) -> dict[str, dict[str, Any]]:
    """The entries of a `trace/tests.yaml` text by ID; raises ValueError when it is not a YAML mapping."""
    try:
        data = yaml.safe_load(text or "") or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"not valid YAML ({type(exc).__name__})") from None
    if not isinstance(data, dict):
        raise ValueError("not a YAML mapping")
    return {str(t.get("id")): t for t in data.get("tests") or [] if isinstance(t, dict)}


def changed_tests(repo: Path, merge_base: str, commit: str) -> dict[str, list[str]]:
    """(d) the test IDs whose `trace/tests.yaml` entry the change adds, removes or edits, with their requirements;
    raises ValueError when the file cannot be read at either commit."""
    before = _test_entries(_show(repo, merge_base, "trace/tests.yaml"))
    after = _test_entries(_show(repo, commit, "trace/tests.yaml"))
    return {key: sorted((after.get(key) or before.get(key) or {}).get("source_requirements") or [])
            for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)}


def trace_links(report: dict[str, Any], changed: list[str]) -> tuple[list[str], set[str]]:
    """(c) the architecture and requirement items the trace model links to changed files, and their IDs."""
    lines, ids = [], set()
    architecture = report.get("architecture", {})
    for arch_id, arch in sorted(architecture.items()):
        files = [f for f in arch.get("implemented_by", []) if f in changed]
        if files:
            ids |= {arch_id, *arch.get("satisfies", [])}
            lines.append(f"- {arch_id} (found: its `Implemented by:` line names {', '.join(files)}); satisfies "
                         f"{', '.join(arch.get('satisfies', [])) or 'none'}")
    for dd_id, design in sorted(report.get("design", {}).items()):
        where = [loc for loc in design.get("locations", []) if loc.rsplit(":", 1)[0] in changed]
        if where:
            archs = design.get("implements_architecture", [])
            reqs = sorted({r for a in archs for r in architecture.get(a, {}).get("satisfies", [])})
            ids |= {dd_id, *archs, *reqs}
            lines.append(f"- {dd_id} (found: its DD tag at {', '.join(where)}) implements {', '.join(archs)}; "
                         f"satisfies {', '.join(reqs) or 'none'}")
    return lines, ids


@dataclass(frozen=True)
class Upstream:
    """The upstream section's text and the IDs it names (for the trace gaps among them)."""

    text: str
    ids: frozenset[str] = frozenset()


def upstream_items(repo: Path, commits: tuple[str, str], record: str, changed: list[str],
                   report: dict[str, Any] | None) -> Upstream:
    """S42-D3: the upstream section; `commits` is the merge-base and the reviewed commit."""
    merge_base, commit = commits
    lines = ["Plans:", *plan_lines(repo, commit, record, changed), ""]
    ids: set[str] = set()
    if report is None:
        lines += ["Trace links: not available (the trace model could not be read at this commit; see the evidence)."]
    else:
        links, linked = trace_links(report, changed)
        ids |= linked
        lines += ["Trace links of changed files:", *(links or ["- none"]), ""]
    reqs = changed_sections(repo, merge_base, commit, "docs/requirements.md", REQ_HEADING)
    archs = changed_sections(repo, merge_base, commit, "docs/architecture.md", ARCH_HEADING)
    try:
        tests = changed_tests(repo, merge_base, commit)
        test_lines = [f"- {t}; proves {', '.join(rs) or 'no requirement'}" for t, rs in tests.items()] or ["- none"]
    except ValueError as unreadable:
        tests, test_lines = {}, [f"- not available: trace/tests.yaml is {unreadable} at one of the commits"]
    ids |= set(reqs) | set(archs) | set(tests) | {r for rs in tests.values() for r in rs}
    lines += ["Requirement and architecture sections the change edits:",
              *([f"- {i} (found: the change edits its section in docs/requirements.md)" for i in reqs]
                + [f"- {i} (found: the change edits its section in docs/architecture.md)" for i in archs] or ["- none"]),
              "", "Test entries the change edits in trace/tests.yaml:", *test_lines,
              "", UPSTREAM_QUESTION]
    return Upstream("\n".join(lines), frozenset(ids))


# --- Evidence (S42-D5 to S42-D8) ---------------------------------------------------------------


@dataclass
class Evidence:
    """Numbered entries with the command that produced each; a status per item (coverage, trace, ci)."""

    entries: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    status: dict[str, str] = field(default_factory=dict)

    def add(self, text: str) -> None:
        self.entries.append(f"EV{len(self.entries) + 1}: {text}")  # EV, so no finding ID like E1 collides

    @property
    def items(self) -> list[str]:
        return [entry.split(":", 1)[0] for entry in self.entries]

    def text(self) -> str:
        body = self.entries or ["No entries: nothing to account for."]
        return "\n".join(["Each numbered entry must be listed under `accounted`.", "", *body, "", *self.notes]).rstrip()


@dataclass(frozen=True)
class Scratch:
    """Where evidence is computed: a clone of the reviewed commit and a HOME of its own, both temporary."""

    root: Path
    clone: Path
    home: Path


def make_scratch(repo: Path, commit: str) -> Scratch:
    """A clone of the commit and a HOME of its own in a new temporary directory, removed again if either fails."""
    root = Path(tempfile.mkdtemp(prefix="review-evidence-"))
    clone, home = root / "clone", root / "home"
    try:
        home.mkdir()
        _git(repo, "clone", "-q", "--shared", "--no-checkout", str(repo), str(clone))
        _git(clone, "checkout", "-q", "--detach", commit)
        _link_user_site(home)
    except (ValueError, OSError):
        shutil.rmtree(root, ignore_errors=True)
        raise
    return Scratch(root, clone, home)


def _link_user_site(home: Path) -> None:
    """Let the interpreter see its `pip --user` packages under the scratch HOME: only the user site-packages
    directory is linked, at the place the interpreter computes from HOME, not the rest of the author's ~/.local."""
    user_site, user_base = Path(site.getusersitepackages()), Path(site.getuserbase())
    if not user_site.is_dir():
        return
    target = home / user_base_under_home(user_base) / user_site.relative_to(user_base)
    target.parent.mkdir(parents=True)
    target.symlink_to(user_site)


def user_base_under_home(user_base: Path) -> Path:
    """Where the interpreter puts its user base relative to HOME: `.local` on Linux, `Library/Python/X.Y` for a macOS
    framework build; `.local` when the base does not lie under the current HOME."""
    try:
        return user_base.relative_to(Path(os.path.expanduser("~")))
    except ValueError:
        return Path(".local")


def evidence_env(scratch: Scratch) -> dict[str, str]:
    """S42-D8: only PATH, LANG and the scratch HOME."""
    return {"PATH": os.environ.get("PATH", ""), "LANG": os.environ.get("LANG", "C.UTF-8"), "HOME": str(scratch.home)}


def _run(argv: list[str], scratch: Scratch) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=scratch.clone, env=evidence_env(scratch), capture_output=True, text=True,  # noqa: S603 - fixed argv, no shell
                          timeout=TIMEOUT_S, check=False)


def changed_lines(repo: Path, merge_base: str, commit: str, path: str) -> set[int]:
    """The lines of `path` at the commit that the change adds or edits."""
    lines: set[int] = set()
    for line in _git(repo, "diff", "-U0", merge_base, commit, "--", path).splitlines():
        match = HUNK.match(line)
        if match:
            start, count = int(match.group(1)), int(match.group(2) if match.group(2) is not None else 1)
            lines.update(range(start, start + count))
    return lines


def _ranges(numbers: list[int]) -> str:
    out, start, prev = [], None, None
    for n in sorted(numbers):
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append(f"{start}-{prev}" if start != prev else str(start))
            start = prev = n
    if start is not None:
        out.append(f"{start}-{prev}" if start != prev else str(start))
    return ", ".join(out)


def coverage_evidence(evidence: Evidence, repo: Path, commits: tuple[str, str], changed: list[str],
                      scratch: Scratch) -> None:
    """(a) changed script lines and branches the tooling tests did not run; a gate line per changed service file."""
    merge_base, commit = commits
    scripts = [p for p in changed if p.startswith("scripts/") and p.endswith(".py")]
    for path in (p for p in changed if p.startswith("services/") and p.endswith(".py")):
        gate = next((g for prefix, g in GATED_SERVICES.items() if path.startswith(prefix)), None)
        evidence.add(f"{path}: covered by the gate {gate}" if gate else f"{path}: no coverage gate")
    if not scripts:
        evidence.status["coverage"] = "ok"
        return
    report_file = scratch.root / "coverage.json"
    argv = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/tools", "--cov=scripts",
            "--cov-branch", f"--cov-report=json:{report_file}"]
    try:
        run = _run(argv, scratch)
    except (OSError, subprocess.TimeoutExpired) as exc:
        evidence.add(f"failed: {COVERAGE_COMMAND}: {type(exc).__name__}")
        evidence.status["coverage"] = "failed"
        return
    failing = re.findall(r"^(?:FAILED|ERROR) (\S+)", run.stdout, re.MULTILINE)
    if failing:
        evidence.add(f"tests failing at this commit ({COVERAGE_COMMAND}): {', '.join(failing[:20])}"
                     + (f" and {len(failing) - 20} more" if len(failing) > 20 else ""))
    if not report_file.is_file():
        tail = (run.stdout.strip().splitlines() or run.stderr.strip().splitlines() or ["no output"])[-1]
        evidence.add(f"failed: {COVERAGE_COMMAND}: exit {run.returncode}, no coverage report: {tail[:200]}")
        evidence.status["coverage"] = "failed"
        return
    files = json.loads(report_file.read_text(encoding="utf-8")).get("files", {})
    covered = []
    for path in scripts:
        lines = changed_lines(repo, merge_base, commit, path)
        data = files.get(path)
        missing = sorted(lines & set(data["missing_lines"])) if data else sorted(lines)
        branches = [f"{a}->{b if b > 0 else 'exit'}" for a, b in (data or {}).get("missing_branches", []) if a in lines]
        if missing or branches:
            evidence.add(f"{path}: changed lines not run: {_ranges(missing) or 'none'}; branches not taken: "
                         f"{', '.join(branches) or 'none'} ({COVERAGE_COMMAND})")
        else:
            covered.append(path)
    if covered:
        evidence.notes.append(f"Every changed line and branch run by the tooling tests: {', '.join(covered)}.")
    evidence.notes.append(SUBPROCESS_NOTE)
    evidence.status["coverage"] = "failed" if failing else "ok"


def trace_report(scratch: Scratch, merge_base: str) -> tuple[dict[str, Any] | None, str]:
    """The trace model at the reviewed commit, compared with the merge-base; None and the reason when it fails."""
    if not (scratch.clone / "scripts" / "validate_traceability.py").is_file():
        return None, "scripts/validate_traceability.py does not exist at this commit"
    report = scratch.root / "trace.json"
    argv = [sys.executable, "scripts/validate_traceability.py", "--mode", "pr", "--base", merge_base,
            "--report-json", str(report), "--design-report-json", str(scratch.root / "design.json")]
    try:
        run = _run(argv, scratch)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, type(exc).__name__
    if run.returncode not in (0, 1) or not report.is_file():
        return None, f"exit {run.returncode}: {(run.stderr.strip().splitlines() or ['no output'])[-1][:200]}"
    return json.loads(report.read_text(encoding="utf-8")), ""


def trace_evidence(evidence: Evidence, report: dict[str, Any] | None, reason: str, ids: frozenset[str]) -> None:
    """(b) the trace gaps among the upstream items, each marked new, existing or accepted."""
    if report is None:
        evidence.add(f"failed: {TRACE_COMMAND}: {reason}")
        evidence.status["trace"] = "failed"
        return
    gate = report.get("gap_gate", {})
    new, accepted = set(gate.get("new_gaps", [])), set(gate.get("accepted", []))
    gaps = [f"{category}:{item}" for category, items in sorted(report.get("coverage_gaps", {}).items())
            for item in items if item in ids]
    for gap in gaps:
        mark = "accepted" if gap in accepted else "new" if gap in new else "existing"
        evidence.add(f"trace gap {gap} ({mark}, against the merge-base; {TRACE_COMMAND})")
    if not gaps:
        evidence.notes.append(f"No trace gap among the upstream items ({TRACE_COMMAND}).")
    evidence.status["trace"] = "ok"


Fetch = Callable[[str], Any]


def fetch_json(url: str) -> Any:
    """GET a public GitHub API URL without a token."""
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",  # noqa: S310 - fixed https URL
                                                   "User-Agent": "review-launcher"})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - fixed https URL
        return json.loads(response.read().decode("utf-8"))


def github_repo(repo: Path) -> tuple[str, str] | None:
    try:
        match = GITHUB_REMOTE.search(_git(repo, "remote", "get-url", "origin").strip())
    except ValueError:
        return None
    return (match.group(1), match.group(2)) if match else None


def ci_evidence(evidence: Evidence, repo: Path, commit: str, fetch: Fetch) -> None:
    """(c) every job of the workflow runs whose head is the reviewed commit, with its status and conclusion."""
    owner_repo = github_repo(repo)
    if owner_repo is None:
        evidence.add(f"failed: {CI_COMMAND}: the origin remote is not a GitHub repository")
        evidence.status["ci"] = "failed"
        return
    base = f"https://api.github.com/repos/{owner_repo[0]}/{owner_repo[1]}/actions/runs"
    try:
        runs = [r for r in fetch(f"{base}?head_sha={commit}&per_page=50").get("workflow_runs", [])
                if r.get("head_sha") == commit]
        jobs = {r["id"]: fetch(f"{base}/{r['id']}/jobs?per_page=100").get("jobs", []) for r in runs}
    except (OSError, ValueError, KeyError, AttributeError, urllib.error.URLError) as exc:
        evidence.add(f"failed: {CI_COMMAND}: {type(exc).__name__}")
        evidence.status["ci"] = "failed"
        return
    if not runs:
        evidence.add(f"no CI run for this commit ({CI_COMMAND})")
    for run in runs:
        listed = "; ".join(f"{j.get('name')}: {j.get('status')}"
                           + (f"/{j.get('conclusion')}" if j.get("status") == "completed" else "")
                           for j in jobs[run["id"]]) or "no jobs listed"
        evidence.add(f"CI run {run.get('name')} {run['id']} ({run.get('event')}): {run.get('status')}"
                     + (f"/{run.get('conclusion')}" if run.get("status") == "completed" else "") + f"; jobs: {listed}")
    evidence.status["ci"] = "ok"


def sanitise(text: str, scratch: Scratch) -> str:
    """S42-D8: paths relative to the clone; the scratch and the author's HOME as <home>; the interpreter as <python>."""
    text = text.replace(str(scratch.clone) + os.sep, "").replace(str(scratch.clone), ".")
    for home in (str(scratch.home), os.path.expanduser("~")):
        text = text.replace(home, "<home>")
    for prefix in {sys.prefix, sys.base_prefix, sys.exec_prefix}:
        text = text.replace(os.path.join(prefix, "lib", "python"), "<python>/lib/python")
    return text


def leaked_paths(text: str, scratch: Scratch) -> list[str]:
    """What must never reach a prompt: the author's HOME path or the scratch root."""
    home = os.path.expanduser("~")
    return [name for name, needle in (("the author's HOME path", home), ("the scratch root", str(scratch.root)))
            if needle and needle != os.sep and needle in text]
