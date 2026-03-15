"""CLI entry point for pico standalone constrained-agent.

Subcommands:
    chat   — Interactive constrained agent session (with Rich rendering)
    check  — One-shot constraint validation
    audit  — Dry-run LLM validation against a transcript

Usage::

    pico-amplifier chat
    pico-amplifier check bash '{"command": "rm -rf /"}'
    pico-amplifier audit transcript.json

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
        description="Pico standalone constrained agent",
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
    subparsers.add_parser("chat", help="Interactive constrained agent session")

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

    from pico.gate import ConstraintGate

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


def cmd_chat(config: dict, system_prompt: str) -> None:
    """Run an interactive constrained agent session with Rich rendering."""
    from pico.gate import ConstraintGate
    from pico.runtime import PicoAgent
    from pico.tools import LocalToolExecutor

    gate = ConstraintGate(
        constraints_path=str(config["constraints_path"]),
        project_root=str(config["project_root"]),
    )
    executor = LocalToolExecutor(str(config["project_root"]))
    agent = PicoAgent(
        gate=gate,
        executor=executor,
        system_prompt=system_prompt,
        model=str(config["model"]),
        max_retries=int(config["max_retries"]),  # type: ignore[arg-type]
    )

    if _RICH_AVAILABLE:
        console = Console()
        console.print(
            f"[bold green]Pico agent ready.[/bold green] "
            f"Project: {config['project_root']}"
        )
        console.print("Type [bold]exit[/bold] or [bold]Ctrl-C[/bold] to quit.\n")
    else:
        print(f"Pico agent ready. Project: {config['project_root']}")
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

            try:
                response = asyncio.run(agent.process_turn(user_input))
            except KeyboardInterrupt:
                print("\nCancelled.")
                continue

            if _RICH_AVAILABLE and console is not None:
                console.print("\n[bold]Agent:[/bold]")
                console.print(Markdown(response))
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
    from pico.gate import ConstraintGate

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
        cmd_chat(config, system_prompt)
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
