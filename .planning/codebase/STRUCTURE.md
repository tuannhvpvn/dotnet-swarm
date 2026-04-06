# STRUCTURE.md — Directory Layout & Organization

## Root Layout

```
dotnet-swarm/
├── main.py                        # CLI entry point (Typer app)
├── dashboard.py                   # Streamlit live dashboard
├── ruflo_start.py                 # Ruflo harness initializer
├── run-migration-with-dashboard.sh # Shell script: launch swarm + dashboard
├── config.yaml                    # Runtime configuration (MCP URLs, migration ID)
├── pyproject.toml                 # Project metadata & dependencies
├── requirements.txt               # Flat requirements list
├── IMPLEMENTATION-PLAN-v2.md     # Development roadmap/plan document
├── README.md                      # Brief overview
│
├── app/                           # Main Python package
│   ├── __init__.py
│   ├── agents/                    # LangGraph agent nodes
│   ├── core/                      # Core infrastructure
│   ├── integrations/              # MCP adapter modules
│   ├── tools/                     # Harness adapter
│   └── utils/                     # Utility functions
│
├── .migration-skills/             # Migration skill bundles (SKILL.md format)
├── .planning/                     # GSD planning directory
│   └── codebase/                  # Codebase map documents (this folder)
└── .git/                          # Git history
```

## `app/agents/` — LangGraph Nodes

Each file exports a single `*_node(state) -> state` function:

| File | Node Name | Responsibility |
|---|---|---|
| `surveyor.py` | `surveyor` | Scan target .NET repo via GitNexus + omo harness |
| `phase1_migrator.py` | `phase1_migrator` | Lift & shift to .NET 10 via omx harness |
| `phase2_modernizer.py` | `phase2_modernizer` | Modernize architecture via omc harness |
| `validator.py` | `validator` | Run `dotnet build && dotnet test` via omo harness; trigger self-healing |
| `documenter.py` | `documenter` | Generate migration documentation |
| `__init__.py` | — | Re-exports all `*_node` functions |

## `app/core/` — Core Infrastructure

| File | Purpose |
|---|---|
| `graph.py` | `build_migration_graph()` and `run_migration()` — LangGraph definition |
| `state.py` | `MigrationState` Pydantic model |
| `config.py` | `Settings` pydantic-settings model, `settings` singleton |
| `persistence.py` | `MigrationPersistence` — SQLite + JSON dual write |
| `ruflo_mcp.py` | `RufloMCPClient` — HTTP client for Ruflo reasoning/routing |
| `auto_skill_creator.py` | `AutoSkillCreator` — generates new SKILL.md on repeated errors |
| `logger.py` | `setup_logging()` — configures loguru output to file |

## `app/integrations/` — MCP Service Adapters

| File | Class | Service |
|---|---|---|
| `gitnexus_adapter.py` | `GitNexusAdapter` | GitNexus Knowledge Graph MCP |
| `vibekanban_adapter.py` | `VibekanbanAdapter` | VibeKanban event board MCP |
| `__init__.py` | — | Re-exports `gitnexus`, `vibekanban` singletons |

## `app/tools/` — Harness Adapter

| File | Purpose |
|---|---|
| `adapter.py` | `call_harness(task_spec)` — subprocess execution of omo/omx/omc commands |

## `app/utils/` — Utilities

| File | Purpose |
|---|---|
| `worktree.py` | `create_worktree()` — git worktree creation for phase isolation |
| `sync_skills.py` | `run()` — copies `.migration-skills/` into target repo's harness dirs |
| `reporter.py` | Migration reporting (likely summary / final report generation) |
| `auto_skill_creator.py` | Duplicate of `app/core/auto_skill_creator.py` (potential redundancy) |

## `.migration-skills/` — Skill Bundles

Pre-built Antigravity/OpenCode/Kiro skill bundles for specific migration tasks:

```
.migration-skills/
├── dotnet-phase1-csproj-upgrade/   # .csproj SDK-style upgrade patterns
├── dotnet-oracle-ef6-migration/    # Oracle EF6 → EF Core migration
├── dotnet-msal-update/             # MSAL auth library update
├── dotnet-clean-arch-cqrs/         # Clean Architecture + CQRS patterns
└── dotnet-ddd-value-objects/       # DDD value object patterns
```

Each skill directory contains at minimum a `SKILL.md` file with frontmatter metadata and implementation guidance.

## Key File Paths

| Path | What It Is |
|---|---|
| `app/core/graph.py` | Central graph definition — start here to understand flow |
| `app/core/state.py` | Data contract shared across all nodes |
| `app/core/config.py` | All configurable values |
| `app/tools/adapter.py` | Bridge to external AI harnesses |
| `config.yaml` | Runtime MCP endpoint config |
| `main.py` | CLI entry point |

## Naming Conventions

- **Agent nodes:** `{name}_node()` function, file `{name}.py` — e.g. `surveyor_node` in `surveyor.py`
- **Adapters:** `{Service}Adapter` class, singleton exported as lowercase name — e.g. `GitNexusAdapter` → `gitnexus`
- **Config:** snake_case Pydantic fields mapping from env vars
- **Skills:** kebab-case directory names — `dotnet-clean-arch-cqrs`

## Generated at Runtime (not in repo)

| Path | Generated By | Contents |
|---|---|---|
| `state/migration.db` | `MigrationPersistence` | SQLite migration history |
| `state/current_state.json` | `MigrationPersistence` | Live JSON state snapshot |
| `.worktrees/` | `create_worktree()` | Isolated git worktrees per phase |
| `{target}/.kiro/skills/` | `sync_skills.py` | Synced skills for Kiro harness |
| `{target}/.opencode/skills/` | `sync_skills.py` | Synced skills for OpenCode |
| `{target}/.omc/skills/` | `sync_skills.py` | Synced skill .md files for omc |
| `{target}/.omx/skills/` | `sync_skills.py` | Synced skill .md files for omx |
