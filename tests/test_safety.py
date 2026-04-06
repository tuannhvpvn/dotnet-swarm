"""Tests for SafetyRules with real config."""
import pytest
from app.core.safety import SafetyRules


@pytest.fixture
def rules():
    return SafetyRules("config/safety.yaml")


def test_check_file_path_clean(rules):
    result = rules.check_file_path("src/Controllers/UserController.cs")
    assert result.safe is True


def test_check_blacklisted_folder(rules):
    result = rules.check_file_path("keys/secret.pem")
    assert result.safe is False
    assert result.rule_id == "SAFE-002"


def test_check_sql_forbidden(rules):
    result = rules.check_sql("DROP TABLE Users;")
    assert result.safe is False
    assert result.rule_id == "SAFE-001"


def test_check_sql_clean(rules):
    result = rules.check_sql("SELECT id, name FROM Users WHERE active = 1")
    assert result.safe is True
