# Phase 5: Ruflo MCP - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace legacy REST wrappers in `app/core/ruflo_mcp.py` with standard MCP connectivity to the SONA / Ruflo system. This ensures the `.NET Swarm` directly consumes external auditing context using robust cross-agent protocols rather than hardcoded HTTP requests.

**Requirements:** MCP-01, MCP-02
**Success criteria:**
1. Ruflo client reliably utilizes MCP protocol instead of raw REST calls.
</domain>

<decisions>
## Implementation Decisions

### MCP Integration Architecture (1A)
- **D-01:** Implement standard Python MCP capability using `mcp` library (instead of wrapping multiple raw `subprocess.run` CLI calls). We will establish an async stdio context connection once to avoid Node.js initialization latency loops per task.

### Graceful Degradation / Fallback Behavior (2A) + Metric
- **D-02:** Decouple workflow stability from external AI. If the MCP endpoint crashes or is unavailable, the swarm must log a `WARNING`, skip the AI audit, and proceed strictly along the deterministic execution graph logic.
- **D-03 (Metric Tracking):** Implement a `fallback_count` metric internal to `RufloMCPClient` returning exactly how many checkpoints were processed blind due to MCP connection timeouts. This ensures project operators can investigate instability. Example spec: `logger.warning(f"[Ruflo Unavailable] Fallback #{self.fallback_count}: {e}")`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source Specs
- `IMPLEMENTATION-PLAN-v2.md` § Phase 4: Ruflo MCP Integration (Note: aligned as Phase 5 in ROADMAP structure)
- `app/core/ruflo_mcp.py` — Current legacy REST architecture codebase.

</canonical_refs>

<deferred>
## Deferred Ideas
None.
</deferred>

---

*Phase: 05-ruflo-mcp*
*Context gathered: via discuss-phase and Quint FPF comparison*
