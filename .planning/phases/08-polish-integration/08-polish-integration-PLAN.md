---
wave: 1
depends_on: []
files_modified: [
    "main.py",
    "dashboard.py",
    "config.yaml",
    ".gitignore",
    "tests/test_state.py",
    "tests/test_safety.py",
    "tests/test_sop.py",
    "tests/test_graph.py",
    "tests/test_adapter_mock.py",
    "tests/test_persistence.py",
    "tests/test_planner.py",
    "tests/test_skills_sync.py",
    "tests/fixtures/sample_state.json",
    "tests/fixtures/sample_inventory.yaml",
    "docs/ARCHITECTURE.md",
    "docs/SOP.md"
]
autonomous: true
gap_closure: false
requirements_addressed: [POL-01, POL-02, POL-03, POL-04, POL-05, POL-06]
---

# Phase 8: Polish & Integration Blueprint

<objective>
Ship the final v1.0-ready state: an enhanced Typer CLI, a live-accurate Streamlit dashboard, unified config.yaml, 8 integration test files, and core documentation.
</objective>

<tasks>

<task>
  <id>pol-01-cli</id>
  <title>Extend `main.py` CLI with resume, status, approve commands</title>
  <read_first>
    <file>main.py</file>
    <file>app/core/persistence.py</file>
    <file>app/core/config.py</file>
  </read_first>
  <action>
Keep the existing `start` command intact. Add three new Typer commands:

```python
@app.command()
def resume(solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET")):
    """Khôi phục migration đang dở từ state được lưu."""
    solution_path = Path(solution_path).resolve()
    setup_logging(str(solution_path))
    persistence = MigrationPersistence(str(solution_path))
    # Find latest migration_id from DB (use settings.migration_id or last saved)
    state = persistence.load(settings.migration_id)
    if not state:
        console.print("[bold red]❌ Không tìm thấy state đã lưu.[/]")
        raise typer.Exit(1)
    console.print(f"[bold green]✅ Khôi phục migration: {state.migration_id}[/]")
    run_migration(str(solution_path), start_phase=1, persistence=persistence)

@app.command()
def status(solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET")):
    """Hiển thị trạng thái migration hiện tại."""
    json_path = Path(solution_path) / "state" / "current_state.json"
    if not json_path.exists():
        console.print("[yellow]⚠️ Chưa có state. Chạy lệnh start trước.[/]")
        raise typer.Exit(1)
    state_dict = json.loads(json_path.read_text(encoding="utf-8"))
    tasks = state_dict.get("tasks", [])
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    console.print(f"[bold cyan]Migration:[/] {state_dict.get('migration_id', 'N/A')}")
    console.print(f"[bold cyan]Phase:[/] {state_dict.get('current_phase', 'N/A')}")
    console.print(f"[bold cyan]Tasks:[/] {completed}/{len(tasks)} completed")
    console.print(f"[bold cyan]Workflow:[/] {state_dict.get('workflow_state', 'normal')}")
    if state_dict.get("blocked_reason"):
        console.print(f"[bold red]Blocked:[/] {state_dict.get('blocked_reason')}")

@app.command()
def approve(
    solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET"),
    decision: str = typer.Option("approve", help="approve|modify|reject")
):
    """Ghi human gate decision vào state và tiếp tục."""
    json_path = Path(solution_path) / "state" / "current_state.json"
    if not json_path.exists():
        console.print("[bold red]❌ Không tìm thấy state.[/]")
        raise typer.Exit(1)
    state_dict = json.loads(json_path.read_text(encoding="utf-8"))
    state_dict["human_decision"] = decision
    state_dict["workflow_state"] = "normal"
    state_dict["blocked_reason"] = None
    json_path.write_text(json.dumps(state_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"[bold green]✅ Decision recorded: {decision}[/]")
```

Add `import json` to the top of `main.py` if not already present.
  </action>
  <acceptance_criteria>
    <check>python -m py_compile main.py</check>
    <check>python main.py --help shows all 4 commands</check>
  </acceptance_criteria>
</task>

<task>
  <id>pol-02-dashboard</id>
  <title>Update `dashboard.py` to display task-level metrics</title>
  <read_first>
    <file>dashboard.py</file>
    <file>app/core/state.py</file>
  </read_first>
  <action>
Rewrite `dashboard.py` with the same polling loop but updated to use new `MigrationState` field schema. Keep `state/current_state.json` as input source (D-02: no internal imports).

