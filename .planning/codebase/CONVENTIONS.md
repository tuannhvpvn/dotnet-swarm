# CONVENTIONS.md — Coding Conventions & Patterns

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

All LangGraph agent nodes follow the same signature:

```python
# app/agents/{name}.py
def {name}_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("{Name}", "🟢 Running", ...)
    console.print("[bold color]...")

    task_spec = {
        "harness": "omo|omx|omc",
        "model": "claude-...",
        "command": "ultrawork|team",
        "task": "...",
        "worktree": state.solution_path | state.git_worktree
    }
    result = call_harness(task_spec)  # Always delegate to harness

    state.phase_progress["..."] = float
    state.completed_tasks.append({...})
    vibekanban.update_agent("{Name}", "✅ Completed", progress=100.0)
    return state
```

Rules:
- Always call `vibekanban.update_agent()` at start and end
- Always use `console.print()` with colored bracket formatting for status
- Always delegate code execution to external harness via `call_harness()`
- Mutate and return the `state` object directly

## HTTP Adapter Pattern

All MCP integrations follow the same pattern:

```python
class ServiceAdapter:
    def __init__(self):
        self.enabled = settings.service_enabled
        self.url = settings.service_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def method(self, ...):
        if not self.enabled:
            return False/None  # Graceful opt-out
        try:
            resp = self.session.post(f"{self.url}/endpoint", json=payload, timeout=N)
            if resp.status_code == 200:
                return resp.json() or True
        except Exception as e:
            console.print(f"[yellow]⚠️ Service fail: {e}[/]")
        return False/None  # Silent failure

service = ServiceAdapter()  # Module-level singleton
```

Key rules:
- Always check `self.enabled` first — all MCP calls can be disabled
- Always catch bare `Exception` on HTTP calls — never crash on integration failure
- Always return safe defaults (`False`, `None`, `"validator"`) on failure
- Timeout values: Ruflo 6–10s, GitNexus 10–30s, VibeKanban 4s

## Error Handling Philosophy

**Swarm-internal errors (Python):** Use loguru `logger.error()` + console rich print, accumulate in `state.error_log`. Do NOT crash.

**Harness errors:** Check `result["returncode"] != 0`, read `result["stderr"]`. Call `ruflo_client.learn_pattern()` to record the failure.

**Integration errors:** Bare `try/except` blocks, graceful degradation. No re-raises.

**Repeated errors (≥3):** `AutoSkillCreator.create_skill()` generates a new SKILL.md — adaptive recovery.

## Console Output Style

Uses `rich.console.Console` exclusively. Color conventions:
- **bold green** — success / completion
- **bold blue** — info / scan
- **bold yellow** — phase 1 migrator
- **bold magenta** — phase 2 modernizer / auto-skill
- **bold cyan** — validator / harness calls
- **yellow** — warnings
- **green with prefix ✅** — operation success
- **yellow with prefix ⚠️** — non-fatal warnings

## Logging

`loguru` used alongside rich console:
- `logger.info()` — general operational messages
- `logger.error()` — errors/failures
- `logger.success()` — completions (green output)
- `logger.debug()` — not currently used
- Log files written to solution directory by `setup_logging()` in `app/core/logger.py`

## Configuration Access

Settings are only accessed via the `settings` singleton from `app/core/config.py`. Never read `config.yaml` directly in business logic (that's `pydantic-settings`'s job via env vars / `.env`).

```python
from app.core.config import settings
url = settings.ruflo_mcp_url  # Always via settings singleton
```

## Import Organization

Imports follow standard Python order: stdlib → third-party → local. Local imports use absolute paths from `app.` root:

```python
from app.core.state import MigrationState
from app.core.config import settings
from app.tools.adapter import call_harness
```

## Pydantic Usage

- `BaseModel` for `MigrationState` (shared state)
- `BaseSettings` + `SettingsConfigDict` for `Settings`
- `.model_dump_json()` and `.model_validate()` (Pydantic v2 API)
- `Field(default_factory=...)` for mutable defaults
