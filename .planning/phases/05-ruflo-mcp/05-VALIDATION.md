---
phase: 5
slug: ruflo-mcp
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | python/unittest |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `PYTHONPATH=. python tests/test_ruflo_mcp.py` |
| **Full suite command** | `PYTHONPATH=. python tests/test_ruflo_mcp.py` |
| **Estimated runtime** | ~1 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. python tests/test_ruflo_mcp.py`
- **After every plan wave:** Run `PYTHONPATH=. python tests/test_ruflo_mcp.py`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| mcp-01-dependencies | 05 | 1 | MCP-01 | unit | `PYTHONPATH=. python tests/test_ruflo_mcp.py` | ✅ | ✅ green |
| mcp-02-client-rewrite | 05 | 1 | MCP-02 | unit | `PYTHONPATH=. python tests/test_ruflo_mcp.py` | ✅ | ✅ green |

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
