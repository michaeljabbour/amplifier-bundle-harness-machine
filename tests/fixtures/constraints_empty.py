"""Constraints file with neither is_legal_action nor validate_action.

Used to test the error case where mount() can't find a usable function.
"""


def some_unrelated_function():
    return 42
