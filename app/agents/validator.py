from app.core.state import MigrationState
from app.core.harness_adapter import harness
from app.core.ruflo_mcp import ruflo_client
from app.core.auto_skill_creator import auto_skill_creator
from app.integrations.vibekanban_adapter import vibekanban
from rich.console import Console
from datetime import datetime

console = Console()

def validator_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Validator", "🟢 Running", progress=50)
    console.print("[bold cyan]✅ Validator & Self-Healing đang chạy...[/]")

    worktree = state.worktree_path or state.solution_path
    task_spec = {
        "harness": "omo",
        "model": "glm-5",
        "command": "ultrawork",
        "task": "dotnet build --no-incremental && dotnet test",
        "worktree": worktree
    }
    result = harness.execute(task_spec, state)

    if result["returncode"] == 0:
        vibekanban.update_agent("Validator", "✅ Completed", progress=100.0)
    else:
        error = result["stderr"][:800]
        ruflo_client.learn_pattern(state, error, "Auto-fix by Ruflo")

        # Auto Skill Creation nếu lỗi lặp lại
        if len(state.error_log) >= 3:
            skill_name = f"auto-fix-{hash(error[:100]) % 10000}"
            auto_skill_creator.create_skill(skill_name, f"Auto fix for repeated error: {error[:80]}")

        vibekanban.push("error", {"message": error[:300], "phase": state.current_phase})
        vibekanban.update_agent("Validator", "⚠️ Error", progress=0)
        state.error_log.append({"error": error, "timestamp": datetime.now().isoformat()})

    return state
