"""Tests for MigrationPersistence — real SQLite round-trip (D-01)."""
import pytest
from app.core.state import MigrationState, TaskItem
from app.core.persistence import MigrationPersistence


def test_save_and_load(tmp_path):
    state = MigrationState(
        migration_id="persist-test",
        solution_path=str(tmp_path)
    )
    state.tasks = [
        TaskItem(id="t1", title="Setup", status="completed"),
        TaskItem(id="t2", title="Migrate", status="in_progress"),
    ]

    p = MigrationPersistence(str(tmp_path))
    p.save(state)

    loaded = p.load("persist-test")
    assert loaded is not None
    assert loaded.migration_id == "persist-test"
    assert len(loaded.tasks) == 2


def test_load_missing_returns_none(tmp_path):
    p = MigrationPersistence(str(tmp_path))
    result = p.load("nonexistent-id")
    assert result is None
