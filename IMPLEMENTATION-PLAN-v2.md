# 🔨 .NET Migration Swarm — Implementation Plan v2.0

> **Mục tiêu:** Fix toàn bộ issues từ review, align với SOP, đưa project từ prototype → production-ready.
> **Ước lượng:** 7 phases, ~45 tasks

---

## Phase 0: Foundation — State & Data Model
**Mục tiêu:** Xây nền tảng data model đúng trước khi sửa bất kỳ thứ gì khác.
**Lý do ưu tiên:** Mọi component đều phụ thuộc vào state model — sửa sau sẽ cascade changes.

### Task 0.1 — Redesign `MigrationState` (`app/core/state.py`)
**Deliverable:** File `state.py` mới với đầy đủ fields
**Changes:**
```
Thêm fields:
- inventory: dict | None              # Survey output (dependency graph, endpoints, NuGet packages)
- plan: dict | None                    # Migration plan (đã approve)
- tasks: list[TaskItem]                # Danh sách tasks đã decompose
- current_task_id: str | None          # Task ID đang thực thi
- current_tier: int = 0                # Dependency tier hiện tại
- build_errors: list[BuildError]       # Lỗi build hiện tại
- fix_attempts: int = 0                # Đếm retry cho task hiện tại
- max_fix_attempts: int = 5            # Giới hạn retry
- debt: list[DebtItem]                 # SOP: tracking debt rõ ràng
- blocked_reason: str | None           # SOP: blocked state reason
- workflow_state: Literal["normal", "blocked", "remediation"]
- human_decision: Literal["pending", "approve", "modify", "reject"] | None
- reports: list[str]                   # Generated report file paths
- safety_violations: list[dict]        # Log vi phạm safety rules
- worktree_path: str | None            # (rename từ git_worktree)
- session_id: str                      # Cho LangGraph checkpointer
```

**Thêm sub-models:**
```python
class TaskItem(BaseModel):
    id: str
    phase: str                          # survey|phase1|phase2
    type: str                           # csproj_conversion|nuget_migration|controller_migration|...
    title: str
    description: str
    source_files: list[str]             # Files input
    target_files: list[str]             # Files output
    status: Literal["pending","in_progress","completed","failed","skipped","blocked","escalated"]
    tier: int = 0                       # Dependency tier
    depends_on: list[str] = []          # Task IDs
    harness: str                        # omo|omc|omx|kiro
    model_tier: str                     # low|standard|high
    command: str                        # autopilot|team|ralph|ultrawork
    attempt_count: int = 0
    max_attempts: int = 5
    error_message: str | None = None
    fix_history: list[dict] = []
    verify_command: str | None = None   # SOP: "verify bằng cách nào"
    done_criteria: str | None = None    # SOP: "done khi nào"
    started_at: datetime | None = None
    completed_at: datetime | None = None

class BuildError(BaseModel):
    code: str                           # CS0234, NU1101, ...
    message: str
    file: str
    line: int | None = None
    category: str                       # missing_reference|missing_member|nuget|config|...
    auto_fixable: bool = False

class DebtItem(BaseModel):
    id: str
    description: str
    file: str | None = None
    severity: Literal["low", "medium", "high"]
    phase: str
    created_at: datetime
```

**Xóa fields thừa:**
```
- phase_progress: Dict[str, float]     # Thay bằng computed từ tasks
- completed_tasks: List[Dict]          # Thay bằng tasks với status filter
- failed_tasks: List[Dict]             # Thay bằng tasks với status filter
```

**Verify:** Unit test validate model creation, serialization, deserialization.

---

### Task 0.2 — Upgrade persistence (`app/core/persistence.py`)
**Deliverable:** Persistence tương thích state mới + SQLite schema mở rộng
**Changes:**
```
- Thêm bảng `tasks` riêng (không chỉ embed trong state JSON)
- Thêm bảng `error_log` cho Sage/SONA learning
- Thêm bảng `knowledge_patterns` cho auto-learned patterns
- Thêm bảng `agent_log` cho metrics
- Migration script cho schema cũ → mới
- save()/load() tương thích MigrationState mới
```

**Verify:** Test save → load round-trip với state đầy đủ fields.

---

### Task 0.3 — Xóa duplicate `auto_skill_creator.py`
**Deliverable:** Chỉ giữ 1 file tại `app/core/auto_skill_creator.py`
**Changes:**
```
- Xóa app/utils/auto_skill_creator.py
- Update app/utils/__init__.py: import từ app.core
- Grep toàn project, fix mọi import
```

**Verify:** `python -c "from app.utils import auto_skill_creator"` pass.

---

## Phase 1: Safety Layer
**Mục tiêu:** Implement safety rules TRƯỚC KHI chạy bất kỳ migration nào.
**Lý do ưu tiên:** Project truy vấn Oracle production DB — không có safety = risk cao.

