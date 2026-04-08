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
    "dotnet-controller-migration",
    "dotnet-webconfig-to-appsettings",
    "dotnet-startup-migration",
    "dotnet-auth-middleware",
    "dotnet-namespace-replacement",
    "dotnet-logging-adapter",
    "dotnet-docker-setup",
    "dotnet-nuget-mapping",
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
            # Claude Code: skills go in .claude/commands/ (slash-command skills)
            (target / ".claude" / "commands").mkdir(parents=True, exist_ok=True)
            # omx: skills go in AGENTS.md or omx's skill overlay dir
            (target / ".omx" / "agents").mkdir(parents=True, exist_ok=True)
            shutil.copy(src / "SKILL.md", target / ".claude" / "commands" / f"{skill}.md")
            shutil.copy(src / "SKILL.md", target / ".omx" / "agents" / f"{skill}.md")
            table.add_row(skill, "[green]✅ OK[/]")
            success += 1
        except Exception as e:
            table.add_row(skill, f"[red]Error: {e}[/]")

    console.print(table)
    console.print(f"[bold green]✅ Synced {success}/{len(SKILLS)} skills[/]")

if __name__ == "__main__":
    app()
