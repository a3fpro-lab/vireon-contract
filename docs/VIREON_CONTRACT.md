# VIREON Contract v0.2 — Power Core Spec
**Canonical file.** This is the **axiom + law + math** layer that every VIREON repo must obey.

**Origin:** The Architects (VIREON)  
**Purpose:** Turn *any* computational experiment into a **reproducible, falsifiable, hash-locked truth artifact**.

---

## 0. Prime Directive
A result is **not real** until it is:
1) **Reproducible** (same spec → same artifact, within declared tolerance),  
2) **Falsifiable** (explicit tests that can fail),  
3) **Provenanced** (exact code+deps+platform recorded),  
4) **Hash-locked** (content-addressed integrity),  
5) **Claim-locked** (pre-registered claims hashed into the capsule).

---

## 1. Objects

### 1.1 Experiment
An experiment is a map
$begin:math:display$
\\mathcal\{E\}\:\\ \(\\mathbf\{s\}\,\\omega\)\\ \\mapsto\\ \\mathbf\{a\}
$end:math:display$
- $begin:math:text$\\mathbf\{s\}$end:math:text$ = **Spec** (model, parameters, discretization, boundary conditions, dataset pointers)
- $begin:math:text$\\omega$end:math:text$ = **Stochasticity control** (seed(s), RNG algorithm, nondeterminism knobs)
- $begin:math:text$\\mathbf\{a\}$end:math:text$ = **Artifacts** (files: arrays/images/logs)

### 1.2 Capsule
A **Capsule** is the minimal truth package:
$begin:math:display$
\\mathcal\{C\} \= \(\\mathbf\{s\}\,\\mathbf\{p\}\,\\mathbf\{m\}\,\\mathbf\{f\}\,\\mathbf\{A\}\,\\mathbf\{H\}\,h\_c\)
$end:math:display$
- $begin:math:text$\\mathbf\{s\}$end:math:text$ Spec
- $begin:math:text$\\mathbf\{p\}$end:math:text$ Provenance
- $begin:math:text$\\mathbf\{m\}$end:math:text$ Metrics (contracted observables)
- $begin:math:text$\\mathbf\{f\}$end:math:text$ Falsifiers (tests + verdicts + details)
- $begin:math:text$\\mathbf\{A\}$end:math:text$ Artifacts (paths)
- $begin:math:text$\\mathbf\{H\}$end:math:text$ Hash manifest (sha256 of all capsule contents)
- $begin:math:text$h\_c$end:math:text$ Claim hash (sha256 of canonical `claim.json`)

A capsule is **valid** iff every required axiom and law below is satisfied.

---

## 2. Canonical Axioms (non-negotiable)

### AXIOM A0 — Spec Completeness
The spec must uniquely identify the run.
Formally, the spec $begin:math:text$\\mathbf\{s\}$end:math:text$ must be sufficient to reconstruct the experiment:
$begin:math:display$
\(\\mathbf\{s\}\,\\omega\) \\Rightarrow \\mathbf\{a\}\\ \\ \\text\{\(up to declared tolerance\)\}
$end:math:display$
**Test:** a third party can reproduce without guessing hidden defaults.

---

### AXIOM A1 — Provenance Integrity
Every capsule records:
- git commit SHA (or explicit “UNKNOWN” with a failure flag),
- platform fingerprint,
- python version,
- dependency versions (lock or explicit list).

**Lawful output requires:** $begin:math:text$\\mathbf\{p\}$end:math:text$ present and non-empty.

---

### AXIOM A2 — Falsifiability is Mandatory
Every capsule must include at least one falsifier:
$begin:math:display$
\|\\mathbf\{f\}\| \\ge 1
$end:math:display$
A capsule with zero falsifiers is **invalid**, regardless of pretty plots.

---

### AXIOM A3 — Hash-Locked Reality
Every capsule must be content-addressed:
- A `manifest.json` listing file → sha256(file)
- A `capsule.sha256` equal to sha256(bytes(capsule.json))

If hashes don’t match, the capsule is **not** truth—only a claim.

---

### AXIOM A4 — Metric Contract
Metrics are functions:
$begin:math:display$
m\_i\:\\ \\mathbf\{a\}\\ \\mapsto\\ \\mathbb\{R\}
$end:math:display$
Each metric must provide:
- name,
- numeric value,
- units (or explicit “unitless”),
- notes/definition pointer.

Metrics without definitions are **decorations**, not science.

---

### AXIOM A5 — Declared Tolerances (No Hidden Slack)
If nondeterminism exists, the capsule must declare tolerances:
$begin:math:display$
d\(\\mathbf\{a\}\_1\,\\mathbf\{a\}\_2\) \\le \\tau
$end:math:display$
where $begin:math:text$d$end:math:text$ is a declared distance (L2, PSNR, spectral distance, etc.) and $begin:math:text$\\tau$end:math:text$ is explicit.

No tolerance ⇒ exact match is expected.

---

### AXIOM A6 — Claim-Locked Scoring
Every capsule must be bound to a **pre-registered claim file**:
- capsule must contain `claim.json`
- capsule must include `claim_sha256`
- `claim_sha256` must equal sha256(canonical stable-json bytes of `claim.json`)

If any of those fail, the capsule is invalid.

---

## 3. Core Laws (Power Core format)

Each law has: **Statement → Math → Test → Failure Mode → Enforcement**

---

