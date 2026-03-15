"""Pico hybrid entry point (deployment mode: hybrid / event-driven daemon).

Event-driven daemon for running a pico-tier agent as a long-running service.
Reads events from a configurable EventSource, processes each event through
the agent loop, and emits JSON results to stdout.

Supports graceful shutdown on SIGTERM / SIGINT.

Exports:
  - Event: dataclass for incoming events
  - EventSource: abstract base class with listen() -> AsyncIterator[Event]
  - StdinSource: reads JSON events from stdin (one per line)
  - WebhookSource: listens for HTTP POST events
  - PicoService: main service class with event processing loop

Usage::

    import asyncio
    from pico.service import PicoService, StdinSource

    service = PicoService(config_path="config.yaml")
    asyncio.run(service.start())
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator


# ---------------------------------------------------------------------------
# Event dataclass
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """Represents an incoming event for the service to process.

    Attributes:
        prompt: The user prompt / task description.
        metadata: Optional metadata dict (e.g., session_id, source).
        event_id: Optional event identifier for tracing.
    """

    prompt: str
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = ""


# ---------------------------------------------------------------------------
# EventSource ABC
# ---------------------------------------------------------------------------


class EventSource(ABC):
    """Abstract base class for event sources.

    Subclasses implement listen() as an async generator that yields Event
    instances until the source is exhausted or the service is stopped.

    Usage::

        class MySource(EventSource):
            async def listen(self) -> AsyncIterator[Event]:
                while True:
                    event = await get_next_event()
                    yield event
    """

    @abstractmethod
    async def listen(self) -> AsyncIterator[Event]:
        """Yield events from this source.

        Yields:
            Event instances to process.
        """
        # This is an abstract async generator — subclasses must implement
        raise NotImplementedError
        # Required for type checking to accept this as AsyncIterator
        yield  # type: ignore[misc]  # noqa: unreachable


# ---------------------------------------------------------------------------
# StdinSource — JSON events from stdin
# ---------------------------------------------------------------------------


class StdinSource(EventSource):
    """Event source that reads JSON events from stdin, one per line.

    Each line must be a JSON object with at minimum a ``prompt`` field.
    Additional fields are passed through as ``metadata``.

    Example input line::

        {"prompt": "List all Python files", "session_id": "abc123"}
    """

    async def listen(self) -> AsyncIterator[Event]:
        """Yield events by reading JSON lines from stdin.

        Yields:
            Event instances parsed from each stdin line.
        """
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        async for line_bytes in reader:
            line = line_bytes.decode("utf-8").strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                _emit_error(f"Invalid JSON input: {exc}", line=line)
                continue

            prompt = data.pop("prompt", "")
            event_id = data.pop("event_id", "")
            yield Event(prompt=prompt, metadata=data, event_id=event_id)


# ---------------------------------------------------------------------------
# WebhookSource — HTTP POST events
# ---------------------------------------------------------------------------


class WebhookSource(EventSource):
    """Event source that listens for HTTP POST requests.

    Starts a minimal HTTP server on the configured host/port. Each POST
    to ``/event`` with a JSON body containing a ``prompt`` field yields
    an Event.

    Args:
        host: Host to bind (default: "0.0.0.0").
        port: Port to listen on (default: 8080).
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Initialize the WebhookSource.

        Args:
            host: Bind host.
            port: Bind port.
        """
        self.host = host
        self.port = port
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._server: Any = None

    async def listen(self) -> AsyncIterator[Event]:
        """Start the HTTP server and yield incoming events.

        Yields:
            Event instances from incoming HTTP POST requests.
        """
        await self._start_server()
        try:
            while True:
                event = await self._queue.get()
                yield event
        finally:
            if self._server is not None:
                self._server.close()
                await self._server.wait_closed()

    async def _start_server(self) -> None:
        """Start the HTTP server in the background."""
        self._server = await asyncio.start_server(
            self._handle_request, self.host, self.port
        )

    async def _handle_request(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle one HTTP request, enqueue event if valid POST.

        Args:
            reader: Asyncio stream reader.
            writer: Asyncio stream writer.
        """
        try:
            request_data = await reader.read(65536)
            request_text = request_data.decode("utf-8", errors="replace")

            # Parse minimal HTTP request
            lines = request_text.split("\r\n")
            if not lines:
                writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                await writer.drain()
                writer.close()
                return

            request_line = lines[0]
            method = request_line.split(" ")[0] if " " in request_line else ""

            if method != "POST":
                writer.write(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
                await writer.drain()
                writer.close()
                return

            # Find body (after double CRLF)
            body_start = request_text.find("\r\n\r\n")
            if body_start == -1:
                writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                await writer.drain()
                writer.close()
                return

            body = request_text[body_start + 4 :]
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\nInvalid JSON")
                await writer.drain()
                writer.close()
                return

            prompt = data.pop("prompt", "")
            event_id = data.pop("event_id", "")
            event = Event(prompt=prompt, metadata=data, event_id=event_id)
            await self._queue.put(event)

            writer.write(
                b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"status":"queued"}'
            )
            await writer.drain()
        finally:
            writer.close()


