# Roadmap: dotnet-swarm

**8 phases** | **40 requirements mapped** | All v1 requirements covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Foundation | Redesign State and Persistence schema | Complete    | 2026-04-06 |
| 2 | Safety Layer | Implement absolute rules enforcer | Complete    | 2026-04-06 |
| 3 | Tool Adapter | Robust harness integrations with retry | Complete    | 2026-04-06 |
| 4 | Graph Redesign | Complete SOP-aligned node definitions | Complete    | 2026-04-06 |
| 5 | Ruflo MCP | Integrate SONA feedback system via MCP | Complete    | 2026-04-06 |
| 6 | Migration Skills | Define standard `.NET` modernization payload | SKL-01 to SKL-09 | 2 |
| 7 | SOP Compliance | Implement algorithmic checklist validation | SOP-01, SOP-02, SOP-03 | 2 |
| 8 | Polish & Integration | Ship CLI, dashboard, and integration tests | POL-01 to POL-06 | 3 |

## Phase Details

### Phase 1: Foundation
**Goal:** Redesign MigrationState and Persistence schema
**Requirements:** FND-01, FND-02, FND-03
**Success criteria:**
1. Tests validate `MigrationState` model creation and serialization.
2. Saving and loading states works successfully through the SQLite checks.

### Phase 2: Safety Layer
**Goal:** Implement absolute rules enforcer
**Requirements:** SFE-01, SFE-02, SFE-03
**Success criteria:**
1. `SafetyRules` block operations on `keys/` or restricted files.
2. All 3 execution vectors (path, content, git) trigger violation correctly.

### Phase 3: Tool Adapter
**Goal:** Robust harness integrations with retry
**Requirements:** TAD-01, TAD-02, TAD-03, TAD-04, TAD-05
**Success criteria:**
1. `adapter.execute()` reliably uses proper interface to CLIs (`omo`, `omx`, `omc`).
2. Retries work smoothly via `tenacity` on mock failures.
3. Jinja2 templates compile appropriately for task contexts.

### Phase 4: Graph Redesign
**Goal:** Complete SOP-aligned node definitions
**Requirements:** GRD-01 to GRD-09
**Success criteria:**
1. `human_gate_node` pauses graph execution using `interrupt_before`.
2. Graph edges cleanly route via standard workflow checkpoints.
3. `checkpoint_node` successfully flags deviation logic.
4. Final delivery automatically handles GitHub/ADO PR logic.

### Phase 5: Ruflo MCP
**Goal:** Integrate SONA feedback system via MCP
**Requirements:** MCP-01, MCP-02
**Success criteria:**
1. Ruflo client reliably utilizes MCP protocol instead of raw REST calls.

### Phase 6: Migration Skills
**Goal:** Define standard `.NET` modernization payload
**Requirements:** SKL-01 to SKL-09
**Success criteria:**
1. All 9 standard missing phase 1 migration core skills defined clearly in `.migration-skills`.
2. `sync_skills.py` successfully injects files.

### Phase 7: SOP Compliance
**Goal:** Implement algorithmic checklist validation
**Requirements:** SOP-01, SOP-02, SOP-03
**Success criteria:**
1. `SOPEnforcer` statically blocks phase progression missing requirements.
2. Reporting engine generates Markdown metrics without hallucinations.

### Phase 8: Polish & Integration
**Goal:** Ship CLI, dashboard, and integration tests
**Requirements:** POL-01 to POL-06
**Success criteria:**
1. Typer CLI commands `start`, `resume`, `approve` work end-to-end.
2. Streamlit Dashboard displays `status` live metrics.
3. Complete critical integration paths test coverage.
