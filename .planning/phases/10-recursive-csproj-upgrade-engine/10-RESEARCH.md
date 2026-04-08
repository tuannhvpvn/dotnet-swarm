# Phase 10: Recursive `.csproj` Upgrade Engine — Research

**Phase:** 10
**Gathered:** 2026-04-07
**Status:** Complete

---

## Domain Overview

Phase 10 adds a deterministic recursive dependency graph resolver to the orchestrator. The engine must:
1. Parse a root `.sln` or `.csproj` to discover all transitive `<ProjectReference>` paths
2. Update `<TargetFramework>` tags across the entire resolved graph
3. Integrate with the existing `migrate_task_node` / `validator_node` pipeline

The core architectural decision (**D-01** from `dec_adv01_parse.md`) locks in **Pure Python XML parsing** for both graph resolution and tag mutation — no AI harness involvement.

---

## Technical Research

### 1. Python `xml.etree.ElementTree` API

**Parsing:**
```python
import xml.etree.ElementTree as ET
tree = ET.parse('MyProject.csproj')
root = tree.getroot()
```

**Finding elements (SDK-style, no namespace):**
```python
# Direct tag access — works for modern SDK-style .csproj
tf = root.find('.//TargetFramework')
tf_multi = root.find('.//TargetFrameworks')
refs = root.findall('.//ProjectReference')
```

**Legacy format (ToolsVersion="15.0" — `xmlns` present):**
```python
NS = 'http://schemas.microsoft.com/developer/msbuild/2003'
ET.register_namespace('', NS)  # avoids ns0: prefix on write-back
refs = root.findall(f'.//{{{NS}}}ProjectReference')
```

**Mutating and writing back:**
```python
tf.text = 'net10.0'
tree.write('MyProject.csproj', encoding='utf-8', xml_declaration=True)
```

**Key gotcha:** `ET.write()` drops the `<?xml version="1.0" encoding="utf-8"?>` declaration unless `xml_declaration=True`. SDK-style `.csproj` files typically don't have one — write without it unless the original had it.

---

### 2. `.csproj` XML Namespace Handling

| Format | Root element | Namespace present? | How to detect |
|---|---|---|---|
| **SDK-style** (modern) | `<Project Sdk="Microsoft.NET.Sdk">` | ❌ No | `root.get('Sdk') is not None` |
| **Legacy** (old) | `<Project ToolsVersion="..." xmlns="...">` | ✅ Yes | `root.get('xmlns') or '{' in root.tag` |

Phase 10 scope: **SDK-style only** (Decision D-03). If `ToolsVersion` is detected, bail to Human Gate.

---

### 3. `ProjectReference` Element Structure

SDK-style `.csproj`:
```xml
<ItemGroup>
  <ProjectReference Include="..\MyLibrary\MyLibrary.csproj" />
</ItemGroup>
```

The `Include` attribute value is a **relative path** from the current project's directory. The resolver must:
```python
import os
ref_path_attr = elem.get('Include')  # e.g. "..\MyLib\MyLib.csproj"
abs_path = os.path.normpath(os.path.join(project_dir, ref_path_attr))
```

On Linux the backslash paths must be normalized: `ref_path_attr.replace('\\', os.sep)`.

---

### 4. Recursive Resolution Algorithm

```python
def resolve_graph(root_path: str, visited: set[str] | None = None) -> list[str]:
    """BFS/DFS resolver — returns ordered list of all .csproj paths."""
    if visited is None:
        visited = set()
    root_path = os.path.normpath(root_path)
    if root_path in visited:
        return []
    visited.add(root_path)
    result = [root_path]
    
    tree = ET.parse(root_path)
    root_elem = tree.getroot()
    project_dir = os.path.dirname(root_path)
    
    for ref in root_elem.findall('.//ProjectReference'):
        include = ref.get('Include', '').replace('\\', os.sep)
        abs_ref = os.path.normpath(os.path.join(project_dir, include))
        if os.path.exists(abs_ref):
            result.extend(resolve_graph(abs_ref, visited))
    
    return result
```

**Circular dependency protection:** `visited` set prevents infinite recursion.  
**Missing file guard:** `os.path.exists(abs_ref)` check before recursing — missing refs are logged, not fatal.

---

### 5. `.sln` Parsing

`.sln` files are NOT XML. They use a custom text format:
```
Project("{FAE04EC0-...}") = "MyApp", "src\MyApp\MyApp.csproj", "{GUID}"
EndProject
```

Extract `.csproj` paths using regex:
```python
import re
SLN_PROJECT_RE = re.compile(
    r'Project\("[^"]+"\)\s*=\s*"[^"]+",\s*"([^"]+\.csproj)"',
    re.IGNORECASE
)
```

Then run `resolve_graph()` on each extracted `.csproj` path individually (union of all subtrees).

---

### 6. TargetFramework Update Logic

```python
VALID_TF_TAGS = {'TargetFramework', 'TargetFrameworks'}

def upgrade_target_framework(csproj_path: str, target_tf: str) -> bool:
    tree = ET.parse(csproj_path)
    root_elem = tree.getroot()
    modified = False
    
    # Detect legacy format
    if 'ToolsVersion' in root_elem.attrib:
        raise ValueError(f"Legacy format not supported: {csproj_path}")
    
    for tag in VALID_TF_TAGS:
        for elem in root_elem.iter(tag):
            if elem.text != target_tf:
                elem.text = target_tf
                modified = True
    
    if modified:
        tree.write(csproj_path, encoding='utf-8', xml_declaration=False)
    return modified
```

**Note:** `TargetFrameworks` (plural) is for multi-targeting — replacing all values with a single `net10.0` is intentional for Phase 1 lift-and-shift.

---

### 7. SOP Hard-Block Integration

Phase 10 must integrate at the `migrate_task_node` level (not a new node). The upgrade sequence inserts as a pre-flight task:

```
TASK: upgrade_csproj_frameworks
  → resolve_graph(entry_path)
  → for each .csproj: upgrade_target_framework(path, target_tf)
  → if any ValueError (legacy): set workflow_state = "blocked" → human_gate
```

On XML parse error (`ET.ParseError`): also hard block — never silently continue.

---

### 8. Validation Architecture (Nyquist)

Post-upgrade validation:
- **Unit tests:** `test_csproj_resolver.py` — parametrized with fixture `.csproj` trees (mock filesystem)
- **Integration tests:** Run `dotnet build {solution}` on a real fixture solution and assert exit code 0
- **Coverage requirement:** `resolve_graph()` and `upgrade_target_framework()` must reach 90%+ statement coverage

---

## Files to Create / Modify

| Action | Path | Purpose |
|---|---|---|
| **CREATE** | `app/utils/csproj_resolver.py` | Core resolver + upgrader module |
| **MODIFY** | `app/agents/phase1_migrator.py` | Call resolver as pre-flight task |
| **CREATE** | `tests/utils/test_csproj_resolver.py` | Unit + integration tests |
| **MODIFY** | `app/core/state.py` | Add optional `resolved_csproj_paths` field |

---

## RESEARCH COMPLETE
