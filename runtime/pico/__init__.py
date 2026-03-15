"""Pico Runtime — the smallest standalone constrained-agent tier.

A laser-focused, single-provider, no-frills constrained agent CLI.
Copies into each generated harness's standalone/ directory at packaging time.

Components:
    gate.py     — ConstraintGate: load constraints.py, check actions
    tools.py    — LocalToolExecutor: 7 project-root-scoped tools
    runtime.py  — PicoAgent: async litellm loop with retry + hard cap
    cli.py      — argparse CLI (chat / check / audit) with Rich output
"""
