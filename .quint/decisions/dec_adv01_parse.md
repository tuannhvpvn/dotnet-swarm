---
id: dec_adv01_parse
problem: prob_adv01_parse
title: "Pure Python XML Orchestration for CSPROJ graph"
status: "locked"
created_at: 2026-04-07T15:57:00+07:00
---

# Decision: Pure Python XML Orchestration

## Rationale
To guarantee the strict zero-tolerance failure criteria from `SOP D-01`, delegating graph resolution to an AI harness introduces unacceptable non-determinism. By implementing standard `xml.etree` parsing natively inside the LangGraph `migrate_task_node` or pre-flight phase, we achieve sub-second graph resolution parsing with 100% path accuracy.

## Consequences
- **Positive:** Immune to AI hallucination or missing paths deep in the tree.
- **Negative:** Takes some responsibility away from the AI harnesses, making the orchestrator slightly more tightly coupled to `.csproj` XML structures.
- **Trade-off accepted:** We prioritize safety and execution reliability over pure AI delegation across the board.
