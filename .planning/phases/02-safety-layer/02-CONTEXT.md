# Phase 2: Safety Layer - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the safety enforcement layer that prevents any migration harness from modifying blacklisted files/folders or committing sensitive content. Must be in place BEFORE any real migration execution.

**Requirements:** SFE-01, SFE-02, SFE-03
**Success criteria:**
1. `SafetyRules` block operations on `keys/` or restricted files.
2. All 3 execution vectors (path, content, git) trigger violation correctly.
</domain>

<decisions>
## Implementation Decisions

### Interception Strategy — Defense in Depth (1A+1B Combined)
- **D-01 (Primary Gate — Git Hook):** Dynamically generate a `.git/hooks/pre-commit` script in the worktree that invokes `SafetyRules.check_pre_commit()`. Harness commits are blocked at the git level with zero blast radius.
- **D-02 (Secondary Check — Post-Execution Scan):** Run `SafetyRules.scan_worktree()` immediately after every `call_harness()` subprocess returns. If violations are found in the working tree (files created but not yet committed), execute `git checkout -- .` to discard changes, log the violation to `state.safety_violations`, and mark the task as failed.
- **D-03 (Soft Layer — Prompt Injection):** Parse `config/safety.yaml` absolute rules into text and inject them into the harness prompt context (e.g., `CLAUDE.md` or task description) to reduce the frequency of violations reaching the hard gates.

### Adapter Architecture — Generic Harness Adapter (2A)
- **D-04:** Create `app/core/harness_adapter.py` as a wrapper around the existing `call_harness()` in `app/tools/adapter.py`. The new adapter handles: pre-flight safety checks, git hook installation, subprocess delegation, post-execution scan, and violation logging.
- **D-05:** All 4 agent nodes (`surveyor`, `phase1_migrator`, `phase2_modernizer`, `validator`) will import from the new adapter instead of `app/tools/adapter.py` directly. The old `call_harness()` remains as the low-level subprocess executor.

### Agent's Discretion
- Internal structure of `SafetyResult` dataclass (fields, severity levels).
- Hook script template format (bash vs python shim).
- Whether `scan_worktree` uses `pathlib.glob` or `os.walk`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source Specs
- `IMPLEMENTATION-PLAN-v2.md` § Phase 1: Safety Layer — Task 1.1, 1.2, 1.3 definitions and exact class/method signatures.
- `app/tools/adapter.py` — Current `call_harness()` implementation (subprocess wrapper, 80 lines).
- `app/core/state.py` — `MigrationState.safety_violations` field for violation logging.

### Codebase References
- `app/agents/surveyor.py`, `phase1_migrator.py`, `phase2_modernizer.py`, `validator.py` — All 4 callers of `call_harness()` that must be re-routed.
</canonical_refs>

<deferred>
## Deferred Ideas

- Retry logic and model selection in adapter — belongs to Phase 3 (Tool Adapter Rewrite).
- SQL injection detection in `check_sql()` — low priority, Oracle queries are read-only in current scope.
</deferred>

---

*Phase: 02-safety-layer*
*Context gathered: 2026-04-06 via discuss-phase*
