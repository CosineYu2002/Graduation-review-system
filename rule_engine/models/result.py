from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union
from rule_engine.models.course import ResultCourse


class BaseEvaluationResult(BaseModel):
    name: Annotated[str, Field(..., description="規則名稱")]
    description: Annotated[str | None, Field(None, description="規則描述")]
    is_valid: Annotated[bool, Field(True, description="是否符合規則")]
    earned_credits: Annotated[float, Field(0.0, ge=0, description="獲得學分數")]


class SetResult(BaseEvaluationResult):
    result_type: Annotated[
        Literal["rule_set"],
        Field("rule_set", description="結果類型"),
    ]
    sub_results: Annotated[
        list[Result],
        Field(default_factory=list, description="子規則結果列表"),
    ]
    sub_rule_logic: Annotated[
        Literal["AND", "OR"], Field("AND", description="子規則邏輯關係")
    ]


class AllResult(BaseEvaluationResult):
    result_type: Annotated[
        Literal["rule_all"],
        Field("rule_all", description="結果類型"),
    ]
    finished_course_list: Annotated[
        list[ResultCourse],
        Field(default_factory=list, description="符合規則的課程列表"),
    ]
    required_course_list: Annotated[
        list[str] | None, Field(None, description="規則要求的課程列表")
    ]


"""
class CCEPResult(BaseEvaluationResult):
    result_type: Annotated[
        Literal["rule_ccep"],
        Field("rule_ccep", description="結果類型"),
    ]
    sub_results: Annotated[
        list[Result], Field(default_factory=list, description="子規則結果列表")
    ]
    college_course_list: Annotated[
        list[ResultCourse],
        Field(default_factory=list, description="符合學院規則的課程列表"),
    ]
"""

Result = Annotated[Union[SetResult, AllResult], Field(discriminator="result_type")]