### Task 1.1 — Tạo `app/core/safety.py`
**Deliverable:** Module safety rules enforcement
**Changes:**
```python
# Implement:
class SafetyRules:
    blacklist_folders: list[str]        # keys/, certs/, pgp/, ssl/, ...
    blacklist_files: list[str]          # *.pfx, *.pem, *.key, ...
    blacklist_content: list[re.Pattern] # password=, BEGIN RSA PRIVATE KEY, ...
    protected_branches: list[str]       # main, master, production
    forbidden_sql: list[str]           # INSERT, UPDATE, DELETE, DROP, ...

    def check_file_path(path: str) -> SafetyResult
    def check_file_content(content: str) -> SafetyResult
    def check_sql(sql: str) -> SafetyResult
    def check_branch(branch: str) -> SafetyResult
    def check_pre_commit(staged_files: list[str]) -> list[SafetyResult]
    def scan_worktree(worktree_path: str) -> list[SafetyResult]
```

**Verify:** Unit tests cho mỗi check function — positive và negative cases.

---

### Task 1.2 — Tạo `config/safety.yaml`
**Deliverable:** Configurable safety rules
**Changes:**
```yaml
absolute_rules:
  - id: SAFE-001
    rule: "NEVER execute SQL write operations"
    severity: critical
  - id: SAFE-002
    rule: "NEVER modify blacklisted files"
    severity: critical
  # ... 7 rules tổng cộng

blacklist:
  folders: ["**/keys/", "**/certs/", "**/pgp/", "**/ssl/", "**/.vs/"]
  files: ["*.pfx", "*.pem", "*.key", "*.p12", "*.cer", "*.pgp", "*.snk"]
  content_patterns: ["password=", "BEGIN RSA PRIVATE KEY", "connectionString="]

git_safety:
  protected_branches: ["main", "master", "production"]
```

**Verify:** SafetyRules loads config correctly.

---

### Task 1.3 — Integrate safety vào Tool Adapter
**Deliverable:** Safety check TRƯỚC mỗi harness call
**Changes:**
```
- adapter.py gọi SafetyRules.check_file_path() trước khi modify file
- adapter.py gọi SafetyRules.scan_worktree() trước mỗi commit
- Log safety violations vào state.safety_violations
- HALT execution nếu critical violation
```

**Verify:** Test: gọi adapter với path chứa "keys/" → blocked.

---

## Phase 2: Tool Adapter Rewrite
**Mục tiêu:** Adapter gọi đúng oh-my-* harnesses, có retry, skill injection.
**Lý do ưu tiên:** Adapter sai = không chạy được gì cả.

### Task 2.1 — Research oh-my-* CLI interfaces
**Deliverable:** File `docs/harness-interfaces.md` documenting đúng CLI API cho mỗi tool
**Changes:**
```
Cần xác minh cho mỗi harness:
- oh-my-claudecode (cc): Có --print mode? Headless? Pipe stdin?
  - Cách inject CLAUDE.md context
  - $autopilot, $team, $ralph syntax chính xác
- oh-my-codex (omx): Interactive hay one-shot?
  - Cách inject AGENTS.md
  - $ralph, $team syntax
- oh-my-opencode (omo): Dynamic model selection cách nào?
  - .sisyphus/rules/ format
  - ultrawork mode
- kiro-cli: --headless mode? Rules injection?
  - .kiro/rules/ format
```

**Verify:** Manual test mỗi harness với 1 simple task.

---

### Task 2.2 — Rewrite `app/tools/adapter.py`
**Deliverable:** Adapter hoạt động thực tế với oh-my-* tools
**Changes:**
```python
# Thay thế hoàn toàn call_harness()

class HarnessAdapter:
    def __init__(self, safety: SafetyRules):
        self.safety = safety
        self.harnesses = {
            "omc": ClaudeCodeHarness(),
            "omx": CodexHarness(),
            "omo": OpenCodeHarness(),
            "kiro": KiroHarness(),
        }

    def execute(self, task: TaskItem, worktree: str, skills: list[str]) -> TaskResult:
        # 1. Safety check
        # 2. Inject context (CLAUDE.md / AGENTS.md / .kiro/rules)
        # 3. Inject migration skills
        # 4. Execute with retry (tenacity)
        # 5. Parse output
        # 6. Verify result (SOP checkpoint)
        # 7. Return structured result

class ClaudeCodeHarness:
    """Adapter cho oh-my-claudecode"""
    def inject_context(self, worktree: str, task: TaskItem): ...
    def execute(self, task: TaskItem, worktree: str) -> TaskResult: ...
    # Sử dụng claude --print hoặc cc $autopilot "..."

class CodexHarness:
    """Adapter cho oh-my-codex"""
    # Sử dụng omx hoặc codex --quiet

class OpenCodeHarness:
    """Adapter cho oh-my-opencode"""
    # Sử dụng omo ultrawork hoặc tương đương

class KiroHarness:
    """Adapter cho kiro-cli"""
    # Inject .kiro/rules/, execute
```

