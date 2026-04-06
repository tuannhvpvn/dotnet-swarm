---
wave: 1
depends_on: []
files_modified: ["app/core/safety.py", "config/safety.yaml", "app/core/harness_adapter.py", "app/tools/adapter.py", "app/agents/surveyor.py", "app/agents/phase1_migrator.py", "app/agents/phase2_modernizer.py", "app/agents/validator.py"]
autonomous: true
requirements_addressed: [SFE-01, SFE-02, SFE-03]
---

# Phase 2: Safety Layer Plan

<objective>
Implement the SafetyRules enforcement module, configurable safety rules YAML, and a generic harness adapter that wraps all external CLI calls with defense-in-depth safety checks (git hook + post-execution scan + prompt injection).
</objective>

<tasks>

<task>
  <id>sfe-01-safety-module</id>
  <title>Create SafetyRules module (app/core/safety.py)</title>
  <read_first>
    <file>IMPLEMENTATION-PLAN-v2.md</file>
    <file>app/core/state.py</file>
  </read_first>
  <action>
Create `app/core/safety.py` with the following:

1. **`SafetyResult` dataclass:**
   - `safe: bool`
   - `rule_id: str | None`
   - `severity: Literal["critical", "warning", "info"]`
   - `message: str`
   - `file_path: str | None`

2. **`SafetyRules` class** loaded from `config/safety.yaml`:
   - `blacklist_folders: list[str]` — glob patterns like `**/keys/`, `**/certs/`
   - `blacklist_files: list[str]` — patterns like `*.pfx`, `*.pem`, `*.key`
   - `blacklist_content: list[re.Pattern]` — compiled from `password=`, `BEGIN RSA PRIVATE KEY`, etc.
   - `protected_branches: list[str]` — `main`, `master`, `production`
   - `forbidden_sql: list[str]` — `INSERT`, `UPDATE`, `DELETE`, `DROP`

3. **Methods:**
   - `check_file_path(path: str) -> SafetyResult` — match against folder+file blacklists using `fnmatch`
   - `check_file_content(content: str) -> SafetyResult` — regex scan content for blacklisted patterns
   - `check_sql(sql: str) -> SafetyResult` — detect forbidden SQL keywords (case-insensitive)
   - `check_branch(branch: str) -> SafetyResult` — reject protected branches
   - `check_pre_commit(staged_files: list[str]) -> list[SafetyResult]` — iterate staged files through `check_file_path`
   - `scan_worktree(worktree_path: str) -> list[SafetyResult]` — walk directory, check every file path and content
   - `generate_hook_script(worktree_path: str) -> str` — return a bash pre-commit hook that calls `python -m app.core.safety --pre-commit`
   - `install_hook(worktree_path: str)` — write `generate_hook_script()` output to `{worktree_path}/.git/hooks/pre-commit`, chmod +x

4. **CLI entry point** (for git hook invocation):
   ```python
   if __name__ == "__main__":
       import sys
       if "--pre-commit" in sys.argv:
           # Load rules, check staged files, exit(1) if violations
   ```
  </action>
  <acceptance_criteria>
    <check>grep -q "class SafetyRules:" app/core/safety.py</check>
    <check>grep -q "class SafetyResult:" app/core/safety.py</check>
    <check>grep -q "def check_file_path" app/core/safety.py</check>
    <check>grep -q "def check_file_content" app/core/safety.py</check>
    <check>grep -q "def check_sql" app/core/safety.py</check>
    <check>grep -q "def scan_worktree" app/core/safety.py</check>
    <check>grep -q "def install_hook" app/core/safety.py</check>
    <check>python -m py_compile app/core/safety.py exits 0</check>
  </acceptance_criteria>
</task>

<task>
  <id>sfe-02-safety-config</id>
  <title>Create configurable safety rules (config/safety.yaml)</title>
  <read_first>
    <file>IMPLEMENTATION-PLAN-v2.md</file>
  </read_first>
  <action>
Create `config/safety.yaml` with exact content:

