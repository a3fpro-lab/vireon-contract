# VIREON Contract — Reproducible, Falsifiable Experiment Capsules

This repo is the **canonical kernel** for VIREON-style science.

- **Capsule** = spec + provenance + metrics + falsifiers + artifacts + hashes
- **Hash-locked**: `manifest.json` + `capsule.sha256`
- **Falsification-first**: at least one falsifier is mandatory

The full axiom/law/maths are in **docs/VIREON_CONTRACT.md**.

## Install (dev)
```bash
python -m pip install -U pip
python -m pip install -e . pytest
pytest -q
