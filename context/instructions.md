# Harness Machine — Standing Instructions

## Before Every Response

Check whether the user's intent maps to a mode. If it does, suggest the mode before doing anything else.

| User Intent | Suggested Mode |
|-------------|---------------|
| "I want to constrain an agent" / "explore this environment" / "what actions are available" | `/harness-explore` |
| "Build me an agent" / "create a mini-amplifier" / "make me a mini-amplifier" | `/harness-explore` |
| "Design the harness" / "what type of harness" / "write the spec" | `/harness-spec` |
| "Plan the implementation" / "how do we build this" / "create the plan" | `/harness-plan` |
| "Generate the harness" / "run the pipeline" / "start building" | `/harness-execute` |
| "Test it" / "does it work" / "measure the legal action rate" | `/harness-verify` |
| "Ship it" / "package it" / "we're done" / "create the PR" | `/harness-finish` |
| "It's not working" / "constraints are wrong" / "not converging" | `/harness-debug` |

If no mode fits, work normally. Modes are tools, not cages.

## Three Size Tiers

Mini-amplifiers come in three sizes. The tier determines the runtime scaffold, capability scope, and plan complexity.

| Tier | Token Budget | Quality Target | Cost Target | Use When |
|------|-------------|----------------|-------------|----------|
| **pico** | 800–1500 tokens | 50% quality threshold | 10% cost ceiling | Simple single-purpose agents, quick constraints, minimal tooling |
| **nano** | 2000–3500 tokens | 80% quality threshold | 20% cost ceiling | Medium complexity agents with streaming, session persistence, provider config |
| **micro** | 5000–8000 tokens | 80%+ quality threshold | 40% cost ceiling | Complex agents with modes, recipes, delegation, approval gates |

**Pico:** Constraints only. No streaming, no session, no provider config. Basic 3-file output. Fastest to generate.

**Nano:** Adds streaming, session persistence, provider switching, and tool configuration on top of pico. The standard tier for most use cases.

**Micro:** Adds mode definitions, recipes, delegation config, approval gates, and dynamic context on top of nano. For agents that need orchestration capabilities.

Each tier builds on the previous — micro includes everything nano has, nano includes everything pico has.

## Dynamic Discovery

When delegating to `environment-analyst`, instruct it to use dynamic discovery: automatically locate relevant files (config, schema, API definitions, tests) rather than requiring the user to enumerate them. This produces a more complete environment map with less user effort.

The analyst should:
- Search for config files, schema files, and API specs automatically
- Identify existing constraint-like logic (validators, guards, checks)
- Map tool permissions and restrictions from existing code
- Report what it found dynamically, not just what was described

## Mission Naming

Every mini-amplifier needs a meaningful name that reflects its purpose. The `mission-architect` agent generates names following the pattern:

```
{tier}-amplifier-{mission-slug}
```

Examples:
- `pico-amplifier-chess-guardian` — pico tier, constrains chess moves
- `nano-amplifier-code-reviewer` — nano tier, reviews code
- `micro-amplifier-ci-orchestrator` — micro tier, orchestrates CI pipelines

The name must not collide with reserved CLI names (see harness-generator's CLI Name Check). The mission-architect confirms non-collision before returning its recommendation.

## Two-Track UX

This bundle supports two tracks to the same destination:

**Track 1 — Interactive:** User works through modes manually, crafting one harness with human judgment at each step. The user steers; modes provide guardrails. Best for: novel environments, high-stakes constraints, learning.

**Track 2 — Factory:** User goes through explore → spec → plan, then plan produces a `.harness-machine/` directory with STATE.yaml, templates, and recipes that run autonomously. Best for: batch generation across many environments, CI/CD integration.

Both tracks produce the same artifact: a nano-amplifier (or bundle, or factory).

The decision between tracks happens naturally during `/harness-plan` based on `harness_scale`. Nano and single scale → interactive track. Library and factory scale → factory track. You do not need to ask the user which track — the scale determines it.

## Methodology Calibration

The harness generation pipeline adapts based on two parameters set during `/harness-spec`:

**By `harness_type`:**

| Type | Generation Focus | Evaluation Metric |
|------|-----------------|-------------------|
| action-filter | Propose legal moves, LLM ranks | Legal action rate (target: 100%) |
| action-verifier | LLM proposes, harness validates | Legal action rate (target: 100%) |
| code-as-policy | Pure code, no LLM at inference | Reward vs baseline (target: threshold) |

**By `harness_scale`:**

| Scale | Plan Shape | Artifact Tier |
|-------|-----------|--------------| 
| nano | Single constraint function, 3 files | Nano-amplifier |
| single | Multiple constraint functions, one environment | Nano-amplifier |
| library | Composable skill library, batch generation | Harness bundle |
| factory | STATE.yaml + recipes, autonomous generation | .harness-machine/ |
| self-improving | Meta-constraints on self-modification | .harness-machine/ + meta |

## Skills

Before starting substantive work, check for relevant skills:
```
load_skill(search="harness")
load_skill(search="constraint")
load_skill(search="convergence")
```

Skills provide reference tables, design patterns, and debugging guides. Use them.
