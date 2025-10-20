from pydantic import BaseModel


class APIResponse[DataT](BaseModel):
    success: bool
    message: str
    data: DataT
