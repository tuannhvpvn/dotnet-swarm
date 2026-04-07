# Roadmap v2.0 Core Advancements

## Overview

**2 phases** | **4 requirements mapped**

| #  | Phase                                 | Goal                                                                                         | Requirements           | Success Criteria |
|----|---------------------------------------|----------------------------------------------------------------------------------------------|------------------------|------------------|
| 10 | Recursive `.csproj` Upgrade Engine    | Implement recursive discovery, parsing, and multi-project framework upgrading of `.NET` apps | ADV-01, ADV-02, ADV-03 | 3                |
| 11 | `learn_node` & SONA Logging Framework | Introduce the `learn_node` to LangGraph for recording successful migration patterns          | GRD-08                 | 2                |

---

## Phase Details

### Phase 10: Recursive `.csproj` Upgrade Engine

**Goal:** Automate dependency-aware upgrades by recursing through ProjectReference elements to update entire solutions coherently.

**Requirements:**
- **ADV-01**: Parse target `.sln` or `.csproj` to definitively resolve all internal project references in its dependency graph, recursively.
- **ADV-02**: Update the `<TargetFramework>` tag for the entry project and all transitively referenced `.csproj` files to the target framework.
- **ADV-03**: Successfully compile the root solution/project after the recursive upgrade to verify structural integrity.

**Success criteria:**
1. Given a root `.sln` or `.csproj` file, orchestrator can parse and return a complete list of valid local `<ProjectReference>` paths.
2. Given a target `.NET` framework (e.g. `net8.0`), all correctly resolved `.csproj` files in the graph have their `<TargetFramework>` tags upgraded.
3. The `validator_node` successfully runs `dotnet build` without runtime reference mismatch errors.

---

### Phase 11: `learn_node` & SONA Logging Framework

**Goal:** Lay the foundation for autonomous skill generation by tracking successful interventions across state cycles.

**Requirements:**
- **GRD-08**: The orchestrator must include a scaffolded `learn_node` that executes after successful migration phases to persist a successful code modification pattern (SONA).

**Success criteria:**
1. A new `learn_node` is correctly integrated into the core `LangGraph` topology, reachable upon validation success.
2. The node saves basic contextual data (e.g., node input/output diff signals, state metadata) to the execution history.
