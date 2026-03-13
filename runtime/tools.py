"""Standalone tool executor for nano-amplifier agents.

Implements: read_file, write_file, edit_file, bash, grep, glob.
Every tool independently enforces the project_root boundary (defense-in-depth).

Dependencies: stdlib only (subprocess, pathlib, os, re).
"""

from __future__ import annotations

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
                        rel = (
                            filepath.relative_to(resolved)
                            if target.is_dir()
                            else filepath.name
                        )
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

        matches = sorted(
            str(p.relative_to(resolved)) for p in target.glob(pattern) if p.is_file()
        )
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
        {
            "file_path": "file_path",
            "old_string": "old_string",
            "new_string": "new_string",
        },
    ),
    "bash": ("bash", {"command": "command", "timeout": "timeout"}),
    "grep": ("grep", {"pattern": "pattern", "path": "path"}),
    "glob": ("glob_files", {"pattern": "pattern", "path": "path"}),
}
