# src/vireon_contract/demo.py
from __future__ import annotations
import numpy as np

def _demo_gray_scott_like(seed: int, steps: int) -> np.ndarray:
    """
    Deterministic workload that produces a reproducible artifact vector x.
    """
    rng = np.random.default_rng(seed)
    x = rng.normal(size=4096)
    for _ in range(steps):
        x = np.tanh(x + 0.01 * np.roll(x, 1))
    return x

def _energy(x: np.ndarray) -> float:
    return float(np.mean(x * x))

def _fingerprint(x: np.ndarray, k: int = 64) -> np.ndarray:
    """Stable signature for inverse reconstruction."""
    return (x[:k] > 0.0).astype(np.uint8)
