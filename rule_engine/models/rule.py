from typing import Self, Literal, Annotated, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from rule_engine.models.course import Course


class BaseRule(BaseModel):
    description: str = Field(..., min_length=1, description="規則描述")
    priority: int = Field(0, ge=0, description="規則優先級")

    @field_validator("description", mode="after")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("規則描述不能為空")
        return v.strip()


class ListSelectedRule(BaseRule):
    rule_type: Literal["list_selected"] = Field("list_selected", description="規則類型")
    min_credits: float | None = Field(None, ge=0, description="最少學分數")
    min_course_number: int | None = Field(None, ge=0, description="最少課程數量")
    learn_in_dept: bool = Field(..., description="是否限本系修課")
    fallback_department: list[str] = Field(
        default_factory=list, description="可替代系所"
    )
    course_list: list[Course] = Field(default_factory=list, description="課程列表")

    @model_validator(mode="after")
    def validate_min_requires(self) -> Self:
        if self.min_credits is not None and self.min_course_number is not None:
            raise ValueError("不能同時設定最少學分數和最少課程數量")
        elif self.min_credits is None and self.min_course_number is None:
            raise ValueError("至少需要設定最少學分數或最少課程數量")
        return self


class RequiredRule(BaseRule):
    rule_type: Literal["required"] = Field("required", description="規則類型")
    learn_in_dept: bool = Field(..., description="是否限本系修課")
    course_list: list[Course] = Field(default_factory=list, description="課程列表")


class PrerequisiteRule(BaseRule):
    rule_type: Literal["prerequisite"] = Field("prerequisite", description="規則類型")
    learn_in_dept: bool = Field(..., description="是否限本系修課")
    course_list: list[Course] = Field(default_factory=list, description="課程列表")


class CorrespondingRule(BaseRule):
    rule_type: Literal["corresponding"] = Field("corresponding", description="規則類型")
    learn_in_dept: bool = Field(..., description="是否限本系修課")
    course_list: list[Course] = Field(default_factory=list, description="課程列表")


class AnySelectedRule(BaseRule):
    rule_type: Literal["any_selected"] = Field("any_selected", description="規則類型")
    learn_in_dept: bool = Field(..., description="是否限本系修課")
    min_credits: float | None = Field(None, ge=0, description="最少學分數")
    min_course_number: int | None = Field(None, ge=0, description="最少課程數量")

    @model_validator(mode="after")
    def validate_min_requires(self) -> Self:
        if self.min_credits is not None and self.min_course_number is not None:
            raise ValueError("不能同時設定最少學分數和最少課程數量")
        elif self.min_credits is None and self.min_course_number is None:
            raise ValueError("至少需要設定最少學分數或最少課程數量")
        return self


class FinalRule(BaseRule):
    rule_type: Literal["final"] = Field("final", description="規則類型")
    min_credits: float = Field(..., ge=0, description="最少學分數")


Rule = Annotated[
    Union[
        ListSelectedRule,
        RequiredRule,
        PrerequisiteRule,
        CorrespondingRule,
        AnySelectedRule,
        FinalRule,
    ],
    Field(discriminator="rule_type"),
]
