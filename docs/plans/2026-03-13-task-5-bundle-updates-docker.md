# Bundle Updates + Docker Templates + Structural Tests — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Update existing bundle files to reflect the three-stud nano-amplifier architecture, add Docker templates for standalone deployment, and extend the structural test suite to cover `modules/` and `runtime/` directories.

**Architecture:** This task modifies three existing documentation/mode files (`harness-finish.md`, `harness-generator.md`, `harness-format.md`) to describe the new 3-stud packaging model, creates two new Docker template files in `runtime/`, and appends two new test classes to `tests/test_scaffold.py`. All changes are text-level — no Python logic is being added to production code.

**Tech Stack:** Markdown, YAML, Dockerfile, pytest, Python `os.path` for structural assertions

**Design doc:** `docs/plans/2026-03-13-harness-runtime-design.md`
**Parent plan:** `docs/plans/2026-03-13-harness-runtime-implementation.md` (Task 5 of 5)

**Dependencies:** Tasks 1–4 must be complete before this task. Those tasks created:
- `modules/hooks-harness/` — the Amplifier hook module (Task 1)
- `runtime/tools.py` — the tool executor (Task 2)
- `runtime/runtime.py` — the constraint gate + agent loop (Task 3)
- `runtime/cli.py` + `runtime/pyproject.toml.template` — CLI packaging (Task 4)

**Quality note:** The Dockerfile.template runs as root. This is acceptable for a local development/agent tool. If the harness is ever deployed in shared environments, add `RUN useradd -m agent && USER agent` before `ENTRYPOINT`.

---

## Orientation: What You're Working With

You are modifying an existing Amplifier bundle at the repo root. The repo has:

```
amplifier-bundle-autoharness/
├── bundle.md                              # Bundle manifest (DO NOT MODIFY)
├── behaviors/harness-machine.yaml         # Behavior config
├── agents/                                # 7 agent files (*.md)
│   └── harness-generator.md               # ← MODIFY (Task 2)
├── modes/                                 # 7 mode files (*.md)
│   └── harness-finish.md                  # ← MODIFY (Task 1)
├── context/                               # Instructions, philosophy, pattern, etc.
│   └── harness-format.md                  # ← MODIFY (Task 3)
├── modules/hooks-harness/                 # Created by Task 1 (already exists)
├── runtime/                               # Created by Tasks 2-4 (already exists)
│   ├── __init__.py
│   ├── cli.py
│   ├── runtime.py
│   ├── tools.py
│   └── pyproject.toml.template
├── tests/
│   ├── test_scaffold.py                   # ← MODIFY (Task 5)
│   ├── test_hooks_harness.py              # Created by Task 1
│   ├── test_tools.py                      # Created by Task 2
│   ├── test_runtime.py                    # Created by Task 3
│   └── test_cli.py                        # Created by Task 4
└── docs/plans/                            # Design docs
```

**Current test count:** ~186 passing tests across 5 test files.

**Test conventions:**
- Framework: pytest (no conftest.py, no pyproject.toml at repo root)
- Run command: `python -m pytest tests/ -v`
- `test_scaffold.py` uses a module-level `BUNDLE_ROOT` constant and `_read_file()` helper
- Test classes are grouped by structural concern (e.g., `TestModes`, `TestAgents`, `TestDirectories`)
- Each test has a single assertion with a descriptive failure message

---

### Task 1: Update harness-finish.md with 3-stud packaging

**Files:**
- Modify: `modes/harness-finish.md` (lines 36–75, the Step 2 section)

**Step 1: Read the current file**

Read `modes/harness-finish.md` to confirm the current content. Find the `### Step 2: Package the Artifact` section. It currently contains a simple Tier 1 block that says "Nano-amplifier" with just 3-file verification.

**Step 2: Replace Step 2 content**

Find the entire Step 2 section from `### Step 2: Package the Artifact` through the end of Tier 3, and replace it with the 3-stud version. The replacement starts at `### Step 2: Package the Artifact` and ends just before `### Step 3: Summarize the Work`.

