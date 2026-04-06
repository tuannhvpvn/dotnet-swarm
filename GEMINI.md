<!-- GSD:project-start source:PROJECT.md -->
## Project

**dotnet-migration-swarm**

A Queen-led autonomous agent swarm for automating .NET codebase migrations. It utilizes a LangGraph workflow, integrates with multiple MCPs (Ruflo, GitNexus, VibeKanban), and orchestrates external AI harnesses. The current focus is moving the prototype to a production-ready state by fixing review issues and enforcing Standard Operating Procedure (SOP) compliance.

**Core Value:** Reliable, safe, and autonomous migration of .NET applications without risking production side-effects or hallucinated codebase states, ensuring all steps are verifiable and SOP compliant.

### Constraints

- **Technology**: Must use Python 3.12+, LangGraph, and Pydantic v2.
- **Safety**: No operations may touch blacklisted folders (e.g., `keys/`, `certs/`) or contain hardcoded keys (Regex scanned).
- **Execution**: The process must support a Human Gate (interactive pause/resume) between critical phases.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Language & Runtime
- **Language:** Python 3.12+
- **Package manager:** pip / setuptools
- **Configuration:** `pyproject.toml`, `requirements.txt`, `config.yaml`
- **Entry points:** `main.py` (CLI via Typer), `dashboard.py` (Streamlit UI), `ruflo_start.py` (Ruflo harness start)
## Core Frameworks
### LangGraph (≥0.2.0)
- `app/core/graph.py` — constructs and runs the `build_migration_graph()` function
- Node types: `supervisor`, `surveyor`, `phase1_migrator`, `phase2_modernizer`, `validator`, `documenter`
- Edges: START → supervisor → (conditional) worker → validator → documenter → supervisor
### LangChain (≥0.3.0)
### Pydantic v2 (≥2.10)
- State model `MigrationState` defined in `app/core/state.py`
- Settings model `Settings` in `app/core/config.py` (via `pydantic-settings`)
### Typer (≥0.15)
### Rich (≥13.0)
### Streamlit (optional)
## Supporting Libraries
| Library | Version | Purpose |
|---|---|---|
| `pyyaml` | latest | YAML config parsing |
| `requests` | latest | HTTP calls to MCP services |
| `loguru` | latest | Structured file logging |
| `tenacity` | latest | Retry logic (available, usage TBD) |
| `sqlite3` | stdlib | State persistence database |
## AI Harness Commands (External)
| Harness | Command | Model | Use Case |
|---|---|---|---|
| `omo` | `ultrawork` | `claude-4.6-sonnet` | Survey & validate |
| `omx` | `team` | `claude-4.6-sonnet` | Phase 1 lift-and-shift |
| `omc` | `team` | `claude-4.6-opus` | Phase 2 modernize |
| `omo` | `ultrawork` | `glm-5` | Validate (build+test) |
## Environment Configuration
- `migration_id` — unique migration run ID
- `vibekanban_url` — default `http://localhost:3000/api/mcp`
- `ruflo_mcp_url` — default `http://localhost:3131`
- `gitnexus_mcp_url` — default `http://localhost:4000/mcp`
## Persistence
- **SQLite DB:** `{solution_path}/state/migration.db` (3-column table: `migration_id`, `state_json`, `last_updated`)
- **JSON snapshot:** `{solution_path}/state/current_state.json` — read by Streamlit dashboard
- **In-memory checkpointing:** LangGraph `MemorySaver` for graph state during run
## Migration Skills
- `dotnet-phase1-csproj-upgrade`
- `dotnet-oracle-ef6-migration`
- `dotnet-msal-update`
- `dotnet-clean-arch-cqrs`
- `dotnet-ddd-value-objects`
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Language Style
- **Python 3.12+** with modern type hints everywhere
- Union types use `X | None` syntax (not `Optional[X]`) — Python 3.10+ style
- No `from __future__ import annotations` needed (runtime 3.12+)
- Vietnamese is used for all user-facing console output strings and inline comments (bilingual codebase)
## Naming Conventions
| Construct | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `phase1_migrator.py` |
| Classes | `PascalCase` | `MigrationState`, `GitNexusAdapter` |
| Functions | `snake_case` | `build_migration_graph()`, `call_harness()` |
| Agent nodes | `{name}_node` suffix | `surveyor_node`, `validator_node` |
| Singleton exports | lowercase module-level | `gitnexus`, `vibekanban`, `ruflo_client`, `settings` |
| Skills | `kebab-case` directories | `dotnet-clean-arch-cqrs` |
| Config fields | `snake_case` Pydantic | `migration_id`, `ruflo_mcp_url` |
## Agent Node Pattern
- Always call `vibekanban.update_agent()` at start and end
- Always use `console.print()` with colored bracket formatting for status
- Always delegate code execution to external harness via `call_harness()`
- Mutate and return the `state` object directly
## HTTP Adapter Pattern
- Always check `self.enabled` first — all MCP calls can be disabled
- Always catch bare `Exception` on HTTP calls — never crash on integration failure
- Always return safe defaults (`False`, `None`, `"validator"`) on failure
- Timeout values: Ruflo 6–10s, GitNexus 10–30s, VibeKanban 4s
## Error Handling Philosophy
## Console Output Style
- **bold green** — success / completion
- **bold blue** — info / scan
- **bold yellow** — phase 1 migrator
- **bold magenta** — phase 2 modernizer / auto-skill
- **bold cyan** — validator / harness calls
- **yellow** — warnings
- **green with prefix ✅** — operation success
- **yellow with prefix ⚠️** — non-fatal warnings
## Logging
- `logger.info()` — general operational messages
- `logger.error()` — errors/failures
- `logger.success()` — completions (green output)
- `logger.debug()` — not currently used
- Log files written to solution directory by `setup_logging()` in `app/core/logger.py`
## Configuration Access
## Import Organization
## Pydantic Usage
- `BaseModel` for `MigrationState` (shared state)
- `BaseSettings` + `SettingsConfigDict` for `Settings`
- `.model_dump_json()` and `.model_validate()` (Pydantic v2 API)
- `Field(default_factory=...)` for mutable defaults
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern: Queen-Led Agent Swarm (LangGraph + MCP)
## The Two Migration Phases
| Phase | Goal | Harness | Model |
|---|---|---|---|
| Phase 1 — Lift & Shift | Upgrade `.csproj`, packages, and syntax to .NET 10 without architectural changes | `omx` | `claude-4.6-sonnet` |
| Phase 2 — Modernize | Refactor to Clean Architecture + DDD + CQRS + TDD + Dapper/EF Core | `omc` | `claude-4.6-opus` |
## Graph Architecture
```
```
## State Model
```python
```
## AI Harness Delegation Layer
```python
```
## Self-Healing & Auto-Skill Loop
```
```
## Worktree Isolation
- `app/utils/worktree.py` — `create_worktree(solution_path, prefix)`
- Creates: `{solution_path}/.worktrees/{prefix}-{timestamp}/`
- Falls back to plain directory if git fails
## Persistence Architecture
## Observability Architecture
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
