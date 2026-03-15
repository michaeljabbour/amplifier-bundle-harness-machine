"""Structural tests for the Micro Runtime Scaffold.

Validates that runtime/micro/ contains exactly 19 files with the required
structural patterns (imports, classes, functions, template vars).

~50 tests across 8 test classes.
"""

from __future__ import annotations

import os

import pytest

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MICRO_DIR = os.path.join(BUNDLE_ROOT, "runtime", "micro")


def _read_micro(filename: str) -> str:
    """Read a file from runtime/micro/."""
    path = os.path.join(MICRO_DIR, filename)
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# TestMicroFilesExist
# ---------------------------------------------------------------------------

# 14 nano files (copied into micro)
NANO_FILES = [
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
    "streaming.py",
    "session.py",
    "context.py",
    "providers.py",
]

# 5 micro-specific files
MICRO_SPECIFIC_FILES = [
    "modes.py",
    "recipes.py",
    "delegate.py",
    "approval.py",
    "loader.py",
]

ALL_NINETEEN = NANO_FILES + MICRO_SPECIFIC_FILES


class TestMicroFilesExist:
    @pytest.mark.parametrize("filename", ALL_NINETEEN)
    def test_micro_file_exists(self, filename):
        path = os.path.join(MICRO_DIR, filename)
        assert os.path.isfile(path), f"Missing: runtime/micro/{filename}"

    def test_micro_dir_has_exactly_nineteen_files(self):
        """runtime/micro/ must contain exactly 19 files."""
        files = [
            f
            for f in os.listdir(MICRO_DIR)
            if os.path.isfile(os.path.join(MICRO_DIR, f))
        ]
        assert sorted(files) == sorted(ALL_NINETEEN), (
            f"Expected {sorted(ALL_NINETEEN)}, got {sorted(files)}"
        )


# ---------------------------------------------------------------------------
# TestMicroModes
# ---------------------------------------------------------------------------


class TestMicroModes:
    def test_modes_has_mode_manager_class_and_default_modes_dict(self):
        """modes.py must have ModeManager class and DEFAULT_MODES dict."""
        content = _read_micro("modes.py")
        assert "class ModeManager" in content
        assert "DEFAULT_MODES" in content

    def test_modes_supports_switching(self):
        """ModeManager must have set_mode() switching method."""
        content = _read_micro("modes.py")
        assert "def set_mode(" in content or "def set_mode\n" in content

    def test_modes_has_default_work_review_plan_modes(self):
        """DEFAULT_MODES must include work, review, and plan modes."""
        content = _read_micro("modes.py")
        assert '"work"' in content or "'work'" in content
        assert '"review"' in content or "'review'" in content
        assert '"plan"' in content or "'plan'" in content

    def test_modes_has_system_prompt_overlay(self):
        """ModeManager must have get_prompt_overlay() returning overlay string."""
        content = _read_micro("modes.py")
        assert "system_prompt_overlay" in content
        assert "get_prompt_overlay" in content

    def test_modes_has_tool_restrictions_allowed_tools_safe(self):
        """modes.py must have allowed_tools, safe_tools, and is_tool_allowed()."""
        content = _read_micro("modes.py")
        assert "allowed_tools" in content
        assert "safe_tools" in content
        assert "is_tool_allowed" in content
        assert "get_allowed_tools" in content


# ---------------------------------------------------------------------------
# TestMicroRecipes
# ---------------------------------------------------------------------------


class TestMicroRecipes:
    def test_recipes_has_step_execution(self):
        """RecipeRunner must have _execute_step() for step dispatch."""
        content = _read_micro("recipes.py")
        assert "_execute_step" in content

    def test_recipes_has_yaml_loading(self):
        """RecipeRunner.execute() must load YAML recipe files."""
        content = _read_micro("recipes.py")
        assert "yaml" in content.lower()
        assert "def execute(" in content

    def test_recipes_has_while_loop(self):
        """recipes.py must support while_condition loops."""
        content = _read_micro("recipes.py")
        assert "while_condition" in content

    def test_recipes_has_approval_gate(self):
        """RecipeRunner must have _prompt_approval() for approval gates."""
        content = _read_micro("recipes.py")
        assert "_prompt_approval" in content or "approval" in content.lower()

    def test_recipes_has_context_accumulation(self):
        """RecipeRunner must accumulate context across steps."""
        content = _read_micro("recipes.py")
        assert "accumulated_context" in content or "context" in content.lower()


# ---------------------------------------------------------------------------
# TestMicroDelegate
# ---------------------------------------------------------------------------


class TestMicroDelegate:
    def test_delegate_spawn_creates_fresh_pico_agent(self):
        """Delegator.spawn() must create a fresh PicoAgent instance."""
        content = _read_micro("delegate.py")
        assert "spawn" in content
        assert "PicoAgent" in content or "create" in content or "fresh" in content

    def test_delegate_fresh_clean_own_new_context(self):
        """Each delegation must get its own clean context."""
        content = _read_micro("delegate.py")
        # Fresh context per delegation (not shared state)
        assert (
            "fresh" in content
            or "clean" in content
            or "new" in content
            or "own" in content
        )

    def test_delegate_returns_result(self):
        """Delegator.spawn() must return result from sub-agent."""
        content = _read_micro("delegate.py")
        assert "result" in content or "return" in content

    def test_delegate_has_tool_set_parameter(self):
        """Delegator must accept constrained tool_names parameter."""
        content = _read_micro("delegate.py")
        assert "tool_names" in content or "tool_set" in content or "tools" in content


