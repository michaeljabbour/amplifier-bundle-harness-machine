# Example: Domain Library Harness
**Scale:** Large (library) — LabClaw-style composable skill library for a scientific domain (genomics).
**Walkthrough:** Spec → Plan → Artifact (Tier 2 bundle), annotated with WHY each decision was made.

---

## SPEC

```
harness_type:  action-verifier
harness_scale: library
target:        An AI lab automation agent orchestrating genomics workflows.
               The agent selects and sequences lab procedures; the harness ensures
               each procedure is applied only when its prerequisites are met and
               safety conditions are satisfied.
```

### Domain Skills (22 across 5 categories)

**Sample Handling (5 skills)**
- `sample-intake` — register incoming specimens, verify chain of custody
- `sample-storage` — assign storage location, check temperature requirements
- `sample-thaw` — enforce controlled thaw protocol before any analysis
- `sample-aliquot` — track volume consumed per aliquot
- `sample-disposal` — require dual confirmation before irreversible disposal

**PCR Protocols (5 skills)**
- `pcr-setup` — validate reagent availability and sample prep completion
- `pcr-thermocycler` — check thermocycler is calibrated and available
- `pcr-gel-electrophoresis` — require PCR completion before gel run
- `pcr-quantification` — require gel confirmation before quantification
- `pcr-result-record` — require quantification before recording final result

**Sequencing Pipeline (4 skills)**
- `library-prep` — require sample aliquot and PCR quantification
- `sequencing-run` — require library prep completion and instrument availability
- `sequencing-demultiplex` — require run completion before demultiplexing
- `sequencing-qc` — require demultiplex before quality control

**Reagent & Equipment (4 skills)**
- `reagent-validation` — check expiry, lot number, storage conditions before use
- `reagent-lot-change` — require protocol update sign-off on lot changes
- `equipment-calibration-check` — verify calibration is current before critical steps
- `equipment-maintenance-flag` — block instrument use if maintenance is overdue

**Safety & Compliance (4 skills)**
- `biosafety-level-check` — verify operator BSL clearance before pathogen work
- `ppe-confirmation` — confirm PPE requirements met before hazardous procedure
- `incident-report` — require incident logging before resuming after any spill/failure
- `chain-of-custody` — enforce documentation at every sample hand-off

### Key Constraint Pattern: Skill Chaining
Skills form a directed acyclic graph (DAG). A skill may only execute if all predecessor skills in its chain have completed for the current sample. Example chain:
```
sample-intake → sample-thaw → pcr-setup → pcr-thermocycler →
pcr-gel-electrophoresis → pcr-quantification → library-prep →
sequencing-run → sequencing-demultiplex → sequencing-qc
```

### Acceptance Criteria
Each nano-amplifier: `is_legal_action()` enforces prerequisites for its skill. No skill executes out of sequence. Safety skills (`biosafety-level-check`, `ppe-confirmation`) block downstream work when not satisfied.

> **Why individual nano-amplifiers per skill, not one monolithic constraints.py?**
> A monolithic file grows to 2,000+ lines, becomes hard to test, and breaks when any one skill changes. Individual nano-amplifiers let you update, test, and redeploy `pcr-setup` without touching `sequencing-run`. Composition via `bundle.md` `includes:` is cheaper than maintaining a single god-file. This is the LabClaw insight: skills are atomic units that compose, not sections of a large policy file.
>
> **Why action-verifier not action-filter for a fixed skill set?**
> Even though the skill names are enumerable, the *invocation context* (which sample ID, which run, which state) is not. The agent must propose which skill to apply to which specimen — that proposal space is infinite. Verification is cheaper than enumeration.

---

## PLAN

**Batch generation strategy:** Generate one nano-amplifier per skill (22 total), then assemble into a Tier 2 bundle.

### Phase 1: Generate shared prerequisite module
Create `modules/prerequisites.py` with:
- `sample_state(sample_id)` — query current workflow state for a sample
- `prerequisites_met(sample_id, skill_name, required_steps)` — check DAG prerequisites
- `safety_cleared(sample_id, safety_checks)` — verify safety preconditions

### Phase 2: Generate per-skill nano-amplifiers (parallel: 5)
For each skill, generate a nano-amplifier with:
- `is_legal_action(board, action)` — checks prerequisites via shared module
- `propose_action(board)` — suggests the skill if prerequisites are met
- `behavior.yaml` — wires the skill's hook
- `context.md` — documents the skill's place in the workflow DAG

### Phase 3: Assemble bundle
Write `bundle.md` with `includes:` for all 22 nano-amplifiers. Wire shared module.

