"""Micro hybrid entry point (deployment mode: hybrid / event-driven daemon).

Extends nano service with micro-tier features: mode switching, recipe
triggering, and sub-agent delegation — all controllable via event metadata.

Special event metadata fields:
  - ``mode``: switch agent mode before processing (e.g., "review", "plan")
  - ``recipe``: path to a YAML recipe file to execute instead of a prompt
  - ``delegate``: task string to run via sub-agent delegation

Exports:
  - MicroService: extends NanoService with mode/recipe/delegate handling

Usage::

    import asyncio
    from micro.service import MicroService
    from pico.service import StdinSource

    service = MicroService(config_path="config.yaml")
    asyncio.run(service.start())

Example event with mode switching::

    {"prompt": "Review the auth module", "mode": "review"}

Example event with recipe execution::

    {"prompt": "run workflow", "recipe": "workflows/deploy.yaml"}

Example event with delegation::

    {"prompt": "summarize", "delegate": "Summarize all Python files"}
"""

from __future__ import annotations

import os
from typing import Any

from nano.service import NanoService
from pico.service import Event, EventSource


# ---------------------------------------------------------------------------
# MicroService — extends NanoService with modes, recipes, and delegation
# ---------------------------------------------------------------------------


class MicroService(NanoService):
    """Event-driven daemon with micro-tier mode, recipe, and delegation support.

    Extends NanoService with:
      - Mode switching: ``metadata.mode`` field switches agent mode
      - Recipe execution: ``metadata.recipe`` field triggers YAML workflow
      - Delegation: ``metadata.delegate`` field routes task to sub-agent

    These special metadata fields control routing before prompt processing.
    Multiple fields can be combined (e.g., mode + prompt for mode-restricted
    processing).

    Usage::

        service = MicroService(config_path="config.yaml")
        asyncio.run(service.start())
    """

    def __init__(
        self,
        config_path: str | None = None,
        config: dict[str, Any] | None = None,
        source: EventSource | None = None,
    ) -> None:
        """Initialize MicroService.

        Args:
            config_path: Path to YAML config file.
            config: Config dict (takes precedence over config_path).
            source: EventSource to read from (default: StdinSource).
        """
        super().__init__(config_path=config_path, config=config, source=source)

    # ------------------------------------------------------------------
    # Agent management with MicroAgent
    # ------------------------------------------------------------------

    def _get_or_create_agent(self, session_id: str | None) -> Any:
        """Get an existing MicroAgent by session_id or create a new one.

        Args:
            session_id: Optional session identifier.

        Returns:
            MicroAgent instance (reused if session_id already exists).
        """
        from micro.api import MicroAgent  # noqa: PLC0415

        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        # Build a new MicroAgent
        constraints_path = self._config.get("constraints_path", "constraints.py")
        project_root = self._config.get("project_root", os.getcwd())
        system_prompt = self._config.get(
            "system_prompt", "You are a helpful constrained agent."
        )
        model = self._config.get("model", "anthropic/claude-sonnet-4-20250514")
        sessions_dir = self._config.get("sessions_dir", ".sessions")
        harness_name = self._config.get("harness_name", "micro-service")

        agent = MicroAgent(
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
    # Event processing (override to support mode/recipe/delegate)
    # ------------------------------------------------------------------

    async def _process_event(self, event: Event) -> dict[str, Any]:
        """Process one event with micro-tier routing.

        Handles special metadata fields before prompt processing:
          - ``mode``: switches agent mode
          - ``recipe``: executes a YAML workflow recipe
          - ``delegate``: routes task to a sub-agent

        Args:
            event: Incoming event to process.

        Returns:
            Result dict with event_id, prompt, result, status keys,
            and optionally mode, recipe, delegate routing keys.
        """
        session_id = event.metadata.get("session_id") or None
        mode = event.metadata.get("mode") or None
        recipe = event.metadata.get("recipe") or None
        delegate_task = event.metadata.get("delegate") or None

        result: dict[str, Any] = {
            "event_id": event.event_id,
            "prompt": event.prompt,
            "status": "ok",
            "result": "",
        }
        if session_id:
            result["session_id"] = session_id
        if mode:
            result["mode"] = mode
        if recipe:
            result["recipe"] = recipe
        if delegate_task:
            result["delegate"] = delegate_task

        try:
            agent = self._get_or_create_agent(session_id)

            # 1. Mode switching via event metadata
            if mode:
                try:
                    agent.set_mode(mode)
                except ValueError as exc:
                    result["mode_error"] = str(exc)

            # 2. Recipe execution via event metadata
            if recipe:
                recipe_results = agent.execute_recipe(recipe)
                result["result"] = {
                    "type": "recipe",
                    "steps": recipe_results,
                }
                return result

            # 3. Delegation via event metadata
            if delegate_task:
                delegation_result = agent.delegate(delegate_task)
                result["result"] = {
                    "type": "delegation",
                    "output": delegation_result,
                }
                return result

            # 4. Standard prompt processing (with streaming support)
            if self._streaming_enabled:
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
    # Main entry point (override to announce MicroService)
    # ------------------------------------------------------------------

    async def start(self, _service_name: str = "") -> None:
        """Start the micro event processing loop.

        Delegates to PicoService.start() with the MicroService display name
        so the shared event loop lives in one place.

        Args:
            _service_name: Override display name (default: auto-generated from
                streaming config). Accepts the same parameter as the parent so
                the override is Liskov-compatible.
        """
        if not _service_name:
            _service_name = (
                f"MicroService (streaming="
                f"{'enabled' if self._streaming_enabled else 'disabled'})"
            )
        await super().start(_service_name=_service_name)
