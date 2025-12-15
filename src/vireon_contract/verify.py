from __future__ import annotations
from pathlib import Path
import json

from .hashing import sha256_bytes, sha256_file


def stable_json_bytes(obj) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def claim_sha256(repo_root: Path) -> str:
    p = repo_root / "claim.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return sha256_bytes(stable_json_bytes(data))


def verify_hashes(capsule_dir: Path) -> None:
    # Verify capsule.sha256 matches capsule.json
    capsule_json = (capsule_dir / "capsule.json").read_bytes()
    expected = (capsule_dir / "capsule.sha256").read_text(encoding="utf-8").strip()
    actual = sha256_bytes(capsule_json)
    if actual != expected:
        raise AssertionError(f"capsule.sha256 mismatch: expected {expected}, got {actual}")

    # Verify manifest hashes
    manifest = json.loads((capsule_dir / "manifest.json").read_text(encoding="utf-8"))
    for rel, h in manifest.items():
        fp = capsule_dir / rel
        if not fp.is_file():
            raise AssertionError(f"manifest references missing file: {rel}")
        if sha256_file(fp) != h:
            raise AssertionError(f"manifest hash mismatch for {rel}")


def verify_claim_locked(capsule_dir: Path) -> None:
    """
    LAW §5 enforcement:
    - capsule must contain claim.json
    - hash(claim.json canonical stable-json) must equal capsule.claim_sha256
    """
    capsule = json.loads((capsule_dir / "capsule.json").read_text(encoding="utf-8"))
    expected = capsule.get("claim_sha256")
    if not expected:
        raise AssertionError("capsule.json missing claim_sha256")

    claim_path = capsule_dir / "claim.json"
    if not claim_path.is_file():
        raise AssertionError("capsule missing claim.json (must be self-contained)")

    claim_obj = json.loads(claim_path.read_text(encoding="utf-8"))
    actual = sha256_bytes(stable_json_bytes(claim_obj))
    if actual != expected:
        raise AssertionError(f"claim hash mismatch: expected {expected}, got {actual}")