---

## ARTIFACT (Tier 2 Bundle)

### Directory structure

```
genomics-lab-harness/
  bundle.md
  behaviors/
    sample-intake.yaml
    sample-thaw.yaml
    pcr-setup.yaml
    pcr-thermocycler.yaml
    pcr-gel-electrophoresis.yaml
    library-prep.yaml
    sequencing-run.yaml
    biosafety-level-check.yaml
    ... (one per skill)
  modules/
    prerequisites/
      prerequisites.py        # shared prerequisite-checking logic
  context/
    genomics-domain.md        # domain knowledge: PCR, sequencing, biosafety
    skill-dag.md              # the full prerequisite DAG diagram
```

### `bundle.md` (excerpt)

```markdown
## Genomics Lab Harness

Composable constraint library for AI lab automation in genomics workflows.

### Includes
- behaviors/sample-intake.yaml
- behaviors/sample-thaw.yaml
- behaviors/pcr-setup.yaml
- behaviors/pcr-thermocycler.yaml
- behaviors/library-prep.yaml
- behaviors/sequencing-run.yaml
- behaviors/biosafety-level-check.yaml
... (all 22 behaviors)
```

### `behaviors/pcr-setup.yaml` (representative nano-amplifier)

```yaml
bundle:
  name: pcr-setup-harness
  version: 0.1.0
  description: Constrains PCR setup — requires sample thaw completion and reagent validation.

hooks:
  - event: tool:pre
    module: pcr-setup-constraints
    source: ./pcr-setup-constraints.py
    action: deny
    config:
      harness_type: action-verifier
      skill: pcr-setup
      prerequisites: [sample-thaw, reagent-validation]
```

### `modules/prerequisites/prerequisites.py`

```python
"""Shared prerequisite logic for genomics lab harness skills."""
import json


def sample_state(board: str, sample_id: str) -> dict:
    """Extract completed workflow steps for a sample from the board state."""
    try:
        state = json.loads(board)
        return state.get("samples", {}).get(sample_id, {}).get("completed_steps", {})
    except Exception:
        return {}


def prerequisites_met(board: str, sample_id: str, required_steps: list[str]) -> tuple[bool, str]:
    """Return (True, "") if all required steps are completed for the sample."""
    completed = sample_state(board, sample_id)
    missing = [step for step in required_steps if not completed.get(step)]
    if missing:
        return False, f"Prerequisites not met: {missing}"
    return True, ""


def safety_cleared(board: str, sample_id: str, safety_checks: list[str]) -> tuple[bool, str]:
    """Return (True, "") if all safety checks are satisfied for this sample."""
    try:
        state    = json.loads(board)
        cleared  = state.get("safety", {})
        failures = [chk for chk in safety_checks if not cleared.get(chk)]
        if failures:
            return False, f"Safety checks not cleared: {failures}"
        return True, ""
    except Exception:
        return False, "Safety state unavailable — block by default."
```

### `behaviors/pcr-setup-constraints.py` (calls shared module)

```python
"""PCR setup harness: requires sample-thaw and reagent-validation completion."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../modules/prerequisites"))
from prerequisites import prerequisites_met, safety_cleared

PREREQUISITES = ["sample-thaw", "reagent-validation"]
SAFETY_CHECKS = ["biosafety-level-check", "ppe-confirmation"]


def is_legal_action(board: str, action: str) -> bool:
    try:
        act       = json.loads(action)
        sample_id = act.get("sample_id", "")
        ok, _     = prerequisites_met(board, sample_id, PREREQUISITES)
        if not ok:
            return False
        ok, _ = safety_cleared(board, sample_id, SAFETY_CHECKS)
        return ok
    except Exception:
        return False


def validate_action(state: dict, action: dict) -> tuple[bool, str]:
    board = json.dumps(state)
    ok, reason = prerequisites_met(board, action.get("sample_id", ""), PREREQUISITES)
    if not ok:
        return False, reason
    return safety_cleared(board, action.get("sample_id", ""), SAFETY_CHECKS)
```

### `context/genomics-domain.md` (excerpt)

```markdown
## Genomics Lab Domain

**Workflow:** Sample intake → storage → thaw → PCR → gel → quantification →
library prep → sequencing run → demultiplex → QC.

**Safety rules:**
- Biosafety level check must precede ANY work on BSL-2 or higher specimens.
- PPE confirmation required before centrifuge, gel electrophoresis, and sequencing runs.
- No irreversible procedure (disposal, sequencing run) without dual confirmation.

**Skill DAG:** See skill-dag.md for the full prerequisite graph.
```
