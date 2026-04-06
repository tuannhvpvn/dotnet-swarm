"""Tests for worker node behaviors (GRD-03).

Covers: human_gate_node, prepare_node, migrate_task_node, checkpoint_node, fix_node.
All external integrations (vibekanban, ruflo, call_harness, create_worktree) are mocked.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.core.state import MigrationState, TaskItem


def make_state(**kwargs) -> MigrationState:
    defaults = dict(migration_id="test-001", solution_path="/tmp/test-solution")
    defaults.update(kwargs)
    return MigrationState(**defaults)


# ── human_gate_node ────────────────────────────────────────────────────────────

def test_human_gate_is_a_noop_passthrough():
    """human_gate_node should return state unchanged — it is a structural interrupt hook."""
    from app.agents.worker import human_gate_node
    state = make_state()
    original_id = state.migration_id

    result = human_gate_node(state)

    assert result is state
    assert result.migration_id == original_id


# ── prepare_node ───────────────────────────────────────────────────────────────

@patch("app.agents.worker.create_worktree", return_value="/tmp/worktree-abc")
@patch("app.agents.worker.vibekanban")
def test_prepare_node_creates_worktree_when_missing(mock_vk, mock_create_worktree):
    """prepare_node should create a worktree if worktree_path is not set."""
    from app.agents.worker import prepare_node
    state = make_state(worktree_path=None)

    result = prepare_node(state)

    mock_create_worktree.assert_called_once_with(state.solution_path, "migration")
    assert result.worktree_path == "/tmp/worktree-abc"


@patch("app.agents.worker.create_worktree")
@patch("app.agents.worker.vibekanban")
def test_prepare_node_skips_worktree_when_already_set(mock_vk, mock_create_worktree):
    """prepare_node should NOT create a worktree if one is already configured."""
    from app.agents.worker import prepare_node
    state = make_state(worktree_path="/tmp/existing-worktree")

    prepare_node(state)

    mock_create_worktree.assert_not_called()


# ── migrate_task_node ──────────────────────────────────────────────────────────

@patch("app.agents.worker.call_harness", return_value={"returncode": 0, "stdout": "ok"})
@patch("app.agents.worker.vibekanban")
def test_migrate_task_marks_completed_on_success(mock_vk, mock_harness):
    """migrate_task_node should mark the task completed when harness returns 0."""
    from app.agents.worker import migrate_task_node
    task = TaskItem(id="t-01", title="Upgrade csproj", type="csproj_conversion", target="App.csproj")
    state = make_state(tasks=[task])

    result = migrate_task_node(state)

    assert result.tasks[0].status == "completed"
    assert result.current_task_id == "t-01"


@patch("app.agents.worker.call_harness", return_value={"returncode": 1, "stdout": "error"})
@patch("app.agents.worker.vibekanban")
def test_migrate_task_marks_failed_on_harness_error(mock_vk, mock_harness):
    """migrate_task_node should mark the task failed when harness returns non-zero."""
    from app.agents.worker import migrate_task_node
    task = TaskItem(id="t-02", title="NuGet migration", type="nuget_migration", target="App.csproj")
    state = make_state(tasks=[task])

    result = migrate_task_node(state)

    assert result.tasks[0].status == "failed"


@patch("app.agents.worker.vibekanban")
def test_migrate_task_with_no_pending_tasks_returns_state(mock_vk):
    """migrate_task_node should return state unchanged when there are no pending tasks."""
    from app.agents.worker import migrate_task_node
    task = TaskItem(id="t-03", title="Done task", type="csproj_conversion", target="App.csproj", status="completed")
    state = make_state(tasks=[task])

    result = migrate_task_node(state)

    assert result.current_task_id is None  # unchanged
    assert result.tasks[0].status == "completed"


# ── checkpoint_node ────────────────────────────────────────────────────────────

@patch("app.agents.worker.ruflo_client")
@patch("app.agents.worker.vibekanban")
def test_checkpoint_node_calls_ruflo_and_returns_state(mock_vk, mock_ruflo):
    """checkpoint_node should call ruflo_client.get_reasoning and pass state through."""
    from app.agents.worker import checkpoint_node
    mock_ruflo.get_reasoning.return_value = "No deviations found"
    state = make_state(current_task_id="t-01")

    result = checkpoint_node(state)

    mock_ruflo.get_reasoning.assert_called_once()
    assert result is state


# ── fix_node ───────────────────────────────────────────────────────────────────

@patch("app.agents.worker.vibekanban")
def test_fix_node_increments_fix_attempts_and_resets_task(mock_vk):
    """fix_node should increment fix_attempts and reset the current task to in_progress."""
    from app.agents.worker import fix_node
    task = TaskItem(id="t-04", title="Failed task", type="csproj_conversion", target="App.csproj", status="failed")
    state = make_state(tasks=[task], current_task_id="t-04", fix_attempts=0)

    result = fix_node(state)

    assert result.fix_attempts == 1
    assert result.tasks[0].status == "in_progress"
