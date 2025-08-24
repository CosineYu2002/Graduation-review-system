from pydantic import BaseModel, Field, field_validator
from rule_engine.models.course import StudentCourse


class Student(BaseModel):
    name: str = Field(..., min_length=1, description="學生姓名")
    id: str = Field(..., pattern="^[A-Z][0-9]{8}$", description="學號")
    courses: list[StudentCourse] = Field(default_factory=list, description="修課列表")
    major: str = Field(..., min_length=1, description="主修科系")

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("姓名不能為空")
        return v.strip()
