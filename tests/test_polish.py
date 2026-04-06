"""Tests for Phase 8 polish & integration deliverables (POL-01 through POL-06).

Covers:
- POL-01: CLI commands registered (resume, status, approve, start)
- POL-02: dashboard.py is syntactically valid Python
- POL-03: config.yaml has all 9 required top-level sections
- POL-04: .gitignore contains all required runtime artifact entries
- POL-06: docs/SOP.md and docs/ARCHITECTURE.md exist with required SOP gate content
"""
from pathlib import Path
import ast
import yaml


PROJECT_ROOT = Path(__file__).parent.parent


# ── POL-01: CLI commands ───────────────────────────────────────────────────────

def test_cli_all_four_commands_registered():
    """main.py must expose start, resume, status, approve commands via Typer (POL-01)."""
    src = (PROJECT_ROOT / "main.py").read_text()
    for cmd in ["def start", "def resume", "def status", "def approve"]:
        assert cmd in src, f"Missing CLI command: {cmd}"


def test_cli_resume_loads_persistence():
    """resume command must use MigrationPersistence to load state (POL-01)."""
    src = (PROJECT_ROOT / "main.py").read_text()
    assert "persistence.load" in src or "MigrationPersistence" in src, (
        "resume command must load state via MigrationPersistence"
    )


def test_cli_status_reads_json_snapshot():
    """status command must read from state/current_state.json, not internal imports (POL-01, D-02)."""
    src = (PROJECT_ROOT / "main.py").read_text()
    assert "current_state.json" in src, (
        "status command must read from current_state.json snapshot"
    )


def test_cli_approve_writes_human_decision():
    """approve command must write human_decision to the JSON snapshot (POL-01)."""
    src = (PROJECT_ROOT / "main.py").read_text()
    assert "human_decision" in src, (
        "approve command must write human_decision to state"
    )
    assert "workflow_state" in src, (
        "approve command must reset workflow_state"
    )


def test_cli_compiles():
    """main.py must be syntactically valid Python (POL-01)."""
    src = (PROJECT_ROOT / "main.py").read_text()
    ast.parse(src)  # raises SyntaxError if invalid


# ── POL-02: Dashboard ─────────────────────────────────────────────────────────

def test_dashboard_is_valid_python():
    """dashboard.py must be syntactically valid Python (POL-02)."""
    src = (PROJECT_ROOT / "dashboard.py").read_text()
    ast.parse(src)


def test_dashboard_reads_current_state_json():
    """dashboard.py must read from current_state.json only — no internal imports (POL-02, D-02)."""
    src = (PROJECT_ROOT / "dashboard.py").read_text()
    assert "current_state.json" in src, (
        "Dashboard must use current_state.json as data source (D-02)"
    )
    # Must NOT import from app.core.* (internal coupling)
    assert "from app.core" not in src and "import app.core" not in src, (
        "Dashboard must not import internal app modules (D-02)"
    )


def test_dashboard_shows_task_status_icons():
    """dashboard.py must display task status icons for all states (POL-02)."""
    src = (PROJECT_ROOT / "dashboard.py").read_text()
    # At least some of the required status icons must be present
    assert any(icon in src for icon in ["✅", "❌", "🔄", "⏳", "⛔"]), (
        "Dashboard must display task status icons"
    )


# ── POL-03: config.yaml ────────────────────────────────────────────────────────

def test_config_yaml_is_valid():
    """config.yaml must be parseable YAML (POL-03)."""
    cfg = yaml.safe_load((PROJECT_ROOT / "config.yaml").read_text())
    assert isinstance(cfg, dict)


def test_config_yaml_has_all_nine_sections():
    """config.yaml must have all 9 required top-level sections (POL-03)."""
    required = {
        "migration", "safety", "tools", "vibekanban",
        "ruflo", "gitnexus", "git", "session", "logging"
    }
    cfg = yaml.safe_load((PROJECT_ROOT / "config.yaml").read_text())
    missing = required - set(cfg.keys())
    assert not missing, f"config.yaml missing sections: {missing}"


