# Phase 6: Migration Skills - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Define standard `.NET` modernization payloads so that the swarm can properly translate Phase 1 syntax changes autonomously.

**Requirements:** SKL-01 to SKL-09
**Success criteria:**
1. All 8 standard missing Phase 1 migration core skills defined clearly in `.migration-skills` structure.
2. `sync_skills.py` successfully injects files logic to deployment directories without breaking previous dependencies.
</domain>

<decisions>
## Implementation Decisions

### Formatting Constraints in SKILL.md (1A)
- **D-01:** Implement `Strict/Authoritative` structures. All 8 new Phase 1 skills must explicitly demand the `omx` and `omc` agents limit their replacements *only* to the defined namespaces or variables in the tables, effectively disabling AI hallucination padding. Example rule format: *"DO NOT invent namespaces, use EXACTLY the mapping table provided."*

### Legacy Skills Handling (2A)
- **D-02:** Append to Existing Base. When modifying `app/utils/sync_skills.py`, do NOT overwrite the `SKILLS` array. Keep the 5 legacy skills active for cross-phase robustness, resulting in 13 total `SKILL.md` bundles synced concurrently via `shutil`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source Specs
- `IMPLEMENTATION-PLAN-v2.md` § Phase 5: Migration Skills (Tasks 5.1-5.9) - Lists all explicit `Deliverables` directory names and `Content` attributes needed for the new skills.
- `app/utils/sync_skills.py` — File responsible for distribution.

</canonical_refs>

<deferred>
## Deferred Ideas
None.
</deferred>

---

*Phase: 06-migration-skills*
*Context gathered: via discuss-phase and Quint FPF comparison*
