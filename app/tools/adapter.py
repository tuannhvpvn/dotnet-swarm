import subprocess
import json
import os
from typing import Dict, Any
from pathlib import Path
from rich.console import Console
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

console = Console()

class HarnessExecutor:
    def _write_sidecar(self, worktree: str, filename: str, content: str):
        path = Path(worktree) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.debug(f"Generated sidecar context: {path}")

    def _inject_context(self, task_spec: Dict[str, Any]):
        worktree = task_spec.get("worktree", ".")
        skills = task_spec.get("skills", [])
        rules = task_spec.get("rules", "")

        if skills or rules:
            content = f"# Migration Rules\n{rules}\n\n# Skills\n"
            idx = 0
            for skill in skills:
                content += f"## Skill {idx}\n{skill}\n\n"
                idx += 1
            filename = self._get_sidecar_filename()
            self._write_sidecar(worktree, filename, content)

    def _get_sidecar_filename(self) -> str:
        return "CLAUDE.md"

    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        raise NotImplementedError()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def execute(self, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực thi harness với factory pattern và retry feedback loop.
        """
        self._inject_context(task_spec)
        cmd = self._build_cmd(task_spec)
        worktree = task_spec.get("worktree", ".")
        console.print(f"[bold cyan]📡 Executing: {' '.join(cmd)}[/]")
        logger.info(f"Harness call: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.warning(f"Harness failed with {result.returncode}. Output: {result.stderr[:200]}")
                # Append error to the task prompt for the LLM to read on retry
                task_spec["task"] += f"\n\nPrevious attempt failed. Error:\n{result.stderr[:500]}\nFix this error and retry."
                raise Exception(f"Harness returned {result.returncode}")

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": None
            }
        except subprocess.TimeoutExpired:
            logger.error("Harness timeout")
            task_spec["task"] += "\n\nPrevious attempt timed out. Work faster or simpler."
            raise Exception("Harness timeout")
        except Exception as e:
            logger.error(f"Harness error: {str(e)}")
            # Nếu là do subprocess raise Exception ở trên, tenacity sẽ tự retry
            raise


class OpenCodeHarness(HarnessExecutor):
    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        return ["omo", task_spec.get("command", "ultrawork"), "--model", task_spec.get("model", "glm-5"), "--task", task_spec.get("task", ""), "--work-dir", task_spec.get("worktree", ".")]


class ClaudeCodeHarness(HarnessExecutor):
    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        return ["omc", task_spec.get("command", "team"), "--model", task_spec.get("model", "claude-4.6-opus"), "--task", task_spec.get("task", ""), "--work-dir", task_spec.get("worktree", ".")]


class CodexHarness(HarnessExecutor):
    def _get_sidecar_filename(self) -> str:
        return "AGENTS.md"

    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        return ["omx", task_spec.get("command", "team"), "--model", task_spec.get("model", "claude-4.6-sonnet"), "--task", task_spec.get("task", ""), "--work-dir", task_spec.get("worktree", ".")]


class KiroHarness(HarnessExecutor):
    def _get_sidecar_filename(self) -> str:
        return ".kiro/rules/migration.md"

    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        # Kiro uses positional task or flags differently, assuming parity for uniform CLI API
        return ["kiro", task_spec.get("command", "run"), "--model", task_spec.get("model", "claude-4.6-sonnet"), "--task", task_spec.get("task", ""), "--work-dir", task_spec.get("worktree", ".")]


def call_harness(task_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Factory function for routing harness commands.
    Used seamlessly by app.core.harness_adapter in Phase 2.
    """
    harness_type = task_spec.get("harness", "omo")
    try:
        if harness_type == "omo":
            return OpenCodeHarness().execute(task_spec)
        elif harness_type == "omc":
            return ClaudeCodeHarness().execute(task_spec)
        elif harness_type == "omx":
            return CodexHarness().execute(task_spec)
        elif harness_type == "kiro":
            return KiroHarness().execute(task_spec)
        else:
            logger.warning(f"Unknown harness type {harness_type}, falling back to omo")
            return OpenCodeHarness().execute(task_spec)
    except Exception as e:
        logger.error(f"Harness {harness_type} exhausted all retries. Final error: {str(e)}")
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"All retries exhausted. {str(e)}",
            "output": None
        }
