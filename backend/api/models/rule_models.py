from enum import Enum
from pydantic import BaseModel

from rule_engine.models.rule import Rule


class RuleTypeEnum(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    DOUBLE_MAJOR = "double_major"


class RuleBasicInfo(BaseModel):
    """規則基本資訊（用於列表顯示）"""

    department_code: str
    department_name: str
    admission_year: int
    college: str
    rule_type: RuleTypeEnum


class RuleDetail(BaseModel):
    """規則詳細資訊（包含系所資訊和完整規則內容）"""

    basic_info: RuleBasicInfo
    rule_content: Rule


class CreateRuleRequest(BaseModel):
    """新增規則請求"""

    admission_year: int
    department_code: str
    rule_type: RuleTypeEnum
    rule_content: Rule
