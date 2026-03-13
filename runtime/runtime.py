"""Standalone agent runtime for nano-amplifier constrained agents.

Provides:
- ConstraintGate: loads constraints.py, checks actions before dispatch
- AgentLoop: LLM conversation + constraint gate + tool dispatch + retry

Dependencies: litellm (LLM client), pyyaml (config loading).
For testing, pass llm_fn to AgentLoop to mock the LLM.
"""

from __future__ import annotations

import importlib.util
import json
import os
from typing import Callable

from tools import TOOL_DISPATCH, ToolExecutor


# ---------------------------------------------------------------------------
# Constraint gate
# ---------------------------------------------------------------------------


class ConstraintGate:
    """Loads a constraints.py and checks actions before dispatch.

    Supports both is_legal_action(tool_name, params) and
    validate_action(state, action) signatures with auto-detection.
    """

    def __init__(self, constraints_path: str) -> None:
        path = os.path.abspath(constraints_path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Constraints file not found: {path}")

        spec = importlib.util.spec_from_file_location("_constraints", path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not load constraints module: {path}")
        self._module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self._module)  # type: ignore[union-attr]

        # Auto-detect signature
        if hasattr(self._module, "is_legal_action"):
            self._signature = "is_legal_action"
            self._fn = self._module.is_legal_action
        elif hasattr(self._module, "validate_action"):
            self._signature = "validate_action"
            self._fn = self._module.validate_action
        else:
            raise ValueError(
                "Constraints module exports neither 'is_legal_action' nor 'validate_action'"
            )

    def check(self, tool_name: str | None, parameters: dict | None) -> tuple[bool, str]:
        """Check whether an action is legal.

        Args:
            tool_name: Name of the tool being called.
            parameters: Tool parameters dict.

        Returns:
            (True, "") for legal actions.
            (False, reason) for illegal actions.
        """
        try:
            if not isinstance(tool_name, str):
                raise TypeError(
                    f"tool_name must be a string, got {type(tool_name).__name__}"
                )
            safe_params = parameters if parameters is not None else {}
            if self._signature == "is_legal_action":
                return self._fn(tool_name, safe_params)
            else:
                state = {}
                action = {"tool_name": tool_name, "parameters": safe_params}
                return self._fn(state, action)
        except Exception as exc:
            return False, f"Constraint check error: {exc}"


# ---------------------------------------------------------------------------
# Tool definitions for LLM (OpenAI function calling format)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
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
            "description": "Write content to a file",
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
            "description": "Replace a string in a file",
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
            "name": "bash",
            "description": "Execute a bash command",
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
            "description": "Search for a regex pattern in files",
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


# ---------------------------------------------------------------------------
# Default LLM function (uses litellm)
# ---------------------------------------------------------------------------


def _default_llm_fn(
    messages: list[dict], tools: list | None = None, model: str | None = None
) -> dict:
    """Call the LLM via litellm. Imported lazily to avoid import errors in tests."""
    import litellm  # type: ignore[import-untyped]

    response = litellm.completion(
        model=model or "anthropic/claude-sonnet-4-20250514",
        messages=messages,
        tools=tools,
    )
    choice = response.choices[0].message
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


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------


class AgentLoop:
    """LLM agent loop with constraint gate and tool dispatch.

    Flow per turn:
    1. Add user message to conversation
    2. Send to LLM
    3. If LLM returns text: done, return text
    4. If LLM returns tool call:
       a. Check via constraint gate
       b. If illegal: add rejection to conversation, re-prompt (up to max_retries)
       c. If legal: dispatch to ToolExecutor, add result, re-prompt for next step
    """

    def __init__(
        self,
        constraints_path: str,
        project_root: str,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
        llm_fn: Callable | None = None,
    ) -> None:
        self.gate = ConstraintGate(constraints_path)
        self.executor = ToolExecutor(project_root)
        self.model = model
        self.max_retries = max_retries
        self._llm_fn = llm_fn or _default_llm_fn
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]

    def _call_llm(self) -> dict:
        """Send current conversation to LLM and return response."""
        return self._llm_fn(
            messages=self.messages,
            tools=TOOL_DEFINITIONS,
            model=self.model,
        )

    def _dispatch_tool(self, tool_name: str, parameters: dict) -> str:
        """Execute a tool via the ToolExecutor.

        Args:
            tool_name: Name of the tool.
            parameters: Tool parameters.

        Returns:
            Tool result as a string.
        """
        if tool_name not in TOOL_DISPATCH:
            return f"Unknown tool: {tool_name}"

        method_name, param_map = TOOL_DISPATCH[tool_name]
        method = getattr(self.executor, method_name)

        # Map API parameter names to method parameter names
        kwargs = {}
        for api_name, method_param in param_map.items():
            if api_name in parameters:
                kwargs[method_param] = parameters[api_name]

        try:
            return method(**kwargs)
        except Exception as exc:
            return f"Tool error: {exc}"

    def process_turn(self, user_input: str) -> str:
        """Process one user turn through the agent loop.

        Args:
            user_input: The user's message.

        Returns:
            The agent's final text response for this turn.
        """
        self.messages.append({"role": "user", "content": user_input})

        retries = 0
        while True:
            response = self._call_llm()

            # Text response — done
            if not response.get("tool_calls"):
                text = response.get("content", "")
                self.messages.append({"role": "assistant", "content": text})
                return text

            # Tool call — gate check
            tool_call = response["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            try:
                arguments = (
                    json.loads(tool_call["function"]["arguments"])
                    if isinstance(tool_call["function"]["arguments"], str)
                    else tool_call["function"]["arguments"]
                )
            except (json.JSONDecodeError, TypeError):
                arguments = {}

            is_legal, reason = self.gate.check(tool_name, arguments)

            if not is_legal:
                retries += 1
                if retries > self.max_retries:
                    exhaustion_msg = (
                        f"Max retries ({self.max_retries}) exhausted. "
                        f"Could not find a legal approach. Last rejection: {reason}"
                    )
                    self.messages.append(
                        {"role": "assistant", "content": exhaustion_msg}
                    )
                    return exhaustion_msg

                # Add rejection to conversation for agent self-correction
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": response["tool_calls"],
                    }
                )
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": (
                            f"REJECTED by constraint gate: {reason}\n"
                            f"Please try a different approach."
                        ),
                    }
                )
                continue

            # Legal — dispatch
            result = self._dispatch_tool(tool_name, arguments)

            self.messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": response["tool_calls"],
                }
            )
            self.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(result),
                }
            )
            retries = 0  # Reset retry counter after successful dispatch