**Verify:** Integration test gọi 1 harness thực tế với 1 simple .csproj conversion.

---

### Task 2.3 — Thêm retry với tenacity
**Deliverable:** Retry logic cho adapter calls
**Changes:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    retry=retry_if_result(lambda r: r.returncode != 0)
)
def execute_with_retry(self, task, worktree, skills): ...
```

**Verify:** Test retry khi harness fail lần 1, succeed lần 2.

---

### Task 2.4 — Context injection templates
**Deliverable:** Template files cho mỗi harness type
**Changes:**
```
templates/
├── claude-code-context.md.j2     # CLAUDE.md template với task vars
├── codex-agents.md.j2            # AGENTS.md template
├── opencode-agents.md.j2         # AGENTS.md cho opencode
├── kiro-rule.md.j2               # .kiro/rules/ template
└── task-prompt.md.j2             # Shared task description template
```

Sử dụng Jinja2 để render context với: task details, safety rules, migration patterns, known errors, dependency info.

**Verify:** Render template với sample task, check output hợp lệ.

---

### Task 2.5 — Tạo `app/tools/config.yaml`
**Deliverable:** Task type → harness mapping configuration
**Changes:**
```yaml
task_routing:
  # Survey
  survey_scan:
    harness: omo
    model_tier: low
    command: ultrawork
    timeout: 300

  # Phase 1 tasks
  csproj_conversion:
    harness: omx
    model_tier: standard
    command: "$ralph"
    timeout: 180
    skills: [dotnet-phase1-csproj-upgrade]

  nuget_migration:
    harness: omx
    model_tier: standard
    command: "$team 2:executor"
    timeout: 180

  controller_migration:
    harness: omc
    model_tier: high
    command: "$autopilot"
    timeout: 300
    skills: [dotnet-phase1-csproj-upgrade]

  config_migration:
    harness: kiro
    model_tier: standard
    timeout: 180
    skills: [dotnet-phase1-csproj-upgrade]

  auth_migration:
    harness: omc
    model_tier: high
    command: "$autopilot"
    timeout: 300

  oracle_migration:
    harness: omc
    model_tier: high
    command: "$autopilot"
    timeout: 300
    skills: [dotnet-oracle-ef6-migration]

  ef6_migration:
    harness: omc
    model_tier: high
    command: "$autopilot"
    timeout: 300
    skills: [dotnet-oracle-ef6-migration]

  startup_migration:
    harness: omc
    model_tier: high
    command: "$autopilot"
    timeout: 300

  namespace_update:
    harness: omx
    model_tier: low
    command: "$team 3:executor"
    timeout: 120

  logging_migration:
    harness: kiro
    model_tier: standard
    timeout: 180

  docker_setup:
    harness: omo
    model_tier: low
    command: ultrawork
    timeout: 120

  build_validate:
    harness: omo
    model_tier: low
    command: ultrawork
    timeout: 120

  error_fix:
    harness: omc
    model_tier: high
    command: "$autopilot"
    timeout: 300

  documentation:
    harness: omo
    model_tier: low
    command: ultrawork
    timeout: 120

  # Phase 2 tasks
  domain_analysis:
    harness: omc
    model_tier: high
    command: "$ultrapilot"
    timeout: 600

  clean_arch_scaffold:
    harness: omc
    model_tier: high
    command: "$team 4:architect"
    timeout: 600
    skills: [dotnet-clean-arch-cqrs]

  cqrs_migration:
    harness: omc
    model_tier: high
    command: "$team 4:executor"
    timeout: 600
    skills: [dotnet-clean-arch-cqrs, dotnet-ddd-value-objects]

fallback_chain: [omc, omx, omo, kiro]
```

**Verify:** Load config, lookup task type → correct harness.

---

## Phase 3: Graph Redesign
**Mục tiêu:** LangGraph graph đúng workflow SOP.
**Lý do ưu tiên:** Graph sai = workflow sai = mọi thứ sai.

### Task 3.1 — Redesign `app/core/graph.py`
**Deliverable:** Graph hoàn toàn mới theo SOP workflow
**Changes:**
```
Nodes mới:
- survey_node          # Scout scan codebase → inventory
- plan_node            # Decompose tasks → task list
- human_gate_node      # LangGraph interrupt_before
- prepare_node         # Setup worktree, copy templates
- migrate_task_node    # Execute SINGLE task (loop controller)
- validate_node        # dotnet build + endpoint verify
- fix_node             # Fix errors (Ralph Loop)
- checkpoint_node      # SOP: review scope, check lệch spec
- document_node        # Generate reports
- deliver_node         # Git commit, push, create PR
- learn_node           # SONA feedback + auto skill creation

