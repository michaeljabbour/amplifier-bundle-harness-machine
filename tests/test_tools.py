"""Tests for the standalone tool executor (runtime/tools.py).

Every tool enforces project_root boundary independently (defense-in-depth).
Tests use a temporary directory as project_root.
"""

import os
import sys
import tempfile

import pytest

# Add runtime/pico to path (pico tier replaced the flat runtime files)
_RUNTIME_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime"
)
sys.path.insert(0, os.path.join(_RUNTIME_DIR, "pico"))
sys.path.insert(0, _RUNTIME_DIR)


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
    """Create a LocalToolExecutor bound to the temp project."""
    from tools import LocalToolExecutor  # type: ignore[import]

    return LocalToolExecutor(project_root=str(project))


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
        result = tools.glob("**/*.py", str(project))
        assert "main.py" in result

    def test_glob_relative_path(self, tools):
        result = tools.glob("**/*.txt", ".")
        assert "hello.txt" in result

    def test_glob_outside_project_raises(self, tools):
        with pytest.raises(PermissionError, match="outside project root"):
            tools.glob("*.conf", "/etc")


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
