# tests/test_capsule_determinism.py
import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from vireon_contract.demo import _demo_gray_scott_like  # noqa: E402


def _sha256_array(x: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(str(x.shape).encode("utf-8"))
    h.update(str(x.dtype).encode("utf-8"))
    h.update(x.tobytes(order="C"))
    return h.hexdigest()


def test_demo_determinism_exact():
    x1 = _demo_gray_scott_like(seed=7, steps=80)
    x2 = _demo_gray_scott_like(seed=7, steps=80)

    # Exact determinism (strong): same bytes => same hash
    assert _sha256_array(x1) == _sha256_array(x2)
