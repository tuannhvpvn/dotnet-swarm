from app.core.state import MigrationState
from app.core.harness_adapter import harness
from app.utils.worktree import create_worktree
from app.integrations.vibekanban_adapter import vibekanban
from rich.console import Console

console = Console()

def phase1_migrator_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Phase1 Migrator", "🟢 Running", progress=10)
    console.print("[bold yellow]🔄 Phase1 Migrator (Lift & Shift) đang chạy...[/]")

    worktree = create_worktree(state.solution_path, "phase1")
    state.worktree_path = worktree

    task_spec = {
        "harness": "omx",
        "model": "claude-4.6-sonnet",
        "command": "team",
        "task": "Lift-and-shift sang .NET 10, giữ nguyên kiến trúc cũ, chỉ thay csproj/packages",
        "worktree": worktree
    }
    result = harness.execute(task_spec, state)

    vibekanban.update_agent("Phase1 Migrator", "✅ Completed", progress=100.0)
    console.print("[green]✅ Phase 1 Lift & Shift hoàn tất[/]")
    return state
