# Example: Developer Tooling Harness
**Scale:** Medium (single) — Claude-Code-style tool permissions, command allowlists, filesystem boundaries.
**Walkthrough:** Spec → Plan → Artifact, annotated with WHY each decision was made.

---

## SPEC

```
harness_type:  action-verifier
harness_scale: single
target:        An AI coding agent with access to bash, read_file, write_file, edit_file tools.
               Operating on a single software project in /workspace/project/
```

### Constraints (9)

| # | Constraint | Rationale |
|---|-----------|-----------|
| 1 | **Tool allowlist** — only `bash`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` permitted | Any tool not explicitly allowed is denied. Unknown tools = unknown risk surface. |
| 2 | **Command blocklist** — reject `rm -rf`, `sudo`, `chmod 777`, `curl \| bash`, `eval` | These are the canonical "foot guns." A coding agent should never need them. |
| 3 | **No push to remote** — block `git push`, `git push --force`, `gh pr merge` | Prevents irreversible remote state changes without human review. |
| 4 | **No credential access** — block reads of `~/.ssh/`, `~/.aws/`, `.env` files outside project | Protects credentials the agent should never see. |
| 5 | **Filesystem boundary** — all file ops must resolve inside `/workspace/project/` | Same principle as nano-filesystem, applied to a coding agent. |
| 6 | **Env var protection** — block commands that export or print `AWS_`, `SECRET_`, `TOKEN_` variables | Prevents accidental exfiltration of secrets already in the shell environment. |
| 7 | **No background processes** — block `nohup`, `&` at end of command, `screen`, `tmux` | Background processes outlive the agent turn. Untracked processes are an audit gap. |
| 8 | **Max output size** — truncate bash stdout/stderr at 100 KB | Prevents context flooding from `cat large-file.log` or infinite loop output. |
| 9 | **No package manager installs** — block `pip install`, `npm install -g`, `brew install` outside dev-dependencies | Agents should not silently modify the system package state. |

### Legal Action Space
Any tool call that uses an allowed tool, executes an allowed command, stays inside the project directory, does not touch credentials, and does not spawn background processes.

### Acceptance Criteria
`validate_action()` returns `(False, reason)` for all blocklisted patterns. Returns `(True, "")` for normal coding operations: running tests, reading source files, editing code, running `git status` / `git diff` / `git add` / `git commit`.

> **Why enforcement layer (hook deny) not behavioral (context instructions)?**
> A `context.md` instruction saying "don't run rm -rf" is a suggestion. The agent can ignore it, forget it mid-conversation, or be prompted to override it. A `tool:pre deny` hook fires at the kernel level — the action is physically blocked regardless of what the agent intends. For security constraints, enforcement is not optional.
>
> **Why action-verifier not action-filter?**
> The set of legal bash commands is unbounded. Action-filter requires enumerating legal moves; you cannot list every valid `pytest` invocation, `grep` pattern, or `git` command. Action-verifier lets the agent propose freely and blocks the small set of dangerous patterns.

---

## PLAN

Three constraint functions, one per domain:

**`validate_tool(tool_name: str) -> tuple[bool, str]`**
- Check tool_name against `ALLOWED_TOOLS` set
- Return `(False, "Tool not permitted: {tool_name}")` if not in set

**`validate_command(command: str) -> tuple[bool, str]`**
- Check against `BLOCKED_PATTERNS` list of regex patterns
- Patterns cover: `rm -rf`, `sudo`, `git push`, credential paths, background ops, global installs
- Return first matching block reason, or `(True, "")` if none match

**`validate_path(path: str) -> tuple[bool, str]`**
- Resolve via `os.path.realpath()` (same as nano-filesystem, same symlink concern)
- Check resolved path starts with `/workspace/project/`
- Check not a credential path (`.ssh`, `.aws`, `.env`)

**`validate_action(state: dict, action: dict) -> tuple[bool, str]`** — Amplifier hook entry point
- Route to the appropriate sub-validator based on `action["tool_name"]`
- For `bash`: run `validate_command(action["tool_input"]["command"])`
- For file ops: run `validate_path(action["tool_input"]["path"])`
- For all: run `validate_tool(action["tool_name"])` first

---

## ARTIFACT

### `developer-tooling-harness/behavior.yaml`

```yaml
bundle:
  name: developer-tooling-harness
  version: 0.1.0
  description: >
    Constrains AI coding agent to safe tool usage: allowlisted tools,
    blocked dangerous commands, project filesystem boundary.

