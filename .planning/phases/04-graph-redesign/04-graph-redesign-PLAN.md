---
wave: 1
depends_on: []
files_modified: ["app/core/graph.py", "app/agents/planner.py", "app/agents/worker.py", "app/agents/surveyor.py", "app/agents/phase1_migrator.py", "app/agents/phase2_modernizer.py"]
autonomous: true
requirements_addressed: [GRD-01, GRD-02, GRD-03, GRD-04, GRD-05, GRD-06, GRD-07, GRD-08, GRD-09]
---

# Phase 4: Graph Redesign Plan

<objective>
Fully align the LangGraph configuration with the SOP checklist. Remove the monolithic phase nodes (`phase1_migrator`, `phase2_modernizer`) in favor of a granular `migrate_task_node` execution queue. Redefine edge routing to be strictly deterministic and introduce `interrupt_before` via LangGraph's `SqliteSaver` checkpointing, while retaining `MigrationPersistence` for Streamlit dashboard updates (Dual-Write strategy).
</objective>

<tasks>

<task>
  <id>grd-01-deprecate</id>
  <title>Deprecate legacy monolithic nodes</title>
  <action>
Delete `app/agents/phase1_migrator.py` and `app/agents/phase2_modernizer.py`. Remove their imports globally (e.g. from `app/core/graph.py` or `__init__.py`).
  </action>
  <acceptance_criteria>
    <check>Files `app/agents/phase1_migrator.py` and `app/agents/phase2_modernizer.py` are deleted</check>
  </acceptance_criteria>
</task>

<task>
  <id>grd-02-planner</id>
  <title>Implement planner node</title>
  <action>
Create `app/agents/planner.py`.
The node `plan_node` reads `state.inventory` (populated by surveyor) and breaks it down into a list of tasks.
These tasks are saved to `state.tasks`. Types of tasks: `csproj_conversion`, `nuget_migration`, etc., according to SOP.
Each `TaskItem` dict should have: `id`, `type`, `target`, `status: pending`, `depends_on`.
  </action>
  <acceptance_criteria>
    <check>File `app/agents/planner.py` exists with `plan_node(state)`</check>
  </acceptance_criteria>
</task>

<task>
  <id>grd-03-worker</id>
  <title>Implement task worker nodes</title>
  <action>
Create `app/agents/worker.py`.
Implement:
1. `human_gate_node(state)`: No-op node, used as a structural checkpoint for `interrupt_before`.
2. `prepare_node(state)`: Sets up worktrees dynamically if not present.
3. `migrate_task_node(state)`: 
   - Finds the first pending task in `state.tasks`.
   - Checks if any dependencies `depends_on` are unmet.
   - If unblocked, updates task status to "in_progress" and delegates to `HarnessAdapter` (from Phase 3).
   - If no tasks remain, leaves graph route intact for standard termination.
   - Saves `state.current_task_id`.
4. `checkpoint_node(state)`:
   - Contains the call to `ruflo_client` to perform an SOP review of the task changes via LLM.
   - Returns deterministic evaluation.
  </action>
  <acceptance_criteria>
    <check>File `app/agents/worker.py` contains 4 required node logic segments.</check>
  </acceptance_criteria>
</task>

<task>
  <id>grd-04-graph-logic</id>
  <title>Redesign edge and graph routes</title>
  <read_first>
    <file>app/core/graph.py</file>
  </read_first>
  <action>
Rewrite `app/core/graph.py`.

1. **Dual-Write DB Checkpointing**: 
   Import `SqliteSaver` from `langgraph.checkpoint.sqlite`.
   Use `checkpointer = SqliteSaver.from_conn_string("state/graph_checkpoints.db")`. Keep calling custom persistence (`persistence.save(state)`) manually at the end of nodes for UI dashboard.
2. **Nodes**: Add `survey_node`, `plan_node`, `human_gate_node`, `prepare_node`, `migrate_task_node`, `checkpoint_node`, `validate_node`, `fix_node`, `documenter_node`.
3. **Edges**:
   - `START` -> `surveyor`
   - `surveyor` -> `plan`
   - `plan` -> `human_gate`
   - `human_gate` relies on `interrupt_before=["human_gate_node"]`.
   - `human_gate` -> `prepare`
   - `prepare` -> `migrate_task`
   - `migrate_task` -> `checkpoint`
   - `checkpoint` -> `validate` (conditional: proceed vs reverse)
   - `validate` -> `fix` (conditional failure handling)
   - `validate` -> `migrate_task` (if more tasks pending)
   - `validate` -> `documenter` (if no more tasks)
   - `documenter` -> `END`
  </action>
  <acceptance_criteria>
    <check>graph uses `SqliteSaver`</check>
    <check>graph is compiled with `interrupt_before=["human_gate_node"]`</check>
  </acceptance_criteria>
</task>

</tasks>

<verification>
## Verification
1. `python -m py_compile app/core/graph.py` — ensure edges and conditional maps are syntactically sound.
2. Initialize and compile graph visually: generate Mermaid diagram with `.get_graph().draw_mermaid()` to verify standard SOP tracks.
</verification>

<must_haves>
- Uses `interrupt_before` for the structural `human_gate_node`.
- Integrates Dual-Write DB mechanism properly.
</must_haves>
