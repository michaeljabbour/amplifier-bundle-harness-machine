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
