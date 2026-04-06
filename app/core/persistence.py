import json
import sqlite3
from pathlib import Path
from datetime import datetime
from app.core.state import MigrationState, TaskItem
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT,
                migration_id TEXT,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                logs TEXT,
                PRIMARY KEY (id, migration_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_id TEXT,
                error_code TEXT,
                file_path TEXT,
                message TEXT,
                timestamp TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_id TEXT,
                pattern_key TEXT,
                pattern_value TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_id TEXT,
                agent_name TEXT,
                action TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save(self, state: MigrationState):
        state.last_updated = datetime.now()
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        state_json_str = state.model_dump_json(indent=2)
        with open(self.json_path, "w", encoding="utf-8") as f:
            f.write(state_json_str)

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO migrations (migration_id, state_json, last_updated) VALUES (?, ?, ?)",
            (state.migration_id, state.model_dump_json(), state.last_updated.isoformat())
        )
        
        # Save tasks 
        for t in state.tasks:
            conn.execute(
                "INSERT OR REPLACE INTO tasks (id, migration_id, title, status, logs) VALUES (?, ?, ?, ?, ?)",
                (t.id, state.migration_id, t.title, t.status, json.dumps(t.logs))
            )
            
        conn.commit()
        conn.close()
        logger.info(f"State saved: {state.migration_id}")

    def load(self, migration_id: str) -> MigrationState | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT state_json FROM migrations WHERE migration_id = ?", (migration_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            conn.close()
            return None
            
        state_dict = json.loads(row[0])
        state = MigrationState.model_validate(state_dict)
        
        # Optionally enrich state from tables if relational tracking diverged
        task_cursor = conn.execute("SELECT id, title, status, logs FROM tasks WHERE migration_id = ?", (migration_id,))
        db_tasks = task_cursor.fetchall()
        if db_tasks:
            loaded_tasks = []
            for t_row in db_tasks:
                loaded_tasks.append(TaskItem(
                    id=t_row[0],
                    title=t_row[1],
                    status=t_row[2],
                    logs=json.loads(t_row[3]) if t_row[3] else []
                ))
            # Merge with state
            state.tasks = loaded_tasks
            
        conn.close()
        return state
