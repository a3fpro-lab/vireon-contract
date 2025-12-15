from __future__ import annotations
from pathlib import Path
import json, sys, platform
import numpy as np
from .schema import Capsule, Provenance
from .hashing import sha256_bytes, hash_tree

def _deps_minimal() -> dict:
    return {"numpy": np.__version__}

def default_provenance(git_sha: str = "UNKNOWN") -> Provenance:
    return Provenance(
        git_sha=git_sha,
        platform=f"{platform.system()}-{platform.machine()}",
        python=sys.version.split()[0],
        deps=_deps_minimal(),
    )

def write_capsule(out_dir: Path, capsule: Capsule) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "artifacts").mkdir(exist_ok=True)

    capsule_json = capsule.to_json().encode("utf-8")
    (out_dir / "capsule.json").write_bytes(capsule_json)

    manifest = hash_tree(out_dir)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
    (out_dir / "capsule.sha256").write_text(sha256_bytes(capsule_json) + "\n", encoding="utf-8")
