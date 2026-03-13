"""Tests for the standalone CLI (runtime/cli.py).

Tests argument parsing and the check subcommand.
The chat subcommand requires an LLM, so it is not tested here.
"""

import os
import sys

# Add runtime to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime"
    ),
)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


# ---------------------------------------------------------------------------
# Tests: argument parsing
# ---------------------------------------------------------------------------


class TestArgParsing:
    def test_check_subcommand_parses(self):
        from cli import build_parser  # type: ignore[import]

        parser = build_parser()
        args = parser.parse_args(["check", "bash", '{"command": "echo hi"}'])
        assert args.subcommand == "check"
        assert args.tool_name == "bash"
        assert args.params_json == '{"command": "echo hi"}'

    def test_chat_subcommand_parses(self):
        from cli import build_parser  # type: ignore[import]

        parser = build_parser()
        args = parser.parse_args(["chat"])
        assert args.subcommand == "chat"

    def test_audit_subcommand_parses(self):
        from cli import build_parser  # type: ignore[import]

        parser = build_parser()
        args = parser.parse_args(["audit", "transcript.json"])
        assert args.subcommand == "audit"
        assert args.transcript_file == "transcript.json"

    def test_config_flag_parses(self):
        from cli import build_parser  # type: ignore[import]

        parser = build_parser()
        args = parser.parse_args(["--config", "my-config.yaml", "chat"])
        assert args.config == "my-config.yaml"


# ---------------------------------------------------------------------------
# Tests: check subcommand
# ---------------------------------------------------------------------------


class TestCheckSubcommand:
    def test_check_legal_action_returns_true(self):
        from cli import run_check  # type: ignore[import]

        result = run_check(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            tool_name="read_file",
            params_json='{"file_path": "src/main.py"}',
        )
        assert result[0] is True

    def test_check_illegal_action_returns_false_with_reason(self):
        from cli import run_check  # type: ignore[import]

        result = run_check(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            tool_name="bash",
            params_json='{"command": "rm -rf /"}',
        )
        assert result[0] is False
        assert "rm" in result[1].lower()

    def test_check_invalid_json_returns_error(self):
        from cli import run_check  # type: ignore[import]

        result = run_check(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            tool_name="bash",
            params_json="not valid json",
        )
        assert result[0] is False
        assert "json" in result[1].lower() or "error" in result[1].lower()


# ---------------------------------------------------------------------------
# Tests: config loading
# ---------------------------------------------------------------------------


class TestConfigLoading:
    def test_load_config_from_yaml(self, tmp_path):
        from cli import load_config  # type: ignore[import]

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "project_root: /my/project\n"
            "model: anthropic/claude-sonnet-4-20250514\n"
            "harness_type: action-verifier\n"
            "max_retries: 5\n"
        )
        config = load_config(str(config_file))
        assert config["project_root"] == "/my/project"
        assert config["max_retries"] == 5

    def test_load_config_missing_file_returns_defaults(self):
        from cli import load_config  # type: ignore[import]

        config = load_config("/nonexistent/config.yaml")
        assert config["project_root"] == os.getcwd()
        assert config["max_retries"] == 3

    def test_load_system_prompt(self, tmp_path):
        from cli import load_system_prompt  # type: ignore[import]

        prompt_file = tmp_path / "system-prompt.md"
        prompt_file.write_text("You are a constrained agent.\n")
        prompt = load_system_prompt(str(prompt_file))
        assert "constrained agent" in prompt

    def test_load_system_prompt_missing_uses_default(self):
        from cli import load_system_prompt  # type: ignore[import]

        prompt = load_system_prompt("/nonexistent/system-prompt.md")
        assert (
            "constrained" in prompt.lower()
        )  # Returns the default prompt about constrained agents
