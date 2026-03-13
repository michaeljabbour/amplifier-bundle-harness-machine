# Harness Runtime Gap Fix Design

## Goal

Close the runtime gap in amplifier-bundle-harness-machine so that generated nano-amplifiers are self-contained constrained agent runtimes — not just constraint libraries. A generated harness should be usable three ways: as an Amplifier hook (compose into any bundle), as a standalone CLI agent (zero Amplifier dependency), or as a Docker container.

## Background

### The Problem

The harness-machine's first real test produced pico-amplifier at `~/dev/pico-amplifier` — a set of constraint functions (`is_legal_action`, `validate_file_path`, `validate_bash_command`) with 81 passing tests. The constraint logic is production-grade after 6 refinement iterations.

But the output is not self-contained:

- **No enforcement layer** — nothing calls `is_legal_action()` at runtime
- **No hook loader** — `behavior.yaml` declares intent but nothing reads it
- **No LLM wrapper / agent loop** — no code wraps an LLM, intercepts tool proposals, gates them through constraints
- **No tool executor** — validates `read_file`/`bash` but doesn't actually execute them
- **Hardcoded `PROJECT_ROOT`** instead of loading from config
- **No system prompt** — the constrained agent has no mission/scope/retry instructions
- **No CLI entry point** — no way to say `pico-amplifier chat` and get a constrained agent

This is like building a lock without a door. The constraint logic is the lock — excellent and battle-tested. The runtime is the door — completely absent.

### Reference Architecture

NanoClaw (`github.com/qwibitai/nanoclaw`) — 15 files, ~3,900 lines, security-first standalone agent with container isolation. Proves that a self-contained constrained agent runtime can be small and auditable.

### Core Insight

> "constraints.py is the brick. The deployment targets are different studs."

The constraint logic is the invariant core. Everything else is an adapter connecting that core to a runtime. The generator should produce only what varies. The infrastructure should be pre-built, tested, and static.

## Approach

**Ship static runtime scaffold in the harness-machine bundle, generate only what varies. Docker as an optional third deployment mode.**

Why this over generating everything: The runtime components (LLM client, tool executor, hook loader, retry loop, CLI) are ~700 lines of Python identical for every nano-amplifier. Generating them fresh each time is wasteful and error-prone. The generator stays focused on what LLMs are good at: constraint logic and documentation.

Why this over Docker-only: Docker is heavyweight for nano-scale. It is an optional layer on top of the standalone runtime, not a replacement.

## Architecture: One Brick, Three Studs

A generated nano-amplifier ships as a directory with one core and three deployment adapters:

```
pico-amplifier/
├── constraints.py           # THE BRICK — generated, unique per harness
├── config.yaml              # GENERATED — project_root, harness_type, covered_tools, allowed_env_vars
├── context.md               # GENERATED — constraint rationale, limitations
├── system-prompt.md         # GENERATED — agent mission, scope, retry instructions
├── test_constraints.py      # GENERATED — constraint test suite
│
├── behavior.yaml            # STUD 1: AMPLIFIER — references generic hooks-harness module
│                            #   Use: amplifier --bundle ./pico-amplifier
│
├── standalone/              # STUD 2: STANDALONE CLI — copied from runtime scaffold
│   ├── pyproject.toml       #   Use: cd standalone && pip install -e . && pico-amplifier chat
│   ├── pico_amplifier/
│   │   ├── __init__.py
│   │   ├── cli.py           # Entry point: chat, check, audit subcommands
│   │   ├── runtime.py       # LLM client + constraint gate + retry loop
│   │   ├── tools.py         # Tool implementations (read_file, write_file, bash, grep, glob)
│   │   └── constraints.py   # Same file, copied in for zero-dependency
│   ├── config.yaml          # Same config, copied in
│   └── system-prompt.md     # Same prompt, copied in
│
└── docker/                  # STUD 3: DOCKER — optional, from template
    ├── Dockerfile           #   Use: cd docker && docker compose up
    └── docker-compose.yaml
```

