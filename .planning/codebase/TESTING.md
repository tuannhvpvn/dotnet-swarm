# TESTING.md — Test Structure & Practices

## Current State

**No test files are present in the codebase.** There is no `tests/` directory, no `*_test.py` or `test_*.py` files, and no test runner configuration.

## Test Framework (Implied by Stack)

The project uses Python 3.12+. Given the LangGraph/Pydantic stack, the natural test stack would be:

- **pytest** — standard Python test runner
- **pytest-asyncio** — for async LangGraph patterns (if async nodes are added)
- **unittest.mock** — for mocking HTTP calls to Ruflo, GitNexus, VibeKanban
- **pydantic's model validation** — already testable synchronously

## What Needs Tests (Gap Analysis)

### Unit Tests (Pure Python, No External Deps)

| Component | What to Test |
|---|---|
| `app/core/state.py` | `MigrationState` field defaults, phase literal validation, JSON serialization |
| `app/core/config.py` | Settings defaults, env var override |
| `app/tools/adapter.py` | `call_harness()` with mocked `subprocess.run` |
| `app/core/auto_skill_creator.py` | `create_skill()` writes correct SKILL.md content |
| `app/utils/worktree.py` | Worktree path generation, fallback to plain dir |
| `app/utils/sync_skills.py` | Skill copy logic with temp directories |

### Integration Tests (Mock HTTP)

| Component | What to Test |
|---|---|
| `app/core/ruflo_mcp.py` | `learn_pattern`, `get_reasoning`, `route_task` — mock POST responses |
| `app/integrations/gitnexus_adapter.py` | `index_repo`, `query` — mock POST with 200 and failure cases |
| `app/integrations/vibekanban_adapter.py` | `push`, `update_agent` — mock POST and `enabled=False` path |
| `app/core/persistence.py` | SQLite and JSON write/load round-trip using temp directories |

### Graph Tests (LangGraph)

| Component | What to Test |
|---|---|
| `app/core/graph.py` | `build_migration_graph()` — verify node existence, edge structure |
| Agent routing | `supervisor_node` routes correctly to `surveyor`, `phase1_migrator`, `phase2_modernizer` |
| Human gate | `needs_human_approval` triggers END after phase1 hits 100% |

## Mock Patterns (Recommended)

```python
# Mocking harness subprocess
from unittest.mock import patch, MagicMock

@patch("app.tools.adapter.subprocess.run")
def test_call_harness_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
    result = call_harness({"harness": "omo", "model": "claude-4.6-sonnet", ...})
    assert result["returncode"] == 0

# Mocking HTTP integration
@patch("app.integrations.gitnexus_adapter.requests.Session.post")
def test_gitnexus_index_success(mock_post):
    mock_post.return_value = MagicMock(status_code=200)
    assert gitnexus.index_repo("/some/path") == True
```

## CI/CD

No CI pipeline configured (`no .github/`, `.gitlab-ci.yml`, or similar).

## Recommended Next Steps for Testing

1. Add `pytest` and `pytest-cov` to `pyproject.toml` dev dependencies
2. Create `tests/unit/` and `tests/integration/` directories
3. Use `tmp_path` pytest fixture for all filesystem tests
4. Mock all HTTP calls — never call real Ruflo/GitNexus/VibeKanban in tests
5. Mock all subprocess calls — never run real harnesses in tests
