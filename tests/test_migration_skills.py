"""Tests for Phase 6 migration skill file contents (SKL-01 through SKL-08).

Verifies:
- All 8 phase-6 skill files exist with proper YAML frontmatter
- All contain strict AI constraint warnings preventing hallucinated replacements
- Key mapping tables and required directives are present per skill definition
"""
from pathlib import Path
import pytest

SKILLS_ROOT = Path(".migration-skills")

# The 8 skills introduced in Phase 6
PHASE_6_SKILLS = [
    "dotnet-controller-migration",
    "dotnet-webconfig-to-appsettings",
    "dotnet-startup-migration",
    "dotnet-auth-middleware",
    "dotnet-namespace-replacement",
    "dotnet-logging-adapter",
    "dotnet-docker-setup",
    "dotnet-nuget-mapping",
]


def read_skill(skill_name: str) -> str:
    path = SKILLS_ROOT / skill_name / "SKILL.md"
    assert path.exists(), f"SKILL.md not found for: {skill_name}"
    return path.read_text()


# ── Existence & structure ──────────────────────────────────────────────────────

@pytest.mark.parametrize("skill", PHASE_6_SKILLS)
def test_skill_file_exists(skill):
    """Each phase-6 skill must have a SKILL.md at the expected path."""
    path = SKILLS_ROOT / skill / "SKILL.md"
    assert path.exists(), f"Missing skill file: {path}"


@pytest.mark.parametrize("skill", PHASE_6_SKILLS)
def test_skill_has_yaml_frontmatter(skill):
    """Each skill must start with YAML frontmatter (--- block)."""
    content = read_skill(skill)
    assert content.startswith("---"), f"{skill}: SKILL.md must start with YAML frontmatter"
    assert content.count("---") >= 2, f"{skill}: SKILL.md must have closing --- frontmatter"


@pytest.mark.parametrize("skill", PHASE_6_SKILLS)
def test_skill_has_name_in_frontmatter(skill):
    """Each skill frontmatter must declare its name field."""
    content = read_skill(skill)
    assert f"name: {skill}" in content, f"{skill}: frontmatter missing 'name: {skill}'"


# ── Strict constraint tags (must-have per PLAN) ────────────────────────────────

@pytest.mark.parametrize("skill", PHASE_6_SKILLS)
def test_skill_contains_strict_ai_constraint(skill):
    """Each phase-6 skill must contain a strict AI constraint directive — the
    core safety mechanism preventing LLM hallucination during migration."""
    content = read_skill(skill)
    strict_markers = [
        "DO NOT invent",
        "DO NOT guess",
        "NEVER copy",
        "STRICTLY",
        "DO NOT retain",
        "NEVER replace",
        "must be",
        "MUST be",
    ]
    has_constraint = any(marker in content for marker in strict_markers)
    assert has_constraint, (
        f"{skill}: Missing strict AI constraint. "
        f"Must contain one of: {strict_markers}"
    )


# ── Per-skill key content requirements ────────────────────────────────────────

def test_controller_skill_has_api_controller_mapping():
    """dotnet-controller-migration must map ApiController -> ControllerBase (SKL-01)."""
    content = read_skill("dotnet-controller-migration")
    assert "ApiController" in content, "Missing ApiController mapping"
    assert "ControllerBase" in content, "Missing ControllerBase target"


def test_webconfig_skill_has_placeholder_rule():
    """dotnet-webconfig-to-appsettings must forbid raw connection strings (SKL-02)."""
    content = read_skill("dotnet-webconfig-to-appsettings")
    # Must reference placeholder handling for connection strings
    assert any(kw in content for kw in ["PLACEHOLDER", "placeholder", "Placeholder"]), (
        "Missing placeholder rule for connection string scrubbing"
    )
    assert "appsettings.json" in content, "Missing appsettings.json target reference"


def test_startup_skill_has_programcs_mapping():
    """dotnet-startup-migration must map Global.asax -> Program.cs (SKL-03)."""
    content = read_skill("dotnet-startup-migration")
    assert "Program.cs" in content, "Missing Program.cs target"
    assert any(kw in content for kw in ["Global.asax", "Application_Start"]), (
        "Missing Global.asax / Application_Start source reference"
    )


def test_auth_skill_has_middleware_pipeline():
    """dotnet-auth-middleware must mandate UseAuthentication + UseAuthorization (SKL-04)."""
    content = read_skill("dotnet-auth-middleware")
    assert "UseAuthentication" in content, "Missing UseAuthentication() directive"
    assert "UseAuthorization" in content, "Missing UseAuthorization() directive"


def test_namespace_skill_has_system_web_mapping():
    """dotnet-namespace-replacement must map System.Web.Http -> Microsoft.AspNetCore.Mvc (SKL-05)."""
    content = read_skill("dotnet-namespace-replacement")
    assert "System.Web.Http" in content, "Missing System.Web.Http source namespace"
    assert "Microsoft.AspNetCore.Mvc" in content, "Missing Microsoft.AspNetCore.Mvc target namespace"


def test_logging_skill_has_ilogger_target():
    """dotnet-logging-adapter must target ILogger<T> injection pattern (SKL-06)."""
    content = read_skill("dotnet-logging-adapter")
    assert "ILogger" in content, "Missing ILogger<T> target reference"


def test_docker_skill_has_multistage_and_nonroot():
    """dotnet-docker-setup must mandate multi-stage build and non-root user (SKL-07)."""
    content = read_skill("dotnet-docker-setup")
    assert any(kw in content for kw in ["Multi-stage", "multi-stage", "AS build"]), (
        "Missing multi-stage build requirement"
    )
    assert any(kw in content for kw in ["Non-root", "non-root", "USER app"]), (
        "Missing non-root user requirement"
    )


def test_nuget_skill_has_removal_directives():
    """dotnet-nuget-mapping must list packages to prune and upgrade mappings (SKL-08)."""
    content = read_skill("dotnet-nuget-mapping")
    assert any(kw in content for kw in ["prune", "Prune", "PRUNE", "Remove", "remove"]), (
        "Missing package removal/pruning directives"
    )
    assert "EntityFramework" in content, "Missing EntityFramework -> EF Core upgrade mapping"