Edges:
START → survey
survey → plan
plan → human_gate                     # ⛔ interrupt_before
human_gate → prepare                  # (if approve)
human_gate → plan                     # (if modify)
human_gate → END                      # (if reject)
prepare → migrate_task
migrate_task → checkpoint             # SOP: review sau mỗi task
checkpoint → validate                 # (if scope OK)
checkpoint → migrate_task             # (if lệch spec, redo)
validate → fix                        # (if build fail & attempts < max)
validate → learn → migrate_task       # (if build pass & more tasks)
validate → learn → document           # (if build pass & no more tasks)
fix → validate                        # (retry build)
fix → escalate_node                   # (if max attempts)
document → deliver
deliver → END

Conditional edges:
- route_after_human: approve|modify|reject
- route_after_checkpoint: pass|redo|escalate
- route_after_validate: fix|next_task|document
- route_after_fix: retry|escalate
- has_more_tasks: yes → migrate_task | no → document
```

**Quan trọng:**
```python
# Dùng SqliteSaver thay MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("state/migration.db")

# Dùng interrupt_before cho human gate
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_gate_node"]
)
```

**Verify:**
- Graph compiles
- Graph renders (graph.get_graph().draw_mermaid())
- Dry run với mock adapter

---

### Task 3.2 — Implement `survey_node` (`app/agents/surveyor.py`)
**Deliverable:** Node trả về inventory đúng format
**Changes:**
```
Output inventory phải chứa:
- solutions: list of .sln paths
- projects: list of { name, type, framework, csproj_path, csproj_style, references }
- dependency_graph: { project → [dependencies] }
- migration_order: [ { tier: 1, projects: [...] }, { tier: 2, ... } ]
- nuget_packages: list of { id, version, status, new_package }
- patterns: { di_framework, orm, oracle, stored_procedures, auth, logging }
- controllers: list of { name, route_prefix, endpoints: [...] }
- sensitive_files: list of blacklisted paths found
- statistics: { total_projects, total_controllers, total_endpoints, ... }
```

**Verify:** Chạy survey trên sample .NET project, check inventory YAML valid.

---

### Task 3.3 — Implement `plan_node` (`app/agents/planner.py`) [MỚI]
**Deliverable:** Node decompose inventory thành danh sách tasks
**Changes:**
```
Tạo file mới: app/agents/planner.py

Logic:
1. Đọc inventory từ state
2. Cho mỗi project (theo migration_order tier):
   a. Tạo task: csproj_conversion
   b. Tạo task: nuget_migration
   c. Tạo task: nuget_update
   d. Tạo task: startup_migration (nếu has_global_asax)
   e. Tạo task: config_migration
   f. Tạo task: auth_migration (nếu has_custom_auth)
   g. Tạo tasks: controller_migration × N (mỗi controller 1 task)
   h. Tạo task: oracle_migration (nếu uses_oracle)
   i. Tạo task: ef6_migration (nếu uses_ef6)
   j. Tạo task: logging_migration
   k. Tạo task: namespace_update
   l. Tạo task: docker_setup
3. Set dependencies giữa tasks
4. Assign harness/model theo config.yaml
5. Tạo summary cho human review

Output:
- state.tasks = [TaskItem, TaskItem, ...]
- state.plan = { strategy, tiers, estimated_tasks, high_risk, ... }
```

**Verify:** Plan từ sample inventory → valid task list, dependency order đúng.

---

### Task 3.4 — Implement `migrate_task_node`
**Deliverable:** Node thực thi SINGLE task, loop controller
**Changes:**
```python
def migrate_task_node(state: MigrationState) -> MigrationState:
    # 1. Lấy next pending task (theo dependency order)
    task = get_next_task(state)
    if task is None:
        return state  # No more tasks → edge sẽ route to document

    # 2. Check dependencies đã completed chưa
    if not all_deps_completed(task, state):
        state.workflow_state = "blocked"
        state.blocked_reason = f"Task {task.id} waiting for: {task.depends_on}"
        return state

    # 3. Load routing config
    routing = load_task_routing(task.type)

    # 4. Execute via adapter
    task.status = "in_progress"
    task.started_at = datetime.now()
    task.attempt_count += 1

    result = adapter.execute(task, state.worktree_path, routing.skills)

    # 5. Update task status
    if result.success:
        task.status = "completed"
        task.completed_at = datetime.now()
    else:
        task.status = "failed"
        task.error_message = result.error

    state.current_task_id = task.id
    return state
