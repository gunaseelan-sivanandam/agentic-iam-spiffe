#!/usr/bin/env python3
"""Offline delegation utility for M4 token chains.

Usage:
  python3 scripts/delegate_token.py \
    --token <parent_token_b64> \
    --public-key-b64-file capiss_keys/root_public_key.b64 \
    --subject spiffe://varambu.org/rogue
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import uuid

from biscuit_auth import (
    Algorithm,
    Biscuit,
    BiscuitBlockError,
    BiscuitSerializationError,
    BiscuitValidationError,
    BlockBuilder,
    Fact,
    PublicKey,
)

FACT_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)$")


def parse_fact_arg(raw: str) -> str | int:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        return raw[1:-1].replace(r'\"', '"').replace(r"\\", "\\")
    if re.fullmatch(r"-?[0-9]+", raw):
        return int(raw)
    return raw


def parse_block_source(src: str) -> dict[str, str | int]:
    out: dict[str, str | int] = {}
    for line in src.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(";"):
            line = line[:-1].strip()
        m = FACT_RE.match(line)
        if not m:
            continue
        out[m.group(1)] = parse_fact_arg(m.group(2))
    if "subject_spiffe_id" not in out and "sub" in out:
        out["subject_spiffe_id"] = out["sub"]
    return out


def extract_final_claims(biscuit: Biscuit) -> dict[str, str | int]:
    count = biscuit.block_count()
    if count <= 0:
        raise ValueError("token has no blocks")

    root = parse_block_source(biscuit.block_source(0))
    final = dict(root)
    depth = 0
    for idx in range(1, count):
        block = parse_block_source(biscuit.block_source(idx))
        final.update(block)
        depth = idx

    if "subject_spiffe_id" not in final:
        raise ValueError("missing subject_spiffe_id")
    for key in ("root_token_id", "token_id", "aud", "act", "res", "exp"):
        if key not in final:
            raise ValueError(f"missing {key}")

    final["effective_depth"] = depth
    return final


def delegate(
    token_b64: str,
    public_key_b64: str,
    subject_spiffe_id: str,
    aud: str | None,
    act: str | None,
    res: str | None,
    exp: int | None,
) -> str:
    public_key = PublicKey.from_bytes(base64.b64decode(public_key_b64), Algorithm.Ed25519)

    try:
        parent = Biscuit.from_base64(token_b64, public_key)
    except (BiscuitSerializationError, BiscuitValidationError, BiscuitBlockError) as exc:
        raise ValueError(f"invalid parent token: {exc}") from exc

    claims = extract_final_claims(parent)
    next_depth = int(claims["effective_depth"]) + 1

    chosen_aud = aud or str(claims["aud"])
    chosen_act = act or str(claims["act"])
    chosen_res = res or str(claims["res"])
    chosen_exp = exp if exp is not None else int(claims["exp"])

    if chosen_aud != str(claims["aud"]) or chosen_act != str(claims["act"]) or chosen_res != str(claims["res"]):
        raise ValueError("M4 slice only allows equal aud/act/res in offline delegation")
    if chosen_exp > int(claims["exp"]):
        raise ValueError("delegated exp cannot exceed parent exp")

    block = BlockBuilder()
    block.add_fact(Fact(f'sub("{subject_spiffe_id}")'))
    block.add_fact(Fact(f'subject_spiffe_id("{subject_spiffe_id}")'))
    block.add_fact(Fact(f'delegator_spiffe_id("{claims["subject_spiffe_id"]}")'))
    block.add_fact(Fact(f'root_token_id("{claims["root_token_id"]}")'))
    block.add_fact(Fact(f'token_id("{uuid.uuid4()}")'))
    block.add_fact(Fact(f'parent_token_id("{claims["token_id"]}")'))
    block.add_fact(Fact(f'aud("{chosen_aud}")'))
    block.add_fact(Fact(f'act("{chosen_act}")'))
    block.add_fact(Fact(f'res("{chosen_res}")'))
    block.add_fact(Fact(f"exp({chosen_exp})"))
    block.add_fact(Fact(f"delegation_depth({next_depth})"))

    return parent.append(block).to_base64()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--public-key-b64-file", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--aud")
    parser.add_argument("--act")
    parser.add_argument("--res")
    parser.add_argument("--exp", type=int)
    args = parser.parse_args()

    with open(args.public_key_b64_file, "r", encoding="utf-8") as f:
        public_key_b64 = f.read().strip()

    try:
        delegated = delegate(
            token_b64=args.token,
            public_key_b64=public_key_b64,
            subject_spiffe_id=args.subject,
            aud=args.aud,
            act=args.act,
            res=args.res,
            exp=args.exp,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(delegated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
