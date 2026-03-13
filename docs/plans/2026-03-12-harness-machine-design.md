# Harness Machine Design

## Goal

Build `amplifier-bundle-harness-machine` — a single Amplifier bundle that enables both interactive crafting and autonomous factory generation of constraint harnesses for LLM agents, from tiny nano-amplifiers to enterprise-scale governance systems.

## Background

### The Research Foundation

The AutoHarness paper (Lou et al., Google DeepMind, 2026, arXiv:2603.03329v1) proved that LLMs can automatically generate constraint code achieving 100% legal action rates across 145 games, with a smaller model + harness outperforming larger models without one.

The paper demonstrates three harness types:

1. **Action Filter** — harness proposes legal moves, LLM ranks them
2. **Action Verifier** — LLM proposes, harness validates, retry if illegal (primary focus)
3. **Code-as-Policy** — pure code chooses the action, no LLM at inference time ($0 cost)

The generation mechanism is tree search over program space with Thompson sampling, using a Critic/Refiner/Evaluator loop. Average convergence: 14.5 iterations for action-verifier, 89.4 for code-as-policy. Heavy-tailed distribution — most games converge in under 10 iterations, but outliers like Chess-v0 take 60+.

Two core function signatures from the paper:

```python
def propose_action(board: str) -> str:
    """Propose a valid action given the game board as text."""

def is_legal_action(board: str, action: str) -> bool:
    """Check if an action string is valid given the game board as text."""
```

### The Amplifier Connection

Amplifier's existing primitives map directly to harness concepts:

| Amplifier Primitive | Harness Concept |
|---|---|
| Hook system (tool:pre deny/modify, provider:request inject_context) | Harness enforcement |
| HookResult actions (deny, modify, inject_context, continue) | Harness decision vocabulary |
| Ephemeral context injection | Per-turn state description without history bloat |
| Bundle behavior pattern | Harness packaging and composition |
| Recipe system with while_condition | Convergence loops |
| Multi-agent delegation | Critic/Refiner/Evaluator roles |

Zero kernel changes required. The harness is pure module-level policy using existing kernel mechanisms.

### The Claw Ecosystem

The bundle draws domain knowledge from four constraint architectures:

- **OpenClaw**: SKILL.md-based behavioral constraints (soft constraints)
- **NanoClaw**: OS-level container isolation (hard constraints, ~3,900 lines, security-first)
- **NemoClaw**: NVIDIA enterprise guardrails with Colang DSL (programmatic policy constraints)
- **LabClaw**: 206+ composable domain-specific skills for scientific lab automation

### Structural Lineage

The bundle draws structural patterns from two proven Amplifier bundles:

- **amplifier-bundle-superpowers**: interactive mode-driven workflow (brainstorm, plan, execute, verify, finish)
- **amplifier-bundle-dev-machine**: autonomous machine factory (admissions, design, generate, run)

## Approach

**Unified bundle with both superpowers-style interactive modes AND dev-machine-style factory generation.** One bundle, one namespace (`harness-machine:`), two UX tracks. The interactive-vs-factory decision is a planning question within the pipeline, not a workflow fork.

The bundle is pure configuration — zero Python application code — following the dev-machine pattern. All content is markdown, YAML, and agent instructions.

## Architecture

### Seven-Mode Pipeline

```
/harness-explore --> /harness-spec --> /harness-plan --> /harness-execute --> /harness-verify --> /harness-finish
                                                               ^
                                                               |
                                                        /harness-debug
```

### Two-Track UX

**Track 1 — Interactive:** User works through modes manually, crafting one harness with human judgment at each step. Same feel as superpowers brainstorm, write-plan, execute-plan, verify, finish.

**Track 2 — Factory:** User goes through explore, spec, plan, then plan produces a `.harness-machine/` directory with STATE.yaml, templates, and recipes that run autonomously to generate harnesses across many environments. Same pattern as dev-machine's `/generate-machine`.

Both tracks produce the same artifact: a nano-amplifier.

## Components

### Modes

#### /harness-explore (Merges brainstorm + admissions)

Understand the target environment(s) and assess feasibility. Interactive dialogue: what actions exist? What is legal vs illegal? Can constraints be defined? Can legality be evaluated automatically?

**Feasibility gate:** Not every environment can be harnessed. If the action space is too ambiguous or verification is purely subjective, stop here.