## Components

### Generated Per Harness (unique every time)

These are the files the LLM agents create during the harness-machine pipeline:

| File | Purpose |
|------|---------|
| `constraints.py` | The constraint logic (`is_legal_action`, `validate_file_path`, `validate_bash_command`) |
| `config.yaml` | `project_root`, `harness_type`, `covered_tools` list, `allowed_env_vars` list, `max_retries` |
| `context.md` | Constraint rationale, limitations, known edge cases |
| `system-prompt.md` | Agent mission, scope rules, what to do when a call is rejected |
| `test_constraints.py` | Constraint test suite |

### Stud 1: Generic Amplifier Hook Module (`modules/hooks-harness/`)

A proper Amplifier hook module (~100 lines) that dynamically loads ANY `constraints.py` and enforces it via `tool:pre` deny. Ships with the harness-machine bundle, shared by all generated harnesses.

Key design decisions:

- `mount()` function following the Hook protocol from amplifier-core
- Dynamically loads `constraints.py` via `importlib.util` from the path specified in config
- Registers on `tool:pre` at priority 5 (high — enforce before other hooks)
- On illegal action: returns `HookResult(action="deny", reason="Constraint violation: {reason}")` with `context_injection` explaining why, enabling agent self-correction
- On legal action: returns `HookResult(action="continue")`
- `PROJECT_ROOT` resolved from `coordinator.get_capability("session.working_dir")` — no hardcoding
- Strict mode (deny) vs warn mode (`inject_context` only) via config flag
- Supports both `validate_action(state, action)` and `is_legal_action(tool_name, params)` signatures with auto-detection

The `behavior.yaml` in each generated harness references this module via git URL:

```yaml
hooks:
  - module: hooks-harness
    source: git+https://github.com/michaeljabbour/amplifier-bundle-harness-machine@main#subdirectory=modules/hooks-harness
    config:
      constraints_path: ./constraints.py
      harness_type: action-verifier
      strict: true
```

### Stud 2: Standalone Runtime Scaffold (`runtime/`)

A static Python package (~600 lines total) that provides the complete agent loop. Copied per harness with only `constraints.py` and `config.yaml` injected.

#### `runtime/runtime.py` (~300 lines)

- LLM client via litellm (supports Anthropic, OpenAI, Google, local models via one interface)
- Conversation history management (system prompt + user/assistant/tool messages)
- Tool call parsing from LLM response
- Constraint gate: calls `is_legal_action(tool_name, params)` before tool execution
- On rejection: adds rejection reason to conversation, re-prompts LLM (`max_retries` from config)
- On approval: dispatches to tool executor, returns result to conversation
- Clean shutdown on Ctrl+C

#### `runtime/tools.py` (~200 lines)

- `read_file(file_path)` — reads file, respects `project_root` boundary
- `write_file(file_path, content)` — writes file, respects `project_root` boundary
- `edit_file(file_path, old_string, new_string)` — string replacement
- `bash(command, timeout)` — subprocess execution with timeout
- `grep(pattern, path)` — ripgrep or Python `re` fallback
- `glob(pattern, path)` — file pattern matching
- All tools enforce `project_root` boundary independently (defense-in-depth)

#### `runtime/cli.py` (~100 lines)

- `pico-amplifier chat` — interactive constrained agent session
- `pico-amplifier check <tool_name> <params_json>` — one-shot constraint validation
- `pico-amplifier audit <transcript_file>` — post-hoc analysis of agent actions
- Loads `config.yaml` for `project_root`, model, `harness_type`
- Loads `system-prompt.md` for agent instructions

#### `runtime/pyproject.toml.template` (~20 lines)

- Template with `{{harness_name}}` variable for package name
- Dependencies: litellm (LLM client), pyyaml (config loading)
- Entry point: `pico-amplifier = "pico_amplifier.cli:main"`

