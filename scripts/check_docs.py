#!/usr/bin/env python3
"""Check that the live documentation set is complete and internally consistent.

Checks (see docs/slices/docs-consolidation/test_plan.md):
- spec:   every E2E test ID in the harness has a heading in docs/test_spec.md, and no heading
          names a test the harness does not run
- links:  every relative Markdown link in a live document resolves, including #anchors
- images: every image in docs/ is referenced by a live document; every .puml has its .svg
- slices: every slice bundle directory has a row in docs/slices/README.md
- ids:    every test ID in a documented TEST_ONLY= example exists in the harness
"""

from __future__ import annotations

import argparse
import re
import subprocess  # nosec B404 - fixed git argv, no shell
import sys
import unicodedata
from pathlib import Path

HARNESS_ID_RE = re.compile(r'^\s*begin_test_evidence\s+"([^"]+)"', re.MULTILINE)
SPEC_HEADING_RE = re.compile(r"^### (M[0-9A-Za-z.]+-T\d+) — ", re.MULTILINE)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
TEST_ONLY_RE = re.compile(r"TEST_ONLY=([A-Za-z0-9.,-]+)")
IMAGE_SUFFIXES = {".svg", ".png"}
LIVE_DOC_GLOBS = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "tests/unit/AGENTS.md",
    "docs/*.md",
    "docs/slices/README.md",
    "docs/slices/_template/*.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--harness", default="scripts/rogue_node_tests.sh")
    parser.add_argument("--spec", default="docs/test_spec.md")
    return parser.parse_args()


def live_docs(root: Path) -> list[Path]:
    found: set[Path] = set()
    for pattern in LIVE_DOC_GLOBS:
        found.update(p for p in root.glob(pattern) if p.is_file())
    return sorted(found)


def harness_ids(harness_text: str) -> list[str]:
    return HARNESS_ID_RE.findall(harness_text)


def check_spec(harness_text: str, spec_text: str) -> list[str]:
    run = harness_ids(harness_text)
    documented = SPEC_HEADING_RE.findall(spec_text)
    problems = [f"spec: harness test {t} has no heading in the test spec" for t in run if t not in documented]
    problems += [f"spec: heading {t} names a test the harness does not run" for t in documented if t not in run]
    seen: set[str] = set()
    for test_id in documented:
        if test_id in seen:
            problems.append(f"spec: duplicate heading for {test_id}")
        seen.add(test_id)
    return problems


def heading_anchors(markdown: str) -> set[str]:
    """GitHub-style anchors for every heading, including -1, -2 suffixes for repeats."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in markdown.splitlines():
        m = HEADING_RE.match(line)
        if not m:
            continue
        slug = _slug(m.group(1))
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        anchors.add(slug if n == 0 else f"{slug}-{n}")
    return anchors


def _slug(heading: str) -> str:
    text = re.sub(r"`|\*\*|__", "", heading).strip().lower()
    kept = [c for c in text if c in " -_" or unicodedata.category(c)[0] in "LN"]
    return "".join(kept).replace(" ", "-")


def check_links(root: Path, doc: Path) -> list[str]:
    problems: list[str] = []
    text = doc.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target):
            continue
        problem = _link_problem(doc, text, target)
        if problem:
            problems.append(f"links: {doc.relative_to(root)}: {problem}")
    return problems


def _link_problem(doc: Path, doc_text: str, target: str) -> str | None:
    path_part, _, anchor = target.partition("#")
    dest = (doc.parent / path_part).resolve() if path_part else doc
    if not dest.exists():
        return f"missing target {target}"
    if not anchor or dest.is_dir() or dest.suffix != ".md":
        return None
    dest_text = doc_text if dest == doc else dest.read_text(encoding="utf-8")
    if anchor not in heading_anchors(dest_text):
        return f"missing anchor {target}"
    return None


def tracked_files(root: Path, subdir: str) -> list[Path]:
    """Files git tracks directly in `subdir`, so local untracked renders do not count."""
    out = subprocess.run(  # nosec B603 B607 - fixed argv
        ["git", "-C", str(root), "ls-files", "--", subdir],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    base = (root / subdir).resolve()
    return sorted(p for p in (root / line for line in out.splitlines()) if p.resolve().parent == base)


def check_images(root: Path, docs: list[Path]) -> list[str]:
    tracked = tracked_files(root, "docs")
    referenced: set[Path] = set()
    for doc in docs:
        for target in LINK_RE.findall(doc.read_text(encoding="utf-8")):
            referenced.add((doc.parent / target.partition("#")[0]).resolve())
    problems = [
        f"images: {img.relative_to(root)} is not referenced by any live document"
        for img in tracked
        if img.suffix in IMAGE_SUFFIXES and img.resolve() not in referenced
    ]
    problems += [
        f"images: {src.relative_to(root)} has no rendered {src.stem}.svg"
        for src in tracked
        if src.suffix == ".puml" and src.with_suffix(".svg") not in tracked
    ]
    return problems


def check_slice_index(root: Path) -> list[str]:
    slices = root / "docs" / "slices"
    index_text = (slices / "README.md").read_text(encoding="utf-8")
    bundles = [p.name for p in slices.iterdir() if p.is_dir() and p.name not in {"_template", "archive"}]
    archive = slices / "archive"
    if archive.is_dir():
        bundles += [p.name for p in archive.iterdir() if p.is_dir()]
    return [f"slices: {name} has no row in docs/slices/README.md" for name in sorted(bundles) if f"[{name}]" not in index_text]


def check_test_only_ids(root: Path, docs: list[Path], known: set[str]) -> list[str]:
    problems: list[str] = []
    for doc in docs:
        for group in TEST_ONLY_RE.findall(doc.read_text(encoding="utf-8")):
            problems += [
                f"ids: {doc.relative_to(root)}: TEST_ONLY example names unknown test {test_id}"
                for test_id in group.split(",")
                if test_id and test_id not in known
            ]
    return problems


def run_checks(root: Path, harness: Path, spec: Path) -> list[str]:
    harness_text = harness.read_text(encoding="utf-8")
    docs = live_docs(root)
    problems = check_spec(harness_text, spec.read_text(encoding="utf-8"))
    for doc in docs:
        problems += check_links(root, doc)
    problems += check_images(root, docs)
    problems += check_slice_index(root)
    problems += check_test_only_ids(root, docs, set(harness_ids(harness_text)))
    return problems


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    problems = run_checks(root, root / args.harness, root / args.spec)
    if problems:
        print("[docs-check] FAILED", file=sys.stderr)
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print(f"[docs-check] PASSED (live documents={len(live_docs(root))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