**Pattern:** Hybrid — main agent owns the conversation, environment-analyst agent does the investigation work.

**Output:** Environment map + feasibility assessment.

| Tool | Permission |
|---|---|
| read_file | safe |
| bash | warn |
| write_file / edit_file | blocked |

**Allowed transitions:** harness-spec, harness-debug.

---

#### /harness-spec (Design the harness)

Takes the environment map and produces a concrete harness specification. Key fields:

- `harness_type`: action-filter, action-verifier, or code-as-policy
- `harness_scale`: nano, single, library, factory, or self-improving
- Constraint list with rationale for each
- Legal action space definition
- Acceptance criteria (legal action rate target, reward threshold for policy type)
- Target environment description

The `harness_type` and `harness_scale` flow through every downstream mode, parametrizing behavior.

**Pattern:** Hybrid — main agent presents sections for validation, spec-writer agent creates the document.

**Output:** `docs/plans/YYYY-MM-DD-<name>-harness-spec.md`

| Tool | Permission |
|---|---|
| read_file | safe |
| bash | warn |
| write_file / edit_file | blocked |

**Allowed transitions:** harness-plan, harness-explore, harness-debug.

---

#### /harness-plan (Plan the implementation)

Takes the spec and produces a concrete plan. The `harness_scale` determines the plan shape:

- **nano / single:** Which constraint functions to write, what test environments, acceptance criteria, TDD tasks.
- **library:** Which domain skills to constrain, composition strategy, batch generation plan.
- **factory:** STATE.yaml schema, iteration recipe design, templates to stamp out, environment list.
- **self-improving:** Meta-constraint boundaries, convergence loop design, self-modification limits.

**Pattern:** Hybrid — main agent discusses structure, plan-writer agent creates the document.

**Output:** `docs/plans/YYYY-MM-DD-<name>-harness-plan.md`

| Tool | Permission |
|---|---|
| read_file | safe |
| bash | warn |
| write_file / edit_file | blocked |

**Allowed transitions:** harness-execute, harness-spec, harness-debug.

---

#### /harness-execute (Orchestrator-only)

Main agent dispatches agents, never writes files directly. Two paths based on plan:

**For single harness generation:** Dispatches the three-agent pipeline:

1. harness-generator produces constraint code
2. harness-critic reviews for coverage gaps, over-constraints, edge cases
3. harness-refiner improves based on critic feedback

This is ONE iteration. The convergence loop (tree search + Thompson sampling) lives in a recipe (`harness-refinement-loop.yaml`) that calls this pipeline repeatedly.

**For factory stamping:** Dispatches machine-generator agent to stamp out `.harness-machine/` from templates.

| Tool | Permission |
|---|---|
| read_file | safe |
| delegate | safe |
| recipes | safe |
| bash | warn |
| write_file / edit_file | blocked |

**Allowed transitions:** harness-verify, harness-debug, harness-spec, harness-plan.

---

#### /harness-verify (Evidence-based)

Run the generated harness against the target environment. The verification protocol depends on `harness_type`:

- **action-verifier:** Novel test rollouts (10 random seeds, 1000 steps), measure legal action rate. Target: 100%.
- **code-as-policy:** Reward measurement vs baseline agents. Target: H >= threshold.
- **factory:** Verify `.harness-machine/` runs, STATE.yaml valid, recipes parse.

The Gate Function applies: IDENTIFY, RUN, READ, VERIFY, CLAIM. No claims without fresh evidence.

| Tool | Permission |
|---|---|
| read_file | safe |
| bash | safe |
| delegate | warn (cannot delegate verification claims) |
| write_file / edit_file | warn |

**Allowed transitions:** harness-finish, harness-debug, harness-execute, harness-spec, harness-plan.

---

#### /harness-finish (Ship the result)

Package and deliver:

- **Single harness:** Package as nano-amplifier directory, commit, present 4 options (merge / PR / keep / discard).
- **Factory:** Verify `.harness-machine/` is complete, present Docker/cron startup instructions, same 4 options.

| Tool | Permission |
|---|---|
| read_file | safe |
| bash | safe |
| delegate | safe |
| write_file / edit_file | warn |

**Allowed transitions:** harness-execute, harness-explore. `allow_clear: true` (only mode that can exit).

---

#### /harness-debug (Off-ramp from any mode)

