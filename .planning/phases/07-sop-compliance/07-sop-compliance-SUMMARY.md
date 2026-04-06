# Plan Summary: 07-sop-compliance

## What Was Built

Encoded SOP rules as deterministic Python gate checks — no LLM inference anywhere.

- **`app/core/state.py`** — Extended `TaskItem` with 4 SOP-required fields: `source_files`, `target_files`, `done_criteria`, `verify_command`. All have safe defaults, zero breaking changes.
- **`app/core/sop.py`** — New `SOPEnforcer` class with 4 static check methods covering SOP Sections A, B, E, I. `SOPResult` dataclass with computed `passed` and `failed_checks` properties. Git-diff-based scope verification helpers (fail-open in non-git environments). Corrected the spec bug: `safety.scan_worktree()` returns `list[SafetyResult]` not `.is_clean`.
- **`app/utils/reporter.py`** — New `MigrationReporter` class with 6 report-type methods. All values sourced directly from `MigrationState` fields. `generate_all()` populates `state.reports` enabling the `done_criteria_check` gate.
- **`app/core/__init__.py`** — Converted graph imports to lazy wrappers to decouple from `langgraph-checkpoint-sqlite` at import time.
- **`app/utils/__init__.py`** — Updated to export `MigrationReporter` class (replacing stale function names).

## Key Decisions Applied (from D-01/02/03)
- D-01: Hard block — `SOPResult.passed == False` → callers must set `workflow_state = "blocked"`
- D-02: State-direct — zero LLM calls, zero inferred strings
- D-03: `TaskItem` extended — pre-task checks are now real WLNK-bounded gates

## Verification
- All 3 modules pass `py_compile`
- SOPEnforcer: empty state fails correctly, full task passes correctly
- Reporter: all 6 report types generated from state fields, `state.reports` populated

<key-files>
<modified>
app/core/state.py
app/core/sop.py (NEW)
app/utils/reporter.py (REWRITE)
app/core/__init__.py
app/utils/__init__.py
</modified>
</key-files>
