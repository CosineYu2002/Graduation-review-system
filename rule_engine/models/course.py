from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from rule_engine.exception import (
    DataValidationError,
    MissingFieldError,
    InvalidTypeError,
    InvalidValueError,
)


@dataclass
class BaseCourse(ABC):
    course_name: str
    credits: float

    def __post_init__(self):
        if self.credits < 0:
            raise ValueError("學分數需大於0")
        if not self.course_name:
            raise ValueError("課程名稱不能為空")

    @classmethod
    @abstractmethod
    def from_dict(cls, course_data: dict) -> BaseCourse:
        raise NotImplementedError("子類必須實現 from_dict 方法")

    @classmethod
    def _validate_field_type(cls, data, expected_type, description: str):
        if not isinstance(data, expected_type):
            raise InvalidTypeError(description, expected_type, type(data))

    @classmethod
    def _validate_required_field(
        cls, data: dict, field_name: str, data_type: str = "課程資料"
    ):
        if field_name not in data:
            raise MissingFieldError(field_name, data_type)


@dataclass
class StudentCourse(BaseCourse):
    grade: int
    course_code: str
    category: str
    course_type: int
    recognized: bool = False

    def __post_init__(self):
        super().__post_init__()
        if (self.grade < 0 or self.grade > 100) and (
            self.grade not in [111, 555, 777, 999]
        ):
            raise ValueError("成績必須在0到100之間或是特殊值111、555、777或999")
        if not self.course_code:
            raise ValueError("課程代碼不能為空")
        if not self.category:
            raise ValueError("課程類別不能為空")
        if self.course_type not in [0, 1, 2]:
            raise ValueError("課程類型必須是0、1或2")

    @classmethod
    def from_dict(cls, course_data: dict) -> StudentCourse:
        return cls(
            course_name=course_data.get("course_name", ""),
            credits=course_data.get("credits", 0.0),
            grade=course_data.get("grade", 0),
            course_code=course_data.get("course_code", ""),
            category=course_data.get("category", ""),
            course_type=course_data.get("course_type", 0),
            recognized=course_data.get("recognized", False),
        )


@dataclass
class Course(BaseCourse):
    course_codes: list[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.course_codes:
            raise ValueError("課程代碼列表不能為空")
        if not all(isinstance(code, str) for code in self.course_codes):
            raise ValueError("所有課程代碼必須是字符串類型")
        if len(self.course_codes) != len(set(self.course_codes)):  # set去重
            raise ValueError("課程代碼列表不能有重複的項目")

    @classmethod
    def from_dict(cls, course_data: dict) -> Course:
        return cls(
            course_name=course_data.get("course_name", ""),
            credits=course_data.get("credits", 0.0),
            course_codes=course_data.get("course_codes", []),
        )
