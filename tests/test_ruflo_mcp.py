import unittest
import asyncio
from unittest.mock import patch, MagicMock

# Attempt to load the module (verifying its syntax)
from app.core.ruflo_mcp import RufloMCPClient
from app.core.state import MigrationState

class TestRufloMCP(unittest.TestCase):
    def test_mcp_dependency_installed(self):
        """Verify MCP dependency is available (MCP-01)."""
        import mcp
        self.assertIsNotNone(mcp)
        
        with open("requirements.txt", "r") as f:
            content = f.read()
            self.assertIn("mcp", content.lower())

    @patch("app.core.ruflo_mcp.stdio_client")
    def test_ruflo_client_fallback(self, mock_stdio_client):
        """Verify RufloMCPClient gracefully degrades when MCP is unavailable (MCP-02)."""
        # Force stdio_client context manager to raise an exception 
        mock_stdio_client.side_effect = Exception("Connection closed")
        
        client = RufloMCPClient()
        initial_count = client.fallback_count
        
        result = client.get_reasoning("test query")
        
        self.assertEqual(result, "Ruflo unavailable (MCP Fallback)")
        self.assertEqual(client.fallback_count, initial_count + 1)

    @patch("app.core.ruflo_mcp.stdio_client")
    def test_ruflo_client_learn_pattern_fallback(self, mock_stdio_client):
        """Verify learn_pattern degrades gracefully (MCP-02)."""
        mock_stdio_client.side_effect = Exception("Connection closed")
        
        client = RufloMCPClient()
        state = MigrationState(migration_id="123", current_phase="phase1", solution_path="/tmp") 
        initial_patterns_count = len(state.learned_patterns)
        
        # Should not raise exception
        client.learn_pattern(state, "error", "fix")
        
        self.assertEqual(client.fallback_count, 1)
        self.assertEqual(len(state.learned_patterns), initial_patterns_count)

if __name__ == '__main__':
    unittest.main()
