from app.core.state import MigrationState
from app.utils.reporter import MigrationReporter
from app.integrations.vibekanban_adapter import vibekanban
from rich.console import Console

console = Console()
_reporter = MigrationReporter()

def documenter_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Documenter", "🟢 Running")
    console.print("[bold white]📝 Documenter đang tạo report...[/]")

    _reporter.phase_summary(state)
    _reporter.task_detail_yaml(state)
    _reporter.evolution_report(state)

    vibekanban.update_agent("Documenter", "✅ Completed")
    vibekanban.push("phase_complete", {"phase": state.current_phase})
    return state
