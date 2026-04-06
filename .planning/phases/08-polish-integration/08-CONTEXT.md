# Phase 8: Polish & Integration — Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

The final milestone phase. Ship a production-ready CLI, updated Streamlit dashboard, unified config, integration tests, and documentation.

**Requirements:** POL-01 to POL-06
**Success criteria:**
1. Typer CLI: `start`, `resume`, `status`, `approve` commands work end-to-end.
2. Streamlit Dashboard displays live task-level metrics from updated JSON schema.
3. Critical integration paths have test coverage passing `pytest tests/ -v`.
</domain>

<decisions>
## Implementation Decisions

### D-01: Test Strategy — Critical-Path Integration + Mocks (B)
- Tests for MCPs (`gitnexus_adapter`, `vibekanban_adapter`, `ruflo_mcp`) use **mocked HTTP/stdio calls**.
- Tests for core system paths use **real objects** (no mocks):
  - `test_graph.py` — must call `build_migration_graph()` and verify it compiles without error; verify edge routing functions return expected node names.
  - `test_persistence.py` — must do a real SQLite save/load round-trip with a `MigrationState` object.
  - `test_state.py` — real `MigrationState` construction, field access, `model_dump()` round-trip.
  - `test_safety.py` — real `SafetyRules` with `config/safety.yaml`.
  - `test_sop.py` — real `SOPEnforcer` with populated and empty `TaskItem`/`MigrationState`.
- **FPF Citation:** `A.9:2` — "Unit-tested module fails once integrated." Critical integration paths (graph wiring, state persistence) must be exercised with real objects.

### D-02: Dashboard — JSON Polling with Updated Field Keys (A)
- Keep `dashboard.py` as a polling loop reading `state/current_state.json`.
- Update dashboard field reads to match new `MigrationState` schema:
  - Replace legacy agent name list with `state.get("tasks", [])` task list display.
  - Add `build_errors`, `debt`, `safety_violations`, `fix_attempts`, `workflow_state` sections.
  - Add `tasks` table with status icons: `completed=✅`, `failed=❌`, `in_progress=🔄`, `pending=⏳`.
- Do NOT import `MigrationPersistence` into `dashboard.py` — keep process isolation.
- **FPF (E.16 SoD):** Process isolation between dashboard and swarm ensures observability survives migration crashes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Files to Read Before Implementing
- `main.py` — existing CLI; needs `resume`, `status`, `approve` commands added.
- `dashboard.py` — existing dashboard; update field keys to new schema only (keep polling architecture).
- `app/core/state.py` — current `MigrationState` and `TaskItem` schemas (source of truth for dashboard field keys).
- `app/core/persistence.py` — `MigrationPersistence` interface (for `status` and `resume` CLI commands).
- `app/core/sop.py` — `SOPEnforcer` (for `test_sop.py`).
- `app/core/safety.py` — `SafetyRules` (for `test_safety.py`).
- `config/safety.yaml` — required by `SafetyRules` in tests.
- `IMPLEMENTATION-PLAN-v2.md` § Phase 7: Task 7.1–7.6 — full spec for all deliverables.

### Config Schema Target
`config.yaml` must be updated with the full schema from spec Task 7.3 (migration, safety, tools, vibekanban, ruflo, gitnexus, git, session, logging sections).

### Test Files Required (from spec Task 7.4)
- `tests/test_state.py`
- `tests/test_safety.py`
- `tests/test_sop.py`
- `tests/test_graph.py`
- `tests/test_adapter_mock.py`
- `tests/test_persistence.py`
- `tests/test_planner.py`
- `tests/test_skills_sync.py`
- `tests/fixtures/` — sample data files

</canonical_refs>

<deferred>
## Deferred Ideas
- Live WebSocket push from swarm to dashboard (instead of polling) — deferred, out of scope for v1.0.
- Full end-to-end test against a real .NET project — deferred, requires external fixture.
</deferred>

---

*Phase: 08-polish-integration*
*Context gathered: via discuss-phase with Quint Code FPF analysis*
*FPF citations: A.9:2 (integration failure mode), E.16 SoD (process isolation)*
