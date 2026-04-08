# Milestone v2.0 Requirements

## recursive-upgrade

- [ ] **ADV-01**: The system must parse a target `.sln` or `.csproj` file to definitively resolve all internal project references in its dependency graph, recursively.
- [ ] **ADV-02**: The `MigrateTaskNode` (or a dedicated phase logic) must update the `<TargetFramework>` tag for the entry project and all its transitively referenced `.csproj` files to the target framework (e.g., `net8.0`).
- [ ] **ADV-03**: The orchestrator must successfully compile the root solution/project (`dotnet build`) using `validator_node` explicitly after the recursive upgrade to verify structural integrity.

## auto-skill

- [ ] **GRD-08**: The orchestrator must include a scaffolded `learn_node` that executes after successful migration phases to persist a successful code modification pattern (SONA) to history.

## Future Requirements

- Real CI harness integration testing
- Generating custom migration skills automatically using LLMs analyzing the history (delayed to v2.1 or v3.0)

## Out of Scope

- Support for non-C# .NET languages
- Advanced GUI implementation for SONA auto-skill (beyond basic CLI/Streamlit telemetry updates)

---

## Traceability

- **ADV-01** → Phase 10
- **ADV-02** → Phase 10
- **ADV-03** → Phase 10
- **GRD-08** → Phase 11