Systematic debugging for harness-specific problems:

- Why is the harness allowing illegal actions? (constraint gap)
- Why is generation not converging? (plateau detection, Thompson sampling stuck)
- Why is evaluation failing? (environment adapter issue)
- Is the search stuck in a local optimum? (exploration vs exploitation)

**Process:** 4-phase — investigate, analyze, hypothesize, fix via delegation.

**Plateau detection:** If heuristic is flat for 10+ iterations, diagnose search strategy not just code.

| Tool | Permission |
|---|---|
| read_file | safe |
| bash | safe |
| delegate | safe |
| write_file / edit_file | blocked |

**Allowed transitions:** harness-verify, harness-explore, harness-execute.

### Agents

Seven agents, each with a single clear role:

| Agent | Role | Model Role | Used In |
|---|---|---|---|
| environment-analyst | Explores target, maps action space, assesses feasibility | research, general | /harness-explore |
| spec-writer | Produces harness specification from exploration | reasoning, general | /harness-spec |
| plan-writer | Creates implementation plan (single or factory) | reasoning, general | /harness-plan |
| harness-generator | Generates constraint code + nano-amplifier artifacts | coding, general | /harness-execute |
| harness-critic | Reviews harness: coverage gaps, over-constraints, edge cases | critique, reasoning, general | /harness-execute |
| harness-refiner | Improves harness from critic feedback (LLM as mutation operator) | coding, general | /harness-execute |
| harness-evaluator | Independent measurement: legal action rate, reward | critique, reasoning, general | /harness-verify |

Each agent `@mentions` only the context it needs (context sink pattern). Fresh agent per task (`context_depth="none"` for generator/critic/refiner).

### Recipes

#### harness-development-cycle.yaml (Staged, 3 approval gates)

Full interactive cycle: explore, spec, plan, execute, verify, finish. Pattern: superpowers full-development-cycle.

Stages:

1. **exploration:** environment-analyst explores, spec-writer produces spec — APPROVAL GATE
2. **planning:** plan-writer creates plan — APPROVAL GATE
3. **execution:** invokes `harness-refinement-loop.yaml` sub-recipe
4. **verification:** harness-evaluator runs novel test rollouts — APPROVAL GATE
5. **completion:** package as nano-amplifier

#### harness-refinement-loop.yaml (While-loop convergence)

Pattern: dev-machine outer loop with `while_condition`. Iterates `harness-single-iteration.yaml` until convergence:

- `while_condition`: converged != 'true'
- `max_while_iterations`: 60 (action-verifier) or 256 (code-as-policy)
- `break_when`: heuristic >= target
- Maintains Thompson sampling tree state across iterations
- `patience`: 15 iterations without improvement before plateau diagnosis
- `checkpoint_best`: always save best-so-far for resumability
- `on_timeout`: return best achieved (do not fail)

#### harness-single-iteration.yaml (Sub-recipe, one cycle)

Pattern: three-agent pipeline per iteration.

Steps:

1. **generate:** harness-generator produces/refines constraint code
2. **critique:** harness-critic reviews against spec
3. **refine:** harness-refiner improves based on critique (conditional: only if critique.needs_refinement)
4. **assess:** harness-evaluator measures legal action rate, produces convergence JSON

Refinement decision logic from the paper: if `is_legal_action()` returns True but the action is actually invalid, refine BOTH functions. If `is_legal_action()` returns False and the action is invalid, refine only `propose_action()`.

#### harness-factory-generation.yaml (Foreach, batch)

Pattern: dev-machine factory with foreach over environments.

Steps:

1. **load-state:** read STATE.yaml
2. **generate-per-environment:** foreach environment, invoke `harness-development-cycle.yaml` with `parallel: 3`
3. **verify-factory:** harness-evaluator verifies all generated harnesses
4. **update-state:** write results to STATE.yaml

## Data Flow

### Artifact Format: Three Tiers

#### Tier 1: Nano-amplifier (3 files)

The atomic unit. Output of a single harness generation:

```
my-harness/
  behavior.yaml        # Amplifier behavior: hooks config, mode reference
  constraints.py       # Python: propose_action(), is_legal_action(), validate_action()
  context.md           # Environment description, constraint rationale
```

Any Amplifier bundle can compose a nano-amplifier via `includes:` in its bundle.md.

#### Tier 2: Harness Bundle (full bundle with multiple nanos)

