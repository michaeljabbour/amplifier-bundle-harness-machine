# Harness Runtime Gap Fix — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Close the runtime gap so generated nano-amplifiers are self-contained constrained agent runtimes — usable as an Amplifier hook, a standalone CLI agent, or a Docker container.

**Architecture:** One brick (constraints.py), three studs. The hook module (`modules/hooks-harness/`) dynamically loads any constraints.py and enforces it via Amplifier's `tool:pre` hook. The standalone runtime (`runtime/`) provides an LLM agent loop with constraint gate and tool executor. Docker templates wrap the standalone runtime in a container. The `/harness-finish` mode assembles all three studs into a complete deliverable.

**Tech Stack:** Python 3.11+, pytest, litellm (standalone LLM client), pyyaml, importlib.util (dynamic module loading), subprocess (tool execution), dataclasses

**Design doc:** `docs/plans/2026-03-13-harness-runtime-design.md`

---

## Orientation: What Already Exists

You are adding to an existing Amplifier bundle at the repo root. Here is what's already here:

```
amplifier-bundle-autoharness/
├── bundle.md                    # Bundle manifest (DO NOT MODIFY)
├── behaviors/harness-machine.yaml   # Behavior config
├── agents/                      # 7 agent files (*.md)
├── modes/                       # 7 mode files (*.md)
├── recipes/                     # 4 recipe files (*.yaml)
├── skills/                      # 3 skill directories
├── context/                     # Instructions, philosophy, pattern, harness-format, examples/
├── templates/                   # STATE.yaml, Docker templates, scripts
├── tests/test_scaffold.py       # 139 passing structural tests
└── docs/plans/                  # Design docs
```

**There are NO `modules/` or `runtime/` directories yet.** You are creating them from scratch.

**There is NO `conftest.py`, NO `pyproject.toml`, NO `pytest.ini` at the repo root.** Tests run with bare `pytest tests/`.

**`amplifier_core` is NOT installed** in the current environment. The hook module must provide a fallback `HookResult` for testing.

---

## Task 1: Generic Amplifier Hook Module

**What you're building:** A Python package at `modules/hooks-harness/` that dynamically loads ANY `constraints.py` and enforces it via Amplifier's `tool:pre` hook event. This is the highest-value piece — get it right.

**Files:**
- Create: `tests/fixtures/constraints_simple.py`
- Create: `tests/fixtures/constraints_validate.py`
- Create: `tests/fixtures/constraints_empty.py`
- Create: `tests/test_hooks_harness.py`
- Create: `modules/hooks-harness/pyproject.toml`
- Create: `modules/hooks-harness/amplifier_module_hooks_harness/__init__.py`

### Step 1: Create test fixture — simple `is_legal_action` constraints file

Create the directory and a minimal constraints file that uses the `is_legal_action(tool_name, params) -> (bool, str)` signature (same as pico-amplifier):

```bash
mkdir -p tests/fixtures
```

Create file `tests/fixtures/constraints_simple.py`:

```python
"""Simple test constraints using is_legal_action signature.

Mimics the pico-amplifier pattern: is_legal_action(tool_name, parameters) -> (bool, str).
Only allows read_file inside /tmp/test-project.
"""

import os

PROJECT_ROOT = "/tmp/test-project"


def is_legal_action(tool_name: str, parameters: dict) -> tuple[bool, str]:
    """Top-level dispatcher for constraint checking."""
    if tool_name == "read_file":
        path = parameters.get("file_path", "")
        resolved = os.path.realpath(os.path.join(PROJECT_ROOT, path))
        if resolved.startswith(os.path.realpath(PROJECT_ROOT)):
            return True, ""
        return False, f"Path {path!r} resolves outside project root"
    if tool_name == "bash":
        cmd = parameters.get("command", "")
        if "rm" in cmd:
            return False, "rm commands are not permitted"
        return True, ""
    return True, ""
```

### Step 2: Create test fixture — `validate_action` signature

Create file `tests/fixtures/constraints_validate.py`:

```python
"""Test constraints using validate_action(state, action) signature.

The Amplifier-native hook signature used in harness-format.md examples.
"""


def validate_action(state: dict, action: dict) -> tuple[bool, str]:
    """Validate an action against constraints."""
    tool_name = action.get("tool_name", "")
    if tool_name == "bash":
        cmd = action.get("parameters", {}).get("command", "")
        if "sudo" in cmd:
            return False, "sudo is not permitted"
    return True, ""
```

### Step 3: Create test fixture — empty constraints (error case)

Create file `tests/fixtures/constraints_empty.py`:

```python
"""Constraints file with neither is_legal_action nor validate_action.

Used to test the error case where mount() can't find a usable function.
"""


def some_unrelated_function():
    return 42
```

### Step 4: Write the failing tests

Create file `tests/test_hooks_harness.py`:

