# Example: Nano Filesystem Harness
**Scale:** Trivial (nano) — Constrain an agent to read/write within a single directory.
**Walkthrough:** Spec → Plan → Artifact, annotated with WHY each decision was made.

---

## SPEC

```
harness_type:  action-verifier
harness_scale: nano
target:        Any file-reading/writing agent operating on /workspace/data/
```

### Constraints (5)

| # | Constraint | Rationale |
|---|-----------|-----------|
| 1 | **Path boundary** — all operations must stay inside `BASE_DIR` | The core safety guarantee. Everything else is secondary. |
| 2 | **No parent traversal** — reject any path containing `..` | `../../../etc/passwd` defeats a resolved-path check on some platforms. Defense in depth. |
| 3 | **No symlink escape** — resolve symlinks before checking boundary | A symlink inside `BASE_DIR` can point outside it. `os.path.realpath()` must be used, not `abspath()`. |
| 4 | **Allowed extensions** — only `.txt`, `.csv`, `.json`, `.md` | Limits blast radius. An agent that can write `.sh` or `.py` files can execute code. |
| 5 | **Max file size** — reject reads/writes > 10 MB | Prevents accidental memory exhaustion from large binary files and limits exfiltration payload size. |

### Legal Action Space
Read or write any file whose resolved path is inside `BASE_DIR`, has an allowed extension, and is under 10 MB.

### Acceptance Criteria
`is_legal_action()` returns `True` for all legal paths. Returns `False` (never raises) for any illegal path, including adversarial inputs.

> **Why action-verifier, not action-filter?**
> Action-filter requires enumerating legal moves upfront. File paths are infinite — you cannot list all valid paths before the agent acts. Action-verifier lets the agent propose freely, then validates the proposal. This is the correct type whenever the legal action space is too large to enumerate.
>
> **Why 5 constraints, not 3 or 10?**
> 3 would omit symlink escape (a real attack vector) or size limits (a real operational risk). 10 would add constraints like "no hidden files" or "no filenames with spaces" that are preferences, not safety rules. 5 is the set where every rule prevents a distinct class of harm.

---

## PLAN

Two constraint functions to write:

**`is_legal_action(board: str, action: str) -> bool`**
- Parse `action` as JSON: `{"op": "read"|"write", "path": "..."}`
- Check: no `..` in raw path
- Resolve: `os.path.realpath(path)` to expand symlinks
- Check: resolved path starts with `BASE_DIR`
- Check: extension in `ALLOWED_EXTENSIONS`
- Check: file size ≤ `MAX_FILE_BYTES` (for writes: check proposed content length; for reads: check existing file size)
- Return `False` on any parse error or failed check — never raise

**`propose_action(board: str) -> str`**
- Parse `board` for task description
- List files in `BASE_DIR` matching allowed extensions
- Return a JSON action pointing to the first matching file
- Fallback: return action pointing to `BASE_DIR/output.txt`

---

## ARTIFACT

### `filesystem-harness/behavior.yaml`

```yaml
bundle:
  name: filesystem-harness
  version: 0.1.0
  description: Constrains agent file operations to a single directory with extension and size limits.

hooks:
  - module: harness-constraints
    source: ./constraints.py
    config:
      harness_type: action-verifier
      strict: true
```

### `filesystem-harness/constraints.py`

```python
"""Filesystem harness: constrains file ops to BASE_DIR."""
import json
import os

BASE_DIR   = os.environ.get("HARNESS_BASE_DIR", "/workspace/data")
ALLOWED_EXT = {".txt", ".csv", ".json", ".md"}
MAX_BYTES   = 10 * 1024 * 1024  # 10 MB


def is_legal_action(board: str, action: str) -> bool:
    """Return True iff the file action is safe to execute."""
    try:
        act  = json.loads(action)
        path = act.get("path", "")
        # Rule 2: block raw traversal before resolution
        if ".." in path:
            return False
        resolved = os.path.realpath(path)          # Rule 3: expand symlinks
        base     = os.path.realpath(BASE_DIR)
        # Rule 1: path must be inside BASE_DIR
        if not resolved.startswith(base + os.sep) and resolved != base:
            return False
        # Rule 4: extension must be allowed
        if os.path.splitext(resolved)[1].lower() not in ALLOWED_EXT:
            return False
        # Rule 5: size check
        content = act.get("content", "")
        if content and len(content.encode()) > MAX_BYTES:
            return False
        if act.get("op") == "read" and os.path.isfile(resolved):
            if os.path.getsize(resolved) > MAX_BYTES:
                return False
        return True
    except Exception:
        return False  # never raise — malformed input is illegal


def propose_action(board: str) -> str:
    """Propose a safe file action given the current task description."""
    base = os.path.realpath(BASE_DIR)
    try:
        for fname in os.listdir(base):
            if os.path.splitext(fname)[1].lower() in ALLOWED_EXT:
                return json.dumps({"op": "read", "path": os.path.join(base, fname)})
    except OSError:
        pass
    return json.dumps({"op": "write", "path": os.path.join(base, "output.txt"), "content": ""})


def validate_action(state: dict, action: dict) -> tuple[bool, str]:
    """Amplifier hook entry point (tool:pre)."""
    ok = is_legal_action(str(state), json.dumps(action))
    return (ok, "") if ok else (False, "Action violates filesystem boundary constraints.")
```

### `filesystem-harness/context.md`

```markdown
## Filesystem Harness

**Environment:** Any agent operating on files in a designated workspace directory.
**Action space:** read/write operations expressed as JSON `{"op": ..., "path": ..., "content": ...}`.

### Constraints
1. Path boundary: operations must resolve inside `HARNESS_BASE_DIR`.
2. No parent traversal: `..` in path strings is rejected before resolution.
3. No symlink escape: `realpath()` is used, not `abspath()`.
4. Allowed extensions: `.txt .csv .json .md` only.
5. Max file size: 10 MB per read or write.

### Known Limitations
- Does not check file permissions beyond path boundary.
- `BASE_DIR` must be set via environment variable `HARNESS_BASE_DIR` before use.
```
