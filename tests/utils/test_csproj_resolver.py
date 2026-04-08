"""
Unit tests for app/utils/csproj_resolver.py

Decision coverage:
  D-01: Pure Python XML — no subprocess/AI calls needed
  D-02: Orchestrator edits XML directly
  D-03: SDK-style only — legacy format raises ValueError
"""
import os
import textwrap
import xml.etree.ElementTree as ET
import pytest

from app.utils.csproj_resolver import (
    parse_sln,
    resolve_graph,
    resolve_from_entry,
    upgrade_target_framework,
    upgrade_solution,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_csproj(path: str, tf: str = "net6.0", refs: list[str] | None = None) -> None:
    """Write a minimal SDK-style .csproj to path."""
    ref_xml = ""
    if refs:
        items = "\n".join(f'    <ProjectReference Include="{r}" />' for r in refs)
        ref_xml = f"  <ItemGroup>\n{items}\n  </ItemGroup>\n"
    content = textwrap.dedent(f"""\
        <Project Sdk="Microsoft.NET.Sdk">
          <PropertyGroup>
            <TargetFramework>{tf}</TargetFramework>
          </PropertyGroup>
        {ref_xml}</Project>
    """)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def make_legacy_csproj(path: str) -> None:
    """Write a legacy-style .csproj (ToolsVersion) to path."""
    content = textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
          <PropertyGroup>
            <TargetFrameworkVersion>v4.8</TargetFrameworkVersion>
          </PropertyGroup>
        </Project>
    """)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def make_sln(path: str, csproj_paths: list[str]) -> None:
    """Write a minimal .sln referencing the given .csproj files."""
    sln_dir = os.path.dirname(path)
    entries = []
    for i, cp in enumerate(csproj_paths):
        rel = os.path.relpath(cp, sln_dir).replace(os.sep, "\\")
        entries.append(
            f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = '
            f'"Proj{i}", "{rel}", "{{GUID-{i}}}"\nEndProject'
        )
    content = "\n".join(["Microsoft Visual Studio Solution File", *entries])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ── parse_sln ─────────────────────────────────────────────────────────────────

class TestParseSln:
    def test_single_project(self, tmp_path):
        proj = tmp_path / "App" / "App.csproj"
        make_csproj(str(proj))
        sln = tmp_path / "App.sln"
        make_sln(str(sln), [str(proj)])
        result = parse_sln(str(sln))
        assert len(result) == 1
        assert result[0] == str(proj)

    def test_multiple_projects(self, tmp_path):
        proj_a = tmp_path / "A" / "A.csproj"
        proj_b = tmp_path / "B" / "B.csproj"
        make_csproj(str(proj_a))
        make_csproj(str(proj_b))
        sln = tmp_path / "MySolution.sln"
        make_sln(str(sln), [str(proj_a), str(proj_b)])
        result = parse_sln(str(sln))
        assert len(result) == 2

    def test_empty_sln_returns_empty_list(self, tmp_path):
        sln = tmp_path / "Empty.sln"
        sln.write_text("Microsoft Visual Studio Solution File\n")
        result = parse_sln(str(sln))
        assert result == []

    def test_missing_sln_raises_oserror(self, tmp_path):
        with pytest.raises(OSError):
            parse_sln(str(tmp_path / "does_not_exist.sln"))


# ── resolve_graph ─────────────────────────────────────────────────────────────

class TestResolveGraph:
    def test_single_project_no_refs(self, tmp_path):
        proj = tmp_path / "App.csproj"
        make_csproj(str(proj))
        result = resolve_graph(str(proj))
        assert result == [str(proj)]

    def test_simple_chain_a_b_c(self, tmp_path):
        """A → B → C: result must have C before B before A (dependencies first)."""
        c = tmp_path / "C" / "C.csproj"
        b = tmp_path / "B" / "B.csproj"
        a = tmp_path / "A" / "A.csproj"
        make_csproj(str(c))
        make_csproj(str(b), refs=["../C/C.csproj"])
        make_csproj(str(a), refs=["../B/B.csproj"])
        result = resolve_graph(str(a))
        assert result.index(str(c)) < result.index(str(b))
        assert result.index(str(b)) < result.index(str(a))

    def test_diamond_no_duplicates(self, tmp_path):
        """A → B, A → C, B → D, C → D: D appears exactly once."""
        d = tmp_path / "D" / "D.csproj"
        b = tmp_path / "B" / "B.csproj"
        c = tmp_path / "C" / "C.csproj"
        a = tmp_path / "A" / "A.csproj"
        make_csproj(str(d))
        make_csproj(str(b), refs=["../D/D.csproj"])
        make_csproj(str(c), refs=["../D/D.csproj"])
        make_csproj(str(a), refs=["../B/B.csproj", "../C/C.csproj"])
        result = resolve_graph(str(a))
        assert result.count(str(d)) == 1

    def test_circular_reference_does_not_infinite_loop(self, tmp_path):
        """A → B → A: must terminate without infinite recursion."""
        a = tmp_path / "A" / "A.csproj"
        b = tmp_path / "B" / "B.csproj"
        make_csproj(str(a), refs=["../B/B.csproj"])
        make_csproj(str(b), refs=["../A/A.csproj"])
        result = resolve_graph(str(a))
        assert len(result) == 2  # both discovered, no infinite loop

    def test_missing_ref_is_skipped(self, tmp_path):
        """ProjectReference pointing to non-existent file is skipped silently."""
        a = tmp_path / "A.csproj"
        make_csproj(str(a), refs=["../NonExistent/NonExistent.csproj"])
        result = resolve_graph(str(a))
        assert result == [str(a)]

    def test_legacy_format_raises_value_error(self, tmp_path):
        proj = tmp_path / "Legacy.csproj"
        make_legacy_csproj(str(proj))
        with pytest.raises(ValueError, match="ToolsVersion"):
            resolve_graph(str(proj))

    def test_corrupt_xml_raises_parse_error(self, tmp_path):
        proj = tmp_path / "Bad.csproj"
        proj.write_text("<<not valid xml>>")
        with pytest.raises(ET.ParseError):
            resolve_graph(str(proj))


# ── resolve_from_entry ────────────────────────────────────────────────────────

class TestResolveFromEntry:
    def test_accepts_csproj(self, tmp_path):
        proj = tmp_path / "App.csproj"
        make_csproj(str(proj))
        result = resolve_from_entry(str(proj))
        assert str(proj) in result

    def test_accepts_sln(self, tmp_path):
        proj = tmp_path / "App" / "App.csproj"
        make_csproj(str(proj))
        sln = tmp_path / "App.sln"
        make_sln(str(sln), [str(proj)])
        result = resolve_from_entry(str(sln))
        assert str(proj) in result

    def test_unsupported_extension_raises(self, tmp_path):
        f = tmp_path / "something.txt"
        f.write_text("")
        with pytest.raises(ValueError, match="Unsupported file type"):
            resolve_from_entry(str(f))

    def test_missing_entry_raises_oserror(self, tmp_path):
        with pytest.raises(OSError):
            resolve_from_entry(str(tmp_path / "missing.csproj"))


# ── upgrade_target_framework ──────────────────────────────────────────────────

class TestUpgradeTargetFramework:
    def test_upgrades_single_target_framework(self, tmp_path):
        proj = tmp_path / "App.csproj"
        make_csproj(str(proj), tf="net6.0")
        modified = upgrade_target_framework(str(proj), "net10.0")
        assert modified is True
        tree = ET.parse(str(proj))
        tf = tree.getroot().find(".//TargetFramework")
        assert tf is not None and tf.text == "net10.0"

    def test_no_change_when_already_at_target(self, tmp_path):
        proj = tmp_path / "App.csproj"
        make_csproj(str(proj), tf="net10.0")
        modified = upgrade_target_framework(str(proj), "net10.0")
        assert modified is False

    def test_upgraded_xml_is_valid(self, tmp_path):
        """The written file must be parseable without error."""
        proj = tmp_path / "App.csproj"
        make_csproj(str(proj), tf="net6.0")
        upgrade_target_framework(str(proj), "net10.0")
        tree = ET.parse(str(proj))  # must not raise
        assert tree.getroot() is not None

    def test_legacy_format_raises_value_error(self, tmp_path):
        proj = tmp_path / "Legacy.csproj"
        make_legacy_csproj(str(proj))
        with pytest.raises(ValueError, match="ToolsVersion"):
            upgrade_target_framework(str(proj), "net10.0")

    def test_upgrades_multi_target_frameworks_tag(self, tmp_path):
        """<TargetFrameworks> (plural) is upgraded to single target tf — Dimension 1."""
        content = textwrap.dedent("""\
            <Project Sdk=\"Microsoft.NET.Sdk\">
              <PropertyGroup>
                <TargetFrameworks>net6.0;net48</TargetFrameworks>
              </PropertyGroup>
            </Project>
        """)
        proj = tmp_path / "MultiTarget.csproj"
        proj.write_text(content)
        modified = upgrade_target_framework(str(proj), "net10.0")
        assert modified is True
        tree = ET.parse(str(proj))
        tf = tree.getroot().find(".//TargetFrameworks")
        assert tf is not None and tf.text == "net10.0"


# ── upgrade_solution ──────────────────────────────────────────────────────────

class TestUpgradeSolution:
    def test_upgrades_all_projects_in_chain(self, tmp_path):
        b = tmp_path / "B" / "B.csproj"
        a = tmp_path / "A" / "A.csproj"
        make_csproj(str(b), tf="net6.0")
        make_csproj(str(a), tf="net6.0", refs=["../B/B.csproj"])

        results = upgrade_solution(str(a), "net10.0")
        assert all(v is True for v in results.values())

        for p in [str(a), str(b)]:
            tf = ET.parse(p).getroot().find(".//TargetFramework")
            assert tf is not None and tf.text == "net10.0"

    def test_returns_false_for_already_upgraded(self, tmp_path):
        proj = tmp_path / "App.csproj"
        make_csproj(str(proj), tf="net10.0")
        results = upgrade_solution(str(proj), "net10.0")
        assert results[str(proj)] is False


# ── D3: SOP hard-block integration ──────────────────────────────────────────

class TestPreflightCsprojUpgrade:
    """
    Dimension 3: Verify _preflight_csproj_upgrade hard-blocks state on failures.
    Tests the SOP contract: ValueError/ET.ParseError → workflow_state="blocked".
    """

    def _make_task(self, description: str = "") -> object:
        """Build a minimal TaskItem-like object for testing."""
        from app.core.state import TaskItem
        return TaskItem(
            id="t-test",
            title="Test csproj upgrade",
            type="csproj_upgrade",
            description=description,
        )

    def _make_state(self, solution_path: str) -> object:
        """Build a minimal MigrationState for testing."""
        from app.core.state import MigrationState
        return MigrationState(migration_id="test-123", solution_path=solution_path)

    def _call_preflight(self, task, state):
        """Load _preflight_csproj_upgrade with transitive mcp deps stubbed out."""
        import sys
        import types
        import importlib.util
        import pathlib

        # Stub out missing optional deps so worker.py module-level imports succeed
        for mod_name in [
            "mcp", "mcp.client", "mcp.client.stdio",
            "app.integrations.vibekanban_adapter",
            "app.core.ruflo_mcp",
            "app.core.harness_adapter",
            "app.tools.adapter",
            "app.core.auto_skill_creator",
            "app.core.sop",
        ]:
            if mod_name not in sys.modules:
                stub = types.ModuleType(mod_name)
                # Provide common attributes workers depend on at import time
                stub.ruflo_client = None  # type: ignore[attr-defined]
                stub.vibekanban = None  # type: ignore[attr-defined]
                stub.harness = None  # type: ignore[attr-defined]
                stub.call_harness = None  # type: ignore[attr-defined]
                stub.SOPEnforcer = None  # type: ignore[attr-defined]
                stub.AutoSkillCreator = None  # type: ignore[attr-defined]
                stub.StdioServerParameters = None  # type: ignore[attr-defined]
                stub.ClientSession = None  # type: ignore[attr-defined]
                sys.modules[mod_name] = stub

        worker_path = str(
            pathlib.Path(__file__).parent.parent.parent / "app" / "agents" / "worker.py"
        )
        spec = importlib.util.spec_from_file_location("worker_isolated", worker_path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod._preflight_csproj_upgrade(task, state)

    def test_hardblock_on_legacy_csproj(self, tmp_path):
        """D3: ValueError (legacy ToolsVersion) must set workflow_state=blocked."""
        proj = tmp_path / "Legacy.csproj"
        make_legacy_csproj(str(proj))
        task = self._make_task()
        state = self._make_state(str(proj))
        result = self._call_preflight(task, state)
        assert result is False
        assert state.workflow_state == "blocked"
        assert state.blocked_reason is not None
        assert "ToolsVersion" in state.blocked_reason
        assert task.status == "failed"

    def test_hardblock_on_corrupt_xml(self, tmp_path):
        """D3: ET.ParseError (corrupt XML) must set workflow_state=blocked."""
        proj = tmp_path / "Corrupt.csproj"
        proj.write_text("<<not valid xml>>")
        task = self._make_task()
        state = self._make_state(str(proj))
        result = self._call_preflight(task, state)
        assert result is False
        assert state.workflow_state == "blocked"
        assert task.status == "failed"

    def test_hardblock_on_missing_solution(self, tmp_path):
        """D3: OSError (missing path) must set workflow_state=blocked."""
        task = self._make_task()
        state = self._make_state(str(tmp_path / "nonexistent.csproj"))
        result = self._call_preflight(task, state)
        assert result is False
        assert state.workflow_state == "blocked"
        assert task.status == "failed"

    def test_preflight_success_sets_resolved_paths(self, tmp_path):
        """D5: On success, state.resolved_csproj_paths is populated."""
        b = tmp_path / "B" / "B.csproj"
        a = tmp_path / "A" / "A.csproj"
        make_csproj(str(b), tf="net6.0")
        make_csproj(str(a), tf="net6.0", refs=["../B/B.csproj"])
        task = self._make_task("target_tf=net10.0")
        state = self._make_state(str(a))
        result = self._call_preflight(task, state)
        assert result is True
        assert state.workflow_state == "normal"
        assert len(state.resolved_csproj_paths) == 2
        assert task.status == "completed"
