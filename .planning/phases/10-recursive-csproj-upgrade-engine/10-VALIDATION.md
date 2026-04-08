# Phase 10: Validation Strategy

**Phase:** 10
**Phase slug:** recursive-csproj-upgrade-engine
**Date:** 2026-04-07
**Audit date:** 2026-04-08
**nyquist_compliant:** true

---

## Test Infrastructure

| Framework | Config | Command |
|---|---|---|
| pytest | `pyproject.toml` | `python -m pytest tests/utils/test_csproj_resolver.py -v` |
| pytest-cov | `pyproject.toml` | `python -m pytest --cov=app.utils.csproj_resolver --cov-report=term-missing` |

---

## Per-Task Requirement Map

| Task ID | Requirement | Test File | Status |
|---|---|---|---|
| 10-01 | D1: `parse_sln()` — single/multi/empty/.sln | `test_csproj_resolver.py::TestParseSln` | ✅ COVERED |
| 10-01 | D1: `resolve_graph()` — chain, diamond, circular, missing | `TestResolveGraph` (7 tests) | ✅ COVERED |
| 10-01 | D1: `upgrade_target_framework()` — single `<TargetFramework>` | `TestUpgradeTargetFramework` | ✅ COVERED |
| 10-01 | D1: `upgrade_target_framework()` — `<TargetFrameworks>` multi-target | `test_upgrades_multi_target_frameworks_tag` | ✅ COVERED |
| 10-01 | D1: Already at target → `modified=False` | `test_no_change_when_already_at_target` | ✅ COVERED |
| 10-01 | D1: Legacy ToolsVersion → `ValueError` | `test_legacy_format_raises_value_error` (×2) | ✅ COVERED |
| 10-02 | D5: `resolved_csproj_paths` field in `MigrationState` | `TestPreflightCsprojUpgrade::test_preflight_success_sets_resolved_paths` | ✅ COVERED |
| 10-03 | D3: SOP hard-block — legacy csproj → `workflow_state="blocked"` | `test_hardblock_on_legacy_csproj` | ✅ COVERED |
| 10-03 | D3: SOP hard-block — corrupt XML → `workflow_state="blocked"` | `test_hardblock_on_corrupt_xml` | ✅ COVERED |
| 10-03 | D3: SOP hard-block — missing path → `workflow_state="blocked"` | `test_hardblock_on_missing_solution` | ✅ COVERED |
| 10-01 | D1: `upgrade_solution()` — full chain upgrade | `TestUpgradeSolution` (2 tests) | ✅ COVERED |

---

## Acceptance Baseline

| Check | Command / Assertion | Result |
|---|---|----|
| Unit tests pass | `pytest tests/utils/test_csproj_resolver.py -v` exits 0 | ✅ 26/26 passed |
| Coverage ≥ 90% | `pytest --cov=app.utils.csproj_resolver --cov-report=term-missing` | ✅ 97% |
| State field present | `grep "resolved_csproj_paths" app/core/state.py` | ✅ line 73 |
| Hard block on legacy | Test asserts `state.workflow_state == "blocked"` on ToolsVersion input | ✅ verified |
| Hard block on corrupt XML | Test asserts `state.workflow_state == "blocked"` on ET.ParseError | ✅ verified |
| State paths populated | Test asserts `len(state.resolved_csproj_paths) == 2` after success | ✅ verified |

---

## Manual-Only Items

| Item | Reason |
|---|---|
| D4: `dotnet build` fixture integration test | `dotnet` SDK not installed in test environment |

---

## Validation Audit 2026-04-08

| Metric | Count |
|---|---|
| Gaps found | 3 |
| Resolved (automated) | 3 |
| Escalated to manual | 0 |

**Gaps fixed:**
1. `<TargetFrameworks>` multi-target tag — added `test_upgrades_multi_target_frameworks_tag`
2. SOP D3 hard-block contract (ValueError) — added `TestPreflightCsprojUpgrade::test_hardblock_on_legacy_csproj`
3. SOP D3 hard-block contract (ET.ParseError, OSError) — added 2 additional `TestPreflightCsprojUpgrade` tests + D5 `resolved_csproj_paths` assertion
