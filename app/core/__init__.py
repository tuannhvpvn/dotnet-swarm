from app.core.state import MigrationState
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.persistence import MigrationPersistence

# Graph import is lazy — requires langgraph-checkpoint-sqlite at runtime
def build_migration_graph(*args, **kwargs):
    from app.core.graph import build_migration_graph as _build
    return _build(*args, **kwargs)

def run_migration(*args, **kwargs):
    from app.core.graph import run_migration as _run
    return _run(*args, **kwargs)

__all__ = [
    "MigrationState",
    "settings",
    "setup_logging",
    "MigrationPersistence",
    "build_migration_graph",
    "run_migration",
]
