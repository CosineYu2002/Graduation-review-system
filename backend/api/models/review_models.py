from pydantic import BaseModel
from api.models.student_models import StudentBasicInfo
from rule_engine.models.result import Result


class ReviewResult(BaseModel):
    student_info: StudentBasicInfo
    is_eligible_for_graduation: bool
    evaluation_results: Result
