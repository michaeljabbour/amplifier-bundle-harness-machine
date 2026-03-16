# Harness Artifact Format

## Size Tiers

Each mini-amplifier is built to one of three size tiers. The tier determines which runtime scaffold files are included and which features are available.

| Tier | Runtime Scaffold | Features |
|------|-----------------|----------|
| **pico** | Minimal: cli.py, runtime.py, constraints.py, config.yaml, system-prompt.md, behavior.yaml, setup.sh, context.md, pyproject.toml (9 files) | Constraints only. No streaming, no session, no provider config. Basic toolset. |
| **nano** | Standard: pico + tools.py, streaming_config.yaml, session_config.yaml, provider_config.yaml (13 files) | Adds streaming response, session persistence, provider/model switching, full tool executor. |
| **micro** | Full: nano + modes/, recipes/, delegation_config.yaml, approval_config.yaml, dynamic_context.md (18 files) | Adds mode switching, recipe execution, sub-agent delegation, approval gates, dynamic context loading. |

Tiers are cumulative — micro includes everything nano has, nano includes everything pico has.

## Three Artifact Tiers

### Tier 1: Nano-Amplifier (3 studs)

The atomic unit of harness output. Every harness generation produces at minimum a nano-amplifier built from one brick and three studs:

**The Brick** (generated, unique per harness):
```
my-harness/
  constraints.py       # The constraint logic — is_legal_action(), validate_action(), propose_action()
```

**Generated Files** (supporting artifacts):
```
my-harness/
  config.yaml          # Runtime configuration for standalone CLI
  context.md           # Environment description, constraint rationale
  system-prompt.md     # Agent mission and scope rules
  test_constraints.py  # Unit tests verifying each constraint function
```

**Stud 1: Amplifier Hook** — plug into any Amplifier session:
```
my-harness/
  behavior.yaml        # Wires hooks-harness module with git source URL, constraints_path, harness_type, strict config
```

**Stud 2: Standalone CLI** — run without Amplifier:
```
my-harness/
  standalone/
    pyproject.toml                 # Stamped from runtime/pyproject.toml.template
    <package_name>/
      cli.py                       # Entry point: chat, check, audit subcommands
      runtime.py                   # ConstraintGate + AgentLoop
      tools.py                     # ToolExecutor (read_file, write_file, bash, grep, glob)
      constraints.py               # Copy of the brick
      config.yaml                  # Copy of runtime config
      system-prompt.md             # Copy of system prompt
```

**Stud 3: Docker Container** (optional) — containerized deployment:
```
my-harness/
  docker/
    Dockerfile                     # Stamped from runtime/Dockerfile.template
    docker-compose.yaml            # Stamped from runtime/docker-compose.template.yaml
```

**Three usage modes:**
1. **Amplifier hook** — compose `behavior.yaml` via `includes:` in any bundle.md
2. **Standalone CLI** — `pip install -e standalone/` then `<harness_name> chat`
3. **Docker container** — `docker compose -f docker/docker-compose.yaml up`

Any Amplifier bundle can compose a nano-amplifier via `includes:` in its bundle.md.

### Tier 2: Harness Bundle (full bundle)

For library-scale (composable skills) or enterprise-scale (governance layers):

```
my-harness-bundle/
  bundle.md
  behaviors/
    domain-constraints.yaml
  modules/
    hook-constraints/
      constraints.py
  context/
    domain-knowledge.md
```

Composed of multiple nano-amplifiers assembled into a single bundle.

### Tier 3: Harness Machine (.harness-machine/ directory)

For factory-scale autonomous generation:

```
.harness-machine/
  STATE.yaml              # Tracks environments, candidates, legal action rates
  CONTEXT-TRANSFER.md     # Session handoff notes
  SCRATCH.md              # Ephemeral working memory
  build.yaml              # Outer loop recipe
  iteration.yaml          # Inner loop: one iteration per session
  harnesses/              # Generated nano-amplifiers accumulate here
```

Zero runtime dependency on the harness-machine bundle. Self-contained.

## Harness Type Enum

| Type | Mechanism | Use When | Core Functions |
|------|-----------|----------|----------------|
| `action-filter` | Harness proposes legal moves, LLM ranks | Action space is enumerable | `propose_action()` |
| `action-verifier` | LLM proposes, harness validates, retry if illegal | Action space is too large to enumerate | `is_legal_action()` |
| `code-as-policy` | Pure code chooses action, no LLM at inference | Deterministic optimal policy exists | `propose_action()` (no LLM) |

## Harness Scale Enum

| Scale | Scope | Artifact Tier | Typical Iterations |
|-------|-------|--------------|-------------------|
| `nano` | Single constraint, one environment | Tier 1 | 1-5 |
| `single` | Multiple constraints, one environment | Tier 1 | 5-30 |
| `library` | Composable skills across a domain | Tier 2 | 10-50 per skill |
| `factory` | Autonomous generation across environments | Tier 3 | 10-60 per environment |
| `self-improving` | Meta-constraints on self-modification | Tier 3 + meta | Variable |

## Core Function Signatures

From the AutoHarness paper (Lou et al., 2026):

