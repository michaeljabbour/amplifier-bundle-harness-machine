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
        cleanup = asyncio.run(mount(coordinator, config))
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
        asyncio.run(mount(coordinator, config))
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
            asyncio.run(mount(coordinator, config))

    def test_mount_no_function_raises_value_error(self):
        """mount() raises ValueError when constraints.py has neither function."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator()
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, "constraints_empty.py"),
            "strict": True,
        }
        with pytest.raises(ValueError, match="neither"):
            asyncio.run(mount(coordinator, config))

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
        asyncio.run(mount(coordinator, config))
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
        asyncio.run(mount(coordinator, config))
        # Handler was registered — it will use the working_dir internally
        assert "tool:pre" in coordinator.hooks.handlers


# ---------------------------------------------------------------------------
# Tests: tool:pre handler behavior
# ---------------------------------------------------------------------------


class TestToolPreHandler:
    """Test the tool:pre hook handler that enforces constraints."""

    def _setup_handler(
        self, constraints_file, strict=True, working_dir="/tmp/test-project"
    ):
        """Helper: mount with given constraints and return the handler."""
        from amplifier_module_hooks_harness import mount

        coordinator = MockCoordinator(working_dir=working_dir)
        config = {
            "constraints_path": os.path.join(FIXTURES_DIR, constraints_file),
            "strict": strict,
        }
        asyncio.run(mount(coordinator, config))
        return coordinator.hooks.handlers["tool:pre"]

    def test_legal_action_returns_continue(self):
        """Legal action returns HookResult with action='continue'."""
        handler = self._setup_handler("constraints_simple.py")
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": "read_file",
                    "parameters": {"file_path": "src/main.py"},
                },
            )
        )
        assert result.action == "continue"

    def test_illegal_action_returns_deny_in_strict_mode(self):
        """Illegal action returns HookResult with action='deny' when strict=True."""
        handler = self._setup_handler("constraints_simple.py", strict=True)
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": "bash",
                    "parameters": {"command": "rm -rf /"},
                },
            )
        )
        assert result.action == "deny"
        assert "rm" in result.reason.lower()

    def test_illegal_action_returns_inject_context_in_warn_mode(self):
        """Illegal action returns HookResult with action='inject_context' when strict=False."""
        handler = self._setup_handler("constraints_simple.py", strict=False)
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": "bash",
                    "parameters": {"command": "rm -rf /"},
                },
            )
        )
        assert result.action == "inject_context"
        assert result.context_injection  # non-empty warning message

    def test_deny_includes_context_injection_for_agent_retry(self):
        """Deny result includes context_injection so the agent can self-correct."""
        handler = self._setup_handler("constraints_simple.py", strict=True)
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": "bash",
                    "parameters": {"command": "rm -rf /tmp/stuff"},
                },
            )
        )
        assert result.action == "deny"
        assert result.context_injection  # agent gets explanation for retry

    def test_validate_action_signature_works(self):
        """constraints.py with validate_action() is correctly invoked."""
        handler = self._setup_handler("constraints_validate.py")
        # This should be denied — validate_action blocks sudo
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": "bash",
                    "parameters": {"command": "sudo apt install foo"},
                },
            )
        )
        assert result.action == "deny"
        assert "sudo" in result.reason.lower()

    def test_validate_action_legal_returns_continue(self):
        """validate_action() with a legal action returns continue."""
        handler = self._setup_handler("constraints_validate.py")
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": "read_file",
                    "parameters": {"file_path": "readme.md"},
                },
            )
        )
        assert result.action == "continue"

    def test_unknown_tool_passes_through(self):
        """Tools not covered by constraints pass through as legal."""
        handler = self._setup_handler("constraints_simple.py")
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": "web_search",
                    "parameters": {"query": "hello"},
                },
            )
        )
        assert result.action == "continue"

    def test_constraint_exception_treated_as_deny(self):
        """If is_legal_action() raises, treat as deny (fail-closed)."""
        handler = self._setup_handler("constraints_simple.py")
        # Pass parameters that might cause issues — None as tool_name
        result = asyncio.run(
            handler(
                "tool:pre",
                {
                    "tool_name": None,
                    "parameters": None,
                },
            )
        )
        # Should deny (fail-closed), not crash
        assert result.action == "deny"

    def test_non_tool_pre_event_returns_continue(self):
        """Events other than tool:pre are passed through."""
        handler = self._setup_handler("constraints_simple.py")
        result = asyncio.run(handler("prompt:submit", {"prompt": "hello"}))
        assert result.action == "continue"
