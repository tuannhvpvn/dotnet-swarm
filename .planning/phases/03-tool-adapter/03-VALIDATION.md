---
phase: 3
slug: tool-adapter
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `PYTHONPATH=. python -m pytest tests/test_tool_adapter.py tests/test_harness_adapter.py tests/test_adapter_mock.py -v` |
| **Full suite command** | `PYTHONPATH=. python -m pytest tests/ -v` |
| **Estimated runtime** | ~8 seconds (includes tenacity retry delay) |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. python -m pytest tests/test_tool_adapter.py tests/test_harness_adapter.py tests/test_adapter_mock.py -v`
- **After every plan wave:** Run `PYTHONPATH=. python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| tad-01-requirements | 03 | 1 | TAD-01 | unit | `PYTHONPATH=. python -m pytest tests/test_tool_adapter.py::test_tenacity_in_requirements -v` | ✅ | ✅ green |
| tad-02-harness-executors (OOP structure) | 03 | 1 | TAD-02 | unit | `PYTHONPATH=. python -m pytest tests/test_tool_adapter.py -k "base_class or four_concrete or factory" -v` | ✅ | ✅ green |
| tad-02-harness-executors (retry) | 03 | 1 | TAD-03 | unit | `PYTHONPATH=. python -m pytest tests/test_tool_adapter.py::test_harness_retry_appends_error_to_task -v` | ✅ | ✅ green |
| tad-02-harness-executors (sidecar injection) | 03 | 1 | TAD-04 | unit | `PYTHONPATH=. python -m pytest tests/test_tool_adapter.py -k "sidecar or inject" -v` | ✅ | ✅ green |
| tad-02-harness-executors (CLI routing) | 03 | 1 | TAD-05 | unit | `PYTHONPATH=. python -m pytest tests/test_tool_adapter.py -k "routes_by_key or defaults_to_omo" -v` | ✅ | ✅ green |
| SFE-03 integration (safety in adapter) | 03 | 1 | SFE-03 | unit | `PYTHONPATH=. python -m pytest tests/test_harness_adapter.py -v` | ✅ | ✅ green |
| MCP adapters (disabled returns silently) | 03 | 1 | TAD-01 | unit | `PYTHONPATH=. python -m pytest tests/test_adapter_mock.py -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real harness invocation (omo/omx/omc/kiro) | TAD-02/05 | Requires external CLI binaries not installed in dev env | On a system with harnesses installed, run `python -c "from app.tools.adapter import call_harness; call_harness({'harness': 'omo', 'task': 'test', 'worktree': '/tmp'})"` and verify non-zero exit produces retry |

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
| Gaps found | 5 |
| Resolved | 5 |
| Escalated | 0 |

### Gap Resolution Summary

- **tad-01 (MISSING→green):** No test verified `tenacity` was in `requirements.txt`. Added `test_tenacity_in_requirements`.
- **tad-02 OOP structure (MISSING→green):** No tests verified `HarnessExecutor` base class or 4 concrete subclasses existed. Added `test_harness_executor_base_class_exists` and `test_four_concrete_harness_classes_exist`.
- **tad-03 retry error context (MISSING→green):** No test verified that on subprocess failure, the error was appended to `task_spec['task']` before tenacity retried. Added `test_harness_retry_appends_error_to_task` — patches subprocess.run to always return returncode=1, verifies error string appears in task and retry count ≥ 2.
- **tad-04 sidecar injection (MISSING→green):** No tests for `_write_sidecar` or `_inject_context`. Added `test_write_sidecar_creates_file` (uses temp dir) and `test_inject_context_writes_skills_sidecar` (mocks `_write_sidecar`, verifies called).
- **tad-05 CLI routing (MISSING→green):** No tests verified `call_harness()` routes to the correct CLI binary for each harness key. Added 5 parametrized tests (omo/omc/omx/kiro + unknown-key fallback), capturing `subprocess.run` call args to verify first element is the correct binary.
