"""Tests for the standalone runtime (runtime/runtime.py).

All LLM calls are mocked — these tests verify the constraint gate logic,
retry loop, and conversation management, not the LLM itself.
"""

import os
import sys

# Add runtime to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime"
    ),
)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


# ---------------------------------------------------------------------------
# Mock LLM response helpers
# ---------------------------------------------------------------------------


def make_tool_call_response(tool_name, parameters, call_id="call_001"):
    """Build a mock LLM response that proposes a tool call."""
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": parameters,
                },
            }
        ],
    }


def make_text_response(text):
    """Build a mock LLM response that is plain text (no tool call)."""
    return {
        "role": "assistant",
        "content": text,
        "tool_calls": None,
    }


# ---------------------------------------------------------------------------
# Tests: constraint gate
# ---------------------------------------------------------------------------


class TestConstraintGate:
    """Test the constraint gate that checks actions before dispatch."""

    def test_gate_blocks_illegal_action(self, tmp_path):
        from runtime import ConstraintGate

        gate = ConstraintGate(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py")
        )
        is_legal, reason = gate.check("bash", {"command": "rm -rf /"})
        assert is_legal is False
        assert "rm" in reason.lower()

    def test_gate_passes_legal_action(self, tmp_path):
        from runtime import ConstraintGate

        gate = ConstraintGate(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py")
        )
        is_legal, reason = gate.check("read_file", {"file_path": "src/main.py"})
        assert is_legal is True
        assert reason == ""

    def test_gate_exception_treated_as_deny(self):
        from runtime import ConstraintGate

        gate = ConstraintGate(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py")
        )
        # None tool_name will likely cause an exception in the constraint
        is_legal, reason = gate.check(None, None)
        assert is_legal is False


# ---------------------------------------------------------------------------
# Tests: agent loop
# ---------------------------------------------------------------------------


class TestAgentLoop:
    """Test the agent loop with mocked LLM."""

    def test_retry_on_illegal_action(self, tmp_path):
        """Agent retries when constraint gate blocks an action."""
        from runtime import AgentLoop

        # First call: LLM proposes illegal action
        # Second call: LLM proposes legal action (text response = done)
        call_count = 0
        illegal_response = make_tool_call_response("bash", {"command": "rm -rf /"})
        legal_response = make_text_response("I'll use a different approach.")

        def mock_llm(messages, tools=None, model=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return illegal_response
            return legal_response

        # Create a test file so ToolExecutor has a project
        (tmp_path / "file.txt").write_text("test")

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=3,
            llm_fn=mock_llm,
        )

        result = loop.process_turn("Do something dangerous")
        assert call_count == 2  # retried once
        assert "different approach" in result.lower()

    def test_max_retries_exhaustion(self, tmp_path):
        """Agent gives up after max_retries consecutive rejections."""
        from runtime import AgentLoop

        illegal_response = make_tool_call_response("bash", {"command": "rm -rf /"})

        def mock_llm(messages, tools=None, model=None):
            return illegal_response  # always proposes illegal action

        (tmp_path / "file.txt").write_text("test")

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=2,
            llm_fn=mock_llm,
        )

        result = loop.process_turn("Do something dangerous")
        assert "max retries" in result.lower() or "exhausted" in result.lower()

    def test_legal_tool_call_dispatches_and_returns(self, tmp_path):
        """Legal tool call is dispatched to executor and result returned to LLM."""
        from runtime import AgentLoop

        (tmp_path / "hello.txt").write_text("Hello from test!")

        call_count = 0
        tool_response = make_tool_call_response(
            "read_file",
            {"file_path": str(tmp_path / "hello.txt")},
        )
        final_response = make_text_response("The file says: Hello from test!")

        def mock_llm(messages, tools=None, model=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return tool_response
            return final_response

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=3,
            llm_fn=mock_llm,
        )

        result = loop.process_turn("Read hello.txt")
        assert "Hello from test" in result

    def test_conversation_history_accumulates(self, tmp_path):
        """Each turn adds to conversation history."""
        from runtime import AgentLoop

        (tmp_path / "f.txt").write_text("x")

        def mock_llm(messages, tools=None, model=None):
            return make_text_response(
                f"Response (history has {len(messages)} messages)"
            )

        loop = AgentLoop(
            constraints_path=os.path.join(FIXTURES_DIR, "constraints_simple.py"),
            project_root=str(tmp_path),
            system_prompt="You are a test agent.",
            model="mock",
            max_retries=3,
            llm_fn=mock_llm,
        )

        loop.process_turn("First message")
        loop.process_turn("Second message")
        # system + user1 + assistant1 + user2 + assistant2 = 5
        assert len(loop.messages) == 5
