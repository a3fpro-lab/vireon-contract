from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import json


def _stable_json(obj: Any) -> str:
    # Stable JSON for hashing + reproducibility
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Provenance:
    git_sha: str
    platform: str
    python: str
    deps: Dict[str, str]


@dataclass(frozen=True)
class Spec:
    domain: str
    model: str
    params: Dict[str, Any]
    discretization: Dict[str, Any]
    init: Dict[str, Any]
    boundary: Dict[str, Any]


@dataclass(frozen=True)
class Metric:
    name: str
    value: float
    units: str = ""
    notes: str = ""


@dataclass(frozen=True)
class Falsifier:
    name: str
    description: str
    passed: bool
    details: Dict[str, Any]


@dataclass(frozen=True)
class Capsule:
    spec: Spec
    provenance: Provenance
    metrics: List[Metric]
    falsifiers: List[Falsifier]
    claim_sha256: str
    artifacts: Dict[str, str]

    def to_json(self) -> str:
        return _stable_json(asdict(self))
