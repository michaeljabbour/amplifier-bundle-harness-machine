"""Nano Runtime — the sweet spot tier with streaming, session persistence,
dynamic context loading, and multi-provider support.

A full-featured constrained-agent CLI that extends Pico with:
  - Streaming responses (Rich Console live output via litellm streaming)
  - Session persistence (JSON-backed .sessions/ directory)
  - Dynamic context loading (@mention file references in prompts)
  - Multi-provider support (configure and switch providers at runtime)

Copies into each generated harness's standalone/ directory at packaging time.

Components:
    gate.py       — ConstraintGate: load constraints.py, check actions
    tools.py      — LocalToolExecutor: 7 project-root-scoped tools
    runtime.py    — NanoAgent: async litellm loop with streaming + session
    cli.py        — argparse CLI (chat / check / audit) with Rich output
    streaming.py  — StreamHandler: Rich-backed streaming completions
    session.py    — SessionManager: JSON file-based session persistence
    context.py    — ContextLoader: @mention file reference resolution
    providers.py  — ProviderManager: multi-provider config and switching
"""
