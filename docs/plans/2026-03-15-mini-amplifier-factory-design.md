# Mini-Amplifier Factory Design

## Goal

Transform amplifier-bundle-harness-machine from a constraint harness generator into the ultimate mini-amplifier factory. Users describe their mission, the bundle discovers what is available in their Amplifier ecosystem, presents a capability picker, asks the right questions, names the result meaningfully, and generates a self-contained mini-amplifier at 20% the size with 80% of the capabilities of full Amplifier.

The generated output is a purpose-built AI specialist -- not a stripped-down Amplifier missing features, but a complete mini-Amplifier with all selected capabilities present in compact form. Examples: `pico-amplifier-tumor-genome-to-vaccine` (genomics specialist), `pico-amplifier-k8s-security-auditor` (infrastructure specialist), `pico-amplifier-lab-protocol-assistant` (science specialist).

## Background

### What the First Test (pico-amplifier) Revealed

Session `caf9a5eb` generated pico-amplifier: 903 lines of constraint logic, 229 tests, three deployment stubs. The constraints were production-grade after 4 rounds of critic-driven hardening. But:

1. It was a constraint LIBRARY, not a self-contained runtime. Nothing called `is_legal_action`.
2. Round 2 added the runtime scaffold (hooks-harness module, standalone CLI, Docker templates).
3. Even with the runtime, pico-amplifier was only 22% of Amplifier's size with roughly 15% of its capabilities.
4. It was missing: web_fetch, delegate, recipes, LSP, python_check, skills, session persistence, approval gates, modes, streaming, dynamic context.
5. The CLI had problems: name collision with macOS `pico`, generic system prompt, no markdown rendering, broken signal handling.
6. The constraint spec was incomplete. Four rounds of critic found bypasses the spec template should have included from the start.

### The Numbers (Real, Measured)

| Metric | amplifier-core | amplifier-foundation | pico-amplifier v1 | Target: nano v2 |
|---|---|---|---|---|
| Python source | 8,256 lines | 8,425 lines | 1,839 lines | ~2,500-3,500 lines |
| Capabilities | 100% (kernel) | 100% (library) | ~15% | 80%+ |
| Size ratio | 100% | 100% | 22% | 20-25% |
| Providers | 14 available | 5 configured | 1 (litellm) | User-selected via litellm |
| Tools | 25 available | varies by bundle | 8 | User-selected |
| Agents | 16 foundation | varies | 0 | Included mini-agents |
| Modes | via modes bundle | varies | 0 | 2-3 modes minimum |

### The Full Module Ecosystem

The harness-machine must discover and offer from the full Amplifier ecosystem (67 modules, 37 bundles, 30 behaviors, 16 agents):

- 3 orchestrators (loop-basic, loop-streaming, loop-events)
- 14 providers (Anthropic, OpenAI, Gemini, Azure, Ollama, vLLM, GitHub Copilot, Bedrock, Perplexity, and others)
- 25 tools (filesystem, bash, web, search, task/delegate, todo, skills, MCP, memory, and others)
- 3 context managers (simple, persistent, memory-enhanced)
- 22 hooks (logging, redaction, approval, streaming-ui, status-context, and others)
- 37 bundles and 30 behaviors available for composition

The module inventory is not static. The harness-machine discovers what is installed at session time, so it automatically reflects new modules, providers, and community contributions as the ecosystem grows.

## Approach

Three key design shifts from the v1 harness-machine.

### 1. Dynamic Capability Discovery (Not Static Lists)

During `/harness-explore`, the bundle runs `amplifier module list`, `amplifier bundle list --all`, and reads the user's installed modules at session time. The capability picker is always current. As the Amplifier ecosystem grows, the picker automatically reflects what is available.

The discovery agent inventories:

- Installed modules by type: tools, hooks, providers, orchestrators, context managers
- Available bundles with their nested behaviors
- Foundation agents available for delegation
- The user's current bundle configuration (what is already active)

### 2. Size Tiers (Micro, Nano, Pico)

The user selects a compression level during `/harness-spec`. This determines the runtime scaffold, feature depth, and code budget:

