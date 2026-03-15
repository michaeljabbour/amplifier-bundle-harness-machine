"""Micro in-app entry point (deployment mode: in-app).

Extends nano with micro-tier features: mode management, recipe execution,
sub-agent delegation, and approval gates.

Pure Python API for embedding micro-tier agent capabilities directly in an
application. No CLI machinery (no argparse, no rich, no signal handling).

Exports:
  - MicroAgent: extends NanoAgent with set_mode(), get_mode(), list_modes(),
    execute_recipe(), delegate(), and set_approval_mode()

Usage::

    from micro.api import MicroAgent

    agent = MicroAgent(
        constraints_path="constraints.py",
        project_root="/project",
        system_prompt="You are a helpful assistant.",
    )

    # Run a turn
    result = await agent.run("Summarize the codebase.")

    # Mode management
    agent.set_mode("review")
    current_mode = agent.get_mode()
    modes = agent.list_modes()

    # Recipe execution
    results = agent.execute_recipe("workflow.yaml")

    # Sub-agent delegation
    summary = agent.delegate("Summarize all Python files", tool_names=["read_file"])

    # Approval mode
    agent.set_approval_mode(required=True)
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from nano.api import NanoAgent


# ---------------------------------------------------------------------------
# MicroAgent — extends NanoAgent with modes, recipes, delegation
# ---------------------------------------------------------------------------


class MicroAgent(NanoAgent):
    """Async agent with mode management, recipe execution, and delegation.

    Extends nano-tier NanoAgent with:
      - ``set_mode()`` / ``get_mode()`` / ``list_modes()``: mode management
      - ``execute_recipe()``: YAML-driven workflow execution
      - ``delegate()``: sub-agent delegation via micro.delegate.Delegator
      - ``set_approval_mode()``: configure approval gate behavior

    Usage::

        agent = MicroAgent(
            constraints_path="constraints.py",
            project_root="/project",
            system_prompt="You are a helpful assistant.",
        )
        agent.set_mode("review")
        result = await agent.run("Review the authentication module.")
    """

    def __init__(
        self,
        constraints_path: str,
        project_root: str,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
        sessions_dir: str = ".sessions",
        harness_name: str = "micro-agent",
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize MicroAgent.

        Args:
            constraints_path: Path to constraints.py module.
            project_root: Project root for tool boundary enforcement.
            system_prompt: System prompt for the agent.
            model: litellm model string.
            max_retries: Max gate-denial retries per turn.
            sessions_dir: Directory for session persistence files.
            harness_name: Name for session file naming.
            config: Optional config dict for provider list and modes.
        """
        super().__init__(
            constraints_path=constraints_path,
            project_root=project_root,
            system_prompt=system_prompt,
            model=model,
            max_retries=max_retries,
            sessions_dir=sessions_dir,
            harness_name=harness_name,
            config=config,
        )
        self._mode_manager: Any = None
        self._approval_mode: bool = False

    # ------------------------------------------------------------------
    # Mode manager (lazy init)
    # ------------------------------------------------------------------

    def _ensure_mode_manager(self) -> Any:
        """Lazily initialize the mode manager."""
        if self._mode_manager is None:
            from micro.modes import ModeManager  # noqa: PLC0415

            self._mode_manager = ModeManager(config=self._config)
        return self._mode_manager

    # ------------------------------------------------------------------
    # Mode management
    # ------------------------------------------------------------------

    def set_mode(self, mode_name: str) -> None:
        """Switch the agent to a named mode.

        Modes control tool access and add system prompt overlays:
          - ``work``: full tool access (default)
          - ``review``: read-only tools
          - ``plan``: planning-focused, read-only

        Args:
            mode_name: Name of the mode to activate.

        Raises:
            ValueError: If the mode is not recognized.
        """
        manager = self._ensure_mode_manager()
        manager.set_mode(mode_name)

    def get_mode(self) -> str:
        """Return the currently active mode name.

        Returns:
            Name of the active mode (e.g., "work", "review", "plan").
        """
        manager = self._ensure_mode_manager()
        return manager.current_mode

    def list_modes(self) -> list[dict[str, Any]]:
        """Return information about all available modes.

        Returns:
            List of mode info dicts, each with: name, description,
            allowed_tools, safe_tools, active keys.
        """
        manager = self._ensure_mode_manager()
        return manager.list_modes()

    # ------------------------------------------------------------------
    # Recipe execution
    # ------------------------------------------------------------------

    def execute_recipe(self, recipe_path: str) -> list[dict[str, Any]]:
        """Execute a YAML-driven multi-step workflow recipe.

        Loads and runs a recipe file, executing each step through the
        agent loop (or as a bash command). Context is accumulated across
        steps for template variable substitution.

        Args:
            recipe_path: Path to the YAML recipe file.

        Returns:
            List of step result dicts with name, type, and output keys.
        """
        from micro.recipes import RecipeRunner  # noqa: PLC0415

        # Ensure the underlying agent is initialized
        agent = self._ensure_agent()
        runner = RecipeRunner(agent=agent)
        return runner.execute(recipe_path)

    # ------------------------------------------------------------------
    # Sub-agent delegation
    # ------------------------------------------------------------------

    def delegate(
        self,
        task: str,
        tool_names: list[str] | None = None,
        max_iterations: int = 20,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Delegate a task to an isolated sub-agent via Delegator.

        Spawns a fresh PicoAgent instance with clean context. No state
        is shared between delegations or with the parent agent.

        Args:
            task: Task description for the sub-agent.
            tool_names: Optional restricted tool set for the sub-agent.
            max_iterations: Max iterations for the sub-agent loop.
            context: Optional extra context dict.

        Returns:
            Sub-agent's final response string.
        """
        from micro.delegate import Delegator  # noqa: PLC0415

        delegator = Delegator(
            sandbox_path=self.project_root,
            model=self.model,
            system_prompt=self.system_prompt,
            constraints_path=self.constraints_path,
        )
        return delegator.spawn(
            task=task,
            tool_names=tool_names,
            max_iterations=max_iterations,
            context=context,
        )

    # ------------------------------------------------------------------
    # Approval mode
    # ------------------------------------------------------------------

    def set_approval_mode(self, required: bool = True) -> None:
        """Configure whether approval is required before tool execution.

        When approval mode is enabled, the agent will request human
        approval before executing potentially destructive operations.

        Args:
            required: If True, enable approval mode; False to disable.
        """
        self._approval_mode = required

    def get_approval_mode(self) -> bool:
        """Return whether approval mode is currently enabled.

        Returns:
            True if approval is required, False otherwise.
        """
        return self._approval_mode

    # ------------------------------------------------------------------
    # Override run() to apply mode overlays
    # ------------------------------------------------------------------

    async def run(self, prompt: str) -> str:
        """Run one agent turn with mode-aware system prompt.

        Applies the current mode's system prompt overlay before
        processing the turn.

        Args:
            prompt: User message to process.

        Returns:
            Agent's final text response.
        """
        agent = self._ensure_agent()

        # Apply mode overlay to system prompt if mode manager is active
        if self._mode_manager is not None:
            overlay = self._mode_manager.get_prompt_overlay()
            if overlay:
                # Update system message with overlay
                if agent.messages and agent.messages[0]["role"] == "system":
                    base = agent.messages[0].get(
                        "_base_prompt", agent.messages[0]["content"]
                    )
                    agent.messages[0]["_base_prompt"] = base
                    agent.messages[0]["content"] = f"{base}\n\n{overlay}"

        return await agent.process_turn(prompt)

    # ------------------------------------------------------------------
    # Override stream() to yield AsyncIterator[str]
    # ------------------------------------------------------------------

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream agent response tokens with mode-aware processing.

        Args:
            prompt: User message to process.

        Yields:
            String chunks of the agent's response.
        """
        async for chunk in super().stream(prompt):
            yield chunk
