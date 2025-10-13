from pydantic import BaseModel


class APIResponse[DataT](BaseModel):
    success: bool
    message: str
    data: DataT


class StudentBasicInfo(BaseModel):
    id: str
    name: str
    major: str
