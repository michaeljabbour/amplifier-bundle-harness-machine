"""Tests for task-3: upgrade-checker agent and check-upgrade recipe.

Validates:
- agents/upgrade-checker.md exists with valid YAML frontmatter
  - meta.name = upgrade-checker
  - meta.description is non-empty
  - body @mentions context/version.md
  - body @mentions context/harness-format.md
  - body references generated_version

- recipes/check-upgrade.yaml exists as valid YAML
  - name = check-upgrade
  - context has target_path field
  - steps reference upgrade-checker agent
"""

import os

import yaml

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_file(rel_path):
    """Read a file relative to bundle root."""
    full_path = os.path.join(BUNDLE_ROOT, rel_path)
    with open(full_path) as f:
        return f.read()


def _parse_frontmatter(content):
    """Extract and parse YAML frontmatter from markdown content."""
    parts = content.split("---")
    assert len(parts) >= 3, "File must have YAML frontmatter delimited by ---"
    return yaml.safe_load(parts[1])


# ---------------------------------------------------------------------------
# agents/upgrade-checker.md tests
# ---------------------------------------------------------------------------


class TestUpgradeCheckerAgent:
    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "agents", "upgrade-checker.md")
        assert os.path.isfile(path), "agents/upgrade-checker.md does not exist"

    def test_has_frontmatter(self):
        content = _read_file("agents/upgrade-checker.md")
        fm = _parse_frontmatter(content)
        assert fm is not None
        assert isinstance(fm, dict)

    def test_name_matches(self):
        fm = _parse_frontmatter(_read_file("agents/upgrade-checker.md"))
        assert fm["meta"]["name"] == "upgrade-checker"

    def test_has_description(self):
        fm = _parse_frontmatter(_read_file("agents/upgrade-checker.md"))
        desc = fm["meta"]["description"]
        assert isinstance(desc, str)
        assert len(desc.strip()) > 0

    def test_mentions_version_md(self):
        content = _read_file("agents/upgrade-checker.md")
        body = content.split("---", 2)[2]
        assert "context/version.md" in body, (
            "Agent body must @mention context/version.md"
        )

    def test_mentions_harness_format_md(self):
        content = _read_file("agents/upgrade-checker.md")
        body = content.split("---", 2)[2]
        assert "context/harness-format.md" in body, (
            "Agent body must @mention context/harness-format.md"
        )

    def test_mentions_generated_version(self):
        content = _read_file("agents/upgrade-checker.md")
        assert "generated_version" in content, (
            "Agent must reference generated_version field"
        )


# ---------------------------------------------------------------------------
# recipes/check-upgrade.yaml tests
# ---------------------------------------------------------------------------


class TestCheckUpgradeRecipe:
    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "recipes", "check-upgrade.yaml")
        assert os.path.isfile(path), "recipes/check-upgrade.yaml does not exist"

    def test_valid_yaml(self):
        content = _read_file("recipes/check-upgrade.yaml")
        parsed = yaml.safe_load(content)
        assert parsed is not None, "recipes/check-upgrade.yaml must be valid YAML"
        assert isinstance(parsed, dict)

    def test_name_matches(self):
        content = _read_file("recipes/check-upgrade.yaml")
        parsed = yaml.safe_load(content)
        assert parsed["name"] == "check-upgrade", (
            f"Recipe name must be 'check-upgrade', got '{parsed.get('name')}'"
        )

    def test_has_target_path_context(self):
        content = _read_file("recipes/check-upgrade.yaml")
        parsed = yaml.safe_load(content)
        assert "context" in parsed, "Recipe must have a context section"
        assert "target_path" in parsed["context"], (
            "Recipe context must include 'target_path' field"
        )

    def test_references_upgrade_checker_agent(self):
        content = _read_file("recipes/check-upgrade.yaml")
        assert "upgrade-checker" in content, (
            "Recipe must reference the upgrade-checker agent"
        )


# ---------------------------------------------------------------------------
# agents/upgrade-planner.md tests
# ---------------------------------------------------------------------------


class TestUpgradePlannerAgent:
    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "agents", "upgrade-planner.md")
        assert os.path.isfile(path), "agents/upgrade-planner.md does not exist"

    def test_has_frontmatter(self):
        content = _read_file("agents/upgrade-planner.md")
        fm = _parse_frontmatter(content)
        assert fm is not None
        assert isinstance(fm, dict)

    def test_name_matches(self):
        fm = _parse_frontmatter(_read_file("agents/upgrade-planner.md"))
        assert fm["meta"]["name"] == "upgrade-planner"

    def test_has_description(self):
        fm = _parse_frontmatter(_read_file("agents/upgrade-planner.md"))
        desc = fm["meta"]["description"]
        assert isinstance(desc, str)
        assert len(desc.strip()) > 0

    def test_mentions_version_md(self):
        content = _read_file("agents/upgrade-planner.md")
        body = content.split("---", 2)[2]
        assert "context/version.md" in body, (
            "Agent body must @mention context/version.md"
        )

    def test_mentions_pattern_md(self):
        content = _read_file("agents/upgrade-planner.md")
        body = content.split("---", 2)[2]
        assert "context/pattern.md" in body, (
            "Agent body must @mention context/pattern.md"
        )


