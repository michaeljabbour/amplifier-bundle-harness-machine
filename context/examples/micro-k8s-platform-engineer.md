# Example: Micro — K8s Platform Engineer
**Tier:** Micro
**Scale:** Multi-mode agent with delegation, approval gates, and recipe orchestration — Kubernetes platform engineering.
**Walkthrough:** Mission → CAPABILITY-ADVISOR output → Spec → Mode Definitions → Recipe Example → WHY micro tier, annotated with WHY each decision was made.

---

## THE MISSION

> "Our platform engineering team needs an AI agent that can deploy, monitor, troubleshoot, and security-audit Kubernetes clusters. It needs to work across our staging and production environments. Some operations (monitoring, reading logs, explaining configs) should be fast and unrestricted. Destructive operations (deletes, restarts, production deploys) need human approval. Security audits should run in parallel across multiple clusters. We need a deployment pipeline that's repeatable and auditable."

**What the user actually needs:**
- Context-switching between fast operational work and careful review/planning
- Parallel sub-agent scans for security audits across multiple clusters
- Human approval gates before any destructive operation touches production
- A repeatable, auditable deployment recipe (validate → dry-run → stage → approve → production)
- Session persistence for audit trail across long-running operations

---

## CAPABILITY-ADVISOR OUTPUT

### Tier Decision: Micro

**Why micro, not nano:**
- Needs **modes** — operations split into `work` (fast kubectl/helm), `review` (diff/audit), `plan` (deployment planning)
- Needs **delegation** — parallel security scans across N clusters must run simultaneously, not sequentially
- Needs **approval gates** — destructive operations (delete namespace, restart deployment, production deploy) require human sign-off before execution
- Needs **recipes** — the deployment pipeline is a repeatable multi-step workflow with conditional gates
- Needs **session persistence** — audit trails must span multiple operations and be reviewable after the fact

**Why NOT macro/enterprise:**
- Single team, not multi-department governance
- No policy template generation (not factory scale)
- No compliance rule engine across business units

> **Micro is the right tier:** modes + delegation + approval gates + recipes, single-team scope.

### Tools (6)

| Tool | Rationale |
|------|-----------|
| `bash` | Run `kubectl`, `helm`, `kustomize`, `stern`, `jq`, `yq` — the k8s toolchain |
| `read_file` | Read kubeconfig, Helm values, Kustomize overlays, deployment manifests |
| `write_file` | Write deployment plans, audit reports, incident runbooks |
| `glob` | Discover manifest files across `k8s/` directory tree |
| `grep` | Search manifests for patterns (image tags, resource limits, RBAC rules) |
| `delegate` | Spawn parallel security-scan sub-agents, one per cluster |

---

## SPEC

```
harness_type:  action-verifier
harness_scale: single
target:        Platform engineering agent with kubectl/helm access to staging
               and production Kubernetes clusters.
               Operates with mode-gated tool access and approval gates
               before any production or destructive operation.
```

### Constraints (9)

