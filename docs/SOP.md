# SOP — Standard Operating Procedure

> **Authoritative enforcement document.** These gates are implemented in `app/core/sop.py` as deterministic Python checks. No LLM inference is used in any gate evaluation.

## Section A: Pre-Phase Checks (`SOPEnforcer.pre_phase_check`)

Before any migration phase begins, all three conditions must be True:

| Check | Condition |
|---|---|
| `goal_defined` | `state.plan is not None` |
| `scope_locked` | `len(state.tasks) > 0` |
| `worktree_set` | `state.worktree_path is not None` |

**On failure:** `workflow_state = "blocked"`, `blocked_reason` set, route to Human Gate.

---

## Section B: Pre-Task Checks (`SOPEnforcer.pre_task_check`)

Before delegating any task to the AI harness, all six conditions must be True:

| Check | Condition |
|---|---|
| `task_small_enough` | `len(task.source_files) <= 5` |
| `single_deliverable` | `task.done_criteria is not None` |
| `input_clear` | `len(task.source_files) > 0` |
| `output_clear` | `len(task.target_files) > 0` |
| `verify_step_defined` | `task.verify_command is not None` |
| `timeout_set` | Always True (enforced by config) |

**On failure:** `workflow_state = "blocked"`, task not delegated to harness.

---

## Section E: Post-Task Checks (`SOPEnforcer.post_task_check`)

After harness completes a task, all three conditions must be True:

| Check | Condition |
|---|---|
| `scope_correct` | Only expected `target_files` changed (via `git diff`) |
| `no_contract_violation` | `len(safety_rules.scan_worktree(worktree)) == 0` |
| `no_side_effects` | No unexpected files in `git status --porcelain` |

**On failure:** `workflow_state = "remediation"`, fix loop triggered.  
**Fail-open rule:** Subprocess errors in git checks return `True` (CI safety).

---

## Section I: Done-Criteria Checks (`SOPEnforcer.done_criteria_check`)

Before a phase is considered complete, all four conditions must be True:

| Check | Condition |
|---|---|
| `implementation_done` | All tasks have `status == "completed"` |
| `validation_pass` | `len(state.build_errors) == 0` |
| `debt_recorded` | Always True (debt list maintained throughout) |
| `report_generated` | `len(state.reports) > 0` |

**On failure:** Phase cannot advance. Report generated with gap analysis.

---

## Human Gate

The Human Gate is triggered when `workflow_state == "blocked"`. The swarm pauses and surfaces the `blocked_reason` to the operator.

**Operator actions:**
```bash
# View current block reason
python main.py status /path/to/solution

# Approve and continue
python main.py approve /path/to/solution --decision approve

# Reject (abort phase)
python main.py approve /path/to/solution --decision reject
```

After `approve`, run `python main.py resume /path/to/solution` to continue.
