# ARCHITECTURE.md — System Architecture

## Pattern: Queen-Led Agent Swarm (LangGraph + MCP)

This project implements a **Queen-led autonomous agent swarm** pattern for automating .NET codebase migration. The Queen Supervisor node acts as the central router, delegating work to specialist worker nodes. Each worker node calls an external AI harness (`omo`/`omx`/`omc`) via subprocess for actual .NET code transformation.

## The Two Migration Phases

The swarm performs migration in two distinct phases with a **human-in-the-loop gate** between them:

| Phase | Goal | Harness | Model |
|---|---|---|---|
| Phase 1 — Lift & Shift | Upgrade `.csproj`, packages, and syntax to .NET 10 without architectural changes | `omx` | `claude-4.6-sonnet` |
| Phase 2 — Modernize | Refactor to Clean Architecture + DDD + CQRS + TDD + Dapper/EF Core | `omc` | `claude-4.6-opus` |

## Graph Architecture

```
START
  │
  ▼
supervisor (Queen via Ruflo routing)
  │
  ├──[survey]──► surveyor ──────────────────┐
  ├──[phase1]──► phase1_migrator ────────────┤
  └──[phase2]──► phase2_modernizer ──────────┤
                                             ▼
                                          validator (build + test)
                                             │
                                          documenter
                                             │
                                          supervisor ◄─── (loop back)
                                             │
                                    [phase1 done 100%]
                                             │
                                           END (human gate → approve → phase2)
```

**Graph construction:** `app/core/graph.py` — `build_migration_graph()`
**Graph execution:** `run_migration()` streams events and handles human approval interactively

## State Model

All nodes share a single Pydantic `MigrationState` object (never split across nodes):

```python
# app/core/state.py
class MigrationState(BaseModel):
    migration_id: str          # Unique run ID
    solution_path: str         # Target .NET repo path
    current_phase: Literal["survey", "phase1", "phase2", "complete"]

    phase_progress: Dict[str, float]    # 0–100 per phase
    completed_tasks: List[Dict]
    failed_tasks: List[Dict]
    error_log: List[Dict]               # Accumulated errors
    learned_patterns: Dict[str, str]    # Ruflo-learned fixes

    needs_human_approval: bool          # Human gate flag
    git_worktree: str | None            # Active isolated worktree path
    last_updated: datetime
```

## AI Harness Delegation Layer

All actual .NET code transformation is **delegated outside** the Python process:

```python
# app/tools/adapter.py
call_harness({
    "harness": "omx",
    "model": "claude-4.6-sonnet",
    "command": "team",
    "task": "Lift-and-shift to .NET 10",
    "worktree": "/path/to/worktree"
})
```

This runs `omx team --model claude-4.6-sonnet --task "..." --work-dir ./worktree` as a subprocess with a 300s timeout.

## Self-Healing & Auto-Skill Loop

```
Validator detects build failure
        │
        ▼
Ruflo learns pattern (POST /learn)
        │
        ▼
If error count ≥ 3 → AutoSkillCreator generates new SKILL.md
        │
        ▼
sync_skills copies new skill to target repo's harness directories
```

**Files:** `app/core/auto_skill_creator.py`, `app/utils/sync_skills.py`

## Worktree Isolation

Each migration phase creates an isolated git worktree of the target .NET repo, preventing Phase 1 and Phase 2 changes from mixing:
- `app/utils/worktree.py` — `create_worktree(solution_path, prefix)`
- Creates: `{solution_path}/.worktrees/{prefix}-{timestamp}/`
- Falls back to plain directory if git fails

## Persistence Architecture

Dual-write pattern: every `supervisor_node` and `run_migration` completion saves state to both:
1. **SQLite** (`{solution_path}/state/migration.db`) — queryable history
2. **JSON** (`{solution_path}/state/current_state.json`) — polled by Streamlit dashboard

## Observability Architecture

Three observability channels run in parallel during migration:
1. **Rich console** — colored terminal output per agent
2. **Loguru file logs** — structured logs written to solution directory
3. **VibeKanban push** — real-time event stream to VibeKanban MCP (kanban board)
4. **Streamlit dashboard** — reads JSON state, refreshes every 2 seconds
