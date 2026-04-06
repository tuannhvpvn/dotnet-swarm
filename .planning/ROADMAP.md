# Roadmap: dotnet-swarm

## Milestones

- ✅ **v1.0 Foundation & Migration Engine** — Phases 1–9 (shipped 2026-04-06)

## Phases

<details>
<summary>✅ v1.0 Foundation & Migration Engine (Phases 1–9) — SHIPPED 2026-04-06</summary>

- [x] Phase 1: Foundation (1/1 plan) — Redesigned MigrationState + dual-write SQLite/JSON persistence
- [x] Phase 2: Safety Layer (1/1 plan) — SafetyRules enforcer + HarnessAdapter pre-flight/post-scan
- [x] Phase 3: Tool Adapter (1/1 plan) — OOP harness factory for omo/omx/omc/kiro with tenacity retries
- [x] Phase 4: Graph Redesign (1/1 plan) — LangGraph nodes aligned to SOP checklist + SqliteSaver
- [x] Phase 5: Ruflo MCP (1/1 plan) — RufloMCPClient MCP adapter with graceful fallback
- [x] Phase 6: Migration Skills (1/1 plan) — 13 SKILL.md payloads with strict AI constraint tags
- [x] Phase 7: SOP Compliance (1/1 plan) — SOPEnforcer algorithmic gates + MigrationReporter
- [x] Phase 8: Polish & Integration (1/1 plan) — CLI commands, dashboard, 128-test suite, docs
- [x] Phase 9: Audit Housekeeping (1/1 plan) — Nyquist gap closure, REQUIREMENTS.md cleanup

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

## ▶ Next Milestone

Run `/gsd-new-milestone` to define v2.0 requirements and roadmap.

**v2.0 candidates:**
- `learn_node` / SONA auto-skill generation (GRD-08)
- Recursive `.csproj` target framework upgrades (ADV-01)
- Real harness integration test suite (requires omo/omx/omc/kiro in CI)
- Ruflo npm package publishing