```python
"""Tests for the generic Amplifier hook module (modules/hooks-harness).

Tests:
- Dynamic loading of constraints.py via importlib
- Auto-detection of is_legal_action vs validate_action signatures
- tool:pre deny on illegal action
- tool:pre continue on legal action
- strict=true (deny) vs strict=false (inject_context)
- Missing constraints file raises FileNotFoundError
- Missing function raises ValueError
- project_root from coordinator capability
"""

import asyncio
import os
import sys

import pytest

# Add modules to path so we can import the hook module directly
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "modules",
        "hooks-harness",
    ),
)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


# ---------------------------------------------------------------------------
# Mock coordinator for testing (simulates Amplifier's ModuleCoordinator)
# ---------------------------------------------------------------------------


class MockHookRegistry:
    """Records hook registrations so tests can invoke handlers directly."""

    def __init__(self):
        self.handlers = {}

    def register(self, event, handler, priority=100, name=""):
        self.handlers[event] = handler
        # Return an unregister function (matches real API)
        def unregister():
            self.handlers.pop(event, None)
        return unregister


class MockCoordinator:
    """Simulates the Amplifier ModuleCoordinator."""

    def __init__(self, working_dir="/tmp/test-project"):
        self.hooks = MockHookRegistry()
        self._capabilities = {"session.working_dir": working_dir}

    def get_capability(self, name):
        return self._capabilities.get(name)


# ---------------------------------------------------------------------------
# Tests: mount() function
# ---------------------------------------------------------------------------


class TestMount:
    """Test the mount() function that loads constraints and registers hooks."""

    def test_mount_with_is_legal_action_succeeds(self):
        """mount() succeeds when constraints.py exports is_legal_action."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator()
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            "strict": True,
        }
        cleanup = asyncio.get_event_loop().run_until_complete(
            mount(coordinator, config)
        )
        assert "tool:pre" in coordinator.hooks.handlers
        assert cleanup is not None
        cleanup()
        assert "tool:pre" not in coordinator.hooks.handlers

    def test_mount_with_validate_action_succeeds(self):
        """mount() succeeds when constraints.py exports validate_action."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator()
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, "constraints_validate.py"),
            "strict": True,
        }
        cleanup = asyncio.get_event_loop().run_until_complete(
            mount(coordinator, config)
        )
        assert "tool:pre" in coordinator.hooks.handlers

    def test_mount_missing_file_raises_file_not_found(self):
        """mount() raises FileNotFoundError when constraints_path doesn't exist."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator()
        config = {
            "constraints_path": "/nonexistent/constraints.py",
            "strict": True,
        }
        with pytest.raises(FileNotFoundError):
            asyncio.get_event_loop().run_until_complete(mount(coordinator, config))

    def test_mount_no_function_raises_value_error(self):
        """mount() raises ValueError when constraints.py has neither function."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator()
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, "constraints_empty.py"),
            "strict": True,
        }
        with pytest.raises(ValueError, match="neither"):
            asyncio.get_event_loop().run_until_complete(mount(coordinator, config))

    def test_mount_registers_at_priority_5(self):
        """mount() registers the hook at priority 5 (high priority)."""
        from amplifier_module_hooks_harness import mount

        # Patch register to capture the priority argument
        captured = {}
        coordinator = MockCoordinator()
        original_register = coordinator.hooks.register

        def capture_register(event, handler, priority=100, name=""):
            captured["priority"] = priority
            captured["event"] = event
            return original_register(event, handler, priority, name)

        coordinator.hooks.register = capture_register
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            "strict": True,
        }
        asyncio.get_event_loop().run_until_complete(mount(coordinator, config))
        assert captured["priority"] == 5
        assert captured["event"] == "tool:pre"

    def test_mount_uses_working_dir_from_coordinator(self):
        """mount() reads project_root from coordinator capability."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator(working_dir="/custom/project/dir")
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            "strict": True,
        }
        asyncio.get_event_loop().run_until_complete(mount(coordinator, config))
        # Handler was registered — it will use the working_dir internally
        assert "tool:pre" in coordinator.hooks.handlers


# ---------------------------------------------------------------------------
# Tests: tool:pre handler behavior
# ---------------------------------------------------------------------------


class TestToolPreHandler:
    """Test the tool:pre hook handler that enforces constraints."""

    def _setup_handler(self, constraints_file, strict=True, working_dir="/tmp/test-project"):
        """Helper: mount with given constraints and return the handler."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator(working_dir=working_dir)
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, constraints_file),
            "strict": strict,
        }
        asyncio.get_event_loop().run_until_complete(mount(coordinator, config))
        return coordinator.hooks.handlers["tool:pre"]

    def test_legal_action_returns_continue(self):
        """Legal action returns HookResult with action='continue'."""
        handler = self._setup_handler("constraints_simple.py")
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": "read_file",
                "parameters": {"file_path": "src/main.py"},
            })
        )
        assert result.action == "continue"

    def test_illegal_action_returns_deny_in_strict_mode(self):
        """Illegal action returns HookResult with action='deny' when strict=True."""
        handler = self._setup_handler("constraints_simple.py", strict=True)
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": "bash",
                "parameters": {"command": "rm -rf /"},
            })
        )
        assert result.action == "deny"
        assert "rm" in result.reason.lower()

    def test_illegal_action_returns_inject_context_in_warn_mode(self):
        """Illegal action returns HookResult with action='inject_context' when strict=False."""
        handler = self._setup_handler("constraints_simple.py", strict=False)
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": "bash",
                "parameters": {"command": "rm -rf /"},
            })
        )
        assert result.action == "inject_context"
        assert result.context_injection  # non-empty warning message

    def test_deny_includes_context_injection_for_agent_retry(self):
        """Deny result includes context_injection so the agent can self-correct."""
        handler = self._setup_handler("constraints_simple.py", strict=True)
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": "bash",
                "parameters": {"command": "rm -rf /tmp/stuff"},
            })
        )
        assert result.action == "deny"
        assert result.context_injection  # agent gets explanation for retry

    def test_validate_action_signature_works(self):
        """constraints.py with validate_action() is correctly invoked."""
        handler = self._setup_handler("constraints_validate.py")
        # This should be denied — validate_action blocks sudo
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": "bash",
                "parameters": {"command": "sudo apt install foo"},
            })
        )
        assert result.action == "deny"
        assert "sudo" in result.reason.lower()

    def test_validate_action_legal_returns_continue(self):
        """validate_action() with a legal action returns continue."""
        handler = self._setup_handler("constraints_validate.py")
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": "read_file",
                "parameters": {"file_path": "readme.md"},
            })
        )
        assert result.action == "continue"

    def test_unknown_tool_passes_through(self):
        """Tools not covered by constraints pass through as legal."""
        handler = self._setup_handler("constraints_simple.py")
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": "web_search",
                "parameters": {"query": "hello"},
            })
        )
        assert result.action == "continue"

    def test_constraint_exception_treated_as_deny(self):
        """If is_legal_action() raises, treat as deny (fail-closed)."""
        handler = self._setup_handler("constraints_simple.py")
        # Pass parameters that might cause issues — None as tool_name
        result = asyncio.get_event_loop().run_until_complete(
            handler("tool:pre", {
                "tool_name": None,
                "parameters": None,
            })
        )
        # Should deny (fail-closed), not crash
        assert result.action == "deny"

    def test_non_tool_pre_event_returns_continue(self):
        """Events other than tool:pre are passed through."""
        handler = self._setup_handler("constraints_simple.py")
        result = asyncio.get_event_loop().run_until_complete(
            handler("prompt:submit", {"prompt": "hello"})
        )
        assert result.action == "continue"
```

### Step 5: Run tests to verify they fail

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_hooks_harness.py -v 2>&1 | head -30
```

**Expected:** All tests FAIL with `ModuleNotFoundError: No module named 'amplifier_module_hooks_harness'`

### Step 6: Create the hook module package definition

Create file `modules/hooks-harness/pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "amplifier-module-hooks-harness"
version = "0.1.0"
description = "Generic constraint enforcement hook — dynamically loads any constraints.py and enforces via tool:pre"
requires-python = ">=3.11"
license = "MIT"
# Zero declared dependencies — amplifier-core is a peer dependency provided by the host
dependencies = []

[project.entry-points."amplifier.modules"]
hooks-harness = "amplifier_module_hooks_harness:mount"
```

### Step 7: Implement the hook module

```bash
mkdir -p modules/hooks-harness/amplifier_module_hooks_harness
```

Create file `modules/hooks-harness/amplifier_module_hooks_harness/__init__.py`:

```python
"""Amplifier Hook Module: Generic Constraint Enforcement.

Dynamically loads ANY constraints.py and enforces it via Amplifier's tool:pre hook.
Supports two constraint function signatures with auto-detection:
  - is_legal_action(tool_name: str, parameters: dict) -> (bool, str)
  - validate_action(state: dict, action: dict) -> (bool, str)

Usage in behavior.yaml:
    hooks:
      - module: hooks-harness
        config:
          constraints_path: ./constraints.py
          strict: true  # deny on violation (false = warn via inject_context)
"""

from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable

# ---------------------------------------------------------------------------
# HookResult: use amplifier_core's if available, otherwise define our own
# compatible dataclass (for testing without amplifier installed).
# ---------------------------------------------------------------------------
try:
    from amplifier_core.models import HookResult
except ImportError:

    @dataclass
    class HookResult:
        """Minimal HookResult compatible with Amplifier's hook protocol."""

        action: str = "continue"
        reason: str = ""
        context_injection: str = ""
        context_injection_role: str = "system"
        ephemeral: bool = True
        user_message: str = ""
        user_message_level: str = "info"


__all__ = ["mount"]
__version__ = "0.1.0"


# ---------------------------------------------------------------------------
# Dynamic constraint loading
# ---------------------------------------------------------------------------