For library-scale (LabClaw-style) or enterprise (NemoClaw-style):

```
my-harness-bundle/
  bundle.md
  behaviors/
    domain-skill-1.yaml
    domain-skill-2.yaml
    ...
  modules/
    hook-constraints/
      constraints.py
  context/
    domain-knowledge.md
```

Composed of multiple nano-amplifiers assembled into a single bundle.

#### Tier 3: Harness Machine (.harness-machine/ directory)

For factory-scale autonomous generation:

```
.harness-machine/
  STATE.yaml              # Tracks environments, harness candidates, legal action rates
  CONTEXT-TRANSFER.md     # Session handoff notes
  SCRATCH.md              # Ephemeral working memory
  build.yaml              # Outer loop recipe
  iteration.yaml          # Inner loop: one environment per session
  harnesses/              # Generated nano-amplifiers accumulate here
```

Zero runtime dependency on the harness-machine bundle. Self-contained.

### Pipeline Data Flow

```
Environment description
    |
    v
/harness-explore  -->  environment map + feasibility assessment
    |
    v
/harness-spec     -->  harness specification (type, scale, constraints, acceptance criteria)
    |
    v
/harness-plan     -->  implementation plan (tasks for single, or STATE.yaml for factory)
    |
    v
/harness-execute  -->  constraint code (one iteration of generate/critique/refine)
    |                    ^
    |                    | (convergence loop via recipe)
    v                    |
/harness-verify   -->  evidence: legal action rate, reward measurements
    |
    v
/harness-finish   -->  packaged artifact (nano-amplifier, bundle, or .harness-machine/)
```

## Reference Examples

Four annotated walkthroughs as context files, showing spec to plan to artifact at each scale. These are the harness-machine equivalent of superpowers' `example-plan.md` — not code to run, but canonical references for what the agents should produce. Each is annotated with WHY each design decision was made, not just WHAT the artifact looks like.

### context/examples/nano-filesystem-harness.md

Trivial scale. Constrains an agent to read/write within a single directory. 5 rules. Shows the minimal nano-amplifier: a `constraints.py` with `validate_action()` checking path boundaries, a `behavior.yaml` wiring the hook, a `context.md` explaining why.

### context/examples/developer-tooling-harness.md

Medium scale (Claude-Code-style). Tool permissions (which tools allowed/blocked), command allowlists (no `rm -rf`, no `git push` to main), filesystem boundaries (project directory only), environment variable protection. Shows how `harness_type=action-verifier` produces rejection sampling around tool calls.

### context/examples/domain-library-harness.md

Large scale (LabClaw-style). Composable skill library with 20+ skills across a domain. Shows how individual nano-amplifiers compose into a bundle-tier artifact. Demonstrates skill chaining constraints (skill A must precede skill B), domain safety rules (no operations on live specimens without confirmation), and the library structure pattern.

### context/examples/enterprise-governance-harness.md

Complex scale (NemoClaw-style). Multi-layer constraints: input moderation, output filtering, action governance, audit trail, compliance rules. Shows how `harness_type=action-filter` produces a ranked-action system with governance overlay. Demonstrates the policy specification pattern and how enterprise harnesses differ from technical constraint harnesses.

## Skills

### skills/harness-reference/SKILL.md

Complete reference tables: all 7 modes with tool permissions and transitions, all 7 agents with roles and when-to-use, all 4 recipes with patterns, `harness_type` and `harness_scale` enums, artifact tier definitions, anti-rationalization table.

### skills/constraint-design/SKILL.md

How to design good constraints. Three constraint layers from the Claw ecosystem research:

- **Behavioral constraints (soft):** SKILL.md instructions, context files (OpenClaw/LabClaw pattern)
- **Enforcement constraints (hard):** hook deny/modify, container isolation (NanoClaw pattern)
- **Policy constraints (programmatic):** governance rules, audit, compliance (NemoClaw pattern)

When to use each layer, how they compose, common mistakes.

### skills/convergence-debugging/SKILL.md

Diagnosing convergence problems in the refinement loop. Thompson sampling mechanics, tree search state, plateau patterns. Three convergence profiles from the paper:

- **Fast convergers** (2048-v0: ~5 iterations)
- **Steady climbers** (FrozenLake: ~19 iterations)
- **Plateau-then-breakthrough** (Chess: ~60 iterations)

