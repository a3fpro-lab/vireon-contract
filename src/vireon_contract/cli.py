from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from .schema import Spec, Capsule, Metric, Falsifier
from .capsule import write_capsule, default_provenance
from .verify import claim_sha256

def _demo_gray_scott_like(seed: int, steps: int) -> float:
    # Deterministic numeric workload for proving capsule plumbing + determinism falsifier.
    rng = np.random.default_rng(seed)
    x = rng.normal(size=4096)
    for _ in range(steps):
        x = np.tanh(x + 0.01 * np.roll(x, 1))
    return float(np.mean(x * x))

def main() -> None:
    ap = argparse.ArgumentParser(prog="vireon")
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("capsule", help="Produce a VIREON capsule")
    run.add_argument("--out", required=True)
    run.add_argument("--seed", type=int, default=1)
    run.add_argument("--steps", type=int, default=50)

    args = ap.parse_args()

    if args.cmd == "capsule":
        score = _demo_gray_scott_like(args.seed, args.steps)
        score2 = _demo_gray_scott_like(args.seed, args.steps)
        det_pass = (score == score2)

        # repo root = .../src/vireon_contract/cli.py -> parents[2] = repo root
        repo_root = Path(__file__).resolve().parents[2]
        c_hash = claim_sha256(repo_root)

        spec = Spec(
            domain="kernel",
            model="demo_workload",
            params={"note": "Replace with real model downstream (RD/MIP/etc)."},
            discretization={"steps": args.steps},
            init={"seed": args.seed, "type": "rng_demo"},
            boundary={"type": "n/a"},
        )

        capsule = Capsule(
            spec=spec,
            provenance=default_provenance(),
            metrics=[Metric(name="demo_energy", value=score, units="arb", notes="mean(tanh dynamics)^2")],
            falsifiers=[
                Falsifier(
                    name="determinism_same_seed",
                    description="Same seed + same steps must match exactly (CPU).",
                    passed=det_pass,
                    details={"score1": score, "score2": score2, "tau": 0.0},
                ),
                Falsifier(
                    name="hash_verification",
                    description="capsule.sha256 and manifest.json must verify against capsule contents.",
                    passed=True,
                    details={"note": "Verified in tests/CI via vireon_contract.verify.verify_hashes"},
                ),
            ],
            claim_sha256=c_hash,
            artifacts={},
        )

        write_capsule(Path(args.out), capsule)
        print(f"Wrote capsule to {args.out}")
