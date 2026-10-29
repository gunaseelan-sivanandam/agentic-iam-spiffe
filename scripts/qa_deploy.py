#!/usr/bin/env python3
"""Check the deployed compose against security/invariants.yaml (slice agentic-delivery-process, 1B).

Default deny: every service's image, user, networks, published ports, mounts, secret env var names
and privileges must match its register entry. Every protected asset (REQ-SEC-K*) may reach only its
holders; a violation passes only as an unexpired known violation of an open OPL. Services run as
non-root, except the grandfathered baseline until the grace date. Environment values are never kept.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # nosec B404 - fixed docker argv
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "compose" / "spiffe.compose.yml"
REGISTER_FILE = ROOT / "security" / "invariants.yaml"
REQUIREMENTS_FILE = ROOT / "docs" / "requirements.md"
OPL_FILE = ROOT / "docs" / "open_problem_log.md"

SECRET_ENV_RE = re.compile(r"TOKEN|SECRET|PASSWORD|PASSWD|API_KEY|PRIVATE_KEY|CREDENTIAL")
REQ_SEC_RE = re.compile(r"^## (REQ-SEC-K\d+) — ")
HOLDERS_RE = re.compile(r"Holders:([^\n]*)")
OPL_HEADING_RE = re.compile(r"^## (OPL-\d+):", re.MULTILINE)
OPL_STATUS_RE = re.compile(r"^- Status:\s*(.+)$", re.MULTILINE)
NONROOT_GRACE_END = datetime(2027, 2, 1, tzinfo=timezone.utc)  # grandfathered through 2027-01-31
# The services that existed when the non-root rule was introduced (D7, 2026-10-29); no others may
# be grandfathered.
GRANDFATHERED_BASELINE = frozenset({
    "agent-a", "capability-issuer", "capability-issuer-envoy", "capability-issuer-no-opa",
    "capability-issuer-no-opa-envoy", "codex-jira-mcp-adapter", "jira-mcp-envoy", "jira-mcp-gateway",
    "jira-mcp-mock", "jira-mock", "jira-tool", "jira-tool-envoy", "opa", "redis", "rogue",
    "rogue-socket", "rogue-tests", "spire-agent", "spire-rogue-agent", "spire-server",
    "spire-token-init", "tool-b", "tool-b-envoy",
})
FIELDS = (("image", "image"), ("user", "user"), ("networks", "network"), ("ports", "port"),
          ("mounts", "mount"), ("privileges", "privilege"))


class DeployCheckError(Exception):
    """The deployment could not be read; never treated as an empty inventory."""


@dataclass(frozen=True)
class Service:
    name: str
    image: str
    user: str | None
    networks: tuple[str, ...]
    ports: tuple[str, ...]
    mounts: tuple[str, ...]
    env: tuple[str, ...]  # names only, never values
    privileges: tuple[str, ...]


@dataclass(frozen=True)
class Violation:
    asset: str
    service: str
    via: str


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    known: list[str] = field(default_factory=list)


# --- reading the deployment ---------------------------------------------------


def _run_compose_config(compose_file: Path, project_dir: Path) -> dict:
    argv = ["docker", "compose", "-f", str(compose_file), "--project-directory", str(project_dir),
            "--profile", "*", "config", "--format", "json"]
    try:
        result = subprocess.run(argv, capture_output=True, text=True, check=False)  # nosec B603
    except OSError as exc:
        raise DeployCheckError(f"cannot run docker compose: {exc}") from exc
    if result.returncode != 0:
        raise DeployCheckError(f"docker compose config failed: {result.stderr.strip()[:300]}")
    try:
        config = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise DeployCheckError(f"docker compose config is not JSON: {exc}") from exc
    if not isinstance(config, dict) or not config.get("services"):
        raise DeployCheckError("docker compose config has no services")
    return config


def load_compose_config(compose_file: Path, project_dir: Path) -> dict:
    """Merged config over every profile, as the stack uses it."""
    return _run_compose_config(compose_file, project_dir)


def load_compose_text(text: str, project_dir: Path) -> dict:
    """Same, for a compose file given as text (for example from `git show`)."""
    with tempfile.NamedTemporaryFile("w", suffix=".yml", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        return _run_compose_config(Path(handle.name), project_dir)


def _relative(source: str, root: Path) -> str:
    path = Path(source)
    if not path.is_absolute():
        return source
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return source
    return rel.as_posix() or "."


def _image(spec: dict, root: Path) -> str:
    build = spec.get("build")
    if build:
        return f"build {_relative(build.get('context', '.'), root)} {build.get('dockerfile', 'Dockerfile')}"
    return str(spec.get("image", ""))


def _mounts(spec: dict, root: Path) -> tuple[str, ...]:
    mounts = []
    for volume in spec.get("volumes") or []:
        mode = "ro" if volume.get("read_only") else "rw"
        kind = volume.get("type", "bind")
        source = _relative(volume.get("source", ""), root) if kind == "bind" else f"{kind}:{volume.get('source', '')}"
        mounts.append(f"{source}:{volume.get('target', '')}:{mode}")
    return tuple(mounts)


def _ports(spec: dict) -> tuple[str, ...]:
    return tuple(f"{p.get('published', '')}:{p.get('target', '')}/{p.get('protocol', 'tcp')}"
                 for p in spec.get("ports") or [])


def _device(dev: str | dict) -> str:
    return f"device:{dev if isinstance(dev, str) else dev.get('source', '')}"


def _privileges(spec: dict) -> tuple[str, ...]:
    found = [f"cap_add:{cap}" for cap in spec.get("cap_add") or []]
    found += [_device(dev) for dev in spec.get("devices") or []]
    found += [f"security_opt:{opt}" for opt in spec.get("security_opt") or []]
    found += [f"{key}:host" for key in ("network_mode", "pid", "ipc", "userns_mode") if spec.get(key) == "host"]
    found += ["privileged"] if spec.get("privileged") else []
    return tuple(sorted(found))


def inventory_from_config(config: dict, root: Path) -> dict[str, Service]:
    inventory = {}
    for name, spec in sorted(config["services"].items()):
        inventory[name] = Service(
            name=name,
            image=_image(spec, root),
            user=spec.get("user"),
            networks=tuple(sorted(spec.get("networks") or {})),
            ports=_ports(spec),
            mounts=_mounts(spec, root),
            env=tuple(sorted(spec.get("environment") or {})),
            privileges=_privileges(spec),
        )
    return inventory


def load_register(path: Path) -> dict:
    register = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(register, dict) or "services" not in register or "assets" not in register:
        raise DeployCheckError(f"{path}: register needs 'assets' and 'services'")
    register.setdefault("known_violations", [])
    return register


# --- checks -------------------------------------------------------------------


def check_allowlist(inventory: dict[str, Service], register: dict) -> list[str]:
    """Default deny: every deployed fact must be the registered one."""
    entries = register["services"]
    errors = [f"{name}: service not in the register" for name in inventory if name not in entries]
    errors += [f"{name}: registered service not in compose" for name in entries if name not in inventory]
    for name, service in inventory.items():
        if name in entries:
            errors += _entry_errors(service, entries[name])
    return errors


def _entry_errors(service: Service, entry: dict) -> list[str]:
    errors = []
    for attr, label in FIELDS:
        expected = entry.get(attr)
        actual = getattr(service, attr)
        if isinstance(actual, tuple):
            expected, actual = tuple(sorted(expected or [])), tuple(sorted(actual))
        if expected != actual:
            errors.append(f"{service.name}: {label} {actual!r} is not the registered {expected!r}")
    secret = sorted(e for e in service.env if SECRET_ENV_RE.search(e))
    registered = sorted(entry.get("secret_env") or [])
    if secret != registered:
        errors.append(f"{service.name}: secret env {secret} is not the registered {registered}")
    return errors


def _reaches_path(mount: str, location: str) -> bool:
    source = mount.split(":")[0]
    if source.startswith(("volume:", "tmpfs:")):
        return False
    if source == ".":
        return not location.startswith("/")
    return location == source or location.startswith(source.rstrip("/") + "/")


def _reaches_container_path(mount: str, path: str) -> bool:
    target = mount.split(":")[1]
    return target == path or target.startswith(path + "/") or path.startswith(target.rstrip("/") + "/")


def _reach(service: Service, location: dict) -> str | None:
    if "env" in location:
        return f"env {location['env']}" if location["env"] in service.env else None
    for mount in service.mounts:
        if "path" in location and _reaches_path(mount, location["path"]):
            return f"mount {mount}"
        if "container_path" in location and _reaches_container_path(mount, location["container_path"]):
            return f"mount {mount}"
    return None


def asset_violations(inventory: dict[str, Service], register: dict) -> list[Violation]:
    found: set[Violation] = set()
    for asset, spec in register["assets"].items():
        for location in spec.get("locations") or []:
            holders = set(location.get("holders") or [])
            for name, service in inventory.items():
                via = None if name in holders else _reach(service, location)
                if via:
                    found.add(Violation(asset, name, via))
    unique = {(v.asset, v.service): v for v in sorted(found, key=lambda v: (v.asset, v.service, v.via))}
    return list(unique.values())


def opl_statuses(text: str) -> dict[str, str]:
    statuses = {}
    headings = list(OPL_HEADING_RE.finditer(text))
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        status = OPL_STATUS_RE.search(text, heading.end(), end)
        statuses[heading.group(1)] = status.group(1).strip() if status else "unknown"
    return statuses


def _row_problem(row: dict, opls: dict[str, str], now: datetime) -> str | None:
    if not all(row.get(key) for key in ("opl", "asset", "services", "expires")):
        return "needs opl, asset, services and expires"
    status = opls.get(row["opl"])
    if status is None:
        return f"{row['opl']} is not in the open problem log"
    if not status.startswith("Open"):
        return f"{row['opl']} is {status}; the exception is void"
    expires = row["expires"] if isinstance(row["expires"], date) else date.fromisoformat(str(row["expires"]))
    if now >= datetime.combine(expires + timedelta(days=1), time(), tzinfo=timezone.utc):
        return f"expired on {expires.isoformat()}"
    return None


def check_known_violations(violations: list[Violation], register: dict, opls: dict[str, str],
                           now: datetime) -> Report:
    report = Report()
    rows = {}
    for row in register.get("known_violations") or []:
        problem = _row_problem(row, opls, now)
        if problem:
            report.errors.append(f"known violation {row}: {problem}")
            continue
        for service in row["services"]:
            rows[(row["asset"], service)] = row
    for violation in violations:
        row = rows.pop((violation.asset, violation.service), None)
        if row is None:
            report.errors.append(f"{violation.asset} reaches {violation.service} through {violation.via}: not a holder")
        else:
            report.known.append(f"{row['opl']} {violation.asset} {violation.service} ({violation.via}), "
                                f"expires {row['expires']}")
    report.warnings += [f"known violation {row['opl']} {key[0]} {key[1]} no longer occurs; remove it"
                        for key, row in rows.items()]
    return report


def effective_user(service: Service, image_user: Callable[[str], str | None]) -> str | None:
    """Compose `user`, else the image's USER; None when it cannot be read."""
    if service.user is not None:
        return service.user
    return image_user(service.image)