```

**Verify:** Single task execution → status updated correctly.

---

### Task 3.5 — Implement `checkpoint_node` [MỚI]
**Deliverable:** SOP checkpoint review sau mỗi task
**Changes:**
```python
def checkpoint_node(state: MigrationState) -> MigrationState:
    """SOP: Review sau mỗi task"""
    task = get_task_by_id(state, state.current_task_id)

    checks = {
        "scope_correct": verify_scope(task, state.worktree_path),
        "no_blacklist_touched": safety.scan_worktree(state.worktree_path),
        "no_spec_deviation": verify_no_extra_changes(task, state.worktree_path),
        "output_usable": verify_output_exists(task, state.worktree_path),
    }

    if all(checks.values()):
        state.workflow_state = "normal"
    else:
        failed_checks = [k for k, v in checks.items() if not v]
        logger.warning(f"Checkpoint failed: {failed_checks}")
        # SOP: "output bẩn hoặc lệch spec thì kill sớm"
        task.status = "failed"
        task.error_message = f"Checkpoint failed: {failed_checks}"
        state.workflow_state = "remediation"

    return state
```

**Verify:** Test checkpoint với clean task → pass. Test với extra file changes → fail.

---

### Task 3.6 — Implement `fix_node` với escalation
**Deliverable:** Fix + escalation logic theo SOP
**Changes:**
```python
def fix_node(state: MigrationState) -> MigrationState:
    task = get_current_task(state)

    if task.attempt_count >= task.max_attempts:
        # SOP: Escalate to human
        task.status = "escalated"
        generate_escalation_report(task, state)
        # Thêm vào debt
        state.debt.append(DebtItem(
            id=f"debt-{task.id}",
            description=f"Cannot auto-fix: {task.error_message}",
            file=task.source_files[0] if task.source_files else None,
            severity="high",
            phase=state.current_phase,
            created_at=datetime.now()
        ))
        return state

    # Execute fix via OMC with ralph loop
    result = adapter.execute(task, state.worktree_path, skills=[], is_fix=True)

    # SONA feedback
    ruflo_client.learn_pattern(state, task.error_message, result.output)

    state.fix_attempts += 1
    return state
```

**Verify:** Test fix succeeds. Test max attempts → escalation report generated.

---

### Task 3.7 — Implement `human_gate_node` với LangGraph interrupt
**Deliverable:** Proper human approval gate
**Changes:**
```python
# graph.py
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_gate_node"]
)

# main.py — resume after approval
def resume_after_approval(decision: str):
    # Load state from checkpointer
    # Update state.human_decision = decision
    # Resume graph
    for event in graph.stream(None, config={"configurable": {"thread_id": session_id}}):
        ...
```

Xóa `input("Approve Phase 2? (y/n)")` — thay bằng interrupt pattern.

**Verify:** Graph pauses at human_gate. Resume with approve → continues. Resume with reject → ends.

---

### Task 3.8 — Implement `learn_node` [MỚI]
**Deliverable:** SONA feedback + auto skill creation node
**Changes:**
```python
def learn_node(state: MigrationState) -> MigrationState:
    """Chạy sau mỗi validate thành công"""
    task = get_current_task(state)

    # 1. Nếu task had errors → được fix → learn pattern
    if task.fix_history:
        for fix in task.fix_history:
            ruflo_client.learn_pattern(state, fix["error"], fix["fix"])

    # 2. Auto skill creation nếu pattern lặp ≥ 3 lần
    error_counts = count_error_patterns(state.error_log)
    for pattern, count in error_counts.items():
        if count >= 3:
            auto_skill_creator.create_skill(
                f"auto-fix-{pattern[:20]}",
                f"Auto fix for: {pattern}",
                examples=[e for e in state.error_log if pattern in e.get("error", "")]
            )

    # 3. Metrics logging
    log_agent_metrics(task, state)

    return state
```

**Verify:** After fix → pattern saved. After 3 same errors → skill created.

---

### Task 3.9 — Implement `deliver_node` [MỚI]
**Deliverable:** Git commit, push, create PR
**Changes:**
```python
def deliver_node(state: MigrationState) -> MigrationState:
    """Git operations + Azure DevOps PR"""
    worktree = state.worktree_path

    # 1. Safety: pre-commit check
    staged = get_staged_files(worktree)
    violations = safety.check_pre_commit(staged)
    if violations:
        state.safety_violations.extend(violations)
        logger.error(f"Pre-commit safety violation: {violations}")
        return state  # Don't commit

    # 2. Commit
    commit_msg = f"forge(migration): {state.current_phase} [{state.migration_id}]"
    git_commit(worktree, commit_msg)

    # 3. Push
    git_push(worktree)

    # 4. Create PR (Azure DevOps)
    create_pr(state)

    return state
