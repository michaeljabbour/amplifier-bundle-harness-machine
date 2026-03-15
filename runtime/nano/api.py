"""Nano in-app entry point (deployment mode: in-app).

Extends pico with nano-tier features: streaming completions, session
management, and multi-provider switching.

Pure Python API for embedding nano-tier agent capabilities directly in an
application. No CLI machinery (no argparse, no rich, no signal handling).

Exports:
  - NanoAgent: extends PicoAgent with stream(), save_session(),
    resume_session(), switch_provider(), get_current_provider()

Usage::

    from nano.api import NanoAgent

    agent = NanoAgent(
        constraints_path="constraints.py",
        project_root="/project",
        system_prompt="You are a helpful assistant.",
        sessions_dir=".sessions",
    )

    # Run a turn
    result = await agent.run("List all Python files in src/")

    # Save and resume sessions
    agent.save_session("my-session")
    agent.resume_session("my-session")

    # Stream responses
    async for chunk in agent.stream("Explain this code"):
        print(chunk, end="", flush=True)

    # Switch providers at runtime
    agent.switch_provider("openai")
    current = agent.get_current_provider()
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

_log = logging.getLogger(__name__)

# Chunk size used when simulating token-by-token streaming from a full response
_DEFAULT_STREAM_CHUNK_SIZE = 50


# ---------------------------------------------------------------------------
# NanoAgent — extends pico with streaming, sessions, and providers
# ---------------------------------------------------------------------------


class NanoAgent:
    """Async agent with streaming, session management, and provider switching.

    Extends pico-tier capabilities with:
      - ``stream()``: async generator yielding response tokens
      - ``save_session()`` / ``resume_session()``: JSON-backed persistence
      - ``switch_provider()`` / ``get_current_provider()``: runtime switching

    Usage::

        agent = NanoAgent(
            constraints_path="constraints.py",
            project_root="/project",
            system_prompt="You are a helpful assistant.",
        )
        result = await agent.run("Summarize the codebase.")
    """

    def __init__(
        self,
        constraints_path: str,
        project_root: str,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
        sessions_dir: str = ".sessions",
        harness_name: str = "nano-agent",
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize NanoAgent.

        Args:
            constraints_path: Path to constraints.py module.
            project_root: Project root for tool boundary enforcement.
            system_prompt: System prompt for the agent.
            model: litellm model string.
            max_retries: Max gate-denial retries per turn.
            sessions_dir: Directory for session persistence files.
            harness_name: Name for session file naming.
            config: Optional config dict for provider list.
        """
        self.constraints_path = constraints_path
        self.project_root = project_root
        self.system_prompt = system_prompt
        self.model = model
        self.max_retries = max_retries
        self.sessions_dir = sessions_dir
        self.harness_name = harness_name
        self._config = config or {}
        self._agent: Any = None
        self._session_manager: Any = None
        self._provider_manager: Any = None

    # ------------------------------------------------------------------
    # Internal agent initialization (lazy)
    # ------------------------------------------------------------------

    def _ensure_agent(self) -> Any:
        """Lazily initialize the underlying NanoAgent runtime."""
        if self._agent is None:
            from nano.gate import ConstraintGate as _Gate  # noqa: PLC0415
            from nano.runtime import NanoAgent as _NanoAgent  # noqa: PLC0415
            from nano.tools import LocalToolExecutor  # noqa: PLC0415

            gate = _Gate(
                constraints_path=self.constraints_path,
                project_root=self.project_root,
            )
            executor = LocalToolExecutor(self.project_root)
            self._agent = _NanoAgent(
                gate=gate,
                executor=executor,
                system_prompt=self.system_prompt,
                model=self.model,
                max_retries=self.max_retries,
            )
        return self._agent

    def _ensure_session_manager(self) -> Any:
        """Lazily initialize the session manager."""
        if self._session_manager is None:
            from nano.session import SessionManager  # noqa: PLC0415

            self._session_manager = SessionManager(
                harness_name=self.harness_name,
                sessions_dir=self.sessions_dir,
            )
        return self._session_manager

    def _ensure_provider_manager(self) -> Any:
        """Lazily initialize the provider manager."""
        if self._provider_manager is None:
            from nano.providers import ProviderManager  # noqa: PLC0415

            self._provider_manager = ProviderManager(self._config)
        return self._provider_manager

    # ------------------------------------------------------------------
    # Core run
    # ------------------------------------------------------------------

    async def run(self, prompt: str) -> str:
        """Run one agent turn asynchronously.

        Args:
            prompt: User message to process.

        Returns:
            Agent's final text response.
        """
        agent = self._ensure_agent()
        return await agent.process_turn(prompt)

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream agent response tokens.

        Yields response tokens/chunks as they arrive from the LLM.
        Falls back to yielding the full response in one chunk if streaming
        is not available.

        Args:
            prompt: User message to process.

        Yields:
            String chunks of the agent's response.
        """
        agent = self._ensure_agent()

        # Append user turn to history
        agent.messages.append({"role": "user", "content": prompt})

        try:
            from nano.streaming import StreamHandler  # noqa: PLC0415

            handler = StreamHandler(model=self.model)

            # Use streaming LLM call
            response = await handler.stream_completion(
                messages=agent.messages,
                tools=None,
            )
            content = response.get("content") or ""

            # Yield the content in chunks (simulate token streaming)
            for i in range(0, max(len(content), 1), _DEFAULT_STREAM_CHUNK_SIZE):
                yield content[i : i + _DEFAULT_STREAM_CHUNK_SIZE]

            # Update agent history
            agent.messages.append({"role": "assistant", "content": content})

        except Exception as exc:
            # Log the streaming failure so operators can diagnose it
            _log.warning("Streaming failed, falling back to run(): %s", exc)
            # Remove the optimistically-appended user message so process_turn
            # doesn't insert it a second time (duplicate history corruption)
            _user_msg = {"role": "user", "content": prompt}
            if agent.messages and agent.messages[-1] == _user_msg:
                agent.messages.pop()
            response = await agent.process_turn(prompt)
            yield response

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def save_session(self, session_id: str) -> None:
        """Persist the current conversation to disk.

        Args:
            session_id: Unique session identifier.
        """
        agent = self._ensure_agent()
        manager = self._ensure_session_manager()
        manager.save(session_id, agent.messages)

    def resume_session(self, session_id: str) -> None:
        """Restore a previously saved session from disk.

        Args:
            session_id: Unique session identifier.

        Raises:
            FileNotFoundError: If the session does not exist.
        """
        manager = self._ensure_session_manager()
        messages = manager.load(session_id)
        agent = self._ensure_agent()
        agent.messages = messages

    def list_sessions(self) -> list[dict[str, Any]]:
        """List all saved sessions for this agent.

        Returns:
            List of session metadata dicts.
        """
        manager = self._ensure_session_manager()
        return manager.list_sessions()

    # ------------------------------------------------------------------
    # Provider switching
    # ------------------------------------------------------------------

    def switch_provider(self, provider_name: str) -> None:
        """Switch the active LLM provider at runtime.

        Args:
            provider_name: Name of the provider to switch to.

        Raises:
            ValueError: If the provider is not configured.
        """
        pm = self._ensure_provider_manager()
        pm.select_provider(provider_name)

        # Update the model on the agent if already initialized
        new_model = pm.get_model()
        self.model = new_model
        if self._agent is not None:
            self._agent.model = new_model

    def get_current_provider(self) -> dict[str, Any]:
        """Return the currently active provider configuration.

        Returns:
            Dict with name, model, api_key_env keys.
        """
        pm = self._ensure_provider_manager()
        return pm.current_provider()

    def list_providers(self) -> list[str]:
        """Return all configured provider names.

        Returns:
            List of provider name strings.
        """
        pm = self._ensure_provider_manager()
        return pm.list_providers()
