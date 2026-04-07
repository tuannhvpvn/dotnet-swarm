# Phase 10: Validation Strategy

**Phase:** 10
**Phase slug:** recursive-csproj-upgrade-engine
**Date:** 2026-04-07

---

## Validation Architecture

### Dimension 1: Unit Coverage
- `test_csproj_resolver.py` tests `resolve_graph()` with:
  - Simple chain (A → B → C)
  - Diamond (A → B, A → C, B → D, C → D)
  - Circular reference (A → B → A — must not recurse infinitely)
  - Missing file (ref path does not exist — should log and skip, not crash)
- `upgrade_target_framework()` tests:
  - Single `<TargetFramework>` → updated
  - `<TargetFrameworks>` (multi-target) → updated
  - Already at target version → no change, `modified=False`
  - Legacy format (`ToolsVersion` present) → `ValueError` raised

### Dimension 2: SLN Parsing Coverage
- `parse_sln()` tests with fixture `.sln` files:
  - Single project
  - Multiple projects
  - No `.csproj` entries (empty) → returns `[]`

### Dimension 3: SOP Hard-Block Integration
- When `ValueError` (legacy format): verify `state.workflow_state == "blocked"`
- When `ET.ParseError`: verify `state.workflow_state == "blocked"`
- Confirm `human_gate` routing is called after block

### Dimension 4: Integration Build Test
- Fixture solution with 2 projects (A depends on B) at `net6.0`
- After upgrade engine runs: both set to `net10.0`
- `dotnet build` exits 0

### Dimension 5: State Mutation
- After resolver runs: `state.resolved_csproj_paths` is a list of normalized absolute paths
- Paths are in dependency order (dependencies before dependents)

---

## Acceptance Baseline

| Check | Command / Assertion |
|---|---|
| Unit tests pass | `pytest tests/utils/test_csproj_resolver.py -v` exits 0 |
| Coverage ≥ 90% | `pytest --cov=app/utils/csproj_resolver --cov-report=term-missing` shows ≥90% |
| State field present | `grep "resolved_csproj_paths" app/core/state.py` |
| Hard block on legacy | Test asserts `state.workflow_state == "blocked"` on ToolsVersion input |
| Integration build | `dotnet build` fixture exits 0 after upgrade |
