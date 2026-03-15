"""Micro async agent loop.

Extends nano's NanoAgent with micro-tier features:
  - ModeManager: work/review/plan mode system with tool restrictions and overlays
  - RecipeRunner: YAML-driven multi-step workflow execution with approval gates
  - Delegator: isolated PicoAgent sub-agent delegation with clean context
  - ApprovalGate: always/dangerous/never approval for sensitive operations
  - PluginLoader: dynamic .py plugin discovery and loading via importlib

Also includes all nano-tier features:
  - StreamHandler: streaming completions via litellm streaming API
  - SessionManager: JSON-backed session persistence in .sessions/
  - ContextLoader: @mention file reference resolution for dynamic context
  - ProviderManager: multi-provider configuration and runtime switching

Uses litellm.acompletion for LLM calls with optional streaming.
Enforces a constraint gate on every tool call with configurable retries
and a hard MAX_ITERATIONS cap to prevent infinite loops.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from micro.gate import ConstraintGate, ConstraintViolation
from micro.tools import LocalToolExecutor, _TOOL_METHOD_MAP

# Nano-tier extensions (inherited)
from micro.context import ContextLoader
from micro.providers import ProviderManager
from micro.session import SessionManager
from micro.streaming import StreamHandler

# Micro-specific extensions
from micro.approval import ApprovalGate
from micro.delegate import Delegator
from micro.loader import PluginLoader
from micro.modes import ModeManager
from micro.recipes import RecipeRunner

# ---------------------------------------------------------------------------
# Hard iteration cap
# ---------------------------------------------------------------------------

MAX_ITERATIONS: int = 50

# ---------------------------------------------------------------------------
# OpenAI-compatible tool schemas for all 7 tools
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
# NanoAgent
# ---------------------------------------------------------------------------


class NanoAgent:
    """Async constrained agent loop backed by litellm.acompletion.

    Extends pico's PicoAgent with nano-tier features:
    - StreamHandler for streaming LLM responses
    - SessionManager for JSON-backed session persistence
    - ContextLoader for @mention dynamic context loading
    - ProviderManager for multi-provider configuration and switching

    Flow per turn:
    1. Resolve @mention context from user message → inject as system messages.
    2. Append user message to *messages* history.
    3. Call LLM with TOOL_SCHEMAS (streaming or non-streaming).
    4. If LLM returns text → done, return text, persist session.
    5. If LLM returns tool_calls:
       a. Check each call via constraint gate.
       b. If denied → add rejection to history, retry (up to *max_retries*).
       c. If approved → dispatch to LocalToolExecutor, append result, loop.
    6. Hard cap: MAX_ITERATIONS prevents infinite loops.
    """

    def __init__(
        self,
        gate: ConstraintGate,
        executor: LocalToolExecutor,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
        project_root: str | None = None,
        config: dict[str, Any] | None = None,
        streaming: bool = True,
        session_id: str | None = None,
        harness_name: str = "nano",
    ) -> None:
        self.gate = gate
        self.executor = executor
        self.model = model
        self.max_retries = max_retries
        self.streaming = streaming

        # Nano extensions
        resolved_root = project_root or "."
        cfg = config or {}

        self._context_loader = ContextLoader(resolved_root)
        self._provider_manager = ProviderManager({**cfg, "model": model})
        self._session_manager = SessionManager(
            harness_name=harness_name,
            sessions_dir=".sessions",
        )
        self._stream_handler = StreamHandler(model=self._provider_manager.get_model())
        self._session_id = session_id or str(uuid.uuid4())[:8]

        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def resume_session(self, session_id: str) -> None:
        """Resume a previously saved session by loading its messages.

        Args:
            session_id: Session ID to resume.

        Raises:
            FileNotFoundError: If the session does not exist.
        """
        loaded = self._session_manager.load(session_id)
        self._session_id = session_id
        # Preserve the system message (first message) and restore history
        if self.messages and self.messages[0]["role"] == "system":
            self.messages = [self.messages[0]] + loaded
        else:
            self.messages = loaded

    def _save_session(self) -> None:
        """Persist the current messages (excluding system prompt) to disk."""
        # Exclude the system message from persistence
        to_save = [m for m in self.messages if m.get("role") != "system"]
        self._session_manager.save(self._session_id, to_save)

    # ------------------------------------------------------------------
    # Provider management
    # ------------------------------------------------------------------

    def get_current_provider(self) -> str:
        """Return the name of the current provider."""
        return self._provider_manager.current_provider()["name"]

    def switch_provider(self, name: str) -> None:
        """Switch to a different provider by name.

        Args:
            name: Provider name to activate.

        Raises:
            ValueError: If no provider with that name is configured.
        """
        self._provider_manager.select_provider(name)
        # Update stream handler model
        self._stream_handler = StreamHandler(
            model=self._provider_manager.get_model(),
            api_key=self._provider_manager.get_api_key(),
        )

    # ------------------------------------------------------------------
    # LLM calls
    # ------------------------------------------------------------------

    async def _call_llm(self) -> dict[str, Any]:
        """Send current *messages* to the LLM and return the response dict.

        Uses streaming if enabled; falls back to non-streaming automatically.
        """
        if self.streaming:
            return await self._stream_handler.stream_completion(
                self.messages,
                tools=TOOL_SCHEMAS,
            )

        # Non-streaming path (same as pico)
        import litellm  # lazy import — absent in tests that mock

        response = await litellm.acompletion(  # type: ignore[misc]
            model=self._provider_manager.get_model(),
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

        Resolves @mention context references, appends to history, runs the
        constraint-gated agent loop, and persists the session on completion.

        Args:
            user_input: The user's message.

        Returns:
            The agent's final text response for this turn.
        """
        # Resolve @mention context references → inject as system messages
        context_messages = self._context_loader.resolve_mentions(user_input)
        for ctx_msg in context_messages:
            self.messages.append(ctx_msg)

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
                self._save_session()
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
                        self._save_session()
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
        self._save_session()
        return cap_msg


