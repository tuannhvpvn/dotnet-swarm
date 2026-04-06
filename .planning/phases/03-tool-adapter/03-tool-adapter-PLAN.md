---
wave: 1
depends_on: []
files_modified: ["app/tools/adapter.py", "app/core/harness_adapter.py", "requirements.txt"]
autonomous: true
requirements_addressed: [TAD-01, TAD-02, TAD-03, TAD-04, TAD-05]
---

# Phase 3: Tool Adapter Rewrite Plan

<objective>
Refactor `app/tools/adapter.py` into an object-oriented factory pattern supporting specific CLI executors (`omo`, `omx`, `omc`, `kiro`), integrate `tenacity` for feedback-loop retries, and implement sidecar file generation for context injection.
</objective>

<tasks>

<task>
  <id>tad-01-requirements</id>
  <title>Update project dependencies</title>
  <read_first>
    <file>requirements.txt</file>
  </read_first>
  <action>
Add `tenacity` to `requirements.txt` if not already present.
  </action>
  <acceptance_criteria>
    <check>grep -q "tenacity" requirements.txt</check>
  </acceptance_criteria>
</task>

<task>
  <id>tad-02-harness-executors</id>
  <title>Rewrite adapter executors (app/tools/adapter.py)</title>
  <read_first>
    <file>app/tools/adapter.py</file>
  </read_first>
  <action>
Rewrite `app/tools/adapter.py` to use an OOP factory pattern with `tenacity` retries.

1. **Imports:**
   - Add `import subprocess`, `json`, `os`, `shutil`, `from pathlib import Path`
   - Add `from tenacity import retry, stop_after_attempt, wait_exponential`
   
2. **Base Class `HarnessExecutor`:**
   - `def execute(self, task_spec: dict) -> dict:` (Abstract)
   - `def _write_sidecar(self, worktree: str, filename: str, content: str):` writes context to file.
   - `def _build_cmd(self, task_spec: dict) -> list[str]:` (Abstract)

3. **Concrete Classes:**
   - `OpenCodeHarness(HarnessExecutor)` (omo)
   - `ClaudeCodeHarness(HarnessExecutor)` (omc)
   - `CodexHarness(HarnessExecutor)` (omx)
   - `KiroHarness(HarnessExecutor)` (kiro)
   
   *For each concrete class:*
   - Implement `_build_cmd` returning the specific CLI syntax.
   - Implement `execute` with `@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))`
   - In the execute method, catch non-zero exit codes. If an error occurs, mutate `task_spec["task"]` to append `\n\nPrevious error:\n{stderr}` and then `raise Exception` to trigger `tenacity` retry.

4. **Context Injection:**
   - In `execute()`, read `task_spec.get("skills", [])` and `task_spec.get("rules", "")`.
   - Before running the CLI, write these to the worktree (e.g. `CLAUDE.md`, `.kiro/rules/migration.md`) using `_write_sidecar`.

5. **Factory function `call_harness(task_spec: dict)`:**
   - Inspects `task_spec["harness"]`
   - Instantiates the correct `HarnessExecutor` subclass
   - Calls `.execute(task_spec)`
  </action>
  <acceptance_criteria>
    <check>grep -q "class HarnessExecutor" app/tools/adapter.py</check>
    <check>grep -q "@retry" app/tools/adapter.py</check>
    <check>grep -q "def call_harness" app/tools/adapter.py</check>
    <check>python -m py_compile app/tools/adapter.py exits 0</check>
  </acceptance_criteria>
</task>

</tasks>

<verification>
## Verification
1. `python -m py_compile app/tools/adapter.py` — syntax valid
2. Write a mock `test_adapter.py` script that invokes `call_harness({"harness": "omo", "model": "mock", "task": "mock", "worktree": "."})` to verify the factory routes properly.
3. Verify that `requirements.txt` has `tenacity` installed.
</verification>

<must_haves>
- Uses `tenacity` for feedback-loop retry.
- Implements sidecar file context injection.
- Preserves the `call_harness()` top-level signature so `app/core/harness_adapter.py` doesn't break.
</must_haves>
