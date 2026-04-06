import subprocess
import json
from typing import Dict, Any
from rich.console import Console
from loguru import logger

console = Console()

def call_harness(task_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call external harness (omo, omx, omc) to execute migration task.

    Args:
        task_spec: {
            "harness": "omo" | "omx" | "omc",
            "model": "claude-4.6-sonnet" | "claude-4.6-opus" | "glm-5",
            "command": "ultrawork" | "team",
            "task": "Task description",
            "worktree": "Path to working directory"
        }

    Returns:
        {
            "returncode": int,
            "stdout": str,
            "stderr": str,
            "output": Any
        }
    """
    harness = task_spec.get("harness", "omo")
    model = task_spec.get("model", "claude-4.6-sonnet")
    command = task_spec.get("command", "ultrawork")
    task = task_spec.get("task", "")
    worktree = task_spec.get("worktree", ".")

    console.print(f"[bold cyan]📡 Calling harness {harness} with {model}[/]")
    logger.info(f"Harness call: {harness} | Model: {model} | Command: {command}")

    try:
        # Construct harness command
        cmd = [
            harness,
            command,
            "--model", model,
            "--task", task,
            "--work-dir", worktree
        ]

        result = subprocess.run(
            cmd,
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=300
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output": None
        }

    except subprocess.TimeoutExpired:
        logger.error(f"Harness timeout: {harness}")
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": "Task timeout",
            "output": None
        }
    except Exception as e:
        logger.error(f"Harness error: {str(e)}")
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "output": None
        }
