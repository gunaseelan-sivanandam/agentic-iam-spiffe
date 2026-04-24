from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any


FACT_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)$")

ClaimValue = str | int
Claims = dict[str, ClaimValue]
ResourceTransitionValidator = Callable[[Claims, Claims], tuple[bool, str | None]]


def parse_fact_arg(raw: str) -> ClaimValue:
    value = raw.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        unquoted = value[1:-1]
        return unquoted.replace(r'\"', '"').replace(r"\\", "\\")
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return value


def parse_block_source(src: str) -> Claims:
    claims: Claims = {}
    for line in src.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(";"):
            line = line[:-1].strip()
        match = FACT_RE.match(line)
        if not match:
            continue
        name, arg = match.groups()
        claims[name] = parse_fact_arg(arg)
    if "subject_spiffe_id" not in claims and "sub" in claims:
        claims["subject_spiffe_id"] = claims["sub"]
    return claims


def extract_chain_claims(biscuit: Any) -> list[Claims]:
    count = biscuit.block_count()
    chain: list[Claims] = []
    for idx in range(count):
        block = parse_block_source(biscuit.block_source(idx))
        if "delegation_depth" not in block:
            block["delegation_depth"] = idx
        chain.append(block)
    return chain


# DD: DD-220
# Implements: ARCH-020
# Title: verify_chain_contract shared chain depth and attenuation contract
def verify_chain_contract(
    biscuit: Any,
    *,
    max_depth: int,
    allow_resource_transition: ResourceTransitionValidator | None = None,
) -> tuple[Claims | None, str | None]:
    chain = extract_chain_claims(biscuit)
    if not chain:
        return None, "invalid_chain"

    required = ("root_token_id", "token_id", "subject_spiffe_id", "aud", "act", "res", "exp")
    first = chain[0]
    for key in required:
        if key not in first:
            return None, "missing_chain_metadata"

    root_token_id = str(first["root_token_id"])
    prev_token_id = str(first["token_id"])
    prev_aud = str(first["aud"])
    prev_act = str(first["act"])
    prev_res = str(first["res"])
    prev_exp = int(first["exp"])

    previous = first
    for block in chain[1:]:
        for key in required:
            if key not in block:
                return None, "missing_chain_metadata"
        if str(block["root_token_id"]) != root_token_id:
            return None, "invalid_chain"
        if str(block.get("parent_token_id", "")) != prev_token_id:
            return None, "invalid_chain"
        if not block.get("delegator_spiffe_id"):
            return None, "invalid_chain"

        aud = str(block["aud"])
        act = str(block["act"])
        res = str(block["res"])
        exp = int(block["exp"])

        if aud != prev_aud or act != prev_act:
            return None, "amplified_authority"
        if res != prev_res:
            if allow_resource_transition is None:
                return None, "amplified_authority"
            allowed, reason = allow_resource_transition(dict(previous), block)
            if not allowed:
                return None, reason or "amplified_authority"
        if exp > prev_exp:
            return None, "amplified_authority"

        prev_token_id = str(block["token_id"])
        prev_aud = aud
        prev_act = act
        prev_res = res
        prev_exp = exp
        previous = block

    final = dict(chain[-1])
    effective_depth = len(chain) - 1
    final["effective_depth"] = effective_depth
    if int(final.get("delegation_depth", effective_depth)) != effective_depth:
        return None, "invalid_depth_metadata"
    if effective_depth > max_depth:
        return None, "depth_exceeded"
    return final, None
