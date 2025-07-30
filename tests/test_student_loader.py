import pytest
import json
from rule_engine.loader import StudentLoader
from pathlib import Path


@pytest.fixture(scope="module")
def dummy_student_data(tmp_path_factory):
    student_data = {
        "name": "Cosine Yu",
        "id": "E24119045",
        "courses": [
            {
                "course_name": "設計思考教中學",
                "course_code": "P371000",
                "credit": 2.0,
                "grade": 85,
                "category": " ",
            },
            {
                "course_name": "Python程式語言與互動式遊戲設計",
                "course_code": "N986700",
                "credit": 3.0,
                "grade": 90,
                "category": "Y",
            },
        ],
    }
    temp_dir = tmp_path_factory.mktemp("data")
    student_file: Path = temp_dir / "student.json"
    student_file.write_text(json.dumps(student_data), encoding="utf-8")
    return student_file


def test_student_loader(dummy_student_data: Path):
    loader = StudentLoader(dummy_student_data)
    data = loader.load()

    assert isinstance(data, dict)
    assert data["name"] == "Cosine Yu"
    assert data["id"] == "E24119045"
    assert isinstance(data["courses"], list)
    assert len(data["courses"]) == 2
    assert data["courses"][0]["course_name"] == "設計思考教中學"
    assert data["courses"][0]["course_code"] == "P371000"
    assert data["courses"][0]["credit"] == 2.0
    assert data["courses"][0]["grade"] == 85
    assert data["courses"][0]["category"] == " "
    assert data["courses"][1]["course_name"] == "Python程式語言與互動式遊戲設計"
    assert data["courses"][1]["course_code"] == "N986700"
    assert data["courses"][1]["credit"] == 3.0
    assert data["courses"][1]["grade"] == 90
    assert data["courses"][1]["category"] == "Y"


def test_student_loader_invalid_file():
    with pytest.raises(FileNotFoundError):
        loader = StudentLoader(Path("non_existent_file.json"))
        loader.load()


def test_student_loader_invalid_json(tmp_path):
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("Invalid JSON content", encoding="utf-8")

    loader = StudentLoader(invalid_file)
    with pytest.raises(ValueError):
        loader.load()