```

**Verify:** Test commit with clean files → success. Test with blacklisted file → blocked.

---

## Phase 4: Ruflo MCP Integration
**Mục tiêu:** Kết nối đúng cách với Ruflo qua MCP protocol.

### Task 4.1 — Rewrite `app/core/ruflo_mcp.py`
**Deliverable:** MCP client chuẩn thay REST calls
**Changes:**
```python
# Option A: Dùng Ruflo MCP tools qua subprocess
class RufloMCPClient:
    def __init__(self):
        self.available = self._check_available()

    def _check_available(self) -> bool:
        result = subprocess.run(["npx", "ruflo", "--version"], capture_output=True)
        return result.returncode == 0

    def learn_pattern(self, error: str, fix: str):
        """Sử dụng ruflo neural train"""
        subprocess.run([
            "npx", "ruflo", "neural", "train",
            "--pattern-type", "optimization",
            "--training-data", json.dumps({"error": error, "fix": fix})
        ])

    def route_task(self, task_type: str, context: dict) -> str:
        """Sử dụng ruflo route"""
        result = subprocess.run([
            "npx", "ruflo", "route",
            "--task", json.dumps({"type": task_type, **context})
        ], capture_output=True, text=True)
        return parse_route_result(result.stdout)

    def get_reasoning(self, query: str) -> str:
        """Sử dụng ruflo analyze"""
        result = subprocess.run([
            "npx", "ruflo", "analyze", "code",
            "--query", query
        ], capture_output=True, text=True)
        return result.stdout

# Option B: Graceful degradation khi Ruflo không available
    def route_task_fallback(self, task_type: str, context: dict) -> str:
        """Static routing từ config.yaml khi Ruflo unavailable"""
        routing = load_task_routing(task_type)
        return routing["harness"]
```

**Verify:** Ruflo available → MCP calls work. Ruflo unavailable → fallback to static config.

---

### Task 4.2 — Ruflo startup integration
**Deliverable:** Auto-start Ruflo MCP server
**Changes:**
```
- Rewrite ruflo_start.py:
  + Check nếu Ruflo đã running
  + npx ruflo init nếu chưa init
  + npx ruflo mcp start --port 3131 (background)
  + Health check sau start
  + Graceful shutdown handler
```

**Verify:** Start → health check pass. Kill → restart works.

---

## Phase 5: Migration Skills
**Mục tiêu:** Bổ sung skills còn thiếu cho Phase 1.

### Task 5.1 — Controller Migration skill
**Deliverable:** `.migration-skills/dotnet-controller-migration/SKILL.md`
**Content:**
```
- ApiController → ControllerBase + [ApiController]
- IHttpActionResult → IActionResult
- [RoutePrefix] → [Route]
- [FromUri] → [FromQuery]
- Request.CreateResponse() → Ok(), BadRequest(), etc.
- Full namespace mapping table
- Examples before/after
```

### Task 5.2 — Web.config Migration skill
**Deliverable:** `.migration-skills/dotnet-webconfig-to-appsettings/SKILL.md`
**Content:**
```
- appSettings → appsettings.json
- connectionStrings → ConnectionStrings (với placeholder!)
- system.web/authentication → middleware
- ⚠️ SAFETY: không copy connection strings thật
```

### Task 5.3 — Global.asax → Program.cs skill
**Deliverable:** `.migration-skills/dotnet-startup-migration/SKILL.md`
**Content:**
```
- Application_Start → top-level statements
- WebApiConfig.Register → AddControllers()
- Route config → attribute routing
- DI registration migration
- Middleware pipeline setup
```

### Task 5.4 — Auth Middleware Migration skill
**Deliverable:** `.migration-skills/dotnet-auth-middleware/SKILL.md`
**Content:**
```
- DelegatingHandler → Middleware class
- Bearer token validation pattern
- UseAuthentication() + UseAuthorization()
```

### Task 5.5 — Namespace Replacement skill
**Deliverable:** `.migration-skills/dotnet-namespace-replacement/SKILL.md`
**Content:**
```
- Full mapping table: System.Web.Http → Microsoft.AspNetCore.Mvc, etc.
- Common type replacements
- API call replacements
```

### Task 5.6 — Logging Adapter skill
**Deliverable:** `.migration-skills/dotnet-logging-adapter/SKILL.md`
**Content:**
```
- Custom logger → ILogger<T> adapter pattern
- Preserve existing interface
```

### Task 5.7 — Dockerfile skill
**Deliverable:** `.migration-skills/dotnet-docker-setup/SKILL.md`
**Content:**
```
- Multi-stage build template
- Health check endpoint
- Non-root user
- Environment variables
```

### Task 5.8 — NuGet Package Mapping skill
**Deliverable:** `.migration-skills/dotnet-nuget-mapping/SKILL.md`
**Content:**
```
- Full mapping table (40+ packages)
- Packages to remove (built-in)
- Packages to keep
- Packages needing version update
```

### Task 5.9 — Update `sync_skills.py`
**Deliverable:** Updated SKILLS list với tất cả skills mới
**Changes:**
```python
SKILLS = [
    # Phase 1
    "dotnet-phase1-csproj-upgrade",
    "dotnet-oracle-ef6-migration",
    "dotnet-msal-update",
    "dotnet-controller-migration",
    "dotnet-webconfig-to-appsettings",
    "dotnet-startup-migration",
    "dotnet-auth-middleware",
    "dotnet-namespace-replacement",
    "dotnet-logging-adapter",
    "dotnet-docker-setup",
    "dotnet-nuget-mapping",
    # Phase 2
    "dotnet-clean-arch-cqrs",
    "dotnet-ddd-value-objects",
]
```

**Verify:** sync_skills syncs all 13 skills to all harness skill directories.

---

## Phase 6: SOP Compliance Layer
**Mục tiêu:** Encode SOP rules vào code, đảm bảo không vi phạm.

### Task 6.1 — SOP Checklist Enforcement (`app/core/sop.py`) [MỚI]
**Deliverable:** Module enforce SOP checklists programmatically
**Changes:**
```python
class SOPEnforcer:
    def pre_phase_check(state: MigrationState) -> SOPResult:
        """SOP Section A: Trước khi bắt đầu phase"""
        checks = [
            ("goal_defined", state.plan is not None),
            ("scope_locked", len(state.tasks) > 0),
            ("worktree_set", state.worktree_path is not None),
        ]
        return SOPResult(checks)

    def pre_task_check(task: TaskItem) -> SOPResult:
        """SOP Section B: Trước khi giao task"""
        checks = [
            ("task_small_enough", len(task.source_files) <= 5),
            ("single_deliverable", task.done_criteria is not None),
            ("input_clear", len(task.source_files) > 0),
            ("output_clear", len(task.target_files) > 0),
            ("verify_step_defined", task.verify_command is not None),
            ("timeout_set", True),  # Always true from config
        ]
        return SOPResult(checks)

    def post_task_check(task: TaskItem, worktree: str) -> SOPResult:
        """SOP Section E: Sau khi task xong"""
        checks = [
            ("scope_correct", verify_only_expected_files_changed(task, worktree)),
            ("no_contract_violation", safety.scan_worktree(worktree).is_clean),
            ("no_side_effects", verify_no_extra_changes(task, worktree)),
        ]
        return SOPResult(checks)

    def done_criteria_check(state: MigrationState) -> SOPResult:
        """SOP Section I: Điều kiện chốt phase"""
        checks = [
            ("implementation_done", all_tasks_completed(state)),
            ("validation_pass", len(state.build_errors) == 0),
            ("debt_recorded", True),  # debt list is always maintained
            ("report_generated", len(state.reports) > 0),
        ]
        return SOPResult(checks)