# ---------------------------------------------------------------------------
# Convenience: run a single turn synchronously (useful for scripts)
# ---------------------------------------------------------------------------


def run_turn(agent: NanoAgent, user_input: str) -> str:
    """Run one agent turn synchronously (wraps asyncio.run)."""
    return asyncio.run(agent.process_turn(user_input))


# ---------------------------------------------------------------------------
# MicroAgent — extends NanoAgent with micro-tier features
# ---------------------------------------------------------------------------


class MicroAgent(NanoAgent):
    """Async constrained agent loop with micro-tier extensions.

    Extends NanoAgent with all micro-tier capabilities:
    - ModeManager: work/review/plan modes with tool restrictions + overlays
    - RecipeRunner: YAML-driven multi-step workflow execution
    - Delegator: spawn isolated sub-agents with clean context per delegation
    - ApprovalGate: always/dangerous/never approval for sensitive tool calls
    - PluginLoader: dynamic plugin discovery via importlib

    All NanoAgent capabilities are preserved:
    - StreamHandler for streaming LLM responses
    - SessionManager for JSON-backed session persistence
    - ContextLoader for @mention dynamic context loading
    - ProviderManager for multi-provider configuration and switching
    """

    def __init__(
        self,
        gate: ConstraintGate,
        executor: LocalToolExecutor,
        system_prompt: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_retries: int = 3,
        project_root: str | None = None,
        config: dict[str, Any] | None = None,
        streaming: bool = True,
        session_id: str | None = None,
        approval_mode: str = "dangerous",
        plugins_dir: str = "plugins",
        harness_name: str = "micro",
    ) -> None:
        # Initialise base NanoAgent
        super().__init__(
            gate=gate,
            executor=executor,
            system_prompt=system_prompt,
            model=model,
            max_retries=max_retries,
            project_root=project_root,
            config=config,
            streaming=streaming,
            session_id=session_id,
            harness_name=harness_name,
        )

        # Micro-tier extensions
        cfg = config or {}
        self._mode_manager = ModeManager(cfg)
        self._approval_gate = ApprovalGate(mode=approval_mode)
        self._recipe_runner = RecipeRunner(agent=self)
        self._plugin_loader = PluginLoader(plugins_dir=plugins_dir)
        self._delegator = Delegator(
            sandbox_path=project_root or ".",
            model=model,
            system_prompt=system_prompt,
        )

    # ------------------------------------------------------------------
    # Mode management
    # ------------------------------------------------------------------

    def set_mode(self, mode_name: str) -> None:
        """Switch the agent to a named mode (work/review/plan).

        Args:
            mode_name: Mode to activate.
        """
        self._mode_manager.set_mode(mode_name)

    def get_current_mode(self) -> str:
        """Return the name of the current mode."""
        return self._mode_manager.current_mode

    # ------------------------------------------------------------------
    # Recipe execution
    # ------------------------------------------------------------------

    def run_recipe(self, recipe_path: str) -> list[dict[str, Any]]:
        """Execute a YAML recipe file.

        Args:
            recipe_path: Path to the recipe YAML.

        Returns:
            List of step result dicts.
        """
        return self._recipe_runner.execute(recipe_path)

    # ------------------------------------------------------------------
    # Delegation
    # ------------------------------------------------------------------

    def delegate(
        self,
        task: str,
        tool_names: list[str] | None = None,
    ) -> str:
        """Delegate a task to an isolated sub-agent.

        Args:
            task: Task description for the sub-agent.
            tool_names: Optional restricted tool set.

        Returns:
            Sub-agent response string.
        """
        return self._delegator.spawn(task, tool_names=tool_names)
