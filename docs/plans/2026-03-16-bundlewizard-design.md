# amplifier-bundle-bundlewizard Design

## Goal

Create `amplifier-bundle-bundlewizard` — an Amplifier bundle that generates and improves Amplifier bundles through a structured design-first interview process with iterative convergence. It applies the factory pattern proven by harness-machine (generate → critique → refine → evaluate) to the bundle composition domain, with adaptive depth for newcomers and experienced users alike.

## Chosen Approach

Hybrid of Approach A (harness-machine's factory pattern for quality control) and Approach C (shared factory-core architecture for reusability), delivered as a single bundle. The factory-core patterns live inside bundlewizard as internal structure, documented and organized for future extraction into a separate `amplifier-bundle-factory-core` when harness-machine is ready to refactor. Build the second machine first, extract the shared core when both consumers exist.

## Architecture — Single Bundle, Internal Factory Pattern

The design produces one deliverable: `amplifier-bundle-bundlewizard`. The factory pattern (interview pipeline, convergence loop, two-track UX, anti-rationalization, version stamping) lives inside as internal context files, shared recipes, and reusable templates — structured as if they could be extracted later, but shipped as one coherent bundle.

A future refactor plan for harness-machine is documented separately at `docs/plans/2026-03-16-factory-core-extraction.md` in the harness-machine repo. When both machines exist and are working, the shared factory patterns get extracted into `amplifier-bundle-factory-core`. Not before.

Three-deliverable roadmap:

1. **Now:** `amplifier-bundle-bundlewizard` (single bundle with internal factory patterns)
2. **Later:** Extract `amplifier-bundle-factory-core` (shared behavior)
3. **Later:** Refactor `amplifier-bundle-harness-machine` to use factory-core as a domain skin

## Two-Path Routing Fork

The defining design choice is the routing fork that happens early in the interview:

**Path A: Create New Bundle**
Flows through the full factory pipeline: explore → spec → plan → execute (convergence loop) → verify → finish.

**Path B: Improve Existing Bundle**
Starts with a full audit (structural + philosophical + functional), user picks which improvements to pursue, then converges to the same pipeline from spec onward.

The "improve" path is NOT just structural fixes. It's a full audit + evolution — understanding what the bundle does, evaluating whether it does it well, and proposing what it should become. Including new agents, capabilities, or recommending the bundle be split.

## Agents (10 total)

### Factory-core slot agents (8)

| Agent | Slot | Responsibility |
|-------|------|---------------|
| `bundle-explorer` | explorer | Opens the interview. Asks "improve or create new?" Gauges experience passively from how the user answers (vocabulary, specificity, ecosystem awareness). For "create new": surveys ecosystem for similar bundles (delegates to `amplifier:amplifier-expert`). For "improve": reads the existing bundle, dispatches `bundle-auditor`, presents findings. |
| `bundle-spec-writer` | spec-writer | Designs the bundle composition. Output tier (behavior/bundle/application bundle). What modules, agents, context, behaviors it needs. What it should delegate to existing experts vs carry itself. Produces a `bundle-spec.md`. |
| `bundle-plan-writer` | plan-writer | Creates the implementation plan. For "create new": file-by-file generation order. For "improve": ordered renovation tasks. For batch: STATE.yaml + target list. |
| `bundle-generator` | generator | Writes the actual bundle artifacts — bundle.md, behavior YAMLs, agent definitions, context files, mode definitions, recipe skeletons. Never called directly by the user; always dispatched by the execute orchestrator. |
| `bundle-critic` | critic | Adversarial review with `context_depth="none"`. Validates against thin bundle pattern, checks for context duplication, verifies URI syntax, checks agent description quality (WHY/WHEN/WHAT/HOW). Delegates to `foundation:foundation-expert` when it needs authoritative answers about composition rules. |
| `bundle-refiner` | refiner | Targeted fixes based on critic feedback. Modifies only what the critic flagged — no scope creep. |
| `bundle-evaluator` | evaluator | Three-level convergence check: (1) structural — does the bundle load? (2) philosophical — thin pattern, no redeclaration, proper context sinks? (3) functional — do agents respond correctly, does context flow as intended? Delegates to experts for functional evaluation. |
| `bundle-packager` | packager | Git init, README generation, version stamping, first commit. For "improve" path: creates a feature branch, commits changes, offers PR or merge. |

### Bundlewizard-specific agents (2)

| Agent | Responsibility |
|-------|---------------|
| `bundle-auditor` | Deep analysis of an existing bundle. Only used in the "improve" path. Reads everything, produces a structured findings report: structural issues, philosophical violations, missing capabilities, evolution recommendations. Delegates to `foundation:foundation-expert` for structural review and `amplifier:amplifier-expert` for ecosystem positioning. |
| `ecosystem-scout` | Searches the Amplifier ecosystem for similar bundles, reusable behaviors, and existing agents the new bundle should delegate to rather than rebuild. Prevents reinventing wheels. Delegates to `amplifier:amplifier-expert` for ecosystem knowledge. |

## Three-Level Convergence Criteria

### Level 1: Structural (pass/fail gates)

- Bundle loads without errors
- All agent references resolve
- All URI sources are syntactically valid
- No duplicate context loading
- Module source URIs point to real, reachable repos

If any Level 1 gate fails, convergence score is 0. Fix structural issues before evaluating anything else.

### Level 2: Philosophical (scored rubric, 0-1)

| Criterion | What It Checks | Weight |
|-----------|---------------|--------|
| Thin bundle pattern | bundle.md ≤20 lines frontmatter, no redeclaration | 25% |
| Context sink discipline | Heavy docs in agents not root session, no >100 line context at root | 25% |
| Agent description quality | Each agent has WHY/WHEN/WHAT/HOW, LLM-discoverable | 25% |
| Composition hygiene | Behaviors reusable, no circular includes, sources pinned appropriately | 25% |

### Level 3: Functional (domain-specific, scored 0-1)

Evaluates whether the bundle actually does what the user intended. Varies by domain — for a code-review bundle: "Does it review code?" For a mode bundle: "Do modes activate?" The evaluator delegates to the appropriate domain expert for functional assessment.

### Convergence Formula

```
converged = (level_1 == PASS) AND (level_2 >= 0.85) AND (level_3 >= 0.80)
```

Level 2 bar is higher because philosophical violations are objective. Level 3 is slightly lower because functional evaluation involves expert judgment. The loop iterates until all three pass or patience exhausts (checkpoint_best, patience counter, never silently declare done).

## Adaptive-Depth Interview Design

### Experience Detection (passive, never asked directly)

| Signal | Indicates | Calibration |
|--------|----------|-------------|
| Uses "behavior," "context sink," "thin pattern" naturally | Experienced | Accelerate — skip fundamentals, ask about composition decisions |
| Says "I want to build something that does X" without bundle vocabulary | Newcomer | Guide — explain what a bundle is, what tiers exist, ask about the problem |
| References specific existing bundles or modules by name | Experienced | Accelerate — they know the ecosystem, focus on architecture |
| Describes the outcome they want, not the mechanism | Newcomer | Guide — translate their outcome into bundle concepts |

### Create New — interview questions (one at a time, order adapts)

1. What problem does this solve? Who uses it?
2. Does something similar exist already? (delegates to `ecosystem-scout`)
3. What tier feels right? Behavior / bundle / application bundle — with concrete ecosystem examples calibrated to experience
4. What capabilities does it need? (agents, tools, modes, recipes, context)
5. What should it delegate to existing experts vs carry itself?

### Improve Existing — interview flow

1. Point me at the bundle (path or repo URL)
2. `bundle-auditor` runs the full audit
3. Findings presented: X structural issues, Y philosophical violations, Z capability gaps
4. Which improvements to tackle? All? Just critical?
5. Any new capabilities to add while we're in here?

Both paths produce a `bundle-spec.md` that feeds into the plan → execute → verify → finish pipeline.

## Output Tiers (scope-driven, not size-driven)

| Tier | What It Is | When It's Right |
|------|-----------|----------------|
| **Behavior** | Reusable capability package (behavior YAML + context + maybe agents). Composed into other bundles via `includes:`. | Adding a capability to an existing bundle |
| **Bundle** | Standalone bundle with its own bundle.md, behaviors, agents, context. A complete product. | A focused tool or capability that stands alone |
| **Application Bundle** | Full-featured bundle with modes, recipes, skills, possibly its own modules. What harness-machine and superpowers are. | A complete development workflow or domain-specific system |

Size is emergent from scope, not a design input.

## Two-Track UX

| Track | How | Best For |
|-------|-----|----------|
| Interactive modes | `/bundle-explore` → `/bundle-spec` → `/bundle-plan` → `/bundle-execute` → `/bundle-verify` → `/bundle-finish` | Hands-on sessions, control at each step |
| Recipe automation | `bundle-development-cycle.yaml` | End-to-end with approval gates |

Off-ramp: `/bundle-debug` when composition fails, generation doesn't converge, or evaluation breaks.

The "improve existing" path has its own entry: `bundle-audit.yaml` recipe, or `/bundle-explore` which detects the improve path and dispatches the auditor.

## Expert Delegation Pattern

| Bundlewizard Agent | Delegates To | For What |
|-------------------|-------------|----------|
| `bundle-explorer` | `amplifier:amplifier-expert` | "Does something similar already exist?" |
| `ecosystem-scout` | `amplifier:amplifier-expert` | "What bundles, behaviors, modules should this compose rather than rebuild?" |
| `bundle-spec-writer` | `foundation:foundation-expert` | "Is this composition valid? Does this tier make sense?" |
| `bundle-critic` | `foundation:foundation-expert` | "Thin pattern compliance? URIs correct? Agent descriptions adequate?" |
| `bundle-evaluator` | `foundation:foundation-expert` + domain expert | Philosophical checks → foundation-expert. Functional checks → domain expert. |
| `bundle-auditor` | `foundation:foundation-expert` + `amplifier:amplifier-expert` | Structural audit → foundation-expert. Ecosystem positioning → amplifier-expert. |

Key discipline: Bundlewizard agents never guess about composition rules. They delegate to the authoritative expert. Experts are knowledge sinks. Bundlewizard agents are process drivers.

## Anti-Rationalization Table

| Temptation | Rule |
|-----------|------|
| "I'll just write the bundle.md directly, it's only 14 lines" | No. The generator writes it. The critic reviews it. Every time. |
| "The fix is obvious, skip the critic" | No. The critic runs with `context_depth="none"`. It sees what you can't. |
| "This is a simple behavior, skip the evaluator" | No. "Simple" is where the pattern.md double-load bug hid. Evaluate. |
| "I know what the expert would say" | No. Delegate. The expert has @mentioned docs you don't. |
| "One more quick fix, then we'll evaluate" | No. Evaluate after every refinement. Checkpoint_best. |

## Capability Gap Detection — Bundlewizard as an Ecosystem Service

Bundlewizard isn't just invoked manually. It should be invocable by the ecosystem itself when Amplifier detects a capability gap.

### How gaps surface

- User asks for something no agent handles
- An existing bundle is missing a feature
- A delegation fails because no agent matches
- A task repeatedly requires manual workarounds

### How bundlewizard enables this

Bundlewizard exposes itself as a delegatable agent. Any session can call `bundlewizard:bundle-explorer` when it detects a capability gap. The explorer's interview can be seeded with context about what gap was detected, skipping generic questions and jumping to the specific need.

Detection is NOT bundlewizard's job. It's the response to detection. A future root session behavior or AMOS advisory could include: "If no agent can handle this request and it describes a repeatable capability, suggest bundlewizard."

## `/dangerously-skip-permissions` Mode — Self-Evolution

A mode where Amplifier stops asking permission for intermediate steps and builds what it needs autonomously.

### Flow

1. Amplifier is doing normal work
2. Hits a capability gap
3. Invokes bundlewizard autonomously (no human approval gates)
4. Bundlewizard runs all stages without approval checkpoints
5. New capability installed
6. Amplifier returns to original task and continues

### What stays enforced (even in dangerous mode)

| Guardrail | Why It Can't Be Skipped |
|-----------|------------------------|
| Convergence loop (generate → critique → refine → evaluate) | Quality. You skip human approval, not machine quality gates. |
| Structural validation (Level 1) | A bundle that doesn't load is worse than no bundle. |
| Philosophical validation (Level 2) | Thin pattern violations cause downstream problems. |
| Version stamping | Traceability for audit. |

### What gets skipped

| Gate | Why Safe-ish |
|------|-------------|
| Human approval between stages | Machine makes design decisions — that's the point. |
| "Does this look right?" checkpoints | Critic and evaluator replace human judgment. |
| Routing question | Triggering context already tells bundlewizard what's needed. |
| Experience calibration | Amplifier is the user — always "experienced." |

### Return-to-process contract

Bundlewizard returns: what was built, what capability it provides, how to compose it, convergence summary. Calling session hot-composes and continues. User sees notification: "I needed X capability, so I built it. Here's what I created: [summary]. Continuing."

### Audit trail

```yaml
generated_by: bundlewizard (dangerously-skip-permissions)
triggered_by: <session_id>
trigger_reason: <capability gap description>
```

## Repo Structure

```
amplifier-bundle-bundlewizard/
├── bundle.md                          # Thin — includes foundation + bundlewizard behavior
├── behaviors/
│   └── bundlewizard.yaml              # Includes factory patterns, mounts modes + skills,
│                                      #   registers all 10 agents
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
│   ├── factory-protocol.md            # Reusable factory pattern, documented for extraction
│   └── anti-rationalization.md        # Shared discipline tables
├── recipes/
│   ├── bundle-development-cycle.yaml  # Full staged pipeline with approval gates
│   ├── bundle-refinement-loop.yaml    # Convergence loop with patience + checkpoint_best
│   ├── bundle-single-iteration.yaml   # One generate → critique → refine → evaluate
│   ├── bundle-batch-generation.yaml   # Foreach over targets with STATE.yaml
│   └── bundle-audit.yaml             # Standalone audit recipe for "improve existing"
├── skills/
│   ├── bundle-reference/SKILL.md      # Modes, agents, recipes reference
│   └── bundle-design/SKILL.md         # Composition patterns, common mistakes
├── templates/
│   ├── STATE.yaml                     # Factory state tracking
│   ├── CONTEXT-TRANSFER.md            # Session handoff notes
│   └── SCRATCH.md                     # Working memory
└── docs/
    ├── BUNDLEWIZARD-GUIDE.md          # User-facing guide
    └── FACTORY-PATTERN.md             # Documents the pattern for future extraction
```

## Design Constraints Summary

| Constraint | Decision |
|-----------|----------|
| Audience | Adaptive — newcomers guided, experts accelerated |
| Entry routing | "Improve existing" vs "Create new" as first fork |
| Process model | Design-first interview, not scaffolding |
| Domain knowledge | Delegates to foundation-expert + amplifier-expert; bundlewizard owns the process |
| Output tiers | Behavior → Bundle → Application Bundle (scope-driven) |
| Convergence | Structural + philosophical + functional; experts evaluate |
| "Improve" path | Full audit + evolution |
| Composability | Harness-machine could call bundlewizard for Tier 2 packaging |
| Self-evolution | `/dangerously-skip-permissions` enables autonomous capability building |
| Factory extraction | Internal patterns structured for future extraction when harness-machine refactors |

## Open Questions

1. **Factory-core extraction timing** — When does it make sense to extract? After bundlewizard is stable? After harness-machine refactor begins? Documented in harness-machine's `docs/plans/2026-03-16-factory-core-extraction.md`.
2. **Dangerous mode scope limits** — Should there be a ceiling on what `dangerously-skip-permissions` can build? (e.g., only behaviors, not full application bundles?) Or is the convergence loop sufficient guardrail?
3. **Hot-compose mechanism** — The return-to-process contract assumes the calling session can hot-compose a newly built bundle. The actual mechanism for this needs design — is this a kernel capability, a foundation pattern, or something new?

## Related Documents

- `amplifier-bundle-harness-machine/docs/plans/2026-03-16-factory-core-extraction.md` — Future refactor plan for harness-machine
- `foundation:docs/BUNDLE_GUIDE.md` — Authoritative bundle composition guide
- `foundation:docs/URI_FORMATS.md` — Source URI syntax reference
- AutoHarness paper (Lou et al., Google DeepMind, 2026, arXiv:2603.03329) — Research foundation for the convergence loop pattern