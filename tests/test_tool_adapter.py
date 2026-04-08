"""Tests for Phase 3 Tool Adapter implementation (TAD-01 through TAD-05).

Verifies:
- TAD-01: tenacity in requirements.txt
- TAD-02: HarnessExecutor OOP structure with concrete subclasses
- TAD-02: call_harness() factory routes by harness key
- TAD-03: retry logic appends error context to task on failure
- TAD-04: sidecar context injection (_write_sidecar / _inject_context)
- TAD-05: All CLI keys (opencode, omx, claude, kiro, gemini, aider, + legacy aliases) are mapped
"""
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import tempfile
import os

PROJECT_ROOT = Path(__file__).parent.parent


# ── TAD-01: Dependency ────────────────────────────────────────────────────────

def test_tenacity_in_requirements():
    """requirements.txt must list tenacity (TAD-01 — retry library dependency)."""
    req_text = (PROJECT_ROOT / "requirements.txt").read_text()
    assert "tenacity" in req_text, "tenacity must be listed in requirements.txt"


# ── TAD-02: OOP Structure ─────────────────────────────────────────────────────

def test_harness_executor_base_class_exists():
    """HarnessExecutor base class must exist in app.tools.adapter (TAD-02)."""
    from app.tools.adapter import HarnessExecutor
    assert HarnessExecutor is not None


def test_four_concrete_harness_classes_exist():
    """All concrete harness classes must exist (TAD-02)."""
    from app.tools.adapter import (
        OpenCodeHarness, ClaudeCodeHarness, CodexHarness, KiroHarness,
        GeminiHarness, AiderHarness,
    )
    for cls in [OpenCodeHarness, ClaudeCodeHarness, CodexHarness, KiroHarness, GeminiHarness, AiderHarness]:
        assert issubclass(cls, __import__("app.tools.adapter", fromlist=["HarnessExecutor"]).HarnessExecutor), (
            f"{cls.__name__} must inherit from HarnessExecutor"
        )


def test_call_harness_factory_exists():
    """call_harness() must be importable as the top-level factory (TAD-02)."""
    from app.tools.adapter import call_harness
    assert callable(call_harness)


# ── TAD-05: CLI key routing ───────────────────────────────────────────────────

@pytest.mark.parametrize("harness_key,expected_bin", [
    # Canonical keys → correct binary as first argv element
    ("opencode", "opencode"),
    ("claude",   "claude"),
    ("omx",      "omx"),
    ("kiro",     "kiro-cli"),
    ("gemini",   "gemini"),
    ("aider",    "aider"),
    # Legacy aliases must still route
    ("omo",      "opencode"),   # omo → OpenCodeHarness → opencode binary
    ("omc",      "claude"),     # omc → ClaudeCodeHarness → claude binary
])
def test_call_harness_routes_by_key(harness_key, expected_bin):
    """call_harness() must route each harness key to its correct CLI binary (TAD-05)."""
    from app.tools.adapter import call_harness

    task_spec = {
        "harness": harness_key,
        "task": "do nothing",
        "worktree": "/tmp",
        "skills": [],
    }

    # Patch subprocess.run to capture the command without executing
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Also patch sidecar writes to avoid filesystem side-effects
        with patch.object(
            __import__("app.tools.adapter", fromlist=["HarnessExecutor"]).HarnessExecutor,
            "_write_sidecar"
        ):
            call_harness(task_spec)

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == expected_bin, (
            f"harness='{harness_key}' must route to binary '{expected_bin}', got '{call_args[0]}'"
        )


def test_call_harness_defaults_to_claude_on_unknown_key():
    """call_harness() with unknown harness key must fall back to claude (TAD-05)."""
    from app.tools.adapter import call_harness

    task_spec = {
        "harness": "unknown-harness",
        "task": "do nothing",
        "worktree": "/tmp",
        "skills": [],
    }

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        with patch.object(
            __import__("app.tools.adapter", fromlist=["HarnessExecutor"]).HarnessExecutor,
            "_write_sidecar"
        ):
            result = call_harness(task_spec)
        # Should succeed (claude fallback) rather than crashing
        assert result is not None
        # Verify it fell back to claude binary
        assert mock_run.call_args[0][0][0] == "claude"


# ── TAD-03: Retry with error context ─────────────────────────────────────────

def test_harness_retry_appends_error_to_task():
    """On subprocess failure, execute() must append the error to task_spec['task']
    before tenacity retries — giving the AI context on next attempt (TAD-03)."""
    from app.tools.adapter import OpenCodeHarness

    task_spec = {
        "harness": "opencode",
        "task": "migrate Foo.cs",
        "worktree": "/tmp",
        "skills": [],
    }

    call_count = {"n": 0}

    def mock_subprocess(*args, **kwargs):
        call_count["n"] += 1
        result = MagicMock()
        result.returncode = 1  # always fail
        result.stdout = ""
        result.stderr = "CS0246: Type not found"
        return result

    harness = OpenCodeHarness()

    with patch("subprocess.run", side_effect=mock_subprocess):
        with patch.object(harness, "_write_sidecar"):
            with pytest.raises(Exception):
                harness.execute(task_spec)

    # After first failure, error context must be appended to task
    assert "CS0246" in task_spec["task"] or "Previous attempt" in task_spec["task"], (
        "execute() must append error context to task_spec['task'] for retry"
    )
    # tenacity must have retried (3 attempts total)
    assert call_count["n"] >= 2, "tenacity must retry on subprocess failure"


# ── TAD-04: Sidecar context injection ────────────────────────────────────────

def test_write_sidecar_creates_file():
    """_write_sidecar() must create the specified file in the worktree (TAD-04)."""
    from app.tools.adapter import HarnessExecutor

    class ConcreteExecutor(HarnessExecutor):
        def _build_cmd(self, task_spec):
            return ["echo"]

    executor = ConcreteExecutor()

    with tempfile.TemporaryDirectory() as tmpdir:
        executor._write_sidecar(tmpdir, "CLAUDE.md", "# Context\nDO NOT invent namespaces.")
        sidecar_path = Path(tmpdir) / "CLAUDE.md"
        assert sidecar_path.exists(), "_write_sidecar must create the file"
        assert "DO NOT invent namespaces" in sidecar_path.read_text()


def test_inject_context_writes_skills_sidecar():
    """_inject_context() must write skill content to the sidecar file (TAD-04)."""
    from app.tools.adapter import OpenCodeHarness

    harness = OpenCodeHarness()

    with tempfile.TemporaryDirectory() as tmpdir:
        task_spec = {
            "worktree": tmpdir,
            "skills": ["dotnet-controller-migration"],
            "rules": "Follow the mapping table exactly.",
        }

        with patch.object(harness, "_write_sidecar") as mock_write:
            harness._inject_context(task_spec)
            # _write_sidecar must have been called at least once for skill/rules injection
            assert mock_write.called, "_inject_context must call _write_sidecar"