### Stud 3: Docker Templates (~50 lines total)

#### `runtime/Dockerfile.template`

- `FROM python:3.12-slim`
- `COPY` standalone package
- `pip install`
- `ENTRYPOINT` pointing to CLI

#### `runtime/docker-compose.template.yaml`

- Service definition, `network_mode: host`, environment for API keys

### Templated Per Harness (variables injected at `/harness-finish`)

| File | Variable Injected |
|------|-------------------|
| `behavior.yaml` | hooks-harness git URL + local `constraints_path` |
| `standalone/pyproject.toml` | Package name from config |
| `docker/Dockerfile` | Harness name |
| `docker/docker-compose.yaml` | Container name |

## Data Flow

### Amplifier Path (Stud 1)

```
User prompt
  -> Amplifier orchestrator
    -> LLM proposes tool call (e.g., bash "rm -rf /")
      -> hooks-harness tool:pre handler fires
        -> loads constraints.py, calls is_legal_action("bash", {"command": "rm -rf /"})
          -> returns (False, "rm with recursive+force flags not permitted")
        -> returns HookResult(action="deny", reason="...")
      -> orchestrator injects rejection reason into context
    -> LLM retries with legal action
      -> hooks-harness validates -> returns HookResult(action="continue")
    -> tool executes normally
```

### Standalone Path (Stud 2)

```
User types in CLI
  -> runtime.py sends to LLM via litellm
    -> LLM proposes tool call
      -> runtime.py calls is_legal_action(tool_name, params)
        -> returns (False, reason)
      -> runtime.py adds rejection message to conversation
    -> LLM retries
      -> is_legal_action returns (True, "")
      -> tools.py executes the tool
      -> result added to conversation
    -> LLM responds to user
```

### Docker Path (Stud 3)

Same as standalone, just inside a container with API keys passed via environment.

## Changes to the Harness-Machine Bundle

### New Files to Add

| File | Est. Lines | Purpose |
|------|-----------|---------|
| `modules/hooks-harness/pyproject.toml` | ~15 | Package definition for the generic hook module |
| `modules/hooks-harness/amplifier_module_hooks_harness/__init__.py` | ~100 | `mount()` + `tool:pre` handler. Dynamic `constraints.py` loading, deny/continue, `project_root` from capability |
| `runtime/__init__.py` | ~5 | Package marker |
| `runtime/runtime.py` | ~300 | Standalone agent loop: litellm client, constraint gate, retry, conversation management |
| `runtime/tools.py` | ~200 | Tool implementations: `read_file`, `write_file`, `edit_file`, `bash`, `grep`, `glob` with `project_root` enforcement |
| `runtime/cli.py` | ~100 | CLI entry point: `chat`, `check`, `audit` subcommands |
| `runtime/pyproject.toml.template` | ~20 | Template for generated standalone package |
| `runtime/Dockerfile.template` | ~20 | Template for Docker deployment |
| `runtime/docker-compose.template.yaml` | ~15 | Template for Docker Compose |

Total new Python: ~735 lines (all static infrastructure, tested once).

### Files to Update

| File | Change |
|------|--------|
| `modes/harness-finish.md` | Add 3-stud packaging steps: generate `behavior.yaml`, copy standalone scaffold + inject constraints, optionally stamp Docker |
| `agents/harness-generator.md` | Add `system-prompt.md` and `config.yaml` to output contract (2 more generated files) |
| `context/examples/nano-filesystem-harness.md` | Show complete 3-stud artifact, not just `constraints.py` |
| `context/examples/developer-tooling-harness.md` | Same — show complete artifact |
| `context/examples/domain-library-harness.md` | Same |
| `context/examples/enterprise-governance-harness.md` | Same |
| `context/harness-format.md` | Update nano-amplifier format spec to include `standalone/` and `docker/` studs |
| `behaviors/harness-machine.yaml` | Add hooks-harness module reference |
| `tests/test_scaffold.py` | Add tests for `modules/hooks-harness/` and `runtime/` directories |

