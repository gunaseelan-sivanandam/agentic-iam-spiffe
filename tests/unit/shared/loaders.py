from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SERVICES_ROOT = Path(REPO_ROOT, "services")


def _stable_module_name(path: Path, module_prefix: str) -> str:
    rel = path.relative_to(REPO_ROOT).with_suffix("")
    # Keep mutmut-compatible path-like module names (including hyphenated dirs)
    # so mutant-to-test association can resolve function ownership correctly.
    return rel.as_posix().replace("/", ".")


def load_module_from_path(path: Path, module_prefix: str):
    module_name = _stable_module_name(path, module_prefix)
    if module_name in sys.modules:
        del sys.modules[module_name]
    if str(SERVICES_ROOT) not in sys.path:
        sys.path.insert(0, str(SERVICES_ROOT))
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