# ---------------------------------------------------------------------------
# recipes/execute-upgrade.yaml tests
# ---------------------------------------------------------------------------


class TestExecuteUpgradeRecipe:
    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "recipes", "execute-upgrade.yaml")
        assert os.path.isfile(path), "recipes/execute-upgrade.yaml does not exist"

    def test_valid_yaml(self):
        content = _read_file("recipes/execute-upgrade.yaml")
        parsed = yaml.safe_load(content)
        assert parsed is not None, "recipes/execute-upgrade.yaml must be valid YAML"
        assert isinstance(parsed, dict)

    def test_name_matches(self):
        content = _read_file("recipes/execute-upgrade.yaml")
        parsed = yaml.safe_load(content)
        assert parsed["name"] == "execute-upgrade", (
            f"Recipe name must be 'execute-upgrade', got '{parsed.get('name')}'"
        )

    def test_has_approval_gate(self):
        content = _read_file("recipes/execute-upgrade.yaml")
        assert "approval" in content, (
            "Recipe must include an approval gate between analysis and execution"
        )

    def test_has_backup_step(self):
        content = _read_file("recipes/execute-upgrade.yaml")
        assert "backup" in content, (
            "Recipe must include a backup step before executing changes"
        )

    def test_has_target_path_context(self):
        content = _read_file("recipes/execute-upgrade.yaml")
        parsed = yaml.safe_load(content)
        assert "context" in parsed, "Recipe must have a context section"
        assert "target_path" in parsed["context"], (
            "Recipe context must include 'target_path' field"
        )

    def test_references_upgrade_planner(self):
        content = _read_file("recipes/execute-upgrade.yaml")
        assert "upgrade-planner" in content, (
            "Recipe must reference the upgrade-planner agent"
        )


# ---------------------------------------------------------------------------
# modes/harness-upgrade.md tests
# ---------------------------------------------------------------------------


class TestHarnessUpgradeMode:
    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "modes", "harness-upgrade.md")
        assert os.path.isfile(path), "modes/harness-upgrade.md does not exist"

    def test_has_frontmatter(self):
        content = _read_file("modes/harness-upgrade.md")
        fm = _parse_frontmatter(content)
        assert fm is not None
        assert isinstance(fm, dict)

    def test_name_matches(self):
        fm = _parse_frontmatter(_read_file("modes/harness-upgrade.md"))
        assert fm["mode"]["name"] == "harness-upgrade"

    def test_has_allowed_transitions(self):
        fm = _parse_frontmatter(_read_file("modes/harness-upgrade.md"))
        transitions = fm["mode"]["allowed_transitions"]
        assert isinstance(transitions, list), "allowed_transitions must be a list"
        assert len(transitions) >= 2, (
            f"must have at least 2 allowed_transitions, got {len(transitions)}"
        )

    def test_default_action_is_block(self):
        fm = _parse_frontmatter(_read_file("modes/harness-upgrade.md"))
        assert fm["mode"]["default_action"] == "block", (
            "Mode default_action must be 'block'"
        )

    def test_has_safe_tools(self):
        fm = _parse_frontmatter(_read_file("modes/harness-upgrade.md"))
        safe_tools = fm["mode"]["tools"]["safe"]
        assert isinstance(safe_tools, list), "tools.safe must be a list"
        assert len(safe_tools) > 0, "tools.safe must contain at least one tool"

    def test_allow_clear_is_false(self):
        fm = _parse_frontmatter(_read_file("modes/harness-upgrade.md"))
        assert fm["mode"]["allow_clear"] is False, "Mode allow_clear must be false"


# ---------------------------------------------------------------------------
# Intent detection tests (nano + micro CLI)
# ---------------------------------------------------------------------------


class TestModeDetection:
    def test_nano_cli_has_intent_detection(self):
        """nano/cli.py must define INTENT_PATTERNS, detect_intent, and
        format_intent_suggestion, and call detect_intent inside cmd_chat."""
        content = _read_file("runtime/nano/cli.py")
        assert "INTENT_PATTERNS" in content, (
            "runtime/nano/cli.py must define INTENT_PATTERNS dict"
        )
        assert "detect_intent" in content, (
            "runtime/nano/cli.py must define detect_intent() function"
        )
        assert "format_intent_suggestion" in content, (
            "runtime/nano/cli.py must define format_intent_suggestion() function"
        )

    def test_micro_cli_has_mode_detection(self):
        """micro/cli.py must define INTENT_PATTERNS with a 'work' keyword pattern
        and include detect_intent/format_intent_suggestion, and call detect_intent
        inside cmd_chat."""
        content = _read_file("runtime/micro/cli.py")
        assert "INTENT_PATTERNS" in content, (
            "runtime/micro/cli.py must define INTENT_PATTERNS dict"
        )
        assert "detect_intent" in content, (
            "runtime/micro/cli.py must define detect_intent() function"
        )
        assert "work" in content, (
            "runtime/micro/cli.py INTENT_PATTERNS must include a 'work' intent pattern"
        )

    def test_micro_cli_has_mode_command(self):
        """/mode command must be handled in micro cli cmd_chat."""
        content = _read_file("runtime/micro/cli.py")
        assert "/mode" in content, (
            "runtime/micro/cli.py must handle the /mode REPL command"
        )