```

**Verify:** Each check function works with sample state.

---

### Task 6.2 — Reporting theo SOP format (`app/utils/reporter.py`)
**Deliverable:** Reports đúng SOP Section 10 format
**Changes:**
```
Mỗi report phải có:
- Đã chạy gì (list of tasks executed)
- Pass gì (completed tasks)
- Fail gì (failed tasks with error details)
- Fix gì (fixes applied)
- Debt gì (remaining debt items)

Không dùng "chắc ổn" — chỉ dùng dữ liệu từ state.

Report types:
1. Phase Summary Report (MD)
2. Task Detail Report (YAML per task)
3. Error & Fix Log (MD)
4. Debt Register (YAML)
5. Endpoint Comparison (MD table)
6. NuGet Mapping Report (MD table)
7. PR Description (MD)
8. Evolution Report (MD — SONA patterns learned)
```

**Verify:** Generate reports từ sample state → all sections present, no "chắc ổn".

---

### Task 6.3 — Workflow states (normal/blocked/remediation)
**Deliverable:** State machine transitions theo SOP
**Changes:**
```python
# Trong graph.py conditional edges:

def route_workflow_state(state) -> str:
    if state.workflow_state == "blocked":
        return "handle_blocked"        # Collect missing evidence
    if state.workflow_state == "remediation":
        return "fix"                   # Repair artifact
    return "normal_next"               # Continue

def handle_blocked_node(state):
    """SOP: Collect missing evidence / artifact / decision"""
    generate_blocked_report(state)
    # Pause cho human decision
    state.needs_human_approval = True
    return state
```

**Verify:** Task fails with missing dep → blocked state. Human provides info → resumes.

---

## Phase 7: Polish & Integration
**Mục tiêu:** Dashboard, testing, documentation.

### Task 7.1 — Update `main.py` entry point
**Deliverable:** CLI với resume, status, individual phase commands
**Changes:**
```python
@app.command()
def start(solution_path: str, phase: int = 1): ...

@app.command()
def resume(solution_path: str): ...

@app.command()
def status(solution_path: str): ...

@app.command()
def approve(solution_path: str, decision: str = "approve"): ...
```

**Verify:** Each command works end-to-end.

---

### Task 7.2 — Update `dashboard.py`
**Deliverable:** Dashboard hiển thị task-level progress
**Changes:**
```
- Task list với status icons (✅❌🔄⏳⛔)
- Build errors section
- Debt section
- SONA learned patterns
- Current agent + tool being used
- Retry count
- Safety violations (if any)
```

**Verify:** Dashboard updates live khi migration chạy.

---

### Task 7.3 — Update `config.yaml` schema
**Deliverable:** Unified config với tất cả settings
**Changes:**
```yaml
migration:
  id: "mig-202604"
  target_framework: "net10.0"
  strategy: "lift-and-shift"
  nullable: "disable"
  implicit_usings: "disable"

