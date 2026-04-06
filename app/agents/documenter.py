from app.core.state import MigrationState
from app.utils.reporter import generate_phase_report, generate_task_report, generate_evolution_report
from app.integrations.vibekanban_adapter import vibekanban
from rich.console import Console

console = Console()

def documenter_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Documenter", "🟢 Running")
    console.print("[bold white]📝 Documenter đang tạo report...[/]")

    generate_phase_report(state)
    generate_task_report(state)
    generate_evolution_report(state)

    vibekanban.update_agent("Documenter", "✅ Completed")
    vibekanban.push("phase_complete", {"phase": state.current_phase})
    return state
