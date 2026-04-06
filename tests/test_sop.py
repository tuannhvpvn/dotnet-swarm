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
