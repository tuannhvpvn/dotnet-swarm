from app.core.state import MigrationState, TaskItem
from app.integrations.vibekanban_adapter import vibekanban
from rich.console import Console

console = Console()

def plan_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Planner", "🟢 Running", progress=10)
    console.print("[bold blue]📝 Planner Agent đang phân tích workflow task...[/]")
    
    inventory = state.inventory or {}
    
    tasks = []
    
    tasks.append(TaskItem(
        id="csproj_migration_1",
        title="Lift and shift .csproj and Packages to .NET 10",
        status="pending"
    ))
    
    tasks.append(TaskItem(
        id="ef6_migration_1",
        title="Refactor Oracle EF6 dependency",
        status="pending"
    ))
    
    state.tasks = tasks
    
    vibekanban.update_agent("Planner", "✅ Completed", progress=100.0)
    console.print(f"[green]✅ Plan hoàn tất với {len(tasks)} tasks[/]")
    return state
