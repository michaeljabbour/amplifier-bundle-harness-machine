# Bundlewizard Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `amplifier-bundle-bundlewizard` — a bundle that generates and improves Amplifier bundles through structured interview + iterative convergence.

**Architecture:** Single bundle with internal factory patterns. 10 agents fill abstract pipeline slots (explore → spec → plan → generate → critique → refine → evaluate → package). Two-path routing fork (create new vs improve existing). Three-level convergence (structural + philosophical + functional).

**Tech Stack:** Amplifier bundle system (markdown + YAML). No Python code — all bundle artifacts.

**Design Document:** `docs/plans/2026-03-16-bundlewizard-design.md` (in the harness-machine repo)

---

## Background for New Contributors

An **Amplifier bundle** is a package of markdown and YAML files that gives an AI assistant new capabilities. Think of it like a plugin system:

- **`bundle.md`** — The entry point. A thin file that includes other bundles and behaviors. Should have ≤20 lines of YAML frontmatter.
- **Behaviors** — Reusable capability packages (YAML files) that mount tools, agents, hooks, and context.
- **Agents** — Specialist AI personas (markdown files) that can be delegated to. Each has tools and instructions.
- **Modes** — Permission configurations that control which tools are available. Users switch modes with `/mode-name`.
- **Recipes** — Multi-step workflow definitions (YAML files) that orchestrate agents through pipelines.
- **Context files** — Markdown documents that provide knowledge to agents via `@mention` syntax.
- **Skills** — Loadable knowledge documents (markdown files in a `skills/` directory).
- **Templates** — Starter files that agents copy and fill in during work.

The **thin bundle pattern** is critical: `bundle.md` should be a lightweight router, not a knowledge dump. Heavy content goes into context files that agents `@mention` — this is called the **context sink** discipline.

**URI format for sources:** `git+https://github.com/org/repo@tag#subdirectory=path`

---

## Repo Structure (target)

```
amplifier-bundle-bundlewizard/
├── bundle.md                          # Thin — includes foundation + bundlewizard behavior
├── behaviors/
│   └── bundlewizard.yaml              # Mounts modes, skills, registers all 10 agents
├── agents/
│   ├── bundle-explorer.md             # Interview + routing fork + experience detection
│   ├── bundle-auditor.md              # Full audit for "improve existing" path
│   ├── ecosystem-scout.md             # Ecosystem survey, duplicate detection
│   ├── bundle-spec-writer.md          # Composition design → bundle-spec.md
│   ├── bundle-plan-writer.md          # Task breakdown for generation or renovation
│   ├── bundle-generator.md            # Writes bundle artifacts
│   ├── bundle-critic.md               # Adversarial review, delegates to foundation-expert
│   ├── bundle-refiner.md              # Targeted fixes from critic feedback
│   ├── bundle-evaluator.md            # Three-level convergence
│   └── bundle-packager.md             # Git init, version stamp, deliver
├── modes/
│   ├── bundle-explore.md              # Interview phase
│   ├── bundle-spec.md                 # Design phase
│   ├── bundle-plan.md                 # Planning phase
│   ├── bundle-execute.md              # Convergence loop orchestrator
│   ├── bundle-verify.md               # Evidence collection
│   ├── bundle-finish.md               # Package and deliver
│   ├── bundle-debug.md                # Off-ramp for issues
│   └── dangerously-skip-permissions.md # Autonomous self-evolution mode
├── context/
│   ├── instructions.md                # Mode routing, tier definitions, two-track UX
│   ├── philosophy.md                  # "Bundles are compositions, not monoliths"
│   ├── bundle-patterns.md             # Thin pattern, context sinks, agent descriptions
│   ├── convergence-criteria.md        # Three-level evaluation rubric
│   ├── factory-protocol.md            # Reusable factory pattern for future extraction
│   └── anti-rationalization.md        # Shared discipline tables
├── recipes/
│   ├── bundle-development-cycle.yaml  # Full staged pipeline with approval gates
│   ├── bundle-refinement-loop.yaml    # Convergence loop with patience + checkpoint_best
│   ├── bundle-single-iteration.yaml   # One generate → critique → refine → evaluate
│   ├── bundle-batch-generation.yaml   # Foreach over targets with STATE.yaml
│   └── bundle-audit.yaml             # Standalone audit recipe for "improve existing"
├── skills/
│   ├── bundle-reference/SKILL.md      # Modes, agents, recipes quick reference
│   └── bundle-design/SKILL.md         # Composition patterns, common mistakes
├── templates/
│   ├── STATE.yaml                     # Factory state tracking
│   ├── CONTEXT-TRANSFER.md            # Session handoff notes
│   └── SCRATCH.md                     # Working memory
└── docs/
    ├── BUNDLEWIZARD-GUIDE.md          # User-facing guide
    └── FACTORY-PATTERN.md             # Documents the pattern for future extraction
```

---

## Phase 1: Foundation

> Everything else depends on this skeleton. Create the repo, bundle entry point, behavior, context files, modes, and templates.

---

### Task 1: Create repo, initialize git, push to GitHub

**What:** Create the empty directory structure, initialize git, create the GitHub remote under `michaeljabbour/`.

- [ ] **Step 1.1** — Create the repo and directory structure:

```bash
mkdir -p ~/dev/amplifier-bundle-bundlewizard
cd ~/dev/amplifier-bundle-bundlewizard
git init
mkdir -p agents behaviors context modes recipes skills/bundle-reference skills/bundle-design templates docs
```

- [ ] **Step 1.2** — Create a minimal README so the repo isn't empty:

Create `~/dev/amplifier-bundle-bundlewizard/README.md`:

```markdown
# amplifier-bundle-bundlewizard

Bundle generation and improvement factory for the Amplifier ecosystem.

Generates new bundles and improves existing ones through structured interview + iterative convergence using the factory pattern (generate → critique → refine → evaluate).

## Status

Under construction. See `docs/plans/` in the harness-machine repo for the design document.
```

- [ ] **Step 1.3** — Initial commit and push:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
git add .
git commit -m "chore: initialize bundlewizard repo"
gh repo create michaeljabbour/amplifier-bundle-bundlewizard --private --source=. --push
```

- [ ] **Step 1.4** — Validate: confirm `git remote -v` shows the GitHub remote and `git log --oneline` shows the initial commit.

---

### Task 2: bundle.md — the thin entry point

**What:** The single entry point for the bundle. Must follow the **thin bundle pattern**: ≤20 lines YAML frontmatter, NO `@mentions` of heavy context files, just includes and a brief markdown body describing what's available.

**Why thin:** The bundle.md is loaded into every session that composes this bundle. Heavy content here wastes context tokens. All knowledge goes into context files that agents `@mention` when needed.

- [ ] **Step 2.1** — Create `~/dev/amplifier-bundle-bundlewizard/bundle.md`:

```markdown
---
bundle:
  name: bundlewizard
  version: 0.1.0
  description: |
    Bundle generation and improvement factory for the Amplifier ecosystem.
    Generates new bundles and improves existing ones through structured
    interview + iterative convergence using the factory pattern.

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: bundlewizard:behaviors/bundlewizard
---

# Bundlewizard

Bundle generation and improvement factory. Two paths: create new bundles or improve existing ones.

## Modes

| Shortcut | Phase | What Happens |
|----------|-------|--------------|
| `/bundle-explore` | Interview | Understand what you need, route to create or improve |
| `/bundle-spec` | Design | Compose the bundle specification |
| `/bundle-plan` | Planning | Break spec into implementation tasks |
| `/bundle-execute` | Generation | Convergence loop: generate → critique → refine → evaluate |
| `/bundle-verify` | Verification | Collect evidence that the bundle works |
| `/bundle-finish` | Delivery | Package, version stamp, deliver |
| `/bundle-debug` | Off-ramp | Diagnose issues at any stage |

## Recipes

- `bundle-development-cycle.yaml` — Full pipeline with approval gates
- `bundle-audit.yaml` — Standalone audit for existing bundles
- `bundle-batch-generation.yaml` — Generate multiple bundles from a target list

## Getting Started

Say what you want to build, or point me at a bundle to improve. I'll figure out the rest.
```

- [ ] **Step 2.2** — Validate frontmatter is valid YAML: `head -14 bundle.md | python3 -c "import sys,yaml; yaml.safe_load(sys.stdin)"` — should exit 0 with no errors.

- [ ] **Step 2.3** — Commit:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
git add bundle.md
git commit -m "feat: add bundle.md — thin entry point"
```

---

### Task 3: behaviors/bundlewizard.yaml — the behavior mount

**What:** The behavior YAML that mounts the modes system (hooks-mode + tool-mode), registers all 10 agents, mounts skills, and includes the two root-level context files (instructions.md and philosophy.md).

**Why this structure:** Behaviors are the wiring layer. This file tells Amplifier: "here are the tools, hooks, agents, and context this bundle provides." Agents and modes live in their own files — the behavior just registers them.

- [ ] **Step 3.1** — Create `~/dev/amplifier-bundle-bundlewizard/behaviors/bundlewizard.yaml`:

```yaml
bundle:
  name: bundlewizard-behavior
  version: 0.1.0
  description: |
    Core behavior for bundlewizard. Mounts the modes system, registers all
    agents, loads skills, and includes root-level context.

includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=behaviors/modes.yaml

hooks:
  - module: hooks-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/hooks-mode
    config:
      search_paths:
        - "@bundlewizard:modes"

tools:
  - module: tool-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/tool-mode
    config:
      gate_policy: "warn"
  - module: tool-skills
    source: git+https://github.com/microsoft/amplifier-module-tool-skills@main
    config:
      skills:
        - "@bundlewizard:skills"

agents:
  include:
    - bundlewizard:agents/bundle-explorer
    - bundlewizard:agents/bundle-auditor
    - bundlewizard:agents/ecosystem-scout
    - bundlewizard:agents/bundle-spec-writer
    - bundlewizard:agents/bundle-plan-writer
    - bundlewizard:agents/bundle-generator
    - bundlewizard:agents/bundle-critic
    - bundlewizard:agents/bundle-refiner
    - bundlewizard:agents/bundle-evaluator
    - bundlewizard:agents/bundle-packager

context:
  include:
    - bundlewizard:context/instructions.md
    - bundlewizard:context/philosophy.md
```

- [ ] **Step 3.2** — Validate YAML parses: `python3 -c "import yaml; yaml.safe_load(open('behaviors/bundlewizard.yaml'))"` — should exit 0.

- [ ] **Step 3.3** — Verify agent count matches design (10 agents): `grep -c 'bundlewizard:agents/' behaviors/bundlewizard.yaml` — should print `10`.

- [ ] **Step 3.4** — Commit:

```bash
git add behaviors/bundlewizard.yaml
git commit -m "feat: add bundlewizard behavior — mounts modes, agents, skills, context"
```

---

### Task 4: context/instructions.md — the routing brain

