from pydantic import BaseModel, Field, field_validator
from rule_engine.models.rule import Rule


class GraduationRule(BaseModel):
    admission_year: int = Field(..., gt=0, description="入學年度")
    department_code: str = Field(..., min_length=1, description="系所代碼")
    rules: list[Rule] = Field(..., description="畢業規則列表")

    @field_validator("department_code", mode="after")
    @classmethod
    def validate_department_code(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("系所代碼不能為空")
        return v.strip()
