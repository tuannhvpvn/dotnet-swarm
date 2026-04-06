---
wave: 1
depends_on: []
files_modified: ["app/core/state.py", "app/core/persistence.py", "app/utils/auto_skill_creator.py", "app/utils/__init__.py"]
autonomous: true
requirements_addressed: [FND-01, FND-02, FND-03]
---

# Phase 1: Foundation Plan

<objective>
Redesign `MigrationState` tracking fields, upgrade persistence schema to match, and definitively consolidate `auto_skill_creator.py` to prevent logic duplication.
</objective>

<tasks>

<task>
  <id>fnd-01-state-redesign</id>
  <title>Redesign MigrationState in app/core/state.py</title>
  <read_first>
    <file>app/core/state.py</file>
    <file>IMPLEMENTATION-PLAN-v2.md</file>
  </read_first>
  <action>
Modify `MigrationState` in `app/core/state.py` to include the robust v2 fields:
- Add `inventory: dict | None`
- Add `plan: dict | None`
- Add `tasks: list[TaskItem]`
- Add `current_task_id: str | None`
- Add `current_tier: int = 0`
- Add `build_errors: list[BuildError]`
- Add `fix_attempts: int = 0`
- Add `max_fix_attempts: int = 5`
- Add `debt: list[DebtItem]`
- Add `blocked_reason: str | None`
- Add `workflow_state: Literal["normal", "blocked", "remediation"]`
- Add `human_decision: Literal["pending", "approve", "modify", "reject"] | None`
- Add `reports: list[str]`
- Add `safety_violations: list[dict]`
- Add `worktree_path: str | None`
- Add `session_id: str`
Remove obsolete fields: `phase_progress`, `completed_tasks`, `failed_tasks`.
Define Pydantic sub-models exactly as described in IMPLEMENTATION-PLAN-v2.md (Task 0.1): `TaskItem`, `BuildError`, `DebtItem`.
  </action>
  <acceptance_criteria>
    <check>grep -q "class TaskItem(BaseModel):" app/core/state.py</check>
    <check>grep -q "class BuildError(BaseModel):" app/core/state.py</check>
    <check>grep -q "class DebtItem(BaseModel):" app/core/state.py</check>
    <check>grep -q "class MigrationState(BaseModel):" app/core/state.py</check>
    <check>! grep -q "phase_progress:" app/core/state.py</check>
    <check>python -m py_compile app/core/state.py exits 0</check>
  </acceptance_criteria>
</task>

<task>
  <id>fnd-02-persistence-upgrade</id>
  <title>Upgrade Persistence Schema in app/core/persistence.py</title>
  <read_first>
    <file>app/core/persistence.py</file>
    <file>app/core/state.py</file>
  </read_first>
  <action>
Modify `app/core/persistence.py` to handle the new state sub-entities:
1. Update schema initialization in `ensure_schema()` (or its equivalent) to create tables:
   - `tasks`
   - `error_log`
   - `knowledge_patterns`
   - `agent_log`
2. Update `save()` to serialize the full `MigrationState` properly (inserting into `tasks` table instead of relying only on a monolithic state JSON).
3. Update `load()` to deserialize the new relational structure back into the complete `MigrationState` model.
  </action>
  <acceptance_criteria>
    <check>grep -q "CREATE TABLE IF NOT EXISTS tasks" app/core/persistence.py</check>
    <check>grep -q "CREATE TABLE IF NOT EXISTS error_log" app/core/persistence.py</check>
    <check>grep -q "CREATE TABLE IF NOT EXISTS knowledge_patterns" app/core/persistence.py</check>
    <check>grep -q "CREATE TABLE IF NOT EXISTS agent_log" app/core/persistence.py</check>
    <check>python -m py_compile app/core/persistence.py exits 0</check>
  </acceptance_criteria>
</task>

<task>
  <id>fnd-03-consolidate-skill-creator</id>
  <title>Deduplicate auto_skill_creator.py</title>
  <read_first>
    <file>app/utils/__init__.py</file>
  </read_first>
  <action>
1. Delete `app/utils/auto_skill_creator.py` entirely.
2. Update `app/utils/__init__.py` to replace local module exposure `from app.utils.auto_skill_creator import ...` to redirect gracefully or directly `from app.core import auto_skill_creator`. The file `app/core/auto_skill_creator.py` is the retained copy.
3. Use `rgrep "app.utils.auto_skill_creator" app/` to fix any other dependent references across files to point to `app.core.auto_skill_creator`.
  </action>
  <acceptance_criteria>
    <check>test ! -f app/utils/auto_skill_creator.py</check>
    <check>! grep -q "app.utils.auto_skill_creator" app/utils/__init__.py</check>
    <check>python -c "from app.utils import auto_skill_creator" exits 0 OR python -c "from app.core import auto_skill_creator" acts as the new direct reference.</check>
  </acceptance_criteria>
</task>

</tasks>

<verification>
## Verification
1. Run `python -c "from app.core.state import MigrationState"`. Must succeed.
2. Run `python -c "from app.core.auto_skill_creator import create_skill"`. Must succeed.
3. Validate persistence with `python -c "from app.core.persistence import load; load()"` (or equivalent simple test).
</verification>

<must_haves>
- State schema exactly matches the requested structure with no stray legacy fields.
- `app/utils/auto_skill_creator.py` is fully removed.
- Valid `tasks` and `error_log` tables exist in SQLite definitions.
</must_haves>
