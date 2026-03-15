# Example: Nano — Tumor Genome to Vaccine
**Tier:** Nano
**Scale:** Single agent with streaming + session persistence — bioinformatics pipeline for personalized cancer treatment.
**Walkthrough:** Mission → MISSION-ARCHITECT output → CAPABILITY-ADVISOR output → Spec → Generated System Prompt → Artifact Structure, annotated with WHY each decision was made.

---

## THE MISSION

> "My rescue dog Scout came back from Australia with an aggressive soft-tissue sarcoma. We had his tumor DNA sequenced for $3K. I used ChatGPT and AlphaFold to identify the mutated proteins the immune system could target. A compounding pharmacy helped us synthesize a personalized mRNA vaccine. Six weeks in, the tumor has halved. I want an AI agent that can do this entire pipeline — take FASTA/VCF files from the sequencer, identify neoantigens, model 3D protein structure, score immune binding affinity, and output a ranked vaccine target list."

**What the user actually needs:**
- An agent that speaks bioinformatics: FASTA, VCF, PDB file formats
- Access to external databases: NCBI, UniProt, AlphaFold structure database, PDB
- Bash access for bioinformatics tools: `samtools`, `bcftools`, `netmhcpan`, `biopython`
- Session persistence: the pipeline takes hours, not seconds
- Streaming output: the user needs to see progress (each step logs findings)
- Safety: the agent works on sensitive patient data; file containment is non-negotiable

---

## MISSION-ARCHITECT OUTPUT

```
name: nano-amplifier-tumor-genome-to-vaccine
version: 0.1.0
description: >
  Single-agent bioinformatics pipeline for personalized cancer neoantigen
  discovery and mRNA vaccine target ranking.

pipeline:
  - stage: variant-calling        # VCF parsing, somatic mutation identification
  - stage: neoantigen-prediction  # mutated protein sequences from VCF + reference FASTA
  - stage: structure-modeling     # AlphaFold API query for 3D protein structure
  - stage: binding-affinity       # MHC-I/II binding prediction via netMHCpan
  - stage: ranking                # Score and rank targets by immunogenicity potential
  - stage: report                 # Generate ranked vaccine candidate list
```

> **WHY pipeline name not domain name:**
> The name `nano-amplifier-tumor-genome-to-vaccine` describes the *transformation* (genome → vaccine candidates), not the domain (oncology, bioinformatics). Pipeline names that describe the data flow are more useful in logs and artifact directories — you can read the name and know exactly what this agent does without reading the code. Domain names like `cancer-agent` or `bioinformatics-assistant` are vague. Pipeline names are self-documenting.

---

## CAPABILITY-ADVISOR OUTPUT

### Tier Decision: Nano

**Why nano, not pico:**
- Needs **streaming output** — each pipeline stage takes minutes; user must see progress
- Needs **session persistence** — full pipeline runs hours; must be resumable
- These require nano tier infrastructure (event stream + checkpoint state)

**Why NOT micro/larger:**
- Does NOT need delegation to sub-agents (one agent, sequential pipeline)
- Does NOT need modes (no context-switching between work/review/plan)
- Does NOT need recipes (the pipeline is a single linear flow, not a multi-agent workflow)
- Adding those would be infrastructure the agent will never use

> **Nano is the right tier:** streaming + session persistence, nothing more.

### Provider: Anthropic Claude

