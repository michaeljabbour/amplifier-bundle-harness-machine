"""Tests for task-8: update 7 mode files and 3 context files for tier awareness.

Validates:
- modes/harness-explore.md: 7-item todo checklist, 3 agent delegations
  (environment-analyst, mission-architect, capability-advisor), Phase 3a/3b/3c,
  Phase 4 with capability picker + name approval + Amplifier escalation warning.
- modes/harness-spec.md: Phase 0 before Phase 1, Phase 5 includes
  tier/mission/name/capabilities/bash_constraints.
- modes/harness-plan.md: '## Plan Shape by Tier' before '## Plan Shape by Scale',
  tier table with pico=simple, nano=medium+extra config files, micro=complex+mode defs.
- modes/harness-execute.md: Stage 1 delegate instruction includes Tier,
  Capability selections, Mission statement, System prompt draft.
- modes/harness-verify.md: '### mini-amplifier CLI (all tiers)' section after
  '### factory' with 6 numbered checks.
- modes/harness-finish.md: tier-aware scaffold table (pico/nano/micro file counts),
  setup.sh generation, Step 3 presents name/tier/tools/provider/artifact path.
- modes/harness-debug.md: Failure Mode 5 with tier-specific feature troubleshooting
  table covering streaming/session/provider/context/mode/recipes/delegation/approval.
- context/instructions.md: Three Size Tiers, Dynamic Discovery, Mission Naming
  sections before ## Two-Track UX; 'build me an agent'/'mini-amplifier' triggers.
- context/harness-format.md: Size Tiers table before 'Tier 1: Nano-Amplifier'.
- context/pattern.md: Three-Tier Architecture before '## Seven Components'.

All 7 mode files must have valid YAML frontmatter with mode.name and mode.tools.safe.
"""

import os
import re

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


def _get_body(rel_path):
    """Return the markdown body (after frontmatter) of a file."""
    return _read_file(rel_path).split("---", 2)[2]


# ---------------------------------------------------------------------------
# Mode file frontmatter validity (all 7 modes)
# ---------------------------------------------------------------------------

MODE_FILES = {
    "harness-explore": "modes/harness-explore.md",
    "harness-spec": "modes/harness-spec.md",
    "harness-plan": "modes/harness-plan.md",
    "harness-execute": "modes/harness-execute.md",
    "harness-verify": "modes/harness-verify.md",
    "harness-finish": "modes/harness-finish.md",
    "harness-debug": "modes/harness-debug.md",
}


