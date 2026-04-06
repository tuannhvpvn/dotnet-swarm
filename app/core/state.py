from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, List, Dict, Any

class TaskItem(BaseModel):
    id: str
    title: str
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    logs: List[str] = Field(default_factory=list)
    # SOP fields — required by SOPEnforcer pre_task_check (Phase 7)
    source_files: list[str] = Field(default_factory=list)
    target_files: list[str] = Field(default_factory=list)
    done_criteria: str | None = None
    verify_command: str | None = None

class BuildError(BaseModel):
    error_code: str
    file_path: str
    line_number: int | None = None
    message: str

class DebtItem(BaseModel):
    id: str
    description: str
    phase: str
    resolved: bool = False

class MigrationState(BaseModel):
    migration_id: str
    solution_path: str
    current_phase: Literal["survey", "phase1", "phase2", "complete"] = "survey"
    
    inventory: dict | None = None
    plan: dict | None = None
    tasks: list[TaskItem] = Field(default_factory=list)
    current_task_id: str | None = None
    current_tier: int = 0
    
    build_errors: list[BuildError] = Field(default_factory=list)
    fix_attempts: int = 0
    max_fix_attempts: int = 5
    
    debt: list[DebtItem] = Field(default_factory=list)
    blocked_reason: str | None = None
    workflow_state: Literal["normal", "blocked", "remediation"] = "normal"
    human_decision: Literal["pending", "approve", "modify", "reject"] | None = None
    
    reports: list[str] = Field(default_factory=list)
    safety_violations: list[dict] = Field(default_factory=list)
    worktree_path: str | None = None
    session_id: str = ""

    error_log: List[Dict[str, Any]] = Field(default_factory=list)
    learned_patterns: Dict[str, str] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
