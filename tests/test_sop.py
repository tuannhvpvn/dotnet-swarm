"""Tests for SOPEnforcer — algorithmic compliance checks."""
from app.core.sop import SOPEnforcer, SOPResult
from app.core.state import MigrationState, TaskItem


def test_pre_phase_fail_empty():
    state = MigrationState(migration_id="t", solution_path="/tmp")
    result = SOPEnforcer.pre_phase_check(state)
    assert result.passed is False
    assert "goal_defined" in result.failed_checks
    assert "scope_locked" in result.failed_checks
    assert "worktree_set" in result.failed_checks


def test_pre_task_fail_empty():
    task = TaskItem(id="t1", title="Empty Task")
    result = SOPEnforcer.pre_task_check(task)
    assert result.passed is False
    assert "single_deliverable" in result.failed_checks
    assert "input_clear" in result.failed_checks
    assert "output_clear" in result.failed_checks
    assert "verify_step_defined" in result.failed_checks


def test_pre_task_pass_full():
    task = TaskItem(
        id="t2", title="Full Task",
        source_files=["src/Foo.cs"],
        target_files=["src/Foo.cs"],
        done_criteria="File compiles without errors",
        verify_command="dotnet build"
    )
    result = SOPEnforcer.pre_task_check(task)
    assert result.passed is True
    assert result.failed_checks == []


def test_done_criteria_fail_no_reports():
    state = MigrationState(migration_id="t", solution_path="/tmp")
    result = SOPEnforcer.done_criteria_check(state)
    assert result.passed is False
    assert "report_generated" in result.failed_checks


def test_sop_result_passed_property():
    r = SOPResult(checks=[("a", True), ("b", True)])
    assert r.passed is True
    r2 = SOPResult(checks=[("a", True), ("b", False)])
    assert r2.passed is False
    assert r2.failed_checks == ["b"]


def test_post_task_check_fail_opens_in_non_git_environment():
    """post_task_check git checks must fail-open (return True) when git is unavailable.
    The safety scan is mocked to isolate git behavior (SOP-02)."""
    from unittest.mock import patch, MagicMock
    task = TaskItem(
        id="t3", title="Some Task",
        source_files=["Foo.cs"], target_files=["Foo.cs"],
        done_criteria="builds", verify_command="dotnet build"
    )
    # SafetyRules is imported lazily inside post_task_check — patch at its source module
    mock_instance = MagicMock()
    mock_instance.scan_worktree.return_value = []
    with patch("app.core.safety.SafetyRules", return_value=mock_instance):
        # Use /tmp as worktree — not a git repo, git diff returns non-zero → fail-open
        result = SOPEnforcer.post_task_check(task, "/tmp")
    # All three git-based checks should fail-open to True in non-git env
    assert result.passed is True


def test_post_task_check_has_three_checks():
    """post_task_check must evaluate scope_correct, no_contract_violation,
    and no_side_effects — the three post-execution SOP gates (SOP-02)."""
    task = TaskItem(id="t4", title="Post Task", source_files=["A.cs"], target_files=["A.cs"],
                    done_criteria="ok", verify_command="dotnet build")
    result = SOPEnforcer.post_task_check(task, "/tmp")
    check_names = [name for name, _ in result.checks]
    assert "scope_correct" in check_names
    assert "no_contract_violation" in check_names
    assert "no_side_effects" in check_names
