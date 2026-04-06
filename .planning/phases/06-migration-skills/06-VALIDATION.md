---
phase: 6
slug: migration-skills
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py tests/test_skills_sync.py -v` |
| **Full suite command** | `PYTHONPATH=. python -m pytest tests/ -v` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. python -m pytest tests/test_migration_skills.py tests/test_skills_sync.py -v`
- **After every plan wave:** Run `PYTHONPATH=. python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| skl-01-controller | 06 | 1 | SKL-01 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k controller -v` | ✅ | ✅ green |
| skl-02-webconfig | 06 | 1 | SKL-02 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k webconfig -v` | ✅ | ✅ green |
| skl-03-startup | 06 | 1 | SKL-03 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k startup -v` | ✅ | ✅ green |
| skl-04-auth | 06 | 1 | SKL-04 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k auth -v` | ✅ | ✅ green |
| skl-05-namespace | 06 | 1 | SKL-05 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k namespace -v` | ✅ | ✅ green |
| skl-06-logging | 06 | 1 | SKL-06 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k logging -v` | ✅ | ✅ green |
| skl-07-docker | 06 | 1 | SKL-07 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k docker -v` | ✅ | ✅ green |
| skl-08-nuget | 06 | 1 | SKL-08 | unit | `PYTHONPATH=. python -m pytest tests/test_migration_skills.py -k nuget -v` | ✅ | ✅ green |
| skl-09-sync | 06 | 1 | SKL-09 | unit | `PYTHONPATH=. python -m pytest tests/test_skills_sync.py -v` | ✅ | ✅ green |

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
| Gaps found | 1 |
| Resolved | 1 |
| Escalated | 0 |

### Gap Resolution Summary

- **skl-01..08 strict constraints (MISSING→green):** No tests verified that the strict AI anti-hallucination directives (`DO NOT invent`, `NEVER copy`, etc.) were present in the 8 new skill SKILL.md files. Created `tests/test_migration_skills.py` with 40 parametrized tests covering: file existence, YAML frontmatter structure, `name` field presence, strict constraint presence, and per-skill key content requirements (API mapping tables, placeholder rules, pipeline directives).
