"""Standalone runtime scaffold for generated nano-amplifiers.

This package provides the agent loop, tool executor, and CLI for
running a constrained agent without Amplifier installed.

Copied into each generated nano-amplifier's standalone/ directory
at /harness-finish packaging time.
"""

from runtime.runtime import AgentLoop, ConstraintGate

__all__ = ["AgentLoop", "ConstraintGate"]