### What Stays the Same

- All 7 modes (pipeline unchanged; `/harness-finish` gets richer packaging)
- All 7 agents (generator adds 2 files to output, core job unchanged)
- All 4 recipes (orchestration unchanged, packaging happens at finish)
- The constraint generation loop (generator -> critic -> refiner -> evaluator)
- All 3 skills
- All templates for factory mode

## The `/harness-finish` Packaging Flow

The current `/harness-finish` mode just commits and presents 4 delivery options. It needs to become a packaging step that assembles the complete nano-amplifier before delivery.

New flow:

1. **Verify evaluation evidence exists** (same as today)
2. **Package the Amplifier stud** — generate `behavior.yaml` pointing to `hooks-harness` via the bundle's git URL, with `constraints_path` pointing to local `constraints.py`
3. **Package the standalone stud** — copy `runtime/` scaffold from the harness-machine bundle into `standalone/`, inject `constraints.py`, write `config.yaml` with `project_root` resolved from the actual project, inject `system-prompt.md`
4. **Package the Docker stud (optional)** — ask user "Do you also want Docker deployment?" If yes, stamp out `Dockerfile` and `docker-compose.yaml` from templates
5. **Present delivery options** — same 4 options (merge/PR/keep/discard), but now the artifact is a complete self-contained directory

## Error Handling

### Constraint Gate Errors

- `is_legal_action()` raises exception: treat as deny (fail-closed), log the error
- `constraints.py` not found at path: `mount()` fails with clear error message
- Neither `validate_action()` nor `is_legal_action()` exported: `mount()` fails with clear error

### Standalone Runtime Errors

- LLM API unavailable: retry with exponential backoff, exit after 3 failures
- Tool execution fails: return error to LLM as tool result, let it adapt
- Max retries exhausted on same tool call: inform user, skip to next prompt
- `config.yaml` missing: use defaults (`cwd` as `project_root`, `action-verifier` type)
- `system-prompt.md` missing: use minimal default prompt

### Docker Errors

- API key not in environment: clear error message with instructions
- Container cannot reach LLM API: `network_mode: host` should handle this

## Testing Strategy

### Hook Module Tests

- Test `mount()` with valid `constraints.py` succeeds
- Test `mount()` with missing file raises `FileNotFoundError`
- Test `mount()` with no `validate_action`/`is_legal_action` raises `ValueError`
- Test `tool:pre` with legal action returns `HookResult(continue)`
- Test `tool:pre` with illegal action returns `HookResult(deny)` with reason
- Test `strict=false` returns `HookResult(inject_context)` instead of deny
- Test `project_root` resolution from capability

### Standalone Runtime Tests

- Test constraint gate blocks illegal actions
- Test constraint gate passes legal actions
- Test retry loop re-prompts after rejection (mock LLM)
- Test max_retries exhaustion
- Test tool implementations respect `project_root`
- Test CLI subcommands (`chat`, `check`, `audit`)

### Integration Test

- Use pico-amplifier's existing 81 constraint tests as the validation suite
- Run `standalone/pico-amplifier check` on the same 20 probe cases from the pico-amplifier session
- Verify identical `(bool, reason)` results from both the library and the standalone CLI

## Open Questions

1. **LLM client library for the standalone runtime.** litellm (broadest model support, single dependency) vs raw httpx (zero dependencies but manual per-provider). Recommendation: litellm — it is one dependency and supports every provider.

2. **Streaming responses in the standalone runtime.** For MVP: no. Blocking responses are simpler and the constraint gate needs the complete tool call before validation. Streaming can be added later.

3. **Multiple constraint files (composing nano-amplifiers).** For MVP: one `constraints.py` per harness. Composition happens at the bundle level (Tier 2), not the standalone runtime level.
