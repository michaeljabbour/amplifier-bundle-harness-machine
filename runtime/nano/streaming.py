"""Streaming response handler for nano runtime.

Provides StreamHandler class with Rich Console live output using litellm
streaming completions. Falls back gracefully to non-streaming for providers
that don't support it.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# StreamHandler
# ---------------------------------------------------------------------------


class StreamHandler:
    """Rich-backed streaming completion handler using litellm.acompletion.

    Streams LLM responses token-by-token using litellm's async streaming API,
    accumulating content and tool_calls with index tracking.

    Falls back to non-streaming (stream=False) for providers that don't
    support streaming, returning a response in the same shape.

    Usage::

        handler = StreamHandler(model="anthropic/claude-sonnet-4-20250514")
        response = await handler.stream_completion(messages, tools=TOOL_SCHEMAS)
    """

    def __init__(
        self,
        model: str = "anthropic/claude-sonnet-4-20250514",
        api_key: str | None = None,
        console: Any | None = None,
    ) -> None:
        """Initialise the StreamHandler.

        Args:
            model: litellm model string (e.g. "anthropic/claude-sonnet-4-20250514").
            api_key: Optional API key override.
            console: Optional Rich Console instance for live output.
        """
        self.model = model
        self.api_key = api_key
        self._console = console

    async def stream_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Stream a completion and return the full assembled response.

        Attempts streaming first; falls back to non-streaming if the provider
        raises an error or doesn't support streaming.

        Args:
            messages: Conversation messages list.
            tools: Optional OpenAI-compatible tool schemas.

        Returns:
            Response dict with keys: ``role``, ``content``, ``tool_calls``.
        """
        try:
            return await self._stream(messages, tools=tools)
        except Exception:
            return await self._non_stream_fallback(messages, tools=tools)

    async def _stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Internal streaming implementation using litellm.acompletion with stream=True.

        Processes async chunks/deltas, accumulating content and tool_calls
        with index tracking.

        Args:
            messages: Conversation messages list.
            tools: Optional tool schemas.

        Returns:
            Assembled response dict.
        """
        import litellm  # lazy import — absent in tests that mock

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools
        if self.api_key:
            kwargs["api_key"] = self.api_key

        # Accumulate streaming content and tool_calls
        accumulated_content = ""
        # tool_calls indexed by index
        tool_calls_by_index: dict[int, dict[str, Any]] = {}

        response_stream = await litellm.acompletion(**kwargs)  # type: ignore[misc]

        async for chunk in response_stream:  # type: ignore[union-attr]
            choice = chunk.choices[0] if chunk.choices else None  # type: ignore[index]
            if choice is None:
                continue

            delta = choice.delta  # type: ignore[union-attr]

            # Accumulate text content
            if delta.content:
                accumulated_content += delta.content
                # Live output to console if available
                if self._console is not None:
                    self._console.print(delta.content, end="")

            # Accumulate tool_calls with index tracking
            if delta.tool_calls:  # type: ignore[union-attr]
                for tc_delta in delta.tool_calls:  # type: ignore[union-attr]
                    idx = tc_delta.index if hasattr(tc_delta, "index") else 0
                    if idx not in tool_calls_by_index:
                        tool_calls_by_index[idx] = {
                            "id": "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }
                    tc = tool_calls_by_index[idx]
                    if tc_delta.id:
                        tc["id"] += tc_delta.id
                    if tc_delta.type:
                        tc["type"] = tc_delta.type
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tc["function"]["name"] += tc_delta.function.name
                        if tc_delta.function.arguments:
                            tc["function"]["arguments"] += tc_delta.function.arguments

        # Build final tool_calls list (sorted by index)
        tool_calls = (
            [tool_calls_by_index[i] for i in sorted(tool_calls_by_index)]
            if tool_calls_by_index
            else None
        )

        return {
            "role": "assistant",
            "content": accumulated_content or None,
            "tool_calls": tool_calls,
        }

    async def _non_stream_fallback(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Non-streaming fallback for providers that don't support streaming.

        Uses stream=False and returns a response in the same shape as streaming.

        Args:
            messages: Conversation messages list.
            tools: Optional tool schemas.

        Returns:
            Response dict matching the streaming response shape.
        """
        import litellm  # lazy import

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            kwargs["tools"] = tools
        if self.api_key:
            kwargs["api_key"] = self.api_key

        response = await litellm.acompletion(**kwargs)  # type: ignore[misc]
        choice = response.choices[0].message  # type: ignore[union-attr]

        return {
            "role": "assistant",
            "content": choice.content,
            "tool_calls": (
                [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.tool_calls
                ]
                if choice.tool_calls
                else None
            ),
        }