hooks:
  - event: tool:pre
    module: harness-constraints
    source: ./constraints.py
    action: deny           # hook returns deny to block the tool call
    config:
      harness_type: action-verifier
      strict: true
      project_root: /workspace/project
```

> **How `tool:pre` maps to Amplifier's hook system:**
> The `tool:pre` event fires before every tool call. The hook receives the tool name and tool input. Returning `deny` from `validate_action()` prevents the tool from executing and returns the rejection reason to the agent. The agent sees: "Tool call blocked: [reason]" and must propose a different action. This is rejection sampling at the tool layer.

### `developer-tooling-harness/constraints.py`

```python
"""Developer tooling harness: tool allowlist, command blocklist, path boundary."""
import json, os, re

PROJECT_ROOT = os.environ.get("HARNESS_PROJECT_ROOT", "/workspace/project")

ALLOWED_TOOLS = {"bash", "read_file", "write_file", "edit_file", "glob", "grep"}

BLOCKED_PATTERNS = [
    (r"rm\s+-rf",                    "Destructive delete (rm -rf) is blocked."),
    (r"\bsudo\b",                    "Privilege escalation (sudo) is blocked."),
    (r"chmod\s+777",                 "World-writable chmod is blocked."),
    (r"curl[^|]+\|\s*(bash|sh)",     "Pipe-to-shell execution is blocked."),
    (r"\beval\b",                    "eval is blocked."),
    (r"git\s+push",                  "Remote push is blocked — commit only."),
    (r"gh\s+pr\s+merge",             "PR merge from agent is blocked."),
    (r"(nohup|&\s*$|\bscreen\b|\btmux\b)", "Background processes are blocked."),
    (r"pip\s+install\s+(?!-r)",      "Global pip install is blocked (use requirements)."),
    (r"npm\s+install\s+-g",          "Global npm install is blocked."),
    (r"brew\s+install",              "Homebrew installs are blocked."),
    (r"(AWS_|SECRET_|TOKEN_)\w*",    "Credential variable access is blocked."),
]

CREDENTIAL_PATHS = (".ssh", ".aws", ".env", ".netrc", ".gnupg")


def validate_tool(tool_name: str) -> tuple[bool, str]:
    if tool_name not in ALLOWED_TOOLS:
        return False, f"Tool not in allowlist: {tool_name}"
    return True, ""


def validate_command(command: str) -> tuple[bool, str]:
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, reason
    return True, ""


def validate_path(path: str) -> tuple[bool, str]:
    try:
        resolved = os.path.realpath(path)
        root     = os.path.realpath(PROJECT_ROOT)
        if not (resolved.startswith(root + os.sep) or resolved == root):
            return False, f"Path outside project boundary: {path}"
        if any(cred in resolved for cred in CREDENTIAL_PATHS):
            return False, f"Credential path access blocked: {path}"
        return True, ""
    except Exception:
        return False, "Path validation error."


def validate_action(state: dict, action: dict) -> tuple[bool, str]:
    """Amplifier tool:pre hook entry point."""
    tool_name  = action.get("tool_name", "")
    tool_input = action.get("tool_input", {})

    ok, reason = validate_tool(tool_name)
    if not ok:
        return False, reason

    if tool_name == "bash":
        return validate_command(tool_input.get("command", ""))

    if tool_name in ("read_file", "write_file", "edit_file"):
        return validate_path(tool_input.get("path") or tool_input.get("file_path", ""))

    return True, ""  # glob/grep: no additional checks needed


def is_legal_action(board: str, action: str) -> bool:
    """AutoHarness paper-compatible wrapper."""
    try:
        return validate_action({}, json.loads(action))[0]
    except Exception:
        return False
```

### `developer-tooling-harness/context.md`

```markdown
## Developer Tooling Harness

**Environment:** AI coding agent (Claude-Code style) with bash and file tools.
**Project root:** Configured via `HARNESS_PROJECT_ROOT` (default: `/workspace/project`).

### What this harness allows
Normal coding work: reading source files, editing code, running tests (`pytest`, `jest`, `cargo test`),
using `git add`, `git commit`, `git diff`, `git status`, `git log`.

### What this harness blocks
Destructive commands, remote pushes, credential access, background processes, global package installs.

### Enforcement model
Tool calls are intercepted at `tool:pre`. The agent cannot bypass this by rephrasing —
the hook fires at the kernel level regardless of instruction content.
```
