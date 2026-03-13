# The Harness Machine Pattern

## Core Insight

LLMs can automatically generate constraint code that achieves 100% legal action rates — but only with the right generation loop. Raw generation fails. Iterative refinement with antagonistic review and quantitative evaluation converges reliably.

## Seven Components

### 1. Progressive Specification

Three layers of specification, each gating the next:

**Layer 1 — Environment Map (from `/harness-explore`)**
- What actions exist in this environment?
- Which actions are legal vs illegal, and under what conditions?
- Can legality be defined programmatically?
- Feasibility assessment: can this environment be harnessed at all?

**Layer 2 — Harness Specification (from `/harness-spec`)**
- `harness_type`: action-filter, action-verifier, or code-as-policy
- `harness_scale`: nano, single, library, factory, or self-improving
- Constraint list with rationale for each
- Acceptance criteria (legal action rate target, reward threshold)

**Layer 3 — Implementation Plan (from `/harness-plan`)**
- For single harness: which functions to write, what tests, TDD tasks
- For factory: STATE.yaml schema, template design, environment list

**Gating rule:** Each layer requires the previous layer to be validated before proceeding.

### 2. YAML State Persistence (Factory Track)

For factory-scale generation, state lives in files, not sessions:

**STATE.yaml** — Machine-readable truth:
- Environment list with per-environment status
- Best harness candidate per environment with legal action rate
- Thompson sampling tree state (arm counts, rewards)
- `next_action` field for the next session
- Updated after EVERY iteration

**CONTEXT-TRANSFER.md** — Human-readable session handoff:
- Reverse-chronological session summaries
- Design decisions about constraint strategies
- Convergence observations per environment

**SCRATCH.md** — Disposable working memory for current session.

### 3. Recipe-Driven Iteration

The refinement loop is a recipe, not a manual process:

**Outer loop** (`harness-refinement-loop.yaml`):
1. Read current harness state
2. Check convergence (legal action rate >= target?)
3. Dispatch single iteration (inner loop)
4. After iteration, re-read state
5. If not converged and patience not exhausted, loop
6. On timeout: return best achieved

**Inner loop** (`harness-single-iteration.yaml`):
1. Generate: harness-generator produces/refines constraint code
2. Critique: harness-critic reviews against spec
3. Refine: harness-refiner improves based on critique
4. Evaluate: harness-evaluator measures legal action rate

### 4. Working Session Protocol (Factory Track)

Each factory session follows a strict protocol:

**Orientation (read-only):**
1. Read STATE.yaml — what's done, what's next
2. Read CONTEXT-TRANSFER.md — recent decisions
3. Read harness specification
4. Read current best harness candidate

**Work loop (per iteration):**
1. Mark iteration in-progress
2. Run the generate/critique/refine/evaluate pipeline
3. Compare result against best-so-far
4. If improved, save as new best candidate
5. Update STATE.yaml with metrics
6. Record observations in CONTEXT-TRANSFER.md

**Stop conditions:**
- Convergence achieved (legal action rate >= target)
- Patience exhausted (N iterations without improvement)
- Session budget consumed
- Unrecoverable error

### 5. Antagonistic Review

Every generated harness is reviewed by a fresh critic with no shared context from the generator.

The critic looks for:
- **Coverage gaps** — action patterns not covered by constraints
- **Over-constraints** — valid actions incorrectly rejected
- **Edge cases** — boundary conditions where constraints may fail
- **Consistency** — constraints that conflict with each other

The critic's verdict (APPROVED or NEEDS CHANGES) gates whether refinement runs.

### 6. Three-Tier Evaluation

| Tier | Scope | When | Metric |
|------|-------|------|--------|
| Per-function | Individual constraint functions | After each generation | Function correctness |
| Per-harness | Complete harness against environment | After each iteration | Legal action rate |
| Cross-environment | All harnesses in a factory run | After factory completion | Aggregate pass rate |

Evaluation uses novel test rollouts — random seeds, unseen board states, scenarios not in the training examples.

### 7. Convergence Health Check

Monitor the refinement loop for pathological patterns:

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| Flat heuristic for 10+ iterations | Search stuck in local optimum | Increase exploration (Thompson sampling temperature) |
| Oscillating heuristic | Refinement undoing previous improvements | Lock successful constraints, refine only failing ones |
| Monotonic decline | Constraints getting worse | Reset to best checkpoint, try different approach |
| Slow steady climb | Normal convergence | Continue with patience |

The `patience` parameter (default: 15 iterations) triggers plateau diagnosis automatically.
