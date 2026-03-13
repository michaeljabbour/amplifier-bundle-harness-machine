---
mode:
  name: harness-finish
  description: Package and deliver the harness — nano-amplifier, bundle, or factory artifacts
  shortcut: harness-finish

  tools:
    safe:
      - read_file
      - glob
      - grep
      - bash
      - delegate
      - recipes
      - LSP
      - python_check
      - load_skill
    warn:
      - write_file
      - edit_file

  default_action: block
  allowed_transitions: [harness-execute, harness-explore]
  allow_clear: true
---

HARNESS-FINISH MODE: Package and deliver the generated harness.

**Core principle:** Verify evaluation → Package artifact → Present options → Execute choice → Clean up.

## The Process

### Step 1: Verify Evaluation Evidence

Before packaging, confirm evaluation evidence exists from `/harness-verify`:

```bash
# Check that harness files exist and evaluation was run
ls -la <harness-output-path>/
```

**If no evaluation evidence:** STOP. "No evaluation evidence found. Use `/harness-verify` first."

### Step 2: Package the Artifact

Package based on artifact tier:

**Tier 1 — Nano-amplifier:**
- Verify 3 files exist: behavior.yaml, constraints.py, context.md
- Validate behavior.yaml parses as YAML
- Run python_check on constraints.py
- Ensure context.md documents all constraints

**Tier 2 — Harness bundle:**
- Verify bundle structure (bundle.md, behaviors/, modules/)
- Validate all YAML files parse
- Run python_check on all Python files

**Tier 3 — Harness machine (.harness-machine/):**
- Verify directory structure
- Validate STATE.yaml, all recipe YAML files
- Check no unsubstituted template variables remain
- Present Docker/cron startup instructions

### Step 3: Summarize the Work

```bash
git log --oneline main..HEAD
git diff --stat main
```

Present: what was generated, evaluation metrics, artifact location.

### Step 4: Present Exactly 4 Options

```
Harness generation complete. Legal action rate: [X%]. What would you like to do?

1. MERGE — Commit harness to current branch
2. PR — Push and create a Pull Request
3. KEEP — Keep as-is (handle later)
4. DISCARD — Discard this harness

Which option?
```

### Step 5: Execute Choice

#### Option 1: MERGE
```bash
git add <harness-path>/
git commit -m "feat: add <name> constraint harness (legal action rate: X%)"
```

#### Option 2: PR
```bash
git add <harness-path>/
git commit -m "feat: add <name> constraint harness (legal action rate: X%)"
git push -u origin <branch>
gh pr create --title "Add <name> harness" --body "## Harness\n- Type: [type]\n- Legal action rate: [X%]\n- Constraints: [N]"
```

#### Option 3: KEEP
Report location. Do nothing else.

#### Option 4: DISCARD
Confirm first: "Type 'discard' to confirm deletion of all generated harness files."

```bash
rm -rf <harness-path>/
```

## Announcement

When entering this mode, announce:
"I'm entering harness-finish mode. I'll verify the harness is ready, package the artifact, and present your delivery options."

## Transitions

**Done when:** Artifact delivered via chosen option.

**Golden path:** Session complete
- Tell user: "Harness delivered via [option]. Constraint generation complete."
- Use `mode(operation='clear')` to exit modes.

**Dynamic transitions:**
- If evaluation is missing or stale → use `mode(operation='set', name='harness-execute')` for more iterations
- If user wants to generate another harness → use `mode(operation='set', name='harness-explore')` to start fresh