safety:
  config_file: "config/safety.yaml"

tools:
  config_file: "app/tools/config.yaml"

vibekanban:
  enabled: true
  url: "http://localhost:3000/api/mcp"

ruflo:
  enabled: true
  mcp_url: "http://localhost:3131"
  fallback_to_static: true

gitnexus:
  enabled: true
  mcp_url: "http://localhost:4000/mcp"
  index_on_start: true

git:
  branch_format: "migration/v1-{project_name}"
  commit_format: "forge({agent}): {title} [{task_id}]"
  use_worktree: true
  auto_push: false
  create_pr: true
  pr_target_branch: "develop"

session:
  auto_save_interval: 60
  resume_on_start: true

logging:
  level: "DEBUG"
  rotation: "10 MB"
  retention: "30 days"
```

**Verify:** Settings load correctly from YAML + .env override.

---

### Task 7.4 — Integration tests
**Deliverable:** Test suite cho critical paths
**Changes:**
```
tests/
├── test_state.py              # State model creation, serialization
├── test_safety.py             # All safety checks
├── test_sop.py                # SOP enforcement checks
├── test_graph.py              # Graph compilation, edge routing
├── test_adapter_mock.py       # Adapter with mocked harnesses
├── test_persistence.py        # Save/load round-trip
├── test_planner.py            # Inventory → task decomposition
├── test_skills_sync.py        # Skill sync to all harnesses
└── fixtures/
    ├── sample_inventory.yaml
    ├── sample_state.json
    └── sample_csproj/          # Minimal .NET project for testing
```

**Verify:** `pytest tests/ -v` → all pass.

---

### Task 7.5 — Update `.gitignore`
**Deliverable:** Ignore runtime state, keep config
**Changes:**
```
# Thêm vào .gitignore:
state/
.worktrees/
*.db
*.db-journal
*.db-wal
__pycache__/
.env
```

---

### Task 7.6 — Documentation updates
**Deliverable:** Updated README, architecture docs
**Changes:**
```
docs/
├── ARCHITECTURE.md            # Updated architecture diagram
├── SOP.md                     # Embedded SOP (từ sop_swarm.txt)
├── HARNESS-INTERFACES.md      # Task 2.1 output
├── TASK-ROUTING.md            # Task → harness mapping explanation
├── SAFETY-RULES.md            # Safety rules documentation
└── TROUBLESHOOTING.md         # Common issues & fixes
```

---

## Dependency Graph

```
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 6 ──→ Phase 7
  │            │            │            │            │
  │            │            │            │            │
  0.1 state    1.1 safety   2.1 research 3.1 graph    6.1 sop
  0.2 persist  1.2 config   2.2 adapter  3.2 survey   6.2 reporter
  0.3 dedup    1.3 integ.   2.3 retry    3.3 planner  6.3 workflow
                             2.4 template 3.4 migrate
                             2.5 routing  3.5 checkpt   Phase 4
                                          3.6 fix        │
                                          3.7 human      4.1 ruflo
                                          3.8 learn      4.2 startup
                                          3.9 deliver
                                                         Phase 5
                                                           │
                                                         5.1-5.9 skills
```

## Priority Execution Order

```
CRITICAL PATH (phải làm trước khi test bất kỳ thứ gì):
  0.1 → 0.2 → 0.3 → 1.1 → 1.2 → 2.2 → 3.1 → 3.3 → 3.4

CAN PARALLELIZE:
  [1.3, 2.1, 2.4, 2.5]   # Sau khi 1.1 + 2.2 done
  [5.1 - 5.9]             # Independent, anytime
  [4.1, 4.2]              # Independent
  [7.1 - 7.6]             # After Phase 3 done

OPTIONAL/NICE-TO-HAVE:
  7.2 dashboard
  7.4 integration tests
  7.6 documentation
```

## Estimated Effort

| Phase | Tasks | Complexity | Est. Lines |
|-------|-------|-----------|-----------|
| 0: Foundation | 3 | Medium | ~300 |
| 1: Safety | 3 | Medium | ~250 |
| 2: Tool Adapter | 5 | High | ~500 |
| 3: Graph Redesign | 9 | Very High | ~800 |
| 4: Ruflo MCP | 2 | Medium | ~200 |
| 5: Skills | 9 | Low | ~400 (md) |
| 6: SOP Compliance | 3 | Medium | ~350 |
| 7: Polish | 6 | Medium | ~500 |
| **Total** | **40** | | **~3,300** |
