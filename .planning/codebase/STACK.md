# STACK.md — Technology Stack

## Language & Runtime

- **Language:** Python 3.12+
- **Package manager:** pip / setuptools
- **Configuration:** `pyproject.toml`, `requirements.txt`, `config.yaml`
- **Entry points:** `main.py` (CLI via Typer), `dashboard.py` (Streamlit UI), `ruflo_start.py` (Ruflo harness start)

## Core Frameworks

### LangGraph (≥0.2.0)
The backbone orchestration framework. Defines the agent graph as a `StateGraph`, compiles it with a `MemorySaver` checkpointer, and streams execution events.
- `app/core/graph.py` — constructs and runs the `build_migration_graph()` function
- Node types: `supervisor`, `surveyor`, `phase1_migrator`, `phase2_modernizer`, `validator`, `documenter`
- Edges: START → supervisor → (conditional) worker → validator → documenter → supervisor

### LangChain (≥0.3.0)
Used indirectly through LangGraph integration for agent/chain patterns.

### Pydantic v2 (≥2.10)
- State model `MigrationState` defined in `app/core/state.py`
- Settings model `Settings` in `app/core/config.py` (via `pydantic-settings`)

### Typer (≥0.15)
CLI interface. Entry command `start` in `main.py` accepts `solution_path` and `phase` arguments.

### Rich (≥13.0)
All console output uses `rich.console.Console` for colored, formatted terminal output.

### Streamlit (optional)
`dashboard.py` provides a live Streamlit dashboard polling `state/current_state.json` with a 2-second refresh loop.

## Supporting Libraries

| Library | Version | Purpose |
|---|---|---|
| `pyyaml` | latest | YAML config parsing |
| `requests` | latest | HTTP calls to MCP services |
| `loguru` | latest | Structured file logging |
| `tenacity` | latest | Retry logic (available, usage TBD) |
| `sqlite3` | stdlib | State persistence database |

## AI Harness Commands (External)

The swarm delegates actual .NET code edits to external AI harnesses via subprocess calls (`app/tools/adapter.py`):

| Harness | Command | Model | Use Case |
|---|---|---|---|
| `omo` | `ultrawork` | `claude-4.6-sonnet` | Survey & validate |
| `omx` | `team` | `claude-4.6-sonnet` | Phase 1 lift-and-shift |
| `omc` | `team` | `claude-4.6-opus` | Phase 2 modernize |
| `omo` | `ultrawork` | `glm-5` | Validate (build+test) |

These harnesses must be pre-installed on the host machine and available on `$PATH`.

## Environment Configuration

Settings loaded via `pydantic-settings` from:
1. `.env` file (env var overrides)
2. `config.yaml` (runtime config, read as separate YAML load)
3. Defaults in `app/core/config.py`

Key config fields:
- `migration_id` — unique migration run ID
- `vibekanban_url` — default `http://localhost:3000/api/mcp`
- `ruflo_mcp_url` — default `http://localhost:3131`
- `gitnexus_mcp_url` — default `http://localhost:4000/mcp`

## Persistence

- **SQLite DB:** `{solution_path}/state/migration.db` (3-column table: `migration_id`, `state_json`, `last_updated`)
- **JSON snapshot:** `{solution_path}/state/current_state.json` — read by Streamlit dashboard
- **In-memory checkpointing:** LangGraph `MemorySaver` for graph state during run

## Migration Skills

Pre-built SKILL.md bundles in `.migration-skills/`:
- `dotnet-phase1-csproj-upgrade`
- `dotnet-oracle-ef6-migration`
- `dotnet-msal-update`
- `dotnet-clean-arch-cqrs`
- `dotnet-ddd-value-objects`

At startup, `app/utils/sync_skills.py` copies these into the target repo's `.kiro/skills/`, `.opencode/skills/`, `.omc/skills/`, and `.omx/skills/` directories so the harnesses can use them.
