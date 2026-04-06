# Requirements: dotnet-swarm

**Defined:** 2026-04-06
**Core Value:** Reliable, safe, and autonomous migration of .NET applications without risking production side-effects or hallucinated codebase states, ensuring all steps are verifiable and SOP compliant.

## v1 Requirements

### Foundation

- [ ] **FND-01**: Redesign `MigrationState` model to support all task and error tracking fields
- [ ] **FND-02**: Upgrade SQLite persistence schema to match new state model
- [ ] **FND-03**: Deduplicate and consolidate `auto_skill_creator` logic

### Safety Layer

- [ ] **SFE-01**: Implement `SafetyRules` enforcer for file paths, content, SQL, and Git branches
- [ ] **SFE-02**: Define configurable absolute safety rules and blacklists in `config/safety.yaml`
- [ ] **SFE-03**: Integrate safety checks into Tool Adapter execution and pre-commit steps

### Tool Adapter

- [ ] **TAD-01**: Implement custom harness adapters for `omo`, `omx`, `omc`, and `kiro`
- [ ] **TAD-02**: Add retry mechanics via `tenacity` for agent tool external calls
- [ ] **TAD-03**: Create Jinja2 context injection templates for each internal harness framework
- [ ] **TAD-04**: Map task routing configuration via `app/tools/config.yaml`
- [ ] **TAD-05**: Reverse engineer undocumented oh-my-* CLI API interfaces

### Graph Redesign

- [ ] **GRD-01**: Redesign LangGraph to use `SqliteSaver` and precise workflow nodes (survey, plan, human gate, prepare, migrate, fix, validate, document, etc.)
- [ ] **GRD-02**: Implement `survey_node` to extract accurate target repository inventory
- [ ] **GRD-03**: Implement `plan_node` to decompose inventory into an ordered list of atomic tasks
- [ ] **GRD-04**: Implement `migrate_task_node` to execute individual tasks in a controlled loop
- [ ] **GRD-05**: Implement `checkpoint_node` to do immediate post-task SOP verifications
- [ ] **GRD-06**: Implement `fix_node` for remediation and auto-escalation based on retry limits
- [ ] **GRD-07**: Implement `human_gate_node` utilizing LangGraph `interrupt_before`
- [ ] **GRD-08**: Implement `learn_node` for providing SONA pattern feedback and auto-skill generation
- [ ] **GRD-09**: Implement `deliver_node` for Git commits, pushes, and Azure DevOps PR creation

### Ruflo MCP Integration

- [ ] **MCP-01**: Create proper MCP adapter `RufloMCPClient` in Python
- [ ] **MCP-02**: Automate `ruflo mcp start` background initiation via the `ruflo_start.py` bootloader

### Migration Skills

- [ ] **SKL-01**: Write `.migration-skills/dotnet-controller-migration/SKILL.md`
- [ ] **SKL-02**: Write `.migration-skills/dotnet-webconfig-to-appsettings/SKILL.md`
- [ ] **SKL-03**: Write `.migration-skills/dotnet-startup-migration/SKILL.md`
- [ ] **SKL-04**: Write `.migration-skills/dotnet-auth-middleware/SKILL.md`
- [ ] **SKL-05**: Write `.migration-skills/dotnet-namespace-replacement/SKILL.md`
- [ ] **SKL-06**: Write `.migration-skills/dotnet-logging-adapter/SKILL.md`
- [ ] **SKL-07**: Write `.migration-skills/dotnet-docker-setup/SKILL.md`
- [ ] **SKL-08**: Write `.migration-skills/dotnet-nuget-mapping/SKILL.md`
- [ ] **SKL-09**: Update `sync_skills.py` to copy all new skills

### SOP Compliance

- [ ] **SOP-01**: Create `SOPEnforcer` to programmatically validate SOP Sections A, B, E, and I
- [ ] **SOP-02**: Generative SOP-formatted reports via `app/utils/reporter.py`
- [ ] **SOP-03**: Implement precise state transitions (normal/blocked/remediation)

### Polish & Integration

- [ ] **POL-01**: Update Typer CLI `main.py` entry point with resume/status/approve commands
- [ ] **POL-02**: Render task-level progress and metrics on Streamlit `dashboard.py`
- [ ] **POL-03**: Unify configurations into a standard `config.yaml` schema
- [ ] **POL-04**: Create comprehensive integration test suite
- [ ] **POL-05**: Cleanup project `.gitignore`
- [ ] **POL-06**: Update project documentation (SOP.md, TASK-ROUTING.md, TROUBLESHOOTING.md)

## v2 Requirements

(Deferred to a future release, not in current roadmap).

### Advanced

- **ADV-01**: Support for automatically updating `.NET` target frameworks recursively

## Out of Scope

| Feature | Reason |
|---------|--------|
| Migrating to non-C# frameworks | Out of scope for this automation tool |
| Local LLM running (e.g. Ollama via local interface) | The orchestration assumes external harnesses manage their own model access |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01 | Phase 1 | Pending |
| FND-02 | Phase 1 | Pending |
| FND-03 | Phase 1 | Pending |
| SFE-01 | Phase 2 | Pending |
| SFE-02 | Phase 2 | Pending |
| SFE-03 | Phase 2 | Pending |
| TAD-01 | Phase 3 | Pending |
| TAD-02 | Phase 3 | Pending |
| TAD-03 | Phase 3 | Pending |
| TAD-04 | Phase 3 | Pending |
| TAD-05 | Phase 3 | Pending |
| GRD-01 | Phase 4 | Pending |
| GRD-02 | Phase 4 | Pending |
| GRD-03 | Phase 4 | Pending |
| GRD-04 | Phase 4 | Pending |
| GRD-05 | Phase 4 | Pending |
| GRD-06 | Phase 4 | Pending |
| GRD-07 | Phase 4 | Pending |
| GRD-08 | Phase 4 | Pending |
| GRD-09 | Phase 4 | Pending |
| MCP-01 | Phase 5 | Pending |
| MCP-02 | Phase 5 | Pending |
| SKL-01 | Phase 6 | Pending |
| SKL-02 | Phase 6 | Pending |
| SKL-03 | Phase 6 | Pending |
| SKL-04 | Phase 6 | Pending |
| SKL-05 | Phase 6 | Pending |
| SKL-06 | Phase 6 | Pending |
| SKL-07 | Phase 6 | Pending |
| SKL-08 | Phase 6 | Pending |
| SKL-09 | Phase 6 | Pending |
| SOP-01 | Phase 7 | Pending |
| SOP-02 | Phase 7 | Pending |
| SOP-03 | Phase 7 | Pending |
| POL-01 | Phase 8 | Pending |
| POL-02 | Phase 8 | Pending |
| POL-03 | Phase 8 | Pending |
| POL-04 | Phase 8 | Pending |
| POL-05 | Phase 8 | Pending |
| POL-06 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 40 total
- Mapped to phases: 40
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-06*
*Last updated: 2026-04-06 after initial definition*