How to distinguish "stuck in local optimum" from "needs more iterations." When to increase exploration vs refine exploitation.

## Error Handling

### Mode-Level Error Handling

Every mode except `/harness-finish` can transition to `/harness-debug`. Debug is the universal off-ramp for when things go wrong at any point in the pipeline.

### Convergence Loop Error Handling

The refinement loop recipe handles failures through several mechanisms:

- **Patience parameter (15 iterations):** If the heuristic is flat for 15 consecutive iterations without improvement, trigger plateau diagnosis rather than continuing blindly.
- **checkpoint_best:** Always save the best-so-far harness. If the loop times out or is interrupted, the best achieved result is available, not lost.
- **on_timeout:** Return the best achieved result rather than failing. A 95% legal action rate harness is better than no harness.
- **Refinement decision logic:** When `is_legal_action()` returns True but the action is actually invalid, refine BOTH functions. When `is_legal_action()` returns False and the action is invalid, refine only `propose_action()`. This prevents wasted iterations refining the wrong function.

### Factory Error Handling

The factory recipe generates harnesses across multiple environments with `parallel: 3`. Individual environment failures do not halt the factory. Results (success or failure with diagnosis) are written to STATE.yaml per environment.

### Feasibility Gate

The `/harness-explore` mode includes a feasibility gate. If the action space is too ambiguous or verification is purely subjective, the pipeline stops before investing in specification, planning, or generation. This is the earliest and cheapest failure mode.

## Testing Strategy

`test_scaffold.py` validates bundle structure (following dev-machine's pattern):

- `bundle.md` exists with correct name/version/agents
- Behavior YAML parses and wires modes hook + tools
- All 7 mode files exist with correct frontmatter (tool permissions, transitions)
- All 7 agent files exist with correct meta (name, description, tools)
- All 4 recipe files exist and are valid YAML
- All context and example files exist
- All 3 skill directories contain SKILL.md
- Directory structure matches specification

## Bundle File Inventory

```
amplifier-bundle-harness-machine/
  bundle.md
  behaviors/
    harness-machine.yaml
  agents/
    environment-analyst.md
    spec-writer.md
    plan-writer.md
    harness-generator.md
    harness-critic.md
    harness-refiner.md
    harness-evaluator.md
  modes/
    harness-explore.md
    harness-spec.md
    harness-plan.md
    harness-execute.md
    harness-verify.md
    harness-finish.md
    harness-debug.md
  context/
    instructions.md
    philosophy.md
    pattern.md
    harness-format.md
    examples/
      nano-filesystem-harness.md
      developer-tooling-harness.md
      domain-library-harness.md
      enterprise-governance-harness.md
  skills/
    harness-reference/
      SKILL.md
    constraint-design/
      SKILL.md
    convergence-debugging/
      SKILL.md
  recipes/
    harness-development-cycle.yaml
    harness-refinement-loop.yaml
    harness-single-iteration.yaml
    harness-factory-generation.yaml
  templates/
    STATE.yaml
    CONTEXT-TRANSFER.md
    SCRATCH.md
    recipes/
      harness-machine-build.yaml
      harness-machine-iteration.yaml
  docs/
    research/
      autoharness-paper.md
      autoharness-concept-map.dot/svg/png
      amplifier-bundle-autoharness.dot/svg/png
      xinghua-lou-autoharness-2603.03329v1.pdf
  tests/
    test_scaffold.py
  README.md
```

Zero Python application code. Pure markdown + YAML configuration bundle.
7 modes, 7 agents, 4 recipes, 3 skills, 4 reference examples, 5 context files, 5 templates.

## Open Questions

1. **Factory Docker infrastructure.** Should the factory templates include Docker infrastructure (Dockerfile, docker-compose, entrypoint.sh, watchdog, monitor) like dev-machine, or start simpler with just recipe templates?

2. **Thompson sampling state persistence.** How should the tree search state be persisted between recipe iterations? In STATE.yaml? In a separate tree-state.json?

3. **Environment runner access.** Should the harness-evaluator agent have access to an actual environment runner (e.g., TextArena for game harnesses), or should evaluation be simulated/mocked for MVP?

4. **Template variable syntax.** The dual-syntax issue from dev-machine (generation-time `{{variables}}` vs runtime `{{variables}}` in templates) — should we implement the whitelist fix from day one?
