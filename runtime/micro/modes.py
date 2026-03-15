"""Mode system for micro runtime.

Provides a ModeManager that controls agent behavior via named modes:
  - work:   Full tool access, unrestricted operation
  - review: Read-only tools, no write/execute operations
  - plan:   Read-only tools, planning-focused prompt overlay

Each mode can define:
  - description: Human-readable mode description
  - system_prompt_overlay: Additional instructions appended to system prompt
  - allowed_tools: None (all tools allowed) or list of permitted tool names
  - safe_tools: Always-allowed tools regardless of mode restrictions
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Default mode definitions
# ---------------------------------------------------------------------------

DEFAULT_MODES: dict[str, dict[str, Any]] = {
    "work": {
        "description": "Full tool access for unrestricted development work",
        "system_prompt_overlay": "",
        "allowed_tools": None,  # None means all tools are allowed
        "safe_tools": ["read_file", "grep", "glob"],
    },
    "review": {
        "description": "Read-only mode for code review — no write or execute operations",
        "system_prompt_overlay": (
            "You are in REVIEW mode. You may only read files and search code. "
            "Do not write, edit, or execute anything."
        ),
        "allowed_tools": ["read_file", "grep", "glob"],
        "safe_tools": ["read_file", "grep", "glob"],
    },
    "plan": {
        "description": "Planning mode — read code and produce plans, no execution",
        "system_prompt_overlay": (
            "You are in PLAN mode. Focus on understanding the codebase and producing "
            "detailed implementation plans. Do not write or execute code."
        ),
        "allowed_tools": ["read_file", "grep", "glob"],
        "safe_tools": ["read_file", "grep", "glob"],
    },
}


# ---------------------------------------------------------------------------
# ModeManager
# ---------------------------------------------------------------------------


class ModeManager:
    """Manages agent operational modes with tool restrictions and prompt overlays.

    Usage::

        manager = ModeManager()
        manager.set_mode("review")
        overlay = manager.get_prompt_overlay()
        allowed = manager.get_allowed_tools()
        ok = manager.is_tool_allowed("bash")  # False in review mode

    The manager can be initialized with a custom modes dict to override
    the defaults (e.g., from config.yaml).
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize ModeManager with optional config overrides.

        Args:
            config: Optional config dict. If it contains a ``modes`` key,
                    those mode definitions override DEFAULT_MODES entries.
        """
        self._modes: dict[str, dict[str, Any]] = dict(DEFAULT_MODES)

        # Apply config overrides
        if config and "modes" in config:
            for mode_name, mode_def in config["modes"].items():
                if mode_name in self._modes:
                    self._modes[mode_name] = {**self._modes[mode_name], **mode_def}
                else:
                    self._modes[mode_name] = mode_def

        self._current_mode: str = "work"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_mode(self) -> str:
        """Return the name of the currently active mode."""
        return self._current_mode

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------

    def set_mode(self, mode_name: str) -> None:
        """Switch to the named mode.

        Args:
            mode_name: Name of the mode to activate.

        Raises:
            ValueError: If mode_name is not a known mode.
        """
        if mode_name not in self._modes:
            known = ", ".join(sorted(self._modes.keys()))
            raise ValueError(f"Unknown mode: {mode_name!r}. Known modes: {known}")
        self._current_mode = mode_name

    # ------------------------------------------------------------------
    # Mode info
    # ------------------------------------------------------------------

    def get_prompt_overlay(self) -> str:
        """Return the system prompt overlay for the current mode.

        Returns:
            Additional instructions to append to the system prompt,
            or empty string if the mode has no overlay.
        """
        mode_def = self._modes[self._current_mode]
        return mode_def.get("system_prompt_overlay", "")

    def get_allowed_tools(self) -> list[str] | None:
        """Return the allowed tool list for the current mode.

        Returns:
            List of allowed tool names, or None if all tools are allowed.
        """
        mode_def = self._modes[self._current_mode]
        return mode_def.get("allowed_tools", None)

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check whether a tool is permitted in the current mode.

        Args:
            tool_name: Name of the tool to check.

        Returns:
            True if the tool is allowed, False otherwise.
        """
        allowed = self.get_allowed_tools()
        if allowed is None:
            return True  # All tools permitted
        return tool_name in allowed

    def list_modes(self) -> list[dict[str, Any]]:
        """Return a list of info dicts for all available modes.

        Each dict contains: name, description, allowed_tools, safe_tools.

        Returns:
            List of mode info dicts sorted by name.
        """
        result = []
        for name, defn in sorted(self._modes.items()):
            result.append(
                {
                    "name": name,
                    "description": defn.get("description", ""),
                    "allowed_tools": defn.get("allowed_tools"),
                    "safe_tools": defn.get("safe_tools", []),
                    "active": name == self._current_mode,
                }
            )
        return result
