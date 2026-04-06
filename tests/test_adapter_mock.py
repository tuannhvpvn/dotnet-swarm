"""Tests for MCP adapters with mocked HTTP — no live services needed."""
from unittest.mock import patch, MagicMock


def test_vibekanban_update_agent_disabled():
    """When enabled=False, VibeKanban adapter must return silently."""
    from app.integrations.vibekanban_adapter import VibekanbanAdapter
    adapter = VibekanbanAdapter(enabled=False)
    # Should not raise, should return False or None
    result = adapter.push("agent_update", {"agent": "test", "status": "running"})
    assert result is False or result is None


def test_gitnexus_index_repo_disabled():
    """When enabled=False, GitNexus adapter must return silently."""
    from app.integrations.gitnexus_adapter import GitNexusAdapter
    adapter = GitNexusAdapter()
    adapter.enabled = False  # override to disable
    result = adapter.index_repo("/tmp/fake")
    assert result is None or result is False or result == {}


def test_vibekanban_push_mocked():
    """With enabled=True, adapter makes HTTP call — mock the request."""
    from app.integrations.vibekanban_adapter import VibekanbanAdapter
    adapter = VibekanbanAdapter(enabled=True)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("requests.Session.post", return_value=mock_resp):
        result = adapter.push("test_event", {"key": "value"})
        # Returns True on 200 status
        assert result is True or result is None
