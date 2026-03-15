# Decision Architecture: Pico vs Nano vs Micro

The three tiers aren't just about code size — they represent fundamentally different decision-making architectures. Each tier adds a new dimension of agency.

---

## Pico: Single-Loop Reactor

```
User prompt → LLM thinks → proposes tool call → constraint gate → execute or deny → respond
```

**Decision model:** Stimulus-response. One LLM, one turn at a time, no memory between sessions, no ability to break work into subtasks. When denied, it retries with a different approach (up to 3 times) then gives up.

**What it can decide:**
- Which tool to use for this specific request
- How to adapt when a tool call is denied
- When to stop trying (max_retries exhausted)

**What it can't decide:**
- "I should split this into three subtasks" (no delegation)
- "I should switch to review mode" (no modes)
- "Let me save this and come back later" (no sessions)
- "This needs human approval before I proceed" (no gates)
- "Let me look this up online first" (no web tools)

**Analogy:** A skilled craftsperson with one tool belt, working on whatever's in front of them right now. No planning, no delegation, no memory of yesterday.

**When to use pico:**
- Single-purpose tools (file validator, code linter, command checker)
- Embedded in CI/CD pipelines
- Quick prototyping ("can an agent do X safely?")
- Resource-constrained environments

---

## Nano: Multi-Source Reasoner with Memory

```
User prompt → load context files → LLM thinks (streaming) → proposes tool call
    → constraint gate → execute or deny → save to session → respond

Next session: load previous conversation → continue where we left off
```

**Decision model:** Context-aware persistent agent. Same single LLM loop as pico, but with three critical additions: it can stream responses (think out loud), persist sessions (remember across restarts), and load dynamic context (read @mentioned files at runtime). Multi-provider support means it can switch models mid-conversation.

**What it can decide (beyond pico):**
- "I need more context — let me load that file" (dynamic context)
- "I should use Claude for reasoning but switch to GPT for code" (provider switching)
- "I'll save this session and resume tomorrow" (persistence)
- "Let me think through this step by step..." (streaming shows the reasoning)

**What it still can't decide:**
- "I should split this into three parallel subtasks" (no delegation)
- "I'm in research mode, not implementation mode" (no modes)
- "This is a multi-step pipeline, let me run it as a recipe" (no recipes)
- "This is dangerous, let me ask the human first" (no approval gates)

**Analogy:** A researcher with a notebook, multiple reference books, and the ability to pick up where they left off tomorrow. Still working alone, but with memory and multiple information sources.

**When to use nano:**
- Domain-specific assistants (genomics researcher, security auditor, lab protocol assistant)
- Long-running investigations that span multiple sessions
- Tasks requiring multiple LLM providers for different strengths
- Interactive tools where streaming feedback matters

---

## Micro: Orchestrating Multi-Agent System

```
User prompt → detect intent → suggest/switch mode → LLM thinks (streaming)
    → proposes action:
        Option A: tool call → constraint gate → execute or deny
        Option B: delegate to sub-agent → fresh agent runs → returns result
        Option C: run recipe → multi-step pipeline with checkpoints
        Option D: request approval → human confirms → proceed or abort
    → save to session → respond

Mode system: work / review / plan (each with different tool permissions)
Recipe system: step 1 → step 2 → approval gate → step 3 → ...
```

**Decision model:** Orchestrator with delegation. The micro agent doesn't just react — it plans, delegates, manages modes, and requests human judgment for sensitive operations. It can spawn fresh sub-agents for focused work, run multi-step recipes, and switch behavioral modes.

**What it can decide (beyond nano):**
- "This is a three-part problem — let me delegate part 1 to a focused sub-agent while I plan parts 2 and 3" (delegation)
- "I'm in review mode now, not work mode — I should only read, not write" (modes)
- "This is a 5-step deployment pipeline — let me run it as a recipe with human approval at step 3" (recipes + approval)
- "This would modify production config — I need the human to confirm before I proceed" (approval gates)
- "The user said 'review this' — I should suggest switching to review mode" (intent detection)
- "This sub-agent found a security issue — let me spawn another sub-agent to verify independently" (multi-agent verification)

