import requests
from rich.console import Console
from app.core.config import settings

console = Console()

class GitNexusAdapter:
    def __init__(self):
        self.enabled = settings.gitnexus_enabled
        self.mcp_url = settings.gitnexus_mcp_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def index_repo(self, solution_path: str):
        """Index codebase bằng GitNexus để tạo Knowledge Graph"""
        if not self.enabled:
            return False
        try:
            resp = self.session.post(
                f"{self.mcp_url}/index",
                json={"path": solution_path, "language": "csharp"},
                timeout=30
            )
            if resp.status_code == 200:
                console.print("[green]✅ GitNexus đã index repo thành công[/]")
                return True
        except Exception as e:
            console.print(f"[yellow]⚠️ GitNexus index fail: {e}[/]")
        return False

    def query(self, query: str):
        """Query Knowledge Graph"""
        if not self.enabled:
            return None
        try:
            resp = self.session.post(
                f"{self.mcp_url}/query",
                json={"query": query},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
        except:
            return None
        return None

gitnexus = GitNexusAdapter()
