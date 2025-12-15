# VIREON Contract v0.1 — Power Core Spec
**Canonical file.** This is the **axiom + law + math** layer that every VIREON repo must obey.

**Origin:** The Architects (VIREON)  
**Purpose:** Turn *any* computational experiment into a **reproducible, falsifiable, hash-locked truth artifact**.

---

## 0. Prime Directive
A result is **not real** until it is:
1) **Reproducible** (same spec → same artifact, within declared tolerance),  
2) **Falsifiable** (explicit tests that can fail),  
3) **Provenanced** (exact code+deps+platform recorded),  
4) **Hash-locked** (content-addressed integrity).

---

## 1. Objects
### 1.1 Experiment
An experiment is a map
\[
\mathcal{E}:\ (\mathbf{s},\omega)\ \mapsto\ \mathbf{a}
\]
- \(\mathbf{s}\) = **Spec** (model, parameters, discretization, boundary conditions, dataset pointers)
- \(\omega\) = **Stochasticity control** (seed(s), RNG algorithm, nondeterminism knobs)
- \(\mathbf{a}\) = **Artifacts** (files: arrays/images/logs)

### 1.2 Capsule
A **Capsule** is the minimal truth package:
\[
\mathcal{C} = (\mathbf{s},\mathbf{p},\mathbf{m},\mathbf{f},\mathbf{A},\mathbf{H})
\]
- \(\mathbf{s}\) Spec
- \(\mathbf{p}\) Provenance
- \(\mathbf{m}\) Metrics (contracted observables)
- \(\mathbf{f}\) Falsifiers (tests + verdicts + details)
- \(\mathbf{A}\) Artifacts (paths)
- \(\mathbf{H}\) Hash manifest (sha256 of all capsule contents)

A capsule is **valid** iff every required axiom and law below is satisfied.

---

## 2. Canonical Axioms (non-negotiable)

### AXIOM A0 — Spec Completeness
The spec must uniquely identify the run.
Formally, the spec \(\mathbf{s}\) must be sufficient to reconstruct the experiment:
\[
(\mathbf{s},\omega) \Rightarrow \mathbf{a}\ \ \text{(up to declared tolerance)}
\]
**Test:** a third party can reproduce without guessing hidden defaults.

---

### AXIOM A1 — Provenance Integrity
Every capsule records:
- git commit SHA (or explicit “UNKNOWN” with a failure flag),
- platform fingerprint,
- python version,
- dependency versions (lock or explicit list).

**Lawful output requires:** \(\mathbf{p}\) present and non-empty.

---

### AXIOM A2 — Falsifiability is Mandatory
Every capsule must include at least one falsifier:
\[
|\mathbf{f}| \ge 1
\]
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
\[
m_i:\ \mathbf{a}\ \mapsto\ \mathbb{R}
\]
Each metric must provide:
- name,
- numeric value,
- units (or explicit “unitless”),
- notes/definition pointer.

Metrics without definitions are **decorations**, not science.

---

### AXIOM A5 — Declared Tolerances (No Hidden Slack)
If nondeterminism exists, the capsule must declare tolerances:
\[
d(\mathbf{a}_1,\mathbf{a}_2) \le \tau
\]
where \(d\) is a declared distance (L2, PSNR, spectral distance, etc.) and \(\tau\) is explicit.

No tolerance ⇒ exact match is expected.

---

## 3. Core Laws (Power Core format)

Each law has: **Statement → Math → Test → Failure Mode → Enforcement**

---

### LAW §1 — Deterministic Replay (within tolerance)
**Statement:** Same \((\mathbf{s},\omega)\) reproduces.
**Math:**
\[
\mathcal{E}(\mathbf{s},\omega)=\mathbf{a}\ \Rightarrow\
d\big(\mathcal{E}(\mathbf{s},\omega),\mathcal{E}(\mathbf{s},\omega)\big)\le\tau
\]
**Test:** `determinism_same_seed` falsifier.
**Failure:** nondeterministic drift without declared tolerance.
**Enforcement:** capsule invalid unless it declares and meets \(\tau\).

---

