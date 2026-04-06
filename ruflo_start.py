import subprocess
import typer
from rich.console import Console

console = Console()
app = typer.Typer()

@app.command()
def start(port: int = 3131, background: bool = False):
    cmd = ["npx", "ruflo", "mcp", "start", "--port", str(port)]
    if background:
        subprocess.Popen(cmd, start_new_session=True)
        console.print(f"✅ Ruflo MCP running in background (port {port})")
    else:
        subprocess.run(cmd)

if __name__ == "__main__":
    app()
