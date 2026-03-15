"""Dynamic context loading for nano runtime.

Provides ContextLoader class that resolves @mention references in prompts
and loads file contents as system messages for dynamic context injection.
"""

from __future__ import annotations

import glob as glob_module
import os
import re
from typing import Any

# ---------------------------------------------------------------------------
# @mention regex
# ---------------------------------------------------------------------------

_MENTION_RE = re.compile(r"@([\w./\-*?]+)")


# ---------------------------------------------------------------------------
# ContextLoader
# ---------------------------------------------------------------------------


class ContextLoader:
    """Resolves @mention file references and loads file contents as context.

    Parses ``@path`` references from text and loads the referenced files
    as system messages for dynamic context injection into agent prompts.

    Supports:
    - Single file: ``@src/main.py``
    - Glob pattern: ``@src/**/*.py``
    - Directory: ``@docs/`` (loads all files in directory)

    All resolved paths are verified to be inside ``project_root`` for
    defense-in-depth boundary checking.

    Usage::

        loader = ContextLoader("/path/to/project")
        messages = loader.resolve_mentions("Review @src/main.py and @tests/")
        # Returns list of {role: system, content: ...} messages
    """

    def __init__(self, project_root: str) -> None:
        """Initialise the ContextLoader.

        Args:
            project_root: Root directory to resolve paths relative to and
                enforce as the security boundary.
        """
        self.project_root = os.path.realpath(project_root)

    def resolve_mentions(self, text: str) -> list[dict[str, Any]]:
        """Find @path references in text and load file contents as system messages.

        Args:
            text: Text to scan for @mention references.

        Returns:
            List of ``{role: "system", content: "..."}`` message dicts,
            one per loaded file.  Empty list if no mentions found or no
            files could be loaded.
        """
        mentions = _MENTION_RE.findall(text)
        if not mentions:
            return []

        messages: list[dict[str, Any]] = []
        seen: set[str] = set()

        for mention in mentions:
            paths = self._resolve_paths(mention)
            for path in paths:
                if path in seen:
                    continue
                seen.add(path)
                content = self._read_file(path)
                if content is not None:
                    rel_path = os.path.relpath(path, self.project_root)
                    messages.append(
                        {
                            "role": "system",
                            "content": f"# File: {rel_path}\n\n{content}",
                        }
                    )

        return messages

    def _resolve_paths(self, mention: str) -> list[str]:
        """Resolve a mention string to a list of absolute file paths.

        Handles three cases:
        - Single file (no glob chars, not a directory): returns [path]
        - Glob pattern (contains ``*``, ``?``, ``[``, ``{``): expands glob
        - Directory: returns all files recursively inside the directory

        All resolved paths are filtered through ``_is_inside_root``.

        Args:
            mention: The path string from an @mention (relative to project_root).

        Returns:
            List of absolute file paths that exist and are inside project_root.
        """
        # Determine whether the mention is a glob, directory, or file
        glob_chars = {"*", "?", "[", "{"}

        if any(c in mention for c in glob_chars):
            # Glob pattern
            abs_pattern = os.path.join(self.project_root, mention)
            paths = glob_module.glob(abs_pattern, recursive=True)
            return [p for p in paths if os.path.isfile(p) and self._is_inside_root(p)]

        abs_path = os.path.realpath(os.path.join(self.project_root, mention))

        if os.path.isdir(abs_path):
            # Directory — load all files recursively
            result: list[str] = []
            for dirpath, _dirnames, filenames in os.walk(abs_path):
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname)
                    if self._is_inside_root(fpath):
                        result.append(fpath)
            return sorted(result)

        # Single file
        if os.path.isfile(abs_path) and self._is_inside_root(abs_path):
            return [abs_path]

        return []

    def _is_inside_root(self, path: str) -> bool:
        """Check whether *path* is inside (or equal to) ``project_root``.

        Defense-in-depth boundary check to prevent loading files outside
        the project boundary even when called with crafted paths.

        Args:
            path: Absolute path to check.

        Returns:
            ``True`` if the path is inside ``project_root``; ``False`` otherwise.
        """
        real = os.path.realpath(path)
        return real == self.project_root or real.startswith(self.project_root + os.sep)

    def _read_file(self, path: str) -> str | None:
        """Read a file's contents, handling errors gracefully.

        Args:
            path: Absolute path to the file.

        Returns:
            File contents as a string, or ``None`` if the file could not
            be read (``OSError`` or ``UnicodeDecodeError``).
        """
        try:
            with open(path) as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            return None
