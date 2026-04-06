from pathlib import Path
import shutil
import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer()

SKILLS = [
    "dotnet-phase1-csproj-upgrade",
    "dotnet-oracle-ef6-migration",
    "dotnet-msal-update",
    "dotnet-clean-arch-cqrs",
    "dotnet-ddd-value-objects",
]

@app.command()
def run(solution_path: str):
    target = Path(solution_path).resolve()
    source_base = Path(".migration-skills").resolve()

    table = Table(title="Skill Sync Result")
    table.add_column("Skill")
    table.add_column("Status")

    success = 0
    for skill in SKILLS:
        src = source_base / skill
        if not src.exists():
            table.add_row(skill, "[red]❌ Missing[/]")
            continue
        try:
            shutil.copytree(src, target / ".kiro/skills" / skill, dirs_exist_ok=True)
            shutil.copytree(src, target / ".opencode/skills" / skill, dirs_exist_ok=True)
            (target / ".omc/skills").mkdir(parents=True, exist_ok=True)
            (target / ".omx/skills").mkdir(parents=True, exist_ok=True)
            shutil.copy(src / "SKILL.md", target / ".omc/skills" / f"{skill}.md")
            shutil.copy(src / "SKILL.md", target / ".omx/skills" / f"{skill}.md")
            table.add_row(skill, "[green]✅ OK[/]")
            success += 1
        except Exception as e:
            table.add_row(skill, f"[red]Error: {e}[/]")

    console.print(table)
    console.print(f"[bold green]✅ Synced {success}/{len(SKILLS)} skills[/]")

if __name__ == "__main__":
    app()
