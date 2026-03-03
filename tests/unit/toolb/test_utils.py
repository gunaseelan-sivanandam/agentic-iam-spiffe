from __future__ import annotations

import base64
import datetime
import time
from pathlib import Path

import pytest
import redis
from biscuit_auth import KeyPair
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def _premise_module_loaded(guard, toolb_module):
    guard.premise("tool-b module loaded", toolb_module is not None)


def test_load_capiss_public_key_handles_missing_file(toolb_module, monkeypatch, tmp_path, guard):
    _premise_module_loaded(guard, toolb_module)
    guard.exercise("reset cached public key", lambda: monkeypatch.setattr(toolb_module, "_CAPISS_PUBLIC_KEY", None))
    guard.exercise("point key path to missing file", lambda: monkeypatch.setattr(toolb_module, "CAPISS_PUBLIC_KEY_PATH", str(tmp_path / "missing-key.b64")))
    public_key = guard.exercise("load capiss public key", toolb_module.load_capiss_public_key)
    guard.outcome("public key is none", public_key is None)


def test_load_capiss_public_key_round_trip(toolb_module, monkeypatch, tmp_path, guard):
    _premise_module_loaded(guard, toolb_module)
    keypair = guard.exercise("generate keypair", KeyPair)
    key_path = tmp_path / "root_public_key.b64"
    guard.exercise(
        "write key file",
        lambda: key_path.write_text(base64.b64encode(keypair.public_key.to_bytes()).decode("utf-8"), encoding="utf-8"),
    )

    guard.exercise("reset cached public key", lambda: monkeypatch.setattr(toolb_module, "_CAPISS_PUBLIC_KEY", None))
    guard.exercise("set key path", lambda: monkeypatch.setattr(toolb_module, "CAPISS_PUBLIC_KEY_PATH", str(key_path)))
    public_key = guard.exercise("load capiss public key", toolb_module.load_capiss_public_key)
    guard.outcome("public key loaded", public_key is not None)


def make_spiffe_cert(path: Path, spiffe_id: str):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "unit-test")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([x509.UniformResourceIdentifier(spiffe_id)]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def test_spiffe_id_from_cert_path(toolb_module, tmp_path, guard):
    _premise_module_loaded(guard, toolb_module)
    cert_path = tmp_path / "svid.pem"
    guard.exercise("generate spiife cert", lambda: make_spiffe_cert(cert_path, "spiffe://example.org/agent-a"))
    spiffe_id = guard.exercise("extract spiffe id", lambda: toolb_module.spiffe_id_from_cert_path(str(cert_path)))
    guard.outcome("spiffe id matches", spiffe_id == "spiffe://example.org/agent-a")


def test_is_capiss_minted_token_miss(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class Client:
        def get(self, key):
            return None

    guard.exercise("mock redis client miss", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: Client()))
    ok, hit = guard.exercise("check capiss marker", lambda: toolb_module.is_capiss_minted_token("token-1", int(time.time()) + 10))
    guard.outcome("store check succeeded", ok is True)
    guard.outcome("marker miss", hit is False)


def test_is_capiss_minted_token_hit_with_ttl_adjust(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class Client:
        def __init__(self):
            self.expire_calls = []

        def get(self, key):
            return "1"

        def ttl(self, key):
            return 100

        def expire(self, key, ttl):
            self.expire_calls.append((key, ttl))

    client = guard.exercise("create redis client", Client)
    guard.exercise("mock redis accessor", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: client))
    ok, hit = guard.exercise("check capiss marker", lambda: toolb_module.is_capiss_minted_token("token-1", int(time.time()) + 5))
    guard.outcome("store check succeeded", ok is True)
    guard.outcome("marker hit", hit is True)
    guard.outcome("ttl adjusted", bool(client.expire_calls))


@pytest.mark.invariant
def test_is_capiss_minted_token_fail_closed_on_store_error(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class Client:
        def get(self, key):
            raise redis.RedisError("down")

    guard.exercise("mock redis failure", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: Client()))
    ok, hit = guard.exercise("check capiss marker", lambda: toolb_module.is_capiss_minted_token("token-1", int(time.time()) + 10))
    guard.outcome("store check failed closed", ok is False)
    guard.outcome("marker hit false", hit is False)


def test_consume_budget_and_rate_handles_malformed_store_reply(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class Client:
        def eval(self, *args, **kwargs):
            return "bad-response"

    guard.exercise("mock malformed store reply", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: Client()))
    allowed, reason, remaining = guard.exercise(
        "consume budget and rate",
        lambda: toolb_module.consume_budget_and_rate("root-1", int(time.time()) + 20),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason store_unavailable", reason == "store_unavailable")
    guard.outcome("remaining -1", remaining == -1)


def test_record_discovery_success(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class Client:
        def eval(self, *args, **kwargs):
            return 1

    guard.exercise("mock redis client", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: Client()))
    ok = guard.exercise(
        "record discovery",
        lambda: toolb_module.record_discovery(
            "root-1",
            "spiffe://example.org/agent-a",
            ["tool-b:/read-file:fileA", "tool-b:/read-file:fileB"],
            int(time.time()) + 10,
        ),
    )
    guard.outcome("record discovery succeeded", ok is True)


def test_verify_biscuit_rejects_when_issuer_key_unavailable(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    guard.exercise("mock missing issuer key", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: None))
    allowed, reason, claims = guard.exercise(
        "verify biscuit",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://example.org/agent-a",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason issuer_key_unavailable", reason == "issuer_key_unavailable")
    guard.outcome("claims none", claims is None)
