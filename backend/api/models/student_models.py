from pydantic import BaseModel


class StudentBasicInfo(BaseModel):
    id: str
    name: str
    major: str
