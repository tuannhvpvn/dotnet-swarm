# Architecture — .NET Migration Swarm v1.0

## Overview

A Queen-led autonomous agent swarm for migrating .NET codebases to .NET 10 + Clean Architecture. Uses LangGraph for orchestration, external AI harnesses for code execution, and a suite of MCP integrations for observability and knowledge management.

---

## Graph Topology

```
START → supervisor → planner → worker (migrate_task_node loop)
                                 ↓
                            validator
                                 ↓
                           documenter
                                 ↓
                         human_gate (if blocked)
                                 ↓
                          supervisor (loop back or END)
```

**Node responsibilities:**
- `supervisor`: routes based on `workflow_state` (normal/blocked/remediation)
- `planner`: surveys codebase → builds `TaskItem` queue from inventory
- `worker` (`migrate_task_node`): dequeues one task, runs `SOPEnforcer.pre_task_check`, delegates to harness, runs `SOPEnforcer.post_task_check`
- `validator`: runs `dotnet build` + `SOPEnforcer.done_criteria_check`
- `documenter`: calls `MigrationReporter.generate_all()`, writes reports
- `human_gate`: LangGraph interrupt — pauses graph, waits for `approve` CLI command

---

## The Two Migration Phases

| Phase | Goal | Harness | Model |
|---|---|---|---|
| Phase 1 — Lift & Shift | Upgrade `.csproj`, packages, syntax to .NET 10 | `omx` (`omx exec`) | `claude-sonnet-4-6` |
| Phase 2 — Modernize | Refactor to Clean Architecture + DDD + CQRS | `claude` (`claude -p`) | `claude-opus-4-6` |

---

## Dual-Write Persistence Strategy

Every state mutation writes to two locations:

| Location | Format | Purpose |
|---|---|---|
| `{solution}/state/migration.db` | SQLite 3-table schema | Durable, queryable, crash-safe |
| `{solution}/state/current_state.json` | JSON (`model_dump_json`) | Live read by Streamlit dashboard |

```python
persistence.save(state)  # writes both atomically
state = persistence.load(migration_id)  # reads from SQLite
```

---

## SOPEnforcer Integration Points

```
worker node:
  pre_task_check(task) ──→ FAIL → workflow_state = "blocked"
                       └──→ PASS → delegate to harness

  post_task_check(task, worktree) → FAIL → workflow_state = "remediation"

validator node:
  done_criteria_check(state) → FAIL → block phase completion
```

All checks are in `app/core/sop.py`. No LLM calls in any gate.

---

## MCP Integrations

| MCP | Transport | Purpose | Fallback |
|---|---|---|---|
| Ruflo | `stdio` (official `mcp` SDK) | Reasoning bank — store/retrieve patterns | In-memory dict + `fallback_count` metric |
| GitNexus | HTTP/SSE | Codebase semantic search + indexing | Disabled gracefully (`enabled=False`) |
| Vibekanban | HTTP | Agent status board | Silent no-op |

---

## Migration Skills (13 total)

**Legacy Phase 2 skills (5):**
- `dotnet-phase1-csproj-upgrade`
- `dotnet-oracle-ef6-migration`
- `dotnet-msal-update`
- `dotnet-clean-arch-cqrs`
- `dotnet-ddd-value-objects`

**Phase 1 Lift-&-Shift skills (8):**
- `dotnet-controller-migration`
- `dotnet-webconfig-migration`
- `dotnet-startup-migration`
- `dotnet-auth-migration`
- `dotnet-namespace-migration`
- `dotnet-logging-migration`
- `dotnet-docker-migration`
- `dotnet-nuget-migration`

All skills use **Strict/Authoritative** formatting to prevent AI hallucination during code migration.

---

## Key Files

| File | Role |
|---|---|
| `main.py` | Typer CLI: `start`, `resume`, `status`, `approve` |
| `dashboard.py` | Streamlit live dashboard (JSON polling) |
| `app/core/graph.py` | LangGraph graph builder |
| `app/core/state.py` | `MigrationState` + `TaskItem` Pydantic models |
| `app/core/sop.py` | `SOPEnforcer` — all 4 gate methods |
| `app/core/persistence.py` | `MigrationPersistence` — dual-write SQLite + JSON |
| `app/core/safety.py` | `SafetyRules` — blacklist + regex scanning |
| `app/utils/reporter.py` | `MigrationReporter` — 6 report types, state-direct only |
| `app/integrations/ruflo_mcp.py` | Ruflo MCP client with fallback telemetry |
| `config/safety.yaml` | Blacklist folders, files, content patterns |
| `config.yaml` | Unified configuration — all 9 sections |