### LAW §2 — Perturbation Stability (local robustness)
**Statement:** Small spec perturbations yield bounded metric drift.
Let \(\mathbf{s}'=\mathbf{s}+\delta\) (e.g., dt tweak, grid tweak).
**Math:**
\[
|m_i(\mathbf{a}) - m_i(\mathbf{a}')| \le \kappa_i \|\delta\| \quad \text{(declared bound)}
\]
**Test:** `dt_grid_perturbation` falsifier runs a controlled delta suite.
**Failure:** metrics jump wildly under minor perturbations.
**Enforcement:** must record drift table and pass declared bounds.

---

### LAW §3 — Cross-Implementation Correspondence
**Statement:** Two independent implementations of the same spec must agree (within tolerance).
Let \(\mathcal{E}_1,\mathcal{E}_2\) be two solvers.
**Math:**
\[
d\big(\mathcal{E}_1(\mathbf{s},\omega),\mathcal{E}_2(\mathbf{s},\omega)\big)\le\tau_{\text{ximpl}}
\]
**Test:** `cross_impl_equivalence` falsifier.
**Failure:** “works on my solver.”
**Enforcement:** capsule must state whether cross-impl was attempted; “not attempted” is allowed only in v0.* with an explicit flag.

---

### LAW §4 — Evidence Pack Completeness
**Statement:** A capsule must be sufficient for audit.
**Required files:**
- `capsule.json`
- `capsule.sha256`
- `manifest.json`
- `artifacts/` (may be empty, but then must justify)
**Test:** filesystem check + hash verification.
**Failure:** missing manifest/hashes/artifacts.
**Enforcement:** CI must fail.

---

### LAW §5 — Pre-Registration of Claims (no moving goalposts)
**Statement:** Claims must be stated before the run is scored.
Define a claim vector \(\mathbf{c}\) (targets, thresholds, falsifiers).
**Math:**
\[
\mathbf{c}\ \text{fixed} \Rightarrow \text{evaluate}(\mathcal{C})\ \text{without editing}\ \mathbf{c}
\]
**Test:** `claim_lock` falsifier ensures claim spec hash is recorded.
**Failure:** changing metrics after seeing outputs.
**Enforcement:** store claim hash in capsule.

---

## 4. TRP + ΔE_store (make it measurable, or delete it)

### 4.1 ΔE_store (canonical)
We define an experiment “energy” functional \(E(\cdot)\) over the realized state/artifacts.
- \(x\) = state (field configuration, parameter estimate, model weights, etc.)
- \(E(x)\) = a computable scalar from artifacts

Define the **reference / attractor** value \(E^\star\) as one of:
- known ground truth optimum,
- certified lower bound,
- equilibrium free energy,
- best-known baseline under fixed budget.

Then:
\[
\Delta E_{\text{store}} := E(x_{\text{current}}) - E^\star \ge 0\ \ \text{(by definition if }E^\star=\inf E\text{)}
\]

**Rule:** The capsule must state *which* \(E^\star\) is used and how it’s obtained.

### 4.2 TRP (canonical control signal)
TRP is a **rate of verified progress per resource**:
\[
\mathrm{TRP} := \frac{R \cdot P}{T+\varepsilon}
\]
- \(R\) = Result magnitude (measurable improvement, e.g. \(\Delta E_{\text{store}}\) reduction or metric gain)
- \(P\) = Product / robustness factor (penalize fragility under falsifiers; e.g. pass-rate weighted)
- \(T\) = time/compute budget
- \(\varepsilon>0\) = stability constant (declared)

**Minimal instantiation (v0.1):**
Let \(R = \Delta E_{\text{store}}^{\text{before}} - \Delta E_{\text{store}}^{\text{after}}\).
Let \(P = \frac{1}{|\mathbf{f}|}\sum_j \mathbf{1}\{f_j=\text{pass}\}\).
Then:
\[
\mathrm{TRP} = \frac{\left(\Delta E_{\text{store}}^{\text{before}} - \Delta E_{\text{store}}^{\text{after}}\right)\cdot \left(\frac{\#\text{passes}}{\#\text{falsifiers}}\right)}{T+\varepsilon}
\]

**Hard rule:** If TRP is reported, the capsule must include:
- explicit \(E(\cdot)\),
- explicit \(E^\star\),
- explicit \(T\) (wall time, FLOPs proxy, steps, etc.),
- falsifier pass-rate \(P\).

No definitions → TRP is forbidden.

---

## 5. Levels of Correspondence (VIREON Canon)
Every domain must expose three linked layers:

1) **Transformation (Freedom):** \(X \to Y\) — forward generation  
2) **Definition (Precision):** \(Y \to X\) — inverse reconstruction  
3) **Correspondence (Coherence):** \(X \leftrightarrow Y\) — mutual agreement under falsifiers

In capsule terms:
- Transformation = produce artifacts \(\mathbf{a}\) from spec
- Definition = infer spec/params from partial artifacts
- Correspondence = cross-impl + perturbation stability + invariance tests

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
    { "name": "determinism_same_seed",
      "description": "Same seed + spec must match within tau",
      "passed": true,
      "details": { "tau": 0.0, "distance": 0.0 }
    }
  ],
  "artifacts": {
    "field_u_final": "artifacts/u_final.npy",
    "field_v_final": "artifacts/v_final.npy"
  }
}

