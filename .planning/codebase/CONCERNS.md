# CONCERNS.md — Technical Debt & Risks

## Critical Issues

### No Tests
**Severity: High**
Zero test coverage. No `tests/` directory, no pytest, no mocks. Entire swarm (graph routing, harness calls, state mutations, MCP adapters) runs with no automated validation.

**Risk:** Regressions go undetected. Workflow failures surface at runtime against real .NET codebases.

### External Harnesses Are Undocumented Black Boxes
**Severity: High**
All actual migration work is delegated to `omo`, `omx`, `omc` via subprocess. These harnesses are:
- Not included in the repository
- Not documented anywhere in the codebase
- Assumed to be pre-installed on `$PATH`
- Called with a `--task`, `--model`, `--work-dir` CLI API that may not be stable

**Risk:** Harness availability or API changes break the swarm silently (returncode -1, no meaningful error).

### Duplicate `auto_skill_creator.py`
**Severity: Medium**
`app/core/auto_skill_creator.py` and `app/utils/auto_skill_creator.py` appear to be identical files. `validator.py` imports from `app.core`, while `sync_skills.py` (inside utils) calls the utils version.

**Files:** `app/core/auto_skill_creator.py`, `app/utils/auto_skill_creator.py`

**Risk:** Divergence between copies, confusion about which is authoritative.

---

## Architecture Concerns

### Mutable Pydantic State Anti-Pattern
**Severity: Medium**
`MigrationState` is a `BaseModel`, but all nodes mutate it in place (`state.phase_progress["survey"] = 100.0`) and then return the state object. Pydantic v2 models are not designed as mutable shared state objects. LangGraph TypedDict-based state is the recommended pattern.

**File:** `app/core/state.py`, all `app/agents/*.py`

### Bare `except` Blocks Hide Real Errors
**Severity: Medium**
Multiple integration adapters use bare `except:` (not even `except Exception:`) which swallows all exceptions including `KeyboardInterrupt`, `SystemExit`, and `MemoryError`.

```python
# app/integrations/gitnexus_adapter.py:43
except:
    return None
```

**Risk:** Debugging failures is extremely difficult; critical signals are silently lost.

### Human Gate Uses Blocking `input()`
**Severity: Medium**
The human approval gate in `run_migration()` calls `input("Approve Phase 2? (y/n): ")` which blocks the process. This is incompatible with automated orchestration, CI pipelines, or any non-interactive context.

**File:** `app/core/graph.py` line 67

### LangGraph Graph Construction Creates New MemorySaver Each Run
**Severity: Low-Medium**
`build_migration_graph()` creates a new `MemorySaver()` on each call. There is no persistent thread_id passed to `graph.stream()`, so LangGraph checkpointing does not enable true resume from checkpoint.

**File:** `app/core/graph.py`

---

## Operational Concerns

### Five Local Services Must Be Running
To function, the swarm requires 4 local MCP services to be up: Ruflo (`:3131`), GitNexus (`:4000`), VibeKanban (`:3000`), plus the harness CLI tools. No health checks or startup validation. Missing services produce silent failures only.

### No Retry Logic Despite `tenacity` in Dependencies
`tenacity` is declared as a dependency in `pyproject.toml` but appears nowhere in the actual code. All HTTP calls have single-shot requests with no retry.

### Timeout Values May Be Too Low
GitNexus index: 30s. Ruflo reasoning: 10s. VibeKanban push: 4s. For large .NET solution indexing, 30s may be insufficient.

### Vietnamese Output Makes Logs Hard to Parse in International Context
All user-facing strings mix Vietnamese and English. Log files (loguru) and VibeKanban payloads mix languages.

---

## Security Concerns

### No Secret Management
Config loaded from `.env` and `config.yaml`. No `.env.example` template, no vault integration. AI harness model names (`claude-4.6-sonnet`, `claude-4.6-opus`, `glm-5`) with API keys presumably managed by the harness tools, not audited here.

### SQLite DB Written to Target Repo Directory
`{solution_path}/state/migration.db` is written inside the target .NET repo's directory tree, which could accidentally be committed to that repo's git history.

### Git Worktrees Left in Target Repo
`.worktrees/` directories are created inside the target solution path and are never cleaned up automatically.

---

## Missing Features (Implied by Implementation Plan)

Based on `IMPLEMENTATION-PLAN-v2.md`:
- Phase 2 modernization (Clean Arch + CQRS) is scaffolded but the `omc` harness may not have the skills deployed yet
- Auto-skill creation (`auto_skill_creator`) generates skills but doesn't verify whether they improve outcomes
- GitNexus query results are not actually used in the survey analysis — the surveyor node calls `index_repo` but passes a fixed task string to the harness instead of injecting graph query results
