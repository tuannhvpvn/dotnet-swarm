---
wave: 1
depends_on: []
files_modified: ["requirements.txt", "app/core/ruflo_mcp.py"]
autonomous: true
gap_closure: false
requirements_addressed: [MCP-01, MCP-02]
---

# Phase 5: Ruflo MCP Integration Plan

<objective>
To replace the legacy REST interface in `app/core/ruflo_mcp.py` with standard MCP (Model Context Protocol) connectivity to the SONA/Ruflo system using the official Python SDK, implementing resilient degradation and telemetry tracking capabilities.
</objective>

<tasks>

<task>
  <id>mcp-01-dependencies</id>
  <title>Integrate MCP Python SDK</title>
  <read_first>
    <file>requirements.txt</file>
  </read_first>
  <action>
Append `mcp` to `requirements.txt` to ensure the official SDK package provides stdio server parameters and client sessions.
  </action>
  <acceptance_criteria>
    <check>grep "mcp" requirements.txt</check>
  </acceptance_criteria>
</task>

<task>
  <id>mcp-02-client-rewrite</id>
  <title>Rewrite `RufloMCPClient`</title>
  <read_first>
    <file>app/core/ruflo_mcp.py</file>
  </read_first>
  <action>
Refactor `app/core/ruflo_mcp.py`.
1. **Remove** `import requests`.
2. **Import** `from mcp import StdioServerParameters, ClientSession` and `from mcp.client.stdio import stdio_client`.
3. **Internal Telemetry**: Add `self.fallback_count = 0` to the class.
4. **Transport Initialization**: Configure the server parameters to point to the Ruflo runtime:
   ```python
   server_params = StdioServerParameters(command="npx", args=["-y", "ruflo-mcp-server"])
   ```
5. **Sync wrappers**: Keep the public methods `get_reasoning` and `learn_pattern` synchronous. Internalize the async connection setup using `asyncio.run()`, e.g., `asyncio.run(self._get_reasoning_async(query))`.
6. **Error Handling/Degradation**: In the async handler, catch connection/timeout exceptions. 
   - Increment `self.fallback_count += 1`.
   - Log `[Ruflo Unavailable] Fallback #{self.fallback_count}: {e}`.
   - Return safe fallback strings without throwing exceptions outward to prevent halving the LangGraph swarm.
  </action>
  <acceptance_criteria>
    <check>python -m py_compile app/core/ruflo_mcp.py passes</check>
    <check>Verify `fallback_count` exists in the class logic</check>
  </acceptance_criteria>
</task>

</tasks>

<verification>
## Verification
1. Syntax validity logic: `python -m py_compile app/core/ruflo_mcp.py`
2. Validate graph isolation using the standalone `python -c "from app.core.ruflo_mcp import ruflo_client; print(ruflo_client.get_reasoning('test'))"` to ensure standard fallback behavior resolves when `npx` hasn't established server yet.
</verification>

<must_haves>
- Uses standard Python SDK (`mcp`) connection models via `StdioServerParameters`.
- Graceful degradation: The node skips tasks and continues running upon endpoint crashes instead of blowing up the parent process.
</must_haves>
