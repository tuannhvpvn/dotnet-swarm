import asyncio
from rich.console import Console
from app.core.state import MigrationState
from loguru import logger
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

console = Console()

class RufloMCPClient:
    def __init__(self):
        self.fallback_count = 0
        self.server_params = StdioServerParameters(
            command="npx", 
            args=["-y", "ruflo-mcp-server"]
        )

    async def _learn_pattern_async(self, state: MigrationState, error: str, fix: str) -> None:
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    payload = {
                        "action": "learn", 
                        "migration_id": state.migration_id, 
                        "phase": state.current_phase, 
                        "error": error[:600], 
                        "fix": fix[:400]
                    }
                    
                    await session.call_tool("learn_pattern", arguments=payload)
                    state.learned_patterns[f"pattern_{len(state.learned_patterns)+1}"] = f"{error[:60]} → {fix[:60]}"
                    console.print("[magenta]🧬 SONA: Learned new pattern via MCP[/]")
        except Exception as e:
            self.fallback_count += 1
            logger.warning(f"[Ruflo Unavailable] Fallback #{self.fallback_count}: {e}")

    async def _get_reasoning_async(self, query: str) -> str:
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool("analyze", arguments={"query": query})
                    
                    # Dùng fallback text nếu parse SDK types lỗi
                    if hasattr(result, "content") and getattr(result, "content", None):
                        return str(result.content[0].text)
                    return str(result)
        except Exception as e:
            self.fallback_count += 1
            logger.warning(f"[Ruflo Unavailable] Fallback #{self.fallback_count}: {e}")
            return "Ruflo unavailable (MCP Fallback)"

    # Synchronous wrappers for LangGraph compatibility
    def learn_pattern(self, state: MigrationState, error: str, fix: str):
        asyncio.run(self._learn_pattern_async(state, error, fix))

    def get_reasoning(self, query: str) -> str:
        return asyncio.run(self._get_reasoning_async(query))

ruflo_client = RufloMCPClient()
