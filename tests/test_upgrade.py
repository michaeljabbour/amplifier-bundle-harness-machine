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

import pytest
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