Replace the old Step 2 with this exact content:

```markdown
### Step 2: Package the Artifact

Package based on artifact tier:

**Tier 1 — Nano-amplifier (3 studs):**

**Stud 1: Amplifier hook**

Generate `behavior.yaml` that wires the harness into Amplifier:

```yaml
bundle:
  name: <harness_name>
  version: 0.1.0
  description: Constraint harness for <environment>

hooks:
  - module: hooks-harness
    source: git+https://github.com/<org>/<harness_name>@main
    config:
      constraints_path: ./constraints.py
      harness_type: <action-filter|action-verifier|code-as-policy>
      strict: true
```

**Stud 2: Standalone CLI**

Copy the runtime/ scaffold into `standalone/<package_name>/`:
- Copy `runtime/runtime.py`, `runtime/tools.py`, `runtime/cli.py` into the package directory
- Copy `constraints.py`, `config.yaml`, `system-prompt.md` into the package directory
- Stamp `pyproject.toml` from `runtime/pyproject.toml.template` (substitute `{{harness_name}}` and `{{package_name}}`)

```
standalone/
  <package_name>/
    cli.py
    runtime.py
    tools.py
    constraints.py
    config.yaml
    system-prompt.md
  pyproject.toml
```

**Stud 3: Docker (optional)**

Ask user: "Would you like a Docker deployment? (yes/no)"

If yes, create `docker/` directory and stamp templates:
- Copy `runtime/Dockerfile.template` → `docker/Dockerfile` (substitute `{{harness_name}}`)
- Copy `runtime/docker-compose.template.yaml` → `docker/docker-compose.yaml` (substitute `{{harness_name}}` and `{{project_root}}`)

**Verification for all studs**

- Validate `behavior.yaml` parses as YAML
- Run `python_check` on `constraints.py`
- Ensure `config.yaml` has required keys: `project_root`, `model`, `harness_type`, `max_retries`
- Ensure `system-prompt.md` contains agent instructions

**Tier 2 — Harness bundle:**
- Verify bundle structure (bundle.md, behaviors/, modules/)
- Validate all YAML files parse
- Run python_check on all Python files

**Tier 3 — Harness machine (.harness-machine/):**
- Verify directory structure
- Validate STATE.yaml, all recipe YAML files
- Check no unsubstituted template variables remain
- Present Docker/cron startup instructions
```

**Step 3: Verify the edit**

Read `modes/harness-finish.md` again. Confirm:
- "3 studs" appears in the Tier 1 heading
- Stud 1, Stud 2, Stud 3 are all present
- Tier 2 and Tier 3 sections remain unchanged
- Step 3 ("Summarize the Work") still follows immediately after

---

### Task 2: Update harness-generator.md output contract

**Files:**
- Modify: `agents/harness-generator.md` (the `## Final Response Contract` section near end of file)

**Step 1: Read the current file**

Read `agents/harness-generator.md`. Find the `## Final Response Contract` section. It currently has a simple 4-item list ending with "Any concerns or limitations noted".

**Step 2: Replace the Final Response Contract**

Find the section starting with `## Final Response Contract` and everything after it up to (but NOT including) `## Red Flags`. Replace it with this expanded version:

```markdown
## Final Response Contract

Your response must include:
1. List of files generated with full paths
2. Self-review checklist (all items checked)
3. Summary of constraint functions implemented
4. Any concerns or limitations noted

### Required Output Files

| File | Purpose |
|------|---------|
| `constraints.py` | The constraint logic — `is_legal_action()`, `validate_action()`, or `propose_action()` |
| `test_constraints.py` | Unit tests verifying each constraint function |
| `behavior.yaml` | Amplifier hook wiring — references hooks-harness module with git source URL |
| `context.md` | Environment description, constraint rationale, known limitations |
| `config.yaml` | Runtime configuration for the standalone CLI |
| `system-prompt.md` | Agent mission statement and scope rules for the standalone agent |

### config.yaml Format

```yaml
project_root: /path/to/project
model: anthropic/claude-sonnet-4-20250514
harness_type: action-verifier  # action-filter | action-verifier | code-as-policy
max_retries: 3
covered_tools:
  - bash
  - write_file
  - edit_file