def _load_constraints_module(constraints_path: str) -> Any:
    """Load a constraints.py file as a Python module via importlib.

    Args:
        constraints_path: Absolute or relative path to the constraints.py file.

    Returns:
        The loaded module object.

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    path = os.path.abspath(constraints_path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Constraints file not found: {path}")

    spec = importlib.util.spec_from_file_location("_harness_constraints", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _detect_signature(
    module: Any,
) -> tuple[str, Callable]:
    """Auto-detect which constraint function signature the module exports.

    Checks for (in order of preference):
      1. is_legal_action(tool_name, parameters) -> (bool, str)
      2. validate_action(state, action) -> (bool, str)

    Args:
        module: The loaded constraints module.

    Returns:
        Tuple of (signature_name, callable).

    Raises:
        ValueError: If neither function is found.
    """
    if hasattr(module, "is_legal_action") and callable(module.is_legal_action):
        return "is_legal_action", module.is_legal_action
    if hasattr(module, "validate_action") and callable(module.validate_action):
        return "validate_action", module.validate_action
    raise ValueError(
        f"Constraints module exports neither 'is_legal_action' nor "
        f"'validate_action'. Found: {[n for n in dir(module) if not n.startswith('_')]}"
    )


# ---------------------------------------------------------------------------
# Hook handler factory
# ---------------------------------------------------------------------------


def _make_handler(
    constraint_fn: Callable,
    signature_name: str,
    strict: bool,
    project_root: str,
) -> Callable:
    """Build the async tool:pre handler that enforces constraints.

    Args:
        constraint_fn: The is_legal_action or validate_action callable.
        signature_name: "is_legal_action" or "validate_action".
        strict: If True, deny on violation. If False, inject_context (warn).
        project_root: The project root directory for context.

    Returns:
        An async handler function compatible with Amplifier's hook protocol.
    """

    async def handler(event: str, data: dict[str, Any]) -> HookResult:
        # Only act on tool:pre events
        if event != "tool:pre":
            return HookResult(action="continue")

        tool_name = data.get("tool_name")
        parameters = data.get("parameters") or {}

        try:
            if signature_name == "is_legal_action":
                is_legal, reason = constraint_fn(tool_name, parameters)
            else:
                # validate_action(state, action) signature
                state = {"project_root": project_root}
                action = {"tool_name": tool_name, "parameters": parameters}
                is_legal, reason = constraint_fn(state, action)
        except Exception as exc:
            # Fail-closed: exceptions are treated as deny
            is_legal = False
            reason = f"Constraint check raised an exception: {exc}"

        if is_legal:
            return HookResult(action="continue")

        # Build context injection for agent self-correction
        injection = (
            f"<constraint-violation>\n"
            f"Your proposed {tool_name!r} call was rejected.\n"
            f"Reason: {reason}\n"
            f"Please retry with a modified approach that satisfies the constraint.\n"
            f"</constraint-violation>"
        )

        if strict:
            return HookResult(
                action="deny",
                reason=f"Constraint violation: {reason}",
                context_injection=injection,
                context_injection_role="system",
                ephemeral=True,
            )
        else:
            return HookResult(
                action="inject_context",
                context_injection=injection,
                context_injection_role="system",
                ephemeral=True,
                user_message=f"⚠️ Constraint warning: {reason}",
                user_message_level="warn",
            )

    return handler


# ---------------------------------------------------------------------------
# Module entry point
# ---------------------------------------------------------------------------


async def mount(
    coordinator: Any,
    config: dict[str, Any],
) -> Callable[[], None] | None:
    """Mount the constraint enforcement hook module.

    Called by Amplifier kernel during session initialization.
    Loads the constraints.py specified in config and registers a tool:pre handler.

    Args:
        coordinator: The Amplifier ModuleCoordinator.
        config: Module configuration from behavior.yaml. Expected keys:
            - constraints_path (str): Path to the constraints.py file.
            - strict (bool, default True): Deny on violation vs warn.

    Returns:
        Cleanup function to unregister hooks on shutdown.

    Raises:
        FileNotFoundError: If constraints_path doesn't exist.
        ValueError: If constraints.py exports neither function.
    """
    constraints_path = config.get("constraints_path", "constraints.py")
    strict = config.get("strict", True)

    # Resolve project_root from coordinator capability, fall back to config
    project_root = None
    if hasattr(coordinator, "get_capability"):
        project_root = coordinator.get_capability("session.working_dir")
    if not project_root:
        project_root = config.get("project_root", os.getcwd())

    # Load and detect
    module = _load_constraints_module(constraints_path)
    signature_name, constraint_fn = _detect_signature(module)

    # Build and register handler
    handler = _make_handler(constraint_fn, signature_name, strict, project_root)

    handlers = []
    handlers.append(
        coordinator.hooks.register(
            event="tool:pre",
            handler=handler,
            priority=5,  # High priority — enforce before other hooks
            name="harness-constraint-enforcement",
        )
    )

    def cleanup() -> None:
        for unregister in handlers:
            unregister()

    return cleanup
```

### Step 8: Run tests to verify they pass

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/test_hooks_harness.py -v
```

**Expected:** All 14 tests PASS.

### Step 9: Run the full existing test suite to check for regressions

```bash
python -m pytest tests/ -v
```

**Expected:** All 139 existing tests PASS plus the 14 new ones = 153 total.

### Step 10: Commit

```bash
git add modules/ tests/fixtures/ tests/test_hooks_harness.py
git commit -m "feat: add generic amplifier hook module (modules/hooks-harness)

- Dynamic constraints.py loading via importlib.util
- Auto-detects is_legal_action vs validate_action signatures
- tool:pre enforcement: deny (strict) or inject_context (warn)
- Fail-closed on exceptions
- project_root from coordinator capability
- 14 tests covering all code paths"
```

---

## Task 2: Standalone Tool Executor

**What you're building:** `runtime/tools.py` — the actual tool implementations (read_file, write_file, edit_file, bash, grep, glob) that execute after constraints pass. Every tool independently enforces the project_root boundary as defense-in-depth.

**Files:**
- Create: `tests/test_tools.py`
- Create: `runtime/__init__.py`
- Create: `runtime/tools.py`

### Step 1: Write the failing tests

Create file `tests/test_tools.py`:

```python
"""Tests for the standalone tool executor (runtime/tools.py).

