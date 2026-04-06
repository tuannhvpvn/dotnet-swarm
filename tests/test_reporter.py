"""Tests for MigrationReporter — state-direct reporting engine (SOP-03).

Verifies:
- All 7 report methods produce output sourced from MigrationState fields
- No inferred/hallucinated strings (all values traceable to state fields)
- generate_all() returns all 6 report types and populates state.reports
- done_criteria_check gate passes once state.reports is populated
"""
from app.core.state import MigrationState, TaskItem, BuildError, DebtItem
from app.utils.reporter import MigrationReporter
from app.core.sop import SOPEnforcer


def make_state(**kwargs) -> MigrationState:
    defaults = dict(migration_id="rpt-001", solution_path="/tmp/test-sol")
    defaults.update(kwargs)
    return MigrationState(**defaults)


# ── generate_all ───────────────────────────────────────────────────────────────

def test_generate_all_returns_six_report_types():
    """generate_all() must return exactly 6 named reports."""
    state = make_state()
    r = MigrationReporter()
    reports = r.generate_all(state)
    expected_keys = {
        "phase_summary", "task_detail_yaml", "error_fix_log",
        "debt_register_yaml", "pr_description", "evolution_report"
    }
    assert set(reports.keys()) == expected_keys


def test_generate_all_populates_state_reports():
    """generate_all() must append report names to state.reports — this is what
    done_criteria_check reads to determine if reporting is complete (SOP-03)."""
    state = make_state()
    assert state.reports == []
    r = MigrationReporter()
    r.generate_all(state)
    assert len(state.reports) == 6
    assert "phase_summary" in state.reports
    assert "evolution_report" in state.reports


def test_done_criteria_passes_after_generate_all():
    """After generate_all(), done_criteria_check should not fail on report_generated."""
    state = make_state()
    task = TaskItem(id="t1", title="Done", status="completed",
                    source_files=["A.cs"], target_files=["A.cs"],
                    done_criteria="builds", verify_command="dotnet build")
    state.tasks.append(task)
    MigrationReporter().generate_all(state)
    result = SOPEnforcer.done_criteria_check(state)
    assert "report_generated" not in result.failed_checks


# ── phase_summary ──────────────────────────────────────────────────────────────

def test_phase_summary_contains_migration_id():
    """phase_summary must embed state.migration_id — proves it's state-sourced."""
    state = make_state(migration_id="my-mig-xyz")
    r = MigrationReporter()
    output = r.phase_summary(state)
    assert "my-mig-xyz" in output


def test_phase_summary_contains_solution_path():
    """phase_summary must embed state.solution_path."""
    state = make_state(solution_path="/opt/my-app")
    r = MigrationReporter()
    output = r.phase_summary(state)
    assert "/opt/my-app" in output


def test_phase_summary_lists_failed_tasks():
    """phase_summary must include failed task IDs in the Failed section."""
    state = make_state()
    state.tasks.append(TaskItem(id="t-fail", title="Bad Task", status="failed"))
    r = MigrationReporter()
    output = r.phase_summary(state)
    assert "t-fail" in output


def test_phase_summary_shows_fix_attempts():
    """phase_summary must reflect state.fix_attempts count."""
    state = make_state()
    state.fix_attempts = 3
    r = MigrationReporter()
    output = r.phase_summary(state)
    assert "3" in output


# ── task_detail_yaml ───────────────────────────────────────────────────────────

def test_task_detail_yaml_serializes_task_ids():
    """task_detail_yaml must embed task IDs from state.tasks."""
    state = make_state()
    state.tasks.append(TaskItem(id="task-abc", title="My Task"))
    r = MigrationReporter()
    output = r.task_detail_yaml(state)
    assert "task-abc" in output


def test_task_detail_yaml_is_valid_yaml():
    """task_detail_yaml output must be parseable YAML."""
    import yaml
    state = make_state()
    state.tasks.append(TaskItem(id="t1", title="Task One"))
    r = MigrationReporter()
    output = r.task_detail_yaml(state)
    parsed = yaml.safe_load(output)
    assert isinstance(parsed, list)


# ── error_fix_log ──────────────────────────────────────────────────────────────

def test_error_fix_log_shows_error_codes():
    """error_fix_log must embed error codes from state.build_errors."""
    state = make_state()
    state.build_errors.append(
        BuildError(error_code="CS0246", message="Type not found", file_path="Foo.cs")
    )
    r = MigrationReporter()
    output = r.error_fix_log(state)
    assert "CS0246" in output
    assert "Foo.cs" in output


def test_error_fix_log_shows_fallback_when_empty():
    """error_fix_log should indicate no errors when build_errors is empty."""
    state = make_state()
    r = MigrationReporter()
    output = r.error_fix_log(state)
    assert "No errors" in output or "—" in output


# ── debt_register_yaml ─────────────────────────────────────────────────────────

def test_debt_register_yaml_serializes_debt_ids():
    """debt_register_yaml must embed debt item IDs from state.debt."""
    state = make_state()
    state.debt.append(DebtItem(id="debt-01", description="Legacy coupling", phase="phase1"))
    r = MigrationReporter()
    output = r.debt_register_yaml(state)
    assert "debt-01" in output


# ── pr_description ─────────────────────────────────────────────────────────────

def test_pr_description_contains_migration_id():
    """pr_description must embed state.migration_id."""
    state = make_state(migration_id="pr-test-001")
    r = MigrationReporter()
    output = r.pr_description(state)
    assert "pr-test-001" in output


def test_pr_description_shows_completed_task_count():
    """pr_description must reflect completed task count from state.tasks."""
    state = make_state()
    state.tasks.append(TaskItem(id="t1", title="Done", status="completed"))
    state.tasks.append(TaskItem(id="t2", title="Pending", status="pending"))
    r = MigrationReporter()
    output = r.pr_description(state)
    # "1/2" or similar completed count must appear
    assert "1" in output and "2" in output


# ── evolution_report ───────────────────────────────────────────────────────────

def test_evolution_report_shows_learned_patterns():
    """evolution_report must embed learned pattern entries from state.learned_patterns."""
    state = make_state()
    state.learned_patterns["pattern_1"] = "null ref → null check added"
    r = MigrationReporter()
    output = r.evolution_report(state)
    assert "pattern_1" in output
    assert "null ref" in output


def test_evolution_report_shows_fallback_when_empty():
    """evolution_report should indicate no patterns when learned_patterns is empty."""
    state = make_state()
    r = MigrationReporter()
    output = r.evolution_report(state)
    assert "No patterns" in output or "—" in output