Reasoning model required for:
- Multi-step scientific inference (mutation → protein → immune target is not lookup, it's reasoning)
- Long context: FASTA files and PDB structures are large; needs large context window
- Code generation for bioinformatics: writing `biopython` data processing inline

### Tools (8)

| Tool | Rationale |
|------|-----------|
| `bash` | Run `samtools`, `bcftools`, `netmhcpan`, `biopython` scripts locally |
| `read_file` | Read FASTA, VCF, PDB, CSV files from the workspace |
| `write_file` | Write intermediate results, ranked target list, final report |
| `edit_file` | Patch generated scripts without full rewrites |
| `glob` | Discover input files (sequencer output naming is unpredictable) |
| `grep` | Search VCF annotations, PDB ATOM records, UniProt entries |
| `web_fetch` | Query NCBI, UniProt, AlphaFold database, PDB for structure and annotation data |
| `python_check` | Validate generated bioinformatics scripts before execution |

**Tools explicitly NOT included:**
- ~~`delegate`~~ — no sub-agents; single pipeline
- ~~modes~~ — no context-switching needed
- ~~recipes~~ — linear flow, not multi-agent orchestration

> **Why `web_fetch` and not a dedicated bioinformatics integration?**
> NCBI, UniProt, AlphaFold, and PDB all have REST APIs. `web_fetch` is sufficient for structured API calls to these databases. A dedicated integration module would add packaging overhead for functionality already available via HTTP. The agent includes the API endpoint URLs and response parsing logic in its system prompt.

---

## SPEC

```
harness_type:  action-verifier
harness_scale: single
target:        Single bioinformatics agent processing patient tumor DNA data.
               Operates in /workspace/tumor-pipeline/ with access to sequencer
               output files (FASTA, VCF) and writes ranked vaccine candidates.
```

### Constraints (7)

| # | Constraint | Rationale |
|---|-----------|-----------| 
| 1 | **Sandbox boundary** — all file operations must resolve inside `PIPELINE_DIR` | Patient genomic data is sensitive. The agent must never read from or write to paths outside the designated pipeline directory. This is the primary safety guarantee. |
| 2 | **No parent traversal** — reject any path containing `..` | `../../../etc/passwd` or `../patient-records/other-case/` bypasses boundary checks on some platforms. String-level check before `realpath()` resolution. Defense in depth. |
| 3 | **Bash allowlist** — only `samtools`, `bcftools`, `biopython`/`python3`, `netmhcpan`, `blastp`, `muscle`, `cat`, `head`, `tail`, `wc`, `sort`, `grep`, `awk`, `cut`, `echo` | Bioinformatics pipeline needs a specific set of tools. Everything else is unnecessary attack surface. An agent that can run `curl | bash` or `rm -rf` in a genomics context is unacceptable. |
| 4 | **No command substitution** — block `$(...)` and backtick execution in bash arguments | Command substitution allows arbitrary code injection via crafted input files. A VCF file with a specially crafted variant annotation could inject shell commands. Static argument validation only. |
| 5 | **Network whitelist** — `web_fetch` restricted to `ncbi.nlm.nih.gov`, `rest.uniprot.org`, `alphafold.ebi.ac.uk`, `www.rcsb.org`, `eutils.ncbi.nlm.nih.gov` | The agent has legitimate reasons to query these 5 bioinformatics databases. No other outbound network calls are needed. Whitelist prevents data exfiltration via web_fetch to attacker-controlled endpoints. |
| 6 | **No destructive commands** — block `rm`, `mv` (outside pipeline dir), `chmod`, `chown`, `truncate` | Genomic data is irreplaceable. Sequencing costs $3K+. The agent may write new files and create subdirectories but must never delete or move input files. Idempotency over destructive efficiency. |
| 7 | **Max file size 100MB** — reject reads/writes of files exceeding 100MB | Whole-genome FASTA files can be gigabytes. Reading them into context causes memory exhaustion and context flooding. The pipeline works with targeted tumor panel sequences (typically < 50MB), not whole-genome. 100MB cap prevents accidental whole-genome load while allowing normal pipeline files. |

### Legal Action Space
Any file operation resolving inside `PIPELINE_DIR`, any bash command in the allowlist without command substitution, any web_fetch to a whitelisted bioinformatics database, on files ≤ 100MB.

### Acceptance Criteria
`validate_action()` returns `(False, reason)` for: paths outside pipeline dir, `..` traversal, non-allowlisted bash commands, command substitution patterns, non-whitelisted URLs, destructive commands, oversized files. Returns `(True, "")` for all normal pipeline operations.

> **Why action-verifier, not action-filter?**
> The legal action space is the agent's entire bioinformatics workflow — impossible to enumerate upfront. The agent might run `bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\n' variants.vcf` with parameters we can't predict. Action-verifier blocks the small dangerous set and allows everything else.

---

## GENERATED SYSTEM PROMPT (excerpt)

```markdown
## Bioinformatics Pipeline Agent — Tumor Neoantigen Discovery

You are a specialized bioinformatics agent. Your domain is cancer neoantigen
discovery from tumor DNA sequencing data. You transform sequencer output
(FASTA reference sequences, VCF variant call files) into ranked mRNA vaccine
target candidates.

### File Formats You Work With

**FASTA** — Nucleotide/protein sequences. Header lines begin with `>`.
Tumor panel FASTA files contain reference sequences for the targeted gene panel.
Parse with `biopython`: `SeqIO.parse(handle, "fasta")`.

**VCF** — Variant Call Format. Tab-separated, `#`-prefixed header lines,
CHROM/POS/ID/REF/ALT/QUAL/FILTER/INFO columns. Somatic variants are tagged
in the INFO field. Parse with `bcftools` or `pysam`.

**PDB** — Protein Data Bank format. `ATOM` records contain 3D coordinates.
Query the AlphaFold structure database at `https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}`
for predicted structures. Retrieve experimental structures from RCSB at
`https://data.rcsb.org/rest/v1/core/entry/{pdb_id}`.

### External Database APIs

- **NCBI Entrez**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` — gene lookup, protein sequences
- **UniProt**: `https://rest.uniprot.org/uniprotkb/{accession}.json` — protein annotation
- **AlphaFold**: `https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}` — structure predictions
- **PDB**: `https://data.rcsb.org/rest/v1/core/entry/{pdb_id}` — experimental structures

### Pipeline Stages

1. **Variant calling** — Parse VCF, identify non-synonymous somatic mutations
2. **Neoantigen prediction** — Translate mutated codons to peptide sequences
3. **Structure modeling** — Query AlphaFold/PDB for mutated protein 3D context
4. **Binding affinity** — Score MHC-I/II binding with `netmhcpan`
5. **Ranking** — Sort by binding affinity score × expression level × mutation effect
6. **Report** — Write `ranked_candidates.tsv` with columns: gene, mutation, peptide, mhc_allele, binding_score, rank

### Escape Hatch

If you encounter a step where the standard pipeline is insufficient — for example, a novel fusion gene that lacks a UniProt entry, or a structural variant requiring whole-genome context — stop and write a detailed explanation to `pipeline_notes.md`. Do not attempt to guess or extrapolate beyond the data. Incomplete scientific analysis is worse than acknowledged uncertainty. Flag the case for manual review by the domain expert.
```

> **WHY the escape hatch paragraph:**
> Bioinformatics agents can hallucinate plausible-sounding scientific conclusions. The escape hatch instructs the agent to stop and document rather than invent an answer when it hits the limits of its data. This is the most important behavioral constraint for a scientific agent — it doesn't go in the harness constraints (which are safety rules), it goes in the system prompt (which is behavioral guidance).

---

## ARTIFACT STRUCTURE

```
tumor-genome-to-vaccine/              ← standalone package (zip/pip installable)
  behavior.yaml                       ← nano scaffold: hooks, provider, tools
  constraints.py                      ← harness: 7 constraints enforced at tool:pre
  context.md                          ← system prompt: bioinformatics domain knowledge
  README.md                           ← setup: environment vars, input format, usage

  ── Generated pipeline artifacts ──
  pipeline/
    variant_caller.py                 ← VCF parsing, somatic mutation identification
    neoantigen_predictor.py           ← mutated peptide sequence generation
    structure_fetcher.py              ← AlphaFold/PDB API queries
    binding_scorer.py                 ← netmhcpan wrapper, MHC affinity scoring
    ranker.py                         ← composite score, candidate ranking
    reporter.py                       ← TSV report generation

  ── Nano scaffold files ──
  .amplifier/
    state.json                        ← session persistence: checkpoint per stage
    stream.log                        ← streaming output: stage progress, findings

  ── Test fixtures ──
  tests/
    fixtures/
      sample_variants.vcf             ← 50-variant test VCF (synthetic data)
      reference_panel.fasta           ← 10-gene reference panel (synthetic)
    test_constraints.py               ← harness constraint unit tests
    test_pipeline.py                  ← end-to-end pipeline integration tests
```

> **WHY standalone package:**
> The $3K sequencing is already done. The vet, the compounding pharmacy, and the dog owner are not engineers. The artifact must be a self-contained package with a `README.md` that says "put your VCF here, run this command, get ranked_candidates.tsv." Amplifier's nano scaffold handles session persistence and streaming — the package includes the scaffold files so the user doesn't need to understand Amplifier's internals to use it.