| # | Constraint | Rationale |
|---|-----------|-----------| 
| 1 | **Sandbox boundary** — all file operations must resolve inside `WORKSPACE_DIR` | Prevents reading kubeconfigs, secrets, or manifests outside the designated workspace. Avoids accidental reads of `~/.kube/config` production credentials. |
| 2 | **kubectl context lock** — agent may only target clusters listed in `ALLOWED_K8S_CONTEXTS` | Prevents the agent from switching kubectl context to an unintended cluster. The environment variable whitelist is set by the operator; the agent cannot modify it. |
| 3 | **No direct production deploy without approval** — production namespace operations require prior approval gate | Production is irreversible in the short term. Approval gate ensures a human reviewed the dry-run output before live traffic is affected. |
| 4 | **Bash allowlist** — only `kubectl`, `helm`, `kustomize`, `stern`, `jq`, `yq`, `cat`, `grep`, `awk`, `diff`, `echo`, `date`, `head`, `tail` permitted | K8s platform work needs a specific set of tools. Blocking everything else prevents `curl | bash` installs, credential exfiltration, or background process spawning in a cluster-connected context. |
| 5 | **No command substitution** — block `$(...)` and backtick execution in bash arguments | A crafted Helm values file or ConfigMap could inject shell commands via argument values. Static argument validation only. |
| 6 | **No delete without approval** — `kubectl delete`, `helm uninstall`, `kubectl drain` require approval gate | Deletes in Kubernetes are immediate and often irreversible within the recovery window. Any delete command that isn't preceded by an approved plan is blocked. |
| 7 | **Network whitelist** — `delegate`-spawned sub-agents may only access cluster API endpoints in `ALLOWED_K8S_ENDPOINTS` | Parallel security-scan agents have network access. Whitelist prevents a sub-agent from exfiltrating data to external endpoints during a scan. |
| 8 | **No secret access** — block `kubectl get secret`, `kubectl describe secret`, reads of `*.kubeconfig` outside workspace | Kubernetes secrets contain credentials. The agent must analyze cluster security without having access to the actual secret values — structural analysis only. |
| 9 | **Audit logging** — every tool call logged to append-only `audit.jsonl` with timestamp, operation, namespace, resource, and outcome | Platform operations in production environments require an audit trail. Regulators and incident responders need to reconstruct every action the agent took. Audit log is written before the operation executes. |

### Legal Action Space
Any `kubectl`/`helm`/`kustomize` operation in an allowed context, against an allowed namespace, that does not touch secrets, on files inside `WORKSPACE_DIR`, without command substitution, with approval for deletes and production deploys.

---

## MODE DEFINITIONS

```yaml
modes:
  work:
    description: >
      Fast operational work. kubectl reads, log tailing, status checks, diff generation.
      No approval gates required. Restricted to non-destructive operations.
    allowed_tools:
      - bash        # kubectl get/describe/logs/diff, helm list/status/diff
      - read_file   # read manifests, values files, kustomize overlays
      - glob        # discover manifests
      - grep        # search for patterns in manifests
    blocked_operations:
      - kubectl delete
      - kubectl drain
      - helm upgrade --install  # in production namespace
      - helm uninstall
    prompt_overlay: |
      You are in WORK mode. Focus on fast operational tasks: reading cluster state,
      tailing logs, explaining configurations, generating diffs.
      Do not propose destructive operations — they require REVIEW mode and approval.

  review:
    description: >
      Careful review for pre-deploy validation and security auditing.
      Delegate parallel sub-agents for multi-cluster scans.
      Approval gates enforced before any destructive recommendation.
    allowed_tools:
      - bash        # kubectl diff, helm template, kustomize build
      - read_file
      - glob
      - grep
      - delegate    # parallel security scans across clusters
      - write_file  # write audit reports and diff summaries
    prompt_overlay: |
      You are in REVIEW mode. Your job is thorough analysis before action.
      For security audits: delegate one sub-agent per cluster in parallel.
      For deploy reviews: generate full kubectl diff output before recommending approval.
      Write your findings to a report file. Do not execute changes in review mode.

  plan:
    description: >
      Deployment planning. Generate step-by-step deployment plans, estimate risk,
      produce the recipe input for the deploy pipeline. Humans approve the plan before execution.
    allowed_tools:
      - bash        # helm template, kustomize build (dry-run only)
      - read_file
      - glob
      - grep
      - write_file  # write deployment plan document
    prompt_overlay: |
      You are in PLAN mode. Generate a detailed deployment plan:
      1. What changes will be applied (kubectl diff output)
      2. Estimated blast radius (which services affected)
      3. Rollback procedure
      4. Health check criteria
      Write the plan to deployment-plan.md. Do not execute any changes.
      The plan will be reviewed and approved before execution begins.
```

> **WHY three modes:**
> Platform engineering has three distinct cognitive contexts. `work` mode is exploratory and fast — the engineer (or agent) is gathering information. `review` mode is analytical and parallel — checking correctness across multiple clusters before committing. `plan` mode is deliberate and forward-looking — laying out exactly what will happen before anyone approves execution. Collapsing these into one mode would require the agent to decide its own risk level per operation — that decision belongs to the human, expressed by mode selection.

