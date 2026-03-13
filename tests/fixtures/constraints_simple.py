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
