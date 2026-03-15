"""Micro Runtime — the most capable tier with mode system, recipe runner,
sub-agent delegation, approval gates, and dynamic module loading.

A maximum-power constrained-agent CLI that extends Nano with:
  - Mode system (work/review/plan modes with tool restrictions and prompt overlays)
  - Recipe runner (YAML-driven multi-step workflows with approval gates)
  - Sub-agent delegation (spawn isolated PicoAgent instances per delegation)
  - Approval gates (always/dangerous/never approval for sensitive operations)
  - Dynamic plugin loading (discover tools and constraints from .py plugins)

Copies into each generated harness's standalone/ directory at packaging time.

Components:
    gate.py       — ConstraintGate: load constraints.py, check actions
    tools.py      — LocalToolExecutor: 7 project-root-scoped tools
    runtime.py    — MicroAgent: async litellm loop with all micro extensions
    cli.py        — argparse CLI (chat / check / audit) with Rich output
    streaming.py  — StreamHandler: Rich-backed streaming completions
    session.py    — SessionManager: JSON file-based session persistence
    context.py    — ContextLoader: @mention file reference resolution
    providers.py  — ProviderManager: multi-provider config and switching
    modes.py      — ModeManager: work/review/plan mode system with tool gates
    recipes.py    — RecipeRunner: YAML-driven multi-step workflow execution
    delegate.py   — Delegator: isolated PicoAgent sub-agent delegation
    approval.py   — ApprovalGate: always/dangerous/never approval gates
    loader.py     — PluginLoader: dynamic .py plugin discovery and loading
"""
