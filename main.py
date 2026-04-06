import json
import typer
from rich.console import Console
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.core.logger import setup_logging
from app.core.persistence import MigrationPersistence
from app.utils.sync_skills import run as sync_skills
from app.integrations.gitnexus_adapter import gitnexus

console = Console()
app = typer.Typer(help="🧬 .NET Migration Swarm — Queen-led autonomous migration orchestrator")


@app.command()
def start(
    solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET"),
    phase: int = typer.Option(1, help="Phase bắt đầu (1=lift-and-shift, 2=modernize)")
):
    """🚀 Bắt đầu migration mới từ đầu."""
    from app.core.graph import run_migration
    sol = Path(solution_path).resolve()
    setup_logging(str(sol))
    logger.info(f"🚀 Migration Swarm khởi động cho: {sol}")

    persistence = MigrationPersistence(str(sol))

    if settings.gitnexus_enabled and settings.gitnexus_index_on_start:
        logger.info("🔍 Indexing codebase with GitNexus...")
        gitnexus.index_repo(str(sol))

    sync_skills(str(sol))
    run_migration(str(sol), start_phase=phase, persistence=persistence)


@app.command()
def resume(
    solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET")
):
    """♻️ Khôi phục migration đang dở từ state được lưu."""
    from app.core.graph import run_migration
    sol = Path(solution_path).resolve()
    setup_logging(str(sol))
    persistence = MigrationPersistence(str(sol))

    state = persistence.load(settings.migration_id)
    if not state:
        console.print("[bold red]❌ Không tìm thấy state đã lưu. Chạy lệnh start trước.[/]")
        raise typer.Exit(1)

    console.print(f"[bold green]✅ Khôi phục migration: {state.migration_id}[/]")
    console.print(f"[bold cyan]Phase hiện tại:[/] {state.current_phase}")
    run_migration(str(sol), start_phase=1, persistence=persistence)


@app.command()
def status(
    solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET")
):
    """📊 Hiển thị trạng thái migration hiện tại."""
    json_path = Path(solution_path) / "state" / "current_state.json"
    if not json_path.exists():
        console.print("[yellow]⚠️ Chưa có state. Chạy lệnh start trước.[/]")
        raise typer.Exit(1)

    state_dict = json.loads(json_path.read_text(encoding="utf-8"))
    tasks = state_dict.get("tasks", [])
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    failed = sum(1 for t in tasks if t.get("status") == "failed")

    console.print(f"\n[bold]🧬 Migration Status[/]")
    console.print(f"[bold cyan]Migration ID:[/]   {state_dict.get('migration_id', 'N/A')}")
    console.print(f"[bold cyan]Phase:[/]          {state_dict.get('current_phase', 'N/A')}")
    console.print(f"[bold cyan]Workflow:[/]        {state_dict.get('workflow_state', 'normal')}")
    console.print(f"[bold cyan]Tasks:[/]           {completed} ✅  {failed} ❌  {len(tasks)} total")
    console.print(f"[bold cyan]Fix Attempts:[/]    {state_dict.get('fix_attempts', 0)}")
    console.print(f"[bold cyan]Build Errors:[/]    {len(state_dict.get('build_errors', []))}")
    console.print(f"[bold cyan]Debt Items:[/]      {len(state_dict.get('debt', []))}")

    if state_dict.get("blocked_reason"):
        console.print(f"\n[bold red]⛔ BLOCKED:[/] {state_dict.get('blocked_reason')}")
        console.print("[yellow]  → Dùng lệnh 'approve' để tiếp tục.[/]")


@app.command()
def approve(
    solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET"),
    decision: str = typer.Option("approve", help="Quyết định: approve | modify | reject")
):
    """✅ Ghi human gate decision vào state và tiếp tục migration."""
    json_path = Path(solution_path) / "state" / "current_state.json"
    if not json_path.exists():
        console.print("[bold red]❌ Không tìm thấy state.[/]")
        raise typer.Exit(1)

    state_dict = json.loads(json_path.read_text(encoding="utf-8"))
    state_dict["human_decision"] = decision
    state_dict["workflow_state"] = "normal"
    state_dict["blocked_reason"] = None
    json_path.write_text(json.dumps(state_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"[bold green]✅ Human gate decision recorded: {decision}[/]")
    console.print("[bold cyan]Chạy lại lệnh resume để tiếp tục migration.[/]")


if __name__ == "__main__":
    app()
