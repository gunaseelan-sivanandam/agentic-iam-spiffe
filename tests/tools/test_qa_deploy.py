"""Negative controls for scripts/qa_deploy.py (test plan T-8 to T-13): deployment facts are a checked contract."""

from __future__ import annotations

import importlib.util
import subprocess  # nosec B404 - fixed git and script argv
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "qa_deploy.py"
_spec = importlib.util.spec_from_file_location("qa_deploy", SCRIPT)
assert _spec and _spec.loader
qa = importlib.util.module_from_spec(_spec)
sys.modules["qa_deploy"] = qa
_spec.loader.exec_module(qa)

NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)
OPLS = {"OPL-005": "Open", "OPL-006": "Open", "OPL-001": "Closed"}


def _svc(name: str, **overrides: object) -> "qa.Service":
    base: dict[str, object] = {
        "name": name, "image": f"build . services/{name}/Dockerfile", "user": None, "profiles": (),
        "networks": ("app_net",), "ports": (), "mounts": (), "env": ("REDIS_URL",), "privileges": (),
    }
    base.update(overrides)
    return qa.Service(**base)  # type: ignore[arg-type]


def _entry(service: "qa.Service", root: str = "grandfathered") -> dict[str, object]:
    return {
        "image": service.image, "user": service.user, "profiles": list(service.profiles),
        "networks": list(service.networks),
        "ports": list(service.ports), "mounts": list(service.mounts), "secret_env": [],
        "privileges": list(service.privileges), "root": root,
    }


def _register(*services: "qa.Service", **extra: object) -> dict[str, object]:
    register: dict[str, object] = {
        "assets": {
            "K1": {"requirement": "REQ-SEC-K1", "locations": [
                {"path": "capiss_keys/root_key.b64", "holders": ["issuer"]}]},
            "K3": {"requirement": "REQ-SEC-K3", "locations": [
                {"env": "JIRA_API_TOKEN", "holders": ["jira-tool"]}]},
            "K7": {"requirement": "REQ-SEC-K7", "locations": [
                {"container_path": "/run/spire/svid", "holders": []},
                {"path": "tmp_svid", "holders": ["harness"]}]},
        },
        "services": {s.name: _entry(s) for s in services},
        "known_violations": [],
    }
    register.update(extra)
    return register


def _errors(inventory: dict[str, "qa.Service"], register: dict[str, object]) -> list[str]:
    return qa.check_allowlist(inventory, register)


# --- T-8 inventory -----------------------------------------------------------


def test_inventory_extracts_every_fact_and_no_env_values() -> None:
    config = {"name": "compose", "services": {"tool-b": {
        "build": {"context": str(ROOT), "dockerfile": "services/tool-b/Dockerfile"},
        "profiles": ["tests"], "user": "1000",
        "networks": {"toolb_app_net": None}, "ports": [{"target": 8443, "published": "8443", "protocol": "tcp"}],
        "volumes": [{"type": "bind", "source": str(ROOT / "capiss_keys"), "target": "/k", "read_only": True},
                    {"type": "bind", "source": "/var/run/docker.sock", "target": "/var/run/docker.sock"}],
        "environment": {"JIRA_API_TOKEN": "s3cr3t-value", "REDIS_URL": "redis://x"},
        "privileged": True, "pid": "host", "cap_add": ["NET_ADMIN"],
    }}}
    service = qa.inventory_from_config(config, ROOT)["tool-b"]
    assert service.image == "build . services/tool-b/Dockerfile"
    assert service.user == "1000"
    assert service.networks == ("toolb_app_net",)
    assert service.ports == ("8443:8443/tcp",)
    assert service.mounts == ("capiss_keys:/k:ro", "/var/run/docker.sock:/var/run/docker.sock:rw")
    assert service.env == ("JIRA_API_TOKEN", "REDIS_URL")
    assert service.privileges == ("cap_add:NET_ADMIN", "pid:host", "privileged")
    assert service.profiles == ("tests",)
    assert "s3cr3t-value" not in repr(service)


