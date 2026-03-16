# Future: Factory-Core Extraction from Harness-Machine

**Status:** Planned (not yet started)
**Depends on:** amplifier-bundle-bundlewizard reaching functional parity with harness-machine's process infrastructure

## Context

During the design of `amplifier-bundle-bundlewizard`, we identified that harness-machine's core process infrastructure — the interview pipeline, convergence loop, two-track UX, anti-rationalization enforcement, version stamping, and factory-scale batch generation — is a reusable pattern, not a harness-specific capability.

The decision was made to:
1. Extract the shared factory pattern into `amplifier-bundle-factory-core` (a reusable behavior)
2. Build bundlewizard as the first consumer of factory-core
3. Refactor harness-machine to become a domain skin on top of factory-core

This document tracks the harness-machine refactor (step 3).

## What Gets Extracted to Factory-Core

These are harness-machine capabilities that are **not domain-specific**:

| Current Location | What It Does | Factory-Core Equivalent |
|-----------------|-------------|------------------------|
| Modes pipeline (explore → spec → plan → execute → verify → finish → debug) | Structured interview + generation phases | Abstract pipeline stages with domain-pluggable agents |
| `harness-refinement-loop.yaml` | Convergence loop with patience + checkpoint_best | Generic convergence recipe with configurable evaluation |
| `harness-single-iteration.yaml` | Generate → critique → refine → evaluate cycle | Generic iteration recipe with abstract agent slots |
| `harness-development-cycle.yaml` | Full staged recipe with approval gates | Generic development cycle with configurable stages |
| `harness-factory-generation.yaml` | Foreach over targets with STATE.yaml | Generic batch factory recipe |
| Anti-rationalization tables in modes | Orchestrator never writes output directly | Shared enforcement pattern |
| Version stamping in harness-format.md | Traceability back to generator version | Generic version stamping spec |
| Two-track UX (modes vs recipes) | Hands-on vs automation | Shared UX infrastructure |

## What Stays in Harness-Machine (Domain Skin)

These are **constraint-harness-specific**:

| Capability | Why It's Domain-Specific |
|-----------|------------------------|
| 11 agents (environment-analyst, harness-generator, harness-critic, etc.) | Trained on constraint code, AutoHarness paper methodology |
| Legal Action Rate evaluation | Constraint-specific quality metric |
| Thompson sampling parameters | Tuned for constraint convergence characteristics |
| `hooks-harness` module | Constraint enforcement at runtime |
| `runtime/pico,nano,micro` scaffolds | Constraint agent deployment packages |
| `constraint-spec-template.md` | Bash attack vector categories |
| 3 harness types (action-filter, action-verifier, code-as-policy) | Domain taxonomy |

## Refactor Plan (High-Level)

1. Extract factory-core behavior from harness-machine's working patterns
2. Verify factory-core works with bundlewizard as the test consumer
3. Create `harness-machine-v2` branch
4. Replace harness-machine's bespoke process with factory-core includes
5. Map existing agents to factory-core's abstract agent slots
6. Verify all existing harness-machine recipes still work
7. Run regression: generate a known harness, compare output quality

## Key Constraint

**Do not break a working machine to build the second one.** Harness-machine continues working as-is until factory-core is proven with bundlewizard. The refactor happens only after factory-core has a working consumer.

## Related

- `amplifier-bundle-factory-core` — the shared behavior (to be created)
- `amplifier-bundle-bundlewizard` — first factory-core consumer (to be created)
- Design doc: see bundlewizard design document (to be created during current brainstorm session)
