from pathlib import Path
import subprocess

from vireon_contract.verify import verify_hashes, verify_claim_locked


def test_capsule_hash_and_claim_verify(tmp_path: Path):
    out = tmp_path / "capsule"
    subprocess.check_call(
        ["vireon", "capsule", "--out", str(out), "--seed", "7", "--steps", "80"]
    )
    verify_hashes(out)
    verify_claim_locked(out)