def test_secrets_configs_and_volumes_from_are_inventoried() -> None:
    # Review finding C1: grants outside `volumes` must not be invisible.
    config = {"name": "compose",
              "secrets": {"k": {"file": str(ROOT / "capiss_keys" / "root_key.b64")}},
              "configs": {"c": {"file": str(ROOT / "services" / "opa" / "policy.rego")}},
              "services": {"mock": {"image": "mock:1", "secrets": [{"source": "k", "target": "key"}],
                                    "configs": [{"source": "c"}], "volumes_from": ["capability-issuer:ro"]}}}
    service = qa.inventory_from_config(config, ROOT)["mock"]
    assert "capiss_keys/root_key.b64:/run/secrets/key:ro" in service.mounts
    assert "services/opa/policy.rego:/c:ro" in service.mounts
    assert "volumes_from:capability-issuer:ro" in service.privileges
    found = {(v.asset, v.service) for v in qa.asset_violations({"mock": service}, _register())}
    assert ("K1", "mock") in found


def test_explicit_image_on_a_build_service_is_kept_and_inspected() -> None:
    # Review finding C2.
    config = {"name": "compose", "services": {"tool-b": {
        "build": {"context": str(ROOT), "dockerfile": "Dockerfile"}, "image": "evil/tool-b:1"}}}
    service = qa.inventory_from_config(config, ROOT)["tool-b"]
    assert service.image == "build . Dockerfile image evil/tool-b:1"
    assert qa.image_ref(service, "compose") == "evil/tool-b:1"
    assert qa.image_ref(_svc("tool-b"), "compose") == "compose-tool-b"
    assert qa.image_ref(_svc("redis", image="redis:7-alpine"), "compose") == "redis:7-alpine"


def test_live_inventory_covers_every_profile() -> None:
    config = qa.load_compose_config(ROOT / "compose" / "spiffe.compose.yml", ROOT / "compose")
    inventory = qa.inventory_from_config(config, ROOT)
    # tests-profile and clients-profile services are included, not only the default profile.
    assert {"rogue-tests", "capability-issuer-no-opa", "agent-a", "tool-b"} <= set(inventory)
    assert "capiss_keys:/var/lib/capiss/keys:rw" in inventory["capability-issuer-no-opa"].mounts


def test_compose_config_failure_is_an_error(tmp_path: Path) -> None:
    broken = tmp_path / "broken.yml"
    broken.write_text("services: [not, a, mapping\n", encoding="utf-8")
    with pytest.raises(qa.DeployCheckError):
        qa.load_compose_config(broken, tmp_path)


# --- T-9 default deny --------------------------------------------------------


def test_matching_register_passes() -> None:
    svc = _svc("tool-b")
    assert _errors({"tool-b": svc}, _register(svc)) == []


@pytest.mark.parametrize(
    ("change", "fragment"),
    [
        ({"image": "redis:latest"}, "image"),
        ({"networks": ("app_net", "edge_net")}, "network"),
        ({"ports": ("8080:8080/tcp",)}, "port"),
        ({"mounts": ("capiss_keys:/k:ro",)}, "mount"),
        ({"user": "0"}, "user"),
        ({"privileges": ("privileged",)}, "privilege"),
        ({"privileges": ("network_mode:host",)}, "privilege"),
        ({"privileges": ("pid:host",)}, "privilege"),
        ({"privileges": ("cap_add:SYS_ADMIN",)}, "privilege"),
        ({"privileges": ("device:/dev/kmsg",)}, "privilege"),
        ({"env": ("REDIS_URL", "JIRA_API_TOKEN")}, "secret env"),
        ({"profiles": ()}, "profile"),
    ],
)
def test_each_unregistered_fact_fails(change: dict[str, object], fragment: str) -> None:
    # A test-only service losing its profile would start by default (review finding C4).
    registered = _svc("tool-b", profiles=("tests",))
    change.setdefault("profiles", ("tests",))
    deployed = _svc("tool-b", **change)
    errors = _errors({"tool-b": deployed}, _register(registered))
    assert any(fragment in error for error in errors), errors


def test_mount_mode_change_fails() -> None:
    registered = _svc("tool-b", mounts=("spire/agent:/run/spire/agent:ro",))
    deployed = _svc("tool-b", mounts=("spire/agent:/run/spire/agent:rw",))
    assert any("mount" in e for e in _errors({"tool-b": deployed}, _register(registered)))


def test_unregistered_service_and_stale_entry_fail() -> None:
    errors = _errors({"new-svc": _svc("new-svc")}, _register(_svc("old-svc")))
    assert any("new-svc" in e and "not in the register" in e for e in errors)
    assert any("old-svc" in e and "not in compose" in e for e in errors)