def _is_root(user: str | None) -> bool:
    if user is None:
        return True
    uid = user.split(":")[0].strip()
    return uid in ("", "0", "root")


def check_nonroot(inventory: dict[str, Service], register: dict,
                  user_of: Callable[[Service], str | None], now: datetime,
                  unknown_is_root: bool = True) -> Report:
    """With unknown_is_root False (images not inspected), a user that cannot be read is skipped."""
    report = Report()
    for name, service in inventory.items():
        policy = (register["services"].get(name) or {}).get("root", "forbidden")
        if policy == "grandfathered" and name not in GRANDFATHERED_BASELINE:
            report.errors.append(f"{name}: only the 2026-10-29 baseline services may be grandfathered as root")
            continue
        user = user_of(service)
        if _is_root(user) and (user is not None or unknown_is_root):
            _report_root(report, name, user, policy == "grandfathered" and now < NONROOT_GRACE_END)
    return report


def _report_root(report: Report, name: str, user: str | None, in_grace: bool) -> None:
    shown = "unknown user" if user is None else f"user {user!r}"
    if in_grace:
        report.warnings.append(f"{name}: runs as root ({shown}); grandfathered until 2027-01-31")
    else:
        report.errors.append(f"{name}: runs as root ({shown}); must be non-root")


def _holder_names(line: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", line))


def _required_holders(requirements_text: str) -> dict[str, set[str]]:
    """REQ-SEC-K* id -> the backticked names on its Holders line."""
    required: dict[str, set[str]] = {}
    current = None
    for line in requirements_text.splitlines():
        heading = REQ_SEC_RE.match(line)
        if heading:
            current = heading.group(1)
            required[current] = set()
        elif line.startswith("#"):
            current = None
        elif current and HOLDERS_RE.search(line):
            required[current] |= _holder_names(HOLDERS_RE.search(line).group(1))
    return required


def check_register_consistency(register: dict, requirements_text: str) -> list[str]:
    """Each REQ-SEC-K* Holders line names exactly the holders the register lists for its asset."""
    required = _required_holders(requirements_text)
    errors = []
    by_requirement = {spec.get("requirement"): (asset, spec) for asset, spec in register["assets"].items()}
    for requirement, holders in sorted(required.items()):
        if requirement not in by_requirement:
            errors.append(f"{requirement}: no asset in the register")
            continue
        asset, spec = by_requirement[requirement]
        listed = set().union(*[set(loc.get("holders") or []) for loc in spec.get("locations") or []])
        if listed != holders:
            errors.append(f"{requirement}: register holders {sorted(listed)} differ from the requirement {sorted(holders)}")
    errors += [f"{requirement}: register asset {asset} has no requirement"
               for requirement, (asset, _spec) in by_requirement.items() if requirement not in required]
    return errors


# --- entry point --------------------------------------------------------------


def docker_image_user(ref: str) -> str | None:
    """USER of a locally present image; None when it is not present or cannot be read."""
    try:
        result = subprocess.run(["docker", "image", "inspect", ref, "--format", "{{.Config.User}}"],  # nosec B603 B607
                                capture_output=True, text=True, check=False)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def run(args: argparse.Namespace) -> Report:
    register = load_register(args.register)
    config = load_compose_config(args.compose, args.compose.parent)
    inventory = inventory_from_config(config, ROOT)
    now = datetime.now(timezone.utc)
    report = Report(errors=check_allowlist(inventory, register))
    report.errors += check_register_consistency(register, REQUIREMENTS_FILE.read_text(encoding="utf-8"))
    known = check_known_violations(asset_violations(inventory, register), register,
                                   opl_statuses(OPL_FILE.read_text(encoding="utf-8")), now)
    report.errors += known.errors
    report.warnings += known.warnings
    report.known += known.known
    project = config.get("name", "compose")

    def user_of(service: Service) -> str | None:
        if args.skip_image_users:
            return service.user
        image = f"{project}-{service.name}" if service.image.startswith("build ") else service.image
        return effective_user(service, lambda _ref: docker_image_user(image))

    if args.skip_image_users:
        report.warnings.append("image USER not inspected (--skip-image-users): only a compose `user` is checked")
    root_report = check_nonroot(inventory, register, user_of, now, unknown_is_root=not args.skip_image_users)
    report.errors += root_report.errors
    report.warnings += root_report.warnings
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose", type=Path, default=COMPOSE_FILE)
    parser.add_argument("--register", type=Path, default=REGISTER_FILE)
    parser.add_argument("--skip-image-users", action="store_true",
                        help="do not inspect images for USER (CI, where images are not built)")
    args = parser.parse_args(argv)
    try:
        report = run(args)
    except (DeployCheckError, OSError, yaml.YAMLError, ValueError) as exc:
        print(f"[qa-deploy] ERROR {exc}", file=sys.stderr)
        return 2
    for line in report.known:
        print(f"[qa-deploy] known violation: {line}")
    for line in report.warnings:
        print(f"[qa-deploy] warning: {line}")
    for line in report.errors:
        print(f"[qa-deploy] {line}")
    if report.errors:
        print(f"[qa-deploy] FAILED ({len(report.errors)} problems)", file=sys.stderr)
        return 1
    print(f"[qa-deploy] PASSED ({len(report.known)} known violations, {len(report.warnings)} warnings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