Display sections:
1. **Header metrics row** — Migration ID, Current Phase, Workflow State (normal/blocked/remediation), Human Gate status.
2. **Task Progress table** — for each task in `state.tasks`: show ID, title, status with icon (`completed=✅`, `failed=❌`, `in_progress=🔄`, `pending=⏳`, `blocked=⛔`).
3. **Build Errors** — table of `build_errors` list with `error_code`, `file_path`, `message`. If empty: "✅ No errors."
4. **Debt Register** — list of `debt` items with resolved status. If empty: "✅ No debt."
5. **Safety Violations** — list from `safety_violations`. If empty: "✅ Clean."
6. **SONA Patterns** — `learned_patterns` dict as key → value expansions (keep existing section).
7. **Fix Attempts** — `fix_attempts` counter metric.

Remove the hardcoded agent name loop (`for agent in agents`) — replace with real task data.
  </action>
  <acceptance_criteria>
    <check>python -c "import ast; ast.parse(open('dashboard.py').read()); print('✅ parse OK')"</check>
  </acceptance_criteria>
</task>

<task>
  <id>pol-03-config</id>
  <title>Update `config.yaml` with full unified schema</title>
  <read_first>
    <file>config.yaml</file>
  </read_first>
  <action>
Update `config.yaml` to match the full spec (Task 7.3 from IMPLEMENTATION-PLAN-v2.md). The file must include all top-level sections:
- `migration` (id, target_framework, strategy, nullable, implicit_usings)
- `safety` (config_file)
- `tools` (config_file)
- `vibekanban` (enabled, url)
- `ruflo` (enabled, mcp_url, fallback_to_static)
- `gitnexus` (enabled, mcp_url, index_on_start)
- `git` (branch_format, commit_format, use_worktree, auto_push, create_pr, pr_target_branch)
- `session` (auto_save_interval, resume_on_start)
- `logging` (level, rotation, retention)

Preserve any existing values (especially MCPs URLs) — only add missing sections.
  </action>
  <acceptance_criteria>
    <check>python -c "import yaml; yaml.safe_load(open('config.yaml')); print('✅ YAML valid')"</check>
  </acceptance_criteria>
</task>

<task>
  <id>pol-04-gitignore</id>
  <title>Update `.gitignore`</title>
  <read_first>
    <file>.gitignore</file>
  </read_first>
  <action>
Append the following entries to `.gitignore` if not already present:
```
state/
.worktrees/
*.db
*.db-journal
*.db-wal
__pycache__/
.env
```
  </action>
  <acceptance_criteria>
    <check>grep -q "state/" .gitignore && echo "✅ OK"</check>
  </acceptance_criteria>
</task>

<task>
  <id>pol-05-tests</id>
  <title>Create integration test suite under `tests/`</title>
  <read_first>
    <file>app/core/state.py</file>
    <file>app/core/sop.py</file>
    <file>app/core/safety.py</file>
    <file>app/core/persistence.py</file>
    <file>app/agents/planner.py</file>
    <file>app/utils/sync_skills.py</file>
  </read_first>
  <action>
Create `tests/` directory and all test files. Use `pytest` style (no class required). Follow D-01: core paths use real objects, MCPs use mocks.

**`tests/__init__.py`** — empty file.

**`tests/fixtures/sample_state.json`** — minimal valid `MigrationState` JSON:
```json
{"migration_id": "test-fixture", "solution_path": "/tmp/test-app", "current_phase": "survey", "tasks": [], "build_errors": [], "debt": [], "reports": [], "safety_violations": [], "fix_attempts": 0, "max_fix_attempts": 5, "workflow_state": "normal", "human_decision": null, "blocked_reason": null, "worktree_path": null, "session_id": "", "inventory": null, "plan": null, "current_task_id": null, "current_tier": 0, "error_log": [], "learned_patterns": {}, "last_updated": "2026-04-06T00:00:00"}
```

**`tests/fixtures/sample_inventory.yaml`** — minimal inventory:
```yaml
projects:
  - name: "TestApp"
    path: "TestApp/TestApp.csproj"
    framework: "net48"
```

**`tests/test_state.py`** — test `MigrationState` and `TaskItem`:
- `test_state_creation` — construct with required fields, check defaults.
- `test_taskitem_sop_fields` — verify all 4 SOP fields exist with correct defaults.
- `test_state_model_dump_json` — `model_dump_json()` round-trip via `model_validate`.

