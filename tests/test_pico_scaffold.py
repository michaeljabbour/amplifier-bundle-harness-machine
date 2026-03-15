"""Structural tests for the Pico Runtime Scaffold.

Validates that runtime/pico/ contains exactly 10 files with the required
structural patterns (imports, classes, functions, template vars).

~45 tests across 6 test classes.
"""

from __future__ import annotations

import os

import pytest

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICO_DIR = os.path.join(BUNDLE_ROOT, "runtime", "pico")


def _read_pico(filename: str) -> str:
    """Read a file from runtime/pico/."""
    path = os.path.join(PICO_DIR, filename)
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# TestPicoFilesExist
# ---------------------------------------------------------------------------


PICO_FILES = [
    "__init__.py",
    "gate.py",
    "tools.py",
    "runtime.py",
    "cli.py",
    "setup.sh.template",
    "pyproject.toml.template",
    "Dockerfile.template",
    "docker-compose.template.yaml",
    "config.yaml.template",
]


class TestPicoFilesExist:
    @pytest.mark.parametrize("filename", PICO_FILES)
    def test_pico_file_exists(self, filename):
        path = os.path.join(PICO_DIR, filename)
        assert os.path.isfile(path), f"Missing: runtime/pico/{filename}"

    def test_pico_dir_has_exactly_ten_files(self):
        """runtime/pico/ must contain exactly 10 files (no extras, no missing)."""
        files = [
            f for f in os.listdir(PICO_DIR) if os.path.isfile(os.path.join(PICO_DIR, f))
        ]
        assert sorted(files) == sorted(PICO_FILES), (
            f"Expected {sorted(PICO_FILES)}, got {sorted(files)}"
        )


# ---------------------------------------------------------------------------
# TestPicoCli
# ---------------------------------------------------------------------------


class TestPicoCli:
    def test_cli_imports_rich(self):
        content = _read_pico("cli.py")
        assert "rich" in content

    def test_cli_uses_markdown(self):
        content = _read_pico("cli.py")
        assert "Markdown" in content

    def test_cli_handles_keyboard_interrupt(self):
        content = _read_pico("cli.py")
        assert "KeyboardInterrupt" in content

    def test_cli_handles_eoferror(self):
        content = _read_pico("cli.py")
        assert "EOFError" in content

    def test_cli_goodbye_message(self):
        content = _read_pico("cli.py")
        assert "Goodbye" in content

    def test_cli_has_chat_subcommand(self):
        content = _read_pico("cli.py")
        assert "chat" in content

    def test_cli_has_check_subcommand(self):
        content = _read_pico("cli.py")
        assert "check" in content

    def test_cli_has_audit_subcommand(self):
        content = _read_pico("cli.py")
        assert "audit" in content

    def test_cli_loads_config_yaml(self):
        content = _read_pico("cli.py")
        assert "config.yaml" in content or "yaml.safe_load" in content

    def test_cli_loads_system_prompt(self):
        content = _read_pico("cli.py")
        assert "system-prompt" in content or "system_prompt" in content

    def test_cli_has_main_function(self):
        content = _read_pico("cli.py")
        assert "def main(" in content

    def test_cli_uses_argparse(self):
        content = _read_pico("cli.py")
        assert "argparse" in content

    def test_cli_has_console_instance(self):
        content = _read_pico("cli.py")
        assert "Console" in content

    def test_cli_has_cancel_message(self):
        content = _read_pico("cli.py")
        # "Cancelled" or "cancel" should appear for KeyboardInterrupt cancel during response
        assert "cancel" in content.lower() or "Cancelled" in content


# ---------------------------------------------------------------------------
# TestPicoRuntime
# ---------------------------------------------------------------------------


class TestPicoRuntime:
    def test_runtime_uses_constraint_gate(self):
        content = _read_pico("runtime.py")
        assert "ConstraintGate" in content or "gate" in content

    def test_runtime_has_retry_logic(self):
        content = _read_pico("runtime.py")
        assert "max_retries" in content or "retry" in content.lower()

    def test_runtime_has_max_iterations(self):
        content = _read_pico("runtime.py")
        assert "MAX_ITERATIONS" in content

    def test_runtime_has_system_prompt_parameter(self):
        content = _read_pico("runtime.py")
        assert "system_prompt" in content

    def test_runtime_uses_config_driven_model(self):
        content = _read_pico("runtime.py")
        assert "model" in content

    def test_runtime_imports_litellm(self):
        content = _read_pico("runtime.py")
        assert "litellm" in content

    def test_runtime_uses_acompletion(self):
        content = _read_pico("runtime.py")
        assert "acompletion" in content

    def test_runtime_processes_tool_calls(self):
        content = _read_pico("runtime.py")
        assert "tool_calls" in content

    def test_runtime_maintains_messages_history(self):
        content = _read_pico("runtime.py")
        assert "messages" in content

    def test_runtime_has_tool_schemas(self):
        content = _read_pico("runtime.py")
        assert "TOOL_SCHEMAS" in content

    def test_runtime_has_tool_definitions_alias(self):
        content = _read_pico("runtime.py")
        assert "TOOL_DEFINITIONS" in content


