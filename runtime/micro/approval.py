"""Approval gate for micro runtime.

Provides ApprovalGate that intercepts sensitive tool calls and prompts
the user for explicit approval before execution.

Modes:
  - never:     Auto-approve all tool calls (no prompting)
  - always:    Prompt for every tool call
  - dangerous: Only prompt for sensitive/destructive tool calls

Sensitive tools: bash, write_file, edit_file, apply_patch
Destructive patterns: rm -rf, dd, mkfs, DROP TABLE, etc.
"""

from __future__ import annotations

import re
from typing import Any

try:
    from rich.console import Console

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False
    Console = None  # type: ignore[misc, assignment]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SENSITIVE_TOOLS: frozenset[str] = frozenset(
    {
        "bash",
        "write_file",
        "edit_file",
        "apply_patch",
    }
)

_DESTRUCTIVE_PATTERNS: list[str] = [
    r"rm\s+-rf",
    r"rm\s+-fr",
    r"\bdd\b.*of=",
    r"\bmkfs\b",
    r"\bformat\b.*[A-Z]:",
    r"DROP\s+TABLE",
    r"DROP\s+DATABASE",
    r"TRUNCATE\s+TABLE",
    r"DELETE\s+FROM",
    r"> /dev/",
    r"shred\b",
    r"wipefs\b",
    r":\s*>\s*/",  # :> / truncation
]

# ---------------------------------------------------------------------------
# ApprovalGate
# ---------------------------------------------------------------------------


class ApprovalGate:
    """Intercepts tool calls and prompts for user approval when needed.

    Usage::

        gate = ApprovalGate(mode="dangerous")
        approved = gate.check("bash", {"command": "rm -rf /tmp/old"})
        if not approved:
            print("User denied execution")

    Mode behaviours:
      - ``never``:     Always returns True (auto-approve)
      - ``always``:    Always prompts via _prompt()
      - ``dangerous``: Detects sensitive/destructive calls via _is_sensitive(),
                       prompts only when sensitivity is detected
    """

    def __init__(self, mode: str = "dangerous") -> None:
        """Initialize ApprovalGate.

        Args:
            mode: Approval mode — one of ``always``, ``dangerous``, ``never``.

        Raises:
            ValueError: If mode is not a valid choice.
        """
        valid_modes = ("always", "dangerous", "never")
        if mode not in valid_modes:
            raise ValueError(
                f"Invalid approval mode: {mode!r}. "
                f"Must be one of: {', '.join(valid_modes)}"
            )
        self.mode = mode

        if _RICH_AVAILABLE and Console is not None:
            self._console: Any = Console()
        else:
            self._console = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(self, tool_name: str, params: dict[str, Any]) -> bool:
        """Check whether the tool call is approved for execution.

        Args:
            tool_name: Name of the tool to check.
            params: Tool parameters dict.

        Returns:
            True if approved (proceed), False if denied (skip).
        """
        if self.mode == "never":
            return True  # Auto-approve all

        if self.mode == "always":
            return self._prompt(tool_name, params)

        # dangerous mode: only prompt if sensitive or destructive
        if self._is_sensitive(tool_name, params):
            return self._prompt(tool_name, params)

        return True  # Not sensitive — auto-approve

    # ------------------------------------------------------------------
    # Sensitivity detection
    # ------------------------------------------------------------------

    def _is_sensitive(self, tool_name: str, params: dict[str, Any]) -> bool:
        """Detect whether a tool call is sensitive or destructive.

        Checks:
        1. Tool name is in _SENSITIVE_TOOLS
        2. bash 'command' parameter matches a _DESTRUCTIVE_PATTERNS pattern

        Args:
            tool_name: Tool name to check.
            params: Tool parameters dict.

        Returns:
            True if the call is considered sensitive/dangerous.
        """
        if tool_name in _SENSITIVE_TOOLS:
            return True

        # Extra check for bash commands with destructive patterns
        if tool_name == "bash":
            command = params.get("command", "")
            if self._matches_destructive_pattern(command):
                return True

        return False

    def _matches_destructive_pattern(self, command: str) -> bool:
        """Check if a command string matches any known destructive pattern.

        Args:
            command: Shell command string to check.

        Returns:
            True if any destructive pattern matches.
        """
        for pattern in _DESTRUCTIVE_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    # ------------------------------------------------------------------
    # User prompting
    # ------------------------------------------------------------------

    def _prompt(self, tool_name: str, params: dict[str, Any]) -> bool:
        """Prompt the user for approval of the tool call.

        Uses Rich console if available, falls back to plain input().

        Args:
            tool_name: Tool name being requested.
            params: Tool parameters dict.

        Returns:
            True if the user approves, False if denied.
        """
        formatted = self._format_call(tool_name, params)

        if self._console is not None:
            self._console.print(
                f"\n[bold yellow]⚠ Approval required:[/bold yellow] "
                f"[bold]{tool_name}[/bold]"
            )
            self._console.print(f"  [dim]{formatted}[/dim]")
            answer = input("Approve? [y/N] ").strip().lower()
        else:
            print(f"\nApproval required: {tool_name}")
            print(f"  {formatted}")
            answer = input("Approve? [y/N] ").strip().lower()

        return answer in ("y", "yes")

    def _format_call(self, tool_name: str, params: dict[str, Any]) -> str:
        """Format a tool call for human-readable display.

        Args:
            tool_name: Tool name.
            params: Tool parameters dict.

        Returns:
            Formatted string like: ``bash(command='rm -rf /tmp')``
        """
        param_parts = []
        for key, value in params.items():
            val_str = repr(value)
            if len(val_str) > 80:
                val_str = val_str[:77] + "..."
            param_parts.append(f"{key}={val_str}")
        return f"{tool_name}({', '.join(param_parts)})"
