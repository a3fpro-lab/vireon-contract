import subprocess
from pathlib import Path
import json


def test_capsule_contains_inverse_and_correspondence(tmp_path: Path):
    out = tmp_path / "capsule"
    subprocess.check_call(
        ["vireon", "capsule", "--out", str(out), "--seed", "7", "--steps", "80", "--seed-search-max", "50"]
    )

    cap = json.loads((out / "capsule.json").read_text(encoding="utf-8"))
    fals = {f["name"]: f for f in cap["falsifiers"]}

    assert fals["determinism_same_seed"]["passed"] is True
    assert fals["inverse_seed_recovery"]["passed"] is True
    assert fals["correspondence_seed_matches_spec"]["passed"] is True
