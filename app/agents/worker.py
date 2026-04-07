import subprocess
from collections import Counter
from datetime import datetime

from app.core.state import MigrationState, DebtItem, TaskItem
from app.core.harness_adapter import harness as harness_adapter
from app.core.sop import SOPEnforcer
from app.core.auto_skill_creator import AutoSkillCreator
from app.tools.adapter import call_harness
from app.utils.worktree import create_worktree
from app.integrations.vibekanban_adapter import vibekanban
from app.core.ruflo_mcp import ruflo_client
from rich.console import Console
from loguru import logger

console = Console()


# ── Shared helpers ────────────────────────────────────────────────────────────

def _current_task(state: MigrationState) -> TaskItem | None:
    return next((t for t in state.tasks if t.id == state.current_task_id), None)


def _build_task_spec(task: TaskItem, state: MigrationState, task_description: str | None = None) -> dict:
    return {
        "harness": task.harness,
        "command": task.command,
        "task": task_description or task.description or task.title,
        "worktree": state.worktree_path or state.solution_path,
        "source_files": task.source_files,
        "skills": [],
    }


def _all_deps_completed(task: TaskItem, state: MigrationState) -> bool:
    if not task.depends_on:
        return True
    completed_ids = {t.id for t in state.tasks if t.status == "completed"}
    return all(dep_id in completed_ids for dep_id in task.depends_on)


def _execute_harness(task_spec: dict, state: MigrationState) -> dict:
    if harness_adapter:
        return harness_adapter.execute(task_spec, state)
    return call_harness(task_spec)


def _update_task_result(task: TaskItem, result: dict) -> None:
    if result["returncode"] == 0:
        task.status = "completed"
        task.completed_at = datetime.now()
    else:
        task.status = "failed"
        task.error_message = result.get("stderr", "")[:500]


# ── Nodes ─────────────────────────────────────────────────────────────────────

def human_gate_node(state: MigrationState) -> MigrationState:
    """No-op node. LangGraph pauses here via interrupt_before."""
    console.print("[bold yellow]⛔ Human Gate: Đợi phê duyệt...[/]")
    return state


def prepare_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Worker", "🟢 Preparing", progress=10)
    if not state.worktree_path:
        state.worktree_path = create_worktree(state.solution_path, "migration")
    console.print("[green]✅ Prepare hoàn tất[/]")
    return state


def migrate_task_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Migrator", "🟢 Migrating", progress=40)

    pending_task = next(
        (t for t in state.tasks if t.status in ["pending", "failed"] and _all_deps_completed(t, state)),
        None,
    )
    if not pending_task:
        console.print("[bold cyan]Không còn tasks nào cần migrate.[/]")
        return state

    console.print(f"[bold magenta]🚀 Migrating Task: {pending_task.title}[/]")
    state.current_task_id = pending_task.id
    pending_task.status = "in_progress"
    pending_task.started_at = datetime.now()
    pending_task.attempt_count += 1

    result = _execute_harness(_build_task_spec(pending_task, state), state)
    _update_task_result(pending_task, result)
    return state


def checkpoint_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Checkpoint", "🟢 Analyzing", progress=80)

    task = _current_task(state)
    if not task:
        return state

    worktree = state.worktree_path or state.solution_path

    # SOPEnforcer.post_task_check is the single authority for scope + safety checks.
    # It internally runs SafetyRules.scan_worktree — no need to re-scan here.
    sop_result = SOPEnforcer.post_task_check(task, worktree)

    # Supplementary Ruflo review (non-blocking, informational only)
    try:
        reasoning = ruflo_client.get_reasoning(
            f"Review worktree for task {state.current_task_id}. Deviations?"
        )
        console.print(f"[bold cyan]🔍 Ruflo Audit: {reasoning[:150]}[/]")
    except Exception:
        pass

    if sop_result.passed:
        state.workflow_state = "normal"
        console.print(f"[bold green]✅ Checkpoint passed for task {task.id}[/]")
    else:
        # Copy before appending to avoid fragile aliasing if SOPResult changes internals
        failed = [*sop_result.failed_checks]
        logger.warning(f"Checkpoint failed: {failed}")
        task.status = "failed"
        task.error_message = f"Checkpoint failed: {failed}"
        state.workflow_state = "remediation"
        console.print(f"[bold red]❌ Checkpoint failed: {failed}[/]")

    return state