class TestAllModeFrontmatterValid:
    """All 7 mode files must have valid YAML frontmatter with mode.name and mode.tools.safe."""

    def test_harness_explore_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("modes/harness-explore.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_spec_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("modes/harness-spec.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_plan_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("modes/harness-plan.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_execute_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("modes/harness-execute.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_verify_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("modes/harness-verify.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_finish_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("modes/harness-finish.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_debug_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("modes/harness-debug.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_explore_has_mode_name(self):
        fm = _parse_frontmatter(_read_file("modes/harness-explore.md"))
        assert fm["mode"]["name"] == "harness-explore"

    def test_harness_spec_has_mode_name(self):
        fm = _parse_frontmatter(_read_file("modes/harness-spec.md"))
        assert fm["mode"]["name"] == "harness-spec"

    def test_harness_plan_has_mode_name(self):
        fm = _parse_frontmatter(_read_file("modes/harness-plan.md"))
        assert fm["mode"]["name"] == "harness-plan"

    def test_harness_execute_has_mode_name(self):
        fm = _parse_frontmatter(_read_file("modes/harness-execute.md"))
        assert fm["mode"]["name"] == "harness-execute"

    def test_harness_verify_has_mode_name(self):
        fm = _parse_frontmatter(_read_file("modes/harness-verify.md"))
        assert fm["mode"]["name"] == "harness-verify"

    def test_harness_finish_has_mode_name(self):
        fm = _parse_frontmatter(_read_file("modes/harness-finish.md"))
        assert fm["mode"]["name"] == "harness-finish"

    def test_harness_debug_has_mode_name(self):
        fm = _parse_frontmatter(_read_file("modes/harness-debug.md"))
        assert fm["mode"]["name"] == "harness-debug"

    def test_harness_explore_has_tools_safe(self):
        fm = _parse_frontmatter(_read_file("modes/harness-explore.md"))
        assert isinstance(fm["mode"]["tools"]["safe"], list)
        assert len(fm["mode"]["tools"]["safe"]) > 0

    def test_harness_spec_has_tools_safe(self):
        fm = _parse_frontmatter(_read_file("modes/harness-spec.md"))
        assert isinstance(fm["mode"]["tools"]["safe"], list)
        assert len(fm["mode"]["tools"]["safe"]) > 0

    def test_harness_plan_has_tools_safe(self):
        fm = _parse_frontmatter(_read_file("modes/harness-plan.md"))
        assert isinstance(fm["mode"]["tools"]["safe"], list)
        assert len(fm["mode"]["tools"]["safe"]) > 0

    def test_harness_execute_has_tools_safe(self):
        fm = _parse_frontmatter(_read_file("modes/harness-execute.md"))
        assert isinstance(fm["mode"]["tools"]["safe"], list)
        assert len(fm["mode"]["tools"]["safe"]) > 0

    def test_harness_verify_has_tools_safe(self):
        fm = _parse_frontmatter(_read_file("modes/harness-verify.md"))
        assert isinstance(fm["mode"]["tools"]["safe"], list)
        assert len(fm["mode"]["tools"]["safe"]) > 0

    def test_harness_finish_has_tools_safe(self):
        fm = _parse_frontmatter(_read_file("modes/harness-finish.md"))
        assert isinstance(fm["mode"]["tools"]["safe"], list)
        assert len(fm["mode"]["tools"]["safe"]) > 0

    def test_harness_debug_has_tools_safe(self):
        fm = _parse_frontmatter(_read_file("modes/harness-debug.md"))
        assert isinstance(fm["mode"]["tools"]["safe"], list)
        assert len(fm["mode"]["tools"]["safe"]) > 0


# ---------------------------------------------------------------------------
# harness-explore.md tests
# ---------------------------------------------------------------------------


class TestHarnessExploreUpdated:
    """harness-explore.md must have 8-item checklist and 3 agent delegations."""

    def test_todo_checklist_has_8_items(self):
        body = _get_body("modes/harness-explore.md")
        # Find the todo checklist section
        checklist_items = re.findall(r"^- \[ \]", body, re.MULTILINE)
        assert len(checklist_items) == 8, (
            f"Todo checklist must have exactly 8 items, found {len(checklist_items)}"
        )

    def test_checklist_mentions_build_mission(self):
        body = _get_body("modes/harness-explore.md")
        assert "BUILD" in body or "build" in body.lower(), (
            "Checklist must include 'understand BUILD mission' item"
        )
        assert "mission" in body.lower(), "Checklist must mention mission"

    def test_checklist_has_clarifying_questions_like_brainstorm(self):
        body = _get_body("modes/harness-explore.md")
        assert "brainstorm" in body.lower() or "clarifying" in body.lower(), (
            "Checklist must mention clarifying questions like brainstorm"
        )

    def test_has_environment_analyst_delegation(self):
        body = _get_body("modes/harness-explore.md")
        assert "environment-analyst" in body, (
            "Must delegate to environment-analyst agent"
        )

    def test_has_mission_architect_delegation(self):
        body = _get_body("modes/harness-explore.md")
        assert "mission-architect" in body, (
            "Must have delegation to mission-architect for naming"
        )

    def test_has_capability_advisor_delegation(self):
        body = _get_body("modes/harness-explore.md")
        assert "capability-advisor" in body, (
            "Must have delegation to capability-advisor for tier/tools/provider"
        )

    def test_has_phase_3a_environment_analysis(self):
        body = _get_body("modes/harness-explore.md")
        assert "3a" in body or "Phase 3a" in body or "3a." in body, (
            "Must have Phase 3a for environment analysis with dynamic discovery"
        )

    def test_has_phase_3b_mission_naming(self):
        body = _get_body("modes/harness-explore.md")
        assert "3b" in body or "Phase 3b" in body, (
            "Must have Phase 3b for mission naming delegation"
        )

    def test_has_phase_3c_capability_recommendation(self):
        body = _get_body("modes/harness-explore.md")
        assert "3c" in body or "Phase 3c" in body, (
            "Must have Phase 3c for capability recommendation delegation"
        )

    def test_phase_4_has_capability_picker(self):
        body = _get_body("modes/harness-explore.md")
        idx_phase4 = body.find("Phase 4")
        assert idx_phase4 != -1, "Must have Phase 4"
        section = body[idx_phase4 : idx_phase4 + 2000]
        assert "capability" in section.lower() and (
            "picker" in section.lower() or "pick" in section.lower()
        ), "Phase 4 must present capability picker"

    def test_phase_4_has_proposed_name(self):
        body = _get_body("modes/harness-explore.md")
        idx_phase4 = body.find("Phase 4")
        assert idx_phase4 != -1
        section = body[idx_phase4 : idx_phase4 + 2000]
        assert "name" in section.lower(), "Phase 4 must present proposed name"

    def test_phase_4_has_recommended_tier(self):
        body = _get_body("modes/harness-explore.md")
        idx_phase4 = body.find("Phase 4")
        assert idx_phase4 != -1
        section = body[idx_phase4 : idx_phase4 + 2000]
        assert "tier" in section.lower(), "Phase 4 must present recommended tier"

    def test_phase_4_has_amplifier_escalation_warning(self):
        body = _get_body("modes/harness-explore.md")
        idx_phase4 = body.find("Phase 4")
        assert idx_phase4 != -1
        section = body[idx_phase4 : idx_phase4 + 2000]
        assert "amplifier" in section.lower() and (
            "escalation" in section.lower() or "warning" in section.lower()
        ), "Phase 4 must have Amplifier escalation warning if detected"

    def test_phase_4_has_user_approves_name(self):
        body = _get_body("modes/harness-explore.md")
        idx_phase4 = body.find("Phase 4")
        assert idx_phase4 != -1
        section = body[idx_phase4 : idx_phase4 + 2000]
        assert "approv" in section.lower() or "confirm" in section.lower(), (
            "Phase 4 must have user reviewing picker and approving name"
        )

    def test_phase_4_has_blockers(self):
        body = _get_body("modes/harness-explore.md")
        idx_phase4 = body.find("Phase 4")
        assert idx_phase4 != -1
        section = body[idx_phase4 : idx_phase4 + 2000]
        assert "blocker" in section.lower(), "Phase 4 must mention blockers"


# ---------------------------------------------------------------------------
# harness-spec.md tests
# ---------------------------------------------------------------------------


class TestHarnessSpecPhase0:
    """harness-spec.md must have Phase 0 before Phase 1."""

    def test_has_phase_0_heading(self):
        body = _get_body("modes/harness-spec.md")
        assert "### Phase 0: Confirm Tier and Name" in body, (
            "Must have '### Phase 0: Confirm Tier and Name' heading"
        )

    def test_phase_0_before_phase_1(self):
        body = _get_body("modes/harness-spec.md")
        idx_phase0 = body.find("### Phase 0: Confirm Tier and Name")
        idx_phase1 = body.find("### Phase 1: Choose Harness Type")
        assert idx_phase0 != -1, "Must have Phase 0"
        assert idx_phase1 != -1, "Must have Phase 1"
        assert idx_phase0 < idx_phase1, "Phase 0 must come before Phase 1"

    def test_phase_0_mentions_tier(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 0: Confirm Tier and Name")
        section = body[idx : idx + 1000]
        assert "tier" in section.lower(), "Phase 0 must confirm tier"

    def test_phase_0_mentions_name(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 0: Confirm Tier and Name")
        section = body[idx : idx + 1000]
        assert "name" in section.lower(), "Phase 0 must confirm name"

    def test_phase_0_handles_skipped_explore(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 0: Confirm Tier and Name")
        section = body[idx : idx + 1500]
        assert "skip" in section.lower() or "gather" in section.lower(), (
            "Phase 0 must handle case where /harness-explore was skipped"
        )

    def test_phase_5_delegate_includes_tier(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 5")
        assert idx != -1, "Must have Phase 5"
        section = body[idx : idx + 1500]
        assert "tier" in section.lower(), (
            "Phase 5 delegate instruction must include tier"
        )

    def test_phase_5_delegate_includes_mission(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 5")
        section = body[idx : idx + 1500]
        assert "mission" in section.lower(), (
            "Phase 5 delegate instruction must include mission"
        )

    def test_phase_5_delegate_includes_name(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 5")
        section = body[idx : idx + 1500]
        assert "name" in section.lower(), (
            "Phase 5 delegate instruction must include name"
        )

    def test_phase_5_delegate_includes_capabilities(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 5")
        section = body[idx : idx + 1500]
        assert "capabilities" in section.lower() or "capability" in section.lower(), (
            "Phase 5 delegate instruction must include capabilities"
        )

    def test_phase_5_delegate_includes_bash_constraints(self):
        body = _get_body("modes/harness-spec.md")
        idx = body.find("### Phase 5")
        section = body[idx : idx + 1500]
        assert "bash_constraints" in section or "bash constraints" in section.lower(), (
            "Phase 5 delegate instruction must include bash_constraints"
        )


# ---------------------------------------------------------------------------
# harness-plan.md tests
# ---------------------------------------------------------------------------


class TestHarnessPlanTierShape:
    """harness-plan.md must have Plan Shape by Tier before Plan Shape by Scale."""

    def test_has_plan_shape_by_tier_heading(self):
        body = _get_body("modes/harness-plan.md")
        assert "## Plan Shape by Tier" in body, (
            "Must have '## Plan Shape by Tier' heading"
        )

    def test_plan_shape_by_tier_before_plan_shape_by_scale(self):
        body = _get_body("modes/harness-plan.md")
        idx_tier = body.find("## Plan Shape by Tier")
        idx_scale = body.find("## Plan Shape by Scale")
        assert idx_tier != -1, "Must have '## Plan Shape by Tier'"
        assert idx_scale != -1, "Must still have '## Plan Shape by Scale'"
        assert idx_tier < idx_scale, (
            "'## Plan Shape by Tier' must come before '## Plan Shape by Scale'"
        )

    def test_tier_table_has_pico_simple(self):
        body = _get_body("modes/harness-plan.md")
        idx = body.find("## Plan Shape by Tier")
        section = body[idx : idx + 2000]
        assert "pico" in section.lower(), "Tier table must include pico"
        assert "simple" in section.lower(), "Pico tier must be described as simple"

    def test_tier_table_has_nano_medium(self):
        body = _get_body("modes/harness-plan.md")
        idx = body.find("## Plan Shape by Tier")
        section = body[idx : idx + 2000]
        assert "nano" in section.lower(), "Tier table must include nano"
        assert "medium" in section.lower(), "Nano tier must be described as medium"

    def test_tier_table_nano_has_extra_config_files(self):
        body = _get_body("modes/harness-plan.md")
        idx = body.find("## Plan Shape by Tier")
        section = body[idx : idx + 2000]
        # nano = medium + 4 extra config files
        assert "4" in section, "Nano tier table must mention 4 extra config files"

    def test_tier_table_has_micro_complex(self):
        body = _get_body("modes/harness-plan.md")
        idx = body.find("## Plan Shape by Tier")
        section = body[idx : idx + 2000]
        assert "micro" in section.lower(), "Tier table must include micro"
        assert "complex" in section.lower(), "Micro tier must be described as complex"

    def test_tier_table_micro_has_mode_definitions(self):
        body = _get_body("modes/harness-plan.md")
        idx = body.find("## Plan Shape by Tier")
        section = body[idx : idx + 2000]
        assert "mode" in section.lower(), "Micro tier must mention mode definitions"

    def test_tier_table_micro_has_extra_config_files(self):
        body = _get_body("modes/harness-plan.md")
        idx = body.find("## Plan Shape by Tier")
        section = body[idx : idx + 2000]
        # micro = complex + 5 extra config files + mode definitions
        assert "5" in section, "Micro tier table must mention 5 extra config files"


# ---------------------------------------------------------------------------
# harness-execute.md tests
# ---------------------------------------------------------------------------


class TestHarnessExecuteStage1Updated:
    """harness-execute.md Stage 1 must include tier, capabilities, mission, system prompt draft."""

    def test_stage_1_delegate_includes_tier(self):
        body = _get_body("modes/harness-execute.md")
        idx = body.find("### Stage 1")
        assert idx != -1, "Must have Stage 1 section"
        section = body[idx : idx + 1500]
        assert "tier" in section.lower() or "Tier" in section, (
            "Stage 1 delegate instruction must include Tier field"
        )

    def test_stage_1_delegate_includes_capability_selections(self):
        body = _get_body("modes/harness-execute.md")
        idx = body.find("### Stage 1")
        section = body[idx : idx + 1500]
        assert "capability" in section.lower() or "Capability" in section, (
            "Stage 1 delegate instruction must include Capability selections"
        )

    def test_stage_1_delegate_includes_mission_statement(self):
        body = _get_body("modes/harness-execute.md")
        idx = body.find("### Stage 1")
        section = body[idx : idx + 1500]
        assert "mission" in section.lower() or "Mission" in section, (
            "Stage 1 delegate instruction must include Mission statement"
        )

    def test_stage_1_delegate_includes_system_prompt_draft(self):
        body = _get_body("modes/harness-execute.md")
        idx = body.find("### Stage 1")
        section = body[idx : idx + 1500]
        assert "system prompt" in section.lower() or "System prompt" in section, (
            "Stage 1 delegate instruction must include System prompt draft"
        )


# ---------------------------------------------------------------------------
# harness-verify.md tests
# ---------------------------------------------------------------------------


class TestHarnessVerifyCLISection:
    """harness-verify.md must have mini-amplifier CLI section after factory."""

    def test_has_mini_amplifier_cli_section(self):
        body = _get_body("modes/harness-verify.md")
        assert "### mini-amplifier CLI (all tiers)" in body, (
            "Must have '### mini-amplifier CLI (all tiers)' section"
        )

    def test_cli_section_after_factory(self):
        body = _get_body("modes/harness-verify.md")
        idx_factory = body.find("### factory")
        idx_cli = body.find("### mini-amplifier CLI (all tiers)")
        assert idx_factory != -1, "Must have '### factory' section"
        assert idx_cli != -1, "Must have '### mini-amplifier CLI (all tiers)' section"
        assert idx_cli > idx_factory, (
            "CLI section must come after '### factory' section"
        )

    def test_cli_section_has_cli_starts_check(self):
        body = _get_body("modes/harness-verify.md")
        idx = body.find("### mini-amplifier CLI (all tiers)")
        assert idx != -1
        idx_end = body.find("\n###", idx + 1)
        section = body[idx : idx_end if idx_end != -1 else idx + 2000]
        assert "cli" in section.lower() and (
            "start" in section.lower() or "check" in section.lower()
        ), "Check 1: CLI starts"

    def test_cli_section_has_chat_mode_check(self):
        body = _get_body("modes/harness-verify.md")
        idx = body.find("### mini-amplifier CLI (all tiers)")
        idx_end = body.find("\n###", idx + 1)
        section = body[idx : idx_end if idx_end != -1 else idx + 2000]
        assert "chat" in section.lower(), "Check 2: chat mode initializes"

    def test_cli_section_has_system_prompt_check(self):
        body = _get_body("modes/harness-verify.md")
        idx = body.find("### mini-amplifier CLI (all tiers)")
        idx_end = body.find("\n###", idx + 1)
        section = body[idx : idx_end if idx_end != -1 else idx + 2000]
        assert "system prompt" in section.lower(), (
            "Check 3: system prompt matches capabilities"
        )

    def test_cli_section_has_config_check(self):
        body = _get_body("modes/harness-verify.md")
        idx = body.find("### mini-amplifier CLI (all tiers)")
        idx_end = body.find("\n###", idx + 1)
        section = body[idx : idx_end if idx_end != -1 else idx + 2000]
        assert "config" in section.lower(), "Check 4: config loads"

    def test_cli_section_has_tools_check(self):
        body = _get_body("modes/harness-verify.md")
        idx = body.find("### mini-amplifier CLI (all tiers)")
        idx_end = body.find("\n###", idx + 1)
        section = body[idx : idx_end if idx_end != -1 else idx + 2000]
        assert "tool" in section.lower(), "Check 5: tools functional"

    def test_cli_section_has_hook_check(self):
        body = _get_body("modes/harness-verify.md")
        idx = body.find("### mini-amplifier CLI (all tiers)")
        idx_end = body.find("\n###", idx + 1)
        section = body[idx : idx_end if idx_end != -1 else idx + 2000]
        assert "hook" in section.lower(), "Check 6: hook loads"

    def test_cli_section_has_6_checks(self):
        body = _get_body("modes/harness-verify.md")
        idx = body.find("### mini-amplifier CLI (all tiers)")
        assert idx != -1
        idx_end = body.find("\n###", idx + 1)
        section = body[idx : idx_end if idx_end != -1 else idx + 2000]
        numbered = re.findall(r"^\s*\d+\.", section, re.MULTILINE)
        assert len(numbered) >= 6, (
            f"CLI section must have at least 6 numbered checks, found {len(numbered)}"
        )


# ---------------------------------------------------------------------------
# harness-finish.md tests
# ---------------------------------------------------------------------------


class TestHarnessFinishTierAwareScaffold:
    """harness-finish.md must have tier-aware scaffold table and updated Step 3."""

    def test_has_tier_aware_scaffold_table(self):
        body = _get_body("modes/harness-finish.md")
        assert "pico" in body.lower(), "Must have pico in scaffold table"
        assert "nano" in body.lower(), "Must have nano in scaffold table"
        assert "micro" in body.lower(), "Must have micro in scaffold table"

    def test_pico_has_9_files(self):
        body = _get_body("modes/harness-finish.md")
        # pico = 9 files in scaffold table
        assert "9" in body, "Pico tier must show 9 files in scaffold table"

    def test_nano_has_13_files(self):
        body = _get_body("modes/harness-finish.md")
        # nano = 13 files
        assert "13" in body, "Nano tier must show 13 files in scaffold table"

    def test_micro_has_18_files(self):
        body = _get_body("modes/harness-finish.md")
        # micro = 18 files
        assert "18" in body, "Micro tier must show 18 files in scaffold table"

    def test_has_setup_sh_generation(self):
        body = _get_body("modes/harness-finish.md")
        assert "setup.sh" in body, (
            "Must reference setup.sh generation from tier template"
        )

    def test_step_3_presents_name(self):
        body = _get_body("modes/harness-finish.md")
        idx = body.find("Step 3") if "Step 3" in body else body.find("### Step 3")
        assert idx != -1, "Must have Step 3"
        section = body[idx : idx + 1000]
        assert "name" in section.lower(), "Step 3 must present meaningful name"

    def test_step_3_presents_tier(self):
        body = _get_body("modes/harness-finish.md")
        idx = body.find("Step 3") if "Step 3" in body else body.find("### Step 3")
        section = body[idx : idx + 1000]
        assert "tier" in section.lower(), "Step 3 must present tier"

    def test_step_3_presents_tools(self):
        body = _get_body("modes/harness-finish.md")
        idx = body.find("Step 3") if "Step 3" in body else body.find("### Step 3")
        section = body[idx : idx + 1000]
        assert "tool" in section.lower(), "Step 3 must present tools"

    def test_step_3_presents_provider(self):
        body = _get_body("modes/harness-finish.md")
        idx = body.find("Step 3") if "Step 3" in body else body.find("### Step 3")
        section = body[idx : idx + 1000]
        assert "provider" in section.lower(), "Step 3 must present provider"

    def test_step_3_presents_artifact_path(self):
        body = _get_body("modes/harness-finish.md")
        idx = body.find("Step 3") if "Step 3" in body else body.find("### Step 3")
        section = body[idx : idx + 1000]
        assert "artifact" in section.lower() or "path" in section.lower(), (
            "Step 3 must present artifact path"
        )


# ---------------------------------------------------------------------------
# harness-debug.md tests
# ---------------------------------------------------------------------------


class TestHarnessDebugFailureMode5:
    """harness-debug.md must have Failure Mode 5 with tier-specific feature table."""

    def test_has_failure_mode_5(self):
        body = _get_body("modes/harness-debug.md")
        assert "Failure Mode 5" in body, (
            "Must have 'Failure Mode 5: Tier-Specific Feature Issues'"
        )

    def test_failure_mode_5_about_tier_specific(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "tier" in section.lower(), (
            "Failure Mode 5 must be about tier-specific issues"
        )

    def test_failure_mode_5_table_has_streaming(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "streaming" in section.lower(), "Feature table must have streaming"

    def test_failure_mode_5_table_has_session_persistence(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "session" in section.lower() and "persist" in section.lower(), (
            "Feature table must have session persistence"
        )

    def test_failure_mode_5_table_has_provider_switching(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "provider" in section.lower(), (
            "Feature table must have provider switching"
        )

    def test_failure_mode_5_table_has_dynamic_context(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "dynamic context" in section.lower() or "dynamic" in section.lower(), (
            "Feature table must have dynamic context"
        )

    def test_failure_mode_5_table_has_mode_switching(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "mode switch" in section.lower() or "mode" in section.lower(), (
            "Feature table must have mode switching"
        )

    def test_failure_mode_5_table_has_recipes(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "recipe" in section.lower(), "Feature table must have recipes"

    def test_failure_mode_5_table_has_delegation(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "delegation" in section.lower() or "delegate" in section.lower(), (
            "Feature table must have delegation"
        )

    def test_failure_mode_5_table_has_approval_gates(self):
        body = _get_body("modes/harness-debug.md")
        idx = body.find("Failure Mode 5")
        section = body[idx : idx + 3000]
        assert "approval" in section.lower() or "gate" in section.lower(), (
            "Feature table must have approval gates"
        )


# ---------------------------------------------------------------------------
# context/instructions.md tests
# ---------------------------------------------------------------------------


class TestInstructionsUpdated:
    """context/instructions.md must have Three Size Tiers, Dynamic Discovery, Mission Naming."""

    def test_has_three_size_tiers_section(self):
        content = _read_file("context/instructions.md")
        assert "Three Size Tiers" in content, "Must have 'Three Size Tiers' section"

    def test_three_size_tiers_has_pico_spec(self):
        content = _read_file("context/instructions.md")
        idx = content.find("Three Size Tiers")
        section = content[idx : idx + 2000]
        assert "pico" in section.lower(), "Three Size Tiers must describe pico"
        # pico: 800-1500 tokens, 50% quality target at 10% cost
        assert "800" in section or "1500" in section, (
            "Pico tier must specify token range"
        )

    def test_three_size_tiers_has_nano_spec(self):
        content = _read_file("context/instructions.md")
        idx = content.find("Three Size Tiers")
        section = content[idx : idx + 2000]
        assert "nano" in section.lower(), "Three Size Tiers must describe nano"
        assert "2000" in section or "3500" in section, (
            "Nano tier must specify token range"
        )

    def test_three_size_tiers_has_micro_spec(self):
        content = _read_file("context/instructions.md")
        idx = content.find("Three Size Tiers")
        section = content[idx : idx + 2000]
        assert "micro" in section.lower(), "Three Size Tiers must describe micro"
        assert "5000" in section or "8000" in section, (
            "Micro tier must specify token range"
        )

    def test_has_dynamic_discovery_section(self):
        content = _read_file("context/instructions.md")
        assert "Dynamic Discovery" in content, "Must have 'Dynamic Discovery' section"

    def test_has_mission_naming_section(self):
        content = _read_file("context/instructions.md")
        assert "Mission Naming" in content, "Must have 'Mission Naming' section"

    def test_all_new_sections_before_two_track_ux(self):
        content = _read_file("context/instructions.md")
        idx_tiers = content.find("Three Size Tiers")
        idx_discovery = content.find("Dynamic Discovery")
        idx_naming = content.find("Mission Naming")
        idx_two_track = content.find("## Two-Track UX")
        assert idx_tiers != -1, "Three Size Tiers must exist"
        assert idx_discovery != -1, "Dynamic Discovery must exist"
        assert idx_naming != -1, "Mission Naming must exist"
        assert idx_two_track != -1, "Two-Track UX must still exist"
        assert idx_tiers < idx_two_track, (
            "Three Size Tiers must come before ## Two-Track UX"
        )
        assert idx_discovery < idx_two_track, (
            "Dynamic Discovery must come before ## Two-Track UX"
        )
        assert idx_naming < idx_two_track, (
            "Mission Naming must come before ## Two-Track UX"
        )

    def test_intent_mapping_has_build_me_an_agent(self):
        content = _read_file("context/instructions.md")
        assert (
            "build me an agent" in content.lower() or "build me a" in content.lower()
        ), "Intent mapping must include 'build me an agent' trigger"

    def test_intent_mapping_has_mini_amplifier_trigger(self):
        content = _read_file("context/instructions.md")
        assert "mini-amplifier" in content.lower(), (
            "Intent mapping must include 'mini-amplifier' trigger"
        )


# ---------------------------------------------------------------------------
# context/harness-format.md tests
# ---------------------------------------------------------------------------


class TestHarnessFormatSizeTiers:
    """context/harness-format.md must have Size Tiers table before Tier 1: Nano-Amplifier."""

    def test_has_size_tiers_table(self):
        content = _read_file("context/harness-format.md")
        assert "Size Tiers" in content, "Must have 'Size Tiers' table/section"

    def test_size_tiers_before_tier_1(self):
        content = _read_file("context/harness-format.md")
        idx_size_tiers = content.find("Size Tiers")
        idx_tier1 = content.find("Tier 1: Nano-Amplifier")
        assert idx_size_tiers != -1, "Must have Size Tiers section"
        assert idx_tier1 != -1, "Must still have Tier 1: Nano-Amplifier"
        assert idx_size_tiers < idx_tier1, (
            "Size Tiers table must come before 'Tier 1: Nano-Amplifier'"
        )

    def test_size_tiers_table_has_tier_column(self):
        content = _read_file("context/harness-format.md")
        idx = content.find("Size Tiers")
        section = content[idx : idx + 1500]
        assert "tier" in section.lower(), "Size Tiers table must have a tier column"

    def test_size_tiers_table_has_runtime_scaffold_column(self):
        content = _read_file("context/harness-format.md")
        idx = content.find("Size Tiers")
        section = content[idx : idx + 1500]
        assert "runtime" in section.lower() or "scaffold" in section.lower(), (
            "Size Tiers table must have a runtime scaffold column"
        )

    def test_size_tiers_table_has_features_column(self):
        content = _read_file("context/harness-format.md")
        idx = content.find("Size Tiers")
        section = content[idx : idx + 1500]
        assert "feature" in section.lower(), (
            "Size Tiers table must have a features column"
        )

    def test_size_tiers_table_has_pico_nano_micro(self):
        content = _read_file("context/harness-format.md")
        idx = content.find("Size Tiers")
        section = content[idx : idx + 1500]
        assert "pico" in section.lower(), "Size Tiers table must have pico row"
        assert "nano" in section.lower(), "Size Tiers table must have nano row"
        assert "micro" in section.lower(), "Size Tiers table must have micro row"


# ---------------------------------------------------------------------------
# context/pattern.md tests
# ---------------------------------------------------------------------------


class TestPatternThreeTierArchitecture:
    """context/pattern.md must have Three-Tier Architecture before ## Seven Components."""

    def test_has_three_tier_architecture_section(self):
        content = _read_file("context/pattern.md")
        assert "Three-Tier Architecture" in content, (
            "Must have 'Three-Tier Architecture' section"
        )

    def test_three_tier_architecture_before_seven_components(self):
        content = _read_file("context/pattern.md")
        idx_three_tier = content.find("Three-Tier Architecture")
        idx_seven = content.find("## Seven Components")
        assert idx_three_tier != -1, "Must have Three-Tier Architecture"
        assert idx_seven != -1, "Must still have ## Seven Components"
        assert idx_three_tier < idx_seven, (
            "Three-Tier Architecture must come before '## Seven Components'"
        )

    def test_three_tier_has_pico_description(self):
        content = _read_file("context/pattern.md")
        idx = content.find("Three-Tier Architecture")
        section = content[idx : idx + 3000]
        assert "pico" in section.lower(), "Three-Tier Architecture must describe Pico"

    def test_three_tier_has_nano_description(self):
        content = _read_file("context/pattern.md")
        idx = content.find("Three-Tier Architecture")
        section = content[idx : idx + 3000]
        assert "nano" in section.lower(), "Three-Tier Architecture must describe Nano"

    def test_three_tier_has_micro_description(self):
        content = _read_file("context/pattern.md")
        idx = content.find("Three-Tier Architecture")
        section = content[idx : idx + 3000]
        assert "micro" in section.lower(), "Three-Tier Architecture must describe Micro"

    def test_three_tier_has_pico_use_case(self):
        content = _read_file("context/pattern.md")
        idx = content.find("Three-Tier Architecture")
        section = content[idx : idx + 3000]
        assert "pico" in section.lower() and (
            "use case" in section.lower()
            or "best for" in section.lower()
            or "when" in section.lower()
            or "simple" in section.lower()
        ), "Pico tier must have use case description"

    def test_three_tier_has_each_builds_on_previous(self):
        content = _read_file("context/pattern.md")
        idx = content.find("Three-Tier Architecture")
        section = content[idx : idx + 3000]
        assert (
            "builds on" in section.lower()
            or "each tier" in section.lower()
            or "adds" in section.lower()
            or "extends" in section.lower()
        ), "Three-Tier Architecture must note each-builds-on-previous relationship"
