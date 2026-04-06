---
phase: 8
slug: polish-integration
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `PYTHONPATH=. python -m pytest tests/test_polish.py -v` |
| **Full suite command** | `PYTHONPATH=. python -m pytest tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. python -m pytest tests/test_polish.py -v`
- **After every plan wave:** Run `PYTHONPATH=. python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| pol-01-cli | 08 | 1 | POL-01 | unit | `PYTHONPATH=. python -m pytest tests/test_polish.py -k cli -v` | ✅ | ✅ green |
| pol-02-dashboard | 08 | 1 | POL-02 | unit | `PYTHONPATH=. python -m pytest tests/test_polish.py -k dashboard -v` | ✅ | ✅ green |
| pol-03-config | 08 | 1 | POL-03 | unit | `PYTHONPATH=. python -m pytest tests/test_polish.py -k config -v` | ✅ | ✅ green |
| pol-04-gitignore | 08 | 1 | POL-04 | unit | `PYTHONPATH=. python -m pytest tests/test_polish.py -k gitignore -v` | ✅ | ✅ green |
| pol-05-tests | 08 | 1 | POL-05 | integration | `PYTHONPATH=. python -m pytest tests/ -v` | ✅ | ✅ green (94 pre-existing + 22 new = 116 total) |
| pol-06-docs | 08 | 1 | POL-06 | unit | `PYTHONPATH=. python -m pytest tests/test_polish.py -k md -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live Streamlit dashboard rendering | POL-02 | Requires browser + running Streamlit server | Run `streamlit run dashboard.py`, paste a `current_state.json` to `state/`, verify all 7 sections render correctly |
| CLI `resume` end-to-end flow | POL-01 | Requires a real saved SQLite state | Run `start` on a test repo, then kill, then run `resume` — verify it picks up from the saved state |

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
| Gaps found | 4 |
| Resolved | 4 |
| Escalated | 0 |

### Gap Resolution Summary

- **pol-01 CLI (MISSING→green):** No tests verified the 4 CLI commands were registered. Created `tests/test_polish.py` with 5 CLI tests: `test_cli_all_four_commands_registered` (checks all 4 `def` are present), `test_cli_resume_loads_persistence`, `test_cli_status_reads_json_snapshot` (D-02 compliance), `test_cli_approve_writes_human_decision`, and `test_cli_compiles` (AST parse).
- **pol-03 config.yaml (PARTIAL→green):** Only YAML parse was checked. Added 3 tests: `test_config_yaml_has_all_nine_sections` (verifies all 9 required top-level keys), `test_config_migration_section_has_target_framework`, and `test_config_ruflo_section_has_mcp_url`.
- **pol-04 .gitignore (MISSING→green):** No tests for ignored entries. Added 4 tests covering `state/`, `.worktrees/`, `*.db`, and `.env`.
- **pol-06 docs (MISSING→green):** Only `test -f` shell check existed. Added 5 tests: existence of both files, SOP.md covers all 4 gate sections (A/B/E/I) and Human Gate doc, ARCHITECTURE.md covers graph topology and dual-write persistence.
