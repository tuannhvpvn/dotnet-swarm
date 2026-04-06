from app.core.state import MigrationState
from app.tools.adapter import call_harness
from app.utils.worktree import create_worktree
from app.integrations.vibekanban_adapter import vibekanban
from rich.console import Console

console = Console()

def phase2_modernizer_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Phase2 Modernizer", "🟢 Running", progress=10)
    console.print("[bold magenta]🚀 Phase2 Modernizer đang chạy...[/]")

    worktree = create_worktree(state.solution_path, "phase2")
    state.git_worktree = worktree

    task_spec = {
        "harness": "omc",
        "model": "claude-4.6-opus",
        "command": "team",
        "task": "Refactor sang Clean Architecture + DDD + CQRS + TDD + Dapper + EF Core hybrid",
        "worktree": worktree
    }
    result = call_harness(task_spec)

    state.phase_progress["phase2"] = 85.0
    state.completed_tasks.append({"task_id": "phase2-001", "status": "completed"})

    vibekanban.update_agent("Phase2 Modernizer", "✅ Completed", progress=100.0)
    console.print("[green]✅ Phase 2 Modernize hoàn tất[/]")
    return state
