from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union
from rule_engine.models.course import ResultCourse
from rule_engine.models.rule import RuleTypeEnum


class BaseEvaluationResult(BaseModel):
    name: str = Field(..., description="規則名稱")
    description: str | None = Field(None, description="規則描述")
    is_valid: bool = Field(True, description="是否符合規則")
    earned_credits: float = Field(0.0, ge=0, description="獲得學分數")


class SetResult(BaseEvaluationResult):
    result_type: Literal[RuleTypeEnum.RULE_SET] = Field(
        RuleTypeEnum.RULE_SET, description="結果類型"
    )
    sub_results: list[BaseEvaluationResult] = Field(
        default_factory=list, description="子規則結果列表"
    )
    sub_rule_logic: Literal["AND", "OR"] = Field("AND", description="子規則邏輯關係")


class ListResult(BaseEvaluationResult):
    result_type: Literal[RuleTypeEnum.RULE_LIST] = Field(
        RuleTypeEnum.RULE_LIST, description="結果類型"
    )
    course_list: list[ResultCourse] = Field(
        default_factory=list, description="符合規則的課程列表"
    )


class CriteriaResult(BaseEvaluationResult):
    result_type: Literal[RuleTypeEnum.RULE_CRITERIA] = Field(
        RuleTypeEnum.RULE_CRITERIA, description="結果類型"
    )
    course_list: list[ResultCourse] = Field(
        default_factory=list, description="符合規則的課程列表"
    )


Result = Annotated[
    Union[SetResult, ListResult, CriteriaResult], Field(discriminator="result_type")
]
