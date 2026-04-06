from pathlib import Path
import subprocess
from rich.console import Console
from datetime import datetime

console = Console()

def create_worktree(solution_path: str, prefix: str = "phase") -> str:
    """Tạo isolated git worktree cho từng phase/task"""
    solution_path = Path(solution_path).resolve()
    worktree_base = solution_path / ".worktrees"
    worktree_base.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    worktree_name = f"{prefix}-{timestamp}"
    worktree_path = worktree_base / worktree_name

    console.print(f"[bold blue]🌳 Tạo isolated worktree:[/] {worktree_name}")

    try:
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree_path)],
            cwd=solution_path,
            check=True,
            capture_output=True,
            text=True
        )
        console.print(f"[green]✅ Worktree tạo thành công:[/] {worktree_path}")
        return str(worktree_path)
    except subprocess.CalledProcessError:
        console.print("[yellow]⚠️ Fallback: dùng thư mục tạm[/]")
        worktree_path.mkdir(parents=True, exist_ok=True)
        return str(worktree_path)
