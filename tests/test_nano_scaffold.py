"""Structural tests for the Nano Runtime Scaffold.

Validates that runtime/nano/ contains exactly 13 files with the required
structural patterns (imports, classes, functions, template vars).

~40 tests across 7 test classes.
"""

from __future__ import annotations

import os

import pytest

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NANO_DIR = os.path.join(BUNDLE_ROOT, "runtime", "nano")


def _read_nano(filename: str) -> str:
    """Read a file from runtime/nano/."""
    path = os.path.join(NANO_DIR, filename)
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# TestNanoFilesExist
# ---------------------------------------------------------------------------

# 9 pico files (copied into nano)
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
]

# 4 nano-specific files
NANO_SPECIFIC_FILES = [
    "streaming.py",
    "session.py",
    "context.py",
    "providers.py",
]

ALL_THIRTEEN = PICO_FILES + NANO_SPECIFIC_FILES


class TestNanoFilesExist:
    @pytest.mark.parametrize("filename", ALL_THIRTEEN)
    def test_nano_file_exists(self, filename):
        path = os.path.join(NANO_DIR, filename)
        assert os.path.isfile(path), f"Missing: runtime/nano/{filename}"

    def test_nano_dir_has_exactly_thirteen_files(self):
        """runtime/nano/ must contain exactly 13 files."""
        files = [
            f for f in os.listdir(NANO_DIR) if os.path.isfile(os.path.join(NANO_DIR, f))
        ]
        assert sorted(files) == sorted(ALL_THIRTEEN), (
            f"Expected {sorted(ALL_THIRTEEN)}, got {sorted(files)}"
        )


# ---------------------------------------------------------------------------
# TestNanoStreaming
# ---------------------------------------------------------------------------


class TestNanoStreaming:
    def test_streaming_has_stream_handler_class(self):
        content = _read_nano("streaming.py")
        assert "class StreamHandler" in content

    def test_streaming_is_async(self):
        content = _read_nano("streaming.py")
        assert "async def" in content or "acompletion" in content

    def test_streaming_processes_chunks_and_deltas(self):
        content = _read_nano("streaming.py")
        # Should process streaming chunks/deltas and accumulate content
        assert "delta" in content or "chunk" in content
        assert "content" in content

    def test_streaming_has_non_stream_fallback(self):
        content = _read_nano("streaming.py")
        # Non-streaming fallback for providers that don't support streaming
        assert "_non_stream_fallback" in content or "stream=False" in content


# ---------------------------------------------------------------------------
# TestNanoSession
# ---------------------------------------------------------------------------


class TestNanoSession:
    def test_session_has_session_manager_class(self):
        content = _read_nano("session.py")
        assert "class SessionManager" in content

    def test_session_can_save_and_load(self):
        content = _read_nano("session.py")
        assert "def save(" in content or "def save\n" in content
        assert "def load(" in content or "def load\n" in content

    def test_session_uses_json_not_sqlite(self):
        content = _read_nano("session.py")
        assert "json" in content.lower()
        assert "sqlite" not in content.lower()

    def test_session_has_list_sessions(self):
        content = _read_nano("session.py")
        assert "list_sessions" in content

    def test_session_uses_dot_sessions_directory(self):
        content = _read_nano("session.py")
        assert ".sessions" in content


# ---------------------------------------------------------------------------
# TestNanoContext
# ---------------------------------------------------------------------------


class TestNanoContext:
    def test_context_has_mention_parsing(self):
        content = _read_nano("context.py")
        # @mention parsing via regex
        assert "_MENTION_RE" in content or "MENTION_RE" in content or "@" in content

    def test_context_loads_file_contents(self):
        content = _read_nano("context.py")
        assert "resolve_mentions" in content or "load" in content.lower()

    def test_context_supports_glob_patterns(self):
        content = _read_nano("context.py")
        assert "glob" in content

    def test_context_has_project_root_reference(self):
        content = _read_nano("context.py")
        assert "project_root" in content


# ---------------------------------------------------------------------------
# TestNanoProviders
# ---------------------------------------------------------------------------


class TestNanoProviders:
    def test_providers_has_provider_manager_class(self):
        content = _read_nano("providers.py")
        assert "class ProviderManager" in content

    def test_providers_has_switching_support(self):
        content = _read_nano("providers.py")
        assert "select_provider" in content or "set_provider" in content

    def test_providers_reads_from_config(self):
        content = _read_nano("providers.py")
        assert "config" in content.lower()

    def test_providers_has_model_attribute(self):
        content = _read_nano("providers.py")
        assert "model" in content

    def test_providers_has_api_key_reference(self):
        content = _read_nano("providers.py")
        assert "api_key" in content


# ---------------------------------------------------------------------------
# TestNanoCli
# ---------------------------------------------------------------------------


class TestNanoCli:
    def test_cli_has_resume_flag(self):
        content = _read_nano("cli.py")
        assert "--resume" in content

    def test_cli_has_provider_command(self):
        content = _read_nano("cli.py")
        assert "/provider" in content or "provider" in content.lower()

    def test_cli_has_stream_flag(self):
        content = _read_nano("cli.py")
        # Either --stream or --no-stream flag
        assert "--stream" in content or "stream" in content.lower()

    def test_cli_still_has_rich(self):
        content = _read_nano("cli.py")
        assert "rich" in content

    def test_cli_still_has_signal_handling(self):
        content = _read_nano("cli.py")
        assert "KeyboardInterrupt" in content or "signal" in content


# ---------------------------------------------------------------------------
# TestNanoRuntime
# ---------------------------------------------------------------------------


class TestNanoRuntime:
    def test_runtime_uses_streaming(self):
        content = _read_nano("runtime.py")
        assert "StreamHandler" in content or "streaming" in content.lower()

    def test_runtime_uses_session(self):
        content = _read_nano("runtime.py")
        assert "SessionManager" in content or "session" in content.lower()

    def test_runtime_uses_context(self):
        content = _read_nano("runtime.py")
        assert "ContextLoader" in content or "context" in content.lower()

    def test_runtime_uses_providers(self):
        content = _read_nano("runtime.py")
        assert "ProviderManager" in content or "providers" in content.lower()

    def test_runtime_still_has_constraint_gate(self):
        content = _read_nano("runtime.py")
        assert "ConstraintGate" in content or "gate" in content

    def test_runtime_still_uses_litellm(self):
        content = _read_nano("runtime.py")
        assert "litellm" in content
