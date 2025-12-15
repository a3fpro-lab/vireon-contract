# tests/test_capsule_determinism.py
import hashlib
import numpy as np

from vireon_rd_groundtruth.demo import _demo_gray_scott_like


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
