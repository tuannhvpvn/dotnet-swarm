from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict

class Settings(BaseSettings):
    migration_id: str = "mig-default-202604"
    default_phase: int = 1
    timeout_minutes: int = 30

    # Vibekanban
    vibekanban_enabled: bool = True
    vibekanban_url: str = "http://localhost:3000/api/mcp"

    # Ruflo
    ruflo_mcp_url: str = "http://localhost:3131"
    ruflo_port: int = 3131

    # GitNexus
    gitnexus_enabled: bool = True
    gitnexus_mcp_url: str = "http://localhost:4000/mcp"
    gitnexus_index_on_start: bool = True

    # Task mapping
    task_mapping: Dict = {
        "survey": {"harness": "omo", "model": "claude-4.6-sonnet"},
        "phase1_lift": {"harness": "omx", "model": "claude-4.6-sonnet"},
        "phase2_modernize": {"harness": "omc", "model": "claude-4.6-opus"},
        "validate": {"harness": "omo", "model": "glm-5"}
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
