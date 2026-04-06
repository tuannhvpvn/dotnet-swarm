"""Tests for skills sync registry."""


def test_skills_list_has_13_entries():
    """SKILLS registry must have exactly 13 entries (5 legacy + 8 phase-1 skills)."""
    from app.utils.sync_skills import SKILLS
    assert len(SKILLS) == 13, f"Expected 13 skills, got {len(SKILLS)}: {SKILLS}"


def test_skills_are_strings():
    """SKILLS entries are skill name strings."""
    from app.utils.sync_skills import SKILLS
    for skill in SKILLS:
        assert isinstance(skill, str), f"Expected string, got {type(skill)}: {skill}"
        assert len(skill) > 0, "Skill name must not be empty"