| Tier | Lines | Capabilities | What Is Included | Best For |
|---|---|---|---|---|
| **micro** | 5,000-8,000 | 80%+ at ~40% size | Own module loader, multiple providers, session persistence, sub-agent delegation, recipes, modes, streaming, dynamic context. Near-full portable Amplifier. | Complex multi-step workflows, team tools, production systems |
| **nano** | 2,000-3,500 | 80% at ~20% size | All selected tools, constraint engine, agent loop with retry, streaming, basic session persistence, web fetch, dynamic context. The sweet spot. | Purpose-built specialists, domain experts, daily-use tools |
| **pico** | 800-1,500 | 50% at ~10% size | One provider, selected tools only, constraint engine, basic CLI. No sub-agents, no recipes, no modes, no session persistence. Laser focused. | Single-purpose agents, quick prototypes, embedded tools |

The tier cascades into everything: which runtime scaffold to copy, how much infrastructure to include, how many features the generator wires up, and how aggressively the code is compressed.

### 3. Two New Agents (9 Total, Up From 7)

**mission-architect** -- Takes the user's mission description ("cure my dog's cancer with genomics and AlphaFold") and distills it into:

- A meaningful name: `pico-amplifier-tumor-genome-to-vaccine`
- A purpose-built system prompt that knows the domain (genomics pipelines, protein folding, drug targets, mRNA vaccine design)
- A README tailored to the mission
- Context documentation explaining what the agent does and why each constraint and capability was chosen
- Naming convention: `{tier}-amplifier-{mission-slug}`

**capability-advisor** -- Reads the dynamic module inventory and the user's mission, then recommends which tools, providers, and features to include:

- "For a genomics pipeline, you will want web_fetch (to query NCBI/UniProt databases), bash (to run bioinformatics tools like BLAST, samtools), python_check (for data analysis scripts), and the Anthropic provider (for reasoning about protein structures)."
- "For a k8s security auditor, you will want bash (kubectl), web_fetch (vulnerability databases), approval gates (before destructive operations), and session persistence (audit trails)."
- Uses Amplifier expert knowledge to understand what each module does and whether it fits the mission.

The existing 7 agents remain unchanged: environment-analyst, spec-writer, plan-writer, harness-generator, harness-critic, harness-refiner, harness-evaluator.

## Architecture

### The Updated Pipeline (7 Modes, Same Flow, Richer Output)

```
/harness-explore  -->  /harness-spec  -->  /harness-plan  -->  /harness-execute  -->  /harness-verify  -->  /harness-finish
                                                                     ^
                                                              /harness-debug
```

### /harness-explore (Enhanced)

Now does three things:

1. Understands the user's MISSION (not just "what to constrain" but "what do you want to build").
2. Discovers available capabilities (runs module/bundle inventory dynamically).
3. Assesses feasibility (can this mission be served by a mini-amplifier?).

The environment-analyst agent runs `amplifier module list` and `amplifier bundle list --all` to build a live capability inventory. It presents the capability picker as a markdown checkbox interface:

```markdown
## Configure your {tier}-amplifier

### Mission: [user's description]
### Proposed name: {tier}-amplifier-{mission-slug}

### LLM Providers (pick one or more)
- [x] Anthropic Claude (recommended for reasoning)
- [ ] OpenAI GPT
- [ ] Google Gemini
- [ ] Ollama (local/offline)
- [ ] Azure OpenAI
[dynamically populated from installed providers]

### Tools (recommended based on mission)
- [x] read_file / write_file / edit_file / apply_patch
- [x] bash (sandboxed)
- [x] grep / glob (code search)
- [x] web_fetch / web_search (for querying databases)
- [ ] delegate (spawn sub-agents)
- [x] todo (task tracking)
- [ ] LSP (code intelligence)
- [ ] python_check (linting + types)
- [ ] skills (loadable knowledge)
- [ ] MCP (external tool servers)
- [ ] memory (persistent across sessions)
[dynamically populated from installed tools, pre-checked based on mission analysis]

### Agent Features (varies by tier)
- [x] Streaming responses
- [x] Rich markdown CLI output
- [x] Proper signal handling (Ctrl-C / Ctrl-D)
- [ ] Session persistence (resume later)
- [ ] Dynamic context loading
- [ ] Modes (switchable behaviors)
- [ ] Recipes (multi-step workflows)
- [ ] Approval gates (human-in-loop)
- [ ] Sub-agent delegation
[greyed out if tier does not support; pre-checked by tier defaults]

### Deployment
- [x] Standalone CLI
- [x] Amplifier hook module
- [ ] Docker container
```

The capability-advisor agent recommends selections based on the mission. The user adjusts. Then proceeds to `/harness-spec`.

### /harness-spec (Enhanced)

Now includes:

