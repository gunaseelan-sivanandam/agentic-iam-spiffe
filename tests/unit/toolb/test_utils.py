from __future__ import annotations

import base64
import datetime
import io
import json
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


# UT: UT-077
# Test Description: Verifies that load capiss public key handles missing file.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-213
def test_load_capiss_public_key_handles_missing_file(toolb_module, monkeypatch, tmp_path, guard):
    _premise_module_loaded(guard, toolb_module)
    guard.exercise("reset cached public key", lambda: monkeypatch.setattr(toolb_module, "_CAPISS_PUBLIC_KEY", None))
    guard.exercise("point key path to missing file", lambda: monkeypatch.setattr(toolb_module, "CAPISS_PUBLIC_KEY_PATH", str(tmp_path / "missing-key.b64")))
    public_key = guard.exercise("load capiss public key", toolb_module.load_capiss_public_key)
    guard.outcome("public key is none", public_key is None)


# UT: UT-078
# Test Description: Verifies load capiss public key round trip.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-213
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


# UT: UT-079
# Test Description: Verifies spiffe id from cert path.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-212
def test_spiffe_id_from_cert_path(toolb_module, tmp_path, guard):
    _premise_module_loaded(guard, toolb_module)
    cert_path = tmp_path / "svid.pem"
    guard.exercise("generate spiife cert", lambda: make_spiffe_cert(cert_path, "spiffe://varambu.org/agent-a"))
    spiffe_id = guard.exercise("extract spiffe id", lambda: toolb_module.spiffe_id_from_cert_path(str(cert_path)))
    guard.outcome("spiffe id matches", spiffe_id == "spiffe://varambu.org/agent-a")


# UT: UT-088
# Test Description: Verifies that parse fact arg decodes quoted strings, integers, and raw symbols correctly.
# Precondition: Module fixtures are loaded and representative biscuit fact arguments are available as plain strings.
# Expected Output: The SUT unquotes string literals, converts integer literals to integers, and leaves raw symbols unchanged.
# Covers DD: DD-214
def test_parse_fact_arg_decodes_string_integer_and_raw(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    quoted = guard.exercise("parse quoted string", lambda: toolb_module.parse_fact_arg('"read\\"write"'))
    integer = guard.exercise("parse integer", lambda: toolb_module.parse_fact_arg("42"))
    raw = guard.exercise("parse raw symbol", lambda: toolb_module.parse_fact_arg("tool-b:/search"))
    guard.outcome("quoted string unescaped", quoted == 'read"write')
    guard.outcome("integer converted", integer == 42)
    guard.outcome("raw symbol preserved", raw == "tool-b:/search")


# UT: UT-089
# Test Description: Verifies that parse block source extracts known facts, aliases sub to subject_spiffe_id, and ignores noise.
# Precondition: Module fixtures are loaded and a biscuit block source string contains valid facts alongside unrelated lines.
# Expected Output: The SUT returns parsed claims for recognized facts, adds subject_spiffe_id from sub when needed, and drops unmatched lines.
# Covers DD: DD-215
def test_parse_block_source_aliases_sub_and_ignores_noise(toolb_module, guard):
    _premise_module_loaded(guard, toolb_module)
    source = '\n'.join([
        'sub("spiffe://varambu.org/agent-a");',
        'act("read");',
        "exp(7);",
        "not a fact line",
    ])
    claims = guard.exercise("parse biscuit block source", lambda: toolb_module.parse_block_source(source))
    guard.outcome("sub preserved", claims.get("sub") == "spiffe://varambu.org/agent-a")
    guard.outcome("subject alias added", claims.get("subject_spiffe_id") == "spiffe://varambu.org/agent-a")
    guard.outcome("act preserved", claims.get("act") == "read")
    guard.outcome("exp converted", claims.get("exp") == 7)
    guard.outcome("noise ignored", "not a fact line" not in claims)


# UT: UT-080
# Test Description: Verifies is capiss minted token miss.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-205
def test_is_capiss_minted_token_miss(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class Client:
        def get(self, key):
            return None

    guard.exercise("mock redis client miss", lambda: monkeypatch.setattr(toolb_module, "get_redis", lambda: Client()))
    ok, hit = guard.exercise("check capiss marker", lambda: toolb_module.is_capiss_minted_token("token-1", int(time.time()) + 10))
    guard.outcome("store check succeeded", ok is True)
    guard.outcome("marker miss", hit is False)


# UT: UT-081
# Test Description: Verifies is capiss minted token hit with ttl adjust.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-205
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


# UT: UT-082
# Test Description: Verifies is capiss minted token fail closed on store error.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-205
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


# UT: UT-083
# Test Description: Verifies that consume budget and rate handles malformed store reply.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT exhibits the behavior asserted by the outcome guards for this scenario.
# Covers DD: DD-203
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


# UT: UT-084
# Test Description: Verifies that record discovery success.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT returns the successful values and side effects asserted by the outcome guards for this scenario.
# Covers DD: DD-204
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
            "spiffe://varambu.org/agent-a",
            ["tool-b:/read-file:fileA", "tool-b:/read-file:fileB"],
            int(time.time()) + 10,
        ),
    )
    guard.outcome("record discovery succeeded", ok is True)


