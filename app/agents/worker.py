from app.core.state import MigrationState
from app.tools.adapter import call_harness
from app.utils.worktree import create_worktree
from app.integrations.vibekanban_adapter import vibekanban
from app.core.ruflo_mcp import ruflo_client
from rich.console import Console

console = Console()

def human_gate_node(state: MigrationState) -> MigrationState:
    """No-op node. Used as hook for LangGraph interrupt_before."""
    console.print("[bold yellow]⛔ Human Gate: Đợi phê duyệt...[/]")
    return state

def prepare_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Worker", "🟢 Preparing", progress=10)
    if not state.worktree_path:
        worktree = create_worktree(state.solution_path, "migration")
        state.worktree_path = worktree
    console.print("[green]✅ Prepare hoàn tất[/]")
    return state

def migrate_task_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Migrator", "🟢 Migrating", progress=40)
    
    # Tìm task pending hoặc failed đầu tiên
    pending_task = next((t for t in state.tasks if t.status in ["pending", "failed"]), None)
    if not pending_task:
        console.print("[bold cyan]Không còn tasks nào cần migrate.[/]")
        return state
        
    console.print(f"[bold magenta]🚀 Migrating Task: {pending_task.title}[/]")
    state.current_task_id = pending_task.id
    
    task_spec = {
        "harness": "omc",
        "command": "team",
        "task": pending_task.title,
        "worktree": state.worktree_path or state.solution_path
    }
    
    result = call_harness(task_spec)
    
    if result["returncode"] == 0:
        pending_task.status = "completed"
    else:
        pending_task.status = "failed"
        
    return state

def checkpoint_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Checkpoint", "🟢 Analyzing", progress=80)
    
    # Dùng Ruflo MCP để review thay vì điều phối route dynamic
    reasoning = ruflo_client.get_reasoning(f"Review worktree for task {state.current_task_id}. Deviations?")
    console.print(f"[bold cyan]🔍 Checkpoint Audit: {reasoning[:150]}[/]")
    
    return state

def fix_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Worker", "🟢 Fixing", progress=90)
    
    pending_task = next((t for t in state.tasks if t.id == state.current_task_id), None)
    if pending_task:
        pending_task.status = "in_progress" # Reset for retry
        state.fix_attempts += 1
        console.print(f"[bold magenta]🛠️ Fix attempt {state.fix_attempts} for: {pending_task.title}[/]")
        
    return state