- Size tier selection (micro / nano / pico)
- Mission statement (from mission-architect)
- Selected capabilities (from capability picker)
- Constraint design (same as before but with an expanded bash spec template that includes ALL known attack vectors from the pico-amplifier hardening rounds)
- Acceptance criteria
- Meaningful name (from mission-architect)

### /harness-plan (Same Shape, Tier-Aware)

Plan shape adapts to tier:

- **Pico:** Simple plan. Constraint functions and basic CLI.
- **Nano:** Medium plan. Constraints, runtime, and selected features.
- **Micro:** Complex plan. Constraints, full runtime, module loader, and all features.

### /harness-execute (Enhanced)

The generator now produces a complete mini-amplifier based on the selected tier:

- Constraint engine (generated, same as before)
- Runtime scaffold (copied from tier-specific scaffold, not generated from scratch)
- CLI with rich rendering and proper signal handling (from scaffold)
- System prompt (generated by mission-architect, domain-specific)
- config.yaml (generated, not hardcoded -- includes model, project_root, max_retries, and other settings)
- All selected tools wired into the executor
- All selected features enabled in the runtime

The critic now also checks:

- CLI name collision against reserved Unix names
- System prompt accuracy (does it mention only the tools actually included?)
- Config completeness (no hardcoded values that should be in config)
- Signal handling presence
- Markdown rendering presence

### /harness-verify (Same, But Checks More)

Verifies:

- Constraint correctness (legal action rate)
- CLI works (check subcommand returns correct results)
- Chat mode starts without crashing
- System prompt matches actual capabilities
- Config loads correctly
- All selected tools are functional
- Amplifier hook loads and enforces

### /harness-finish (Enhanced)

Packages based on tier:

- **Always:** constraints.py, config.yaml, system-prompt.md, context.md, README.md, test_constraints.py
- **Always:** behavior.yaml (Amplifier hook)
- **Always:** standalone/ directory with CLI
- **Optional:** docker/ directory
- **Setup:** setup.sh (creates venv, installs dependencies, runs tests)
- **Escape hatch:** every mini-amplifier knows when to say "this needs a full Amplifier session"

### /harness-debug (Same)

Used when /harness-verify fails. Investigates root cause, proposes fix, re-enters /harness-execute.

## Components

### The Amplifier-Aware Escape Hatch

Every generated mini-amplifier includes:

1. A reference to the amplifier-expert context.
2. A recognition pattern in the system prompt: "If this task requires capabilities beyond your tool set (for example, you need sub-agents but do not have delegate, or you need a recipe but do not have the recipe runner), say: 'This task exceeds my capabilities. For a full Amplifier session with [needed capability], run: `amplifier run -B foundation`'"
3. No mini-amplifier pretends to be more than it is.

### Runtime Scaffolds by Tier

Three runtime scaffold directories ship with the harness-machine bundle:

**runtime/pico/ (~800-1,200 lines)**

- cli.py -- chat/check/audit with rich rendering and signal handling
- runtime.py -- single-provider agent loop, constraint gate, retry
- tools.py -- selected tools only, project_root enforcement
- constraints.py -- (copied from generated)

**runtime/nano/ (~2,000-3,000 lines)**

Everything in pico plus:

- streaming.py -- streaming response handler
- session.py -- basic session persistence (save/resume conversation)
- context.py -- dynamic context loading from @mention files
- providers.py -- multi-provider support via litellm config

**runtime/micro/ (~4,000-6,000 lines)**

Everything in nano plus:

- modes.py -- mode system (work/review/plan or custom)
- recipes.py -- mini recipe runner for multi-step workflows
- delegate.py -- sub-agent spawning
- approval.py -- human-in-loop approval gates
- loader.py -- mini module loader for dynamic capability addition

### New Agents

**agents/mission-architect.md**

- Role: Takes user's mission description and creates the mini-amplifier's identity.
- Outputs: meaningful name (`{tier}-amplifier-{mission-slug}`), domain-specific system prompt, tailored README.md, context.md with domain knowledge.
- Model role: creative, reasoning, general.

**agents/capability-advisor.md**

- Role: Reads dynamic module inventory and user's mission. Recommends capability selections.
- Outputs: recommended tools with rationale, recommended provider, recommended tier, pre-checked capability picker with explanations.
- Model role: reasoning, general.

### Fixes Baked Into the Bundle

All gaps from the first pico-amplifier test are fixed in the scaffolds and agent instructions:

