---
bundle:
  name: harness-machine
  version: 0.2.0
  description: |
    Mini-amplifier factory for LLM constraint harness generation.
    Based on the AutoHarness paper (Lou et al., Google DeepMind, 2026).
    Provides 11 agents, 8 modes, 6 recipes, and 3 skills supporting three size
    tiers (pico/nano/micro) with dynamic capability discovery, mission-based
    naming, and three runtime scaffolds.

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: harness-machine:behaviors/harness-machine
---

# Harness Machine

Generate constraint harnesses for LLM agents — from tiny nano-amplifiers to enterprise-scale governance systems.

This bundle is a mini-amplifier factory. It generates pico (≤300 lines), nano (≤600 lines), and micro (≤1200 lines) constraint harnesses with mission-based naming and dynamic capability discovery, each packaged as a ready-to-deploy runtime scaffold.

It provides eleven agents and eight modes that guide you through constraint harness generation:

1. **`/harness-explore`** — Understand the target environment, map the action space, assess feasibility
2. **`/harness-spec`** — Design the harness: type, scale, constraints, acceptance criteria
3. **`/harness-plan`** — Plan the implementation: single harness tasks or factory machine design
4. **`/harness-execute`** — Orchestrate generation via the generator/critic/refiner pipeline
5. **`/harness-verify`** — Evidence-based verification: legal action rate, reward measurement
6. **`/harness-finish`** — Package and deliver: nano-amplifier, bundle, or factory
7. **`/harness-debug`** — Off-ramp: constraint failures, convergence plateaus, search diagnostics

**Two tracks to the same destination:**

| Track | How | Best For |
|-------|-----|----------|
| **Interactive modes** | `/harness-explore` → `/harness-spec` → `/harness-plan` → `/harness-execute` → `/harness-verify` → `/harness-finish` | Hands-on sessions where you want control at each step |
| **Recipe automation** | `harness-development-cycle.yaml` | End-to-end automation with approval gates between stages |

Both tracks produce the same artifact: a constraint harness packaged as a nano-amplifier. Modes give you the steering wheel; recipes give you cruise control.

**Off-ramp at any time:** `/harness-debug` when constraints fail, generation doesn't converge, or evaluation breaks.

## Available Commands

| Command | Purpose | Next Step |
|---------|---------|-----------|
| `/harness-explore` | Understand environment and assess feasibility | `/harness-spec` |
| `/harness-spec` | Design harness specification | `/harness-plan` |
| `/harness-plan` | Create implementation plan | `/harness-execute` |
| `/harness-execute` | Orchestrate harness generation pipeline | `/harness-verify` |
| `/harness-verify` | Collect evidence that harness works | `/harness-finish` or `/harness-debug` |
| `/harness-finish` | Package and deliver the result | Session complete |
| `/harness-debug` | Diagnose constraint or convergence failures | `/harness-verify` |
| `/harness-upgrade` | Check and apply upgrades to existing harnesses | `/harness-verify` |

## Available Agents

| Agent | Purpose |
|-------|---------|
| `harness-machine:environment-analyst` | Explores target environment, maps action space, assesses feasibility; runs dynamic capability discovery |
| `harness-machine:mission-architect` | Creates meaningful name, domain-specific system prompt, README, context docs |
| `harness-machine:capability-advisor` | Recommends tier, tools, provider; produces pre-checked capability picker |
| `harness-machine:spec-writer` | Produces tier-aware harness specification from exploration results |
| `harness-machine:plan-writer` | Creates implementation plan (single harness or factory) |
| `harness-machine:harness-generator` | Generates constraint code and nano-amplifier artifacts |
| `harness-machine:harness-critic` | Reviews harness for coverage gaps and over-constraints |
| `harness-machine:harness-refiner` | Improves harness from critic feedback |
| `harness-machine:harness-evaluator` | Independent measurement of legal action rate and reward |
| `harness-machine:upgrade-checker` | Inspects existing harnesses for version drift and upgrade opportunities |
| `harness-machine:upgrade-planner` | Plans and executes upgrade migrations for existing harnesses |

## Available Recipes

| Recipe | Purpose |
|--------|---------|
| `harness-machine:recipes/harness-development-cycle.yaml` | Full cycle with approval gates (staged) |
| `harness-machine:recipes/harness-refinement-loop.yaml` | Convergence loop with Thompson sampling |
| `harness-machine:recipes/harness-single-iteration.yaml` | One generate/critique/refine/evaluate cycle |
| `harness-machine:recipes/harness-factory-generation.yaml` | Batch generation across environments |
| `harness-machine:recipes/check-upgrade.yaml` | Check existing harness for version drift and upgrade opportunities |
| `harness-machine:recipes/execute-upgrade.yaml` | Plan and execute upgrade migration for existing harness |

## Skills Library

- **harness-reference** — Complete reference tables: modes, agents, recipes, enums
- **constraint-design** — Three constraint layers, composition patterns, common mistakes
- **convergence-debugging** — Thompson sampling, plateau detection, search diagnostics

Use `load_skill(search="harness")` to discover available skills.

---

@foundation:context/shared/common-system-base.md
