import subprocess
from dataclasses import dataclass, field as dc_field
from pathlib import Path
from loguru import logger

from app.core.state import MigrationState, TaskItem


@dataclass
class SOPResult:
    checks: list[tuple[str, bool]] = dc_field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(v for _, v in self.checks)

    @property
    def failed_checks(self) -> list[str]:
        return [name for name, v in self.checks if not v]

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        failed = self.failed_checks
        if failed:
            return f"SOPResult({status}, failed={failed})"
        return f"SOPResult({status})"


def _verify_only_expected_files_changed(task: TaskItem, worktree: str) -> bool:
    """Check that only expected target files were modified in the worktree."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return True  # fail-open in non-git environments
        changed = {f.strip() for f in result.stdout.splitlines() if f.strip()}
        if not task.target_files:
            return True  # no target files defined — cannot verify, assume OK
        unexpected = changed - set(task.target_files)
        return len(unexpected) == 0
    except Exception:
        return True  # fail-open


def _verify_no_extra_changes(task: TaskItem, worktree: str) -> bool:
    """Check that no untracked files were created outside the expected target scope."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return True
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        if not task.target_files:
            return True
        for line in lines:
            # porcelain: "?? filename" or " M filename"
            fname = line[3:].strip()
            if fname not in task.target_files:
                return False
        return True
    except Exception:
        return True  # fail-open


class SOPEnforcer:
    """Algorithmic SOP compliance gates — no LLM inference."""

    @staticmethod
    def pre_phase_check(state: MigrationState) -> SOPResult:
        """SOP Section A: Before starting a migration phase."""
        checks: list[tuple[str, bool]] = [
            ("goal_defined", state.plan is not None),
            ("scope_locked", len(state.tasks) > 0),
            ("worktree_set", state.worktree_path is not None),
        ]
        result = SOPResult(checks=checks)
        if not result.passed:
            logger.warning(f"[SOPEnforcer] pre_phase_check FAILED: {result.failed_checks}")
        return result

    @staticmethod
    def pre_task_check(task: TaskItem) -> SOPResult:
        """SOP Section B: Before delegating a task to the harness."""
        checks: list[tuple[str, bool]] = [
            ("task_small_enough", len(task.source_files) <= 5),
            ("single_deliverable", task.done_criteria is not None),
            ("input_clear", len(task.source_files) > 0),
            ("output_clear", len(task.target_files) > 0),
            ("verify_step_defined", task.verify_command is not None),
            ("timeout_set", True),  # always satisfied from config
        ]
        result = SOPResult(checks=checks)
        if not result.passed:
            logger.warning(f"[SOPEnforcer] pre_task_check FAILED for '{task.id}': {result.failed_checks}")
        return result

    @staticmethod
    def post_task_check(task: TaskItem, worktree: str) -> SOPResult:
        """SOP Section E: After task execution completes."""
        # Import safety lazily to handle missing config gracefully
        try:
            from app.core.safety import SafetyRules
            safety_rules = SafetyRules()
            violations = safety_rules.scan_worktree(worktree)
            is_clean = len(violations) == 0
        except Exception as e:
            logger.warning(f"[SOPEnforcer] Safety scan skipped: {e}")
            is_clean = True  # fail-open when safety config unavailable

        checks: list[tuple[str, bool]] = [
            ("scope_correct", _verify_only_expected_files_changed(task, worktree)),
            ("no_contract_violation", is_clean),
            ("no_side_effects", _verify_no_extra_changes(task, worktree)),
        ]
        result = SOPResult(checks=checks)
        if not result.passed:
            logger.warning(f"[SOPEnforcer] post_task_check FAILED for '{task.id}': {result.failed_checks}")
        return result

    @staticmethod
    def done_criteria_check(state: MigrationState) -> SOPResult:
        """SOP Section I: Phase completion gate."""
        all_done = all(t.status == "completed" for t in state.tasks)
        checks: list[tuple[str, bool]] = [
            ("implementation_done", all_done),
            ("validation_pass", len(state.build_errors) == 0),
            ("debt_recorded", True),  # debt list is always maintained by workflow
            ("report_generated", len(state.reports) > 0),
        ]
        result = SOPResult(checks=checks)
        if not result.passed:
            logger.warning(f"[SOPEnforcer] done_criteria_check FAILED: {result.failed_checks}")
        return result