def fix_node(state: MigrationState) -> MigrationState:
    vibekanban.update_agent("Worker", "🟢 Fixing", progress=90)

    task = _current_task(state)
    if not task:
        return state

    if task.attempt_count >= task.max_attempts:
        task.status = "escalated"
        state.debt.append(DebtItem(
            id=f"debt-{task.id}",
            description=f"Cannot auto-fix: {task.error_message}",
            file=task.source_files[0] if task.source_files else None,
            severity="high",
            phase=state.current_phase,
        ))
        console.print(f"[bold red]⛔ Escalated task {task.id} after {task.attempt_count} attempts[/]")
        logger.warning(f"Task {task.id} escalated to debt after {task.attempt_count} attempts")
        return state

    # Capture error before it may be overwritten by _update_task_result
    error_before_fix = task.error_message or ""
    task.fix_history.append({
        "attempt": task.attempt_count,
        "error": error_before_fix,
        "timestamp": datetime.now().isoformat(),
    })

    task.status = "in_progress"
    task.attempt_count += 1
    state.fix_attempts += 1  # global aggregate across all tasks; per-task limit is task.attempt_count
    console.print(f"[bold magenta]🛠️ Fix attempt {task.attempt_count} for: {task.title}[/]")

    fix_prompt = (
        f"{task.description or task.title}\n\n"
        f"Previous attempt failed with error:\n{error_before_fix}\n"
        f"Fix this error."
    )
    result = _execute_harness(_build_task_spec(task, state, fix_prompt), state)
    _update_task_result(task, result)

    # Learn the error→fix pair regardless of outcome (the error is the training signal)
    try:
        ruflo_client.learn_pattern(state, error_before_fix, result.get("stdout", "")[:500])
    except Exception as e:
        logger.warning(f"Ruflo pattern learning failed: {e}")

    return state


def learn_node(state: MigrationState) -> MigrationState:
    """SONA feedback + auto skill creation after successful validation."""
    vibekanban.update_agent("Learner", "🟢 Learning", progress=85)

    task = _current_task(state)
    if not task:
        return state

    for fix in task.fix_history:
        try:
            ruflo_client.learn_pattern(
                state, fix.get("error", ""), f"Fixed on attempt {fix.get('attempt')}"
            )
        except Exception as e:
            logger.warning(f"Ruflo pattern learning failed for fix entry: {e}")

    error_counts = Counter(
        t.error_message[:80].strip()
        for t in state.tasks
        if t.error_message
    )

    creator = AutoSkillCreator()
    for pattern, count in error_counts.items():
        if count >= 3:
            skill_name = f"auto-fix-{pattern[:20].replace(' ', '-').lower()}"
            examples = [
                {"error": t.error_message, "task": t.title}
                for t in state.tasks if t.error_message and pattern in t.error_message
            ]
            try:
                creator.create_skill(skill_name, f"Auto fix for: {pattern}", examples)
                logger.info(f"Auto-created skill for repeated pattern: {pattern[:50]}")
            except Exception as e:
                logger.warning(f"Auto-skill creation failed for '{skill_name}': {e}")

    console.print(f"[bold cyan]🧠 Learn node completed for task {task.id}[/]")
    return state


def deliver_node(state: MigrationState) -> MigrationState:
    """Git commit and push with safety pre-commit check."""
    vibekanban.update_agent("Deliverer", "🟢 Delivering", progress=95)

    worktree = state.worktree_path or state.solution_path

    # Safety check on staged files before committing
    try:
        safety = harness_adapter.safety if harness_adapter else None
        if safety:
            staged_result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=worktree, capture_output=True, text=True, timeout=10
            )
            staged = [f.strip() for f in staged_result.stdout.splitlines() if f.strip()]
            violations = safety.check_pre_commit(staged)
            if violations:
                for v in violations:
                    logger.error(f"Pre-commit violation: [{v.rule_id}] {v.message}")
                    state.safety_violations.append({
                        "rule_id": v.rule_id,
                        "severity": v.severity,
                        "message": v.message,
                        "file_path": v.file_path,
                    })
                console.print(f"[bold red]🚫 Delivery blocked: {len(violations)} safety violation(s)[/]")
                return state
    except Exception as e:
        logger.warning(f"Safety pre-commit check skipped: {e}")

    # Stage only files produced by completed tasks in the current phase; fall back to -A
    phase_files = [
        f for t in state.tasks
        if t.status == "completed" and t.phase == state.current_phase
        for f in t.target_files
    ]
    if phase_files:
        subprocess.run(["git", "add", "--"] + phase_files, cwd=worktree, capture_output=True, timeout=30)
    else:
        subprocess.run(["git", "add", "-A"], cwd=worktree, capture_output=True, timeout=30)

    commit_msg = f"forge(migration): {state.current_phase} [{state.migration_id}]"
    try:
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=worktree, capture_output=True, text=True, timeout=30
        )
        logger.info(f"Committed: {commit_msg}")
        console.print(f"[bold green]✅ Committed: {commit_msg}[/]")
    except Exception as e:
        logger.error(f"Git commit failed: {e}")

    try:
        subprocess.run(
            ["git", "push", "-u", "origin", "HEAD"],
            cwd=worktree, capture_output=True, text=True, timeout=60
        )
        logger.info("Pushed to remote")
        console.print("[bold green]✅ Pushed to remote[/]")
    except Exception as e:
        logger.warning(f"Git push failed (non-critical): {e}")

    return state