# VIREON Contract v0.1 — Power Core Spec
**Canonical file.** This is the **axiom + law + math** layer that every VIREON repo must obey.

**Origin:** The Architects (VIREON)  
**Purpose:** Turn *any* computational experiment into a **reproducible, falsifiable, hash-locked truth artifact**.

---

## 0. Prime Directive
A result is **not real** until it is:
1) **Reproducible** (same spec → same artifact, within declared tolerance),  
2) **Falsifiable** (explicit tests that can fail),  
3) **Provenanced** (exact code+deps+platform recorded),  
4) **Hash-locked** (content-addressed integrity).

---

## 1. Objects
### 1.1 Experiment
An experiment is a map
\[
\mathcal{E}:\ (\mathbf{s},\omega)\ \mapsto\ \mathbf{a}
\]
- \(\mathbf{s}\) = **Spec** (model, parameters, discretization, boundary conditions, dataset pointers)
- \(\omega\) = **Stochasticity control** (seed(s), RNG algorithm, nondeterminism knobs)
- \(\mathbf{a}\) = **Artifacts** (files: arrays/images/logs)

### 1.2 Capsule
A **Capsule** is the minimal truth package:
\[
\mathcal{C} = (\mathbf{s},\mathbf{p},\mathbf{m},\mathbf{f},\mathbf{A},\mathbf{H})
\]
- \(\mathbf{s}\) Spec
- \(\mathbf{p}\) Provenance
- \(\mathbf{m}\) Metrics (contracted observables)
- \(\mathbf{f}\) Falsifiers (tests + verdicts + details)
- \(\mathbf{A}\) Artifacts (paths)
- \(\mathbf{H}\) Hash manifest (sha256 of all capsule contents)

A capsule is **valid** iff every required axiom and law below is satisfied.

---

## 2. Canonical Axioms (non-negotiable)

### AXIOM A0 — Spec Completeness
The spec must uniquely identify the run.
Formally, the spec \(\mathbf{s}\) must be sufficient to reconstruct the experiment:
\[
(\mathbf{s},\omega) \Rightarrow \mathbf{a}\ \ \text{(up to declared tolerance)}
\]
**Test:** a third party can reproduce without guessing hidden defaults.

---

### AXIOM A1 — Provenance Integrity
Every capsule records:
- git commit SHA (or explicit “UNKNOWN” with a failure flag),
- platform fingerprint,
- python version,
- dependency versions (lock or explicit list).

**Lawful output requires:** \(\mathbf{p}\) present and non-empty.

---

### AXIOM A2 — Falsifiability is Mandatory
Every capsule must include at least one falsifier:
\[
|\mathbf{f}| \ge 1
\]
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
\[
m_i:\ \mathbf{a}\ \mapsto\ \mathbb{R}
\]
Each metric must provide:
- name,
- numeric value,
- units (or explicit “unitless”),
- notes/definition pointer.

