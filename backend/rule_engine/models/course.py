from pydantic import BaseModel, Field, field_validator
from typing import Literal, Annotated


class BaseCourse(BaseModel):
    course_name: Annotated[str, Field(..., min_length=1, description="課程名稱")]
    course_codes: Annotated[
        list[str], Field(..., min_length=1, description="課程代碼列表")
    ]
    credit: Annotated[float, Field(..., ge=0, description="學分數")]
    course_type: Annotated[int, Field(..., description="選必修")]
    tag: Annotated[list[str], Field(default_factory=list, description="課程標籤")]

    @field_validator("course_name", mode="after")
    @classmethod
    def validate_course_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("課程名稱不能為空")
        return v.strip()

    @field_validator("course_codes", mode="after")
    @classmethod
    def validate_course_codes(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("課程代碼列表中不能有重複的課程代碼")
        return v

    @field_validator("course_type", mode="after")
    @classmethod
    def validate_course_type(cls, v: int) -> int:
        if v not in [0, 1, 2, 3]:
            raise ValueError("選修必修類別錯誤")
        return v


class StudentCourse(BaseCourse):
    grade: Annotated[int, Field(..., description="成績")]
    category: Annotated[
        str, Field(..., min_length=1, max_length=1, description="承抵課程類別")
    ]
    year_taken: Annotated[int, Field(..., description="修課學年")]
    semester_taken: Annotated[Literal[0, 1, 2], Field(..., description="修課學期")]
    recognized: Annotated[bool, Field(False, description="是否檢查過")]

    @field_validator("grade", mode="after")
    @classmethod
    def validate_grade(cls, v: int) -> int:
        if (v < 0 or v > 100) and (v not in [111, 555, 777, 999]):
            raise ValueError("成績必須在0到100之間，或為特殊值111, 555, 777, 999")
        return v

    @field_validator("category", mode="after")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in [
            " ",
            "A",
            "B",
            "D",
            "E",
            "F",
            "J",
            "K",
            "L",
            "N",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "X",
            "Y",
            "Z",
        ]:
            raise ValueError("承抵課程類別錯誤")
        return v


class ResultCourse(BaseCourse):
    status: Annotated[str, Field(..., description="修課狀態")]
    year_taken: Annotated[int, Field(..., description="修課學年")]
    semester_taken: Annotated[Literal[0, 1, 2], Field(..., description="修課學期")]
