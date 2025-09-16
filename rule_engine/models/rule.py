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
    department_codes: list[str] | None = Field(None, description="允許的系所代碼列表")
    exclude_department_codes: list[str] | None = Field(
        None, description="排除的系所代碼列表"
    )

    # 課程屬性
    course_types: list[int] | None = Field(None, description="允許的課程屬性（選必修）")
    categories: list[str] | None = Field(None, description="允許的課程屬性（承抵類別）")
    tags: list[str] | None = Field(None, description="限制的（必須包含的）課程標籤")

    # 特殊條件
    whitelist_courses: list[BaseCourse] | None = Field(
        None, description="白名單課程列表"
    )
    blacklist_courses: list[BaseCourse] | None = Field(
        None, description="黑名單課程列表"
    )
    exclude_same_name: bool = Field(True, description="是否排除跟本系同名課程")
    allow_fail: bool = Field(False, description="是否允許未通過的課程計入")
    series_courses: bool = Field(False, description="是否修完完整課程才承認")
    allow_external_substitute_after_fail: bool = Field(
        True, description="是否允許外系同名課程承抵未通過的課程"
    )


class RequirementType(Enum):
    ALL = "全部課程"
    MIN_CREDITS = "最少學分數"
    MAX_CREDITS = "最多承認學分數，超過的不算"
    MIN_COURSES = "最少課程數量"
    MAX_COURSES = "最多課程數量，超過的不算"
    PREREQUISITE = "先修（不算學分）"
    CREDIT_RANGE = "學分區間（指定最少與最多學分數）"


class RuleRequirement(BaseModel):
    """規則需求"""

    type: RequirementType = Field(..., description="需求類型")

    mincredits: float | None = Field(None, ge=0, description="最少學分數")
    maxcredits: float | None = Field(None, ge=0, description="最多學分數")
    mincourses: int | None = Field(None, ge=0, description="最少課程數量")
    maxcourses: int | None = Field(None, ge=0, description="最多課程數量")

    pass_or_none: bool = Field(
        False, description="如果規則不符合（未達成），獲得學分數計算為0"
    )

    @model_validator(mode="after")
    def validate_requirements(self):
        match self.type:
            case RequirementType.MIN_CREDITS:
                if self.mincredits is None:
                    raise ValueError("最少學分數需求需要指定 mincredits")
                if (
                    self.maxcredits is not None
                    or self.mincourses is not None
                    or self.maxcourses is not None
                ):
                    raise ValueError("最少學分數需求不能指定其他需求參數")
            case RequirementType.MAX_CREDITS:
                if self.maxcredits is None:
                    raise ValueError("最多學分數需求需要指定 maxcredits")
                if (
                    self.mincredits is not None
                    or self.mincourses is not None
                    or self.maxcourses is not None
                ):
                    raise ValueError("最多學分數需求不能指定其他需求參數")
            case RequirementType.MIN_COURSES:
                if self.mincourses is None:
                    raise ValueError("最少課程數量需求需要指定 mincourses")
                if (
                    self.mincredits is not None
                    or self.maxcredits is not None
                    or self.maxcourses is not None
                ):
                    raise ValueError("最少課程數量需求不能指定其他需求參數")
            case RequirementType.MAX_COURSES:
                if self.maxcourses is None:
                    raise ValueError("最多課程數量需求需要指定 maxcourses")
                if (
                    self.mincredits is not None
                    or self.maxcredits is not None
                    or self.mincourses is not None
                ):
                    raise ValueError("最多課程數量需求不能指定其他需求參數")
            case RequirementType.ALL:
                if (
                    self.mincredits is not None
                    or self.maxcredits is not None
                    or self.mincourses is not None
                    or self.maxcourses is not None
                ):
                    raise ValueError("全部課程需求不能指定其他需求參數")
            case RequirementType.PREREQUISITE:
                if (
                    self.mincredits is not None
                    or self.maxcredits is not None
                    or self.mincourses is not None
                    or self.maxcourses is not None
                ):
                    raise ValueError("先修需求不能指定其他需求參數")
            case RequirementType.CREDIT_RANGE:
                if self.mincredits is None or self.maxcredits is None:
                    raise ValueError(
                        "學分區間需求需要同時指定 mincredits 與 maxcredits"
                    )
                if self.mincredits > self.maxcredits:
                    raise ValueError("mincredits 不能大於 maxcredits")
                if self.mincourses is not None or self.maxcourses is not None:
                    raise ValueError("學分區間需求不能指定課程數量相關參數")
            case _:
                raise ValueError(f"未知的需求類型: {self.type}")
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
    RULE_ALL = "rule_all"


class RuleSet(BaseRule):
    rule_type: RuleTypeEnum = Field(RuleTypeEnum.RULE_SET, description="規則類型")
    sub_rules: list[RuleSet | Rule] = Field(
        default_factory=list, description="子規則列表"
    )
    sub_rule_logic: Literal["AND", "OR"] = Field(
        default="AND", description="子規則邏輯關係"
    )
    requirement: RuleRequirement = Field(..., description="規則需求")


class RuleAll(BaseRule):
    rule_type: RuleTypeEnum = Field(RuleTypeEnum.RULE_ALL, description="規則類型")
    course_list: list[BaseCourse] | None = Field(None, description="課程列表")
    requirement: RuleRequirement = Field(..., description="規則需求")
    course_criteria: CourseCriteria = Field(..., description="課程篩選條件")


Rule = Annotated[Union[RuleSet, RuleAll], Field(discriminator="rule_type")]
