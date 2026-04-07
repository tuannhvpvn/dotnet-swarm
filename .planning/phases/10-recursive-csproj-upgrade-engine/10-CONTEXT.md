# Phase 10: Recursive `.csproj` Upgrade Engine - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement deterministic discovery, parsing, and multi-project framework upgrading for `.NET` target references recursively, to automate dependency-aware framework solution upgrades across large trees.
</domain>

<decisions>
## Implementation Decisions

### Resolution Strategy
- **D-01:** Implement **Pure Python XML Parsing** within the orchestrator natively (`xml.etree`). Do NOT delegate graph discovery to AI harnesses to satisfy strict safe zero-hallucination tolerance (SOP D-01).

### Editor Role
- **D-02:** The orchestrator will parse and map the graph, but it will *also* mutate the `<TargetFramework>` tags directly rather than relying on sequential external harness requests. Since this is a simple XML edit, latency is reduced from multi-minute token limits to <1s.

### Format Support
- **D-03:** Focus exclusively on reading and mutating **modern SDK-style `.csproj` configurations** for Phase 10 (target framework standard tag layouts). If legacy attributes like `ToolsVersion="15.0"` are hit, we flag/bail out to the Human Gate rather than attempting legacy upgrades.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### FPF Decisions
- `.quint/problems/prob_adv01_parse.md` — Framed problem limits and options
- `.quint/decisions/dec_adv01_parse.md` — Formal locked decision contract for Python XML tree evaluation

### Standards
No external specs — requirements fully captured in decisions above.
</canonical_refs>
