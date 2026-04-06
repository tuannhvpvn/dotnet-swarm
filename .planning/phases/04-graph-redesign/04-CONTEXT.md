# Phase 4: Graph Redesign - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Refactor the LangGraph architecture to fully align with the SOP checklist. Remove the monolithic phase nodes in favor of a `migrate_task_node` queue, and introduce deterministic edges containing strict validation and `human_gate` checkpoints.

**Requirements:** GRD-01 to GRD-09
**Success criteria:**
1. `human_gate_node` pauses graph execution using `interrupt_before`.
2. Graph edges cleanly route via standard workflow checkpoints.
3. `checkpoint_node` successfully flags deviation logic.
4. Final delivery automatically handles GitHub/ADO PR logic.
</domain>

<decisions>
## Implementation Decisions

### Persistence Convergence (1A)
- **D-01:** Implement a Dual-Write database architecture. Use LangGraph's native `SqliteSaver` exclusively for graph checkpointing (to enable `interrupt_before` properly). We will keep `MigrationPersistence` parallelly writing high-level status updates to ensure the external Streamlit Dashboard maintains full observability.

### Node Granularity Cleanup (2A)
- **D-02:** Deprecate the old monolithic nodes (`phase1_migrator.py` & `phase2_modernizer.py`). The core workflow will use a single `migrate_task_node` working on granular subsets defined by the `planner`.

### Queen Supervisor (Ruflo) Routing Behavior (3A)
- **D-03:** Rewrite `app/core/graph.py` edge logic to be purely deterministic Python rules. The LLM (Ruflo) will no longer act as a traffic router.
- **D-04:** Relocate the Ruflo MCP integration into the `checkpoint_node` where it acts as a qualitative human-in-the-loop auditor prior to moving to verification.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source Specs
- `IMPLEMENTATION-PLAN-v2.md` § Phase 3: Graph Redesign — Task 3.1 to 3.5 specifics.
- `app/core/graph.py` — Current state of the LangGraph instance.
- `app/core/persistence.py` — Current state of the DB layer.

</canonical_refs>

<deferred>
## Deferred Ideas
- Cross-agent debate loops. For now, Ruflo acts as a solitary checkpoint auditor.
</deferred>

---

*Phase: 04-graph-redesign*
*Context gathered: via discuss-phase and Quint FPF comparison*
