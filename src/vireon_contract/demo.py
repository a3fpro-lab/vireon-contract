from __future__ import annotations
import numpy as np

def _demo_gray_scott_like(seed: int, steps: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=4096)
    for _ in range(steps):
        x = np.tanh(x + 0.01 * np.roll(x, 1))
    return x
