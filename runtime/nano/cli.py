"""CLI entry point for nano standalone constrained-agent.

Nano tier adds streaming responses, session persistence, dynamic context
loading, and multi-provider support on top of the pico foundation.

Subcommands:
    chat   — Interactive constrained agent session (with Rich rendering,
             streaming output, session persistence, @mention context)
    check  — One-shot constraint validation
    audit  — Dry-run LLM validation against a transcript

Additional chat flags:
    --resume SESSION_ID   Resume a saved session by ID
    --no-stream           Disable streaming responses (use blocking completion)

REPL commands (during chat):
    /provider [NAME]      Show current provider or switch to NAME
    exit / quit           Exit the session
    Ctrl-C                Cancel current response
    Ctrl-D                Exit cleanly

Usage::

    nano-amplifier chat
    nano-amplifier chat --resume abc123
    nano-amplifier chat --no-stream
    nano-amplifier check bash '{"command": "rm -rf /"}'
    nano-amplifier audit transcript.json

KeyboardInterrupt during a response shows "Cancelled." and returns to prompt.
EOFError (Ctrl-D at prompt) prints "Goodbye." and exits cleanly.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys


# ---------------------------------------------------------------------------
# Rich imports (graceful degradation if not installed)
# ---------------------------------------------------------------------------

try:
    from rich.console import Console
    from rich.markdown import Markdown

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False  # type: ignore[assignment]
    Console = None  # type: ignore[misc, assignment]
    Markdown = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Config defaults
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: dict[str, object] = {
    "project_root": os.getcwd(),
    "model": "anthropic/claude-sonnet-4-20250514",
    "harness_type": "action-verifier",
    "max_retries": 3,
    "constraints_path": "constraints.py",
    "streaming": True,
}

DEFAULT_SYSTEM_PROMPT = (
    "You are a constrained agent. When a tool call is rejected, "
    "read the rejection reason and try a different approach. "
    "Do not repeat rejected actions."
)

# ---------------------------------------------------------------------------
# Config + prompt loading
# ---------------------------------------------------------------------------


def load_config(config_path: str) -> dict:
    """Load config from config.yaml; falls back to DEFAULT_CONFIG for missing keys."""
    config = dict(DEFAULT_CONFIG)
    try:
        import yaml  # type: ignore[import-untyped]

        with open(config_path) as f:
            user_config = yaml.safe_load(f.read())
        if isinstance(user_config, dict):
            config.update(user_config)
    except FileNotFoundError:
        pass
    except ImportError:
        print("Warning: pyyaml not installed, using default config", file=sys.stderr)
    return config


def load_system_prompt(prompt_path: str) -> str:
    """Load system prompt from system-prompt.md; returns DEFAULT_SYSTEM_PROMPT if missing."""
    try:
        with open(prompt_path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return DEFAULT_SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Nano standalone constrained agent",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "--system-prompt",
        default="system-prompt.md",
        help="Path to system-prompt.md (default: system-prompt.md)",
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # chat
    chat_parser = subparsers.add_parser(
        "chat",
        help="Interactive constrained agent session with streaming and session persistence",
    )
    chat_parser.add_argument(
        "--resume",
        metavar="SESSION_ID",
        default=None,
        help="Resume a previously saved session by ID",
    )
    chat_parser.add_argument(
        "--no-stream",
        action="store_true",
        default=False,
        help="Disable streaming responses (use blocking completion instead)",
    )

    # check
    check_parser = subparsers.add_parser("check", help="One-shot constraint validation")
    check_parser.add_argument("tool_name", help="Tool name (e.g., bash, read_file)")
    check_parser.add_argument("params_json", help="Tool parameters as JSON string")

    # audit
    audit_parser = subparsers.add_parser(
        "audit", help="Dry-run LLM validation against a transcript"
    )
    audit_parser.add_argument("transcript_file", help="Path to transcript JSON file")

    return parser


# ---------------------------------------------------------------------------
# Subcommand: check
# ---------------------------------------------------------------------------


def run_check(
    constraints_path: str,
    tool_name: str,
    params_json: str,
) -> tuple[bool, str]:
    """Run a one-shot constraint check and return (is_legal, reason).

    Args:
        constraints_path: Path to constraints.py.
        tool_name: Tool name to check.
        params_json: JSON string of tool parameters.

    Returns:
        ``(True, "")`` for legal actions; ``(False, reason)`` for illegal ones.
    """
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON parameters: {exc}"

    from nano.gate import ConstraintGate

    gate = ConstraintGate(constraints_path)
    return gate.check(tool_name, params)


def cmd_check(constraints_path: str, tool_name: str, params_json: str) -> None:
    """Run a one-shot constraint check and print result."""
    is_legal, reason = run_check(constraints_path, tool_name, params_json)
    if is_legal:
        print(f"LEGAL: {tool_name}")
    else:
        print(f"ILLEGAL: {tool_name} — {reason}")
    sys.exit(0 if is_legal else 1)


# ---------------------------------------------------------------------------
# Subcommand: chat
# ---------------------------------------------------------------------------


def cmd_chat(
    config: dict,
    system_prompt: str,
    resume_session_id: str | None = None,
    streaming: bool = True,
) -> None:
    """Run an interactive nano agent session with Rich rendering.

    Supports:
    - Streaming responses (toggled by ``streaming`` flag)
    - Session persistence (``--resume SESSION_ID``)
    - @mention context loading
    - Multi-provider switching via ``/provider`` REPL command
    """
    from nano.gate import ConstraintGate
    from nano.runtime import NanoAgent
    from nano.tools import LocalToolExecutor

    gate = ConstraintGate(
        constraints_path=str(config["constraints_path"]),
        project_root=str(config["project_root"]),
    )
    executor = LocalToolExecutor(str(config["project_root"]))
    agent = NanoAgent(
        gate=gate,
        executor=executor,
        system_prompt=system_prompt,
        model=str(config["model"]),
        max_retries=int(config["max_retries"]),  # type: ignore[arg-type]
        project_root=str(config["project_root"]),
        config=config,
        streaming=streaming,
    )

    # Resume session if requested
    if resume_session_id:
        try:
            agent.resume_session(resume_session_id)
        except FileNotFoundError:
            print(
                f"Warning: session {resume_session_id!r} not found, starting fresh.",
                file=sys.stderr,
            )

    if _RICH_AVAILABLE:
        console = Console()  # type: ignore[misc]
        console.print(
            f"[bold green]Nano agent ready.[/bold green] "
            f"Project: {config['project_root']}"
        )
        stream_status = "streaming" if streaming else "non-streaming"
        console.print(
            f"Mode: [bold]{stream_status}[/bold]. "
            "Type [bold]/provider[/bold] to switch providers. "
            "Type [bold]exit[/bold] or [bold]Ctrl-C[/bold] to quit.\n"
        )
    else:
        print(f"Nano agent ready. Project: {config['project_root']}")
        print("Type 'exit' or Ctrl-C to quit.\n")
        console = None  # type: ignore[assignment]

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                print("\nGoodbye.")
                return

            if not user_input or user_input.lower() in ("exit", "quit"):
                print("Goodbye.")
                return

            # Handle /provider REPL command
            if user_input.startswith("/provider"):
                parts = user_input.split(None, 1)
                if len(parts) == 1:
                    # Show current provider
                    current = agent.get_current_provider()
                    print(f"Current provider: {current}")
                else:
                    # Switch provider
                    provider_name = parts[1].strip()
                    try:
                        agent.switch_provider(provider_name)
                        print(f"Switched to provider: {provider_name}")
                    except ValueError as exc:
                        print(f"Error: {exc}", file=sys.stderr)
                continue

            try:
                response = asyncio.run(agent.process_turn(user_input))
            except KeyboardInterrupt:
                print("\nCancelled.")
                continue

            if _RICH_AVAILABLE and console is not None:
                console.print("\n[bold]Agent:[/bold]")
                console.print(Markdown(response))  # type: ignore[misc]
                console.print()
            else:
                print(f"\nAgent: {response}\n")

    except KeyboardInterrupt:
        print("\nGoodbye.")


# ---------------------------------------------------------------------------
# Subcommand: audit
# ---------------------------------------------------------------------------


def cmd_audit(config: dict, transcript_path: str) -> None:
    """Dry-run LLM validation against a transcript file."""
    from nano.gate import ConstraintGate

    gate = ConstraintGate(str(config["constraints_path"]))

    try:
        with open(transcript_path) as f:
            transcript = json.load(f)
    except FileNotFoundError:
        print(f"Error: transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in transcript: {exc}", file=sys.stderr)
        sys.exit(1)

    violations = 0
    total = 0

    for entry in transcript:
        if entry.get("tool_calls"):
            for tc in entry["tool_calls"]:
                try:
                    tool_name = tc["function"]["name"]
                    params = json.loads(tc["function"]["arguments"])
                except (KeyError, json.JSONDecodeError) as exc:
                    print(f"Warning: skipping malformed tool_call entry: {exc}")
                    continue
                total += 1
                is_legal, reason = gate.check(tool_name, params)
                if not is_legal:
                    violations += 1
                    print(f"VIOLATION: {tool_name}({params}) — {reason}")

    print(f"\nAudit complete: {violations} violations in {total} tool calls")
    if total > 0:
        print(f"Legal action rate: {(total - violations) / total:.1%}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(args.config)
    system_prompt = load_system_prompt(args.system_prompt)

    if args.subcommand == "chat":
        streaming = not args.no_stream
        cmd_chat(
            config,
            system_prompt,
            resume_session_id=args.resume,
            streaming=streaming,
        )
    elif args.subcommand == "check":
        cmd_check(
            constraints_path=str(config["constraints_path"]),
            tool_name=args.tool_name,
            params_json=args.params_json,
        )
    elif args.subcommand == "audit":
        cmd_audit(config, args.transcript_file)


if __name__ == "__main__":
    main()
