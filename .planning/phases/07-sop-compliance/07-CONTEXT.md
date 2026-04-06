# Phase 7: SOP Compliance - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Encode SOP rules as hard algorithmic checks in Python — no LLM guesswork, deterministic enforcement before/during/after each task.

**Requirements:** SOP-01, SOP-02, SOP-03
**Success criteria:**
1. `SOPEnforcer` statically blocks phase progression on missing requirements.
2. Reporting engine generates Markdown/YAML metrics without hallucinations.
</domain>

<decisions>
## Implementation Decisions

### D-01: SOPResult — Hard Block on Failure (1A)
- When any `SOPEnforcer` check fails, set `workflow_state = "blocked"` and route to `human_gate`. Zero tolerance. Do NOT log-and-continue.
- **FPF Citation:** `E.16:7` — "Guards are **hard** gates; depletion halts further autonomy-gated Work."
- **FPF Citation:** `C.24:5` — "Where scripts encode safety-critical gating or compliance, scripts prevail."

### D-02: Reporting Engine — State-Direct Only (2A)
- `app/utils/reporter.py` receives `MigrationState` and serializes fields directly (`state.tasks`, `state.debt`, `state.build_errors`). Pure Python serialization.
- No LLM calls, no inference, no "chắc ổn" assumptions.
- **FPF Citation:** `B.3:4.2` — "Design-time and run-time SHALL be reported separately and not mixed." Reports must be grounded in explicit typed data.
- **FPF Citation:** `C.25:19.1` — "No report-only proxy may replace the bundle in norms, gates, or endpoint ontology."

### D-03: Extend `TaskItem` Schema (3A)
- Add 4 fields to `TaskItem` in `app/core/state.py` with safe defaults:
  - `source_files: list[str] = Field(default_factory=list)`
  - `target_files: list[str] = Field(default_factory=list)`
  - `done_criteria: str | None = None`
  - `verify_command: str | None = None`
- **FPF Citation:** `B.1.1:6.2` (WLNK) — Always-True checks are a weakest-link failure; the compliance chain integrity is bounded by its weakest check.
- **FPF Citation:** `C.3.2:4` — "Masks must express real constraints and be **deterministically checkable** at guard time."

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source Specs
- `IMPLEMENTATION-PLAN-v2.md` § Phase 6: SOP Compliance Layer — Tasks 6.1 and 6.2 define the exact `SOPEnforcer` check names and `reporter.py` report types.
- `app/core/state.py` — Current `TaskItem` and `MigrationState` definitions; extend `TaskItem` per D-03.
- `app/core/safety.py` — `safety.scan_worktree()` is used inside `post_task_check`; read interface before using.

### Report Types Required (from spec Task 6.2)
1. Phase Summary Report (MD)
2. Task Detail Report (YAML per task)
3. Error & Fix Log (MD)
4. Debt Register (YAML)
5. Endpoint Comparison (MD table)
6. NuGet Mapping Report (MD table)
7. PR Description (MD)
8. Evolution Report (MD — SONA patterns learned)

</canonical_refs>

<deferred>
## Deferred Ideas
None.
</deferred>

---

*Phase: 07-sop-compliance*
*Context gathered: via discuss-phase with Quint Code FPF-grounded comparison*
*FPF citations: E.16:7, C.24:5, B.3:4.2, C.25:19.1, B.1.1:6.2, C.3.2:4*
