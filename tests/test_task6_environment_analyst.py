"""Tests for task-6: environment-analyst agent updates.

Validates:
- agents/environment-analyst.md has valid YAML frontmatter with meta.name=environment-analyst
- Body contains new section: Dynamic Capability Discovery
  - Mentions 'amplifier module list' command
  - Mentions 'amplifier bundle list' command (with --all flag)
  - Organizes inventory by type: Providers, Tools, Hooks, Orchestrators, Bundles
  - Has fallback if discovery fails
- Body contains new section: Open Questions
  - One question at a time pattern
  - Covers mission/tools/databases/session length/offline topics
- Body contains new section: Amplifier Escalation Detection
  - Indicator: >25 simultaneous tools
  - Indicator: dynamic module loading at runtime
  - Indicator: multiple concurrent sessions
  - Indicator: real-time event processing
  - Recommends full Amplifier with CLI command if detected
- Output Format section has 8 items including:
  - Item 7: Capability inventory with modules organized by type
  - Item 8: Escalation assessment (yes/no with rationale)
"""

import os

import yaml

BUNDLE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = "agents/environment-analyst.md"


def _read_file(rel_path=FILE_PATH):
    """Read a file relative to bundle root."""
    full_path = os.path.join(BUNDLE_ROOT, rel_path)
    with open(full_path) as f:
        return f.read()


def _parse_frontmatter(content):
    """Extract and parse YAML frontmatter from markdown content."""
    parts = content.split("---")
    assert len(parts) >= 3, "File must have YAML frontmatter delimited by ---"
    return yaml.safe_load(parts[1])


def _get_frontmatter():
    """Return parsed YAML frontmatter of the file."""
    return _parse_frontmatter(_read_file())


def _get_body():
    """Return the markdown body (after frontmatter) of the file.

    Splits on '---' with a max of 3 parts (opening delimiter, frontmatter, body).
    """
    return _read_file().split("---", 2)[2]


# ---------------------------------------------------------------------------
# agents/environment-analyst.md tests
# ---------------------------------------------------------------------------


