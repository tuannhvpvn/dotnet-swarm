"""
Generic Harness Adapter — wraps all external CLI calls with defense-in-depth safety.

Flow: Pre-flight check → Install git hook → Delegate to call_harness → Post-scan → Return
"""
import subprocess
from typing import Any
from loguru import logger
from rich.console import Console

from app.core.safety import SafetyRules, SafetyResult
from app.tools.adapter import call_harness

console = Console()


class HarnessAdapter:
    """Adapter bọc call_harness() với safety checks trước và sau."""

    def __init__(self, safety: SafetyRules):
        self.safety = safety

    def execute(self, task_spec: dict[str, Any], state: Any) -> dict[str, Any]:
        """
        Thực thi harness call với defense-in-depth safety.

        1. Pre-flight: check source files
        2. Install git hook
        3. Delegate to call_harness
        4. Post-execution scan
        5. Return result or rollback on violation
        """
        worktree = task_spec.get("worktree", ".")

        # ── 1. Pre-flight safety check ───────────────────────
        source_files = task_spec.get("source_files", [])
        for fpath in source_files:
            result = self.safety.check_file_path(fpath)
            if not result.safe:
                console.print(f"[bold red]🚫 Pre-flight violation: {result.message}[/]")
                logger.error(f"Safety pre-flight blocked: {result.message}")
                self._log_violation(state, result)
                return {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Safety violation: {result.message}",
                    "output": None
                }

        # ── 2. Install git pre-commit hook ───────────────────
        try:
            self.safety.install_hook(worktree)
        except Exception as e:
            logger.warning(f"Hook install skipped: {e}")

        # ── 3. Delegate to low-level harness ─────────────────
        console.print(f"[bold cyan]🔒 Safety adapter → delegating to harness[/]")
        harness_result = call_harness(task_spec)

        # ── 4. Post-execution worktree scan ──────────────────
        violations = self.safety.scan_worktree(worktree)
        if violations:
            console.print(f"[bold red]🚫 Post-scan: {len(violations)} violation(s) found — rolling back[/]")
            for v in violations:
                logger.error(f"Safety violation: [{v.rule_id}] {v.message}")
                self._log_violation(state, v)

            # Rollback worktree changes
            try:
                subprocess.run(
                    ["git", "checkout", "--", "."],
                    cwd=worktree, capture_output=True, text=True
                )
                logger.info("Worktree rolled back after safety violation")
            except Exception as e:
                logger.error(f"Rollback failed: {e}")

            return {
                "returncode": -1,
                "stdout": harness_result.get("stdout", ""),
                "stderr": f"Safety violations detected post-execution: {len(violations)} issue(s)",
                "output": None
            }

        # ── 5. Success ───────────────────────────────────────
        console.print(f"[bold green]✅ Safety adapter: harness completed cleanly[/]")
        return harness_result

    def _log_violation(self, state: Any, result: SafetyResult):
        """Log violation vào state.safety_violations nếu state có field đó."""
        if hasattr(state, "safety_violations"):
            state.safety_violations.append({
                "rule_id": result.rule_id,
                "severity": result.severity,
                "message": result.message,
                "file_path": result.file_path,
            })


# ── Module-level singleton ───────────────────────────────────
try:
    harness = HarnessAdapter(SafetyRules("config/safety.yaml"))
except Exception:
    # Nếu config chưa tồn tại (test environment), tạo adapter rỗng
    harness = None  # type: ignore