allowed_env_vars:
  - HOME
  - PATH
```

### system-prompt.md Format

```markdown
You are a constrained agent for <environment>.

## Mission
<Agent mission — what task the agent is trying to accomplish>

## Scope Rules
- Only use tools listed in covered_tools
- <environment-specific scope rules>

## Retry Instructions
When a tool call is rejected by the constraint gate:
1. Read the rejection reason carefully
2. Do NOT repeat the rejected action
3. Try a different approach that satisfies the constraint

## Environment Context
<Environment-specific guidance, known limitations, useful patterns>
```
```

**Step 3: Verify the edit**

Read `agents/harness-generator.md` again. Confirm:
- The "Required Output Files" table has 6 rows (constraints.py, test_constraints.py, behavior.yaml, context.md, config.yaml, system-prompt.md)
- The "config.yaml Format" subsection shows YAML with `project_root`, `model`, `harness_type`, `max_retries`, `covered_tools`, `allowed_env_vars`
- The "system-prompt.md Format" subsection shows markdown with Mission, Scope Rules, Retry Instructions, Environment Context
- The `## Red Flags` section still exists after the contract

---

### Task 3: Update harness-format.md with complete nano-amplifier spec

**Files:**
- Modify: `context/harness-format.md` (the `### Tier 1` section)

**Step 1: Read the current file**

Read `context/harness-format.md`. Find the `### Tier 1: Nano-Amplifier (3 files)` section. It currently shows just 3 files (behavior.yaml, constraints.py, context.md).

**Step 2: Replace the Tier 1 section**

Find the section starting with `### Tier 1: Nano-Amplifier (3 files)` through the line `Any Amplifier bundle can compose a nano-amplifier via includes: in its bundle.md.` and replace with the expanded 3-stud version:

```markdown
### Tier 1: Nano-Amplifier (3 studs)

The atomic unit of harness output. Every harness generation produces at minimum a nano-amplifier built from one brick and three studs:

**The Brick** (generated, unique per harness):
```
my-harness/
  constraints.py       # The constraint logic — is_legal_action(), validate_action(), propose_action()
```

**Generated Files** (supporting artifacts):
```
my-harness/
  config.yaml          # Runtime configuration for standalone CLI
  context.md           # Environment description, constraint rationale
  system-prompt.md     # Agent mission and scope rules
  test_constraints.py  # Unit tests verifying each constraint function
```

**Stud 1: Amplifier Hook** — plug into any Amplifier session:
```
my-harness/
  behavior.yaml        # Wires hooks-harness module with git source URL, constraints_path, harness_type, strict config
```

**Stud 2: Standalone CLI** — run without Amplifier:
```
my-harness/
  standalone/
    pyproject.toml                 # Stamped from runtime/pyproject.toml.template
    <package_name>/
      cli.py                       # Entry point: chat, check, audit subcommands
      runtime.py                   # ConstraintGate + AgentLoop
      tools.py                     # ToolExecutor (read_file, write_file, bash, grep, glob)
      constraints.py               # Copy of the brick
      config.yaml                  # Copy of runtime config
      system-prompt.md             # Copy of system prompt
```

**Stud 3: Docker Container** (optional) — containerized deployment:
```
my-harness/
  docker/
    Dockerfile                     # Stamped from runtime/Dockerfile.template
    docker-compose.yaml            # Stamped from runtime/docker-compose.template.yaml
```

**Three usage modes:**
1. **Amplifier hook** — compose `behavior.yaml` via `includes:` in any bundle.md
2. **Standalone CLI** — `pip install -e standalone/` then `<harness_name> chat`
3. **Docker container** — `docker compose -f docker/docker-compose.yaml up`

Any Amplifier bundle can compose a nano-amplifier via `includes:` in its bundle.md.
```

