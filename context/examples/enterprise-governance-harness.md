# Example: Enterprise Governance Harness
**Tier:** Micro (factory-scale)
**Scale:** Complex (factory) — NemoClaw-style multi-layer constraints with governance and audit.
**Walkthrough:** Spec → Plan → Artifact (Tier 3 machine), annotated with WHY each decision was made.

---

## SPEC

```
harness_type:  action-filter
harness_scale: factory
target:        Enterprise AI assistants deployed across multiple departments
               (HR, Finance, Legal, Engineering, Customer Support).
               Each department has different data classifications, action permissions,
               and compliance requirements. The factory generates a governance
               harness per department from shared policy templates.
```

### Governance Layers (6)

| Layer | Mechanism | Constraint Type |
|-------|-----------|-----------------|
| **Input moderation** | Screen user prompts for PII, prompt injection, policy violations | Enforcement (hook: provider:request) |
| **Output filtering** | Screen agent responses for credential leakage, toxic content, PII | Enforcement (hook: provider:response) |
| **Action authorization** | Only explicitly permitted actions allowed per department role | Enforcement (hook: tool:pre deny) |
| **Data classification** | Files/records tagged by sensitivity; access requires clearance level | Policy (programmatic check at access time) |
| **Audit trail** | Every action logged with timestamp, user, department, decision | Policy (append-only log) |
| **Compliance rules** | GDPR right-to-erasure, SOX financial controls, HIPAA data residency | Policy (rule engine) |

### Department-Specific Action Permissions

```
HR:          read employee records, draft communications, schedule interviews
             BLOCKED: modify compensation, access payroll systems, delete records

Finance:     read financial reports, query analytics dashboards
             BLOCKED: initiate transfers, approve expenses > $5k, modify audit logs

Legal:       read contracts, draft NDAs, query case management
             BLOCKED: execute contracts, file externally, access sealed case files

Engineering: read/write code, run CI/CD pipelines, deploy to staging
             BLOCKED: deploy to production, access customer PII, modify access controls

Customer Support: read customer records, draft responses, escalate tickets
             BLOCKED: modify account data, issue refunds > $100, access payment details
```

### Acceptance Criteria
`propose_action()` returns only department-permitted actions from the authorized action set. Actions not in the department allowlist are never proposed. Audit log entry written for every interaction. Compliance rules evaluated on every data access.

> **Why action-filter for enterprise, not action-verifier?**
> Enterprise governance inverts the default assumption: instead of "allow everything that isn't forbidden," enterprise policy is "forbid everything that isn't explicitly allowed." Action-filter enumerates the legal action set and the LLM ranks within it — this is the correct model when the permitted action space is small and must be auditable. You can't audit "we blocked bad things"; you can audit "we only permitted these specific things."
>
> **Why factory scale?**
> The same governance framework applies to 5 departments but with different permission tables, compliance rules, and data classifications. Factory scale generates one harness per department from shared templates, keeping policy logic in one place while producing department-specific artifacts. This is the NemoClaw pattern: one policy engine, many deployment contexts.
>
> **How the audit trail works:**
> Every call to `propose_action()` or `validate_action()` writes an immutable record: timestamp, department, user_id, action_type, decision (allowed/denied), and the applicable policy rule that governed the decision. This is written BEFORE the action executes. The audit log is the compliance artifact — regulators can reconstruct every decision from it.

---

## PLAN

**Factory plan — STATE.yaml tracks generation progress across departments.**

### STATE.yaml schema

```yaml
factory:
  version: 0.1.0
  departments:
    - name: hr
      status: pending          # pending | generating | complete | failed
      harness_path: null
      last_run: null
    - name: finance
      status: pending
      harness_path: null
      last_run: null
    - name: legal
      status: pending
      harness_path: null
      last_run: null
    - name: engineering
      status: pending
      harness_path: null
      last_run: null
    - name: customer-support
      status: pending
      harness_path: null
      last_run: null

templates:
  behavior_yaml: templates/governance-behavior.yaml.j2
  constraints_py: templates/governance-constraints.py.j2
  policy_rules:   templates/policy-rules.yaml.j2
  permissions:    data/department-permissions.yaml
```

### Generation steps (per department, parallel: 3)

1. **Load permissions** — read department allowlist from `data/department-permissions.yaml`
2. **Render templates** — stamp `behavior.yaml`, `constraints.py`, `policy-rules.yaml` with department values
3. **Generate compliance module** — department-specific GDPR/SOX/HIPAA rules
4. **Assemble harness** — write to `.harness-machine/harnesses/<department>-governance/`
5. **Update STATE.yaml** — mark `status: complete`, record path

---

## ARTIFACT: All Three Constraint Layers

### `hr-governance-harness/behavior.yaml`

```yaml
bundle:
  name: hr-governance-harness
  version: 0.1.0
  description: Enterprise governance harness for HR department AI assistant.

hooks:
  # Layer 1: Input moderation — fires before the LLM sees the prompt
  - event: provider:request
    module: input-moderator
    source: ./constraints.py
    action: inject_context       # behavioral layer: inject policy context
    config:
      department: hr
      layer: input-moderation

  # Layer 2: Action authorization — fires before any tool call
  - event: tool:pre
    module: action-authorizer
    source: ./constraints.py
    action: deny                 # enforcement layer: hard deny
    config:
      department: hr
      layer: action-authorization

  # Layer 3: Output filtering — fires before response reaches user
  - event: provider:response
    module: output-filter
    source: ./constraints.py
    action: modify               # enforcement layer: redact then continue
    config:
      department: hr
      layer: output-filtering
```

