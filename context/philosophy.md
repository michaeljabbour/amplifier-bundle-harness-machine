# Harness Engineering Principles

## Core Belief

A constrained agent that always acts legally is more valuable than an unconstrained agent that sometimes acts optimally. Constraints are not limitations — they are guarantees.

## Six Principles

### 1. Constraints Over Suggestions

A suggestion says "you should stay within bounds." A constraint makes it impossible to leave. Harnesses enforce — they do not advise.

- Bad: "Please only propose legal moves"
- Good: `if not is_legal_action(board, action): reject(action)`

When designing a harness, ask: "If the LLM ignores this entirely, does the constraint still hold?" If the answer is no, it is a suggestion, not a constraint.

### 2. Enforcement Over Trust

Never assume the constrained agent will cooperate. The harness must enforce correctness even when the agent actively tries to circumvent it.

Three enforcement layers, in order of strength:

| Layer | Mechanism | Example | Bypassed By |
|-------|-----------|---------|-------------|
| **Behavioral** (soft) | Instructions, context, SKILL.md | "Only propose moves within the board" | Ignoring instructions |
| **Enforcement** (hard) | Hook deny/modify, code validation | `tool:pre` hook rejects illegal tool calls | Nothing short of kernel modification |
| **Policy** (programmatic) | Governance rules, audit trail, compliance | Action logged + reviewed before execution | Administrative override only |

Use the weakest layer sufficient for the risk. But never use ONLY the behavioral layer for safety-critical constraints.

### 3. Evidence-Based Verification

No harness is correct until measured. Correctness claims require:

- **Novel test rollouts** — not the training data, not the examples from the spec
- **Quantitative metrics** — legal action rate, reward measurement, not "looks right"
- **Fresh evidence** — from THIS session, not a previous run

The Gate Function applies to harness verification just as it does to code verification: IDENTIFY the metric, RUN the evaluation, READ the output, VERIFY it confirms the claim, ONLY THEN make the claim.

### 4. YAGNI on Constraints

Add constraints for observed problems, not hypothetical ones. Every constraint narrows the action space. Over-constraining is as dangerous as under-constraining — it forces the agent into suboptimal actions or makes valid actions unreachable.

Signs of over-constraining:
- Legal action rate drops below 100% because valid actions are rejected
- The agent cannot find any legal action and deadlocks
- Constraints conflict with each other

Signs of under-constraining:
- Illegal actions pass validation
- The agent causes side effects the harness should prevent

Start minimal. Add constraints when evaluation reveals gaps. Remove constraints when they reject valid actions.

### 5. Composition Over Monolith

A nano-amplifier with 5 focused constraints composes better than a monolithic harness with 50 entangled rules.

Composition principles:
- Each nano-amplifier constrains ONE concern (filesystem boundaries, tool permissions, domain safety)
- Nano-amplifiers compose via Amplifier's `includes:` mechanism
- Conflicts between composed nano-amplifiers surface as evaluation failures, not silent bugs
- Test each nano-amplifier independently BEFORE composing

### 6. Convergence Is Not Guaranteed

The refinement loop (generator → critic → refiner → evaluator) is a search process. Search processes can:

- **Converge fast** — most simple environments, 5-10 iterations
- **Converge slow** — complex action spaces, 50+ iterations
- **Plateau** — heuristic flat for many iterations, then breakthrough
- **Fail to converge** — environment too complex or constraints too tight

Patience and checkpoint_best are your safety nets. Never discard a 95% harness chasing 100%. A harness that achieves 95% legal action rate and ships is infinitely more valuable than a 100% harness that never finishes.