# UT: UT-085
# Test Description: Verifies that verify biscuit rejects when issuer key unavailable.
# Precondition: Module fixtures are loaded and any scenario-specific stubs or inputs are prepared in the exercise phase.
# Expected Output: The SUT rejects or fails closed exactly as asserted by the outcome guards for this scenario.
# Covers DD: DD-202, DD-213
def test_verify_biscuit_rejects_when_issuer_key_unavailable(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    guard.exercise("mock missing issuer key", lambda: monkeypatch.setattr(toolb_module, "load_capiss_public_key", lambda: None))
    allowed, reason, claims = guard.exercise(
        "verify biscuit",
        lambda: toolb_module.verify_biscuit(
            "token",
            "spiffe://varambu.org/agent-a",
            "read",
            "tool-b:/search",
        ),
    )
    guard.outcome("allowed false", allowed is False)
    guard.outcome("reason issuer_key_unavailable", reason == "issuer_key_unavailable")
    guard.outcome("claims none", claims is None)


# UT: UT-112
# Test Description: Verifies that tool-b iso_utc_now returns the exact ISO timestamp from the module-local datetime source.
# Precondition: Module fixtures are loaded and the module-local datetime dependency is stubbed to a fixed UTC instant.
# Expected Output: The SUT returns the exact ISO-8601 string produced by the stubbed datetime object.
# Covers DD: DD-209
@pytest.mark.invariant
def test_toolb_iso_utc_now_returns_exact_stubbed_timestamp(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)

    class FixedInstant:
        def isoformat(self):
            return "2026-04-03T12:13:14+00:00"

    class FixedDateTime:
        @staticmethod
        def now(tz):
            return FixedInstant()

    guard.exercise("stub datetime.now", lambda: monkeypatch.setattr(toolb_module, "datetime", FixedDateTime))
    out = guard.exercise("call iso_utc_now", toolb_module.iso_utc_now)
    guard.outcome("exact timestamp returned", out == "2026-04-03T12:13:14+00:00")


# UT: UT-113
# Test Description: Verifies that tool-b log_event emits an exact structured JSON audit record using the module-local timestamp helper.
# Precondition: Module fixtures are loaded, the timestamp helper is stubbed to a fixed value, and print output is captured.
# Expected Output: The SUT prints exactly one compact JSON object containing the event type, timestamp, and supplied fields.
# Covers DD: DD-210
@pytest.mark.invariant
def test_toolb_log_event_emits_exact_structured_json(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    printed: list[tuple[tuple[object, ...], dict[str, object]]] = []
    guard.exercise("stub audit timestamp", lambda: monkeypatch.setattr(toolb_module, "iso_utc_now", lambda: "2026-04-03T12:13:14+00:00"))
    guard.exercise(
        "capture print",
        lambda: monkeypatch.setattr(toolb_module, "print", lambda *args, **kwargs: printed.append((args, kwargs)), raising=False),
    )
    guard.exercise(
        "emit audit log",
        lambda: toolb_module.log_event("toolb_test", result="ok", reason_code="demo"),
    )
    guard.outcome("single print call", len(printed) == 1)
    guard.outcome("exact print kwargs", printed[0][1] == {"flush": True})
    guard.outcome(
        "exact structured payload",
        json.loads(printed[0][0][0])
        == {
            "event_type": "toolb_test",
            "timestamp": "2026-04-03T12:13:14+00:00",
            "result": "ok",
            "reason_code": "demo",
        },
    )


# UT: UT-114
# Test Description: Verifies that tool-b get_redis constructs the Redis client once with exact module configuration and then reuses the cached instance.
# Precondition: Module fixtures are loaded, the module cache is empty, and the Redis factory is replaced with a recording stub.
# Expected Output: The SUT calls Redis.from_url exactly once with the configured URL and socket settings, then returns the cached client on subsequent calls.
# Covers DD: DD-211
@pytest.mark.invariant
def test_toolb_get_redis_caches_exact_constructed_client(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    client = object()
    guard.exercise("reset redis cache", lambda: monkeypatch.setattr(toolb_module, "_redis_client", None))

    def fake_from_url(*args, **kwargs):
        calls.append((args, kwargs))
        return client

    guard.exercise(
        "capture redis factory",
        lambda: monkeypatch.setattr(toolb_module.redis.Redis, "from_url", fake_from_url),
    )
    first = guard.exercise("get redis first time", toolb_module.get_redis)
    second = guard.exercise("get redis second time", toolb_module.get_redis)
    guard.outcome("cached client returned first time", first is client)
    guard.outcome("cached client returned second time", second is client)
    guard.outcome("factory called once", len(calls) == 1)
    guard.outcome(
        "factory args exact",
        calls[0]
        == (
            (toolb_module.M4_REDIS_URL,),
            {
                "encoding": "utf-8",
                "decode_responses": True,
                "socket_timeout": toolb_module.M4_REDIS_SOCKET_TIMEOUT,
            },
        ),
    )


# UT: UT-117
# Test Description: Verifies that tool-b main wires the HTTP server bootstrap exactly once and starts serving with the resolved SPIFFE identity.
# Precondition: Module fixtures are loaded, identity lookup and HTTP server construction are stubbed, and print output is captured.
# Expected Output: The SUT resolves the SPIFFE ID from SVID_CERT, constructs HTTPServer with the exact listen tuple and handler, prints startup lines, and invokes serve_forever once.
# Covers DD: DD-219
@pytest.mark.invariant
def test_toolb_main_bootstraps_http_server_exactly(toolb_module, monkeypatch, guard):
    _premise_module_loaded(guard, toolb_module)
    printed: list[str] = []
    server_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    serve_called = {"count": 0}

    class FakeServer:
        def __init__(self, *args, **kwargs):
            server_calls.append((args, kwargs))

        def serve_forever(self):
            serve_called["count"] += 1

    guard.exercise(
        "stub spiffe id lookup",
        lambda: monkeypatch.setattr(toolb_module, "spiffe_id_from_cert_path", lambda path: f"spiffe-for:{path}"),
    )
    guard.exercise("capture prints", lambda: monkeypatch.setattr(toolb_module, "print", lambda msg: printed.append(msg), raising=False))
    guard.exercise("stub http server", lambda: monkeypatch.setattr(toolb_module, "HTTPServer", FakeServer))
    guard.exercise("run main", toolb_module.main)
    guard.outcome(
        "server constructed exactly once",
        server_calls == [((("0.0.0.0", 8080), toolb_module.ToolBHandler), {})],
    )
    guard.outcome("serve_forever called once", serve_called["count"] == 1)
    guard.outcome(
        "startup prints exact lines",
        printed
        == [
            f"tool-b SPIFFE ID: spiffe-for:{toolb_module.SVID_CERT}",
            "tool-b listening on http://0.0.0.0:8080",
        ],
    )
