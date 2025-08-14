from __future__ import annotations
from dataclasses import dataclass, field
from rule_engine.models.course import StudentCourse
from pathlib import Path
import json


@dataclass
class Student:
    name: str
    id: str
    courses: list[StudentCourse] = field(default_factory=list)
    major: str = ""

    def __post_init__(self):
        if not self.name:
            raise ValueError("學生姓名不能為空")
        if not self.id:
            raise ValueError("學生ID不能為空")
        if not isinstance(self.courses, list):
            raise TypeError("課程必須是列表類型")
        for c in self.courses:
            if not isinstance(c, StudentCourse):
                raise TypeError("課程列表中的項目必須是 StudentCourse 類型")

    @classmethod
    def from_dict(cls, student_data: dict) -> Student:
        courses = [
            StudentCourse.from_dict(course_data)
            for course_data in student_data.get("courses", [])
        ]

        return cls(
            name=student_data.get("name", ""),
            id=student_data.get("id", ""),
            courses=courses,
            major=student_data.get("major", ""),
        )

    @classmethod
    def from_json(cls, json_file_path: Path) -> Student:
        if not json_file_path.exists():
            raise FileNotFoundError(f"找不到學生檔案: {json_file_path}")

        try:
            data = json.loads(json_file_path.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"錯誤的 JSON 格式：{e}，路徑：{json_file_path}")
        except Exception as e:
            raise RuntimeError(f"讀取學生檔案時發生錯誤：{e}，路徑：{json_file_path}")