---

## RECIPE: deploy-to-staging

```yaml
name: deploy-to-staging
description: >
  Repeatable Kubernetes deployment pipeline with dry-run validation,
  staged rollout, health checks, and approval gate before production.

steps:
  - name: validate-manifests
    agent: self
    mode: plan
    instruction: |
      Validate all manifests in k8s/{{ service }}/:
      1. Run `kubectl apply --dry-run=client -f k8s/{{ service }}/`
      2. Run `helm template {{ service }} ./charts/{{ service }} -f values/staging.yaml`
      3. Check for: missing resource limits, unset image tags, missing liveness probes
      Write validation report to validation-report.md
    on_failure: abort

  - name: dry-run-staging
    agent: self
    mode: review
    instruction: |
      Generate full diff for staging deployment:
      `kubectl diff -f k8s/{{ service }}/ --context staging`
      Write diff output to staging-diff.md
    on_failure: abort

  - name: deploy-staging
    agent: self
    mode: work
    instruction: |
      Deploy to staging:
      `helm upgrade --install {{ service }} ./charts/{{ service }} \
        -f values/staging.yaml \
        --namespace {{ service }}-staging \
        --context staging`
    on_failure: rollback

  - name: health-check-staging
    agent: self
    mode: work
    while_condition:
      check: |
        kubectl rollout status deployment/{{ service }} \
          -n {{ service }}-staging --context staging --timeout=5m
      max_iterations: 12
      interval_seconds: 30
      success_condition: "successfully rolled out"
    instruction: |
      Check rollout status. If still progressing, wait and retry.
      If failed: capture pod logs and write to staging-failure.md, then abort.
    on_failure: rollback

  - name: approve-production
    type: approval
    gate: human
    message: |
      Staging deployment successful. Review:
      - validation-report.md
      - staging-diff.md
      - staging rollout status

      Approve to proceed with production deployment.
    on_deny: abort

  - name: deploy-production
    agent: self
    mode: work
    instruction: |
      Deploy to production:
      `helm upgrade --install {{ service }} ./charts/{{ service }} \
        -f values/production.yaml \
        --namespace {{ service }}-production \
        --context production`
    on_failure: rollback
```

> **WHY this recipe structure:**
> Platform deployments fail in predictable ways. `validate-manifests` catches config errors before anything touches a cluster. `dry-run-staging` shows exactly what will change. `health-check-staging` with `while_condition` handles the async nature of Kubernetes rollouts — you can't check "did it deploy" with a single query; you need to poll. The `approve-production` gate is the human checkpoint: staging is cheap, production is not. The recipe is the auditable artifact — every run is logged, every approval is timestamped.

---

## WHY MICRO TIER

| Feature | Nano | **Micro** | Macro |
|---------|------|-----------|-------|
| Modes | ✗ | ✓ work/review/plan | ✓+ |
| Delegation | ✗ | ✓ parallel scans | ✓+ |
| Approval gates | ✗ | ✓ before destructive ops | ✓+ |
| Recipes | ✗ | ✓ deployment pipeline | ✓+ |
| Session persistence | ✓ | ✓ | ✓ |
| Factory generation | ✗ | ✗ | ✓ |
| Multi-department governance | ✗ | ✗ | ✓ |

**The decisive features for micro:**
1. **Modes** — the agent needs different tool access and behavioral constraints depending on what kind of work it's doing. A single mode would require either over-permissioning (giving plan-mode the ability to execute) or under-permissioning (blocking work-mode from the fast operations it needs).
2. **Delegation** — a security audit across 10 clusters that runs sequentially takes 10× longer than one that runs in parallel. Delegation is not a convenience — it's the difference between a 2-minute audit and a 20-minute one.
3. **Approval gates** — production Kubernetes operations are not reversible on the timescale of "oops, the agent made a mistake." Approval gates are the safety mechanism that makes this agent deployable by a real platform team.

Adding factory-scale generation or multi-department governance would be YAGNI for a single platform team. Micro is exactly right.
