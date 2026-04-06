from loguru import logger
import sys
from pathlib import Path

def setup_logging(solution_path: str):
    log_dir = Path(solution_path) / "state" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    # File log
    logger.add(
        log_dir / "migration_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {message}",
        encoding="utf-8"
    )

    # Console log
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | {message}",
        colorize=True
    )

    logger.info("=== .NET Migration Swarm Logger initialized ===")
    return logger