Every tool enforces project_root boundary independently (defense-in-depth).
Tests use a temporary directory as project_root.
"""

import os
import sys
import tempfile

import pytest

# Add runtime to path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime"),
)


@pytest.fixture
def project(tmp_path):
    """Create a temporary project directory with some files."""
    # Create test files
    (tmp_path / "hello.txt").write_text("Hello, world!\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')\n")
    return tmp_path


@pytest.fixture
def tools(project):
    """Create a ToolExecutor bound to the temp project."""
    from tools import ToolExecutor

    return ToolExecutor(project_root=str(project))


# ---------------------------------------------------------------------------
# read_file tests
# ---------------------------------------------------------------------------


class TestReadFile:
    def test_read_file_inside_project(self, tools, project):
        result = tools.read_file(str(project / "hello.txt"))
        assert "Hello, world!" in result

    def test_read_file_relative_path(self, tools):
        result = tools.read_file("hello.txt")
        assert "Hello, world!" in result

    def test_read_file_outside_project_raises(self, tools):
        with pytest.raises(PermissionError, match="outside project root"):
            tools.read_file("/etc/passwd")

    def test_read_file_traversal_raises(self, tools):
        with pytest.raises(PermissionError, match="outside project root"):
            tools.read_file("../../etc/passwd")

    def test_read_file_nonexistent_raises(self, tools, project):
        with pytest.raises(FileNotFoundError):
            tools.read_file(str(project / "nonexistent.txt"))


# ---------------------------------------------------------------------------
# write_file tests
# ---------------------------------------------------------------------------


class TestWriteFile:
    def test_write_file_inside_project(self, tools, project):
        tools.write_file(str(project / "output.txt"), "test content")
        assert (project / "output.txt").read_text() == "test content"

    def test_write_file_relative_path(self, tools, project):
        tools.write_file("output.txt", "relative write")
        assert (project / "output.txt").read_text() == "relative write"

    def test_write_file_creates_parent_dirs(self, tools, project):
        tools.write_file("new_dir/output.txt", "nested")
        assert (project / "new_dir" / "output.txt").read_text() == "nested"

    def test_write_file_outside_project_raises(self, tools):
        with pytest.raises(PermissionError, match="outside project root"):
            tools.write_file("/tmp/evil.txt", "hacked")


# ---------------------------------------------------------------------------
# edit_file tests
# ---------------------------------------------------------------------------


class TestEditFile:
    def test_edit_file_replaces_string(self, tools, project):
        tools.edit_file(str(project / "hello.txt"), "Hello", "Goodbye")
        assert (project / "hello.txt").read_text() == "Goodbye, world!\n"

    def test_edit_file_old_string_not_found_raises(self, tools, project):
        with pytest.raises(ValueError, match="not found"):
            tools.edit_file(str(project / "hello.txt"), "NONEXISTENT", "replacement")

    def test_edit_file_outside_project_raises(self, tools):
        with pytest.raises(PermissionError, match="outside project root"):
            tools.edit_file("/etc/hosts", "old", "new")


# ---------------------------------------------------------------------------
# bash tests
# ---------------------------------------------------------------------------


class TestBash:
    def test_bash_simple_command(self, tools):
        result = tools.bash("echo hello")
        assert "hello" in result

    def test_bash_respects_timeout(self, tools):
        with pytest.raises(TimeoutError):
            tools.bash("sleep 60", timeout=1)

    def test_bash_returns_stderr_on_failure(self, tools):
        result = tools.bash("ls /nonexistent_dir_xyz 2>&1 || true")
        assert "No such file" in result or "nonexistent" in result.lower()


# ---------------------------------------------------------------------------
# grep tests
# ---------------------------------------------------------------------------


class TestGrep:
    def test_grep_finds_pattern(self, tools, project):
        result = tools.grep("Hello", str(project))
        assert "hello.txt" in result

    def test_grep_relative_path(self, tools):
        result = tools.grep("Hello", ".")
        assert "hello.txt" in result

    def test_grep_outside_project_raises(self, tools):
        with pytest.raises(PermissionError, match="outside project root"):
            tools.grep("root", "/etc")

    def test_grep_no_match_returns_empty(self, tools, project):
        result = tools.grep("ZZZZNONEXISTENT", str(project))
        assert result == "" or "no matches" in result.lower()


# ---------------------------------------------------------------------------
# glob tests
# ---------------------------------------------------------------------------


class TestGlob:
    def test_glob_finds_files(self, tools, project):
        result = tools.glob_files("**/*.py", str(project))
        assert "main.py" in result

    def test_glob_relative_path(self, tools):
        result = tools.glob_files("**/*.txt", ".")
        assert "hello.txt" in result

    def test_glob_outside_project_raises(self, tools):
        with pytest.raises(PermissionError, match="outside project root"):
            tools.glob_files("*.conf", "/etc")


# ---------------------------------------------------------------------------
# Boundary enforcement tests (defense-in-depth)
# ---------------------------------------------------------------------------


class TestBoundaryEnforcement:
    def test_symlink_escape_blocked(self, tools, project):
        """Symlink pointing outside project_root is blocked."""
        escape_target = tempfile.mkdtemp()
        link_path = project / "sneaky_link"
        os.symlink(escape_target, str(link_path))
        with pytest.raises(PermissionError, match="outside project root"):
            tools.read_file(str(link_path / "file.txt"))

    def test_resolve_to_project_root_itself_allowed(self, tools, project):
        """Reading a file at the project root itself is allowed."""
        result = tools.read_file(str(project / "hello.txt"))
        assert "Hello" in result
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_tools.py -v 2>&1 | head -20
```

**Expected:** All tests FAIL with `ModuleNotFoundError: No module named 'tools'`

### Step 3: Create runtime package marker

Create file `runtime/__init__.py`:

```python
"""Standalone runtime scaffold for generated nano-amplifiers.

This package provides the agent loop, tool executor, and CLI for
running a constrained agent without Amplifier installed.

Copied into each generated nano-amplifier's standalone/ directory
at /harness-finish packaging time.
"""
```

### Step 4: Implement the tool executor

Create file `runtime/tools.py`:

```python
"""Standalone tool executor for nano-amplifier agents.

Implements: read_file, write_file, edit_file, bash, grep, glob.
Every tool independently enforces the project_root boundary (defense-in-depth).

Dependencies: stdlib only (subprocess, pathlib, os, fnmatch, re).
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from pathlib import Path


class ToolExecutor:
    """Executes tools within a project_root boundary.

    Every path-accepting method resolves the path against project_root and
    rejects any resolved path that falls outside it. This is defense-in-depth —
    even if the constraint gate is bypassed, tools still enforce boundaries.
    """

    def __init__(self, project_root: str) -> None:
        self._project_root = os.path.realpath(project_root)

    def _resolve_and_check(self, path: str) -> str:
        """Resolve a path and verify it's inside project_root.

        Args:
            path: Absolute or relative path.

        Returns:
            The resolved absolute path.

        Raises:
            PermissionError: If the resolved path is outside project_root.
        """
        if os.path.isabs(path):
            resolved = os.path.realpath(path)
        else:
            resolved = os.path.realpath(os.path.join(self._project_root, path))

        if resolved == self._project_root or resolved.startswith(
            self._project_root + os.sep
        ):
            return resolved

        raise PermissionError(
            f"Path resolves outside project root: {path!r} -> {resolved!r} "
            f"(project_root: {self._project_root!r})"
        )

    # ------------------------------------------------------------------
    # read_file
    # ------------------------------------------------------------------

    def read_file(self, file_path: str) -> str:
        """Read a file's contents.

        Args:
            file_path: Path to read (absolute or relative to project_root).

        Returns:
            File contents as a string.

        Raises:
            PermissionError: Path outside project_root.
            FileNotFoundError: File doesn't exist.
        """
        resolved = self._resolve_and_check(file_path)
        if not os.path.isfile(resolved):
            raise FileNotFoundError(f"File not found: {resolved}")
        with open(resolved) as f:
            return f.read()

    # ------------------------------------------------------------------
    # write_file
    # ------------------------------------------------------------------

    def write_file(self, file_path: str, content: str) -> str:
        """Write content to a file.

        Creates parent directories if needed.

        Args:
            file_path: Path to write (absolute or relative to project_root).
            content: String content to write.

        Returns:
            Confirmation message.

        Raises:
            PermissionError: Path outside project_root.
        """
        resolved = self._resolve_and_check(file_path)
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        with open(resolved, "w") as f:
            f.write(content)
        return f"Wrote {len(content)} bytes to {resolved}"

    # ------------------------------------------------------------------
    # edit_file
    # ------------------------------------------------------------------

    def edit_file(self, file_path: str, old_string: str, new_string: str) -> str:
        """Replace a string in a file.

        Args:
            file_path: Path to edit.
            old_string: Exact string to find and replace.
            new_string: Replacement string.

        Returns:
            Confirmation message.

        Raises:
            PermissionError: Path outside project_root.
            FileNotFoundError: File doesn't exist.
            ValueError: old_string not found in file.
        """
        resolved = self._resolve_and_check(file_path)
        if not os.path.isfile(resolved):
            raise FileNotFoundError(f"File not found: {resolved}")
        with open(resolved) as f:
            content = f.read()
        if old_string not in content:
            raise ValueError(f"String not found in {resolved}: {old_string!r}")
        new_content = content.replace(old_string, new_string, 1)
        with open(resolved, "w") as f:
            f.write(new_content)
        return f"Replaced in {resolved}"

    # ------------------------------------------------------------------
    # bash
    # ------------------------------------------------------------------

    def bash(self, command: str, timeout: int = 30) -> str:
        """Execute a bash command.

        Args:
            command: Shell command string.
            timeout: Max seconds to wait (default 30).

        Returns:
            Combined stdout+stderr output.

        Raises:
            TimeoutError: Command exceeded timeout.
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self._project_root,
            )
            output = result.stdout
            if result.stderr:
                output += result.stderr
            return output
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out after {timeout}s: {command!r}")

    # ------------------------------------------------------------------
    # grep
    # ------------------------------------------------------------------

    def grep(self, pattern: str, path: str) -> str:
        """Search for a regex pattern in files.

        Uses ripgrep if available, falls back to Python re.

        Args:
            pattern: Regex pattern to search for.
            path: Directory or file to search in.

        Returns:
            Matching lines with file:line prefix, or empty string.

        Raises:
            PermissionError: Path outside project_root.
        """
        resolved = self._resolve_and_check(path)

        # Try ripgrep first (fast)
        try:
            result = subprocess.run(
                ["rg", "-n", "--no-heading", pattern, resolved],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout
        except FileNotFoundError:
            pass  # ripgrep not installed, fall back
        except subprocess.TimeoutExpired:
            return ""

        # Python fallback
        regex = re.compile(pattern)
        matches = []
        target = Path(resolved)

        if target.is_file():
            files = [target]
        else:
            files = [f for f in target.rglob("*") if f.is_file()]

        for filepath in files:
            try:
                for lineno, line in enumerate(filepath.read_text().splitlines(), 1):
                    if regex.search(line):
                        rel = filepath.relative_to(resolved) if target.is_dir() else filepath.name
                        matches.append(f"{rel}:{lineno}:{line}")
            except (UnicodeDecodeError, PermissionError):
                continue

        return "\n".join(matches)

    # ------------------------------------------------------------------
    # glob
    # ------------------------------------------------------------------

    def glob_files(self, pattern: str, path: str) -> str:
        """Find files matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., '**/*.py').
            path: Base directory to search from.

        Returns:
            Newline-separated list of matching paths.

        Raises:
            PermissionError: Path outside project_root.
        """
        resolved = self._resolve_and_check(path)
        target = Path(resolved)

        if not target.is_dir():
            return ""

        matches = sorted(str(p.relative_to(resolved)) for p in target.glob(pattern) if p.is_file())
        return "\n".join(matches)


# ---------------------------------------------------------------------------
# Tool dispatch table (used by runtime.py)
# ---------------------------------------------------------------------------

# Maps tool_name -> (method_name, parameter_mapping)
# parameter_mapping: dict of {api_param_name: method_param_name}
TOOL_DISPATCH = {
    "read_file": ("read_file", {"file_path": "file_path"}),
    "write_file": ("write_file", {"file_path": "file_path", "content": "content"}),
    "edit_file": (
        "edit_file",
        {"file_path": "file_path", "old_string": "old_string", "new_string": "new_string"},
    ),
    "bash": ("bash", {"command": "command", "timeout": "timeout"}),
    "grep": ("grep", {"pattern": "pattern", "path": "path"}),
    "glob": ("glob_files", {"pattern": "pattern", "path": "path"}),
}
```

### Step 5: Run tests to verify they pass

```bash
python -m pytest tests/test_tools.py -v
```

**Expected:** All 18 tests PASS.

### Step 6: Run full test suite

```bash
python -m pytest tests/ -v
```

**Expected:** 153 + 18 = 171 total, all PASS.

### Step 7: Commit

```bash
git add runtime/__init__.py runtime/tools.py tests/test_tools.py
git commit -m "feat: add standalone tool executor (runtime/tools.py)

- ToolExecutor class with 6 tools: read_file, write_file, edit_file, bash, grep, glob
- Every tool independently enforces project_root boundary (defense-in-depth)
- bash uses subprocess with configurable timeout
- grep tries ripgrep, falls back to Python re
- TOOL_DISPATCH table for runtime.py integration
- 18 tests covering legal/illegal paths, edge cases"
```

---

## Task 3: Standalone Runtime + Constraint Gate

**What you're building:** `runtime/runtime.py` — the LLM agent loop. Takes user input, sends to LLM via litellm, parses tool calls from the response, gates each tool call through `is_legal_action()`, retries on rejection, dispatches to ToolExecutor on approval.

**Files:**
- Create: `tests/test_runtime.py`
- Create: `runtime/runtime.py`

### Step 1: Write the failing tests

Create file `tests/test_runtime.py`:

```python
"""Tests for the standalone runtime (runtime/runtime.py).

