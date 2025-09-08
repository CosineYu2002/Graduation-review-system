from __future__ import annotations
from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from rule_engine.models.course import BaseCourse
from enum import Enum


class CourseCriteria(BaseModel):
    """課程篩選條件"""

    # 基本條件
    course_name_pattern: str | None = Field(
        None, description="課程名稱模式（正則表達式）"
    )
    course_code_pattern: str | None = Field(
        None, description="課程代碼模式（正則表達式）"
    )

    # 系所條件
    department_codes: list[str] | None = Field(None, description="系所代碼列表")
    exclude_department_codes: list[str] | None = Field(
        None, description="排除的系所代碼列表"
    )

    # 課程屬性
    course_types: list[int] | None = Field(None, description="課程類型（選必修）")
    categories: list[str] | None = Field(None, description="課程類型（承抵類別）")
    tags: list[str] | None = Field(None, description="課程標籤")

    # 特殊條件
    whitelist_courses: list[BaseCourse] | None = Field(
        None, description="白名單課程列表"
    )
    blacklist_courses: list[BaseCourse] | None = Field(
        None, description="黑名單課程列表"
    )
    exclude_same_name: bool = Field(True, description="是否排除跟本系同名課程")
    allow_fail: bool = Field(False, description="是否允許未通過的課程計入")
    allow_substitute: bool = Field(False, description="是否允許替代課程")
    learn_in_dept: bool = Field(True, description="是否限定本系課程")


class RequirementType(Enum):
    ALL = "全部課程"
    MIN_CREDITS = "最少學分數"
    MAX_CREDITS = "最多學分數"
    MIN_COURSES = "最少課程數量"
    MAX_COURSES = "最多課程數量"


class RuleRequirement(BaseModel):
    """規則需求"""

    type: RequirementType = Field(..., description="需求類型")

    mincredits: float | None = Field(None, ge=0, description="最少學分數")
    maxcredits: float | None = Field(None, ge=0, description="最多學分數")
    mincourses: int | None = Field(None, ge=0, description="最少課程數量")
    maxcourses: int | None = Field(None, ge=0, description="最多課程數量")

    @model_validator(mode="after")
    def validate_requirements(self):
        match self.type:
            case RequirementType.MIN_CREDITS:
                if self.mincredits is None:
                    raise ValueError("最少學分數需求需要指定 mincredits")
            case RequirementType.MAX_CREDITS:
                if self.maxcredits is None:
                    raise ValueError("最多學分數需求需要指定 maxcredits")
            case RequirementType.MIN_COURSES:
                if self.mincourses is None:
                    raise ValueError("最少課程數量需求需要指定 mincourses")
            case RequirementType.MAX_COURSES:
                if self.maxcourses is None:
                    raise ValueError("最多課程數量需求需要指定 maxcourses")
        return self


class BaseRule(BaseModel):
    name: str = Field(..., min_length=1, description="規則名稱")
    description: str | None = Field(None, min_length=1, description="規則描述")
    priority: int = Field(default=0, ge=0, description="規則優先級")

    @field_validator("description", "name", mode="after")
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("規則描述或名稱不能為空")
        return v.strip()


class RuleTypeEnum(Enum):
    RULE_SET = "rule_set"
    RULE_LIST = "rule_list"
    RULE_CRITERIA = "rule_criteria"


class RuleSet(BaseRule):
    rule_type: RuleTypeEnum = Field(RuleTypeEnum.RULE_SET, description="規則類型")
    sub_rules: list[RuleSet | RuleList | RuleCriteria] = Field(
        default_factory=list, description="子規則列表"
    )
    sub_rule_logic: Literal["AND", "OR"] = Field(
        default="AND", description="子規則邏輯關係"
    )
    requirement: RuleRequirement = Field(..., description="規則需求")


class RuleList(BaseRule):
    rule_type: RuleTypeEnum = Field(RuleTypeEnum.RULE_LIST, description="規則類型")
    course_list: list[BaseCourse] = Field(default_factory=list, description="課程列表")
    requirement: RuleRequirement = Field(..., description="規則需求")
    course_criteria: CourseCriteria = Field(..., description="課程篩選條件")


class RuleCriteria(BaseRule):
    rule_type: RuleTypeEnum = Field(RuleTypeEnum.RULE_CRITERIA, description="規則類型")
    course_criteria: CourseCriteria = Field(..., description="課程篩選條件")
    requirement: RuleRequirement = Field(..., description="規則需求")


Rule = Annotated[
    Union[RuleSet, RuleList, RuleCriteria], Field(discriminator="rule_type")
]
