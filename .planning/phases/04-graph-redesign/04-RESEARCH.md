# Phase 4: Graph Redesign - Research

**Objective:** What do I need to know to PLAN this phase well?

## Domain Understanding

The goal is to refactor `app/core/graph.py` and the node implementations to shift from an LLM-routed monolithic workflow to a deterministic, SOP-aligned node graph.

Current state (`app/core/graph.py`):
- `supervisor_node` delegates entirely to `ruflo_client.route_task(state, "default")`.
- Monolithic nodes: `surveyor_node`, `phase1_migrator_node`, `phase2_modernizer_node`, `validator_node`, `documenter_node`.
- Missing granularity, no `SqliteSaver` utilization.

Desired state:
- Edges defined by deterministic python code (e.g. `workflow.add_edge("plan_node", "human_gate_node")`).
- Granular nodes: `survey_node`, `plan_node`, `human_gate_node`, `prepare_node`, `migrate_task_node`, `checkpoint_node`, `fix_node`, `learn_node`, `deliver_node`.
- Dual-Write Persistence (D-01): `graph = workflow.compile(checkpointer=SqliteSaver(conn))` combined with `MutationPersistence` updates.

## Technical Analysis

1. **SqliteSaver Integration:**
   - LangGraph `SqliteSaver` requires a sqlite3 connection. We need to initialize this in `build_migration_graph` alongside `MigrationPersistence`.
   - `interrupt_before=["human_gate_node"]` is how LangGraph handles breakpoints. When execution stops there, we use `graph.update_state()` to resume.

2. **Graph Structure (Deterministic):**
   - START 
   - `survey_node` -> extracts rep inventory (GRD-02)
   - `plan_node` -> builds atomic tasks list (GRD-03)
   - `human_gate_node` (interrupt) -> waits for user approval (GRD-07)
   - `prepare_node` -> initial setup
   - `migrate_task_node` -> processes one task in a loop (GRD-04)
   - `checkpoint_node` -> calls Ruflo MCP for qualitative review (GRD-05, D-04)
   - `fix_node` -> if checkpoint fails, attempt to fix (GRD-06)
   - `learn_node` -> SONA feedback generation (GRD-08)
   - `deliver_node` -> Commit/PR (GRD-09)
   - END

3. **Routing Logic (D-03):**
   - Edges out of `checkpoint_node` should conditionally route to `fix_node` or back to `migrate_task_node` (next task) or `learn_node` (if all tasks done).
   - This requires `MigrationState` to hold `tasks: list[TaskItem]` and a cursor or similar to track the current active task. Currently, `state.py` has `tasks: list[TaskItem]` but we need to ensure the graph iteration can track index.

## Validation Architecture

To ensure the new graph fulfills requirements, the verification plan should include:
- Execution tests that check if `interrupt_before` correctly halts the execution before `human_gate_node`.
- Mock validations for `checkpoint_node` returning failures to see if it correctly routes to `fix_node`.
- Ensure Dual-Write database correctly produces expected `.db` entries and LangGraph checkpoint data.
