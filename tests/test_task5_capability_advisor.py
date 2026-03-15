"""Tests for task-5: capability-advisor agent.

Validates:
- agents/capability-advisor.md exists with valid YAML frontmatter
  - meta.name = capability-advisor
  - meta.model_role includes reasoning (and general)
  - exactly 3 tools: tool-filesystem, tool-search, tool-bash
  - description contains 2 examples (genomics specialist tools, k8s tier assessment)
- body has:
  - Dynamic Discovery section (amplifier module list / bundle list --all,
    organized by type, fallback to known baseline)
  - Recommendation Process with 5 subsections:
    1. Analyze the Mission
    2. Recommend Tier
    3. Recommend Tools
    4. Recommend Provider
    5. Detect Tier Conflicts
  - Capability Picker template (checkboxes for Tier, Providers, Tools, Features, Deployment)
  - MUST NOT list (no constraint code, no runtime code, no naming, no skip tier conflict)
  - Final response contract (tier+rationale, provider+rationale, tools, tier conflict warnings,
    capability picker markdown, discovery status)
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


def _get_body(rel_path="agents/capability-advisor.md"):
    """Return the markdown body (after frontmatter) of a file."""
    return _read_file(rel_path).split("---", 2)[2]


# ---------------------------------------------------------------------------
# agents/capability-advisor.md tests
# ---------------------------------------------------------------------------


class TestCapabilityAdvisorAgent:
    # ------------------------------------------------------------------
    # File existence
    # ------------------------------------------------------------------

    def test_file_exists(self):
        path = os.path.join(BUNDLE_ROOT, "agents", "capability-advisor.md")
        assert os.path.isfile(path), "agents/capability-advisor.md does not exist"

    # ------------------------------------------------------------------
    # Frontmatter structural validity
    # ------------------------------------------------------------------

    def test_frontmatter_parses(self):
        content = _read_file("agents/capability-advisor.md")
        fm = _parse_frontmatter(content)
        assert fm is not None
        assert isinstance(fm, dict)

    def test_meta_name_is_capability_advisor(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        assert fm["meta"]["name"] == "capability-advisor"

    def test_meta_description_is_non_empty_string(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        desc = fm["meta"]["description"]
        assert isinstance(desc, str)
        assert len(desc.strip()) > 0

    def test_meta_description_has_two_examples(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        desc = fm["meta"]["description"]
        assert desc.count("<example>") >= 2, "Description must have at least 2 examples"

    def test_meta_description_mentions_genomics(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        desc = fm["meta"]["description"]
        assert "genomics" in desc.lower(), (
            "Description must mention genomics specialist tools example"
        )

    def test_meta_description_mentions_k8s_tier_assessment(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        desc = fm["meta"]["description"]
        assert "k8s" in desc.lower() or "kubernetes" in desc.lower(), (
            "Description must mention k8s tier assessment example"
        )

    # ------------------------------------------------------------------
    # model_role
    # ------------------------------------------------------------------

    def test_model_role_includes_reasoning(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        model_role = fm["meta"]["model_role"]
        assert isinstance(model_role, list), "model_role must be a list"
        assert "reasoning" in model_role, "model_role must include 'reasoning'"

    def test_model_role_includes_general(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        model_role = fm["meta"]["model_role"]
        assert "general" in model_role, "model_role must include 'general'"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def test_has_exactly_three_tools(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        tools = fm["tools"]
        assert isinstance(tools, list), "tools must be a list"
        assert len(tools) == 3, f"Expected 3 tools, got {len(tools)}"

    def test_tools_include_tool_filesystem(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        tool_modules = [t["module"] for t in fm["tools"]]
        assert "tool-filesystem" in tool_modules

    def test_tools_include_tool_search(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        tool_modules = [t["module"] for t in fm["tools"]]
        assert "tool-search" in tool_modules

    def test_tools_include_tool_bash(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        tool_modules = [t["module"] for t in fm["tools"]]
        assert "tool-bash" in tool_modules

    def test_tools_have_git_sources(self):
        fm = _parse_frontmatter(_read_file("agents/capability-advisor.md"))
        for tool in fm["tools"]:
            assert "source" in tool, f"Tool {tool.get('module')} missing source"
            assert tool["source"].startswith("git+https://"), (
                f"Tool {tool.get('module')} source must be a git URL"
            )

    # ------------------------------------------------------------------
    # Body: Dynamic Discovery section
    # ------------------------------------------------------------------

    def test_body_has_dynamic_discovery_section(self):
        body = _get_body()
        assert "dynamic discovery" in body.lower() or "Dynamic Discovery" in body, (
            "Body must have Dynamic Discovery section"
        )

    def test_body_discovery_runs_amplifier_module_list(self):
        body = _get_body()
        assert "amplifier module list" in body, (
            "Dynamic Discovery must mention 'amplifier module list'"
        )

    def test_body_discovery_runs_amplifier_bundle_list(self):
        body = _get_body()
        assert "amplifier bundle list" in body, (
            "Dynamic Discovery must mention 'amplifier bundle list'"
        )

    def test_body_discovery_organizes_by_type(self):
        body = _get_body()
        # Must mention at least: Providers, Tools, Hooks, Orchestrators, Bundles
        assert "providers" in body.lower() or "Providers" in body
        assert "tools" in body.lower() or "Tools" in body
        assert "hooks" in body.lower() or "Hooks" in body
        assert "orchestrators" in body.lower() or "Orchestrators" in body
        assert "bundles" in body.lower() or "Bundles" in body

    def test_body_discovery_has_fallback(self):
        body = _get_body()
        assert (
            "fall back" in body.lower()
            or "fallback" in body.lower()
            or "baseline" in body.lower()
        ), "Dynamic Discovery must mention fallback to known baseline"

    # ------------------------------------------------------------------
    # Body: Recommendation Process — 5 subsections
    # ------------------------------------------------------------------

    def test_body_has_recommendation_process_section(self):
        body = _get_body()
        assert "recommendation process" in body.lower(), (
            "Body must have Recommendation Process section"
        )

    def test_body_has_analyze_mission_subsection(self):
        body = _get_body()
        assert (
            "analyze the mission" in body.lower()
            or "analyse the mission" in body.lower()
        ), "Body must have 'Analyze the Mission' subsection"

    def test_body_analyze_mission_mentions_domain(self):
        body = _get_body()
        assert "domain" in body.lower()

    def test_body_analyze_mission_mentions_workflow_type(self):
        body = _get_body()
        assert "workflow" in body.lower()

    def test_body_has_recommend_tier_subsection(self):
        body = _get_body()
        assert "recommend tier" in body.lower(), (
            "Body must have 'Recommend Tier' subsection"
        )

    def test_body_tier_decision_table_mentions_pico(self):
        body = _get_body()
        assert "pico" in body.lower(), "Tier decision table must mention pico"

    def test_body_tier_decision_table_mentions_nano(self):
        body = _get_body()
        assert "nano" in body.lower(), "Tier decision table must mention nano"

    def test_body_tier_decision_table_mentions_micro(self):
        body = _get_body()
        assert "micro" in body.lower(), "Tier decision table must mention micro"

    def test_body_has_recommend_tools_subsection(self):
        body = _get_body()
        assert "recommend tools" in body.lower(), (
            "Body must have 'Recommend Tools' subsection"
        )

    def test_body_tools_mentions_per_tool_rationale(self):
        body = _get_body()
        assert "rationale" in body.lower(), (
            "Recommend Tools section must mention per-tool rationale"
        )

    def test_body_tools_mentions_no_delegate_for_pico(self):
        body = _get_body()
        assert "delegate" in body.lower() and "pico" in body.lower(), (
            "Recommend Tools must mention no delegate for pico"
        )

    def test_body_has_recommend_provider_subsection(self):
        body = _get_body()
        assert "recommend provider" in body.lower(), (
            "Body must have 'Recommend Provider' subsection"
        )

    def test_body_provider_mentions_anthropic_claude(self):
        body = _get_body()
        assert "anthropic" in body.lower() or "claude" in body.lower(), (
            "Recommend Provider must mention Anthropic/Claude"
        )

    def test_body_provider_mentions_openai(self):
        body = _get_body()
        assert "openai" in body.lower(), "Recommend Provider must mention OpenAI"

    def test_body_provider_mentions_gemini(self):
        body = _get_body()
        assert "gemini" in body.lower(), "Recommend Provider must mention Gemini"

    def test_body_provider_mentions_ollama(self):
        body = _get_body()
        assert "ollama" in body.lower(), "Recommend Provider must mention Ollama"

    def test_body_provider_mentions_azure(self):
        body = _get_body()
        assert "azure" in body.lower(), "Recommend Provider must mention Azure"

    def test_body_has_detect_tier_conflicts_subsection(self):
        body = _get_body()
        assert "tier conflict" in body.lower() or "detect tier" in body.lower(), (
            "Body must have 'Detect Tier Conflicts' subsection"
        )

    def test_body_tier_conflicts_has_hard_warning(self):
        body = _get_body()
        assert "warning" in body.lower() or "⚠" in body or "hard" in body.lower(), (
            "Tier conflict detection must mention hard warning"
        )

    def test_body_tier_conflicts_mentions_pico_cannot_delegate(self):
        body = _get_body()
        # pico can't delegate is the canonical example in the spec
        body_lower = body.lower()
        assert "pico" in body_lower and "delegate" in body_lower, (
            "Tier conflict section must mention pico cannot delegate"
        )

    # ------------------------------------------------------------------
    # Body: Capability Picker template
    # ------------------------------------------------------------------

    def test_body_has_capability_picker_template(self):
        body = _get_body()
        assert "capability picker" in body.lower(), (
            "Body must have Capability Picker template section"
        )

    def test_body_capability_picker_has_checkboxes(self):
        body = _get_body()
        assert "- [x]" in body or "- [ ]" in body, (
            "Capability Picker must use markdown checkboxes"
        )

    def test_body_capability_picker_has_tier_section(self):
        body = _get_body()
        body_lower = body.lower()
        assert "recommended tier" in body_lower or (
            "tier" in body_lower and "rationale" in body_lower
        ), "Capability Picker must include Recommended Tier with rationale"

    def test_body_capability_picker_has_llm_providers_section(self):
        body = _get_body()
        body_lower = body.lower()
        assert "llm provider" in body_lower or (
            "provider" in body_lower and ("checkbox" in body_lower or "- [" in body)
        ), "Capability Picker must include LLM Providers section"

    def test_body_capability_picker_has_tools_section(self):
        body = _get_body()
        # The picker should show tools with checkboxes
        assert "- [" in body and ("tool" in body.lower()), (
            "Capability Picker must include Tools section with checkboxes"
        )

    def test_body_capability_picker_has_features_section(self):
        body = _get_body()
        assert "feature" in body.lower(), (
            "Capability Picker must include Features section"
        )

    def test_body_capability_picker_has_deployment_section(self):
        body = _get_body()
        assert "deployment" in body.lower(), (
            "Capability Picker must include Deployment section"
        )

    # ------------------------------------------------------------------
    # Body: MUST NOT list
    # ------------------------------------------------------------------

    def test_body_has_must_not_list(self):
        body = _get_body()
        assert "must not" in body.lower() or "must_not" in body.lower(), (
            "Body must have a MUST NOT list"
        )

    def test_must_not_mentions_no_constraint_code(self):
        body = _get_body()
        body_lower = body.lower()
        assert "constraint" in body_lower and "code" in body_lower, (
            "MUST NOT list must mention no constraint code"
        )

    def test_must_not_mentions_no_runtime_code(self):
        body = _get_body()
        body_lower = body.lower()
        assert "runtime" in body_lower and "code" in body_lower, (
            "MUST NOT list must mention no runtime code"
        )

    def test_must_not_mentions_no_naming(self):
        body = _get_body()
        body_lower = body.lower()
        assert "naming" in body_lower, "MUST NOT list must mention no naming"

    def test_must_not_mentions_no_skip_tier_conflict(self):
        body = _get_body()
        body_lower = body.lower()
        assert "skip" in body_lower and "conflict" in body_lower, (
            "MUST NOT list must mention no skip tier conflict"
        )

    # ------------------------------------------------------------------
    # Body: Final Response Contract
    # ------------------------------------------------------------------

    def test_body_has_final_response_contract(self):
        body = _get_body()
        assert (
            "response contract" in body.lower() or "final response" in body.lower()
        ), "Body must have a Final Response Contract section"

    def test_final_response_contract_mentions_tier_rationale(self):
        body = _get_body()
        body_lower = body.lower()
        assert "tier" in body_lower and "rationale" in body_lower, (
            "Final Response Contract must mention tier + rationale"
        )

    def test_final_response_contract_mentions_provider_rationale(self):
        body = _get_body()
        body_lower = body.lower()
        assert "provider" in body_lower and "rationale" in body_lower, (
            "Final Response Contract must mention provider + rationale"
        )

    def test_final_response_contract_mentions_tools_per_tool_rationale(self):
        body = _get_body()
        body_lower = body.lower()
        assert "tool" in body_lower and "rationale" in body_lower, (
            "Final Response Contract must mention tools + per-tool rationale"
        )

    def test_final_response_contract_mentions_tier_conflict_warnings(self):
        body = _get_body()
        body_lower = body.lower()
        assert "conflict" in body_lower and (
            "warning" in body_lower or "warn" in body_lower
        ), "Final Response Contract must mention tier conflict warnings"

    def test_final_response_contract_mentions_capability_picker_markdown(self):
        body = _get_body()
        body_lower = body.lower()
        assert "capability picker" in body_lower, (
            "Final Response Contract must mention complete capability picker markdown"
        )

    def test_final_response_contract_mentions_discovery_status(self):
        body = _get_body()
        body_lower = body.lower()
        assert "discovery" in body_lower and "status" in body_lower, (
            "Final Response Contract must mention discovery status"
        )
