# Phase 3: Tool Adapter Rewrite - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Refactor the raw `call_harness()` subprocess executor into a robust tool adapter system that understands the specific CLI capabilities of `omo`, `omx`, `omc`, and `kiro`. Implement dynamic context injection and resilient retry loops.

**Requirements:** TAD-01, TAD-02, TAD-03, TAD-04, TAD-05
**Success criteria:**
1. `adapter.execute()` reliably uses proper interface to CLIs.
2. Retries work smoothly via `tenacity` on mock failures.
3. Dependencies and skills are properly injected.
</domain>

<decisions>
## Implementation Decisions

### Context & Skill Injection Strategy (1A)
- **D-01:** The adapter will use Sidecar Files for large payloads. Before a harness starts, generate tool-specific context files (e.g., `CLAUDE.md`, `.kiro/rules/*.md`) in the worktree containing migration skills and guidelines. The main command directive remains in the `--task` flag.

### Adapter Architecture Layout (2A)
- **D-02:** `app/tools/adapter.py` will act as a factory exposing an abstract `HarnessHarness` class and concrete subclasses (`CodexHarness`, `ClaudeCodeHarness`, `KiroHarness`, etc.).
- **D-03:** `app/core/harness_adapter.py` (the safety interceptor from Phase 2) will consume `app/tools/adapter.py`, requesting the correct tool executor from the factory, wrapping it in safety logic.

### Retry Strategy with Tenacity (3A)
- **D-04:** Implement Feedback Loop Retry using `tenacity`. If a harness fails with a non-zero exit code, the retry loop will catch it, extract `stderr`, and append it to the context or prompt for the next attempt (e.g., "Previous error: {stderr}").

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source Specs
- `IMPLEMENTATION-PLAN-v2.md` § Phase 2: Tool Adapter Rewrite — Task 2.1, 2.2 specifics.
- `app/tools/adapter.py` — Current state of the legacy `call_harness` executor.
- `app/core/harness_adapter.py` — The safety wrapper that must be integrated with the new factory.

</canonical_refs>

<deferred>
## Deferred Ideas
- Sophisticated parsing of LLM outputs. For now, exit code determines success.
- Complex parallel execution logic — this is just the low-level adapter for 1 task.
</deferred>

---

*Phase: 03-tool-adapter*
*Context gathered: via discuss-phase and Quint FPF comparison*
