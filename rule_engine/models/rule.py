from __future__ import annotations
from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from rule_engine.models.course import BaseCourse
from enum import Enum


class CourseCriteria(BaseModel):
    """課程篩選條件"""

    # 基本條件
    course_name_pattern: Annotated[
        str | None, Field(description="課程名稱模式（正則表達式）")
    ] = None
    course_code_pattern: Annotated[
        str | None, Field(description="課程代碼模式（正則表達式）")
    ] = None

    # 系所條件
    department_codes: Annotated[
        list[str] | None, Field(description="允許的系所代碼列表")
    ] = None
    exclude_department_codes: Annotated[
        list[str] | None, Field(description="排除的系所代碼列表")
    ] = None

    # 課程屬性
    course_types: Annotated[
        list[int] | None, Field(description="允許的課程屬性（選必修）")
    ] = None
    categories: Annotated[
        list[str] | None, Field(description="允許的課程屬性（承抵類別）")
    ] = None
    tags: Annotated[
        list[str] | None, Field(description="限制的（必須包含的）課程標籤")
    ] = None

    # 特殊條件
    whitelist_courses: Annotated[
        list[BaseCourse] | None, Field(description="白名單課程列表")
    ] = None
    blacklist_courses: Annotated[
        list[BaseCourse] | None, Field(description="黑名單課程列表")
    ] = None
    exclude_same_name: Annotated[bool, Field(description="是否排除跟本系同名課程")] = (
        True
    )
    allow_fail: Annotated[bool, Field(description="是否允許未通過的課程計入")] = False
    series_courses: Annotated[bool, Field(description="是否修完完整課程才承認")] = False
    allow_external_substitute_after_fail: Annotated[
        bool, Field(description="是否允許外系同名課程承抵未通過的課程")
    ] = False


class RequirementType(str, Enum):
    ALL = "all"
    MIN_CREDITS = "min_credits"
    MAX_CREDITS = "max_credits"
    MIN_COURSES = "min_courses"
    MAX_COURSES = "max_courses"
    PREREQUISITE = "prerequisite"
    CREDIT_RANGE = "credit_range"
    MEANINGLESS = "meaningless"


class RuleRequirement(BaseModel):
    """規則需求"""

    type: RequirementType = Field(..., description="需求類型")

    min_credits: Annotated[float | None, Field(None, ge=0, description="最少學分數")]
    max_credits: Annotated[float | None, Field(None, ge=0, description="最多學分數")]
    min_courses: Annotated[int | None, Field(None, ge=0, description="最少課程數量")]
    max_courses: Annotated[int | None, Field(None, ge=0, description="最多課程數量")]

    pass_or_none: Annotated[
        bool, Field(False, description="如果規則不符合（未達成），獲得學分數計算為0")
    ]

    @model_validator(mode="after")
    def validate_requirements(self):
        match self.type:
            case RequirementType.MIN_CREDITS:
                if self.min_credits is None:
                    raise ValueError("最少學分數需求需要指定 min_credits")
                if (
                    self.max_credits is not None
                    or self.min_courses is not None
                    or self.max_courses is not None
                ):
                    raise ValueError("最少學分數需求不能指定其他需求參數")
            case RequirementType.MAX_CREDITS:
                if self.max_credits is None:
                    raise ValueError("最多學分數需求需要指定 max_credits")
                if (
                    self.min_credits is not None
                    or self.min_courses is not None
                    or self.max_courses is not None
                ):
                    raise ValueError("最多學分數需求不能指定其他需求參數")
            case RequirementType.MIN_COURSES:
                if self.min_courses is None:
                    raise ValueError("最少課程數量需求需要指定 min_courses")
                if (
                    self.min_credits is not None
                    or self.max_credits is not None
                    or self.max_courses is not None
                ):
                    raise ValueError("最少課程數量需求不能指定其他需求參數")
            case RequirementType.MAX_COURSES:
                if self.max_courses is None:
                    raise ValueError("最多課程數量需求需要指定 max_courses")
                if (
                    self.min_credits is not None
                    or self.max_credits is not None
                    or self.min_courses is not None
                ):
                    raise ValueError("最多課程數量需求不能指定其他需求參數")
            case RequirementType.ALL:
                if (
                    self.min_credits is not None
                    or self.max_credits is not None
                    or self.min_courses is not None
                    or self.max_courses is not None
                ):
                    raise ValueError("全部課程需求不能指定其他需求參數")
            case RequirementType.PREREQUISITE:
                if (
                    self.min_credits is not None
                    or self.max_credits is not None
                    or self.min_courses is not None
                    or self.max_courses is not None
                ):
                    raise ValueError("先修需求不能指定其他需求參數")
            case RequirementType.CREDIT_RANGE:
                if self.min_credits is None or self.max_credits is None:
                    raise ValueError(
                        "學分區間需求需要同時指定 min_credits 與 max_credits"
                    )
                if self.min_credits > self.max_credits:
                    raise ValueError("min_credits 不能大於 max_credits")
                if self.min_courses is not None or self.max_courses is not None:
                    raise ValueError("學分區間需求不能指定課程數量相關參數")
            case RequirementType.MEANINGLESS:
                if (
                    self.min_credits is not None
                    or self.max_credits is not None
                    or self.min_courses is not None
                    or self.max_courses is not None
                ):
                    raise ValueError("無意義需求不能指定其他需求參數")
            case _:
                raise ValueError(f"未知的需求類型: {self.type}")
        return self


class BaseRule(BaseModel):
    name: Annotated[str, Field(..., min_length=1, description="規則名稱")]
    description: Annotated[
        str | None, Field(None, min_length=1, description="規則描述")
    ]
    priority: Annotated[int, Field(default=0, ge=0, description="規則優先級")]

    @field_validator("description", "name", mode="after")
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("規則描述或名稱不能為空")
        return v.strip()


class RuleAll(BaseRule):
    rule_type: Annotated[
        Literal["rule_all"],
        Field("rule_all", description="規則類型"),
    ]
    course_list: Annotated[list[str] | None, Field(None, description="課程列表")]
    requirement: Annotated[RuleRequirement, Field(..., description="規則需求")]
    course_criteria: Annotated[CourseCriteria, Field(..., description="課程篩選條件")]


class RuleSet(BaseRule):
    rule_type: Annotated[
        Literal["rule_set"],
        Field("rule_set", description="規則類型"),
    ]
    sub_rules: Annotated[
        list[Rule], Field(default_factory=list, description="子規則列表")
    ]
    sub_rule_logic: Annotated[
        Literal["AND", "OR"], Field(default="AND", description="子規則邏輯關係")
    ]

    requirement: Annotated[RuleRequirement, Field(..., description="規則需求")]


"""
class RuleCCEP(BaseRule):
    rule_type: Annotated[
        Literal["rule_ccep"],
        Field("rule_ccep", description="規則類型"),
    ]
    college: Annotated[str | None, Field(None, description="學院名稱")]
    minor_rule: Annotated[Rule | None, Field(None, description="適用輔系規則")]
"""


Rule = Annotated[Union[RuleSet, RuleAll], Field(discriminator="rule_type")]