def test_docker_socket_mount_is_a_mount_fact() -> None:
    deployed = _svc("tool-b", mounts=("/var/run/docker.sock:/var/run/docker.sock:ro",))
    assert any("mount" in e for e in _errors({"tool-b": deployed}, _register(_svc("tool-b"))))


# --- T-10 assets and the historical replay ---------------------------------


def test_asset_reached_by_ancestor_mount_and_env_and_container_path() -> None:
    inventory = {
        "issuer": _svc("issuer", mounts=("capiss_keys:/k:rw",)),
        "tool-b": _svc("tool-b", mounts=("capiss_keys:/k:ro",)),
        "harness": _svc("harness", mounts=(".:/repo:rw",)),
        "pubonly": _svc("pubonly", mounts=("capiss_keys/root_public_key.b64:/k/pub:ro",)),
        "gw": _svc("gw", env=("JIRA_API_TOKEN",)),
        "shared": _svc("shared", mounts=("tmp:/run/spire/svid:rw",)),
        "exported": _svc("exported", mounts=("tmp_svid/agent-a_out:/svid:ro",)),
    }
    found = {(v.asset, v.service) for v in qa.asset_violations(inventory, _register())}
    assert found == {("K1", "tool-b"), ("K1", "harness"), ("K3", "gw"), ("K7", "shared"), ("K7", "exported")}


def _compose_at(commit: str) -> dict[str, "qa.Service"]:
    text = subprocess.run(  # nosec B603 B607 - fixed git argv
        ["git", "-C", str(ROOT), "show", f"{commit}:compose/spiffe.compose.yml"],
        capture_output=True, text=True, check=True,
    ).stdout
    config = qa.load_compose_text(text, ROOT / "compose")
    return qa.inventory_from_config(config, ROOT)


def test_historical_compose_reports_signing_key_in_tool_b() -> None:
    register = qa.load_register(ROOT / "security" / "invariants.yaml")
    found = {(v.asset, v.service) for v in qa.asset_violations(_compose_at("07520d7"), register)}
    assert ("K1", "tool-b") in found


def test_current_compose_reports_exactly_the_known_violations() -> None:
    register = qa.load_register(ROOT / "security" / "invariants.yaml")
    config = qa.load_compose_config(ROOT / "compose" / "spiffe.compose.yml", ROOT / "compose")
    found = {(v.asset, v.service) for v in qa.asset_violations(qa.inventory_from_config(config, ROOT), register)}
    listed = {(k["asset"], s) for k in register["known_violations"] for s in k["services"]}
    assert found == listed


def test_removing_a_known_violation_row_fails() -> None:
    inventory = {"tool-b": _svc("tool-b", mounts=("capiss_keys:/k:ro",))}
    register = _register(_svc("tool-b", mounts=("capiss_keys:/k:ro",)))
    report = qa.check_known_violations(qa.asset_violations(inventory, register), register, OPLS, NOW)
    assert any("K1" in e and "tool-b" in e for e in report.errors)


# --- T-11 non-root ------------------------------------------------------------


def _root_report(service: "qa.Service", root: str, user: str | None, now: datetime) -> "qa.Report":
    register = {"services": {service.name: _entry(service, root)}}
    return qa.check_nonroot({service.name: service}, register, lambda _s: user, now)


@pytest.mark.parametrize(
    ("now", "expect_error"),
    [
        (datetime(2027, 1, 31, 23, 59, 58, tzinfo=timezone.utc), False),
        (datetime(2027, 1, 31, 23, 59, 59, tzinfo=timezone.utc), False),
        (datetime(2027, 2, 1, 0, 0, 0, tzinfo=timezone.utc), True),
    ],
)
def test_grandfathered_root_warns_until_expiry(now: datetime, expect_error: bool) -> None:
    report = _root_report(_svc("tool-b"), "grandfathered", None, now)
    assert bool(report.errors) is expect_error
    assert bool(report.warnings) is not expect_error


def test_new_service_cannot_be_grandfathered() -> None:
    report = _root_report(_svc("brand-new"), "grandfathered", None, NOW)
    assert any("brand-new" in e and "grandfather" in e for e in report.errors)


@pytest.mark.parametrize("user", [None, "", "root", "0", "0:0", ":", "root:root"])
def test_locked_service_running_as_root_or_unknown_fails(user: str | None) -> None:
    assert _root_report(_svc("opa"), "forbidden", user, NOW).errors


def test_locked_service_as_non_root_passes() -> None:
    report = _root_report(_svc("opa"), "forbidden", "1000:1000", NOW)
    assert report.errors == [] and report.warnings == []


