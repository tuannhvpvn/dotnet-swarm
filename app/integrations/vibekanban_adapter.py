import requests
from datetime import datetime
from rich.console import Console

console = Console()

class VibekanbanAdapter:
    def __init__(self, enabled: bool = True, base_url: str = "http://localhost:3000/api/mcp"):
        self.enabled = enabled
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def push(self, event_type: str, data: dict):
        if not self.enabled:
            return False
        payload = {
            "source": "dotnet-migration-swarm",
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        try:
            resp = self.session.post(f"{self.base_url}/push", json=payload, timeout=4)
            if resp.status_code == 200:
                console.print(f"[green]📤 Vibekanban: {event_type} pushed[/]")
                return True
        except:
            pass
        return False

    def update_agent(self, agent_name: str, status: str, task_id: str = None, progress: float = None):
        data = {
            "agent": agent_name,
            "status": status,
            "task_id": task_id,
            "progress": progress
        }
        return self.push("agent_status", data)

# Singleton
vibekanban = VibekanbanAdapter(enabled=True)