Metrics without definitions are **decorations**, not science.

---

### AXIOM A5 — Declared Tolerances (No Hidden Slack)
If nondeterminism exists, the capsule must declare tolerances:
\[
d(\mathbf{a}_1,\mathbf{a}_2) \le \tau
\]
where \(d\) is a declared distance (L2, PSNR, spectral distance, etc.) and \(\tau\) is explicit.

No tolerance ⇒ exact match is expected.

---

## 3. Core Laws (Power Core format)

Each law has: **Statement → Math → Test → Failure Mode → Enforcement**

---

### LAW §1 — Deterministic Replay (within tolerance)
**Statement:** Same \((\mathbf{s},\omega)\) reproduces.
**Math:**
\[
\mathcal{E}(\mathbf{s},\omega)=\mathbf{a}\ \Rightarrow\
d\big(\mathcal{E}(\mathbf{s},\omega),\mathcal{E}(\mathbf{s},\omega)\big)\le\tau
\]
**Test:** `determinism_same_seed` falsifier.
**Failure:** nondeterministic drift without declared tolerance.
**Enforcement:** capsule invalid unless it declares and meets \(\tau\).

---

### LAW §2 — Perturbation Stability (local robustness)
**Statement:** Small spec perturbations yield bounded metric drift.
Let \(\mathbf{s}'=\mathbf{s}+\delta\) (e.g., dt tweak, grid tweak).
**Math:**
\[
|m_i(\mathbf{a}) - m_i(\mathbf{a}')| \le \kappa_i \|\delta\| \quad \text{(declared bound)}
\]
**Test:** `dt_grid_perturbation` falsifier runs a controlled delta suite.
**Failure:** metrics jump wildly under minor perturbations.
**Enforcement:** must record drift table and pass declared bounds.

---

### LAW §3 — Cross-Implementation Correspondence
**Statement:** Two independent implementations of the same spec must agree (within tolerance).
Let \(\mathcal{E}_1,\mathcal{E}_2\) be two solvers.
**Math:**
\[
d\big(\mathcal{E}_1(\mathbf{s},\omega),\mathcal{E}_2(\mathbf{s},\omega)\big)\le\tau_{\text{ximpl}}
\]
**Test:** `cross_impl_equivalence` falsifier.
**Failure:** “works on my solver.”
**Enforcement:** capsule must state whether cross-impl was attempted; “not attempted” is allowed only in v0.* with an explicit flag.

---

### LAW §4 — Evidence Pack Completeness
**Statement:** A capsule must be sufficient for audit.
**Required files:**
- `capsule.json`
- `capsule.sha256`
- `manifest.json`
- `artifacts/` (may be empty, but then must justify)
**Test:** filesystem check + hash verification.
**Failure:** missing manifest/hashes/artifacts.
**Enforcement:** CI must fail.

---

### LAW §5 — Pre-Registration of Claims (no moving goalposts)
**Statement:** Claims must be stated before the run is scored.
Define a claim vector \(\mathbf{c}\) (targets, thresholds, falsifiers).
**Math:**
\[
\mathbf{c}\ \text{fixed} \Rightarrow \text{evaluate}(\mathcal{C})\ \text{without editing}\ \mathbf{c}
\]
**Test:** `claim_lock` falsifier ensures claim spec hash is recorded.
**Failure:** changing metrics after seeing outputs.
**Enforcement:** store claim hash in capsule.

---

## 4. TRP + ΔE_store (make it measurable, or delete it)

### 4.1 ΔE_store (canonical)
We define an experiment “energy” functional \(E(\cdot)\) over the realized state/artifacts.
- \(x\) = state (field configuration, parameter estimate, model weights, etc.)
- \(E(x)\) = a computable scalar from artifacts

Define the **reference / attractor** value \(E^\star\) as one of:
- known ground truth optimum,
- certified lower bound,
- equilibrium free energy,
- best-known baseline under fixed budget.

Then:
\[
\Delta E_{\text{store}} := E(x_{\text{current}}) - E^\star \ge 0\ \ \text{(by definition if }E^\star=\inf E\text{)}
\]

**Rule:** The capsule must state *which* \(E^\star\) is used and how it’s obtained.

### 4.2 TRP (canonical control signal)
TRP is a **rate of verified progress per resource**:
\[
\mathrm{TRP} := \frac{R \cdot P}{T+\varepsilon}
\]
- \(R\) = Result magnitude (measurable improvement, e.g. \(\Delta E_{\text{store}}\) reduction or metric gain)
- \(P\) = Product / robustness factor (penalize fragility under falsifiers; e.g. pass-rate weighted)
- \(T\) = time/compute budget
- \(\varepsilon>0\) = stability constant (declared)

**Minimal instantiation (v0.1):**
Let \(R = \Delta E_{\text{store}}^{\text{before}} - \Delta E_{\text{store}}^{\text{after}}\).
Let \(P = \frac{1}{|\mathbf{f}|}\sum_j \mathbf{1}\{f_j=\text{pass}\}\).
Then:
\[
\mathrm{TRP} = \frac{\left(\Delta E_{\text{store}}^{\text{before}} - \Delta E_{\text{store}}^{\text{after}}\right)\cdot \left(\frac{\#\text{passes}}{\#\text{falsifiers}}\right)}{T+\varepsilon}
\]

**Hard rule:** If TRP is reported, the capsule must include:
- explicit \(E(\cdot)\),
- explicit \(E^\star\),
- explicit \(T\) (wall time, FLOPs proxy, steps, etc.),
- falsifier pass-rate \(P\).

No definitions → TRP is forbidden.

---

## 5. Levels of Correspondence (VIREON Canon)
Every domain must expose three linked layers:

1) **Transformation (Freedom):** \(X \to Y\) — forward generation  
2) **Definition (Precision):** \(Y \to X\) — inverse reconstruction  
3) **Correspondence (Coherence):** \(X \leftrightarrow Y\) — mutual agreement under falsifiers

In capsule terms:
- Transformation = produce artifacts \(\mathbf{a}\) from spec
- Definition = infer spec/params from partial artifacts
- Correspondence = cross-impl + perturbation stability + invariance tests

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
    { "name": "determinism_same_seed",
      "description": "Same seed + spec must match within tau",
      "passed": true,
      "details": { "tau": 0.0, "distance": 0.0 }
    }
  ],
  "artifacts": {
    "field_u_final": "artifacts/u_final.npy",
    "field_v_final": "artifacts/v_final.npy"
  }
}

