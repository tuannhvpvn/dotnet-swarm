import json
import sqlite3
from pathlib import Path
from datetime import datetime
from app.core.state import MigrationState
from loguru import logger

class MigrationPersistence:
    def __init__(self, solution_path: str):
        self.base_path = Path(solution_path)
        self.db_path = self.base_path / "state" / "migration.db"
        self.json_path = self.base_path / "state" / "current_state.json"
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                migration_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, state: MigrationState):
        state.last_updated = datetime.now()
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO migrations (migration_id, state_json, last_updated) VALUES (?, ?, ?)",
            (state.migration_id, state.model_dump_json(), state.last_updated.isoformat())
        )
        conn.commit()
        conn.close()
        logger.info(f"State saved: {state.migration_id}")

    def load(self, migration_id: str) -> MigrationState | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT state_json FROM migrations WHERE migration_id = ?", (migration_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return MigrationState.model_validate(json.loads(row[0]))
        return None