```python
def propose_action(board: str) -> str:
    """Propose a valid action given the current state as text.

    Used by action-filter and code-as-policy harness types.
    For action-filter: returns a set of legal moves for the LLM to rank.
    For code-as-policy: returns the chosen action directly (no LLM).
    """

def is_legal_action(board: str, action: str) -> bool:
    """Check if an action string is valid given the current state as text.

    Used by action-verifier harness type.
    Returns True if the action is legal, False otherwise.
    The harness retries with a new LLM proposal on False.
    """

def validate_action(state: dict, action: dict) -> tuple[bool, str]:
    """Validate an action against constraints, returning (valid, reason).

    Amplifier-native version of is_legal_action.
    Used in hook enforcement (tool:pre handlers).
    Returns (True, "") for valid actions.
    Returns (False, "reason for rejection") for invalid actions.
    """
```

## Refinement Decision Logic

When evaluation reveals illegal actions, the refiner must decide WHAT to refine:

| `is_legal_action()` returns | Action actually is | Refine |
|-----------------------------|--------------------|--------|
| True | Legal | Nothing — correct |
| True | Illegal | BOTH `is_legal_action()` AND `propose_action()` |
| False | Illegal | Only `propose_action()` |
| False | Legal | Only `is_legal_action()` — it's too strict |

This decision logic prevents wasted iterations refining the wrong function.

## Nano-Amplifier File Formats

### behavior.yaml

```yaml
bundle:
  name: <environment>-harness
  version: 0.1.0
  description: Constraint harness for <environment>

hooks:
  - module: hooks-harness
    source: {{hooks_harness_source}}
    config:
      constraints_path: ./constraints.py
      harness_type: <action-filter|action-verifier|code-as-policy>
      strict: true
```

### constraints.py

Must export the core functions for the chosen `harness_type`. Must be pure Python with no external dependencies beyond the standard library. Must handle malformed input gracefully (return False/reject, never raise).

### context.md

Describes: what environment this constrains, what the action space is, why each constraint exists, known limitations.

## Deployment Mode Enum

Each generated harness is deployed in one of three modes. The mode determines the entry point and packaging format.

| Mode | Description | Entry Point | Use When |
|------|-------------|-------------|----------|
| `standalone` | Self-contained CLI package, runs without Amplifier | `<harness_name> chat` (pip-installed) | Delivering to teams who don't use Amplifier |
| `in-app` | Amplifier hook only, embedded in an existing bundle | `behavior.yaml` via `includes:` | Enhancing an existing Amplifier workflow |
| `hybrid` | Both standalone CLI and Amplifier hook, side-by-side | CLI + behavior.yaml compose | Maximum flexibility, local dev + Amplifier integration |

### Entry Points by Deployment Mode

| Mode | Amplifier Entry | Standalone Entry | Docker Entry |
|------|----------------|-----------------|--------------|
| `standalone` | — | `<harness_name> chat` | `docker compose up` |
| `in-app` | `includes: ./behavior.yaml` | — | — |
| `hybrid` | `includes: ./behavior.yaml` | `<harness_name> chat` | `docker compose up` |

### Deployment Mode in Config

All generated `config.yaml` files carry a `deployment_mode` field stamped at generation time:

```yaml
deployment_mode: standalone  # standalone | in-app | hybrid
```

## Version Stamping Spec

Every generated harness artifact includes version stamping fields in its `config.yaml`. These fields are populated at generation time and provide traceability back to the harness-machine version that produced the artifact.

### Required Stamping Fields

| Field | Type | Description |
|-------|------|-------------|
| `generated_version` | string | Harness-machine version that generated this artifact (e.g. `0.2.0`) |
| `generated_by` | string | Generator identifier (e.g. `harness-machine:harness-generator`) |
| `deployment_mode` | string | Deployment mode: `standalone`, `in-app`, or `hybrid` |
| `harness_name` | string | Mission-based name for this harness (e.g. `chess-legal-moves`) |
| `package_name` | string | Python package name (snake_case, e.g. `chess_legal_moves`) |
| `tier` | string | Size tier: `pico`, `nano`, or `micro` |
| `project_root` | string | Absolute path to the project root at generation time |
| `model` | string | LLM model used during generation (e.g. `claude-opus-4-5`) |

### Template Variables

Config templates use Mustache-style double-brace syntax for variable substitution:

```yaml
generated_version: {{generated_version}}
generated_by: {{generated_by}}
deployment_mode: {{deployment_mode}}
harness_name: {{harness_name}}
package_name: {{package_name}}
tier: {{tier}}
project_root: {{project_root}}
model: {{model}}
```

### Hook Source Variable

The `behavior.yaml` template uses a source variable for the hooks-harness module:

| Variable | Description | Example |
|----------|-------------|---------|
| `hooks_harness_source` | Git source URL for the hooks-harness module, pinned to a tagged release | `git+https://github.com/microsoft/amplifier-bundle-harness-machine@v0.2.0#subdirectory=modules/hooks-harness` |

The generator MUST:
1. Use the current harness-machine repo URL (not a hardcoded personal org)
2. Pin to a version tag (`@v0.2.0`), not `@main` — so generated harnesses survive repo reorganization
3. Include `#subdirectory=modules/hooks-harness`

Substitution is performed by `harness-machine:harness-generator` at generation time.