All LLM calls are mocked — these tests verify the constraint gate logic,
retry loop, and conversation management, not the LLM itself.
"""

import os
import sys

import pytest

# Add runtime to path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime"),
)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


# ---------------------------------------------------------------------------
# Mock LLM response helpers
# ---------------------------------------------------------------------------


def make_tool_call_response(tool_name, parameters, call_id="call_001"):
    """Build a mock LLM response that proposes a tool call."""
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": parameters,
                },
            }
        ],
    }


def make_text_response(text):
    """Build a mock LLM response that is plain text (no tool call)."""
    return {
        "role": "assistant",
        "content": text,
        "tool_calls": None,
    }


# ---------------------------------------------------------------------------
# Tests: constraint gate
# ---------------------------------------------------------------------------


class TestConstraintGate:
    """Test the constraint gate that checks actions before dispatch."""

    def test_gate_blocks_illegal_action(self, tmp_path):
        from runtime import ConstraintGate

        gate = ConstraintGate(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py")
        )
        is_legal, reason = gate.check("bash", {"command": "rm -rf /"})
        assert is_legal is False
        assert "rm" in reason.lower()

    def test_gate_passes_legal_action(self, tmp_path):
        from runtime import ConstraintGate

        gate = ConstraintGate(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py")
        )
        is_legal, reason = gate.check("read_file", {"file_path": "src/main.py"})
        assert is_legal is True
        assert reason == ""

    def test_gate_exception_treated_as_deny(self):
        from runtime import ConstraintGate

        gate = ConstraintGate(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py")
        )
        # None tool_name will likely cause an exception in the constraint
        is_legal, reason = gate.check(None, None)
        assert is_legal is False


# ---------------------------------------------------------------------------
# Tests: agent loop
# ---------------------------------------------------------------------------


class TestAgentLoop:
    """Test the agent loop with mocked LLM."""

    def test_retry_on_illegal_action(self, tmp_path):
        """Agent retries when constraint gate blocks an action."""
        from runtime import AgentLoop

        # First call: LLM proposes illegal action
        # Second call: LLM proposes legal action (text response = done)
        call_count = 0
        illegal_response = make_tool_call_response("bash", {"command": "rm -rf /"})
        legal_response = make_text_response("I'll use a different approach.")

        def mock_llm(messages, tools=None, model=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return illegal_response
            return legal_response

        # Create a test file so ToolExecutor has a project
        (tmp_path / "file.txt").write_text("test")

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=3,
            llm_fn=mock_llm,
        )

        result = loop.process_turn("Do something dangerous")
        assert call_count == 2  # retried once
        assert "different approach" in result.lower()

    def test_max_retries_exhaustion(self, tmp_path):
        """Agent gives up after max_retries consecutive rejections."""
        from runtime import AgentLoop

        illegal_response = make_tool_call_response("bash", {"command": "rm -rf /"})

        def mock_llm(messages, tools=None, model=None):
            return illegal_response  # always proposes illegal action

        (tmp_path / "file.txt").write_text("test")

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=2,
            llm_fn=mock_llm,
        )

        result = loop.process_turn("Do something dangerous")
        assert "max retries" in result.lower() or "exhausted" in result.lower()

    def test_legal_tool_call_dispatches_and_returns(self, tmp_path):
        """Legal tool call is dispatched to executor and result returned to LLM."""
        from runtime import AgentLoop

        (tmp_path / "hello.txt").write_text("Hello from test!")

        call_count = 0
        tool_response = make_tool_call_response(
            "read_file",
            {"file_path": str(tmp_path / "hello.txt")},
        )
        final_response = make_text_response("The file says: Hello from test!")

        def mock_llm(messages, tools=None, model=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return tool_response
            return final_response

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=3,
            llm_fn=mock_llm,
        )

        result = loop.process_turn("Read hello.txt")
        assert "Hello from test" in result

    def test_conversation_history_accumulates(self, tmp_path):
        """Each turn adds to conversation history."""
        from runtime import AgentLoop

        (tmp_path / "f.txt").write_text("x")

        def mock_llm(messages, tools=None, model=None):
            return make_text_response(f"Response (history has {len(messages)} messages)")

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=3,
            llm_fn=mock_llm,
        )

        loop.process_turn("First message")
        loop.process_turn("Second message")
        # system + user1 + assistant1 + user2 + assistant2 = 5
        assert len(loop.messages) == 5
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_runtime.py -v 2>&1 | head -20
```

**Expected:** All tests FAIL with `ModuleNotFoundError: No module named 'runtime'`

### Step 3: Implement the runtime

Create file `runtime/runtime.py`:

```python
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
from typing import Any, Callable

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
        self._module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self._module)

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

    def check(self, tool_name: str, parameters: dict) -> tuple[bool, str]:
        """Check whether an action is legal.

        Args:
            tool_name: Name of the tool being called.
            parameters: Tool parameters dict.

        Returns:
            (True, "") for legal actions.
            (False, reason) for illegal actions.
        """
        try:
            if self._signature == "is_legal_action":
                return self._fn(tool_name, parameters)
            else:
                state = {}
                action = {"tool_name": tool_name, "parameters": parameters or {}}
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
                    "new_string": {"type": "string", "description": "Replacement string"},
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
                    "command": {"type": "string", "description": "Shell command to run"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds (default 30)"},
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
                    "path": {"type": "string", "description": "Directory or file to search"},
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
                    "pattern": {"type": "string", "description": "Glob pattern (e.g., **/*.py)"},
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


def _default_llm_fn(messages: list[dict], tools: list | None = None, model: str | None = None) -> dict:
    """Call the LLM via litellm. Imported lazily to avoid import errors in tests."""
    import litellm

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
                    self.messages.append({"role": "assistant", "content": exhaustion_msg})
                    return exhaustion_msg

                # Add rejection to conversation for agent self-correction
                self.messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": response["tool_calls"],
                })
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": (
                        f"REJECTED by constraint gate: {reason}\n"
                        f"Please try a different approach."
                    ),
                })
                continue

            # Legal — dispatch
            result = self._dispatch_tool(tool_name, arguments)

            self.messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": response["tool_calls"],
            })
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": str(result),
            })
            retries = 0  # Reset retry counter after successful dispatch
```

### Step 4: Run tests to verify they pass

```bash
python -m pytest tests/test_runtime.py -v
```

**Expected:** All 7 tests PASS.

### Step 5: Run full test suite

```bash
python -m pytest tests/ -v
```

**Expected:** 171 + 7 = 178 total, all PASS.

### Step 6: Commit

```bash
git add runtime/runtime.py tests/test_runtime.py
git commit -m "feat: add standalone runtime with constraint gate (runtime/runtime.py)

- ConstraintGate: loads constraints.py, checks before dispatch
- AgentLoop: LLM conversation + constraint gate + retry loop
- Retry on rejection with reason injected into conversation
- Max retries exhaustion with clear message
- Tool dispatch via ToolExecutor integration
- litellm for LLM calls (lazy import, mockable for tests)
- 7 tests with mocked LLM covering all gate/retry paths"
```

---

## Task 4: CLI Entry Point + Packaging Templates

**What you're building:** `runtime/cli.py` with three subcommands (`chat`, `check`, `audit`) plus the `pyproject.toml.template` for generating standalone packages.

**Files:**
- Create: `tests/test_cli.py`
- Create: `runtime/cli.py`
- Create: `runtime/pyproject.toml.template`

### Step 1: Write the failing tests

Create file `tests/test_cli.py`:

```python
"""Tests for the standalone CLI (runtime/cli.py).

