from pathlib import Path
import yaml
from datetime import datetime
from rich.console import Console
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.state import MigrationState

console = Console()

def generate_task_report(state: "MigrationState"):
    reports_dir = Path(state.solution_path) / "state" / "reports" / "tasks"
    reports_dir.mkdir(parents=True, exist_ok=True)
    for task in state.tasks:
        if task.status in ["completed", "failed"]:
            report = {
                "task_id": task.id,
                "phase": state.current_phase,
                "status": task.status,
                "timestamp": datetime.now().isoformat()
            }
            (reports_dir / f"{task.id}.yaml").write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True))

def generate_phase_report(state: "MigrationState"):
    reports_dir = Path(state.solution_path) / "state" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"phase-{state.current_phase}-summary-{state.migration_id}.md"
    completed = [t for t in state.tasks if t.status == "completed"]
    failed = [t for t in state.tasks if t.status == "failed"]
    content = f"# Migration Report - {state.current_phase.upper()}\n**ID:** {state.migration_id}\n**Time:** {datetime.now()}\n\nCompleted: {len(completed)}\nFailed: {len(failed)}\n"
    report_path.write_text(content, encoding="utf-8")
    console.print(f"[green]📝 Phase report created:[/] {report_path.name}")

def generate_evolution_report(state: "MigrationState"):
    reports_dir = Path(state.solution_path) / "state" / "reports"
    report_path = reports_dir / f"evolution-{state.migration_id}.md"
    content = f"# 🧬 Self-Evolution Report\nLearned Patterns: {len(state.learned_patterns)}\n"
    for k, v in state.learned_patterns.items():
        content += f"- {k}: {v}\n"
    report_path.write_text(content, encoding="utf-8")
    console.print(f"[magenta]🧬 Evolution report created[/]")
