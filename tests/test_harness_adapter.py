"""Tests for HarnessAdapter (SFE-03)."""
import pytest
from unittest.mock import patch, MagicMock
from app.core.harness_adapter import HarnessAdapter
from app.core.safety import SafetyRules, SafetyResult
from app.core.state import MigrationState

@pytest.fixture
def safety_mock():
    mock = MagicMock(spec=SafetyRules)
    # Default to safe
    mock.check_file_path.return_value = SafetyResult(safe=True, rule_id=None, severity="info", message="ok", file_path=None)
    mock.scan_worktree.return_value = []
    # No-op hook
    mock.install_hook.return_value = None
    return mock

@pytest.fixture
def state():
    return MigrationState(migration_id="test", solution_path="/tmp")

def test_harness_adapter_preflight_blocked(safety_mock, state):
    """Test that pre-flight safety violations block the harness call."""
    adapter = HarnessAdapter(safety=safety_mock)
    
    # Mock preflight violation
    safety_mock.check_file_path.return_value = SafetyResult(safe=False, rule_id="P-1", severity="critical", message="blocked path", file_path="key.pem")
    
    task_spec = {"source_files": ["key.pem"], "worktree": "/tmp"}
    
    with patch("app.core.harness_adapter.call_harness") as mock_call:
        result = adapter.execute(task_spec, state)
        
        assert result["returncode"] == -1
        assert "Safety violation" in result["stderr"]
        mock_call.assert_not_called()
        assert len(state.safety_violations) == 1
        assert state.safety_violations[0]["rule_id"] == "P-1"

def test_harness_adapter_clean_execution(safety_mock, state):
    """Test that clean execution delegates properly and returns result."""
    adapter = HarnessAdapter(safety=safety_mock)
    
    task_spec = {"source_files": ["safe.cs"], "worktree": "/tmp"}
    mock_harness_result = {"returncode": 0, "stdout": "ok", "stderr": ""}
    
    with patch("app.core.harness_adapter.call_harness", return_value=mock_harness_result) as mock_call:
        result = adapter.execute(task_spec, state)
        
        assert result["returncode"] == 0
        mock_call.assert_called_once_with(task_spec)
        assert len(state.safety_violations) == 0

def test_harness_adapter_post_scan_rollback(safety_mock, state):
    """Test that post-execution scan violations trigger rollback."""
    adapter = HarnessAdapter(safety=safety_mock)
    
    # Pre-flight passes, post-scan fails
    safety_mock.scan_worktree.return_value = [
        SafetyResult(safe=False, rule_id="S-1", severity="critical", message="bad content", file_path="test.cs")
    ]
    
    task_spec = {"source_files": ["test.cs"], "worktree": "/tmp"}
    mock_harness_result = {"returncode": 0, "stdout": "made edits", "stderr": ""}
    
    with patch("app.core.harness_adapter.call_harness", return_value=mock_harness_result) as mock_call:
        with patch("subprocess.run") as mock_subproc:
            result = adapter.execute(task_spec, state)
            
            assert result["returncode"] == -1
            assert "Safety violations detected" in result["stderr"]
            mock_call.assert_called_once_with(task_spec)
            mock_subproc.assert_called_once()
            assert mock_subproc.call_args[0][0][:2] == ["git", "checkout"]
            assert len(state.safety_violations) == 1
