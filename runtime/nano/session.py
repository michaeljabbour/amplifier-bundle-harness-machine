"""Session persistence for nano runtime.

Provides SessionManager class with JSON file-based session storage in a
.sessions/ directory. Pure JSON files — no external databases required.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------


class SessionManager:
    """JSON file-backed session persistence for nano agent conversations.

    Sessions are stored as JSON files in a ``.sessions/`` directory within
    the harness root.  File naming convention::

        {harness_name}-session-{id}.json

    Each session file contains::

        {
            "session_id": "...",
            "harness_name": "...",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "messages": [...]
        }

    Pure JSON files for portability — no external database required.

    Usage::

        manager = SessionManager("my-harness", sessions_dir=".sessions")
        manager.save("abc123", messages)
        messages = manager.load("abc123")
        sessions = manager.list_sessions()
        manager.delete("abc123")
    """

    def __init__(
        self,
        harness_name: str,
        sessions_dir: str = ".sessions",
    ) -> None:
        """Initialise the SessionManager.

        Args:
            harness_name: Name of the harness (used in file naming).
            sessions_dir: Directory to store session files (default: .sessions).
        """
        self.harness_name = harness_name
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)

    def _session_path(self, session_id: str) -> str:
        """Return the file path for a given session ID.

        Args:
            session_id: Unique session identifier.

        Returns:
            Absolute path to the session JSON file.
        """
        filename = f"{self.harness_name}-session-{session_id}.json"
        return os.path.join(self.sessions_dir, filename)

    def save(self, session_id: str, messages: list[dict[str, Any]]) -> None:
        """Save a session's messages to disk.

        Preserves the ``created_at`` timestamp from any existing session file.
        Updates ``updated_at`` to the current UTC time.

        Args:
            session_id: Unique session identifier.
            messages: List of message dicts to persist.
        """
        path = self._session_path(session_id)
        now = datetime.now(timezone.utc).isoformat()

        # Preserve created_at from existing session
        created_at = now
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    existing = json.load(f)
                created_at = existing.get("created_at", now)
            except (json.JSONDecodeError, OSError):
                pass

        session_data: dict[str, Any] = {
            "session_id": session_id,
            "harness_name": self.harness_name,
            "created_at": created_at,
            "updated_at": now,
            "messages": messages,
        }

        with open(path, "w") as f:
            json.dump(session_data, f, indent=2)

    def load(self, session_id: str) -> list[dict[str, Any]]:
        """Load messages for a given session ID.

        Args:
            session_id: Unique session identifier.

        Returns:
            List of message dicts.

        Raises:
            FileNotFoundError: If the session file does not exist.
        """
        path = self._session_path(session_id)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Session not found: {session_id} (looked at {path})"
            )
        with open(path) as f:
            data = json.load(f)
        return data.get("messages", [])

    def list_sessions(self) -> list[dict[str, Any]]:
        """List all sessions for this harness, sorted by updated_at descending.

        Returns:
            List of session metadata dicts, each containing:
                - ``session_id``
                - ``created_at``
                - ``updated_at``
                - ``message_count``
        """
        results: list[dict[str, Any]] = []
        prefix = f"{self.harness_name}-session-"

        for filename in os.listdir(self.sessions_dir):
            if not filename.startswith(prefix) or not filename.endswith(".json"):
                continue
            path = os.path.join(self.sessions_dir, filename)
            try:
                with open(path) as f:
                    data = json.load(f)
                results.append(
                    {
                        "session_id": data.get("session_id", ""),
                        "created_at": data.get("created_at", ""),
                        "updated_at": data.get("updated_at", ""),
                        "message_count": len(data.get("messages", [])),
                    }
                )
            except (json.JSONDecodeError, OSError):
                continue

        # Sort by updated_at descending (newest first)
        results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return results

    def delete(self, session_id: str) -> bool:
        """Delete a session file.

        Args:
            session_id: Unique session identifier.

        Returns:
            ``True`` if the session was deleted; ``False`` if it didn't exist.
        """
        path = self._session_path(session_id)
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False