7. Required Falsifiers (v0.1 baseline)

Every domain must implement at least one; RD domains should implement all three:
	1.	determinism_same_seed
	2.	dt_grid_perturbation
	3.	hash_verification (manifest + capsule hash)

Optional but strong:
	•	cross_impl_equivalence
	•	noise_injection_robustness
	•	boundary_condition_flip
	•	precision_mode_compare (fp32 vs fp64)

⸻

8. Evidence Pack Layout (canonical)

results/<run_id>/
  capsule.json
  capsule.sha256
  manifest.json
  artifacts/
    ...files...

CI must:
	•	build capsule,
	•	verify hashes,
	•	publish artifact bundle.

⸻

9. What “canonical” means

If a VIREON repo produces results without producing capsules obeying this file, those results are non-canonical and must be treated as exploratory.

Canonical = auditable = falsifiable = hash-locked.

⸻

10. Absolute Rule: No Mysticism in the Math Layer

Names like “TRP” and “ΔE_store” are allowed only if they are:
	•	defined as computable functions,
	•	accompanied by falsifiers,
	•	reproducible under a declared tolerance.

Otherwise: delete them.

⸻

11. Minimal TODO to go from v0.1 → v0.2 (the real ground-break)
	•	Add claim pre-registration file claim.json hashed into capsule
	•	Add cross-impl correspondence harness
	•	Add inverse problem and control tasks to force Levels-of-Correspondence completeness

That is where the paradigm shift becomes visible.

⸻

END OF CANONICAL FILE


