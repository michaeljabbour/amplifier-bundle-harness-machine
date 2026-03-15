"""Nano hybrid entry point (deployment mode: hybrid / event-driven daemon).

Extends pico service with nano-tier features: session persistence and
streaming support in the event processing loop.

Exports:
  - NanoService: extends PicoService with _sessions dict for session
    persistence and streaming support in config

Usage::

    import asyncio
    from nano.service import NanoService
    from pico.service import StdinSource

    service = NanoService(config_path="config.yaml")
    asyncio.run(service.start())
"""

from __future__ import annotations

import os
from typing import Any

from pico.service import (
    Event,
    EventSource,
    PicoService,
    _emit_info,
    _emit_result,
)


# ---------------------------------------------------------------------------
# NanoService — extends PicoService with session persistence and streaming
# ---------------------------------------------------------------------------


class NanoService(PicoService):
    """Event-driven daemon with nano-tier session persistence and streaming.

    Extends PicoService with:
      - ``_sessions``: dict mapping session_id -> NanoAgent for persistence
      - Streaming support: agents can be configured to use streaming responses
      - Session ID routing: events with ``session_id`` metadata reuse agents

    Session IDs are passed via event metadata (``metadata.session_id``).
    If a session_id is provided, the same NanoAgent instance is reused,
    maintaining conversation history across events.

    Usage::

        service = NanoService(config_path="config.yaml")
        asyncio.run(service.start())
    """

    def __init__(
        self,
        config_path: str | None = None,
        config: dict[str, Any] | None = None,
        source: EventSource | None = None,
    ) -> None:
        """Initialize NanoService.

        Args:
            config_path: Path to YAML config file.
            config: Config dict (takes precedence over config_path).
            source: EventSource to read from (default: StdinSource).
        """
        super().__init__(config_path=config_path, config=config, source=source)

        # Session persistence: session_id -> NanoAgent instance
        self._sessions: dict[str, Any] = {}

        # Streaming config flag
        self._streaming_enabled: bool = bool(self._config.get("streaming", False))

    # ------------------------------------------------------------------
    # Agent management with session support
    # ------------------------------------------------------------------

    def _get_or_create_agent(self, session_id: str | None) -> Any:
        """Get an existing NanoAgent by session_id or create a new one.

        Args:
            session_id: Optional session identifier.

        Returns:
            NanoAgent instance (reused if session_id already exists).
        """
        from nano.api import NanoAgent  # noqa: PLC0415

        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        # Build a new agent
        constraints_path = self._config.get("constraints_path", "constraints.py")
        project_root = self._config.get("project_root", os.getcwd())
        system_prompt = self._config.get(
            "system_prompt", "You are a helpful constrained agent."
        )
        model = self._config.get("model", "anthropic/claude-sonnet-4-20250514")
        sessions_dir = self._config.get("sessions_dir", ".sessions")
        harness_name = self._config.get("harness_name", "nano-service")

        agent = NanoAgent(
            constraints_path=constraints_path,
            project_root=project_root,
            system_prompt=system_prompt,
            model=model,
            sessions_dir=sessions_dir,
            harness_name=harness_name,
            config=self._config,
        )

        # Register the session if session_id given
        if session_id:
            self._sessions[session_id] = agent

        return agent

    # ------------------------------------------------------------------
    # Event processing (override to support sessions and streaming)
    # ------------------------------------------------------------------

    async def _process_event(self, event: Event) -> dict[str, Any]:
        """Process one event through the nano agent loop.

        Supports session routing via ``metadata.session_id`` and
        streaming if ``streaming`` is enabled in config.

        Args:
            event: Incoming event to process.

        Returns:
            Result dict with event_id, prompt, result, status, and
            optionally session_id keys.
        """
        session_id = event.metadata.get("session_id") or None

        result: dict[str, Any] = {
            "event_id": event.event_id,
            "prompt": event.prompt,
            "status": "ok",
            "result": "",
        }
        if session_id:
            result["session_id"] = session_id

        try:
            agent = self._get_or_create_agent(session_id)

            if self._streaming_enabled:
                # Stream the response and accumulate
                chunks: list[str] = []
                async for chunk in agent.stream(event.prompt):
                    chunks.append(chunk)
                result["result"] = "".join(chunks)
            else:
                result["result"] = await agent.run(event.prompt)

        except Exception as exc:
            result["status"] = "error"
            result["error"] = str(exc)

        return result

    # ------------------------------------------------------------------
    # Main entry point (override to announce NanoService)
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the nano event processing loop with session support.

        Reads events from the source, routes to session-aware agents,
        and emits JSON results to stdout.
        """
        self._setup_signal_handlers()
        _emit_info(
            f"NanoService starting (streaming={'enabled' if self._streaming_enabled else 'disabled'})"
        )

        async for event in self._source.listen():
            if self._stopping:
                break

            result = await self._process_event(event)
            _emit_result(result)

            if self._stopping:
                break

        _emit_info("NanoService stopped")
