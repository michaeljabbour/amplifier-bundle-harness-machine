"""Pico async agent loop.

Uses litellm.acompletion for LLM calls (single provider, no frills).
Enforces a constraint gate on every tool call with configurable retries
and a hard MAX_ITERATIONS cap to prevent infinite loops.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pico.gate import ConstraintGate, ConstraintViolation
from pico.tools import LocalToolExecutor, _TOOL_METHOD_MAP

# ---------------------------------------------------------------------------
# Hard iteration cap
# ---------------------------------------------------------------------------

MAX_ITERATIONS: int = 50

# ---------------------------------------------------------------------------
# OpenAI-compatible tool schemas for all 7 tools
#
# NOTE: TOOL_SCHEMAS is intentionally defined inline in each tier (pico/nano/micro)
# rather than imported from a shared location. Each tier's runtime.py is a
# self-contained template that gets COPIED to the generated harness output
# directory — the three tiers are never co-installed in the same Python package.
# At generation time, only one tier's files are written to the output directory,
# so cross-tier imports would be dead references. The duplication is load-bearing
# by design. Do not extract to a shared module without restructuring the
# generation stamping system.
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file's contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file, creating parent directories as needed",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace a string in a file (first occurrence)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "old_string": {"type": "string", "description": "String to find"},
                    "new_string": {
                        "type": "string",
                        "description": "Replacement string",
                    },
                },
                "required": ["file_path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_patch",
            "description": "Apply a unified diff patch to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to patch"},
                    "patch": {
                        "type": "string",
                        "description": "Unified diff patch string",
                    },
                },
                "required": ["file_path", "patch"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a bash command in the project root",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default 30)",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for a regex pattern in files (uses ripgrep with fallback)",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern"},
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search",
                    },
                },
                "required": ["pattern", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Find files matching a glob pattern",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., **/*.py)",
                    },
                    "path": {"type": "string", "description": "Base directory"},
                },
                "required": ["pattern", "path"],
            },
        },
    },
]

# Alias for backwards-compatibility / external consumers
TOOL_DEFINITIONS = TOOL_SCHEMAS


# ---------------------------------------------------------------------------
# PicoAgent
# ---------------------------------------------------------------------------


class PicoAgent:
    """Async constrained agent loop backed by litellm.acompletion.

    Flow per turn:
    1. Append user message to *messages* history.
    2. Call LLM with TOOL_SCHEMAS.
    3. If LLM returns text → done, return text.
    4. If LLM returns tool_calls:
       a. Check each call via constraint gate.
       b. If denied → add rejection to history, retry (up to *max_retries*).
       c. If approved → dispatch to LocalToolExecutor, append result, loop.
    5. Hard cap: MAX_ITERATIONS prevents infinite loops.
    """

    def __init__(
        self,
        gate: ConstraintGate,
        executor: LocalToolExecutor,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
    ) -> None:
        self.gate = gate
        self.executor = executor
        self.model = model
        self.max_retries = max_retries
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    async def _call_llm(self) -> dict[str, Any]:
        """Send current *messages* to the LLM and return the response dict."""
        import litellm  # lazy import — absent in tests that mock

        response = await litellm.acompletion(  # type: ignore[misc]
            model=self.model,
            messages=self.messages,
            tools=TOOL_SCHEMAS,
        )
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

    def _dispatch_tool(self, tool_name: str, parameters: dict[str, Any]) -> str:
        """Execute a tool call via LocalToolExecutor.

        Args:
            tool_name: Name of the tool.
            parameters: Tool parameters dict.

        Returns:
            Tool result as a string.
        """
        method_name = _TOOL_METHOD_MAP.get(tool_name)
        if method_name is None:
            return f"Unknown tool: {tool_name}"

        method = getattr(self.executor, method_name, None)
        if method is None:
            return f"Tool method not found: {method_name}"

        try:
            return str(method(**parameters))
        except ConstraintViolation as exc:
            return f"CONSTRAINT VIOLATION: {exc.reason}"
        except Exception as exc:
            return f"Tool error: {exc}"

    async def process_turn(self, user_input: str) -> str:
        """Process one user turn through the async agent loop.

        Args:
            user_input: The user's message.

        Returns:
            The agent's final text response for this turn.
        """
        self.messages.append({"role": "user", "content": user_input})

        retries = 0
        denial_count = 0
        iterations = 0

        while iterations < MAX_ITERATIONS:
            iterations += 1
            response = await self._call_llm()

            # Pure text response — done
            if not response.get("tool_calls"):
                text = response.get("content") or ""
                self.messages.append({"role": "assistant", "content": text})
                return text

            # Process tool calls
            tool_calls = response["tool_calls"]
            all_legal = True

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]

                # Parse arguments
                raw_args = tool_call["function"]["arguments"]
                try:
                    arguments = (
                        json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    )
                except (json.JSONDecodeError, TypeError):
                    arguments = {}

                # Gate check
                is_legal, reason = self.gate.check(tool_name, arguments)

                if not is_legal:
                    all_legal = False
                    denial_count += 1
                    retries += 1

                    if retries > self.max_retries:
                        exhaustion_msg = (
                            f"Max retries ({self.max_retries}) exhausted after "
                            f"{denial_count} denial(s). "
                            f"Could not find a legal approach. Last rejection: {reason}"
                        )
                        self.messages.append(
                            {"role": "assistant", "content": exhaustion_msg}
                        )
                        return exhaustion_msg

                    # Inform agent of denial so it self-corrects
                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call],
                        }
                    )
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": (
                                f"REJECTED by constraint gate: {reason}\n"
                                "Please try a different approach."
                            ),
                        }
                    )
                    break  # re-prompt after first denial

            if not all_legal:
                continue  # re-prompt with denial in history

            # All tool calls are legal — dispatch each
            self.messages.append(
                {
                    "role": "assistant",
                    "content": response.get("content"),
                    "tool_calls": tool_calls,
                }
            )

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                raw_args = tool_call["function"]["arguments"]
                try:
                    arguments = (
                        json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    )
                except (json.JSONDecodeError, TypeError):
                    arguments = {}

                result = self._dispatch_tool(tool_name, arguments)
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    }
                )

            retries = 0  # reset retry counter after successful dispatch

        # Hard cap reached
        cap_msg = f"Hard iteration cap ({MAX_ITERATIONS}) reached. Stopping."
        self.messages.append({"role": "assistant", "content": cap_msg})
        return cap_msg


# ---------------------------------------------------------------------------
# Convenience: run a single turn synchronously (useful for scripts)
# ---------------------------------------------------------------------------


def run_turn(agent: PicoAgent, user_input: str) -> str:
    """Run one agent turn synchronously (wraps asyncio.run)."""
    return asyncio.run(agent.process_turn(user_input))
