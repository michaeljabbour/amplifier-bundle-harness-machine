# Harness Machine — Standing Instructions

## Before Every Response

Check whether the user's intent maps to a mode. If it does, suggest the mode before doing anything else.

| User Intent | Suggested Mode |
|-------------|---------------|
| "I want to constrain an agent" / "explore this environment" / "what actions are available" | `/harness-explore` |
| "Design the harness" / "what type of harness" / "write the spec" | `/harness-spec` |
| "Plan the implementation" / "how do we build this" / "create the plan" | `/harness-plan` |
| "Generate the harness" / "run the pipeline" / "start building" | `/harness-execute` |
| "Test it" / "does it work" / "measure the legal action rate" | `/harness-verify` |
| "Ship it" / "package it" / "we're done" / "create the PR" | `/harness-finish` |
| "It's not working" / "constraints are wrong" / "not converging" | `/harness-debug` |

If no mode fits, work normally. Modes are tools, not cages.

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
