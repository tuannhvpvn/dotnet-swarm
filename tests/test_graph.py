"""Tests for graph compilation — real build_migration_graph call (D-01)."""
import pytest


def test_build_graph_compiles():
    """Verify the LangGraph compiles without error (skip if deps missing)."""
    try:
        from app.core.graph import build_migration_graph
        graph = build_migration_graph()
        assert graph is not None
    except ImportError as e:
        pytest.skip(f"LangGraph deps not installed: {e}")
    except Exception as e:
        pytest.fail(f"build_migration_graph() raised: {e}")
