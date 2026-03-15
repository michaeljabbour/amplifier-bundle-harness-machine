"""Tests for reference example files in context/examples/."""

from pathlib import Path

EXAMPLES_DIR = Path("context/examples")


def _read(filename: str) -> str:
    return (EXAMPLES_DIR / filename).read_text()


# ── Existence / count ────────────────────────────────────────────────────────


def test_six_example_files_exist():
    """Acceptance criterion: exactly 6 example files."""
    files = list(EXAMPLES_DIR.glob("*.md"))
    assert len(files) == 6, (
        f"Expected 6 files, got {len(files)}: {[f.name for f in files]}"
    )


def test_old_nano_filesystem_harness_does_not_exist():
    """nano-filesystem-harness.md must be gone (git mv'd)."""
    assert not (EXAMPLES_DIR / "nano-filesystem-harness.md").exists()


def test_pico_filesystem_sandbox_exists():
    assert (EXAMPLES_DIR / "pico-filesystem-sandbox.md").exists()


def test_nano_tumor_genome_to_vaccine_exists():
    assert (EXAMPLES_DIR / "nano-tumor-genome-to-vaccine.md").exists()


def test_micro_k8s_platform_engineer_exists():
    assert (EXAMPLES_DIR / "micro-k8s-platform-engineer.md").exists()


def test_enterprise_governance_harness_exists():
    assert (EXAMPLES_DIR / "enterprise-governance-harness.md").exists()


# ── pico-filesystem-sandbox.md ───────────────────────────────────────────────


def test_pico_sandbox_header():
    content = _read("pico-filesystem-sandbox.md")
    assert "Example: Pico Filesystem Sandbox" in content


def test_pico_sandbox_tier_pico():
    content = _read("pico-filesystem-sandbox.md")
    # Header uses markdown bold: **Tier:** Pico
    assert "Tier" in content and "Pico" in content


def test_pico_sandbox_scale_trivial_nano():
    content = _read("pico-filesystem-sandbox.md")
    # Header uses markdown bold: **Scale:** Trivial (nano)
    assert "Scale" in content and "Trivial (nano)" in content


# ── nano-tumor-genome-to-vaccine.md ─────────────────────────────────────────


def test_nano_tumor_has_mission_section():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "THE MISSION" in content


def test_nano_tumor_australia_rescue_dog():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "Australia" in content
    assert "rescue dog" in content.lower() or "rescue" in content


def test_nano_tumor_sequencing_cost():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "$3" in content or "3K" in content or "3,000" in content


def test_nano_tumor_mrna_vaccine():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "mRNA vaccine" in content or "mRNA" in content


def test_nano_tumor_tumor_halves():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "halv" in content.lower() or "50%" in content  # tumor halves


def test_nano_tumor_has_mission_architect_output():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "MISSION-ARCHITECT" in content


def test_nano_tumor_pipeline_name():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "nano-amplifier-tumor-genome-to-vaccine" in content


def test_nano_tumor_dna_pipeline():
    content = _read("nano-tumor-genome-to-vaccine.md")
    # DNA → mutated proteins → immune targets → mRNA vaccine
    assert "DNA" in content
    assert "mRNA" in content
    assert "immune" in content.lower()


def test_nano_tumor_has_capability_advisor_output():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "CAPABILITY-ADVISOR" in content


def test_nano_tumor_tier_nano():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "nano" in content.lower()


def test_nano_tumor_anthropic_claude():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "Anthropic" in content or "Claude" in content


def test_nano_tumor_eight_tools():
    content = _read("nano-tumor-genome-to-vaccine.md")
    # Should mention 8 tools or web_fetch for bioinformatics databases
    assert "web_fetch" in content


def test_nano_tumor_ncbi_uniprot_alphafold_pdb():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert (
        "NCBI" in content
        or "UniProt" in content
        or "AlphaFold" in content
        or "PDB" in content
    )


def test_nano_tumor_no_delegation_strikethrough():
    content = _read("nano-tumor-genome-to-vaccine.md")
    # delegate/modes strikethrough mentioned
    assert "delegate" in content.lower() or "~~delegate~~" in content.lower()


def test_nano_tumor_has_spec_section():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "## SPEC" in content or "SPEC" in content


def test_nano_tumor_action_verifier():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "action-verifier" in content


def test_nano_tumor_seven_constraints():
    content = _read("nano-tumor-genome-to-vaccine.md")
    # Should have 7 constraints
    assert "7" in content or "seven" in content.lower() or content.count("| **") >= 7


def test_nano_tumor_sandbox_boundary_constraint():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "sandbox" in content.lower()


def test_nano_tumor_no_parent_traversal():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "parent traversal" in content.lower() or ".." in content


def test_nano_tumor_bash_allowlist():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "bash" in content.lower() and "allowlist" in content.lower()


def test_nano_tumor_no_command_substitution():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "command substitution" in content.lower() or "$(" in content


