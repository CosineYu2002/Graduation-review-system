import pytest
import json
from pathlib import Path
from rule_engine.loader import RuleLoader


# Create a dummy rules file for testing
@pytest.fixture(scope="module")
def dummy_rules_file(tmp_path_factory):
    rules_data = {
        "109": [
            {
                "type": "list_selected",
                "target": "ee_selected_list_109.json",
                "min_credits": 28,
                "learn_in_department": True,
                "fallback_department": ["E2"],
            },
            {
                "type": "final",
                "total_credits": 28,
                "department_name": "electrical engineering",
            },
        ],
        "110": [
            {
                "type": "list_selected",
                "target": "ee_selected_list_110.json",
                "min_credits": 28,
                "learn_in_department": True,
                "fallback_department": ["E2", "N2", "Q1", "Q3", "Q7"],
            },
            {
                "type": "final",
                "total_credits": 28,
                "department_name": "electrical engineering",
            },
        ],
    }
    temp_dir = tmp_path_factory.mktemp("data")
    rules_file: Path = temp_dir / "rules.json"
    rules_file.write_text(json.dumps(rules_data), encoding="utf-8")
    return rules_file


def test_rule_loader_valid_file(dummy_rules_file: Path):
    loader = RuleLoader(dummy_rules_file)
    rules = loader.load()
    assert isinstance(rules, dict)
    assert "109" in rules
    assert "110" in rules
    assert len(rules["109"]) == 2
    assert len(rules["110"]) == 2
    assert rules["109"][0]["type"] == "list_selected"
    assert rules["109"][0]["target"] == "ee_selected_list_109.json"
    assert rules["109"][0]["min_credits"] == 28
    assert rules["109"][0]["learn_in_department"] is True
    assert rules["109"][0]["fallback_department"] == ["E2"]
    assert rules["109"][1]["type"] == "final"
    assert rules["109"][1]["total_credits"] == 28
    assert rules["109"][1]["department_name"] == "electrical engineering"


def test_rule_loader_invalid_file():
    with pytest.raises(FileNotFoundError):
        RuleLoader(Path("nonexistent_file.json"))


def test_rule_loader_invalid_json(tmp_path):
    # Create an invalid JSON file
    invalid_json_path = tmp_path / "invalid.json"
    invalid_json_path.write_text("This is not JSON", encoding="utf-8")

    loader = RuleLoader(invalid_json_path)
    with pytest.raises(ValueError):
        loader.load()
