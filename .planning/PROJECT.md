# dotnet-migration-swarm

## What This Is

A Queen-led autonomous agent swarm for automating .NET codebase migrations. It utilizes a LangGraph workflow, integrates with multiple MCPs (Ruflo, GitNexus, VibeKanban), and orchestrates external AI harnesses. The current focus is moving the prototype to a production-ready state by fixing review issues and enforcing Standard Operating Procedure (SOP) compliance.

## Core Value

Reliable, safe, and autonomous migration of .NET applications without risking production side-effects or hallucinated codebase states, ensuring all steps are verifiable and SOP compliant.

## Requirements

### Validated

- ✓ LangGraph-based workflow architecture (prototype) — existing
- ✓ Integration adapters for GitNexus and VibeKanban — existing
- ✓ Basic CLI interface via Typer — existing
- ✓ Isolated execution via Git Worktrees — existing
- ✓ Complete Phase 1: Foundation (Redesign `MigrationState` and Persistence SQL schema) — Validated in Phase 1: Foundation
- ✓ Complete Phase 2: Safety Layer (Pre-flight checks to prevent unwanted destructive actions) — Validated in Phase 2: Safety Layer
- ✓ Complete Phase 3: Tool Adapter Rewrite (Robustly interface with omo, omx, omc, kiro with retries) — Validated in Phase 3: Tool Adapter
- ✓ Complete Phase 4: Graph Redesign (Fully align nodes and edges to the SOP checklist and human gates) — Validated in Phase 4: Graph Redesign

### Active
- [ ] Complete Phase 5: Migration Skills (Package `.migration-skills/` payload)
- [ ] Complete Phase 6: SOP Compliance Layer (Checklist enforcers and precise reporting)
- [ ] Complete Phase 7: Polish & Integration (Dashboard updates, comprehensive test suite)

### Out of Scope

- Support for languages other than .NET (C#) — Core scope is strictly .NET migration.
- Developing alternative proprietary harnesses — The project focuses on orchestrating existing external CLI harnesses (omo, omx, omc).
- Advanced GUI implementation — Focus remains on CLI and lightweight Streamlit dashboard observability.

## Context

- The project relies on external LLM CLIs (`omo`, `omx`, `omc`) accessible via `$PATH`.
- Deep queries to existing .NET solution repos depend heavily on the `GitNexus` knowledge graph.
- The `v2.0` push is driven by the need to resolve prototype review feedback, heavily emphasizing Safety and SOP adherence.

## Constraints

- **Technology**: Must use Python 3.12+, LangGraph, and Pydantic v2.
- **Safety**: No operations may touch blacklisted folders (e.g., `keys/`, `certs/`) or contain hardcoded keys (Regex scanned).
- **Execution**: The process must support a Human Gate (interactive pause/resume) between critical phases.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| SQLite over JSON | Need better relational tracking for tasks and error records across execution loops | — Pending |
| Multi-agent LangGraph Redesign | SOP requires discrete phases (survey, plan, human review, single-task loops, checkpts) | — Pending |
| Delegating execution to local harness tools | Maximizes flexibility for context injections without bloating this Python runtime | — Pending |

---
*Last updated: 2026-04-06 after Phase 1 completion*
## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state