# ---------------------------------------------------------------------------
# TestPicoTools
# ---------------------------------------------------------------------------


REQUIRED_TOOLS = [
    "read_file",
    "write_file",
    "edit_file",
    "apply_patch",
    "bash",
    "grep",
    "glob",
]


class TestPicoTools:
    def test_tools_enforce_project_root(self):
        content = _read_pico("tools.py")
        assert "project_root" in content

    def test_tools_use_resolve_realpath(self):
        content = _read_pico("tools.py")
        assert "realpath" in content or "_resolve" in content

    @pytest.mark.parametrize("tool_name", REQUIRED_TOOLS)
    def test_required_tool_exists(self, tool_name):
        content = _read_pico("tools.py")
        assert (
            f"def {tool_name}" in content
            or f'"{tool_name}"' in content
            or f"'{tool_name}'" in content
        ), f"Tool '{tool_name}' not found in tools.py"

    def test_tools_use_subprocess_for_bash(self):
        content = _read_pico("tools.py")
        assert "subprocess" in content

    def test_tools_have_ripgrep_fallback(self):
        content = _read_pico("tools.py")
        # ripgrep (rg) should be tried first, with python fallback
        assert "rg" in content or "ripgrep" in content
        assert "fallback" in content.lower() or "FileNotFoundError" in content

    def test_tools_raise_permission_error(self):
        content = _read_pico("tools.py")
        assert "PermissionError" in content

    def test_tools_integrate_with_constraint(self):
        content = _read_pico("tools.py")
        assert (
            "ConstraintViolation" in content
            or "gate" in content.lower()
            or "constraint" in content.lower()
        )


# ---------------------------------------------------------------------------
# TestPicoGate
# ---------------------------------------------------------------------------


class TestPicoGate:
    def test_gate_has_constraint_gate_class(self):
        content = _read_pico("gate.py")
        assert "class ConstraintGate" in content

    def test_gate_has_check_method(self):
        content = _read_pico("gate.py")
        assert "def check(" in content

    def test_gate_supports_is_legal_action(self):
        content = _read_pico("gate.py")
        assert "is_legal_action" in content


# ---------------------------------------------------------------------------
# TestPicoTemplates
# ---------------------------------------------------------------------------


class TestPicoTemplates:
    # setup.sh.template
    def test_setup_sh_creates_venv(self):
        content = _read_pico("setup.sh.template")
        assert "venv" in content

    def test_setup_sh_pip_install(self):
        content = _read_pico("setup.sh.template")
        assert "pip install" in content

    def test_setup_sh_runs_pytest(self):
        content = _read_pico("setup.sh.template")
        assert "pytest" in content

    # pyproject.toml.template
    def test_pyproject_has_harness_name_var(self):
        content = _read_pico("pyproject.toml.template")
        assert "{{harness_name}}" in content

    def test_pyproject_has_litellm_dep(self):
        content = _read_pico("pyproject.toml.template")
        assert "litellm" in content

    def test_pyproject_has_rich_dep(self):
        content = _read_pico("pyproject.toml.template")
        assert "rich" in content

    def test_pyproject_has_pyyaml_dep(self):
        content = _read_pico("pyproject.toml.template")
        assert "pyyaml" in content

    def test_pyproject_uses_hatchling(self):
        content = _read_pico("pyproject.toml.template")
        assert "hatchling" in content

    def test_pyproject_has_entry_point(self):
        content = _read_pico("pyproject.toml.template")
        assert "[project.scripts]" in content or "scripts" in content

    # Dockerfile.template
    def test_dockerfile_uses_python_slim(self):
        content = _read_pico("Dockerfile.template")
        assert "python:3.11-slim" in content

    def test_dockerfile_installs_git_and_ripgrep(self):
        content = _read_pico("Dockerfile.template")
        assert "git" in content
        assert "ripgrep" in content

    def test_dockerfile_has_nonroot_user(self):
        content = _read_pico("Dockerfile.template")
        assert "useradd" in content or "adduser" in content

    # docker-compose.template.yaml
    def test_docker_compose_has_project_root_volume(self):
        content = _read_pico("docker-compose.template.yaml")
        assert "{{project_root}}" in content

    def test_docker_compose_has_resource_limits(self):
        content = _read_pico("docker-compose.template.yaml")
        assert "mem_limit" in content or "cpus" in content

    def test_docker_compose_has_security_opts(self):
        content = _read_pico("docker-compose.template.yaml")
        assert "no-new-privileges" in content or "security_opt" in content
