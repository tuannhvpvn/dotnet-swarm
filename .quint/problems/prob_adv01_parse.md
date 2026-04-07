---
id: prob_adv01_parse
title: "Dependency Graph Resolution Strategy"
status: "framed"
created_at: 2026-04-07T15:55:00+07:00
---

# Problem: Dependency Graph Resolution Strategy

## Signal
Phase 10 needs to recursively find all downstream `.csproj` dependencies of a root project to consistently upgrade the `<TargetFramework>` tags. We currently lack a deterministic graph resolution mechanism that adheres to our strict zero-tolerance failure SOP.

## Core Conflict
LLM-based graph resolution hallucinates structure for large dependency trees, but standard CLI options (like `dotnet list reference`) require shell execution and iterative token-heavy AI edits.

## Constraints
1. **Zero Hallucination:** Path resolution must be deterministic (SOP D-01).
2. **Speed & Latency:** Minimizing deep token context loops across 50+ projects.
3. **Execution Domain:** Edits must be isolated so they can be easily rolled back by the `SafetyRules` enforcer.

## Suggested Variants
- **V1: Pure Python XML (Deterministic Orchestration)**
- **V2: CLI Discovery + AI Harness Loop**
- **V3: Pure AI Harness Delegation**