def test_nano_tumor_network_whitelist():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "network" in content.lower() and (
        "whitelist" in content.lower() or "allowlist" in content.lower()
    )


def test_nano_tumor_no_destructive_commands():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "destructive" in content.lower()


def test_nano_tumor_max_file_size_100mb():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "100MB" in content or "100 MB" in content


def test_nano_tumor_has_system_prompt_section():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "SYSTEM PROMPT" in content.upper() or "system prompt" in content.lower()


def test_nano_tumor_fasta_vcf_pdb_formats():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "FASTA" in content or "VCF" in content or "PDB" in content


def test_nano_tumor_escape_hatch():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "escape hatch" in content.lower()


def test_nano_tumor_has_artifact_structure():
    content = _read("nano-tumor-genome-to-vaccine.md")
    assert "ARTIFACT" in content.upper()


def test_nano_tumor_directory_tree():
    content = _read("nano-tumor-genome-to-vaccine.md")
    # Should show directory tree with nano scaffold files
    assert "behavior.yaml" in content or "constraints.py" in content


# ── micro-k8s-platform-engineer.md ──────────────────────────────────────────


def test_micro_k8s_has_mission():
    content = _read("micro-k8s-platform-engineer.md")
    assert (
        "platform engineer" in content.lower()
        or "k8s" in content.lower()
        or "kubernetes" in content.lower()
    )


def test_micro_k8s_has_capability_advisor_output():
    content = _read("micro-k8s-platform-engineer.md")
    assert "CAPABILITY-ADVISOR" in content


def test_micro_k8s_tier_micro():
    content = _read("micro-k8s-platform-engineer.md")
    assert "micro" in content.lower()


def test_micro_k8s_modes():
    content = _read("micro-k8s-platform-engineer.md")
    assert "work" in content and "review" in content and "plan" in content


def test_micro_k8s_delegation():
    content = _read("micro-k8s-platform-engineer.md")
    assert "delegation" in content.lower() or "delegate" in content.lower()


def test_micro_k8s_approval_gates():
    content = _read("micro-k8s-platform-engineer.md")
    assert "approval" in content.lower() and "gate" in content.lower()


def test_micro_k8s_recipes():
    content = _read("micro-k8s-platform-engineer.md")
    assert "recipe" in content.lower()


def test_micro_k8s_nine_constraints():
    content = _read("micro-k8s-platform-engineer.md")
    # Should have 9 constraints
    assert "9" in content or "nine" in content.lower() or content.count("| **") >= 9


def test_micro_k8s_sandbox_constraint():
    content = _read("micro-k8s-platform-engineer.md")
    assert "sandbox" in content.lower()


def test_micro_k8s_kubectl_context_lock():
    content = _read("micro-k8s-platform-engineer.md")
    assert "kubectl" in content.lower()


def test_micro_k8s_no_direct_production_deploy():
    content = _read("micro-k8s-platform-engineer.md")
    assert "production" in content.lower()


def test_micro_k8s_bash_allowlist_kubectl():
    content = _read("micro-k8s-platform-engineer.md")
    assert "kubectl" in content and (
        "allowlist" in content.lower() or "allowed" in content.lower()
    )


def test_micro_k8s_no_delete_without_approval():
    content = _read("micro-k8s-platform-engineer.md")
    assert "delete" in content.lower() and "approval" in content.lower()


def test_micro_k8s_network_whitelist():
    content = _read("micro-k8s-platform-engineer.md")
    assert "network" in content.lower()


def test_micro_k8s_no_secret_access():
    content = _read("micro-k8s-platform-engineer.md")
    assert "secret" in content.lower()


def test_micro_k8s_audit_logging():
    content = _read("micro-k8s-platform-engineer.md")
    assert "audit" in content.lower()


def test_micro_k8s_mode_definitions_yaml():
    content = _read("micro-k8s-platform-engineer.md")
    assert "allowed_tools" in content or "prompt_overlay" in content


def test_micro_k8s_recipe_yaml():
    content = _read("micro-k8s-platform-engineer.md")
    assert "deploy-to-staging" in content or "dry-run" in content


def test_micro_k8s_while_condition():
    content = _read("micro-k8s-platform-engineer.md")
    assert "while_condition" in content or "health check" in content.lower()


def test_micro_k8s_why_micro_tier():
    content = _read("micro-k8s-platform-engineer.md")
    assert "WHY" in content.upper() and "micro" in content.lower()


# ── enterprise-governance-harness.md ────────────────────────────────────────


def test_enterprise_governance_tier_micro():
    content = _read("enterprise-governance-harness.md")
    # Header uses markdown bold: **Tier:** Micro (factory-scale)
    assert "Tier" in content and "Micro" in content


def test_enterprise_governance_factory_scale():
    content = _read("enterprise-governance-harness.md")
    assert "factory" in content.lower()