> **Three hooks, three layers:** `provider:request` (behavioral), `tool:pre` (enforcement), `provider:response` (enforcement). This is the full constraint stack: shape what the LLM believes is appropriate, block what it tries to do, and sanitize what it returns. No single layer is sufficient alone.

### `hr-governance-harness/constraints.py`

```python
"""Enterprise governance harness — HR department."""
import json, re, time, os
from pathlib import Path

DEPARTMENT = "hr"
AUDIT_LOG  = Path(os.environ.get("AUDIT_LOG_PATH", "/var/log/ai-governance/hr-audit.jsonl"))

# Action-filter: the COMPLETE set of permitted actions for HR
PERMITTED_ACTIONS = {
    "read_employee_record", "draft_communication", "schedule_interview",
    "search_candidates", "generate_offer_letter", "query_org_chart",
}

BLOCKED_DATA_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",       # SSN
    r"\b[A-Z]{2}\d{6}\b",            # Passport
    r"salary:\s*\$[\d,]+",           # Compensation data
    r"api[_-]?key\s*[:=]\s*\S+",     # Credentials
]

COMPLIANCE_RULES = {
    "gdpr_erasure_check":    lambda action: "delete" not in action.get("type", "").lower(),
    "no_compensation_write": lambda action: action.get("type") != "modify_compensation",
    "no_payroll_access":     lambda action: "payroll" not in action.get("resource", "").lower(),
}


def propose_action(board: str) -> str:
    """Return permitted actions for the LLM to rank. Never returns blocked actions."""
    try:
        state = json.loads(board)
        context = state.get("context", {})
        # Filter permitted actions based on current context
        available = [a for a in PERMITTED_ACTIONS
                     if _action_valid_in_context(a, context)]
        _audit({"event": "propose_action", "available": available, "decision": "allow"})
        return json.dumps({"permitted_actions": available})
    except Exception:
        return json.dumps({"permitted_actions": []})


def validate_action(state: dict, action: dict) -> tuple[bool, str]:
    """Enforcement layer: deny any action outside the permitted set."""
    action_type = action.get("type", "")

    # Action authorization (enforcement)
    if action_type not in PERMITTED_ACTIONS:
        _audit({"event": "action_denied", "action": action_type, "rule": "not-in-allowlist"})
        return False, f"Action '{action_type}' not permitted for HR department."

    # Compliance rules (policy)
    for rule_name, rule_fn in COMPLIANCE_RULES.items():
        if not rule_fn(action):
            _audit({"event": "compliance_block", "action": action_type, "rule": rule_name})
            return False, f"Compliance rule violated: {rule_name}"

    _audit({"event": "action_allowed", "action": action_type})
    return True, ""


def filter_output(response: str) -> str:
    """Output filtering layer: redact sensitive patterns before response reaches user."""
    for pattern in BLOCKED_DATA_PATTERNS:
        response = re.sub(pattern, "[REDACTED]", response, flags=re.IGNORECASE)
    return response


def _action_valid_in_context(action_type: str, context: dict) -> bool:
    """Check if an action makes sense in the current conversational context."""
    return True  # Extended by department-specific logic in templates


def _audit(record: dict) -> None:
    """Append-only audit log entry. Written before action executes."""
    entry = {
        "timestamp":  time.time(),
        "department": DEPARTMENT,
        "user_id":    os.environ.get("AI_USER_ID", "unknown"),
        **record
    }
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # audit failure is logged elsewhere; never block on log write
```

### `hr-governance-harness/context.md` (behavioral layer)

```markdown
## HR Department AI Assistant — Governance Context

You are an AI assistant for the HR department. You operate within a strict
governance framework. This context describes the policy constraints you must
respect (behavioral layer — the enforcement layer is active independently).

### What you are authorized to do
- Read employee records (read-only)
- Draft communications (offers, rejections, schedules)
- Schedule and coordinate interviews
- Search and query candidate information
- Generate offer letters using approved templates
- Query the org chart

### What you must never do
- Access, suggest, or infer compensation data
- Modify any employee record
- Access payroll or benefits administration systems
- Delete any HR record (GDPR erasure requests go through legal review)
- Share individual employee data across requests

### Why this matters
Every action you take is logged for compliance. GDPR requires data minimization.
SOX requires HR action audit trails. When in doubt, do less and ask.
```

### `.harness-machine/STATE.yaml` (after factory run)

```yaml
factory:
  version: 0.1.0
  departments:
    - name: hr
      status: complete
      harness_path: .harness-machine/harnesses/hr-governance/
      last_run: "2026-03-13T14:22:00Z"
      legal_action_rate: 1.0
    - name: finance
      status: complete
      harness_path: .harness-machine/harnesses/finance-governance/
      last_run: "2026-03-13T14:25:00Z"
      legal_action_rate: 1.0
    - name: legal
      status: complete
      harness_path: .harness-machine/harnesses/legal-governance/
      last_run: "2026-03-13T14:28:00Z"
      legal_action_rate: 1.0
    - name: engineering
      status: complete
      harness_path: .harness-machine/harnesses/engineering-governance/
      last_run: "2026-03-13T14:31:00Z"
      legal_action_rate: 1.0
    - name: customer-support
      status: complete
      harness_path: .harness-machine/harnesses/customer-support-governance/
      last_run: "2026-03-13T14:34:00Z"
      legal_action_rate: 1.0
```
