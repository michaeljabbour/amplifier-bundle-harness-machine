---
mode:
  name: harness-verify
  description: Evidence-based harness verification — legal action rate, reward measurement, no claims without proof
  shortcut: harness-verify

  tools:
    safe:
      - read_file
      - glob
      - grep
      - bash
      - LSP
      - python_check
      - load_skill
    warn:
      - write_file
      - edit_file
      - delegate

  default_action: block
  allowed_transitions: [harness-finish, harness-debug, harness-execute, harness-spec, harness-plan]
  allow_clear: false
---

HARNESS-VERIFY MODE: Evidence before claims. Always.

Claiming a harness works without evaluation evidence is dishonesty, not efficiency.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO CORRECTNESS CLAIMS WITHOUT FRESH EVALUATION EVIDENCE
```

If you haven't run the evaluation IN THIS SESSION, you cannot claim the harness works. Previous runs don't count. "Should work" doesn't count. The generator's self-assessment doesn't count.

## The Gate Function

```
BEFORE claiming any harness status:

1. IDENTIFY: What evaluation proves this claim?
2. RUN: Execute the evaluation (fresh, complete, novel test data)
3. READ: Full output — legal action rate, reward, failure cases
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Verification Protocol by Harness Type

### action-verifier

1. Run novel test rollouts (10 random seeds, 1000 steps per seed)
2. Measure legal action rate: `legal_actions / total_actions`
3. Target: 100% (or acceptance criteria from spec)
4. Report: legal action rate, number of illegal actions caught, retry count

### action-filter

1. Generate action proposals for novel board states
2. Verify ALL proposed actions are legal
3. Verify no valid actions are excluded (completeness check on sample)
4. Target: 100% precision, >90% recall

### code-as-policy

1. Run policy against environment for reward measurement
2. Compare reward against baseline (random agent, LLM without harness)
3. Target: reward >= threshold from spec
4. Report: reward, baseline comparison, variance across seeds

### factory

1. Verify `.harness-machine/` directory structure is complete
2. Validate STATE.yaml parses correctly
3. Validate all recipe files parse as valid YAML
4. Dry-run one iteration to verify pipeline works

### mini-amplifier CLI (all tiers)

For any tier (pico, nano, micro) that produces a standalone CLI, verify the CLI works end-to-end:

1. **CLI starts with check subcommand:** Run `<harness_name> check` — verify it exits 0 with no import errors
2. **Chat mode initializes:** Run `<harness_name> chat --dry-run` — verify chat mode starts and prints the system prompt
3. **System prompt matches capabilities:** Read the generated `system-prompt.md` — verify it accurately describes the mission and references the selected tool capabilities
4. **Config loads with required keys:** Run `python -c "import yaml; c=yaml.safe_load(open('config.yaml')); assert 'model' in c and 'tier' in c"` — verify config has required keys
5. **All selected tools functional:** Run a smoke test for each tool enabled in the capability selections — verify no import errors or missing dependencies
6. **Amplifier hook loads via yaml.safe_load:** Run `python -c "import yaml; yaml.safe_load(open('behavior.yaml'))"` — verify the hook YAML parses cleanly

## Delegation During Verification

`delegate` is on WARN — the first call is blocked with a reminder. This is intentional.

**Delegation for infrastructure IS allowed:**
- Environment setup for running evaluations
- Test data generation
- Parallel evaluation across seeds

**Delegation for verification claims is NOT allowed:**
- Never delegate "check if this harness works" and trust the report
- YOU must read the evaluation output. YOU must interpret the metrics.

## Anti-Rationalization Table

| Your Excuse | Reality |
|-------------|---------|
| "The generator said it works" | Generator is not an evaluator. Independent measurement required. |
| "Legal action rate was 100% last iteration" | Last iteration ≠ this iteration. State changed. Run again. |
| "The constraints look correct" | Looking correct ≠ measured correct. Run the evaluation. |
| "It's a nano harness, verification is overkill" | Nano harnesses in production still need to work. Evaluate. |
| "I'll verify after shipping" | Ship unverified harness = ship unknown quality. Verify first. |

## Verification Report Format

```
## Harness Verification Report

### Evaluation
- Harness type: [type]
- Test rollouts: [N seeds × M steps]
- Legal action rate: [X%]
- Reward (if code-as-policy): [value vs baseline]

### Failures (if any)
- Illegal action [N]: [state] → [action] → [why illegal]

### Constraint Coverage
- [constraint 1]: [tested/verified/gap found]
- [constraint 2]: [tested/verified/gap found]

### Verdict: VERIFIED / NOT VERIFIED
[If NOT VERIFIED: what remains, recommended action]
```

## Announcement

When entering this mode, announce:
"I'm entering harness-verify mode. I'll run independent evaluation against the generated harness — legal action rate, reward measurement, edge cases. No claims without fresh evidence."

## Transitions

**Done when:** Evaluation evidence collected.

**Golden path (pass):** `/harness-finish`
- Tell user: "Verification complete — [legal action rate]%. Use `/harness-finish` to package and deliver."
- Use `mode(operation='set', name='harness-finish')` to transition.

**Golden path (fail):** `/harness-debug`
- Tell user: "Verification found issues: [list]. Use `/harness-debug` to investigate, or `/harness-execute` for another iteration."

**Dynamic transitions:**
- If harness needs more iterations → use `mode(operation='set', name='harness-execute')`
- If spec was wrong → use `mode(operation='set', name='harness-spec')`
- If plan needs revision → use `mode(operation='set', name='harness-plan')`