**Step 3: Verify the edit**

Read `context/harness-format.md` again. Confirm:
- Heading says "3 studs" not "3 files"
- "The Brick" section shows `constraints.py`
- "Generated Files" section shows `config.yaml`, `context.md`, `system-prompt.md`, `test_constraints.py`
- Stud 1 shows `behavior.yaml`
- Stud 2 shows `standalone/` directory tree with 6 files inside `<package_name>/`
- Stud 3 shows `docker/` directory with `Dockerfile` and `docker-compose.yaml`
- Three usage modes are listed

---

### Task 4: Create Docker templates

**Files:**
- Create: `runtime/Dockerfile.template`
- Create: `runtime/docker-compose.template.yaml`

**Step 1: Write the failing tests first**

Before creating the templates, note that the structural tests in Task 5 will verify these files exist and contain the right template variables. We create the files first since they are simple templates with no test-code-test cycle needed.

**Step 2: Create `runtime/Dockerfile.template`**

Create the file with this exact content:

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY standalone/ ./
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["{{harness_name}}"]
CMD ["chat"]
```

Key details:
- `python:3.12-slim` base image (matches the project's Python 3.11+ requirement, slim for size)
- Installs `git` (for pip git dependencies) and `ripgrep` (for grep tool)
- `--no-install-recommends` and `rm -rf /var/lib/apt/lists/*` for Docker hygiene
- `--no-cache-dir` on pip to keep image small
- `{{harness_name}}` is the template variable stamped at packaging time
- `ENTRYPOINT` + `CMD` pattern allows `docker run <image> check` to override subcommand

**Step 3: Create `runtime/docker-compose.template.yaml`**

Create the file with this exact content:

```yaml
services:
  agent:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: {{harness_name}}-agent
    network_mode: host
    stdin_open: true
    tty: true
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - {{project_root}}:{{project_root}}
```

Key details:
- Single `agent` service — one container per harness
- `context: .` builds from parent directory (where `standalone/` lives)
- `dockerfile: docker/Dockerfile` points to the Dockerfile in the docker/ subdirectory
- `{{harness_name}}` and `{{project_root}}` are template variables stamped at packaging time
- `network_mode: host` gives the agent access to localhost services
- `stdin_open: true` + `tty: true` enable interactive `chat` mode
- API keys passed via environment variables (user sets them in their shell)
- Volume mount gives the agent read/write access to the project directory

**Step 4: Verify both files exist**

Run:
```bash
ls -la runtime/Dockerfile.template runtime/docker-compose.template.yaml
```
Expected: Both files exist with non-zero sizes.

Run:
```bash
grep '{{harness_name}}' runtime/Dockerfile.template
grep '{{harness_name}}' runtime/docker-compose.template.yaml
grep '{{project_root}}' runtime/docker-compose.template.yaml
```
Expected: All three greps produce matches.

---

### Task 5: Write structural tests

**Files:**
- Modify: `tests/test_scaffold.py` (append after existing `TestYamlValidity` class)

**Step 1: Read the current test file**

Read `tests/test_scaffold.py`. Confirm:
- `BUNDLE_ROOT` is defined at module level as `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`
- `_read_file(rel_path)` helper reads files relative to BUNDLE_ROOT
- The last class is `TestYamlValidity` (ends around line 465)
- There is NO existing `TestHookModule` or `TestRuntime` class

**Step 2: Append TestHookModule class**

Append the following after the `TestYamlValidity` class at the end of the file:

```python


# ---------------------------------------------------------------------------
# Hook module structural tests
# ---------------------------------------------------------------------------


class TestHookModule:
    def test_modules_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "modules"))

    def test_hooks_harness_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "modules", "hooks-harness"))

    def test_hooks_harness_pyproject_exists(self):
        path = os.path.join(BUNDLE_ROOT, "modules", "hooks-harness", "pyproject.toml")
        assert os.path.isfile(path)

    def test_hooks_harness_package_dir_exists(self):
        path = os.path.join(
            BUNDLE_ROOT, "modules", "hooks-harness", "amplifier_module_hooks_harness"
        )
        assert os.path.isdir(path)

    def test_hooks_harness_init_exists(self):
        path = os.path.join(
            BUNDLE_ROOT,
            "modules",
            "hooks-harness",
            "amplifier_module_hooks_harness",
            "__init__.py",
        )
        assert os.path.isfile(path)

    def test_hooks_harness_init_exports_mount(self):
        content = _read_file(
            "modules/hooks-harness/amplifier_module_hooks_harness/__init__.py"
        )
        assert "def mount(" in content

    def test_hooks_harness_pyproject_has_entry_point(self):
        content = _read_file("modules/hooks-harness/pyproject.toml")
        assert "amplifier.modules" in content
```

This class has **7 tests** verifying:
1. `modules/` directory exists
2. `modules/hooks-harness/` directory exists
3. `modules/hooks-harness/pyproject.toml` file exists
4. `modules/hooks-harness/amplifier_module_hooks_harness/` package directory exists
5. `modules/hooks-harness/amplifier_module_hooks_harness/__init__.py` exists
6. `__init__.py` exports a `def mount(` function
7. `pyproject.toml` has `amplifier.modules` entry point

**Step 3: Append TestRuntime class**

Append immediately after TestHookModule:

```python


# ---------------------------------------------------------------------------
# Runtime structural tests
# ---------------------------------------------------------------------------


class TestRuntime:
    def test_runtime_dir_exists(self):
        assert os.path.isdir(os.path.join(BUNDLE_ROOT, "runtime"))

    def test_runtime_init_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "__init__.py")
        assert os.path.isfile(path)

    def test_runtime_py_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "runtime.py")
        assert os.path.isfile(path)

    def test_tools_py_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "tools.py")
        assert os.path.isfile(path)

    def test_cli_py_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "cli.py")
        assert os.path.isfile(path)

    def test_pyproject_template_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "pyproject.toml.template")
        assert os.path.isfile(path)

    def test_dockerfile_template_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "Dockerfile.template")
        assert os.path.isfile(path)

    def test_docker_compose_template_exists(self):
        path = os.path.join(BUNDLE_ROOT, "runtime", "docker-compose.template.yaml")
        assert os.path.isfile(path)

    def test_docker_compose_template_has_project_root(self):
        content = _read_file("runtime/docker-compose.template.yaml")
        assert "{{project_root}}" in content

    def test_runtime_py_has_constraint_gate(self):
        content = _read_file("runtime/runtime.py")
        assert "ConstraintGate" in content

    def test_runtime_py_has_agent_loop(self):
        content = _read_file("runtime/runtime.py")
        assert "AgentLoop" in content

    def test_tools_py_has_tool_executor(self):
        content = _read_file("runtime/tools.py")
        assert "ToolExecutor" in content

    def test_cli_py_has_main(self):
        content = _read_file("runtime/cli.py")
        assert "def main(" in content

    def test_pyproject_template_has_harness_name(self):
        content = _read_file("runtime/pyproject.toml.template")
        assert "{{harness_name}}" in content

    def test_dockerfile_template_has_harness_name(self):
        content = _read_file("runtime/Dockerfile.template")
        assert "{{harness_name}}" in content
```

This class has **15 tests** verifying:
1. `runtime/` directory exists
2. `runtime/__init__.py` exists
3. `runtime/runtime.py` exists
4. `runtime/tools.py` exists
5. `runtime/cli.py` exists
6. `runtime/pyproject.toml.template` exists
7. `runtime/Dockerfile.template` exists
8. `runtime/docker-compose.template.yaml` exists
9. `docker-compose.template.yaml` contains `{{project_root}}` variable
10. `runtime.py` contains `ConstraintGate` class
11. `runtime.py` contains `AgentLoop` class
12. `tools.py` contains `ToolExecutor` class
13. `cli.py` contains `def main(` function
14. `pyproject.toml.template` contains `{{harness_name}}` variable
15. `Dockerfile.template` contains `{{harness_name}}` variable

**Important assertion patterns:**
- Use `"def mount("` with the opening paren — matches the pattern used in `test_hooks_harness_init_exports_mount`. This is more precise than `"def mount"` which could match `def mount_something`.
- Use `"def main("` with the opening paren — same reasoning.
- Use `"ConstraintGate"` without `class` prefix — matches both `class ConstraintGate` and any reference to it.

**Step 4: Run only the structural tests to verify**

Run:
```bash
python -m pytest tests/test_scaffold.py -v
```
Expected: All tests PASS. The original ~139 structural tests plus 7 (TestHookModule) + 15 (TestRuntime) = ~161 total in this file.

---

### Task 6: Run full test suite

**Files:** None (verification only)

**Step 1: Run all tests**

Run:
```bash
python -m pytest tests/ -v
```
Expected: All ~218 tests PASS across all test files:
- `test_scaffold.py`: ~161 (139 original + 7 hook + 15 runtime)
- `test_hooks_harness.py`: ~14 (from Task 1)
- `test_tools.py`: ~18 (from Task 2)
- `test_runtime.py`: ~7 (from Task 3)
- `test_cli.py`: ~8 (from Task 4)

**Step 2: Verify no existing tests broken**

Check that no pre-existing test classes report failures. All original `TestBundleMd`, `TestBehaviorYaml`, `TestModes`, `TestAgents`, `TestRecipes`, `TestSkills`, `TestContextFiles`, `TestTemplates`, `TestDirectories`, `TestYamlValidity` tests must still pass.

**Step 3: Verify final directory structure**

Run:
```bash
find modules runtime -type f | sort
```

Expected output:
```
modules/hooks-harness/amplifier_module_hooks_harness/__init__.py
modules/hooks-harness/pyproject.toml
runtime/__init__.py
runtime/Dockerfile.template
runtime/cli.py
runtime/docker-compose.template.yaml
runtime/pyproject.toml.template
runtime/runtime.py
runtime/tools.py
```

---

### Task 7: Commit

**Files:** None (git operation only)

**Step 1: Stage all changed files**

```bash
git add modes/harness-finish.md agents/harness-generator.md context/harness-format.md \
       runtime/Dockerfile.template runtime/docker-compose.template.yaml \
       tests/test_scaffold.py
```

**Step 2: Commit with descriptive message**

```bash
git commit -m "feat: update bundle for 3-stud architecture + Docker templates

- harness-finish.md: 3-stud packaging (amplifier hook, standalone, docker)
- harness-generator.md: config.yaml + system-prompt.md in output contract
- harness-format.md: complete nano-amplifier spec with standalone/ and docker/
- Dockerfile.template + docker-compose.template.yaml for standalone deployment
- 22 new structural tests for modules/ and runtime/ directories"
```

**Step 3: Verify the commit**

Run:
```bash
git log --oneline -1
```
Expected: Shows the commit with message starting "feat: update bundle for 3-stud architecture"

---

## Acceptance Criteria Checklist

| # | Criterion | Verified By |
|---|-----------|-------------|
| 1 | All ~218 tests pass | Task 6 Step 1 |
| 2 | `modes/harness-finish.md` contains 3-stud packaging | Task 1 Step 3 |
| 3 | `agents/harness-generator.md` has expanded contract | Task 2 Step 3 |
| 4 | `context/harness-format.md` shows "3 studs" | Task 3 Step 3 |
| 5 | `runtime/Dockerfile.template` exists with `{{harness_name}}` | Task 4 Step 4 |
| 6 | `runtime/docker-compose.template.yaml` exists with variables | Task 4 Step 4 |
| 7 | `tests/test_scaffold.py` has TestHookModule (7) + TestRuntime (15) | Task 5 Step 4 |
| 8 | No existing structural tests broken | Task 6 Step 2 |
| 9 | Directory structure matches expected | Task 6 Step 3 |
| 10 | Clean commit | Task 7 Step 3 |