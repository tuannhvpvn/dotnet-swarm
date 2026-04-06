from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, List, Dict, Any

class MigrationState(BaseModel):
    migration_id: str
    solution_path: str
    current_phase: Literal["survey", "phase1", "phase2", "complete"] = "survey"

    phase_progress: Dict[str, float] = Field(default_factory=dict)
    completed_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    failed_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    error_log: List[Dict[str, Any]] = Field(default_factory=list)
    learned_patterns: Dict[str, str] = Field(default_factory=dict)

    needs_human_approval: bool = False
    git_worktree: str | None = None
    last_updated: datetime = Field(default_factory=datetime.now)
