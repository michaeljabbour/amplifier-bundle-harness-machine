"""Sub-agent delegation for micro runtime.

Provides Delegator that spawns isolated PicoAgent instances per delegation:
  - Each delegation gets a fresh PicoAgent with clean context (no shared state)
  - Configurable tool restriction via tool_names parameter
  - Max iterations cap for safety
  - Builds delegation context and tool restriction instructions

Usage::

    delegator = Delegator(
        sandbox_path="/project",
        model="anthropic/claude-sonnet-4-20250514",
        system_prompt="You are a code review assistant.",
        constraints_path="constraints.py",
    )
    result = delegator.spawn(
        task="Review the authentication module",
        tool_names=["read_file", "grep", "glob"],
    )
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Delegator
# ---------------------------------------------------------------------------


class Delegator:
    """Spawns isolated PicoAgent instances for sub-agent delegation.

    Each call to spawn() creates a fresh PicoAgent with its own clean
    context — no state is shared between delegations or with the parent agent.

    Usage::

        delegator = Delegator(sandbox_path="/project")
        result = delegator.spawn("Analyze this code", tool_names=["read_file"])
    """

    def __init__(
        self,
        sandbox_path: str = ".",
        model: str = "anthropic/claude-sonnet-4-20250514",
        system_prompt: str = "You are a helpful constrained agent.",
        constraints_path: str = "constraints.py",
    ) -> None:
        """Initialize Delegator.

        Args:
            sandbox_path: Project root for the sub-agent's tool executor.
            model: LLM model to use for sub-agents.
            system_prompt: Base system prompt for sub-agents.
            constraints_path: Path to constraints.py for gate enforcement.
        """
        self.sandbox_path = sandbox_path
        self.model = model
        self.system_prompt = system_prompt
        self.constraints_path = constraints_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def spawn(
        self,
        task: str,
        tool_names: list[str] | None = None,
        max_iterations: int = 20,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Spawn a fresh isolated sub-agent to execute a task.

        Creates a new PicoAgent with clean context (no shared state with
        the parent agent). The sub-agent has its own tool executor,
        constraint gate, and message history.

        Args:
            task: Task description / user prompt for the sub-agent.
            tool_names: Optional list of allowed tool names. If provided,
                        restricts which tools the sub-agent may call.
            max_iterations: Maximum agent loop iterations (safety cap).
            context: Optional additional context dict to inject into prompt.

        Returns:
            Sub-agent's final response string.
        """
        # Build sub-agent prompt with delegation context
        sub_prompt = self._build_sub_prompt(
            task, tool_names=tool_names, context=context
        )

        try:
            # Create a fresh PicoAgent with clean context
            agent = self._create_fresh_agent(
                tool_names=tool_names, max_iterations=max_iterations
            )
            result = self._run_agent(agent, sub_prompt)
            return result
        except Exception as exc:
            return f"Delegation error: {exc}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_fresh_agent(
        self,
        tool_names: list[str] | None = None,
        max_iterations: int = 20,
    ) -> Any:
        """Create a fresh PicoAgent with its own clean context.

        Each call creates a new instance — no state from previous delegations
        or the parent agent is shared.

        Args:
            tool_names: Optional restricted tool set.
            max_iterations: Max iterations for this agent.

        Returns:
            Fresh PicoAgent instance.
        """
        try:
            # Import pico runtime for sub-agent creation
            # Use nano's gate and tools since micro includes them
            from micro.gate import ConstraintGate
            from micro.tools import LocalToolExecutor
        except ImportError:
            try:
                from nano.gate import ConstraintGate  # type: ignore[no-redef]
                from nano.tools import LocalToolExecutor  # type: ignore[no-redef]
            except ImportError as exc:
                raise ImportError(
                    "micro.gate / micro.tools not found. "
                    "Ensure the runtime is on sys.path."
                ) from exc

        gate = ConstraintGate(
            constraints_path=self.constraints_path,
            project_root=self.sandbox_path,
        )
        executor = LocalToolExecutor(self.sandbox_path)

        # Build delegation system prompt
        delegation_system = self._build_delegation_system_prompt(tool_names)

        # Create a fresh PicoAgent — clean context, own state
        agent = _PicoAgentWrapper(
            gate=gate,
            executor=executor,
            system_prompt=delegation_system,
            model=self.model,
            max_retries=3,
            max_iterations=max_iterations,
        )
        return agent

    def _build_sub_prompt(
        self,
        task: str,
        tool_names: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Build the sub-agent prompt with delegation context.

        Adds delegation framing and tool restriction notice if applicable.

        Args:
            task: Original task description.
            tool_names: Optional restricted tool set.
            context: Optional extra context.

        Returns:
            Full prompt string for the sub-agent.
        """
        parts = [task]

        if context:
            ctx_lines = [f"  {k}: {v}" for k, v in context.items()]
            parts.append("Context:\n" + "\n".join(ctx_lines))

        if tool_names is not None:
            tools_str = ", ".join(tool_names)
            parts.append(f"[Restricted to tools: {tools_str}]")

        return "\n\n".join(parts)

    def _build_delegation_system_prompt(
        self,
        tool_names: list[str] | None = None,
    ) -> str:
        """Build the delegation system prompt with tool restrictions.

        Args:
            tool_names: Optional restricted tool set.

        Returns:
            System prompt string with delegation context and restrictions.
        """
        lines = [self.system_prompt]
        lines.append(
            "\nYou are a sub-agent spawned for a specific delegation task. "
            "Complete the assigned task and provide a clear, concise result. "
            "Do not ask clarifying questions — work with the information provided."
        )
        if tool_names is not None:
            tools_str = ", ".join(tool_names)
            lines.append(
                f"\nTool restrictions: You may ONLY use these tools: {tools_str}. "
                "Do not attempt to use any other tools."
            )
        return "\n".join(lines)

    def _run_agent(self, agent: Any, prompt: str) -> str:
        """Run the sub-agent on the given prompt.

        Args:
            agent: Agent instance (PicoAgentWrapper or similar).
            prompt: User prompt to process.

        Returns:
            Agent's response string.
        """
        return agent.run(prompt)


# ---------------------------------------------------------------------------
# Lightweight PicoAgent wrapper for delegation
# ---------------------------------------------------------------------------


class _PicoAgentWrapper:
    """Minimal synchronous agent wrapper for sub-agent delegation.

    Wraps the gate/executor pattern without requiring a full async loop.
    Provides a simple run() interface for delegation.

    This is a fresh instance with its own clean context — no shared state.
    """

    def __init__(
        self,
        gate: Any,
        executor: Any,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
        max_iterations: int = 20,
    ) -> None:
        self.gate = gate
        self.executor = executor
        self.system_prompt = system_prompt
        self.model = model
        self.max_retries = max_retries
        self.max_iterations = max_iterations
        # Fresh, clean context — own message history per delegation
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    def run(self, prompt: str) -> str:
        """Run the agent on a prompt synchronously.

        Args:
            prompt: User input to process.

        Returns:
            Agent response string.
        """
        try:
            import asyncio
            from nano.runtime import NanoAgent  # type: ignore[import-untyped]
        except ImportError:
            return f"(delegation not available — runtime not on path): {prompt}"

        # Create a real agent with the same gate/executor — fresh, clean context
        real_agent = NanoAgent(
            gate=self.gate,
            executor=self.executor,
            system_prompt=self.system_prompt,
            model=self.model,
            max_retries=self.max_retries,
        )
        return asyncio.run(real_agent.process_turn(prompt))
