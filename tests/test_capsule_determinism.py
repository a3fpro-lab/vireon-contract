# tests/test_capsule_determinism.py
import hashlib
import importlib.util
from pathlib import Path

import numpy as np


def _find_and_load_demo_fn(name: str):
    """
    Find a function by name in the repo by scanning .py files, then load that file as a module.
    This avoids brittle import paths and works in CI for src/ layouts or flat scripts.
    """
    root = Path(__file__).resolve().parents[1]
    candidates = []

    # Prefer src/ if present, else scan entire repo.
    scan_roots = []
    if (root / "src").exists():
        scan_roots.append(root / "src")
    scan_roots.append(root)

    needle = f"def {name}("
    for base in scan_roots:
        for p in base.rglob("*.py"):
            # Skip obvious noise
            if any(part in {".git", ".venv", "venv", "__pycache__", "site-packages"} for part in p.parts):
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if needle in txt:
                candidates.append(p)

    if not candidates:
        raise ImportError(
            f"Could not find function {name!r} anywhere in the repo. "
            f"Searched under: {', '.join(str(r) for r in scan_roots)}"
        )

    # Load the first hit deterministically (sorted path).
    target = sorted(candidates, key=lambda x: str(x))[0]
    spec = importlib.util.spec_from_file_location("_vireon_demo_module", target)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {target}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]

    fn = getattr(mod, name, None)
    if fn is None:
        raise ImportError(f"Found {name!r} in {target}, but attribute not loadable after import.")
    return fn


def _sha256_state(x) -> str:
    """Exact fingerprint for nested states containing numpy arrays."""
    h = hashlib.sha256()

    def upd(obj):
        if isinstance(obj, np.ndarray):
            h.update(str(obj.shape).encode("utf-8"))
            h.update(str(obj.dtype).encode("utf-8"))
            h.update(obj.tobytes(order="C"))
            return
        if obj is None:
            h.update(b"None")
            return
        if isinstance(obj, (bool, int, float, str)):
            h.update(repr(obj).encode("utf-8"))
            return
        if isinstance(obj, (list, tuple)):
            h.update(b"[")
            for item in obj:
                upd(item)
                h.update(b",")
            h.update(b"]")
            return
        if isinstance(obj, dict):
            h.update(b"{")
            for k in sorted(obj.keys(), key=lambda z: repr(z)):
                upd(k)
                h.update(b":")
                upd(obj[k])
                h.update(b",")
            h.update(b"}")
            return
        h.update(repr(obj).encode("utf-8"))

    upd(x)
    return h.hexdigest()


def test_demo_determinism_exact():
    demo = _find_and_load_demo_fn("_demo_gray_scott_like")

    s1 = demo(seed=7, steps=80)
    s2 = demo(seed=7, steps=80)

    assert _sha256_state(s1) == _sha256_state(s2)