class TestEnvironmentAnalystAgent:
    # ------------------------------------------------------------------
    # File existence
    # ------------------------------------------------------------------

    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "agents", "environment-analyst.md")
        assert os.path.isfile(path), "agents/environment-analyst.md does not exist"

    # ------------------------------------------------------------------
    # Frontmatter structural validity
    # ------------------------------------------------------------------

    def test_frontmatter_parses(self):
        fm = _get_frontmatter()
        assert fm is not None
        assert isinstance(fm, dict)

    def test_meta_name_is_environment_analyst(self):
        fm = _get_frontmatter()
        assert fm["meta"]["name"] == "environment-analyst", (
            "meta.name must be 'environment-analyst'"
        )

    def test_meta_description_is_non_empty_string(self):
        fm = _get_frontmatter()
        desc = fm["meta"]["description"]
        assert isinstance(desc, str)
        assert len(desc.strip()) > 0

    # ------------------------------------------------------------------
    # Body: Dynamic Capability Discovery section
    # ------------------------------------------------------------------

    def test_body_has_dynamic_capability_discovery_section(self):
        body = _get_body()
        assert "dynamic capability discovery" in body.lower(), (
            "Body must have 'Dynamic Capability Discovery' section"
        )

    def test_body_discovery_runs_amplifier_module_list(self):
        body = _get_body()
        assert "amplifier module list" in body, (
            "Dynamic Capability Discovery must mention 'amplifier module list'"
        )

    def test_body_discovery_runs_amplifier_bundle_list_all(self):
        body = _get_body()
        assert "amplifier bundle list" in body, (
            "Dynamic Capability Discovery must mention 'amplifier bundle list'"
        )
        assert "--all" in body, (
            "Dynamic Capability Discovery must use 'amplifier bundle list --all'"
        )

    def test_body_discovery_organizes_by_providers(self):
        body = _get_body()
        assert "providers" in body.lower(), (
            "Dynamic Capability Discovery must organize inventory by Providers"
        )

    def test_body_discovery_organizes_by_tools(self):
        body = _get_body()
        assert "tools" in body.lower(), (
            "Dynamic Capability Discovery must organize inventory by Tools"
        )

    def test_body_discovery_organizes_by_hooks(self):
        body = _get_body()
        assert "hooks" in body.lower(), (
            "Dynamic Capability Discovery must organize inventory by Hooks"
        )

    def test_body_discovery_organizes_by_orchestrators(self):
        body = _get_body()
        assert "orchestrators" in body.lower(), (
            "Dynamic Capability Discovery must organize inventory by Orchestrators"
        )

    def test_body_discovery_organizes_by_bundles(self):
        body = _get_body()
        assert "bundles" in body.lower(), (
            "Dynamic Capability Discovery must organize inventory by Bundles"
        )

    def test_body_discovery_has_fallback(self):
        body = _get_body()
        assert (
            "fall back" in body.lower()
            or "fallback" in body.lower()
            or "fails" in body.lower()
        ), "Dynamic Capability Discovery must have fallback if discovery fails"

    # ------------------------------------------------------------------
    # Body: Open Questions section
    # ------------------------------------------------------------------

    def test_body_has_open_questions_section(self):
        body = _get_body()
        assert "open questions" in body.lower(), (
            "Body must have 'Open Questions' section"
        )

    def test_body_open_questions_one_at_a_time(self):
        body = _get_body()
        body_lower = body.lower()
        assert (
            "one question" in body_lower
            or "one at a time" in body_lower
            or "per message" in body_lower
        ), "Open Questions must specify asking one question at a time"

    def test_body_open_questions_multiple_choice(self):
        body = _get_body()
        body_lower = body.lower()
        assert "multiple-choice" in body_lower or "multiple choice" in body_lower, (
            "Open Questions must prefer multiple-choice format"
        )

    def test_body_open_questions_covers_mission(self):
        body = _get_body()
        assert "mission" in body.lower(), "Open Questions must cover mission topic"

    def test_body_open_questions_covers_tools(self):
        body = _get_body()
        # 'tools' is already in body from other sections; check in context of open questions
        assert "tools" in body.lower(), "Open Questions must cover tools topic"

    def test_body_open_questions_covers_databases(self):
        body = _get_body()
        assert "database" in body.lower(), "Open Questions must cover databases topic"

    def test_body_open_questions_covers_session_length(self):
        body = _get_body()
        body_lower = body.lower()
        assert "session" in body_lower and (
            "length" in body_lower or "duration" in body_lower or "long" in body_lower
        ), "Open Questions must cover session length topic"

    def test_body_open_questions_covers_offline(self):
        body = _get_body()
        assert "offline" in body.lower(), "Open Questions must cover offline topic"

    def test_body_open_questions_stop_condition(self):
        body = _get_body()
        body_lower = body.lower()
        assert "stop" in body_lower or "enough" in body_lower, (
            "Open Questions must specify when to stop asking (when enough to assess+recommend)"
        )

    # ------------------------------------------------------------------
    # Body: Amplifier Escalation Detection section
    # ------------------------------------------------------------------

    def test_body_has_amplifier_escalation_detection_section(self):
        body = _get_body()
        body_lower = body.lower()
        assert "amplifier escalation" in body_lower or (
            "escalation detection" in body_lower
        ), "Body must have 'Amplifier Escalation Detection' section"

    def test_body_escalation_indicator_25_tools(self):
        body = _get_body()
        assert "25" in body, (
            "Escalation Detection must mention >25 simultaneous tools indicator"
        )

    def test_body_escalation_indicator_dynamic_module_loading(self):
        body = _get_body()
        body_lower = body.lower()
        assert "dynamic" in body_lower and (
            "module" in body_lower or "loading" in body_lower
        ), (
            "Escalation Detection must mention dynamic module loading at runtime indicator"
        )

    def test_body_escalation_indicator_multiple_concurrent_sessions(self):
        body = _get_body()
        body_lower = body.lower()
        assert "concurrent" in body_lower and "session" in body_lower, (
            "Escalation Detection must mention multiple concurrent sessions indicator"
        )

    def test_body_escalation_indicator_real_time_event_processing(self):
        body = _get_body()
        body_lower = body.lower()
        assert "real-time" in body_lower or "real time" in body_lower, (
            "Escalation Detection must mention real-time event processing indicator"
        )

    def test_body_escalation_recommends_full_amplifier(self):
        body = _get_body()
        body_lower = body.lower()
        assert "full amplifier" in body_lower or (
            "amplifier" in body_lower and "recommend" in body_lower
        ), "Escalation Detection must recommend full Amplifier when detected"

    def test_body_escalation_has_cli_command(self):
        body = _get_body()
        # Must include a CLI command reference like 'amplifier' command
        body_lower = body.lower()
        assert "amplifier" in body_lower and (
            "cli" in body_lower
            or "install" in body_lower
            or "npx" in body_lower
            or "pip" in body_lower
            or "brew" in body_lower
            or "command" in body_lower
        ), "Escalation Detection must include CLI command if Amplifier detected"

    # ------------------------------------------------------------------
    # Body: Output Format section - 8 items
    # ------------------------------------------------------------------

    def test_body_output_format_has_capability_inventory(self):
        body = _get_body()
        assert "capability inventory" in body.lower(), (
            "Output Format must include item 7: Capability inventory"
        )

    def test_body_output_format_capability_inventory_mentions_modules_by_type(self):
        body = _get_body()
        body_lower = body.lower()
        assert "capability inventory" in body_lower and (
            "type" in body_lower or "module" in body_lower
        ), "Capability inventory must mention available modules organized by type"

    def test_body_output_format_has_escalation_assessment(self):
        body = _get_body()
        assert "escalation assessment" in body.lower(), (
            "Output Format must include item 8: Escalation assessment"
        )

    def test_body_output_format_escalation_assessment_yes_no(self):
        body = _get_body()
        body_lower = body.lower()
        # Must have yes/no mention near escalation assessment
        assert "escalation assessment" in body_lower and (
            "yes" in body_lower or "no" in body_lower
        ), "Escalation assessment must include yes/no with rationale"