**What:** The primary instruction context file. Loaded at root session level (via the behavior's `context.include`). Contains: mode routing table, tier definitions, two-track UX, experience detection signals, and interview flow summaries for both paths.

**Why root-level:** This is one of only two context files loaded into every session. It must be concise — just enough to route correctly. Deep knowledge lives in other context files that agents `@mention`.

- [ ] **Step 4.1** — Create `~/dev/amplifier-bundle-bundlewizard/context/instructions.md`:

```markdown
# Bundlewizard Instructions

You are operating the Bundlewizard — an Amplifier bundle factory that generates new bundles and improves existing ones.

## Mode Routing

Users navigate the pipeline via modes. Each mode has a specific phase, a paired agent that does the real work, and strict tool permissions.

| Mode | Phase | Agent That Does The Work | Key Constraint |
|------|-------|--------------------------|----------------|
| `/bundle-explore` | Interview | `bundle-explorer` | You converse; agent investigates. No writing. |
| `/bundle-spec` | Design | `bundle-spec-writer` | Produces `bundle-spec.md`. No code yet. |
| `/bundle-plan` | Planning | `bundle-plan-writer` | Produces implementation plan. No code yet. |
| `/bundle-execute` | Generation | `bundle-generator` + `bundle-critic` + `bundle-refiner` + `bundle-evaluator` | Convergence loop. Orchestrator NEVER writes directly. |
| `/bundle-verify` | Verification | `bundle-evaluator` | Three-level evidence. Independent of generation. |
| `/bundle-finish` | Delivery | `bundle-packager` | Version stamp, git, deliver. Terminal mode. |
| `/bundle-debug` | Off-ramp | (you, directly) | Diagnose issues. Can transition to any mode. |
| `/dangerously-skip-permissions` | Self-evolution | (autonomous) | All approval gates bypassed. Convergence still enforced. |

## The Two-Path Routing Fork

The FIRST question in every session is implicit: does the user want to **create a new bundle** or **improve an existing one**?

**Signals for "create new":**
- "I want to build..." / "Create a bundle that..."
- Describes a capability that doesn't exist yet
- No mention of an existing bundle path or repo

**Signals for "improve existing":**
- "Look at this bundle..." / "Review my bundle..."
- Provides a path, repo URL, or bundle name
- "This bundle doesn't do X well enough"

### Path A: Create New

`/bundle-explore` → `/bundle-spec` → `/bundle-plan` → `/bundle-execute` → `/bundle-verify` → `/bundle-finish`

Interview questions (one at a time, adapt order to experience level):
1. What problem does this solve? Who uses it?
2. Does something similar already exist? (delegate to `ecosystem-scout`)
3. What tier? Behavior / Bundle / Application Bundle — with examples calibrated to experience
4. What capabilities does it need? (agents, tools, modes, recipes, context)
5. What should it delegate to existing experts vs carry itself?

### Path B: Improve Existing

`/bundle-explore` → audit → findings → `/bundle-spec` → `/bundle-plan` → `/bundle-execute` → `/bundle-verify` → `/bundle-finish`

Interview flow:
1. Point me at the bundle (path or repo URL)
2. `bundle-auditor` runs the full three-level audit
3. Findings presented: X structural, Y philosophical, Z capability gaps
4. Which improvements? All? Just critical? Add new capabilities?
5. Produces `bundle-spec.md` with the renovation plan

## Output Tiers (scope-driven, not size-driven)

| Tier | What It Is | When It's Right |
|------|-----------|----------------|
| **Behavior** | Reusable capability package (YAML + context + maybe agents). Composed into bundles via `includes:`. | Adding a capability to an existing bundle |
| **Bundle** | Standalone bundle with bundle.md, behaviors, agents, context. A complete product. | A focused tool/capability that stands alone |
| **Application Bundle** | Full-featured with modes, recipes, skills, possibly modules. What harness-machine and superpowers are. | A complete development workflow or domain system |

Size is emergent from scope, not a design input.

## Two-Track UX

| Track | How | Best For |
|-------|-----|----------|
| Interactive modes | Navigate modes manually: `/bundle-explore` → `/bundle-spec` → ... | Hands-on sessions, control at each step |
| Recipe automation | `bundle-development-cycle.yaml` with approval gates | End-to-end with checkpoints |

Both tracks produce the same output. The recipe just automates the mode transitions.

## Experience Detection (passive — never ask directly)

| Signal | Indicates | Response |
|--------|----------|----------|
| Uses "behavior," "context sink," "thin pattern" naturally | Experienced | Accelerate — skip fundamentals, focus on architecture |
| Says "I want to build something that does X" | Newcomer | Guide — explain tiers, show examples, ask about the problem |
| References specific bundles or modules by name | Experienced | Accelerate — they know the ecosystem |
| Describes the outcome, not the mechanism | Newcomer | Guide — translate outcome into bundle concepts |

Never say "are you experienced?" or "do you know what a bundle is?" — detect from vocabulary and adjust.
```

- [ ] **Step 4.2** — Commit:

```bash
git add context/instructions.md
git commit -m "feat: add context/instructions.md — routing, tiers, two-track UX"
```

---

### Task 5: context/philosophy.md — the principles

**What:** Core design philosophy for bundle creation. This is the second of two root-level context files. Short and punchy — principles, not procedures.

- [ ] **Step 5.1** — Create `~/dev/amplifier-bundle-bundlewizard/context/philosophy.md`:

```markdown
# Bundlewizard Philosophy

These principles govern every bundle that bundlewizard creates or improves.

## Bundles Are Compositions, Not Monoliths

A bundle is a **composition** of capabilities — behaviors, agents, context, tools — wired together with clear boundaries. It is NOT a single large document that tries to do everything.

Good bundles compose other bundles. Great bundles are themselves composable.

## Delegate to Experts, Don't Guess

When bundlewizard needs to know about bundle composition rules → delegate to `foundation:foundation-expert`.
When it needs to know about the Amplifier ecosystem → delegate to `amplifier:amplifier-expert`.
When it needs domain expertise for functional evaluation → delegate to the appropriate domain expert.

Bundlewizard owns the **process**. Experts own the **knowledge**. Never guess what an expert would say.

## The Thin Pattern

`bundle.md` is a router, not a knowledge base.

- ≤20 lines YAML frontmatter
- NO `@mentions` of heavy context files
- NO redeclaration of what behaviors already provide
- Just `includes:` and a brief markdown body listing what's available

Heavy content sinks to context files. Agents `@mention` what they need. Users never see unused context.

## Context Sinks

Knowledge flows **down** to where it's used:

- Root session gets only routing info (instructions.md, philosophy.md)
- Agents `@mention` the specific context files they need
- No agent loads ALL context — each loads only what's relevant to its role

This is called the **context sink discipline**. It prevents context overflow and keeps each agent focused.

## Scope-Driven Tiers

Don't ask "how big should this bundle be?" Ask "what scope does this serve?"

- Adding a capability → Behavior
- Standalone focused tool → Bundle
- Complete workflow system → Application Bundle

Size is emergent from scope. Never pad a behavior into a bundle for perceived importance.

## Convergence Over Assumptions

Never declare a bundle "done" without evidence. The convergence loop exists because:

1. **Generators hallucinate** — they produce plausible-looking artifacts with subtle bugs
2. **Critics see differently** — `context_depth="none"` gives the critic a fresh perspective
3. **Evaluators measure** — three-level scoring replaces gut feeling with evidence

Every generated bundle goes through generate → critique → refine → evaluate. No exceptions. The "simple" ones are where the bugs hide.
```

- [ ] **Step 5.2** — Commit:

```bash
git add context/philosophy.md
git commit -m "feat: add context/philosophy.md — core principles"
```

---

### Task 6: context/bundle-patterns.md — the rules

**What:** Specific, actionable rules for bundle construction. This is NOT loaded at root level — agents `@mention` it when they need composition guidance. More detailed than philosophy.md.

- [ ] **Step 6.1** — Create `~/dev/amplifier-bundle-bundlewizard/context/bundle-patterns.md`:

```markdown
# Bundle Construction Patterns

Actionable rules for creating high-quality Amplifier bundles. Referenced by agents that generate, critique, or evaluate bundle artifacts.

## The Thin Bundle Pattern

### bundle.md Rules

1. **≤20 lines YAML frontmatter** — name, version, description, includes. That's it.
2. **NO `@mentions`** in the markdown body — don't pull context files into the root session.
3. **NO redeclaration** — if a behavior provides agents, don't list them again in bundle.md frontmatter.
4. **Includes are composition** — `includes:` says "I am composed of these things." Each included bundle or behavior adds its capabilities.
5. **Markdown body is a menu** — brief description of what's available (modes, agents, recipes). Human-readable orientation, not machine context.

### What Goes Where

| Content Type | Where It Lives | Loaded When |
|-------------|---------------|-------------|
| Bundle identity + composition | `bundle.md` frontmatter | Always (root session) |
| Tool/hook/agent registration | `behaviors/*.yaml` | Always (via includes) |
| Routing instructions | `context/instructions.md` | Always (behavior context.include) |
| Core principles | `context/philosophy.md` | Always (behavior context.include) |
| Detailed domain knowledge | `context/*.md` (other files) | On-demand (agent @mention) |
| Agent instructions | `agents/*.md` body | When agent is delegated to |
| Mode permissions | `modes/*.md` frontmatter | When mode is activated |

## Context Sink Discipline

1. **Root context ≤ 2 files** — Only `instructions.md` and `philosophy.md` load into every session.
2. **No file >100 lines at root** — If it's longer, it belongs in an agent-level @mention.
3. **Agents @mention only what they need** — `bundle-critic` needs `convergence-criteria.md` and `bundle-patterns.md`. It does NOT need `factory-protocol.md`.
4. **No duplicate loading** — If a behavior includes a context file, agents in that behavior don't @mention the same file again.

## Agent Description Quality (WHY/WHEN/WHAT/HOW)

Every agent's `meta.description` must answer four questions for the LLM that decides whether to delegate:

1. **WHY** does this agent exist? — "Use when [trigger condition]."
2. **WHEN** should it be called? — Examples with `<example>` tags showing trigger → delegation.
3. **WHAT** does it produce? — "Produces [output artifact]."
4. **HOW** does it work? — Brief mention of approach (e.g., "delegates to foundation-expert for structural review").

Bad description: "Handles bundle auditing."
Good description: "Use when improving an existing bundle. Reads the entire bundle, produces a structured findings report covering structural issues, philosophical violations, and capability gaps. Delegates to foundation:foundation-expert for structural review and amplifier:amplifier-expert for ecosystem positioning."

## Composition Hygiene

1. **Source URIs must be pinned** — Use `@v1.0.0` tags, not `@main`, for anything published. During development, `@main` is acceptable with a comment noting it should be pinned before release.
2. **No circular includes** — Bundle A includes B includes A is forbidden. The loader will detect this, but don't rely on the loader.
3. **Behaviors are reusable** — Design behaviors so other bundles could compose them. Don't hardcode bundle-specific paths.
4. **One behavior per concern** — Don't create a mega-behavior that does everything. Split by responsibility.

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| Putting agent descriptions in bundle.md | Wastes root context; changes require editing the wrong file | Put descriptions in agent files; bundle.md just lists names |
| @mentioning context files from bundle.md body | Loads heavy docs into every session | Move @mentions to agent bodies |
| Declaring the same agent in behavior AND bundle.md | Double registration; confusing | Declare in behavior only |
| Using `@main` in published source URIs | Breaking changes hit consumers silently | Pin to version tags |
| Creating a "utils" context file | Unfocused grab-bag; every agent loads it "just in case" | Split by topic |
| Agent without examples in description | LLM can't pattern-match when to delegate | Add 2+ `<example>` blocks |
```

- [ ] **Step 6.2** — Commit:

```bash
git add context/bundle-patterns.md
git commit -m "feat: add context/bundle-patterns.md — construction rules and anti-patterns"
```

---

### Task 7: context/convergence-criteria.md — the evaluation rubric

**What:** The three-level convergence system. Referenced by `bundle-evaluator`, `bundle-critic`, and the convergence loop recipe. Defines exactly what "done" means.

- [ ] **Step 7.1** — Create `~/dev/amplifier-bundle-bundlewizard/context/convergence-criteria.md`:

```markdown
# Three-Level Convergence Criteria

Every bundle produced by bundlewizard must pass all three levels before delivery. There are no shortcuts. "Simple" bundles are where the bugs hide.

## Convergence Formula

```
converged = (level_1 == PASS) AND (level_2 >= 0.85) AND (level_3 >= 0.80)
```

Level 2 bar is higher because philosophical violations are objective. Level 3 is lower because functional evaluation involves expert judgment.

---

## Level 1: Structural (pass/fail gates)

All gates must pass. If ANY gate fails, convergence score is 0. Fix structural issues before evaluating anything else.

| Gate | Check | How To Verify |
|------|-------|--------------|
| Bundle loads | `bundle.md` frontmatter parses as valid YAML | `python3 -c "import yaml; yaml.safe_load(open('bundle.md').read().split('---')[1])"` |
| Agent references resolve | Every agent in `behaviors/*.yaml` → `agents.include` has a corresponding file | Cross-reference `agents/` directory against behavior |
| URI syntax valid | All `source:` and `includes:` URIs match `git+https://...@tag` format | Regex check on all YAML files |
| No duplicate context | No context file is loaded by BOTH `context.include` AND an agent `@mention` in the same session | Manual review of behavior + agent @mentions |
| Source URIs reachable | Module/bundle source repos exist (at least structurally valid) | URI format validation (don't HTTP check during generation) |
| Mode references valid | All mode files in `modes/` are discoverable by hooks-mode | Check `search_paths` config in behavior |

**If Level 1 fails:** Stop. Fix the structural issue. Do not evaluate Level 2 or 3.

---

## Level 2: Philosophical (scored rubric, 0.0 – 1.0)

Four criteria, equally weighted at 25% each. Threshold: **0.85**.

### 2a. Thin Bundle Pattern (25%)

| Score | Criteria |
|-------|----------|
| 1.0 | bundle.md ≤20 lines frontmatter, no @mentions in body, no redeclaration |
| 0.75 | Minor violation: frontmatter slightly over 20 lines but no content duplication |
| 0.5 | Moderate violation: @mentions in bundle.md body or some redeclaration |
| 0.0 | bundle.md is a monolith with inline agent descriptions or heavy context |

### 2b. Context Sink Discipline (25%)

| Score | Criteria |
|-------|----------|
| 1.0 | Root context ≤2 files, no file >100 lines at root, agents @mention only what they need |
| 0.75 | Root context has 3 files or one root file slightly over 100 lines |
| 0.5 | Multiple heavy files at root or agents @mentioning everything |
| 0.0 | All context loaded at root level; agents are empty shells |

### 2c. Agent Description Quality (25%)

| Score | Criteria |
|-------|----------|
| 1.0 | Every agent has WHY/WHEN/WHAT/HOW, 2+ examples with `<example>` tags |
| 0.75 | All agents have descriptions but some missing examples or unclear trigger |
| 0.5 | Some agents have good descriptions, others are vague one-liners |
| 0.0 | Agent descriptions are perfunctory ("Handles X") |

### 2d. Composition Hygiene (25%)

| Score | Criteria |
|-------|----------|
| 1.0 | No circular includes, behaviors reusable, sources appropriately pinned, one behavior per concern |
| 0.75 | Minor: one source using @main that should be pinned, but no structural issues |
| 0.5 | Behavior does too many things or has hardcoded paths |
| 0.0 | Circular includes, duplicate declarations, or fundamentally broken composition |

### Level 2 Score Calculation

```
level_2 = (thin_pattern * 0.25) + (context_sink * 0.25) + (agent_quality * 0.25) + (composition * 0.25)
```

**If Level 2 < 0.85:** Iterate. The critic identifies which criteria scored low. The refiner targets those specific issues.

---

## Level 3: Functional (domain-specific, scored 0.0 – 1.0)

Threshold: **0.80**.

Evaluates whether the bundle actually does what the user intended. This varies by what the bundle is FOR:

| Bundle Type | Functional Check |
|------------|-----------------|
| Code review bundle | Does it review code? Delegate a sample review task. |
| Mode bundle | Do modes activate? Do tool permissions work? |
| Agent bundle | Do agents respond to their trigger conditions? |
| Workflow bundle | Does the recipe pipeline complete? |
| General bundle | Does the primary use case work end-to-end? |

The evaluator delegates to the appropriate **domain expert** for functional assessment. Bundlewizard does NOT judge domain fitness itself.

### Functional Score Breakdown

| Score | Criteria |
|-------|----------|
| 1.0 | Primary use case works, edge cases handled, no broken paths |
| 0.80 | Primary use case works, some edge cases need attention |
| 0.60 | Primary use case partially works, significant gaps |
| 0.0 | Bundle does not achieve its stated purpose |

---

## Loop Discipline

1. **Evaluate after every refinement** — Never batch multiple refinements before evaluating.
2. **checkpoint_best** — Save the highest-scoring iteration. If convergence stalls, deliver the best achieved.
3. **Patience counter** — If score hasn't improved in 3 iterations, trigger diagnosis: are we refining the right things?
4. **Never silently declare done** — Convergence is a measured state, not a feeling.
```

- [ ] **Step 7.2** — Commit:

```bash
git add context/convergence-criteria.md
git commit -m "feat: add context/convergence-criteria.md — three-level evaluation rubric"
```

---

### Task 8: context/factory-protocol.md — the reusable pattern

**What:** Documents the abstract factory pipeline pattern. Written so it could be extracted into `amplifier-bundle-factory-core` later. Describes pipeline stages, agent slots, convergence loop protocol, two-track UX, and version stamping.

- [ ] **Step 8.1** — Create `~/dev/amplifier-bundle-bundlewizard/context/factory-protocol.md`:

```markdown
# Factory Protocol

This document defines the abstract factory pattern used by bundlewizard. It is structured for future extraction into `amplifier-bundle-factory-core` when a second consumer (harness-machine) is ready to share it.

**Current status:** Internal to bundlewizard. Do not depend on this from outside the bundle.

## Abstract Pipeline Stages

Every factory follows this stage sequence. Domain-specific factories fill each stage with their own agents.

| Stage | Abstract Slot | Bundlewizard Agent | Purpose |
|-------|--------------|-------------------|---------|
| Explore | `explorer` | `bundle-explorer` | Understand the problem, interview the user, route to the right path |
| Spec | `spec-writer` | `bundle-spec-writer` | Design the solution, produce a specification document |
| Plan | `plan-writer` | `bundle-plan-writer` | Break the spec into implementation tasks |
| Execute | `generator` | `bundle-generator` | Produce artifacts from the plan |
| Execute | `critic` | `bundle-critic` | Adversarial review of generated artifacts |
| Execute | `refiner` | `bundle-refiner` | Targeted fixes based on critic feedback |
| Execute | `evaluator` | `bundle-evaluator` | Measure convergence (did we improve?) |
| Verify | `evaluator` | `bundle-evaluator` | Final independent verification |
| Finish | `packager` | `bundle-packager` | Version stamp, package, deliver |
| Debug | (none) | (user-directed) | Off-ramp for issues at any stage |

The Execute stage contains the **convergence loop**: generator → critic → refiner → evaluator, repeated until convergence criteria are met or patience exhausts.

## Convergence Loop Protocol

```
iteration = 0
best_score = 0
patience_counter = 0

while not converged and iteration < max_iterations:
    iteration += 1
    
    # Generate (or refine if iteration > 1)
    artifacts = generator.generate(spec, plan, previous_critique)
    
    # Critique (adversarial, context_depth="none")
    critique = critic.review(artifacts)
    
    # Refine (targeted fixes only)
    artifacts = refiner.fix(artifacts, critique)
    
    # Evaluate (three-level scoring)
    score = evaluator.score(artifacts)
    
    if score > best_score:
        best_score = score
        checkpoint_best(artifacts)
        patience_counter = 0
    else:
        patience_counter += 1
    
    if patience_counter >= patience_limit:
        diagnose("Score stalled for {patience_limit} iterations")
    
    converged = meets_convergence_criteria(score)

# On exit: deliver best_checkpoint (not necessarily last iteration)
```

### Key discipline:

- **checkpoint_best** after every improvement — never lose progress
- **patience_limit** (default: 3 for bundles) — don't spin forever on diminishing returns
- **On timeout:** deliver checkpoint_best with a note about what didn't converge. 95% is better than nothing.
- **Never skip the critic** — even for "obvious" fixes. The critic sees what you can't.

## Two-Track UX Infrastructure

| Component | Interactive Track | Recipe Track |
|-----------|------------------|--------------|
| Stage transitions | User types `/mode-name` | Recipe `stages:` with approval gates |
| Approval points | Implicit (user sees output, decides next step) | Explicit `gate: approval` between stages |
| Convergence loop | `/bundle-execute` mode orchestrates | `bundle-refinement-loop.yaml` recipe |
| Single iteration | Agent delegation from execute mode | `bundle-single-iteration.yaml` sub-recipe |

Both tracks use the **same agents** with the **same context**. The only difference is who decides when to advance to the next stage.

## Version Stamping

Every bundle produced by the factory gets a version stamp:

```yaml
# In the generated bundle.md frontmatter:
bundle:
  name: <generated-bundle-name>
  version: 0.1.0
  description: |
    <generated description>
  generated_by:
    tool: bundlewizard
    version: 0.1.0
    convergence:
      iterations: <N>
      level_1: PASS
      level_2: <score>
      level_3: <score>
```

This metadata enables traceability — you can always tell which bundles were machine-generated and what quality bar they met.

## Domain-Specific Extensions

Each factory adds domain-specific agents beyond the core slots:

| Factory | Extra Agents | Purpose |
|---------|-------------|---------|
| Bundlewizard | `bundle-auditor`, `ecosystem-scout` | Improve-path audit, ecosystem survey |
| Harness-machine | `environment-analyst` | Environment feasibility mapping |

These are NOT part of the abstract protocol — they're domain concerns.
```

- [ ] **Step 8.2** — Commit:

```bash
git add context/factory-protocol.md
git commit -m "feat: add context/factory-protocol.md — abstract pipeline for future extraction"
```

---

### Task 9: context/anti-rationalization.md — the discipline gates

**What:** The anti-rationalization rules from the design. These are gates, not guidelines. Referenced by agents that might be tempted to skip process steps.

- [ ] **Step 9.1** — Create `~/dev/amplifier-bundle-bundlewizard/context/anti-rationalization.md`:

```markdown
# Anti-Rationalization Rules

These are NOT guidelines. These are **gates**. Every temptation in this table has been encountered in production. Every rule exists because skipping it caused a real bug.

## The Table

| Temptation | Rule | Why |
|-----------|------|-----|
| "I'll just write the bundle.md directly, it's only 14 lines" | **No.** The generator writes it. The critic reviews it. Every time. | The pattern.md double-load bug was exactly 1 line. The generator + critic pipeline caught it. You wouldn't have. |
| "The fix is obvious, skip the critic" | **No.** The critic runs with `context_depth="none"`. It sees what you can't. | Fresh eyes catch assumptions. The critic doesn't share your context, so it evaluates the artifact as-is, not as-intended. |
| "This is a simple behavior, skip the evaluator" | **No.** "Simple" is where the pattern.md double-load bug hid. Evaluate. | Complexity is not correlated with bug density. Simple artifacts are under-scrutinized by default. The evaluator compensates. |
| "I know what the expert would say" | **No.** Delegate. The expert has @mentioned docs you don't. | The expert loads authoritative context (foundation docs, ecosystem knowledge). Your guess is informed by whatever's in your session context, which is intentionally incomplete. |
| "One more quick fix, then we'll evaluate" | **No.** Evaluate after every refinement. Checkpoint_best. | Batching fixes before evaluation means you can't attribute score changes to specific fixes. If a batch makes things worse, you don't know which fix caused it. |

## Enforcement

These rules are enforced at three levels:

1. **Mode permissions** — Modes that shouldn't write files have write_file blocked. The orchestrator (execute mode) cannot write directly.
2. **Recipe structure** — Recipes encode the pipeline order. You can't run the refiner without a critique.
3. **Agent instructions** — Each agent's markdown body includes the relevant anti-rationalization rules for its role.

## When You Think You've Found an Exception

You haven't. The table covers the cases that felt like exceptions. If you genuinely believe the process should change, that's a design discussion — not a runtime shortcut. Propose the change, get it reviewed, update the table. Don't skip the gate.
```

- [ ] **Step 9.2** — Commit:

```bash
git add context/anti-rationalization.md
git commit -m "feat: add context/anti-rationalization.md — discipline gates"
```

---

### Task 10: modes/bundle-explore.md — interview phase

**What:** The first mode users enter. Interview phase with strict tool permissions. Follows the "hybrid pattern": you (the mode operator) handle the conversation, agents handle the investigation.

- [ ] **Step 10.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/bundle-explore.md`:

```markdown
---
mode:
  name: bundle-explore
  description: Explore and interview for bundle generation or improvement
  shortcut: bundle-explore

  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - delegate
      - recipes
    warn:
      - bash

  default_action: block
  allowed_transitions: [bundle-spec, bundle-debug]
  allow_clear: false
---

BUNDLE-EXPLORE MODE: Understand what the user needs before designing anything.

<CRITICAL>
THE HYBRID PATTERN: You handle the CONVERSATION. Investigation agents handle the RESEARCH.

Your role: Ask the user about their needs, discuss what they want to build or improve, detect their experience level passively. This is interactive dialogue between you and the user.

Agent roles:
- `bundlewizard:ecosystem-scout` — When you need to check if something similar exists or find reusable components
- `bundlewizard:bundle-auditor` — When the user points at an existing bundle for the "improve" path
- `amplifier:amplifier-expert` — When you need ecosystem knowledge

You CANNOT write files in this mode. write_file and edit_file are blocked. This mode is for understanding, not creating.
</CRITICAL>

<HARD-GATE>
Do NOT delegate to any generation agent, invoke any generation recipe, or transition to bundle-spec until you have:
1. Determined whether this is "create new" or "improve existing"
2. Gathered enough context to write a meaningful spec
3. Confirmed your understanding with the user

This applies to EVERY request regardless of perceived simplicity.
</HARD-GATE>

## Your Checklist

Track progress using the todo tool:

For **Create New**:
- [ ] What problem does this solve? Who uses it?
- [ ] Ecosystem check: does something similar exist? (delegate to ecosystem-scout)
- [ ] What tier? Behavior / Bundle / Application Bundle
- [ ] What capabilities? Agents, tools, modes, recipes, context
- [ ] What should delegate to existing experts vs carry itself?
- [ ] User confirmed understanding — ready for spec

For **Improve Existing**:
- [ ] Bundle identified (path or repo URL)
- [ ] Audit complete (delegate to bundle-auditor)
- [ ] Findings presented and discussed
- [ ] Improvements selected (all / critical / specific)
- [ ] New capabilities to add?
- [ ] User confirmed scope — ready for spec

## Experience Detection

Detect experience level passively from vocabulary and adjust your depth:

**Experienced user signals:** Uses "behavior," "context sink," "thin pattern," references specific bundles/modules by name, discusses architecture unprompted.
→ Accelerate: Skip fundamentals, ask about composition decisions and architecture.

**Newcomer signals:** Describes outcome not mechanism ("I want something that does X"), no bundle vocabulary, asks what terms mean.
→ Guide: Explain what a bundle is, show tier examples, translate their outcome into bundle concepts.

Never ask "are you experienced?" — detect and adapt.

## Transition

When exploration is complete: "Ready to design the bundle specification. Transitioning to `/bundle-spec`."
```

- [ ] **Step 10.2** — Validate YAML frontmatter: `python3 -c "import yaml; yaml.safe_load(open('modes/bundle-explore.md').read().split('---')[1])"` — should exit 0.

- [ ] **Step 10.3** — Commit:

```bash
git add modes/bundle-explore.md
git commit -m "feat: add modes/bundle-explore.md — interview phase"
```

---

### Task 11: modes/bundle-spec.md — design phase

- [ ] **Step 11.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/bundle-spec.md`:

```markdown
---
mode:
  name: bundle-spec
  description: Design the bundle composition — produce a bundle specification document
  shortcut: bundle-spec

  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - delegate
      - recipes
    warn:
      - bash
      - write_file
      - edit_file

  default_action: block
  allowed_transitions: [bundle-plan, bundle-explore, bundle-debug]
  allow_clear: false
---

BUNDLE-SPEC MODE: Design the bundle composition.

<CRITICAL>
THE HYBRID PATTERN: You handle the CONVERSATION. The spec-writer agent handles the DOCUMENT.

Your role: Discuss composition decisions with the user — what agents, behaviors, context, modes, and recipes the bundle needs. Confirm the design before writing.

Agent role: `bundlewizard:bundle-spec-writer` produces the `bundle-spec.md` document. Delegate when the design discussion is complete.

The spec-writer delegates to `foundation:foundation-expert` for composition validation.
</CRITICAL>

<HARD-GATE>
Do NOT delegate to the spec-writer until you have discussed:
1. Output tier (behavior / bundle / application bundle)
2. What capabilities the bundle needs
3. What it delegates vs carries
4. User has confirmed the design direction
</HARD-GATE>

## Spec Design Checklist

- [ ] Output tier confirmed
- [ ] Capabilities enumerated (agents, modes, tools, recipes, context)
- [ ] Delegation decisions made (what to delegate to existing experts)
- [ ] Composition validated (delegate to foundation-expert if uncertain)
- [ ] bundle-spec.md produced by spec-writer agent
- [ ] User reviewed and approved spec

## Transition

When spec is complete: "Specification ready. Transitioning to `/bundle-plan` for task breakdown."

Can also go back: "Need to revisit the interview? Transitioning to `/bundle-explore`."
```

- [ ] **Step 11.2** — Validate YAML frontmatter: `python3 -c "import yaml; yaml.safe_load(open('modes/bundle-spec.md').read().split('---')[1])"` — should exit 0.

- [ ] **Step 11.3** — Commit:

```bash
git add modes/bundle-spec.md
git commit -m "feat: add modes/bundle-spec.md — design phase"
```

---

### Task 12: modes/bundle-plan.md — planning phase

- [ ] **Step 12.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/bundle-plan.md`:

```markdown
---
mode:
  name: bundle-plan
  description: Break the bundle specification into implementation tasks
  shortcut: bundle-plan

  tools:
    safe:
      - read_file
      - glob
      - grep
      - load_skill
      - delegate
      - recipes
    warn:
      - bash
      - write_file
      - edit_file

  default_action: block
  allowed_transitions: [bundle-execute, bundle-spec, bundle-debug]
  allow_clear: false
---

BUNDLE-PLAN MODE: Break the specification into implementation tasks.

<CRITICAL>
THE HYBRID PATTERN: You handle the CONVERSATION. The plan-writer agent handles the DOCUMENT.

Your role: Discuss task ordering and boundaries with the user. Confirm the plan structure.

Agent role: `bundlewizard:bundle-plan-writer` produces the implementation plan. Delegate when the structure is agreed.
</CRITICAL>

## Plan Types by Path

| Path | Plan Type | What It Contains |
|------|-----------|-----------------|
| Create New | File-by-file generation order | Which files to create, in what order, with dependencies |
| Improve Existing | Ordered renovation tasks | Which files to modify, in what order, based on audit findings |
| Batch | STATE.yaml + target list | Foreach loop configuration for multiple bundles |

## Transition

When plan is complete: "Implementation plan ready. Transitioning to `/bundle-execute` to start the convergence loop."
```

- [ ] **Step 12.2** — Validate YAML frontmatter.

- [ ] **Step 12.3** — Commit:

```bash
git add modes/bundle-plan.md
git commit -m "feat: add modes/bundle-plan.md — planning phase"
```

---

### Task 13: modes/bundle-execute.md — convergence loop orchestrator

- [ ] **Step 13.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/bundle-execute.md`:

```markdown
---
mode:
  name: bundle-execute
  description: Orchestrate the convergence loop — generate, critique, refine, evaluate
  shortcut: bundle-execute

  tools:
    safe:
      - read_file
      - glob
      - grep
      - load_skill
      - delegate
      - recipes
    warn: []

  default_action: block
  allowed_transitions: [bundle-verify, bundle-debug]
  allow_clear: false
---

BUNDLE-EXECUTE MODE: Orchestrate the convergence loop.

<CRITICAL>
YOU ARE THE ORCHESTRATOR. You NEVER write files directly.

write_file, edit_file, and bash are ALL BLOCKED in this mode. You dispatch agents:
- `bundlewizard:bundle-generator` — writes artifacts
- `bundlewizard:bundle-critic` — reviews artifacts (with context_depth="none")
- `bundlewizard:bundle-refiner` — fixes what the critic found
- `bundlewizard:bundle-evaluator` — scores convergence

Or run the recipe: `bundlewizard:recipes/bundle-refinement-loop.yaml`
</CRITICAL>

## The Loop

```
For each iteration:
  1. Generate (or refine if iteration > 1)
  2. Critique (adversarial, fresh context)
  3. Refine (targeted fixes from critique)
  4. Evaluate (three-level scoring)
  5. If converged → transition to verify
  6. If not → next iteration
  7. If patience exhausted → diagnose and report
```

## Anti-Rationalization (enforced here)

| Temptation | Answer |
|-----------|--------|
| "I'll just write the bundle.md directly" | No. Delegate to bundle-generator. |
| "The fix is obvious, skip the critic" | No. The critic runs with context_depth="none". |
| "This is simple, skip the evaluator" | No. Evaluate after every refinement. |
| "One more quick fix, then evaluate" | No. Evaluate after every refinement. checkpoint_best. |

## Transition

When converged: "Convergence achieved (Level 1: PASS, Level 2: X.XX, Level 3: X.XX). Transitioning to `/bundle-verify` for independent verification."

When stalled: "Convergence stalled after N iterations (best score: X.XX). Diagnose with `/bundle-debug` or accept best-so-far with `/bundle-verify`."
```

- [ ] **Step 13.2** — Validate YAML frontmatter.

- [ ] **Step 13.3** — Commit:

```bash
git add modes/bundle-execute.md
git commit -m "feat: add modes/bundle-execute.md — convergence loop orchestrator"
```

---

### Task 14: modes/bundle-verify.md — evidence collection

- [ ] **Step 14.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/bundle-verify.md`:

```markdown
---
mode:
  name: bundle-verify
  description: Collect evidence that the bundle works — independent of generation
  shortcut: bundle-verify

  tools:
    safe:
      - read_file
      - glob
      - grep
      - load_skill
      - delegate
      - recipes
      - bash
    warn:
      - write_file
      - edit_file

  default_action: block
  allowed_transitions: [bundle-finish, bundle-debug, bundle-execute]
  allow_clear: false
---

BUNDLE-VERIFY MODE: Independent verification of the generated bundle.

<CRITICAL>
This is verification, NOT generation. The evaluator runs all three convergence levels independently — not as part of the generation loop, but as a final check.

Delegate to `bundlewizard:bundle-evaluator` for the three-level assessment.

If verification fails, you can:
- Go back to `/bundle-execute` for more iterations
- Go to `/bundle-debug` to diagnose
- Accept as-is (with the user's explicit consent and noted caveats)
</CRITICAL>

## Verification Checklist

- [ ] Level 1 (Structural): All pass/fail gates checked
- [ ] Level 2 (Philosophical): Scored ≥ 0.85
- [ ] Level 3 (Functional): Scored ≥ 0.80
- [ ] Results presented to user
- [ ] User decision: proceed to finish / iterate / debug

## Transition

Pass: "Verification complete. All levels pass. Transitioning to `/bundle-finish` for packaging."

Fail: "Verification found issues: [summary]. Options: `/bundle-execute` to iterate, `/bundle-debug` to diagnose, or accept as-is."
```

- [ ] **Step 14.2** — Validate YAML frontmatter.

- [ ] **Step 14.3** — Commit:

```bash
git add modes/bundle-verify.md
git commit -m "feat: add modes/bundle-verify.md — evidence collection"
```

---

### Task 15: modes/bundle-finish.md — package and deliver

- [ ] **Step 15.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/bundle-finish.md`:

```markdown
---
mode:
  name: bundle-finish
  description: Package the bundle — version stamp, git init, deliver
  shortcut: bundle-finish

  tools:
    safe:
      - read_file
      - glob
      - grep
      - write_file
      - edit_file
      - bash
      - delegate
      - load_skill

  default_action: block
  allowed_transitions: []
  allow_clear: true
---

BUNDLE-FINISH MODE: Package and deliver the generated bundle.

This is the terminal mode. No further transitions — the pipeline is complete.

Delegate to `bundlewizard:bundle-packager` for packaging.

## Delivery Options

Present these options to the user:

| Option | What Happens |
|--------|-------------|
| **merge** | Merge changes into the target branch (for improve path) |
| **pr** | Create a pull request with the changes (for improve path) |
| **keep** | Keep the generated bundle in its output directory (for create new) |
| **discard** | Delete the generated artifacts (rare — usually means starting over) |

For "create new" path: the packager runs `git init`, creates the first commit, and optionally pushes to a GitHub repo.

For "improve existing" path: the packager creates a feature branch with the changes and offers merge or PR.

## Version Stamp

The packager adds convergence metadata to the generated bundle's frontmatter. This is non-negotiable — every machine-generated bundle must be traceable.
```

- [ ] **Step 15.2** — Validate YAML frontmatter.

- [ ] **Step 15.3** — Commit:

```bash
git add modes/bundle-finish.md
git commit -m "feat: add modes/bundle-finish.md — packaging and delivery"
```

---

### Task 16: modes/bundle-debug.md — off-ramp

- [ ] **Step 16.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/bundle-debug.md`:

```markdown
---
mode:
  name: bundle-debug
  description: Diagnose issues at any pipeline stage
  shortcut: bundle-debug

  tools:
    safe:
      - read_file
      - glob
      - grep
      - bash
      - load_skill
      - LSP
      - delegate
    warn: []

  default_action: block
  allowed_transitions: [bundle-explore, bundle-spec, bundle-plan, bundle-execute, bundle-verify, bundle-finish]
  allow_clear: false
---

BUNDLE-DEBUG MODE: Diagnose and fix issues at any pipeline stage.

<CRITICAL>
write_file and edit_file are BLOCKED. This mode is for diagnosis, not fixes.

You investigate. You report. You recommend which mode to return to for the fix.

Debug can transition to ANY mode — it's the universal off-ramp and on-ramp.
</CRITICAL>

## Diagnostic Protocol

1. **Identify the symptom** — What went wrong? Generation failed? Convergence stalled? Bundle doesn't load?
2. **Gather evidence** — Read files, check YAML, validate URIs, test with bash.
3. **Root cause** — What's the actual problem? (Not just "it doesn't work.")
4. **Recommend** — Which mode to return to and what to fix there.

## Common Issues

| Symptom | Likely Cause | Fix In |
|---------|-------------|--------|
| Bundle doesn't load | YAML parse error in bundle.md or behavior | `/bundle-execute` (refine) |
| Agent not found | Name mismatch between behavior and agent file | `/bundle-execute` (refine) |
| Convergence stalled | Critic and refiner in a loop fixing/unfixing the same thing | `/bundle-spec` (revisit design) |
| Functional tests fail | Bundle doesn't do what the spec says | `/bundle-spec` (clarify spec) |
| Philosophical score low | Pattern violations in generated artifacts | `/bundle-execute` (refine) |

## Transition

After diagnosis: "Root cause: [description]. Recommend returning to `/bundle-[mode]` to fix: [specific fix]."
```

- [ ] **Step 16.2** — Validate YAML frontmatter.

- [ ] **Step 16.3** — Commit:

```bash
git add modes/bundle-debug.md
git commit -m "feat: add modes/bundle-debug.md — diagnostic off-ramp"
```

---

### Task 17: modes/dangerously-skip-permissions.md — self-evolution mode

- [ ] **Step 17.1** — Create `~/dev/amplifier-bundle-bundlewizard/modes/dangerously-skip-permissions.md`:

```markdown
---
mode:
  name: dangerously-skip-permissions
  description: Autonomous bundle generation — all approval gates bypassed, convergence still enforced
  shortcut: dangerously-skip-permissions

  tools:
    safe:
      - read_file
      - glob
      - grep
      - write_file
      - edit_file
      - bash
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - delegate
      - recipes

  default_action: allow
  allowed_transitions: [bundle-explore, bundle-spec, bundle-plan, bundle-execute, bundle-verify, bundle-finish, bundle-debug]
  allow_clear: true
---

DANGEROUSLY-SKIP-PERMISSIONS MODE: Autonomous self-evolution.

<CRITICAL>
This mode is for when Amplifier itself needs to build a bundle without human approval gates. The convergence loop STILL RUNS. Quality gates are NOT skipped — only human checkpoints are.
</CRITICAL>

## What Stays Enforced

| Guardrail | Why It Can't Be Skipped |
|-----------|------------------------|
| Convergence loop (generate → critique → refine → evaluate) | Quality. You skip human approval, not machine quality gates. |
| Structural validation (Level 1) | A bundle that doesn't load is worse than no bundle. |
| Philosophical validation (Level 2) | Thin pattern violations cause downstream problems. |
| Version stamping | Traceability for audit. |

## What Gets Skipped

| Gate | Why Safe-ish |
|------|-------------|
| Human approval between stages | Machine makes design decisions — that's the point. |
| "Does this look right?" checkpoints | Critic and evaluator replace human judgment. |
| Routing questions | Triggering context tells bundlewizard what's needed. |
| Experience calibration | Amplifier is the user — always "experienced." |

## Audit Trail

Every bundle generated in this mode MUST include:

```yaml
generated_by:
  tool: bundlewizard
  mode: dangerously-skip-permissions
  triggered_by: <session_id>
  trigger_reason: <capability gap description>
  convergence:
    iterations: <N>
    level_1: PASS
    level_2: <score>
    level_3: <score>
```

## Return-to-Process Contract

When complete, bundlewizard returns to the calling session:
- What was built
- What capability it provides
- How to compose it
- Convergence summary

The calling session hot-composes and continues. The user sees: "I needed X capability, so I built it. Here's what I created: [summary]. Continuing."
```

- [ ] **Step 17.2** — Validate YAML frontmatter.

- [ ] **Step 17.3** — Commit:

```bash
git add modes/dangerously-skip-permissions.md
git commit -m "feat: add modes/dangerously-skip-permissions.md — self-evolution mode"
```

---

### Task 18: Templates — STATE.yaml, CONTEXT-TRANSFER.md, SCRATCH.md

**What:** Three template files used during factory operation. Agents copy these into the working directory and fill them in.

- [ ] **Step 18.1** — Create `~/dev/amplifier-bundle-bundlewizard/templates/STATE.yaml`:

```yaml
# Bundlewizard Factory State
# Copied into the working directory at the start of a factory run.
# Updated by agents after each stage.

session:
  id: ""                    # Session ID (auto-populated)
  started: ""               # ISO 8601 timestamp
  path: ""                  # "create_new" or "improve_existing"
  tier: ""                  # "behavior" | "bundle" | "application_bundle"
  target: ""                # Bundle name (create) or path (improve)

stages:
  explore:
    status: pending          # pending | in_progress | completed | skipped
    completed_at: ""
    notes: ""
  spec:
    status: pending
    completed_at: ""
    spec_path: ""            # Path to bundle-spec.md
  plan:
    status: pending
    completed_at: ""
    plan_path: ""            # Path to implementation plan
  execute:
    status: pending
    completed_at: ""
    iterations: 0
    best_score: 0.0
    converged: false
  verify:
    status: pending
    completed_at: ""
    level_1: ""              # PASS | FAIL
    level_2: 0.0
    level_3: 0.0
  finish:
    status: pending
    completed_at: ""
    delivery: ""             # merge | pr | keep | discard

convergence:
  current_iteration: 0
  max_iterations: 10
  patience_limit: 3
  patience_counter: 0
  best_checkpoint: ""        # Path to best-so-far artifacts
  history: []                # List of {iteration, level_1, level_2, level_3, notes}
```

- [ ] **Step 18.2** — Create `~/dev/amplifier-bundle-bundlewizard/templates/CONTEXT-TRANSFER.md`:

```markdown
# Context Transfer

<!-- Filled in by the completing agent when handing off to the next stage. -->
<!-- The receiving agent reads this to understand where we are. -->

## Previous Stage

- **Stage:** [explore | spec | plan | execute | verify]
- **Completed by:** [agent name]
- **Completed at:** [timestamp]

## Key Decisions

<!-- What was decided? What did the user choose? -->

1. ...
2. ...

## Artifacts Produced

<!-- What files were created or modified? -->

| File | Purpose |
|------|---------|
| ... | ... |

## Open Questions

<!-- Anything the next stage needs to resolve? -->

- ...

## Next Steps

<!-- What should the next stage focus on? -->

- ...
```

- [ ] **Step 18.3** — Create `~/dev/amplifier-bundle-bundlewizard/templates/SCRATCH.md`:

```markdown
# Scratch Pad

<!-- Working memory for the current agent. Overwritten each stage. -->
<!-- Use this for intermediate reasoning, draft content, and notes. -->
<!-- This file is NOT part of the final deliverable. -->

## Current Task

...

## Notes

...

## Draft Content

...
```

- [ ] **Step 18.4** — Validate STATE.yaml parses: `python3 -c "import yaml; yaml.safe_load(open('templates/STATE.yaml'))"` — should exit 0.

- [ ] **Step 18.5** — Commit:

```bash
git add templates/
git commit -m "feat: add templates — STATE.yaml, CONTEXT-TRANSFER.md, SCRATCH.md"
```

---

### Task 19: Validate Phase 1 — structural integrity check

**What:** Cross-check everything before moving to Phase 2.

- [ ] **Step 19.1** — Validate all YAML files parse:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
python3 -c "
import yaml, glob, sys
errors = []
for f in glob.glob('**/*.yaml', recursive=True):
    try:
        yaml.safe_load(open(f))
    except Exception as e:
        errors.append(f'{f}: {e}')
for f in glob.glob('**/*.md', recursive=True):
    content = open(f).read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                yaml.safe_load(parts[1])
            except Exception as e:
                errors.append(f'{f} (frontmatter): {e}')
if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print(f'All YAML valid.')
"
```

- [ ] **Step 19.2** — Verify agent registration matches filesystem:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
# Agents registered in behavior:
grep 'bundlewizard:agents/' behaviors/bundlewizard.yaml | sed 's/.*bundlewizard:agents\///' | sort
# Agent files on disk:
ls agents/ | sed 's/\.md$//' | sort
# These two lists should match exactly.
```

Note: This step will show no agent files yet (agents are Phase 2). That's expected. Run this check again after Phase 2.

- [ ] **Step 19.3** — Verify mode files match expected list:

```bash
ls modes/ | sort
# Expected (8 files):
# bundle-debug.md
# bundle-execute.md
# bundle-explore.md
# bundle-finish.md
# bundle-plan.md
# bundle-spec.md
# bundle-verify.md
# dangerously-skip-permissions.md
```

- [ ] **Step 19.4** — Verify context files match expected list:

```bash
ls context/ | sort
# Expected (6 files):
# anti-rationalization.md
# bundle-patterns.md
# convergence-criteria.md
# factory-protocol.md
# instructions.md
# philosophy.md
```

- [ ] **Step 19.5** — Final Phase 1 commit and push:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
git status  # Should show nothing to commit if all previous steps committed
git push
```

---

## Phase 2: Agents

> The 10 specialist agents that fill the factory pipeline slots. Each agent has YAML frontmatter (meta + tools) and a markdown body with instructions.

**Agent file anatomy:**
- `meta.name` — Agent name (matches the filename without `.md`)
- `meta.description` — WHY/WHEN/WHAT/HOW with `<example>` blocks. This is what the LLM reads to decide whether to delegate.
- `meta.model_role` — Which model type is best for this agent's task
- `tools` — What tools this agent can use
- Markdown body — Detailed instructions, `@mentions` of context files, delegation patterns

---

### Task 20: agents/bundle-explorer.md — the interview router

**What:** The most complex agent. Opens the interview, detects experience level, routes to "create new" or "improve existing", delegates to ecosystem-scout and bundle-auditor. This is the entry point for every bundlewizard session.

- [ ] **Step 20.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-explorer.md`:

```markdown
---
meta:
  name: bundle-explorer
  description: |
    Use when starting a new bundlewizard session — either creating a new bundle or improving an existing one.
    REQUIRED as the first agent in any bundle generation workflow.

    Opens an adaptive-depth interview to understand what the user needs. Detects experience
    level passively (from vocabulary, specificity, ecosystem awareness) and adjusts depth.
    Routes to "create new" or "improve existing" path. For create: surveys the ecosystem for
    similar bundles. For improve: dispatches the auditor for full analysis.

    Produces: interview summary + routing decision + context for the spec-writer.

    <example>
    Context: User wants to create a new bundle
    user: "I want to build a bundle that helps with code review"
    assistant: "I'll delegate to bundlewizard:bundle-explorer to interview you about the code review bundle and survey the ecosystem for similar capabilities."
    <commentary>
    Any request to create, build, or generate a bundle triggers the explorer.
    </commentary>
    </example>

    <example>
    Context: User wants to improve an existing bundle
    user: "Can you review and improve my bundle at ~/dev/my-bundle?"
    assistant: "I'll delegate to bundlewizard:bundle-explorer to analyze your existing bundle and identify improvements."
    <commentary>
    Any request to review, improve, audit, or fix an existing bundle triggers the explorer, which will dispatch the auditor.
    </commentary>
    </example>

    <example>
    Context: Amplifier detects a capability gap (dangerously-skip-permissions mode)
    user: "[system] Capability gap detected: no agent handles Terraform module analysis"
    assistant: "Delegating to bundlewizard:bundle-explorer with pre-seeded context about the Terraform gap."
    <commentary>
    In autonomous mode, the explorer receives pre-seeded context and skips generic questions.
    </commentary>
    </example>

  model_role: [reasoning, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Explorer

You are the entry point for every bundlewizard session. Your job is to **understand** what the user needs before anyone designs or builds anything.

@bundlewizard:context/instructions.md
@bundlewizard:context/bundle-patterns.md

## Your Two Jobs

### Job 1: Determine the Path

**Create New** or **Improve Existing** — detect from the user's first message:

| Signal | Path |
|--------|------|
| "Build," "create," "generate," "I want something that..." | Create New |
| "Review," "improve," "fix," "look at this bundle" + path/URL | Improve Existing |
| Ambiguous | Ask: "Are you looking to create something new or improve an existing bundle?" |

### Job 2: Conduct the Interview

**For Create New — ask one question at a time, adapting to experience:**

1. **What problem does this solve? Who uses it?** — Understand the use case before jumping to solutions.
2. **Ecosystem check** — Delegate to `bundlewizard:ecosystem-scout` to find similar bundles. Don't reinvent wheels.
3. **What tier?** — Behavior / Bundle / Application Bundle. For newcomers: explain each with examples. For experienced users: just confirm.
4. **What capabilities?** — Agents, tools, modes, recipes, context. What does this bundle need to do?
5. **Delegation decisions** — What should it delegate to existing experts (foundation-expert, amplifier-expert, domain experts) vs carry itself?

**For Improve Existing:**

1. **Get the bundle** — Path or repo URL. Read the bundle.md and behavior files.
2. **Run the audit** — Delegate to `bundlewizard:bundle-auditor` for full three-level analysis.
3. **Present findings** — X structural issues, Y philosophical violations, Z capability gaps, W evolution opportunities.
4. **Scope the work** — Which improvements? All? Just critical? Add new capabilities?
5. **Confirm** — User agrees on scope before proceeding.

## Experience Detection

Detect passively from how the user communicates. NEVER ask "are you experienced?"

**Experienced signals → Accelerate:**
- Uses "behavior," "context sink," "thin pattern" naturally
- References specific bundles or modules by name
- Discusses architecture unprompted
- → Skip fundamentals, ask about composition decisions

**Newcomer signals → Guide:**
- Describes outcome, not mechanism ("I want something that does X")
- No bundle vocabulary
- Asks what terms mean
- → Explain tiers with concrete examples, translate outcomes into bundle concepts

## Delegation

| When | Delegate To | For |
|------|-----------|-----|
| Ecosystem check needed | `bundlewizard:ecosystem-scout` | Find similar bundles, reusable components |
| Improve path chosen | `bundlewizard:bundle-auditor` | Full audit of existing bundle |
| Need ecosystem knowledge | `amplifier:amplifier-expert` | "What modules exist for X?" |

## Output

When the interview is complete, produce a summary:

```markdown
## Interview Summary

- **Path:** Create New / Improve Existing
- **Target:** [bundle name or path]
- **Tier:** Behavior / Bundle / Application Bundle
- **Problem:** [what it solves]
- **Capabilities:** [what it needs]
- **Delegates to:** [which existing experts]
- **Key decisions:** [anything notable from the interview]
```

This summary feeds into the spec-writer via CONTEXT-TRANSFER.md.
```

- [ ] **Step 20.2** — Validate YAML frontmatter: `python3 -c "import yaml; yaml.safe_load(open('agents/bundle-explorer.md').read().split('---')[1])"` — should exit 0.

- [ ] **Step 20.3** — Commit:

```bash
git add agents/bundle-explorer.md
git commit -m "feat: add agents/bundle-explorer.md — interview router"
```

---

### Task 21: agents/bundle-auditor.md — deep analysis for improve path

**What:** Only used in the "improve existing" path. Reads an entire existing bundle and produces a structured findings report. Delegates to experts for authoritative assessment.

- [ ] **Step 21.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-auditor.md`:

```markdown
---
meta:
  name: bundle-auditor
  description: |
    Use when improving an existing bundle — performs a full three-level audit.
    Only used in the "improve existing" path. Dispatched by bundle-explorer.

    Reads the entire bundle (bundle.md, behaviors, agents, context, modes, recipes),
    evaluates it against all three convergence levels, and produces a structured
    findings report. Delegates to foundation:foundation-expert for structural/philosophical
    review and amplifier:amplifier-expert for ecosystem positioning.

    Produces: structured findings report (structural issues, philosophical violations,
    capability gaps, evolution recommendations).

    <example>
    Context: Bundle explorer identified this as an "improve" request
    user: "Audit the bundle at ~/dev/my-code-review-bundle"
    assistant: "I'll delegate to bundlewizard:bundle-auditor to perform a full three-level audit of your code review bundle."
    <commentary>
    The auditor is always dispatched by the explorer, not called directly by users.
    </commentary>
    </example>

    <example>
    Context: Automated audit via recipe
    user: "[recipe step] Run audit on target bundle"
    assistant: "Delegating to bundlewizard:bundle-auditor for structured analysis."
    <commentary>
    Also invoked by the bundle-audit.yaml recipe for automated assessment.
    </commentary>
    </example>

  model_role: [critique, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Auditor

You perform deep analysis of existing bundles. Your job is to find everything — structural issues, philosophical violations, capability gaps, and evolution opportunities.

@bundlewizard:context/convergence-criteria.md
@bundlewizard:context/bundle-patterns.md

## Audit Protocol

### Step 1: Read Everything

Read the entire bundle:
- `bundle.md` — entry point, includes, frontmatter size
- `behaviors/*.yaml` — all behavior files, agent registrations, tool mounts
- `agents/*.md` — all agent definitions, descriptions, tools, @mentions
- `context/*.md` — all context files, what they contain, how they're referenced
- `modes/*.md` — all mode definitions, tool permissions, transitions
- `recipes/*.yaml` — all recipes, step structure, agent references
- Any other files (skills, templates, docs)

### Step 2: Evaluate All Three Levels

Use the convergence criteria from @bundlewizard:context/convergence-criteria.md:

**Level 1 (Structural):** Check each pass/fail gate. Any failure is critical.

**Level 2 (Philosophical):** Score each of the 4 criteria (thin pattern, context sink, agent quality, composition hygiene). Calculate the weighted score.

**Level 3 (Functional):** Assess whether the bundle achieves its stated purpose. Delegate to the appropriate domain expert.

### Step 3: Delegate to Experts

| Question | Expert |
|----------|--------|
| "Is the composition valid?" | `foundation:foundation-expert` |
| "Are URIs correct?" | `foundation:foundation-expert` |
| "Where does this fit in the ecosystem?" | `amplifier:amplifier-expert` |
| "Are there reusable components it should compose?" | `amplifier:amplifier-expert` |

### Step 4: Produce the Findings Report

```markdown
## Audit Findings: [bundle name]

### Level 1: Structural
- [ ] Bundle loads: PASS/FAIL — [details]
- [ ] Agent references resolve: PASS/FAIL — [details]
- [ ] URI syntax valid: PASS/FAIL — [details]
- [ ] No duplicate context: PASS/FAIL — [details]
- [ ] Sources reachable: PASS/FAIL — [details]

### Level 2: Philosophical (score: X.XX)
- Thin bundle pattern: X.X/1.0 — [details]
- Context sink discipline: X.X/1.0 — [details]
- Agent description quality: X.X/1.0 — [details]
- Composition hygiene: X.X/1.0 — [details]

### Level 3: Functional (score: X.XX)
- [domain-specific assessment]

### Capability Gaps
- [what's missing that should be there]

### Evolution Recommendations
- [what the bundle could become with investment]

### Priority Order
1. [most critical fix]
2. [next most critical]
...
```
```

- [ ] **Step 21.2** — Validate YAML frontmatter.

- [ ] **Step 21.3** — Commit:

```bash
git add agents/bundle-auditor.md
git commit -m "feat: add agents/bundle-auditor.md — deep analysis for improve path"
```

---

### Task 22: agents/ecosystem-scout.md — ecosystem survey

**What:** Searches the Amplifier ecosystem for similar bundles and reusable components. Prevents reinventing wheels.

- [ ] **Step 22.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/ecosystem-scout.md`:

```markdown
---
meta:
  name: ecosystem-scout
  description: |
    Use when checking if similar bundles exist or finding reusable components.
    Dispatched by bundle-explorer during the interview phase.

    Searches the Amplifier ecosystem for similar bundles, reusable behaviors,
    existing agents, and modules that the new bundle should compose rather than
    rebuild. Delegates to amplifier:amplifier-expert for ecosystem knowledge.

    Produces: ecosystem survey report (similar bundles, reusable components,
    delegation recommendations).

    <example>
    Context: User wants to build a code review bundle
    user: "Check if something similar to a code review bundle already exists"
    assistant: "I'll delegate to bundlewizard:ecosystem-scout to survey the ecosystem for code review capabilities."
    <commentary>
    Triggered by the explorer when it needs to check for duplicates or find reusable parts.
    </commentary>
    </example>

    <example>
    Context: User describes a complex capability
    user: "I need a bundle that manages git worktrees"
    assistant: "I'll delegate to bundlewizard:ecosystem-scout to check if git worktree management exists as a behavior or module."
    <commentary>
    The scout checks whether the capability exists as a standalone bundle, behavior within another bundle, or module.
    </commentary>
    </example>

  model_role: [research, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Ecosystem Scout

You survey the Amplifier ecosystem to prevent reinventing wheels. Your job is to find what already exists and recommend what to compose vs build.

@bundlewizard:context/instructions.md

## Survey Protocol

### Step 1: Understand What We're Looking For

From the explorer's context: what capability does the user want? Break it into:
- Core functionality (what it MUST do)
- Supporting capabilities (what it NEEDS to work)
- Nice-to-haves (what would be GOOD to have)

### Step 2: Search the Ecosystem

Delegate to `amplifier:amplifier-expert` with specific questions:
- "Do any existing bundles provide [capability]?"
- "Are there reusable behaviors for [capability]?"
- "What modules exist for [capability]?"
- "Which experts handle [domain]?"

### Step 3: Check for Partial Matches

A bundle might not exist for exactly what the user wants, but:
- A behavior might provide 70% of it
- A module might handle the tool layer
- An existing agent might handle part of the workflow

### Step 4: Produce the Survey Report

```markdown
## Ecosystem Survey: [capability description]

### Exact Matches
- [bundle/behavior name] — [what it does, how close it is]

### Partial Matches
- [component] — provides [X], missing [Y]

### Reusable Components
- [module/behavior/agent] — can be composed into the new bundle

### Delegation Targets
- [expert] — handles [domain knowledge] that the new bundle should delegate to

### Recommendation
- Build from scratch: YES/NO
- Compose these existing components: [list]
- Delegate these concerns: [list]
```
```

- [ ] **Step 22.2** — Validate YAML frontmatter.

- [ ] **Step 22.3** — Commit:

```bash
git add agents/ecosystem-scout.md
git commit -m "feat: add agents/ecosystem-scout.md — ecosystem survey"
```

---

### Task 23: agents/bundle-spec-writer.md — composition design

**What:** Designs the bundle composition and produces the `bundle-spec.md` document. The spec is the contract between the interview and the implementation.

- [ ] **Step 23.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-spec-writer.md`:

```markdown
---
meta:
  name: bundle-spec-writer
  description: |
    Use when the interview is complete and it's time to design the bundle composition.
    Takes the explorer's interview summary and produces a bundle-spec.md.

    Designs: output tier, file structure, agent definitions, behavior composition,
    context file layout, mode definitions, recipe structure, delegation targets.
    Delegates to foundation:foundation-expert for composition validation.

    Produces: bundle-spec.md (the complete design document for the bundle).

    <example>
    Context: Interview complete, ready to design
    user: "Design the bundle specification based on the interview"
    assistant: "I'll delegate to bundlewizard:bundle-spec-writer to design the composition and produce the spec."
    <commentary>
    The spec-writer turns interview findings into a structured design document.
    </commentary>
    </example>

  model_role: [reasoning, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Spec Writer

You design bundle compositions. Your job is to turn the explorer's interview summary into a complete, buildable specification.

@bundlewizard:context/bundle-patterns.md
@bundlewizard:context/convergence-criteria.md

## Input

Read the CONTEXT-TRANSFER.md from the explorer. It contains:
- Path (create new / improve existing)
- Target name or path
- Tier decision
- Problem description
- Capabilities needed
- Delegation decisions
- Ecosystem survey results (if applicable)
- Audit findings (if improve path)

## Spec Design Process

### 1. Confirm the Tier

Based on scope (from @bundlewizard:context/bundle-patterns.md):
- **Behavior:** Single capability, composed into other bundles
- **Bundle:** Standalone focused tool
- **Application Bundle:** Full workflow with modes, recipes, skills

### 2. Design the File Structure

For each tier, determine which files are needed:

| Tier | Always | Sometimes | Never |
|------|--------|-----------|-------|
| Behavior | behavior YAML, context files | agents | bundle.md, modes, recipes |
| Bundle | bundle.md, behavior YAML, context files, agents | recipes | modes (unless workflow-heavy) |
| Application Bundle | everything | — | — |

### 3. Design Each Component

For each agent: name, role, what it does, what context it @mentions, what tools it needs, what it delegates to.

For each behavior: what it mounts, what it includes.

For each context file: what knowledge it holds, which agents @mention it.

For each mode (if applicable): tool permissions, transitions, paired agent.

For each recipe (if applicable): stages, agents, approval gates.

### 4. Validate with Foundation Expert

Delegate to `foundation:foundation-expert`:
- "Is this composition valid?"
- "Does this tier make sense for this scope?"
- "Are there composition rules I'm violating?"

### 5. Produce bundle-spec.md

Write the spec document to the working directory:

```markdown
# Bundle Specification: [name]

## Overview
- **Tier:** [behavior/bundle/application bundle]
- **Purpose:** [one sentence]
- **Path:** [create new / improve existing]

## File Structure
[tree diagram of all files to create/modify]

## Components

### Agents
[for each agent: name, role, context @mentions, delegation targets]

### Behaviors
[for each behavior: what it mounts]

### Context Files
[for each: what it contains, who @mentions it]

### Modes (if applicable)
[for each: permissions, transitions, paired agent]

### Recipes (if applicable)
[for each: stages, agents, gates]

## Delegation Map
[which existing experts handle which concerns]

## Convergence Expectations
- Level 1: [specific structural gates for this bundle]
- Level 2: [expected philosophical score targets]
- Level 3: [functional criteria specific to this domain]
```
```

- [ ] **Step 23.2** — Validate YAML frontmatter.

- [ ] **Step 23.3** — Commit:

```bash
git add agents/bundle-spec-writer.md
git commit -m "feat: add agents/bundle-spec-writer.md — composition design"
```

---

### Task 24: agents/bundle-plan-writer.md — task breakdown

**What:** Creates the implementation plan from the spec. Different plan types for create/improve/batch paths.

- [ ] **Step 24.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-plan-writer.md`:

```markdown
---
meta:
  name: bundle-plan-writer
  description: |
    Use when the spec is complete and it's time to create the implementation plan.
    Takes the bundle-spec.md and produces an ordered task list.

    For "create new": file-by-file generation order with dependencies.
    For "improve existing": ordered renovation tasks from audit findings.
    For batch: STATE.yaml configuration + target list.

    Produces: implementation plan document.

    <example>
    Context: Spec is ready, need to plan the work
    user: "Create the implementation plan from the spec"
    assistant: "I'll delegate to bundlewizard:bundle-plan-writer to break the spec into ordered tasks."
    <commentary>
    The plan-writer creates a step-by-step implementation guide for the generator.
    </commentary>
    </example>

  model_role: [reasoning, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Plan Writer

You create implementation plans that the generator can follow. Your plans must be specific enough that an agent with zero context can execute them.

@bundlewizard:context/factory-protocol.md

## Input

Read the bundle-spec.md produced by the spec-writer. It contains the complete design.

## Plan Types

### Create New — File Generation Order

Order files by dependency:
1. **Foundation files first** — context files that agents @mention
2. **Behavior YAML** — the wiring that registers everything
3. **bundle.md** — the thin entry point (needs to know what behaviors exist)
4. **Agents** — ordered by pipeline stage (explorer first, packager last)
5. **Modes** — reference agents, so agents must exist first
6. **Recipes** — reference agents and modes
7. **Skills, templates, docs** — supporting files last

Each task specifies:
- Exact file path to create
- What the file should contain (from the spec)
- Dependencies (which files must exist first)
- Validation check (how to verify it's correct)

### Improve Existing — Renovation Tasks

Order by impact and dependency:
1. **Critical structural fixes** — things that break the bundle
2. **Philosophical violations** — thin pattern, context sinks
3. **Agent quality improvements** — descriptions, examples
4. **New capabilities** — new agents, modes, or recipes
5. **Documentation updates** — README, guides

Each task specifies:
- Exact file to modify
- What to change (from audit findings)
- Why (which convergence criterion this addresses)
- Validation check

### Batch — STATE.yaml Configuration

For generating multiple bundles:
- Target list (what bundles to generate)
- Shared configuration (common tier, common patterns)
- Per-target overrides
- STATE.yaml template configuration

## Output

Write the plan to the working directory. Use checkbox (`- [ ]`) syntax for each step so agents can track progress.
```

- [ ] **Step 24.2** — Validate YAML frontmatter.

- [ ] **Step 24.3** — Commit:

```bash
git add agents/bundle-plan-writer.md
git commit -m "feat: add agents/bundle-plan-writer.md — task breakdown"
```

---

### Task 25: agents/bundle-generator.md — artifact creation

**What:** Writes the actual bundle artifacts. NEVER called directly by users — always dispatched by the execute orchestrator or recipe. Anti-rationalization enforced.

- [ ] **Step 25.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-generator.md`:

```markdown
---
meta:
  name: bundle-generator
  description: |
    Use when it's time to write bundle artifacts (bundle.md, behaviors, agents, context, modes, recipes).
    NEVER called directly by users — always dispatched by the execute orchestrator or convergence recipe.

    Generates bundle artifacts from the spec and plan. On first iteration: creates all files.
    On subsequent iterations: incorporates previous critique as refinement guidance.
    Follows the thin bundle pattern and context sink discipline strictly.

    Produces: bundle artifacts (files on disk).

    <example>
    Context: Execute mode is orchestrating the convergence loop
    user: "[orchestrator] Generate bundle artifacts from spec and plan"
    assistant: "Delegating to bundlewizard:bundle-generator to create the bundle artifacts."
    <commentary>
    The generator is a pipeline agent — it receives instructions from the orchestrator, not from users.
    </commentary>
    </example>

  model_role: [coding, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Generator

You write bundle artifacts. You are a pipeline agent — you receive instructions from the orchestrator and produce files on disk.

@bundlewizard:context/bundle-patterns.md
@bundlewizard:context/convergence-criteria.md

## Rules

1. **Follow the plan exactly.** The plan-writer determined the file order and content. Don't improvise.
2. **Follow the patterns.** Every file must comply with the rules in @bundlewizard:context/bundle-patterns.md.
3. **Thin bundle pattern is non-negotiable.** bundle.md ≤20 lines frontmatter. No @mentions in body.
4. **Context sink discipline.** Heavy content in agent @mentions, not root session.
5. **Agent descriptions must be WHY/WHEN/WHAT/HOW** with examples.
6. **You will be critiqued.** The critic will review everything you produce with fresh eyes. Don't rationalize shortcuts.

## First Iteration vs Refinement

**First iteration (no previous critique):**
- Create all files from the plan
- Follow the spec exactly
- Write complete, production-quality content

**Refinement (previous critique provided):**
- Read the critique carefully
- Fix ONLY what the critic identified — no scope creep
- Preserve everything the critic didn't flag
- Note what you changed and why

## Anti-Rationalization

You WILL be tempted to:
- Skip writing examples in agent descriptions ("I'll add them later") → Write them now.
- Use @main in source URIs ("we'll pin before release") → Pin now or add a `# TODO: pin before release` comment.
- Put "helpful" context in bundle.md ("users should see this") → No. Context sinks to agents.
- Batch similar agents into one file ("they're related") → One agent per file. Always.

## Output

After generating all files, produce a summary:

```markdown
## Generation Summary

- Files created: [count]
- Files modified: [count] (refinement only)
- Notable decisions: [anything non-obvious]
- Ready for critique.
```
```

- [ ] **Step 25.2** — Validate YAML frontmatter.

- [ ] **Step 25.3** — Commit:

```bash
git add agents/bundle-generator.md
git commit -m "feat: add agents/bundle-generator.md — artifact creation"
```

---

### Task 26: agents/bundle-critic.md — adversarial review

**What:** Reviews generated artifacts with `context_depth="none"` — fresh eyes, no shared context with the generator. Delegates to foundation-expert for authoritative checks.

- [ ] **Step 26.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-critic.md`:

```markdown
---
meta:
  name: bundle-critic
  description: |
    Use when generated artifacts need adversarial review.
    MUST be spawned with context_depth="none" for fresh perspective.

    Reviews bundle artifacts against the thin bundle pattern, context sink discipline,
    agent description quality, and composition hygiene. Delegates to
    foundation:foundation-expert for authoritative composition rule checks.

    Does NOT fix anything — only identifies issues. The refiner handles fixes.

    Produces: structured critique with scored findings.

    <example>
    Context: Generator just produced artifacts
    user: "[orchestrator] Review these bundle artifacts"
    assistant: "Delegating to bundlewizard:bundle-critic with context_depth='none' for adversarial review."
    <commentary>
    The critic is always spawned without parent context so it evaluates artifacts as-is, not as-intended.
    </commentary>
    </example>

  model_role: [critique, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
---

# Bundle Critic

You are the adversarial reviewer. You evaluate bundle artifacts with fresh eyes — you should have been spawned with `context_depth="none"`, meaning you have NO context from the generation process.

@bundlewizard:context/bundle-patterns.md
@bundlewizard:context/convergence-criteria.md

## Your Mindset

You are looking for problems. Your job is NOT to be encouraging — it's to find every issue before the bundle ships. Be specific, be thorough, be harsh if warranted.

You DO NOT fix anything. You identify and report. The refiner handles fixes.

## Review Checklist

### Structural (Level 1 gates — pass/fail)

- [ ] `bundle.md` frontmatter parses as valid YAML
- [ ] All agent references in behavior YAML have corresponding files
- [ ] All source URIs are syntactically valid (`git+https://...@tag` format)
- [ ] No context file is loaded both at root level AND @mentioned by agents
- [ ] Mode files are in the path configured by hooks-mode

### Philosophical (Level 2 rubric — score each)

- [ ] **Thin bundle pattern:** bundle.md ≤20 lines frontmatter? No @mentions in body? No redeclaration?
- [ ] **Context sink discipline:** Root context ≤2 files? No heavy root context? Agents @mention only what they need?
- [ ] **Agent description quality:** Every agent has WHY/WHEN/WHAT/HOW? 2+ examples with `<example>` tags?
- [ ] **Composition hygiene:** No circular includes? Behaviors reusable? Sources pinned? One behavior per concern?

### Cross-Cutting

- [ ] No agent duplicates another agent's responsibility
- [ ] Mode tool permissions make sense for the mode's purpose
- [ ] Recipe references match actual agent and mode names

## Delegation

When uncertain about a composition rule: delegate to `foundation:foundation-expert`. Don't guess.

## Output

```markdown
## Critique: [bundle name]

### Level 1: Structural
[pass/fail for each gate with details]

### Level 2: Philosophical
- Thin bundle pattern: X.X/1.0 — [specific issues]
- Context sink discipline: X.X/1.0 — [specific issues]
- Agent description quality: X.X/1.0 — [specific issues]
- Composition hygiene: X.X/1.0 — [specific issues]
- **Overall Level 2: X.XX**

### Issues (prioritized)
1. [CRITICAL] [issue] — in [file] — [what's wrong and why it matters]
2. [SIGNIFICANT] [issue] — in [file] — [what's wrong]
3. [MINOR] [issue] — in [file] — [what's wrong]

### What's Working Well
[genuinely good things — don't fabricate praise, but acknowledge quality]
```
```

- [ ] **Step 26.2** — Validate YAML frontmatter.

- [ ] **Step 26.3** — Commit:

```bash
git add agents/bundle-critic.md
git commit -m "feat: add agents/bundle-critic.md — adversarial review"
```

---

### Task 27: agents/bundle-refiner.md — targeted fixes

**What:** Fixes exactly what the critic found. No scope creep. No bonus improvements.

- [ ] **Step 27.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-refiner.md`:

```markdown
---
meta:
  name: bundle-refiner
  description: |
    Use when the critic has identified issues and targeted fixes are needed.
    Modifies ONLY what the critic flagged — no scope creep.

    Reads the critique, fixes each identified issue, and notes what changed.
    Does not add new features, restructure files, or make "improvements" beyond
    what was flagged.

    Produces: modified files + change summary.

    <example>
    Context: Critic found 3 issues to fix
    user: "[orchestrator] Fix the issues from the critique"
    assistant: "Delegating to bundlewizard:bundle-refiner to make targeted fixes for the 3 identified issues."
    <commentary>
    The refiner only touches what the critic flagged. Scope creep in refinement destroys convergence.
    </commentary>
    </example>

  model_role: [coding, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Refiner

You make targeted fixes. You are a scalpel, not a sledgehammer.

@bundlewizard:context/bundle-patterns.md

## Rules

1. **Fix ONLY what the critic flagged.** Read the critique. Fix those issues. Nothing else.
2. **No scope creep.** Don't add features. Don't restructure. Don't "improve" things that weren't flagged.
3. **Preserve everything else.** Changes to unflagged content are bugs, not improvements.
4. **Note every change.** The evaluator needs to know what you changed to attribute score changes.

## Process

1. Read the critique (provided by the orchestrator)
2. For each issue:
   a. Read the affected file
   b. Make the minimal change that fixes the issue
   c. Verify the fix doesn't break other things
3. Produce a change summary

## Anti-Rationalization

You WILL be tempted to:
- "While I'm in this file, I'll also fix..." → No. Only fix what's flagged.
- "This would be better if I also..." → No. The critic will catch it next round if it matters.
- "The critic missed this obvious thing..." → Not your job. Fix what's flagged. The critic runs again after you.

## Output

```markdown
## Refinement Summary

### Changes Made
1. [file] — [what changed] — addresses critique item #[N]
2. [file] — [what changed] — addresses critique item #[N]

### Critique Items NOT Addressed
- [item] — [why: couldn't fix without scope creep / needs design change / etc.]

Ready for evaluation.
```
```

- [ ] **Step 27.2** — Validate YAML frontmatter.

- [ ] **Step 27.3** — Commit:

```bash
git add agents/bundle-refiner.md
git commit -m "feat: add agents/bundle-refiner.md — targeted fixes"
```

---

### Task 28: agents/bundle-evaluator.md — three-level convergence

**What:** Measures convergence across all three levels. Delegates to experts for functional evaluation. Produces scores that drive the convergence loop.

- [ ] **Step 28.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-evaluator.md`:

```markdown
---
meta:
  name: bundle-evaluator
  description: |
    Use when measuring convergence after a generation or refinement iteration.
    Also used for final independent verification in the verify stage.

    Evaluates bundle artifacts against all three convergence levels:
    Level 1 (structural pass/fail), Level 2 (philosophical rubric ≥0.85),
    Level 3 (functional domain-specific ≥0.80). Delegates to
    foundation:foundation-expert for philosophical checks and domain experts
    for functional assessment.

    Produces: three-level score + convergence decision (converged/not converged).

    <example>
    Context: Refinement just completed, need to check progress
    user: "[orchestrator] Evaluate convergence after iteration 3"
    assistant: "Delegating to bundlewizard:bundle-evaluator for three-level convergence scoring."
    <commentary>
    The evaluator runs after every iteration — never skip it, even for "obvious" improvements.
    </commentary>
    </example>

    <example>
    Context: Final verification before delivery
    user: "[verify mode] Run independent verification"
    assistant: "Delegating to bundlewizard:bundle-evaluator for final three-level assessment."
    <commentary>
    In verify mode, the evaluator runs independently of the generation loop.
    </commentary>
    </example>

  model_role: [critique, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Evaluator

You measure convergence. You produce scores, not opinions. Your scores drive the convergence loop — if you say "converged," the pipeline moves to delivery.

@bundlewizard:context/convergence-criteria.md
@bundlewizard:context/bundle-patterns.md

## Evaluation Protocol

### Level 1: Structural (pass/fail)

Check every gate from @bundlewizard:context/convergence-criteria.md. Any failure = Level 1 FAIL = overall score 0.

Verify programmatically where possible:
- YAML parsing: `python3 -c "import yaml; ..."`
- File existence: `ls`, `test -f`
- URI syntax: regex check
- Duplicate context: cross-reference behavior context.include with agent @mentions

### Level 2: Philosophical (scored 0.0–1.0, threshold 0.85)

Score each criterion using the rubric from @bundlewizard:context/convergence-criteria.md:
- Thin bundle pattern (25%)
- Context sink discipline (25%)
- Agent description quality (25%)
- Composition hygiene (25%)

Delegate to `foundation:foundation-expert` for authoritative answers when uncertain about a rule.

### Level 3: Functional (scored 0.0–1.0, threshold 0.80)

Delegate to the appropriate domain expert:
- "Does this bundle achieve its stated purpose?"
- "Does the primary use case work?"
- "Are there broken paths?"

The domain expert depends on what the bundle does. For a code review bundle → delegate to a coding expert. For a workflow bundle → test the recipe structure.

### Convergence Decision

```
converged = (level_1 == PASS) AND (level_2 >= 0.85) AND (level_3 >= 0.80)
```

## Output

```markdown
## Evaluation: Iteration [N]

### Level 1: Structural
- Status: PASS / FAIL
- Gates: [pass/fail for each]

### Level 2: Philosophical
- Thin bundle pattern: X.X/1.0
- Context sink discipline: X.X/1.0
- Agent description quality: X.X/1.0
- Composition hygiene: X.X/1.0
- **Overall: X.XX** (threshold: 0.85)

### Level 3: Functional
- **Score: X.XX** (threshold: 0.80)
- [domain-specific assessment details]

### Convergence
- **Status: CONVERGED / NOT CONVERGED**
- Previous best: X.XX → Current: X.XX
- [if not converged: what needs to improve]
```
```

- [ ] **Step 28.2** — Validate YAML frontmatter.

- [ ] **Step 28.3** — Commit:

```bash
git add agents/bundle-evaluator.md
git commit -m "feat: add agents/bundle-evaluator.md — three-level convergence"
```

---

### Task 29: agents/bundle-packager.md — version stamp and deliver

**What:** The terminal agent. Git init, version stamping, first commit, delivery. For improve path: feature branch + PR or merge.

- [ ] **Step 29.1** — Create `~/dev/amplifier-bundle-bundlewizard/agents/bundle-packager.md`:

```markdown
---
meta:
  name: bundle-packager
  description: |
    Use when the bundle has passed verification and is ready for delivery.
    The terminal agent in the factory pipeline.

    Handles: version stamping (convergence metadata in frontmatter),
    git init + first commit (create path), feature branch + PR/merge (improve path),
    README generation, delivery option presentation.

    Produces: packaged, versioned, committed bundle ready for use.

    <example>
    Context: Verification passed, ready to deliver
    user: "[finish mode] Package and deliver the bundle"
    assistant: "Delegating to bundlewizard:bundle-packager to version stamp and deliver."
    <commentary>
    The packager is always the last agent in the pipeline. It handles git and delivery.
    </commentary>
    </example>

  model_role: [fast]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Bundle Packager

You package bundles for delivery. This is the last step — make it clean and traceable.

## Version Stamp

Add convergence metadata to the generated bundle's `bundle.md` frontmatter:

```yaml
bundle:
  name: <bundle-name>
  version: 0.1.0
  description: |
    <description>
  generated_by:
    tool: bundlewizard
    version: 0.1.0
    timestamp: <ISO 8601>
    convergence:
      iterations: <N>
      level_1: PASS
      level_2: <score>
      level_3: <score>
```

This is NON-NEGOTIABLE. Every machine-generated bundle must be traceable.

## Delivery by Path

### Create New Path

1. Ensure the output directory is a git repo (`git init` if not)
2. Stage all files: `git add .`
3. First commit: `git commit -m "feat: initial bundle generation by bundlewizard"`
4. Offer GitHub repo creation: `gh repo create <org>/<name> --private --source=. --push`
5. Present delivery options to the user

### Improve Existing Path

1. Create a feature branch: `git checkout -b bundlewizard/improvements`
2. Stage changes: `git add .`
3. Commit: `git commit -m "feat: bundle improvements by bundlewizard"`
4. Offer delivery options:
   - **merge**: `git checkout main && git merge bundlewizard/improvements`
   - **pr**: `gh pr create --title "Bundlewizard improvements" --body "<summary>"`
   - **keep**: leave on branch for manual review
   - **discard**: `git checkout main && git branch -D bundlewizard/improvements`

## Dangerously-Skip-Permissions Path

In autonomous mode, add extra metadata:

```yaml
  generated_by:
    tool: bundlewizard
    mode: dangerously-skip-permissions
    triggered_by: <session_id>
    trigger_reason: <capability gap description>
```

Auto-select "keep" delivery — the calling session will hot-compose.

## Output

```markdown
## Delivery Summary

- **Bundle:** [name]
- **Version:** 0.1.0
- **Convergence:** Level 1 PASS, Level 2 X.XX, Level 3 X.XX (N iterations)
- **Delivery:** [merge/pr/keep/discard]
- **Location:** [path or repo URL]
```
```

- [ ] **Step 29.2** — Validate YAML frontmatter.

- [ ] **Step 29.3** — Commit:

```bash
git add agents/bundle-packager.md
git commit -m "feat: add agents/bundle-packager.md — version stamp and delivery"
```

---

### Task 30: Validate Phase 2 — agent integrity check

**What:** Cross-check all agents against the behavior registration.

- [ ] **Step 30.1** — Verify agent count: `ls agents/ | wc -l` — should print `10`.

- [ ] **Step 30.2** — Verify names match behavior registration:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
echo "=== Registered in behavior ==="
grep 'bundlewizard:agents/' behaviors/bundlewizard.yaml | sed 's/.*agents\///' | sort
echo ""
echo "=== Files on disk ==="
ls agents/ | sed 's/\.md$//' | sort
echo ""
echo "=== Diff (should be empty) ==="
diff <(grep 'bundlewizard:agents/' behaviors/bundlewizard.yaml | sed 's/.*agents\///' | sort) <(ls agents/ | sed 's/\.md$//' | sort)
```

The diff should be empty — every registered agent has a file, every file is registered.

- [ ] **Step 30.3** — Verify all agents have valid YAML frontmatter:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
python3 -c "
import yaml, glob, sys
errors = []
for f in sorted(glob.glob('agents/*.md')):
    content = open(f).read()
    if not content.startswith('---'):
        errors.append(f'{f}: missing YAML frontmatter')
        continue
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append(f'{f}: malformed frontmatter')
        continue
    try:
        data = yaml.safe_load(parts[1])
        if 'meta' not in data:
            errors.append(f'{f}: missing meta key')
        elif 'name' not in data['meta']:
            errors.append(f'{f}: missing meta.name')
        elif 'description' not in data['meta']:
            errors.append(f'{f}: missing meta.description')
    except Exception as e:
        errors.append(f'{f}: {e}')
if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print(f'All {len(glob.glob(\"agents/*.md\"))} agents valid.')
"
```

- [ ] **Step 30.4** — Verify @mentions reference existing context files:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
# Find all @bundlewizard:context/ references in agent files
grep -h '@bundlewizard:context/' agents/*.md | sed 's/.*@bundlewizard:context\///' | sed 's/\.md.*/\.md/' | sort -u
echo "---"
# List actual context files
ls context/ | sort
# Every referenced file should exist in the context/ directory
```

- [ ] **Step 30.5** — Verify every agent has `<example>` blocks:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
for f in agents/*.md; do
  count=$(grep -c '<example>' "$f")
  name=$(basename "$f" .md)
  echo "$name: $count examples"
  if [ "$count" -lt 2 ]; then
    echo "  WARNING: fewer than 2 examples"
  fi
done
```

- [ ] **Step 30.6** — Final Phase 2 commit and push:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
git status  # Should show nothing to commit
git push
```

---

## Phase 3: Recipes, Skills, and Docs

> The recipe YAML that automates the pipeline, the loadable skill references, and the user-facing documentation. This phase wires the agents from Phase 2 into executable workflows.

**Recipe anatomy (quick primer for newcomers):**
- **Staged recipes** have `stages:` with approval gates between them. The human reviews and approves before the next stage runs. Think of it like a deployment pipeline with manual checkpoints.
- **While-loop recipes** repeat a sub-recipe until a condition is met (like a `while` loop in code). Used for convergence loops where you iterate until quality is good enough.
- **Flat recipes** have `steps:` that run sequentially. No stages, no loops, just step-by-step.
- **Foreach recipes** iterate over a list of items, running a sub-recipe for each one. Like a `for` loop in code.
- **Sub-recipes** are invoked by other recipes via `type: recipe`. They're not meant to be run directly.

**Skill anatomy:**
- A markdown file at `skills/<skill-name>/SKILL.md`
- YAML frontmatter with `name:` and `description:`
- Markdown body with reference tables, patterns, and guidance
- Loaded on-demand via `load_skill` tool — NOT loaded into every session

---

### Task 31: recipes/bundle-development-cycle.yaml — full staged pipeline

**What:** The main recipe. Automates the entire pipeline with approval gates so the human can review at critical points. This is the recipe-track equivalent of manually walking through `/bundle-explore` → `/bundle-spec` → `/bundle-plan` → `/bundle-execute` → `/bundle-verify` → `/bundle-finish`.

**Pattern:** Follows `harness-development-cycle.yaml` exactly — staged recipe with approval gates between stages.

- [ ] **Step 31.1** — Create `~/dev/amplifier-bundle-bundlewizard/recipes/bundle-development-cycle.yaml`:

```yaml
# Bundle Development Cycle
# Full interactive cycle with 3 approval gates: explore → spec → plan → execute → verify → finish.
#
# Pattern: staged recipe with human checkpoints (same pattern as harness-development-cycle).
# Each stage has a defined job; approval gates let the human validate at critical junctures.
#
# Stages:
#   1. exploration  — bundle-explorer + bundle-spec-writer           → APPROVAL GATE
#   2. planning     — bundle-plan-writer                             → APPROVAL GATE
#   3. execution    — invokes bundle-refinement-loop sub-recipe      (no gate — let it run)
#   4. verification — bundle-evaluator independent assessment        → APPROVAL GATE
#   5. completion   — bundle-packager delivers the artifact
#
# Context variables:
#   bundle_description — What the user wants (e.g., "a bundle that helps with code review")
#   output_dir         — Where to put generated artifacts (e.g., "~/dev/my-new-bundle")
#   path               — "create" for new bundles, or a filesystem path/URL for improve mode
#
# Usage:
#   amplifier run "execute bundlewizard:recipes/bundle-development-cycle.yaml
#     with bundle_description='a bundle that helps with code review'
#     output_dir='~/dev/amplifier-bundle-code-review'
#     path='create'"

name: "bundle-development-cycle"
description: "Full interactive bundle development cycle with 3 approval gates — explore, spec, plan, execute, verify, finish"
version: "1.0.0"
author: "Bundlewizard Bundle"
tags: ["bundle", "development-cycle", "staged", "approval-gate", "interactive", "full-cycle"]

context:
  bundle_description: ""   # Required: What to build (e.g., "a bundle that helps with code review")
  output_dir: "output"     # Where to put generated artifacts
  path: "create"           # "create" for new bundles, or a path/URL for improve mode

stages:
  # ============================================================================
  # STAGE 1: Exploration
  # Understand what the user needs and produce a bundle specification.
  # Two steps: explorer interviews → spec-writer documents the design.
  # APPROVAL GATE: human reviews the spec before we invest in planning.
  # ============================================================================
  - name: "exploration"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Explore and interview
      # -----------------------------------------------------------------------
      - id: "explore-needs"
        agent: "bundlewizard:bundle-explorer"
        prompt: |
          Explore the user's needs and produce an interview summary.

          BUNDLE DESCRIPTION: {{bundle_description}}
          OUTPUT DIR: {{output_dir}}
          PATH MODE: {{path}}

          {{#if path == 'create'}}
          This is a CREATE NEW bundle request. Investigate thoroughly:
          1. What problem does this bundle solve? Who uses it?
          2. Does something similar exist? (delegate to bundlewizard:ecosystem-scout)
          3. What tier? Behavior / Bundle / Application Bundle
          4. What capabilities does it need? (agents, tools, modes, recipes, context)
          5. What should it delegate to existing experts vs carry itself?
          {{else}}
          This is an IMPROVE EXISTING bundle request. The bundle is at: {{path}}
          1. Read the existing bundle (bundle.md, behaviors, agents, context)
          2. Delegate to bundlewizard:bundle-auditor for full three-level audit
          3. Present findings: structural issues, philosophical violations, capability gaps
          4. Determine scope: which improvements to make
          {{/if}}

          Return a comprehensive interview summary including:
          - Path decision (create new / improve existing)
          - Target name or path
          - Tier decision (behavior / bundle / application bundle)
          - Problem description and capabilities needed
          - Delegation decisions (what to delegate to existing experts)
          - Ecosystem survey results (if applicable)
          - Audit findings (if improve path)
        output: "interview_summary"
        timeout: 600

      # -----------------------------------------------------------------------
      # Step 2: Write the spec
      # -----------------------------------------------------------------------
      - id: "write-spec"
        agent: "bundlewizard:bundle-spec-writer"
        prompt: |
          Produce a concrete bundle specification from the interview summary.

          BUNDLE DESCRIPTION: {{bundle_description}}
          OUTPUT DIR: {{output_dir}}
          PATH MODE: {{path}}

          INTERVIEW SUMMARY:
          {{interview_summary}}

          Create a bundle specification document at:
          {{output_dir}}/bundle-spec.md

          The specification MUST include:
          - Output tier: behavior | bundle | application-bundle
          - Complete file structure (tree diagram of all files)
          - Component design: agents, behaviors, context files, modes, recipes
          - Delegation map: which existing experts handle which concerns
          - Convergence expectations: Level 1 gates, Level 2 targets, Level 3 criteria
          - For improve path: ordered list of changes from audit findings

          Delegate to foundation:foundation-expert to validate the composition.
          Write the file and return its path.
        output: "spec_path"
        timeout: 600

    # APPROVAL GATE: Human reviews the spec before we invest in planning
    approval:
      required: true
      prompt: |
        ======================================================================
        STAGE 1 COMPLETE — SPEC READY FOR REVIEW
        ======================================================================

        The bundle has been explored and a specification has been written.

        INTERVIEW SUMMARY:
        {{interview_summary}}

        SPEC FILE: {{spec_path}}

        Please review the specification:
        - Is the bundle scope correctly understood?
        - Is the output tier appropriate?
        - Are the components comprehensive and correctly designed?
        - Is the delegation map sensible?
        - Are the convergence expectations measurable?

        APPROVE to proceed to planning.
        DENY to revise the spec (provide feedback and we will iterate).
        ======================================================================
      timeout: 0
      default: "deny"

  # ============================================================================
  # STAGE 2: Planning
  # Plan writer creates an implementation plan based on the approved spec.
  # APPROVAL GATE: human reviews the plan before autonomous generation begins.
  # ============================================================================
  - name: "planning"
    steps:
      # -----------------------------------------------------------------------
      # Step 3: Write the plan
      # -----------------------------------------------------------------------
      - id: "write-plan"
        agent: "bundlewizard:bundle-plan-writer"
        prompt: |
          Create an implementation plan from the approved bundle specification.

          BUNDLE DESCRIPTION: {{bundle_description}}
          OUTPUT DIR: {{output_dir}}
          PATH MODE: {{path}}
          SPEC: {{spec_path}}

          Read the spec file carefully. Produce a concrete implementation plan at:
          {{output_dir}}/bundle-plan.md

          The plan MUST include:
          - File-by-file generation order (create) or ordered renovation tasks (improve)
          - Dependencies between files (what must exist before what)
          - For each file: exact path, what it should contain, validation check
          - Task ordering by dependency graph
          - Estimated number of convergence iterations

          Write the file and return its path.
        output: "plan_path"
        timeout: 600

    # APPROVAL GATE: Human reviews the plan before autonomous generation
    approval:
      required: true
      prompt: |
        ======================================================================
        STAGE 2 COMPLETE — PLAN READY FOR REVIEW
        ======================================================================

        The implementation plan has been written.

        SPEC: {{spec_path}}
        PLAN FILE: {{plan_path}}

        Please review the plan:
        - Does the plan fully address the spec requirements?
        - Is the file generation order correct (dependencies respected)?
        - Are the validation checks sufficient?
        - Any concerns before autonomous generation begins?

        APPROVE to start the refinement loop (this may take several minutes).
        DENY to revise the plan (provide feedback and we will iterate).
        ======================================================================
      timeout: 0
      default: "deny"

  # ============================================================================
  # STAGE 3: Execution
  # Invokes bundle-refinement-loop as a sub-recipe.
  # Iterates generate/critique/refine/evaluate until convergence.
  # No approval gate here — the loop runs autonomously.
  # ============================================================================
  - name: "execution"
    steps:
      # -----------------------------------------------------------------------
      # Step 4: Run the refinement loop
      # -----------------------------------------------------------------------
      - id: "run-refinement-loop"
        type: recipe
        recipe: "bundlewizard:recipes/bundle-refinement-loop.yaml"
        context:
          spec_path: "{{spec_path}}"
          plan_path: "{{plan_path}}"
          output_path: "{{output_dir}}/bundle"
          converged: "false"
          iteration: "0"
        output: "refinement_result"
        timeout: 3600
        on_error: "continue"

  # ============================================================================
  # STAGE 4: Verification
  # bundle-evaluator runs independent three-level assessment.
  # This is independent verification — not the same evaluator from the loop.
  # APPROVAL GATE: human reviews the evidence before packaging.
  # ============================================================================
  - name: "verification"
    steps:
      # -----------------------------------------------------------------------
      # Step 5: Independent three-level evaluation
      # -----------------------------------------------------------------------
      - id: "run-verification"
        agent: "bundlewizard:bundle-evaluator"
        prompt: |
          Run independent verification of the generated bundle using all three convergence levels.

          SPEC: {{spec_path}}
          BUNDLE PATH: {{output_dir}}/bundle
          REFINEMENT RESULT: {{refinement_result}}

          This is INDEPENDENT verification — not the same evaluation from the generation loop.
          Evaluate with fresh eyes against all three levels:

          Level 1 (Structural): All pass/fail gates from convergence-criteria.md.
          - Does bundle.md parse? Do agent references resolve? Are URIs valid?
          - Any duplicate context loading? Mode files discoverable?

          Level 2 (Philosophical): Score each of the 4 criteria.
          - Thin bundle pattern, context sink discipline, agent description quality, composition hygiene.
          - Delegate to foundation:foundation-expert for authoritative checks.

          Level 3 (Functional): Does the bundle achieve its stated purpose?
          - Delegate to the appropriate domain expert for functional assessment.
          - Test the primary use case end-to-end if possible.

          Return a verification report including:
          - Level 1: PASS/FAIL with details for each gate
          - Level 2: scored rubric (threshold: 0.85)
          - Level 3: scored assessment (threshold: 0.80)
          - Overall: CONVERGED or NOT CONVERGED
          - Recommendation: SHIP IT or NEEDS MORE WORK
        output: "verification_report"
        timeout: 900

    # APPROVAL GATE: Human reviews evidence before packaging
    approval:
      required: true
      prompt: |
        ======================================================================
        STAGE 4 COMPLETE — VERIFICATION RESULTS READY
        ======================================================================

        Independent verification has been run on the generated bundle.

        VERIFICATION REPORT:
        {{verification_report}}

        SPEC: {{spec_path}}
        BUNDLE: {{output_dir}}/bundle

        Review the evidence:
        - Does Level 1 (structural) pass all gates?
        - Does Level 2 (philosophical) meet the 0.85 threshold?
        - Does Level 3 (functional) meet the 0.80 threshold?
        - Any remaining issues you are concerned about?

        APPROVE to package and deliver the bundle.
        DENY to return to execution (provide feedback on what to improve).
        ======================================================================
      timeout: 0
      default: "deny"

  # ============================================================================
  # STAGE 5: Completion
  # Package the verified bundle — version stamp, git, deliver.
  # ============================================================================
  - name: "completion"
    steps:
      # -----------------------------------------------------------------------
      # Step 6: Package and deliver
      # -----------------------------------------------------------------------
      - id: "package-bundle"
        agent: "bundlewizard:bundle-packager"
        prompt: |
          Package the verified bundle for delivery.

          BUNDLE PATH: {{output_dir}}/bundle
          OUTPUT DIR: {{output_dir}}
          SPEC: {{spec_path}}
          PATH MODE: {{path}}
          VERIFICATION REPORT: {{verification_report}}

          Packaging steps:
          1. Add version stamp to bundle.md frontmatter (generated_by metadata with convergence scores)
          2. Generate or update README.md with usage instructions

          {{#if path == 'create'}}
          For CREATE NEW path:
          3. Run git init (if not already a git repo)
          4. Stage all files: git add .
          5. First commit: git commit -m "feat: initial bundle generation by bundlewizard"
          6. Offer GitHub repo creation
          {{else}}
          For IMPROVE EXISTING path:
          3. Create feature branch: git checkout -b bundlewizard/improvements
          4. Stage changes: git add .
          5. Commit: git commit -m "feat: bundle improvements by bundlewizard"
          6. Offer merge, PR, keep, or discard
          {{/if}}

          Return a completion summary:
          - Final artifact paths
          - Convergence scores achieved
          - How to use this bundle
          - Delivery option chosen
        output: "completion_summary"
        timeout: 600
```

- [ ] **Step 31.2** — Validate YAML parses: `python3 -c "import yaml; yaml.safe_load(open('recipes/bundle-development-cycle.yaml'))"` — should exit 0.

- [ ] **Step 31.3** — Verify agent references match registered agents:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
grep 'agent:' recipes/bundle-development-cycle.yaml | sed 's/.*agent: "//' | sed 's/".*//' | sort -u
# Expected: bundlewizard:bundle-evaluator, bundlewizard:bundle-explorer,
#           bundlewizard:bundle-packager, bundlewizard:bundle-plan-writer,
#           bundlewizard:bundle-spec-writer
# All should match agents registered in behaviors/bundlewizard.yaml
```

- [ ] **Step 31.4** — Commit:

```bash
git add recipes/bundle-development-cycle.yaml
git commit -m "feat: add recipes/bundle-development-cycle.yaml — full staged pipeline"
```

---

### Task 32: recipes/bundle-refinement-loop.yaml — convergence wrapper

**What:** The while-loop that repeatedly calls `bundle-single-iteration.yaml` until the evaluator says the bundle is good enough (converged) or we hit the max iteration limit. Think of it as a `while (!converged)` loop.

**Pattern:** Follows `harness-refinement-loop.yaml` exactly — while-loop convergence with checkpoint_best.

**Key difference from harness-machine:** Bundles converge faster than constraint code. Harness-machine uses 60 max iterations (constraint code can take 14–60+ passes). Bundlewizard uses 10 max iterations (bundle artifacts typically converge in 2–5 passes because the issues are compositional, not algorithmic).

- [ ] **Step 32.1** — Create `~/dev/amplifier-bundle-bundlewizard/recipes/bundle-refinement-loop.yaml`:

```yaml
# Bundle Refinement Loop
# While-loop convergence wrapper around bundle-single-iteration.yaml.
#
# Implements the generate → critique → refine → evaluate convergence loop
# from the factory pattern (same pattern as harness-refinement-loop).
#
# Loop mechanics:
#   - Iterates bundle-single-iteration.yaml until converged == 'true'
#   - max 10 iterations (bundles converge faster than constraints — typically 2-5 passes)
#   - Saves best-so-far on each iteration (checkpoint_best)
#   - On timeout: returns best achieved (do not fail — 95% is better than nothing)
#
# Why 10 max instead of harness-machine's 60:
#   Bundle artifacts are compositional (YAML, markdown, file structure).
#   Issues are pattern violations and missing content, not algorithmic edge cases.
#   If a bundle hasn't converged in 10 iterations, the spec needs revision, not more iterations.
#
# Usage (via bundle-development-cycle.yaml — not for direct invocation):
#   amplifier run "execute bundlewizard:recipes/bundle-refinement-loop.yaml
#     with spec_path=output/bundle-spec.md plan_path=output/bundle-plan.md
#     output_path=output/bundle"

name: "bundle-refinement-loop"
description: "While-loop convergence wrapper — iterates single-iteration until three-level convergence is met"
version: "1.0.0"
author: "Bundlewizard Bundle"
tags: ["bundle", "convergence", "while-loop", "refinement", "factory-pattern"]

context:
  spec_path: ""      # Required: Path to bundle specification document
  plan_path: ""      # Required: Path to implementation plan document
  output_path: ""    # Required: Where to write generated bundle artifacts
  converged: "false" # Loop control — updated by sub-recipe assessment result
  iteration: "0"     # Current iteration counter — updated each cycle

steps:
  # ---------------------------------------------------------------------------
  # Convergence Loop
  # Repeatedly invokes bundle-single-iteration.yaml until the evaluator signals
  # convergence (all three levels pass) or max iterations is reached.
  #
  # Context updates each cycle from the sub-recipe's assessment JSON output:
  #   converged  ← assessment.converged
  #   iteration  ← assessment.iteration
  # ---------------------------------------------------------------------------
  - id: "refinement-cycle"
    type: recipe
    recipe: "bundlewizard:recipes/bundle-single-iteration.yaml"
    context:
      spec_path: "{{spec_path}}"
      plan_path: "{{plan_path}}"
      output_path: "{{output_path}}"
      iteration: "{{iteration}}"
      previous_critique: "{{critique}}"
    while_condition: "{{converged}} != 'true'"
    max_while_iterations: 10
    break_when: "{{converged}} == 'true'"
    update_context:
      converged: "{{assessment.converged}}"
      iteration: "{{assessment.iteration}}"
    checkpoint_best: true
    timeout: 3600
    on_error: "continue"
    on_timeout: "return_best"
```

- [ ] **Step 32.2** — Validate YAML parses: `python3 -c "import yaml; yaml.safe_load(open('recipes/bundle-refinement-loop.yaml'))"` — should exit 0.

- [ ] **Step 32.3** — Verify sub-recipe reference exists: `test -f recipes/bundle-single-iteration.yaml || echo "WARNING: sub-recipe not yet created (Task 33)"` — warning is expected at this point.

- [ ] **Step 32.4** — Commit:

```bash
git add recipes/bundle-refinement-loop.yaml
git commit -m "feat: add recipes/bundle-refinement-loop.yaml — convergence wrapper"
```

---

### Task 33: recipes/bundle-single-iteration.yaml — one generate/critique/refine/evaluate cycle

**What:** The innermost sub-recipe. One complete iteration of: generate artifacts → critic reviews them → refiner fixes issues → evaluator scores convergence. Called repeatedly by `bundle-refinement-loop.yaml`.

**Pattern:** Follows `harness-single-iteration.yaml` exactly — sequential 4-step pipeline with conditional refine step.

**Key difference from harness-machine:** The harness version generates Python constraint code. This version generates bundle artifacts (YAML, markdown, file structure). The evaluator returns three-level convergence scores instead of a single legal action rate.

- [ ] **Step 33.1** — Create `~/dev/amplifier-bundle-bundlewizard/recipes/bundle-single-iteration.yaml`:

```yaml
# Bundle Single Iteration
# The innermost sub-recipe — one generate/critique/refine/evaluate cycle.
#
# This is called repeatedly by bundle-refinement-loop.yaml until convergence.
# Each iteration runs the four-agent pipeline:
#   generator → critic → refiner (conditional) → evaluator
#
# Refinement decision logic:
#   - Critique says "NEEDS CHANGES" → refiner runs, applies targeted fixes
#   - Critique says "APPROVED"      → refiner is skipped, evaluator runs directly
#
# The evaluator returns a JSON object that the refinement loop reads to decide
# whether to stop (converged == "true") or iterate again.
#
# Usage (via bundle-refinement-loop.yaml — not meant for direct invocation):
#   Not meant to be invoked directly. Invoked as a sub-recipe.

name: "bundle-single-iteration"
description: "One generate/critique/refine/evaluate cycle for bundle convergence"
version: "1.0.0"
author: "Bundlewizard Bundle"
tags: ["bundle", "generation", "critique", "refinement", "evaluation", "convergence"]

context:
  spec_path: ""         # Path to bundle specification document
  plan_path: ""         # Path to implementation plan document
  output_path: ""       # Where to write generated bundle artifacts
  iteration: "1"        # Current iteration number (passed from refinement loop)
  previous_critique: "" # Critique from prior iteration (empty on first pass)

steps:
  # ---------------------------------------------------------------------------
  # Step 1: Generate
  # bundle-generator produces bundle artifacts from spec + plan.
  # On iteration > 1, incorporates the previous critique as refinement guidance.
  # ---------------------------------------------------------------------------
  - id: "generate"
    agent: "bundlewizard:bundle-generator"
    prompt: |
      Generate bundle artifacts for this iteration.

      SPEC: {{spec_path}}
      PLAN: {{plan_path}}
      OUTPUT PATH: {{output_path}}
      ITERATION: {{iteration}}

      {{#if previous_critique}}
      PREVIOUS CRITIQUE (apply these refinements):
      {{previous_critique}}

      This is a refinement iteration. Apply the critic's feedback precisely.
      Fix ONLY the issues identified — no scope creep. Preserve everything
      the critic did not flag.
      {{else}}
      This is the first iteration. Generate all bundle artifacts from the spec and plan.
      Follow these rules strictly:
      - Thin bundle pattern: bundle.md ≤20 lines frontmatter, no @mentions in body
      - Context sink discipline: heavy content in agent @mentions, not root session
      - Agent descriptions: WHY/WHEN/WHAT/HOW with <example> blocks
      - One agent per file, one behavior per concern
      {{/if}}

      Read the spec and plan documents. Produce all required bundle artifacts:
      - bundle.md — thin entry point
      - behaviors/*.yaml — behavior wiring
      - agents/*.md — agent definitions
      - context/*.md — knowledge files
      - modes/*.md — mode definitions (if application bundle)
      - recipes/*.yaml — recipe definitions (if applicable)
      - Any other files from the spec

      Write artifacts to {{output_path}}.
      Return a summary of what was generated and key design decisions.
    output: "generated"
    timeout: 600

  # ---------------------------------------------------------------------------
  # Step 2: Critique
  # bundle-critic independently reviews the generated artifacts against the spec.
  # Spawned with context_depth="none" for fresh perspective — no shared context
  # with the generator.
  # Produces actionable feedback — either APPROVED or NEEDS CHANGES with specifics.
  # ---------------------------------------------------------------------------
  - id: "critique"
    agent: "bundlewizard:bundle-critic"
    prompt: |
      Review the generated bundle artifacts against the specification.

      SPEC: {{spec_path}}
      OUTPUT PATH: {{output_path}}
      ITERATION: {{iteration}}

      GENERATED ARTIFACT SUMMARY:
      {{generated}}

      Read the actual generated files at {{output_path}}.
      Review against all three convergence levels:

      Level 1 (Structural):
      1. Does bundle.md frontmatter parse as valid YAML?
      2. Do all agent references in behavior YAML have corresponding files?
      3. Are all source URIs syntactically valid?
      4. Is any context file loaded BOTH at root level AND @mentioned by agents?
      5. Are mode files in the correct path?

      Level 2 (Philosophical):
      1. Thin bundle pattern — bundle.md ≤20 lines frontmatter? No @mentions in body?
      2. Context sink discipline — root context ≤2 files? Agents @mention only what they need?
      3. Agent description quality — every agent has WHY/WHEN/WHAT/HOW? 2+ examples?
      4. Composition hygiene — no circular includes? Sources pinned? One behavior per concern?

      Level 3 (Functional):
      1. Does the bundle achieve its stated purpose (from the spec)?
      2. Are there broken paths or missing capabilities?

      Delegate to foundation:foundation-expert when uncertain about composition rules.

      End your review with exactly one of:
      - "VERDICT: APPROVED" — bundle meets all convergence criteria
      - "VERDICT: NEEDS CHANGES — [list specific issues by level and file]"
    output: "critique"
    timeout: 600

  # ---------------------------------------------------------------------------
  # Step 3: Refine
  # bundle-refiner applies the critic's feedback.
  # Conditional: only runs if critique contains "NEEDS CHANGES".
  # ---------------------------------------------------------------------------
  - id: "refine"
    condition: "{{critique}} contains 'NEEDS CHANGES'"
    agent: "bundlewizard:bundle-refiner"
    prompt: |
      Apply the critic's feedback to improve the bundle artifacts.

      SPEC: {{spec_path}}
      OUTPUT PATH: {{output_path}}
      ITERATION: {{iteration}}

      CRITIC FEEDBACK:
      {{critique}}

      ORIGINAL GENERATION:
      {{generated}}

      Apply targeted fixes:
      - For Level 1 (structural) issues: fix YAML, add missing files, correct URIs
      - For Level 2 (philosophical) issues: fix pattern violations, improve descriptions
      - For Level 3 (functional) issues: add missing capabilities, fix broken paths

      Fix ONLY the issues identified. Do not change parts that were not critiqued.
      Do not add features. Do not restructure. Do not "improve" unflagged content.
      Write updated artifacts to {{output_path}}.
      Return a summary of all changes made and why.
    output: "refined"
    timeout: 600

  # ---------------------------------------------------------------------------
  # Step 4: Assess
  # bundle-evaluator independently scores all three convergence levels.
  # Returns convergence JSON so the refinement loop can decide whether to stop.
  # ---------------------------------------------------------------------------
  - id: "assess"
    agent: "bundlewizard:bundle-evaluator"
    prompt: |
      Evaluate the bundle and score all three convergence levels.

      SPEC: {{spec_path}}
      OUTPUT PATH: {{output_path}}
      ITERATION: {{iteration}}

      CRITIQUE FROM THIS ITERATION:
      {{critique}}

      {{#if refined}}
      REFINEMENT SUMMARY:
      {{refined}}
      {{/if}}

      Run three-level evaluation against the bundle at {{output_path}}:

      Level 1 (Structural): Check each pass/fail gate.
      - Bundle loads? Agent references resolve? URIs valid?
      - No duplicate context? Mode files discoverable?

      Level 2 (Philosophical): Score each criterion (0.0-1.0).
      - Thin bundle pattern (25%)
      - Context sink discipline (25%)
      - Agent description quality (25%)
      - Composition hygiene (25%)
      - Weighted score must be ≥ 0.85 to pass.

      Level 3 (Functional): Score domain-specific fitness (0.0-1.0).
      - Does the bundle achieve its stated purpose?
      - Score must be ≥ 0.80 to pass.

      Convergence formula:
        converged = (level_1 == PASS) AND (level_2 >= 0.85) AND (level_3 >= 0.80)

      Return ONLY a JSON object with this exact structure:
      {
        "converged": "true" or "false",
        "level_1": "PASS" or "FAIL",
        "level_2_score": "X.XX",
        "level_3_score": "X.XX",
        "iteration": "N",
        "best_so_far": "path/to/output"
      }

      Set converged="true" ONLY if all three levels pass their thresholds.
      Set best_so_far to the output_path if this is the best result so far.
    output: "assessment"
    parse_json: true
    timeout: 600
```

- [ ] **Step 33.2** — Validate YAML parses: `python3 -c "import yaml; yaml.safe_load(open('recipes/bundle-single-iteration.yaml'))"` — should exit 0.

- [ ] **Step 33.3** — Verify all agent references match registered agents:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
grep 'agent:' recipes/bundle-single-iteration.yaml | sed 's/.*agent: "//' | sed 's/".*//' | sort -u
# Expected: bundlewizard:bundle-critic, bundlewizard:bundle-evaluator,
#           bundlewizard:bundle-generator, bundlewizard:bundle-refiner
```

- [ ] **Step 33.4** — Commit:

```bash
git add recipes/bundle-single-iteration.yaml
git commit -m "feat: add recipes/bundle-single-iteration.yaml — one iteration cycle"
```

---

### Task 34: recipes/bundle-batch-generation.yaml — foreach over targets

**What:** Generates multiple bundles from a target list. Uses STATE.yaml to track progress. If one bundle fails, the factory continues with the next one. Results are written back to STATE.yaml so you can retry failures later.

**Pattern:** Follows `harness-factory-generation.yaml` exactly — foreach with STATE.yaml tracking.

- [ ] **Step 34.1** — Create `~/dev/amplifier-bundle-bundlewizard/recipes/bundle-batch-generation.yaml`:

```yaml
# Bundle Batch Generation
# Foreach batch recipe — generates bundles for multiple targets from STATE.yaml.
#
# Pattern: factory with foreach over targets (same pattern as harness-factory-generation).
# Individual target failures do not halt the factory (on_error: continue).
# Results (success or failure) are written back to STATE.yaml per target.
#
# Prerequisites:
#   - targets list must be non-empty
#   - output_dir must be writable
#   - STATE.yaml will be created at state_yaml_path if it doesn't exist
#
# Usage:
#   amplifier run "execute bundlewizard:recipes/bundle-batch-generation.yaml
#     with targets=['code-review helper','git worktree manager','terraform module analyzer']
#     state_yaml_path=output/STATE.yaml
#     output_dir=output/bundles"

name: "bundle-batch-generation"
description: "Batch bundle generation — foreach over targets list with STATE.yaml tracking"
version: "1.0.0"
author: "Bundlewizard Bundle"
tags: ["bundle", "factory", "foreach", "batch", "state-yaml", "autonomous"]

context:
  targets: []                             # Required: list of bundle descriptions to generate
  state_yaml_path: "output/STATE.yaml"    # Path to STATE.yaml tracking file
  output_dir: "output/bundles"            # Where to accumulate generated bundles

steps:
  # ---------------------------------------------------------------------------
  # Step 1: Load State
  # Read STATE.yaml to get current generation status.
  # Produces a JSON object with current state for downstream steps.
  # If STATE.yaml doesn't exist yet, creates an empty initial state.
  # ---------------------------------------------------------------------------
  - id: "load-state"
    type: bash
    command: |
      python3 -c "
      import yaml, json, sys

      state_path = '{{state_yaml_path}}'
      try:
          with open(state_path, 'r') as f:
              state = yaml.safe_load(f)
          print(json.dumps(state))
      except FileNotFoundError:
          # Initialize empty state if file doesn't exist yet
          initial = {
              'version': '1.0.0',
              'bundles': {},
              'summary': {
                  'total': 0,
                  'converged': 0,
                  'in_progress': 0,
                  'failed': 0
              }
          }
          print(json.dumps(initial))
      except Exception as e:
          print(json.dumps({'error': str(e)}), file=sys.stderr)
          sys.exit(1)
      "
    output: "state"
    parse_json: true

  # ---------------------------------------------------------------------------
  # Step 2: Generate Per Target
  # Foreach loop over the targets list.
  # Each target gets a full bundle-development-cycle run.
  # Individual failures are isolated — the factory continues.
  # Results collected into all_bundles.
  # ---------------------------------------------------------------------------
  - id: "generate-per-target"
    foreach: "{{targets}}"
    as: "bundle_target"
    type: recipe
    recipe: "bundlewizard:recipes/bundle-development-cycle.yaml"
    context:
      bundle_description: "{{bundle_target}}"
      output_dir: "{{output_dir}}/{{bundle_target}}"
      path: "create"
    on_error: "continue"
    collect: "all_bundles"

  # ---------------------------------------------------------------------------
  # Step 3: Verify Factory
  # bundle-evaluator reviews ALL generated bundles holistically.
  # Checks for consistency, quality patterns, and any systemic issues.
  # ---------------------------------------------------------------------------
  - id: "verify-factory"
    agent: "bundlewizard:bundle-evaluator"
    prompt: |
      Review all generated bundles from the batch factory run.

      OUTPUT DIR: {{output_dir}}
      TARGETS: {{targets}}
      STATE FILE: {{state_yaml_path}}

      GENERATION RESULTS:
      {{all_bundles}}

      Perform holistic factory verification:
      1. For each target that completed: verify bundle artifact structure
      2. Check convergence scores — are all three levels within acceptable range?
      3. Identify any systemic patterns across failed targets
      4. Note any targets that need retry or manual intervention
      5. Assess overall factory health

      Return a factory verification report including:
      - Per-target status (converged, Level 1/2/3 scores, artifact path)
      - Overall success rate (converged / total)
      - Systemic issues (if any)
      - Targets requiring retry
      - Recommendation for next steps
    output: "factory_verification"
    timeout: 900

  # ---------------------------------------------------------------------------
  # Step 4: Update State
  # Write generation results back to STATE.yaml.
  # Each target gets its status, convergence scores, and artifact path recorded.
  # ---------------------------------------------------------------------------
  - id: "update-state"
    type: bash
    command: |
      python3 -c "
      import yaml, json, os, sys
      from datetime import datetime

      state_path = '{{state_yaml_path}}'
      output_dir = '{{output_dir}}'
      targets_raw = '''{{targets}}'''
      all_bundles_raw = '''{{all_bundles}}'''
      verification_raw = '''{{factory_verification}}'''

      # Load existing state (or empty)
      try:
          with open(state_path, 'r') as f:
              state = yaml.safe_load(f) or {}
      except FileNotFoundError:
          state = {}

      # Ensure structure
      if 'bundles' not in state:
          state['bundles'] = {}
      if 'summary' not in state:
          state['summary'] = {'total': 0, 'converged': 0, 'in_progress': 0, 'failed': 0}

      # Parse targets list
      try:
          targets = json.loads(targets_raw)
      except Exception:
          targets = [t.strip().strip('\"') for t in targets_raw.strip('[]').split(',') if t.strip()]

      # Update each target entry
      timestamp = datetime.utcnow().isoformat() + 'Z'
      for target in targets:
          target_key = str(target).replace('/', '-').replace(' ', '-').lower()
          artifact_path = os.path.join(output_dir, target_key)
          has_artifact = os.path.isdir(artifact_path) and os.path.exists(os.path.join(artifact_path, 'bundle', 'bundle.md'))

          if target_key not in state['bundles']:
              state['bundles'][target_key] = {}

          state['bundles'][target_key].update({
              'description': str(target),
              'status': 'converged' if has_artifact else 'failed',
              'artifact_path': artifact_path if has_artifact else None,
              'last_updated': timestamp,
          })

      # Recompute summary
      bundles_state = state['bundles']
      state['summary'] = {
          'total': len(bundles_state),
          'converged': sum(1 for v in bundles_state.values() if v.get('status') == 'converged'),
          'in_progress': sum(1 for v in bundles_state.values() if v.get('status') == 'in_progress'),
          'failed': sum(1 for v in bundles_state.values() if v.get('status') == 'failed'),
          'last_factory_run': timestamp,
      }

      # Write back
      os.makedirs(os.path.dirname(state_path), exist_ok=True)
      with open(state_path, 'w') as f:
          yaml.dump(state, f, default_flow_style=False, sort_keys=False)

      print(json.dumps({'updated': True, 'summary': state['summary']}))
      "
    output: "state_update"
    parse_json: true
```

- [ ] **Step 34.2** — Validate YAML parses: `python3 -c "import yaml; yaml.safe_load(open('recipes/bundle-batch-generation.yaml'))"` — should exit 0.

- [ ] **Step 34.3** — Commit:

```bash
git add recipes/bundle-batch-generation.yaml
git commit -m "feat: add recipes/bundle-batch-generation.yaml — foreach batch factory"
```

---

### Task 35: recipes/bundle-audit.yaml — standalone audit recipe

**What:** A standalone recipe for the "improve existing" path. Runs a full audit on an existing bundle and returns findings + scores. This is useful when you just want to evaluate a bundle without going through the full development cycle.

**Pattern:** Flat recipe — sequential steps, no stages, no loops.

- [ ] **Step 35.1** — Create `~/dev/amplifier-bundle-bundlewizard/recipes/bundle-audit.yaml`:

```yaml
# Bundle Audit
# Standalone audit recipe for evaluating an existing bundle.
#
# Pattern: flat sequential recipe (no stages, no loops).
# Use this when you want to audit and score an existing bundle without
# running the full development cycle. Useful for:
#   - Evaluating a bundle before deciding to improve it
#   - Periodic quality checks on existing bundles
#   - Comparing bundles against convergence criteria
#
# Usage:
#   amplifier run "execute bundlewizard:recipes/bundle-audit.yaml
#     with bundle_path='~/dev/my-existing-bundle'"

name: "bundle-audit"
description: "Standalone audit of an existing bundle — three-level evaluation with structured findings"
version: "1.0.0"
author: "Bundlewizard Bundle"
tags: ["bundle", "audit", "evaluation", "standalone", "improve"]

context:
  bundle_path: ""    # Required: Path to the existing bundle to audit

steps:
  # ---------------------------------------------------------------------------
  # Step 1: Run Full Audit
  # bundle-auditor reads the entire bundle and produces a structured findings
  # report covering structural issues, philosophical violations, and capability
  # gaps. Delegates to foundation-expert and amplifier-expert.
  # ---------------------------------------------------------------------------
  - id: "run-audit"
    agent: "bundlewizard:bundle-auditor"
    prompt: |
      Perform a full audit of the existing bundle.

      BUNDLE PATH: {{bundle_path}}

      Read the entire bundle:
      - bundle.md — entry point, includes, frontmatter
      - behaviors/*.yaml — behavior files, agent registrations, tool mounts
      - agents/*.md — agent definitions, descriptions, tools, @mentions
      - context/*.md — context files, content, references
      - modes/*.md — mode definitions, permissions, transitions
      - recipes/*.yaml — recipe definitions, steps, agent references
      - Any other files (skills, templates, docs)

      Evaluate against all three convergence levels.
      Delegate to foundation:foundation-expert for structural and philosophical review.
      Delegate to amplifier:amplifier-expert for ecosystem positioning.

      Produce a structured findings report with:
      - Level 1 (Structural): pass/fail for each gate
      - Level 2 (Philosophical): scored rubric for each criterion
      - Level 3 (Functional): domain-specific assessment
      - Capability gaps: what's missing
      - Evolution recommendations: what the bundle could become
      - Priority-ordered issue list
    output: "audit_findings"
    timeout: 900

  # ---------------------------------------------------------------------------
  # Step 2: Score Current State
  # bundle-evaluator runs the formal three-level evaluation and returns
  # numerical scores. This gives a precise quality measurement.
  # ---------------------------------------------------------------------------
  - id: "score-bundle"
    agent: "bundlewizard:bundle-evaluator"
    prompt: |
      Score the existing bundle using the three-level convergence criteria.

      BUNDLE PATH: {{bundle_path}}

      AUDIT FINDINGS:
      {{audit_findings}}

      Using the audit findings as input, produce formal three-level scores:

      Level 1 (Structural): PASS or FAIL
      - Check each gate from convergence-criteria.md

      Level 2 (Philosophical): Score 0.0-1.0
      - Thin bundle pattern (25%)
      - Context sink discipline (25%)
      - Agent description quality (25%)
      - Composition hygiene (25%)

      Level 3 (Functional): Score 0.0-1.0
      - Does the bundle achieve its stated purpose?

      Return ONLY a JSON object:
      {
        "level_1": "PASS" or "FAIL",
        "level_2_score": "X.XX",
        "level_3_score": "X.XX",
        "meets_convergence": "true" or "false",
        "top_issues": ["issue 1", "issue 2", "issue 3"]
      }
    output: "scores"
    parse_json: true
    timeout: 600

  # ---------------------------------------------------------------------------
  # Step 3: Return Results
  # Combine findings and scores into a final audit report.
  # This is a summary step — just formats the output for the user.
  # ---------------------------------------------------------------------------
  - id: "format-results"
    type: bash
    command: |
      python3 -c "
      import json

      findings = '''{{audit_findings}}'''
      scores_raw = '''{{scores}}'''

      try:
          scores = json.loads(scores_raw)
      except Exception:
          scores = {'error': 'Could not parse scores'}

      report = {
          'bundle_path': '{{bundle_path}}',
          'scores': scores,
          'findings_summary': findings[:500] + '...' if len(findings) > 500 else findings,
          'full_findings': 'See audit_findings output for complete details'
      }
      print(json.dumps(report, indent=2))
      "
    output: "audit_report"
    parse_json: true
```

- [ ] **Step 35.2** — Validate YAML parses: `python3 -c "import yaml; yaml.safe_load(open('recipes/bundle-audit.yaml'))"` — should exit 0.

- [ ] **Step 35.3** — Commit:

```bash
git add recipes/bundle-audit.yaml
git commit -m "feat: add recipes/bundle-audit.yaml — standalone audit for improve path"
```

---

### Task 36: skills/bundle-reference/SKILL.md — quick reference tables

**What:** The loadable reference skill. Contains pipeline diagram, mode table, agent table, recipe table, output tier table, convergence criteria summary, and anti-rationalization table. Loaded on-demand via `load_skill` — NOT in every session.

**Pattern:** Follows `harness-reference/SKILL.md` exactly — YAML frontmatter with name + description, then markdown tables.

- [ ] **Step 36.1** — Create `~/dev/amplifier-bundle-bundlewizard/skills/bundle-reference/SKILL.md`:

```markdown
---
name: bundle-reference
description: "Complete reference tables for Bundlewizard modes, agents, recipes, output tiers, and anti-patterns"
---

## Reference: The Bundlewizard Pipeline

The full bundle development workflow:

```
/bundle-explore  -->  interview summary + routing decision (create new / improve existing)
       |
/bundle-spec     -->  bundle spec (tier, file structure, components, delegation map)
       |
/bundle-plan     -->  implementation plan (file order or renovation tasks)
       |
/bundle-execute  -->  bundle artifacts (generate/critique/refine per iteration)
       |         ^
       |         | (convergence loop via recipe)
       v         |
/bundle-verify   -->  evidence: Level 1 PASS, Level 2 ≥0.85, Level 3 ≥0.80
       |
/bundle-finish   -->  packaged artifact (behavior, bundle, or application bundle)
```

At any point, if something goes wrong: `/bundle-debug` (systematic diagnosis).

**Two-track UX:**
- **Interactive** — work through modes manually, human judgment at each step
- **Recipe** — use `bundle-development-cycle.yaml` with approval gates at critical junctures

Both tracks produce the same artifact. The recipe just automates mode transitions.

---

## Reference: Modes

| Mode | Shortcut | Purpose | Who Does The Work | Tool Permissions Summary |
|------|----------|---------|-------------------|--------------------------|
| Explore | `/bundle-explore` | Interview the user, route to create or improve path | bundle-explorer agent | read_file: safe, bash: warn, write: BLOCKED |
| Spec | `/bundle-spec` | Design the bundle composition, produce bundle-spec.md | bundle-spec-writer agent | read_file: safe, bash: warn, write: warn |
| Plan | `/bundle-plan` | Break spec into ordered implementation tasks | bundle-plan-writer agent | read_file: safe, bash: warn, write: warn |
| Execute | `/bundle-execute` | Orchestrate generate/critique/refine pipeline | dispatch agents only | read_file: safe, delegate: safe, recipes: safe, write: BLOCKED |
| Verify | `/bundle-verify` | Independent three-level convergence assessment | bundle-evaluator agent | read_file: safe, bash: safe, write: warn |
| Finish | `/bundle-finish` | Version stamp, git, deliver the artifact | bundle-packager agent | read_file: safe, bash: safe, write: safe |
| Debug | `/bundle-debug` | Diagnose issues at any pipeline stage | main agent (you) | read_file: safe, bash: safe, write: BLOCKED |
| Skip Permissions | `/dangerously-skip-permissions` | Autonomous self-evolution — all approval gates bypassed | autonomous | everything: safe/allow |

**Mode transition graph (allowed_transitions):**

| From | Allowed Next Modes |
|------|---------------------|
| bundle-explore | bundle-spec, bundle-debug |
| bundle-spec | bundle-plan, bundle-explore, bundle-debug |
| bundle-plan | bundle-execute, bundle-spec, bundle-debug |
| bundle-execute | bundle-verify, bundle-debug |
| bundle-verify | bundle-finish, bundle-debug, bundle-execute |
| bundle-finish | (none — terminal mode, `allow_clear: true`) |
| bundle-debug | bundle-explore, bundle-spec, bundle-plan, bundle-execute, bundle-verify, bundle-finish |
| dangerously-skip-permissions | all modes, `allow_clear: true` |

---

## Reference: Agents

| Agent | Role | When to Use | Model Role |
|-------|------|-------------|------------|
| `bundlewizard:bundle-explorer` | Interview + routing fork + experience detection | MANDATORY — first agent in every session | reasoning, general |
| `bundlewizard:bundle-auditor` | Full three-level audit of existing bundles | Only in "improve existing" path — dispatched by explorer | critique, general |
| `bundlewizard:ecosystem-scout` | Ecosystem survey, find reusable components | During exploration — dispatched by explorer | research, general |
| `bundlewizard:bundle-spec-writer` | Composition design → bundle-spec.md | After interview — delegate document creation | reasoning, general |
| `bundlewizard:bundle-plan-writer` | Implementation plan from spec | After spec approved — delegate plan creation | reasoning, general |
| `bundlewizard:bundle-generator` | Writes bundle artifacts (YAML, markdown, files) | Every generate step in /bundle-execute — NEVER called directly | coding, general |
| `bundlewizard:bundle-critic` | Adversarial review with context_depth="none" | Every critique step in /bundle-execute | critique, general |
| `bundlewizard:bundle-refiner` | Targeted fixes from critic feedback (no scope creep) | Every refine step (when critique says NEEDS CHANGES) | coding, general |
| `bundlewizard:bundle-evaluator` | Three-level convergence scoring | After every iteration + /bundle-verify | critique, general |
| `bundlewizard:bundle-packager` | Version stamp, git init/branch, deliver | Terminal step in /bundle-finish | fast |

**Fresh agent per task:** Use `context_depth="none"` for generator/critic/refiner. Clean context = focused attention = quality output.

---

## Reference: Recipes

| Recipe | Pattern Type | When to Use |
|--------|-------------|-------------|
| `bundlewizard:recipes/bundle-single-iteration.yaml` | Sub-recipe, sequential 4-step pipeline | Invoked by refinement-loop only — not for direct use |
| `bundlewizard:recipes/bundle-refinement-loop.yaml` | While-loop convergence (max 10 iterations) | When you need the autonomous generate/critique/refine loop |
| `bundlewizard:recipes/bundle-development-cycle.yaml` | Staged recipe, 3 approval gates | Full interactive cycle: explore → spec → plan → execute → verify → finish |
| `bundlewizard:recipes/bundle-batch-generation.yaml` | Foreach batch recipe | Batch generation for multiple bundles using STATE.yaml |
| `bundlewizard:recipes/bundle-audit.yaml` | Flat sequential recipe | Standalone audit of an existing bundle — evaluation only, no generation |

---

## Reference: Output Tiers

| Tier | What It Is | When It's Right | Example |
|------|-----------|----------------|---------|
| **Behavior** | Reusable capability package (YAML + context + maybe agents). Composed via `includes:`. | Adding a capability to an existing bundle | A logging behavior, a mode system, a tool mount |
| **Bundle** | Standalone with bundle.md, behaviors, agents, context. A complete product. | A focused tool/capability that stands alone | A code review bundle, a git helper bundle |
| **Application Bundle** | Full-featured with modes, recipes, skills, possibly modules. | A complete workflow or domain system | harness-machine, superpowers, bundlewizard itself |

Size is emergent from scope, not a design input. Never pad a behavior into a bundle for perceived importance.

---

## Reference: Convergence Criteria Summary

```
converged = (Level 1 == PASS) AND (Level 2 ≥ 0.85) AND (Level 3 ≥ 0.80)
```

| Level | What It Checks | Type | Threshold |
|-------|---------------|------|-----------|
| Level 1: Structural | Bundle loads, agent refs resolve, URIs valid, no duplicate context | pass/fail gates | ALL must PASS |
| Level 2: Philosophical | Thin pattern, context sinks, agent descriptions, composition hygiene | scored rubric (4×25%) | ≥ 0.85 |
| Level 3: Functional | Does it do what the spec says? Domain-expert evaluated. | scored assessment | ≥ 0.80 |

**Loop discipline:**
- Evaluate after every refinement — never batch fixes
- checkpoint_best after every improvement — never lose progress
- Max 10 iterations for bundles (vs 60 for constraint code)
- On timeout: deliver checkpoint_best with a note about what didn't converge

---

## Reference: Anti-Rationalization Table

| Your Excuse | Why It's Wrong | What You MUST Do |
|-------------|----------------|-----------------|
| "I'll just write the bundle.md directly, it's only 14 lines" | The pattern.md double-load bug was exactly 1 line. Generator + critic caught it. You wouldn't have. | Delegate to bundle-generator. Critic reviews it. Every time. |
| "The fix is obvious, skip the critic" | Critic runs with context_depth="none". It sees what you can't because it doesn't share your assumptions. | Always run generate → critique → refine → assess in order. |
| "This is a simple behavior, skip the evaluator" | "Simple" is where bugs hide. Simple artifacts are under-scrutinized by default. | Evaluate after every refinement. checkpoint_best. |
| "I know what the expert would say" | The expert loads authoritative context (foundation docs, ecosystem knowledge). Your guess is based on incomplete session context. | Delegate. The expert has @mentioned docs you don't. |
| "One more quick fix, then we'll evaluate" | Batching fixes before evaluation means you can't attribute score changes to specific fixes. | Evaluate after every refinement. One fix, one evaluation. |
| "The bundle is simple enough to skip the convergence loop" | Every generated bundle goes through the loop. No exceptions. | Use /bundle-execute and the recipe pipeline. |
| "I'll pin the source URIs before release" | You'll forget. Or someone will ship @main to production. | Pin now, or add `# TODO: pin before release` and flag in critique. |

---

## Reference: Key Commands

```bash
# Run full interactive cycle (create new)
amplifier run "execute bundlewizard:recipes/bundle-development-cycle.yaml \
  with bundle_description='a bundle that helps with code review' \
  output_dir='~/dev/amplifier-bundle-code-review' \
  path='create'"

# Run full interactive cycle (improve existing)
amplifier run "execute bundlewizard:recipes/bundle-development-cycle.yaml \
  with bundle_description='improve code review bundle' \
  output_dir='~/dev/amplifier-bundle-code-review' \
  path='~/dev/amplifier-bundle-code-review'"

# Standalone audit of existing bundle
amplifier run "execute bundlewizard:recipes/bundle-audit.yaml \
  with bundle_path='~/dev/my-existing-bundle'"

# Batch factory generation
amplifier run "execute bundlewizard:recipes/bundle-batch-generation.yaml \
  with targets=['code-review helper','git worktree manager'] \
  state_yaml_path=output/STATE.yaml \
  output_dir=output/bundles"

# Check pending approvals (staged recipes)
amplifier run "list pending approvals"

# Approve and resume
amplifier run "approve recipe session <session-id> stage exploration"
amplifier run "resume recipe session <session-id>"
```
```

- [ ] **Step 36.2** — Validate YAML frontmatter: `python3 -c "import yaml; yaml.safe_load(open('skills/bundle-reference/SKILL.md').read().split('---')[1])"` — should exit 0.

- [ ] **Step 36.3** — Commit:

```bash
git add skills/bundle-reference/SKILL.md
git commit -m "feat: add skills/bundle-reference/SKILL.md — modes, agents, recipes reference"
```

---

### Task 37: skills/bundle-design/SKILL.md — composition patterns and common mistakes

**What:** The loadable design skill. Contains the composition patterns, common mistakes, agent description quality framework, tier selection guidance, and expert delegation patterns. More detailed than the reference skill — this is for when you need to actually DESIGN a bundle, not just look up a table.

- [ ] **Step 37.1** — Create `~/dev/amplifier-bundle-bundlewizard/skills/bundle-design/SKILL.md`:

```markdown
---
name: bundle-design
description: "Composition patterns, common mistakes, tier selection guidance, and expert delegation patterns for designing Amplifier bundles"
---

## The Thin Bundle Pattern

The most important pattern in bundle design. `bundle.md` is a router, not a knowledge base.

### Rules

| Rule | What It Means | How to Check |
|------|-------------|--------------|
| ≤20 lines YAML frontmatter | name, version, description, includes. That's it. | Count lines between `---` markers |
| NO `@mentions` in markdown body | Don't pull context files into the root session | Search for `@` in the body section |
| NO redeclaration | If a behavior provides agents, don't list them in bundle.md frontmatter | Cross-reference behavior with bundle.md |
| Markdown body is a menu | Brief description of what's available (modes, agents, recipes) | Human-readable, not machine context |

### Good Example

```yaml
---
bundle:
  name: my-bundle
  version: 0.1.0
  description: |
    Does X for Y users.

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@v1.0.0
  - bundle: my-bundle:behaviors/core
---

# My Bundle

Does X for Y users.

## Modes
| Shortcut | What It Does |
|----------|-------------|
| /my-mode | Does the thing |

## Getting Started
Tell me what you need.
```

### Bad Example

```yaml
---
bundle:
  name: my-bundle
  version: 0.1.0
  description: |
    Does X for Y users. This bundle provides comprehensive capabilities
    for managing Y workflows including A, B, C, D, E features with
    full integration into the Amplifier ecosystem and support for
    multiple deployment targets across cloud and local environments.
    It uses the factory pattern with generate/critique/refine cycles
    and supports both interactive and automated workflows.
  agents:
    - name: my-agent-1
      description: "Does thing 1"
    - name: my-agent-2
      description: "Does thing 2"
    - name: my-agent-3
      description: "Does thing 3"
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
---

# My Bundle

@my-bundle:context/instructions.md
@my-bundle:context/philosophy.md
@my-bundle:context/patterns.md
@my-bundle:context/everything-else.md
```

**What's wrong:** Description is too long. Agents are redeclared (behavior handles this). `@main` not pinned. Four context files @mentioned from bundle.md pollute every session.

---

## Context Sink Discipline

Knowledge flows DOWN to where it's used. Root session gets minimal context. Agents @mention what they need.

### Rules

| Rule | Why | How to Check |
|------|-----|--------------|
| Root context ≤ 2 files | More root context = more wasted tokens in every session | Count files in `behavior.context.include` |
| No root file > 100 lines | Long root files = context bloat | `wc -l context/instructions.md context/philosophy.md` |
| Agents @mention only what they need | Focused context = focused output | Review each agent's @mentions |
| No duplicate loading | If behavior includes it, agents don't @mention it again | Cross-reference behavior context.include with agent @mentions |

### What Goes Where

| Content Type | Where It Lives | Loaded When |
|-------------|---------------|-------------|
| Bundle identity + composition | `bundle.md` frontmatter | Always |
| Tool/hook/agent registration | `behaviors/*.yaml` | Always |
| Routing instructions (≤100 lines) | `context/instructions.md` | Always (via behavior) |
| Core principles (≤100 lines) | `context/philosophy.md` | Always (via behavior) |
| Detailed domain knowledge | `context/*.md` (other files) | On-demand (agent @mention) |
| Agent-specific instructions | `agents/*.md` body | When agent is delegated to |
| Mode permissions | `modes/*.md` frontmatter | When mode is activated |

---

## Agent Description Quality (WHY/WHEN/WHAT/HOW)

Every agent's `meta.description` must answer four questions. The LLM reads this to decide whether to delegate — if the description is vague, delegation will be unreliable.

### The Framework

| Question | What It Answers | Example |
|----------|---------------|---------|
| **WHY** | Why does this agent exist? | "Use when improving an existing bundle" |
| **WHEN** | What triggers delegation? | `<example>` blocks showing trigger → delegation |
| **WHAT** | What does it produce? | "Produces a structured findings report" |
| **HOW** | What's the approach? | "Delegates to foundation-expert for structural review" |

### Bad Description

```yaml
meta:
  name: bundle-auditor
  description: "Handles bundle auditing."
```

**Why it's bad:** The LLM doesn't know WHEN to delegate here, WHAT it gets back, or HOW the audit works. It might delegate for the wrong reasons or not at all.

### Good Description

```yaml
meta:
  name: bundle-auditor
  description: |
    Use when improving an existing bundle — performs a full three-level audit.
    Only used in the "improve existing" path. Dispatched by bundle-explorer.

    Reads the entire bundle (bundle.md, behaviors, agents, context, modes, recipes),
    evaluates it against all three convergence levels, and produces a structured
    findings report. Delegates to foundation:foundation-expert for structural/
    philosophical review and amplifier:amplifier-expert for ecosystem positioning.

    Produces: structured findings report (structural issues, philosophical violations,
    capability gaps, evolution recommendations).

    <example>
    Context: Bundle explorer identified this as an "improve" request
    user: "Audit the bundle at ~/dev/my-code-review-bundle"
    assistant: "I'll delegate to bundlewizard:bundle-auditor to perform a full
    three-level audit of your code review bundle."
    </example>
```

### Minimum Standard

Every agent MUST have:
- At least 3 sentences of description (WHY + WHAT + HOW minimum)
- At least 2 `<example>` blocks showing trigger → delegation with `<commentary>`
- A `model_role` that matches the agent's task (coding for generators, critique for reviewers)

---

## Tier Selection Guidance

Use this decision tree to pick the right output tier:

```
Is this adding a capability to an existing bundle?
├── YES → Behavior
│         (YAML + context + maybe agents, composed via includes:)
│
└── NO → Does it need its own bundle.md?
         ├── NO → Behavior (compose it into something bigger)
         │
         └── YES → Does it need modes, recipes, or skills?
                   ├── NO → Bundle
                   │         (standalone with bundle.md, behaviors, agents, context)
                   │
                   └── YES → Application Bundle
                             (full-featured: modes, recipes, skills, possibly modules)
```

**Signs you picked the wrong tier:**
- You're creating modes for a behavior → upgrade to Bundle or Application Bundle
- Your "bundle" has one agent and no modes → downgrade to Behavior
- Your "application bundle" has no recipes or skills → downgrade to Bundle

---

## Common Mistakes with Corrections

| Mistake | Why It's Wrong | Correction |
|---------|---------------|------------|
| Putting agent descriptions in bundle.md | Wastes root context; changes require editing the wrong file | Declare agents in behavior YAML, descriptions in agent .md files |
| @mentioning context from bundle.md body | Loads heavy docs into every session | Move @mentions to agent bodies |
| Declaring same agent in behavior AND bundle.md | Double registration, confusing | Declare in behavior only |
| Using `@main` in published source URIs | Breaking changes hit consumers silently | Pin to version tags (`@v1.0.0`) |
| Creating a "utils" context file | Unfocused grab-bag; every agent loads it "just in case" | Split by topic: one file per concern |
| Agent without examples in description | LLM can't pattern-match when to delegate | Add 2+ `<example>` blocks with `<commentary>` |
| One mega-behavior that does everything | Not reusable; changes affect all consumers | Split by responsibility: one behavior per concern |
| Circular includes (A includes B includes A) | Loader may detect it but don't rely on that | Design acyclic dependency graph |
| Heavy root context (>100 lines) | Context bloat in every session | Shorten root files; move detail to agent @mentions |
| Mode without clear tool permissions | Users don't know what's allowed; agents may bypass intent | Explicit safe/warn/block for every tool |

---

## Expert Delegation Patterns

Bundlewizard agents own the PROCESS. Experts own the KNOWLEDGE. Never guess what an expert would say.

| When You Need | Delegate To | Example Question |
|--------------|-----------|-----------------|
| Composition rule validation | `foundation:foundation-expert` | "Is this includes: structure valid?" |
| URI format verification | `foundation:foundation-expert` | "Is this source URI syntactically correct?" |
| Ecosystem survey | `amplifier:amplifier-expert` | "Does a code review bundle already exist?" |
| Reusable component discovery | `amplifier:amplifier-expert` | "What behaviors should this compose rather than rebuild?" |
| Domain-specific functional testing | Appropriate domain expert | "Does this code review bundle actually review code well?" |

**The delegation discipline:** If you're unsure about a composition rule, delegate. If you're unsure about what exists in the ecosystem, delegate. If you're unsure about domain fitness, delegate. The only thing you should be sure about is the PROCESS.
```

- [ ] **Step 37.2** — Validate YAML frontmatter: `python3 -c "import yaml; yaml.safe_load(open('skills/bundle-design/SKILL.md').read().split('---')[1])"` — should exit 0.

- [ ] **Step 37.3** — Commit:

```bash
git add skills/bundle-design/SKILL.md
git commit -m "feat: add skills/bundle-design/SKILL.md — composition patterns and guidance"
```

---

### Task 38: docs/BUNDLEWIZARD-GUIDE.md — user-facing guide

**What:** The guide that users read to understand what bundlewizard is and how to use it. Written for someone who has never heard of Amplifier bundles. Covers both tracks (modes and recipes), all commands, all agents, and the FAQ.

- [ ] **Step 38.1** — Create `~/dev/amplifier-bundle-bundlewizard/docs/BUNDLEWIZARD-GUIDE.md`:

```markdown
# Bundlewizard Guide

## What is Bundlewizard?

Bundlewizard is a bundle that builds other bundles. It's a factory — you describe what you want, and bundlewizard designs, generates, reviews, and delivers it.

An **Amplifier bundle** is a package of markdown and YAML files that gives an AI assistant new capabilities. Think of it like a plugin system. Bundlewizard automates the creation and improvement of these plugins.

### What can it do?

1. **Create new bundles** from a description of what you need
2. **Improve existing bundles** by auditing them and fixing issues
3. **Batch-generate** multiple bundles from a target list

### How does it work?

Bundlewizard uses a **factory pipeline**: interview → design → plan → generate → critique → refine → evaluate → deliver. Each step is handled by a specialist agent. The generate/critique/refine/evaluate cycle repeats until quality criteria are met — this is called the **convergence loop**.

---

## Quick Start: Create a New Bundle

### Option A: Interactive (mode-by-mode)

```
You: I want to build a bundle that helps with code review.
```

Bundlewizard detects this is a "create new" request and starts the interview:

1. `/bundle-explore` — Interview: What problem does this solve? What tier? What capabilities?
2. `/bundle-spec` — Design: Produces a bundle-spec.md with the complete composition design
3. `/bundle-plan` — Planning: Breaks the spec into ordered implementation tasks
4. `/bundle-execute` — Generation: Runs the convergence loop (generate → critique → refine → evaluate)
5. `/bundle-verify` — Verification: Independent three-level quality check
6. `/bundle-finish` — Delivery: Version stamp, git init, deliver

You control the pace. Review each step. Move forward when ready.

### Option B: Recipe (automated with checkpoints)

```bash
amplifier run "execute bundlewizard:recipes/bundle-development-cycle.yaml \
  with bundle_description='a bundle that helps with code review' \
  output_dir='~/dev/amplifier-bundle-code-review' \
  path='create'"
```

Same pipeline, but automated. You approve at 3 checkpoints:
1. After the spec is written (is the design right?)
2. After the plan is written (is the task breakdown right?)
3. After verification (does the bundle meet quality criteria?)

Between checkpoints, bundlewizard runs autonomously.

---

## Quick Start: Improve an Existing Bundle

### Option A: Interactive

```
You: Can you review and improve my bundle at ~/dev/my-bundle?
```

Bundlewizard detects the path and runs an audit:

1. `/bundle-explore` — Audit: Reads the whole bundle, runs three-level evaluation, presents findings
2. You choose which improvements to make (all, critical only, add new capabilities)
3. `/bundle-spec` → `/bundle-plan` → `/bundle-execute` → `/bundle-verify` → `/bundle-finish`

### Option B: Recipe

```bash
amplifier run "execute bundlewizard:recipes/bundle-development-cycle.yaml \
  with bundle_description='improve code review bundle' \
  output_dir='~/dev/my-bundle' \
  path='~/dev/my-bundle'"
```

### Option C: Audit only (no changes)

```bash
amplifier run "execute bundlewizard:recipes/bundle-audit.yaml \
  with bundle_path='~/dev/my-bundle'"
```

Returns findings and scores without making any changes.

---

## Two-Track UX: Modes vs Recipes

| Track | How It Works | Best For |
|-------|-------------|----------|
| **Interactive modes** | You navigate manually: `/bundle-explore` → `/bundle-spec` → ... | Hands-on sessions where you want control at each step |
| **Recipe automation** | `bundle-development-cycle.yaml` runs the pipeline with approval gates | End-to-end generation with 3 human checkpoints |

Both tracks use the same agents, same context, same convergence criteria. The only difference is who decides when to advance.

---

## Available Commands

### Mode Shortcuts

| Command | What It Does |
|---------|-------------|
| `/bundle-explore` | Start the interview — understand what to build or improve |
| `/bundle-spec` | Design the bundle composition |
| `/bundle-plan` | Break the spec into implementation tasks |
| `/bundle-execute` | Run the convergence loop (generate → critique → refine → evaluate) |
| `/bundle-verify` | Independent quality verification |
| `/bundle-finish` | Package and deliver |
| `/bundle-debug` | Diagnose issues at any stage |
| `/dangerously-skip-permissions` | Autonomous mode — all approval gates bypassed |

### Recipe Commands

```bash
# Full pipeline (create or improve)
amplifier run "execute bundlewizard:recipes/bundle-development-cycle.yaml \
  with bundle_description='...' output_dir='...' path='create'"

# Standalone audit
amplifier run "execute bundlewizard:recipes/bundle-audit.yaml \
  with bundle_path='...'"

# Batch generation
amplifier run "execute bundlewizard:recipes/bundle-batch-generation.yaml \
  with targets=['...','...'] state_yaml_path='...' output_dir='...'"

# Check pending approvals
amplifier run "list pending approvals"

# Approve a stage
amplifier run "approve recipe session <session-id> stage <stage-name>"
```

---

## Available Agents

| Agent | What It Does | When It Runs |
|-------|-------------|-------------|
| `bundle-explorer` | Interviews you, detects experience level, routes to create/improve | First agent in every session |
| `bundle-auditor` | Deep analysis of existing bundles (improve path only) | During exploration, dispatched by explorer |
| `ecosystem-scout` | Checks if similar bundles exist, finds reusable components | During exploration, dispatched by explorer |
| `bundle-spec-writer` | Designs the bundle composition, produces bundle-spec.md | After interview, in /bundle-spec |
| `bundle-plan-writer` | Creates implementation plan from the spec | After spec approved, in /bundle-plan |
| `bundle-generator` | Writes all bundle artifacts (YAML, markdown, files) | Each iteration in /bundle-execute |
| `bundle-critic` | Adversarial review with fresh eyes (no shared context) | Each iteration in /bundle-execute |
| `bundle-refiner` | Targeted fixes for issues the critic found | Each iteration (when critique says NEEDS CHANGES) |
| `bundle-evaluator` | Three-level convergence scoring | After each iteration + /bundle-verify |
| `bundle-packager` | Version stamp, git, deliver | Terminal step in /bundle-finish |

---

## Available Recipes

| Recipe | What It Does | When to Use |
|--------|-------------|-------------|
| `bundle-development-cycle.yaml` | Full pipeline with 3 approval gates | Create or improve a bundle end-to-end |
| `bundle-refinement-loop.yaml` | Convergence loop (max 10 iterations) | Runs inside the development cycle — not for direct use |
| `bundle-single-iteration.yaml` | One generate/critique/refine/evaluate cycle | Runs inside the refinement loop — not for direct use |
| `bundle-batch-generation.yaml` | Generate multiple bundles from a target list | When you need many bundles at once |
| `bundle-audit.yaml` | Standalone audit with three-level scoring | When you just want to evaluate, not change |

---

## /dangerously-skip-permissions

This mode is for when Amplifier itself needs to build a bundle without human intervention. All approval gates are bypassed — the pipeline runs end-to-end autonomously.

**What stays enforced:**
- The convergence loop (generate → critique → refine → evaluate) — quality is non-negotiable
- Structural validation (Level 1) — a broken bundle is worse than no bundle
- Philosophical validation (Level 2) — pattern violations cause downstream problems
- Version stamping — every machine-generated bundle must be traceable

**What gets skipped:**
- Human approval between stages
- "Does this look right?" checkpoints
- Interview routing questions (context already tells bundlewizard what's needed)
- Experience calibration (Amplifier is always "experienced")

**Audit trail:** Every bundle generated in this mode includes `generated_by.mode: dangerously-skip-permissions` in its frontmatter, plus the session ID and trigger reason.

---

## FAQ

**Q: How long does it take to generate a bundle?**
A: Depends on complexity. A simple behavior (Tier 1) typically converges in 2-3 iterations (a few minutes). A full application bundle (Tier 3) may take 5-8 iterations (10-15 minutes). Batch generation time scales linearly with target count.

**Q: What if the convergence loop gets stuck?**
A: After 10 iterations without convergence, the loop stops and returns the best result achieved so far. Use `/bundle-debug` to diagnose why convergence stalled — usually it means the spec needs revision, not more iterations.

**Q: Can I use bundlewizard to improve bundlewizard?**
A: Yes. Point it at its own bundle and run the improve path. The anti-rationalization rules still apply — it goes through the full convergence loop even on itself.

**Q: What's the difference between the audit recipe and the full development cycle?**
A: The audit recipe (`bundle-audit.yaml`) only evaluates — it reads the bundle, scores it, and reports findings. No changes are made. The development cycle (`bundle-development-cycle.yaml`) with `path` set to an existing bundle does the full improve pipeline: audit → spec → plan → generate → verify → deliver.

**Q: What if I disagree with the critic's findings?**
A: In interactive mode (modes), you have full control — you can override, skip, or redirect at any point. In recipe mode, the DENY option at approval gates lets you provide feedback and iterate. The convergence loop is a quality tool, not a cage.

**Q: Can bundlewizard generate bundles that use Python modules?**
A: Bundlewizard generates the bundle structure (YAML, markdown, file organization). If the bundle needs Python modules, bundlewizard will specify the module requirements in the spec and generate the behavior YAML that mounts them, but the actual Python code would need to be written separately or by a coding agent.
```

- [ ] **Step 38.2** — Commit:

```bash
git add docs/BUNDLEWIZARD-GUIDE.md
git commit -m "feat: add docs/BUNDLEWIZARD-GUIDE.md — user-facing guide"
```

---

### Task 39: docs/FACTORY-PATTERN.md — documenting the pattern for extraction

**What:** Documents the abstract factory pattern so it can be extracted into `amplifier-bundle-factory-core` in the future. Written for someone who wants to build a NEW domain factory (like bundlewizard is for bundles, or harness-machine is for constraints).

- [ ] **Step 39.1** — Create `~/dev/amplifier-bundle-bundlewizard/docs/FACTORY-PATTERN.md`:

```markdown
# The Factory Pattern

## What is the Factory Pattern?

The factory pattern is a reusable pipeline for generating, reviewing, and delivering artifacts through iterative convergence. It's the architecture shared by bundlewizard (generates bundles) and harness-machine (generates constraint code).

The pattern is domain-agnostic. The pipeline stages, agent slots, convergence loop, two-track UX, and anti-rationalization enforcement are the same regardless of what you're generating. The domain-specific parts (what "quality" means, what artifacts look like, what experts know) are plugged in through agent implementations and convergence criteria.

**Current status:** The pattern lives inside bundlewizard as internal structure. It will be extracted into `amplifier-bundle-factory-core` when both bundlewizard and harness-machine are stable and a third consumer appears.

## Abstract Pipeline Stages

Every factory follows this stage sequence. Domain-specific factories fill each stage with their own agents.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EXPLORE   │ →  │    SPEC     │ →  │    PLAN     │
│  (interview)│    │  (design)   │    │  (tasks)    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
   APPROVAL           APPROVAL           APPROVAL
    GATE               GATE               GATE
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────┐
│                    EXECUTE                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │
│  │ GENERATE │→ │ CRITIQUE │→ │  REFINE  │→ │EVAL │ │
│  └──────────┘  └──────────┘  └──────────┘  └──┬──┘ │
│       ▲                                       │     │
│       └───── not converged ───────────────────┘     │
└──────────────────────┬──────────────────────────────┘
                       │ converged
                       ▼
┌─────────────┐    ┌─────────────┐
│   VERIFY    │ →  │   FINISH    │
│ (evidence)  │    │ (deliver)   │
└──────┬──────┘    └─────────────┘
       │
   APPROVAL
    GATE
```

## Abstract Agent Slots

Each factory defines agents that fill these abstract slots:

| Slot | Responsibility | Bundlewizard Agent | Harness-Machine Agent |
|------|---------------|-------------------|----------------------|
| `explorer` | Interview, understand the problem, route | `bundle-explorer` | `environment-analyst` |
| `spec-writer` | Design the solution, produce spec document | `bundle-spec-writer` | `spec-writer` |
| `plan-writer` | Break spec into implementation tasks | `bundle-plan-writer` | `plan-writer` |
| `generator` | Produce artifacts from the plan | `bundle-generator` | `harness-generator` |
| `critic` | Adversarial review (context_depth="none") | `bundle-critic` | `harness-critic` |
| `refiner` | Targeted fixes from critic feedback | `bundle-refiner` | `harness-refiner` |
| `evaluator` | Measure convergence (did we improve?) | `bundle-evaluator` | `harness-evaluator` |
| `packager` | Version stamp, git, deliver | `bundle-packager` | `harness-generator` (dual role) |

Domain-specific factories may add extra agents beyond these core slots (e.g., bundlewizard adds `bundle-auditor` and `ecosystem-scout`; harness-machine adds `environment-analyst`).

## Convergence Loop Protocol

The convergence loop is the core quality mechanism. It's a `while (!converged)` loop over four steps:

```
iteration = 0
best_score = 0
patience_counter = 0

while not converged and iteration < max_iterations:
    iteration += 1

    # 1. Generate (or refine if iteration > 1)
    artifacts = generator.generate(spec, plan, previous_critique)

    # 2. Critique (adversarial, fresh context)
    critique = critic.review(artifacts)  # context_depth="none"

    # 3. Refine (targeted fixes only — no scope creep)
    if critique.needs_changes:
        artifacts = refiner.fix(artifacts, critique)

    # 4. Evaluate (domain-specific scoring)
    score = evaluator.score(artifacts)

    # Checkpoint best
    if score > best_score:
        best_score = score
        checkpoint(artifacts)
        patience_counter = 0
    else:
        patience_counter += 1

    if patience_counter >= patience_limit:
        diagnose("Score stalled for {patience_limit} iterations")

    converged = meets_criteria(score)

# On exit: deliver checkpoint_best (not necessarily last iteration)
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `context_depth="none"` for critic | Fresh eyes catch assumptions the generator shares with the orchestrator |
| Refiner fixes ONLY flagged issues | Scope creep during refinement destroys convergence |
| Evaluate after EVERY refinement | Can't attribute score changes to specific fixes if you batch |
| checkpoint_best, not checkpoint_last | Last iteration might be worse (refinement oscillation) |
| patience_limit | Prevents infinite loops on diminishing returns |
| on_timeout: return_best | 95% quality is better than 0% (pipeline failure) |

### Domain-Specific Convergence Parameters

| Parameter | Bundlewizard | Harness-Machine | Rationale |
|-----------|-------------|----------------|-----------|
| max_iterations | 10 | 60 | Bundles are compositional; constraints are algorithmic |
| patience_limit | 3 | 15 | Bundle issues are usually spec problems, not iteration problems |
| convergence_criteria | 3-level (structural + philosophical + functional) | Legal action rate ≥ target | Different domains, different quality metrics |

## Two-Track UX Infrastructure

Every factory provides two ways to use the pipeline:

| Component | Interactive Track | Recipe Track |
|-----------|------------------|--------------|
| Stage transitions | User types `/mode-name` | Recipe `stages:` with approval gates |
| Approval points | Implicit (user sees output, decides to continue) | Explicit `approval.required: true` |
| Convergence loop | Mode orchestrates agent delegation | `refinement-loop.yaml` sub-recipe |
| Single iteration | Agent delegation from execute mode | `single-iteration.yaml` sub-recipe |

Both tracks use the SAME agents with the SAME context. The only difference is who decides when to advance to the next stage.

## Anti-Rationalization Enforcement

Every factory has an anti-rationalization table. These are GATES, not guidelines.

The universal anti-rationalization rules (domain-independent):

| Temptation | Rule |
|-----------|------|
| "I'll just write it directly" | No. Use the generator. The critic reviews everything. |
| "The fix is obvious, skip the critic" | No. The critic has fresh context you don't. |
| "This is simple, skip the evaluator" | No. Simple artifacts are under-scrutinized. |
| "I know what the expert would say" | No. Delegate. Experts have authoritative context. |
| "One more fix, then evaluate" | No. Evaluate after every refinement. |

Domain factories ADD to this table with domain-specific temptations.

## Version Stamping

Every artifact produced by a factory gets metadata:

```yaml
generated_by:
  tool: <factory-name>
  version: <factory-version>
  timestamp: <ISO 8601>
  convergence:
    iterations: <N>
    <domain-specific scores>
```

This enables traceability — you can always tell which artifacts were machine-generated and what quality bar they met.

## How to Build a New Domain Factory

If you want to create a factory for a new domain (e.g., generating test suites, API clients, documentation sites):

### Step 1: Define Your Convergence Criteria

What does "done" mean for your domain? Define measurable quality levels.

### Step 2: Fill the Agent Slots

Create domain-specific agents for each abstract slot (explorer, spec-writer, plan-writer, generator, critic, refiner, evaluator, packager).

### Step 3: Create the Recipes

Copy the recipe structure from bundlewizard or harness-machine. Change agent references and prompts. Adjust `max_while_iterations` and convergence parameters.

### Step 4: Create the Modes

One mode per pipeline stage with appropriate tool permissions.

### Step 5: Write the Anti-Rationalization Table

What temptations will agents face in your domain? Document them as gates.

### Step 6: Test the Loop

Run the convergence loop on a simple example. Verify that the critic finds real issues, the refiner fixes them, and the evaluator's scores track improvement.

## Future: amplifier-bundle-factory-core Extraction Plan

When ready, the shared patterns will be extracted into `amplifier-bundle-factory-core`:

**What moves to factory-core:**
- Abstract pipeline stage definitions
- Convergence loop recipe templates
- Two-track UX infrastructure (mode templates + recipe templates)
- Anti-rationalization enforcement patterns
- Version stamping protocol
- STATE.yaml schema for batch generation

**What stays domain-specific:**
- Agent implementations (the actual markdown files)
- Convergence criteria (what "quality" means)
- Context files (domain knowledge)
- Domain-specific modes and their tool permissions

**Extraction trigger:** When a third consumer exists (beyond bundlewizard and harness-machine). Don't extract prematurely — the pattern needs at least two working implementations to know what's truly shared.

**Documented separately at:** `amplifier-bundle-harness-machine/docs/plans/2026-03-16-factory-core-extraction.md`
```

- [ ] **Step 39.2** — Commit:

```bash
git add docs/FACTORY-PATTERN.md
git commit -m "feat: add docs/FACTORY-PATTERN.md — factory pattern for future extraction"
```

---

### Task 40: Validate Phase 3 — structural integrity check

**What:** Cross-check all Phase 3 artifacts before committing the phase.

- [ ] **Step 40.1** — Validate all recipe YAML files parse:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
python3 -c "
import yaml, glob, sys
errors = []
for f in sorted(glob.glob('recipes/*.yaml')):
    try:
        yaml.safe_load(open(f))
        print(f'OK: {f}')
    except Exception as e:
        errors.append(f'{f}: {e}')
        print(f'FAIL: {f}: {e}')
if errors:
    sys.exit(1)
else:
    print(f'\nAll {len(glob.glob(\"recipes/*.yaml\"))} recipe files valid.')
"
# Expected: 5 recipe files, all OK
```

- [ ] **Step 40.2** — Verify recipe agent references match registered agents:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
echo "=== Agent references in recipes ==="
grep -h 'agent:' recipes/*.yaml | sed 's/.*agent: "//' | sed 's/".*//' | sort -u
echo ""
echo "=== Agents registered in behavior ==="
grep 'bundlewizard:agents/' behaviors/bundlewizard.yaml | sed 's/.*agents\///' | sed 's/^/bundlewizard:/' | sort
echo ""
echo "Every agent reference in recipes should exist in the behavior registration."
```

- [ ] **Step 40.3** — Verify skill YAML frontmatter:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
python3 -c "
import yaml, sys
skills = ['skills/bundle-reference/SKILL.md', 'skills/bundle-design/SKILL.md']
errors = []
for f in skills:
    try:
        content = open(f).read()
        parts = content.split('---', 2)
        data = yaml.safe_load(parts[1])
        if 'name' not in data:
            errors.append(f'{f}: missing name')
        if 'description' not in data:
            errors.append(f'{f}: missing description')
        print(f'OK: {f} (name={data.get(\"name\")})')
    except Exception as e:
        errors.append(f'{f}: {e}')
if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print(f'\nAll {len(skills)} skill files valid.')
"
```

- [ ] **Step 40.4** — Verify doc files exist:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
ls -la docs/BUNDLEWIZARD-GUIDE.md docs/FACTORY-PATTERN.md
# Both files should exist and have non-zero size
wc -l docs/BUNDLEWIZARD-GUIDE.md docs/FACTORY-PATTERN.md
# BUNDLEWIZARD-GUIDE.md should be ~200+ lines
# FACTORY-PATTERN.md should be ~200+ lines
```

- [ ] **Step 40.5** — Final Phase 3 commit:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
git add recipes/ skills/ docs/
git status
git commit -m "feat: complete Phase 3 — recipes, skills, and docs"
```

---

### Task 41: Final Validation + Push

**What:** Run a full structural check of the entire bundle. Verify everything exists, cross-references resolve, and the bundle is complete. Then push.

- [ ] **Step 41.1** — Full file count:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
echo "=== File count by directory ==="
echo "Root:      $(ls *.md 2>/dev/null | wc -l) files"
echo "Agents:    $(ls agents/*.md 2>/dev/null | wc -l) files"
echo "Behaviors: $(ls behaviors/*.yaml 2>/dev/null | wc -l) files"
echo "Context:   $(ls context/*.md 2>/dev/null | wc -l) files"
echo "Modes:     $(ls modes/*.md 2>/dev/null | wc -l) files"
echo "Recipes:   $(ls recipes/*.yaml 2>/dev/null | wc -l) files"
echo "Skills:    $(find skills -name 'SKILL.md' 2>/dev/null | wc -l) files"
echo "Templates: $(ls templates/* 2>/dev/null | wc -l) files"
echo "Docs:      $(ls docs/*.md 2>/dev/null | wc -l) files"
echo ""
echo "=== Total files ==="
find . -type f -not -path './.git/*' | wc -l
# Expected:
#   Root: 2 (bundle.md, README.md)
#   Agents: 10
#   Behaviors: 1
#   Context: 6
#   Modes: 8
#   Recipes: 5
#   Skills: 2
#   Templates: 3
#   Docs: 2
#   Total: ~39 files (may vary by 1-2 with .gitignore etc.)
```

- [ ] **Step 41.2** — Verify ALL expected files exist:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
missing=0

# Root files
for f in bundle.md README.md; do
  test -f "$f" && echo "OK: $f" || { echo "MISSING: $f"; missing=$((missing+1)); }
done

# Agents (10)
for f in bundle-explorer bundle-auditor ecosystem-scout bundle-spec-writer \
         bundle-plan-writer bundle-generator bundle-critic bundle-refiner \
         bundle-evaluator bundle-packager; do
  test -f "agents/${f}.md" && echo "OK: agents/${f}.md" || { echo "MISSING: agents/${f}.md"; missing=$((missing+1)); }
done

# Behavior
test -f "behaviors/bundlewizard.yaml" && echo "OK: behaviors/bundlewizard.yaml" || { echo "MISSING: behaviors/bundlewizard.yaml"; missing=$((missing+1)); }

# Context (6)
for f in instructions philosophy bundle-patterns convergence-criteria \
         factory-protocol anti-rationalization; do
  test -f "context/${f}.md" && echo "OK: context/${f}.md" || { echo "MISSING: context/${f}.md"; missing=$((missing+1)); }
done

# Modes (8)
for f in bundle-explore bundle-spec bundle-plan bundle-execute bundle-verify \
         bundle-finish bundle-debug dangerously-skip-permissions; do
  test -f "modes/${f}.md" && echo "OK: modes/${f}.md" || { echo "MISSING: modes/${f}.md"; missing=$((missing+1)); }
done

# Recipes (5)
for f in bundle-development-cycle bundle-refinement-loop bundle-single-iteration \
         bundle-batch-generation bundle-audit; do
  test -f "recipes/${f}.yaml" && echo "OK: recipes/${f}.yaml" || { echo "MISSING: recipes/${f}.yaml"; missing=$((missing+1)); }
done

# Skills (2)
test -f "skills/bundle-reference/SKILL.md" && echo "OK: skills/bundle-reference/SKILL.md" || { echo "MISSING: skills/bundle-reference/SKILL.md"; missing=$((missing+1)); }
test -f "skills/bundle-design/SKILL.md" && echo "OK: skills/bundle-design/SKILL.md" || { echo "MISSING: skills/bundle-design/SKILL.md"; missing=$((missing+1)); }

# Templates (3)
for f in STATE.yaml CONTEXT-TRANSFER.md SCRATCH.md; do
  test -f "templates/${f}" && echo "OK: templates/${f}" || { echo "MISSING: templates/${f}"; missing=$((missing+1)); }
done

# Docs (2)
for f in BUNDLEWIZARD-GUIDE FACTORY-PATTERN; do
  test -f "docs/${f}.md" && echo "OK: docs/${f}.md" || { echo "MISSING: docs/${f}.md"; missing=$((missing+1)); }
done

echo ""
if [ "$missing" -eq 0 ]; then
  echo "ALL FILES PRESENT. Bundle is complete."
else
  echo "WARNING: $missing files missing!"
fi
```

- [ ] **Step 41.3** — Run full YAML validation:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
python3 -c "
import yaml, glob, sys
errors = []

# YAML files
for f in sorted(glob.glob('**/*.yaml', recursive=True)):
    try:
        yaml.safe_load(open(f))
    except Exception as e:
        errors.append(f'{f}: {e}')

# Markdown files with frontmatter
for f in sorted(glob.glob('**/*.md', recursive=True)):
    content = open(f).read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                yaml.safe_load(parts[1])
            except Exception as e:
                errors.append(f'{f} (frontmatter): {e}')

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    print(f'\n{len(errors)} errors found.', file=sys.stderr)
    sys.exit(1)
else:
    print('All YAML valid across entire bundle.')
"
```

- [ ] **Step 41.4** — Cross-reference: every agent referenced in recipes exists in behavior registration:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
python3 -c "
import glob, re, sys

# Get registered agents from behavior
with open('behaviors/bundlewizard.yaml') as f:
    content = f.read()
registered = set(re.findall(r'bundlewizard:agents/(\S+)', content))
print(f'Registered agents: {sorted(registered)}')

# Get agent references from recipes
recipe_refs = set()
for f in glob.glob('recipes/*.yaml'):
    with open(f) as fh:
        for line in fh:
            match = re.search(r'agent:\s*\"?bundlewizard:(\S+?)\"?$', line.strip())
            if match:
                recipe_refs.add(match.group(1))
print(f'Recipe references: {sorted(recipe_refs)}')

# Check
missing = recipe_refs - {f'agents/{a}' for a in registered} - {a for a in registered}
# Normalize: recipe refs are like 'bundle-generator', registered are like 'bundle-generator'
recipe_agent_names = set()
for ref in recipe_refs:
    name = ref.replace('agents/', '')
    recipe_agent_names.add(name)
registered_names = set(registered)

missing = recipe_agent_names - registered_names
if missing:
    print(f'ERROR: Recipe references agents not in behavior: {missing}', file=sys.stderr)
    sys.exit(1)
else:
    print('All recipe agent references match behavior registration.')
"
```

- [ ] **Step 41.5** — Git status, add, commit, push:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
git status

# If anything uncommitted:
git add .
git commit -m "feat: complete bundlewizard bundle — all phases (foundation + agents + recipes/skills/docs)"

git push
```

- [ ] **Step 41.6** — Verify push succeeded:

```bash
cd ~/dev/amplifier-bundle-bundlewizard
git log --oneline -5
git remote -v
echo ""
echo "=== Bundle complete! ==="
echo "Repo: $(git remote get-url origin)"
echo "Files: $(find . -type f -not -path './.git/*' | wc -l)"
echo "Agents: $(ls agents/*.md | wc -l)"
echo "Recipes: $(ls recipes/*.yaml | wc -l)"
echo "Skills: $(find skills -name 'SKILL.md' | wc -l)"
echo "Modes: $(ls modes/*.md | wc -l)"
```