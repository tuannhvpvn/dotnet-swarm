import typer
from rich.console import Console
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.core.graph import run_migration
from app.core.logger import setup_logging
from app.core.persistence import MigrationPersistence
from app.utils.sync_skills import run as sync_skills
from app.integrations.gitnexus_adapter import gitnexus

console = Console()
app = typer.Typer()

@app.command()
def start(solution_path: str = typer.Argument(..., help="Đường dẫn repo .NET"), phase: int = 1):
    solution_path = Path(solution_path).resolve()
    setup_logging(str(solution_path))
    logger.info(f"🚀 Migration Swarm khởi động cho: {solution_path}")

    persistence = MigrationPersistence(str(solution_path))

    # GitNexus index
    if settings.gitnexus_enabled and settings.gitnexus_index_on_start:
        logger.info("🔍 Indexing codebase with GitNexus...")
        gitnexus.index_repo(str(solution_path))

    sync_skills(str(solution_path))

    run_migration(str(solution_path), start_phase=phase, persistence=persistence)

if __name__ == "__main__":
    app()
