"""Tests for version infrastructure and deployment mode definitions.

Task 1: Version Infrastructure and Deployment Mode Definitions.

Tests:
  - TestVersionFile: version.md existence, format, consistency across files
  - TestConfigTemplates: config.yaml.template files for each tier
  - TestDeploymentModeDefinitions: harness-format.md deployment modes + version stamping
"""

import re
from pathlib import Path

import pytest
import yaml

# Root of the bundle repo
BUNDLE_ROOT = Path(__file__).parent.parent

EXPECTED_VERSION = "0.2.0"
TIERS = ["pico", "nano", "micro"]

# Mustache-style substitution values for YAML validity check
SUBSTITUTION_VALUES = {
    "harness_name": "test-harness",
    "package_name": "test_harness",
    "tier": "pico",
    "deployment_mode": "standalone",
    "generated_version": "0.2.0",
    "generated_by": "harness-machine",
    "project_root": "/tmp/test",
    "model": "claude-opus-4-5",
}


def substitute_template(content: str) -> str:
    """Replace Mustache-style {{variable}} placeholders with dummy values."""
    result = content
    for key, value in SUBSTITUTION_VALUES.items():
        result = result.replace("{{" + key + "}}", value)
    return result


class TestVersionFile:
    """Tests for context/version.md existence, content, and cross-file consistency."""

    @pytest.fixture(autouse=True)
    def version_file(self):
        self.path = BUNDLE_ROOT / "context" / "version.md"
        self.content = self.path.read_text() if self.path.exists() else ""

    def test_file_exists(self):
        """context/version.md must exist."""
        assert self.path.exists(), "context/version.md does not exist"

    def test_contains_version_number(self):
        """version.md must contain HARNESS_MACHINE_VERSION: 0.2.0."""
        assert (
            f"HARNESS_MACHINE_VERSION: {EXPECTED_VERSION}" in self.content
        ), f"version.md must contain 'HARNESS_MACHINE_VERSION: {EXPECTED_VERSION}'"

    def test_contains_changelog(self):
        """version.md must contain a changelog section."""
        assert (
            "changelog" in self.content.lower() or "## " in self.content
        ), "version.md must contain a changelog section"

    def test_bundle_md_version_matches(self):
        """bundle.md version must be 0.2.0."""
        bundle_path = BUNDLE_ROOT / "bundle.md"
        assert bundle_path.exists(), "bundle.md does not exist"
        content = bundle_path.read_text()
        assert (
            f"version: {EXPECTED_VERSION}" in content
        ), f"bundle.md must contain 'version: {EXPECTED_VERSION}'"

    def test_behavior_yaml_version_matches(self):
        """behaviors/harness-machine.yaml version must be 0.2.0."""
        behavior_path = BUNDLE_ROOT / "behaviors" / "harness-machine.yaml"
        assert behavior_path.exists(), "behaviors/harness-machine.yaml does not exist"
        content = behavior_path.read_text()
        assert (
            f"version: {EXPECTED_VERSION}" in content
        ), f"behaviors/harness-machine.yaml must contain 'version: {EXPECTED_VERSION}'"


