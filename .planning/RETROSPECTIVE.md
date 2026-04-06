# Retrospective

## Milestone: v1.0 — Foundation & Migration Engine

**Shipped:** 2026-04-06  
**Phases:** 9 | **Plans:** 9 | **Timeline:** 1 day  
**Tests:** 128 passing | **LOC:** 2,822 Python

### What Was Built

- Granular `MigrationState` + dual-write SQLite/JSON persistence with full round-trip fidelity
- `SafetyRules` enforcer with pre-flight path/content/SQL/git checks and post-execution worktree scan + automatic git rollback
- OOP `HarnessExecutor` factory for 4 AI CLI tools with `tenacity` retry loop and sidecar context injection
- SOP-aligned LangGraph nodes: `human_gate_node`, `migrate_task_node`, `checkpoint_node`, `fix_node`, `deliver_node`
- `RufloMCPClient` MCP adapter with graceful npm-unavailable fallback
- 13 `.migration-skills/` SKILL.md payloads with strict AI anti-hallucination directives; synchronized to all harness directories
- Algorithmic `SOPEnforcer` (4 deterministic gate methods) + state-direct `MigrationReporter` (7 report types, zero LLM inference)
- Full observability surface: Typer CLI (start/resume/status/approve), Streamlit dashboard, 9-section `config.yaml`, SOP+Architecture docs

### What Worked

- **Nyquist validation workflow** — Running `/gsd-validate-phase` for each phase caught ~20 real gaps (missing tests) that would have remained hidden. The 5-second feedback loop constraint kept test quality high.
- **Algorithmic SOPEnforcer** — Choosing deterministic field inspection over LLM inference for compliance gates removed an entire class of reliability concerns.
- **Fail-open git verification** — Designing `post_task_check` to return `True` in non-git environments made the system CI-safe without any special configuration.
- **Sidecar context injection** — Avoiding POSIX argument length limits (E2BIG) by writing skills/rules to files before harness invocation was the right call for large skill payloads.
- **Dual-write persistence** — SQLite for checkpointing + JSON snapshot for Streamlit polling avoids file-locking conflicts elegantly.

### What Was Inefficient

- **Stale REQUIREMENTS.md checkboxes** — 12 requirements were completed but not checked off during phase execution, requiring a dedicated Phase 9 housekeeping step. Phase execution should update REQUIREMENTS.md atomically.
- **Missing VERIFICATION.md for phases 07 and 08** — These were executed before the VERIFICATION convention was established. Retroactive stubs were needed.
- **GRD-02..07 checkbox drift** — VERIFICATION.md said "passed" but REQUIREMENTS.md had unchecked boxes. The 3-source cross-reference in `/gsd-audit-milestone` caught this, but it required manual reconciliation.
- **`state.plan` type ambiguity** — The `plan` field is `dict | None` but it's easy to accidentally assign a string. Caught during E2E integration check; should be a TypedDict or Pydantic model.

### Patterns Established

- **Nyquist compliance as a validation gate** — Every phase must have a VALIDATION.md with `nyquist_compliant: true` before the milestone can pass audit.
- **State-direct reporting** — All report generation reads exclusively from `MigrationState` fields; no LLM calls in reporting paths.
- **Fail-open for external dependencies** — Any gate that depends on an external binary (git, npm, harness CLIs) must fail-open to keep the orchestrator operational.
- **Sidecar injection > CLI arg concatenation** — Write large context (skills, rules) to files before invoking subprocesses.

### Key Lessons

1. Run `/gsd-validate-phase` for every phase, not just the ones that feel complex — the "simple" phases (tool-adapter, polish) had the most gaps.
2. Update REQUIREMENTS.md checkboxes during phase execution, not after audit.
3. VERIFICATION.md and VALIDATION.md serve different purposes — one verifies phase goals, the other verifies test coverage continuity. Both are needed.
4. Design for graceful degradation from the start: external dependencies (ruflo npm, omo CLI, git) will be unavailable in many environments.

### Cost Observations

- Model: Gemini 2.5 Pro (single model, all phases)
- Sessions: 1 session (full milestone)
- Notable: 9 phases in 1 day is achievable when phases are well-scoped (2-4 tasks each) and test infrastructure is established early

---

## Cross-Milestone Trends

| Milestone | Phases | Plans | Tests | LOC | Days |
|-----------|--------|-------|-------|-----|------|
| v1.0 | 9 | 9 | 128 | 2,822 | 1 |

| Pattern | First seen | Status |
|---------|-----------|--------|
| Nyquist per-phase validation | v1.0 | ✓ Established |
| State-direct reporting | v1.0 | ✓ Established |
| Fail-open external deps | v1.0 | ✓ Established |
| Sidecar context injection | v1.0 | ✓ Established |
