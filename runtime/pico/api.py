"""Pico in-app entry point (deployment mode: in-app).

Pure Python API for embedding pico-tier agent capabilities directly in an
application. No CLI machinery (no argparse, no rich, no signal handling).

Exports:
  - PicoAgent: async run() entry point for the constrained agent loop
  - ConstraintGate: check() interface for validating tool actions
  - ToolExecutor: execute() interface for running tool calls
  - check(): convenience function for one-shot constraint checking

Usage::

    from pico.api import PicoAgent, ConstraintGate, ToolExecutor, check

    gate = ConstraintGate("constraints.py", project_root="/project")
    executor = ToolExecutor("/project")
    agent = PicoAgent(
        constraints_path="constraints.py",
        project_root="/project",
        system_prompt="You are a helpful assistant.",
    )
    result = await agent.run("Summarize the Python files in src/")
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# ConstraintGate — thin re-export wrapper
# ---------------------------------------------------------------------------


class ConstraintGate:
    """Constraint gate for checking tool actions before dispatch.

    Wraps pico.gate.ConstraintGate with a simplified API.

    Usage::

        gate = ConstraintGate("constraints.py", project_root="/project")
        allowed, reason = gate.check("read_file", {"file_path": "src/main.py"})
    """

    def __init__(
        self,
        constraints_path: str,
        project_root: str | None = None,
    ) -> None:
        """Initialize the constraint gate.

        Args:
            constraints_path: Path to constraints.py module.
            project_root: Optional project root; defaults to cwd.
        """
        # Lazy import to avoid top-level dependency on pico.gate at import time
        from pico.gate import ConstraintGate as _ConstraintGate  # noqa: PLC0415

        self._gate = _ConstraintGate(
            constraints_path=constraints_path,
            project_root=project_root,
        )

    def check(self, tool_name: str | None, parameters: dict | None) -> tuple[bool, str]:
        """Check whether a tool action is permitted.

        Args:
            tool_name: Name of the tool being called.
            parameters: Tool parameters dict (may be None or empty).

        Returns:
            ``(True, "")`` if the action is legal.
            ``(False, reason)`` if the action is denied.
        """
        return self._gate.check(tool_name, parameters)


# ---------------------------------------------------------------------------
# ToolExecutor — thin re-export wrapper
# ---------------------------------------------------------------------------


class ToolExecutor:
    """Local tool executor with project_root boundary enforcement.

    Wraps pico.tools.LocalToolExecutor with an ``execute()`` dispatch method.

    Usage::

        executor = ToolExecutor("/project")
        result = executor.execute("read_file", {"file_path": "src/main.py"})
    """

    def __init__(self, project_root: str) -> None:
        """Initialize the tool executor.

        Args:
            project_root: Root directory; all paths validated against this.
        """
        from pico.tools import LocalToolExecutor  # noqa: PLC0415

        self._executor = LocalToolExecutor(project_root)

    def execute(self, tool_name: str, parameters: dict[str, Any]) -> str:
        """Execute a named tool with given parameters.

        Args:
            tool_name: Name of the tool (read_file, write_file, bash, etc.).
            parameters: Tool parameters dict.

        Returns:
            Tool result as a string.

        Raises:
            AttributeError: If the tool name is not recognized.
        """
        from pico.tools import _TOOL_METHOD_MAP  # noqa: PLC0415

        method_name = _TOOL_METHOD_MAP.get(tool_name)
        if method_name is None:
            return f"Unknown tool: {tool_name}"
        method = getattr(self._executor, method_name, None)
        if method is None:
            return f"Tool method not found: {method_name}"
        return str(method(**parameters))


# ---------------------------------------------------------------------------
# PicoAgent — async run() entry point
# ---------------------------------------------------------------------------


class PicoAgent:
    """Async constrained agent with a simple run() entry point.

    Wraps pico.runtime.PicoAgent with a clean async run() interface
    suitable for in-app embedding.

    Usage::

        agent = PicoAgent(
            constraints_path="constraints.py",
            project_root="/project",
            system_prompt="You are a helpful assistant.",
            model="anthropic/claude-sonnet-4-20250514",
        )
        result = await agent.run("Summarize the Python files in src/")
    """

    def __init__(
        self,
        constraints_path: str,
        project_root: str,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
    ) -> None:
        """Initialize PicoAgent.

        Args:
            constraints_path: Path to constraints.py module.
            project_root: Project root for tool boundary enforcement.
            system_prompt: System prompt for the agent.
            model: litellm model string.
            max_retries: Max gate-denial retries per turn.
        """
        self.constraints_path = constraints_path
        self.project_root = project_root
        self.system_prompt = system_prompt
        self.model = model
        self.max_retries = max_retries
        self._agent: Any = None

    def _ensure_agent(self) -> Any:
        """Lazily initialize the underlying PicoAgent runtime."""
        if self._agent is None:
            from pico.gate import ConstraintGate as _Gate  # noqa: PLC0415
            from pico.runtime import PicoAgent as _PicoAgent  # noqa: PLC0415
            from pico.tools import LocalToolExecutor  # noqa: PLC0415

            gate = _Gate(
                constraints_path=self.constraints_path,
                project_root=self.project_root,
            )
            executor = LocalToolExecutor(self.project_root)
            self._agent = _PicoAgent(
                gate=gate,
                executor=executor,
                system_prompt=self.system_prompt,
                model=self.model,
                max_retries=self.max_retries,
            )
        return self._agent

    async def run(self, prompt: str) -> str:
        """Run one agent turn asynchronously.

        Args:
            prompt: User message to process.

        Returns:
            Agent's final text response.
        """
        agent = self._ensure_agent()
        return await agent.process_turn(prompt)


# ---------------------------------------------------------------------------
# check() — convenience function for one-shot constraint validation
# ---------------------------------------------------------------------------


def check(
    constraints_path: str,
    tool_name: str,
    parameters: dict[str, Any] | None = None,
    project_root: str | None = None,
) -> tuple[bool, str]:
    """One-shot convenience function for checking a tool action against constraints.

    Creates a ConstraintGate, checks the action, and returns the result.
    Useful for quick validation without creating a full agent.

    Args:
        constraints_path: Path to constraints.py module.
        tool_name: Name of the tool to check.
        parameters: Tool parameters dict (optional).
        project_root: Optional project root; defaults to cwd.

    Returns:
        ``(True, "")`` if the action is legal.
        ``(False, reason)`` if the action is denied.
    """
    gate = ConstraintGate(
        constraints_path=constraints_path,
        project_root=project_root,
    )
    return gate.check(tool_name, parameters or {})
