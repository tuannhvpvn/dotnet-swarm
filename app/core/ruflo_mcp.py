import requests
from rich.console import Console
from app.core.state import MigrationState

console = Console()

class RufloMCPClient:
    def __init__(self, base_url: str = "http://localhost:3131"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def learn_pattern(self, state: MigrationState, error: str, fix: str):
        payload = {"action": "learn", "migration_id": state.migration_id, "phase": state.current_phase, "error": error[:600], "fix": fix[:400]}
        try:
            self.session.post(f"{self.base_url}/learn", json=payload, timeout=6)
            state.learned_patterns[f"pattern_{len(state.learned_patterns)+1}"] = f"{error[:60]} → {fix[:60]}"
            console.print("[magenta]🧬 SONA: Learned new pattern[/]")
        except:
            pass

    def get_reasoning(self, query: str) -> str:
        try:
            resp = self.session.post(f"{self.base_url}/reason", json={"query": query}, timeout=10)
            return resp.json().get("reasoning", "No reasoning")
        except:
            return "Ruflo unavailable"

    def route_task(self, state: MigrationState, context: str) -> str:
        payload = {"action": "route_hierarchical", "migration_id": state.migration_id, "current_phase": state.current_phase, "context": context}
        try:
            resp = self.session.post(f"{self.base_url}/route", json=payload, timeout=8)
            return resp.json().get("next_node", "validator")
        except:
            return "validator"

ruflo_client = RufloMCPClient()