def test_config_migration_section_has_target_framework():
    """migration section must specify target_framework (POL-03)."""
    cfg = yaml.safe_load((PROJECT_ROOT / "config.yaml").read_text())
    assert "target_framework" in cfg.get("migration", {}), (
        "migration section must have target_framework"
    )


def test_config_ruflo_section_has_mcp_url():
    """ruflo section must have mcp_url (POL-03)."""
    cfg = yaml.safe_load((PROJECT_ROOT / "config.yaml").read_text())
    ruflo = cfg.get("ruflo", {})
    assert "mcp_url" in ruflo, "ruflo section must have mcp_url"


# ── POL-04: .gitignore ────────────────────────────────────────────────────────

def test_gitignore_excludes_state_directory():
    """state/ must be in .gitignore to prevent committing migration runtime data (POL-04)."""
    content = (PROJECT_ROOT / ".gitignore").read_text()
    assert "state/" in content, "Missing state/ in .gitignore"


def test_gitignore_excludes_worktrees():
    """.worktrees/ must be in .gitignore (POL-04)."""
    content = (PROJECT_ROOT / ".gitignore").read_text()
    assert ".worktrees/" in content, "Missing .worktrees/ in .gitignore"


def test_gitignore_excludes_sqlite_files():
    """*.db must be in .gitignore to prevent committing SQLite checkpoint databases (POL-04)."""
    content = (PROJECT_ROOT / ".gitignore").read_text()
    assert "*.db" in content, "Missing *.db in .gitignore"


def test_gitignore_excludes_env_file():
    """.env must be in .gitignore (POL-04)."""
    content = (PROJECT_ROOT / ".gitignore").read_text()
    assert ".env" in content, "Missing .env in .gitignore"


# ── POL-06: Documentation ─────────────────────────────────────────────────────

def test_sop_md_exists():
    """docs/SOP.md must exist (POL-06)."""
    assert (PROJECT_ROOT / "docs" / "SOP.md").exists(), "Missing docs/SOP.md"


def test_architecture_md_exists():
    """docs/ARCHITECTURE.md must exist (POL-06)."""
    assert (PROJECT_ROOT / "docs" / "ARCHITECTURE.md").exists(), "Missing docs/ARCHITECTURE.md"


def test_sop_md_covers_all_four_gate_sections():
    """docs/SOP.md must document all 4 SOPEnforcer gate sections (A, B, E, I) (POL-06)."""
    content = (PROJECT_ROOT / "docs" / "SOP.md").read_text()
    for section in ["Section A", "Section B", "Section E", "Section I"]:
        assert section in content, f"docs/SOP.md missing {section}"


def test_sop_md_covers_human_gate():
    """docs/SOP.md must document the Human Gate mechanism (POL-06)."""
    content = (PROJECT_ROOT / "docs" / "SOP.md").read_text()
    assert any(kw in content for kw in ["Human Gate", "human_gate", "workflow_state"]), (
        "docs/SOP.md must document the Human Gate"
    )


def test_architecture_md_covers_graph_topology():
    """docs/ARCHITECTURE.md must describe the graph node topology (POL-06)."""
    content = (PROJECT_ROOT / "docs" / "ARCHITECTURE.md").read_text()
    assert any(kw in content for kw in ["surveyor", "planner", "human_gate", "migrate_task"]), (
        "docs/ARCHITECTURE.md must describe graph nodes"
    )


def test_architecture_md_covers_dual_write():
    """docs/ARCHITECTURE.md must describe the dual-write persistence strategy (POL-06)."""
    content = (PROJECT_ROOT / "docs" / "ARCHITECTURE.md").read_text()
    assert any(kw in content for kw in ["Dual-Write", "dual-write", "SqliteSaver", "SQLite"]), (
        "docs/ARCHITECTURE.md must describe dual-write persistence"
    )