```yaml
absolute_rules:
  - id: SAFE-001
    rule: "NEVER execute SQL write operations"
    severity: critical
  - id: SAFE-002
    rule: "NEVER modify blacklisted files or folders"
    severity: critical
  - id: SAFE-003
    rule: "NEVER commit to protected branches"
    severity: critical
  - id: SAFE-004
    rule: "NEVER embed credentials in source code"
    severity: critical
  - id: SAFE-005
    rule: "NEVER modify files outside the worktree"
    severity: critical
  - id: SAFE-006
    rule: "NEVER execute arbitrary shell commands from LLM output"
    severity: critical
  - id: SAFE-007
    rule: "ALWAYS validate harness output before applying"
    severity: warning

blacklist:
  folders:
    - "**/keys/"
    - "**/certs/"
    - "**/pgp/"
    - "**/ssl/"
    - "**/.vs/"
  files:
    - "*.pfx"
    - "*.pem"
    - "*.key"
    - "*.p12"
    - "*.cer"
    - "*.pgp"
    - "*.snk"
  content_patterns:
    - "password="
    - "BEGIN RSA PRIVATE KEY"
    - "BEGIN PRIVATE KEY"
    - "connectionString="

git_safety:
  protected_branches:
    - "main"
    - "master"
    - "production"

forbidden_sql:
  - "INSERT"
  - "UPDATE"
  - "DELETE"
  - "DROP"
  - "TRUNCATE"
  - "ALTER"
```
  </action>
  <acceptance_criteria>
    <check>test -f config/safety.yaml</check>
    <check>grep -q "SAFE-001" config/safety.yaml</check>
    <check>grep -q "\\*\\*/keys/" config/safety.yaml</check>
    <check>python -c "import yaml; yaml.safe_load(open('config/safety.yaml'))" exits 0</check>
  </acceptance_criteria>
</task>

<task>
  <id>sfe-03-harness-adapter</id>
  <title>Create generic harness adapter with safety integration</title>
  <read_first>
    <file>app/tools/adapter.py</file>
    <file>app/core/safety.py</file>
    <file>app/agents/surveyor.py</file>
    <file>app/agents/phase1_migrator.py</file>
    <file>app/agents/phase2_modernizer.py</file>
    <file>app/agents/validator.py</file>
  </read_first>
  <action>
1. **Create `app/core/harness_adapter.py`:**
   - Import `SafetyRules` from `app.core.safety` and `call_harness` from `app.tools.adapter`
   - Class `HarnessAdapter`:
     - `__init__(self, safety: SafetyRules)` — store safety rules instance
     - `execute(self, task_spec: dict, state: MigrationState) -> dict`:
       1. **Pre-flight:** Call `safety.check_file_path()` on each file in `task_spec["source_files"]` (if present). If any critical violation → return failure immediately, log to `state.safety_violations`.
       2. **Install hook:** Call `safety.install_hook(task_spec["worktree"])` to set up git pre-commit hook.
       3. **Delegate:** Call `call_harness(task_spec)` — the existing subprocess wrapper.
       4. **Post-scan:** Call `safety.scan_worktree(task_spec["worktree"])`. If violations found → run `subprocess.run(["git", "checkout", "--", "."], cwd=worktree)` to discard changes, log violations, return failure.
       5. **Return** harness result on success.
   - Module-level singleton: `harness = HarnessAdapter(SafetyRules("config/safety.yaml"))`

2. **Update all 4 agent nodes** to import from new adapter:
   - `app/agents/surveyor.py`: Change `from app.tools.adapter import call_harness` → `from app.core.harness_adapter import harness` and replace `call_harness(task_spec)` with `harness.execute(task_spec, state)`
   - Same change in `phase1_migrator.py`, `phase2_modernizer.py`, `validator.py`

3. **Keep `app/tools/adapter.py` unchanged** — it remains the low-level subprocess executor.
  </action>
  <acceptance_criteria>
    <check>grep -q "class HarnessAdapter:" app/core/harness_adapter.py</check>
    <check>grep -q "from app.core.harness_adapter import harness" app/agents/surveyor.py</check>
    <check>grep -q "from app.core.harness_adapter import harness" app/agents/phase1_migrator.py</check>
    <check>grep -q "from app.core.harness_adapter import harness" app/agents/phase2_modernizer.py</check>
    <check>grep -q "from app.core.harness_adapter import harness" app/agents/validator.py</check>
    <check>! grep -q "from app.tools.adapter import call_harness" app/agents/surveyor.py</check>
    <check>python -m py_compile app/core/harness_adapter.py exits 0</check>
  </acceptance_criteria>
</task>

</tasks>

<verification>
## Verification
1. `python -m py_compile app/core/safety.py` — syntax valid
2. `python -m py_compile app/core/harness_adapter.py` — syntax valid
3. `python -c "from app.core.safety import SafetyRules; s = SafetyRules('config/safety.yaml'); r = s.check_file_path('keys/secret.pfx'); assert not r.safe"` — blacklist enforcement works
4. `python -c "from app.core.safety import SafetyRules; s = SafetyRules('config/safety.yaml'); r = s.check_file_content('password=hunter2'); assert not r.safe"` — content scan works
5. `python -c "from app.core.safety import SafetyRules; s = SafetyRules('config/safety.yaml'); r = s.check_file_path('app/core/state.py'); assert r.safe"` — clean files pass
</verification>

<must_haves>
- `SafetyRules` blocks operations on `keys/` or restricted files (SFE-01 success criterion 1).
- All 3 execution vectors (path, content, git) trigger violation correctly (SFE-01 success criterion 2).
- Safety checks run before AND after every harness call via `HarnessAdapter`.
- `config/safety.yaml` is the single source of truth for all safety rules.
</must_haves>
