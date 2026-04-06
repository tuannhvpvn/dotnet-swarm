"""Tests for MigrationState and TaskItem schema."""
from app.core.state import MigrationState, TaskItem


def test_state_creation():
    state = MigrationState(migration_id="test-001", solution_path="/tmp/app")
    assert state.migration_id == "test-001"
    assert state.current_phase == "survey"
    assert state.workflow_state == "normal"
    assert state.tasks == []
    assert state.build_errors == []
    assert state.debt == []


def test_taskitem_sop_fields():
    task = TaskItem(id="t1", title="Test")
    assert hasattr(task, "source_files")
    assert hasattr(task, "target_files")
    assert hasattr(task, "done_criteria")
    assert hasattr(task, "verify_command")
    assert task.source_files == []
    assert task.target_files == []
    assert task.done_criteria is None
    assert task.verify_command is None


def test_state_model_dump_json():
    state = MigrationState(migration_id="test-002", solution_path="/tmp/app2")
    json_str = state.model_dump_json()
    restored = MigrationState.model_validate_json(json_str)
    assert restored.migration_id == state.migration_id
    assert restored.solution_path == state.solution_path
