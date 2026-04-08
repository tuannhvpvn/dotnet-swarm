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
    """
    Harness: opencode (oh-my-openagent's ultrawork mode).
    Binary: opencode (installed at ~/.local/bin/opencode)
    Headless execution: opencode run <prompt> --cwd <dir>
    """
    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        cmd = [
            "opencode", "run",
            task_spec.get("task", ""),
            "--cwd", task_spec.get("worktree", "."),
        ]
        model = task_spec.get("model")
        if model:
            cmd += ["--model", model]
        return cmd


class ClaudeCodeHarness(HarnessExecutor):
    """
    Harness: claude (Claude Code CLI — /usr/bin/claude).
    Uses -p/--print for headless non-interactive mode.
    Context injected via CLAUDE.md sidecar in the worktree.
    """
    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        model = task_spec.get("model", "claude-opus-4-6")
        return [
            "claude",
            "-p", task_spec.get("task", ""),
            "--model", model,
            "--output-format", "text",
            "--dangerously-skip-permissions",
        ]


class CodexHarness(HarnessExecutor):
    """
    Harness: omx exec (oh-my-codex non-interactive mode).
    Binary: omx (installed at ~/.local/share/pnpm/omx)
    Uses 'omx exec' which runs codex non-interactively with OMX overlay injection.
    Context injected via AGENTS.md sidecar in the worktree.
    """
    def _get_sidecar_filename(self) -> str:
        return "AGENTS.md"

    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        return [
            "omx", "exec",
            "--task", task_spec.get("task", ""),
            "--work-dir", task_spec.get("worktree", "."),
        ]


class KiroHarness(HarnessExecutor):
    """
    Harness: kiro-cli (installed at ~/.local/bin/kiro-cli).
    Context injected via .kiro/rules/migration.md sidecar.
    """
    def _get_sidecar_filename(self) -> str:
        return ".kiro/rules/migration.md"

    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        return [
            "kiro-cli",
            "--task", task_spec.get("task", ""),
            "--work-dir", task_spec.get("worktree", "."),
        ]


class GeminiHarness(HarnessExecutor):
    """
    Harness: gemini (Google Gemini CLI — ~/.local/share/pnpm/gemini).
    Uses -p/--print equivalent for non-interactive mode.
    Context injected via GEMINI.md sidecar.
    """
    def _get_sidecar_filename(self) -> str:
        return "GEMINI.md"

    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        return [
            "gemini",
            "-p", task_spec.get("task", ""),
            "--yolo",
        ]


class AiderHarness(HarnessExecutor):
    """
    Harness: aider (installed at ~/.local/bin/aider).
    Good for deterministic file edits and structured diffs.
    Uses --message for non-interactive one-shot execution.
    """
    def _get_sidecar_filename(self) -> str:
        return ".aider.conf.yml"

    def _build_cmd(self, task_spec: Dict[str, Any]) -> list[str]:
        model = task_spec.get("model", "claude-opus-4-6")
        return [
            "aider",
            "--message", task_spec.get("task", ""),
            "--model", model,
            "--yes-always",
            "--no-stream",
        ]


def call_harness(task_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Factory function for routing harness commands.

    Harness key → CLI binary mapping (all verified installed):
      "opencode" / "omo" → opencode run        (~/.local/bin/opencode)
      "claude"   / "omc" → claude -p           (/usr/bin/claude)
      "omx"              → omx exec            (~/.local/share/pnpm/omx)
      "kiro"             → kiro-cli            (~/.local/bin/kiro-cli)
      "gemini"           → gemini -p           (~/.local/share/pnpm/gemini)
      "aider"            → aider --message     (~/.local/bin/aider)
    """
    harness_type = task_spec.get("harness", "claude")
    _REGISTRY: Dict[str, type] = {
        "opencode": OpenCodeHarness,
        "omo":      OpenCodeHarness,   # legacy alias
        "claude":   ClaudeCodeHarness,
        "omc":      ClaudeCodeHarness,  # legacy alias
        "omx":      CodexHarness,
        "kiro":     KiroHarness,
        "gemini":   GeminiHarness,
        "aider":    AiderHarness,
    }
    harness_cls = _REGISTRY.get(harness_type)
    if harness_cls is None:
        logger.warning(f"Unknown harness type '{harness_type}', falling back to claude")
        harness_cls = ClaudeCodeHarness
    try:
        return harness_cls().execute(task_spec)
    except Exception as e:
        logger.error(f"Harness '{harness_type}' exhausted all retries. Final error: {str(e)}")
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"All retries exhausted. {str(e)}",
            "output": None
        }
