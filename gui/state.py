from dataclasses import dataclass
from pathlib import Path
from rule_engine.models.student import Student


@dataclass(slots=True)
class AppStatus:
    students: dict[str, Student]
    students_dir: Path = Path("data/students")
    rules_dir: Path = Path("data/rules")
    selected_id: str | None = None
