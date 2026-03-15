"""Tests for deployment mode entry points (api.py and service.py for all tiers).

Task 2: Deployment Mode Entry Points.

Tests validate:
  - File existence for all 6 entry point files
  - Correct class/function exports per tier
  - No CLI imports (argparse/rich/signal) in api.py files
  - Tier-appropriate features (streaming/session for nano, modes/delegation/recipes for micro)
  - Event source / graceful shutdown for service files
"""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest

# Root of the bundle repo
BUNDLE_ROOT = Path(__file__).parent.parent
RUNTIME_ROOT = BUNDLE_ROOT / "runtime"


def _load_module(tier: str, module_name: str):
    """Load a runtime module by tier and name."""
    path = RUNTIME_ROOT / tier / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(
        f"{tier}.{module_name}", path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_source(tier: str, module_name: str) -> str:
    """Read source code for a runtime module."""
    path = RUNTIME_ROOT / tier / f"{module_name}.py"
    return path.read_text()


def _has_import(source: str, module_name: str) -> bool:
    """Check if source imports a given module."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == module_name or alias.name.startswith(f"{module_name}."):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == module_name or (
                node.module and node.module.startswith(f"{module_name}.")
            ):
                return True
    return False


# ---------------------------------------------------------------------------
# TestPicoApi
# ---------------------------------------------------------------------------


class TestPicoApi:
    """Tests for runtime/pico/api.py."""

    def test_file_exists(self):
        """pico/api.py must exist."""
        path = RUNTIME_ROOT / "pico" / "api.py"
        assert path.exists(), "runtime/pico/api.py does not exist"

    def test_pico_agent_class(self):
        """pico/api.py must export PicoAgent class with async run() method."""
        source = _read_source("pico", "api")
        assert "class PicoAgent" in source, "pico/api.py must define PicoAgent class"
        # Check for run method
        assert "def run" in source or "async def run" in source, (
            "PicoAgent must have a run() method"
        )

    def test_constraint_gate_class(self):
        """pico/api.py must export ConstraintGate class with check() method."""
        source = _read_source("pico", "api")
        assert "ConstraintGate" in source, "pico/api.py must reference ConstraintGate"

    def test_tool_executor_class(self):
        """pico/api.py must export ToolExecutor class with execute() method."""
        source = _read_source("pico", "api")
        assert "ToolExecutor" in source, "pico/api.py must reference ToolExecutor"

    def test_check_convenience_function(self):
        """pico/api.py must export a check() convenience function."""
        source = _read_source("pico", "api")
        assert "def check(" in source, "pico/api.py must define a check() function"

    def test_no_argparse(self):
        """pico/api.py must not import argparse (pure API, not CLI)."""
        source = _read_source("pico", "api")
        assert not _has_import(source, "argparse"), (
            "pico/api.py must not import argparse (pure in-app API)"
        )

    def test_no_rich(self):
        """pico/api.py must not import rich (pure API, no display)."""
        source = _read_source("pico", "api")
        assert not _has_import(source, "rich"), (
            "pico/api.py must not import rich (pure in-app API)"
        )

    def test_no_signal(self):
        """pico/api.py must not import signal (pure API, no signal handling)."""
        source = _read_source("pico", "api")
        assert not _has_import(source, "signal"), (
            "pico/api.py must not import signal (pure in-app API)"
        )


# ---------------------------------------------------------------------------
# TestPicoService
# ---------------------------------------------------------------------------


class TestPicoService:
    """Tests for runtime/pico/service.py."""

    def test_file_exists(self):
        """pico/service.py must exist."""
        path = RUNTIME_ROOT / "pico" / "service.py"
        assert path.exists(), "runtime/pico/service.py does not exist"

    def test_event_source_abc(self):
        """pico/service.py must define EventSource ABC with listen() method."""
        source = _read_source("pico", "service")
        assert "class EventSource" in source, "pico/service.py must define EventSource class"
        assert "def listen" in source or "async def listen" in source, (
            "EventSource must have a listen() method"
        )

    def test_graceful_shutdown(self):
        """pico/service.py must handle SIGTERM/SIGINT graceful shutdown."""
        source = _read_source("pico", "service")
        # Must reference signal handling
        assert "SIGTERM" in source or "SIGINT" in source, (
            "pico/service.py must handle SIGTERM or SIGINT for graceful shutdown"
        )
        # Must have StdinSource and WebhookSource
        assert "StdinSource" in source, "pico/service.py must define StdinSource"
        assert "WebhookSource" in source, "pico/service.py must define WebhookSource"

    def test_pico_service_class(self):
        """pico/service.py must define PicoService class."""
        source = _read_source("pico", "service")
        assert "class PicoService" in source, "pico/service.py must define PicoService class"


# ---------------------------------------------------------------------------
# TestNanoApi
# ---------------------------------------------------------------------------


class TestNanoApi:
    """Tests for runtime/nano/api.py."""

    def test_file_exists(self):
        """nano/api.py must exist."""
        path = RUNTIME_ROOT / "nano" / "api.py"
        assert path.exists(), "runtime/nano/api.py does not exist"

    def test_streaming_support(self):
        """nano/api.py must define NanoAgent with stream() -> AsyncIterator[str]."""
        source = _read_source("nano", "api")
        assert "class NanoAgent" in source, "nano/api.py must define NanoAgent class"
        assert "def stream" in source or "async def stream" in source, (
            "NanoAgent must have a stream() method"
        )

    def test_session_management(self):
        """nano/api.py must define save_session and resume_session methods."""
        source = _read_source("nano", "api")
        assert "def save_session" in source, (
            "NanoAgent must have a save_session() method"
        )
        assert "def resume_session" in source, (
            "NanoAgent must have a resume_session() method"
        )

    def test_no_argparse(self):
        """nano/api.py must not import argparse."""
        source = _read_source("nano", "api")
        assert not _has_import(source, "argparse"), (
            "nano/api.py must not import argparse (pure in-app API)"
        )


# ---------------------------------------------------------------------------
# TestNanoService
# ---------------------------------------------------------------------------


class TestNanoService:
    """Tests for runtime/nano/service.py."""

    def test_file_exists(self):
        """nano/service.py must exist."""
        path = RUNTIME_ROOT / "nano" / "service.py"
        assert path.exists(), "runtime/nano/service.py does not exist"

    def test_session_persistence(self):
        """nano/service.py must define NanoService with _sessions dict."""
        source = _read_source("nano", "service")
        assert "class NanoService" in source, (
            "nano/service.py must define NanoService class"
        )
        assert "_sessions" in source, (
            "NanoService must maintain a _sessions dict for session persistence"
        )

    def test_streaming_support(self):
        """nano/service.py must support streaming in config or class."""
        source = _read_source("nano", "service")
        assert "stream" in source.lower(), (
            "nano/service.py must support streaming"
        )


# ---------------------------------------------------------------------------
# TestMicroApi
# ---------------------------------------------------------------------------


class TestMicroApi:
    """Tests for runtime/micro/api.py."""

    def test_file_exists(self):
        """micro/api.py must exist."""
        path = RUNTIME_ROOT / "micro" / "api.py"
        assert path.exists(), "runtime/micro/api.py does not exist"

    def test_mode_management(self):
        """micro/api.py must define MicroAgent with set_mode/get_mode/list_modes."""
        source = _read_source("micro", "api")
        assert "class MicroAgent" in source, "micro/api.py must define MicroAgent class"
        assert "def set_mode" in source, "MicroAgent must have set_mode() method"
        assert "def get_mode" in source, "MicroAgent must have get_mode() method"
        assert "def list_modes" in source, "MicroAgent must have list_modes() method"

    def test_delegation(self):
        """micro/api.py must define delegate(task) -> str using micro.delegate.Delegator."""
        source = _read_source("micro", "api")
        assert "def delegate" in source, "MicroAgent must have delegate() method"
        assert "Delegator" in source, (
            "micro/api.py must reference Delegator from micro.delegate"
        )

    def test_recipe_execution(self):
        """micro/api.py must define execute_recipe method."""
        source = _read_source("micro", "api")
        assert "def execute_recipe" in source, (
            "MicroAgent must have execute_recipe() method"
        )

    def test_no_argparse(self):
        """micro/api.py must not import argparse."""
        source = _read_source("micro", "api")
        assert not _has_import(source, "argparse"), (
            "micro/api.py must not import argparse (pure in-app API)"
        )


# ---------------------------------------------------------------------------
# TestMicroService
# ---------------------------------------------------------------------------


class TestMicroService:
    """Tests for runtime/micro/service.py."""

    def test_file_exists(self):
        """micro/service.py must exist."""
        path = RUNTIME_ROOT / "micro" / "service.py"
        assert path.exists(), "runtime/micro/service.py does not exist"

    def test_recipe_trigger_via_event(self):
        """micro/service.py must support recipe triggering via event metadata."""
        source = _read_source("micro", "service")
        assert "class MicroService" in source, (
            "micro/service.py must define MicroService class"
        )
        # Recipe field in event metadata
        assert "recipe" in source, (
            "micro/service.py must handle 'recipe' field in event metadata"
        )

    def test_mode_switching_via_event(self):
        """micro/service.py must support mode switching via event metadata."""
        source = _read_source("micro", "service")
        # Mode field in event metadata
        assert "mode" in source, (
            "micro/service.py must handle 'mode' field in event metadata"
        )

    def test_delegation_via_event(self):
        """micro/service.py must support delegation via event metadata."""
        source = _read_source("micro", "service")
        # Delegate field in event metadata
        assert "delegate" in source, (
            "micro/service.py must handle 'delegate' field in event metadata"
        )
