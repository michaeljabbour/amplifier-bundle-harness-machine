"""Tests for task-7: update remaining 6 agents to be tier-aware.

Validates:
- agents/spec-writer.md: tier-aware template with Mission, Proposed Name,
  Tier Selection, Capability Selections, Bash Constraints sections, and
  explicit critic round budget (4-5 rounds).
- agents/plan-writer.md: '## Plan Shape by Tier and Scale' heading,
  tier table (pico/nano/micro), scale subsections with setup.sh generation task,
  per-skill plan, STATE.yaml.
- agents/harness-generator.md: '### 1b. Determine Generation Scope by Tier',
  '### 1c. Reserved CLI Name Check', updated config.yaml with tier and
  max_iterations fields.
- agents/harness-critic.md: expanded 12-row check table and
  '## Bash Constraint Review' section with all 8 categories.
- agents/harness-refiner.md: '### 0. Tier Awareness' with pico/nano/micro
  tier-specific requirements.
- agents/harness-evaluator.md: '### For mini-amplifier CLI verification (all tiers)'
  with 6 verification checks.

All 6 files must have valid YAML frontmatter with correct names and
non-empty descriptions.
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


def _get_body(rel_path):
    """Return the markdown body (after frontmatter) of a file."""
    return _read_file(rel_path).split("---", 2)[2]


# ---------------------------------------------------------------------------
# Shared frontmatter validity tests for all 6 agents
# ---------------------------------------------------------------------------

AGENT_FILES = {
    "spec-writer": "agents/spec-writer.md",
    "plan-writer": "agents/plan-writer.md",
    "harness-generator": "agents/harness-generator.md",
    "harness-critic": "agents/harness-critic.md",
    "harness-refiner": "agents/harness-refiner.md",
    "harness-evaluator": "agents/harness-evaluator.md",
}


class TestAllAgentsFrontmatterValid:
    """All 6 updated agents must have valid YAML frontmatter."""

    def test_spec_writer_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("agents/spec-writer.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_plan_writer_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("agents/plan-writer.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_generator_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("agents/harness-generator.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_critic_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("agents/harness-critic.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_refiner_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("agents/harness-refiner.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_harness_evaluator_frontmatter_parses(self):
        fm = _parse_frontmatter(_read_file("agents/harness-evaluator.md"))
        assert fm is not None and isinstance(fm, dict)

    def test_spec_writer_name(self):
        fm = _parse_frontmatter(_read_file("agents/spec-writer.md"))
        assert fm["meta"]["name"] == "spec-writer"

    def test_plan_writer_name(self):
        fm = _parse_frontmatter(_read_file("agents/plan-writer.md"))
        assert fm["meta"]["name"] == "plan-writer"

    def test_harness_generator_name(self):
        fm = _parse_frontmatter(_read_file("agents/harness-generator.md"))
        assert fm["meta"]["name"] == "harness-generator"

    def test_harness_critic_name(self):
        fm = _parse_frontmatter(_read_file("agents/harness-critic.md"))
        assert fm["meta"]["name"] == "harness-critic"

    def test_harness_refiner_name(self):
        fm = _parse_frontmatter(_read_file("agents/harness-refiner.md"))
        assert fm["meta"]["name"] == "harness-refiner"

    def test_harness_evaluator_name(self):
        fm = _parse_frontmatter(_read_file("agents/harness-evaluator.md"))
        assert fm["meta"]["name"] == "harness-evaluator"

    def test_spec_writer_description_non_empty(self):
        fm = _parse_frontmatter(_read_file("agents/spec-writer.md"))
        assert isinstance(fm["meta"]["description"], str)
        assert len(fm["meta"]["description"].strip()) > 0

    def test_plan_writer_description_non_empty(self):
        fm = _parse_frontmatter(_read_file("agents/plan-writer.md"))
        assert isinstance(fm["meta"]["description"], str)
        assert len(fm["meta"]["description"].strip()) > 0

    def test_harness_generator_description_non_empty(self):
        fm = _parse_frontmatter(_read_file("agents/harness-generator.md"))
        assert isinstance(fm["meta"]["description"], str)
        assert len(fm["meta"]["description"].strip()) > 0

    def test_harness_critic_description_non_empty(self):
        fm = _parse_frontmatter(_read_file("agents/harness-critic.md"))
        assert isinstance(fm["meta"]["description"], str)
        assert len(fm["meta"]["description"].strip()) > 0

    def test_harness_refiner_description_non_empty(self):
        fm = _parse_frontmatter(_read_file("agents/harness-refiner.md"))
        assert isinstance(fm["meta"]["description"], str)
        assert len(fm["meta"]["description"].strip()) > 0

    def test_harness_evaluator_description_non_empty(self):
        fm = _parse_frontmatter(_read_file("agents/harness-evaluator.md"))
        assert isinstance(fm["meta"]["description"], str)
        assert len(fm["meta"]["description"].strip()) > 0


# ---------------------------------------------------------------------------
# spec-writer.md tests
# ---------------------------------------------------------------------------


class TestSpecWriterTierAware:
    """spec-writer.md must have tier-aware template sections."""

    def test_has_mission_section_in_template(self):
        body = _get_body("agents/spec-writer.md")
        assert "## Mission" in body, "Template must have a Mission section"

    def test_has_proposed_name_in_template(self):
        body = _get_body("agents/spec-writer.md")
        # Proposed Name must mention tier pattern like {tier}-amplifier-{mission-slug}
        assert "Proposed Name" in body, "Template must have Proposed Name"
        assert "mission-slug" in body, (
            "Proposed Name must reference mission-slug pattern"
        )

    def test_proposed_name_includes_tier_prefix(self):
        body = _get_body("agents/spec-writer.md")
        # Must show tier pattern: {tier}-amplifier-{mission-slug}
        assert "{tier}-amplifier-" in body or "tier}-amplifier-" in body, (
            "Proposed Name must include tier prefix pattern"
        )

    def test_has_tier_selection_section_in_template(self):
        body = _get_body("agents/spec-writer.md")
        assert "Tier Selection" in body, "Template must have Tier Selection section"

    def test_tier_selection_mentions_pico_nano_micro(self):
        body = _get_body("agents/spec-writer.md")
        assert "pico" in body.lower(), "Tier Selection must mention pico"
        assert "nano" in body.lower(), "Tier Selection must mention nano"
        assert "micro" in body.lower(), "Tier Selection must mention micro"

    def test_tier_selection_mentions_rationale(self):
        body = _get_body("agents/spec-writer.md")
        assert "rationale" in body.lower(), "Tier Selection must reference rationale"

    def test_has_capability_selections_section_in_template(self):
        body = _get_body("agents/spec-writer.md")
        assert "Capability Selections" in body, (
            "Template must have Capability Selections section"
        )

    def test_has_bash_constraints_section_in_template(self):
        body = _get_body("agents/spec-writer.md")
        assert "Bash Constraints" in body, "Template must have Bash Constraints section"

    def test_bash_constraints_references_constraint_spec_template(self):
        body = _get_body("agents/spec-writer.md")
        assert "constraint-spec-template" in body, (
            "Bash Constraints section must reference @harness-machine:context/constraint-spec-template.md"
        )

    def test_has_critic_round_budget(self):
        body = _get_body("agents/spec-writer.md")
        # Must mention 4-5 critic rounds explicitly
        assert "4" in body and "5" in body, "Must mention 4-5 critic rounds"
        assert "critic" in body.lower(), "Must mention critic rounds"

    def test_template_section_heading_present(self):
        body = _get_body("agents/spec-writer.md")
        assert "## Specification Document Template" in body, (
            "Must retain ## Specification Document Template heading"
        )


# ---------------------------------------------------------------------------
# plan-writer.md tests
# ---------------------------------------------------------------------------


class TestPlanWriterTierAware:
    """plan-writer.md must have tier-aware plan shape section."""

    def test_has_plan_shape_by_tier_and_scale_heading(self):
        body = _get_body("agents/plan-writer.md")
        assert "## Plan Shape by Tier and Scale" in body, (
            "Must have '## Plan Shape by Tier and Scale' heading"
        )

    def test_old_heading_replaced(self):
        body = _get_body("agents/plan-writer.md")
        # The old heading "## Plan Shape by Scale" should be replaced
        # (it should NOT appear alone, only as part of "by Tier and Scale")
        lines = body.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped == "## Plan Shape by Scale":
                raise AssertionError(
                    "Old '## Plan Shape by Scale' heading must be replaced with "
                    "'## Plan Shape by Tier and Scale'"
                )

    def test_tier_table_has_pico(self):
        body = _get_body("agents/plan-writer.md")
        assert "pico" in body.lower(), "Tier table must include pico"

    def test_tier_table_has_nano(self):
        body = _get_body("agents/plan-writer.md")
        assert "nano" in body.lower(), "Tier table must include nano"

    def test_tier_table_has_micro(self):
        body = _get_body("agents/plan-writer.md")
        assert "micro" in body.lower(), "Tier table must include micro"

    def test_tier_table_mentions_simple_for_pico(self):
        body = _get_body("agents/plan-writer.md")
        assert "simple" in body.lower(), "Tier table must mention simple for pico"

    def test_tier_table_mentions_medium_for_nano(self):
        body = _get_body("agents/plan-writer.md")
        assert "medium" in body.lower(), "Tier table must mention medium for nano"

    def test_tier_table_mentions_complex_for_micro(self):
        body = _get_body("agents/plan-writer.md")
        assert "complex" in body.lower(), "Tier table must mention complex for micro"

    def test_tier_table_mentions_4_5_critic_rounds(self):
        body = _get_body("agents/plan-writer.md")
        # Must mention 4-5 critic rounds for each tier
        assert "4" in body and "5" in body, "Tier table must mention 4-5 critic rounds"
        assert "critic" in body.lower(), "Tier table must mention critic rounds"

    def test_has_setup_sh_in_nano_single_plan(self):
        body = _get_body("agents/plan-writer.md")
        assert "setup.sh" in body, (
            "nano/single plan must include setup.sh generation task"
        )

    def test_has_per_skill_plan_for_library(self):
        body = _get_body("agents/plan-writer.md")
        assert "per-skill" in body.lower() or "per skill" in body.lower(), (
            "library plan must include per-skill plan"
        )

    def test_has_state_yaml_for_factory(self):
        body = _get_body("agents/plan-writer.md")
        assert "STATE.yaml" in body, "factory plan must reference STATE.yaml"


# ---------------------------------------------------------------------------
# harness-generator.md tests
# ---------------------------------------------------------------------------


class TestHarnessGeneratorTierAware:
    """harness-generator.md must have generation scope table and CLI name check."""

    def test_has_generation_scope_by_tier_section(self):
        body = _get_body("agents/harness-generator.md")
        assert "1b. Determine Generation Scope by Tier" in body, (
            "Must have '### 1b. Determine Generation Scope by Tier' section"
        )

    def test_generation_scope_section_after_read_specification(self):
        body = _get_body("agents/harness-generator.md")
        idx_read_spec = body.find("### 1. Read the Specification")
        idx_scope = body.find("1b. Determine Generation Scope by Tier")
        assert idx_read_spec != -1, "Must have '### 1. Read the Specification' section"
        assert idx_scope != -1, (
            "Must have '1b. Determine Generation Scope by Tier' section"
        )
        assert idx_scope > idx_read_spec, (
            "'1b. Determine Generation Scope by Tier' must come after '### 1. Read the Specification'"
        )

    def test_generation_scope_has_pico_nano_micro(self):
        body = _get_body("agents/harness-generator.md")
        idx = body.find("1b. Determine Generation Scope by Tier")
        section = body[idx : idx + 2000]
        assert "pico" in section.lower(), "Generation scope table must include pico"
        assert "nano" in section.lower(), "Generation scope table must include nano"
        assert "micro" in section.lower(), "Generation scope table must include micro"

    def test_generation_scope_mentions_scaffold(self):
        body = _get_body("agents/harness-generator.md")
        idx = body.find("1b. Determine Generation Scope by Tier")
        section = body[idx : idx + 2000]
        assert "scaffold" in section.lower(), (
            "Generation scope table must mention what comes from scaffold"
        )

    def test_has_reserved_cli_name_check_section(self):
        body = _get_body("agents/harness-generator.md")
        assert "1c. Reserved CLI Name Check" in body, (
            "Must have '### 1c. Reserved CLI Name Check' section"
        )

    def test_reserved_cli_names_present(self):
        body = _get_body("agents/harness-generator.md")
        idx = body.find("1c. Reserved CLI Name Check")
        section = body[idx : idx + 2000]
        # Must have a list of reserved names
        assert "amplifier" in section.lower(), (
            "Reserved name list must mention amplifier"
        )

    def test_collision_rule_full_hyphenated_name(self):
        body = _get_body("agents/harness-generator.md")
        idx = body.find("1c. Reserved CLI Name Check")
        section = body[idx : idx + 2000]
        # The rule: full hyphenated name != collision
        assert "collision" in section.lower(), "Must explain collision rules"

    def test_config_yaml_has_tier_field(self):
        body = _get_body("agents/harness-generator.md")
        # The config.yaml format section should have tier field
        idx = body.find("config.yaml Format")
        assert idx != -1, "Must have config.yaml Format section"
        section = body[idx : idx + 1000]
        assert "tier:" in section, "config.yaml must include tier field"

    def test_config_yaml_has_max_iterations_field(self):
        body = _get_body("agents/harness-generator.md")
        idx = body.find("config.yaml Format")
        section = body[idx : idx + 1000]
        assert "max_iterations" in section, (
            "config.yaml must include max_iterations field"
        )


# ---------------------------------------------------------------------------
# harness-critic.md tests
# ---------------------------------------------------------------------------


class TestHarnessCriticExpanded:
    """harness-critic.md must have expanded 12-row check table and Bash Constraint Review."""

    def test_what_you_check_table_has_cli_name_collision(self):
        body = _get_body("agents/harness-critic.md")
        assert "CLI name collision" in body or "cli name collision" in body.lower(), (
            "Check table must include CLI name collision row"
        )

    def test_what_you_check_table_has_system_prompt_accuracy(self):
        body = _get_body("agents/harness-critic.md")
        assert "system prompt" in body.lower(), (
            "Check table must include system prompt accuracy row"
        )

    def test_what_you_check_table_has_signal_handling(self):
        body = _get_body("agents/harness-critic.md")
        assert "signal handling" in body.lower(), (
            "Check table must include signal handling present row"
        )

    def test_what_you_check_table_has_config_completeness(self):
        body = _get_body("agents/harness-critic.md")
        assert (
            "config completeness" in body.lower() or "config complete" in body.lower()
        ), "Check table must include config completeness row"

    def test_what_you_check_table_has_rich_rendering(self):
        body = _get_body("agents/harness-critic.md")
        assert "rich rendering" in body.lower() or "rich" in body.lower(), (
            "Check table must include Rich rendering present row"
        )

    def test_what_you_check_table_has_bash_constraints(self):
        body = _get_body("agents/harness-critic.md")
        assert (
            "bash constraints" in body.lower() or "bash constraint" in body.lower()
        ), "Check table must include bash constraints row"

    def test_check_table_has_at_least_12_rows(self):
        body = _get_body("agents/harness-critic.md")
        # Find the What You Check table and count rows
        idx_start = body.find("## What You Check")
        assert idx_start != -1, "Must have '## What You Check' section"
        # Extract table section (until next ##)
        idx_next_section = body.find("\n## ", idx_start + 1)
        table_section = body[
            idx_start : idx_next_section if idx_next_section != -1 else idx_start + 3000
        ]
        # Count table rows (lines starting with |, excluding header and separator)
        rows = [
            line.strip()
            for line in table_section.split("\n")
            if line.strip().startswith("|")
            and not line.strip().startswith("| Check")
            and not line.strip().startswith("|---")
            and not line.strip().startswith("|----")
            and "---" not in line
        ]
        assert len(rows) >= 12, (
            f"'What You Check' table must have at least 12 data rows, found {len(rows)}"
        )

    def test_has_bash_constraint_review_section(self):
        body = _get_body("agents/harness-critic.md")
        assert "## Bash Constraint Review" in body, (
            "Must have '## Bash Constraint Review' section"
        )

    def test_bash_constraint_review_has_all_8_categories(self):
        body = _get_body("agents/harness-critic.md")
        idx = body.find("## Bash Constraint Review")
        assert idx != -1
        section = body[idx : idx + 3000]
        # All 8 categories from constraint-spec-template.md
        assert "command substitution" in section.lower(), (
            "Category 1: Command Substitution"
        )
        assert "operator bypass" in section.lower(), "Category 2: Operator Bypasses"
        assert "prefix bypass" in section.lower(), "Category 3: Prefix Bypasses"
        assert "absolute path" in section.lower(), (
            "Category 4: Absolute Path Invocation"
        )
        assert "output redirection" in section.lower(), "Category 5: Output Redirection"
        assert "rm" in section.lower(), "Category 6: rm Long-Form Flags"
        assert "dd" in section.lower(), "Category 7: dd Without Safeguards"
        assert "network exfiltration" in section.lower(), (
            "Category 8: Network Exfiltration"
        )


# ---------------------------------------------------------------------------
# harness-refiner.md tests
# ---------------------------------------------------------------------------


class TestHarnessRefinerTierAware:
    """harness-refiner.md must have Tier Awareness section."""

    def test_has_tier_awareness_section(self):
        body = _get_body("agents/harness-refiner.md")
        assert "### 0. Tier Awareness" in body, (
            "Must have '### 0. Tier Awareness' section"
        )

    def test_tier_awareness_after_refinement_process(self):
        body = _get_body("agents/harness-refiner.md")
        idx_process = body.find("## Refinement Process")
        idx_tier = body.find("### 0. Tier Awareness")
        assert idx_process != -1, "Must have '## Refinement Process' section"
        assert idx_tier != -1, "Must have '### 0. Tier Awareness' section"
        assert idx_tier > idx_process, (
            "'### 0. Tier Awareness' must come after '## Refinement Process'"
        )

    def test_tier_awareness_mentions_pico(self):
        body = _get_body("agents/harness-refiner.md")
        idx = body.find("### 0. Tier Awareness")
        section = body[idx : idx + 2000]
        assert "pico" in section.lower(), "Tier Awareness must mention pico"

    def test_tier_awareness_pico_constraints_only(self):
        body = _get_body("agents/harness-refiner.md")
        idx = body.find("### 0. Tier Awareness")
        section = body[idx : idx + 2000]
        # pico = constraints only
        assert "constraint" in section.lower(), (
            "Tier Awareness must specify pico = constraints only"
        )

    def test_tier_awareness_mentions_nano(self):
        body = _get_body("agents/harness-refiner.md")
        idx = body.find("### 0. Tier Awareness")
        section = body[idx : idx + 2000]
        assert "nano" in section.lower(), "Tier Awareness must mention nano"

    def test_tier_awareness_nano_streaming_session_provider(self):
        body = _get_body("agents/harness-refiner.md")
        idx = body.find("### 0. Tier Awareness")
        section = body[idx : idx + 2000]
        # nano = may refine streaming/session/provider config
        assert (
            "streaming" in section.lower()
            or "session" in section.lower()
            or "provider" in section.lower()
        ), (
            "Tier Awareness must specify nano may refine streaming/session/provider config"
        )

    def test_tier_awareness_mentions_micro(self):
        body = _get_body("agents/harness-refiner.md")
        idx = body.find("### 0. Tier Awareness")
        section = body[idx : idx + 2000]
        assert "micro" in section.lower(), "Tier Awareness must mention micro"

    def test_tier_awareness_micro_mode_recipe_delegation(self):
        body = _get_body("agents/harness-refiner.md")
        idx = body.find("### 0. Tier Awareness")
        section = body[idx : idx + 2000]
        # micro = may refine mode/recipe/delegation/approval config
        assert (
            "mode" in section.lower()
            or "recipe" in section.lower()
            or "delegation" in section.lower()
            or "approval" in section.lower()
        ), (
            "Tier Awareness must specify micro may refine mode/recipe/delegation/approval config"
        )


# ---------------------------------------------------------------------------
# harness-evaluator.md tests
# ---------------------------------------------------------------------------


class TestHarnessEvaluatorCLIVerification:
    """harness-evaluator.md must have mini-amplifier CLI verification protocol."""

    def test_has_cli_verification_section(self):
        body = _get_body("agents/harness-evaluator.md")
        assert "### For mini-amplifier CLI verification (all tiers)" in body, (
            "Must have '### For mini-amplifier CLI verification (all tiers)' section"
        )

    def test_cli_verification_after_factory_artifacts(self):
        body = _get_body("agents/harness-evaluator.md")
        idx_factory = body.find("### For factory artifacts")
        idx_cli = body.find("### For mini-amplifier CLI verification (all tiers)")
        assert idx_factory != -1, "Must have '### For factory artifacts' section"
        assert idx_cli != -1, "Must have CLI verification section"
        assert idx_cli > idx_factory, (
            "CLI verification section must come after '### For factory artifacts'"
        )

    def test_cli_verification_has_check_subcommand(self):
        body = _get_body("agents/harness-evaluator.md")
        idx = body.find("### For mini-amplifier CLI verification (all tiers)")
        section = body[idx : idx + 2000]
        assert "check" in section.lower(), (
            "Verification check 1: CLI starts with check subcommand"
        )

    def test_cli_verification_has_chat_mode(self):
        body = _get_body("agents/harness-evaluator.md")
        idx = body.find("### For mini-amplifier CLI verification (all tiers)")
        section = body[idx : idx + 2000]
        assert "chat" in section.lower(), "Verification check 2: chat mode initializes"

    def test_cli_verification_has_system_prompt_accuracy(self):
        body = _get_body("agents/harness-evaluator.md")
        idx = body.find("### For mini-amplifier CLI verification (all tiers)")
        section = body[idx : idx + 2000]
        assert "system prompt" in section.lower(), (
            "Verification check 3: system prompt accuracy"
        )

    def test_cli_verification_has_config_loads(self):
        body = _get_body("agents/harness-evaluator.md")
        idx = body.find("### For mini-amplifier CLI verification (all tiers)")
        section = body[idx : idx + 2000]
        assert "config" in section.lower(), (
            "Verification check 4: config loads with required keys"
        )

    def test_cli_verification_has_tools_functional(self):
        body = _get_body("agents/harness-evaluator.md")
        idx = body.find("### For mini-amplifier CLI verification (all tiers)")
        section = body[idx : idx + 2000]
        assert "tool" in section.lower(), (
            "Verification check 5: all selected tools functional"
        )

    def test_cli_verification_has_amplifier_hook(self):
        body = _get_body("agents/harness-evaluator.md")
        idx = body.find("### For mini-amplifier CLI verification (all tiers)")
        section = body[idx : idx + 2000]
        assert "hook" in section.lower() or "yaml.safe_load" in section.lower(), (
            "Verification check 6: Amplifier hook loads via yaml.safe_load"
        )

    def test_cli_verification_has_6_checks(self):
        body = _get_body("agents/harness-evaluator.md")
        idx_start = body.find("### For mini-amplifier CLI verification (all tiers)")
        assert idx_start != -1
        # Find end of this section (next ###)
        idx_end = body.find("\n###", idx_start + 1)
        section = body[idx_start : idx_end if idx_end != -1 else idx_start + 2000]
        # Count numbered items (1. 2. 3. etc.)
        import re

        numbered = re.findall(r"^\s*\d+\.", section, re.MULTILINE)
        assert len(numbered) >= 6, (
            f"CLI verification section must have at least 6 numbered checks, found {len(numbered)}"
        )
