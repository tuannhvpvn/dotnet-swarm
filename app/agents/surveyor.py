from app.core.state import MigrationState
from app.tools.adapter import call_harness
from app.integrations.vibekanban_adapter import vibekanban
from app.integrations.gitnexus_adapter import gitnexus
from rich.console import Console

console = Console()

def surveyor_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Surveyor", "🟢 Running", task_id="survey-001")
    console.print("[bold blue]📊 Surveyor Agent đang scan...[/]")

    # Sử dụng GitNexus để scan chính xác
    if gitnexus.enabled:
        console.print("[cyan]🔍 Sử dụng GitNexus Knowledge Graph...[/]")
        gitnexus.index_repo(state.solution_path)

    task_spec = {
        "harness": "omo",
        "model": "claude-4.6-sonnet",
        "command": "ultrawork",
        "task": "Scan multi-solution, dependency graph, Oracle, EF6, MSAL, breaking changes",
        "worktree": state.solution_path
    }
    result = call_harness(task_spec)

    state.phase_progress["survey"] = 100.0
    state.completed_tasks.append({"task_id": "survey-001", "status": "completed"})

    vibekanban.update_agent("Surveyor", "✅ Completed", progress=100.0)
    console.print("[green]✅ Survey hoàn tất[/]")
    return state
