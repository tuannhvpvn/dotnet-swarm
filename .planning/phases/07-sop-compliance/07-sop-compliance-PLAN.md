---
wave: 1
depends_on: []
files_modified: [
    "app/core/state.py",
    "app/core/sop.py",
    "app/utils/reporter.py"
]
autonomous: true
gap_closure: false
requirements_addressed: [SOP-01, SOP-02, SOP-03]
---

# Phase 7: SOP Compliance Blueprint

<objective>
Encode SOP rules as hard algorithmic checks in Python. `SOPEnforcer` blocks phase/task progression on any failed check (D-01). `reporter.py` serializes `MigrationState` directly with no LLM inference (D-02). `TaskItem` is extended with 4 new fields to make pre-task checks non-vacuous (D-03).
</objective>

<tasks>

<task>
  <id>sop-01-extend-taskitem</id>
  <title>Extend `TaskItem` in `state.py`</title>
  <read_first>
    <file>app/core/state.py</file>
  </read_first>
  <action>
Add 4 fields to the `TaskItem` class with safe defaults that do not break existing code:

```python
source_files: list[str] = Field(default_factory=list)
target_files: list[str] = Field(default_factory=list)
done_criteria: str | None = None
verify_command: str | None = None
```

These fields power the `SOPEnforcer.pre_task_check()` non-vacuous checks (WLNK constraint from D-03).
  </action>
  <acceptance_criteria>
    <check>python -m py_compile app/core/state.py</check>
    <check>All 4 new fields present with correct types and defaults</check>
  </acceptance_criteria>
</task>

<task>
  <id>sop-02-enforcer</id>
  <title>Create `app/core/sop.py` — SOPEnforcer</title>
  <read_first>
    <file>app/core/state.py</file>
    <file>app/core/safety.py</file>
  </read_first>
  <action>
Create new file `app/core/sop.py`. Important implementation notes:

1. **`SOPResult` dataclass**: holds `checks: list[tuple[str, bool]]`, a computed property `passed: bool = all(v for _, v in checks)`, and a `failed_checks: list[str]` property listing names of False checks.

2. **`SOPEnforcer` class** with 4 static methods (no `self`):
   - `pre_phase_check(state: MigrationState) -> SOPResult` — checks `goal_defined`, `scope_locked`, `worktree_set`
   - `pre_task_check(task: TaskItem) -> SOPResult` — checks `task_small_enough` (`len(task.source_files) <= 5`), `single_deliverable`, `input_clear`, `output_clear`, `verify_step_defined`, `timeout_set`
   - `post_task_check(task: TaskItem, worktree: str) -> SOPResult` — checks `scope_correct` (verify only expected files changed via git diff), `no_contract_violation` (use `safety.scan_worktree(worktree)` — returns `list[SafetyResult]`, so `is_clean = len(violations) == 0`), `no_side_effects`
   - `done_criteria_check(state: MigrationState) -> SOPResult` — checks `implementation_done`, `validation_pass`, `debt_recorded`, `report_generated`

3. **IMPORTANT** — `safety.scan_worktree()` returns `list[SafetyResult]` not a single object. Use `len(safety_rules.scan_worktree(worktree)) == 0` to get the clean status. Instantiate `SafetyRules` locally if config is available, else default to `True` on import error.

4. **Hard-block integration point**: When `SOPEnforcer.pre_task_check()` returns `result.passed == False`, callers in `worker.py` must set `state.workflow_state = "blocked"` and `state.blocked_reason = str(result.failed_checks)`.

5. **Helper functions** `verify_only_expected_files_changed(task, worktree)` and `verify_no_extra_changes(task, worktree)` — implement using `git diff --name-only HEAD` in the worktree directory and cross-referencing with `task.target_files`. Return `True` on subprocess failure (fail-open for CI environments without git).
  </action>
  <acceptance_criteria>
    <check>python -m py_compile app/core/sop.py</check>
    <check>`SOPResult.passed` is False when any check is False</check>
    <check>`scan_worktree` list length used correctly (not `.is_clean` attribute)</check>
  </acceptance_criteria>
</task>

<task>
  <id>sop-03-reporter</id>
  <title>Create `app/utils/reporter.py` — State-Direct Reporter</title>
  <read_first>
    <file>app/core/state.py</file>
  </read_first>
  <action>
Create new file `app/utils/reporter.py`. All report generation reads directly from `MigrationState` fields. No LLM calls. No string inference.

Implement a single `MigrationReporter` class with these methods, all accepting `state: MigrationState`:

1. `phase_summary(state) -> str` — Markdown. Sections: Tasks Executed (list), Passed (completed), Failed (failed + error details from `state.build_errors`), Fixes Applied (`state.fix_attempts`), Debt (`state.debt`).

2. `task_detail_yaml(state) -> str` — YAML. Serialize `state.tasks` using `[t.model_dump() for t in state.tasks]` → `yaml.dump()`.

3. `error_fix_log(state) -> str` — Markdown. Table of `state.build_errors` with columns: `error_code`, `file_path`, `line_number`, `message`.

4. `debt_register_yaml(state) -> str` — YAML. Serialize `state.debt` using `[d.model_dump() for d in state.debt]` → `yaml.dump()`.

5. `pr_description(state) -> str` — Markdown. Sections: Migration ID, Solution Path, Tasks Completed count, Build Errors count, Debt Items count, Patterns Learned count (from `state.learned_patterns`).

6. `evolution_report(state) -> str` — Markdown. Table of `state.learned_patterns` (key → value).

7. `generate_all(state) -> dict[str, str]` — Calls all above methods, returns dict keyed by report name. Also appends each report name to `state.reports` (the field that `done_criteria_check` reads).

**No hallucination rule**: Every value in reports MUST come from a `state.*` field. Do NOT write strings like "migration appears complete" or "likely succeeded".
  </action>
  <acceptance_criteria>
    <check>python -m py_compile app/utils/reporter.py</check>
    <check>All 7 report types implemented with state-sourced data only</check>
  </acceptance_criteria>
</task>

</tasks>

<verification>
## Verification
1. `python -m py_compile app/core/state.py app/core/sop.py app/utils/reporter.py`
2. Smoke test SOPEnforcer with a minimal state:
   ```python
   python -c "
   from app.core.sop import SOPEnforcer
   from app.core.state import MigrationState, TaskItem
   state = MigrationState(migration_id='test', solution_path='/tmp')
   result = SOPEnforcer.pre_phase_check(state)
   print('passed:', result.passed, 'failed:', result.failed_checks)
   "
   ```
3. Smoke test reporter:
   ```python
   python -c "
   from app.core.state import MigrationState
   from app.utils.reporter import MigrationReporter
   state = MigrationState(migration_id='test', solution_path='/tmp')
   r = MigrationReporter()
   print(r.phase_summary(state)[:200])
   "
   ```
</verification>

<must_haves>
- `SOPResult.passed` correctly computes `all(v for _, v in checks)`.
- `safety.scan_worktree()` return value treated as `list` not object with `.is_clean`.
- Reporter never writes inferred text — all values from `state.*` fields.
- `TaskItem` extended non-destructively with safe defaults.
</must_haves>