class TestConfigTemplates:
    """Tests for runtime/{tier}/config.yaml.template existence and required fields."""

    @pytest.fixture(autouse=True)
    def template_content(self, request):
        tier = request.param if hasattr(request, "param") else None
        if tier:
            path = BUNDLE_ROOT / "runtime" / tier / "config.yaml.template"
            self.tier = tier
            self.path = path
            self.content = path.read_text() if path.exists() else ""

    @pytest.mark.parametrize("tier", TIERS)
    def test_template_exists(self, tier):
        """config.yaml.template must exist for each tier."""
        path = BUNDLE_ROOT / "runtime" / tier / "config.yaml.template"
        assert path.exists(), f"runtime/{tier}/config.yaml.template does not exist"
        # Also validate that after substitution the file is valid YAML
        content = path.read_text()
        substituted = substitute_template(content)
        parsed = yaml.safe_load(substituted)
        assert parsed is not None, f"runtime/{tier}/config.yaml.template is not valid YAML after substitution"

    @pytest.mark.parametrize("tier", TIERS)
    def test_has_generated_version(self, tier):
        """config.yaml.template must contain {{generated_version}} field."""
        path = BUNDLE_ROOT / "runtime" / tier / "config.yaml.template"
        assert path.exists(), f"runtime/{tier}/config.yaml.template does not exist"
        content = path.read_text()
        assert (
            "{{generated_version}}" in content
        ), f"runtime/{tier}/config.yaml.template missing {{{{generated_version}}}} field"

    @pytest.mark.parametrize("tier", TIERS)
    def test_has_generated_by(self, tier):
        """config.yaml.template must contain {{generated_by}} field."""
        path = BUNDLE_ROOT / "runtime" / tier / "config.yaml.template"
        assert path.exists(), f"runtime/{tier}/config.yaml.template does not exist"
        content = path.read_text()
        assert (
            "{{generated_by}}" in content
        ), f"runtime/{tier}/config.yaml.template missing {{{{generated_by}}}} field"

    @pytest.mark.parametrize("tier", TIERS)
    def test_has_deployment_mode(self, tier):
        """config.yaml.template must contain {{deployment_mode}} field."""
        path = BUNDLE_ROOT / "runtime" / tier / "config.yaml.template"
        assert path.exists(), f"runtime/{tier}/config.yaml.template does not exist"
        content = path.read_text()
        assert (
            "{{deployment_mode}}" in content
        ), f"runtime/{tier}/config.yaml.template missing {{{{deployment_mode}}}} field"

    @pytest.mark.parametrize("tier", TIERS)
    def test_has_harness_name(self, tier):
        """config.yaml.template must contain {{harness_name}} field."""
        path = BUNDLE_ROOT / "runtime" / tier / "config.yaml.template"
        assert path.exists(), f"runtime/{tier}/config.yaml.template does not exist"
        content = path.read_text()
        assert (
            "{{harness_name}}" in content
        ), f"runtime/{tier}/config.yaml.template missing {{{{harness_name}}}} field"


class TestDeploymentModeDefinitions:
    """Tests for deployment mode enum and version stamping spec in harness-format.md."""

    @pytest.fixture(autouse=True)
    def harness_format_content(self):
        path = BUNDLE_ROOT / "context" / "harness-format.md"
        assert path.exists(), "context/harness-format.md does not exist"
        self.content = path.read_text()

    def test_has_deployment_mode_section(self):
        """harness-format.md must contain a Deployment Mode section."""
        assert (
            "deployment" in self.content.lower() and "mode" in self.content.lower()
        ), "harness-format.md must contain a deployment mode section"
        # Look for a markdown section header with deployment mode
        assert re.search(
            r"##\s+.*[Dd]eployment\s+[Mm]ode", self.content
        ), "harness-format.md must have a '## Deployment Mode' section header"

    def test_has_standalone_definition(self):
        """harness-format.md must define the 'standalone' deployment mode."""
        assert (
            "standalone" in self.content
        ), "harness-format.md must define 'standalone' deployment mode"

    def test_has_in_app_definition(self):
        """harness-format.md must define the 'in-app' deployment mode."""
        assert (
            "in-app" in self.content
        ), "harness-format.md must define 'in-app' deployment mode"

    def test_has_hybrid_definition(self):
        """harness-format.md must define the 'hybrid' deployment mode."""
        assert (
            "hybrid" in self.content
        ), "harness-format.md must define 'hybrid' deployment mode"

    def test_has_version_stamping_spec(self):
        """harness-format.md must contain a version stamping specification section."""
        assert re.search(
            r"##\s+.*[Vv]ersion\s+[Ss]tamp", self.content
        ), "harness-format.md must have a '## Version Stamp' section header"

    def test_has_generated_by_spec(self):
        """harness-format.md must reference generated_by in version stamping."""
        assert (
            "generated_by" in self.content
        ), "harness-format.md must reference 'generated_by' in version stamping spec"
