"""Shape-only secret check over published test evidence (slice ci-evidence-trace, D3).

Finds secrets by their shape, never by comparing against a secret file, and never returns or prints
a matched value: a finding names the file, the line and the kind of secret. Secrets this repository
creates use recognisable formats (AGENTS.md coding rule 7), so each has a shape below.

The E2E harness also uses this module to publish each test's scratch directory into the evidence
directory, replacing every token-shaped value with its SHA-256 fingerprint:
    python3 evidence_secrets.py publish <scratch-dir> <evidence-dir>
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# A token-shaped run: capiss tokens are 600 or more base64url characters; other evidence stays under
# 100. A long run of few distinct characters (padding, hex) is not a token.
MIN_TOKEN_RUN = 200
MIN_TOKEN_DISTINCT = 20

PEM_PRIVATE_KEY = re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----")
PEM_CERTIFICATE_BLOCK = re.compile(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", re.DOTALL)
BASE64_RUN = re.compile(r"[A-Za-z0-9+/_-]{40,}={0,2}")
# base64 of "-----BEGIN " when the PEM text starts the encoded data.
BASE64_PEM_START = "LS0tLS1CRUdJTi"
CREDENTIAL_LINE = re.compile(
    r"(?:JIRA_API_TOKEN\s*=|Authorization\s*:[ \t]*(?:(?:Bearer|Basic|Token)[ \t]+)?)[ \t]*['\"]?(?P<value>[^\s'\"]+)",
    re.IGNORECASE,
)
# A value that names a variable or a redaction marker is not a credential.
PLACEHOLDER = re.compile(r"^(?:\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|<[^>]*>|\[?REDACTED\]?|\*+|Bearer|Basic)$", re.IGNORECASE)
ATLASSIAN_TOKEN = re.compile(r"ATATT3[A-Za-z0-9_=-]{20,}")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.kind}"


def _b64decode(run: str) -> bytes | None:
    data = run.rstrip("=").replace("-", "+").replace("_", "/")
    data += "=" * (-len(data) % 4)
    try:
        return base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError):
        return None


def _der_length(der: bytes, index: int) -> tuple[int, int] | None:
    """Return (length, index after the length octets) of the DER element whose length starts at index."""
    if index >= len(der):
        return None
    first = der[index]
    if first < 0x80:
        return first, index + 1
    count = first & 0x7F
    if count == 0 or count > 2 or index + 1 + count > len(der):
        return None
    return int.from_bytes(der[index + 1:index + 1 + count], "big"), index + 1 + count


def is_pkcs8_der(der: bytes) -> bool:
    """PKCS#8 / OneAsymmetricKey: SEQUENCE { INTEGER 0 or 1, SEQUENCE AlgorithmIdentifier, ... }."""
    if len(der) < 16 or der[0] != 0x30:
        return False
    parsed = _der_length(der, 1)
    if parsed is None:
        return False
    length, body = parsed
    if body + length != len(der):
        return False
    return der[body:body + 3] in (b"\x02\x01\x00", b"\x02\x01\x01") and der[body + 3:body + 4] == b"\x30"


def _run_kinds(run: str) -> list[str]:
    kinds = []
    decoded = _b64decode(run)
    if decoded is not None and is_pkcs8_der(decoded):
        kinds.append("base64 PKCS#8 private key")
    start = run.find(BASE64_PEM_START)
    if start >= 0:
        pem = _b64decode(run[start:])
        if pem is not None and PEM_PRIVATE_KEY.search(pem.decode("ascii", "replace")):
            kinds.append("base64-encoded PEM private key")
    if _is_token_shaped(run):
        kinds.append("token-shaped value")
    return kinds


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_text(text: str, path: str) -> list[Finding]:
    findings = [Finding(path, _line_of(text, m.start()), "PEM private key") for m in PEM_PRIVATE_KEY.finditer(text)]
    without_certs = PEM_CERTIFICATE_BLOCK.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    for match in BASE64_RUN.finditer(without_certs):
        line = _line_of(text, match.start())
        findings += [Finding(path, line, kind) for kind in _run_kinds(match.group(0))]
    for match in CREDENTIAL_LINE.finditer(text):
        if not PLACEHOLDER.match(match.group("value")):
            findings.append(Finding(path, _line_of(text, match.start()), "credential line"))
    findings += [Finding(path, _line_of(text, m.start()), "Atlassian API token") for m in ATLASSIAN_TOKEN.finditer(text)]
    return sorted(set(findings), key=lambda f: (f.line, f.kind))


def _walk(root: Path) -> tuple[list[Path], list[str]]:
    """Every file under root, and an error for each directory that could not be listed."""
    if not root.is_dir():
        return [root], []
    files: list[Path] = []
    errors: list[str] = []

    def on_error(exc: OSError) -> None:
        errors.append(f"{exc.filename}: cannot list ({exc.strerror or type(exc).__name__})")

    for dirpath, _dirnames, filenames in os.walk(root, onerror=on_error):
        files += [Path(dirpath) / name for name in filenames]
    return sorted(files), errors


def _read(path: Path) -> str:
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8", "replace")


def scan(paths: list[Path]) -> tuple[list[Finding], list[str]]:
    """Scan every file under the given paths. Returns (findings, errors); an unreadable file is an error."""
    findings: list[Finding] = []
    errors: list[str] = []
    for root in paths:
        if not root.exists():
            continue
        files, walk_errors = _walk(root)
        errors += walk_errors
        for path in files:
            try:
                text = _read(path)
            except OSError as exc:
                errors.append(f"{path}: cannot read ({exc.strerror or type(exc).__name__})")
                continue
            findings += scan_text(text, str(path))
    return findings, errors


def fingerprint(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("ascii")).hexdigest()


def _is_token_shaped(run: str) -> bool:
    body = run.rstrip("=")
    return len(body) >= MIN_TOKEN_RUN and len(set(body)) >= MIN_TOKEN_DISTINCT


def redact_text(text: str) -> str:
    """Replace every token-shaped run outside PEM CERTIFICATE blocks with its fingerprint."""
    without_certs = PEM_CERTIFICATE_BLOCK.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    spans = [m.span() for m in BASE64_RUN.finditer(without_certs) if _is_token_shaped(m.group(0))]
    for start, end in reversed(spans):
        text = text[:start] + fingerprint(text[start:end]) + text[end:]
    return text


def publish(src: Path, dst: Path) -> None:
    """Copy src to dst with token-shaped values replaced by fingerprints, all or nothing.

    The copy is built in a sibling directory and renamed onto dst (which must be absent or empty)
    only when every file was copied; on any error nothing new appears in dst and the error is raised.
    """
    partial = dst.with_name(dst.name + ".partial")
    shutil.rmtree(partial, ignore_errors=True)
    try:
        partial.mkdir(parents=True)
        files, errors = _walk(src)
        if errors:
            raise OSError("; ".join(errors))
        for path in files:
            target = partial / path.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "rb") as handle:
                data = handle.read()
            text = data.decode("utf-8", "surrogateescape")
            target.write_bytes(redact_text(text).encode("utf-8", "surrogateescape"))
            shutil.copymode(path, target)
        os.replace(partial, dst)
    except OSError:
        shutil.rmtree(partial, ignore_errors=True)
        raise


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[0] == "publish":
        publish(Path(argv[1]), Path(argv[2]))
        return 0
    print("usage: evidence_secrets.py publish <scratch-dir> <evidence-dir>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
