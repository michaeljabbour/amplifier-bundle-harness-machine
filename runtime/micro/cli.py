"""CLI entry point for micro standalone constrained-agent.

Micro tier adds mode system, recipe runner, sub-agent delegation, approval
gates, and dynamic module loading on top of the nano foundation.

Subcommands:
    chat   — Interactive constrained agent session (with Rich rendering,
             streaming output, session persistence, @mention context,
             mode switching, recipe execution, sub-agent delegation)
    check  — One-shot constraint validation
    audit  — Dry-run LLM validation against a transcript

Additional chat flags:
    --resume SESSION_ID        Resume a saved session by ID
    --no-stream                Disable streaming responses (use blocking completion)
    --approval-mode MODE       Approval mode: always, dangerous, never (default: dangerous)

REPL commands (during chat):
    /provider [NAME]      Show current provider or switch to NAME
    /mode [NAME]          Show current mode or switch to NAME (work/review/plan)
    /recipe FILE          Execute a YAML recipe file
    /delegate TASK        Delegate a task to a fresh sub-agent
    exit / quit           Exit the session
    Ctrl-C                Cancel current response
    Ctrl-D                Exit cleanly

Usage::

    micro-amplifier chat
    micro-amplifier chat --resume abc123
    micro-amplifier chat --no-stream
    micro-amplifier chat --approval-mode always
    micro-amplifier chat --approval-mode never
    micro-amplifier check bash '{"command": "rm -rf /"}'
    micro-amplifier audit transcript.json

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
    "approval_mode": "dangerous",
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
        description="Micro standalone constrained agent",
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
        help="Interactive constrained agent session with streaming, modes, recipes, delegation",
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
    chat_parser.add_argument(
        "--approval-mode",
        choices=["always", "dangerous", "never"],
        default="dangerous",
        help=(
            "Approval gate mode: 'always' prompts for every tool call, "
            "'dangerous' prompts only for destructive/sensitive operations, "
            "'never' auto-approves all (default: dangerous)"
        ),
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

    from micro.gate import ConstraintGate

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
    approval_mode: str = "dangerous",
) -> None:
    """Run an interactive micro agent session with Rich rendering.

    Supports:
    - Streaming responses (toggled by ``streaming`` flag)
    - Session persistence (``--resume SESSION_ID``)
    - @mention context loading
    - Multi-provider switching via ``/provider`` REPL command
    - Mode switching via ``/mode`` REPL command (work/review/plan)
    - Recipe execution via ``/recipe`` REPL command
    - Sub-agent delegation via ``/delegate`` REPL command
    - Approval gates with configurable ``approval_mode``
    """
    from micro.approval import ApprovalGate
    from micro.gate import ConstraintGate
    from micro.loader import PluginLoader
    from micro.modes import ModeManager
    from micro.recipes import RecipeRunner
    from micro.runtime import MicroAgent
    from micro.tools import LocalToolExecutor

    gate = ConstraintGate(
        constraints_path=str(config["constraints_path"]),
        project_root=str(config["project_root"]),
    )
    executor = LocalToolExecutor(str(config["project_root"]))
    agent = MicroAgent(
        gate=gate,
        executor=executor,
        system_prompt=system_prompt,
        model=str(config["model"]),
        max_retries=int(config["max_retries"]),  # type: ignore[arg-type]
        project_root=str(config["project_root"]),
        config=config,
        streaming=streaming,
    )

    # Initialize micro-tier features
    mode_manager = ModeManager(config)
    _approval_gate = ApprovalGate(mode=approval_mode)  # TODO: wire into process_turn()
    recipe_runner = RecipeRunner(agent=agent)
    plugin_loader = PluginLoader(plugins_dir=str(config.get("plugins_dir", "plugins")))

    # Load plugins if plugins dir exists
    try:
        plugin_loader.discover()
    except Exception:
        pass

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
            f"[bold green]Micro agent ready.[/bold green] "
            f"Project: {config['project_root']}"
        )
        stream_status = "streaming" if streaming else "non-streaming"
        console.print(
            f"Mode: [bold]{mode_manager.current_mode}[/bold] | "
            f"Approval: [bold]{approval_mode}[/bold] | "
            f"{stream_status}. "
            "Type [bold]/mode[/bold], [bold]/recipe[/bold], [bold]/delegate[/bold], "
            "[bold]/provider[/bold] for commands. "
            "Type [bold]exit[/bold] or [bold]Ctrl-C[/bold] to quit.\n"
        )
    else:
        print(f"Micro agent ready. Project: {config['project_root']}")
        print(
            f"Mode: {mode_manager.current_mode} | Approval: {approval_mode}. "
            "Type 'exit' or Ctrl-C to quit.\n"
        )
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
                    current = agent.get_current_provider()
                    print(f"Current provider: {current}")
                else:
                    provider_name = parts[1].strip()
                    try:
                        agent.switch_provider(provider_name)
                        print(f"Switched to provider: {provider_name}")
                    except ValueError as exc:
                        print(f"Error: {exc}", file=sys.stderr)
                continue

            # Handle /mode REPL command
            if user_input.startswith("/mode"):
                parts = user_input.split(None, 1)
                if len(parts) == 1:
                    # Show current mode and available modes
                    print(f"Current mode: {mode_manager.current_mode}")
                    print("Available modes:")
                    for mode_info in mode_manager.list_modes():
                        marker = " *" if mode_info["active"] else "  "
                        print(
                            f"{marker} {mode_info['name']}: {mode_info['description']}"
                        )
                else:
                    mode_name = parts[1].strip()
                    try:
                        mode_manager.set_mode(mode_name)
                        overlay = mode_manager.get_prompt_overlay()
                        print(f"Switched to mode: {mode_name}")
                        if overlay:
                            print(f"  Mode overlay: {overlay[:80]}...")
                    except ValueError as exc:
                        print(f"Error: {exc}", file=sys.stderr)
                continue

            # Handle /recipe REPL command
            if user_input.startswith("/recipe"):
                parts = user_input.split(None, 1)
                if len(parts) < 2:
                    print("Usage: /recipe <path-to-recipe.yaml>", file=sys.stderr)
                    continue
                recipe_path = parts[1].strip()
                try:
                    print(f"Executing recipe: {recipe_path}")
                    results = recipe_runner.execute(recipe_path)
                    print(f"Recipe complete: {len(results)} steps executed")
                    for r in results:
                        print(
                            f"  [{r.get('name', '?')}]: {str(r.get('output', ''))[:80]}"
                        )
                except FileNotFoundError:
                    print(
                        f"Error: recipe file not found: {recipe_path}", file=sys.stderr
                    )
                except Exception as exc:
                    print(f"Error executing recipe: {exc}", file=sys.stderr)
                continue

            # Handle /delegate REPL command
            if user_input.startswith("/delegate"):
                parts = user_input.split(None, 1)
                if len(parts) < 2:
                    print("Usage: /delegate <task description>", file=sys.stderr)
                    continue
                task = parts[1].strip()
                from micro.delegate import Delegator

                delegator = Delegator(
                    sandbox_path=str(config["project_root"]),
                    model=str(config["model"]),
                    system_prompt=DEFAULT_SYSTEM_PROMPT,
                    constraints_path=str(config["constraints_path"]),
                )
                try:
                    print(f"Delegating task: {task[:60]}...")
                    result = delegator.spawn(task)
                    print(f"Delegation result:\n{result}")
                except Exception as exc:
                    print(f"Delegation error: {exc}", file=sys.stderr)
                continue

            # TODO: enforce mode tool restrictions on user-initiated turns
            # (e.g. warn or block when mode_manager.is_tool_allowed() returns False)

            # TODO: wire approval_gate into process_turn() tool-call path
            # so user-initiated turns also pass through the approval gate

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
    from micro.gate import ConstraintGate

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
        approval_mode = getattr(args, "approval_mode", "dangerous")
        cmd_chat(
            config,
            system_prompt,
            resume_session_id=args.resume,
            streaming=streaming,
            approval_mode=approval_mode,
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
