---
phase: 7
slug: sop-compliance
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `PYTHONPATH=. python -m pytest tests/test_sop.py tests/test_state.py tests/test_reporter.py -v` |
| **Full suite command** | `PYTHONPATH=. python -m pytest tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. python -m pytest tests/test_sop.py tests/test_state.py tests/test_reporter.py -v`
- **After every plan wave:** Run `PYTHONPATH=. python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| sop-01-extend-taskitem | 07 | 1 | SOP-01 | unit | `PYTHONPATH=. python -m pytest tests/test_state.py::test_taskitem_sop_fields -v` | ✅ | ✅ green |
| sop-02-enforcer (pre_phase) | 07 | 1 | SOP-02 | unit | `PYTHONPATH=. python -m pytest tests/test_sop.py::test_pre_phase_fail_empty -v` | ✅ | ✅ green |
| sop-02-enforcer (pre_task) | 07 | 1 | SOP-02 | unit | `PYTHONPATH=. python -m pytest tests/test_sop.py -k pre_task -v` | ✅ | ✅ green |
| sop-02-enforcer (post_task) | 07 | 1 | SOP-02 | unit | `PYTHONPATH=. python -m pytest tests/test_sop.py -k post_task -v` | ✅ | ✅ green |
| sop-02-enforcer (done_criteria) | 07 | 1 | SOP-02 | unit | `PYTHONPATH=. python -m pytest tests/test_sop.py::test_done_criteria_fail_no_reports -v` | ✅ | ✅ green |
| sop-03-reporter | 07 | 1 | SOP-03 | unit | `PYTHONPATH=. python -m pytest tests/test_reporter.py -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-06

---

## Validation Audit 2026-04-06

| Metric | Count |
|--------|-------|
| Gaps found | 3 |
| Resolved | 3 |
| Escalated | 0 |

### Gap Resolution Summary

- **sop-02 / post_task_check (MISSING→green):** `post_task_check` was not tested at all. Added `test_post_task_check_fail_opens_in_non_git_environment` (mocking `SafetyRules` at source so the lazy import is intercepted correctly) and `test_post_task_check_has_three_checks` verifying all three SOP gate names are present.
- **sop-03 / MigrationReporter methods (MISSING→green):** Created `tests/test_reporter.py` with 16 behavioral tests covering all 7 reporter methods, verifying values are sourced from `MigrationState` fields (state-direct, no inference), `generate_all()` returns all 6 types, and `state.reports` is populated enabling `done_criteria_check`.
- **sop-03 / generate_all → state.reports (MISSING→green):** Covered by `test_generate_all_populates_state_reports` and `test_done_criteria_passes_after_generate_all`.
