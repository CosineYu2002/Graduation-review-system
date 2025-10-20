from pydantic import BaseModel


class ResultBasicInfo(BaseModel):
    """審查結果基本資訊"""

    file_name: str
    student_id: str
    student_name: str
