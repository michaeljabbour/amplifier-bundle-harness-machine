"""Recipe runner for micro runtime.

Provides RecipeRunner that executes YAML-driven multi-step workflows:
  - Sequential step execution with state accumulation
  - while_condition loops with configurable iteration
  - Approval gates via _prompt_approval() y/n prompts
  - Context accumulation across steps
  - Template variable substitution in step parameters
  - Bash steps and agent steps

Recipe YAML format::

    name: My Workflow
    steps:
      - name: Read files
        type: agent
        prompt: "Read and summarize all Python files"

      - name: Iterate
        type: agent
        prompt: "Process item {{ item }}"
        while_condition: "more_items"

      - name: Deploy
        type: bash
        command: "echo done"
        approval: true
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Any

import importlib.util

_YAML_AVAILABLE = importlib.util.find_spec("yaml") is not None

try:
    from rich.console import Console

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False
    Console = None  # type: ignore[misc, assignment]

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# RecipeRunner
# ---------------------------------------------------------------------------


class RecipeRunner:
    """Executes YAML-driven multi-step agent workflows.

    Usage::

        runner = RecipeRunner(agent=my_agent)
        runner.execute("workflow.yaml")

    The runner accumulates context across steps so each step can reference
    results from previous steps via template variables.
    """

    def __init__(self, agent: Any = None) -> None:
        """Initialize RecipeRunner.

        Args:
            agent: Agent instance to use for agent-type steps. Can be None
                   for testing; agent steps will be skipped if no agent.
        """
        self.agent = agent
        self.accumulated_context: list[dict[str, Any]] = []

        if _RICH_AVAILABLE and Console is not None:
            self.console: Any = Console()
        else:
            self.console = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(self, recipe_path: str) -> list[dict[str, Any]]:
        """Load and execute a YAML recipe file.

        Args:
            recipe_path: Path to the YAML recipe file.

        Returns:
            List of step result dicts with name and output keys.

        Raises:
            FileNotFoundError: If recipe_path does not exist.
            ValueError: If YAML parsing fails or recipe is invalid.
        """
        recipe = self._load_recipe(recipe_path)
        results: list[dict[str, Any]] = []

        steps = recipe.get("steps", [])
        for step in steps:
            result = self._run_step(step)
            results.append(result)

        return results

    # ------------------------------------------------------------------
    # Recipe loading
    # ------------------------------------------------------------------

    def _load_recipe(self, recipe_path: str) -> dict[str, Any]:
        """Load and parse a YAML recipe file.

        Args:
            recipe_path: Path to the YAML recipe.

        Returns:
            Parsed recipe dict.
        """
        with open(recipe_path) as f:
            content = f.read()

        if not _YAML_AVAILABLE:
            raise ImportError(
                "pyyaml is required for recipe execution. pip install pyyaml"
            )
        import yaml as _yaml  # type: ignore[import-untyped]

        data = _yaml.safe_load(content)

        if not isinstance(data, dict):
            raise ValueError(f"Recipe must be a YAML dict, got {type(data).__name__}")

        return data

    # ------------------------------------------------------------------
    # Step dispatch
    # ------------------------------------------------------------------

    def _run_step(self, step: dict[str, Any]) -> dict[str, Any]:
        """Run a single step, handling while_condition loops.

        Args:
            step: Step definition dict.

        Returns:
            Step result dict.
        """
        while_condition = step.get("while_condition")

        if while_condition:
            return self._run_while_step(step, while_condition)

        return self._execute_step(step)

    def _run_while_step(
        self, step: dict[str, Any], while_condition: str
    ) -> dict[str, Any]:
        """Execute a step in a while_condition loop.

        Continues executing the step while _evaluate_condition() returns True.

        Args:
            step: Step definition dict.
            while_condition: Condition string to evaluate each iteration.

        Returns:
            Combined result dict from all iterations.
        """
        outputs: list[str] = []
        max_iterations = 10  # safety cap

        for _ in range(max_iterations):
            if not self._evaluate_condition(while_condition):
                break
            result = self._execute_step(step)
            outputs.append(result.get("output", ""))

        return {
            "name": step.get("name", "while_step"),
            "output": "\n".join(outputs),
            "iterations": len(outputs),
        }

    def _execute_step(self, step: dict[str, Any]) -> dict[str, Any]:
        """Execute a single step by dispatching to the appropriate handler.

        Supports:
          - type: agent  — runs prompt through the agent
          - type: bash   — executes a shell command

        Template variables in prompt/command are substituted from
        accumulated_context.

        Args:
            step: Step definition dict.

        Returns:
            Step result dict with name, type, and output keys.
        """
        step_name = step.get("name", "unnamed")
        step_type = step.get("type", "agent")
        needs_approval = step.get("approval", False)

        # Approval gate
        if needs_approval:
            approved = self._prompt_approval(step)
            if not approved:
                return {
                    "name": step_name,
                    "type": step_type,
                    "output": "SKIPPED (approval denied)",
                    "approved": False,
                }

        if step_type == "bash":
            output = self._execute_bash_step(step)
        else:
            output = self._execute_agent_step(step)

        result: dict[str, Any] = {
            "name": step_name,
            "type": step_type,
            "output": output,
        }

        # Accumulate context
        self.accumulated_context.append(result)
        return result

    def _execute_agent_step(self, step: dict[str, Any]) -> str:
        """Execute an agent step by running a prompt through the agent.

        Args:
            step: Step definition dict with 'prompt' key.

        Returns:
            Agent response string.
        """
        if self.agent is None:
            return "(no agent configured)"

        prompt = step.get("prompt", "")
        prompt = self._substitute_variables(prompt)

        try:
            import asyncio

            return asyncio.run(self.agent.process_turn(prompt))
        except Exception as exc:
            return f"Agent step error: {exc}"

    def _execute_bash_step(self, step: dict[str, Any]) -> str:
        """Execute a bash step.

        Args:
            step: Step definition dict with 'command' key.

        Returns:
            Command output string.
        """
        command = step.get("command", "")
        command = self._substitute_variables(command)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout
            if result.returncode != 0:
                output += f"\nExit code: {result.returncode}\n{result.stderr}"
            return output
        except subprocess.TimeoutExpired:
            return "TIMEOUT: command exceeded 30s"
        except Exception as exc:
            return f"Bash step error: {exc}"

    # ------------------------------------------------------------------
    # Approval gate
    # ------------------------------------------------------------------

    def _prompt_approval(self, step: dict[str, Any]) -> bool:
        """Prompt the user for step approval via y/n input.

        Args:
            step: Step definition dict (for display).

        Returns:
            True if approved, False if denied.
        """
        step_name = step.get("name", "unnamed")
        step_type = step.get("type", "agent")
        detail = step.get("prompt", step.get("command", ""))

        if self.console is not None:
            self.console.print(
                f"\n[bold yellow]⚠ Approval required:[/bold yellow] "
                f"[bold]{step_name}[/bold] ({step_type})"
            )
            if detail:
                self.console.print(f"  [dim]{detail[:120]}[/dim]")
            answer = input("Approve? [y/N] ").strip().lower()
        else:
            print(f"\nApproval required: {step_name} ({step_type})")
            if detail:
                print(f"  {detail[:120]}")
            answer = input("Approve? [y/N] ").strip().lower()

        return answer in ("y", "yes")

    # ------------------------------------------------------------------
    # Condition evaluation
    # ------------------------------------------------------------------

    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a while_condition string.

        Simple string matching against accumulated context.

        Args:
            condition: Condition string to evaluate.

        Returns:
            True if condition is met (context contains the condition string).
        """
        # Simple string matching: check if any context entry references the condition
        for entry in self.accumulated_context:
            output = entry.get("output", "")
            if condition.lower() in output.lower():
                return True
        return False

    # ------------------------------------------------------------------
    # Template variable substitution
    # ------------------------------------------------------------------

    def _substitute_variables(self, text: str) -> str:
        """Substitute template variables in text from accumulated context.

        Replaces {{ var_name }} patterns with values from accumulated_context.

        Args:
            text: Template string with {{ variable }} placeholders.

        Returns:
            String with variables substituted.
        """
        import re

        def replace_var(match: re.Match[str]) -> str:
            var_name = match.group(1).strip()
            # Look up in accumulated context
            for entry in reversed(self.accumulated_context):
                if var_name in entry:
                    return str(entry[var_name])
            return match.group(0)  # leave unresolved vars as-is

        return re.sub(r"\{\{\s*(\w+)\s*\}\}", replace_var, text)