| Gap | Fix | Where |
|---|---|---|
| G1: CLI name collision | Reserved name checker in harness-generator. mission-architect validates names. | agents/harness-generator.md, agents/mission-architect.md |
| G2: No venv setup | setup.sh generated by /harness-finish. README includes setup instructions. | runtime/*/setup.sh.template |
| G3: Generic system prompt | mission-architect generates domain-specific system prompt from mission, selected tools, and constraints. | agents/mission-architect.md |
| G4: No markdown rendering | `rich` included by default in all scaffolds. Console and Markdown rendering in CLI. | runtime/*/cli.py |
| G5: Broken signal handling | Battle-tested REPL pattern in all scaffolds: separate input/response phases, Ctrl-C cancels current operation, Ctrl-D exits. | runtime/*/cli.py |
| G6: Incomplete bash spec | Expanded constraint spec template with ALL known attack vectors: substitution, absolute paths, prefix bypass, xargs, redirects, process substitution. | context/constraint-spec-template.md |
| G7: No critic budget | Plan template allocates 4-5 explicit critic/refine rounds. | agents/plan-writer.md |

## Data Flow

### Mission to Mini-Amplifier

```
User describes mission
        |
        v
mission-architect --> name, system prompt, README, context.md
        |
        v
environment-analyst --> dynamic module/bundle inventory
        |
        v
capability-advisor --> recommended tools, provider, tier, pre-checked picker
        |
        v
User reviews/adjusts capability picker
        |
        v
spec-writer --> constraint spec + capability spec + tier selection
        |
        v
plan-writer --> tier-aware implementation plan (4-5 critic rounds budgeted)
        |
        v
harness-generator --> constraints.py + runtime scaffold (from tier template) + config + CLI
        |
        v
harness-critic --> validates constraints, CLI name, system prompt, signal handling, config
        |
        v
harness-refiner --> fixes issues found by critic (repeat 4-5 rounds)
        |
        v
harness-evaluator --> runs tests, verifies CLI, verifies chat mode, verifies all tools
        |
        v
Packaged mini-amplifier: {tier}-amplifier-{mission-slug}/
```

### Dynamic Discovery Flow

```
/harness-explore triggers environment-analyst
        |
        v
amplifier module list --> structured inventory of installed modules by type
amplifier bundle list --all --> inventory of available bundles
        |
        v
Grouped into: providers, tools, orchestrators, context managers, hooks, bundles, behaviors, agents
        |
        v
capability-advisor cross-references inventory with user's mission
        |
        v
Markdown checkbox picker with pre-checked recommendations
        |
        v
User confirms or adjusts selections
```

## Updated Bundle Structure

```
amplifier-bundle-harness-machine/
|-- bundle.md                              # Updated: 9 agents (was 7)
|-- behaviors/harness-machine.yaml         # Updated: registers 2 new agents
|-- agents/
|   |-- environment-analyst.md             # Enhanced: runs dynamic discovery
|   |-- capability-advisor.md              # NEW: recommends capabilities
|   |-- mission-architect.md               # NEW: names + documents the mini-amplifier
|   |-- spec-writer.md                     # Enhanced: includes tier selection
|   |-- plan-writer.md                     # Enhanced: tier-aware plans, 4-5 critic rounds
|   |-- harness-generator.md               # Enhanced: generates complete mini-amplifier
|   |-- harness-critic.md                  # Enhanced: checks CLI name, system prompt, signals
|   |-- harness-refiner.md                 # Same
|   +-- harness-evaluator.md              # Enhanced: verifies CLI + chat mode + all tools
|-- modes/                                 # Same 7 modes, enhanced content
|-- context/
|   |-- instructions.md                    # Updated: tier awareness, dynamic discovery
|   |-- philosophy.md                      # Same
|   |-- pattern.md                         # Updated: three-tier pattern
|   |-- harness-format.md                  # Updated: tier-specific artifact formats
|   |-- constraint-spec-template.md        # NEW: expanded template with all known attack vectors
|   +-- examples/                          # Updated: one example per tier
|       |-- pico-filesystem-sandbox.md
|       |-- nano-tumor-genome-to-vaccine.md
|       |-- micro-k8s-platform-engineer.md
|       +-- enterprise-governance-harness.md
|-- skills/                                # Same 3, enhanced
|-- recipes/                               # Same 4
|-- modules/
|   +-- hooks-harness/                     # Same generic hook module
|-- runtime/
|   |-- pico/                              # Pico scaffold (~1,200 lines)
|   |   |-- cli.py
|   |   |-- runtime.py
|   |   |-- tools.py
|   |   |-- setup.sh.template
|   |   |-- pyproject.toml.template
|   |   |-- Dockerfile.template
|   |   +-- docker-compose.template.yaml
|   |-- nano/                              # Nano scaffold (~3,000 lines)
|   |   |-- cli.py
|   |   |-- runtime.py
|   |   |-- tools.py
|   |   |-- streaming.py
|   |   |-- session.py
|   |   |-- context.py
|   |   |-- providers.py
|   |   |-- setup.sh.template
|   |   |-- pyproject.toml.template
|   |   |-- Dockerfile.template
|   |   +-- docker-compose.template.yaml
|   +-- micro/                             # Micro scaffold (~6,000 lines)
|       |-- cli.py
|       |-- runtime.py
|       |-- tools.py
|       |-- streaming.py
|       |-- session.py
|       |-- context.py
|       |-- providers.py
|       |-- modes.py
|       |-- recipes.py
|       |-- delegate.py
|       |-- approval.py
|       |-- loader.py
|       |-- setup.sh.template
|       |-- pyproject.toml.template
|       |-- Dockerfile.template
|       +-- docker-compose.template.yaml
|-- templates/                             # Same factory templates
+-- tests/                                 # Updated: test all three scaffolds
```

## Error Handling

### Constraint Generation Errors

The critic runs 4-5 rounds against the generated constraints. Known attack vectors are enumerated in the expanded `constraint-spec-template.md`. If the critic finds bypasses, the refiner patches them before moving to verification. If all critic rounds are exhausted and issues remain, `/harness-debug` is entered.

### Dynamic Discovery Failures

If `amplifier module list` or `amplifier bundle list --all` fail (Amplifier not installed, older version without these commands), the environment-analyst falls back to a static capability list representing the known ecosystem baseline. The user is informed that dynamic discovery was unavailable and the picker may not reflect their exact installation.

### Tier Mismatch

If the user selects pico tier but checks capabilities that require nano or micro (for example, session persistence or sub-agent delegation), the capability-advisor flags the conflict and recommends upgrading the tier. The user decides whether to upgrade the tier or drop the conflicting capability.

### CLI Name Collision

The harness-generator checks the proposed CLI name against a list of reserved Unix/macOS commands. If a collision is detected, the mission-architect proposes alternatives. This is a hard blocker -- the generator will not produce a CLI with a colliding name.

### Amplifier Escalation

Every generated mini-amplifier includes a recognition pattern for tasks that exceed its capabilities. Rather than failing silently or producing bad output, it tells the user exactly what capability is missing and how to access it through a full Amplifier session.

## Testing Strategy

### Scaffold Tests (Per Tier)

Each scaffold is tested independently:

- CLI starts without error
- Chat mode initializes and accepts input
- Constraint gate blocks illegal actions
- Signal handling works (Ctrl-C cancels, Ctrl-D exits)
- Streaming works (nano and micro tiers)
- Session persistence works (nano and micro tiers)

The existing 229 constraint tests from pico-amplifier v1 serve as a test fixture for all tiers.

### Integration Tests

- Generate a pico-tier mini-amplifier from scratch, verify it runs
- Generate a nano-tier mini-amplifier, verify streaming and session persistence work
- Dynamic discovery returns correct module inventory
- Capability picker pre-checks appropriate tools for known missions
- mission-architect produces meaningful names from descriptions

### Regression Tests

- All 218 existing scaffold tests continue to pass
- Bundle structure validation (agents, modes, recipes, skills all present and well-formed)

## Open Questions

1. **Micro scaffold module loader.** Should the micro scaffold include its own mini-module-loader, or should it use Amplifier's actual loader via an amplifier-core dependency? Recommendation: own mini-loader for true standalone operation; amplifier-core for the Amplifier-hook stud.

2. **Session persistence format.** Should session persistence in the nano tier use SQLite, JSON files, or YAML (matching Amplifier's state pattern)? Recommendation: JSON. Simplest, no dependency, human-readable.

3. **Domain knowledge depth in mission-architect.** How much domain knowledge should mission-architect inject? Should it do web research to learn about the user's domain, or just use what the LLM already knows? Recommendation: use LLM knowledge for v1, add web_research in v2 for deeper domain context.

4. **Capability picker revisability.** Should the capability picker be a one-time selection during /harness-spec, or should it be revisable during /harness-execute if the generator discovers it needs more tools? Recommendation: revisable. If the critic says "this mission needs web_fetch but it was not selected," allow adding it mid-generation.
