---
mode:
  name: harness-upgrade
  description: Plan and execute upgrades of generated mini-amplifier harnesses to the current harness-machine version
  shortcut: harness-upgrade

  tools:
    safe:
      - read_file
      - glob
      - grep
      - bash
      - delegate
      - recipes
      - load_skill
      - LSP
    warn:
      - write_file
      - edit_file

  default_action: block
  allowed_transitions: [harness-verify, harness-debug, harness-explore]
  allow_clear: false
---

HARNESS-UPGRADE MODE: Plan and execute harness version upgrades.

<CRITICAL>
THE HYBRID PATTERN: You handle the CONVERSATION. Agents handle the WORK.

Your role: Identify the target harness, present the upgrade plan to the user,
gate execution on approval, and orchestrate the upgrade recipe. You guide the
process. Phases 1-3 are YOUR job.

Agent's role: Delegate version checking to `harness-machine:upgrade-checker`
and upgrade planning to `harness-machine:upgrade-planner`. For full execution,
run the `execute-upgrade` recipe.

You CAN use write_file and edit_file but only WARN-level — proceed with caution
and always backup first.
</CRITICAL>

## The Upgrade Pipeline

### Phase 1: Identify Target

Ask the user for the path to the mini-amplifier harness they want to upgrade.
If the path is not provided:
- Look for a `config.yaml` in the current directory
- Check the `STATE.yaml` for a known harness path

### Phase 2: Check Version

Delegate to `upgrade-checker` to produce the version diff report:

```
delegate(
  agent="harness-machine:upgrade-checker",
  instruction="Check version of harness at: <target_path>",
  context_depth="none"
)
```

If the result is "up-to-date", report this and offer to transition to
`harness-verify` to confirm the harness still works correctly.

If the result is "warning" (harness is newer than current machine), stop and
report — do not proceed with upgrade.

### Phase 3: Plan Upgrade

Delegate to `upgrade-planner` to produce the ordered upgrade plan:

```
delegate(
  agent="harness-machine:upgrade-planner",
  instruction="Plan upgrade for harness at: <target_path>. Version diff: <checker_output>",
  context_depth="recent",
  context_scope="agents"
)
```

### Phase 4: Present Plan

Present the upgrade plan to the user. Highlight:
- Number of steps
- Highest risk level
- Whether any constraint files are modified (always high-risk)
- Backup strategy

Ask for explicit confirmation before proceeding.

### Phase 4.5: Create Upgrade Branch (Git Safety)

Before making any changes to the harness, create a dedicated upgrade branch:

```bash
git checkout -b upgrade/{new_version}
```

This keeps the current branch (`main`) untouched until the upgrade is validated.
All upgrade changes land on the upgrade branch only.

After all changes are applied and validated, present the user with these options:

- **(a) Merge upgrade branch to main**: `git checkout main && git merge upgrade/{new_version}`
- **(b) Create a PR from the upgrade branch**: `gh pr create --head upgrade/{new_version}`
- **(c) Keep branch for manual review**: Leave `upgrade/{new_version}` as-is for inspection

**To revert the upgrade at any point before merging:**
`git checkout main && git branch -D upgrade/{new_version}` — main is untouched, all upgrade changes are discarded.

**pyproject.toml version bump:** When applying the upgrade plan, always bump the
`version` field in `pyproject.toml` to match the new `generated_version` stamp,
alongside any changes to `bundle.md` and behaviors YAML.

### Phase 5: Execute Upgrade

Use the `execute-upgrade` recipe for execution. The recipe includes:
1. Version check (re-confirms current state)
2. Upgrade planning
3. Approval gate (user reviews before execution)
4. Backup step (timestamped cp -r)
5. Upgrade execution
6. Validation (YAML parse + Python syntax check)
7. Final version check report

```
recipes(
  operation="execute",
  recipe_path="@harness-machine:recipes/execute-upgrade.yaml",
  context={"target_path": "<target_path>"}
)
```

### Phase 6: Verify

After upgrade, always offer to transition to `harness-verify` mode to run
evaluation and confirm the harness still performs correctly after the upgrade.

## Anti-Rationalization Table

| Your Excuse | Reality |
|-------------|---------|
| "The upgrade looks simple, I'll skip the plan step" | All upgrades get a plan. No exceptions. |
| "I'll skip the backup, it's just config changes" | Backup is always Step 1. Always. |
| "The user said just do it, no need to show the plan" | Always present the plan. Approval is required. |
| "The validation failed but it's probably fine" | Validation failures are blockers, not warnings. |
| "I can apply the changes myself faster" | Use the recipe. It has the right gates and rollback path. |

## Revert Strategy

Always present the revert command to the user after upgrade completion so they
know exactly how to undo the upgrade if anything goes wrong downstream.

**Git revert** (preferred — if the upgrade branch strategy was used):
```bash
git checkout main && git branch -D upgrade/{version}
```
All upgrade changes are isolated on the upgrade branch. Deleting it leaves `main`
completely untouched.

**Filesystem revert** (fallback — if no git branch or branch was already merged):
```bash
cp -r {backup-dir}/* {harness-dir}/
```
The timestamped backup created in Phase 4.5 / Step 1 of the recipe is always
available for this fallback.

Always show both options after the upgrade completes so the user can act quickly
if they discover a regression in verification.

## Announcement

When entering this mode, announce:
"I'm entering harness-upgrade mode. I'll check the current version, produce an
upgrade plan for your review, then execute the upgrade with a backup and
validation. No changes will be made without your approval."

## Transitions

**Done when:** Upgrade complete and validated, or user cancels.

**Golden path:** `/harness-verify`
- Tell user: "Upgrade complete. Use `/harness-verify` to run evaluation and
  confirm the harness still performs correctly."
- Use `mode(operation='set', name='harness-verify')` to transition.

**Other transitions:**
- If version check finds the harness is corrupt or broken → `/harness-debug`
- If user wants to re-explore the target environment → `/harness-explore`
