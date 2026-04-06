# INTEGRATIONS.md — External Services & APIs

## Ruflo MCP (Queen Supervisor Brain)

**Purpose:** Acts as the reasoning and routing engine for the Queen Supervisor node. Provides hierarchical task routing and pattern learning.

**Transport:** HTTP REST over `requests.Session`
**Base URL:** `http://localhost:3131` (configurable via `ruflo_mcp_url`)
**Adapter:** `app/core/ruflo_mcp.py` — `RufloMCPClient`

### Endpoints Used

| Method | Path | Purpose |
|---|---|---|
| POST | `/learn` | Submit error+fix pair to build Ruflo's reasoning bank |
| POST | `/reason` | Query reasoning for a given context string |
| POST | `/route` | Get next graph node to visit (hierarchical routing) |

### Payload Examples

```python
# /learn
{"action": "learn", "migration_id": "mig-202604", "phase": "phase1", "error": "...", "fix": "..."}

# /route
{"action": "route_hierarchical", "migration_id": "mig-202604", "current_phase": "phase1", "context": "default"}
```

### Failure Handling
All calls are wrapped in bare `except` blocks — Ruflo unavailability silently degrades (returns `"validator"` for routing, `"Ruflo unavailable"` for reasoning).

---

## GitNexus MCP (Codebase Knowledge Graph)

**Purpose:** Indexes the target .NET solution into a knowledge graph, enabling semantic queries for accurate codebase understanding.

**Transport:** HTTP REST over `requests.Session`
**Base URL:** `http://localhost:4000/mcp` (configurable via `gitnexus_mcp_url`)
**Adapter:** `app/integrations/gitnexus_adapter.py` — `GitNexusAdapter`
**Singleton:** `gitnexus` instance exported from module

### Lifecycle
- Indexed at startup in `main.py` if `gitnexus_index_on_start=True`
- Re-indexed in `surveyor_node` before scan

### Endpoints Used

| Method | Path | Purpose |
|---|---|---|
| POST | `/index` | Index a .NET repo by path |
| POST | `/query` | Query the knowledge graph |

### Payload Examples

```python
# /index
{"path": "/path/to/solution", "language": "csharp"}

# /query
{"query": "what Oracle dependencies exist?"}
```

---

## VibeKanban MCP (Agent Status Board)

**Purpose:** Real-time agent status tracking and event push. Acts as a kanban/event bus for observability.

**Transport:** HTTP REST over `requests.Session`
**Base URL:** `http://localhost:3000/api/mcp` (configurable via `vibekanban_url`)
**Adapter:** `app/integrations/vibekanban_adapter.py` — `VibekanbanAdapter`
**Singleton:** `vibekanban` instance exported from module

### Endpoints Used

| Method | Path | Purpose |
|---|---|---|
| POST | `/push` | Push any typed event with payload |

### Event Types Used

| Event Type | Trigger |
|---|---|
| `agent_status` | Agent start, progress, complete |
| `human_gate` | Phase 1 complete, awaiting human approval |
| `error` | Build/test failure in validator node |

### Payload Structure

```python
{
    "source": "dotnet-migration-swarm",
    "timestamp": "2026-04-06T08:00:00.000",
    "event_type": "agent_status",
    "data": {"agent": "Surveyor", "status": "✅ Completed", "progress": 100.0}
}
```

---

## External AI Harnesses (omo / omx / omc)

**Purpose:** Delegate actual .NET code transformation to AI coding agents installed on the host.

**Transport:** `subprocess.run()` — executed as CLI commands
**Adapter:** `app/tools/adapter.py` — `call_harness()`
**Timeout:** 300 seconds per harness call

### Command Pattern

```bash
{harness} {command} --model {model} --task "{task}" --work-dir {worktree}
```

### Harness Map

| Harness | Deployed To | Primary Role |
|---|---|---|
| `omo` | Host `$PATH` | Survey + Validate |
| `omx` | Host `$PATH` | Phase 1 lift-and-shift team |
| `omc` | Host `$PATH` | Phase 2 Clean Arch modernize team |

---

## Local Streamlit Dashboard

**Purpose:** Developer observability — displays live migration state.
**File:** `dashboard.py`
**Polls:** `state/current_state.json` every 2 seconds
**Not integrated via HTTP** — reads local filesystem JSON snapshot directly.

---

## Git Worktree (Target .NET Repo)

**Purpose:** Creates isolated git worktrees for each migration phase to prevent cross-phase interference.
**Adapter:** `app/utils/worktree.py` — `create_worktree()`
**Path pattern:** `{solution_path}/.worktrees/{phase}-{YYYYMMDD-HHMMSS}/`
**Fallback:** Creates plain directory if `git worktree add` fails.
