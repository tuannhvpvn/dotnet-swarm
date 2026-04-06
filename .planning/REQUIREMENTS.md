# Requirements: dotnet-swarm

**Defined:** 2026-04-06
**Core Value:** Reliable, safe, and autonomous migration of .NET applications without risking production side-effects or hallucinated codebase states, ensuring all steps are verifiable and SOP compliant.

## v1 Requirements

### Foundation

- [x] **FND-01**: Redesign `MigrationState` model to support all task and error tracking fields
- [x] **FND-02**: Upgrade SQLite persistence schema to match new state model
- [x] **FND-03**: Deduplicate and consolidate `auto_skill_creator` logic

### Safety Layer

- [x] **SFE-01**: Implement `SafetyRules` enforcer for file paths, content, SQL, and Git branches
- [x] **SFE-02**: Define configurable absolute safety rules and blacklists in `config/safety.yaml`
- [x] **SFE-03**: Integrate safety checks into Tool Adapter execution and pre-commit steps

### Tool Adapter

- [x] **TAD-01**: Implement custom harness adapters for `omo`, `omx`, `omc`, and `kiro`
- [x] **TAD-02**: Add retry mechanics via `tenacity` for agent tool external calls
- [x] **TAD-03**: Create Jinja2 context injection templates for each internal harness framework
- [x] **TAD-04**: Map task routing configuration via `app/tools/config.yaml`
- [x] **TAD-05**: Reverse engineer undocumented oh-my-* CLI API interfaces

### Graph Redesign

- [x] **GRD-01**: Redesign LangGraph to use `SqliteSaver` and precise workflow nodes (survey, plan, human gate, prepare, migrate, fix, validate, document, etc.)
- [ ] **GRD-02**: Implement `survey_node` to extract accurate target repository inventory
- [ ] **GRD-03**: Implement `plan_node` to decompose inventory into an ordered list of atomic tasks
- [ ] **GRD-04**: Implement `migrate_task_node` to execute individual tasks in a controlled loop
- [ ] **GRD-05**: Implement `checkpoint_node` to do immediate post-task SOP verifications
- [ ] **GRD-06**: Implement `fix_node` for remediation and auto-escalation based on retry limits
- [ ] **GRD-07**: Implement `human_gate_node` utilizing LangGraph `interrupt_before`
- [ ] **GRD-08**: Implement `learn_node` for providing SONA pattern feedback and auto-skill generation
- [x] **GRD-09**: Implement `deliver_node` for Git commits, pushes, and Azure DevOps PR creation

### Ruflo MCP Integration

- [x] **MCP-01**: Create proper MCP adapter `RufloMCPClient` in Python
- [x] **MCP-02**: Automate `ruflo mcp start` background initiation via the `ruflo_start.py` bootloader

### Migration Skills

- [x] **SKL-01**: Write `.migration-skills/dotnet-controller-migration/SKILL.md`
- [x] **SKL-02**: Write `.migration-skills/dotnet-webconfig-to-appsettings/SKILL.md`
- [x] **SKL-03**: Write `.migration-skills/dotnet-startup-migration/SKILL.md`
- [x] **SKL-04**: Write `.migration-skills/dotnet-auth-middleware/SKILL.md`
- [x] **SKL-05**: Write `.migration-skills/dotnet-namespace-replacement/SKILL.md`
- [x] **SKL-06**: Write `.migration-skills/dotnet-logging-adapter/SKILL.md`
- [x] **SKL-07**: Write `.migration-skills/dotnet-docker-setup/SKILL.md`
- [x] **SKL-08**: Write `.migration-skills/dotnet-nuget-mapping/SKILL.md`
- [x] **SKL-09**: Update `sync_skills.py` to copy all new skills

### SOP Compliance

- [x] **SOP-01**: Create `SOPEnforcer` to programmatically validate SOP Sections A, B, E, and I
- [x] **SOP-02**: Generative SOP-formatted reports via `app/utils/reporter.py`
- [x] **SOP-03**: Implement precise state transitions (normal/blocked/remediation)

### Polish & Integration

- [x] **POL-01**: Update Typer CLI `main.py` entry point with resume/status/approve commands
- [x] **POL-02**: Render task-level progress and metrics on Streamlit `dashboard.py`
- [x] **POL-03**: Unify configurations into a standard `config.yaml` schema
- [x] **POL-04**: Create comprehensive integration test suite
- [x] **POL-05**: Cleanup project `.gitignore`
- [x] **POL-06**: Update project documentation (SOP.md, TASK-ROUTING.md, TROUBLESHOOTING.md)

### Audit Housekeeping (v1.0 Gap Closure)

- [ ] **HOK-01**: Fix 12 stale unchecked boxes in REQUIREMENTS.md traceability
- [ ] **HOK-02**: Create VERIFICATION.md stubs for phases 07 and 08
- [ ] **HOK-03**: Run `/gsd-validate-phase 3` — create 03-VALIDATION.md with `nyquist_compliant: true`
- [ ] **HOK-04**: Re-run `/gsd-audit-milestone` and confirm `status: passed`

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
| FND-01 | Phase 1 | Complete |
| FND-02 | Phase 1 | Complete |
| FND-03 | Phase 1 | Complete |
| SFE-01 | Phase 2 | Complete |
| SFE-02 | Phase 2 | Complete |
| SFE-03 | Phase 2 | Complete |
| TAD-01 | Phase 3 | Complete |
| TAD-02 | Phase 3 | Complete |
| TAD-03 | Phase 3 | Complete |
| TAD-04 | Phase 3 | Complete |
| TAD-05 | Phase 3 | Complete |
| GRD-01 | Phase 4 | Complete |
| GRD-02 | Phase 4 | Pending |
| GRD-03 | Phase 4 | Pending |
| GRD-04 | Phase 4 | Pending |
| GRD-05 | Phase 4 | Pending |
| GRD-06 | Phase 4 | Pending |
| GRD-07 | Phase 4 | Pending |
| GRD-08 | Phase 4 | Pending |
| GRD-09 | Phase 4 | Complete |
| MCP-01 | Phase 5 | Complete |
| MCP-02 | Phase 5 | Complete |
| SKL-01 | Phase 6 | Complete |
| SKL-02 | Phase 6 | Pending |
| SKL-03 | Phase 6 | Pending |
| SKL-04 | Phase 6 | Pending |
| SKL-05 | Phase 6 | Pending |
| SKL-06 | Phase 6 | Pending |
| SKL-07 | Phase 6 | Pending |
| SKL-08 | Phase 6 | Pending |
| SKL-09 | Phase 6 | Complete |
| SOP-01 | Phase 7 | Complete |
| SOP-02 | Phase 7 | Complete |
| SOP-03 | Phase 7 | Complete |
| POL-01 | Phase 8 | Complete |
| POL-02 | Phase 8 | Complete |
| POL-03 | Phase 8 | Complete |
| POL-04 | Phase 8 | Complete |
| POL-05 | Phase 8 | Complete |
| POL-06 | Phase 8 | Complete |
| HOK-01 | Phase 9 | Pending |
| HOK-02 | Phase 9 | Pending |
| HOK-03 | Phase 9 | Pending |
| HOK-04 | Phase 9 | Pending |

**Coverage:**
- v1 requirements: 44 total (40 original + 4 HOK)
- Mapped to phases: 44
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-06*
*Last updated: 2026-04-06 after initial definition*