**`tests/test_safety.py`** — test `SafetyRules` with real config:
- `test_check_file_path_clean` — clean path returns `safe=True`.
- `test_check_blacklisted_folder` — `keys/secret.pem` returns `safe=False`.
- `test_check_sql_forbidden` — SQL with `DROP TABLE` returns `safe=False`.
- `test_check_sql_clean` — `SELECT *` returns `safe=True`.

**`tests/test_sop.py`** — test `SOPEnforcer`:
- `test_pre_phase_fail_empty` — empty `MigrationState` fails `pre_phase_check`.
- `test_pre_task_fail_empty` — empty `TaskItem` fails `pre_task_check`.
- `test_pre_task_pass_full` — fully populated `TaskItem` passes `pre_task_check`.
- `test_done_criteria_fail_no_reports` — state with no reports fails `done_criteria_check`.
- `test_sop_result_passed_property` — verify `SOPResult.passed` logic.

**`tests/test_persistence.py`** — real SQLite round-trip:
- `test_save_and_load` — save a `MigrationState`, load it back, assert `migration_id` matches. Use `tmp_path` pytest fixture for temp dir.

**`tests/test_graph.py`** — graph compilation (skip if langgraph deps not installed):
- `test_build_graph_compiles` — call `build_migration_graph()` inside a `try/except ImportError` and assert it returns a non-None object.

**`tests/test_adapter_mock.py`** — adapters with mocked HTTP:
- Use `unittest.mock.patch` to mock `requests.post` and `requests.get`.
- `test_vibekanban_update_agent_disabled` — with `enabled=False`, method returns silently.
- `test_gitnexus_index_repo_disabled` — with `enabled=False`, method returns silently.

**`tests/test_planner.py`** — planner with minimal state:
- `test_planner_node_returns_state` — call `planner_node(state)` with a minimal state object that has `inventory` set to `{"projects": []}`, assert returned state is a dict or `MigrationState`.

**`tests/test_skills_sync.py`** — skills sync:
- `test_skills_list_has_13_entries` — import `SKILLS` from `app.utils.sync_skills` and assert `len(SKILLS) == 13`.
  </action>
  <acceptance_criteria>
    <check>python -m pytest tests/ -v --tb=short 2>&1 | tail -20</check>
  </acceptance_criteria>
</task>

<task>
  <id>pol-06-docs</id>
  <title>Create core documentation files</title>
  <action>
Create `docs/` directory with two files:

**`docs/SOP.md`** — embed the SOP operational summary as a structured Markdown document covering:
- Section A: Pre-Phase Checks (3 gates from SOPEnforcer)
- Section B: Pre-Task Checks (6 gates from SOPEnforcer)
- Section E: Post-Task Checks (3 gates)
- Section I: Done-Criteria Checks (4 gates)
- Human Gate definition (when `workflow_state == "blocked"`)

**`docs/ARCHITECTURE.md`** — updated architecture summary including:
- Current graph topology (planner → worker → validator → documenter → human_gate)
- Dual-write persistence strategy (SQLite + JSON)
- SOPEnforcer gate integration points
- Ruflo MCP integration with fallback telemetry
- Migration skills payload (13 skills)
  </action>
  <acceptance_criteria>
    <check>test -f docs/SOP.md && test -f docs/ARCHITECTURE.md && echo "✅ docs exist"</check>
  </acceptance_criteria>
</task>

</tasks>

<verification>
## Verification
```bash
python -m py_compile main.py
python main.py --help
python -c "import ast; ast.parse(open('dashboard.py').read()); print('✅ dashboard OK')"
python -c "import yaml; yaml.safe_load(open('config.yaml')); print('✅ config OK')"
grep -q "state/" .gitignore && echo "✅ gitignore OK"
python -m pytest tests/ -v --tb=short
test -f docs/SOP.md && test -f docs/ARCHITECTURE.md && echo "✅ docs OK"
```
</verification>

<must_haves>
- D-01: `test_graph.py` and `test_persistence.py` use real objects, no mocks.
- D-02: `dashboard.py` reads ONLY from `state/current_state.json`, no internal imports.
- `tests/test_skills_sync.py` asserts `len(SKILLS) == 13`.
- All 4 CLI commands documented in `python main.py --help`.
</must_haves>
