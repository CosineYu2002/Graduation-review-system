from pydantic import BaseModel, Field, field_validator
from rule_engine.models.course import StudentCourse
from enum import Enum


class StudentType(Enum):
    REGULAR = "general"  # 一般生
    TRANSFER = "transfer"  # 轉學生
    DEPARTMENT_TRANSFER = "department_transfer"  # 轉系生
    DUAL = "dual"  # 雙主修
    MINOR = "minor"  # 輔系


class Student(BaseModel):
    name: str = Field(..., min_length=1, description="學生姓名")
    id: str = Field(..., pattern="^[A-Z][0-9]{8}$", description="學號")
    courses: list[StudentCourse] = Field(default_factory=list, description="修課列表")
    major: str = Field(..., min_length=1, description="主修科系")
    student_type: list[StudentType] = Field(
        default_factory=list, description="學生身份別"
    )

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("姓名不能為空")
        return v.strip()
