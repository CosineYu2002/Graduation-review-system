from pydantic import BaseModel, Field, field_validator, computed_field
from rule_engine.models.course import StudentCourse
from enum import Enum
from typing import Annotated


class Student(BaseModel):
    name: Annotated[str, Field(..., min_length=1, description="學生姓名", frozen=True)]
    id: Annotated[
        str,
        Field(..., pattern="^[A-Z][A-Z0-9][0-9]{7}$", description="學號", frozen=True),
    ]
    major: Annotated[str, Field(..., min_length=1, description="主修科系")]
    courses: Annotated[
        list[StudentCourse], Field(default_factory=list, description="修課列表")
    ]

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("姓名不能為空")
        return v.strip()

    @computed_field
    @property
    def admission_year(self) -> int:
        return int(self.id[3:5]) + 100
