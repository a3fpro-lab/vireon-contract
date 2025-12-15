import hashlib
import sys
from pathlib import Path

import numpy as np

# Ensure `src/` layout works in CI even if the package isn't installed yet.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

# Try the likely module paths in *this* repo.
_demo_gray_scott_like = None
for modpath in (
    "vireon_contract.demo",
    "vireon_contract.demos",
    "vireon_contract.capsule_demo",
    "vireon_contract.gray_scott",
    "demo",
):
    try:
        mod = __import__(modpath, fromlist=["_demo_gray_scott_like"])
        _demo_gray_scott_like = getattr(mod, "_demo_gray_scott_like")
        break
    except Exception:
        pass

if _demo_gray_scott_like is None:
    raise ImportError(
        "Could not find _demo_gray_scott_like in this repo. "
        "Search for its location and add it to the modpath list."
    )


def _sha256_state(x) -> str:
    """
    Deterministic, exact fingerprint for nested states that may contain numpy arrays.
    This avoids Python's ambiguous array truthiness and gives a single exact check.
    """
    h = hashlib.sha256()

    def upd(obj):
        if isinstance(obj, np.ndarray):
            # include shape + dtype + bytes so different views can't collide
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
            # sort keys for deterministic order
            h.update(b"{")
            for k in sorted(obj.keys(), key=lambda z: repr(z)):
                upd(k)
                h.update(b":")
                upd(obj[k])
                h.update(b",")
            h.update(b"}")
            return

        # fallback: stable repr
        h.update(repr(obj).encode("utf-8"))

    upd(x)
    return h.hexdigest()


def test_demo_determinism_exact():
    s1 = _demo_gray_scott_like(seed=7, steps=80)
    s2 = _demo_gray_scott_like(seed=7, steps=80)

    assert _sha256_state(s1) == _sha256_state(s2)