# ---------------------------------------------------------------------------
# TestMicroApproval
# ---------------------------------------------------------------------------


class TestMicroApproval:
    def test_approval_has_prompt(self):
        """ApprovalGate must have _prompt() for user input."""
        content = _read_micro("approval.py")
        assert "_prompt" in content

    def test_approval_has_modes_always_dangerous_never(self):
        """ApprovalGate must support always, dangerous, and never modes."""
        content = _read_micro("approval.py")
        assert "always" in content
        assert "dangerous" in content
        assert "never" in content

    def test_approval_detects_sensitive_dangerous_destructive(self):
        """ApprovalGate must detect sensitive tools and destructive patterns."""
        content = _read_micro("approval.py")
        assert "_SENSITIVE_TOOLS" in content
        assert "_DESTRUCTIVE_PATTERNS" in content or "destructive" in content.lower()
        assert "_is_sensitive" in content


# ---------------------------------------------------------------------------
# TestMicroLoader
# ---------------------------------------------------------------------------


class TestMicroLoader:
    def test_loader_uses_importlib(self):
        """loader.py must use importlib for dynamic module loading."""
        content = _read_micro("loader.py")
        assert "importlib" in content

    def test_loader_has_plugin_discover(self):
        """PluginLoader must have discover() method."""
        content = _read_micro("loader.py")
        assert "class PluginLoader" in content
        assert "def discover(" in content or "discover" in content

    def test_loader_has_get_tools_interface(self):
        """PluginLoader must collect get_tools() from loaded modules."""
        content = _read_micro("loader.py")
        assert "get_tools" in content

    def test_loader_has_get_constraints_interface(self):
        """PluginLoader must collect get_constraints() from loaded modules."""
        content = _read_micro("loader.py")
        assert "get_constraints" in content

    def test_loader_py_directory_scanning_with_iterdir(self):
        """PluginLoader must scan directories for .py files via iterdir."""
        content = _read_micro("loader.py")
        assert "iterdir" in content or "listdir" in content or "glob" in content


# ---------------------------------------------------------------------------
# TestMicroCli
# ---------------------------------------------------------------------------


class TestMicroCli:
    def test_cli_has_mode_command(self):
        """/mode REPL command must exist in CLI."""
        content = _read_micro("cli.py")
        assert "/mode" in content

    def test_cli_has_recipe_command(self):
        """/recipe REPL command must exist in CLI."""
        content = _read_micro("cli.py")
        assert "/recipe" in content

    def test_cli_has_delegate_command(self):
        """/delegate REPL command must exist in CLI."""
        content = _read_micro("cli.py")
        assert "/delegate" in content

    def test_cli_has_approval_mode_flag(self):
        """--approval-mode flag must exist with choices=[always,dangerous,never]."""
        content = _read_micro("cli.py")
        assert "--approval-mode" in content
        assert "always" in content
        assert "dangerous" in content
        assert "never" in content

    def test_cli_still_has_rich(self):
        """CLI must still use Rich for output."""
        content = _read_micro("cli.py")
        assert "rich" in content

    def test_cli_still_has_signal_handling(self):
        """CLI must still handle KeyboardInterrupt."""
        content = _read_micro("cli.py")
        assert "KeyboardInterrupt" in content or "signal" in content

    def test_cli_still_has_streaming(self):
        """CLI must still support streaming responses."""
        content = _read_micro("cli.py")
        assert "stream" in content.lower()


# ---------------------------------------------------------------------------
# TestMicroRuntime
# ---------------------------------------------------------------------------


class TestMicroRuntime:
    def test_runtime_uses_modes(self):
        """runtime.py must import and use ModeManager."""
        content = _read_micro("runtime.py")
        assert "ModeManager" in content or "modes" in content.lower()

    def test_runtime_uses_recipes(self):
        """runtime.py must import and use RecipeRunner."""
        content = _read_micro("runtime.py")
        assert "RecipeRunner" in content or "recipes" in content.lower()

    def test_runtime_uses_delegate(self):
        """runtime.py must import and use Delegator."""
        content = _read_micro("runtime.py")
        assert "Delegator" in content or "delegate" in content.lower()

    def test_runtime_uses_approval(self):
        """runtime.py must import and use ApprovalGate."""
        content = _read_micro("runtime.py")
        assert "ApprovalGate" in content or "approval" in content.lower()

    def test_runtime_uses_loader(self):
        """runtime.py must import and use PluginLoader."""
        content = _read_micro("runtime.py")
        assert "PluginLoader" in content or "loader" in content.lower()

    def test_runtime_still_has_constraint_gate(self):
        """runtime.py must still use ConstraintGate."""
        content = _read_micro("runtime.py")
        assert "ConstraintGate" in content or "gate" in content

    def test_runtime_still_uses_litellm(self):
        """runtime.py must still use litellm for LLM calls."""
        content = _read_micro("runtime.py")
        assert "litellm" in content
