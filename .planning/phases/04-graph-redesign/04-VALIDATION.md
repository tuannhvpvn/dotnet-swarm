---
phase: 4
slug: graph-redesign
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `PYTHONPATH=. python -m pytest tests/test_graph.py tests/test_planner.py tests/test_worker.py -v` |
| **Full suite command** | `PYTHONPATH=. python -m pytest tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. python -m pytest tests/test_graph.py tests/test_planner.py tests/test_worker.py -v`
- **After every plan wave:** Run `PYTHONPATH=. python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| grd-01-deprecate | 04 | 1 | GRD-01 | unit | `PYTHONPATH=. python -m pytest tests/test_graph.py -v` | ✅ | ✅ green |
| grd-02-planner | 04 | 1 | GRD-02 | unit | `PYTHONPATH=. python -m pytest tests/test_planner.py -v` | ✅ | ✅ green |
| grd-03-worker | 04 | 1 | GRD-03 | unit | `PYTHONPATH=. python -m pytest tests/test_worker.py -v` | ✅ | ✅ green |
| grd-04-graph-logic | 04 | 1 | GRD-04/05 | unit | `PYTHONPATH=. python -m pytest tests/test_graph.py -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Human Approval Gate (interactive) | GRD-07 | Requires stdin interaction at runtime | Start `run_migration()` with a real solution path, verify the graph pauses at `human_gate` and only continues after `y` input |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-06

---

## Validation Audit 2026-04-06

| Metric | Count |
|--------|-------|
| Gaps found | 4 |
| Resolved | 4 |
| Escalated | 0 |

### Gap Resolution Summary

- **grd-01-deprecate / GRD-01** (PARTIAL→green): `test_build_graph_compiles` was SKIPPED due to `documenter.py` importing non-existent free functions (`generate_phase_report`, `generate_task_report`, `generate_evolution_report`). Fixed by rewriting `documenter.py` to use the `MigrationReporter` class methods that exist in `reporter.py`. Also fixed `build_migration_graph()` — was using `settings.solution_path` (doesn't exist in `Settings` model) and `SqliteSaver.from_conn_string()` wrong (returns context manager, not a direct saver). Refactored to accept `checkpointer` param with `MemorySaver` fallback; `run_migration()` now manages the `SqliteSaver` context.
- **grd-02-planner / GRD-02** (PARTIAL→green): `test_planner_node_returns_state` was SKIPPED. Fixed wrong import (`planner_node` → `plan_node`).
- **grd-03-worker / GRD-03** (MISSING→green): No tests for worker nodes existed. Created `tests/test_worker.py` with 8 behavioral tests covering `human_gate_node`, `prepare_node`, `migrate_task_node` (success/failure/no-pending), `checkpoint_node`, and `fix_node`.
- **grd-04-graph-logic / GRD-04/05** (PARTIAL→green): Covered by `test_build_graph_compiles` once the import chain was fixed. Graph now compiles with all 10 nodes and correct `interrupt_before=["human_gate"]`.
