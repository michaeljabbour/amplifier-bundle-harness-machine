"""Tests for task-4: mission-architect agent and constraint-spec-template.

Validates:
- agents/mission-architect.md exists with valid YAML frontmatter
  - meta.name = mission-architect
  - meta.model_role includes both creative and reasoning
  - exactly 3 tools: tool-filesystem, tool-search, tool-bash
  - description contains 2 examples (genomics specialist, k8s auditor)
  - body has naming convention, reserved CLI names, 4 output artifacts, MUST NOT list,
    final response contract, @foundation common-agent-base reference

- context/constraint-spec-template.md exists with all 8 categories and key attack vectors:
  - Category 1: Command Substitution ($(), backticks, <(), >(), nested, arithmetic expansion)
  - Category 2: Operator Bypasses (>|, <>, semicolons/&&/||/pipes, background &, subshell, brace group)
  - Category 3: Prefix Bypasses (env, xargs, find -exec, timeout, etc.)
  - Category 4: Absolute Path Invocation
  - Category 5: Output Redirection Target Validation
  - Category 6: rm Long-Form Flags (--recursive, --force)
  - Category 7: dd Without Safeguards (dd of=)
  - Category 8: Network Exfiltration
  - Implementation Checklist with 10 items
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
# agents/mission-architect.md tests
# ---------------------------------------------------------------------------


class TestMissionArchitectAgent:
    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "agents", "mission-architect.md")
        assert os.path.isfile(path), "agents/mission-architect.md does not exist"

    def test_frontmatter_parses(self):
        content = _read_file("agents/mission-architect.md")
        fm = _parse_frontmatter(content)
        assert fm is not None
        assert isinstance(fm, dict)

    def test_meta_name_is_mission_architect(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        assert fm["meta"]["name"] == "mission-architect"

    def test_meta_description_is_non_empty_string(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        desc = fm["meta"]["description"]
        assert isinstance(desc, str)
        assert len(desc.strip()) > 0

    def test_meta_description_has_two_examples(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        desc = fm["meta"]["description"]
        assert desc.count("<example>") >= 2, "Description must have at least 2 examples"

    def test_meta_description_mentions_genomics(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        desc = fm["meta"]["description"]
        assert "genomics" in desc.lower(), "Description must mention genomics specialist example"

    def test_meta_description_mentions_k8s(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        desc = fm["meta"]["description"]
        assert "k8s" in desc.lower() or "kubernetes" in desc.lower(), (
            "Description must mention k8s/kubernetes auditor example"
        )

    def test_model_role_includes_creative(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        model_role = fm["meta"]["model_role"]
        assert isinstance(model_role, list), "model_role must be a list"
        assert "creative" in model_role, "model_role must include 'creative'"

    def test_model_role_includes_reasoning(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        model_role = fm["meta"]["model_role"]
        assert "reasoning" in model_role, "model_role must include 'reasoning'"

    def test_model_role_includes_general(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        model_role = fm["meta"]["model_role"]
        assert "general" in model_role, "model_role must include 'general'"

    def test_has_exactly_three_tools(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        tools = fm["tools"]
        assert isinstance(tools, list), "tools must be a list"
        assert len(tools) == 3, f"Expected 3 tools, got {len(tools)}"

    def test_tools_include_tool_filesystem(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        tool_modules = [t["module"] for t in fm["tools"]]
        assert "tool-filesystem" in tool_modules

    def test_tools_include_tool_search(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        tool_modules = [t["module"] for t in fm["tools"]]
        assert "tool-search" in tool_modules

    def test_tools_include_tool_bash(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        tool_modules = [t["module"] for t in fm["tools"]]
        assert "tool-bash" in tool_modules

    def test_tools_have_git_sources(self):
        fm = _parse_frontmatter(_read_file("agents/mission-architect.md"))
        for tool in fm["tools"]:
            assert "source" in tool, f"Tool {tool.get('module')} missing source"
            assert tool["source"].startswith("git+https://"), (
                f"Tool {tool.get('module')} source must be a git URL"
            )

    def test_body_has_naming_convention(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "{tier}-amplifier-{mission-slug}" in body or "tier}-amplifier-{mission" in body, (
            "Body must document naming convention {tier}-amplifier-{mission-slug}"
        )

    def test_body_has_five_naming_rules(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        # Check for pipeline not domain rule
        assert "pipeline" in body.lower() or "domain" in body.lower()
        # Check for hyphens only rule
        assert "hyphen" in body.lower()
        # Check for max 5 words rule
        assert "5 word" in body.lower() or "five word" in body.lower() or "max 5" in body.lower() or "maximum" in body.lower()
        # Check for no generic names rule
        assert "generic" in body.lower()
        # Check for CLI collision check rule
        assert "collision" in body.lower() or "cli" in body.lower()

    def test_body_has_reserved_cli_names(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        # Verify reserved CLI names list with common Unix utilities
        assert "ls" in body or "cat" in body or "grep" in body, (
            "Body must include reserved CLI names list"
        )

    def test_body_has_output_artifacts_section(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "output artifact" in body.lower() or "artifacts" in body.lower()

    def test_body_mentions_system_prompt(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "system-prompt" in body.lower() or "system_prompt" in body.lower()

    def test_body_mentions_readme(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "readme" in body.lower()

    def test_body_mentions_context_doc(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "context.md" in body.lower()

    def test_body_has_must_not_list(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "must not" in body.lower() or "must_not" in body.lower()

    def test_body_has_final_response_contract(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "response contract" in body.lower() or "final response" in body.lower()

    def test_body_references_foundation_common_agent_base(self):
        content = _read_file("agents/mission-architect.md")
        body = content.split("---", 2)[2]
        assert "@foundation:context/shared/common-agent-base.md" in body


# ---------------------------------------------------------------------------
# context/constraint-spec-template.md tests
# ---------------------------------------------------------------------------


class TestConstraintSpecTemplate:
    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "context", "constraint-spec-template.md")
        assert os.path.isfile(path), "context/constraint-spec-template.md does not exist"

    def test_file_is_non_empty(self):
        content = _read_file("context/constraint-spec-template.md")
        assert len(content.strip()) > 0

    def test_has_category_1_command_substitution(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 1" in content or "command substitution" in content.lower()

    def test_category_1_mentions_dollar_paren(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "$()" in content or "$(" in content, "Category 1 must mention $() command substitution"

    def test_category_1_mentions_backticks(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "backtick" in content.lower() or "`" in content

    def test_category_1_mentions_process_substitution(self):
        content = _read_file("context/constraint-spec-template.md")
        # Process substitution: <() and >()
        assert "<(" in content or "process substitution" in content.lower(), (
            "Category 1 must mention process substitution <() or >()"
        )

    def test_category_1_mentions_arithmetic_expansion(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "arithmetic" in content.lower() or "$((" in content

    def test_has_category_2_operator_bypasses(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 2" in content or "operator bypass" in content.lower()

    def test_category_2_mentions_clobber_redirect(self):
        content = _read_file("context/constraint-spec-template.md")
        assert ">|" in content, "Category 2 must mention >| clobber redirect"

    def test_category_2_mentions_read_write_redirect(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "<>" in content, "Category 2 must mention <> read-write redirect"

    def test_category_2_mentions_append_redirect(self):
        content = _read_file("context/constraint-spec-template.md")
        assert ">>" in content, "Category 2 must mention >> append redirect"

    def test_category_2_mentions_background_operator(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "background" in content.lower() or " &" in content

    def test_has_category_3_prefix_bypasses(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 3" in content or "prefix bypass" in content.lower()

    def test_category_3_mentions_xargs(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "xargs" in content, "Category 3 must mention xargs"

    def test_category_3_mentions_env(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "env" in content.lower()

    def test_category_3_mentions_find_exec(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "find -exec" in content or "find" in content

    def test_has_category_4_absolute_path(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 4" in content or "absolute path" in content.lower()

    def test_has_category_5_output_redirection(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 5" in content or "output redirection" in content.lower()

    def test_has_category_6_rm_long_form_flags(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 6" in content or "rm" in content

    def test_category_6_mentions_recursive_flag(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "--recursive" in content, "Category 6 must mention --recursive"

    def test_category_6_mentions_force_flag(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "--force" in content, "Category 6 must mention --force"

    def test_has_category_7_dd_without_safeguards(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 7" in content or "dd" in content

    def test_category_7_mentions_dd_of(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "dd" in content and "of=" in content, "Category 7 must mention dd of="

    def test_has_category_8_network_exfiltration(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Category 8" in content or "network exfiltration" in content.lower() or "network" in content.lower()

    def test_category_8_mentions_curl_wget(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "curl" in content or "wget" in content

    def test_category_8_mentions_netcat(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "nc" in content or "netcat" in content

    def test_has_implementation_checklist(self):
        content = _read_file("context/constraint-spec-template.md")
        assert "Implementation Checklist" in content or "implementation checklist" in content.lower()

    def test_implementation_checklist_has_ten_items(self):
        content = _read_file("context/constraint-spec-template.md")
        # Count checkbox items: "- [ ]"
        checklist_items = content.count("- [ ]")
        assert checklist_items >= 10, (
            f"Implementation Checklist must have at least 10 items, found {checklist_items}"
        )

    def test_all_eight_categories_present(self):
        content = _read_file("context/constraint-spec-template.md")
        for i in range(1, 9):
            assert f"Category {i}" in content, (
                f"Category {i} not found in constraint-spec-template.md"
            )