# ---------------------------------------------------------------------------
# PicoService — main service class
# ---------------------------------------------------------------------------


class PicoService:
    """Event-driven daemon wrapping a pico-tier agent.

    Reads events from an EventSource, processes each through the agent loop,
    and emits JSON results to stdout. Handles SIGTERM/SIGINT for graceful
    shutdown.

    Usage::

        service = PicoService(config_path="config.yaml")
        asyncio.run(service.start())
    """

    def __init__(
        self,
        config_path: str | None = None,
        config: dict[str, Any] | None = None,
        source: EventSource | None = None,
    ) -> None:
        """Initialize PicoService.

        Args:
            config_path: Path to YAML config file.
            config: Config dict (takes precedence over config_path).
            source: EventSource to read from (default: StdinSource).
        """
        self._config = config or {}
        if config_path and not self._config:
            self._config = self._load_config(config_path)

        self._source = source or StdinSource()
        self._stopping = False
        self._agent: Any = None

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load YAML config from disk.

        Args:
            config_path: Path to the YAML config file.

        Returns:
            Parsed config dict, or empty dict if loading fails.
        """
        if not os.path.isfile(config_path):
            return {}
        try:
            import yaml  # type: ignore[import-untyped]  # noqa: PLC0415

            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        except Exception as exc:
            _emit_error(f"Failed to load config from {config_path}: {exc}")
            return {}

    # ------------------------------------------------------------------
    # Agent initialization
    # ------------------------------------------------------------------

    def _build_agent(self) -> Any:
        """Build the pico agent from config.

        Returns:
            Configured PicoAgent instance, or None if config is incomplete.
        """
        from pico.api import PicoAgent  # noqa: PLC0415

        constraints_path = self._config.get("constraints_path", "constraints.py")
        project_root = self._config.get("project_root", os.getcwd())
        system_prompt = self._config.get(
            "system_prompt", "You are a helpful constrained agent."
        )
        model = self._config.get("model", "anthropic/claude-sonnet-4-20250514")

        return PicoAgent(
            constraints_path=constraints_path,
            project_root=project_root,
            system_prompt=system_prompt,
            model=model,
        )

    # ------------------------------------------------------------------
    # Signal handling
    # ------------------------------------------------------------------

    def _setup_signal_handlers(self) -> None:
        """Register SIGTERM / SIGINT handlers for graceful shutdown."""
        loop = asyncio.get_running_loop()

        def _handle_signal(sig: int) -> None:
            sig_name = signal.Signals(sig).name
            _emit_info(f"Received {sig_name} — initiating graceful shutdown")
            self._stopping = True

        loop.add_signal_handler(signal.SIGTERM, _handle_signal, signal.SIGTERM)
        loop.add_signal_handler(signal.SIGINT, _handle_signal, signal.SIGINT)

    # ------------------------------------------------------------------
    # Event processing
    # ------------------------------------------------------------------

    async def _process_event(self, event: Event) -> dict[str, Any]:
        """Process one event through the agent loop.

        Args:
            event: Incoming event to process.

        Returns:
            Result dict with event_id, prompt, result, and status keys.
        """
        result: dict[str, Any] = {
            "event_id": event.event_id,
            "prompt": event.prompt,
            "status": "ok",
            "result": "",
        }
        try:
            if self._agent is None:
                self._agent = self._build_agent()
            response = await self._agent.run(event.prompt)
            result["result"] = response
        except Exception as exc:
            result["status"] = "error"
            result["error"] = str(exc)
        return result

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def start(self, _service_name: str = "PicoService") -> None:
        """Start the event processing loop.

        Reads events from the source, processes each, and emits JSON
        results to stdout. Stops cleanly on SIGTERM / SIGINT.

        Args:
            _service_name: Display name used in startup/shutdown log lines.
                Subclasses pass their own name so log messages identify the
                correct tier without duplicating the loop implementation.
        """
        self._setup_signal_handlers()
        _emit_info(f"{_service_name} starting")

        async for event in self._source.listen():
            if self._stopping:
                break

            result = await self._process_event(event)
            _emit_result(result)

            if self._stopping:
                break

        _emit_info(f"{_service_name} stopped")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _emit_result(data: dict[str, Any]) -> None:
    """Emit a JSON result to stdout.

    Args:
        data: Result dict to emit.
    """
    print(json.dumps(data), flush=True)


def _emit_info(message: str) -> None:
    """Emit an info log message to stderr.

    Args:
        message: Info message string.
    """
    print(
        json.dumps({"level": "info", "message": message}), file=sys.stderr, flush=True
    )


def _emit_error(message: str, **extra: Any) -> None:
    """Emit an error log message to stderr.

    Args:
        message: Error message string.
        **extra: Additional fields to include in the log.
    """
    payload: dict[str, Any] = {"level": "error", "message": message}
    payload.update(extra)
    print(json.dumps(payload), file=sys.stderr, flush=True)
