# src/vireon_contract/verify.py
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    errors: list[str]


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_path_hash_pairs(obj: Any) -> Iterable[tuple[str, str]]:
    """
    Generic extractor: finds dicts like {"path": "...", "sha256": "..."} anywhere in manifest JSON.
    Also supports {"relpath": "...", "sha256": "..."} and {"file": "...", "sha256": "..."}.
    """
    if isinstance(obj, dict):
        keys = set(obj.keys())
        for k in ("path", "relpath", "file"):
            if k in keys and "sha256" in keys and isinstance(obj[k], str) and isinstance(obj["sha256"], str):
                yield (obj[k], obj["sha256"])
        for v in obj.values():
            yield from _iter_path_hash_pairs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_path_hash_pairs(v)


def verify_capsule_dir(capsule_dir: str | Path) -> VerifyResult:
    d = Path(capsule_dir)
    errors: list[str] = []

    manifest = d / "manifest.json"
    lock = d / "capsule.sha256"

    if not d.exists():
        return VerifyResult(False, [f"Capsule dir does not exist: {d}"])
    if not manifest.exists():
        return VerifyResult(False, [f"Missing manifest.json in: {d}"])
    if not lock.exists():
        return VerifyResult(False, [f"Missing capsule.sha256 in: {d}"])

    manifest_bytes = manifest.read_bytes()
    expected_manifest_hash = lock.read_text(encoding="utf-8", errors="ignore").strip()

    got_manifest_hash = _sha256_bytes(manifest_bytes)
    if got_manifest_hash != expected_manifest_hash:
        errors.append(
            f"manifest hash mismatch: got {got_manifest_hash} != expected {expected_manifest_hash}"
        )

    try:
        data = json.loads(manifest_bytes.decode("utf-8"))
    except Exception as e:
        errors.append(f"manifest.json not valid JSON: {e}")
        return VerifyResult(False, errors)

    # Verify every (path, sha256) pair we can find in the manifest.
    seen_any = False
    for rel, h in _iter_path_hash_pairs(data):
        seen_any = True
        p = (d / rel).resolve()
        try:
            p.relative_to(d.resolve())
        except Exception:
            errors.append(f"path escapes capsule dir: {rel}")
            continue
        if not p.exists():
            errors.append(f"missing file referenced by manifest: {rel}")
            continue
        got = _sha256_file(p)
        if got != h:
            errors.append(f"file hash mismatch: {rel}: got {got} != expected {h}")

    # If your manifest doesn’t store artifact hashes yet, this warns you by failing loudly.
    if not seen_any:
        errors.append(
            "manifest contains no embedded (path, sha256) pairs. "
            "Add artifact hashing into manifest so verification proves something."
        )

    return VerifyResult(ok=(len(errors) == 0), errors=errors)