Tests argument parsing and the check subcommand.
The chat subcommand requires an LLM, so it is not tested here.
"""

import json
import os
import sys
import tempfile

import pytest

# Add runtime to path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime"),
)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


# ---------------------------------------------------------------------------
# Tests: argument parsing
# ---------------------------------------------------------------------------


class TestArgParsing:
    def test_check_subcommand_parses(self):
        from cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["check", "bash", '{"command": "echo hi"}'])
        assert args.subcommand == "check"
        assert args.tool_name == "bash"
        assert args.params_json == '{"command": "echo hi"}'

    def test_chat_subcommand_parses(self):
        from cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["chat"])
        assert args.subcommand == "chat"

    def test_audit_subcommand_parses(self):
        from cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["audit", "transcript.json"])
        assert args.subcommand == "audit"
        assert args.transcript_file == "transcript.json"

    def test_config_flag_parses(self):
        from cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["--config", "my-config.yaml", "chat"])
        assert args.config == "my-config.yaml"


# ---------------------------------------------------------------------------
# Tests: check subcommand
# ---------------------------------------------------------------------------


class TestCheckSubcommand:
    def test_check_legal_action_returns_true(self):
        from cli import run_check

        result = run_check(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            tool_name="read_file",
            params_json='{"file_path": "src/main.py"}',
        )
        assert result[0] is True

    def test_check_illegal_action_returns_false_with_reason(self):
        from cli import run_check

        result = run_check(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            tool_name="bash",
            params_json='{"command": "rm -rf /"}',
        )
        assert result[0] is False
        assert "rm" in result[1].lower()

    def test_check_invalid_json_returns_error(self):
        from cli import run_check

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
        from cli import load_config

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
        from cli import load_config

        config = load_config("/nonexistent/config.yaml")
        assert config["project_root"] == os.getcwd()
        assert config["max_retries"] == 3

    def test_load_system_prompt(self, tmp_path):
        from cli import load_system_prompt

        prompt_file = tmp_path / "system-prompt.md"
        prompt_file.write_text("You are a constrained agent.\n")
        prompt = load_system_prompt(str(prompt_file))
        assert "constrained agent" in prompt

    def test_load_system_prompt_missing_uses_default(self):
        from cli import load_system_prompt

        prompt = load_system_prompt("/nonexistent/system-prompt.md")
        assert len(prompt) > 0  # Returns a non-empty default
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_cli.py -v 2>&1 | head -20
```

**Expected:** All tests FAIL with `ModuleNotFoundError: No module named 'cli'`

### Step 3: Implement the CLI

Create file `runtime/cli.py`:

```python
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
    except (FileNotFoundError, ImportError):
        pass
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

    with open(transcript_path) as f:
        transcript = json.load(f)

    violations = 0
    total = 0

    for entry in transcript:
        if entry.get("tool_calls"):
            for tc in entry["tool_calls"]:
                total += 1
                tool_name = tc["function"]["name"]
                params = json.loads(tc["function"]["arguments"])
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
```

### Step 4: Create the pyproject.toml template

Create file `runtime/pyproject.toml.template`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{{harness_name}}"
version = "0.1.0"
description = "Standalone constrained agent — {{harness_name}}"
requires-python = ">=3.11"
license = "MIT"
dependencies = [
    "litellm>=1.0",
    "pyyaml>=6.0",
]

[project.scripts]
{{harness_name}} = "{{package_name}}.cli:main"
```

### Step 5: Run tests to verify they pass

```bash
python -m pytest tests/test_cli.py -v
```

**Expected:** All 8 tests PASS.

### Step 6: Run full test suite

```bash
python -m pytest tests/ -v
```

**Expected:** 178 + 8 = 186 total, all PASS.

### Step 7: Commit

```bash
git add runtime/cli.py runtime/pyproject.toml.template tests/test_cli.py
git commit -m "feat: add CLI entry point and packaging template (runtime/cli.py)

- Three subcommands: chat (interactive), check (one-shot), audit (transcript)
- Config loading from config.yaml with sensible defaults
- System prompt loading from system-prompt.md with fallback
- pyproject.toml.template with {{harness_name}} variable
- 8 tests covering arg parsing, check validation, config loading"
```

---

## Task 5: Bundle Updates + Docker Templates + Structural Tests

**What you're building:** Update existing bundle files to reflect the new three-stud architecture, add Docker templates for standalone deployment, and extend the structural test suite.

**Files:**
- Modify: `modes/harness-finish.md`
- Modify: `agents/harness-generator.md`
- Modify: `context/harness-format.md`
- Create: `runtime/Dockerfile.template`
- Create: `runtime/docker-compose.template.yaml`
- Modify: `tests/test_scaffold.py`

### Step 1: Update `/harness-finish` mode with 3-stud packaging

Open `modes/harness-finish.md`. Replace the content of **Step 2: Package the Artifact** (the section between `### Step 2: Package the Artifact` and `### Step 3: Summarize the Work`). Here is the complete replacement for that section:

Find and replace this exact block in `modes/harness-finish.md`:

**Find (old Step 2):**
```
### Step 2: Package the Artifact

Package based on artifact tier:

**Tier 1 — Nano-amplifier:**
- Verify 3 files exist: behavior.yaml, constraints.py, context.md
- Validate behavior.yaml parses as YAML
- Run python_check on constraints.py
- Ensure context.md documents all constraints

**Tier 2 — Harness bundle:**
- Verify bundle structure (bundle.md, behaviors/, modules/)
- Validate all YAML files parse
- Run python_check on all Python files

**Tier 3 — Harness machine (.harness-machine/):**
- Verify directory structure
- Validate STATE.yaml, all recipe YAML files
- Check no unsubstituted template variables remain
- Present Docker/cron startup instructions
```

**Replace with (new Step 2):**
```
### Step 2: Package the Artifact — Three Studs

Package based on artifact tier. For Tier 1 nano-amplifiers, assemble all three deployment studs:

**Tier 1 — Nano-amplifier (3 studs):**

**Stud 1: Amplifier hook** — Generate `behavior.yaml` referencing the generic hooks-harness module:
```yaml
hooks:
  - module: hooks-harness
    source: git+https://github.com/michaeljabbour/amplifier-bundle-harness-machine@main#subdirectory=modules/hooks-harness
    config:
      constraints_path: ./constraints.py
      harness_type: action-verifier
      strict: true
```

**Stud 2: Standalone CLI** — Copy `runtime/` scaffold from the harness-machine bundle into `standalone/`:
1. Create `standalone/<package_name>/` from `runtime/` files (cli.py, runtime.py, tools.py, __init__.py)
2. Copy `constraints.py` into the package directory
3. Copy `config.yaml` and `system-prompt.md` into `standalone/`
4. Stamp `pyproject.toml` from `runtime/pyproject.toml.template` with harness name

**Stud 3: Docker (optional)** — Ask: "Do you also want Docker deployment?"
If yes:
1. Create `docker/` directory
2. Stamp `Dockerfile` from `runtime/Dockerfile.template` with harness name
3. Stamp `docker-compose.yaml` from `runtime/docker-compose.template.yaml` with container name

**Verification for all studs:**
- Validate behavior.yaml parses as YAML
- Run `python_check` on constraints.py
- Ensure context.md documents all constraints
- Ensure config.yaml has `project_root`, `model`, `max_retries`
- Ensure system-prompt.md has agent instructions

**Tier 2 — Harness bundle:**
- Verify bundle structure (bundle.md, behaviors/, modules/)
- Validate all YAML files parse
- Run python_check on all Python files

**Tier 3 — Harness machine (.harness-machine/):**
- Verify directory structure
- Validate STATE.yaml, all recipe YAML files
- Check no unsubstituted template variables remain
- Present Docker/cron startup instructions
```

### Step 2: Update harness-generator agent output contract

In `agents/harness-generator.md`, find the section `## Final Response Contract` and replace it.

**Find:**
```
## Final Response Contract

Your response must include:
1. List of files generated with full paths
2. Self-review checklist (all items checked)
3. Summary of constraint functions implemented
4. Any concerns or limitations noted
```

**Replace with:**
```
## Final Response Contract

Your response must include:
1. List of files generated with full paths
2. Self-review checklist (all items checked)
3. Summary of constraint functions implemented
4. Any concerns or limitations noted

### Required Output Files

Every generation must produce these files:

| File | Purpose |
|------|---------|
| `constraints.py` | Constraint logic (is_legal_action / validate_action) |
| `test_constraints.py` | Constraint test suite |
| `behavior.yaml` | Amplifier hook configuration |
| `context.md` | Constraint rationale and limitations |
| `config.yaml` | Project config: `project_root`, `model`, `harness_type`, `max_retries`, `covered_tools` |
| `system-prompt.md` | Agent instructions: mission, scope, what to do when a call is rejected |

### config.yaml Format

```yaml
project_root: /path/to/project  # Resolved at /harness-finish
model: anthropic/claude-sonnet-4-20250514
harness_type: action-verifier
max_retries: 3
covered_tools:
  - read_file
  - write_file
  - edit_file
  - bash
  - grep
  - glob
allowed_env_vars:
  - PATH
  - HOME
```

### system-prompt.md Format

A markdown file with:
- Agent mission (what this agent does)
- Scope rules (what directories/files/commands are in scope)
- Retry instructions (what to do when a tool call is rejected)
- Any environment-specific guidance
```

### Step 3: Update harness-format.md with complete nano-amplifier spec

In `context/harness-format.md`, find the `### Tier 1: Nano-Amplifier (3 files)` section and replace it.

**Find:**
```
### Tier 1: Nano-Amplifier (3 files)

The atomic unit of harness output. Every harness generation produces at minimum a nano-amplifier:

```
my-harness/
  behavior.yaml        # Amplifier behavior: hooks config, mode reference
  constraints.py       # Python: propose_action(), is_legal_action(), validate_action()
  context.md           # Environment description, constraint rationale
```

Any Amplifier bundle can compose a nano-amplifier via `includes:` in its bundle.md.
```

**Replace with:**
```
### Tier 1: Nano-Amplifier (3 studs)

The atomic unit of harness output. Every generation produces a nano-amplifier with one brick (constraints.py) and three deployment studs:

```
my-harness/
  constraints.py           # THE BRICK — generated, unique per harness
  config.yaml              # GENERATED — project_root, harness_type, covered_tools
  context.md               # GENERATED — constraint rationale, limitations
  system-prompt.md         # GENERATED — agent mission, scope, retry instructions
  test_constraints.py      # GENERATED — constraint test suite

  behavior.yaml            # STUD 1: AMPLIFIER — amplifier --bundle ./my-harness

  standalone/              # STUD 2: STANDALONE — cd standalone && pip install -e . && my-harness chat
    pyproject.toml
    my_harness/
      __init__.py
      cli.py
      runtime.py
      tools.py
      constraints.py
    config.yaml
    system-prompt.md

  docker/                  # STUD 3: DOCKER (optional) — cd docker && docker compose up
    Dockerfile
    docker-compose.yaml
```

Three ways to use the same harness:
1. **Amplifier hook:** `amplifier --bundle ./my-harness` — compose into any Amplifier bundle
2. **Standalone CLI:** `cd standalone && pip install -e . && my-harness chat` — zero Amplifier dependency
3. **Docker container:** `cd docker && docker compose up` — isolated execution

Any Amplifier bundle can compose a nano-amplifier via `includes:` in its bundle.md.
```

### Step 4: Create Docker templates

Create file `runtime/Dockerfile.template`:

```dockerfile
# Generated by amplifier-bundle-autoharness — do not edit directly
# Standalone constrained agent: {{harness_name}}
#
# Build:  docker compose build
# Run:    docker compose up
# Shell:  docker compose exec agent bash

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ripgrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the standalone package
COPY standalone/ /app/

# Install the package
RUN pip install --no-cache-dir -e .

# Default to interactive chat
ENTRYPOINT ["{{harness_name}}"]
CMD ["chat"]
```

Create file `runtime/docker-compose.template.yaml`:

```yaml
# Generated by amplifier-bundle-autoharness — do not edit directly
# Standalone constrained agent: {{harness_name}}
#
# Usage:
#   docker compose up        (interactive chat)
#   docker compose run agent check bash '{"command": "echo hi"}'

services:
  agent:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: {{harness_name}}-agent
    network_mode: host
    stdin_open: true
    tty: true
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    volumes:
      - {{project_root}}:{{project_root}}
```

### Step 5: Write the structural tests

Add these two new test classes to `tests/test_scaffold.py`. Append them **after the existing `TestYamlValidity` class** (at the end of the file):

```python


# ---------------------------------------------------------------------------
# Hook module structural tests
# ---------------------------------------------------------------------------


class TestHookModule:
    """Verify the hooks-harness module directory structure."""

    def test_modules_directory_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "modules"))

    def test_hooks_harness_directory_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "modules", "hooks-harness"))

    def test_hooks_harness_pyproject_exists(self):
        path = os.path.join(BUNDLE_ROOT, "modules", "hooks-harness", "pyproject.toml")
        assert os.path.isfile(path)

    def test_hooks_harness_package_directory_exists(self):
        path = os.path.join(
            BUNDLE_ROOT, "modules", "hooks-harness", "amplifier_module_hooks_harness"
        )
        assert os.path.isdir(path)

    def test_hooks_harness_init_exists(self):
        path = os.path.join(
            BUNDLE_ROOT,
            "modules",
            "hooks-harness",
            "amplifier_module_hooks_harness",
            "__init__.py",
        )
        assert os.path.isfile(path)

    def test_hooks_harness_init_exports_mount(self):
        content = _read_file(
            os.path.join(
                "modules",
                "hooks-harness",
                "amplifier_module_hooks_harness",
                "__init__.py",
            )
        )
        assert "async def mount(" in content

    def test_hooks_harness_pyproject_has_entry_point(self):
        content = _read_file(
            os.path.join("modules", "hooks-harness", "pyproject.toml")
        )
        assert "amplifier.modules" in content
        assert "hooks-harness" in content


# ---------------------------------------------------------------------------
# Runtime scaffold structural tests
# ---------------------------------------------------------------------------


class TestRuntime:
    """Verify the runtime/ scaffold directory structure."""

    def test_runtime_directory_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime"))

    def test_runtime_init_exists(self):
        assert os.path.isfile(os.path.join(BUNDLE_ROOT, "runtime", "__init__.py"))

    def test_runtime_py_exists(self):
        assert os.path.isfile(os.path.join(BUNDLE_ROOT, "runtime", "runtime.py"))

    def test_tools_py_exists(self):
        assert os.path.isfile(os.path.join(BUNDLE_ROOT, "runtime", "tools.py"))

    def test_cli_py_exists(self):
        assert os.path.isfile(os.path.join(BUNDLE_ROOT, "runtime", "cli.py"))

    def test_pyproject_template_exists(self):
        assert os.path.isfile(
            os.path.join(BUNDLE_ROOT, "runtime", "pyproject.toml.template")
        )

    def test_dockerfile_template_exists(self):
        assert os.path.isfile(
            os.path.join(BUNDLE_ROOT, "runtime", "Dockerfile.template")
        )

    def test_docker_compose_template_exists(self):
        assert os.path.isfile(
            os.path.join(BUNDLE_ROOT, "runtime", "docker-compose.template.yaml")
        )

    def test_runtime_py_has_constraint_gate(self):
        content = _read_file("runtime/runtime.py")
        assert "class ConstraintGate" in content

    def test_runtime_py_has_agent_loop(self):
        content = _read_file("runtime/runtime.py")
        assert "class AgentLoop" in content

    def test_tools_py_has_tool_executor(self):
        content = _read_file("runtime/tools.py")
        assert "class ToolExecutor" in content

    def test_cli_py_has_main(self):
        content = _read_file("runtime/cli.py")
        assert "def main(" in content

    def test_pyproject_template_has_harness_name_variable(self):
        content = _read_file("runtime/pyproject.toml.template")
        assert "{{harness_name}}" in content

    def test_dockerfile_template_has_harness_name_variable(self):
        content = _read_file("runtime/Dockerfile.template")
        assert "{{harness_name}}" in content
```

### Step 6: Run all tests

```bash
python -m pytest tests/ -v
```

**Expected:** All tests PASS. Previous 186 + ~22 new structural tests = ~208 total.

### Step 7: Commit

```bash
git add modes/harness-finish.md agents/harness-generator.md context/harness-format.md \
       runtime/Dockerfile.template runtime/docker-compose.template.yaml \
       tests/test_scaffold.py
git commit -m "feat: update bundle for 3-stud architecture + Docker templates

- harness-finish.md: 3-stud packaging (amplifier hook, standalone, docker)
- harness-generator.md: config.yaml + system-prompt.md in output contract
- harness-format.md: complete nano-amplifier spec with standalone/ and docker/
- Dockerfile.template + docker-compose.template.yaml for standalone deployment
- 22 new structural tests for modules/ and runtime/ directories"
```

---

## Post-Implementation Checklist

After all 5 tasks are complete, run these final checks:

### Full test suite

```bash
cd /Users/michaeljabbour/dev/amplifier-bundle-autoharness
python -m pytest tests/ -v
```

**Expected:** ~208 tests, all PASS.

### Verify no regressions in existing 139 structural tests

```bash
python -m pytest tests/test_scaffold.py -v
```

**Expected:** 139 original + ~22 new = ~161, all PASS.

### Verify new code passes python_check

```bash
python -m pytest tests/test_hooks_harness.py tests/test_tools.py tests/test_runtime.py tests/test_cli.py -v
```

**Expected:** All behavioral tests PASS.

### Final directory structure

```bash
find modules runtime -type f | sort
```

**Expected output:**
```
modules/hooks-harness/amplifier_module_hooks_harness/__init__.py
modules/hooks-harness/pyproject.toml
runtime/__init__.py
runtime/Dockerfile.template
runtime/cli.py
runtime/docker-compose.template.yaml
runtime/pyproject.toml.template
runtime/runtime.py
runtime/tools.py
```

### Git log should show 5 clean commits

```bash
git log --oneline HEAD~5..HEAD
```

**Expected:** 5 commits, one per task, each with a descriptive message.

---

## File Summary

| File | Lines (est.) | Task | Action |
|------|-------------|------|--------|
| `tests/fixtures/constraints_simple.py` | ~25 | 1 | Create |
| `tests/fixtures/constraints_validate.py` | ~15 | 1 | Create |
| `tests/fixtures/constraints_empty.py` | ~10 | 1 | Create |
| `tests/test_hooks_harness.py` | ~225 | 1 | Create |
| `modules/hooks-harness/pyproject.toml` | ~15 | 1 | Create |
| `modules/hooks-harness/amplifier_module_hooks_harness/__init__.py` | ~175 | 1 | Create |
| `tests/test_tools.py` | ~155 | 2 | Create |
| `runtime/__init__.py` | ~8 | 2 | Create |
| `runtime/tools.py` | ~210 | 2 | Create |
| `tests/test_runtime.py` | ~165 | 3 | Create |
| `runtime/runtime.py` | ~300 | 3 | Create |
| `tests/test_cli.py` | ~100 | 4 | Create |
| `runtime/cli.py` | ~165 | 4 | Create |
| `runtime/pyproject.toml.template` | ~18 | 4 | Create |
| `modes/harness-finish.md` | +40 | 5 | Modify |
| `agents/harness-generator.md` | +35 | 5 | Modify |
| `context/harness-format.md` | +25 | 5 | Modify |
| `runtime/Dockerfile.template` | ~20 | 5 | Create |
| `runtime/docker-compose.template.yaml` | ~20 | 5 | Create |
| `tests/test_scaffold.py` | +75 | 5 | Modify |

**Total new Python:** ~735 lines implementation + ~645 lines tests = ~1,380 lines
**Total new config/template:** ~73 lines
**Total modified:** ~175 lines across 3 existing files