def test_effective_user_prefers_compose_user_over_image() -> None:
    assert qa.effective_user(_svc("x", user="1000"), lambda _ref: "") == "1000"
    assert qa.effective_user(_svc("x"), lambda _ref: "1000:1000") == "1000:1000"
    assert qa.effective_user(_svc("x"), lambda _ref: None) is None


# --- T-12 register consistency -----------------------------------------------

REQS = """
## REQ-SEC-K1 — Issuer signing key confinement
Readable only inside the issuer. Holders: `issuer`.

## REQ-SEC-K3 — Upstream credential confinement
Holders: `jira-tool`.

## REQ-SEC-K7 — Workload key confinement
Holders: `harness` (exports keys for tests).
"""


def test_consistent_register_passes() -> None:
    assert qa.check_register_consistency(_register(), REQS) == []


def test_widened_holders_without_requirement_change_fails() -> None:
    register = _register()
    register["assets"]["K1"]["locations"][0]["holders"].append("tool-b")  # type: ignore[index]
    assert any("REQ-SEC-K1" in e for e in qa.check_register_consistency(register, REQS))


def test_requirement_without_asset_and_asset_without_requirement_fail() -> None:
    extra_req = REQS + "\n## REQ-SEC-K9 — Something new\nHolders: `x`.\n"
    assert any("REQ-SEC-K9" in e for e in qa.check_register_consistency(_register(), extra_req))
    register = _register()
    register["assets"]["K8"] = {"requirement": "REQ-SEC-K8", "locations": []}  # type: ignore[index]
    assert any("REQ-SEC-K8" in e for e in qa.check_register_consistency(register, REQS))


# --- T-13 known violations ---------------------------------------------------


def _violating() -> tuple[list["qa.Violation"], dict[str, object]]:
    svc = _svc("tool-b", mounts=("capiss_keys:/k:ro",))
    register = _register(svc)
    return qa.asset_violations({"tool-b": svc}, register), register


def _known(**fields: object) -> dict[str, object]:
    row: dict[str, object] = {"opl": "OPL-005", "asset": "K1", "services": ["tool-b"], "expires": "2026-12-31"}
    row.update(fields)
    return row


def test_matching_known_violation_is_reported_as_known() -> None:
    violations, register = _violating()
    register["known_violations"] = [_known()]
    report = qa.check_known_violations(violations, register, OPLS, NOW)
    assert report.errors == [] and any("OPL-005" in k for k in report.known)


@pytest.mark.parametrize(
    "row",
    [
        {"opl": "OPL-005", "asset": "K1", "services": ["tool-b"]},                  # no expiry
        {"opl": "OPL-005", "asset": "K1", "expires": "2026-12-31"},                  # no services
        _known(services=["jira-tool"]),                                              # other service
        _known(asset="K3"),                                                          # other asset
        _known(opl="OPL-001"),                                                       # closed OPL
        _known(opl="OPL-404"),                                                       # unknown OPL
    ],
)
def test_invalid_or_mismatched_known_violation_fails(row: dict[str, object]) -> None:
    violations, register = _violating()
    register["known_violations"] = [row]
    assert qa.check_known_violations(violations, register, OPLS, NOW).errors


@pytest.mark.parametrize(
    ("now", "expect_error"),
    [
        (datetime(2026, 12, 31, 23, 59, 58, tzinfo=timezone.utc), False),
        (datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc), False),
        (datetime(2027, 1, 1, 0, 0, 0, tzinfo=timezone.utc), True),
    ],
)
def test_known_violation_expiry_boundary(now: datetime, expect_error: bool) -> None:
    violations, register = _violating()
    register["known_violations"] = [_known()]
    assert bool(qa.check_known_violations(violations, register, OPLS, now).errors) is expect_error


def test_opl_status_parsing() -> None:
    text = "## OPL-005: a\n\n- Status: Open\n\n## OPL-001: b\n- Status: Closed (2026-01-02)\n"
    assert qa.opl_statuses(text) == {"OPL-005": "Open", "OPL-001": "Closed (2026-01-02)"}


# --- end to end on the repository --------------------------------------------


def test_repository_deployment_passes_with_known_violations_only() -> None:
    result = subprocess.run(  # nosec B603 - fixed argv
        [sys.executable, str(SCRIPT), "--skip-image-users"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[qa-deploy] PASSED" in result.stdout
    assert "OPL-005" in result.stdout