**What it still can't decide (vs full Amplifier):**
- Dynamic module loading at runtime (plugins are discovered at startup, not mid-session)
- Full bundle composition (can't nest bundles within bundles)
- gRPC transport (no remote agent communication)
- Full event bus (simplified hook system, not the full kernel event architecture)

**Analogy:** A team lead with a whiteboard, a plan, a set of specialists they can dispatch, and the judgment to know when to stop and ask the boss. They don't have the full corporate infrastructure, but they can run a small team effectively.

**When to use micro:**
- Complex multi-step workflows (deployment pipelines, research projects)
- Teams that need approval gates for sensitive operations
- Systems that benefit from different operational modes (work vs review vs plan)
- Tasks that require parallel investigation by focused sub-agents

---

## The Decision-Making Spectrum

| Decision Type | Pico | Nano | Micro |
|---|---|---|---|
| "Which tool do I use?" | Yes | Yes | Yes |
| "How do I recover from denial?" | Retry 3x | Retry 3x | Retry 3x + delegate alternative |
| "Do I need more context?" | No — static prompt only | Yes — load files dynamically | Yes — load files + switch providers |
| "Should I remember this?" | No — each session is fresh | Yes — save/resume sessions | Yes — save/resume + session history |
| "Should I break this down?" | No — one tool call at a time | No — still sequential | Yes — delegate + recipes |
| "What mode am I in?" | N/A — always the same | N/A — no modes | Yes — work/review/plan with tool restrictions |
| "Is this dangerous?" | Constraint gate only | Constraint gate only | Constraint gate + approval gate + mode restrictions |
| "Should I ask the human?" | Only on max_retries failure | Only on max_retries failure | Yes — approval gates for sensitive ops |
| "Can I run a multi-step workflow?" | No | No | Yes — recipe engine with checkpoints |
| "Can I spawn a specialist?" | No | No | Yes — fresh sub-agents with clean context |
| "Can I detect user intent?" | No | Basic (suggests modes) | Yes — maps intent to modes, switches automatically |

---

## Size vs Capability

| Metric | Pico | Nano | Micro | Full Amplifier |
|---|---|---|---|---|
| **Lines of code** | 800-1,500 | 2,000-3,500 | 5,000-8,000 | ~28,000+ |
| **% of full stack** | ~5% | ~12% | ~25% | 100% |
| **Capabilities** | ~40% | ~65% | ~80% | 100% |
| **Providers** | 1 (via litellm) | Multiple (switchable) | Multiple + routing | 14 modules |
| **Tools** | Selected subset | Selected + web | All + delegation | 25+ modules |
| **Decision depth** | React | React + remember | Plan + delegate + approve | Full orchestration |

---

## Progression: Reactive → Aware → Orchestrating

```
Pico (Reactive)
  │  + streaming, sessions, context, multi-provider
  ▼
Nano (Aware)
  │  + modes, recipes, delegation, approval, intent detection
  ▼
Micro (Orchestrating)
  │  + module loading, bundle composition, gRPC, full event bus
  ▼
Full Amplifier (Complete)
```

Each tier adds a new dimension of agency, not just more tools. The constraint engine (the safety layer) remains identical across all tiers — what changes is how the agent thinks, plans, and collaborates.

---

## Examples in the Wild

**Pico:** `pico-amplifier-filesystem-sandbox` — constrains a coding agent to one directory. 5 rules, 8 tools, no memory. Runs `pico-amplifier check "rm -rf /"` and gets an instant DENY.

**Nano:** `nano-amplifier-tumor-genome-to-vaccine` — a genomics research assistant. Streams reasoning about protein structures, persists sessions across multi-day investigations, dynamically loads research papers as context, switches between Claude (reasoning) and GPT (analysis).

**Micro:** `micro-amplifier-k8s-platform-engineer` — manages Kubernetes clusters. Modes for deploy/monitor/audit, recipes for deployment pipelines with approval gates before production changes, delegates security scans to focused sub-agents, detects "review this deployment" intent and switches to review mode automatically.
