from __future__ import annotations

import pytest


def _premise_module_loaded(guard, capiss_module):
    guard.premise("capiss module loaded", capiss_module is not None)


@pytest.mark.boundary
@pytest.mark.parametrize(
    ("aud", "res", "expected"),
    [
        ("tool-b", "tool-b:/search", "tool-b:/search"),
        ("tool-b", "/search", "tool-b:/search"),
        ("tool-b", "tool-b:/secret", "tool-b:/secret"),
        ("tool-b", "/secret", "/secret"),
        ("tool-b", "tool-b:/read-file:fileA", "tool-b:/read-file:fileA"),
        ("tool-b", "tool-b:/read-file:file A", None),
        ("tool-b", "tool-b:/read-file:file/A", None),
        ("tool-b", "tool-b:/read-file:*", None),
        ("tool-b", "tool-b:/read-file:file?", None),
        ("tool-b", "tool-b:/all", None),
        ("tool-x", "tool-b:/search", None),
        ("tool-b", "search", None),
    ],
)
def test_canonicalize_resource_matrix(capiss_module, guard, aud: str, res: str, expected: str | None):
    _premise_module_loaded(guard, capiss_module)
    out = guard.exercise(
        "canonicalize resource",
        lambda: capiss_module.canonicalize_resource(aud, res),
    )
    guard.outcome("canonical result matches expected", out == expected)


@pytest.mark.invariant
def test_canonicalize_resource_rejects_wildcards(capiss_module, guard):
    _premise_module_loaded(guard, capiss_module)
    results = guard.exercise(
        "canonicalize wildcard-like resources",
        lambda: [
            capiss_module.canonicalize_resource("tool-b", wildcard_like)
            for wildcard_like in (
                "tool-b:/read-file:*",
                "tool-b:/read-file:[a-z]",
                "tool-b:/read-file:file?",
            )
        ],
    )
    guard.outcome("all wildcard-like resources rejected", all(item is None for item in results))
