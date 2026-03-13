"""CLI entry point for standalone nano-amplifier agents.

Subcommands:
    chat   — Interactive constrained agent session
    check  — One-shot constraint validation
    audit  — Post-hoc analysis of an agent transcript

Usage:
    pico-amplifier chat
    pico-amplifier check bash '{"command": "rm -rf /"}'
    pico-amplifier audit transcript.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
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


def load_config(config_path: str) -> dict:
    """Load config from a YAML file.

    Args:
        config_path: Path to config.yaml.

    Returns:
        Config dict. Falls back to defaults for missing keys or missing file.
    """
    config = dict(DEFAULT_CONFIG)
    try:
        import yaml

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
    """Load system prompt from a markdown file.

    Args:
        prompt_path: Path to system-prompt.md.

    Returns:
        Prompt string. Falls back to default if file is missing.
    """
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
        description="Standalone nano-amplifier constrained agent",
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
    audit_parser = subparsers.add_parser("audit", help="Post-hoc transcript analysis")
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
    """Run a one-shot constraint check.

    Args:
        constraints_path: Path to constraints.py.
        tool_name: Tool name to check.
        params_json: JSON string of tool parameters.

    Returns:
        (is_legal, reason) tuple.
    """
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON parameters: {exc}"

    from runtime import ConstraintGate

    gate = ConstraintGate(constraints_path)
    return gate.check(tool_name, params)


# ---------------------------------------------------------------------------
# Subcommand: chat
# ---------------------------------------------------------------------------


def run_chat(config: dict, system_prompt: str) -> None:
    """Run an interactive constrained agent session.

    Args:
        config: Loaded configuration dict.
        system_prompt: System prompt string.
    """
    from runtime import AgentLoop

    loop = AgentLoop(
        constraints_path=config["constraints_path"],
        project_root=config["project_root"],
        system_prompt=system_prompt,
        model=config["model"],
        max_retries=config["max_retries"],
    )

    print(f"Constrained agent ready. Project: {config['project_root']}")
    print("Type 'exit' or Ctrl+C to quit.\n")

    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ("exit", "quit"):
                break
            response = loop.process_turn(user_input)
            print(f"\nAgent: {response}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")


# ---------------------------------------------------------------------------
# Subcommand: audit
# ---------------------------------------------------------------------------


def run_audit(config: dict, transcript_path: str) -> None:
    """Audit a transcript file for constraint violations.

    Args:
        config: Loaded configuration dict.
        transcript_path: Path to transcript JSON file.
    """
    from runtime import ConstraintGate

    gate = ConstraintGate(config["constraints_path"])

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
        run_chat(config, system_prompt)
    elif args.subcommand == "check":
        is_legal, reason = run_check(
            config["constraints_path"],
            args.tool_name,
            args.params_json,
        )
        if is_legal:
            print(f"LEGAL: {args.tool_name}")
        else:
            print(f"ILLEGAL: {args.tool_name} — {reason}")
        sys.exit(0 if is_legal else 1)
    elif args.subcommand == "audit":
        run_audit(config, args.transcript_file)


if __name__ == "__main__":
    main()