### LAW §1 — Deterministic Replay (within tolerance)
**Statement:** Same $begin:math:text$\(\\mathbf\{s\}\,\\omega\)$end:math:text$ reproduces.  
**Math:**
$begin:math:display$
\\mathcal\{E\}\(\\mathbf\{s\}\,\\omega\)\=\\mathbf\{a\}\\ \\Rightarrow\\
d\\big\(\\mathcal\{E\}\(\\mathbf\{s\}\,\\omega\)\,\\mathcal\{E\}\(\\mathbf\{s\}\,\\omega\)\\big\)\\le\\tau
$end:math:display$
**Test:** `determinism_same_seed` falsifier.  
**Failure:** nondeterministic drift without declared tolerance.  
**Enforcement:** capsule invalid unless it declares and meets $begin:math:text$\\tau$end:math:text$.

---

### LAW §2 — Perturbation Stability (local robustness)
**Statement:** Small spec perturbations yield bounded metric drift.  
Let $begin:math:text$\\mathbf\{s\}\'\=\\mathbf\{s\}\+\\delta$end:math:text$.  
**Math:**
$begin:math:display$
\|m\_i\(\\mathbf\{a\}\) \- m\_i\(\\mathbf\{a\}\'\)\| \\le \\kappa\_i \\\|\\delta\\\|
$end:math:display$
**Test:** `dt_grid_perturbation` falsifier.  
**Failure:** metrics jump wildly under minor perturbations.  
**Enforcement:** must record drift table and pass declared bounds.

---

### LAW §3 — Cross-Implementation Correspondence
**Statement:** Two independent implementations of the same spec must agree (within tolerance).  
**Math:**
$begin:math:display$
d\\big\(\\mathcal\{E\}\_1\(\\mathbf\{s\}\,\\omega\)\,\\mathcal\{E\}\_2\(\\mathbf\{s\}\,\\omega\)\\big\)\\le\\tau\_\{\\text\{ximpl\}\}
$end:math:display$
**Test:** `cross_impl_equivalence` falsifier.  
**Failure:** “works on my solver.”  
**Enforcement:** must explicitly state attempted/not attempted.

---

### LAW §4 — Evidence Pack Completeness
**Statement:** A capsule must be sufficient for audit.  
**Required files:**
- `capsule.json`
- `capsule.sha256`
- `manifest.json`
- `claim.json`
- `artifacts/` (may be empty, but then must justify)
**Test:** filesystem check + hash verification.  
**Failure:** missing manifest/hashes/claim/artifacts.  
**Enforcement:** CI must fail.

---

### LAW §5 — Pre-Registration of Claims (no moving goalposts)
**Statement:** Claims must be stated before the run is scored.  
Define a claim vector $begin:math:text$\\mathbf\{c\}$end:math:text$.  
**Math:**
$begin:math:display$
\\mathbf\{c\}\\ \\text\{fixed\} \\Rightarrow \\text\{evaluate\}\(\\mathcal\{C\}\)\\ \\text\{without editing\}\\ \\mathbf\{c\}
$end:math:display$
**Test:** `claim_lock` (implemented as A6 + verify).  
**Failure:** changing metrics after seeing outputs.  
**Enforcement:** claim hash is recorded and verified.

---

## 4. TRP + ΔE_store (make it measurable, or delete it)

### 4.1 ΔE_store (canonical)
Define an experiment “energy” functional $begin:math:text$E\(\\cdot\)$end:math:text$ over realized state/artifacts.  
Define a reference value $begin:math:text$E\^\\star$end:math:text$. Then:
$begin:math:display$
\\Delta E\_\{\\text\{store\}\} \:\= E\(x\_\{\\text\{current\}\}\) \- E\^\\star
$end:math:display$
**Rule:** The capsule must state *which* $begin:math:text$E\^\\star$end:math:text$ is used and how obtained.

### 4.2 TRP (canonical control signal)
$begin:math:display$
\\mathrm\{TRP\} \:\= \\frac\{R \\cdot P\}\{T\+\\varepsilon\}
$end:math:display$
If TRP is reported, the capsule must include explicit definitions for $begin:math:text$R\,P\,T\,\\varepsilon$end:math:text$, and the falsifier pass-rate.

---

## 5. Levels of Correspondence (VIREON Canon)
1) **Transformation (Freedom):** $begin:math:text$X \\to Y$end:math:text$  
2) **Definition (Precision):** $begin:math:text$Y \\to X$end:math:text$  
3) **Correspondence (Coherence):** $begin:math:text$X \\leftrightarrow Y$end:math:text$  

A domain that only does (1) is a demo, not a paradigm.

---

## 6. Capsule Schema (canonical JSON shape)
**capsule.json MUST serialize to stable, sorted-key JSON.**

```json
{
  "spec": {
    "domain": "reaction_diffusion",
    "model": "gray_scott",
    "params": { "F": 0.035, "k": 0.062 },
    "discretization": { "dt": 1.0, "steps": 10000, "grid": [256, 256] },
    "init": { "seed": 7, "type": "noise_patch" },
    "boundary": { "type": "periodic" }
  },
  "provenance": {
    "git_sha": "abc123...",
    "platform": "Linux-x86_64",
    "python": "3.11.9",
    "deps": { "numpy": "1.26.4" }
  },
  "metrics": [
    { "name": "spectral_entropy", "value": 1.234, "units": "nats", "notes": "radial PSD entropy" }
  ],
  "falsifiers": [
    {
      "name": "determinism_same_seed",
      "description": "Same seed + spec must match within tau",
      "passed": true,
      "details": { "tau": 0.0, "distance": 0.0 }
    },
    {
      "name": "hash_verification",
      "description": "manifest + capsule.sha256 verify against files",
      "passed": true,
      "details": { "note": "Verified by verifier" }
    },
    {
      "name": "claim_lock",
      "description": "claim.json inside capsule matches claim_sha256",
      "passed": true,
      "details": { "note": "Verified by verifier" }
    }
  ],
  "claim_sha256": "0123abcd...deadbeef",
  "artifacts": {
    "field_u_final": "artifacts/u_final.npy",
    "field_v_final": "artifacts/v_final.npy"
  }
}
